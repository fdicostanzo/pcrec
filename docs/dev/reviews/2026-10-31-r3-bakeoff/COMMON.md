# COMMON brief: critic round `bakeoff` (design mode), 2026-10-31

You are one critic in an adversarial review of a DESIGN document. Read this whole file before your
lens prompt's question. Your lens prompt gives you ONE question; stay on it.

## Scope mandate (binding)

- Touch ONLY the pcrec repo (`/home/pcrec/projects/pcrec`) and pcrec-bench
  (`/home/pcrec/projects/pcrec-bench`), and pcrec-bench READ-ONLY.
- You are READ-ONLY on both repos: no edits, no commits, no branches, no worktrees, no `git stash`,
  no `git checkout`. Use `git show <rev>:<path>` and `git -C <dir>` to read other revisions.
- Your only writable place is your own directory under `/var/tmp/pcrec-pcrec/scratch/crit-bakeoff/`
  (named in your lens prompt). Never write to `/tmp`. Never `cd` in a compound command; use absolute
  paths.
- NEVER run `make`, any test suite, any timing (`perf`, the bench, grid1, `scripts/measure.sh`,
  benchmark drivers), `scripts/boxlock`, `scripts/boxqueue`. The box is shared with the owner and
  with timing runs.
- Allowed execution: the PREBUILT compilers of the review tree, single compiles, each under
  `gnutimeout 30 nice ...`; `--list-axes`, `--explain`, `--emit-facts` and the like; `gcc -S`/`-c` of a
  generated file; small python3 scripts of your own (run with `python3 -I`) that read files or
  drive compiles. Keep any compile sweep to at most ~300 compiles in total, run sequentially and
  niced. Never kill a process you did not start (`scripts/safekill PID` only, never `pkill -f`).
- Never read PCRE2 source (D181). libpcre2 as a library you call is fine, but you should not need it.

## The subject (frozen)

- Design: `docs/design/pricing_bakeoff.md` rev 0 (PROPOSED) on branch `lane/bakeoff`, frozen at
  commit `a7b229f3ff19ac046f3a00a44cb88dac8578c04d`. Read the exported copy
  `/var/tmp/pcrec-pcrec/scratch/crit-bakeoff/pricing_bakeoff_a7b229f3f.md` (identical to
  `git show a7b229f3f:docs/design/pricing_bakeoff.md`). It is ~950 lines; read all of it.
- What it is: the design of an EXPERIMENT (a bake-off) that decides where search-strategy PRICING
  lives: the pcrec front end, the backend (`src/gen` today) or the memfn kit (`memfn/`). Each
  candidate placement is simulated as a decision rule over shared measured constants and graded by
  regret against a measured, forced-path timing oracle on held-out sites. It also designs the
  per-box re-measure command and per-architecture measurement sets that feed it.
- The owner's bar: this decision is core, so the evidence must be clear and trustworthy. The
  round's overall question: can the experiment, as designed, actually DECIDE the question, and
  would its numbers be trustworthy?
- Build tree for code citations: main HEAD `a3cc4de82230daa1904a2166228191f210a6604b`, which is
  also the design's base (the branch changes no code). A clean review tree at that commit:
  `/home/pcrec/projects/pcrec/worktrees/crit-bakeoff/` (read code there), with
  - `worktrees/crit-bakeoff/build/pcrec` (the default compiler) and
  - `worktrees/crit-bakeoff/build-trace/pcrec` (the same sources built with
    `-DPCREC_CAND_TRACE`, the "trace build" the design's levers would live in).
  Do NOT build anything; both already exist. Any code the design cites that does not match the
  review tree at the cited line is a finding.

## What you may read

- The guide the round reviews against: `docs/dev/guide/` (README.md, architecture.md, coding.md,
  style.md, critics.md, addenda/).
- `docs/design/CLAUDE.md` (the three standing measurement questions); `docs/dev/learnings.md` §3
  (how checks fail); `docs/dev/decisions.md` (the D-rows the design cites: D35, D77, D146, D147,
  D153, D156, D157, D158, D161 and addenda, D166 and addenda, D172, D174, D176, D177, D181, D182,
  D183, and any other).
- The inputs the design cites:
  - the split study: `worktrees/splitstudy/docs/dev/lanes/splitstudy_report.md` (rev 1; this ONE
    file under that worktree is allowed);
  - review 1 of it: `/var/tmp/pcrec-pcrec/scratch/crit-pricing-split/review.md` and its `review/`
    dir and critic dirs; review 2: `/var/tmp/pcrec-pcrec/scratch/crit-pricing-split2/` (review.md,
    review/, critic dirs);
  - the kit's pricing requirements rev 1:
    `git -C /home/pcrec/projects/pcrec show 90d5150f7:docs/design/memfn/pricing_requirements.md`
    ("PR"); the price survey report on the same commit
    (`git show 90d5150f7:docs/dev/lanes/pricesurvey_report.md`, "PS") if present;
  - the stop-ranking study ("SRS"):
    `git show lane/memfn-stopstudy:docs/design/memfn/stop_ranking_study.md`;
  - `docs/design/memfn/regime_eval.md`, `docs/design/memfn/walk_vs_v1_record.md`,
    `docs/design/locate_finish.md`, `docs/dev/lanes/grid1/README.md`,
    `docs/dev/lanes/armread_report.md`, `docs/dev/lanes/rwquest_report.md`,
    `docs/dev/lanes/rwquest/questions.tsv`;
  - `measure_store/` (with its CLAUDE.md), `docs/spec/measures.md`, `docs/design/measure_sets.md`;
  - `src/`, `memfn/`, `lib/pcrec.h`, `scripts/` (including `scripts/emit_sweep.py`,
    `scripts/compile_time_census.py`, `scripts/run_axes.sh` / `tests/axes/`),
    `tests/codegen/run_form_census.sh`, the `.rxt` corpus under `tests/`;
  - the real-world corpus `worktrees/.corpus/` (data; read-only, list and sample it);
  - pcrec-bench READ-ONLY: `testees/pcrec/configs.toml`, `testees/pcrec/CLAUDE.md`,
    `docs/methodology.md`, `docs/design/gate_shape_v14.md`, its harness docs and CLAUDE.md files.

## Denylist (do not open, grep, list or summarize; if a search result lands in one, skip it)

- `docs/dev/lanes/bakeoff_*` (the lane's report AND its rulings file `bakeoff_rulings.md`; the
  design restates what it applies from them; read the restatements, never the file).
- `/var/tmp/pcrec-pcrec/scratch/bakeoff/` (the lane's probes; re-run any probe you want to check
  yourself with the review tree's compiler).
- `/var/tmp/pcrec-pcrec/scratch/crit-bakeoff/.coord/` and every OTHER critic's directory in this
  round (`/var/tmp/pcrec-pcrec/scratch/crit-bakeoff/<other lens>/`).
- `docs/dev/wake.md`, `docs/dev/owner.md`, `docs/dev/dev_journal.md` entries dated 2026-10-31.
- Any message between sessions; the box queue (`scripts/boxqueue`, its state files); job logs.
- `git log` BODIES (subject lines only, `git log --format=%s`); other worktrees under `worktrees/`
  except the review tree `worktrees/crit-bakeoff/`, the one splitstudy report above, and the
  `worktrees/.corpus/` data.

## Output format

Your lens prompt names your directory `/var/tmp/pcrec-pcrec/scratch/crit-bakeoff/<lens>/`, your
findings file `<lens>/findings.md` and your DELIVER file `<lens>/DELIVER.txt`. The directory and
DELIVER file exist; **`findings.md` does NOT exist yet: you CREATE it**, early, and write it
INCREMENTALLY (append each finding as you confirm it; never hold everything for the end).

`findings.md` shape:

    # <LENS> findings: bakeoff (pricing_bakeoff.md @ a7b229f3f)
    ## Findings
    ### <LENS>-1 <one-line title>
    - status: CONFIRMED | SUSPECTED
    - severity: answer | speed | size | maintenance | doc | design
    - effort: (to fix in the design) small | medium | large
    - blast radius: (what the defect would do to the bake-off's verdict if unfixed)
    - where: design § (and file:line in the review tree where code is involved)
    - finding: what is wrong, in plain words
    - repro: CONFIRMED needs one: the input, the command (or the grep/read/arithmetic), observed vs
      expected. SUSPECTED says what would confirm it.
    - proposed fix: (one or two lines)
    ### <LENS>-2 ...
    ## PROBED-AND-HELD
    - what you checked that held, each with a case count (e.g. "12 cited line ranges: all match")

Severity for a design: `answer` = the experiment would reach a WRONG verdict (picks the wrong
placement, or reads PASS where it should not); `design` = it cannot reach a verdict, or a verdict
would not be trustworthy; `doc` = wording/cites; `maintenance`/`speed`/`size` as usual.
A finding against a ruled D-row cites the D-row and argues against it, or is dropped. A design
choice the doc marks CHOSEN is fair game only if you show a consequence, not a preference.

Finish: run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-bakeoff --deliver <your DELIVER.txt> <lens>`
and fix what it reports until it prints `lanecheck: DONE rc=0`. Then END with a final reply of at
most 150 words (the file is what counts; the reply may be lost).
