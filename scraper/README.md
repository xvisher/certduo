# CertDuo Scraper

This is a standalone Python scraper project for seeding the CertDuo database.

## Setup

```bash
cd scraper
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

## Usage

### 1. Scrape questions

```bash
# Scrape a single certification
python run_scraper.py --cert az-900

# Scrape only Microsoft Learn questions
python run_scraper.py --cert az-900 --sources microsoft

# Scrape all certifications
python run_scraper.py --all
```

This will save scraped data to `output/az-900.json`, etc.

### 2. Seed the database

```bash
# Seed a single cert
python seed_database.py --cert az-900 --input output/az-900.json

# Seed all certs from output/ directory
python seed_database.py --all
```

## Output Format

Each output JSON has the structure:

```json
{
  "certification": "AZ-900",
  "name": "Azure Fundamentals",
  "description": "...",
  "questions": [
    {
      "questionText": "Which cloud model...",
      "questionType": "SINGLE_CHOICE",
      "answers": [
        { "id": "a", "text": "Public cloud", "isCorrect": true },
        ...
      ],
      "explanation": "...",
      "source": "MICROSOFT",
      "sourceUrl": "https://learn.microsoft.com/...",
      "documentationLinks": [
        { "url": "https://learn.microsoft.com/...", "title": "Cloud Models" }
      ],
      "module": "Cloud Concepts",
      "topic": "Cloud Models",
      "difficulty": 2,
      "communityScore": null
    }
  ]
}
```

## Legal Notes

- Microsoft Learn content is publicly accessible but subject to Microsoft's Terms of Service.
  Consider paraphrasing questions rather than copying verbatim.
- ExamTopics content is community-sourced and exists in a legal gray area.
  Always link back to the source and maintain a DMCA/takedown process.
- See CERTDUO_SPEC.md → Legal Considerations for more details.
