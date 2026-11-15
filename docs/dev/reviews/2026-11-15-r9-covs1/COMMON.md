# COMMON brief — critic round covs1 (CODE mode: the [COVER-CAP] stage-1 build, before landing)

## Scope mandate (binding)
- You may READ only the pcrec repo (/home/pcrec/projects/pcrec, including the review tree
  below) and pcrec-bench (/home/pcrec/projects/pcrec-bench), plus this round dir.
- You WRITE only under YOUR OWN lens directory
  /var/tmp/pcrec-pcrec/scratch/crit-covs1/<lens>/ (findings file, DELIVER file, scratch).
  Nothing anywhere else on the machine. Not /tmp: export `TMPDIR` and `PCREC_TMPDIR` to
  `<lens dir>/tmp` (create it) before running any repo script.
- READ-ONLY: never edit either repo, never commit, never run `make`, any test suite
  (`run_cover.sh`, `run_sabotage_matrix.sh`, harness sections), `scripts/boxqueue`/`boxlock`,
  or any loop over more than your lens's stated compile cap. You MAY run the built compilers
  below on single patterns, `gcc` on their output into your own dir, the run kit, the
  libpcre2 oracle, python3 `-I` scripts, `git -C ... show/diff/grep`. Prefix loops with `nice`,
  bound every command with `timeout 120` or less.
- The box is SHARED with the owner. Stop all probing by 19:45 local time (his evening hold
  starts 20:00): finish your file, then lanecheck. Kill nothing except your own processes, by PID.
- Never `cd` into a `worktrees/` path (a hook blocks it): absolute paths or `git -C`, or a
  `( cd X && ... )` subshell.

## Subject (frozen)
- Branch `lane/covs1`: SUBJECT `65ad7d2263403705695a31fb46c07e5857a06bec`, BASE (merge-base
  with main) `91bae2d987a9c20960d808f605244ac171796870`. The change: `git -C
  /home/pcrec/projects/pcrec diff 91bae2d98 65ad7d226 -- <pathspec excludes below>`.
  Commit subjects only: `git log --format='%h %s' 91bae2d98..65ad7d226` (never bodies).
- What it is: the BUILD of [COVER-CAP] STAGE 1 per `docs/design/cover_cap.md` REVISION 4.1
  (identical on main and the branch; read it in full). The exact cover stretch is read from
  the anchored DFA (`kn_walk`, no `KN_CAP`); the NFA span slice (`src/facts/kset.c`
  `pcrec_span_walk`), `span_facts`, `MkLang`, `PCREC_SPAN_WALK_SUBSETS` are deleted; C15
  `statement-fits`; abi 107 -> 108; a new `cover` section in `--emit-facts`
  (`docs/spec/facts_listing.md`); sabotage rows S3220-S3225 new, S1131/S1136/S1139
  re-anchored, S1149 retired; kitproof cases/floors/answers; re-pins (start-set manifest,
  door-start_bytes floor, recursion identity gate); `scripts/emit_sweep.py` changes.
  THE ROUND'S QUESTION: does the code do what rev 4.1 says, and can its checks fail?
- Code changed: `src/gen/known.c` (most of it), `src/gen/known.h`, `src/gen/emit_dfa.c`,
  `src/core/compile.c`, `src/core/internal.h`, `src/core/limits.def`, `src/facts/{facts.c,
  facts.def,facts.h,facts_derive.h,kset.c,CLAUDE.md}`, `src/dump/facts_dump.c`. Kit constants
  read by C15: grep `MF_WSPAN_POS`, `MF_WREACH`, `MF_MAX_FWD`, `MF_MAX_SPAN_POS` under `memfn/`.
- Evidence job scripts under `docs/dev/lanes/covs1_evidence/` (`common.sh`, `job_*`,
  `predict.py`) are part of the diff: read them ONLY as `git diff 91bae2d98 65ad7d226 --
  'docs/dev/lanes/covs1_evidence/*.sh' 'docs/dev/lanes/covs1_evidence/job_*'
  'docs/dev/lanes/covs1_evidence/predict.py'`. Never any `.log`, report or other file there.

## Built trees (all built by the coordinator; you never build)
- REVIEW TREE = SUBJECT: /home/pcrec/projects/pcrec/worktrees/crit-covs1
  (`build/pcrec`, `build/pcrec-harness`, `build/libpcrec.a`). Grep code here by absolute path.
- BASE tree (git archive of BASE, built): /var/tmp/pcrec-pcrec/scratch/crit-covs1/base
- PLANTED compilers, one per sabotage row, the row's own BEFORE/AFTER applied to a copy of
  the review tree and built: /var/tmp/pcrec-pcrec/scratch/crit-covs1/plants/<ID>/build/
  {pcrec,pcrec-harness} for ID in S3220 S3221 S3222 S3223 S3224 S3225 S1131 S1136 S1139.
  (Each plant dir is a full tree copy: the denylist applies inside it too.)

## Run kit (/var/tmp/pcrec-pcrec/scratch/crit-covs1/kit/; `. kit/env.sh` sets the paths)
- `kit/cmp.sh OUTDIR 'PATTERN' [pcrec args]`: BASE and SUBJECT artifacts under the SAME
  basename (OUTDIR/base/rx.c, OUTDIR/subj/rx.c), each `RX_DFA_SCAN` route, diff line count
  (abi lines dropped). `HARNESS=1` compiles through `pcrec-harness --harness=kit-proof` as
  `tests/kitproof/run_cover.sh` does. = 2 compiles. Put OUTDIR under your lens dir.
- `kit/facts.sh base|subj|<PLANT_ID> 'PATTERN' [-e utf8] [-i]`: SUBJECT/plant: the
  `--emit-facts` `cover` section rows (`encoding why k exact_len sets`); BASE: its
  `span_facts` row. E.g. `facts.sh subj 'ab|abc|ad'` -> `byte cover 2 2 97,[2]`.
- `kit/ans.sh base|subj|<PLANT_ID> FLAGS 'PATTERN' SUBJECT...`: compiles (harness lever;
  `NOHARNESS=1` for plain pcrec), links `tests/kitproof/drv.c`, compares rx_search at every
  startoffset + the find-all loop against libpcre2 10.46; prints `route=` then OK/DIFF per
  subject. FLAGS as cases.tsv: `-`, or letters `i` (caseless), `u` (utf8), `R`
  (-fno-rev-end). Set `ANSDIR=<lens>/tmp` (dir must exist) so its temp dirs land in yours.
- `kit/oracle`: tests/kitproof/oracle.c over libpcre2 10.46 (stdin
  `FLAGS<TAB>PATTERN_HEX<TAB>SUBJECT_HEX`). python3 `re` is fine for base-tier sanity.
- Plain compile: `build/pcrec -p rx --features all [-e utf8] --emit-main -o X.c --pattern P`
  then `gcc -O2 X.c`; `--memfn=no-window-search` denies the cover route.
- For a run that could hang or balloon: `/home/pcrec/projects/pcrec/scripts/watchdog -s 60 -m 2g -c 60 -S <label> -- CMD`.

## Rulings and context (frozen: main `5d0e75680`; read via git show, never the live tree)
- `git -C /home/pcrec/projects/pcrec show 5d0e75680:docs/dev/decisions.md`; owner criteria
  in force: D198 (`## D198`, (a)-(g)). Also cited by the design: D26, D77, D80, D94, D146/D147,
  D157, D174. The branch's own `docs/dev/plan.md` hunks are part of the diff; locate the row
  only by `grep -n '^- \[COVER-CAP\]'` (never print its neighbours).
- Allowed design context: `docs/design/cover_cap.md` (rev 4.1) and its three design reviews
  `docs/dev/reviews/2026-11-15-r5-covcap-r2.md`, `-r6-covcap-r3.md`, `-r7-covcap-r4.md` and
  their sibling dirs. Guide: `docs/dev/guide/` (README.md, coding.md, style.md, critics.md),
  `docs/dev/learnings.md` §3, `docs/design/kit_proof.md`, `docs/spec/facts_listing.md`,
  `docs/spec/match_api.md`, `docs/dev/history/abi_changelog.md`, `tests/kitproof/CLAUDE.md`,
  `tests/mech/CLAUDE.md`, `scripts/CLAUDE.md`.

## DENYLIST (do not open, grep or diff these; exclude them from EVERY grep and diff)
- `docs/dev/lanes/covs1*` (reports, deliver/rulings files, triage, the evidence dir's logs;
  the evidence job scripts only AS DIFF, above), `docs/dev/lanes/covcap*`
- `docs/dev/dev_journal.md`, `docs/dev/wake.md`, `docs/dev/owner.md`
- `docs/dev/reviews/2026-11-15-r2-covcap0*` (file and dir)
- `worktrees/.boxqueue/` (queue and job logs), GitHub Actions logs, `git log` bodies
- every `worktrees/*` other than `worktrees/crit-covs1`
- `/var/tmp/pcrec-pcrec/scratch/` EXCEPT `crit-covs1/`; inside it, `.coord/` and other
  lenses' dirs
- Plain grep exclude string (grep -r does NOT honour git pathspecs):
  `--exclude-dir=worktrees --exclude-dir='covs1*' --exclude-dir=.coord --exclude=dev_journal.md
  --exclude=wake.md --exclude=owner.md --exclude='covs1*' --exclude='covcap*'
  --exclude='2026-11-15-r2-covcap0*' --exclude-dir='2026-11-15-r2-covcap0*'`
  (when grepping the review tree or a plant by absolute path, the start path may contain
  `worktrees`; --exclude-dir only prunes subdirectories, so keep it).
- git pathspec excludes for every diff/grep: `':!docs/dev/lanes/covs1*'
  ':!docs/dev/lanes/covcap*' ':!docs/dev/dev_journal.md' ':!docs/dev/wake.md'
  ':!docs/dev/owner.md' ':!docs/dev/reviews/2026-11-15-r2-covcap0*'`

## Output format
Your findings file is `<lens dir>/<lens>.md`; your DELIVER file `<lens dir>/<lens>_deliver.txt`
exists. The findings file does NOT exist yet: CREATE it as your FIRST action with headings
`# <LENS> — covs1`, `## Findings`, `## PROBED-AND-HELD`, then APPEND each finding the moment
you have it, ONE APPEND PER FINDING. Each finding:
- id `<LENS>-n`; CONFIRMED (repro: input, command, observed vs expected) or SUSPECTED (what
  would confirm it); severity (answer / speed / size / maintenance / doc / design); effort;
  blast radius; cite (`file:line` at the review tree, or design §).
- A finding against a ruled D-row, owner criterion or design-review disposition cites it
  and argues, or drops.
- PROBED-AND-HELD at the end: what you tested that held, with case counts.
- If your findings-file Write is refused, SendMessage your findings to the coordinator
  (`crit-covs1`) at once marked "relayed"; never route around a refusal.
- When done, run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir
  /var/tmp/pcrec-pcrec/scratch/crit-covs1 --deliver <your DELIVER file> <lens>` and end only
  once it prints DONE. Final reply at most 150 words.
