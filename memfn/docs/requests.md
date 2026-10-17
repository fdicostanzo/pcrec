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

## R-5 (2026-10-07, pcrec manager) — M1b, runcmp migrates, zero movers (after R4c′)

**Customer:** `[MEMFN]`, integration.md §22 "M1b, runcmp migrates" exactly as written there (bit 43 crosses per §14.10; `RUN_WORDS` becomes the kit's stamp). **Prerequisite:** R4c (merged 81bc13de) and R4c′ delivered and merged first. **Trigger:** completeness (Q42; a migration step). M1b also unlocks M7.

**Why M1b before R4g/R4h/M4 (manager's sequencing, D153 remodel-first):** of the zero-mover steps whose prerequisite is met, M1b is the only one with no overlap with main's in-flight remodel. R4g (PF) touches the prefilter sites that [START-TABLE] C1-C7 and refactor B ([DEC-FALLBACK], incl. prefilter admission) edit next; R4h's scan-edge loop and M4's MLINE scan sit next to the start rows too. Those wait until C1 has re-derived its edit set on post-R4c′ main. If your scoping finds that M1b DOES read a start decision, stop and name the read (R-4's boundary rule applies unchanged).

**Landing bar:** same as R-4. Zero movers: the identity gate is byte-identical to main over the corpus and every axis, with I2 over both comment tiers. Also `make strict`, `make test-codegen`, and the registry, codegen and rxtsource suites. State the mech-row re-point count, and [SABANCHOR] must be green. Mac `make test` goes on a slot I name, and the Linux verdict comes through my executor channel (a pinned script). Any byte that moves is a defect: STOP and report it. Use sabotage ids from a block you request from me; do not take the next free id.

## R-6 (2026-10-07, pcrec manager) — pcrec states `miss = MF_MISS_N` at the three N2 cells, zero movers

**Customer:** `[MEMFN-ROWCON]` N3 (enforcement). N3's entry condition is an N2 re-run showing 0 would-decline verdicts. The kit's notices "N2 census DONE; the R-6 list" and "MF_MISS_N ready for R-6" are the source of this request.

**Trigger:** N2 (`docs/design/memfn/probes/rowcon/n2_results_5fc4b0e5.md`, 958,292 compiles) found 129,937 would-decline verdicts. They collapse to exactly three cells, all rule R1 (`miss` used by the row, left unstated by the site):
1. ofsskip, FUNC / FIND / RETURN, at DEFINE (56,104 sites);
2. the same ofsskip site at USE, the call (56,104);
3. precheck, STMT / ALL_PRESENT / ASSIGN, at USE (17,729).

**Wanted:** pcrec's hook builders state `.miss = MF_MISS_N` at those three cells and nowhere else:
- `ofs_site_define` (define hooks) and `pf_ofs_call` (use hooks) in `src/gen/emit_dfa.c`;
- the ASSIGN route of `pcrec_emit_req_byte_check` (use hooks) in `src/gen/emit_dfa.c`.

`MF_MISS_N` is on main (kit lane `missn`, merged at 13b9f2ae). The kit resolves it to the site's `n` hook; its bytes never reach an artifact.

**Contract:** ZERO MOVERS. Prove it with `scripts/emit_sweep.py --ref <main sha>` judged by `memfn_r4c_gate.py --zero-dumps` (R4C-GATE PASS, 0 movers on all six streams). No abi event. Where cheap, show the N2 would-decline count at those cells falling to 0.

**Landing bar:** the gate above, `make strict`, the full `make test`, and solo mech for every sabotage row whose anchor file was edited (they must stay DETECTED).

## R-7 (2026-10-08, pcrec manager) — M4, MLINE migrates, zero movers (READ-ONLY scoping first)

**Customer:** `[MEMFN]`, integration.md §15.7 M4: the `(?m)^` candidate scan, a `memchr('\n')` in `emit_attempt` (src/gen/emit_dfa.c). Shape: the same as R4g's FIND.

**Prerequisite:** R4c (met).

**Trigger:** completeness (D147 addendum 5 / Q42, "every search site migrates"). MLINE is one of the four `pending` sites in the checked manifest (with N6, VMSTRIDE, N7). It also finishes the C12 memchr ratchet: 1 -> 0 outside the kit.

**Sequencing:** the kit's order is accepted: M4, then M7 (N7, the span compare in the encoding seam; Q54 ruled YES), then M6 (N6 + VMSTRIDE), then R4j/M5 (the planner goes live; needs a careful overlap check with refactor B). Each step after M4 gets its own request.

**Step 1, READ-ONLY scoping, before any edit.** Post the edit set to me (responses notice), with an OVERLAP CHECK against:
- refactor B, [DEC-FALLBACK]: docs/design/dec_fallback.md (rev 2 in progress, lane decfbrev2). B edits compile.c's fallback ladder, select_engine.c's admission/esel_of, and the emit_vm.c stamp writers. Its edit set is under docs/design/dec_fallback/.
- anything else touching `emit_attempt` or the ATTEMPT route: the start table's `cand_rows[]` NEXT/BOUND rows on CAND_ROUTE_ATTEMPT, `attempt_next_read`, `attempt_cand`.

**The boundary (R-4's rule, unchanged):** move the SEARCH TEXT only. Every start decision, row selection, admission and BOUND/route read stays pcrec-side. Name any read the migrating emitter does today.

**Landing bar (same as R-5/R-6):**
- ZERO MOVERS: `scripts/emit_sweep.py --ref <main sha>` judged by `memfn_r4c_gate.py --zero-dumps`, R4C-GATE PASS with 0 movers on all six streams. No abi event; any byte that moves is a defect, so STOP and report it.
- `make strict`; the full `make test` on a slot I name; solo mech for every sabotage row whose anchor moves (they must stay DETECTED); [SABANCHOR] green.
- Sabotage ids come from a block you request from me.

## R-8 (2026-10-08, pcrec manager) — M7, N7 (the encoding seam's span compare) migrates, zero movers (READ-ONLY scoping first)

**Customer:** `[MEMFN]`, integration.md §22 M7: N7, `src/enc/enc_byte.c`'s `$_span_match` / `$_span_match_caseless` (the backreference and variable span compare the encoding seam emits).

**Prerequisite:** M1b (met). Q54 is RULED YES (D147 addendum 10).

**Trigger:** completeness (D147 addendum 5 / Q42). N7 is one of the three remaining `pending` manifest sites (with N6 and VMSTRIDE).

**Sequencing:** M7 now, then M6 (N6 + VMSTRIDE; R4h has landed), then R4j/M5 (the planner goes live, with a careful overlap check against refactor B). Each step gets its own request.

**Step 1, READ-ONLY scoping, before any edit.** Post a responses notice to me with:
- the edit set;
- the BOUNDARY: what stays the encoding's under D58/DD-12. The seam's per-encoding text is the encoding module's (src/enc/CLAUDE.md, D58's revisit clause), so name which bytes move to the kit and which stay backend text;
- the OVERLAP CHECK under D153:
  - against refactor B, [DEC-FALLBACK] B3+ (docs/design/dec_fallback.md; B3 is lane decfbB3, compile.c only; B4 edits select_engine.c's admission and the `--emit-ir` chain; B5 the token derivations);
  - against any in-flight `src/enc/` work;
- the VOCABULARY gap: the `MF_VOCAB` bump for a run-time-operand `mismatch` that returns a prefix count, caseless variant included.

**Scope also carries:**
- C17's static scan gains `src/enc/`;
- manifest N7 goes `pending` -> `delegated`;
- the rider: delete the redundant `"memchr"` entry in `src/gen/memfn_stamps.c` `libc_names[]` (no byte moves; S513's tripwire is re-pinned or retired in the same change).

**Blinded G2:** the new `mismatch` operation gets its oracle from a D27 lane (cell `g2u-cell`), before the slot.

**Landing bar (as R-7):**
- ZERO MOVERS: `scripts/emit_sweep.py --ref <main sha>` judged by `memfn_r4c_gate.py --zero-dumps`, R4C-GATE PASS with 0 movers on every stream. Run both encodings: N7 is per-encoding text, so the `-e utf8` base is mandatory. No abi event; any byte that moves is a defect, so STOP and report it.
- `make strict`. The slot chain is census, identity gate, G2 full, `make test` via `scripts/perfrun`, and solo mech for every row whose anchor moves (they must stay DETECTED). [SABANCHOR] green.
- Sabotage ids: S666-S675 are yours. Grep main and worktrees before taking one.

## R-9 (2026-10-08, pcrec manager) — R4e′ DESIGN PASS: the SIMD layer as a parallel thread (D147 addendum 11), design + D6 panel, no pcrec bytes

**Customer:** `[OPT-SIMD]`, opened 2026-10-08 for the kit's opt-in `-fmemfn-simd` layer only (D147 addendum 11, Frank: the "I'm not left handed" strategy, meaning the scalar and SIMD paths are optimized independently).

**Trigger:** Frank's ruling (D147 addendum 11). It supersedes integration.md §22 R4e′'s old trigger ("`[OPT-SIMD]` opened (D119: SIMD last)").

**Capacity:** this is the SIMD thread's first item under the 2:1 migration:SIMD split. Design only: no pcrec bytes, no heavy slot.

**Deliverable:** a revision of integration.md §R4.3.2 and §22 R4e′ under the ruling. It covers:
- the SCAN_ROWS form table (SIMD forms as rows beside the scalar arms, selected by the site's facts and the policy word);
- cascades and the short-span path (R-1's 16 B AVX2 rows);
- the `-fmemfn-simd` axis status (built or owed; pcrec owns the axis, so name any pcrec-side change as a later request);
- the MEASUREMENT REGIME on the shared box: the Linux verdict, both layers reported, quiet-box slots through main, the aarch64 rule of D147 addendum 8, and every unroll width, block size or cut-over measured, derived or left to the compiler (D149);
- the acceptance bar per form: faster than the CURRENT scalar layer at its sites, or a named benefit;
- the first batch of sites, with each one's evidence (R-1/R4b, isa_*.md, linux_results.md);
- the three standing questions of docs/design/CLAUDE.md.

Then a D6 panel (2-4 read-only critics; the lenses include check independence and the sibling-of-a-family lens). Finish with the Q-n for Frank and a notice to me. Each later batch of SIMD sites is its own request.

## R-10 (2026-10-08, pcrec manager) — M6: N6 + VMSTRIDE migrate, zero movers (READ-ONLY scoping first)

**Customer:** `[MEMFN]`, integration.md §22 M6. **Prerequisite:** R4h (landed).

**Trigger:** completeness (D147 addendum 5 / Q42). After M7 these are the last `pending` manifest sites, apart from N7U.

**Capacity:** a migration-thread item (2:1 split). It may start as soon as a migration lane is free; M7's slot comes first.

**Step 1, READ-ONLY scoping, before any edit.** Post a responses notice with the same shape as R-8's:
- the edit set;
- the boundary (search text only; every start decision, row selection, admission and BOUND/route read stays pcrec-side; name every read the migrating emitter does today);
- the OVERLAP CHECK under D153 against refactor B (B4 = select_engine.c's admission and emit_vm.c's `--emit-ir` prefilter chain, landing now; B5 = the token derivations: `esel_of`, PFLW, `size_term_why`, `VM_PREFILTER_WHY`) and against any in-flight work on the VM's strided span loop;
- the vocabulary gap, if any.

**Landing bar:** R-5/R-6/R-8's. ZERO MOVERS judged by `memfn_r4c_gate.py --zero-dumps`; `make strict`; the full `make test` on a slot I name; solo mech for every moved anchor; [SABANCHOR] green. Sabotage ids: S676-S685.

## R-11 (2026-10-09, pcrec manager) — R4e′.0 then R4e′.0b: the FUNC-body seam `fn_rows[]` (zero movers), then SIMD-off routed through `<fn>__body` (one pcrec abi event)

**Customer:** `[OPT-SIMD]`, integration.md rev 4.9 §R4.9 (R-9 done, ad3d9ea4, merged to main in this session).

**Trigger:** R-9 is done, and §R4.9's build order puts these two steps ahead of every SIMD row.

**Capacity:** the SIMD thread's item under the 2:1 split. It does not jump M6. R-10 keeps its order, and both R-11 steps queue behind M6's slot14 for heavy slots.

**Step R4e′.0, kit-only, ZERO MOVERS (§R4.9.2.1, RQ-0).** PRE and OFS share a selected first-match table `fn_rows[]`. It has a BODY slot, today's scalar loops promoted byte-identically, and an empty PREFIX slot. No decorator over the floor.
- Landing bar: R-8/R-10's. Zero movers by `memfn_r4c_gate.py --zero-dumps`; `make strict`; full `make test` on a slot I name; solo mech for every moved anchor; [SABANCHOR] green.

**Step R4e′.0b, the routing commit (§R4.9.2.5/§R4.9.2.6, D155 item 6, RQ-6).** SIMD-off routes every FUNC through `<fn>__body`, and the FUNC becomes the file-scope selector. This is a pcrec ABI EVENT, done in the same commit:
- bump to the next abi number at landing; do not presume it, read main's;
- find EVERY reader of the number by grep (D94: the `.abi` stamp, test expectations, spec sentences, the gate's (B) pin);
- re-pin the identity gates;
- run `make test-codegen` plus the suites that count (registry, codegen, rxtsource).
- Measured as §R4.9.2.6's G1 census:
  - movers by id against the `fn` census, with the predicted +139 B per FUNC checked per mover;
  - the un-done text diff;
  - assembly identity at `-O2` default and at v3 (predicted 0 assembly movers);
  - timing ONLY for a non-identical mover.
- The census report travels with the commit.
- Its two prerequisites: R4e′.0 merged, and main free of an in-flight abi event. Ask me before the slot so I can confirm the number.

**Not in this request:**
- Batch 1's rows (`vrun-w32`/`vrun-w16`). They wait on main's RQ-1 (`--memfn=` carrier), RQ-2 (`pcrec_find_pick2` / `plan_pos2`) and RQ-3 (SIMD-guarded bytes neutral to length decisions), and on RQ-4's slot. Main files them on pcrec's side, then files batch 1 as its own request.
- [EMIT-VERB]: no plan row. It resolves through decisions.md, and no measured need asks for a row (D77).

**Sabotage ids:** S686-S695.

## R-12 (2026-10-09, pcrec manager) — VMLAZY + N7U: READ-ONLY scoping of the last two `pending` migration sites

**Customer:** `[MEMFN]`, completeness (D147 addendum 5 / Q42). After M6 and M7, the site manifest's only `pending` rows are VMLAZY (`vm_cursor_rep`'s lazy rmin prefix loop, listed at M6) and N7U (`u8_defs_bref_ci`, the utf8 caseless per-character compare, split off at M7).

**Capacity:** the migration thread's item under the 2:1 split, run beside R-13.

**Step 1, READ-ONLY scoping, before any edit** (R-8/R-10's shape). For each site, post a responses notice giving:
- the edit set;
- the boundary: search text only, and name every pcrec read the migrating emitter does today;
- the vocabulary or contract gap. Both rows say they need one: VMLAZY needs a counted ADVANCE that must reach K, or VERIFY over a counted run of position sets. N7U needs a per-character decode compare with a decode hook, two cursors and a length-changing result.
- whether either is better RETIRED by ruling than migrated, as N6 was (D147 addendum 12). Argue it either way.
- an overlap check against R-13 (batch 1 touches the FUNC seam, not these sites, but confirm it).
Also say which of the two, if either, should go before R4j/M5 (the planner moving live).

**Landing bar for the later steps:** R-8/R-10's. Sabotage ids: S706-S715.

## R-13 (2026-10-09, pcrec manager) — R4e′ BATCH 1: `vrun-w32` / `vrun-w16`, the first SIMD rows (CANDIDATE)

**Customer:** `[OPT-SIMD]`, integration.md rev 4.9 §R4.9 (batch 1 = §R4.9.7, narrowed by D155's facts to the fused pair search, `fn-pair` sites).

**Trigger:** R-11 is complete (R4e′.0 + R4e′.0b on main, abi 70). pcrec's prerequisites:
- **RQ-1** (`--memfn=`) is on main (5761cd03). `options.def` is empty today, so a non-empty string is refused. Batch 1's deny rows are its first entries, and each comes with a pcrec cli case in the same commit.
- **RQ-3** (SIMD bytes neutral to size decisions, `<PREFIX>_SIMD_GUARDED_BYTES`, `make test-memfn-guarded`) is on lane/rq3 at abi 71, landing after its chain. Build against main once it lands. pcrec's half of the bracket is `pcrec_memfn_sink_simd_open(void*, int level)` / `_close(void*)` in src/gen/memfn_sites.h, unwired. Wire it into `mf_sink` (the kit's members) and `pcrec_memfn_sink`. Every SIMD row brackets its guarded text, and declares its per-row bound in tests/memfn/simd_bounds.tsv (D155 Q-R9-9 + addendum 2).
- **RQ-2** (`pcrec_find_pick2` / `plan_pos2`) is NOT built. It is needed before the tier-U sweeps, not before the build. Main schedules it.
- **RQ-4** (the dev-box tier-U slot: one logical CPU, sibling idle, load1 < 0.5) is main's to grant when the sweeps are ready.
- **RQ-5** (the bench submission) goes via main after the rows land as CANDIDATE.

**Deliverable:** §R4.9.7 batch 1:
- the sink ops first;
- then the PREFIX rows `vrun-w32`/`vrun-w16`, SSE first, in `levels.def` order;
- each row with its own deny, its bound, G2 coverage, C18's four legs and the guard lint;
- landing as CANDIDATE, with both layers read and `-fmemfn-simd` default OFF.
The floor rule holds: SIMD-off artifacts are byte-identical to main's. Prove it with the identity gate on every arm. SIMD-on changes only guarded text.

**Capacity:** the SIMD thread's item under the 2:1 split. Heavy slots come through main, one at a time.

**Sabotage ids:** S716-S730. The R-13 follow-up (lane rankuse, the kit's use of `mf_pred.rank_*`, D157) holds S750-S757 (allocated 2026-10-09; next free S758).

## R-14 (2026-10-11, pcrec manager) — VRUN VERIFY TRIM: verify only the run positions the filter did not prove; re-time KB's losing regimes

**Customer:** `[OPT-SIMD]`; Frank's Q-RQ4-1 ruling, D147 addendum 15 (kit notice 46499759).

**Trigger:** RQ-4's measured KB losses (slot20: 179 of 1,396 comparisons, +2..11% in the dense-hit and short-span regimes; `docs/dev/lanes/rq4h_report.md` addendum, `docs/design/memfn/probes/rq4/out/slot20_table.md`).

**Deliverable:**
- vrun's per-candidate verify checks only the run positions NOT covered by the filter (KA, plus KB when rendered).
- It is kit-local and changes no SIMD-off byte: prove that with the identity gate on every arm, so there is no pcrec abi event. SIMD-on text moves. If the trimmed verify is its own form, it gets its own deny row per the `options.def` rule.
- G2 and simdfloor stay green.
- A re-timing pass on slot20's harness (`RQ4` cells: dense-hit, the spacing ladder, pc16/short75), at both levels and both layers. It is a heavy slot, so ask main for the GO. Report the 179 losing comparisons before and after.

**Out of scope:** N >= 3 positions (a mask-is-verify run) and handing the DFA the post-run state (pcrec-side); both are logged in memfn/docs/ideas.md.

**Capacity:** the SIMD thread's item under the 2:1 split.

**Sabotage ids:** S793-S799 (allocated 2026-10-11; next free S800).

## R-15 (2026-10-11, pcrec manager) — the byte gate's ASSIGN over ONE set term becomes a hot scan site under [REQ-HANDOFF-L1]'s re-entry

**Customer:** `[REQ-HANDOFF-L1]` (plan.md), measured by lane rlhtwin (`docs/dev/lanes/rlhtwin_report.md` §5 Q4).

**Facts:** the req byte gate site with mode (ALL_PRESENT, ASSIGN, SET) and exactly ONE byte term, where the matched position is KEPT, not just tested. Today it renders through the generic per-byte loop. Under the re-entered handoff, this site runs at every restart of the unanchored body, so it becomes the hot scan of the search. Cells: loglines/ipv6, loglines/ipv4, bounded/dotted4.

**Deliverable:** a row serving that site shape (the kit's method). SIMD-off bytes may move only on the sites this row serves, and they move together with pcrec's [REQ-HANDOFF-L1] merge (one abi event, sequenced by main). Prove identity on every other site.

**Trigger:** rlhtwin's twins: the re-entered handoff captures 109-120% of reverse-inner's win on ipv6/ipv4 with the scan on this site.

**Capacity:** migration thread; after slot21.

**Sabotage ids:** S800-S804 (allocated 2026-10-11; next free S805).

## R-16 (2026-10-11, pcrec manager) — KB AT w32 ONLY: w16 vrun filters on KA alone

**Customer:** `[OPT-SIMD]`; Frank's Q-R14-1 ruling, D147 addendum 16.

**Trigger:** slot21's reading after R-14 (w16 KB throughput 133 W / 59 L; w32 still wins).

**Deliverable:** w16 vrun renders KA only; w32 keeps KA+KB. SIMD-off byte-identical (identity gate on every arm), so no pcrec abi event. `vrun-kb` deny unchanged. G2 and simdfloor green. Fold in the triage of slot21's 11 D-F comparisons losing >= 10% (w32 sparse throughput, m10/m12/v03/v05/v11) if it concerns the same rows. Any re-timing is a heavy slot on main's GO.

**Capacity:** the SIMD thread; after R-15.

**Sabotage ids:** S815-S819 (allocated 2026-10-11; next free S820).

## R-17 (2026-10-11, pcrec manager) — FIND sites scanning a SMALL or ONE-CUBE byte set lose to the peers; the VM hat scans a one-byte set through a table

**Customer:** `[LOSS-REVIEW]` (docs/dev/optloop/lossreview/fixes.md candidate 5(b), revision 2; the r2 D6 panel `docs/dev/reviews/2026-10-11-r2-lossreview-fixes.md` F4).

**Facts:**
- FIND sites (the DFA prefilter, the DFA hat, the VM hat seek; reached today through `PcrecFind`) render the byte-table walk for every scanned set S with |S| > 1 (the facts: S itself, as a set; e.g. `{s,S}`, `{a,c}`, `{A,B,a,b}`, `[0-9]`). [Restated 2026-10-11 per D157: an earlier wording named shape classes (cube, range), which are the kit's methods, not facts.] Measured losses on the bench (phase 1, per-cell tables in `docs/dev/optloop/lossreview/dfa.md` / `vm.md`): set-skip 3.85 ms, PAIR-SKIP 1.36 ms, RANGE-SKIP 0.44 ms. The set-skip and range peers that win are SIMD-capable (rust); the pair cells also trail scalar peers.
- The VM hat seek renders the TABLE walk even at |S| = 1 (C2, 2.58 ms; the caller near `src/gen/emit_dfa.c:7200` passes the set, not a byte).
- The OFS BODY and PRE sites that test the same kinds of sets present them through the same FIND description (population 0 today per the kit's scoping, r17s_report.md).
- Density: pcrec will fill `mf_site.cand_ppm_lo/hi` and `mf_term.ppm_lo/hi` (memfn.h:272, :337) from its prior at every one of these sites in a separate no-mover change after this request (they read "unknown" today). The kit may read them once filled; nothing in this request presumes it does.

**Deliverable:** rows serving these site shapes — the kit's method and form choice. D122's rule binds: one implementation per search, reachable from every site that presents the shape, not a copy per site. SIMD-off bytes may move only where the rows serve; a SIMD-off mover is a pcrec abi event sequenced by main.

**Trigger:** the phase-1 cells above (loss measured; GAIN unknown). Twin the forms on the named cells first; the build follows only a measured win (D77, D147: each form must beat the scalar it replaces or show a named benefit).

**Capacity:** migration thread (the scalar forms), after R-16; any SIMD form is the SIMD thread's under the 2:1 split.

**Sabotage ids:** S820-S824 (allocated 2026-10-11; next free S825).

## R-18 (2026-10-12, pcrec manager) — THE WINDOW SEARCH (D161): one general search category, fed by spans and the analysis object

**Customer:** D161 and addenda 1-9, D162 and addenda 1-4 (chunk 3, docs/dev/chunks_2026-10-11.md). The contract is docs/design/memfn/window_contract.md revision 2.1 (light D6 panel docs/dev/reviews/2026-10-12-r4-window-contract.md, dispositions applied). It SUPERSEDES the per-shape interfaces of R-15 (the ASSIGN gate), R-17 (the set FIND) and the PF/OFS/PRE sites; their forms and measurements carry over.

**Facts pcrec will state (contract §2-§3):**
- A site is a bounded sub-problem whose ORIGIN pcrec chooses (segment 0's start, or an inner segment's start where pcrec recovers the head itself). Given the origin, pcrec sends EVERY span whose distance to it is bounded and never pre-selects among them (D161 add. 9).
- Spans are `mf_pred`s with stated `move_back`/`overshoot` and `need`; every stated parameter is true and required (D161 add. 4). `spans_seq` states the sequence rule (tri-state; a tight hull, not exact distances). Context predicates (negative offsets, e.g. `(?m)^`'s preceding `\n`) are not spans; pcrec tries the edge itself (D161 add. 7).
- Presence sites carry no window (their own table).
- `mf_site.analysis`: the per-compile analysis object, kinds keyed by name with PROVENANCE, frequency always offered (D162 add. 2-3). Derived data you need (rankings, rarity) is yours to build once per compile as a memo of the object (D162 add. 3-4).

**Obligations on the reply:** a STREAM of candidate origins (the stateful next-candidate form, D155 add. 4.1): COMPLETE (every position where the stated spans hold appears), ASCENDING with no repeats, each candidate the origin; an exhausted stream means no covered candidate; totality without the analysis object (D162). When [KIT-VERIFY] builds: a compile-time `proven` statement that is the same in every layer (D161 add. 8).

**Facts pcrec will NOT state:** a consumer price (D161 add. 6), a span index, a scan position (`plan_hint` retires at S4), a ranking (`rank_*` retires at S3), per-site rates.

**Deliverable:** your method is your own (D157). Serve every degenerate site (one span, length 1) at zero SIMD-off movers first; then multi-span sites behind their own denies; every SIMD-off byte move lands with pcrec's abi event in the same commit.

**Capability pcrec provides:** storage as ratified (contract §7: `mf_locals`, one handle per site).

**Trigger:** R-17's PF routing event merged (R17-b). First multi-span consumer: the K82/L1 handoff's fused gate re-expressed as a stream (contract §2.4), cells loglines/ipv6, ipv4, bounded/dotted4; then wingame's syslogbase-expanded and the refine witnesses. Twin first, build on a measured win (D77, D147).

**Sequencing (main's):** the contract's S1-S3 (the frequency kind, your ranking under a shadow comparison, the MF_SITE_ABI retirement) may land before the R-18 build; S4 (prior-reading picks into the kit) rides it.

**Capacity:** migration thread (scalar forms); SIMD forms are the SIMD thread's under the 2:1 split.

**Sabotage ids:** S871-S880 (allocated 2026-10-12; next free S881).

> **R-18 amendment (2026-10-16, pcrec manager; window_contract.md revision 3,
> C-7).** Three bullets of R-18 are superseded:
> - "Presence sites carry no window (their own table)" → **presence is a span
>   class of the one window request** (D161 add. 14 and its clarification;
>   R-21). A PRESENCE span states `omin ≥ 0` from the match start, no `omax`,
>   a `need`, and, for a set member, its `member_order`. An EMPTY stream is
>   NOMATCH, decided before the first element, one verdict per activation, and
>   K65's give-up conversions are preserved (contract §2.2, §2.4 obligations
>   5-7).
> - "`mf_site.analysis`: the per-compile analysis object" → **the analysis
>   object is stated ONCE per art, in the `mf_art_begin` slot your B1
>   declares** (contract §3.7.2). From the first commit that routes a row
>   reading a kind (B3b, or S2's REPLACE if earlier), you return a per-kind
>   `consulted` at `mf_art_end`, the same in every layer (contract §3.3 rule
>   8). pcrec ORs it into `<PREFIX>_FINDINGS`.
> - "Serve every degenerate site (one span, length 1) at zero SIMD-off movers
>   first" → **every degenerate site: one BOUNDED span of length 1, a
>   CONTEXT-only site (MLINE), or a PRESENCE-only site**, at zero SIMD-off
>   movers first.
>
> Two facts are added: every span's `byte_form` (EXACT or SUPERSET, D161 add.
> 10; verify and proofs on EXACT only) and the span class enum
> (`UNSTATED`, `BOUNDED`, `CONTEXT`, `PRESENCE`). Main's E-1 fills the
> analysis slot after your B2 merges, with no kit edit. Under the contract's
> CONSULTED stamp rule it moves no byte.

## R-19 (2026-10-14, pcrec manager) — R17-b′'s site facts: the CALL MODE per entry body, and the activation's ORIGIN expression

**Customer:** [REGIME] / D161 addenda 11-13; the kit's R17-b′ (docs/design/memfn/r17b_prime.md on lane/memfn-r17 a1799a5d2). The facts are the knowledge keys M and N (docs/design/regime_tables.md §2).

**Facts pcrec will state:**
- `mf_site.body`: the CALL MODE of the entry body the site sits in, `MF_BODY_ONESHOT` / `MF_BODY_ITER`; `0` = unstated, and the rows that need it (R1/R2) skip. Every builder states ONESHOT at R17-b′; the D165 iterator's `next` bodies state ITER at R17-b″.
- The START HOOK: the TEXT of the activation's origin expression at the storage point, so the kit can emit `N = n - start` for its dispatch: `search_from` for the DFA forward scan and the VM `_search_run`, the relocate path's moved start, `fwd->from` in unanch_scan. Unstated, the dispatch rows skip. (This is NOT the D165 iterator's state zero-init, a separate R17-b″ item.)

**Not stated now:** `site_kind` (key P's site kind for R5/R6's per-site g*) is GATED on [REGIME-LANDINGS] (D77: needed only when E arrives). The measurement-set channel `mf_measures` waits for [MEASURE-SET]; until then the kit reads its own TSV in D166's shape (regime_eval.md Q-REVAL-10).

**Deliverable:** your method is your own (D157). The facts are stated at zero movers first (no emitted byte moves until a row reads them).

**Trigger:** R17-b′'s D6 panel outcome.

**Sabotage ids:** within R17-b′'s S911-S922 (allocated 2026-10-14).

**Amendment (2026-10-16, main, Q-R17P-16; r17b_prime.md rev 3 on lane/memfn-fd a8ee399fe):** the builder list gains `req_site_define`, MLINE and `attempt_entry` (every builder states `body`). The original text above is unchanged.

## R-20 (2026-10-14, pcrec manager) — [MEASURE-SET] M0's kit seams: the set in, "consulted" out, form hashes, reader declarations, method cards

**Customer:** [MEASURE-SET] and [KNOW-SRC] (docs/design/measure_sets.md revision 2.1, §4.4 and §10.1; D166 + addenda 1-2; panel docs/dev/reviews/2026-10-14-r1-measure-sets.md). Five items, with the landing bars as in the note (main-side numbering R-MS1..R-MS5):

|---|---|---|---|
| R-MS1 | `mf_measures` on `mf_art_begin` as §4.1 states (kit rows only, no `status`; NULL = no set) | the kit's tests run every finder row with NULL, with a synthetic set lacking each key in turn (the row skips to its `unpaid` pick or the next row), and with the full set; a kit row never reads a `pcrec.` key | M0 |
| R-MS2 | `consulted` out of `mf_art_end` (§4.2) | a kit test with a compile whose sites read no set key → false; one row that reads an ABSENT key → true; one that reads a present key → true. pcrec's S945 (§8.5) reaches it | M0 |
| R-MS3 | `mf_form_hash(form_id)` over the canonical instance (§2.4), and the form ids the kit's cards name in `deps` | the hash is unchanged under a zero-mover kit refactor (renamed helper, comment edit) and changed under a one-instruction body edit, both as kit fixtures; every form id a kit card names resolves | M0 (staleness listing) |
| R-MS4 | the kit's READER DECLARATION: per finder-table row, the keys it reads and, per threshold key, its SAFE direction (`max`/`min`/`none`: the side of its conservative or `unpaid` pick), as data the kit's listing exposes in [LIST-TABLES]' census shape (§5.4); and, per artifact, which finder rows fired per site, as the `--emit-facts` section `memfn` (§4.5) | keys: every key a row reads is declared (the kit-side half of §8.6's ⊆ check); directions: each declared direction agrees with the row's comparison operator by a kit test | keys M0 (the listing's readers); directions M2 (the envelope) |
| R-MS5 | the kit's METHOD CARDS for its quantities (§7.2), as a section TSV in the kit tree, versioned `kit-grid@N` | each quantity R17-b′ §3.2 lists has a card; grid1's and grid2's rows are on-card (`make test-measures` §8.2) | M0 (the first committed set must be on a card) |

**Sequencing:** pcrec's [KNOW-SRC] stages K0-K3 build first at zero movers. M0 (the `measures` kind) triggers when R17-b′ lands WITH R-MS1, R-MS2, R-MS3 and R-MS5. R-MS4's keys are due at M0 and its safe directions at M2 (the envelope).

**Facts only (D157):** pcrec hands over the kit's rows of the active set and never presumes how the kit uses them. The cards, hashes and reader declarations are the kit's own data. Until [KNOW-SRC]'s canonical view lands, the interim set TSV follows that shape.

**Sabotage ids:** pcrec-side S943-S963 (allocated); kit-side ids on request.

## R-21 (2026-10-14, pcrec manager) — THE ONE WINDOW REQUEST (D161 add. 14 + its clarification): single-byte FIND, presence and handoff stated as facts

**Customer:** D161 addenda 11-14 and the add. 14 clarification (presence + find = ONE window request; EMPTY = NOMATCH; the K65 give-up obligation). Source: the kit's merged list docs/dev/lanes/winreq_report.md (lane/memfn-r17 4404387d0), from the sbscope + pcscope scoping lanes. Steps: ST1 facts stated + shadow comparator (zero movers); ST2 one-byte rows replace (zero movers); ST3 presence + handoff replace (zero movers, after E-1 mf_analysis); ST4 the pre-scan row priced (a mover, its own abi event); ST5 libc deny (future work, D161 add. 14 / Q-WR-7); ST6 R17-b′ dispatch rows.

**Facts pcrec will state (PR-1..PR-11, verbatim from winreq §1.2):**

| id | kind | the fact | where pcrec has it today (main) | size | trigger | D157 check |
|---|---|---|---|---|---|---|
| PR-1 | fact | the candidate set as a SET term at every count (one member included), plus the table offer, on every PF/VM-hat site | `cand_derive` `emit_dfa.c:4290` (`use_memchr = count == 1`); term encoding `:6505` (`PF_SCAN_BYTE` → `term_byte`, no table); `find_site` `:6443`, `pcrec_emit_find` `:6490`. Kit side: R17-a `reads_table`/`includes` on this branch | S | ST2 | OK: states the set and that a table exists. Today's one-member `term_byte` encoding IS a form choice; removing it is the fix |
| PR-2 | fact | the miss and move behaviour as hooks: what the consumer needs when the subject is at or past `n` (`empty` + `on_miss`), the bound `n - 1` for bounded rows, a hook that runs when the candidate differs from the start (the DFA hat's re-seed `skip_from`) | guard BEFORE memchr `:6536`; test AFTER walk `:6570`; wrapper `:6556`, `:7233`; re-seed `pf_emit_moved_reseed`; `if (attempt_position >= n) return 0;` for the VM hat | M | ST2 | **REWORDED.** sbscope worded F2/F3 as text pcrec "places inside the kit's guard", which presumes the kit has a guard. Stated as consumer facts (empty-at-n, bound, "if moved, then X"), the kit places them |
| PR-3 | fact | the consumer kind: DFA forward scan / DFA hat / hybrid prefilter / VM attempt seek / ATTEMPT predecessor seek; plus, from pcscope: one start (BOUND `one`), body decides presence (LOCATE `whole`), skipping barred (`use = DISCARD`) | `MF_C_ENGINE` for every PF/MLINE site (`memfn_sites.c`); G2 `req_route_one_attempt` `:7623`; `whole` `:7664`; Q10 collapsed hybrid `:7843` (`use` exists) | M | ST2 (kind), ST3 (rest) | **REWORDED.** sbscope's "reproduces Q-R5 (VM hat keeps a table at \|S\|=1)" names a form; the fact is the kind, the default row reproduces Q-R5. Alternative for the pcscope half: pcrec withholds presence there (Q-WR-4) |
| PR-4 | fact | `need` per span: REQUIRED exactly where dropping, narrowing or answering unconstrained over the span could let a budgeted engine do more work on an input the denied build answers; OPTIONAL elsewhere. Covers pcscope P2 (no-DFA-scan routes incl. framed one-attempt VM per K64) and sbscope F8 (VM hat span 0, no-scan VM pre-check) | `pcrec_artifact_has_dfa_scan` `:469`; gate need at `req_site_define` `:1532` (set-leads lead OPTIONAL on a DFA-scan route, REQUIRED otherwise; every other predicate REQUIRED) | S | ST3 (presence), ST4 (NONE) | OK: a fact about the consumer. D158 is its source |
| PR-5 | fact | presence spans UNPICKED: every necessary-set member as its own one-byte presence span, and the whole run with its mask, each with `need` (not just the pick and the prior-cut window) | pick `req.c:709`; window `req.c:667`; whole run + mask + `whole_maxoff` `req.c:638`; sent today: the pick, the window, and (no-DFA routes only) K65 rest `:1413`, K66 whole `:1112` | M | ST3 | OK. Keep `req_set` asked only where today asks (the `--emit-facts` `used` column, Q-WR-12) |
| PR-6 | fact | offsets relative to the chosen origin: `req_set_maxoff`, `whole_maxoff` as offsets; K as `h_max`; presence `omin` (NEW walk half; 0 is a sound under-estimate) | `req_set_maxoff` `req.c`, `rb_union` `:189`; `req_landmark_maxoff` `req.c`; omin does not exist | M | ST3 (omin 0), ST4 (true omin) | OK |
| PR-7 | fact | each set member's position in pattern order (the order the leftmost/rightmost distinction reads) | `rightmost` in `pcrec_find_set_pick` `findings.c:476` (tiebreak) | S | ST3 | **REWORDED.** pcscope called it "the tiebreak", a pick rule (method). Stated as a per-member order fact; if PR-6's per-member offsets are sent it may be derivable and PR-7 retires |
| PR-8 | change | emission order: the presence verdict is decided before pcrec's context-edge attempt (`(?m)^` at `search_from`/0) | today's order: pre-check at the entry; edge attempt after (`emit_dfa.c:12376` region) | S | ST3 | OK: an obligation on pcrec's text, not a kit statement. Witness W2 |
| PR-9 | change | pcrec's readers of the scan FORM read the kit's define-time result stated as facts (which bytes the scan proves, whether a scan precedes the engine, the includes), not a form name: G1 (`dfa_cand_scan` `:7515`, `req_byte_dominated_by` `:7664`), R4 (`pcrec_dfa_cand_ppm` `:7561`), the handoff K admission (`req_landmark_admits` `:7920`), `landing` L4 (`start_landing_applies` `:8544`), `<string.h>` (`:13485`), the stamps (`dfa_prefilter_name` `:13935`, `REQ_BYTE` `:13659`, `REQ_RUN`, `REQ_WHY` `:13713`, `REQ_HANDOFF` `:13722`), `--emit-facts` `used`/`why`, the trace records, and the `--list-axes` `req-admit`/`req-use` rows. Also: rename the method-named count fact (`DFA_PF_MEMCHR`, `use_memchr`) to the count it is; stamp VALUES stay pcrec row identities | as listed | M | ST1 (shadow), ST2/ST3 (switch) | **REWORDED.** sbscope/pcscope call the result a "form class", which names a method. G1's need ("the scan tests byte b") IS window_contract's PROVEN-facts statement (D161 add. 8); `<string.h>` is R17-a `includes`. Stamp source: pcrec shadow through ST3, then a kit result with identical values |
| PR-10 | change | the PF comment (`pf_comment_memchr` `:6387`, "one memchr() replaces the steps") made method-neutral, or moved to the kit | `:6387` | S | ST2 | OK once neutral. `-fcomments` moves unless the kit renders it (Q-WR-11) |
| PR-11 | control | the claim "every DFA-scan front enforces the necessary set and run" checked as a census over collapsed hybrids, with a planted collapse that drops `rmin` | argument + one probe only (`nfa.c:803`, `:818-821`; W4) | M | ST3 (gates PR-4's OPTIONAL) | not a fact, a pcrec check. Share no source with the walk (learnings §3) |


**Rulings (main's, answer-free, 2026-10-14):** Q-WR-4 withhold presence at ST3; Q-WR-5 handoff (a) first, (b) later behind its own deny; Q-WR-8 ungate `site_kind` for the categorical kinds ST2 reads, and S3 replaces `consumer` rather than dropping it; Q-WR-10 ST2 on main's baseline, R17-b′'s set-site move its own abi event, ST3 after E-1; Q-WR-11 the PF comment method-neutral in pcrec; Q-WR-12 ask `req_set` only where today asks, flip `used` and the deny in the same commit as the row move. Q-WR-7 RULED by Frank (libc-free is future work). **Frank's:** Q-WR-1, Q-WR-2, Q-WR-3, Q-WR-6, Q-WR-9 RULED 2026-10-14 (D161 add. 15, Frank session 112: "agree with 1-5"). State as of 2026-10-16 (kit finding A23, r17b_prime.md rev 3): R-21 TAKEN 2026-10-14; the kit folded it into the R17-b' design note (rev 2, then rev 3 + panel r1 delivered on lane/memfn-fd a8ee399fe); design only, B1 is briefed after B0 merges.

**Amendment (2026-10-16, main, Q-R17P-16; r17b_prime.md rev 3 on lane/memfn-fd a8ee399fe):** PR-3's consumer kind ATTEMPT_PRED is renamed DFA_ATTEMPT and now includes `attempt_entry` as its third caller (with MLINE's seek and the attempt entry's presence). The original PR-3 text above is unchanged.

**Kit work list:** winreq §3 KW-1..KW-13. **Contract:** winreq §4, window_contract.md revisions.

**Sabotage ids:** S964-S980 (17 rows, winreq §7 SW-1..SW-17; allocated 2026-10-14). Every presence-side plant must reach a route with no DFA scan in front.

## R-22 (2026-10-16, pcrec manager) — R-MS6 ([MEASURE-SET] seam addendum): the harness-only arm-entry counter

**Customer:** [MEASURE-SET] M0's REACH floor (docs/design/measure_sets.md revision 3, §4.4 R-MS6 and §8.1; r2 re-check major M7; docs/dev/reviews/2026-10-16-r2-measure-sets-recheck.md). One item, numbered R-MS6 on the main side, an addendum to R-20's R-MS1..R-MS5:

| item | what pcrec needs (facts) | landing bar | needed by |
|---|---|---|---|
| R-MS6 | a count of how many times each dispatch arm the kit emits was ENTERED, reachable only through `build/pcrec-harness` (the reserved internal name prefix and one-global fence of compound.md §A.11), exported under the reserved prefix with the arm's kit row id. The default emission is byte-identical with the lever off | the lever off: zero movers on every emit_sweep arm; the lever on: each fired row's arm counts at least 1 on a kit fixture that enters it, and 0 on one that does not | M0 (§8.1's REACH floor) |

**Sequencing:** with R-MS1, R-MS2, R-MS3 and R-MS5 for M0's trigger (R-20).

**Facts only (D157):** pcrec states that it needs arm REACH counts; how the kit counts is the kit's.

**Sabotage ids:** pcrec-side S983-S990 (allocated 2026-10-16, measure_sets.md §8.5); kit-side ids on request.


## R-23 (2026-10-17, pcrec manager) — `mf_site.body` is a STATED fact: an UNSTATED zero, refused where read

**Customer:** the no-silent-defaults rule (memory pcrec-no-silent-defaults; Frank 2026-10-07) and main's B1+B2 review (b12rev finding 4, lane/int4). Today the common site constructor writes `body = MF_BODY_ONESHOT`, so every builder USES a default, and a future iterator site that forgets `body` would silently inherit one-shot. `need` and `kind` were already turned into UNSTATED zeros in B1+B2; `body` is the last one.

| item | what pcrec needs (facts) | landing bar | needed by |
|---|---|---|---|
| R-23 | `mf_site.body`'s zero value is UNSTATED, and no reader treats it as any body. Every kit reader of `body` REFUSES an UNSTATED site. pcrec's builders state `body` on every site in the same change, so pcrec never sends an unstated one | MF_SITE_ABI 13→14, with its readers found by grep; zero artifact movers on every emit_sweep arm (default and the --memfn arms); a G2/finder fixture that states every body value, and one sabotage row in which an UNSTATED body reaches a reader and must be refused | before the first iterator-state site (the kit's contract order: window, then span-verify, then iterator state) |

**Who edits what:** memfn.h, the kit readers and the fixture are the kit's. pcrec's builder lines (src/gen/memfn_sites.c, emit_dfa.c) may be written by the kit's lane in the same commit, so the field never goes unstated in between; main reviews them at delivery.

**Facts only (D157):** pcrec states which body each site has; how the kit acts on it is the kit's.

**Sabotage ids:** kit-side on request (next free main ledger id S1089).
