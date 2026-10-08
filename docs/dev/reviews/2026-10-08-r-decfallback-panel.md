# 2026-10-08 — light D6 panel on docs/design/dec_fallback.md rev 1 (refactor B)

Two read-only critics: critB1 (opus, soundness/semantics) and critB2 (sonnet, checks/instruments). Recorded by the manager from the hand-backs. Dispositions are at the end.

## critB2 — CHECKS / INSTRUMENTS

**Verdict:** the re-aim list is complete at region level, and the attempt histogram is mostly independent. One BLOCKING gate hole (B4); the rest are MAJOR gaps in reach, refusals and sabotage.

### BLOCKING
- **B1. T2's listing half has no byte gate where its rows fire.**
  - emit_sweep stream 3 always runs `--emit-ir --engine=vm`, where `would_prefilter` is false. So T2 rows 3-7 (`yes`, `yes-collapsed`, `no-nullable-exact`, `no-nullable-collapsed`, `no-dfa-overflow`) never print there.
  - Probed: `(a*)*` is `no-nullable-exact` at auto and `no-engine-vm` at vm.
  - decfb0 never counted listing tokens. The both-derivations oracle shares predicates with its subject.
  - Fix:
    - a B0 stream `emit-ir-auto`: stdout + rc incl. refusals, over 4 variants plus the arms `-fno-prefilter` / `-fprefilter` / `-fno-prefilter-collapse`, floored per listing token per variant;
    - adopt and extend tests/prefilter/run_prefilter_tests.sh's hand-written `check_ir_value` rows to every T2 row and scope.

### MAJOR
- **M1. Refusals are not compared.** emit_sweep only counts `both_refuse`. B3 rewrites the exhaustion diagnostic and which cap is named (compile.c:2303-2307). Fix: stream 7 = the full stderr + rc of every compile, with refusal floors per variant.
- **M2. Population mismatch.**
  - decfb0 runs 4,792 `--list-source` blocks with their own encoding/features. The streams use byte + `--features all`.
  - The shipped-limit size-rung witnesses are utf8 (`-e utf8 '(\p{Xwd})'`).
  - Fix:
    - re-measure every floor in emit_sweep's own population, with a `-e utf8` base per variant;
    - the histogram runs in a separate driver over decfb0's population;
    - freeze the case list, or gate parent-vs-child (pinned absolute counts rot).
- **M3. No per-row reach instrument** (A had row_census/assert_reach). Zero or near-zero witnesses:
  - T1 `nomem`: only S259 via the alloc injector. Put `make alloc` in the B3 gate.
  - The collapse -> sel1-collapse(-> drop) sequence: in no variant.
  - T2 row 5 at CR_SIZECAP scope: new sabotage #3 ships UNREACHED.
  - `-fno-prefilter`: in no arm list; it is row 8 and row 6's subtle clause, and only lowdfa reaches it.
  - T3 `forced` / `nullable`: never stamped.
  - T4 `capacity-declined`: none. `option` / `denied`: arms only.
  - `overflowed-prefilter`: 4 patterns. `size-model-declined`: 2.
  - Fix: a committed `row_reach` instrument (variant x row counts from the B1 trace). Each zero gets an explicit UNREACHED entry with its argument and an alternative witness. Add a `--tune=min-size` arm at lowsize.
- **M4. Sabotage: T3 and T4 have no plants.** Also missing: T2 rows 5-7; the T1 `on` mask widened to `overflow` on size rows (needs an `--engine=dfa` arm); the `sets` cells (`latch`, `carry`, `restart_term`); T1 row 2. Register run_fallback_table.sh in TEST_SECTIONS and as a mech arm.
- **M5. The trace gate needs instrument changes B0 omits.**
  - Per-slot ORDERED (fallback) vs SET (others) in trace_diff.py.
  - The fallback record carries no post-row state (dd, CR, SDR, flags_or, carry, latch), so a wrong `sets` cell is seen only downstream. Add the post-row state tuple.
  - State how `--variant` composes with `--trace`.
- **M6. The reader census undercounts.** Its FIELDS list is hand-kept. Missed: `fit.prefilter` 17 lines (incl. ir/nfa.c, dump/axes_dump.c), `prefilter_collapsed` 11, `overflow_why`/`dfa_overflow_why` 12, `size_cap_*` 14, `st_rescue`/`st_capexcl`/`st_final_k` 17, `dfa_overflow_is_budget` 3, `prefilter_nfa_states`/`prefilter_sizecap_*` 9. Fix: derive FIELDS from the EngineFit/Ctx cross-attempt members.
- **M7. Retiring the registry legs (axes_registry_check.sh:755/:782).**
  - (a) Timing: B5 deletes `cx.size_term_why =`, so the leg goes red at B5. Retire it at B5 with the PASS re-pin.
  - (b) No replacement ties the stamps to the doc. Fix: an observed-stamp leg in run_fallback_table.sh against match_api.md §6.3's hand-written sets, with K35 floors for all 7 UNROLL_K_WHY and all 8 ESEL values. Retire the old legs only after.

### MINOR
- **m1.** The histogram is independent for attempts and order, but it shares the setjmp / `rung->name` sites, cannot split size-term-trial from other, and never counts state.
- **m2.** Re-aims complete at region level (11 RE-AIM + S237/S252/S420 RE-RUN). The RE-RUN set is hand-derived. Do stc67's: owner resolution as a hard error, plus a B-rooted call graph so `rerun_at` is computed.
- **m3.** `degrading` vs `fof`: rows 3-4 are degrading yes and fof no, which contradicts limits.md §8 / run_resource_tests.sh:1338. Define it, or fix the sentence at B7.
- **m4.** The §1.8 self-check compares hand vs hand. Also assert max-observed (9) <= bound (25) in the trace build.
- **m5.** The has_var invariants are a corpus argument plus a structural argument, not a proof. Say so.

Not found wrong: S259/nomem coverage, the COMPILE_MAX_ATTEMPTS arithmetic, the T3 order vs compile.c:1850-1858, T2 rows 1-2.

## critB1 — SOUNDNESS
(pending)
