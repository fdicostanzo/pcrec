# pcrec-memory-functions — journal

Append-only, dated, newest last. One entry per significant work session
or delivery: what was done, what was measured (both layers, D147, with
box and regime), issues, next steps. Never edit an entry away; correct
it with a later one. pcrec's `docs/dev/dev_journal.md` gets a one-line
pointer when a kit change merges to main.

---

### 2026-10-05 — subtree set up (lane memfnsetup)

- Frank's rulings: D146 (delegation), D147 (layers: the scalar layer is
  live and improvable forever, SIMD is a layer that must beat the
  CURRENT scalar, both layers reported), Q35 (integration.md §8+§14 is
  the design of record), Q36 (in-tree `memfn/`, `pcrec_mf_*` symbols,
  0BSD, extraction on a measured trigger: a stable API over several
  migration steps AND a real second consumer).
- Set up: CLAUDE.md, README.md, LICENSE (0BSD), the ledger pair
  (`requests.md`, `responses.md`), this journal, the session wake
  template, `src/`/`include/`/`tests/` with planned-contents stubs. No
  code and no Makefile wiring: the first code lands with R4a (D77).
- integration.md revised to 4.2 for D147 (the frozen baseline becomes a
  per-step comparator only; the SIMD-off profile is the current scalar
  layer; G1 reads each change against its own deny, in both layers).
- First request filed: R-1, the R4b measurement (T-B twin re-run on
  Linux on the post-handoff build, with a SWAR fused variant).

## 2026-10-05 — integration.md revision 4.3: Frank's rulings folded (lane memfnr43)

- D147 addenda 1-7 folded into integration.md (§R4.3, read first):
  - Q35-Q42 and Q50 ruled; Q51/Q52 rejected.
  - ONE SIMD switch, `-fno-memfn-simd` / `-fmemfn-simd` (axis
    `memfn-simd`), OFF by default until the SIMD hold lifts:
    - OFF = portable C (plain C, SWAR, libc);
    - ON = optimized for a specific CPU, no portability promise;
    - the contents of ON are this kit's per-site choice, cascades
      included (K-6).
  - EVERY search site migrates (Q42 reversed), under a checked site
    manifest (C17, born at R4a, every row `pending`). The memchr
    ratchet ends at 0 outside the kit.
  - The planner moves live at M5; M5′ is the ruled adoption event.
  - Stamps: `MEMFN_FORMS` (Q39 as ruled) plus a `MEMFN_LIBC` record
    (spelling asked as Q53).
- New questions: Q53 (the libc line), Q54 (N7 under completeness), Q55
  (the plan's stamp visibility at SIMD-off).
- R-1's "R4c's trigger" now reads "R4d's trigger": M1 (R4c) is triggered
  by completeness. `requests.md` is the manager's to amend.

## 2026-10-05 — integration.md revision 4.4: addenda 8-9 folded (lane memfnr44)

- Q43 ruled: SIMD-on forms tuned for aarch64 are not ACCEPTED until Frank
  admits Mac measurements as verdict-grade for those cells, or an aarch64
  Linux box exists. x86 Linux gives the verdicts.
- Q44, Q45, Q46, Q48 and Q49 ruled as recommended.
- Q47 refined: the kit's OWN option namespace.
  - pcrec keeps one axis, `-fmemfn-simd`. Kit per-form switches are
    `--memfn=<opt>[,<opt>…]`, passed through uninterpreted.
  - The registry is `memfn/src/options.def` (born empty at R4a), with
    `mf_options()` and `mf_opts_check()`. It replaces `mf_switches()`
    and the generated-axis-rows idea.
  - `--list-axes` prints a `memfn` section from it. A spec-pinned floor
    on the section's member count is the independent control, born with
    the first row (R4d).
- Open questions: Q53-Q55 only.

## 2026-10-05 — first kit session (pcrecdev3): R-1 acked, probe built (lane memfnr4b)

- Branch `lane/memfn-r4b` cut from main d4d9ed90; R-1 acked (766d08eb).
  Main's answers: pin d4d9ed90 (abi 61, post-handoff text); K85's off
  arm is `-fno-req-set-lead` alone (never with `-fno-req-handoff`); the
  Linux verdict runs through main's executor at the first quiet slot.
- Lane memfnr4b (opus) delivered, reviewed and merged:
  - `emit` copied byte-exact from d4d9ed90 (gates_sync.sh re-checks it);
  - new portable `swar` fused pair-filter, with a written in-bounds argument;
  - lead-first variants `swlf`/`ffllf`;
  - correctness: 0 wrong, 10/10 planted defects caught, over 6 builds.
- Mac readings (DIRECTIONAL ONLY):
  - SIMD-off: `swar` beats `emit` far past the floor on union-select
    and mod-i. On userpass `swar` loses per call, because the new
    memchr('=') lead rejects first there; lead-first `swlf` is null or
    a win.
  - SIMD-on: `ffl` wins or ties against `swar` except on userpass's
    lead-absent rows.
  - K85 cls-n-uc: the fused forms remove the dense-text loss (swlf 175k
    vs nosl 565k ns per 1m sweep).
- §15.5 proposal (report §6): the lead order is a kit per-site choice,
  lead-first by default; a "lead can reject" density fact would decide
  it. To fold into integration.md after the Linux read.
- OWED: the Linux verdict, `docs/design/memfn/probes/lxrun/memfn_r4b.sh`
  (~20-25 min, cap 120, last line `R4B-DONE status=<n> dir=<OUTDIR>`),
  run by main's executor. Then R-1's `done:`.

## 2026-10-05 — Frank (direct): be suspicious of tuning constants

- Asked why `swar`'s hot loop is 16 bytes (2x) and not 32. Answer: an
  UNMEASURED default, inherited from `ffl`'s 2xVW shape; the lane
  measured no unroll ladder.
- Frank's direction (nothing to do now, this early): note it as an
  unmeasured default; he dislikes hand-tuned numbers like that. Prefer a
  formulation where the compiler picks the unroll (e.g. a simple loop
  gcc unrolls and schedules itself) over a fixed constant. In general,
  every such constant in kit forms (unroll widths, block sizes, short-span
  cut-overs, thresholds) is suspect: it is either measured, with its
  regime named, or derived, or left to the compiler. Never adopted
  silently.
- Recorded: comment at the loop in tb_r4b.c; responses.md N-1 for main.

## 2026-10-05 — R-1 done: Linux verdict read

- First Linux attempt aborted at step 4: a LeakSanitizer finding in the
  harness. Fixed in 4ecea50b; the re-run was green (R4B-DONE status=0,
  main's executor, OUTDIR scratch_lx/r4b2). Transcripts are archived
  under probes/out/twins/r4b/linux/; report §9 has the read.
- R4d's trigger is MET on union-select: `swar` beats `emit` in both
  regimes, 1.4-2.0x. userpass needs lead-first. K85's find-all loss is
  cured by the fused forms. SIMD-on: `ffl` beats `swar` except at 16 B
  on AVX2.
- `done:` posted. Next: main reviews the branch. R4a (code skeleton)
  needs a request from main before it starts. The §15.5 revision (lead
  order as a kit choice) is a design deliverable after the review.

## 2026-10-05 — R-1 merged (main 08caf4a3); R-2 taken

- Main merged lane/memfn-r4b and filed N-1 as D149 (applies to pcrec and
  the kit). Landing note from main: a lane's report must be added to
  docs/dev/lanes/CLAUDE.md in the same change. Every kit lane brief now
  says so.
- R-2 acked on lane/memfn-r45: rev 4.5, a light panel, Q53-Q55.

## 2026-10-05 — R-2 done: rev 4.5, panel r5, rev 4.6

- Rev 4.5 (lane memfnr45) folded R-1 and D149. The kit session answered
  the fold's four open points (§R4.5.5): wait 2 MET; the early-hit gate
  call is a Q48 candidate, judged at R4d's G1; the lead order is part of
  R4d's one form; old blocks stay history.
- Panel r5 (critic A opus, contract vs emitters; critic B sonnet, stamps
  and Q55) found 1 BLOCKER and 9 MAJOR; 23 of 23 were accepted.
  - The blocker sat in rev 4's contract: on no-DFA routes the set-leads
    lead is REQUIRED (K65), so a kit arm that dropped it would turn
    NOMATCH into a step give-up. R-1's cells are all DFA-route.
- Rev 4.6 (lane memfnr46, opus) applied all 23.
- Q53-Q55 recommendations posted in responses.md (R-2 done:).
- Lesson: two critics' final messages truncated mid-finding. Brief
  critics to write their findings to a scratchpad file and reply with
  the path.

## 2026-10-05 — R-3 taken (R4a lanes memfnskel, memfnmanifest)

- Frank ruled Q53-Q55 as recommended (D147 addendum 10). R-3 filed: R4a
  (zero movers), then R4a′ (the stamps' abi event; its number is agreed
  with main first because of START-SET's events).
- OWED (design text): integration.md still writes B4/B5 (the libc
  record) and B6 (N7's scope) as Q53/Q54 PROPOSALS, with Q53-Q55 open.
  Mark them RULED (addendum 10) and promote them to the design of
  record. This rides R4a′'s branch, which builds the libc line.

## 2026-10-05 — R4a: sabotage ids renumbered (S478-S480 → S510-S512)

- START-SET (D148) reserved S478-S504, and the manifest lane had taken
  S478-S480 off main's highest. Renumbered to S510-S512 from the kit's
  block S510-S529, which main assigned. Solo mech re-runs: all three
  DETECTED, reach ok, 0 anomalies.
- RULE from main: sabotage ids AND abi numbers serialize through the
  pcrec manager. The kit's next free id is S513, and its block ends at
  S529; ask main for the next block. Never take "main's highest + 1"
  again; a reservation in a design doc does not show in the highest id.

## 2026-10-05 — R4a: G2 (blinded) found three kit defects; fix lane memfnfix

- G2 (lane memfng2, opus, D27 cell) rendered 4,011 generated sites and ran
  ~137M checks against its own byte-loop reference, compiled with gcc,
  clang and ASan. It found three defects the skeleton's own smoke test
  missed:
  - F1: VERIFY ignored its empty range. That is an answer defect, and an
    over-read at lo > n.
  - F2: ON_CAND+NOP was refused (totality).
  - F3: out-of-enum `empty`/`need` were rendered instead of refused.
  No pcrec customer reaches them today (the kit is not called), but a
  later VERIFY site with end_back or a negative offset would hit F1.
- Kit contract rulings on Q-G2-1..17 (the kit's, under D146), recorded in
  the memfnfix brief. They go into integration.md §R4.7.
  - Refused outright: NOP on value forms, MISS on ADVANCE, SKIP sets at
    offset ≠ 0, empty conjunctions, zero-length runs, reverse
    ALL_PRESENT, run bytes outside their mask, and `guard_by_caller`
    beyond EXPR VERIFY at offsets ≥ 0.
  - Q-G2-5 (reverse ADVANCE) stays open until M3.
- G2 merged as the blinded author's commit. The fix lane may not edit
  g2/ (it is the control); it only adds `--quick` for the `make test`
  section.
- OWED: G2 coverage of the newly refused shapes, from a blinded author
  later. The cell worktree under worktrees/memfn/worktrees/memfng2 and
  the cell copy are left in place; removal needs a worktree rm.
- Lesson: the blinded author found in one pass what the implementing
  lane's 480k-check smoke test missed. That smoke test was written by
  the implementer, so it shared the implementer's reading of "range".

## 2026-10-05 — R4a delivered (zero movers; Mac make test green but for a pre-existing darwin red)

- Merged memfnfix (G2 green), then main f3c726d7 (START-SET 0+1). C17
  caught START-SET's FIND extraction on the merge: the PF row was
  re-pointed to `pcrec_emit_find`, and the vocabulary learned the
  format-hole walk (`walk-fmt`), which it could not see. That was the
  check working on its first real refactor.
- Landing run (Mac suite lock, detached): sweep 0 artifact movers vs
  main; make test 52/52, red only on run_inline_capability (darwin nm,
  pre-existing). R-3 R4a `done:` posted.
