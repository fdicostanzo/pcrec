# docs/dev/summaries/ — executive summaries

Executive summaries written for Frank at his request; the manager's voice;
each cites the ledger/review it summarises and never replaces it.

## Files

- `2026-09-02-exec-bench-full-suite-1989c62.md` — findings, surprises,
  impact, next steps for the pcrec-bench full-suite night at pin `1989c62`
  (abi 15). Cites `pcrec-bench`'s ledger
  `docs/dev/ledgers/2026-09-02-full-suite-1989c62.md` and outbox `O-14`.
- `2026-09-03-exec-bench-altwide-noedge-ccrerun-1989c62.md` — findings,
  surprises, impact, next steps for `altwide@0.2`'s first sample, the
  raised-cap pair, the `loglines` scan-edge counterfactual, and the
  clang-only `bounded@0.3` re-run, all at pin `1989c62` (abi 15). Each
  finding carries the measured fact, a plain-language mechanism, and what
  it changes. Cites `pcrec-bench`'s ledger
  `docs/dev/ledgers/2026-09-03-altwide-0.2-noedge-ccrerun-1989c62.md`,
  outbox `O-15`, and pcrec's own answer `I-39`.
- `2026-09-05-exec-bench-b37-denysplit-after-334fd10e.md` — the [B37]
  deny-flag AFTER at pin `334fd10e` (abi 22): a dedicated "big win,
  explained" section on the [ENG-ISL] alternation island (Frank's ask),
  an ahead/behind table vs PCRE2's JIT, then findings, surprises, impact,
  next steps. Cites `pcrec-bench`'s ledger
  `docs/dev/ledgers/2026-09-05-b37-denysplit-after-334fd10e.md`, outbox
  `O-17`, and pcrec's own answer `I-50`. Published as an artifact page
  the same day.

Maintenance: update this file when files are added or removed.

- `2026-09-23-optloop-cycle1-exec-summary.md` — the optimization loop's
  CYCLE 1, end to end (memory `pcrec-exec-summary-after-bench-reports`,
  written after the bench's O-45 ledger): the analysis's five mechanisms
  and the caps view, the profile pass, batch 1's landing (abi 28→29,
  three axes), the ledger (39 of 41 target rows meet the bar), and the
  four surprises — 16 "regressions" on artifacts whose program text did
  not change, the pre-check emitted above the free check that decides the
  call, one artifact running the same `memchr` twice, and four
  regressions 111×-60,674× larger than the mechanism's own work. Carries
  the recommended per-mechanism dispositions for Frank and what cycle 2
  already has in flight. Cites `docs/dev/optloop/cycle1_ledger_reading.md`
  for every derivation.
- `2026-09-23-optloop-cycle2-batch2-exec-summary.md` — the optimization
  loop's CYCLE 2 BATCH 2, end to end (memory
  `pcrec-exec-summary-after-bench-reports`, written after the bench's
  O-49 ledger): `[OPT-FREQPICK]` MEETS (`nested-comment-rec` 9.3 ms →
  23.1 µs on 4/4, predicted to 0.2% of its absolute value) and
  `[OPT-REQPOS]` tier 2b's targets meet while its carve-out clause
  FAILS (the run loop costs one `memchr` call per occurrence of its
  scan byte, not of the run — a 124× amplification on
  `router-prefix-order`). Of I-95's 17 missing target rows: 6 removed
  by the unmerged admission fix, 6 the run mechanism's own defect, 5
  already at the floor before the batch started. Three surprises, each
  a prediction whose sign or scope was wrong before measurement — the
  ledger's largest movement (a 500× floor jump) was listed as a gain
  by the design note; the named no-decline-rule falsifier is
  `^`-anchored and loses its entire pre-check under the fix, so it
  cannot answer the question it was chosen for; the admission fix's
  own one-byte dominance rule declines the cheap form of a pre-check
  and admits the expensive one. Recommends merging
  `[OPT-PRECHECK-ADMIT]` as a precondition on shipping the pick, a
  cycle-3 row for the run-form dominance rule, and I-102/I-103/I-104
  to the bench. Cites `docs/dev/optloop/cycle2_batch2_reading.md` for
  every derivation.
- `2026-09-27-utf8-bench-exec-summary.md` — pcrec-bench's NEW `bench/utf8@0.1`
  set, first sample at pin `ce658cb7` (abi 33, 2026-09-26): pcrec answers
  every row correctly on all four `-e utf8` configs (0 wrong of ~33K rows,
  matched only by `pcre2-utf-interp`/`-jit`); every other engine's wrong
  answer is a documented Script-vs-Script_Extensions/case-folding/`\B`
  semantics difference (U8-U10). Compile time is dominated by `\p{L}+`/
  `\P{L}+`'s emitted-size retry ladder (70-106 s, already
  `[OPT-RETRY-REUSE]`'s cited evidence, jointly with `[OPT-CLOSURE-CTX]`,
  K67's witness). Of 69 ranked large-subject-throughput patterns, 42
  win, 5 lose ≤×2, 22 lose >×2 (68 win / 1 lose ≤×2 on short-subject
  search) — **REVISED (lane utf8sum2) to split the 22 into ATTRIBUTED
  (10 literal-run patterns, ×2.1-×16 vs rust/re2: the necessary-run scan
  byte was the UTF-8 LEAD byte, the densest byte of the subject's own
  script — already found and fixed as `[OPT-REQRUN-ENC]` abi 38, merged,
  but AFTER this sample so unmeasured; only 4 of the 10 are individually
  named as the fix's witnesses, the other 6 are likely-but-unconfirmed)
  and UNATTRIBUTED (12 patterns: caseless, alternation, two assertions,
  the lookbehind trio, `cls-dot-rep` — no mechanism identified, no fix
  in flight, an attribution read proposed not run)**. A re-measure
  (I-112) is owed once K68 (abi 39) also merges. U11 (libpcre2's own
  Cyrillic-vs-ASCII UTF-8-validation cost) and `alt-cyr-64`'s compile-time
  cliff (settled as a branch-count, not encoding, effect against
  `altwide`'s own ladder) are read as non-actionable/non-defects. Cites
  pcrec-bench's `docs/dev/ledgers/2026-09-26-utf8-0.1-first-ce658cb7.md`
  and its two addenda, the `alt-cyr-64` control read, and pcrec's own
  `docs/dev/plan.md` `[OPT-REQRUN-ENC]`/`[OPT-LITSCAN]`/`[OPT-A]`/
  `[ENG-LOOK]`/`[OPT-RETRY-REUSE]`/`[OPT-CLOSURE-CTX]` rows for every
  derivation.
- `2026-09-28-b108-exec-summary.md` — [B108]'s bench read of pin
  `a32bc86e`: `[OPT-LITSCAN]` S2a (the VM literal run as one compare).
  - The results:
    - 0 answer changes;
    - DFA-null exact;
    - the named FASTER population null or slower on x86;
    - the D119 bar NOT met on it;
    - wins confined to the forced-VM L-sweep;
    - size and acceptance wins.
  - The compile-side attribution: every non-VM function is
    instruction-identical, so the slowdowns are codegen and placement.
  - The unasked ~5.5 ns-per-pass pre-check cost in find-all.
  - Recommends keeping S2a, and filing F5 (the `L >= 3` narrowing, measured
    first) and F6 (the pre-check per-call price).
  - Cites pcrec-bench's ledger `docs/dev/ledgers/2026-09-28-b108-a32bc86e.md`,
    outbox O-64, and `docs/dev/optloop/b108_reading.md`.
- `2026-09-29-b115-findings-tiers-exec-summary.md` — `[FINDINGS-BENCH-TIERS]`'s
  first four-column read (DEFAULT/DECLARED/PROFILED/ORACLE-BEST,
  `loglines@0.1` + `email-specimen@0.2`, scratch tier), plus a short
  second-section addendum on `[CLS-TREE]` S0's ubuntubudu calibration
  (O-76/O-77) — both land in D131 together.
  - The four-column results: DECLARED can mislead (weblog makes `iso-ts`
    ×1.47/×1.84 SLOWER on loglines' own text); PROFILED never measurably
    regresses and wins on three cells; ORACLE-BEST headroom is ~0 on
    loglines and real on email's whole-subject forms (forced-VM ×0.648
    floor / ×0.856 orig vs auto); `--tune` moves the program at only two
    positions, direct evidence for the D131 λ re-proposal.
  - Recommends `[FIND-DOMAIN-CHECK]` (filed) for DECLARED's domain-mismatch
    risk, pulls the email selector gap into `[SEL-COST]`'s queue, and notes
    PROFILED's unattributed `iso-ts` program move in `[LIST-TABLES]`.
    `[FINDINGS-BENCH-TIERS]` itself is closed and archived.
  - The addendum: the pinned five-constant λ table predicted nothing twice
    (member r +0.08 → the refitted per-probe model's +0.98, branch
    mispredicts ~3.9 ns each); no multi-section kit sectioning beats the
    whole-set tables at any measured price; the fair-dispatch CLSPACK
    re-run reverses the byte tier's size argument. Records the D131 λ
    table ruling and `[OPT-CLSPACK]`'s promotion to build.
  - Cites pcrec-bench's ledger
    `docs/dev/ledgers/2026-09-29-b115-findings-tiers-f7f5a143.md`, outbox
    O-74, and `docs/design/cls_tree_design.md` §1.7 + its O-77 addendum.
- `2026-10-03-bench-o79-o82-notes.md` — pcrec's reading of pcrec-bench outbox
  O-79..O-82 at pin `fc719ca4` (abi 50), lane benchnote, numbers re-verified
  against the outbox text: [B117]'s compilee `-O` sweep (-O0 median x2.24 on
  the DFA subset, x3.10 on forced VM), O-80's no-ill-formed-`-e utf8`-cell
  answer to K75, O-81's reseed items (real-text wins x11-x200, 10 syntax
  cells and 3 synthetic cells >5% slower), O-82's A1-A5/Q1-Q12 answers. Lists
  the rows annotated and filed (`[GUIDE-OPT-LEVEL]`, `[BENCH-ASKS-PENDING]`).
  Cites the bench ledgers `2026-10-01-b117-olevel-fc719ca4.md` and
  `2026-10-02-b120-b121-fc719ca4.md`.
- `2026-10-05-bench-o83-round1.md` — pcrec's reading of pcrec-bench outbox
  O-83 (I-127): [OPTLOOP] round 1 on the wide bench at pin `c4c70f2c` (abi
  59), lane o83read. Per change and per regime, in absolute ns/B or ns per
  subject:
  - C3/K82: every alpha magnitude reproduced, plus the regime split the
    bench asked about;
  - C1: the widest mover, net positive;
  - VEDGE/K81: the entry term IS on the bench's `floor` whole-subject
    cells; the named real-scale cells are alpha-only programs;
  - the flagless [CLS-TREE] S2 range respelling (D139's one spelling):
    throughput slower and short search faster, consistently; not a D144
    item-4 violation, but a gap in D139's "measured" clause.

  Also attributes the "new" utf8 movers, and says what moved since the
  first gap report. Cites the bench ledger
  `2026-10-05-b122-round1-wide-c4c70f2c.md` and its sweep.
