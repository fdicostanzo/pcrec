# EMIT lens: emitted vs replaced (crit-memfn-sp1d)

SUBJECT e9e5f035e vs BASE daf6f002b. Read-only; no denied file opened.
I read each BASE/SUBJECT pair side by side, worked out where they could
differ, then built witnesses to reach those conditions. The emitted C of
every compile was diffed, and so was the MFTRACE output (WCAND lines
excluded).

## FINDINGS

### EMIT-1: the WCAND `walked` field is 1 on positions that are not RESEED walked offsets (trace_format.md says RESEED only)
CONFIRMED. Severity: doc (trace honesty). Effort: XS. Blast radius: trace
readers only; no emitted byte.
memfn/docs/trace_format.md (WCAND, `walked`: "1 iff a RESEED walked offset
(A-model's domain...)") vs memfn/src/window.c `walked()` / `cands()` /
`trace_cands()`. `walked()` is `len == 1 && start != 0` and never reads the
alternative's `entry`, so any one-position span at a nonzero offset on a
NONE or PARKED alternative is put on the walk list and traced `walked=1`.
Repro (tr-subject):
    tr-subject/pcrec -p rx --features all -e utf8 -o x.c --pattern '\bfoo\b'
prints `alt=0 off=-1 members=193 ... core=0 stop=0 walked=1` and the same
at off=3. That site's Table A shows `A-parked ... fields=entry:R2:NOENTRY`
(entry NONE, single alternative). `(?<=x)yz` gives `alt=0 off=-1 ...
walked=1` in the same way. Across all my sweeps, 6 records had alt=0 and
walked=1.
Behaviour is the same as BASE: BASE's `a_model_holds`/`a_model_choose`
also read every `walked()` span whatever the entry. For `(?<=x)yz`,
A-model's predicate HOLDS on the NONE alternative in both trees and the
gate declines it on `entry`. So the walk list is "one-position spans at
offset != 0, any entry", and the record says what the list holds. The doc
sentence is what is wrong.
Fix: either say "1 iff a one-position span at a nonzero offset (A-model's
input list, any entry)", or trace `walked` only on a RESEED alternative.
Which one depends on what the record is meant to show.

### EMIT-2: WCAND is documented "before its WPATH", but a decision whose Table E row draws no WPATH writes WCAND with no WPATH after it
CONFIRMED. Severity: doc. Effort: XS. Blast radius: a trace reader that
pairs WCAND groups with WPATH lines.
trace_format.md WCAND paragraph ("...in alternative then offset order,
before its `WPATH`"). compose.c writes WPATH only `if (wpath)`.
Repro: `tr-subject/pcrec -p rx --features all -o x.c --pattern '(^)*ab'`
prints wfA/wfM, two WCAND records, then `END table=wfE ... chosen=E-func`
and no WPATH. In my 80-pattern corpus sample, 7 (pattern, arm) compiles
had WCAND>0 and WPATH=0 (`(^)*ab` x3 arms, `^(?:(a)(b)\2\1)+$` x4 arms).
No consumer pairs them today (see PROBED (c)). Fix: "before its WPATH
where one is written (a define whose Table E row draws none writes the
WCAND records alone)".

### EMIT-3: after C-bound, the plan's order differs from BASE's before C-asc sorts it (no emitted effect today)
CONFIRMED by derivation; no emitted effect. Severity: maintenance. Effort:
XS to document, S to make order-preserving. Blast radius: any future
T-VERIFY row placed between C-bound and C-run that reads plan ORDER, or a
re-ruled ordering row.
window.c `c_bound` walks `poff` from the end and calls `plan_drop`, which
moves the LAST entry into the freed slot. BASE never added the full-set
positions, so its pre-sort plan was in step-2 offset order. Example: a
floor plan over offsets 0..4 with offset 1 full is [0,2,3,4] in BASE and
[0,4,2,3] in SUBJECT. Every reader between C-bound and the sort uses set
semantics: `c_pin`/`tested_elsewhere` go through `in_plan`, `c_stop` is a
`plan_drop`, and `c_model` appends. `c_run` calls `c_asc` before it reads
adjacency, and C-asc re-sorts. Offsets are unique (`plan_add` dedupes), so
the sorted result is the same, and every compare in PROBED-AND-HELD was
byte-identical. Name this in the C-bound/C-asc comment ("the plan is a
SET until C-asc"), or make `plan_drop` keep order (memmove). Then a future
order-reading row, or a C-asc re-ruled to "most selective first" with a
stable tie on insertion order, cannot pick up a hidden difference from
BASE.

## PROBED-AND-HELD

Derivation (BASE vs SUBJECT, every rewritten piece):
- `kit_pick_takes` / KIT_PICK_NONE {-1,0,0}: the first candidate is always
  taken because pos<0. That matches BASE's `best<0`, `bk<0`, `b.pos<0`
  and `w == lo_s` openings.
- A-mass: `p->mass`, `stretch` and `stop_ok` are computed once in `cands`
  from `p->set`. `merge` is the only writer of `p->set`, and `d->rate` is
  set before `cands`, so the inputs are the same as BASE's choose-time
  `kit_mass`. `kit_mass` is pure (presence.c:77), so pricing more
  positions has no side effect. holds is `any_stop`, the same as BASE's
  `mass_domain` scan. `m->stop = best.key = k+WF_LO`, the same as BASE.
- A-model: the walk list is the `walked()` spans in span-index order, the
  same order BASE used. `order[]` (all other walk entries) equals BASE's
  `walked(j) && j!=si`. f0_mass equals BASE's `mass[f0]` (CAP, own set[0]).
  The T_MODEL key is the span start in both. `m->nwalk <= nspan <=
  MF_WMAX_SPAN` (wf_check), so `walk[]` cannot overflow, and `merge`'s
  memset resets nwalk and the any_* accumulators for each alternative.
- kit_run_member: the `after` skip `!kit_pick_takes(&c, after.mass, R,
  after.pos)` with c.pos=j>=0 expands to `ms < after.mass || (ms ==
  after.mass && !tie(R, after.pos, j))`, which is BASE's test exactly. The
  main pick's key is j, as in BASE. With no position found, mass
  (uint32)b.v is 0, as in BASE.
- C-bound: C-floor holds iff !has_stop and C-yes holds iff has_stop, so
  `has_stop ? yset : rd_set` is per-row BASE. `rd_set` reads `d->reseed`,
  which `c_floor` sets before its add loop in both trees and nothing
  changes before c_bound. Only step-2 rows add before C-bound (run_member
  adds nothing). Capacity cannot bind: `plan_add` caps at WF_NPOS and
  offsets are unique positions. C-model's full-set walked picks are never
  chosen (cost rises), so C-bound running before C-model drops nothing
  BASE kept. Order: see EMIT-3.
- C-member as table row 0 (c_always): runs at the same point as BASE's
  `run_member(d)` before the loop. `wf_crows[].rule` has no reader other
  than c_plan (grep), so the text change reaches no output.
- presence P3 set pick: the key is the same `member_key`. P3 window: the
  loop can be empty only if lo_s > hi_s, which needs n < MF_PRES_WINDOW or
  scan < 0. The branch requires n > 8, and kit_run_member(exact=0, n>0)
  always returns a position, so BASE's `at = lo_s` fallback and SUBJECT's
  `at = bw.pos` (-1) cannot differ. That is an internal invariant, not
  reachable by a caller, so no finding.
- gate.c cl_run, generic.c pred_test, run_cmp_sat/run_pos_sat: same truth
  table, including a NULL mask (EXACT, and sat = 1). The order in which
  UNSAT and MASKED are detected cannot change the class.
- sizeof wf_dec grows by about 0.8 KB (heap or arena; R-28 holds). The
  "~10 KB" comment is still roughly right.

Compares (SAME = identical emitted C and identical MFTRACE minus WCAND;
REJ = rc 1 on both sides):
- w1, 29 targeted witnesses (full-set positions, ties, runs > 8,
  lookbehind, RESEED/parked pairs, masked runs, alternations), default
  arm, trace builds: 29/29 SAME. 28 reached the window family (paths
  mass, mass+pin, parked, reseed, reseed+pin).
- w2, 63 (arm, pattern) lines: all of pres_pick_witnesses.tsv with their
  own arms/denies, plus 34 edge witnesses (40-byte runs, (?i) runs > 8
  under no-window-search, (?s) dot spans, two-alt dot sites, back
  context, \b, [\x00-\xff]): 63/63 SAME.
- 80 sampled corpus patterns (seed 1104, of 5015 distinct .rxt patterns)
  x 4 arms, trace builds: 300 SAME, 20 REJ (5 rejected patterns x 4), 0
  moved. 194 of them traced WCAND.
- Release binaries (base/build/pcrec vs worktree build/pcrec), 20 window
  witnesses x 4 arms: 80/80 SAME.
- Rate regimes, 20 window witnesses, trace builds: adversarial `inverted`,
  `onehot-80`, `uniform` (all-tie), and `-e utf8` + `random-20260927`:
  80/80 SAME. NONE is covered by every `-e utf8` arm above. COMMON's
  `--analysis uniform` is refused by both builds (rc 1, "unknown
  analysis", 20 REJ compares); the working spelling is `-I
  tests/findings/adversarial --analysis=uniform`.
- (a) MFTRACE: no REACH, ROW, END, SEL, FDROUTE or WPATH line moved on any
  of the compares above (TSAME everywhere).
- (b) reach_equal.py --limit 20 --jobs 2, default 4 arms: `reach_equal:
  LIMITED rc=0 keys=120 differ=0`, rows 30/30 per arm, 0 gone rows, 1
  pattern rejected the same way on both sides per arm. Log:
  EMIT/reach_equal.log.
- (c) WCAND format: the printed fields and their order (table= art= site=
  phase= alt off members mass core stop walked key incumbent) match
  trace_format.md, apart from EMIT-1 and EMIT-2. Consumers: rows_check.py,
  finder_check.py, reach_equal.py, run_g2*.sh/py and run_g2_gate.sh match
  on exact prefixes ("MFTRACE REACH ", "MFTRACE FD ", "MFTRACE FDROUTE ",
  "MFTRACE END ", "MFTRACE ASK ", "MFTRACE REACH_DROPPED"), or strip all
  MFTRACE lines (run_g2.sh:269). No consumer counts all MFTRACE lines or
  matches a WCAND prefix, so nothing chokes or miscounts. scripts/ has no
  MFTRACE reader.

Compile count: 1350 pcrec compiles (1190 logged in EMIT/compiles.log,
probe scripts and single probes together, plus 160 from reach_equal's
20x4x2). reach_equal's enumerate_corpus also made 226
list-source calls, which are not compiles. All runs used `nice`; no make,
no boxlock.
