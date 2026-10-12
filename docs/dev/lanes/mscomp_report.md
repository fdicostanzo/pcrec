# mscomp — [COMPOSITE] design note, first client [MATCH-SPLIT] (2026-10-12, opus)

Branch `lane/mscomp` from main `a080c69a` (abi 76). Design only: nothing under `src/`,
`tests/`, `docs/spec/`. Deliverable: `docs/design/composite.md`, with its evidence in
`docs/design/composite/twin/` (own CLAUDE.md). `match_split_pinonly.md` is marked
SUPERSEDED, and both notes are registered in `docs/design/CLAUDE.md`.

## Commits
- `a784027a`: the split twin (differential, counted loads, one-TU probe, sizes).
- `fb2d780a`: the design note, the SUPERSEDED marker and the registration.
- This report.

## Measurements (light, as the brief allowed; no clock, no make test)
- **Differential** (`twin/results/split_differential.tsv`). Hand-composed composite =
  plain-compiled parts `\G(?:P)` + Q (anchors textually killed) + hand controller. It ran
  over 94 cases (mssurvey's 79 floor-mixed rows plus hand witnesses), every startpos, plus
  find-all. Result: **0 differences vs today, 0 vs libpcre2 10.46, over 1,416,556 cells.**
- **D163's literal controller** (Q searched from `from`) is wrong on 3 of 94 cases, the
  atomic/possessive floor arms (`(?>^a|ab)c` on "abc" gives (0,3); P and libpcre2 find no
  match). See `split_differential_literal.tsv`.
- **Leaving `\G` in Q** gave 1,344 and 1,442 wrong cells on gpos.rxt:453/470. That first run
  caught it; the kill was fixed and the run repeated.
- **Counted loads** (`split_loads.tsv`, the survey's qdrv.c instrument):
  - trim `Q·\t^16000·Q`: 128,040,002 → 3.
  - wrapper: n+3 attempt entries → 1.
  - concat-sqli: 0.25-0.33× today.
  - trailing run + final `\n`: **3.00× today**. This is Q's rev-end two seeds plus the tie,
    i.e. the panel's B1 cost.
- **One-TU probe:** two self-contained parts plus a controller compile clean under the
  harness `-Werror` flags. Static-without-omission fails with 13 errors.
- **Sizes**, linked with gc-sections: trim 3.0×, wrapper 2.3×, concat-sqli 1.15×.
- **Route probe:** the unpruned kill `[^\x00-\xff]\s+|\s+$` routes `unanchored`, while the
  pruned `\s+$` routes `rev-end`.
- **Admission count**, exact from `ms_rows.tsv.gz`: 56 floor-mixed + 9 floor-only patterns
  in the first (DFA-only) build. Bench 2 (concat-sqli ×2), corpus 24, idioms 30.

## Findings (note §I)
1. D163's controller must search Q from `next_pos(floor)`, not from `from`.
2. Killing `\G` in Q is required. Killing `^`/`\A` is a route optimization only.
3. The derivation must prune dead arms: the facts are not dead-path aware.
4. [EMIT-ENTRIES]'s row misreads `nentries`, which counts `groups[]` rows.
5. A composite's `_match` becomes one attempt; today's attempt-route `_match` filters a whole
   attempt loop.
6. The floor-only composite covers mssurvey finding 6's start half (9 patterns).
7. The panel's 3× final-newline cost is confirmed by count, and it belongs to rev-end (B3).
8. One-TU composition is already clean under `-Werror`. The only hazard is linkage, which B0
   solves.

## Build plan (note §F)
- **B0:** EMIT-ENTRIES internal. Zero movers, no abi.
- **B1:** part mode.
- **B2:** the derivation hook and the split kill/prune.
- **B3:** [OPT-REVEND] one-pass two-seed walk. Its own abi event; it gates G3.
- **B4:** composite driver and split client. Abi event, bit 55.
- **B5:** VM parts, on ruling.
- **B6:** the cross-call hook with [FINDALL-NEXT].

## For Frank (note §G)
- **Q1:** record the next_pos(floor) correction as a D163 addendum.
- **Q2:** B3 before B4 (leaning yes).
- **Q3:** VM parts and D158 (leaning DFA-only first).
- **Q4:** `"composite"` route values.
- **Q5:** default ON.

## Resuming
A follow-up lane starts from `composite.md` §0 and §F. The twin reproduces with the two
commands in `docs/design/composite/twin/CLAUDE.md`. Nothing is owed: no long run was
launched. A D6 panel on the note is the expected next step.

## Rulings received
None. No `mscomp_rulings.md` appeared during the run.
