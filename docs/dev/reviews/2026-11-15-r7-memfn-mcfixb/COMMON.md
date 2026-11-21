# COMMON brief — critic round memfn-mcfixb (code, LIGHT), 2026-11-15

## Scope mandate (binding)
- Work only in /home/pcrec/projects/pcrec (read-only on /home/pcrec/projects/pcrec-bench). Write ONLY under
  /var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfixb/<your-lens>/ (your own subdir; your findings file is in it).
  Set `PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfixb/<your-lens>` for every script you run.
- READ-ONLY critic: never edit either repo (not even the review tree), never `make`, no suites, no box-queue jobs,
  no timing (no clocked `run.py run`/`screen`; `run.py dry` is fine, it has no clock). `gnutimeout` on every
  uncertain command. Kill only with `scripts/safekill PID`. Never `cd` into a worktrees/ path in a chained command
  (a hook blocks it): use absolute paths, `git -C`, or a `(cd X && ...)` subshell.
- NEVER touch worktrees/mfind (a box gate runs there) or any worktree except the review tree below.
- Plants go in a COPY under your own subdir (copy slot/ there and run it with
  `SLOT_TREE=/home/pcrec/projects/pcrec/worktrees/crit-memfn-mcfixb`), or a copy of emitted C / kit source
  compiled into your dir with gcc. Never in the tree.

## Subject (frozen)
- SUBJECT = 6ab3f485b9942606ebd5765fd68fd9a586804138 (branch lane/memfn-mcfixb).
- BASE = ac097a76e2a85a5daef793dc2506ed6f6a13423b (stated, by design: earlier code was reviewed by rounds r5 and r6).
  Review the FIX DIFF only, plus the comment-only commit ac097a76e itself (`git show ac097a76e`):
  `git -C /home/pcrec/projects/pcrec diff ac097a76e 6ab3f485b -- . ':!docs/dev/lanes/mcfixa*' ':!docs/dev/lanes/mcfixb*' ':!docs/dev/lanes/mcfixd*' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md' ':!memfn/docs/wake.md' ':!docs/dev/dev_journal.md'`
- Review tree (built: build/pcrec, build/pcrec-harness, build/libpcrec.a):
  /home/pcrec/projects/pcrec/worktrees/crit-memfn-mcfixb (detached at SUBJECT). Read-only.
- The PROMISE: the prior round's ruled review, committed in the subject:
  `docs/dev/reviews/2026-11-15-r6-memfn-mcfix.md` (+ sibling dir). Its "RULED" section lists the FIX-NOW ids
  (RULE-1, RULE-2 + RULE-5/RULE-6/equality tail, RULE-3 + FIDELITY-3, FIDELITY-2/RULE-8(b), FIDELITY-1, RULE-7,
  CHECKS-A1, CHECKS-A3). Read it as the promise each fix makes; JUDGE FROM THE CODE, not from prose.
- Claimed by the fix: 0 emitted-byte movers (1200 pairs), no abi event.
- Contents: slot/d197_rule.tsv + d197_rule.py (NOT-WIN ordering, confirm/second provenance guards, confirm cells
  only at CONFIRM levels, libc_variant table, drill), record.py (rule pins at `window`, cells pins at `finalize`),
  est.py (refuses a pin mismatch), link.py (TIMED-SHAPE per-form callee allowlist `TIMED_CALLEES`, section-symbol
  and indirect branch refusal, `shape-selftest`), sabotage.sh rows (m1)-(m5) S3207-S3209 S3214 S3215,
  memfn/src/kit.h + finder.c + window.c (enum sentinel FF__COUNT), memfn/tests/run_g2_mfind.py (--sites < 80
  refusal), slot/CLAUDE.md.

## Rulings in force (frozen at main d64c3e822; decisions.md/plan.md last touched 782502e99)
Read rulings only via `git -C /home/pcrec/projects/pcrec show d64c3e822:docs/dev/decisions.md` (D197 at line 10219).
- D197 (Frank 2026-11-15): the fused mfind row is an UNPICKED MEASURING INSTRUMENT; the timing is ONE-SIDED.
- Main's rule conditions (2026-11-15; home: the subject's d197_rule.tsv header): one verdict per ISA level; each
  level's emitted form vs libc memchr as it runs on the box (variant recorded) + the AVX2-tunable arm; the per-hit
  slope decides, scan is printed with its libc ratio and never decides; a LOSS on 1-2 of 36 comparisons must
  reproduce in ONE confirming re-run, 3+ counts at once; a second INCONCLUSIVE is NOT-WIN, never LOSS; the timed
  shape is inline as pcrec emits it.
- Kit ruling R1 (2026-11-15): a confirming record's cells apply ONLY at levels whose first-pass verdict was
  CONFIRM; other levels keep their first-pass verdict.
- Standing: the thing TIMED is the thing GATED, KEYED and RECORDED; checks must be able to fail
  (docs/dev/learnings.md §3: controls sharing a source with what they control, uncounted populations, witnesses
  that stopped reaching their site). Over-refusal (a valid input refused) is a finding too.

## Guide files
docs/dev/guide/README.md, coding.md, critics.md; docs/dev/learnings.md §3; slot/CLAUDE.md;
docs/design/memfn/span_cards.md §3.x; memfn/CLAUDE.md.

## Run kit (prepared; reuse, do not rebuild)
- slot dir: S=/home/pcrec/projects/pcrec/worktrees/crit-memfn-mcfixb/docs/design/memfn/span_cards/slot
- A finished JMH DRY RUN of the review tree: /var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfixb/kit/dry (log
  kit/dry_JMH.log). TUs, objects, cell_text.tsv, manifest under kit/dry/JMH/. READ only; copy to your dir to vary.
  Command that made it (for variants, into YOUR dir, ~3 min):
  `(cd $MYDIR && PCREC_TMPDIR=$MYDIR SLOT_TREE=/home/pcrec/projects/pcrec/worktrees/crit-memfn-mcfixb gnutimeout 900 nice python3 -I $S/run.py dry JMH $MYDIR/dry crit-dry)`
- Rule drill: `python3 -I $S/d197_rule.py drill` -> `== d197 DRILL ok: 43 cases, 0 wrong` (checked).
- Shape self-test: `python3 -I $S/link.py shape-selftest $MYDIR/shape`.
- est.py self-test: `python3 -I $S/est.py selftest $MYDIR/est`.
- The lever build: `<tree>/build/pcrec-harness --harness=mfind [-fmemfn-simd=x86-64|x86-64-v3] -p rx --emit-main -o OUT.c --pattern 'xy[0-9]+z'`
- BASE tree: `git -C /home/pcrec/projects/pcrec archive ac097a76e | tar -x -C $MYDIR/base` (your dir only).

## DENYLIST (do not read; exclude from every diff and grep)
docs/dev/lanes/mcfixa*, docs/dev/lanes/mcfixb*, docs/dev/lanes/mcfixd*, memfn/docs/journal.md,
memfn/docs/responses.md, memfn/docs/wake.md, docs/dev/dev_journal.md, /var/tmp/pcrec-pcrec/scratch/memfn/,
/var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfixb/.coord/, other critics' subdirs in this round dir, other round dirs
under scratch/, `git log` bodies (subject lines only), job logs, the box queue, every worktree other than
worktrees/crit-memfn-mcfixb.
Plain grep: `grep -r --exclude='mcfixa*' --exclude='mcfixb*' --exclude='mcfixd*' --exclude=journal.md --exclude=responses.md --exclude=wake.md --exclude=dev_journal.md ...`
(plain grep ignores git pathspecs).

## Output format
Your findings file DOES NOT EXIST YET: CREATE it as your FIRST action at `<your-lens>/findings.md` with headings
`# <lens> — memfn-mcfixb`, `## Findings`, `## PROBED-AND-HELD`; APPEND each finding the moment you have it, one
append per finding. Each finding: id `<LENS>-n`; CONFIRMED (repro: input, command, observed vs expected) or
SUSPECTED (what would confirm it); severity (answer / measurement / speed / size / maintenance / doc / design);
effort; blast radius; file:line. "measurement" = the timing could record, key or decide something other than it
claims. A finding against a ruled D-row cites it and argues, or drops. End with PROBED-AND-HELD (with case counts).
If your Write is REFUSED, SendMessage your findings to `crit-memfn-mcfixb` at once, marked relayed.
Before ending run: `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfixb --deliver /var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfixb/<lens>_deliver.txt <lens>`
and end only when it prints DONE. Final reply at most 150 words.
TIME BOX: 35 minutes from launch (a timing window depends on this round). Findings first; polish never.
