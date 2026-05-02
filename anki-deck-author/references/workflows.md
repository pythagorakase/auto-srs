# Workflows for Larger Deck Operations

Patterns developed for authoring, QC, and maintaining decks that span multiple source documents or hundreds of cards. Read this when:

- The user has multiple slide decks / source PDFs to convert in one pass
- Card counts exceed a few hundred and your context can't reason about every card
- The user has imported a deck and wants in-place patches to live notes
- A previous import created a "Patch" deck instead of updating cleanly

Each pattern explains *when* to reach for it and the *gotcha* that surfaced when we worked through it for the first time.

## Pattern 1 — Parallel agents for multi-deck authoring

**When:** the user provides ≥3 source documents (e.g., separate course modules) and wants a deck per document.

**Why parallel:** authoring a 60-card deck requires reading the source PDF, identifying templates, drafting cards, and packaging — roughly 3–10 minutes of work. Done sequentially, four decks take 30+ minutes; in parallel they take ~10.

**How:**

1. Build the first deck yourself, end-to-end. This validates the source-material pipeline (PDF rendering, card patterns, .apkg packaging) and gives the agents a concrete reference build script to adapt.
2. Spawn one agent per remaining source document, all in the same turn. Each agent prompt should contain:
   - Path to its source PDF (bash sandbox path)
   - Path to SKILL.md and principles-detail.md (must read first)
   - Path to your reference build script (concrete example)
   - Output destination (consistent naming: `CCC - {CODE}.apkg` or similar)
   - Internal deck-naming convention for tree nesting (`CCC::{CODE}::{SubDeck}`)
   - Card budget and any dropped-content rules
3. Keep prompts self-contained — the agent has no memory of your conversation.

**Gotcha — agent drift on conventions:** even with the skill loaded, agents will sometimes drift from specific conventions (e.g., they'll author abbreviation-as-cloze patterns despite #24). Plan for a QC pass after parallel authoring; don't ship without one. (See Pattern 2.)

**Gotcha — naming/file consistency:** agents will pick reasonable but inconsistent file names if you don't specify. Always tell each agent the exact output filename and the exact deck-name string for tree nesting.

## Pattern 2 — Parallel agents for QC passes

**When:** the deck collection has grown beyond what fits in one model context (typically >150 notes), or you suspect agent drift after an authoring round, or the user has manually edited and you want to verify against current conventions.

**Why parallel:** scrutinizing every card against a multi-point checklist is mechanical but slow. Splitting by sub-deck (or by source module) lets six agents check 50–100 notes each in parallel.

**How:**

1. Decide on a checklist of antipatterns to look for. The 8-point list we used:
   1. Numbers that haven't earned their place inside a cloze
   2. Abbreviation-as-cloze inside template
   3. Cryptic placeholders (undefined symbols/labels)
   4. Trivial cloze deletions (answerable by elimination)
   5. Heading-doubling-as-prompt
   6. Linkage presuming external knowledge
   7. Reverse-direction nonsense
   8. Lists that should be thin-sliced
2. Spawn one agent per sub-deck or per source module. Each agent reads SKILL.md + principles-detail.md, scrutinizes its assigned notes, and emits a JSON file with flagged notes (GUID, content, antipattern numbers, proposed fix).
3. Consolidate the JSON files. Group findings by severity. Present to the user with proposed fix scope before authoring patches.
4. **Spawn a second round of parallel agents to author the actual patches** based on the QC findings. Each agent reads its QC json + skill, then writes out a Python data file with `PATCHES`, `NEW_ACRONYMS`, `NEW_NOTES`, `DELETE_GUIDS` lists. You consolidate into one build script.

**Gotcha — false positives:** agents flag aggressively. A 5–15% false-positive rate is normal. The user can dismiss noise faster than you can find true positives, so let agents over-flag.

**Gotcha — patches must use the existing model_id:** for in-place updates to work, the patch's note must use the same GUID *and* the same `model_id` as the existing note. Define `genanki.Model` objects with the existing model IDs (extracted from the user's collection) — Anki recognizes them by ID.

## Pattern 3 — Patch deck for in-place updates

**When:** the user has imported a deck and reviewed/edited it; you need to fix some notes without losing their review history.

**The right approach:**

- Build a separate `.apkg` (the "patch deck") containing only the notes you want to change.
- Each patched note uses the **exact same GUID** as the existing note in the user's collection. Extract GUIDs from the user's exported `.apkg` (or via AnkiConnect, see Pattern 4).
- Each patched note uses the **exact same `model_id`** as the existing note.
- Anki's import logic: same-GUID notes are matched to existing notes; the existing note's content is replaced with the imported note's content.

**Critical gotcha — increased cloze count creates new cards in the import deck:**

When you patch a cloze note from N to M deletions where M > N (e.g., atomizing a list cloze):
- The note's content updates in place ✓
- The original card (`ord 0`) stays in its existing deck ✓
- **New cards (`ord 1`, `ord 2`, ..., `ord M-1`) are created in the IMPORT deck**, not the original deck

So if you ship a patch that increases cloze deletion counts, the user will see:
- Their original deck looking *almost* right (missing the new cards)
- A populated patch deck full of the new cards that should have gone to the original deck

This is what happened to us in CCC patch v2: 113 cards landed in `CCC::Patch v2` deck because many patches atomized lists from 1 cloze to 4–5.

**The fix is post-import card relocation** — see Pattern 4.

**Other gotchas:**

- The user's hand-authored notes use a different `notetype` than yours (in our case the vanilla `Cloze`). Don't include those notes in patches; respect the boundary. Always check the model_id before patching.
- Bumping the model_id while keeping the same GUID creates duplicates. Anki considers `(GUID, model_id)` together for matching — different model_id, same GUID = different note from Anki's view.
- If you really need to migrate a note across models, ship a delete-by-GUID instruction alongside a fresh-GUID replacement.

## Pattern 4 — AnkiConnect bridge for live cleanup

**When:** you need to read or modify the user's live Anki collection without the export/import dance — diagnostics, post-import cleanup, batch deletions, deck moves, in-place patches to live notes.

**Prerequisite:** the user has the **AnkiConnect** add-on installed in their Anki (code 2055492159) and Anki is running.

### Transport: pick the right one for your environment

There are two ways to talk to AnkiConnect. **Try direct first.** Only fall back to the Chrome bridge when the direct path fails because of network isolation.

#### Option A (default) — Direct via bash + Python

Works whenever your bash environment shares the network namespace with the user's machine — i.e., **Claude Code running locally on the user's machine** (the common case). `localhost:8765` is reachable from the bash sandbox; just POST JSON-RPC.

```python
import json, urllib.request
def call(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    req = urllib.request.Request("http://localhost:8765", data=payload)
    resp = json.load(urllib.request.urlopen(req, timeout=10))
    if resp.get("error"):
        raise RuntimeError(f"{action}: {resp['error']}")
    return resp["result"]

# Examples:
call("version")                                          # sanity check
call("deckNames")                                        # list all decks
call("findNotes", query='deck:"CCC::CO 101"')            # search
call("notesInfo", notes=[1234, 5678])                    # fetch full data
call("updateNoteFields", note={"id": 1234, "fields": {"Front": "..."}})
call("addNote", note={"deckName": "...", "modelName": "...", "fields": {...}})
call("storeMediaFile", filename="x.png", data=b64data)   # data is base64
call("changeDeck", cards=[1, 2], deck="X")
call("deleteNotes", notes=[1234])
call("deleteDecks", decks=["X"], cardsToo=True)
```

Default CORS allowlist includes `http://localhost` so this works out of the box. No extra config needed.

#### Option B (fallback) — Chrome MCP bridge

Use this **only when bash can't reach localhost** — typically because you're running in a sandboxed environment like Claude Cowork, where the bash sandbox is network-isolated from the user's machine. The bridge makes the request from the user's actual browser to their actual localhost.

Setup:
1. The user has the **Claude in Chrome** extension and has connected their browser to your session.
2. AnkiConnect's `webCorsOriginList` includes `"http://localhost:8765"` (with port — the default `"http://localhost"` won't match because port disambiguation matters for CORS).

Call shape via `mcp__claude-in-chrome__javascript_tool`:
```javascript
fetch('http://localhost:8765', {
  method: 'POST',
  body: JSON.stringify({action: 'findNotes', version: 6, params: {query: 'deck:"X"'}})
}).then(r => r.json()).then(j => j.result)
```

**Heuristic for picking transport:** if you can run `python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8765', timeout=2)"` successfully via bash, use Option A. If it fails with a connection error AND the user is in a sandboxed harness, fall back to Option B.

### Gotchas (apply to both transports)

**AnkiConnect doesn't expose GUIDs:** `notesInfo` returns note ID, model name, fields, tags, cards — but no GUID. Anki's search syntax also doesn't support `guid:`. To map GUID → note ID, read the user's `collection.anki2` SQLite directly (from a recent `.apkg` export they made) and run a query joining on GUID. Pass the resulting note IDs to AnkiConnect.

**Chrome bridge only — fetch responses with sensitive-looking strings get blocked:** if a JS expression via Chrome MCP returns a string containing many random-looking GUIDs or credentials-shaped tokens (or even plain ASCII strings like `XXXXX` that pattern-match cookie shapes), Claude's response reader may flag it as potential leaked data and return `[BLOCKED: Cookie/query string data]`. This does not affect Option A. Workaround for Option B: aggregate or summarize before returning (counts, model names, hashes).

## Pattern 4b — Fixing botched image crops in place

**When:** an image extracted from a source PDF is wrong (off-by-one row, captured the wrong cell, includes header artifacts) and the user has already imported the deck.

**The mechanism:** notes reference media files by filename (e.g., `<img src="p56__Medical_Role_1.png">`). Anki's media folder is per-profile. If you overwrite the file at the same name, the notes pick up the new content automatically — no note edits, no GUID changes, no review history disruption.

**How:**
1. Re-extract the icon with corrected coordinates. Save with the same filename as the existing media file.
2. Use AnkiConnect's `storeMediaFile` action with `path` parameter pointing to the corrected file on disk and `deleteExisting: true`. This avoids base64-encoding overhead:
   ```javascript
   await call('storeMediaFile', {
     filename: 'p56__Medical_Role_1.png',
     path: '/absolute/path/to/corrected/p56__Medical_Role_1.png',
     deleteExisting: true,
   });
   ```
3. The next time the user flips to a card referencing that image, Anki renders the updated content.

**Common cause: line detection merging header into first data row.** Tabular slides where the divider between the purple/colored header and the first data row is absent or thinly drawn will be detected as one block. The extraction code that maps `idx 0` to the first detected block then crops the wrong cell. The fix is row-coordinate adjustment in the extraction script — bump the y1 of the first data row past the header explicitly. Always verify a sample crop visually before running bulk extraction.

## Pattern 5 — Surfacing the live collection state

**When:** you want a snapshot of card counts, deck structure, or note distribution to inform a decision.

**How:** use AnkiConnect's `findCards` / `findNotes` with deck-filter queries. Aggregate counts client-side:

```javascript
const decks = await call('deckNames');
for (const d of decks.filter(d => d.startsWith('CCC'))) {
  const cards = await call('findCards', {query: `deck:"${d}"`});
  console.log(`${d}: ${cards.length}`);
}
```

If you need GUIDs (e.g., to compare against a patch list), have the user re-export `.apkg` and read it from `/Users/pythagor/CCC/CCC.apkg` via the bash sandbox. Map `(GUID → note ID)` in Python, then drive deletions through AnkiConnect with the resolved note IDs.

## When NOT to use these patterns

- Small decks (<60 cards): hand-author end-to-end. Parallel agents have coordination overhead that isn't worth it.
- One-off conversational fixes: just ship a corrected `.apkg` directly.
- Agent drift on a tiny deck: re-author yourself faster than QC pass + patch round.
- The user hasn't installed AnkiConnect: fall back to script-and-paste (write a Python script to `/Users/pythagor/CCC/`, ask user to run it, paste output). The Chrome MCP bridge is also unavailable without the extension; script-and-paste covers both gaps.
