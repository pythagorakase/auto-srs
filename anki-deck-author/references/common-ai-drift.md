# Common AI Drift Patterns — Catalog

When AI agents author Anki decks, certain antipatterns recur even when the principles forbidding them are documented. This catalog names each drift pattern, explains *why* AI tends to commit it, and gives the corrective rule. Read this **before authoring** to inoculate against drift; reference it during the self-audit step.

These patterns surfaced during real iteration cycles. Each one cost a QC pass to discover.

## Drift ↔ principle map

Each drift pattern maps to one or more principles in `SKILL.md` and `principles-detail.md`. The drift catalog is the *AI-failure-mode* lens; the principles list is the *positive-rule* lens. Both stay in sync via the numbering convention (numbers are stable IDs, append-only).

| Drift | Principle(s)        | Lint rule (`scripts/lint_deck.py`) |
|-------|---------------------|------------------------------------|
| D1    | §27                 | `D1-abbrev-in-template`            |
| D2    | §5 corollary        | `D2-image-back-def-front`          |
| D3    | §26                 | `D3-precision-number`              |
| D4    | §7                  | not implemented (semantic)         |
| D5    | §6                  | `D5-trivial-deletions-suspect`     |
| D6    | §20                 | `D6-heading-only-front`            |
| D7    | §21                 | not implemented (semantic)         |
| D8    | §28                 | `D8-arithmetic-leak`               |
| D9    | §5                  | `D9-example-in-body`               |
| D10   | §23 corollary       | `D10-empty-template-slot`          |
| D11   | §30                 | `D11-acronym-expansion-pair`       |
| D12   | §29                 | `D12-orphan-label-to-cloze`        |
| D13   | §6, §28, §29        | `D13-orphan-side-by-side-mapping`  |
| D14   | §23                 | `D14-vague-prompt-label`           |
| D15   | §23                 | `D15-singleton-template`           |
| D16   | §23                 | `D16-untemplated-cloze-list`       |
| D17   | §2, §4, §28         | `D17-mixed-repeat-cloze-state`     |
| D18   | §23, §29            | `D18-overfit-entity-label`         |
| D19   | §23, §31            | not implemented (semantic)         |

D4, D7, and D19 require judgment the regex-based linter can't make: D4 (asymmetric attribution) and D7 (verbose-Basic-vs-compressed-cloze) need semantic understanding; D19 (high-volume low-density output from one source) needs source-topic attribution that lives outside the .apkg. Catch them in the fresh-agent leak audit (SKILL.md workflow step 7) instead.

---

## Drift #1 — Abbreviation-as-cloze inside a template

**The pattern:**
```
<i>unit:</i><br>medical logistics management center<br>
<i>abbreviation:</i><br>{{c1::MLMC}}<br>
<i>BOA:</i><br>1 per force
```

**Why AI does this:** templates are slot-filling exercises. When the source material has both a full name and an abbreviation, the AI naturally generates a slot for each. Treating the abbreviation as a cloze feels like atomization (#1).

**Why it's wrong:** the test direction is wrong. The student encounters the abbreviation in the wild and looks up the expansion — never the reverse. Clozing the abbreviation tests name → abbreviation, which the student doesn't need to drill.

**Corrective rule (per §24, §27):** put the abbreviation in the heading line: `<i>unit:</i><br>MLMC (medical logistics management center)`. Drop the abbreviation slot. Ship a separate multi-cloze acronym note in the central Acronyms deck (per §24) if the student needs the lookup direction.

---

## Drift #2 — Image on the back, definition on the front

**The pattern:**
```
Text: <i>tactical mission task:</i><br><i>definition:</i><br>seal off enemy<br>from sources of support<br><i>name:</i><br>{{c1::isolate}}
Extra: <img src="isolate_symbol.png">
```

**Why AI does this:** definitions are textually generative — easy to write — and AI defaults to "definition first" because that's the dominant pattern in flashcard training data. The image is supplementary and gets relegated to extra.

**Why it's wrong:** test direction. The student will see a symbol on a map and identify it. They won't be given a definition and asked to name the TMT. Worse: the visible definition often contains synonyms of the cloze answer ("seal off" → "isolate"), giving the answer away.

**Corrective rule (per #5 corollary):** image goes on the FRONT, name is the cloze answer, definition lives in extra as supporting context only.

---

## Drift #3 — Numbers in clozes when they haven't earned their place

**The pattern:**
```
<i>BOA / PAX:</i> 1 per {{c1::43,000}} pop / {{c1::88}}
```

**Why AI does this:** the source material has specific numbers; the AI assumes specificity = value and clozes them. It feels like atomization.

**Why it's wrong:** exact recall of "43,000" or "88" isn't a clean Again/Hard/Good/Easy decision when the student guesses "40,000" or "85". Grading collapses; the card teaches less than its review burden costs.

**Corrective rule (per #26):** numbers must earn their place inside a cloze. Default is to reverse direction (cloze the unit, not the number) or move the number to extra. Allowed in cloze only if short, doctrinally canonical, and itself the testable atom (Role 1, S4, 4 vehicles).

---

## Drift #4 — Multi-cloze lists when thin-slicing is needed

**The pattern:**
```
sector 2 = {{c1::mobility}} / {{c2::size}} / {{c3::range}} / {{c4::altitude}}
```

(With sector 1 = capability nearby in the deck.)

**Why AI does this:** atomizing each list element looks like principle #1 in action. The visible structure even reinforces atomization.

**Why it's wrong:** for asymmetric attribution (sector 1 has 1 thing, sector 2 has 4), the student can deduce attribution from cardinality without recalling specific facts. They see "sector 2 = [...], size, range, altitude" and answer "mobility" because it's the only sector-2 attribute they remember — not because they recall the attribution.

**Corrective rule (per #7):** create dedicated single-cloze notes per attribute (`sector {{c1::2}} = mobility`, `sector {{c1::2}} = size`, etc.) for child→parent attribution drilling. Keep the parent-list note as a separate card for parent→list testing.

---

## Drift #5 — Trivial cloze deletions

**The pattern:**
```
sector {{c1::1}} = capability
sector {{c2::2}} = mobility
```

**Why AI does this:** clozing both numbers seems balanced and atomic.

**Why it's wrong:** the student reasons by elimination. Seeing "sector [...] = capability", they answer "1" because they know "2 = mobility" from the next card. The deletion teaches no recall — just reading comprehension.

**Corrective rule (per #6):** if a deletion is answerable via elimination from adjacent context, remove it. Cloze only deletions that genuinely require recall.

---

## Drift #6 — Heading-only fronts on definition cards

**The pattern:**
```
Front: <u>Company Team</u>
Back: a combined-arms organization formed by attaching one or more nonorganic
      armor, mech infantry... (long doctrinal definition)
```

**Why AI does this:** for "company team", the heading IS the term. AI maps "term → definition" to "heading → body" naturally.

**Why it's wrong:** the front is ambiguous. Is "Company Team" a heading framing more content (and the student should wait for click)? Or is it the term to recall the definition for? The student doesn't know what's being asked.

**Corrective rule (per #20):** pair the heading with `<i>term:</i>` and the term beneath. The heading frames the topic; the sub-label specifies "this is the term being defined."

---

## Drift #7 — Verbose definitions left as Basic Q→A

**The pattern:**
```
Front: <u>Company Team</u>
Back: [50-word doctrinal block]
```

**Why AI does this:** the doctrinal definition is long; AI assumes long = "Basic only, can't be cloze-d cleanly".

**Why it's wrong:** the student is now memorizing a paragraph instead of atomic concepts. Most 50-word definitions have 1-3 essential terms; the rest is qualifying language.

**Corrective rule (per #21):** compress to the essential 1-3 atoms, atomize via cloze, push illustrative material to extra. Length is poor authoring, not a justification for abandoning cloze.

---

## Drift #8 — Answer leaks via arithmetic / logical derivation

**The pattern:**
```
<i>config:</i> {{c1::3}} wards × {{c2::20}} ICW each = 60 total
```

**Why AI does this:** including the total feels informative ("3 × 20 = 60, here's the total for context").

**Why it's wrong:** if the student sees "3 wards × [...] ICW each = 60 total", they can solve for "20" via division. The "60 total" leaks the answer arithmetically. Same problem with sums, complements, ratios, etc.

**Corrective rule (per #28 — see SKILL.md):** before clozing numeric content, check whether the visible context constrains the answer mathematically. If yes, drop the derivable value or restructure so all derivable values are clozed together with the same cloze number.

Also applies to:
- Logical complements (if A and B exhaust the space, knowing one implies the other)
- Cardinality (a 4-item list with 3 visible items)
- Format hints (a `[#]` placeholder suggests digit-shaped answers, ruling out word answers)

---

## Drift #9 — Examples adjacent to cloze answers

**The pattern:**
```
sector {{c1::1}} = {{c2::capability}} (e.g., radar)
```

**Why AI does this:** examples make the card feel grounded; AI puts them inline for context.

**Why it's wrong:** "(e.g., radar)" tells anyone who knows what radar is that the cloze answer is "capability". Synonym/exemplar leak.

**Corrective rule (per #5):** examples ALWAYS go in the extra field. Never inline.

---

## Drift #10 — Cluttered template slots that don't earn their place

**The pattern:** unit templates with 6-8 slots even when only 2-3 are testable for that specific unit. AI fills slots because they exist in the template, not because the content warrants it.

**Why it's wrong:** more slots = more cloze targets = more cards = more review burden. Template uniformity is valuable (#23), but slot fidelity to actual content is too. Filling a slot with "n/a" or padding text is worse than omitting it.

**Corrective rule:** templates define the SLOT ORDER, not a requirement that every slot be filled. Skip slots that don't apply to a particular instance.

---

## Drift #11 — Acronym and expansion paired in the same card

**The pattern** (real example from CO 102 fresh build):
```
{{c1::ambulance loading point}} (ALP)
{{c2::ambulance relay point}} (ARP)
{{c3::ambulance control point}} (ACP)
```

**Why AI does this:** when the source material introduces a term with its acronym (`ambulance loading point (ALP)`), the AI faithfully copies both. The pairing reads naturally — feels informative, like "showing your work." It also feels safer: if the student can't recall the expansion, the acronym serves as a hint.

**Why it's wrong:** the parenthetical neutralizes the cloze. The student sees `[...] (ALP)` and decodes "ambulance loading point" from the acronym. The card now tests acronym → expansion lookup — and that lookup is already owned by a separate multi-cloze acronym note per §24 (in the central Acronyms deck). The cloze teaches nothing it didn't already teach.

The reverse direction is just as bad: `{{c1::ALP}} (ambulance loading point)` lets the student decode ALP from the visible expansion.

**Corrective rule (per §30):** ship one form per card. Pick the acronym alone OR the expansion alone. The acronym lookup direction (acronym → expansion) lives in its own multi-cloze acronym note per §24 (in the central Acronyms deck). Every other card trusts that lookup card and uses one form consistently.

The exception (per §27): a heading line like `<i>unit:</i><br>MLMC (medical logistics management center)` is fine — that's a non-clozed disambiguator, not a paired cloze. The lint rule `D11-acronym-expansion-pair` only fires when the cloze answer itself is paired with a parenthetical acronym/expansion of the answer.

---

## Drift #12 — Orphan labels mapped directly to cloze values

**The pattern:**
```
<i>medical materiel:</i><br>{{c1::Class VIIIA}}<br>
<i>blood:</i><br>{{c2::Class VIIIB}}
```

when no other note uses the same `medical materiel → blood` slot signature.

**Why AI does this:** source tables often present rows as `thing → value`, and AI faithfully turns the row header into an italic label.

**Why it's wrong:** the row header may be a testable value rather than a reusable structural slot. The linter should not decide that from the label text alone; the structural clue is whether the label signature recurs. A repeated signature is evidence of a real template. A singleton signature with label→cloze-only mappings is suspect.

**Corrective rule (per §29):** either add sibling notes with the same slot signature, or lift row values into abstract slots:
```
<i>MEDLOG function:</i><br>{{c1::medical materiel}}<br>
<i>class:</i><br>{{c2::VIIIA}}
```

---

## Drift #13 — Orphan side-by-side mapping tables

**The pattern:**
```
<i>low:</i><br>{{c1::company}}<br>
<i>moderate:</i><br>{{c2::BN}}<br>
<i>high:</i><br>{{c3::BDE}}
```

when no other note uses the same `low → moderate → high` slot signature.

**Why AI does this:** tables feel compact, and compactness looks like good Anki formatting.

**Why it's wrong:** adjacent mappings invite elimination, contrast guessing, and answer-shape inference. The student can often recover one answer from the neighboring rows rather than recalling the tested relationship.

**Corrective rule:** repeated mapping signatures are allowed because the student learns the template. Singleton mapping tables should be split into single prompt→answer notes or converted into a stable abstract template where the relationship itself is explicit.

---

## Drift #14 — Vague or editorial prompt labels

**The pattern:**
```
<i>often-missed function:</i><br>{{c1::regulated medical waste}}
```

**Why AI does this:** AI uses editorial labels to justify including a marginal fact.

**Why it's wrong:** the label does not tell the student what relationship is being tested. It also masks low-yield content: if the best prompt is "often-missed," the atom probably does not belong in a slim deck.

**Corrective rule:** replace the label with a concrete structural slot or delete the atom.

---

## Drift #15 — Singleton templates

**The pattern:**
```
<i>unit:</i><br>MLMC<br>
<i>mission:</i><br>centralized tactical-to-strategic {{c1::MEDLOG}} management<br>
<i>coordination:</i><br>{{c2::TMC}} and {{c3::theater surgeon}}
```

when no other notes use the same `unit → mission → coordination` slot signature.

**Why AI does this:** AI invents a custom "template" for every source-table row, because the local row has slightly different details from its neighbors.

**Why it's wrong:** a real template earns its cognitive overhead by recurring. If a slot signature has no siblings, the student must parse a new layout for one note only. That is a sign the note may be a value-as-label table, an over-bundled row, or a one-off card whose labels need closer scrutiny.

**Corrective rule:** reusable templates should have siblings. A top-level `<u>...</u>` heading is optional; missing headings are not a problem when the italic labels make the prompt clear. The linter treats exact italic-label signatures as the template identity, independent of whether the label strings appear in a whitelist. For singleton signatures, either normalize the slots to match an existing template, verify the labels are still abstract roles, or split high-yield atoms into simpler notes.

---

## Drift #16 — Untemplated cloze lists

**The pattern:**
```
<u>Ambulance Shuttle System Components</u><br>
{{c1::ALP}}<br>
{{c2::ARP}}<br>
{{c3::ACP}}
```

**Why AI does this:** a heading plus a compact cloze list is easy to generate and often looks clean.

**Why it's wrong:** the note has no slot-label signature, so it cannot prove that the layout is a reusable template. The student sees a one-off list rather than a learned relationship shape.

**Corrective rule:** convert the note into labeled slots that can recur:
```
<i>system:</i><br>ambulance shuttle system<br>
<i>components:</i><br>{{c1::ALP}}<br>{{c2::ARP}}<br>{{c3::ACP}}
```

If another note uses `system → components`, the repeated signature gives the template a green light.

---

## Drift #17 — Mixed visible/clozed repeated strings

**The pattern:**
```
<i>section:</i><br>BSS<br>
<i>responsibilities:</i><br>
identifies {{c1::casualty estimates}}<br>
identifies casualty {{c2::flow/timing}}<br>
forecasts Class&nbsp;{{c3::VIII}} consumption
```

**Why AI does this:** AI tends to cloze the phrase as it appears in the first source bullet, then preserve shared context words visibly in later bullets. It looks like natural prose compression, but it creates an inconsistent recall target.

**Why it's wrong:** the same atom appears both hidden and visible inside one note. On the `c1` card, the visible sibling line tells the student that "casualty" belongs in the answer. If the repeated atom is testable, every occurrence should be linked behind the same cloze number. If it is just scaffolding, every occurrence should stay visible.

**Corrective rule:** choose one treatment for the repeated string:
```
identifies casualty&nbsp;{{c1::estimates}}<br>
identifies casualty&nbsp;{{c2::flow/timing}}
```

or, if "casualty" itself is worth drilling:
```
identifies {{c4::casualty}}&nbsp;{{c1::estimates}}<br>
identifies {{c4::casualty}} {{c2::flow/timing}}
```

The same rule applies when a repeated term is clozed under different ordinals; repeated testable terms should use a linked cloze, not separate cloze numbers.

---

## Drift #18 — Entity-specific labels instead of normalized schema

**The pattern:**
```
<i>HH-60M crew station:</i><br>cabin<br>
<i>crew:</i><br>{{c1::crew chief}}<br>{{c2::flight paramedic}}
```

**SQL-schema mental model:** treat the first italic label like a table name and later italic labels like columns. `vehicle` is a plausible table. `HH-60M crew station` is not; it bakes a row value into the schema.

**Why AI does this:** source slides are often organized around one platform, unit, or named system. AI mirrors that local heading into the label, producing a one-off schema that looks specific and helpful.

**Why it's wrong:** the label is doing two jobs: naming the entity and naming the relationship. That prevents template reuse and hides the underlying structure. If one vehicle gets a custom "HH-60M crew station" schema, the deck either needs comparable schemas for other vehicles or, more likely, needs a normalized `vehicle → station → crew` template.

**Corrective rule (per §23, §29):** lift the entity into a value slot and keep labels abstract:
```
<i>vehicle:</i><br>HH-60M<br>
<i>station:</i><br>cabin<br>
<i>crew:</i><br>{{c1::crew chief}}<br>{{c2::flight paramedic}}
```

The linter flags italic labels containing common platform/model designators such as `HH-60M`, `M997A1`, or `M1133`. Use `lint-ok-d18` only after manually confirming the entity-specific label is genuinely clearer than normalization.

---

## Drift #19 — High-volume, low-density output from one source

**The pattern:** a family of 3+ notes sharing the same template signature, where most notes have ≤1 testable atom each and the labels are vague or editorial:

```
<i>patient movement policy fact:</i><br>constraint<br><i>value:</i><br>{{c1::operational environment}}
<i>patient movement policy fact:</i><br>decision driver<br><i>value:</i><br>{{c1::clinical imperatives}}
<i>patient movement policy fact:</i><br>development input<br><i>value:</i><br>{{c1::JCS advice}}
<i>patient movement policy fact:</i><br>not<br><i>value:</i><br>hold until {{c1::last policy day}}
```

(...continuing for 5 more notes from the same source slide.)

**Why AI does this:** when source material is editorial scaffolding (a slide of vague bullets, a transition page, a "considerations include..." enumeration), the AI tries to extract testable atoms from text that doesn't actually contain any. Templating helps the output *look* uniform — same italic slot signature across the family — so it superficially looks like §23 reusable-template practice. The linter checks per-note rules and doesn't catch slide-level over-extraction, so each note passes lint and the family ships.

**Why it's wrong:** read the family together (which the per-note linter never does) and the failure becomes obvious. Each note in isolation looks plausible; the family read in aggregate reveals that the source had nothing to teach. The student studies a deck full of notes whose answers are not memorable atoms, only positions in an arbitrary list. Worse, the family burns review budget that should have gone to high-yield content elsewhere in the deck.

The single-word slot labels (`not`, `constraint`, `development input`) are themselves a tell: D14 (vague/editorial labels) catches them per-note, but the underlying problem is upstream — the topic should have been gated out by §31 before authoring.

**Corrective rule:** at the self-audit (SKILL.md Step 6) or fresh-agent audit (Step 7), look for families of 3+ notes sharing a template signature where most notes have ≤1 atom and labels are vague. When you find one:

1. Identify the originating source (slide / topic).
2. Re-judge the topic against §31's three-condition test: ≥3 atomic facts, otherwise-not-recallable, LO-aligned.
3. If the topic fails any condition, **delete the entire family**. Don't try to salvage individual notes — the topic is scaffolding.
4. If the topic actually passes §31 and you still authored a low-density family, the schemas were wrong. Re-plan in 2e: maybe the content is a definition (§5), maybe a process flow, maybe a single context note in `extra`.

**Why this isn't lint-detectable:** the linter sees notes, not the topics they came from. Without source attribution (note → topic / slide), it can't ask "did this topic deserve N notes?" Future heuristics could flag families where (template-signature note count ≥ K) AND (median atom-per-note ≤ M), but real coverage probably needs `src_topic` embedded in note tags OR the linter reading the Step 2.5 outline YAML alongside the .apkg.

**Cross-references:**
- **§31** (yield-density triage gate) — the upstream principle. D19 is the post-hoc signal that §31 was missed.
- **D14** (vague/editorial labels) — the per-note signal of the same problem. D14 catches the symptom; §31/D19 are the root cause.
- **SKILL.md Step 7** (fresh-agent audit) — where D19 is operationally caught.

---

## How to use this catalog

1. **Read before authoring.** Each pattern names a recurring drift mode. Knowing the failure mode in advance makes it more salient when you're about to commit it.
2. **Self-audit step.** After drafting cards, walk through the drift patterns above against each card. Flag and fix any matches.
3. **Fresh-agent leak audit.** For deeper checks (synonym leaks, derivation, cardinality), spawn a separate agent that reads each card cold and asks "could a forgetful student answer this without recalling the testable knowledge?" Fresh eyes catch what the author misses.

Linter suppressions are tags, not text edits. Add `lint-ok-d18` to suppress a reviewed D18 exception, or `lint-ok-all` only for rare notes where all current and future lint warnings should be ignored.

These patterns aren't exhaustive. New drift modes will surface. When they do, add them here — append-only, never renumber (the D# IDs are stable across SKILL.md, this file, and `scripts/lint_deck.py`).
