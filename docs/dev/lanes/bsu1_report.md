# bsu1 — R-47 unit U1 of docs/design/memfn/block_span.md (lane bsu1, opus, 2026-11-21)

## STATE AT HANDOFF

U1 is built on branch lane/bsu1 (merge base 367cbdedb). No U2 work is in the branch and no abi number moved.

Green:
- the identity gate (0 movers, 10 arms x 2 streams, no mask);
- the build, `make strict` and `make test-codegen` (21/21);
- the G2 window family (27376 passed, 0 failed);
- SPAN-SEED through the harness (1145/1145);
- the pin sections after re-pinning: test-rxtsource, test-startset, test-memfn-rows and test-memfn-finder at make rc=0, with guarded/simdfloor/g2 green on the first run.

Owed: two box-queue jobs, queued as my last act.
- `713-kit-bsu1-test` (key kit-bsu1-test): `make test` via perfrun; log /var/tmp/pcrec-pcrec/scratch/bsu1/maketest.log.
- `714-kit-bsu1-mech` (key kit-bsu1-mech): detection of the 11 U1 sabotage rows, after kit-bsu1-test.

Rulings file (docs/dev/lanes/bsu1_rulings.md): one ruling, R-1, the decider census (see OWED RUNS).

Commits:
- d2173b97a: rev 4.1.
- 0963bd61a: the code and SPAN-SEED.
- 7a9d3c056: the re-aims and docs.
- ad02b50b1: the population re-pins, the decider census and rev 4.1's census line.
- The report commit.

## THE JOB

The brief:
- Rev 4.1 of block_span.md, applying review r71 as ruled.
- Then U1: `wf_span_head`, today's if-chain, becomes the span form table, with rows T-deny / T-force / T-lever / T-head. The V rows wait for U2.
- The stretch list is stored once, by one enumerator. `skip` becomes a plan fact. `w->head` is retired.
- SPAN-SEED is committed.
- An identity gate with no mask: every corpus artifact and SPAN-SEED at width 4095 byte-identical to the merge base, at both layers and both engines.
- A refactor gets no flag, and any moved byte means stop.

Premise test: the if-chain sat in memfn/src/window.c as the brief said, so the premise held.

## REV 4.1

Commit d2173b97a: "rev 4.1 (2026-11-21): review r71 applied". The changes:
- R71-1: §10.1/§10.2 now name three witnesses, x86-64-v3 only, with a per-target column.
- R71-2 and the §15 Q4 ruling: the floor is pinned at the measure at U2 (about 28 byte / 20 utf8 on c-default, 0 on c-vm).
- R71-3: CONFIRMED in R-2's words (why the floor-branch call is needed). The trace hunk names floor sites, and the reach slots are 54 of 64.
- R71-4: the C18 row and its unit.
- R71-5: the U1 note. The `.rxt` shifts the every-10th sample, which reaches the simd-form floor.
- R71-6: the counted pin spellings.
- R71-7: (a) §16 item 12 tool note (26/22 difflib, 24/20 GNU diff; U2b names its tool); (b) the U5 re-aim of S2931; (c) §5; (d) `wf_find_prepare` gains one parameter, gphases, and quiet is `!build`.

The owner question is renamed `scalar-check-cut`, replacing wrap-differs. Both readings are carried in §2.2 and §15 Q1.

There is a new §18.0, the r71 dispositions table, and the §18.1 R-20 row is amended. The note's line in docs/design/memfn/CLAUDE.md was updated in the same commit.

## THE CHANGE

All in memfn/src/window.c unless named otherwise.

**The span form table.** `wf_spantable` ("wfS") is a kit_table walked by kit_walk with real contracts. The rows:

| row | holds when | h |
|---|---|---|
| T-deny | `no-span-loop` | INT32_MAX |
| T-force | `span-loop` | 0 |
| T-lever | the artifact's `KIT_LEVER_SPAN_HEAD` | its span_head |
| T-head | always | WF_SPAN_HEAD (64) |

- Six contracts: `WF_CT_S` × 4, plus the serves line. `wf_tables_check` refuses a row with a hole.
- `WF_SPAN_HEAD` and `WF_LOOP_ID` are kept (S3285's anchor).
- The trace hunk is in memfn/docs/trace_format.md: `table=wfS`, one selection per one-class stretch at E-find and floor sites. wfS is not in the printed reach tables.

**The stretch list.** There is one enumerator, `wf_stretches`. It stores `{i, k, h}` per one-class stretch on the plan (`w->str`, `w->nstr`), with k found by `wf_loop_len` at head 0. Its two callers:
- the E-find site, in `wf_find_prepare`, which gains `gphases` (R71-7 d);
- the floor branch, in `wf_plan_site`.

`wf_test_to` renders from the stored list. Below a stretch's h each entry is a lone test, and from h it is a loop. That is today's rendering, bounded by the stored stretch.

The V counter `j` is NOT in `struct wf_stretch` at U1. It has no reader until V lands at U2, which adds it.

**skip as a plan fact.** `skip` is now a plan fact, `w->skip`, set from the search renderer table's new `skip` column:
- `stop_skip` on PAIR, MEMCHR and WALK;
- `hors_skip` on HORS.

The column replaces the `int *skip` out-parameter of the `head` column, and `ren_check_row.test` loses its `skip` argument. `w->head` is retired: `wf_loop_len(w, i, head)` takes the head.

**Comments.** compose.c and kit.h now say "the span form table's T-lever row".

**SPAN-SEED.**
- tests/memfn/gen_span_seed.py writes tests/memfn/span_seed.rxt: 41 patterns (bench 3, pins 11, the grid slice) and 1145 cases.
- Every expectation comes from python3 `re` (bytes, ASCII).
- verify_rxt.py: ALL CHECKS PASSED.
- The tests/memfn/CLAUDE.md line was added. That file was at its 12 KB limit, so the advtri worked example moved to tests/memfn/NOTES.md.

The kit_walk no-row return (-1, reported as "out of memory") cannot be reached: T-head always holds and serves everything.

## IDENTITY GATE

- Tool: scripts/emit_sweep.py, base binaries built at 367cbdedb against the U1 build.
- Streams: c-default and c-vm, so both engines.
- Compared: `-o -`, so .c and .h together.
- No mask.
- Logs: /var/tmp/pcrec-pcrec/scratch/bsu1/idg_*.log.

| arm | flags | population | movers | asymmetric |
|---|---|---|---|---|
| off_byte | (none) | 7274 | 0 / 0 | 0 |
| v3_byte | -fmemfn-simd=x86-64-v3 | 7274 | 0 / 0 | 0 |
| off_utf8 | -e utf8 | 7274 | 0 / 0 | 0 |
| v3_utf8 | -e utf8, v3 | 7274 | 0 / 0 | 0 |
| force_byte | --memfn=span-loop | 7274 | 0 / 0 | 0 |
| deny_byte | --memfn=no-span-loop | 7274 | 0 / 0 | 0 |
| seed4095_off | SPAN-SEED, --window-search-width=4095 | 41 | 0 / 0 | 0 |
| seed4095_v3 | the same, plus v3 | 41 | 0 / 0 | 0 |
| seed4095_force | the same, plus span-loop | 41 | 0 / 0 | 0 |
| seed4095_deny | the same, plus no-span-loop | 41 | 0 / 0 | 0 |

- The corpus population of 7274 includes span_seed.rxt's 41 patterns.
- Every emit_sweep run ended `DONE rc=0`.

## SABOTAGE AND REACH

Rows touched, all on memfn/src/window.c (§10.2). No new ids: S3490-S3499 are unused.

- **Re-aimed onto the table:**
  - S3278 (T-force never holds) and S3281 (T-deny never holds).
  - S3279 (T-lever never holds) and S3282 (T-lever reads 0).
  - S3280 (`wf_loop_len` reads head as `<=`).
- **Anchors unchanged, re-proven:** S3276, S3277, S3283, S3284, S3285, S2982.

Checks run:
- VALIDATE_ONLY: 11/11 definitions valid.
- Each SAB_BEFORE occurs exactly once in window.c.
- REACH_ONLY: rows=11, no-probe=11. None of these rows declares a SAB_REACH probe, so REACH has nothing to re-prove by probe. Their reach proof is detection, owed as job 714.

## OWED RUNS

- **`713-kit-bsu1-test`**: `make test` on lane/bsu1 through perfrun. Verdict: the make error lines in /var/tmp/pcrec-pcrec/scratch/bsu1/maketest.log, or `scripts/verdict` on that log.
- **`714-kit-bsu1-mech`**: detection of the 11 rows above. It runs after 713.
- The pin sections, run in the lane under the box lock (`test-rxtsource test-startset test-memfn-guarded test-memfn-simdfloor test-memfn-rows test-memfn-finder test-memfn-g2`, make rc=2). Four were red, with two causes:
  - **test-rxtsource** (deliberate, re-pinned). The population moved by span_seed.rxt exactly: CENSUS/RUNSH files +1 (342 to 343 and 318 to 319), blocks +41 (7233 to 7274), lines +1145 (100188 to 101333); C3_PASS +1145 (24840 to 25985) and C3_VERIFIABLE +1145 (27259 to 28404). SKIP is unchanged: every case is python-verified.
  - **test-startset** (deliberate, re-pinned). `[vm-movers]` under `--engine=vm` found 41 movers not in manifest_s2_vm_forced.tsv, all span_seed.rxt blocks, and 0 manifest rows that are not movers. The manifest was regenerated with census_s1.py and only the corpus rows were taken. Of the regenerated manifest, only the 41 `tests/memfn/span_seed.rxt` rows were appended, with a header line (k147f2's append shape). The regeneration's other differences are NOT taken: forced spanarms/l1d27 +22/-22 by row text, auto spanarms +4/-4, and bench rows. The ID-keyed check reads them as unchanged, and they predate this lane. s2_vm_auto and s3_dfa are untouched.
  - **test-memfn-rows / test-memfn-finder** (one cause, the decider census). U1's new `kit_walk(&wf_spantable, ...)` in `wf_stretches` is a decider outside every census member, so the backstop counts 68 hits against 67, and S2985's plant reads that line as a third stray. Manager ruling R-1 (rulings file, 05:41):
    - `tests/memfn/decider_census.tsv` gains `wf_stretches` (fn) and `wf_spanrows` (data), answering **T-SPAN** (the span form table, wfS). T-SPAN joins the header's table list.
    - The retired `wf_span_head` chain had no census row: it used no backstop shape.
    - Re-derived from the map by running the census: MEMBER_COUNT 70 to 72, HITS 67 to 68.
    - S2985's expected strays stay at 2. The plant still turns its copied key walk and REN_ROWS call stray, and the count fell back from 3 once the new walk sat inside a member.
    - Census: 102 passed, 0 failed.
    - Rev 4.1 gained the note-missed line in §14 U1 and a §17 row in the same commit.
  - test-memfn-guarded, test-memfn-simdfloor and test-memfn-g2 were green. R71-5's simd-form sample floor held with the `.rxt` included.
