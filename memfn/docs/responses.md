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
