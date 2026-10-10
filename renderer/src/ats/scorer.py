"""
Deterministic ATS keyword matcher and scoring engine.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set, Union

from ..schemas.resume_schema import TailoredResume


# Pre-curated high-signal technical & industry keyword patterns
COMMON_TECH_PATTERNS = [
    r"\b[A-Z][a-zA-Z0-9_\+\#\.\-]{1,20}\b",  # Capitalized tech terms
    r"\b[A-Z]{2,6}\b",                      # Acronyms: SQL, AWS, GCP, API, ETL, KPI
    r"\b[a-zA-Z0-9_\+\#\.\-]+/[a-zA-Z0-9_\+\#\.\-]+\b", # e.g. CI/CD, A/B
]

STOPWORDS = {
    "and", "or", "the", "a", "an", "in", "on", "at", "to", "for", "with", "by",
    "from", "of", "about", "into", "through", "during", "before", "after", "above",
    "below", "between", "under", "again", "further", "then", "once", "here", "there",
    "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
    "too", "very", "s", "t", "can", "will", "just", "don", "should", "now", "our",
    "we", "you", "your", "they", "them", "their", "what", "which", "who", "whom",
    "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "having", "do", "does", "did", "doing", "would",
    "could", "years", "experience", "role", "team", "work", "working", "looking",
    "candidate", "opportunity", "company", "requirements", "qualifications", "responsibilities"
}

COMMON_TECH_ACRONYMS = {
    "AI", "ML", "BI", "QA", "CI", "CD", "DB", "UI", "UX", "SQL", "ETL", "KPI",
    "API", "AWS", "GCP", "SDK", "REST", "SOAP", "LLM", "NLP", "CSS", "HTML",
    "JVM", "CRM", "ERP", "SaaS", "PaaS", "IaaS", "TCP", "HTTP", "HTTPS", "DNS"
}

@dataclass
class ATSReport:
    total_target: int = 0
    matched_count: int = 0
    match_rate: float = 0.0
    matched_keywords: Dict[str, int] = field(default_factory=dict)
    missing_keywords: List[str] = field(default_factory=list)
    section_breakdown: Dict[str, List[str]] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_target": self.total_target,
            "matched_count": self.matched_count,
            "match_rate": round(self.match_rate, 2),
            "matched_keywords": self.matched_keywords,
            "missing_keywords": self.missing_keywords,
            "section_breakdown": self.section_breakdown,
            "warnings": self.warnings,
        }

    def format_report(self) -> str:
        lines = []
        lines.append("==================================================")
        lines.append(f"ATS Keyword Match: {self.match_rate:.1f}% ({self.matched_count}/{self.total_target} keywords)")
        lines.append("==================================================")

        lines.append(f"\nMatched ({self.matched_count}/{self.total_target}):")
        if self.matched_keywords:
            for kw, count in sorted(self.matched_keywords.items(), key=lambda x: -x[1]):
                lines.append(f"  [+] {kw} (x{count})")
        else:
            lines.append("  (None)")

        lines.append(f"\nMissing ({len(self.missing_keywords)}/{self.total_target}):")
        if self.missing_keywords:
            for kw in sorted(self.missing_keywords):
                lines.append(f"  [-] {kw}")
        else:
            lines.append("  All target keywords present!")

        if self.section_breakdown:
            lines.append("\nKeyword Distribution by Section:")
            for sec, kws in sorted(self.section_breakdown.items()):
                lines.append(f"  [{sec}]: {', '.join(sorted(set(kws)))}")

        if self.warnings:
            lines.append("\nWarnings:")
            for w in self.warnings:
                lines.append(f"  [!] {w}")
        return "\n".join(lines)


def extract_keywords_from_jd(jd_text_or_path: Union[str, Path]) -> List[str]:
    """
    Extract key technical and domain keywords from a Job Description.
    """
    text = str(jd_text_or_path)
    p = Path(text)
    if p.exists() and p.is_file():
        text = p.read_text(encoding="utf-8", errors="ignore")

    found_keywords: Set[str] = set()

    # Look for known stack/technology list items in JD
    # Match colon lists like: "Stack: Airflow, Redshift, Presto" or "SQL: Redshift, Presto"
    colon_matches = re.findall(r"(?:Stack|Tools|Technologies|Skills|Languages|Frameworks|Databases):\s*([^\n\r]+)", text, re.IGNORECASE)
    for match in colon_matches:
        for item in re.split(r"[,;/]+", match):
            clean = item.strip()
            words_in_item = clean.lower().split()
            if 2 <= len(clean) <= 25 and not any(w in STOPWORDS for w in words_in_item):
                found_keywords.add(clean)

    # Multi-word phrase regexes for common methodologies
    common_phrases = [
        "A/B Testing", "A/B Experiments", "Cohort Analysis", "Funnel Analysis",
        "Experiment Design", "Data Modeling", "Data Pipelines", "CI/CD",
        "Business Intelligence", "Machine Learning", "System Design"
    ]
    for phrase in common_phrases:
        if re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text, re.IGNORECASE):
            found_keywords.add(phrase)

    # Match well-known tech tokens
    # Examples: SQL, Python, dbt, Airflow, Redshift, Presto, Statsig, Segment, Docker, AWS, etc.
    word_tokens = re.findall(r"\b[A-Za-z0-9_\+\#\.\-]{2,20}\b", text)
    for word in word_tokens:
        lower = word.lower()
        if lower in STOPWORDS:
            continue
        if word in COMMON_TECH_ACRONYMS:
            found_keywords.add(word)
        elif word.isupper() and 3 <= len(word) <= 6 and not word.isdigit():
            found_keywords.add(word)
        elif (word[0].isupper() and any(c.isupper() for c in word[1:]) and any(c.islower() for c in word)) or word in {
            "dbt", "Kubernetes", "Docker", "PostgreSQL", "MySQL", "MongoDB", "Redis",
            "Kafka", "Spark", "Hadoop", "Airflow", "Tableau", "Looker", "Redshift",
            "Presto", "Statsig", "Segment", "Amplitude", "Snowflake", "BigQuery",
            "FastAPI", "React", "TypeScript", "Node.js", "GraphQL", "Python", "SQL"
        }:
            found_keywords.add(word)

    cleaned = []
    seen_lower = set()
    for kw in sorted(found_keywords, key=lambda x: (-len(x), x)):
        if kw.lower() not in seen_lower:
            seen_lower.add(kw.lower())
            cleaned.append(kw)
    return sorted(cleaned, key=lambda x: x.lower())


def _gather_resume_sections(resume: Union[TailoredResume, Dict[str, Any]]) -> Dict[str, str]:
    """Gather text contents mapped to section names."""
    if isinstance(resume, dict):
        resume_obj = TailoredResume.from_dict(resume)
    else:
        resume_obj = resume

    sections: Dict[str, str] = {}

    if resume_obj.summary:
        sections["summary"] = resume_obj.summary

    skills_text = []
    sk = resume_obj.skills
    skills_text.extend(sk.core)
    skills_text.extend(sk.tools)
    skills_text.extend(sk.methods)
    skills_text.extend(sk.domains)
    if skills_text:
        sections["skills"] = " ".join(skills_text)

    exp_text = []
    for e in resume_obj.experience:
        exp_text.append(f"{e.title} {e.company} {e.location}")
        exp_text.extend(e.bullets)
    if exp_text:
        sections["experience"] = " ".join(exp_text)

    proj_text = []
    for p in resume_obj.projects:
        proj_text.append(f"{p.name} {p.subtitle}")
        proj_text.extend(p.bullets)
    if proj_text:
        sections["projects"] = " ".join(proj_text)

    edu_text = []
    for ed in resume_obj.education:
        edu_text.append(f"{ed.school} {ed.degree} {ed.location}")
        edu_text.extend(ed.details)
    if edu_text:
        sections["education"] = " ".join(edu_text)

    if resume_obj.certifications:
        sections["certifications"] = " ".join(resume_obj.certifications)
    if resume_obj.awards:
        sections["awards"] = " ".join(resume_obj.awards)

    return sections


def score_ats(
    resume: Union[TailoredResume, Dict[str, Any]],
    target_keywords_or_jd: Union[str, Path, List[str]],
) -> ATSReport:
    """
    Score resume against target keywords or job description text.
    """
    if isinstance(target_keywords_or_jd, list):
        target_keywords = target_keywords_or_jd
    else:
        target_keywords = extract_keywords_from_jd(target_keywords_or_jd)

    sections = _gather_resume_sections(resume)
    all_text = " ".join(sections.values())
    total_words = max(len(re.findall(r"\b\w+\b", all_text)), 1)

    matched_keywords: Dict[str, int] = {}
    missing_keywords: List[str] = []
    section_breakdown: Dict[str, List[str]] = {}
    warnings: List[str] = []

    for kw in target_keywords:
        kw_clean = kw.strip()
        if not kw_clean:
            continue

        # Regex with word boundaries
        pattern = r"(?<![\w])" + re.escape(kw_clean) + r"(?![\w])"
        rx = re.compile(pattern, re.IGNORECASE)

        # Count in full text
        occurrences = len(rx.findall(all_text))
        if occurrences > 0:
            matched_keywords[kw_clean] = occurrences

            # Track section appearances
            for sec_name, sec_content in sections.items():
                if rx.search(sec_content):
                    if sec_name not in section_breakdown:
                        section_breakdown[sec_name] = []
                    section_breakdown[sec_name].append(kw_clean)

            # Check for keyword stuffing
            # Flag if keyword occurs > 5 times and makes up > 2.5% of total words
            kw_density = (occurrences / total_words) * 100
            if occurrences >= 5 and kw_density > 2.5:
                warnings.append(
                    f"Possible keyword stuffing: {kw_clean!r} appears {occurrences} times ({kw_density:.1f}% density)"
                )
        else:
            missing_keywords.append(kw_clean)

    total_target = len(target_keywords)
    matched_count = len(matched_keywords)
    match_rate = (matched_count / total_target * 100) if total_target > 0 else 100.0

    return ATSReport(
        total_target=total_target,
        matched_count=matched_count,
        match_rate=match_rate,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        section_breakdown=section_breakdown,
        warnings=warnings,
    )
