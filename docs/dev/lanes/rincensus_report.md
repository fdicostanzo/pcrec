# rincensus: reverse-inner stage 1's deciding census, and the model gaps the critic named

**Lane `rincensus`, 2026-10-11, sonnet. Census + model + docs only: nothing under `src/`.**
Pin: `build/pcrec` of main `4fd394f2` (abi 74, `pcrec 0.2.0-beta`), Linux dev box, python 3.14.4, **libpcre2 10.46
2025-08-27**. pcrec-bench read only, at `d359564f`. Instruments and verbatim outputs are in
`docs/design/where_to_start/` (`rincensus.py`, `rincensus_summary.py`, `rincensus_run.sh`, `rinner_model_multi.py`,
`rincensus_summary.txt`, `rincensus_rows.tsv.gz`, `rincensus_selftest.txt`, `rinner_model_multi_*.txt`); everything
regenerates with `rincensus_run.sh BENCH SCRATCH` in about a minute.

## 0. Answers first

**Part 1, the census.** Stage 1's gates (G1, G2 with all three arms, G3, ONE common L across top-level branches, not
start-anchored, DFA route) admit, outside `loglines/ipv6` and `altwide/sfx-*`:

| population (DFA route, unanchored) | eligible outside | not already served | **LIVE** (not served, not already an exact row) | weight (bench only, upper estimate) |
|---|---|---|---|---|
| **bench**, 245 patterns, F = 2, strict reading | **12** | 8 | **6** | **2.430 ms LIVE** (2.446 ms outside), 2.299 ms of it `loglines/ipv4` |
| bench, F = 2, generous reading | 17 | 9 | 7 | 2.452 ms |
| bench, F = 1, strict / generous | 20 / 78 | 14 / 32 | 9 / 16 | 2.497 / 2.887 ms |
| **corpus**, 1,967 patterns, F = 2, strict / generous | 135 / 167 | 91 / 97 | **79 / 83** | none exist |
| **realistic catalog**, 36 patterns, F = 2 | 18 | 11 | **10** | none exist |

The six bench LIVE patterns at F = 2 (strict) are `loglines/ipv4`, `syntax/qnt-plus`,
`capability/wild-waf-crs-942160-sleep-benchmark`, `bounded/dotted4`, `bounded/csv5`, `utf8/cls-s-ucp`. For scale: the
instrument's total m_gap weight over every bench pattern is 158.4 ms, `loglines/ipv6` is 5.83 ms, `altwide/sfx-*` is 5.82 ms
(admitted at F = 1 only, section 1.5), and the outside-LIVE total is 2.43 ms, 95% of it one pattern. Read: **outside the two
named families the bench holds a handful of eligible patterns worth about 2.4 ms in all; the corpus and a hand-written
"patterns a person writes" list show the shape (a rare separator after a class run) is common in ordinary patterns (10 of 36
realistic DFA-route patterns are LIVE) but it is not weighted anywhere.** Whether that is "enough" is Frank's call; the
numbers are above and each is reproducible.

**Part 2, the model.** Against libpcre2 10.46, the per-branch tactic with ONE common L and per-branch verify in increasing
start order is **sound under a stricter gate than "every branch passes G2"**: the branches must COMPOSE (section 2.3).
Gated rows: **0 wrong** (`tactic[comp]` 354,457 single-search checks over three random populations, `floor[strong]` 333,039 (70,573 + 46,598 + 215,868), 499,329 shaped `comp` checks), every mutant and negative control fires, every planted row
behaves as the critic said. The ruled text (pair) needs one added conjunct: a fixed-width arm is "weak" and composes only
when every branch is fixed at the SAME width; the disjoint and factor-free arms are "strong" and compose freely. Without it
`(?:aq|[abq]{5}q)` on `bbaqbq` answers (2,4) where the truth is (0,6).

## 1. The census

### 1.1 Method and definitions

Instrument `rincensus.py`. It reads lane startstudy's `census.py` Reader (copied and extended: scoped `(?i:`, `\Q..\E`,
`\x{..}`, class-range escapes, `\p`/`\X` as a conservative approximate item), imports the population loaders, `facts()` and
the byte-rate prior from the artrev census, and asks `pcrec --emit-facts` for the route, `start_anchor`, scan key and
stamps. No subject is matched and no clock is read. A pattern is **eligible** when it is on the DFA route
(`RX_ENGINE dfa`), not start-anchored, and has:

1. **ONE common L** across its top-level branches (revised Q2). The branches are the pattern's top-level alternation,
   looking through a lone `(?:...)` wrapper (that is `loglines/ipv6`'s shape). L is a literal run of single-byte or
   caseless-pair items on the flattened spine. Two readings: **strict** (L is a maximal run, the same run in every branch)
   and **generous** (L may be any contiguous sub-run of the branches' maximal runs; `altwide/sfx-*` needs this, its `ing` is
   the tail of each branch's whole-word literal). `peel` splices the first iteration of a mandatory single-alternative
   group repeat (`(?:H:){4,7}` = `H:(?:H:){3,6}`), an exact rewrite; `loglines/ipv6`, `ipv4`, `csv5` and `dotted4` need it
   (the headline always peels; the no-peel columns are in the summary; peeling adds exactly these four bench patterns and one corpus pattern).
2. **A non-empty P_i** in at least one branch (a landmark at the start is a prefix literal).
3. **G1**: no backreference, call, atomic, possessive or lookaround in any P_i.
4. **G2 per (P_i, L)**, three arms: fixed BYTE width; `bytes(L) not subset alphabet(P_i)`; factor-free (no string of P_i
   contains L as a factor) AND border-free, **both over L's case-fold variant set** (F4). The factor test is P_i's Thompson
   NFA times a shift-and automaton of L's per-position byte sets (so fold variants are handled exactly), never a DFA (F7).
5. **G3**: `ppm(L's rarest scan byte) <= ppm(today's key) / F`, F = 1, 2 (D149's default, the headline), 8. Today's key is
   census.py's K1 key: the necessary byte when a run ships, else the start set's summed mass.

Besides `eligible` (the ruled text, **pair**), each pattern carries **comp**: pair AND the branches compose (section 2.3).
They differ on 7 bench patterns at F = 1 (generous) and on none at F = 2.

Two further columns explain the second table row. **Served**: the start is already exact without a reverse-pass search
(`RX_DFA_SCAN rev-end`, or `RX_DFA_START end-minus-width` / `landing`), so REVEND / START-LANDING walk the pattern backwards
today. **Keyed**: the forward scan is already an EXACT row at the landmark's offset (`offset-set*`, `run-pinned*`), the
rows above `rev-inner` in `where_to_start.md` 1.4's table. **LIVE** = neither. Both are read off stamps, not argued.

### 1.2 The funnel (DFA route, strict reading, cumulative)

| population | patterns | compiled | parsed | DFA route | unanchored | landmark | common L | P non-empty | G1 | G2 | G3 F=1 | F=2 | F=8 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bench | 367 | 342 | 330 | 261 | 245 | 158 | 115 | 41 | 36 | 32 | 21 | 13 | 7 |
| corpus | 4,714 | 4,342 | 3,904 | 2,096 | 1,967 | 989 | 858 | 353 | 270 | 209 | 186 | 135 | 38 |
| catalog | 42 | 42 | 42 | 36 | 36 | 27 | 27 | 23 | 23 | 23 | 20 | 18 | 13 |

The funnel's steep step is "P non-empty": 74 of the bench's 115 common-L patterns have their landmark at the start (a
prefix literal, which the existing rows scan). The G2 step loses 4 bench and 61 corpus patterns, every one by
`P-contains-L` (a class run that contains the landmark, `[a-z]+xy`, `\S+@`); **none is lost by border-freeness alone**, so
F5's unlock trigger (a cell that fails ONLY border-freeness) is not met in any population.

Blind spots, listed not dropped: 12 bench / 438 corpus patterns do not parse (`(?x)`, `\K`, branch reset, conditionals,
`(*VERB)`; ids in the summary), and 25 bench / 372 corpus patterns are refused by pcrec itself under `--features all`. A
parse failure is an unknown, not a decline. The corpus loader reads only each block's encoding and `i` flag (the artrev
population's rule), so `m`/`s`/`x` flags of a block are not modelled. The corpus is a COMPILER test corpus,
adversarial by construction; `tests/possessify` alone is 43 of the 79 LIVE strict-F=2 corpus patterns.

### 1.3 Eligible counts (the decision table, F = 2 then F = 1)

pair / comp, DFA route. Full tables with all four readings are in `rincensus_summary.txt` section 2.

| population | reading | F=2 eligible | outside | outside, not served | outside, LIVE | F=1 eligible | outside | not served | LIVE |
|---|---|---|---|---|---|---|---|---|---|
| bench | strict | 13 | 12 | 8 | **6** | 21 | 20 | 14 | 9 |
| bench | generous | 18 | 17 | 9 | **7** | 82 (75 comp) | 78 | 32 | 16 |
| corpus | strict | 135 | 135 | 91 | **79** | 186 | 186 | 130 | 117 |
| corpus | generous | 167 | 167 | 97 | **83** | 354 | 354 | 167 | 138 |
| catalog | strict | 18 | 18 | 11 | **10** | 20 | 20 | 12 | 11 |

By arm (strict, F = 2), bench: fixed 4, disj 9, factor-free first-match 0; the factor-free arm is the ONLY admitting arm
for **0** patterns at F = 2. At F = 1 it is needed for 1 strict bench pattern (`capability/wild-waf-crs-942500-comment-obfuscation`,
`*/`) and, generous, for `altwide/sfx-256` and `sfx-512`; `sfx-64` needs no factor-free arm because every stem alone
cannot consume `i`, `n` and `g` together, so each branch passes the disjoint arm and the branches compose (D151 add. 5's
admission of sfx-64 is therefore redundant under add. 6's per-branch reading). Corpus: 0 patterns need the arm; catalog: 1
(`... HTTP/`, F = 1). Sabotage (summary, last table): making every P factor-free admits **+35** corpus and +2 bench
patterns at F = 2 strict, so the factor conjunct is load-bearing in the count; making every L border-free changes **no
count in any population** (the border conjunct is load-bearing only in the model, section 2.1, and in the selftest rows).

Shape of the eligible patterns (headline, F = 2): by L, bench 9 single-byte separator / 4 word / 0 other; catalog 16 / 1 / 1.
The bench's outside LIVE patterns are one family seen from several angles: a rare delimiter after a class run
(`ipv4`/`dotted4` `.`, `csv5` `,`, the WAF pattern `(`, `qnt-plus` `b`, `utf8/cls-s-ucp` `b`).

### 1.4 The outside list (every bench pattern eligible at F >= 1 outside ipv6/sfx, strict, weights in ms)

| id | L | ratio | arm | served | keyed | LIVE | stamps (scan / start / prefilter / handoff) | weight |
|---|---|---|---|---|---|---|---|---|
| loglines/ipv4 | `.` | 7.5 | disj | n | n | **y** | unanchored / reverse-pass / byte-class / none | 2.2986 |
| syntax/qnt-plus | `b` | 5.5 | disj | n | n | **y** | .. / reverse-pass / memchr / none | 0.0897 |
| syntax/cls-s-lc | `sat` | 1.0 | disj | n | n | y (F=1) | .. / reverse-pass / memchr / none | 0.0531 |
| capability/wild-waf-crs-942160-sleep-benchmark | `(` | 34.4 | disj | n | n | **y** (2 branches) | .. / reverse-pass / byte-class / none | 0.0416 |
| loglines/iso-ts | `-` | 15.0 | fixed | n | y | n | .. / reverse-pass / offset-set / none | 0.0140 |
| loglines/kv-quoted | `="` | 1.0 | disj | n | n | y (F=1) | .. / reverse-pass / first-class-bounded / 32 | 0.0085 |
| syntax/cls-h | `=` | 1.95 | disj | n | n | y (F=1) | .. / reverse-pass / memchr / none | 0.0051 |
| bounded/dotted4 | `.` | 7.5 | disj | n | n | **y** | .. / reverse-pass / byte-class / none | 0.0001 |
| bounded/csv5 | `,` | 149.0 | disj | n | n | **y** | .. / reverse-pass / memchr / none | 0.0000 |
| utf8/cls-s-ucp | `b` | 5.5 | disj | n | n | **y** | .. / reverse-pass / memchr / none | 0.0000 |
| loglines/uuid, utf8/cls-s-nbsp, syntax/cls-n-uc, syntax/mod-s, capability/wild-validator-uuid-grok | | | fixed/disj | y | y | n | end-minus-width | <= 0.007 |
| loglines/stack-frame, syntax/cls-v | `(`, `done` | | disj | n | y | n | offset-set | <= 0.006 |

`syntax/cls-s-uc` (`\S+@`) and both `email/*` patterns fail G2 or G1 and are not on the list, matching et1twin's recount; the
census reproduces et1twin's table on the K12 class (ipv6 survives; sfx passes only the factor-free / per-branch reading;
kv-quoted and uuid survive; the eight `^`-anchored cells are `anchored`; the two VM hybrids are off route). The generous
reading adds `utf8/ci-moskva` (0.2237 ms, F = 1 only), `altwide/sh1-*` (admitted by the ruled text, composition-UNSAFE,
section 2.3), `utf8/ci-strasse` and a dozen served/keyed rows. The catalog list (10 LIVE) and the corpus families are in
the summary; the catalog is `docs/design/eng_brep_measurements/probes/realistic_patterns.txt` (40 hand-written patterns
plus its two `#rrggbb` colours; its own disclosed bias is "written from memory").

### 1.5 Weights (bench, upper estimates)

walk_survey's K12 formula applied to ANY pattern: est ms = sum over default-config cells of bench_ns x m_gap / T, K1-owned
cells excluded (`rincensus.weights`). **Control: over walk_survey's own 24 K12 patterns it returns 15.786 ms, exactly the
survey's figure (asserted).** It is an upper estimate for the reasons the survey gives (uniform per-byte cost; m_gap counts
the forward machine's steps before each match start, which a perfect landmark scan would avoid, before paying the reverse
walks).

| set | F = 2 strict | F = 1 generous |
|---|---|---|
| `loglines/ipv6` | 5.829 | 5.829 |
| `altwide/sfx-64/256/512` | not admitted: ratio 1.00, today already scans the same `ing` byte | 5.817 |
| outside both, eligible | 2.446 | 2.981 |
| outside both, LIVE | 2.430 | 2.887 |

G3 note: sfx's L is the same byte the artifact already keys on (`RX_REQ_RUN 696e67@2`, handoff 9), so at the D149 default
F = 2 G3 DECLINES the pattern the factor-free arm was added for. The hand twin's -93.3% (et1twin) is the handoff-window versus
exact-start gain, which G3's byte-rate ratio does not see. Either G3's reference key must be the handoff window for such
patterns, or sfx rides F = 1, or add. 5's headline admission is vacuous at the shipped default. This is a finding for the
ruling, not a census error: the census applies G3 as written.

### 1.6 Off route and sensitivity

Stage 2 populations with the same gates (hybrid / VM-only, F = 2, strict): bench 1 / 4, corpus 123 / 26, catalog 3 / 0.
Readings (bench / corpus eligible at F = 2): strict no-peel 9 / 134, strict peel 13 / 135, generous no-peel 14 / 166,
generous peel 18 / 167. Peeling is worth four bench patterns and one corpus pattern; the sub-run reading is worth five bench
(all utf8: `ci-ascii-control`, `ci-sigma`, `ci-strasse`, `lit-offset-at-tail`, `lit-sharp-s`) and 32 corpus.

### 1.7 Controls (K35)

- **C1** hand-classified rows (`rincensus.py --selftest`, 21 rows plus the equal/mixed-P flags: each arm positive and negative, caseless L, mixed P, the
  two F2 distinct-landmark shapes, `loglines/ipv6`), 0 failed.
- **C2** the arms against an independent implementation: 2,491 generated cases (804 with a factor string) compared with
  `rinner_model.py`'s own bookkeeping and `factor_witness` (parse_p plus Dijkstra over NFA x KMP): fixed width, alphabet arm,
  factor test and border test, **0 disagreements**. And necessity against pcrec's own `req_set` (`src/facts/req.c`, no shared
  code): 1,857 patterns, 6,008 landmark bytes, **0 violations**.
- **C3** sabotage: `--selftest --sabotage no-border` fails 3 rows, `--sabotage no-factor` fails 806 (the C2 factor
  comparison reds 804 by itself); the census counts move only for no-factor (above).
- The weights control and the strict-subset-of-generous assertion are in `rincensus_summary.py`.

## 2. The model (critic findings F1-F4, F6)

`rinner_model_multi.py` imports `rinner_model.py` (libpcre2 10.46 as the oracle AND as the tactic's two components, the same
instrument) and adds the per-branch tactic, the floor mutants, a caseless L, a distinct-landmark scan and the planted rows.
The form (ii) tactic: per occurrence j of the common L, each branch's own minimum start s*_i(j) (P_i end-pinned at j, run
anchored by the backtracking matcher); verify the whole R anchored at them in increasing order; first success wins.

### 2.1 The planted rows (`rinner_model_multi_fixed.txt`, every startpos and find-all, `--selftest` PASS)

| row | subject | truth | what the transcript shows |
|---|---|---|---|
| F4 `(?i)(?:xb*a\|b)aA` | `xbaaa` | (0,5) | the arm DECLINES (variants `AA Aa aA aa`: bordered); the ungated tactic answers (1,4), wrong |
| F4' `(?:xb*a\|b)aa` | `xbaaa` | (0,5) | same, case-sensitive: border-freeness is necessary |
| F3 `b[ax]+ab` | `abxab` | (1,5) | start+1 floor right; `floor_end` (previous END) answers none: wrong; admitted by the factor-free arm |
| F3' `(?:dog\|cat)ing` | `doging` | (0,6) | start+1 floor right; **`floor_bytehit` (previous hit of the scan byte `g`) answers none: wrong** |
| F1 `(?:[ab]+:x\|b:y)` | `ab:y` | (1,4) | per-branch verify in increasing order right; **`unionmin` (whole R at the union minimum 0) answers none: wrong** |
| C `(?:aq\|[abq]{5}q)` | `bbaqbq` | (0,6) | pair-admitted (both fixed), composition-unsafe: the tactic answers (2,4), wrong; the composition gate DECLINES |
| F2 `yab\|[xy]*abc` | `xyabc` | (0,5) | one scan over the distinct landmarks `yab`, `abc` answers (1,4): wrong |
| F2 `x[a-y]*z\|cq` | `xcqz` | (0,4) | one scan over `z`, `cq` answers (1,3): wrong |

Both F2 shapes are DECLINED by the strict common-L rule (`no-common-L` in the census selftest). Each branch alone passes
G2 (`[True, True]`); the failure is purely the combination, which is F2's point.

### 2.2 Random populations (all `--selftest` PASS)

Population: `R = (?:P_1 L S_1 | P_2 L S_2 [| P_3 L S_3])`, one common L, P_i/S_i from rinner_model's generator, subjects
over `abX\n` (plus `é` in UTF mode), every startpos plus find-all. Gate classes: `pair` = every branch has an arm and G1
holds, `comp` = pair AND composes, `strong` = every branch strong (floor sound).

| run | cases | pair / comp / strong | `tactic[comp]` | `floor[strong]` | `unionmin[comp]` | `floor_end[strong]` | `floor_bytehit[strong]` | `gate_off` |
|---|---|---|---|---|---|---|---|---|
| byte seed 1 | 6,000 | 1,379 / 1,076 / 1,014 | **0** / 74,860 | **0** / 70,573 | 179 wrong | 38 wrong | 308 wrong | 13 wrong |
| utf8 seed 2 | 4,000 | 904 / 715 / 672 | **0** / 49,617 | **0** / 46,598 | 56 wrong | 5 wrong | 82 wrong | 9 wrong |
| byte seed 7 | 20,000 | 4,321 / 3,315 / 3,113 | **0** / 229,980 | **0** / 215,868 | 535 wrong | 139 wrong | 1,253 wrong | 109 wrong |

1,051 of the 1,076 seed-1 comp cases have branches with DIFFERENT P_i, so the mixed-P_i case is the bulk of the
population, not a corner. Find-all agrees everywhere the single searches do.

### 2.3 The composition finding (a gate the ruled text lacks)

The random populations never tripped `pair_not_comp` (0 wrong over 21,256 checks), because the 3-letter alphabet almost
never lets two fixed widths collide. A SHAPED population (branches over `{a,b,q}`, L = `q`; kinds FIXED (`[abq]{w}`, literals),
STRONG (`[ab]+`, empty), AMBIGUOUS (`[abq]+`)) separates them:

| class (shaped, byte seed 1 x 1,500 cases) | checks | wrong |
|---|---|---|
| `comp` | 113,902 | **0** |
| `pair_not_comp` (a fixed branch beside a different-width fixed branch, or beside a strong branch) | 71,394 | **372** (fixed+strong 305, fixed 67) |
| `gate_off` (a branch with no arm) | 213,040 | 159 |

seed 7 x 5,000: comp 385,427 checks 0 wrong; pair_not_comp 244,701 checks 1,430 wrong.

The mechanism: a **strong** arm (disjoint, or factor-free with border-free, or an empty P) guarantees every start of a later
occurrence lies above every earlier occurrence, independent of the other branches. A **weak** fixed-width arm only gives
monotonicity within its own branch. With two widths, branch B's start at j' can precede branch A's start at j
(`(?:aq|[abq]{5}q)` on `bbaqbq`), and the candidate loop answers at j. Rule, proposed for the build:

> Branches compose iff every branch is strong (cannot-contain-L, factor-free with border-free L, or width 0), OR every
> branch is fixed at the SAME width. A single branch needs one arm of either kind.

Effect on the bench: `altwide/sh1-64/256/512`, `altwide/pfx3-256/512` and `capability/file-ext-order` (plus its sentinel
twin) pass "every branch passes G2" and fail composition. All seven are F = 1 rows (L has ratio 1.00). `pfx3-*` and
`file-ext-order` are `keyed` today; `sh1-*` are LIVE at F = 1 and are the three LIVE rows the gate removes. The consequence for D151 add. 5/6 is that the factor-free arm's role is narrower than stated: it is one of two
strong arms (with the alphabet arm), and the census (1.3) shows it is the only admitting arm for 0 bench patterns at F = 2.

### 2.4 Verdicts per finding

| id | verdict |
|---|---|
| F1 | CONFIRMED on libpcre2 10.46: `unionmin` is wrong on `ab:y`; form (ii) right; 535 random wrongs over 229,980 checks |
| F2 | CONFIRMED: a single scan over distinct landmarks is wrong on both shapes and in 8 to 15 random cases; both shapes declined by the strict common-L rule. The generous (sub-run) reading would admit `yab\|[xy]*abc` as L = `ab` with P_1 = `y` (weak), P_2 = `[xy]*` (strong), which the composition gate declines |
| F3 | CONFIRMED and DEFINED: floor = previous occurrence's start + 1; `floor_end` and `floor_bytehit` are both wrong and detected on the planted rows and in every random population |
| F4 | CONFIRMED: border-freeness and the factor test over fold variants; `(?i)(?:xb*a\|b)aA` declined; census selftest row passes; under utf8 with a caseless L containing `k`/`s` or a non-ASCII byte the census declines conservatively (U+212A, U+017F, non-ASCII folds are not modelled) |
| F6 | DONE: per-branch generator, population counted (the arm-3-only counts are census 1.3), fixed rows planted, floor mutants, drop-the-border sabotage (selftest) |

## 3. What this changes in D151

1. Add. 6's "verify at each branch's own minimum start, increasing order" needs the composition gate of 2.3; the ruled
   per-branch G2 alone is unsound for mixed fixed widths. A one-line addendum.
2. G3 as written declines `altwide/sfx-*` at F = 2 (ratio 1.00, same byte as today's run scan). The gain the twin measured is
   the exact-start-versus-handoff-window gain. Frank's call: admit at F = 1 for handoff-keyed rows, or key G3 on the window.
3. ipv6 needs the peeled first iteration of a mandatory group repeat; so do `ipv4`, `dotted4`, `csv5`. The build's
   inner_split fact must splice it (rust's `flatten` does not).
4. The census count is the decision input: outside ipv6/sfx, 6 bench patterns are LIVE at F = 2 and weigh 2.4 ms of an
   upper-estimate 158 ms (one pattern is 95% of it), 79 corpus and 10 realistic-catalog patterns are LIVE. The shape is
   "a rare delimiter after a class run", shared by the two named families.

Nothing here builds or files anything (D77, "no build without a problem scenario").

## 4. Validation

- `rincensus.py --selftest` 0 failed; both sabotage runs fail as required (`rincensus_selftest.txt`).
- `rinner_model_multi.py --selftest`: fixed rows PASS, byte seed 1, utf8 seed 2, byte seed 7 PASS, every mutant and control
  detected, gated rows 0 wrong, all against libpcre2 10.46.
- Re-run: `docs/design/where_to_start/rincensus_run.sh /home/pcrec/projects/pcrec-bench SCRATCH`.
- `make test-spec-history`: see the handback (run async after this report and the two CLAUDE.md edits).
