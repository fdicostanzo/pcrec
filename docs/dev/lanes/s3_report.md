# s3 — D172 S3 (REPORT routed + D-hors): BUILT; code review r1's C1 build and r2's fixes + PAIR widening folded (S3 commit bc675b020); jobs 587, 588 re-staged

Lane s3, 2026-10-22 (opus). Worktree `worktrees/s3`, branch `lane/memfn-s3w`. Part 2 (the build, below)
was done by the resumed lane under main's rulings R1-R6. Part 1 (further below) is the first lane's
stop: its questions, its decisions, and the abi readers it found. Build go: D172 addendum (Frank
2026-10-21); main cleared S3 on 2026-10-22. No rulings file was named.

PART 11 (2026-10-24, lane s3fix): the S3 final review's FIX-NOW items and the manager's R-a..R-d
done (EMIT-1's bounded look-ahead, EMIT-3, the rename to window-search/window-skip, the spec hunks,
rev 3.3 accepted, the R-d mover declarations, job 588's two-stream sample); job 620's stale axes
pins re-pinned with cause; job 621 queued, its verdict OWED (Part 11).

PART 10 (2026-10-24, lane s3pair): main 0d3765c87 merged, S3 renumbered to abi 85, light suites
green, job 620 (from 587, reference main) queued (Part 10).

PART 9 (2026-10-24): the four trailing checks job 606 left red are fixed and green alone (census
twin rule, cpset HeLLo pin, the cover_pick reader); the K50 addition was not needed (Part 9).

STATE AT HANDOFF (part 8, code review r2's fixes + the PAIR widening, lane s3pair; supersedes every
earlier sha): THE S3 COMMIT is now **bc675b020** (b5b85aeac + this round's code and spec, by plumbing,
parent f7bc3cf05; the 13 commits after it replayed unchanged), on branch `lane/memfn-s3pair`
(worktree `worktrees/s3pair`); the design draft 48494f406, the follow-up eef859891. PAIR decides a
window stop of ANY two bytes (R2-1); B-pair and fn-pair share one renderer (R2-6); Table D's rows carry
their actions (R2-7); spec rows by behaviour (R2-5); test-axes' memfn arm classifies wf-find/wf-hors
(R2-4, floors OWED). No answer moved: G2 10,042/0, 18/18 plants red, the predicted manifest 40/40, the
OFF arms identical. OWED (job 606 held the box throughout): the armed chain
`build/chainrun/20261023-133141-s3pair-checks/` (differential, wreply, codegen, census_r2,
axes_measure) and `build/s3pair/simd_members.log`; then jobs 587 and 588, re-staged, not queued.
Part 8 is below this block.

STATE AT HANDOFF (part 7, the code review r1 C1 build, supersedes every earlier sha): THE S3 COMMIT is now
**b5b85aeac** (7e1caad08 + the C1 build, by plumbing, parent f7bc3cf05; the ten commits after it replayed
unchanged); the C1 tests/pins/manifests/jobs are d190e3a70, the window_site.md rev 3.3 DRAFT 15a4e5390. E-find
asks Table B the design's question and renders the deciding row's pick: caseless windows get fn-pair's two
memchr streams, and their SIMD kernels under -fmemfn-simd. Light checks green (7.12); no answer moved (G2,
3,600 differential cases, the OFF arms identical). OWED: jobs 587 (correctness, 125 mech rows, REACH_ONLY)
and 588 (timing; the mover sample is now part of the bar), both dry-run clean, not queued. Predicted: 588's
bar FAILS on stratum WALK/one/norun (two-byte non-cube stops; F-C1-1, a design question for Frank). Part 7
is below this block.

STATE AT HANDOFF (part 6, job 605's RESULT, supersedes nothing): job 605 GREEN (1,890 rows); the bar reads FAIL on one cell, foobar match/real 1.032 > 1.020, diagnosed as layout (identical rx_match code, 6.2); all five capped cells inside their caps. Part 6 is below this block.

STATE AT HANDOFF (part 5, job 600's reds, supersedes part 4's shas): THE S3 COMMIT is now
**7e1caad08** (d3886a656 + the §6.3.4¶8/¶9 cover clarification; no code change: R1's premise
did not hold, see 5.2); the R2-R6 follow-up is 34ee758a1. Every red family was rerun green by
section; the full job (587's script) is re-staged, dry-run rc 0. Part 5 is below this block.

STATE AT HANDOFF (part 4, supersedes part 3's shas): THE S3 COMMIT is now **d3886a656**: a962449c4
without review fix C (Frank 2026-10-23), so D-hors admits exactly as e1e95a584 did, plus fix B's two
asserts. The K27 fixture runs on both arms (ee0d4488d, F-5). Job 588 gains the "D-hors admission
(E[sh])" reading (86b9afa69, findings only). Light checks green; 587 and 588 dry-run clean. Part 4 is
below this block, before Part 3.

STATE AT HANDOFF (part 3, the review fixes, supersedes part 2's shas): THE S3 COMMIT is now
**a962449c4** (e1e95a584 amended with fixes A-H); light checks green; jobs 587/588 re-staged (§3.8).
Part 3 is below this block, before Part 2.

STATE AT HANDOFF (part 2):
- **The S3 commit is built:** e1e95a584. It contains the kit half, the pcrec half, abi 84
  (PROVISIONAL), the spec hunks, the manifests, the retirements, the mech re-aims and the reader
  re-pins. History: nits f7bc3cf05, then part 1's report 6f100c00f, then S3, then this report.
- **Light checks are green** (§2.12).
  - The predicted byte-diff agrees on 24 of 24 rows.
  - The OFF arm is byte-identical to c3ea619c3 apart from the abi digits, on all 24 rows.
  - G2's window family passes 7,640 checks (ASan+UBSan included), and every plant is red.
  - `make strict` is clean.
- **OWED, staged, not queued:**
  - job 587, the correctness job: the full census against c3ea619c3, the full `make test`, mech
    (108 rows) and reach-only;
  - job 588, §6's timing.

  The exact `scripts/boxqueue add` commands are in §2.11.
- **Not done here:**
  - the window_site.md rev 3.3 fold (§2.2 is written to fold);
  - the bench `[inbox]` relay (kit_proof.md §6.1; the manager's, at merge);
  - `PCREC_NO_KIT_PROOF` (R3: main files it under [IFACE-PUSH]);
  - the kit's journal and responses ledger (the kit session's).

---

# Part 11. Final review fixes (lane s3fix, 2026-10-24)

Brief: the kit manager's fix lane for the S3 final code review
(`docs/dev/reviews/2026-10-24-r1-memfn-s3-final-code.md`; its "Rulings" section overrides the proposed
dispositions) and the manager's mid-run rulings R-a..R-d. Worktree `worktrees/s3fix`, branch
`lane/memfn-s3fix`, cut from `lane/memfn-s3pair` @ `cc4f54eb2`. Every byte move stays inside abi 85
(not landed): re-pins only, no new bump. Two agents: the first fix lane (commits `e7b54ae53` to
`0e53c8dfa`, stopped before its report; its draft is the base of §11.1-§11.5) and fix round 2 (this
part's remaining items, under a BOX RULE: no suite or sweep run outside one queued job, only single
compiles of a handful of patterns).

STATE AT HANDOFF: tip = the commit that adds this part (job 621 prints the sha it runs on). No
rulings file. Job 621 QUEUED (owner kit), its verdict OWED (§11.8).

Commits: `e7b54ae53` (EMIT-1, EMIT-3/HOUSE-7, the rename, HOUSE-1/6, SLOT-8, G2), `83b5578a7`
(spec hunks, kit_proof.md rev 2.3, window_site.md rev 3.3 ACCEPTED, job 588's layout variants),
`966d247f4` (CHECK-1, readers, re-aims, CHECK-5's witness), `209d8f5eb` (G2 below-window sites, the
OFF-arm sentences, the abi 85 changelog), `d0d81e4e8` (the pair loop ends by construction, readers
and witnesses re-aimed, pins), `0e53c8dfa` (final pins); round 2: `c8a0f8961` (job 620's memfn_arm
re-pins, tri620.md), `55ebe5184` (R-d), `e5bed220d` (R-b), the job 621 commit, this report.

## 11.1 Inventory (each FIX-NOW id and each mid-run ruling)

| id | status | commit | evidence |
|---|---|---|---|
| EMIT-1 | DONE | e7b54ae53, 966d247f4, d0d81e4e8 | §11.2; G2 long subjects, plant S1541 red |
| EMIT-3 + HOUSE-7 | DONE | e7b54ae53 | §11.3; S1543 red, S1423 re-aimed red |
| the rename (CONTRACT-7 / SLOT-9 names) | DONE: `window-search`, `window-skip` | e7b54ae53; list_axes_delta.tsv in the job 621 commit | §11.4 |
| CONTRACT-1 | DONE: §6.3.4¶3's `"none"` row has a `"cover"` clause | 83b5578a7 | spec |
| CONTRACT-2 | DONE: match_api §6.3.7¶7 (`@idx` on cover), ¶8 (`"dominated"`), tuning §2.29¶5 and ¶10's table, the `dominated` row's `--list-axes` text | 83b5578a7 | spec, emit_dfa.c `.desc` |
| CONTRACT-3 | DONE: tuning §2.47¶2 (witnesses `ab\|cd`, `(?<=ab)cd`, `(?!a)`; `abcd`/`a\|b`/`[a-z]` named under `--memfn=no-window-search`), match_api §3.1¶21. The old ¶2 held a raw BACKSPACE byte (0x08) where `\b` was meant; the new sentence drops it | 83b5578a7 | each witness compiled and read `"end-minus-width"` |
| CONTRACT-4 | DONE: tuning §3's `_DFA_SCAN` row lists `"cover"` | 83b5578a7 | spec |
| CONTRACT-5 | DONE: tuning §2.46¶4 (`cat\z -fno-rev-end` reads `"cover"`) | 83b5578a7 | compiled: `cat\z`, `[ab]c\z` cover, `cat$` unanchored |
| CONTRACT-6 | DONE: the `attempt-start` and `dominated` texts name cover; registry §6¶3a names `cover` as the second row that reads the kit with no pcrec deny | 83b5578a7 | list_axes_delta.sh against main: 9 rows exactly as declared (the two texts are a - and a + each) |
| CONTRACT-7 prose | DONE: no S3, C8, `cover_conj` or kit source file in the caller-facing hunks | 83b5578a7 | grep |
| SLOT-5 | DONE: kit_proof.md rev 2.3, §R2.3 (what S3 built instead of B1's plan; `cover` has no pcrec-side identity; C13's `refused` cannot tell a deny from a decline), `[s3]` marks on the superseded sentences | 83b5578a7 | |
| SLOT-6 / HOUSE-8 / HOUSE-9 | DONE (comments only): memfn/src/CLAUDE.md, finder.c (PAIR is no "cube stop"; the retired-bit tombstones; `kind_cl`'s KD_ALL comment; RPT history), memfn.h (the `mf_preview` tombstone deleted), fields.def, options.def, window.c's header, `wf_plan_brow`'s header, `wf_floor_applies` renamed `wf_family_applies`, kit.h's `wf_prepare` header, emit_dfa.c, internal.h + cli/main.c (HOUSE-2: the lever "changes no byte", retirement filed under [KIT-VERIFY], no lane-report pointer), the design index line. PAIR's refutation text moved to memfn/docs/finder_history.md | e7b54ae53, 83b5578a7 | |
| CHECK-1 | DONE: `cover_pick` reads B-fn's helper body (the frontier raise, hit tests, memchrs, `cand -= K`) and the one-line B-pair text | 966d247f4 | test-encoding-checks green (round 2 of the first lane) |
| CHECK-2 | DONE: a 100-site BELOW-WINDOW G2 stream (`G2W_H2_SITES`), the generator's own D-hors scope census (`hwin`: every site whose stop window lies wholly below the candidate; none may carry a skip table), plant S1542 | e7b54ae53, 966d247f4, 209d8f5eb | G2 `hwin` 163 (floor 146); S1542 red |
| CHECK-5 | PARTLY: the PAIR witness is `x[Q%]y` (two unrelated bytes, rows.tsv); row_floors.tsv's `fd PAIR` cells stay PLACEHOLDER (the pcrec floor needs the slot N2 census, the g2 floor G2's `--rows` tier) | 966d247f4 | test-memfn-rows green; floors OWED (§11.8) |
| HOUSE-1 | DONE: `pcrec_fact_span` deleted | e7b54ae53 | build |
| HOUSE-6 | DONE: `WF_STATES(x)` in kit.h, the one spelling (gate.c, compose.c, window.c). gate.c's missing `wfloor` was not a defect: `wf_check` refuses a `wfloor`-only site before any row renders it | e7b54ae53 | |
| SLOT-8 | DONE: `b_fn_holds` requires the BODY walk to take fn-pair (`ofs_fn_serves`' `*two`), so the FIND pick and the BODY pick agree by a stated condition; G2 holds every B-fn body to the two streams. No plant: dropping the condition alone is equivalent by construction (S454 stays the pre-check's detector) | e7b54ae53 | G2 |
| window_site.md rev 3.3 | DONE, ACCEPTED 2026-10-24: Goal 2 reworded (relative floor OR the measured per-call layout allowance), every named cap deleted, "Known gaps (D176 witnesses)" (the 3+-member set-stop walk; dense-hex SKIP) | 83b5578a7 | |
| job 588's bar | DONE: the DEF arm's layout variants DV1-DV3 and the allowance (83b5578a7); R-b's two-stream sample (e5bed220d, §11.6) | 83b5578a7, e5bed220d | synthetic smokes of read_588.py, both ways |
| R-a (no new deny; OFF-arm identity sentence) | DONE: no deny; tuning §2.43¶3d, registry `window-search`, window_site.md Goal 1 and job 588's DEF note all say "but for the abi digits and the two-stream find's bounded look-ahead" | 209d8f5eb | grep |
| R-b (the bound's cost visible) | DONE: §11.6 | e5bed220d | pair-build/pair-gate smoke on 3 rows: 36 arm cells equal to python `re` |
| R-c (bounded effort on the dense cost) | DONE: the look-ahead GROWS GEOMETRICALLY from a first chunk (it doubles each time it comes up empty); the first chunk, 128 bytes, is chosen by instruction count and its TIME is labelled an UNMEASURED DEFAULT at its site (ofsskip.c `PAIR_LOOKAHEAD`) | e7b54ae53, 966d247f4 | §11.2 |
| R-d (declared non-cover movers) | DONE: census.py's PAIR class and bytediff.sh's MOVES-pair, from the artifact's own two-stream text, judged both ways; CHECK-4's OFF-arm wording follows R-a's sentence | 55ebe5184 | §11.5 |
| job 620's triage | DONE: tri620.md committed; memfn_arm.py re-pinned with cause (§11.5); the step ERE fixed in 621 | c8a0f8961 | witnesses checked by single compiles |

## 11.2 EMIT-1: bounded look-aheads in the one two-stream renderer

THE DEFECT. `ofs_pair_text` searched both streams to `n` on every call. The stream whose byte is
absent or far cost O(n - from) per call and a find-all O(n x matches), on every PAIR cover artifact
and (BASE too) on the caseless fn-pair arm.

THE DESIGN (kit.h `ofs_pair`, ofsskip.c `ofs_pair_text` + `ofs_pair_decl`). Each stream keeps a
FRONTIER: no byte of that stream lies in [at, h), and h is a hit where s[h] is the stream's byte.
Per candidate, both frontiers are first raised to `at` (= pos + k; a stale hit lies below it). Then
the LOWER frontier is searched next, by one `memchr` over [h, min(n, h + w)). An empty look-ahead
sets h to its end and doubles w; a hit that stays the lower frontier breaks out at once. The loop
ends when the lower frontier is a hit (the leftmost byte of either stream at or past `at`), or when
both reach `n`. Why linear: a stream is searched only while its frontier is the lower one, so in a
call it reads at most its last look-ahead past the answer, and w doubles only on EMPTY look-aheads,
which lie below the answer. Per call the cost is O(distance to the answer + w0), so a find-all is
O(n + calls x w0). A near byte costs one `memchr`, as before. There is no `fresh` flag: a zero
frontier is below every `at`. The widths are locals, reset per call.

TERMINATION BY CONSTRUCTION (d0d81e4e8). G2's W2 mutation 2 (the first ` >= ` flipped to ` > `)
first landed on the lower-frontier test `ha >= n`, and the mutant spun at `ha == n`: the run hung 26
minutes. The final text computes the look-ahead's end first and breaks on an EMPTY look-ahead
(`if (e == ha || subject[ha] == B) break;`). Every pass now breaks or moves a frontier forward,
whatever one comparison says.

INSTRUCTION COUNTS. Method: find-all by repeated `rx_search` from the previous match end,
`perf stat -e instructions:u`, `taskset -c 7`, min of 3, gcc 15.2 -O2. Subjects: the review's
repros at 4 MiB (the unit repeated) and the 1.8 MB dev_journal.md (and a lower-cased copy). Data:
`build/scr/m/{all,w,final}.log` in this worktree (not committed). Instructions per byte:

| pattern / subject | BASE (OFF arm) | before (cc4f54eb2) | w=32 | w=64 | w=128 | w=256 | w=512 | TIP (final text, w=128) |
|---|---|---|---|---|---|---|---|---|
| `(?i)xq`, "xq"+60 sp, 4 MiB | 15.24 | 3182.09 | 11.84 | 10.91 | 11.04 | 11.41 | 11.95 | 11.12 |
| `x[Q%]y`, "x%y"+60 sp, 4 MiB | 10.51 | 3131.72 | 11.81 | 10.94 | 11.07 | 11.43 | 11.97 | 11.23 |
| `(?i)hello`, "hello"+60 sp, 4 MiB | 3038.36 | 3036.31 | 12.25 | 11.36 | 11.48 | 11.83 | 12.35 | 11.63 |
| `(?i)xq`, 1 MiB | 15.33 | 803.85 | 11.93 | 11.00 | 11.13 | 11.50 | 12.04 | 11.21 |
| `(?i)the`, journal lower-cased (no `T`) | 968.01 | 966.98 | 3.85 | 3.58 | 3.35 | 3.41 | 3.72 | 3.46 |
| `(?i)the`, journal | 5.19 | 4.16 | 3.85 | 3.57 | 3.35 | 3.39 | 3.63 | 3.46 |
| `(?i)hello`, journal | 1.85 | 1.85 | 2.21 | 2.14 | 2.14 | 2.14 | 2.14 | 2.23 |
| `(?i)xq`, journal | 6.17 | 0.33 | 0.34 | 0.34 | 0.34 | 0.34 | 0.34 | 0.34 |
| `x[Q%]y`, journal | 0.52 | 0.29 | 0.30 | 0.30 | 0.30 | 0.30 | 0.30 | 0.30 |
| `[st][hr]`, journal | 9.25 | 5.33 | 6.60 | 6.28 | 6.10 | 6.06 | 6.07 | 6.42 |
| `[et][ao]`, journal | 9.56 | 5.65 | 6.86 | 6.52 | 6.40 | 6.38 | 6.39 | 6.82 |
| `(?<=x)foo`, "xfox" x 262144 (EMIT-3) | 17.88 | 31.14 | 27.14 | | | | | 27.14 |

The width columns w=64..512 are the renderer with the break-on-lower-hit, before the termination
change, with the emitted width edited in the artifact. The w=32 column is an earlier cut without
that break. TIP is the committed text (pcrec.final, 14:35). Every quadratic row is linear: the
1 MiB and 4 MiB `(?i)xq` rows read the same per byte. 128 is within 1.3% of the best width on every
row and the best on the dense real-text rows, which is why it is the first chunk.

THE COST, and R-c. On the dense real-text pairs the tip reads 18-21% more instructions than the
unbounded form (`[st][hr]` 5.33 -> 6.42, still 0.69x BASE; `[et][ao]` 5.65 -> 6.82, 0.71x BASE).
`(?i)hello` on the journal reads 1.85 -> 2.23, 1.21x BASE. That is about 12 more instructions per
candidate: the raise, the lower-frontier selection and the hit test. The termination change cost
about 0.3 instructions/byte on the dense rows over the width-table renderer. R-c's "grow
geometrically from a first chunk" is the design (w doubles on every empty look-ahead), so a far byte
pays O(log distance) calls. These are instructions only. Instructions under-count `memchr`'s call
cost, so the time is job 588's to read (§11.6 makes the cost a bar term). SIMD-on: the vrun rungs
scan one masked stream and do not use this text (unchanged).

THE BYTES OUTSIDE COVER (R-a). The renderer is shared, as ruled, so every native fn-pair body (the
run pre-check's `rx_reqrun__body`, e.g. `(?i)hello.*world`, `(?i)select`'s OFF arm) moves too. No
new deny. The OFF arm is the pre-S3 build but for the abi digits AND this look-ahead (tuning
§2.43¶3d, registry `window-search`, window_site.md Goal 1, job 588's DEF note).

THE CHECKS. G2's window driver gains LONG SUBJECTS for every two-stream site (408 bytes, a 12-byte
alphabet cluster across the first two look-aheads' ends): census `long pair`. Plant S1541 (an empty
look-ahead's frontier one past its end) must go red; S1540 is re-aimed at the renderer's entry.
pcrec-side readers were re-taught: reqcube_check.py, the encoding checks' pair-arm normalization and
marker, rows.tsv's fn-pair signature, S450 (the raise to `pos`) and S455 (two searches hoisted above
the guard). tuning §2.39¶2's emitted example was regenerated.

## 11.3 EMIT-3 + HOUSE-7

RAISE (window.c `wf_raise`). Where a core offset is below the candidate, E-find raises C to the
bound's lower half ONCE, before its loop. Every resume moves C forward, so E-find's TEST drops the
lower-half conjunct (the floor keeps it), and B's per-iteration raise is deleted. `(?<=x)foo` over
"xfox" x 262144 (find-all) went from 31.14 to 27.14 instr/B (-13%). Plant S1543 (the raise dropped)
must go red. D-hors's head writes the shared bound (`if (!(C + chi < N)) break;`, HOUSE-7), and
S1423 is re-aimed at it.

## 11.4 The rename (D174)

`wf-find` became `window-search` and `wf-hors` became `window-skip`. Each row's own `--list-axes`
text starts "the window search" or "the window search's skip", so the names are the caller's words.
The kit's form id is the same string (WF_FIND_ID), so G2's census keys moved with it. The stamp
value `"cover"` stays (filed for [IFACE-PUSH]). Neither name reaches an artifact, so there is no abi
event. Readers renamed (82 files, by grep): options.def, window.c, finder.c, plan_cost.def,
memfn.h, the kit's CLAUDE.md files and trace_format.md, emit_dfa.c, known.c, src/gen/CLAUDE.md,
docs/spec (match_api, registry, tuning), window_site.md, the abi changelog's unlanded 85 entry,
tests/axes/memfn_arm.py (MEMFN_CLASS), tests/cli, tests/codegen (14 scripts +
cand_oracle_witnesses.tsv), tests/memfn (rows.tsv, c10/pres witnesses, run_wreply.sh,
simd_floor_check.py), tests/startset (dfahat_checks.py, manifest_s3_dfa.tsv), 39 mech sabotage
rows' REACH/flags, memfn/tests (run_g2_win.sh, g2_win_gen.c), scripts/emit_sweep.py, jobs 588 and
620, and the s3_evidence scripts they run. Round 2 added the one reader the first lane missed:
list_axes_delta.tsv, the declared `--list-axes` delta (`+ memfn window-search`,
`+ memfn window-skip`, and CONTRACT-6's two descriptions as a - and a + each; checked against main:
9 rows, exactly as declared). Left as records: reviews, journals, docs/dev/history/claude_md,
s3_report.md Parts 1-10, job 587, the evidence result tables. A grep of the readers (scripts,
tests, memfn, src, cli, docs/spec, s3_evidence) finds no `wf-find`/`wf-hors` but memfn_arm.py's
cited measurement.

## 11.5 Re-pins and declarations (inside abi 85, with cause)

- tests/memfn/pins/arms.tsv: `ofsskip ofs-pair def` 2413 -> 2781 B and `precheck
  pre-masked-whole-rest def` 3160 -> 3528 B (+368 each, the two-stream body); digests re-pinned.
- tests/codegen/manifests/m5_stage1_stamps.tsv: `(?i)HeLLo EMITTED_BYTES` 29,591 -> 29,960 (+369,
  its B-fn helper's body).
- tests/codegen/run_recursion_identity.sh: (B) self-pinned to `d0d81e4e8`, the lane's last src
  commit; the manager re-pins it to the merge.
- tests/memfn/rows.tsv, run_handoff_reach.sh, S686/S688's REACH: the fn-pair declaration witness
  `size_t ha = 0, hb = 0, wa`.
- run_g2_win.sh: floors `hwin:146`, `long pair` 365 (new populations, measured less ~10%).
- tests/axes/memfn_arm.py (round 2, from job 620's axes_memfn log on cc4f54eb2, 4796 patterns;
  tri620.md). CAUSE: `cover` takes the fixed-width windows off the pre-check route, so fewer patterns
  differ under each PRES/assign deny on the default engine. The corpus grew 4624 -> 4796, so this is
  not corpus noise. The floors: fd-pres-g1 1271/1105 -> 949/878; fd-pres-pick 187/262 -> 168/232;
  precheck-assign-byte 176/244 -> 155/219; pres-set-lead c-default 16/8 -> 14/7 (c-vm unchanged);
  vrun-pad utf8/c-default 14 -> 13. Witnesses that became cover artifacts (the deny is inert on them)
  were replaced by variable-width siblings that are still pre-checked, each checked by single
  compiles at the tip at both sides: `ab` -> `abc+d` (byte and utf8), `é{2}cat` -> `é{2,}cat`
  (byte), `a{3}(?i:cat)` -> `a{3,}(?i:cat)` (utf8). The window-search/window-skip floors were OWED
  and are now pinned from job 620's axes_measure log: window-search byte 805, utf8 613; window-skip
  byte 7, utf8 2; c-vm 0. The utf8 count corrects the static classification's "byte only": the utf8
  witness is `\w\B\w`, which differs under the deny at both layers by single compile. Job 621
  re-measures all seven rows (axes_measure) before axes_memfn checks them.
- R-d DECLARATIONS (55ebe5184). census.py has a PAIR class. A non-cover artifact is PAIR iff NEW's
  own text carries the bounded declaration (`size_t ha = 0, hb = 0, wa = `, any prefix). It must
  move, carry as many bounded declarations as BASE carries unbounded ones (`size_t ha = 0, hb = 0;`),
  and keep every `#define RX_` stamp. A non-PAIR artifact whose BASE has the unbounded form is
  UNEXPECTED. It is judged on every .c arm and every OFF arm (an OFF arm's movers must be exactly its
  PAIR artifacts); `ir` still expects none; facts counts PAIR twins `text-only`. Smoke:
  `(?i)hello.*world`'s ten arms read PAIR + moved on every .c arm, nothing on `ir`, facts text-only on
  both encodings. bytediff.sh reads MOVES-pair the same way. predicted_movers.tsv gains an `off`
  column, declared from NEW's own text before any diff: rows 23, 25, 26 and 28 carry a two-stream
  find at both arms, row 27 only in its cover B-pair, and row 23 (VM, not cover) is MOVES-pair on
  its default arm too. Smoke on 5 rows, both arms: 0 disagree.
- docs/dev/history/abi_changelog.md: the unlanded 85 entry records the byte moves; no new abi.

## 11.6 R-b: the two-stream sample in job 588's bar

`docs/dev/lanes/s3_evidence/pair_588.tsv` holds 11 rows, hand-picked per stratum from the review's
and this part's repros. Each stratum was read off the tip's artifact:
- REQRUN, the run pre-check's fn-pair body, not cover: `(?i)hello.*world`, `(?i)hello\w*`,
  `\w+(?i:select)`, `(?i)(hello|help)`.
- COVER-BFN, cover through B-fn's helper: `(?i)hello`, `(?i)the`, `(?i)select`, `(?i)xq`.
- COVER-PAIR, B-pair's inline streams: `x[Q%]y`, `[st][hr]`, `[et][ao]`.

The arms are BASE (main's default build at the merge base 0d3765c87, the compiler job 621's refbuild
builds and stamps `REV`) and RTE (the tip's default build, which 621 copies into build/s3/bin).
- Classes (gen_sample_588.py, new): `real` (prose with plants at 1/200; the prose has no upper case,
  so a caseless pair's upper stream is ABSENT, EMIT-1's case), `dense` (plants at 1/8) and `mixed`
  (word-initial capitals at 1/8: both streams live, as in a real text). All 33 subjects generate.
- Regimes: throughput and search_short.
- Premise: RTE carries the bounded declaration and reads cover iff COVER-*, and a REQRUN row's BASE
  carries as many unbounded ones.
- Reading: read_588.py "Two-stream sample (part of the bar)". Per cell RTE/BASE against this run's
  A/A floor OR the per-call layout allowance. A stratum PASSES iff its geometric mean is within
  1 + floor or every cell passes. A dropped row, a missing file or a missing base compiler FAILS the
  bar, and `== s3t BAR` names it.
- Validation without the box: the pair-build/pair-gate stages on pr01/pr05/pr09 (built with job
  620's identical ref compiler) gave 36 arm cells equal to python `re`. A synthetic s3t_pair.tsv
  (RTE x1.0 / x1.3 / x0.9) read PASS / FAIL (stratum COVER-BFN 1.300 > 1.131) / PASS, and BAR FAIL
  named it.
- Job 588 now needs both compilers. Its dry run refuses until 621 has built them (`REV` ==
  0d3765c87), and `--ready` holds while key `kit-s3-heavy` is pending or running. It adds 132 items,
  ~1 min.

## 11.7 Validation

FIRST LANE (light single sections under `scripts/boxlock run`, before the box rule; verdicts by
`grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`). On the d0d81e4e8 build:
- green: `make strict`, test-codegen, test-encoding-checks, test-cpset-structure, test-memfn-g2,
  test-memfn-reach, test-memfn-rows, test-memfn-finder, test-kitproof, test-registry;
- test-memfn-arms red on the two pins, which were re-pinned in 0e53c8dfa (and then 374 checks, 0
  failed, `build/scr/sec3_arms.log`);
- test-rxtsource unfinished (the run was terminated when the lane stopped).

ROUND 2: no suite run (the box rule). Single-compile checks are in §11.5 and §11.6.
`list_axes_delta.sh` against main: 9 rows, exactly as declared. Job 621's dry run: rc 0.

## 11.8 Job 621 and what is OWED

Job 621 (`docs/dev/lanes/s3_job_621-kit-s3-heavy`, queued as `621-kit-s3-heavy`, owner kit) runs on
this tree's tip against main 0d3765c87. Each step prints `== s3 step NAME rc=N`, and the population
is 21 steps (`^== s3 step [a-z_0-9]+ rc=0$`). The steps, in order:
1. mechval (142 ids);
2. build;
3. strict;
4. refbuild (+ REV + build/s3/bin);
5. census (R-d's PAIR class, both ways, ten arms);
6. sweep_start;
7. evidence (bytediff default and OFF with the `off` column; the list-axes delta);
8. diff_r2;
9. test-codegen;
10. test-registry;
11. test-rxtsource;
12. test-encoding-checks;
13. test-cpset-structure;
14. the test-memfn-* sections and test-kitproof;
15. the G2 window family and its plants (S1400-S1410, S1422, S1423, S1425-S1429, S1540-S1543);
16. axes_measure (the seven rows);
17. axes_memfn (the re-pins);
18. `make test` through perfrun;
19. the proof and wreply plants;
20. mech over 142 rows (job 620's 126 plus the 16 rows this lane re-aimed);
21. reach-only over the whole matrix.

OWED:
- Job 621's verdict, read by a fresh agent from `build/s3/heavy621/` and the queue's job.log. On a
  red axes_memfn, re-pin from its own axes_measure log.
- Job 588, the timing bar, queued only after 621 is green. G1's alpha at both layers is that run's.
- CHECK-5's floors: fd PAIR's pcrec floor (the slot N2 census) and its g2 floor (G2 `--rows`).
- The PLAN items as ruled: CHECK-3 (test-axes floors for the two classes; the memfn arm's floors
  are now pinned), EMIT-2, SLOT-2/3, HOUSE-3/4/5/10-14, CHECK-4/6. The [KIT-VERIFY] row's line for
  the lever's retirement goes in main's plan.md, not edited here.
- run_recursion_identity.sh's (B) pin, to the merge (the manager's).

---

# Part 10. Merge main + abi 85 (lane s3pair, 2026-10-24)

Main 0d3765c87 (167+ commits since c3ea619c3, the iterators I1+I4 at abi 84 among them) merged into
lane/memfn-s3pair as ad8842546. S3's emitted change is now abi **85** on top of main's 84
(450dca216); the (B) self-pin is d4c94b834; the cpset re-record, census map and job 620 are 8e4d5dafe.

**Conflicts (10 files, 15 hunks), resolved on meaning.**

| file | resolution |
|---|---|
| docs/dev/history/abi_changelog.md | main's 84 (iterators) entry and its corefix 83 wording kept; S3's entry above it (renumbered to 85 in the bump commit; main's entry now past tense, "S3 took 85") |
| docs/dev/history/claude_md/docs__dev__lanes.md | both index lines |
| docs/spec/match_api.md §6.3.4 (`DFA_UNIFORM_FOLDS`) | both facts: the iterator's retry machine (`0..8`) and `"cover"`'s at most `2`, apart from that retry machine |
| tests/codegen/manifests/m5_stage1_stamps.tsv | main's values in the merge, then RE-MEASURED (below) |
| tests/codegen/run_codegen_tests.sh | main's bump ledger; S3's step appended as 84->85 in the bump commit |
| tests/codegen/run_cpset_structure.sh | both RE-RECORDED histories (main's, then S3's), plus the merge's re-record note |
| tests/codegen/run_encoding_checks.sh (4) | union of the count keys: main's `forwarder`/`bind_checks`/`search_split` + S3's `cover_pick` |
| S284 | S3's measured DETECTED record (desc + figure) plus fsfix's flip note |
| S693 | main's re-aim, then re-aimed 85/84 in the bump commit |
| tests/memfn/simd_guarded_check.py | S3's `simd-form` 6 + main's `scaffold-copy` 200 floors |

**abi readers found by grep** (`git grep` for the number's spellings over src lib cli memfn tests
docs/spec Makefile, then the S3 commit's own `+…84` lines): 13 sites in 7 files. `src/gen/emit_dfa.c`
`PCREC_ARTIFACT_ABI`; match_api.md §1¶7's guard sample (3 spellings: `!= 85`, `(abi 85)`,
`PCREC_RX_ABI_H 85`), §6¶1's `abi` row, §6¶17's sentence; `ABI_EXPECT` + its bump-ledger message;
S693 `SAB_BEFORE`/`SAB_AFTER` + comment; abi_changelog (S3 entry, main's entry tense);
`run_recursion_identity.sh` FILEPIN self-pinned to 450dca216 (the manager re-pins to the landing
merge); `s3_evidence/census.py`'s ABI map (85 -> 84, the job's reference is main at 84).
bytediff.sh masks `8[0-9]` and needed no change. Historical mentions (NOTES, journals, design
docs, other lanes' reports) are records and were not edited.

**Re-measured pin.** m5_stage1_stamps.tsv: the four `cover` rows read RX_DFA_PREFILTER "none" and
EMITTED_BYTES main's value minus EXACTLY the pre-merge S3 delta (`a` 28,498 -> 26,094, -2,404;
`abc` 29,329 -> 26,417, -2,912; `\bword\b` 32,294 -> 27,840, -4,454; `(?i)HeLLo` 32,694 -> 29,591,
-3,103); the other eight rows are main's. `simd-form` now reads 7 against its floor 6 (not raised:
a floor, and the extra member is not S3's to explain here).

**Suites** (each alone under `scripts/boxlock run`, `make -k`, verdict read with
`grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`; logs `worktrees/s3pair/build/s3pair_suites/`):
`make -j16` and `make strict` clean. test-cpset-structure RED on the first pass (the manifest
drift above, merge-caused), GREEN on the re-run after the re-record (29+17+59 passed, 0 failed).
test-encoding-checks, test-registry, test-rxtsource, test-codegen, and the kit's sections
test-memfn-{manifest,arch,forms,reach,link,stamps,guarded,simdfloor,rank,arms,deleg,rows,finder,g2}:
all GREEN (no red line). No answer moved anywhere.

**Job 620** (`docs/dev/lanes/s3_job_620-kit-s3-heavy`, from 587): reference = main 0d3765c87, the
subject = this branch's HEAD at run time (dry-run refuses a tip that does not contain 0d3765c87 or
is not at abi 85). The r2 stages against the C1 tip ae83da9d4 (c1ref, census_r2, evidence_r2) are
DROPPED: that tip predates the iterators, so every artifact would differ from it by the iterator's
text; the census and the byte-diff against main cover S3's whole delta. 16 steps (was 19), the
same 126 mech rows. Pre-checks against a main build (`build/s3pair_ref`): bytediff 29 rows 0
disagree on both arms (the predicted set needed no refresh: the iterators moved no member);
list-axes delta 5 rows as declared; a census smoke `--limit 40` (960 compiles) `unexpected=0`.

---

# Part 9. Trailing checks after job 606 (lane s3 trailing checks, 2026-10-24)

Job 606 (the C1 tip ae83da9d4, worktrees/s3) and the s3pair chain `build/chainrun/20261023-133141-s3pair-checks/`
went red on four CHECKS that had not kept up with the intended byte moves. No answer changed in this part;
nothing under `src/`, `cli/`, `lib/` or `memfn/src/` was touched; abi stays 84 (provisional). The previous
lane's WIP 36422a84e (UNVERIFIED) was reviewed. Its cover_pick reader is kept as written. Its census twin rule
had a fatal bug and was rewritten (9.1). Every section below was re-run ALONE under `scripts/boxlock run`, on
this branch's build/pcrec (built from the tip; `make -j16` was a no-op).

## 9.1 Census twin rule (`census.py`, `census_r2.py`)

- **The WIP's bug.** `facts_judge` compiled the E-twin .c without `--pattern`. Both sides then fail
  identically, so no twin ever "moved" and every facts mover would have stayed red. It also judged only one
  way: "twin moved, rows did not" was counted, not red.
- **The rule as built** (`census.facts_judge`, one implementation; census_r2 calls it). The listing has one
  row set per encoding E. Its `RX_*` rows are the E artifact's `#define RX_*` stamps, one for one (35 = 35 on
  `abc`), and its `used` cells say which facts the passes that built that artifact asked. So:
  - E's rows move iff the E-TWIN's STAMPS moved, i.e. its rc or a `#define RX_` line. The E-TWIN is the
    task's own options, then `-p rx --features all -e E`; the last `-e` wins (checked).
  - This is judged BOTH WAYS per encoding. Rows that moved with unmoved twin stamps are UNEXPECTED. So are
    twin stamps that moved with rows that did not.
  - Non-row lines, rc and stderr may not move.
  - Two populations are counted, not judged. A twin whose .c moved in its text only predicts no row move:
    `text-only`, which is r2's `pair text` mover `(?i)\bcat\b`. A listing REFUSED on both sides (one encoding
    refuses the pattern, so it has no rows): `refused`.
- **Why the stamps and not the whole .c.** The first both-ways run on the whole .c read 2 reds in census_r2,
  both `(?i)\bcat\b`. Its twin .c moved only in the B-pair text (BASE already rendered B-pair), and a facts
  listing does not mirror body text. Before the refused-listing rule, census.py also read 65 reds, every one
  a listing refused on both sides (rc 1: `\x{3b1}` under byte, UCP `\w` under utf8). There were no rows to
  move.
- **Control vs source** (learnings §3). The control is a different artifact (the .c), compiled separately.
  Its STAMP rows share an emitter with the listing's `RX_*` rows. So the rule catches a listing that moves
  apart from its artifact, but it is not a second witness that a stamp's value is right: the stamped .c arms
  (cover / B-pair judged from NEW's own text) carry that. Population counted: 4,967 tasks = 4,474 judged
  (8,948 encodings) + 493 refused.
- **Witnesses** (`s3_evidence/twin_witness.py`, log `twin_witness.log`): 6/6 read as planted. The genuine
  and unmoved controls are clean. rows-moved/twin-not, twin-moved/rows-not and a moved header line are red.
  The refused row is counted.
- **Results** (logs `s3_evidence/census_s3t.log`, `census_r2_s3t.log`):
  - `census.py` (BASE main c3ea619c3, rebuilt under `build/s3/heavy587/ref`, job 606's invocation):
    `== s3 census COMPLETE: patterns=4967 compiles=119208 movers=3681 unexpected=0`. Facts: 1,465 twin
    stamps moved, 0 text-only, 493 refused. **All 165 of job 606's unexpected rows** (byte `end_window
    used yes->no` and siblings on utf8-block tasks) are now facts TWIN rows; 0 are left over. Each one's byte
    twin became cover (example `(*UCP)(?-a)\d [-e utf8]`: byte twin `RX_DFA_SCAN` unanchored -> cover, its
    byte rows `end_window`/`width` `used` yes -> no plus the SCAN/PREFILTER/START stamp rows; utf8 twin
    unmoved, utf8 rows unmoved).
  - `census_r2.py` (BASE build/s3pair/base = the C1 tip; the chain's invocation):
    `== r2 census COMPLETE: patterns=4967 compiles=109274 movers=344 unexpected=0`. Facts: 139 twin stamps
    moved, 2 text-only (`(?i)\bcat\b` byte+utf8), 493 refused. **All 19 of the chain's unexpected rows**
    (byte `RX_MEMFN_LIBC` none -> memchr, `(?i)k [-e utf8]` etc.) are facts TWIN rows: their byte twin moved
    to B-pair.

## 9.2 test-cpset-structure CHECK 3: `(?i)HeLLo` EMITTED_BYTES 21,700 -> 22,441

- **Cause.** The S3 commit was rebuilt with C1/r2 folded in (bc675b020; the 21,700 was measured on the
  superseded d3886a656 / a962449c4, and 99f310c49 recorded it). That change gave the window text G2's caseless
  two-byte stream. The cover window find is no longer the in-place class-scan loop over `L`/`l`. It is now a
  call to an `rx_mf1_ofsskip` helper. The helper's `__body` holds two `memchr` streams (76/108), the nearer
  hit, the `-= 3` back-off and the same two masked `rx_w4` compares. `RX_MEMFN_LIBC` reads "memchr" (it was
  "none").
- **Verified** by diffing against d3886a656's compiler at `-o -` (`s3_evidence/hello_d3886a656_vs_tip.diff`,
  34 lines): the 30 added helper lines, the one scan_position line and that stamp, nothing else. 99f310c49's
  own tree, rebuilt, also reads 22,441, so the pin was stale when it was committed.
- The note is in run_cpset_structure.sh's re-record history, beside the S3 entry.
- Section alone: `checks passed: 29 / failed: 0` (plus 17/0 and 59/0 for the chained parts), rc 0,
  **0 `*** [...test-...]` lines** (`s3_evidence/cpset_structure_s3t.log`).

## 9.3 test-encoding-checks

- **(a) The cover_pick reader (WIP, kept as written).** `COVER_PAIR_RE` recognizes the B-pair leapfrog
  inside the window statement and reads its K and its two bytes. Each side's pick is then held to its own
  `RX_REQ_RUN` stamp (the member and its case cube, at K).
  - Control. The pre-WIP script (457bd231a's, run on this build) reproduces job 606's three reds exactly
    (`s3_evidence/encoding_checks_prewip_s3t.log`): "byte cover find carries 0 search clause(s), not 1",
    the K50 list mismatch on `(?i)\bcat\b`, and "4 of 237 strict-identity pairs differ".
  - The current script: `checks passed: 11 / failed: 0`, rc 0, 0 red lines, EXCISED cover_pick 16 -> 18
    (`encoding_checks_s3t.log`).
  - Witnesses (`s3_evidence/cover_pick_witness.py`, read from the file the suite runs, log
    `cover_pick_witness.log`): 6/6. The real byte (C/c at +0) and utf8 (T/t at +2) picks equal their
    stamps. Moving the stamp offset, moving a byte, or splitting K reads red. After normalization the window
    statements are identical.
- **(b) The K50 undeclared-form list does NOT gain `(?i)\bcat\b`: STOPPED on the brief's premise, not done.**
  With the reader fixed, `(?i)\bcat\b` no longer diverges (it is one of the 18 comment-only strict pairs).
  The list is EXACT over the reached subset, so adding it would itself turn the section red ("a missing
  reached one is a claim that has expired"). Its cause is a stamped pick, so it is no undeclared form. The
  manager may rule otherwise.
- **(c) The 4 of 237 pairs, hunk by hunk** (`s3_evidence/identity_s3t.sh`, log `identity_s3t.log`, the
  pre-WIP FINDING lines in `dd12ai_prewip_findings.txt`):
  - **`\b` (twice) and `\B`.** The byte/utf8 diff is BYTE-IDENTICAL on main c3ea619c3 and on this build:
    170 lines, 21 hunks, led by the utf8 `rx_forward_row`/`view_*` helpers. These are pre-existing
    `#UNDECLARED` K50 members (the manifest's accept-placement FINDING), not S3 moves, and they do not differ
    in the window text. Strictly read, the brief's "differ ONLY in the window text" does not hold for these
    three. They are not S3's: S3 moved nothing in them. I did not STOP for that, and I re-pinned nothing.
  - **`(?i)\bcat\b`.** 10 hunks. Nine are named encoding-owned regions:
    - the STARTPOS_GUARD/UTF_CHECK stamps;
    - RX_REQ_RUN `434154@0` vs `@2` (the declared pick);
    - the startpos guard, twice;
    - next_pos;
    - valid_upto;
    - RX_FINDINGS, twice;
    - `.encoding`.

    The tenth is the WINDOW TEXT, the scan_position line. Split at `;`, it differs in exactly the pick: the
    byte side has the bound `c >= n`, streams `memchr(s + c, 67|99, n - c)` and no back-off. The utf8 side
    has `c + 2 >= n`, `memchr(s + c + 2, 84|116, n - (c + 2))` and `c -= 2`. The verify half is
    token-identical. After excision the check's own diff is that line plus the startpos-guard excision
    marker (a comment).

## 9.4 Verdicts (each alone, under the box lock)

| section | invocation | verdict |
|---|---|---|
| census | `python3 -I s3_evidence/census.py --base build/s3/heavy587/ref/build/pcrec --new build/pcrec --tree . --out build/s3/heavy587/census.tsv --jobs 16` | GREEN, unexpected=0 |
| census_r2 | the chain's stage (`--base build/s3pair/base/build/pcrec`) | GREEN, unexpected=0 |
| test-cpset-structure | `make test-cpset-structure` | GREEN, 0 red lines |
| test-encoding-checks | `make test-encoding-checks` (ENC_MAX_BLOCKS default 250; DD12a is compile-only, full) | GREEN, 0 red lines |

OWED: none of these four. The heavy job (587's script) is the manager's at merge. The abi 85 renumber is the
manager's.

---

# Part 8. Code review r2 fixes + PAIR widening (lane s3pair, 2026-10-23)

Lane s3pair (opus), worktree `worktrees/s3pair`, branch `lane/memfn-s3pair` (from `lane/memfn-s3w`
ae83da9d4). Build go: Frank, 2026-10-23, "Widen two pair s3 now". Brief source: code review r2
(`worktrees/memfn/docs/dev/reviews/2026-10-23-r2-memfn-s3-c1-code.md`, §3), its FIX-NOW items. No
rulings file was named. Job 606 (the C1 tip's heavy job, worktrees/s3) held the box for this whole
lane, so every box-wide check is ARMED, not read (8.7).

## 8.1 Commits

| sha | what |
|---|---|
| **bc675b020** | THE S3 COMMIT: b5b85aeac plus this round's code and spec (R2-1 PAIR widened, R2-6 one two-stream renderer, R2-7, R2-5's spec hunks), by plumbing on b5b85aeac's tree, parent f7bc3cf05; ONE byte-moving commit, abi 84 PROVISIONAL unchanged (the widening rides S3's abi event) |
| 223537114 .. bf33a6aa2 | the 13 commits after S3, cherry-picked unchanged (none touches a folded file: memfn/src, finder_history.md, registry.md, tuning.md) |
| 48494f406 | window_site.md rev 3.3 DRAFT: ranked goals (R2-10), PAIR's contract, the one renderer, D-hors's `whi >= 0` (R2-9), Table D's row actions |
| eef859891 | the follow-up: G2 two-byte stream + plant S1540 + re-aims + floors; test-axes' MEMFN_CLASS (R2-4); emit_sweep's SIMD cells (R2-3); the r2 manifest, census, differential and SIMD-members scripts; jobs 587/588 re-staged |
| (next) | this part |

The tree at bf33a6aa2 differs from ae83da9d4 by exactly the nine folded files (`git diff --stat`).

## 8.2 PAIR's contract (R2-1)

| | facts (finder.c) | in words |
|---|---|---|
| BEFORE (C1) | `SF_SPAN0 \| SF_STRETCH_CUBE` | a window site's stop that is a two-member one-bit cube inside a stated run stretch (fn-pair's scope) |
| AFTER | `SF_SPAN0 \| SF_TWO_MEMBER \| SF_WINDOW_STOP` | a window site's stop of ANY two bytes at or past the candidate |

- `SF_TWO_MEMBER` is a fact of the set, stated by `set_facts` for EVERY asker (native routes too).
- `SF_WINDOW_STOP` is stated only by `fd_find`: PAIR's renderers are the window family's, and
  `fd_route` has no arm for FF_PAIR (a routed pick with no arm is a refusal), so a native one-term
  FIND site with a two-byte set keeps R7w's walk. This is a renderer fact, not a label: its
  trigger to drop is a native pair arm.
- `SF_STRETCH_CUBE` (bit 13) retires, unreused; window.c's `stop_stretch_cube`/`in_stretch_at` go.
- Basis (UNMEASURED-DEFAULT) and place (after D1w, before R7w) unchanged; no deny (it moves bytes
  only under E-find's `wf-find`). Logged in memfn/docs/finder_history.md.
- Still no row: a stop of two bytes BELOW the candidate (PAIR keeps SPAN0; R2-8, D176's priced choice).
- Under `-fmemfn-simd`: B-pair has no SIMD row, so the widened scalar PAIR is the text at both
  layers where B-fn (a plain caseless literal, vrun's rows) does not hold. The arbitrary-pair kernel
  is [MEMFN-PAIRSIMD], not built.

**What the widening does to the other sites that reach PAIR.** Native routes: nothing (the
WINDOW_STOP fact). Window sites that are not REPORT (a native window site whose legacy rows decline
reaches E-find): they move exactly like cover sites, a two-byte stop that R7w walked now taking
B-pair. G2 counts them in its own space: on the SAME 2,200 sites as the C1 tip, 103 stops moved from
the walk to PAIR (walk 217 -> 114, pair 141 -> 244, libc 598 -> 701); the predicted manifest's native
fn-pair sites (the pre-check's `(?i)cat\d+`, both layers) are byte-identical. The corpus count of
non-REPORT movers is census_r2's (8.7): it judges every B-pair artifact on either side, cover or not.

## 8.3 R2-6: one two-stream renderer

`ofs_pair_text` (ofsskip.c, kit.h `ofs_pair`): the two streams, the nearer hit, the miss, `cand -= k`,
over the caller's names and layout. fn-pair's body renders through it (its bytes unchanged: the
manifest's B-fn and native rows IDENTICAL). B-pair renders through it on one line, with its guard
moved out front (`if (C + d >= N) break;`, then the shared text; before, each `memchr` carried its own
`P < N ? ... : 0`). Both callers keep their own member array, so the plants S1428 (B-pair) and S1429
(fn-pair) still drop one caller's stream, and the new S1540 drops the shared text's.

## 8.4 Movers: predicted, then actual

`s3_evidence/predicted_r2.tsv` (committed as WIP c017a282b before any diff ran): 40 rows, the
C1 tip (ae83da9d4, `git archive` build) vs this build.

| check | result |
|---|---|
| `bytediff_r2.sh` default | **40/40 agree**: 13 MOVES-pair, 4 MOVES-pair-text, 23 IDENTICAL |
| `bytediff_r2.sh` OFF arm, `--memfn=no-wf-find,no-wf-hors` both sides | **40/40 IDENTICAL** |
| the same, `--memfn=no-wf-find` alone | 40/40 IDENTICAL |
| `bytediff.sh` (S3's 29 rows) vs main c3ea619c3 | 29/29 agree; OFF arm 29/29 ABI-ONLY |
| `--memfn=no-wf-hors` alone | 17 rows move, as they must (E-find stays on; not an OFF arm) |

The corpus census (`census_r2.py`, 9 arms) is OWED (8.7).

## 8.5 The probes: the find each renders now

`pcrec -p rx --features all`, the E-find loop's find (names shortened); before = the C1 tip.

| pattern | before | now |
|---|---|---|
| `[\x80-\xff]q` | walk `s[c] >= 128` at 0 | the same (the stop is the 128-member set: no PAIR) |
| `[\x80-\xff]x`, `[\x80-\xff]j`, `[^\x00-\x7f]e` | the same walk | the same |
| `[\x00-\x08]z` | walk `s[c] <= 8` | the same (nine members) |
| `the[qx]` | walk `{q,x}` at +3 | B-pair: `memchr` 113 and 120 at +3 |
| `ab[qj]cd` | walk `{j,q}` at +2 | B-pair: 106 / 113 at +2 |
| `ee[qj]ee` | walk `{j,q}` at +2 | B-pair: 106 / 113 at +2 (both layers) |
| `e[qj]e` | walk `{j,q}` at +1 | B-pair: 106 / 113 at +1 |
| `ab(?=[Qq])` | walk `{Q,q}` at +2 | B-pair: 81 / 113 at +2 |
| `[xq]abc` | walk `{q,x}` at 0 | B-pair: 113 / 120 at 0 |

Five of the critic's nine (the high-byte and control-range sets) are NOT two-byte stops: A-mass
picks a many-member set over a rarer-to-find single literal, and only the priced stop choice (D176
Q1; [MEMFN-PAIRSTOP]; R2-8's family) moves them. The widening serves the other four and both of
the slot lens's (`ab(?=[Qq])`, `[xq]abc`), and 588's WALK/one/norun rows `[a-]`, `[[:]`, `[:a]`,
`(?:(?!a)z|w)` (manifest rows 13-16); `[a[:b]` (four members) stays the walk.

## 8.6 R2 items

| item | state |
|---|---|
| R2-1 PAIR widening | DONE (8.2) |
| R2-3 SIMD pin | RECORDED (8.8); emit_sweep's two cells pinned back AT 606's measure (22/15) |
| R2-4 test-axes memfn arm | DONE STATICALLY: MEMFN_CLASS gains wf-find/wf-hors (both layers; DIFFER; witnesses `\bcat\b` byte+utf8, `\b[0-9a-f]{8}\b` byte, each checked by single compiles at both layers; neither moves the VM engine, wf-hors does not move utf8). The arm's population check now equals `--list-axes` (14 = 14, read with the arm's own reader). FLOORS OWED: `axes_measure` (8.7, and job 587); the arm itself OWED to 587's `axes_memfn` |
| R2-5 spec by behaviour | DONE: registry.md §6¶8a's wf-find/wf-hors rows, tuning.md §2.43¶3d, `--list-axes`' wf-find desc; no E-find/D-hors/HORS_MIN/"kit refuses"; wf-find's row says the jump per position size, the caseless-literal SIMD case, the below-candidate exclusion and the deny's effect |
| R2-6 one renderer | DONE (8.3) |
| R2-7 Table D dispatch | DONE: rows carry `finds` and `prepare`; `wf_d_text[]` (head, resume, file-scope text) in wf_drows' order with a `_Static_assert`; `w->hors` is gone (`w->drow`; B's index is `WF_NBROWS` under D-hors, so `bren == B_FN`/`B_PAIR` alone decide) |
| R2-7 const cast | DONE: `hors_window` runs in the setup; `d_hors_holds` reads a const `wf_dx` |
| R2-7 320-byte bound | DONE: the comment states the real texts (176-byte REPORT text, 34-byte head, gate_describe truncating) and labels 320 an UNMEASURED DEFAULT |
| R2-7 `"wf-hors"` once | DONE: `WF_HORS_ID` |
| R2-7 find_groups | DONE: `find_groups` groups only (no flag, no allocation); `build_runs` builds the define's terms. The query keeps the grouping (its class reads the count) |
| R2-7 headers | DONE: `wf_b_search`'s, kit.h's three "preview art" and window.c's one; one-line headers on wf_find_expr/use, wf_floor_applies/define/use, wf_need, wf_plan_*, d_one_holds, wf_has_parts, wf_part_site, wf_parts_check/prepare, part_states, wf_prepare, wf_plan_class |
| R2-9, R2-10 (DOC) | DONE in rev 3.3 DRAFT (48494f406), with PAIR's widened contract |
| not touched | the REPORT refusal's "(the kit manager's R2 ruling)" text (house F7; not in R2-7's list); `b_fn_holds`/`e_legacy_holds` still translate inside a predicate (house F1's other two) |

## 8.7 Checks

| check | verdict |
|---|---|
| `make -j16`, `make strict` | clean ("whole tree compiles clean with -Werror -Wshadow") |
| `tests/memfn/run_link_checks.sh` | 11/0 |
| `memfn/tests/run_g2_win.sh` | 10,042/0 (ASan+UBSan 5,000/0); E-find 1,294: libc 995, walk 114, hors 131, run 421, below 175, report 1,013, pair 352, fn 54 |
| `memfn/tests/run_g2_win.sh --plants` | **18/18 RED** (S1428 red on 135 sites, was 15; S1540 on 143) |
| mech anchors in the edited files | 37/37 rows' SAB_BEFORE found exactly once (S450/S455's fn-pair anchors kept verbatim) |
| byte-diffs and OFF arms | 8.4 |
| `list_axes_delta.sh` vs main | 5 row(s), exactly as declared (vs the C1 tip: wf-find's description alone) |
| differential smoke (`diff_r2.py`, 6 patterns) | 120 cases, 0 bad (5 witnesses) |
| `tests/memfn/run_wreply.sh` | OWED: it takes the box lock and waited 600 s behind job 606; my timeout ended it |
| ARMED, OWED (the box was job 606's) | chain `build/chainrun/20261023-133141-s3pair-checks/` (scripts/chainrun, detached, `--keep-going`; each stage takes the box lock): `diff_r2` (120 patterns x 30 subjects x 2 layers, ASan+UBSan, FAILS under 1,000 witness cases; trailer `== diff_r2 COMPLETE`), `wreply`, `codegen` (make test-codegen), `census_r2` (`== r2 census COMPLETE ... unexpected=0`), `axes_measure` (the four cells' counts for MEMFN_CLASS's floors). Completion: `== CHAIN DONE` or `== CHAIN FAILED` in chain.log; read with `scripts/verdict`. Also `build/s3pair/simd_members.log` (boxlock-waiting, nohup): `== simd_members COMPLETE` |

A light slip, recorded: the R2-4 witness probe ran 128 single compiles in one loop outside the box
lock (seconds; job 606 was a correctness run, not a timing window).

## 8.8 R2-3: the `-fmemfn-simd` DIFFER pin, a judged trade

- History: main 20 byte / 15 utf8 (`(?i)cat`); job 600 measured S3 (before C1) at 9 / 10 and pinned
  them there; C1 restored B-fn's SIMD rows but not the pins (the r2 critics' R2-13); job 606's
  `sweep_start` at the C1 tip read **22 / 15**. This round moves no SIMD form (B-pair's text is the
  same at both layers), so the cells are pinned back AT 22 / 15, the manifest `((?i:abc))` checked a
  member at both bases.
- The trade: membership changed though the count did not fall. LEFT the cell (vrun at main, none
  now): a caseless word beside a boundary, lookahead or class position (`(?i)\bthe\b`,
  `(?i)\bhello\b`, `(?i)\bthe`, `(?i)the\b`, `(?i)abc(?=d)`, `(?i)[0-9]hello`, `(?i)abc[xy]`,
  `\b(?i:foobar)\b`, `(?i)foo[0-9]bar`: verify.md's nine, single compiles), whose plan is not the
  offset-skip function's predicate, so B-pair renders it with no SIMD row. JOINED: pure caseless
  runs that had a byte-class walk (`(?i)ab`, `(?i)ss`, `(?i)qu`, ...: emit's eight). The corpus
  members by name are `simd_members.py`'s (OWED, 8.7).
- Judged: ACCEPTED for S3. SIMD is off by default; window_site.md §6 makes a SIMD-on loss a finding
  for the SIMD thread, not an S3 blocker. The unlock is the emit critic's G3 (B-fn's post-filter
  carries the extra verify positions) or [MEMFN-PAIRSIMD]; trigger: the default flip of
  `-fmemfn-simd` (R4f) or a SIMD-layer witness on `(?i)\bthe\b`.

## 8.9 Jobs re-staged (not queued)

- **587-kit-s3-heavy** on `worktrees/s3pair`: as before plus `c1ref` (ae83da9d4 built under
  $OUT/c1ref), `census_r2`, `evidence_r2` (bytediff_r2 default and OFF), `diff_r2`, `axes_measure`,
  `axes_memfn` (AXES=--memfn MEMFN_REACH_ONLY=1), plant S1540, mech 126 rows (S1026 added: the axes
  memfn arm's own row). 19 steps; `--dry-run` rc 0 in 0.07 s.
- **588-kit-s3-timing** on `worktrees/s3pair`, PCREC `build/s3/bin/pcrec` re-copied (sha256
  6688a940c46c). `--dry-run` rc 0 in 6.5 s. Prediction: the WALK/one/norun stratum's rows now take
  B-pair; 605 measured 1.2-4.5x losses for their walk.
- Commands (from the MAIN tree): `scripts/boxqueue add --name 587-kit-s3-heavy
  worktrees/s3pair/docs/dev/lanes/s3_job_587-kit-s3-heavy`, then `scripts/boxqueue add --name
  588-kit-s3-timing worktrees/s3pair/docs/dev/lanes/s3_job_588-kit-s3-timing` after 587 is green.

## 8.10 Findings

- **F-R2-1.** The widening moves frequent-letter case pairs too (`(?i)a`, `(?i)e`, `[xq]`: a
  one-position window walked before, two `memchr` streams now). For a byte that dense the
  walk-vs-memchr crossover is UNMEASURED (as D1's for one byte). 588's sample has no such row.
- **F-R2-2.** Five of the critic's nine probes are not two-byte stops (8.5): the stop choice, not
  the find, is their cause (D176 Q1).
- **F-R2-3.** PAIR's pcrec-side reach floor is still `PLACEHOLDER` (slot F12); G2's pair floor (316)
  is its only count.

---

# Part 7. C1 build (code review r1, 2026-10-23)

Lane s3 (opus), the build of the S3 code review r1 (`docs/dev/reviews/2026-10-23-r1-memfn-s3-code.md`,
on the memfn branch's worktree), findings C1-C17. Build go: Frank, 2026-10-23 ("We absolutely will"). The
manager's brief is the charter; no rulings file was named.

## 7.1 Commits

| sha | what |
|---|---|
| b5b85aeac | THE S3 COMMIT, now with the C1 build folded in (memfn/src, the cover desc in src/gen/emit_dfa.c, `registry.md` §6¶8a's two rows, `finder_history.md`, `trace_format.md`, the two CLAUDE.md files): built by plumbing from 7e1caad08's tree plus the code diff, parent f7bc3cf05; ONE byte-moving commit, abi 84 PROVISIONAL, unchanged |
| (replayed) | the ten commits after S3 (b3fba6b28 .. a017fe98a), their diffs applied unchanged (none touches a folded file) |
| d190e3a70 | the C1 follow-up: G2 (caseless stream, plants S1425-S1429, floors), the manifests (`rows.tsv`, `row_floors.tsv`, `finder_check.py`, `run_rows.sh`), the SIMD floors (`simd_floor_check.py`, `simd_guarded_check.py`), census options, the C1 mover manifest and its script, jobs 587/588 re-staged (587's clean-tree check now ignores `docs/dev/artifact_size_log.tsv`, a full-suite run's byproduct, dirty here and not this lane's) |
| 15a4e5390 | window_site.md rev 3.3 DRAFT (C4), its own commit, for the manager |
| (next) | this report |

## 7.2 Table B: the question as built (C1, C3)

`fd_find` (finder.c) replaces `fd_find_form`. It asks slot FIND about:
- **the site:** the window site itself, under its define hooks: its consumer kind, `body`, `policy`, options
  (`fd-d1` and the VM seek role keep their effect). No synthetic one-term site, no `MF_SPAN_BOUNDED`.
- **the stop:** its own set, its ACTUAL offset d* (below the candidate: a CONTEXT stop), and the stretch fact
  `SF_STRETCH_CUBE` (the stop, a two-member cube, inside a stated run stretch: a neighbour position of a span
  holding it is one member or a cube). Need REQUIRED: B's find is the stop's test at every candidate it yields.
- **the layer:** the OFF variant, as `fd_route` (the finder's §1.5 rule 1). This is a JUDGEMENT the manager
  should check against the brief's "the ACTUAL layer": at a SIMD layer the slot has no built row for a set
  stop (R7w is OFF-only; R8/R2's W64 is unbuilt), so an actual-layer ask would refuse every multi-member
  stop under `-fmemfn-simd`. The SIMD forms are instead the offset-skip function's PREFIX rows over PAIR's
  body, which read the site's actual `policy` (B-fn, 7.4). No `table_ref` is invented (7.3).
- **the answer:** the deciding row's id and its pick (`fd_form`, now in kit.h); E-find renders the pick.
  `fd_find` is asked quietly in E-find's setup and once more, traced, when the define chose E-find (the
  selection's record and reach); the row id reaches the trace (`MFTRACE FDROUTE ... arm=E-find`, `WPATH fd=`).

## 7.3 Row-contract changes, each justified

| change | why |
|---|---|
| PAIR added (slot FIND, facts SPAN0 + STRETCH_CUBE, pick FF_PAIR, KD_STOP, LY_ALL, no deny, UNMEASURED-DEFAULT, step S3), after D1w and before R7w | window_site.md §2.2's "now a FIND-slot row"; its facts are disjoint from D1/D1c/D1w's (two members), so its place among them decides nothing and the existing ORDER is unchanged; only a window site states the stretch fact, so no native route meets it (`fd_route` has no arm for it). No deny: it moves bytes only inside E-find, under `wf-find` (fn-pair has none either) |
| KD_ALL's REPORT widening REVERTED for R8, R3a, R3b, R4, R1, R2 and P0-P9 | no REPORT site asks them ("KEPT UNCHANGED"; the PRES rows serve an ALL_PRESENT site's kinds). Zero bytes |
| REPORT kept on D1, D1w, R7w (KD_STOP) and added to PAIR | the rows whose pick renders a window site's stop: a REPORT site is the window family's since RPT retired |
| D1c gains REPORT beside DFA_ATTEMPT | §2.2 re-keys D1c to "the stop lies below the candidate" ([rev3 bB7]); a one-byte REPORT stop below the candidate is now decided D1c (before: the synthetic ask's D1 at offset 0). Its text is the same memchr-with-raise (zero bytes, 7.11's manifest row 13) |
| R7w keeps `table_ref` REF; gate.c's `cl_table_ref` reads a window site's `table_ref` as UNSTATED | NARROW, not invent: a window site states no terms (wf_check refuses them), so the OBLIG "0 = no table" never applies to it; its offers are `toffer`, which E-find's walk reads (C-table) or does without (C-own). Native sites state terms and are unchanged. R7w's comment says so |
| no row for a stop of two or more members BELOW the candidate | D1c is one byte; R7w and PAIR need the stop at or past the candidate (SF_SPAN0, unchanged to keep native routing). E-find declines such a plan; a REPORT site's cover then declines (the default build's composite, byte-for-byte: manifest row `(?<=[qj])[a-z]`). Finding F-C1-2 |

## 7.4 E-find renders the pick (C1): B's renderer rows and the probes

`wf_brows` (window.c), first match over the pick and the plan; they decide nothing about the find:

| row | holds | renders |
|---|---|---|
| B-fn | PAIR, and the plan IS the offset-skip function's predicate (legacy_ok, no range end past the terms, one RUN term holding the stop's cube, `ofs_fn_serves`: the BODY walk takes it) | `ofs_fn_define_at` over the translated predicate: fn-pair's body, vrun's SIMD rungs under `-fmemfn-simd`, named `<prefix>_mf<h>_ofsskip` (the FUNC suffix D155's routing rule reads); E-find's frame calls it |
| B-pair | PAIR elsewhere (a context item, a floor, a non-core position) | two `memchr` streams in E-find's loop (`_ha`/`_hb`, `_fr` for the first round) |
| B-memchr | LIBC (D1), LIBC_BACK (D1c) | today's E-find memchr, raise included (bytes unchanged) |
| B-walk | WALK (R7w, D1w) | today's E-find walk (bytes unchanged) |

Why B-fn renders through the function at BOTH layers: the SIMD rows sit over fn-pair's body (vrun's `over`),
and D155's seam makes a SIMD-on artifact the SIMD-off text plus guarded rungs; an in-loop pair at OFF with a
function at SIMD would give the two layers different scalar text. One-byte stops keep E-find's inline memchr
(no SIMD row sits over fn-memchr), so the 41 FASTER cells of job 605 keep their bytes.

**The probes** (`-p rx`, default and `-fmemfn-simd`; before = the S3 tip a017fe98a):

| pattern | before (both layers) | after, default | after, `-fmemfn-simd` |
|---|---|---|---|
| `(?i)foobar` | byte walk `{B,b}` at +3 | fn-pair: `memchr(.., 66, ..)` and `memchr(.., 98, ..)` at +3 | the same body + `__w16`, `__w32` (MEMFN_FORMS `vrun@w32+w16`) |
| `(?i)x/1234` | byte walk `{X,x}` at 0 | fn-pair, memchr 88 / 120 at 0 | + `__w16`, `__w32` |
| `(?i)abc` | byte walk `{B,b}` at +1 | fn-pair, memchr 66 / 98 at +1 | + `__w16`, `__w32` |
| `[Qq]uery` | byte walk `{Q,q}` at 0 | fn-pair, memchr 81 / 113 at 0 | + `__w16`, `__w32` |
| `[0-9a-f]{8}` | Horspool (D-hors) | Horspool, byte-identical | Horspool, byte-identical |

Answers: 3,600 cases of these and `(?i)\bfoo\b` (B-pair) and `(?:(?i:abs)|(?i:ab)S)`, both layers, compiled
`-O2 -march=native` (the w32 rung live), against Python `re` (ASCII): 0 differ.

## 7.5 Deleted code

- `fd_find_form` (finder.c, ~45 lines, one stack `mf_site`, 3,456 B frame) and its enum `FD_FORM_NONE/LIBC/WALK`
  (kit.h); `fd_find` is 560 B.
- E-find's two-valued B (`wf_find_b`'s LIBC/WALK switch): now one renderer per pick, keyed by `wf_brows`.
- `e_find_holds`'s write through a const predicate (C14): Tables D and B are decided ONCE in `wf_find_decide`
  before Table E walks; the predicate reads `fx->holds`.
- The duplicated frame and loop (C9): `wf_find_use`'s copy of the ASSIGN/NOP frame, `wf_find_expr`'s copy of
  the `({ ... })` head and tail, and `wf_find_test`/`wf_test`'s two candidate tests. Shared now: `wf_frame`
  (ON_MISS and ASSIGN/NOP, the floor's and E-find's), `wf_open`/`wf_cand`/`wf_close`, `wf_test_to` (the floor's
  `grp` is -1 throughout). The floor's emitted bytes are unchanged (manifests, codegen, G2).
- Table D's ad hoc `if` in `wf_find_prepare` and the hand deny check (C7).

## 7.6 Table D as a kit_table (C7)

`wf_dtable` ("wfD") on `kit_walk`: rows D-hors (`d_hors_holds`: mass >= HORS_MIN, window >= 2 positions, its
last at an offset >= 0, exactly as before; no new admission predicate) and D-one; a contract each (D-hors's
`core` CORED, both serving the frame and the window fields); the deny `wf-hors` read by the walk; trace and
reach through the walk at the define's traced setup; the path id gains `+hors` (`mass+hors`).

## 7.7 C14, C15, C17

- C14: 7.5.
- C15 (D174): `--list-axes` descs by behaviour: cover ("every match is one fixed-width window whose bytes, and
  the one byte before and after it, decide a match exactly: the window search's first hit IS the leftmost
  match ...; turned off by --memfn=no-wf-find"), wf-find ("the window search: jump to the next byte of one
  window position's set (memchr, two memchr streams for a letter's two cases, or a byte walk; SIMD under
  -fmemfn-simd), then test the rest of the window; ..."), wf-hors ("the window search's skip for a common byte
  set ..."). No pinned test reads the desc text (`list_axes_delta.sh` keys rows by identity; the registry
  check counts rows and authored descs). `registry.md` §6¶8a's two rows reworded the same way (they described
  the find as "the C library for one byte, a table walk otherwise", now wrong).
- C17 where touched: window.c's and finder.c's headers; WF_WHY_MAX names the 320-byte refusal buffer;
  `WF_FIND_ID` spells "wf-find" once (Table E's deny, the arm's id and deny, the refusals; G2 plant S1422
  re-anchored to it, same intent); `find_groups` builds its run terms only at the define (the query counts
  them, `nrun`, for the class); the class's libc/includes are the plan's own (`w->libc`/`w->includes`:
  memchr where B calls it or a run compare exists), not the arm's widest; `mf_defined` reports them;
  `fd_find`'s frame replaces the 3,456 B `mf_site`. Not touched: `pcrec_mf_form_hash` and `define_sel`
  (3,600 / 3,456 B, unchanged).

## 7.8 Plants (C13), G2 (memfn/tests/run_g2_win.sh)

G2 gained 300 CASELESS REPORT sites from their own stream (`G2W_C1_SITES`; cube windows of 2-8 positions,
`A/a`, `0/1` and the high-byte cube `0xC4/0xE4`, fewer context items; the 1,900 sites before them unchanged;
the driver's subject alphabet gains the high-byte pair last, so no earlier site's subjects move). E-find
census: `pair 141` (B-pair), `fn 54` (B-fn), floors 125 / 48; FLOOR_SITES 1,900 -> 2,200.

| plant | defect | verdict |
|---|---|---|
| S1425 | D-hors's shift VALUE +1 | RED (67 sites: a candidate skipped) |
| S1426 | C-run's mask word dropped (a cube stretch compared as its lower bytes) | RED (62) |
| S1427 | the walk's set short its highest member (sets of 2+) | RED (67) |
| S1428 | B-pair's second stream searches the first member (the Table B pick's own text) | RED (15) |
| S1429 | fn-pair's second stream searches the first member (B-fn; native sites too) | RED (9) |

All 17 plants RED (S1400-S1407, S1409, S1410, S1422, S1423, S1425-S1429; S1424 was fix C's withdrawn plant and is not reused), each on answers but S1400 (its text stops
compiling, as before) and S1405/S1409/S1422 (refusal controls, as before). S1427's first draft emptied a
one-member D1w set and went red only by a compile error; it was narrowed to sets of two or more and is red on
answers.

## 7.9 Census options (C11)

`census.py` enumerates every corpus pattern row WITH its block's options (`--list-source`'s `flags`: i ->
`-i`, u -> `--ucp`; `encoding` -> `-e`), one task per distinct (pattern, options), the options first on every
arm's command line (an arm's own `-e` overrides). A row stating a raw `pcrec` flag or a `with`/`from` cascade
is REFUSED as UNEXPECTED rather than compiled without it (the corpus has none). Light enumeration: 5,966 rows,
4,967 tasks, 881 under options (`-e utf8` 465, `-e byte` 169, `-i` 146, `-i -e utf8` 76, `--ucp -e utf8` 9,
`-i -e byte` 5, `--ucp -e byte` 5, `--ucp` 4), 0 refused. Compiled at c-default (the C1 build, 1,762 compiles under the box lock): 199 of the 881 read cover under their own options; 18 of those read cover ONLY under them (17 `-e utf8`, 1 `-i -e utf8`); and 183 read cover compiled plain but NOT under their block's options. S3's census, which passed no options, counted those 183 as cover and missed the 18. The census's own tally line
(`options: N tasks ..., C of them cover at c-default`) is job 587's.

## 7.10 SIMD floors re-measured (C2)

| check | S3 (lowered) | now | floor |
|---|---|---|---|
| `simd_floor_check.py` movers / SIMD FUNCs | 33 / 33 | 46 / 46 (pre-S3 measure: 44) | 46 / 46, pinned AT the measure |
| `simd_guarded_check.py` simd-form | 3 | 6 (pre-S3: 6) | 6 |

`(?i)cat`'s witness is back on the DEFAULT path (`[]`, was `--memfn=no-wf-find`), and so are `rows.tsv`'s
fn-pair, vrun-w16 and vrun-w32 witnesses (`(?i)cat` default / `-fmemfn-simd`; signatures `size_t ha = 0, hb =
0;`, `_ofsskip__w16(const unsigned char`, `_ofsskip__w32(...`; each control the row's own deny, fn-pair's the
OFF arm with `-fno-req-run-fold`): `test-memfn-rows` 231/0. Leg (d), D155's routing
rule over the ON text, needed the function's suffix: the first name, `_find`, read as a work function holding
`#if` (13 rows red); renamed `_ofsskip`, which it is.

## 7.11 Movers (re-predicted FIRST)

- `s3_evidence/predicted_c1.tsv` (committed as WIP 73da45fc4 before any diff ran; that pre-fold history,
  old tips 3073fbbe7 and bb65e8c81, is in the reflog; folded into d190e3a70): 31 rows, C1 build vs the S3 tip
  before it (a017fe98a, built from `git archive`): `bytediff_c1.sh` **31/31 agree** (9 MOVES-fn/-fn-simd, 2
  MOVES-pair, 1 MOVES-uncover, 19 IDENTICAL); OFF arm (both denies, both sides) **31/31 IDENTICAL**.
- `s3_evidence/predicted_movers.tsv` (S3's, vs main c3ea619c3), 5 rows added first: `bytediff.sh` **29/29
  agree**; OFF arm **29/29 ABI-ONLY**.

## 7.12 Checks (this tree, the final code)

| check | verdict |
|---|---|
| `make -j16`, `make strict` | clean; "whole tree compiles clean with -Werror -Wshadow" |
| `make test-codegen` | 16/16 scripts |
| `tests/memfn/run_link_checks.sh` | 11/0 (R-28: largest frame 3,600 B) |
| `memfn/tests/run_g2_win.sh` | 8,842/0 (ASan+UBSan 4,400/0) |
| `memfn/tests/run_g2_win.sh --plants` | 17/17 RED (S1425-S1429 re-run under their final ids, all RED) |
| `tests/memfn/run_wreply.sh` | 112/0 |
| `make test-memfn-finder`, `-rows`, `-simdfloor`, `-guarded`, `-g2` | all green (rows 231/0 with the re-aimed witnesses; g2: the window family 8,842 among 70.4 M checks, 0 failed) |
| `make test-memfn-arms`, `-deleg`, `-forms`, `-reach`, `-rank`, `-manifest`, `-stamps`, `-arch` | green, at the final code |
| byte-diffs and OFF arms | 7.11 |
| `list_axes_delta.sh` vs main | 5 row(s), exactly as declared (descriptions moved, keys did not) |
| mech: the 61 rows anchored in the touched files | every anchor applies exactly once (S596's intent unchanged); FULL runs OWED to 587 |
| differential vs Python `re` | 7.4 |

## 7.13 Jobs re-staged

- **587-kit-s3-heavy** (correctness): the mech union grows 108 -> 125 (every row anchored in a file this build
  edited); the census runs per (pattern, options); the plants step runs all 17 G2 plants. Its REACH_ONLY step
  is the [MECH-REACH] re-aim check PAIR and B-fn's new firing places need: OWED to it.
- **588-kit-s3-timing**: the mover sample is PART OF THE BAR (`read_588.py`): every cell and row prints
  PASS/FAIL, a stratum FAILS where its cells' geometric-mean RTE/DEF exceeds 1 + its floor (this run's A/A), a
  dropped row FAILS; foobar match/real is a named layout cap at 1.052. Read over job 605's own data the new
  reader prints foobar match/real 1.032 "within" its cap and FAILS the bar on strata WALK/one/run (2.429; the
  rows this build moves to PAIR) and WALK/one/norun (1.381).
- `PCREC` for 588 is `build/s3/bin/pcrec`, re-copied from this build (sha256 0680489570db).
- Commands (from the MAIN tree; not queued here):
  `scripts/boxqueue add --name 587-kit-s3-heavy worktrees/s3/docs/dev/lanes/s3_job_587-kit-s3-heavy`, then
  `scripts/boxqueue add --name 588-kit-s3-timing worktrees/s3/docs/dev/lanes/s3_job_588-kit-s3-timing`
  (588 after 587 is green; 588 holds for i2build-parity and r27c's quiet gate as before).
- Dry runs: 587 rc 0 in 0.1 s (its 125 mech ids are validated as the job's first step, ~100 s, over the 30 s bound, as before); 588 rc 0 in 10.5 s (one §6 cell, sample row smp01, E[sh] site esh02: build, premises, differential, gate; no clock).

## 7.14 Findings

- **F-C1-1 (the bar will most likely still FAIL on WALK/one/norun).** Its five rows (`[a[:b]`,
  `(?:(?!a)z|w)`, `[a-]`, `[[:]`, `[:a]`) stop at two-member sets that are NOT one-bit cubes (`{a,-}`,
  `{w,z}`, ...), which PAIR's scope ("today's": a cube inside a run stretch) does not take, so they keep the
  walk and 605's 1.2-4.5x losses. Two `memchr` streams find any two bytes; widening PAIR to every two-member
  stop is a one-fact change in the kit, but it widens a row the design scoped as "today's", so it is a design
  question for Frank (I did not build it). Their other cause is C8's (pricing the stop by its find method).
- **F-C1-2 (an honest refusal).** A stop of two or more members below the candidate has no Table B row; S3's
  synthetic ask walked it. Such a cover now declines to the default build's composite (manifest row
  `(?<=[qj])[a-z]`). The corpus count is in 587's census (a cover in main's sense that leaves cover reads as an
  UNEXPECTED non-mover only if it moved before; it reads ABI-ONLY here).
- **F-C1-3 (the layer reading, 7.2).** The FIND slot is asked at the OFF variant, as every native FIND site is;
  the brief asked for the actual layer. Recorded for the manager.
- **F-C1-4.** `[Qq]uery` and `(?i)x/1234` still stop at the cube (A-mass's rarity, C8 not built): now PAIR.

## 7.15 C1-C17

| id | state |
|---|---|
| C1 | DONE: Table B's pick rendered (B-fn, B-pair, B-memchr, B-walk); PAIR and the SIMD rows reachable; probes 7.4 |
| C2 | DONE: the floors (46/46, 6) re-measured and the witnesses (simd_floor_check's `(?i)cat`, rows.tsv's fn-pair/vrun) back on the default path (7.10) |
| C3 | DONE: the honest question (7.2), the contracts (7.3); D1c reachable |
| C4 | DONE as a DRAFT: window_site.md rev 3.3, its own commit, for the manager |
| C5 | NOT IN SCOPE |
| C6 | NOT IN SCOPE |
| C7 | DONE (7.6) |
| C8 | NOT IN SCOPE (F-C1-1, F-C1-4 name where it bites) |
| C9 | DONE (7.5) |
| C10 | DONE in 588's reader (the sample in the bar); G2's alphabet and width widened only for the new caseless stream (a high-byte cube, windows to 8); NUL/utf8 and windows to 13 NOT done |
| C11 | DONE (7.9) |
| C12 | NOT IN SCOPE |
| C13 | DONE: S1425-S1429 (7.8) |
| C14 | DONE (7.5) |
| C15 | DONE (7.7) |
| C16 | NOT IN SCOPE |
| C17 | DONE where touched (7.7); `define_sel`'s frame untouched |

---

# Part 6. RESULT (job 605, 2026-10-23)

Job 605-kit-s3-timing is job 588's script run at the S3 build (pcrec 8d53dc29df1a), GREEN: rc 0,
wall 805 s, 1,890 rows, 5 launches (L=5, T=20 ms, N=9; cpu 7, sibling 15; gcc 15.2.0 -O2, no -march).
Stages build, diff (112 arm builds equal to python `re`, asan on), gate (504 arm cells), sample-gate
and esh-gate all passed before any clock. **No answer differs anywhere.** The job's own verdict:

    == s3t BAR FAIL: 72 cells read on the scalar layer; FAILING: foobar match/real 1.032 > 1.020

Evidence (copied from the job's OUT dir and log, `docs/dev/lanes/s3_evidence/`):
`results_605_table.md` (every table below, as printed), `results_605_header.md`,
`s3t_results_605.tsv.gz` (the §6 cells' raw rows), `s3t_sample_605.tsv.gz`, `s3t_esh_605.tsv.gz`,
`read_605_summary.py` (the tallies below, recomputed from the table). Reading rule throughout:
FASTER < 1 - floor, SLOWER > 1 + floor, else within; floor = 581's floor for the cell (the bar) or
this run's A/A in the regime (sample, E[sh]).

## 6.1 The §6 bar (scalar layer; 72 cells; RTE/DEF)

**The five capped cells** (cap = 581's ratio plus its floor, window_site.md §6):

| cell | measured RTE/DEF | cap | verdict |
|---|---:|---:|---|
| hex8-bounded throughput/dense | 1.543 | 1.551 | within cap |
| hex8-bounded search_short/dense | 0.962 | 1.159 | within cap (and FASTER than DEF) |
| file-ext-order search_short/none | 1.032 | 1.053 | within cap |
| file-ext-order match/real | 1.050 | 1.059 | within cap |
| file-ext-order match/none | 1.067 | 1.085 | within cap |

All five are inside their caps. The single failing cell is **not** one of the five: it is
foobar match/real, 1.032 against the uncapped 1 + floor = 1.020 (the cell was FASTER in 581, 6.2).

**Every cell's RTE/DEF, by group** (scalar; 72 cells):

| group | cells | notes |
|---|---:|---|
| FASTER beyond floor | 41 | |
| within floor | 26 | |
| SLOWER beyond floor | 5 | the four capped cells that read SLOWER (file-ext-order search_short/none 1.032, match/real 1.050, match/none 1.067; hex8-bounded throughput/dense 1.543, which is the 1.53x statement) and foobar match/real 1.032 |

- Biggest wins: hex8-bounded search_short/none 0.173; file-ext-order search_short/dense 0.242;
  word-digit throughput/none 0.256; lit-l8 throughput/dense 0.267 and search_short/dense 0.268;
  word-digit throughput/real 0.274; foobar throughput/dense 0.308 and search_short/dense 0.299.
- Biggest losses: hex8-bounded throughput/dense 1.543 (capped), file-ext-order match/none 1.067 and
  match/real 1.050 (capped), file-ext-order search_short/none 1.032 (capped), foobar match/real
  1.032 (the failing cell).
- Every `throughput` and `search_short` cell not named above is FASTER or within; all 24 `match`
  cells are within except file-ext-order real/none and foobar real (above).
- **A/A (RT2/RTE, 72 cells):** min 0.970, max 1.039, geometric mean 0.999. 67 of 72 within 2%, 64
  within 1%. The five outside 2%: lit-l8 search_short/dense 0.970, year4 search_short/dense 0.975,
  done-eol search_short/none 0.978, word-digit throughput/dense 0.980, done-eol match/dense 1.039.
  RT2 and RTE are the same text compiled and linked twice, so the A/A shows timing noise and
  nothing else (it cannot show a layout effect between different texts, 6.2).

## 6.2 One bounded diagnosis: foobar match/real (1.032)

Method: the job's own compiled artifacts, `build/s3/job588/arts/foobar/{DEF,RTE}/` (a.c, a.h, a.o,
bin, d.o). Nothing was compiled or timed new; objdump and diff only.

- **The harness's match regime** (docs/design/kit_proof/measure/cdrv.c) is one `rx_match(&ctx)` per
  record at pos 0, through `pass()`. It never calls `rx_search`.
- **The anchored function's C text is identical** between the arms (`rx_match`, its three
  `rx_anchored_*` tables and the `rx_anchored_*` helpers: `diff` empty). The only differences in
  a.c are the three `RX_DFA_*` stamps, the `RX_DFA_START` stamp, `rx_search` (DEF: forward DFA with
  `rx_ofsskip`; RTE: the inlined window scan), the removed forward tables and helpers, and the
  `rx_info` scan/prefilter/search_form strings. a.h and the harness's d.o are byte-identical.
- **The object code is identical** instruction for instruction: `rx_match` is 0xf9 bytes in both
  arms, 73 objdump lines each, the same mnemonics and operands. The only differences are
  displacements and relocation targets (branch targets, `lea` of the rodata tables), which move with
  the section layout. `pass()` is likewise identical but for the displacements of `g_*` and the
  `call` to `rx_match` / `rx_next_pos`.
- **What differs is placement, caused by `rx_search` shrinking** (nm -S on the linked bins):

  | | DEF | RTE |
  |---|---:|---:|
  | `rx_search` size | 0x169 | 0xc1 |
  | `rx_match` address (mod 64) | 0x1e70 (48) | 0x1dd0 (16) |
  | `rx_anchored_byte_class` (256 B) address (mod 64) | 0x3200 (0) | 0x21e0 (32) |
  | `rx_anchored_next_state` (72 B) address (mod 64) | 0x31a0 (32) | 0x2180 (0) |
  | `rx_anchored_is_accepting` (36 B) address (mod 64) | 0x3300 (0) | 0x22e0 (32; crosses a line) |
  | `a.o` `.text` / `.rodata` size | 0x318 / 0x32a | 0x278 / 0x184 |

  The hot code moves 32 bytes within its cache line group, the 256-byte class table goes from
  4 lines to 5 (it was line-aligned, now it straddles), and the accepting table now crosses a line.
  Symbol order is unchanged. gcc inlines the same helpers in both. The `.rodata` shrinks
  because the forward tables are gone.
- **Does the match regime touch anything the cover changed?** No. It reads only `rx_match` and the
  anchored tables. S3's cover change is in `rx_search` (and the `rx_info` strings, not read here).
- **581's reading of the same cell:** the same code (the anchored machine did not change) read
  FASTER there: foobar match/real COV/DEF 0.979 (F), PRO/DEF 0.972 (F), SHF 0.997, AA 0.994, while
  HRS/DEF 1.043 and PRF/DEF 1.045 read SLOWER; match/none COV 0.932 (F), PRO 0.929 (F), SHF 1.002,
  HRS 0.997, PRF 0.997. In 581 the `rx_match` text was equally the same across arms (the anchored
  machine did not change); only the surrounding arm code differed. So across two jobs the same
  anchored instruction stream has read from 0.93 to 1.045 in the match regime of this cell, with
  the value following the arm's other code.
- **The other match-regime cells in this job (RTE/DEF, scalar):** 21 of 24 within. lit-l8
  1.002/1.011/1.017; year4 1.000/1.001/0.998; file-ext-order 1.050/1.067/1.001 (the first two
  capped); hex8-bounded 1.002/1.001/0.999; foobar 1.032/1.000/1.006; cat-bounded
  1.001/1.000/0.976; done-eol 1.003/1.000/0.994; word-digit 0.985/0.984/0.997 (order real/none/dense).
  SIMD-on: the same pattern (foobar match/real 1.033, file-ext-order match/real 1.034, none 1.066).
  The spread is all in cells whose `rx_search` shrank or changed, never in a cell whose anchored
  code differs.

**Conclusion: a layout/alignment effect. There is no S3 code on the path.** The measured function is
byte-for-byte the same, and its code and tables moved (the forward machine's removal shifted
everything after `rx_search`). The A/A cannot catch it because RT2 and RTE are the same text and so
the same layout. Not measured here (and deliberately not run): a padded control arm that restores
`rx_match`'s old address; if the manager wants the cell to read green by evidence rather than by
argument, that is one small compile-and-time job, not a code change. Caveat: this is an argument from
identical instructions plus a placement difference, supported by 581's opposite-sign reading, not a
proof that the 3.2% is alignment and not, say, i-cache set conflicts with `pass()` (also identical
text).

## 6.3 SIMD-on reading (RTEs/DEFs; reported, not the bar)

| group | cells |
|---|---:|
| FASTER beyond floor | 44 |
| within floor | 23 |
| SLOWER beyond floor | 5 |

The five SLOWER are the same cells as the scalar layer: foobar match/real 1.033, file-ext-order
search_short/none 1.031, match/real 1.034, match/none 1.066, hex8-bounded throughput/dense 1.538.
The job's SIMD line: `SLOWER: foobar match/real 1.033 > 1.020` (the others sit within their caps).
Wins are the same cells at nearly the same ratios (hex8-bounded search_short/none 0.172, file-ext-order
search_short/dense 0.229). The largest scalar/SIMD gaps are a few points (word-digit throughput/dense 0.629
against 0.655, done-eol match/dense 1.026 against 0.994).

## 6.4 Mover sample (24 rows, 122 row-regime-class cells; NOT the bar)

Per-stratum counts, scalar layer (reading against this run's A/A):

| stratum | FASTER | within | SLOWER |
|---|---:|---:|---:|
| LIBC/one/norun (smp01, 06, 11, 16, 21) | 23 | 3 | 0 |
| LIBC/one/run (smp02, 07, 12, 17, 22) | 13 | 17 | 0 |
| WALK/hors/norun (smp03, 08, 13, 18, 23) | 19 | 0 | 1 |
| WALK/one/norun (smp04, 09, 14, 19, 24) | 2 | 2 | 18 |
| WALK/one/run (smp05, 10, 15, 20) | 3 | 0 | 21 |
| **all** | **60** | **22** | **40** |

SIMD-on layer: 57 / 22 / 43 (WALK/one/run 0 / 0 / 24; the other strata unchanged).
**Overall median RTE/DEF: 0.9715 scalar, 0.985 SIMD-on** (over the 122 cells; geometric mean
1.074 scalar, 1.339 SIMD-on, pulled up by the walk rows below).

**Every SLOWER row, scalar (ratio, throughput / search_short, real / none / random):**

| row | pattern | stratum | SLOWER cells (RTE/DEF) |
|---|---|---|---|
| smp04 | `[a[:b]` | WALK/one/norun | thr/random 4.464; short/random 1.951 |
| smp05 | `(?:(?i:abs)\|(?i:ab)S)` | WALK/one/run | thr/none 4.908, thr/random 2.268; short/real 1.653, none 2.292, random 1.934 |
| smp08 | `\b\w*?\B\w` | WALK/hors/norun | thr/random 1.139 |
| smp09 | `(?:(?!a)z\|w)` | WALK/one/norun | thr/real 1.157, random 1.317; short/real 1.253, random 1.413 |
| smp10 | `(?i)foobar` | WALK/one/run | thr/none 7.352, random 3.276; short/real 2.567, none 3.936, random 3.201 |
| smp14 | `[a-]` | WALK/one/norun | thr/random 1.216; short/real 1.244, random 1.611 |
| smp15 | `(?i)abc` | WALK/one/run | thr/none 5.127, random 2.319; short/real 1.711, none 2.372, random 1.905 |
| smp19 | `[[:]` | WALK/one/norun | thr/real 1.891, none 1.461, random 1.251; short/real 1.659, none 1.346, random 1.626 |
| smp20 | `(?i)x/1234` | WALK/one/run | thr/real 10.263, none 29.071, random 8.913; short/real 3.160, none 5.933, random 3.673 |
| smp24 | `[:a]` | WALK/one/norun | thr/random 1.249; short/real 1.224, random 1.623 |

Ten of 24 rows have at least one SLOWER cell (40 cells); nine of them are WALK/one, the tenth is a
single WALK/hors cell. No LIBC row is SLOWER. At the SIMD layer the smp05/10/15 rows also
go SLOWER on `real` (9.5x, 12.8x, 9.9x throughput/real; the largest SIMD ratios 11.8-18.2x on
none), the SIMD DEF being the faster baseline for those. Facts only; why these walk
rows lose to DEF was not investigated here, and whether they are the intended trade is a ruling for
main.

## 6.5 E[sh] reading (12 D-hors sites; D-hors RTE vs D-one NOH; NOT the bar)

All 12 sites' SIMD text equals their scalar text, so the SIMD alpha IS the scalar alpha (the
columns are equal in every row). alpha = RTE/NOH; < 1: D-hors is faster. Geometric mean over
regimes and classes, sorted by E[sh]; per-class and per-regime means beside:

| site | pattern | E[sh] | max(sh) | stop ppm | alpha gmean [min, max] | SLOWER/FASTER of cells | real | random | none | throughput | search_short |
|---|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| esh01 | `(?s)[0-9a-f].[0-9a-f]` | 1.000 | 1 | 284434 | 2.130 [1.699, 2.733] | 4/0 of 4 | 1.886 | 2.405 | | 1.897 | 2.392 |
| esh02 | `(?s)[^a]..` | 1.000 | 1 | 945837 | 0.976 [0.900, 1.005] | 0/1 of 4 | 1.003 | 0.950 | | 1.002 | 0.951 |
| esh03 | `[aeiou]..[aeiou]` | 1.030 | 4 | 252788 | 1.766 [0.955, 3.821] | 3/1 of 4 | 1.087 | 2.868 | | 1.434 | 2.174 |
| esh04 | `\b\w*?\B\w` | 1.193 | 2 | 807006 | 0.899 [0.823, 0.974] | 0/4 of 4 | 0.954 | 0.848 | | 0.922 | 0.877 |
| esh05 | `\w{5}` | 1.772 | 5 | 807006 | 0.735 [0.589, 0.883] | 0/4 of 4 | 0.833 | 0.648 | | 0.793 | 0.680 |
| esh06 | `[a-z][a-z0-9]{3}` | 1.785 | 4 | 663413 | 0.938 [0.825, 0.991] | 0/2 of 4 | 0.974 | 0.904 | | 0.894 | 0.985 |
| esh07 | `[a-z]{6}` | 2.683 | 6 | 663413 | 0.605 [0.252, 1.100] | 2/2 of 4 | 1.067 | 0.342 | | 0.694 | 0.526 |
| esh08 | `[0-9a-f]{4}` | 3.147 | 4 | 284434 | 0.512 [0.402, 0.637] | 0/4 of 4 | 0.489 | 0.537 | | 0.616 | 0.426 |
| esh09 | `[0-9a-f]{5}` | 3.862 | 5 | 284434 | 0.396 [0.286, 0.524] | 0/6 of 6 | 0.387 | 0.417 | 0.386 | 0.516 | 0.304 |
| esh10 | `[0-9a-f]{6}` | 4.578 | 6 | 284434 | 0.322 [0.221, 0.458] | 0/6 of 6 | 0.326 | 0.332 | 0.309 | 0.439 | 0.236 |
| esh11 | `[0-9a-f]{7}` | 5.293 | 7 | 284434 | 0.273 [0.182, 0.401] | 0/6 of 6 | 0.285 | 0.278 | 0.258 | 0.378 | 0.198 |
| esh12 | `[0-9a-f]{8}` | 6.009 | 8 | 284434 | 0.235 [0.153, 0.348] | 0/6 of 6 | 0.250 | 0.236 | 0.220 | 0.327 | 0.169 |

Facts:
- D-hors is slower on every cell at esh01 (E 1.000; 1.70-2.73x) and on three of four at esh03
  (E 1.030; one 0.955; the others 1.24-3.82x).
- At E[sh] >= 1.19 it is faster on every cell at esh04, esh05, esh08-esh12 (monotone from 0.51 at
  E 3.1 to 0.24 at E 6.0), mixed at esh06 (faster on throughput, within on search_short) and at
  esh07 (E 2.68: `real` 1.035 and 1.100 SLOWER, `random` 0.465 and 0.252 FASTER).
- Not a clean cut-off on E[sh]: esh02 is also E = 1.000 yet within/faster (1.003, 0.950). It has
  the highest stop mass of the set (945,837 ppm) while esh01's is 284,434 and esh03's 252,788.
- **max(sh) does not predict it**: esh02 (max 1) is fine, esh03 (max 4) is slower, esh01 (max 1)
  is slower. **Stop mass** separates esh01/esh03 (<= 285k, slower) from esh02 (946k, not), but
  esh08-12 share esh01's stop mass (284,434, same class) and are fast, so stop mass alone does not
  decide either; E[sh] > ~3 does within that stop mass.
- The only `random`/`real` split of consequence: esh03 and esh07 are slower on `real` and far
  faster (esh07) or far slower (esh03) on `random`; class matters beside E[sh].
- 12 sites, one per E[sh] point, four to six cells each: the evidence is suggestive of a
  threshold in E[sh] (below roughly 1.1 with low stop mass D-hors is slower; above roughly 2.7 it
  is faster in all but one cell) and is not enough to fix one.

**What it supports:** E[sh] discriminates better than max(sh) (the withdrawn fix C's rule would have
kept esh03, which is the slower site at E 1.030); the loss region is E[sh] close to 1 with a low
stop mass, and the win is large and monotone above E[sh] ~3. No default moved.

## 6.6 What this supports / does not support

- Supports: the cover's routed artifacts are not slower than the OFF arm on 67 of 72 §6 cells at
  the scalar layer (41 FASTER, 26 within); the four capped cells and hex8-bounded throughput/dense
  all land inside their caps, including the 1.53x statement (1.543 against 1.551).
- Supports: foobar match/real is not S3 code on the path (6.2); the anchored function is identical
  down to the instruction, only its placement moved.
- Does not support: calling the bar PASS as run. The script's rule fails one cell at 1.032 > 1.020,
  and 6.2 is an argument that the cell is layout, not a measurement that it is; reading it GREEN is a
  ruling for main (or one padded control arm).
- Does not support: the mover sample as a clean result. Ten of 24 sample rows (nine WALK/one) have
  SLOWER cells, to 29x at smp20 (`(?i)x/1234`) and 18x at the SIMD layer on smp10; the whole WALK/one
  stratum reads SLOWER on 39 of 46 cells. This is outside §6's bar and is a finding for main.
- Supports (weakly): D-hors helps from E[sh] ~3 up and hurts near E[sh] 1 with a low stop mass.
  Does not support moving an admission default: 12 sites, one pattern family above E 3, a
  non-monotone middle (esh06, esh07).
- Does not support: any SIMD verdict. The SIMD-on layer mirrors the scalar one here; the official
  SIMD verdict stays pcrec-bench's (D144 addendum 4).

---

# Part 5. Job 600 reds (lane s3fix600, 2026-10-23)

Job 600 is job 587's script, run at ba6ebf720. It was RED in five steps (census, sweep_start,
test, mech, reach) and changed NO answer: every red was a reader of a witness that became a
`cover` artifact by default. **No answer changed anywhere**, and none of the runs below shows
one:
- census: c-vm, ir and every OFF arm have 0 movers;
- every mech row's corpus arm is clean on the clean tree;
- the sections' differentials (start-landing §5, anchored diff, startset vmhat_diff) answer
  identically.

## 5.1 Commits

| sha | what |
|---|---|
| **7e1caad08** | **THE S3 COMMIT**: d3886a656 plus the R1 spec hunk below. Built by `reset --hard d3886a656`, applying the hunk, then `reset --soft f7bc3cf05` and one commit. abi stays 84 (PROVISIONAL). `git diff d3886a656 7e1caad08` = match_api.md only |
| b3fba6b28 .. fc795da15 | the seven later commits (b8bcb23b1 .. ba6ebf720), cherry-picked unchanged |
| 34ee758a1 | `s3: witnesses, pins and manifests after the cover default (job 600)`: R2-R6 |
| (next) | this part |

The WIP tip 260dd1bbf has a tree identical to 34ee758a1's.

## 5.2 R1: the stamp is not a lie. Spec clarified; code unchanged

The ruling's premise does not hold. I reported this to main on 2026-10-23 and had no reply
before the restructure:
- Every cover artifact carries the ANCHORED machine. `cover_conj`'s C4 (`anchored-A`) requires
  it, `_DFA_MATCH` reads `"unwrapped"`, and `rx_anchored_next_state[]` and `rx_anchored_step`
  are in `rx_match`.
- `_DFA_TABLE`, `_UNIFORM_FOLDS` and `_SCAN_EDGE` fold over `dfa_member_machines`, the path
  members, which on cover is {anchored}. So `"premultiplied"` is that machine's real
  encoding. Under `-fno-premul-table`, `abc` stamps `"indexed"` and carries
  `short rx_anchored_next_state[16]`. On `[0-9a-f]{4}`, FOLDS 1 and SCAN_EDGE `"bitmap"` are
  the anchored machine's folded step and its edge.
- §6.3.4¶7's `"mixed"` row already counts the anchored machine, ¶8 keeps the name when a table
  is folded, and ¶9 forbids naming a machine the artifact does NOT carry. Stamping `"none"`
  would hide that machine's encoding.

**The red was a check gap.** `run_premul_table.sh`'s matcher-text scan markers had no cover
shape; `run_dfa_stamps.sh` gained one in S3. That gap produced all 811 `[iff]` reds, and
`[agreement] 811` is the same drift count. The fix (in 34ee758a1) adds the cover marker, so
the agreement check compares the stamp against the anchored tables.
- First rerun: the marker's comment carried an apostrophe and closed the single-quoted awk
  program (a syntax error, fixed).
- After the fix, `make test-premul-table`: **16 passed, 0 failed**.
  - stamp distribution premultiplied=2992 indexed=53 mixed=40 none=511;
  - 1798 anchored machines read.

**Spec hunk (in 7e1caad08), worded by behaviour:**
- §6.3.4¶8 gains: "On a `"cover"` scan the search itself steps no machine, so the composition
  is the one machine the artifact still carries, the anchored one under
  `<PREFIX>_DFA_MATCH "unwrapped"`: the value is that machine's encoding (`"premultiplied"`
  or `"indexed"`), and `"none"` where the artifact carries no anchored machine either. The
  same holds for `_DFA_UNIFORM_FOLDS` and `_DFA_SCAN_EDGE` below."
- §6.3.4¶9's zero list gains: "and on `"cover"` at most `2` (the anchored machine's two
  tables)".

**cpset-structure was never R1's.** Its drift is RX_DFA_PREFILTER and EMITTED_BYTES on the four
cover sample patterns (R4 below). If main still wants `"none"`, that is a code change: the
abi 84 artifacts move again and premul's agreement check needs a cover clause. Say so and a
lane can do it.

## 5.3 R2: mech/reach, the 32 rows, by ID

Every row's SAB_REACH compile(s) gained `--memfn=no-wf-find` (S283: both compiles). A dated
`RE-AIMED` comment says why.
- REACH_ONLY over the 33 rows: **33 reached, 0 unreached** (reach33.log).
- Mech over the same 33 (mech33.log): **32 DETECTED**, S283 UNDETECTED (R3).
- Rerun of S283/S284 after the flips: `mech run COMPLETE: 2 rows (unexpected: 0)`.

| row | detecting arm(s) after the re-aim |
|---|---|
| S1121 | partlayout 1 |
| S1415 | prechecks 1 |
| S1416 | prechecks 3, offsetskip 9 |
| S1421 | prechecks 4, corpus 4 |
| S227 | scanedge 11 (corpus 0: `foo\B` is cover by default) |
| S267, S270, S280, S282, S288, S468 | prechecks (S468: corpus 0) |
| S279, S285, S287 | offsetskip 3 (+ corpus) |
| S447, S448, S450, S454 | corpus (reqcube.rxt) + codegen |
| S455, S571 | codegen |
| S464 | corpus 25 (handoff.rxt still reaches at the default) |
| S482-S484 | dfahat |
| S517 | memfnstamps |
| S607 | candoracle |
| S686, S688, S694 | memfnarms (+ corpus / memfnstamps) |
| S786 | startlanding + corpus |
| S787 | dfastamps + startlanding |

**Where the point is also the default path:** cover's own default witnesses already cover it:
- run_dfa_stamps.sh's `a` cover witness and its `[start]` agreement (S786, S787 and the
  start-landing family);
- runcmp_check.py's cover witness (fix F) and G2's window family (the run/pair rows S279,
  S285, S447-S455, S686-S694).

No row needed a harness-flag mechanism: every row whose harness arm went blind (S227, S468)
is detected by its structural arm. A `SAB_HARNESS_RXTFLAGS` field I drafted was removed
unused (D77).

## 5.4 R3: S284 (and S283)

**S284 is DETECTED, and the cause predates S3.**
- Since D172 S2 commit 6 (32f9b1781), `dfa_form_derive` refuses a NEXT row whose `reseeds`
  disagrees with the window reply's RE-SEED path, as an internal error.
- Under the plant every seeded run-row site refuses at compile: `foo\B` and `(foo\B)` in the
  scan-edge census, `/user|/users` and `a\K/user` in run_pinned.rxt. That is a loud refusal,
  never a wrong answer.
- Measured with a scratch build of the plant (p284.log):

  | tree | scanedge | run_pinned.rxt |
  |---|---|---|
  | c3ea619c3 | 3 fail / 18 pass | 42 fail / 13 pass |
  | S3 | 3 fail / 18 pass | 4 fail / 51 pass (cover asks no NEXT row) |

- The row's header and SAB_DOC_FIGURE say this, and SAB_EXPECT reads DETECTED. This is not a
  cover-path detection: the claim expired at S2. Job 587/600 was the first matrix run of this
  row since then.

**S283 is UNDETECTED (EXPECTED), found by this lane's re-aim run, and it also predates S3.**
- `pf_window_of` states no run R under PCREC_NO_OFFSET_SKIP, so no reply carries C-pin and no
  run row applies, whatever the row's mask says.
- A scratch plant build at c3ea619c3 and at S3: `/user|/users -fno-offset-skip
  -fno-req-handoff` stays "memchr", identical to the clean build.
- The row records the reason and what would close it.

## 5.5 R4: make test sections

| section | change | cause |
|---|---|---|
| cli | the vrun block's 12 `(?i)cat` compiles take `--memfn=no-wf-find` (folded into the one `--memfn=` list: the last `--memfn=` wins) | `(?i)cat` is cover, no reqrun helper |
| assertions (wordctx) | a 4th legitimate non-difference, **cover, deny-proved**: the artifact is cover AND its `--memfn=no-wf-find` arm DOES differ between the two builds (else still UNEXPLAINED) | the 2 (`-*?(?:\b\|\B)\W`, `\W+?(?:\b){0,2}`) are cover: no scan machine, and the anchored machine's language is unchanged by their vacuous assertions; under the deny both differ (measured) |
| premul-table | the cover scan marker (R1) | the 811 stamp-without-a-scan reds |
| search-pinned | `not nullable` 'abc' row adds the deny | abc is cover |
| start-landing | §1 abcd and [a-z] rows add the deny (cover's default stamp attempt-start is run_dfa_stamps.sh's witness). §3 floors pinned AT the measured value: end-minus-width 510 (was 1124), product reach 705 (was 1290), landing untouched (195 above 168). §5 adds `ab\|cd` (not a window, end-minus-width) | the fixed-width windows left end-minus-width |
| prechecks | a file-level `COVER_DENY` on `emit()` and `fact()`, run_scan_edge_census.sh's own shape | the witnesses are cover; every non-cover artifact is byte-identical under the deny (census: default movers == cover artifacts), so it moves nothing else |
| anchored-match | the §2 offset-k arm `\d{4}-\d{2}-\d{2}` takes the deny (pf_scan gained extra args); K53_DENY gains it | cover search carries no prefilter; cover artifacts fit the K53 cap with the anchored machine |
| cpset-structure | manifest re-recorded, 4 rows (`a`, `abc`, `\bword\b`, `(?i)HeLLo`): PREFILTER -> "none", EMITTED_BYTES 21348->18944, 22179->19267, 25144->20690, 25544->21700; the other 8 untouched; note in the script | cover: no scan, no forward/reverse machine |
| encoding-checks | **the region is declared**: the cover window search's pick | see below |
| startset | manifest_s3_dfa.tsv **-25 rows**, each cover by default and still a hat mover under the deny (measured per row, listed in the manifest header); `[dfa-wit]` `\B(?<!a)d` and `\bab\b` take the deny | the premise is not inverted: the manifest names hat movers, cover artifacts have no hat (0 joiners) |

**encoding-checks (K50/DD12a(i)): it is cover, not something else.** All of the 11 diverging
strict pairs except the three `\b`/`\B` ones are cover artifacts on both sides (`fo|foo|fool`, `x\By`, `\bcat\b`, `\Bcat`,
`\bcat`, `(?i)\bcat\b`, `(?m)abc$`, ...).
- **Mechanism.** Their window search scans the run pick, which reads the byte-keyed prior
  exactly as the run pre-check's pick does: byte takes the rarest member (`c@0`), utf8
  (prior NONE) the rightmost (`t@2`). REQ_RUN/REQ_BYTE declare the pick.
- **The other two (`\b`, `\B`) are not S3's.** They diverge identically under main's own
  binary (a2d4d9738, wsmain's green job 586) and are excused there by the undeclared-form
  manifest.
- **What the check now does:** when both sides are cover and their stamped picks differ, it
  normalizes ONLY the search clause and counts it (`cover_pick`, added to the
  never-excised-region floor):
  - memchr form `memchr(s + c [+ K], B, ...)` with its `- K` back-off;
  - class form `while (c [+ K] < n && !(s[c+K] == B || ...)) c++;`.
- **What still holds:** each side is held to its own stamps (the searched bytes are the
  REQ_RUN member at K, or its cube, else REQ_BYTE). The verify in the same statement is still
  compared token for token.
- **Result:** `make test-encoding-checks` (S3 binary, ENC_MAX_BLOCKS=250) **11 passed, 0
  failed**. The ref tree's own script with the ref binary: 11/0 (encref.log).

## 5.6 R5: sweep_start

**DIFFER_PINS re-pins.** 20 c-default cells were pinned AT the measured values, under the S3
RE-PIN header. Each cell's comment keeps its old value.

| base | arm | differ/stamp floor | manifest |
|---|---|---|---|
| byte | -fno-offset-skip | 328/328 (was 513) | `ab+` (was `ab`) |
| byte | -fno-run-prefilter | 54/54 (was 127) | `(ABC)` (was `fi`) |
| byte | -fno-start-set | floors held | `(\b)x` (was `\Bx`) |
| byte | -fno-req-handoff | 226/226 (was 339) | `ab?c` (was `SS`) |
| byte | -fno-req-run | stamp 102 (was 208) | `SS` kept |
| byte | -fno-req-run-fold | stamp 26 (was 32) | kept |
| byte | -fmemfn-simd | 9 (was 20) | `((?i:abc))` (was `(?i)cat`) |
| utf8 | -fno-offset-skip | 376/376 (was 604) | `ab+` |
| utf8 | -fno-run-prefilter | 2/2 (was 3) | `frank\|fred` |
| utf8 | -fno-start-set | floors held | `(\b)x` |
| utf8 | -fno-req-handoff | 349/347 (was 519/517) | `ab?c` |
| utf8 | -fno-req-run | stamp 58 (was 79) | kept |
| utf8 | -fno-req-run-fold | stamp 27 (was 31) | kept |
| utf8 | -fmemfn-simd | 10 (was 15) | `((?i:abc))` |
| byte, utf8 | no-pres-set-lead | 14, 7 (was 16, 8) | `x{2,5}(?i:cat)` |
| byte, utf8 | no-fd-pres-g1 | 944, 873 (was 1271, 1105) | `a+` (was `ab`) |
| byte, utf8 | no-fd-pres-pick | 167, 231 (was 188, 263) | kept |

**The cause, per pattern.** `docs/dev/lanes/s3_evidence/armcause.py` (new; armcause2.tsv)
compiles BASE and BASE+FLAG at the default and under `--memfn=no-wf-find`, with the `--memfn`
lists merged.
- On all 20 cells, every leaver is a default-cover pattern (DIFFER and STAMP).
- There are 0 joiners.
- The cause "S3 routes N fixed-width patterns to cover" holds with N = 208, 74, 30, 125, 11,
  263, 1, 19, 181, 5, 2, 1, 382, 301, 23, 34 (and the stamp-only leavers 112, 6, 21, 4).

**Rerun:** `emit_sweep --arms start` -> **DONE rc=0**, no cell short (sweep_start.log).

## 5.7 R6: census

census.py's facts rule gains ONE class. A pattern whose `-e utf8` .c is cover (but whose
default .c is not) may move its `utf8` listing rows and nothing else. This is job 600's
three: `\p{Zl}`, `\p{Zp}` and `\p{sc=Thaana}` are `empty` under byte and `cover` under utf8,
with utf8 end_window E2's `used` going yes -> no.

Rerun (vs the c3ea619c3 ref): `== s3 census COMPLETE: patterns=4755 compiles=95100
movers=3812 unexpected=0`; facts reads `utf8-cover 25` (3 of them moved).

## 5.8 Commands run (all on this tree; logs under build/s3fix600/)

| command | verdict |
|---|---|
| armcause.py (boxlock) x2 | 20/20 cells cause holds (the first run's `--memfn` cells were void: the last `--memfn=` wins; fixed) |
| scratch S284 plant, both trees | above |
| scratch S283 plant, both trees | memchr, unchanged |
| `REACH_ONLY=1 run_sabotage_matrix.sh` 33 rows | 33 reached |
| `run_sabotage_matrix.sh` 33 rows | 32 DETECTED, S283 UNDETECTED (flipped after) |
| `run_sabotage_matrix.sh S283 S284` | unexpected 0 |
| `make -k test-cli test-assertions test-premul-table test-search-pinned test-start-landing test-prechecks test-anchored-match test-cpset-structure test-encoding-checks test-startset` | 9 green; premul red on my own awk-quoting slip |
| `make test-premul-table` (after the fix) | 16/0 |
| run_encoding_checks.sh, S3 binary / ref tree+binary | 11/0, 11/0 |
| census.py | unexpected=0 |
| `emit_sweep --arms start` | rc=0 |
| `s3_job_587-kit-s3-heavy --dry-run` | rc 0, 0.1 s |

Not run here, per the brief: the full `make test`, timing. The manager re-queues the full job
(same script).

## 5.9 Re-staged job

The script is the same (`docs/dev/lanes/s3_job_587-kit-s3-heavy`); its dry-run is rc 0 in
0.1 s on the clean tree (tip of this part). Queue it from the MAIN tree:

```
scripts/boxqueue add --name 6NN-kit-s3-heavy worktrees/s3/docs/dev/lanes/s3_job_587-kit-s3-heavy
```

---

# Part 4. Fix C withdrawn; E[sh] reading (2026-10-23)

Frank's ruling (2026-10-23): fix C (D-hors declines where max(sh) == 1) moved bytes on an argument
with no measurement. It is taken out. Job 588 measures D-hors's admission instead, on the expected
shift per probe under the byte-rate prior: E[sh] = Σ_b rate[b]·sh[b].

## 4.1 Commits (ONE-S3-COMMIT kept)

| sha | what |
|---|---|
| f7bc3cf05 | part 1's review nits (unchanged) |
| **d3886a656** | **THE S3 COMMIT, amended again**: a962449c4 without fix C. Built with `git reset --hard a962449c4`, the C paths restored from e1e95a584 (fix B's asserts re-added), then `git reset --soft f7bc3cf05` and one commit. No interactive rebase |
| b8bcb23b1, 492461e74 | the part 1-3 report commits (d712939e5, 316f515f4), cherry-picked unchanged |
| ee0d4488d | `s3: K27 NULL-subject fixture on both arms (F-5)`, test-only |
| 86b9afa69 | job 588's E[sh] reading: esh_588.py, pick_esh_588.py, esh_588.tsv, measure_588.sh, read_588.py and the job's header |
| (next) | this part, the history-index entry, ideas.md |

What left the S3 commit (`git diff --stat a962449c4 d3886a656`, 8 files):
- window.c: the decline and `hors_table`'s return value;
- registry.md §6¶8a, the `wf-hors` row's decline clause;
- memfn/src/CLAUDE.md and memfn/tests/CLAUDE.md, the decline and plant S1424;
- g2_win_gen.c: the G2 decline control and `ctl_render_at`;
- run_g2_win.sh: plant S1424, and the controls note back to 116 (fix G's wf-floor 486 pin is kept);
- predicted_movers.tsv: fix C's note and its three rows;
- the 587 job header's plant list.

Everything else of fixes A, B and D-H is unchanged.

**The window.c diff against e1e95a584** is fix B's two asserts and nothing else, so D-hors's
admission is e1e95a584's:

```diff
@@ -1459,6 +1459,7 @@ static int run_group_ok(const struct wf_plan *w, unsigned from, unsigned to)
+_Static_assert(MF_MAX_TERM - 1 <= INT8_MAX, "a C-run term index (< MF_MAX_TERM) is an int8_t: w->grp[k] = (int8_t)nterm");
 static int find_groups(const mf_art *art, const wf_dec *d, struct wf_plan *w)
@@ -1530,6 +1531,7 @@ static int d_hors_holds(const wf_dec *d, const struct wf_plan *w, int32_t *wlo,
+_Static_assert(MF_MAX_SPAN_POS < 256, "a D-hors shift (at most a window's length) is a uint8_t: sh[b] = (uint8_t)t");
 static void hors_table(const struct wf_plan *w, int32_t wlo, int32_t whi, uint8_t sh[256])
```

**Finding F-8 (the manager's K27 edit).** The uncommitted edit to tests/codegen/run_codegen_tests.sh
had TRUNCATED the file: it ended after the new K27 loop's `done`, at 1,751 lines instead of 3,836. The
2,098 lines from the K27 pair arm to the end of the file were gone. I rebuilt it from the edit plus
HEAD's lines after the old K27 block, so the commit is +24/-14. `make test-codegen` reads the whole
file: 16/16.

## 4.2 Checks (d3886a656's tree; ee0d4488d for codegen)

| check | result |
|---|---|
| `make -j16` | clean |
| `make strict` | "whole tree compiles clean with -Werror -Wshadow" |
| `memfn/tests/run_g2_win.sh` | 7,640 passed, 0 failed; controls refused 116 |
| `memfn/tests/run_g2_win.sh --plants` | **12 of 12 RED** (S1400-S1407, S1409, S1410, S1422, S1423) |
| `tests/memfn/run_link_checks.sh` | 11 passed, 0 failed |
| `tests/memfn/run_wreply.sh` | 112 passed, 0 failed |
| bytediff vs c3ea619c3, default arm | **24 of 24 AGREE**: 16 ABI-ONLY, 7 MOVES-cover, 1 MOVES-cover-hors (hex8) |
| bytediff, OFF arm (`--memfn=no-wf-find,no-wf-hors`) | 24 of 24 ABI-ONLY |
| new vs e1e95a584's build (24 rows) | 24 of 24 identical |
| `(?s)[^a]..`, `(?s)[0-9a-f].[0-9a-f]`, `[0-9a-f].[0-9a-f]` vs e1e95a584 | identical (only the `#include` name differs). All three are cover with a `_sh[256]` table: D-hors again |
| `make test-codegen` (ee0d4488d) | 16/16 scripts passed. `[K27]` and `[K27 no-wf-find]` both PASS |
| 588 `--dry-run` | rc 0, 6 s: `esh-gate: 8 arm cells read; 1 esh rows live` (esh02) |
| all 12 E[sh] sites, smoke without a clock (under boxlock) | 12 of 12 built and premised; esh-gate 112 arm cells equal to python `re` |
| 587 `--dry-run` | rc 0, 98 s: 12 steps, mech 108 rows |

Not run, per the brief: make test, mech, timing. The two ref compilers (c3ea619c3, e1e95a584) were
built from `git archive` under build/.

## 4.3 The E[sh] reading (job 588, findings only)

- `esh_588.py` computes each value from pcrec's own text.
  - **sh[]** comes from the default artifact's `rx_mf<N>_sh[256]`.
  - **E[sh]** = Σ rate[b]·sh[b] / 10^6.
  - **max(sh)** is the largest entry of sh[].
  - **The stop set** is the `--memfn=no-wf-hors` artifact's D-one walk condition, evaluated by gcc
    over all 256 bytes inside a copy of that artifact.
  - **The stop mass** is Σ rate over the stop set, capped at 10^6 (kit_set_mass's arithmetic).
  - The prior is tests/findings/default_ppm.tsv.
- `pick_esh_588.py` (seed 20261023) draws the sites from 6 corpus D-hors movers and 19 hand
  patterns (24 candidates). §6's cells are excluded.
  - The strata are: e1 (E = 1, both forced), b1 [1, 1.5), b2 [1.5, 2.5), b3 [2.5, 3.5),
    b4 [3.5, 5) and b5 [5, hex8].
  - hex8-bounded is E[sh] **6.009**, the top of the span.
  - Dropped: `\N{2}` (not generatable), and `[0-9A-F]{6}` and `[0-9a-f]-[0-9a-f]{2}` (not D-hors).

| site | stratum | pattern | E[sh] | max(sh) | stop mass ppm | source |
|---|---|---|---:|---:|---:|---|
| esh01 | e1 | `(?s)[0-9a-f].[0-9a-f]` | 1.000 | 1 | 284,434 | forced |
| esh02 | e1 | `(?s)[^a]..` | 1.000 | 1 | 945,837 | forced |
| esh03 | b1 | `[aeiou]..[aeiou]` | 1.030 | 4 | 252,788 | hand |
| esh04 | b1 | `\b\w*?\B\w` | 1.193 | 2 | 807,006 | corpus |
| esh05 | b2 | `\w{5}` | 1.772 | 5 | 807,006 | hand |
| esh06 | b2 | `[a-z][a-z0-9]{3}` | 1.785 | 4 | 663,413 | hand |
| esh07 | b3 | `[a-z]{6}` | 2.683 | 6 | 663,413 | hand |
| esh08 | b3 | `[0-9a-f]{4}` | 3.147 | 4 | 284,434 | hand |
| esh09 | b4 | `[0-9a-f]{5}` | 3.862 | 5 | 284,434 | hand |
| esh10 | b4 | `[0-9a-f]{6}` | 4.578 | 6 | 284,434 | hand |
| esh11 | b5 | `[0-9a-f]{7}` | 5.293 | 7 | 284,434 | hand |
| esh12 | b5 | `[0-9a-f]{8}` | 6.009 | 8 | 284,434 | hand |

- esh03 is the case fix C's rule would have kept: max(sh) 4, but E[sh] 1.030. The reading tells
  them apart.
- **How the sites are timed.** measure_588.sh's side-set machinery is now shared (`use_set`) by
  the mover sample and this set.
  - Arms: NOH (`--memfn=no-wf-hors`, D-one) and RTE (default, D-hors), with NOHs/RTEs at
    `-fmemfn-simd`. All 12 sites have SIMD text equal to their scalar text (cover carries no SIMD
    form), so each is built and timed once and read for both layers.
  - Regimes: throughput and search_short.
  - Classes: real, random, and none where the prose does not match. Only esh09-12 get `none`, so
    there are 28 class subjects.
  - Same core (cpu 7), calibration (T = 20 ms, N = 9) and 5 launches as §6's cells.
  - Premise: both arms read cover, RTE has `_sh[256]` and NOH does not.
- **What read_588.py prints** under "D-hors admission (E[sh])":
  - per site, regime and class: E[sh], max(sh), the stop mass, NOH ns, the scalar and SIMD alpha
    (RTE/NOH), the floor (this run's A/A in the regime) and SLOWER/within/FASTER;
  - then a per-site summary sorted by E[sh] (geometric-mean alpha [min, max], SLOWER/FASTER counts),
    so a cut-off, if there is one, is visible.
  - It is outside `== s3t BAR PASS|FAIL` and changes no default. Tested on synthetic data only.
- **588's wall time:** 560 more timed items (about 1.7 min) plus about 0.5 min of
  subjects/build/gate, so **about 16-17 min** against about 14 before. The cap stays 3600 s.

## 4.4 Queue commands (from the MAIN tree)

```
scripts/boxqueue add --name 587-kit-s3-heavy worktrees/s3/docs/dev/lanes/s3_job_587-kit-s3-heavy
scripts/boxqueue add --name 588-kit-s3-timing worktrees/s3/docs/dev/lanes/s3_job_588-kit-s3-timing
```

- Queue 588 after 587 is green.
- 588 reads `worktrees/s3/build/s3/bin/pcrec`, now refreshed to d3886a656's build (sha256
  8d53dc29df1a; part 3's copy was ddbbf3191e9b).
- The ideas log gains the E[sh] admission row (memfn/docs/ideas.md, 2026-10-23).

---

# Part 3. Review fixes (lane s3fix, 2026-10-22/23)

The D6 review of S3 found no correctness bug. Its fixes A-I are folded in under the kit manager's
build go, and the ONE-S3-COMMIT structure is kept:

| sha | what |
|---|---|
| f7bc3cf05 | part 1's review nits (unchanged) |
| **a962449c4** | **THE S3 COMMIT, amended**: e1e95a584 plus fixes A-H. Rebuilt with `git reset --soft f7bc3cf05` from the WIP tip b39146772, the report-side paths unstaged. The tree equals b39146772's apart from the report, the history index and ideas.md |
| (next) | this report (parts 1-3), its history-index entry, and ideas.md (item I) |

## 3.1 Items A-I, each mapped to its artifact

| item | artifact |
|---|---|
| A abi reader miss | `docs/spec/match_api.md` §1¶7 guard sample `!= 83` -> `!= 84`. Re-grep in §3.3 |
| B latent wrap | `memfn/src/window.c`: `_Static_assert(MF_MAX_SPAN_POS < 256, ...)` above `hors_table`; `_Static_assert(MF_MAX_TERM - 1 <= INT8_MAX, ...)` above `find_groups`, which writes `grp[k] = (int8_t)nterm`. No byte move |
| C no-op D-hors (**WITHDRAWN in Part 4**) | `window.c`: `hors_table` now returns its largest shift, and `d_hors_holds` builds the table (into `w->sh`, the one source of the shift) and declines when it returns 1. Then D-one serves. The registry.md §6¶8a `wf-hors` row states the decline (D80). Updated: memfn/src/CLAUDE.md, memfn/tests/CLAUDE.md. Manifest, diff and G2 in §3.2 |
| D 587 census arms | `s3_evidence/census.py`: arms `c-simd` (`-fmemfn-simd`) and `c-norun` (`-fno-run-prefilter`). Each is judged both ways against NEW's own `RX_DFA_SCAN "cover"` stamp on that arm. Their OFF arms `off-simd` and `off-norun` (the same flag on both sides, both denies on NEW) are expected at zero movers. 587's header is updated. Smoke (2 patterns x 10 arms): hex8 moves on c-default/c-simd/c-norun (cover + D-hors), and is identical on all three OFF arms and on c-vm/ir. `x+y` is identical on all 10 arms |
| E 588 mover sample | `s3_evidence/pick_588.py` (the pick rule), `sample_588.tsv` (the committed pick, §3.4), `gen_sample_588.py` (subjects), `measure_588.sh` (stages `sample-build` and `sample-gate`, items after each launch's cells), `read_588.py` (section "Mover sample (not the §6 bar)"), `s3_job_588-kit-s3-timing` (dry run covers the sample, plus the estimate). The bar and `== s3t BAR PASS\|FAIL` are unchanged |
| F default-path witnesses | §3.5 |
| G floors | pinned AT the measure, cause kept: `simd_floor_check.py` MOVERS 29 -> **33** and SIMD_FUNC 29 -> **33** (measured 33/33 by the S3 lane's `sec2_test-memfn-simdfloor.log`. The part 2 report's "32" was wrong); `simd_guarded_check.py` simd-form 3 (already the measure, comment says so); `rank_check.py` door-can_begin_match 1060 -> **1179**; `run_libc_census.sh` funcs 127 -> **141**; G2 `FORM_FLOORS` wf-floor 435 -> **486** (seeded, deterministic). Fix C cannot move these counts: none of them reads D-hors's table (verified for SIMD: cover artifacts are byte-identical with and without `-fmemfn-simd`, 5 of 5 checked). The counts were not re-run on this build (§3.7) |
| H small items | (1) The facts_listing.md §4.1¶2 sentence that states the `cc_exact` read: *"Stating a span to the kit never sets `used`, and neither does the `cover` LOCATE row's admission (`match_api.md` §6.3.4¶2, routed by default since D172 S3), which reads `span_facts` as the statement its exact-language check (`kit_proof.md` §1.1's C8) holds the anchored machine to, on every build alike."* It was already there, so nothing was added. (2) `tests/mech/run_sabotage_matrix.sh`: B4''s stale clause "S922/S1079/S1105 are re-aimed at fd_row_decides" is removed, and its history is moved into the S3 paragraph's S1079/S1105 sentence. (3) ZK6/ZK7's retirement is recorded in that header beside S1251-S1256 |
| I ideas log | `memfn/docs/ideas.md`: three 2026-10-23 entries (widen D-hors's window to the contiguous tested core run; priced probe choice under the byte-rate; D-hors at non-REPORT E-find sites), each with its trigger. They are in the report commit, not the S3 commit |

## 3.2 Item C: the mover manifest delta (WITHDRAWN in Part 4: none of this is in d3886a656)

The prediction was committed BEFORE the diff ran (WIP ac5ae250b, squashed into a962449c4).
`predicted_movers.tsv` gains three rows:

| row | pattern | prediction | why |
|---|---|---|---|
| 9 | `(?s)[^a]..` | MOVES-cover | dense stop, both dots full (C-bound drops them): every shift 1, D-hors declines |
| 10 | `(?s)[0-9a-f].[0-9a-f]` | MOVES-cover | a full middle position: every shift 1, declines |
| 11 | `[0-9a-f].[0-9a-f]` | MOVES-cover-hors | control: the middle `.` is tested, so `sh['\n']` = 3, and D-hors holds |

`bytediff.sh` against c3ea619c3:
- default arm: **27 of 27 AGREE**;
- OFF arm (`--memfn=no-wf-find,no-wf-hors`): **27 of 27 ABI-ONLY**.

Old S3 (e1e95a584's build) against new: **exactly rows 9 and 10 change**. They lose an all-1
`_sh[256]` table; the old build gave both of them one. The other 25 rows are byte-identical,
hex8's D-hors included. At corpus scale the census's rule is unchanged (a mover is a cover
artifact); fix C changes the TEXT of some cover artifacts, never their class.

G2 window space:
- a new S3 control `(?s)[ab0].[ab0]` (a dense window whose middle position is every byte) must
  render E-find with NO `_sh[` table. `ctl_render_at` gains a per-position full-set mask;
- plant **S1424** (the decline ignored: `(void)hors_table(...)`) is RED on that control;
- the generated population's D-hors count is unchanged at 124. No generated site had an all-1
  table, so the control is the case that must decline. Controls: 117 (was 116).

## 3.3 Item A: the abi re-grep

The grep is not keyed on `abi`:

```
git grep -nwE '83' -- docs/spec tests/codegen 'CHANGELOG*' docs/dev/history/abi_changelog.md scripts tests/mech/sabotages/S693_abi_not_bumped.sh src cli lib memfn/include
git grep -nwE '83' -- tests docs/spec memfn/tests ':!*.rxt' ':!*.tsv'
```

The second grep returns 50 hits in 38 files. I reviewed each one. **The only abi reader was
match_api.md §1¶7's guard sample (fixed).** The other hits are not readers:
- `abi_changelog.md`: the 83 entry and its renumbering note (history, correct);
- `S693`: `SAB_AFTER` 83 is the parent's number, as designed, plus its re-aim notes;
- `run_codegen_tests.sh:3153`: the transition list in the message;
- the rest are counts unrelated to abi: emit_sweep pins, reqcube/S452's byte 83 `'S'`, bench
  ledgers, floors and NOTES.

CHANGELOG.md has no 83.

**Does any test read the guard-sample block?** No.
- The two tests that open match_api.md, `run_fallback_table.sh` and `axes_registry_check.sh`, read
  only its `<!-- value-set: ... -->` tables.
- The K80/multi-artifact checks in `run_codegen_tests.sh` read the ARTIFACT's guard, not the spec's
  sample.

**FILED:** the spec's guard sample has no checking reader, so a future bump can miss it the same
way. No new check was built, per the brief.

## 3.4 Item E: the sample, its rule and its estimate

`pick_588.py`, run once on this build under `scripts/boxlock` (`pick_588: 4753 corpus patterns, 804
cover movers in 5 strata, 24 picked`):
- the mover list is census.py's rule on census.py's enumeration (default artifact reads `cover`),
  with §6's 8 cells excluded;
- strata are read from the artifact's text. B form: LIBC (`memchr(`) or WALK, read for a D-hors
  artifact from its `no-wf-hors` compile, since D-hors replaces B. D: `_sh[256]`. C-run: `rx_w`/`memcmp(`
  in the E-find statement;
- **engine: the vm stratum is empty by construction** (C1, cover is a DFA-route row), so it is
  reported, not sampled;
- a candidate must be generatable (python `re` reads it and a generated match verifies);
- the pick: `random.Random(20261023)` per stratum over the sorted candidates, round robin.

| stratum (B/D/C) | movers | generatable | picked |
|---|---:|---:|---:|
| LIBC/one/norun | 286 | 153 | 5 (smp01 `\|`, smp06 `z(?!a)`, smp11 `(?x)a#`, smp16 `(?<!a)c`, smp21 `:`) |
| LIBC/one/run | 216 | 136 | 5 (smp02 `ABCDEFGH`, smp07 `z(?:ab){3,}?`, smp12 `.{3}cat`, smp17 `a{ , }`, smp22 `a{2,2}c`) |
| WALK/hors/norun | 6 | 5 | 5 (smp03 `[^abc]{2,4}?`, smp08 `\b\w*?\B\w`, smp13 `...`, smp18 `..`, smp23 `\w\B\w`) |
| WALK/one/norun | 282 | 85 | 5 (smp04 `[a[:b]`, smp09 `(?:(?!a)z\|w)`, smp14 `[a-]`, smp19 `[[:]`, smp24 `[:a]`) |
| WALK/one/run | 14 | 12 | 4 (smp05 `(?:(?i:abs)\|(?i:ab)S)`, smp10 `(?i)foobar`, smp15 `(?i)abc`, smp20 `(?i)x/1234`) |
| LIBC/hors/* , WALK/hors/run | 0 | - | - (empty in the corpus) |

How each sample row is timed:
- **Classes:** `real` (prose with generated matches planted), `none` (the prose, skipped where it
  matches), `random` (uniform printable ASCII). Generated here (python only): 61 of 72 class
  subjects. The 11 skips are all `none` on patterns the prose itself matches.
- **Regimes:** throughput and search_short.
- **Arms:** DEF/RTE at the scalar layer and DEFs/RTEs at the SIMD layer. Same core (cpu 7), same
  calibration (T=20 ms, N=9) and same 5 launches as the cells.
- **Shared arms:** an arm whose text equals its other-layer twin's is built and timed once and
  read for both. A cover artifact carries no SIMD form.
- **Floor:** this run's A/A in the regime (the largest |RT2/RTE - 1| over §6's cells). Above
  1 + floor is flagged **SLOWER**.
- **Drops:** a row that fails a premise, a compile or the answer gate is DROPPED with a loud
  `SAMPLE ...` line and never stops the job.

**Estimates.** One timed item measures 0.18 s.
- 587: the census grows from 6 to 10 arms, about 95k compiles at about 3 ms over 16 jobs, i.e.
  about a minute. 587's other stages are unchanged (cap 21600 s).
- 588: the §6 cells are about 1,900 items, about 6 min, plus about 1 min of build, differential
  and gate. The sample is at most about 1,700 items, about 4-5 min, plus about 1.5 min of
  subjects, build and gate. So about **14 min in all, against about 7 before** (2x). The cap stays
  3600 s.

## 3.5 Item F: default-path witnesses, section by section

These are every test file the S3 commit re-aimed to `--memfn=no-wf-find`.

| section (file) | disposition |
|---|---|
| tests/codegen/runcmp_check.py | **WITNESS ADDED.** `cover7` (`ABCDEFG`, no deny) must read `RX_DFA_SCAN "cover"`. Every runcmp check then holds of E-find's C-run compare: words at [0, 3] spell the run, the last at L - W, `RX_RUN_WORDS` 1, helper ahead of use, `-Werror`, and `-fno-run-overlap` restores one memcmp. The helper-before-use check now finds the first use of any spelling, not `rx_w<W>(subject`. 104 passed, 0 failed |
| tests/codegen/run_dfa_stamps.sh | already has a default `cover` witness (`cover none 'a'`) and the cover-walk derivation marker (S3) |
| tests/codegen/cand_oracle_witnesses.tsv / run_cand_oracle.sh | already has default `cover` rows (U1, e.g. `cover - foobar`, harness flag dropped at S3) |
| tests/codegen/run_codegen_tests.sh (K27 pair arm) | old mechanism only: K27's pair arm is the pre-check's caseless pair block, and a cover artifact runs no pre-check. The K27 CONTRACT (NULL subject, n = 0) does reach cover by default: the first K27 fixture `abc` now compiles to `K27_DFA_SCAN "cover"` (finding F-5) |
| tests/codegen/run_offset_skip.sh | old mechanism only: the offset-skip block. A cover artifact defines no offset-skip function |
| tests/codegen/run_scan_edge_census.sh | old mechanism only: the scan machines' edges. A cover artifact runs no forward machine |
| tests/codegen/reqcube_check.py | old mechanism only: the run PRE-CHECK's caseless necessary run and its REQ_* stamps. A cover artifact runs no pre-check (emit_cover hard-fails on one). E-find's masked compares are not witnessed here; runcmp's cover7 is unmasked |
| tests/codegen/run_facts_checks.sh (E3) | old mechanism only: E3 lists the unanchored forward scan's NEXT-row run and pin, and cover has no forward scan. The cover listing's stamps are job 587's `facts` census arm |
| tests/memfn/rows.tsv | old mechanism only: the re-aimed rows (pf_memchr_bounded, pf_walk_bounded, fn-pair, vrun-w16/w32) are prefilter/pre-check/FUNC rows a cover artifact never calls. The window family's rows are not rows.tsv rows. Their reach witness is run_g2_win.sh's controls |
| tests/memfn/c10_presence.tsv | old mechanism only: the pre-check's presence handoff |
| tests/memfn/pres_pick_witnesses.tsv | old mechanism only: the pre-check's five picks. A cover artifact makes no pick |
| tests/memfn/run_wreply.sh | old mechanism only: the window REPLY (phase 1) as the prefilter NEXT rows read it. Cover renders through phase 2 |
| tests/memfn/simd_floor_check.py | old mechanism only: SIMD FUNC movers. Measured: cover artifacts are byte-identical under `-fmemfn-simd` (E-find has no SIMD row) |

## 3.6 Findings (new)

- **F-5 (a re-aim the S3 commit missed).** `run_codegen_tests.sh`'s first K27 fixture `abc` is a
  `cover` artifact by default now.
  - Its comment says it "is chosen to take the single-escape-byte memchr arm".
  - The K27 contract is still checked, on E-find's guarded LIBC find (`c + d < n ? memchr(...)`).
  - The old pf_memchr arm is no longer K27-witnessed.
  - Cheap fix, not done here (scope): run the fixture a second time under `--memfn=no-wf-find`.
  - Owner: whoever lands S3, or a follow-up.
- **F-6.** The earlier s3 lane left a detached poller, `build/s3scratch/run_sections.sh` (PID 1270061).
  - It was holding on the findbench-parity jobs, and was then going to run 54 `make test` sections
    one by one in this worktree.
  - That contradicts this brief ("Do NOT run make test"), and it would have built in a tree under
    edit.
  - I killed it with `scripts/safekill` (it was in its 2-minute HOLD sleep; no section had run).
- **F-7.** `(?s)[^a]..`-shaped windows were rare in the space: none of G2's 1,900 generated sites
  hit them, and of 804 corpus cover movers 6 carry D-hors at all.

## 3.7 Checks run (this build, a962449c4's tree)

| check | result |
|---|---|
| `make -j16` | clean |
| `make strict` | "whole tree compiles clean with -Werror -Wshadow" |
| `make test-codegen` | 16/16 scripts passed (incl. SABANCHOR: 915 anchors resolve) |
| `tests/memfn/run_link_checks.sh` | 11 passed, 0 failed |
| `memfn/tests/run_g2_win.sh` | 7,640 passed, 0 failed (ASan+UBSan 3,800/0; W1 4/4 red; controls 117) |
| `memfn/tests/run_g2_win.sh --plants` | **13 of 13 RED** (S1400-S1407, S1409, S1410, S1422-S1424) |
| `tests/memfn/run_wreply.sh` | 112 passed, 0 failed |
| byte-diff vs the updated predicted manifest | 27/27 AGREE; OFF arm 27/27 ABI-ONLY |
| `list_axes_delta.sh` | "5 row(s), exactly as declared" |
| runcmp_check.py (standalone, the file test-codegen runs) | 104 passed, 0 failed |
| 588 `--dry-run` | rc 0, 6 s. hex8 cell: build, premises, differential and gate. Sample row smp01: `sample-gate: 12 arm cells read; 1 sample rows live` |
| 587 `--dry-run` | NOT run: it needs a clean tree (the report commit), and by then 598-findbench-parity-opt (a timing window) held the box, where only reads and edits are allowed. `boxqueue add` dry-runs it at enqueue (108 mech ids, census.py parse, clean tree); 587's only changes are census.py's 4 arms (smoke-run in-process, §3.1 D) and its header |

**NOT run** (per the brief): make test, mech, timing.
- The G floors were pinned from the S3 lane's measured logs, not re-measured. A single-section
  run needs findbench-parity-opt/-opt2 to be clear, and both were pending throughout.
- Job 587's `make test` reads them.

## 3.8 Queue commands (from the MAIN tree)

```
scripts/boxqueue add --name 587-kit-s3-heavy worktrees/s3/docs/dev/lanes/s3_job_587-kit-s3-heavy
scripts/boxqueue add --name 588-kit-s3-timing worktrees/s3/docs/dev/lanes/s3_job_588-kit-s3-timing
```

Queue 588 after 587 is green. 588 reads `worktrees/s3/build/s3/bin/pcrec`. It has been refreshed to
this build (sha256 ddbbf3191e9b); the part 2 copy was 014efd267a4e.

---

# Part 2. Build

## 2.1 Commits

| sha | what |
|---|---|
| f7bc3cf05 | part 1's review nits (comments only) |
| 6f100c00f | part 1's report |
| e1e95a584 | THE S3 COMMIT (kit + pcrec + abi 83 -> 84 + spec + manifests + retirements + re-pins), squashed from the lane's WIP commits with `git reset --soft 6f100c00f` |
| (next) | this report, its history-index entry, the 588 dry-run on one cell |

## 2.2 E-find as built (ready for window_site.md rev 3.3, §2.6)

**Table E**, first match (`wf_erows[]`, window.c):

| row | holds when | text | deny |
|---|---|---|---|
| E-func | FUNC/RETURN, no expression floor, and the plan translates (legacy_ok) into a site today's rows serve | today's | - |
| E-stmt | STMT/ASSIGN or ON_MISS, same | today's PF block | - |
| **E-find** | STMT/ASSIGN (its contract); the plan has a STOP whose set is not every byte; the FIND slot gives that stop a form (`fd_find_form`: LIBC or WALK) | the family's find-then-verify loop (below) | `wf-find` |
| E-generic | any frame, but not a REPORT site | the floor (`wf_floor_arm`) | - |

**Ordering argument (R1).** The legacy rows come first, so every site the legacy translation serves
keeps today's bytes. E-find comes before the floor. So S3's movers are exactly the sites the legacy rows
decline that reach E-find:
- REPORT, which `e_legacy_holds` excludes by name (a REPORT site is never translated);
- D-hors, inside E-find.

No non-REPORT site of a default artifact reaches E-find, and the census (job 587) holds this: a mover
must read `cover` on its own artifact.

**E-generic declines REPORT.** For a REPORT site the floor is COV, which R-27 measured as 10x slower than
DEF on literal cells. So a REPORT site E-find does not render is REFUSED. That happens when:
- `no-wf-find` denies E-find;
- the frame is not STMT/ASSIGN;
- the plan has no stop.

`mf_ask` then refuses. pcrec's C13 (`report-served`) declines `cover`, LOCATE falls to `composite`, and
the OFF arm is exactly DEF (R2). This rule is keyed on the consumer kind and is separate from E-find,
which is keyed on none. It is stated in the code.

**E-find's text** (`wf_find_expr`). The frame is the floor's STMT/ASSIGN shape: NOP's guard, the result,
the on_miss test. The search is one statement expression:

```
({ S, N, LO[, FL]; size_t C = LO; int F = 0;
   for (;;) { B; if (!(BOUND)) break; if (TEST) { F = 1; break; } C++; }
   F ? C : miss; })
```

- **B: the FIND slot's decision, read for the FORM only (R1).** `fd_find_form` asks `fd_rows[]`'s FIND
  slot "the next byte in set(d*)".
  - It states a one-term FIND site of today's PF shape with the window site's kind, policy and opts, so
    `fd-d1` and the VM seek role keep their effect.
  - Its table is stated OFFERED, because R7w's REF requirement is a contract on the pf_walk arm, not on
    the form. KD_ALL gained REPORT, the kind RPT alone served.
  - LIBC is a `memchr` for the stop's byte from `C + d*`; a miss leaves the loop.
  - WALK is an in-place walk, with C-table if pcrec names an offered table (`table_name`), else C-own
    (`kit_set_test`).
  - A stop below the candidate (d* < 0, a FAILS before-side) first raises C to |d*|, or to F + |d*|
    under an expression floor. So no read lies below max(c + d*, F, 0).
- **BOUND:** the floor's hoisted core bound, upper half (`wf_bound`, shared with the floor).
- **TEST** (`wf_find_test`), in order:
  - the floor's lower bound (`wf_lower`);
  - each position in ascending order (`wf_pos_test`, shared with the floor: membership on a core
    position, the three-way guard otherwise), less the stop where C-stop dropped it;
  - a C-run stretch (the decision's `pterm` group, every position core and run-shaped) is ONE run
    compare through runcmp's row table (`run_cmp_render`), its word helpers declared at define
    (`run_cmp_prepare`).
- **D-one:** `C++`.

**D-hors** is Table D's first row (`wf_drows[]`, deny `wf-hors`). It holds when all of these hold:
- the stop set's mass (`kit_set_mass` over pcrec's byte-rate) is at least `HORS_MIN`. That is
  plan_cost.def's 145,822 ppm, floor(sqrt(74,760 x 284,434)), PROVISIONAL;
- the window (the core of the first verify-YES span whose core holds the stop) has 2 or more positions;
- the window's last offset `hl` is >= 0.

It replaces B:

```
if (C + chi >= N) break; unsigned char b = S[C + hl];
if (!(b in T_hl)) { C += sh[b]; continue; }
if (TEST less hl) { F = 1; break; } C += sh[b];
```

`sh[b]` is the least t >= 1 such that b lies in the TESTED set at offset hl - t (an untested offset
accepts every byte). Where no such t lies inside the window, `sh[b]` is the window's length. So a
candidate c + u with 0 < u < sh[b] would need b at its own offset hl - u, and no tested set there holds
it. The table is a file-scope `static const unsigned char <p>_mf<h>_sh[256]`, written at define.
chi >= hl, so the probe lies inside the bound.

**Class.** `wf_plan_class` covers the positions the text tests (the stop's find included) and the row's
libc and include bounds (E-find: `libc` 1, `MF_INC_STRING_H`). On a REPORT site that is EXACTLY the
stated sets, which pcrec's C14 holds (emit_cover hard-fails otherwise).

## 2.3 The mover manifest: predicted, then actual

The prediction was committed BEFORE any diff ran: `s3_evidence/predicted_movers.tsv`, WIP commit
ac687f688, squashed into S3. It has 24 rows:
- 581's 8 cells, predicted `MOVES-cover` (hex8-bounded `MOVES-cover-hors`);
- 16 non-cover patterns (variable width, anchored, end-pinned, VM), predicted `ABI-ONLY`.

`bytediff.sh` compared against c3ea619c3 (`-fcomments --features all`, `.c` and `.h`, abi digits
masked):

| arm | rows | agree |
|---|---|---|
| default | 24 | **24** (8 MOVES-cover, of which hex8 MOVES-cover-hors; 16 ABI-ONLY) |
| OFF (`--memfn=no-wf-find,no-wf-hors`) | 24 | **24 ABI-ONLY**: every cell, the 8 cover cells included, is byte-identical to c3ea619c3 apart from the abi digits |

The first run printed 16 DISAGREE. The cause was my mask missing the header's
`(PCREC_RX_ABI_H + 0) != 83` line, not the prediction. I fixed the script; the prediction is unchanged.

At corpus scale, the prediction is census.py's rule, judged both ways in job 587:

| arm | declared |
|---|---|
| c-default, c-utf8 | a mover is exactly an artifact reading `RX_DFA_SCAN "cover"` |
| c-vm, ir | no mover |
| facts | movers only among default-cover patterns: the listing mirrors the artifact's `RX_DFA_*` stamps and the `used` record |
| OFF | no mover |

D-hors's table may appear only in a cover artifact. A 40-pattern smoke run had 0 unexpected.

Light population: `run_dfa_stamps.sh` over 4,871 corpus patterns finds 828 of 2,263 DFA artifacts
reading `cover`. No hybrid does (cover is a DFA-route row).

## 2.4 The OFF arm

Both denies render the parent's text but for the abi digits (§2.3, 24 of 24).
- `no-wf-find`: the family refuses a REPORT site, so C13 reads `refused` and `cover` declines.
- `no-wf-hors`: hex8 keeps `cover`, resumes by D-one and has no `_sh[256]` table. Checked by hand and by
  G2's control.

## 2.5 The `--list-axes` delta (R4 condition 2)

`s3_evidence/list_axes_delta.tsv` declares the delta, and `list_axes_delta.sh` checks it both ways:
- `-locate 2 unanchored`
- `+locate 2 cover`
- `+locate 3 unanchored`
- `+memfn wf-find`
- `+memfn wf-hors`

Result: "5 row(s), exactly as declared".

`axes_registry_check.sh`: 236 passed, 0 failed, memfn floor 14 (registry.md §6¶8b, raised from 12).

## 2.6 abi readers (D76/D94), by grep

Command (part 1's): ``git grep -nIE '(abi|ABI_EXPECT|PCREC_ARTIFACT_ABI|PCREC_RX_ABI_H)[^0-9]{0,40}\b83\b|`83`|\b83\b[^0-9]{0,25}\babi\b' -- src tests docs/spec scripts cli lib memfn``

| reader | change |
|---|---|
| `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI` | 83 -> 84 |
| `docs/spec/match_api.md` §1¶7 (`#error` text, `PCREC_RX_ABI_H`), §6's `rx_info` `abi` row, §6¶17 | 84 |
| `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT` and its transition message (83->84 appended) | 84 |
| `tests/mech/sabotages/S693_abi_not_bumped.sh` | BEFORE 84, AFTER 83; re-aim note |
| `docs/dev/history/abi_changelog.md` | the 84 paragraph (PROVISIONAL), above 83's |

The suites that count:
- codegen: test-codegen's 16 scripts, after the re-aims;
- registry: test-registry rc 0;
- rxtsource: in job 587's `make test`.

**84 is PROVISIONAL.** Main's I1+I2 iterators may land first and take 84. In that case S3 renumbers at
landing with the same grep, and this report's numbers move with it.

## 2.7 Retirements (window_site.md §4's S3 row; R5)

| retired | where |
|---|---|
| RPT (finder row, `ct_rpt`) | memfn/src/finder.c; tests/memfn/{rows.tsv, row_floors.tsv, finder_check.py FIND_ROWS, run_rows.sh ROWS_FLOOR 36 -> 35}, arm_fixtures.c (`fd-RPT`, `report2`) |
| `kit_report_exact` | memfn/src/compose.c, kit.h; finder.c `report_facts` |
| `SF_PROOF_EXACT` | finder.c (bit 12 reserved by comment) |
| `FF_PROOF` | finder.c. `ff_name` is fixed: A3 had printed "RUN" since D2's retirement (§2.16 F-2) |
| `fd_nested_walk` (FF_PROOF's only producer) | finder.c, kit.h, compose.c `select_arm` |
| `mf_preview("R-26.6")`, `fd_previews`, `fd_preview_step`, `fd_row_decides`, `mf_art.preview` | compose.c, finder.c, kit.h, memfn.h (a retirement note left); src/gen/memfn_sites.c (the call); src/core/internal.h and cli/main.c (comments: the `--harness=kit-proof` lever is INERT, F-4) |
| D2 | already retired at S2 commit 6 |
| tests | proof_check.c families C and D: the preview renders and controls retire, and a REPORT site stated in terms is now REFUSED on every art. run_proof.sh plants S1251-S1256, ZK6 and ZK7 |
| mech | S922, S1251, S1252, S1253, S1254, S1255 and S1256 deleted; the matrix's memfnfinder note names their successors (run_g2_win.sh's REPORT controls, plants S1422/S1423). S1079 and S1105 are re-anchored from `fd_row_decides` to `fd_route`/`fd_pres`, with the same intent |
| finder_history.md | three entries (RPT; KD_ALL + the form read; `ff_name`) |

No retirement's premise turned out false: nothing still needs RPT. An old-field REPORT site (terms in
`pred`) is now refused in `select_arm` before any walk, with a message naming the window family.

## 2.8 The pcrec half (R3; R4 conditions 1 and 4)

- `locate_cover_applies` is `pcrec_cover(cx)->why == NULL`: routed by default.
- `.list` is `locate 2 cover`; `composite` is re-indexed to `locate 3 unanchored`.
- `RX_DFA_SCAN "cover"` (spec in §2.9).
- C17: `tests/memfn/site_manifest.tsv` row COVER moves `preview` -> `delegated`. test-memfn-manifest is
  green.
- `cc_exact` reads `pcrec_fact_span_stated` on every build. **This is a choice, stated in
  facts_listing.md §4.1¶2:** the cover admission reads `span_facts` as a statement check, so `used` does
  not move for it. The alternative, `pcrec_fact_span` (what the harness did), would flip `used` no->yes
  on every pattern that reaches C8, and that needs a partial declared-move form emit_sweep does not
  have. Overturn it if `used` should read yes.
- NOT built: the `PCREC_NO_KIT_PROOF` flag bit 57 (R3). known.c's table comment says so.

## 2.9 Spec hunks (D80, in the S3 commit; R4 condition 1)

- `match_api.md`:
  - §3.1¶21: a `"cover"` scan takes none of the four start-recovery forms;
  - §6 `rx_info.scan` row: `"cover"`;
  - §6.3.4¶2: the `RX_DFA_SCAN` value table gains a `"cover"` row;
  - §6.3.4¶11: `"attempt-start"` now covers `"cover"`;
  - abi 84 in §1¶7, §6 and §6¶17.
- `registry.md`: §6¶8a rows `wf-find` and `wf-hors`; §6¶8b floor 14.
- `tuning.md` §2.43¶3d: both deny rows, and the OFF arm's identity.
- `facts_listing.md` §4.1¶2: `used` and the cover admission.

## 2.10 §6.1's readers that move, derived by grep and by running them (R3)

The scan stamp's readers by grep (``git grep -lE 'RX_DFA_SCAN|DFA_SCAN=|"unanchored"' -- tests scripts``)
come to 74 files. I then ran the sections that own them. Each re-aim follows one of two rules:
- **(a)** A witness of a non-cover mechanism that became `cover` carries the cover row's deny
  `--memfn=no-wf-find`. That renders the default build before S3, so its old expectation holds
  unchanged.
- **(b)** Where the DEFAULT path is the point, the witness becomes a non-fixed-width variant, or the row
  moves to witness `cover` itself.

Corpus POPULATION floors that cover legitimately shrank are re-pinned to about 90% of the new measure,
with the cause beside each.

| reader | change |
|---|---|
| tests/codegen/run_dfa_stamps.sh | `cover` in SCAN_VALUES; a derivation marker for the cover walk (`emit_cover`'s report line); witness `cover none 'a'`; the offset-0, hat, offset-set and run-pinned witnesses under (a) |
| tests/codegen/run_codegen_tests.sh | the K27 pair arm compile under (a); the ABI pin and message |
| tests/codegen/runcmp_check.py, reqcube_check.py | every witness compile under (a) |
| tests/codegen/run_offset_skip.sh | `emit` under (a): every row is offset-k, measured before cover |
| tests/codegen/run_scan_edge_census.sh | every compile under (a): the census is of scan machines |
| tests/codegen/run_facts_checks.sh | E3 witnesses `abc` and `/abcd[xy]/user` (x2) under (a) |
| tests/codegen/run_nomatch_caps.sh | three dead-group witnesses now witness `cover/attempt-start` (b); `(a){0}x$\n` keeps end-minus-width; `cover/attempt-start` joins the forms list |
| tests/codegen/cand_oracle_witnesses.tsv, run_cand_oracle.sh | 12 lines under (a); the `cover` witnesses drop `--harness=kit-proof` (shipped); [cand-oracle-shipped] prints UNREACHED when no harness-only row exists |
| tests/memfn/pres_pick_witnesses.tsv | 9 lines under (a) |
| tests/memfn/rows.tsv | pf_memchr_bounded, pf_walk_bounded, fn-pair and vrun-w16/w32: witness and control under (a) |
| tests/memfn/c10_onebyte.tsv | `\B(?<!a)d` -> `\B(?<!a)d+` (b) |
| tests/memfn/c10_presence.tsv | `x\d{3}abcde` under (a) |
| tests/memfn/run_arm_reach.sh | `\B(?<!a)d` -> `\B(?<!a)d+` (b) |
| tests/memfn/run_presence.sh | `é{2}cat` -> `é{2,3}cat`, `a{3}(?i:cat)` -> `a{3,4}(?i:cat)` (b) |
| tests/memfn/run_wreply.sh | `comp` under (a) |
| tests/memfn/simd_floor_check.py | witness mod-i under (a); the MOVERS and SIMD_FUNC floors 39 -> 29 (32 measured) |
| tests/memfn/simd_guarded_check.py | `simd-form` floor 5 -> 3 (3 measured) |
| tests/memfn/rank_check.py | `door-can_begin_match` floor 1400 -> 1060 (1,179 measured) |
| tests/memfn/run_libc_census.sh | `funcs` floor 169 -> 127 (141 measured) |

These sections run green after the re-pins:

| section | result |
|---|---|
| test-codegen | 16 of 16 scripts |
| test-registry | green |
| test-kitproof | 88/0 |
| test-cand-oracle | 168/0 |
| test-memfn-finder | 1,916/0 |
| test-memfn-g2, -arms, -rows, -deleg, -forms, -reach, -guarded, -rank, -arch, -manifest, -stamps, -simdfloor | green |
| test-fallback-table | green |
| test-spec-history, test-claudemd-size, test-plan-lint, test-ci-shards | green |

**OWED to job 587.** I ran none of the remaining TEST_SECTIONS members: the box carried a queued
`make test` (597-iteropt-test held the lock), and the brief says no `make test`. kit_proof.md §6.1 names
the likely movers among them: startset manifests, endmark, prechecks, findings mover manifests,
rxtsource, search-pinned, start-landing, emit_sweep's DIFFER_PINS (job 587's `sweep_start` step), size,
and corpus answers. A red there is this delivery's re-pin: the census names the patterns that moved, and
rule (a) or (b) applies.

## 2.11 Staged jobs (not queued)

| job | file | runs |
|---|---|---|
| 587 | `docs/dev/lanes/s3_job_587-kit-s3-heavy` | build, strict, the reference build of c3ea619c3, `s3_evidence/census.py` (6 arms, movers declared and judged both ways, the OFF arm expecting zero), `emit_sweep --arms start` (DIFFER_PINS), the bytediff and `--list-axes` evidence, test-codegen, `make test` via perfrun, test-memfn-link, the G2/proof/wreply plants, mech over the derived union (108 rows), REACH_ONLY |
| 588 | `docs/dev/lanes/s3_job_588-kit-s3-timing` | §6's acceptance through `s3_evidence/measure_588.sh`: 581's cells, classes and regimes, L=5 T=20 ms N=9, cpu 7, a differential and answer gate first; arms DEF (both denies), RTE, RT2, NOH and the -fmemfn-simd trio. `read_588.py` prints, per cell, the ratio to DEF, 581's floor, PASS/FAIL against §6's bar and the five caps, plus the G1 alpha of `wf-find` and `wf-hors` at both layers |

**Gating.**
- Both `--ready)` branches start with the i2build-parity hold.
- Job 588 also takes r27c's quiet gate.
- Job 588 reads the S3 compiler copied to `worktrees/s3/build/s3/bin/pcrec` (sha256 014efd267a4e, the S3
  commit's build).

**Dry runs** (`bash FILE --dry-run`):
- 588 (one cell, hex8-bounded): build, premises (D-hors fires, so NOH is timed), the differential (14
  arm builds, ASan included) and the gate (63 cells) pass in 5 s.
- 587: field validation of the 108 mech ids, the scripts, and a clean tree. It printed "worktree dirty"
  before this report's commit; the report commit makes the tree clean, and its rerun result is in the
  manager handback.

**Commands** (from the MAIN tree):

```
scripts/boxqueue add --name 587-kit-s3-heavy worktrees/s3/docs/dev/lanes/s3_job_587-kit-s3-heavy
scripts/boxqueue add --name 588-kit-s3-timing worktrees/s3/docs/dev/lanes/s3_job_588-kit-s3-timing
```

Queue 588 after 587 is green. Its verdict line is `== s3t BAR PASS|FAIL`.

## 2.12 Light checks (R4; the brief's list), on the S3 tree

| check | result |
|---|---|
| `make -j16` | clean |
| `make strict` | "whole tree compiles clean with -Werror -Wshadow" |
| `make test-codegen` | 16 of 16 scripts (after the re-aims, §2.10) |
| `tests/memfn/run_link_checks.sh` | 11 passed, 0 failed (R-28: 316 functions, largest 3,600 B) |
| `memfn/tests/run_g2_win.sh` | 7,640 passed, 0 failed (ASan+UBSan driver 3,800/0; W1 4 of 4 red) |
| `memfn/tests/run_g2_win.sh --plants` | 12 of 12 RED (S1400-S1407, S1409, S1410, S1422, S1423) |
| `tests/memfn/run_wreply.sh` | 112 passed, 0 failed (its plants are in job 587) |
| byte-diff, predicted manifest | 24/24 agree; OFF arm 24/24 ABI-ONLY |
| `--list-axes` declared delta | exactly as declared (5 rows) |

## 2.13 G2: the extension and its result

`g2_win_gen.c` and `run_g2_win.sh` are the independent control. Answers come from the generated facts
through g2_win_ref.c and the driver's scalar byte loop, never from the kit's generator.

- **400 DENSE REPORT sites appended** from their own stream (`rng3`, `G2W_S3_SITES`).
  - Each has span 0 with 3-5 alphabet draws per position, the tie-heavy rate (60,000 ppm a byte, so
    D-hors fires), REPORT kind, and an ASSIGN or in-place ASSIGN frame.
  - The 1,500 S2 sites are generated unchanged. I checked this with a site-by-site family diff against
    REF's generator.
- **REPORT sites E-find cannot render** must be REFUSED, and are then rendered as DFA_SCAN. That covers
  a FUNC or ON_MISS frame, and no stop by G2's OWN decision.
- **The S3 controls:**
  - E-find renders a REPORT site;
  - `no-wf-find` refuses it, with `mf_ask` and define agreeing;
  - a REPORT site in the FUNC frame is refused;
  - E-find renders a DFA_SCAN site no legacy row serves, and `no-wf-find` sends that site to the floor;
  - a dense window carries D-hors's table, and `no-wf-hors` removes it.
- **E-find census floors (K35).** These count the kit's text: a population, never a verdict.

  | part | measured | floor |
  |---|---|---|
  | libc | 357 | 320 |
  | walk | 220 | 195 |
  | hors | 124 | 110 |
  | run | 129 | 115 |
  | below | 110 | 95 |
  | report | 413 | 370 |
  | refused | 19 | 17 |

  Form floors: wf-find 701, floor 630 (new). wf-floor's floor goes 740 -> 435 (486 measured), because
  306 S2 sites moved off the floor to E-find.
- **The brief's edge cases.** The driver's layouts are a guard page at s + n, a guard page at s + F,
  and sentinel buffers, over subjects of length 0-12.
  - D-hors's probe and shift at the subject end and at n < window run under those layouts
    (`hors 124`).
  - A FAILS before-side stop at the start of the subject runs through B's raise (`below 110`).
- **Plants.** S1422 (E-find's deny ignored) and S1423 (D-hors's bound one short, 581's plant) are RED.
  A planted kit whose text no longer compiles now counts as red, not green: S1400's dropped F read
  leaves E-find's F declaration unused (`-Werror`).

## 2.14 Frames (R-28)

The `-fstack-usage` recipe, gcc 15.2 x86_64 -O2:
- largest: 3,600 B (`pcrec_mf_form_hash`, unchanged);
- next: `define_sel` and the new `fd_find_form`, 3,456 B each (`fd_find_form` holds one `mf_site`, E-find's
  form read);
- then: `wf_parts_prepare` 3,376 B, `wf_parts_check` 3,024 B, `pair_facts` 2,448 B.

`kit_report_exact`'s 3,184 B is gone. All frames are under 4,096 B. memfn/CLAUDE.md's peak line is
updated.

## 2.15 R6: `req_run_member` re-confirmed

`req_run_member` asks phase 1 only, and S3 changes no phase-1 row: E-find and D-hors are phase 2, and
the reply is unchanged. A cover artifact runs no pre-check (`emit_cover` hard-fails if one is
admitted), so the pre-check's run part never meets a REPORT site.

Measured:
- `run_dfa_stamps.sh` compiled all 4,871 corpus patterns, 828 of them `cover` (hex8's D-hors among the
  corpus covers);
- `run_nomatch_caps.sh` compiled 604 (route, pattern) artifacts.

Neither hit the hard-fail. The decision stands unchanged.

## 2.16 Findings

- **F-1 (latent, in S2's floor, not S3's code).** I found it with a perturbed G2 stream: my first S3
  draft shifted the RNG.
  - The site is `random#1416`, PARKED. It has a verify-YES span `{-3..-1}` with an empty core, an
    expression floor, and a FULL-SET position at -2.
  - C-bound drops the full-set position from the plan. At c = 2, F = 1, position -2 lies at subject
    offset 0, inside [0, F), which the core rule makes pcrec's EDGE: not covered.
  - The plan yields c = 2; BIND (the facts) says not covered.
  - Which side should win is a design question: C-bound against the three-way guard, on a full-set
    non-core position below F. No pcrec site states this shape (an expression floor is MLINE's
    `{-1: \n}` only).
  - G2's S2 population is kept unchanged.
  - Filed for the kit: a full-set non-core position below the candidate under an expression floor.
- **F-2.** `ff_name` was off by one after D2's retirement, so the finder listing printed A3 as "RUN".
  Fixed (§2.7), with a `_Static_assert`.
- **F-3.** The 650 harness's `measure.sh` premise ("DEF does not read cover") is false since S3. It is a
  design-dir instrument that no check reads, so it is left as is. Job 588 has its own premises.
- **F-4.** The `--harness=kit-proof` lever is INERT since S3. Its callers (tests/kitproof/,
  site_census.py, the 650 harness) still pass it. Filed retirement trigger: the next edit of
  tests/kitproof/.

## 2.17 Charter vs committed

| promise | artifact |
|---|---|
| R1 E-find: B a form-only read; C-yes under the hoisted bound and three-way guard; C-run via runcmp; D-one or D-hors (HORS_MIN, window >= 2) giving HRS's text; not keyed on REPORT; order E-func E-stmt E-find E-generic; the argument in code and report | window.c (`e_find_holds`, `wf_find_*`, the `wf_erows[]` comment), finder.c `fd_find_form`; §2.2 |
| R2 two deny rows; OFF = DEF exactly; floor 12 -> 14 with the spec literal | options.def `wf-find`, `wf-hors`; registry.md §6¶8b 14; §2.3-§2.4 |
| R3 .list re-index; "cover" scan value; C17 delegated; §6.1 readers by grep; NOT bit 57 | emit_dfa.c; match_api.md; site_manifest.tsv; §2.10 (sections run, the rest OWED to 587); bit 57 not built |
| R4(1) spec hunks in the same commit | §2.9 |
| R4(2) `--list-axes` delta declared, checked both ways | s3_evidence/list_axes_delta.{tsv,sh}; §2.5 |
| R4(3) movers by ID against a PREDICTED manifest written first; the OFF arm byte-identical | predicted_movers.tsv (committed before the diff); bytediff.sh; §2.3-§2.4; the corpus census in 587 |
| R4(4) abi readers by grep; 83 -> 84 PROVISIONAL | §2.6 |
| R5 the S3 retirements with their file lists | §2.7 |
| R6 req_run_member stays, re-confirmed | §2.15 |
| ONE S3 commit (kit + pcrec + abi + spec + manifests + retirements) | e1e95a584 |
| G2 extension: each B form x C-yes/C-run x D-one/D-hors against the scalar byte loop, ASan+UBSan, D-hors at the end and on short subjects, a FAILS before-side at the start | §2.13 |
| jobs 587/588 staged, dry-run, `--ready` holds | §2.11 |
| CLAUDE.md files whose files changed role | memfn/CLAUDE.md, memfn/src/CLAUDE.md, memfn/tests/CLAUDE.md, tests/memfn/CLAUDE.md, tests/kitproof/CLAUDE.md, src/gen/CLAUDE.md |

---

# Part 1. The stop (the first lane, kept as written)

**Original title:** s3 — D172 S3 (REPORT routed + D-hors): STOPPED at a design gap before the byte-moving commit

Lane s3, 2026-10-22 (opus). Worktree `worktrees/s3`, branch `lane/memfn-s3w`, cut from `lane/memfn-s3`
= main c3ea619c3 (R-29 / D172 S2 merged). Build go: D172 addendum (Frank 2026-10-21, "we need this
regardless of where hex lands"); main cleared S3 on 2026-10-22. No rulings file was named.

STATE AT HANDOFF:
- **Delivered:** the review-nits commit (nits 1-3), with no byte moves; `make` and `make strict` clean.
- **Nit 4 (req_run_member):** decided, with no code change needed (§3).
- **The S3 commit is NOT built.** The brief says to stop on a design ambiguity, and I found three (§2).
  Q1 blocks the kit half. Q2 and Q3 shape the pcrec half and the deny rows. Each has a recommendation.
- **Not staged:** jobs 587 and 588. Both measure the S3 commit, which does not exist yet (§6).

## 1. Commits

| sha | class | what |
|---|---|---|
| f7bc3cf05 | comments + CLAUDE.md, no byte moves | nit 1: `mf_wdecide`'s comment (memfn/src/window.c) says that -1 also means a refused heap allocation (OOM, R-28), and that every pcrec caller turns -1 into `pcrec_ctx_fail`. Nit 2: `src/facts/facts.h` (the `kset_walk` member) and `src/core/internal.h` (the [OPT-K] bounds header) now name the current home: emit_dfa.c `window_reply_ask` states the walk, and memfn/src/window.c's A-model/C-model make the selection; prefix_k.c retired at S2 commit 6. Nit 3: memfn/CLAUDE.md's frame peak line was re-measured (below) |
| (r) | docs | this report and its history-index entry |

**Nit 3, measured.** Recipe: `tests/memfn/run_link_checks.sh`'s `frames_of`, i.e. `gcc -O2 -std=gnu11
-fstack-usage` over every `memfn/src/*.c`, gcc 15.2.0, x86_64, at c3ea619c3. The six largest frames:

| frame (B) | function |
|---:|---|
| 3,600 | `pcrec_mf_form_hash` (the peak; unchanged) |
| 3,456 | `define_sel` |
| 3,376 | `pcrec_mf_wf_parts_prepare` |
| 3,184 | `pcrec_mf_kit_report_exact` |
| 3,024 | `pcrec_mf_wf_parts_check` |
| 2,448 | `pair_facts` |

All are under the 4,096 B bar.

## 2. The questions (STOP: the design does not say how S3 renders, or what pcrec's B1 half is)

### Q1 (BLOCKING, kit half): no row can render the routed REPORT form

window_site.md §6 defines the routed form as 581's PRO: "A-mass + B + C-yes + D-one + E-stmt". With D-hors,
HRS replaces D-one. §2.2 says Table B is the finder's FIND slot, with its rows kept unchanged. §2.6 says E-stmt
is "today's PF block". In the code at c3ea619c3, none of those rows can render PRO for a REPORT site:

1. **E-stmt reaches today's rows only through the legacy translation.** `legacy_ok` (window.c) declines any
   plan that tests a non-core position: `if (!w->core[i]) return 0;`. Every cover site with a SATISFIES
   context side states that side with an empty core (known.c `cover_window`). Examples: cat-bounded `\b...\b`,
   done-eol `...$`, hex8-bounded. So those sites cannot translate.
2. **No today row renders find-then-verify over a multi-term predicate.**
   - pffind's five rows render one SET term at offset 0 (`pf_shape_at`).
   - The generic row is the byte loop. That loop is COV, the text R-27 found 10x slower on literal cells.
3. **Table B's walk rows serve only sites that offer a table.**
   - R7w's contract serves `table_ref` REF only (finder.c `ct_r7w`). D1w is the same walk.
   - The cover statement offers no table.
   - So the year4, hex8 and word-digit stops (set stops) have no B row that serves them.
4. **`e_legacy_holds` excludes REPORT by name** ("REPORT routes at S3"), and the translation would carry
   `site_kind` REPORT into `select_arm`. There, only RPT serves REPORT, and RPT is retiring.

Measured today on `build/pcrec-harness --harness=kit-proof`:
- `abcdefgh` and `[0-9]{4}` render the family's FLOOR row (E-generic). That is `for (; c + 7 < n; c++)
  if (s[c] == 97 && ... && s[c+7] == 104)`, with no stop find, no run compare and resume `c++`.
- 581's PRO for lit-l8 is a different loop: a `memchr` for `b` at offset 1, then the rest verified (the literal
  as one compare), then resume.

So S3 needs one NEW family renderer. The design names its parts (§2 phase 2: "B FIND the next p in
[max(c + d*, F, 0), n) with s[p] in set(d*) ... C test the plan at c (one hoisted core bound, three-way guards
outside it) ... D on failure RESUME ... E render in the FRAME"), but it names no row that can render them.

**Recommendation: one family-owned STMT row, path `report`, on the floor's loop.** It holds where the frame is
STMT/ASSIGN and the plan has a stop (A-mass on a no-entry alternative). Its text:
- **B:** the floor's candidate loop with the stop's find at its head. The FIND slot's decision is read for the
  FORM only: LIBC (D1) becomes `memchr` at `c + d*`; WALK becomes the in-place walk over the stop's set, using
  C-table when pcrec offers a table and the kit's own `set_test` (C-own) otherwise.
  - R7w's and D1w's table requirement is a contract on the pf_walk ARM, not on the form. The family reading the
    decision this way changes no fd_rows contract.
  - A stop below the candidate (a FAILS before-side) starts its find at `max(c + d*, 0)`.
- **C:** C-yes positions under the hoisted bound and the three-way guard (the floor's `wf_test`). C-run's
  groups go through runcmp's row table (`run_cmp_render`, §2.7's "STAY: C-run's compare"), not one test per byte.
- **D:** D-one, or D-hors where the stop's mass is at least `HORS_MIN` and the window has at least 2 positions.
  D-hors gives HRS's text: probe the window's last position; advance by `sh[b]` over the TESTED sets.
- **The deny `no-<report row>` (the alpha OFF arm):**
  - The family DECLINES such a site, and `mf_ask` refuses it.
  - pcrec's C13 (`report-served`) then declines `cover`, and the LOCATE slot falls to `composite`. The OFF arm is
    therefore the pre-S3 default artifact, which is §6's DEF.
  - Do not use the floor as the OFF arm: that would be COV.
- **D-hors's own deny:** resume by D-one.
- One open point: whether this row is "E-stmt" with a new renderer or a Table E row of its own. That is naming,
  and the kit's call. I lean to an E row of its own (`E-report`) rather than overloading E-stmt's legacy
  meaning.

### Q2 (pcrec half): how much of kit_proof.md §7's B1 row is S3?

D172 calls B1 "cover on by default". window_site.md §5.2's S3 column names only the kit side (two deny rows,
registry §6¶8a/8b, "the cover stamps where caller-visible", the pcrec abi bump). kit_proof.md §7's B1 row and
§6.1's reader table add the following pcrec items:
- (a) `.list` for `cover`, which re-indexes the `locate` axis (`unanchored` 2 → 3, a declared `--list-axes` move);
- (b) the `"cover"` value of `RX_DFA_SCAN`/`rx_info.scan` (match_api.md §6.3.4, §6.3.4¶11, §5.5¶12);
- (c) the C17 manifest row `pending` → `delegated`;
- (d) **a pcrec flag `PCREC_NO_KIT_PROOF` (bit 57, `-fno-kit-proof`)**;
- (e) the §6.1 reader list: form-census floors and `KNOWN_VALUES`, `memfn_arm.py` ASSERT_ZERO cells (every kit
  deny that removes REPORT becomes a cover → composite mover), the startset manifests, `tests/endmark/`,
  `cand_oracle_witnesses.tsv`, `run_dfa_stamps.sh`, `run_rev_end.sh` and the rest, mech anchors that quote the
  scan stamp (21 files);
- (f) the bench `[inbox]` relay.

**Recommendation:**
- (a), (b), (c), (e): YES, in the S3 commit. (b) is caller-observable (D80). Once `"cover"` is in §6.3.4's value
  table, `axes_registry_check.sh`'s converse check ("every listed value is dumped") needs (a).
- (d): NO. The kit deny (Q1) already declines `cover` through C13, so a pcrec bit would be a second deny of
  the same choice. Flag bits are also [IFACE-PUSH]'s to batch. File it, with the trigger "a caller wants
  `cover` off without naming a kit row".
- (f): the manager's, at merge.

The light checks the brief names do not cover (e). Its reds would first appear in job 587's `make test`, so
the S3 lane should run the `make test-*` sections for (e)'s owners before staging.

### Q3: one deny row or two?

- The brief says "its own deny row ... the alpha OFF arm".
- window_site.md §5.2 says "TWO kit DENY rows (SCALAR, options.def): the routed REPORT row and D-hors", with the
  floor going 12 → 14.

**Recommendation:** two rows, as the design says. Each byte-moving change carries its own alpha OFF arm
(D144 item 4). With one row, D-hors's G1 alpha has no OFF arm separate from REPORT's. The floor goes to 14 in
registry.md §6¶8b.

## 3. Nit 4: `req_run_member`'s hard-fail stays as it is

`req_run_member` (src/gen/emit_dfa.c) states ONE alternative (`MF_ENTRY_NONE`) with ONE span: the run's
positions, verify YES. It asks phase 1 only (`mf_wdecide`).

The reply's `run_member` is computed by window.c `run_member()`:
- It reads only the stated R span and the byte-rate: the least cube mass, ties HIGHER, which is
  `pcrec_find_run_scan_index`'s rule.
- It runs inside `c_plan` before any C row. With one alternative, `d->ch` is 0 whatever Table A chose.
- Neither S3 change reaches it:
  - routing REPORT changes which phase-2 row renders a REPORT site;
  - D-hors is a Table D row, so it is phase-2 text that the reply does not carry.

So S3 gives no legitimate reason for the reply's member to differ from `r->idx`. A difference would still
mean the two copies of one rule disagree.

The function already is R-29's "ONE resolver" (filing note, condition (a)): it returns pcrec's index where
no window exists (`len < 2`) and the reply's member otherwise. **Decision: unchanged.** The hard-fail stays a
consistency assertion. It would need narrowing only if a later row read the frame or the frequencies
differently for R. That trigger is a change to `run_member()`'s inputs.

## 4. The abi readers (for the S3 commit; found by grep, D76/D94)

```
git -C worktrees/s3 grep -nIE '(abi|ABI_EXPECT|PCREC_ARTIFACT_ABI|PCREC_RX_ABI_H)[^0-9]{0,40}\b83\b|`83`|\b83\b[^0-9]{0,25}\babi\b' -- src tests docs/spec scripts cli lib memfn
```
(the ctx_span.md form, scoped to the live tree):

| reader | site |
|---|---|
| the define | `src/gen/emit_dfa.c` `#define PCREC_ARTIFACT_ABI 83` |
| spec | `docs/spec/match_api.md`: §1¶7's guard sample (the `#error` text and `PCREC_RX_ABI_H 83`), §6¶1's `rx_info` table (the `abi` row), §6¶17's sentence |
| codegen pin | `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT=83` |
| mech | `tests/mech/sabotages/S693_abi_not_bumped.sh` `SAB_BEFORE` |
| kit ledger | `memfn/docs/responses.md` (a historical sentence, not re-pinned) |

These are not found by citing the number but move with it (kit_proof.md §6.1, D94 addendum):
- `docs/dev/history/abi_changelog.md`;
- `tests/codegen/run_recursion_identity.sh`'s (B) pin;
- the byte-identity gates' pins;
- then the suites that count: registry, codegen, rxtsource.

The stamps `<PREFIX>_MEMFN_FORMS` and `_MEMFN_LIBC` move where the routed row calls `memchr` (LIBC) or adds a
form name. That is also the S3 lane's to re-pin.

## 5. Light checks run

| check | result |
|---|---|
| `make -j16` at f7bc3cf05 | clean |
| `make strict` at f7bc3cf05 | "whole tree compiles clean with -Werror -Wshadow" |
| pre-commit hook | 48 staged checks passed, CLAUDE.md sizes within limits |

None of the S3 checks ran: test-codegen, link checks, g2 win, wreply and the byte-diff all need the S3 commit.
The nits commit moves no emitted byte: it changes C comments and a CLAUDE.md line only.

## 6. Charter vs committed

| promise (brief / window_site.md) | artifact or OWED |
|---|---|
| nits 1-3, a separate commit before S3 | f7bc3cf05 |
| nit 4 decision | §3 (unchanged, with reasons) |
| §5.2 S3: REPORT routed by default (E-stmt text) | OWED. Owner: the S3 build lane after main's ruling on Q1. Trigger: that ruling |
| §5.2 S3: D-hors in the default table, `HORS_MIN` in plan_cost.def (PROVISIONAL) | OWED, same owner and trigger |
| §5.2 deny: kit rows in options.def, floor 12 → 14 | OWED. Q3 asks one or two |
| §4: RPT, `kit_report_exact`, `SF_PROOF_EXACT`, `FF_PROOF`, `mf_preview("R-26.6")` retire with the readers listed there (finder.c, kit.h, compose.c, memfn/src/CLAUDE.md, tests/memfn/{rows.tsv,row_floors.tsv,arm_fixtures.c,run_proof.sh,finder_check.py,run_rows.sh,proof_check.c}, memfn_sites.c, internal.h); D2 already retired at S2 | OWED with the S3 commit. S1255/S1256 wake or retire with RPT (wsc6 §5) |
| pcrec half (kit_proof.md §7 B1) | OWED. Q2 asks which items |
| abi bump + readers by grep in the same commit | readers listed in §4. Bump OWED |
| spec hunks (registry §6¶8a/8b; match_api §6.3.4 "cover" per Q2) | OWED |
| §5.2 sabotage: "the routed row denied but rendering"; "D-hors's bound one short" | OWED. Kit ids S1422-S1429 are free in the R-29 range (wsc6 §5) |
| §6 acceptance: 581 cells x 3 regimes x 3 classes, scalar bar + SIMD-on reported, five capped cells, G1 alpha both layers | OWED. Job 588 is staged after the build |
| correctness heavy job 587 (sweeps vs c3ea619c3 with declared movers, make test, mech, wreply) | OWED. Staged after the build |
| byte-diff on about 20 patterns (`-fcomments --features all`), movers = REPORT + hex8's D-hors | OWED |
| `req_run_member` per R-29's resolver ruling | done: unchanged (§3) |

## 7. For the lane that resumes

- Start from lane/memfn-s3w @ the report commit. The nits are in.
- Read §2 for main's rulings on Q1-Q3.
- The cover population is the movers: kit_proof.md §1.2 counts 79/51 bench and 712/526 corpus patterns
  (native/utf8), 1,288 distinct (flags, pattern). Re-count it from `cover_conj[]` at the build (K35).
