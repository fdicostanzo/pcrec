# Check-adequacy findings, lens CHK, round trailgc (SUBJECT 801ad12)

## Findings

### CHK-1: the "fast tier escalates / hysteresis" check cannot see the quarter rule's stop branch
- status: SUSPECTED, strong argument (confirm: apply S1793 by hand on a copy, run section 3 alone; expected escalations 1, default_rc 1, i.e. green)
- severity: speed (the O(1)-work-per-write bound is the stated reason for the quarter rule)
- effort: small (a compaction counter behind the existing RX_TEST_TIER_HOOK, asserted <= f(trail writes)); blast radius: tests/vm only
- location: tests/vm/run_trail_compact.sh section 3 (header lines 17-19, `cscan-idents` block), trail_compact_driver.c escalation count
- Section 3 asserts only `escalations == 1 && default_rc == 1`. With the stop branch removed (S1793: always re-arm at the floor) the fast tier still fills its trail and escalates once, with the same answer. The header says the check proves it "stops compacting instead of compacting at every pass"; nothing counts compactions. S1793's own comment says it is caught by the 816/817 boundary probes only, so the thrash property (work per write) is unobserved; any mutant that keeps the n=200 boundary but compacts more often passes.

### CHK-2: the two `identity` witnesses assert nothing about answers
- status: CONFIRMED. Run: bash tests/vm/run_trail_compact.sh (scratch TMPDIR) => `greedy-frames ... answered 0 below_hw 0 gaveup 315 mismatch 0`, `empty-guard ... answered 0 ... gaveup 376`, `backref-loop answered 1` (the single answer is nt==hw-ish).
- severity: answer (coverage claim only)
- effort: small (add a capacity == hw run to the ladder, or assert answered >= 1 + that compaction ran); blast radius: tests/vm
- location: run_trail_compact.sh witnesses lines "identity"; driver ladder loop
- `mismatch 0` is vacuously true when every capacity below the high-water gives up, and the ladder's stride (nt/64) usually skips hw itself. The header promise "the answers must still never change" for these three is therefore unobserved. The population gate (11/8/2) counts only the `compacts` kind, so nothing flags it. Also the population is exact-count (11, 8, 2): a wrong-direction edit has to be a coordinated edit, but learnings 3 prefers a manifest.

### CHK-3: check (2) "heaviest checkpoint-free path <= margin" is tautological
- status: CONFIRMED by reading plus output: every report shows heaviest == margin when the artifact has one function (`1 checkpoints ... path 5, margin 5`; corpus top: 251/251).
- severity: maintenance
- effort: small (compare per-function weight to the number of `_SET(` sites in that function, or drop the claim); blast radius: trail_checkpoints.py docstring/verdict
- location: trail_checkpoints.py check_text (margin compare), docstring VERDICT (2)
- Given verdict (1) (no SET-bearing SCC), a path in the condensation visits each line once, so its weight can never exceed the total `_SET(` count; the margin IS that count (emitter's `nset`, same source as the text). (2) can fail only if `nset` undercounts SETs in the text (a SET emitted bypassing vm_set) AND that path is the heaviest. It is not an independent check of "margin bounds growth between checkpoints"; the real bound rests on (1) alone and on the checker's "SET weight 1" assumption (a `_SET(` that writes more than one trail entry, or a direct `_TRAIL(` in emitted text, would not be counted; today `_TRAIL(` appears only inside the `_SET` macro, so this holds, but nothing checks it).

### CHK-4: the universal structural claim is checked on 11 artifacts in `make test`; the corpus sweep is opt-in on a wrong cost claim
- status: CONFIRMED. `python3 -I tests/vm/trail_checkpoints.py --corpus build/pcrec . ` takes 10 s wall (4984 corpus patterns, 4531 VM artifacts, 747 with a checkpoint, 0 FAIL), not "minutes".
- severity: maintenance/answer-risk
- effort: trivial (wire TRAIL_CORPUS=1 by default); blast radius: test-vm runtime +10 s
- location: run_trail_compact.sh header ("minutes, not part of make test"), end of script
- The only population check of "every cycle passes a checkpoint" (the soundness-of-reach, not of answers) is off by default. Mutants of `vm_jump_closes_trail_cycle` weaker than S1794-S1796 (e.g. `<` for `<=`, label clock off by one) are unsabotaged and would be found, if at all, only by the opt-in sweep or by a witness that happens to contain that edge. Also corpus mode counts refused patterns silently (453 skipped), and reads only the `pattern` rows, not their flags.

### CHK-5: ladder buffer is oversized, so a missing give-up/overrun is invisible except at two probes
- status: SUSPECTED (confirm: a mutant that drops the `trail_depth >= trail_cap` test; expect `mismatch 0`, and every capacity answers)
- severity: maintenance
- effort: small (allocate exactly nt entries per run under ASAN, as fb_exact_driver does for the specimen); blast radius: tests/vm driver
- location: trail_compact_driver.c `run()`: passes capacity nt but the buffer behind it is REF_TRAIL entries
- A write past capacity lands in the spare buffer, so a compaction (or write guard) that overruns reads as "answered below_hw" ("only a compaction can"). The claim is defended only by the specimen's 816 -> -3 probe and fb_exact's ASAN arm. Witnesses other than the specimen have no overrun detector.

### CHK-6: the 4n+17 boundary and the 763/764 ceilings are pinned from the implementation's own run
- status: CONFIRMED as a property (sr_gen.py: "placed BY HAND ... from edited constants"; fb_exact_driver.c: "Measured exact at every n tried"); not a defect, a limitation of the control
- severity: doc/design
- effort: none required; blast radius: S179/S180 anchors
- location: run_trail_compact.sh section 4 (one n = 200), sr_depth.rxt/sr_gen.py CEIL_OK/CEIL_GU, S179/S180 comments
- The formula (L = 3n-2, quarter, margin 15) is an analytic model fitted to measurement and then used as the expectation; it pins floor+margin+quarter together at n=200 and (via fb_exact, n = 761..765 and mmap) at large n, so a change in any constant breaks it loudly, which is the intent. But the expected value moves whenever the site count (margin) moves, so any emitter change that adds a SET site re-pins silently-by-hand. S179's cell is 1 entry beyond the stamped 3072 (n=764 needs 3073): its reach rests on a one-entry margin. The match spans themselves are libpcre2's (independent).

### CHK-7: sabotage coverage gaps
- status: SUSPECTED (each needs a hand mutant on a copy to confirm)
- severity: maintenance
- location: tests/mech/sabotages S1790-S1796
- Not sabotaged: `trail_gc_floor` (margin or the cap/2 clamp), the TRAIL_CHECK compare (`>` vs `>=`/`<`), segment-0 / last-segment handling (`f <= resume_depth`), the weaker predicate mutants of vm_jump_closes_trail_cycle (CHK-4), the cold/noinline attributes (a measured claim, no check). S1794-S1796 are caught by the emitted-C cycle checker, which is independent of the emitter (good); S1790-S1792 by the answer ladder (reach confirmed below). S1796 only if a witness has a guarded back-jump (the empty-guard star; witness `empty-guard`, which is an `identity` witness, so its structural arm is what carries it).

## PROBED-AND-HELD
- Full run of tests/vm/run_trail_compact.sh (scratch TMPDIR, review-tree binaries): 34 pass / 0 fail, all ref rc = 1 (a match, so captures are compared, not just rc); 11 witnesses, 8 compacting, 2 probes.
- Corpus structural sweep: 4984 patterns, 4531 artifacts, 747 with checkpoints, 0 FAIL, 10 s.
- Checker independence: it reads emitted C, models both `goto *` sites present in emit_vm.c (fail-dispatch via push edge, call_ret via CALL labels); no other computed jump exists in the emitter. Format assumptions (own-line `{`, `static` header, label regex) are shared with the emitter but a miss shows as "0 checkpoints" in the runner.
- Reach of the cscan k134 cells (BASE vs SUBJECT compiler, five bodies: 350 idents, 700 splices, 300 parens, 60 mixed, 60 braces): BASE default entry returns -3 on all five (even after tier escalation), SUBJECT returns 1; ladder: 382/308/350/339/33 capacities answer below the high-water. So the .rxt cells do reach the compaction (and spans come from libpcre2 via gen_cscan.py).
- My own differential (same driver, subject compiler, 21 patterns, each ~300-500 capacities): backtracking into older frames after compaction with captures read back (alternation fallback after possessive loop, recursion with captures, lookahead + negative lookahead in a possessive loop, lazy loops, atomic groups, subroutine calls): 0 mismatches; 11 of them answered at 300+ capacities below the high-water (unwind1, p03, p05, p06, p08, p16, q1, q2, q4 and the specimens).
- Soundness hazard search: trail depth is stored only in resume_stack marks (grep trail_depth/trail_mark: macros, compaction, the fail unwind at emit_vm.c:13354 and the full rewind at 12971), so no saved depth outside the frames' marks is invalidated by compaction.
- Mech arm "trailcompact": runs the tree's script with PCREC/CC/TMPDIR set, scores f/p from the script's own trailer lines (an ERR if the script dies); S1790-S1796 each use a single-occurrence anchor (SAB_COUNT=1).
- Re-pinned S155/S179/S180/S693 and codegen ABI expectation 91->93: the edits are consistent with the 93 stamp and the 764-level cell (S180: 2048 trail < 3073 needed, so the transposition still bites).
