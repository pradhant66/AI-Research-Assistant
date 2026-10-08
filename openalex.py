"""Paper search and metadata normalization for the OpenAlex Works API."""

from __future__ import annotations

import re

import requests


API_BASE = "https://api.openalex.org/works"
WORK_ID = re.compile(r"W\d+\Z")


class PaperSearchError(Exception):
    """A paper search could not be completed."""


def _abstract_from_index(index: dict | None) -> str:
    if not index:
        return ""
    positions = [(position, word) for word, offsets in index.items() for position in offsets]
    positions.sort(key=lambda item: item[0])
    return " ".join(word for _, word in positions)


def normalize_work(work: dict) -> dict:
    """Return only fields the application needs from an OpenAlex work."""
    primary = work.get("primary_location") or {}
    open_access = work.get("best_oa_location") or {}
    authors = [
        item.get("author", {}).get("display_name", "")
        for item in work.get("authorships") or []
    ]
    authors = [name for name in authors if name]
    return {
        "external_id": work.get("id", ""),
        "work_id": (work.get("id") or "").rsplit("/", 1)[-1],
        "title": work.get("title") or "Untitled paper",
        "authors": ", ".join(authors) or "Authors unavailable",
        "year": work.get("publication_year"),
        "abstract": _abstract_from_index(work.get("abstract_inverted_index")),
        "paper_url": work.get("doi") or primary.get("landing_page_url") or work.get("id", ""),
        "pdf_url": open_access.get("pdf_url") or "",
    }


def _get(url: str, params: dict | None = None) -> dict:
    try:
        response = requests.get(
            url,
            params=params,
            headers={"User-Agent": "HW1-AI-Research-Assistant/0.1 (student project)"},
            timeout=12,
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        raise PaperSearchError("OpenAlex is unavailable right now. Please try again.") from exc


def search_papers(query: str) -> list[dict]:
    query = query.strip()
    if not query:
        return []
    payload = _get(
        API_BASE,
        {
            "search": query,
            "filter": "type:article|preprint|conference-paper,has_abstract:true",
            "per_page": 12,
        },
    )
    return [normalize_work(work) for work in payload.get("results", [])]


def get_paper(work_id: str) -> dict:
    if not WORK_ID.fullmatch(work_id):
        raise PaperSearchError("Invalid paper identifier.")
    return normalize_work(_get(f"{API_BASE}/{work_id}"))
