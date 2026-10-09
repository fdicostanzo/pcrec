# m7fix — the four defects M7's landing chain found

Lane m7fix (opus), 2026-10-08, branch `lane/m7fix` cut from the kit branch
`lane/memfn-m7` @ c9e90c77. Inputs: `docs/dev/lanes/m7_report.md`, the slot12
triage reports `worktrees/memfn-slot/slot12/{n2_triage,startset_triage}.md`.
LIGHT WORK ONLY (`taskset -c 12-15`, -j4): no `make test`, no mech matrix, no
full census, no full G2, no emit_sweep identity gate. Those are the kit
manager's re-validation slot (§6).

## 1. Summary (resume from here)

| # | commit | fix | evidence |
|---|---|---|---|
| 1 | `dc7ef868` | `inplace_applies` (memfn/src/mismatch.c) states the row's shape: STMT / MISMATCH / ON_DIFF / fold_kind ASCII or UCP / `kit_fold_shape(def->fold) == CL_FOLD_STMT` | 0 movers / 43,870 pairs; arms 286/0; rows 127/0; G2 --quick 48,566,739/0 with `mismatch_inplace` chosen 2,670 ≥ g2_floor 2,403; N2 sample would_decline 0 (pre-fix: 2,973) |
| 2 | `1ffcc5b7` | the census's zero rules enforced (rc 5), `moved_from` kept and reported as the declined row; sample runner + mech arm `n2sample` + row S668 | S668 hand-measured: clean rc 0, planted rc 5 (would_decline 85, declined row `mismatch_inplace`) |
| 3 | `d411f88f` | S512's `SAB_REACH_POP` re-pinned to `^C17_ROW_FLOOR=14[[:space:]]` (lane m6's form, e48cc296) | clean 13/0; plant 12/1, "13 rows, below its K35 floor of 14" |
| 4 | `a50c2ed7` | startset VM manifests +8 auto / +8 forced (the s670cell blocks); header line; tests/startset/CLAUDE.md note | `make test-startset` alone, pinned: 3/0, 22/0, 35/0 |

Closing checks: `python3 scripts/m6read_check_sab_anchors.py` 562
sabotages / 580 anchor sites, all resolve; `make -j4 strict` clean.
No abi event, no emitted byte moved, no `docs/spec/` hunk (nothing a caller
observes changed: fix 1 changes only which row the walk asks first; fixes 2-4
are checks).

## 2. Fix 1 — `inplace_applies` (and why its old comment was the bug)

The row returned 1 ("the gate holds it to its sites"). It sits just before
`generic` in compose.c's arms walk, so every site no specialized row took
selected it first, the contract gate declined it, and the walk moved the
selection to `generic`: one gate move per generic site, zero artifact
movers, 7,726,522 census would-declines (n2_triage.md). N3's model is the
other way round: the predicate SELECTS, the gate CHECKS. The predicate now
states the contract's shape, in the pffind.c rows' idiom:

```c
return s->form == MF_FORM_STMT && s->op == MF_OP_MISMATCH &&
       s->handoff == MF_H_ON_DIFF &&
       (s->fold_kind == MF_FOLD_ASCII || s->fold_kind == MF_FOLD_UCP) &&
       def && def->fold && kit_fold_shape(def->fold) == CL_FOLD_STMT;
```

`fold` is a DEFINE-phase field, so `def` carries it.

Evidence (all pinned to cpus 12-15):

- **Zero movers, lane-style pre/post sweep** (m7_report.md §4's
  `ident_sweep.py`, reused in `build/m7fixscratch/`): `pcrec.base` built from
  `git archive c9e90c77` against the fixed build, every unique corpus
  `pattern` line (5,431 rows, 4,387 unique) x 10 configs (byte, utf8, each
  with `-fcomments`, `--ucp` x2, `(?i)` byte/utf8/ucp/cmt), `--features all`,
  `.c`/`.h`/rc/stderr compared: **43,870 pairs, 0 movers**. Reach per config
  (span_exact / span_caseless / fold table): byte 434/17/5, utf8 436/17/17,
  byte-ucp 434/17/17, i-byte 1/443/0, i-utf8 1/445/445, i-byte-ucp 1/443/443.
- `make test-memfn-arms` 286 passed / 0 failed; `make test-memfn-rows` 127 / 0.
- `make test-memfn-g2` (the --quick tier): **48,566,739 passed / 0 failed**;
  check (b) "every row chosen >= 1"; `row-chosen arms mismatch_inplace 2670`;
  (e) every row meets its g2_floor (mismatch_inplace 2,403); (f) MISMATCH
  sites chose `mismatch_inplace` 336 times (floor 300) and `generic` 673
  (floor 600).
- **N2 on a sample** (the census's own `.sh`, driver and report, through the
  new `N2_ARMS`/`N2_LIMIT`/`N2_PATTERNS`; arms `null`, `null+comments`,
  `null@utf8`; streams c-default, c-vm, one composition file):

  | sample | traced build | compiles | sites | would_decline | rc |
  |---|---|---|---|---|---|
  | first 400 distinct corpus patterns | fixed | 2,403 | 13,873 | **0** | 0 |
  | same | pre-fix (c9e90c77) | 2,403 | 13,873 | **2,973** (= every generic define selection) | **5** |
  | the 12 witness patterns | fixed | 75 | 648 | **0** (mismatch_inplace chosen 8) | 0 |

  The pre-fix run's report blames `mismatch_inplace` in three cells, the
  triage's three shapes: SKIP/ADVANCE (2,629), exact MISMATCH (324),
  FOLD_EXPR (20).

## 3. Fix 2 — the census's rc and its blame

- **rc** (`docs/design/memfn/probes/rowcon/n2_census.sh`): `wd` was parsed and
  printed and never tested. Now `would_decline != 0` or `noend != 0` (or either
  UNREAD from the report) makes **rc 5** on ANY run, full or partial (one
  would-decline anywhere is the defect, unlike the floors, which scale with
  the population). Precedence: 1/2/3 first, then 5, then 4. The DONE line is
  `== N2 DONE rc=N would_decline=K noend=K floors=... ==`; the header's rc
  legend says so.
- **noend**: `n2_report.py` prints `noend=K` before `would_decline=K`.
- **moved_from**: `parse_trace` keeps the END's `moved_from=`; the would-decline
  key gains it (old arm files load with `-`), §2's table gains a "declined
  row" column and §3's R-6 table is keyed on the declined row (the
  misreading was "generic declined").
- **SAMPLE plumbing**: `N2_ARMS`, `N2_LIMIT`, `N2_PATTERNS` (passed as
  `--pattern=...` so a pattern starting `-` survives argparse), and
  `N2_TREE` (a mech scratch tree is a `git archive` copy; inside another
  checkout `git rev-parse` would name THAT checkout). Linux callers must set
  `N2_LOCK` (the default is the Mac's) and `CC=gcc`.
- **The census's mech arm: none existed.** New arm `n2sample`
  (`tests/mech/run_sabotage_matrix.sh`) runs the new
  `tests/memfn/run_n2_sample.sh`: builds an `-DMF_TRACE` pcrec from the
  sabotaged tree, runs the census `.sh` on `tests/memfn/n2_sample_patterns.txt`
  (12 witnesses: every MISMATCH shape, the triage's SKIP witness, FIND,
  pre-check, offset skip; floor 8) x the three null arms, `checks failed: 1`
  iff rc != 0. About a minute.
- **S668** (`memfn/src/mismatch.c`, arm `n2sample`; free ids S668/S672/S674/S675
  were checked on main and every worktree): the plant makes
  `inplace_applies` hold everywhere (`return 1 ? 1 : ...`), M7's defect.
  `SAB_REACH`: `(?i)(ab)\1` emits `unsigned char x, y;` (mismatch_inplace
  live in pcrec) and `(a+)\1` emits the generic exact loop (the move's
  target); `SAB_REACH_POP`: the sample file still holds the triage's three
  witnesses. Both checked by hand on the clean build. VALIDATE_ONLY: fields OK.
  **Hand-measured** (plant applied to the working tree with
  `tests/mech/lib/replace.py`, traced pcrec rebuilt, `run_n2_sample.sh`, file
  restored): clean `checks passed: 1 / failed: 0` (would_decline 0);
  planted `== N2 DONE rc=5 would_decline=85 noend=0 ==`, `checks failed: 1`,
  table naming `mismatch_inplace` as the declined row (SKIP 69, exact
  MISMATCH 12, FOLD_EXPR 4). The matrix figure is owed (§5).

## 4. Fixes 3 and 4

- **S512**: M7 raised `C17_ROW_FLOOR` to 14 (N7U split), so the POP's
  `^C17_ROW_FLOOR=13$` matched nothing and the row scored UNREACHED. Re-pinned
  to `^C17_ROW_FLOOR=14[[:space:]]` (m6's e48cc296 form; this branch still
  carries N6, so the manifest holds 14 rows: PF..N7U). Hand-measured via
  `bash tests/memfn/run_site_manifest.sh`: clean `checks passed: 13 / failed:
  0`; SETREST commented out, `FAIL: the manifest holds 13 rows, below its K35
  floor of 14`, 12 / 1. Both POP lines count 1 on the clean tree.
- **startset manifests**: `docs/design/startset/s1/census_s1.py`
  (`PCREC=build/pcrec TREE=. BENCH=/home/pcrec/projects/pcrec-bench
  MANIFESTS=... JOBS=2`) regenerated into scratch and compared as SETS: corpus
  rows `s2_vm_auto` **+8 / -0**, `s2_vm_forced` **+8 / -0**, every one an
  s670cell block (caseless.rxt:71,86; caseless_ucp.rxt:262,274,288,298,310,322),
  `s3_dfa` corpus rows identical. (A line diff shows reorders: the committed
  files carry earlier hand appends out of sort order; nothing else moved.)
  **Finding**: the same run adds BENCH rows, +6 forced and +1 `s3_dfa`
  (`bench/capability/hex8-bounded`, `tail-*`), because this box's pcrec-bench
  checkout (bb87dfa5) has newer exports than the last regeneration's. Bench
  rows are counted, never checked, so they were NOT taken (the brief's reviewed
  diff is +8/+8 with `s3_dfa` unchanged); a bench-pin re-sync is a separate
  decision. The 8 rows were appended with a header line; tests/startset/CLAUDE.md
  carries the note.
- `make test-startset` alone, pinned (`taskset -c 12-15 make -j4
  test-startset`, log `build/m7fixscratch/test_startset.log`): **GREEN**,
  no `*** [test-` line. run_startset_checks 3/0; vmhat 22/0 with
  `[vm-movers] auto: movers == manifest_s2_vm_auto.tsv by ID (394 rows, 0
  off-diagonal)` and `vm: ... (3176 rows, 0 off-diagonal)`, vm-diff 5,536,701
  cells all same; dfahat 35/0, `[dfa-movers]` 82 rows 0 off-diagonal,
  dfa-diff 2,256,086 cells all same.

## 5. Mech rows the manager runs SOLO

`bash tests/mech/run_sabotage_matrix.sh <id>`, one invocation each, no commit
during the run:

- **anchored in mismatch.c / the changed lines** (`rows_for.sh
  memfn/src/mismatch.c`): **S668** (new; the plant IS the changed lines),
  S666, S667, S669, S670, S671 (anchors in `mm_render`, unchanged text, lines
  shifted +7; `m6read_check_sab_anchors.py`: 562 sabotages / 580 anchor
  sites, all resolve).
- **S512** (re-pinned).
- **the new census row**: S668 (arm `n2sample`; it builds a traced pcrec, so it
  is the slowest of these).
- **startset**: no row's anchor moved (no sabotage names a manifest file). The
  rows whose detector reads the regenerated VM manifests (`[vm-movers]`, arm
  `vmhat`) are worth one solo pass: S478 S491 S492 S493 S494 S498 S499 (and
  the vmhat rows declared UNREACHED, S479 S496 S497, plus S501 S502, read the
  same arm).

## 6. Commands (the slot's re-validation, not run here)

```
# identity gate (m7_report §8 step 3), N2 full census, G2 full, make test:
python3 scripts/emit_sweep.py --ref <merge-base> ... --bases byte,utf8 --extra -fcomments --extra --ucp
N2_LOCK=<scratch> CC=gcc JOBS=16 bash docs/design/memfn/probes/rowcon/n2_census.sh   # expect rc 0, would_decline 0
python3 docs/design/memfn/probes/rowcon/n2_report.py <out> --floors tests/memfn/row_floors.tsv --propose   # pins mismatch_inplace's pcrec_floor
make test-memfn-g2-full
scripts/perfrun --label m7fix -- <log>
# mech, each solo:
for r in S668 S666 S667 S669 S670 S671 S512 S478 S491 S492 S493 S494 S498 S499; do bash tests/mech/run_sabotage_matrix.sh $r; done
```

Note: `docs/design/start_table/sabotage_anchors.{tsv,total}` were already
behind this branch's row count (555 vs 562 files) before S668; no check
reads them, so they were not re-derived here.
