"""Search normalization and provider failures without live OpenAlex calls."""

from unittest.mock import Mock

import pytest
import requests

import openalex


def test_normalize_work_reconstructs_abstract_and_prefers_open_pdf():
    record = openalex.normalize_work({
        "id": "https://openalex.org/W123", "title": "A paper", "publication_year": 2023,
        "authorships": [{"author": {"display_name": "Alice Example"}}],
        "doi": "https://doi.org/10.example/paper",
        "abstract_inverted_index": {"works": [2], "This": [0], "method": [1]},
        "primary_location": {"pdf_url": "https://example.org/publisher.pdf"},
        "best_oa_location": {"pdf_url": "https://example.org/open.pdf"},
    })
    assert record["abstract"] == "This method works"
    assert record["authors"] == "Alice Example"
    assert record["work_id"] == "W123"
    assert record["year"] == 2023
    assert record["pdf_url"] == "https://example.org/open.pdf"
    assert record["paper_url"] == "https://doi.org/10.example/paper"


def test_normalize_missing_fields_has_explicit_fallbacks():
    record = openalex.normalize_work({})
    assert record["title"] == "Untitled paper"
    assert record["authors"] == "Authors unavailable"
    assert record["abstract"] == record["pdf_url"] == record["paper_url"] == ""
    assert record["year"] is None


def test_search_strips_query_and_returns_normalized_results(monkeypatch):
    fetch = Mock(return_value={"results": [{"id": "https://openalex.org/W123", "title": "A paper"}]})
    monkeypatch.setattr(openalex, "_get", fetch)
    result = openalex.search_papers("  attention  ")
    assert result[0]["title"] == "A paper"
    args, _ = fetch.call_args
    assert args[1]["search"] == "attention"
    # Check the intended provider restrictions without fixing clause/type order.
    filters = dict(clause.split(":", 1) for clause in args[1]["filter"].split(","))
    assert set(filters["type"].split("|")) == {"article", "preprint", "conference-paper"}
    assert filters["has_abstract"] == "true"


def test_empty_query_never_requests_provider(monkeypatch):
    fetch = Mock()
    monkeypatch.setattr(openalex, "_get", fetch)
    assert openalex.search_papers("  ") == []
    fetch.assert_not_called()


@pytest.mark.parametrize("work_id", ["", "W123/extra", "https://openalex.org/W123"])
def test_invalid_identifier_is_rejected_before_network(monkeypatch, work_id):
    fetch = Mock()
    monkeypatch.setattr(openalex, "_get", fetch)
    with pytest.raises(openalex.PaperSearchError, match="Invalid paper identifier"):
        openalex.get_paper(work_id)
    fetch.assert_not_called()


@pytest.mark.parametrize("error", [requests.Timeout(), requests.HTTPError(), ValueError("invalid JSON")])
def test_provider_errors_become_user_facing_error(monkeypatch, error):
    response = Mock()
    fetch = Mock(return_value=response)
    if isinstance(error, requests.Timeout):
        fetch.side_effect = error
    elif isinstance(error, ValueError):
        response.json.side_effect = error
    else:
        response.raise_for_status.side_effect = error
    monkeypatch.setattr(openalex.requests, "get", fetch)
    with pytest.raises(openalex.PaperSearchError, match="OpenAlex is unavailable"):
        openalex.search_papers("research")
    fetch.assert_called_once()
    if isinstance(error, requests.Timeout):
        response.raise_for_status.assert_not_called()
        response.json.assert_not_called()


def test_alternate_pdf_urls_are_https_and_distinct(monkeypatch):
    monkeypatch.setattr(openalex, "_get", Mock(return_value={
        "best_oa_location": {"pdf_url": "https://example.org/a.pdf"},
        "locations": [
            {"pdf_url": "https://example.org/a.pdf"},
            {"pdf_url": "http://example.org/insecure.pdf"},
            {"pdf_url": "https://example.org/b.pdf"}, {},
        ],
    }))
    assert openalex.get_pdf_urls("W123") == ["https://example.org/a.pdf", "https://example.org/b.pdf"]


def test_get_by_identifier_fetches_and_normalizes_record(monkeypatch):
    response = Mock()
    response.json.return_value = {
        "id": "https://openalex.org/W123", "title": "Retrieved paper",
        "primary_location": {"landing_page_url": "https://example.org/publication"},
    }
    get = Mock(return_value=response)
    monkeypatch.setattr(openalex.requests, "get", get)
    result = openalex.get_paper("W123")
    assert result["title"] == "Retrieved paper"
    assert result["paper_url"] == "https://example.org/publication"
    assert get.call_args.args[0] == "https://api.openalex.org/works/W123"
    assert get.call_args.kwargs["timeout"] > 0
    response.raise_for_status.assert_called_once()


def test_invalid_identifier_for_alternate_urls_never_fetches(monkeypatch):
    fetch = Mock()
    monkeypatch.setattr(openalex, "_get", fetch)
    with pytest.raises(openalex.PaperSearchError, match="Invalid paper identifier"):
        openalex.get_pdf_urls("W123/other")
    fetch.assert_not_called()
