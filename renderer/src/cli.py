"""
CLI entry point — installed as the `resume-skill` command via pip.

Usage (after `pip install .`):
    resume-skill render   --input resume.json --output resume.docx [--jd job_description.md]
    resume-skill validate --input resume.json [--jd job_description.md]
    resume-skill extract  --input master_resume.pdf [--output master.txt]
    resume-skill ats      --resume resume.json --jd job_description.md [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .ats.scorer import score_ats
from .ingest.extract import extract_text_from_file
from .rendering.config import RenderConfig
from .rendering.render_docx import ResumeRenderer
from .schemas.resume_schema import TailoredResume
from .utils.utils import load_json
from .validation.validate_output import validate
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def _render_cmd(args):
    raw = load_json(args.input)
    resume = TailoredResume.from_dict(raw)

    if not args.skip_validation:
        result = validate(resume, jd=args.jd)
        print(result.report())
        if not result.passed:
            print("\nValidation failed. Fix errors before rendering.", file=sys.stderr)
            sys.exit(1)
    out_path = Path(args.output)
    if out_path.suffix.lower() == ".pdf":
        import tempfile
        from .export.rendercv import export_rendercv_yaml, render_pdf_with_rendercv

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_yaml = Path(tmp_dir) / "resume.yaml"
            export_rendercv_yaml(resume, tmp_yaml, theme=args.theme or "engineeringresumes")
            pdf_path = render_pdf_with_rendercv(tmp_yaml, out_path)
            print(f"PDF saved: {pdf_path}")
    else:
        renderer = ResumeRenderer(config=RenderConfig())
        out = renderer.render(resume, args.output)
        print(f"DOCX saved: {out}")


def _export_cmd(args):
    raw = load_json(args.input)
    resume = TailoredResume.from_dict(raw)
    from .export.rendercv import export_rendercv_yaml

    out = export_rendercv_yaml(resume, args.output, theme=args.theme or "engineeringresumes")
    print(f"RenderCV YAML exported: {out}")

def _validate_cmd(args):
    raw = load_json(args.input)
    resume = TailoredResume.from_dict(raw)
    result = validate(resume, jd=args.jd)
    print(result.report())
    sys.exit(0 if result.passed else 1)


def _extract_cmd(args):
    try:
        text = extract_text_from_file(args.input)
    except Exception as e:
        print(f"Error extracting text from {args.input}: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(text, encoding="utf-8")
        print(f"Extracted master resume text saved to: {out_p}")
    else:
        print(text)


def _ats_cmd(args):
    raw = load_json(args.resume)
    resume = TailoredResume.from_dict(raw)

    target_source = None
    if args.keywords:
        target_source = [k.strip() for k in args.keywords.split(",") if k.strip()]
    elif args.jd:
        target_source = args.jd
    else:
        print("Error: Either --jd or --keywords must be provided for ATS scoring.", file=sys.stderr)
        sys.exit(1)

    report = score_ats(resume, target_source)
    if args.json_output:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.format_report())


def main():
    parser = argparse.ArgumentParser(
        prog="resume-skill",
        description="Resume skill CLI - render, validate, extract, and score tailored resumes",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── render ────────────────────────────────────────────────────────────
    # ── render ────────────────────────────────────────────────────────────
    render_p = sub.add_parser("render", help="Render resume JSON → .docx or .pdf")
    render_p.add_argument("--input", "-i", required=True, help="Path to resume JSON")
    render_p.add_argument("--output", "-o", required=True, help="Output .docx or .pdf path")
    render_p.add_argument("--theme", help="Theme for PDF rendering (default: engineeringresumes)")
    render_p.add_argument("--jd", help="Path or text of Job Description for optional ATS scoring check")
    render_p.add_argument("--skip-validation", action="store_true")
    render_p.set_defaults(func=_render_cmd)
    # ── validate ──────────────────────────────────────────────────────────
    val_p = sub.add_parser("validate", help="Validate resume JSON only")
    val_p.add_argument("--input", "-i", required=True, help="Path to resume JSON")
    val_p.add_argument("--jd", help="Path or text of Job Description for ATS keyword match validation")
    val_p.set_defaults(func=_validate_cmd)

    # ── extract ───────────────────────────────────────────────────────────
    ext_p = sub.add_parser("extract", help="Extract text from master resume file (.pdf, .docx, .txt, .md)")
    ext_p.add_argument("--input", "-i", required=True, help="Path to master resume file")
    ext_p.add_argument("--output", "-o", help="Optional output text path (prints to stdout if omitted)")
    ext_p.set_defaults(func=_extract_cmd)

    # ── ats ───────────────────────────────────────────────────────────────
    ats_p = sub.add_parser("ats", help="Score resume keyword coverage against Job Description")
    ats_p.add_argument("--resume", "-r", required=True, help="Path to tailored resume JSON")
    ats_p.add_argument("--jd", "-j", help="Path to Job Description file or raw JD string")
    ats_p.add_argument("--keywords", "-k", help="Comma-separated target keywords list")
    ats_p.add_argument("--json", dest="json_output", action="store_true", help="Output results in JSON format")
    ats_p.set_defaults(func=_ats_cmd)

    # ── export ────────────────────────────────────────────────────────────
    exp_p = sub.add_parser("export", help="Export tailored resume JSON to RenderCV YAML")
    exp_p.add_argument("--input", "-i", required=True, help="Path to tailored resume JSON")
    exp_p.add_argument("--output", "-o", required=True, help="Output .yaml path")
    exp_p.add_argument("--theme", default="engineeringresumes", help="RenderCV theme (default: engineeringresumes)")
    exp_p.set_defaults(func=_export_cmd)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
