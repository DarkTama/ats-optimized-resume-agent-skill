"""
RenderCV format converter and PDF export engine.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from ..schemas.resume_schema import TailoredResume


def _extract_username_from_url(url: str, platform: str) -> str:
    """Extract username handle from a profile URL."""
    if not url:
        return ""
    clean = url.rstrip("/")
    if platform.lower() in clean.lower():
        parts = clean.split("/")
        return parts[-1] if parts else clean
    return clean


def to_rendercv_dict(resume: TailoredResume, theme: str = "engineeringresumes") -> Dict[str, Any]:
    """
    Convert a TailoredResume instance to a RenderCV YAML-compatible dictionary.
    """
    cv: Dict[str, Any] = {
        "name": resume.header.name,
    }

    if resume.header.location:
        cv["location"] = resume.header.location
    if resume.header.email:
        cv["email"] = resume.header.email
    if resume.header.phone:
        cv["phone"] = resume.header.phone
    if resume.header.website:
        cv["website"] = resume.header.website

    social_networks = []
    if resume.header.github:
        username = _extract_username_from_url(resume.header.github, "github")
        if username:
            social_networks.append({"network": "GitHub", "username": username})
    if resume.header.linkedin:
        username = _extract_username_from_url(resume.header.linkedin, "linkedin")
        if username:
            social_networks.append({"network": "LinkedIn", "username": username})

    if social_networks:
        cv["social_networks"] = social_networks

    sections: Dict[str, Any] = {}

    # Summary
    if resume.summary:
        sections["summary"] = [resume.summary]

    # Skills
    skills_entries = []
    sk = resume.skills
    if sk.core:
        skills_entries.append({"label": "Core", "details": ", ".join(sk.core)})
    if sk.tools:
        skills_entries.append({"label": "Tools", "details": ", ".join(sk.tools)})
    if sk.methods:
        skills_entries.append({"label": "Methods", "details": ", ".join(sk.methods)})
    if sk.domains:
        skills_entries.append({"label": "Domains", "details": ", ".join(sk.domains)})
    if skills_entries:
        sections["skills"] = skills_entries

    # Experience
    if resume.experience:
        exp_entries = []
        for e in resume.experience:
            entry: Dict[str, Any] = {
                "company": e.company,
                "position": e.title,
            }
            if e.location:
                entry["location"] = e.location
            if e.dates:
                entry["date"] = e.dates
            if e.bullets:
                entry["highlights"] = list(e.bullets)
            exp_entries.append(entry)
        sections["experience"] = exp_entries

    # Projects
    if resume.projects:
        proj_entries = []
        for p in resume.projects:
            entry = {
                "name": p.name,
            }
            if p.subtitle:
                entry["summary"] = p.subtitle
            if p.dates:
                entry["date"] = p.dates
            if p.bullets:
                entry["highlights"] = list(p.bullets)
            if p.url:
                entry["url"] = p.url
            proj_entries.append(entry)
        sections["projects"] = proj_entries

    # Education
    if resume.education:
        edu_entries = []
        for ed in resume.education:
            # RenderCV requires both 'institution' and 'area'
            degree = ed.degree or "Degree"
            area = "General"
            if " in " in degree:
                parts = degree.split(" in ", 1)
                degree = parts[0].strip()
                area = parts[1].strip()
            elif degree:
                area = degree

            entry = {
                "institution": ed.school,
                "area": area,
                "degree": degree,
            }
            if ed.location:
                entry["location"] = ed.location
            if ed.dates:
                entry["date"] = ed.dates
            if ed.details:
                entry["highlights"] = list(ed.details)
            edu_entries.append(entry)
        sections["education"] = edu_entries

    # Certifications
    if resume.certifications:
        sections["certifications"] = list(resume.certifications)

    # Awards
    if resume.awards:
        sections["awards"] = list(resume.awards)

    cv["sections"] = sections

    return {
        "cv": cv,
        "design": {
            "theme": theme,
        },
        "locale": {
            "last_updated_date_template": "",
        },
    }


def export_rendercv_yaml(
    resume: TailoredResume,
    output_path: Union[str, Path],
    theme: str = "engineeringresumes",
) -> Path:
    """Export a TailoredResume to a RenderCV YAML file."""
    data = to_rendercv_dict(resume, theme=theme)
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)
    return out_p


def render_pdf_with_rendercv(
    yaml_path: Union[str, Path],
    output_pdf_path: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Render a RenderCV YAML file to PDF using the rendercv CLI.
    """
    y_path = Path(yaml_path)
    if not y_path.exists():
        raise FileNotFoundError(f"YAML file not found: {y_path}")

    # Run rendercv render
    cmd = ["rendercv", "render", str(y_path.resolve())]
    proc = subprocess.run(cmd, cwd=str(y_path.parent), capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"RenderCV execution failed:\n{proc.stderr}\n{proc.stdout}")

    # Locate generated PDF in rendercv_output
    out_dir = y_path.parent / "rendercv_output"
    generated_pdfs = list(out_dir.glob("*.pdf"))
    if not generated_pdfs:
        raise FileNotFoundError("RenderCV finished but no PDF was found in rendercv_output")

    gen_pdf = generated_pdfs[0]
    if output_pdf_path:
        dest_p = Path(output_pdf_path)
        dest_p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(gen_pdf, dest_p)
        return dest_p
    return gen_pdf
