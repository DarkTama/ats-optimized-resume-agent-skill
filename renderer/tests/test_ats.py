"""
Tests for deterministic ATS keyword matching and scoring.
"""

from src.ats.scorer import (
    extract_keywords_from_jd,
    score_ats,
    ATSReport,
)
from src.schemas.resume_schema import (
    HeaderData,
    ResumeMetadata,
    SkillsData,
    ExperienceEntry,
    TailoredResume,
)


def _sample_resume() -> TailoredResume:
    return TailoredResume(
        candidate_level="senior_ic",
        target_role="Senior Data Analyst",
        target_company="Stripe",
        section_order=["header", "summary", "skills", "experience", "education"],
        header=HeaderData(
            name="Alex Chen",
            email="alex@example.com",
            phone="(555) 123-4567",
        ),
        summary="Data analyst with 5 years building SQL pipelines, product analytics, and experimentation.",
        skills=SkillsData(
            core=["SQL", "Python", "Tableau", "dbt", "A/B Testing"],
            tools=["BigQuery", "Snowflake", "Looker", "Airflow", "Statsig"],
            methods=["Cohort Analysis", "Funnel Analysis", "Experiment Design"],
            domains=["Product Analytics", "Payments", "Fintech"],
        ),
        experience=[
            ExperienceEntry(
                title="Senior Data Analyst",
                company="Brex",
                dates="2022 – Present",
                bullets=[
                    "Built SQL + dbt pipelines tracking spend adoption across 2,400 SMB customers.",
                    "Designed A/B test framework in Statsig for card onboarding flow.",
                    "Automated 6 weekly finance reports via Airflow + BigQuery.",
                ],
            )
        ],
        projects=[],
        education=[],
        metadata=ResumeMetadata(humanization_pass_complete=True),
    )


def test_keyword_extraction_from_jd():
    sample_jd = """
    ## Who You Are
    - Expert-level SQL; experience with dbt preferred
    - Strong Python skills for data analysis
    - Experience designing and analyzing A/B experiments
    - Experience with BI tools: Looker, Tableau
    - Stack: Airflow, Redshift, Presto, Statsig, Segment
    """
    keywords = extract_keywords_from_jd(sample_jd)
    assert "SQL" in keywords
    assert "Python" in keywords
    assert "dbt" in keywords
    assert "Looker" in keywords
    assert "Airflow" in keywords
    assert "Presto" in keywords


def test_score_ats_matches():
    resume = _sample_resume()
    target_keywords = ["SQL", "Python", "dbt", "Tableau", "Airflow", "Presto", "Kubernetes"]
    report = score_ats(resume, target_keywords)

    assert isinstance(report, ATSReport)
    assert report.total_target == 7
    # SQL, Python, dbt, Tableau, Airflow matched; Presto, Kubernetes missing
    assert report.matched_count == 5
    assert "SQL" in report.matched_keywords
    assert "Presto" in report.missing_keywords
    assert "Kubernetes" in report.missing_keywords
    assert round(report.match_rate, 1) == 71.4


def test_score_ats_stuffing_warning():
    resume = _sample_resume()
    # Add repeated occurrences of SQL
    resume.experience[0].bullets.extend([
        "SQL SQL SQL database query tuning.",
        "More SQL scripts and SQL transformations.",
        "Deep SQL queries for SQL reports.",
    ])
    report = score_ats(resume, ["SQL", "Python"])
    assert any("SQL" in warn for warn in report.warnings)


def test_ats_report_formatting():
    resume = _sample_resume()
    report = score_ats(resume, ["SQL", "Python", "Docker"])
    text_report = report.format_report()
    assert "ATS Keyword Match:" in text_report
    assert "Matched (2/3):" in text_report
    assert "Missing (1/3):" in text_report
    assert "Docker" in text_report
