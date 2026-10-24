# 2026-10-23 r2 — memfn S3 C1 build, CODE critic round (pcrec-code-critic skill, first use)

- **Subject:** `lane/memfn-s3w` @ ae83da9d40b527ff0ace88d6cdb721ce50d97772. The S3 commit is b5b85aeac and the tests are d190e3a70. BASE is c3ea619c3.
- **Review tree:** `worktrees/crit-memfn-s3-c1`, detached at the subject and built once.
- **Critic texts and verification:** the sibling directory `2026-10-23-r2-memfn-s3-c1-code/`.

**Blinding.** The critics were denied:
- the lane's report and evidence (including its own prediction that two-byte non-case-pair stops still walk);
- the 605 results;
- the memfn journal and responses;
- the stop-ranking study;
- main's D176 and the PAIR plan rows.

Leaks: c2-trade saw `git log` commit subjects. The others report none.

## 1. Lenses as run

| lens | model | question | why chosen |
|---|---|---|---|
| emitted vs replaced | opus | C/asm of the new path vs `--memfn=no-wf-find`, per byte, over 139 patterns × 4 arms | emitted C changed |
| slot tracing (+ ruling check, contract, goals, round-1 roll-call, standing questions) | opus | does every slot reach its named table, and do the rulings hold? | a table/selector changed, plus rulings relied on |
| trade audit + check adequacy | sonnet | every moved pin and who judged it; do the checks and the bar represent the movers? | floors, pins and checks changed |
| house rules | sonnet | duplication, altitude, tables as if-chains, side effects, frames | C structure changed |
| verification | sonnet | re-ran every CONFIRMED repro | skill §5.2 |

## 2. Did the round catch the known-but-hidden issue?

**YES, twice and independently.** The hidden issue was that two-or-more-member stops which are not a case pair get a scalar walk. Both opus lenses found it blind:
- emit F3 (9/9 probes);
- slot F1 (PAIR still requires a run stretch: `ab(?=[Qq])`).

The verification found the lane's own examples `[a-]x` and `[:a]q` keep `memchr`, because a rarer single byte wins the stop. The real population is the critics' probes.

## 3. Findings and dispositions (VERIFIED unless noted)

| id | sev | finding | disposition |
|---|---|---|---|
| R2-1 (emit F3, slot F1) | speed | A 2+-member stop that is not a case pair, or a case pair outside a run stretch, gets a scalar walk where the old artifact used `memchr`: `ab(?=[Qq])`, `[xq]abc`-type stops. | **ASK FRANK.** This is Q6/[MEMFN-PAIRSTOP] (filed with trigger census + pair card). S3 itself creates the regression, so the recommendation is to widen PAIR's contract inside S3 (FIX-NOW). Otherwise these sites must not route to cover. |
| R2-2 (emit F1) | speed | Same-set windows (`\d{6}`, `\w{8}`, `[0-9a-f]{8}`, `[a-z]{16}`) lose the old run counter. Counted reads/byte: English ≤1.0; dense `\d{6}` 2.50, `[a-z]{16}` 1.94, `\w{8}` 1.15, `[0-9a-f]{8}` 1.13; old ≈1.0. (Verification corrected the critic's 6-12.5 model.) | **MEASURE in 588**, then decide. The general fix is the run-skip resume (round-1 C12, ideas.md) or Q1/Q2's priced choice. |
| R2-3 (emit F2, slot F2) | speed, SIMD layer only | A caseless word plus `\b` or a class position loses vrun (9/9). The emit_sweep `-fmemfn-simd` differ pin stays lowered 20→9. | **PLAN** (SIMD is off by default; §6 makes a SIMD-on loss a SIMD-thread finding). The pin lowering must be RECORDED as a judged trade in the report. |
| R2-4 (trade F2) | check broken | `make test-axes`'s memfn arm: `MEMFN_CLASS` lacks wf-find/wf-hors while `--list-axes` lists them, and tests/axes is untouched (static verification). | **FIX-NOW.** This also gives the corpus-wide answer check under the deny arms (trade F1). |
| R2-5 (slot F7) | contract | Spec/registry rows still name E-find, D-hors and HORS_MIN (D174), and the `wf-find` registry row over-promises. | **FIX-NOW** (doc). |
| R2-6 (slot F3) | maintenance | B-pair copies fn-pair's two-stream body. | **FIX-NOW** (share the body). |
| R2-7 (house) | maintenance | Partial round-1 fixes: Table D's actions are `if (w->hors)` at ~10 sites; `d_hors_holds` casts away const; the 320-byte buffer comment cites a non-existent bound; `"wf-hors"` is a bare literal; find_groups has a `build` flag on the query path; stale headers (`wf_b_search` window.c:2397, "preview art"). | **FIX-NOW** (small). |
| R2-8 (slot F6) | missed win | `(?<=[Qq])ab`: Table A picks a stop Table B cannot find, so cover declines. The old arm is the same. | **PLAN.** Resolved structurally by D176 Q1 (one priced choice over position × method). |
| R2-9 (slot F8) | doc | D-hors has an undocumented `whi >= 0` condition. | **DOC** (rev 3.3). |
| R2-10 (slot F9) | doc | window_site states no ranked, checkable goals. | **DOC** (rev 3.3 adds them). |
| R2-11 (trade F3) | gate | The bar fails on stratum geomeans and dropped rows, never on a single row. | **NOTED.** It is by the ruled bar (no stratum slower). Per-row SLOWER is listed for the owner. |
| R2-12 (trade F4) | coverage | The sample reaches 391/804 movers: no high-byte, utf8, wide-window or match-regime rows (python `re` generatability). | **PLAN:** a high-byte/utf8 timing class beside the generator limit. |
| R2-13 (trade F5) | pin | The DIFFER_PINS were measured pre-C1. | **NOTED:** job 606's `sweep_start` reads them, and they are re-pinned with cause if it is red. |
| R2-14 (emit F4) | speed, SUSPECTED | Literal runs like `\x00{8}` make more `memchr` calls. | **NOTED** (588's sample / R2-2 measurement). |

**Round-1 roll-call:** FIXED C1, C3, C7, C9, C13, C14. PARTLY C2 (SIMD: R2-3) and C15 (R2-5). C11 was not checked by the critic (evidence denied); job 606's census covers it.

**Rulings re-checked (slot lens), all agree with design and guide:**
- the FIND slot asked at the OFF layer variant;
- the KD_ALL revert;
- `table_ref` UNSTATED;
- a 2+-member stop below the candidate declines;
- E-find as its own row;
- D-hors admission unchanged.

## 4. PROBED-AND-HELD

- **Answers:** 2,849 answer comparisons with no difference (emit). The lane's differential had 3,600 cases, 0 bad.
- **Frames:** every kit frame is ≤ 4096 B (the largest is 3,456 B).
- **Table B:** every pick a cover site can reach renders (D1, D1c, D1w, PAIR, R7w; checked by compiles). R8/R3a/R3b/R2 are SIMD-layer only and asked at OFF; R4/R1 have no REPORT kind.
- **Floors:** no performance-form floor ends below BASE. The lowered floors are reach floors with causes (EMW 1124→510, PROD 1290→705, DOOR_CBM 1400→1179).
- **Size and the other entry points:** no regression found (emit).

## 5. Which lens caught what

| lens | what it caught |
|---|---|
| emitted vs replaced (opus) | R2-1, R2-2, R2-3 |
| slot tracing (opus) | R2-1, R2-3, R2-5, R2-6, R2-8, R2-9, R2-10, plus the round-1 roll-call |
| trade/checks (sonnet) | R2-4 (a real breakage nobody else saw), R2-11..13 |
| house (sonnet) | R2-7 |

## 6. Lessons, for main to append to docs/dev/guide/critics.md

1. The hidden-issue test passed again: both strong lenses found it blind.
2. **Verification earns its place.** It corrected a modelled magnitude (6-12.5 down to 1.1-2.5 reads/byte) and showed the lane's own example patterns were controls, not members.
3. The check-adequacy lens found a broken gate (test-axes) that no behaviour lens would see. Keep it whenever checks or flags change.
4. A ruling can be agreed with the design and still have an unmeasured consequence (R2-1 traces to the PAIR scope "today's scope"). The slot lens should list each ruling's consequences, not only its agreement.

## 7. Completeness

R2-1..R2-14 each have a disposition.
- **FIX-NOW:** R2-4, R2-5, R2-6, R2-7, and R2-1 if Frank agrees.
- **MEASURE:** R2-2.
- **PLAN:** R2-3, R2-8, R2-12.
- **DOC:** R2-9, R2-10.
- **NOTED:** R2-11, R2-13, R2-14.

The FIX-NOW lane waits for job 606, so the tree is not edited under a running validation.
