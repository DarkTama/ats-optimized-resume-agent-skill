"""
Tests for the Theme registry (see CONTEXT.md and docs/adr/0001-themes-style-only.md).

Every Theme must:
  - build a valid DOCX RenderConfig and RenderCV design
  - use ATS-safe fonts only in DOCX
  - render a DOCX with no text boxes, shapes, images, or multi-column sections
  - pass validation and keep its content readable by an ATS-style text extractor
"""

import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.export.rendercv import to_rendercv_dict
from src.ingest.extract import extract_text_from_file
from src.rendering.config import RenderConfig
from src.rendering.render_docx import ResumeRenderer
from src.rendering.themes import (
    ATS_SAFE_FONTS,
    DEFAULT_THEME,
    THEMES,
    UnknownThemeError,
    get_theme,
    list_theme_names,
)
from src.schemas.resume_schema import TailoredResume
from src.validation.validate_output import validate

SAMPLE_JSON = ROOT / "examples" / "sample_resume_json.json"
LOCAL_JSON = ROOT / "tests" / "local" / "personal_resume.json"

THEME_NAMES = ["modern-clean", "executive-serif", "minimalist-mono"]


def _load(path: Path) -> TailoredResume:
    return TailoredResume.from_dict(json.loads(path.read_text(encoding="utf-8")))


def _resume_sources():
    sources = [pytest.param(SAMPLE_JSON, id="sample")]
    if LOCAL_JSON.exists():
        sources.append(pytest.param(LOCAL_JSON, id="personal"))
    return sources


# ── Registry ─────────────────────────────────────────────────────────────────

def test_v1_themes_registered():
    assert list_theme_names() == THEME_NAMES


def test_default_theme_is_modern_clean():
    assert DEFAULT_THEME == "modern-clean"
    assert get_theme(None).name == "modern-clean"


def test_modern_clean_matches_legacy_docx_look():
    """Default Theme must reproduce today's navy + Calibri DOCX output."""
    legacy = RenderConfig()
    cfg = get_theme("modern-clean").docx
    assert cfg.font_name == legacy.font_name
    assert cfg.name_color == legacy.name_color
    assert cfg.section_border_color == legacy.section_border_color


def test_unknown_theme_lists_valid_names():
    with pytest.raises(UnknownThemeError) as exc:
        get_theme("foo")
    msg = str(exc.value)
    for name in THEME_NAMES:
        assert name in msg


def test_engineeringresumes_is_deprecated_alias():
    with pytest.warns(DeprecationWarning):
        theme = get_theme("engineeringresumes")
    assert theme.pdf_base == "engineeringresumes"


@pytest.mark.parametrize("name", THEME_NAMES)
def test_docx_fonts_are_ats_safe(name):
    cfg = THEMES[name].docx
    assert cfg.font_name in ATS_SAFE_FONTS
    assert cfg.font_name_heading in ATS_SAFE_FONTS


def test_themes_look_different():
    looks = {
        (t.docx.font_name, t.docx.name_color, t.docx.show_section_bottom_border)
        for t in THEMES.values()
    }
    assert len(looks) == len(THEMES)


# ── RenderCV export ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("name", THEME_NAMES)
def test_rendercv_dict_carries_theme_design(name):
    resume = _load(SAMPLE_JSON)
    data = to_rendercv_dict(resume, theme=name)
    design = data["design"]
    assert design["theme"] == THEMES[name].pdf_base
    for key, value in THEMES[name].pdf_design.items():
        assert design[key] == value


def test_rendercv_dict_defaults_to_default_theme():
    data = to_rendercv_dict(_load(SAMPLE_JSON))
    assert data["design"]["theme"] == THEMES[DEFAULT_THEME].pdf_base


# ── DOCX ATS gate (the ADR's enforcement) ────────────────────────────────────

FORBIDDEN_XML = ["<w:txbxContent", "<w:pict", "<w:drawing", "<mc:AlternateContent", "<wps:", "<v:shape"]


@pytest.mark.parametrize("source", _resume_sources())
@pytest.mark.parametrize("name", THEME_NAMES)
def test_docx_theme_passes_ats_gate(name, source, tmp_path):
    resume = _load(source)

    result = validate(resume)
    assert result.passed, result.report()

    out = tmp_path / f"{name}.docx"
    ResumeRenderer(config=get_theme(name).docx).render(resume, out)
    assert out.exists()

    with zipfile.ZipFile(out) as z:
        xml = z.read("word/document.xml").decode("utf-8")
        media = [n for n in z.namelist() if n.startswith("word/media/")]

    for tag in FORBIDDEN_XML:
        assert tag not in xml, f"{name}: forbidden structure {tag}"
    assert not media, f"{name}: embedded images {media}"
    for m in re.finditer(r'<w:cols[^>]*w:num="(\d+)"', xml):
        assert int(m.group(1)) <= 1, f"{name}: multi-column section"

    used = set(re.findall(r'w:ascii="([^"]+)"', xml))
    assert used <= ATS_SAFE_FONTS, f"{name}: non-ATS-safe fonts {used - ATS_SAFE_FONTS}"

    # Round trip: an ATS-style text extractor must still find the content.
    text = extract_text_from_file(out)
    assert resume.header.name in text
    assert resume.header.email in text
    for exp in resume.experience:
        assert exp.company in text

    # Keyword coverage from the resume's own skills must survive rendering.
    keywords = (resume.skills.core + resume.skills.tools)[:8]
    for kw in keywords:
        assert kw.lower() in text.lower(), f"{name}: lost keyword {kw}"

# ── PDF (real RenderCV run, skipped when rendercv is not installed) ──────────

@pytest.mark.skipif(shutil.which("rendercv") is None, reason="rendercv not installed")
@pytest.mark.parametrize("source", _resume_sources())
@pytest.mark.parametrize("name", THEME_NAMES)
def test_pdf_theme_renders_and_text_extracts(name, source, tmp_path):
    from src.export.rendercv import export_rendercv_yaml, render_pdf_with_rendercv

    resume = _load(source)
    resume.header.phone = "+14155552671"  # RenderCV rejects fake 555 numbers
    yaml_path = export_rendercv_yaml(resume, tmp_path / "resume.yaml", theme=name)
    pdf = render_pdf_with_rendercv(yaml_path, tmp_path / f"{name}.pdf")
    assert pdf.exists() and pdf.stat().st_size > 0

    text = extract_text_from_file(pdf)
    assert resume.header.name in text
    for exp in resume.experience:
        assert exp.company in text
