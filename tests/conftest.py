"""Isolated data and network boundaries for the HW2 test suite."""

import importlib
import sqlite3
from contextlib import closing
from unittest.mock import patch

import pymupdf
import pytest
import requests


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    def blocked(*args, **kwargs):
        raise AssertionError("Unexpected network request: supply a controlled service response")

    monkeypatch.setattr(requests.sessions.Session, "request", blocked)
    # Gemini uses httpx; block that transport as well as requests.
    import httpx
    monkeypatch.setattr(httpx.Client, "send", blocked)
    monkeypatch.setattr(httpx.AsyncClient, "send", blocked)


@pytest.fixture(scope="session")
def app_module(tmp_path_factory):
    # app.py calls init_db during import. Redirect that one connection before
    # importing, so even collection/setup cannot write to the user's database.
    bootstrap = tmp_path_factory.mktemp("bootstrap") / "papers.sqlite3"
    with closing(sqlite3.connect(bootstrap)) as connection:
        with patch("sqlite3.connect", return_value=connection):
            module = importlib.import_module("app")
    return module


@pytest.fixture
def web(app_module, tmp_path, monkeypatch):
    for name, value in {
        "TESTING": True,
        "SECRET_KEY": "test-session-secret",
        "DATABASE": tmp_path / "papers.sqlite3",
        "UPLOAD_FOLDER": tmp_path / "pdfs",
    }.items():
        monkeypatch.setitem(app_module.app.config, name, value)
    app_module.init_db()
    return app_module


@pytest.fixture
def client(web):
    return web.app.test_client()


@pytest.fixture
def paper_data():
    return {
        "external_id": "https://openalex.org/W123",
        "work_id": "W123",
        "title": "Reliable Research Workflows",
        "authors": "Alice Example, Bob Researcher",
        "year": 2023,
        "abstract": "A study of reliable research workflows.",
        "paper_url": "https://example.org/publication",
        "pdf_url": "https://example.org/paper.pdf",
    }


@pytest.fixture
def add_paper(web, paper_data):
    def insert(**changes):
        data = {k: v for k, v in paper_data.items() if k != "work_id"}
        data.update(changes)
        columns = ", ".join(data)
        placeholders = ", ".join("?" for _ in data)
        with closing(web.connect_db()) as db, db:
            return db.execute(
                f"INSERT INTO papers ({columns}) VALUES ({placeholders})", tuple(data.values())
            ).lastrowid
    return insert


@pytest.fixture
def make_pdf():
    def build(inline_abstract=False):
        abstract = "We evaluate reliable research workflows using repeatable experiments."
        with pymupdf.open() as document:
            page = document.new_page()
            page.insert_text((72, 90), "Reliable Research Workflows", fontsize=20)
            page.insert_text((72, 125), "Alice Example, Bob Researcher", fontsize=12)
            if inline_abstract:
                page.insert_text((72, 180), "Abstract " + abstract, fontsize=10)
            else:
                page.insert_text((72, 180), "Abstract", fontsize=12)
                page.insert_text((72, 205), abstract, fontsize=10)
            page.insert_text((72, 250), "1 Introduction", fontsize=12)
            page.insert_textbox(
                (72, 275, 520, 430),
                "The introduction describes the experimental design and separates it from the abstract. " * 4,
                fontsize=10,
            )
            page.insert_text((72, 760), "arXiv:2301.01234", fontsize=9)
            page = document.new_page()
            page.insert_textbox(
                (72, 90, 520, 400),
                "Evaluation results show repeatable outcomes across the tested workflows. " * 5,
                fontsize=10,
            )
            return document.tobytes()
    return build
