# r4 START-SET panel: ssc-checks (checks, controls and contract lens)

Review r4, checks/controls/contract lens, on `docs/design/startset.md`: 13 findings, 6 MAJOR, 4 MINOR, 3 NOTE, no BLOCKER. I read the design, D148 and the D122 add.4 / D124 / D46 / D91 texts, `learnings.md` §3, `docs/design/CLAUDE.md` and the `memfn/integration.md` C17 text. I checked claims against `src/gen/emit_dfa.c`, `src/facts/facts.def`, `tests/axes/run_axes.sh`, `tests/base/k65_precheck_whole_set.rxt`, the registry pin, `docs/design/startset/census_summary.txt` and the k82h/k82hbuild precedent. I ran nothing and edited nothing.

**Verified as sound, no finding:**
- K84 has exactly two `strcmp` readers, at `emit_dfa.c:6569` and `:6602`.
- `pcrec_artifact_has_dfa_scan` is `fit.chosen == ENGM_DFA || fit.prefilter` (`emit_dfa.c:384-387`), so the VM hat cannot flip it unless the code is changed to.
- Bit 47 is free; the highest bit is `PCREC_BIT(46)`.
- Highest S on main is S477.
- abi readers at `emit_dfa.c:52`, `run_codegen_tests.sh:3021` and `match_api.md §1¶7` (was `:302`) are correct.
- D148 rules Q3 (no force flag), so the D46 departure is not re-argued.

## F1. MAJOR. §6.1: the movers-only stamp `<PREFIX>_VM_START_SCAN` contradicts Frank's ruling on the K82 handoff stamp.
- **Claim:** the stamp goes on movers only "for k82h Q3's reasons".
- **Evidence:** k82h Q3's movers-only recommendation was reversed by Frank on 2026-10-05 (`litscan_k82h.md:1444`): "`REQ_HANDOFF` goes on EVERY artifact of the family, `none` where the handoff does not apply. House convention: stamps vary only by engine family, never by presence within a family." `k82hbuild_report.md:25` built it that way, at a cost of 30 bytes on every artifact. The note cites the reversed recommendation as its precedent.
- **Fix:**
  - Stamp every artifact of a stated family, with `none` where the hat does not apply. The family should be every VM artifact (hybrid included) or VM-none only; say which.
  - Re-price the byte-count readers as k82h §2.3a did: `m5_stage1_stamps.tsv`, the resource pin, `artifact_size_log.tsv`, the recursion-identity sweep.
  - The deny arm then reads "DENY == BASE modulo the abi digit and one line".
  - Correct §6.1's "k82h Q3's reasons".

## F2. MAJOR. §6.2: the C-SS control has zero overlap with either hat's mover set.
- **Claim:** E ⊆ S on unseeded machines is "the fact's own control" (685 artifacts, 0 violations).
- **Evidence:**
  - The note itself says `T == E` on unseeded machines, so no unseeded artifact can mover on the DFA hat.
  - `census_summary.txt` shows 30 seeded bench DFA-hat artifacts, of which 18 narrow. Every DFA-hat mover is seeded, so none is in the control population.
  - The `dfa_needs_seed` definition (`emit_dfa.c:3804`) confirms seeded means a context atom (`\b`, `(?m)^`, lookaround) is present.
  - The VM-hat movers are VM-none artifacts with no DFA machine, so no E exists for them.
  - The control therefore cannot reach the arms §3.2's soundness argument rests on: zero-width ∅ (`A_CTX`, `A_LOOK`, `A_BOL`, `A_GSTART`, `A_KRESET`) and `A_BREF`/`A_CALL`/`A_VAR`. All three of those are seeded or VM-only.
  - The drop-one twin firing on 685/685 shows S ≈ E on that population; it checks the comparison's arithmetic, not the walk.
- **Fix:** add two controls that take their expectation from outside the walk.
  - **(a) Seeded DFA machines:** every seed state's live escape set must be a subset of S. Take that set as the union over the seed-state transition rows, in the emitted `<p>_seed_state` and transition tables.
  - **(b) Start-byte oracle, all constructs:** over every subject on a small alphabet up to length L, for every start position where the `-fno-start-set` arm (or libpcre2) reports a non-empty match, `s[p] ∈ S`. This is independent of the walk and reaches the VM-only arms.
  - Add a per-`AKind` arm-reach count, K35 style, with a floor.
  - Pin that the build's C-SS reads the shipped `src/facts/startset.c` row, not `fs_probe.c`. `fs_probe.c` reconstructs the pipeline prefix itself, which is the c2prep F5 hazard.

## F3. MAJOR. §7 and Q7/D148: the sweep that supposedly covers the 2,263-artifact forced-VM population does not exist.
- **Claim:** "the per-change test-axes sweep of `-fno-start-set` × `--engine=vm` covers" the large population (Q7, ruled in D148 on this basis).
- **Evidence:** `tests/axes/run_axes.sh:50-52` sweeps every bit-flag axis "over the DEFAULT (auto) engine selection". The engine axis is a separate row (§2.11). There is no axis × engine product; the baseline carries no extra flags. At auto only 59 corpus VM-none movers are reached. §6.2's "every corpus pattern × every startpos × {auto, --engine=vm, --no-captures}" names no tool.
- **Fix:** stage 2 must deliver both of these as named, floored artifacts:
  - a `run_axes.sh` product arm with its own baseline, `--engine=vm` against `-fno-start-set --engine=vm`, with a mover-count floor;
  - an every-startpos differential in the style of `run_startbnd_diff.sh`, with the k82hbuild 4.4M-cell precedent for plain and ASan/UBSan runs.
- At stage 2 the DFA half of "both engines" has no population, so state that it is vacuous.

## F4. MAJOR. §6.3: sabotage coverage falls short of D122 add.4 item 3 ("a sabotage row per new predicate") and has reach gaps.
- **Claim:** S478-S485 cover the new predicates and arms.
- **Evidence:**
  - **§3.3 vs §6.3:** §3.3 says the verb/callout conjunct's row "ships declared UNREACHED with a compile-time assertion beside it". §6.3 has no such row; S483 is the utf8 one.
  - **Row coverage:** S478 drops one member of a 2-member set, which reaches `first-class` only. `first-memchr` (|S| = 1) has no answer witness. The `-bounded` twins (stop at n−1, both landing paths) have none either.
  - **S479:** a single plant on one emitter; there are four row emitters, each with its own re-seed call site.
  - **Predicate conjuncts:** F's seeded, nullable and |S| < 256 conjuncts, and V's `unanchored` and "no prefn" conjuncts, have no rows. `unanchored` is probably answer-invisible, so it needs a structural detector.
  - **Walk arms:** S481 plants only `A_CALL`. `A_BREF` and `A_VAR` have no witness. A reach witness for `A_BREF` exists, but only with a lookaround-captured group, e.g. `(?=(a))\1b`, where a bref→∅ plant loses the match at 'a'. The zero-width arms are covered only indirectly.
  - **S484:** it plants `|| vm_hat_selected` in a function that today has no VM-hat knowledge. The plant is plausible, but its detection should be confirmed by a solo run before numbering, as r1mtriage did for S220.
- **Fix:** add a row and a `SAB_REACH` per hat per form (memchr/class, bounded/unbounded), per V and F conjunct, and per conservative walk arm. A table-driven "arm → ∅" plant is one way to do it.

## F5. MAJOR. §6.2 "mover biconditional": the population is counted by `census.py`, which "no check reads", and the build only "reports both".
- **Claim:** the biconditional guards the movers. §10 Q3 says "no check reads the TSV".
- **Evidence:** standing question 2 asks who counts the population. K35 asks for a floor equal to a committed count. The k82hbuild precedent committed a mover manifest by ID (bench 47, corpus 160, 0 off-diagonal, deny identical).
- **Fix:** commit a mover manifest by ID for each hat and stage, checked at build, with the 0 off-diagonal and deny-identical arms. Update §10 Q3 to say the data file then moves a check when regenerated.

## F6. MAJOR. §2/§8: the walker and `DfaSel` are not gated by route.
- **Claim:** rows have a "DFA predicate" and a "VM predicate" column; `DfaSel` gains `route`.
- **Evidence:**
  - `dfa_select` (`emit_dfa.c:5071-5086`) calls `cand->applies(s)` for every non-denied row. `DfaCand` has one `applies` and no route concept.
  - The existing rows' `applies` read `s->us` and `s->d` (`pf_memchr_applies` at `:5709` and the others). A VM-route `DfaSel` has no machine, so a first-match walk reaches `pf_run_applies` and `pf_memchr_applies` before `first-class`, and they dereference nothing valid.
  - Every `DfaSel` is built with a positional initializer, e.g. `{ cx, d, NULL, true, -1 }`.
- **Fix:** state that the walk tests a per-row route mask before calling `applies`, so the "never" cells are data and not code. Make the zero value of `route` the legacy DFA route. Add a structural check that no `DfaSel` initializer omits the new field. Say how `--list-axes` and `axes_registry_check.sh` list a two-predicate row.

## F7. MINOR. §8 abi/reader list is incomplete.
- **Claim:** readers are "found by grep at landing", with five reader classes listed.
- **Evidence:** the list omits several readers a new axis and a moved stamp reach:
  - **Registry axes pin:** `run_registry_tests.sh:633-645` (189, +3 per axis).
  - **Doc and header counts:** `registry.md` row/axis counts; `cli.md`'s deny list; `lib/pcrec.h` and `axes.def` rows.
  - **Other readers:** `tests/codegen/CLAUDE.md` and `docs/testing.md` abi mentions; the `rx_info.prefilter` runtime mirror of the four new `DFA_PREFILTER` values (`emit_dfa.c:3141`); `run_axes.sh`'s `tuning.md` "(bit N)" cross-check.
- **Fix:** add them.

## F8. MINOR. §5: VMSTART is classed D91 budget 1, but §4.4 says it runs per failed attempt.
- **Evidence:** D91 budget 1 is the prefilter, "run ~once per match point, dispatch cost is noise". §4.4 says the call entry is paid per failed attempt, on candidates 1-2 bytes apart. By D91's own definition that is budget 2 ("inside the pattern ... dispatch may NOT be noise"). The budget is a column of the manifest row, so a misclassification would let the kit choose dispatch cost incorrectly.
- **Fix:** classify as budget 2, or split the row by regime and re-measure at the site.

## F9. MINOR. §3.1: the `start_set` walk's `nullable` column is a second nullability derivation, and the epoch is misstated.
- **Claim:** the epoch is E2 "beside `nullable`/`req_set`".
- **Evidence:** `facts.def:42` has `NULLABLE` at epoch 1 (E1). pf35/k69 already had to unify two nullability definitions, including the `A_CALL` rule.
- **Fix:** derive `S.nullable` from the NULLABLE fact (S's value being the erased-language bit, ≥ NULLABLE) rather than re-walking, with a check, or state why the second bit is a different question under D120's one-owner rule.

## F10. MINOR. §8: stage gates are not named.
- **Evidence:** stages 0 and 1 say "none (the identity gates)". The established zero-mover instrument is `scripts/emit_sweep.py` (five streams, REACH figure, `--ref`), which the design does not name. Stage 0 ships the K84 fix with no structural guard against name-reading, because S485 only becomes reachable at stage 3.
- **Fix:** name the zero-mover gate and its reach count per stage. Add a cheap stage-0 check that no `strcmp` on a `dfa_pfs[]` row name remains.

## F11. NOTE. Citation and wording errors.
- §4.1 cites `emit_dfa.c:5454` for P5, "the window's start is a lower bound". That line is the EOL-view emission; re-cite.
- §7 says the re-seed read is "guarded by `q > entry`". The emitted guard is `pos ? seed_state[...subject[pos-1]] : s0` (`emit_dfa.c:6373`). The read is safe at any `pos` > 0, so the claim should match the text.
- §2 cites "`axes.def:106`" for "most axes are deny-only". Line 106 is the FORCE PAIRS comment; the deny-only statement is the rung-ladder header.
- §4.1 says the narrowed rows reuse "the same emitters called with T". The existing memchr and byte-class rows have `reseeds = false` and emit no re-seed (`:6465-6468`), so wrapper emitters are required; the note's own "a second and third call site" implies that.

## F12. NOTE. Stamp and row names carry the form.
- `first-memchr` and `first-class` become the `DFA_PREFILTER`/`VM_START_SCAN` values. D146 and D147 make the form the kit's choice, so after migration the names would misreport it, and renaming means another abi event and spec change. This is the same debt as the existing `memchr`/`byte-class` rows. Consider an operation-named value now, e.g. `first-set`, with |T| = 1 as a form detail, or record the re-spec as a known M1 cost.
- The same row name on both stamps means different things per hat.

## F13. NOTE. (d) [MEMFN] D146/D147 conformance, otherwise adequate.
- VMSTART as a `pending` manifest row, with the stage-2 extraction producing one emitter and no new `memchr(` text, avoids two spellings under C17.
- Both T1 PF and VMSTART rows must name the extracted emitter's function. The static half fires on any function that spells a search form without being named.
- The `|set| == 1 → memchr` split is a pcrec-side form choice; the note says it migrates with the kit, which is acceptable if recorded.
- The extracted primitive is cross-file, so it needs a `pcrec_` prefix and the link-symbol check.
