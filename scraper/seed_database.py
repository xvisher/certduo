#!/usr/bin/env python3
"""
Seed the CertDuo database from scraped JSON files.

Usage:
    python seed_database.py --cert az-900 --input output/az-900.json
    python seed_database.py --all
"""

import argparse
import json
import hashlib
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv(Path(__file__).parent.parent / ".env.local")

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in .env.local")
    sys.exit(1)


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def seed_cert(cert_code: str, data: dict, conn):
    """Seed a single certification and its questions."""
    cert_code = cert_code.upper()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    print(f"\n{'='*50}")
    print(f"Seeding {cert_code}...")

    # Upsert certification
    cursor.execute("""
        INSERT INTO "Certification" (id, code, name, description, "createdAt", "updatedAt")
        VALUES (gen_random_uuid()::text, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (code) DO UPDATE
        SET name = EXCLUDED.name,
            description = EXCLUDED.description,
            "updatedAt" = NOW()
        RETURNING id
    """, (cert_code, data.get("name", cert_code), data.get("description", "")))

    cert_row = cursor.fetchone()
    cert_id = cert_row["id"]
    print(f"Certification ID: {cert_id}")

    # Process modules and topics
    modules_map = {}  # module_title → module_id
    topics_map = {}   # (module_title, topic_title) → topic_id

    for i, q in enumerate(data.get("questions", [])):
        module_title = q.get("module", "General")
        topic_title = q.get("topic", module_title)

        # Upsert module
        if module_title not in modules_map:
            cursor.execute("""
                INSERT INTO "Module" (id, "certificationId", title, "orderIndex", "createdAt")
                VALUES (gen_random_uuid()::text, %s, %s, %s, NOW())
                ON CONFLICT DO NOTHING
                RETURNING id
            """, (cert_id, module_title, len(modules_map)))

            row = cursor.fetchone()
            if row:
                modules_map[module_title] = row["id"]
            else:
                cursor.execute(
                    'SELECT id FROM "Module" WHERE "certificationId" = %s AND title = %s',
                    (cert_id, module_title)
                )
                row = cursor.fetchone()
                if row:
                    modules_map[module_title] = row["id"]

        module_id = modules_map.get(module_title)
        if not module_id:
            continue

        # Upsert topic
        topic_key = (module_title, topic_title)
        if topic_key not in topics_map:
            ms_learn_url = (
                q.get("documentationLinks", [{}])[0].get("url", "https://learn.microsoft.com")
                if q.get("documentationLinks")
                else "https://learn.microsoft.com"
            )
            cursor.execute("""
                INSERT INTO "Topic" (id, "moduleId", title, "msLearnUrl", "orderIndex", "createdAt")
                VALUES (gen_random_uuid()::text, %s, %s, %s, %s, NOW())
                ON CONFLICT DO NOTHING
                RETURNING id
            """, (module_id, topic_title, ms_learn_url, len(topics_map)))

            row = cursor.fetchone()
            if row:
                topics_map[topic_key] = row["id"]
            else:
                cursor.execute(
                    'SELECT id FROM "Topic" WHERE "moduleId" = %s AND title = %s',
                    (module_id, topic_title)
                )
                row = cursor.fetchone()
                if row:
                    topics_map[topic_key] = row["id"]

        topic_id = topics_map.get(topic_key)

        # Hash question for deduplication
        question_hash = hashlib.sha256(
            q["questionText"].lower().strip().encode()
        ).hexdigest()[:16]

        # Upsert question
        cursor.execute("""
            INSERT INTO "Question" (
                id, "certificationId", "moduleId", "topicId",
                "questionText", "questionType", answers, explanation,
                source, "sourceUrl", "sourceIcon", "documentationLinks",
                difficulty, "communityScore", "isActive", "createdAt", "updatedAt"
            )
            VALUES (
                gen_random_uuid()::text, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, true, NOW(), NOW()
            )
            ON CONFLICT DO NOTHING
        """, (
            cert_id, module_id, topic_id,
            q["questionText"],
            q.get("questionType", "SINGLE_CHOICE"),
            json.dumps(q.get("answers", [])),
            q.get("explanation", ""),
            q.get("source", "COMMUNITY"),
            q.get("sourceUrl"),
            q.get("sourceIcon", "community"),
            json.dumps(q.get("documentationLinks", [])),
            q.get("difficulty", 2),
            q.get("communityScore"),
        ))

        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1} questions...")

    # Update totalModules count
    cursor.execute("""
        UPDATE "Certification"
        SET "totalModules" = (
            SELECT COUNT(*) FROM "Module" WHERE "certificationId" = %s
        )
        WHERE id = %s
    """, (cert_id, cert_id))

    total_q = cursor.execute(
        'SELECT COUNT(*) as count FROM "Question" WHERE "certificationId" = %s',
        (cert_id,)
    )
    row = cursor.fetchone()
    total_count = row["count"] if row else 0

    conn.commit()
    cursor.close()

    print(f"✓ Seeded {cert_code}: {total_count} questions, {len(modules_map)} modules, {len(topics_map)} topics")


def main():
    parser = argparse.ArgumentParser(description="Seed CertDuo database")
    parser.add_argument("--cert", help="Cert code to seed (e.g., az-900)")
    parser.add_argument("--input", help="Path to input JSON file")
    parser.add_argument("--all", action="store_true", help="Seed all certs from output/ directory")
    args = parser.parse_args()

    conn = get_connection()

    try:
        if args.all:
            output_dir = Path(__file__).parent / "output"
            for json_file in sorted(output_dir.glob("*.json")):
                cert_code = json_file.stem.upper()
                with open(json_file) as f:
                    data = json.load(f)
                seed_cert(cert_code, data, conn)
        elif args.cert and args.input:
            with open(args.input) as f:
                data = json.load(f)
            seed_cert(args.cert.upper(), data, conn)
        else:
            parser.print_help()
            sys.exit(1)
    finally:
        conn.close()

    print("\n✓ Database seeding complete!")


if __name__ == "__main__":
    main()
