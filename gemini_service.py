"""Grounded summaries and answers using the Gemini API."""

from __future__ import annotations

import os
import re


MODEL = "gemini-3.5-flash-lite"


class AnalysisError(Exception):
    """An LLM analysis request could not be completed."""


def _generate(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise AnalysisError("Set GEMINI_API_KEY in your local environment to enable analysis.")
    try:
        from google import genai
        from google.genai.errors import APIError
    except ImportError as exc:
        raise AnalysisError("Gemini support is not installed. Install the project requirements.") from exc
    stage = "creating the Gemini client"
    try:
        client = genai.Client(api_key=api_key)
        stage = "sending the request"
        response = client.models.generate_content(
            model=MODEL,
            contents=(
                "Write readable plain text only. Do not use Markdown markers, code fences, "
                "or LaTeX notation. Express mathematical symbols and formulas in ordinary "
                "words when needed.\n\n" + prompt
            ),
        )
        stage = "reading the model response"
        result = (response.text or "").strip()
        if not result:
            raise AnalysisError("The model returned no text. Please try again.")
        return result
    except AnalysisError:
        raise
    except APIError as exc:
        raise AnalysisError(_api_error_message(exc.code)) from exc
    except Exception as exc:
        raise AnalysisError(
            f"Gemini failed while {stage} ({type(exc).__name__}). "
            "Share this error label so the issue can be diagnosed."
        ) from exc


def _api_error_message(code: int) -> str:
    if code in (400, 413):
        return f"Gemini rejected the request (HTTP {code}). Try a shorter paper or a different model."
    if code in (401, 403):
        return f"Gemini rejected the API key or project access (HTTP {code}). Check the key's project and API permissions."
    if code == 402:
        return "Gemini billing or prepaid credits need attention (HTTP 402). Check the project in AI Studio."
    if code == 404:
        return f"The configured Gemini model is unavailable to this project (HTTP 404): {MODEL}."
    if code == 429:
        return "Gemini rate limit or quota reached (HTTP 429). Check this project's limits in AI Studio."
    if code in (500, 502, 503, 504):
        return f"Gemini is temporarily unavailable (HTTP {code}). Try again later."
    return f"Gemini API request failed (HTTP {code}). Check the project's status in AI Studio."


def _pages(full_text: str) -> list[tuple[int, str]]:
    parts = re.split(r"\[Page (\d+)\]\n", full_text)
    return [(int(parts[i]), parts[i + 1].strip()) for i in range(1, len(parts) - 1, 2)]


def summarize(title: str, full_text: str) -> str:
    pages = _pages(full_text)
    if not pages:
        raise AnalysisError("This paper has no extracted full text to summarize.")
    chunks = []
    current = ""
    for number, text in pages:
        section = f"\n[Page {number}]\n{text}\n"
        if current and len(current) + len(section) > 28000:
            chunks.append(current)
            current = ""
        current += section[:28000]
    if current:
        chunks.append(current)
    if len(chunks) > 8:
        raise AnalysisError("This paper is too long for the current summary limit.")

    if len(chunks) == 1:
        return _generate(
            "Summarize this research paper using only the supplied full-text excerpt. "
            "Cover the problem, method, evidence/results, and limitations. "
            "Give page numbers for specific claims. Do not invent missing information.\n"
            f"Title: {title}\nPaper text:\n{chunks[0]}"
        )

    partials = []
    for chunk in chunks:
        partials.append(
            _generate(
                "Summarize this portion of a research paper faithfully in 150-250 words. "
                "Include page numbers and preserve concrete methods, results, and limitations.\n"
                f"Title: {title}\nPaper text:\n{chunk}"
            )
        )
    return _generate(
        "Combine these grounded section summaries into one concise paper summary. "
        "Cover problem, method, evidence/results, and limitations. Keep page references. "
        "Use the plain headings Problem:, Method:, Evidence and results:, and Limitations:. "
        "Start directly with Problem: and do not add facts absent from the section summaries.\n"
        f"Title: {title}\nSection summaries:\n" + "\n\n".join(partials)
    )


def answer_question(title: str, full_text: str, question: str) -> str:
    pages = _pages(full_text)
    if not pages:
        raise AnalysisError("This paper has no extracted full text to answer from.")
    terms = {term for term in re.findall(r"[a-z]{4,}", question.lower()) if term not in {
        "what", "which", "where", "when", "does", "this", "paper", "about", "were", "their",
        "with", "from", "that", "have", "they", "using", "used", "main", "major",
    }}
    ranked = sorted(
        pages,
        key=lambda page: sum(page[1].lower().count(term) for term in terms),
        reverse=True,
    )
    selected = {number: text for number, text in ranked[:4]}
    selected[pages[0][0]] = pages[0][1]
    context = "\n\n".join(
        f"[Page {number}]\n{text[:9000]}" for number, text in pages if number in selected
    )
    return _generate(
        "Answer the question using only the paper passages below. Cite page numbers in your answer. "
        "If the passages do not support an answer, say you could not find it in the supplied text. "
        "Do not use outside knowledge.\n"
        f"Title: {title}\nQuestion: {question}\nPassages:\n{context}"
    )
