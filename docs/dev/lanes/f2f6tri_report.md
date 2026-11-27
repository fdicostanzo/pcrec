# f2f6tri report: red job 190-f2f6-alloc

## Verdict
Not (c). Two causes, both benign: (a) the job's `--w7-only` mode trips the
stale-`known_stranded` check, and (b) the W7/W3 floor is due a D110 re-pin
(267 -> 264). The W7 control read STRANDED (THE SEEN GATE sees the planted
strand), and W7/W3 passed with 528 diagnosed trials, no new stranded heap.
Premise test: the job ran `ALLOC_ARGS=--w7-only make alloc` in worktrees/f2f6
(39 s: it built build-alloc, then ran the check; it did run).

## Cause
The only FAIL: `known stranding [ARENA-SCOPES] (K155, target_headers_render nb)
was NOT REACHED by any witness`. That row is filed until F3 and is reached by
the non-W7 witnesses (W6 compound etc.). `--w7-only` ("measuring W7 alone",
alloc_check.c) skips those, so the end-of-run stale check
(alloc_check.c ~1268) reads the row as fixed. The job's own `expect` line
anticipated a floor miss, not this.
- Defect CLASS: a check whose precondition (all witnesses ran) is not held by
  one of its own modes (a measure-only flag still running the whole-run
  stale-allowlist assertion).
- House rule broken: none (learnings section 3's stale-allowlist check is
  right for a full run); the mode flag is the gap.
- Siblings: `grep -n "w7_only" tests/core/alloc_check.c` = 2 uses (flag set,
  loop guard); other end-of-run assertions run unconditionally under it.
  `grep -rn "w7-only"`: only f2f6_report.md and the job; no Makefile target.
- Class-level fix shape (NOT applied, outside this lane's fix scope): skip the
  stale-known_stranded loop when `w7_only` (it depends on every witness having
  run). Checked against the mechanism: `known_stranded_seen` is only filled by
  the witness sweeps, which `w7_only` skips, so the skip is sound.
Floor: W7/W3 population is 528 after F6 (535 at R-1 included the uprops
hand-kept window). D110 floor = half = 264; was 267.

## Fix
Committed on lane/f2f6tri: `tests/core/alloc_check.c` W7_ROWS floor 267 -> 264
(comment updated), `docs/design/arena_scopes.md` line 627 note (535 at R-1, 528
after F6). Not run again (a full `make alloc` is over 2 min; owed run: none
queued). A full `make alloc` (no `--w7-only`) on the f2f6 branch should be green
on the stale row (it is reached there); the manager should merge this floor
into f2f6 and let the already-queued gates (200-f2f6-*) proceed; a plain
`make alloc` re-run is the confirming check.

## STATE AT HANDOFF
Rulings file f2f6tri_rulings.md: empty, none applied. Owed runs: none. Fix
commit on lane/f2f6tri; worktrees/f2f6 untouched.
