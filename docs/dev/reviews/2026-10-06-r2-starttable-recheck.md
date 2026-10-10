# 2026-10-06 — start_table.md revision 2: the short re-check, and its dispositions

**Subject:** `docs/design/start_table.md` revision 2 (lane `starttabrev`,
branch head `ae6cc89b`), against the light D6 panel
`2026-10-06-r-starttable-panel.md` (critics `…-crit-sound.md`,
`…-crit-checks.md`). This is §6 Q9's short re-check: the same two critics,
each against their own findings.

**Critics:** checks (sonnet), soundness (opus). Both read-only, main tree.
**Verdict, both:** **CLEARS with listed fixes.** No blocker; three majors
(C-N1, C-N2, S-N1).

**Applied by:** lane `starttabrev3` as revision 2.1 of the note (changes marked
`[r2.1 <id>]`, §R.1 of the note is the short form of this table). Every
finding is ACCEPTED. One (C-M2) is accepted with a measured nuance; nothing is
disputed. The instruments under `docs/design/start_table/` were changed and
re-run; the deny census itself was not re-run (no change to it requires that),
and two new runs were added (plain arms; a 1-in-10 all-flag sample).

| id | finding | disposition |
|---|---|---|
| C-N1 (MAJOR) | `sabotage_anchors.py` leaves 61 anchor sites with owner `?` (comment block, struct, `.def` row, header) classed OTHER; at least S282, S475, S479, S496, S299 are start-family rows silently dropped. Resolve leading-comment/struct sites, make an unresolved `src/` owner a hard error, print the count, re-derive 95/81/14 | **ACCEPT, fixed.** `call_graph.py` now parses types, sized/initializer/string data, object-like macros and headers (1,892 definitions; 1,392 before), never draws an edge to a type, and adds ROW TYPES to the family (a family table's element type and the types it embeds by value). `sabotage_anchors.py` resolves by def / factrow / datarow (family iff a decision SITE names the row) / lead (header comment) / filescope / outside; an unresolved `src/` site exits 2. Today 0 unresolved (def 440, outside 24, datarow 11, lead 3, factrow 1, filescope 1). Control: removing `DfaCand`'s def makes S282 unresolved and the script exits 2. Exactly the five named rows joined the family, nothing else: **100 family / 15 re-aim / 85 re-run** (was 95/14/81; the 15th re-aim is S490, from S-N2). Inventory 125/125 (eleven new members dispositioned, class TYPE added) |
| C-N2 (MAJOR) | The trace (§3.3 item 5) has no instrument: C0 must name the trace stream + diff tool, `-DPCREC_CAND_TRACE` through `build_from_rev` (`:344` runs plain make) on both sides, stderr capture, pattern-index+arm attachment, the C5b multiplicity filter, a records-per-arm floor, a failing-direction control and its sabotage row | **ACCEPT, fixed.** Verified `scripts/emit_sweep.py:344` runs `make -j4 CC=…` with no flag pass-through. C0's row now lists all seven items (i)-(vi) plus the full all-flag sweep; §3.3 item 5 points at it |
| C-M2 (PARTIAL) | Pin NOW the plain `-e utf8` and `-i` arms' DIFFER floors; with `-e utf8` dropped on both sides several deny floors still pass (run-prefilter 132 vs 3, start-set 136 vs 127, req-set-lead 14 vs 8); only the asserted 0 and the plain utf8 floor catch it — say so | **ACCEPT, measured** (`plain_arms.tsv`). `-e utf8`: whole bytes 3,188/3,221 (auto), 3,189/3,222 (vm), plus 74 refusal moves; START-stamp movers 674 / 341. `-i`: every artifact's bytes move (rx_info.flags), start-stamp movers 1,752 / 1,567 (byte), 1,775 / 1,605 (utf8). Both floors pinned per arm, because the whole-byte count is near-total and catches only an outright drop. **Nuance (measured, not a dispute):** 8 of 13 utf8 deny floors pass with `-e utf8` dropped; 4 more (`offset-skip` 513 vs 604, `req-handoff` 163 vs 280, `hyb-reseed` 403 vs 420, `req-run` 530 vs 572) happen to fail because utf8's population is the larger — an accident, not a control. The note says the design-level catches are the asserted 0 and the plain utf8 floors |
| C-N3 | Sweep the deny census over every `--list-axes` flag, report non-start-family movers, or make it C0's deliverable and measure the cost | **ACCEPT.** 1-in-10 sample (360 patterns) × 29 other flags × 4 arms: 43,200 compiles, 321 s at 6 jobs → full ≈ 54 min (6 jobs). Route-input flags move rows through the route; four flags move start stamps with NO route change: `-fno-length-prune` (bit 7, 11 `VM_RESEED` movers per auto arm in the sample, via `Vm.mrl_win`, R1's predicate input — **added to the deny arms**), `-fno-ctx-node` (6), `-fno-splice-calls` (10), `-fno-cls-kit` (1). The full sweep is C0's deliverable. Side finding below (F-2) |
| C-N4 | Reader list is src-only: `docs/dev/history/abi_changelog.md` (was `match_api.md line 2348`, `:2441`), `tuning.md:2530` name `dfa_pfs[]`; `run_sabotage_matrix.sh`, `tests/mech/CLAUDE.md`, `tests/codegen/CLAUDE.md` name retiring identifiers | **ACCEPT, fixed, by grep.** `reader_grep.sh` → `reader_grep.txt` (61 lines). Beyond the named ones it also finds `lib/CLAUDE.md:421`, `Makefile:517` (a comment), `tests/codegen/run_cand_rows.sh:3`, `tests/registry/axes_registry_check.sh:787`, `run_registry_tests.sh:601`, `studies/hyb_reseed_cal/README.md:33`. Spec readers ride C3's hunk; the rest ride the commit that retires each identifier |
| C-N5 | Re-run rows swept only once after C5b: run the subset owned by functions each commit touches, per commit | **ACCEPT, fixed.** `rerun_at` column: 32 re-run rows (34 sites) re-run in the commit that touches their owner (sites C3 12, C5 20, C5b 4); 53 once after C5b |
| C-N7 | §3.3 item 1 says "all five streams"; C0 adds a sixth | **ACCEPT, fixed** |
| C-(reconcile) | `inventory_check` reconciles only `inventory.tsv` vs the graph; method 2's movers and method 3's OTHER rows are reconciled in prose ("every hidden fingerprint is mapped") | **ACCEPT, made mechanical.** `reconcile.py` + `reconcile_map.tsv`: fails on an unmapped moved stamp key (10/10 mapped), an unmapped or ambiguous hidden fingerprint (5,192 movers over 5 members), a member not in `inventory.tsv`, an OTHER sabotage row naming a family identifier (0). Control: two map lines removed → exit 1 |
| S-N1 (MAJOR) (a) | Declaring `hands = LOWER` does not prove termination; replace with a per-row progress obligation checked at review; E11's landmark search must resume past the previous hit | **ACCEPT, fixed** (§1.6 "per-row PROGRESS obligation") |
| S-N1 (b) | E10 on an empty match: the strict advance is the caller's empty-match rule | **ACCEPT, fixed**, cited `match_api.md` §3.1.3 (was `:885`) |
| S-N1 (c) | E5's in-scan cycle missing from the termination list | **ACCEPT, fixed**; E5 marked re-entering, argument via `pf_emit_ofs` (`emit_dfa.c:6520-6524`) |
| S-N1 (d) | CAND's obligation gains `x ≥` the accepted LOWER | **ACCEPT, fixed**, satisfied today at `emit_vm.c:13280-13290` |
| S-N1 (e)/(f) | The structural type check is unevaluable: add HIT and START, name the non-slot successors, type PRESENCE's gate hit, fix E11 | **ACCEPT, fixed.** HIT (`litscan_k82h.md` §1.1a's contract) and START added; verifier / loop header / caller named as successors with `accepts`; E3 hands HIT; E11 re-typed (`LOWER` into NEXT's scan; FIRST is where `handoff-rev` is selected, not what it hands to) |
| S-N2 | §2.3 item 3's "the one dispatch" is false: ~14 `job->engine` tests | **ACCEPT, fixed.** Fifteen enumerated (the critic's fourteen plus the dispatch `:10271`); ONE `cand_route_of(cx)` added at C2, read by all fifteen from C3; fifteen `line` entries in the edit set. S490's anchor is one (re-aim at C3, which also carries sound-n5's re-verification) |
| S-N3 | Edit set misses R3's C5b line (`emit_vm.c:11090`) and m1's stamp/listing lines (`emit_dfa.c:10114`, `emit_vm.c:11558`, `emit_vm.c:9492` `st->`); S441 must be listed under C5 AND C5b; 463 vs ROWS 462 | **ACCEPT, fixed.** Lines added; the classifier collects every hit and lists S441 as C5+C5b. **Duplicate id CONFIRMED** (F-1 below) |
| S-N4 | "Three methods share no source" is false (method 3's family comes from `call_graph.txt`); optionally list OTHER rows whose anchors read a seed/field | **ACCEPT, fixed.** Restated as two independent derivations + a cross-record (§2.1, §5.2); the `reads` column lists every family/seed/field identifier an anchor names; 0 OTHER rows name one |
| S-N5 | §1.3(b) has no derived population | **ACCEPT, fixed.** `assert_reach.py` → `assert_reach.tsv`: 34 predicate roots, 13 reach an assertion, 8 sites in 5 definitions, +1 fact-layer site (`req.c:252`), +BOUND's body assertion `emit_dfa.c:9374-9382`; C5b's added reads reach none |
| both: Q1 | §6 Q1 is RULED (D151 addendum 1) | **ACCEPT, fixed** |
| sibling lens | File the POSITION-DOMAIN family as its own FILED-not-scheduled row; reference from §2.5/§5.4 | **ACCEPT.** `[DEC-POSDOM]` in `docs/dev/plan.md`; referenced in §2.5 and §5.4 |

## Findings the re-check produced (filed here)

- **F-1. Two sabotage rows share the id S169.**
  `tests/mech/sabotages/S169_root_minw_unchecked.sh` (H1's `root_minw` row,
  [DD-14.E], `1c822faf`) and `S169_postresolve_pass_deleted.sh` ([DD-14.LB],
  `e2f7c898`), both added 2026-08-24 by two lanes. Anything keyed on the id
  merges them (revision 2's "ROWS 462"). Owner: the mech suite; fix by
  renumbering one at the next free id on main (BOILERPLATE's "check the highest
  existing S-id ON MAIN"), with its `tests/mech/CLAUDE.md` references. Not done
  in this design lane (no `tests/` change). The start table's C5 re-aim names
  the FILE.
- **F-2. Bits 12 and 13 have the [AXES-DENY-MASK] shape.** On `(?:\Ga|b)c`
  (no atomic group, no call), `-fno-atomic-discharge` and `-fno-splice-calls`
  move only `rx_info`'s `.flags` (0 → 4096 / 8192), as `-fno-scan-edge` (bit
  21, already on lane flagbits' list) does. Cross-noted on the
  `[AXES-DENY-MASK]` row; passed to lane flagbits.
- **F-3. `-fno-length-prune` (bit 7) is a start-table input.** It reaches R1
  `exact` through `Vm.mrl_win` (a seed field) and moves `VM_RESEED` with no
  route change, so it joins the refactor's deny arms (§3.3 item 4); revision
  2's hand-picked 13 flags missed it, which is exactly what C-N3 asked to
  measure.
