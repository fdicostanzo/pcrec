# axtri1115 report

## REPRO
On main's code (worktree at main, `make -j4`), `RXTFLAGS=-fno-req-run` and `RXTFLAGS=-fno-req-byte` over
`tests/litscan/d27` (tests/harness/run.sh + tests/axes/dump_diff.awk against the default dump) each give
`keys_base=143 agree=142 giveup1=1`: `tests/litscan/d27/partd_required.rxt:32` default={trc=0 nomatch}
axis={trc=3 steps}. Confirmed as main's red, not the kit's.

## CAUSE
Line 32 is the file's own "subject that gives up without the run" witness (`(x?)([a-z]+)+eeeeeeee~#~#~#~#.[0-7]{32}\1`,
pcre2-only). The default build's necessary-run pre-check proves nomatch; both deny flags remove it and the VM's
catastrophic backtracking exhausts the steps budget: the K65/K66 shape. The D27 file's header says nothing against
an allowance (it states the subject gives up without the run). No allowance existed because the file landed after
the manifest was populated.

## FIX
Two text-keyed GIVEUP1_ALLOWANCE entries in tests/axes/run_axes.sh (after the handoff_vm group), keyed
`<flag>|tests/litscan/d27/partd_required.rxt@pattern ... :: n "..."` with reason lines. The witness is untouched.
Commit 20d5e2ffd on lane/axtri1115. giveup1_key_check.sh passes (4/4).

## VALIDATION
- AXES="-fno-req-run -fno-req-byte" run_axes.sh over tests/litscan/d27: both axes OK, giveup1-allowed=1, unallowed=0.
- Whole axis list over tests/litscan/d27 (run_axes.sh with no AXES, cut by timeout 580 s in the memfn arms): 105
  axes ran, every one giveup1-unallowed=0, mismatches=0; so no other d27 file has the shape under any deny flag.
  (The floor/mover FAILs in that narrowed run are the K35 population floors, expected for a one-directory run.)
- OWED: full `make test-axes` on lane/axtri1115, queued as job key `450-main-axtri1115-axes` (its --ready holds it
  until 01:00 and lifts it by 20:00). Completion: `scripts/boxqueue state 450-main-axtri1115-axes` exit 0 / its
  job.log in worktrees/.boxqueue/done/*-450-main-axtri1115-axes.
