# n4 — [MEMFN-ROWCON] N4: rows.tsv, signatures, census floors, spec literals

Lane n4 (opus), 2026-10-07, worktree `worktrees/n4`, branch `lane/n4`, cut
from the kit branch `lane/memfn-n4` (main d33e1d55 + the n2_census one-pool
fix). Design of record: `docs/design/memfn/row_contracts.md` rev 4.1 §4 and
§5's N4 row. Scratch: `worktrees/memfn-slot/n4/`.

## 1. Summary

- **Reach counters (item 1):** they were already present (N1: CHOSEN per row
  and per (row, used field, class), printed at exit under `MF_TRACE`). One
  gap fixed: the counter registry (16 slots) dropped a row SILENTLY when
  full. That row then printed `chosen=0`, a population nobody counted. The
  exit lines now end with `MFTRACE REACH_DROPPED n=N`
  (`memfn/src/gate.c`, trace-only), and the census and the new check
  require it to be 0. `n2_report.py` already summed the counters. It now
  also keeps up to three witnesses per chosen row, the dropped count, and
  the floor verdict (`--floors`, `--propose`).
- **rows.tsv (item 2):** `tests/memfn/rows.tsv`, hand-written, 13 rows:
  - the composer's 9 arms: `ofsskip`, `precheck`, `precheck_assign`,
    `runcmp`, the four `pf_*` rows and `generic`;
  - runcmp's 4 rows: `words`, `overlap`, `bytes`, `memcmp`.

  12 rows are `pcrec` (each reached by a corpus-style pattern; see §6) and
  `generic` is `total-fallback`. No row needs `pending-site` or
  `contract-reach` at N4.
- **Signatures (item 3):** one literal per row. Each is checked IN its
  witness's artifact, where the kit's own trace must show the row chosen.
  Each is checked ABSENT from its control's artifact, where the trace must
  show the row NOT chosen. Then every signature is held against every
  artifact and fixture of the run.
- **Floors (item 4):** `tests/memfn/row_floors.tsv`. Every cell is a
  PLACEHOLDER: no number is invented. The command that measures the pcrec
  column is in its header and in §8. The G2 column needs a G2 change
  (§7). The census applies the floors: `n2_census.sh` passes `--floors`,
  and a FULL run with a failure is rc 4.
- **Spec (item 5):** no spec hunk. The arm table and the witnessed rows
  are not caller-observable. runcmp's rows ARE observable and are already
  stated in two places, which the new check now holds rows.tsv to (§5).
- **Wiring (item 6):** `make test-memfn-rows` (in TEST_SECTIONS, about
  1.4 s), `tests/memfn/run_rows.sh` + `rows_check.py`. CLAUDE.md updated in
  `tests/memfn/`, `tests/`, `memfn/src/` and `docs/design/memfn/probes/rowcon/`,
  plus `docs/testing.md` and `memfn/docs/trace_format.md`.
- **Zero pcrec movers:**
  - `build/pcrec` is byte-identical (`cmp`) to the pre-edit binary: every C
    change is inside `#ifdef MF_TRACE` or in a test file;
  - 10 compiles against the pre-edit binary: 10/10 identical (§4);
  - every run of the new check compiles each witness and control twice,
    traced and plain, and requires identical bytes.

## 2. Files

| file | what |
|---|---|
| `memfn/src/gate.c` | `REACH_DROPPED` (trace-only): count the selections the full registry cannot hold, print the count at exit |
| `memfn/docs/trace_format.md` | the new line |
| `tests/memfn/rows.tsv` | the row manifest (new) |
| `tests/memfn/row_floors.tsv` | the floor file, PLACEHOLDERs + the measuring command (new) |
| `tests/memfn/rows_check.py`, `run_rows.sh` | the checks A-D (new) |
| `tests/memfn/arm_fixtures.c` | `--only FIXTURE`: render one fixture alone (C5's output unchanged: `test-memfn-arms` 138/0) |
| `docs/design/memfn/probes/rowcon/n2_report.py` | per-row witnesses, `REACH_DROPPED`, `--floors`/`--propose`, the floor table (§7 of the report) |
| `docs/design/memfn/probes/rowcon/n2_census.sh`, `n2_census.py` | the report runs with `--floors`; the DONE line gains `floors=<summary>`; rc 4 on a full-run floor failure; `meta.json` records `limit` and `explicit patterns` |
| `Makefile` | `test-memfn-rows` (TEST_SECTIONS, .PHONY) |

## 3. What each check controls, and its independent control

| check | subject | independent control | why it is independent |
|---|---|---|---|
| A. row set | rows.tsv (hand-written) | the kit's rows, from its OWN trace. The kit is built `-DMF_TRACE` from a `find` list of `memfn/src/*.c` (short list fatal). The fixture driver runs, and the exit `REACH` lines walk `compose.c`'s `arms[]` and runcmp.c's table. | The manifest is typed by hand. The trace is the code. Neither is `fields.def`. Both directions are red, and so are a duplicate, `REACH_DROPPED != 0` and fewer than `ROWS_FLOOR` (13, a literal) rows. |
| A'. runcmp rows | rows.tsv's runcmp lines | `pcrec --list-axes`'s `run-overlap` rows (walked live off `mf_run_rows`) AND `docs/spec/tuning.md` §2.38's row table (hand-written spec) | The spec table shares no source with either. The listing is a third reading of the kit. A blind reader (zero names found) is red. |
| B. reasons | rows.tsv's `reach` column | the closed vocabulary, written in the checker; G2's families read from `memfn/tests/run_g2.sh` `FAM_FLOORS` (G2's own file) | A `contract-reach` family must exist in G2, not in a list of ours. An unreadable FAM_FLOORS is red. |
| C. signatures | each row's literal | its witness (literal present AND trace chose the row) and its control (literal absent AND trace did not choose the row) | The literal is TEXT, the selection is the kit's own TRACE: two observations that must agree. The control must also change the artifact (identical witness and control artifacts are red). |
| C'. sibling exclusion | every signature | every artifact and every fixture the run produced (53 artifacts, 689 pairs) | Wherever a signature appears, the trace must show its row there. A literal shared with a sibling row's rendering is red. This is what found §6 (1). |
| C''. identity | the traced pcrec | `build/pcrec` (the shipped compiler), byte-identical per compile | The text checked is the shipped compiler's. A kit byte move against a stale `build/` is red. |
| D. floor file | row_floors.tsv | rows.tsv's rows and reasons | Same rows, a positive integer or PLACEHOLDER for a `pcrec` row, `-` iff not `pcrec`. PLACEHOLDER prints UNREACHED, never pass. |
| census floors | each row's CHOSEN over the full census | row_floors.tsv (measured by a previous full census, by hand) | Applied only on a FULL run (no limit, no explicit patterns, every arm run). On ANY run, a closed-reason row chosen > 0 is a STALE REASON, and a nonzero `REACH_DROPPED` is red. |

**What none of it sees:** G2's per-row reach (G2 counts form ids); whether
the floors hold between full censuses (`make test` never runs the census);
a row that stays chosen for its own witness pattern but leaves the corpus.
That last one is the census floor's job, which is why it is a floor on the
population and not on the witness.

## 4. Zero movers, shown

- `build/pcrec` after every edit: `cmp` with the pre-edit binary
  (`memfn-slot/n4/pcrec.pre`, built from 1ad01078) is IDENTICAL. That
  held after the gate.c change and after the P8b rebuild-and-restore.
- 10 compiles, pre-edit binary vs `build/pcrec`, `-p rx --features all -o -`:
  - patterns: `abc[0-9]+xyz`, `(ab)c?userpass`, `(?!x)abc`,
    `[a-z]+@[a-z]+\.com`, `\b\.[0-9]{4}Z`, `(?i)(cat)s?dog`, `(x)?userz`,
    `foo(bar|baz)qux`, `(?:(?<=[ab])z|w)`, `(?i)select\s+\w+\s+from`;
  - result: **10/10 identical**, 304,842 bytes.
- `make strict` rc 0. The nine kit sources compile clean under
  `-DMF_TRACE -O2 -Wall -Wextra -Werror`.
- Green: `test-memfn-arms` 138/0, `test-memfn-rows` 70/0 (+1 UNREACHED,
  the placeholders), `link` 4/0, `manifest` 8/0, `forms` 4/0, `arch` 5/0,
  `deleg` 21/0, `reach` 15/0. No `*** [test-` lines.

## 5. docs/spec/ (D80)

The design asks for "rows per table, and witnessed rows" as spec literals.
Read against what a caller can observe:

- **runcmp's rows (4):** observable through `--list-axes` (the
  `run-overlap` axis rows) and through the emitted forms.
  `docs/spec/tuning.md` §2.38 already states the 4-row table by name. No new
  literal is needed. The existing one is now CHECKED: rows.tsv must name
  exactly those rows (check A'; plant P4).
- **The composer's arms (9):** NOT observable. No listing shows them
  (`row_contracts.md` §5: "Listing the composer arms in `--list-axes` is
  NOT in scope"; H3 holds it), and they leave no stamp. A spec literal
  would state a count no caller can read, so no hunk. The count lives in
  `run_rows.sh` (`ROWS_FLOOR`) and rows.tsv.
- **Witnessed rows:** a property of an `MF_TRACE` scratch build. No caller
  can observe it, so no hunk.

## 6. Findings

1. **A signature can be shared with the fallback's rendering of the SAME
   site.** The first `ofsskip` signature was `size_t rx_ofsskip(`. The
   generic row renders the same FUNC site under the same pcrec-given
   name, so the literal appeared where `ofsskip` was not chosen (the
   generic witness and the `ofs-decline-*` fixtures). The sibling-exclusion
   check caught it on its first run. The signature is now the kit's own
   parameter list, `rx_ofsskip(const unsigned char *subject, size_t n,`.
2. **A deny is not always a control.** `pf_walk`'s first control was its
   witness without `-fno-offset-skip`. The default compile of
   `[a-z]+@[a-z]+\.com` still takes `pf_walk` (the class prefilter is not an
   offset-skip). The control is now another pattern, `abc[0-9]+xyz`, where
   `pf_memchr` is chosen. The trace-agreement check refused the first
   control; a text-only check would have needed the planted defect to see
   it.
3. **The reach registry could undercount silently** (16 slots, 13 rows
   today): a full registry printed a chosen row as `chosen=0`. Now
   `REACH_DROPPED` is printed and required to be 0 (plant P10: a registry of
   8 → 13 dropped, red).
4. **Reach today:** in a 31-pattern sample (census run 1, 4 arms), all 12
   non-generic rows are chosen from pcrec. `generic` is chosen 0 times.
   The committed N2 census (`n2_results_5fc4b0e5.md`, Mac) predates N3's
   split and R4g's PF rows, so its reach table lacks `precheck_assign` and
   the four `pf_*` rows. The manager's full census re-measures it (§8).
5. **Disclosure:** early in the lane, several commands (about ten: edits, the first runs and one commit) began with `cd <worktree> &&`.
   The brief forbids `cd`. Each Bash call starts in a fresh cwd, so
   nothing moved, but the rule was broken; later commands use `git -C` and
   absolute paths only.

## 7. G2 needs (for the blinded author; memfn/tests/ untouched)

- **Per-ROW chosen counts.** G2 prints form ids, and a form id is not a
  row: `precheck` is two rows (`precheck`, `precheck_assign`), `pf_memchr`
  and `pf_walk` are two each (their `_bounded` twins), and runcmp's four
  rows have no form id. The cheapest route that shares no source with G2's
  generator is to link G2's kit with `-DMF_TRACE` and sum the exit
  `MFTRACE REACH table=T row=R chosen=N` lines (format:
  `memfn/docs/trace_format.md`, now ending with `REACH_DROPPED n=0`). The
  output should be one `row-chosen <table> <row> <n>` line per row of both
  tables, 0 included.
- **Per-row floors over G2:** with that output, `row_floors.tsv`'s
  `g2_floor` column is floor(0.9 x measured) on the quick tier. A `generic`
  floor over G2 is meaningful, because G2 reaches the fallback and pcrec
  does not.
- **A check in G2** that every row of both tables is chosen at least once
  over G2 (the contract-reach floor `row_contracts.md` §4 names). No row
  needs a `contract-reach` reason at N4, but the vocabulary is ready:
  `rows_check.py` reads the family names from `run_g2.sh`'s `FAM_FLOORS`.

## 8. VALIDATION OWED (manager's slot)

1. **The full census that pins the floors** (Linux, one heavy suite,
   detached). From the merged tree:

       cd /home/pcrec/projects/pcrec && mkdir -p build/scratch && \
         N2_LOCK=build/scratch/n2.lock OUT=build/scratch/n2_n4 CC=gcc JOBS=12 \
         nohup bash docs/design/memfn/probes/rowcon/n2_census.sh \
         > build/scratch/n2_n4.log 2>&1 & disown

   - Done when the log's last line is
     `== N2 DONE rc=0 would_decline=0 floors=floor_fail=0,floor_placeholder=12,reason_stale=0,reach_dropped=0 ==`.
     `floor_placeholder` counts the pcrec column only: 12 `pcrec` rows
     (the 13th, `generic`, is `-`). rc 4 means a floor failure, a stale
     reason or a dropped count, which is a finding.
   - Then pin. This command prints `propose <table> <row> <floor>` per row:

         python3 docs/design/memfn/probes/rowcon/n2_report.py build/scratch/n2_n4 \
           -o build/scratch/n2_n4/n2_results.md \
           --floors tests/memfn/row_floors.tsv --propose

     Copy the values into `row_floors.tsv`'s `pcrec_floor` column by hand,
     naming the run in the commit. Re-run the same report command: it must
     print `floor_fail=0 floor_placeholder=0 ...` with the g2 column still
     PLACEHOLDER (the report only counts the pcrec column).
   - Expected: 107 arms (or whatever `--list-axes` now gives), about 960k
     compiles. On the Mac at 8 jobs it took about 45 min.
2. **`make test`** on the merged tree (`make -k -j16 -Otarget test`; verdict
   from `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`, empty = green). The
   new section is `test-memfn-rows`.

## 9. Sabotage plants run by hand (none committed)

Each plant was applied to the worktree, the check was run, and the file
was restored with `git checkout` (transcripts in
`memfn-slot/n4/plants/*.log`). For the rows check, the clean result is
70 pass / 0 fail.

| id | plant | result |
|---|---|---|
| P1 | rows.tsv loses the `generic` line | RED 2: "the kit has row arms/generic and rows.tsv does not"; the floor file names a row rows.tsv lacks |
| P2 | rows.tsv gains a `runcmp/ghost` row | RED 7: "rows.tsv names runcmp/ghost and the kit has no such row"; `--list-axes` and the spec table disagree; the witness has no signature |
| P3 | `compose.c` drops `&pf_walk_bounded_arm` from `arms[]` | RED 3: the trace lists 12 rows (under ROWS_FLOOR 13); rows.tsv names a row the kit lacks; the traced artifact differs from build/pcrec's |
| P4 | tuning.md §2.38's `bytes` row renamed | RED 1: the spec lists [memcmp, overlap, words], rows.tsv [bytes, ...] |
| P5a | `generic` reach → `unreachable` | RED 1: not in the closed set |
| P5b | → `contract-reach:nosuch` | RED 1: the family is not one of G2's nine |
| P5c | → `pending-site:` (no trigger) | RED 1 |
| P5d | `pf_memchr_bounded` → `pending-site:x` with a pattern witness | RED 2: needs a fixture witness; the floor file gives a pcrec floor to a non-pcrec row |
| P6 | `words` signature → `) \| rx_w` (absent) | RED 1: witness "signature absent, row IS chosen" |
| P7a | `ofsskip` signature back to `size_t rx_ofsskip(` | RED 3: appears in the generic witness and two `ofs-decline-*` fixtures, where the trace did not choose ofsskip (finding §6.1) |
| P7b | `precheck` control loses its deny | RED 2: "control: signature present, row IS chosen"; "the control's artifact is the witness's" |
| P8 | runcmp.c's word join `" && "` → `" &&  "`, `build/` stale | RED 14: every affected traced artifact differs from build/pcrec's |
| P8b | the same, with `make` rebuilt | RED 1: overlap witness "signature absent, row IS chosen" (afterwards restored, rebuilt, `cmp`-identical) |
| P9 | gate.c's `reach_print` walks only the arms table | RED 5: 9 rows (under 13); rows.tsv names the four runcmp rows the kit "lacks" |
| P10 | gate.c `REACH_ROWS` 16 → 8 | RED 1: "REACH_DROPPED is 13" |
| P11a-d | row_floors.tsv: ofsskip `0`; precheck `-`; generic `5`; the bytes line deleted | RED 1 each: the value rule, or "rows.tsv names runcmp/bytes and row_floors.tsv has no line for it" |

Census side (`n2_report.py --floors` on a copy of census run 1 with its
meta set to "full", floors = the proposal):

| id | plant | result |
|---|---|---|
| F0 | clean | `floor_fail=0 floor_placeholder=0 reason_stale=0 reach_dropped=0` |
| F1 | ofsskip floor 1000 (chosen 39) | `floor_fail=1`, row "BELOW FLOOR" |
| F2 | pf_memchr_bounded declared `pending-site:x` (chosen 1) | `reason_stale=1`, "STALE REASON: pending-site:x, chosen 1" |
| F3 | generic declared `pcrec` (chosen 0) | `floor_fail=1`, "UNREACHED: reach is pcrec, chosen 0" |
| F4 | one arm file's `reach_dropped` = 3 | `reach_dropped=3` |
| rc rule | the `.sh`'s `case` on five summaries | placeholders-only rc 0; dropped 3 rc 4; a partial run with a stale reason rc 4; a clean partial run rc 0; floor_fail 1 rc 4 |

Census runs used: 3 of 4.
- Run 1: the 31-pattern, 4-arm discovery (reach + witnesses).
- Runs 2 and 3: `SMOKE=1` through `n2_census.sh`; run 3 checked the fixed
  DONE line, `== N2 DONE rc=0 would_decline=0 floors=NOT-APPLIED,reason_stale=0,reach_dropped=0 ==`.

## 10. Charter checklist (row_contracts.md §4 and §5 N4)

| item | status |
|---|---|
| §4 counters: CHOSEN per row and per (row, used field, class), kit-private, printed at exit under MF_TRACE only, summed by the census | ✓ already present (N1); hardened with `REACH_DROPPED`. n2_report sums and now carries witnesses + floors. Nothing reaches an artifact (`cmp` identical) |
| §4 rows.tsv: hand name manifest, one line per row, reach reason + witness, closed reasons, not derived from fields.def, checked against the kit's actual rows both directions | ✓ 13 rows; check A (P1, P2, P3, P9); reasons B (P5a-d) |
| §4 a text signature per row, checked in its witness's artifact, absent under deny/control | ✓ check C + C' (P6, P7a, P7b, P8b); control is a deny for 8 rows, another pattern for 3, a fixture for generic |
| §4 per-row CHOSEN floor over pcrec's corpus | ✓ file + census check (F0-F4); values PLACEHOLDER, OWED to the manager's slot (§8) |
| §4 per-row CHOSEN floor over G2 | PLACEHOLDER; the G2 need is stated (§7) |
| §4 literal floors in docs/spec/: rows per table, witnessed rows | no hunk: not caller-observable except runcmp's rows, whose spec table is now checked (§5, P4) |
| §5 N4 "pcrec artifact movers: none" | ✓ binary identical; 10/10 compiles; per-run traced-vs-plain identity |
| wiring + CLAUDE.md | ✓ `make test-memfn-rows` in TEST_SECTIONS; tests/memfn, tests, memfn/src, rowcon CLAUDE.md; docs/testing.md; trace_format.md |

## 11. VALIDATION (kit manager's slot, 2026-10-07/08, Linux dev box)

§8's owed runs, done on lane/memfn-n4 after main ad669fb8 was merged in:

| run | tip | result |
|---|---|---|
| full N2 census, JOBS=16 (the one-pool driver) | 4492a0a1 | rc 0, **wall 379 s**, `would_decline=0 floors=floor_fail=0,floor_placeholder=12,reason_stale=0,reach_dropped=0` |
| `n2_report --propose`, pinned by hand | 4e081f78 | 12 `pcrec_floor` values = floor(0.9 x chosen); the re-run report reads `floor_fail=0 floor_placeholder=0` |
| `make -k -j16 -Otarget test` | 4e081f78 | 680 s, ONE red: test-codegen [K37] |
| K37 fix (`run_rows.sh`'s prerequisite test in K37's exempt form) | e8e3e1d8 | `make test-codegen` green (K37: 1,077 sites bounded or allowlisted); `test-memfn-rows` 70/0 |

The K37 red was this lane's own new script. Its `for f in build/pcrec ...`
existence loop read as an unbounded compiler site. It was a false positive of
a textual check, and K37 was right to ask for the exempt spelling. The re-run
covered test-codegen alone: the fix touches one test script that no other
section reads. A triage lane (read-only) found the cause; `[SABANCHOR]`
resolved all 498 rows, so no mech row moved.

`g2_floor` stays PLACEHOLDER (§7): OWED to a blinded follow-up that makes G2
count per row.
