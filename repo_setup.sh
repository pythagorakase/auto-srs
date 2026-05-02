#!/bin/bash
# One-shot repo setup. Run this once from your terminal:
#   bash ~/auto_srs/repo_setup.sh
#
# It cleans up sandbox cruft, initializes git, adds the remote, and stages an initial commit.

set -e
cd "$(dirname "$0")"

echo "→ Cleaning sandbox cruft (files Claude couldn't delete from inside)..."
rm -rf .git/ 2>/dev/null || true
rm -f .DS_Store delete_guids.txt anki-deck-author.skill
rm -f scripts/ccc_cleanup.py scripts/ccc_diagnose.py
rm -rf anki-deck-author/.obsidian/
rm -rf anki-deck-author/reports/  # empty dir left over
find . -name '.DS_Store' -delete 2>/dev/null || true
find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true

echo "→ Initializing git..."
git init -b main

echo "→ Configuring identity (override if you want)..."
git config user.email "neilgordonclark@gmail.com"
git config user.name "Neil Clark"

echo "→ Adding files..."
git add -A

echo "→ What will be committed:"
git status --short
echo ""
echo "→ Counts:"
echo "   tracked: $(git ls-files | wc -l | tr -d ' ')"
echo "   ignored: $(git ls-files --others --ignored --exclude-standard | wc -l | tr -d ' ')"

echo ""
echo "→ Adding remote: https://github.com/pythagorakase/auto-srs.git"
git remote add origin https://github.com/pythagorakase/auto-srs.git

echo ""
echo "✓ Setup complete. To make the initial commit and push:"
echo ""
echo "    git commit -m 'Initial commit: auto-srs skill + repo conventions'"
echo "    git push -u origin main"
echo ""
echo "(Review the staged files first — run 'git status' or 'git diff --cached'.)"
