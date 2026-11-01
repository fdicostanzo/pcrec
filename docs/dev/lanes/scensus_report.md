# scensus: compile-only censuses M0-M6 for the "one instruction stream" design (lane scensus, sonnet, 2026-11-01)

Build go: Frank 2026-11-01 ("the data gathering approach is good"). Plan: synthesis section 7 (M0-M6); the
benefit rows they turn from argued to measured are 4.1 (M1-M3), 4.2 (M1, M6), 4.3 (M0), 4.4 (M4, M5).
Deliverable: `docs/dev/lanes/scensus_evidence/census.py` (python3, read-only on the tree), the queued job
`798-scensus-run` (copy: `scensus_evidence/798-scensus-run`), this report. No `src/`, `cli/` or `lib/` change.

## What the script does

- Populations (counted separately): CORPUS = every `tests/**/*.rxt` pattern block, read by `build/pcrec --list-source`
  (5,210 distinct patterns after dedup within the population); BENCH = pcrec-bench's `bench/*/patterns.rxt`,
  `bench/*/export/*.rxt` and `bench/unusual/patterns/*.rx`, read-only (356 distinct). Each is compiled with
  `--features all` (plus `-i` / `-e` from its block), engine auto. Head-level `config`/`with` composition is not
  applied (`--list-source` is "as written"); a pattern that needs a head setting shows up as `refused`, counted.
- One compile per pattern: `--emit-ir`. A DFA-routed pattern makes `--emit-ir` refuse with "compiles to the DFA
  engine"; that refusal is the DFA verdict (engine=dfa). Fields read from `#section summary`: `engine` (+ the
  "forced by:" note), `prefilter`, `rungs`, `resume-points`, `prune-ceiling`, `subject-ceiling`.
- Pattern STRUCTURE (M3-M6) is not printed by pcrec as a tree, so a small conservative scanner (`Scanner` in the
  script) builds one from the pattern text. A pattern it cannot follow is `unparsed`, never guessed; the run goes
  RED if more than 5% of the patterns that compiled are unparsed (measured offline: 39 of 5,566 patterns,
  0.7%, almost all deliberate reject-table inputs).
- Output (`$PCREC_TMPDIR/scratch/scensus/run/`): `m0_sites.tsv`, `m0_kind_host.tsv`, `m1_resume0.tsv`,
  `m2_prefilter.tsv`, `m3_seam.tsv`, `m4_cap_in_repeat.tsv`, `m5_regular_after_irregular.tsv`,
  `m6_resume_regular.tsv`, `summary.txt` (counts per population, 3 example patterns per row, parse-control
  tally). Plant rows carry `pop=plant` and are excluded from the counts.
- Final line `scensus: COMPLETE plants=N corpus=N bench=N vm_corpus=N vm_bench=N`, only if every plant passed and
  the controls held; else `scensus: RED` plus the reasons, exit 1.

## Per measurement: reads, approximation, plant

**M0 (14 glue sites, kind x host cells).** Reads: grep over `src/`. `m0_sites.tsv` checks each synthesis
section 4.3 site (X1-X14, X1 and X13 split in two rows): where the table cites a line range
(`emit_vm.c:13005-13033`, `10366-10441`, `4298-4745`, `vm_cursor_rep 4890`, `vm_revdet_rep 5705`) the row is
CONFIRMED only if the expected symbol occurs inside that range; others are symbol-present checks (the table
cites no line). `m0_kind_host.tsv`: mentions of each `DELEG_*` site (from `memfn_sites.def`) and each `MF_SK_*`
kind per host file. Approximation: a mention count, not a call-site census. Finding already visible in the
smoke: X12 (`emit_landmark_walk`, p1build) is ABSENT on this main (f574eab2d), so that row reads FAIL and is
reported, not made red; all the cited ranges for X1-X4 still hold. Plant: the cited-range check is itself the
control (a moved range goes red; X12 is the one expected non-confirmation).

**M1 (VM artifacts with `resume-points 0`, split by landmark admission).** Reads: engine=vm and
`resume-points 0` from `--emit-ir`. The split by "D161 add. 17 admits a landmark for the capture-erased prefix"
is NOT MEASURABLE TODAY: pcrec prints no stamp or fact for that admission (the landmark walk is the kit's and
the walk's decision is not a printed field; `emit_landmark_walk` is not on main). Printing it would take a fact or
stamp from the landmark-walk admission row (what p1build's decision table decides), emitted in `--emit-facts`.
Proxy, labelled as such and NOT the admission: for capture-forced rows only, a second compile
`--no-captures --emit-facts` reads whether the capture-erased pattern has a derived `req_run` or `req_byte`
(`landmark-exists`/`no-landmark`) and prints `req_landmark_maxoff`. It is an upper bound on the admission
(a necessary byte can exist where no reverse walk is admitted), so the proxy column is a ceiling, never the
number. `m1_resume0.tsv` carries the proxy and a fixed `NOT-MEASURABLE-TODAY` admission column. Plant:
`(\w+)@(\w+)\.com` and `(\w+)\s+\1` must land in vm-resume0.

**M2 (VM artifacts by prefilter reason).** Reads `prefilter` (first word: `yes`, `no-backreference`,
`no-callout`, others as printed) and `prune-ceiling` (`subject-end` when lookaround/atomic/count-collapsed
applies, `prefilter-window` otherwise). Approximation: none beyond the printed words; `prune-ceiling
subject-end` is tabulated as printed and is not split further into lookaround vs atomic (the note does not
say which; the structure scanner's irregular kinds in `m3_seam.tsv` can be joined for that). Plant:
`(\w+)\s+\1` -> `no-backreference`, `x(?C1)y\d+` -> `no-callout`, `(\w+)@(\w+)\.com` -> `yes`.

**M3 (VM artifacts whose only forcing reason is captures, or a zero-width item).** The seam classifier
(documented, in `classify`): a VM artifact is `captures-only` if the scanner finds a capture group, NO irregular
node (backref, callout, lookaround, atomic, recursion/subroutine call, conditional, backtracking verb, `\K`) and
the compiler's own forced-by note starts "capture group"; `zero-width-only` if every irregular node is a
lookaround (captures allowed, anchors and `\b` are not irregular); `no-irregular-node(forced-by-other)` if the
scanner sees nothing irregular but pcrec forced the VM for another reason (an unmodelled forcing construct,
visible in the `forced_by` column); else `mixed-or-other`. Approximation: pcrec prints only the FIRST forcing
reason, so "only" rests on the scanner tree; the parse-control tally (summary) checks the scanner against the
compiler's text (forced-by capture implies the scanner found a capture; forced-by callout implies a callout
node; forced-by backreference a backref) and any disagreement turns the run RED. Plant: `(\w+)@(\w+)\.com` ->
captures-only; `foo(?=bar)` -> zero-width-only; `(\w+)\s+\1`, `x(?C1)y\d+` -> mixed-or-other.

**M4 (capture inside a repeat).** Reads the scanner tree: a capture node with a repeat ancestor whose max is
unbounded or above 1. Approximation: `?` and `{0,1}` are not repeats; "inside a would-be segment" is not
computed (no segment definition is printed); counted for all engines and for VM only. Plant:
`(\w+\.)+com` and `(a+)+b` -> yes; `(\w+)@(\w+)\.com` -> no.

**M5 (regular region after the first irregular node below the top level; more than one VM-forcing construct).**
Reads the scanner tree. "Below the top level" = nesting depth at least 1 counting capture, group, atomic,
lookaround, conditional, repeat AND each branch of a root alternation (the compound concat split does not cut
an alternation). M5a = for the first irregular node at depth at least 1, some consuming regular leaf (literal,
class, any) follows its subtree in document order, outside any irregular ancestor. M5b = at least two
irregular nodes (captures are not counted; the TSV lists the kinds so a with-captures variant is a join away).
Approximation: this is a textual-order stand-in for "a region the compound could tile"; it does not model
which regions are DFA-able, only that nothing irregular surrounds the leaf. Plants (each compiled through the
same path): `(\w+)=([^;]*);(?:\1(?=x)|x)+` M5a yes M5b yes; `(?:a(\w)\1)cd` M5a yes M5b no;
`(?:a(?=b))cd` (a DFA pattern) M5a yes; `(a)(?=a)b\1` M5a no (both irregular nodes at depth 0) M5b yes.

**M6 (VM artifacts with `resume-points > 0` regular apart from captures; `frames-unbounded` stamp).** Reads
`resume-points` and `rungs` (a `frames-unbounded` entry) from `--emit-ir`; "regular apart from captures" is the
scanner finding no irregular node. Approximation: regular here means "nothing the scanner calls irregular",
so a construct pcrec treats as irregular but the scanner does not model would be counted in (the M3
`forced-by-other` row and the summary expose how many VM artifacts that is). Plant: `(\w+\.)+com` and
`(a+)+b` must read `resume>0 regular-apart-from-captures frames-unbounded`.

Controls beyond the plants: run-level REDs for a missing `build/pcrec`, a population under 100 patterns on a
full run, more than 5% unparsed, and any parse-control disagreement. Hole worth knowing: the plants and
controls share the scanner with the numbers they check (learnings section 3's shared-source failure); the
independent leg is the compiler's own forced-by text and the printed stamps, which the plants assert.

## Smoke (<= 20 compiles)

`census.py --smoke` (plants only, 11 compiles, includes `(\w+)@(\w+)\.com`, `(\w+)\s+\1`, `x(?C1)y\d+`,
`(\w+\.)+com`, `(a+)+b`, `abc`): `scensus: COMPLETE plants=11 corpus=0 bench=0`; `--limit 5` (11 plants + 5
corpus compiles) also COMPLETE. Offline (no compiles) the corpus reader found 5,210 corpus and 356 bench
patterns and the scanner left 39 unparsed. Output kept in `$PCREC_TMPDIR/scratch/scensus/smoke/`. The full
sweep has NOT been run (a loop over 50 compiles is queued-only); the population counts above are the reader's,
the measurement counts do not exist until the job runs. Cost estimate: compiles measured at ~6 ms each, ~5.6k
patterns plus the M1 proxy compiles, so a few minutes at 4 threads (est 300, cap 1800).

## OWED: scensus-run

Job `798-scensus-run` (key `scensus-scensus-run`), queued with `not-before 2026-11-03T01:00`, est 300, cap 1800,
dry-run verified (`boxqueue --dry-run` lists it `ok`). Runs `census.py` in the lane worktree, writes to
`/var/tmp/pcrec-pcrec/scratch/scensus/run/`. Completion line: `scensus: COMPLETE plants=11 corpus=<n> bench=<n>
vm_corpus=<n> vm_bench=<n>` (expect `plants=11 last=^scensus: COMPLETE plants=`); a RED run prints `scensus: RED`
and the reasons, exit 1. The job executes from the lane worktree (`worktrees/scensus`, build/pcrec in it): do
NOT `wtprune` that worktree before the job has run, or re-queue from main after the merge.

## STATE AT HANDOFF

Script, job and report committed on lane/scensus; smoke green; full sweep OWED to the box queue (above). Not
measured: every M0-M6 count (only the populations are known); M1's landmark-admission split is NOT MEASURABLE
TODAY (proxy only, labelled). Last rulings entry applied: none (`scensus_rulings.md` had only "(none yet)" at
the last check). Next: after the job, a fresh agent reads `summary.txt` and fills the synthesis section 4
grades; if the unparsed or forced-by-other rows are large, extend the scanner first.
