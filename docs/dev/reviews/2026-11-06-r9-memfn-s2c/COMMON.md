# COMMON brief — critic round memfn-s2c (CODE mode), 2026-11-06

You are a READ-ONLY critic in an adversarial code review of the memfn kit's unit **S2c, "the producer"**
(span_pick stage 2, kit request R-35). Read this whole file before your lens prompt's question.

## Scope mandate (binding)

- Touch ONLY the pcrec and pcrec-bench repositories, and READ them only. You edit NOTHING in either repo
  (no file writes, no git commands that write: no commit/checkout/stash/worktree/branch/merge).
- Your only writable place: your own dir `R/<lens>/` and your findings file, where
  `R=/var/tmp/pcrec-pcrec/scratch/crit-memfn-s2c`. Run every probe with `PCREC_TMPDIR=$R/<lens>` set.
  Never write under /tmp, $HOME, or anywhere else.
- NEVER run `make` (any target), `make test`, any suite, `scripts/boxqueue`, `scripts/boxlock`, timing jobs, or
  the slot harness's REAL runs (`run.py run`, `run.py screen`). Never queue box jobs.
- ALLOWED: `build/pcrec` / `build/pcrec-harness` compiles of single patterns; `gcc -S` / `gcc -c` / linking small
  drivers into your dir; building `tests/memfn/arm_fixtures.c` against a tree's `build/libpcrec.a` into your dir;
  python3 checks run directly (`python3 -I ...`); the slot harness's DRY runs
  (`python3 -I <slot>/run.py dry JOB $R/<lens>/run s2c-dry`, and `slot/sabotage.sh $R/<lens>/sab [ROW..]`, which
  runs dry runs in scratch copies). Every dry run under `gnutimeout 900 nice`, AT MOST 2 dry runs at a time in
  the round in total (so: one at a time per critic, never in parallel), and NEVER between 19:00 and 01:00 local.
  A dry run takes ~2-20 s. Box is shared: prefix heavier loops with `nice`.
- Budget: at most ~800 pattern compiles in total for your lens (a BASE/SUBJECT pair counts as 2).
- Bound anything that might hang with `gnutimeout`.

## Subject (frozen)

- SUBJECT = branch `lane/memfn-s2c` = `8983c402673921c40c799fb735364781c8d41c72`.
- Review tree (built, `build/pcrec`, `build/libpcrec.a`): `T=/home/pcrec/projects/pcrec/worktrees/crit-memfn-s2c`.
  Read code there or by `git -C /home/pcrec/projects/pcrec show 8983c4026:PATH`.
- BASE tree for S2c (built, same layout): `B=$R/base` = an export of `ea5d54abf` (S2c's own named base, the
  merge of S2b + S2a-fix into the kit branch).
- **S2c's OWN diff (your scope)** — the branch also carries units S2a and S2b, reviewed separately; do not
  review them except as context S2c relies on:

      git -C /home/pcrec/projects/pcrec diff ea5d54abf 8983c4026 -- . \
          ':!tests/registry/limits_check.sh' ':!docs/dev/lanes/s2c*' ':!docs/dev/lanes/s2cdoc*' \
          ':!docs/dev/history/claude_md/docs__dev__lanes.md' \
          ':!memfn/docs/journal.md' ':!memfn/docs/wake.md' ':!memfn/docs/responses.md'

  (`tests/registry/limits_check.sh` is S2a's fix merged mid-unit at 979eeae83; S2c's commits are
  4cc755a15..8983c4026.) The diff: `memfn/src/formhash.c` (the form-hash ENTRY TABLE + renderer), `memfn/src/kit.h`,
  `memfn/src/runcmp.c` (`run_cmp_row`), `memfn/data/cards/kit-grid.tsv` (kit-grid@3 card rows) + its CLAUDE.md,
  `tests/memfn/arm_fixtures.c` (`--hash`, `--site-text`, `--site-parts`, `--facts`), `tests/memfn/finder_check.py`
  (check C's card deps guard, `check_hash`), sabotage rows `tests/mech/sabotages/S2930..S2932_*.sh`,
  the SLOT HARNESS `docs/design/memfn/span_cards/slot/` (read its CLAUDE.md first: plan.py, vcls.py/.out,
  slot.h, gen.c, drv.c, link.py, art.py, enter/fixtures.tsv, j1/, run.py, est.py, j1_rule.py, record.py,
  sabotage.sh, movers.py), the spec hunks `docs/spec/measures.md` new §3.4 "The estimator", §3.5 "Gates, the NULL
  rule, drift, outcomes" and §2.2¶5, `docs/design/measure_sets.md` and `docs/design/memfn/span_pick.md` [s2] lines,
  and the design `docs/design/memfn/span_cards.md` rev 1.3 text edits.
- **Design of record**: `$T/docs/design/memfn/span_cards.md` (rev 1.3). §9's S2c row is the unit's CHARTER
  (content, witness, sabotage rows (j)-(o)). §0 decisions, §1 goals (ranked), §2 cards, §3 producer (§3.2 timed
  text/renderer/placement, §3.3 job shape, §3.4 estimator, §3.5 gates/NULL/drift/run record/outcomes, §3.6 J1,
  §3.8 assembly). Its committed drills live in `span_cards/*.py` (evidence for the design; not S2c's code).
  Related: `span_pick.md`, `measure_sets.md` (§7.1 seam), `memfn/docs/requests.md` "R-35" (the request and its
  rulings), `docs/spec/measures.md` (the contract).
- Rulings: read `docs/dev/decisions.md` and `docs/dev/plan.md` ONLY as frozen on main:
  `git -C /home/pcrec/projects/pcrec show ae7b58d8c:docs/dev/decisions.md` (same for plan.md). Relevant: D26,
  D77, D80, D146/D147, D149 (unmeasured defaults), D157, D174, D176, D186, D188 (+ add. 1). Locate a plan.md row
  only by `grep -n '^- \[TAG\]'`. A finding against a ruled D-row cites it and argues, or drops.
- Guide (what you review against): `$T/docs/dev/guide/` — README.md, coding.md, architecture.md, style.md,
  critics.md, addenda/. Learnings on checks: `$T/docs/dev/learnings.md` §3. `$T/memfn/CLAUDE.md`,
  `$T/memfn/src/CLAUDE.md`.

## Probing notes

- Emitted-C compares: compile BASE and SUBJECT under the SAME basename in two dirs (the C names its basename),
  e.g. `$B/build/pcrec -p rx --emit-main -o $R/<lens>/b/rx.c --pattern P` vs `$T/build/pcrec ... -o
  $R/<lens>/s/rx.c`. Rate regimes: default prior; `-e utf8` = NONE. Not expected to matter (S2c claims no
  emitted byte moves); if you need another regime, check its spelling with one compile first.
- Form hashes: `gcc -std=gnu11 -O1 -I$X/memfn/include $X/tests/memfn/arm_fixtures.c $X/build/libpcrec.a -o
  $R/<lens>/fx.<b|s>` for X in $B, $T; then `fx --hash`, `fx --site-text ID [CLS]`, `fx --site-parts ID [CLS]`,
  `fx --facts ID [CLS]` (SUBJECT only for the new modes).
- Slot dry run (verified spelling, rc 0 in 2 s): `SLOT=$T/docs/design/memfn/span_cards/slot;
  gnutimeout 900 nice python3 -I $SLOT/run.py dry J2 $R/<lens>/run s2c-dry`. Jobs: J1..J5, J2p. The harness
  writes only under the RUNDIR you name. `SLOT_TREE` names the tree when slot/ runs from a copy (a plant in a
  scratch copy: copy `slot/` into your dir, patch it, run it with `SLOT_TREE=$T`).
- Planting in kit C or checks: copy the file(s) into your dir and build/run from the copy; never edit $T.
  Classify every plant compare as SAME, SILENT-MOVE (rc 0, bytes differ) or LOUD (rc != 0); delete old outputs
  before each compare.

## DENYLIST (never open, grep, diff or cite; exclude from EVERY git diff/grep)

- `docs/dev/lanes/s2c*`, `docs/dev/lanes/s2cdoc*` (the lanes' reports and deliver files), and every other
  `docs/dev/lanes/*` file of this branch's lanes (s2a*, s2afix*, s2b*, s2rev*, s2design*).
- `docs/dev/reviews/2026-11-06-r4*`, `r5*`, `r6*`, `r7*`, `r8*` (earlier reviews of this subject/design).
- `memfn/docs/journal.md`, `memfn/docs/wake.md`, `memfn/docs/responses.md`.
- `/var/tmp/pcrec-pcrec/scratch/memfn/` (the lanes' scratch, incl. `s2c/`), every other `crit-*` scratch dir,
  and `$R/.coord/` (the coordinator's notes), and other critics' dirs/files under `$R`.
- The worktrees `s2a`, `s2b`, `s2c`, `s2rev*`, `memfn`, and every other worktree except `worktrees/crit-memfn-s2c`.
- `git log` bodies beyond subject lines; job logs; the box queue (`worktrees/.boxqueue`).
- In git: append `':!docs/dev/lanes/s2*' ':!docs/dev/reviews/2026-11-06-r[4-8]*' ':!memfn/docs/journal.md'
  ':!memfn/docs/wake.md' ':!memfn/docs/responses.md'` to every diff/grep/log -p. For PLAIN `grep -r` add
  `--exclude-dir=lanes --exclude-dir=reviews --exclude=journal.md --exclude=wake.md --exclude=responses.md`
  (plain grep ignores pathspecs).
- If you land on denied text by accident, stop reading it and say so in your file.

## Output (your deliverable)

- Your findings file `$R/findings-<lens>.md` DOES NOT EXIST YET: CREATE it as your FIRST action with these
  headings, then write it INCREMENTALLY (append each finding as you confirm it):

      # findings — <lens> — memfn-s2c
      ## Findings
      ## PROBED-AND-HELD

- Each finding: id `<LENS>-n` (e.g. `EMIT-1`); **CONFIRMED** (with a repro: input, exact command, observed vs
  expected) or **SUSPECTED** (what would confirm it); severity (answer / speed / size / maintenance / doc /
  design); effort; blast radius; file:line or §. A measurement-harness defect that would let a WRONG number or a
  wrong verdict into the set counts as severity `answer` for the set.
- End with `## PROBED-AND-HELD`: what you probed that held, with case counts.
- When done: `python3 /home/pcrec/projects/pcrec/scripts/lanecheck --dir $R --deliver $R/crit-<lens>.deliver crit-<lens>`
  must print `lanecheck: DONE rc=0`; fix the file until it does. Then end. Final reply at most 150 words.
- If your Write of the findings file is REFUSED, SendMessage your findings to the coordinator at once, marked
  relayed; if a harness rule refuses it, do not route around it: return the findings as your final text.
