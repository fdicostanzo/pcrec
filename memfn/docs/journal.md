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

## 2026-10-07 — R4c merged to main; R4c′ queued; session reset (Frank)

- Linux verdict for R4c:
  - 91f5b607: red. Every red was check-side, environment or harness;
    there were zero movers on every I2 arm.
  - abae07fa: I2 17/17 green; C4 red again (FP_FAST_FMA*).
  - 5645a37a: green. C4 now plants the COMMITTED ubuntubudu gcc 15.2
    population on every run; the old rule reproduces the box's failure
    exactly on the Mac.
- Total coverage: gate, make test, 35 mech rows, 94 I2 arms, the axes
  pair, C11.
- Main merged R4c (81bc13de, abi 65). Its review: MERGE-READY WITH LISTED
  FIXES. Those are R4c′ (responses.md R-4 note 2026-10-07):
  - (a)+(b) re-pin B1-B18 and add two decision reads; these gate main's C1;
  - (c) to (g) and the nits.
  - None moves a byte.
- Fixes along the way:
  - the memfnarch rows were vacuous on Linux (they now require a clean C4
    first);
  - the memfn-simd pair is back in I2 as per-side-DIFFER inertness arms;
  - the matrix runs one id per call;
  - S526 is two-site;
  - S527's desc tripped the trailer grep.
- I dropped my own Linux artifact_size_log.tsv commit (no precedent; the
  baseline is the Mac's).
- LESSONS:
  - check a regex against the target box's REAL compiler population, not
    the dev box's proxy. It failed twice before the dumps were committed;
  - a rerun is cheaper than a full run when the script can select steps;
    build that in from the start.
- Frank asked for a clean session reset. R4c′ is NOT started: branch
  lane/memfn-r4c2 is cut, and its lane worktree r4c2fix is empty.

## 2026-10-07 — R4c′ in flight; R-5 (M1b) scoped, kit rulings Q-M1b-1..8

- R4c′ (lane r4c2fix, opus) is running on lane/r4c2fix. Its (a)+(b)
  commit, 4f2b401f, went to main for C1. In it, r4ccore §3's B1-B18 are
  re-pinned at 81bc13de, with B19 (the req_run len>=2 guard, :1517) and
  B20 (ofs_pred_of's need classification, :1083-1107) added. Sabotage
  ids: S566-S569 for R4c′, S570-S579 for M1b (main, 2026-10-07).
- R-5 filed (adf2644b) and acked (110f0490). The read-only scoping pass
  m1bscope ran against main 54c42e36; its scratch output is
  worktrees/m1bscope-scratch/m1b_scope.md. It found NO STOP: rc_row_of
  reads only the run and bit 43, a form deny. Start-decision reads
  D1-D12 all stay pcrec-side on lines M1b doesn't edit.
- FINDING: integration.md §14.8 is wrong to say RUN_WORDS via
  `sink->stamp` is byte-identical. pcrec's sink quotes
  (memfn_stamps.c:189 → sb.c:366), so every artifact would get
  `RX_RUN_WORDS "0"`, a caller-visible type change. This is fixed in the
  contract (M1b commit 0) before any code.
- Kit rulings (mine; recommendations taken):
  - Q-M1b-1: yes, fill mf_art_begin's denies from the same map table,
    and the kit asserts that site.denies == art.denies;
  - Q-M1b-2: (i) a new `stamp_int` sink op, APPENDED at the end of
    mf_sink (G2 builds its sink positionally);
  - Q-M1b-3: yes, a kit row accessor (the mf_options() precedent), so
    --list-axes stream 5 stays byte-identical;
  - Q-M1b-4: S285 goes kit-side, onto the renderer's read of run_len;
  - Q-M1b-5: a VMRUN site's `empty` is EXCLUDED;
  - Q-M1b-7: retire mf_hooks.run_cmp outright, together with `note`'s
    helper role, in ONE MF_SITE_ABI 3→4 bump; MF_VOCAB stays 2. This is
    kit-internal and no pcrec abi event (zero movers);
  - Q-M1b-8: S570-S579 (10 ids) is enough for the ~4 rows expected.
- Q-M1b-6 (VERIFY as a DELEG_SITES row, or carried as an OFS/PRE term
  like SETREST) is MAIN's call, since DELEG_SITES belongs to main. It
  went to main with "carried" recommended.
- M1b waits for R4c′ to merge; its branch is then lane/memfn-m1b, cut
  from that main.
- Main ruled Q-M1b-6 (2026-10-07): VERIFY is CARRIED as a term of
  OFS/PRE (the SETREST precedent), with no DELEG_SITES row of its own;
  VMRUN gets its own row (D91). Main also accepted: commit 0's contract
  fix (stamp_int, MF_SITE_ABI 3→4), C12 12→9, and the re-point count of
  6 with S514/S516/S528 checked. Overlap rule: M1b and START-TABLE
  C3/C4 share pcrec_emit_prologue on disjoint lines, so whichever
  merges second merges main ALONE and re-runs its zero-mover gate. The
  M1b report keeps the D1-D12 restatement (stc1 cross-checks it).
- R4c′ merged into lane/memfn-r4c2 (ab61b0db; make strict green). It
  covers r4c2fix's (a)-(g) + nits (fa676374) and r4c2fu's follow-ups:
  S530 renumbered to S566 (the block is S566-S569); S526's file-scope
  `_Static_assert` anchor taught to sabotage_anchors.py (main asked:
  the resolver exited 2 on main); and a Linux wrapper,
  lxrun/memfn_r4c2.sh, built on memfn_r4c.sh's RERUN mode with the new
  GATEFLAGS. The Mac validation chain DIED at 01:26: stopping the lane
  killed its "detached" nohup chain (lesson recorded in memory). Main
  routed the re-run to the Linux executor (gate --zero-dumps vs 81bc13de
  + mech S511 S524 S525 S566 S526); it is OWED, with completion line
  `== r4c2-lx DONE rc=N ==`. Finding sent to main: stc1's committed
  call_graph.txt is stale (IndexError).

## 2026-10-07 (morning) — R4c closed; M1b built, Linux verdict owed

- R4c′ Linux-green at ab61b0db (294 s: gate 0 movers; S511 S524 S525
  S526 S566 clean). Main merged it as 993f8c1d. R4c's done: is posted
  (aa7b82b1).
- M1b (R-5) on lane/memfn-m1b, cut from 993f8c1d, built by lane m1b
  (opus):
  - commits: CONTRACT d8b3fbf0 (integration.md rev 4.8, §R4.8, §14.8
    corrected), IMPLEMENT d14e7df3 (memfn/src/runcmp.c, stamp_int,
    MF_SITE_ABI 4, the deny map, I1), REPLACE 199b2ded (src/gen/runcmp.c
    deleted; VMRUN delegated; VERIFY carried; C12 12→9; C5 28 rows);
  - Mac: 35,980 compiles with 0 movers at both IMPLEMENT and REPLACE;
    the list streams byte-identical;
  - mech: 7 re-anchored (S454 added, for the dead `pidx` param), 3
    adjacent checked, S570-S573 new, every row hand-planted;
  - D1-D12 restated at the tip (report §3).
- Kit decisions the lane made, accepted in review:
  - `cstr` writes the BODY of a literal (the quotes are the kit's); G2's
    stub sink was aligned to it;
  - MF_CMT_NONESSENTIAL is a kit constant that pcrec asserts equal to
    its own;
  - G2 draws its deny per batch.
- Review notes:
  - the lane's I1 sweep went far past the brief's "handful" while
    k93tri held the box; I told main;
  - three commit subjects keep a WIP prefix.
- Verdict OWED: the Linux run lxrun/memfn_m1b.sh (5-8 h estimated:
  make test, gate, 14 mech rows, axes, C11, all I2 arms); completion
  line `== m1b-lx DONE rc=N ==`. The Mac make test goes on a slot main
  names.
- 2026-10-07, later morning:
  - The Mac make test at 20b9d3cb had ONE red, test-memfn-g2, with a
    two-layer cause:
    - (a) G2's h_note stub wrote bare text where the contract asks for a
      comment, fixed at 6467f6a2;
    - (b) a kit defect: R4c's ofsskip arm accepted sites whose `miss` is
      not `n` or that state a `floor` (G2 sites 1682 and 2587; 11
      under-read faults below the floor).
  - (b) is an unstated precondition, latent on main since 81bc13de and
    unreachable from pcrec. Lane m1bfix fixed it: the arm declines to the
    generic row and the use side refuses loudly. Proof: 200 compiles with
    0 differing; G2/arms/forms/manifest green. It is merged into the
    branch. Main files it as K96 at the M1b merge.
  - The Mac gate vs e947b406 PASSED with 0 movers on all six streams.
  - The Linux full verdict at 5f0f4dca is green apart from G2 (the same
    known cause). Main re-runs G2 alone on Linux at the fixed tip.
  - OWED (kit), K35-type gaps, both to be closed with a blinded G2
    extension:
    - G2 reaches neither ofsskip (0 sites after the fix) nor precheck
      (it never sets on_miss_leaves), nor runcmp's words row;
    - Q-G2-6's floor scope (general or SKIP/ON_CAND-only) needs my ruling.
  - Lesson: the m1bfix lane's detached chain was checked to be truly
    detached (ppid 1, own pgid) before I stopped the lane, and it
    survived.

## 2026-10-07 (late morning) — M1b merged; G2 reach extension started

- Main merged M1b as 1c037dce (Linux g2 green at 0125aeb5) and filed
  K96. The R-5 done: is posted on lane/memfn-g2x.
- Main's sequencing: no next migration until main names it. [START-TABLE]
  C2 merges first, then main picks between R4g and C3 by remodel
  overlap.
- Q-G2-6 re-read: it is already RULED general (memfn.h `floor`). Site
  2587's under-reads came from an out-of-contract G2 input; its wrong miss
  was a genuine kit defect (K96). The ofsskip arm now declines ANY stated
  floor. That is conservative; relax it only on a measured need (D77).
- Blinded lane g2x (opus) works in the D27 cell worktrees/g2x-cell
  (worktree g2x, branch g2x, from main 92ca17fc). Its allowlist matches
  memfng2's. The brief is written in contract terms only and names no arm.
  It closes the K35 gap and adds per-shape rendered counts as a floor;
  G2 becomes a conforming caller under Q-G2-6.
- Next, non-blinded, after g2x: a per-ARM reach census of G2's sites
  (ofsskip / precheck / runcmp rows) with literal floors. This is the
  independent check that the shapes reach the arms.

## 2026-10-07 (midday) — [MEMFN-ROWCON] opened (Frank)

- Frank, after K96: "the general learning then is to check rows'
  contracts". He liked the proposal (a per-row allowlist of honoured
  fields, a shared gate that declines everything else, a field × row
  audit, every row reached) and asked for: create an item, a light
  design, then a critic pass. His concerns: VISIBILITY into decisions;
  are ALL ROWS REACHABLE by at least one pattern; is the LOGIC SOUND.
- Item: [MEMFN-ROWCON]. A plan row was requested of main (responses.md
  notice).
- Step 1: a read-only sonnet audit (lane rowaudit) builds the
  rows/selection map, the field × row matrix (H/D/R/I), the
  disagreements, and today's visibility and reachability. Output:
  worktrees/rowcon-scratch/audit.md.
- Step 2: a light design, docs/design/memfn/row_contracts.md (mine).
  Step 3: a D6 panel with one lens each: visibility, reachability,
  logic soundness, contract/docs.
- Also: K94 (main ab6e0f8a) added defs_bref_ci_ucp as an N7-pending
  instance. M7's scope grows by 1; the C12 span-index ceiling is now 3.
- Frank, 2026-10-07 (ROWCON design constraint): "we are moving decisions
  into memfn in the future, so either do it then or expect to migrate."
  Consequence: the visibility/explain mechanism is KIT-OWNED. It is a
  decision record the kit keeps per art and site, with rows evaluated,
  the verdict and the failing field, read through a kit API. It is not a
  pcrec-side trace hook now. Its record shape must be the one pcrec's
  start decisions (C1's PCREC_CAND_TRACE site-key records) can migrate
  INTO when the planner moves into the kit (M5). The default is no R-6;
  a pcrec-side piece is requested only if the design proves it can't
  wait, and then it is marked as migrating.
- Frank, 2026-10-07 (ROWCON scope): "if there is a general mechanism
  pcrec can use for its other tables, I'd like to see that rather than a
  one-off. It might be partially generalized." The design must therefore
  offer ROWCON's parts (row contract/allowlist gate, decision record,
  per-row reach floor) as a GENERAL table mechanism that pcrec's
  first-match tables (dfa_pfs[]/DFA_SELECT, the start table, ...) can
  adopt, within the kit boundary (the kit links nothing from src/ and
  stays extractable). The audit gained §7: pcrec's tables, prior
  unification designs, and boundary implications.

## 2026-10-07 (afternoon) — ROWCON rev 2/2.1; Q-ROW-1 ruled by Frank

- Main relayed Frank: design the engine against pcrec's decision tables
  as REFERENCE CUSTOMERS. Lane rowcust gathered six customers
  (probes/rowcon/customers.md). Rev 2 (e5f5c0c0) has two layers:
  - a generic engine (stride rows with an mf_row head; scope/route
    filters; deny; a pluggable gate; on_none policy; a decision record
    mapping onto C1's trace; MF_TRACE reach; a listing accessor);
  - the kit profile.

  cand_rows[] is hosted on paper (Appendix A). analyses[] (an
  AND-reduction) and POSS-CTX (indexed dispatch) are declared
  NOT hosted.
- Frank RULED Q-ROW-1, differently from my recommendation:
  - NO SILENT DEFAULTS. "These are bugs waiting to happen …
    assumptions that may be forgotten … not seen until circumstances line
    up." Every value a row reads is stated explicitly (named tokens such
    as MF_MISS_N); unstated means a loud refusal. pcrec states its values
    via R-6 (zero movers).
  - Caller text, option B: SNAPSHOT each value hook once into a reserved
    `mf_` local, inside parentheses. Plus refusals for comments, `#` and
    backslash, and for an on_miss/on_cand that is not a jump or a braced
    block. Frank: B "also handles the case of function calls called
    twice". It is an ABI EVENT at every delegated site (T3b): G1 at both
    layers, deny --memfn=no-snapshot.
- Rev 2.1 folds both. Q-ROW-4 (charter) is still pending. Next: the re-check
  panel, with a pcrec-customer lens.
- Memory: pcrec-no-silent-defaults.
- Frank RULED (2026-10-07, directly):
  - Q-ROW-4 AGREE: the kit hosts the general first-match table engine
    as a kit utility under MF_NS (D146's charter is widened);
  - Q-ROW-6 AGREE: the hook snapshot carries NO public deny, and G1's
    comparator is the pre-snapshot commit (a D144 item-4 exception for a
    correctness change);
  - Q-ROW-5, answered by a CLARIFICATION: "my concern about defaults was
    that they would be USED … if it's unused, as in a wildcard, then that
    isn't important. I don't want to specify everything for the sake of
    it." So a row may use only a value the caller STATED; unstated fields
    are wildcards; a row that needs an unstated field DECLINES, and if no
    row can serve, the kit refuses and names the field. There is no
    blanket stated-bitmask: an enum a row uses gets an UNSTATED = 0
    member, and per-kind obligations stay required. The r2 review
    (fa334f08) closes; rev 3 follows.
- SCOPE RULING (Frank via main, 2026-10-07): narrow [MEMFN-ROWCON]. "I
  don't want this to turn into a solution without problem scenario."
  - BUILD NOW, the K96 generalization only:
    - per-row allowlists of the fields each row USES/serves;
    - one shared gate that declines everything else;
    - decline reasons in the kit's own trace;
    - per-row reach floors;
    - the narrowed stated-value rule (R-6 stays small).
  - HOLD, filed:
    - (a) the general table engine. The charter stays ruled, and it is
      built when a real table wants it. The cand_rows paper mapping
      stays only as no-corner evidence; the rev-2 customer framing is
      design input only.
    - (b) SNAPSHOT. Its trigger is a measured hazard. A cheap census of
      pcrec's actual hook texts runs first (lane hookcensus). If none
      are risky, SNAPSHOT stays filed with the census as its "not yet"
      evidence; if one is, the case goes to Frank.
  - The next panel is LIGHT: a one-critic re-check of the narrowed gate.
    Rev 4 rescopes the design.

## 2026-10-07 (afternoon) — [MEMFN-ROWCON] N1 built (lane rowconn1)

- fields.def (39 fields, 37 classes) + gate.c: rules 1-3 of row_contracts.md
  §2 as `gate_check`, run in WARN mode in the arm walk (define), the use
  re-check (every mf_use / mf_call) and the run-compare walk; verdicts
  recorded on site_rec / mf_art, no selection changed, nothing refused.
- `uses`/`serves` declared on all 8 rows, each with its citation, at the end
  of the row's own file. MF_TRACE (off by default) writes MFTRACE
  SEL/ROW/END records and REACH counters (docs/trace_format.md).
- Trace demo: the only would-declines on pcrec sites are the unstated `miss`
  (rule 1) at ofsskip define and use and at precheck's ASSIGN use: R-6's
  predicted items. The C5 decline fixtures show the general gate reaching
  K96's two declines (`miss:R2:OTHER`, `floor:R2:OTHER`) on its own.
- Choices for review (lane report §5): uses excludes contract-defaulted and
  shape-dependent reads; precheck serves BRACED; on_cand classes {OTHER};
  a third phase `run`; memfn.h sentences deferred to N3.

## 2026-10-07 (late afternoon) — ROWCON narrowed (rev 4/4.1), N1 merged

- Rev 4 (d0dd3f5e) narrowed per Frank. The hook census found NO RISKY
  HOOK, so SNAPSHOT stays filed (97f9f8c7). The light re-check (opus)
  produced rev 4.1 (f7647b9e):
  - the gate runs at both phases;
  - IDENT/JUMP text classes close S2-S7 with no snapshot;
  - a semantic differential;
  - N3's entry re-census;
  - the UNSTATED bump is cut.
- N1 (lane rowconn1, opus, 3dea08c8) is merged into lane/memfn-rowcon:
  - fields.def (39 fields), uses/serves on all 8 rows with citations,
    and the WARN gate at define/use/run;
  - MF_TRACE + trace_format.md.
  - Validation, Mac, under the lock 14:42-14:51: build, strict, g2,
    arms, forms, manifest, stamps, link and strict_trace are all rc 0;
    the gate vs 92ca17fc is R4C-GATE PASS (--zero-dumps), 0 movers on
    all six streams.
- Would-decline preview: 3 cells, all `miss` unstated (ofsskip at
  define and use; precheck at use on ASSIGN). That is R-6's predicted
  list.
- Review condition applied: five contract-defaulted reads become WRITTEN
  exemptions in fields.def (floor = absent constraint; result_decl, count
  and member = absent offer; indent = layout only).
- Next: N2, the WARN census over the whole corpus × every axis (a heavy
  Mac or Linux run, slot via main). Then R-6, G2u, N3 and N4. g2x run 1
  started 15:04.

## 2026-10-07 (evening) — N2 done; wind-down for the box move

- N2 census (Mac, under the lock, 15:11 to about 15:55): 958,292 compiles,
  0 timeouts, 0 no-row sites. 129,937 would-declines → exactly 3 cells,
  all `miss` R1 (ofsskip define/use, precheck ASSIGN use). That is the
  predicted R-6 list, posted in responses.md.
- Frank: start nothing new; close out; push the kit branches; wind down
  (pcrec dev moves to pcrec@192.168.1.17, cloned from GitHub). g2x was
  stopped at a consistent point. Its interim blinded work is committed on
  branch `g2x` (5be6fe58, unreviewed): run 1 had 138 failed, 0 faults,
  findings F1/F2/G1 (see wake.md §4). wake.md was rewritten for the new
  box.
- Lessons: lanes still overran numeric caps "for timing" (rowconn2: ~770
  compiles outside the lock). Briefs must forbid timing runs outright.

## 2026-10-07 (late) — woke on the new Linux dev box (pcrec@192.168.1.17)

- Kit worktree re-created at worktrees/memfn from origin/lane/memfn-rowcon
  (c808c3d5); main 23111928 merged in; make strict + build rc 0.
- Box facts (from main): 16 threads, ~29 GB, gcc 15.2.0, libpcre2 10.46;
  bare `timeout` is uutils, so use `gnutimeout`; no git identity configured
  (commit with -c user.name/-c user.email).
- Main's first full make test here holds the box; the kit runs nothing heavy
  until main releases it.
- One read-only sonnet triage of g2x F1/F2/G1 (capped at 20 pcrec + 20 gcc
  invocations). Asked main whether MF_MISS_N ships kit-side (recommended)
  or with R-6.
- g2x triage done (read-only, 7 pcrec + 2 gcc runs). F2 is a kit defect:
  the arms never note their own libc calls. pcrec's stamp is right, because
  its finishing pass scans the artifact. The fix lane runs after missn.
  F1 = the N3 cell, unreachable from pcrec. G1 is G2-side (equivalent
  mutants) and goes to G2u. Posted in responses.md.
- libcnote merged into lane/memfn-rowcon. The arms note memchr (ofsskip
  define, precheck use) and memcmp (runcmp's memcmp form) at render; the
  constant-size memcpy is excluded. The arm-pins test now checks the
  stand-alone MEMFN_LIBC stamp (it failed 8 fixtures before the fix, 0
  after). 16 sample compiles show identical .c/.h. After the merge, strict,
  build, test-memfn-arms and test-memfn-stamps are all rc 0. OWED to a heavy
  slot: the identity gate vs ccf0ca33 and the full G2.
- missn merged (MF_MISS_N; review nit: comment re-wrap 728bf063). Slot run
  on 728bf063: identity gate vs ccf0ca33 PASS with 0 movers on all 6
  streams; full G2 61,020,752/0, the token cell 538 sites. Posted in
  responses.md; offered the branch to main as an interim delivery so R-6
  can consume the token. Lesson: the session scratchpad vanished
  mid-session, so kit scratch moved to worktrees/memfn-slot/ (gitignored).
- Landing bar for the interim rowcon delivery (main s96): full make test
  640 s, 59/59, one red: [SABANCHOR] S570 stale under N1 (check-side). It
  was re-pinned (4e6c42c4); test-codegen rc 0. All 16 D69 mech rows
  DETECTED, with S570 re-run after the re-pin. done: posted. Lesson: N1's
  lane never ran SABANCHOR; any kit lane that edits memfn/src must run
  `python3 scripts/m6read_check_sab_anchors.py` (under a second) before
  delivering.

## 2026-10-07 (evening) — rowcon interim merged to main; G2u started

- Main merged lane/memfn-rowcon at 13b9f2ae and pushed it. The kit
  worktree is now on lane/memfn-g2u, cut from main 13b9f2ae.
- G2u: the blinded opus author works in the D27 cell worktrees/g2u-cell
  (worktree g2u, branch g2u, from main 13b9f2ae; made from the MAIN tree,
  not nested). Allowlist: memfn/include, memfn/tests,
  docs/design/memfn/integration.md, memfn/docs/trace_format.md. The g2x
  interim patch and the main-since-base delta are in the cell's .g2x/.
- Brief items:
  1. fold g2x;
  2. F1 cases go to a counted PENDING-ENFORCE bucket, with
     G2_STRICT_HOOKS=1 as N3's acceptance switch;
  3. G1's floor is judged only over negative-offset sites;
  4. explicit values;
  5. refusal expectations;
  6. the POISON differential, with "unused" sets from the contract text;
  7. the SEMANTIC differential;
  8. per-form floors.
- Caps: --quick at most 4 times, taskset to 4 cores; no timing; no full
  run (that is the manager's slot).
- A stall watcher (cell mtimes, 30 min) is running.
- Main's queue: possland → admin1008 → stc3 → R-6. N3 waits for R-6 plus
  the N2 re-run.
- G2u done. g2u (opus, blinded) folded g2x and added items 1-8. Quick run:
  462 failures, all K-1, a contract gap. The kit ruled (memfn.h: a FUNC
  site's name is site.pred.fn_ref for every op; fn_ref 0 on FUNC is
  refused under N3), and g2u2 (sonnet, blinded) aligned the poison table.
  Full G2 in main's slot: 138,742,037/0. S526 DETECTED. done: posted.
- G2u merged to main (038ed335). N3 started: kit branch lane/memfn-n3 from
  main; opus lane n3 in worktrees/n3 (enforce at both phases; F1/miss/K-1
  fn_ref/refusal naming; the ofsskip K96 ad hoc checks replaced by the
  gate). Authoring only. The census, identity gate, full G2 (strict) and
  make test happen in a slot after R-6 lands on main. STOP rule: any pcrec
  site other than the N2 cells that would be refused.
- n3 merged into lane/memfn-n3. The gate enforces at define and use; the
  pre-check is split by handoff (precheck / precheck_assign, one form id);
  ofsskip's K96 ad hoc checks are replaced by the gate (20 --gate arm
  fixtures, 19 of them flip with the gate off); fn_ref is a hook id (0 =
  unstated). Strict, build and arms (104/0) pass.
- Pre-R-6, test-memfn-stamps fails 2 floors (calls-memcmp 35 < 40, idiom
  55 < 80), because pcrec now has its N2-cell patterns refused (215
  refused in the sample). That is expected until R-6; recheck on the
  main+R-6 merge.
- Without R-6, n3's 40 compiles show only the N2 cells refused; with a
  scratch R-6, none. No STOP.
- G2 is still red, 457 checks, all fn_ref-0 FUNC sites that G2 treats as
  hard. The blinded follow-up g2u3 (sonnet; the cell is refreshed with
  N3's build and memfn.h) makes the enforced outcome G2's default.
- N3 validated in one chain (18:37-19:34): census on the enforcing build
  0/0, identity gate 0 movers, full G2 149.0M/0 (1,103 enforced-class
  cases), make test 747 s green, 16 mech rows DETECTED. done: posted.
- R4g edit set posted. Main cleared it: start after N3 delivers, land
  after C4, conditions recorded in responses.md.
- N3 merged to main (5e9ec93c). R4g started: kit branch lane/memfn-r4g
  from main; opus lane r4g in worktrees/r4g. Main's conditions are in the
  brief: no CandPf/CandRow change, the anchored rows re-pinned + solo in
  R4g's commit, sabotage_anchors.tsv re-derived, zero movers (shown on
  ≤ 60 compiles against a pre-edit reference binary). It lands on
  post-C4 main via a slot.
- Main ruled: the R4g memchr widening is accepted (an edit-set amendment in
  done:). §19 row 6's rarity half is deferred after C5b; the decision stays
  pcrec's in cand_rows[]; the kit receives text only. This narrows §19 row
  6 of the design. Revise that row in the design deliverable that goes with
  R4g's done:.
- g2pf (blinded) added the PF family: cells 1-4, the pf-edge class, form
  ids pf_memchr/pf_walk. Quick: 871 failures, all finding 1. Answers 0
  failed. Kit rulings:
  - F1 (stated ret_pred/preds on FIND moves PF to generic) is a defect:
    the PF rows serve ANY for fields irrelevant to their shape;
  - F2 (memchr row leaves result unwritten on a miss with
    on_miss_leaves = 1) is a contract amendment: result UNSPECIFIED on a
    miss when on_miss_leaves, and on_miss must not read it (pcrec's
    `return 0;` complies);
  - F3 (mf_emit picks a row, then mf_use refuses on result_decl) is a
    defect: one-call entries gate the use-phase fields at selection.
  Lane r4gfix (sonnet), zero movers on compiles.
- r4gfix merged:
  - F1: the PF rows serve ANY for preds/ret_pred; on_miss_leaves stays a
    decline, with the reason commented;
  - F2: memfn.h comments say result is UNSPECIFIED on a miss when
    on_miss_leaves = 1;
  - F3: mf_emit selects over define|use, mf_define over define only.
  arms 138/0, stamps 14/0. Its compile identity ran before a final revert
  and missed the bounded forms; the slot's identity gate is the real
  check.
- G2 quick after the fix: 314 failures, all G2-side (the mf_emit trial vs
  the real define+use path, which now differ by contract). Blinded g2pf2
  makes G2 judge each path by its own contract.
- R4g validated in one chain (21:16-22:18): census 0/0, identity gate 0
  movers, full G2 173.8M/0, make test 685 s green, 29 rule-(b) mech rows
  DETECTED. done: posted.
- Frank's observation through main: the N2 census runs with a per-arm
  barrier (stragglers like `((a)|ab){4000}c` leave one compile running).
  Follow-up: one pool across all arms.
- R4g merged to main (d33e1d55). n2pool delivered (one census pool, byte-
  identical, resumable). N4 started: opus lane n4 in worktrees/n4 on
  lane/memfn-n4 (from the n2pool branch), covering the MF_TRACE reach
  counters, rows.tsv, the per-row signatures with controls, the census
  floors (placeholders, pinned in a slot) and the spec literals.
- Session reset (Frank). N4 is queued for a slot; its slot8 script is
  written but not launched. n2pool was delivered and awaits main's merge.
  wake.md is current. No lanes or runs are in flight.
- 2026-10-08: N4 validated in slot8 and delivered.
  - Full census: 379 s at JOBS=16, rc 0, 0 would-decline. The 12 pcrec
    floors are pinned.
  - make test had one red, test-codegen K37: N4's own `run_rows.sh` loop
    read as an unbounded compiler site. A sonnet triage found it, the fix
    is in e8e3e1d8, and test-codegen is green.
  - The test-codegen re-run (5m43s) overlapped main's possland2 make test.
    Main had cleared the triage to proceed, but the run was heavier than
    "light". Next time, ask first.
  - done: posted.
  - OWED: g2_floor (blinded, per-row G2 count).
- 2026-10-08: R4h scoped by a read-only opus lane, and its edit set posted.
  - Overlap with C5-C7: disjoint functions.
  - Contract gaps: G1 (counter ownership), G2 (layout), G3 (hook classes),
    G4/G5.
  - Main ruled Q-R4h-1 (a)+(b) (session 97): a caller-owned-counter hook at
    MF_SITE_ABI 5, plus one pcrec layout-normalization mover after C7.
  - Next on the kit side: R4h prep (G3 classes, the (a) hook, Q-G2-5
    recorded) as a kit-only zero-mover unit.
- 2026-10-08: main merged lane/memfn-g2floor (N4 + G2 floors) as 37462a8e:
  make test 60/60, 707 s. C5 is merged too.
  - r4hprep (opus) delivered the kit-only R4h prep: MF_SITE_ABI 5
    `count_by_caller`, the CONJ/POSTFIX/EXPR_STMT hook classes, and Q-G2-5
    recorded as ruled.
  - Its light checks: arms 171, rows 117, stamps 14, G2 quick 45.2M/0, and
    18 witness compiles byte-identical.
  - It is merged into lane/memfn-r4hprep together with main 37462a8e+.
    strict and the light sections are green after the merge.
  - The slot9 chain is written: census, identity gate vs main, G2 full,
    make test, and 17 mech rows. It waits for main's slot.
  - Findings for R4h:
    - the `member` hook's text (scan_test) is pasted as a bare `&&`
      operand and only exists at render, so it needs a render-time class
      or a pcrec shape promise;
    - deleting the conditional `count` use is caught only by check E.
- 2026-10-08: the layout normalization landed on main (c4c37af8, abi 67) and
  the frozen ADVANCE target matches it. R4h was built by an opus lane:
  - zero movers, no abi event, no kit source change;
  - I1 shadow comparator: 78,298 sites, 0 mismatches; 38/38 witness
    compiles byte-identical; G2 quick green;
  - S72/S214/S512 re-aimed, S614-S616 added, S617 returned.

  Merged into lane/memfn-r4h. slot10 is QUEUED behind nullanch2 (abi 68).
  On GO: merge the new main FIRST, then run slot10/run.sh.
- 2026-10-08: R4h DELIVERED (lane/memfn-r4h @ 1428d550).
  - slot10: identity gate 0 movers, G2 full 173.8M/0, make test 655 s,
    18 mech rows clean.
  - The census's reason_stale on `generic` was expected: pcrec now selects
    the kit's generic ADVANCE row. Fixed by making generic a pcrec row
    (witness a[^x]*, control abc, plant red); the census re-run gave rc 0.
- 2026-10-08: R4h MERGED to main. R-7 (M4, MLINE) filed: scoped (no
  overlap with DEC-FALLBACK; gaps G1-G3 closed kit-side, Q-R7-1/2/3) and
  acked by main. Ids S617-S619.
  - Lane m4 BUILT it on lane/memfn-m4 @ 9c7b848e:
    - MF_SITE_ABI 6, `pf_memchr_back`, PcrecFind generalized, MLINE
      delegated;
    - 0 movers (shadow and corpus pairs), C12 clear of memchr.
  - Blocked on a blinded G2 lane, because G2's oracle predates Q-R7-1.
  - Session reset at Frank's request; wake.md lists the order of what
    follows.
- 2026-10-08 (session after reset): R-7 (M4) DELIVERED.
  - The blinded G2 lane g2m4 (sonnet, cell g2u-cell) brought G2 to
    MF_SITE_ABI 6: reads-below range, mline AT_N family, loop-exit class
    plus W2 mutation 8, FLOOR_ROWS 14. Quick 47.4M/0, merged via g2u.
  - Floors for pf_memchr_back: g2 4109, pcrec 3271.
  - slot11 on kit + main e99ad486 was green except S513/S525, which are
    equivalent mutants once pcrec has no memchr. Read-only triage lanes
    confirmed it; both re-pinned UNDETECTED as tripwires and re-run solo,
    clean. make test now runs through scripts/perfrun.
  - Posted done: R-7 and a notice with G2's Q-G2M4-1..9 and the redundant
    libc_names memchr entry.
- 2026-10-08: RULING from Frank, given directly to the kit session. SIMD
  is an INDEPENDENT, PARALLEL thread and no longer waits to come "last".
  - It can be switched on and off (`-fmemfn-simd`, default OFF), so it is
    its own optimization path. It does not wait for the algorithmic queue
    or the migration to finish; part of the refactor's purpose is to
    allow exactly this.
  - Bar: each SIMD form must be faster than the non-SIMD code at its
    sites, or show a specific named benefit (e.g. code space), because it
    imposes restrictions.
  - Default-ON stays its own ruled event (D147).
  - Posted to main as a proposed D-entry (responses.md).
  - Meanwhile M7 is merged on lane/memfn-m7; blinded G2 lane g2m7 is
    running; slot12/run.sh is written.
- 2026-10-08: RULING from Frank (kit session). He approved the SIMD plan
  with a capacity split: "2 parts migrating to 1 part simd until the
  migration is done, then you're unlocked." Lanes go 2:1, and heavy slots
  go 2:1 when both threads have a run queued. The split lifts at the
  migration's end state (M5′). Posted to main.
- 2026-10-08: The bench box's CPU, at Frank's prompt ("bench ... runs on a
  separate Linux box that uses an older CPU"). pcrecdev2 read it with
  lscpu.
  - budu-ryzen1600 is an AMD Ryzen 5 1600 (Zen 1). Flags: sse2..sse4_2,
    ssse3, avx, avx2 (executed as 2x128-bit uops), bmi1/bmi2 (PDEP/PEXT
    microcoded, so slow), popcnt, abm (lzcnt), sha_ni. NO AVX-512.
  - The dev box is a Ryzen 7 7700X (Zen 4: full-width AVX2, AVX-512).
  - For the SIMD thread:
    - 16 B SSE2/SSE4.2 forms first; AVX2 second, with smaller bench gains
      expected; AVX-512 filed (no bench evidence possible); no PDEP/PEXT
      in kernels.
    - Acceptance is read on the bench CPU, or both CPUs are reported. A
      dev-box-only verdict overstates.
  - These go to R-9's D6 panel as inputs. r9d was briefed before this, so
    there is no addendum to the running lane.
- 2026-10-08: RULING from Frank (kit session). Short-form unofficial
  benches can run anywhere and are directional. An OFFICIAL result needs a
  pcrec-bench run, macOS work included. The bench can run on the dev box
  too, but it is PLANNED and coordinated through main, which owns the
  bench inbox. Posted to main.
- 2026-10-08: D144 addendum 4 (Frank via main, main 04733583). Official
  SIMD verdicts are pcrec-bench runs on the hardware each form targets.
  The bench runs on several boxes: ubuntubudu (Zen 1), this dev box
  (7700X, Zen 4: AVX2 and full AVX-512) and the Mac. Main coordinates runs
  on this box. CORRECTION to my earlier priority: AVX-512 is NOT filed;
  SSE first stands, and the AVX2/AVX-512 order is argued on evidence. The
  r9 panel was briefed before this, so the consolidation folds it in.
- 2026-10-08: Frank answered R-9's questions directly to the kit:
  - Q-R9-1/2/3/5/7/8/9: "I agree" (as recommended).
  - Q-R9-4: "if that [space] isn't true then it's fastest wins". This
    matches the recommendation: no named-benefit path for SIMD rows.
  - Q-R9-6 (the floor rule) is PENDING: he asked what it is, and it was
    explained (SIMD-on = SIMD-off plus guarded text only; compiled without
    the feature it IS the scalar code; checked by C18).
  - Posted to main. Also: lane g2m6 (M6 blinded G2) was stopped by Frank;
    no relaunch without his word.
- 2026-10-08: Frank (kit session) on R-9:
  - Q-R9-6 (floor rule): AGREED.
  - **No `#if`/`#ifdef` inside function bodies** ("hard to read"). The SIMD
    choice moves to FILE SCOPE: per-level `static inline` helpers selected
    by `#if` there, and the function body makes one plain call. The kit's
    reading: the SIMD-off artifact also calls the helper (scalar body =
    today's loop). That is a one-time byte move and abi event, so the
    floor rule stays byte-exact; measured under G1.
  - **Runtime dispatch is FILED, not current.** The motive: one artifact
    must not need 4-5 whole copies (500 KB) for different CPUs. So it is
    per-SITE multiversioning: only the hot helpers get one copy per level
    (target attribute), selected once at startup from the CPU. The level
    set is named at compile time and need not cascade (e.g. AVX-512 or
    scalar). Static (#if) and dynamic (startup choice) share the same
    file-scope structure.
- 2026-10-08: Frank, refining runtime dispatch (still FILED):
  - (1) Per-arch separate artifacts selected later (e.g. a chosen lib.so)
    already work through static selection; nothing is needed from pcrec.
  - (2) There are two frequency classes:
    - INFREQUENT sites (precheck, find-start; about once per search call)
      may be dispatched dynamically per hardware;
    - FREQUENT / hot-loop sites must not pay a hardware check. They take a
      STATIC choice: the lowest common denominator of the selected set, or
      a named most-common level.
  - This only matters with more than one arch selected for dynamic support
    AND a hot-loop SIMD form, so it may be theoretical. Example classes
    (r9fu): PRE's FUNC runs once per call (infrequent); the filed OFS
    run-pinned vrun re-seeds inside the DFA scan loop (frequent).
- 2026-10-08: Frank ruled Q-R9-10 (from revision D155): shape (b), one
  unchanging FUNC that calls a level macro selected at file scope by
  `#if/#elif/#else`, NOT the FUNC-as-selector shape (a). The macro is ALL
  CAPS so it reads as a macro: `<PREFIX>_<FN>_LEVEL` (e.g.
  `RX_REQRUN_LEVEL`), following pcrec's upper-cased-prefix stamp
  convention; the helpers stay `<p>_<fn>__body` / `__w16` / `__w32`.
  Q-R9-11 (frequency class): kit-decided, a `freq` column in DELEG_SITES
  built only when [MEMFN-RTDISPATCH] triggers (not MF_P_INLOOP).
- 2026-10-08: Frank REVISED Q-R9-10 to shape (c), superseding (b): no
  level macro. The FUNC is written once, and its whole body is the
  `#if/#elif/#else` chain with one helper call per arm. The rule's
  wording, confirmed by Frank: "a function that does work never contains
  `#if`; a selector function's whole body may be the `#if` chain, one call
  per arm, and nothing else."
