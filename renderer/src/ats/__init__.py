"""
ATS keyword scoring and gap analysis module.
"""

from .scorer import (
    ATSReport,
    extract_keywords_from_jd,
    score_ats,
)

__all__ = [
    "ATSReport",
    "extract_keywords_from_jd",
    "score_ats",
]
