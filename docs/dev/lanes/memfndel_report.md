# memfndel — [MEMFN] R1d revision 3: the DELEGATION model (2026-10-05, lane memfndel, opus, design only)

Branch `lane/memfndel` from main `90d396fd`. Deliverable:
`docs/design/memfn/integration.md` REVISION 3, on D146 (Frank,
2026-10-05). Read the note's §R3 first. Changed passages are marked
`[rev3]`; the new material is §8-§13. Nothing under `src/`, `cli/`,
`lib/` or `tests/` changed, no emitted byte moved, there is no abi event,
and no validation run applies (docs only). The only measurements taken
are greps at 90d396fd (the `memchr(` census, the runcmp and pre-check
caller lists, `PCREC_ARTIFACT_ABI` = 60). Every other number is cited
from linux_results.md, twins.md, `src/opt/prefix_k.c` or the r2 panel.

## Summary (resume from here)

1. **The contract (§8).** pcrec hands the kit (named
   **pcrec-memory-functions**) an `mf_site`: an op (FIND, SKIP, VERIFY,
   ALL_PRESENT) over a PREDICATE, a conjunction of position terms
   (byte sets and masked runs at offsets from the candidate), plus proven
   span, anchoring, per-term and per-predicate density hints, a `consumer`
   kind (named, never priced) and a policy word. The kit writes the code
   through TEXT hooks (subject, read limit, bounds, result + miss value,
   cursor/step/more, an optional ON_CAND verify ending in accept/reject
   tokens, T4's one-position `member` spelling, pcrec's table names).
   Eight hook rules, each with its check. Versioning: `MF_SITE_ABI`
   (layout), `MF_VOCAB` (ops; checked against pcrec's delegation table at
   build), `mf_kit_version()` (text). Totality: a kit decline is a kit
   defect, never a pcrec fallback.
2. **Compound work (§8.4)** is the predicate algebra (scan fused with
   verify = one FIND over a conjunction: T-B's shape), ALL_PRESENT
   ("check then check"), ON_CAND, RETURN-then-pcrec-text for the DFA
   handoff, and new shapes by request with an `MF_VOCAB` bump.
3. **What pcrec still decides (§8.5):** `DELEG_SITES` (delegable by op
   type: PF, PRE, OFS, SETREST, VERIFY, STAY, EDGE's loop, VMSPAN, MLINE;
   never T4, T8/T9, N7) and ONE first-match profile table: `baseline`
   (under `-fno-memfn-scan`/`-loop`: pcrec's own frozen pre-migration
   text, the guard's off arm), `portable` (under `-fno-memfn-native`,
   DEFAULT during the SIMD hold), `native`. The kit decides everything
   else with its own tables and data; the r2 measurement findings become
   its charter obligations K-1..K-5 (§8.6).
4. **Migration (§9).** The unit is an emitter function with ALL its
   callers. Each step is implement (kit baseline arm + a shadow
   comparator on every compile) then replace. Zero movers, so the
   delegation path is live code from the first step (dissolves r2 C-e's
   dead-stub problem). Order by customer: M1 OFS/PRE/SETREST/VERIFY
   (ofsskip blocks, runcmp.c entire, the pre-check, N4) for K82; M2 PF
   (+ §2.4 e's strcmp readers); M3 in-loop (only the scan edge's LOOP);
   M4 MLINE not taken (Q30); M5 prefix_k's scan PLAN (the derivation
   stays pcrec's; the five constants move behind a measured trigger,
   Q29). Identity gates I1-I5, including a `memchr(` ratchet born at 9.
5. **Guards (§10).** G1 = D146's kit on/off timing: alpha per mover step
   on Linux with long subjects and a population floor, and a
   `pcrec[memfn-off]` bench testee; G2 the kit's exhaustive tests; G3 the
   abi ritual for any kit byte move, detected by the standing identity
   gates, stamp on movers only; G4 C4 rebuilt (7 classes + 2 delegation
   classes, held-out plant, scopes incl. tests/); C5, C6, C9 cross-target
   syntax, C10, C11, C12; spec limits (gcc-measured, glibc/libSystem,
   compiler headers); ten deterministic sabotage rows.
6. **Coupling (§11).** In-tree `memfn/` first (decisive reason: a kit
   change and its pcrec abi bump must be one commit); extraction to
   `pcrec-memory-functions` needs a scope-mandate extension; 0BSD; a
   request ledger `memfn/docs/requests.md` now, D78's inbox/outbox pair at
   extraction.
7. **option_sets.md (§12.1)**: family `memfn` (`auto`/`simd`/`no-simd`/
   `memfn-off`) over three bits; `scalar` dissolves; `memfn-off` is likely
   §6.1's first trigger. The cross-note in option_sets.md is updated.
8. **Build order (§12.2)** R4a-R4j, each with prerequisite and trigger
   separated: R4b is the first customer's measurement (T-B re-run on
   Linux on the post-handoff build, with a PORTABLE/SWAR fused variant);
   R4c (M1) and R4d (first movers) fire on it; R4f is the native default
   flip as its own ruled event.
9. **r2 findings (§R3.2):** 23 rows; 11 carried, 7 moved inside the kit,
   3 dissolved, 2 split. Every measurement HIGH (P1, P3, P5) leaves
   pcrec; every artifact/check HIGH (K1, P9, B1) stays.
10. **Questions Q24-Q34 (§13)**, with §13.1 mapping Q12-Q23.

## Notes for the manager

- `lane/memfnk0r3` (the price-model rev 3, two WIP commits, unmerged) is
  SUPERSEDED by this lane. Its C4 census (code 1, src docs 1, tests 15
  in 10 files, at b7542fbe) is cited in §10.4 as unmerged and to be
  re-taken at build; its Q24-Q30 are declared void in §13.
- The K82 handoff (`lane/k82hbuild`) is cited as built and pending merge;
  R4b's trigger is its merge plus alpha.
- `docs/dev/plan.md`'s [MEMFN] row is not edited here; §12.2's quoted
  block is the paste text.
- Not done, by design: a light panel. The r2 pattern ("name the regime;
  name the independent control; name what moves when data is
  regenerated") is answered structurally: no regime at the boundary,
  G1's off arm pinned by pcrec's own gates, and every kit byte move an
  abi event.
