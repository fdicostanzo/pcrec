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

## 9. Heavy validation (lane ctxbuild-val, opus, 2026-10-20)

Run on the Linux dev box after the bench window closed, one heavy run at a time. Step 0
merged main `6ce289976` (no conflicts). Logs are under `worktrees/ctxbuild/build/val/`
(gitignored). The REFERENCE for items 2/4/5 is main `5fd84491d` (the lane's base) built
from `git archive` TWICE: as-is (`build/base/`) and with `PCREC_ARTIFACT_ABI` relabelled
80 → 81 (`build/base81/`). Every abi-carrying emitted line derives from that one define
(checked on `ab+c`: the relabelled base and P2c emit identical C), so `base81` vs P2c
isolates the real movers from the abi digits without a normalizer.

### Item 7 — A4's three possessify cells (commit `d34ef5681`)
- `possessify.rxt`: `a{0,3}(?m)$`, `(?m)^a+b`, `[a\n]+(?m)$\n`, bare and capture-wrapped,
  in the `$`-follow family (D47.5's `(?m)` obligation, whose two stale "pcrec refuses
  `(?m)` today" comments now point at them). +6 blocks / +116 cells. Both oracles: libpcre2
  10.46 (`tests/fuzz/pcre2_oracle.c`) and python3 `re` agreed on every cell, python under the
  leading-`(?m)` spelling (a mid-pattern `(?m)` is a python error), so five blocks carry
  `# pcre2-only` and `(?m)^a+b` is C3-verified. Harness: 3,653 passed, 0 failed (was 3,537).
- possdiff: `arms_mline.txt` (the six patterns, `# features: all`) joins `ARMS_ENV_FILES`;
  `subjects_exh.py` adds a newline to the exhaustive alphabet when `mlscan.multiline_anchor`
  holds (no existing `arms_*` pattern has a `(?m)` anchor, so no other sweep moves). The
  manifest gains `hold/A4/*` (stamp 0) on the three: S1156's witnesses. File-only run: 6
  agreed, 21,302 cells, manifest 38/38.
- `mlscan.py`'s two docstrings still named `N_BOT_M`/`N_EOL_M`: reworded.

### Item 1 — `make test` (perfrun, `build/val/test.log`)
`scripts/perfrun --label ctxbuild` (shape j16p1): rc 2, wall 1,048 s, `class=RED-REAL`,
three red sections, all dispositioned:
- `test-rxtsource`: STALE PIN, item 7's own corpus move (+6 blocks / +116 lines; PASS +13,
  pcre2-only +103). Re-pinned (commit `197ea7eb2`); re-run 298/0.
- `test-codegen`: REAL CHECK DEFECT in the lane's own P2b work: assertions §1c's two
  compiles (`r1_views`, `a8_lb`) called `"$PCREC"` with no bound, so [K37] went red. Routed
  through `pcrec_run` (same commit); re-run green (35/0, run_group 16/16).
- `test-startset`: STALE PIN, item 7 again: the inserted blocks shifted possessify.rxt's rows
  in the VM-hat manifests and added 4 forced-VM movers (the `(?m)^a+b` and
  `[a\n]+(?m)$\n` blocks, bare and wrapped). `census_s1.py` regenerated on the lane build;
  compared as (options, pattern) multisets, `s2_vm_auto` moved by line only (93 rows) and
  `s2_vm_forced` by line plus exactly those 4; no other corpus row moved. Corpus rows taken,
  bench rows untouched (m7fix's precedent). Commit `c9cf822bc`; `make test-startset` green.
- `docs/dev/artifact_size_log.tsv` was rewritten by the run and NOT committed (kept as
  `build/val/artifact_size_log_ctxbuild.tsv`); the manager's post-merge run owns it.

### Item 2 — emit_sweep vs `5fd84491d` (`build/val/sweep/{default,start}.log`)
- Default streams (`--ref-bin build/base81/build/pcrec`, 56.9 s): self-check clean; c-default
  3 movers, all ONE pattern `(?m)^a|\B` (three corpus rows: utf8/axis11 ×2, utf8/k73); c-vm,
  emit-ir-vm, facts, every emit-ir-auto arm, stderr, composition: 0 movers, every tag floor
  held. dumps: 1 mover, `--list-syntax`'s `^`/`$` descriptions, the lane's DECLARED registry
  rewrite (§1 P2c). rc 1 = those two declared movers.
- `--arms start` (390.6 s): all 52 arms × {c-default, c-vm}. c-vm 0 movers on every arm.
  c-default: exactly 1 mover on every arm (`(?m)^a|\B`, byte and utf8 bases), DIFFER counts
  equal on both sides on every arm and every pinned floor held; the arm FAILs are that one
  identity-required mover.
- CK-4(a): the movers are the light probe's exactly. A text-order prediction (a `(?m)` anchor
  by `mlscan`, a `\b`/`\B` after it) gives 4 distinct corpus patterns (`(?m)^\bfoo\b$`,
  `(?m)^\bx*`, `(?m)^\w+\b$`, `(?m)^a|\B`); only the last moves, the other three are
  byte-identical. So the TEXT rule over-predicts by 3 (the corpus is not short of identity
  evidence); "exactly the DFA artifacts with a `(?m)` node before another A_CTX set" is not
  reproduced by a text rule. Finding for the manager, not a defect.
- CK-4(b): the mover's diff (byte and utf8) is the ENG_ATTEMPT machine's tables
  (`is_accepting_by_class`, `targets_2/3`, `seed_state`) plus one `last_accept_position`
  line moving between state bodies: F-2's state permutation. Nothing else moves (no stamp, no
  `VALID_LB`, no program line). CK-4(c): c-vm/emit-ir-vm 0 movers (VM, possessify listing),
  the mover keeps its engine (route 0).

### Item 3 — mech rows (`build/val/mech/mech.log`, re-run `mech2.log`)
The brief's 39 rows, solo, at `02e252ab8`: unexpected 1, undetected 2, unreached 2,
anomaly 1. Every row is dispositioned below.
- DETECTED as stated: S341 (R1's plant), S693 (abi 81/80), S1151-S1159, S1100, S14, S746,
  S157, S49, S84, S365, S86, S613, S761, S893, S69, S882, S218, S222, S235, S463, S470,
  S608, S617, S78, S81, S82. The measured cells of S1152-S1159 are now their
  SAB_DOC_FIGURE (they read OWED; commit `95b42a3a2`). S1156's cell is
  `possdiff:1fail/294pass`, i.e. item 7's `hold/A4/*` rows are its detector.
- S1160 and S904: UNREACHED, both declared expected.
- S490: UNDETECTED, declared expected (an equivalent mutant).
- **S71 ANOMALY, a stale AFTER the lane's derivation missed.** The plant text still wrote
  `cs->rows = 1u << CTXROW_CTX`, which F-5's rename to `row` turned into a build failure.
  (The row was on the re-run list, but an AFTER that names a renamed field is not an anchor,
  so `[SABANCHOR]` stays green.) Re-aimed to `cs->row = CTXROW_CTX`, intent unchanged.
  Solo: `wordctxid:1fail/2pass,corpus:0fail/71281pass`, DETECTED.
- **S1161 UNEXPECTED UNDETECTED, a real detection gap, now closed.** The plant drops the
  VM's `(?m)^` `pos < n` cell, and it is reachable: `(a\n(?m)^)` under `--engine=vm`
  answers (0,2) on `"a\n"` instead of nomatch. But every corpus `(?m)^` cell is DFA-routed.
  Fix: three capture-wrapped blocks appended to `tests/assertions/multiline.rxt`
  (`(?m)(\n^)`, `(?m)(a\n^)`, `(?m)(^)$`; 36 cells).
  - Oracles: generated by libpcre2 10.46 and checked by `verify_pcre2.py`, 3,349 cells, 0
    disagree. python3 `re` disagrees on 9 cells, all U11b, so the blocks are `# pcre2-only`.
  - Solo: `corpus:3fail/71278pass`, DETECTED.
  - Re-pins in the same commit (`2619ced1b`): rxtsource +3 blocks / +36 lines (own-oracle
    +36), and two `s2_vm_forced` rows for the two VM-hat movers.
- `[SABANCHOR]`: green in every test-codegen run (829 rows resolve). Five rows deleted and
  eleven added, as §5 states.

### Item 4 — CK-5 machine identity (`build/val/ck5.log`)
- Method: every distinct corpus pattern carrying a `(?m)` anchor or a `\b`/`\B`, compiled
  base81 vs P2c at byte and `-e utf8` (default engine, `--features all`). Then classified:
  - `(?m)$` (mlscan): 62 / 62.
  - `\b`-ending with a reverse machine: 82 / 84.
  - a `\b`/`\B` artifact carrying an eol/end view (the has_end population): 41 / 85.
  - the rest: 504 / 473.
- Every artifact in the three named classes is BYTE-IDENTICAL, so tables, `eolvar`/`endvar`
  interning and the views flag are identical. The one differing artifact, in either encoding,
  is `(?m)^a|\B` (class "rest", ENG_ATTEMPT).
- That mover was compared under permutation by `build/v/permcheck.py`. It rebuilds the
  computed-goto machine (accept-by-class rows, targets, seed table, state bodies), renumbers
  states by BFS from s0 then the seeds, and compares. Result: EQUAL under renumbering, with
  the text outside the machine identical, in byte and utf8. Failing direction: one flipped
  accept cell reads unequal.
- Sizing: this mover's state permutation is the only list-order mover the corpus has. A
  table-form mover would need a kvdfa-based compare, and none exists.

### Item 5 — U-B3, `conj.py` (`build/val/conj_*`)
- `census`, `witnesses` and a per-pattern dump (`build/v/conj_pp.py`, 1,998 patterns, `why`
  plus k/absB/absA) were run with the base compiler and with P2c. All three outputs are
  byte-identical. Sections A/B/E also equal the committed `conj.txt`.
- The two witness verdicts ctxspan21 left OWED now read `cover k=2 absB=True absA=True`:
  `a(?=b)[a-z]|ac` and `[ab](?<=a)c|bc`. Their S1150 slice half is still OWED at Z2;
  conj.py does not model it.
- `rarm` (verdicts under `-fno-rev-end`): base and P2c byte-identical, and equal to
  `conj.txt` §C.

### Item 6 — `make test-axes` and `run_mline_diff.sh` (`build/val/axes*.log`, `mline_diff.log`)
- First attempt, the UNBATCHED default shape under a 7,200 s bound: KILLED (rc 124). That
  was this lane's error, not a hang. testing.md records the full sweep only in the battery
  shape. Before the kill, 50 jobs completed, and every one was answer-identical (mismatches
  0, lost-other 0, giveup1-unallowed 0): the 49 bit axes, `--harness=no-compound` and
  `--engine=vm` (its 12 GIVEUP1 cells all allowance-named). Kept as `axes_unbatched.log`.
- Re-run in the recorded shape (`AXES_FULL=1 HARNESS_BATCH=64`, bound 10,800 s): **rc 0,
  wall 10,381 s, 111 axis jobs OK, 0 AXIS FAIL**, form census green. That is slower than
  ubuntubudu's 6,012 s at abi 37 (the sweep has grown), and is now recorded in
  docs/testing.md beside the older figures.
- `run_mline_diff.sh`: rc 0, 4/0. 22 patterns, 115 subjects, 5,038 DFA + 5,038 VM cells,
  0 disagreements.

### Closing checks
- recursion-identity: FILEPIN re-pinned `9f7cb74e3` → `95b42a3a2`, the validation tip.
  Its src is identical to P2c's self-pin and it contains the main merge. The manager re-pins
  to the merge commit. Gate: 18/0, rc 0, 1,428 s. (B) is whole-file identical on 3,878
  call-free patterns.
- `make strict` clean, `run_plan_lint.sh` 2/0, `make test-spec-history` 0 failed.

### For the manager
- **Real fixes, all check-side: no `src/` change.**
  - K37 bounds on assertions §1c (the lane's own P2b section).
  - S1161's detection gap closed by corpus cells.
  - S71's stale AFTER.
- **Re-pins, each traced to its corpus move.**
  - rxtsource ×2: item 7's six blocks, S1161's three.
  - The startset VM-hat manifests: line shifts plus 4 + 2 forced movers.
  - FILEPIN.
- **To rule.**
  - CK-4(a) as worded ("exactly the artifacts with a `(?m)` node before another A_CTX set")
    is not reproduced by a text rule. The rule predicts 4, and 1 moves. Leaning: restate it
    as "a subset of" plus the measured list.
  - `artifact_size_log.tsv` from the full run is not committed.
  - The D62 addendum (§7) is unchanged.
