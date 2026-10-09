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
