"""
Theme registry. See CONTEXT.md and docs/adr/0001-themes-style-only.md.

A Theme changes Styling only (typography, color, spacing, alignment, dividers).
It never changes Structure (columns, text boxes, shapes, graphics). One Theme
name gives a matching look in DOCX (RenderConfig) and PDF (RenderCV design).
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .config import RenderConfig

# Fonts common enough on recruiter machines that they will not be substituted.
ATS_SAFE_FONTS = frozenset({
    "Calibri", "Arial", "Georgia", "Times New Roman", "Cambria", "Verdana", "Tahoma",
})

DEFAULT_THEME = "modern-clean"

# Old name -> (current Theme name, RenderCV base theme to keep the old PDF look)
DEPRECATED_ALIASES = {
    "engineeringresumes": "minimalist-mono",
}


class UnknownThemeError(ValueError):
    pass


@dataclass(frozen=True)
class Theme:
    name: str
    description: str
    docx: RenderConfig
    pdf_base: str                                   # RenderCV built-in theme to start from
    pdf_design: Dict[str, Any] = field(default_factory=dict)  # RenderCV design overrides


def _rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return f"rgb({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)})"


def _pdf_colors(name: str, accent: str, text: str = "000000") -> Dict[str, str]:
    return {
        "text": _rgb(text),
        "name": _rgb(name),
        "connections": _rgb(accent),
        "section_titles": _rgb(accent),
        "links": _rgb(accent),
    }


THEMES: Dict[str, Theme] = {
    "modern-clean": Theme(
        name="modern-clean",
        description="Tech / startup. Sans-serif, navy accent, compact.",
        # Defaults of RenderConfig are the legacy navy + Calibri look.
        docx=RenderConfig(),
        pdf_base="classic",
        pdf_design={
            "colors": _pdf_colors("1F3864", "1F3864"),
            # RenderCV 2.3 fails unless all four margins are equal.
            "page": {"top_margin": "1.5cm", "bottom_margin": "1.5cm",
                     "left_margin": "1.5cm", "right_margin": "1.5cm"},
            "header": {"alignment": "left", "name_font_family": "Source Sans 3",
                       "connections_font_family": "Source Sans 3"},
            "section_titles": {"type": "with-full-line", "line_thickness": "0.75pt",
                               "font_family": "Source Sans 3"},
            "text": {"font_family": "Source Sans 3"},
        },
    ),
    "executive-serif": Theme(
        name="executive-serif",
        description="Finance / corporate / senior. Serif, charcoal, subtle dividers.",
        docx=RenderConfig(
            font_name="Georgia",
            font_name_heading="Georgia",
            name_color="262626",
            section_title_color="262626",
            section_border_color="7F7F7F",
            section_border_size=4,
            section_spacing_before=8,
        ),
        pdf_base="classic",
        pdf_design={
            "colors": _pdf_colors("262626", "262626"),
            "header": {"alignment": "center", "name_font_family": "XCharter",
                       "connections_font_family": "XCharter", "name_bold": False},
            "section_titles": {"type": "with-full-line", "line_thickness": "0.4pt",
                               "font_family": "XCharter", "small_caps": True},
            "text": {"font_family": "XCharter"},
        },
    ),
    "minimalist-mono": Theme(
        name="minimalist-mono",
        description="Quant / dev / research. Pure black, no divider lines.",
        docx=RenderConfig(
            font_name="Arial",
            font_name_heading="Arial",
            name_color="000000",
            section_title_color="000000",
            show_section_bottom_border=False,
            body_font_size=10,
            section_spacing_before=8,
        ),
        pdf_base="engineeringresumes",
        pdf_design={
            "colors": _pdf_colors("000000", "000000"),
            "section_titles": {"type": "without-line"},
        },
    ),
}


def list_theme_names() -> List[str]:
    return list(THEMES)


def get_theme(name: Optional[str]) -> Theme:
    """Look up a Theme. None means the default. Unknown names raise with the valid list."""
    if not name:
        return THEMES[DEFAULT_THEME]
    if name in THEMES:
        return THEMES[name]
    if name in DEPRECATED_ALIASES:
        warnings.warn(
            f"Theme '{name}' is deprecated; use '{DEPRECATED_ALIASES[name]}'.",
            DeprecationWarning,
            stacklevel=2,
        )
        # Keep the exact old PDF look: plain RenderCV engineeringresumes.
        return Theme(
            name=name,
            description="Deprecated alias.",
            docx=THEMES[DEPRECATED_ALIASES[name]].docx,
            pdf_base=name,
            pdf_design={},
        )
    raise UnknownThemeError(
        f"Unknown theme '{name}'. Valid themes: {', '.join(list_theme_names())}"
    )
