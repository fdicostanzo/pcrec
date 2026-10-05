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
