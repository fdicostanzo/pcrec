# VERIFIER brief — round memfn-s2c

Read `/var/tmp/pcrec-pcrec/scratch/crit-memfn-s2c/COMMON.md` first: its scope mandate, read-only rules, dry-run limits
(one at a time, gnutimeout 900, never 19:00-01:00), compile budget and DENYLIST bind you too. Your dir:
`$R/verify/` (R=/var/tmp/pcrec-pcrec/scratch/crit-memfn-s2c), `PCREC_TMPDIR=$R/verify`.

The critics' findings files are `$R/findings-{emit,contract,checks,slot,house}.md` (you may read these; not
`$R/.coord/` and not the critics' own subdirs except to re-run a script they name, copied into your dir).

You trust NO critic's consequence claim. For each id below, re-run or re-derive it yourself and record a verdict:
**HOLDS / REFUTED / PARTLY / not verified (why)**. A REFUTED quotes the exact call you ran. A plant claim records
the plant's exit code beside its byte verdict (SAME / SILENT-MOVE / LOUD). Structural claims: quote the cited lines
(file:line at the subject tree $T). Design claims: quote the design/spec sentence and the code that contradicts it.

Write `$R/verify.md` (it does not exist yet: CREATE it first) with headings `## Verdicts` and, at the end, a line
section `## VERIFY COMPLETE`. Append one `### <ID>` subsection per finding AS YOU GO (incrementally). When done,
run `python3 /home/pcrec/projects/pcrec/scripts/lanecheck --dir $R --deliver $R/verify.deliver verify` until it
prints `lanecheck: DONE rc=0`, then end (final reply at most 150 words).

## Tier A — answer-level for the set; REPRODUCE each (plant/repro in scratch copies)

- CHECKS-1: the answer gate never checks the timed `_time` loop (plant: halve the `_time` loop in link.py's
  WRAP_FIND; J2 dry stays green).
- CHECKS-2: the gate's population (arms, pools) is never asserted (plant nlen 0; J3 dry prints ok with 0 pools).
- SLOT-15: the cell-text check compares the Arm's (form, cls), not the KEY's tokens (plant in plan.py: key
  `kit.find_byte.libc` with Arm form walk; J2 dry stays green).
- SLOT-1 / CONTRACT-2: est.py's verdict reads cell-file presence and a live plan.build(), not the record's
  jobs/plan/floor: two byte-identical records, different outcomes. Also CONTRACT-2's odd-gate halving
  (`GATE_E6 // 2` vs the spec's doubled comparisons): quote both and compute the counterexample.
- EMIT-1 / SLOT-6 / HOUSE-2 (one finding): est.py records `kit:form.<id>=<FORM hash>` (canonical instance) for rows
  that time non-canonical instances (settest c1/cn, rc-words w1/w3). Show the hashes differ (`fx --hash`) and quote
  est.py's dep line; and say whether span_cards.md §2.4 READY-8 promises the timed instance's hash.
- EMIT-2 / SLOT-7 / HOUSE-1: est.py's `form_hash` reads `TREE/build/arm_fixtures`, which nothing builds (grep
  Makefile/scripts/tests/slot); `est.py draft` fails. Also: isa/box/libc header keys never written by record.py.
- SLOT-2: `run.py run` times whatever executables are in RUNDIR; the run id is only logged; gate on launch 1 only.
  (Verify by READING run.py/link.py; never run `run.py run`.)
- SLOT-3 / HOUSE-3: record.py writes run_id/set/code_commit only in `j1`; finalize maps any non-green J2p to
  `declined-j1b`. Reproduce with record.py on an empty rundir and a hand STATES file (as the critics did).
- SLOT-4 / CONTRACT-5: boxqueue `after` answers 75 for a FAILED upstream; `record.py ready-j2p` answers 75 with no
  verdict; so a failed J1 wedges J2p/J9. Quote scripts/boxqueue's lines and the design §3.3/§3.5 sentences.
- SLOT-12: run.py's quiet wait is bounded from the job's start, not per wait (quote run.py:71-98; reason it through).
- HOUSE-4: link.py's null-base `L` dict duplicates formhash.c's entry bytes with `.get(..., 0)`.
- HOUSE-8 (only the link.py:214 `.get(a.landing, "LD_MISS")` and run.py:150 git rc parts): quote; does a typo'd
  landing really give a 0 == 0 gate pass? (one plant in a scratch copy, J2 or J3 dry).

## Tier B — design/charter/doc; quote the sentences and the code

- SLOT-5: the job scripts (§3.1 table row "THIS RUN's harness ... the job scripts", §3.3 job shape, §9 S2c) are
  absent from slot/. Is it S2c's charter or S2d's? Quote both.
- CONTRACT-1: the spec (measures.md new §3.4¶1) says the recompute reads the set and record "and nothing else", yet
  the base rule, `unless-j1-b` and J1's rule live only in span_cards.md.
- CONTRACT-3: measures.md §2.1's `partial` sentence not amended for format 2.
- CONTRACT-4 (a)-(c): L=7 assumed; absent unit row; W <= 0 / E = 0.
- EMIT-3: c2's instance `{X,x}` lowers to ONE compare under gcc -O2 (show the asm of the entry's text in a TU).
- EMIT-4: RUNCMP's row guard re-derives via run_cmp_row instead of reading the rendering arm; settest has no
  selection (row NULL). Quote formhash.c.
- EMIT-5: PAIR's B-fn (ofsskip) text differs from the E-find text the dep covers (one compile pair suffices).
- SLOT-8: plan.py's LENGTHS/L/R/GATE vs the ver-3 card rows (quote both).
- SLOT-9: vcls.out vs census0.out's class vocabularies; vcls.out's input provenance.
- SLOT-10: §2.5 walk-set `alt` rows vs plan.py.
- SLOT-11: enter fixtures for kinds 5/6 vs the card's `die1` regime.
- SLOT-13: the MAXDRAW trigger wording (§3.2) vs per-(launch, arm) bound and observed draw sums.
- CHECKS-3: check C's card guard accepts a respelled/invented `kit:form.` dep (one plant).
- CHECKS-4: R-MS3's rename fixture is never asserted to have renamed anything (quote arm_fixtures.c).
- HOUSE-5 / SLOT-18: j1_rule.py copies est.py's primitives (quote).
- HOUSE-6: est.py's unit by key string beside the card's unit column (quote).

Skip the rest (maintenance-only: HOUSE-7, 9-17, CHECKS-5..7, SLOT-14, SLOT-16, SLOT-17): do not verify them.
