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
