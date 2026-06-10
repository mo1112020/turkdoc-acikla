"""Groq API integration for explaining Turkish government documents."""

import os
import re

from dotenv import load_dotenv
from groq import APITimeoutError, Groq

load_dotenv()

MODEL = "llama-3.3-70b-versatile"
MAX_RETRIES = 1

TURKISH_CHARS = set("çğıöşüÇĞİÖŞÜ")
TURKISH_WORDS = {
    "ve", "bir", "bu", "için", "ile", "olan", "tarafından", "sayın",
    "tarih", "numara", "başvuru", "belge", "resmi", "kurum", "müdürlük",
    "bakanlık", "belediye", "vergi", "ikamet", "ödeme", "son", "gün",
}


def build_prompt(turkish_text: str, language: str) -> str:
    return f"""
You are an expert assistant specializing in Turkish bureaucracy, 
government documents, and immigration law. 

A foreign resident in Turkey has received the following official 
Turkish document and needs help understanding it:

---
{turkish_text}
---

Please respond ONLY in {language} and structure your response 
EXACTLY as follows:

DOCUMENT TYPE: [what kind of document this is]
SENT BY: [which government body or institution]

EXPLANATION:
[Explain in 3-5 simple sentences what this document means. 
Avoid legal jargon. Write as if explaining to someone who 
has no knowledge of Turkish law or bureaucracy.]

URGENCY: [LOW / MEDIUM / HIGH]
REASON: [One sentence explaining why]

DEADLINES:
[List any dates or timeframes mentioned. If none, write "No deadline detected."]

WHAT YOU SHOULD DO:
1. [First action]
2. [Second action]
3. [Third action]
[Add more if needed]

IMPORTANT CONTACTS:
[List any relevant government offices, phone numbers, or 
websites the person should contact based on this document type]

DISCLAIMER:
This is an AI-generated explanation for informational purposes 
only. It is not legal advice. For important matters, please 
consult a qualified lawyer or official interpreter in Turkey.
"""


def _get_api_key() -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key.strip() == "your_api_key_here":
        env = os.getenv("ENVIRONMENT", "development").lower()
        if env == "production":
            raise EnvironmentError("AI service is not configured.")
        raise EnvironmentError(
            "No Groq API key found.\n\n"
            "To set up your API key:\n"
            "  1. Copy .env.example to .env\n"
            "  2. Get a free key at https://console.groq.com/\n"
            "  3. Set GROQ_API_KEY=your_key in .env"
        )
    return api_key


def is_likely_turkish(text: str) -> bool:
    """Heuristic check for whether text appears to be Turkish."""
    lower = text.lower()
    words = set(re.findall(r"[a-zçğıöşü]+", lower))
    turkish_word_hits = len(words & TURKISH_WORDS)
    turkish_char_hits = sum(1 for c in text if c in TURKISH_CHARS)
    return turkish_char_hits >= 2 or turkish_word_hits >= 3


def parse_response(response_text: str) -> dict:
    """Parse structured LLM response into a dictionary."""
    sections = {
        "document_type": "",
        "sent_by": "",
        "explanation": "",
        "urgency": "MEDIUM",
        "reason": "",
        "deadlines": "",
        "next_steps": [],
        "contacts": "",
        "disclaimer": (
            "This is an AI explanation, not legal advice. "
            "Consult a professional for important matters."
        ),
        "raw": response_text,
    }

    doc_type_match = re.search(r"DOCUMENT TYPE:\s*(.+)", response_text)
    if doc_type_match:
        sections["document_type"] = doc_type_match.group(1).strip()

    sent_by_match = re.search(r"SENT BY:\s*(.+)", response_text)
    if sent_by_match:
        sections["sent_by"] = sent_by_match.group(1).strip()

    explanation_match = re.search(
        r"EXPLANATION:\s*\n(.*?)(?=\nURGENCY:)", response_text, re.DOTALL
    )
    if explanation_match:
        sections["explanation"] = explanation_match.group(1).strip()

    urgency_match = re.search(r"URGENCY:\s*(LOW|MEDIUM|HIGH)", response_text, re.IGNORECASE)
    if urgency_match:
        sections["urgency"] = urgency_match.group(1).upper()

    reason_match = re.search(r"REASON:\s*(.+)", response_text)
    if reason_match:
        sections["reason"] = reason_match.group(1).strip()

    deadlines_match = re.search(
        r"DEADLINES:\s*\n(.*?)(?=\nWHAT YOU SHOULD DO:)", response_text, re.DOTALL
    )
    if deadlines_match:
        sections["deadlines"] = deadlines_match.group(1).strip()

    steps_match = re.search(
        r"WHAT YOU SHOULD DO:\s*\n(.*?)(?=\nIMPORTANT CONTACTS:)", response_text, re.DOTALL
    )
    if steps_match:
        steps_text = steps_match.group(1).strip()
        sections["next_steps"] = [
            re.sub(r"^\d+\.\s*", "", line).strip()
            for line in steps_text.splitlines()
            if re.match(r"^\d+\.", line.strip())
        ]

    contacts_match = re.search(
        r"IMPORTANT CONTACTS:\s*\n(.*?)(?=\nDISCLAIMER:)", response_text, re.DOTALL
    )
    if contacts_match:
        sections["contacts"] = contacts_match.group(1).strip()

    return sections


def explain_document(turkish_text: str, language: str = "english") -> dict:
    """Send document text to Groq and return parsed explanation."""
    api_key = _get_api_key()
    client = Groq(api_key=api_key, timeout=60.0)
    prompt = build_prompt(turkish_text, language)

    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            completion = client.chat.completions.create(
                model=MODEL,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            response_text = completion.choices[0].message.content or ""
            return parse_response(response_text)
        except APITimeoutError as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                continue
            raise TimeoutError(
                "The API request timed out after retrying.\n"
                "Please check your internet connection and try again later."
            ) from exc

    raise last_error  # type: ignore[misc]
