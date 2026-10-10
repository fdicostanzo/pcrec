# flagacc -- [FLAG-ACCESS] report (lane flagacc, 2026-10-10)

Branch `lane/flagacc`, from main 273ba1ac. NO-MOVER: no abi bump, no public
(`lib/pcrec.h`) change, no emitted byte moved.

## 1. Census (before / after)

Detector: `tests/core/flag_access_check.py` run against `git archive 273ba1ac
src cli lib` (before) and the lane tree (after). It counts source LINES that
read the option word raw (comments and strings stripped).

| | before | after |
|---|---|---|
| raw reads | 65 lines (plan estimated ~63 in 11 files) | 0 |
| files | 15 | 0 (outside the accessor block) |
| accessor uses | 0 | 65 |

Files before (lines): compile.c 18, emit_vm.c 12, emit_dfa.c 11, select_engine.c
6, facts.c 2, clskit.c 2, altcls.c 2, possessify.c 2, scanedge.c 2, parse.c 2,
rxt_compose.c 2, memfn_sites.c 1, atomic.c 1, callgraph.c 1, ctxnode.c 1.
The plan's 11 was an undercount: it missed the dynamic-key reads (`r->deny &
flags`, `flags & DENY_FLAG[d]`, `flags & ~mask`) and `rxt_compose.c`.

Not counted as reads, and left raw on purpose: WRITES (`opt.flags |= ...`,
`&= ~PCREC_SIZE_CAP_REFUSE`, `cli_axis_apply`'s `*flags |= dm`, `defo.flags |=`),
which are the CLI's and the driver's construction of the word.

## 2. Accessor design

`src/core/internal.h`, one block bracketed by `FLAG-ACCESS-BEGIN/END`:

- `pcrec_flags_has(flags, key)` -- any bit of `key` set
- `pcrec_opt_has(opt, key)` -- same, on a `pcrec_options *`
- `pcrec_flags_masked(flags, key)` -- the subset of `flags` selected by `key`
- `pcrec_flags_without(flags, key)` -- `flags` with `key` cleared

A KEY is a `lib/pcrec.h` option macro, an OR of them, or a table's `deny`
column. The spelling follows internal.h's `cls_has`/`cls_set` static-inline
idiom. "Keyed by axis": the keys ARE the tokens `axes.def` names (deny/force
macros), not a second name set; `compile.c` derives from `axes.def` a pair of
`_Static_assert`s that every deny/force key is zero or a single bit, so the
accessors' "any of" reading is only exercised on multi-bit keys the caller
wrote as an explicit OR. `pcrec_axis_on` now reads through the accessor.

What is hidden: today's representation (one `uint64_t`, `key = 1ull << n`).
A two-word or bitset change is a change to this block plus the key macros'
encoding. What is NOT hidden (residue for [IFACE-PUSH], by design of the lane's
"reads" scope): the word still travels as a `uint64_t` PARAMETER (`cand_select`,
`DFA_SELECT`, `pcrec_clskit_deny_of`, `pcrec_memfn_*`, `fit_rung_denied`), the
CLI/driver writes are raw, and `emit_dfa.c` prints the word as a number into the
`.flags = N` stamp. A representation change must touch those types/sites; the
gate does not (and cannot) catch them because they are not reads.

## 3. Gate and sabotage

`tests/core/flag_access_check.py`, run as the last section of
`tests/core/run_core_tests.sh` (`make test-core`, a `make test` section); a source
scan, no build.

Independence of the control (learnings 3): the option-key population is parsed
from `lib/pcrec.h`'s `PCREC_BIT(n)` lines, not from the accessors or the call
sites; the detector is validated before the scan by literal MUST_FLAG /
MUST_PASS fixtures that live in the script (a detector that missed a raw read
or flagged a clean line exits 2 before scanning); and two population floors turn a
scan that reached nothing into a failure (55 option keys parsed, floor 50; 65
accessor uses seen, floor 55). The first draft failed its own fixtures twice
(`&&` read as a mask, unary `&opt.flags` read as a mask), which is the
fixtures doing their job.

Sabotage row **S792** (`tests/mech/sabotages/S792_flag_access_raw_read.sh`,
arm `core`): callgraph.c's `pcrec_opt_has(cx->opt, PCREC_NO_SPLICE_CALLS)`
respelled as the raw read. Behaviour-identical, so only this gate can see it.
S-id taken: **S792** (highest on main and in all worktrees was S791; the kit's
reserved ranges end at S757). Main's `worktrees/.mgr/sabotage_ids.txt` is NOT
updated by me (read-only): please add `S792 flagacc ...; next free S793`.

## 4. Identity proof (NO-MOVER)

`scripts/emit_sweep.py --ref 273ba1ac --bin build/pcrec --tree . --out ...`
(reference built from `git archive 273ba1ac`, self-check against a second
independent rebuild of the ref included). Population: argv=5621 corpus pattern
lines, composition_files=384 / producing=37 / artifacts=106, dumps=7. Streams
c-default, c-vm, emit-ir-vm, facts, emit-ir-auto (+3 arms), stderr, composition,
dumps: every stream `movers=0 asymmetric=0`, in both the self-check and the real
comparison. Log: `build/scratch/sweep.log` (worktree, gitignored). 67 s.

## 5. Validation

- `make`: clean. `make strict`: "whole tree compiles clean with -Werror -Wshadow".
- `make test-core` (incl. the new gate): 6 checks passed, 0 failed.
- `make test` (perfrun), mech S792, `make test-spec-history`: see section 6.

## 6. Validation verdicts and triage (triage lane, 2026-10-10)

First chain (5f06e1d3) came back RED on two counts; both fixed.

1. `make test`: `test-codegen` failed. Cause: `[SABANCHOR]`
   (`scripts/m6read_check_sab_anchors.py`) -- seven older sabotage rows
   (S232, S252, S342, S395, S401, S406, S421) anchor `SAB_BEFORE` on the raw
   spellings (`cx->opt->flags & PCREC_...`, `r->deny && (cx->opt->flags &
   r->deny)`, `(flags & (A | B))`, ...) that this lane replaced with accessors.
   Not a structural check keyed on spellings, not a census floor, not an
   emitted-text change. Fix: re-anchored the seven rows (BEFORE and, where it
   repeats the line, AFTER) onto the accessor spellings, same semantics and same
   sabotage; the tripwire reads "all anchors resolve" (670 rows). Nothing
   weakened.
2. mech S792 UNDETECTED. Cause: the gate was fine (a direct run on a planted
   raw read, and on `r->deny & flags`, `flags & ~mask`, `!(x->flags & K)`, all
   exit 1, and the kept sabotaged tree's `core.log` shows the runner's own
   `FAIL: raw option-word read` and `checks failed: 1`). The defect was the
   mech `core` arm's scrape: `grep -m1 '^checks failed:'` read the FIRST
   summary in `core.log`, which is the first sub-binary's (sat_arith_check:
   `7 passed / 0 failed`), not the runner's total at the end. So the core arm
   was blind to every check the runner itself runs after its sub-binaries
   (a pre-existing mech bug the new gate was the first to expose). Fix:
   `tests/mech/run_sabotage_matrix.sh` core arm takes the LAST summary pair
   (`tail -1`), with a comment saying why.
3. `docs/dev/artifact_size_log.tsv` modified: a side effect of the full test run
   (the artifact-size harness regenerates it); it is committed only by a
   deliberate regeneration (last: 042e9d3c), so restored with `git checkout`.

Verdicts (tip is the commit carrying this report; chain `build/scratch/val2/`):
- `make strict`: rc 0.
- mech S792: `core:1fail/5pass DETECTED`, `== mech run COMPLETE: 1 rows
  (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0 ...)`.
- `make test-spec-history`: rc 0.
- full `make test`: see the line appended below.
- full `make test`: rc 0, `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` empty (green), at the tip below.
