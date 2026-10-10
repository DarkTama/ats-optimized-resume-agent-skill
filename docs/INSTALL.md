# Installation & Setup Guide

[← Back to README](../README.md)

---

## Installation

Choose one of the five methods below. All of them let you pick between **global** (available in all your projects) or **project-based** (current project only).

---

### Method 0 — Agent-Assisted (fastest)

Copy one of the prompts below and paste it directly into your coding agent (Claude Code, Cursor, Windsurf, etc.). Your agent will detect your OS and run the install automatically.

#### For PI-Desktop

**Global install (all projects):**
```
Please install the build-tailored-resume skill for PI-Desktop globally. Clone the repo at https://github.com/SankaiAI/ats-optimized-resume-agent-skill.git into a temporary directory, then run the install script: install.ps1 -Runtime pi -Scope user on Windows, or ./install.sh --runtime=pi --user on Mac/Linux. After install, confirm it works with resume-skill --help.
```

**Project-level install (current project only):**
```
Please install the build-tailored-resume skill for this project in PI-Desktop. Clone the repo at https://github.com/SankaiAI/ats-optimized-resume-agent-skill.git into a temporary directory, then run: install.ps1 -Runtime pi -Scope project on Windows, or ./install.sh --runtime=pi --project on Mac/Linux. After install, confirm with resume-skill --help.
```

#### For Claude Code

**Global install (all projects):**
```
Please install the build-tailored-resume Claude Code skill for me globally. Clone the repo at https://github.com/SankaiAI/ats-optimized-resume-agent-skill.git into a temporary directory, then run the install script: install.ps1 -Runtime claude -Scope user on Windows, or ./install.sh --runtime=claude --user on Mac/Linux. After install, confirm with resume-skill --help.
```

**Project-level install (current project only):**
```
Please install the build-tailored-resume Claude Code skill for this project only. Clone the repo at https://github.com/SankaiAI/ats-optimized-resume-agent-skill.git into a temporary directory, then run: install.ps1 -Runtime claude -Scope project on Windows, or ./install.sh --runtime=claude --project on Mac/Linux. After install, confirm with resume-skill --help.
```

---

### Method 1 — Direct Clone

Clone the repository directly into your agent's skills directory, then install the Python CLI.

#### For PI-Desktop (`~/.agents/skills`)

**Global — all projects:**

Mac / Linux:
```bash
git clone https://github.com/SankaiAI/ats-optimized-resume-agent-skill.git ~/.agents/skills/build-tailored-resume
pip install ~/.agents/skills/build-tailored-resume/renderer
```

Windows (PowerShell):
```powershell
git clone https://github.com/SankaiAI/ats-optimized-resume-agent-skill.git "$HOME\.agents\skills\build-tailored-resume"
pip install "$HOME\.agents\skills\build-tailored-resume\renderer"
```

#### For Claude Code (`~/.claude/skills`)

**Global — all projects:**

Mac / Linux:
```bash
git clone https://github.com/SankaiAI/ats-optimized-resume-agent-skill.git ~/.claude/skills/build-tailored-resume
pip install ~/.claude/skills/build-tailored-resume/renderer
```

Windows (PowerShell):
```powershell
git clone https://github.com/SankaiAI/ats-optimized-resume-agent-skill.git "$HOME\.claude\skills\build-tailored-resume"
pip install "$HOME\.claude\skills\build-tailored-resume\renderer"
```

---

### Method 2 — Install Script (recommended for most users)

**Step 1 — Download**

```bash
git clone https://github.com/SankaiAI/ats-optimized-resume-agent-skill.git
cd ats-optimized-resume-agent-skill
```

**Step 2 — Run the script**

Mac / Linux:
```bash
chmod +x install.sh
./install.sh
```

Windows (PowerShell):
```powershell
.\install.ps1
```

Both scripts ask you to choose a scope:

```
[1] User    — available in ALL your projects (recommended)
[2] Project — current project only, shared with your team via git
[3] Local   — current project only, NOT committed to git
```

You can also skip the prompt by passing the scope directly:

```bash
./install.sh --user       # Mac/Linux
./install.sh --project
./install.sh --local

.\install.ps1 -Scope user      # Windows
.\install.ps1 -Scope project
.\install.ps1 -Scope local
```

Then invoke it:
```
/build-tailored-resume
```

---

### Method 3 — Manual Install

**Step 1 — Download**

```bash
git clone https://github.com/SankaiAI/ats-optimized-resume-agent-skill.git
cd ats-optimized-resume-agent-skill
```

**Step 2 — Install the Python CLI**

```bash
pip install renderer/
```

**Step 3 — Copy SKILL.md to the right location**

**Global — available in all your projects:**

```bash
# Mac/Linux
mkdir -p ~/.claude/skills/build-tailored-resume
cp SKILL.md ~/.claude/skills/build-tailored-resume/SKILL.md
```

```powershell
# Windows (PowerShell)
New-Item -ItemType Directory -Force "$HOME\.claude\skills\build-tailored-resume"
Copy-Item SKILL.md "$HOME\.claude\skills\build-tailored-resume\SKILL.md"
```

**Project-based — current project only:**

```bash
# Mac/Linux
mkdir -p .claude/skills/build-tailored-resume
cp /path/to/resume-skill/SKILL.md .claude/skills/build-tailored-resume/SKILL.md
```

```powershell
# Windows (PowerShell)
New-Item -ItemType Directory -Force ".claude\skills\build-tailored-resume"
Copy-Item C:\path\to\resume-skill\SKILL.md ".claude\skills\build-tailored-resume\SKILL.md"
```

To share with your team, commit the file:
```bash
git add .claude/skills/build-tailored-resume/SKILL.md
git commit -m "Add build-tailored-resume skill"
```

To keep it local only, add it to `.gitignore`:
```bash
echo ".claude/skills/" >> .gitignore
```

Then invoke it:
```
/build-tailored-resume
```

---

### Method 4 — Plugin Marketplace

Open Claude Code and run:

```
/plugin install resume-skill
```

Choose your scope when prompted, or pass it directly:

```bash
/plugin install resume-skill              # global — all your projects
/plugin install resume-skill --project    # current project only, committed to git
/plugin install resume-skill --local      # current project only, not committed
```

Then invoke it:
```
/resume-skill:build-tailored-resume
```

---

## Update

### Agent-Assisted Update (fastest)

Copy one of the prompts below and paste it into your coding agent. It will pull the latest changes and reinstall everything automatically.

**Global install:**

```
Please update my build-tailored-resume Claude Code skill to the latest version. Clone the latest repo from https://github.com/SankaiAI/ats-optimized-resume-agent-skill.git into a temporary directory, then run the install script with the user/global flag — install.sh --user on Mac/Linux, or install.ps1 -Scope user on Windows. After update, confirm with resume-skill --help.
```

**Project-level install:**

```
Please update my build-tailored-resume Claude Code skill to the latest version. Clone the latest repo from https://github.com/SankaiAI/ats-optimized-resume-agent-skill.git into a temporary directory, then run the install script with the project flag — install.sh --project on Mac/Linux, or install.ps1 -Scope project on Windows. After update, confirm with resume-skill --help.
```

---

### Manual Update

**If you installed via Method 1 (Direct Clone):**

Pull the latest changes and reinstall the Python CLI:

```bash
# Mac/Linux
cd ~/.claude/skills/build-tailored-resume   # global
# or: cd .claude/skills/build-tailored-resume  # project-level
git pull
pip install renderer/ --upgrade
```

```powershell
# Windows (PowerShell)
cd "$HOME\.claude\skills\build-tailored-resume"   # global
# or: cd ".claude\skills\build-tailored-resume"   # project-level
git pull
pip install renderer\ --upgrade
```

**If you installed via Method 2 (Install Script):**

Re-clone and re-run the script — it overwrites `SKILL.md` and upgrades the Python CLI in one step:

```bash
# Mac/Linux
git clone https://github.com/SankaiAI/ats-optimized-resume-agent-skill.git /tmp/build-tailored-resume
chmod +x /tmp/build-tailored-resume/install.sh
/tmp/build-tailored-resume/install.sh --user      # or --project
```

```powershell
# Windows (PowerShell)
git clone https://github.com/SankaiAI/ats-optimized-resume-agent-skill.git $env:TEMP\build-tailored-resume
& "$env:TEMP\build-tailored-resume\install.ps1" -Scope user   # or -Scope project
```

**If you installed via Method 3 (Manual):**

Re-clone, reinstall the Python CLI, and copy the updated `SKILL.md`:

```bash
# Mac/Linux
git clone https://github.com/SankaiAI/ats-optimized-resume-agent-skill.git /tmp/build-tailored-resume
pip install /tmp/build-tailored-resume/renderer --upgrade
cp /tmp/build-tailored-resume/SKILL.md ~/.claude/skills/build-tailored-resume/SKILL.md   # global
# or: cp /tmp/build-tailored-resume/SKILL.md .claude/skills/build-tailored-resume/SKILL.md  # project
```

```powershell
# Windows (PowerShell)
git clone https://github.com/SankaiAI/ats-optimized-resume-agent-skill.git $env:TEMP\build-tailored-resume
pip install "$env:TEMP\build-tailored-resume\renderer" --upgrade
Copy-Item "$env:TEMP\build-tailored-resume\SKILL.md" "$HOME\.claude\skills\build-tailored-resume\SKILL.md"   # global
# or: Copy-Item "$env:TEMP\build-tailored-resume\SKILL.md" ".claude\skills\build-tailored-resume\SKILL.md"   # project
```

---

## Verify the install

Open a new Claude Code session, type `/`, and confirm **`/build-tailored-resume`** appears in the list.

From the terminal:
```bash
resume-skill --help
```

---

## Uninstall

**Mac / Linux:**
```bash
rm -rf ~/.claude/skills/build-tailored-resume    # global scope
rm -rf .claude/skills/build-tailored-resume       # project scope
pip uninstall resume-skill
```

**Windows (PowerShell):**
```powershell
Remove-Item -Recurse -Force "$HOME\.claude\skills\build-tailored-resume"   # global
Remove-Item -Recurse -Force ".claude\skills\build-tailored-resume"          # project
pip uninstall resume-skill
```

---
