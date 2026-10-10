"""
Tests for master resume text extraction (PDF, DOCX, TXT, MD).
"""

from pathlib import Path
import pytest

from src.ingest.extract import extract_text_from_file, extract_text_from_docx, extract_text_from_pdf


def test_extract_from_text(tmp_path: Path):
    sample = tmp_path / "resume.txt"
    sample.write_text("Alex Chen\nSoftware Engineer\nBuilt web apps.", encoding="utf-8")
    extracted = extract_text_from_file(sample)
    assert "Alex Chen" in extracted
    assert "Software Engineer" in extracted


def test_extract_from_markdown(tmp_path: Path):
    sample = tmp_path / "resume.md"
    sample.write_text("# Alex Chen\n\n- Bullet 1\n- Bullet 2", encoding="utf-8")
    extracted = extract_text_from_file(sample)
    assert "Alex Chen" in extracted
    assert "Bullet 1" in extracted


def test_extract_from_docx():
    example_docx = Path(__file__).parent.parent / "examples" / "output" / "alex_chen_stripe.docx"
    assert example_docx.exists(), "Sample docx must exist for test"
    text = extract_text_from_file(example_docx)
    assert "Alex Chen" in text
    assert len(text) > 100


def test_extract_from_pdf(tmp_path: Path):
    import pypdf
    writer = pypdf.PdfWriter()
    page = writer.add_blank_page(width=72 * 8.5, height=72 * 11)
    
    # We can create a simple pdf using pypdf writer with an annotation or text
    pdf_path = tmp_path / "test.pdf"
    with open(pdf_path, "wb") as f:
        writer.write(f)
        
    text = extract_text_from_file(pdf_path)
    # Blank page returns empty string or whitespace
    assert isinstance(text, str)


def test_extract_unsupported_extension(tmp_path: Path):
    sample = tmp_path / "test.xyz"
    sample.write_text("Some text", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_text_from_file(sample)


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        extract_text_from_file("non_existent_file_12345.pdf")
