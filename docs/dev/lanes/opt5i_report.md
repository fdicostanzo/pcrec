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
| `2100caa` | untrack `opt5i_rulings.md` — its own header says never commit it |
| `d155de7` | the `RX_DFA_START` value-set pair in the axis registry check; the report |
| `df372fb` | **manager ruling R1**: `<PREFIX>_VM_FRAMELESS` rides this abi bump |
| `b9f7690` | the axes-registry coverage guard, 88 → 93, read from a run |




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

### 4.3 Manager ruling R1 — `<PREFIX>_VM_FRAMELESS`

Landed on this abi event rather than taking one of its own, per the ruling.
`docs/dev/optvmfl_step0.md` §4.1-§4.4 is the proposal; nothing in it conflicts
with this lane's charter, so it did not have to be done last.

| the ruling asked for | delivered |
|---|---|
| a §6.3 (b)-family macro, VM route only, UNCONDITIONAL, not on a pure DFA artifact | `src/gen/emit_vm.c`, beside `_VM_RUNGS`. Both values spelled; §2 of the check asserts the DFA-side absence |
| value read from `has_push` at the stamp's own site — the SAME bool the fail label reads, one derivation, two readers; NOT recomputed from `v.npush` | the `const bool has_push = v.emitted_push \|\| v.has_linked_calls;` declaration MOVED UP to sit beside the stamp; the fail label now reads that one variable |
| no `rx_info` mirror | none |
| the `match_api.md` §6.3 entry with its IFF | landed, with the IFF verbatim |
| the `tuning.md` line if §4.2 names one | **§4.2 names none, and none was invented.** That file's §3 is the DFA side's own stamps; the VM's (b) family is documented in `match_api.md` §6.3 and has no `tuning.md` section to join, because there is no flag |
| a `tests/codegen` structural check: every VM/hybrid artifact defines it; 1 ⇔ no `goto *`; 0 ⇔ it does; corpus + `-fprefilter` force axis | `tests/codegen/run_vm_frameless.sh`, `make test-vm-frameless`, **6 / 0**. Default axis: 1,492 VM artifacts (583 frameless / 909 pushing). Force axis: 1,266 VM (495 / 771). Both sides floored at 100 on each axis |
| it rides the abi 15→16 bump and (B) re-pin, no separate bump | the `emit_dfa.c` abi comment, the `run_codegen_tests.sh` ledger sentence and `match_api.md`'s abi paragraph all name it |

**Its first run found a trap worth carrying forward, and it is finding F8
below**: the `goto *` count must be SCOPED to the VM program's own function.

### 4.4 Suite results

| gate | result |
|---|---|
| `make -j4` | clean |
| `make strict` | clean — "whole tree compiles clean with `-Werror -Wshadow`" |
| `make test-search-pinned` | **16 / 0** |
| `bash tests/harness/run.sh` on the two new `.rxt` files | **112 / 0** |
| `scripts/m6read_check_sab_anchors.py` | 218 sabotages, 230 anchor sites, all resolve |
| `make test` | four sections red for four NON-DEFECT causes, all re-derived (§6a); all four re-run **GREEN** — resource 30/0, anchored-match 15/0 + 7/0, lookaround 5/0 + 11/0 |
| `make test-codegen` | **109/0, 31/0, 22/0, 32/0, 7/0** |
| `make test-registry` | **0 failed** (the axes coverage guard moved 88 → 93, read from a run) |
| `make test-premul-table` | **16 / 0** |
| `make test-axes` | **`-fno-start-pinned` 22309/22309 agree, 0 mismatches; five pre-existing AXIS FAILs on main's own cells, reproduced with main's compiler, filed by the manager as K45** (§4.5, finding F12) |

### 4.5 `make test-axes` — the row's primary control

**`-fno-start-pinned` (bit 22): OK.**

```
keys_base=22309 keys_axis=22309 agree=22309 budget=0
refused=0 lost=0 gained=0 mismatches=0 refused_doc=0 refused_undoc=0   175s
```

Every one of 22,309 corpus cases answers IDENTICALLY under the denied build,
whose match start comes from an independently built reverse automaton. That
is the row's whole answer-identity claim, proven corpus-wide, and it is the
one number in this report that could not have been produced by any structural
check.

**The run as a whole FAILS, on five axes that have nothing to do with this
row, and I did not paper over it.** `-fno-counter` (6), `-fprefilter` (9),
`-fno-altcls-merge` (10), `-fno-size-term` (18) and `--engine=dfa` (§2.11)
each report `refused_undoc=2` and **`mismatches=0`**. All five point at the
same two cells, `tests/size/size_term.rxt:34` and `:35`.

**They are PRE-EXISTING, and that is measured rather than argued.** The
pattern is `[ART-SIZE.2]`'s nested-repeat tower
`(?:(?:(?:(?:(?:(?:a|b){41}){41}){41}){41}){41}){41}`, last touched at
`fa9b6d4`, reachable from this lane's branch point;
`git diff 5496ca6..HEAD -- tests/size/` is empty. A compiler built from
`5496ca6` by `git archive` produces the IDENTICAL refusal message under all
five flags, and `run_axes.sh` run with `AXES="-fno-altcls-merge"` against THAT
compiler reproduces both AXIS FAIL lines verbatim, including "this axis has NO
documented refusal population at all".

**The controlled re-run is byte-for-byte identical.** `run_axes.sh` with
`AXES="--engine=dfa -fno-altcls-merge"` and `PCREC` pointed at the
`5496ca6` build, on this same corpus:

| axis | MAIN's compiler | this lane's compiler |
|---|---|---|
| `-fno-altcls-merge` | FAIL agree=22307 refused=2 mismatches=0 refused_undoc=2 | **identical** |
| `--engine=vm` | OK agree=22299 budget=10 mismatches=0 | **identical** |
| `--engine=dfa` | FAIL agree=12826 refused=9483 mismatches=0 refused_doc=9481 refused_undoc=2 | **identical** |

Not one figure moves. The mechanism is the block's own design: it carries
`engine vm` precisely
because forcing the VM skips the NFA build — its own comment records that it
was "found by writing the cell without it and watching it fail for the wrong
reason" — and `RXTFLAGS` layering an engine or a denial on top defeats that,
so the NFA is built and explodes.

**Not fixed in this lane, and that is the manager's ruling rather than my
preference.** The repair is either an axis-documented-limit entry for the
nested-replication family or an axis exclusion on that block, and both are
decisions about ANOTHER row's witness inside this row's abi bump. **Filed as
K45**; the tower's axis documentation belongs to `[ART-SIZE.2]`'s row and
lands as a separate item after this merge. Carried as finding **F12** below.

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
| 9 | `N_hybrid_pinned` under the FORCE axis | **70** with captures on, **23** under the check's own `--no-captures` flags. M1's `0` was a DEFAULT-axis number and the note was right to refuse it as a population. The force axis is now a second arm of the corpus sweep, floored |
| 10 | the P3 EVALUATION count (not the decline count), both axes | **ZERO, on all three axes** — default, `-fprefilter`, `--no-captures`. P3 is never ASKED: every machine reaching the seed gate needs no seed, and every seed-needing machine is refused earlier. S219's UNREACHED is now measured, not only derived |
| 11 | `N_pinned ∩ search-filter` over the corpus | **0.** All 175 pinned artifacts stamp `RX_DFA_MATCH "unwrapped"`. C3's corpus population is EMPTY; its three named members (`[a-z]{0,4096}`, `{0,8192}`, `{0,16384}`) are out-of-corpus witnesses, which is what §6 of the check drives and asserts the membership of |
| 12 | the `startpos > 0` population over the 175 | **5 patterns, 14 cells** (`x*` 5, `a*` 4, `(?>a?)` 2, `(?:ab)?+` 2, `\Q\E` 1). Both of §5.6d's acceptable discharges taken: counted here, and 112 synthetic cells built (`tests/base/start_pinned_startpos.rxt` + its seeded sibling) |
| 13 | S220's disjointness from S218 | **They are NOT disjoint — they are a defence-in-depth pair, and NEITHER has a failing direction alone.** Measured by planting each half, rebuilding, and sweeping: P1 widened alone → 224 pinned (the clean figure) and the check 17/0; P2 dropped alone → 224 and 17/0; BOTH → 243, 19 artifacts flip, the check RED in three places including a real ANSWER divergence. S218 became a two-hunk row; S220 ships declared UNDETECTED |
| 5 | artifact-size movement, predicted then compared | **DONE**, §5 above |

---

## 6a. The four IN-TREE CHECKS the elision moved

`make test` found four sections red. **None was a defect in the emitter**;
each check's own message asked for a deliberate re-derivation naming the
cause, and that is what landed.

| section | cause | disposition |
|---|---|---|
| `test-lookaround` (11) | my `tests/assertions/start_pinned_startpos.rxt` joined `run_expansion_diff.sh`'s pinned population | re-pinned: +1 block / +16 cells on the totals AND the qualifying counts, +1 per policy pattern and lookaround count, **0** on the six disqualification counts and the two identity counts. The arithmetic is the evidence; a delta that moved a disqualification count would be a different event |
| `test-resource` (4) | the three size-cap witnesses lost ~HALF their bytes and stopped reaching the cap | row 1 becomes `(?:[a-z][0-9]){1,8000}` — the old witness MINUS ONE CHARACTER, non-nullable, therefore DECLINED, therefore still refusing at the default with no flag. Rows 2-3 keep the classic witnesses under `-fno-start-pinned`, as STEP 1 kept them under `-fno-scan-edge`. The `[OPT-4.1]` cell gets the same flag or goes vacuous |
| `test-premul-table` (1) | `implied_stamp` demanded a reverse table on a pinned artifact — 178 artifacts read as drift while the emitter was right | the fold now runs over the machines PRESENT. The absence is read from MATCHER TEXT, never from `RX_DFA_START`, and a reverse table missing while a `rewind_position` REMAINS is still a drift |
| `test-anchored-match` (1) | my own corpus file's `[a-z]{0,4096}` exceeds `PCREC_ANCHORED_MAX_STATES` and moved [ENG-ABS]'s overflow population 0 → 1 | REMOVED from the corpus file. That check says "do not simply re-pin this line", a startpos file has no business moving an unrelated census, and `[a-z]{0,64}` makes the identical claim |

**MEASURED, and worth carrying**: each size-cap witness lost very close to
HALF its bytes — 1,063,395 → 537,224; 1,103,670 → 557,311; 1,333,410 →
683,524. On those shapes the reverse machine WAS half the artifact.

**NAMED so the next reader does not re-derive it**: for the
`(?:[a-z][0-9]){0,n}` family, SCALING THE COUNT no longer reaches the byte
cap at all. n=10,000 → 669,228; n=12,000 → 481,228 (the table crosses the
65,535-entry bound and the accept table stops being class-replicated);
n=14,000 → 561,228; and by n=22,000 the DFA state cap fires first and
[SEL-1] retries onto the VM at 20,229 bytes. That is why row 1 changes
SHAPE rather than COUNT.

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

**F8 — a whole-file `goto *` count is not a VM fact on the default or force
axis, and `[DD-14-RECURSION rule 1]` is right only because it forces
`--engine=vm`.** `run_vm_frameless.sh`'s first run reported 199 artifacts
stamping `RX_VM_FRAMELESS 1` while "the artifact contains 6 `goto *`". Every
one was correct: an `ENG_ATTEMPT` DFA scan's STEP IS A COMPUTED GOTO
(`goto *<p>_targets_K[class]`), and a hybrid inlines one. MEASURED on
`(?m)^(a|b)$`: six `goto *`, all inside `static int rx_prefilter(...)`, none
inside the VM program. Rule 1 avoids this by compiling under `--engine=vm`,
which turns the prefilter off (D44/R21 E-6) — a property of ITS axis, not of
the count. The check now scopes to the program's own function and says so.

**F9 — two of my own `RX_VM_FRAMELESS` witnesses were wrong, and the file
records why rather than swapping them quietly.** `(a|b)(?1)(?1)` was chosen as
a LINKED-call row and is nothing of the kind: `altcls` merges `(a|b)` to a
class before any engine exists, and wave G then SPLICES both call sites
(`RX_VM_CALL_SPLICED 2`, `_LINKED 0`), so the artifact is genuinely frameless.
A row needing a linked call needs a target in a CYCLE. And
`foo[0-9]+bar -fprefilter` is REFUSED rather than compiled: the pattern is
capture-free, so it is a pure DFA artifact and `-fprefilter` is do-or-die.

**F12 — `make test-axes` was ALREADY RED on main, on five axes, and the row's
own axis is clean.** `-fno-start-pinned` reports 22,309 of 22,309 cases
agreeing with 0 mismatches. Five OTHER axes — `-fno-counter`, `-fprefilter`,
`-fno-altcls-merge`, `-fno-size-term`, `--engine=dfa` — each report
`refused_undoc=2` with `mismatches=0`, all pointing at
`tests/size/size_term.rxt:34-35`, `[ART-SIZE.2]`'s nested `{41}` tower
(`fa9b6d4`, 2026-08-29, untouched by this lane). Reproduced with a compiler
built from `5496ca6`: every figure identical, including both AXIS FAIL lines
verbatim. **`make test-axes` is opt-in and not part of the union battery**,
which is how a pre-existing red there survived unnoticed. Filed by the
manager as **K45**, and NOT repaired in this lane by ruling.

**F10 — the note's §3.4(a) is wrong about reachability: the widened bit is
not a miscompile on its own.** F3/§3.4(a) presents the `state_acc_any`
widening as "the sharpest miscompile available here", with a discriminating
population of 16. MEASURED: planting exactly that widening changes NOTHING —
224 pinned artifacts, the same 224 the clean tree gives, and
`run_search_pinned.sh` 17/0. `state_acc_any` ORs over the CLASS-CONTEXT
views, not the position views, so the two spellings of P1 disagree only on a
state whose accept varies by class context — and P2 refuses exactly those.
Meanwhile the `(?m)…$` family fails P1 in BOTH spellings, because its start
state accepts only under the EOL VIEW, which `state_acc_any` does not see.
M2's 16 artifacts are a fact about `unanch_start`'s PREFILTER gate, which has
no P2 beside it; they are not this predicate's discriminating population.

**F11 — P1, P2 and P3 are not three independent guards on this corpus; they
are one guard with two spares.** Instrumented sweep, 2,850 patterns: P1
refuses 1,705, P2 refuses exactly THREE (`\B`, `\B\B`, `\Bx*`), 224 pass
both and need no seed, and P3 is asked ZERO times on every axis. The three
P2-refused artifacts are all seed-needing, so removing P2 at the start state
only lets them reach P3 — whose per-seed loop applies P1 and P2 again and
refuses them there. That is why S220 is inert at one hunk AND at two.
**This does not make P2 or P3 removable**: both defend against machine shapes
the corpus does not contain, which is what the compiler assertion and the
declared-UNREACHED rows are for. It does mean the note's §5.6 table
overstates what a single-hunk plant can show.

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
