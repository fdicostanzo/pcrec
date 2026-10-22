# langfix2 — the defects the blinded adversary langmisc found (2026-10-22)

Lane langfix2 (opus), branch `lane/langfix2` off `lane/langfix` @ 208dd3450
(which carries `langmisc_report.md` and its evidence). Brief: fix F1-F6, document
F7/F12, fix the trivial ones among F8-F11/F13/F14 and list the rest. Parked on the
branch for review, not merged.

## STATE AT HANDOFF

- Code, corpus, sabotage rows, re-pins, spec hunks, CLAUDE.md entries and
  K122-K127 committed (WIP commits, then this report).
- Rulings file `langfix2_rulings.md`: last entry applied is **R1** (F5 = option B,
  a doc fix with no gate; K126 CLOSED). The gate patch built before R1 was
  parked as `build/lf2/k126_gate.patch` (untracked) and never committed.
- VALIDATION OWED (queued with `scripts/boxqueue add`, dry-runs passed):
  - `698-langfix2-test`: make -j16, make strict, `scripts/perfrun --label
    langfix2` make test, then make's own red-line grep. Completion =
    `== 698 step verdict OK`; log = the job's run dir under
    `worktrees/.boxqueue/` (`job.log`, make's output in `job.log.make`).
  - `698-langfix2-mech`: S136 S1450..S1455, after langfix2-test. Completion =
    `== mech run COMPLETE: 7 rows`. Every new row's figure is PREDICTED.
  - The `--ready` gate holds both jobs while `i2build-parity` is pending or
    running. It had ended (green) by the time the jobs were queued, so the gate
    answered 0. Its 75 arm is the same `case` line 695-langfix uses.
- Run here by hand, green (named files): `bash tests/harness/run.sh` on each
  new corpus file: possessive_ungreedy 46/0, lookbehind_group_alt 38/0,
  optrun_group 25/0, octal_wide 25/0, inlookaround_self 24/0. On main's
  binary (`/home/pcrec/projects/pcrec/build/pcrec`) they score 18/28, 7/31,
  4/21, 4/21 and 14/10, so every file detects its fix.
  `python3 tests/harness/verify_rxt.py` reports 0 failures on each file.
  `bash tests/rxtsource/run_rxtsource_tests.sh` is green after the re-pin
  (291 files / 5926 blocks / 71492 lines; the C3 pins are re-pinned too).
  `bash tests/spec_history/run_spec_history.sh` passes 11/0, and so do
  `compliance_section.py --write-annotations` / `--check-annotations`.
  `VALIDATE_ONLY=1 run_sabotage_matrix.sh` passes on all seven rows.
- NOT run here (box rules: a timing window was live): make strict,
  test-codegen, test-cli (3 new assertions), test-reject, the startset
  manifests, the size tripwire and the axes allowances. The five new corpus
  files can move population pins beyond rxtsource, so a red in
  test-startset/test-corpus's tripwire is a RE-PIN owed, not a defect (BOILERPLATE
  "Delivery bar").
- Emitted bytes: no change expected for any pattern that was right. K122
  changes text only for `(?U)` + a possessive suffix, which was the wrong
  answer. K123, K124, K125 and K127 change only patterns that used to be
  refused or hit an internal error. The VM's lookbehind emitter now gets the
  same branch array from a shared helper. No abi event.
- INCIDENT, repaired: a `git stash` / `git stash pop` I ran to check a file had
  nothing to stash, so the pop took the repository's shared top stash ("WIP on
  main: 62ca83389 K113 landing", a `docs/dev/artifact_size_log.tsv` rewrite)
  into this worktree. I restored that file to HEAD and put the entry back on
  the stash list with `git stash store` (same commit 34617d1806d9, same
  message). `git stash list` shows it as `stash@{0}`. Nothing of it was
  committed here.

## What changed, per finding

1. **F1 / K122, the wrong answer: FIXED.** `p_rep` (parse.c) desugars `X q+` to
   `A_ATOMIC(A_REP)` and kept the `(?U)`-inverted greed, so `(?U)a*+` was
   `(?>a*?)`. The possessive arm now forces `greedy = true`. Probed against
   libpcre2 10.46 on both engines, plus `--engine=dfa --no-captures`: every
   suffix form (`*+ ++ ?+ {n,m}+ {n,}+ {,m}+`), groups with captures, scoped
   `(?U:)`, and the lazy-`?`-under-`(?U)` control (`(?U)a+?b??`, still greedy).
   All agree. Corpus `tests/atomic_groups/possessive_ungreedy.rxt` (every block
   on the default engine and `engine vm`); sabotage S1450.
2. **F2 / K123, the internal error: FIXED at the root.** A non-capturing or
   scoped group parses to a bare `A_ALT`, the same kind as the lookbehind's
   top-level spine. Both spine walks (`la_widths` and `vm_look_behind`) peeled
   A_ALTs until none was left, so they took the group for spine. One split,
   `pcrec_lookbehind_branches` (mod_lookaround.c, declared in internal.h),
   peels exactly `nbr - 1` nodes, the count the parse reported, and both
   readers call it. The "shorter" internal error stays; the "longer" one is
   gone because it cannot be told apart from a legal first-branch group.
   Same-length groups now compile and match libpcre2 (first branch, later
   branch, `(?i:`, `(*plb:`, negative, captures, nesting, utf8). Groups of
   different lengths get §7.4's capability refusal, the answer
   `(?<=(a|bc))x` has always had; libpcre2 accepts those as variable-length
   lookbehind. STOP RULE not triggered: no other answer moves. S136 is
   re-aimed (same text, SAB_COUNT 2 -> 1). Corpus
   `tests/lookaround/lookbehind_group_alt.rxt`; sabotage S1451.
   **Simplification candidate (not done):** `lower_enc.c` wraps a multi-branch
   UTF-8 class replacement in `A_CAT(A_EMPTY, alt)` purely so this walk would
   not misread it. The general split makes that wrapper redundant, but removing
   it moves emitted bytes (an abi event), so it is left in place and named here.
3. **F3 / K124: FIXED.** The bare option run's `not_repeatable` flag reached
   the quantifier for two reasons: a non-capturing or scoped group returns
   its body node, and four wrappers copied the flag up (A_CAP in parse.c, the
   named group, atomic, lookaround). `pcrec_wrap_bare_anchor`, which every
   body-carrying group calls at its `)`, now also seals a `not_repeatable`
   body. The four copies are deleted. `a(?i)*` is still err 109. Corpus
   `tests/modifiers/optrun_group.rxt` (accepted spellings plus the two err-109
   `perr` controls); sabotage S1452.
4. **F4 / K125: FIXED.** `pcrec_clsport_octal`'s ceiling was a literal 0xff.
   It now uses the encoding's universe (`cls_universe`), the same range check
   `\x{...}` takes. The fix covers the class position, the atom position and
   the digit rule's octal reading, because all three use this one scan. Byte
   mode is unchanged (err 151, same offset). Corpus `tests/utf8/octal_wide.rxt`;
   sabotage S1453.
5. **F5 / K126: CLOSED, doc fix (R1).** I built and measured the gate first
   (`-i requires module 'modifiers'`, the same shape as `--ucp`). It would have
   refused every library caller that sets `PCREC_CASELESS` with `features`
   NULL (match_api §8.2¶9 means no module), and 26 corpus blocks plus their
   startset-manifest rows and the PC-4 harness. On the R1 ruling I wrote
   pattern_language.md §2.3¶5a (new) and rewrote §6.2¶4. Case folding is base
   machinery (`cls_casefold` and `fold_rows` in parse.c, core/fold.c), which
   is what R1's condition required. Nothing else changed.
6. **F6 / K127: FIXED (refused).** pcrec's acceptance was not worth defending:
   the artifacts answered no-match or `PCREC_ERR_FRAMES`. I measured
   libpcre2's rule over 20 probes. A lookbehind is refused when its length
   computation reaches a group that contains the lookbehind anywhere, a
   lookaround included (`(a(?=(?<=(?1))))`). The search follows the body's
   calls and each callee's calls. It does not follow calls inside a nested
   lookaround (`((?<=(?2))a)(b(?=(?1)))` and `(?<=a(?=(?R)))x` compile).
   A call under `{0}` or inside an atomic group still counts.
   `pcrec_callgraph_lookbehind_recurses` (callgraph.c) answers that question.
   `pcrec_postresolve` passes the answer to `pcrec_lookaround_fix_widths`
   (new `bool` parameter), which refuses as UNBOUNDED at the recorded offset,
   ahead of the width rule. All refusal offsets equal libpcre2's. Corpus
   `tests/recursion/inlookaround_self.rxt`; sabotage S1454 (the check is
   deleted) and S1455 (lookaround calls are followed).
7. **F7: documented**, §9¶4a: where libpcre2 returns RECURSELOOP, pcrec runs
   the search and answers a match, no match, or a give-up. Measured:
   `(?:a|(?R))+` gives `[0,1)` on `a`, `[0,2)` on `aa`, and FRAMES on `b`.
8. **F12: documented**, §9¶5a (a mid-character startpos under utf8 returns
   `PCREC_ERR_STARTPOS`, -7; libpcre2 returns `[2,3)`).
9. **F13: FIXED (doc)**, cli.md §1.11¶1 and the `--help` text. Measured:
   `--no-captures` forces no engine. Under auto, `(a)(b)` builds a DFA,
   `(a)\1` builds a VM, and `--engine=vm --no-captures` builds a VM.
10. **F14: FIXED (trivial).** `--features=LIST` is now accepted (cli/main.c,
    the `--engine=` shape). A trailing comma is now refused as the empty
    module `''`, like a leading or doubled one. Before, enabled.c's
    `while (*p)` loop dropped the empty name. cli.md §1.17¶1 has the spec
    hunk; there are 3 assertions in tests/cli/run_cli_tests.sh case10. No
    corpus or script used a trailing comma (grep).
11. **F10: documented** in §6.2¶3: only SETTING a gated letter is refused.
    Unsetting one (`(?-m)`, `(?-J)`, `(?-r)` under utf8) compiles, because it
    enables nothing the module owns. Measured: `(?-m)a` compiles under std1
    and `(?m-m)a` is refused.

## Candidate rows (not fixed: not trivial, or not pcrec's)

- **F8, refusal SHAPE for unknown `\p` names** (`\p{Foo}`, `\p{InGreek}`,
  `\p{gc=L}`, `\p{Hrkt}`, `\p{Katakana_Or_Hiragana}`) and for `\c` at the end,
  `[\c]`, and `\N{U+41}` under byte. pcrec answers shape 2 ("enabled but not
  implemented"); libpcre2 answers a grammar error (shape 7). The uprops split
  is deliberate (parse/CLAUDE.md: "refusals split by gate state",
  `Katakana_Or_Hiragana` declined) and pinned in tests/reject/. Telling
  "unknown to PCRE2" from "known but unbuilt" needs a name census against
  10.46, which is a uprops row, not a few lines. Tier: D26 says the WORDING
  is not exact; this is the SHAPE claim (§2.4) only.
- **F9, `\p{ ^Greek}` / `\p{ ^L}`** (a space before the caret) are refused;
  libpcre2's loose matching accepts them. The fix lives in the uprops scanner,
  whose caret rule and blame offsets are pinned ("scanner algorithm
  unchanged"). Small, but it touches a pinned scanner; it is a row.
- **F11 is not a pcrec finding.** `pcrec -o - --pattern $'\xe9'` exits 0
  here. The adversary's exit 125 and "invalid UTF-8 was detected in one or
  more arguments" come from the uutils `timeout` it wrapped calls in, which
  refuses non-UTF-8 argv (BOILERPLATE: this box's bare `timeout` is uutils).
  No action.
- **lower_enc.c's `A_CAT(A_EMPTY, alt)` seal** (see F2): retirement is an
  abi event plus a re-pin; it qualifies as a simplification.

## Compliance rows

No row's status changes. The possessive, lookbehind and recursion rows stay
`OK-GATED`/`OK-LIMITED`; these were defects inside shipped rows. The octal
annotation (FIX-3/K13 record) now says err 151 applies under byte only and
utf8 accepts U+0100..U+01FF. Re-rendered with
`compliance_section.py --write-annotations`.

## Files

src/parse/parse.c (K122, K124, K125), src/parse/mod_lookaround.c (K123, K124,
K127), src/gen/emit_vm.c (K123), src/opt/callgraph.c + src/opt/postresolve.c
(K127), src/parse/mod_named_groups.c + mod_atomic_groups.c (K124),
src/core/internal.h, src/parse/enabled.c + cli/main.c (F14, F13 help);
docs/spec/pattern_language.md, docs/spec/cli.md; docs/dev/known_issues.md;
docs/pcre2_compliance{.md,_annotations.txt}; five corpus files above;
tests/rxtsource/run_rxtsource_tests.sh (re-pin), tests/cli/run_cli_tests.sh;
tests/mech/sabotages/S136 (re-aim) and S1450-S1455; CLAUDE.md of src/parse and
tests/{atomic_groups,lookaround,modifiers,recursion,utf8}.
