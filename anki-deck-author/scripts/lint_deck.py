"""
lint_deck.py — Antipattern linter for built .apkg files.

Scans every note against the drift patterns from references/common-ai-drift.md
and reports flagged notes for review. Runs as a non-fatal check (warnings); the
author or fresh-agent reviewer decides which flags are false positives.

Usage:
    python lint_deck.py path/to/deck.apkg [--strict] [--show-suppressed]
    python lint_deck.py --anki-deck "<TOPIC>::<CODE>" [--strict] [--show-suppressed]

--anki-deck: query a live Anki deck root through AnkiConnect; exact deck and
descendant subdecks are included. Repeat --anki-deck to lint multiple roots as
one combined corpus.

--strict: exit non-zero if any flags found (useful in CI).

Suppression tags: add lint-ok-d17 to suppress a specific D# for a manually
reviewed note, or lint-ok-all for rare note-wide suppression.

Coverage: 16 of 18 drift patterns are implemented (D1, D2, D3, D5, D6, D8, D9,
D10, D11, D12, D13, D14, D15, D16, D17, D18). D4 (asymmetric attribution that needs thin-slicing per §7) and D7
(verbose Basic Q→A that should have been compressed cloze per §21) are not
implemented because regex can't decide when a multi-cloze list crosses into
asymmetric attribution, or when a Basic answer is "too verbose to be Basic."
Catch those in the fresh-agent leak audit (SKILL.md workflow step 7).

When adding new drift rules: append-only. Don't renumber existing rules — the
D# IDs are stable across SKILL.md, common-ai-drift.md, and this file.
"""
import argparse
from collections import Counter, defaultdict
import html
import json
import os
import re
import sqlite3
import sys
import tempfile
import urllib.request
import zipfile

try:
    import zstandard
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False


LABEL_RE = re.compile(r"<i>(.*?)</i>\s*<br>", re.I | re.S)
CLOZE_RE = re.compile(r"\{\{c\d+::")
CLOZE_FULL_RE = re.compile(r"\{\{c(\d+)::(.*?)(?:::[^{}]*)?\}\}", re.S)
LEADING_HEADING_RE = re.compile(r"^\s*<u>.*?</u>\s*<br>\s*", re.I | re.S)
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9'-]*", re.I)

VAGUE_LABEL_RE = re.compile(
    r"\b("
    r"often[- ]missed|main\s+(?:readiness|corrective)\s+function|unique role|"
    r"also conducts|additional training|best environment|primary driver|"
    r"tempered by|as needed|misc(?:ellaneous)?|other"
    r")\b",
    re.I,
)

ENTITY_SPECIFIC_LABEL_RE = re.compile(
    r"\b(?:[a-z]{1,4}-\d+[a-z0-9]*|m\d{3,}[a-z0-9]*)\b",
    re.I,
)

REPEAT_TOKEN_STOPWORDS = {
    "about", "above", "across", "after", "again", "against", "also", "and",
    "another", "are", "around", "because", "before", "below", "between",
    "both", "but", "can", "cannot", "care", "capability", "capabilities",
    "class", "concept", "context", "day", "days", "does", "each", "fact",
    "facts", "for", "from", "function", "functions", "has", "have", "into",
    "key", "may", "medical", "mission", "must", "not", "only", "other",
    "patient", "patients", "program", "provide", "provides", "provided",
    "responsibility", "responsibilities", "role", "section", "should", "such",
    "support", "supports", "supported", "system", "task", "than", "that",
    "the", "their", "then", "there", "these", "this", "those", "through",
    "unit", "used", "uses", "using", "value", "values", "when", "where",
    "which", "while", "with", "within", "without",
}


def normalize_label(label):
    """Return a normalized structural label without styling punctuation."""
    label = html.unescape(re.sub(r"<[^>]+>", "", label))
    label = label.replace("\xa0", " ")
    label = re.sub(r"\s+", " ", label).strip()
    return label.rstrip(":").strip().lower()


def normalize_tags(tags):
    if isinstance(tags, str):
        tags = tags.split()
    return {str(tag).strip().lower() for tag in tags if str(tag).strip()}


def suppression_tags(rule):
    rule_id = rule.split("-", 1)[0].lower()
    return {"lint-ok-all", f"lint-ok-{rule_id}", f"lint-ok-{rule.lower()}"}


def is_suppressed(rule, tags):
    return bool(normalize_tags(tags) & suppression_tags(rule))


def cloze_count(text):
    return len(CLOZE_RE.findall(text))


def plain_text(text):
    """Return normalized plain text for lightweight lint heuristics."""
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    text = text.replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip().lower()


def repeated_string_candidates(text):
    """Return meaningful token/short-phrase candidates from normalized text."""
    tokens = TOKEN_RE.findall(plain_text(text))
    candidates = []
    for token in tokens:
        if len(token) >= 4 and token not in REPEAT_TOKEN_STOPWORDS:
            candidates.append(token)

    # Catch compact repeated atoms such as "role 1" that single-token filters skip.
    for size in (2, 3):
        for start in range(0, len(tokens) - size + 1):
            gram = tokens[start:start + size]
            if all(token in REPEAT_TOKEN_STOPWORDS for token in gram):
                continue
            if not any(len(token) >= 4 or token.isdigit() for token in gram):
                continue
            phrase = " ".join(gram)
            if len(phrase) >= 6:
                candidates.append(phrase)
    return candidates


def cloze_answers(text):
    """Return [(ordinal, answer_text), ...] for simple Anki cloze deletions."""
    return [(match.group(1), match.group(2)) for match in CLOZE_FULL_RE.finditer(text)]


def mixed_repeat_issues(text):
    """Return repeated strings with mixed visible/clozed or unlinked cloze states."""
    if "{{c" not in text:
        return []

    visible = CLOZE_FULL_RE.sub(" ", text)
    # Italic labels are structural scaffolding, not repeated content atoms.
    visible = LABEL_RE.sub(" ", visible)
    visible_counts = Counter(repeated_string_candidates(visible))

    clozed_counts = Counter()
    cloze_ordinals_by_candidate = defaultdict(set)
    for ordinal, answer in cloze_answers(text):
        for candidate in repeated_string_candidates(answer):
            clozed_counts[candidate] += 1
            cloze_ordinals_by_candidate[candidate].add(ordinal)

    issues = []
    for candidate in sorted(set(visible_counts) | set(clozed_counts)):
        visible_count = visible_counts[candidate]
        clozed_count = clozed_counts[candidate]
        if visible_count + clozed_count < 2:
            continue
        ordinals = sorted(cloze_ordinals_by_candidate[candidate], key=int)
        if visible_count and clozed_count:
            issues.append(f"{candidate} visible {visible_count}x / clozed c{','.join(ordinals)}")
        elif len(ordinals) > 1:
            issues.append(f"{candidate} clozed under multiple ordinals: c{','.join(ordinals)}")
    return issues


def overfit_entity_labels(text):
    """Return labels that contain entity/model designators instead of abstract roles."""
    labels = []
    for label, _segment in label_segments(text):
        if ENTITY_SPECIFIC_LABEL_RE.search(label) and re.search(r"[a-z]", label):
            labels.append(label)
    return labels


def label_segments(text):
    """Return [(label, segment_after_label_before_next_label), ...]."""
    matches = list(LABEL_RE.finditer(text))
    segments = []
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        segments.append((normalize_label(match.group(1)), text[match.end():end]))
    return segments


def template_signature(text):
    """Return a normalized italic-label signature if a note looks templated."""
    labels = tuple(label for label, _segment in label_segments(text) if label)
    if len(labels) < 2:
        return ()
    return labels


def is_answer_only_segment(segment):
    """True when a label points directly at one or more cloze-only values."""
    if "{{c" not in segment:
        return False
    without_clozes = re.sub(r"\{\{c\d+::.*?(?:::.*?)?\}\}", "", segment)
    without_tags = html.unescape(re.sub(r"<[^>]+>", "", without_clozes))
    without_tags = without_tags.replace("\xa0", " ")
    residue = re.sub(r"[\s/;,+&()\-–—:]+", "", without_tags)
    return not residue


def is_untemplated_cloze_list(text):
    """True for heading/plain body notes that are just a bare cloze list."""
    if LABEL_RE.search(text) or cloze_count(text) < 2:
        return False
    body = LEADING_HEADING_RE.sub("", text, count=1)
    if body == text:
        return False
    return is_answer_only_segment(body)


def open_apkg(apkg_path):
    """Extract apkg and return SQLite connection. Caller must close."""
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(apkg_path) as zf:
        zf.extractall(tmp)
    src = next((os.path.join(tmp, n) for n in
                ("collection.anki21b", "collection.anki21", "collection.anki2")
                if os.path.exists(os.path.join(tmp, n))), None)
    if src is None:
        raise FileNotFoundError(f"No collection in {apkg_path}")
    if src.endswith(".anki21b"):
        if not HAS_ZSTD:
            raise RuntimeError("zstandard required for newer Anki 21b format. pip install zstandard")
        dst = os.path.join(tmp, "c.db")
        zstandard.ZstdDecompressor().copy_stream(open(src, "rb"), open(dst, "wb"))
        src = dst
    conn = sqlite3.connect(src)
    conn.create_collation("unicase", lambda a, b: -1 if a < b else (1 if a > b else 0))
    return conn, tmp


def anki_request(url, action, params=None):
    payload = json.dumps({"action": action, "version": 6, "params": params or {}}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if data.get("error"):
        raise RuntimeError(f"AnkiConnect {action} failed: {data['error']}")
    return data.get("result")


def anki_deck_query(deck_name):
    escaped = deck_name.replace("\\", "\\\\").replace('"', '\\"')
    return f'deck:"{escaped}"'


def fetch_anki_note_records(deck_roots, url):
    """Return note records from live Anki for exact deck roots plus descendants."""
    deck_names = anki_request(url, "deckNames")
    selected_decks = []
    for root in deck_roots:
        matches = [name for name in deck_names if name == root or name.startswith(root + "::")]
        if not matches:
            raise ValueError(f"No live Anki deck matched {root!r}")
        selected_decks.extend(matches)

    note_ids = []
    seen_notes = set()
    for deck_name in sorted(set(selected_decks)):
        ids = anki_request(url, "findNotes", {"query": anki_deck_query(deck_name)})
        for note_id in ids:
            if note_id not in seen_notes:
                note_ids.append(note_id)
                seen_notes.add(note_id)

    note_records = []
    for start in range(0, len(note_ids), 100):
        infos = anki_request(url, "notesInfo", {"notes": note_ids[start:start + 100]})
        for info in infos:
            ordered_fields = sorted(info["fields"].items(), key=lambda item: item[1].get("order", 0))
            field_values = [field["value"] for _name, field in ordered_fields]
            fields = {name: field["value"] for name, field in ordered_fields}
            text = fields.get("Text", "") or fields.get("Front", "")
            signature = template_signature(text)
            tags = info.get("tags", [])
            note_records.append((info["noteId"], info.get("modelName", "?"), field_values, fields, signature, tags))
    return note_records


def fetch_apkg_note_records(apkg_path):
    conn, _tmp = open_apkg(apkg_path)
    cur = conn.cursor()

    try:
        cur.execute("SELECT id, name FROM notetypes")
        models = {r[0]: r[1] for r in cur.fetchall()}
        cur.execute("SELECT ntid, ord, name FROM fields ORDER BY ntid, ord")
        fields_by_model = {}
        for ntid, ord_, name in cur.fetchall():
            fields_by_model.setdefault(ntid, []).append(name)
    except sqlite3.OperationalError:
        models_json = json.loads(cur.execute("SELECT models FROM col").fetchone()[0])
        models = {int(mid): m["name"] for mid, m in models_json.items()}
        fields_by_model = {int(mid): [f["name"] for f in m["flds"]] for mid, m in models_json.items()}

    note_records = []
    cur.execute("SELECT id, mid, flds, tags FROM notes")
    for nid, mid, flds, tags_raw in cur.fetchall():
        field_names = fields_by_model.get(mid, [])
        field_values = flds.split("\x1f")
        fields = dict(zip(field_names, field_values))
        text = fields.get("Text", "") or fields.get("Front", "")
        signature = template_signature(text)
        tags = (tags_raw or "").split()
        note_records.append((nid, models.get(mid, "?"), field_values, fields, signature, tags))

    conn.close()
    return note_records


def run_lint(note_records, show_suppressed=False):
    signature_counts = {}
    for _nid, _model_name, _field_values, fields, signature, _tags in note_records:
        if signature:
            signature_counts[signature] = signature_counts.get(signature, 0) + 1

    total_flags = 0
    flagged_notes = 0
    suppressed_flags = 0
    by_rule = {}
    for nid, model_name, field_values, fields, signature, tags in note_records:
        flags = lint_note(nid, model_name, fields)
        if signature and signature_counts.get(signature) == 1:
            text = fields.get("Text", "") or fields.get("Front", "")
            segments = label_segments(text)
            answer_only_labels = [
                label for label, segment in segments
                if label and is_answer_only_segment(segment)
            ]
            if answer_only_labels:
                sample = ", ".join(answer_only_labels[:4])
                flags.append(("D12-orphan-label-to-cloze",
                              f"Orphan template signature has label(s) mapping directly to cloze-only value(s): {sample}. "
                              f"If these labels are real slots, add sibling notes with the same signature; otherwise lift values out of labels."))
            if len(answer_only_labels) >= 2:
                sample = ", ".join(answer_only_labels[:4])
                flags.append(("D13-orphan-side-by-side-mapping",
                              f"Orphan template maps multiple labels directly to cloze-only values: {sample}. "
                              f"Repeated signatures are allowed; singleton mapping tables are suspect."))
            labels = " → ".join(signature[:6])
            flags.append(("D15-singleton-template",
                          f"Italic-label signature is used by no exact sibling notes: {labels}. "
                          f"Good templates should recur; if this is a one-off, verify each label is still an abstract role."))
        active_flags = []
        note_suppressed = []
        for rule, msg in flags:
            if is_suppressed(rule, tags):
                note_suppressed.append((rule, msg))
            else:
                active_flags.append((rule, msg))
        suppressed_flags += len(note_suppressed)
        if show_suppressed and note_suppressed:
            print(f"\n--- nid {nid} ({model_name}) suppressed by tag(s): {', '.join(sorted(normalize_tags(tags)))} ---")
            for rule, msg in note_suppressed:
                print(f"  [{rule}] {msg}")
            preview = (field_values[0] if field_values else "")[:200].replace("\n", " ")
            print(f"  text: {preview}")
        flags = active_flags
        if flags:
            flagged_notes += 1
            total_flags += len(flags)
            for rule, _msg in flags:
                by_rule[rule] = by_rule.get(rule, 0) + 1
            print(f"\n--- nid {nid} ({model_name}) ---")
            for rule, msg in flags:
                print(f"  [{rule}] {msg}")
            preview = (field_values[0] if field_values else "")[:200].replace("\n", " ")
            print(f"  text: {preview}")

    print(f"\n{'='*60}")
    print(f"Total notes scanned: {len(note_records)}")
    print(f"Notes with flags:    {flagged_notes}")
    print(f"Total flags raised:  {total_flags}")
    print(f"Suppressed flags:    {suppressed_flags}")
    if by_rule:
        print(f"\nBy rule:")
        for rule, count in sorted(by_rule.items(), key=lambda x: -x[1]):
            print(f"  {rule}: {count}")
    return total_flags


# ---------- Lint rules ----------
def lint_note(note_id, model_name, fields):
    """Return list of (rule_id, message) for any antipatterns detected."""
    flags = []
    text = fields.get("Text", "") or fields.get("Front", "")
    extra = fields.get("Extra", "") or fields.get("Back Extra", "")

    # Drift #1 — abbreviation-as-cloze inside template
    if re.search(r"<i>abbreviation:</i>\s*<br>\s*\{\{c\d+::", text, re.I):
        flags.append(("D1-abbrev-in-template",
                      "Abbreviation appears as a cloze inside a template. Move to heading + Basic acronym card."))

    # Drift #2 — image in extra, definition in text (likely test-direction inversion)
    if "<i>definition:</i>" in text.lower() and re.search(r'<img\s+src=', extra, re.I):
        flags.append(("D2-image-back-def-front",
                      "Image in extra + definition in text — usually test-direction is inverted. Should image be the prompt?"))

    # Drift #3 — high-precision numbers in cloze
    for match in CLOZE_FULL_RE.finditer(text):
        a = match.group(2).strip()
        prev_char = text[match.start() - 1:match.start()]
        next_char = text[match.end():match.end() + 1]
        in_alphanumeric_designator = (
            re.fullmatch(r"\d{3,}", a)
            and (prev_char.isalpha() or next_char.isalpha())
        )
        if in_alphanumeric_designator:
            continue
        if re.fullmatch(r"\d+\.\d+%?", a) or re.fullmatch(r"\d{3,}%?", a) or re.search(r"\d+\s*per\s*[\d,]+", a):
            flags.append(("D3-precision-number",
                          f'Cloze answer "{a}" is high-precision. Consider reverse direction or move to extra.'))

    # Drift #5 — trivial cloze deletions (small-int cloze near another small-int cloze in same note)
    nums = re.findall(r'\{\{c\d+::(\d{1,2})\}\}', text)
    if len(nums) >= 2 and len(set(nums)) == len(nums):
        flags.append(("D5-trivial-deletions-suspect",
                      f"Multiple small-int clozes ({nums}) in one note — verify they're not answerable by elimination."))

    # Drift #6 — heading-only front (Basic) without term sub-label
    if not text.startswith("<i>") and re.fullmatch(r"<u>[^<]+</u>", text.strip()):
        flags.append(("D6-heading-only-front",
                      "Heading on front with no <i>term:</i> companion — front may be ambiguous."))

    # Drift #8 — arithmetic leak (sum/total visible alongside multipliers)
    if re.search(r"\b(total|sum|altogether|combined)\b", text, re.I) and len(re.findall(r"\{\{c\d+::\d+\}\}", text)) >= 2:
        flags.append(("D8-arithmetic-leak",
                      "Total/sum visible alongside numeric clozes — answer may be derivable arithmetically."))

    # Drift #9 — examples in cloze body (e.g., adjacency)
    if re.search(r"\(\s*e\.?g\.?,?\s*[^)]+\)", text, re.I):
        flags.append(("D9-example-in-body",
                      "'e.g., ...' inline in card text — examples should be in extra to avoid synonym leaks."))

    # Drift #10 — abbreviation field exists but is empty / has placeholder
    if re.search(r"<i>abbreviation:</i>\s*<br>\s*(n/a|none|—|-)\b", text, re.I):
        flags.append(("D10-empty-template-slot",
                      "Empty abbreviation slot — drop the slot rather than fill with placeholder."))

    # Drift #11 — acronym/expansion paired with a clozed answer (per §30)
    # Pattern A: cloze contains multi-word lowercase phrase, parenthetical is uppercase acronym
    for m in re.finditer(r'\{\{c\d+::([a-z][^}]*\s[^}]+)\}\}\s*\(([A-Z]{2,6})\)', text):
        flags.append(("D11-acronym-expansion-pair",
                      f'Cloze "{m.group(1)}" paired with parenthetical "{m.group(2)}" — '
                      f'acronym leaks the answer. Ship one form per §30.'))
    # Pattern B: cloze contains uppercase acronym, parenthetical contains lowercase expansion
    for m in re.finditer(r'\{\{c\d+::([A-Z]{2,6})\}\}\s*\(([a-z][^)]+)\)', text):
        flags.append(("D11-acronym-expansion-pair",
                      f'Cloze "{m.group(1)}" paired with parenthetical "{m.group(2)}" — '
                      f'expansion leaks the answer. Ship one form per §30.'))

    # Drift #14 — vague/editorial prompt labels
    labels = label_segments(text)
    vague_labels = [label for label, _segment in labels if VAGUE_LABEL_RE.search(label)]
    if vague_labels:
        sample = ", ".join(sorted(set(vague_labels))[:4])
        flags.append(("D14-vague-prompt-label",
                      f"Vague or editorial prompt label(s): {sample}. "
                      f"Replace with a concrete structural slot or delete the low-yield atom."))

    # Drift #16 — heading plus bare cloze list, with no reusable slot labels
    if is_untemplated_cloze_list(text):
        flags.append(("D16-untemplated-cloze-list",
                      "Heading plus bare multi-cloze list has no template signature. "
                      "Convert to labeled slots so sibling notes can prove the template is reusable."))

    # Drift #17 — repeated strings inconsistently visible/clozed
    repeat_issues = mixed_repeat_issues(text)
    if repeat_issues:
        sample = "; ".join(repeat_issues[:4])
        flags.append(("D17-mixed-repeat-cloze-state",
                      f"Repeated string(s) have mixed visible/clozed or unlinked cloze states: {sample}. "
                      "Either leave every occurrence visible, or hide every occurrence with the same linked cloze number."))

    # Drift #18 — entity-specific labels that should be normalized into values
    entity_labels = overfit_entity_labels(text)
    if entity_labels:
        sample = ", ".join(entity_labels[:4])
        flags.append(("D18-overfit-entity-label",
                      f"Italic label(s) look like overfit schema/table names containing entity-specific tokens: {sample}. "
                      "Treat the first italic label like a SQL table name: use an abstract slot such as vehicle/unit/system, "
                      "then store the entity as a value."))

    return flags


# ---------- Main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("apkg", nargs="?", help="Path to .apkg file")
    ap.add_argument("--anki-deck", action="append", default=[],
                    help="Live Anki deck root to lint via AnkiConnect. Can be repeated; descendants are included.")
    ap.add_argument("--anki-url", default="http://127.0.0.1:8765",
                    help="AnkiConnect endpoint for --anki-deck")
    ap.add_argument("--strict", action="store_true", help="Exit 1 if any flags found")
    ap.add_argument("--show-suppressed", action="store_true",
                    help="Print flags suppressed by lint-ok-d# or lint-ok-all tags")
    args = ap.parse_args()

    if args.anki_deck:
        print(f"Linting live Anki deck root(s): {', '.join(args.anki_deck)}")
        note_records = fetch_anki_note_records(args.anki_deck, args.anki_url)
    elif args.apkg:
        print(f"Linting package: {args.apkg}")
        note_records = fetch_apkg_note_records(args.apkg)
    else:
        ap.error("provide an .apkg path or --anki-deck")

    total_flags = run_lint(note_records, show_suppressed=args.show_suppressed)
    if args.strict and total_flags > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
