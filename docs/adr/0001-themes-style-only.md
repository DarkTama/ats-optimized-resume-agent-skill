# Themes change Styling only, enforced in code

## Status

Accepted

## Context

We want users to choose between several visual designs (Themes) for DOCX and PDF output. Resume builders usually split into two camps: visually rich layouts that ATS parsers mangle (columns, text boxes, rating bars), and plain layouts that parse well but look dull.

## Decision

A Theme may change Styling only: typography, color, spacing, alignment, and section dividers. A Theme may not change Structure: no multi-column layouts, text boxes, shapes, or graphics such as skill-rating bars. Themes use ATS-safe fonts only.

Code enforces this. Every Theme in the registry must pass `validate_output.py` and reach a minimum score from `ats/scorer.py` in an automated test.

## Alternatives considered

- **Free-form layouts**: more design freedom, but any Theme could silently break ATS parsing, which is the point of this project.
- **Convention only, no enforcement**: cheap, but the rule erodes as Themes get added.

## Consequences

- Users cannot get a two-column or graphic-heavy design from this tool. This is intentional.
- Adding a Theme means passing the ATS gate, which adds a small test cost.
- Themes that need non-ATS-safe fonts are rejected or must fall back to a safe font.
