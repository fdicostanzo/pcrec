# LENS 4 — CLARITY (naming, comments, structure) + LENS 7 (archaeology migration)

Lane `lens4clar`, opus, READ-ONLY (nothing under `src/`, `cli/`, `lib/`,
`tests/`; no `make`, no build, no suite run). Charter:
`docs/dev/reviews/code_review_criteria_draft.md` (RATIFIED 2026-09-17),
lens 4 carrying lens 7's deliverable per the ratification's open-item
disposition ("7 merges into 4").

Scope: the charter's PRIMARY tier — `src/`, `cli/`, `lib/`, 60,380 lines
across 47 `.c`/`.h` files, 860 functions.

---

## 0. THE HEADLINE, AND IT INVERTS THE CHARTER'S OWN PREMISE

The charter's seed for this lens is *"the inline-archaeology problem — wave
histories and panel citations living in code comments (emit_vm.c carries
30-line change-history preambles)."*

**Measured, that example does not reproduce, and the diffuse problem it
describes is not there.** `emit_vm.c`'s preamble (`:1-55`) is architecture
prose — five numbered design decisions, the no-interpreter constraint, the
one-indirect-jump invariant — with exactly one dated clause in it. Scanned
programmatically over the whole tier, **only TWO comment blocks are
multi-event change logs** (≥20 lines, ≥3 distinct dated/versioned event
markers), and **one of them is 431 lines while the other is 31**:

| block | lines | distinct events |
|---|---|---|
| `src/gen/emit_dfa.c:1534-1964` (inside `emit_info_def`) | **431** | 17 |
| `src/core/internal.h:1741-1771` (the `ESEL_*` enum) | 31 | 3 |

So the archaeology is **concentrated, not diffuse**, and finding **A1** below
is essentially the whole of lens 7's remediable population. That is the good
news, and it is what lets this report recommend something narrow.

The real clarity problem this lens found is a different one, and it is
structural rather than textual:

**The tree is 56.0% comment (33,834 of 60,380 lines), and header-comment
coverage falls as functions get longer — 7 of the 8 longest functions have no
function header at all.** A reader arriving at `pcrec_emit_vm` (778 code
lines, 3,037 span) gets three thousand lines of excellent section-by-section
prose and not one sentence saying what the function does or what it
guarantees. That is finding **C1**, and it is the highest-value item here.

---

## 1. FINDINGS — CLARITY (lens 4)

Ranked per A4. Severity / effort / blast radius on every row.

### C1 — Header coverage inverts with function length; the 8 longest functions have none

**MAINTAINABILITY · LOCAL (per function) · blast radius: 43 files-touched-if-all, 0 checks staled**

A5 evidence: `tools/review/out/function_census.tsv`, joined against a
preceding-comment-line count taken for all 860 rows.

| code lines | functions | with a ≥3-line header | rate |
|---|---|---|---|
| ≥200 | 8 | 1 | **12.5%** |
| 100-199 | 23 | 7 | 30.4% |
| 50-99 | 45 | 23 | 51.1% |
| 25-49 | 111 | 75 | **67.6%** |
| <25 | 673 | 305 | 45.3% |

The monotone fall from 67.6% to 12.5% across the three buckets above 25 lines
is the finding. The one exception in the ≥200 bucket is `cli_parse`
(`cli/main.c:379`, 4-line header).

**43 functions at ≥50 code lines have ZERO preceding comment lines.** The
worst ten, all of which are also the census's longest rows:

| function | file:line | code / span |
|---|---|---|
| `pcrec_emit_vm` | `src/gen/emit_vm.c:8539` | 778 / 3037 |
| `pcrec_rxt_source_parse` | `src/parse/rxt_source.c:2095` | 548 / 975 |
| `compile_driver` | `src/core/compile.c:556` | 402 / 1234 |
| `main` | `cli/main.c:1223` | 331 / 514 |
| `vm_render_listing` | `src/gen/emit_vm.c:7777` | 288 / 501 |
| `vm_emit` | `src/gen/emit_vm.c:7129` | 211 / 515 |
| `emit_attempt` | `src/gen/emit_dfa.c:6373` | 201 / 509 |
| `vm_revdet_rep` | `src/gen/emit_vm.c:4827` | 184 / 323 |
| `emit_predicate_axes` | `src/parse/axes_dump.c:375` | 178 / 294 |
| `pcrec_rxt_source_tsv` | `src/parse/rxt_source.c:3816` | 167 / 222 |

This is not a comment-mass problem — `pcrec_emit_vm`'s span-vs-code gap is
2,259 lines, i.e. three quarters of it IS commentary. The commentary is all
*interior*: it explains each decision at the point the decision is made and
nothing explains the function. The cost is concrete. `pcrec_emit_vm` takes
`Ast *root` rather than `const Ast *root`, and the reason (the emitter fills
`u.call.save`/`nsave`, so the qualifier is dropped deliberately rather than
casually) is recorded in `src/core/CLAUDE.md` and **nowhere in
`emit_vm.c`** — a reader who wants to know whether that non-const is a smell
or a contract has to leave the file.

**Suggestion.** Not "write headers everywhere" — that is the perversion lens
11 warns about. Write one for each of the 43, sized to the function: for the
ten above, a 5-15 line header answering (a) what it produces, (b) what it
reads that is not a parameter, (c) the one invariant a caller must not break.
Most of that text already exists inside the body and can be hoisted rather
than composed. Zero checks bind to any of these sites (§3 annex), so this is
the cheapest MECHANICAL work in the whole review.

### C2 — `emit_attempt`'s section banner sits above the wrong function

**POLISH · MECHANICAL · blast radius: 1 file, 0 checks**

`src/gen/emit_dfa.c:6365` reads `/* ---- ENG_ATTEMPT: computed-goto per-start
attempt loop ---- */` and is immediately followed by `emit_target` (a 4-line
helper at `:6367`), with `emit_attempt` itself starting at `:6373`. The banner
names the section correctly and lands on the wrong function, so the 201-line
function it describes reads as header-less (C1) and the 4-line helper reads as
the engine.

**Suggestion.** Move the banner above `emit_target` *as a section banner*
(spaced, not attached) and give `emit_attempt` its own header. This is a
special case of C1 and should ride it.

### C3 — [M6-READ]'s rename reached the EMITTED names and not the compiler-side locals that produce them

**MAINTAINABILITY · MECHANICAL · blast radius: 1 file, 26 sites, 1 sabotage row re-aimed (S82)**

`src/gen/CLAUDE.md`'s `[M6-READ]` section records a deliberate, approved
rename of emitted identifiers, ENG_ATTEMPT's row included:
`cls/acc2/seed/gseed/t<N>` → `byte_class / is_accepting_by_class /
seed_state / gstart_seed_state / targets_<N>`.

**The emitted side moved; the compiler-side locals that decide and emit them
did not.** `src/gen/emit_dfa.c:6417-6435`:

```c
bool acc2  = dfa_has_clsacc(d);
bool seed  = dfa_needs_seed(d);
bool gseed = dfa_needs_gseed(d);
bool gtbl  = false;
```

…and `:6555-6561`'s `a_bot` / `a_gst` / `anchored`. 26 occurrences of that
family in the file. `acc2` is the sharpest: the `2` means "class-indexed",
which nothing in the name says, and the comment directly above it has to
translate it back (*"`acc2` is the class-indexed accept"*) — a comment that
exists only because the name does not carry the property. The emitted
spelling, `is_accepting_by_class`, needs no such gloss.

**A1 check:** this does NOT contradict `[M6-READ]`. That section's scope is
explicitly the *generated* vocabulary ("the generated C is a first-class
deliverable"), and its two stated rules are about emitted names. Extending the
same vocabulary inward is additive to it, not a reversal.

**Suggestion.** Rename the six to their already-approved emitted spellings
(`has_class_accept`, `needs_seed`, `needs_gstart_seed`, `gstart_seed_table`,
`interior_dead_bot`, `interior_dead_gstart`) and delete the glossing clauses
the comments now need. Note `src/gen/CLAUDE.md`'s own **RULE 2** ("a variable
spelled in two places will be renamed in one") applies to *emitted* format
strings; these are ordinary C locals and carry no such hazard.

**A3 carve-out, found by grepping rather than assumed — and it changes the
row's cost.** `gseed` is not rename-free: sabotage row
`tests/mech/sabotages/S82_prefilter_bound_at_zero.sh:56` anchors on
`SAB_BEFORE='                  gseed ? "search_from" : "0",'`, an anchor
whose text is the identifier itself. A `gseed` rename **stales S82 and must
carry its re-aim in the same change** (and, per BOILERPLATE, the re-aim needs
its intent re-verified, not merely its text updated). The other five
(`acc2`, `gtbl`, `a_bot`, `a_gst`, and the emitted-side `facc2`/`racc2`
spellings) appear in `tests/` only inside script header comments, failure
messages and one `.rxt` comment (`run_wordctx_identity.sh:17`,
`run_mlinectx_identity.sh:18`, `run_gstart_identity.sh:7,256`,
`gpos.rxt:419`, `S83`'s own header) — prose, not needles, so they cost
nothing but are worth updating for consistency with the rename.

### C4 — Opaque locals in long scopes

**POLISH · MECHANICAL · blast radius: 3 files, 0 checks**

The genuine instances, all inside functions over 100 code lines:

- `src/gen/emit_vm.c:9220-9222` — `long long a` and `long long b` holding the
  frame-derived and trail-derived subject ceilings, then
  `ceiling = (a && b) ? (a < b ? a : b) : (a ? a : b);`. Two unexplained
  single letters in the single longest function in the tree, in an expression
  whose whole content is *which* of them is which. `frames_ceiling` /
  `trail_ceiling` costs nothing and removes the need to read `vm_ceiling`'s
  arguments to decode the line.
- `src/gen/emit_vm.c:8626` `bool *mk`, `:8794` `bool *nn` — arena arrays
  whose meaning is a scroll away.
- `src/core/compile.c:1611` `int fk = 0;`
- `src/parse/rxt_source.c:2126-2127` `nc` / `nv` (new capacity / new vector).

That is the whole list worth filing. See **P1** in §4 for the much larger set
this lens deliberately did NOT file.

---

## 2. FINDINGS — ARCHAEOLOGY (lens 7)

### A1 — The `abi` change log lives in THREE independently written homes, none of them complete, and the one in the code is eight events behind

**CORRECTNESS-RISK (documentation-of-contract) · LOCAL · blast radius: 2 files, 1 check message**

This is the finding. It is also the answer to lens 7's charter question, and
the answer is not "move the block to the docs" — the docs home already exists
and already disagrees.

`emit_info_def` (`src/gen/emit_dfa.c:1470-2282`) is 104 code lines inside an
813-line span. Of that span, **`:1534-1964` — 431 consecutive comment
lines — is a serial change log of 18 dated `abi` bump narratives**, sitting
above one line of code:

```c
sb_puts(c,   "    .abi = 26,\n");
```

The same change log exists twice more:

| home | transitions named | complete? |
|---|---|---|
| `src/gen/emit_dfa.c:1534-1964` (the code comment) | 16 | **no — missing 7→8, 10→11, 16→17, 17→18, 18→19, 19→20, 20→21, 21→22** |
| `tests/codegen/run_codegen_tests.sh:2795` (one 11,861-character failure-message string) | 22 | **no — missing 20→21, 21→22** |
| `src/gen/CLAUDE.md` (per-milestone `##` sections) | partial; is the ONLY home for 16→17 and 17→18 | no |

**20→21 and 21→22 are recorded nowhere in the tree at all.**

Textual overlap between the code comment and the shell message is **6 shared
8-grams out of 1,799** — they are not copies of each other, they are two
independently authored narratives of one 24-event sequence, drifting
separately. The comment's ordering is also non-monotone: `abi 8 -> 9` sits
between `3 -> 4` and `4 -> 5` (`:1559`, between `:1547` and `:1567`), and
`15 -> 16` is followed by `22 -> 23`.

**Why this is CORRECTNESS-RISK and not POLISH.** D76/D94's ritual makes the
abi number's reader set the thing a bump must sweep, and `battriage_report.md`
(2026-09-15) already found one reader class the grep-for-the-old-digit sweep
structurally cannot reach. A maintainer performing that ritual reads the
comment beside `.abi = 26` as the record of what the number means, and that
record is missing a third of its events — including `[ENG-ISL]`'s 17→18, the
first bump that moved the VM program region and therefore the one that
changed `run_recursion_identity.sh`'s comparison (A) from an allowance into
an IFF. The comment beside the constant does not know that happened.

**A1 (admissibility) check.** D76 requires a bump to carry its re-pin and its
spec hunk; it does not require a narrative beside the constant, and no D-row,
design-note section or panel disposition mandates this block. `docs/dev/
decisions.md` has 106 D-rows and none governs in-code change history
(grepped). The block is convention, not ruling.

**Suggestion, and it is deliberately not "delete it".** Three parts:

1. **One home, and it is `docs/spec/match_api.md` §6.3** — the abi number is a
   caller-observable contract, so D80 already puts its history in the spec
   tier. Move the per-event narratives there as a versioned table.
2. **The code keeps ~8 lines**: what `abi` means, the D76/D94 ritual in one
   sentence, the current value's own event, and a pointer. That is the
   charter's art applied literally — the invariant and the
   why-not-the-alternative stay, the history goes.
3. **The check message at `run_codegen_tests.sh:2795` becomes one sentence
   plus the same pointer.** An 11,861-character failure message is not a
   diagnostic; nobody reads it when the check fires, and its only function
   today is to be the most complete of the three copies, which is an accident.

Because the three copies disagree, **reconciliation is a prerequisite to the
move, not a by-product of it** — and reconciling them will need `git log` on
`.abi`, since 20→21 and 21→22 have no written record anywhere.

### A2 — A superseded claim left standing in the present tense, corrected fifteen lines below

**MAINTAINABILITY · MECHANICAL · blast radius: 1 file, 0 checks**

`src/opt/select_engine.c:496-516`. The first paragraph:

> *"[M6.4.2] THE FREE DISCHARGE runs ONCE, before the analysis loop — NOT as a
> registered `discharge` hook."*

The paragraph fifteen lines below it:

> *"[DD-14 wave G] IT NO LONGER RUNS *HERE*. It is `src/core/compile.c`'s own
> line now…"*

Both paragraphs are correct about their own era and the first is stated
without qualification. A reader who stops at the paragraph break — which is
where a reader stops — leaves with a false belief about where a pass runs, in
the file whose pass ordering is the thing most likely to be got wrong.

**This is one instance and not a class, which is the useful half of the
finding.** Scanned tree-wide, 48 comment blocks carry a retraction marker ≥12
lines into the block. **47 of the 48 mark the superseded text as superseded
in the sentence that carries it** — `src/ir/nfa.c:16` (*"THAT LAST CLAUSE IS
NO LONGER TRUE ON ITS OWN"*), `src/parse/mod_lookaround.c:208` (*"This comment
used to say…"*), `src/core/internal.h:1818` (*"It used to read…"*),
`src/gen/emit_dfa.c:444` (*"IT USED TO BE THE CONSTANT 1 ON THE DFA PATH, and
the comment that said so…"*). The house discipline is correction-in-place and
it is working; this is the one site where the correction was appended below
the claim instead of attached to it.

**Suggestion.** Attach the correction: open the [M6.4.2] paragraph with
"Until [DD-14] wave G, …" or move the wave-G paragraph above it. One edit.

### A3 — `RECALIBRATED` provenance stacked above generated values

**POLISH · MECHANICAL · blast radius: 1 file, 0 checks**

`src/gen/emit_vm.c:69-116` is 48 comment lines above a `#define` +
`#include "core/limits.def"` pair that defines nothing the prose names — the
values moved to `limits.def` at `[LIM-1]`/D90, and `:100-116` says so
explicitly (*"This comment's own PROVENANCE PROSE is unchanged; only the
mechanical `= value,` lines moved"*). So the file carries the calibration
history of four constants it no longer declares, while `src/core/limits.def`
declares them.

The prose is genuinely valuable (the D19 128 KB arithmetic, the [M4.6a]
recalibration and the measured two-knobs discovery). It is in the wrong file.

**Suggestion.** Move `:69-99` to the four `limits.def` rows' own anchors —
`limits.def` already carries an `anchor` field per row, which is the
mechanism for exactly this — and leave the `[LIM-1]` note plus a pointer.

---

## 3. LENS 7 DELIVERABLE — THE MIGRATION INVENTORY

Per-file, with the docs destination named and whether that home exists today.

### 3.1 MOVE (genuine change history; the whole remediable population)

| file | span | lines | kind | destination | home exists? |
|---|---|---|---|---|---|
| `src/gen/emit_dfa.c` | 1534-1964 | 431 | 18 serial `abi` bump narratives above `.abi = 26` | `docs/spec/match_api.md` §6.3 (the abi contract's own section) | **yes** — and it must absorb `run_codegen_tests.sh:2795` and `src/gen/CLAUDE.md`'s per-milestone sections in the same change, since all three disagree (finding A1) |
| `src/gen/emit_vm.c` | 69-99 | 31 | calibration history of four constants this file no longer declares | the four rows' `anchor` text in `src/core/limits.def` | **yes** (the `anchor` field is the mechanism) |
| `src/core/internal.h` | 1741-1771 | 31 | `ESEL_*` value-addition log ([OPT-4] → [OPT-4.1] → [OPT-4.2]) | `docs/spec/match_api.md` §6.3's `_ENGINE_SEL` token table | **yes** |

**Total: 493 comment lines, three blocks, two destinations, both existing.**
That is the entire lens-7 move list, and its smallness is the measured
result, not a sampling artefact — the scan ran over all 47 files.

### 3.2 STRIP THE CLAUSE, KEEP THE PARAGRAPH (no docs destination needed)

One site: **A2** above (`src/opt/select_engine.c:496`). The fix is a
conjunction, not a migration.

### 3.3 STAYS — and the reason is the charter's own art

The blocks a coarse date-grep flags and that must NOT move. I read each of
these in full:

| file:span | lines | why it stays |
|---|---|---|
| `src/gen/emit_vm.c:6004-6248` | 245 | The lookaround lowering: the positive/negative/non-atomic emitted shapes, three named invariants each with the line that makes them true, and the measured cells that discriminate them (`(?!(a)x)(a)` on `"ab"`). Invariant + why-not-the-alternative, verbatim the charter's "stays" class. |
| `src/gen/emit_vm.c:1-55` | 55 | The no-interpreter architecture constraint and the five decisions the emitted shape encodes. The charter's own cited example — it is not a change-history preamble. |
| `src/parse/registry.c:1-114` | 114 | Why the registry exists (the 2026-08-09 `\v` two-homes bug), the four doorways, and the measured base-tier lookup cost that *replaced a wrong claim*. The dates are evidence citations under A5, not history. |
| `src/core/limits.h:45-338`, `:364-671` | 602 | D26's three provenance tiers spelled out per constant, each with the probe that measured it (`R8/C2-9`: 638 probes, two transitions, both at 129). Deleting the dates deletes the evidence. |
| `src/parse/syntax_dump.c:1089-1191` | 103 | Why `--explain` is a doorway call and not a column read, including the refutation (R10/C4-1: swapping two rows' modules left every assertion green). A panel citation carrying a live check-design argument. |
| `src/core/internal.h:1780-1853` | 73 | The `ESEL_*` semantics, the K35 argument for each value's separateness, and the three-rung stamp table. Its *log* half is §3.1's third row; this half stays. |
| `src/ir/dfa.c:1-102` | 102 | The wave A-E class-axis derivation, which is the machine's structure and not its history. |

**The measurement that decides this, and it corrects a hypothesis I started
with.** I expected these blocks to be near-duplicates of the per-directory
`CLAUDE.md` files, making them free to delete. Measured at 9-word shingles:

| code comments | vs | shared | % of the code comments |
|---|---|---|---|
| `src/gen/emit_vm.c` | `src/gen/CLAUDE.md` | 833 / 62,030 | 1.3% |
| `src/gen/emit_dfa.c` | `src/gen/CLAUDE.md` | 771 / 39,712 | 1.9% |
| `src/core/internal.h` | `src/core/CLAUDE.md` | 300 / 40,913 | 0.7% |
| `src/opt/select_engine.c` | `src/opt/CLAUDE.md` | 283 / 7,685 | 3.7% |
| `src/parse/parse.c` | `src/parse/CLAUDE.md` | 82 / 11,641 | 0.7% |

**Verbatim duplication is 0.7-3.7%.** The `CLAUDE.md` files *paraphrase* the
same events at a different altitude rather than copying them, so "it is
already in the docs" is false for essentially all of this text, and a lens-7
proposal built on that premise would have deleted unique content. The one
place the paraphrase relationship *does* become a real three-way divergence is
the abi log (A1), and that is precisely why A1 is the finding and the rest is
not.

---

## 4. A3 ANNEX — CHECK COUPLING (what a comment edit re-aims)

Grepped, not assumed. Anything touching these sites carries its re-aim.

**(i) 27 of the 261 sabotage rows have comment text inside `SAB_BEFORE`.**
Editing a comment *inside* one of those anchor regions breaks the row's
text match. By file:

- `src/gen/emit_vm.c` — S39, S63, S85, S88, S90, S100, S132, S141, S169
- `src/gen/emit_dfa.c` — S07, S218, S219, S220, S227
- `src/parse/mod_uprops.c` — S33, S35
- `src/opt/possessify.c` — S84 · `src/opt/scanedge.c` — S213
- `src/opt/callgraph.c` — S175 · `src/opt/mrl.c` — S-U4
- `src/opt/lower_enc.c` — S-U7 · `src/ir/nfa.c` — S12
- `src/parse/mod_lookaround.c` — S136
- `src/gen/enc/enc_byte.c` — S233 · `src/gen/enc/enc_utf8.c` — S-U5

**None of the three §3.1 move-blocks is inside any of these anchors.**
Verified by locating each `emit_dfa.c` anchor's first line in the file:
S218 `:5320`, S220 `:5322`, S219 `:5325`, S227 `:5983`, S07 `:6154` — all
well above `emit_info_def`'s `:1534-1964`, and none inside `emit_vm.c:69-99`
or `internal.h:1741-1771` either. **So findings A1, A2 and A3 stale zero
sabotage rows.**

**(i-b) One anchor binds an IDENTIFIER this report proposes renaming:** S82
on `gseed` (see C3's carve-out). That is the only such collision across C1-C4;
it is the reason the identifier half of the anchors was grepped separately
from the comment-text half.

**(ii) Two checks grep COMMENT TEXT in `src/` as a needle:**

- `tests/codegen/run_search_pinned.sh:632` — `grep -q "P0 routing "` into
  `src/gen/emit_dfa.c`
- `tests/codegen/run_search_pinned.sh:633` — `grep -q 'liveness conjunct
  should'` into the same file

Both phrases live in `dfa_search_start_of`'s predicate comments, not in any
block this report proposes touching. Anyone rewording either sentence must
move the needle in the same change. (The other four `grep -q … src/…` sites
across `tests/` — `run_backref_identity.sh:80`,
`run_atomic_identity.sh:105`, `run_lookaround_identity.sh:221`,
`run_search_pinned.sh:631/634` and `S223`'s reach probe — match
*identifiers*, not prose, and are unaffected by comment edits.)

**(iii) `tests/codegen/run_codegen_tests.sh:2795`** — the 11,861-character
abi failure message. Not a needle; it is finding A1's third copy and moves
with it.

**(iv) C1, C2, C4, A2, A3 stale nothing; C3 stales exactly one row (S82).**
Header insertion, banner placement and the C4 renames touch no anchor and no
needle. C3's `gseed` rename is the single exception, priced at its row above.

---

## 5. PROBED-AND-HELD

Negative results with the evidence, so this ground is not re-covered.

**P1 — Names are, with the four exceptions in C4, good. Do not gold-plate.**
Function names across all 860 rows are consistently module-prefixed with
readable stems (`vm_`, `cg_`, `rd_`, `pss_`, `clo_`, `cls_`, `dfa_`, `p_`),
and the single-letter locals that dominate the emitters — `c` (the C string
buffer), `d` (the `Dfa`), `p` (the prefix), `b` (a `StrBuf`), `v` (the `Vm`),
`st` (a state), `r` (a row) — are a **consistent house convention applied
identically across `emit_dfa.c`, `emit_vm.c` and `rxt_source.c`**. Renaming
them would cost thousands of lines of diff, buy nothing a reader of two files
does not already have, and is exactly the violence lens 11's own warning
names. The handful of genuinely opaque ones are C4's four; there is no fifth
worth the diff. A short-name scan over the twelve longest functions produced
178 declarations and **four** findings.

**P2 — The correction-in-place discipline is honest at 47 of 48 sites.**
Every comment block ≥12 lines whose retraction marker sits ≥12 lines in was
enumerated (48 blocks). Only `select_engine.c:496` (A2) leaves the superseded
claim unmarked. This is a working practice, not a defect class, and the
review should say so rather than filing 48 findings.

**P3 — The 56% comment ratio is not itself a finding.** Per-file:
`src/core/limits.h` 94.7%, `lib/pcrec.h` 83.3%, `src/core/internal.h` 76.6%,
`src/opt/select_engine.c` 76.0%, `src/gen/emit_vm.c` 55.6%. For a compiler
whose emitted text *is* its product and whose comments carry the measured
evidence for each emitted shape, this is a deliberate posture, visibly
consistent, and the charter's art puts almost all of it in the "stays" column
(§3.3). Filing "too many comments" would be a taste claim with no measurement
behind it.

**P4 — Structural layout is sound.** Function ordering follows
helpers-then-user in every file sampled; `#include` blocks are uniform
(system, then `core/internal.h`, then module headers) across all 47 files;
no file mixes declarations and definitions in a way that hurts navigation.
Lens 6 owns the dependency question and this lens found nothing to hand it.

**P5 — No false function header found.** Every one of the 42 top-ranked
functions' headers that exists was read against its body; all describe what
the function currently does. The truthfulness problem in this tree is in the
*interior* prose of two blocks (A1's incomplete log, A2's standing claim), not
in headers. The charter asked for headers "audited for presence and
truthfulness" — presence is C1, truthfulness holds.

---

## 6. WHERE THE LENGTH-RANKED SWEEP STOPPED (ADDENDUM 2)

Stated because the ratification requires it — no silent caps.

- **Whole population (860 functions), programmatically:** header-presence
  count (C1's table), short-local declaration scan, and the archaeology block
  scan (all comment blocks in all 47 files, three separate classifiers).
- **Read in full, top-down by `code_lines`:** the top 42 rows of
  `function_census.tsv` (778 → 77 code lines) for the header audit; the
  bodies of `pcrec_emit_vm`, `emit_attempt`, `pcrec_select_engine`,
  `emit_info_def` and `vm_look_behind` for naming and interior prose.
- **Read in full, by comment mass:** the top 12 blocks by span, plus every
  block in §3.1 and §3.3.
- **NOT reviewed:** the 818 functions below rank 42 by code lines were covered
  only by the programmatic passes, not read. `src/parse/rxt_source.c`
  (4,038 lines, 2,499 code — the largest non-emitter file and the second
  longest function in the tree) was read only around
  `pcrec_rxt_source_parse`'s entry; its 46 short-named locals were counted,
  not judged. `src/parse/registry.c`'s 32 comment blocks were sampled at the
  preamble only.
- **Trigger for a second pass** (the charter's own): a second pass over
  `rxt_source.c` and `registry.c` would be the highest-value continuation, and
  it is a *naming* pass, not an archaeology one — §3.1 is complete and closed.

---

## 7. SUGGESTED WAVE ORDER (input to the manager's synthesis)

MECHANICAL-and-safe first, per A4.

1. **C1 + C2** — 43 function headers, zero checks staled, no behaviour. The
   pre-tour cleanup, and the one that most changes how the tree reads.
2. **A2 + A3** — two comment edits, zero checks staled.
3. **C3 + C4** — 6 + 4 local renames in 3 files; one sabotage re-aim (S82),
   which per BOILERPLATE needs its intent re-verified rather than its text
   patched.
4. **A1** — the abi log. LOCAL effort but it is a **reconciliation** before it
   is a move: three disagreeing sources, two transitions (20→21, 21→22)
   recorded nowhere, and a D80 spec hunk in the same change. It should not
   ride wave 1, and it should not be given to a lane that has not been told
   the three copies disagree.
