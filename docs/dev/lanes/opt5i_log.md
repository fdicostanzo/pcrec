# Lane opt5i — [OPT-5] STEP 2 implementation log

Charter: `docs/design/opt5_step2_twopass.md` revision 2 (merged `66da68c`),
panel review `docs/dev/reviews/2026-09-01-r49-opt5-step2.md`. Frank's go
2026-09-02. Worktree `worktrees/opt5i`, branch `lane/opt5i`, branched from
main `5496ca6`.

Scope mandate restated: this lane touches ONLY files under
`/home/duxevents/pcrec/worktrees/opt5i/`. `pcrec-bench` is read-only.

---

## Step 0 — orientation, 2026-09-02

Read in order: root `CLAUDE.md`; the design note in full (1,917 lines);
`docs/dev/lanes/opt5d_report.md` §5 (the two catches); D76/D77/D80/D82/D90/D94;
`docs/spec/match_api.md`'s `rx_info` block; `docs/spec/tuning.md` §2.18/§3/§3.2;
and the code sites — `emit_unanchored` (`src/gen/emit_dfa.c:4725`),
`unanch_start` (`:2473`), `dfa_needs_seed` (`:2161`), `dfa_premul` (`:2205`),
`dfa_table_name` (`:2655`), `dfa_scan_edge_name` (`:2709`), axis G
(`:4169`), axes H/I (`:4317`/`:4349`), `pcrec_emit_dfa_scan_stamps` (`:5843`),
`emit_info_def` (`:1660`), the `rx_info` struct text (`:637`-`:785`),
`src/opt/scanedge.c`'s `member_ok` (`:186`), `src/parse/axes_dump.c`,
`cli/main.c`'s flag loop, `tests/axes/run_axes.sh`,
`tests/registry/run_registry_tests.sh`.

Baseline build at `5496ca6`: clean (`make -j4`, rc=0).

---

## THE PREDICTION TABLE — written BEFORE any census was run

Per the brief item 9 and note §4.2. Nothing below is read off a measurement;
it is derived from the note's §4.2 fold table and the code as read above.
The measured column is filled in after the AFTER census.

### P-1. Stamp movements (note §4.2's five artifact classes)

| # | artifact class | stamp | today | PREDICTED after |
|---|---|---|---|---|
| 1 | pinned, forward and reverse reprs AGREE | `RX_DFA_TABLE` | the shared form name | unchanged |
| 2 | pinned, forward and reverse reprs DIFFER | `RX_DFA_TABLE` | `"mixed"` | the FORWARD machine's form name |
| 3 | pinned, reverse machine has edges the forward one lacks | `RX_DFA_SCAN_EDGE` | `"mixed"` or the reverse's value | the FORWARD machine's value (`"none"` where the forward machine has no edge) |
| 4 | pinned AND `RX_DFA_MATCH "unwrapped"` | both | folds three machines | folds two (forward + anchored) |
| 5 | DECLINED (any) | both | unchanged | **unchanged** |

### P-2. New stamp / mirror

| where | predicted |
|---|---|
| `RX_DFA_START` | present on every artifact with a DFA scan (same IFF as `RX_DFA_TABLE`), absent on a plain VM artifact; `"pinned"` on the accepted population, `"reverse-pass"` elsewhere |
| `rx_info.search_form` | non-NULL iff `pcrec_artifact_has_dfa_scan`, equal to the stamp; NULL on a plain VM artifact |

### P-3. Population (before the census confirms it)

Predicted from M1 (`docs/dev/opt5_step2_premeasure.md`), which measured the
predicate's verdict with a probe at today's tree: **`RX_DFA_START "pinned"`
on 175 of 2,845 corpus patterns**, all of them `RX_ENGINE "dfa"`, 0 hybrids
on the DEFAULT axis. The AFTER census either reproduces 175 or the difference
is a finding about the shipped predicate versus M1's probe (M1's probe omitted
P3's LIVENESS conjunct and P4's empty-engine clause, so the shipped predicate
can only be EQUAL OR SMALLER).

### P-4. `RX_DFA_MATCH` / `RX_DFA_SCAN` census movement

**No movement predicted on either.** Axis J is a new axis; axis G's predicate
(`job->anchored_ok && !dfa_engine_is_empty`) is untouched, and `dfa_scan_name`
reads `job->engine`, which this change does not write. Any movement in either
column is a finding.

### P-5. Size (note §5.5, narrowed)

DOWNWARD on the accepted population, and the movement is **the reverse
machine's tables and accessor block only**: its transition table, accept
table, byte-class table, any stay tables, any scan-edge membership tables,
the `<prefix>_reverse_*` accessor block, and the reverse scan loop's text.
NOT the view tables (`f->viewsel` is an OR over both machines), NOT the
accept ORDER. Declined artifacts move by the size of the new
`RX_DFA_START` line, the new `.search_form` initializer line and the new
struct member — all of which are `#define`/initializer text, plus prose that
`size_count.sh` does not count where the comment sits ABOVE its member.

Predicted sign per class:

| class | predicted size movement |
|---|---|
| pinned | large decrease (a whole machine's tables) |
| declined, DFA or hybrid | small increase (one `#define` line + one initializer line) |
| plain VM (no DFA scan) | small increase (one initializer line: `.search_form = NULL`) |

### P-6. What must NOT move (the named witnesses)

- `cls-atleast-4096` = `[a-z]{4096,}` — the predicate DECLINES it (`P1` fails:
  its start state does not accept). Its stamps and its size must not move
  except by P-5's declined row.
- `(?:[a-z]{0,8192})\z` — the whole form. Declined (view). Must not move.
- The `VIEW_DECLINE_MANIFEST` — every member declined, none accepted.
- The `unwrapped` `match`-regime rungs — a CONTROL; `<prefix>_match` is not
  touched by this change at all.

---
