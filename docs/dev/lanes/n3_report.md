# n3 report: [MEMFN-ROWCON] N3, the row-contract gate ENFORCES

Lane n3 (opus), 2026-10-07, Linux dev box. Branch `lane/n3`, cut from the
kit branch `lane/memfn-n3` at main 038ed335. Kit-only, plus the kit's own C5
fixture test. NO `src/` change is committed. A scratch R-6 was built once
and reverted (§4.3). Design of record: `docs/design/memfn/row_contracts.md`
rev 4.1, §1, §2 and §5 (N3). Nothing in §6 was built.

Commits on top of 038ed335:
- `3e25cd36`: enforcement, the rulings and the --gate cases.
- `0214280d`: the trace stays an honest census; the split rows test their
  own handoff; citations re-derived.
- `cb434ef7`: memfn.h text, trace_format.md, the CLAUDE.md files and the
  N2 lock override.
- (this report).

## 1. Rule-by-rule changes

**One verdict, now acted on** (`gate_check`, unchanged; gate.c).

**DEFINE, the arm walk** (`compose.c` `select_arm`).
- Each row's gate verdict is taken BEFORE its predicate.
- A failing row is DECLINED (trace `ROW verdict=DECLINED`) and the walk
  moves on.
- No row left means `mf_define` REFUSES:
  ``mf_define: no row serves this site: `fn_ref` (R1: used, not stated)``.
  The fields named are those of the last row the walk declined, the generic
  row: it applies everywhere, so only the gate can leave a site with no row.

**DEFINE, the run walk** (`runcmp.c` `rc_row_of`).
- The same: deny, then the gate, then the predicate.
- No row left records the refusal itself:
  ``runcmp: no run-compare row serves the RUN term: `run` (R2: stated as UNSAT, not served)``.
- `run_cmp_render` and `run_cmp_prepare` return it.
- Every caller already filters unsatisfiable runs (`run_cmp_sat`), so pcrec
  never reaches this refusal.

**USE** (`mf_use`, and so `mf_call`). The chosen row is re-checked against
the use hooks. A failing use is REFUSED, with no re-selection:
``mf_use: row `ofsskip` does not serve this use of handle 1: `floor` (R2: stated as OTHER, not served)``.

**(d) Every refusal names its field.** One writer, `gate_describe` (gate.c),
names every failing field in backquotes with its rule and class. G2's
`names_field` accepts that spelling (backquoted).

**WARN-only state removed** (kit.h): `site_rec.warn_define`/`warn_use` and
`mf_art.run_warns`.

**(a) F1: non-identifier `s`/`n`/`lo`.**
- `s`, `n` and `lo` are now read at DEFINE as well as USE
  (fields.def phase `MF_PH_DEFINE | MF_PH_USE`).
- A define that STATES a non-identifier is declined by every raw-pasting row
  (they serve IDENT only) and reaches generic, which parenthesizes.
- A define that leaves them unstated selects as before; the use re-check
  then refuses the shape, naming `s`/`n`/`lo`.
- pcrec states none of these at a define, except VMRUN's `mf_emit`, which
  passes identifiers. So no pcrec selection can change.

**(b) Unstated `miss`.** No code change was needed: N1's contracts already
put `miss` in the `uses` of ofsskip (define and use) and of the pre-check's
ASSIGN (use). Enforcement makes R1 real:
- ofsskip is declined at define, and its call is refused;
- the pre-check's ASSIGN use is refused;
- generic refuses RETURN/ASSIGN through its own `uses`.

**(c) K-1, `fn_ref` 0 on a FUNC site. The general mechanism:** `fn_ref`
left the OBLIG exemption list and became what it is, a HOOK ID.
- Its classifier (`cl_fn_ref`) returns UNSTATED for 0, exactly as a NULL
  hook does; fields.def `absent` is HOOK, class set REF|OTHER.
- Every row that renders a function name puts `fn_ref` in its FUNC-form
  `uses`: generic `{FUNC, any handoff, DEFINE}`, ofsskip
  `{FUNC, RETURN, DEFINE}`.
- So a FUNC site stating 0 is declined (R1) by every row, generic
  included, and refused naming `fn_ref`, for every op.
- On a non-FUNC site no row uses `fn_ref`, so its 0 is a wildcard (R1
  applies only to USED fields).
- **No FUNC special case exists in the gate or in fields.def.** The FUNC
  scoping lives where every other field's scoping lives, in each row's
  `uses` (form, handoff, phase). `table_ref` stays OBLIG; no ruling
  touched it.

**§5 "precheck serves a stated `miss`" and "a shape-dependent row is
split".**
- The pre-check's text depends on `miss` BY HANDOFF:
  - an ON_MISS site writes no value, so its text is right for every
    stated miss;
  - an ASSIGN site tests the run call's result `>= n`, which is right only
    for `MISS_N`.
- `serves` is per field, not per handoff, so the one renderer is now TWO
  rows:
  - `precheck_arm` (ON_MISS): serves `miss` ANY, `ret_pred` NONE;
  - `precheck_assign_arm` (ASSIGN): serves `miss` MISS_N, uses
    result|miss.
- Both report form id `precheck`. The pins and G2's per-form floors are
  unchanged.
- Each row's predicate tests its own handoff, so its predicate and its
  contract name the same sites.
- Hook SHAPES (IDENT/JUMP/BRACED) are DECLINED, never split: a raw-pasting
  row serves only IDENT/JUMP/BRACED, and generic serves OTHER.

**4. ofsskip's ad hoc K96 checks replaced** (§2 below).

**6. MF_TRACE** (`memfn/docs/trace_format.md` updated).
- New ROW verdicts: `DECLINED`, and `DECLINED:PRED_HOLDS`.
- A trace build also asks a declined row's predicate. Every predicate is a
  pure function of the site and the hooks; a non-trace build never asks it,
  via `GATE_TRACING`, which needs no `#ifdef` in the walks.
- `END would_decline` KEEPS N1's meaning on the enforcing build:
  - at define/run it is 1 iff the gate MOVED the selection (the first row
    whose predicate held was declined), with that row's `fields` and a new
    trailing `moved_from=<row>`;
  - at use it is 1 iff refused.
- A no-row `END` now carries the refusal's `fields`.
- So `n2_census.py`/`n2_report.py` read an N3 build unchanged. On an
  enforcing build, without this, the census would read zero by construction.
- `n2_census.sh` gains `N2_LOCK`. Its Mac lock path makes the script wait
  forever on Linux; it is the only probe change.

**7. Docs.**
- memfn.h: the enforced-contracts paragraph at `mf_define`/`mf_use`, and
  ruling F1 at `s`/`n`/`lo`. Comments only, so no `MF_SITE_ABI` bump: the
  K-1 and `miss` meanings were already stated there.
- `memfn/src/CLAUDE.md`, `tests/memfn/CLAUDE.md`.
- **docs/spec/: no hunk.** No pcrec caller observes a change once R-6 is
  under N3: the same rows render the same bytes (§4). Before R-6 the change
  IS observable, as an internal-error refusal, which is why the merge order
  below matters.

## 2. Deleted ad hoc checks and their gate replacements

All four deletions are in `memfn/src/ofsskip.c`; the old text is in 038ed335.

| deleted | was | replaced by (gate) | shown by (`tests/memfn/arm_fixtures.c --gate`, `run_arm_pins.sh` check 6) |
|---|---|---|---|
| `ofs_fn_applies`: `def->floor` test | a stated floor at define → generic | ofsskip/precheck `serves[floor] = 0`, R2 at define | `ofs-define-floor`, `pre-define-floor` → RENDER generic |
| `ofs_fn_call`: "states a floor its definition did not" | refusal at the call | R2 at the use re-check | `ofs-call-floor`, `pre-use-floor` → REFUSE `` `floor` `` |
| `miss_is_n` in `ofsskip_applies` (define) | a non-`n` miss → generic (an UNSTATED one was read as `n`) | `uses` miss + `serves` MISS_N: R2 (other) and R1 (unstated) at define | `ofs-define-miss-other`, `ofs-define-miss-unstated` → RENDER generic |
| `miss_is_n` in `ofsskip_use` | "the call's miss is not its n" | R2/R1 at the use re-check | `ofs-call-miss-other`, `ofs-call-miss-unstated` → REFUSE `` `miss` `` |

Also deleted as gate-duplicated: `s->pred.fn_ref && def->fn_name` in
`ofsskip_applies`. The gate's R1 on `fn_ref`/`fn_name` now holds it, and the
case `ofs-fn_ref-0` refuses `` `fn_ref` ``.

**The other gate cases** (20 in all):
- `ofs-define-nonident` (RENDER generic) and `ofs-call-nonident` (REFUSE
  `s`);
- `allp-func-fn_ref-0` (REFUSE `fn_ref`) and `allp-func-fn_ref-7`
  (RENDER generic: the positive control);
- `pre-assign-miss-unstated` (REFUSE `miss`), `pre-assign-miss-token`
  (RENDER precheck), `pre-assign-miss-other` (RENDER generic) and
  `pre-onmiss-miss-other` (RENDER precheck: the split);
- `pre-define-nonident` (RENDER generic), `pre-use-nonident` (REFUSE `s`)
  and `run-nonident` (RENDER generic).

**The gate is what covers them.** A scratch plant turned the gate off: both
walks' decline and the use refusal became `if (0 && …)`, built into
`BUILD_DIR=<scratch>` and never committed.
- Result: 19 of 20 cases changed outcome. Every K96 case rendered through
  `ofsskip`/`precheck`, and the floor and miss sites were no longer refused.
- The one case that did not change is `allp-func-fn_ref-7`, the positive
  control, as it must.
- No mech row was added: no `make mech` arm runs `run_arm_pins.sh`. If one
  is wanted, the plant above is the row (next free id after S599 on main);
  that is a manager call.

C5 pins: unchanged, 38/38 rows, every digest identical. The fixtures now
STATE `miss = MF_MISS_N`; their text is the same bytes as before, as lane
missn's token twins already showed.
`make test-memfn-arms`: **checks passed 104, failed 0** (was 81 before
check 6).

## 3. G2 `--quick` results (3 of 3 runs used, seed 20261005, `taskset -c 12-15 gnutimeout 2400`)

**The runs.**

| run | mode | checks passed | checks failed | rc |
|---|---|---|---|---|
| 1 | normal | 34,473,591 | 457 | 1 |
| 2 | normal `--keep` | 34,473,591 | 457 | 1 |
| 3 | `G2_STRICT_HOOKS=1` `--keep` | 37,342,131 | 457 | 1 |

Logs: `worktrees/memfn-slot/n3/g2q{1,2,3}.log`. Work dirs of runs 2 and 3
are kept under `worktrees/memfn-slot/n3/g2tmp{2,3}/`.

**The 457 failures, all from one cause.** It is ruling (c) working, and G2
is not yet aligned with it.
- **415** are `FAIL render site N: kit refused a contract site: mf_define:
  no row serves this site: `fn_ref` (R1: used, not stated)`. Base space
  gives 403 and sem 12. That is exactly G2u2's `fn_ref-unstated` population
  (415): G2 still GENERATES FUNC sites with `site.pred.fn_ref` 0 as hard
  contract sites.
- **41** are coverage MISSING cells (RUN term offset × length × mask), and
  **1** is `RUN cells 1565 < floor 1644`. Those cells were reached only by
  the 415 refused sites.
- G2 also reports "coverage count 80 is not its MISSING lines" against 41
  printed lines. That is G2's own count/print consistency check; it is
  downstream of the same loss, and it is G2's to read.

**The PENDING-ENFORCE classes under strict** (run 3: `strict_pass=326
strict_fail=0`; gcc-15 answer run passed 36,936,245, failed 0, over 9,580
sites):

| class | outcome | as a hard check |
|---|---|---|
| `hook-nonident` (F1) | 728 RENDERED (all through generic); 0 PENDING batches fail to compile (was 298 under N1); 2,868,214 checks, 0 failed, 0 faults | **PASSES** |
| `miss-unstated` | 0 rendered, 314 refused NAMING `miss` | **PASSES** |
| `refusal-unnamed` | 12 of 12 refusals name their field | **PASSES** |
| `fn_ref-unstated` | the kit refuses all 415 naming `` `fn_ref` ``, but G2 counts them as "kit refused a contract site" and never reaches its PENDING branch, which also has no `fn_ref` naming rule | **DOES NOT PASS: G2 change needed** |

Other G2 numbers (run 2):
- POISON: 8,852 sites, all identical.
- Families: 0 failed sites.
- Forms (hard sites rendered): generic 6,314, ofsskip 1,248, precheck 275,
  runcmp 1,015.
- The 4-id floor holds.

**Why precheck went from G2u2's 324 to 275:** N1's contract already had the
pre-check serve no stated `floor` (K96's decline), and N3 enforces it.
Floor-stating pre-check sites now render through generic. pcrec states no
floor, so nothing in pcrec moves. Note, not a change made here: under
Q-G2-6 (`floor <= lo`), neither ofsskip nor the pre-check reads below `lo`,
so serving a stated floor would also be sound. Keeping K96's decline is
N1's contract and the brief's, and I left it.

**G2 CHANGES NEEDED** (G2 is the blinded author's; I did not edit it):
1. `pend_class`: a FUNC site whose `site.pred.fn_ref` is 0 (any op) is class
   `fn_ref-unstated`. Where `miss` is ALSO unstated on RETURN, accept a
   refusal naming either field: the define refusal names `fn_ref`, since
   `miss` is a use-time field.
2. `pend_named(G2_PEND_FNREF)`: accept `` `fn_ref` `` (or `fn_name`). Today
   it returns 0 for that class.
3. Base-space FUNC sites should state a nonzero `fn_ref` (`fn_ref_on` forced
   on FUNC), so the 41 RUN coverage cells and the RUN-cell floor are reached
   by hard sites again. The fn_ref-0 sample then lives in class 1.
4. With all four classes enforced, G2 can retire the PENDING bucket, or make
   `G2_STRICT_HOOKS=1` its default.
5. Read the "coverage count 80 vs 41 MISSING lines" mismatch on the G2
   side.

## 4. pcrec single-compile evidence (40 of 40 compiles; traced build `-DMF_TRACE`)

Driver: `worktrees/memfn-slot/n3/pc.py`. Logs: `pc1.log` (30), `pc2.log`
(8) and the R-6 pair (2), all under `worktrees/memfn-slot/n3/`.

### 4.1 Without R-6 (this branch as committed): refusals at EXACTLY the N2 cells

Across 38 compiles, every refusal and every gate-moved selection is one of
N2's cells, `miss:R1:UNSTATED`:
- **ofsskip define** (moved to generic) **and its call** (refused). Seen at
  `(?!x)abc`, `(?(DEFINE)(?<g>\bab))(?&g)`, `user[0-9]+pass`,
  `foo(bar|baz)qux`, `abc[0-9]+xyz`, `[a-c]x[0-9]yz`, `Москва[0-9]` (utf8),
  `é@x` (utf8), and under `-fno-req-handoff`, `--tune=min-size` and
  `-fcomments`.
- **The pre-check ASSIGN use** (refused, row `precheck_assign`). Seen at
  `(?:(?i:ab)S|(?i:abs))`, `(?:(?i:sab)|S(?i:ab))`, `(?i)strasse`,
  `GET /index`, `(?i)userpass[0-9]` (`--tune=max-speed`),
  `(?!x)abc` (`-fno-offset-skip`), and the two utf8 patterns.

Every refusal text: ``pcrec: internal error: the memfn kit refused a site:
mf_use: row `generic|precheck_assign` does not serve this use of handle H:
`miss` (R1: used, not stated)``.

**No other pcrec site refuses or moves.** None did at the pre-check ON_MISS,
VMRUN `runcmp` (exact, masked `words`, `-fno-run-overlap`), the run walk
(`words`/`overlap`/`memcmp`), or patterns with no kit site. That is
23 compiles with kit sites, rc 0 where no N2 cell is present. **No STOP
condition was met.**

The first 30 compiles also showed one artifact of my own split: the ON_MISS
row "moved" ASSIGN sites, because the two rows shared one predicate. Fixed
in `0214280d`: each row's predicate tests its handoff. The 8 re-run
compiles show only the N2 cells.

### 4.2 Why the census needs `moved_from`

The trace change in §1 item 6 is what made 4.1 measurable on an enforcing
build: `DECLINED:PRED_HOLDS` rows are the selections the gate changed.

### 4.3 With a scratch R-6 (2 compiles, built into scratch, reverted, never committed)

The three lines tested, all in `src/gen/emit_dfa.c`, each `.miss = MF_MISS_N`:
- in `ofs_site_define`'s hooks;
- in `pf_ofs_call`'s hooks;
- in `pcrec_emit_req_byte_check`'s hooks.

Results:
- `--engine=dfa '(?!x)abc'`: rc 0, ofsskip chosen at define and use, no
  move, no refusal.
- `'(?i)strasse'`: rc 0, `precheck_assign` chosen, no move, no refusal.

If main's R-6 differs from those three lines, the census (§6) is the judge.

## 5. Anchors and sabotage rows

`python3 scripts/m6read_check_sab_anchors.py`: **497 sabotages, 515 anchor
sites, all resolve.**
- No anchor moved.
- S570's `if (rows[i].row.deny & art->denies) {` is kept verbatim.
- No row was anchored on the deleted K96 text.
- Nothing was re-pinned.

Rows whose SAB_FILE this change touches (from `tests/mech/rows_for.sh`):
S185 S265 S267 S279 S285 S443 S444 S445 S447 S450 S454 S455 S464 S526 S570
S573.

## 6. VALIDATION OWED (manager's slot)

Run from the merged tree, one heavy suite at a time, each wrapped in
`gnutimeout`.

1. **Merge main (with R-6) ALONE** under this branch:
   `git -C <wt> merge main`, read its result, resolve, then
   `make -j4 && make strict` (expect `strict: whole tree compiles clean`).
2. **The N2 census, BOTH builds.**
   - (a) main+R-6 without N3, if not already run.
   - (b) this branch merged with main+R-6.

   Each run, Linux:

       N2_LOCK=<scratch>/n2.lock CC=gcc JOBS=8 OUT=<scratch>/n2_<sha> \
         nohup bash docs/design/memfn/probes/rowcon/n2_census.sh > <scratch>/n2_<sha>.log 2>&1 & disown

   Completion line: `== N2 DONE rc=0 would_decline=0 ==`. In
   `$OUT/n2_results.md`, BOTH "would-decline selections" AND "selections
   with no row (kit refused the site)" must read 0. On (b), would-decline
   counts the selections the gate MOVED plus refused uses, so 0 means zero
   refusals at both phases. Check also that §4 lists every pcrec builder's
   row: `ofsskip`, `precheck`, `precheck_assign`, `runcmp`, and the four
   run rows.
3. **The identity gate**, against main's tip (with R-6):

       python3 scripts/emit_sweep.py --ref <main tip> > <scratch>/sweep.log 2>&1
       python3 docs/design/memfn/probes/lxrun/memfn_r4c_gate.py --zero-dumps <scratch>/sweep.log

   Expect `R4C-GATE PASS` (rc 0) with zero movers on every stream.
   `--zero-dumps`: no option row was added.
4. **Full G2, with `G2_STRICT_HOOKS=1`**, after G2 takes §3's changes 1-3:

       G2_STRICT_HOOKS=1 TMPDIR=<scratch> taskset -c <cores> gnutimeout 7200 bash memfn/tests/run_g2.sh --seed 20261005

   Expect `checks failed: 0`. Until G2 changes, expect exactly §3's
   failure: the fn_ref-0 sites refused naming `fn_ref`, plus their
   coverage cells.
5. **Full `make test`.** Its memfn sections are the ones touched:
   `test-memfn-arms` (104/0 here), `test-memfn-g2` (red until the G2
   change), `test-memfn-stamps`, `-deleg`, `-reach` and `-forms`. Before
   R-6 these are red by construction (pcrec refuses the N2 cells).
6. **Solo mech rows** (`bash tests/mech/rows_for.sh <changed files>`): S185
   S265 S267 S279 S285 S443 S444 S445 S447 S450 S454 S455 S464 S526 S570
   S573. Each solo:

       bash tests/mech/run_sabotage_matrix.sh <S-id>

## 7. Charter vs committed

| charter item | committed |
|---|---|
| 1. DEFINE: a failing row is declined and the walk moves on; no row is a loud refusal naming the fields (arm walk AND runcmp walk) | yes: `select_arm`, `rc_row_of`, `gate_describe` |
| 2. USE: the chosen row is re-checked; a failure is refused naming fields; no re-selection | yes: `mf_use` (and `mf_call`) |
| 3a. F1: non-identifier s/n/lo reaches only generic | yes: s/n/lo read at define (stated), declined by raw rows; refused at a use that states them alone. G2 hook-nonident 728/728 rendered and correct, 0 compile failures |
| 3b. miss unstated: decline, else refuse | yes, by enforcement of N1's `uses`; G2 miss-unstated 314/314 refused naming `miss` |
| 3c. K-1: FUNC with fn_ref 0 refused for every op, generic included; general mechanism stated | yes: `fn_ref` is a hook id (0 UNSTATED), used on FUNC by every name-rendering row (§1). G2 needs a change to count it (§3) |
| 3d. every refusal names its field | yes: one writer; G2 refusal-unnamed 12/12 |
| 4. precheck serves a stated miss; a shape-dependent row is split or declines the shape | yes: precheck split by handoff (ON_MISS serves any miss); hook shapes declined |
| 4. ofsskip's ad hoc K96 checks replaced and deleted, shown by test | yes: §2, 20 gate cases, plant 19/20 |
| 5. zero pcrec movers; which patterns refuse without R-6 | §4: exactly the N2 cells; with a scratch R-6 none; no STOP |
| 6. MF_TRACE decline/refuse records; trace_format.md | yes: DECLINED / DECLINED:PRED_HOLDS, END semantics, moved_from |
| 7. CLAUDE.md files; memfn.h text; docs/spec only if a caller observes | yes / yes / no spec hunk (§1 item 7) |
| G2 untouched | yes; 5 needed changes listed (§3) |
| box rules | 3/3 G2 quick runs (last strict), 40/40 compiles, make/strict/test-memfn-arms only, everything in gnutimeout, scratch in worktrees/memfn-slot/n3 |
