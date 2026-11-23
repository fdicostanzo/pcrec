# COMMON brief: critic round r79 memfn-bsu5 (code mode)

Read this whole file first. Then your own lens prompt.

## Scope mandate (binding)

- Touch only the pcrec and pcrec-bench repositories. Write ONLY under your own
  directory `R=/var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu5/<lens>/` and your
  findings file `$R/../<lens>.md`. Nothing else on this machine, ever.
- READ-ONLY: no edits to either repo, no commits, no `make`, no suites
  (`make test*`, `run_finder.sh`, `run_sabotage_matrix.sh`, mech, batteries),
  and NO TIMING of any kind. Never run `cards.py` in any mode except `plan`
  and `dry` (`dry` only into a RUNDIR under your own directory, at most ONCE,
  `JOBS=2 nice`, with `--cards C6,C6c`; prefer the round's finished dry below).
  You MAY `python3 -I` import `cards.py` and call its pure functions
  (`cells`, `regimes_of`, `subject`, `check_c6`, `arm_flags`, `C6_RULE`, ...);
  never `time_cells`, `run_cell` timing paths, `cmd_run`, `cmd_rerun`,
  `cmd_c3`, `cmd_identity`, `cmd_rule` on timed data.
- Box: shared with other work. Wrap anything that might be long in
  `timeout`. Never take `scripts/boxlock`, never `boxqueue`. Kill nothing.
- Compile budget: at most ~300 `pcrec` compiles and ~60 `gcc`/`clang` compiles
  per critic (a BASE/SUBJECT pair counts 2).

## Subject

- SUBJECT = branch `lane/bsu5` = `28b2da326b7592cb021683f079183812360c6190`.
- BASE = `git merge-base lane/bsu5 lane/memfn-k1108` =
  `b51fd80bd27d813f668bf6aed280d80e54866de2` (NOT main's merge-base; the kit
  branch is ahead of main). Diff: `git -C /home/pcrec/projects/pcrec diff b51fd80bd 28b2da326 -- <paths> <EXCLUDES>`.
- What it is: unit U5 of the kit's request R-47 (the block span "V" at the SIMD layer):
  - card C6 `span_vector` and its clang sibling C6c in `memfn/tests/span_forms/cards.py`;
  - the `kit-grid@8` row in `memfn/data/cards/kit-grid.tsv` (UNMEASURED);
  - a new formhash SHAPE `MF_FH_SPAN`, its renderer and one entry `span-vector`
    (`memfn/src/formhash.c`, struct field `k` in `memfn/src/kit.h`), with
    `tests/memfn/arm_fixtures.c` and `tests/memfn/finder_check.py` rows;
  - sabotage row S2930 re-aimed (`tests/mech/sabotages/S2930_formhash_two_ids_one_text.sh`).
- The author's claims under test (each lens takes the ones its prompt names):
  1. U5 moves no emitted byte or stamp (no abi event). [The coordinator checked
     this inline: do not re-spend budget on it unless your lens finds a path.]
  2. Card C6 times exactly the trade §8 states (the shipped V vs
     `--memfn=no-span-vector` on ONE binary), with the stated patterns,
     widths, regimes and rule clauses.
  3. The A/A arm can fail.
  4. The formhash entry stales when the V text changes, and does not stale otherwise.
  5. The clang card's compiler column is a declared column, not a parallel mechanism.
  6. Nothing is timed.

## Design of record and rulings (read the FROZEN copies)

- `R/subject/block_span.md` (read-only copy of `docs/design/memfn/block_span.md`
  at SUBJECT): §8 (the card), §14's U5 row, §10.2's "At U5" note, §3.1 (what k
  is), §0.1 (the 3 real sites), §2.2.1 (owner question wrap-clang), §12.
  Quote it by section; it is the contract U5 is reviewed against.
- Job 710's decision rule, which §8 adopts with listed clauses:
  `R/decision_rule_710.md` (read-only copy of the kit scratch file
  `scratch/memfn/blockconfirm/decision_rule.md`) and `R/meta_710.json` (its run's meta, `rule_sha`).
- Rulings: read via `git -C /home/pcrec/projects/pcrec show 28b2da326:docs/dev/decisions.md`
  and `...:docs/dev/plan.md`, never the live tree (main's copies are identical at the freeze).
  - D201 addendum 5 (decisions.md, the line beginning `- **Addendum 5 (Frank, 2026-11-21, to the kit`),
    quoted verbatim: "wrap-clang: a. Policy is inline wrappers where possible so this is a move towards that. The wrapper is a separate fix to an out of policy coding not related to the simd change / That said, do track the clang issue with an item for follow-up to make sure no surprises".
  - plan row `[BSPAN-CLANG-DIFF]`: locate it ONLY by `grep -n '^  - \[BSPAN-CLANG-DIFF\]'` on the
    `git show` output and read that row's own 5 lines; never print its neighbours.
  - D155 item 2, D144 addendum 4 as §8 cites them (grep decisions.md for `## D155`, `## D144`).
- Guide: `docs/dev/guide/` (coding.md, architecture.md, style.md, critics.md) in the review tree.
- The ONE lens that verifies the owner's quote word for word against the record: SLOT. Others cite without re-checking.

## Trees and the run kit

- Review tree (SUBJECT, built): `/home/pcrec/projects/pcrec/worktrees/crit-memfn-bsu5`
  (`build/pcrec`, `build/pcrec-harness`, `build/libpcrec.a`). Read code there or with
  `git -C ... show 28b2da326:path`. Never `cd` into it in a chained command (a hook
  blocks it); use absolute paths or a `( cd X && ... )` subshell.
- BASE tree (git archive, built clean): `$RD/base` where `RD=/var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu5`.
- `$RD/kit/run.sh TREE BIN [args..]`: TREE = `base` | `subject` | `plant:<ID>`; BIN =
  `pcrec` | `pcrec-harness` | `fx` (the `tests/memfn/arm_fixtures.c` driver linked to
  that tree's libpcrec.a; e.g. `run.sh subject fx --hash` prints every FORM / FORMCLS hash).
  Example: `$RD/kit/run.sh subject pcrec -p rxa --features all --window-search-width=32 -fmemfn-simd=x86-64-v3 -o $R/x.c --pattern '[0-9a-f]{32}'`
  Pass patterns in SINGLE quotes or via a file; check the `Pattern:` header of every
  emitted file you cite. Compare BASE/SUBJECT emitted C under the SAME basename in two
  dirs (the C names its basename).
- Plants (assigned to the CHECK lens only; others may read but not plan new ones):
  `$RD/plants/<ID>/tree` (SUBJECT + one source edit, rebuilt; the edit is in
  `$RD/kit/build_plants.sh` and `$RD/kit/build_plants2.py`), each with its `fx`:
  - `S2930`: the row's own SAB_BEFORE -> SAB_AFTER.
  - `PV32`, `PV16`: identifier-only edits in `vs_w32_block` (`"_mm256"`->`"_mm256X"`; `"_mm"`->`"_mmX"`).
  - `PBODY`: `wf_span_v_define`'s `__body` return wrapped in parentheses.
  - `PV32b`, `PV16b`: `vs_w32_block`'s loop line, `<` -> `<=` only where the block width b is 32 / only where b is 16.
  The coordinator ran `tests/memfn/run_finder.sh` on SUBJECT and on S2930, PV16b, PV32b, PBODY:
  logs in `$RD/finder/*.log` (do NOT re-run it).
- The finished partial dry (`cards.py dry --cards C6,C6c`, JOBS=2) : `$RD/dry/dry.out`, its
  RUNDIR `$RD/dry/run` (artifacts `art/`, built exes `bin/` with their `.c` TUs). `cards.py plan`'s
  output: in `$RD/dry/plan.out`. Read them; do not write into `$RD/dry/`.
- Regimes (cards.py `REGIMES` + C6's `near-miss-in`), widths (`--window-search-width=32|4095`),
  layers (`on` = `-fmemfn-simd=x86-64-v3`; `off-clang` = no SIMD flag, built by clang).
  clang is `/usr/bin/clang` (21.1.8), gcc 15.2.0.

## Denylist (D27 for review): EXCLUDED from EVERY read, git diff and grep

- `docs/dev/lanes/bsu5*` (the lane's report; it sits in the review tree too);
- every file or directory under `docs/dev/reviews/` whose name contains `memfn-bsu` or `memfn-bspan`;
- `memfn/docs/journal.md`, `memfn/docs/responses.md`, `memfn/docs/wake.md`;
- every worktree except `worktrees/crit-memfn-bsu5` (in particular bsu5, memfn, u4tip, bsu4*);
- `$PCREC_TMPDIR/scratch/bsu5/` and every other scratch dir except this round's `$RD`
  (the 710 rule is provided as `$RD/R/` copies); `$RD/.coord/`; other critics' dirs and files in `$RD`;
- `git log` bodies beyond subject lines; job logs; the box queue.
- The same paths inside `$RD/base/` are denied too.
- Git excludes to append to EVERY `git diff` / `git grep`:
  `-- . ':!docs/dev/lanes/bsu5*' ':!docs/dev/reviews/*memfn-bsu*' ':!docs/dev/reviews/*memfn-bspan*' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md' ':!memfn/docs/wake.md'`
- Plain grep excludes: `--exclude='bsu5*' --exclude='*memfn-bsu*' --exclude='*memfn-bspan*' --exclude-dir='*memfn-bsu*' --exclude-dir='*memfn-bspan*' --exclude=journal.md --exclude=responses.md --exclude=wake.md`

## Output format

- Your findings file `$RD/<lens>.md` ALREADY EXISTS (pre-created with its headings
  `## Findings` and `## PROBED-AND-HELD`). APPEND to it (Edit, or `cat >>`); never
  overwrite it with Write (the harness refuses a subagent's whole-file Write).
  Append each finding the MOMENT you have it, one append per finding.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command, observed vs
  expected) or SUSPECTED (what would confirm it); severity (answer / speed / size /
  maintenance / doc / design); effort; blast radius; file:line or §. A finding against
  a ruled D-row cites it and argues, or drops.
- State the minimum witness size your probes reached where it matters (pattern k, subject length).
- End the file with PROBED-AND-HELD entries (what you tried that held, with case counts),
  then a last line `CRITIC COMPLETE`.
- Then run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir $RD --deliver $RD/<lens>.deliver <lens>`
  and end only when it prints DONE (fix the file's form if it does not).
- Final reply at most 150 words. A failed final reply is EXPECTED for a nested agent and needs
  no escalation: the CRITIC COMPLETE line in your file is the delivery. If your findings-file
  append is REFUSED, SendMessage your findings to the coordinator at once, marked relayed.
