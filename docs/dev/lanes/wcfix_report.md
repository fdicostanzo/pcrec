# Lane wcfix — window_contract.md revision 3.1 (2026-10-16)

Brief: revise `docs/design/memfn/window_contract.md` from revision 3 to 3.1
against the light panel r4 (`docs/dev/reviews/2026-10-16-r4-window-contract-rev3.md`),
fold Frank's Q3 ruling (D167 add. 2: CONSULTED), and add the manager's
finding X1. Design-doc lane: nothing under `src/`, `cli/`, `lib/`, `tests/`
changed. Branch `lane/wcfix` from main `2288ad1cb`.

## Summary

- **B1 (blocker) discharged without the D80 route.** The panel's witness
  reproduces on main's binary (`window_contract_rev31/b1_witness.out`). The
  offer now derives through a NON-RAISING status derivation; the refusal stays
  on the ASK path; T-KIND gains `underivable-arrives` (PRESENT/PRIOR_NONE) and
  `underivable` (ABSENT); a new rule 9 refuses an underivable kind iff it is
  CONSULTED (by pcrec at the ask, by the kit at the art-end pass from B3b), so
  the refusal set is the same before E-1, after E-1 and after B3b. Census over
  the analysis axis (`analysiscount.out`): 1,905 / 3,246 / 5,367 utf8 compiles
  in the three deny arms succeed today with `""` under `l1none` and refuse when
  asked; those are G1-E1's new floors. The analysis axis moves no `""` count
  under `weblog`, `log` or a measured `-I` bundle.
- **M1-M5, m1-m6 all discharged; nothing rejected.** §R3.1 of the note maps
  each to its section; the review file's appended table does the same.
- **M3:** ONE render point after `mf_art_end` for `_FINDINGS`/`.findings =`
  and, at M0, `_MEASURES`/`.measures =`, byte positions kept through marks, as
  its own zero-mover commit RP before any OR (§3.7.3a). **Owed sibling edit
  (not made):** `measure_sets.md` §3.5/§4.2 (and §9.2 part 5's `ks_stamp` call
  site) need the same render-point sentence, beside F-4.
- **M2:** provenance from each block's own `provenance` stanza, with
  `bytes`/`fidelity` carried (evidence strength BUILT). This changes the
  manager's reading of D162 add. 3 for a user's authored block, so it is
  **Q5** (discussion, leaning content-sourced, link identity kept as a
  cross-check).
- **X1:** C-PERT, an independent perturbation check (same bundle name and stop,
  data held vs perturbed; reads only bytes and the stamp; null control and
  power floor; one perturber row per kind). The prototype on main
  (`perturb_proto.out`, 8 arms × 5,790 patterns): 0 null-control failures,
  power 1,161 (default byte) down to 263, and **exactly 2 FAILs**.
- **New finding F-5 → Q6:** the stamp reports only the FINAL attempt. Two
  corpus artifacts (`(\p{Xwd})x`, `x(\p{Xwd})y`, `-e utf8 -fno-req-byte`)
  stamp `""` while attempt 0 asked and the artifact depends on it (the
  quoted `_WHY` size even moves with the bundle name). Leaning: the union over
  attempts, its own small abi event beside RP; until then a named, floored
  C-PERT bucket selected by the fallback stamp.
- **F-6 (filed):** findings.md 3a¶3's "is refused at compile" reads two ways;
  the code refuses only when asked. A wording fix, not a contract change.
- **Sabotage:** S991-S998 kept (S992, S995, S996 updated); **S1027-S1034
  PROPOSED** for the manager to allocate (S1029 declared UNREACHED until B4).

## Open questions (for Frank, in the note's §12)

- **Q5:** provenance from the block's declared stanza (design of record,
  pending) vs the answering link (revision 3).
- **Q6:** what the stamp records for a multi-attempt compile (leaning: the
  union over attempts).
- Q4 (F-2's re-sourcing) stays the manager's; now latent.

## Evidence

`docs/design/memfn/window_contract_rev31/` (own CLAUDE.md): `b1_witness.sh/.out`,
`analysiscount.py/.out`, `perturb_proto.py/.out`. All compile-only counts on
main `2288ad1cb`'s binary, Linux dev box. No suite was run (design lane); no
validation is owed by this lane.
