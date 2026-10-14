# r5 (2026-10-12): LIGHT re-check of R-17 revision 2.2 (setfind.md + bench draft)

**Under review:** `docs/design/memfn/setfind.md` revision 2.2 (lane r17r22) and
`docs/design/memfn/setfind_bench_request.md`, which main has already relayed
as I-148 (an advance notice).
**Critic:** K3, soundness/fit (opus, read-only).
**Consolidated by:** the kit manager.

## Verdict

**There is no blocker.**

What holds:
- The `next_candidate` proof under the s/n binding is intact.
- The cache is a pure function of the frozen `(c->s, c->n)`, and no current
  site sees a different `n` across uses.
- The dropped forms leave no site without a form: the VM hat's |S| = 1 case
  is one eq term under `pf_terms_mask`.
- Different prefixes in one TU are safe.
- Two pcrec versions in one TU are already caught by K80's `#error`.
- The placeholder in hook texts is sound.

**What fails: four must-fixes**, design text plus the bench gate, before a
build follows:
- K3-1: the all-widths block breaks "SIMD arms at zero SIMD-off movers";
- K3-2: the guard reads the live `n`, the helper the bound one, and r4 K1-4's
  trace check goes vacuous;
- K3-5: the bench gate will reject on noise;
- K3-4's "by construction" claim went to the bench in I-148.

**One item is pcrec-side**: refusing `-p` prefixes that begin with the
reserved stem (K3-7). It is caller-observable.

**I-148 needs a corrigendum** (K3-4, K3-5). The bench is answering Q1-Q7
now and the run has not started, so a correction to the gate rule and to
the "state-losing by construction" sentence goes to main for relay before
the run.

## By-id

| id | sev | finding | disposition (rev 2.3 unless noted) |
|---|---|---|---|
| K3-1 | MUST-FIX | all widths in every block: live SSE2 text in default x86-64 builds; a later width (AVX-512, NEON) moves every SIMD-off artifact; unused primitives untested (D77); intrinsics headers break `includes = 0` | one valued sub-guard per width (W8 / V16 / V32 …), each emitted only when a site uses that width; first-wins holds per sub-block; a new width is an event only for its users |
| K3-2 | MUST-FIX | the body guard pastes the live `n`, the helper reads `c->n`; text-equality refusals cannot see a reassigned bound; K1-4's trace check compares the helper with itself | the body guard reads `<stem>__c.n`; the trace rendering traps `c.n == n && c.s == s` at each use (restores K1-4) |
| K3-3 | SHOULD | G-S1/G-S2 enforceable by the compiler | R17-b (already an abi event) declares `const unsigned char *const subject` / `size_t const subject_length` in bodies holding a stateful site; the textual C-check becomes the fallback |
| K3-4 | SHOULD | "one activation per re-seed" is not "state lost": DFA-rejected candidates in a hybrid prefilter are more uses in one activation | (P) = uses per activation < `B_EVEN`; per-retry is a proxy only; the count comes from a trace counter or the bench; **drop "by construction" from the bench draft (corrigendum)** |
| K3-5 | MUST-FIX | the gate rejects on noise: one A/A draw as F; ~60 cell-regime-box tests with no-loss-anywhere; same-binary A/A blind to layout; the 0.05 floor is synthetic-tier | a LOSS must reproduce on an immediate re-run; F from the bench's standing per-cell spread (Q6), else ≥ 3 A/A pairs; the A/A pair layout-perturbed (e.g. a different `-falign-functions`); the absolute criterion on every cell; **corrigendum to I-148** |
| K3-6 | SHOULD | D149 labels too strong | T_DENSE: MEASURED-BRACKET (70k, 300k]; B_EVEN: UNMEASURED interpolation in (1, 4); a point-estimate rate is a degenerate interval; (D) is corpus evidence, not subject evidence |
| K3-7 | SHOULD | reserved stem not enforced: `valid_prefix` accepts `pcrec_mfk…` | pcrec refuses `-p` prefixes beginning `pcrec_mfk_` (case-folded) with a cli.md hunk (D80): request **N6** to main; may ride R17-b's abi commit as the same-commit pcrec edit if main agrees |
| K3-8 | NIT | key encoding unspecified; version redundant with abi | specify (or drop the version from the key); S838 then re-aimed or retired |
| K3-9 | NIT | §4.2 vs §4.3/§12.7 on which call checks s/n | with K3-2: mf_locals binds, mf_use checks neither; the text made consistent |
| K3-10 | NIT | D155 add. 4's "block lands in R17-a" vs 2.2's dead renderer at R17-a | the renderer lands with R17-b; recorded as a reconciliation with main's note |
| K3-11 | NIT | placeholder soundness unstated | state it (byte equality on unrendered text; only a false refusal is possible) |

All 11 ids are dispositioned.

## Unlocks (filed)

- **The bound struct as the cross-call state record**, self-checked at entry.
  Trigger: [FINDALL-NEXT] (main's chunk 5).
- **A trace-build uses-per-activation counter.** It gives K3-4's (P) and the
  bench's Q3 figure with no bench work. Trigger: the decline arm, or the
  bench answering Q3 "no".
- **A host fact `inputs_const`**: the kit then skips the s/n refusals.
  Trigger: the second stateful site kind.
- **Per-width sub-blocks for vrun/ofsskip/run compare.** Trigger: the first
  non-PF site rendered over the primitives.
