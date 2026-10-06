# alphas3 — START-SET stage 3 (the DFA hat) Linux alpha, read

Lane `alphas3` (sonnet), 2026-10-06. Measurement and reading only; nothing under
`src/`, `tests/`, `docs/spec/`. Raw data and tables:
`docs/dev/optloop/startset/alpha_s3_results/` (its README names pin, box, protocol,
every file). Method copied from `alphas2_report.md`: the driver's own verdicts are read
against the identical-program control cells and a second `time`-only pass. D144 item 3:
regressions past the floor are issue rows, not reverts; this lane lists them (§6) and
files nothing.

## 0. Verdict

- **No wrong answer anywhere.** `alpha_s3.sh check`: `rc=0` (24 subject SHAs OK; W cells
  carry a `first-*` `RX_DFA_PREFILTER` and differ from BASE with DENY == BASE; C cells
  program-identical; base/new/deny answer identically on every subject). The extension's
  own `g1 check`: `rc=0` over all 89 manifest movers (5 arms on the 30 G1 movers, 3 on the
  rest, two subjects each).
- **IMPROVE: 6 of 7 named cell groups MET, reproduced to within 2% in a second pass; the
  seventh, the four `ctx-*` hybrids, REGRESSES (+4.0..+5.9%, both runs).** level-context is
  met (-80%). §2.1.
- **F3 at the dense movers (kv-quoted, wb-256/512, hex32-id): no loss** — sign 0 or better
  (kv-quoted null at the `memchr` floor, wb-256/512 -3..-5%, hex32-id -12.8%). §2.2.
- **The two one-byte null cells (grok 4 -> 3, float-literal 11 -> 10) are NOT null: they WIN
  by 10-11% and 6-7%.** The `T ⊊ E` admission's null cells therefore show the re-seed's fixed
  cost does not eat a one-byte narrowing (Q4, §4).
- **Q3, the G1 elision on a one-byte T:** elided is FASTER than keeping the pre-check on 41 of
  60 (mover x subject) cells in both runs (by 0.02-0.12 ns/B on a present byte, one pass
  instead of two). It is SLOWER than keeping, in both runs, on **9 cells beyond the
  program-identical null band** — all on byte-ABSENT, `memchr`-floor subjects, by +2.6..+9 ns
  per 64 KiB call (+0.4..0.5% of the cell; one `wordb_empty_compose` fixed-cost cell +33% of
  an ~8 ns call). Per D148 addendum 4's letter that is a G1 rule change to file; §3 gives the
  list, why no pattern-shape rule can separate them, and a recommendation (do not change G1;
  file the per-call term as an issue).
- **Regressions past the floor, reproduced (issue rows, §6):** I1 `ctx-*` on `bnd:t-letters`
  (an IMPROVE cell regressing), I2 the bench's `wild-logparse-syslogbase-expanded` (+3..6%),
  I3 corpus `\b[0-9a-f]{8}\b` (+7.5%), I4 a per-call entry term of +2.6..+9 ns on absent-byte
  G1 movers, I5 a short-call term on hit-at-offset-0 and the aws no-start-byte miss (+0.4..+4.4
  ns/call), I6 four sub-1.5% corpus movers.
- **K90 comparison (§5):** the DFA hat shows the same FAMILY of cost as the VM hat (a skip
  that cannot skip pays its entry / re-seed) but in a smaller and different shape: dense-subject
  loss is confined to T of 3..16 bytes at d_T 12-31%, not the large losses K90 L1 saw; the
  offset-0 short-call term is +1.4..+3.9 ns on the four hit-at-0 cells (K90 L3: +14..+17), and
  the 4.3 ns hit on aws's no-start-byte miss is a new, larger-in-relative-terms cell.

## 1. Protocol facts

BASE `5d47db6b` (abi 63), NEW `8148e034` (abi 64), DENY = NEW `-fno-start-set`.
ubuntubudu (Ryzen 5 1600), gcc 15.2.0, **glibc 2.43** (`ldd` 2.43-2ubuntu2.4), `taskset -c 2`,
scalar layer only (no `-fmemfn-simd`), governor schedutil / boost=1. Pre-run: load1 0.06,
`df -h /` 13 GB free. The driver `alpha_s3.sh` is unmodified, run as committed on main. The
box repo has neither commit, so both trees were `git archive`d here, copied to a scratch dir
under the gitignored `scratch_lx/`, built there, and the whole dir was removed afterwards (no
ref, no worktree created; the box's `git worktree list` is back to its 6 entries).

Run 1 and run 2 are the same artifacts timed twice (`alpha_s3.sh time`, then again ~38 min
later). The per-cell load gate (load1 < 0.5 before every cell) governs; the run-1 header
prints 1.63 (the build tail), run-2's 0.51. Deviation from "stop if >= 0.5 at start": none, the
box read 0.06 before launch.

**Extension.** `alpha_s3.sh` has 19 named cells and no per-call cells. D148 addendum 4 asks
for the 28 movers with and without the pre-check, and Q4's null cells, so
`alpha_s3_g1.py` (new, committed beside the driver) compiles every row of
`tests/startset/manifests/manifest_s3_dfa.tsv` (89 rows: 71 corpus + 18 bench; the
classifier reads `RX_REQ_WHY` and `RX_DFA_PREFILTER` off NEW and DENY) and times every mover
on its throughput subjects: base / new / deny, plus on the G1 movers `noreq`
(NEW `-fno-req-byte`, the ruled arm) and **`keep`**. `-fno-req-byte` alone does not give "hat
plus pre-check" (on a G1 mover NEW already has no pre-check, so it compiles to the same
program: `.text` byte-identical on all 30, `textsame` = Y), and no flag does: the `dominated`
row of `req_admits[]` is undeniable. `keep` is therefore a scratch build of NEW with one line
patched (`req_dominated_applies` returns false), never committed to any branch. `noreq` also
doubles as a direct program-identical null sample.

**What "the 28" is.** The classifier finds **30** `G1 emitted -> dominated` rows (29 distinct
pattern/option pairs): 28 corpus rows (ssbuild3's count) plus the bench's two aws rows
(`capability` and `litrun`, one pattern). aws is also alpha_s3.sh's `aws` cell.

**Corpus movers have no throughput subject of their own.** They are timed on the bench's
capability prose (`cap:t-64k`, `cap:t-1m`); read those cells as SCRATCH-tier population
evidence, not as a bench cell. Bench movers use their set's own subjects.

## 2. Cell-by-cell reading of the driver's cells (run 1 / run 2; ns/B; delta = new - base)

Source: `alpha_s3_results/main_cells.md`. Floors are the driver's |deny - base| (<= 0.006 on
every real mover).

### 2.1 IMPROVE

| cell (§7) | subject | base -> new | delta r1 / r2 | reading |
|---|---|---|---|---|
| aws (E 63 -> T 1, d 0.2%) | cap t-64k / t-1m | 2.886 -> 0.032 / 2.922 -> 0.053 | -2.854 / -2.851, -2.869 / -2.868 | MET (the `memchr` form, -98%) |
| json-constant (63 -> 3) | cap t-64k / t-1m | 3.008 -> 1.635 / 3.049 -> 1.630 | -1.373 / -1.367, -1.419 / -1.419 | MET (-45%) |
| dbnames (63 -> 14, d 22%; "may read null") | cap | 3.051 -> 2.726 / 3.112 -> 2.808 | -0.325 / -0.324, -0.305 / -0.303 | MET (-10%), not null |
| bignum (63 -> 10, d 12%; "may read null") | log t-064k / t-1024k | 2.750 -> 1.528 / 2.761 -> 1.560 | -1.222 / -1.225, -1.202 / -1.203 | MET (-44%) |
| hex32-id (63 -> 16, d 32%; "may read null") | log | 2.749 -> 2.399 / 2.757 -> 2.415 | -0.351 / -0.350, -0.341 / -0.345 | MET (-12.8%), not null |
| level-context (63 -> 3) | log | 2.412 -> 0.488 / 2.464 -> 0.488 | -1.924 / -1.924, -1.975 / -1.959 | MET (-80%) |
| ctx-lazy-64 (63 -> 3) | bnd t-letters-064k | 1.880 -> 1.970 | **+0.090 / +0.086** | **REGRESSION** (+4.8%) |
| ctx-lazy-256 | bnd t-letters-064k | 1.878 -> 1.965 | **+0.087 / +0.090** | **REGRESSION** (+4.6%) |
| ctx-lazy-1024 | bnd t-letters-064k | 1.880 -> 1.963 | **+0.083 / +0.067** | **REGRESSION** (+4.0%) |
| ctx-greedy-256 | bnd t-letters-064k | 1.858 -> 1.959 | **+0.101 / +0.110** | **REGRESSION** (+5.9%) |

The six MET groups reproduce in run 2 to within ~2% (aws -2.854 vs -2.851, json-constant
-1.373 vs -1.367). The four `ctx-*` cells are an IMPROVE target that regresses on the one
subject this alpha carries (`bnd:t-letters-064k`), in both runs, at 2-3 orders of magnitude
above the floor (0.0003-0.0025). Mechanism read from the emitted text (a diff of NEW against
DENY for `ctx-lazy-64`): the 63-byte word-class skip becomes a 3-byte set `{a,f,p}` skip with
the re-seed `if (scan_position > skip_from) forward_state = rx_forward_seed_state[...]`
after it; on all-letters text d_T is 11.9%, so a candidate arrives about every 8 bytes and
each pays the re-seed's two dependent loads for a DFA walk that dies in a byte or two. That
is §4.4's F3 regime (the re-seed least amortized), here at an expected-IMPROVE cell. The
design's own ctx evidence is the bench's SHORT-CALL subjects, which this alpha does not time
and the lane may not reverse-engineer (§7 Q-A); the throughput cell on letters is the
unfavourable subject.

### 2.2 F3: the DENSE movers (sign 0: flat, a loss up to the floor possible)

| cell | d_T | subject | delta r1 / r2 | reading |
|---|---|---|---|---|
| kv-quoted (T 27 / E 63) | 48% | log t-064k / t-1024k | -0.00001 / +0.00002; +0.00000 / +0.00000 | NULL at the `memchr` floor (0.0167 ns/B; r2's 64k "REGRESSION" is +0.1%) |
| wb-256 (T 26) | 78% | alt sparse / dense | -0.110 / -0.114; -0.109 / -0.113 | sign 0 met, better (-3%) |
| wb-512 (T 26) | 78% | alt sparse / dense | -0.201 / -0.204; -0.190 / -0.186 | sign 0 met, better (-4.5%) |
| hex32-id (T 16) | 41% | log | -0.351 / -0.350; -0.341 / -0.345 | better (-12.8%) |

No dense mover loses. The losses in §2.1/§6 sit at **d_T 12-31%**, not at the dense end: the
re-seed is paid per candidate, and at d_T above ~40% the machine rarely leaves its run so the
fixed cost amortizes (the design's §4.4 reading); the wins at d 78% are small (-3..-5%).

### 2.3 NULL cells (one-byte narrowings: "expected ~0, a re-seed fixed cost with a deny floor")

| cell | narrowing | subject | delta r1 / r2 | reading |
|---|---|---|---|---|
| quotedstring-grok | 4 -> 3 (d 0.5%) | cap t-64k / t-1m | -0.075 / -0.075; -0.077 / -0.078 | **WIN -10.5%**, not null |
| float-literal-bound | 11 -> 10 (d 12%) | cap t-64k / t-1m | -0.084 / -0.088; -0.098 / -0.098 | **WIN -6.1% / -6.8%**, not null |

Neither null cell loses. Their deny floors (0.001-0.003) are 25-70x below the effect. §4.

### 2.4 DO-NOT-REGRESS controls (C: NEW == BASE == DENY program text)

floor-byte, high-byte-run, uuid-near-miss, union-select are program-identical (the `check`
step), |delta| <= 0.00014 ns/B (high-byte-run, 0.04%; run 2 +0.00000 / -0.00009: flips sign).
The driver prints REGRESSION/WIN on several at the 1e-5 level (floor ~0.00001); alphas2 §2.4's
caution applies unchanged (a one-sample floor near zero turns layout wiggle into a verdict).
Reading: NULL. The control band for this box and pass: max |delta| 0.0001 ns/B on the C cells.

## 3. Q3 — the G1 elision on a one-byte T (D148 addendum 4)

Source: `alpha_s3_results/q3_per_mover.md` (every one of the 30 G1 rows x its 2 subjects, both
runs; columns: base / new / `-fno-req-byte` / keep, `new - keep` in ns/B and ns/call, the
program-identical null `|new - noreq|`).

**Counts (60 mover x subject cells):** elided FASTER than keep, both runs: **41**; SLOWER both
runs: **9**; NULL both: 2; mixed or one-run: 8. On every present-byte cell the elided form wins
by one pass: `new - keep` -0.020..-0.123 ns/B (e.g. `reseed.rxt:216` -0.091 / -0.123,
`spellings.rxt:88` -0.079 / -0.093, `lookbehind.rxt:107` -0.044 / -0.052, `gating.rxt:120`
-0.020 / -0.033). aws, the one bench mover, reads -0.002 / -0.001 (its pre-check and hat are
the same single `memchr`; 4 of 4 cells NULL or FASTER, never SLOWER). The null band
(`|new - noreq|`, same program, same launches) is <= 0.0003 ns/B everywhere, and `.text`
byte-identical on all 30.

**Cells where the elided form is slower than keep beyond that band, reproduced in both runs
(each a "list each such cell" entry):**

| mover (pattern) | subject | new vs keep, ns/B r1 / r2 | ns/call r1 / r2 | program-identical null r1 / r2 |
|---|---|---|---|---|
| `tests/lookaround/d27/matrix.rxt:1524` `(?<!a)z` | cap t-64k | +0.00006 / +0.00006 | +3.9 / +3.9 | 0.00000 / 0.00001 |
| `matrix.rxt:1564` `((?<!a)z)` | cap t-64k | +0.00009 / +0.00009 | +5.9 / +5.9 | 0.00000 / 0.00002 |
| `matrix.rxt:1564` | cap t-1m | +0.00001 / -0.00001 | +10.5 / -10.5 | (sign flips: not a reproduction) |
| `matrix.rxt:1576` `(?>(?<!a)z)` | cap t-64k | +0.00009 / +0.00010 | +5.9 / +6.6 | 0.00000 / 0.00001 |
| `matrix.rxt:1584` `(?<![ab])z` | cap t-64k | +0.00006 / +0.00007 | +3.9 / +4.6 | 0.00000 / 0.00000 |
| `matrix.rxt:1624` `((?<![ab])z)` | cap t-64k | +0.00008 / +0.00009 | +5.2 / +5.9 | 0.00001 / 0.00000 |
| `matrix.rxt:1636` `(?>(?<![ab])z)` | cap t-64k | +0.00009 / +0.00014 | +5.9 / +9.2 | 0.00000 / 0.00000 |
| `matrix.rxt:1636` | cap t-1m | +0.00002 / +0.00002 | +21 / +21 | 0.00000 / 0.00001 |
| `tests/assertions/wordb_empty_compose.rxt:1168` `\Bo\Z` | cap t-64k | +0.00004 / +0.00008 | +2.6 / +5.2 | 0.00000 / 0.00001 |

(The `matrix.rxt:1584` / `1624` 1m cells and `matrix.rxt:1524` / `1564` 1m cells read
SLOWER in one run and NULL or FASTER in the other, so they are not listed as reproduced.
`dfahat.rxt:437` 64k reads NULL in run 1 and +0.0056 (+0.8%) in run 2 inside the cell's
own floor 0.0026-0.0040: not reproduced.)

**Reading.** These are the byte-ABSENT, `memchr`-floor cells. The pattern's one start byte (`z`,
`o`) does not occur in `cap:t-64k` / `t-1m`, so keep (pre-check `memchr` finds nothing, returns)
and new (the hat's `memchr` finds nothing, returns) both pay ONE pass over the subject, the cell
reads 0.0167 ns/B, and the whole difference is the entry cost around that one pass: +3.9..+9 ns
per 64 KiB call, +0.4..+0.5% (at 1 MiB it is lost in the noise except `1636`). The same cells
read the same sign against BASE (NEW vs BASE: +4.6..+6.6 ns/call, 0.42-0.54%, reproduced), so
this is the hat's per-call entry term, K88/K90-L3's family, not something G1 adds. The
wordb_empty_compose cell is a fixed-cost call (~8 ns, the pre-check answers before the scan
starts), so +2.6..+5 ns reads +33% of it; at 64 KiB throughput scale that is 0.00004 ns/B.

**Ruling's letter vs substance.** D148 addendum 4 says: slower on any cell beyond the
program-identical null band -> "G1 KEEPS the pre-check for that shape". By the letter, the table
above trips it for nine cells. Three things argue against a G1 rule change, offered as the
reading for the manager's call, not as a ruling:
1. The shape is not separable at compile time. The tripping cells are two-byte-or-three-byte-E
   lookaround patterns whose T byte is ABSENT from this text; other patterns of the identical
   compile-time shape (`alpha_spellings.rxt:129`, `lookbehind.rxt:107`, T 1 / E 2) have the byte
   PRESENT in this text and win by 0.044-0.052 ns/B. G1 cannot see the subject. Keeping the
   pre-check for the shape would forfeit those 41 wins (2-12% on 28 corpus rows, plus the
   per-pass saving everywhere a byte is present) to remove a 0.4% / ~5 ns per-call term.
2. The effect is a fixed per-call term of single-digit ns, the same family as I4/I5 below, which
   alpha_s2's K90 L3 already put under a separate entry-cost fix (a first-position check, a
   density-adaptive disarm), not under G1.
3. The bench's one G1 cell (aws, both aws rows) is NULL-or-FASTER at all four cells.
Recommendation: leave G1 as built, file the per-call entry term once (I4/I5), and have the
manager decide whether the letter of the addendum is meant to bind at 4-9 ns / 0.5%.

## 4. Q4 — the `T ⊊ E` admission's null cells

The admission admits a one-byte (or two-byte) narrowing with no margin; D149 labels it an
unmeasured default. Population: the driver's two cells plus every manifest mover with
|E| - |T| in {1, 2} (`kind` `Q4n` in `all_movers.md`: 7 cells x 2 subjects) plus the 30 G1
movers with E = 2 or 3 (also one- or two-byte narrowings).

| cell | T / E | d_T | delta r1 / r2 (ns/B) | reading |
|---|---|---|---|---|
| grok | 3 / 4 | 0.5% | -0.073 / -0.077 (-10.3%) | WIN |
| noatomic | 3 / 4 | 0.5% | -0.074 / -0.070 (-12.2%) | WIN |
| float-literal-bound | 10 / 11 | 12% | -0.086 / -0.088 (-6.3%) | WIN |
| `matrix.rxt:1548`, `dfahat.rxt:591` | 2 / 3 | 0.6% | -0.533 (-50%) | WIN |
| `matrix.rxt:1608`, `dfahat.rxt:626` | 2 / 4 | 0.6% | -0.60 (-53%) | WIN |
| G1 movers E = 2 | 1 / 2 | 0.5-2% | -0.89 .. -0.95 (-58..-85%) | WIN (and Q3 above) |

**Verdict: no one- or two-byte narrowing loses.** The admission's null cells read as gains of
6-13% (grok, float-literal) and 50% (two-byte E), against floors of 0.001-0.008 ns/B. The only
reproduced absent-byte losses in this population are the sub-0.6% I4 per-call term above. So
the admission can stay as built on this evidence; its remaining unmeasured edge is a subject
where the narrowed byte is dense (not covered: d_T for these cells is 0.5-12%).

## 5. K90 comparison (the VM hat's dense / offset-0 costs, `known_issues.md` K90)

| K90 shape | VM hat (alphas2) | DFA hat (this alpha) |
|---|---|---|
| L1: improve cell regresses on its own match-DENSE subject | quoted-delim dense: +0.84..+0.91 ns/B (+8%) | **yes, smaller and narrower:** ctx-* on letters +4..6% (d_T 12%), syslogbase-expanded +3.2..5.8% (23%), `\b[0-9a-f]{8}\b` +7.5% (31%). At d_T >= 40% the hat wins or ties (hex32-id -12.8%, kv-quoted 0, wb -3..-5%). |
| L2: match-dense `a(\w)\1` d 33% / 80% | +0.37..+0.53 ns/B | not measured (no VM-style backref cell in this alpha); the d_T 12-31% movers above are the DFA analogue |
| L3: hit at offset 0, short call | +14..+17 ns/call on 4 of 75 subjects | **same sign, ~4x smaller** (§5.1) |

### 5.1 Synthetic short-call probe (SCRATCH tier, `alpha_s3_short.py`)

alpha_s3.sh times throughput only (its `PERCALLS` list is empty; the CTX short-call subjects
are the bench's, owed by the pcrec-bench-dev rule). To answer "does the DFA hat show the same
offset-0 shape" at all, five of its own cells' artifacts were called once per timed call on
hand-written short subjects of four shapes (hit at offset 0, hit after a 40-byte filler,
start bytes present but no match, no start byte). Absolute ns/call (new - base), two passes:

| cell | hit0 | late hit | miss, T present | miss, no T |
|---|---|---|---|---|
| aws | **+3.4 / +3.5** (110.5 -> 113.9) | -80.3 / -79.7 | **+5.9 / +4.9** | **+4.3 / +4.4** (8.6 -> 12.9) |
| json-constant | +0.4 / +0.5 (18.2 -> 18.5) | -56.3 / -57.2 | -18.4 / -18.6 | -84.5 / -84.6 |
| level-context | **+3.4 / +3.9** (186.7 -> 190.2) | -51.0 / -52.1 | -50.8 / -50.2 | -88.0 / -88.1 |
| grok | -36.2 / -34.5 | -38.0 / -35.7 | -71.2 / -71.2 | +0.7 / +2.5 (run-1 NULL, run-2 floor 0.008) |
| ctx-lazy-64 | **+2.0 / +1.4** (68.0 -> 70.0) | -62.0 / -64.0 | -11.1 / -11.9 | -79.1 / -78.7 |

Reading: the offset-0 shape is present (4 of 5 cells read +0.4..+3.9 ns on a hit at offset 0,
2-4% of a ~70-190 ns call, 4-10x smaller than K90's L3 +14..+17 ns), and everywhere else the
hat wins big (-11..-88 ns). The new cell is **aws's no-start-byte miss: +4.3 ns on an 8.6 ns
call (+50%)** and its start-byte-present miss (+4.9..+5.9): for a G1-elided pattern the hat's
seek replaces the pre-check, so on the miss path NEW pays the hat's entry where BASE answered
from the pre-check. It is the same +4..+6 ns/call entry term §3 found at throughput scale on
the absent-byte movers. Subjects are synthetic, one call shape each; the numbers are directional
for the bench's real short-call subjects, which remain owed.

## 6. Issues for the manager (D144 item 3; not filed by this lane)

| id | cell | delta (r1 / r2) | evidence |
|---|---|---|---|
| **I1** | ctx-lazy-64/256/1024, ctx-greedy-256 on `bnd:t-letters-064k` (IMPROVE cells, 63 -> 3) | +0.090 / +0.086, +0.087 / +0.090, +0.083 / +0.067, +0.101 / +0.110 ns/B (+4.0..+5.9%), floor <= 0.0025 | `main_cells.md`; the F3 regime at d_T 11.9%; the design's own ctx evidence is short-call subjects, unmeasured here |
| **I2** | bench `wild-logparse-syslogbase-expanded` (T 16 / E 63) | cap t-64k +0.122 / +0.092 (+4.2% / +3.2%); t-1m +0.170 / +0.171 (+5.8% / +5.8%), floor 0.002-0.004 | `all_movers.md`; a bench capability pattern, not in alpha_s3.sh's cells; d_T 22-23% |
| **I3** | corpus `\b[0-9a-f]{8}\b` (`offset_skip.rxt:255`, T 16 / E 63) | cap t-64k +0.215 / +0.222; t-1m +0.229 / +0.235 (+7.1..+7.7%) | `all_movers.md`; d_T 31%; the bench's `hex32-id` (`{32}`, same T, log subject) wins -12.8%, so the loss is subject- or length-specific |
| **I4** | absent-byte one-byte-T movers, `memchr`-floor (`matrix.rxt:1524/1564/1576/1584/1624/1636`, `wordb_empty_compose:1168`, `reseed.rxt:176`) vs BASE and vs keep | +3.9..+9.2 ns per 64 KiB call (+0.4..+0.5%); +2.6..+5.2 ns on a ~8 ns fixed-cost call | §3; the same term vs BASE (hat's entry) and vs keep (the Q3 letter) |
| **I5** | short call, hit at offset 0 / no start byte, G1-elided aws and the ctx/level/json cells | hit0 +0.4..+3.9 ns; aws no-start-byte miss +4.3 ns (+50% of 8.6 ns), aws T-present miss +4.9..+5.9 | §5.1, SYNTHETIC subjects |
| **I6** | corpus `(?i)\bcat\b` (`word_boundary.rxt:91`, `dfahat.rxt:1031`, T 2), `dfahat.rxt:1074` (T 27) | +1.2% / +0.8% at 64k (+0.2% at 1m); +1.5% / +1.3% | `all_movers.md`; sub-1.5%, reproduced; judged NULL in substance (alphas2 L4 shape), listed because they clear the driver floor |

I1-I3 are the same family (a re-seed paid per candidate at moderate density); I4/I5 the same
(a per-call entry term); neither is a wrong answer, and all have the interim lever
`-fno-start-set` (bit 47), which restores the base program on every one of them (DENY == BASE
program text). Candidate fix shapes are K90's, unchanged (a first-position check; a
density-adaptive disarm): D77 says a design pass with §4.4's cost model comes first.

## 7. Open / not done / questions to relay

- **Q-A (bench, relay; never reverse-engineered here):** (a) which subject does the bench time
  the litrun `aws` cell on, and how dense is `A` there (alpha_s3.sh's aws reads 0.2% on
  `cap:t-1m`); (b) do the CTX cells' short-call subjects contain the context bytes (`E \ S`)
  the re-seed restores; I1 says the `bounded` throughput subject's letters hit T every ~8 bytes,
  so what are the bench's `ctx-lazy-*` subjects' T density and the expected per-call count.
- `-fmemfn-simd` layer: not built at this pin; scalar only (stated in the driver header).
- The short-call probe is synthetic and one-call-shape; the bench's real short-call cells are
  the arbiter for I5.
- I did not repeat beyond two passes; the two agree on every IMPROVE delta to within ~2% and
  on every issue row's sign and size to within ~10% of run 1.
- `keep` is a scratch patch; if the manager wants a shipped way to pin the pre-check under the
  hat for a future A/B, G1's `dominated` row would need a deny bit (it has `0` today).

## 8. Box state and housekeeping

Work dir `/home/duxevents/pcrec/scratch_lx/alphas3` (513 MB) created and removed; the box repo
has no new refs or worktrees; `git status` there shows only the pre-existing
`.final_lx_keep/`. **The last box run ended 2026-10-06T17:26:18Z** (`chain2.log`
`ALL2_DONE`); the box was idle (load1 0.12) when checked after cleanup. One slip on this Mac:
the first `git archive -o` wrote two tarballs into the main tree root for about a minute
(relative-path `-o` under `git -C`); moved into this worktree's gitignored `build/scratch/`
before any commit and removed at the end; nothing in the main tree was committed or modified.
