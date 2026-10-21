# Responses from the kit — pcrec-memory-functions → the pcrec manager

PROTOCOL (D78; integration.md §20.1). ONE writer: the kit session (or a
kit lane through it), as a single-file commit prefixed `[responses]` on
the kit's branch; the pcrec manager merges it and reads this file at
wake. The pcrec manager never edits it. The reverse direction is
`requests.md`.

Per request `R-n` / defect `D-n`, append under a heading naming it:

- `ack: <date> — <plan>` when the work is taken up;
- `done: <date> — <kit commit>, MF_VOCAB <n> if the vocabulary moved,
  the abi event it rode (pcrec abi N → N+1), both-layer readings (D147)`;
- or `declined: <date> — <why>` (the manager rules what follows).

The kit's own durable notices (a re-tune that will move bytes, a switch
added or retired) go here as `N-n` items. Items are numbered and never
deleted; a superseded item says so in place.

---

## R-1 — R4b: the fused scan+verify measurement (post-handoff build)

- ack: 2026-10-05 — taken by the kit session (first session), branch
  `lane/memfn-r4b` cut from main d4d9ed90. Plan: ONE probe lane (opus:
  the new `swar` fused kernel's boundary/over-read argument is the hard
  part), worktree off `lane/memfn-r4b`, extending
  `docs/design/memfn/probes/twins/` (`tb_run.c`, `twins_run.sh`):
  `emit` re-copied verbatim from the post-handoff `-p rx` artifact at
  the run's pin (8a41efd2's copy retired as comparator), `swar` new,
  `ffl` SSE2/AVX2 and the byte loop carried; cells us/up/mi + K85's
  `cls-n-uc`; THROUGHPUT (gate/sweep, t-64k/t-1m) and PER-CALL (75
  short subjects); generated correctness set (len 0..129, hit at every
  offset, alignment 0..15) plus a planted wrong variant. Mac run is
  directional only; the Linux verdict run (ubuntubudu, gcc 15.2,
  taskset, ≥50 ms loops, base-vs-base floor, both layers) is ONE
  script handed to main's executor channel in a slot main names. No
  kit code, no pcrec byte moves.

- done: 2026-10-05 — MEASUREMENT ONLY: no kit code, no pcrec byte moved,
  no abi event, MF_VOCAB unchanged. Branch `lane/memfn-r4b`; the probe
  was merged from lane memfnr4b (7549a3b8) and its harness leak fixed
  (4ecea50b). Report: `docs/dev/lanes/memfnr4b_report.md` (§9 is the
  Linux read). Validation: `memfn_r4b.sh` on ubuntubudu via main's
  executor, `R4B-DONE status=0` (gcc 15.2, taskset, 3 launches, floor =
  max|emit−emit2|). Correctness 0 wrong and 10/10 planted defects caught
  in 5 builds, LSan included. Transcripts:
  `docs/design/memfn/probes/out/twins/r4b/linux/`.
  - **SIMD-off (`swar` vs `emit`): R4d's trigger is MET on union-select.**
    It wins every row in both regimes: throughput 1.4-2.0x, per-call
    1.4-2.0x. mod-i wins every row but one (an early-hit single gate
    call, +2.4 ns). userpass: run-first loses because the `=` lead
    rejects first; lead-first (`swlf`) is null there. The lead ORDER is
    part of the form.
  - **SIMD-on (`ffl` vs `swar`):** `ffl` wins every row at SSE2 and AVX2,
    except two 16 B rows at AVX2 (+0.36/+0.64 ns, a short-path detail for
    R4e′).
  - **K85 cls-n-uc:** the fused forms remove the dense-text loss in
    find-all and beat the no-gate floor. 1m sweep: emit 437,242, nosl
    403,594, `swlf` 242,662, `ffl` AVX2 97,527 ns. Single gate calls on
    dense text still lose at SIMD-off (64k/256k).
  - **For §15.5 (a kit design revision, after main's review):** the lead
    order is the kit's per-site choice, lead-first by default when a lead
    is present. A "lead can reject" density fact would decide it.
  - **Caveat:** `swar`'s raw rate (~0.18 ns/B) depends on unmeasured
    choices (2x unroll, exact zbytes); N-1 applies at R4d.

## N-1 (2026-10-05, kit session) — Frank's direction given to the kit directly: tuning constants are suspect

Frank, to the kit session: the R-1 `swar` probe's 16-byte (2x) hot loop
is an UNMEASURED default (inherited from `ffl`'s 2xVW shape) and is to be
noted as such. He dislikes hand-tuned numbers like that and prefers a
shape where the compiler picks the unroll. No action now. Standing
consequence for kit forms: every unroll width, block size, short-span
cut-over or threshold is measured (regime named), derived, or left to
the compiler, and is never adopted silently. Proposed for main to file
(a D-entry or a D147 addendum, main's call). Recorded in
`memfn/docs/journal.md` and as a comment at the loop in
`docs/design/memfn/probes/twins/tb_r4b.c`.

## R-2 — integration.md rev 4.5, light panel, Q53-Q55 recommendations

- ack: 2026-10-05 — branch `lane/memfn-r45` cut from main 08caf4a3. Plan:
  (1) lane memfnr45 (sonnet) folds R-1 §9 and D149 into rev 4.5 (§15.5
  lead order, §22 R4d trigger MET, R4e′ 16 B short path, D149 labels);
  (2) a light panel of 2 read-only critics on rev 4.5: A (opus) the
  contract vs the emitters at abi 61, B (sonnet) Q55's contradiction plus
  stamp/docs staleness; (3) the kit session consolidates
  `docs/dev/reviews/2026-10-05-r4-memfn-rev45.md` with a by-id
  completeness check and writes the Q53-Q55 recommendations itself.
- done: 2026-10-05 — DESIGN ONLY: no kit code, no pcrec byte moved, no abi
  event. Branch `lane/memfn-r45` (rev 4.5 by lane memfnr45; the kit
  session's §R4.5.5; panel r5; rev 4.6 by lane memfnr46). Reports:
  `docs/dev/lanes/memfnr45_report.md` and `memfnr46_report.md`.
  - **Panel:** `docs/dev/reviews/2026-10-05-r5-memfn-rev45.md`, with the
    critics' full texts beside it (the ack named it r4; r4 was taken).
    It found ONE BLOCKER, in rev 4's contract: the set-leads lead is
    REQUIRED on no-DFA routes (K65), not OPTIONAL. Fixed in rev 4.6, and
    R-1 is unaffected because its cells are all DFA-route. Nine MAJOR;
    all 23 findings ACCEPTED and applied (§R4.6.0 is the by-id table).
  - **Q53-Q55** are rewritten in §23 to the refined form and stay OPEN.
    Recommendations, for Frank:
    - **Q53:** yes, a separate `<PREFIX>_MEMFN_LIBC` line. It is a
      source-level inventory of the whole artifact's libc calls, with
      fixed-size idiom loads excluded. Its control comes from the
      compile (`nm -u` of an `-O0 -fno-builtin` object). Born in R4a′.
    - **Q54:** yes, N7 is listed `pending`. Its owner is D58/DD-12 (not
      D23); the definition widens to "search or span-compare site"; C17
      scans `src/enc/`; M7 bumps `MF_VOCAB`.
    - **Q55:** accept that `MEMFN_FORMS` is constant `none` at the
      default build until R4f. The bench attributes kit state by its
      recorded build recipe; C11's FORMS half is UNREACHED until the
      first SIMD-on form; R4d's spec hunk stops pcrec's own stamps
      describing the scan form. Filed: an always-present
      `<PREFIX>_MEMFN_OPTS` line (if Frank wants attribution in the
      artifact now, it rides R4a′ cheaply) and a plan line.
  - **Left as is:** line citations outside §14-§16 (history and §19).
    They are converted when next touched.

## R-3 — R4a (the kit skeleton), then R4a′ (the stamps' abi event)

- ack: 2026-10-05 — branch `lane/memfn-r4a`, which carries main with
  R-3. R4a goes first and lands on its own branch tip with its own
  `done:`. Plan, three lanes:
  - (1) `memfnskel` (opus): `memfn.h` (MF_SITE_ABI 2, MF_VOCAB 2, MF_NS),
    the `mf_*` entry points, the generic scalar row, K1 reference
    functions, `src/options.def` born empty with
    `mf_options()`/`mf_opts_check()`, the `--list-axes` `memfn` section
    header (with its spec hunk if caller-observable), the Makefile
    wiring, C15/C16, `PROVENANCE.md`;
  - (2) `memfnmanifest` (opus), in parallel:
    `tests/memfn/site_manifest.tsv` (every site `pending`, N7 included)
    and C17. The static half is live over `src/gen/` + `src/enc/`; the
    dynamic half is declared UNREACHED until a site calls `mf_emit_site`;
  - (3) after (1): G2's first tests from a D27-blinded author in a cell,
    written from the contract and `memfn.h` alone.
  Landing bar: identity gate 0 movers, `make strict`, Mac `make test`
  in a slot main names. R4a′ follows on its own branch, and its abi
  number is agreed with main before it lands (START-SET's events).
- done: 2026-10-05 — **R4a (R-3 part 1) DELIVERED: zero movers.** Branch
  `lane/memfn-r4a` @ (this commit's parent chain from 3495afe1, which
  includes main f3c726d7). Reports: `docs/dev/lanes/memfnskel_report.md`,
  `memfnmanifest_report.md`, `memfng2_report.md`, `memfnfix_report.md`.
  - **Landing bar:**
    - identity: `emit_sweep.py --ref f3c726d7` shows 0 movers on all
      four artifact streams (4,065 / 4,066 / 4,066 / 102). The one dump
      mover is `--list-axes` (+ the `#section memfn` header, intended,
      spec hunk in registry.md §6 / table_contract.md rule 5 / cli.md).
      The self-check passed.
    - `make strict` is clean.
    - Mac `make test`: 52/52 sections ran (6,272 s). The one red,
      `test-codegen`, is `run_inline_capability.sh`'s "nm could not read
      arm_a.o", darwin-only and PRE-EXISTING (the base binary fails it
      identically). Every other section is green, including the new
      test-memfn-link (C15/C16), test-memfn-manifest (C17) and
      test-memfn-g2 (G2 quick).
  - **Charter vs committed:**
    - memfn.h (MF_SITE_ABI 2, MF_VOCAB 2, MF_NS), the generic scalar
      row and K1: DONE;
    - options.def born empty + mf_options/mf_opts_check + the
      `--list-axes` `memfn` section (floor UNREACHED until R4d): DONE;
    - Makefile wiring, with libpcrec linking the kit and calling only
      mf_options: DONE;
    - the site manifest (13 rows, all pending, N7 included) + C17,
      sabotage rows S510-S512: DONE. At the main merge it was re-pointed
      for START-SET's `pcrec_emit_find`, and the vocabulary learned the
      format-hole walk;
    - G2: DONE, D27-blinded. It found kit defects F1-F3, all fixed;
      quick 21.7M/0, full 137.6M/0, every witness firing;
    - PROVENANCE.md, C15, C16: DONE;
    - contract rulings on G2's questions: integration.md rev 4.7.
      Addendum 10 is folded (Q53-Q55 RULED; the libc record and N7
      scope are the design of record).
  - **OWED (owner, trigger):**
    - G2 coverage of the newly refused shapes (kit, a blinded author at
      G2's next touch);
    - Q-G2-5, reverse ADVANCE (kit, at M3's design);
    - the bench's list_axes readers select the main table (bench, I-128).
  - **Next:** R4a′ (the stamps' abi event) on its own branch, AFTER its
    abi number is agreed with the pcrec manager.
- ack: 2026-10-05 — **R4a′** on `lane/memfn-r4a2` (an ASCII name for
  R4a′), cut from main after R4a merged. ABI ORDER per the pcrec manager:
  START-SET stage 2 takes 62 and R4a′ takes 63, landing AFTER stage 2.
  Lane `memfnstamp` (opus) builds everything except the bump: the two
  stamp lines on every artifact, the libc inventory and its `nm -u`
  control (C11's LIBC half; the FORMS half UNREACHED), the D80 spec hunk
  and sabotage rows from S513. The abi bump plus re-pins found by grep
  is the LAST commit, made after merging main once stage 2 has landed.
  Validation: the Linux make test via the manager's executor, by day,
  plus the census (each artifact moves by exactly the two lines and the
  abi digit).
- done: 2026-10-06 — **R4a′ (R-3 part 2) DELIVERED: on main as abi 63**
  (merge 340d8fef of `lane/memfn-r4a2` @ a0aefc40; code ends at
  49ace440). START-SET stage 3 stacked on top as abi 64 (8148e034).
  - **The abi event it rode:** pcrec abi 62 → 63. Re-pins found by grep
    (memfnbump_report.md, the `g1` grep row), stamp values, D80 spec
    hunk, all in the bump's own commit chain.
  - **MF_VOCAB:** unchanged (2). No kit search form exists yet, so no
    search byte moved.
  - **Linux verdict (main's executor, at eef95511):** 53/53 sections
    ran. The one red, `test-encoding-checks`, was a CHECK-side gap
    (`RX_MEMFN_LIBC` follows the excised `rx_reqrun` block), attributed
    by main's lane enctri and fixed on main with a failing-direction
    control. The `*** [test-` grep is clean with that fix.
  - **Census vs 57db5152 (Linux):** CLEAN. Each artifact moves by the
    two stamp lines and the abi digit, plus the one named
    `RX_VM_PREFILTER_WHY` value that main accepted.
  - **Both layers (D147):** SIMD-off is the only layer that exists:
    `-fmemfn-simd` has no form until R4e′ (Q55), so every artifact
    stamps `MEMFN_FORMS none`. No search code moved, so G1 has no
    population: nothing to time at either layer.
  - **Leftover worktrees:** `memfnstamp` and `memfnbump` pruned via
    `scripts/wtprune --apply`. The nested `worktrees/memfn/worktrees/
    memfng2` (+ cell) stays on Frank's raw-removal list.
  - **OWED (carried from R4a):** G2 coverage of the newly refused
    shapes; Q-G2-5 (M3); C11's FORMS half UNREACHED until the first
    form.
  - **Next:** R4c (the M1 migration) waits for R-4 in requests.md. No
    R4c code before it is filed.

## R-4 — R4c, M1: the composite PRE site + the offset-skip trio migrate, zero movers

- ack: 2026-10-06 — branch `lane/memfn-r4c` cut from main 691a8b7c
  (contains 05c33ce0). Plan:
  - (0) a read-only opus scoping pass maps the migrated emitters, every
    start-DECISION read inside them (the boundary list R-4 asks for),
    the mech rows whose `SAB_BEFORE` lives there, and the current state
    of C4/C5/C10-C14/C17 and I2;
  - (1) one opus build lane does IMPLEMENT then REPLACE on
    `lane/memfn-r4c`. The decision reads stay on pcrec's half and are
    NAMED in its report;
  - (2) the checks and the I2 VM-hybrid witness go to a second lane
    only if (0) shows they are disjoint from (1)'s files.
  Heavy runs: the identity gate and suites go through the Mac suite lock
  in a slot main names, then the Linux verdict through main's executor.
  Any byte move is a STOP-and-report defect, never a re-pin.
- note: 2026-10-07 — **R4c MERGED to main** (81bc13de; abi stays 65). The
  Linux verdict is green at 91f5b607 → abae07fa → 5645a37a. The pcrec
  manager's review verdict: MERGE-READY WITH LISTED FIXES, no blocker
  or MAJOR. The fixes are taken as **R4c′** on `lane/memfn-r4c2` (cut from
  main 81bc13de). None moves a byte:
  - (a) re-pin r4ccore §3's B1-B18 at current-main line numbers (the
    list predates the FLAGBITS merge);
  - (b) add two decision reads: `pcrec_fact_req_run(cx)->len >= 2` at
    emit_dfa.c:1517, and ofs_pred_of's per-term need classification
    (:1095-1104);
  - (c) `pcrec_emit_req_byte_check` (:1503) emits nothing when
    `job->mf_pre` is NULL: fail the compile when the admission says a
    pre-check is emitted;
  - (d) an inert-branch plant in `memfn_r4c_i2.py --selftest`;
  - (e) C11: also compile `-fmemfn-simd`, or correct libc_census.py's
    docstring (default IS -fno-memfn-simd);
  - (f) `c4_populations/.../m_lahf-lm.txt` is 0 bytes (gcc spells it
    `-msahf`): population loading must FAIL on an empty dump. The
    re-probe was asked of main (→ `worktrees/r4c-lx-results/gccmacros2/`);
  - (g) S524/S525 need the `checks failed: 0` reach line;
  - nits: S511's header prose; `strategy_denials` naming in
    lib/pcrec.h:1128 and tuning §2.43.
  (a)+(b) gate main's C1. Validation: make strict, the touched sections,
  the solo mech rows, and the zero-mover gate vs the new main. R4c's
  `done:` follows R4c′ (its draft is in
  `worktrees/r4cscope-scratch/r4c_done_draft.md`).
- done: 2026-10-07 — **R4c (R-4) DELIVERED: M1 migrated, ZERO MOVERS.**
  Branch `lane/memfn-r4c` @ 91f5b607 → main 81bc13de (with r4clx/r4clx2 on top). Linux verdict at 91f5b607 / abae07fa /
  5645a37a: the later commits add only checks, scripts and docs, and
  nothing under src/cli/lib/memfn changed between them.
  Reports: `docs/dev/lanes/r4ccore_report.md` (§3 is the BOUNDARY LIST),
  `r4caxis_report.md`, `r4cchecks_report.md`, `r4cfix_report.md` (§10
  startset re-pin + §10.1 per-row facts), `r4clx_report.md` (+ the kit
  manager's addenda 1-2).
  - **Abi event:** NONE. `PCREC_ARTIFACT_ABI` is unchanged: 64 at the cut,
    65 after main's flagbits merge. MF_VOCAB is unchanged (2). MF_SITE_ABI
    2→3 (Q-G2-18, `mf_site.on_miss_leaves`), kit-internal, no artifact byte.
  - **Landing bar:**
    - zero-mover gate vs e6e6d6eb: streams 1-4 have 0 movers / 0
      asymmetric; the only dump mover is `--list-axes` + the two declared
      memfn-simd rows (judge `memfn_r4c_gate.py`, rc 0);
    - I2: 94 arms, every axis × both comment tiers + the M1 denies at
      utf8 + `--arms start`; every arm 0 movers. The memfn-simd pair are
      inertness arms (per-side DIFFER 0/0). Three declared composition-floor
      exceptions, each measured on both sides (`memfn_r4c_i2.py`);
    - make strict clean; Linux make test green (one test-startset re-pin,
      one C4 environment fix);
    - mech: 35 rows, each run alone, all DETECTED/reached; [SABANCHOR]
      green;
    - axes pair and C11 green.
  - **Mech re-point count:** 20 rows anchored in the M1 emitters, not ~28:
    11 re-anchored (kit-side S464 S265 S454 S185 S447 S450 S455 S279;
    pcrec-side S285 S460 S511), 9 unchanged. S514 re-aimed. S287 now
    DETECTED. S472 lives in `pcrec_emit_start_zero`, not `emit_req_handoff`.
  - **Boundary list (for main's fold):** B1-B18 at file:line, r4ccore
    report §3. Every start-decision read stays on pcrec's half.
  - **Contract moves:**
    - Q-G2-18 CHOSEN by the kit manager (pcrec states `on_miss_leaves`;
      the kit never parses hook text);
    - D145 addendum 1 provenance on the moved arms;
    - C12 memchr 8→2;
    - C17's dynamic census is LIVE (the `pcrec_memfn_define` door);
    - the memfn-simd pair is born inert (D80 hunk: tuning.md §2.43,
      registry.md §6, match_api.md C11).
  - **Sabotage ids used:** S518-S529 (the S510-S529 block is EXHAUSTED).
  - **OWED (owner, trigger):**
    - G2 coverage of the newly refused shapes and of `on_miss_leaves` at
      both values (kit, blinded author, next G2 touch);
    - Q-G2-5 (kit, M3);
    - the matrix/emit_sweep backlog (a)-(d) (main's admin lane);
    - plan.md [MECH-SAN-ARM] loses S287 as its motivation (main).
  - **R4c′ (the review fixes) DELIVERED:** branch `lane/memfn-r4c2` @
    6957810d (code at ab61b0db) → main 993f8c1d. Report
    `docs/dev/lanes/r4c2fix_report.md`. Items:
    - (a)+(b): B1-B21 at file:line, plus B19 (req_run len>=2) and B20
      (ofs_pred_of's need classification);
    - (c): a loud fail in `pcrec_emit_req_byte_check`, with row S566;
    - (d): the I2 selftest inert plant;
    - (e): C11 covers both layers;
    - (f): `m_sahf.txt`, with an empty dump now FAILING;
    - (g): the S524/S525 reach lines;
    - the nits;
    - also the S526 filescope anchor (sabotage_anchors.py).
    Linux verdict at ab61b0db (294 s): the gate `--zero-dumps` vs
    81bc13de is 0 movers / 0 asymmetric on every stream; S511 S524 S525
    S526 S566 are each COMPLETE with 0 unexpected/undetected/unreached/
    anomalies. make strict is clean. Abi event: none.
  - **Next:** R-5 (M1b) on `lane/memfn-m1b`, cut from 993f8c1d.

## R-5 — M1b, runcmp migrates, zero movers (after R4c′)

- ack: 2026-10-07 — queued behind R4c′ (lane r4c2fix, in flight on
  `lane/memfn-r4c2`). Once main merges R4c′, M1b gets its own branch,
  `lane/memfn-m1b`, cut from that main. Plan: (0) a read-only scoping
  pass maps runcmp's emitters, bit 43's crossing (§14.10), `RUN_WORDS`
  as a kit stamp, the mech rows anchored there, and any start-decision
  read (if one exists we STOP and name it, per R-4's boundary rule);
  (1) one opus build lane does implement-then-replace. Sabotage ids:
  S566+ (main, 2026-10-07); the exact block is confirmed with main
  before the build lane is briefed.
- done: 2026-10-07 — **M1b (R-5) DELIVERED: runcmp migrated, ZERO MOVERS.**
  Branch `lane/memfn-m1b` @ 0125aeb5 → main 1c037dce. Reports:
  `docs/dev/lanes/m1b_report.md` (§3 + §3.1: D1-D12 at file:line,
  cross-checked against stc1 §2, AGREE, no collisions) and
  `docs/dev/lanes/m1bfix_report.md`.
  - **Abi event:** NONE. MF_SITE_ABI 3→4 is kit-internal (stamp_int,
    run_cmp retired, note's helper role ended); MF_VOCAB stays 2.
    integration.md rev 4.8 (§R4.8; §14.8 corrected: RUN_WORDS needs an
    unquoted sink op).
  - **Landing bar:**
    - Linux full verdict at 5f0f4dca (17,582 s): gate 0, mech 0 over
      14 rows, axes 0, C11 0, I2 94/94, strict 0. make test was green
      except test-memfn-g2, whose cause is known and fixed;
    - Linux test-memfn-g2 at 0125aeb5: checks failed 0;
    - Mac make test at 20b9d3cb: only G2 red (the same cause);
    - Mac gate vs e947b406 (after [START-TABLE] C1): 0 movers on all six
      streams.
  - **Mech:** 7 rows re-anchored (S267 S443 S444 S445 S279 S285 S454),
    3 adjacent checked (S514 S516 S528), S570-S573 new. Every row was
    hand-planted.
  - **Sites:** VMRUN delegated; VERIFY carried as an OFS/PRE term
    (Q-M1b-6); C12 12→9; C5 28→34 rows.
  - **Found and fixed along the way (K96):** R4c's ofsskip arm accepted
    sites whose miss is not `n` or that state a floor. This was an
    unstated precondition, latent since 81bc13de and unreachable from
    pcrec. Also, G2's h_note stub wrote bare text where the contract
    asks for a comment.
  - **OWED (kit):** the K35 G2 reach extension (ofsskip / precheck with
    on_miss_leaves / the words row), now running as blinded lane g2x on
    `lane/memfn-g2x`. Q-G2-6 confirmed as written: `floor <= lo` is a
    caller precondition for EVERY site; G2 becomes a conforming caller.

- notice: 2026-10-07 — **[MEMFN-ROWCON] opened (Frank, after K96).**
  Every kit row checks its own contract: a per-row ALLOWLIST of honoured
  site fields plus one shared gate that declines the rest, so a new
  contract field is declined by every row until someone states otherwise.
  It covers visibility into row decisions and a reach floor per row. Plan
  is an audit → light design → D6 panel → build, all zero-mover for
  pcrec. **Please add the plan.md row** under [MEMFN]. No pcrec-side
  change is expected unless the design asks for an explain/trace hook,
  which would go to you as a request.
- notice: 2026-10-07 — **[MEMFN-ROWCON] Q-ROW-1 RULED by Frank (directly
  to the kit session); proposed decision entry:** "Kit contracts carry NO
  SILENT DEFAULTS: every value a row's output depends on is stated
  explicitly (named tokens, e.g. `MF_MISS_N`, never NULL-means-X); a row
  that reads an unstated field refuses loudly. Caller text is SNAPSHOT
  once into reserved `mf_` locals, inside parentheses, at the top of every
  delegated site; text with comments, `#` or backslash is refused, and
  `on_miss`/`on_cand` must be a jump statement or a braced block. The
  snapshot is a pcrec abi event (every delegated site), accepted for
  correctness; it lands with G1 at both layers and its deny
  `--memfn=no-snapshot`." Coming to you: **R-6** (pcrec's hook builders
  state `MF_MISS_N`, `"0"` and the rest explicitly; zero movers) when T3a
  is cut, and the T3b abi event, sequenced through you. Design:
  docs/design/memfn/row_contracts.md rev 2.1.
- notice: 2026-10-07 — **[MEMFN-ROWCON] Frank's rulings (given directly
  to the kit session); proposed decision entries:**
  (1) Q-ROW-1 as clarified (Q-ROW-5): "A kit row may USE only a value the
  caller STATED; it never presumes one. Unstated fields are wildcards,
  not defaults. A row that needs an unstated field declines, and if no
  row can serve, the kit refuses and names the field. Not every field
  must be stated, only those the chosen row uses."
  (2) Q-ROW-1(c): caller hook text is SNAPSHOT once into reserved `_mf_`
  locals (a pcrec abi event, accepted for correctness), with refusals for
  comments, `#`, backslash, and bare break/continue in kit loops.
  (3) Q-ROW-6: the snapshot has NO public deny (D144 item 4 exception for
  a correctness change); G1's comparator is the pre-snapshot commit.
  (4) Q-ROW-4: D146's charter widens. The kit hosts a general first-match
  table engine (Layer 1) as a utility under MF_NS; pcrec's tables MAY
  adopt it per table (an offer, after START-TABLE C7).
  Design: docs/design/memfn/row_contracts.md (rev 3 to follow); reviews
  r1 and r2 under docs/dev/reviews/2026-10-07-r{1,2}-memfn-rowcon.md.
- notice: 2026-10-07 — **[MEMFN-ROWCON] N2 census DONE; the R-6 list.**
  The run was on the Mac, 15:11 to about 15:55, against main merged into
  lane/memfn-rowcon at 5fc4b0e5: 107 axis arms (deny and force, both
  comment tiers, utf8-scoped) × default/VM/composition. Results:
  958,292 compiles, 0 timeouts, 0 sites with no serving row, 1,072,494
  sites traced. The 129,937 would-decline verdicts collapse to EXACTLY
  THREE cells, all R1 (`miss` used, unstated):
  1. ofsskip, form FUNC / op FIND / handoff RETURN, at DEFINE (56,104
     sites);
  2. the same ofsskip site at USE (the call) (56,104);
  3. precheck, form STMT / op ALL_PRESENT / handoff ASSIGN, at USE
     (17,729).
  No other row, field or phase would decline, and nothing is R2.
  **Please file R-6:** pcrec states `miss = MF_MISS_N` in the hooks of
  (a) the offset-skip site's define AND call hooks (`ofs_site_define` /
  its use, src/gen/emit_dfa.c) and (b) the PRE ASSIGN handoff's use hooks
  (`pcrec_emit_req_byte_check`'s ASSIGN route). It is zero-mover, and
  nothing refuses until N3. The kit side adds the `MF_MISS_N` token to
  memfn.h in the same unit, so R-6 lands after the kit branch with the
  token merges (or ships the token itself; your choice). Reach from
  pcrec: generic 0 (declared total-fallback), ofsskip 56,104, precheck
  299,232, runcmp 62,908; the run rows: memcmp 97,522, overlap 121,004,
  words 17,120, bytes 360. Full table:
  docs/design/memfn/probes/rowcon/n2_results_5fc4b0e5.md.
- notice: 2026-10-07 (late) — **MF_MISS_N goes kit-side first (main's
  ruling by message).** R-6 lands after it and consumes the token. Main's
  three conditions: (1) memfn.h states the token's meaning; (2) G2 covers
  the token in the same change, with floors; (3) zero movers, shown by the
  identity gate, or the unit stops and reports. It is in lane `missn`
  (worktrees/missn, branch lane/missn, cut from lane/memfn-rowcon @ 5f0e926e).
  The full G2 run and the identity gate wait for a heavy slot from main.
- notice: 2026-10-07 (late) — **g2x triage (F1/F2/G1). No pcrec defect.**
  - **F2, a kit defect, latent for pcrec.** The arms render memchr/memcmp
    but never call `mf_art_note_libc`. pcrec's stamp is correct because its
    finishing pass (`scan_libc_calls`, src/gen/memfn_stamps.c) inventories
    the whole artifact. On 6 corpus artifacts the stamp matches `nm -u`
    exactly. A non-pcrec host (and G2) gets "none". memfn.h/§R4.3.3 say
    the kit records its own calls, so the kit is wrong. Fix (kit,
    queued after lane missn): each arm notes its own libc calls at render.
    The list is sorted and deduplicated, so pcrec's stamp should not move.
    The identity gate proves it.
  - **F1** is exactly the N3 cell (row_contracts.md §2): G2's ternary s/n/lo
    hooks reach the raw-pasting runcmp/precheck rows, because the gate is
    still WARN-only. pcrec passes only literal identifiers (emit_dfa.c
    :1597/:6287, emit_vm.c :4431/:13269), so it cannot reach this. N3
    enforcement routes these hooks to generic. G2u keeps them as N3's
    acceptance witness.
  - **G1** is G2-side: mutation 7 (floor − 1) is equivalent wherever no
    term reads below the candidate. G2u judges its kill rate over sites
    with a negative offset only.
- notice: 2026-10-07 (late) — **MF_MISS_N ready for R-6; F2 fixed. Both
  merged on lane/memfn-rowcon @ 728bf063.** Validated in main's slot,
  16:16-16:22:
  - The identity gate, `emit_sweep --ref ccf0ca33` judged by
    memfn_r4c_gate.py --zero-dumps, gives **R4C-GATE PASS: 0 movers on every
    stream** (c-default, c-vm, composition, dumps, emit-ir-vm, facts).
  - The full G2 is rc 0, with **61,020,752 checks passed, 0 failed**, 4044
    sites and coverage-missing 0.
  - The MF_MISS_N cell: 538 sites (RETURN 150, ASSIGN 56, FUNC/RETURN 105)
    and 11.76M checks.
  - The W1 witnesses fired.
  - make strict, test-memfn-arms (82/0) and test-memfn-stamps (14/0) pass.

  Main's three conditions are met:
  1. memfn.h states the token's meaning at `miss`: the site's own `n`;
     NULL means unstated.
  2. G2 and the arm pins (two fixtures on the N2 cells) cover it.
  3. Zero movers is shown by the gate above.

  The token is `MF_MISS_N`, an exported sentinel compared by address and
  resolved to `n`'s text by `kit_miss()`; its bytes never reach an
  artifact. R-6 sets `.miss = MF_MISS_N` at the 3 N2 cells. Reports:
  docs/dev/lanes/missn_report.md and libcnote_report.md. The branch is
  deliverable as an interim unit (N1 WARN gate, N2 driver, F2, MF_MISS_N),
  so R-6 can consume the token from main.
- done: 2026-10-07 — **[MEMFN-ROWCON] INTERIM delivery: lane/memfn-rowcon @
  TIP (the commit carrying this entry; code tip 4e6c42c4).** It contains:
  - N1: the row-contract gate in WARN mode, fields.def, uses/serves on all 8
    rows, MF_TRACE;
  - the N2 census driver and results;
  - F2: the arms note their own libc calls;
  - MF_MISS_N, the kit side of R-6.
  All of it is zero-mover. Main 745278be is merged in. Landing bar (main,
  2026-10-07):
  1. **make test**, full `-k -j16 -Otarget` on 3fb4dbb4: 640 s, 59/59
     sections ran. ONE red, test-codegen, which was [SABANCHOR]: S570's
     anchor went stale under N1's gate trace (check-side; no pcrec byte).
     Log: worktrees/memfn-slot/slot3/make_test.log (gitignored).
     **Re-pinned** at 4e6c42c4:
     - the check reports "all anchors resolve" (497 rows, 515 sites);
     - **make test-codegen rc 0** in 155 s, with no `*** [test-` lines
       (worktrees/memfn-slot/slot4/test_codegen.log).
  2. **make strict** rc 0 on the merged tip.
  3. **Mech, solo, one id per call**: the 16 rows rows_for.sh names for the
     kit files touched (D69's src tier). These are S185 S265 S267 S279 S285
     S443 S444 S445 S447 S450 S454 S455 S464 S526 S573: all DETECTED, 0
     unexpected/undetected/unreached/anomalies. **S570**, the only row the
     branch RE-ANCHORS (none added), gave ANOMALY on the stale anchor, then
     after the re-pin **DETECTED** (reach ok 1/1, codegen 19 fail/311
     pass). Its anchor is still the DENY TEST in rc_row_of,
     `if (rows[i].row.deny & art->denies) {`, planted as `0 && (...)`. The
     plant kills the deny test itself; N1's DENIED trace call inside the
     block dies with it. It is not anchored on the trace line.
  4. The **identity gate** vs ccf0ca33 is R4C-GATE PASS, 0 movers on all 6
     streams (at 728bf063; the later commits touch only the merge of main,
     ledger/journal and one sabotage row).
  5. The **full G2** gave 61,020,752 passed, 0 failed, 4044 sites; the
     MF_MISS_N cell is 538 sites with 11.76M checks.
  Reports: docs/dev/lanes/rowconn1_report.md, rowconn2_report.md,
  libcnote_report.md, missn_report.md. Charter vs committed: N1 ✓, N2 ✓
  (R-6 list posted), F2 ✓, MF_MISS_N ✓ (main's 3 conditions). OWED, not in
  this unit:
  - R-6 (main files it; pcrec states MF_MISS_N at the 3 N2 cells);
  - G2u (the blinded update; folds g2x);
  - N3 (enforcement; entry is an N2 re-run after R-6 showing 0
    would-decline + the identity gate);
  - N4.
- notice: 2026-10-07 (evening) — **G2u delivered blinded; K-1 is a contract
  gap, and the kit has ruled on it.** G2u (D27 cell, opus) is merged on
  lane/memfn-g2u.
  - The quick run: 35.53M passed and 462 failed, all of them **K-1**: on
    ALL_PRESENT/FUNC sites the kit takes the function's name from
    `site.pred.fn_ref`, but memfn.h scoped `pred` to FIND/SKIP/VERIFY, so
    the POISON differential (a field the contract says is unused, set to
    junk) moved the name. No answer is wrong.
  - **Kit ruling (contract detail, kit-owned):** a FUNC site's own name is
    ALWAYS `site.pred.fn_ref`, for every op. On ALL_PRESENT/DENSE only that
    member of `pred` is read. memfn.h now states this, with no layout
    change and no byte moved. A FUNC site stating `fn_ref` 0 states no name
    and is REFUSED (R1); that joins N3's enforcement. G2u's
    `fn_ref-unstated` PENDING-ENFORCE class (415 cases) is its acceptance.
  - pcrec's only FUNC site (ofs_site_define, emit_dfa.c:6255) passes
    fn_ref 1, so no pcrec site can be refused.
  - PENDING-ENFORCE for N3 has 4 classes and 1,455 cases: hook-nonident
    (F1, still live: 286 sites in 5 batches don't compile), miss-unstated,
    refusal-unnamed, fn_ref-unstated. `G2_STRICT_HOOKS=1` is N3's
    acceptance switch.
  - F2 is confirmed fixed by the blinded side: MEMFN_LIBC = nm -u on 93
    batches.
  - Next: a blinded follow-up aligns G2's poison table to the K-1 text,
    then the full G2 in a slot.
- done: 2026-10-07 — **[MEMFN-ROWCON] G2u: lane/memfn-g2u @ TIP (the commit
  carrying this entry; code/test tip 238f2368), cut from main 13b9f2ae.**
  It contains the blinded G2 update (D27 cell, authors g2u (opus) and g2u2
  (sonnet), folding g2x) plus K-1's contract text in memfn.h (a FUNC
  site's name is `site.pred.fn_ref` for every op; fn_ref 0 on FUNC is
  refused under N3). No kit code changed and no pcrec byte moved: the diff
  touches memfn/tests, memfn.h comments and docs only. Validation:
  - **Full G2** (main's slot, 17:47-17:55, seed 20261005): rc 0,
    **138,742,037 passed, 0 failed**, 10,307 generator sites, coverage-missing
    0, libc record 95 agree / 0 disagree, mutation 7 over negative-offset
    sites 1,764 / 1,877 killed (floor 1,600), PENDING-ENFORCE 1,469 cases
    (counted outcomes owed to N3; 298 are F1 renders that do not
    compile). Log: worktrees/memfn-slot/slot5/g2.log (gitignored).
  - Quick tier (blinded author, 4 cores): 36,341,888 passed, 0 failed.
  - make strict rc 0. [SABANCHOR] "all anchors resolve". Mech: rows_for.sh
    names only S526, which is DETECTED solo (reach 2/2).
  Report: memfn/tests/G2U_REPORT.md (§7 is the G2u2 addendum).
  Charter (row_contracts.md §5 G2u): explicit values ✓, refusal
  expectations ✓ (491 cases), POISON differential ✓ (9,267 sites, 25
  fields), SEMANTIC differential ✓, per-form floors ✓; plus g2x folded ✓
  and G1 ✓. N3's acceptance = `G2_STRICT_HOOKS=1` over the bucket. OWED:
  N3 (after R-6 and the N2 re-run), then N4.
- done: 2026-10-07 — **[MEMFN-ROWCON] N3: lane/memfn-n3 @ TIP (the commit
  carrying this entry; validated tip b3dcb927 = N3 + G2u3 + main 42771cb8
  with R-6).** The row-contract gate ENFORCES at define and at use:
  - a failing row declines; a site no row serves is refused, naming the
    fields; an unserved use is refused (no re-selection);
  - F1: non-identifier s/n/lo text goes only to generic;
  - miss unstated → decline/refuse;
  - K-1: fn_ref is a hook id, and a FUNC site with 0 is refused;
  - the pre-check is split by handoff into two rows with one form id;
  - ofsskip's K96 ad hoc checks are deleted and replaced by the gate
    (20 --gate arm fixtures);
  - G2 enforces by default (G2u3, blinded).
  No pcrec byte moves and no abi event. memfn.h changed in comments only;
  no docs/spec/ hunk (no caller observes a change after R-6). Validation
  (main's slot, 18:37-19:34, one serial chain;
  logs in worktrees/memfn-slot/slot6/, gitignored):
  1. **N2 census on the ENFORCING build:** `== N2 DONE rc=0
     would_decline=0 ==`; would-decline selections 0; selections with no
     row 0. So zero refusals at both phases on every pcrec site.
  2. **Identity gate vs main 42771cb8:** R4C-GATE PASS, 0 movers on all 6
     streams.
  3. **Full G2** (enforced default): **149,029,184 passed, 0 failed**;
     ENFORCED-CLASS cases 1,103 (hook-nonident 728 render + compile,
     miss-unstated 314 refused naming `miss`, refusal-unnamed 12/12,
     fn_ref-unstated 49 refused naming `fn_ref`); the W1 witnesses fired.
  4. **Full make test** (`-k -j16 -Otarget`): rc 0, 747 s, no `*** [test-`
     lines.
  5. **Mech, solo:** the 16 rows rows_for.sh names, S185 S265 S267 S279
     S285 S443 S444 S445 S447 S450 S454 S455 S464 S526 S570 S573, all
     DETECTED, 0 unexpected/undetected/unreached/anomalies.
  6. make strict rc 0; test-memfn-arms 104/0; test-memfn-stamps 14/0.
  Reports: docs/dev/lanes/n3_report.md; memfn/tests/G2U_REPORT.md §8.
  Charter (row_contracts.md §5 N3): enforce both phases ✓, precheck serves
  a stated miss ✓ (split), shape-dependent row split ✓, K96 ad hoc → gate
  ✓; ENTRY (census 0 after R-6 + identity gate) ✓. OWED: N4 (rows.tsv,
  signatures, census floors, docs/spec/ literals).
- notice: 2026-10-07 — **R4g edit set vs [START-TABLE] C4-C7 (read from main
  bc8277d4). CLEARED by main** to start after N3 delivers and land after
  C4 merges.
  - **The edit set: SEARCH TEXT only, in src/gen/emit_dfa.c:**
    - pcrec_emit_find (:5911-5925);
    - pf_emit_find (:5928-5937);
    - the memchr find line of pf_emit_memchr and its _bounded twin
      (:5945-5986);
    - the while-table line of pf_emit_bcls and its _bounded twin
      (:5992-6016);
    - the FIND call in pf_vm_emit_first_class (:6713-6731).
    pf_emit_first_*_bounded (:6605-6632) follow through pf_emit_find with
    no edit. Also memfn_sites.def, the manifest PF row and C12 3→1.
  - **Stays pcrec-side:** guards, `return 0`s, clamps, comments, the
    pf_*_applies predicates, cand_select(NEXT)/dfa_pf_of, unanch_start,
    pf_scan_set_of, dfa_cand_scan, cand_ppm, the reseed text, and the
    start_bytes/can_begin_match tables. The K84 strcmp readers are already
    fixed on main.
  - **Overlap:**
    - C4: no shared function (same file and same cand_rows[]
      initializer, different rows);
    - C5/C5b: disjoint (the CandRow union is a soft touchpoint, unused);
    - C6/C7: disjoint.
  - **Main's conditions:**
    1. no CandPf/CandRow field change (if one is needed, stop and ask);
    2. re-pin and solo-run every row anchored in R4g's functions (S68
       S186 S478 S481-S485 S524) in R4g's own commit, and re-derive
       docs/design/start_table/sabotage_anchors.tsv so S478/S481-S484's
       after-C5b rerun_at entries point at R4g's anchors;
    3. this entry.
  - Landing: on post-C4 main, with the zero-mover sweep on that tree, and
    merges serialized through main.
- notice: 2026-10-07 (night) — **R4g BUILT, merged on lane/memfn-r4g (not
  yet delivered; it lands on post-C4 main).**
  - **Kit:** a new arm `pffind` (memfn/src/pffind.c, 0BSD) has four rows,
    each with uses/serves, all on the one shape FIND/STMT/ASSIGN over one
    SET term at offset 0.
  - **pcrec side:** `pcrec_emit_find` only DESCRIBES the site (DELEG_SITES
    row PF). The form, holdback, set, guards and table stay the caller's
    decisions (report §3, P1-P7).
  - **Main's conditions:**
    1. CandPf/CandRow/cand_rows[] untouched;
    2. S68, S478 and S524 re-pinned (same defects, named lines); S186 and
       S481-S485 unchanged; all 9 DETECTED solo; sabotage_anchors.tsv and
       call_graph.txt re-derived (S478/S481-S484 keep rerun_at after-C5b
       at R4g's lines; S68's owner moved to memfn/);
    3. the edit set posted earlier.
  - **One deliberate widening of the posted edit set:** for the memchr
    forms, the NULL test and the position store moved with the `memchr`
    line, because a pointer is not a FIND result. pcrec still states
    `return 0;` (as `on_miss`) and the `subject_length - 1` clamp (as
    `miss`), and the kit writes them from those hooks.
  - **Identity:** 41 compiles across every PF shape and hat, byte-identical
    to a pre-edit binary; the I1 shadow is clean. C12: emit_dfa.c memchr
    2→1.
  - **Checks on the merged tip:** strict 0, arms 126/0, stamps 14/0.
  - **PROPOSAL, for main to sequence:** §19 row 6's RARITY half is NOT
    moved in R4g. That half would make the pre-check's necessary byte an
    OPTIONAL second term of the PF site, with the kit deciding whether
    testing it pays. That changes the PF site's shape and moves G1's
    elision (`req_byte_dominated_by`, read in `req_admits[]`, which C4 is
    deleting) into the kit. It is an admission decision, which your
    clearance keeps pcrec's. Proposal: its own step after C4/C5b,
    byte-identical through a baseline row that tests exactly as pcrec does
    today. integration.md §22 records the deferral.
  - **G2:** no G2 family reaches the new rows yet (C5 fixtures + pcrec
    compiles only). A blinded follow-up (g2pf) is adding the PF family
    before R4g is delivered.
- notice: 2026-10-07 (night) — **Main's rulings on R4g, recorded.**
  1. The memchr widening (the NULL test and position store move with the
     line; `return 0` and the `len - 1` clamp stay pcrec's, as hooks) is
     ACCEPTED. R4g's done: records it as an edit-set amendment.
  2. §19 row 6's RARITY half is DEFERRED to its own step after C5b,
     re-checked against refactor B [DEC-FALLBACK]'s scope before it starts
     (B absorbs prefilter admission). **CONSTRAINT:** the admission
     decision (`req_byte_dominated_by`) stays pcrec's and lives in
     cand_rows[] after C4. The kit may only ever receive the resulting
     text, never the decision. **Note:** this narrows integration.md §19
     row 6 ("the kit decides whether testing it pays"). The kit will
     revise that row's text, and any later kit form that wants the choice
     brings it to main as a request.
- done: 2026-10-07 — **R4g (M2: PF migrates, zero movers): lane/memfn-r4g @
  TIP (the commit carrying this entry; validated tip cbb7e953, which
  contains post-C4 main 8cada7b9).**
  - **What it delivers:**
    - The kit arm `pffind` (memfn/src/pffind.c, 0BSD; four rows with
      uses/serves). `pcrec_emit_find` only describes the site (DELEG_SITES
      row PF), and the manifest's PF row is `delegated`. C12: emit_dfa.c
      memchr 2→1.
    - The r4gfix kit fixes:
      - the PF rows serve ANY for preds/ret_pred;
      - mf_emit's selection gates the use-phase fields.
    - The contract amendment: result is UNSPECIFIED on a miss when
      on_miss_leaves = 1, and on_miss must not read it.
    - The blinded G2 PF family (G2pf, G2pf2).
    - integration.md §19 row 6 is revised per your ruling.
  - **EDIT-SET AMENDMENT (ruled OK):** for the memchr forms, the NULL test
    and position store moved with the memchr line. pcrec states
    `return 0;` (as on_miss) and the `len - 1` clamp (as miss) as hooks.
  - **Conditions:**
    1. CandPf/CandRow/cand_rows[] are untouched.
    2. S68, S478 and S524 are re-pinned, each planting the same defect;
       S186 and S481-S485 are unchanged. All are DETECTED solo.
       sabotage_anchors.tsv/.total and call_graph.txt were re-derived on
       the post-C4 merge; S478/S481-S484 keep rerun_at after-C5b; the one
       unresolved site (S571) is identical on main.
    3. The edit set was posted.
  - **Validation** (your slot, 21:16-22:18, one serial chain; logs
    worktrees/memfn-slot/slot7/, gitignored):
    1. N2 census on the enforcing build: would-decline 0, no-row 0.
    2. Identity gate vs 8cada7b9: R4C-GATE PASS, 0 movers on all 6
       streams.
    3. Full G2: **173,824,444 passed, 0 failed**. ENFORCED-CLASS is 1,563;
       pf_memchr 422 and pf_walk 449 hard sites; the W1 witnesses fired.
    4. make test: rc 0, 685 s, no `*** [test-` lines.
    5. Mech, selection rule (b) as ruled: the rows whose anchor's owning
       definition (sabotage_anchors.tsv owner via call_graph.txt)
       intersects a line R4g changed in src/, plus every row on a
       memfn/ or tests/memfn/ file, plus the re-pinned rows, plus
       condition (2)'s list. The changed definitions are PcrecFind,
       PcrecFindTable, find_site, find_table_name, find_table_tag,
       pcrec_emit_find, pf_emit_bcls[_bounded], pf_emit_find,
       pf_emit_first_{class,memchr}_bounded, pf_emit_memchr[_bounded] and
       pf_vm_emit_first_class. The **29 rows**, all DETECTED (0
       unexpected/undetected/unreached/anomalies), are: S68 S185 S186 S265
       S267 S279 S285 S443 S444 S445 S447 S450 S454 S455 S464 S478 S481
       S482 S483 S484 S485 S512 S522 S523 S524 S525 S526 S570 S573.
    6. strict 0; arms 138/0; stamps 14/0; anchors all resolve.
  - Reports: docs/dev/lanes/r4g_report.md, r4gfix_report.md;
    memfn/tests/G2U_REPORT.md §9-§10.
  - **OWED:**
    - §19 row 6's rarity half (after C5b, decision pcrec's, text only);
    - PF movers (U-2 + a Linux cell in pf_emit_bcls);
    - N4;
    - the kit follow-up: n2_census.py gets one pool across all arms (no
      per-arm barrier); scripts/emit_sweep.py shows the same per-arm
      pool shape and is yours to judge.
- done: 2026-10-07 — **n2_census one-pool fix: lane/memfn-n2pool @ TIP (the
  commit carrying this entry; from main d33e1d55).** It touches
  docs/design/memfn/probes/rowcon/ only, plus the lanes index:
  - one pool across all arms with no per-arm barrier;
  - per-arm reorder buffers, so the arm jsons and meta.json are
    byte-identical to the old script's (proven on a fixed 31-pattern,
    8-arm selection, with 3 stragglers);
  - kill-resume proven: SKIP of the finished arms, identical report.
  On the small run the wall time went from 18.6 s to 12.3 s (an
  observation only). No C, no pcrec byte, nothing make runs. Report:
  docs/dev/lanes/n2pool_report.md. Also adds the missing lanes index
  entry for r4gfix_report.md.
- done: 2026-10-08 — **[MEMFN-ROWCON] N4: lane/memfn-n4 @ TIP (the commit
  carrying this entry; main ad669fb8 merged in).** Report:
  docs/dev/lanes/n4_report.md (§11 is the slot's validation).
  - What it adds:
    - `tests/memfn/rows.tsv` (13 kit rows, closed reach reasons, witness,
      signature, control);
    - `row_floors.tsv`;
    - `make test-memfn-rows` (in TEST_SECTIONS);
    - the trace's `REACH_DROPPED`;
    - `n2_report.py --floors/--propose`.
    No pcrec byte moves and there is no spec hunk.
  - **Census wall time: 379 s** at JOBS=16 with the one-pool driver.
    Result: rc 0, would_decline=0, floor_fail=0, reason_stale=0,
    reach_dropped=0.
  - The 12 `pcrec_floor` values are pinned from `--propose` (4e081f78), and
    the re-check reads floor_placeholder=0.
  - make test on 4e081f78 took 680 s, with one red in test-codegen [K37]:
    N4's new `run_rows.sh` existence loop. Fixed in e8e3e1d8, after which
    test-codegen is green and test-memfn-rows is 70/0.
  - **OWED:** `g2_floor` (PLACEHOLDER) needs G2 to count per row, via a
    blinded follow-up (n4_report §7).
- notice: 2026-10-08 — **R4h (M3) edit set vs [START-TABLE] C5-C7 (read from
  main d1a4105e and lane/stc5land 56a806c7). NOT YET BUILDABLE AS ZERO-MOVER:
  two rulings are needed first (Q-R4h-1, Q-R4h-2 below).**
  - **The edit set (search text only):**
    - STAY: the `while` printf in `dir_fwd_skip` (emit_dfa.c:7348-7350) and
      in `dir_rev_skip` (:7375-7377).
    - EDGE: in `emit_scan_edge`, the unbounded loop (:8862-8864) and the
      counted loop with its `scan_run_length++` (:8874-8878).
    - VMSPAN: `vm_emit_span_scan` (emit_vm.c:4680-4684), at stride 1 only.
      The function splits into a VMSPAN site builder plus the strided loop,
      which stays as VMSTRIDE (M6).
    - Three DELEG_SITES rows (SKIP/ADVANCE/SET, MF_P_INLOOP).
  - **Stays pcrec-side:**
    - the entry/guard lines, the peeled guard and the peeled `advance;`;
    - accept stores, `stay<K>`/`scan<N>` tables, the counted fall-through
      block, `dfa_edge_of`/`dfa_edges[]`, axis F;
    - `lim_`/PRUNE_CLAMP, the cursor init, `vm_cursor_rep`;
    - comments.
    - `scan_test` stays T4 and renders the `member` hook.
  - **Overlap:**
    - C5: same files, disjoint functions (every C5 hunk is in the
      cand/reseed/stamp/listing regions; DFA_SELECT and `dfa_edge_of`
      survive).
    - C5b, C6, C7: disjoint.
    - Under D153 it may be built now. It lands after C5, with its sweep on
      post-C5 main, serialized with C5b.
  - **Contract gaps** (the emitted text does not fit memfn.h byte for byte):
    - G1: the counter is declared by pcrec, with pcrec text (the peeled
      step, `lim_`, the cursor init) between the declaration and the
      `while`. EDGE also reads `scan_run_length` after the loop. §14.3 has
      the kit declare it, while §15 rev 4.1 keeps it pcrec's.
    - G2: layouts that no site fact decides. The counted condition is
      wrapped (EDGE) or on one line (VMSPAN). The body is `) step;` or
      `) { step; }`.
    - G3: `more`/`peek`/`step` are OTHER-class only (fields.def), so a
      byte-identical row cannot claim them (K96). This needs new kit
      classes (a conjunct-safe `more`, a postfix `peek`), which is kit
      ROWCON work.
    - G4: Q-G2-5 (ADVANCE's empty range) has customers now: the reverse
      STAY and the reverse EDGE.
    - G5: the reverse SKIP offset comment in memfn.h:46-48 needs
      reconciling with Q-G2-9.
  - **Q-R4h-1 (main/Frank).** The kit recommends:
    - (a) for G1, a SEMANTIC hook: "the caller declares and owns the
      counter", an MF_SITE_ABI 5 bump. The counter is shared state,
      because EDGE reads it after the loop, so it is a real site fact and
      not layout.
    - (b) for G2, ONE pcrec-side normalization pre-commit: a declared mover
      with pcrec's abi bump and the D76/D94 re-pins, landing AFTER C7. It
      gives every in-loop site one condition layout and one body layout,
      so no layout variant enters the contract.

    The alternative is layout hints in the contract, which ties pcrec's
    formatting to the kit ABI permanently. The kit recommends against it.
  - **Q-R4h-2 (kit's own, recorded for main).** Q-G2-5 is ruled as
    recommended: ADVANCE's range is `more`, `empty` is NOP, and the kit
    adds no empty test.
  - **Sabotage:**
    - re-pin and solo-run S214 (owner moves to the kit) and S72
      (re-anchored to the accept-store guard at :7378);
    - solo-run S433, S61 and S39;
    - re-derive sabotage_anchors.tsv and call_graph.txt;
    - add kit-side rows for the three unplanted bounds: the STAY view
      `+ 1 <`, the unbounded EDGE loop and VMSPAN's `it_` cap.
  - **C12/C17:**
    - C12: emit_dfa.c walk-stmt 2→0 and walk-open 2→0 (both rows deleted);
      rows 8→6, forms 12→8, C12_CEIL_ROWS_FLOOR 8→6.
    - C17: STAY, EDGE and VMSPAN become delegated (6→9); VMSTRIDE stays
      pending.
  - **§19 (proposed new row):** `SCAN_TEST_CALLS 2` (emit_dfa.c:8680) and
    `vm_cls_reads` price T4 by how many times the loop writes its test.
    After R4h, that count belongs to the kit's form. It holds at zero
    movers and must be restated before any in-loop mover.
  - **Gate reach:** VMSPAN is reached only under `--engine=vm`. The
    identity sweep needs that stream, plus witness cells: `a[^x]*`,
    `a[^x]*x$`, `[a-z]*`, `a[0-9]{3,20}x`, and `(a)[a-z]{2,9}x` /
    `a[a-z]*x` under `--engine=vm`.
  - **Order the kit proposes:**
    1. ROWCON G3 classes (kit-only, zero movers);
    2. the Q-R4h-1 rulings;
    3. the normalization pre-commit after C7, if ruled;
    4. R4h.
- ruling recorded: 2026-10-08 — **Q-R4h-1 RULED (a)+(b)** (manager,
  2026-10-08, session 97).
  - **(a)** MF_SITE_ABI 5 semantic hook: the CALLER owns the counter. pcrec
    declares it and reads it after the loop; the kit's text only advances it.
  - **(b)** ONE pcrec-side layout-normalization pre-commit, scheduled AFTER
    C7. It is a declared mover with its own abi bump and re-pins in the same
    change. Main checks it against refactor B's ([DEC-FALLBACK]) scope
    before briefing it.
  - No layout hints go in the contract. R4h lands zero-mover on top of (b).
  - Kit-only work cleared now: the G3 hook classes in fields.def, and
    recording Q-G2-5 as ruled (ADVANCE's empty range is NOP; the range is
    `more`).
  - The §19 row (the T4 pricing count becomes the kit's) is FILED, not
    scheduled.
  - Nothing is built pcrec-side until C7 merges.
- done: 2026-10-08 — **[MEMFN-ROWCON] N4 follow-up, the G2 per-row floor:
  lane/memfn-g2floor @ TIP (the commit carrying this entry; it is N4's tip plus
  this unit plus the R4h notice/ruling entries).**
  - **G2rows (blinded, cell; branch g2u 635c1f11):** `run_g2.sh --rows`, ON by
    default under `--quick`, sums the trace's REACH `chosen=` over all 8 kit
    processes into `row-chosen` lines, with four checks:
    - REACH_DROPPED 0;
    - every row >= 1;
    - a literal floor of 13 rows;
    - every process traced.

    Controls for (b) and (d) run on every invocation. Report:
    memfn/tests/G2ROWS_REPORT.md.
  - **At the merge (manager):**
    - `build/libpcrec_mftrace.a`, built by make (`tests/memfn/mk_mftrace_lib.sh`;
      answers Q-G2R-1);
    - G2 check (e): every row meets its `g2_floor` from row_floors.tsv,
      tested in the failing direction;
    - the 13 g2_floor values pinned at floor(0.9 x).

    row_floors.tsv has no PLACEHOLDER left.
  - **Validation:**
    - `make test-memfn-g2` (taskset 12-15) passes: 45,229,686 checks, 0
      failed, in 147 s;
    - `test-memfn-rows` 70/0;
    - no C changed, no pcrec byte moved.
  - **Note:** test-memfn-g2 is a make test section. Its rows half adds about
    nothing measurable (the G2 author measured inside ~25 s noise), but it
    now depends on the traced library rule.
  - **Q-G2R-2** (the literal FLOOR_ROWS stays at 13 when a row is added):
    intended. rows.tsv's ROWS_FLOOR is the same kind of literal, and the
    change that adds a row raises both.
- done: 2026-10-08 — **R4h PREP (kit-only, Q-R4h-1 (a)): lane/memfn-r4hprep @
  TIP (the commit carrying this entry; main a3c2f4ef merged in).** Report:
  docs/dev/lanes/r4hprep_report.md.
  - **What it adds:**
    - MF_SITE_ABI 5, `mf_site.count_by_caller` (appended last). The caller
      owns an ADVANCE counter, and the kit only advances and caps it. pcrec's
      builders zero-allocate, so 0 is stated.
    - The ADVANCE hook shape classes CONJ, POSTFIX and EXPR_STMT, with
      lexical checks in gate.c; no row serves them yet.
    - Q-G2-5 recorded as ruled, with MF_MAX_BACK's comment reconciled with
      Q-G2-9.
    - Fixtures and gate cases: arms 171, rows 117 (check E classifies hook
      texts), gate cases 39.
  - **Validation (slot9):**
    - census would_decline=0, all floors met;
    - identity gate 0 movers on six streams;
    - G2 full 173,824,444/0;
    - make test rc 0 in 718 s;
    - 17 solo mech rows, all clean.
  - **Files outside memfn/:**
    - tests/memfn (fixtures, pins/arms.tsv +4 rows, rows_check, run_arm_pins,
      run_rows, CLAUDE.md);
    - docs/design/memfn (integration.md §14.3/§14.4, row_contracts.md §2);
    - the lanes index.

    No src/ change and no pcrec byte moved, so there is no abi event.
  - **Findings for R4h:**
    - EDGE's `member` hook text (`scan_test`) is pasted as a bare `&&`
      operand and exists only at render, so R4h needs a render-time class or
      a pcrec shape promise;
    - the conditional `count` use is caught only by rows check E.
- done: 2026-10-08 — **R4h's ADVANCE target, FROZEN (main's request before
  the layout-normalization mover): lane/memfn-next @ TIP (the commit carrying
  this entry; it merges lane/advtarget 72db7d6c).** Report:
  docs/dev/lanes/advtarget_report.md.
  - **The target is the kit's render; pcrec normalizes to it.** Kit
    decisions, all kept:
    - `more` and `member` are always parenthesized, and `member` is opaque
      (so EDGE's render-only `scan_test` shape no longer matters);
    - the body is always braced, with the counter step on its own line;
    - the cap is `%llu` + `ULL`;
    - the counted shapes use count_by_caller = 1.
  - **Eight shapes**, each pinned in arms.tsv and committed byte for byte in
    `tests/memfn/pins/r4h_target/<shape>.c` with a trailing
    `/* pcrec today: */` block: stay-fwd, stay-rev, stay-view,
    edge-unbounded, edge-counted-fwd, edge-counted-rev, vmspan-it, vmspan.
  - **The deltas** classify into (a)/(b)/(c)/(d) only; nothing falls outside
    them.
  - **run_arm_pins.sh check 8** re-renders each shape and compares it with
    its file, with a planted-byte control.
  - **Validation:** arms 221/0 and rows 117/0. Nine witness compiles were
    byte-identical, and no src/ file changed (zero movers).
  - **For pcrec's mover and R4h:** the member hook must pass pcrec's own
    test text (today's `scan_test`/`vm_cls_test` output), never a text
    rebuilt from the kit's `peek` expression.
- done: 2026-10-08 — **[MEMFN] R4h (M3): STAY, the scan edge's loop and
  VMSPAN at stride 1 migrate. lane/memfn-r4h @ TIP (the commit carrying this
  entry; main 02db3811 merged in).** Report: docs/dev/lanes/r4h_report.md.
  - **Zero movers, no abi event, no kit source change.** The kit's generic
    ADVANCE row reproduces the normalized text (c4c37af8).
  - **Site builders:** `stay_advance`, `edge_advance` and `vm_span_advance`,
    beside their decisions. They pass pcrec's own hook texts and set
    count_by_caller for `scan_run_length`/`it_`.
  - **`vm_emit_span_scan` is split:** stride 1 goes to the kit, and
    `vm_stride_loop` stays pcrec's (VMSTRIDE).
  - **Manifest and form checks:** C17 has 9 delegated and 4 pending. C12 has
    6 rows and 8 forms, with floor 6.
  - **Evidence:**
    - I1 shadow comparator: 78,298 sites, 0 mismatches.
    - slot10:
      - identity gate 0 movers on six streams;
      - G2 full 173.8M/0;
      - make test rc 0 in 655 s;
      - 18 solo mech rows clean.
    - The census re-run, after the generic row became a `pcrec` row, gave
      rc 0 and reason_stale=0.
  - **Sabotage:** S72 and S214 re-anchored, S512 re-aimed, S614-S616 new.
    S617 is returned.
- ack: 2026-10-08 — **R-7 (M4, MLINE).** Taken now. Step 1 is a read-only
  scoping lane (r4mlscope, opus). Its edit set and its overlap check
  against [DEC-FALLBACK] and the ATTEMPT-route start rows will be posted here
  as a notice. No build until main has read it.
- notice: 2026-10-08 — **R-7 (M4, MLINE): edit set and overlap (read from
  main dafcc639). NOT buildable as zero-mover on today's contract: three
  kit-contract gaps, all closable kit-side with no pcrec byte moved.**
  - **The edit set:**
    - **Moves to the kit:** the three statements inside `emit_attempt`'s
      MLINE block (emit_dfa.c:10386-10390: the `memchr`, `if (!q) break;`,
      and the `start = ... + 1;` store).
    - **Stays pcrec's:**
      - the guard line `if (start > X && subject[start - 1] != 10) {` and
        its `}`;
      - `if (cpre)`, the D63 comment, the K50/K73 guards, the `for` header,
        `start_max`;
      - every start decision: NEXT via `attempt_next_of`, then `pred-memchr`
        and `attempt_cand` (BOUND); `cpre`; `cand.byte`/`cand.offset`; and
        `gseed`, which picks X = `search_from` or 0.
    - **Pcrec side:** generalize the one describer `pcrec_emit_find`/
      `PcrecFind` (a site id, a term offset, a floor) instead of adding a
      parallel builder. Add DELEG_SITES row MLINE (FIND/ASSIGN/SET/SCAN).
  - **Reach:**
    - Reached: `(?m)^abc`, `(?m)^\d+`, `(?m)^`, `(?m)^$`, `^a|(?m)^b` (default
      and `-e utf8`), `(?m)^a|\Gb` (X = search_from), and VM hybrids through
      the inlined prefilter (`(?m)^(a|b)$`).
    - Not reached: anything under `--engine=vm`.
  - **Contract gaps** (`pf_memchr` renders the first two statements byte for
    byte; three gaps remain):
    - **G1, the `+ 1` store:** a negative-offset FIND (the term `{'\n'}` at
      offset -1, as memfn.h/§15.7 already reserve) cannot name the candidate
      `n`. FIND's range `[lo, n - end_back)` excludes it, yet this site
      produces it (`(?m)^$` on "a\n" at 2).
    - **G2, the empty range:** `start == n` is reachable (`memchr(s+n, 10,
      0)`). pcrec's text is safe because `start > X >= 0` proves `s` non-NULL
      and BOUND `all` proves `start <= n`. `pf_memchr` serves EXCLUDED only.
    - **G3, `on_miss` `break;`:** it classes OTHER (JUMP is `return`/`goto`),
      so the site falls back to the generic row and bytes would move.
  - **Kit rulings** (the kit's own contract; proposed for main's ack):
    - **Q-R7-1:** for a negative-offset term the FIND range is bounded by its
      READS (MF_SITE_ABI 6). No `result_bias` field, because term offsets
      already say it. No pcrec normalization, because it would move bytes. It
      also serves [ENG-TACTICS]' "resume at hit+1".
    - **Q-R7-2:** a kit-only proven-fact class, "empty only as lo == n over a
      non-NULL subject". The alternative (a pcrec `start < subject_length`
      guard) is an abi event plus a compare per attempt, so it is rejected.
    - **Q-R7-3:** a kit-only LOOP-EXIT `on_miss` class. A row may paste it
      only where its own text opens no loop around it, so the generic row may
      not serve it.
    - **Also:** §15.7's floor sketch is corrected. X is a start decision and
      stays in pcrec's guard; the kit's floor is `start`.
  - **Overlap:**
    - [DEC-FALLBACK] (main and decfbrev2 c301580f) is DISJOINT: no
      emit_dfa.c line, and `pcrec_engine_sel_name` is unchanged.
    - ATTEMPT route: `cand_rows[]` `pred-memchr`/BOUND, `attempt_next_read`
      and `attempt_cand` are the same file but NOT edited. `emit_attempt` is
      the same function, and M4 is its only edit.
    - [DEC-POSDOM] and [START-D1] are unscheduled neighbours.
    - So under D153, M4 may build now, serialized with B's landing, with the
      sweep on that main.
  - **Plan:**
    1. **M4 prep** (kit-only, zero pcrec bytes): G1 at MF_SITE_ABI 6 (G2's
       negative-offset oracle re-derived; generic.c's bound moves only for
       negative-offset sites, and none is delegated today), plus the G2 and
       G3 classes, fixtures, and a G2 family at offset -1 that reaches n.
    2. **M4 itself:**
       - the describer is generalized;
       - MLINE becomes delegated (10/3);
       - C12 memchr row deleted (rows 6→5, forms 8→7, floor 6→5);
       - a new kit row → ROWS_FLOOR and FLOOR_ROWS 13→14;
       - `MEMFN_LIBC` is unchanged.
  - **Sabotage:**
    - re-pin and solo-run S82 (the gseed argument line);
    - re-aim S511 to a still-pending row, since "MLINE pending" dies;
    - re-pin S524 (the DELEG_PF call and its ceiling text);
    - solo-run S235 and S81, plus R4g's rule (b) rows;
    - **3 new ids needed:**
      - the `+ k` store dropped;
      - the range stopping one short of `n`;
      - a row serving a loop-exit `on_miss` inside its own loop.
  - **Gate reach:** the default stream and `-e utf8`. Witness cells:
    - `(?m)^$` on "a\n";
    - find-all `(?m)^`;
    - `(?m)^a|\Gb`;
    - `(?m)^(a|b)$`;
    - `^a|(?m)^b`.
- ruling recorded: 2026-10-08 — **R-7 plan ACKED by main.** M4 prep
  (kit-only), then M4, with pcrec_emit_find generalized. Q-R7-1/2/3 are
  kit-side contract classes. MF_SITE_ABI 6 is fine (needed by M4 itself).
  Sabotage ids S617, S618, S619. S511 is re-aimed. Note: Q-R7-1's
  read-bounded range is also what [ENG-TACTICS]' "resume at hit+1" would
  need. Not designed for it.
- done: 2026-10-08 — **R-7 (M4, MLINE) DELIVERED: lane/memfn-m4 @ TIP (the
  commit carrying this entry), ZERO MOVERS, no abi event.** Report
  `docs/dev/lanes/m4_report.md` (§10 = the landing). Validation slot11
  (`worktrees/memfn-slot/slot11/verdict.txt`), tree 32197d74 = kit + main
  e99ad486:
  - census rc 0, would_decline 0, reason_stale 0, floor_fail 0;
  - identity gate R4C-GATE PASS --zero-dumps, 0 movers on every stream;
  - G2 full 182,763,715 / 0; W1 defects 1-4 all red;
  - make test via scripts/perfrun (-j16 PROCS=16): rc 0, 670 s, no
    `*** [test-` lines;
  - mech 36/38 clean at first run. S513 and S525 read UNDETECTED: they are
    equivalent mutants after M4, which removed pcrec's last memchr (the
    recogniser's memchr entry and C12's memchr ceiling have nothing left
    to catch). Triage reports are `slot11/S513_triage.md` and
    `S525_triage.md`. Both are re-pinned `SAB_EXPECT=UNDETECTED` as
    tripwires (S524 still catches a new pcrec memchr), and re-run solo:
    unexpected 0.
  - Floors: `pf_memchr_back` g2_floor 4109, pcrec_floor 3271;
    test-memfn-rows and test-memfn-g2 green.
  - G2 at MF_SITE_ABI 6 by the blinded lane g2m4
    (`memfn/tests/G2M4_REPORT.md`): quick 47,436,029 / 0.
  - **For main:** the [MEMFN] M4 plan state and your dev_journal line.
    `docs/dev/artifact_size_log.tsv` was regenerated by the run and NOT
    committed (yours to regenerate). The leftover worktree `m4` can be
    pruned after the merge.
- notice: 2026-10-08 — **G2's open readings Q-G2M4-1..9 (blinded lane g2m4;
  detail in memfn/tests/G2M4_REPORT.md).** None blocks M4: each reading is
  the conservative one and is green. The kit will settle them in its
  contract text (integration.md §14) at the next contract revision. Points
  worth main's eye:
  - Q-G2M4-2: ON_CAND keeps the old range per the brief, but memfn.h states
    Q-R7-1 at MF_OP_FIND with no ON_CAND exception.
  - Q-G2M4-4: `miss = MF_MISS_N` on a reads-below site, where n is itself a
    candidate. Untested. pcrec states no miss on MLINE, so it is
    unreachable today.
  - Q-G2M4-6: G2 recognises the generic row by its form_id string.
  - Manager review note: G2's oracle applies Q-R7-1 only to
    single-predicate FINDs.
  - Finding about pcrec (for known_issues, if you agree): the "memchr" entry
    in `src/gen/memfn_stamps.c`'s `libc_names[]` is now redundant (pcrec
    spells no memchr). Deleting it moves no byte. S513 is the tripwire that
    says so.
- notice: 2026-10-08 — **Proposed text for R-8 (M7, N7), for main to file.
  The kit does not write requests.md.** Main and the kit were each
  waiting for the other to write it. Suggested request:
  - **R-8 — M7: N7, the encoding seam's span compare
    (`src/enc/enc_byte.c` `$_span_match[_caseless]`), migrates, zero
    movers.**
  - **Trigger:** completeness (integration.md §22 M7; its prerequisite M1b
    has landed; Q54 RULED YES, D147 addendum 10).
  - **Step 1 is a READ-ONLY scoping lane, as R-7 had:**
    - the edit set;
    - the boundary (what stays the encoding's under D58/DD-12);
    - the overlap check against refactor B ([DEC-FALLBACK] B3+) and any
      in-flight `src/enc/` work, under D153;
    - the vocabulary gap. The `MF_VOCAB` bump is a run-time-operand
      `mismatch` returning a prefix count, caseless variant included.
  - **Scope also carries:**
    - C17's static scan gains `src/enc/`;
    - manifest N7 goes pending → delegated;
    - main's ruled rider: delete the redundant `"memchr"` entry in
      `src/gen/memfn_stamps.c` `libc_names[]` (no byte moves; S513's
      tripwire is re-pinned or retired in the same change).
  - **Sabotage ids:** about 3, named by the scoping lane.
  - **Validation:** the slot chain as for R-7 (census, identity gate, G2
    full, make test via perfrun, mech by rule (b)).
  - **Blinded G2:** the new `mismatch` operation gets its oracle from a
    D27 lane (cell g2u-cell).
  - **Ordering:** M6 (N6 + the strided VM span; prerequisite R4h, landed)
    could go first instead. The kit has no preference beyond main's: M7
    first per main's message.

## R-8 — M7, N7 (the encoding seam's span compare) migrates, zero movers

- ack: 2026-10-08 — **R-8 (M7, N7).** Taken now on branch `lane/memfn-m7`,
  cut from main bec97b31. Step 1 is a READ-ONLY scoping lane (m7scope,
  opus). It will post a notice here: the edit set; the D58 boundary
  (which bytes move to the kit and which stay backend text, per
  encoding); the D153 overlap check against refactor B3+ and any
  in-flight src/enc/ work; and the MF_VOCAB gap for `mismatch`. No build
  until main has read that notice. Ids S666-S675 are noted.
- notice: 2026-10-08 — **R-8 step 1 DONE: N7 scoping. Report
  `docs/dev/lanes/m7scope_report.md` (lane m7scope, opus, read-only;
  commit b5ed028f). No build until main has read this. Two items need
  main: Q-R8-1 and Q-R8-3.**
  - **Edit set:**
    - pcrec side: about 8 files: enc_byte.c, enc_utf8.c, enc.c, enc.h,
      src/enc/CLAUDE.md, emit_dfa.c `emit_residual_defs` (lines
      3245-3258 only), memfn_sites.{c,h,def}, and the rider
      memfn_stamps.c:47;
    - checks/pins: manifest, C12 ceilings, C10's D91 list, rows.tsv,
      fixtures;
    - kit side: memfn.h, compose/fields/gate, a row, K1 references;
    - nothing in emit_vm.c, compile.c or select_engine.c. No abi event,
      no spec hunk.
    - The byte-wise compare is 3 shapes over 4 text constants (exact,
      ASCII in-place fold, UCP fold expression). utf8 exact is the byte
      text verbatim.
  - **Boundary (D58/DD-12):** the kit renders the compare LOOP only, a
    statement site inside the backend's exported function. The backend
    keeps:
    - signature, braces and the final `return (ptrdiff_t)reflen;`;
    - the fold spelling (hook text) and the failure statement (hook
      text);
    - the UCP fold function and table, and every comment/declaration.
    Rendering the whole function is rejected (linkage, entry contract,
    DD-12 (7)).
  - **Vocabulary:** one kit-only PREP commit (zero pcrec bytes, M4 Phase A
    shape):
    - `MF_VOCAB` 3: `MF_OP_MISMATCH`, `MF_T_REF` (a run-time operand
      span), `MF_H_ON_DIFF` (the prefix count is written, then `on_miss`
      may read it);
    - `MF_SITE_ABI` 7: hooks `ref`/`reflen`/`fold`, appended last.
  - **Overlap (D153): DISJOINT.**
    - B3 is compile.c plus a comment; B4/B5 are select_engine.c,
      emit_vm.c and compile.c.
    - emit_dfa.c is shared, but the edits are in different functions.
    - No unmerged src/enc/ work anywhere.
    - The gate ref is M7's merge-base; if B merges first, I merge main
      and re-take the ref (Q-R8-8).
  - **C17/C12 already scan src/enc/** (since R4a). M7 flips N7 and
    deletes its ceiling rows.
  - **Rider confirmed dead.** S513's anchor line goes away: re-aim it at
    `strlen` if a hand plant shows C11's quick arm reaches it, else
    retire it. S517 shares the line, so it is re-anchored and re-measured
    in the same commit.
  - **Sabotage:** moved anchors are S116, S394 (only if the entry struct
    grows), S513 and S517. New rows come from S666-S675 (grepped free).
  - **Gate reach:** both encodings, plus `-fcomments` and `--ucp`, with a
    per-base count of artifacts that contain the compare; witnesses in
    report §7.
  - **For MAIN:**
    - **Q-R8-1, scope.** utf8's caseless body (`u8_defs_bref_ci`) is NOT
      a byte mismatch. It decodes and folds per character with two
      cursors and length-changing consumption. **Kit recommends: split
      it into a new `pending` manifest row N7U**, with its own later
      vocabulary step (decode hook, length-changing result). M7 then
      covers every byte-wise compare, exact and caseless (ASCII and
      UCP). Please confirm that is how you read "caseless variant
      included", and add the N7U manifest row (the manifest is yours).
    - **Q-R8-3, the seam (a D58 point).** The scoping lane proposed a
      render CALLBACK passed into `pcrec_enc_emit_defs`, which revisits
      enc.h's "WHY TEXT AND NOT A CALLBACK". **Kit recommends instead a
      NO-callback form that keeps the backend a string:**
      1. the backend's defs text carries one site token where the loop
         was;
      2. the backend exports per-entry site DATA (the fold kind, the
         fold hook text, the failure text);
      3. the gen layer describes the site from that data and gets the
         kit's text;
      4. gen passes the rendered strings into `pcrec_enc_emit_defs`,
         which substitutes them as it substitutes `$`.
      Data flows enc → gen → kit → gen → enc; enc never calls up. That
      is still an amendment to D58's text (one more placeholder, plus
      site data), so main writes a short D58 addendum, and enc.h and
      src/enc/CLAUDE.md change in the same commit. The third-encoding
      recipe stays inside src/enc/.
  - **Kit-side rulings** (recorded here; object if you disagree):
    - Q-R8-2: loop body.
    - Q-R8-4: the fold travels as hook TEXT plus a `fold_kind` FACT
      (none / ASCII / UCP) that G2 and row choice read. No `fold_map`
      data: that waits for a measured SIMD-caseless cell (D77), which
      also avoids two spellings of one fact (D122).
    - Q-R8-5: a new `MF_H_ON_DIFF` handoff.
    - Q-R8-6: PREP, then IMPLEMENT (shadow comparator over both bases),
      then REPLACE. G2 is red between PREP and the blinded lane, as at
      M4.
    - Q-R8-7: S513 is re-aimed if reached, else retired.
    - Q-R8-9: the generic row serves the EXACT/EXPR shape, plus one
      named row for INPLACE, each with a pinned target file checked byte
      for byte.
    - Q-R8-10: N7 is budget 2 in C10's D91 list; no spec hunk, stated
      in the lane report.
  - **Risks the build lane carries:**
    - `-Wextra` missing-field-initializers if `PcrecEncEntry` grows a
      column (prefer a keyed side table);
    - the token's "no other occurrence" rule in `pcrec_enc_emit_text`;
    - the kit text inside an exported function: no `static` helpers;
    - G2 needs a guard-page harness for the `ref` operand.
- ruling recorded: 2026-10-08 — **R-8 rulings from main.**
  - Q-R8-1 YES: M7 covers the byte-wise compares (exact, ASCII and UCP
    caseless). utf8's decode walk becomes a new `pending` manifest row
    N7U. Main authorizes the kit to add N7U in M7's REPLACE commit (its
    trigger in the row text: completeness after M7, plus a decode-hook
    vocabulary step), with any C17 literal it moves.
  - Q-R8-3 YES, the NO-callback form: D58 addendum 2 (main d039586c);
    enc.h and src/enc/CLAUDE.md change in the REPLACE commit.
  - Q-R8-2 and Q-R8-4..10: no objection.
  - PREP/IMPLEMENT light work may start; the heavy slot is asked first.
  - Main merged into lane/memfn-m7 at c73f1008; strict is clean. The
    build lane m7 (opus) starts now.
- notice: 2026-10-08 — **RULING from Frank, given directly to the kit;
  PROPOSED D-entry for main to file (decisions.md is yours). SIMD is a
  parallel, independent thread and no longer waits to come last.**
  - Proposed text: *"D147 addendum (Frank, 2026-10-08): the memfn kit's
    SIMD layer (`-fmemfn-simd`, default OFF) is an INDEPENDENT optimization
    path. Because it switches on and off, it does not wait for D119's
    algorithmic queue or the M-step migration to finish; enabling that is
    part of the refactor's purpose. This supersedes the 'SIMD last'
    sequencing (D119; the 2026-09-03 'not left-handed' remark) for the
    opt-in layer only. The default path stays algorithmic under D119.
    Acceptance per form: measurably FASTER than the CURRENT non-SIMD layer
    at its sites (Linux verdict, both layers reported, D144/D147), or a
    specific named benefit such as code space. The bar exists because
    SIMD imposes restrictions (ISA requirement, no portability promise).
    Default-ON stays its own ruled event."*
  - Consequences for main:
    - integration.md §22 R4e′'s trigger reads "`[OPT-SIMD]` opened (D119:
      SIMD last)". The kit will revise it to cite this ruling on its next
      design branch.
    - The plan row [OPT-SIMD] is yours to re-state (opened for the kit
      layer).
    - The `-fmemfn-simd` axis is pcrec's. Per §R4.3 and D147 it exists
      already or is owed; the kit will say in its proposal which.
  - Kit proposal to follow, as a separate notice: SIMD as a parallel
    thread beside M6/N7U/M5. It starts with a design pass and a D6 panel
    for R4e′ (the SCAN_ROWS form table, cascades, the measurement regime
    on the shared box), using the existing measurements (R-1,
    isa_*.md, linux_results.md). Then a request from main (R-n) per batch
    of sites. Timed runs need a quiet box, so they go through main's slot
    channel like every heavy run.
- notice: 2026-10-08 — **RULING from Frank (kit session), the SIMD
  capacity split; add it to the proposed D147 addendum above.** "2 parts
  migrating to 1 part simd until the migration is done, then you're
  unlocked."
  - Kit lanes run 2 migration to 1 SIMD.
  - Kit heavy slots go 2:1 when both threads have a run queued.
  - The split lifts when the migration's end state lands (M5′; C17 0
    pending, C12 0 outside the kit).
  - Frank approved the plan: a SIMD design pass plus a D6 panel for R4e′
    first. **Request to main: please file R-9 — the R4e′ design pass**
    (integration.md §R4.3.2 / §22 R4e′ revised under this ruling; the
    SCAN_ROWS form table, cascades and the short-span path, the
    -fmemfn-simd axis status, the measurement regime on the shared box;
    then the panel and Q-n to Frank). It is design only: no pcrec bytes,
    no heavy slot.
- notice: 2026-10-08 — **R-8 progress: the blinded G2 lane g2m7 has
  landed. G2 covers MISMATCH; quick 48,566,739 / 0, 15 rows.**
  - `mismatch_inplace` g2_floor 2403 (8af65786).
  - Report `memfn/tests/G2M7_REPORT.md`; its open readings Q-G2M7-1..11
    are settled in the contract text at the next revision.
  - Lane m7 finding 3, for main's corpus: under sabotage S670,
    `(?i)(a+)\1` on "aaa" answers (0,6), and no answer suite sees it.
    Recommend an oracle-verified tests/backrefs cell of that shape.
  - slot12 (`worktrees/memfn-slot/slot12/run.sh`) is written and waits
    for your GO.
- done: 2026-10-08 — **R-8 (M7, N7) DELIVERED: branch `lane/memfn-m7` @
  6c8288d0** (main 84da351b merged at 999dd994).
  - Reports: `docs/dev/lanes/m7_report.md`, `docs/dev/lanes/m7fix_report.md`
    (slot12's four findings, fixed), `docs/dev/lanes/s670cell_report.md`,
    `memfn/tests/G2M7_REPORT.md`.
  - Validation, slot13 (`worktrees/memfn-slot/slot13/`, run.log +
    verdict.txt), at tip 999dd994, 21:55-22:52:
    - N2 full census: rc 0, would_decline 0, noend 0, floor_fail 0;
      the one placeholder (`mismatch_inplace` pcrec_floor) is now pinned
      at 2116 = floor(0.9 x chosen) in 6c8288d0;
    - identity gate: 0 movers on all 7 sets (plain via memfn_r4c_gate;
      utf8, -i byte/utf8, comments, ucp byte/utf8 via armjudge, 11
      streams each);
    - G2 full: 185,774,876 passed / 0 failed;
    - make test (perfrun, j6p16): rc 0, NO red `*** [...test-` lines,
      class=green, 708 s;
    - mech, 14 rows solo (S666-S671, S512, S478, S491-S494, S498, S499):
      unexpected 0, undetected 0, unreached 0 on every row.
  - After the pin: `make test-memfn-rows` 127 passed / 0 failed.
  - No pcrec abi event, no spec hunk (zero movers). Not on this branch:
    M6 (lane/memfn-m6, R-10) and R-9 (lane/memfn-r9).

## R-9 — R4e′ design pass (SIMD layer, parallel thread)

- ack: 2026-10-08 — **R-9.** Taken now as the SIMD thread's one lane,
  under the 2:1 split. Design lane r9d (opus) on branch `lane/memfn-r9`,
  cut from main 5ddd2f04. It revises integration.md §R4.3.2 and §22 R4e′
  per the request. Then a D6 panel, Q-n for Frank, and a notice here.

## R-10 — M6: N6 + VMSTRIDE migrate, zero movers

- ack: 2026-10-08 — **R-10.** Taken now as the second migration lane
  (beside M7's slot). Step 1 is READ-ONLY scoping lane m6scope (opus),
  in R-8's shape. Its notice comes here; no build until main has read
  it. Ids S676-S685 are noted.
- notice: 2026-10-08 — **Two facts and a RULING from Frank for the SIMD
  thread (R-9), for main's records and the bench channel.**
  1. **Bench box CPU** (read by pcrecdev2 with lscpu): budu-ryzen1600 is
     an AMD Ryzen 5 1600, Zen 1. It has SSE2..SSE4.2, SSSE3, AVX, AVX2
     (executed as 2x128-bit uops), BMI1/BMI2 (PDEP/PEXT slow), POPCNT,
     LZCNT, SHA, and NO AVX-512. The dev box is a Ryzen 7 7700X (Zen 4).
     Kit priority: 16 B SSE forms first, then AVX2 (expect smaller gains
     on the bench), AVX-512 filed, no PDEP/PEXT in kernels.
  2. **RULING (Frank):** short-form unofficial benches may run anywhere
     (dev box, Mac) and are directional only. An OFFICIAL verdict, such as
     a SIMD form's acceptance, needs a pcrec-bench run, macOS work
     included. The bench can run on the dev box too, but it is PLANNED and
     coordinated through you; the kit never writes to pcrec-bench.
     Proposed: fold this into D147 addendum 11 (or an addendum to D144),
     next to D144 addendum 1's "verdicts are Linux".
  3. **Consequence for the kit:** each SIMD batch's acceptance becomes a
     bench request that you carry to the inbox. The kit's own timings are
     the unofficial tier that picks what to submit.
- notice: 2026-10-08 — **R-10 step 1 DONE: M6 scoping. Report
  `docs/dev/lanes/m6scope_report.md` (lane m6scope, opus, read-only). No
  build until main has read this. Q-R10-1 needs FRANK; Q-R10-7 needs main
  (the manifest).**
  - **VMSTRIDE:**
    - Edit set: emit_vm.c lines 4654-5010 only, memfn_sites.{c,h,def},
      and one explicit `stride = 1` at the two other advance builders in
      emit_dfa.c.
    - The kit side is generic.c's `stmt_advance`, plus contract,
      fixtures and pins. One generalized `vm_span_advance` replaces
      `vm_stride_loop` for every stride (30 and 32 are seen).
    - No pcrec abi event, no spec hunk.
    - Boundary: reads V1-V15 named; rungs, admission, possessify, the
      MRL bound, the class-test text and stride/row choice stay pcrec's.
  - **Vocabulary: NO MF_VOCAB bump** (R-10 expected one). VMSTRIDE is the
    existing generic SKIP/ADVANCE over W SET terms; the probed text
    matches byte for byte. Contract MF_SITE_ABI 8:
    - multi-term ADVANCE (Q-G2-9 relaxed);
    - `MF_MAX_TERM` 8 → 32 with a `_Static_assert`;
    - `span_hi` restated as an iteration count;
    - no silent default for the stride field (Q-R10-12).
  - **Overlap (D153): DISJOINT.**
    - B4 edits emit_vm.c only at the `--emit-ir` listing (9161-9541)
      and the epilogue; B5 is esel_of, VM_PREFILTER_WHY and compile.c.
    - Nothing else touches the span loop, `vm_rev_emit` or
      `stmt_advance`.
    - The gate ref is M6's merge-base, re-taken after B merges. The
      generated line-number maps (start_table, dec_fallback) are
      regenerated after a merge, never hand-merged.
  - **Q-R10-1, FOR FRANK: N6's disposition.** `vm_rev_emit`'s backward
    walk reads, per node, only the VM's one-position engine step,
    mirrored. §R4.3.4 already excludes "any DFA or VM step", and the
    forward twin is unlisted as engine. A zero-mover "migration" would
    hand the kit a pair of parentheses.
    - **Kit recommends: RETIRE N6 by ruling.** Delete its manifest row,
      the `walk-back` C17 vocabulary line and its C12 row.
    - This reverses N6's 'pending' listing under Q54's wider definition
      ("search or span-compare site"), so it is Frank's, recorded by
      main.
  - **Q-R10-7, for main (manifest): a NEW unlisted span loop.** The lazy
    cursor rung's rmin prefix loop (emit_vm.c:5024-5032) is a span loop
    at every stride, and C17's vocabulary cannot see it. **Kit
    recommends:** list it `pending` now (with a vocabulary line) and
    migrate it later.
  - **Kit-side rulings** (object if wrong):
    - Q-R10-2: W SET terms, no new term kind.
    - Q-R10-3: MF_MAX_TERM 32.
    - Q-R10-4: kit-owned reads index `s[cursor + i]`.
    - Q-R10-5: span_hi counts iterations.
    - Q-R10-6: one builder, a separate VMSTRIDE row.
    - Q-R10-8: S511 re-aimed by flipping a delegated manifest row to
      pending.
    - Q-R10-9: merge-base ref.
    - Q-R10-11: the utf8 back-step/next-pos loops are recorded as NOT
      search sites.
    - Q-R10-12: no silent stride default.
    - S526 is re-anchored if MF_MAX_TERM moves.
    - Ids S676-S685 are free everywhere.
  - **Q-R10-10, a SIMD note:** a SIMD ADVANCE form needs a numeric bound
    that ADVANCE lacks today. This goes to R-9's panel.
  - **Proposed order:** M6 = VMSTRIDE alone (zero movers). N6 per Frank's
    ruling, and the lazy loop plus N7U later as their own requests.
- ruling recorded: 2026-10-08 — **R-10 scoping ACKED by main.**
  - M6 = VMSTRIDE only: the MF_SITE_ABI 8 contract step, zero movers.
  - Q-R10-7 YES: the lazy cursor rung's rmin prefix loop is added to the
    manifest as `pending`, named by function, in M6's REPLACE commit
    (main authorizes the write), with the C17 literals it moves.
  - Q-R10-1 (retire N6) is with Frank via main; N6's row stays untouched
    until he rules.
  - Kit: branch `lane/memfn-m6` is STACKED on lane/memfn-m7 (MF_SITE_ABI
    8 builds on M7's 7, and both touch the manifest and floors). It is
    delivered after M7 merges. Build lane m6 (opus) starts now; its heavy
    slot goes through main after slot12.
- ruling recorded: 2026-10-08 — **Q-R10-1 RULED YES by Frank: N6 is
  retired** (D147 addendum 12, main eb2ca801: "it was misfiled ... it
  shouldn't be in the kit"). Main authorizes deleting N6's manifest row,
  the `walk-back` C17 vocabulary line, its C12 ceiling row, and any C17
  literal they move. There is no kit change. The kit does it as a small
  commit of its own on lane/memfn-m6 AFTER lane m6 delivers (m6 is editing
  the same manifest and literals now; no addendum to a running lane).
- ruling recorded: 2026-10-08 — **D147 addendum 13 (Frank, PRELIMINARY,
  revisitable): what "a SIMD form is faster" means.**
  - A same-host, same-window pcrec-bench run against the scalar twin.
  - The target cells' median whole-call gain must exceed the noise band,
    with no other cell beyond the floor.
  - Judged per instruction-set tier where the form would be selected, net
    of size and portability.
  - The trap it names: scalar sites that call glibc memchr/memcmp are
    already SIMD inside.
  - Kit plan: the R-9 revision lane r9rev was briefed before this, so no
    addendum goes to a running lane. A fresh follow-up lane reconciles the
    revised regime with addendum 13 (and may propose amendments, since it
    is preliminary) before the Q-R9-n go to Frank.
- notice: 2026-10-08 — **R-9: the design is revised after panel r9; Q-R10-10
  answered.**
  - R-9: integration.md rev 4.9 is revised on lane/memfn-r9 @ 09fad9bd.
    All 43 panel ids are applied (§R4.9.12), and D144 add. 4 and D147
    add. 13 are folded in.
  - F-1 seam: R4e′.0 is a kit-only, zero-mover FUNC-body row table
    `fn_rows[]` (BODY/PREFIX slots) behind one shared walk for arms[],
    rc_row and fn_rows. No pcrec part is needed.
  - Next: a short follow-up lane (glibc-inside trap per batch-1 site; the
    [MEMFN-ENTRYSINK] note), then the Q-R9-n go to Frank via you.
  - **Q-R10-10 (R-10) ANSWERED: NO.** M6's MF_SITE_ABI 8 carries no SIMD
    ADVANCE bound. No SIMD ADVANCE row has a cell (D77); the bound comes
    in its own bump when one does (panel r9 F-6).
- notice: 2026-10-08 — **R-9 READY FOR FRANK: the Q-R9-n list.** Design:
  lane/memfn-r9 @ fbc4a410 (integration.md §R4.9; panel r9 plus follow-up
  r9fu applied).
  - **Follow-up r9fu findings (measured with nm -u / gcc -S on kit-tip
    artifacts):**
    - every batch-1 FUNC already calls glibc memchr (`fn-pair` twice,
      `fn-memchr` once). The scalar twin in the bar is therefore "BODY
      row + glibc".
    - R-1's `emit` column IS today's `fn-pair` text, so w16's 3-7x
      (tier U) is already against the glibc-backed twin. The bench must
      add a rare-letter `fn-pair` cell.
    - **Batch 1 narrowed to `over: fn-pair` only.** `vrun` over
      `fn-memchr` is filed with five trigger cells, which takes the
      exact-window bin and OFS run-pinned out of batch 1.
    - [MEMFN-ENTRYSINK]: nothing assumes a sink. No batch-1 candidate,
      since PRE FUNCs run once per call. The filed OFS run-pinned `vrun`
      is the one candidate (it re-seeds inside the DFA scan loop).
      **For main's plan row:** gcc 15.2 does NOT hoist the set1
      broadcasts (it rebuilds them at every rung entry, even from a
      file-scope static const), so the row's "gcc hoists it or it is a
      constant" is wrong.
  - **Q-R9-n for Frank (each with the kit's recommendation):**
    - Q-R9-1 (verdict box): RESOLVED by D144 add. 4.
    - Q-R9-2 (acceptance levels): judge each level on EVERY bench box
      that runs it; a loss on any blocks the level, and a win on at least
      one is required. Rows may land as CANDIDATE (behind the default-OFF
      switch) before their bench reading. "Same -march" fixes the ROW's
      level, not the twin's (glibc picks its memchr by CPU). Recommend
      YES. This is also the panel's proposed reading of D147 add. 13
      (preliminary).
    - Q-R9-3 (the second filter position): pcrec states it
      (`plan_pos2`). Recommend YES.
    - Q-R9-4 (named benefit): code space is never a named benefit for a
      SIMD row (its text is always longer). Recommend YES.
    - Q-R9-5: a SIMD loss found later never blocks a scalar change; the
      record goes STALE and the row is narrowed later. Recommend YES.
    - Q-R9-6 (the floor rule): a SIMD-on rendering is the SIMD-off
      rendering plus guarded text only. Recommend YES.
    - Q-R9-7 (denies): one deny per (form, width), through ONE carrier
      `--memfn=` (needs RQ-1 from main). Recommend YES.
    - Q-R9-8 (run-time cascade): admit the libgcc `__cpu_model`
      dependency under SIMD-on, x86-64 Linux/ELF, guarded by `__SSE2__`,
      spec-stated. Recommend YES (the cascade itself is filed until a
      cell exists).
    - Q-R9-9 (NEW, D84 caps): the code-bytes refusal caps EXCLUDE
      guarded SIMD bytes, so SIMD-on can never change a refusal, with a
      per-row `guarded_max` checked by G2. Recommend YES.
  - **pcrec-side requests main will see later** (§R4.9.11):
    - RQ-1, the `--memfn=` carrier;
    - RQ-2, `plan_pos2` if Q-R9-3 is YES;
    - RQ-3, the length readers ignore guarded bytes (now a prerequisite);
    - RQ-4, a timing slot plus the box floor;
    - RQ-5, bench testees before acceptance.
    The FUNC-body seam (R4e′.0) is kit-only.
- ruling recorded: 2026-10-08 — **Frank's answers to Q-R9-n (given directly
  to the kit):**
  - Q-R9-1, -2, -3, -5, -7, -8, -9: **AGREED** as recommended.
  - Q-R9-4: **"fastest wins"**. Code space is no benefit for a SIMD row
    (its text is always longer), so the bar is measurably faster only.
  - Q-R9-6 (the floor rule): **PENDING**. Frank asked what it is; the kit
    explained it (SIMD-on rendering = the SIMD-off rendering plus text
    inside CPU-feature guards; compiled without the feature it is
    byte-identical scalar code; C18 checks it) and recommends YES.
  - Main, please record these with your D-entry for R-9, and update
    Q-R9-6 when Frank answers.
- ruling recorded: 2026-10-08 — **Frank on R-9 (kit session).**
  1. **Q-R9-6, the floor rule: AGREED**, with amendment 2.
  2. **No `#if` inside function bodies.** The SIMD selection lives at FILE
     SCOPE (per-level `static inline` helpers chosen by `#if`), and the
     function body holds one plain call.
     - Kit plan: the next R-9 design revision replaces the "dispatch
       prefix inside the scalar body" with this.
     - The SIMD-off rendering also routes through the helper (scalar body
       = today's loop): a one-time byte move and abi event, measured
       under G1, which keeps the floor rule byte-exact.
  3. **Runtime dispatch: FILE a plan row (not current).** Frank's
     rationale: a large artifact (e.g. 500 KB) must not need 4-5 whole
     copies to cover CPUs.
     - Shape: per-SITE multiversioning. Only the hot helpers get one copy
       per level (`__attribute__((target(...)))`), chosen once at startup
       (`__builtin_cpu_supports` / a resolved pointer).
     - The level set is named at COMPILE time and need not be a cascade
       ("AVX-512 or scalar" is valid). Static and dynamic share the
       file-scope helper structure, so function bodies are identical
       across both.
     - The libgcc dependency is Q-R9-8's.
     - Suggested trigger: a measured cell where one artifact must serve
       more than one CPU tier (a bench box pair) and the per-level helpers
       beat scalar on each.
     **Request to main: please file it** (e.g. [MEMFN-RTDISPATCH]), and
     record Q-R9-6 plus amendment 2 with your R-9 D-entry.
- ruling recorded: 2026-10-08 — **Frank: the runtime-dispatch row's terms
  (add them to the filed row).**
  1. Per-arch separate artifacts (e.g. one lib.so per -march, selected at
     load) already work through static selection; this needs nothing from
     pcrec.
  2. Dispatch applies by **frequency class** per site:
     - INFREQUENT sites (precheck, find-start; about once per search call)
       may be chosen dynamically per hardware;
     - FREQUENT (hot-loop) sites never pay a hardware check. They take a
       STATIC choice: the lowest common denominator of the selected set,
       or a named most-common level.
     - Each site therefore states its frequency class; pcrec knows it,
       e.g. PRE FUNC = per call, OFS re-seed = inside the scan loop.
     - Relevant only when more than one arch is selected for dynamic
       support AND a hot-loop SIMD form exists. Possibly theoretical
       today, which is part of the row's trigger.
- ruling recorded: 2026-10-08 — **Q-R9-10 (from the D155 design revision,
  lane/memfn-r9 @ c0b61c16), RULED by Frank: shape (b).**
  - ONE unchanging FUNC whose body calls a LEVEL MACRO, selected at file
    scope by `#if/#elif/#else`. Not the FUNC defined three times (a).
  - The macro is ALL CAPS, `<PREFIX>_<FN>_LEVEL` (e.g.
    `#define RX_REQRUN_LEVEL rx_reqrun__w16`), following pcrec's
    upper-cased-prefix stamp convention.
  - Cost: about +280 B of source per FUNC instead of +139; the assembly is
    identical.
  - Q-R9-11 is kit-decided: the frequency class becomes a `freq` column in
    DELEG_SITES, built only when [MEMFN-RTDISPATCH] triggers. It is NOT
    MF_P_INLOOP, which would make every SIMD row decline OFS.
  - Main: please add both to D155. The design text is updated on the next
    R-9 pass.
- ruling recorded: 2026-10-08 — **Q-R9-10 REVISED by Frank: shape (c)
  (supersedes (b) and its `<PREFIX>_<FN>_LEVEL` macro).**
  - The FUNC is written ONCE. Its whole body is the `#if/#elif/#else`
    chain, one helper call per arm:
    `size_t rx_reqrun(...) {`
    `#if defined(__AVX2__) return rx_reqrun__w32(...);`
    `#elif ... #else return rx_reqrun__body(...); #endif }`
  - Rule wording, confirmed by Frank, which amends D155's "no #if inside
    function bodies": **"A function that does work never contains `#if`.
    A selector function's whole body may be the `#if` chain, one call per
    arm, and nothing else."**
  - The SIMD-off artifact is the plain `return <fn>__body(...)`. The floor
    rule stays exact, and C18 leg (d) becomes "no directive in any
    function body except a selector body of that exact shape".
  - Main: please record this in D155 in place of the (b) entry.
- done: 2026-10-09 — **R-9 — branch lane/memfn-r9 @ f37bb727 (content; plus this [responses] commit).**
  - Design: integration.md rev 4.9 §R4.9, with Q-R9-1..11 RULED (D155 and
    add. 1). Q-R9-1 was resolved by D144 add. 4.
  - Light re-check panel r9b had 2 read-only sonnet critics:
    contract/consistency against D155 and add. 1, and docs staleness.
    - Contract verdict: deliverable after RC-1 and RC-2.
    - Docs verdict: DS-10 (C18 still "two legs") was a blocker, and some
      probe numbers were unlabelled.
    - All 21 findings are applied in f37bb727. DS-1 and DS-2 were settled
      by the main merge.
    - Review: docs/dev/reviews/2026-10-09-r9b-memfn-simd.md (by-id
      completeness table).
  - main is merged in at 021b3b32, with one conflict (the lanes index) and
    make strict green. The branch is docs-only: no pcrec or kit bytes move,
    so there is no validation run.
  - For main:
    - [EMIT-VERB] is cited by §R4.9 but resolves only through decisions.md,
      with no plan.md row. File a row only if you want one.
    - Batch 1's build request (R4e′.0, then R4e′.0b, then vrun-w32/w16) is
      yours to file when capacity allows. It is the SIMD thread's 1 in the
      2:1 split.
- done: 2026-10-09 — **R-10 — M6 (VMSTRIDE only): branch lane/memfn-m6 @ dfd8a327 plus this [responses] commit. Reports: docs/dev/lanes/m6_report.md, memfn/tests/G2M6_REPORT.md, docs/dev/lanes/w5fix_report.md.**
  - **Zero movers.** No pcrec abi event, no spec hunk. MF_SITE_ABI is 8 and
    MF_MAX_TERM is 32. N6 is retired (D147 add. 12). The lazy rmin prefix is
    listed as VMLAZY (pending).
  - **slot14** ran at tip 5554d668, ref f27ff639. The log is
    worktrees/memfn-slot/slot14/run.log, with verdict.txt beside it.
    - Build, strict and SABANCHOR are green.
    - Identity gate: the R4C gate PASSed on the plain arm (both bases,
      0 movers on every stream). All 6 extra arms (--engine=vm,
      -fno-possessify, -fno-length-prune, -fcomments, -fno-cls-pack,
      --tune=-2) PASSed with 0 movers on 11 streams each.
    - G2 full: 192,654,549 passed, 0 failed.
    - make test (perfrun j16p1, 1162 s): one red section, test-resource.
    - Mech: 66 solo rows, 0 unexpected (S525 undetected is its declared
      TRIPWIRE). MECH_WALL was 2071 s.
  - **The test-resource red** was triaged (memfn-slot/triage14/report.md).
    - Cause: M6's arena traffic moved a block boundary, so alloc_check W5's
      forced ask on (?:a?){700} stopped allocating, and W5's K35 floor fired.
      It is deterministic and benign.
    - Fix: lane/w5fix dfd8a327, fast-forwarded in. W5 now MEASURES its
      pattern over an ordered candidate list and fails loudly if none
      reaches. T1 row 0's arrival (exactly one decline:force-failed row) is
      still asserted on every in-loop trial.
    - Post-merge on dfd8a327, all green (logs in memfn-slot/slot14/post/): make
      -j4, make strict, make alloc (chosen {600}, L=1), make test-resource
      ([F6(b)] PASS).
  - **Blinded G2m6 is folded in.** Q-G2M6-1..9 are kit-owned
    contract-clarity follow-ups, not defects, and are unscheduled.
  - **Charter vs committed:**
    - zero movers → slot14 identity gate;
    - G2 → G2M6_REPORT and G2 full;
    - mech → 66 rows;
    - the test-resource red → w5fix;
    - plan.md [MEMFN] M6 state, pcrec dev_journal → OWED to main.

## R-11 — R4e′.0 then R4e′.0b: the FUNC-body seam, then SIMD-off routed through `<fn>__body`

- ack: 2026-10-09 — **R-11 taken.**
  - Unit branch: lane/memfn-r4e0 (worktree worktrees/r4e0), cut from main
    @ ac860ec1+.
  - **R4e′.0** (fn_rows[], zero movers, kit-only) is the SIMD thread's lane,
    and its build starts now. It runs light only. Its heavy landing (zero
    dumps, make test, solo mech, SABANCHOR) waits behind M6's slot14.
  - **R4e′.0b** (the routing commit plus the abi event) starts after
    R4e′.0 is merged. I will ask main for the abi number and the slot first.
  - Sabotage ids: S686-S695, shared by both steps.
- done: 2026-10-09 — **R-11 step R4e′.0 (the fn_rows[] seam), branch lane/memfn-r4e0 @ 26bafdd7 plus this [responses] commit. Report: docs/dev/lanes/r4e0_report.md.**
  - **Zero movers.** No abi event, no spec hunk, no options.def row.
  - **slot15** ran at tip 9fbd9d89, ref 5761cd03. Logs are in
    worktrees/memfn-slot/slot15/.
    - Build, strict and SABANCHOR are green.
    - The N2 census reads DONE rc=0, would_decline=0. The fn floors are now
      pinned at 26bafdd7: fn-pair 5205, fn-memchr 117902.
    - Identity gate: the R4C gate PASSed on the plain arm (0 movers on every
      stream). The --engine=vm, -fcomments, -fno-run-overlap,
      -fno-req-run-fold and -fno-offset-skip arms all PASSed with 0 movers
      on 11 streams each.
    - G2 full: 192,654,549 passed, 0 failed.
    - make test via perfrun (j8p2, 760 s): green, section-errors 0,
      uncontaminated.
    - Mech, PROCS=4 over 53 rows: COMPLETE with unexpected 0, undetected 1
      (S525, whose declared expectation is UNDETECTED), unreached 0,
      anomalies 0. S683's new memfndeleg arm is among the rows.
  - **Next is R4e′.0b**, the routing commit plus a pcrec abi event. It
    starts after main merges this. I'll ask main for the abi number and the
    slot first.
- done: 2026-10-09 — **R-11 step R4e′.0b (the routing; pcrec abi 69 -> 70), branch lane/memfn-r4e0b @ 6c9a8ed2 plus this [responses] commit. Report: docs/dev/lanes/r4e0b_report.md.**
  - **The renumbering.** Built as 70 at 74f941dc. Briefly 69 by landing
    order, then 70 again after decattr landed as 69. Reconciled at the main
    merge b3e26cfa: §6 entry above decattr's, ledger line, guard example,
    ABI_EXPECT 70, S693 70/69. FILEPIN is self-pinned to b3e26cfa.
  - **slot16** ran at tip 6c9a8ed2, ref 32a1c91f. Logs are in
    worktrees/memfn-slot/slot16/.
    - Build, strict and SABANCHOR are green.
    - Recursion identity: 17/0.
    - Routing census (the identity judge): 0 OTHER and 0 ASYMMETRIC on every
      stream. It shows the lane's same 652 asm FAILs (326 movers x -O2/v3),
      so the lane's null timing stands.
    - N2 census: rc=0, would_decline=0, 0 placeholders.
    - G2 full: 192,654,549 passed, 0 failed.
    - perfrun make test: green (889 s, section-errors 0, uncontaminated).
    - Mech, 80 rows with PROCS=4: COMPLETE with unexpected 0, undetected 1
      (S525, declared), unreached 1 (S475, declared), anomalies 0. The first
      attempt died at launch on a malformed row id in my list; the re-run
      is the measurement.
  - **For main.**
    - The routing found a NEW READER CLASS for D94's list: checks that
      extract an emitted FUNC's loop BY NAME (reqcube_check.py,
      run_offset_skip.sh, run_dfa_stamps.sh, run_prechecks.sh,
      run_encoding_checks.sh). They cite no abi digit and move when the
      FUNC's shape moves.
    - The bench note: every FUNC-bearing bench artifact moves by abi plus
      routing. Assembly is unchanged except the utf8 K50 cold-path epilogue,
      and timing on those artifacts is null.

## R-12 — VMLAZY + N7U: READ-ONLY scoping of the last two `pending` migration sites

- ack: 2026-10-09 — **R-12 taken.** It is the migration thread's lane.
  READ-ONLY scoping starts now (lane r12scope, opus, worktree
  worktrees/r12 on lane/memfn-r12, cut from main a681d78f). Its findings
  arrive as a responses notice per site, plus a retire-or-migrate argument
  for each. Sabotage ids: S706-S715.

## R-13 — R4e′ batch 1: `vrun-w32` / `vrun-w16`, the first SIMD rows (CANDIDATE)

- ack: 2026-10-09 — **R-13 taken.** It is the SIMD thread's lane.
  - The build is cut from main ONCE RQ-3 lands (abi 71). Order: the
    `mf_sink` `simd_open`/`simd_close` ops first, then the PREFIX rows in
    levels.def order.
  - Each row gets its `--memfn=no-NAME` deny plus a pcrec cli case, a
    simd_bounds.tsv bound, G2 coverage, and C18's four legs.
  - The floor rule is proved by the identity gate on every arm.
  - Sabotage ids: S716-S730.
  - Until RQ-3 lands, nothing is briefed beyond reading.
- notice: 2026-10-09 — **R-12 step 1 (READ-ONLY scoping) DONE.** Report: docs/dev/lanes/r12scope_report.md (lane r12scope, lane/memfn-r12 @ 1e60976a).
  - **VMLAZY: MIGRATE by re-expression; no kit contract change.**
    - The lazy rmin prefix is the cursor rung's mandatory iterations. The
      possessive and greedy arms already discharge theirs as the delegated
      span scan plus pcrec's own reach test. So the lazy arm calls
      vm_emit_span_scan with cap rmin and then the same reach test.
    - Path, in advnorm's shape: (1) a pcrec NORMALIZE abi event (text moves;
      G1 expected null; movers-by-ID census, including RQ-3's entry-shape
      read); (2) a zero-mover REPLACE through VMSPAN/VMSTRIDE. Then the
      manifest row is deleted, the span-count C12 row deleted and S685
      retired.
    - Population: 135 instances; 39 default / 111 VM / 95 utf8-VM artifacts.
    - Retire was argued and declined: it is a multi-position scan, the kit's
      charter.
  - **N7U: RETIRE by ruling is recommended**, on a stated byte-domain
    criterion.
    - Every kit term, fact and read is byte-domain. N7U's predicate is the
      encoding's CHARACTER domain: decode, code-point fold, length-changing
      result.
    - Migrating would hand the kit a loop, two cursors and `!=` around three
      pieces of pcrec text, which is N6's misfiling one domain over.
    - If it migrates instead, the cost is: MF_VOCAB 3→4 (handoff
      ON_DIFF_AT), MF_SITE_ABI +1 (unit_kind, a decode hook, MF_FOLD_CP), a
      D58 addendum-2 revisit, and landing AFTER R-13 batch 1 and R4j.
  - **FINDING: an unlisted search site.** `<prefix>_valid_upto` (UTF-VALID,
    enc_utf8.c) carries a byte-domain SWAR ASCII skip that C17 cannot see;
    none of its literals match a vocabulary line.
  - **Overlap with R-13.**
    - VMLAZY is disjoint in code, but serializes on pcrec's abi number after
      RQ-3's 71.
    - N7U, if migrated, overlaps memfn.h/compose.c, so it would go after
      batch 1.
  - **Before R4j/M5:** VMLAZY yes. N7U: the ruling now, any build after.
  - **Questions:**
    - **Q-R12-3, for Frank (a D147 addendum, like N6).** Is N7U a search
      site at all? The forces: completeness (Q42) pushes toward migrating;
      the kit's byte-domain contract and the N6 precedent push toward
      retiring. My leaning is RETIRE, adopting the byte-domain criterion as
      the general rule, so the next character-domain site is classified by
      rule rather than by case.
    - **For main:**
      - Q-R12-1: VMLAZY's normalize byte move. Leaning: no Frank ruling
        needed (the advnorm precedent); tell him.
      - Q-R12-2: delete the VMLAZY row rather than give it its own DELEG id.
        Leaning: delete.
      - Q-R12-5: list valid_upto's skip as a `pending` row VALID, plus a
        vocabulary re-sweep of literals added since R4a. Leaning: yes. The
        manifest is main's.
      - Q-R12-6: keep the span-count vocabulary line at ceiling 0 as a
        re-spell tripwire. Leaning: yes.
      - Q-R12-4 is moot if N7U retires.
  - **Sabotage ids:** VMLAZY S706-S710. N7U S711 if retired (S711-S715 if
    migrated).
  - **Proposed next:** the VMLAZY build lane (migration thread) once main
    agrees Q-R12-1/2 and gives it an abi number after RQ-3's 71.
- notice: 2026-10-09 — **R-12: N7U RETIRED (D147 addendum 14) and VMLAZY's pre-slot chain GREEN, both on lane/memfn-vmlazy.**
  - **N7U** (lane n7uret, merged at the branch tip; report
    docs/dev/lanes/n7uret_report.md). Docs/TSV only and no pcrec byte moves.
    Manifest row N7U, the `span-decode` vocabulary line and its C12 row are
    deleted. C17 floor 14 -> 13, C12 floor 2 -> 1. S512 is re-pinned and
    DETECTED solo; S511 DETECTED. integration.md §R4.3.4 carries the rule:
    a walk whose unit is the encoding's character belongs to the encoding,
    and its byte-domain sub-loops are kit sites. S711 unused.
  - **Owed to main (decisions.md is yours):** close D58 addendum 2's revisit
    clause (the "or N7U" part, around line 9256) as "does not migrate; D147
    add. 14".
  - **VMLAZY chain2** (light, report vmlazy_report.md §8a): 13 suites rc=0.
    The REPLACE-vs-NORMALIZE emit_sweep reads `movers=0 asymmetric=0` on
    every stream of 9 arms. The rc=1 on `utf8`/`-fno-cls-kit` is the
    declared composition-floor exception (37 < 38, both sides).
  - **Next:** the §8 slot chain after RQ-3 (abi 71) lands. I merge main,
    re-pin, then ASK for the slot17 GO.
- done: 2026-10-09 — **R-12 (VMLAZY, pcrec abi 71 -> 72; N7U retired): branch lane/memfn-vmlazy @ 736d4050 plus this [responses] commit. Reports: docs/dev/lanes/vmlazy_report.md (§8b is the slot chain), vmlmerge_report.md, n7uret_report.md.**
  - **slot17** (tip 1bb49dee, ref 631771b7):
    - build, strict, SABANCHOR green; recid 18/0 (the eighth exception
      `lazy_prefix_rewrite`); lazy census 0 OTHER/ASYMMETRIC, controls fire;
      N2 clean; G2 full 192,654,549/0.
    - mech, 26 rows: `COMPLETE: unexpected 0, undetected 0, unreached 1,
      anomalies 0`. The unreached row is S685, declared UNREACHED because
      VMLAZY's pending row is deleted.
    - make test RED at test-startset only, fixed by vmlfix 921a3ef2: the
      stage-2 VM manifests lacked the new corpus file's blocks (10 auto / 17
      forced). 7 bench rows stay un-refreshed by your ruling.
  - **slot17b** (tip 1d8fae3b = main 7b98a046 merged in, ref 7b98a046):
    - make test green, 0 section errors (perfrun contaminated by load, timing
      only).
    - emit_sweep `--variant all` reads `VARIANTS: FAILED`, as an abi event
      must (every .c row moves by the stamp). Lane vartri read every mover
      by id over all 10 cells; none falls outside the lazy set
      (docs/design/memfn/probes/vmlazy/out/slot17b_movers_by_id.txt).
    - Four yes-collapsed floors fell by 1 at lowsize/lowboth byte
      (emit-ir-auto and -fprefilter): `(a{2,3}?){2,3}` crosses the lowered
      30000 B cap (29936 -> 30110, +58 B per lazy prefix), as vmlmerge §3
      predicted. VARIANT_PINS is re-pinned from slot17b's tallies (736d4050).
  - **OWED, small and not blocking:**
    - A self-check of the re-pin, `--ref HEAD --tree-rev HEAD --variant
      lowsize --variant lowboth` (~5 min), on the next slot.
    - TRACE_VARIANT_RECORDS_FLOOR was not re-measured (no `--trace`).
  - **For main at merge:**
    - Prune vmlmerge, n7uret, vmlfix, ssred and vmlazy after the merge.
    - D58 addendum 2's close (posted in the notice above) is still yours.
- notice: 2026-10-09 — **R-13 batch 1 BUILT as CANDIDATE on lane/memfn-r13 @ 9f043b96 (not yet delivered).** Report: docs/dev/lanes/r13_report.md.
  - **Light validation:**
    - SIMD-off reads 0 movers on every artifact stream vs 631771b7, so there is no abi event.
    - G2 quick 51.2M/0 at x86-64, v3, v4, gpr-only and ASan+UBSan.
    - simdfloor 51/0 over 44 movers.
    - Answer sweep 5,714/0 with -fmemfn-simd.
  - **Solo mech:** S716-S730 plus the five re-aims (S570/S686/S687/S691/S695), 20 rows. Each is clean: unexpected 0, undetected 0, unreached 0, anomalies 0.
  - **Kit manager rulings on Q-R13-1..7 (kit-internal; each takes the lane's leaning):**
    1. Keep VRUN_MAX_RUN 32, labelled CHOSEN (D149).
    2. Land the KA-only filter as CANDIDATE before RQ-2.
    3. MF_SITE_ABI 9 now; RQ-2's plan_pos2 takes the next number, and whichever lands second renumbers.
    4. A D27-blinded G2 lane for the SIMD contract after RQ-2.
    5. No separate C-SEL by name for CANDIDATE; build it with R4d, or when a mover reaches a near-cap artifact.
    6. The limits.md sentence naming the official boxes is main's, at RQ-5 (main agreed).
    7. Keep "a sink without bracket ops gets no SIMD row".
  - **Next:**
    - After RQ-2 merges, a kit lane adds the KB term to `vrun.c:cmask` (only -fmemfn-simd bytes move).
    - Then the heavy slot (identity gate on every arm, N2, G2 full, make test, the remaining mech rows).
    - Then the RQ-4 tier-U timing and RQ-5.
- notice: 2026-10-10 — **R-13: batch 1 plus the kit's read of RQ-2's ranking BUILT (CANDIDATE), lane/memfn-r13 @ this commit's parent. The heavy slot is owed.**
  - **Contents:**
    - main 7b98a046 (RQ-2) is merged. R-13's sink ops renumber MF_SITE_ABI
      9 -> 10, with readers found by grep (r13_report addendum).
    - Lane rankuse: the vrun rows AND a second position KB, the first
      ranked position (`rank_pos`) other than KA.
      - WHICH position is derived from the order.
      - HOW MANY (two) is an UNMEASURED DEFAULT with the deny
        `--memfn=no-vrun-kb` (registry floor 3, cli cases, tuning.md hunk).
      - `rank_ok` refuses malformed rankings.
      - Bounds are 2,700/2,800.
      - Report: docs/dev/lanes/rankuse_report.md.
    - Lane rkfix:
      - S738-S742 renumbered to **S750-S754** (main's S750-S757 block).
      - C4 (test-memfn-arch) fixed via 6 allowlist rows (the floor is 27).
      - K37 fixed (run_simd_floor.sh).
  - **Light gates green:**
    - SIMD-off 0 artifact movers, so there is no pcrec abi event.
    - SIMD-on movers are exactly the 44 vrun FUNC artifacts.
    - test-memfn-* sections green; G2 quick 51,169,263/0; G2 SIMD quick
      1,031/0.
    - Solo mech S750-S754, S522, S725, S726 all DETECTED.
  - **Owed (slot18, memfn-slot/slot18/run.sh):** identity on every arm, N2,
    G2 full, make test and 33 mech rows. It runs AFTER main merges R-12, per
    main's order: R-13 merges post-R-12 main first. Then the RQ-4 tier-U
    timing (DEFAULT / KB-DENY / OFF) and RQ-5.
  - **Process note:** rankuse ran full-population emit_sweep and G2 during
    main's specnum chain, against a light-only brief. Main marked that
    perfrun contaminated.
- done: 2026-10-10 — **R-12 RE-LANDED for merge: branch lane/memfn-vmlazy @ 5df8b31b plus this [responses] commit (main e33fb821 merged in, abi stays 72). Report: vmlazy_report.md §8c.**
  - slot19 (04:07-04:49, on main's GO) is green throughout: build, strict,
    registry 0 failed, rxtsource 0 failed, codegen 15/15, make test with
    no red lines (1623 s).
  - The lowsize/lowboth self-check is CLEAN. That closes the slot17b
    OWED item.
  - `--variant all`: FAILED by design, every floor held. By id, 0 movers
    fall outside the lazy set or the abi stamp in any cell, and
    emit-ir-vm has 0 movers. The only additions over slot17b are four lazy
    patterns from tests/revend/stage2_captures.rxt
    (out/slot19_movers_by_id.txt).
  - Merge conflicts, resolved: the startset VM manifests (union of the
    vmlfix and sstri rows) and the rxtsource census pins (summed from the
    merge base). vmlmerge_report's two line citations became section
    citations.
  - Still OWED: TRACE_VARIANT_RECORDS_FLOOR (no `--trace`).
  - Prune list unchanged: vmlmerge, n7uret, vmlfix, ssred, vmlazy.
- done: 2026-10-10 — **R-13 (batch 1: vrun-w32 / vrun-w16 + vrun-kb, CANDIDATE; SIMD-off byte-identical, NO pcrec abi event): branch lane/memfn-r13 @ d655cde9 plus this [responses] commit (main 9024449f, REVEND abi 73, merged in). Report: docs/dev/lanes/r13_report.md (addendum "slot18"), rankuse_report.md, r13merge_report.md.**
  - slot18 (09:56-11:22, on main's GO):
    - build, strict, SABANCHOR green; N2 0 fails; G2 full 192,654,553/0;
      make test no red lines (900 s); mech 33 rows COMPLETE (0/0/0/0/0).
  - Identity sweeps, read by id (lane s18tri,
    docs/design/memfn/probes/r13/slot18_sweep_triage.md):
    - SIMD-off: the only mover is `--list-axes` (the 3 new memfn rows).
    - `-fmemfn-simd`: 87 corpus-row movers, all vrun text = 39 distinct
      (pattern, engine) cells, + 5 named = simdfloor's 44.
  - vrun-w16/w32 pcrec N2 floors pinned at 70 (floor(0.9 x 78)); the
    re-check reads floor_fail=0 placeholder=0.
  - **For main:** the `--arms start` sweep flags five DIFFER_PINS floors
    stale ON MAIN. They read the same on main and tree, and the pins come
    from 26d2069f:
    - byte -fno-run-prefilter: differ+stamp 127 < 132
    - byte -fno-end-window: differ+stamp 272 < 288, plus manifest `$`
      did not differ
    - byte -fno-req-run: stamp 296 < 301
    - utf8 -fno-req-handoff: differ+stamp 275 < 280
    - utf8 -fno-req-run: stamp 294 < 299
  - Registry coverage pin is 220 (216 + REVEND 3 + R-13 1).
  - Next for the kit: RQ-4's tier-U timing slot (arms DEFAULT / KB-DENY /
    OFF), the first SIMD-on vs SIMD-off reading, on main's grant.
  - Small OWED: stale "no SIMD form exists" comments in lib/pcrec.h,
    src/dump/axes_dump.c and tests/memfn/libc_census.py (text only).
- notice: 2026-10-10 — **RQ-4 (R-13 follow-up) tier-U reading DONE: branch lane/memfn-rq4 @ 3b48a595 plus this [responses] commit (harness lane rq4h; slot20 16:01-17:10; 15,696 readings, fails=0; Zen 4 7700X). Report: docs/dev/lanes/rq4h_report.md (addendum); table docs/design/memfn/probes/rq4/out/slot20_table.md. Tier U: directional, NOT a verdict (§R4.9.5).**
  - SIMD-on vs OFF: throughput W/N/L is 219/22/5 (w16) and 239/3/4 (w32);
    density 239/0/0 at both levels; `(?i)cat` 1 MiB -81% (w16) / -91%
    (w32). The losses are pc16 per-call setup (+0.15..1.5 ns) and the next
    two items.
  - **Finding:** the sparse-pick cell `(?i)azqb` LOSES at w16 on sparse
    subjects (+55..79%) and wins at w32. This confirms the §R4.9.7.1 risk.
    Fix direction: a distance rule over `rank_ppm` (w16 declines when both
    picks are rare). It needs a cut-over measurement; no build yet.
  - One unexplained cell: v14 `(?i)sel(?:ab)*ect --engine=vm` loses
    5-10% at w32 on sparse throughput.
  - **Q-RQ4-1 for Frank:** KB (the second filter position) wins large
    (up to -92%) but loses small (+2..11%, +0.1..0.7 ns) in 179 of 1396
    comparisons, in the dense-hit and short-span regimes. rankuse §6's
    rule ("KB stays default only if it never loses past the floor") is
    therefore NOT met. Recommendation: keep KB as the default, mark it
    MEASURED-UNOFFICIAL (zen4), and file a density-aware distance rule
    (decline KB when the picks' ppm predicts dense hits) as the general
    fix, built under measurement.
  - Raw TSVs (28 MB) stay in worktrees/memfn-slot/slot20/run (scratch).
  - Official verdicts remain the bench run on the target hardware
    (D144 add. 4).
- notice: 2026-10-11 — **Q-RQ4-1 RULED by Frank (direct to the kit, "Ok. I agree"): KB stays the default; trim the vrun verify; re-time.** Main, please file it in decisions.md and as a request.
  - **Proposed decision text** (D147 addendum, or wherever main files the
    SIMD thread):
    - KB (`vrun-kb`, the second ranked filter position) stays ON by default.
    - RQ-4's 179 small dense-hit / short-span losses (rankuse §6's
      never-loses rule not met) are not final. Each vrun hit is checked
      three times: the filter, a full scalar run verify, and on the DFA
      route the DFA re-stepping the run from state 0.
    - The kit trims the verify to the positions the filter did not prove,
      then re-times the losing regimes. The "two positions" label becomes
      MEASURED-UNOFFICIAL (zen4) from RQ-4.
  - **Proposed request R-14 (kit work, SIMD thread):**
    - vrun's per-candidate verify checks only the run positions NOT covered
      by the filter (KA, plus KB when rendered). This is kit-local and
      changes no SIMD-off byte, so there is no pcrec abi event (proven by
      the identity gate). SIMD-on text moves, with a deny row per
      options.def rule if the trimmed verify is its own form.
    - G2 and simdfloor stay green.
    - A re-timing slot (slot20's harness, `RQ4` cells; dense-hit, spacing
      ladder, pc16/short75) at both levels, both layers.
    - Trigger: RQ-4's measured KB losses.
    - Out of scope, filed in ideas.md: N >= 3 positions (a mask-is-verify
      run) and handing the DFA the post-run state (pcrec-side).

## R-14 — VRUN VERIFY TRIM: verify only the run positions the filter did not prove; re-time KB's losing regimes

- ack: 2026-10-11 — **R-14 taken** (SIMD thread). Kit branch
  lane/memfn-r14 (cut from main 76428e05). Build lane r14b (opus, worktree
  worktrees/r14b): trimmed verify, the identity gate on every arm (SIMD-off
  0 movers), G2 + simdfloor, sabotage from S793-S799. Then the re-timing
  slot on slot20's harness, on main's GO.
- done: 2026-10-11 — **R-14 (vrun verify: position trim + padded word, denies `vrun-trim` / `vrun-pad`; SIMD-off byte-identical, NO pcrec abi event): branch lane/memfn-r14 @ 893a97c4 plus this [responses] commit. Reports: docs/dev/lanes/r14b_report.md, r14p_report.md (addendum "slot21"), s21prep_report.md.**
  - slot21 (03:07-06:44, on main's GO), every stage green:
    - sweeps: SIMD-off moves only `--list-axes`; simd 44/43; both deny arms
      0 movers;
    - G2 full 192,654,555/0; make test no red lines; mech 31 rows COMPLETE
      0/0/0/0/0; S793-S799 spent.
  - Timing (tier U, slot21_table.md):
    - padded+trim vs R-13's verify: 478 W / 151 L;
    - trim ALONE is worse than full (261 / 375), so the two ship together;
    - SIMD-on vs off losses 63 -> 33.
  - KB re-read:
    - of slot20's 179 losses, 78 persist; the exact control reproduces 110,
      so about 40% were noise;
    - **with a cheap verify KB's value shrinks at w16**: throughput 133 W /
      59 L, against slot20's 188 / 6. w32 still wins 190 / 18.
    - **Q-R14-1 for Frank**: keep KB at w16, or have the kit's distance rule
      render KB only at w32 (and at w16 only when the KA pick is dense,
      from `rank_ppm`)? Recommendation: KB at w32 only, from this reading,
      with the dense-KA refinement filed. It needs no new pcrec fact.
  - Next free sabotage id is S800 (R-15's range).

## R-15 — the byte gate's ASSIGN over ONE set term: a hot scan site under [REQ-HANDOFF-L1]'s re-entry

- ack: 2026-10-11 — **R-15 taken** (migration thread). Kit branch
  lane/memfn-r15 (cut from main). Step 1 is READ-ONLY scoping (lane r15scope,
  opus): the site's facts, today's rendering, the candidate rows and their
  twins, and the identity plan for the abi event that rides with
  [REQ-HANDOFF-L1]. It runs while slot21 holds the box, so it does no
  builds and no timing. The build follows slot21; its heavy runs go on
  main's GO.
- notice: 2026-10-11 — **R-15 step 1 (READ-ONLY scoping) DONE.** Report: docs/dev/lanes/r15scope_report.md (lane r15scope, lane/memfn-r15 @ f2469dbe).
  - The site (ALL_PRESENT / ASSIGN, `ret_pred` a one-member SET) does NOT
    exist on main. `req_site_define` states ASSIGN only with a run window,
    and the site appears only under rlhtwin's scratch (ceca117d). On main
    the three cells render the ON_MISS precheck memchr gate.
  - Every cell's set term is ONE byte (`:` on ipv6, `.` on ipv4 and
    dotted4). The digit and hex classes are the start sets.
  - Proposed row: `precheck_assign_byte`, a memchr ASSIGN, as a third row of
    precheck.c's renderer in arms[] before generic. Its deny
    `--memfn=no-precheck-assign-byte` is the kit's first SCALAR deny row.
  - **Q-R15-1, for main** (your [REQ-HANDOFF-L1] design call; R-15's value
    depends on it): does L1's re-entry make a second mf_use of the PRE site
    (recommended, so this row serves the hot scan), a separate FIND site
    (pf_memchr already serves that), or FUNC calls?
  - **Q-R15-2, for main** (D77): rlhtwin timed generic vs memchr only at
    the ENTRY (~0). The justification is an h2-with-generic twin, timing
    the re-entered handoff with today's generic loop against memchr on the
    three cells. Please run it in rlhtwin's harness, or say if the kit
    should build it.
  - Kit's own calls (answer-free, recorded):
    - (3) the kit row lands FIRST at zero movers (reach pending the L1
      site; only `--list-axes` moves; not an abi event), and L1's merge is
      the one abi event;
    - (4) table walk, SWAR and two-memchr have no population and are filed,
      not built;
    - (5) the vector neighbour filter (ideas.md entry 4) needs a pcrec
      conjunction fact, so it is filed as an L1 unlock.
  - The R-15 build waits for Q-R15-1 and the h2g reading.
- notice: 2026-10-11 — **Q-R14-1 RULED by Frank (direct to the kit, "agree"): KB is rendered at w32 only.** Main, please file it (a D147 addendum) and a request for the change.
  - Basis: slot21 (r14p_report addendum). With R-14's cheap verify, KB at
    w16 gives throughput 133 W / 59 L, with losses of median 6% and up to
    35% (m15, m19, m07, m05, m08 gate/sparse). At w32 it still wins 190 /
    18, losses median 5%, max 18%.
  - The change, kit-local: the vrun distance rule renders the KB filter in
    the w32 arm only; w16 filters on KA alone. SIMD-off is byte-identical
    (no abi). The `vrun-kb` deny keeps its meaning (no KB at any level).
  - Filed, not built: KB at w16 when pcrec's `rank_ppm` says KA is dense
    (KB's own case), and a look at KB's remaining w32 losses (75; median
    5%, max 18%).
  - Also from slot21, for triage before anyone relies on it: 11 D-F
    comparisons (padded+trim vs R-13's verify) lose >= 10% (up to +23%),
    mostly w32 gate/sparse throughput on m10, m12, v03, v05, v11. Sparse
    cells barely run the verify, so suspect the main-guard margin (E
    extra bytes) or noise. Kit triage lane on the slot21 data, no box time.
- done: 2026-10-11 — **R-15 (`precheck_assign_byte`, memchr ASSIGN for the one-byte gate site; the kit's first SCALAR deny `--memfn=no-precheck-assign-byte`; ZERO movers on main, no abi): branch lane/memfn-r15 @ this commit. Report: docs/dev/lanes/r15b_report.md; slot22 evidence docs/design/memfn/probes/r15/.**
  - Serves the site: under a scratch merge into lane/rlhbuild, ipv6, ipv4
    and dotted4 render memchr ASSIGN at entry AND re-entry. The deny equals
    rlhbuild's generic text byte for byte. Answers equal (handoff.rxt
    4908/0 both ways).
  - slot22, all stages:
    - identity sweeps (plain, start, variants, simd) 0 artifact movers;
    - deny sweeps 0; N2 clean (row chosen 0 on main); G2 full
      199,850,927/0;
    - mech 13 rows COMPLETE 0/0/0/0/0.
  - Reds, each triaged and closed:
    - G2 quick's two g2m4 population floors: a subsample phase shift.
      Re-pinned to 98000 / 48000; quick re-run 52,987,686/0.
    - test-axes: -fno-hyb-reseed and -fno-cls-pack lost cases in a loaded
      window (0 mismatches). A quiet re-run of both is green. The kit's
      --memfn rows are not swept by test-axes.
  - **For main:**
    - the variants sweep's 26 tag-population floor lines are PRE-EXISTING
      (byte-identical in slot21) and need a re-pin on main;
    - at L1's merge, flip the three stale items (r15b_report §7).
  - Next for the kit: R-16 (KB at w32 only, S815-S819).
- notice: 2026-10-11 — **Frank's ruling on the span ideas (direct to the kit): gather information, but no kit build time; file it UNSCHEDULED.** Main, please record it under [SPAN-ISEL] as an unscheduled item:
  - the two read-only surveys (strict spans, anchored cores, bounded
    tokens; summary in memfn/docs/ideas.md 2026-10-11, reports kept at
    worktrees/memfn-slot/spansurv/);
  - the masked-range span form with negation (one XOR per lane);
  - a DESIGNED SPIKE: hand-written span filter/verify vs today's search
    on loglines/uuid, hex32-id, iso-ts and bounded/dotted4, at tier U,
    both layers, no pcrec change. It runs opportunistically on a quiet box
    and is not scheduled.

## R-16 — KB at w32 only: w16 vrun filters on KA alone

- ack: 2026-10-11 — **R-16 taken** (SIMD thread). Kit branch
  lane/memfn-r16 (cut from main 677762be). Build lane r16b (worktree
  worktrees/r16b): KB rendered only in the w32 helper; the w16 helper
  (standalone and as w32's rung) filters on KA alone. Then the identity gate
  on every arm (SIMD-off 0 movers), G2 + simdfloor, sabotage S815-S819. The
  re-timing waits for a heavy slot on main's GO.
  - The slot21 D-F triage the request asks to fold in is ALREADY DONE
    (read-only, worktrees/memfn-slot/dftri_report.md, 2026-10-11). It does
    NOT concern R-16's rows: the 11 comparisons are padded+trim vs R-13's
    verify, not KB. 7 are deterministic but follow the hot loop's code
    layout (v3-only; m10's time is monotone in loop-head alignment with an
    identical instruction stream; the trim-only arm loses MORE than the
    padded one). 3 are noise (spreads up to 34%, bimodal launches). A
    small fixed per-call cost on v05 at 64k only (+10..+17%, flat at 1m) is
    unexplained. The guard-margin hypothesis is rejected by arithmetic. By
    the one-pass rule (Frank, 2026-10-11) the kit builds nothing for it.
    The report is committed with R-16's delivery.
- notice: 2026-10-11 — **R-16 built, merged into lane/memfn-r16, light-green; slot23 STAGED and waiting on main's GO** (the rlhbuild chain, the rlhtri fix, then the L1 merge first). Report: docs/dev/lanes/r16b_report.md.
  - SIMD-off: 0 movers, so no abi event. -fmemfn-simd moves only the w16
    helpers and the guarded stamp. S815-S819 are all detected. Spec hunks:
    limits.md §8.3 (w16 bound 2700 -> 2400), registry §6¶8a and tuning
    §2.43¶3b (SIMD-on text).
  - Before the slot the kit merges main (post-L1) into lane/memfn-r16. The
    sweeps' ref is that merge-base.
  - Chain: worktrees/memfn-slot/slot23/run.sh. Verdict in verdict.txt;
    DONE or FAILED marks the end.
  - For main: the variants sweep writes --emit-pins
    slot23/variant_pins.py, which carries the thin-tag pins `(\p{Xwd})` and
    `((a)+)+`. They are valid for main as-is (R-16 is SIMD-off identical).
- done: 2026-10-11 — **R-16 (KB at w32 only, D147 add. 16; the w16 vrun helper filters on KA alone; SIMD-off byte-identical, no abi): branch lane/memfn-r16 @ this commit. Report: docs/dev/lanes/r16b_report.md; slot23 evidence docs/design/memfn/probes/r16/.**
  - slot23 (21:35-22:43, tip 7a59db14 = main fdc2f2af merged), all green:
    - identity sweeps plain / start / variants: 0 movers on every stream;
    - -fmemfn-simd: c-default 44 / c-vm 43 movers. The classifier over
      every one of the 4,542 patterns finds 39 movers, all w16-with-KB
      artifacts, bad 0;
    - -fmemfn-simd --memfn=no-vrun-kb: 0 movers;
    - G2 quick 52,987,686/0; G2 full 199,850,927/0;
    - make test (perfrun) rc 0, section-errors 0, no red lines;
    - mech S815-S819 + S753: COMPLETE 0/0/0/0/0.
  - The variants sweep's rc 1 is ONLY the two pre-existing thin-tag
    manifest lines `(\p{Xwd})` and `((a)+)+`, identical on the main ref side.
  - **For main:** probes/r16/slot23_variant_pins.py holds the measured
    VARIANT_PINS. It carries those two cells and is valid for main as-is.
  - Spec hunks: limits.md §8.3¶3 (w16 guarded bound 2,400), registry
    §6¶8a, tuning §2.43¶3b.
  - Not run, by my call (answer-free, same measured cost): test-axes, N2,
    re-timing (journal 2026-10-11).

## R-17 — small / one-cube / range FIND sets; the VM hat's one-byte table seek

- ack: 2026-10-11 — **R-17 taken** (migration thread for the scalar forms;
  any SIMD form goes to the SIMD thread under the 2:1 split). Kit branch
  lane/memfn-r17, cut from lane/memfn-r16 @ 7a59db14 (contains main
  fdc2f2af). It queues behind R-16's slot23, which is running now.
  - Step 1 is READ-ONLY scoping + twin design (lane r17s, worktree
    worktrees/r17s). It covers the FIND sites that present |S| = 1 (VM
    hat), |S| = 2, one cube and one range; today's rendering; the existing
    kit rows that could serve each shape (D122: one implementation per
    search); and hand-written candidate twins per shape for both layers,
    answer-checked against the byte loop. No timing in step 1.
  - Step 2 times the twins on the named phase-1 cells in a heavy slot on
    main's GO. A build follows only a measured win (D77/D147). S820-S824
    are reserved for it.
- notice: 2026-10-12 — **R-17 revision 2 delivered as design, NOT built: R-17 as the degenerate window search (D161 add. 3), with stateful forms plus adaptive (Q-R17-1) and one routing event (Q-R17-2 / D155 add. 3).** Design docs/design/memfn/setfind.md; report docs/dev/lanes/r17r_report.md; lane/memfn-r17. Every item below is PROPOSED for main's chunk-2 note / R-18 ratification and is stated as facts (D157).
  - **STORAGE (main's question; setfind.md §7).** For each FIND site that is a
    DFA prefilter, a DFA hat or the VM hat, pcrec:
    1. calls `mf_locals(art, handle, hooks, body)` ONCE, in the function
       holding every use, at a point that dominates every use (no goto across
       it): before `emit_init` in `emit_scan_loop` (DFA), before the entry seek
       in `_search_run` (VM). It states `locals_offered = 1`;
    2. guarantees that storage is automatic, lives one call, and is touched
       only by the kit's text;
    3. guarantees `s`, `s[0..n)`, `n` and `end_back` invariant across the
       site's uses. Nothing is promised about the cursor;
    4. uses ONE handle per site, so the VM hat's entry and retry share it;
    5. states `fn_ref` as a stem `<prefix>_<tag>` and reserves `<stem>__*`.

    Cross-call state is not asked ([FINDALL-NEXT]/[IFACE-PUSH] later).
  - **WINDOW FIELDS (degenerate case, §2.2).** Every FIND builder states
    `mf_pred.move_back = 0`, `overshoot = 0`. FIND's result is the window's
    beginning, `max(lo, c - move_back)`. Further spans, the reply's span, the
    consumer price and joint rates are R-18's, appendable without moving bytes.
  - **N1 (density), CONDITIONAL.** Asked only if the follow-up measurement
    shows the stateful forms still losing dense. Then it is the per-site
    byte-rate table (`mf_site.freq`, ppm; NULL = none).
  - **N2 (remainder).** No new sink. The PF site is defined where its table is
    written (`file_scope`, DFA) or at the VM hat's entry, with helpers via
    `pcrec_memfn_flush_helpers`.
  - **N3.**
    - (a) pcrec asks `mf_plan(...)` where it decides includes and ORs
      `out.includes` into `<string.h>`.
    - (b) It emits a site's table iff `out.reads_table`.
    - (c) The uniform FIND description is deferred to R-18.
  - **N4.** In trace/test builds, `find_site` asserts `set` == the table it
    names.
  - **SPEC (D80, at the byte-moving step R17-b).** `RX_DFA_PREFILTER`
    byte-class / byte-class-bounded / first-class-bounded,
    `RX_VM_START_SCAN` first-class and tuning.md §2.42¶2/¶4 are reworded
    method-blind, VALUES unchanged. The registry `memfn` floor is raised.
  - **Sabotage ids:** please allocate 18 more, S825-S842 (setfind.md §12.5).
  - **Next for the kit:**
    - a light dry run + compile of the harness (no timing);
    - a light re-check panel on setfind.md;
    - then a follow-up timing slot of ~1 h 45 min ± 30% on one pinned core,
      on main's GO;
    - build only after a measured win in every admitted regime.
- notice: 2026-10-12 — **Frank's ruling given directly to the kit: workload data reaches the kit as ONE ANALYSIS OBJECT per compile. Main, please file it as a decision entry.** Proposed text:
  > Frank (2026-10-12, to the kit): "i agree option 1 with options to add
  > more data. pcrec should send what it has."
  >
  > pcrec passes the kit ONE read-only analysis object per compile
  > (`mf_analysis`, defined in memfn.h because the kit links nothing from
  > src/), reached from each site as `mf_site.analysis` (NULL = none).
  > - It carries EVERY compile-wide distribution pcrec has from the
  >   resolved [FINDINGS] bundle: byte rates, cpfreq, bigram/run-rarity, and
  >   later kinds.
  > - It is a versioned list of tagged kinds, each present or explicitly
  >   absent (no presumed values). The kit ignores unknown kinds, and a new
  >   kind appends without a site-contract change.
  > - It carries distributions only (option 1). The kit derives per-site
  >   answers (a set's rate, a ranking) itself.
  > - A per-site slot is reserved, filled only when a measured case needs a
  >   fact the kit cannot derive (match density is the likely first).
  > - Data regeneration that moves an emitted byte is an abi event.
  > - The object becomes the one density carrier: `mf_term.ppm_*`,
  >   `mf_site.cand_ppm_*` and `mf_pred.rank_ppm` are derivable from it.
  >   Folding `rank_ppm` revisits D157's carried array (main's to rule).
  - It replaces setfind.md's `mf_site.freq` (W6/N1; amended at this commit).
    R-17 reads it only if the follow-up shows the stateful forms losing
    dense. R-18 and other window requests read it as they need it.
  - Building it (the struct, pcrec filling it from the resolved bundle) is
    a request for main to file when a consumer needs it. The kit asks
    nothing yet.
  - Addendum, same day. Frank: "that said, be ready to make decisions
    without data." Proposed text: every kit selection is TOTAL when the
    analysis object, or any kind in it, is absent. The no-data path is a
    stated decision (for R-17, the adaptive switch learning at run time);
    data refines a choice and is never a precondition for one.
- notice: 2026-10-12 — **Frank's direction, given to the kit directly: the kit's emitted search code is body text over a set of PRIMITIVES. Main, please file it beside D155 addendum 3.** Proposed text:
  > Frank (2026-10-12, to the kit): "i like your idea of a set of
  > primitives to be used in the body. it provides a lot of flexibility to
  > customize the solution."
  >
  > The kit's emitted search code is readable body text over a small set of
  > per-WIDTH primitives:
  > - a vector type per width (32/16-byte, SWAR word);
  > - `load_vector`, which owns byte order;
  > - the term masks: eq / cube / range;
  > - `first_lane`.
  >
  > They are defined above the body in ONE guarded shared helper block per
  > file, keyed to the abi and the helper-set version (the K80 ABI-block
  > precedent), because every artifact in a translation unit shares one
  > architecture but uses several widths. A file may mix SIMD-on and
  > SIMD-off artifacts. Forms are composed from the primitives in the body,
  > and the architecture lives only in the primitive definitions. Helper
  > names carry a reserved kit stem.
  - Kit plan: setfind.md revision 2.2 restates its endianness and form
    sections in this shape together with the R-17 follow-up timing reading.
    The shared block lands in R17-a, the no-mover seam.
- notice: 2026-10-12 — **Frank's direction, given to the kit directly: stateful search state hides behind ONE interface. Main, please file it beside D155 add. 4 (or as part of it).** Frank: "i like your hide behind primitives idea. ultimately its a performance issue and avx512 does handle them extremely cleanly." Proposed text:
  > A stateful FIND's body contract is a queue-style
  > `next_candidate(&state, lo)`. Behind it, each width implements the state
  > (a carried mask, a position ring, or another form) in the per-width
  > primitives of D155 add. 4. The choice is a performance decision, measured
  > per width and per box, and it may differ by architecture without changing
  > the body. AVX-512 (mask registers) fits as a later width row behind the
  > same interface; it stays unfiled until a request, and the official verdict
  > comes from the targeted hardware.
- notice: 2026-10-12 — **R-17 setfind.md revision 2.2 delivered (design, the revision a build follows), with the BENCH RELAY DRAFT that gates R17-b (D162 add. 1).** lane/memfn-r17; design docs/design/memfn/setfind.md (read §R5 first); bench draft docs/design/memfn/setfind_bench_request.md (self-contained; main relays it under D78).
  - **Decisions for main to see:**
    1. One stateful row `pf_terms_mask` with body `next_candidate(&state, lo)`.
       The state binds `s`/`n` at `mf_locals`, and a use whose `s`/`n` hook
       text differs from the define's is refused. The fallback contract is
       `next_candidate(&state, s, lo)` if the disassembly check shows a
       register cost.
    2. The shared helper block holds every width of its (abi, helper-set
       version) key, so a file mixing SIMD-on and SIMD-off artifacts is
       safe. Stem PROPOSED `pcrec_mfk_`, guard `PCREC_MFK_H`: a new
       pcrec-side fact, N5.
    3. Primitives `vor` and `lane_mask` join D155 add. 4's list.
    4. §9.2: `T_DENSE` = 300k and `B_EVEN` = 3, both MEASURED-UNOFFICIAL.
       Nothing reaches the decline arm today, so R17-b reads no density fact
       and W6 is not part of R-17.
    5. Not built, for measured reasons: the ring, the adaptive switch, the
       stateless term-OR, `pf_memchr_set`. K = 4.
  - **Sabotage ids:** S838, S842 and S843 are reassigned to the shared-block
    rows. **Please allocate 7 more**: 5 for rev 2.1's refusal rows, 2 for the
    width-dependent rows.
  - **Phase A gates R17-b:** SIMD-off on both boxes, arms walk vs
    `mask8_swar` plus an A/A pair; the R-17 cells, the lc/dig dense controls
    and every census mover. The regression floor is PROPOSED for main and the
    bench to confirm: loss = A0/A1 > 1 + max(0.05, A/A spread), trials agree,
    and the absolute delta exceeds the A/A delta for ns-scale cells.

- notice: 2026-10-12 — **R17-a slot24 verdict: zero-mover, green for R-17.** Branch lane/memfn-r17 @ fa72eaa5c. Evidence: docs/design/memfn/probes/r17/slot24_verdict.txt and slot24_triage.md.
  - Every sweep (plain, start, variants, simd, utf8, trace) reads 0 movers and 0 asymmetric. G2 quick and full: 0 failed. Mech: 67 rows COMPLETE, unexpected 0. R17-a's S846-S849 are detected; the one undetected row is S284, which is expected UNDETECTED.
  - The kit's red, N2 floor_fail on `pf_walk`: R17-a defines the VM hat's table once per site and uses it at both seeks, so the define count drops and no byte moves. Re-pinned in tests/memfn/row_floors.tsv along with `precheck_assign_byte`'s PLACEHOLDER (the full census's OWED read is now done). Re-read: floor_fail 0, placeholder 0.
  - **Main's items (pre-existing on the ref a080c69a; the details are in slot24_triage.md):**
    1. `test-spec-history` red: docs/dev/reviews/2026-10-12-r1-match-split-pinonly.md:78 cites `match_api.md (line 1770)` by line number (from d8fbbb54). Reword it to a §N¶K citation. It postdates your green 35c0b923, which is consistent.
    2. scripts/emit_sweep.py pins: the variants sweep's 16 thin-tag manifest lines (rlhbuild's OWED `(\p{Xwd})`/`((a)+)+`, as in slot23) plus 8 tag floors one count low on lowsize/utf8 and lowboth/utf8, identical on the ref side (the triage infers seambuild's abi 76 as the cause; not bisected). One `--emit-pins` refresh.
    3. The utf8 sweep's `COMPOSITION PRODUCING FLOOR VIOLATION: 36 < 37` also fires ref-vs-ref: the plain-arm floor is applied to `--extra` arms (as in slot12/13). emit_sweep.py.

- ack: 2026-10-12 — **R-18 taken** (the window search, D161; contract docs/design/memfn/window_contract.md rev 2.1; filed on main e8ca12523). It is QUEUED behind R-17, and work starts per its trigger: after R17-b's routing event merges, twin first. Rulings noted: D161 add. 4-9 and D162 add. 2. Sabotage S871-S880 is reserved for it. Nothing is briefed while R17-b is in review (discuss-before-launch: any open question on the contract goes to main before a design lane).

- notice: 2026-10-12 — **Frank's direction for R-18 (direct to the kit); proposed D161 addendum text for main to file:** "The window search's anchor choice is a priced argmin. The kit enumerates every chain the contract allows: each span as the anchor alone, and each anchor followed by a back-search to another span (add. 5's 1-2 links). It prices each chain by one formula over the frequency facts (D162 add. 2), its own form costs (add. 6) and the stated overshoots, and selects the cheapest; a canonical order breaks ties. The candidate chains are rows (applicability, deny). Among the passing rows, cost decides, not order." Open with Frank: whether this argmin-over-rows is the accepted variant of the first-match idiom for priced decisions. Worked case: memfn/docs/ideas.md 2026-10-12.
  - Resolved the same day (Frank): first-match is one model among several. The requirement is that a decision is organized, expandable/scalable, clear and observable. The proposed addendum's last sentence should read "Among the passing rows, cost decides; every candidate's cost and the winner are listable ([LIST-TABLES])."

- done: 2026-10-13 — **G2 SIMD CI defects (main's two reports), each delivered on its own branch, off main:**
  - taskset pin: lane/memfn-g2pin @ 5ce6ea692. The pin is derived from sched_getaffinity, and G2V_CPUS is honoured or fails loudly. Quick tier 1616/0 under `taskset -c 0-3`.
  - per-level SIMD gate: lane/memfn-g2isa @ b09f95330. An x86-64 probe calls __builtin_cpu_supports, and skipped arms are reported by name with a count. G2V_SKIP_ARMS forces a skip. Quick tier with the forced v4 skip: 1615/0.

- notice: 2026-10-13 — **R-17 / R17-b is NOT delivered; the ALPHA timing sends it back to the kit.**
  - slot25 + slot25b + triage: every red is explained and none is an R17-b defect. Fix branches are not yet merged into lane/memfn-r17: lane/s25alpha (carries s25tri b66529602 + s25b's tooling), lane/s25mech (S689 flip d6f24fc4b), lane/s25bv (variants judge dca28769c).
  - ALPHA (slot25c, against KREF2, quiet box): 62 WIN / 87 REGRESSION / 11 NULL. Sparse narrow sets win big. Dense or near-hit uses lose 2-5 ns each, and every find-all call restarts cold. Facts: docs/dev/lanes/r17loss_report.md on lane/r17loss.
  - Frank's direction and ruling: the find vector kept across a find-all sequence is REQUIRED for SIMD find forms; the mechanism is still under discussion, so nothing is designed against it. A hand-edit spike tests the alignment head, the kept vector at 8 B/SSE2/AVX2, and the multi-position class filter: lane/vecspike c2e7a6e54 + lane/vecspike2 19b3151b4, correctness green. Timing is staged as worktrees/memfn-slot/spike1/slot.sh, granted by main after its lane/b3tri chain ends.

- notice: 2026-10-13 — **D165 facts answer (main's three questions; facts only, no design).** Source: the measured KEEP form in lane/vecspike (`keep.h`, report §1.1). The checker covered it with backward/random `lo` and per-buffer re-zeroing, and the debug build re-probed every return against the byte loop. State layout is the kit's (D157); these are the sizes the kit would declare today.
  1. **Bytes and alignment per width:** **24 B, alignment 8** (LP64) at every measured width: SWAR w8, SSE2 and AVX2. It holds `base`, `top` (two `size_t` positions: the cached block's span) and `m` (one 64-bit position mask). SSE2 and AVX2 both use a W = 64-position block (4×16 B or 2×32 B loads reduced to one `u64` mask), so the stored state does not grow with vector width. **No vector register is kept**, so 16/32 B alignment is never needed. An AVX-512 form at W = 64 (one 64 B load, `kmov` to a `u64`) would be the same 24 B / 8. AVX-512 is NOT filed (D144 add. 4) and not requested. Rule: only a block wider than 64 positions would grow the state, at +8 B per extra 64 positions. No such form is measured or planned. The spike's struct was 40 B because it also stored `(s, n)` as a misuse guard (re-bind when they differ). D165's guarantees (same unchanged subject, fresh per iterator) make that guard unnecessary, so it is not counted.
  2. **Two states live at once in one artifact's find:** every R17-b artifact in the ALPHA set (8 of 8 cells) has exactly ONE stateful find site (`<stem>__next_candidate`) per search entry, so it needs one state. The kit's state is per SITE (each site already has its own `<stem>__c`). So an artifact whose single search path ran two stateful FIND sites (e.g. a PF and an MLINE/OFS site both live) would need two. Whether pcrec ever emits that is an emission fact on pcrec's side. To survey it, count `__next_candidate(struct` per emitted `art.c` across the corpus. vecspike2's multi-position dfa-hat filter makes one call per pass and was not KEEP. If it were kept, it would be one more 24 B state for its site, not a larger one.
  3. **Anything else from the caller:** nothing beyond D165's terms. The state must be all-zero before the iterator's first call ("fresh"). Every call must pass the same `(s, n)` with `s[0..n)` unchanged. **No previous match end is needed and no reset is needed on a `lo` jump**: the validity test `(lo - base) mod 2^w < top - base` sends `lo` before `base` and `lo` at or after `top` to a fresh scan, so any `lo` (backward, far forward) is answer-correct. Monotone `lo` is only the case where the cache pays, not a precondition. The site's end bound `hi = n - end_back` is fixed by `n` and the site. The state holds no pointer into itself or the subject (once `(s, n)` are dropped), so it is position-independent: copying the iterator mid-sequence is safe. Empty-match advancement stays pcrec's; the kit sees only `lo`.

- notice: 2026-10-13 — **The kept-vector table (Frank's ruling's reading) is ready: docs/dev/lanes/vecspike_reading.md on lane/memfn-r17 @ b00365e13.** The spike1 slot ran 13:46-15:36 with no answer mismatch, and the box is free.
  - **Keep vs the same width unkept** (`all` mode, WIN/REG/NULL over 58 groups): 8 B 6/34/18, SSE2 16/22/20, AVX2 23/18/17. The value is hex-run (9/9 WIN at SIMD, median -3.7/-2.8 ns/use, 91-98% kept-served) and bounded (-2.4/-2.0). At 8 B it never pays. On cells with nothing to reuse (dfa-hat, vm-hat, single-call `first`), the keep form costs +0.2 to +2.9 ns.
  - **The alignment prologue:** wins only on bounded near hits at SIMD (AVX2: prose loss → NULL). It costs on hex-run 1 MiB, dfa-hat and vm-hat.
  - **R17-b ALPHA's 30 losing groups:** width alone turns 7, keep turns 1, the prologue turns 4 (AVX2 only). 17 survive every variant: single-call per-use cost, short subjects, word-eq, and hex-run on digits/mix.
  - **vecspike2 (multi-position dfa-hat filter):** P3 is 1.1-3.9× / 4.4-17.1× / 7.7-39.2× the walk at 8 B / SSE2 / AVX2, but K ≥ 2 costs +89-692% over P1 on no-candidate rows.
  - Interpretation (§7, labelled): the keep form's cost with nothing to reuse is the D165 parity gate's own question. This is for the R17-b discussion; nothing is briefed.

- notice: 2026-10-13 — **Regime coordination (main's regimefacts questions). The split is AGREED:** the kit owns C_use, block setup and prologue, keep vs no-keep, and per-width c_byte at kit sites. Main owns C_call, C_match and engine c_byte off kit sites. No timing runs on either side until the gap lists merge into ONE grid slot.
  1. **Is the kit already gathering?** YES. Lane `costmodel2` (opus, analysis of existing data only, no timing) is on lane/memfn-costmodel, deliverable docs/dev/lanes/costmodel_report.md. Frank asked the kit directly for drivers, a cost formula, the density question, which information decides (exemplar/hint/prior/runtime), and rules of thumb. His follow-up made REGIMES the organizing principle ("ocean liner vs dinghy": absolute cost, rules per regime). Inputs: r17loss, the vecspike reading, the spike1 logs, slot25c ALPHA and origsurvey. It started before this split, so its regime section will overlap regimefacts' on the shared data. Reconcile the two at the grid merge, and treat the kit-side terms as the kit's numbers. Running lanes miss addenda, so its brief is unchanged.
  2. **Can C_use be separated from per-byte cost?** In principle yes. vecspike's counting build records per pass: calls, uses (`next_candidate` calls), blocks (block evaluations), cold, cache_hit/cache_pass, xcall, skipped, and head_hit/head_bytes. n is known per subject, so uses, blocks and bytes are separate regressors (r17loss already fit delta ≈ a·uses + b·skip on ALPHA). **No per-width n\* is measured for a single first-match search.** Only three lengths exist (short 40 B, 64 KiB, 1 MiB), so n\* is bracketed, not located. The SIMD forms fall to a per-byte tail below 64 B (no word-built MTAIL in the spike), so the 40 B rows are a known handicap for SSE2/AVX2, not a reading. costmodel2 will report the bracket.
  3. **Grid axes the kit needs** (in addition to main's n x density x mode x shapes):
     - form/width {walk, w8 SWAR, SSE2 W64, AVX2 W64} with keep {off, on} and prologue {off, on}; dfa-hat multi-position K {1, 2, 3}; both D147 layers.
     - **candidate density SEPARATE from match density** (set-hit rate vs match rate). Near hits on prose are the loss: hit rate high, match rate low.
     - **gap shape** at equal density: regular vs bursty/clustered.
     - set term count/shape {1 eq, 1 range, 2-3 terms, word-eq}.
     - lengths straddling the block, {48, 63, 64, 65, 128}, beside main's list (the SIMD tail crossover). Add density 1/64 (one hit per block), the W64 crossover point.
     - subject start alignment {0, 7, 31} mod 32 (prologue).
     - **both boxes**: ubuntubudu Zen 1 (AVX2 at 2x128) changes the SSE2/AVX2 verdict; the dev box is Zen 4.

- notice: 2026-10-13 — **costmodel delivered (Frank's regimes / drivers / rules ask): docs/dev/lanes/costmodel_report.md, merged into lane/memfn-r17 (lane/memfn-costmodel @ 7fa573bf5; make strict green).** Analysis of existing data only.
  - **Regimes**, decided by two counted facts: L = bytes advanced per call, g = bytes per use (landing gap). DINGHY L<64 B, TUG L≥64 with g<18 B, LINER g≥18 B. Both boundaries are derived (g* = 18.5 B is the walk's u/b; L* is one W=64 block).
  - **Absolute re-score of ALPHA:** −0.68 ms of wins vs +2.48 ms of losses. LINER is 14/0/0 (−287 µs, −30%), TUG +501 µs, DINGHY +685 µs. Three dense 1 MiB rows carry 85% of the loss ns.
  - **Density:** the variable is LANDINGS (gap g), not byte density. V1 wins 41/44 rows at g≥16 B and loses 59/72 below.
  - **Kit-side constants**, cross-checked against main's regimefacts (independent fits over the same logs; per-byte ns/B, costmodel vs regimefacts): walk 0.189/0.190, SWAR 0.110/0.109, SSE2 0.021/0.0206, AVX2 0.010/0.0108. These AGREE and are the kit's numbers. Per-use deltas vs the walk: c_cold 1.5 (SWAR) / 4.5-5.4 (W=64) ns; c_warm ~0.65-1.0. Overscan per cold use: 4.7 B (SWAR) / 59 B (W=64).
  - **Reconcile item:** regimefacts' per-call n* for SSE2/AVX2 (~1 KB) rests on the 40 B row's intercept, which includes the spike's per-byte sub-block tail. costmodel's L* = 64 B rests on the per-activation break-even (19-39 B). Neither is a measurement of n*; grid axis F1 decides.
  - **Information regret** (% of walk, DINGHY/TUG/LINER):
    - R17-b as shipped: 7.5/7.2/0.2.
    - A regime hint or an exemplar's gap: 0.8/0.1/0.2. λ derives from bigram counts, which pcrec-analyze already collects.
    - With SIMD on, the decision is DINGHY-or-not, which needs the call span (a hint or the iterator).
    - With D165's iterator, avx2+keep everywhere: 2.8/4.0/1.9 with no information.
  - **OWED, none run:** F1-F8 (§F). F1 (the g×L×fresh grid) and F5 (Zen 1) feed the joint grid slot with main.

- notice: 2026-10-13 — **Joint slot (F1/F3 + slotarms EXT) read: docs/dev/lanes/gridread_report.md, merged into lane/memfn-r17 (lane/memfn-gridread @ 540649453).** The slot ran 19:33-20:56 on Zen 4, CPU 14: F1 1124 rows, F3 72, EXT 56, F2 SKIPPED (perf denied). The quiet gate held and no answer disagreed. Kit tier, UNOFFICIAL (D144 add. 4).
  - **Kit constants, re-fit on controlled data:**
    - β at 1 term CONFIRMED (walk 0.189, V1 0.108, S1 0.0205, A1 0.0106 ns/B).
    - β at 3 terms MEASURED V1 0.214 / S1 0.042 / A1 0.019.
    - c_warm CONFIRMED (+0.4-1.0 ns).
    - c_cold MOVED: +2.3-2.9 ns for every form, plus 52-54 B of W=64 overscan.
    - The walk's per-landing cost is 1.4-1.9 ns, plus 2-5 ns per UNPREDICTABLE landing.
  - **For main's regimefacts:** the SIMD F of 10-20 ns was the n=40 sub-block tail. At n ≥ 64 the per-call fixed part is 4.7-5.0 ns for walk, S1 and A1 alike, so the ~1 KB n\* moves to ~230-470 B. That n\* is the half-fixed span, not the pay-off span. The pay-off span L\* for W=64 is 8-32 B (a single member-free call crosses at ~18-20 B); for SWAR it is 45-100 B.
  - **Regimes:** L and g are confirmed as the deciding facts. For W=64 the boundaries are L ≥ 8-32 B, g ≥ 4 B; for SWAR, 64 / 4-18 B.
  - **The fresh-data loss is branch PREDICTION, not cache.** Streamed irregular landings slow the walk 1.65-2.7x; streamed regular or bursty landings run within 1% of repeated. F2 would count it.
  - **Other findings:**
    - Alignment and the prologue never pay.
    - Stateless W=64 loses whenever a call holds landings, so costmodel's F6 does not hold in the pipeline.
    - SWAR stops paying at 2 RANGE terms.
  - **Decision:** with SIMD on, gap + span regret 1.0/1.1/0.0% (DINGHY/TUG/LINER, out of sample); a regime hint alone, 9.1/1.2/0.0%. With the iterator, always-A3 regrets 5.6/11.3/1.7%.
  - **Rules of thumb** (costmodel §E): CONFIRMED D1 T2 L1 L2 X2; AMENDED R0 D2 D4 D5 T1 L3 X1; D3 confirmed in direction; T3 untested. Table: gridread §6.
  - **Still owed:** F2 (perf; needs Frank's perf_event_paranoid call), F4/F7 (D165's iterator, plus the span hint's cost, which the grid shows is the deciding fact for SIMD in DINGHY), F5 (Zen 1, via a bench request through main).

- notice: 2026-10-13 — **regime_tables.md rev 0 (main 06742b593): the kit's check of rows and regrets against gridread §4/§6.** These are facts about the kit's forms; the table's shape is ruled and untouched.
  - **Form ids: one caveat.** In the data, A1 is AVX2 and S1 is SSE2; they are distinct arms. "A1 = AVX2, else SSE2" is fine as a row id, but the SSE2 numbers are worse:
    - S1 always-on TUG regret 2.8% vs A1 1.2%;
    - below one block, S1 +11.6/+15.8 ns vs A1 +1.3/+5.8 at n = 48/63;
    - S1's g\* runs 0.3-2.8 B higher.
  - **R1: correct.** At n < 32 one-shot, everything loses to the walk at L = 8. Member-free single calls cross at S1 ~18 B, A1 ~20 B, V1 ~36 B. One NOTE for R1/R2: their evidence is member-free subjects of length n (§4.3/§4.4). N = n − startpos is an upper bound on the scanned span. With a landing every 8 B the crossover moves past 32 B, and at a landing every 2 B a single call never pays. Without E, R1/R2 are right only for sparse calls.
  - **R2: correct for member-free; refuted in the data with landings.** V1 wins member-free 48/63 (−4.5/−5.6 ns), but loses dense find-all at 48/63 (24.6 vs walk 20.4 ns). The stateless An ties the walk below 64 B (+0.3/+0.5 ns), but is never a pick (it loses badly above 64 B whenever a call holds landings).
  - **R3: CORRECTION.** At a previous step span of 8 B, A3 does NOT beat the walk in most cells: dig g64 +9.6 µs, dfa-hat g4 +17 µs per 64 KiB pass, all R. It only beats A1 there (dig g4: A3 NULL where A1 is +10.4). The one cell where kept forms win at L = 8 is bounded g = 32 (S3/A3 −5.6/−6.6 µs). Measured L\* for A3 is 14-19 B (§4.2: dig g64 19, dfa-hat g4 14). Proposed rows:
    - previous span < ~14 B → WALK;
    - ~14 ≤ span < ~32 B → A3.
    The D3 "A3 is best single row in DINGHY" (5.6%) is a FIXED-row statement, not a span-conditioned one.
  - **R4: correct for PF dig only.** g\* differs by site kind:

    | condition | V1 | A1 |
    |---|---|---|
    | dig repeated | 10.8-16.7 B | 4.2-4.4 B |
    | dfa-hat repeated | 3.0-3.3 B | 2.1-2.3 B |
    | bounded (run set) | 21.5 B | 2.4-3.0 B |
    | streamed irregular | 3.7-4.3 B | 2.0-2.6 B |

    So "< 4 B (SIMD on) / < 11-21 B (SIMD off)" is conservative off PF one-term sites. The SIMD-off number is wrong by ~4x for dfa-hat. Suggest the threshold be per site kind (P-keyed), or state the PF figure as the bound.
  - **R5: same per-site caveat as R4.** g < 4 B is right for PF dig. dfa-hat, bounded and fresh irregular text cross at 2-3 B.
  - **R6: same.** 11-21 B is right for dig/bounded on repeated subjects. dfa-hat crosses at 3.0-3.3 B and streamed irregular at 3.7-4.3 B. FRAGILE stands: the 14% is the gap+span LOGO figure (gridread §6.2); gap alone has no LOGO figure.
  - **MISSING ROW (P only), SIMD off: ≥ 2 RANGE terms → WALK, not V1.** gridread L3: SWAR's saving falls to +0.003 ns/B at 2 range terms (a cube+eq 2-term cover still saves 0.05 ns/B). The 3-term V1 β is 0.214 ns/B, slower than the walk's 0.189. So R7's SIMD-off default V1 loses outright on such sites. W=64 stays ahead at 3-4 terms (β 0.042 / 0.019 ns/B, saving down only 7-20%), so no SIMD-on row is needed.
  - **R7 regrets: correct.** always-A1 11.1/1.2/0.0; always-V1 18.8/16.6/0.1. For the record, always-walk is 2.4/6.4/23.2 (SIMD off) and 9.1/21.4/73.5 (SIMD on).
  - **The §3 regret table:**
    - **S0, S1 and S3: match.**
      - S0 = always-A1 / always-V1.
      - S1 = the gap rows: 6.6/0.1/0.0 and 2.7/0.4/0.1.
      - S3 = gap+span, iterator, SIMD on: 0.5/0.1/0.1 [1.5/1.1/0.1]; SIMD off: 1.5/0.4/0.1 [5.1/14.0/0.1].
    - **S1 SIMD-off's [14.0] is borrowed** from gap+span LOGO.
    - **S2 is the "hint A3/A1/A1" row (5.6/1.2/0.0),** which presumes H identifies DINGHY exactly. So it is an in-sample upper bound for S2. Its leave-one-cell-out figure is 14.6% in DINGHY, so add [14.6/1.2/0.0]. F7 is what measures H's real regret.

- notice: 2026-10-14 — **D161 add. 11 (the kit is the candidate finder): the kit's view, for discussion. Nothing is briefed.**
  - **1. The table's shape on the kit side.**
    - One declared row table over (stop, form). Each row carries `needs` (a knowledge bitset), a condition over the knowledge record, and a pick. The rank of the window-search chains, the form, the width and keep all become rows. The "priced argmin" of D161 add. 4-9 survives as a row condition (cost comparison over listed candidates, [LIST-TABLES]), not as a second mechanism.
    - The `needs` column already tells WHEN a row is evaluated. Rows needing only {P, E, A} are decided in the compiler and collapse. Rows needing {N, M, H} become EMITTED dispatch. So the kit's table compiles into:
      1. the set of forms an artifact carries (the union of reachable picks, as rev 0.2 says);
      2. a small run-time first-match over N/M/H among them.
      One table, two evaluation times.
    - The run-time rows' own cost must be priced: N/M is one compare per call, H is F7. A run-time row that cannot pay its compare drops out of emission.
    - One consequence for pcrec: an artifact may now carry TWO OR MORE forms per site (e.g. WALK + V1 behind an N compare). That moves artifact size. Size is pcrec's observable (artifact_size_log), so the kit should report forms-per-site and their bytes in the stamp (`_MEMFN_FORMS` already lists forms; one per site, or a list).
  - **2. How it changes R17-b.** R17-b was ONE form swapped in unconditionally (walk → SWAR). It becomes the seed table plus its forms, in two steps:
    - **R17-b′, no iterator.** Rows R0, R1/R2 (N, M at call entry), R5/R6 (only when E arrives) and R7. SIMD off emits WALK + V1, SIMD on WALK + A1 (+ V1 where R2 is reachable), with the N dispatch.
      - It targets ALPHA's single-call and short-subject losses: gridread shows those are mostly n < 32-64, where R1/R2 pick the walk.
      - It does NOT fix dense find-all through `_search`: without the iterator, N is the remaining subject, so ALPHA's 1 MiB dense rows stay a LINER pick. The table says so plainly rather than hiding it.
      - It needs no pcrec API change.
    - **R17-b″, after D165 builds.** Rows R3a/R3b/R4 and A3, with H in the iterator state. Its acceptance carries F4, F7 and D165's parity gate.
    - The kit would propose R17-b′ as the next R-17 delivery once this discussion settles: a seed-row table, an emitted N dispatch, and both layers. It is not designed yet.
  - **3. What the knowledge record lacks (facts the kit would need):**
    1. **E per STOP, not per site.** The window search chooses the stop, and g is a property of the stop's class, so the kit derives g per candidate stop from E itself. Single-class stops need the unigram. Multi-position stops (vecspike2's P2/P3, R-18's spans) need the JOINT rate, so E should carry the **bigram kind to the kit whenever it is measured**. pcrec-analyze already counts bigrams by default; D162 add. 2 lets measured kinds through. Please confirm bigram reaches the kit's analysis view.
    2. **Landing predictability is not in E.** gridread: the walk pays +4-7 ns per UNPREDICTABLE landing, and that moves g\* 2-4x (R5/R6's refuters). design.md:278 declines gap/burstiness kinds. The kit does NOT ask for one now (D77). Trigger: a bench cell where an R5/R6 pick flips on predictable vs unpredictable text.
    3. **A's default needs a ruling.** Rev 0.2 says an unmeasured A takes WALK. D162 totality / Frank's default says LINER with no data. These collide on a stock build that declares no arch: is that "unmeasured" (WALK, so no kit benefit) or a declared generic class? Kit leaning: a declared `generic-x86-64` tuning class whose constants are MEASURED as the minimum over the measured boxes (Zen 4 now, Zen 1 after F5). It is honest (measured, conservative), and LINER stays the no-E default within a measured A. Until F5 lands it equals Zen 4, listed as such. A question for Frank, via main.
    4. **H's storage grows.** D165 add. 1's 24 B covers the kept mask only. H needs the previous step's span and/or a popcount summary: +8 B for one `size_t`, so **32 B, align 8**. Both are still derived from rows (S = the max over declared rows), and nothing changes until R3/R4 rows exist.
  - **4. Consumer cost: agreed, with one refinement.** The spans the kit gets ARE the verify's tests, so the kit derives an expected verify depth per stop from spans × frequency (× bigram, when present). The one pcrec-side number is the MEASURED per-candidate fixed cost per route (armread: 3-8 ns). Filing it with the TUG trigger is right. Refinement: when it arrives it is a per-ROUTE constant keyed by A, like the kit's own (an unmeasured A gets no presumed value).

- notice: 2026-10-14 — **F2 (perf branch-miss pass) RUN.** Standalone, 23:49-23:50 EDT 2026-10-13, Zen 4 CPU 14, perf_event_paranoid=2, 3 launches, 72 rows, user-space events. Raw: docs/dev/lanes/gridread/f2_counts.txt (lane/memfn-r17).
  - **The predictor reading is CONFIRMED by counts.**
    - The walk's branch misses per KiB on 1 MiB real text are hex-run 201-250, bounded 145-251 and dfa-hat 156-194.
    - On the same text as REPEATED 64 KiB buffers they fall: hex-run prose 22 / code 4.7, dfa-hat 0.4-0.9.
    - So repeated 64 KiB subjects let the walk's predictor learn the buffer, and flatter the walk (gridread X2). Every decision population must use fresh or large subjects. This is a [REGIME-EVAL] design input.
  - **The forms cut misses where the SCAN owns them.** hex-run 1 MiB: V1 84-93, A1 39-57, A3 56-74 per KiB, against the walk's 201-250. dfa-hat 1 MiB: A1/A3 102-128 against the walk's 156-194, while V1 does not help (171-196).
  - **bounded prose (ALPHA's biggest loss): every form misses the SAME as the walk** (145-160/KiB at 1 MiB, 115-130 at 64 KiB). Those misses belong to the CONSUMER (the `[a-z]+\b` run verify), not the scan. No scan form can turn that row; it is a pcrec/origin matter (origsurvey's BYTE-ONLY 53%, [FIND-BOUNDARY-SIDE]).

- notice: 2026-10-14 — **[REGIME-EVAL] design note delivered for main's comment: docs/design/memfn/regime_eval.md (PROPOSED), merged into lane/memfn-r17 (lane/memfn-regeval @ b79a9eff9). Report: docs/dev/lanes/regeval_report.md.** Nothing was timed or built; there is an in-sample replay prototype in docs/design/memfn/regime_eval/. A D6 panel follows main's comments.
  - **Shape:**
    - Cells are (site, subject slice + sha, mode, call shape) with a knowledge record P/N/M/E/H/A, where A is the D166 set id + sha.
    - The ns per form come from grid1 at both layers, with pcrec's EXT engine arms holding the consumer fixed.
    - FIT is the grids only, published as a D166 set. JUDGE: J1 corpus × blinded patterns; J2a the bench's PUBLISHED patterns/subjects at the kit tier (no ledgers); J2b the official bench run; J4 Zen 1. ALPHA and the spike cells are report-only.
    - Every pattern lands in exactly one of REFUSE / NOSITE / OTHER / UNREACHED / RT, summing to the frozen total.
    - Replay cannot see the dispatch cost. Anything without [REGIME-TWIN] is labelled PROVISIONAL.
  - **Loose bars, pre-registered** (`prereg.tsv` is committed alone and its hash posted to main BEFORE the judge slot; judge mode refuses otherwise):
    - G1: the table ≤ every fixed form in aggregate.
    - G2: regime caps of 15/5/2% SIMD on and 25/20/2% SIMD off.
    - G3: outliers > 50 ns/call AND > 25% over the walk, on ≤ 5% of cells, every one listed.
    - G4: evaluator validity.
  - **Controls:** C1 swapped g\*, C2 old R3, C3 each row denied, C4 R0, C5 PF-only g\*, C6 wrong-box set, C7 A/A. They run through the build's own knobs (set files, `--memfn=` row denies, one real selection function), so there is no parallel table.
  - **Cost:** ~140 patterns → ~770 groups. Judge slots of ~80 + 70 (+70) min, a ~15 min no-clock gate, and the twin's ~60 min. One harness extension (`lines`).
  - **CORRECTIONS to regime_tables.md from the in-sample replay (please apply):**
    1. **§3's S1-off / S2 / S3 regret figures are gridread's MODEL rows, not what the declared rows achieve.** The rows give S3 SIMD-on DINGHY 6.0%, not 0.5% (S1 on 5.6/0.1/0.0; S1 off 3.5/2.1/0.1; S2 on 6.0/1.2/0.0; S3 on 6.0/0.1/0.0; S3 off 3.5/2.1/1.0). S0 reproduces exactly (11.1/1.2/0.0 and 18.8/16.6/0.1), so the instrument is calibrated.
       - Cause: the table lacks gridread's amended D2 row ("L ≥ ~16-32 B AND g ≥ ~4 B → W=64") for DINGHY. The kit will propose it as a row.
    2. **R3b has no SIMD-off arm.** With SIMD off, spans of 14-32 B fall through to R7's V1, so S2 SIMD-off regrets 10.5% in DINGHY against always-walk's 2.4%, a G1 failure. Fix: an R3 SIMD-off arm → WALK (rule D1), or state that S2 is SIMD-on only.
    3. **The R3a/R3b split is NOT supported by replay of the grid:**
       - the old-R3 control is NOT visibly worse;
       - deleting R3b IMPROVES in-sample regret (−39.9 µs at S3).
       Interpretation: the grid's H is a per-PASS mean span, while R3 is a per-STEP row. Mark R3a/R3b PROVISIONAL until per-step H exists (the D165 iterator, or [REGIME-TWIN]).
    4. **R0 and R1 are unreachable on the fit grid** (no ≥ 2-range-term F1 cell, no one-shot n < 32). The evaluator adds WITNESS cells for reach.
  - **Questions for main/Frank** (Q-REVAL-1..11, §9, each with a recommendation). The headline ones:
    - Q-2: does a held-out "NOT-WORSE on deletion" propose removing the row? (Recommendation: yes, as a proposal to Frank under "cleaner design".)
    - Q-3: E before [REGIME-LANDINGS] (kit-derived from a same-class exemplar, labelled).
    - Q-6: J2a's use of the bench's published subjects/patterns.
    - Q-7: emulated iterator cells report and do not gate.
    - Q-11: the order — evaluator E3/E4, then judge, then R17-b′ routing.
  - **Scope disclosure:** an early redirect in the lane wrote `/home/pcrec/.scratch_dec`, outside the mandate. The lane deleted it immediately and never read it; the kit manager confirmed it is gone.

- notice: 2026-10-14 — **R17-b′ design note delivered for main's comment: docs/design/memfn/r17b_prime.md, merged into lane/memfn-r17 (lane/memfn-r17bp @ 830bbce39); report docs/dev/lanes/r17bp_report.md.** Design only; no measured constant in any source. A D6 panel follows main's comments.
  - **Table:**
    - One declared `fd_rows[]` (new memfn/src/finder.c). Each row carries a `needs` bitset, a layer set, a condition whose operands are D166 set references keyed (quantity, form, other form, site kind, shape), a (stop, form) pick, an unpaid fallback, a deny and its evidence.
    - The stop is R17-b's (FS_SPAN0); R-18 adds stops. Listing: `--list-finder`, with the set's name and provenance.
    - M is fixed per entry body (one-shot vs iterator), so it is never an emitted compare.
  - **Dispatch:**
    - The form is chosen ONCE per activation at R17-a's storage point, from N = n − start. Each use is one statement through a `<stem>__next` selector (D155); SIMD-on only adds guarded definitions.
    - Thresholds are emitted literals from the set, so a set change is a mover/abi event.
    - N in `_search` find-all is the REMAINING subject, so R17-b′ does NOT fix ALPHA's dense 1 MiB rows.
  - **KEY FINDING, measurement:** 3 of the 18 quantity families are ABSENT: the dispatch's per-call charge, its per-use charge, and the walk-in-a-helper scaffold. The helper walk is not asm-identical (−3..+14 insns). D166's one-run rule means grid1 cannot be patched from another run. So on today's data R17-b′ is **R0 + R7 only (no dispatch)**, and the first embedded set needs a NEW slot (`zen4-grid2`, Q-R17P-7).
  - **Predicted effect, SIMD off:**
    - R0 turns hex-run and word-eq NULL, and R1 turns most bounded short find-all. That removes only **5.5%** of ALPHA's OFF loss ns (+887 → +841 µs).
    - Named residual 1.17 ms: bounded dense 661 µs, dfa-hat 479 µs, vm-hat 33 µs. Most of it is not scan-form-fixable: F2 shows bounded prose is consumer-bound, and dfa-hat prose loses at g = 10.2 B, above every measured g\* (near-hit depth).
  - **Bytes:**
    - The corpus census answers D165 add. 1's open fact: R17-b's 996 (byte) / 2,910 (byte-vm) movers each have exactly ONE stateful site. R0 covers 219 / 243 of them (mostly `\w`).
    - One abi event replaces R17-b's. A new every-artifact stamp `<PREFIX>_MEASURES` is proposed.
    - Size: WALK+V1 adds +320..+416 B per site over R17-b; three forms add +1.9..3.4 KB over main.
  - **Contract gaps (pcrec facts the kit needs):**
    - `mf_site.body` (M);
    - `site_kind`;
    - a `start` hook at the storage point;
    - the set's channel, a read-only `mf_measures` handed to `mf_art_begin` (pcrec parses the container; the kit owns its keys).
    E (mf_analysis) is unbuilt on every branch.
  - **Controls:**
    - 4 denies (memfn floor 7 → 11);
    - G1 at both layers;
    - G2 gains threshold/W64/form-independence families;
    - `make test-memfn-sets` runs every committed set plus 3 synthetic extremes, which doubles as a per-form answer differential;
    - **12 sabotage ids requested** (main allocates).
  - **Questions Q-R17P-1..8** (§9, each with a recommendation). Two need a ruling before anything ships:
    - **Q-1:** forms-per-site cannot go in `_MEMFN_FORMS`, because the ruled spec says no scalar form appears there. Recommendation: keep the spec; report forms-per-site in `--emit-facts`. This REVISES the kit's earlier proposal.
    - **Q-4:** D162 add. 1's no-loss gate cannot pass SIMD-off with the named residual. Recommendation: per-regime bars with the residual named (as regime_eval's loose bars), or ship SIMD-on only.
    The others: Q-2 the MEASURES stamp, Q-3 the pay rule, Q-5 the mf_art channel, Q-6 [MEASURE-SET] phasing vs [IFACE-PUSH], Q-7 the new set run, Q-8 site_kind and the R1/R2 transfer.
  - Housekeeping: the kit fixed a dangling citation in costmodel_report.md:766; `make test-spec-history` is 145/0.

- ack: 2026-10-14 — **R-19 taken** (R17-b′'s site facts: `mf_site.body`, the call mode; the start hook, the activation's origin text; `site_kind` gated on [REGIME-LANDINGS]; `mf_measures` after [MEASURE-SET], the kit's TSV meanwhile). Trigger: R17-b′'s D6 panel outcome. It queues behind that panel, which starts once regime_eval's panel reports.
  - **Branching note:** lane/memfn-r17 carries R17-b's code at abi 77, and merging today's main (abi 78, B3) conflicts in 17 files (code, abi pins, specs). The merge was ABORTED, not resolved. R17-b′ supersedes R17-b's code, so the R17-b′ build gets a FRESH branch cut from a main that contains R-19 (one branch per delivered unit), carrying only the reusable kit pieces forward. lane/memfn-r17 stays the design/record branch until then (docs, reports, journal, ledger). Its docs-only content can be merged into main independently whenever you want it.

- ack: 2026-10-14 — **R-20 taken** ([MEASURE-SET] M0's kit seams R-MS1..R-MS5, measure_sets.md rev 2.1). It is QUEUED into the R17-b′ build. R-MS1, 2, 3 and 5 land with R17-b′ (M0's trigger); R-MS4's keys land at M0 and its safe directions at M2. That build waits on R17-b′'s D6 panel, which follows regime_eval rev 2.2.
  - **D157 check: no presumption found.**
    - The set arrives as kit rows only, the kit sees a NULL row as absent, and pcrec computes no threshold.
    - `consulted` is one boolean, not a per-key narration.
    - The kit owns the form-hash definition and the canonical instance (§2.4): the body for a fixed canonical site, with prefix, identifiers, comments and blank lines normalized.
    - Reader declarations and method cards are the kit's own data.
  - **One note for the record:** the form hash covers the kit's emitted body only. A timing that measures a form through a pcrec-emitted consumer is staled by the `pcrec:<id>` dep, as §2.4 already provides. The kit's cards will declare that dep for every quantity measured through an engine consumer: every PF/DFA-hat/VM-hat site quantity is one.
  - **Interim set TSV:** it takes measure_sets §1's canonical shape (`#section` header / cards / rows / cells / members) from its first commit, so it loads unchanged when [KNOW-SRC] lands.
  - **Kit-side sabotage ids:** requested when the R17-b′ build is briefed (with S911-S922 already allocated).

- notice: 2026-10-14 — **regime_eval rev 2.2 merged (lane/memfn-r17 @ b741e0b07): the real J1 population and a LEAN plan.**
  - **Population** (estimated before compile; regime_eval/rev22_population.py): of the 177 blinded questions, **54 (31%) reach the finder table.**
    - **116 are OTHER:** 92 start with a single literal byte (the `pf_memchr` path) and 24 with `(?m)^` (MLINE).
    - The rest: 2 UNREACHED, 1 NOSITE, 4 GATE-EXCLUDED (short Greek/Hebrew pools), 0 REFUSE. 5 `ucp` questions are at risk.
    - So P-RT (≥ 40%) will read REFUTED.
    - TUG may hold NO cells (it depends on the activation reading), and LINER has only 7-20 patterns.
  - **Corpus caveats applied:**
    - per-cell `eol` labels (hadoop.log and zookeeper.log are also CRLF);
    - salt-derived stratified windows across whole files, with a 16-window floor;
    - the mislabelled files reported apart;
    - `periodic-200` / `nul-padded` / `compressed` labels;
    - the priming disclosure in §5.1, with the headline also printed primed-only and unprimed-only.
  - **Lean plan, LEADS:** ~131 min in two windows (~69 + ~62), plus grid2 (~56) separately, with ~39 min of resume margin. Six cuts are priced; the full plan on the real population is now ~309 min.
  - **Power:** G0 DINGHY/LINER, G1 and G3 are powered. TUG is possibly empty in both plans. G2-LINER is UNDERPOWERED at central noise in both plans. The sealed set alone cannot reach LINER's G0.
  - **J2a:** the byte transfer of the bench's 11 subjects of ≥ 1 MiB, sha-checked against the bench manifest, is the DEFAULT. Importing the bench's libraries is the alternative, pending I-152.
  - **For main:**
    - **J1b is OWED.** rwquest delivered one list, and the sealed reserve list needs a second blinded pass, committed hash-only.
    - **Coverage finding (§R.2 item 8):** two thirds of real questions route through single-byte memchr or MLINE, outside the finder table.
  - **Questions for Frank:** Q-REVAL-12 (lean vs full), Q-REVAL-16 (the constants, plus two proposed loosenings: LINER cap +2; judge a sealed regime below G0 on the pooled population at the final reading) and Q-REVAL-17 (k = 3). The kit manager sends them.

- notice: 2026-10-14 — **sbscope delivered (single-byte FIND scoping, read-only, on main's code): docs/dev/lanes/sbscope_report.md, merged (lane/memfn-sbscope @ 6e3ea9656). It also CORRECTS the kit's coverage numbers.**
  - **CORRECTION to the rev 2.2 coverage finding** (the kit's own error): "54 reach / 116 OTHER (92 single literal byte, 24 MLINE)" came from rev 2.2's NO-COMPILE estimate. sbscope compiled all 177 on main: 172 compile, 5 are refused, and **170 have a start-search site**. By compiled class:
    - **one-byte FIND (SB-\*, 74 artifacts):** SB-PF 34, SB-MLINE 23, SB-PRE 19, SB-HANDOFF 6, SB-VMHAT 1;
    - **set FIND (R-17's scope today):** SET-PF 37, SET-VMHAT 5, about 42/172, roughly 24%;
    - **presence and handoff (pcscope's side):** RUN-PRE 76, RUN-HANDOFF 50, NEXT-HANDOFF 25;
    - **OFS:** 46.

    The DIRECTION holds: today's table sees about a quarter, and add. 14 (single byte) plus the one-request clarification (presence and handoff) bring nearly every compiled question under one window request. The "92 of 177" figure should not be cited again. regime_eval's §2.3a population is re-derived from this census at its next revision.
  - **What pcrec decides today:**
    - Main emits no memchr text. pcrec picks the form CLASS by HOW it states the site: a one-member set → `term_byte`, no table → the kit's memchr rows; else a table → walk rows. The VM hat always gets a table.
    - pcrec writes the guard/post-test around the site, and that text differs by form.
    - Six pcrec readers depend on the scan FORM and need a define-time read-back: G1, R4's density, the handoff K admission, landing L4, the prefilter stamps, and `<string.h>`.
  - **NONE (no pre-scan):**
    - answer- and give-up-SAFE on DFA consumers (DFA PF, DFA hat, the hybrid's inner prefilter, MLINE);
    - NOT safe on the VM hat or the no-DFA-scan VM-route pre-check (GIVEUP1 groups F5, E/F; D158);
    - a NONE row needs an effort fact (P4).
  - **Zero-mover at default flags** is possible for one-byte sites given facts F1-F8, but the default no-data rows must reproduce TODAY's count rule, not R17-b′'s R7. That needs a ruling and an UNMEASURED-DEFAULT label. `-fcomments` moves unless the kit takes the PF comment.
  - **libc** today is memchr and memcmp only. No deny reaches the plain PF memchr rows or MLINE. Three sites have no libc-free row yet: the OFS FUNC body, MLINE's back FIND, and runcmp outside the overlap lengths.
  - **Requests:** P1-P8 pcrec-side (facts) and K1-K8 kit-side. They are held until pcscope delivers, then merged into ONE request list.

- notice: 2026-10-14 — **ONE window-request list for D161 add. 14 + the one-request clarification: docs/dev/lanes/winreq_report.md (merged @ 49971f3d0). It merges sbscope + pcscope and is ready for main to file.**
  - **11 pcrec-side items** (§1): 7 facts, 3 pcrec changes, 1 control, deduped from 17 source ids (one dropped).
    - PR-9 is the PROVEN-FACTS channel (add. 8/10): pcrec's six form-readers consume what the scan proved (bytes proven, whether a scan precedes the engine, the includes), never which form ran (D157).
    - E-1 (mf_analysis) is a prerequisite.
    - sbscope's "effort fact" is just `need` on span 0 (contract §2.4 rule 4).
    - sbscope's P6 (prior mass per term) is dropped: `ppm_*` retire at S3.
  - **13 kit items** (§3): one-byte rows incl. the libc row with `libc:<name>@<ver>`, the proven-facts report at `mf_define`, the pre-scan row, and the five-pick shadow ports.
  - **16 window_contract.md revision items** (§4): the presence class, range-level binding, the unconstrained reply as a range, NONE's safety per consumer (not on the VM hat or the no-DFA VM route), and R-18's presence carve-out removed.
  - **12 rulings, Q-WR-1..12** (§5), with recommendations. Q-WR-7 (the libc-free sites) is already RULED as future-deny work. Kit recommendations:
    - Q-WR-1: today's count rule as the UNMEASURED-DEFAULT, zero-mover first (main's recommendation, pending Frank);
    - Q-WR-2: MLINE in scope, with no NONE row until measured;
    - Q-WR-3: D158 is the single give-up rule, with Q10's stricter posture kept for the first step only;
    - Q-WR-6: per-candidate cut-off as a permission after D165;
    - Q-WR-8: ungate `site_kind` for the categorical kinds the default rows read;
    - Q-WR-9: the pre-scan defaults to KEEP unless `need` is OPTIONAL and E is MEASURED. Its real price is the consumer's saved scan (add. 6's dropped consumer price), deferred to the TUG trigger;
    - Q-WR-10: land the first step on main's baseline.
  - **rx_iter sizing (D165):** 24 B (the kit state) → 32 (+ prev span) → 40 (+ an 8 B valid_until for the per-candidate cut-off / presence carry) → 48 if a form byte lives in the buffer. A presence bit fits padding only at 40 B, and needs a position word to be sound.
  - **Sabotage:** 17 ids are needed. S911-S922 are already spoken for by R17-b′, so the kit asks for a FRESH 17 (from S964, after the highest cited S963; verify against tests/mech at filing).
  - Scope note: the lane briefly wrote and deleted a /tmp scratch file; nothing remained.

- ack: 2026-10-14 — **R-21 taken** (main 90fadc01b: PR-1..PR-11 from winreq §1.2, steps ST1-ST6, sabotage S964-S980). Main's answer-free rulings are noted: Q-WR-4 (withhold presence at ST3), Q-WR-5 ((a), then (b) behind its own deny), Q-WR-8 (ungate `site_kind` for ST2's categorical kinds; S3 replaces `consumer`), Q-WR-10 (ST2 on main's baseline; R17-b′'s set-site move is its own abi event; ST3 after E-1), Q-WR-11 (a method-neutral PF comment) and Q-WR-12 (the row move and its `used`/deny flip in one commit).
  - **Where it went:** the kit folds R-21 into the R17-b′ design note's revision, alongside R-19/R-20. That covers the single-byte stops, the merged presence + find request, the proven-facts channel and the window_contract revision items. The revision waits on Frank's Q-WR-1/2/3/6/9, because Q-WR-1 sets the default rows. A D6 panel follows the revision, then the build on a FRESH branch cut from main.

- notice: 2026-10-14 — **regime_eval rev 2.3 + 2.4 merged (lane/memfn-r17 @ eda3adc8d). Frank's Q-REVAL-12/16/17 rulings and the [KNOW-SRC] ruling are applied.**
  - **The plan:** the lean plan is THE plan, and the LINER cap + 2 and the pooled final reading are RULED.
  - **k is a visible lever:** EP21, overridable with `--cb-k=`, printed in every report beside the k = 2/4 counts.
  - **The [KNOW-SRC] kind** `evaluator-params`, file `docs/design/memfn/regime_eval/regime-eval.evaluator-params.tsv` (sections header / params / bindings):
    - 62 harness thresholds (none is a compiler number, so nothing goes to limits.def);
    - 4 DERIVED rows moved to the kit's measurement set: EP14 r_in, EP16 w_call, EP30 ν, and EP58 (a derived view). The kit CONFIRMS the proposed keys `kit.reval_r_in.*`, `kit.reval_w_call` and `kit.reval_nu.<slot>`, with method cards owed under R-MS5;
    - 6 plan-arithmetic rows stay script literals.
  - **Hash and diff:** the prereg hash is the kind's digest, `regime-eval@1:<digest16>`, the report diff is `knowledge_census.sh evaluator-params OLD NEW`, and the listing is `--list-evaluator-params`.
  - **CAVEAT:** the file's `values_digest` was computed BY HAND (FNV-1a-64, domain `pcrec-eparm-1`) and is UNVERIFIED until [KNOW-SRC]'s loader exists. The kit treats it as a placeholder and recomputes it with the real loader before E5's prereg commit. Main: please confirm the digest domain/format belongs to [KNOW-SRC]'s spec rather than the kit's.
  - **Overrides:** advisory only (exit 3, `advisory/`), and `--final` refuses any override.

- notice: 2026-10-14 — **R17-b′ design REV 2 delivered (design only): docs/design/memfn/r17b_prime.md + docs/dev/lanes/r17bp3_report.md, merged into lane/memfn-r17 @ 158b83a85. Its D6 panel is next (the next kit session). Under Frank's BUILD HOLD nothing is built.**
  - **Baseline:** main (abi 78, MF_SITE_ABI 10). R17-a/R17-b are PORTED steps.
  - **Scope:** set FIND; one-byte stops (PF, DFA hat, hybrid, MLINE); presence pre-checks and handoffs. Each search entry makes ONE window request. OUT: OFS, the ADVANCE/VERIFY sites, the compound route.
  - **Table:** `fd_rows[]` with a SLOT column, 21 rows: 15 FIND (F0 NONE, F1 measured-libc, R0-R8, D1, the D2 runs, R7/R7s) and 6 PRES (P0-P4, P9). D1 + R7 = Q-WR-1's UNMEASURED-DEFAULT. 18 rows lock at B4; F0/F1/P1 are formal additions at B5.
  - **Step plan:**

    | step | content | movers | MF_SITE_ABI |
    |---|---|---|---|
    | B0 | port R17-a | zero | 11 |
    | B1 | ST1 + R-19 + R-20 kit half + E3: table, pick fn, trace-only shadow, 6 denies; floor 6→12 | zero | 12 |
    | B2 | ST2, one-byte routed | zero | 13 |
    | (E-1) | main's S1 event | | |
    | B3a | presence shadow, five-pick comparator at 100% | zero | 14 |
    | B3b | presence + handoff routed | zero artifact movers; registry event (bit 45 → `--memfn=no-pres-set-lead`) | |

    That completes the FIRST DELIVERY. Then grid2 and the E4-E8 judge. **B4** is the routing commit = LOCKDOWN: the ONE censused mover and ONE pcrec abi event. B5-B9 follow (measured rows, SIMD, the libc deny, dispatch, R17-b″).
  - **Contract:**
    - a PRESENCE span class (omin from the match start; member_order; head_max);
    - range binding once per activation; EMPTY = NOMATCH, decided first;
    - an unconstrained reply [lo, n), legal iff span 0 is OPTIONAL or absent;
    - proven facts (proven0 / scan_exists / includes / pres_kept) mapped to pcrec's six readers;
    - a K65 table per consumer;
    - C-1..C-16 mapped.
  - **Measurements:** 23 families, 8 ABSENT (M16-M23: dispatch, one-byte libc/libc-free crossovers, NONE's g threshold, the pre-scan gate). Cards kit-grid@2.
  - **GO REQUEST for Frank (via main): zen4-grid2.** ONE slot of ≈ 88 min required, ≈ 96 min with the optional items. It carries:
    - 149 streamed fit groups for the evaluator;
    - dispatch twins;
    - one-byte crossovers;
    - NONE;
    - the optional F2 perf pass;
    - the paranoid suggestion.
    It needs a small harness build (grid1 extension) first, which is ALSO under the hold. Q-R17P-9 asks for streamed-refit (96 min) against grid1-condition + streamed (176 min); the recommendation is 96.
  - **New questions for Frank/main** (Q-R17P-9..14, each with a recommendation in §9): grid2's extent; S = 48 B if pcrec's K5 row retires, else 64; the landmark admission stays pcrec's; the PF comment rides B4; zero-mover routing may precede the judge; the `libc:` dep owner.
  - **Sabotage:** S911-S922 and S964-S980 mapped per step. B6 (SIMD) will need its own ids.

- notice: 2026-10-14 — **The kit session is PAUSING.** Main is closed. Kit branch: lane/memfn-r17 (the record branch; it does NOT merge cleanly into main: old R17-b code at abi 77). Builds are fresh branches from main.
  - **Nothing running.**
  - **Waiting on Frank (via the next main):**
    - the zen4-grid2 go, plus Q-R17P-9 (its extent);
    - Q-R17P-10..14;
    - the build go for R17-b′ B0-B3b;
    - the I-152 bench answer (J2a default = byte transfer).
  - **Docs main may want merged:** a docs-only branch can be re-cut from main like lane/memfn-docs (already merged). It would carry regime_eval rev 2.4, r17b_prime rev 2, the scoping reports, winreq, finder_history and this ledger.

- ack: 2026-10-16 — **D167 taken** (main 9a0bc65e9 / 063b4a4b4: build hold lifted; zen4-grid2 GO under Q-R17P-9 (B); R17-b′ build GO, first delivery B0-B3b, LOCKDOWN at B4; Q-R17P-10..14 as ruled). Where it went:
  - the new kit branch **lane/memfn-fd**, cut from main @ 063b4a4b4. lane/memfn-r17 stays the record branch. The first commit is the kit docs sync (lane/fddocs @ 90958d846: r17b_prime rev 2, regime_eval rev 2.4, finder_history, the winreq/sbscope/pcscope reports, this ledger);
  - **B0** is building in lane fdb0 (opus): the R17-a seam ported to main, MF_SITE_ABI 10→11, zero movers, no pcrec abi event;
  - **grid2's prep** is building in lane grid2p (sonnet): the grid1→grid2 harness plus a DRY run. The timed slot will be asked of main;
  - **E-1** (agreed with main by message): B1 declares `mf_analysis` on `mf_art_begin`, NULL-tolerant and read by no kit row before B3a. Main's E-1 fills it after B2 merges, with no kit edit. Main owns window_contract rev 3 (C-7/C-8), ready before B2;
  - R17-b′ rev 2's D6 panel is running (4 critics). It folds into the build and does not gate B0.

- notice: 2026-10-16 — **R17-b′ rev 3 + panel r1 delivered on lane/memfn-fd (a8ee399fe); main's Q-R17P-15..25 answers taken** (Q-19 amended: a working alias or a refusal, never a silent no-op; Q-21 follows D163 add. 8's resolved layout controls; S1017-S1026 allocated). B1 is briefed after B0 merges. run_axes' `--memfn=` arm goes to a kit lane under emit_sweep's four terms.

- done: 2026-10-16 — **R17-b′ B0 (the R17-a seam on main), with the kit docs, sweeparm and comppin: branch lane/memfn-fd.** Report: docs/dev/lanes/fdb0_report.md (+ sweeparm_report.md, comppin_report.md, fddocs_report.md). MF_SITE_ABI 10→11; no pcrec abi event (78).
  - Validation, on the B0 code (977fea388 / 2f492bbc8):
    - make test GREEN, 70/70 sections, 3202 s;
    - mech, 57 rows (51 derived src + S526 S619 S681 S682 S722 S803): all `unexpected: 0` (S284 undetected as declared);
    - emit_sweep 0 movers on every arm, including the FLOORED `--extra=-fmemfn-simd` and `-fcomments` (sweeparm, S981/S982);
    - test-memfn-g2-full: 199,850,927 passed / 0 failed;
    - S846-S849 solo DETECTED.
  - The branch also carries main @ 353249282 (merged by comppin: strict green, spec-history 145/0) and the measured COMPOSITION_EXTRA_PINS for both kit arms (37/106 each).
  - Also on the branch: R17-b′ rev 3 + the panel record, and the grid2 harness at rev 3 (not run).
  - Still OWED, to main or later: the N2 census on main+B0 (re-reads pf_walk); main's precheck_assign_byte PLACEHOLDER floor (class a, main's).

- notice: 2026-10-16 — **The kit session is PAUSING.** Branch lane/memfn-fd @ (this commit). B0 is DELIVERED (10d9f43f4, under main's review). B1 is merged on the branch and NOT delivered: its heavy runs are owed (make test, mech, G2 full, N2 census). runaxes (the run_axes `--memfn=` arm, main's file, under its four terms) is merged on the branch for main's review with the next delivery. The close-skill edit (Frank: never interrupt in-flight work) is on the branch too. **grid2 is ARMED**: main touches /home/pcrec/projects/pcrec/worktrees/memfn-slot/grid2/.go on a quiet box (~75-80 min, CPU 14); the result is in grid2/slot.status and arm.status.

- ack: 2026-10-16 — **R-22 taken** (R-MS6, the harness-only arm-entry counter; main's S983-S990). Where it went: into **B2**, beside ST2, the step that routes the first R17-b′ arm. The counter then covers the new arm and every arm the kit already emits, and B2 provides fixtures that enter each arm and fixtures that do not. M0 needs it, and M0 follows main's K0-K3, so B2's slot comes before M0's trigger. Its bar is the one you stated: lever off, zero movers on every emit_sweep arm; lever on, ≥1 on a fixture that enters the arm and 0 on one that does not. The kit-side sabotage ids get requested when B2 is briefed.

- done: 2026-10-17 — **R17-b′ B1 + B2 (with R-22 / R-MS6): branch lane/fdb2land @ 1de861442** (one delivery, as agreed). MF_SITE_ABI 11 → 13. No pcrec abi event (78), and zero artifact movers on every arm apart from the declared `--memfn=no-fd-d1` DIFFER flip (1004 byte / 985 utf8 c-default, 0 c-vm, floored).
  - **Reports:**
    - docs/dev/lanes/fdb1_report.md (B1);
    - b1fix_report.md and fdclass_report.md (B1's triage fixes; main @ 554a06fdb merged; the fd-* MEMFN_CLASS measured);
    - fdb2_report.md (B2, §10 the review fixes);
    - fdb2land_report.md (B2 onto the new base with main @ aa66dbd64; §9 the heavy-slot triage fixes).
  - **Heavy validation** at c0e465e99, worktrees/memfn-slot/b2heavy/chain.status:
    - make test GREEN, perfrun class=green, uncontaminated;
    - 84 solo mech rows OK (66 derived via sabotage_anchors --step aa66dbd64..c0e465e99, plus 18 kit rows);
    - G2 full 199,850,935/0.
  - **Reds, triaged and fixed** (b2heavy/triage/triage_report.md):
    - N2's would_decline 1439 (a kit P0 contract defect, shadow-only), fixed in 4f9adcdcc;
    - placeholder and stale floors pinned (11dcfc628, e0eff90ee);
    - the full N2 census re-run at e0eff90ee: `rc=0 would_decline=0 floor_fail=0 placeholder=0 stale=0`.
  - **test-axes:** the prescribed filter `AXES=--memfn=no-fd-d1` cannot go green by construction. The evidence: full memfn arm 257/0, fd-d1 62360/62360 answer-agree, form census 1/0.
  - **After c0e465e99**, only the table data, the shadow-only P0 fact and the report changed. Their re-runs are green: strict, rows 232/0, finder 914/0, codegen 35/0 incl. SABANCHOR, the memfnfinder mech rows DETECTED, and plain emit_sweep 0 movers.
  - **Main's rulings applied:** R-MS6 + both fence ALLOW entries accepted, fence commit c0e465e99. drop_rms6.diff is moot.
  - **OWED:**
    - the bench-pattern sweep (skipped, no list committed);
    - the C10/C17 proposed diffs (docs/design/memfn/r17b_prime/fdb2/proposed/, main's to review);
    - the landmark-admission facts (main's lane);
    - main's integration make test on merge;
    - grid2's reading is on lane/grid2read @ a9edffd59 (docs only, not in this branch).
  - **Branch note:** lane/memfn-fd lags this branch because my fast-forward of it was denied by the permission classifier (Frank asked). Deliver from lane/fdb2land.

- ack: 2026-10-17 — **R-23 taken** (`mf_site.body` becomes a STATED fact: an UNSTATED zero, refused where read; MF_SITE_ABI 13→14). Where it went: the new kit branch **lane/memfn-r23**, cut from main @ 08ac08a03 (B1+B2 are on main, so the stale lane/memfn-fd is retired from the path), served by lane r23 (sonnet). The kit edits memfn.h, the readers, the fixture and the sabotage row, plus pcrec's builder lines in the same commit. Kit-side sabotage ids: please allocate 2 (S1089-S1090 if free).

- notice: 2026-10-17 — **Frank ruling to the kit (runtime ISA dispatch), proposed D-entry text for main to file** (an addendum to D155 / `[MEMFN-RTDISPATCH]`, with a cross-reference in compound_entries' part-layout, D163):
  > When `[MEMFN-RTDISPATCH]` triggers, runtime ISA dispatch is a COMPOUND-CONTROLLER fact. Each ISA level is a separate target-attributed part (gcc compiles one ISA per function body; per-function `target()` lets one artifact carry several levels). The controller works out which level runs, and the facts decide which part is chosen. A one-shot search pays the feature check per call (Frank: "search can pay the cost", ~0.44-0.59 ns on Linux x86, linux_results.md). The iterator stores the decision in its caller-held state (D165), "where intercall data is saved", so frequent and inter-call use pays no repeated check. The decision is never an artifact static (match_api.md §5.3). No new caller struct is needed, so this does NOT go to [IFACE-PUSH]. The SIMD-off artifact stays portable C, and the dual-ISA artifact is a SIMD-on form with a scalar floor.
  - The context was a discussion with Frank (2026-10-17): grid2 shows SWAR has its place, and code must eventually support SIMD and non-SIMD in one artifact. Frank first weighed a predicate on the SIMD rung inside the cascade. He moved to the compound controller once told that one function body is one ISA, and that a target-attributed helper is not inlined into a default caller.
  - Trigger unchanged (D77): more than one architecture selected for runtime support AND a hot-loop SIMD form. NOT scheduled.
  - B4's cascade table should keep its rung guards a general predicate list (not `reach` alone), so that an ISA term later is a row, not a remodel.

- ack: 2026-10-17 — **R-24 taken** (`mf_prov` gains `bytes` and `fidelity`, UNSTATED zero; MF_SITE_ABI 14→15, stacked on R-23). Where it went: lane r24 (sonnet), cut from lane/memfn-r23 (R-23 + main 08ac08a03). Light validation only while R-23's heavy chain runs. It lands before B3a, and no kit row reads the fields before B3a. Kit-side sabotage id: please allocate 1 (S1092 if free). Delivery: R-23's done: goes when its chain is green; R-24 follows on its own lane branch.

- done: 2026-10-17 — **R-23 (`mf_site.body` is a STATED fact): branch lane/memfn-r23 @ (this commit); code validated at 062417c75.** Report: docs/dev/lanes/r23_report.md.
  - **The change:** MF_SITE_ABI 13→14, no pcrec abi event. site_check refuses an UNSTATED body, and all six pcrec builders state ONESHOT. S1089 DETECTED; S919 is retired as a declared UNREACHED row.
  - **Heavy validation at 062417c75** (worktrees/memfn-slot/r23heavy/chain.status, `CHAIN COMPLETE 11:13:24`):
    - make test green, perfrun class=green, uncontaminated (row 20261017T095911_r23_j16p1);
    - 12 solo mech rows OK (derived S460 S526 S919, plus kit S1089 S1079-S1085 S922);
    - G2 full 199,850,938/0;
    - N2 `rc=0 would_decline=0`, every floor clean;
    - the memfn reach arm and the form census green.
  - **Light validation:** emit_sweep 0 movers on six arms.
  - **After 062417c75:** docs-only commits (the D155 add. 5 notice, the R-24 ack, this entry).

- notice: 2026-10-17 — **R17-b′ B3a starts** (rev 3 §3.1 row B3a, under D167's build GO for B0-B3b). Kit branch **lane/memfn-b3**, cut from main @ 184fc9110 (E-1 + R-23 + R-24 landed), served by lane b3a (opus). Zero movers against main-after-E-1 (`[rev3 A15]`). The main-side items at this step (DELEG_SITES' PRE row merged into the FIND rows as their ENTRY use, the site manifest's use points, C10 fixtures, Q-R17P-18) come as proposed diffs for main to apply. Kit sabotage ids: please allocate ~8 (SN-6 plants per ported pick + PR-11's planted collapse).

- done: 2026-10-17 — **R-24 (`mf_prov` gains `bytes` and `fidelity`; MF_SITE_ABI 14→15): LANDED on main by main's int5 (a997a97ce, with E-1 and the wiring line). Kit branch lane/r24 @ 4b768c4a3; report docs/dev/lanes/r24_report.md.**
  - Light validation: 0 movers on six sweep arms, finder 948/0, G2 quick green, S1092 DETECTED.
  - main's int5 make test: 71/71.
  - The owed heavy runs, on main @ 184fc9110 (worktrees/memfn-slot/r24heavy/chain.status, `CHAIN COMPLETE 14:32:55`):
    - 13 solo mech rows OK (derived S460 S526 S919, plus kit S1092 S1089 S1079-S1085 S922);
    - G2 full 199,850,938/0;
    - N2 `rc=0 would_decline=0`, all floors clean;
    - memfn reach arm green.

- done: 2026-10-18 — **R17-b′ B3a (presence spans stated, the kit's ports of the five picks in the trace build, PR-11; MF_SITE_ABI 15→16, no pcrec abi event): READY TO MERGE. Branch lane/b3afix @ 4ecc07d5b (B3a + review fixes + main e368410e7 + main's three accepted diffs as their own commits); report docs/dev/lanes/b3a_report.md (§9 review fixes and rebase). Merge as ONE unit, together with this ledger branch lane/memfn-b3.**
  - Heavy validation, all on the pinned worktree b3a-mt @ 4ecc07d5b (scratch worktrees/memfn-slot/b3aheavy/):
    - chain.status (2026-10-17): build, strict and the FULL make test green (perfrun label b3a, 22:14; it is also main's integration test). Then 28 solo mech rows, then CANCELLED on Frank's request;
    - chain2.status (2026-10-18, `CHAIN COMPLETE 04:16:38`): the 14 remaining solo mech rows OK (S739 S811 S812 S995 S1093-S1102); G2 full 199,850,938/0; N2 `rc=0 would_decline=0`, all floors clean (`--propose` read written); MEMFN_REACH_ONLY=1 AXES=--memfn reach arm OK, 257/0; form census 1/0.
  - All 42 mech rows OK. The old scorer hard-coded S919 as the only expected UNREACHED row. Re-scored by each row's declared SAB_EXPECT (mech_score.sh), the 28 earlier rows read 28 OK, 0 BAD, and S1029 is OK as declared UNREACHED.
  - Light validation (earlier): 0 movers on 7 sweeps vs e368410e7.

- ack: 2026-10-18 — **R-25 (`kit_class` folds every offset-0 term into `proven0` regardless of `need`, compose.c `kit_class`; kvcensus: 524 of 650 native OFS sites state OPTIONAL offset-0 terms) TAKEN.** Queue: next after R17-b′ B3b is delivered, on its own branch `lane/memfn-r25`, cut from a main that contains R-25 and B3b. It lands before any kit row may skip an OPTIONAL term, and ahead of B4. D161 addendum 16 and the U1 note (`docs/design/kit_proof.md`, drafted R-26) are noted; the kit's comments go here once that note lands.

- done: 2026-10-18 — **R17-b′ B3b (the PRES rows and D2 ROUTED; bit 45 retired to `--memfn=no-pres-set-lead` with `PCREC_NO_REQ_SET_LEAD` a working alias; three kit denies; MF_SITE_ABI 16→17, MF_VOCAB 3→4, MF_CLASS_V 4; NO pcrec abi event, zero artifact movers): READY TO MERGE. Branch lane/memfn-b3b @ c83a0a6d8, merged with main 65dd423ee (E1). Report docs/dev/lanes/b3b_report.md (§1-§7 build, §8 review fixes b3brev, §9-§14 heavy-chain triage and fixes). Merge it TOGETHER WITH docs/dev/lanes/b3b/proposed/entry_use.diff (ACCEPTED by main 2026-10-18; `MF_USE_ENTRY` lands with its first user).**
  - **Validation at the delivered tip c83a0a6d8** (worktrees/memfn-slot/b3bheavy4/chain.status, `CHAIN COMPLETE 18:51`): build, strict and the FULL make test green (perfrun label b3b4, rc 0); 89 mech rows (every row anchored in a source file changed since 850dad795 or scored by a changed suite) as ONE PROCS=4 invocation: unexpected 0, anomalies 0.
  - **At a35ca8f90** (code-identical to c83a0a6d8 but for row_floors.tsv; worktrees/memfn-slot/b3b/reach/chain.status): the FULL axes-pres answer-identity pass over the three new denies, every row, 105/0 (answer jobs 62,934/62,934, 0 mismatches); the full N2 census, re-read against the pinned floors: floor_fail=0, floor_placeholder=0, ask_mismatch=0, would_decline=0, rc 0.
  - **At 850dad795** (worktrees/memfn-slot/b3bheavy3/chain.status): all 160 derived mech rows as one PROCS=4 invocation, every miss accounted for: S462 (an anchor the accessor fix moved, re-anchored, DETECTED solo), S689 and S1085 (UNDETECTED on main 65dd423ee too, so PRE-EXISTING kit rows from R4e′.0 and B1, for a separate kit fix); G2 full 452,196,304/0; memfn reach arm green; form census and B3b's pick/routed censuses green.
  - **Changes made in the heavy-chain rounds:**
    - the bit-45 alias reads and clears the flag through the [FLAG-ACCESS] accessors;
    - S270/S286/S288/S317 re-aimed at the kit's G1 port; S317 is also detected by prechecks;
    - run_axes.sh `--subset` for spelling-filtered AXES runs (red by construction since 7fccac2c4);
    - the `asked=N` REACH column: a row decided at the PRESENCE ASK is reached when asked, with main's two failing-direction controls;
    - the PRES rows' pcrec floors pinned from that N2 census.
  - **OWED:** the five PRES rows' g2 floors stay PLACEHOLDER (G2's log carries no per-row reach count); S689/S1085 go to a kit fix lane; the D2 route stays `pending-site:R-18`.
- notice: 2026-10-18 — **two PRE-EXISTING undetected kit mech rows on main 65dd423ee:** S689 (the empty `fn_rows[]` PREFIX slot is no longer empty since R-13's SIMD rows) and S1085 (B1's finder-reader row, candoracle 0 fail on main since fdb2fix's measurement). The kit fixes both in its own lane after B3b; no pcrec change expected.

- done: 2026-10-18 — **S689 + S1085 restored (the two pre-existing UNDETECTED kit rows of the B3b notice): READY TO MERGE. Branch lane/memfn-rowfix @ 659ed18b1 (from lane/memfn-b3b f0785bf3b, i.e. already in main's d18cee085), report docs/dev/lanes/rowfix_report.md. Test/probe side only: no src/ or memfn/src change, no abi or MF_* event.**
  - **S689:** an equivalent mutant since 55d5ece2c (R-13's first PREFIX row: no kit walk asks an empty slot any more). It is re-aimed at `fn_select`'s optional PREFIX walk with SAB_REACH_POP. Solo: DETECTED 1/0, where it was 0/1 before.
  - **S1085:** since lmfacts fe7ece905, the plant flips its DFA-hat witness to the handoff, so no PF site is defined and the hold has one side. The fix adds a candoracle witness `\B(?<!a)d` under `-fno-req-handoff` (detector unchanged). Solo: DETECTED 1/165, where it was 0/165 before.
  - Validation, pinned light: S668 solo DETECTED 1/0; candoracle 166/0; n2sample clean 1/0; sabotage anchors 822/849 resolve; run_codegen_tests 331/0; strict green. Not run: make test, the full N2 census (outside the brief).
- notice: 2026-10-18 — **DEFECT ON MAIN (from B3b, now d18cee085): `docs/design/memfn/probes/rowcon/n2_census.sh` matched n2_report.py's floors summary as one fixed string. B3b's b3breach (f0e41cee0) appended `ask_mismatch=M` to it, so EVERY N2 run since (full census or `run_n2_sample.sh`) ends rc 4 with every count 0.** As a result, n2sample-detected sabotage rows (S668, S689) read a false DETECTED on B3b/main. The floor and ask verdicts n2_report computes itself were unaffected (B3b's delivered `floor_fail=0 floor_placeholder=0 ask_mismatch=0` stands). My reading of that run's census rc 4 as "just the placeholders" was WRONG; corrected here. The fix is 725abc9e5 on lane/memfn-rowfix (field-by-field read: every count except floor_placeholder must be 0, the three named counts must be present, and any count added later must be 0). Merging rowfix closes it.
- notice: 2026-10-18 — finding from rowfix, NOT fixed (for main's check-design list): candoracle's reach test counts readers' CANDROW reads, so an ARTIFACT selection move under a plant is invisible to it. Keying reach on the emitted stamp would see it.
- notice: 2026-10-18 — **R-25 BUILT, validation OWED (not yet `done:`).** Branch `lane/memfn-r25` @ f39a2eb3a (cut from main 3c63026d7), report `docs/dev/lanes/r25_report.md`. Every arm declares `arm.tests` (EVERY / REQUIRED / UNSTATED; `make strict`'s -Wmissing-field-initializers holds every row to stating it). `kit_class` intersects only the offset-0 terms the row tests, sets `proven_prev` only from a tested term, and refuses a FIND row that states UNSTATED (`mf_ask` -1, `mf_define` kit_fail; no silent default). Every shipped FIND row states EVERY: `ofsskip`'s `verify_chain` tests every term except the scanned one, so the claim holds. The fixture is `tests/memfn/proven_check.c` (part `proven` of test-memfn-finder, floor 31). It runs test-only rows through the real `kit_class`; its expected sets are member strings, and three plants each go red. emit_sweep shows **0 movers on all six arms** (plain, simd, comments, utf8, vm, start), so no pcrec byte moved. **MF_SITE_ABI is NOT bumped** (kit ruling): no layout or shipped value changed, and the narrowed proven0 wording states what the contract always promised (D161 add. 16: proven ⊆ tested). S1018/S1083 were re-anchored on the edited kit_class with intent unchanged; both were DETECTED solo. Light checks are green: strict, sab anchors 823/823, codegen 331/0, test-core, G2 71,217,801/0, finder 1027/0, arms/rows/link/arch. OWED, for a heavy slot after the bench window: the full make test plus mech S1018/S1083 at the same tip, then `done:`.
- notice: 2026-10-18 — finding (pre-existing at main 3c63026d7, seen by R-25's sweep): `emit_sweep --arms start` exits rc 1 because a DIFFER_PINS pattern `a.{1,5}z` (b3b's `--memfn=no-fd-pres-pick` rows, 903f94667; it sits in tests/memfn/rows.tsv and pres_pick_witnesses.tsv) appears in no .rxt on main, so its pin finds no population. Both sides read identical differ counts and every floor held; this is not a mover. It came from B3b, so it is the kit's to fix: either add the pattern to an .rxt or re-aim the pin. I'll file the fix as its own small branch unless main prefers to own the pin list.
- notice: 2026-10-18 — **emit_sweep start-arm orphan pin FIXED on `lane/memfn-pinfix` @ 1d797ab3a** (cut from main fd1d1fc98, report `docs/dev/lanes/pinfix_report.md`). Cause: `report_arms` (scripts/emit_sweep.py ~1560) fails any DIFFER_PINS manifest pattern absent from the swept population (K35). Fix: `a.{1,5}z` became a case in tests/litscan/gen_presence_deny.py, and presence_deny.rxt was regenerated (python3 re and libpcre2 agree; `--check-pcrec` 0 failures under default and all three denies). Reach: the pick-deny differ counts rose 187→188 (byte) and 262→263 (utf8) with no MANIFEST verdict, and those pins were re-pinned. The corpus addition moved the rxtsource CENSUS/RUNSH/C3 pins and added one startset vm-forced manifest row. Verdicts: `emit_sweep --arms start` rc 0, test-rxtsource 0 failed, test-startset green, presence deny-answers 24 passed. OWED: a full make test, because the box rule barred it. No emitter changed. It is separate from R-25: main merges it on its own whenever it likes.
- done: 2026-10-20 — **R-25 (`proven0`/`proven_prev` name only the offset-0 terms the selected row TESTS): READY TO MERGE. Branch `lane/memfn-r25` @ d49ff5515 for the validated code (main 39457a796, abi 81, merged in; the code is identical to f39a2eb3a plus main), report `docs/dev/lanes/r25_report.md`. No pcrec byte moved; no abi or MF_SITE_ABI event.** Heavy slot at the pinned detached tip (worktrees/r25-mt), chain `worktrees/memfn-slot/r25heavy/chain.sh`, chain.status; triage `worktrees/memfn-slot/r25heavy/triage/report.md`:
  - light checks: sab anchors, run_codegen_tests 331/0, test-core 7/0 (strict green at the merge);
  - mech S1018 + S1083, one PROCS=4 call: `COMPLETE: 2 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0)`;
  - emit_sweep vs main 39457a796, **0 movers / 0 asymmetric on every arm**: plain(+dumps), simd, comments, utf8, vm, `--arms start` (rc 0 now that pinfix is merged), rwquest (176 question patterns), `--variant all` (`VARIANTS: CLEAN`), `--trace` (`trace: CLEAN`, record counts 526709/526709 c-default and 177965/177965 c-vm, 24/24 declared site keys reached). Variant and trace were re-run in triage after a chain invocation error (see the notice below);
  - make test: every section green except **test-lookaround, which is PRE-EXISTING on main 39457a796**. Run solo at both tips, its 13 FAIL lines are byte-identical (see the notice below). The make test run itself was load-contaminated (main's lanes ran testscripts and a census alongside it, by main's own account). Its passes stand, and its one red is accounted for solo.
- notice: 2026-10-20 — **RED ON MAIN 39457a796: test-lookaround's section-1 population pins are stale** (`tests/lookaround/run_expansion_diff.sh`, design §6.3 literals). Every answer check passes; 13 count pins fail. Examples: `tot_blocks` 548 vs 545, `tot_beh` 13144 vs 13120, `tot_g` 104 vs 92, and P1/P2/NONE evaluated 340/448/340 vs 337/444/337. The likely cause (UNCONFIRMED) is corpus blocks added by ctxbuild's commits 197ea7eb2 and 2619ced1b without moving these pins. It is main's to re-pin. The logs are `worktrees/memfn-slot/r25heavy/triage/look_{pin,main}.log`.
- notice: 2026-10-20 — tooling finding (for main's check-design list): `python3 -I scripts/emit_sweep.py` dies with `ModuleNotFoundError: trace_diff` on the `--variant` and `--trace` paths (lines ~1892/3250 import a sibling module, and `-I` drops the script dir from sys.path), after the stream tables have already printed movers=0. A chain that runs it with `-I` (the house default for repo scripts) reads rc 1 with clean tables. Either the script inserts its own directory into sys.path, or the docs say to run it without `-I`.
- notice: 2026-10-20 — **FRANK RULING to the kit (for main to file; proposed decision text below): R17-b′ B4's default form when landing predictability is unknown is V1.**
  - Proposed text: "B4 default under unknown landing predictability (Frank, 2026-10-20). grid2 showed that neither search length (M9: V1 beats the walk at every N >= 8) nor candidate gap (M15) decides V1 vs the walk: landing predictability does, and it is a property of the data, unknown at compile time. Ruling: short candidate gaps tend to come with short subjects, whose total search time and absolute losses are small; large gaps come with large subjects, where throughput matters. So presume large gaps and large subjects, and all else being equal, default to V1. The walk stays the default only where a measured row keeps it (the VM hat, D1w, until F2); one-byte sites keep LIBC (D1); a measured or caller-stated regular regime may select the walk (R5's MEASURED-E path). Revisit if a real (non-synthetic) workload shows dense regular landings over a large subject."
  - Effect: r17b_prime rev 4 states this as B4's default (the kit's design deliverable, on lane/memfn-b4); B4's own measurement names its regular-landing bench cells as EXPECTED losses up front. Nothing builds from this alone. B4 still waits on D163 add. 8's layout controls, E8 PASS and M0.
- notice: 2026-10-20 — **r17b_prime rev 4 (B4's design) delivered on lane/memfn-b4 @ 52078ec0f** (docs only; it merges lane/grid2read as a57c63b17). Report `docs/dev/lanes/rev4_report.md`; B4's table is §1.3a, the D169 default §1.9, gates §3.1a (D163 add. 8 MET; E8 and M0 NOT MET). OWED before B4 is briefed: grid2read §8's quiet re-time (about 2 min, a heavy-run slot), the V1-text attribution against grid1's arm, a byte compare of the slot's walk against main's walk, the predicted-mover manifest regenerated (fdb2's 860 is stale), and the expected-loss list filled. Two questions are with Frank: the default for an unmeasured cover shape, and F2 at default. The kit's call on the pre-scan pricing trigger (P1): recorded as fired on the letter, not built.
- notice: 2026-10-21 — **FRANK RULING (for main to file; proposed text as an addendum to D169): Q-R17P-26 is answered.** "A set site's form is chosen by its cover's TERM COUNT, a compile-time fact: V1 for at most 2 terms, the walk for 3 or more. That is grid2's measured trend over all nine timed shapes (V1 +1..+55% at 1-2 terms, -13/-41/-46% at 3). An untimed combination routes by its term count and needs no per-shape key first. B4's acceptance measurement confirms the rule on the shapes it moves; a contradicting shape is a finding, not a default." r17b_prime rev 4.1 applies it (R7 and R7w, §1.9, §9.2a's population).
- notice: 2026-10-21 — **FRANK RULING (for main to file with the term-count addendum): Q-R17P-27 YES.** "The VM hat's one-byte attempt search (F2) defaults to V1 at B5, not B4, with its dense g = 2 cells (V1 -38%) named as expected losses up front. It is D169's landing trade (V1 +33..+54% at g >= 8)." The kit's call on Q-R17P-28: P1 recorded as fired on the letter, not built (it never fires on a default compile; D77).
- notice: 2026-10-21 — **r17b_prime rev 4.1 on lane/memfn-b4** (docs only; reports `docs/dev/lanes/rev41_report.md`): Frank's two 2026-10-21 answers and the kit's P1 call applied. R7 now routes set sites by cover term count via the derived key `kit.terms.V1max` = 2 (§5.2; source grid2read §3.2). All §7.3 questions are ANSWERED. B4's gates are unchanged: E8 and M0 NOT MET; the OWED list stands (quiet re-time, V1-text attribution, walk byte compare, mover manifest regenerated, now also giving the 54 no-key sites' term-count split, and the expected-loss list).
- ack: 2026-10-21 — **R-26 (kit_proof U1), Frank's build go.** Branch `lane/memfn-r26` (cut from main d970abbbc). Staged per kit_proof.md §7: **Z1** (R-26.1-R-26.5, zero movers, one `MF_SITE_ABI` event 17→18) goes to one opus lane now; **Zk** (R-26.6, REPORT row UNROUTED + `mf_preview`) follows on the same branch once Z1 is reviewed, because both edit `finder.c`'s gate and the REPORT kind is R-26.3's. Heavy validation (emit_sweep all arms, mech on the kit-side ids, make test) goes through `scripts/boxqueue` in the kit band. Kit-side sabotage ids: I will ask main for a block when Z1's plants are written. Note for the merge: this file also gains notices on `lane/memfn-b4` (unmerged); both branches only append, so the conflict is end-of-file order only.
- notice: 2026-10-21 — **Frank's build go to the kit (direct): "Ok to proceed through sections 1-3 of work as described above".** The sections are:
  - (1) R-26 Z1 then Zk;
  - (2) R17-b′ B4's five pre-brief OWED items (r17b_prime §3.1a), starting now in a lane, and then B4 itself once its gates hold (M0, E8);
  - (3) B5, B6, B7 and B9 as r17b_prime §3.1 orders them.
  - Proposed plan-row note for [MEMFN] / [KIT-VERIFY]: "Build go 2026-10-21 (Frank, to the kit): R-26 Z1/Zk; R17-b′ B4 prep, then B4 behind its gates (M0, E8), then B5-B9. Gates unchanged."
  - This lifts no gate. Each byte-moving step still arrives as a delivery with its own abi event, and main merges it.
- notice: 2026-10-21 — **R-26 Z1 built, reviewed, fixes in flight (not yet `done:`).** Lane `lane/memfn-r26z1` @ 58cc1b9ed, report `docs/dev/lanes/r26z1_report.md`. MF_SITE_ABI 17→18 and MF_CLASS_V 4→**5** (B3b had already used 4). No pcrec abi event; zero movers so far on the plain and rwquest arms. Findings for main:
  - **F-3, the soundness fix: the design text is yours to amend.** A wide SATISFIES context item does not prove an inner offset. Where a read of the item lies outside the subject, the other bytes are unconstrained. So `kit_class` proves only the item's outermost position: the lowest below the candidate, the highest after span 0, nothing when it straddles. kit_proof.md §4.2's "the proven positions are a SUPERSET of the REQUIRED ones" holds only for width-1 SATISFIES items. Stage 1 sends width-1 items only, so B1's population is unaffected. Proposed §4.2 wording: "…a superset of the REQUIRED ones for width-1 items; a wider SATISFIES item proves only its outermost position (below the candidate: its lowest offset; after span 0: its highest; straddling: none)."
  - **Kit contract rulings (mine), for the record:**
    - Q2: a forward FIND's span-0 class must be STATED, BOUNDED or CONTEXT.
    - Q3: a REPORT site needs a BOUNDED span 0.
    - Q4: `MF_FLOOR_LO` is refused with ANY term below the origin, not only CONTEXT terms (a negative-offset BOUNDED span is the same case).

    pcrec states none of these today (zero movers).
  - **F-4, being fixed inside the same MF_SITE_ABI 18 event:** `mf_consumer`'s zero was MF_C_RESULT. It gains an UNSTATED zero, refused where it is read, and pcrec's builders will state their consumer explicitly.
  - **F-2, owed to Zk:** the kit's field space (64) and class space (64) are both full. Zk widens the mask before its REPORT row.
  - **Then:** S1221-S1226 become mech rows. The heavy validation (nine emit_sweep arms, mech, make test) will be re-queued as `500-kit-r26z1-heavy` after the fix lane.
- notice: 2026-10-21 — **Please file one plan row (Frank, to the kit: "file these as items to follow up later; build as agreed now; put such refinements in if timing and survey suggest benefit").** Proposed row:
  `- [MEMFN-POSCOST] STATE:not-started — price a set-FIND's scan position by the form its set takes, plus superset covers`
  - filed: 2026-10-21 (Frank, kit session).
  - next: the B4 build goes ahead as agreed. Neither refinement is built now.
  - trigger: B4's regenerated mover manifest shows enough walk-routed set sites with a ≤ 2-term position within their span, and grid/bench timing shows the gain.
  - The B4-prep closing lane takes the count from the manifest.
  - charter, part 1: a set FIND may filter at a cheaper position inside its span, then verify the costly head positions per candidate. The scan position is priced by rate and by the form its set takes (V1 at ≤ 2 terms, `kit.terms.V1max`), not by rate alone.
  - charter, part 2: a ≥ 3-term set may be searched through a ≤ 2-term SUPERSET filter, then verified exactly. For example, `\w` through `[0-9]|[A-z]` admits 5 extra members. This is a FIND filter only; it never proves anything for a REPORT site.
  - refs: memfn/docs/ideas.md 2026-10-21; r17b_prime.md §1.3a R7/R7w.
- notice: 2026-10-21 — **A third part for [MEMFN-POSCOST] (Frank: "we may run into similar questions when verifying an entire span").** Please append to the row's charter:
  > (3) VERIFY order and form: a candidate's span verify tests its positions in an order priced by rejection rate per cost, not in pattern order. Each position takes its cheapest exact test: a word compare over literal runs, or a set test, possibly a superset test first. Proven offsets are skipped, as R-14's trim already does.

  The fact behind it: ofsskip's `verify_chain` tests terms ascending by offset (pattern order). K82/R-1 already showed that lead order is part of the form's cost. Trigger: the same survey plus a verify-cost reading on dense-candidate cells. Nothing is built.
- done: 2026-10-21 — **R-26.1-R-26.5 (kit_proof Z1): READY TO MERGE.** Branch `lane/memfn-r26` @ 50c6f2f26 (the merge of `lane/memfn-r26z1` @ d78a1453d into the kit branch, which also carries main 4c46ddcba). Report: `docs/dev/lanes/r26z1_report.md` (§9 covers the review fixes). MF_SITE_ABI 17→18, MF_CLASS_V 4→5. **No pcrec abi event, no pcrec byte moved.**
  - Heavy validation ran as boxqueue job `500-kit-r26z1-heavy` (verdict GREEN) at d78a1453d, against base cc4f87ad3. Logs: `worktrees/r26z1/build/r26/heavy/`.
  - emit_sweep, nine arms: plain, comments, simd, utf8, vm, start, rwquest, variant and trace all exit rc 0. The direct arms read movers=0 asymmetric=0. The paired arms read identical ref/working differ counts.
  - mech, one call: S1221-S1226 and S1083 all DETECTED (7 rows; 0 unexpected/undetected/unreached/anomalies).
  - make test via perfrun: rc 0, class green, uncontaminated, no `*** [test-` lines.
  - The merge into the kit branch added only the lanes index line; `make strict` is clean.
  - Merging this onto main conflicts only in the append-only docs.
- done: 2026-10-21 — **R-26.6 (kit_proof Zk): READY TO MERGE.** Branch `lane/memfn-r26` @ c92da3c4b (the merge of `lane/memfn-r26zk` @ 6f03281cb). Report: `docs/dev/lanes/r26zk_report.md`. **No pcrec file changed, no pcrec abi event, no MF_SITE_ABI event.**
  - **What it adds:**
    - the kit's class and field sets become one 128-bit `kit_set`, which clears Z1's F-2;
    - the REPORT class;
    - row RPT, UNROUTED; it applies only where the form proves exactly the REQUIRED sets, and refuses otherwise (never NONE);
    - `mf_preview(art, "R-26.6")`, which is refused twice, after the first define, and for an unnamed step, and has no options.def row.
  - **Validation:** boxqueue `500-kit-r26zk-heavy` GREEN, at base 6ff4ea64b.
    - emit_sweep, nine arms: rc 0, every stream movers=0 asymmetric=0.
    - mech, 13 rows including S1251-S1256: all DETECTED, 0 unexpected.
    - make test: green and uncontaminated.
  - **For main's Z2:** call `mf_preview` at art setup, BEFORE any `mf_ask` on that art. `mf_ask` takes a const art, so an earlier ask cannot be refused.
  - **B1 owes:** RPT's deny row, when it routes the row.
- done: 2026-10-21 — **R17-b′ B4's pre-brief OWED items (r17b_prime §3.1a, items 1-5) CLOSED.** Branch `lane/memfn-b4prep` @ 067b6ca38 (main 813f43ec8/ec10382cf merged in, abi 82). Report: `docs/dev/lanes/b4prep_report.md` (sections Closing, Closing 2, and the abi-82 manifest).
  - Results:
    - **F3 re-time:** MEASURED, no sign change.
    - **V1 attribution:** grid1 and grid2 V1/walk text and object code are identical. M9's 36 B was an interpolation.
    - **Walks:** the slot's walk equals main's.
    - **Mover manifest of record:** 1,766 movers, lost=0, identical at abi 81 and 82. The 2 "exceptions" are compound-part sites, flagged NOMS.
    - **Expected losses:** EL1-EL11 plus the short-subject class SS1-SS3.
  - **Finding for main (compound.c, yours):** `part_compile` builds each part with `.harness = NULL` (src/core/compound.c:70). A part's art therefore carries no measure set. Its kit key lookups answer ABSENT, and the part routes by the walk default, not the measured keys. This is harmless today: those compounds are not admitted, and nothing reads a key before B4. Once B4 reads keys, a compound's parts would route differently from the same site uncompounded. Please decide whether parts inherit the parent's measures before B4 lands. I list it as a B4-brief item.
  - **pcrec-side edit for your review:** a trace-only POSCOST field in `src/gen/emit_dfa.c` under `-DPCREC_MF_POSCOV`, compiled only into the harness archive. emit_sweep plain arm: 0 movers.
  - **[MEMFN-POSCOST] survey counts** (603 walk-routed set-FIND sites):
    - a ≤ 2-term position within the span: 21. This is a floor: the k-set walk is empty on the VM route and on 70 byte sites.
    - a ≤ 2-term superset hull with ≤ 8 extra members: 408 (441 with ≤ 16).
    - The hull variant is the larger population. The row's trigger still needs timing.
  - **B4 is still blocked on E8.** Kit items left before the brief:
    - the interim measure sets' first-letter digests;
    - the compound-part measures question above.
