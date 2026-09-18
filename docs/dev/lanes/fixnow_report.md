# fixnow — [REVW.FIX] the code review's FIX-NOW pile, landed

Authority: `docs/dev/reviews/2026-09-17-code-review.md` §1. Ten items, in the
synthesis's own order, one commit each, each independently validated before
the next. Branch `lane/fixnow`, PARKED (not merged) per the brief.

## Item-by-item

### 1. L8-F1 — Ctx back-pointer on `Job.scr_test`/`scr_desc`

`src/core/compile.c:756-762`'s comment described a COUNT ("the four Job
buffers") where the actual rule is that every `StrBuf` the `Job` owns gets
`.cx = &cx` as soon as the `Job` exists. `scr_test`/`scr_desc` (added by
`[ART-SIZE]` after K7 closed) were missed — a live caller-`abort()` on OOM,
reachable from an ordinary VM-route compile. One line added, comment
reworded to state the rule. Validated: clean build, tests/rxtsource 212/0.

### 2. L5-R0.2 — cpset/mrl unit checks join the sanitizer manifest

`tests/codegen/run_cpset_structure.sh` and `tests/mrl/run_mrl_tests.sh` had
never been built under a sanitizer — added to `tests/lib/san_scripts.txt`
(2 lines). Validated: both scripts pass standalone (28/0, 27/0); the
manifest's own `[TT-9]` structural check in `run_codegen_tests.sh` still
passes (109/0 total).

### 3. L9-P2/P7/P8 — `lib/pcrec.h` header sweep

P2 (CORRECTNESS-RISK): `PCREC_ENC_UTF8`'s comment said "not yet implemented
(arrives with milestone M5)" — [M5.0] shipped. Replaced with the accurate
line pointing at `match_api.md` §8.2. P7: `RX_NCAPS`/`RX_PUSH`/`RX_SET`
(7 sites) genericized to `<PREFIX>_*` inside contract prose that uses that
spelling everywhere else. P8: deleted the false "order of magnitude" claim
(250,000 vs 1,000,000 is 4x, and was 4x at the commit that wrote the
sentence — verified via `git show`). Checked docs/spec/ for the same stale
claims (D80): none found. Comment-only. Validated: clean build,
tests/rxtsource 212/0.

### 4. L8-F2 + L8-F5 (+ L10-L10-8) — libdirs leak; write ferror coverage

`cli_parse`'s own failure returns leaked `st->libdirs` at both call sites
(`main`'s top-level parse, `apply_target`'s per-target `pcrec` config-line
parse) — fixed by freeing before return at each site. `write_file`'s
`fputs` return/`ferror(f)` were unread; added `ferror(f)` before the
existing `fclose` check. The `-o -` stdout path had no write-error coverage
at all (`pcrec -o - PAT > /full/disk` exited 0 having written nothing) —
added `fflush`/`ferror(stdout)` after both `fputs(out.c_src, stdout)` call
sites. This discharges L10-L10-8 (duplicate finding, same gap). A3: 0
sabotage rows bind to either site. Validated: clean build; tests/cli
284/0; tests/rxtsource 212/0; manually reproduced the leak scenario
(`--lib-path /tmp --bogus`, exit 1 unchanged, now leak-free). ENOSPC
reproduction not possible on this darwin box (no `/dev/full`; `ulimit -f`
raises SIGXFSZ rather than a returned write error) — verified by code
inspection against the review's exact suggested shape instead.

### 5. L3-F3 — FNV-1a constant pair, 9 sites → one helper pair

`dfa.c`'s `dhash` and `minimize.c`'s signature hash open-coded the FNV-1a
32-bit fold (init `2166136261u`, mix xor-then-multiply-`16777619u`) seven
times with nothing naming the algorithm. Added `fnv1a_32_init`/
`fnv1a_32_mix` (`src/core/internal.h`, beside `cls_set`/`cls_has`) —
byte-preserving by construction (same arithmetic, same order). The
per-class-view golden-ratio salt in `dhash` is NOT FNV-1a and stays
open-coded per the review's own warning. The two 64-bit sites
(`lctx_slot`/`pmemo_slot`) use the FNV 64-bit prime as a plain
Knuth-style multiplier — a different shape — named as
`PCREC_HASH64_MUL` with a comment explaining it is not the FNV-1a mix.
Validated: clean build; emit-diff on 4 patterns (including one exercising
`dhash`'s salted term and one exercising `minimize.c`'s signature hash)
byte-identical before/after; tests/rxtsource 212/0;
tests/codegen/run_cpset_structure.sh 28/0.

### 6. L3-F5 — "missing closing ) for group" → one `#define`

Eight sites carried the identical string (base grammar, `ext.c` x2, and
five modules) — not "a different message per module" as
`parse.c:1902`'s own comment claimed. Deduped onto
`PCREC_MISSING_CLOSE_PAREN_MSG` (`internal.h`, beside `REFUSE`). NOT a
diagnostic-wording change: byte-identical text at every site, verified
live (all eight constructs re-triggered, output unchanged) and by grep.
Corrected the `parse.c:1902` comment (and the identical claim in
`src/parse/CLAUDE.md`) to state the real shared clause: ownership, never
wording. `registry_check.c:1482` (the "undeclared ninth home") now
references the same macro. **Fixed a stale check found while
validating**: `tests/parse/run_parse_tests.sh`'s "exactly one home" check
grepped for the literal string inside a raw `ctx_fail(...)` call, which is
exactly the spelling this change replaced at the base grammar's own site
— updated the grep to match the macro (or a reintroduced literal),
preserving the check's real invariant (exactly one raw `ctx_fail(...)`
call site; everything else routes through `REFUSE`). Validated: clean
build, make strict clean; tests/reject 615/0; tests/parse 9/0 (was 8/1
before the check fix); tests/cli 284/0;
tests/registry/run_registry_tests.sh exit 0, no FAIL lines (backgrounded,
>120s runtime); tests/rxtsource 212/0.

### 7. L4-C1 + C2 — headers for the 43 headerless ≥50-line functions

Header coverage inverts with function length tree-wide (67.6% at 25-49
lines down to 12.5% at ≥200). Re-derived the 43-function population
independently against `tools/review/out/function_census.tsv` rather than
trusting the report's copied count — the census's own `start_line` is off
by one to several lines on 7 of the 76 ≥50-line rows (multi-line
signatures, long preceding comment blocks that confuse a naive
brace/comment walker), corrected by grepping each real signature; the
re-derived count matches 43 exactly (see the population note below). One
1-9-line header per function, sized to it, hoisting text already inside
the body where it existed. C2 rides the same commit: moved `emit_attempt`'s
misplaced section banner's implication by giving `emit_target` (the
4-line helper the banner sat on) its own one-line comment and
`emit_attempt` its own header; the banner itself is untouched.
Comment-only: no code line moved, nothing an anchor could quote was
touched (pure insertions above signatures). Validated: clean build, make
strict clean; `tests/codegen/run_codegen_tests.sh`'s SABANCHOR check — all
261 sabotage rows' anchors still resolve; emit-diff on 8 diverse patterns
byte-identical before/after; tests/possessify 18/0, tests/rungselect
24/0, tests/altcls 15/0 (the three differential suites covering the
analysis passes touched by the header insertions); tests/rxtsource 212/0.

**Population note**: my re-derivation script is
`/private/tmp/.../scratchpad/find_headerless2.py` (session-scratch, not
committed — a fresh agent re-deriving this population should write its
own rather than trust this note). The 43 functions, file:line at commit
time (before this lane's own insertions shifted later lines — grep each
name fresh):

`src/gen/emit_vm.c`: `pcrec_emit_vm`, `vm_render_listing`, `vm_emit`,
`vm_revdet_rep`, `vm_cost`, `vm_rev_emit`, `vm_rep`, `vm_isl_emit`,
`vm_look` (9). `src/parse/rxt_source.c`: `pcrec_rxt_source_parse`,
`pcrec_rxt_source_tsv`, `pcrec_rxt_source_resolve`, `closure_walk` (4).
`src/core/compile.c`: `compile_driver` (1). `cli/main.c`: `main` (1).
`src/gen/emit_dfa.c`: `emit_attempt`, `emit_info_def`,
`emit_state_legend`, `emit_scan_edge`, `pcrec_emit_prologue`,
`emit_scan_loop` (6). `src/parse/axes_dump.c`: `emit_predicate_axes` (1).
`src/parse/rxt_compose.c`: `pcrec_rxt_compose` (1).
`src/parse/syntax_dump.c`: `pcrec_syntax_explain` (1).
`src/parse/mod_modifiers.c`: `pcrec_modport_optrun` (1). `src/ir/nfa.c`:
`compile_ast`, `trie_build` (2). `src/opt/select_engine.c`:
`pcrec_select_engine` (1). `src/opt/minimize.c`: `pcrec_minimize_dfa`
(1). `src/parse/parse.c`: `p_class`, `p_rep` (2). `src/opt/scanedge.c`:
`pcrec_scanedge_dfa` (1). `src/opt/callgraph.c`: `pcrec_callgraph_build`,
`cg_eligibility` (2). `src/opt/possessify.c`: `first_of`, `gk_build`,
`pss_walk` (3). `src/ir/dfa.c`: `pcrec_build_dfa` (1).
`src/parse/mod_backrefs.c`: `pcrec_bref_resolve` (1).
`src/parse/mod_named_groups.c`: `pcrec_ngport_declare` (1).
`src/opt/revdet.c`: `rd_reverse` (1). `src/parse/mod_lookaround.c`:
`pcrec_laport_group` (1). `src/gen/emit_dfa.c` again:
`pcrec_emit_prologue`, `emit_scan_loop` (already counted above). Total 43.

### 8. L6 §5 step 1 — `match_api.md` §8.0 links `-Wl,-dead_strip`

`libpcrec.a` statically reaches the whole `.rxt`-source composer/parser
from the ordinary compile path; a minimal consumer that never touches
`--source` pulls those objects in unless the linker drops unreachable
sections. Added the flag to the worked example plus a paragraph citing
the review's measurement (43,968 of 44,448 bytes recovered, no source
change). Verified live: rebuilt and ran the exact 8.0 example with
`gcc -Wall -Wextra -Werror -Wl,-dead_strip`, confirmed `matcher.c`/
`matcher.h` still emit and `matcher.c` still compiles clean. Docs only.
Validated: tests/rxtsource 212/0.

### 9. L4-A2 — `select_engine.c:496`'s superseded claim, corrected in place

The `[M6.4.2]` paragraph asserted "THE FREE DISCHARGE runs ONCE, before
the analysis loop" unqualified; fifteen lines below, a `[DD-14 wave G]`
paragraph says it moved to `compile.c`. This was the one site (of 48
comment blocks carrying a retraction ≥12 lines in) where the correction
was appended below rather than attached to the claim. Opened the
paragraph with "UNTIL [DD-14] WAVE G, ... ran ONCE HERE" per the review's
suggested wording; remaining prose reflowed, unchanged in content.
Comment-only. Validated: clean build, make strict clean; tests/rxtsource
212/0.

### 10. L1-X2 (the pilot) — merged `cg_walk`/`pr_walk` into `pcrec_ast_visit`

Re-grepped the anchor population on my OWN tree per the brief
(`grep -rl cg_walk tests/mech/sabotages/` → 2 files: S-U10, S171;
`grep -rl pr_walk tests/mech/sabotages/` → 0 files) — matches the
review's own count exactly, so no surprise population. `cg_walk`
(`src/opt/callgraph.c`) and `pr_walk` (`src/opt/postresolve.c`) were
confirmed byte-identical in logic (same switch, same kinds, same spine
loop) before merging — pasted verbatim into `pcrec_ast_visit`
(`src/core/internal.h`, `static inline`, beside `pcrec_ast_engines`),
with a combined header comment. Both files' local `typedef`+function
definitions removed; all 16 call sites (14 in callgraph.c, 2 in
postresolve.c) renamed to `pcrec_ast_visit`. Re-aimed S-U10 and S171's
`SAB_BEFORE`/`SAB_AFTER` (they quote the CALLER's text —
`cg_walk(root, cg_cwmin_publish, &m)` / `cg_cwmax_publish` — not the
walk's own body, exactly the review's "a rename reaches every row that
quotes the caller" lesson). Narrowed the `src/opt/CLAUDE.md` sentence the
merge contradicted (the "house style" claim that `callgraph.c` "carries
its own descent because what varies is which edges it follows" — false of
this pair, whose edges were identical; the four files it's still true of
keep their own descent). Also updated `docs/dev/coding_guide.md`'s
`[wave 2 / fix-now #10]` marker, now that `pcrec_ast_visit` exists (the
marker's own maintenance rule), and one leftover in-body comment in
`callgraph.c` that named `cg_walk` directly.

Validated: clean build, make strict clean; sabotage re-aim confirmed
against the COMMITTED HEAD (mech tests `git archive HEAD`, never the
working tree) via `bash tests/mech/run_sabotage_matrix.sh S-U10` and
`... S171` after committing — both DETECTED at their exact recorded
figures (`corpus:2fail/48pass` each, byte-for-byte the pre-merge
numbers, `anomalies: 0`); tests/lookaround/run_lookaround_diff.sh 5/0
(exercises `postresolve.c`'s width rule through `pcrec_ast_visit`);
tests/rxtsource 212/0.

`tests/recursion/run_recursion_diff.sh` (the most direct exercise of
`callgraph.c`'s 14 call sites, ~15,912+ cells across its later
sections) is a bonus thoroughness check beyond the brief's stated bar
— OWED, still running as this report is written. Log:
`/private/tmp/claude-501/-Users-fdicostanzo-pcrec/e376655c-1114-41d5-80a1-fba4416c13f0/scratchpad/recursion_diff.log`
(session scratchpad — read it directly; not committed). Through §3
(1,836 cells, 0 disagreements) it is clean; nothing past that had
printed at hand-off time.

## Full validation, after item 10

`make strict`: clean throughout, checked after every item.

`make test` (full suite, backgrounded per BOILERPLATE, launched as the
lane's last act): OWED. Log: `build/fixnow_test.log` in the worktree
(`/Users/fdicostanzo/pcrec/worktrees/fixnow/build/fixnow_test.log`).
Poll its tail for the `checks passed:`/`checks failed:` summary lines
and the `sections ran: N/M` completion trailer. Not yet complete at
hand-off.

## Rulings received

None — no ruling was requested or needed; all ten items were mechanical
per the synthesis's own ranking and none surfaced a design question.

## Skipped

None. All ten items landed as specified.
