"""
Tests for resume-skill CLI commands (extract, ats, validate, render).
"""

import json
from pathlib import Path
import pytest
from src import cli


def test_cli_extract_text(tmp_path: Path, capsys):
    sample = tmp_path / "resume.txt"
    sample.write_text("Master Resume: John Doe\n5 years Python", encoding="utf-8")

    class Args:
        input = str(sample)
        output = None

    cli._extract_cmd(Args())
    captured = capsys.readouterr()
    assert "Master Resume: John Doe" in captured.out


def test_cli_extract_output_file(tmp_path: Path):
    sample = tmp_path / "resume.txt"
    sample.write_text("Master Resume: John Doe", encoding="utf-8")
    out_file = tmp_path / "out.txt"

    class Args:
        input = str(sample)
        output = str(out_file)

    cli._extract_cmd(Args())
    assert out_file.exists()
    assert "Master Resume: John Doe" in out_file.read_text(encoding="utf-8")


def test_cli_ats_scoring(capsys):
    example_json = Path(__file__).parent.parent / "examples" / "sample_resume_json.json"
    example_jd = Path(__file__).parent.parent / "examples" / "sample_jd.md"

    class Args:
        resume = str(example_json)
        jd = str(example_jd)
        keywords = None
        json_output = False

    cli._ats_cmd(Args())
    captured = capsys.readouterr()
    assert "ATS Keyword Match:" in captured.out
    assert "SQL" in captured.out


def test_cli_ats_json_output(capsys):
    example_json = Path(__file__).parent.parent / "examples" / "sample_resume_json.json"

    class Args:
        resume = str(example_json)
        jd = None
        keywords = "SQL, Python, Docker"
        json_output = True

    cli._ats_cmd(Args())
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "match_rate" in data
    assert "matched_keywords" in data


def test_cli_export_yaml(tmp_path: Path):
    example_json = Path(__file__).parent.parent / "examples" / "sample_resume_json.json"
    out_yaml = tmp_path / "resume.yaml"

    class Args:
        input = str(example_json)
        output = str(out_yaml)
        theme = "engineeringresumes"

    cli._export_cmd(Args())
    assert out_yaml.exists()
    assert "engineeringresumes" in out_yaml.read_text(encoding="utf-8")
