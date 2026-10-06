# Requests to the kit — the pcrec manager → pcrec-memory-functions

PROTOCOL (D78; integration.md §20.1). ONE writer: the pcrec manager, as
a single-file commit prefixed `[requests]` on main. A pcrec lane that
needs kit work says so in its report and the manager files it here. The
kit never edits this file; it answers in `responses.md`. A request is
on main BEFORE the kit lane that serves it is briefed (the lane's
worktree is cut from a main that contains it). Items are numbered and
never deleted; a superseded item says so in place.

Each request names: the customer row; the measured cell that is its D77
trigger (or, for a measurement request, the decision it feeds); and the
SEMANTIC operation wanted — never an ISA or a kernel. Defects against a
kit choice (a G1 revisit-when event) are filed as `D-n` with their
timing transcript. Every measured answer reports BOTH layers, SIMD-off
and SIMD-on (D147).

---

## R-1 (2026-10-05, pcrec manager) — R4b: the first customer's measurement, the fused scan+verify on the post-handoff build

**Customer:** `[MEMFN]` R4c/R4d (integration.md §22) — K82 cause (B),
the DFA-route run pre-check gate on `union-select`, `userpass`, `mod-i`;
and K85 (`cls-n-uc`, set-leads on match-dense text), whose general
answers include the fused form.

**Kind:** MEASUREMENT ONLY (a probe; no kit code, no pcrec byte moves).
The probe code lives beside the original twin,
`docs/design/memfn/probes/twins/` (`tb_run.c`, `twins_run.sh`).

**Prerequisite / trigger:** `lane/k82hbuild` merged (main f116cff5, abi
61, the T3 handoff) — met. The manager confirms the handoff's alpha
acceptance before briefing the lane.
**Confirmed 2026-10-05 (pcrec manager):** the handoff's Linux alpha is
accepted (docs/dev/lanes/k82halpha_report.md, merged ad16111b): cause (B)
cured, DENY==BASE on every cell, answers identical. R-1 is clear to serve.

**The operation wanted (semantic):** FIND over the composite pre-check
predicate — a lead byte, a caseless masked RUN at its offset, and the
set rest — returning the leftmost candidate position, with the run
verified in the same pass ("lead + window in one pass"; integration.md
§15.5's composite site). The decision it feeds is R4d's trigger: does a
PORTABLE fused form beat the emitted gate?

**Variants (each computing the emitted gate's function exactly):**

1. `emit` — the post-handoff `-p rx` artifact's gate, copied verbatim
   from main at the run's pin (twins.md §3.1 copied 8a41efd2's,
   pre-handoff; that copy is now stale and is NOT the comparator).
2. `swar` — NEW: a fused pair-filter scan+verify in portable C (64-bit
   words, no ISA text, no intrinsics), the scalar-layer candidate.
3. `ffl` — the existing vector fused form, SSE2 and AVX2 builds (the
   SIMD-layer reading).
4. the scalar byte loop — the correctness reference (timed too, for
   scale).

**Cells:** twins.md T-B's three (`us`, `up`, `mi`) and K85's `cls-n-uc`
(its pattern and subject from the bench's published cell, read-only).

**Regimes (integration.md §21.1), both measured:**

- THROUGHPUT: find-all over subjects of at least 1 MiB, chained calls,
  hit-dense and hit-sparse (twins.md's `gate` and `sweep` at t-64k and
  t-1m);
- PER-CALL: one search per short subject, 16 B to 1 KiB (the 75
  capability short subjects).

**Protocol:** ubuntubudu, gcc 15.2 for verdicts (clang directional
only), `taskset`-pinned, quiet box, calibrated loops of at least
~50 ms, absolute deltas against a base-vs-base floor measured the same
way (D144 addendum 1). Correctness: every variant equals the byte-loop
reference on every subject and on a generated set (lengths 0..129, hit
at every offset, alignments 0..15), and a planted wrong variant is
shown to fail. Heavy Linux time goes through the manager (the executor
channel; one heavy suite at a time); the Mac run is directional.

**Report (in `responses.md` as `done:`, transcript archived under
`docs/design/memfn/probes/`):**

- per cell × regime: `emit`, `swar`, `ffl`-SSE2, `ffl`-AVX2, the floor;
- **SIMD-off reading:** `swar` vs `emit` (R4d's trigger: `swar` beats
  `emit` past the floor on at least one K82 cell in its own regime,
  with no loss past the floor in the other);
- **SIMD-on reading:** `ffl` vs `swar` — the SIMD layer against the
  current best scalar (D147), not against `emit`;
- K85's `cls-n-uc`: whether either fused form removes the dense-text
  loss, against `-fno-req-set-lead` as the off arm;
- anything that would change §15.5's composite site description.

---

## R-2 (2026-10-05, pcrec manager) — integration.md rev 4.5: fold R-1, then a light panel; Q53-Q55 recommendations

**Customer:** `[MEMFN]` R4a / R4a′ (integration.md §22). The wake brief's queue is: a light panel on rev 4.4, then Frank rules Q53-Q55, then R4a (the kit skeleton) and R4a′ (the stamp's abi event). R4a is NOT requested yet. It is filed as R-3 after Frank rules Q53-Q55.

**Kind:** DESIGN ONLY. No kit code, no pcrec byte moves.

**Trigger:** R-1 done (lane/memfn-r4b merged at main, report `docs/dev/lanes/memfnr4b_report.md` §9). It changes §15.5: lead order is part of the composite site's form, since userpass's run-first `swar` loses while lead-first `swlf` is null.

**Wanted:**
1. **Rev 4.5:** fold R-1's §9 findings into §15.5 and §22. That covers the lead order as a kit per-site choice, R4d's trigger as MET at SIMD-off (union-select), and the 16 B AVX2 short-path note for R4e′. Also fold D149 (decisions.md): every unroll width, block size and cut-over in a kit form is measured, derived, or left to the compiler, or labelled as an unmeasured default. The `swar` 2x unroll is the first label.
2. **A LIGHT PANEL on rev 4.5** (2 read-only critics, your skill §6). The lenses: the contract against pcrec's emitters at abi 61 (the handoff moved them since rev 4); and Q55's contradiction (MEMFN_FORMS `none`-iff-identical vs the plan being visible in the stamp at SIMD-off). Consolidate with a by-id completeness check in `docs/dev/reviews/YYYY-MM-DD-rN-memfn-rev45.md`.
3. **Q53-Q55:** each with options and a recommendation, written for Frank in plain text. I relay them to him.

**Deliverable:** a branch, the review file, and a `done:` naming the Q53-Q55 recommendations.

---

## R-3 (2026-10-05, pcrec manager) — R4a, the kit skeleton; then R4a′, the stamps' abi event

**Customer:** `[MEMFN]`, integration.md rev 4.6 §22 (R4a and R4a′ exactly as written there; this request adds only sequencing and the landing bar).

**Trigger:** Frank ruled Q53-Q55 on 2026-10-05 (D147 addendum 10). R4a moves no emitted byte, and the completeness migration is the ruled D77 exception (Q42). R4a′'s trigger is the same ruling.

**Two deliveries, in order, each its own branch and `done:`:**
1. **R4a: ZERO MOVERS.** It must keep these zero-mover:
   - `memfn/include/memfn.h`, the generic scalar row and the K1 reference functions;
   - `src/options.def` born empty, with `mf_options()`;
   - the Makefile wiring (libpcrec links the kit; nothing reaches an artifact);
   - `tests/memfn/site_manifest.tsv` with every site `pending` (N7 included, per Q54) and C17;
   - G2's first tests;
   - `PROVENANCE.md` with SPDX/provenance headers (C16) and C15's export check.

   Landing bar: the identity gate shows 0 movers (every artifact byte-identical to main), `make strict`, and the Mac `make test` on a slot I name. `docs/spec/` gets a hunk only if something caller-observable changes.
2. **R4a′: an ABI EVENT.** It adds `<PREFIX>_MEMFN_FORMS` (constant `none`, Q55) and `<PREFIX>_MEMFN_LIBC` (Q53, with its `nm -u` control) on EVERY artifact. Everything moves in the SAME commit:
   - the abi bump (the next number at landing; find its readers by grep, never a hand list);
   - the re-pins (byte-count readers included: m5_stage1_stamps.tsv, the resource pin, artifact_size_log.tsv, the recursion-identity sweep);
   - the D80 spec hunk;
   - `make test-codegen` plus the registry, codegen and rxtsource suites.

   Validation is the Linux `make test` through my executor channel, plus a mover census showing that every artifact moves by exactly the two stamp lines and the abi digit.

**Sequencing:** abi events serialize through the pcrec manager. START-SET (D148) has its own abi events coming at its stages 2-3. Tell me before R4a′ lands so the two don't collide; whichever lands second takes the next number.

---

## R-4 (2026-10-06, pcrec manager) — R4c, M1: the composite PRE site + the offset-skip trio migrate, zero movers

**Customer:** `[MEMFN]`, integration.md rev 4.6 §22 R4c exactly as written there (the `[rev4.3]` block's R4c row with its `[rev4.5]`/`[rev4.6]` marks: implement-then-replace, the `use` CEILING column + per-instance `req_use(cx)`, the REPLACE commit re-pointing every mech row anchored in a migrated emitter with the count stated, the `emit_req_handoff` split (S464 kit-side; S463/S470/S471/S472 pcrec-side), I2 reaching the VM hybrid handoff route with its witness, the inert `memfn-simd` pair in `strategy_denials`, `arms.tsv`, checks C4/C5/C10-C14/C17). This request adds only sequencing and the landing bar.

**Trigger:** completeness (Q42; a MIGRATION step). Prerequisites all MET: R4a′ on main (abi 63, 340d8fef); `lane/k82hbuild` merged; K85 re-measured (§R4.5.5 item 1).

**Sequencing (Frank, 2026-10-06, Q5):** R4c lands BEFORE main's unified start-table fold (docs/design/start_table.md, D151 addendum 1, steps C1-C7). Main's C0 (the `scripts/emit_sweep.py` extension; no `src/` change) runs in parallel with R4c. The fold's C1-C7 then re-derive their edit set on top of R4c. Cut the branch from a main that contains this request; if main moves under you, merge main ALONE in its own command, then `make strict`.

**The boundary this request must keep (D146/D147):** the migration moves the SEARCH TEXT of the offset-skip trio and the PRE site behind the kit; it does not move any start DECISION. Which row/site is selected, its admission (`src/opt/prefix_k.c`, `dfa_pfs[]`, the R/N/P predicates) and every BOUND/route read stay pcrec-side, untouched. Where a migrated emitter today also reads or restates a start decision, leave that read on pcrec's half of the split and NAME it in your report — main's fold edits exactly those lines next, and needs the list.

**Landing bar:** zero movers — the identity gate shows every artifact byte-identical to main over the corpus and every axis (I2 over both comment tiers); `make strict`; `make test-codegen` + the registry, codegen and rxtsource suites; the mech-row re-point count stated and [SABANCHOR] green; the Mac `make test` on a slot I name (Mac suite lock is main's lanes' — ask), then the Linux verdict through my executor channel (commit a pinned script; send path, wall time, completion line). No abi event expected (zero movers); if any byte moves, STOP and report — it is a defect, not a re-pin. `docs/spec/` gets a hunk only if something caller-observable changes.
