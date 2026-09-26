# k65fix — K65 fix (a) (lane k65fix, opus, 2026-09-25)

Branch `lane/k65fix` from `5a2094e7` (abi 33). Brief: fix K65 as ruled
(D123 addendum 8 item 1, candidate (a)): on VM routes with no DFA in front,
the pre-check tests EVERY member of the necessary set.

## FINDINGS FIRST

1. **The fix is one emitter helper plus one published field.**
   `src/opt/reqbyte.c` already computed the whole necessary set and threw it
   away after the pick; `pcrec_req_byte` now also writes it to a new
   `Job.req_set` (`ReqSet`, a 256-bit map, `src/core/internal.h`), empty
   under `-fno-req-byte` exactly as `req_byte` is -1. In
   `src/gen/emit_dfa.c`, `pcrec_emit_req_byte_check` calls a new
   `emit_req_set_rest` after the byte check or the run check. It emits
   nothing unless `!pcrec_artifact_has_dfa_scan(cx)` (the existing
   predicate the hybrid's own stamps read) and some set member is left
   untested (not the pick; not a run byte). Then it emits one 6-line block:
   `static const unsigned char rq_set[] = { … };` plus a `memchr` loop,
   any absent member → `return 0`. It is not an admission rule: `req_admit`,
   `REQ_BYTE`/`REQ_RUN`/`REQ_WHY` are untouched. No parallel mechanism: one
   walk, one set, one emitted pre-check, extended.
2. **The witness is fixed, in both directions.** `(x?)([a-z]+)+Z.@\1` on
   `a`×31 + `Zb`: `-e byte` (pick `Z`) was `steps` in 2.23 s, now
   `nomatch`; `-e utf8` (pick `@`) `nomatch` before and after. The mirror
   subject (`@` present, `Z` absent) flipped the other way before
   (utf8 gave up) and is NOMATCH under both now.
3. **The hazard is wider than "backtracking": a FRAMELESS unanchored VM
   program has it too.** Linear per attempt, but retried at every start:
   `[a-z]+Z.@ --engine=vm -e byte` (frameless, pick `Z`) on 200,000 `a`s +
   `Zb` gave up with `work` (0.75 s) at the branch point, `nomatch` after.
   The rule's guard (no DFA scan) covers it with no clause of its own; 188 of
   the 452 movers are this shape. It is a structural §5.7 row only — a
   corpus cell would need a ~200 KB subject (the step budget is per
   attempt and does not bite; `work` scales with the subject).
4. **Census (movers):** `docs/dev/optloop/admitfix/k65_census.py`
   (`k64_census.py` re-aimed), base = 5a2094e7 build, new = the fix before
   the digit bump (same abi, so byte-exact comparison):
   - bench 256 configs: 30 changed (vm-caps 11, vm-nocaps 11, auto-caps 4,
     auto-nocaps 4), all predicted.
   - corpus 6,386 configs (3,193 distinct patterns × auto / `--engine=vm`):
     422 changed (vm 374, auto 48), all predicted.
   - All 452: a single 6-line pure insertion of the `rq_set` block (checked
     by `difflib`, and separately by `diff` hunk count), `RX_VM_PREFILTER
     "none"`, `REQ_WHY "emitted"` before and after. None is a DFA artifact or
     a hybrid. Framed/frameless × start: framed unanchored 202, frameless
     unanchored 188, framed anchored 61, framed gstart 1. Array sizes: 1
     member 437, 2 members 12, 3 members 3 (the largest is
     `\10(a)(b)…(j)`).
   - 0 refusal mismatches, 0 timeouts, and 0 identical artifacts carrying the
     array.
   (The instrument's `pure_add` field had a bug on its first run and was
   corrected before commit; the corrected logic was re-applied to the saved
   census files, 452/452.)
5. **abi 33 → 34** (the brief's ruling). No stamp, stamp value, declaration
   or layout changes; emitted PROGRAM text moves on the 452. The ritual:
   `PCREC_ARTIFACT_ABI`, `match_api.md` §6's new top entry (and "gap-free from
   2 to 34"), `run_codegen_tests.sh` `ABI_EXPECT` and its narrative, and
   `run_recursion_identity.sh` (B) re-pinned to `3b3c06f0` (the bump commit).
   The digit is a same-length substitution, so no byte-count manifest moves.
   Readers were found by grep. The remaining `abi 33` hits are history
   (`litscan_s1.md` §8.1, journal, optloop readings).

## Residue (stated, not closed)

- **Long runs.** A run longer than `PCREC_MAX_REQ_RUN_EMIT` (8) is truncated
  to a window the prior picks. So a subject can hold every set byte and one
  8-byte window of the run but not another, and still be proved under one
  prior and not another. That is findings-dependent in principle. It is
  written into `tuning.md` §2.29. Closing it would mean a second run
  compare, which is D77 territory with no measured case.
- **Count-collapsed hybrids** are out of the ruling's scope (a DFA scan runs
  in front), so they are untouched. The superset keeps every necessary
  byte of every `m ≥ 1` repeat, so I expect no case, but none was measured.

## Checks (both directions verified)

- **`tests/base/k65_precheck_whole_set.rxt`**: 3 blocks × (6 n + 1 m + 1 gu),
  `features backrefs`, `budget steps=10000`, L = 16..18.
  - Blocks 1 and 2 are the witness under `encoding byte` and under
    `encoding utf8`, one for each pick.
  - Block 3 is the run form `(x?)([a-z]+)+Z.@#\1` (run `@#`, rest `Z`).
  - `tests/harness/run.sh` on the file: **24/0 on the fix**, **9 failed /
    15 passed with `PCREC=<5a2094e7 build>`**. The nine are exactly the
    subjects lacking the member the pick did not test, all as `steps`
    give-ups.
  - `verify_rxt.py`: PASS=21, SKIP=3 (giveup). A libpcre2 10.48 spot check
    agrees (NOMATCH on all probes; the match cells give the same spans).
- **`tests/codegen/run_prechecks.sh` §5.7** (+9 checks, 258 → 267).
  - Seven rows, each with a HAND-DERIVED expected `rq_set` list: the witness
    under byte (`64`) and utf8 (`90`), the run form (`90`), frameless
    unanchored forced VM (`64`), and three `none` controls (a one-member set
    `(Z)\1`, an exact-hybrid control, the DFA engine).
  - Two `[5.7r]` reach rows: the witness is unguarded VM with the pick's
    `memchr` first, and the control is a hybrid.
- **Sabotage S277** (`tests/mech/sabotages/S277_precheck_whole_set_removed.sh`):
  plants an early `return;` in `emit_req_set_rest`. `SAB_HARNESS_TARGET`
  is the new `.rxt`, and `SAB_REACH` probes the witness's array on the clean
  tree. `run_sabotage_matrix.sh S277` run before the §5.7 frameless row was
  added: **DETECTED, `reach:ok(1/1)`, `prechecks:3fail/263pass`,
  `corpus:9fail/15pass`**, with 0 unexpected, 0 undetected and 0 unreached.
  Re-run on the final tree (`626d564c`, with the frameless row): **DETECTED,
  `reach:ok(1/1)`, `prechecks:4fail/263pass`, `corpus:9fail/15pass`**, again
  0 unexpected/undetected/unreached/anomalies. That is the figure in the
  row's `SAB_DOC_FIGURE`.
- S269/S270 clean-tree figures now read 267 (258 before K65). S274's
  measured `prechecks:2fail/256pass` figure predates §5.7. §5.7's rows
  are not one-attempt, so S274 should now read 2 fail / 265 pass
  (not re-run).

## Re-pins (readers found by grep)

- `tests/rxtsource/run_rxtsource_tests.sh`:
  - CENSUS_* and RUNSH_* move 217/4001/29129 → 218/4004/29153.
  - C3_PASS 13729 → 13750, C3_SKIP 15228 → 15231, C3_SKIP_GIVEUP 24 → 27,
    from the file checked alone.
- The abi readers listed above, plus the (B) FILEPIN.
- `run_prechecks.sh` has no count pin besides the S269/S270 figures.

## Validation

- `make strict`: clean ("whole tree compiles clean with -Werror -Wshadow").
- `make test-codegen` (after the abi bump): `run_group: 9/10 scripts
  passed`. The one red is `run_inline_capability.sh` ("nm could not read
  arm_a.o (no rx_search symbol)"), the known darwin Mach-O `nm` red that
  k64fix A/B'd as pre-existing. That includes `ABI_EXPECT=34` and the
  sab-anchor tripwire (S277's anchor).
- `make test-prechecks`: 267 passed / 0 failed.
- `make test-rxtsource`: exit 0, including the re-pinned census and C3.
- Targeted: the regression `.rxt` (24/0 fix, 9/15 base) and S277 (above).
- **OWED: the full `make test`.** Lane chkgapsmerge held the box's one
  heavy slot: its `worktrees/chkgaps/build/watchdog.log` was being written
  at 17:02. So a detached chain
  (`/tmp/k65fix.RMJi/maketest_chain.sh`) waits until that log has been
  idle for 10 minutes, then runs `make test CC=gcc-16` in this worktree.
  - Log: `/tmp/k65fix.RMJi/maketest.log`. Its completion line is
    `EXIT=<rc>`, appended at the end.
  - The verdict is make's `*** [test-X] Error` lines. The expected darwin
    red is the nm probe only (`test-codegen`'s `run_inline_capability.sh`).
  - The chain's own start/finish stamps are in `/tmp/k65fix.RMJi/chain.log`.
- **OWED at merge/mech:** `make test-recursion-identity` (the (B) re-pin,
  opt-in gate, not run), S274's prechecks figure (predicted 2 fail / 265
  pass, not re-run), and `make test-axes` for `-fno-req-byte` /
  `-fno-req-run` (the whole-set block is under `-fno-req-byte`, so that
  sweep should stay answer-identical).
