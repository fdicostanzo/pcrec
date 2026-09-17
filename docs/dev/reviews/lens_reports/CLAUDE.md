# docs/dev/reviews/lens_reports/ — the code-review lens deliverables

One report per lens of the 2026-09-17 code review, chartered by
`../code_review_criteria_draft.md` (RATIFIED by Frank the same day). Each is a
read-only lane's own voice, delivered against `main` at `7d444f9e`; the
manager's synthesis (`../YYYY-MM-DD-code-review.md`) dedupes findings across
lenses and ranks them per A4. Historical once the synthesis lands.

**Entries are written to be self-contained** — the lenses run in parallel on
separate branches and the manager merges, so each lane adds only its own rows.

- `lens10_emission_kit_charter.md` — **lens 10, emission-kit unification: the
  WAVE 1 CHARTER** (lane `lens10kit`, opus, review + measurement). Chartered
  from lens 2's mechanism map to be precise enough to brief implementation
  lanes from; delivers the kit API, a five-stage plan with per-stage anchor
  populations / abi verdicts / byte-neutrality proofs / rollback shapes, and
  the risk list. **Its first job was the D77 measurement lens 2 named and
  deliberately did not build, and the answer closes the template layer rather
  than deferring it: the population is 1**, and that one run performs zero
  prefix substitutions.
  Read it for three findings that change the charter rather than confirm it.
  **(1) The metric measured a shape the code had already eliminated** — the
  emitters write contiguous literal blocks as ONE `sb_printf` with a multi-line
  concatenated format, so counting *calls in a row* finds 1 of the **28**
  single-call blocks spanning ≥5 source lines (largest: 369 lines / 8,884
  emitted bytes at `emit_dfa.c:681`); *a proxy metric that counts the symptom
  of a shape goes stale the moment somebody fixes the symptom by hand, and then
  reports the underlying population as absent.* **(2) L2-3's 652 is not what it
  counts** — the `grep -o '%s_'` reproduces exactly, but positional pairing
  shows **306 of 584 (52.4%)** bind the prefix and the rest bind the
  *uppercased* prefix (139), a machine name, a tag or a function name; and
  **460 of 771 calls are MIXED**, holding 49,749 of 77,258 literal bytes, which
  `pcrec_enc_emit_text` structurally cannot reach. **(3) The fragment layer's
  correctness payoff is LATENT and lens 2's acceptance number would pass before
  the wave ran** — **zero** of the 43 `snprintf`-into-a-literal-sized-buffer
  sites can provably truncate at a legal 60-byte `-p` prefix (tightest margin:
  **9 bytes**), which is the K35 shape, so the charter supplies a completeness
  criterion instead.
  Also worth reading for two A3 corrections and one instrument finding: **261
  sabotage rows are 277 ANCHORS** (16 rows carry a second, each independently
  re-aimable), of which **123 are in the two emitters** and only **4** quote the
  fragment idiom directly — not the 24 lens 2 reports, which conflated
  text-call anchors with fragment anchors; the source-text-reading check list
  is **7** `src/gen/` readers, not 5, headed by `run_cpset_structure.sh` at 24
  reads; and **the tree's only long-prefix control compiles the pattern `a`**
  (`tests/cli/run_cli_tests.sh` case 3), a trivial DFA artifact reaching
  essentially none of `emit_vm.c`'s 40 literal-sized buffers — the
  [MECH-REACH] shape, filed independent of whether wave 1 ever runs, and the
  reason the charter inserts a **stage 0** (a long-prefix full-corpus sweep)
  as a precondition rather than a cleanup.
  Its §2.4 judges the brief's own claim that retiring the buffers answers lens
  3's F6: true for L2-1, but for F6 it **DISSOLVES** the question rather than
  answering it — a distinction a lane brief must keep, or it will produce a
  lane that thinks it has audited something it has only deleted.
  Evidence and reproduction: `lens10_evidence/` (own CLAUDE.md).

Maintenance: one row per lens report; add yours without editing anyone else's.
