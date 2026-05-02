# Principles in Detail — Before/After Examples

Each principle includes a real-world failure mode plus a corrected version. Read this when designing cards, especially before drafting cloze content for the first time in a deck.

**Anki UX reminder:** the student doesn't type answers. They read the front, recall mentally, press space to reveal the back, then self-grade 1–4. This means literal characters like `+` (for "no prefix") work fine as cloze answers — nobody types them, they just signal mental classification matches.

**Single-screen rule:** every card must fit in one phone screen / desktop viewport without scrolling. Atomize aggressively, but if a note overflows, split it into multiple notes.

## §1 — Atomization: one fact per cloze deletion

**Failure mode:** A single card asks for multiple facts at once, so the student either gets it all right (cheap pass) or all wrong (no partial credit toward retention).

**Bad:**
```
The frame of a symbol indicates which three things?
→ Standard identity, physical domain, and status
```

**Good** (one note → 3 cards):
```
<u>Frame Indicates</u><br>
{{c1::standard identity}}<br>
{{c2::physical domain}}<br>
{{c3::status}}
```

Now one card review tests one atom. Each gets its own review schedule via spaced repetition.

---

## §2 — Linkage: same cloze number for repeated and concept-paired terms

**Two distinct uses, both important:**

### Use 1 — Repeated terms

A term appearing 3× in the same note becomes 3 separate clozes (`{{c1::black}}`, `{{c2::black}}`, `{{c3::black}}`). Each is reviewed independently — the student doesn't develop the unified mental concept "black is the universal fallback color."

**Bad:**
```
hostile = red or {{c2::black}} with ENY ...<br>
obstacle = green or {{c3::black}} if green unavailable
```

**Good:**
```
<u>Control Measure Colors</u><br>
friendly = {{c1::black}} or {{c5::blue}}<br>
hostile = {{c2::red}} or {{c1::black}} with "{{c6::ENY}}" in field {{c8::N}} if {{c2::red}} unavailable<br>
obstacle = {{c3::green}} or {{c1::black}} if {{c3::green}} unavailable<br>
CBRN = {{c4::yellow}}
```

`{{c1::black}}` appears 3× — all three reveal together when the c1 card is reviewed. The student must recall "black" as one concept across all its contexts.

### Use 2 — Concept-paired terms (cause↔effect, anatomy↔function)

Same cloze number can also link **conceptually-paired terms** that aren't the same word. Example from a cranial-nerve lesion card:

```
impairment:    {{c2::SCM}}; {{c3::trapezius}}
presentation:  {{c2::head weak turning}} away; {{c5::ipsi}}lateral {{c3::shoulder drop}}
```

`c2` links the muscle (SCM) to its functional consequence (head weak turning). `c3` links trapezius to shoulder drop. Hiding c2 hides BOTH the muscle and its presentation — the student must recall the cause/effect pair as one unit.

**Caveat:** only link concepts where the pairing is intuitive or part of the testable knowledge itself. If the linkage requires external scaffolding (anatomical knowledge, linguistic etymology) that the future-self might not retain, the link silently breaks. Future-you re-encountering "head weak turning" without retained anatomical knowledge gets a 50/50 muscle guess and learns nothing. Test linkage by imagining the card in 5 years: does the pairing still feel natural without other knowledge?

### Use 2 (extended) — cross-slot threading

The cause↔effect pairing above sits within one slot or row. The same mechanism scales to threading **a single concept across multiple template slots** — where one cloze number reveals the same atom (or a tightly-coupled atom) in two or three different positions on the card.

Real example (Note 1510458517823, DAF deficiency / paroxysmal nocturnal hemoglobinuria):

```
<i>disease:</i> {{c1::DAF deficiency}}
<i>pathology:</i> {{c3::complement}} lysis @ {{c2::erythrocytes}}
<i>presentation:</i> {{c4::paroxysmal nocturnal}} {{c2::hemoglobin}}{{c4::uria}}
```

- `c2` threads `erythrocytes` (in the pathology slot) with `hemoglobin` (in the presentation slot) — the same red-cell-derived molecule revealed under one card. The student recalls the unified concept "intravascular hemolysis releases Hb" rather than two disconnected facts.
- `c4` threads `paroxysmal nocturnal` (the timing modifier) with the `–uria` suffix — splitting a compound word morphologically while still binding the morphologically-related fragments.

When the c2 card comes up for review, both `erythrocytes` and `hemoglobin` reveal together. The pathology and presentation aren't drilled as separate facts — they're drilled as one downstream consequence of complement attack.

**When to use cross-slot threading:** when a single domain concept (a molecule, a structure, a mechanism) genuinely shows up in multiple template slots and the testable knowledge IS that unification. Don't thread merely co-occurring terms — that re-creates the §2 caveat about external scaffolding.

---

## §3 — Cloze the atom, not the wrapper

**Failure mode:** Wrapping too much inside the cloze means the student has to recall multiple things, defeating atomization (#1) and preventing linkage (#2).

**Bad:**
```
A = {{c1::Main Icon and Modifiers}}
```

**Good:**
```
A = {{c1::main icon}} and modifiers
```

The supporting context ("and modifiers") becomes part of the prompt. Only the testable atom ("main icon") is hidden.

---

## §4 — Aggressive cloze coverage

**Failure mode:** Conservative clozing — only the "main answer" is hidden — wastes the format. Every testable token is a separate atom.

**Bad** (conservative):
```
F = {{c1::attached/detached}} (+ reinforced, − reduced)
```

**Good** (every testable token):
```
F = {{c1::attached}}/{{c2::detached}}<br>
{{c3::+}} = reinforced<br>
{{c4::−}} = reduced
```

Even single characters get their own cloze if they're testable.

---

## §5 — Examples belong in an "extra" field

**Failure mode:** `e.g., radar` next to `{{c1::capability}}` leaks the answer. A knowledgeable student knows radar is a capability and decodes the cloze without recall.

**Bad:**
```
sector {{c1::1}} = {{c2::capability}} (e.g., radar)
```

**Good** (cloze body):
```
sector {{c1::1}} = {{c2::capability}}
```

**Plus** an `extra` field: `e.g., radar` (rendered only on the back of the card, after the answer is revealed).

The card model needs an Extra field. See `scripts/build_deck.py` for how to wire it.

---

## §6 — Avoid trivial cloze deletions

*Anti-pattern stub. Full treatment with worked example at **D5** in `references/common-ai-drift.md`.*

Cloze deletions that can be answered by elimination teach nothing. The student sees `sector [...] = capability` next to `sector [...] = mobility` and answers "1" by eliminating "2" — not by recalling the attribution. Corrective rule: cloze only deletions that genuinely require recall.

---

## §7 — Asymmetric 1-vs-many requires thin-slicing

**Failure mode:** When group A has 1 child and group B has N children, "child → group" can't be tested in one multi-cloze note. The student would just memorize cardinality.

Consider Field A modifier sectors:
- Sector 1: capability (1 child)
- Sector 2: mobility, size, range, altitude (4 children)

**Naive (broken) approach:**
```
sector {{c1::1}} = capability<br>
sector {{c2::2}} = mobility / size / range / altitude
```

When `c2` is hidden, the student sees "sector [...] = mobility / size / range / altitude" — and answers "2" because there are 4 things and only sector 2 has multiple things. The student didn't recall the attribution; they deduced from cardinality.

**Correct (thin-sliced) approach:**

```
Note 1: <u>Field A Modifiers</u><br>sector {{c1::1}} = {{c2::capability}}
Note 2: <u>Field A Modifiers</u><br>sector 2 = {{c1::mobility}} / {{c2::size}} / {{c3::range}} / {{c4::altitude}}
Note 3: <u>Field A Modifiers</u><br>sector {{c1::2}} = mobility
Note 4: <u>Field A Modifiers</u><br>sector {{c1::2}} = size
Note 5: <u>Field A Modifiers</u><br>sector {{c1::2}} = range
Note 6: <u>Field A Modifiers</u><br>sector {{c1::2}} = altitude
```

Notes 3–6 force the student to recall "this attribute belongs to sector 2" without context cheating. Each is a single-cloze note with no other attributes visible.

**This is aggressive.** Use judgment: if "altitude → sector 2" is genuinely high-yield (e.g., on a test), thin-slice. If it's nice-to-know, you can collapse Notes 3–6 into Note 2's cloze structure (where the student sees the other attributes as distractors).

---

## §8 — Headings over sentences

**Failure mode:** Full-sentence prompts are wordy, look bad on mobile, and force the eye to read past structure to get to the testable content.

**Bad:**
```
The composition of a unit symbol contains the following four fields A through D:
- Field A: main icon and modifiers
- Field B: echelon
- ...
```

**Good:**
```
<u>Composition Fields A–D</u><br>A = {{c1::main icon}} and modifiers<br>B = {{c2::echelon}}<br>C = {{c3::quantity}}<br>D = {{c4::task organization}}
```

Use `<u>` for the heading (renders as underlined; works in every Anki client). Title case for the heading; lowercase for the body (see §11).

### Exception: templated cards drop `<u>` entirely

When using a reusable template (#23), the first `<i>label:</i>` IS the heading equivalent — no `<u>` needed. The template-type name carries the topic.

```
<i>disease:</i> alzheimer
<i>pathology:</i> {{c1::atrophy}} @ {{c2::cortex}} + {{c3::hippocampus}}
<i>labs:</i> {{c4::ApoE4}}; {{c5::APP}}
```

The student sees `disease: alzheimer` at the top and immediately knows what kind of card this is, what slots will follow, and what kind of recall is being asked. Adding `<u>Disease</u>` above would be redundant.

**Rule of thumb:** `<u>` for one-off conceptual cards (foundational concepts, frame shapes, composition fields). Drop it for templated cards (medical disease, drug, anatomical region). The first `<i>label:</i>` does the work.

---

## §9 — `<br>` instead of punctuation separators

**Failure mode:** Comma- or semicolon-separated lists force horizontal scanning. When a cloze in the middle expands, the line jumps — disorienting on mobile.

**Bad:**
```
{{c1::points}}, {{c2::lines}}, and {{c3::areas}}
```

**Good:**
```
{{c1::points}}<br>
{{c2::lines}}<br>
{{c3::areas}}
```

Each fact gets its own line. Cloze expansion only affects that line's vertical position, not horizontal layout.

---

## §10 — `&nbsp;` for adjacency

**Failure mode:** Short adjacent tokens that should never wrap apart get split across lines on narrow viewports.

**Cases to fix:**
- `field N` → `field&nbsp;N` (keeps "field" with the field letter)
- `air assault` → `air&nbsp;assault` (keeps adjective+noun together)
- `2 or more` → `2&nbsp;or&nbsp;more` (numeric phrase intact)
- `sector 1` → `sector&nbsp;1`

Use sparingly, only where wrapping would obscure meaning or look wrong.

---

## §11 — Lowercase outside headings, with acronym preservation

**Failure mode:** Doctrine-style title case everywhere ("Main Icon and Modifiers") looks shouty and fights the heading hierarchy.

**Rule:** Lowercase everywhere outside `<u>...</u>` headings, EXCEPT:
- Existing all-caps tokens of 2+ chars (CA, MP, ENY, EUCOM, MEDEVAC)
- Alphanumeric model designators (M997, HH-60, F-35)
- Roman numerals (II, III, IV)
- Domain-specific allow-list (e.g., USS, FBI, NATO)

**Good examples:**
- `Field Artillery` → `field artillery`
- `Civil Affairs (CA)` → `civil affairs (CA)` (acronym preserved)
- `Wheeled Ambulance (M997)` → `wheeled ambulance (M997)` (model number preserved)
- `Battalion / Squadron` → `battalion / squadron`

The `smart_lower()` helper in `scripts/build_deck.py` automates this.

---

## §12 — Consolidate symmetric pairs via Basic-and-Reversed

**Failure mode:** Two separate notes for term→definition and definition→term means edits drift apart and you can't reorganize them as a unit.

**Bad** (two separate basic notes):
```
Note A: front="Field Artillery", back="<img src='fa.png'>"
Note B: front="<img src='fa.png'>", back="Field Artillery"
```

**Good** (one Basic-and-Reversed note):
```
Note: front="<img src='fa.png'>", back="field artillery"
→ Generates 2 cards: front→back and back→front, automatically.
```

When you fix a typo on the back, both cards update. When you reorganize the deck, you move one note, not two.

In genanki:
```python
MODEL_BASIC_REVERSED = genanki.Model(
    model_id,
    "Basic (and reversed)",
    fields=[{"name": "Front"}, {"name": "Back"}, ...],
    templates=[
        {"name": "Card 1", "qfmt": "{{Front}}", "afmt": "..."},
        {"name": "Card 2 (reversed)", "qfmt": "{{Back}}", "afmt": "..."},
    ],
)
```

---

## §13 — Stable semantic IDs for GUIDs

**Failure mode:** Random GUIDs (genanki's default) mean re-importing after edits creates duplicate notes and strands review history.

**Rule:** Each note gets a stable identifier (lowercase_snake_case, semantic) used as the GUID seed. Hash via SHA1 to fit Anki's GUID format.

```python
def stable_guid(*parts):
    h = hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()
    return genanki.guid_for(h[:16])

# When adding a note:
note = genanki.Note(
    model=MODEL_CLOZE,
    fields=[text, extra, source],
    guid=stable_guid("cloze", "fundamentals", "frame_indicates"),
)
```

The seed must be **content-independent** — derive it from the note's identity (what concept it tests), not from its current text. When you edit "frame indicates 3 things" to "frame indicates four things", the GUID stays the same, so Anki updates the existing note in place.

If you absolutely must rename the seed (e.g., the concept reorganizes), accept that you'll get a duplicate on next import and clean it up once.

---

## §14 — Italic sub-labels for grouped sub-attributes

**Failure mode:** When a card has multiple sub-attributes nested under a heading, no visual hierarchy means structural labels and testable atoms blur together.

**Bad:**
```
<u>Control Measure Labeling</u><br>
case: {{c1::uppercase}}<br>
orientation: {{c2::horizontal}}, {{c3::left to right}}
```

**Good:**
```
<u>Control Measure Labeling</u><br>
<i>case:</i><br>
{{c1::uppercase}}<br>
<i>orientation:</i><br>
{{c2::horizontal}}<br>
<i>direction:</i><br>
{{c3::→}}
```

Italic distinguishes structural labels from testable content (which gets cloze styling). Don't use bold — it competes with cloze highlighting.

The italic span can wrap a single short label-value pair inline (`<i>mnemonic: box truck</i>`) when there's only one fact and vertical layout would be overkill. Otherwise, use the vertical pattern (label on one line, value on the next).

---

## §15 — Decompose compound concepts at the sub-attribute level

**Failure mode:** Source material conjoins related-but-distinct facts ("horizontal, left-to-right"), and the cloze inherits that grouping. The student then learns the conjunction as one fact instead of two atoms.

In the example above, "horizontal, left-to-right" is actually two attributes:
- **orientation**: horizontal vs. vertical
- **direction**: LTR vs. RTL

Each gets its own italic sub-label and atom. This is principle §1 (atomization) applied one structural level up — atomize not just at the cloze level, but at the sub-attribute framing too.

---

## §16 — Symbols when they carry the meaning

**Failure mode:** Spelled-out phrases for concepts that have established symbolic notation take more horizontal space and don't match the source domain's conventions.

**Use the symbol:**
- `→` instead of "left to right" or "leads to"
- `↑`/`↓` instead of "increasing/decreasing"
- `≥` instead of "greater than or equal to"
- `Ψ` instead of "psi"
- `±` instead of "plus or minus"
- `@` instead of "at / located at / occurs in"

**Don't use the symbol when:**
- It's domain-ambiguous (`+` could mean "and", "reinforced", "plus", "positive" depending on context)
- The student's source material consistently spells it out

In the principle §14 example, `{{c3::→::&harr;}}` uses both: the answer is the symbol `→`, and the inline hint `&harr;` (↔, the bidirectional arrow) clues the student that they're recalling a directional symbol without revealing which direction.

### `@` as a locative operator

`@` is a single-character preposition for "at / located at / occurs in." It chains naturally for nested locations and compresses what would otherwise be wordy spatial prose. Real example (Note 1545595247614, shigellosis):

```
<i>disease:</i><br>
shigellosis<br>
<i>pathology:</i><br>
{{c3::endocytosis}}<br>
@<br>
{{c1::microfold}} cells<br>
@<br>
{{c2::peyer patch}}<br>
@<br>
{{c4::ileum}}
```

Four atomized facts (process, target cell, structure, organ) connected by a vertical `@` chain. Each location is independently testable; the `@` glyph alone does the work of "→ in → in → in." Compresses to about half the horizontal width of the prose form.

### `↑` / `↓` as structural connectors (vs direction symbols)

`↑` and `↓` have two distinct uses that look similar but mean different things:

**Use 1 — direction symbol (inside a cloze answer):**
```
inhibin&nbsp;A<br>
{{c1::↑}}
```
The cloze answer IS the arrow — the student recalls "inhibin A is increased." This is `↑` as a value.

**Use 2 — structural connector (between lines, non-clozed):**
```
<i>reflex:</i> miosis<br>
<i>efferent:</i> edinger westphal nuclei<br>
↓<br>
{{c1::CN3}}<br>
↓<br>
{{c2::ciliary}} ganglion<br>
↓<br>
{{c3::short}} {{c2::ciliary}} N<br>
↓<br>
sphincter pupillae
```
(Note 1548031995713, miosis pathway.) Here `↓` between lines acts like an italic label would for static attributes — it tells the student "next line is downstream of prior." Each step is its own cloze; the arrow is **non-clozed scaffolding** that defines the chain's structure.

This second use is pervasive in pathway/reflex chains, vaccine schedules (`2M ↓ 4M ↓ 6M ↓ 15M-18M ↓ 4Y-6Y`), and treatment ladders (`resection ↑ 3cm ↑ DA agonist ↑ 1cm ↑ observation`). Don't cloze the arrows — they're the template's spine, like `<i>label:</i>` is for static templates.

---

## §17 — Mnemonics in the back extra field, fully unpacked when AI-authored

**Failure mode (1):** Mnemonic lives in the cloze body, leaks the answer.

**Failure mode (2):** AI generates a cryptic personal-style mnemonic ("box truck") that means nothing to the user because they didn't construct the chain.

**Personal style (author built the chain):**
```
Front: <u>Staff Sections</u><br>S{{c1::4}} = {{c2::logistics}}
Back Extra: <i>mnemonic: box truck</i>
```
"Box truck" works for the author because they built the chain (4 → rectangle → box truck → supplies = logistics). The compressed cue triggers the full chain in their head.

**AI style (must spell out the chain):**
```
Back Extra: <i>mnemonic:</i> 4-sided box truck — rectangles have 4 sides, box trucks are rectangular and haul **supplies** = logistics
```

When the user is reviewing an AI-generated mnemonic for the first time, they need the cue → bridge → answer chain laid out. A bare "box truck" gives them nothing to grip onto.

**Treat mnemonic generation as part of the authoring craft.** Don't leave the field empty just because the source didn't provide one — propose mnemonics where they'd help, especially for arbitrary numeric/letter associations (staff section numbers, cranial nerves, etc.).

### Real-world examples at scale

The "box truck" example above is small. Personal-style mnemonics scale up to multi-drug or multi-criteria mappings without losing their personal character. From the gold reference (Note 1525389805097, AED GABA promoters):

```
<i>pharmotype:</i> AED
<i>drugs:</i>
{{c1::gabapentin}}
{{c2::tiagabine}}
{{c3::topiramate}}
{{c4::VPA}}
{{c5::vigabatrin}}
<i>mechanism:</i> promote @ GABA
```
**Extra:** `<i>PENTagram TIAra aTOP an [acid]spitting BAT</i>`

The mnemonic encodes 5 drug-name initial syllables (PENTa = gaba**PENTa**bin? not quite — actually **gaba**PENTin via "TIA" = TIAgabine, "TOP" = TOPiramate, etc.). Cryptic to outsiders; meaningful to the author who built the chain. This is §17 personal-style at full strength.

**Equivalent maxed-out AI-style** (Note 1508888630522, NRTIs):

```
<i>pharmotype:</i> NRTI
<i>drugs:</i>
{{c1::Abacavir}}
{{c2::Didanosine}}
{{c3::Emtricitabine}}
{{c4::Lamivudine}}
{{c5::Stavudine}}
{{c6::Tenofovir}}
{{c7::Zidovudine}}
```
**Extra:** `<i>Angry Dentists Embalm Lewd Shamans in Tangerine Zest</i>`

Note that the cards have the drugs ordered alphabetically by first letter — the mnemonic sentence reconstructs that exact letter sequence (A-D-E-L-S-T-Z). The user can review the back, see the unfamiliar mnemonic, and immediately decode it because each word's first letter maps cleanly. This is what AI-authored mnemonics should look like: cryptic-sounding but parsable on first encounter through a clear cue → bridge → answer chain.

### Standalone Basic cards for high-yield mnemonics

When a mnemonic is itself testable (rather than just a hook for an underlying concept), promote it to a standalone Basic card:

```
Front: mnemonic for S/S of parkinson
Back:  parkinson TRAPS your body

Front: mnemonic for cerebellar nuclei (lateral → medial)
Back:  DEGrees F° (Dentate, Emboliform, Globose, Fastigial)
```

The back-extra approach is right for mnemonics that scaffold a single fact card. The standalone approach is right for mnemonics complex enough to be drilled on their own (acronym mnemonics, multi-letter ordering mnemonics, full-sentence mnemonics).

---

## §18 — Cloze just the differentiator, not the whole token

**Failure mode:** Clozing a whole compound token forces the student to recall structural framing they already know.

**Bad:**
```
{{c1::S4}} = logistics
{{c1::unframed}} = control measures
```

The student knows it's an S-section (the heading says so) and that the prefix is "un-" or empty. They only need to recall the differentiator: the digit, or "un" vs. nothing.

**Good:**
```
S{{c1::4}} = logistics
{{c1::un}}framed = control measures   (vs. {{c1::+}}framed = units, etc.)
```

The structural common part (`S`, `framed`) becomes the prompt; only the discriminating atom is hidden. As a side benefit, this gives the student type-disambiguation for free — `S[...]` clearly expects a digit; `[...]framed` clearly expects a prefix.

**The `+` / `un` notation:** for binary positive/negative cases, `+` represents "no prefix" / "the affirmative case", paired against `un` (or whatever negative prefix). Two separate notes, both clozing c1, semantically linked as one dichotomy. The student doesn't type `+` — they just confirm their mental classification matched.

---

## §19 — Inline hint syntax `{{cN::answer::hint}}`

Anki's cloze hint syntax displays the hint inside the cloze placeholder, where `[...]` would normally appear. Two distinct uses:

### Use 1 — Type cues (single-character)

Disambiguate the answer's data type:

```
{{c3::→::&harr;}}      → student sees [↔]: "expecting a directional symbol"
{{c1::5::#}}           → student sees [#]: "expecting a digit"
```

**When to use:** answer type ambiguous from context AND a single-character hint resolves it.
**When NOT to use:** surrounding structure already implies the type. `S{{c1::4}}` doesn't need `::#` — the `S__` pattern already says "digit".

### Use 2 — Attribute-type labels (in complex multi-attribute cards)

In a card with many cloze deletions across multiple attributes, the hint tells the student *which attribute they're recalling* without revealing the value:

```
<i>disease:</i> migraine
<i>presentation:</i> {{c6::Pulsatile::quality}}; {{c7::One day::onset}};
                     {{c8::Photophobia::context}}; {{c9::Phonophobia::context}}
<i>epidemiology:</i> {{c2::Caucasian::ethnicity}} > {{c3::Africanamerican::ethnicity}}
```

Each cloze tells the student which attribute slot they're filling: "you're recalling a quality"; "you're recalling an ethnicity"; etc. Without these hints, the student would see a row of `[...]` placeholders and lose track of which attribute each maps to.

**This use is heavily underused by people who only know the type-cue use.** In a complex card with 5+ attributes, it's the difference between "I forgot which one was the gender vs the location" and clean recall.

**Examples worth adopting:**
- `{{c2::males::gender}}`, `{{c4::trunk::location}}`, `{{c3::yellow/white::color}}`
- `{{c2::welding::occupation}}`, `{{c5::a}}symmetric` (using a hint to label a partial-cloze prefix's attribute)

### Maxed-out: HACEK (Note 1447621568502)

A real card showing what attribute-type labels look like at saturation:

```
<i>disease:</i> {{c1::endocarditis}}
<i>organisms:</i>
{{c2::Haemophilus}}
{{c3::Aggregatibacter}}
{{c4::Cardiobacterium}}
{{c5::Eikenella corrodens}}
{{c6::Kingella}}
<i>characteristics:</i>
{{c7::small::size}}; {{c8::slow}} growth; gram {{c9::negative}}; {{c10::bacilli::morphology}}
<i>treatment:</i> {{c11::ceftriaxone::R<sub>X</sub>}}
```
**Extra:** `<i>HACEK</i>` (mnemonic for the 5 organisms)

Eleven clozes in one note; four of them carry attribute hints (`::size`, `::morphology`, `::R<sub>X</sub>`). When the student reviews the c10 card and sees `[morphology]`, they immediately know "expecting a shape descriptor" and can focus recall — no fumbling between "is this asking gram-stain, motility, size, shape, growth rate?"

Note that not every cloze needs a hint. The five organism names (c2–c6) don't carry hints because the `<i>organisms:</i>` slot label already disambiguates. The `c7::small` cloze gets `::size` because "small" alone is type-ambiguous (small organism? small colony? small infection?). **Hints earn their place when surrounding context doesn't already disambiguate** — same rule as Use 1.

---

## §20 — Heading must not double as prompt

*Anti-pattern stub. Full treatment with worked example at **D6** in `references/common-ai-drift.md`.*

A `<u>...</u>` heading alone on the front is ambiguous — the student doesn't know whether to recall the definition, wait for more content, or classify the term. Corrective rule: pair the heading with `<i>term:</i>` and the term beneath, so the structure makes clear what's being asked.

---

## §21 — Compress verbose definitions; don't fall back to Basic

*Anti-pattern stub. Full treatment with worked example at **D7** in `references/common-ai-drift.md`.*

When a doctrinal definition runs 50+ words, the temptation is to ship it as a Basic Q→A. The student then memorizes a paragraph instead of atomic concepts. Corrective rule: compress to 1–3 essential terms, cloze those, push illustrative material to the extra field. Length is poor authoring, not a justification for changing format.

---

## §22 — Periods only for complete sentences

**Style point:** cloze content is usually fragments, lists, or labeled values — not prose. Drop trailing periods.

**Bad:** `{{c1::points}}, {{c2::lines}}, and {{c3::areas}}.`
**Good:** `{{c1::points}}<br>{{c2::lines}}<br>{{c3::areas}}`

Reserve periods for the rare cards where the body is actually a complete sentence (e.g., a quotation or proverb).

---

## §23 — Reusable templates per domain

**Why this is the highest-leverage principle:** the hardest part of card review isn't recall — it's parsing the layout. Every card you encounter, your eyes have to find the structure. A predictable template means the eyes know exactly where to look for each slot, and review speed compounds across hundreds of cards.

**The pattern:** define 3-7 structural templates per content domain *before drafting cards*. Each template has a fixed slot order that becomes muscle memory.

**Example: medical deck templates** (counts from a real 159-cloze neuroscience deck)

```
Drug template (29 cards used "pharmotype:")
  pharmotype: ...
  drugs: ...
  mechanism: ...
  use: ...
  side effect: ...
  1st-line Tx: ...
  CV effects: ...

Disease template (23 cards used "disease:")
  disease: ...
  etiology: ...
  presentation: ...
  pathology: ...
  treatment: ...
  association: ...
  epidemiology: ...
  histology: ...

Anatomical lookup (8 each: tongue innervation, hypothalamic nucleus, thalamic nucleus)
  [region]: ...
  function | input | receiver | side: ...

Lesion template (15 cards used "brainstem syndrome:")
  [lesion]: ...
  level: ...
  area: ...
  structures: ...
  presentation: ...
```

**Each card uses a subset of slots** — not every disease card has all 8 attributes. The template defines the *order* the slots appear in; missing slots are skipped.

**The slot-order rule:** once a deck establishes that `etiology` comes before `presentation`, every disease card in that deck must follow that order. Reordering breaks the muscle memory and forces re-parsing.

**Generic fallback:** if the content doesn't fit a domain-specific template, use a generic `group: / members:` pattern as a safety net rather than inventing per-card structure.

**For AI authoring:** before writing any cards, sketch the templates. Show the user a sample of each template type with one populated card. Get sign-off on slot orders. Then draft the rest, reusing the templates verbatim.

---

## §24 — Acronym-expansion as one-direction Basic

**Failure mode:** Treating acronyms like full vocabulary terms (basic-reversed for term ↔ definition) is unnecessary work. You only encounter acronyms one way in source material — you read "JME" in a textbook and need to know it means juvenile myoclonic epilepsy. The reverse direction (knowing JME's expansion → recognizing the acronym) happens naturally as you read.

**Pattern:**
```
Front: JME
Back:  juvenile myoclonic epilepsy

Front: AC<div>(biochemistry)</div>
Back:  adenylyl cyclase
```

**The domain disambiguator** (`<div>(biochemistry)</div>`) is essential when an acronym overlaps domains. `AC` is adenylyl cyclase in biochem, alternating current in physics, air conditioning in HVAC. The disambiguator scopes the recall to the right domain.

**Use plain Basic, not Basic-and-Reversed.** This is one of the few cases where one-direction is actually correct. Saves you from drilling cards you'd never encounter in practice.

---

## §25 — Compress jargon liberally with domain notation

**Failure mode:** Spelled-out terminology in cloze content makes cards verbose, which slows reviews, which means fewer reviews completed per session, which means poorer retention.

**Once a domain abbreviation is established, use it everywhere:**
- `L/O` for "loss of"
- `NUC` for "nucleus"
- `DZ` for "disease"
- `DD<sub>X</sub>` for "differential diagnosis"
- `MTF` for "medical treatment facility"
- `CN3, CN5, CN7...` for cranial nerves
- `ML` for "medial lemniscus", `STT` for "spinothalamic tract"

**HTML entities for domain notation:**
- Subscripts: `T<sub>X</sub>` (treatment), `5HT<sub>1B/1D</sub>` (serotonin receptor subtypes), `Ca<sup>2+</sup>` (calcium ion), `1°` (primary)
- Symbols: `↑` `↓` for increase/decrease, `→` for "leads to", `≥` `≤`, `±`, `°`, `@` for "located at" (see below)

**The `@` locative operator** (cross-reference §16): `@` compresses "at / located at / occurs in" into a single character and chains for nested locations. Real example (Note 1547516526298, GERD histology):

```
<i>disease:</i> GERD
<i>histology:</i>
{{c3::hyperplasia}} @ {{c2::basal zone}}
+
{{c1::elongation}} @ {{c4::papillae}} @ {{c6::lamina propria}}
+
infiltration = {{c5::eosinophils}}
```

Six clozes, three `@` operators, two structural `+` connectors. The card carries information density that would otherwise take three lines of prose.

**The trade-off:** terse content = faster reviews = more reviews = better retention. But abbreviations need to be learned first. So:

- Abbreviations introduced by the source material → use them everywhere
- Novel abbreviations you (the author) coin → make a Basic acronym-expansion card per #24 first, then use freely
- One-off compression → don't bother; readability matters more

**Example of dense, compressed content** (from real deck):
```
<i>disease:</i> CIDP
<i>presentation:</i> {{c2::mixed}} {{c2::sensorimotor}} polyneuropathy
<i>histology:</i> "{{c3::onion bulbs}}"; Ig{{c4::G}}/{{c4::M}}&nbsp;IC
<i>DD<sub>X</sub>:</i> vs {{c5::GBS}} → {{c6::responds to steroids}}
```

Eight tokens carry information density that would take three lines if spelled out.

---

## §26 — Most numbers don't belong inside a cloze

*Anti-pattern stub. Full treatment with worked examples at **D3** in `references/common-ai-drift.md`.*

Exact recall of high-precision numbers (decimals, percentages, large counts, fractional rates) doesn't map cleanly onto Again/Hard/Good/Easy — the student guesses "28%" against "31.7%" and grading collapses. Corrective rule: numbers earn their place in a cloze only when (a) short (1–3 digits), (b) doctrinally canonical, and (c) themselves the testable atom (`Role 2`, `S4`, `4 vehicles`). Default fixes are reverse direction, move to extra, or simplify the testable fact.

**Cross-principle nuance:** §26 says *which* numbers can be cloze answers; §28 says *which surrounding context* makes those answers derivable. Both checks apply — a card can pass §26's "short doctrinal integer" test and still leak via §28 if the surrounding context exposes the product, sum, or complement. See D8 for the ICWAD `= 60 total` example.

---

## §27 — Don't redundantly cloze abbreviations inside other templates

*Anti-pattern stub. Full treatment with worked example at **D1** in `references/common-ai-drift.md`.*

Clozing the abbreviation inside a unit/disease/section template tests name → abbreviation, the wrong direction. Abbreviations are looked up, not recalled from full names. Corrective rule: keep the abbreviation visible in the heading line (`<i>unit:</i><br>MLMC (medical logistics management center)`) and ship a separate Basic acronym card per §24 for the actual lookup.

---

## §28 — Answer leaks via derivation

*Anti-pattern stub. Full treatment with all four leak mechanisms (arithmetic, logical complement, cardinality, format hint) and worked examples at **D8** in `references/common-ai-drift.md`.*

Beyond synonym leaks (§5) and elimination (§6), watch for *derivation leaks* where one cloze answer is derivable from other visible context. The institutional self-check: *if a forgetful student saw this card for the first time, could they answer the cloze WITHOUT recalling the testable knowledge?* The fresh-agent leak audit (SKILL.md workflow step 7) is the scaled-up version.

**Cross-principle nuance:** §26 (number allowance) and §28 (derivation leak) overlap on numeric clozes but are independent checks. A `{{c1::3}}` can pass §26 and still fail §28 if a visible "= 60 total" leaks the related `{{c2::20}}` via division. Apply both.

---

## §29 — Slot labels are abstract roles, not specific values

**Failure mode:** when designing a template, the agent names slots after specific instances (`<i>field surgeon:</i>`, `<i>command surgeon:</i>`, `<i>dental staff officer:</i>`) instead of abstract roles (`<i>position:</i>`). Two consequences:

1. **Template doesn't generalize.** Every position needs a custom slot label. The cognitive-friction reduction §23 promises (predictable slot order across many cards) is forfeited.
2. **Clozes are unlabeled.** The student sees `{{c1::O4}}` under `<i>field surgeon:</i>` and has no signal that the answer is a rank. They might guess section size, age, vehicle count, anything.

**Bad** (real example from CO 102 fresh build):
```
<i>section:</i><br>BSS<br>
<i>field surgeon:</i><br>{{c1::O4}} / branch {{c2::MC}}
```

**Good:**
```
<i>section:</i><br>BSS<br>
<i>position:</i><br>field surgeon<br>
<i>rank:</i><br>{{c1::O4}}<br>
<i>branch:</i><br>{{c2::MC}}
```

Now `<i>rank:</i>` and `<i>branch:</i>` are reusable across every position in every section. The template generalizes; only the values change. Each cloze is unambiguously labeled.

**Heuristic:** if your slot label varies per note (different label on most cards in the family), the slot label is acting as a value. The actual structural slot is the *category* the label belongs to (`position`, `unit`, `disease`, `phase`). Lift the value out of the label.

This is §23 made strict: §23 says "fixed slot order across the template family"; §29 says "fixed slot *labels* across the template family, with values living between them."

---

## §30 — Show acronym OR expansion, never both

*Anti-pattern stub. Full treatment with worked example at **D11** in `references/common-ai-drift.md`.*

Pairing `{{c1::ambulance loading point}} (ALP)` lets the student decode the cloze from the parenthetical. Corrective rule: pick one form per card. The acronym → expansion lookup direction lives in its own one-direction Basic card per §24; every other card uses either the acronym alone or the expansion alone, never both visible together.

**Cross-references — three principles, three problems:**
- **§24** — acronym → expansion lives in its own one-direction Basic card (the *which-card-handles-lookup* answer)
- **§27** — don't cloze the abbreviation slot inside a template (the *direction* problem)
- **§30** — don't pair expansion with acronym anywhere a cloze answer is involved (the *leak* problem)

---

## §31 — Yield-density triage gate

**Failure mode:** the AI authors notes for every slide it sees, even when the slide carries fewer than 3 atomic, high-yield, otherwise-not-recallable facts. Templated nonsense from low-yield content is the signature of this drift (see **D19** in `references/common-ai-drift.md` for the post-hoc detection signal). The author is solving the wrong problem: producing notes that pass linting rather than producing notes worth making.

**The unit of judgment is the topic / information unit, not the slide.** A topic may span multiple slides; a single slide may contain multiple unrelated topics; some slides contribute nothing testable at all. Slides are presentation packaging — don't let them drive content decisions. Group source content into topics during the *organize* stage of the prep pipeline (SKILL.md Step 2c), then apply this gate per topic in the *prioritize* stage (Step 2d).

**Three-condition test** (mirroring §26's structure for per-fact yield, applied at the topic level): a topic deserves a card-family when

- (a) it contains **≥3 atomic facts** — single-fact topics are usually a context note in `extra` or a footnote, not a card-family,
- (b) those facts are **unlikely to be available at test-time without memorization** — content any practitioner in the target field would already know from background isn't a recall target,
- (c) they are **aligned with the LOs** from Step 1 — content outside the test scope is scaffolding even when it's information-dense.

A topic that fails any condition is **scaffolding**. Compress to a single context note (the gist of the topic in one card, often inside `extra`) **or** skip entirely. Do not fill a template just because the template fits.

**High-yield example — keep:**
```
Source: a 3 × 2 matrix on a single slide — priority (urgent / priority / routine)
× stage (POI / patient transfer) → time-to-evacuate.
6 cells of doctrinally canonical integer timing data, all listed in the LOs.

Yield: high. Passes (a) ≥3 atoms, (b) not background knowledge, (c) LO-aligned.
Schema (per §32): bundled matrix, 6 notes / 12 cards.
```

**Low-yield example — skip:**
```
Source: a slide of editorial bullets — "policy considerations include
operational environment, clinical imperatives, JCS advice, theater commander
recommendation, last policy day, surge capability..."

Yield: skip. Fails (a) — there are bullet points but they're scaffolding for
the next slide's actual content, not standalone atomic facts. Authoring 9
templated notes from this slide produces things like
`<i>policy fact:</i><br>not<br><i>value:</i><br>{{c1::hold until last policy day}}` —
the label is nonsense, the atom is editorial. Mark `yield: skip` in the
outline (Step 2.5); produce zero notes.
```

**Cross-references:**
- **§26** (numbers earn their place) — sibling principle. §26 gates *individual cloze answers within a note*; §31 gates *whether a topic is a source at all*. Both apply.
- **D14** (vague/editorial labels) — the per-note signal that §31 was missed during prioritization. Catch it earlier with §31; catch what slips through with D14.
- **D19** (high-volume, low-density output) — the family-level signal of the same failure. If you find a D19-shaped family in self-audit, it's evidence that the originating topic should have been gated out by §31.

---

## §32 — Bundle dense matrices as bidirectional families

**Failure mode:** N × M numerical or categorical matrices (3 priorities × 2 stages, 4 stages × 3 metrics) get collapsed into single-cloze-per-row notes that hide the matrix structure. The student memorizes per-row trivia instead of the grid relationships, and individual cells can't be tested in both directions.

**Bad** (collapsed to one note per row, structure lost):
```
<i>evacuation standard:</i><br>24 hr from POI / 72 hr patient transfer<br>
<i>category:</i><br>{{c1::routine}}
```

There's no way to test "given priority + stage, recall time" or "given time + stage, recall priority." The student memorizes `routine = 24 hr from POI / 72 hr patient transfer` as a single string, and Anki grading collapses to "did I produce this exact string?" — which doesn't track recall of either axis.

**Good** (one note per cell, shared template, multi-cloze for bidirectionality):
```
<u>Evacuation Standards</u><br>
<i>priority:</i><br>{{c1::urgent}}<br>
<i>stage:</i><br>POI<br>
<i>time:</i><br>{{c2::60 minutes}}
```

(Repeat for each of the 6 cells: 3 priorities × 2 stages.)

Each note generates 2 cards via multi-cloze: one with priority hidden (test "given stage + time, recall priority") and one with time hidden (test "given priority + stage, recall time"). Stage stays visible. 6 notes × 2 cards = 12 cards covering the matrix bidirectionally. If you wanted 3-direction testability, cloze stage too: 6 notes × 3 cards = 18 cards.

**Pattern recipe:**

- **A single shared template with consistent slot order** (e.g., `priority / stage / time`) — this is §23 specialized for matrix-shaped data.
- **One note per cell** (N × M notes total).
- **Multi-cloze deletions** chosen to test in multiple directions per cell. The axis you don't cloze stays visible as the "given" context.
- **Optional**: a top-header `<u>...</u>` framing the matrix. Use the header **only when it lets the slot labels be shorter** — e.g., `<u>Evacuation Standards</u>` lets each slot say `priority` instead of `evacuation priority`, `stage` instead of `evacuation stage`. Most matrices don't need a header. The italic slot labels carry the matrix identity on their own.

**When NOT to use §32:**

- **§12 (Basic-and-Reversed)** is the wrong tool for matrices. Basic-and-Reversed is a 2-field pair generating 2 cards; a matrix is N × M cells. Multi-cloze inside a §32-shaped note gives per-cell bidirectionality without the note-count explosion you'd get from chaining Basic-and-Reversed pairs.
- **Asymmetric attribution** (sector 1 has 1 attribute, sector 2 has 4 attributes) is §7 territory, not §32. §7 thin-slices to prevent cardinality cheating; §32 assumes a roughly balanced grid.

**Cross-references:**
- **§23** (reusable templates) — §32 is §23 specialized for N × M data. The shared template carries the matrix identity; the bundling enables bidirectional testability per cell.
- **§12** (Basic-and-Reversed) — wrong tool for matrices; included here as a pointer so the AI doesn't reach for it instinctively.
- **§7** (asymmetric thin-slicing) — orthogonal failure mode for unbalanced shapes; cite §7 instead when cells aren't comparable.
