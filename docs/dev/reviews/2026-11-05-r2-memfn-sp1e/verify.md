# VERIFY crit-memfn-sp1e (SUBJECT 9de5b5638)

Compile count is kept at the end. Plants: VERIFY/plantN (git archive 9de5b5638, kit objects rebuilt into a copy of the review tree's libpcrec.a, -DMF_TRACE where traces are read).

## EMIT-1
Verdict: HOLDS.
- memfn/src/finder.c:528-534: `fd_decide` builds `gate_in in = { q->site, NULL, NULL, &q->ff, NULL };` (def NULL, wf NULL) and passes it to kit_walk.
- finder.c fd_find: `gate_in in = { s, def, NULL, &q.ff, st ? st->wf : NULL };` goes only into `gate_tctx tc` (trace context), not the walk.
- memfn/src/gate.c:588-595 `cl_core`: `a = in->wf ? in->wf->alt : NULL; if (!a) return -1;` so with wf NULL core is unstated.
- finder.c:209-210 `ct_d_hors ... CM(CORED)`.
- Plant1 (stronger than dropping the core test): ct_d_hors contract changed to `CM(NOCORE)` (the opposite of the real contract). tr-subject vs plant1 on `[0-9a-f]{8}`, `[0-9A-Za-z]{4}`, `[a-z]{4}`: all three print `ROW table=fd ... row=D-hors verdict=CHOSEN gate=PASS fields=-` in both. Plant compiler rc 0 (build ok), emitted x.c SAME (cmp) for `[0-9a-f]{8}`. So the contract clause can never refuse.

## SLOT-1 / SEAM-3 / SEAM-4 / CHECK-3 / HOUSE-5 (cluster)
Verdict: HOLDS, with a qualifier on (b): the refusal path exists but is unreachable today.
(a) HOLDS. `renders_pair` is declared at kit.h:545 and has exactly one constructor: window.c:1844 `fd_stop st = { w->set[w->stop_ix], w->off[w->stop_ix], 0, 0, 0, d->rate, &f, 1 };` (last initialiser, the literal 1). `grep -rn "renders_pair\|fd_stop\b"` over memfn/src, src, lib, cli finds no other constructor. The composer calls `fd_find(art, s, def, NULL, quiet, &pick, &rid)` (compose.c:313), st NULL. finder.c:665 `if (st->renders_pair) q.facts |= SF_ASKER_PAIR;` sits in the `if (st)` branch; the else branch (find_facts) never sets it. So SF_ASKER_PAIR == (st != NULL).
(b) HOLDS as stated. D-hors row (finder.c:257) keys on `SF_HORS_WINDOW | SF_HORS_DENSE`, set only by hors_facts (finder.c:638-643, called only in the `if (st)` branch), i.e. window facts only; no asker fact. compose.c fd_renderers[] (lines ~275-281) has rows for FF_LIBC, FF_LIBC_BACK, FF_WALK only; the comment at compose.c:269 says "PAIR and HORS: the window family's alone ... the composer refuses it". Refusal path: compose.c:313-325 `ra = rid ? fd_renderer(s, pick) : NULL; *row = rid; if (rid) { ... return NULL; }`. Qualifier: since the composer passes st NULL, SF_HORS_WINDOW is never set there, so the composer cannot pick HORS today; the refusal is a guard that the table shape (no asker discrimination on D-hors) would need if a composer asker ever set the window facts.
No plant (read-only static check).

## SLOT-2 / HOUSE-1
Verdict: HOLDS. Commands: `git grep -n "wf_brows\|wf_b_find\|wf_b_text\|bren"` at 20fb73159 and 9de5b5638 (memfn/src/window.c), and `git diff 20fb73159 9de5b5638 -U0 -- memfn/src/window.c | grep "^[+-].*(wf_brows|wf_b_find|wf_b_text|bren)"`.
A renderer row's actions now sit in three arrays plus bren branches:
- wf_brows (struct: row, holds, libc, path, prepare, basis): PRE-EXISTING (BASE window.c:1869, 4 rows B-fn..B-walk). NEW at 1e: row `[B_HORS] = {"B-hors", b_hors_holds, 0, "+hors", d_hors_prepare, ...}` (SUBJECT window.c:~1819), the `prepare` member (used at 1880 `if (wf_brows[fx->bren].prepare) ...`) and the `path` member (used at 1949).
- wf_b_find (SUBJECT window.c:2580, fn-pointer array, NULL for B-fn/B-hors): it is BASE's `wf_b_text` (BASE window.c:2650) RENAMED, pre-existing content; same _Static_assert against WF_NBROWS.
- wf_b_text (SUBJECT window.c:2705): NEW at 1e, a different array under the REUSED name (struct head/next/define: d_one_head/next, d_hors_head/next/define); NAME REUSE with a different type vs BASE's wf_b_text is a hazard for any diff reader.
- bren id branches: pre-existing `if (w->bren == B_FN)` (BASE 2789, 2826) and `B_PAIR` (BASE 2797); SUBJECT has them at 2727, 2735, 2764. No new bren branch; B_HORS is dispatched only through the arrays (b_hors_holds, prepare, wf_b_text[B_HORS]).

## SEAM-1
Verdict: HOLDS (at both trees).
Commands (4 compiles): `tr-{subject,base}/pcrec -p rx --features all -o VERIFY/s4/<t><n>.c --pattern '(?i)qzx'` (n=1) and `'(?i)qzx\b'` (n=2); records = `grep -E 'table=(fd|wfE)|FDROUTE|WPATH' err | grep -v REACH | md5sum`. All four compiles rc 0.
- tr-subject: n=1 and n=2 md5 both 1b1d5b051394076b8bd7b7219f79818d (equal); FDROUTE `row=PAIR arm=E-find`, WPATH `path=mass+pin arm=window-search fd=PAIR`, fd ROW D-hors PRED_FALSE, PAIR CHOSEN.
- tr-base: n=1 and n=2 md5 both 2a9da2b8075e5b00d2dc3d20d1f09d68 (equal to each other; differs from subject only by the new D-hors ROW line).
- Emitted C differs (same at both trees): n=1 has `ofsskip` x4 (B-fn: rx_mf1_ofsskip function), n=2 has `ofsskip` x0 and `rx_mf1_ha` x1 (B-pair inline two-stream). So equal records, different renderer; the renderer row is in no record. Not new at 1e (base has the same gap).

## SEAM-2
Verdict: HOLDS.
Commands (2 compiles, rc 0 both): `tr-{subject,base}/pcrec -p rx --features all -o VERIFY/s5/<t>.c --pattern 'a+b'`.
- tr-subject: `ROW table=fd art=1 site=1 phase=define row=D-hors verdict=PRED_FALSE gate=PASS fields=-` and the same for site=2, each followed by `row=D1 verdict=CHOSEN`; the sites are composer sites (FDROUTE `row=D1 arm=pf_memchr`).
- tr-base: the define-phase fd ROW lines are only the two `row=D1 verdict=CHOSEN` lines (site 1, site 2); zero `row=D-hors` lines of any kind.
So the composer's walk gains a D-hors line "PRED_FALSE" it can never answer (SF_HORS_WINDOW never set when st NULL, finder.c:659-665).

## CHECK-1
Verdict: HOLDS (both plants GREEN in both readers; the fabricated line is echoed as "mapped").
Plants (edited copies of tests/memfn/row_map.tsv at SUBJECT): VERIFY/map_noDone.tsv (the `wfD	D-one	-	-	1e` line deleted), VERIFY/map_fab.tsv (appended `zzT	zzR	fd	D1	1e`). No pcrec source change, so the plant compiler is the unchanged tr-subject/pcrec (rc 0 on every compile); no emitted-byte question (SAME by construction).
- reach_equal: `python3 -I tests/memfn/reach_equal.py --ref-bin tr-base/pcrec --bin tr-subject/pcrec --tree <review tree> --map VERIFY/map_X.tsv --patterns-file CHECK/pats4.txt --no-corpus --arms '' --jobs 2` (logs VERIFY/re_{good,noDone,fab}.log). All three end `reach_equal: LIMITED rc=0 keys=31 differ=0` (process exit 3 = LIMITED smoke). good prints `dissolved wfD/D-one ...`; noDone omits that line and is still green; fab prints `mapped zzT/zzR -> fd/D1: chosen BASE 2 HEAD 2 (all arms)`, a from-row that never occurs at BASE, accepted and echoed as mapped.
- rows_check section M: the critic's copy of rows_check.py with section C cut to 2 fd rows (VERIFY/rows_check_trim.py; section M untouched), `ROW_MAP_TSV=VERIFY/map_X.tsv ... --root <review tree> --cc gcc --tmp VERIFY/rc_X` with run_rows.sh's four FLOOR env vars. noDone: `row map: 1 lines ... checks passed: 161 checks failed: 0`, rc 0. fab: `row map: 3 lines, mapped-away tables ['wfD', 'zzT'] ... checks passed: 164 checks failed: 0`, rc 0.
- Source: rows_check.py:677-690 (M) checks only that (from) is no kit/rows.tsv row and (to) exists in both; nothing requires a line per moved row or that a from-row ever existed. Both readers GREEN for D-one deletion and the invented line.

## CHECK-2 plant B
Verdict: HOLDS.
Plant: the critic's CHECK/plantB (read-only reuse; `diff` against `git show 9de5b5638:memfn/src/window.c` is exactly one added line after the fd_find call, `+    if (fx->pick == FF_PAIR) fx->pick = FF_WALK;` at window.c:1847) and its traced twin CHECK/trPB (same one-line diff).
- Bytes: `x[Q%]y`, `--features all`, default arm: review-tree build/pcrec rc 0 vs plantB/build/pcrec rc 0; x.c differs (`cmp`: byte 2142, line 68; 8 diff lines) -> SILENT-MOVE (plant compiler rc 0).
- reach_equal: `reach_equal.py --ref-bin tr-subject/pcrec --bin CHECK/trPB/build/pcrec --tree <review tree> --patterns-file VERIFY/pat_xqy.txt --no-corpus --arms '' --jobs 2`: `rows base 31 head 31, patterns differing 0 ... reach_equal: LIMITED rc=0 keys=31 differ=0`. No difference shown for the pattern that moved bytes.
- rows_check (critic's trimmed copy, section C cut to 2 fd rows, --root CHECK/plantB, which holds tests/; trPB has none): see line below.
  rows_check: checks passed: 162
  rows_check: checks failed: 0

## CHECK-5
Verdict: HOLDS (3 fail / 3160 pass; SAB_DOC_FIGURE's 6fail/3155pass not reproduced).
Plant: VERIFY/plant8 = git archive 9de5b5638, S1079's SAB_BEFORE/AFTER applied to memfn/src/finder.c (count 1; line 683 `... (!st && !strcmp(fd_rows[d.terminal].id, "D1"))) return 0;   /* SABOTAGE S1079 */`), kit objects rebuilt into a copy of libpcrec.a, build/pcrec relinked, and build/pcrec-harness copied from the review tree (present: `ls plant8/build` = libpcrec.a pcrec pcrec-harness).
- Bytes (3 patterns, review-tree build/pcrec vs plant8/build/pcrec, `--features all`): `abc` rc 0/0 SAME, `a+b` rc 0/0 SAME, `x[Q%]y` rc 0/0 SAME. Plant compiler rc 0.
- ONE run: `bash VERIFY/plant8/tests/memfn/run_finder.sh` -> rc 1, `checks passed: 3160`, `checks failed: 3`: `FAIL: byte1t: decided by - ...`, `FAIL: hat1: decided by - ...`, `FAIL: 2 of 4 routed sites checked`. Log VERIFY/rf_plant8.log.
- tests/mech/sabotages/S1079_fd-d1-unrouted.sh SAB_DOC_FIGURE states "memfnfinder 6fail/3155pass (byte1t and hat1 decided by no row; the routed census and the lever cases under their floors)", measured at 7d5d6711c, not 9de5b5638. Measured here: 3fail/3160pass, no census/lever-case failure. Detection holds; the recorded figure does not match.

## CHECK-6 / SLOT-7
Verdict: HOLDS (pre-existing at BASE; unchanged by 1e).
Method: extracted `plant_spec` from `git show <rev>:memfn/tests/run_g2_win.sh` (BASE 20fb73159 and SUBJECT 9de5b5638), took the file and `from` anchor of S1405 (window.c) and S1410 (window.c), applied the script's own unescaping (`\\n` -> newline, `\\&` -> `&`, as at run_g2_win.sh:229-232) and counted occurrences in `git show <rev>:memfn/src/window.c`.
- 20fb73159: S1405 count 0; S1410 count 0.
- 9de5b5638: S1405 count 0; S1410 count 0.
- Controls through the same extractor at SUBJECT: S1425 count 1, S1400 count 1 (so the unescaping and file are right). window.c at SUBJECT holds the nearest text at 926/934 as `if (m->p[k].present ...) plan_add(...)`, not the anchored lines. The plant code's `s.count(a) != 1` makes `--plant S1405|S1410` fail with "the plant does not apply" (a setup failure, not a detection); `--plants` (PLANTS line 165) lists both. No compile of pcrec was needed.

## SLOT-5 / HOUSE-4
Verdict: HOLDS.
- plan_cost.def is expanded twice at SUBJECT, each time into an enum under a different prefix: memfn/src/finder.c:628-630 `#define MF_COST(name, value, unit, provenance, box, basis) FD_COST_##name = (value),` + `#include "plan_cost.def"`; memfn/src/window.c:72-73 `... WC_##name = (value),` + `#include "plan_cost.def"`. (plan_cost.def itself is not in the diff; `git diff --stat BASE SUBJECT -- memfn/src/plan_cost.def` is empty.) finder.c reads only HORS_MIN (FD_COST_HORS_MIN, hors_facts line ~641); the other FD_COST_* constants are defined and unused there; finder.c:625 comment says "window.c reads the rest of the table".

## EMIT-2 / HOUSE-3 / SLOT-4
Verdict: HOLDS (doc staleness; none of these files is in the 1e diff).
- memfn/src/plan_cost.def:22-23: "HORS_MIN (§3.3's last row) is D-hors's (window.c Table D), landed at S3 with its own deny `window-skip`." At SUBJECT D-hors is finder.c's row and `wf_dtable` is gone from memfn/src (git grep wf_dtable memfn/src: no hit).
- docs/design/memfn/window_site.md (unchanged BASE..SUBJECT): line 329 "### 2.5 Table D — the resume", line 331 "A `kit_table` on `kit_walk` [rev3.3 C7] (window.c `wf_dtable`), asked on E-find's text only", line 336 "...the resume, the file-scope table: `wf_d_text`"; §2.6 line 359 (E-find row): "...and Table D resumes it by D-hors or Table B decides its find...". All describe a table 1e removed. docs/design/memfn/units_inventory.md:55-56 likewise cites `wf_d_text` (:2602) and `d_hors_head/_next/_define`; tests/memfn/decider_census.py:64 does carry the 1e note ("Table D's `kit_walk(&wf_dtable` gone"), so the census was updated and the design docs were not.

## HOUSE-8
Verdict: HOLDS.
- tests/memfn/reach_equal.py:67-78 `read_map`: skips lines where `not ln.strip()` or starting `#`; needs `len(c) < 4` -> fatal `SystemExit`; reads columns 0-3 only (the `unit` column is ignored; extra columns accepted).
- tests/memfn/rows_check.py:130-141 `read_tsv(path, ncol)` called at :678 with ncol 5: skips only `not ln` (an empty line) and `#`; `len(c) != ncol` -> `bad(...)` (a recorded failure, line continues); columns 0-4 incl. `unit`.
- Demonstration (no compiles; both modules loaded by importlib, bytecode off) on a one-line 4-column map `wfD	D-hors	fd	D-hors`: `reach_equal.read_map` -> `[('wfD', 'D-hors', 'fd', 'D-hors')]` (accepted); `rows_check.read_tsv(..., 5)` -> `FAIL: map4col.tsv:1 has 4 columns, not 5` and `[]`. Two parsers, two column contracts (>=4 fatal vs ==5 recorded), whitespace-line handling differs too.

## Counts and notes
- pcrec compiles by me: about 10 (item 1) + 4 (item 4) + 2 (item 5) + 24 (three reach_equal --map runs, 4 patterns x 2 bins x 3) + 2 (item 7 bytes) + 2 (item 7 reach_equal) + 6 (item 8 bytes) = about 50 direct, plus the three trimmed rows_check runs (two map plants, one plantB; each reads "60 traced compiles/artifacts", of which the pcrec compiles are the fd-witness patterns and fixture runs; not individually counted, estimated well under the remaining budget). run_finder.sh: 1 run. reach_equal: always --no-corpus --jobs 2. No make, no box lock, nothing outside VERIFY/ written (plants are my archive copies plant1/plant8; plantB/trPB read-only).
- Denylist: nothing denied was opened.

## VERIFY COMPLETE

VERIFY COMPLETE
