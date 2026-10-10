# ats-optimized-resume-agent-skill

**English** | [中文文档](README_CN.md) | [Full Installation Guide](docs/INSTALL.md)

AI agent skill for **PI-Desktop**, **Claude Code**, and AI coding assistants. Transforms a master resume and target job description into an ATS-optimized, professionally styled Word document (`.docx`) and publication-grade PDF (`.pdf`).

---

## ⚡ Quick Install

Paste into your terminal or agent:

**Windows (PowerShell):**
```powershell
git clone https://github.com/DarkTama/ats-optimized-resume-agent-skill.git $env:TEMP\build-tailored-resume; & "$env:TEMP\build-tailored-resume\install.ps1" -Scope user
```

**macOS / Linux:**
```bash
git clone https://github.com/DarkTama/ats-optimized-resume-agent-skill.git /tmp/build-tailored-resume && chmod +x /tmp/build-tailored-resume/install.sh && /tmp/build-tailored-resume/install.sh --user
```

Once installed, invoke inside your agent:
- **PI-Desktop**: Say *"tailor my resume"* or *"edit my resume"*
- **Claude Code**: Run `/build-tailored-resume`

*Need project-level scope, manual pip setup, or offline install? See [docs/INSTALL.md](docs/INSTALL.md).*

---

## Key Capabilities

- **Two Operating Modes**:
  - **Mode A (Full Tailoring)**: Master resume + target JD → role-aligned, humanized resume.
  - **Mode B (Targeted Edit)**: Surgical updates to bullets, skills, or 1-page fit without re-running full intake.
- **Multi-Format Ingestion**: Extracts text from `.pdf`, `.docx`, `.md`, and `.txt` master resumes via `resume-skill extract`.
- **Deterministic ATS Scoring**: Computes exact keyword match %, identifies section coverage, and flags missing JD terms with zero AI hallucination (`resume-skill ats`).
- **ATS-Safe Visual Themes**: Themes change styling only (typography, color accents, dividers, margins) — never document structure — ensuring 100% compliance with ATS parsers.
- **Dual Output Rendering**: Generates pixel-accurate Word documents (`.docx`) and publication-quality Typst PDFs (`.pdf`).

---

## Themes

All themes are strictly ATS-compliant (single-column, no text boxes, ATS-safe system fonts).

| Theme | Best For | Typography | Accent | Divider |
|---|---|---|---|---|
| `modern-clean` *(default)* | Tech, startups, product | Calibri / Source Sans 3 | Deep Navy (`#1F3864`) | 0.75pt solid line |
| `executive-serif` | Finance, legal, corporate, senior | Georgia / XCharter | Charcoal (`#262626`) | 0.4pt subtle line, centered header |
| `minimalist-mono` | Quant, dev, systems, research | Arial / Roboto | Monochrome Black (`#000000`) | Clean whitespace (no line) |

---

## CLI Reference

The bundled `resume-skill` CLI handles validation, scoring, extraction, and rendering:

```bash
# Render to DOCX or PDF with theme
resume-skill render --input tailored_resume.json --output resume.docx --theme modern-clean
resume-skill render --input tailored_resume.json --output resume.pdf --theme modern-clean

# Score keyword coverage against Job Description
resume-skill ats --resume tailored_resume.json --jd job_description.md

# Extract clean text from existing master resume (.pdf, .docx, .txt, .md)
resume-skill extract --input master_resume.pdf --output master.txt

# Validate resume JSON schema and check for banned AI buzzwords
resume-skill validate --input tailored_resume.json

# Export to RenderCV YAML for standalone customization
resume-skill export --input tailored_resume.json --output resume.yaml --theme modern-clean
```

---

## Workflow Protocol

The skill enforces a gated, anti-hallucination workflow:

| Stage | Action | Quality Gate |
|---|---|---|
| **1. Intake** | Read master resume + target JD | Name, contact, experience verified |
| **2. JD Analysis** | Extract critical skills, KPIs, seniority level | Priority keyword target identified |
| **3. Strategy** | Align narrative and project prioritization | Strategy confirmed |
| **4. Tailoring** | Draft bullets with concrete impact formula | Humanization pass complete (no AI buzzwords) |
| **5. ATS Check** | Run deterministic keyword match | ≥60% match rate or critical terms present |
| **6. Render** | Choose theme; render `.docx` and `.pdf` | Schema validation PASS, output file written |
| **7. Final Check** | Confirm 1-page fit, active links, honesty check | Final delivery |

*Full protocol details are specified in [SKILL.md](SKILL.md).*

---

## Architecture & Design Decisions

- [CONTEXT.md](CONTEXT.md): Ubiquitous domain language and definitions.
- [docs/adr/0001-themes-style-only.md](docs/adr/0001-themes-style-only.md): Architecture Decision Record enforcing style-only theme invariance.

---

## License

MIT
