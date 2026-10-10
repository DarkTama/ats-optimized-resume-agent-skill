# install.ps1 — installs the build-tailored-resume skill for PI-Desktop & Claude Code (Windows)
#
# Usage:
#   .\install.ps1                                    # interactive prompt
#   .\install.ps1 -Runtime pi -Scope user            # PI-Desktop (global, available in all projects)
#   .\install.ps1 -Runtime pi -Scope project         # PI-Desktop (current project)
#   .\install.ps1 -Runtime claude -Scope user        # Claude Code (global)
#   .\install.ps1 -Runtime both -Scope user          # Both runtimes

param(
    [ValidateSet("user", "project", "local", "")]
    [string]$Scope = "",
    [ValidateSet("pi", "claude", "both", "")]
    [string]$Runtime = "",
    [string]$ProjectPath = ""
)

$SkillName = "build-tailored-resume"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "============================================================"
Write-Host "  build-tailored-resume - AI Agent Skill Installer"
Write-Host "============================================================"

# ── Interactive Runtime selection when not specified ──────────────────────
if ($Runtime -eq "") {
    Write-Host ""
    Write-Host "  Which AI assistant/runtime do you want to install for?"
    Write-Host ""
    Write-Host "  [1] PI-Desktop / Agent Skills (~/.agents/skills)"
    Write-Host "  [2] Claude Code               (~/.claude/skills)"
    Write-Host "  [3] Both                      (recommended)"
    Write-Host ""

    do {
        $RChoice = Read-Host "  Enter 1, 2, or 3"
    } while ($RChoice -notin @("1", "2", "3"))

    $Runtime = @{ "1" = "pi"; "2" = "claude"; "3" = "both" }[$RChoice]
}

# ── Interactive Scope selection when not specified ────────────────────────
if ($Scope -eq "") {
    Write-Host ""
    Write-Host "  Where do you want to install this skill?"
    Write-Host ""
    Write-Host "  [1] User    - available in ALL your projects (recommended)"
    Write-Host "  [2] Project - current project only"
    Write-Host "  [3] Local   - current project only (not committed)"
    Write-Host ""

    do {
        $SChoice = Read-Host "  Enter 1, 2, or 3"
    } while ($SChoice -notin @("1", "2", "3"))

    $Scope = @{ "1" = "user"; "2" = "project"; "3" = "local" }[$SChoice]
}

Write-Host ""
Write-Host "  Runtime: $Runtime"
Write-Host "  Scope:   $Scope"
Write-Host ""

# ── Determine Project Root if needed ──────────────────────────────────────
$ProjectRoot = ""
if ($Scope -ne "user") {
    if ($ProjectPath -ne "") {
        $ProjectRoot = $ProjectPath
    } else {
        $ProjectRoot = (Get-Location).Path
        while ($true) {
            if ((Test-Path (Join-Path $ProjectRoot ".git")) -or `
                (Test-Path (Join-Path $ProjectRoot ".agents")) -or `
                (Test-Path (Join-Path $ProjectRoot ".claude"))) {
                break
            }
            $Parent = Split-Path $ProjectRoot -Parent
            if ($Parent -eq $ProjectRoot) { break }
            $ProjectRoot = $Parent
        }
    }
}

# ── Collect Target Directories ────────────────────────────────────────────
$TargetDirs = @()

if ($Runtime -in @("pi", "both")) {
    if ($Scope -eq "user") {
        $TargetDirs += (Join-Path $HOME ".agents\skills\$SkillName")
    } else {
        $TargetDirs += (Join-Path $ProjectRoot ".agents\skills\$SkillName")
    }
}

if ($Runtime -in @("claude", "both")) {
    if ($Scope -eq "user") {
        $TargetDirs += (Join-Path $HOME ".claude\skills\$SkillName")
    } else {
        $TargetDirs += (Join-Path $ProjectRoot ".claude\skills\$SkillName")
    }
}

# ── Step 1: pip install the Python package ────────────────────────────────
Write-Host "[1/2] Installing resume-skill Python package..."
pip install "$ScriptDir\renderer" --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Error "pip install failed. Ensure Python and pip are in PATH."
    exit 1
}
Write-Host "      Done - 'resume-skill' CLI is now available in PATH."

# ── Step 2: Copy SKILL.md into target skill directories ───────────────────
Write-Host ""
Write-Host "[2/2] Installing SKILL.md into agent skills directory..."
foreach ($Dest in $TargetDirs) {
    New-Item -ItemType Directory -Force -Path $Dest | Out-Null
    Copy-Item (Join-Path $ScriptDir "SKILL.md") (Join-Path $Dest "SKILL.md") -Force
    Write-Host "      Installed: $Dest\SKILL.md"
}

Write-Host ""
Write-Host "============================================================"
Write-Host "  Installation complete!"
Write-Host ""
Write-Host "  Verify CLI:      resume-skill --help"
if ($Runtime -in @("pi", "both")) {
    Write-Host "  Use in PI:       Skill is active! Tell PI: 'tailor my resume' or 'edit my resume'"
}
if ($Runtime -in @("claude", "both")) {
    Write-Host "  Use in Claude:   /build-tailored-resume"
}
Write-Host "============================================================"
Write-Host ""
