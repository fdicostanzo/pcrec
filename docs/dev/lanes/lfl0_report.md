# lfl0 — [OPT-REVEND] L0: LOCATE × FINISH, the path derivation, the `dfa_matches[]` fold

Lane lfl0, 2026-10-09, opus. Branch `lane/lfl0` off main `e1e387b9` (D156
addendum 1: L0, then REVEND). Design: `docs/design/locate_finish.md` rev 2.1
(§R2.1, §1.2-§1.5, §2, esp. §2.7, §3.4, §5 L0); review
`docs/dev/reviews/2026-10-09-r-locfin-panel.md`; conventions from
`docs/design/start_table.md` (refactor A).

**Status.** Built and committed; a NO-MOVER (no emitted byte, stamp or
listing byte moves; no abi event). Light gates green (§4). New sabotage ids:
REQUESTED, NOT YET ASSIGNED at the time of writing (§3.2): the ten rows are
drafted and validated by plant under placeholder ids. The heavy chain is
OWED (§6).

## 1. What landed, per commit

| commit | what |
|---|---|
| `f9291130` | L0.1: the LOCATE and FINISH slots, LOCATE's rows `empty`/`composite`, §2.7's path derivation, every listed reader re-pointed |
| `76eea9c3` | L0.2: the `dfa_matches[]` fold into FINISH (`verify-at`, `search-from`), the `CT_*` hand keying, the NEEDS half, the `match` listing projection, the oracle's take cells, the F-2 grep row |
| `17ff5a30` | L0.3: `.giveup` deleted, `.contract = CG_FIXED`, the erasure record `Nfa.erased`, the boundary projection at `Vm.mrl_win` |
| `9820a2c5` | L0 follow-up: the VM-only LOCATE ask on CR_VM, the VM entry's seek cell, the census PATH instrument (C5-L0, C6, C7), the four re-anchored rows |
| `9afe18f7` | the spec hunk (LR-S10), the BOUNDARY oracle witnesses, inventory, edit set, CLAUDE.md files |
| `fd4b1f7b` | L0.2 follow-up: `dfa_match_of` counts its hit before its record (so a planted hand-less ask aborts on the check, not on a NULL row) |
| `0cec4a15` | `scripts/emit_sweep.py`'s trace records floors re-pinned for L0 (§4.1); the build-tip sabotage derivation committed |
| (this report's commit) | the ten new sabotage rows, this report, the lanes index entry |

The three planned commits are the first three; the follow-ups are separate
commits rather than rewritten history (no interactive rebase here). Each of
the three was swept on its own (§4.1).

### L0.1 — slots, LOCATE rows, the path derivation

- `CandSlot` (core/internal.h) gains `CAND_SLOT_LOCATE` (first) and
  `CAND_SLOT_FINISH` (last); `CAND_M*` names the machines (F R A ATT VM).
- LOCATE rows (`cand_rows[]` head): `empty` (A1; predicate
  `locate_empty_applies` = the old `dfa_engine_is_empty` body, printing the
  same `ROUTE ... engine-empty` record; walk `emit_empty_unanchored` /
  `emit_empty_attempt`, the old early exits moved out of the two emitters
  byte-for-byte, the ATTEMPT one after the shared front `attempt_entry`) and
  `composite` (A3, `cand_always`, all routes; walk `emit_unanchored` /
  `emit_attempt` by route, NULL on CR_VM). `pcrec_emit_dfa_engine` asks
  LOCATE (`cand_locate_emit`, record site `locate`) and writes the row's walk.
  `dfa_engine_is_empty` = "LOCATE selected the static NOMATCH row".
- §2.7: `CandRow.needs[route]` (`CandNeeds`: `mach`, `cells`, a LOCATE
  row's entry `front`), declared on LOCATE, RECOVER (`reverse-pass` needs R)
  and FINISH rows only. `cand_path_of` = the closure from three roots (the
  search entry's LOCATE ask on `cand_locate_route`; on a VM finisher the VM
  search entry = `search-from`'s VM hat plus RETRY where a prefilter exists;
  on a DFA finisher the match-here entry's FINISH ask), selecting ONLY in
  LOCATE / RECOVER / FINISH through the readers the emitters already use (so
  it evaluates no predicate the emitters do not), recording every other asked
  cell without a walk; MEMBERS = needs ∩ built. Quiet in the trace build.
  Not memoized (a deviation from §2.7's "memoized per compile"): it is three
  selections per reader, each the one its old reader made, and a memo would
  need invalidating across `compile_driver`'s retries.
- Readers re-pointed (§2.7's table): `dfa_table_name`,
  `dfa_scan_edge_name`, `dfa_uniform_folds` fold over the members (LR-S1);
  the orientation block reads `cand_finish_of`, the body bit and RECOVER
  where asked; `pcrec_artifact_has_dfa_scan` IS the body bit and
  `compile.c:2381`'s build gate and `:10922`'s `dfa_body` read it;
  `req_handoff_applies` (`:7355`) reads "F or ATT is a member"; P4
  (`:7895`) reads `cand_recover_asked`; `dfa_scan_name` reads the LOCATE
  row's `u.locate.scan[route]`; the eleven `fit.chosen` FINISH reads read
  `cand_finish_of`. (`compile.c:229`, the NEEDS half, moved to L0.2: it reads
  FINISH rows, which land there.)
- `cand_nodes`: LOCATE and FINISH nodes; per-edge progress classes
  (`raise`/`rank`/`entry`: RETRY→NEXT/VERIFIER and VERIFIER→NEXT and
  CALLER→LOCATE `raise`, FINISH→RETRY `raise`, FINISH→LOCATE `rank` (E-FL)
  and `entry` (E-FC)); `CT_WINDOW` deleted. Self-check additions:
  progress-not-an-edge, progress-cycle (graph minus `raise` acyclic),
  progress-rank, needs-unwalked, needs-unrouted, needs-unasked; the trace
  build asserts `needs ⊆ built` (`path-needs-unbuilt`).
- Trace build: `CANDPATH <finish> <locate> <members> <asks> [<erased>
  <old>]` once per emission; `CANDROW` gains a `kind` (ask/read) and a FINISH
  `hand` field (nobody else reads CANDROW beyond fields 1 and 4).

### L0.2 — the `dfa_matches[]` fold

- FINISH rows `verify-at` (FIN3: CR_DFA, take `AT`, needs A, availability
  `finish_verify_at_applies` = `anchored_ok`; listed `match` 1 `unwrapped`
  with `fact_deny` = `PCREC_NO_ANCHORED_DFA`) and `search-from` (FIN4: all
  routes; take `AT`, `NOMATCH` on CR_DFA/CR_ATTEMPT, none on CR_VM until
  L3; needs the LOCATE cell, and on CR_VM the VM entry's cells). The descs
  moved verbatim from `axes_dump.c:135-136`.
- `CandSel.hand` (mandatory on a FINISH ask) and `.point`; `cand_select`
  keeps a FINISH row only where `cand_takes` (the hand is one of its take
  masks on the route; `AT` only on a point ask). `dfa_match_of` asks with the
  meet `caller ⊓ body` (`NOMATCH` on an `empty` body, LR-G8): the old
  `!dfa_engine_is_empty` conjunct is gone. `dfa_match_is_unwrapped` reads
  `u.finish.act` (F-2). `DfaMatch`, `dfa_matches[]`,
  `match_unwrapped_applies`, `pcrec_dfa_axis_match_cands` and the match arm
  of `axes_dump.c`'s `stamp_macro_of` are deleted; the `match` axis lists
  through `emit_cand_axis`. `-fno-anchored-dfa` has ONE reader,
  `compile.c:230`; `compile.c:229` reads the NEEDS half
  (`pcrec_cand_finish_needs(cx, CAND_MA)`).
- Self-check: FINISH totality per hand on each asked route (the last row
  taking `AT`/`NOMATCH` undeniable and available by construction), a take
  cell on an unrouted route; the trace build aborts a FINISH ask with no
  hand (`finish-no-hand`).
- `tests/codegen/run_cand_oracle.sh`: witnesses for the four new rows; every
  FINISH take cell read off the source must be reached (`CANDROW FINISH`
  row/route/hand) or listed in the new `cand_oracle_unreached.tsv` (EMPTY at
  L0); a stale or undeclared allowance cell fails (validated both ways).
- `tests/codegen/cand_rows_check.py` `[cand-no-row-pointer]`: F-2's revert
  as a grep row (no compare against `&cand_rows[...]`, no `dfa_matches`).

### L0.3 — data corrections, the erasure record, the boundary

- `.giveup` deleted (no reader; F-1's zero default gone); `.contract =
  CG_FIXED` on `handoff` and RETRY `exact`, `clamped`, `retry-anchored`
  (LR-S11); `CG_*` is now `{CG_ANY = 0, CG_FIXED}`.
- `Nfa.erased` (`NFA_ERASED_LOOK/ATOMIC/COUNT`), reset per build, written
  by the `A_LOOK`, `A_ATOMIC` and count-collapse arms of `src/ir/nfa.c`.
  `pcrec_vm_prefilter_window` = `fit.prefilter && !nfa.erased`;
  `RX_VM_PREFILTER_LANG` reads the COUNT member (F-13 stays filed).
- `Vm.mrl_win = pcrec_cand_lang_exact(cx)` (finisher not VM, or the window)
  at its one assignment, with the record `BOUNDARY vm <SPAN|LOWER>` on a
  hybrid; the entry, RETRY recompute and adaptive re-seed read the field.
- `run_cand_oracle.sh [cand-oracle-boundary]`: `(a+)b` must record SPAN,
  `\w{1,2}(?:(?=)|)$` and `(?>a|ab)c(d)` LOWER.

### The follow-up (`9820a2c5`)

- The trace-vs-asks control (§4.3) found that no EMITTER asked LOCATE on
  CR_VM (808 VM-only artifacts): `pcrec_cand_locate_vm` (called by
  `pcrec_emit_vm` when there is no DFA body) is that ask, emitting nothing
  (LR-S6: the `(\w+)\1` witness's LOCATE ask). And that the VM entry asks
  NEXT on CR_VM (its seek): added to the VM entry's cells.

## 2. Sabotage: the re-aims and the re-runs

### 2.1 Derivation

At my base `e1e387b9`, `sabotage_anchors.py` with rev 2.1's edit set
reproduces the plan: **8 re-aim (S140 S494 S566 S599 S606 S607 S608
S609)**, 35 rows / 36 sites re-run at L0, 78 sites after. I appended the
seven lines the build changed beyond the plan to
`studies/locate_finish/l0_edit_set.tsv` (the orientation block's three
`prefilter` lines, the `RX_VM_PREFILTER_LANG` line the plan's set missed,
the dispatch line, `match_unwrapped_applies`' body line, the `CT_WINDOW`
enumerator line) and derived again with the ACTUAL diff:

    python3 -I docs/design/start_table/sabotage_anchors.py <base tree> \
        <call graph at base> studies/locate_finish/l0_edit_set.tsv \
        --repo . --step L0=e1e387b9..HEAD --final after-L0

Result: **RE-AIM 8, the same eight**; **55 rows re-run at L0** (54 by hunk,
1 by reach; the plan's 35 plus the rows the real diff reaches, e.g. the
`src/ir/nfa.c` rows); **75 sites after L0** (S88, S141, S222, S264 among
them); 3 pre-existing unresolved sites (S176, S571, S640), so the tool exits
2 as it does on main. `m6read_check_sab_anchors.py`: after the re-anchors,
589 rows / 607 sites, all resolve.

### 2.2 The eight re-aims

| row | what moved | re-aim | mech (in-lane, HEAD `9820a2c5`) |
|---|---|---|---|
| S140 | `pcrec_vm_prefilter_window` reads the erasure record, not the kinds conjuncts | the READER ignores the record's look member (`!(erased & ~NFA_ERASED_LOOK)`); the WRITER half is new row (9) | DETECTED |
| S494 | `pcrec_artifact_has_dfa_scan` is the path's body bit (body text unchanged) | anchor unchanged; intent re-verified | DETECTED |
| S566 | `emit_unanchored`'s run-block line reads `cand_finish_of` | anchor text updated | DETECTED |
| S599 | the `ceiling` row lost `.giveup` | anchor text updated | DETECTED |
| S606 | `cand_nodes` rewritten (new nodes, progress fields) | anchor unchanged; re-verified | DETECTED |
| S607 | same | anchor unchanged; re-verified | DETECTED |
| S608 | same | anchor unchanged; re-verified | DETECTED |
| S609 | RETRY's node gained `.raise` after its reads | anchor ends at `},` | DETECTED |

Each: `bash tests/mech/run_sabotage_matrix.sh <id>` →
`== mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0, unreached: 0,
anomalies: 0, oracle-skipped: 0)`.

### 2.3 New rows (ten, per §5 L0)

Each was planted on a `git archive HEAD` scratch tree through
`tests/mech/lib/replace.py` (the mech applier), built default + trace, and
run against its detector by hand; each row's `SAB_REACH` passes on the clean
tree. Each row's `SAB_SUITES` names ONLY the detectors measured red here.

| id | the plant (§5 L0 item) | suites | measured at landing |
|---|---|---|---|
| ID1 | (1) LOCATE order swapped: `empty` moved after `composite` | candoracle | `table-not-total LOCATE`, 59 oracle checks fail |
| ID2 | (2) `cand_finish_of` misderives a hybrid as a DFA finisher (reads the body bit) | harness (`tests/lookaround/prefilter.rxt`) | 34 of 53 cases fail |
| ID3 | (3) the match-here FINISH ask passes hand 0 | candoracle codegen | `finish-no-hand FINISH`, 29 checks fail; the default build crashes on every DFA compile |
| ID4 | (4) FIN3/FIN4 order swapped | candoracle | `table-listing-order`, 59 checks fail |
| ID5 | (5) the boundary projection dropped (`pcrec_cand_lang_exact` ignores the erasures) | candoracle harness | 7 oracle checks (two `[cand-oracle-boundary]` cells read SPAN; five RETRY witnesses unreached); 6 of 53 harness cases |
| ID6 | (6) RETRY -> NEXT loses its `raise` class | candoracle | `table-progress-cycle NEXT`, 59 checks fail |
| ID7 | (7) `dfa_table_name`'s anchored member re-keyed to the FINISH selection | candoracle codegen | `no-row FINISH` on every hybrid witness, 27 checks; default build `(a+)b` exits 139 |
| ID8 | (8) `reverse-pass` loses its `needs` (R) | codegen | `run_dfa_uniform_fold.sh` 250 corpus disagreements, `run_premul_table.sh` 2, `run_search_pinned.sh` 480, `run_form_census.sh` 1; census C5-L0 3,656 |
| ID9 | (9) the `A_LOOK` arm stops recording its erasure (the WRITER; S140 is the READER) | harness (`tests/lookaround/prefilter.rxt`) | 6 of 53 cases fail; census C7 478 |
| ID10 | (10) the meet dropped (the match-here entry asks `AT` on an `empty` body) | anchoredmatch | `\B\b` stamps `unwrapped`, 4 checks fail |

The F-2 revert is NOT a row (note §5 L0): it is
`cand_rows_check.py [cand-no-row-pointer]`, run by `make test-codegen`.

## 3. Open items

### 3.1 Deviations from the note (each with its reason)

1. The path is NOT memoized (§1, L0.1).
2. `compile.c:229` (the NEEDS half) landed in L0.2, not L0.1: it reads
   FINISH rows, which L0.2 creates.
3. LOCATE has an explicit VM-route ask (`pcrec_cand_locate_vm`), found
   necessary by the trace-vs-asks control; the note implied one (§2.2's
   "an artifact with NO DFA body, once, on CR_VM") but no edit-set line
   placed it.
4. The VM search entry's cells include NEXT (its seek): the note's §2.7 root
   2 lists WINDOW, PRESENCE, WIDTH, FIRST, BOUND and RETRY.
5. `empty`'s front on CR_DFA is EMPTY, not PRESENCE (§2.7 says "`empty` and
   `rev-end` PRESENCE only"): today's empty DFA body asks no entry slot; the
   REQ stamps' PRESENCE/FIRST asks on it are DECLARED stamp-only asks.
6. The spec hunk also fixes `docs/spec/tuning.md:3822`, which repeated the
   same false sentence.

### 3.2 Sabotage ids

Requested 10 from the manager at lane start; no reply yet when this was
written. Drafted rows are validated by plant (§2.3 when filled).

## 4. Validation

### 4.1 Emit sweeps (`scripts/emit_sweep.py`, reference `git archive e1e387b9`)

| tip | streams | arms | result |
|---|---|---|---|
| L0.1 `f9291130` | c-default, c-vm, emit-ir, composition, facts, dumps; self-check passed | 32 start arms × 2 | **0 movers**, 0 asymmetric (`build/scratch/sw1.log`) |
| L0.2 `76eea9c3` | same six (dumps = `--list-axes` + six more, byte-identical) | 32 × 2 | **0 movers** |
| L0.3 `17ff5a30` | ALL streams (incl. emit-ir-auto, stderr); self-check passed | 32 × 2 | **0 movers** |
| L0.3 `17ff5a30` `-fno-anchored-dfa` (byte) | c-default, c-vm, emit-ir, facts | the arm (differ 1,806 / 1,806 both sides) | **0 movers** |
| final `9afe18f7` | ALL streams (c-default, c-vm, emit-ir, facts, the four emit-ir-auto arms, stderr, composition, dumps); self-check passed | 32 × 2 | **0 movers**, 0 asymmetric |
| final `9afe18f7` `-fno-anchored-dfa` | byte: c-default, c-vm, emit-ir, facts; utf8: c-default, c-vm, facts | the arm, both bases | **0 movers** |
| final `9afe18f7` `--variant all` | every stream, five limit variants × byte/utf8 | — | **0 movers, 0 asymmetric in every cell**; rc 1 from PRE-EXISTING floors (below) |

**The trace (C1 selection trace, `--trace` with
`studies/locate_finish/trace_declared_L0.txt`).** The SET gate is CLEAN at
the final tip (rc 0 after the re-pin). The declared sites `locate`,
`finish-match` and `boundary` filter 19,750 working-side records, and all 25
C1 site keys are reached. The ordered compare is a diagnostic and does not
gate; it differs on 4,196 sequences by order and multiplicity only.

The pinned records floor tripped on the first run, so `0cec4a15` re-pins
`TRACE_RECORDS_FLOOR` and `TRACE_VARIANT_RECORDS_FLOOR`:
- **c-default fell.** It went 335,067 → 270,131, because the membership
  folds read the quiet path derivation and no longer re-print
  RECOVER/ROUTE records. Every record still prints from its emitter or its
  stamp.
- **c-vm rose.** It went 120,691 → 125,687, from the VM-only LOCATE ask and
  BOUNDARY.
- **Measurement.** Every variant was measured with `--variant all --bases
  byte --trace`, and all five SET gates were clean.
- **Pinning rule.** Each arm pins min(base, tip), because the floor binds
  both sides.

**Pre-existing, not L0's.** Running `--variant all` on main itself shows
`lowsize`/`lowboth` reach and tag floors violated identically on side a
(main `e1e387b9`) and side b. For example, c-vm reaches 4,941 < 4,943, and
`yes-collapsed` reads 21 < 25. Every such cell has 0 movers and 0
asymmetric. Those pins are stale on main. I did not re-pin them: they are
not L0's, and some other change moved them.

### 4.2 Listing

`--list-axes` byte-identical to the base (stream 5 at every commit; spot
`diff` at L0.2). No declared listing file: L0 adds no listing row (the
`locate` axis is L2's).

### 4.3 Census controls (C1-C5 re-run, plus L0's three)

`studies/locate_finish/census.py` with `PCREC_TRACE` (the lane's trace
build), both populations (5,798 rows, 5,355 compiled), then `analyze.py`:
C1-C5 unchanged at 0 disagreements; **C5-L0 0 / 5,355** (the derivation's
members vs `rx_forward_`/`rx_reverse_`/`rx_anchored_` text; hybrids FRV
1,231, TV 244, V 18 included); **C6 5,355 / 5,355 agree** (the emitters'
`CANDROW ... ask` cells vs `CANDPATH`'s asks, entry slots route-free, six
declared stamp-only shapes in `asks_declared_L0.tsv`, each used: NEXT@vm on
DFA artifacts 3,052; RECOVER@attempt 572; RECOVER and NEXT on empty bodies
71; PRESENCE and FIRST on empty DFA artifacts 53); **C7 0 / 1,495 hybrids**
(erased empty 761 = old exact 761; A 213, C 6, L 478, LA 36, LC 1 all
inexact under both). Failing direction, each by plant on a scratch tree:
`reverse-pass` loses R → C5-L0 3,656 disagreements; composite's DFA cells
lose NEXT → C6 3,902; `A_LOOK` stops recording → C7 478.

### 4.4 Light gates

| gate | result |
|---|---|
| `make` / `make strict` / trace build `-Werror -Wall -Wextra` | clean |
| `make test-codegen` | green, 15/15 groups, on the final tree |
| `run_cand_oracle.sh` (trace build) | 64 passed, 0 failed (witnesses, coverage, 5 take cells, 3 boundary witnesses); the allowance validated in both failing directions |
| `run_cand_rows.sh` | 4/0 |
| `m6read_check_sab_anchors.py` | 589 rows / 607 sites resolve |
| `inventory_check.py` (call graph at the tip) | 166/166 |

## 5. Spec hunks (exact text, for whichever of specclean/lfl0 lands second)

`docs/spec/match_api.md` (was line 4732), the `RX_DFA_SCAN` paragraph:

    -are `"unanchored"` (the O(n) forward+reverse table pair, D7), `"attempt"`
    +are `"unanchored"` (the O(n) forward scan from `search_from`, D7, followed by a
    +reverse pass that recovers the match start unless `RX_DFA_START` is
    +`"pinned"`), `"attempt"`

`docs/spec/tuning.md` (was line 3822):

    -- `RX_DFA_SCAN` is `"unanchored"` (the O(n) forward+reverse table pair),
    +- `RX_DFA_SCAN` is `"unanchored"` (the O(n) forward scan, followed by a
    +  reverse pass that recovers the match start unless `RX_DFA_START` is
    +  `"pinned"`),

## 6. The heavy chain (OWED)

PLACEHOLDER.
