# COMMON brief: critic round `bakeoff2` (design mode, a RE-CHECK), 2026-10-31

You are one critic in an adversarial review of a REVISED design document. Read this whole file
before your lens prompt's question. Your lens prompt gives you ONE question; stay on it.

## Scope mandate (binding)

- Touch ONLY the pcrec repo (`/home/pcrec/projects/pcrec`) and pcrec-bench
  (`/home/pcrec/projects/pcrec-bench`), and BOTH READ-ONLY.
- No edits, commits, branches, worktrees, `git stash` or `git checkout` in either repo. Read other
  revisions with `git -C /home/pcrec/projects/pcrec show <rev>:<path>`.
- Your only writable place is your own directory
  `/var/tmp/pcrec-pcrec/scratch/crit-bakeoff2/<lens>/` (named in your lens prompt). Never write to
  `/tmp`. Never `cd` in a compound command; use absolute paths and `git -C`.
- NEVER run `make`, any test suite, any timing (`perf`, the bench, grid1's `time.sh`/drivers,
  `scripts/measure.sh`), `scripts/boxlock`, `scripts/boxqueue`, or a parallel compile sweep. The box
  is shared with the owner and is running a heavy queue job now.
- Allowed execution: single compiles with main's PREBUILT compiler
  `/home/pcrec/projects/pcrec/build/pcrec`, each as `gnutimeout 30 nice ...` (run sequentially,
  at most ~100 in total); `gcc -S`/`-c` of one generated file; small python3 scripts of your own,
  run as `python3 -I`, and the design's evidence scripts (below), which are pure computation.
  No trace (`-DPCREC_CAND_TRACE`) build exists for this round: a claim that needs one is SUSPECTED,
  with what would confirm it. Never kill a process you did not start (`scripts/safekill PID` only).
- Never read PCRE2 source (D181).

## The subject (frozen)

- Design: `docs/design/pricing_bakeoff.md` **rev 1** (PROPOSED) on branch `lane/bakeoff`, frozen at
  commit `deebb4dd85a2c1f136cdd0dcf840065afc7ef970`. Exported copies (identical to `git show`):
  - `/var/tmp/pcrec-pcrec/scratch/crit-bakeoff2/subject/pricing_bakeoff_rev1_deebb4dd8.md` (~1,390
    lines; THE SUBJECT; read all of it);
  - `.../subject/pricing_bakeoff_rev0_a7b229f3f.md` (rev 0, what review 1 reviewed);
  - `.../subject/rev0_to_rev1.diff` (the revision as a diff);
  - the design's evidence, from `docs/dev/lanes/bakeoff2_evidence/` at the same commit:
    `.../subject/verdict_drill.py` (+ `verdict_drill.out`), `census_dry.py`,
    `census_dry_summary.txt`, `census_dry_sites.tsv`. Copy a script into your own dir before running
    it if it writes anything; run python as `python3 -I`.
- What it is: the design of an EXPERIMENT (a bake-off) deciding where search-strategy PRICING lives
  (pcrec front end, backend `src/gen`, or the memfn kit `memfn/`): every candidate placement is a
  decision rule simulated over shared measured constants and graded by regret against a measured,
  forced-path timing oracle on held-out sites, read through two pre-registered first-match verdict
  tables (§9.3).
- **This is a RE-CHECK.** Rev 0 went through critic round 1. Its draft review, critic texts and
  verifier file are INPUTS: `/var/tmp/pcrec-pcrec/scratch/crit-bakeoff/review.md` and its
  `review/` dir (`premise.md`, `simulate.md`, `measurement.md`, `cost.md`, `verify.md`). The
  dispositions there were ruled as proposed. Rev 1's §14 maps each finding id (B1-B25, MEAS-19)
  to where rev 1 answers it. The round's question: does each claimed fix HOLD, and what did the
  fixes INTRODUCE?
- The owner's bar: this decision is core; the evidence must be clear and trustworthy.
- Build tree for code citations: main HEAD `a3cc4de82230daa1904a2166228191f210a6604b` (the design
  says every code cite is at that commit; the branch changes no code). Read code in
  `/home/pcrec/projects/pcrec` (main's checkout; do not modify it). Any cited code that does not
  match main HEAD at the cited line is a finding.

## What you may read

- The guide: `docs/dev/guide/` (README.md, architecture.md, coding.md, style.md, critics.md,
  addenda/). `docs/design/CLAUDE.md` (the three standing measurement questions);
  `docs/dev/learnings.md` §3 (how checks fail); `docs/dev/decisions.md` (D-rows the design cites).
- The design's inputs: `worktrees/splitstudy/docs/dev/lanes/splitstudy_report.md` (this ONE file
  under that worktree); its review rounds `/var/tmp/pcrec-pcrec/scratch/crit-pricing-split/` and
  `crit-pricing-split2/` (review.md, review/); the kit's pricing requirements rev 1:
  `git -C /home/pcrec/projects/pcrec show 90d5150f7:docs/design/memfn/pricing_requirements.md`
  ("PR"); `docs/design/memfn/regime_eval.md`; `docs/dev/lanes/grid1/` (README.md and its scripts:
  read only, never run `time.sh`); `measure_store/`, `docs/spec/measures.md`,
  `docs/design/measure_sets.md`; `src/`, `memfn/`, `lib/pcrec.h`, `scripts/`, `tests/` (read);
  the stop-ranking study `git show lane/memfn-stopstudy:docs/design/memfn/stop_ranking_study.md`.
- pcrec-bench READ-ONLY: its docs (`docs/`, `docs/dev/`, `docs/design/`), `testees/pcrec/`, its
  CLAUDE.md files and harness sources.

## Denylist (do not open, grep, list or summarize; if a search result lands in one, skip it)

- `docs/dev/lanes/bakeoff_*` and `docs/dev/lanes/bakeoff2_*` (lane reports, rulings files), EXCEPT
  the evidence directory `docs/dev/lanes/bakeoff2_evidence/` (use the copies under `subject/`).
  The design restates the rulings it applies; read the restatements, never the rulings file.
- `/var/tmp/pcrec-pcrec/scratch/bakeoff/`, `scratch/bakeoff2/`, `scratch/bakeoff_review1/`,
  `scratch/bakeoff2_bench_answers.md`.
- `/var/tmp/pcrec-pcrec/scratch/crit-bakeoff/process.md` and `crit-bakeoff/.coord/`; the critic
  directories of round 1 OTHER than its `review/` copies are fine to read but add nothing.
- This round's `/var/tmp/pcrec-pcrec/scratch/crit-bakeoff2/.coord/` and every OTHER critic's
  directory in this round.
- `docs/dev/wake.md`, `docs/dev/owner.md`, `docs/dev/dev_journal.md` entries dated 2026-10-31.
- Any message between sessions; the box queue and its state files; job logs; `git log` BODIES
  (subject lines only, `--format=%s`); other worktrees under `worktrees/` except the one
  splitstudy report.

## Output format

Your directory exists with a `DELIVER.txt`. **`findings.md` does NOT exist yet: you CREATE it**,
early, and write it INCREMENTALLY (append each finding as you confirm it).

    # <LENS> findings: bakeoff2 (pricing_bakeoff.md rev 1 @ deebb4dd8)
    ## Findings
    ### <LENS>-1 <one-line title>
    - status: CONFIRMED | SUSPECTED
    - severity: answer | speed | size | maintenance | doc | design
    - effort: small | medium | large (to fix in the design)
    - blast radius: what the defect would do to the bake-off's verdict if unfixed
    - where: design § (and file:line at main HEAD where code is involved); the review-1 id it
      concerns, if any (B-n)
    - finding: what is wrong, in plain words
    - repro: CONFIRMED needs one: input, command (or grep/read/arithmetic), observed vs expected.
      SUSPECTED says what would confirm it.
    - proposed fix: one or two lines
    ## PROBED-AND-HELD
    - what you checked that held, each with a case count

Severity for a design: `answer` = the experiment would reach a WRONG verdict; `design` = it cannot
reach a verdict, or the verdict would not be trustworthy; `doc` = wording/cites. A finding against a
ruled D-row or a ruled review-1 disposition cites it and argues, or is dropped. A value the design
marks CHOSEN is fair game only with a shown consequence, not a preference. Do not re-raise a review-1
finding that rev 1 really fixed; DO raise one whose fix does not hold, saying which id.

Finish: run
`/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-bakeoff2 --deliver /var/tmp/pcrec-pcrec/scratch/crit-bakeoff2/<lens>/DELIVER.txt <lens>`
and fix what it reports until it prints `lanecheck: DONE rc=0`. Then END with a final reply of at
most 150 words (the file is what counts; the reply may be lost).
