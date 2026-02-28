"""
Scraper for ExamTopics community questions.
Extracts questions, answers, community votes, and discussion links.

Note: ExamTopics content exists in a legal gray area.
Always paraphrase, link back to source, and maintain DMCA compliance.
"""

import time
import re
from typing import Optional
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


EXAM_PATHS = {
    "AZ-900": "microsoft/az-900",
    "AZ-104": "microsoft/az-104",
    "MD-102": "microsoft/md-102",
    "MS-102": "microsoft/ms-102",
}

BASE_URL = "https://www.examtopics.com/exams"

# Multiple selector patterns — tried in order until one matches
QUESTION_CONTAINER_SELECTORS = [
    ".exam-question-card",
    ".exam-question-card-container",
    ".question-container",
    ".card.exam-question-card-container",
    "[class*='exam-question']",
]

QUESTION_TEXT_SELECTORS = [
    ".card-text",
    ".question-body",
    "p.question",
    ".question-text",
    "[class*='question-text']",
    ".card-body p",
]

ANSWER_OPTION_SELECTORS = [
    ".question-choices li",
    ".answer-option",
    ".choice-item",
    "li.answer",
    "[class*='choice']",
    ".answers-list li",
]

VOTED_ANSWER_SELECTORS = [
    ".voted-answer",
    ".most-voted-answer",
    "[class*='voted']",
    ".correct-answer",
    "[class*='correct']",
    ".community-vote",
]


def scrape_examtopics(cert_code: str, max_pages: int = 60) -> list[dict]:
    """
    Scrape questions from ExamTopics.
    Returns a list of question dicts.
    """
    exam_path = EXAM_PATHS.get(cert_code)
    if not exam_path:
        raise ValueError(f"Unknown cert code: {cert_code}")

    questions = []
    current_page = 1

    with sync_playwright() as p:
        # Use system Google Chrome (properly macOS-signed, avoids Cloudflare)
        # Falls back to Playwright Chromium if Chrome not installed
        try:
            browser = p.chromium.launch(
                channel="chrome",
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--start-maximized",
                ],
            )
        except Exception:
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
            locale="en-US",
            timezone_id="America/New_York",
        )
        page = context.new_page()

        # Comprehensive webdriver/automation hiding
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

        # ── Login gate ────────────────────────────────────────────────────
        # Navigate to login page and wait for user to sign in manually
        print("\n>>> Opening ExamTopics login page...")
        print(">>> Please sign in to your ExamTopics account in the browser window.")
        print(">>> Press ENTER here once you are logged in.\n")
        page.goto("https://www.examtopics.com/login/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)
        input("    [Waiting for login — press ENTER when done] ")
        print()

        while current_page <= max_pages:
            url = f"{BASE_URL}/{exam_path}/view/{current_page}/"
            print(f"Scraping page {current_page}: {url}")

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                # Wait for Cloudflare challenge to complete if present
                time.sleep(6)

                # Dismiss cookie/modal overlays
                for dismiss_sel in [
                    "button[aria-label*='close']",
                    ".modal-close",
                    "#cookie-accept",
                    ".accept-cookies",
                ]:
                    try:
                        btn = page.query_selector(dismiss_sel)
                        if btn:
                            btn.click()
                            time.sleep(0.5)
                    except Exception:
                        pass

            except Exception as e:
                print(f"Failed to load page {current_page}: {e}")
                break

            html = page.content()
            soup = BeautifulSoup(html, "lxml")

            # ── CAPTCHA / login wall detection ────────────────────────────
            # Retry up to 3 times, pausing for user to solve challenge
            page_text = soup.get_text().lower()
            blocked_signals = ["captcha", "verify you are human", "checking your browser",
                               "login", "sign in to continue", "access denied"]
            retry_count = 0
            while not soup.select(QUESTION_CONTAINER_SELECTORS[0]) and \
                    any(sig in page_text for sig in blocked_signals) and \
                    retry_count < 3:
                print(f"\n  ⚠️  Challenge detected on page {current_page}.")
                print("  Please solve the CAPTCHA or log in again in the browser window.")
                input("  Press ENTER when the page is showing questions again: ")
                time.sleep(3)
                html = page.content()
                soup = BeautifulSoup(html, "lxml")
                page_text = soup.get_text().lower()
                retry_count += 1

            # Try each container selector
            question_els = []
            for sel in QUESTION_CONTAINER_SELECTORS:
                candidates = soup.select(sel)
                filtered = [el for el in candidates if _has_question_text(el)]
                if filtered:
                    print(f"  Found {len(filtered)} questions with selector: '{sel}'")
                    question_els = filtered
                    break

            if not question_els:
                print(f"No questions found on page {current_page}. Stopping.")
                body = soup.find("body")
                if body:
                    snippet = body.get_text()[:300].strip()
                    print(f"  Page snippet: {snippet[:200]}")
                break

            for q_el in question_els:
                try:
                    question = _parse_question(q_el, cert_code, current_page)
                    if question:
                        questions.append(question)
                except Exception as e:
                    print(f"  Error parsing question: {e}")
                    continue

            print(f"  Page {current_page}: {len(questions)} total questions so far")
            current_page += 1
            time.sleep(2)

        browser.close()

    print(f"Total questions scraped from ExamTopics for {cert_code}: {len(questions)}")
    return questions


def _has_question_text(el) -> bool:
    """Return True if element looks like it contains a real question."""
    text = el.get_text(strip=True)
    return len(text) > 50 and ("?" in text or len(text) > 100)


def _parse_question(q_el, cert_code: str, page_num: int) -> Optional[dict]:
    """Parse a single question element using multiple selector fallbacks."""

    # ── Question text ──────────────────────────────────────────────────────
    question_text = None
    for sel in QUESTION_TEXT_SELECTORS:
        el = q_el.select_one(sel)
        if el:
            text = el.get_text(separator=" ", strip=True)
            if len(text) > 15:
                question_text = text
                break

    # Fallback: first paragraph with sufficient length
    if not question_text:
        for p in q_el.find_all("p"):
            text = p.get_text(separator=" ", strip=True)
            if len(text) > 15:
                question_text = text
                break

    if not question_text or len(question_text) < 10:
        return None

    # ── Answer options ─────────────────────────────────────────────────────
    answers = []
    for sel in ANSWER_OPTION_SELECTORS:
        option_els = q_el.select(sel)
        if len(option_els) >= 2:
            for i, opt in enumerate(option_els[:6]):
                opt_text = opt.get_text(separator=" ", strip=True)
                # Strip leading "A.", "B)", "1." etc.
                opt_text = re.sub(r'^[A-Za-z0-9][.)]\s*', '', opt_text).strip()
                if opt_text and len(opt_text) > 1:
                    answers.append({
                        "id": chr(ord('a') + i),
                        "text": opt_text,
                        "isCorrect": False,
                    })
            if len(answers) >= 2:
                break

    if len(answers) < 2:
        return None

    # ── Community vote / correct answer ───────────────────────────────────
    community_score = None
    for sel in VOTED_ANSWER_SELECTORS:
        voted_el = q_el.select_one(sel)
        if voted_el:
            voted_text = voted_el.get_text(strip=True)
            # "A (85%)" or "Correct: B"
            match = re.search(r'\b([A-D])\b.*?(\d{1,3})%', voted_text, re.IGNORECASE)
            if not match:
                match = re.search(r'([A-D])\s*\(?(\d{1,3})%\)?', voted_text)
            if match:
                voted_letter = match.group(1).lower()
                community_score = float(match.group(2))
                for ans in answers:
                    if ans["id"] == voted_letter:
                        ans["isCorrect"] = True
                break
            # Just a letter, no percentage
            letter_match = re.search(r'\b([A-D])\b', voted_text)
            if letter_match:
                voted_letter = letter_match.group(1).lower()
                for ans in answers:
                    if ans["id"] == voted_letter:
                        ans["isCorrect"] = True
                break

    # Default to first option if no correct answer found
    if not any(a["isCorrect"] for a in answers):
        answers[0]["isCorrect"] = True

    source_url = f"{BASE_URL}/{EXAM_PATHS.get(cert_code, '')}/view/{page_num}/"

    return {
        "questionText": question_text,
        "questionType": "SINGLE_CHOICE",
        "answers": answers,
        "explanation": "",
        "source": "EXAMTOPICS",
        "sourceUrl": source_url,
        "communityScore": community_score,
        "documentationLinks": [],
        "module": "General",
        "topic": "General",
        "difficulty": 2,
    }
