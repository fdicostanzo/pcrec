# crit-memfn-sp1e — lens EMIT (emitted-vs-replaced)

Subject 9de5b5638 (lane/memfn-sp1e) vs BASE 20fb73159. Probe harness:
EMIT/bin/probe.py (BASE/SUBJECT under the same basename `x` in runs/cur/{b,s},
outputs x.c + x.h compared byte-for-byte, rc, stdout, stderr with MFTRACE
lines split off). Log: EMIT/log.jsonl (one line per pair). Denylist: nothing
denied was opened.

## FINDINGS

No emitted-byte mover was found: 384 BASE/SUBJECT pairs, every one SAME
(rc equal, x.c and x.h byte-identical, stdout equal, non-MFTRACE stderr
equal). Both findings below are by inspection and move no byte.

### EMIT-1: D-hors's `core CORED` contract is never checked in its new table (CONFIRMED by inspection; maintenance; effort XS-S)

- Where: memfn/src/finder.c:215-216 (`ct_d_hors`, FD_CT_T(..., CM(CORED))),
  finder.c:528-533 (`fd_decide`), finder.c fd_find (`gate_in in = { s, def,
  NULL, &q.ff, st ? st->wf : NULL }`).
- The defect: `fd_decide` builds its own walk input
  `gate_in in = { q->site, NULL, NULL, &q->ff, NULL }` and hands that to
  `kit_walk`. `walk_row` runs `gate_check(c, gphases, in)` on that input, so
  the wf facts and def that fd_find now sets reach only the trace context
  `tc`, never the gate. `cl_core` (gate.c:588) returns -1 (unstated) when
  `in->wf` is NULL, and every T-FIND row is served. At BASE, Table D's gate
  read `core` from `&f` (window.c `wf_find_decide`, `in = { s, def, NULL, NULL, &f }`).
  1e moved D-hors from a gate that checked `core` to one that cannot.
- Why no byte moves: `hors_facts` sets SF_HORS_WINDOW only when
  `hors_window` found a verify-YES span with `core_len > 0`, and that already
  makes `cl_core` CORED. Table D's other serves were all MF_ANY.
- What is wrong: the 1e change spends code on this dead check. It adds
  FD_SERVES_COMMON's six window fields, the `cores` parameter of
  FD_SERVES_REST/FD_CT_T, and threads `st->wf` into fd_find's gate_in. Two
  comments describe a check that never runs. finder.c:169-176 says "every row
  serves them all but D-hors, whose window is a stated core (`core` CORED,
  Table D's contract)". finder.c:212-214 says the same. If a later change to
  D-hors's facts drops the core prerequisite, the gate will not catch it.
  The walk's gate_in also carries no `def`. That was already true for D1..R7w
  before 1e; it is new only for D-hors.
- Fix: pass fd_find's `in` into `fd_decide` (and check that D1..R7w still
  serve whatever `def` then states), or delete the dead clause and the two
  comments.
- Blast radius: D-hors only. No answer, speed or size effect today.

### EMIT-2: plan_cost.def still says HORS_MIN belongs to "window.c Table D" (CONFIRMED; doc; effort XS)

- memfn/src/plan_cost.def:22-23: "HORS_MIN (§3.3's last row) is D-hors's
  (window.c Table D)". Since 1e, D-hors is T-FIND's row in finder.c, and
  finder.c `hors_facts` reads HORS_MIN (FD_COST_HORS_MIN). plan_cost.def is
  not in the diff, so nobody updated this comment. Every other "Table D"
  mention in memfn/src, tests/memfn and trace_format.md is worded as
  history ("until 1e").

## PROBED-AND-HELD

Compile count: **1400 of the 1400 budget** (one pair is 2 compiles; both
reach_equal runs are included).

- **Corpus, default arm, prior regime:** 274 patterns, all SAME.
  - Population: 5009 distinct .rxt patterns enumerated with --list-source
    (no compiles). Stratified per directory toward fixed-width patterns;
    tests/offsetskip, landwalk, altcls, island and rungselect taken whole.
  - Sites reached, from SUBJECT's MFTRACE:
    - composer: D1/pf_memchr 69, R7w/pf_walk 42, R7w/pf_walk_bounded 7,
      D1w 4, D1/pf_memchr_bounded 2;
    - E-find: D1 37, R7w 20, PAIR (B-pair) 4, D-hors 3;
    - ofsskip (reseed/parked: B-fn's legacy function frame) 26.
- **Horspool witnesses (round 2):** 8 patterns x (default with prior / all-tie
  / weblog, --engine=vm, -fmemfn-simd, -e utf8) = 48 pairs, all SAME.
  - Patterns: [0-9a-f]{8}, \b[0-9a-f]{8}\b, [a-z]{4}, [0-9]{3}-[0-9]{4},
    [A-Za-z]{2}[0-9]{6}, (?i)[a-z]{5}x, [0-9a-f]{2}:[0-9a-f]{2}, [ -~]{3}[ab].
  - Horspool admission flips across regimes, and each flip is identical on
    both sides:
    - hex8 and [a-z]{4}: D-hors under prior and weblog, R7w under all-tie
      and NONE;
    - [A-Za-z]{2}[0-9]{6} and [0-9]{2}[a-z]{2}: D-hors only under weblog;
    - [0-9A-Za-z]{4}: D-hors under NONE (uniform mass), all-tie, prior,
      weblog and simd.
  - VM arm: no window site (pf_walk R7w).
- **Deny flags (round 3):** 50 pairs, all SAME.
  - no-window-skip alone. D-hors falls to R7w on hex8 and alnum4, also under
    simd, weblog and NONE. The PAIR witnesses (x[Q%]y, (?i)cat,
    (?i)abcdefgh, [ae]{4} and [ e]{3} on weblog) keep PAIR, with the asker
    fact both on (E-find) and off (composer).
  - no-window-search, no-fd-d1, no-window-skip,no-fd-d1, and
    no-window-skip,no-window-search.
  - B-fn vs B-pair: the (?i)cat / (?i)abcdefgh cube and -fmemfn-simd vrun
    rungs vs x[Q%]y's two streams.
  - Multi-literal windows: abcd|efgh|ijkl in 4 regimes.
  - Composer rows: D1 (x+y under simd and NONE), D1w (no-fd-d1, vm), D1c
    ((?m)^ab under NONE), R7w with -fno-offset-skip --engine=vm.
- **MF_TRACE vs plain builds:** on 9 cases the SUBJECT plain build's C is
  byte-identical to the SUBJECT trace build's (sha1 over x.c+x.h). Each plain
  pair was also SAME BASE-vs-SUBJECT.
- **reach_equal.py --limit 150 --jobs 2 --map tests/memfn/row_map.tsv**
  (tr-base vs tr-subject), arms '' and --engine=vm only.
  - Why 2 arms: 4 arms is 150x4x2 = 1200 compiles, the whole budget.
  - Verdict: `patterns differing 0` on both arms, rows 31/31, 9 identical
    rc1 failures per arm, gone rows none,
    `reach_equal: LIMITED rc=1 keys=62 differ=0`.
  - The rc=1 comes only from `FAIL: map target fd/D-hors never chosen at
    HEAD (the map is unexercised)`: the first 150 sorted patterns reach no
    D-hors (mapped chosen BASE 0 HEAD 0).
- **reach_equal targeted run** (`--no-corpus --patterns-file hors.pats`:
  hex8, alnum4, [a-z]{4}, x[Q%]y), all 4 arms.
  - `patterns differing 0` on every arm.
  - `mapped wfD/D-hors -> fd/D-hors: chosen BASE 7 HEAD 7`.
  - D-one dissolved: '' 1, vm 0, simd 1, utf8 3.
  - `reach_equal: LIMITED rc=0 keys=124 differ=0` (exit 3 = clean smoke).
- **Equivalence by inspection** (what the SAME results rely on):
  - Every BASE reader of `drow` maps one-to-one onto `bren`: head/next/define
    text, prepare, the path suffix "+hors", and libc (B-hors libc 0 = BASE's
    bren NBROWS).
  - The HORS_MIN reading is identical: same kit_mass call, same
    unsigned-long-long cast, same rates `d->rate`.
  - The deny `window-skip` is read the same way (site opts, kit_walk).
  - The composer never meets D-hors: no SF_HORS_* fact when `st` is NULL.
  - The fd_route-to-fd_renderers table matches the deleted switch row for row.
  - The only new reader of D-hors's `brow` is the MF_TRACE FDROUTE/WPATH
    print.
  - pres_row/pres_led's index move (MF_CLASS_V 8) is read by pcrec only under
    PCREC_CAND_TRACE (memfn_sites.c:728-747).
- **Not run:** the matcher's answer checks, because there was no mover to
  check.
