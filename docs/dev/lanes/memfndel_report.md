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

---

# Revision 4 (lane memfndel4, 2026-10-05, opus, design only)

Branch `lane/memfndel4`, cut from main `1c2ba975`. Deliverable: integration.md
REVISION 4, applying the r3 light panel
(`docs/dev/reviews/2026-10-05-r3-memfn-delegation.md`). That panel found no
blocker and 27 findings, all accepted. Changed passages in §8-§13 are marked
`[rev4]`, and the new material is §R4 and §14-§23.

Nothing under `src/`, `cli/`, `lib/` or `tests/` changed, no emitted byte
moved, there is no abi event, and no validation run applies (docs only). Every
line cite was re-checked by grep at `1c2ba975`. The handoff was read on
`lane/k82hbuild` `9bb97c7c` (abi 61). `docs/design/option_sets.md`'s
cross-note and both CLAUDE.md indexes are updated.

## Summary (resume from here)

1. **§R4** names the seven standing rulings honoured (Q3's every-artifact
   stamp, D144 item 4's denies, D146 no arch/no pricing, the abi ritual,
   measured-not-tuned, D145, D78) and maps all 27 findings to sections.
2. **§14, the contract from the emitters' shapes.**
   - Three site FORMS: EXPR inside pcrec's `if (guard && …)`, STMT at
     `indent`, and FUNC (a file-scope definition plus `mf_call`).
   - ASSIGN and ON_MISS handoffs, with pcrec's `on_miss` statement
     (`return 0;`, `break;`). A miss is a value or pcrec's statement, never
     the kit's control flow.
   - Notes (pcrec's fact comments) and pcrec's escapers through the sink.
   - ADVANCE's counter with a cap-reached contract, plus `peek`.
   - Ranges `[lo, n − end_back)` that never wrap, with EMPTY declared as
     MISS, NOP or EXCLUDED.
   - Negative offsets under a `floor`.
   - REQUIRED/OPTIONAL terms: `c` is at most the true leftmost, and every
     REQUIRED term holds at `c`. The K82 soundness argument survives this.
   - ALL_PRESENT with `ret_pred`.
   - A `use` column (DISCARD/POSITION).
   - Totality through a generic scalar row tested over a generated space;
     a new shape's baseline is that row, and is UNREACHED for G1.
   - Shape bounds are `_Static_assert`ed against `limits.def`.
   - `on_cand` must be duplicable (C13).
   - Per-artifact `mf_art`: helpers before first use (DFA before the block,
     VM via the prologue flush), the includes subset assert, and
     `RUN_WORDS` written by the kit through the sink.
   - `plan_hint` is permanent until M5 moves prefix_k's MODEL into the kit
     as the baseline's frozen planner.
   - The fate of every shipped deny (only bit 43 crosses, and at M1b). The
     three profile bits join `strategy_denials`. The kit's switches become
     generated axes.
3. **§15** reproduces every M1 site shape byte for byte from the emitters'
   format strings: the offset-skip FUNC, its calls, the one-byte gate, N4's
   block, the K82 composite gate, and the run compare (M1b, shown for the
   contract). It sketches PF, STAY, the scan edge and `(?m)^` (§15.7).
4. **§16, M1 narrowed** to the composite PRE site plus the offset-skip trio.
   runcmp is reached through a `run_cmp` hook and becomes M1b. M1 is
   sequenced after `lane/k82hbuild` merges and after K85's re-measure.
   After migration, edits to those emitters are kit-lane work.
5. **§17 guards.**
   - I2 runs over every `axes.def` axis and both comment tiers, with a floor
     on the number of arms.
   - G1's population comes from a pcrec-side default-vs-`memfn-off` diff,
     with pooled bins (floor 8), a declared regime and a cadence of every
     memfn abi event. armv8 is stated to have no verdict guard.
   - C9 gets a header shim, runs at `-fmemfn-native`, and has a committed
     arm floor.
   - Per-arm and per-pattern pins live under `tests/memfn/pins/`.
   - C4's plant claim is narrowed.
   - 14 mech-runnable sabotage rows, each with `SAB_REACH`.
6. **§18, the stamp.** `<PREFIX>_MEMFN_FORMS` goes on every artifact,
   `none` iff the artifact is byte-identical to its memfn-off compile, with
   no kit version. C11 checks it against a pcrec-side diff. It is born in
   its own abi event R4a′, before M1's replace, with k82h §2.3a's reader
   classes.
7. **§19** lists 12 pricing sites with fates: the prefix_k model and the
   window/byte/position picks (M5); set-leads (now composite order);
   dominated-by's rarity half (M2); runcmp's lengths (M1b); k82b
   (withdrawn). The reseed calibration, the cand ppm and the admission floor
   stay as facts, engine choices or ruled bounds.
8. **§20.** Two inbox files from day one. `memfn-native` is a deny/force
   pair, default OFF. `MF_NS` gives `pcrec_mf_*` symbols, checked by C15.
   Per-file SPDX and provenance, checked by C16.
9. **§21** answers the three standing questions (all relevant): the declared
   two-regime pair, a control table, and a regeneration table.
10. **§22** gives the build order: R4a, R4a′ (stamp), R4b-R4d, R4e/R4e′
    (native behind the opt-in, which breaks R4f's circularity), R4f, M1b,
    R4g-R4j, plus the plan-row paste text. **§23** holds Q35-Q49, mapped
    from Q24-Q34.

## Notes for the manager

- `docs/dev/plan.md`'s [MEMFN] row is not edited. §22's quoted block is the
  paste text.
- One answer departs from the panel's offered options. For F9, neither
  "pcrec computes `plan_hint` forever" nor "M5 re-pins the baseline": the
  MODEL moves into the kit as the baseline's planner, byte-identical. Q40
  asks the open part (adoption, and `RX_DFA_PREFILTER`'s meaning).
- M1 now excludes runcmp (G-F11's narrowing), so bit 43's crossing and the
  VM callers wait for M1b's own trigger. If you prefer rev 3's wider M1,
  §16's table says exactly what re-joins.
- Not done, by design: a panel on rev 4. §15's byte-for-byte claims are
  read off format strings. The build's I1 shadow comparator is what proves
  them over the corpus.
