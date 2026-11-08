"""Round 2 cases guided by uncovered request and download branches."""

from contextlib import closing
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest
import requests


def read_row(web, paper_id):
    with closing(web.connect_db()) as db:
        return db.execute("SELECT * FROM papers WHERE id = ?", (paper_id,)).fetchone()


def download(chunks, error=None):
    response = MagicMock()
    response.__enter__.return_value = response
    response.__exit__.return_value = False
    response.iter_content.return_value = chunks
    if error:
        response.raise_for_status.side_effect = error
    return response


def test_save_lookup_failure_preserves_library_and_query(client, web, add_paper, monkeypatch):
    paper_id = add_paper()
    before = dict(read_row(web, paper_id))
    monkeypatch.setattr(web, "get_paper", Mock(side_effect=web.PaperSearchError("Lookup unavailable")))
    response = client.post("/save/W456", data={"q": "testing"})
    assert response.status_code == 302
    assert response.headers["Location"] == "/?q=testing"
    monkeypatch.setattr(web, "search_papers", Mock(return_value=[]))
    assert "Lookup unavailable" in client.get(response.headers["Location"]).get_data(as_text=True)
    assert dict(read_row(web, paper_id)) == before
    with closing(web.connect_db()) as db:
        assert db.execute("SELECT COUNT(*) FROM papers").fetchone()[0] == 1


@pytest.mark.parametrize("action", ["edit", "remove", "reextract", "attach", "import-pdf", "summarize", "ask"])
def test_missing_paper_post_actions_return_404(client, action):
    assert client.post(f"/papers/999/{action}", data={"question": "What evidence?"}).status_code == 404


@pytest.mark.parametrize("pdf_url", ["", "http://example.org/paper.pdf"])
def test_import_without_https_link_never_downloads(client, web, add_paper, monkeypatch, pdf_url):
    paper_id = add_paper(pdf_url=pdf_url)
    fetch = Mock()
    monkeypatch.setattr(web.requests, "get", fetch)
    before = dict(read_row(web, paper_id))
    response = client.post(f"/papers/{paper_id}/import-pdf", follow_redirects=True)
    assert "No direct open-access PDF is available" in response.get_data(as_text=True)
    assert dict(read_row(web, paper_id)) == before
    fetch.assert_not_called()


def test_import_retries_an_alternate_after_publisher_rejection(client, web, add_paper, make_pdf, monkeypatch):
    primary = "https://example.org/blocked.pdf"
    alternate = "https://example.org/alternate.pdf"
    paper_id = add_paper(pdf_url=primary, summary="Stale summary")
    blocked = download([], requests.HTTPError("Controlled publisher rejection"))
    content = make_pdf()
    available = download([content[:100], content[100:]])
    fetch = Mock(side_effect=[blocked, available])
    monkeypatch.setattr(web.requests, "get", fetch)
    monkeypatch.setattr(web, "get_pdf_urls", Mock(return_value=[primary, alternate]))
    response = client.post(f"/papers/{paper_id}/import-pdf", follow_redirects=True)
    assert "imported and processed" in response.get_data(as_text=True)
    assert [call.args[0] for call in fetch.call_args_list] == [primary, alternate]
    row = read_row(web, paper_id)
    assert row["pdf_url"] == alternate
    assert "[Page 2]" in row["full_text"]
    assert row["summary"] == ""
    assert Path(row["pdf_path"]).read_bytes() == content
    assert list(web.app.config["UPLOAD_FOLDER"].glob("*.pdf")) == [Path(row["pdf_path"])]
    blocked.iter_content.assert_not_called()


@pytest.mark.parametrize("external_id", [None, "https://openalex.org/W123"])
def test_saved_pdf_url_works_without_provider_lookup(client, web, add_paper, make_pdf, monkeypatch, external_id):
    paper_id = add_paper(external_id=external_id)
    lookup = Mock(side_effect=web.PaperSearchError("OpenAlex unavailable"))
    monkeypatch.setattr(web, "get_pdf_urls", lookup)
    monkeypatch.setattr(web.requests, "get", Mock(return_value=download([make_pdf()])))
    response = client.post(f"/papers/{paper_id}/import-pdf", follow_redirects=True)
    assert "imported and processed" in response.get_data(as_text=True)
    assert "[Page 2]" in read_row(web, paper_id)["full_text"]
    if external_id:
        lookup.assert_called_once_with("W123")
    else:
        lookup.assert_not_called()


def test_oversized_import_preserves_record_and_removes_partial_file(client, web, add_paper, monkeypatch):
    paper_id = add_paper(summary="Existing summary")
    before = dict(read_row(web, paper_id))
    monkeypatch.setitem(web.app.config, "MAX_CONTENT_LENGTH", 256)
    monkeypatch.setattr(web, "get_pdf_urls", Mock(return_value=[]))
    # The first chunk is written; the second pushes the stream over the limit.
    response = download([b"a" * 100, b"b" * 200])
    monkeypatch.setattr(web.requests, "get", Mock(return_value=response))
    extract = Mock()
    monkeypatch.setattr(web, "extract_pdf", extract)
    result = client.post(f"/papers/{paper_id}/import-pdf", follow_redirects=True)
    assert "could not be imported" in result.get_data(as_text=True)
    assert dict(read_row(web, paper_id)) == before
    assert list(web.app.config["UPLOAD_FOLDER"].glob("*.pdf")) == []
    extract.assert_not_called()


def test_import_preserves_saved_abstract_if_pdf_has_none(client, web, add_paper, monkeypatch):
    paper_id = add_paper(abstract="Reviewed saved abstract")
    monkeypatch.setattr(web, "get_pdf_urls", Mock(return_value=[]))
    monkeypatch.setattr(web.requests, "get", Mock(return_value=download([b"controlled downloaded bytes"])))
    monkeypatch.setattr(web, "extract_pdf", Mock(return_value={"abstract": "", "full_text": "[Page 1]\nExtracted evidence"}))
    response = client.post(f"/papers/{paper_id}/import-pdf", follow_redirects=True)
    assert "imported and processed" in response.get_data(as_text=True)
    row = read_row(web, paper_id)
    assert row["abstract"] == "Reviewed saved abstract"
    assert row["full_text"] == "[Page 1]\nExtracted evidence"


@pytest.mark.parametrize("file_state", ["no_path", "missing", "outside"])
def test_pdf_view_rejects_unavailable_or_outside_files(client, web, add_paper, tmp_path, file_state):
    if file_state == "no_path":
        stored = ""
    elif file_state == "missing":
        stored = str(web.app.config["UPLOAD_FOLDER"] / "missing.pdf")
    else:
        outside = tmp_path / "original.pdf"
        outside.write_bytes(b"PRIVATE_ORIGINAL_CONTENT")
        stored = str(outside)
    paper_id = add_paper(pdf_path=stored)
    response = client.get(f"/papers/{paper_id}/pdf")
    assert response.status_code == 404
    assert b"PRIVATE_ORIGINAL_CONTENT" not in response.data


@pytest.mark.parametrize("endpoint", ["upload", "attach"])
def test_missing_upload_file_reports_validation_error(client, web, add_paper, endpoint):
    paper_id = add_paper()
    before = dict(read_row(web, paper_id))
    path = "/upload" if endpoint == "upload" else f"/papers/{paper_id}/attach"
    response = client.post(path, follow_redirects=True)
    assert "Choose a PDF file." in response.get_data(as_text=True)
    assert dict(read_row(web, paper_id)) == before
    assert list(web.app.config["UPLOAD_FOLDER"].glob("*.pdf")) == []


def test_delete_file_error_is_reported_after_record_removal(client, web, add_paper, monkeypatch):
    folder = web.app.config["UPLOAD_FOLDER"]
    folder.mkdir()
    path = folder / "stored.pdf"
    path.write_bytes(b"stored copy")
    paper_id = add_paper(pdf_path=str(path))
    original_unlink = Path.unlink
    def fail_for_stored_pdf(self, *args, **kwargs):
        if self == path:
            raise OSError("Controlled deletion failure")
        return original_unlink(self, *args, **kwargs)
    monkeypatch.setattr(Path, "unlink", fail_for_stored_pdf)
    response = client.post(f"/papers/{paper_id}/remove", follow_redirects=True)
    assert "Paper removed, but its stored PDF could not be deleted" in response.get_data(as_text=True)
    assert read_row(web, paper_id) is None
    assert path.read_bytes() == b"stored copy"
