# b1fix report (lane b1fix, 2026-10-17, sonnet)

Branch `lane/b1fix` off `lane/memfn-fd` (77239f45c). Fixes the reds listed in
`worktrees/memfn-slot/b1heavy/triage/triage_report.md` that main's int3 merge
(6ca1589e6) left on the kit branch. All runs `taskset -c 0-7`, `-j8`. A verdict
is green when GNU make's `\*\*\* \[(Makefile:[0-9]+: )?test-` lines do not match.

## 1. Merge main (554a06fdb)

`git merge main` alone: clean, zero conflicts (B0 was already on both sides,
so no content disagreed). `make -j8` and `make strict` clean after it.
MF_SITE_ABI is 12 (the branch's, unchanged), PCREC_ARTIFACT_ABI is 78. The
merge auto-committed.

## 2. test-compound G7 lever fence (3ec84a90a)

`tests/compound/run_lever_fence.sh` check (c) greps docs/spec, docs/guide,
README.md, examples, lib, tests, scripts and cli for the literal `--harness=`
and the prefix `pcrec_harness_` outside its allowlist. cli/CLAUDE.md's "The
harness build" paragraph (B1's 3190c23aa) spelled `--harness=no-compound` and
`--harness=measures=FILE`. Reworded to describe the two options by effect and
to name where their spellings live (main.c, tests/compound/, the fence's own
allowlist). No allowlist widened.
Re-run: `make test-compound` green (no `***` line; `run_lever_fence.sh` itself
PASS "G7 lever fence (3 checks, 4 controls)"; G1/G2/G4 split differential
189 case-arms, 0 failures).

## 3. test-codegen K37 (a974ea7d9)

The site was `run_memfn_reach`'s `python3 -I memfn_arm.py --pcrec "$PCREC"`
(tests/axes/run_axes.sh:1185 at the old base). Bounded as the file's other
call sites are: `"$TIMEOUT_BIN" "${MEMFN_REACH_SECS:-3600}" python3 ...` on the
one line (the guard token must share the line). The ceiling is a backstop:
memfn_arm.py already bounds each compile at 30 s, and the whole reach was
MEASURED at 144 s on this box (`MEMFN_REACH_ONLY=1`, cpus 0-7), 25x under the
ceiling. No allowlist entry added.
Re-run: `make -j8 test-codegen` rc 0, `run_group: 16/16 scripts passed`, no
`***` line; `[K37] ... 1274 site(s) ... is bounded` PASS.

## 4. test-plan-lint PL14

No edit needed. main's int3 lane already fixed it (6b5b47938, "fix two
doc-citation reds from the merged branches (PL14 plan line cite ...)"), so the
`plan.md:859` cite in winreq_report.md is gone after step 1 (the line now
reads `[REGIME-LANDINGS] (not started)`). `make test-plan-lint` green:
180 rows, 0 violations, selftest 32 plants / 17 of 17 rules.

## 5. Sanity after the merge

`make test-memfn-finder test-memfn-rows test-registry` rc 0, no `***` line
(registry 213/0 and the `[memfn floor] 11 rows` check among them).

## Tip

See `git log -1` of `lane/b1fix` (the sha the handback message names).

## Findings, not fixed (out of the brief)

- `tests/axes/memfn_arm.py` (`make test-axes`' memfn arm) is RED on B1's rows:
  `FAIL: list-axes memfn rows [fd-d1, fd-ndisp, fd-r0, fd-r5, fd-r8, ...] !=
  MEMFN_CLASS rows [...]` and ten `cell ('fd-*', layer) has no classification`
  lines (`MEMFN_REACH_ONLY=1 bash tests/axes/run_axes.sh`: 164 passed / 11
  failed, 144 s). MEMFN_CLASS needs a MEASURED class (DIFFER with floors and
  witnesses, ASSERT_ZERO or REFUSES) for the five `fd-*` denies, per the
  file's own header; that is a measurement, so it is left for the kit manager.
  test-axes is not in `make test`, which is why B1's chain did not see it.
- Not touched, per the brief: tests/memfn/row_floors.tsv's
  `precheck_assign_byte` PLACEHOLDER and everything for S494.
