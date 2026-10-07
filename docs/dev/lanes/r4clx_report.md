# r4clx — R4c's Linux reds, triaged and fixed; RERUN mode (2026-10-06)

Lane r4clx (opus), branch `lane/r4clx` off the kit branch `lane/memfn-r4c`
at 71b5db5b. Input: the Linux verdict run of `memfn_r4c.sh` at 91f5b607 on
ubuntubudu (gcc 15.2): `R4C-LX-DONE gate=0 test=2 reds=1 mech=1 axes=0 c11=0
i2=1 i2arms=94`, logs in `worktrees/r4c-lx-results/` (read-only).

Commits: 118a8d8c (C4), 991e0484 (mech rows), ff2ee9be (script + I2 judge),
ef57b1ca (mech CLAUDE.md), this report's commit.

## Item 1: C4 red on Linux (test-memfn-arch). CONFIRMED.

Evidence: `test.log:6426-6443`. The scan was green (15 hits, all allowed).
Two plant controls failed: class 1 missed `ABM` and
`GCC_HAVE_SYNC_COMPARE_AND_SWAP_16`, class 2 missed `__ABM__` and
`__LAHF_SAHF__`. That was the only `*** [...test-` line (reds=1).

**The real cause is wider than four strings.** C4 planted an evenly-spaced
SAMPLE of 6 stems and 8 macros, so which words got tested depended on the
box. I checked the whole population. gcc's x86 set cannot be reached from
the Mac (no x86 gcc here), so clang's x86_64 target stands in for it, with
`-march=znver1` for `-march=native` (ubuntubudu is a Ryzen 5 1600). Over the
Linux flagsets plus x86-64-v4, the proxy declares 42 ISA macros. Over all
-march CPUs it declares 102 macros and 79 stems. The OLD regexes missed 55 of
those macros and 40 of the stems: `__SSSE3__` (class 2's `SSE` prefix never
saw `SSSE3`), bare `FMA`, `SHA`, `RDRND`, `SSE4A`, `ADX`, `CLZERO`, `MWAITX`,
`PRFCHW`, `__znver1__`, `__tune_znver1__`, and so on.
Reproduced on the Mac: the old check run against the proxy compiler goes red
the same way (`FAIL: class 1 ... ADX; RDRND; SSE4A`, `class 2 ... __ADX__;
__MWAITX__`).

**Fix** (`tests/memfn/arch_blind_check.py`):
- Class 1 is now one `ISA_NAMES` alternation, widened from that population:
  x86 feature names (abm, adx, lahf_sahf, clflushopt, clzero, mwaitx,
  prfchw, rdrnd, rdpid, evex512, gfni, vaes, movdiri, ... apx_f, movrs,
  user_msr), bare `fma`, `sse4a` and `3dnow`.
- Class 2 adds two derived branches:
  - `__…<any class-1 name or macro-only name>…`, so widening class 1 widens
    class 2 too;
  - the CPU-name macros (`__znver1`, `__tune_*`, the -march CPU list).
- **Macro-only names.** Three kinds of name are not class-1 words, because a
  case-insensitive word scan cannot tell them from prose:
  - English words (`serialize`);
  - two-letter acronyms (`kl`);
  - hash names (`sha`, `sha512`: the tree spells `sha256`/`<sha>` 100+
    times as a digest; first try measured 34 false groups).

  Class 2 catches them in macro form. `derive_plants` plants them in class 2
  only.
- **`__GCC_HAVE_SYNC_COMPARE_AND_SWAP_16` is EXCLUDED from the class-1
  stems, with the reason stated in the code.** It is gcc's portable atomics
  capability macro, not an ISA's name. The ISA it reflects, cmpxchg16b, is
  class 1's `cx16`. It stays a class-2 plant, and class 2 already matched
  it.
- Classes 1 and 2 now plant the WHOLE derived population instead of a
  sample. `-march=x86-64-v4` was added to the flagsets. Classes 3 and 4 keep
  their sample: the intrinsic population is thousands.

**Plants per class after the change:**

| box | class 1 | class 2 |
|---|---|---|
| Mac gcc-16 | 9 | 9 |
| x86 proxy (clang, Linux flagsets) | 36 | 42 |
| ubuntubudu gcc, expected | ~37 | ~43 |

On ubuntubudu, gcc adds `__ABM__`, which clang does not declare.

Spot-checks: 40 gcc-only x86 names that the proxy does not declare (AVX10,
AMX_*, APX_F, USER_MSR, MOVRS, SM3/4, SHA512, 3dNOW, k8, ...) all hit after
`movrs` and `user_?msr` were added.

**Mac proof:**
- `make test-memfn-arch CC=gcc-16`: checks passed 12, failed 0. The scan
  still shows 15 hits, all allowed, and no new tree hits.
- The same check against the x86 proxy: `class 1: 36/36`, `class 2: 42/42`.

**Residual:** gcc on the box may declare a macro that clang does not. The
Linux re-run is the proof. A miss there is a widening, which is the check
working as designed.

## Item 2: S518 UNREACHED. CONFIRMED; the witness was also unsafe in a second way, now fixed.

S518's reach probe is C4 on the clean tree. On Linux it exited 1 without
`PASS: class 1 (isa-name)` (`mech_S518.log`), so item 1's red caused the
UNREACHED. Item 1 fixes that.

**The witness design's real weakness was the opposite direction.** Arm
`memfnarch` scores the sabotaged tree's ABSOLUTE `checks failed:` count.
When the clean C4 is red, every memfnarch row reads DETECTED whatever its
plant does. On Linux, S519, S520, S521, S522 and S523 all read DETECTED
against a clean C4 that already had 2 failures, so those verdicts were
vacuous. A witness that asserts only its own class's PASS cannot see this.

**Fix:** every memfnarch row (S518-S523) adds `checks failed: 0` to its
SAB_REACH_EXPECT. S522 gains a SAB_REACH for it, because it had only a POP.
A box whose clean C4 is red now reads UNREACHED, which is true: the arm
cannot measure there. The dependence on the box's plants is the witness's
purpose, not a fragility. The same `checks failed: 0` line went into S526
and S527 (memfnforms). S524 and S525 were left alone, to keep the re-run
small; they are a candidate for the same line later.

**Mac proof:**
- S518 reads `reach:ok(2/2),memfnarch:1fail/11pass DETECTED`.
- S519, S520 and S521 read the same.
- S522 reads `reach:ok(1/1),memfnarch:1fail/12pass` (plus its POP).
- S523 reads `memfnarch:2fail/10pass`.
- All trailers are `unexpected: 0, undetected: 0, unreached: 0, anomalies: 0`.

## Item 3: S287 NOW DETECTED. CONFIRMED; flipped.

Linux showed `reach:ok(1/1),corpus:51fail/4pass NOW DETECTED`. Per r4ccore's
report §4, the kit re-derives maxk and `ofs_pred_of` refuses the compile on
a disagreement. S293 was always DETECTED (Linux `prechecks:54fail/266pass,
corpus:16fail/0pass`); its "handling" is a measured SAB_DOC_FIGURE plus a
header paragraph, and S287 now has the same.

**Changes:**
- `SAB_EXPECT=DETECTED`.
- A header paragraph explains the R4c mechanism. The ASan analysis is kept
  as history.
- SAB_DOC_FIGURE now holds the measured figure.
- tests/mech/CLAUDE.md's S287 row and its "second row" paragraph are
  rewritten to match.

**Mac proof:** `bash tests/mech/run_sabotage_matrix.sh S287` gives
`reach:ok(1/1),corpus:51fail/4pass DETECTED`, trailer all 0. That is
identical to Linux.

**For the manager:** plan.md's [MECH-SAN-ARM] cites S287 as its motivating
row. Its D77 trigger, "a second sanitizer-only row", has lost that row.
plan.md is yours to edit; I did not touch it.

## Item 4: S526 ANOMALY (BUILD-FAILED). CONFIRMED.

The Linux build.log stayed in the box's scratch, so I reproduced it on the
Mac in a scratch copy with MF_MAX_TERM set to 4:
`src/gen/emit_dfa.c:1070: error: static assertion failed: "an offset-skip
block's terms ... must fit one memfn predicate (C14)"`. R4c put the same
bound in the BUILD as well as in C14's own TU (`form_checks.py`).

**The matrix has NO expected-build-failure verdict.** `--help` lists
SAB_EXPECT as DETECTED, UNDETECTED or UNREACHED, and a `make all` failure
always prints `BUILD-FAILED ... ANOMALY` (run_sabotage_matrix.sh:1295).

**Row re-design (no matrix change):** S526 is now a two-site row.
SAB_FILE2 removes the build's copy of the assert, and the row measures the
other half of the pair: C14's own compile still refuses the lowered bound.
Mac proof:
- By hand: the build passes, then form checks give `FAIL: C14: a shape bound
  fails ... static assertion failed`.
- Matrix: `bash tests/mech/run_sabotage_matrix.sh S526` gives
  `reach:ok(2/2),memfnforms:1fail/3pass DETECTED`.
- SABANCHOR: `scripts/m6read_check_sab_anchors.py` says "all anchors
  resolve" (481 rows, 499 sites).

**Proposed smallest matrix change, NOT BUILT** (so the build-time half is
also scored):
1. Accept a new `SAB_EXPECT=BUILD-REFUSED` value with a required
   `SAB_BUILD_REFUSAL` literal (field validation, about 4 lines).
2. In the `make all` failure branch: if the row expects BUILD-REFUSED and
   `grep -F` finds the literal in build.log, print `build:refused` and
   DETECTED; otherwise keep today's ANOMALY.
3. If the build SUCCEEDS under BUILD-REFUSED, print `NOW BUILDS
   ***UNEXPECTED***`.

That is about 20 lines. Then a one-site twin of S526 would score the build
assert.

## Item 5: S527 shows `unreached: 1` beside a DETECTED row. CONFIRMED; it is the matrix's documented trap.

The trailer counters `grep -c` the WHOLE row line
(run_sabotage_matrix.sh:2962-2970). S527's SAB_DESC said "the UNREACHED
declaration must turn red", so the row counted itself. The matrix's own
[b2fix] note (lines 1091-1110) records the same trap on S268.

**Fix (kit-side, the established convention):** reworded SAB_DESC and added
a header note. No other SAB_DESC carries a verdict token; I grepped all 481
rows.

**Mac proof:** S527 gives `reach:ok(2/2),memfnforms:1fail/4pass DETECTED`,
trailer `unreached: 0`.

**Recommendation:** this is the trap's SECOND live recurrence. The [b2fix]
note names the robust fix: anchor each counter on the verdict column,
`awk -F'\t' '{print $NF}'`. Its trigger is "whoever next has cause to touch
this section". I did not touch the matrix; the decision is yours.

## Item 6: I2, 17 failing arms

**Claim "every stream movers=0 asymmetric=0": CONFIRMED for 12 logs, REFUTED
for 5.** Checked over all 17 logs, and the judge re-checked all 94.
- **Arms 2, 17, 44, 59 (memfn-simd):** `asymmetric=4165/4166/4166/311`. The
  ref refuses a flag it predates.
- **Arm 1:** dumps reads `movers=1`, the declared `--list-axes` mover.
- **The other 12:** every stream reads 0/0, and so do the 77 arms that
  passed.

**(a) memfn-simd arms: dropped from I2.**
- A tip-vs-tip check is not expressible. `--extra` applies to both sides,
  and one binary on both sides is a mirror (identity trivial).
- The arms family does compare flag-vs-base on each side, and the tip side
  read `differ=0 refusal=0` over 3598 patterns. But it asserts nothing for
  an unpinned flag, and ASSERT_ZERO is not reachable from the CLI.
- The script now filters both spellings out of FLAGS. Its comment cites
  step 5 (axes) and step 6 (C11's "identical (no SIMD form)"), both green on
  Linux.
- 94 arms become 90.

**(b) Floor and witness failures.** Measured on the Mac with the tip and a
scratch build of the ref e6e6d6eb, over all 369 composition files
(`build/scratch/lane/comp_who.log`). Both sides lose the SAME file with the
SAME artifacts:

| arms | file that stops producing | reason |
|---|---|---|
| 9, 51 (`-fno-cls-kit`) | `tests/uprops/size_ladder_prefilter_drop.rxt` | Without the class kit the artifact is 608484 bytes of emitted code, over the 500000 limit, so it is refused. 38 to 37 producing, 108 to 106 artifacts. |
| 31, 73 (`-fno-splice-calls`) | `tests/rxtsource/fixtures/compose_delivers.rxtin` | "a delivering call names a definition this build did not inline ... or -fno-splice-calls denied it", so it is refused by construction. It is a named DELIVER fixture, and with no splice no artifact can carry the SET-pair shape: both DELIVER WITNESS lines. Artifacts 100. |
| 87-94 (`base=utf8`) | `tests/rxtsource/fixtures/compose_encoding_clash.rxtin` | Its `ok` target's definition declares `encoding byte`; under `-e utf8`, "one artifact, one encoding" refuses `ok` as well (the fixture's own D58 refusal). |

**The judge:** `docs/design/memfn/probes/lxrun/memfn_r4c_i2.py LABEL LOG`.
An arm PASSES iff:
- the log is complete;
- every REAL RUN stream is present and reads movers=0 asymmetric=0;
- dumps did not run;
- every failure line (VIOLATION, FAILURE, FAILED, `<--`, MOVERS,
  ASYMMETRIC, Traceback) is declared VERBATIM for that arm's label;
- every declaration occurs in the log (none is stale).

The script now judges each arm with it; emit_sweep's rc is logged but is
not the verdict.

**Declared exceptions (the judge's table):**

| label ERE | declared line(s) | reason |
|---|---|---|
| `^base=(none\|-fcomments) -fno-cls-kit$` | `COMPOSITION PRODUCING FLOOR VIOLATION: 37 < 38` | size_ladder_prefilter_drop.rxt is over the emitted-code limit without the class kit; both sides |
| `^base=(none\|-fcomments) -fno-splice-calls$` | the floor line, `DELIVER WITNESS FAILURE: fixture(s) did not produce: ['compose_delivers.rxtin']`, `DELIVER WITNESS FAILURE: no composition artifact ... DELIVER block.` | delivering calls need a splice, which the flag denies; that file is a named DELIVER fixture; the shape is reached only through a splice |
| `^base=utf8 ` | the floor line | compose_encoding_clash.rxtin's `ok` definition declares `encoding byte`, and one artifact has one encoding; both sides |

**Judge over the 94 real Linux logs:**
- The 77 previously-passing arms: PASS.
- The 12 declared arms (9, 31, 51, 73, 87-94): PASS.
- The 4 memfn-simd arms: FAIL, as they should; they are dropped.
- Arm 1: FAIL on its dumps stream, as it should; it is fixed in (c).

**Planted controls** (`memfn_r4c_i2.py --selftest <logdir>`, doctored copies
of i2_9 and i2_3), all read red:
- an extra mover;
- an asymmetric row;
- an undeclared floor violation;
- a stale declaration (the floor line deleted from an arm that declares it);
- a truncated log.

Both undoctored logs read green. rc 0.

**(c) Arm 1: streams restricted** to `c-default,c-vm,emit-ir,facts,composition`.
- Why restrict rather than re-use the gate's logic: the dumps mover is the
  SAME ref/tip pair step 2 already judges with memfn_r4c_gate.py. Judging it
  twice adds nothing, and copying the gate's EXPECTED_ADDED into a second
  judge makes a second place to re-pin.
- Its arms family, the `--arms start` floors, had no `<--` line on Linux.
- The I2 judge also refuses any arm that runs dumps.

## Item 7: RERUN mode. Done.

`memfn_r4c.sh` changes:
- `STEPS` (default all; comma or space list among gate, test, mech, axes,
  c11, i2). Preflight and build always run. An unselected step prints
  `rc=skip`, and `reds=skip` when test is not run.
- `TESTSECTIONS` runs `make <sections>` instead of the full `make test`.
- `MECHROWS` overrides the 35 ids. It is still one id per call, and
  `rows=<n>` is printed.
- `I2ARMS` is an ERE over labels. Arm numbering stays the full run's, and
  `i2arms` counts the arms RUN.
- The completion line format is unchanged. The header and lxrun/CLAUDE.md
  are updated, and the new judge is listed there.
- `bash -n` OK.

Mac dry run, `build/scratch/lane/rerun_dry.log`:

    STEPS="test mech i2" TESTSECTIONS=test-memfn-arch MECHROWS="S527 S523" I2ARMS='^NOMATCH$' CC=gcc-16 JOBS=4 LOADWAIT=0 bash .../memfn_r4c.sh ff2ee9be
    -> R4C-LX-DONE gate=skip test=0 reds=0 mech=0 axes=skip c11=skip i2=0 i2arms=0 wall=79s   ("i2=0 arms=0 (of 90)")

## Item 8: the RERUN command for main

    STEPS=test,mech,i2 \
    TESTSECTIONS="test-memfn-arch test-memfn-forms test-memfn-reach test-memfn-manifest test-codegen" \
    MECHROWS="S287 S518 S519 S520 S521 S522 S523 S526 S527" \
    I2ARMS='^(arms-start|base=(none|-fcomments) -fno-(cls-kit|splice-calls)|base=utf8 .*)$' \
    nohup gnutimeout 300m bash docs/design/memfn/probes/lxrun/memfn_r4c.sh <TIP> > r4c_linux_rerun.log 2>&1 &

**Deviations from your expectation:**
- **test adds `test-codegen`.** Its [SABANCHOR] section reads the sabotage
  rows I edited (S526 has a new second anchor). forms, reach and manifest
  read nothing I changed. They are kept because they are cheap and you
  listed them.
- **mech adds S519, S520, S521, S522 and S523.** Their witnesses changed,
  and their Linux DETECTED at 91f5b607 was vacuous (clean C4 red; item 2).
- **i2 runs 13 arms:** arms-start, the two cls-kit, the two splice-calls and
  the eight utf8 arms. These are the arms whose verdict path or streams
  changed.
  - The other 77 need no re-run. The judge passes their real logs, and no
    byte pcrec emits changed: this branch touches no `src/`, `cli/`, `lib/`
    or `memfn/` file.
  - For the same reason, gate, axes and c11 are not re-run.
- **PASS** is `test=0 reds=0 mech=0 i2=0 i2arms=13`, with the other steps
  `skip`.

## Validation (Mac, darwin, gcc-16)

| run | result |
|---|---|
| `make strict` | clean (`build/scratch/lane/strict.log`) |
| `make test-memfn-arch` | 12 passed, 0 failed |
| `make test-memfn-forms` / `-reach` / `-manifest` | 4/0, 4/0, 25/0 |
| `scripts/m6read_check_sab_anchors.py` (test-codegen's [SABANCHOR] input) | 481 rows, all anchors resolve |
| mech, one id per call: S287 S518 S519 S520 S521 S522 S523 S526 S527 | all DETECTED, every trailer `unexpected 0, undetected 0, unreached 0, anomalies 0` (`build/scratch/lane/mech/summary.txt`) |
| I2 judge over 94 real Linux logs | as item 6; the 89 kept-and-declared arms all PASS |
| I2 judge selftest | 5/5 planted reds read red, 2/2 clean logs read green |
| RERUN dry run | completion line as item 7 |

Not run: the full `make test` and the full mech matrix (per the brief).
`test-codegen` was not run as a whole on the Mac; only its anchor-check
input was run. The Linux re-run is the verdict.

## Charter vs committed

| # | charter | committed |
|---|---|---|
| 1 | widen C4 classes from the population; decide GCC_HAVE_SYNC; plant counts | yes: whole-population plants, v4, macro-only names, GCC_ exclusion with reason; counts above |
| 2 | confirm S518; robust witness | yes: plus `checks failed: 0` on all memfnarch rows (and S526/S527) |
| 3 | flip S287, Mac proof | yes |
| 4 | S526 build failure; matrix support; row re-design; Mac | yes: two-site row; BUILD-REFUSED proposed, not built |
| 5 | S527 unreached count | yes: SAB_DESC trap; reworded; robust matrix fix recommended |
| 6 | verify 17 logs; (a) simd arms; (b) per-file reasons + judge + planted controls; (c) arm 1 | yes |
| 7 | RERUN mode, header, CLAUDE.md, bash -n | yes |
| 8 | RERUN command, justified | yes |
| — | report + lanes/CLAUDE.md row | yes |

## Kit manager's review addendum (2026-10-07)

1. **The memfn-simd pair is BACK in I2, as INERTNESS arms.** Item 6 had
   dropped it, on the grounds that tip-vs-tip is "a mirror". That is true
   of IDENTITY. It is not true of emit_sweep's per-side DIFFER count
   against the arm's own `--extra-base`, which is exactly the inertness
   claim. Also, C11's identity half compares only default vs
   `-fno-memfn-simd`, so `-fmemfn-simd` had no byte witness anywhere.
   - The driver runs 4 `inert base={none,-fcomments} -f{,no-}memfn-simd`
     arms with `ARMREF=build/pcrec`, so both sides are the tip.
   - memfn_r4c_i2.py requires `differ=0/0 stamp=0/0 refusal=0/0` on
     c-default and c-vm for an `inert` label.
   - Controls: an `-fno-altcls-factor` log relabelled as inert reads RED
     (102/102); a zeroed copy reads GREEN.
   - Real Mac run: `-fmemfn-simd` reads `c-default differ=0/0 stamp=0/0
     refusal=0/0`; judge PASS.
2. **The pcrec manager's point (2), on the composition floor.** Making the
   composition floor and DELIVER witness default-arm-only needs a change
   to `scripts/emit_sweep.py`, which is main's file: it applies them on
   every run that includes the composition stream, and the I2 driver
   cannot scope a floor. So the declarations stand, the allowed
   fallback. Each one names its file, its reason, and its witness: the
   arm's every stream reads movers=0 asymmetric=0, both sides lose the
   file alike. Each one fails if stale. **Request to main (backlog, not
   this lane's):** an emit_sweep option to apply the composition floor
   and DELIVER witness at the default arm only would retire all three
   declarations.
3. **The RERUN command gains the inert arms.** `I2ARMS` becomes
   `'^(arms-start|inert .*|base=(none|-fcomments) -fno-(cls-kit|splice-calls)|base=utf8 .*)$'`,
   so PASS is i2arms=17.

## Addendum 2 (kit manager, 2026-10-07): the Linux re-run's C4 red, and the committed populations

The re-run at abae07fa read C4 class 1 red: `3 of 41 compiler-derived plants
MISSED: FP_FAST_FMAF; FP_FAST_FMAF32; FP_FAST_FMAF64`. gcc 15.2 declares
`__FP_FAST_FMA*` under -mfma; clang, the Mac's x86 proxy, does not. This is
the second Linux-only miss, for one root cause: the regex was checked only
against populations the Mac can produce.
- **Fix 1 (the rule).** `__FP_FAST_FMA*` is C99 <math.h>'s fast-fma
  CAPABILITY macro, not an ISA's name; the ISA is class 1's `fma`. It joins
  `__GCC_HAVE_SYNC_COMPARE_AND_SWAP_N` in the named list
  `CAPABILITY_PREFIXES = ('GCC_', 'FP_FAST_')`. Those are class-2 plants,
  and class 2's regex already covers them, never class-1 stems.
- **Fix 2 (the mechanism).** `tests/memfn/c4_populations/<compiler>-<target>-<box>/`
  holds the box's REAL `gcc -dM -E` dumps (main's executor probe: 5 -march
  levels incl. native, 13 -m flags, VERSION, native_target.txt).
  `population_controls()` plants classes 1-2 from every committed population
  on every run, on any box.
- **Control.** With `CAPABILITY_PREFIXES = ('GCC_',)`, the Mac run reads
  `FAIL: population gcc15.2-x86_64-ubuntubudu class 1 (isa-name): 3 of 41
  plants MISSED by the regex: FP_FAST_FMAF; FP_FAST_FMAF32; FP_FAST_FMAF64`.
  That is the box's exact failure, reproduced offline. With the fix: 37/37
  and 48/48, `checks failed: 0`.
- The probe (for a new box):
  `for m in x86-64 x86-64-v2 x86-64-v3 x86-64-v4 native; do gcc -march=$m -dM -E - </dev/null | sort > march_$m.txt; done`,
  plus `gcc -m$f -dM -E` for each ISA flag set (abm aes avx512f bmi bmi2 cx16
  f16c fma lahf-lm lzcnt movbe pclmul popcnt sha).
