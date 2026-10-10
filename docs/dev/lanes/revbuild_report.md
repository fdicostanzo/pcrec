# revbuild — [OPT-REVEND] L1 + L2 with stage 2 folded in

Lane revbuild, 2026-10-10, opus. Branch `lane/revbuild` off main `c85a1aac`
(L0 merged), with main `64e8aa0e` (sstri) merged in. Design:
`docs/design/locate_finish.md` rev 2.1 §4.3, §5 L1-L3; D156 addendum 1 (Q2
RULED: stage 2 is built with stage 1); `docs/design/revend.md` §6 (form C),
§9. The kit's R-12 (VMLAZY, abi 72) merged to main (`a15fb77b`) while the
lane was finishing; it is merged into this branch and this lane takes
**abi 73** (§5).

**Status.** Built, committed, light gates green (§7). The landing chain (make
strict, make test, test-axes, test-revend-twin, the mech rows) runs detached
as the lane's last act; its verdicts are in §7.2 once its trailer is written.

## 1. What was built, per stage

| commit | stage | what |
|---|---|---|
| `fddd803a` | L1 | revend.md S0: the `end_pin` fact split out of `end_window` (`src/facts/endwin.c`, `facts.def` row `end_pin`, `end_window` depends on it; `--emit-facts` renders `z`/`eol`/`none`). S1: `emit_reverse_block(c, rev, label, dead_skip)`, the reverse walk parameterized by its label and the dead-seed statement. No mover. |
| `4863fc96` | L2.1 | THE GENERATED STAMP RULE: `cand_absent[]` + `cand_stamp_absent(cx, slot, route)`. A slot's stamp reads its selection where the selected path asks the slot (an entry slot on any route), else its ABSENCE value; applied to `DFA_START`/`search_form`, `END_WINDOW`, `REQ_HANDOFF`, `DFA_PREFILTER`(+`_OFFSETS`), `VM_START_SCAN`. RECOVER's absence is `"attempt-start"` (D-2). |
| `a2d3f861` | L2.2 | LOCATE row `rev-end` (A2) between `empty` and `composite`, deny `PCREC_NO_REV_END` (bit 52), CR_DFA, predicate = the `end_pin` fact (the stage-1 conjunct is NOT there: Q2). Its walk `emit_rev_end`: seeds n and n-1 (`$`/`\Z`), the dead-seed skip, the smallest start, and on a TIE (two seeds and `nl_last` on the built reverse machine) a FINISH ask for ENDSET: `verify-at` runs `<p>_match` from the start (T2), `search-from` relocates to the composite (T3). LOCATE rows gain `whole`/`recover`/`fin`; FINISH rows `take[route]`; new FINISH rows `nomatch` (FIN1) and `report`; the RECOVER hands; the PRESENCE deference (`REQ_WHY "dominated"`); the empty engine's `<p>_match` is the `nomatch` form; machine folds read `dfa_member_machines`. |
| `928f7d20` | stage 2 | The walk inside an exact VM hybrid's inlined `<p>_prefilter` (`cand_locate_route` asks LOCATE on the DFA route for an inlined body); FIN3's VM cells `SPAN`/`AT`, FIN4's VM cells `ENDSET`/`LOWER`; a tie inside the body relocates there; `cand_project` (the boundary projection: a superset body's hand is a LOWER bound); `pcrec_cand_finish_vm`, the VM entry's FINISH ask, asserting verify-at iff `mrl_win` (LR-S3). |
| `eea0c23e` | checks | `run_rev_end.sh`, `run_dfa_stamps.sh` `[start]`, the answer net `tests/assertions/rev_end.rxt`, the window twin (`tests/revend/`), three mech arms; the L0 rows re-aimed. |
| `a7d63e45` | L2 | The ladder clause made effective (§4 item 1), `rev_end.rxt`'s decline and superset families, the RECOVER absence on `--list-axes`, re-pins. |
| `9e4e6971` | rows | Sabotage rows S758-S781 (`studies/locate_finish/mk_l2_rows.py`), `run_rev_end.sh` §3 (ladder) and §4 (dead seed under the sanitizer). |
| `f59658ca` | merge | main `64e8aa0e` merged in (clean). |
| `61018d49` | abi | abi 71 -> 72 at every reader (§5); the startset manifests re-pinned. |
| (R-12 merge) | merge + abi | main `a15fb77b` (R-12, abi 72) merged; abi renumbered 72 -> 73; conflicts resolved by mechanism (§5). |
| `0c5bb267`... | docs | Spec hunks, CLAUDE.md files, plan STATE, emit_sweep's trace site, L3's captures net, census controls, FILEPIN self-pin, this report. |

L2's "two separable commits" are `4863fc96` (L2.1, the stamp rule) and
`a2d3f861` (L2.2, the row); the abi number moves once, in its own commit
(§4 item 9).

## 2. Movers

All three censuses are `studies/locate_finish/l2_movers.py` over every corpus
pattern (`-p rx --features all`), parent build vs change build.

- **L1 vs `c85a1aac`: 0 movers** (c-default, c-vm, emit-ir, composition);
  `run_facts_checks.sh` 8/0.
- **L2.1 vs L1: 638 rows**, every one `RX_DFA_START` + `.search_form`
  `"reverse-pass"` -> `"attempt-start"`, which is exactly the
  `RX_DFA_SCAN "attempt"`/`"empty"` population (581 distinct patterns, 0
  outside it). `studies/locate_finish/results/l2_movers_l21.tsv`.
- **L2.2 vs L2.1: 274 rows**: 171 `rev-end` walks (the design's T4 figure, 171),
  85 empty bodies' `_match` -> `nomatch` (36 of them also
  `REQ_WHY "emitted"` -> `"dominated"`), 18 hybrids whose prefilter body is
  `empty` (`REQ_WHY "dominated"`, `MEMFN_LIBC "memchr"` -> `"none"`).
  `studies/locate_finish/results/l2_movers_l22.tsv`.
- **Stage 2 on `tests/revend/stage2_captures.rxt`** (default vs
  `-fno-rev-end`): **89 of 119 blocks move**, 88 exact hybrids whose inlined
  prefilter now walks, and `(\p{L}+)$` under utf8, where the deny loses its
  prefilter to the size cap and the walk keeps it (`ENGINE_SEL` `selected`
  vs `size-cap-retry`). The list is
  `studies/locate_finish/results/l2_stage2_movers.txt`. The corpus is green
  on the default build, `--engine=vm` and `-fno-rev-end` (1,292 cases each).

## 3. Sabotage rows

24 rows, S758-S781 (S758-S780 allocated at the start, S781 taken for the
ladder reader, both appended to `worktrees/.mgr/sabotage_ids.txt`). Written by
`studies/locate_finish/mk_l2_rows.py` from the current source. All DETECTED
by plant (`run_sabotage_matrix.sh`, solo runs on this branch; S764/S780
re-run after their reach probes were fixed, §4 item 11):

| id | plant | detector | verdict |
|---|---|---|---|
| S758 | the n-1 seed dropped | harness on rev_end.rxt, 39 fail | DETECTED |
| S759 | first accepting seed, not the minimum | harness, 7 | DETECTED |
| S760 | seed guard `end < search_from` deleted | harness, 3 | DETECTED |
| S761 | `end_pin` pins an optional repeat | harness, 3 | DETECTED |
| S762 | `end_pin` admits `(?m)$` | harness, 2 | DETECTED |
| S763 | `end_pin` drops the `\G` decline | harness (tests/assertions), 2 | DETECTED |
| S764 | dead-seed skip deleted (DFA) | revend §4 (sanitizer), 5 | DETECTED |
| S765 | tie takes n without the anchored run | harness, 11 | DETECTED |
| S766 | tie takes n-1 without the anchored run | harness, 21 | DETECTED |
| S767 | `nl_last` always false | harness 11, revend 6 | DETECTED |
| S768 | `rev-end` routed on CR_ATTEMPT too | harness 344, candoracle 3 | DETECTED |
| S769 | the stage-1 conjunct restored | revend, 7 | DETECTED |
| S770 | `empty` moved after `rev-end` | revend, 1 | DETECTED |
| S771 | the deny unplumbed | revend, 2 | DETECTED |
| S772 | `verify-at` loses DFA ENDSET | revend, 3 | DETECTED |
| S773 | `DFA_SCAN` stamp forked from LOCATE | revend, 3 | DETECTED |
| S774 | RECOVER's absence spelled `reverse-pass` | dfastamps, 1 | DETECTED |
| S775 | the LOCATE.whole deference dropped | harness, 6 (the walk's own assertion refuses) | DETECTED |
| S776 | the ladder's rev-end clause dropped | revend §3, 1 | DETECTED |
| S777 | VM verify-at takes ENDSET (LR-S3) | revtwin 1, revend 2 | DETECTED |
| S778 | no boundary projection | harness, 5 | DETECTED |
| S779 | inlined LOCATE asked on CR_VM | revend, 8 | DETECTED |
| S780 | dead-seed skip deleted on a hybrid | revend §4 2, revtwin 1 | DETECTED |
| S781 | anchored drop read by the ordinal | revend §3, 1 | DETECTED |

Re-aimed L0 rows (intent unchanged, each says so in a `RE-AIMED` comment):
S222, S237, S608, S738, S740, S741, S744, S745, S747; S693 re-aimed to abi 73 (AFTER 72).
`scripts/m6read_check_sab_anchors.py`: 632 rows, all anchors resolve. S693
re-run: DETECTED (codegen 3 fail). The L0 rows S738-S747 run again in the
landing chain (§7.2).

## 4. Deviations from the design text, with reasons

1. **LR-S12's reader (a code-vs-design contradiction, resolved, flagged for
   review).** The design's clause makes `drop-anchored` skip where the drop
   grows the member set and says the ladder "moves to its next rung". But
   `build_anchored_dfa` read the ladder ORDINALLY (`size_drop_rung >=
   SDR_NO_ANCHORED`), so the next rung (`drop-premul`, ordinal 2) dropped the
   anchored machine anyway, and the tie witness grew past the cap and was
   refused: `run_rev_end.sh` §3 found it (25,947 bytes against a 22,399 cap).
   The reader is now the row's FIRED bit (`Ctx.anchored_dropped`, from the
   fired record `fit_fired`), which is what the clause needs and what the
   fired record's own comment already says the ordinal is not. Answers do
   not move; the fallback table's checks are green; an artifact whose
   anchored machine overflowed its own state cap now retries that build at
   rung 2 (it overflows again, same artifact). S781 is the reader's row. The
   manager should confirm this is the intended reading of "moves to its next
   rung".
2. **The path derivation is not memoized**: `cand_path_of` re-derives per
   call. Compile time was not measured to move; a memo is a later change if
   one is wanted.
3. **FIN3's ATTEMPT ENDSET and FIN4's DFA LOWER take cells are not declared**:
   no producer asks them (no locator hands ENDSET on CR_ATTEMPT; nothing hands
   LOWER to a DFA finisher), and an unproduced declared cell would have to sit
   in `cand_oracle_unreached.tsv` forever.
4. **A tie on a VM hybrid is a relocate inside the inlined body** (FIN4 with
   the projected ENDSET), never the VM's anchored attempt, which is what
   LR-S3 asks for; `pcrec_cand_finish_vm` asserts it.
5. **NEXT is asked only for the forward machine** (`dfa_form_derive`); the
   reverse and anchored machines take the slot's fallback row without a
   selection, so the trace site `form-other` is retired
   (`scripts/emit_sweep.py`'s `TRACE_SITES`). The trace record FLOORS in that
   script were NOT re-measured (a full `--trace` two-build run; the gate's).
6. **The parameterized reverse-block helper parameterizes only the label and
   the dead-seed statement**, the two things the walk differs in; the design's
   "which-seed report" is the walk's own variable, not a helper output.
7. **The `nomatch` `<p>_match` returns -1 behind the startpos guard**, the
   value the search-filter wrapper returned for a no-match.
8. **Bit 52 for `PCREC_NO_REV_END` is this lane's pick** (the next free bit
   at the branch point); the manager confirms it at merge.
9. **The abi bump is its own commit**, after both L2 commits, so `4863fc96`
   and `a2d3f861` carry moved bytes at abi 71; landing the branch whole keeps
   main consistent.
10. **Listing spellings** (the manager's call per D86 practice): the `locate`
    axis lists `rev-end` and `unanchored`; FIN1 is `nomatch`; the RECOVER
    absence row on the `search-start` axis is a predicate row
    (`attempt-start`).
11. **Two sabotage reach probes were wrong at first** (S764/S780: a
    `$(` inside a double-quoted pattern ran as a command substitution, so the
    probe read UNREACHED). Fixed by escaping the dollar and re-run DETECTED.
12. **The window twin is opt-in** (`make test-revend-twin`, mech arm
    `revtwin`): it links libpcre2 and sweeps 4.1M cells, too heavy for
    `make test`; `run_rev_end.sh` (in `test-codegen`) and the answer net
    (in `test-corpus`) are the per-push nets.
13. **The end window is now the walk's denied form**: on an artifact the walk
    takes, `END_WINDOW` reads `"none"` (the slot is off the path).
    `run_prechecks.sh` §2 compiles its witnesses with `-fno-rev-end` and §2.6
    holds the default's absence.
14. **`run_fallback_table.sh`'s `seq-pfcd2` witness moved** to
    `(\bcat\b){2,}\w\w`: the old `(\bcat\b){2,}` is a hybrid with an `empty`
    body whose whole-window pre-check the deference drops (-705 B), so it
    fit under the `lowsize` cap and no longer reached the two-row sequence.
15. **The census's scan-edge ask (C6)**: `pcrec_dfa_scan_state_written` asks
    the forward machine's NEXT at build time, before the anchored build
    decides whether a `rev-end` tie relocates (and so whether F is a member).
    Declared in `asks_declared_L0.tsv` (WHEN `rev-end`, 31 rows) rather than
    reordered: the scan-edge pass must run before the anchored build.
16. **Scope note**: early in the lane a `mkdir -p /tmp/claude` ran (likely a
    pre-existing directory; nothing was written there). Every later scratch
    file is under `build/scratch/` in this worktree.

No ruling on file was contradicted by the code except item 1.

## 5. abi 72 -> 73 (built as 71 -> 72, renumbered on R-12)

Readers found by grep for the number and changed in `61018d49` (71 -> 72),
then again at the R-12 merge `be4b8dd2` (72 -> 73):
`src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI`; `tests/codegen/run_codegen_tests.sh`
`ABI_EXPECT` and its ledger message; `docs/spec/match_api.md` (the TU-guard
example's three lines, the `rx_info` table's `abi` row, §6¶17's sentence);
`tests/mech/sabotages/S693_abi_not_bumped.sh`;
`docs/dev/history/abi_changelog.md` (new top entry). Readers that do not cite
the number: `run_recursion_identity.sh` (B)'s FILEPIN self-pinned to
`be4b8dd2` (the R-12 merge, the lane's last src commit; re-pin at landing if
main's merge moves src); the digit is one width, so byte counts move only by
the text this lane changed: `run_cpset_structure.sh`'s twelve
`EMITTED_BYTES` rows +94 each (the ABI block's ESSENTIAL
`rx_info.search_form` comment now names `"attempt-start"`; `^foo$` +96 with
its two stamp values), re-recorded after a same-`-o` diff against main
`a15fb77b`'s compiler showed the abi digits and that comment only; the
resource rescue pin (762,884) is unchanged (the comment lives in the `.h`
there). The suites that count were run after the renumber: registry,
rxtsource, startset, cpset-structure, codegen 16/16 (§7.1).

**The R-12 merge.** Main `a15fb77b` (R-12 VMLAZY, abi 72) merged in. Six
conflicts, each resolved by mechanism: the abi change log (this lane's entry
on top as `73`, R-12's kept as "was `72`"); the codegen ledger message (R-12's
clause kept, this lane's appended as `72->73`); `run_recursion_identity.sh`'s
FILEPIN (main's R-12 self-pin `fd295ec0` taken, then re-pinned to this lane's
last src commit after the renumber); S693 (re-aimed to BEFORE 73 / AFTER 72);
`tests/mech/CLAUDE.md` (both sections kept); the rxtsource census (R-12's
`vm_lazy_rmin_prefix.rxt` +1 file / +20 blocks / +138 lines and this lane's
+1 / +46 / +240 summed: 279 / 5,616 / 53,743, run.sh 255 files).

## 6. The window twin and the answer net

- **Window-identity twin** (`tests/revend/run_window_twin.sh`, E9 / LR-S2 /
  LR-S4), against libpcre2 10.46 at every character-boundary offset of every
  subject over each pattern's alphabet, windows + answers + every group:

  | stratum | patterns | cells | window diffs | answer diffs | oracle diffs | E-VR |
  |---|---|---|---|---|---|---|
  | exact hybrid | 101 | 2,768,435 | 0 | 0 | 0 | **0** |
  | superset hybrid | 3 | 73,812 | 0 | 0 | 0 | 23,630 (allowed) |
  | DFA-only | 15 | 380,865 | 0 | 0 | 0 | 0 |
  | hybrid vs unprefiltered | 1 | 22,461 | 0 | 0 | 0 | 0 |
  | not rev-end (control) | 30 | 890,532 | 0 | 0 | 0 | 1,371,232 |

  (`studies/revend_twin/results/r3_strata.txt`; re-run in the landing chain.)
- **Answer net** `tests/assertions/rev_end.rxt`: 46 blocks, 215 cells, 25
  group slots, libpcre2 10.46-generated, re-verified by `verify_stage2.py`
  (215 cells, 25 slots, 0 FAIL); green on the default build, `--engine=vm`,
  `-fno-rev-end` and `-fno-anchored-dfa`. Family G is L3's captures net:
  `(\d+)$`, `(a+)$`, `a\Kb$`, `([^c]{1,3})$`, `(\s+){2}$`, `(\s$){1,3}`,
  `(\s+?){2}$` and the superset `(\w{1,2})(?:(?=)|)$`.
- `tests/revend/stage2_captures.rxt` stays green (119 blocks) and 89 of its
  blocks route through the new locator (§2).

## 7. Validation

### 7.1 Light gates (this lane, on the branch tip)

Each red section was read, fixed or re-pinned, and re-run green:
`test-rxtsource` (census pins for the new file), `test-registry` (axes
coverage 216 -> 219, the RECOVER absence listed), `test-search-pinned`,
`test-anchored-match`, `test-prechecks`, `test-fallback-table`,
`test-startset` (manifests, `tests/startset/CLAUDE.md`), `test-memfn-manifest`,
`run_rev_end.sh` 27/0. The census controls (`studies/locate_finish/`, trace
build, 5,963 rows incl. pcrec-bench read-only, 5,520 compiled): C1-C5 0,
C5-L0 0, C6 5,520 agree, C7 0.

### 7.2 Landing chain

OWED at the time of writing; filled in from `build/scratch/landing.log`'s
trailer by the chain's own summary (see the handback message).
