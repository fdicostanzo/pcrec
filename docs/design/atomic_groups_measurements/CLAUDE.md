# docs/design/atomic_groups_measurements — the [M6.4.1] design lane's instruments

The measurements behind `../atomic_groups_design.md` (module `atomic-groups`:
`(?>...)` and the possessive-quantifier spellings `*+` `++` `?+` `{n,m}+`).

**EVERY INSTRUMENT HERE READS A COMPILER THAT CANNOT COMPILE THE CONSTRUCT IT
MEASURES**, and that is this directory's distinguishing property — the opposite
of `../assertions_measurements/`, where some probes read the built construct and
some do not. pcrec refuses every atomic and possessive pattern today, so every
in-pcrec arm below works through a PROXY:

- the **atomicity-ERASED twin** (`(?>` → `(?:`, a two-byte edit), which is
  exactly the machine `src/ir/nfa.c` will build for the prefilter, so the proxy
  is the thing under test rather than a stand-in for it; and
- the **possessify verdict stamp** (`RX_VM_STRATS` bit `0x1`), which is the
  SHIPPED §2.2 analysis answering about a pattern it can compile.

A reader should check each entry's own tier (MEASURED / PROTOTYPE / STRUCTURAL)
rather than assuming the directory has one.

Kept separate from `../assertions_measurements/`, `../eng_brep_measurements/`
and their siblings for the reason those are separate from each other: never
confuse one lane's numbers with another's.

**REVISED AFTER R31 AND ITS FOCUSED RE-CHECK (2026-08-22).** Four of the
instruments below were REBUILT because the panel refuted what they measured
rather than what they reported, and SIX are new. Two of them
(`probe_lift_preference.py`, `probe_sref_consistency.sh`) were written for
findings against claims the FIRST REVISION introduced, and one
(`probe_registry_cost.sh`) was REWRITTEN because the re-check showed its search
population was the answer it already had. Each entry says which. The pattern is worth naming because
it repeated four times: **an instrument can produce a correct number about the
wrong population**, and every one of these was a zero that could not have been
anything else.

## The instruments, and what kind of evidence each produces

- **`probes/probe_atomic_semantics.py` — MEASURED, BOTH ORACLES. EXTENDED
  TWICE BY R31.** The design's whole interaction table (§6) as **109** cells, libpcre2 10.46
  against python3 3.14, with a per-cell AGREE column and a `BOTH-ERR` verdict
  for cells where both refuse (D26 tier 2 satisfied, tier 3 wording ours).
  Headline: **15 diverging cells of 109**. Eight are constructs python cannot
  express or parse; two are U9; and **five are new — R31 E6's family**: on a
  BRACE possessive (`{n}+`, `{n,m}+`, `{n,}+`) over a body whose iteration can
  end in two places, python cuts PER ITERATION and PCRE2 cuts at the GROUP
  EXIT, so python reports NO MATCH where PCRE2 matches. `*+` and `++` over the
  identical body AGREE, and those controls are in the section.
  **It also gained a `spelling_equivalence()` check**, because E6 showed RULE
  1's evidence was measured on the one family that could not refute it (every
  section-B row has body `a`): 18 pairs, 47 cells, **28 of them
  NON-UNIQUE-BODY**, 0 disagreeing, and the check FAILS if the non-unique count
  is zero.
  Its own first run reported three FALSE divergences because `pcre2_match`
  returns "one more than the highest pair that has been SET", so a pattern whose
  LAST group is unset comes back with a SHORTER tuple than python's — the
  padding normalisation and the reason for it are in the file. **R31 D1/C7: the
  design's PROSE went on saying "13 of 95" after the probe was fixed to say 10.
  A corrected instrument does not correct the document that quoted it.**
- **`probes/probe_uncut_superset.py` — MEASURED, libpcre2, SWEEP.** The hybrid
  hazard (§4) over a generated family rather than three hand-picked cells: 1,260
  patterns × 14 subjects, each with its two-byte-edit uncut twin. Headline:
  sound REJECTION and the START lower bound hold at **0 violations**; the END is
  **REFUTED at 122**, which is what makes the prefilter's span end unusable as
  the emitted MRL ceiling. Builds the twin by TEXT SUBSTITUTION on purpose — a
  hand-written twin can differ in something other than the atomicity, which
  makes every divergence unattributable. It deliberately EXCLUDES the possessive
  suffix spellings, because the suffix can also change what the PRECEDING item
  may do (U9) and mixing the two would make somebody else's quirk look like a
  prefilter finding.
- **`probes/probe_ceiling_shape.sh` — STRUCTURAL, in-pcrec.** The other half of
  §4: that today's emitter really does feed `window[0][1]` to the VM as a
  pruning ceiling, shown in emitted C from a pattern the compiler can build
  TODAY. **Its two negative arms are the point**: under `-fno-prefilter` and
  under `--engine=vm` the same pattern emits `window_end = subject_length` and
  stamps `RX_VM_PRUNE_CEILING "subject-end"`. A probe printing only the positive
  arm could not tell a reader whether it had found a SHAPE or a CONSTANT.
- **`probes/cut_proto.c` + `probes/probe_cut_trail.py` — PROTOTYPE, checked
  against libpcre2. NOW SELF-SABOTAGING (R31 C6).** Atomic patterns hand-lowered
  onto the emitted VM's own machinery, with `RX_TRAIL`/`RX_SET`/`RX_PUSH`/
  `RX_CUT` and the fail label copied VERBATIM from a real artifact, so a
  divergence is a divergence in the LOWERING and not in the substrate.
  **C6 refuted its discrimination column**: a critic injected a trail-rewinding
  cut and found 2 of 14 rows went red — both labelled VACUOUS — while all nine
  advertised non-vacuous rows stayed green, because *cut-vs-uncut* and
  *trail-rewind-vs-not* are DIFFERENT AXES. `cut_proto.c` now carries a
  `-DCUT_REWINDS_TRAIL` arm, the driver builds BOTH every run and diffs them
  row by row, and it FAILS if either column is zero. Headline: **17 rows, 0
  disagreeing, 10 cut-discriminating, 4 trail-discriminating** — and the
  corrected naming, which is the lesson: the trail invariant's failing
  direction is RETENTION (`(?>(a)|ab)`), not the outer-failure row the first
  revision named, because a cut that rewinds the trail gets UNDO trivially
  right.
- **`probes/probe_free_discharge.py` — MEASURED, in-pcrec on one arm and
  libpcre2 on the other.** The free discharge (§5.3): 1,764 patterns × 16
  subjects, verdict read off the shipped possessify pass via the twin's
  `RX_VM_STRATS`, truth read off libpcre2 for both spellings. Headline: **532
  positive-verdict patterns, 0 violations**; 834 of 1,232 negative-verdict
  patterns are rescues the discharge declines. **Prints four CONTROLS every
  run** — two that must diverge with a negative verdict, one that must not with
  a positive one, and U9's witness — because a zero from an instrument that
  cannot fire is worth nothing, which is this project's most-repeated finding.
- **`probes/probe_possessify_under_cut.py` — MEASURED, both arms, and it tests a
  claim nobody in this tree has tested.** Whether possessify's §2.2 verdict,
  validated on a corpus that could not contain a cut, stays sound once cuts
  exist. 48,000 cells over FOUR positions of the quantifier relative to the cut
  (inside the body, wrapping the group, before it, after it), because the hole
  in the subset argument is position-dependent. Headline: **0 violations**, with
  a **non-vacuity counter of 202** so the zero is not an artefact of a family
  where possessification never matters.
- **`probes/probe_premises.sh` — MEASURED, in-pcrec.** The design's §1 premise
  table and §6.3's error-shape table as ONE re-runnable script, because a
  premise whose evidence is a shell command quoted in prose is asserted rather
  than verified (R30 M8's finding, one document over). Headline: `(?>` refuses
  at offset 0 from the REGISTRY; the four possessive spellings refuse at the
  `+`'s own offset from `parse.c:987-988`, OUTSIDE it; **`a{,2}b` COMPILES and
  matches `"aab"` at `0 3`**, so pcrec's base tier already reads `{,n}` as a
  quantifier and this module must not touch it; and `a*?+` refuses today with
  `multiple quantifiers on the same item`. It deliberately includes `a*++`,
  whose message CHANGES when the module lands, so a reject-suite author has the
  before-picture without reconstructing it.
- **`probes/probe_cut_dispatch.sh` — MEASURED, in-pcrec. NEW (R31 E2/E4/C3),
  EXTENDED by r31eng's final re-check with §2b, the RUNG'S OWN GATE.**
  Three questions in one instrument because they are one question: which
  emitted code actually cuts. It drives a possessified pattern down each of
  `vm_rep`'s FIVE dispatch paths and reports what the artifact contains.
  Headlines: **the CURSOR rung's possessive path is FRAMELESS** (0 cuts, and
  that is correct — nothing was pushed); **the REVDET rung cuts in a SECOND
  SPELLING** (`run->resume_depth = <p>_rvN_frame_mark`, 0 `RX_CUT(` call
  sites) — a fact THIS LANE found while fixing E2, which the panel did not
  report and which `vm_cut`'s own header records a probe getting wrong once
  before; and **the COUNTER rung's UNBOUNDED arm emits no cut at all** (K29),
  which gives C3 its failing direction on a REAL SHIPPED ARTIFACT with no
  sabotage: `grep -q RX_CUT` matches the unconditional `#define` on an artifact
  that emits no cut. **§2b sweeps for a body that is revdet-APPROVED and
  possessify-REJECTED at an EXACT count** — the cell where `vm_rev_canmove`'s
  "there is one exit" clause would be false — over 14 bodies × 3 counts, and
  finds NONE, so RULE 3's condition (d) ships with a measured-empty population
  and the sweep is what a reader re-runs when either gate moves. It also names
  the NEIGHBOURING cell that is NOT empty (`(?:ab|cd){2,4}c`, a different
  clause, covered by `vm_cuts()`), because an empty sweep beside a non-empty
  neighbour is the pair that shows the sweep was aimed at the right thing.

**EVERY PROBE HERE RESOLVES `pcrec` FROM ITS OWN LOCATION**, not from the
caller's working directory (r31eng final). A bare relative `build/pcrec` makes
a probe's answer depend on where it was invoked, silently measuring a different
compiler or none; all eight had that shape and all were fixed together.
`$PCREC` / `$1` still override, and `archive.sh` now stamps the RUN DIRECTORY
so which tree produced a number is carried rather than assumed.
- **`probes/probe_puc_targeted.py` — MEASURED, both arms. NEW (R31 C2).**
  `probe_possessify_under_cut.py`'s successor on the axis that matters. C2
  refuted that probe's non-vacuity counter (202) as evidence: it counts
  possessive-vs-plain with the VERDICT IGNORED, and the refutable cell needs
  the verdict POSITIVE *and* the cut BITING — measured in the old generator at
  59 cells. This one generates from atomic groups chosen BECAUSE they bite and
  bodies chosen BECAUSE §2.2 accepts them: **10,504 refutable cells, 0
  violations**, with per-position FLOORS the run FAILS if it cannot reach.
  Two things it had to learn are kept in the file: the obvious "Q inside the
  body" shape produces 1,050 positive verdicts, 672 biting patterns and **0
  with both** (the lower-priority branch has to out-reach the quantified one),
  and **"Q wrapping the atomic group" is empty BY CONSTRUCTION** — 0 positive
  verdicts of 8,820, because §2.2 reads the atomic group transparently and
  `a|ab` is not prefix-free. That position gets an ASSERTION instead of a
  floor, and the assertion is also the design's incompleteness finding.
- **`probes/probe_lift_preference.py` — MEASURED, both arms. NEW (R31 focused
  re-check, N1).** The possessive-rung lift's SECOND carve-out, measured the
  way the first one was. Part A (in-pcrec): lazy quantifiers are possessified
  today on **all six** of `vm_rep`'s dispatch paths, not only the cursor rung
  the re-check measured — so the preference collapse is relied on across the
  whole ladder. Part B (both oracles): the lift emits the GREEDY possessive
  shape, so its answer is readable off libpcre2 by compiling that spelling —
  **7 of 8 lift-eligible rows MISCOMPILE**, libpcre2 and python agreeing on
  every correct answer, and three of them are the design's own §6 cells 14-16.
  Its CONTROL is `(?>a*?b)c`, whose `A_ATOMIC` child is an `A_CAT` so the lift
  never applies and the row must agree; the probe FAILS if the control breaks,
  and equally if NOTHING miscompiles (which would refute N1 rather than confirm
  the fix).
- **`probes/probe_sref_consistency.sh` — MEASURED, document-internal. NEW
  (r31chk re-check N3).** Every `SNN` sabotage citation outside §11.4's table,
  looked up in the table and printed NEXT TO the citing sentence so a reader
  can judge aptness — which a membership test cannot. It exists because C4's
  renumbering left five stale references, one of them naming a CODEGEN row as
  what a CORPUS driver would catch. **Its own first run reported 0 mentions
  and 9 undefined rows** — the id list was newline-separated and the `case`
  membership test matched nothing — caught only because the probe refuses to
  print a verdict when it checked nothing. The note stays in the file.
- **`probes/probe_registry_cost.sh` — MEASURED, in-pcrec. REWRITTEN AS A SWEEP
  (r31chk re-check N1); the first version was the defect it was written to
  prevent.** It carried a table headed "MEASURED rather than recalled" and
  greped four files — the four the author already knew about. A grep over the
  answer you already have is a transcript. It now sweeps `src/`, `cli/` and
  `tests/` with no curated list, classifying hits as EXACT equalities (go red),
  FLOORS (pass), kind lists and doorway-routing SET assertions. Headline: **nine
  sites across six files where the re-check named seven** — three EXACT
  equalities (`run_reject_tests.sh:1713` `-eq 99`, `registry_check.c:444`,
  `compliance_section.py:391`), a THIRD hardcoded `kinds[]` array
  (`registry_check.c:1696`) both earlier enumerations missed, seven `RegKind`
  switches, and the REGMANIFEST's two PROSE pins. It closes by telling the
  reader that a tenth site is its next correction, not a surprise.
  What §7.4's four rows actually cost, site by site with line numbers, because
  the first revision said the built-status derivation was "simply a compile of
  the syntax string" and it is `doorway_route` + `doorway_call` over four
  recognised prefixes. Headline: **`--explain 'a*+'` says "no construct
  matches"**, so such a row derives to `BUILT_DEFECT`. It also corrects the
  finding it implements: C8 says "both `all_kinds[]` arrays"; measured, it is
  ONE array with TWO use sites plus a SEPARATE array in `enabled.c`.
- **`probes/probe_premises.sh` — MEASURED, in-pcrec.** The design's §1 premise
  table and §6.3's error-shape table as ONE re-runnable script, because a
  premise whose evidence is a shell command quoted in prose is asserted rather
  than verified (R30 M8's finding, one document over). Headline: `(?>` refuses
  at offset 0 from the REGISTRY; the possessive spellings refuse at the `+`'s
  own offset from `parse.c:987-988`, OUTSIDE it; **`a{,2}b` COMPILES and
  matches `"aab"` at `0 3`**; `a*?+` refuses today with `multiple quantifiers
  on the same item`. It deliberately includes `a*++`, whose message CHANGES
  when the module lands.
- **`probes/probe_rk_alarm.sh` — MEASURED, self-restoring.** What a fifth
  `RegKind` costs (§7.3), on `../assertions_measurements/probes/
  probe_wswitch_alarm.sh`'s shape one enum over. Headline: **0 `-Wswitch`
  diagnostics over 28 files** — the OPPOSITE of `AKind`'s 15, and the fact that
  decides §7.4's ruling. Restores the header under an EXIT trap that VERIFIES
  the restore, and refuses to report zero when it compiled nothing. **Its own
  first run died silently on `set -e` plus an assignment from a failing `ls`** —
  the identical defect `../assertions_measurements/CLAUDE.md` records for
  `probe_kreset_identity.sh`, reproduced by a lane that had read that entry, and
  the note stays in the file for the next one.
- **`probes/archive.sh` — not a probe, the ARCHIVER.** Every file in `out/` is
  written by it. **R30 M7's rule, inherited: the archiver is the ONLY writer of
  `out/`.** A hand edit there is a red line, not a formatting choice.

The `-Wswitch` question for a new `AKind` is answered by **re-running
`../assertions_measurements/probes/probe_wswitch_alarm.sh`**, not by a second
instrument — a lane that rebuilds the probe it is checking cannot detect that
the original moved. Its output is archived here as `out/wswitch_alarm_rerun.txt`
and the design cites it as a re-run.

`probes/pcre2_ctypes.py` is NOT copied here: every probe that needs libpcre2
imports `../../eng_brep_measurements/probes/pcre2_ctypes.py` by path, on
`../assertions_measurements/`'s precedent (one binding, one place it can be
wrong).

## `out/`

Archived probe OUTPUT, written ONLY by `probes/archive.sh`, which stamps one
provenance header on every file (probe path and args, the probe's own
last-change commit, the run's commit/branch, whether the tree was clean, date,
and the python3/libpcre2/gcc versions). Evidence for the [M6.4.1] panel, never
an oracle — no check in `make test` reads these files. See `out/CLAUDE.md`.

Maintenance: update this file when probes or outputs are added/removed or their
roles change.
