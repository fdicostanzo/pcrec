# Lane opt5i — [OPT-5] STEP 2 IMPLEMENTATION, delivery report

The START-PINNED SEARCH ELISION, built to `docs/design/opt5_step2_twopass.md`
revision 2 (merged `66da68c`). Branch `lane/opt5i`, worktree
`worktrees/opt5i`, branched from main `5496ca6`. 2026-09-02.

**Not merged.** The manager reviews, runs the union battery, arbitrates the
sabotage-id range and merges.

---

## 1. What landed

`<prefix>_search` scanned the same bytes twice: forward for the match END,
backwards over an independently built REVERSE machine for the match START.
On a machine whose forward start state accepts UNCONDITIONALLY the backwards
pass provably computes `search_from` on every call, so the whole reverse
machine now leaves the artifact — tables, accessor block, scan-edge membership
tables and loop.

Measured over the corpus: **175 of 2,846 patterns take the pinned form**, and
each one loses **3,232 bytes** of non-comment emitted C.

| piece | where |
|---|---|
| the predicate P0-P5 | `src/gen/emit_dfa.c`, `start_pinned_applies` + `start_pinned_assert_routing` |
| P2, LIFTED and shared | `src/opt/scanedge.c`'s `pcrec_state_view_invariant`, declared in `src/core/internal.h`; `member_ok` now calls it |
| axis J | `dfa_search_starts[]`, `dfa_search_start_of/_name`, `dfa_search_is_pinned` |
| the elision | `emit_unanchored`'s one `if` |
| the two stamp folds | `dfa_table_name`, `dfa_scan_edge_name` — both stop reading `job->rdfa` when pinned |
| the ORIENTATION BLOCK | step 3 and the hybrid's HALF 1 both branch on the same predicate |
| the stamp | `RX_DFA_START`, in `pcrec_emit_dfa_scan_stamps` (so a HYBRID carries it) |
| the mirror | `rx_info.search_form`, appended after `nentries`, guarded on `pcrec_artifact_has_dfa_scan` |
| the flag | `PCREC_NO_START_PINNED` (bit 22), `-fno-start-pinned`, masked out of `rx_info.flags` |
| `--list-axes` | `src/parse/axes_dump.c`, axis `search-start`, two rows |
| abi | 15 → 16 at every reader D94's grep returns |

---

## 2. Commits

| commit | what |
|---|---|
| `8b280f5` | the lane log and the PREDICTION TABLE, written before any measurement |
| `25ca4a8` | axis J, the predicate, the elision, the stamps, the mirror, the flag, abi 16 |
| `e66fe83` | the D80 spec deltas and two directory `CLAUDE.md` entries |
| `bce0d0b` | `tests/codegen/run_search_pinned.sh` + its driver, the `searchpinned` mech arm, sabotage rows S218-S222 |
| `dd4ad2a` | the `startpos > 0` corpus witnesses S221's population needed |
| `dad6306` | the census, measured against the prediction table |

Range for review: `5496ca6..lane/opt5i`.

---

## 3. The abi site list AS FOUND BY GREP (D94)

```sh
grep -rEn '\.abi = |ABI_EXPECT|`rx_info\.abi` is' src lib cli tests docs Makefile
grep -rn  'RECURSION_IDENTITY_FILEPIN' tests
```

Run at this worktree, the grep returns these LIVE readers of the number, and
all of them moved:

| reader | before | after |
|---|---|---|
| `src/gen/emit_dfa.c` — the `.abi = N` stamp | 15 | **16** |
| `tests/codegen/run_codegen_tests.sh` — `ABI_EXPECT=N` | 15 | **16** |
| `tests/codegen/run_codegen_tests.sh` — the `[DD-14.FB]` §10.4 bump ledger sentence | ends at 14→15 | **appends this bump's clause** |
| `docs/spec/match_api.md` — the §3-area "`rx_info.abi` is `N`" sentence | 15 | **16** |
| `docs/spec/match_api.md` — the §6 "`rx_info.abi` is `N` on every artifact today" sentence | 15 | **16** |
| `tests/codegen/run_recursion_identity.sh` — `RECURSION_IDENTITY_FILEPIN` (the (B) pin) | `6dbdf41` | **RE-PIN OWED — see below** |

**The rest of the grep's output is NOT a reader and was deliberately not
touched**: historical narrative in `docs/dev/decisions.md`, `dev_journal.md`,
the lane logs and reports, the `docs/dev/reviews/` files, the completed design
notes' own ritual tables (`premultiplied_dfa_table.md`,
`anchored_match_unwrapped.md`, `offset_k_skip.md`, `emitter_form.md`,
`artifact_size_term.md`, `dd13_format/`), `tests/codegen/CLAUDE.md`'s pin
HISTORY (`ac4917d`/`.abi = 2`, `8fc1e51`/`.abi = 3` — worked examples of the
mechanism, not the current number), and `docs/design/m6read_samples/*.c`, which
are FROZEN sample artifacts at `.abi = 2`.

**`docs/design/opt5_step2_twopass.md` §4.4's own five-reader table was NOT
edited either**, on the note's own instruction: it is a dated snapshot taken
2026-09-02 to show the rule works, and the note says "Do not copy that table
into the implementation."

### THE (B) RE-PIN IS THE ONE THING THIS LANE CANNOT DO, and it is owed

`RECURSION_IDENTITY_FILEPIN` must name **this change's last `src`-touching
commit**, which is `25ca4a8` on this branch — but D76's pin is a commit the
gate can `git archive`, and after the manager's merge the reachable commit is
the MERGE's, not this branch's. Setting it to `25ca4a8` here would pin a
commit on a lane branch. **The manager sets it at merge**, to the merge's own
last `src`-touching commit, exactly as the `w12` and `[OPT-5]` STEP 1 landings
did. Until then `make test-codegen`'s (B) comparison will refuse with D76's own
message (`subject stamps '.abi = 16', pin 6dbdf41 stamps '.abi = 15'`) — which
is the gate working, and is reported here rather than worked around.

---

## 4. Acceptance table

### 4.1 The nine structural checks of the note's §5.4

All in `tests/codegen/run_search_pinned.sh`, **16 passed / 0 failed** at
`dad6306`, `PROCS=4`.

| note §5.4 | claim | where | verdict |
|---|---|---|---|
| 1 | an accepted artifact has no `rewind_position`, no reverse table, no reverse accessor block | §2, corpus-wide | **GREEN**, 2,848 patterns |
| 2 | a declined artifact still has all three | §2, corpus-wide | **GREEN** (with the attempt/empty bucket named and counted separately — 375 artifacts legitimately have no reverse body at all) |
| 3 | the stamp and the body agree: `"pinned"` iff `rewind_position` absent | §2, corpus-wide | **GREEN** |
| 4 | neither stamp fold names a machine the artifact does not contain | §3, corpus-wide, on DECLINED artifacts too | **GREEN**, 2,305 artifacts with a DFA scan |
| 5 | P5 at the ENGINE level, plus the hybrid's bound-not-answer shape | §4 | **GREEN** (see finding F3 on `window_end`) |
| 6 | the `== -1` gate is PRESENT and its LOAD-BEARING comment with it | §5, every pinned artifact | **GREEN** |
| 7 | C3: on pinned ∩ `search-filter`, `_match` never returns −1 | §6, behavioural | **GREEN** for every `startpos <= n` (see finding F1) |
| 8 | M8: `rx_info.search_form` == the stamp on every artifact, both engines, NULL case included | §2, corpus-wide | **GREEN** |
| 9 | P0's routing premise asserted in the compiler | §7 + the 175 pinned compiles | **GREEN** |

Plus, in the same file: the `VIEW_DECLINE_MANIFEST` all-and-only with its five
NAMED shape-anchors and a floor (§8); the five named witnesses that MUST NOT
MOVE (§9); the pinned-population floor (§9); the byte-identity of all 2,083
declined artifacts under the deny flag (§9); the every-startpos `caps[0][0]`
differential (§10); and the whole-file negative control (§1).

### 4.2 Sabotage rows

Ids **S218-S222**, PROVISIONAL — `tests/mech/sabotages/CLAUDE.md` makes the
range the manager's to arbitrate at merge, with a SIMULTANEOUS substitution if
it has moved. All five anchors resolve
(`scripts/m6read_check_sab_anchors.py`: 218 sabotages / 230 anchor sites, all
resolve). A new mech arm `searchpinned` is registered in
`tests/mech/run_sabotage_matrix.sh` and in the sabotages' `CLAUDE.md` closed
vocabulary, BEFORE the rows that name it (R31 C11).

| row | sabotage | `SAB_EXPECT` | reach declared |
|---|---|---|---|
| S218 | P1 widened to `state_acc_any` | DETECTED | `SAB_REACH` on `$`'s decline + `SAB_REACH_POP` on the `(?m)` manifest floor (≥ 12) |
| S219 | P3 dropped, both arms | **UNREACHED, declared** | `SAB_REACH` asserts the derivation's own shapes still behave as its header says |
| S220 | P2's view/context clause dropped | DETECTED | `SAB_REACH` on `\bx*` declining at P2 and `x*` being PINNED (the pair is what says the decline is P2's and not P1's) + the manifest floor |
| S221 | `caps[0][0] = 0` instead of `= search_from` | DETECTED | `SAB_REACH` on the emitted `= (ptrdiff_t)search_from` + `SAB_REACH_POP` on the new corpus file (≥ 60) |
| S222 | the stamp forked from the selection | DETECTED | `SAB_REACH` on the clean stamp agreeing with the body + the manifest floor |

**Solo mech rows are the MANAGER's**: the brief reserves the union battery,
and `make mech` rebuilds the tree once per sabotage. Each row carries a
PREDICTED disposition in its `SAB_DOC_FIGURE` with the canonical DETECTED
figure marked as owed from that run, which is `tests/mech/sabotages/CLAUDE.md`'s
own convention for a row landed outside a battery.

**S219's UNREACHED is argued, not assumed.** Its header carries the derivation
that the P3-discriminating population is EMPTY on `ENG_UNANCH` rather than
merely unpopulated, names the six candidate witness shapes worked through and
rejected, and points at the compiler assertion that is the conjunct's real
guard. The `[MECH-REACH]` reverse check reads NOW REACHED the day somebody
builds the machine it defends against, which is the whole value of shipping it.

**S220's disjointness from S218 is argued in its own header** (the note's §7
item 13): S218's discriminating population fails P1 FIRST, so P2 is never
reached on it and S218's plant leaves every classctx member DECLINED; `\bx*`
is the named member of S220's population S218 does not catch, and it is a
witness in §1 for exactly that reason.

**S222's non-vacuity is demonstrated, not asserted** (r49 [check 7]): the fork
is the WIDENED `state_acc_any` read, on which §8's manifest population
disagrees with the narrowed one by construction, so the row cannot pass by the
two predicates happening to agree.

### 4.3 Suite results

| gate | result |
|---|---|
| `make -j4` | clean |
| `make strict` | clean — "whole tree compiles clean with `-Werror -Wshadow`" |
| `make test-search-pinned` | **16 / 0** |
| `bash tests/harness/run.sh` on the two new `.rxt` files | **112 / 0** |
| `scripts/m6read_check_sab_anchors.py` | 218 sabotages, 230 anchor sites, all resolve |
| `make test` | *filled in below* |
| `make test-codegen` | *filled in below* |
| `make test-axes` | *filled in below* |

---

## 5. The prediction table vs measured

Written into `docs/dev/lanes/opt5i_log.md` at `8b280f5`, BEFORE the BEFORE
census was run, and compared at `dad6306`. Summary; the log has the full
tables.

| prediction | measured | verdict |
|---|---|---|
| `RX_ENGINE` / `_DFA_SCAN` / `_DFA_PREFILTER` / `_DFA_MATCH` do not move | **0 moved on each** | HELD |
| `RX_DFA_TABLE` moves `"mixed"` → the forward form name where the reprs DIFFER | **0 moved** | HELD, but on an **EMPTY POPULATION** — no pinned artifact in this corpus has a forward/reverse repr pair that differs, so the census never exercised the fold's reverse-drop. §3 of the check is what tests it. |
| `RX_DFA_SCAN_EDGE` moves toward the FORWARD machine's own value | **8 moved, every one to `"none"`** (7 from `"range"`, 1 from `"bitmap"`) | HELD, in the predicted direction — the note's own `mc2` shape |
| `RX_DFA_START` "pinned" on 175 artifacts, all pure DFA, 0 hybrids | **exactly 175, all `RX_ENGINE "dfa"`, 0 hybrids** | HELD. The same number M1's probe measured on an unshipped branch, now from the shipped stamp |
| `rewind_position` leaves exactly the accepted population | **1,872 → 1,697, a difference of exactly 175** | HELD |
| size DOWN on pinned, UP slightly elsewhere, and NOT including the view tables | pinned **−3,232 B/artifact**; declined **+71 B**; plain VM **+25 B**; `.h` **+39 B on every artifact** | HELD, including the narrowing |
| the five named witnesses do not move | all five hold | HELD |

**Net size: −411,339 bytes of `.c` plus +39 × 2,552 bytes of `.h` = −311,811
bytes, −0.69 %** over the compiling corpus.

---

## 6. The §7 measurements owed BEFORE SHIP

| note §7 | measurement | RESULT |
|---|---|---|
| 9 | `N_hybrid_pinned` under the FORCE axis | *filled in below* |
| 10 | the P3 EVALUATION count (not the decline count), both axes | *filled in below* |
| 11 | `N_pinned ∩ search-filter` over the corpus | **0.** All 175 pinned artifacts stamp `RX_DFA_MATCH "unwrapped"`. C3's corpus population is EMPTY; its three named members (`[a-z]{0,4096}`, `{0,8192}`, `{0,16384}`) are out-of-corpus witnesses, which is what §6 of the check drives and asserts the membership of |
| 12 | the `startpos > 0` population over the 175 | **5 patterns, 14 cells** (`x*` 5, `a*` 4, `(?>a?)` 2, `(?:ab)?+` 2, `\Q\E` 1). Both of §5.6d's acceptable discharges taken: counted here, and 112 synthetic cells built (`tests/base/start_pinned_startpos.rxt` + its seeded sibling) |
| 13 | S220's disjointness from S218 | *filled in below* |
| 5 | artifact-size movement, predicted then compared | **DONE**, §5 above |

---

## 7. FINDINGS — where the note and the code disagreed

Recorded, not patched around.

**F1 — C3 is true only IN RANGE, and the note says "on every call".** §3.5 and
§1.1 both say `rx_search` "returns 1 with `caps[0][0] == ctx->pos` on every
call" on the pinned ∩ `search-filter` population, from which the fallback's
`return -1` is unreachable. It is not true at `search_from > subject_length`:
the emitted range guard's own `if (search_from > subject_length) return 0;`
sits ABOVE the scan, so the search returns 0 and `<prefix>_match` correctly
returns −1 there — on a pinned artifact exactly as on any other. The claim as
the note states it is falsified by one cell per subject; the claim worth
making, and the one the check asserts, is over the calls the search actually
performs. The driver counts the two separately (`on_match_neg` and
`on_match_neg_inrange`) so the distinction is visible rather than absorbed.

**F2 — the `RX_DFA_TABLE` fold's reverse-drop has an EMPTY corpus
population.** §4.2's prediction table row 2 (`"mixed"` → the forward form name)
never fires on this corpus: every pinned artifact is `premultiplied` on both
machines. The change is still correct and still necessary — an artifact with
that pair WOULD stamp a fact about absent text — but the census cannot
demonstrate it, so what stands behind it is §3 of the check, which recomputes
the fold from emitted text on every artifact rather than watching for movement.

**F3 — the hybrid's `window_end` clamp is CONDITIONAL, and §1.2 quotes it as
if it were not.** The note reproduces

```c
attempt_position = (size_t)window[0][0];
window_end = (size_t)window[0][1] < subject_length ? (size_t)window[0][1] : subject_length;
```

as the emitted `rx_search_run`. `src/gen/emit_vm.c` emits a `window_end` at all
only where the artifact carries an MRL clamp (`v.nclamp > 0`); the `\Ka*`
hybrid the note itself uses as P5's witness has none. The `attempt_position`
half — which is the bound-not-answer argument, and the half that matters — is
unconditional and is asserted unconditionally; the clamp is asserted where it
exists.

**F4 — `docs/guide/` does not exist, so §6 row 10 has no target.** The note's
spec-delta table row 10 says "a pointer only if an existing page already names
the two-pass cost". The tier is chartered as `[GUIDE-1]` and unbuilt; there is
no `docs/guide/` directory in the tree. Row 10 is discharged as vacuous rather
than by creating the tier, which is not this lane's to charter.

**F5 — `docs/spec/registry.md`'s `--list-axes` line was ALREADY STALE by
[OPT-5] STEP 1, and this lane's own read is what found it.** It read "63 rows /
21 axes" and enumerated 21 axis names omitting `scan-edge` and `scan-body`,
which STEP 1 landed. The live dump is **72 rows / 24 axes**. Moved, with the
staleness named in the file so the third demonstration of its own "re-derive
rather than trust this line" rule is on the record.

**F6 — `PCREC_NO_SCAN_EDGE` is NOT in `emit_info_def`'s `strategy_denials`
mask and `PCREC_NO_START_PINNED` is.** Every other answer-identity deny flag in
the family is masked. The [OPT-4] comment beside the mask records a MEASURED
defect from leaving one out: unmasked, the flag moves `rx_info.flags` on EVERY
artifact including ones the axis cannot act on, which destroys the byte
identity that makes the denied build a ground truth. Axis J is masked for
exactly that reason, and §9 of the check proves the consequence (all 2,083
declined artifacts byte-identical under the flag). Whether STEP 1's omission is
deliberate is not this lane's to decide; it is flagged.

**F7 — the ORIENTATION BLOCK is a sixth reader of the selection and the note
lists five.** §4.2 names the emitter's `if`, the stamp, the mirror and the two
stamp folds. The emitted "HOW THIS MATCHER WORKS" map's step 3 describes a
reverse scan, and a hybrid's "HALF 1" describes "a pair of table-driven
scanners"; both are false on a pinned artifact, and a map naming tables that
are not in the file is worse than no map. Both paragraphs now branch on the
same predicate the body did.

---

## 8. Open questions for Frank

1. **Should `-fno-scan-edge` join the `strategy_denials` mask?** F6 above.
   The mask's own stated rule ("it changes no answer, so two artifacts that
   behave identically must not differ in their reflection surface over it")
   covers `-fno-scan-edge` exactly, and the [OPT-4] comment records the
   measured harm of an omission. Not changed here — it is STEP 1's row, and
   moving it would put an unrelated artifact-byte change inside this abi bump.

2. **`docs/guide/` (`[GUIDE-1]`) is unbuilt**, so the D80 guide tier has no
   page for any of the seven optimization axes that have landed since it was
   chartered, not only this one. F4.

3. **C3's corpus population is zero** (§6 item 11). Every artifact the
   predicate accepts is `RX_DFA_MATCH "unwrapped"`, so the failing-call band
   the bench measured at ×37 and the pinned population do not intersect in the
   corpus at all. That is consistent with the note (the ×37 exhibit is
   `[OPT-VEDGE]`'s customer), but it means the C3 check's witnesses are
   necessarily synthetic, and it is worth knowing before the bench's AFTER is
   read against ledger §10.
