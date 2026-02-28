"""
Question normalizer: deduplicates and normalizes questions into a standard format.
"""

import hashlib
import re
from typing import Optional


def normalize_question(question: dict) -> dict:
    """
    Normalize a raw question dict into the standard format.
    Cleans text, validates answers, generates a content hash.
    """
    text = _clean_text(question.get("questionText", ""))
    if not text:
        raise ValueError("Question text is empty")

    answers = _normalize_answers(question.get("answers", []))
    if not answers:
        raise ValueError("No answers provided")

    if not any(a["isCorrect"] for a in answers):
        raise ValueError("No correct answer marked")

    return {
        "questionText": text,
        "questionType": question.get("questionType", "SINGLE_CHOICE"),
        "answers": answers,
        "explanation": _clean_text(question.get("explanation", "")),
        "source": question.get("source", "COMMUNITY"),
        "sourceUrl": question.get("sourceUrl"),
        "sourceIcon": _get_source_icon(question.get("source", "")),
        "documentationLinks": question.get("documentationLinks", []),
        "module": question.get("module", "General"),
        "topic": question.get("topic", "General"),
        "difficulty": int(question.get("difficulty", 2)),
        "communityScore": question.get("communityScore"),
        "contentHash": _hash_question(text),
    }


def _clean_text(text: str) -> str:
    """Remove extra whitespace and normalize line endings."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _normalize_answers(answers: list) -> list:
    """Normalize answer options."""
    result = []
    seen_texts = set()

    for i, ans in enumerate(answers):
        text = _clean_text(ans.get("text", ""))
        if not text or text in seen_texts:
            continue
        seen_texts.add(text)

        answer_id = ans.get("id") or chr(ord('a') + i)
        result.append({
            "id": answer_id,
            "text": text,
            "isCorrect": bool(ans.get("isCorrect", False)),
        })

    return result


def _get_source_icon(source: str) -> str:
    source_map = {
        "MICROSOFT": "microsoft",
        "EXAMTOPICS": "examtopics",
        "COMMUNITY": "community",
    }
    return source_map.get(source.upper(), "community")


def _hash_question(text: str) -> str:
    """Generate a content hash for deduplication."""
    normalized = re.sub(r'\s+', ' ', text.lower().strip())
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def deduplicate_questions(questions: list[dict]) -> list[dict]:
    """Remove duplicate questions based on content hash."""
    seen_hashes = set()
    unique = []

    for q in questions:
        h = q.get("contentHash") or _hash_question(q.get("questionText", ""))
        if h not in seen_hashes:
            seen_hashes.add(h)
            unique.append(q)

    return unique
