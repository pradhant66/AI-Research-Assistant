"""Local-first AI Research Assistant web application."""

from __future__ import annotations

import sqlite3
import os
import re
import unicodedata
import uuid
from pathlib import Path
from urllib.parse import urlparse

import requests
from flask import Flask, abort, flash, redirect, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename

from gemini_service import AnalysisError, answer_question, summarize
from openalex import PaperSearchError, get_paper, get_pdf_urls, search_papers
from pdf_tools import PDFProcessingError, extract_pdf


BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET_KEY", "local-development-only-change-before-public-deployment"
)
app.config["DATABASE"] = BASE_DIR / "instance" / "papers.sqlite3"
app.config["UPLOAD_FOLDER"] = BASE_DIR / "instance" / "pdfs"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


def connect_db() -> sqlite3.Connection:
    app.config["DATABASE"].parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(app.config["DATABASE"])
    db.row_factory = sqlite3.Row
    return db


def init_db() -> None:
    with connect_db() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                external_id TEXT UNIQUE,
                title TEXT NOT NULL,
                authors TEXT NOT NULL,
                year INTEGER,
                abstract TEXT NOT NULL DEFAULT '',
                paper_url TEXT NOT NULL DEFAULT '',
                pdf_url TEXT NOT NULL DEFAULT '',
                pdf_path TEXT NOT NULL DEFAULT '',
                full_text TEXT NOT NULL DEFAULT '',
                summary TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


init_db()


def _paper_key(paper) -> tuple[str, int, str] | None:
    """Match the same paper across PDF uploads and search records."""
    if not paper["year"] or not paper["authors"] or paper["authors"] == "Authors unavailable":
        return None
    title = unicodedata.normalize("NFKD", paper["title"]).casefold()
    author = unicodedata.normalize("NFKD", paper["authors"].split(",", 1)[0]).casefold()
    title_words = re.findall(r"[a-z0-9]+", title)
    author_words = re.findall(r"[a-z0-9]+", author)
    if not title_words or not author_words:
        return None
    return (" ".join(title_words), int(paper["year"]), author_words[-1])


def _matching_paper(db: sqlite3.Connection, paper):
    key = _paper_key(paper)
    if key is None:
        return None
    return next(
        (row for row in db.execute("SELECT * FROM papers WHERE year = ?", (key[1],))
         if _paper_key(row) == key),
        None,
    )


@app.get("/")
def index():
    query = request.args.get("q", "").strip()
    papers = []
    if query:
        try:
            papers = search_papers(query)
        except PaperSearchError as exc:
            flash(str(exc), "error")

    with connect_db() as db:
        saved = db.execute("SELECT external_id, title, authors, year FROM papers").fetchall()
        saved_ids = {row["external_id"] for row in saved if row["external_id"]}
        saved_keys = {_paper_key(row) for row in saved} - {None}
        saved_ids.update(
            paper["external_id"] for paper in papers if _paper_key(paper) in saved_keys
        )
    return render_template("index.html", query=query, papers=papers, saved_ids=saved_ids)


@app.post("/save/<work_id>")
def save_paper(work_id: str):
    try:
        paper = get_paper(work_id)
    except PaperSearchError as exc:
        flash(str(exc), "error")
        return redirect(url_for("index", q=request.form.get("q", "")))

    with connect_db() as db:
        existing = db.execute(
            "SELECT id FROM papers WHERE external_id = ?", (paper["external_id"],)
        ).fetchone()
        if existing:
            flash("This paper is already in your library.", "info")
            return redirect(url_for("paper_detail", paper_id=existing["id"]))
        matching = _matching_paper(db, paper)
        if matching:
            if not matching["external_id"]:
                db.execute(
                    "UPDATE papers SET external_id = ?, paper_url = ?, pdf_url = ? WHERE id = ?",
                    (paper["external_id"], paper["paper_url"], paper["pdf_url"], matching["id"]),
                )
            flash("This paper is already in your library.", "info")
            return redirect(url_for("paper_detail", paper_id=matching["id"]))
        cursor = db.execute(
            """
            INSERT INTO papers (external_id, title, authors, year, abstract, paper_url, pdf_url)
            VALUES (:external_id, :title, :authors, :year, :abstract, :paper_url, :pdf_url)
            """,
            paper,
        )
        paper_id = cursor.lastrowid
    flash("Paper saved to your library.", "success")
    return redirect(url_for("paper_detail", paper_id=paper_id))


@app.get("/library")
def library():
    with connect_db() as db:
        papers = db.execute(
            "SELECT * FROM papers ORDER BY created_at DESC, id DESC"
        ).fetchall()
    return render_template("library.html", papers=papers)


@app.post("/papers/<int:paper_id>/remove")
def remove_paper(paper_id: int):
    with connect_db() as db:
        paper = db.execute("SELECT pdf_path FROM papers WHERE id = ?", (paper_id,)).fetchone()
        if paper is None:
            abort(404)
        db.execute("DELETE FROM papers WHERE id = ?", (paper_id,))
        pdf_in_use = bool(paper["pdf_path"] and db.execute(
            "SELECT 1 FROM papers WHERE pdf_path = ? LIMIT 1", (paper["pdf_path"],)
        ).fetchone())

    if paper["pdf_path"] and not pdf_in_use:
        path = Path(paper["pdf_path"]).resolve()
        if path.is_relative_to(app.config["UPLOAD_FOLDER"].resolve()):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                flash("Paper removed, but its stored PDF could not be deleted.", "error")
                return redirect(url_for("library"))
    flash("Paper removed from your library.", "success")
    return redirect(url_for("library"))


@app.get("/papers/<int:paper_id>")
def paper_detail(paper_id: int):
    with connect_db() as db:
        paper = db.execute("SELECT * FROM papers WHERE id = ?", (paper_id,)).fetchone()
    if paper is None:
        abort(404)
    return render_template("paper.html", paper=paper)


@app.get("/papers/<int:paper_id>/pdf")
def view_pdf(paper_id: int):
    with connect_db() as db:
        paper = db.execute("SELECT pdf_path FROM papers WHERE id = ?", (paper_id,)).fetchone()
    if paper is None or not paper["pdf_path"]:
        abort(404)
    path = Path(paper["pdf_path"]).resolve()
    upload_folder = app.config["UPLOAD_FOLDER"].resolve()
    if not path.is_relative_to(upload_folder) or not path.is_file():
        abort(404)
    return send_file(path, mimetype="application/pdf", as_attachment=False)


def _save_pdf(file_storage) -> tuple[Path, dict]:
    filename = secure_filename(file_storage.filename or "")
    if not filename.lower().endswith(".pdf"):
        raise PDFProcessingError("Choose a PDF file to upload.")
    folder = app.config["UPLOAD_FOLDER"]
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{uuid.uuid4().hex}.pdf"
    file_storage.save(path)
    try:
        result = extract_pdf(path)
    except PDFProcessingError:
        path.unlink(missing_ok=True)
        raise
    return path, result


@app.route("/upload", methods=["GET", "POST"])
def upload_paper():
    if request.method == "GET":
        return render_template("upload.html")
    try:
        path, data = _save_pdf(request.files.get("pdf"))
    except (PDFProcessingError, AttributeError) as exc:
        flash(str(exc) if isinstance(exc, PDFProcessingError) else "Choose a PDF file.", "error")
        return redirect(url_for("upload_paper"))
    with connect_db() as db:
        matching = _matching_paper(db, data)
        if matching:
            if matching["pdf_path"] and Path(matching["pdf_path"]).is_file():
                path.unlink(missing_ok=True)
                flash("This paper is already in your library.", "info")
                return redirect(url_for("paper_detail", paper_id=matching["id"]))
            db.execute(
                "UPDATE papers SET pdf_path = ?, full_text = ?, summary = '' WHERE id = ?",
                (str(path), data["full_text"], matching["id"]),
            )
            flash("PDF added to the paper already in your library.", "success")
            return redirect(url_for("edit_paper", paper_id=matching["id"]))
        cursor = db.execute(
            """
            INSERT INTO papers (title, authors, year, abstract, pdf_path, full_text)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (data["title"], data["authors"], data["year"], data["abstract"],
             str(path), data["full_text"]),
        )
        paper_id = cursor.lastrowid
    flash("PDF uploaded. Review the extracted paper details below.", "success")
    return redirect(url_for("edit_paper", paper_id=paper_id))


@app.route("/papers/<int:paper_id>/edit", methods=["GET", "POST"])
def edit_paper(paper_id: int):
    with connect_db() as db:
        paper = db.execute("SELECT * FROM papers WHERE id = ?", (paper_id,)).fetchone()
        if paper is None:
            abort(404)
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            authors = request.form.get("authors", "").strip()
            year_text = request.form.get("year", "").strip()
            abstract = request.form.get("abstract", "").strip()
            if not title or not authors or (year_text and not year_text.isdigit()):
                flash("Enter a title and authors, and use a numeric year if known.", "error")
                return redirect(url_for("edit_paper", paper_id=paper_id))
            db.execute(
                "UPDATE papers SET title = ?, authors = ?, year = ?, abstract = ? WHERE id = ?",
                (title, authors, int(year_text) if year_text else None, abstract, paper_id),
            )
            flash("Paper details updated.", "success")
            return redirect(url_for("paper_detail", paper_id=paper_id))
    return render_template("edit.html", paper=paper)


@app.post("/papers/<int:paper_id>/reextract")
def reextract_paper(paper_id: int):
    with connect_db() as db:
        paper = db.execute("SELECT pdf_path FROM papers WHERE id = ?", (paper_id,)).fetchone()
    if paper is None:
        abort(404)
    if not paper["pdf_path"] or not Path(paper["pdf_path"]).is_file():
        flash("The uploaded PDF is no longer available. Upload it again.", "error")
        return redirect(url_for("edit_paper", paper_id=paper_id))
    try:
        data = extract_pdf(Path(paper["pdf_path"]))
    except PDFProcessingError as exc:
        flash(str(exc), "error")
        return redirect(url_for("edit_paper", paper_id=paper_id))
    with connect_db() as db:
        db.execute(
            """UPDATE papers
               SET title = ?, authors = ?, year = ?, abstract = ?, full_text = ?, summary = ''
               WHERE id = ?""",
            (data["title"], data["authors"], data["year"], data["abstract"],
             data["full_text"], paper_id),
        )
    flash("Details re-extracted from the PDF. Review them before saving.", "success")
    return redirect(url_for("edit_paper", paper_id=paper_id))


@app.post("/papers/<int:paper_id>/attach")
def attach_pdf(paper_id: int):
    with connect_db() as db:
        paper = db.execute("SELECT id FROM papers WHERE id = ?", (paper_id,)).fetchone()
    if paper is None:
        abort(404)
    try:
        path, data = _save_pdf(request.files.get("pdf"))
    except (PDFProcessingError, AttributeError) as exc:
        flash(str(exc) if isinstance(exc, PDFProcessingError) else "Choose a PDF file.", "error")
        return redirect(url_for("paper_detail", paper_id=paper_id))
    with connect_db() as db:
        old = db.execute("SELECT pdf_path FROM papers WHERE id = ?", (paper_id,)).fetchone()
        db.execute(
            "UPDATE papers SET pdf_path = ?, full_text = ?, summary = '' WHERE id = ?",
            (str(path), data["full_text"], paper_id),
        )
    if old["pdf_path"]:
        Path(old["pdf_path"]).unlink(missing_ok=True)
    flash("PDF attached. This paper is ready for summary and questions.", "success")
    return redirect(url_for("paper_detail", paper_id=paper_id))


@app.post("/papers/<int:paper_id>/import-pdf")
def import_pdf(paper_id: int):
    with connect_db() as db:
        paper = db.execute("SELECT * FROM papers WHERE id = ?", (paper_id,)).fetchone()
    if paper is None:
        abort(404)
    pdf_url = paper["pdf_url"] or ""
    if urlparse(pdf_url).scheme != "https":
        flash("No direct open-access PDF is available. Upload one instead.", "error")
        return redirect(url_for("paper_detail", paper_id=paper_id))
    urls = [pdf_url]
    if paper["external_id"]:
        work_id = paper["external_id"].rsplit("/", 1)[-1]
        try:
            urls.extend(url for url in get_pdf_urls(work_id) if url not in urls)
        except PaperSearchError:
            pass  # The saved URL may still work if OpenAlex is temporarily unavailable.
    folder = app.config["UPLOAD_FOLDER"]
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{uuid.uuid4().hex}.pdf"
    for url in urls:
        path.unlink(missing_ok=True)
        try:
            with requests.get(url, stream=True, timeout=20, headers={"User-Agent": "Mozilla/5.0 (compatible; AIResearchAssistant/0.1)"}) as response:
                response.raise_for_status()
                size = 0
                with path.open("wb") as output:
                    for chunk in response.iter_content(chunk_size=65536):
                        size += len(chunk)
                        if size > app.config["MAX_CONTENT_LENGTH"]:
                            raise PDFProcessingError("The linked PDF is too large.")
                        output.write(chunk)
            data = extract_pdf(path)
            break
        except (requests.RequestException, PDFProcessingError):
            continue
    else:
        path.unlink(missing_ok=True)
        flash("Available PDF links could not be imported. Upload a PDF copy instead.", "error")
        return redirect(url_for("paper_detail", paper_id=paper_id))
    with connect_db() as db:
        db.execute(
            "UPDATE papers SET pdf_url = ?, pdf_path = ?, full_text = ?, abstract = ?, summary = '' WHERE id = ?",
            (url, str(path), data["full_text"], data["abstract"] or paper["abstract"], paper_id),
        )
    flash("An open-access PDF copy was imported and processed. Review the abstract and edit it if needed.", "success")
    return redirect(url_for("paper_detail", paper_id=paper_id))


@app.post("/papers/<int:paper_id>/summarize")
def summarize_paper(paper_id: int):
    with connect_db() as db:
        paper = db.execute("SELECT * FROM papers WHERE id = ?", (paper_id,)).fetchone()
    if paper is None:
        abort(404)
    try:
        summary = summarize(paper["title"], paper["full_text"])
    except AnalysisError as exc:
        flash(str(exc), "error")
        return redirect(url_for("paper_detail", paper_id=paper_id))
    with connect_db() as db:
        db.execute("UPDATE papers SET summary = ? WHERE id = ?", (summary, paper_id))
    flash("Summary generated from the paper text.", "success")
    return redirect(url_for("paper_detail", paper_id=paper_id))


@app.post("/papers/<int:paper_id>/ask")
def ask_paper(paper_id: int):
    with connect_db() as db:
        paper = db.execute("SELECT * FROM papers WHERE id = ?", (paper_id,)).fetchone()
    if paper is None:
        abort(404)
    question = request.form.get("question", "").strip()[:500]
    if not question:
        flash("Enter a question about the paper.", "error")
        return redirect(url_for("paper_detail", paper_id=paper_id))
    try:
        answer = answer_question(paper["title"], paper["full_text"], question)
    except AnalysisError as exc:
        flash(str(exc), "error")
        return redirect(url_for("paper_detail", paper_id=paper_id))
    return render_template("paper.html", paper=paper, question=question, answer=answer)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5050")), debug=True)
