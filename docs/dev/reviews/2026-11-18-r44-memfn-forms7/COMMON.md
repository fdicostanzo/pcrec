# COMMON brief: critic round memfn-forms7 (CODE mode)

## Scope mandate (binding)
- Touch ONLY the pcrec and pcrec-bench repositories, READ-ONLY. Write ONLY under your own lens dir
  `/var/tmp/pcrec-pcrec/scratch/crit-memfn-forms7/<lens>/` (scratch, RUNDIRs, probes) and your findings file.
  No other directory on this machine, no home/system config, never /tmp.
- No commits, merges, `make`, suites, box-queue jobs, or TIMING runs of any kind (never `cards.py run`,
  `rerun`, `c3`, `identity`, never call `run_cell`/`time_cells`, never perf/time a matcher). Building and
  ANSWER-GATING a few cells is allowed (no clock). Run everything `nice -n 19` and bound it with GNU `timeout`.
- Never `cd` into a worktree in a compound command (a hook blocks it); use absolute paths, `git -C`, or a
  `( cd X && ... )` subshell.
- Set `PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-memfn-forms7/<lens>` for every cards.py invocation
  (its selftest writes temp dirs under it).
- The box is free now; the owner holds it 20:00-01:00. Finish well before 19:30 (aim: under 90 minutes).

## Subject (frozen)
- Branch `lane/memfn-forms`, SUBJECT = 27b18e75ca65f993c366c6e4fd5ae89258920b28,
  BASE = merge-base with main = 02bbd527fc68052c08a580bae70bb191729cb676.
- The LAST REVIEWED revision is 42fd4b33e (rev 11). THIS round reviews the delta rev 11 -> rev 12: the
  kit's span forms' CARD script and its pick rule, `memfn/tests/span_forms/cards.py`, and the design of
  record `docs/design/memfn/r45_reply.md` rev 12 ("Changes in rev 12", §3 "The head `h` and the default"
  incl. "The layout pools" ~line 1002, drill (xxiii) ~line 1216, "The night order" ~line 1654).
- Read-only copies (use THESE, no repo access needed for them):
  `R/subject/r45_reply.rev12.md`, `R/subject/cards.rev12.py`, `R/subject/cards.rev11.py`,
  `R/subject/delta_rev11_to_rev12.diff` (the rev 11 -> rev 12 diff of the design, cards.py and 3 doc files).
  (`R/` = /var/tmp/pcrec-pcrec/scratch/crit-memfn-forms7/R/)
- Review tree (built once, do not rebuild): `/home/pcrec/projects/pcrec/worktrees/crit-memfn-forms7`
  (`build/pcrec`, `build/pcrec-harness`). The cards.py there is the subject's.
- What the subject is, in its own words (cards.py docstring): "THE SPAN FORMS' CARDS C1-C5, their rule
  R0-R5 and the identity check ... Every cell compiles a card pattern at PCREC level on ONE binary ...
  h set through the TEST-ONLY lever (`build/pcrec-harness --harness=span-head=N`) ... its answers gated
  against python `re` before any timing." The rule picks the shipped head default h* from a timed night
  (P(h* != 64 on pure noise) <= 5 % is the acceptance, cards.py ALPHA).

## Rulings in force
- The design's rev 12 restates the kit manager's rulings R2 A-D (r45_reply rev 12, "Changes in rev 12",
  rows R2 A..R2 D) and r41 L9 (setup randomization: layout POOLS). FREEZE NOTE: the R2 record itself
  lives only in a lane worktree file you may NOT read; review against the subject's own restatement and
  quote it. Main's rulings files at the freeze: read with `git -C /home/pcrec/projects/pcrec show
  ae57a8e06:docs/dev/decisions.md` (or plan.md), never the live tree. You need them rarely.
- Quoted subject rules you will need (verbatim, r45_reply rev 12 lines 81, 88-91):
  > L9: "every arm's text (I, each head, aa, the engine route, C3's arms) is linked as a pool of
  > `POOL_SIZE` = 4 variants (UNMEASURED DEFAULT), each its own compile of the TU with an IN-TU prelude
  > (a top-level `.skip 16 j` ahead of every function; j drawn mod 256, stratified so the four variants
  > take the four 16-B phase classes mod 64 and each alignment's two variants differ by 16 B mod 32) and
  > an alignment variant (odd variants: gcc's code alignment off, x86's tight-loop alignment too); every
  > launch draws a variant (a hash of the run id, the results file, the cell and the round), recorded
  > per launch (`variants` column); every variant answer-gated ... `dry` ... REFUSES a pool with one
  > 64-B phase vector or one relative layout."
  > R2 A: "a layout share common to every variant of a text is a property of that BODY's own internal
  > layout, which is what ships, so it IS the text's speed, not noise."
  Quote any other rule from the subject file with its line number; never paraphrase a rule into a finding.
- The house guide: `git -C /home/pcrec/projects/pcrec show main:docs/dev/guide/critics.md` (lens rules;
  the "Lessons from review rounds" entries dated 2026-11-17 on PERTURBATION, COMPARISON KINDS and POOLED
  estimators are YOUR standing drills), memory rule: a speed comparison differs in ONE variable (name
  every differing axis between the two objects compared).

## Standing drills both lenses apply (simulate lens + perturbation lens, critics.md)
1. PERTURBATION: for each comparison the rule makes (head vs I, head vs head, aa vs aa.b, a confirm
   re-time vs the night), name what physically differs between the two objects (inspect with `nm`,
   `objdump`, `readelf`: which symbols moved, which hot-loop alignments changed, what does NOT move:
   data/stack/subject-buffer alignment, the driver, the libc). A control that does not vary what the
   real comparison varies is not a control.
2. COMPARISON KINDS: for each ratio, which physical object each side is (one exe, two exes, two
   variants of one text, two texts) and whether the noise estimate was taken over the SAME kind of pair.
3. POOLED estimators: drill with the noise confined to EACH level it pools over (launch, variant, text
   body, round/order), one drill per level, plus a launch-order step (same data, another run order).
4. Selection-rule drills on CONSTRUCTED outcomes: the design's predicted outcome first, then
   adversarial; add a never-picked candidate (must not flip the pick); recompute every number the
   design QUOTES from its OWN formula.
5. Where the design ships its own drill script (cards.py selftest), implement the rule from the design
   TEXT before reading the script's version, then diff. Name the selftest's ORDER/control switches
   (LAYOUT_TEXT_TERM, VARIANT_BIMODAL, ...) and ask whether each can fail: a switch that reverses
   nothing carrying meaning guards nothing.

## The round kit
- `python3 -I R/../kit/pool.py RUNDIR PAT ARM LAYER [REGIME]` i.e.
  `PCREC_TMPDIR=<your dir> nice -n 19 timeout 900 python3 -I /var/tmp/pcrec-pcrec/scratch/crit-memfn-forms7/kit/pool.py <your dir>/rd hex24 h8 off hit-dense`
  builds ONE arm's 4-variant pool with the subject's own cards.py functions (build_cell, pool_proof),
  prints per variant the exe, rxa_search's address, the hot loops' 64-B and 32-B phases and relative
  layout, the refusal verdict, and (with REGIME) answer-gates that cell (prepare_cell; no clock).
  It sets WIDTH_FLAG=none: this branch lacks main's `--window-search-width` option (the lane's own dry
  run used `none` too). Patterns/arms: cards.py PATTERNS, CARDS (arms I, h0..h64, engine, aa, aa.b).
  The bin/ dir under your RUNDIR keeps every exe and its `.c` TU for nm/objdump/readelf.
- You may also import cards.py the same way (see the kit's 10 lines) and call its pure functions
  (analyse, synth_*, noise_drill, power_rate, gapk_rate, text_effects, ...) with your own constructed
  nights. `cards.py selftest --rev12` takes several minutes of CPU; run sub-rows by importing rather
  than the whole selftest repeatedly. Cap: at most ~120 exes built per critic.
- Pass patterns in single quotes or via a file.

## Denylist (D27 applied to review; PATHS EXCLUDED from EVERY git diff, grep and read)
- `docs/dev/lanes/forms*`, `docs/dev/lanes/formsfix*`, `docs/dev/lanes/formsland*`, `docs/dev/lanes/fcards*`,
  `docs/dev/lanes/r45*`, `docs/dev/lanes/span4k*` (lane reports and rulings files)
- `docs/dev/reviews/*memfn-forms*` and their sibling dirs, and every review of this subject
  (`docs/dev/reviews/*memfn-r45*`, `*memfn-span4k*`); the design's own "Changes in rev N" tables may be read.
- `memfn/docs/journal.md`, `memfn/docs/responses.md`, `memfn/docs/wake.md`
- every other worktree under `/home/pcrec/projects/pcrec/worktrees/` except crit-memfn-forms7;
  `/var/tmp/pcrec-pcrec/scratch/memfn/`; the box queue and job logs; `git log` bodies beyond subject lines.
- `/var/tmp/pcrec-pcrec/scratch/crit-memfn-forms7/.coord/` and the OTHER lens's dir.
- For git: append `-- . ':!docs/dev/lanes' ':!docs/dev/reviews' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md' ':!memfn/docs/wake.md'`.
  For plain grep -r: `--exclude-dir=lanes --exclude-dir=reviews --exclude=journal.md --exclude=responses.md --exclude=wake.md`.

## Output format
- Your findings file ALREADY EXISTS (pre-created with headings; it is your OUTPUT, not an input).
  Append each finding the MOMENT you have it, one append per finding.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command, observed vs expected) or
  SUSPECTED (what would confirm it); severity (answer / speed / size / maintenance / doc / design);
  effort; blast radius; file:line or §. A wrong h* default or a rule that cannot see a real win is a
  "speed" (or "design") finding; a check that cannot fail is "maintenance" unless it hides a wrong pick.
- End with PROBED-AND-HELD (what you tried that held, with case counts), then the line `CRITIC COMPLETE`.
- Then run: `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-forms7 --deliver /var/tmp/pcrec-pcrec/scratch/crit-memfn-forms7/<lens>/deliver.txt <lens>`
  and end only after it prints DONE. Final reply at most 150 words. A failed final reply is EXPECTED for
  a nested agent and needs no escalation: the CRITIC COMPLETE line in the file is the delivery.
- If your findings-file Write is refused, SendMessage your findings to the coordinator (marked relayed)
  rather than routing around the refusal.
