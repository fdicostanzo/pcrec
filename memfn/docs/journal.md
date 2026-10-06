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

## 2026-10-05 — R4a′ built except the abi bump (lane memfnstamp, merged into lane/memfn-r4a2)

- Both stamp lines are on every artifact, after `<PREFIX>_RUN_WORDS`.
  pcrec's finishing pass (`src/gen/memfn_stamps.c`) inventories the
  whole artifact's libc calls, and the kit renders the lines through
  `mf_stamps`.
- C11, `make test-memfn-stamps`: 918 artifacts, 0 failed, ~35 s. Its
  control is `nm -u` of an `-O0 -fno-builtin` compile; the idiom
  exclusion goes through a compiler prelude and shares no list with the
  producer. The FORMS half is UNREACHED.
- S513-S517 all DETECTED. Spec hunk: match_api §6.3.
- Census vs 090020a2: every artifact moved by exactly the two lines,
  with one reviewed extra. `RX_VM_PREFILTER_WHY` on
  uprops/size_ladder_prefilter_drop quotes the measured size of the
  discarded hybrid attempt, 1028494 → 1028553. No test pins it; the
  classifier names it. Main must see it.
- Re-pins: m5_stage1_stamps (12), the resource pin 762665, the
  recursion-identity FILEPIN.
- WAITING: START-SET stage 2 (abi 62) to merge to main. Then: merge main
  ALONE, then the bump to 63 + grep-found re-pins as the LAST commit
  (memfnstamp_report.md §8 is the procedure), the census with `--abi
  62:63`, and the Linux make test via main's executor by day. Main reset
  its context at 2026-10-05 ~23:00; its wake.md records this.

## 2026-10-05 — worktree cleanup (Frank OK'd)

- Main's wtprune (23:19) had already removed the merged kit lanes, so no
  --apply was needed. memfnstamp waits for R4a′ on main. The nested G2
  worktree + cell can't be managed by wtprune; that is with main.
  Lesson: mk_d27_cell.sh run from inside worktrees/memfn nests the cell
  there.

## 2026-10-05 — lesson: D27 cells must not nest (main agrees)

- Running `scripts/mk_d27_cell.sh` from inside worktrees/memfn nested the
  G2 worktree and cell there. wtprune refuses nested worktrees, so a raw
  removal (Frank's, on his morning list) is needed.
- The script cuts the cell from HEAD of the tree it is run in. So running
  it from the main tree tests MAIN, not unmerged kit code. Rule for the
  next kit cell:
  - if the code under test is already on main, run it from the main
    tree;
  - if it is only on the kit branch, ask main for a base-ref option on
    mk_d27_cell.sh (cell from `lane/memfn-*`, placed directly under
    worktrees/) before briefing the author.
  Never nest.
- main removed memfn-r4b2-results (byte-identical to the archived
  probes/out/twins/r4b/linux/).

## 2026-10-06 — box rule: lanes' long runs take the Mac suite lock

- The pcrec manager's rule: a kit lane's recursion-identity or any
  multi-section run takes worktrees/.mac-suite.lock (directory form,
  owner file) and releases it on exit. Other lanes (ssbuild3, ARTREV
  timing) wait on it. My briefs had said "do NOT take the lock", which was
  wrong for long runs. memfnbump was corrected mid-run. From now on every
  kit brief says: single quick sections need no lock; long or
  multi-section runs take it.

## 2026-10-06 — R4a′ complete on the Mac; Linux verdict owed

- memfnbump merged (49ace440).
  - Commit 1 re-measured the pins on the merged tree: m5 ×12, the
    resource pin 762697, the FILEPIN, and run_size_term's cap
    31,900→32,300. That witness had lost its headroom to the stamps
    since UTF-VALID; the cap was bisected and derived (D149).
  - The abi bump 62→63 is the last code commit, with every reader found
    by six greps, and a FILEPIN self-pin after it.
- Census vs 57db5152: CLEAN pre- and post-bump (two lines + the abi
  digit + the one named VM_PREFILTER_WHY value).
- Mac suites green except the darwin nm red. recursion-identity 16/0.
  S513-S517 DETECTED.
- Collision recorded: memfnbump's chain ran without the suite lock while
  ssbuild3 held it (my brief's fault). Correctness-only; main ruled to
  let it finish.
- OWED: Linux make test via main's executor (by day), with the census
  on Linux too. Then the R4a′ done:.

## 2026-10-06 — first kit session ends (context reset at Frank's request)

- Delivered this session:
  - R-1, the fused scan+verify probe; Linux verdict: R4d's trigger is
    MET on union-select;
  - R-2: integration.md rev 4.5→4.6, panel r5 with one blocker fixed,
    and Q53-Q55, now ruled as D147 addendum 10;
  - R-3 part 1, R4a: the kit skeleton, manifest + C17, the blinded G2
    (F1-F3 found and fixed), rev 4.7 — all on main;
  - R-3 part 2, R4a′: the stamps' abi event (abi 63), complete on the
    Mac and awaiting main's morning Linux make test.
- Lessons kept:
  - blinded authors find what implementers' smoke tests miss (G2);
  - checks catch refactors on their first merge (C17 on START-SET's FIND);
  - sabotage ids and abi numbers serialize through main;
  - long lane runs take the Mac suite lock;
  - never nest a D27 cell;
  - critics write their findings to a file;
  - Frank: tuning constants are suspect (D149).
- The next session wakes from memfn/docs/wake.md (current as of
  eef95511) and waits for main's Linux results to post R4a′'s done:.

## 2026-10-06 — R4a′ closed

- Main landed R4a′ as abi 63 (340d8fef). The Linux run was 53/53, with
  one check-side red fixed on main (enctri). The census was clean.
  START-SET stage 3 then took abi 64 on top.
- Posted R4a′'s `done:` in responses.md (R-3 closed). Pruned
  memfnstamp/memfnbump via `scripts/wtprune`. Rewrote wake.md.
- Branch `lane/memfn-ledger` from main c9c98e98, ledger commits only.
- Waiting: R-4 (R4c, the M1 migration), which main is sequencing with
  Frank against the start-table refactor (shared emit_dfa.c
  offset-skip/PRE sites). No R4c code before R-4 is filed.

## 2026-10-06 — R-4 (R4c) taken up

- R-4 filed on main at 05c33ce0. Branch `lane/memfn-r4c` cut from main
  691a8b7c; ack d836eb17.
- A read-only opus scoping pass wrote worktrees/r4cscope-scratch/scope.md:
  - the sites can be expressed in MF_VOCAB 2;
  - 18 boundary reads (B1-B18);
  - 20 mech rows, not ~28;
  - C4/C5/C10/C12/C13/C14/I1 do not exist yet;
  - the memfn-simd pair does not exist (it is caller-observable);
  - C17's dynamic half keys on a dead name;
  - I2 needs main's C0.
- Manager calls on Q2-Q13 are in rulings.md beside it. Q1 (pcrec's MIT
  text moved into the 0BSD kit) went to Frank via main, recommending he
  relicense it as 0BSD. It gates merging CORE into the branch.
- Lanes running: r4ccore (opus, implement→replace), r4caxis (sonnet,
  the inert memfn-simd pair), r4cchecks (sonnet, C4/C12/C13/C14, C17
  re-key, VM-hybrid witness). Heavy runs are held for a slot from main.

## 2026-10-06 — R4c: AXIS + CHECKS merged; CORE IMPLEMENT green; Q-G2-18 chosen

- Merged into lane/memfn-r4c: r4caxis (the inert memfn-simd pair, registry
  pin 205, a stream-5 listing mover only) and r4cchecks (C4, C12-C14, the
  C17 re-key + census, the VM-hybrid witness; S518-S529, which used up the
  block). make strict is clean, and the new sections are green on the merge.
- Frank ruled Q1 YES as D145 addendum 1 (main 07573ff7): pcrec text
  moved into the kit is relicensed 0BSD.
- CORE IMPLEMENT (lane/r4ccore 66176e35): 0 movers on all 5 streams
  with the I1 shadow live. I1 is also clean at -fcomments, both
  engines, -e utf8 and the 8 M1 denies. Q10: no define-without-use.
- Q-G2-18, CHOSEN by the kit manager: the precheck arm needs on_miss to
  leave the site. pcrec STATES it (`mf_site.on_miss_leaves`; MF_SITE_ABI
  2→3) and the kit never parses hook text. CORE's interim
  jump-keyword sniff is retired. G2 coverage is OWED.

## 2026-10-06 — R4c integrated on lane/memfn-r4c; heavy runs next

- CORE delivered IMPLEMENT + REPLACE (zero movers) but never read three
  manager messages that arrived while it was busy (the HOLD/LIFT-by-
  artifact lesson, again). A fresh FIX lane applied them from the brief:
  - it merged AXIS/CHECKS;
  - ONE policy derivation;
  - D145 add. 1 provenance;
  - C12 memchr 8→2;
  - C17 LIVE on the real corpus (103 renders, the `pcrec_memfn_define`
    door accounted);
  - stale S524/S528 re-aimed;
  - Q-G2-18 (`on_miss_leaves`, MF_SITE_ABI 2→3, a predicate column of the
    arm table, the text sniff deleted);
  - rxtsource re-pinned for CHECKS's handoff.rxt growth (+278 PASS).
- Merged lane/r4cfix, then main (docs only since 691a8b7c). make strict
  is clean. emit_sweep at FIX: streams 1-4 0 movers; stream 5 only the two
  declared memfn-simd rows.
- OWED, in the slot main names (after flagbits, ~20:45Z): Mac make test,
  then the sabotage matrix (CORE's 23 rows + S518-S529); then the pinned
  Linux script; I2 over every axis × both tiers after main's C0.

## 2026-10-06 (evening) — R4c Mac verdict; Linux run handed to main

- Merged main at e6e6d6eb (flagbits K92, abi 65). One conflict: main's
  DERIVED strategy mask subsumes AXIS's hand-added memfn-simd bits. The
  zero-mover gate vs e6e6d6eb is clean; the only dump mover is the
  declared --list-axes pair.
- Mac make test at 00ede5dc: 58/58 ran, 6202 s. ONE red, test-startset
  [vm-movers]: CHECKS's handoff.rxt witness rows enrolled 9 start-set VM
  movers in main's manifests. lane r4cpin re-pinned them via the
  census generator; test-startset is green alone.
  Main's per-row facts are in r4cfix_report §10.1: identical at
  e6e6d6eb, and the same 24-line seek diff as the existing rows.
  LESSON: corpus rows enroll in other suites' manifests (rxtsource,
  startset), so a lane adding corpus rows owes the full make test.
- FINDING (mine): run_sabotage_matrix.sh takes ONE id per call. My
  35-id call ran only S464 (DETECTED), and the chain still printed
  status=0. I caught it only from the trailer's "1 rows". I sent main a
  backlog note that the matrix should refuse extra args.
- Each mech row is ~10 min of full harness, so I stopped the Mac
  per-row loop and released the lock at 22:20Z. All 35 rows go to Linux.
- Merged main again (C0, d96f8cd3; no src/). Committed the pinned
  Linux script + gate judge (91f5b607), with I2 over every flag x both
  tiers. Main runs it tonight on ubuntubudu.
