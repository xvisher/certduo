"""
Scraper for public GitHub practice-question repos (Ditectrev format).

Format parsed:
    ### Question text here?

    - [x] Correct answer
    - [ ] Wrong answer A
    - [ ] Wrong answer B
    - [ ] Wrong answer C

    **[⬆ Back to Top](#table-of-contents)**

No auth, no Playwright, no CAPTCHA — just plain HTTP.
"""

import re
import urllib.request
from typing import Optional


# Raw README URLs for each cert
GITHUB_SOURCES = {
    "AZ-900": (
        "https://raw.githubusercontent.com/Ditectrev/"
        "Microsoft-Azure-AZ-900-Microsoft-Azure-Fundamentals-"
        "Practice-Tests-Exams-Questions-Answers/main/README.md"
    ),
    "AZ-104": (
        "https://raw.githubusercontent.com/Ditectrev/"
        "Microsoft-Azure-AZ-104-Microsoft-Azure-Administrator-"
        "Practice-Tests-Exams-Questions-Answers/main/README.md"
    ),
}


def scrape_github(cert_code: str) -> list[dict]:
    """
    Download and parse practice questions from a public GitHub repo.
    Returns a list of question dicts compatible with seed_database.py.
    """
    url = GITHUB_SOURCES.get(cert_code)
    if not url:
        print(f"  No GitHub source configured for {cert_code}")
        return []

    print(f"  Fetching {url} ...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    except Exception as e:
        print(f"  Failed to fetch GitHub source: {e}")
        return []

    questions = _parse_ditectrev(raw, cert_code)
    print(f"  Parsed {len(questions)} questions from GitHub ({cert_code})")
    return questions


def _parse_ditectrev(markdown: str, cert_code: str) -> list[dict]:
    """
    Parse the Ditectrev markdown format into question dicts.

    Handles two variants:
      1. AZ-900 style: blocks separated by **[⬆ Back to Top]** markers
      2. AZ-104 style: questions separated only by the next ### heading

    Each question block looks like:
        ### Question text?

        - [x] Correct option
        - [ ] Wrong option
        ...
    """
    questions = []

    # Strategy: split the whole file on ### headings to get blocks.
    # Each block = the heading text + everything until the next ###.
    # We prepend "### " back so _parse_block can find the heading.
    parts = re.split(r"(?=^### )", markdown, flags=re.MULTILINE)

    for part in parts:
        part = part.strip()
        if not part.startswith("### "):
            continue
        # Strip trailing "Back to Top" lines and image lines before parsing
        part = re.sub(r"\*\*\[.*?Back to Top.*?\]\(.*?\)\*\*", "", part, flags=re.IGNORECASE)
        part = re.sub(r"!\[.*?\]\(.*?\)", "", part)  # remove image markdown
        q = _parse_block(part.strip(), cert_code)
        if q:
            questions.append(q)

    return questions


def _parse_block(block: str, cert_code: str) -> Optional[dict]:
    """Parse a single question block."""
    if not block:
        return None

    lines = [l.rstrip() for l in block.splitlines()]

    # Find the question heading (### ...)
    question_text = None
    answer_start = 0
    for i, line in enumerate(lines):
        if line.startswith("### "):
            # Collect multi-line question (some span more than one line)
            q_lines = [line[4:].strip()]
            j = i + 1
            while j < len(lines) and lines[j] and not lines[j].startswith("- ["):
                if lines[j].strip():
                    q_lines.append(lines[j].strip())
                j += 1
            question_text = " ".join(q_lines).strip()
            answer_start = i + 1
            break

    if not question_text or len(question_text) < 10:
        return None

    # Parse answer options
    answers = []
    letter = ord('a')
    for line in lines[answer_start:]:
        # Match "- [x] Text" (correct) or "- [ ] Text" (wrong)
        m = re.match(r"^-\s*\[(x| )\]\s*(.+)", line, re.IGNORECASE)
        if m:
            is_correct = m.group(1).lower() == "x"
            text = m.group(2).strip()
            # Remove trailing period if present
            text = text.rstrip(".")
            if text:
                answers.append({
                    "id": chr(letter),
                    "text": text,
                    "isCorrect": is_correct,
                })
                letter += 1

    if len(answers) < 2:
        return None

    # Ensure exactly one correct answer (use first [x] if multiple)
    correct_count = sum(1 for a in answers if a["isCorrect"])
    if correct_count == 0:
        answers[0]["isCorrect"] = True
    elif correct_count > 1:
        # Keep only the first correct one for SINGLE_CHOICE
        found = False
        for a in answers:
            if a["isCorrect"]:
                if found:
                    a["isCorrect"] = False
                else:
                    found = True

    # Guess difficulty from question length (simple heuristic)
    difficulty = 1 if len(question_text) < 80 else (3 if len(question_text) > 200 else 2)

    return {
        "questionText": question_text,
        "questionType": "SINGLE_CHOICE",
        "answers": answers,
        "explanation": "",
        "source": "COMMUNITY",
        "sourceUrl": GITHUB_SOURCES.get(cert_code, ""),
        "communityScore": None,
        "documentationLinks": [],
        "module": "General",
        "topic": "General",
        "difficulty": difficulty,
    }
