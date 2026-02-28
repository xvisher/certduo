#!/usr/bin/env python3
"""
Main scraper runner. Runs both Microsoft Learn and ExamTopics scrapers,
normalizes the data, and saves to JSON output files.

Usage:
    python3 run_scraper.py --cert az-900
    python3 run_scraper.py --cert az-900 --sources microsoft examtopics
    python3 run_scraper.py --all
"""

import argparse
import json
import sys
from pathlib import Path

from processors.question_parser import normalize_question, deduplicate_questions
from processors.doc_mapper import find_documentation_links


CERT_NAMES = {
    "AZ-900": "Azure Fundamentals",
    "AZ-104": "Azure Administrator",
    "MD-102": "Endpoint Administrator",
    "MS-102": "Microsoft 365 Administrator",
}

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def run_scraper(cert_code: str, sources: list):
    cert_code = cert_code.upper()
    print(f"\n{'='*60}")
    print(f"Scraping {cert_code} - {CERT_NAMES.get(cert_code, cert_code)}")
    print(f"Sources: {', '.join(sources)}")
    print("="*60)

    all_questions = []

    if "microsoft" in sources:
        try:
            print("\n[1/2] Scraping Microsoft Learn...")
            from scrapers.microsoft_learn import scrape_microsoft_learn
            ms_questions = scrape_microsoft_learn(cert_code)
            all_questions.extend(ms_questions)
            print(f"  → {len(ms_questions)} questions from Microsoft Learn")
        except Exception as e:
            print(f"  ✗ Microsoft Learn scraping failed: {e}")

    if "examtopics" in sources:
        try:
            print("\n[2/2] Scraping ExamTopics...")
            from scrapers.examtopics import scrape_examtopics
            et_questions = scrape_examtopics(cert_code)
            all_questions.extend(et_questions)
            print(f"  → {len(et_questions)} questions from ExamTopics")
        except Exception as e:
            print(f"  ✗ ExamTopics scraping failed: {e}")

    if not all_questions:
        print("No questions scraped.")
        return

    # Normalize questions
    print(f"\nNormalizing {len(all_questions)} questions...")
    normalized = []
    skipped = 0

    for q in all_questions:
        try:
            norm = normalize_question(q)
            # Add documentation links if missing
            if not norm.get("documentationLinks"):
                doc_links = find_documentation_links(norm["questionText"], cert_code)
                norm["documentationLinks"] = doc_links
            normalized.append(norm)
        except Exception as e:
            skipped += 1

    print(f"  → {len(normalized)} valid, {skipped} skipped")

    # Deduplicate
    deduped = deduplicate_questions(normalized)
    print(f"  → {len(deduped)} after deduplication")

    # Save output
    output = {
        "certification": cert_code,
        "name": CERT_NAMES.get(cert_code, cert_code),
        "description": f"Prepare for the Microsoft {CERT_NAMES.get(cert_code, cert_code)} certification.",
        "questions": deduped,
    }

    output_file = OUTPUT_DIR / f"{cert_code.lower()}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n✓ Saved {len(deduped)} questions to {output_file}")
    return output_file


def main():
    parser = argparse.ArgumentParser(description="CertDuo scraper")
    parser.add_argument("--cert", help="Cert code (e.g., az-900)")
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=["microsoft", "examtopics"],
        default=["microsoft", "examtopics"],
        help="Which sources to scrape",
    )
    parser.add_argument("--all", action="store_true", help="Scrape all certifications")
    args = parser.parse_args()

    if args.all:
        for cert_code in CERT_NAMES.keys():
            run_scraper(cert_code, args.sources)
    elif args.cert:
        run_scraper(args.cert.upper(), args.sources)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
