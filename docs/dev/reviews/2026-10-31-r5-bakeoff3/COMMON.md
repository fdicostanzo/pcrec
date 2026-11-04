# COMMON brief: critic round `bakeoff3` (design mode, a SHORT third RE-CHECK), 2026-10-31

You are one critic in an adversarial review of a REVISED design document. Read this whole file
before your lens prompt's question. Your lens prompt gives you a NARROW question; stay on it. This
round checks only three items (below); anything else you notice goes in ONE "outside scope" line at
the end of your findings, not a finding.

## Scope mandate (binding)

- Touch ONLY the pcrec repo (`/home/pcrec/projects/pcrec`) and pcrec-bench
  (`/home/pcrec/projects/pcrec-bench`), and BOTH READ-ONLY.
- No edits, commits, branches, worktrees, `git stash` or `git checkout` in either repo. Read other
  revisions with `git -C /home/pcrec/projects/pcrec show <rev>:<path>`.
- Your only writable place is your own directory `/var/tmp/pcrec-pcrec/scratch/crit-bakeoff3/<lens>/`
  (named in your lens prompt). Never write to `/tmp`. Never `cd` in a compound command; use absolute
  paths and `git -C`.
- NEVER run `make`, any test suite, any timing (`perf`, the bench, grid1/grid2 `time.sh` or drivers,
  `scripts/measure.sh`), `scripts/boxlock`, `scripts/boxqueue`, or any compile sweep. The box is
  shared with the owner.
- Allowed execution: small python3 scripts of your own, run as `python3 -I`, and the design's
  evidence scripts (below), which are pure computation. Monte Carlo is fine; keep each run under a
  few minutes of one core (`nice`). Never kill a process you did not start.
- Never read PCRE2 source (D181).

## The subject (frozen)

- Design: `docs/design/pricing_bakeoff.md` **rev 2** (PROPOSED) on branch `lane/bakeoff`, frozen at
  branch tip `ed772fd7169691febb7d33dc9bff255fd3b287bd` (the doc was last changed in `b6380a4d5`).
- Exported copies, in the repo's own layout so the scripts find each other (identical to `git show`):
  `/var/tmp/pcrec-pcrec/scratch/crit-bakeoff3/subject/` containing
  - `docs/design/pricing_bakeoff.md` (~1,720 lines; THE SUBJECT);
  - `docs/design/pricing_bakeoff_verdict.tsv` (the DECLARED verdict file; rendered into §9.3);
  - `docs/dev/lanes/bakeoff3_evidence/`: `verdict_table.py` (loader/renderer), `verdict_drill.py`
    (+ `.out`, 45 scenarios), `check_verdict_table.py` (+ `check.out`, `check_plants.out`),
    `power.py` (+ `power.out`);
  - `docs/dev/lanes/bakeoff2_evidence/` (rev 1's evidence, for comparison).
  Copy the evidence tree into your own dir before modifying or planting anything. The scripts accept
  `BAKEOFF_VERDICT_TSV=<path>` for an alternate TSV, and `check_verdict_table.py [DESIGN.md]`.
  **`check_verdict_table.py --plants` writes a temp dir under `$PCREC_TMPDIR/scratch/bakeoff3/`, a
  DENIED directory**: run it only as
  `mkdir -p <yourdir>/ptmp/scratch/bakeoff3 && PCREC_TMPDIR=<yourdir>/ptmp python3 -I <copy>/check_verdict_table.py --plants`.
- Rev 1 (what round 2 reviewed): `git -C /home/pcrec/projects/pcrec show deebb4dd8:docs/design/pricing_bakeoff.md`.
  Diff: `git -C /home/pcrec/projects/pcrec diff deebb4dd8 b6380a4d5 -- docs/design/pricing_bakeoff.md`.
- What it is: the design of an EXPERIMENT (a bake-off) deciding where search-strategy PRICING lives
  (pcrec front end, backend `src/gen`, or the memfn kit `memfn/`): candidate placements are decision
  rules simulated over shared measured constants, graded by regret against a measured, forced-path
  timing oracle on held-out sites, read through pre-registered first-match verdict tables, now
  declared as ONE data file (the TSV) that the drill evaluates and the text renders.
- **This is the third round.** Round 2's draft review is an INPUT:
  `/var/tmp/pcrec-pcrec/scratch/crit-bakeoff2/review.md` (findings X1-X35 with proposed
  dispositions, ruled as proposed) and its `review/` dir (critic texts, `verify.md`). Rev 2's §14 maps
  each X id to its answer. Do not re-raise a round-2 finding that rev 2 really fixed; DO raise one
  whose fix does not hold, saying which X id.
- The three items this round checks, and nothing else:
  1. **X2, one regret scale throughout** (§0 "Words", §5.4, §7.1, and wherever a statistic or a
     threshold is defined): is any statistic or threshold still on another scale, and can a pair's
     order still flip between the scale the margin/rows are argued on and the one a test reads?
  2. **X25, the drill and the declared file**: does `verdict_drill.py` implement exactly what the TSV
     declares, with no special-casing? Does `check_verdict_table.py` catch a disagreement between the
     text and the file (plant your own, beyond its three)? Do the core power figures re-derive
     independently (equivalence power at H-core; the winner threshold of about 18-20 differing
     sites; the stage-0 floor of 50)? Do the TAIL step's rows (§7.5, the TSV's tail rows) give the
     right answer on cases of your own?
  3. **The grid decision**: §5.1's table (grid2 chosen over grid1) and its "What grid2 costs us"
     paragraph, against `memfn/` and the kit's grid docs.
- The owner's bar: this decision is core; the evidence must be clear and trustworthy.
- Build tree for code citations: main HEAD `a3cc4de82230daa1904a2166228191f210a6604b` = the branch's
  merge base (the branch changes no code). Read code and docs in `/home/pcrec/projects/pcrec`
  (main's checkout; do not modify it). A cited file:line that does not match main HEAD is a finding.

## What you may read

- The guide: `docs/dev/guide/` (README.md, architecture.md, critics.md, addenda/);
  `docs/design/CLAUDE.md` (the three standing measurement questions); `docs/dev/learnings.md` §3;
  `docs/dev/decisions.md` (D-rows the design cites).
- The harnesses and kit: `docs/dev/lanes/grid1/`, `docs/dev/lanes/grid2/` (README.md, scripts,
  evidence; READ only, never run `time.sh`, drivers or `build.sh`), the grid lanes' reports
  (`docs/dev/lanes/grid1_report.md`, `grid2p_report.md`, `grid2r3_report.md`, `grid2read_report.md`,
  `gridread_report.md`), `docs/design/memfn/regime_eval.md` and the rest of `docs/design/memfn/`,
  `memfn/` (its CLAUDE.md, docs/, data/cards/, data/sets/, src/), `measure_store/`,
  `docs/spec/measures.md`.
- pcrec-bench READ-ONLY: its docs and `testees/pcrec/`.

## Denylist (do not open, grep, list or summarize; if a search result lands in one, skip it)

- `docs/dev/lanes/bakeoff_*`, `bakeoff2_*`, `bakeoff3_*` (lane reports, rulings, deliver files),
  EXCEPT the evidence directories `bakeoff2_evidence/` and `bakeoff3_evidence/` (use the copies under
  `subject/`). The design restates the rulings it applies; read the restatements.
- `/var/tmp/pcrec-pcrec/scratch/bakeoff*/` (every lane scratch dir, including `bakeoff3/`) and
  `scratch/bakeoff_review*/`.
- Every earlier round's `process.md` and `.coord/` (`scratch/crit-bakeoff/`, `scratch/crit-bakeoff2/`);
  this round's `/var/tmp/pcrec-pcrec/scratch/crit-bakeoff3/.coord/` and `process.md`, and the OTHER
  critic's directory in this round.
- `docs/dev/wake.md`, `docs/dev/owner.md`, `docs/dev/dev_journal.md` entries dated 2026-10-31.
- Any message between sessions; the box queue and its state; job logs; `git log` BODIES (subject
  lines only, `--format=%s`); other worktrees under `worktrees/`.

## Output format

Your directory exists with a `DELIVER.txt`. **`findings.md` does NOT exist yet: you CREATE it**,
early, and write it INCREMENTALLY (append each finding as you confirm it).

    # <LENS> findings: bakeoff3 (pricing_bakeoff.md rev 2 @ ed772fd71)
    ## Findings
    ### <LENS>-1 <one-line title>
    - status: CONFIRMED | SUSPECTED
    - severity: answer | speed | size | maintenance | doc | design
    - effort: small | medium | large (to fix in the design)
    - blast radius: what the defect would do to the bake-off's verdict if unfixed
    - where: design § (and file:line at main HEAD or in the evidence scripts); the round-2 X id
    - finding: what is wrong, in plain words
    - repro: CONFIRMED needs one: input, command (or grep/read/arithmetic), observed vs expected.
      SUSPECTED says what would confirm it.
    - proposed fix: one or two lines
    ## PROBED-AND-HELD
    - what you checked that held, each with a case count

Severity for a design: `answer` = the experiment would reach a WRONG verdict; `design` = it cannot
reach a verdict, or the verdict would not be trustworthy; `doc` = wording/cites. A finding against a
ruled D-row or ruling cites it and argues, or is dropped. A value the design marks CHOSEN is fair game
only with a shown consequence, not a preference. Keep scripts and their outputs in `<yourdir>/work/`.

Finish: run
`/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-bakeoff3 --deliver /var/tmp/pcrec-pcrec/scratch/crit-bakeoff3/<lens>/DELIVER.txt <lens>`
and fix what it reports until it prints `lanecheck: DONE rc=0`. Then END with a final reply of at
most 150 words (the file is what counts; the reply may be lost).
