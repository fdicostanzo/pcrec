# COMMON brief: critic round spanarms3 (design READINESS re-check, unit L1), 2026-11-08

Read this whole file before anything else. Then your own per-lens prompt.

## Scope mandate (binding)

- Touch ONLY the pcrec and pcrec-bench repositories (/home/pcrec/projects/pcrec,
  /home/pcrec/projects/pcrec-bench), and READ them only: you edit NEITHER repo.
- Your scratch is ONLY your own directory `/var/tmp/pcrec-pcrec/scratch/crit-spanarms3/<lens>/`
  (create it). Never /tmp, never $HOME, never any other directory. Export
  `PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-spanarms3/<lens>` for any script you run.
- Never run `make`, a suite, `scripts/boxqueue`, `scripts/boxlock`, or anything heavy. Single
  compiles of single patterns with the built binary, `gcc` on single generated files, the oracle
  probe, and small python3 scripts (run with `python3 -I`, `nice`) are fine. Budget: at most
  ~1500 pcrec compiles; keep any sweep under ~10 minutes CPU.
- A SABOTAGE PLANT, where cheap, goes in a COPY of the source you make under YOUR dir (e.g.
  `git -C /home/pcrec/projects/pcrec archive 36072b2a0 src lib cli shared memfn Makefile ... | tar -x -C DIR`
  or copy only the files you need and build the one object + link by hand with `gcc`). Never
  edit the review worktree or the main tree. A plant build is one gcc pass, never `make -j` over
  the whole tree (if a plant needs the whole tree rebuilt, `nice make -j2` in YOUR copy is
  allowed ONCE; say so in the file).
- Never `cd` into a `worktrees/` path (a hook blocks it); use absolute paths, `git -C`, or a
  `( cd X && ... )` subshell. Never chain a bare `cd` with other commands.
- Bound any command that could hang with `timeout 20`. Kill nothing except your own PIDs.

## Subject (frozen)

- The design: `docs/design/span_arms.md` **rev 2**, last changed at commit
  `9e879e82cc43f5e3f29dcb24a06231988ae7ecec` (branch lane/spanarms3), merged to main at
  `36072b2a07f2bd8663a9d4edfb4aa84f4b825213` (identical text). Read it with
  `git -C /home/pcrec/projects/pcrec show 36072b2a0:docs/design/span_arms.md`.
  Rev 1 (for diffs): `git -C /home/pcrec/projects/pcrec show f07aaef69:docs/design/span_arms.md`.
- SCOPE OF THIS ROUND: unit **L1 only** (§8's L1 row) and the text it builds on: §2 (the general
  form: pending guards, bound, kept end), §3.7's walk-parameter table (the `look` arm, reach),
  §4.1's E-5 row and the S16 sentence as they hand over to L1, §5.1 (the item), §5.2 (guard rows
  per combinator, T4) including the DEAD column and TOP at reach `[0, maxoff]`, §5.3 (the
  producer; the item combinator in `desc.c`), §5.4's rows L1 changes (A12, A13's L1 half, and any
  row whose L1 cell is not "none"), §5.6's L1 column, §5.7's L1 witnesses, §6 T4, §8's L1 row and
  its depends-on, §9's L1 ledger rows, §10's L1-triggered rows, §12 (the D168 addendum L1 files).
  L2 and L3 are OUT of scope except to judge whether L1 is SEPARABLE from them.
- Its inputs: the two earlier reviews, which you MAY read: `docs/dev/reviews/2026-11-08-r1-spanarms.md`
  (+ dir `2026-11-08-r1-spanarms/`) and `docs/dev/reviews/2026-11-08-r2-spanarms2.md` (+ dir
  `2026-11-08-r2-spanarms2/`), each with "Manager rulings (2026-11-08)" at its end (r2's at
  about line 120). Rev 2's disposition table is its §R2. Those rulings are IN FORCE.
- Parent (client) note: `docs/design/alt_normal_form.md` (version in force: `git show
  36072b2a0:docs/design/alt_normal_form.md`). Also cited: `docs/design/ctx_span.md` (D168's
  producer design), `docs/design/vlookbehind.md`, `docs/design/stream/roadmap.md`; the contract
  `docs/spec/match_api.md` §6.3.7, `docs/spec/facts_listing.md` §4.1, `docs/spec/tuning.md`
  §2.27/§2.28/§2.39; `tests/codegen/reqcube_check.py`.
- Cites: the note cites `file:line` at main `dd2fe2de9`/`c054e38e7`. A BUILD would land on main
  `36072b2a0`. `git diff c054e38e7 36072b2a0 -- src cli lib memfn docs/spec tests` is EMPTY
  (coordinator checked), so every cite should hold at the build tree; one that does not is a finding.
- The BUILD TREE (read-only review worktree, built once at `36072b2a0`):
  `/home/pcrec/projects/pcrec/worktrees/crit-spanarms3`. Its compiler:
  `/home/pcrec/projects/pcrec/worktrees/crit-spanarms3/build/pcrec` (also `build/pcrec-harness`).
  Read source there (`src/facts/req.c`, `desc.c`, `facts.c`, `facts.h`, `facts.def`,
  `src/facts/kinds.c`, `src/core/findings.c`, `internal.h`, `cli/main.c`, ...).
- Rulings: read `docs/dev/decisions.md` and `docs/dev/plan.md` ONLY as frozen, via
  `git -C /home/pcrec/projects/pcrec show 36072b2a0:docs/dev/decisions.md` (and `:docs/dev/plan.md`),
  never the live tree. D168 is at "## D168" (line 9831); also D77, D153, D157, D186, D190.
  Rows: [REQ-LOOKAROUND], [DD-11.5], [DESC-DEAD], [HARNESS-LEVERS], [RUN-POS-SET], [REPEAT-RUN],
  [REQ-EMPTYCAT] (find with `grep -n '^- \[TAG\]'`; long bodies under `docs/design/plan_row_bodies/`).
- The guide: `docs/dev/guide/` (README.md, architecture.md, coding.md, critics.md). Also
  `docs/design/CLAUDE.md` (standing questions).

## Population (the design's own raw evidence, read-only copies)

`/var/tmp/pcrec-pcrec/scratch/crit-spanarms3/population/rev2/` = `docs/dev/lanes/spanarms3_evidence/`
(rev 2's: `oracle1..3.out`, `facts_w.out`, `facts_w2.out`, `facts_extra.out`, drivers `facts.sh`,
`or.sh`). `population/rev1/` = `spanarms2_evidence/`.
- `facts.sh` hardcodes its compiler to the lane's worktree: copy it to your dir and set
  `P=/home/pcrec/projects/pcrec/worktrees/crit-spanarms3/build/pcrec`.
- `or.sh` takes the oracle's dir from `P2PROBE_DIR`: run it with
  `P2PROBE_DIR=/var/tmp/pcrec-pcrec/scratch/crit-spanarms3 bash .../or.sh OPTS PATTERN start:subject ...`.

## Tools (spellings checked by the coordinator at the build tree)

- Facts listing: `build/pcrec --features all -e byte --emit-facts --pattern 'P'` (TSV; field name
  in column 2, value in column 7; `RX_REQ_*` stamps: name col 2, value col 3). Checked on
  `x(?=qr)[pq]r`: `kinds lookaround`, `req_set 114,120`, `req_whole_run none`, `req_byte 120`,
  `RX_REQ_WHY "dominated"`.
- Emitted stamps: `build/pcrec -p rx --features all -e byte -o DIR/a.c --pattern 'P'` then grep
  `RX_DFA_SCAN`, `RX_REQ_WHY`, `RX_REQ_RUN`, `RX_REQ_HANDOFF` in `DIR/a.c`. `-fno-ctx-node` is
  accepted (the `A_LOOK` lowering of a one-character lookaround).
- ORACLE (libpcre2-8 10.46): `/var/tmp/pcrec-pcrec/scratch/crit-spanarms3/p2probe FLAGS PATHEX START:SUBJHEX ...`
  (FLAGS `u i m s x` or `-`; hex via `h(){ printf '%s' "$1" | od -An -tx1 | tr -d ' \n'; }`).
  Prints `OK ncaps` then per subject `M start end` or `N`. Checked:
  `p2probe - $(h '(?<=foo)bar') 3:$(h foobar) 4:$(h foobar)` -> `OK 0` / `M 3 6` / `N`.
- A matcher: `build/pcrec -p rx --emit-main -o DIR/a.c --pattern 'P' && gcc -O1 -o DIR/a DIR/a.c`
  then `DIR/a SUBJECT` (start offset 0 only).
- L1 is NOT BUILT. "Can its witness fail" is tested by APPLYING THE RULE AS WRITTEN and the
  described SABOTAGE (by hand or in a small python model written from the TEXT) to what the build
  tree computes today, plus, where cheap, a real plant in a copy of the source at an EXISTING
  site, recording the observed difference (listing / stamp / answer) correct vs sabotaged.

## Denylist (never read, grep, list or diff these)

- `docs/dev/lanes/spanarms_report.md`, `spanarms2_report.md`, `spanarms3_report.md`, and every
  other `docs/dev/lanes/spanarms*` file EXCEPT the evidence dirs `spanarms_evidence/`,
  `spanarms2_evidence/`, `spanarms3_evidence/`.
- `/var/tmp/pcrec-pcrec/scratch/spanarms*/` (the lanes' scratch), `/var/tmp/pcrec-pcrec/scratch/crit-spanarms/`
  and `crit-spanarms2/` (earlier rounds' scratch: use the committed review dirs instead).
- `/var/tmp/pcrec-pcrec/scratch/crit-spanarms3/.coord/`.
- `docs/dev/reviews/` files about this subject's relatives (`*alt-normal-form*`, `*altcode*`,
  `*span*`) EXCEPT the r1/r2 spanarms reviews named above; the journal `docs/dev/dev_journal.md`,
  `docs/dev/wake.md`, `docs/dev/owner.md`.
- `git log` bodies (subject lines only: `git log --format=%s`), job logs, the box queue
  (`worktrees/.mgr/`, `scripts/boxqueue` state), every other worktree under `worktrees/`
  (especially `worktrees/spanarms*`).
- For any `git grep`, add `':!docs/dev/lanes/spanarms_report.md' ':!docs/dev/lanes/spanarms2_report.md'
  ':!docs/dev/lanes/spanarms3_report.md' ':!docs/dev/dev_journal.md' ':!docs/dev/reviews'`; for
  plain `grep -r` add `--exclude=spanarms_report.md --exclude=spanarms2_report.md
  --exclude=spanarms3_report.md --exclude=dev_journal.md --exclude-dir=reviews --exclude-dir=worktrees`
  (and read the allowed reviews by their paths).

## Output format (binding)

Your findings file DOES NOT EXIST YET: CREATE it as your FIRST action with these headings, then
APPEND each finding the moment you have it, one append per finding (never batch at the end):

    # CRITIC <lens>: spanarms3
    ## Findings
    ## PROBED-AND-HELD

Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command, observed vs expected) or
SUSPECTED (and what would confirm it); severity (answer / speed / size / maintenance / doc /
design); effort; blast radius; the note's § or file:line; and, if it concerns an r2 finding,
which S-id. A finding against a ruled D-row or a manager ruling cites it and argues, or is
dropped. PROBED-AND-HELD lists what you tested that held, with case counts. If you find nothing
in a part, say so under PROBED-AND-HELD.

If your findings-file Write is refused, SendMessage the findings to "crit-spanarms3" at once,
marked relayed. Never route around a refusal.

When done: run
`/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-spanarms3 --deliver /var/tmp/pcrec-pcrec/scratch/crit-spanarms3/<lens>_deliver.txt <lens>`
and end only after it prints DONE (fix what it reports). Final reply: at most 150 words.
