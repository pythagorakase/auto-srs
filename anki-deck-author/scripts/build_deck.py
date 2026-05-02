"""
build_deck.py — reusable Anki deck-builder infrastructure.

Provides three pre-configured note models (Cloze, Basic, Basic-and-Reversed),
a default CSS theme, a stable-GUID helper, a smart_lower() utility for the
acronym-preserving lowercase rule (principle §11), and a DeckBuilder class
that wires it all together.

Usage:
    from build_deck import DeckBuilder

    db = DeckBuilder(
        deck_root="My Topic",
        model_id_base=1730000000,   # any random integer; reuse across builds
        deck_id_base=1740000000,
    )

    # Cloze cards (atomic facts)
    db.add_cloze(
        sub_deck="Fundamentals",
        text="<u>Frame Indicates</u><br>{{c1::standard identity}}<br>{{c2::physical domain}}<br>{{c3::status}}",
        guid_seed="frame_indicates",
        tags=["frame"],
        extra="",   # optional examples shown only on back
        source="FM 1-02.2 Ch.1",
    )

    # Basic-reversed (symmetric pairs)
    db.add_reversed(
        sub_deck="Vocabulary",
        front="ephemeral",
        back="lasting for a very short time",
        guid_seed="vocab_ephemeral",
        tags=["vocab"],
        hint="adjective, formal",
        source="GRE wordlist",
    )

    # Basic (one-direction Q→A, e.g., long doctrinal definitions)
    db.add_basic(
        sub_deck="Definitions",
        front="<u>Company Team</u>",
        back="a combined-arms organization formed by attaching ...",
        guid_seed="def_company_team",
        tags=["task-force"],
        source="FM 3-90",
    )

    # Add media files (copies into the .apkg)
    db.add_media("/path/to/icon.png")

    db.write("output.apkg")
"""
from __future__ import annotations

import hashlib
import os
import re
from typing import List, Optional

import genanki


# =============================================================================
# CSS — clean, mobile-friendly default theme
# =============================================================================
DEFAULT_CSS = """
.card {
  font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
  font-size: 22px;
  text-align: center;
  color: #1a1a1a;
  background: #fafafa;
  padding: 20px 14px;
  line-height: 1.5;
}
.card img { max-width: 90%; max-height: 360px; }
.cloze { color: #b30000; font-weight: 700; }
.extra {
  font-size: 16px; color: #555; font-style: italic;
  display: block; margin-top: 12px;
}
.src {
  font-size: 13px; color: #888; font-style: italic;
  margin-top: 14px; display: block; border-top: 1px solid #ddd; padding-top: 10px;
}
.tagline { font-size: 13px; color: #aaa; }
hr { border: none; border-top: 1px solid #ddd; margin: 14px 0; }
u { text-decoration-thickness: 2px; text-underline-offset: 4px; }
"""


# =============================================================================
# Smart-lower (principle §11) — acronym-preserving lowercase
# =============================================================================
DEFAULT_PRESERVE_CAPS = {
    # Common military / medical / scientific acronyms — extend per domain
    "USA", "USS", "USAF", "USCG", "NATO", "FBI", "CIA", "NSA",
    "MEDEVAC", "CASEVAC", "MTF",
    "DNA", "RNA", "ATP", "NADH", "FADH",
    "URL", "API", "HTTP", "HTTPS", "JSON", "XML", "HTML", "CSS",
}


def smart_lower(s: str, preserve_caps: Optional[set] = None) -> str:
    """Lowercase free text but preserve acronyms, model designators, Roman numerals.

    Per principle §11. Rules per word-token:
      - Already-uppercase 2+-char tokens (CA, MP, ENY) → keep uppercase
      - Mixed alphanumeric tokens (M997, HH-60) → keep as-is (model designators)
      - Roman numerals (I, II, III, IV, ...) → keep uppercase
      - Tokens in preserve_caps allow-list (case-insensitive) → uppercase form
      - Everything else → lowercase
    """
    if preserve_caps is None:
        preserve_caps = DEFAULT_PRESERVE_CAPS
    out = []
    for tok in re.split(r"(\W+)", s):
        if not tok or not any(c.isalpha() or c.isdigit() for c in tok):
            out.append(tok)
            continue
        if tok.upper() in preserve_caps:
            out.append(tok.upper()); continue
        if any(c.isdigit() for c in tok) and any(c.isalpha() for c in tok):
            out.append(tok); continue                      # alphanumeric model #
        if tok.isupper() and len(tok) >= 2:
            out.append(tok); continue                      # already-caps acronym
        if re.fullmatch(r"[IVXLCDM]+", tok):
            out.append(tok.upper()); continue              # Roman numeral
        out.append(tok.lower())
    return "".join(out)


# =============================================================================
# Stable GUID helper (principle §13)
# =============================================================================
def stable_guid(*parts) -> str:
    """Generate a content-independent, stable GUID from semantic parts.

    Pass identifiers that describe what the note IS, not what it currently
    contains. Edits to card text won't change the GUID, so re-imports update
    in place rather than creating duplicates.

    Example:
        stable_guid("cloze", "fundamentals", "frame_indicates")
    """
    h = hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()
    return genanki.guid_for(h[:16])


# =============================================================================
# Model factories
# =============================================================================
def make_basic_model(model_id: int, css: str = DEFAULT_CSS) -> genanki.Model:
    return genanki.Model(
        model_id, "Anki Deck Author — Basic",
        fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Source"}],
        templates=[{
            "name": "Card 1",
            "qfmt": '<div class="q">{{Front}}</div>',
            "afmt": ('<div class="q">{{Front}}</div><hr>'
                     '<div class="a">{{Back}}</div>'
                     '{{#Source}}<span class="src">{{Source}}</span>{{/Source}}'),
        }],
        css=css,
    )


def make_basic_reversed_model(model_id: int, css: str = DEFAULT_CSS) -> genanki.Model:
    """Basic-and-Reversed (principle §12) — one note generates 2 cards."""
    return genanki.Model(
        model_id, "Anki Deck Author — Basic (and reversed)",
        fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Hint"}, {"name": "Source"}],
        templates=[
            {
                "name": "Card 1 (Front → Back)",
                "qfmt": ('<div class="q">{{Front}}</div>'
                         '{{#Hint}}<br><span class="tagline">{{Hint}}</span>{{/Hint}}'),
                "afmt": ('<div class="q">{{Front}}</div><hr>'
                         '<div class="a">{{Back}}</div>'
                         '{{#Source}}<span class="src">{{Source}}</span>{{/Source}}'),
            },
            {
                "name": "Card 2 (Back → Front)",
                "qfmt": ('<div class="q">{{Back}}</div>'
                         '{{#Hint}}<br><span class="tagline">{{Hint}}</span>{{/Hint}}'),
                "afmt": ('<div class="q">{{Back}}</div><hr>'
                         '<div class="a">{{Front}}</div>'
                         '{{#Source}}<span class="src">{{Source}}</span>{{/Source}}'),
            },
        ],
        css=css,
    )


def make_cloze_model(model_id: int, css: str = DEFAULT_CSS) -> genanki.Model:
    """Cloze model with an Extra field (principle §5) — examples render only on back."""
    return genanki.Model(
        model_id, "Anki Deck Author — Cloze",
        fields=[{"name": "Text"}, {"name": "Extra"}, {"name": "Source"}],
        templates=[{
            "name": "Cloze",
            "qfmt": "{{cloze:Text}}",
            "afmt": ("{{cloze:Text}}"
                     '{{#Extra}}<span class="extra">{{Extra}}</span>{{/Extra}}'
                     '{{#Source}}<span class="src">{{Source}}</span>{{/Source}}'),
        }],
        css=css,
        model_type=genanki.Model.CLOZE,   # critical — without this, cloze syntax renders literally
    )


# =============================================================================
# DeckBuilder — main API
# =============================================================================
class DeckBuilder:
    """Wrapper around genanki for an opinionated, well-designed Anki deck.

    Args:
        deck_root: top-level deck name (e.g., "CCC :: Unit Symbology").
        model_id_base: integer base for model IDs. Models get _base, _base+1, _base+2.
        deck_id_base: integer base for sub-deck IDs (auto-incremented per sub-deck).
        css: override the default CSS theme if you want a different look.
        preserve_caps: extend the smart_lower allow-list with domain acronyms.
    """

    def __init__(self, deck_root: str, model_id_base: int = 1730000000,
                 deck_id_base: int = 1740000000, css: str = DEFAULT_CSS,
                 preserve_caps: Optional[set] = None):
        self.deck_root = deck_root
        self.model_basic = make_basic_model(model_id_base, css)
        self.model_basic_reversed = make_basic_reversed_model(model_id_base + 1, css)
        self.model_cloze = make_cloze_model(model_id_base + 2, css)
        self._sub_decks: dict[str, genanki.Deck] = {}
        self._next_deck_id = deck_id_base
        self._media: set[str] = set()
        self.preserve_caps = preserve_caps

    def smart_lower(self, s: str) -> str:
        """Apply principle §11 to a string. Use for unit names, term labels, etc."""
        return smart_lower(s, self.preserve_caps)

    def _get_sub_deck(self, sub_deck: str) -> genanki.Deck:
        if sub_deck not in self._sub_decks:
            full_name = f"{self.deck_root}::{sub_deck}"
            self._sub_decks[sub_deck] = genanki.Deck(self._next_deck_id, full_name)
            self._next_deck_id += 1
        return self._sub_decks[sub_deck]

    def add_cloze(self, sub_deck: str, text: str, guid_seed: str,
                  tags: Optional[List[str]] = None, extra: str = "",
                  source: str = "") -> None:
        """Add a cloze note. `text` should follow principles §1–§11.

        guid_seed should be semantic and stable (e.g., "frame_indicates"), per §13.
        extra renders only on the back — put `e.g., ...` examples here per §5.
        """
        note = genanki.Note(
            model=self.model_cloze,
            fields=[text, extra, source],
            tags=tags or [],
            guid=stable_guid("cloze", sub_deck, guid_seed),
        )
        self._get_sub_deck(sub_deck).add_note(note)

    def add_reversed(self, sub_deck: str, front: str, back: str, guid_seed: str,
                     tags: Optional[List[str]] = None, hint: str = "",
                     source: str = "") -> None:
        """Add a basic-and-reversed note (principle §12) — generates 2 cards."""
        note = genanki.Note(
            model=self.model_basic_reversed,
            fields=[front, back, hint, source],
            tags=tags or [],
            guid=stable_guid("reversed", sub_deck, guid_seed),
        )
        self._get_sub_deck(sub_deck).add_note(note)

    def add_basic(self, sub_deck: str, front: str, back: str, guid_seed: str,
                  tags: Optional[List[str]] = None, source: str = "") -> None:
        """Add a one-direction Basic Q→A note. Use sparingly — long doctrinal definitions
        that don't decompose well into cloze atoms."""
        note = genanki.Note(
            model=self.model_basic,
            fields=[front, back, source],
            tags=tags or [],
            guid=stable_guid("basic", sub_deck, guid_seed),
        )
        self._get_sub_deck(sub_deck).add_note(note)

    def add_media(self, path: str) -> None:
        """Register a media file (image, audio) referenced by notes.

        Note text should reference the file by its basename: <img src="filename.png">.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        self._media.add(path)

    def write(self, output_path: str) -> dict:
        """Build and write the .apkg file. Returns a summary dict."""
        decks = list(self._sub_decks.values())
        package = genanki.Package(decks)
        package.media_files = sorted(self._media)
        package.write_to_file(output_path)
        return {
            "path": output_path,
            "size_kb": os.path.getsize(output_path) / 1024,
            "decks": [d.name for d in decks],
            "note_counts": {d.name: len(d.notes) for d in decks},
            "media_files": len(self._media),
        }


if __name__ == "__main__":
    # Tiny smoke test — build a 3-card demo deck
    db = DeckBuilder(deck_root="Demo", model_id_base=1730099999, deck_id_base=1740099999)
    db.add_cloze(
        "Fundamentals",
        text="<u>Demo Card</u><br>this is a {{c1::cloze}} test with an {{c2::extra}} field.",
        extra="e.g., this only shows on the back.",
        guid_seed="demo_cloze",
        tags=["demo"],
        source="smoke test",
    )
    db.add_reversed(
        "Pairs",
        front="ephemeral",
        back="lasting a very short time",
        guid_seed="demo_pair",
        hint="adjective",
        tags=["demo"],
    )
    summary = db.write("/tmp/demo_deck.apkg")
    print(summary)
