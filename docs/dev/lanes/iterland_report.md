# iterland — the find-all iterator stack, prepared for landing (2026-10-22, sonnet)

Branch `lane/iterland` (worktree `worktrees/iterland`) from main `02f357b39` (abi 83).
NOT merged to main: RX_FOREACH's fate is unruled. STATE: merges and the D94
ritual done and committed; the light sections and the pin re-measure are OWED
(the box was held by the kit's job 600 for the whole lane).

## Merge record

1. `git merge lane/itertri` (8b56b7a7f; carries i1build, i2build, iteropt, iteropt2, the triage re-pins): 21 conflicted files, merge commit `55c757b50`.
   - Makefile: both section lists unioned (main's `test-claudemd-size test-kitproof test-casemap` plus the lane's `test-findall`).
   - `tests/ci/shards.tsv`, `decisions.md`: both sides kept (the lane's i2build Gloss line moved to follow the "Noted for I2" paragraph it glosses).
   - `plan.md`: [M4-SUBST] row from main kept, [FINDALL-NEXT] row from the lane with a one-line landing status (<= 300 chars, plan_lint clean).
   - Ten `CLAUDE.md` files (docs/design, docs/dev/lanes, docs/dev/reviews, src/{facts,gen,ir}, tests, tests/{assertions,codegen,harness}): main de-bulked them, the lane had appended to the pre-de-bulk text. Resolved to main's version; the lane's added lines carried VERBATIM into each directory's `NOTES.md` (new NOTES.md in 8 directories) and one pointer line added to each CLAUDE.md. All within the size limits (`check_claudemd_size` green at commit).
   - abi: see below.
   - `tests/rxtsource/run_rxtsource_tests.sh` census pins and `manifest_s2_vm_forced.tsv`: see "Re-pins owed".
2. `git merge lane/iterdoc` (231364a7a), alone: one conflict (`docs/dev/lanes/CLAUDE.md`, same de-bulk shape), merge commit `934f8bed1`. match_api.md auto-merged.

## ABI: ONE event, 83 -> 84

Main's 83 is lane corefix (K128/K129, renumbered 87 -> 83 at its landing); the
branches' own 83 (I1) and 84 (I2) fold into a single 83 -> 84 event.
`docs/dev/history/abi_changelog.md`: one entry "`rx_info.abi` is `84`" with the I1 part, the I4 part (carrying iteropt and iteropt2) as its sub-items; corefix's entry kept below as "was `83`".

Readers of the number, found by grep (`PCREC_ARTIFACT_ABI|PCREC_RX_ABI_H|ABI_EXPECT|FILEPIN|abi.{0,60}8[34]`), with hit counts after the merge:

| reader | hits | state |
|---|---|---|
| `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI` | 1 | 84 |
| `docs/spec/match_api.md` (guard block, `.abi` row, §6 sentence, mirrored sites) | 5 lines with 84, 0 with 83 | 84 |
| `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT` | 1 | 84 |
| `tests/mech/sabotages/S693_abi_not_bumped.sh` BEFORE/AFTER | 2 (+ comment, corefix and iterland RE-AIMED lines) | 84 / 83 |
| `docs/dev/history/abi_changelog.md` | 1 entry | folded |
| `tests/codegen/run_recursion_identity.sh` `FILEPIN` | 1 | re-pinned to `934f8bed1` (the merge; src/lib/cli/memfn identical to the stack's last src commit) |
| `tests/codegen/run_cpset_structure.sh`, `tests/resource/run_resource_tests.sh` | comments naming 83/84 | byte pins inside them are the owed re-measure |

Corefix's own commit (`52f209cb5`) listed five readers (emit_dfa.c, ABI_EXPECT, S693, match_api.md, abi_changelog); all five are on 84, plus the FILEPIN.

The kit's `lane/memfn-s3` also wants 84 provisionally. Whichever lands first
keeps 84; the other renumbers to 85 (the same five readers + FILEPIN, and its
abi_changelog entry).

## Re-pins owed (nothing copied; none yet re-measured)

Main gained, since the branch point, the B4 compound stamp, the K59 rung and a
start-sweep floor change; the lane's pins were measured before them. Each is
re-measured with its own check's `-o` basename, from the red line of the first
run of that check on this tree:

- `tests/rxtsource/run_rxtsource_tests.sh` CENSUS_*/RUNSH_*/C3_*: conflicts resolved to MAIN's values (the lane's `tests/findall/global.rxt` is a new corpus file, so its blocks/lines are not in them). Re-measure from `make test-rxtsource`.
- `tests/startset/manifests/manifest_s2_vm_forced.tsv`: both sides' appended rows unioned (corefix's 34 `empty_iteration.rxt` rows + the lane's 14). Row order and the manifest's own count are re-checked by `make test-startset` (in `make test`, job 602).
- `tests/codegen/run_cpset_structure.sh` and `tests/resource/run_resource_tests.sh` byte pins; the start-sweep floors; the compound B4 stamp pins: owed to the first red of `test-codegen`, `test-resource`, `test-compound`.

## Light verdicts: OWED

Chain `build/il/light.sh` (detached, each stage under `scripts/boxlock run`,
`gnutimeout 3000`): strict, test-findall, test-codegen, test-registry,
test-rxtsource, test-spec-history, test-plan-lint, test-compound.
Log `worktrees/iterland/build/il/light.log`; per-stage logs `build/il/<stage>.log`.
Completion line: `== LIGHT DONE`. It was waiting for the box lock (job 600) when this report was written.
Read the verdict with `scripts/verdict build/il/<stage>.log` (make's `*** [...test-X] Error` lines), not the stage rc alone.
Measured here: `make -j16` builds the merged tree clean; the staged pre-commit checks (plan_lint 194 rows 0 violations, claudemd size) passed on every commit.

## Queued, OWED

- `602-iterland-test`: full `make test` through `scripts/perfrun --label iterland`; ready only after `== LIGHT DONE`; expect `sections=77` (`sections ran: 77/77`, counted from `TEST_SECTIONS` of this tree; main's is 76 plus `test-findall`); cap 3600.
- `603-iterland-mech`: mech S1297-S1321 plus S02 S05 S693 (28 rows, the field validation resolved all ids); ready `after iterland-test`; expect `rows=28 last=^== mech run COMPLETE: `. S1300, S1303, S1309-S1313, S1321 are in the range; S02/S05 were re-aimed by i1tri, S693 by this merge. REACH_ONLY is not run (no new strategy site).
- Status: `scripts/boxqueue status`.

## Next agent (resume from here)

1. Wait for `== LIGHT DONE` (or run the failing stage solo). For each red stage: read the red line, re-measure that pin with the check's own `-o` basename, commit named paths only.
2. Re-run the touched section; if any src moved (it should not), FILEPIN moves to that last src commit.
3. Jobs 602 and 603 follow on their own; read both with `scripts/verdict`.
4. Merge to main only on Frank's RX_FOREACH ruling.

## Triage (iterfix)

Job 602 (`make test`, perfrun `section-errors=1 class=RED-REAL`): the ONLY red section was `test-rxtsource`
(make line `*** [Makefile:593: test-rxtsource] Error 1`); every other section green, so startset
(manifest_s2_vm_forced union), cpset_structure and resource byte pins and the compound stamps were NOT red.
The light chain agreed (only test-rxtsource, rc=2).

| section | class | cause | fix commit | solo verdict |
|---|---|---|---|---|
| test-rxtsource | (a) stale pin | merge took main's census/RUNSH/C3 values; the lane's new `tests/findall/global.rxt` was not in them. Measured from the check's own output: +1 file, +62 blocks, +1404 lines (CENSUS 293/6038/73976, RUNSH 269/6038/73976); C3 PASS +1188 (21932), SKIP +216 (51958), pcre2-only +216 (19373), verifiable +1188 (24164). The W23-S7 corpus control, the case-row derivation and the C3 reconciliation (21932+51958-3+89=73976) all follow from these pins. | the commit "iterland: re-pin rxtsource census/RUNSH/C3 for tests/findall/global.rxt" on lane/iterland | OWED: `build/il/fix-rxtsource.log` (detached, waiting on the box lock behind queue job 604-kit-s3-heavy); read with `scripts/verdict`. |

Not re-pinned (not red, nothing measured): C3_FILES, the five golden findings files' HARNESS FAILURE lines (the known unparseable-head set, printed by the W23-S7 control as before).

## Macro removal (nomacro)

Lane nomacro (sonnet), 2026-10-23, Frank's ruling: `RX_FOREACH` dropped, `_next` / `_next_n` and `rx_info.next` / `rx_info.next_n` stay (D175). abi stays 84 (the event is unlanded; its changelog entry is amended).

**Sites changed.** Emission: `src/gen/emit_iter.c` (the whole RX_FOREACH block: `RX_FOREACH_PAIRS`, `rx_foreach`, `rx_foreach_begin`, `rx_foreach_pull`, the macro; `rx_nextnfn` stays, it types `rx_info.next_n`). Spec: `docs/spec/match_api.md` (contents entry, §1¶5/¶6, the §2 listing, §3.1.3, §3.8.2 rewritten as "Looping over any artifact's record" with a loop for `info->next` and one for `info->next_n`, §4 table and ¶9a, §6¶14c; anchors `s3-8-2` and `s3-8-2-p1..p4` kept, the old p3-p5 content gone and no citer left). Tests: `tests/findall/iter_drv.c` (F, Fstop, Fcount, Fabi cells replaced by `g1_drain` / `gn_drain` plain loops over the record, cells G1 and GN), `run_iter_diff.sh` (REACH_NEED), `run_findall_tests.sh` (ASan build loses `-DRX_FOREACH_PAIRS=8`), `cells.tsv` comment, `tests/encseam/findall_driver.c` (a plain `fa_info.next_n` loop), comments in tests/assertions, tests/codegen, tests/resource, CLAUDE.md/NOTES.md of src/gen, tests/findall, tests/encseam. `run_facts_checks.sh`: `FOREACH` removed from MACHINERY. Docs: decisions.md D175; abi_changelog.md 84 entry amended; plan.md [FINDALL-NEXT] row; `findall_iter_i2.md` gets a superseded-in-part banner; the twin harness `docs/design/findall_iter/twin/` keeps its F/Fb arms as the evidence behind D175 (they need a pre-D175 compiler; noted in its CLAUDE.md), `tdrv.c`'s stride probe now `-DNN_STRIDE_ONE` instead of `#ifdef RX_FOREACH`.

**Rows retired** (git-deleted, the S293/S1421 precedent): S1315 (doubling), S1316 (brk), S1317 (kmax), S1318 (abi unchecked), and S1320 (refills early; also macro-only, not named in the brief). S1314 (`rx_info.next_n` NULL) stays, re-aimed: its witness is the info arm plus GN, the plain `next_n` loop, reach token `g1`. VALIDATE_ONLY on S1314: valid.

**Pins moved** (each from the check's own output):
- reach tokens (`run_iter_diff.sh`, `run_findall_tests.sh`): `f1 f2 fstopend fcount2 fcount63 fabi kmaxcap frefused` -> `g1 g2 gn5`; test-findall prints `reach n3m4=72 split=118 g2=144` (ASan run), green.
- `tests/codegen/manifests/m5_stage1_stamps.tsv` (test-cpset-structure check [3]): all twelve EMITTED_BYTES rows -2,686 (uniform; no other row moved), now 29 checks pass.
- `tests/codegen/run_recursion_identity.sh` FILEPIN (the (B) pin): 934f8bed1 -> 24d2888f5 (this lane's src commit; the manager re-pins to the merge).
- abi number readers: none move (84 stays); test-codegen 331+ checks green, abi 84 sentences intact.
- `tests/resource` byte pin: unmoved (the macro was in the .h, the pin counts the .c); test-resource 42 green.

**Commits:** 24d2888f5 (removal, tests, spec, decisions), 351f30ff7 (manifest re-record, FILEPIN).

**Validation run by this lane:** make -j16, make strict, test-findall, test-encseam, test-codegen, test-registry, test-plan-lint, test-spec-history, test-claudemd-size, test-cpset-structure, test-entry-shape-identity, test-resource: green. Queued, not run: iterland-test, iterland-mech (see the handback).

## Review fixes (iterfix2)

Lane iterfix2 (opus), 2026-10-23: the engine-side FIX-NOW findings of review
`docs/dev/reviews/2026-10-23-r2-iter-code.md`. abi stays 84 (changelog entry amended).
Commits on lane/iterland: f298d084e (WIP: retry table, one anchored attempt, unsplit entries), bb8faa60b,
1eaf544a8, a298c58e8, 93c5e33c6, 449f00a98, c215d8a8e, cdc976bd9, 3bce46997, 9a8f07602, 3f3761439, 88ef44996, ba7da2ab6, f38dd2ac4, 4f39644d8, 7a9c7e6d0 (pins).

**Item 0, triage of 602 (green) and test-recursion-identity.** 602's verdict: GREEN (no `*** [..test-` line).
test-recursion-identity on the 602 build: (B) whole-file vs 24d2888f5, 0 differing in every mode; (A) region vs
ac4917d: 78 (default), 127 (vm), 78 (noprefilter), 54 (nocaptures) differing, and the bref-rename bucket 366 vs census
411. NOT this branch: all 127 differing patterns produce a region byte-identical to BASE/main 02f357b39's. Main's (A)
gate has been stale since the corefix merge bf33d2dab (K128's empty-repeat guard: 66 of the 127 regions carry
RX_SLOT_EMPTY_GUARD; 36 of 127 are backref patterns, the bref-bucket shortfall). Main-side; recorded, not re-pinned
here (the (A) reference is main's to move).

| id | what changed | commit | evidence |
|---|---|---|---|
| CONTRACT-1, SLOT-2, HOUSE-3 (one root) | The retry is no longer a private copy of the anchored body. DFA: `pcrec_emit_dfa_retry` is ONE anchored attempt of `Job.nedfa` through `dfa_dir_anchored`'s own scan (`emit_anchored_scan_head`/`emit_anchored_scan`), and `^`/`\A` are false at a retry position past 0 (`dfa_start_from_context`, read by `seed_applies` and `dfa_seed_has_dead`). VM: the retry runs `<p>__match_notempty`, a textual copy of the matcher with the guard at its accept (`vm_emit_guarded_matcher`), through the same attempt and report emitters as `_match_caps_run` (`vm_emit_anchored_attempt`, `vm_emit_attempt_report`). | f298d084e, 1eaf544a8 | `tests/findall/retry_anchor.rxt` (` *\|^x+`, `\|^x`, `\|(?:^a\|b)`, `\|\Ax`, `(?m)\|^x`; global counts from libpcre2 10.46, python agrees): 10/10 pass at head, 8/10 red on the pre-fix compiler. Every repro is OK against libpcre2 on auto, dfa and vm (scratch differential `chk.sh`). |
| CONTRACT-2 | The bind check aligns `lo` in place (guard rendered with posvar `(*pos)`, no local), so a `-futf-check` refusal leaves `lo` where `valid_upto` was asked. | bb8faa60b, fix 3bce46997 | The c2 probe: lo after refusal equals the asked position. bb8faa60b refused EVERY `-futf-check` artifact (a twin mark inside the iterator's scaffold bracket); I found that at E0 and fixed it in 3bce46997 (`pcrec_enc_twin_mark` writes a plain byte inside an open bracket). A 48-compile matrix (byte/utf8 x 4 flag sets x auto/vm/dfa x 2 patterns) then compiled warning-clean. |
| EMIT-1 | The guard lives on the iterator path only (the VM's `__match_notempty` copy), and nothing splits unless the search entry's caller-position prologue writes anything (`pcrec_startpos_prologue_on`: a UTF check, or an encoding start guard that is on) and an iterator is requested. Elsewhere `_search`/`_search_run` keep BASE's text and the step calls them. | f298d084e | 21 patterns from emit.md, BASE 02f357b39 vs head, `perf stat -e instructions:u`, `taskset -c 7`, one pattern at a time: every pre-existing entry (`_search`, `_search_in`, `_match`, `_match_in`, `_match_caps`, `_match_caps_in`, `_match_anchored`) is asm-identical except alignment nops, and the constant +22..26 instructions per run is process startup. Re-checked at the final head (asm only): identical to the measured head on all 21. Deviations: `([a-z]+)?=?(\d+)?` (VM): the `_match_caps` TEXT is identical but gcc now inlines `match_caps_run` because the TU grew, so C is -600,026/36.0M (faster). `\w+ -e utf8 -futf-check` (split, the prologue is real): -0.9% L, -0.9% M/C (faster; the `__valid_upto` twin). `(\w)+ -e utf8` VM (split): L/M/C within +22 (startup only). |
| EMIT-6 / T1 | `<p>__one_local` calls `<prefix>_next` (one `noinline` 52-62 byte function) instead of holding a third step. | f298d084e | `.text`, gcc -O2, BASE -> branch 588714855 -> head: `\w+` 904 -> 2,536 -> 1,672; `a*` 520 -> 2,600 -> 1,784; `(a+)(b+)` VM 2,952 -> 8,392 -> 6,824; `(a*)` VM 1,352 -> 5,096 -> 4,104; `ab\Kc?` VM 1,528 -> 6,520 -> 5,176. `__one_local` is 62 B (`a*`) / 52 B (`(a+)(b+)`); it was 513 / 1,578. What remains is `_next` and `_next_n` each inlining the step and search (D171's two controllers: `a*` 275 + 578 + `__retry` 310; `(a+)(b+)` 1,746 + 2,056). |
| T1 (EMITTED_BYTES, priced) | The m5_stage1 manifest's 12 rows, BASE 02f357b39 -> branch 588714855 -> head: `a` 21,349 -> 29,295 -> 28,498; `abc` 22,180 -> 30,126 -> 29,329; `a(b\|c)+d` 32,844 -> 41,546 -> 40,667; `(a)(b)(c)` 29,825 -> 38,527 -> 37,648; `[a-z]+@[a-z]+` 28,080 -> 36,026 -> 35,229; `^foo$` 19,289 -> 27,223 -> 26,438; `\bword\b` 25,145 -> 33,091 -> 32,294; `(?i)HeLLo` 25,545 -> 33,491 -> 32,694; `cat\|dog\|cow\|calf\|camel` 28,833 -> 36,779 -> 35,982; `(\w+)\s+\1` 29,118 -> 37,820 -> 36,941; `(?<=foo)bar` 30,517 -> 39,219 -> 38,340; `(a(?1)?b)` 33,059 -> 42,248 -> 41,448. | 7a9c7e6d0 | The trade: +7,149 (DFA) .. +8,389 (VM) bytes of SCAFFOLD on every artifact (+21% .. +37% of these small artifacts; under 1% of the 766 KB resource rescue). It buys `_next`/`_next_n` on every artifact with no build flag (D171's ruling), and it is excluded from every length decision. It is the shared block's `rx_iter` and its setters, the two controllers, the step, the bind and, on nullable patterns, the retry. This lane removed 796-878 of it. The next cut would be emitting the iterator only on request: that is a contract question (an interface flag; [IFACE-PUSH]), not a fix. |
| EMIT-7 | The VM split's range test is in the `_run` prologue only, in front of the guard (`vm_emit_search_run_prologue`); `<p>__find` has none. Its every caller tests first (the step tests `lo > n`). Unsplit artifacts keep BASE's one test. | f298d084e | Text: one `search_from > subject_length` per path. |
| EMIT-8 | Parts never request an iterator, so `pcrec_entry_emitted(FIND)` is false and a part is unsplit. | f298d084e | `^\s+\|\s+$`: `rx__f_search`/`rx__q_search` are byte-identical to BASE's, with no `__find` in the file. The shell's one changed line is the F-1 twin call `rx__next_pos`, which predates this lane. |
| SLOT-3 | THE RETRY TABLE (`emit_iter.c`): first-match rows `none` / `notempty-machine` / `guarded-matcher`. Each row carries the token it stamps and what the build needs (`PCREC_ITER_NEEDS_NEDFA`/`_GUARDED`); compile.c builds `Job.nedfa` only on NEEDS_NEDFA, the stamp prints the winner's token, and `retry_ok` is gone. | f298d084e | The stamp check (`run_iter_diff.sh`, renamed in 3f3761439) holds the token to the text. |
| SLOT-1, HOUSE-2 | One tier ladder: the iterator's own-storage step and the caller bind are `forward`'s emitters (`pcrec_emit_own_binding`, `pcrec_emit_caller_bind`); `vm_own_binding` is the one selection for entries and iterator. | a298c58e8, ba7da2ab6 (indent) | The entries' text is unchanged (`fwd_in`'s bind is byte-identical to BASE's); all three VM binding forms (own, tiered, EMPTY via `--vm-entry-shape=2/3`) agree with libpcre2. |
| SLOT-5 | Rows state the true call graph. FIND is an EF_BODY row on both engines (`pr_vm_find`). NEXT's parts are FIND or the whole search, plus RETRY and NEXT_POS. `next_n` is its own entry (PCREC_ENTRY_NEXT_N, own linkage, `rx_info.next_n` and its decl gated on it) whose parts include NEXT (the NULL-caps path). The retry is a row (PCREC_ENTRY_RETRY, internal). One `__find` per artifact. | 449f00a98, ba7da2ab6 | E0 (`check_entry_ranks.py`) 10 witness rows, 0 failures; re-seed population 4,797, 0 failures. The VM `__find` folds as owned-inline, so part layout counts the prefilter's callers through it (the `ab-utf8` witness, red until then). |
| HOUSE-7, SLOT-6, HOUSE-8 | The unread mode column became a FORM column (EF_ENTRY / EF_BODY); the four FIND special cases read `pcrec_entry_is_body`. The prologue predicate is a fact (`pcrec_startpos_prologue_on`), not a render-and-measure. | 93c5e33c6 | The predicate was validated over byte/utf8 x 7 flag sets x engines against the emitted prologue. |
| Names (D174, SLOT-10/HOUSE-12) | `<PREFIX>_ITER_RETRY` is `"none"` / `"retry"` / `"retry-budgeted"` (was dfa-root / vm-guard). Spec §6.3.13 has a table of what the caller sees (¶2: the value is the table's winner) and §6.3.4¶9 its reader; the abi 84 changelog entry is amended; src/gen/NOTES.md. | cdc976bd9 | Readers moved: mover_census.py, tests/findall/CLAUDE.md, run_iter_diff.sh (3f3761439, as iterchk asked), S1297/S1298/S1305/S1307/S1308 re-anchored. I probed each plant on a scratch build: S1297/S1307/S1308 DIFF against libpcre2; S1298 DIFFs on `\|a` / `x*\|ab`; S1305 moves the stamp only (its detector is run_iter_diff's stamp check). |
| HOUSE-1 | The iterator's emitted text carries no comments (14 trailing comments dropped); the reasons moved to the C-side headers. | c215d8a8e | `-fno-comments` artifacts (`a*` on DFA, VM, utf8 `-futf-check`): no comment of the iterator's own survives. One remains: `<p>__bind_checks` reuses the startpos guard's text, whose `[K50]` comment BASE already emits unbracketed in `_search` under `-fno-comments` (2 copies at BASE, 3 at head). That comes before this lane: noted, not fixed. |
| HOUSE-4, SLOT-9 | `residual_sites` lost its dead out-of-line half; `pcrec_enc_emit_defs` lost `sites`/`nsites`; the static became `enc_emit_inline_defs` (no `inline_half`/`drop`/`stat`); enc.h comments match. | c215d8a8e | Builds clean; strict green. |
| HOUSE-5 | `rw_alt` and `rw_node`'s A_CAT arm use PCREC_SPINE_EACH; the A_WCLASS/A_CLASS arms stay apart (merging them trips run_cpset_structure.sh [5b]; restored in 4f39644d8). | c215d8a8e, 4f39644d8 | `reports_empty`: 32 spot patterns, both engines, identical to the pre-change compiler; the T3 census below shows no ITER_RETRY move from it. |
| HOUSE-6, SLOT-8 | emit_iter.c header rewritten (two controllers, the table, scaffold); lane names out of src comments (emit_iter.c, emit_dfa.c). | c215d8a8e | - |
| HOUSE-10 | `Mach` designated initializer; `d_notempty` renamed. | c215d8a8e | - |
| HOUSE-11 | `pcrec_enc_twin_name(sb, prefix, name)` is the one place the twin mark sits between prefix and name (both call sites). | c215d8a8e | Emitted text unchanged. |
| T3, SLOT-4 (measurement) | Census of every corpus pattern (4,797), BASE vs head, default route, every string selection stamp but the iterator's and the kit's knowledge stamps. | - | 0 engine or finish-form movers (ENGINE, ENGINE_SEL, DFA_MATCH, DFA_TABLE, ... all identical). The 48 "moved" rows are only compound PARTS gaining `_F_/_Q_ITER_RETRY "none"` (a new stamp, no move). Lowering the auto budget to find the margin is not possible from the CLI (`--max-auto-dfa-elems` is raise-only), so the margin witness stays `run_n1_budget.sh`'s bisect (review T3). Nothing moved, so I did not stop. |

**Pins moved (each from its check's own output).** `tests/findall/one_body/` x3 (ba7da2ab6: no comments; the VM bind is `forward`'s text); rxtsource CENSUS/RUNSH 294/6043/73986 (RUNSH files 270), C3 PASS 21942, VERIFIABLE 24174 (f38dd2ac4, +retry_anchor.rxt); resource `a{5,25000}` rescue 766980 -> 766184; m5_stage1 EMITTED_BYTES x12; recursion-identity (B) FILEPIN 24d2888f5 -> 4f39644d8 (7a9c7e6d0); E0 fixture: 5 rows `find` -> `search` (9a8f07602); partlayout: `held-compound` restored to BASE's row (comp_a=P2, comp_b=P3, `compound=inline/held`; this recovers review T4's lost coverage), writers rows for `__step_own_deep` and `__match_notempty`; 13 sabotage anchors re-derived (88ef44996, ba7da2ab6), and each plant builds. abi stays 84; no abi-number reader moved.

**Light verdicts (head 7a9c7e6d0, box lock held).** Green: make -j16, make strict, test-codegen, test-registry, test-findall, test-encseam, test-resource, test-spec-history, test-plan-lint, test-compound, test-partlayout, test-island, test-rxtsource, test-cpset-structure, test-entry-shape-identity, test-claudemd-size. test-recursion-identity: (B) green; (A) red with the SAME 78/127/78/54 regions and bref 366 vs 411 as 602's build, which is main's stale ac4917d pin (item 0), not this branch.

**Deviations / for the manager.** (1) The EMIT-1 speed deviations listed above: all faster or equal. (2) Emitting the iterator only on request would cut T1 further. That is a contract question, not a fix, so it was not done. (3) The `[K50]` guard comment survives `-fno-comments` (this predates the lane; BASE has it too). (4) S1305 is detected only by run_iter_diff's stamp check; its rename is on this branch (3f3761439) and merges cleanly with iterchk's hunks. (5) A stray `/tmp/tmp.djQK5wYzqA` from an earlier step of this lane sits outside the mandate; please remove it or tell me to.

## iterjoin (2026-10-23): lane/iterchk merged into iterland

- Merge cc5859684 (`--no-ff`). One conflict, `tests/partlayout/fixtures.tsv`: iterfix2 had restored `held-compound` (byte compounds no longer split, T4), which makes iterchk's `compound-inline`/`compound-shared` pair and its header note moot; iterfix2's side kept whole, iterchk's `compound-shared` fixture dropped (test-partlayout 49/0, was 50 on iterchk). `make strict` clean.
- `tests/findall/global.rxt` regenerated with the CHK-8 generator (`gen_global.py`, 67 blocks, +5 blocks, +19 lines), counts from libpcre2's `pcre2_substitute`.
- Re-pins, each from the check's own output: rxtsource CENSUS/RUNSH blocks 6043 -> 6048, lines 73986 -> 74005; C3 PASS 21942 -> 21957, SKIP 51958 -> 51962, SKIP_PCRE2ONLY 19373 -> 19377, VERIFIABLE 24174 -> 24189 (test-rxtsource 298/0); `manifest_s2_vm_forced.tsv` four global.rxt rows renumbered (736/758/900/1271 -> 738/760/902/1273, same patterns), +3 rows (1610, 1619, 1628) (test-startset 22/0).
- Light verdicts: test-rxtsource, test-findall, test-partlayout, test-codegen, test-registry, test-spec-history (173/0 and 11/0), test-plan-lint, test-startset, test-start-landing, test-ci-shards all green after the re-pins; no engine regression seen.
- Queued: `602-iterland-test` (retry of the killed run, `expect sections=77`), then `603-iterland-mech` (23 rows: S1297-S1314, S1319, S1321, S02, S05, S693; the retired macro rows S1315-S1318 and S1320 are out; dry-run needed `BOXQUEUE_DRY_BOUND=120` on the loaded box).

## iterpin (2026-10-23): re-aim of the checks iterfix2 moved

Cause: iterfix2 (88ef44996 / 9a8f07602 / ba7da2ab6) splits the search only
where a UTF-check / start-guard prologue exists. A byte artifact keeps the body
in `rx_search` (DFA) or `rx_search_run` (VM) with no `rx__find`; a utf8 one has
the body in `rx__find` and a thin wrapper under the old name. The VM anchored
program is also written a second time as the scaffold copy
`<prefix>__match_notempty`. Every check was RE-AIMED, none weakened; a check
that finds nothing to read now FAILS.

| check | old assertion | new site | sabotage proof |
|---|---|---|---|
| run_anchored_match.sh §2 positive half | search carries a prefilter, read from `rx__find` | `rx__find`, else the `rx_search` definition; neither found = RED ("neither rx__find nor an rx_search body") | shim removing every prefilter spelling from the artifact: all 4 §2 rows RED ("NO prefilter in its search body"); shim planting `memchr(subject + scan_position` in `rx_match`: all 4 §2 rows RED |
| run_presence.sh [pr8] | verdict precedes first attempt, in `rx__find` | `search_body_start`: first of rx__find / rx_search_run / rx_search DEFINITION (attribute-prefixed heads included) that carries the attempt marker; none = RED "no search body"; `plant` uses the same finder | rename the three candidate names in the file: 4 [pr8] rows RED "no search body"; the existing [pr8-negative] reorder plants still report (24/24 green) |
| run_encoding_checks.sh DD12a(i) | byte vs utf8 text equal outside named encoding-owned regions | new counted region `search_split`: utf8's wrapper `rx_search`/`rx_search_run` (K50 guard shell around `return rx__find(`) excised, the bounds line `if (search_from > subject_length) return 0;` (moved into the wrapper) excised, body head and iterator call name canonicalised to `rx__BODY`. Hot loop beneath compared text for text. 625 hits in the slice; added to the vacuity list (zero = RED) | shim planting `if (subject_length == 12345) return 0;` in every utf8 `rx__find` body: RED again, 231 of 237 strict pairs differ, FINDING lines |
| run_simd_guarded.sh arithmetic | stamp = blocks x block size, blocks counted over the whole text | `strip_blocks` also returns blocks inside the scaffold copy `__match_notempty`; the stamp counts SIMD bytes outside it (the copy is scaffold bytes, `scaf_guarded`, read by no decision), so arithmetic uses `nblk - ncopy`; floor `scaffold-copy` 200 (328 measured) | witness shim bumping the stamp by one nibble: arithmetic RED in every arm; witness shim renaming the copy function: RED (NEUTRALITY trips first, copy blocks unaccounted) |

UNKNOWN verdicts:
- Encoding: the byte/utf8 difference is ONLY the prologue split (wrapper shell,
  moved bounds line, symbol names, and the already-excised K49 advance / guards).
  The hot loop is identical, so the comparison was re-aimed rather than stopped.
- memfn-guarded: stamp 2 blocks vs 3 blocks in the text on the ladder named
  witness and 328 corpus cells: the third is the scaffold copy's inner block
  (`vm_emit_guarded_matcher`, iterfix2 f298d084e), counted as scaffold bytes by
  design. Neutrality (artifact equal with blocks stripped) held throughout.
test-vm / test-memfn-finder carry the run_presence.sh fix. test-vm also runs
tests/codegen/run_ir_listing.sh (the triage's "test-anchored-match" ir-listing
item; run_anchored_match / anchored_diff / anchored_dead_entry were all green):

| run_ir_listing.sh PROGRAM + CHOICE POINTS + resume-point cap | labels and `RX_PUSH` sites read from the whole artifact | the artifact is split into the program text and the scaffold copy `__match_notempty` (a separate C function, so each label legitimately appears once per function); the program is read from the former; the copy is held to its own shape (labels non-empty, no duplicate within it, subset of the program's) | shim duplicating a label inside the program: RED "defines a label more than once" on every VM row; shim hiding the copy's name so the split finds nothing: RED on (a*)*, (|a)+, ((a)(b))* (the original failure) |

Light run (boxlock, detached): test-vm test-anchored-match test-memfn-finder
test-encoding-checks test-memfn-guarded green (no `*** [test-` line, rc 0);
`make strict` clean. Sabotage shims lived in the scratchpad only.
