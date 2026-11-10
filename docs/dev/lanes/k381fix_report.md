# k381fix report — review 2026-11-10 r1 k381, the ruled FIX-NOW set on K38-1

STATE: delivered (gate jobs 520-529 written and dry-run, NOT queued: the kit manager queues them).
Branch lane/memfn-k381, on top of cbe2c255b. Charter: the Rulings section of
`docs/dev/reviews/2026-11-10-r1-k381.md`.

## Summary

All six FIX-NOW items (K1-K6) and the PLAN items carried into the sheet are applied. ZERO emitted
bytes: the 320-artifact BASE(1c043835d)-vs-tip sample (32 patterns x 10 arms, K38-1's list) is
`diff -r` IDENTICAL, artifacts, diagnostics and rc. fd_pres's deleted branch could not have moved a
byte: its reply was the whole run on every input, so `k.member` was never written.

## Fix by fix

- K1: finder.c `fd_pres` loses the whole-run `else if` branch (13 lines, with its 254 refusal);
  `kit.h` gains `KIT_RUN_NONE` and its two positional `{0,-1,0,0,0}` users (presence.c, window.c)
  take it; `decider_census.py` RUN_CALLERS drops `fd_pres` (kit_run_decide: kit_pres_picks 1,
  run_member 1, translate 1); the comments in finder.c, kit.h, presence.c, memfn/src/CLAUDE.md and
  run_decide_check.c no longer name the keep a reader. Evidence: `nice make -j2` clean, `make strict`
  rc 0 (scratch k381fix/strict.log), census D green with the new counts, 320-artifact sample identical.
- K2: sheet rev 1.3 (revision-log table, header paragraph, Goal 2, §4.3, §5 K38-1): two
  `kit_run_member` callers under option A, "run half" un-inverted. Four code comments: memfn/src/
  CLAUDE.md (window.c entry), window.c C-member rule string (a never-read data string, `->rule` has
  no reader, so no trace byte moves; confirmed by the sample), window.c's `kit_run_member`
  PRECONDITION ("both callers" now names them and the `tie` argument's purpose), window.c's
  translate comment (kit_run_decide asks it).
- K3: sheet §2.5 and §6 Q6 (1): the trigger is now "the first rule or lever that changes
  `kit_run_decide`'s tie or mass rule without the verify-NO member (K38-2a's `run-tie-left`), counted
  on artifacts carrying both sites", and says the lever leaves the verify-NO member behind. U2 folded in.
- K4: sheet §2.5 and §7: `pcrec_run_pin`'s rate pick is NAMED, not counted by `decider_census`
  (it reads `memfn/src` only); its movers are counted inside §5.1 item 4's population; a pcrec-side
  decider list is P6's first act.
- K5: `decider_census.py` D counts EVERY use of `kit_run_member` / `kit_run_decide` (patterns
  `\bNAME\b`, `#` lines skipped, definition/prototype skip kept). New plant "kit_run_member alias"
  (`void *census_alias = (void *)kit_run_member;` in an unlisted function). Evidence: census 95
  passed / 0 failed (was 94); the three D plants each print `1 error(s)`.
- K6: `run_decide_check.c` reads the verify-YES member's stretch (`mf_wreply` `run_lo`/`run_len`,
  literals `[0,4)` on W1 and `[0,12)` on W2, as `lo*1000+len`); `RUNDEC_FLOOR` 11 -> 13 in
  `run_finder.sh`, and tests/memfn/CLAUDE.md. Evidence: `make test-memfn-finder` 3419 passed, 0 failed
  (3417 before; rundec 13/0).
- PLAN items: sheet K38-2's row carries K1's general form (the route as the decision's input), U1
  (`kit_run_reply` is `mf_class.run`'s type) and U3; U2 in Q6; U4/U5 stay on §6 P3/P6; K38-2a's row
  records the kit ruling that the plan's in-run stop (`a_mass_choose`) becomes a counted reader of
  `kit_run_decide` before the lever lands.

## Checks re-run

All on worktrees/k381, `nice`, parallelism at 2 (`taskset -c 0,1` for G2 and codegen); logs under
/var/tmp/pcrec-pcrec/scratch/memfn/k381fix/.
- `nice make -j2`: clean. `make strict`: rc 0.
- `make test-memfn-finder`: 3419 passed, 0 failed (finder.log).
- `make test-memfn-rows test-memfn-link`: rc 0; rows 239/0; census with plants 95/0 (rows.log).
- `python3 -I scripts/m6read_check_sab_anchors.py`: rc 0 (anchors.log).
- `make test-codegen` (PROCS=2): rc 0, 21/21 scripts passed (codegen.log).
- `make test-memfn-g2` (quick, taskset 0,1): rc 0, 70,358,660 checks passed, window family 10444 (g2.log).
- BASE-vs-tip single-compile sample: 320 artifacts + 320 logs identical (hs-tip vs k381/hs/base).

## Gate jobs

/var/tmp/pcrec-pcrec/scratch/memfn/k381fix/jobs/, copied from k381/jobs and re-keyed kit-k381f-*
(520-529, the same chain; each job's PREV and `after` keys re-pointed). Not queued. Every
`--dry-run` rc 0. Moved figures: the test job (525) now expects 3 RUN CALLERS plants (kit_run_member,
"kit_run_member alias", T_WINDOW); the outputs live under k381fix, the frozen BASE binary is read
from k381/base. The mech row list is unchanged: `rows_for.sh` over this tip's changed memfn/src and
tests/memfn paths lists 35 rows, all already in mech.sh's 75.

| # | key |
|---|---|
| 520 | kit-k381f-strict |
| 521-523 | kit-k381f-ident1..3 |
| 524 | kit-k381f-reach |
| 525 | kit-k381f-test |
| 526 | kit-k381f-plants |
| 527-529 | kit-k381f-mech1..3 |

## Charter-vs-committed checklist

| promise | artifact |
|---|---|
| K1 dead branch, counts, comments, KIT_RUN_NONE | finder.c, kit.h, presence.c, window.c, decider_census.py |
| K2 sheet 1.3 + four comments | span_runs_sheet.md, CLAUDE.md, window.c x3 |
| K3, K4 sheet text | span_runs_sheet.md §2.5, §6 Q6, §7 |
| K5 identifier census + non-call plant | decider_census.py |
| K6 stretch read, floor | run_decide_check.c, run_finder.sh (13) |
| PLAN items, kit ruling in sheet | span_runs_sheet.md K38-2 and K38-2a rows |
| zero emitted bytes | 320-artifact sample identical |
| jobs 520-529 dry-run, not queued | scratch k381fix/jobs |

## STATE AT HANDOFF

Tip: the last commit on lane/memfn-k381 (this report).
OWED: none from this lane (the gate jobs are the kit manager's, written and dry-run, not queued).
The kit manager's queue: jobs 520-529
(byte-identity over 71 arms, reach, make test with the three RUN CALLERS plants, G2 plants, 75 mech
rows). Not done: nothing else in the ruled set.
