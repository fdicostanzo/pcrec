# possfin report: [ART-POSS-ARMS] S602, the census, the closing validation

Lane `possfin` (sonnet, follow-up/triage), branch `lane/possfin` from
`lane/posstri` aeae1964 (which contains `lane/possbuild` 070f29e4). Scope: the
pcrec worktree only. One stray write during the lane (a diff output into the
possbuild worktree's `build/`) was removed on the spot; nothing else outside
this worktree was touched.

## 1. S602: an equivalent mutant (class b), no `src/` defect

**Verdict.** `S602-poss-b-in-progress-recomputed` is UNDETECTED because the
mutant is observably equivalent. The row now says so: `SAB_EXPECT=UNDETECTED`
with its argument and `SAB_DOC_FIGURE` in the S219/S490 format. No `src/`
change, no K-entry.

**The experiment** (planted tree = `git archive HEAD` plus the row's
`SAB_BEFORE`->`SAB_AFTER`; a counting copy of both trees; scratch under
`build/fin/`, uncommitted):

1. *The witness never walks its cycle.* `(a\2\3)(b\1)(c\1)x+\1`: each group's
   text starts with a literal, so `text_first` stops before the reference.
   Counting `cap_group` computations (clean vs planted): 6 vs 130.
2. *A cycle that is walked is still not exponential.* Nullable-prefix
   witness `(a?\2\3)(b?\1)(c?\1)x+\1`: 3 vs 65 computations, max depth 2 vs
   64. `cap_group` memoizes (CF_DONE) the moment a group's first computation
   finishes, so the planted compiler descends one chain to
   `PCREC_MAX_POSS_REF_DEPTH`, unwinds, and every sibling then hits the memo.
   32 generated mutual-reference patterns, k = 2..40 groups, dense and sparse:
   the planted compiler does 62..124 extra computations (clean 2..78), an
   additive ~2 x depth, independent of branching. Wall time 0.00-0.03 s on
   both. The report's "explores 2^64 paths" was an unmeasured claim.
3. *No answer, artifact or census moves.* Planted artifacts are byte-identical
   to the clean ones (same `-o` basename) on the three witnesses and all 32
   generated patterns with zero diffs; the build census TSV
   (4,875 rows: marks, stamps, engines) is `cmp`-identical between the planted
   and clean compilers. That is the answer-level observable the row's suites
   (harness on `possessify.rxt`, exhaustive possdiff) read; the matrix's
   original ZERO CHECKS FAILED is the correct reading of it.
4. *No cost detector exists to point the row at.* Compile-side work has no
   counter in the tree, and the extra work is bounded by ~2 x depth, so
   building one for this row fails D77 (no build ahead of a measured need).

Also changed (text only, no line counts moved): the `possessify.rxt` cell
comment that claimed the compile "times out" now says what is true; the
`tests/mech/CLAUDE.md` S602 sentence. The old `(a\2\3)(b\1)(c\1)x+\1`
oracle cell stays (it is a valid no-match cell). No nullable-cycle oracle cell
was added: it would move the rxtsource/startset pins under posstri's running
re-validation, and (b) does not need one.

## 2. Census

`build_census.py` crashed in the chain only in `--diff` mode: the module
imported ARTREV_GEN (a census-mode input) at the top for both modes, and the
chain's `--diff` call did not set it. The census itself had run (rc=0, 16 s).
Fix: the three census-mode variables are required by `need()` (a refusal naming
the variable, never a default) and `--diff` reads two TSVs and needs none.
ARTREV_GEN is `docs/dev/optloop/artrev/gen` (holds `census.py`).

Re-run here against this tree's fresh `build/pcrec`
(`build/fin/census_build.tsv`, `census_diff.txt`):

- `--diff` vs `census_r21.tsv`: **0 DIFF** over the 4,132 rows in common;
  743 ONLY-IN-build, 0 ONLY-IN-proto. The 743 are corpus files added after the
  r21 census: `composition_d27.rxt` 666, `possessify.rxt` 68, `caseless_ucp.rxt` 9.
- vm movers (denied vs armed): bench 6, corpus 78 = 13 on the old population
  (matches the build report's expected 6 / 13) + 65 on the new files (50
  `composition_d27`, 15 `possessify`).
- **Default-route engine flips: 10 (all vm->dfa), all on new rows** (3
  `composition_d27.rxt`, 7 `possessify.rxt`), where the build report expected
  0 (it counted the old population: 0 of 4,132 still holds). Examples:
  `(?:a\.)++\B`, `\d++(?![\d.])`, `\w++(?:\b|)`, `(?>\w+)\b`. Cause measured:
  `-fno-poss-ctx-follow` alone flips each back to vm (RX_ENGINE_WHY "possessive
  quantifier"/"(?>...)"), `-fno-poss-bref-first` alone does not. These are
  user-written possessive/atomic quantifiers that arm A now discharges as no-ops
  before a context gate, so the pattern becomes DFA-expressible: an intended
  effect of arm A, on constructs the r21 population did not contain. Their
  answers are read by the composition run (possbuild's compo stage: 0
  divergences, both routes) and the possessify cells. **The manager should
  rule whether "0 flips" was an acceptance bar or a statement about the old
  population**; the data says the latter.

## 3. Validation (armed, not waited for)

`build/fin/chain.sh` (detached, waits on `.lift`): solo mech `S602`
(FATAL count and the `== mech run COMPLETE` trailer both recorded), then
`make -k -j16 -Otarget test-possessify test-codegen test-rxtsource`
(rxtsource added because the `.rxt` comment edit sits under its census; line
counts are unchanged). Stages and completion lines: `build/fin/STAGES`,
`build/fin/DONE`; logs `build/fin/mech.log`, `build/fin/tests.log`.

## STATE AT HANDOFF

- Tip: see the handback message (single commit chain on `lane/possfin`).
- Done and verified: S602 classification (experiments above); census run and
  diff (numbers above); S602 row edit syntax-checked (`bash -n`).
- OWED (armed): solo `S602` must read `UNDETECTED (EXPECTED)` with
  `harness:0fail` and `possdiff:0fail`, `reach:ok`; `test-possessify`,
  `test-codegen`, `test-rxtsource` must show no `*** [... test-` line (the
  darwin `nm` red does not apply on this box). Read:
  `grep STAGES`, `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/fin/tests.log`,
  `grep -E 'S602|UNEXPECTED|unexpected' build/fin/mech.log`, completion line
  `== mech run COMPLETE`.
- The `.lift` file is `worktrees/possfin/.lift`; `touch` it to start the chain.
