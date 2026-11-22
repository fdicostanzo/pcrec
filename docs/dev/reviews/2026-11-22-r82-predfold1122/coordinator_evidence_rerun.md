# Coordinator re-run of every evidence script at the freeze (6f1fe4e84), 2026-11-22 13:47-14:0x
Mirror (R/tree + git shim) and the worktree (HEAD 8997a11d8 = freeze + journal/wake only) agree on every clean run.

| model | committed .out | re-run at freeze | plants |
|---|---|---|---|
| predbound | 21/0 | 21 checks, 1 FAILED (DOC: metadata line printed with the old bare `w.index`; the docs now say `days.w.index`); the script exits rc=0 while red | 20/20 caught, 0 tracebacks; s1, s5 now ALSO fail DOC (committed: not) |
| predref | 8/0 | 8 checks, 1 failed (MARKS: "call-prefix open NO") | every plant run also fails MARKS |
| predcall | 14/0 | 14/0 (its PREDREF check expects predref's MARKS red) | 13/13 match committed |
| predfix77 | 20/0 | TRACEBACK: AssertionError `chars := (.*?)`, `nchars` (lib_body anchor gone) | 20/20 traceback |
| predarr | 17/0 | TRACEBACK: AssertionError `chars := (/.*?/)` | 17/17 traceback |
| predscope | 20/0 | 20 checks, 3 failed (NAMES, CLOSEDB, DOC). CLOSEDB: answers equal, the doc's Composed line no longer verbatim; NAMES: 7 of 17 printed definitions refused by the rule as stated; DOC missing flat-read-outside x2, nested-scope x3, bare-condition | plant outcomes all differ from committed (each adds the 3 reds) |

Reading (coordinator's): predref's red is the expected supersession, declared by predcall's PREDREF check.
predfix77 (array-in-piece, in force) and predarr cannot run at all on the frozen documents; predscope is red on
three checks, one (NAMES) a semantic statement about printed definitions. No later model declares these reds.
=> a FINDING for the draft (EVID-1) regardless of critics: the in-force rulings array-in-piece (predfix77),
array-scope (predarr) and the scope rulings (predscope) have no green evidence at the freeze.
Lint: pred_doc_lint.py in the worktree: 6289 passed, 0 failed; WARN L7 library.md 56549 B > 24576 soft cap; parked.md 20089 > 16384.

CORRECTION 14:05: predbound clean run is RED (DOC). predbound and predcall exit 0 regardless of failures; the verdict is the last line. Caught because MODECLOSURE-7 disagreed with my summary.
