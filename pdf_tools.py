"""Extract paper text and best-effort metadata from text-based PDFs."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pymupdf


class PDFProcessingError(Exception):
    """A PDF could not be read or did not contain usable text."""


def extract_pdf(path: Path) -> dict:
    try:
        with pymupdf.open(path) as document:
            if not document.is_pdf or document.page_count == 0:
                raise PDFProcessingError("Please upload a valid PDF paper.")
            # PDF block order usually preserves columns better than sort=True.
            pages = [page.get_text("text").strip() for page in document]
            first_page = document[0]
            title, title_bottom = _find_title(first_page, path.stem)
            authors = _find_authors(first_page, title_bottom)
            year = _find_year(pages[0], document.metadata)
            abstract = _find_abstract(pages[0])
    except PDFProcessingError:
        raise
    except Exception as exc:
        raise PDFProcessingError("The PDF could not be opened or processed.") from exc

    if not any(len(page) > 100 for page in pages):
        raise PDFProcessingError(
            "This PDF has little or no selectable text. Please use a text-based paper PDF."
        )

    full_text = "\n\n".join(f"[Page {i}]\n{text}" for i, text in enumerate(pages, 1))
    return {
        "title": title,
        "authors": authors,
        "year": year,
        "abstract": abstract,
        "full_text": full_text,
        "page_count": len(pages),
    }


def _clean(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u200b", "").replace("\u2010", "-").replace("\u2011", "-")
    return re.sub(r"\s+", " ", text).strip()


def _page_lines(page) -> list[dict]:
    lines = []
    for block in page.get_text("dict").get("blocks", []):
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            text = _clean(" ".join(span.get("text", "") for span in spans))
            if text:
                lines.append({
                    "text": text,
                    "size": max((span.get("size", 0) for span in spans), default=0),
                    "x": line["bbox"][0],
                    "top": line["bbox"][1],
                    "bottom": line["bbox"][3],
                })
    return lines


def _find_title(page, fallback: str) -> tuple[str, float]:
    lines = _page_lines(page)
    candidates = [
        line for line in lines
        if 14 <= line["size"] <= 40
        and 55 <= line["top"] <= page.rect.height * 0.45
        and line["x"] >= page.rect.width * 0.06
        and 8 <= len(line["text"]) <= 180
        and not re.match(r"(?i)^(arxiv|doi|abstract|research|open access)", line["text"])
    ]
    if not candidates:
        return fallback, 0
    largest = max(line["size"] for line in candidates)
    title_lines = [line for line in candidates if abs(line["size"] - largest) < 0.5]
    title_lines.sort(key=lambda line: (line["top"], line["x"]))
    group = [title_lines[0]]
    for line in title_lines[1:]:
        if line["top"] - group[-1]["bottom"] > largest * 1.5:
            break
        group.append(line)
    return _clean(" ".join(line["text"] for line in group)), max(line["bottom"] for line in group)


def _find_authors(page, title_bottom: float) -> str:
    lines = _page_lines(page)
    abstract_top = min(
        (line["top"] for line in lines if re.match(r"(?i)^abstract\b", line["text"])),
        default=page.rect.height * 0.5,
    )
    candidates = [
        line for line in lines
        if title_bottom < line["top"] < abstract_top
        and line["x"] >= page.rect.width * 0.06
        and not re.match(r"(?i)^(meta ai|google (brain|research)|university|department|institute|school|research|open access|doi|https?://)", line["text"])
        and "@" not in line["text"]
        and len(line["text"]) > 8
    ]
    if not candidates:
        return "Authors unavailable"
    candidates.sort(key=lambda line: (line["top"], line["x"]))
    text = _clean(", ".join(line["text"] for line in candidates))
    text = re.sub(r"(?<=\w)\s*[∗*†‡]+", "", text)
    text = re.sub(r"(?<=\w)\s*\d+(?:,\d+)*\*?(?=\s*(?:,|and|$))", "", text)
    text = re.sub(r"\s+,", ",", text)
    return _clean(text)


def _find_year(first_text: str, metadata: dict) -> int | None:
    arxiv = re.search(r"(?i)arxiv:\s*(\d{2})\d{2}\.\d+", first_text)
    if arxiv:
        return 2000 + int(arxiv.group(1))
    opening = "\n".join(first_text.splitlines()[:12])
    year = re.search(r"\b(?:19|20)\d{2}\b", opening)
    if year:
        return int(year.group())
    created = re.search(r"D:((?:19|20)\d{2})", metadata.get("creationDate") or "")
    return int(created.group(1)) if created else None


def _find_abstract(first_text: str) -> str:
    lines = first_text.splitlines()
    start = next((i for i, line in enumerate(lines) if re.match(r"(?i)^\s*abstract\b", line)), None)
    if start is None:
        return ""
    content = []
    for index, line in enumerate(lines[start + 1:], start + 1):
        if line.strip().isdigit() and index + 1 < len(lines) and re.match(r"(?i)^\s*introduction\b", lines[index + 1]):
            break
        if re.match(r"(?i)^\s*(?:\d+[.\s]+)?(?:introduction|keywords?|scientific contribution)\b", line):
            break
        if re.match(r"(?i)^\s*(?:[∗*†‡]|\d+(?:st|nd|rd|th)\s+conference\b|arxiv:)", line):
            break
        content.append(line.strip())
    text = "\n".join(content)
    text = re.sub(r"-\n(?=to-|and-|or-)", "-", text)
    text = re.sub(r"(?<=[a-z])-\n(?=[a-z])", "", text)
    text = re.sub(r"-\n(?=\d)", "-", text)
    text = re.sub(r"(?<=\w)[¹²³1-9](?=\.$)", "", text)
    return _clean(text)
