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
- 2026-10-08 evening: SESSION RESET at Frank's request. State:
  - **M7 (R-8)** is BUILT, and its slot12 findings are fixed (m7fix) on
    lane/memfn-m7. It waits for slot13's re-validation (main GOs it after
    B5). Then `done: R-8`.
  - **M6 (R-10, VMSTRIDE only)** is BUILT, and N6 is retired, on
    lane/memfn-m6 (stacked on an older m7). Still needed: the blinded G2
    lane g2m6 (stopped for the reset, cell clean), the m7 fixes merged
    in, then its slot.
  - **R-9 (SIMD design):** D155 revision on lane/memfn-r9 @ c0b61c16.
    Q-R9-1..11 are ruled (D155 + addendum 1; Q-R9-10 is shape (c), the
    selector-body rule). The text still describes Q-R9-10 as open with
    (a)/(b): update it to (c), then a light re-check panel.
  - Frank: lettered options are fine, but leave room to bat a question
    around.
- 2026-10-08 night (session after reset): r9c (doc-only) updated §R4.9 to
  Q-R9-10 shape (c) + Q-R9-11 `freq`, Q-R9-1..11 RULED, C18 leg (d)
  selector-only; lane/memfn-r9 fast-forwarded to 5a9e8c4c. The light
  re-check panel is still owed before `done: R-9`. Main asked for pacing
  (subscription 89%, resets 07:00): g2m6 stopped before writing (cell
  clean), held until after the reset; the panel waits too. M7 waits for
  main's slot13 GO (B5's chain still running).
- 2026-10-08 22:55: slot13 GREEN at 999dd994 (main 84da351b merged; one
  lanes-index conflict, both lines kept): census would_decline 0, gate 0
  movers x7 sets, G2 full 185,774,876/0, make test green (perfrun 708 s),
  mech 14/14 unexpected 0. mismatch_inplace pcrec_floor pinned 2116
  (6c8288d0); test-memfn-rows 127/0. `done: R-8` posted (33c02ac9), main
  told. Held for pacing until after 07:00: g2m6, the m7→m6 merge and M6's
  slot, and R-9's light re-check panel.
- 2026-10-08 ~23:30: M7 MERGED by main (post-merge build/strict/rows/
  registry green; m7, m7fix, s670cell pruned). Frank discussed SIMD
  priorities (fused byte+cond forms; prioritize by site-category frequency
  x winnable margin; no population census exists yet) — discussion only,
  nothing scheduled. SESSION RESET at Frank's request; wake.md rewritten.

## 2026-10-09 morning — kit session (pcrecdev3) after the 07:00 reset

- Main confirmed the pacing hold lifted (normal capacity, 2:1 migration:SIMD).
- g2m6 (blinded G2 for M6, sonnet, cell worktrees/g2u-cell) relaunched with
  m6_report §7 pasted into the brief; running.
- main merged into lane/memfn-m6 @ 7cae7465: lanes index and mech CLAUDE.md
  unions, S512 comment keeps both histories (floor 14: N7U +1, N6 -1), the
  fallback call graph + sabotage anchor maps REGENERATED on the merged tree
  (family 99, 589 sites, exit 2 = S571). Anchor check, strict,
  test-memfn-{arms,stamps,rows}, test-codegen green.
- R-9 light re-check panel r9b (2 sonnet critics) done: contract — deliverable
  after RC-1/RC-2; docs — DS-10 (C18 "two legs") blocker + unlabelled probe
  numbers. main merged into lane/memfn-r9 @ 021b3b32 (lanes index conflict
  only). Fix lane r9fix applying RC-1..7, DS-1..14 + the consolidated review
  docs/dev/reviews/2026-10-09-r9b-memfn-simd.md.
- ~08:05: R-9 DONE and merged by main (r9b applied, ad3d9ea4; lane/memfn-r9
  fast-forwarded to it). R-11 filed by main and acked (lane/memfn-r4e0).
  Lane r4e0 (opus) built R4e′.0 (kit_walk + fn_rows[] BODY/PREFIX,
  a8e866dd). It is zero-mover on the light gates, with S686-S689 detected.
  Its heavy chain is slot15, after M6.
- g2m6 delivered: G2 quick 51,169,258/0. Folded into g2u @ 2dc64da6 and
  fast-forwarded into lane/memfn-m6, after lane/memfn-m6 was itself
  fast-forwarded to lane/m6 (it had lagged by one commit). The m6 worktree
  is now on lane/memfn-m6.
- Q-G2M6-1..9 are kit-owned contract-clarity items, not defects. G2 asserts
  the kit's current conservative behaviour. Follow-up, unscheduled:
  - Q-G2M6-3: `peek` is required at W > 1 although it is unused there.
  - Q-G2M6-4: EXCLUDED on a strided ADVANCE.
- slot14 (M6) requested from main; script at memfn-slot/slot14/run.sh.

## 2026-10-09 midday — kit session (pcrecdev3)

- R-10 / M6 DONE and merged by main (287133ba). slot14 was green apart from
  test-resource W5. Triage traced that to M6 moving an arena boundary; it was
  fixed by lane w5fix, where W5 now measures its pattern instead of pinning it.
- LESSON: my verdict on slot14's "66/66 unexpected 0" read only the
  unexpected/undetected columns. Main found anomalies 1: S683 named suite
  `memfndeleg`, which had no arm (UNKNOWN-SUITE), so the row was never
  measured. Fixed by adding the arm (1541a7aa). S683 solo: DETECTED, 2fail/3pass.
  From now on a mech verdict reads the whole COMPLETE trailer, anomalies and
  unreached included.
- main merged into lane/memfn-r4e0 (7798c77a). The start/fallback maps were
  regenerated. Light checks and G2 quick 51,169,258/0 are green.
- slot15 is scripted (memfn-slot/slot15/run.sh): mech is now ONE `PROCS=4`
  invocation, per [TT-MECHPAR] on main. It waits for main's GO.

## 2026-10-09 afternoon — kit session (pcrecdev3)

- R4e′.0 MERGED by main (131c173a). R4e′.0b was built by lane r4e0b (opus).
  The abi number moved 70 -> 69 -> 70 with landing order around decattr,
  and was reconciled at the main merge b3e26cfa.
- slot16 is green (see responses.md done: R4e′.0b). R-11 is complete once
  main merges.
- LESSONS:
  - I launched slot16 without asking main for the GO. No harm this time,
    but always ask.
  - My slot script wrote DONE from an EXIT trap even when a stage died, and
    main's sequencer keys on DONE, so rq3 was lifted early. The script now
    writes DONE only after the LAST stage completes (FAILED otherwise).
  - The mech row list was built with a sed that kept the full path of an
    `S-U8` row. FATAL at launch, nothing measured, re-run.
- For batch 1 (from main): RQ-3 (lane/rq3, abi 71) needs `mf_sink`
  members `simd_open`/`simd_close`. pcrec's
  `pcrec_memfn_sink_simd_open/_close` are ready in
  src/gen/memfn_sites.h. Every SIMD row brackets its guarded text with them
  and declares a bound in tests/memfn/simd_bounds.tsv, which
  `make test-memfn-guarded` checks. RQ-1 (`--memfn=` carrier) landed with
  clibundle; the first options.def row must add a pcrec cli case.

## 2026-10-09 evening — kit session (pcrecdev3), paused for reset (context 53%)

- R-11 COMPLETE (R4e′.0b merged at abi 70, 82ff9432).
- R-12 step 1 scoping merged (df66a032). Main's answers: Q-R12-1 no Frank
  ruling for VMLAZY's normalize, abi 72; Q-R12-2 delete the VMLAZY row; Q-R12-5
  add VALID + vocab re-sweep; Q-R12-6 keep span-count at ceiling 0.
- **Frank ruled Q-R12-3 (D147 addendum 14): N7U RETIRED; the kit is
  ENCODING-BLIND.** The rule: a walk whose unit is the encoding's character
  (a decode on either operand) belongs to the encoding; its byte-domain
  sub-loops are kit sites. Frank: "Kit shouldn't, now at least and unless
  strong counter evidence emerges, know about encoding ... a passed lower()
  type encoding function but then what role is memfn playing?" N7U's site
  (span_match_caseless) serves caseless backrefs AND `${name}` variables; an
  ASCII fast path inside it is filed [MEMFN-CI-ASCII], not scheduled. OWED:
  delete N7U's manifest row and write the rule into integration.md §R4.3.4
  beside Q-R10-11 (a small commit on lane/memfn-vmlazy after its chain).
- VMLAZY built by lane vmlazy (opus) on lane/memfn-vmlazy @ 40a3e5bf
  (normalize abi 70->72, zero-mover REPLACE, VALID row); G1 null; light
  green; chain2 (6 sweep arms) still running detached at pause.
- Frank 2026-10-09: the kit session too looks for a reset above 35% context.

## 2026-10-09 ~17:15 — wake after reset; VMLAZY chain2 green; N7U retired

- Woke from the vmlazy wake.md. Heartbeat cron `17,47` recreated.
  requests.md holds no new item.
- **Chain2 COMPLETE, green** (vmlazy_report §8a): 13 light suites rc=0, and
  9 emit_sweep arms show 0 movers / 0 asymmetric. utf8 and `-fno-cls-kit`
  exited rc=1 on r4clx's DECLARED composition-floor exception (37 < 38, both
  sides). The first read of an rc=1 looked like a failure; the judge table
  in r4clx_report.md is where that exception is declared.
- **N7U retired** by lane n7uret (sonnet, light). Docs/TSV only, so no pcrec
  byte moves. C17 floor 14 -> 13, C12 floor 2 -> 1, S512 re-pinned. Merged
  into lane/memfn-vmlazy after chain2 exited; strict and the manifest/forms
  checks are green on the merge. The D58 add. 2 revisit close is owed to
  main and posted as a notice.
- Stale worktrees r4e0/r4e0b/w5fix/r12: `.scratch` was deleted; they are kept
  by wtprune's 120-min quiet gate, so prune them later.
- Frank asked for the first SIMD directional reading when it exists. It
  does not exist yet: R-13 waits on RQ-3, then RQ-2 and the RQ-4 slot for
  timing. Report it when the R-13 sweeps produce it.
- Waiting on RQ-3 (abi 71; its chain is running) before the §8 slot chain
  and R-13.

## 2026-10-09 ~19:20 — pause for reset (Frank's ask)

- **R-12 VMLAZY.**
  - RQ-3 landed on main (631771b7, abi 71). Lane vmlmerge merged main into
    VMLAZY at abi 72; the readers were found by grep, and 12 light suites
    and S693 are green.
  - Recursion-identity (A) went red on 114/53/53/28 lazy patterns.
    Kit ruling R1: an 8th exception, `lazy_prefix_rewrite`, a one-sided
    mechanical rewrite of the reference. Lane vmlrid built it: matched by ID
    on every axis, near-miss and S711 plants rejected, gate 18/0.
  - lane/memfn-vmlazy fast-forwarded to 1bb49dee. slot17 is RUNNING
    detached under main's GO.
  - vmlmerge ended without reading R1 (sent while it was busy). Again:
    rulings go as a file plus a message, and a fresh lane gets the work.
- **R-13 batch 1.**
  - Built by lane r13 as CANDIDATE: vrun-w16/w32, KA-only until RQ-2.
    SIMD-off 0 movers, G2 51.2M/0, solo mech 20/20 clean. Q-R13-1..7 ruled
    with the lane's leanings.
- **D157 (Frank, via main).**
  - RQ-2 states a ranked rarity array, and the distance rule is the kit's.
    Lane r13doc recorded it in integration.md.
  - Main's correction (do not presume any rule) went to the lane as ruling
    R1, and the lane's second commit removed the candidate rule.
    lane/memfn-r13 is at ae7b6a22.
- Pruned the stale worktrees r4e0/r4e0b/w5fix/r12.
- Frank asked when the first SIMD directional reading comes. It comes after
  RQ-2, then the kit's rank_pos lane, then the RQ-4 timing slot.

## 2026-10-09 evening — wake after reset; slot17 read; startset red fixed

- Woke from lane/memfn-r13's wake.md; heartbeat cron `17,47` recreated.
- slot17 (lane/memfn-vmlazy @ 1bb49dee, ref 631771b7) DONE 20:15:
  - Green: build, strict, sabanchor, recid 18/0, census 0 OTHER/ASYM (controls fire),
    N2 clean, G2 full 192,654,549/0.
  - mech: 26 rows, unexpected 0, undetected 0, anomalies 0; unreached 1 = S685
    (declared UNREACHED: VMLAZY's pending row is deleted).
  - make test RED: test-startset only.
  - VARIANTS measured nothing: my script omitted `--tree-rev` (usage error).
- Triage lane ssred: base green, tip red. Only `[vm-movers]` failed: the new corpus file
  tests/base/vm_lazy_rmin_prefix.rxt was never added to the stage-2 VM manifests
  (10 auto / 17 forced). It was a delivery miss, not an emission defect.
- Lane vmlfix (921a3ef2) regenerated the manifests with census_s1.py and spliced in
  only the corpus rows. test-startset and strict are green. lane/memfn-vmlazy was
  fast-forwarded to it.
  - Finding for main: the generator would also add 7 pcrec-bench rows (6 forced,
    1 s3_dfa; bench @ 76e13c1d). They are un-refreshed, as at m7fix. Whether to
    re-sync them is a bench-pin decision, and it is main's.
- Main's order: rq2's chain → RQ-2 merges (it carries the 8ec0e97a variant re-pin) →
  merge main into vmlazy → slot17b (variant sweep + make test), on main's GO.
  done: R-12 waits for slot17b.
- LESSON: a slot stage that dies on a usage error is a stage that measured nothing.
  Dry-run every new invocation's argument parsing before the slot.

## 2026-10-09 night — R-13 follow-up (rankuse) built; R-12 delivered

- R-12 delivered as `done:` on lane/memfn-vmlazy @ 92213567:
  - slot17b read: make test green; VARIANTS FAILED only by the abi stamp; every mover
    by id is in the lazy set (vartri).
  - Four yes-collapsed floors fell by 1 when `(a{2,3}?){2,3}` crossed the lowered cap,
    and VARIANT_PINS was re-pinned from slot17b's tallies.
  - Main merges R-12 LAST, after specnum and lfl0, then gives a GO for a re-merge
    plus slot (abi changelog re-homed to docs/dev/history/abi_changelog.md).
- main 7b98a046 (RQ-2) merged into lane/memfn-r13 (6d16bbac): R-13's sink ops renumbered
  MF_SITE_ABI 9 -> 10, with readers found by grep.
- Lane rankuse (opus) built the kit's read of `rank_pos`:
  - KB = the first ranked position other than KA. WHICH position is derived; HOW MANY
    (two) is an UNMEASURED DEFAULT with the deny `--memfn=no-vrun-kb`.
  - `rank_ok` refusals; bounds 2,700/2,800; SIMD-off 0 movers.
  - Lane rkfix renumbered its S738-S742 (lfl0's ids) to S750-S754 (main's block), and
    fixed two inherited reds: C4 (S726 renamed; 6 allowlist rows, floor 27) and K37.
  - S522/S725/S726 solo clean. Fast-forwarded into lane/memfn-r13.
- LESSONS:
  - rankuse ran full-population emit_sweep and G2 while main's specnum chain held the
    box, despite a light-only brief. Main marked that perfrun contaminated.
  - rankuse missed two renumber messages while busy; its ids were fixed by a fresh lane.
  - Future briefs: list heavy runs by NAME, and require run start/end times in the
    report.
- slot18 is scripted (memfn-slot/slot18/run.sh): 4 identity sweeps, N2, G2 full,
  make test, 33 mech rows. It waits for seq5's end ("lfl0 CHAIN DONE; seq5 end") and
  main's GO.

## 2026-10-10 ~00:40 — session close (Frank /close)

- Paused while waiting:
  - R-12: the vmlazy re-merge is prepped at 0517caea (specnum in, abi-72 entry
    re-homed). slot19 is scripted and waits for lfl0's merge and the NEXT main's
    GO.
  - R-13: built at 9348a747; slot18 runs after R-12 lands.
  - Main reset at ~00:30.
- wake.md was rewritten on both branches. A responses notice for R-13 is posted.
  Nothing of the kit's is running on the box.
## 2026-10-10 — R-12 re-landed (slot19)

- On main's GO (e33fb821: lfl0 landed, main green), I merged e33fb821 into
  lane/memfn-vmlazy (5df8b31b). Conflicts: startset manifests (union),
  rxtsource census (summed from the merge base 276/5431/52073 to
  278/5570/53503). A new [cites] check caught two line citations in
  vmlmerge_report; they are now section citations.
- slot19 04:07-04:49: every stage green; self-check CLEAN; VARIANTS FAILED
  by design. A sonnet read-only pass re-ran the comparator on slot19's
  binaries and found 0 movers outside abi-stamp or lazy (report §8c).
- done: re-posted; main merges R-12 next, and revbuild takes abi 73 on top.
  Next: merge post-R-12 main into lane/memfn-r13, then slot18 on main's GO.
- LESSON: emit_sweep's log prints only 5 movers per stream. A by-id
  verdict needs the full list, which takes a re-run of the comparator on
  the slot's own binaries. Budget ~25 min for it, or have the slot script
  dump the keys.

## 2026-10-10 — R-13 brought onto post-R-12 main (lane r13merge)

- R-12 merged to main (a15fb77b). Merging it into lane/memfn-r13 conflicted
  in 8 files, 4 of them main's [SPEC-CLEAN] rewrites. I aborted the merge
  and delegated it to lane r13merge (opus). It kept main's structure and
  re-homed R-13's facts at limits §8.3¶3, registry §6¶8a/¶8b (floor literal
  3), tuning §2.43¶3a/¶3b/¶4 and match_api §6.3.10. The history narrative
  was dropped (the history files are frozen; the narrative stays in the
  lane reports).
- One red, fixed in the lane: the axes_registry_check coverage pin went
  216 -> 217, because R-13's memfn floor arm is now reached. The stale pin
  was already on R-13's own tip.
- Reviewed: the ledger unions lost no entry (by count), and the spec diff
  against main is R-13 facts only. Fast-forwarded lane/memfn-r13 to
  48e56aad; build green. Light suites green in the lane (report
  docs/dev/lanes/r13merge_report.md).
- OWED, a kit follow-up: stale "no SIMD form exists" comments in
  lib/pcrec.h, src/dump/axes_dump.c and tests/memfn/libc_census.py.
- Next: slot18 on main's GO (revbuild holds the slot).

## 2026-10-10 — R-13 slot18 read, delivered

- Main's GO came after REVEND (abi 73) merged. Merged 9024449f into
  lane/memfn-r13 (2a44386a): registry coverage pin 216+3+1 = 220, lanes
  index union. Light suites green (8 suites).
- slot18 09:56-11:22: build/strict/SABANCHOR, N2 (0 fails), G2 full
  192,654,553/0, make test no red, mech 33 COMPLETE all zero. The sweeps
  exit 1, as expected. A triage lane (s18tri, sonnet) read them by id: SIMD-off
  moves only --list-axes; the five `start` arm floors are stale on main (equal
  both sides, pins of 26d2069f) and go to main; the SIMD movers are vrun
  text only and reconcile to simdfloor's 44.
- vrun-w16/w32 pcrec N2 floors pinned at 70 (floor(0.9 x 78)).
- done: R-13 posted. Next: RQ-4's tier-U timing slot (Frank's first SIMD-on
  vs SIMD-off reading), on main's grant.
- Side work: started memfn/docs/ideas.md (Frank) on lane/memfn-ideas, 6
  entries from Frank's vrun questions (min-length end bound, duplicate
  constants, plain-case = §R4.9.7.1 deliberate, byte+class filter, held mask,
  VM start-set skip).

## 2026-10-10 — RQ-4 timing harness built (lane rq4h), slot20 ready

- R-13 and lane/memfn-ideas merged to main (a2f66450). Main granted RQ-4's
  tier-U slot, after slbuild's ([START-LANDING], abi 74) chain.
- Lane rq4h (opus) built docs/design/memfn/probes/rq4/: 51 cells (the four
  R-1 cells, 39 slot18 vrun movers, a KB cell with KA's byte at 1/8, a
  sparse-pick fn-pair cell `(?i)azqb`, 8 non-vrun nulls), arms
  DEFAULT/KB-DENY/OFF at x86-64 (w16) and x86-64-v3 (w32), rx_search plus
  find-all, interleaved, rotated, taskset 12-15, with sibling-busy
  discard. The null band is the max |delta| over byte-identical cells.
  Report docs/dev/lanes/rq4h_report.md.
- Merged into lane/memfn-rq4 (67d019a2). slot20/run.sh now points at
  worktrees/rq4. A tiny dry run there is green (11:43-11:44, not a reading).
  Full slot ~75-105 min; it needs cores 12-15 and their SMT siblings 4-7
  quiet.

## 2026-10-10 — slot20: the RQ-4 reading (tier U)

- On main's GO (box quiet, main's lanes held) slot20 ran 16:01-17:10:
  15,696 readings, fails=0. Summary in rq4h_report.md's addendum; table at
  probes/rq4/out/slot20_table.md.
- SIMD-on vs OFF: wins dominate (throughput 458 W / 9 L over both levels;
  `(?i)cat` 1 MiB -81% w16, -91% w32). Losses are pc16 per-call setup
  (+0.15..1.5 ns), the sparse-pick cell `(?i)azqb` at w16 (+55..79% on
  sparse subjects: the §R4.9.7.1 risk CONFIRMED; it wins at w32), and v14
  (VM, unexplained, a single cell).
- KB: large throughput wins (to -92%), 179 small losses in the dense-hit and
  short-span regimes. §6's never-loses rule is not met, so Q-RQ4-1 goes to
  Frank via main (leaning: keep KB; a density-aware distance rule over
  rank_ppm is the general fix, filed rather than built).

## 2026-10-11 — Frank's ruling on Q-RQ4-1 (direct to the kit)

- Q-RQ4-1 (KB loses small in 179 of 1396 RQ-4 comparisons, so rankuse §6's
  never-loses rule is not met). Frank asked whether a hit re-checks the whole
  run. It does, three times for `(?i)cat`: the filter, a full scalar
  verify, and the DFA restarting at state 0 (ideas.md 2026-10-11).
- RULING (Frank, 2026-10-11, "Ok. I agree"): KB stays the default. The
  vrun verify is trimmed to the positions the filter did not prove, and
  the dense-hit / short-span regimes are re-timed before KB's losses are
  called final. Posted as a responses notice with proposed D-entry text
  and a proposed request for main to file.

## 2026-10-11 — R-14 built (trim + padded word), slot21 prepared

- R-14 filed by main (D147 addendum 15) and acked. Lane r14b (opus): the
  position-trimmed vrun verify, deny `vrun-trim`, S793-S796. Frank then
  asked whether one wide masked compare beats single-byte checks. It does:
  the cost is loads and branches. A mid-run design-change message to r14b was
  MISSED (its report never mentions it; see memory
  pcrec-no-addenda-to-running-lanes), so a fresh lane, r14p (opus), built
  the padded word on top: one w4/w8 over the whole run in the main path,
  deny `vrun-pad`, S797-S799. r14p corrected my premise: the top lane has 0
  bytes past its run, so the main guard now reserves E = P - L extra bytes.
- Both merged into lane/memfn-r14 (74b8e0fd); light suites green in both
  lanes.
- Lane s21prep (sonnet): rq4 harness generalised to arm sets (3-arm mode
  reproduces slot20 byte for byte), plus the slot21 script: the heavy chain
  + 6-arm timing (slot21x: DEFAULT/NOPAD/FULL/KBDENY/FULLKB/OFF; FULLKB
  makes F-FK slot20's exact D-K control). Merged (bae70443). Dry run against
  worktrees/r14 green (02:52). Estimate ~3 h 50 min, timing last (137 min).

## 2026-10-11 — slot21: R-14 validated; the 6-arm reading re-opens KB at w16

- slot21 03:07-06:44 is green in every stage (r14p_report addendum).
- Padded word + trim beats R-13's full verify (478 W / 151 L). Trim alone
  is WORSE than full (261 / 375), so pad is required. SIMD-on vs off
  losses went from 63 to 33.
- KB: of slot20's 179 losses, 78 persist under R-14's verify. The exact
  control reproduces 110, so about 40% were noise. With a cheap verify,
  KB's w16 value shrinks (w16 throughput D-K 133 W / 59 L vs 188 / 6), and
  w32 still wins (190 / 18). Q-R14-1 goes to Frank: KB at w16?
- done: R-14 posted.

## 2026-10-11 — Q-R14-1 ruled by Frank: KB at w32 only

- Frank: "agree" to KB at w32 only (the kit's distance rule; no pcrec fact).
  Posted as a responses notice for main to file and request. The dense-KA
  w16 refinement is filed.
- Loss sizes from slot21, given to Frank:
  - D-K at w16: median 6%, max 35% (the ruling removes these);
  - D-K at w32: median 5%, max 18%;
  - D-F: median ~4%, but 11 comparisons at >= 10%, mostly w32 sparse
    throughput. These need a read-only triage lane.

## 2026-10-11 — R-15 built (precheck_assign_byte), slot22 read, delivered

- Main met R-15's D77 trigger (the L1 build through generic regresses: ipv6
  x1.87, ipv4 x4.48, dotted4 x46; a memchr gate restores the wins). Lane r15b
  (opus) built `precheck_assign_byte` (memchr ASSIGN, a third row of
  precheck.c's renderer before generic) and the kit's first SCALAR deny. It
  shows zero movers on main, and under a scratch rlhbuild merge the row
  serves entry + re-entry; deny == generic byte for byte.
- slot22 (08:31-12:51):
  - every identity sweep: 0 artifact movers (dumps only); deny sweeps 0;
    N2 clean; G2 full 199.9M/0; mech 13 rows COMPLETE zero.
  - Reds, each triaged:
    - G2 quick: 2 g2m4 POPULATION floors crossed by a subsample phase shift
      from R-15's landmark sites (no answer failed). Re-pinned 98000 / 48000
      by the file's rule; quick re-run green (ee365ab1).
    - test-axes: two EXISTING axes (-fno-hyb-reseed, -fno-cls-pack) lost
      cases in a slow/loaded window (1265 s vs ~252 s per axis); the
      kit's --memfn rows are not in test-axes. A quiet re-run of those two
      axes is green.
    - The variants sweep's 26 tag-floor lines are PRE-EXISTING (identical in
      slot21, before R-15). Floors are stale on main; reported to main.
- done: R-15 posted. Next is R-16 (KB at w32 only).
- Side thread with Frank (no kit time; UNSCHEDULED under [SPAN-ISEL]): the
  loss survey (accepted), the span surveys, negation as a wrap-around range,
  captures as span offsets, the four-engine taxonomy and cached class truth
  vectors for the VM. All in ideas.md on lane/memfn-ideas3.

## 2026-10-11 — the vrun loss survey (one pass, accepted)

- Frank: no compiler-flag fixes for the residual losses. Survey the loss
  items for an emit-time decline predicate, ONE effort, then accept and move
  on (the losses are only slightly above noise).
- Lane losssurv (opus, read-only) found:
  - no predicate for the padded-verify losses (layout);
  - none for KB's w32 dense-hit losses (density, which the kit cannot see);
  - the `(?i)azqb` w16 decline is reproducible but a net regression;
  - one hypothesis row, KB off when KA is very rare at w32 (one cell).
  It also corrected the slot21 "exact control" claim (RX_DFA_START changed
  on 20 cells).
- Frank accepted: build nothing; ideas.md gains the hypothesis, the pc16
  nested-check residue, and (Frank's addition) pcrec passing the kit more
  workload knowledge: density, subject length, byte profile, call pattern,
  from pcrec-analyze bundles. r14p_report gains the correction.

## 2026-10-11 — R-16 taken, built (lane r16b), merged into lane/memfn-r16

- R-15 and lane/memfn-ideas3 merged by main. R-16 acked (afc74283). The
  slot21 D-F triage the request asks to fold in was already done read-only
  (dftri_report, committed). It is not R-16's rows: 7 losses track the hot
  loop's layout, 3 are noise, and v05 shows a small 64k-only per-call cost.
  One-pass rule: no build.
- Lane r16b (opus): ops_of[] gains `npos` (1 at w16, 2 at w32), so
  vrun_kb() reads KB at w32 only (D147 add. 16). The w16 helper reads KA
  alone, standalone and as w32's rung. The deny is unchanged.
  - Re-pins: VRUN_W16_GUARDED_MAX 2700 -> 2400 (limits.md §8.3 hunk), G2
    VSHAPE_FLOOR none 19 -> 8, and simd_accept loses vrun-kb's w16 lines.
  - Check: G2 SIMD family 1b, KB_LEVELS={'w32'}, now also on the final
    block; three K35 populations.
  - S815-S819 all DETECTED; S753 still detected.
  - Light evidence: SIMD-off 0 movers; -fmemfn-simd movers are only w16
    helpers + the guarded stamp (classifier, every 8th pattern, bad 0);
    no-vrun-kb 0 movers; G2 quick 52,987,686/0. No abi event.
- Reviewed and merged (a8edd0f3); strict rc 0. The slot23 chain is staged at
  worktrees/memfn-slot/slot23/run.sh: identity sweeps on every arm plus
  simd and simd+no-vrun-kb, the classifier over EVERY pattern, G2 quick +
  full, make test, mech S815-S819 + S753.
- My calls (answer-free, same measured cost):
  - no test-axes: SIMD-off is identical and it sweeps no --memfn row;
  - no N2: applicability is unchanged;
  - no re-timing: the w16 text now IS the no-vrun-kb text, already timed in
    slot21, and the w32 helper did not move.
- Waiting on main's GO, which comes after the rlhbuild chain + L1 merge.

## 2026-10-11 — slot23 green, R-16 delivered; R-17 scoped

- Main gave the GO after L1 (00c97769, abi 75). Main merged into
  lane/memfn-r16: three doc conflicts resolved, strict green. slot23 ran
  21:35-22:43, all green (responses `done: R-16`). The variants rc 1 is the
  pre-existing thin-tag manifest, identical on the ref side. The emitted
  VARIANT_PINS go to main.
- R-17 acked on lane/memfn-r17. Lane r17s (opus, read-only) delivered:
  - SIMD-off is pure kit row work; the PF/hat FINDs already carry the set.
  - pcrec needs: N1 (the promised density facts) and N2 (a file-scope sink
    at the PF/MLINE door, SIMD layer only).
  - OFS/PRE have population 0. ci-strasse is no longer a set walk after L1
    (a bench re-measure is owed via main).
  - Leaning: one general term-list row family in pffind.c (memchr |
    SWAR term-OR | walk).
  - 65 twins checked exhaustively, 0 mismatches. The timing harness is
    ready (~8 min, a slot).
  - Merged into lane/memfn-r17 @ 79b3524f.
- Next: ask main for R-17's short timing slot. A D6 panel on the
  general-row design before any build. N2 is filed as a pcrec-side request
  only if the SIMD half is pursued.
## 2026-10-11 (late) — R-17 timing read + D6 panel r3

- R-17's twin timing ran on main's GO (22:46-22:59, core 14): 1,106 rows,
  void 0. The re-check was 0 mismatches. Reading:
  `docs/design/memfn/probes/r17/reading_slot.md`. Every form beats `table`
  except at 300k ppm i.i.d. find-all (SWAR +20%, memchr +18%, avx2 +24%,
  on the bench's dense controls).
- D6 panel r3 (3 sonnet critics, read-only), consolidated in
  `docs/dev/reviews/2026-10-11-r3-memfn-r17.md`. 36 ids. The direction
  holds; the design is not build-ready.
  - BLOCKER C1-1: the n = 0 wrap.
  - Correctness: derivation spec/tests, hook capture, endianness.
  - Rollout: one routing event, not two halves.
  - pcrec-side facts N2-N4 and spec hunks.
  - The measurement is not decision-grade (table non-monotone at 300k,
    i.i.d. placement, grid holes, K unreadable).
- Q-R17-1 (positive-evidence density admission, inert until N1) and
  Q-R17-2 (one routing event for every PF site) sent to main for Frank,
  with recommendations.
- HOLD: the revision-2 lane (setfind.md) waits for the rulings. The
  follow-up measurement needs a slot after main's twintime (~2 h from
  23:05).

## 2026-10-11 (late) — Q-R17-1 ruled (Frank, via main)

- Frank: "If it gets the above pattern [the dense [a-z]/[0-9] case], the
  right choice is just a forward search for the class." Main's reading
  equals the recommendation: the new row is taken only on POSITIVE
  evidence of sparse density; dense or unknown keeps today's forward class
  walk; the threshold is labelled UNMEASURED until the grid fixes it; N1
  (density facts) is the build trigger, and main fills it as a no-mover.
  Main records the decision.
- Q-R17-2 is NOT ruled. Main advises one routing event, timed after BOTH
  the kit's follow-up measurement AND D161's "search for the window"
  design (lane wingame), so the PF sites move once. Revision 2 holds the
  rollout open.
- Revision-2 lane r17r briefed: design + harness text only, no runs.

## 2026-10-11 (late) — WITHDRAWN: the Q-R17-1 "ruled" entry above (4100be02)

- Main corrected its relay. Frank's "just a forward search for the class"
  was about a different pattern (`\d+.*#`, D161's window-search case), NOT
  R-17's dense case. **Q-R17-1 is UNRULED**, as is Q-R17-2. Main brings
  both back to Frank. The previous entry stands only as a record of the
  misrelay. Nothing was built on it.
- Lane r17r was stopped before any work (its brief stated Q-R17-1 as
  ruled). It is relaunched fresh with both questions open.

## 2026-10-11 (late) — Q-R17-1 RULED by Frank (via main; D161 addendum 2)

- Frank, verbatim: "I like adaptive. But also, this depends on how the fast
  form is implemented. If it preserves its data between candidates it might
  be faster. Say we have the truth vector I mentioned and we save it. Or we
  have a circle queue of potential positions and we exhaust it before the
  next simd search."
- Main's reading (D161 add. 2): the dense loss is the per-hit RESTART.
  Design STATEFUL forms:
  - carry the block's match bitmask and pop the next set bit per candidate;
  - or keep a ring of candidate positions, drained before the next vector
    pass;
  - plus the ADAPTIVE switch.

  The follow-up grid measures them at the dense controls. The static
  positive-evidence gate stays only as a FALLBACK, if the stateful form
  still loses dense. State scope: per-site state across candidates within
  one call (the N2 family; the kit names the exact contract item). Across
  find-all calls the state would live in the versioned caller struct
  ([FINDALL-NEXT]/[IFACE-PUSH], later).
- Q-R17-2 is still unruled.
- r17r2 stopped before writing anything. Relaunched as r17r3 with the
  ruling in the brief.

## 2026-10-11 (late) — Q-R17-2 RULED + D155 relaxed (Frank, via main; D155 addendum 2)

- Main's summary of Frank's ruling (the verbatim quote is in decisions.md
  D155 add. 2):
  - The kit's emission restrictions were guidelines from the fixed-choice
    era, not hard rules.
  - The kit MAY emit composable lower-level pieces into the function body.
    It AVOIDS #if/#ifdef in body code: architecture choice lives inside
    lower-level helper definitions (an arch-versioned helper in the header
    is one way; others are allowed).
  - The kit may emit and OWN LOCAL STORAGE the body needs (the start-position
    queue, the carried mask), and decides whether it is emitted at all.
- Q-R17-2 = (A): ONE routing event, where the code fits neatly in a
  function. It is timed after the kit's follow-up measurement and D161's
  window-search design, so the PF sites move once.
- The state-slot contract item becomes "kit-owned local storage in the
  body". Main asks what pcrec must provide (a declaration site? its
  lifetime across candidates?). The revision answers that.
- r17r3 was stopped before writing anything. Relaunched as r17r4 with both
  rulings.
- Correction (main renumbered): Frank's 2026-10-11 Q-R17-2 ruling is **D155
  addendum 3**. "Addendum 2" in the entry above means addendum 3; addendum 2
  is the 2026-10-09 size-neutrality one. r17r4's note gets the citation
  fixed at review (it was briefed before the renumbering).

## 2026-10-11 (late) — D161 addendum 3: the window search subsumes R-17 (Frank, via main)

- Frank: "Ideally the idea of having kit handle 'search for window'
  subsumes other kit requests. It's a more general form of simple search."
- Main's reading:
  - a plain set FIND is the window search with ONE span of length 1,
    move-back 0, overshoot 0;
  - offset-set is a span at move-back k;
  - the presence gate / ASSIGN is a span whose window is anywhere ahead;
  - the handoff is a span with move-back K.
- R-17's interface and its one PF routing event are designed AS that
  degenerate case of the D161 contract, so the sites move once. The
  contract carries spans of classes, move-back, overshoot, minimum offset,
  a frequency table and a per-route consumer price; the reply names the
  window and which span it came from (docs/design/memfn/window_search_game.md).
- R-18 (the general request) follows main's chunk-2 design note. No main
  work starts before a session reset.
- r17r4 was stopped before writing anything. Relaunched as r17r5 with all
  rulings.

## 2026-10-12 — R-17 rev 2 delivered (design); sabotage ids allocated

- r17r5 delivered setfind.md, merged into lane/memfn-r17. The responses
  notice is f92a3013.
- Main allocated sabotage ids **S826-S843** (18). S825 is seambuild's, so
  setfind.md §12.5's S825-S842 shift by +1 when the note is next touched.
  Ratification of the window fields and storage waits for main's chunk-2
  note (its shape is discussed with Frank first).
- Running: r17dry (harness compile + reduced checks + DRYRUN, light, pinned
  12-15) and the light re-check panel r17k1 (soundness, opus) / r17k2
  (contract fit, sonnet).
- The follow-up timing WAITS for seambuild's chain DONE. Main offered a
  single pinned core alongside the chain; declined, because noise would
  defeat a decision-grade reading.

## 2026-10-12 — r4 light re-check + setfind.md revision 2.1

- r17dry: the harness is ready. Full sequence check 190 twins / 4.04G
  calls / 0 mismatches; planted 152/152; ASan+UBSan clean; dry run 619
  invocations, ~80 min.
- r4 light re-check (K1 soundness/opus, K2 contract/sonnet), in
  `docs/dev/reviews/2026-10-12-r4-memfn-setfind.md`: no blocker, 6
  must-fix, 24 ids.
- r17r21 applied them as revision 2.1 (merged b64c620b). It CORRECTED four
  dispositions against the code:
  - K1-5: a function mismatch is a compile error, plus "placed twice".
  - K1-6: the VM hat is defined at file scope near the req-run blocks.
  - K2-1: no flush-helpers change is needed.
  - K2-6: the R-17 rows are header-free via `__builtin_*`; mf_plan is
    gone.

  Signed W1 (D161's origin). Sabotage ids are S826-S843. The harness is
  unchanged.
- OPEN with Frank, raised by him directly: package density and future
  workload data as an ANALYSIS OBJECT rather than one `freq` field ("plan
  for change"). The kit answered with a leaning: one read-only
  `mf_analysis` per compile, tagged kinds present or explicitly absent,
  versioned; compile-wide distributions only, with a per-site slot
  reserved. Rev 2.1's §14 still drafts N1 as `mf_site.freq`; it gets
  rewritten once Frank settles the shape. No lane is launched on it.

## 2026-10-12 — RULED by Frank (direct to the kit): workload data as an analysis object

- Frank asked whether find-window requests need more data than byte rates,
  and suggested delivering it as an "analysis" object that can grow ("plan
  for change"). The kit answered:
  - yes (joint/adjacent rates, run-length profile, length class and call
    pattern, cpfreq, match density);
  - one versioned read-only object with tagged kinds;
  - option 1 (compile-wide distributions) versus option 2 (per-site derived
    facts).
- Frank: "i agree option 1 with options to add more data. pcrec should send
  what it has."
- Applied in setfind.md (amendment + W6 + §14 N1). Posted as a responses
  notice with proposed D-entry text for main to file.
- Frank, same day: "that said, be ready to make decisions without data."
  Recorded as a design rule: every kit selection is TOTAL with the analysis
  object or any kind absent; the no-data path is a stated decision (for
  R-17: the adaptive switch learns at run time); data refines a choice and
  is never a precondition. Added to setfind.md's amendment and to the
  proposed D-entry.

## 2026-10-12 — Frank's direction: body code over a set of primitives

- Frank proposed: readable body code over helpers defined above it, e.g.
  `char_vector_t w = load_vector(s+i);` with `char_vector_t` set by
  architecture and `load_vector` doing the memcpy plus endianness. He asked
  whether every artifact in a file shares one architecture.
- Kit answer: the architecture is the same in one TU, but the WIDTH differs
  (w32 to w16 to SWAR rungs). So the vocabulary is per width, emitted ONCE
  per file in a guarded shared block (the K80 ABI-block precedent), not per
  artifact. A file may mix SIMD-on/off artifacts.
- Frank: "i like your idea of a set of primitives to be used in the body. it
  provides a lot of flexibility to customize the solution." SETTLED.
- Next: fold into setfind.md as revision 2.2 TOGETHER with the follow-up
  timing reading (endianness moves into load_vector, closing C1-2 cleanly;
  forms are composed from primitives). The shared helper block lands in
  R17-a. No lane launched yet.
- Main filed it as **D155 addendum 4**. Main's note: the shared block is
  emitted scaffolding, so a byte it moves is a pcrec abi event in the same
  commit. Kit resolution for rev 2.2: the block is emitted ONLY when some
  site uses a primitive. In R17-a no row uses one, so the block is absent
  and R17-a stays zero-mover. The block first appears in R17-b, inside that
  step's one abi event.

## 2026-10-12 — Frank: stateful state hidden behind a next_candidate interface

- Frank asked why setfind.md favoured the mask over the ring/queue; the
  queue's interface is arch-independent. Kit answer: the doc's reason was
  COST (the mask is a compressed queue, with no drain loop), UNMEASURED and
  in the timing. Uniformity is better got by making the contract
  "next_candidate(&state, lo)", with mask or ring behind it per width,
  written in D155 add. 4's primitives (NEON's missing movemask absorbed by
  first_lane). The ring's real advantage is decoupling (any producer fills
  it).
- Frank: "i like your hide behind primitives idea. ultimately its a
  performance issue and avx512 does handle them extremely cleanly."
  SETTLED: next_candidate is the contract; mask/ring is per-width,
  measurement-chosen. AVX-512 mask registers suit the mask form; AVX-512
  stays unfiled (ubuntubudu Zen 1 lacks it; official verdict per targeted
  box), a later width row behind the same interface.
- Folded into setfind.md revision 2.2 with the timing reading.

## 2026-10-12 — R-17 follow-up timing (slot2) run and read

- slot2: 03:48-05:37, core 14, quiet box (main's gates ended 03:48:04,
  timing began after the ~3 min pre-checks). rc 0, 9,654 rows, void 0,
  perf 126. Checks: 190 twins / 4.04G calls / 0 mismatches; planted 152/152.
  Raw data probes/r17/out/slot2/.
- Reading (lane r17rd, `reading_slot2.md`, from times.tsv by script):
  - Stateful forms beat `table` at dense when the state carries
    (reset=inf): mask8_swar .86, mask64_sse2 .90, mask64_avx2 .88 at 300k.
  - The state helps only within a call. At reset=1 (find-all with true
    matches, today's API): mask8_swar 1.65, mask64_avx2 1.81, mask64_swar
    3.98, rings 25-32x.
  - Mask beats ring everywhere (the ring runs ~2x the branches, from drain
    work, not mispredicts).
  - Adaptive does not pay (it wins 4-9 of 574 rows).
  - K = 4 for the SIMD-off forms.
  - No single form passes K-1. Recommended: mask8_swar (SWAR),
    mask64_sse2, mask64_avx2. Residual losses (<= ~2x) are only in the
    state-lost dense corner, dense percall, and clustered runs.
  - Recommends ADMIT when density is absent (decide without data, Frank),
    declining only on positive evidence of density >= ~300k AND a
    non-carrying call pattern. That reverses §9.2's D_ABSENT-declines rule.
  - Caveat: the 64K table cost looks predictor-memorized (0.65 ns/B at 64K
    vs 1.91 at 1M), so the 64K dense rows are pessimistic for the forms.
    Real bench subjects are still owed.
  - Untested hypothesis: "stateless test first, pack the mask only on a
    nonzero word".
- To Frank: the findings + the admit-when-absent leaning + the cross-call
  state link ([FINDALL-NEXT]). No lane launched.

## 2026-10-12 — RULED (Frank, via main; D162 addendum 1): admit when density is absent

- YES: admit when density is absent; decline only on POSITIVE evidence of
  density >= ~300k with a state-losing call pattern.
- Condition: a bench relay on real subjects GATES the routing event. A real
  cell losing beyond the regression floor comes back to the kit before merge.
- The state-lost dense residual belongs to [FINDALL-NEXT] (chunk 5), not
  R-17.
- SETTLED. Revision 2.2 briefed (lane r17r22, text only).

## 2026-10-12 — rev 2.2 acked by main; bench advance notice I-148

- Main acked rev 2.2. It allocated sabotage ids **S846-S852** (7 more) and
  relayed the bench draft verbatim as I-148 (pcrec-bench fe77018c), an
  ADVANCE notice: the bench answers Q1-Q7 now, and the run waits for the
  R17-b pin plus main's mover census. §4's regression floor is adopted as
  PROPOSED; the bench's own rule wins if it has one. Decisions (1)-(5):
  none blocks. N5 (stem/guard) goes into main's chunk-2 note with the
  window fields and storage.
- Next: the r17k3 light re-check, then tell main R17-a/R17-b are ready to
  be requested (main files the R-n; it schedules after the re-check).

## 2026-10-12 — N6 agreed by main (same commit inside R17-b)

- N6 (refuse `-p` prefixes beginning with the reserved `pcrec_mfk_` stem,
  case-folded) lands in R17-b's abi commit. Main's two conditions:
  1. Enforce it in the LIBRARY's prefix validation (`valid_prefix`, every
     route: `-p`, .rxt target prefixes, libpcrec callers) by extending the
     existing check, not with a CLI-only clause.
  2. The spec hunk goes wherever the prefix contract lives (cli.md, and
     match_api.md or the library spec if they state the prefix rule;
     readers found by grep, D80).
- r17r23 (already running) was briefed before this. Both conditions go into
  the R17-b build brief, and the rev 2.3 text is checked against them at
  review.
- The corrigendum to I-148 goes to main with rev 2.3. The run cannot start
  before the R17-b pin anyway.

## 2026-10-12 — bench O-98 (answers to I-148 Q1-Q7) read

- Read from the local pcrec-bench clone at 55e3f678 (read-only, git show).
  - The bench ADOPTS §4 with two additions: (i) disjoint A0/A1 trial ranges
    are required, else a TIE; (ii) losses are also read at SUBJECT grain.
  - Its A1′ is a cflags no-op twin. That has the same layout, so the merged
    rule asks for a layout-perturbed A1′ (its align64 placement twin).
  - It will count density, run profile and candidates per match per subject.
  - It builds `import` + the host split before the pin, so dev-box phase-A
    records land in its store (kit prefers that).
- `bounded/dig-exact-8` throughput is 1M ppm, every candidate a match (the
  state-lost corner by construction). slot2 shows the mask forms winning at
  >= 500k even at reset=call, so the risk band is ~300-400k.
- Plan: after r17r23 delivers, the kit merges O-98 into the corrigendum as
  ONE gate rule (manager edit, text).

## 2026-10-12 — rev 2.3 merged; corrigendum relayed (I-149); R17-a build started

- r17r23 delivered rev 2.3 (11 r5 ids; K3-7 refined to the bare
  `pcrec_mfk` stem; K3-8 dropped the helper-set version, relying on K80's
  guard). The kit merged bench O-98 into the corrigendum as ONE gate rule
  (A1′ = the align64 placement twin, the 0.05 floor kept, disjoint ranges,
  subject grain, re-run before a loss counts).
- Main relayed the corrigendum as I-149 (with the Q7 answer). It allocated
  S853 (trace trap) and S854 (N6) to R17-b, annotated D155 add. 4 (the
  block first appears in R17-b, per-width, no version), and listed N5/N6,
  the sub-blocks, storage and window fields for its chunk-2 note.
- Lane r17a (opus) is building R17-a, the zero-mover seam (MF_SITE_ABI 11,
  define-then-use, mf_locals, reads_table, N4), light checks only. Main
  gives the heavy slot at the identity gate.

## 2026-10-12 — uses per activation counted on bench subjects (bench O-99 ask)

- Lane r17upa (counts only), `probes/r17/reading_upa.md`: answer-identical
  instrumented copies, bench subjects regenerated into scratch (manifests
  identical), 704 jobs, 0 violations, the planted control firing.
- Search-short: 1 use per call on every named cell, below break-even.
- Find-all: adl and alt-two/nested carry state; the other named cells take 1
  use per call but are sparse.
- The state-lost dense corner is the dense controls (46 cells), whose
  reading decides the decline arm.
- Hybrids: mostly 1 use per prefilter call; level-context and syslogbase
  carry state.
- Also: syntax/rec-* has 18 pre-existing pcrec give-ups versus libpcre2.
- §7's summary went to main for relay.

## 2026-10-12 — R17-a built and merged; main merged in; slot24 staged

- Lane r17a delivered R17-a (MF_SITE_ABI 11, window fields, decl_point and
  stem, mf_locals + refusals, mf_defined/reads_table, N4 door). Light
  evidence: 0 movers on every stream; G2 quick 52,987,686/0; S846-S849 +
  S478 DETECTED; 701 sabotage anchors resolve. Deviations D1-D9 are in
  r17a_report §6, chief among them D1: a new `u.pf.emit_define` hook after
  the run pre-check, which keeps R-15's handle-named local stable.
- Merged into lane/memfn-r17 (40442802), then main a080c69a (abi 76) merged
  in (76cef5aa; doc conflicts unioned, with the R-16 done/journal entries
  from main kept chronologically first). make/strict clean, and the memfn
  light suites green.
- slot24 is staged (worktrees/memfn-slot/slot24/run.sh): identity sweeps vs
  main on every arm plus trace, G2 quick + full, N2, make test, mech 67
  rows. GO asked of main.

## 2026-10-12 — session close (Frank /close); slot24 running detached

- slot24 (R17-a heavy validation) started 10:28 on main's GO, detached via
  setsid; tip c6a3bfea, ref a080c69a. Log worktrees/memfn-slot/slot24/run.log,
  verdict verdict.txt, DONE/FAILED marks the end, ~5-6 h. Main holds heavy
  work until DONE/FAILED.
- No lanes running. Wake rewritten for the next session.

## 2026-10-12 — wake; slot24 ended; triage; N2 floors re-pinned

- slot24 ended 12:14 with DONE, but five stages read red. Triage lane s24tri
  (sonnet, read-only): R17-a is a zero-mover on every sweep, G2 0 failed, and
  its sabotage rows are detected. The reds: main's pre-existing items (the
  spec-history line citation from d8fbbb54, the emit_sweep pins, the utf8
  `--extra` composition floor); mech S284 is expected UNDETECTED; and N2's
  `pf_walk` floor, which is the kit's own (R17-a's define-once/use-twice hat
  lowers the define count). Main's input (35c0b923 green) is consistent:
  d8fbbb54 postdates it.
- Re-pinned `pf_walk` 430563 and `precheck_assign_byte` 20088 (the
  PLACEHOLDER read OWED since R-15) from slot24's census. The re-read of
  slot24's N2 output is clean. No re-run needed. Next: R17-b.

## 2026-10-12 — R17-b built (lane r17b); review and the budget follow-up launched

- Lane r17b (opus) delivered R17-b as one commit, lane/r17b @ 174f3e320:
  abi 76 → 77, MF_SITE_ABI 11 → 12 (mf_result.keeps_storage, which pcrec
  needs to place the const heads), and N6 in valid_prefix. Its census
  (r17b_movers.py, full corpus 4,542 patterns): 957 byte / 2,866 VM / 964 utf8
  / 2,907 utf8-VM movers, SIMD-on identical, and the deny arm byte-identical to
  the base. Light checks green; S850-S854 detected solo. slot25 is staged and
  not launched.
- Its finding §6.2: T3's tripwire is crossed (`\w` 1,486 nodes > BUDGET/4,
  and `\W` 25,763 declines). §3.3 says the budget must then be DERIVED, so
  the follow-up lane r17b2 (opus, off lane/r17b) makes the search cheaper
  while preserving its result, against an exhaustive no-budget reference, and
  derives the bound. Formerly declined sets move in the same abi-77 event. My
  call (answer-free, and the design's own trigger): fix it before slot25 so
  the slot proves the final bytes.
- Read-only critics: r17bcritA (opus, kernel correctness) and r17bcritB
  (sonnet, the contract/abi package).
- Main fixed its three slot24 items on main (fae3987e8, e1fb68800). The
  merge of main into the kit branch comes before slot25. Kit-side
  spec-history citations reworded (d24f5741c).
- Main relayed rulings for R-18 (informational): D161 add. 4-6 (site
  parameters TRUE and REQUIRED; the window search is a chain of 1-2 simple
  searches; the consumer price is dropped, so the kit picks windows from its
  own costs plus the frequency facts); D162 add. 2 (frequency always
  arrives); [KIT-VERIFY] filed, unscheduled.

## 2026-10-12 — Frank: R-18's anchor choice is cost-every-scenario, pick the cheapest

- Frank, on the three-span overshoot case (ideas.md 2026-10-12): "I'm looking
  to see that there is a formula being used to determine the best scenario.
  Seems we can cost out all the scenarios then pick the best."
- Kit reading: R-18 enumerates every candidate chain the contract allows (each
  span alone; each span then a back-search to another), prices each with one
  formula from frequencies, form costs and overshoots, and takes the cheapest.
  Ties go to a canonical order, so the choice is deterministic.
- An open point for Frank: the house idiom is the first-match table (memory
  `pcrec-decisions-as-first-match-tables`). The proposal keeps the rows
  (candidate chains, each with its applicability and deny) but picks among the
  passing rows by cost, not by order. Asked; posted to main as a proposed
  D161 addendum.
- Frank answered the open point the same day: "We have a decision table that
  combines its various choices rather than pick one. We can use other models.
  The point is that it's organized, expandable/scalable, clear, observable."
  So R-18's priced argmin over declared chain rows is acceptable on those four
  properties. The design must show them: rows declared, a new form or link
  shape is a new row, one named formula, and every candidate's cost plus the
  winner listable ([LIST-TABLES]).

## 2026-10-12 — R17-b assembled on the kit branch; slot25 staged, GO asked

- Merged into lane/memfn-r17:
  - lane/r17b2: the pruned search. `\w` takes 21 nodes; `\W` 22, now covered.
    Max nodes are 29 on corpus and bench and 787 on the generated space, so
    MF_SET_BUDGET = 4 x 787 = 3148, derived. The search is SAME as the old
    unbounded one on all 1.37M sets, and 0 coverable sets are declined.
  - lane/r17c: the review fixes, plus `drop-kit-bytes` (main's ruling:
    declared `size` column, bit 55, 8 bits left). Its sabotage rows were
    renumbered S855-S858 → S867-S870 by me, because the lane missed the
    message.
  - lane/r17d: S820-S843 at their declared expectations (20 DETECTED;
    S823/S838 UNREACHED until the SIMD arms; S839 RESERVED), the T2 pin
    (2,158 sets), T4 (6,700 one-cube agreements, 0 disagreements), Q8/Q10,
    and an equivalent mutant at S828, replaced.
  - main, twice.
- Merge conflicts resolved: lanes/CLAUDE.md, and run_setfind.sh sections 5
  (T3) and 6 (cover). FILEPIN self-pinned to 02022d841. The slot25 census
  floors were re-pinned from r17b2's re-run.
- Light suites green on the merged tip. spec-history reached 145/0 after my
  critB-copy citations were reworded and main's k110fix line was fixed.
- slot25 is staged at worktrees/memfn-slot/slot25/run.sh (the in-tree
  docs/dev/optloop/slot25_run.sh with W = memfn-r17). It includes the full
  mech. GO asked of main (~8-10 h).
- Unrelated noted item: mf_set_terms_text's K=0 means "the row's own"
  (test-only). It is a sentinel default, so it should be revisited if it ever
  leaves test code.

## 2026-10-13 — slot25 / slot25b / ALPHA: R17-b is correct but not a uniform win; back to the kit

- slot25 (tip 2edd41a4e, full chain, 16:31-01:42) and every red were triaged by
  lanes before any log read:
  - make test: `test-fallback-table` had stale expectations from R17-c's
    `drop-kit-bytes` rung (s25tri b66529602, 143/0).
  - The census, listing and variants reds: the reference KREF lacked main's K110.
    slot25b reran the front half against KREF2 (lane/kref2 2c597c35f).
    Everything is GREEN, including 11/11 stderr movers predicted (s25b
    c62220fbe). VJUDGE's last red was a rule that was too narrow: auto
    resolves to the VM under lowered caps, plus 8 `-fprefilter` lines no arm
    measures (s25bv dca28769c, offline re-judge GREEN, controls RED).
  - Full mech, 736 rows: none of the 11 unexpected rows is R17-b's.
    - 9 are unreached on main too ([START-LANDING], [OPT-REVEND]); main's
      lane mechwit is re-pointing their witnesses.
    - S157 is undetected on main too (possessify); main is triaging it.
    - S689 has been the kit's equivalent mutant since R-13; flipped
      (s25mech d6f24fc4b).
  - ALPHA's check failed: the hex-dash cell is an offset-set site, not a mover.
    Replaced by hex-run (s25alpha 365752ee0).
- G2 SIMD pin fix for CI (main's defect): g2pin a9645193c, quick tier 1616/0
  under `taskset -c 0-3`.
- ALPHA timing (slot25c, against KREF2, CPU 14, quiet box 02:47-03:11):
  62 WIN / 87 REGRESSION / 11 NULL.
  - Big wins on sparse, narrow sets: dig on prose -42%, vm-hat-1 -35-45%.
  - Large losses on wide sets or dense subjects: bounded [a-z]+\b +20-37%
    everywhere, hex-run find-all +40%, dfa-hat on prose +23%, word-eq on
    mix64k +40%.
  - This is the risk rev 2.3 named: ADMIT when density is absent, with
    nothing reaching the §9 decline arm.
  - R17-b returns to the kit before merge. No census or bench pin yet.
    Lane r17loss (fact-gathering only) tabulates sets, covers, densities, a
    cost fit and a candidate admission predicate. The design is discussed with
    main/Frank before any revision lane.
- Ideas: XOR/AND/saturating-compare span test (Frank), a5d159a14.
- Unmerged into lane/memfn-r17 yet: s25alpha (with s25tri and s25b under it),
  s25mech, s25bv, g2pin, plus main (expect a conflict in
  run_fallback_table.sh, which is 146/0 on main).

## 2026-10-13 — Frank's direction on R17-b's losses; the vecspike spike

- Shown the absolute losses (2-5 ns per match; up to +599 us per 1 MiB
  find-all pass on `[a-z]+\b`) and the facts: the site is the plain class
  FIND, and the vector is kept within one rx_search but not across find-all
  calls.
- Frank's direction: try the serial head up to load alignment, keep the
  vector across searches (a hand-edit spike before any design), the same for
  the wider SIMD widths, and real-text subjects. `\W` for `[a-z]+\b` goes to
  main.
- Lane vecspike (opus) builds hand-edited variants of slot25c's artifacts:
  V0 walk, V1 R17-b, V2 align, V3 keep, V4 both, plus SSE2/AVX2 W-V1..W-V4.
  All are answer-checked and ASan-checked against the walk. Timing is OWED
  to one quiet slot; main has the heads-up.
- G2 SIMD CI fixes delivered to main as separate branches: lane/memfn-g2pin
  (5ce6ea692) and lane/memfn-g2isa (b09f95330).
- Frank's ruling, relayed by main (2026-10-13): preserving the find vector
  across a find-all sequence is a REQUIRED property of SIMD find forms.
  pcrec owes the seam that carries it. The mechanism is still under discussion
  (leaning: an artifact-owned find-all entry where the vector is a loop
  local), so nothing is designed against either. vecspike's V3/V4 values per
  cell at each width are a required part of the slot reading.

## 2026-10-13 — session close (vecspike slot armed by artifact)

- vecspike2 (multi-position class filter, P2-P4/P3W at w8/SSE2/AVX2) was
  delivered, correctness green. Candidates handed to the DFA: prose64k
  4,717 -> 34 at three positions. Timing is staged together with vecspike as
  spike1/slot.sh.
- Frank's design notes are in ideas.md: one class-vector producer for FIND
  and the VM, batched class requests (a multi-output cover), per-class live
  ranges for register sharing, and shift-or alignment for the multi-position
  filter.
- Main closed and handed the slot over by artifact: b3tri's chain.log
  ALL_DONE. spike1/arm.sh is armed detached and starts slot.sh on that line.
  The slot's end note is owed to the new main session.
- wake.md was rewritten. Fix branches are still unmerged into lane/memfn-r17
  (s25alpha/s25btip, s25mech, s25bv).

## 2026-10-13 — evening: spike slot read, D165 facts answered

- The spike1 slot ran itself after b3tri's ALL_DONE: 13:46-15:36. Both scripts
  are COMPLETE rc=0 (1,549 + 288 rows) with no answer mismatch.
- **D165 was ruled (Frank, via main 394287ce2).** The kit gets S bytes of state
  at alignment A, inline in a fixed `rx_iter` find-all iterator. S is derived
  from rows' declared needs. The build gates on a dense-tiny-match parity
  measurement and is undesigned until Frank discusses it; no redesign lane.
  The kit's facts answer: 24 B / align 8 at every width; one state per
  stateful FIND site; nothing from the caller beyond zero-init and the same
  subject. Main filed it as D165 add. 1 (0e370bb04).
- **Reading (lane spikeread, docs/dev/lanes/vecspike_reading.md):**
  - Keep vs unkept (`all`, W/R/N over 58 groups): 8 B 6/34/18, SSE2
    16/22/20, AVX2 23/18/17. Keeping pays only where reuse is large and the
    block is wide: hex-run and bounded at SIMD, -2 to -4 ns/use. It costs
    +0.2 to +2.9 ns with nothing to reuse.
  - The prologue wins only on bounded near hits at SIMD, and costs on
    hex-run 1 MiB, dfa-hat and vm-hat.
  - Width alone turns 7 of the 30 ALPHA losing groups, keep turns 1, the
    prologue turns 4 at AVX2. 17 of 30 survive every variant: single-call
    per-use cost, short subjects, word-eq, and hex-run on digits/mix.
  - vecspike2: P3 at SIMD is 4.4-39x the walk on dense dfa-hat, but K>=2
    costs +89-692% over P1 on no-candidate rows.
- Frank's ruled requirement (keep the vector for SIMD forms) stands. The
  reading says the per-call cost of the keep form needs to fall toward zero
  where nothing is reused. That is for the discussion, not a build.

## 2026-10-13 — late: Frank's regimes ask, costmodel delivered, batch idea

- Frank asked for the WHY of wins and losses: drivers, a cost formula,
  density, the information that decides, and rules of thumb. He then made
  absolute scale the organizing principle ("ocean liner vs dinghy": rules
  per regime, absolute ns not ratios). The first lane was stopped before it
  wrote anything and relaunched as costmodel2 with the regime framing
  (no-addenda rule).
- Main ran the parallel lane regimefacts. Split agreed: the kit owns C_use,
  block, keep, prologue and per-width c_byte at kit sites; main owns C_call,
  C_match and engine c_byte. One joint grid slot later; no timing until then.
- costmodel delivered and merged (docs/dev/lanes/costmodel_report.md). The
  regimes are DINGHY/TUG/LINER on L (bytes per call) and g (bytes per
  landing). The density variable is landings, not bytes. The kit-side
  per-byte constants agree with regimefacts to within 5%. A regime hint or an
  exemplar's bigram-derived gap cuts the SIMD-off regret from 7.5/7.2/0.2 to
  0.8/0.1/0.2 % of walk.
- Frank's out-of-box idea, BATCH MATCHES, is logged in ideas.md with two
  companions (popcount density for free; two-pass bitmap). It was relayed to
  main as an API matter: D41 5(c) once rejected batch find-all; a bounded
  batch on rx_iter does not meet that objection.

## 2026-10-13 — night: joint slot run and read

- grid1 (opus) built the F1/F3 harness with an ext-arm contract. Main's
  slotarms plugged in through it. The check was green (6319 legs), plants
  14/14. Three subject-design bugs were caught and fixed: dfa-hat landings
  were invisible with word filler; member-free subjects were answered by
  the required-byte pre-check; the streamed cycling was unprovable.
- The slot ran 19:33-20:56 (launched early, main agreed to hold), all rc=0.
  F2 skipped loudly: perf_event_paranoid=4, Frank's call.
- gridread (opus) read it.
  - costmodel's per-byte β and c_warm hold. c_cold is ~2.5 ns flat across
    widths.
  - L* for W=64 is 8-32 B. regimefacts' 1 KB n* was the 40 B tail.
  - The W=64 regime bounds move to L ≥ 8-32, g ≥ 4.
  - The fresh-data effect is landing unpredictability (branch prediction),
    not cache.
  - Alignment/prologue and stateless W=64 are out.
  - SWAR's term limit is 2 range terms.
  - With SIMD on, deciding needs the gap AND the span (1% regret); span
    alone is not enough in DINGHY. That makes D165's iterator span
    observation (F7) the open measurement.

## 2026-10-14 — D161 add. 11 received (main d038ef679): the kit is the candidate finder

- Ruling (Frank, via main): the window search and the form choice are ONE kit
  table over (stop, form), filtered by knowledge (P, E, A at compile time; N, M,
  H at run time). regime_tables.md rev 0.2's rows R0-R7 are the seed; the kit's
  copy will be the source of truth. Default LINER. Consumer cost FILED (trigger:
  a TUG cell losing for want of it).
- Before any regime-table work, I checked rev 0 against gridread (7b54791db).
  The R3 split, the per-site g*, the R0 range-term row and the SSE2 arms are
  all applied in rev 0.1/0.2.
- The kit's view is posted (responses.md):
  - The table has two evaluation times, set by `needs`: compile-time rows
    collapse; N/M/H rows become emitted dispatch.
  - R17-b splits into R17-b′ (no iterator: R0/R1/R2/R5/R6/R7 with an N
    dispatch) and R17-b″ (after D165: H rows, A3).
  - Requests:
    - E per stop: bigram to the kit.
    - Predictability: not now, trigger named.
    - A's default (unmeasured → WALK vs LINER): leaning a measured
      `generic` class; a question for Frank.
    - H grows S to 32 B.
  - Discussion only; no lane.

## 2026-10-14 — D161 add. 12 (main 1e68b7725); R17-b′ design note briefed

- Ruled (Frank, via main): each ISA has a GENERIC tuning class with MEASURED
  constants (the conservative envelope over measured boxes; Zen 4 only until
  F5). LINER stays the default and reads generic. An unmeasured specific class
  falls back to generic, never WALK, with its provenance listed. Accepted:
  - the two evaluation times;
  - forms-per-site in _MEMFN_FORMS;
  - the R17-b′/R17-b″ split;
  - H at 32 B;
  - E per stop incl. bigram (pcrec's to-do).
- NEW direction (Frank, binds both sessions): decision-making measurements
  are VISIBLE data with provenance, a formal method and remeasurement,
  distinct from constants. The organization is in discussion between Frank
  and main. Until it is settled, the kit commits NO measured constants to
  kit source.
- Briefed lane r17bp (opus, design note only): docs/design/memfn/r17b_prime.md.
  It covers the table as declared data, the compile-time collapse plus an
  emitted N dispatch, the knowledge fields, and the measurement seam (no
  organization chosen; the needed measurements listed with provenance). It
  also covers the bytes/abi/size, denies/G1/G2/sabotage, acceptance, the
  R17-b″ seam, and Q-R17P-n. A D6 panel follows before any build.

## 2026-10-14 — R17-b′ note and regime_eval rev 1 in; D161 add. 13 (row edits)

- r17bp2 delivered docs/design/memfn/r17b_prime.md (merged; the lanes
  CLAUDE.md conflict was resolved by keeping both lines).
  - On today's data R17-b′ is R0 + R7 only. The dispatch charges are
    unmeasured, and D166's one-run rule calls for a new set slot.
  - It recovers only 5.5% of ALPHA's OFF loss. The residual is mostly
    consumer/origin, not form.
  - 12 sabotage ids were requested.
  - Q-R17P-1 revises the kit's own proposal: forms-per-site go in
    --emit-facts.
- regime_eval rev 1 applies main's review: streamed judge cells, a
  consumer-bound class, P-MOVE. The D6 panel is running (crit-meas,
  crit-indep, crit-contract).
- D161 add. 13 (Frank, via main): until LOCKDOWN the kit edits rows freely
  on evidence, with no per-row proposals. Each edit is logged (row, evidence,
  commit) in the kit's table history, and main mirrors it. LOCKDOWN is the
  table that passes the judge and ships with R17-b′'s routing. After that,
  row edits are formal (a ruled diff, the replay delta, a mover census).
  This answer goes into regime_eval Q-2 after the panel. Pending decisions on
  evidence: R2, R3b, the amended-D2 row.
- Fixed a dangling §17 citation in costmodel_report (spec-history 145/0).

## 2026-10-14 — regime_eval panel, D166 add. 1 / 1.1, grid2 scope items

- The regime_eval D6 panel is consolidated
  (docs/dev/reviews/2026-10-14-r1-memfn-regime-eval.md): 33 ids, 2 blockers
  (I-1, I-2), all ACCEPTED. Rev 2 is in flight (lane regeval3). Main applied
  B-5/B-6/B-2/T20: regime_tables rev 0.4 has A = set id, I = ISA, R8 =
  amended D2, [MEASURE-SET] triggered by E3, and [TABLE-JUDGE] is filed.
- D166 add. 1 (Frank): perf counters are NEVER required by a set, method,
  gate, bar or tool. They are optional diagnostics that skip loudly into
  provenance, and sets are producible from timing alone. The consumer-bound
  class goes timing-only (sent to regeval3; VERIFY in the delivery, with a
  fresh follow-up if it is missed).
- D166 add. 1.1 (Frank): when counters are unavailable, every measuring
  script prints a SUGGESTION and never acts on it. The suggestion gives the
  current paranoid value, says that ≤ 2 enables the optional pass and what
  it adds, and shows the commands (`sudo sysctl kernel.perf_event_paranoid=2`;
  persistent: /etc/sysctl.d/99-perf.conf). Scripts never change system
  settings.
- zen4-grid2 scope so far (to be sent to main once rev 2 lands):
  - R17-b′'s three absent quantities: the per-call dispatch charge, the
    per-use dispatch charge, and the helper-walk scaffold;
  - regime_eval's streamed in-sample fit cells (to re-derive the G2 caps);
  - an OPTIONAL F2 streamed perf pass;
  - the harness prints the paranoid suggestion (add. 1.1);
  - one run, one method version (D166).

## 2026-10-14 — [REGIME-CORPUS] done (main); queued for regime_eval rev 2.2

- J1 population ready on main:
  - docs/dev/lanes/rwcorpus/ (fetch.sh, manifest.tsv: 88 files, 7 classes;
    bytes in worktrees/.corpus/);
  - docs/dev/lanes/rwquest/questions.tsv (177 blinded questions).
- Caveats to fold into regime_eval (rev 2.2, after regeval4's rev 2.1 lands):
  - prose/nonenglish are CRLF (`$`/`^$` semantics);
  - streamed buffers are taken across WHOLE files, never heads (`^TX\t` is
    0 in the first 4 MiB and 1,863 in the whole file);
  - pg8186/pg8453 (accents stripped) and pg20175 (mojibake) are
    MISLABELLED: report them separately or drop them;
  - the gazetteer is fixed-width, and tar members are NUL-padded;
  - the user agent saw spawn-time CLAUDE.md injections (the lanes index),
    so possible priming toward rare-literal/anchor cases goes in the §5
    independence table.
- FYI rulings:
  - D166 add. 2: the latest set until M2; stale defaults are carried with a
    flag;
  - [KNOW-SRC]: one shared knowledge-source module with round-trip identity;
    the listing's canonical view IS the input format.

## 2026-10-14 — J1b sealed; coverage finding with Frank

- J1b is SEALED on main (86a9638da, docs/dev/lanes/rwquest2/SEALED.md):
  - 165 questions, sha256 f41abc634bad5e498726b5fbe14a1b379ba8fbdb6fac185f541057bd631b32fe;
  - the bytes are in worktrees/.corpus/sealed/ (gitignored, unread);
  - unseal ONLY at the J1b judge step;
  - the prereg records the hash.
  The author never read rwquest's files (the lanes index injected its
  one-line summary, which goes in the §5.1 disclosure).
- The coverage finding (rev 2.2) went to Frank: only 31% of real questions
  reach the finder table. Main agrees with routing single-byte FIND and MLINE
  through the table (D161 add. 3/11): memchr/SWAR/W64 become form rows.
  Coverage would go to ~80%. A design note for later: the libc arm's staleness
  dep owner is `libc:<name>@<ver>`, a third owner for R-MS3. Waiting on Frank;
  nothing briefed.
- Open with Frank: Q-REVAL-12 (lean), 16 (constants + 2 loosenings),
  17 (k = 3).

## 2026-10-14 — D161 add. 14 scoped; R-21 filed

- sbscope and pcscope (read-only, on main's code) scoped single-byte FIND
  and the presence/handoff merge. winreq consolidated them into one request
  list.
- Coverage correction: rev 2.2's no-compile estimate (54/116) was wrong.
  Compiled: 170 of 172 have a start-search site; today's set-FIND table sees
  ~24%; single byte + presence/handoff bring nearly all of them under one
  request.
- NONE is unsafe on the VM hat and the no-DFA VM route.
- The pre-scan's benefit is the consumer's saved scan (add. 6's dropped
  price), so it defaults to KEEP.
- R-21 is filed (S964-S980), with main's answer-free rulings in.
- With Frank: Q-WR-1/2/3/6/9 and Q-REVAL-12/16/17.
- Next: revise R17-b′ for R-19/20/21 + add. 14 once Q-WR-1 is ruled, then a
  D6 panel, then build on a fresh branch from main. zen4-grid2 scope follows.

## 2026-10-14 — the evaluator parameters became a [KNOW-SRC] kind; digest spec (owed before E5)

- regime_eval rev 2.3 (a 72-row parameter table; k a visible lever) and rev
  2.4 (the [KNOW-SRC] kind `evaluator-params`; 4 derived rows moved to the
  measurement set under kit.reval_* keys) are merged.
- Digest spec (main, measure_sets §1/§9): FNV-1a-64, 16 lowercase hex. The
  input is the domain + `\0`, then each row in LC_ALL=C key order: key, `\0`,
  then the VALUE columns in declared order (int64 LE; empty = INT64_MIN; enums
  as their byte), with provenance columns excluded. The domain is
  `pcrec-<kind>-<N>`, i.e. `pcrec-evaluator-params-1`.
- OWED before E5 (fold into the E-step brief):
  - declare the value vs provenance columns in the file;
  - rename the domain;
  - recompute the digest with an INDEPENDENT script (not the producer);
  - record the domain in the header.

## 2026-10-14 — BUILD HOLD (Frank, via main)

- "don't start build yet." Under [REGIME], design notes and D6 panels
  proceed. NO build lane starts (kit or pcrec), and no slot-producing or
  set-producing timing run (zen4-grid2 included), until Frank gives an
  explicit go for that item, relayed by main.
- Held: the R17-b′ build, E3, the zen4-grid2 slot, and any other build.
  Allowed: r17bp3 (the R17-b′ design rev 2) and its D6 panel.

## 2026-10-14 — session close (pcrecdev3)

- **Done this session, in order:**
  1. The vecspike slot was read (the kept-vector table).
  2. D165 facts were answered (24 B / align 8).
  3. The costmodel regimes (DINGHY/TUG/LINER on L and g).
  4. The grid1 harness, then the joint slot run with main's arms, then gridread (L* for W=64 is 8-32 B; the fresh-data loss is the walk's branch predictor).
  5. The F2 perf pass (predictor confirmed; bounded prose is consumer-bound).
  6. The regime_eval design note, rev 1 → 2.4, through one D6 panel (33 ids) and Frank's rulings: the lean plan, the constants and loosenings, k = 3 as a visible lever, the parameters as a [KNOW-SRC] kind.
  7. The R17-b′ design note, rev 1 → 2, folding in D161 add. 11-15, D166 (+ add. 1/1.1/2), R-19/20/21, and the single-byte and one-window-request rulings.
  8. sbscope/pcscope/winreq scoping, filed by main as R-21.
  9. lane/memfn-docs (docs to main, merged).
  10. finder_history.md (row edits under add. 13).
- **Errors to remember:**
  - The rev 2.2 no-compile population estimate gave a wrong coverage figure (54/116). Corrected by sbscope's compiled census.
  - Two lanes missed mid-run rulings and needed follow-ups. Rulings to running lanes keep failing; prefer a short follow-up lane.
  - One conflict marker was committed and fixed in the next commit (29df767d3).
  - The heartbeat `cd` habit: bash `cd` in a command moved the session cwd twice. Use `git -C` and absolute paths only.
- **Open:**
  - the BUILD HOLD (Frank): no build or timing without a go relayed by main;
  - the grid2 go request plus Q-R17P-9..14 with Frank;
  - R17-b′ rev 2's D6 panel is the next kit work;
  - the I-152 bench answer;
  - the evaluator-params digest (independent recompute, domain `pcrec-evaluator-params-1`) is owed before E5.

## 2026-10-16 — wake; D167 (build hold lifted); lane/memfn-fd; B0, grid2 prep, panel

- Woke from the 10-14 wake (lane/memfn-r17 c90d65e53). No new requests since R-21.
- Launched R17-b′ rev 2's D6 panel under the hold: critics A (contract vs main's emitters, opus), B (zero-mover + checks), C (measurement), D (unlocks). Findings in worktrees/memfn-slot/panel-r17bp/.
- Main relayed **D167** (Frank: "build hold lifted. full steam ahead."): grid2 GO (B), R17-b′ build GO, Q-R17P-10..14 ruled. Cut **lane/memfn-fd** from main 063b4a4b4.
- Lanes: fddocs (docs sync, merged ff @ 90958d846; I fixed the R17-a marker to "lands at B0"), fdb0 (B0, opus), grid2p (grid2 harness + DRY, sonnet).
- E-1 agreed with main: B1 declares the `mf_analysis` slot (NULL-tolerant, unread before B3a); main fills it after B2.
- Panel so far: D (0 B / 5 M / 6 m / 6 unlocks). D1 = make the finder table a `kit_table` over `kit_walk` (B1 brief takes it). C (0 B / 6 M / 7 m). C3 adds ~3 cover shapes and C5 adds N=33..46 to grid2; these go to a follow-up lane after grid2p, since running lanes miss addenda. C7 puts the honest slot estimate at 88-113 min.
- Slip: I ran one `cd` into worktrees/memfn-fd (the kit's own worktree; no stray write). Absolute paths only from here on.

## 2026-10-16 (cont.) — panel closed; rev 3; main's Q-R17P-15..25

- Panel r1 on rev 2: A 0/11/12, B 1/9/7, C 0/6/7, D 0/5/6 + U1-U6. Record docs/dev/reviews/2026-10-16-r1-memfn-r17bp.md, 70/70 ids dispositioned. Main ruled A7/A10/A11 as D167 add. 1 (members; K5 retires only on a proven single-pass form, S derived; admission input as a fact).
- sweeparm merged (emit_sweep -fmemfn-simd/-fcomments floors, S981/S982). rev 3 merged (r17bp4): kit_table finder, mf_ask define-time query, 23 rows, grid2 1,501 group-arms (~91-129 min). I fixed two dangling spec cites in lane reports (test-spec-history 145/0).
- Main's answers: Q-15 mf_ask ACCEPTED; Q-16 accepted (main's ledger edit, + A23); Q-17, Q-18 (MF_USE_ENTRY), Q-20 (A7 wording → DFA_HAT and VM_ATTEMPT), Q-24, Q-25 accepted. **Q-19 AMENDED:** PCREC_NO_REQ_SET_LEAD stays a WORKING ALIAS of --memfn=no-pres-set-lead until [IFACE-PUSH], else refused with a diagnostic naming the replacement; never a silent no-op. **Q-21 updated by D163 add. 8 (Frank):** part layout = caller-settable switches (per part class + rank threshold), the five positions are presets; kit helpers follow the RESOLVED layout controls as facts (compound_entries rev 4, lane cmprev4, §R4); .o size is Frank's concern. **Q-22:** a kit lane adds run_axes.sh's --memfn= arm under emit_sweep's four terms. **Q-23:** S1017-S1026 for SN-1..SN-9 (+ spare for the run_axes plant).
- Next: runaxes lane now; B1 after B0 merges; grid2 harness → rev 3 spec after grid2p.

## 2026-10-16 (cont.) — B0 merged; grid2 harness at rev 3; B1 building

- **B0 (fdb0) merged** into lane/memfn-fd @ 608dc8b44: R17-a's seam cherry-picked clean onto main, MF_SITE_ABI 10→11, no pcrec abi event. 0 movers on every sweep; suites green; S846-S849 DETECTED. vm/variants rc 1 = main's stale emit_sweep floors (identical on both sides); main's lane swfix is fixing them. B0's make test is running (worktrees/fdb0-mt/build/mt/, from 11:45; main gave the box). Still OWED before delivery: floored simd/comments extras, mech (51 derived src rows + S526 S619 S681 S682 S722 S803), test-memfn-g2-full, and the N2 census. Main sequences the slots after E0's make test.
- **grid2p + grid2r3 merged** (29fc44944): harness at rev 3 §5.4, DRY green, no-clock gate 2,974 legs / 0 fail, 13/13 plants. Compiler is the record branch c90d65e53 (abi 77) with provenance recorded. Measured estimate ~75 min @5 launches. The 4 MiB streams are REQUIRED by regime_eval's judge condition. Open, my calls: staircase twins skipped (item 2 covers M16-M18); cross-launch threshold = max(A/A floor, NULL) accepted; evidence-only arms stay gate-pickable (conservative). Slot requested from main.
- **Process:** grid2r3 never re-read its rulings file and ran its no-clock gate 11:44-11:49 inside the HOLD. Disclosed to main. Lesson (again): a rulings file only works if the brief says "re-read before EVERY heavy command" up front. fdb1's brief says so.
- **B1 building** (fdb1, opus) from 608dc8b44. Sabotage S1017-S1025 = SN-1..SN-9; S1026 = runaxes' plant.
- OWED (main's message, 2026-10-16, before its reset): main's lane/swfix (6c81f60ac, PARKED until a make test) adds per-arm composition floors (COMPOSITION_EXTRA_PINS). An `--extra` arm without an entry then prints "COMPOSITION FLOORS: NOT APPLIED". Trigger: swfix merged into main, then main merged into lane/memfn-fd. Action: a kit lane adds MEASURED COMPOSITION_EXTRA_PINS entries for -fmemfn-simd and -fcomments beside sweeparm's DIFFER_PINS rows (same four terms). Expect a small merge overlap in emit_sweep.py.

## 2026-10-16 (close) — B1 merged; runaxes delivered; grid2 armed; session close

- **B1 (fdb1) merged** @ 6800f833b. It adds the finder table as a kit_table in shadow (19 rows, nothing routed), mf_ask with the reader shadow (census 240,967 asks, 0 aborts), the mf_analysis slot, mf_measures/consulted, form hashes, reader decls and method cards; MF_SITE_ABI 11→12, no pcrec abi event. Zero artifact movers; the declared --list-axes delta (5 fd-* rows) is confirmed by dumps_delta.py; the trace SET gate is clean. S917/S919/S921/S1018/S1019/S1020/S1025 DETECTED solo. Re-runs green: registry 79/0, G2 quick 52,987,691/0, link 8/0, rows 226/0, finder 868/0. OWED: full make test, mech derived rows, G2 full, N2 census; an emit_sweep one-sided ASSERT_ZERO mode for new denies. Findings: the R0/R7 floor token was unnamed (fdb1 chose kit.eps.findall.l64k; CHECK it); fields.def class space is full at 64; the record branch's R17-b also claims MF_SITE_ABI 12 (renumber at B4); R8's basis is DERIVED; F-B1-3 (MLINE ATTEMPT reader disagreement) goes to B2.
- **runaxes merged** @ 8c549afea: run_axes.sh `--memfn=` arm (precheck-assign-byte DIFFER both layers; vrun-* ASSERT_ZERO at default, DIFFER at SIMD-on; no REFUSES row). S1026 DETECTED (axesmemfn 36 fail); the full AXES=--memfn run took 4247 s with 12 jobs all agreeing (62,360 cells), no finding.
- **comppin merged** (main @ 353249282 in; COMPOSITION_EXTRA_PINS 37/106 for both kit arms).
- **B0 delivered** to main (10d9f43f4): make test 70/70, mech 57 rows clean, floored sweeps 0 movers, g2-full 199,850,927/0. Main is reviewing it; the merge waits for main's chains.
- **grid2 ARMED** (worktrees/memfn-slot/grid2/arm.sh, armed 15:52): it starts when main touches grid2/.go (~18:00, quiet box). Compiler: the record branch c90d65e53 (abi 77).
- **Frank (2026-10-16), /close:** never interrupt in-flight work at a close; wait for the lanes to finish. I had told fdb1/runaxes to wrap up, then retracted. The rule is in the close skill (9175611a3, on this branch) and in memory.

## 2026-10-16 (evening wake) — R-22 acked; B2 briefed; B1 heavy chain arming

- Woke (pcrecdev3), heartbeat `17,47`. grid2 still ARMED (waits on main's evening chain).
- **R-22 (R-MS6, harness-only arm-entry counter) acked into B2** (285590dc6). Main allocated S1079-S1088 to B2 + R-MS6; next free S1089.
- **B2 briefed** to lane fdb2 (opus, worktree fdb2 off lane/memfn-fd @ 285590dc6), plus F-B1-3, the fdb1 floor-token check, R-MS6 and drafts of main's C10 fixtures and C17 `site_kind` columns as a proposed diff. Main owns the landmark facts (its lane, tomorrow). The box must stay quiet 18:05-18:40 (maskbench timing); a rulings file in the fdb2 worktree carries this.
- **B1's owed heavy runs** (make test, mech derived + kit rows, G2 full, N2 census) are being armed by lane b1heavy (sonnet) on `worktrees/memfn-slot/b1heavy/.go`, pinned at 285590dc6 in detached worktree fdb1-mt. Main touches .go after grid2 finishes (~21:00-21:30); the chain runs overnight.
- **B2 built** (fdb2, lane/fdb2 @ 8d3540593, MF_SITE_ABI 13, no pcrec abi event). Light suites are green and 10 sweep arms show 0 movers, apart from the declared no-fd-d1 DIFFER flip. fdb2 stopped its first chain at the 18:00 HOLD, and its HOLD-gated chain2 never ran a step. I untracked the rulings file it had committed (a38419d84).
- **B2 review (b2review, opus, read-only): MERGE-WITH-FIXES**, 6 majors. The worst is that the readers ask mf_ask about a hand-rebuilt site that nothing ties to the define once the shadow is retired (a parallel mechanism). The others: S1080 cannot catch its plant; the routed floors are PLACEHOLDER; no sabotage row ever ran; charter sweeps owed (variants, trace, prefix); the floor-token change moved B4's manifest in place. Lane **fdb2fix** (opus) is fixing them in the fdb2 worktree, with runs gated on HOLD.
- **Ruling (kit):** keep fdb1's eps token fix to `kit.eps.streamed.slope` (rev 3 C4). B4's manifest becomes a new file, §3.5 is restated in the same commit, and fdb1's artifact is restored.
- **Tonight:** B1's chain runs ALONE at 285590dc6, as originally armed; B2 is not merged. Main has the lever-fence ALLOW edit and the R-MS6 wiring (cli/main.c, internal.h) to rule on.
- **HOLD maintainer:** `worktrees/memfn-slot/fdb2hold/hold.sh`, the source of the HOLD line in fdb2_rulings.md. It holds over maskbench, grid2 and B1's chain, and exits when B1's chain ends.
