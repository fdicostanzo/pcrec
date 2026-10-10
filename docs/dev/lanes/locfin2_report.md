# Lane `locfin2` — report (D156 revision 2: the locate × finish panel applied)

Lane `locfin2` (opus, design), 2026-10-09, branch `lane/locfin2` from main
`7efca415` (`src/` identical to `525dec33`, abi 71). DESIGN ONLY: nothing under
`src/`, `cli/`, `lib/`, `tests/` or `docs/spec/`. Validation is COMPLETE for what the
lane owns (a compile-side census re-run with two new controls, and a derived
sabotage re-aim list); no long run is owed.

## Delivered

- `docs/design/locate_finish.md` — REVISION 2. A §R2 disposition table at the top
  with one row per panel id (G1-G14, C1-C12, E1-E12) and `[r2 <id>]` marks at every
  in-place edit; §0-§10 rewritten to the revised model; §7 files G13/G14 with
  triggers; §8 restates the questions for Frank.
- `docs/design/where_to_start.md` — §2.2 step 1 CORRECTED in place (`[r2 E1]`), plus
  the matching edits to the claim, §2.4's gate (new G4) and §3's prefilter bullet.
- `docs/design/revend.md` — §5.2 carries a supersession pointer to
  `locate_finish.md` §5.1 (`[r2 C6]`, "record the supersession in both notes").
- `studies/locate_finish/` — `census.py` (+ the `VM_RESEED` stamp), `analyze.py`
  (+ control C4, two-sided C3), re-run `results/rows.tsv.gz` + `summary.txt`
  (no existing table line moved); `l0_edit_set.tsv` and
  `results/l0_sabotage_anchors.{tsv,summary}` (the derived L0 re-aims). Own
  CLAUDE.md updated.
- `docs/design/start_table/sabotage_anchors.py` — ORDER gained `L0`/`L2`
  (byte-neutral for the C/B labels); its CLAUDE.md says so.
- Index entries: `docs/design/CLAUDE.md` (locate_finish rev 2, where_to_start's
  correction).
- Not touched (manager's): `plan.md`, `dev_journal.md`, `decisions.md`; pcrec-bench
  (read only, at `76e13c1d`).

## Validation (numbers)

- **Census re-run** (main `7efca415`, pcrec-bench `76e13c1d`): every existing table
  line byte-identical. New controls, all 0 disagreements:
  - C4 (classifier exact/superset vs the independent `RX_VM_RESEED "exact"`):
    759 / 0 / 0 / 734 over 1,493 hybrids; superset rows stamp adaptive 466,
    clamped 173, anchored 58, adaptive-dense 37.
  - C3 two-sided: forward 0 / 400 (+ width direction 262 agree, 138 declared
    probe-blind-call rows); converse 0 outside the two declared shipped declines
    (multibyte 22 rows / 16 distinct, `\G` 2).
- **Derived L0 re-aims** (`sabotage_anchors.py` with `l0_edit_set.tsv`, 31 entries,
  call graph regenerated at the pin): 6 re-aim (S566, S599, S606, S607, S608, S609),
  18 re-run at L0, 98 after L0; S222 a re-run, not a re-aim. 3 unresolved `src/`
  sites are the tool's pre-existing gap (S176, S640, S571), outside the family.
- Every code citation in §2-§5 was read at this pin; the pcrec-bench vocabularies
  (`adapter.py:699-701`, `:802-804`) were read at `76e13c1d`.

## Summary of revision 2 (for a resuming agent)

1. **Type:** a product `(I = [s,t], p, D)`; the FINISH key is its 5-valued shape
   (`NOMATCH`, `SPAN`, `ENDSET`, `LOWER`, `AT`). `CAND` = `LOWER` (G1, F-6
   withdrawn); `CT_WINDOW` deleted; `UPPER` = the interval's `t`. Superset ⇒
   `{LOWER, NOMATCH}` by a projection applied at the LOCATE → FINISH boundary,
   `cand_lang_exact(cx) = fit.chosen == ENGM_DFA || pcrec_vm_prefilter_window(cx)`
   (C1: no `Vm` needed; C4 controls it).
2. **FINISH:** four actions × two hats (G3); rows F1 nomatch, F2 report,
   F3 verify-anchored (= `dfa_matches[0]`, deny `-fno-anchored-dfa`),
   F4 verify-attempt (`ENDSET` only; taking `AT` would be the filed ATTEMPT
   match-here mover), F5 search-from (= `dfa_matches[1]`), F6 verify-vm, F7
   search-vm. `dfa_matches[]` FOLDS at L0 (G4); F-2 dissolves. Totality on
   (locator route, finisher route) via a triple table (C1, §2.3).
3. **LOCATE:** `empty`, `rev-end` (L2), `composite` (one row, hat by route, G8).
   Asked on `cand_locate_route` (C2: VM only with no DFA body). Relocate → the
   route's fallback row; progress = `(lo, rank)` lexicographic, self-check on
   succ cycles (G6 applied as A′: `s* = lo` happens, so the strict increase is the
   rank's; C2).
4. **Posture (G7):** `.giveup` deleted at L0 (F-1), `.contract = CG_FIXED` on the
   handoff; the classification is derived by a corpus instrument; the control is the
   give-up differential, a new row `[GIVEUP-DIFF]` before any VM-finisher LOCATE row.
5. **REVEND:** stage-1 conjunct reads `cand_finish_of` (G11); stage 2's deference is a
   `dominated` disjunct reading LOCATE, gated on `pcrec_artifact_has_dfa_scan`
   (G9/C11); F7-not-F6 hazard unwitnessed, sabotage witness `(\s+?){2}$` (E3).
   §4.5: reference's own fold (E4), union over `refs[]` (E5), lowered-set closure
   (E6), all Σ* sources gated incl. `A_VAR` and recursive calls (E7). rev-inner: G4
   or LOWER (E1), `\G` left on the caller's `search_from` (E8).
6. **Build:** L0 = G12's list (no mover; 6 derived re-aims; 6 new sabotage ids; an
   empty declared-unreached file for `run_cand_oracle.sh`). L2 = L2.0 machine
   membership `dfa_machines_of` (no mover, F-10), L2.1 D-2 `attempt-start`, L2.2
   `rev-end`; abi 71 → 72 once; pcrec-bench `[inbox]` adapter note + handshake (C7);
   `listing_declared_L2.tsv` (C12). Stamp rule §5.1: locator named once on
   `RX_DFA_SCAN`, REQ_WHY gains `"locator"`, machine-folded stamps read the emitted
   set; supersedes `revend.md` §5.2.

## Dispositions applied in a closest-sound version (A′)

- **G6**: "progress = strictly raised `lo`" is false for relocate when the leftmost
  match starts at `search_from` (`s* = lo`); the measure is `(lo, rank)`
  lexicographic, and every same-locator re-entry must raise `lo` strictly.
- **E1 (`${}`)**: a pattern variable names a caller value, never a group, so
  including `${...}` in G4 is conservative rather than necessary; kept.
- **C1 / F-3**: not data-only (as the panel said); applied as a boundary projection
  reading `pcrec_vm_prefilter_window`, which needs only a `Ctx`.
- **G12 vs `:10922`**: the third spelling of "does a DFA body exist" (`dfa_body` in
  `pcrec_emit_prologue`) is filed as F-9 rather than put in L0, to keep L0 to G12's
  list; `:10708` rides the orientation block's edit.

## New findings (not from the panel)

- F-9: "does a DFA body exist" is spelled three ways.
- F-10: the machine-membership rule is spelled four ways (three stamps + the
  orientation block); L2.0 unifies it.
- F-11: an ENG_ATTEMPT artifact's `_match` runs a whole search from `s` (search-filter);
  the fold makes the alternative a one-bit change (§8 Q7, `anchored_match_unwrapped.md`
  §10's open item).
- The spec defines `"unanchored"` as "the O(n) forward+reverse table pair"
  (`match_api.md#stamp-dfa-scan`): a machine-proxy reading in the contract itself, which
  L2's spec hunk must reword when `"rev-end"` is added.

## Questions for Frank (§8 of the note)

Q1 L0 first or folded into L2; Q2 stage 2 with stage 1; Q3 the stamp RULE (locator
named once, off-path ⇒ absence); Q4 the one-way spec sentence for W1 / VM PRESENCE;
Q5 the relaxed locator's own deny; Q6 rev-inner's reduced VM value after E1; Q7 the
ATTEMPT match-here form mover. Revision 1's Q1 (slot vs table) is struck (G4/G5).

## Next

The panel's verdict asks for a focused re-check by two critics (one with the
generality/unlocks lens) before any `src/` change.
