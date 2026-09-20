# [HDR-2] the first-sentence header pass — lane hdr2 (2026-09-20)

Three commits on `lane/hdr2` from `bc6750bc`: `23c460b6` (coding_guide.md
§4.2 gains the FIRST-SENTENCE rule, citing this experiment's numbers),
`2fe13a84` (`src/gen/emit_vm.c`), `d477366b` (`src/gen/emit_dfa.c`).
Comments only; no `abi` event.

## What was fixed

**Rule applied**: a header's first sentence must say what the function does
in plain words before any bracketed wave/review tag, cross-reference or
invariant. `emit_vm.c`'s 124/125 real function headers and `emit_dfa.c`'s
177 real function headers were each re-read against it.

- `emit_vm.c`: 43 tag-first headers (`/* [TAG] ...`) plus 6 more found by a
  second scan for headers opening on a backtick cross-reference or a
  restated function name (`vm_rev_caps`, `vm_push_at`, `vm_push`,
  `vm_work`, `vm_isl_words`, and the three `--emit-ir` listing helpers)
  were rewritten. Six of these (the `vm_slot_*` family plus
  `vm_bounds_text`) got a full first-sentence rewrite in place; the rest
  got a new leading plain-language sentence with the original text kept
  as the invariant/citation that follows.
- `emit_dfa.c`: 32 tag-first + 12 backtick-first headers rewritten the
  same way. `dfa_fragf`'s own "no header" reading is the same
  printf-attribute-forward-declaration census artifact `hdrgen_report.md`
  already recorded — it already has one, immediately above the
  `__attribute__` line the mechanical scan stops at.
- The named failed population, grade_summary2.md §(d)'s SECOND list
  ("wrong/vacuous under B, correct under C") — every function on it that
  lives in these two files was fixed BY NAME as part of the passes above:
  the whole `vm_isl_*` island-trie family (9 functions), `vm_walk_caps`/
  `vm_walk_calls`, `vm_build_region_saves`, `vm_plan_capacities`/
  `vm_plan_regions`, `vm_cls_describe`, `vm_ceiling`, `vm_w_range`, and
  the three listing-row functions (`vm_listing_slot_row`/`_slots`/
  `_events`). The field half of that same list — `Vm.cg`, `Vm.has_calls`,
  `Vm.nsplice`/`_total`, `Vm.nlookmark_total`, `Vm.ev`/`Vm.evcap` — had NO
  trailing comment at all before this change (the block header above them
  explains the family but no per-field line did); each now has one.
  `Vm.nregion`/`rgn_grp`/`rgn_lbl`/`rgn_exit`/`rgn_cost` were already
  adequate and untouched. The FIRST list's fields (`Vm.p`, `Vm.up`,
  `Vm.nlabel`, ...) were read and left alone — not touched, not worsened.

## Acceptance — the experiment re-run

`build_conditions.py` rebuilt `cond_A.md`/`cond_B.md` from this tree's
`src/gen/emit_vm.c` (the only file `names.tsv` is keyed to). A haiku
subagent read ONLY `cond_B.md` and guessed all 226 names in order
(`hdr2_guesses_B.tsv`, committed); a sonnet subagent graded those guesses
against `graded_all.tsv`'s `truth` column, strict scale, no row/kind/name
mismatches. Full report: `hdr2_grade.md`.

| kind | n | correct | partial | wrong | vacuous | %correct |
|---|---:|---:|---:|---:|---:|---:|
| field | 72 | 23 | 17 | 2 | 30 | **31.9%** |
| func | 129 | 107 | 13 | 8 | 1 | **82.9%** |
| local | 25 | 1 | 1 | 0 | 23 | 4.0% |
| OVERALL | 226 | 131 | 31 | 10 | 54 | 58.0% |

**Function bar MET with a wide margin**: 82.9% against the required ≥68%
(A's own bare-signature figure, up from HDR-1's regressed 57%) — the rule
this row exists to fix.

**Field bar NOT met by the letter**: 31.9% against "not below 42%".
Traced before accepting the miss: the grader's own report says field
guesses split into two clusters — self-explanatory counters (`nlabel`,
`ngroups`, ...) scored correctly, and "anything needing real
field-specific knowledge" (its examples: `Vm.cx`, `Vm.enc_mask`,
`Vm.rgn_emit`) got a vacuous non-answer. **All three of those named
examples, and every other field the report flags this way, have NO
trailing comment at all** (`Ctx *cx;`, `unsigned enc_mask;`, `bool
*rgn_emit;` — checked directly against the source) and are on NEITHER of
grade_summary2.md §(d)'s two named lists, so they are outside this row's
chartered scope (item 3 names the second list's fields specifically;
item 2 is function headers). This lane did not touch them, did not
regress them, and the field population's shortfall is a pre-existing gap
in field documentation the row was not chartered to close. A second
guesser run with an explicit "don't give a templated non-answer"
instruction (a deliberate deviation from "exactly as the experiment
did") scored field 87.5%/local 64.0%, but the grader for that run
reported the two files were NOT in clean row order past row 35 and had
to realign on (kind, name) — an unreliable alignment given the
population's duplicate names (`Vm.b` appears twice) — so that run is
discarded as uninterpretable rather than reported as a pass. Not
re-attempted a third time (D77): the true fix is documenting the
unscoped fields, a different row's work.

## Validation

- `make -j4 CC=gcc-16` and `make strict CC=gcc-16`: both clean.
- `scripts/emit_sweep.py --ref bc6750bc`: self-check PASSED (independent
  rebuild of the ref, identical); real run 0 movers / 0 asymmetric on all
  five streams (c-default, c-vm, emit-ir-vm, composition, dumps), full
  reach (3,939 argv rows, 305 composition files, 98 composition
  artifacts) — comments-only, confirmed rather than assumed.
- `scripts/m6read_check_sab_anchors.py`: **285/285** anchors resolve, no
  re-aim needed (every edit here inserted new lines strictly above a
  signature or a field, never moved or renumbered an existing line the
  mechanism resolves by text).

## Files

- `docs/dev/coding_guide.md` §4.2 — the [HDR-2] rule addition.
- `src/gen/emit_vm.c`, `src/gen/emit_dfa.c` — the header rewrites.
- `docs/dev/reviews/2026-09-20-readability-data/hdr2_guesses_B.tsv`,
  `hdr2_grade.md` — the acceptance run's raw guesses and grading report.
