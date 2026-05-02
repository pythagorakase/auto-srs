# Verifying the .apkg before delivery

A .apkg is just a zip file containing a SQLite database (`collection.anki2` or `collection.anki21`), a `media` JSON manifest, and numbered media files. Every deck shipped should pass these checks.

## Run the verifier

```bash
python scripts/verify_deck.py path/to/deck.apkg
```

This prints note counts, card counts, model summary, deck list, sample notes from each model, and missing-media check.

## What to look for

### Note and card counts
- Note count should match the manifest you built from
- Card count varies by model:
  - Basic: 1 card per note
  - Basic-and-Reversed: 2 cards per note
  - Cloze: 1 card per cloze deletion (so a note with `{{c1::}}, {{c2::}}, {{c3::}}` produces 3 cards)

### Models registered correctly
Three models should appear:
- `*Basic*` with fields `Front, Back, Source`
- `*Basic (and reversed)*` with two templates (Card 1 and Card 2)
- `*Cloze*` with `model_type=1` (cloze model type), and a field for `Extra` if examples are used

If the cloze model is missing `model_type=1`, cloze deletions render literally — `{{c1::xxx}}` shows as text instead of being hidden.

### Sub-deck names
Decks should nest under a single root (e.g., `Topic::Sub-deck 1`, `Topic::Sub-deck 2`). Verify the nesting renders correctly in Anki — no orphaned decks.

### Media references match files
Every `<img src="X.png">` in note text should have a corresponding entry in the `media` manifest, and the file should be present in the package.

```python
referenced = set()  # parse <img src="..."> from notes
media_files = set(json.load(open("media")).values())
missing = referenced - media_files
assert not missing, f"Missing media: {missing}"
```

### Sample render
Open the .apkg in Anki desktop and review 3–5 cards from each sub-deck. Look for:
- Cloze deletions render as `[...]` placeholders, not literal `{{c1::...}}`
- `<u>` headings render underlined
- `<br>` produces line breaks
- `&nbsp;` keeps adjacent tokens together
- Acronyms preserved as uppercase per principle #11
- Examples (extra field) appear only on the back, after the answer

## Common bugs caught by verification

| Symptom | Likely cause |
|---------|--------------|
| Cloze cards render `{{c1::xxx}}` literally | `model_type=genanki.Model.CLOZE` missing |
| 2× notes after re-import | GUIDs are random or content-seeded; not stable |
| Cards show empty answer | Cloze numbering skipped (e.g., `{{c1}}` and `{{c3}}` but no `{{c2}}`) — actually fine in Anki, but verify intentional |
| Image broken (?) icon | File missing from media manifest |
| Sub-decks flat instead of nested | Deck name uses single colon `:` instead of `::` |
