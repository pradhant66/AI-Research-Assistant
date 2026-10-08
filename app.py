"""Local-first AI Research Assistant web application."""

from __future__ import annotations

import sqlite3
import os
import uuid
from pathlib import Path
from urllib.parse import urlparse

import requests
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from gemini_service import AnalysisError, answer_question, summarize
from openalex import PaperSearchError, get_paper, search_papers
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
        saved_ids = {
            row["external_id"]
            for row in db.execute("SELECT external_id FROM papers WHERE external_id IS NOT NULL")
        }
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


@app.get("/papers/<int:paper_id>")
def paper_detail(paper_id: int):
    with connect_db() as db:
        paper = db.execute("SELECT * FROM papers WHERE id = ?", (paper_id,)).fetchone()
    if paper is None:
        abort(404)
    return render_template("paper.html", paper=paper)


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
    folder = app.config["UPLOAD_FOLDER"]
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{uuid.uuid4().hex}.pdf"
    try:
        with requests.get(pdf_url, stream=True, timeout=20) as response:
            response.raise_for_status()
            size = 0
            with path.open("wb") as output:
                for chunk in response.iter_content(chunk_size=65536):
                    size += len(chunk)
                    if size > app.config["MAX_CONTENT_LENGTH"]:
                        raise PDFProcessingError("The linked PDF is too large. Upload a smaller copy.")
                    output.write(chunk)
        data = extract_pdf(path)
    except (requests.RequestException, PDFProcessingError) as exc:
        path.unlink(missing_ok=True)
        flash(str(exc) if isinstance(exc, PDFProcessingError) else "Could not download that PDF. Upload it instead.", "error")
        return redirect(url_for("paper_detail", paper_id=paper_id))
    with connect_db() as db:
        db.execute(
            "UPDATE papers SET pdf_path = ?, full_text = ?, summary = '' WHERE id = ?",
            (str(path), data["full_text"], paper_id),
        )
    flash("Open-access PDF imported and processed.", "success")
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
