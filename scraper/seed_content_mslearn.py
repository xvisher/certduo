#!/usr/bin/env python3
"""
Fetches article content from Microsoft Learn and upserts it into Topic.content.
Only updates topics that match by title (case-insensitive, partial match OK).

Usage:
    python3 seed_content_mslearn.py
    python3 seed_content_mslearn.py --cert AZ-900
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

load_dotenv(Path(__file__).parent.parent / ".env.local")
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set"); sys.exit(1)

from scrapers.mslearn_content import scrape_cert_content, CERT_MODULES

CERTS = list(CERT_MODULES.keys())


def seed_cert(cert_code: str):
    print(f"\n{'='*60}")
    print(f"Scraping MS Learn content for {cert_code}...")
    print(f"{'='*60}")

    scraped = scrape_cert_content(cert_code)
    if not scraped:
        print(f"  No content scraped for {cert_code}")
        return 0

    # Reconnect fresh after (potentially long) scraping to avoid Neon idle timeout
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Get all topics for this cert
    cur.execute("""
        SELECT t.id, t.title
        FROM "Topic" t
        JOIN "Module" m ON t."moduleId" = m.id
        JOIN "Certification" c ON m."certificationId" = c.id
        WHERE c.code = %s
    """, (cert_code,))
    db_topics = {row[1].lower(): row[0] for row in cur.fetchall()}

    updated = 0
    skipped = 0

    for item in scraped:
        title_lower = item["title"].lower()

        # Find matching DB topic (exact match first, then partial)
        topic_id = db_topics.get(title_lower)
        if not topic_id:
            # Try partial match
            for db_title, tid in db_topics.items():
                if title_lower in db_title or db_title in title_lower:
                    topic_id = tid
                    break

        if not topic_id:
            print(f"  [skip] No DB topic matching '{item['title']}'")
            skipped += 1
            continue

        cur.execute("""
            UPDATE "Topic"
            SET content = %s, "readingTime" = %s, "msLearnUrl" = %s
            WHERE id = %s
        """, (item["content"], item["readingTime"], item["msLearnUrl"], topic_id))
        updated += 1
        print(f"  ✓ Updated '{item['title']}' ({len(item['content'])}b)")

    conn.commit()
    conn.close()
    print(f"\n  {cert_code}: {updated} topics updated, {skipped} skipped")
    return updated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cert", choices=CERTS, help="Only seed one cert")
    args = parser.parse_args()

    certs_to_seed = [args.cert] if args.cert else CERTS

    total = 0
    for cert in certs_to_seed:
        total += seed_cert(cert)

    print(f"\n✅ Done — {total} topics updated across {len(certs_to_seed)} cert(s)")


if __name__ == "__main__":
    main()
