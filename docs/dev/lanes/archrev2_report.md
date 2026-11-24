# Lane archrev2: the kit architecture review note, rev 2 (answering review r91)

Tier opus. Documents only: no code, no make, no timing, no queue jobs. Branch lane/archrev2, cut from lane/memfn-arch
at 5af5d02d6. The note is `memfn/docs/arch_review_2026-11.md`, STATUS "DRAFT rev 2, for the r91 re-check". T stays
a0f13ad83a2432f14341831ba4d1ff68964b79d9: `git -C <worktree> diff a0f13ad83 HEAD --stat -- memfn/src memfn/include
memfn/tests src tests Makefile` prints nothing (note C-56).

## Summary

I am a fresh architect; I did not write rev 1. I revised the note to answer every finding F1-F20 of review r91
(`docs/dev/reviews/2026-11-24-r91-memfn-archrev.md`). I re-ran the critics' claims at T where they bore on a change, and
re-derived every count that rev 1 had built from a name list by SHAPE instead (C-9, C-16, C-19, C-34).

The largest changes:
- **ARV-9 (the window.c split) is re-sized from M to L.** Every section now has candidate homes (§8 H1). The note now
  says the split ADDS a private header, with up to 25 names for a two-file cut or up to 54 for a three-file cut
  (CEILING, C-39). It lists the binding checks that must move in the same commit: 58 mech rows, a redesign of
  run_purity_reach.sh, 50 census rows, 41 G2 plants, the rows_check plants, C15/C16 and PROVENANCE, and KITHDRS. It
  no longer claims to delete the presence<->window cycle.
- **New ARV-16 (the position primitives leave window.c).** A shape-derived edge census (C-9) shows every
  presence.c->window.c edge is a window.c primitive (4 names, 6 lines), and those primitives call only each other and
  `kit_mass` (C-59). Moving them out (S-M) deletes the cycle. Order: ARV-5, then ARV-16, then ARV-9. A8 now has a
  disposition: leave it, with triggers ARV-7 and ARV-9.
- **ARV-5** now widens the declared `kit_pos_*` family instead of adding a second one. k1_ref.c (G2's oracle) is
  excluded, the counts are recounted by shape (8 popcount loops), and the bindings are named.
- **ARV-6 and ARV-11** are now one per-level emission family. ARV-11 is D146 add. 1's facts/C split applied a third
  time. It covers `mfind_simd` as well, and it stops before the level-admission fact (that fact is R-48's).
- **ARV-8** is now M, harness, using registration on walk. ARV-10 is now M: the bit has three mechanisms, and the
  unit needs the Q-M1b-1 amendment, a spec amendment and the same-commit pcrec edit, and it serialises with
  [FLAG-DEMOTE]. ARV-12 is now L, riding the filed window_site.md R1 item and D162 add. 3; G2 is not a fixed control
  across it.
- **ARV-1 is split.** It now covers 3 one-site NOTED rows; the 8 second mechanisms become ARV-18
  (implement-then-replace rows). ARV-14 is now a family of three files with a NOTED row. Its trigger follows main's
  ruling R-1: a measured library-size or link cost, NOT "Q36 extraction".
- **New sections.** §8 "What the design step must decide" (H1-H11) holds every layout choice. The owner question
  window-file-split (§9) is re-posed with neutral options A/B, a real example (R-47's block span), the full records
  and the CONFIRM on "the kit split".
- **No ARV id was renumbered.** ARV-16, ARV-17 and ARV-18 are new; the id map is at the end of §7.

## Findings answered

| F | answered how | where |
|---|---|---|
| F1 | FIXED. Every window.c section is listed with candidate homes. The private header and its ceiling counts are stated (C-39: 25 for two files, 54 for three). A3 now reads "opaque outside the private header's includers". §9 no longer says "adds no API and no seam" | §2 A-s2, A13; §8 H1; C-38, C-39 |
| F2 | FIXED. ARV-9 no longer claims the cycle. ARV-16 deletes it; the shape census is C-9 and the primitives' callees are C-59. A8 has a disposition. One correction to F2: the cycle needs window.c's primitives moved OUT, not "most of presence.c" moved in (all 4 presence.c->window.c names are window.c primitives) | §2 A7, A8, A-s5, A8 disposition |
| F3 | FIXED. ARV-9 is L, no-mover + harness redesign, with 7 named binding checks and counts: 58 mech rows by section (C-40), the purity check's one-file population (C-43), 50 census rows (C-41), 41/8 G2 plants (C-42), S2983/S2988, C15/C16/PROVENANCE/KITHDRS | §2 A-s2; §7 |
| F4 | FIXED. A2 is reclassed SHARED ("holds for state, not for code"; C-57). Stated order: ARV-5, then ARV-16, then ARV-9 | §2 A2, goal 3; §7 order column |
| F5 | FIXED. (a) Neutral A/B options. (b) D201 add. 2 is quoted in full, with the kit's caveat, as NOT a ground (it concerned emitted code). (c) D185 add. 2026-11-17, the 11-04 end state (and main's R-1 reading of it) and ARCH-STEP (3) are cited. (d) The triggers are non-circular (a feature event); the "kit split" question is a CONFIRM, and [POS-ONE-DETECTOR] is named and not claimed. (e) Register row 9 is cited. (f) The example uses R-47's landed block span; NEON V is not placed | §9; §6 row 9 |
| F6 | FIXED. `kit_pos_class_of` is named, and the unit widens that family. k1_ref.c is excluded. The counts are recounted by shape (popcount 8; bit reads 13, of which 6 are helper bodies and 1 is the oracle, leaving 6 open). S3106, S3525 and 2 G2 plants are named | §3 B8, B-s1; C-19 |
| F7 | FIXED. The contract-gate field, `cl_denies`, the 10 FLD_denies cells and `rc_deny` are named. So are the levers and the predicate-level option reads (H5), the registry §6¶7 spec amendment, the same-commit memfn_sites.c edit, the Q-M1b-1 amendment, [FLAG-DEMOTE]/D195 and rows 3/15. It is an MF_SITE_ABI event, not a pcrec abi event | §3 B11; §5 D4, D-s3; §6 |
| F8 | FIXED. ARV-12 rides the filed window_site.md R1 item with its own triggers, which may have fired. It cites D162 add. 3, lists the 8 fields, names the G2/fixture writers (C-47) and the harness re-cut (L), and calls the emitting half a layer seam | §5 intro, D5, D-s4 |
| F9 | FIXED. ARV-6 and ARV-11 are one family with one event. `mfind_simd` is counted (4 tables). The (level, width) key is noted, the form is named (D146 add. 1), and the admission fact is excluded as R-48's. The layout is handed on (H4). S2996 and targets_check.c are named | §3 B5, B6, B-s2; §8 H4 |
| F10 | FIXED. Table S and `wf_support` are in B2 and §0. The fix is registration on walk, not a hand array, and the 4 enumerators go. The red readers are named (rows_zero, rows_check A, reach_equal.py, g2_parts); FLOOR_ROWS stays green. ARV-8 amends R5/V-3 and cites it; it is M | §3 B2, B3, B-s4 |
| F11 | FIXED. ARV-7 is now a pure leaf move (held) plus a register row for the order, naming gate.c:750, gate.c:911-913 and the entries as known violations. The carve-outs are H8 | §3 B-s3; §8 H8 |
| F12 | FIXED. The 11 EXC rows are split: 3 one-site NOTED rows (ARV-1) and 8 second mechanisms as open implement-then-replace rows (ARV-18). They are listed as goal-1 strains. The kind/status columns and the single home are stated | §2 goal 1, A-s1, A-s4; §6 |
| F13 | FIXED. Three caller classes (C-48): `mf_pres_ports` and `mf_finder_rows` are compile-path; `mf_reach`/`mf_lever` are test-facing through a compile; `mf_ref_*` and `mf_kernel_find_any` are added to the no-product-caller class | §5 D1, D-s2 |
| F14 | FIXED, with one change from the brief. ARV-14 is a family (formhash.c, k1_ref.c, vany.c) with a reason per member and a NOTED row. Its trigger follows rulings-file R-1, which REPLACES the brief's line: "a measured library-size or link cost", NOT "Q36 extraction". R-1 is cited in the note | §4 C3, C-s2; §6 |
| F15 | FIXED. The headroom is stated (11 and 25 bytes, limit 12288; C-50), and ARV-2 does not touch those two files. The home is memfn/include/NOTES.md (memfn/NOTES.md exists, but it belongs to the memfn/ directory). The 75 `memfn.h:N` cites (C-49) are re-cited by symbol, or ARV-4 lands after | §5 D2, D-s1; §7 ARV-2/ARV-4 |
| F16 | FIXED. Rows 3, 9, 14, 15 and 19 now have verdicts, and the search command is widened (C-34). Row 7b is "no drift" (C-35). A-PLAN, A-KIND and H-SITES are disposed against their Ride-along lines. Row 10 is joined by D-s5. ARV-5/6/7/8/10/16 now have proposed rows. R-48 is named in the ARV-6/11 event | §6 |
| F17 | FIXED. §8 "What the design step must decide" (H1-H11) now holds every file range, home, key, field and record. The section texts state the rule and hand the choice on | §8 |
| F18 | (a) FIXED: C8 and ARV-17 cover the 4 runners' pools (C-51). (b) FIXED: `wf_plan_class` is in A3 (C-5). (c) CLASSED: D11 reply structs and hooks, AS-IS, as [SEAM-READER-CENSUS]'s population (C-54). (d) CLASSED: B12 legacy bridge, AS-IS. It is `select_arm`'s 2nd and 3rd caller, not a second chain (C-53) | §4 C8; §2 A3; §5 D11; §3 B12 |
| F19 | FIXED. B1 now reads 9 calls over 8 tables (C-7). C-20c is widened. The "single set" quote is cited to journal.md:2976 and responses.md:3073 (C-58). ARV-15 is re-grounded (built ahead of need and never measured, so "keep the instrument" does not apply; its ground is the named event, or D197-style naming). The addenda quote now reads "measurement card". [SP1D-ARGMIN]'s trigger is quoted in full | §0, §2 A-s3, §3 B1/B10, §4 kit principles, header |
| F20 | FIXED. ARV-13's layout pools go to, or wait for, [LAYOUT-DRAW] | §4 C2, C-s1; §8 H10 |

Not mine, recorded as ruled: F21 goes to main (listed in §6 drift for the manager). RUL-13 was answered by main as
rulings-file R-1, which is applied. One place where the tree contradicts a finding: F2's remedy ("move most of
presence.c") is not needed. The C-9 shape census and the C-59 callees show the smaller move is enough. The note says
so, and F2's finding itself (ARV-9 does not delete the cycle) holds.

## Re-check scope

For a light arch round (r91's ruling: ARV-9, ARV-10, ARV-12 and the owner question, plus every re-sized ARV):
- ARV-9 (§2 A-s2, §8 H1): the section table and its candidate homes, the C-39 ceilings, and the binding-check counts
  (C-40..C-43).
- ARV-16 (new; §2 A-s5, A7, A8 disposition): does the C-9/C-59 claim hold that the move deletes the cycle, and are its
  bindings complete?
- ARV-10 (§5 D-s3, §3 B11): the three mechanisms, the spec-amendment reading of registry.md §6¶7, and the
  [FLAG-DEMOTE] serialisation.
- ARV-12 (§5 D-s4): riding the R1 filing, the "may have fired" reading, and the G2 re-cut claim.
- The owner question window-file-split (§9): neutrality, the records, the R-1 reading and the CONFIRM.
- The re-sized items: ARV-5 (B-s1), ARV-8 (B-s4), ARV-6/ARV-11 (B-s2), ARV-14 (C-s2, R-1 trigger), ARV-1/ARV-18 split
  (§6 kinds).
- §8 as a whole: does any layout choice remain outside it?

## STATE AT HANDOFF

- STATE: done. The note (rev 2), memfn/docs/CLAUDE.md's one-line entry, this report and the lanes history index are
  committed on lane/archrev2.
- Rulings file: `docs/dev/lanes/archrev2_rulings.md`, re-read before each commit and before this report. Last entry
  applied: R-1 (2026-11-24, main's ruling of RUL-13: Q36 not superseded; ARV-14 on its own trigger).
- Runs: greps and reads only, at T, on 2026-11-24. The scratch helpers (edges.sh, xcut.py, anchors.tsv) live under
  $PCREC_TMPDIR/scratch/archrev2/ and are reproduced inline in note §11 (C-9, C-39). OWED: none.
- Not done, by brief: no edit to architecture.md's register (its rows are PROPOSED in note §6), no edit to the r91
  review files, nothing under src/ or memfn/src.
