# Lane clscand: report (2026-10-16, opus, measurement only)

Branch `lane/clscand` off main `353249282` (abi 78). Nothing under `src/`, `cli/`,
`lib/` or `tests/` changed. Deliverable: `docs/dev/clsmask_candidates.md` plus
`docs/dev/clsmask_candidates/` (scripts, `CLAUDE.md`, `results/`). Also added: an
entry in `docs/dev/CLAUDE.md`.

## Summary (a resuming agent starts here)

- **Population.** 5,283 pattern keys: corpus 4,816, bench 344 (pcrec-bench
  `25480b47`, read-only `git archive` copy), rwquest 173, ref ipv4 1. Each was compiled
  under auto and `--engine=vm`.
  - VM-routed: 2,199 auto, 4,883 forced.
  - Instrumented and run: 2,179 / 4,863. The 20 per config that were not are all
    `tests/vars/*`, whose `rx_search` signature the driver does not speak.
  - 0 timeouts, and 0 unwrapped subject reads.
- **Validation PASS** (`results/validation.txt`).
  - Two hand-counted controls are exact.
  - The cross-check against walk_survey's ASan load instrument is exact: 120 cells,
    0 mismatches.
  - The sabotage control (`CS_SABOTAGE=drop-range`) was detected on 4/4 live witnesses.
- **Headline.**
  - The `\w`-token family leads: `(\w+) \1` and friends, auto = VM, score ~4,400.
    These patterns have an expensive class, runs, re-visit 2.7-4.5, block coverage ≈ 0.9,
    and a shared start mask.
  - Next come line runs (`(?m)^.{400,}$`, `(?m)^(?!.*\bINFO\b).*$`), then hex/digit spans.
  - ipv4 is a good illustration but a mediocre candidate:
    - under auto the VM makes 0.011 tests/B;
    - under forced VM it ranks 83/475, carried mostly by the shared start-skip term.
  - Under forced VM, the attempt loop's start skip makes more class tests than the
    program (0.48 vs 0.33 per byte on real patterns).
- **Timing candidates.** T1 `(\w+) \1`, T2 `(?m)^(?!.*\bINFO\b).*$`, T3
  `(?m)^.{400,}$`, T4 `loglines/ipv6`, T5 ipv4.

## Validation run here

- `docs/dev/clsmask_candidates/validate.py build/cs 40` gave VERDICT PASS.
- The full chain is `run_all.sh`. Its stages were run individually on this box at CPUs
  0-3 / 4 jobs; the instrumented run took about 40 minutes.
- No `make test`: nothing the suite reads changed.

## Notes and caveats

- One check-design lesson, recorded in the memo §3. The first sabotage control counted
  range sites that the panel never evaluates, and read 1/2. The witness set must be the
  sites that are live in the intact run.
- I ran the first validation draft on CPUs 4-5 by mistake. Every later run, including
  the committed one, used 0-3.
- Side findings, not filed:
  - ipv4's inner `\d{1,3}` (3 of 4 run sites) is not possessified, although `\d` and
    `\.` are disjoint;
  - utf8 classes never reach a run site.
