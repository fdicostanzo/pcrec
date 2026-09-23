# fsreconcile — `[OPT-FIRSTSET]` §4 vs the real two-pass `rx_search`
Lane `fsreconcile`, 2026-09-22, opus. Analysis + probes only; nothing under `src/`/`tests/`; no clock read.

**VERDICT (i): §4's UNSOUND verdict STANDS on the real binaries — and the symptom is a DELETED match, not the spurious one §4.2 names.**

**The witness the note lacked.** `\b(?:true|false|null)\b`, the `base_`/`twin_`/`reseed_` binaries from `linux_ask_i89.md` block (B):

| subject | shipped | twin | twin + §4.4 re-seed |
|---|---|---|---|
| `"atrue xnull "` | `matches=0` | `matches=0` | `matches=0` |
| **`"atrue true"`** | **`(6,10)`** | **`matches=0`** | **`(6,10)`** |

`linuxask` was right that the reverse walk vetoes the spurious accept; the veto is not a rescue. `rx_search` has ONE forward scan, so a vetoed candidate is `return 0` for the whole call and every later real match goes with it. §4.1's witness cannot show this — its correct answer is `matches=0` either way. Structured sweep (72 subjects): twin 9 disagreements, re-seed 0. Exhaustive, three artifacts in one process, 4.03M subjects, two `\b`-leading patterns: **552 lost / 0 spurious / 0 wrong-span**, re-seed 0. The bench's `t-1m` reads `matches=0` on all three — structurally blind, as §9 said. The tree had already recorded the direction: `emit_dfa.c:4768` is MISCOMPILE-1 and `tests/codegen/run_offset_skip.sh:290` states its symptom as *"LOSES MATCHES on every pattern with a leading assertion"*.

**The general argument is a COUNT, not an argument.** `c2/skiproute_census.py`, all 3,957 shipped pattern lines (3,535 compiled): **0 artifacts run a candidate-start skip with no reverse walk**; **0 of 217 `RX_DFA_START "pinned"` artifacts carry any prefilter**; the narrowing's reach is **54** artifacts (42 plain DFA, 12 VM hybrid). The empty `pinned × prefilter` cell is STRUCTURAL — `emit_dfa.c:3191` gates the prefilter on `!start_acc`, `emit_dfa.c:5521` requires `up[UPC_PLAIN].accept`, and the latter implies the former — so the one shape whose reverse machine is not emitted can never carry a skip to narrow. §4.4's repair already ships as `pf_emit_ofs_reseed` (`emit_dfa.c:4951`) for [OPT-K], whose own comment calls it *"not optional on a machine that has one"*: a second call site, not a new mechanism. §4.5 splits — sound for the prefilter-less VM attempt loop (412 artifacts; the reason is that the loop carries NO state across an advance, not that the set is a necessary condition), unsound for `hybrid`, measured: `\b(true|false|null)\b` with captures reproduces the deleted match, because `hy_search_run` `return 0`s when `hy_prefilter` misses.

**What F2 now means.** F2 as written is NON-DISCRIMINATING and its `0,1,0` EXPECT is wrong: `"atrue xnull "` answers `matches=0` under a sound and an unsound mechanism alike, so the `0,0,0` the executor will report confirms nothing. §4.6.6 gives the one added line that makes it a test — `printf 'atrue true'`, EXPECT `1,0,1`. F1 untouched; **F3 stops being conditional on F2** — the repair is needed.

**Deliverables.** `firstset_design.md` §4.6 (appended; §4.1-§4.5 untouched) plus a §0 pointer. **Chartered as "§4.5" and renumbered to §4.6** — §4.5 exists and this document is cited by section id, including by `linux_ask_i89.md` block (B); flagged for the manager. Under `docs/dev/optloop/c2/`: `firstset_witness.c`, `firstset_exhaust.c`, `firstset_witness.sh`, `firstset_witness_results.txt`, `skiproute_census.py`, `skiproute_census.tsv`, `skiproute_summary.json`, and their `CLAUDE.md` section.

**Validation COMPLETE** for what this lane delivers (docs + probes): the runner was re-run end to end from the COMMITTED script and its committed results are that run's output. No suite is owed — nothing under `src/`/`tests/` moved. One instrument defect found and fixed in place: the census's first detector required the reverse TRANSITION TABLE, which [CC-DIFF] STEP 1's uniform fold may delete while the reverse WALK stays, and read 84 false positives.
