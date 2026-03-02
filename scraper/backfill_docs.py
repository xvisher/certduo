"""
Backfill documentationLinks for existing questions that have empty/null docs.
Reads questions from the DB, runs doc_mapper, writes back.
"""

import json
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Add scraper dir to path for processors
sys.path.insert(0, os.path.dirname(__file__))
from processors.doc_mapper import find_documentation_links

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env.local"))

DATABASE_URL = os.environ["DATABASE_URL"]


def main():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Get all questions with empty documentationLinks, grouped by cert code
    cur.execute("""
        SELECT q.id, q."questionText", c.code
        FROM "Question" q
        JOIN "Certification" c ON q."certificationId" = c.id
        WHERE q."documentationLinks" IS NULL
           OR q."documentationLinks"::text = '[]'
           OR q."documentationLinks"::text = 'null'
        ORDER BY c.code, q.id
    """)
    rows = cur.fetchall()
    print(f"Found {len(rows)} questions with no documentation links")

    updated = 0
    skipped = 0

    for qid, question_text, cert_code in rows:
        links = find_documentation_links(question_text, cert_code)
        if not links:
            skipped += 1
            continue

        cur.execute(
            'UPDATE "Question" SET "documentationLinks" = %s WHERE id = %s',
            (json.dumps(links), qid)
        )
        updated += 1
        if updated % 50 == 0:
            print(f"  Updated {updated} questions so far...")

    conn.commit()
    cur.close()
    conn.close()

    print(f"\nDone. Updated: {updated}, No match found: {skipped}")
    print(f"Total processed: {len(rows)}")


if __name__ == "__main__":
    main()
