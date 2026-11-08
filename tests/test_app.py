"""HTTP workflows with real SQLite and PDFs, controlled external services."""

from io import BytesIO
from contextlib import closing
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests


def get_row(web, paper_id):
    with closing(web.connect_db()) as db:
        return db.execute("SELECT * FROM papers WHERE id = ?", (paper_id,)).fetchone()


def test_search_renders_metadata_and_links(client, web, paper_data, monkeypatch):
    search = Mock(return_value=[paper_data])
    monkeypatch.setattr(web, "search_papers", search)
    response = client.get("/?q=  reliable  ")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    for field in ("title", "authors", "abstract", "paper_url", "pdf_url"):
        assert paper_data[field] in html
    assert "2023" in html
    search.assert_called_once_with("reliable")


def test_blank_search_skips_service(client, web, monkeypatch):
    search = Mock()
    monkeypatch.setattr(web, "search_papers", search)
    response = client.get("/?q=   ")
    assert response.status_code == 200
    assert "Find papers worth reading" in response.get_data(as_text=True)
    search.assert_not_called()


def test_search_failure_is_displayed(client, web, monkeypatch):
    monkeypatch.setattr(web, "search_papers", Mock(side_effect=web.PaperSearchError("Search unavailable")))
    response = client.get("/?q=research")
    assert response.status_code == 200
    assert "Search unavailable" in response.get_data(as_text=True)


def test_save_persists_metadata_without_downloading(client, web, paper_data, monkeypatch):
    monkeypatch.setattr(web, "get_paper", Mock(return_value=paper_data))
    response = client.post("/save/W123")
    assert response.status_code == 302
    row = get_row(web, 1)
    assert row["title"] == paper_data["title"]
    assert row["external_id"] == paper_data["external_id"]
    assert row["pdf_url"] == paper_data["pdf_url"]
    assert row["pdf_path"] == row["full_text"] == ""
    assert paper_data["title"] in web.app.test_client().get("/library").get_data(as_text=True)


def test_repeated_save_reuses_record(client, web, paper_data, monkeypatch):
    monkeypatch.setattr(web, "get_paper", Mock(return_value=paper_data))
    first = client.post("/save/W123")
    second = client.post("/save/W123", follow_redirects=True)
    assert first.headers["Location"].endswith("/papers/1")
    assert "already in your library" in second.get_data(as_text=True)
    with closing(web.connect_db()) as db:
        assert db.execute("SELECT COUNT(*) FROM papers").fetchone()[0] == 1


def test_save_matches_uploaded_paper_and_retains_text(client, web, add_paper, paper_data, monkeypatch):
    paper_id = add_paper(external_id=None, full_text="[Page 1]\nExisting extracted text", pdf_path="stored.pdf")
    monkeypatch.setattr(web, "get_paper", Mock(return_value=paper_data))
    response = client.post("/save/W123")
    assert response.headers["Location"].endswith(f"/papers/{paper_id}")
    row = get_row(web, paper_id)
    assert row["external_id"] == paper_data["external_id"]
    assert row["full_text"] == "[Page 1]\nExisting extracted text"
    with closing(web.connect_db()) as db:
        assert db.execute("SELECT COUNT(*) FROM papers").fetchone()[0] == 1


def test_edit_saves_corrections(client, web, add_paper):
    paper_id = add_paper()
    response = client.post(f"/papers/{paper_id}/edit", data={
        "title": " Corrected title ", "authors": " Correct Author ",
        "year": "2015", "abstract": "Correct abstract",
    }, follow_redirects=True)
    assert "Paper details updated" in response.get_data(as_text=True)
    row = get_row(web, paper_id)
    assert (row["title"], row["authors"], row["year"], row["abstract"]) == (
        "Corrected title", "Correct Author", 2015, "Correct abstract",
    )


@pytest.mark.parametrize("changes", [{"title": " "}, {"authors": ""}, {"year": "not-a-year"}])
def test_invalid_edit_preserves_record(client, web, add_paper, changes):
    paper_id = add_paper()
    before = dict(get_row(web, paper_id))
    data = {"title": "New title", "authors": "New Author", "year": "2020", "abstract": "New text"}
    data.update(changes)
    response = client.post(f"/papers/{paper_id}/edit", data=data, follow_redirects=True)
    assert "Enter a title and authors" in response.get_data(as_text=True)
    assert dict(get_row(web, paper_id)) == before


def test_upload_review_and_local_pdf_view(client, web, make_pdf):
    content = make_pdf()
    response = client.post("/upload", data={"pdf": (BytesIO(content), "paper.pdf")}, follow_redirects=True)
    assert "Review the extracted paper details" in response.get_data(as_text=True)
    row = get_row(web, 1)
    assert row["title"] == "Reliable Research Workflows"
    assert "[Page 2]" in row["full_text"]
    assert Path(row["pdf_path"]).read_bytes() == content
    view = client.get("/papers/1/pdf")
    assert view.status_code == 200
    assert view.mimetype == "application/pdf"
    assert view.data == content
    view.close()


@pytest.mark.parametrize("filename,content,message", [
    ("paper.txt", b"text", "Choose a PDF file to upload."),
    ("broken.pdf", b"not a pdf", "The PDF could not be opened or processed."),
])
def test_invalid_upload_leaves_no_record_or_pdf(client, web, filename, content, message):
    response = client.post("/upload", data={"pdf": (BytesIO(content), filename)})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/upload")
    page = client.get(response.headers["Location"])
    assert message in page.get_data(as_text=True)
    with closing(web.connect_db()) as db:
        assert db.execute("SELECT COUNT(*) FROM papers").fetchone()[0] == 0
    assert list(web.app.config["UPLOAD_FOLDER"].glob("*.pdf")) == []


def test_summary_stores_service_result(client, web, add_paper, monkeypatch):
    text = "[Page 1]\nPaper evidence"
    paper_id = add_paper(full_text=text)
    service = Mock(return_value="Problem: Repeatability. Method: Controlled experiments.")
    monkeypatch.setattr(web, "summarize", service)
    response = client.post(f"/papers/{paper_id}/summarize", follow_redirects=True)
    assert "Problem: Repeatability" in response.get_data(as_text=True)
    assert get_row(web, paper_id)["summary"] == service.return_value
    service.assert_called_once_with("Reliable Research Workflows", text)


def test_question_passes_paper_text_and_displays_answer(client, web, add_paper, monkeypatch):
    text = "[Page 1]\nPaper evidence"
    paper_id = add_paper(full_text=text)
    service = Mock(return_value="Controlled experiments (page 1).")
    monkeypatch.setattr(web, "answer_question", service)
    response = client.post(f"/papers/{paper_id}/ask", data={"question": " What was evaluated? "})
    assert response.status_code == 200
    assert service.return_value in response.get_data(as_text=True)
    service.assert_called_once_with("Reliable Research Workflows", text, "What was evaluated?")


def test_empty_question_does_not_call_service(client, web, add_paper, monkeypatch):
    paper_id = add_paper(full_text="[Page 1]\nEvidence")
    service = Mock()
    monkeypatch.setattr(web, "answer_question", service)
    response = client.post(f"/papers/{paper_id}/ask", data={"question": " "}, follow_redirects=True)
    assert "Enter a question" in response.get_data(as_text=True)
    service.assert_not_called()


@pytest.mark.parametrize("action,service_name", [("summarize", "summarize"), ("ask", "answer_question")])
def test_analysis_error_preserves_summary(client, web, add_paper, monkeypatch, action, service_name):
    paper_id = add_paper(full_text="[Page 1]\nEvidence", summary="Previous summary")
    monkeypatch.setattr(web, service_name, Mock(side_effect=web.AnalysisError("Analysis unavailable")))
    response = client.post(f"/papers/{paper_id}/{action}", data={"question": "Why?"}, follow_redirects=True)
    assert "Analysis unavailable" in response.get_data(as_text=True)
    assert get_row(web, paper_id)["summary"] == "Previous summary"


def test_import_downloads_extracts_and_replaces_abstract(client, web, add_paper, make_pdf, monkeypatch):
    paper_id = add_paper(abstract="Unrelated external abstract")
    download = Mock()
    download.__enter__ = Mock(return_value=download)
    download.__exit__ = Mock(return_value=False)
    download.iter_content.return_value = [make_pdf()]
    monkeypatch.setattr(web, "get_pdf_urls", Mock(return_value=[]))
    monkeypatch.setattr(web.requests, "get", Mock(return_value=download))
    response = client.post(f"/papers/{paper_id}/import-pdf", follow_redirects=True)
    assert "imported and processed" in response.get_data(as_text=True)
    row = get_row(web, paper_id)
    assert row["abstract"] == "We evaluate reliable research workflows using repeatable experiments."
    assert "[Page 2]" in row["full_text"]
    assert Path(row["pdf_path"]).is_file()
    assert "Import open-access PDF" not in response.get_data(as_text=True)


def test_import_timeout_preserves_record_and_creates_no_pdf(client, web, add_paper, monkeypatch):
    paper_id = add_paper(summary="Existing summary")
    before = dict(get_row(web, paper_id))
    monkeypatch.setattr(web, "get_pdf_urls", Mock(return_value=[]))
    monkeypatch.setattr(web.requests, "get", Mock(side_effect=requests.Timeout()))
    response = client.post(f"/papers/{paper_id}/import-pdf", follow_redirects=True)
    assert "could not be imported" in response.get_data(as_text=True)
    assert dict(get_row(web, paper_id)) == before
    assert list(web.app.config["UPLOAD_FOLDER"].glob("*.pdf")) == []


@pytest.mark.parametrize("path", ["/papers/999", "/papers/999/pdf", "/papers/999/edit"])
def test_missing_paper_returns_404(client, path):
    assert client.get(path).status_code == 404


def test_remove_preserves_referenced_file_outside_managed_folder(client, web, add_paper, tmp_path):
    original = tmp_path / "user-original.pdf"
    original.write_bytes(b"original outside app-managed storage")
    paper_id = add_paper(pdf_path=str(original))
    response = client.post(f"/papers/{paper_id}/remove", follow_redirects=True)
    assert "Paper removed from your library" in response.get_data(as_text=True)
    assert get_row(web, paper_id) is None
    assert original.read_bytes() == b"original outside app-managed storage"


def test_remove_preserves_pdf_until_last_reference_is_removed(client, web, add_paper):
    folder = web.app.config["UPLOAD_FOLDER"]
    folder.mkdir()
    shared = folder / "shared.pdf"
    shared.write_bytes(b"shared stored copy")
    first = add_paper(pdf_path=str(shared))
    second = add_paper(external_id="https://openalex.org/W456", pdf_path=str(shared))
    client.post(f"/papers/{first}/remove")
    assert get_row(web, first) is None
    assert get_row(web, second)["pdf_path"] == str(shared)
    assert shared.read_bytes() == b"shared stored copy"
    response = client.post(f"/papers/{second}/remove", follow_redirects=True)
    assert "Paper removed from your library" in response.get_data(as_text=True)
    assert get_row(web, second) is None
    assert not shared.exists()


def test_attach_replaces_managed_copy_and_clears_stale_analysis(client, web, add_paper, make_pdf):
    folder = web.app.config["UPLOAD_FOLDER"]
    folder.mkdir()
    old = folder / "old.pdf"
    old.write_bytes(b"previous stored copy")
    paper_id = add_paper(
        title="Manually reviewed title", abstract="Reviewed abstract", pdf_path=str(old),
        full_text="[Page 1]\nPrevious evidence", summary="Previous summary",
    )
    content = make_pdf()
    response = client.post(f"/papers/{paper_id}/attach", data={
        "pdf": (BytesIO(content), "replacement.pdf"),
    }, follow_redirects=True)
    assert "PDF attached. This paper is ready" in response.get_data(as_text=True)
    row = get_row(web, paper_id)
    assert row["title"] == "Manually reviewed title"
    assert row["abstract"] == "Reviewed abstract"
    assert row["summary"] == ""
    assert "[Page 2]" in row["full_text"]
    assert row["pdf_path"] != str(old)
    assert Path(row["pdf_path"]).read_bytes() == content
    assert not old.exists()
    assert list(folder.glob("*.pdf")) == [Path(row["pdf_path"])]


@pytest.mark.parametrize("filename,content,message", [
    ("bad.txt", b"not a PDF", "Choose a PDF file to upload."),
    ("bad.pdf", b"corrupt file", "The PDF could not be opened or processed."),
])
def test_failed_attachment_retains_previous_data_and_file(client, web, add_paper, filename, content, message):
    folder = web.app.config["UPLOAD_FOLDER"]
    folder.mkdir()
    old = folder / "old.pdf"
    old.write_bytes(b"previous stored copy")
    paper_id = add_paper(pdf_path=str(old), full_text="[Page 1]\nOld evidence", summary="Old summary")
    before = dict(get_row(web, paper_id))
    response = client.post(f"/papers/{paper_id}/attach", data={"pdf": (BytesIO(content), filename)})
    assert response.status_code == 302
    assert response.headers["Location"].endswith(f"/papers/{paper_id}")
    assert message in client.get(response.headers["Location"]).get_data(as_text=True)
    assert dict(get_row(web, paper_id)) == before
    assert old.read_bytes() == b"previous stored copy"
    assert list(folder.glob("*.pdf")) == [old]


def test_reextract_refreshes_fields_text_and_summary(client, web, add_paper, make_pdf):
    folder = web.app.config["UPLOAD_FOLDER"]
    folder.mkdir()
    path = folder / "stored.pdf"
    content = make_pdf()
    path.write_bytes(content)
    paper_id = add_paper(
        title="Old extraction", authors="Old Author", year=2020, abstract="Old abstract",
        pdf_path=str(path), full_text="[Page 1]\nOld text", summary="Stale summary",
    )
    response = client.post(f"/papers/{paper_id}/reextract", follow_redirects=True)
    assert response.request.path == f"/papers/{paper_id}/edit"
    assert "Details re-extracted from the PDF" in response.get_data(as_text=True)
    row = get_row(web, paper_id)
    assert (row["title"], row["authors"], row["year"]) == (
        "Reliable Research Workflows", "Alice Example, Bob Researcher", 2023,
    )
    assert row["abstract"] == "We evaluate reliable research workflows using repeatable experiments."
    assert "[Page 2]" in row["full_text"]
    assert row["summary"] == ""
    assert row["pdf_path"] == str(path)
    assert path.read_bytes() == content


@pytest.mark.parametrize("file_state", ["missing", "corrupt"])
def test_failed_reextraction_preserves_reviewed_fields(client, web, add_paper, file_state):
    folder = web.app.config["UPLOAD_FOLDER"]
    folder.mkdir()
    path = folder / "stored.pdf"
    if file_state == "corrupt":
        path.write_bytes(b"corrupt PDF")
    paper_id = add_paper(pdf_path=str(path), summary="Previous summary")
    before = dict(get_row(web, paper_id))
    response = client.post(f"/papers/{paper_id}/reextract", follow_redirects=True)
    assert response.request.path == f"/papers/{paper_id}/edit"
    expected = "no longer available" if file_state == "missing" else "could not be opened or processed"
    assert expected in response.get_data(as_text=True)
    assert dict(get_row(web, paper_id)) == before


def test_uploading_same_pdf_twice_retains_one_copy(client, web, make_pdf):
    content = make_pdf()
    client.post("/upload", data={"pdf": (BytesIO(content), "first.pdf")})
    first = dict(get_row(web, 1))
    response = client.post("/upload", data={"pdf": (BytesIO(content), "renamed.pdf")}, follow_redirects=True)
    assert "already in your library" in response.get_data(as_text=True)
    assert dict(get_row(web, 1)) == first
    with closing(web.connect_db()) as db:
        assert db.execute("SELECT COUNT(*) FROM papers").fetchone()[0] == 1
    files = list(web.app.config["UPLOAD_FOLDER"].glob("*.pdf"))
    assert files == [Path(first["pdf_path"])]


def test_upload_attaches_to_matching_search_record(client, web, add_paper, make_pdf, paper_data):
    paper_id = add_paper(summary="Stale summary")
    response = client.post("/upload", data={"pdf": (BytesIO(make_pdf()), "paper.pdf")}, follow_redirects=True)
    assert response.request.path == f"/papers/{paper_id}/edit"
    assert "PDF added to the paper already in your library" in response.get_data(as_text=True)
    row = get_row(web, paper_id)
    assert row["external_id"] == paper_data["external_id"]
    assert row["paper_url"] == paper_data["paper_url"]
    assert "[Page 2]" in row["full_text"]
    assert row["summary"] == ""
    assert Path(row["pdf_path"]).is_file()
    with closing(web.connect_db()) as db:
        assert db.execute("SELECT COUNT(*) FROM papers").fetchone()[0] == 1


@pytest.mark.parametrize("full_text,pdf_url,import_visible,analysis_visible", [
    ("", "https://example.org/paper.pdf", True, False),
    ("", "", False, False),
    ("[Page 1]\nAvailable evidence", "https://example.org/paper.pdf", False, True),
])
def test_detail_actions_depend_on_available_full_text(client, add_paper, full_text, pdf_url, import_visible, analysis_visible):
    paper_id = add_paper(full_text=full_text, pdf_url=pdf_url)
    response = client.get(f"/papers/{paper_id}")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert (f'action="/papers/{paper_id}/import-pdf"' in html) == import_visible
    assert (f'action="/papers/{paper_id}/summarize"' in html) == analysis_visible
    assert (f'action="/papers/{paper_id}/ask"' in html) == analysis_visible
    assert (f'action="/papers/{paper_id}/attach"' in html) == (not analysis_visible)
