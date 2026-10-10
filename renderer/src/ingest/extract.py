"""
Extract plain text from master resumes in various formats (.pdf, .docx, .txt, .md).
"""

from __future__ import annotations

from pathlib import Path
from typing import Union


def extract_text_from_docx(path: Union[str, Path]) -> str:
    """Extract all text paragraphs and table rows from a .docx file."""
    import docx

    doc = docx.Document(str(path))
    chunks: list[str] = []

    for child in doc.element.body:
        if child.tag.endswith("p"):
            para = docx.text.paragraph.Paragraph(child, doc)
            t = para.text.strip()
            if t:
                chunks.append(t)
        elif child.tag.endswith("tbl"):
            table = docx.table.Table(child, doc)
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    deduped = []
                    for c in row_cells:
                        if not deduped or c != deduped[-1]:
                            deduped.append(c)
                    chunks.append(" | ".join(deduped))
    return "\n\n".join(chunks)


def extract_text_from_pdf(path: Union[str, Path]) -> str:
    """Extract all text content from a .pdf file using pypdf."""
    import pypdf

    reader = pypdf.PdfReader(str(path))
    pages_text: list[str] = []

    for page in reader.pages:
        page_str = page.extract_text()
        if page_str:
            pages_text.append(page_str.strip())

    return "\n\n".join(pages_text)


def extract_text_from_text(path: Union[str, Path]) -> str:
    """Extract plain text from .txt or .md file with UTF-8 fallback."""
    p = Path(path)
    try:
        return p.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError:
        return p.read_text(encoding="latin-1").strip()


def extract_text_from_file(path: Union[str, Path]) -> str:
    """
    Extract text content from any supported resume file format:
    .pdf, .docx, .txt, .md
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")

    ext = p.suffix.lower()
    if ext == ".docx":
        return extract_text_from_docx(p)
    elif ext == ".pdf":
        return extract_text_from_pdf(p)
    elif ext in {".txt", ".md", ".markdown"}:
        return extract_text_from_text(p)
    else:
        raise ValueError(
            f"Unsupported file format '{ext}'. Supported formats: .pdf, .docx, .md, .txt"
        )
