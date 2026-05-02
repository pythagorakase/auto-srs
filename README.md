# auto-srs

Automated spaced-repetition deck builder. Pairs the [`anki-deck-author`](anki-deck-author/SKILL.md) skill — an opinionated set of Anki card-design principles refined over many study cycles — with utility scripts that turn source documents (PDFs, slide decks, lecture notes) into well-designed `.apkg` decks.

The skill is harness-agnostic: same skill folder used by Claude Code, Claude Cowork, and (manually loaded) Codex. Single source of truth in `anki-deck-author/`.

## Repo layout

```
auto_srs/
├── anki-deck-author/         # the skill — canonical source for principles, scripts, examples
│   ├── SKILL.md              #   read this first
│   ├── references/           #   principles-detail, common-ai-drift, workflows, verification
│   ├── scripts/              #   reusable: build_deck, lint_deck, verify_deck
│   └── examples/             #   reference decks demonstrating principles in action
│
├── scripts/                  # generic, repo-wide utilities (currently empty)
│
├── courses/                  # course-specific source material — gitignored by default
│   └── README.md             #   how to organize course folders
│
└── temp/                     # build artifacts, ephemeral .apkg files (gitignored)
```

## Setup

```bash
# Clone
git clone https://github.com/pythagorakase/auto-srs.git
cd auto-srs

# Install Python deps
pip install -r requirements.txt
```

## Using the skill across harnesses

**Claude Code** (auto-discovery):
```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/anki-deck-author" ~/.claude/skills/anki-deck-author
```

**Claude Cowork:** package the skill and install via the `.skill` file:
```bash
python -m anki-deck-author.scripts.package_skill anki-deck-author/ temp/
# then double-click temp/anki-deck-author.skill in Cowork
```

**Codex:** load `anki-deck-author/SKILL.md` as a system prompt or context file. References in `anki-deck-author/references/` can be loaded on demand.

## Quickstart

In any harness, ask the agent for help with flashcards, a deck, an .apkg file, or "help me memorize X". The skill triggers automatically. The full workflow (parallel-agent authoring, self-audit, fresh-agent leak detection, AnkiConnect cleanup) is documented inside the skill at `anki-deck-author/references/workflows.md`.

## License

MIT — see [LICENSE](LICENSE).
