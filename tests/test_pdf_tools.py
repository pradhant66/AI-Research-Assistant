"""Exercise actual generated PDF files and check known expected content."""

import pymupdf
import pytest

from pdf_tools import PDFProcessingError, extract_pdf


def test_extracts_metadata_and_all_pages(tmp_path, make_pdf):
    path = tmp_path / "input.pdf"
    path.write_bytes(make_pdf())
    paper = extract_pdf(path)
    assert paper["title"] == "Reliable Research Workflows"
    assert paper["authors"] == "Alice Example, Bob Researcher"
    assert paper["year"] == 2023
    assert paper["abstract"] == "We evaluate reliable research workflows using repeatable experiments."
    assert paper["page_count"] == 2
    assert "[Page 1]" in paper["full_text"] and "[Page 2]" in paper["full_text"]
    assert "Evaluation results show repeatable outcomes" in paper["full_text"]


def test_extracts_abstract_when_heading_and_body_share_a_line(tmp_path, make_pdf):
    # A common layout variation should not discard the abstract's first sentence.
    path = tmp_path / "inline.pdf"
    path.write_bytes(make_pdf(inline_abstract=True))
    paper = extract_pdf(path)
    assert paper["abstract"] == "We evaluate reliable research workflows using repeatable experiments."


def test_corrupt_pdf_is_rejected(tmp_path):
    path = tmp_path / "corrupt.pdf"
    path.write_bytes(b"This is not a PDF")
    with pytest.raises(PDFProcessingError, match="could not be opened or processed"):
        extract_pdf(path)


def test_pdf_without_selectable_text_is_rejected(tmp_path):
    path = tmp_path / "blank.pdf"
    with pymupdf.open() as document:
        document.new_page()
        document.save(path)
    with pytest.raises(PDFProcessingError, match="little or no selectable text"):
        extract_pdf(path)


def test_missing_metadata_uses_filename_and_creation_year(tmp_path):
    path = tmp_path / "fallback-title.pdf"
    with pymupdf.open() as document:
        page = document.new_page()
        page.insert_text((72, 100), "Abstract", fontsize=12)
        page.insert_textbox((72, 130, 500, 400), "Repeatable experiments provide useful evidence. " * 6, fontsize=10)
        document.set_metadata({"creationDate": "D:20210102000000"})
        document.save(path)
    paper = extract_pdf(path)
    assert paper["title"] == "fallback-title"
    assert paper["authors"] == "Authors unavailable"
    assert paper["year"] == 2021
    assert paper["abstract"].startswith("Repeatable experiments")


@pytest.mark.parametrize("ending", ["1\nIntroduction", "Keywords: testing", "* Contribution footnote"])
def test_abstract_stops_before_nonabstract_sections(ending):
    from pdf_tools import _find_abstract
    text = "Abstract\nWe study trans-\nformations with end-\nto-end methods.\n" + ending + "\nUnrelated body text."
    assert _find_abstract(text) == "We study transformations with end-to-end methods."


def test_unknown_year_remains_unknown():
    from pdf_tools import _find_year
    assert _find_year("A paper without a date", {}) is None
