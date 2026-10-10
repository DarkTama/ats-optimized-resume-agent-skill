"""
Ingest module for reading resume and job description sources.
"""

from .extract import extract_text_from_file

__all__ = ["extract_text_from_file"]
