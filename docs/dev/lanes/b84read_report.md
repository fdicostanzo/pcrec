# Lane b84read — delivery report (2026-09-25, opus)

**Task.** Read pcrec-bench's [B84] ledger / O-52, the acceptance of the
`[OPT-PRECHECK-ADMIT]` fix at `6ef76820`, against our I-102. Answer five
questions in order: the new give-up; (c)'s 3/4; per-cell grid verdicts; the
29-cell G2 list; FREQPICK/REQPOS dispositions.

**Branch** `lane/b84read` from `4080ee34`. Nothing under `src/`/`cli/`/
`lib/`/`tests/`; nothing written in pcrec-bench (its `git status` stayed clean
throughout). One light probe was run on the 10.46 reference box (`pcre2test`,
6 subjects).

## Deliverables

- `docs/dev/optloop/cycle2_admitfix_reading.md`: the reading, findings first.
- `docs/dev/optloop/admitfix/`: `cells.py`, `nullctl.py`, `nullband.py`,
  `score.py`, `giveup_repro.sh`, `steps_driver.c`, committed JSON/tables,
  transcripts, and its own `CLAUDE.md`.
- `docs/dev/known_issues.md` **K64**: the give-up, with the proposed fix. Not
  built.
- `docs/dev/optloop/CLAUDE.md` entry; `docs/dev/lanes/CLAUDE.md` entry.

## The five answers (resume from here)

1. **Give-up = a DEFECT IN THE FIX, and an OLD OUTCOME RETURNING.**
   - Reproduced exactly on darwin: `6ef76820`, `--features all --engine=vm`,
     5/75 subjects `-2` at 500,000,001 steps. `b1885a83` answers all 75.
   - The same 5 gave up identically at `25b1984f` (batch-1 BEFORE). Batch 1's
     `memchr('@')` cured them by accident, and G2 removed it. They are the
     only pass/fail changes across 4 pins × 1,992 cells.
   - Mechanism: `^([a-zA-Z0-9._%+-]+)+@`'s one attempt costs `3·2^(L−2) − 2`
     steps over a class run, so the budget is exhausted at L = 30. The auto
     route is linear (an exact hybrid DFA, or a DFA).
   - `tuning.md` §2.29's two G2 sentences are false for a step-budgeted
     backtracking VM. The give-up is contract-legal (`limits.md` §1).
   - PCRE2 10.46 answers these subjects: its req-code-unit check applies to
     anchored patterns under 5,000 bytes, and the boundary was measured.
   - Fix A (recommended): G2's VM arm declines only for an exact hybrid or a
     frameless program. It costs 6 forced-VM throughput cells, back to
     `b1885a83`. Fix C, the pre-check as the step budget's first refill, is
     the general follow-on and is D77-gated.
2. **(c) vm-in-caps +1.84% is null.**
   - The artifact is program-identical, `REQ_WHY emitted`, and has no
     candidate-start scan.
   - `vm-caps` moved −0.25% on the same build, and the band is +6.75%.
   - I-102(c) over-scoped this cell: it should have been a control.
3. **Grid.** This pin pair's own null band covers 394 cells on 146
   program-identical artifact-configs.
   - (a) 4/4, (b) 8/8, (d) 8/8 meet; (c) 2/2 on the cells the mechanism can
     reach.
   - (f)/(g), the six meeting targets: 6/6 within band, program-identical.
   - (h): 8/8 within band, program-identical.
   - (b) forced-VM 7,207 ns: predicted 6,525-7,600 from 826 counted VM steps
     at 7.9-9.2 ns/step, solved from 20 subjects in the same record.
4. **29 G2 cells itemized.** The count cited the BATCH-1 LEDGER's
   §1.2/§2.1/§2.2, not the reading's sections.
   - 27/29 improve and 2/29 sit within the band: (e) MET.
   - The 72-superset's 16 band regressions and 2 give-ups are batch 1's
     search-regime pre-check wins given back: DFA route within ±3.4% of
     `25b1984f`, forced VM still 75-100% faster.
   - The inbox text is ready in reading §4.1 (numbered I-106 if nothing has
     landed since I-105).
5. **Dispositions.**
   - FREQPICK: default-on, precondition met.
   - REQPOS 2b: default-on stands. The router/keyword residual (+82.8% /
     +69.4% over `25b1984f`, DFA) goes to [OPT-LITSCAN] under D122's
     "dominated pre-check is ELIDED" clause, plus the forced-VM
     `json-array-begin` pair (+15/16%) as the pre-check-as-prefilter case.
   - PRECHECK-ADMIT: stays started until K64's fix lands.

## Validation

- Analysis lane: no suite was run.
- Every ledger number this reading cites was re-derived from the bench's own
  records with the bench's own reducer, and matches to the printed digit.
- The 29-row table in the reading was machine-checked against `score.json`.
  That check caught 2 mistyped values, now corrected.
- `giveup_repro.sh` was re-run end to end from a clean scratch tree:
  subjects 75/75 + 3/3 sha-match, rc histograms as tabled.

## For the manager

- K64 is the next free K. `lane/varfollow` and `lane/varland` stop at K63.
- The fix lane (A) owes the `tuning.md` §2.29 hunk and a sabotage row: the
  witness `a`×40 under `--engine=vm`, answer-detectable.
