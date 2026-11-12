# pffix report

## STATE AT HANDOFF

STATE: delivered. Branch lane/pffix (from lane/famland, abi 99), four commits:
f1304934d (emitter + abi 99 -> 100), a888c9926 (recidentity self-pin), 14d65ec7a (harness CCFAIL),
d6f936bb8 (empty-engine manifest +18). Rulings file: none named in the brief.

**Can the uninitialized read happen at run time? No. No answer was at risk.** `rx_prefilter` returns 1 only
on the branch that writes `capture_spans` first, and the caller passes a non-NULL `window`. For an
accept-free machine that branch is dead. gcc `-O1` inlines the prefilter through the iterator and
`-Wmaybe-uninitialized` cannot prove the read dead. So the failure is a warning on a dead path, and the
harness's `-Werror` turns it into a compile failure. There was never a wrong answer.

**Fix (removes the class): an accept-free machine is the EMPTY engine.** New predicate
`dfa_accepts_nowhere` (src/gen/emit_dfa.c, beside `state_acc_any`): it is true when no state accepts in
any view. The end and eol views are states, so it covers them. It is now the empty test on both routes:
- `locate_empty_applies`, the attempt route, where the old test was `d->n == 0`. That old test is the
  new predicate's vacuous case.
- `unanch_start`, the unanchored route, as an extra clause beside the dead start.
- `attempt_cand`'s refusal, so the prologue and `<PREFIX>_DFA_PREFILTER` still answer "none".

The dead prefilter is no longer emitted as a loop: its body is the empty engine's one `return 0`. That
follows the existing LOCATE `empty` row, so this is no new mechanism. `-fprefilter` is still honoured,
and `RX_VM_PREFILTER` stays "hybrid".

I rejected two alternatives:
- Zero-initializing `window`: it moves every hybrid and keeps a loop that can never report.
- Not emitting the prefilter at all: it contradicts `-fprefilter` (do-or-die), and it would need a
  second empty mechanism.

The repro (`ab\Gcd`, `ab\Acd`, `--engine=vm -fprefilter`) now compiles clean at -O0/-O1/-O2/-O3/-Os
`-Wall -Wextra -Werror`. Its stamps are `RX_DFA_SCAN "empty"` and `RX_DFA_PREFILTER "none"`.

**Movers (measured by tests/codegen/run_dfa_stamps.sh's named empty manifest, not guessed):** 18 corpus
patterns join the empty bucket (105 -> 123). Every one is a never-match pattern, checked by hand:
- a start assertion after a consumed byte (`ab\Gcd`, `a\Gb`, `x\G`, `ab\A`, `ab\Acd`, `x\Ay`,
  `.{1,3}\Aa*`, `[a-]{1,2}\A-`);
- a non-multiline `^` after a byte (`.{1,3}^a*`, `[a-]{2}^a*`, `\s{2}^`, `a{2}^-`, `(?m)^a(?-m)^b`,
  `(?m)^a(?-m:^b)`);
- a multiline `^` after a non-newline (`a(?m)^b`);
- a refuted `\b` or `\B` (`^\Bfoo`, `^\Bo`, `^a\bb`).

Every other artifact moves only the abi digits.

**abi 99 -> 100. Readers moved (found by grep of 99 and the previous bump 2a36eb5ce's site list):**
- `PCREC_ARTIFACT_ABI` (emit_dfa.c);
- match_api.md: the guard block (3 lines), the rx_info row 1, §6¶17, and the §6.3 `"empty"` scan row
  (which now names the accept-free case);
- `ABI_EXPECT` and the transition narrative in tests/codegen/run_codegen_tests.sh;
- S693's BEFORE and AFTER;
- docs/dev/history/abi_changelog.md;
- recidentity FILEPIN and ABASEPIN, self-pinned to f1304934d by the convention in the script's own
  header. The manager re-pins both to the landing merge.

The gapreport fixture's "99" is a fake-stamp fixture. The 2a36eb5ce bump did not move it, so this one
does not either.

**Harness: a generated-C compile failure is a NAMED RED.** Changes:
- tests/harness/run.sh: `dump_ccfail` writes an RXTDUMP row with `trc=CCFAIL`, carrying the compiler's
  first `error` line, directory stripped. It runs at all four failure sites: unbatched build, batch
  member, batch dispatch.c, and solo relink.
- dump_diff.awk: a new `CCFAIL` bucket, asked first and on either side, so two sides that fail alike
  never read as AGREE. The summary line gains `ccfail=N`.
- run_axes.sh: one `AXIS FAIL: <axis>: GENERATED C FAILED TO COMPILE at <file>:<line>: <error>` per case,
  and the axis fails. A missing count also fails.
- run_ksweep.sh, the start-set product arm and utfcheck_arm.py fail on CCFAIL too.
- Docs: docs/testing.md (the per-axis line) and tests/axes/CLAUDE.md.

## Validation

Before and after, `AXES="-fprefilter" bash tests/axes/run_axes.sh tests/litscan/spanarms.rxt`:
- **Before** (pre-fix compiler 4518e474a, new harness): `ccfail=3` and three named reds at
  spanarms.rxt:503/504/515, each `gen.c:309:45: error: 'window' may be used uninitialized`.
  Log: $PCREC_TMPDIR/scratch/pffix/logs/before_spanarms.log.
- **After** (f1304934d+): `agree=160 lost=0 ccfail=0 mismatches=0`. Log: after_spanarms.log.

Both runs also print a `refused_documented ... below its K35 floor (12000)` line. That floor is a
whole-corpus figure applied to a one-file run, so it appears before and after and is not this lane's.

**Control.** A PCREC wrapper (scratch/pffix/plant/pcrec_plant.sh) appends `#error PFFIX_PLANT` to one
pattern's gen.c (`cat|dog`, under `--engine=vm` only). The run was
`AXES="--engine=vm" ... tests/base/alternation.rxt`. Result: `ccfail=3`, and three
`AXIS FAIL ... GENERATED C FAILED TO COMPILE at tests/base/alternation.rxt:9/10/11: gen.c:497:2: error:
#error PFFIX_PLANT`. The batched path (`HARNESS_BATCH=8`) gives the same three, as `a1.c:497:2`.
Logs: plant.log, plant_batch.log.

**Local runs:**
- `make strict`: green (strict.log).
- `make test-codegen`: the first run was 20/21 green. tests/codegen/run_dfa_stamps.sh went red on
  exactly the empty-manifest finding above. After the manifest commit, the same file re-ran clean,
  standalone: `checks failed: 0` (dfastamps.log). That is the file test-codegen runs.
- `make test-registry`: green, rc=0 (registry.log; the PC-3 and definitions-oracle runs had 0
  disagreements).
- `make test-rxtsource`: green, rc=0 (rxtsource.log; INV-COMPAT holds over 320 files, 6512 blocks
  and 85263 expectation lines).

**OWED (dispatched last, verdicts to main):**
- cloud `--kind test --name pffix`;
- cloud `--kind axes --name pffix`, the whole-corpus `-fprefilter` unit, where the claim is 0 lost and 0
  ccfail;
- boxqueue `make test-recursion-identity` on this worktree.

## Notes

- I checked no non-empty shape for the same gcc warning class. A live machine's `return 1` always
  follows the write, and `window` is non-NULL. If gcc ever warns on a live hybrid, the harness now names
  it.
- No mech row was added for the CCFAIL path. The control is the plant run above. A permanent row would
  need an S-id range from the manager.
