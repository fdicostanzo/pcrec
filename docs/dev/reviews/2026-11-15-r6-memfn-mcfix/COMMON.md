# COMMON brief — critic round memfn-mcfix (code, LIGHT), 2026-11-15

## Scope mandate (binding)
- Work only in /home/pcrec/projects/pcrec (read-only on /home/pcrec/projects/pcrec-bench). Write ONLY under
  /var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfix/<your-lens>/ (your own subdir) plus your findings file named in
  your prompt. Set `PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfix/<your-lens>` for every script you run.
- READ-ONLY critic: never edit either repo (not even the review tree), never `make`, no suites, no box-queue jobs,
  no timing (no clocked `run.py run`/`screen`; `run.py dry` is fine — it has no clock). `gnutimeout` on every
  uncertain command. Kill only with `scripts/safekill PID`. Never `cd` into a worktrees/ path in a chained command
  (a hook blocks it): use absolute paths, `git -C`, or a `(cd X && ...)` subshell.
- NEVER touch worktrees/mfind (a box gate runs there) or any other worktree except the review tree below.
- Plants (sabotage) go in a COPY of the file under your own subdir (e.g. copy slot/ to your dir and run it with
  `SLOT_TREE=/home/pcrec/projects/pcrec/worktrees/crit-memfn-mcfix`), or a copy of emitted C — never in the tree.

## Subject (frozen)
- SUBJECT = fe1b24e2a6b38bc32fd52053d773c01c3dee91b4 (merge 'lane/memfn-mcfixa' into lane/memfn-mfind).
- BASE = 9cb09119989d72a0b96bbdae97afca23b1cab434 (NOT merge-base main, by design: everything up to BASE was
  reviewed by round r5). This round reviews the FIX DIFF only:
  `git -C /home/pcrec/projects/pcrec diff 9cb091199 fe1b24e2a -- . ':!docs/dev/lanes/mcfixa*' ':!docs/dev/lanes/mcfixd*' ':!docs/dev/lanes/mfind*' ':!docs/dev/lanes/slotx*' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md' ':!memfn/docs/wake.md' ':!docs/dev/dev_journal.md'`
- Review tree (built, `build/pcrec`, `build/pcrec-harness`, `build/libpcrec.a`):
  /home/pcrec/projects/pcrec/worktrees/crit-memfn-mcfix (detached at SUBJECT). Read-only.
- What the fixes CLAIM to fix: the prior round's ruled review, in the subject tree,
  `docs/dev/reviews/2026-11-15-r5-memfn-mfindcomb.md` (+ its sibling dir). You MAY read it as the PROMISE under
  review (finding ids FIDELITY-n, CHECKS-n, EMITTED-n, DRAFTSETS-n, R1/R3 rulings). Judge from the CODE, not from
  the review's or the fix's own prose.
- Claimed by the fix: zero emitted-byte movers at default flags, no abi event.

Contents of the fix diff:
- the slot measurement harness `docs/design/memfn/span_cards/slot/`: inline timed shape (ONE TEXT, TWO OBJECTS:
  `_time` alone in the arm object, `_gate` compiled from the same file under `-DSLOT_GATE_TU`) + the TIMED-SHAPE
  check (link.py), manifest/cell_text pins, duplicate refusals, ISA level from the kit's target facts, unit row
  per set (est.py), record.py (libc memchr variant), plan.py (CONFIRM_CELLS, job 610), sabotage.sh new rows,
  a DECLARED decision rule `d197_rule.tsv` + its reader `d197_rule.py` + its drill;
- kit/test fixes: memfn/src/window.c (`wf_wsearch` sized to FF_MFIND + static assert), memfn/tests/g2/g2_mfind_gen.c
  (selector calls its top rung), memfn/tests/run_g2_mfind.py (floor scaling), new mech row
  tests/mech/sabotages/S3198_simdguarded_mfind_fit_cap_dropped.sh, tests/memfn/rows.tsv (`instrument:mfind`
  reason) + rows_check.py, tests/memfn/simd_guarded_check.py, wording in memfn.h/kit.h/ofsskip.c/compose.c/
  internal.h/run_axes.sh, kit-grid.tsv comment.

## Rulings in force (frozen at main bf16c278f; decisions.md/plan.md last touched bf8319fb8)
Read ruling files only via `git -C /home/pcrec/projects/pcrec show bf16c278f:docs/dev/decisions.md`, never the
live tree.
- D197 (Frank 2026-11-15; decisions.md:10219 at the freeze): the fused mfind row is an UNPICKED measuring
  instrument; the timing is ONE-SIDED (fused per-hit cost is a lower bound for the split shape); a fused LOSS to
  libc memchr at a level settles span_pick row 1 against the finder at that level; a WIN triggers the ruled split
  shape under its own owner go, then a re-measure.
- Main's conditions on the rule table (2026-11-15; message only at main — FREEZE NOTE; its home is the subject's
  d197_rule.tsv header), verbatim from the launcher: "one verdict per ISA level, each level's form = what a build
  at that level emits under the lever, compared with libc memchr as it runs on the box (variant recorded) plus the
  AVX2-tunable arm; each row names cells, statistic (per-hit slope; scan reported separately), A/A floor,
  WIN/LOSS/INCONCLUSIVE and triggers; a LOSS resting on 1-2 of 36 comparisons must reproduce in one confirming
  re-run, 3+ counts at once; a second INCONCLUSIVE is NOT-WIN, not LOSS; a header line says why scan cost never
  decides, and the scan ratio is printed per level; the timed shape is inline as pcrec emits it. Draft sets: one
  per ISA level; the guard exempts exactly the unit_key row."
- Standing: the thing TIMED is the thing GATED, KEYED and RECORDED (span_cards §R1.3 r9 table); a speed
  comparison differs in ONE variable, every differing axis named; checks must be able to fail (docs/dev/learnings.md
  §3: controls that share a source with what they control, uncounted populations, witnesses that stopped reaching).

## Guide files
docs/dev/guide/README.md, coding.md, critics.md; docs/dev/learnings.md §3; the slot dir's CLAUDE.md;
docs/design/memfn/span_cards.md §2.7 and §3.x (slot harness); memfn/CLAUDE.md.

## Run kit (already prepared; reuse, do not rebuild)
- A finished JMH DRY RUN of the review tree: /var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfix/kit/dry (log
  kit/dry_JMH.log: 172 arms, gate + round check green on 7 launches). The rendered TUs, objects, cell_text.tsv,
  manifest live under kit/dry/JMH/. READ them; do not write there (copy to your own dir first).
  Command that made it (for your own variants, into YOUR dir):
  `(cd $MYDIR && PCREC_TMPDIR=$MYDIR gnutimeout 900 nice python3 -I /home/pcrec/projects/pcrec/worktrees/crit-memfn-mcfix/docs/design/memfn/span_cards/slot/run.py dry JMH $MYDIR/dry crit-dry)`
  (~3 min). JMB the same with `JMB`.
- The rule drill: `python3 -I <tree>/docs/design/memfn/span_cards/slot/d197_rule.py drill` → `== d197 DRILL ok: 21 cases, 0 wrong`.
- est.py self-test: `python3 -I <slot>/est.py selftest $MYDIR/est` (writes only under the given dir).
- The lever build: `<tree>/build/pcrec-harness --harness=mfind [-fmemfn-simd=x86-64|x86-64-v3] -p rx --emit-main -o OUT.c --pattern 'xy[0-9]+z'`
  (the timed form's production twin; `gcc -O2 -S` it to compare with the harness's arm object).
- BASE tree for comparisons: `git -C /home/pcrec/projects/pcrec archive 9cb091199 | tar -x -C $MYDIR/base` (your
  dir only), or `git show 9cb091199:PATH`.

## DENYLIST (do not read; exclude from every diff and grep)
docs/dev/lanes/mcfixa*, docs/dev/lanes/mcfixd*, docs/dev/lanes/mfind*, docs/dev/lanes/slotx*, memfn/docs/journal.md,
memfn/docs/responses.md, memfn/docs/wake.md, docs/dev/dev_journal.md, /var/tmp/pcrec-pcrec/scratch/memfn/,
/var/tmp/pcrec-pcrec/scratch/crit-memfn-mfindcomb/.coord/, /var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfix/.coord/,
other critics' subdirs/files in this round dir, `git log` bodies (subject lines only), job logs, the box queue,
every worktree other than worktrees/crit-memfn-mcfix.
Plain grep: `grep -r --exclude='mcfixa*' --exclude='mcfixd*' --exclude='mfind_*' --exclude='slotx*' --exclude=journal.md --exclude=responses.md --exclude=wake.md --exclude=dev_journal.md ...`
(plain grep ignores git pathspecs).

## Output format
Your findings file DOES NOT EXIST YET: CREATE it as your FIRST action, with headings `# <lens> — memfn-mcfix`,
`## Findings`, `## PROBED-AND-HELD`, then APPEND each finding the moment you have it, one append per finding.
Each finding: id `<LENS>-n`; CONFIRMED (repro: input, command, observed vs expected) or SUSPECTED (what would
confirm it); severity (answer / measurement / speed / size / maintenance / doc / design); effort; blast radius;
file:line or §. "measurement" = the timing could record, key or decide something other than what it claims.
A finding against a ruled D-row cites it and argues, or drops. End with PROBED-AND-HELD (what you probed that
held, with case counts). If your Write is REFUSED, SendMessage your findings to the coordinator at once, marked
relayed. Final reply at most 150 words.
Before ending run: `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfix --deliver /var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfix/<lens>_deliver.txt <lens>`
and end only when it prints DONE.
Time box: 45 minutes from launch. Findings first; polish never.
