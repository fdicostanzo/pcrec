# ctxbuild — [DD-11.5] part 2, P2a-P2c: the (?m) fold (delivery report)

Lane ctxbuild (opus, engine code), 2026-10-18/19, branch `lane/ctxbuild` from main
`5fd84491d` (abi 80). Design: `docs/design/ctx_span.md` rev 2.1 §4, §6, §7; rulings D168
+ addenda 1-3. Build go: Frank, 2026-10-19, P2a-P2c only. **P2d/P2e and part 1 are not in
this lane.** Box rule: light checks only, all before 00:45; NO heavy check ran (no
`make test`, no mech, no full emit_sweep, no test-axes). Everything heavy is in §6, owed.

## 1. What landed, per step

| step | commit | what |
|---|---|---|
| P2a | `25dbef7bf` | `src/core/ctxfn.def`: the one 9-cell table, the six four-cell rows re-encoded (absent copied from out), value derived from the grid (`CTXFN_GRID`) and `_Static_assert`ed against the stated hex. `Ast.u.ctx.fn`, `NState.ctxfn`, `pcrec_ast_ctx`, `look_fn`, `pcrec_poss_ctx_admits`, the VM form key widened to `uint16_t`; `vm_ctx_forms` generated from the table. `Sides` gains `left_abs`/`right_abs`, set per direction in `sides_of` (A1); the N_CTX arm indexes `3p + q` and takes absent ONLY where the row reads it (R1). The three derived predicates (`ctxfn_reads_absent_prev/_next`, `ctxfn_reads_membership`) landed here because the gate reads them. |
| P2b | `c687ce466` | rows `MLINE_BOL` (0x1D8) / `MLINE_EOL` (0x1B6) and VM forms `VMCTX_MLBOL/MLEOL` (today's text and role strings verbatim); `pcrec_nfa_has_bot` and the `has_end` hoist read the predicates on N_CTX; a reverse machine meeting an absent-prev row is an internal error (R1's consequence); possessify never narrows an absent-reading row (in `pcrec_poss_ctx_admits` AND in `ps_node`'s gate recording — see §4 F-3). Nothing builds the new rows. CK-8 (`tests/assertions/ctxfn_table_check.py`, assertions §1b); `ctx_admits_check.c` over all 512 rows × 7 masks. |
| P2c | `9f7cb74e3` | the parser builds `A_CTX({\n}, MLINE_BOL/EOL, anchor)` for `(?m)^`/`(?m)$` (no lookbehind raise, A8) through a one-row newline-convention table that refuses a multi-byte newline by name (R3; population 0). Tables A-B deleted: `Ast.u.anch` + its 73-line comment, every multiline reader (nfa, possessify, derive ×2, startanch, endwin ×2, widths ×2, emit_vm ×2 hand arms, mod_assertions pin), `N_BOT_M`/`N_EOL_M`, the two closure arms, `CTXROW_NEWLINE` + `cr_nl_*`, `nl_bit`, `PCREC_NO_MLINECTX`, the dead `rows` mask (`PcrecCtxSet.row`, one row). Comment census: the §4.4 recipe over `src/` code AND comments reads ZERO. Registry `^`/`$` descriptions + the compliance index rewritten. `run_mlinectx_identity.sh` retired (Makefile, `san_scripts.txt`, mech arm); `run_wordctx_identity.sh` population re-defined (A2). abi 80 → 81 (§3). Sabotage: §5. |
| pin | (this report's commit) | `run_recursion_identity.sh` FILEPIN self-pinned to `9f7cb74e3` (manager re-pins to the merge). |

**Departure from the design's step split**: the design put the predicates and three-valued
`Sides` in P2b and the gated index in P2a; the gate reads the predicates, so all three
landed in P2a. Both commits are zero-mover either way.

## 2. Light checks run (times local, all before 00:45)

| time | check | result |
|---|---|---|
| 22:01 | baseline `make -j16`; base binary saved | ok |
| 22:07, 22:13, 22:36 | light probe (scratch, not committed): the 2,451 corpus patterns carrying an assertion spelling, base vs new, at default / `--engine=vm` / `-e utf8` / utf8+vm / `--emit-ir`, byte-compared (abi digits normalized at P2c) | P2a: 0 differ on every arm. P2b: 0. P2c: **1 mover**, `(?m)^a\|\B`, at default and utf8 (0 VM, 0 IR) |
| 22:23 | that mover's diff | per-atom tables AND, on ENG_ATTEMPT, permuted state bodies (`last_accept_position` moves between state labels): see §4 F-2 |
| 22:24 | mover answer check: `--emit-main` base vs new over all 1,365 subjects of `{a,\n,x,-}` up to length 5 | 0 differ |
| 22:08, 22:11, 22:31 | `make strict` after each step | clean |
| 22:09, 22:31 | `tests/registry/limits_check.sh` | 37/0 |
| 22:12, 22:31 | `ctx_admits_check.c` | 189,958 cells agree (absent-reading 184,016, every outcome non-zero) |
| 22:13, 22:31 | CK-8 `ctxfn_table_check.py` | 8 rows × 9 cells, canonical + native spellings: 0 failures; planted `MLINE_EOL` out/absent flip: reported by row and cell (failing direction) |
| 22:10 | R1 plant reach (gate dropped, both sides) | 88 utf8 artifacts move, 0 byte; answers unchanged (5 witnesses × 1,555 subjects) |
| 22:14 | the design's R1 witness `\bfoo\b -e utf8` under the plant | **does NOT move** (§4 F-1); `(?:\w*?)*\b` does (no end view clean, one under the plant) |
| 22:21 | `compliance_section.py --check`/`--names` | pass (142 rows) |
| 22:27-22:29 | `run_wordctx_identity.sh` (new population) | identity 3,570/3,570; control 485 differ, 0 unexplained, 83 `(?m)` patterns joined the control. (A 22:24 run read 954 differing: my own abi bump landed mid-run, reference and subject from different sources; re-run clean.) |
| 22:30-22:32 | `run_endvar_identity.sh` (kept) | 4,026/4,026 identical; control 154 differ |
| 22:35 | harness on `tests/assertions/multiline.rxt`, `gate.rxt`, `d27/multiline.rxt`, `tests/ucp/ctxnode.rxt`, `tests/compound/split.rxt`, `tests/possessify/possessify.rxt` | all 0 failed (multiline 3,325; split 13,839; possessify 3,537 passed). The 27-file `(?m)` set at once exceeded the 170 s cap and was cut: OWED in `make test`. |
| 22:3x | assertions §1c (R1 cell + A8 cell) run from the section by hand, clean and planted | clean PASS; S341 plant FAIL as designed |
| 22:40-22:45 | `run_recursion_identity.sh` vs the self-pin | cut by its 300 s cap after the default-axis positive control PASSed (it is a heavy gate, not a light one); OWED in the validation lane |

## 3. The abi event (80 → 81), readers by §4.5.1's grep

Moved: `src/gen/emit_dfa.c` define; `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT` (+
its message's transition list); `tests/mech/sabotages/S693` BEFORE/AFTER; `docs/spec/match_api.md`
§1¶7 (both lines), §6¶1, §6¶17; `docs/dev/history/abi_changelog.md` (new entry);
`docs/design/kit_proof.md` §6.1's B1 row ("the abi at B1's parent + 1");
`run_recursion_identity.sh` FILEPIN (self-pin). RECORDS left: `memfn/docs/journal.md`,
`src/gen/CLAUDE.md` e1fix line, `plan.md` [ENTRY-TABLE], kit_proof's header and `foobar`
paragraph, `docs/design/CLAUDE.md`, `docs/measurements/*`, `tools/review/out/*`.
**The kit's `memfn/docs/wake.md` ("pcrec abi is 80") is the kit session's file: tell the
kit at merge** (not edited here). Byte-count readers (startset manifests, form-census
floors, emit_sweep pins, size tripwires) are OWED to the validation lane.

## 4. Findings

- **F-1 (the design's R1 witness does not reach).** `\bfoo\b` under `-e utf8` emits the same
  bytes with and without the R1 plant (`endvar` not interned). The reaching witness is
  `(?:\w*?)*\b` under `-e utf8` (no `_forward_end_view` clean, one planted), with control
  `(?:\w*?)*(?m)$`; that pair is assertions §1c and S341's reach.
- **F-2 (CK-4(b)'s confinement is too narrow).** The one mover, `(?m)^a|\B` (ENG_ATTEMPT),
  changes per-atom tables AND the computed-goto engine's STATE BODIES (state numbering
  follows atom order), e.g. `last_accept_position = scan_position;` moves between labels.
  Answer-identical. CK-4(b) as written ("any other differing line fails") would fail it;
  the validation lane should allow a state permutation on ENG_ATTEMPT (CK-5's "modulo the
  predicted permutation" applies to the program too).
- **F-3 (possessify's decline needed a second site).** `ps_node` records every A_CTX as a
  gate group; an absent-reading row would join a group with a same-set four-cell gate
  (`(?=\n)`) and its pm-0 skip differs from today's all-bytes contribution. `ctx_valued`
  keeps such rows out of the gate summary, so they contribute `first_of`'s widened bytes,
  exactly the retired multiline value. Not in the design's edit set.
- **F-4 (a truncation the design's table C missed).** `ctxnode.c`'s `look_fn` returned
  `uint8_t`; `CTXFN_NOT_PREV` is 0x1C7 in the 9-cell encoding, so without the widening
  `(?<!C)` would have silently become another function. Widened in P2a.
- **F-5.** `PcrecCtxSet.rows` → `row`; a set contributed by two rows is now an internal
  error (design: impossible, no byte-expressible A_CTX set equals utf8's non-start set).
- **F-6.** The newline-convention refusal (R3) is a one-row table in `parse.c`
  (`nl_convs[]`, LF); no convention option exists, so the refusal is unreachable and has
  no spec hunk (nothing a caller can select). It becomes observable with [DD-11]'s
  convention row.

## 5. Edit set regenerated from the real diff (R4), and the sabotage population

`docs/design/ctx_span/regen_edit_set.py` → `edit_set_build.tsv` (91 distinctive removed
code lines; 35 non-distinctive lines like `}`/`return r;` left out, as the anchor map
matches substrings tree-wide), compared in `edit_set_compare.txt`:
- planned, not made: `def Sides` at P2b — made at P2a, and insert-only (no removed line).
- made, not planned (60 lines): all are the BODIES of planned edits (the two VM hand arms,
  the closure arms, the `rows` loop, the `anch` struct braces, possessify's multiline
  `First`, parse.c's `return a; }`), plus the abi define, `PcrecCtxSet.name/.rows`, the
  registry strings, and four unplanned-but-required ones: the `pcrec_ast_ctx` PROTOTYPE,
  `look_fn` (F-4), `ps_node` (F-3), the old closure index line `(st->ctxfn >> in)`.
  Each justified; none removed.

`derived_rows_build.tsv` (`derive_rows.py` over `sabotage_anchors_build.tsv`, base tree
`5fd84491d`, `call_graph_build_base.txt`) = the design's population plus **S69, S882**
(owner `make_state`, P2a's `sides_of` call) and **S693** (the abi anchor, re-aimed).
Dispositions:
- RETIRED (files deleted): S76, S77, S343, S762, S900. Witnesses kept as corpus cells:
  S77's in `tests/assertions/multiline.rxt` §4b, S343's in `tests/ucp/ctxnode.rxt`, S900's
  in `tests/compound/split.rxt`; S762's `(?m)$` decline cells live in
  `tests/assertions/end_window.rxt`/`rev_end.rxt` (not re-verified to be the same cell —
  OWED check).
- RE-AIMED: S341 → R1's plant (detector assertions §1c); S693 (abi 81/80).
- NEW (S1151-S1161, ledger range S1151-S1170; S1162-S1170 unused): S1151 (S341's former
  s0 plant, kept), S1152 (SP-4), S1153 (SP-4b), S1154 (SP-4c), S1155 (SP-4d/A8), S1156
  (possessify narrows absent rows), S1157 (has_bot ignores the row), S1158 (SP-8), S1159
  (has_end ignores the row), S1160 (SP-11, declared UNREACHED), S1161 (VM `(?m)^` loses
  `pos < n`). Every anchor verified present exactly once; every figure OWED.

## 6. THE OWED HEAVY-CHECK LIST (post-window validation lane)

1. `scripts/perfrun --label ctxbuild -- LOG` (`make test`). Expected: green. Sections that
   count most: assertions (incl. §1b CK-8, §1c R1/A8), codegen (`ABI_EXPECT=81`), registry
   (compliance index), rxtsource, startset, ucp (ctxnode), possessify (ctx_admits 512×7),
   compound, endmark, recursion identity (FILEPIN self-pin; re-pin to the merge). Likely
   re-pins: byte-count manifests that include the mover class (startset manifests,
   `run_form_census.sh` floors, size tripwire) — re-pin by recompiling witnesses.
2. `scripts/emit_sweep.py` against `5fd84491d`, every arm incl. `--arms start` and
   `-e utf8`: expected movers = ONLY DFA artifacts with a `(?m)` node before a different
   A_CTX set in NFA order (CK-4(a)); prediction from text, `mlscan.py` + NFA order. Light
   probe found exactly `(?m)^a|\B`. VM / route / possessify movers asserted ZERO (CK-4(c)).
   Confinement (CK-4(b)) with F-2's state-permutation allowance.
3. mech rows: S341, S693, S1151-S1161 (new/re-aimed; S1160 expects UNREACHED); re-run
   S71, S1100, S14, S746, S157, S49, S84, S365, S86, S613, S761, S893, S904, S69, S882;
   witness re-runs with reach re-verified: S218, S222, S235, S463, S470, S490, S608, S617,
   S78, S81, S82. Plus the [SABANCHOR] count gate (five rows deleted, eleven added).
4. CK-5: machine identity (forward + reverse tables, `eolvar`/`endvar`, views flag) base vs
   P2c for every `(?m)$` ENG_UNANCH artifact, every `\b`-ending reverse-pass artifact
   (`[a-z]+\b` at `n`), every utf8 copied-row `has_end` artifact; list-order movers compared
   modulo atom permutation.
5. U-B3: `PCREC=build/pcrec python3 -I docs/design/kit_proof/conj.py` on P2c's tree must give
   an IDENTICAL cover census and `why` per pattern (`conj.txt` A/B/D).
6. `make test-axes` (opt-in), every axis answer-identical; `run_mline_diff.sh` sweep.
7. A4's three possessify cells (`a{0,3}(?m)$`, `(?m)^a+b`, `[a\n]+(?m)$\n`) are NOT yet in
   `tests/possessify/` (adding corpus cells moves population pins that need `make test`
   to re-pin): add them in the validation lane, both oracles.

## 7. D62 addendum text (for the manager to add; decisions.md not edited)

> ### D62 addendum — the modifier resolves into the CHOICE OF NODE ([DD-11.5] P2c, D168 add. 1; lane ctxbuild, 2026-10-19)
> - **Ruling superseded:** "multiline-`$` is a parse-resolved FLAG on the node" no longer
>   holds. The parser resolves `(?m)` at the `^`/`$` itself into WHICH node it builds:
>   `(?m)^`/`(?m)$` are `A_CTX` rows (`MLINE_BOL`/`MLINE_EOL`) of the one 9-cell truth
>   table `src/core/ctxfn.def`; a plain `^`/`$` is `A_BOL`/`A_EOL` with no payload.
>   `Ast.u.anch.multiline`, `N_BOT_M`/`N_EOL_M` and their arms are deleted.
> - **Principle kept:** kinds encode structure, and a kind is still never doubled per
>   modifier (no `A_EOL_M`); the modifier maps onto an existing GENERAL kind with data.
>   `$`/`\Z`/`^`/`\A` keep their AST kinds as structure (P2d/P2e, D168 add. 3, decide
>   `\A`/`\z`).
> - **Control 3 retired:** its residual (an analysis matching `case A_EOL:` and forgetting
>   the field) has no field to forget; `(?m)` anchors reach every exhaustive switch as
>   `A_CTX`, which `-Wswitch` already forces each analysis to classify.

## 8. Files

Code: `src/core/ctxfn.def` (new), `internal.h`, `src/ir/{dfa,nfa}.c`, `src/gen/{emit_vm,emit_dfa}.c`,
`src/opt/{possessify,derive,revdet}.c`, `src/facts/{kset,startanch,endwin,widths}.c`,
`src/parse/{parse,ctxnode,mod_assertions,mod_modifiers,registry,definitions}.c`, `parse_mods.h`,
`Makefile`. Checks: `tests/assertions/{ctxfn_table_check.py,run_assertions_tests.sh}`,
`tests/possessify/ctx_admits_check.c`, `tests/codegen/run_wordctx_identity.sh` (population),
`run_mlinectx_identity.sh` (deleted), `run_recursion_identity.sh` (pin),
`tests/mech/sabotages/S341,S693,S1151-S1161` (+5 deleted). Evidence:
`docs/design/ctx_span/{regen_edit_set.py,edit_set_build.tsv,edit_set_compare.txt,sabotage_anchors_build.tsv,derived_rows_build.tsv,call_graph_build_base.txt}`.
