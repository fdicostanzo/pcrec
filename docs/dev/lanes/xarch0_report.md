# xarch0 — [XARCH] STEP 0 lane report

2026-09-05, lane xarch0, Sonnet, Mac-local. Charter: docs/dev/plan.md
[XARCH]. Full memo: `docs/dev/xarch_step0.md`, evidence:
`docs/dev/xarch_step0_evidence/`.

## What shipped

- Half 1 (compile rates): a full-corpus `tests/size/run_size_log.sh` run
  in worktree `xarch0a`, pinned at commit `81731547` (the committed size
  log's own commit), joined against the committed Linux log by
  `(pattern, engine)`. 2,925 rows in common (0 only-Mac, 37 only-Linux,
  all from four assertions files at that WIP-commit's own 751 pre-existing
  test failures). **0 size_bytes movers — byte identity holds perfectly.**
  gcc CPU-seconds ratio Mac÷Linux: median 0.518 (Mac ~1.93x faster CPU-wise),
  flat across engine (DFA 0.518, VM 0.519). Wall ratio 0.468, caveated
  load-contaminated both sides. Reaffirms [TT-14]: spawn tax, not compute.
- Half 2 (matcher throughput), pcrec built at the bench's pin `334fd10e`:
  - **THE HOOK**: `floor` forced-VM at `--vm-entry-shape=1/2/3` on ARM.
    `forward` ties `plain` here (ratio 0.996–1.004) — does NOT reproduce
    the x86 ledger's ×2.0 `forward`-shape regression, confirming
    o17facts's I-50 §2 hypothesis that it's a gcc-15.2/x86-specific
    inline-merge cost. NEW finding: `shared` is the ARM outlier instead,
    ~3x slower than both other shapes — not predicted by either side.
  - Altwide `w-8`/`w-64`/`w-256`, vm+auto: Mac 0.49–0.72x on forced-VM
    (faster), 1.07–1.10x on DFA/auto for the two wider rungs (slightly
    slower), all within a normal architecture-difference band (nothing
    near 5x).
  - Bounded `cls-upto-4/32/1024` + `dig-upto-16` dispatch cells: Mac
    ~3–4.5x faster on the `cls-upto` failed-dispatch cells (two runs
    disagreed by up to 35% with each other — flagged as likely
    P-core/E-core scheduling noise at nanosecond scale, not corrected
    for), `dig-upto-16` very stable at ~2.1x faster.
  - Loglines `iso-ts`: INCONCLUSIVE — used a synthesized subject (did not
    reproduce the bench's own loglines subject tooling in the time
    available), showed the OPPOSITE sign from the bench's pinned ratio;
    flagged as a subject-mismatch artifact, not a finding, needs re-run
    with the bench's real corpus.

## Deliberately not done (see memo's own section)

No JIT column, no clang column, no formal Half-2 byte-identity check
(Half 1's already establishes it at this pin's sibling state), no
investigation of the WIP commit's 751 pre-existing test failures beyond
noting they explain the Half-1 row-count gap.

## Process notes for whoever reads this next

- The box's load1 was very high (18.17 → 9.60, decaying) at session
  start with no visible heavy process and no HOLD/lock artifact found —
  read as a fading spike from something already finished, not a live
  conflict. Documented in memo §4 rather than acted on further.
- `zsh`'s word-splitting bit twice: an unquoted multi-path shell variable
  built with `"$S/x $S/y ..."` collapses to ONE argument under zsh
  (unlike bash) — every subject-path argument list in the evidence
  scripts is passed as individually-quoted arguments, never assembled
  into one variable first.
- Nanosecond-scale single-process timing on this chip needs an internal
  warmup+multi-trial design (see `match_driver.c`), not external
  process-level interleaving — process launch overhead dominated the
  first attempt at the bounded cells by two orders of magnitude.

## Commits

All on branch `lane/xarch0`, not merged, not pushed. Files: memo,
evidence directory, this report, CLAUDE.md updates for `docs/dev/` and
`docs/dev/lanes/`. `plan.md` deliberately left untouched — the manager's
call per the brief.
