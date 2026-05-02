---
name: anki-deck-author
description: Build well-designed Anki decks (.apkg files) using disciplined spaced-repetition card-design principles — atomization, linkage, basic-reversed consolidation, mobile-friendly vertical layout, italic sub-labels, examples and mnemonics in extra fields, thin-slicing for asymmetric attribution, differentiator-only cloze, and inline hint syntax. Use this skill whenever the user wants flashcards, an Anki deck, study cards, .apkg output, spaced-repetition cards, or "help me memorize / drill / study / cram X" — even if they don't say "Anki" explicitly. Also trigger when the user wants to convert source material (PDFs, slide decks, lecture notes, vocabulary lists, tables, textbook chapters) into review-able cards, or when they're prepping for an exam, certification, board, or any test. Generic flashcard-creation requests should default to this skill rather than producing ad-hoc text lists.
---

# Anki Deck Author

This skill builds Anki decks that survive long-term use. The 30 principles below have been refined through years of medical-school study and cross-domain review. They reinforce each other — apply all of them. Skipping one tends to surface as a problem only after weeks of review, when it's expensive to fix.

## How Anki actually works (mental model)

Anki review is **silent recall + self-grade**, not type-the-answer:

1. The card front appears.
2. The student decides what they think the answer is — silently in their head, or muttering.
3. They press space/enter to reveal the back.
4. They self-evaluate and grade: `1=again (wrong), 2=hard (correct but low confidence / high effort), 3=good (default correct), 4=easy`.

The student never types. This means:
- Literal answer characters like `+` (for "no prefix") are fine — nobody types them, they just confirm a mental match.
- Inline hints like `{{c1::5::#}}` are visual scaffolds for recall, not input prompts.
- The bar for "valid answer" is "did my brain produce something I'd grade as equivalent" — not "did I type the right characters."

## The ergonomics frame — single-screen, tap-tap-tap flow

Several principles below trace back to one observation: **most reviews happen on a phone, and the student wants to stay in flow.**

The ideal review session is uninterrupted tap-tap-tap — the student sits with their thumb on the grade buttons (or hand on the numpad on desktop) and grades through cards without ever touching the content. Anything that breaks that flow — horizontal layout shift, scrolling, two-finger zoom — costs concentration. Across hundreds of reviews per session, those tiny disruptions accumulate as eyestrain and review fatigue.

This gives two design constraints:

1. **Be parsimonious with horizontal space.** A line that exceeds phone width wraps; if a cloze in that line expands, the wrap point shifts and the layout jumps horizontally. Stack vertically with `<br>` between facts AND within sub-label/value pairs.

2. **Be generous with vertical space — but not generous enough to require scrolling.** Each card should fit in one phone screen and one desktop viewport. Decompose aggressively, but if a single note's content overflows the screen, split it into multiple notes rather than letting it scroll.

This upper bound matters more than the lower bound. Atomization is good until the card overflows; then it becomes friction.

## Template schema mental model

Treat the first italic label as roughly an **SQL table name** and later italic labels as columns. A good table name is abstract and reusable: `<i>vehicle:</i>`, `<i>unit:</i>`, `<i>concept:</i>`, `<i>section:</i>`. A bad table name bakes in a specific row value: `<i>HH-60M crew station:</i>` is not a schema you want; it should be normalized as:

```html
<i>vehicle:</i><br>HH-60M<br>
<i>station:</i><br>cabin<br>
<i>crew:</i><br>{{c1::crew chief}}
```

This is the practical version of reusable templates (#23) and abstract slot labels (#29). If a label contains a specific platform, unit, model, named program, person, place, or other row value, assume the schema is under-normalized until proven otherwise. Move the specific entity into the value under an abstract label, then use stable column labels for the rest of the note.

## Principles vs. drift catalog — two lenses on the same content

Two artifacts cover the design rules from different angles:

- **Principles (this file + `references/principles-detail.md`)** — *positive rules*. What to do, what to structure, what to atomize. Read these to understand the system.
- **Drift catalog (`references/common-ai-drift.md`)** — *AI-failure-mode lens*. Each entry names a recurring antipattern, explains *why AI tends to commit it*, and gives the corrective rule. Read this to inoculate against drift before authoring.

Where a principle is fundamentally an anti-pattern ("don't do X") and has a corresponding D# entry in the drift catalog, the principles list keeps a one-line **stub** — preserving the §-number for citation but deferring the deep treatment to the drift catalog. The mapping table in `common-ai-drift.md` is the cross-index.

**Numbering convention:** §1–§30 and D1–D18 are stable IDs. Append new entries; never renumber. Retired or stubbed entries stay in place with a forward-pointer.

## The 30 principles

### Atomization & coverage

1. **Atomization** — one fact per cloze deletion. Lists become per-line clozes; multi-fact prompts become multi-card notes. See `references/principles-detail.md` §1.
4. **Aggressive cloze coverage** — cloze every testable token, including small ones (digits, single letters, acronyms). Conservative clozing leaves recall on the table.
15. **Decompose compound concepts at sub-attribute level** — even when source material conjoins related facts ("horizontal, left-to-right"), split them if they're conceptually distinct. Two atoms with their own sub-labels, not one. §15.
18. **Cloze just the differentiator, not the whole token** — `S{{c1::4}}` not `{{c1::S4}}`; `{{c1::un}}framed` not `{{c1::unframed}}`. Structural common parts become the prompt; only the discriminating atom is hidden. §18.

### Linkage & consolidation

2. **Linkage** — same cloze number for repeated testable terms, AND for conceptually-paired terms (cause↔effect, anatomy↔function) when the pairing is intuitive. Don't link concepts that require external scaffolding the future-self might not retain. If the same string repeats within one note, do not mix visible and clozed occurrences: either leave every occurrence visible, or put every occurrence behind the same linked cloze. §2.
12. **Basic-and-Reversed for *test-symmetric* pairs only** — term ↔ definition, image ↔ name, language A ↔ language B. **Direction follows the test, not the data's symmetry.** If the student will encounter "see symbol → identify it" but never "name a unit → draw the symbol", use one-direction Basic, not Basic-and-Reversed. Default questions to ask: *In what context will the student need this knowledge? Will they be reading or producing?* Image-recognition tests (military symbols, anatomy, chemical structures, sheet music) are usually one-direction (image → name). Translation drills and term-definition pairs are usually bidirectional. When in doubt, ask the user. §12.
24. **Acronym-expansion as one-direction Basic** — terse front (the acronym), expansion on back. Add `<div>(domain)</div>` disambiguator when the acronym overlaps domains (e.g., `AC` = adenylyl cyclase in biochem, alternating current in physics). Use plain Basic, not reversed — you encounter expansions naturally in source material. §24.

### Layout & visual hierarchy (mobile ergonomics)

8. **Headings over sentences** — title-cased `<u>...</u>` heading at top of each cloze, not a full-sentence prompt. **Exception:** when using a reusable template (#23) and the first `<i>label:</i>` is descriptive enough on its own, the `<u>` is unnecessary — the template type name *is* the heading. Use `<u>` for one-off conceptual cards; drop it for templated cards.
9. **`<br>` instead of punctuation, both between AND within facts** — each fact (and each label/value pair) on its own line. No semicolon-separated runs. No inline `label: value` — split with `<br>`. §9.
10. **`&nbsp;` for adjacency** — non-breaking space between short adjacent tokens that should never wrap apart (`field&nbsp;N`, `air&nbsp;assault`, `2&nbsp;or&nbsp;more`).
11. **Lowercase outside headings, with acronym preservation** — text outside `<u>` headings is lowercase except: existing all-caps tokens 2+ chars (CA, MP, ENY), alphanumeric model designators (M997, HH-60), Roman numerals (II, III), and a domain-specific allow-list. The `smart_lower()` helper handles this.
14. **Italic sub-labels for grouped sub-attributes** — `<i>case:</i>`, `<i>orientation:</i>`. Italic distinguishes structural labels from testable content; bold would compete with cloze highlighting. §14.
16. **Symbols when they carry meaning** — `→` over "left to right", `↑`/`↓` over "increasing/decreasing", `≥` over "greater than or equal", `Ψ` over "psi", `@` over "located at / occurs in" (chains naturally: `endocytosis @ microfold cells @ peyer patch @ ileum`). Compact, often matches source-domain convention. Use only when the symbol is genuinely unambiguous in context. **`↑`/`↓` also serve as structural connectors** between lines in sequential/causal chains (pathway/reflex chains, vaccine schedules, treatment ladders) — each step gets its own cloze, the arrow is non-clozed scaffolding. §16.
25. **Compress jargon liberally with domain notation** — once a domain abbreviation is established (CN3, NUC, L/O, DZ, MTF), use it everywhere in cloze content. Subscripts/superscripts for ions, exponents, and indexed terms (`Ca<sup>2+</sup>`, `T<sub>X</sub>`, `5HT<sub>1B/1D</sub>`, `1°`). The `@` operator (per §16) compresses "located at" and chains for nested locations. Faster reviews = more reviews completed in a session. §25.
22. **Periods only for complete sentences** — cloze content is usually fragments and labeled values, not prose. Drop trailing periods unless you're writing an actual sentence (rare). §22.

### Examples, mnemonics, and hints (back-extra discipline)

5. **Examples in the extra field** — `e.g., radar` adjacent to a cloze leaks the answer. Move examples to a separate "extra" field that renders only on the back. §5.
   - **Corollary — front/back direction must match the test.** When the testable scenario is image → name (interpret a symbol, identify an organism, read a chart), the image goes on the FRONT and the name is the cloze answer. The verbal definition belongs in the back-extra as supporting context — not in the cloze body, where its synonyms leak the answer (e.g., "seal off enemy" in the body trivializes recall of "isolate"). When you see the pattern *definition → name* with image in extra, it's almost always inverted: flip image to front, definition to extra.
17. **Mnemonics in extra field, fully unpacked when AI-authored** — when a mnemonic exists or naturally fits, include one (`<i>mnemonic: ...</i>`). Personal mnemonics can be cryptic because the author built the chain; AI-generated mnemonics MUST spell out the cue → bridge → answer chain. Treat mnemonic generation as part of the authoring craft, not optional. **Promote to standalone Basic card** when the mnemonic itself is high-yield enough to be testable on its own (`Front: mnemonic for X` / `Back: the mnemonic`). §17.
19. **Inline hint syntax** `{{cN::answer::hint}}` — two distinct uses:
    - **Type cues** for ambiguous answer kinds (`[#]` for digit, `[↔]` for direction).
    - **Attribute-type labels** in complex multi-attribute cards (`{{c2::males::gender}}`, `{{c4::trunk::location}}`, `{{c3::yellow/white::color}}`) — the hint tells the student *which attribute they're recalling* without revealing the specific value.
    Don't use when surrounding structure already implies the type. §19.

### Anti-pattern stubs (full treatment in drift catalog)

3. **Cloze the atom, not the wrapper** — `{{c1::main icon}} and modifiers`, not `{{c1::Main Icon and Modifiers}}`. Supporting context becomes the prompt; only the atom is hidden. §3.
6. **No trivial cloze deletions** — anti-pattern stub; full treatment at **D5** in `references/common-ai-drift.md`. Corrective rule: cloze only deletions that genuinely require recall, not those answerable by elimination from adjacent context.
20. **Heading must not double as prompt** — anti-pattern stub; full treatment at **D6**. Corrective rule: pair the `<u>` heading with `<i>term:</i>` and the term beneath, so the student knows what's structural vs. testable.
21. **Compress verbose definitions; don't fall back to Basic** — anti-pattern stub; full treatment at **D7**. Corrective rule: compress the definition to 1–3 essential atoms and cloze them, rather than shipping a long paragraph as a Basic Q→A back.
26. **Most numbers don't belong inside a cloze** — anti-pattern stub; full treatment at **D3**. Corrective rule: numbers have to earn their place inside a cloze. Default fixes are reverse the direction (cloze the thing, not the number), move to the extra field, or simplify to a less-precise testable fact. Allowed in cloze only if short, doctrinally canonical, and itself the testable atom (`Role 1`, `S4`, `4 vehicles`).
27. **Don't redundantly cloze abbreviations inside other templates** — anti-pattern stub; full treatment at **D1**. Corrective rule: keep the abbreviation visible in the heading line and ship a separate Basic acronym card per §24 for the actual lookup direction.
28. **Answer leaks via derivation** — anti-pattern stub; full treatment at **D8**. Beyond synonym leaks (§5) and elimination (§6), watch for derivation leaks: arithmetic, logical complement, cardinality, or format hints. Corrective rule: before shipping, ask if a forgetful student could answer the cloze without recalling the testable knowledge. If yes, drop or rearrange the leaking element.
30. **Show acronym OR expansion, never both** — anti-pattern stub; full treatment at **D11**. Corrective rule: pick one form per card. The acronym lookup direction lives in its own one-direction Basic card per §24; every other card uses either the acronym alone or the expansion alone, never both visible together.

### Note-author craft

7. **Asymmetric 1-vs-many requires thin-slicing** — when group A has 1 attribute and group B has N attributes, "attribute → group" can't be tested in one multi-cloze note (the student would memorize cardinality, not attribution). Create dedicated single-cloze notes per attribute. §7.
13. **Stable semantic IDs for GUIDs** — each note gets a stable identifier (e.g., `frame_shape_to_identity`) used to seed its GUID via SHA1. Re-importing after edits UPDATES the existing note rather than creating a duplicate, preserving review history. Never seed GUIDs from card content. §13.
23. **Reusable templates per domain** — define a finite set of structural templates (3-7 per major content domain) and reuse them ruthlessly. A medical deck might have templates for `disease`, `drug`, `anatomical region`, `lesion`, `reflex`, `syndrome`. Each template has a fixed slot order (e.g., disease: `etiology → presentation → pathology → treatment`). The student internalizes the slot order across many cards, so cloze deletions become predictable lookups instead of structural surprises. **Massive reduction in cognitive friction** — the hardest part of card review is parsing layout; templates make layout invisible. §23.
29. **Slot labels are abstract roles, not specific values** — when a template's slot label varies per note (`<i>field surgeon:</i>` on one card, `<i>command surgeon:</i>` on the next), the slot label is acting as a value. The actual structural slot is `<i>position:</i>` and `field surgeon` is its value. First-label table-name test: `<i>vehicle:</i>` is a usable schema; `<i>HH-60M crew station:</i>` is under-normalized. Symptoms: the template doesn't generalize (every position or platform needs a custom label), and clozes are unlabeled (the student can't tell whether `{{c1::O4}}` is a rank, a section size, or something else). Lift the value out of the label so the same template works for every instance. §29.

## Workflow

### 1. Capture intent

Before drafting cards, confirm:
- **Source material** — what content is being learned? Provided directly, extractable from a PDF/slide deck, or do you need to research it?
- **Time horizon** — 3-day cram, exam in N weeks, ongoing knowledge base?
- **Scope** — comprehensive vs. high-yield only? When the user gives source material, ask what's likely to be tested vs. nice-to-know.
- **Direction(s) of testing** — symbol↔name? Term↔definition? One-way?

Use `AskUserQuestion` if anything material is ambiguous. Don't over-ask, but don't dive in blind.

**Adjacent-topic prompt:** when the user gives a source, also ask whether they want adjacent topics covered (e.g., "you sent CO 101 — want me to also cover staff sections, command relationships, etc., even though they're not in this PDF?"). Source material rarely covers everything that's testable.

### 2. Triage the content

Read the source. Identify:
- **Learning objectives — read them first.** Most slide decks state their LOs on page 1–2. They are the cleanest signal of which test directions to use, and they prevent over-coverage in directions the test won't actually require. Map LO verbs to test directions:
  - "describe / interpret / decode symbols" → **image → name** (one-direction Basic, image on FRONT, per §12 and drift #2)
  - "explain / list / identify capabilities of X" → **text-only cloze atomization**
  - "define / use vocabulary" → **term ↔ definition** Basic-and-Reversed
  - "calculate / determine quantities" → cloze with §26 numeric-allowance discipline

  **When the LOs don't mention a category, don't invent that test direction.** A deck whose source has unit-symbol illustrations on the slides but no symbol-decoding LO should not ship symbol → name cards just because the symbols are visible. Image extraction is a real cost (PDF cropping, header artifacts, media-folder bloat) that should only be paid when the LO requires it.

  Symbol-heavy decks are the exception, not the default. Most modules are text-only and the LO will reflect that. The canonical symbology exception (from this skill's originating use case, the Army CCC's CO 101 module) had an LO explicitly directing "describe military unit symbols, control measures, and tactical mission symbols" — a clear image-decoding signal that justified the image-extraction cost.

- **Domain templates** (#23) — what reusable patterns will dominate this deck? For a medical deck: disease, drug, anatomical region, syndrome. For a history deck: event, person, treaty, war. **Define 3-7 templates with fixed slot orders before drafting any cards.** This is the single highest-leverage step in deck design.
- **Clozable concepts** — multi-fact statements, lists, attribution maps, taxonomies
- **Symmetric pairs** — go in basic-and-reversed (one note, both directions)
- **Asymmetric attribution** — flag for thin-slicing per principle #7
- **Acronyms** — flag for one-direction Basic cards (#24); collect domain-specific abbreviations to use in cloze content (#25)
- **Examples** — set aside for the `extra` field, never embed in cloze body
- **Verbose definitions** — flag for compression, not fall-back to Basic
- **Mnemonic opportunities** — note where memorable hooks (alliteration, visual associations, acronyms) would help; high-yield mnemonics get standalone Basic cards (#17), others go in extra field

### 3. Draft the card manifest as data

Build a Python file (or JSON/CSV) with structured entries:

```python
CLOZE_CARDS = [
    {"id": "frame_indicates",
     "text": "<u>Frame Indicates</u><br>{{c1::standard}} {{c2::identity}}<br>{{c3::physical domain}}<br>{{c4::status}}",
     "extra": "",
     "tags": ["frame"], "src": "FM 1-02.2 Ch.1"},
]
PAIRS = [
    # basic-reversed: front, back, hint, source
    ("Field Artillery", "<img src='field_artillery.png'>", "cannonball", "p13"),
]
```

The `id` field is critical — it's the GUID seed.

### 4. Apply the principle checklist per note

The principles list above is the master checklist. The high-frequency per-note checks:

**Content shape:**
- Atomized — one fact per cloze, every testable token clozed (#1, #4, #15, #18)
- Atom not wrapper, differentiator not whole token (#3, #18)
- No trivial deletions (answerable by elimination) (#6)
- Numbers earn their place inside a cloze (#26)
- No derivation leaks — arithmetic, complement, cardinality, format hint (#28)

**Cross-cloze structure:**
- Linked across repeats and concept pairs; no mixed visible/clozed repeated strings (#2)
- Examples and mnemonics in extra field, not body (#5, #17)
- Abbreviations in heading line, not as cloze inside templates (#27)
- Show acronym OR expansion, never both (#30)

**Layout:**
- Heading present and not doubling as prompt (#8, #20)
- Vertical `<br>` between AND within facts (#9, #14)
- `&nbsp;` for tight pairs, lowercase with acronym preservation (#10, #11)
- Italic sub-labels for grouped sub-attributes (#14)
- Symbols / domain notation where they carry meaning, periods only for sentences (#16, #22, #25)
- Inline hints where ambiguous, omitted where obvious (#19)

**Format choice:**
- Compress verbose definitions, don't fall back to Basic (#21)
- Symmetric pairs as Basic-and-Reversed, not duplicate notes (#12)
- Acronym-expansion as one-direction Basic (#24)
- Asymmetric attribution thin-sliced (#7)
- Slot labels are abstract roles, not specific values (#29)
- First italic label works as a normalized SQL-table-like schema name, not a specific row value (#23, #29)

**Numbering convention:** principle numbers (§1–§30) and drift numbers (D1–D18) are stable IDs. Append new entries; never renumber. Retired entries become a one-line stub ("§17 — retired, see §X") rather than triggering a renumber across the docs and the linter.

### 5. Show a sample to the user before bulk-generating

Pick 3–5 representative notes covering different card types. The user catches convention drift faster than you will.

### 6. Self-audit: walk through the antipattern checklist

Before packaging, walk through each note against the drift catalog (`references/common-ai-drift.md`). For each card, ask:

1. Abbreviation-as-cloze inside a template? (#27)
2. Image on the back when the test direction is image → name? (#5 corollary)
3. Numbers that haven't earned their place in a cloze? (#26)
4. Multi-cloze list when thin-slicing is needed for asymmetric attribution? (#7)
5. Trivial cloze deletions (answerable by elimination)? (#6)
6. Heading-only fronts on definition cards? (#20)
7. Verbose definitions left as Basic Q→A instead of compressed cloze? (#21)
8. Answer leaks via arithmetic / logical derivation? (#28)
9. Examples adjacent to cloze answers? (#5)
10. Cluttered template slots that don't earn their place? (template fidelity)
11. Orphan label signatures that map directly to cloze values? (#29)
12. Orphan side-by-side mapping tables that should be split? (#6, #28, #29)
13. Vague/editorial labels hiding low-yield atoms? (#23)
14. Singleton templates with no sibling notes? (#23)
15. Heading plus bare cloze list that should become labeled slots? (#23)
16. Repeated strings mixed between visible text and cloze answers, or clozed under multiple unlinked ordinals? (#2)
17. Entity-specific italic labels that should be normalized into an abstract first-label/table schema? (#23, #29)

Fix flagged cards or annotate why each flag is a false positive.

Manual linter suppressions: if a warning is reviewed and accepted, tag the note with `lint-ok-d17` for a specific rule or `lint-ok-all` only for rare note-wide exceptions. Prefer rule-specific suppressions so future drift remains visible.

### 7. Fresh-agent per-note audit

For any deck above ~50 cards, **spawn a separate agent** to audit the notes cold. The author has cognitive bias toward its own design; an independent reader catches what the author rationalizes past.

**Unit of examination: per note, two lenses.** The agent walks every note in its assigned chunk and asks both questions for each:

1. **Principle compliance** — does this note follow §1–§28? (atomization, atom-not-wrapper, examples in extra, no trivial deletions, abbreviations not clozed inside templates, numbers earn their place, etc.)
2. **Leak check** — *if a forgetful student saw this card for the first time, could they answer the cloze WITHOUT recalling the testable knowledge?*

The agent processes all notes in its chunk in **one session** so it has cross-card visibility — many leaks (cardinality cheats, synonyms across related cards) are only detectable by seeing related cards together.

Watch specifically for:
- **Principle violations** caught by §1–§28
- **Synonym/paraphrase leaks** — the visible body mirrors the answer (e.g., "seal off enemy" leaks "isolate")
- **Arithmetic/logical derivation** — visible totals leak multiplicands; complements leak each other
- **Cardinality cheats** — a stated count + N–1 visible items leave one obvious gap
- **Domain-context leaks** — the heading, tags, or extra trivialize recall
- **Format/shape cues** — placeholder length or `[#]` hint over-constrains the answer

Report flagged notes with the offending principle / leak mechanism. **Don't fix — flag and report.** Fixing belongs in a separate pass once the user has reviewed the flag list.

#### Chunk sizing

The unit of work is the **note**, not the card or the sub-deck. A note with N cloze deletions produces N cards but they share the same body text — the agent must see all N together.

**Sweet spot: 30–50 notes per agent**, grouped by template family when possible (all sectors, all CN nerves, all hospital aug dets).

- **Hard floor: never split a note.** A 7-cloze note goes intact to one agent.
- **Below ~30 notes per agent:** spawn overhead (loading SKILL.md, principles, getting started) dominates the actual scrutiny. Wasteful.
- **Sweet spot 30–50:** per-note attention stays sharp; one chunk easily covers a template family, where most cross-note leaks live (cardinality cheats across "sector 1 / sector 2 / sector 3" cards, synonyms across related disease/drug cards).
- **Above ~50:** per-note attention degrades faster than cross-note leak detection improves. The marginal cross-note value isn't worth the attention cost.
- **Cross-chunk leaks** (a card in chunk A leaks the answer to a card in chunk B): caught by a final consolidation pass over the flag list, not by giving each agent a bigger chunk.

**Rationale: most flags are intra-note.** The ICWAD `= 60 total` arithmetic leak (see `references/principles-detail.md` §28) was visible from one note alone — no cross-card context needed to catch it. The same holds for most principle violations (atomization, atom-not-wrapper, examples in body, abbreviation as cloze inside template). Cross-note leaks are real but rarer and concentrate inside template families, which fit comfortably in one 30–50 note chunk.

#### Scaling table

| Deck size       | Pattern                                                                                                  |
|-----------------|----------------------------------------------------------------------------------------------------------|
| ≤50 notes       | Skip — author self-audit (step 6) is enough.                                                             |
| 50–100 notes    | One fresh agent for the whole deck (chunk-of-one).                                                       |
| 100+ notes      | Parallel agents, ~30–50 notes each, grouped by template family (per `references/workflows.md` Pattern 2). |
| Multi-chunk     | After per-chunk flags are consolidated, run a final cross-cutting pass on the flag list to catch leaks that span chunks. |

Why fresh and not self-audit: the author thinks the card is good (else they wouldn't have shipped it). Fresh eyes catch the subtle leaks and principle violations the author rationalizes.

### 8. Build the .apkg

Use `scripts/build_deck.py` — pre-configured Cloze, Basic, and Basic-Reversed models with the right CSS, stable-GUID seeding, and `smart_lower()`. See its docstring for the API.

### 9. Verify

`scripts/verify_deck.py path/to/deck.apkg` — checks note counts, model assignments, media references, and prints sample notes per model. See `references/verification.md` for what to look for.

### 10. Deliver

Save the .apkg where the user can access it. Surface a `computer://` link. One-line summary of note counts per sub-deck.

## Common pitfalls

- **Random GUIDs** (genanki's default) — re-importing after edits creates duplicates and strands review history. Always use `stable_guid()` with a semantic seed (#13).
- **Forgetting `model_type=genanki.Model.CLOZE`** — without it, cloze deletions render literally as `{{c1::xxx}}`.
- **Putting `e.g., ...` in the cloze body** — leaks adjacent answers (#5).
- **Two basic notes for one symmetric pair** — use Basic-and-Reversed (#12). Editing two drifts; one doesn't.
- **Not thin-slicing asymmetric attribution** — "mobility belongs to sector ?" can't be tested if the same note also lists size, range, altitude (#7).
- **Verbose definitions left as Basic** — compress and atomize via cloze instead (#21). Falling back to Basic is laziness.
- **Heading-only cards** — `<u>Term</u>` alone is ambiguous. Pair with `<i>term:</i>` + value (#20).
- **Headings or labels in title case body** — only `<u>` headings are title case; everything else is lowercase + acronym preservation (#11).
- **Inline `label: value`** — split with `<br>` (#9).
- **Cryptic AI-generated mnemonics** — the user didn't build the chain, so unpack it (#17).

## References

- `references/principles-detail.md` — full before/after example for each principle
- `references/common-ai-drift.md` — **READ BEFORE AUTHORING.** Catalog of recurring drift patterns AI agents commit even when the principles forbidding them are documented. Each entry names the pattern, explains why AI tends to commit it, and gives the corrective rule. Use during the self-audit step.
- `references/verification.md` — what to check programmatically before shipping
- `references/workflows.md` — patterns for larger operations: parallel agents for multi-deck authoring, parallel agents for QC passes, AnkiConnect bridge for live in-place patches and cleanup (direct via bash+Python preferred; Chrome MCP fallback for sandboxed harnesses). **Read this when:** authoring ≥3 decks at once, the deck collection is too large for one model to QC end-to-end, or the user wants in-place patches without the export/import dance.
- `scripts/build_deck.py` — reusable infrastructure (models, CSS, helpers)
- `scripts/verify_deck.py` — verification helper
- `scripts/lint_deck.py` — antipattern linter; run on a built .apkg to flag drift-catalog matches before delivery

## Dependencies

```
pip install --break-system-packages genanki Pillow PyMuPDF
```

`genanki` for deck assembly. `Pillow`/`PyMuPDF` only if extracting/cropping images from source PDFs.
