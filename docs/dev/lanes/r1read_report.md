# r1read — [OPTLOOP] round 1 Linux alpha results, read (2026-10-04, lane r1alpha continued, sonnet)

Reads the serial driver of `r1alpha_report.md` (outputs `scratch_lx/r1alpha/{vedge,c1,c3,a2}.out` on
ubuntubudu, gcc 15.2, `taskset -c 2`, quiet box) under D144 + addendum 1: ABSOLUTE deltas beside the
floor |DENY - BASE| (the same program twice); inside the floor = NULL; ns-scale never a percentage.
Verdict labels below are the scripts' own (WIN / NULL / REGRESSION = delta past the floor); the
"readings" are mine. Not merged, not pushed.

## Verdicts (summary)

| item | verdict |
|---|---|
| [OPT-VEDGE] | **Win confirmed on Linux, NOT closeable clean.** Big absolute wins on runs (as predicted), but the short-call entry term is confirmed past the floor (+1.3 to +8.7 ns) AND three larger regressions appear that the Mac read did not size: `base10num-grok` mix4k/hex4k (+4.2 / +6.6 us), `upto-1024` mix4k/hex4k (+537 / +199 ns), `upto-256` mix4k (+78 ns). File issue rows; `-fno-view-edge` is the interim switch. |
| S4 C1 `overlap` | **Keep default-on (weak).** Re-run read at its own deny arm: WIN beyond the floor on 8 of 15 witness cells, largest -0.035 ns/B (lit-l3 lbf), -0.030 (l10 mat), -0.021 (l7 fbf); one witness loss, lit-l3 fbf +0.017. Slack/router wins are tiny (-0.0003 to -0.0017 ns/B). Not a clean win: the byte-identical controls themselves move up to +0.013 ns/B. Q3 asks for "a win beyond the floor": met on 3 lit cells even against the controls' spread. |
| S4 C3 | **Predicted win lands, but 7 mover witnesses LOSE** (past the floor, by large absolute amounts). union-select: -0.40..-0.52 ns/B (base 0.75 -> 0.26-0.35; prediction was ~0.43). Regressions: `userpass` +0.92..+0.95 ns/B (0.0168 -> 0.96, a 57x slowdown), `mod-i`/`mod-r` +0.59..+0.70, `cls-fold-pair`/`cls-pair-ctl` +0.32..+0.41, `ci-strasse` +0.08..+0.10, `alt-shared` +0.08..+0.11. New issue rows per D144 item 3; bit 44 (`-fno-req-run-fold`) is the interim switch. |
| A2 (`[OPT-HYB-RESEED-FORM]`) | **DROP** (no form passes the rule on both compilers). Not built. |

## 1. VEDGE (RC 0; BASE 74017b71, NEW 8562ff3a, DENY = NEW + the three deny flags)

`check`: DENY == BASE on all 14 cells; NEW == BASE on the unmoved control `qnt-dot-bounded`. Cell
timings are in `scratch_lx/r1alpha/vedge.out` (6 subjects x 14 cells, 5 interleaved launches). The
floor is 0.00-0.3 ns on short cells, up to 32 ns on the 4k-subject `\w`-class cells.

Wins (ns per call, base -> new): `cls-upto-N\z`, whole-subject calls.

| cell | short | l4k | prose64k |
|---|---|---|---|
| upto-16 | 56.4 -> 29.2 | 56.3 -> 29.3 | 34.4 -> 24.8 |
| upto-64 | 147 -> 75 | 235 -> 105 | 123 -> 69 |
| upto-256 | 147 -> 75 | 940 -> 332 | 578 -> 239 |
| upto-1024 | 147 -> 75 | 3768 -> 1240 | 2638 -> 1176 |
| upto-4096 | 147 -> 75 | 15110 -> 4865 | 12661 -> 5941 |
| cls-w | 111 -> 56 | 9167 -> 2891 | 212631 -> 144503 |

Prediction (vedge report §5, Mac scratch: x3.1-4.4 for N >= 64): confirmed in direction and size on
Linux (l4k x3.1 at N = 4096, x3.6 at N = 1024; prose64k x2.1-2.2). Also wins: `hex32` on digit/hex
runs (-69 ns), `dig-exact-16` on dig40 (-26 ns).

Regressions past the floor, short non-matching subjects (the predicted fixed entry term, "+0.7 to
+4 ns"): `floor` +1.75 (Mac said +0.7), `year4` +3.6 (Mac +3.6-3.8), `dig-exact-16` +3.4 (Mac
+3.7-4.6), `upto-4/-16/-64..` dig40 +0.9..+3.5, `hex32` short +8.7 / l4k +3.1 / prose +7.0 (Mac
+4-5). All clear their floors (0.00-0.25 ns), so per D144 add.1 rule 3 these become issue rows.
`hex32` short (+8.7) is above the predicted band.

Regressions NOT predicted at this size (real-scale, not ns-noise): 

| cell/subject | base -> new ns/call | delta | floor |
|---|---|---|---|
| base10num-grok mix4k | 6031 -> 10233 | +4202 | 40 |
| base10num-grok hex4k | 7702 -> 14265 | +6563 | 1.3 |
| upto-1024 mix4k / hex4k | 1507 -> 2044 / 1591 -> 1790 | +537 / +199 | 2.1 / 0.5 |
| upto-256 mix4k | 332 -> 410 | +78 | 0.9 |

The Mac read had `base10num-grok` mix4k at +27%; Linux shows it much worse and on hex4k too (not on
the Mac list). The mix/hex subjects have short runs interleaved with breaks, i.e. the edge path re-entered
per run. Hypothesis only, not diagnosed here.

`qnt-dot-bounded`: NEW == BASE artifact, deltas +0.07..+1.7 ns on 80-116000 ns cells = NULL/noise (the
two "REGRESSION" labels at +0.85 ns on 7271 ns are within 0.01% and are the instrument).

Caveat: the log header line shows load1 = 1.07 at start (the per-cell load wait only gates later cells).

## 2. C1 (first run RC 1; fixed; re-run alone)

Diagnosis: the failure was the hand-twin step, not the compiler. At 8562ff3a C3 turns `slack-nocaps`'s
required run into ONE masked word compare, `(rx_w8(subject + cand) & rx_w8("\337..")) == rx_w8("RVICES/T")`;
there is no `A == B && C == D` pair left for the fused-spelling sed, so `TWIN NOT APPLIED` (exit 1). The
twin is moot for that cell. Fix (commit on lane/r1alpha, `alpha_c1.sh`): a twin with no anchor is reported
`TWIN SKIPPED` and its fused arm dropped, not fatal; `check` skips it. `lit-l7-vm`'s twin still applies
(2 fused lines). Re-run: `build check time` (step0 reused), CPU 2, gnutimeout, box idle (load 0.16 at
launch, 0.44 at the time step). `check`: DENY == BASE on all 12 cells, answers identical.

BASE = 14e78104 (pre-C1), NEW = 8562ff3a (C1 + C3), DENY = NEW + `-fno-run-overlap -fno-req-run-fold`.
Because DENY == BASE, new-vs-base is the C1+C3 effect on a cell where C3 did not move the artifact
(lit-*, router) and C1+C3 on slack (C3 moves slack, so its delta is not C1-isolated).

Witnesses (ns/byte; delta = new - base; floor = |deny - base|):

| cell | subject | base | new | delta | floor | label |
|---|---|---|---|---|---|---|
| slack-nocaps | t-1m / t-256k / t-64k | 0.2512 / 0.2472 / 0.2251 | 0.2501 / 0.2462 / 0.2234 | -0.0011 / -0.0010 / -0.0017 | 0.00013-0.00017 | WIN x3 |
| router | t-1m / t-256k / t-64k | 0.2526 / 0.2465 / 0.2225 | 0.2522 / 0.2463 / 0.2224 | -0.0004 / -0.0003 / -0.0001 | 0.0002 / 0.0003 / 0.0001 | WIN / NULL / NULL |
| lit-l3-vm | mat / fbf / lbf | 2.759 / 1.856 / 1.902 | 2.759 / 1.873 / 1.868 | +0.0002 / +0.0171 / -0.0349 | 0.0002 / 0.0026 / 0.0027 | REG(tiny) / REG / WIN |
| lit-l7-vm | mat / fbf / lbf | 1.1855 / 0.7992 / 0.8202 | 1.1855 / 0.7778 / 0.8199 | -0.00003 / -0.0214 / -0.0003 | 0.00015 / 0.00035 / 0.0008 | NULL / WIN / NULL |
| lit-l10-vm | mat / fbf / lbf | 1.3627 / 0.5799 / 0.0167 | 1.3332 / 0.5765 / 0.0167 | -0.0296 / -0.0035 / 0.0000 | 0.00004 / 0.0002 / 0 | WIN / WIN / (0.0000) |

Controls (byte-identical artifacts, 18 cells; keyword-ctl, lit-l2/l4/l8/l16/l31/l40): deltas -0.0011 to
+0.0132 ns/B; 10 of 18 labelled REGRESSION/WIN against floors of 0.0001-0.0003 although the artifacts are
byte-identical. That is code-layout/alignment spread, a SECOND floor of about 0.013 ns/B (worst: lit-l40
mat +0.0132, its own floor 0.0076). Read against 0.013: the lit-l3 lbf (-0.035), lit-l10 mat (-0.030)
and lit-l7 fbf (-0.021) wins stand; lit-l3 fbf (+0.017) is a marginal loss of 0.9% opposite in sign to
its lbf sibling (layout-like); slack/router wins are below that spread.

Fused twin (Q10 input), lit-l7-vm only: fused - new = +0.0003 / -0.0068 / -0.0491 ns/B (mat / fbf / lbf);
the `|` spelling is faster on two of three cells (lbf by 0.049 = 6%), null-ish on mat. Slack twin moot.

Q3 reading: C1 keeps its `overlap` row default-on. The case is weak and rests on the lit VM family (3
cells beyond even the control spread, one marginal loss); on the production-shaped cells (slack, router)
it is at most a ~0.001 ns/B (0.4%) win, which is not a reason to flip it off.

## 3. C3 (RC 0; BASE a588c668 abi 58, NEW 8562ff3a, DENY = NEW + `-fno-req-run-fold`)

`check`: DENY == BASE on all 19 cells. Full data in `scratch_lx/r1alpha/c3.out`; ns/B, floor in
parentheses.

| cell | subject | base | new | delta (floor) | vs prediction |
|---|---|---|---|---|---|
| union-nocaps | 64k/256k/1m | 0.759/0.834/0.745 | 0.257/0.315/0.348 | -0.502/-0.519/-0.397 (0.008/0.084/0.002) | predicted ~0.43 from 0.718: beaten at 64k/256k |
| union-caps | 64k/256k/1m | 0.750/0.751/0.753 | 0.258/0.316/0.348 | -0.493/-0.436/-0.405 | same |
| slack nocaps/caps | 64k-1m | 0.226-0.254 | 0.224-0.250 | -0.0025..-0.0044 (0.0000-0.0003) | "faster or null": WIN, tiny |
| http-5xx | 4 log subj | 0.022-0.166 | 0.021-0.165 | -0.0005..-0.0013 | "null expected": tiny WIN |
| ci-ascii-ctl | u8 x3 | 0.69-0.72 | 0.19-0.27 | -0.45..-0.50 | (a mover, unlisted in the table) WIN |
| **userpass** | cap x3 | 0.0168 | 0.94-0.97 | **+0.92..+0.95** (0.0000) | not predicted |
| **mod-i / mod-r** | syn x3 | 0.94-0.99 | 1.57-1.67 | **+0.59..+0.70** | not predicted |
| **cls-fold-pair / cls-pair-ctl** | syn x3 | 0.57-0.61 | 0.89-1.03 | **+0.32..+0.41** | not predicted |
| **ci-strasse** | u8 x3 | 0.666-0.694 | 0.757-0.797 | **+0.080..+0.103** | not predicted |
| **alt-shared** | u8 x3 | 0.066-0.115 | 0.145-0.226 | **+0.079..+0.112** | not predicted |
| controls sleep/dbnames/concat/stackframe/kvquoted | cap, log | -- | -- | -0.36..+0.13 (concat: +0.13 vs floor 0.085, -0.36 vs 0.33) ; others <= +0.009 | noise, as predicted |

union-srch per call (75 short subjects, ns/call): wins on ~40 cells (largest -44 sec-github-pat, -28
sd-empty-alt, -17.5 slack-webhook, -15.9 lp-syslog) and REGRESSIONS past the floor on ~35 cells,
mostly +2.4..+4.4 ns on 6-10 ns calls (a fixed entry term of the new pair/word loop: base 6.5-7.7 ns ->
10.06 on many), worst +11.0 waf-dbnames, +8.7 waf-union, +7.9 rec-tag-depth3, +7.6 waf-comment-obfuscation,
+7.4 sd-keyword-short, +6.7 la-email-dotdot. The design's expectation ("within the floor, or a regression
row", F1/F6 per-call-constant risk) is met by the second branch: file the row. NULL: waf-sleep,
v-uuid-badnibble.

Mechanism seen for `userpass` (artifact diffed): BASE rejects with `memchr('=')` (REQ_BYTE 61, none in the
text); NEW's REQ_RUN `55534552@0/dfdfdfdf` (`USER`, caseless) replaces it with a two-stream memchr(U,u)
plus a masked compare, and 'u'/'U' are common in the text, so the guard now costs a hit per 'u'. i.e. the
single information ranking prefers the 4-byte caseless run over a rare exact byte. That is the likely
shape of the other regressions (mod-i/mod-r etc.: a masked run chosen over a cheaper scan); not
diagnosed here.

C3 verdict: WIN on its predicted customer (union-select, ci-ascii-ctl) and a net-per-byte loss on 7
unlisted movers that are large in absolute terms. Per D144 item 3 these are issue rows; the interim switch is
bit 44. Whether C3 stays default-on until the rows are fixed is the manager's ruling.

## 4. A2 (RC 0 in ~16 s: not suspicious)

- `a2.out`: `bakeoff: timed lpatom/s:br-doubled-word+74 gcc (iters 18657, answers same)` and the clang row
  (iters 15625). Not skipped by the per < 1 ns guard, no ROWCAP cut. Calibrated iterations are ~16-19k
  (about 50 ms per launch at ~700 ns per pass), 15 launches x 5 variants x 2 compilers: ~16 s is the
  right order. The old ~3 min was the bug's 50,000,000 iterations.
- `table.txt` is complete: `timed rows: 40 of 40`; `raw.tsv` has 150 lines for lpatom (15 launches x 5
  variants x 2 compilers). `answers: same on every row`.
- Rows 1-38 untouched: `diff` of `raw.tsv` minus lpatom against `raw.before_only.tsv` minus lpatom = 0 lines.
- Overrun scan (caps[1][2] bug): of the 19 labels, only `lpatom` has a capturing group (`(.*)`). The other
  patterns, `a?+a`, `item(?= done)`, `item(*pla: done)`, `item(?! done)`, `(?*item)item`, `(?>a|ab)c`,
  `(?<=a|é)x`, `(?<=é)x`, `(?<!日)本`, have none (the atomic/lookaround groups do not capture), so
  `caps[1]` was large enough for them. Nothing to re-time; no ONLY= rerun was needed beyond lpatom.
- lpatom (A1's own cell; a = main, d = branch, both ns per set pass): gcc a/d = 1.089 (775 vs 712 ns,
  floor 0.1%): A1 wins about 63 ns/pass; clang a/d = 0.965 (a 24 ns faster, floor 2.5%): beyond the floor,
  A1 loses on clang. Side finding, not the A2 decision.

A2 decision rule (a2build_report): every improve row at or under 1 + floor on BOTH compilers, no keep
row losing more than its floor against `a`, floor = max(launch spread, |aL/a - 1|); UNMEASURED rows
(layout floor > 10%: clang possq-f, lkapos-f, lkaverb-f, lbvar gap64/bursty) excluded. Failing rows per
form/compiler (of 14 clang / 19 gcc measured rows):

| form | gcc fails | clang fails |
|---|---|---|
| ai | 7 | 2 |
| f1 | 10 | 9 |
| f1i (best) | 3 (lkaneg-s, atalt-s, atalt-f) | 6 (possq-s, lkaneg-s, atalt-s/f, lbfix-f improve and keep) |
| f3 | 14 | 9 |
| f3i | 8 | 5 |

No form passes on both compilers (the closest, f1i, fails 3 + 6 rows, including clang possq-s, the
deciding O-81 cell, which also fails ai/f1/f3/f3i). **Verdict: DROP**; consistent with a2build's round-1
read, now over all 40 rows. The short-search rows are ns-scale (13-36 ns/call), so the
absolute-delta caution of D144 add.1 applies to their ratios as well; the decision does not hinge on them:
clang possq-s fails by a wide margin and the layout-floor-unmeasured rows are excluded, not counted against.

## Re-ran / changed

- C1 only, alone, on Linux (new `scratch_lx/r1alpha/rerun_c1.sh`, `c1.out`; the failed first output kept as
  `c1.first_failed.out`; `alpha_c1.sh` copied to `scratch_lx/r1alpha/`). Step0 not repeated (its output was
  produced in the first run).
- Nothing else re-timed. No A2 rerun (no capture groups outside lpatom). No files outside the worktree and
  `scratch_lx/` were touched (one stray empty `/tmp/x` scratch dir and a /tmp table copy were created and
  removed by this lane in error).

## Caveats

- Single box, single CPU, 5 launches per cell (A2: 15); layout spread is a second floor (C1 controls show
  0.013 ns/B; the stated floor does not capture it).
- C1's NEW includes C3; only the lit-* and router cells are C1-isolated by artifact identity (C3 did not move
  them), slack is not.
- The C3 per-call cell compares against abi 58 BASE a588c668; VEDGE base 74017b71. Different bases per item
  by design (alpha_*.sh).
- Causes proposed above (edge re-entry, ranking) are readings of the emitted text, not measured.
