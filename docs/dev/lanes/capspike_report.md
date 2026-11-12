# capspike — tagged-DFA captures spike: report

Lane `capspike`, opus, 2026-11-12, Linux dev box (7700X). Study only: no
`src/`, `cli/`, `lib/` or `memfn/` edit. Branch `lane/capspike`. Deliverable:
`studies/dfacap_spike/` (code, cases, results). Background:
`docs/design/dfa_captures_research.md` (lane dfacap).

## STATE AT HANDOFF

- STATE: done. All five brief items have results, and every number below
  is in a committed file under `studies/dfacap_spike/results/`.
- Rulings file `docs/dev/lanes/capspike_rulings.md`: last entry read and
  applied is R1 (last-resort escalation). No `capspike_problem_N.md` was
  needed because no hard case failed.
- Premise test passed: the repo's libpcre2 binding (10.46 2025-08-27)
  returns group 1 = (1,2) "b" and group 2 = (0,1) "a" for `((a)|b)+` on "ab".
- Runs: every run was one niced Python process, all before 18:00. The
  population run takes about 130 s. Nothing was queued and nothing is owed.
- Reproduce (from `studies/dfacap_spike/`): `python3 cases.py 6 >
  results/cases.txt`; `CAPSPIKE_SABOTAGE=<s> python3 cases.py 4` for each of
  `noempty noctx fifo nocopy`; `python3 population.py results/population.tsv
  results/population_mismatches.txt`; `python3 summarize.py
  results/population.tsv > results/population_summary.txt`. Scratch goes in
  `$PCREC_TMPDIR/scratch/capspike/`.

## FINDINGS

**F1. A priority-ordered tagged DFA gives PCRE2-exact capture offsets on
everything the spike covers. No mismatch was found.** Every hard case in the
brief passes, on exhaustive subjects up to length 6 over each case's
alphabet (`results/cases.txt`: 70 cases, 0 failing). Over the census's
captures-only class, the spike admits 730 of 815 patterns (bench 21 of 22).
It ran 751,945 subjects (6,284 of them the corpus's own subjects, the rest
exhaustive per pattern) and compared all groups five ways against libpcre2:
the Pike reference, the unanchored TDFA, the anchored TDFA (against
`PCRE2_ANCHORED`), the realized copy-free machine (F4), and pcrec's own
`--engine=vm` artifacts. Every count is 0 (`results/population_summary.txt`,
"DIFFERENTIAL"). The pcrec VM witness also agrees with libpcre2 on all of
them.

**F2. Lazy operators: re2c's doubt does not apply to leftmost-first.**
`(a*)|(a*?)`, `(a*?)|(a*)`, `(?:(a*)|(a*?))b`, `(a*?)(a*)`, `(a*)(a*?)b`,
`(a+?)(a*)`, `(?:(a)|(ab))*?b`, `(a*?)(b*?)(a*)`, `(a{1,3}?)(a*)` and
`(a??)(a?)` all PASS (`results/cases.txt`, `lazy-*`). In this construction a
lazy quantifier is only the reversed order of two split edges. Two paths
merge only when they reach the same NFA node in the same closure context, and
the lower-priority one is dropped, as a backtracker would drop it. The
"fusion" re2c's maintainer feared belongs to longest-match semantics, not to
this one.

**F3. The empty-iteration rule (K18) costs no DFA state identity.** It is
carried by the closure's visited key `(node, loops entered in this closure,
end-condition)`. That key is local to one closure, so it never enters a
state. The controls (`results/sabotage.txt`) show this:
- `noctx`, the textbook Pike VM with visited keyed by node only: 8 cases
  fail. Example: `(a?)*` on "a" gives group 1 = (0,1); PCRE2 gives (1,1).
- `noempty`, which keeps the context key but drops the explicit "an empty
  iteration exits" check: 0 cases fail.

So in a loop built in PCRE's KET form (the exit edge sits on the iteration's
end node, not at the top split), the context-keyed visited set alone
reproduces PCRE2's rule. The explicit check is redundant there. This is a
simplification candidate for D3's K18 open-loop context (INFERRED: it
applies to the spike's NFA shape, and I did not check that pcrec's NFA has
the same shape).

**F4 (the main new result). Copies are an artifact of register naming. On
anchored machines the realized machine needs none, and it needs at most 6
registers.** As built (Laurikari-style, registers named per state), the
anchored TDFAs carry copies in 21% of patterns. The worst is
`((a)|b){0,64}c` with 640. Two allocation-independent facts remove all of
them:
1. **Fixed-offset classes.** A forward dataflow over the DFA finds the value
   classes whose value is `pos - k` on every path into a state, or
   `start + k` when the state's depth is unique. These need no register,
   because the accept reads them off the position. Anchored: 84% of
   patterns (616 of 730) have ONLY fixed classes, so they need zero
   registers and zero ops.
2. **Union-find colouring for the rest.** Union every destination class with
   the source class that feeds it. If no union set contains two classes of
   one state, colour the sets and every transition becomes sets only
   (`r = pos - k`), with no copies. Anchored: 730 of 730 qualify.
   Unanchored: 695 of 730.

`tdfa.Realized` builds this machine, and it is differenced against libpcre2
on all 751,945 subjects with 0 mismatches. It has its own controls:
`verify_fixed` checks every fixed-offset claim at every visited state on
every subject and finds 0 violations. A sabotaged offset table gives 177
violations on `(a|ab)*`, and a sabotaged colouring gives 53 to 309
mismatches on 4 patterns. Anchored realized machine: registers median 0,
p90 1, max 6; set ops for the whole DFA median 0, p90 2, max 216. I have
not checked whether BT22's fixed tags plus interference-based coalescing
reach the same result. Their fixed tags are syntactic distances between
tags, while these offsets are semantic, read per DFA state, so this may be
the "problem the literature found difficult" the brief hoped for (INFERRED;
not compared against an implementation).

**F5. Costs in states.**
- Anchored (Stage 1 shape): tagged states median 5 against untagged
  median 4. The ratio is median 1.00, p90 2.00, and exactly 1.0 for 454 of
  730.
- Unanchored (start tag inside the machine, Stage 4 shape): ratio p90 2.25.
  The as-built machines carry many copies there (median 1, p99 1,511), but
  the realized machine is still copy-free for 695 of 730.
- The worst ratio is `(a)(b)?(c)?(d)?(e)?(f)?(g)?(h)?(i)?(j)?`, with 513
  tagged states against 11 untagged. "Unset" is a compile-time constant in
  the state identity, so each optional group doubles the states. The usual
  fix is to hold "unset" as a register value (-1) when it would split
  states. That fix was not built here.
- Counted repeats of a capturing alternation (`((a)|b){0,64}c`,
  `((a)|ab){0,17}c`) are the other blow-up class, at about 5 times the
  untagged states.

**F6. What is out of the subset, and why** (85 rows, `population_summary.txt`
"OUT reasons"):
- Encoding gaps: UTF-8 constructs that match non-ASCII code points (19),
  multiline `^`/`$` (15), and `\p`/`\P` (8).
- Rows that are not really captures-only for the spike: `\G` (8), `\1` (8),
  possessive (5), consuming after `$` (5), and `(?(`/`(?>`/`(?*` groups.
- The spike's own Python caps: NFA over 3,000 nodes (6, including bench
  `datefinder-alternation` with 36 groups) and TDFA over 4,000 states (2,
  `((a)|ab){0,100}c` class).

None of these is a semantics refusal. Spliced subroutine calls (with the
capture tags stripped from the copy) and one-character context assertions
are inside the subset and pass. Those assertions are `\b`, `\B`, `(?=x)`,
`(?!x)`, `(?<=x)` and `(?<!x)`; they are held pending until the next byte
arrives, and that byte's tags are set at `pos - 1`.

**F7. The population found one bug in the spike itself.** In
`(?<=\w) *(a)`, the byte classes missed `\w` because a lookbehind on `\w`
reuses the `\w` slot. Pike was right and the TDFA was wrong. It is fixed,
and the case is kept as `ctx-lb-word`. The differential does catch defects
in the construction.

## WHAT WORKED

- The construction (`studies/dfacap_spike/tdfa.py`) has five parts:
  - TNFA with priority-ordered split edges.
  - Tags on capture open/close. Counted-repeat copies share tag ids, so
    desugaring creates no new tags; BT22's reason not to desugar is
    POSIX-specific.
  - Loops built in KET form (ENTER/BACK).
  - One closure shared by the Pike reference and the TDFA. It is a
    priority DFS that stops at the first unconditional accept.
  - TDFA states keyed on the ordered endpoint list plus a canonical
    VALUE-CLASS partition per live tag. All tags written in one transition
    share one value (`P`), and "unset" is a constant.
- End assertions (`$`, `\Z`, `\z`) become conditional accepts. The
  one-character context assertions become pending threads that resume when
  the next byte arrives. This is a TDFA(1)-style lookahead used only where a
  pattern needs it.
- Liveness pruning of dead tags keeps tagged states equal to untagged ones
  for 62% of anchored patterns.
- The allocation-independent analysis (`analyze`) and the realized
  copy-free machine (`Realized`), F4.
- Oracles: libpcre2 through the repo's borrowed ctypes binding
  (`docs/design/eng_brep_measurements/probes/pcre2_ctypes.py`, with
  `PCRE2_ANCHORED` for the anchored machines), and pcrec `--engine=vm`
  artifacts through a batch driver. That is one gcc build per pattern, not
  one process per subject.

## WHAT FAILED

- Nothing failed on semantics. The textbook alternatives fail and are kept
  as the controls: node-keyed visited (`noctx`, 8 cases), last-wins dedupe
  (`fifo`, 5 cases), and dropped copies (`nocopy`, 28 cases).
- The as-built Laurikari register naming is a poor allocator: up to 118,247
  copies in an unanchored bench-sized pattern. Do not ship that allocator.
  Use F4.
- Unanchored, 35 patterns are not copy-free even after F4. They are
  overlapping restarts that carry one group from two start threads
  (`(a+)b(?1)c`, `((a)|ab){0,7..}c`, `\B(x|ab){1,2}\b`). Stage 4 needs
  copies or a second register set for those. Stage 1 (anchored) never
  does.
- Not measured: emitted C. The spike is an interpreter. Everything about
  C cost below is an estimate.

## OPINIONS (brief item 6)

1. **The approach is validated.** Leftmost-first tagged determinization
   over pcrec's D3 construction is PCRE2-exact on the whole captures-only
   class it can parse, lazy and K18 cases included. §2.2 of the research
   memo can move from INFERRED to MEASURED (spike), within the subset in F6.
2. **What the product should keep:**
   - State identity = ordered thread list plus a canonical value-class
     partition per thread over LIVE tags. That is D3's key plus a vector
     per thread, which is the "seam" [COND-FAMILY] should leave open.
   - Closure-context keys, not explicit empty-iteration checks (F3).
   - Shared tag ids across counted copies.
   - Fixed-offset classes and union-find colouring instead of per-state
     register naming (F4).
   - Pending one-byte context assertions.
3. **Stage 1 admission rule (proposed):** anchored inside the hybrid window,
   admitted when `analyze()` reports `copyfree_nf` (no union set clashes
   within a state) and the state count is within the DFA cap.
   `allfixed` is the sub-level that needs no registers at all (84%). On this
   population that admits 730 of the 730 parsed rows, so the rule rarely
   bites. The real limits are state blow-up (F5) and the encoding gaps
   (F6). Copies in the as-built machine are not a useful admission signal.
4. **C emission cost (ESTIMATE, not measured):**
   - The realized anchored machine is the untagged DFA (states median ×1.0,
     p90 ×2) plus: a register file of 0 to 6 `ptrdiff_t` locals; median 0
     set ops in the whole machine (p90 2); per accepting state, one
     capture-write block of `2 × ncaps` stores, each `pos - k`, a register,
     or -1.
   - So the hot loop is the existing DFA loop. Most patterns add nothing to
     it, and the rest add a store on a few edges.
   - Size: roughly the DFA's table plus `ncaps × accepting states` stores.
     Compare that against the VM program it replaces.
   - The emitter work is the abi-event part: one new entry form, not a new
     engine. Unanchored Stage 4 adds up to 8 registers and, for 35
     patterns, copies.
5. **"Design the machine so tags can be added later" (the question the
   brief is for):**
   - The seam is the per-thread value-class vector in the state key, plus a
     per-transition list of "feeds" (which source class or position feeds
     each destination class).
   - The feeds list is what both `analyze` and the emitter read, and it
     serializes as text (`pcrec-plan-as-text-seam`).
   - Everything else in F4 is a pass over feeds, not a change to the subset
     construction.
6. **Not shown:** UTF-8 code-point constructs, multiline anchors, and the
   size-cap tail. These are coverage gaps of the spike, not open semantics
   questions. The VM witness stays the control for any build (memo §5.3).

### Proposed rows and decisions (the manager files)

- [ENG-TDFA] `refs:` + `studies/dfacap_spike/` and this report; `next:`
  Stage 1 can skip the counting probe (Stage 0 is answered: 0 mismatches,
  anchored copy-free 730/730), and keep its trigger ([CAPTURES-DFA-MB]).
- A D3 addendum (proposed): the tagged extension is MEASURED exact on the
  spike subset. The K18 rule rides the closure's visited key (F3), and the
  K18 open-loop context in `src/ir/dfa.c` is worth a simplification check
  against this.
- A BOONIES row (proposed, unscheduled): "unset as a register value" to cap
  the optional-group doubling (F5), measured only if Stage 1 meets it.

## OWED

- No runs are owed. All validation in this report is complete and
  committed.
- Not done, by scope:
  - a C emission twin (F4's cost is an estimate);
  - multiline and UTF-8 code-point coverage;
  - a comparison of F4 against BT22's own register optimizations.
