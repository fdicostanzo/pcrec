# k110fix report -- K110 `RX_ENGINE_WHY` offset after rewrites (2026-10-12, lane k110fix, sonnet)

Branch `lane/k110fix` from a8850e084. Closes K110 (`docs/dev/known_issues.md`).

## The change
- `Ast.reg_at` (common field beside `reg`, `internal.h`): the source offset of the stamp, written by `pcrec_ast_stamp` in the same statement as `reg`. `pcrec_ast_stamp` lost its unused `Ctx*` parameter (10 callers).
- `Ctx.first_vmonly_pos` (first-wins parse-time counter, the stale source) is DELETED, with both resets in `compile.c`.
- `forces_registry` reads `why`/`why_pos` off ONE node: `earliest_dfa_excluding` (was `first_dfa_excluding`) returns the DFA-excluding node with the least `reg_at`.
- Selection is EARLIEST BY OFFSET, not first in walk order. The CAT/ALT spines are walked right child first, so "first in walk order" was the LAST construct of a concatenation (my first cut turned `a\Kb\Kc` from offset 1 into 4; the sweep caught it). The old offset was creation order and the old text walk order, so the two could name different constructs; now they cannot.

## Survey: what can move offsets, and what the fix covers
Offsets are taken from `cx->pos` at parse time (user text) and never recomputed, so only the CHOICE of node can go stale. Passes that delete or exempt a stamped node before selection:
- free atomic/possessive discharge (`a++`, `(?>[^"]*)`, nested `(?>(?>a+)b)`): covered (witness + two rows).
- call splice (`CALL_SPLICE` exempted by the walk; `(a)(?1)b(?<=ab)`, `(?<n>a)(?&n)...`): covered, was stale too (offset 3 vs 8, 7 vs 13).
- ctxnode recognizer (`\b`/lookaround to `A_CTX`): never stamps; nothing to carry.
- `pcrec_altcls`, `lower_enc`, vars/bref resolve, postresolve: keep their children; a kept node keeps `reg_at`. `reg` has one writer, so a rebuilt node would already have lost its forcing.
- NOT touched: `first_cap_pos` (captures-first row; capture nodes are never deleted by a rewrite), `dfa overflowed ... offset 0` (convention), `emit_vm.c:10537`'s `first_cap_pos`.
- Side effect, same cause: the `pcrec_ctx_fail(cx, why_pos, ...)` refusals (`-fprefilter` noun refusals, `--engine=dfa` override) use the engine reason's offset, so they move with it (2 of 337 probed corpus patterns, e.g. `^a(?=${v})bc$` 5 -> 2). I tried a noun-specific offset for the `-fprefilter` refusal; it moved 73 of 337 (most already named the capture group's offset 0/1) and was reverted as out of scope. Left as is: the refusal still reports the engine reason's offset.

## Tests (oracle = the byte index of the construct in the pattern text)
`tests/vm/run_vm_tests.sh` section 3a, ten rows (58 checks, was 51), the oracle computed by bash `${pat%%needle*}` from pattern and needle alone, sharing nothing with the compiler: a (witness `a++b(?<=ab)` 4), b (nested atomic), c/d (spliced call, plain and named), e (`a++\K`), f/h/i (controls: nothing rewritten, first of several survivors), g (surviving atomic after a discharged `a++`), j (earlier survivor wins over later `\K`). Against the pre-fix compiler (main build) rows a b c d e g j are RED, f h i green: 7 of 10, so the controls do not depend on the fix.

## Spec / abi
- Spec: `docs/spec/match_api.md` 6.3.3 para 2 states what `N` is (byte index in the caller's pattern of the surviving construct's own spelling). Facts only.
- abi: NOT an event. Emitted scaffolding does not move: `emit_sweep.py --ref a8850e084` (self-check PASSED, full reach 5645 argv rows, 384 composition files) shows 89 movers on each `.c`/`--emit-ir` stream, 90 on `--emit-facts`, 0 on `stderr`, composition and dumps, and an instrumented run (build/sweep_why.py, scratch) classified every differing line: only `RX_ENGINE_WHY`/`.engine_why` text (WHY-ONLY 40 of 40 hunks seen) plus the 2 `-fprefilter` refusal offsets above. The value is the prose stamp (match_api table: "prose"), layout unchanged. If a pinned identity gate reads that line the suite below says so.
- Not a mover class that needed a census file: the stamp text of the 89 corpus patterns is the only delta.

## Validation
- `make` and `make strict` clean. `tests/vm/run_vm_tests.sh` 58/0 (pre-fix compiler: 7 of the 10 K110 rows red).
- Full `make test` (perfrun, `-j4 PROCS=3`, detached; log `build/k110/test.log`, verdict `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`): at 13:39 the only red line was `test-codegen`'s `[SABANCHOR]`: three sabotage rows (S93, S96, S117) quoted `pcrec_ast_stamp(cx, ...`, a text this change edits. Re-aimed (commit after the code), `m6read_check_sab_anchors.py` reports 700 rows, all anchors resolve. The suite was still running when this report was written: OWED are (1) the remaining sections' verdict, (2) `make test-codegen` re-run after the anchor fix, (3) solo mech rows S93/S96/S117 (`bash tests/mech/run_sabotage_matrix.sh S93` etc.; AFTER texts are unchanged and only the BEFORE anchor moved).

## Landing validation (lane k110fin, 2026-10-12)
- Tree of the full run: `d38db367b` (13:24), the re-aim `6bad4d92f` (13:35) came AFTER it, so the one red (`test-codegen` [SABANCHOR] S93/S96/S117) was a stale pin from before the re-aim, not a regression.
- `make test-codegen` at ff619b954 (log `build/k110/codegen2.log`): `run_group: 16/16 scripts passed`, no `*** [..test-` line, [SABANCHOR] clean. GREEN.
- Mech rows solo (`TMPDIR=build/k110/tmp`, logs `build/k110/mech_S{93,96,117}.log`, each `== mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0 ...)`, rc 0), all DETECTED as expected:
  - S93 `codegen:2fail/329pass,corpus:29fail/234pass,atomicdiff:16fail/5pass,registry:6fail/229pass+compliance-FAIL`
  - S96 `registry:1fail/230pass,codegen:5fail/326pass,corpus:12fail/114pass,atomicdiff:5fail/5pass`
  - S117 registry 12 fail / 230 pass, brefdiff 35 fail / 11 pass, corpus 0 fail / 88 pass
- Intent re-verified: the re-aim only drops the `cx,` argument; the plants still skip/neutralize exactly the stamp (S93 no A_ATOMIC wrapper, S96/S117 node left unstamped), and the detectors are the ones the rows name (registry `check_engine_capability`, atomicdiff, brefdiff). None of the three declares `SAB_REACH`, so there was no reach line to re-aim. S96's `SAB_DOC_FIGURE` predicted a green default-engine corpus; measured `corpus:12fail` (the harness target's `--engine=dfa` refusal cells). The figure text is still marked PREDICTED and was left alone.
- `git merge main` (alone): clean, docs-only (13 files, no src/tests). `make strict`: rc 0, "whole tree compiles clean".
- Not rerun: the other full `make test` sections (they ran green on d38db367, which has the identical src; the re-aim touched only three sabotage rows, and the merge brought docs only).
- Note: the first mech launch defaulted its scratch root to /tmp; it was stopped with safekill, its scratch dir removed, and the rows re-run with TMPDIR inside the worktree.
