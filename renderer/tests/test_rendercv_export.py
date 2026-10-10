"""
Tests for converting TailoredResume to RenderCV YAML format.
"""

from pathlib import Path
import pytest
from src.export.rendercv import to_rendercv_dict, render_pdf_with_rendercv
from src.schemas.resume_schema import (
    HeaderData,
    ResumeMetadata,
    SkillsData,
    ExperienceEntry,
    ProjectEntry,
    EducationEntry,
    TailoredResume,
)


def _sample_resume() -> TailoredResume:
    return TailoredResume(
        candidate_level="mid_level",
        target_role="Backend Engineer",
        target_company="Fintech",
        section_order=["header", "summary", "skills", "experience", "projects", "education"],
        header=HeaderData(
            name="Ekatama Ilham Prayoga",
            email="ekatama@example.com",
            phone="+62 851-5648-9171",
            location="Bandung, Indonesia",
            github="https://github.com/DarkTama",
        ),
        summary="Backend engineer with 3.5+ years experience.",
        skills=SkillsData(
            core=["Java", "Spring Boot", "SQL"],
            tools=["Docker", "Git"],
        ),
        experience=[
            ExperienceEntry(
                title="Backend Engineer",
                company="PT Digital Amore",
                location="Bandung, Indonesia",
                dates="Oct 2022 – Present",
                bullets=["Built loan calculation engine."],
            )
        ],
        projects=[
            ProjectEntry(
                name="openterm",
                subtitle="C#, Rust",
                dates="2024",
                bullets=["Built terminal emulator."],
                url="https://github.com/rzkfyn/openterm",
            )
        ],
        education=[
            EducationEntry(
                school="SMKN 1 Katapang",
                degree="Software Engineering",
                location="Bandung",
                dates="2016 – 2019",
            )
        ],
        metadata=ResumeMetadata(),
    )


def test_project_url_becomes_markdown_link_in_name():
    """RenderCV's entry templates ignore a 'url' field, so the link must live in the name."""
    rcv = to_rendercv_dict(_sample_resume())
    entry = rcv["cv"]["sections"]["projects"][0]
    assert entry["name"] == "[openterm](https://github.com/rzkfyn/openterm)"
    assert "url" not in entry


def test_project_without_url_keeps_plain_name():
    resume = _sample_resume()
    resume.projects[0].url = ""
    entry = to_rendercv_dict(resume)["cv"]["sections"]["projects"][0]
    assert entry["name"] == "openterm"
    assert "url" not in entry


def test_to_rendercv_dict():
    resume = _sample_resume()
    rcv = to_rendercv_dict(resume, theme="engineeringresumes")

    assert "cv" in rcv
    assert rcv["cv"]["name"] == "Ekatama Ilham Prayoga"
    assert rcv["cv"]["email"] == "ekatama@example.com"
    assert rcv["design"]["theme"] == "engineeringresumes"

    sections = rcv["cv"]["sections"]
    assert "summary" in sections
    assert "experience" in sections
    assert sections["experience"][0]["company"] == "PT Digital Amore"
    assert sections["experience"][0]["highlights"] == ["Built loan calculation engine."]
    assert "projects" in sections
    assert sections["projects"][0]["name"] == "[openterm](https://github.com/rzkfyn/openterm)"
    assert "skills" in sections
    assert any(s["label"] == "Core" for s in sections["skills"])
