# COMMON brief — critic round sar1 (code), 2026-11-09

Read this whole file first, then your own lens prompt.

## Scope mandate (binding)

- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and pcrec-bench, and only READ them.
- Scratch ONLY under your own dir `/var/tmp/pcrec-pcrec/scratch/crit-sar1/<your-lens>/` (create it).
  Never /tmp. Never write anywhere else on the machine.
- READ-ONLY: no edits to either repo, no commits, no worktrees of your own. NEVER run `make`
  anywhere, and never run a suite (make test, test-axes, harness batteries,
  run_sabotage_matrix.sh, mech, run_facts_checks.sh). Probe single patterns with the built binaries.
- The box is shared and queue jobs are running: run every compile/probe under `nice`; no -j above 2.
  Budget: about 800 pattern compiles per critic (a BASE/SUBJECT pair counts as 2).
- Kill nothing you did not start. Never `pkill -f`.

## Subject (frozen)

- Branch `lane/sar1`, SUBJECT = `79619852e8015945273b8cb0835dfe3d56f2976c`.
- BASE = `c17a1272294cdb17720bd1ae8d08f38e82e0c0c3` (lane/sae1 at the point sar1 branched from it:
  unit E1, reviewed separately; later commits on lane/sae1 are NOT part of this subject).
  Diff: `git -C /home/pcrec/projects/pcrec diff c17a12722 79619852e -- . ':!docs/dev/lanes'`
  (22 files; core: `src/facts/req.c`, `src/facts/desc.c`/`.h`, `src/facts/walk_arms.def`).
- What it is: unit R1 of `docs/design/span_arms.md` under decision D191. A repeat counts as its
  copies: T2 rows 2-3 as rows of E1's first-match table `rb_rep_rows` (`rr_pow_count`, `rr_pow`,
  `rr_rep_exact`, `rr_rep_split`, `rb_rep_exact_into`, `rb_rep_split_into` in req.c);
  `X{m,n}` read as `X^c` then `X{0,n-m}` for head and best and the reverse for the tail; `maxw`
  exact (`rr_rep_w`); the piece description's power `pcrec_pd_pow` (desc.c); the restore arm
  `rep` (`--harness=restore=rep`, build/pcrec-harness only); witnesses in
  `tests/litscan/spanarms.rxt`; `[facts-rep]` in `tests/codegen/run_facts_checks.sh`; sabotage rows
  `tests/mech/sabotages/S1915..S1921_*.sh`; two re-aimed witnesses (`S463_handoff_k_minus_one.sh`'s
  reach, and the VM attempt-loop entry witness in `tests/memfn/run_handoff_reach.sh`); axes arm and
  lever fence (`tests/axes/run_axes.sh`, `tests/compound/run_lever_fence.sh`); spec hunks
  `docs/spec/tuning.md` §2.28¶3, `docs/spec/facts_listing.md` 4.1.2 para 8c (lane/sar1) and 4.1.3 para 4a (lane/sar1).

## Rulings already made (the manager's; not findings — you may report CONSEQUENCES, not argue them away)

1. Two §3.4 predicted-mover cells tie the other way and are ACCEPTED as the walk's one tie rule:
   `xy(?:ab){2,3}zw` lists `ababzw` (the design predicted `xyabab`), `xy(?:ab)+zw` lists `abzw`
   (predicted `xyab`).
2. Under `-e utf8`, `(a.){10}xyz`'s `req_pieces` now reads `decline:over-bound` where BASE read
   `decline:not-fixed-width` (both value `none`); accepted as an advisory listing mover. (The
   contract lens is asked separately whether the reason order tells the truth.)
3. Known shared gap, OUT OF SCOPE: the restore lever does not reach compound parts (being fixed
   elsewhere). Do not report it.

## Rulings and design — read the FROZEN versions only

- Design: `git -C /home/pcrec/projects/pcrec show 90ab55fd3:docs/design/span_arms.md`.
  R1's parts: §3 whole (3.1 rule and six points, offsets [K82], 3.2 owner, 3.3 readers, 3.4
  predicted movers, 3.5 answer identity, 3.6 witnesses W-R1..W-R6, 3.7 walk-parameter table and
  lever rule, 3.8), §6 (T1, T2), §8 row R1 and its gates, §12, §12b.
- Decision: `git show 90ab55fd3:docs/dev/decisions.md`, section `## D191` (line 10119). Plan rows by
  tag only: `git show 90ab55fd3:docs/dev/plan.md | grep -n '^- \[REPEAT-RUN\]\|^- \[HARNESS-LEVERS\]'`
  (read only the row lines you locate, never their neighbours).
- Guide (what critics review against): `docs/dev/guide/README.md`, `coding.md`, `architecture.md`,
  `style.md`, `critics.md` (read from the review tree).
- Spec (review tree): `docs/spec/facts_listing.md` §4.1, `docs/spec/match_api.md` §6.3.7,
  `docs/spec/tuning.md` §2.27, §2.28, §2.39, §2.41.
- Earlier DESIGN reviews of span_arms (`docs/dev/reviews/2026-11-08-r*`) are allowed context.

## Trees and tools (already built; do NOT rebuild)

- Review tree (SUBJECT): `/home/pcrec/projects/pcrec/worktrees/crit-sar1/` with `build/pcrec`
  and `build/pcrec-harness`. Never `cd` into it in a compound command; use absolute paths or
  `(cd X && ...)` subshells. Call it S below.
- BASE tree: `/var/tmp/pcrec-pcrec/scratch/crit-sar1/base-tree/` (a `git archive` export of
  c17a12722, built: `build/pcrec`, `build/pcrec-harness`). Call it B below.
- Sabotage builds (prebuilt by the coordinator, read-only for you): each plant of S1915..S1921 and
  S463 applied to a copy of SUBJECT and built: `/var/tmp/pcrec-pcrec/scratch/crit-sar1/plants/S19xx/`
  (`build/pcrec`, `build/pcrec-harness`, `PLANT_STATUS` = occurrences of the BEFORE text and the
  build rc). These may still be building when you start; wait (poll 2 min) for the dir you need.
- Constructs like backrefs and lookarounds need `--features all`.
- Emitted C: `S/build/pcrec --features all -p rx -o DIR/rx.c --pattern 'P'`, then
  `grep -E 'define RX_(REQ_(RUN|WHY|HANDOFF|BYTE)|DFA_SCAN|VM_PREFILTER|DFA_PREFILTER) ' DIR/rx.c`.
  Compare BASE/SUBJECT emitted C under the SAME basename (`-p rx`, `rx.c`) in two dirs.
- Regimes (both checked to compile): default (shipped prior) and `-e utf8` (no rate). Caseless `-i`.
  Engines: `--engine=vm` / `--engine=dfa` (default auto).
- Facts listing: `S/build/pcrec --features all --emit-facts --pattern 'P'` (TSV: encoding, fact,
  ..., value, why, ...). Restore lever: `S/build/pcrec-harness --features all --harness=restore=rep
  --emit-facts --pattern 'P'` (writes the `harness:rep` why).
  Example: `xy(?:ab){2}zw` gives `req_whole_run` 7879616261627a77 on S, 6162 on B.
- ANSWER ORACLE TOOL: `/var/tmp/pcrec-pcrec/scratch/crit-sar1/tools/cmp1.sh TREE 'PATTERN' 'P2OPTS'
  'PCREC_OPTS' START:SUBJECT ...` with `CMP_DIR=<your dir>/cw` set. It compiles with
  TREE/build/pcrec (pcrec-harness if PCREC_OPTS contains --harness), runs `rx_search` on each
  ASCII/UTF-8 subject from START, and prints per subject `SAME|DIFF  subj  pcrec=M s e [cap
  spans...]|N  pcre2=...` against libpcre2 (P2OPTS letters: u=UTF i=CASELESS m s x; "" for none).
  Captures are compared in full. Example:
  `CMP_DIR=$D/cw .../tools/cmp1.sh S 'x(a(b))\1{2}y' '' '' 0:qxabababy` -> `SAME ... M 1 9 2 4 3 4`.
  Raw oracle: `.../tools/p2probe OPTS PATHEX START:SUBJHEX ...`.
- `.rxt` format: `docs/spec/rxt_format.md`.

## Denylist (never read, never grep into; exclude from EVERY git diff and grep)

- `docs/dev/lanes/sar1*` and `docs/dev/lanes/sae1*` (reports, evidence dirs, deliver files).
  Git: add `':!docs/dev/lanes'` to every diff/log/grep pathspec. Plain grep: `--exclude-dir=lanes`.
- `docs/dev/full_suite_ledger.md`, `worktrees/.boxqueue/`, `worktrees/sar1/`, `worktrees/sae1/`,
  `worktrees/sae2/` and every other worktree except `worktrees/crit-sar1/`,
  `/var/tmp/pcrec-pcrec/scratch/sar1/`, any queue/job log.
- `memfn/docs/journal.md`, `memfn/docs/responses.md` (grep: `--exclude=journal.md --exclude=responses.md`).
- Reviews of E1/R1 code: `docs/dev/reviews/2026-11-09-r3-sae1*` and `/var/tmp/pcrec-pcrec/scratch/crit-sae1/`.
- `git log` message BODIES (subject lines only: `git log --format='%h %s'`).
- The round's coordinator notes `/var/tmp/pcrec-pcrec/scratch/crit-sar1/.coord/` and other critics' dirs.
- Sabotage files' `SAB_DOC_FIGURE` lines point at a denied report: do not follow them.
- `census_r1.py` (the lane's census model, if you meet it): denied.

## Output format

Your findings file DOES NOT EXIST YET. As your FIRST action create it with these headings:

    # <lens> — crit-sar1
    ## Findings
    ## PROBED-AND-HELD

Then append EACH finding the moment you have it, one append per finding. Each finding:
- id `<LENS>-n`; CONFIRMED (with a repro: input, exact command, observed vs expected) or
  SUSPECTED (what would confirm it);
- severity: answer / speed / size / maintenance / doc / design;
- effort (small/medium/large), blast radius, file:line or design §;
- a finding against a ruled D-row or a ruling above cites it and argues, or is dropped.
PROBED-AND-HELD lists what you tested that held, with case counts.

If your findings-file Write is REFUSED, SendMessage your findings to the coordinator at once
(marked "relayed"); if a harness rule refuses it, return the findings as your final text instead.

When done, run
`/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-sar1 --deliver /var/tmp/pcrec-pcrec/scratch/crit-sar1/<lens>.deliver <lens>`
and end only once it prints DONE. Final reply at most 150 words.
