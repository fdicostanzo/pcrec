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

## PREDICTION vs MEASURED — the census, run 2026-09-02

Both censuses over the same 2,846 comparable corpus patterns (2,848 extracted;
2 refused on one side only are excluded from the join). Default flags,
`--features all`, captures ON — the SAME flags M1 used, deliberately, so the
population is comparable to the premeasure memo's.

### P-1 / P-4 — stamp movements

| stamp | predicted | MEASURED | verdict |
|---|---|---|---|
| `RX_ENGINE` | no movement | **0 moved** | HELD |
| `RX_DFA_SCAN` | no movement | **0 moved** | HELD |
| `RX_DFA_PREFILTER` | no movement | **0 moved** | HELD |
| `RX_DFA_MATCH` | no movement (axis G untouched) | **0 moved** | HELD |
| `RX_DFA_TABLE` | `"mixed"` → the forward form name where the reprs DIFFERED | **0 moved** | HELD **with an EMPTY population** — see below |
| `RX_DFA_SCAN_EDGE` | the forward machine's own value where the reverse machine had edges the forward one lacked | **8 moved, every one toward `"none"`** (7 from `"range"`, 1 from `"bitmap"`) | HELD, and in the predicted DIRECTION |

**The `RX_DFA_TABLE` row's population is EMPTY on this corpus, and that is
worth stating rather than reading as a pass.** The prediction was conditional
("where the forward and reverse reprs DIFFER"), and no pinned artifact in this
corpus has such a pair — every one is `premultiplied` on both machines. So the
fold's reverse-drop is UNEXERCISED by the census, and what tests it is
`run_search_pinned.sh` §3, which recomputes the fold from the emitted text on
every artifact including the declined ones.

The eight `RX_DFA_SCAN_EDGE` movements are the note's own `mc2` shape: the
reverse machine grows edges more readily than the forward one, so an artifact
whose forward machine carries no edge used to stamp the REVERSE machine's
value. Those eight are exactly the artifacts that would have stamped a fact
about text no longer in the file.

### P-2 — the new stamp and mirror

Both present and agreeing on every artifact; `run_search_pinned.sh` §2 asserts
it corpus-wide in both directions, including the NULL case on a plain VM
artifact. 2,305 artifacts carry a DFA scan (1,563 pure DFA, 742 hybrid at
`--no-captures`; 1,177 hybrid at the default), 249 plain VM stamp nothing.

### P-3 — the population

**MEASURED: 175 pinned, of 2,846.** That is EXACTLY M1's number
(`docs/dev/opt5_step2_premeasure.md`), measured on the same flags by a
different instrument (M1 used a probe stamp on an unshipped branch; this is
the shipped `RX_DFA_START`). The prediction said "equal or smaller than 175,
because the shipped predicate adds P3's liveness conjunct and P4's
empty-engine clause"; it is equal, i.e. neither conjunct declines anything on
this corpus. All 175 are `RX_ENGINE "dfa"`; **0 hybrids on the default axis**,
also matching M1.

`rewind_position` moved 1,872 → 1,697 artifacts: a difference of exactly 175.
The population and the mechanism agree.

### P-5 — size

`.c` non-comment bytes, over the 2,846 joined patterns (2,552 that compile):

| class | n | before | after | delta | per artifact |
|---|---|---|---|---|---|
| pinned | 175 | 2,179,360 | 1,613,744 | **−565,616** | **−3,232.1** |
| declined (DFA + hybrid) | 2,062 | 37,568,686 | 37,715,088 | +146,402 | +71.0 |
| plain VM (no DFA scan) | 315 | 5,122,621 | 5,130,496 | +7,875 | +25.0 |
| **total, `.c` only** | 2,552 | 44,870,667 | 44,459,328 | **−411,339** | −0.92 % |

Plus the `.h`: **+39 bytes on every artifact of both engines**, the
`search_form` member declaration in the shared `PCREC_RX_ABI_H` block. The
comment above it costs ZERO counted bytes, which is the measured
above-the-member placement `[ENG-ABS]` and `[DD-13b.W1.2]` both record. Whole
change, both files: **−411,339 + 39 × 2,552 = −311,811 bytes**, −0.69 %.

Largest decreases are `.*`, `(?i)a*`, `(?:|[^a])*` and the nullable
`{0,2}`-wrapped shapes at about −4,500 bytes each; largest increases are +71,
the declined-artifact constant. **The prediction's direction and its NARROWING
both hold**: nothing but the reverse machine's tables, accessor block and loop
left the accepted artifacts, and the declined population moved by exactly the
two new lines.

### P-6 — the named witnesses that must not move

All five hold, asserted permanently in `run_search_pinned.sh` §9:
`[a-z]{4096,}` (`cls-atleast-4096`) and `(?:[a-z]{0,8192})\z` are DECLINED;
`[a-z]{0,4096}`, `{0,8192}` and `{0,16384}` are PINNED. The
`VIEW_DECLINE_MANIFEST`'s five shape-anchors are all declined (§8), and the
`unwrapped` `match`-regime control is untouched because `<prefix>_match` is
not changed by this row at all.

---

## Stage log — 2026-09-02, after the first full `make test`

**A contaminated run, discarded.** The first `make test` was started before
manager ruling R1 arrived; landing R1 rebuilt `build/pcrec` MID-RUN, which is
exactly the contamination `tests/codegen/CLAUDE.md` warns about ("doing it
during a `make test` contaminates that run and it has to be discarded and
redone"). Killed with `scripts/safekill 1099500` (PID only, never
`pkill -f`), and re-run clean.

**The clean run found four red sections, four distinct causes, none of them a
defect in the emitter.** Each is written up in the report's §6a with its
re-derivation; the short form is: my new `tests/assertions/` corpus file
joined `run_expansion_diff.sh`'s pinned population; the three size-cap
witnesses lost half their bytes and stopped reaching the cap; the
premultiplied-table check demanded a reverse table a pinned artifact does not
have; and my own corpus file's `[a-z]{0,4096}` moved [ENG-ABS]'s
anchored-overflow census from 0 to 1.

**The last one is the one I got wrong rather than the tree.** A startpos
coverage file has no business moving an unrelated row's population, and the
check says so in its own message ("do not simply re-pin this line"). The
pattern is out of the corpus; `run_search_pinned.sh` §6/§10 drive it
out-of-corpus at every startpos anyway.

## Stage log — the three owed §7 measurements

Taken with instrumented or planted builds, each reverted and the tree rebuilt
and `make strict`-verified afterwards.

**Item 9 — `N_hybrid_pinned` under the FORCE axis: 70** (captures on), **23**
under `run_search_pinned.sh`'s own `--no-captures` flags. M1's `0` was a
default-axis number. This did not stay a number in the report: the force axis
is now a SECOND ARM of the corpus sweep, because before it the default axis
had 742 hybrids and ZERO pinned, so every corpus-scale claim the file made
about a pinned hybrid rested on §4's single named `\Ka*` witness. K35's shape.

**Item 10 — the P3 EVALUATION count: ZERO, on all three axes.** Instrumented
stamp over 2,850 patterns:

| axis | asked | notasked-p1 | notasked-p2 | notasked-noseed |
|---|---|---|---|---|
| default | **0** | 1,696 | 3 | 177 |
| `-fprefilter` | **0** | 1,004 | 0 | 70 |
| `--no-captures` | **0** | 1,705 | 3 | 224 |

P3 is never ASKED. S219's UNREACHED declaration is now measured rather than
only derived, which is the third of the three outcomes §7 item 10 enumerates.

**Item 13 — S220's disjointness from S218: they are NOT disjoint, and neither
has a failing direction alone.** Planted each half, rebuilt, swept:

| plant | pinned artifacts | `run_search_pinned.sh` |
|---|---|---|
| clean | 224 | 17 / 0 |
| P1 widened alone (S218 as first written) | **224** | **17 / 0** |
| P2 dropped alone (S220 as first written) | **224** | **17 / 0** |
| BOTH | **243**, 19 flip | **13 / 5**, incl. a real ANSWER divergence |

So S218 became a TWO-HUNK row (`SAB_FILE2`, S108's own shape) and S220 ships
declared `UNDETECTED` with the derivation. S222's fork was vacuous for the
same reason and now forks both halves.

The sweep also named P2's real discriminating population — `\B`, `\B\B`,
`\Bx*`, three artifacts, NOT the `\bx*` the note names — and showed why S220
is inert even at two hunks: all three are seed-needing, so removing P2 at the
start state only lets them reach P3, whose per-seed loop applies P1 and P2
again and refuses them there.

## Stage log — gates

| gate | result |
|---|---|
| `make -j4`, `make strict` | clean, repeatedly, including after every plant was reverted |
| `make test` | four sections red for four non-defect causes, all re-derived; all four sections re-run GREEN (resource 30/0, anchored-match 15/0 + 7/0, lookaround 5/0 + 11/0) |
| `make test-codegen` | 109/0, 31/0, 22/0, 32/0, 7/0 |
| `make test-registry` | 0 failed (the axes coverage guard moved 88 → 93, read from a run) |
| `make test-search-pinned` | **17 / 0**, two axes |
| `make test-vm-frameless` | **6 / 0**, two axes |
| `make test-premul-table` | 16 / 0 |
| harness on the two new `.rxt` files | 112 / 0 at four blocks + the seeded sibling |
| `scripts/m6read_check_sab_anchors.py` | 218 sabotages, 231 anchor sites, all resolve |
| `make test-axes` | *running at the time of writing* |
