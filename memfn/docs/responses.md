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
