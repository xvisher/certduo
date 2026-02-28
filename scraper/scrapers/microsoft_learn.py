"""
Scraper for Microsoft Learn practice assessments.
Extracts questions, answers, explanations, and documentation links.
"""

import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup


CERT_URLS = {
    "AZ-900": "https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/practice/assessment",
    "AZ-104": "https://learn.microsoft.com/en-us/credentials/certifications/azure-administrator/practice/assessment",
    "MD-102": "https://learn.microsoft.com/en-us/credentials/certifications/modern-desktop/practice/assessment",
    "MS-102": "https://learn.microsoft.com/en-us/credentials/certifications/m365-enterprise-administrator/practice/assessment",
}


def scrape_microsoft_learn(cert_code: str, max_questions: int = 100) -> list[dict]:
    """
    Scrape practice assessment questions from Microsoft Learn.
    Returns a list of question dicts.
    """
    url = CERT_URLS.get(cert_code)
    if not url:
        raise ValueError(f"Unknown cert code: {cert_code}")

    questions = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()

        print(f"Navigating to {url}...")
        page.goto(url, wait_until="networkidle", timeout=60000)
        time.sleep(3)

        # Accept cookies if prompted
        try:
            page.click("button#accept-cookie", timeout=3000)
        except Exception:
            pass

        # Start assessment if button exists
        try:
            page.click("button:has-text('Start assessment')", timeout=5000)
            time.sleep(2)
        except Exception:
            pass

        question_count = 0

        while question_count < max_questions:
            try:
                page.wait_for_selector(".assessment-question", timeout=10000)
            except PlaywrightTimeoutError:
                print("No more questions found.")
                break

            html = page.content()
            soup = BeautifulSoup(html, "lxml")

            question_el = soup.select_one(".assessment-question")
            if not question_el:
                break

            # Extract question text
            question_text_el = question_el.select_one(".question-text, h2, .question-body p")
            question_text = question_text_el.get_text(strip=True) if question_text_el else ""

            if not question_text:
                print("Could not extract question text, skipping.")
                break

            # Extract answer options
            answers = []
            option_els = question_el.select(".answer-option, .choice-item, li.option")
            for i, option in enumerate(option_els):
                option_text = option.get_text(strip=True)
                option_id = chr(ord('a') + i)
                # Correct answer is usually marked with aria-checked or a class
                is_correct = (
                    option.get("aria-checked") == "true"
                    or "correct" in option.get("class", [])
                    or option.select_one(".correct-indicator") is not None
                )
                answers.append({
                    "id": option_id,
                    "text": option_text,
                    "isCorrect": is_correct
                })

            # Extract explanation
            explanation_el = question_el.select_one(".explanation, .rationale, .answer-explanation")
            explanation = explanation_el.get_text(strip=True) if explanation_el else ""

            # Extract documentation links
            doc_links = []
            link_els = question_el.select("a[href*='learn.microsoft.com']")
            for link_el in link_els:
                href = link_el.get("href", "")
                title = link_el.get_text(strip=True)
                if href and title:
                    doc_links.append({"url": href, "title": title})

            # Extract module/topic from page context
            breadcrumb_el = soup.select_one(".breadcrumb, nav.breadcrumb")
            module_name = ""
            if breadcrumb_el:
                crumbs = breadcrumb_el.select("li")
                if len(crumbs) >= 2:
                    module_name = crumbs[-2].get_text(strip=True)

            question_data = {
                "questionText": question_text,
                "questionType": "SINGLE_CHOICE",
                "answers": answers,
                "explanation": explanation,
                "source": "MICROSOFT",
                "sourceUrl": url,
                "documentationLinks": doc_links,
                "module": module_name or "General",
                "topic": module_name or "General",
                "difficulty": 2,
            }

            questions.append(question_data)
            question_count += 1
            print(f"Scraped question {question_count}: {question_text[:60]}...")

            # Click "Next" to advance
            try:
                next_btn = page.query_selector("button:has-text('Next'), button[aria-label='Next question']")
                if next_btn:
                    next_btn.click()
                    time.sleep(1.5)
                else:
                    print("No Next button found, stopping.")
                    break
            except Exception:
                print("Could not navigate to next question.")
                break

        browser.close()

    print(f"Scraped {len(questions)} questions from Microsoft Learn for {cert_code}")
    return questions
