# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Source of truth: `anki-deck-author/`

All workflow guidance for this directory lives in `anki-deck-author/`, not here. This is intentional — the same workflow is run across multiple harnesses (Claude Code, Claude Cowork, Codex local), so instructions are kept harness-agnostic inside the skill folder rather than duplicated into per-harness files.

**Read first:** `anki-deck-author/SKILL.md`. It defines what this directory is, the deck-design principles, the build / verify / lint pipeline, the AnkiConnect bridge for live edits, and pointers to its `references/` files (`common-ai-drift.md`, `principles-detail.md`, `workflows.md`, `verification.md`).

Do not re-summarize that material here or in new docs. If guidance needs to change, edit it inside `anki-deck-author/` so every harness picks it up.
