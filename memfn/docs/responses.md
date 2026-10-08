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
