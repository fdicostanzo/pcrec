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

**Verdict:** the no-mover claim HOLDS in the reachable space (0 BLOCKING). §4.1/§5.1/Q5 and the "total over every arrival" claim do not survive. The method used build/pcrec at dd7c2f3d, gdb hit counts on pcrec_select_engine (one per attempt), the emitted stamps, and --emit-ir reasons.

### MAJOR
- **MAJOR-1. §4.1's split is incomplete.**
  - T2 row 5 reads `empty_admits`, while T3's gate (compile.c:1835, `collapse = wanted && (fpf || !nullable)`) reads BARE nullable.
  - On nullable ∧ ¬empty_admits ∧ collapsible_rep, three things happen in order: the rung is offered; admission keeps the prefilter; the gate declines the collapse. So the exact machine that just failed is rebuilt and fails again. It is a pure waste attempt with an unchanged token, live at shipped limits:
    - `^(?:(?:a|b)*a(?:a|b){20})?$` takes att=3 overflowed-dfa (2 with -fno-prefilter-collapse);
    - `-e utf8 --features all ^(\p{Xwd}{1,3})?$` takes att=3 size-cap-retry (2 with the deny).
  - Fix (a), pfc_rep only, does not remove these, and F-B3 is not structurally closed by it.
  - Fix: split the conjunct three ways (pfc_rep; nullable∧¬empty_admits = waste; empty_admits = designed). The later row is either `requires = pfc_rep && !(nullable && !empty_admits && !fpf)` (compile time only), or a ruling that the gate reads empty_admits (a token mover: a2 goes overflowed-dfa -> collapsed-prefilter). In §7, list T2r5 vs T3r3 as two derivations of one question.
- **MAJOR-2. Fix (a) is not artifact-neutral.**
  - VM_PREFILTER_WHY carries the LAST refused attempt's byte figure, and deleting the wasted attempt changes it. Example: `-e utf8 --features all '(\p{Xwd})'` reads "hybrid 1028613 > 1000000" vs 1028607 with the deny; the .c diff is that one line.
  - So the later row is a STAMP-VALUE mover and needs a D76/D94 ruling. B itself keeps every attempt, so B is unaffected.
- **MAJOR-3. A fifth arrival is missing.**
  - compile.c:1179's `pf.forcing` arm (the --emit-facts forced ask) is tested FIRST, ahead of K60 nomem, and absorbs any failure into `decline:force-failed`.
  - The arm is not in §1.1, B3 or §7, and Q3's "total over every arrival" is false.
  - Risk: a nomem row at the top would propagate where today the forcing arm absorbs it (a stream-6/CLI mover).
  - Fix: a `forcing` label with row 0 ahead of nomem (or declare the arm outside and ahead of the walk), and add `pf.forcing` to state_readers.sh.

### MINOR
- **m1.** Row 2 (size-term-trial) fires up to N per run × 3 runs; the "each row at most once" prose is false. Add a trace-build assert that a non-trial row's bit is never set twice.
- **m2.** §1.7's "no size row after a [SEL-1] row" is argued wrongly. From an F-B3 state (pop 0), sel1-collapse -> prefilter-collapse -> T2 row 6 would stamp `selected` where today it stamps overflowed-{role}. Extend the :976 premise check, or add a §1.9 invariant.
- **m3.** fit_fired/fit_last must be volatile driver locals (setjmp). Declare the anchored machine's own overflow -> search-filter fallback (compile.c:365-372, PCREC_ANCHORED_MAX_STATES) as an unhosted sibling in §7.

### Could not refute
- T2's one order reproduces both the ternary and the listing chain (probed on a${v}b, ^${v}$, (a)*, (a*)*, the SEL-1 pattern, a2, a3, with and without the deny flags).
- esel_of's arm mapping on every reachable sequence.
- T1 order = code order (forcing aside); fof=false on rows 3-4.
- F-B4 (anchored dfa_overflowed save/restore).
- COMPILE_MAX_ATTEMPTS: 25 = 1+6+3·6, worst reachable 21.
- T3 vs the PFLW ternary; T4 vs size_term_why.
- §1.4(a)/(b).

## DISPOSITIONS (manager, 2026-10-08)

All findings ACCEPTED into a rev 2 (lane decfbrev2). Rulings:
- critB2 B1 (the emit-ir-auto stream plus hand-written check_ir_value rows covering every T2 row and scope) is a hard gate for B4.
- M1-M7 fixed as proposed. M7: retire the legs at B5, behind the observed-stamp leg.
- critB1 MAJOR-1/2: the §4.1 fix leaves B entirely and becomes a later row, [DEC-COLLAPSE-WASTE]. It has two candidate forms: compile-time-only `requires`, or the gate reading empty_admits (a token mover). Its D76/D94 status is ruled when it is built. B keeps every attempt and every stamp value.
- critB1 MAJOR-3: a `forcing` row 0 ahead of nomem (so the table really is total), with `pf.forcing` in the census.
- The minors are folded in.
- Frank's open questions are unchanged (Q1, Q2, Q4(b)); the manager takes the recommendations on Q3/Q5/Q6/Q7. Q5 is reframed by MAJOR-1/2: it moves to the later row.
