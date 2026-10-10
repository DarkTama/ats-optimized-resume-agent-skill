#!/usr/bin/env bash
# install.sh — installs the build-tailored-resume skill for PI-Desktop & Claude Code
#
# Usage:
#   ./install.sh                           # interactive prompt
#   ./install.sh --runtime=pi --user       # PI-Desktop (global, available in all projects)
#   ./install.sh --runtime=pi --project    # PI-Desktop (current project)
#   ./install.sh --runtime=claude --user   # Claude Code (global)
#   ./install.sh --runtime=both --user     # Both runtimes

set -e

SKILL_NAME="build-tailored-resume"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCOPE=""
RUNTIME=""
PROJECT_PATH=""

# ── Parse flags ───────────────────────────────────────────────────────────────
for arg in "$@"; do
  case "$arg" in
    --user)             SCOPE="user"    ;;
    --project)          SCOPE="project" ;;
    --local)            SCOPE="local"   ;;
    --runtime=*)        RUNTIME="${arg#*=}" ;;
    --project-path=*)   PROJECT_PATH="${arg#*=}" ;;
  esac
done

echo ""
echo "============================================================"
echo "  build-tailored-resume - AI Agent Skill Installer"
echo "============================================================"

# ── Interactive Runtime selection when no flag given ──────────────────────────
if [[ -z "$RUNTIME" ]]; then
  echo ""
  echo "  Which AI assistant/runtime do you want to install for?"
  echo ""
  echo "  [1] PI-Desktop / Agent Skills (~/.agents/skills)"
  echo "  [2] Claude Code               (~/.claude/skills)"
  echo "  [3] Both                      (recommended)"
  echo ""

  while true; do
    read -rp "  Enter 1, 2, or 3: " RCHOICE
    case "$RCHOICE" in
      1) RUNTIME="pi";     break ;;
      2) RUNTIME="claude"; break ;;
      3) RUNTIME="both";   break ;;
      *) echo "  Please enter 1, 2, or 3." ;;
    esac
  done
fi

# ── Interactive scope selection when no flag given ────────────────────────────
if [[ -z "$SCOPE" ]]; then
  echo ""
  echo "  Where do you want to install this skill?"
  echo ""
  echo "  [1] User    - available in ALL your projects (recommended)"
  echo "  [2] Project - current project only"
  echo "  [3] Local   - current project only (not committed)"
  echo ""

  while true; do
    read -rp "  Enter 1, 2, or 3: " SCHOICE
    case "$SCHOICE" in
      1) SCOPE="user";    break ;;
      2) SCOPE="project"; break ;;
      3) SCOPE="local";   break ;;
      *) echo "  Please enter 1, 2, or 3." ;;
    esac
  done
fi

echo ""
echo "  Runtime: $RUNTIME"
echo "  Scope:   $SCOPE"
echo ""

# ── Determine Project Root if needed ──────────────────────────────────────────
PROJECT_ROOT=""
if [[ "$SCOPE" != "user" ]]; then
  if [[ -n "$PROJECT_PATH" ]]; then
    PROJECT_ROOT="$PROJECT_PATH"
  else
    PROJECT_ROOT="$(pwd)"
    while [[ "$PROJECT_ROOT" != "/" ]]; do
      if [[ -d "$PROJECT_ROOT/.git" || -d "$PROJECT_ROOT/.agents" || -d "$PROJECT_ROOT/.claude" ]]; then break; fi
      PROJECT_ROOT="$(dirname "$PROJECT_ROOT")"
    done
  fi
fi

# ── Collect Target Directories ────────────────────────────────────────────────
TARGET_DIRS=()

if [[ "$RUNTIME" == "pi" || "$RUNTIME" == "both" ]]; then
  if [[ "$SCOPE" == "user" ]]; then
    TARGET_DIRS+=("$HOME/.agents/skills/$SKILL_NAME")
  else
    TARGET_DIRS+=("$PROJECT_ROOT/.agents/skills/$SKILL_NAME")
  fi
fi

if [[ "$RUNTIME" == "claude" || "$RUNTIME" == "both" ]]; then
  if [[ "$SCOPE" == "user" ]]; then
    TARGET_DIRS+=("$HOME/.claude/skills/$SKILL_NAME")
  else
    TARGET_DIRS+=("$PROJECT_ROOT/.claude/skills/$SKILL_NAME")
  fi
fi

# ── Step 1: pip install the Python package ────────────────────────────────────
echo "[1/2] Installing resume-skill Python package..."
pip install "$SCRIPT_DIR/renderer" --quiet
echo "      Done - 'resume-skill' CLI is now available in PATH."

# ── Step 2: Copy SKILL.md into target directories ─────────────────────────────
echo ""
echo "[2/2] Installing SKILL.md into agent skills directory..."
for DEST in "${TARGET_DIRS[@]}"; do
  mkdir -p "$DEST"
  cp "$SCRIPT_DIR/SKILL.md" "$DEST/SKILL.md"
  echo "      Installed: $DEST/SKILL.md"
done

echo ""
echo "============================================================"
echo "  Installation complete!"
echo ""
echo "  Verify CLI:    resume-skill --help"
if [[ "$RUNTIME" == "pi" || "$RUNTIME" == "both" ]]; then
  echo "  Use in PI:     Skill is active! Tell PI: 'tailor my resume' or 'edit my resume'"
fi
if [[ "$RUNTIME" == "claude" || "$RUNTIME" == "both" ]]; then
  echo "  Use in Claude: /build-tailored-resume"
fi
echo "============================================================"
echo ""
