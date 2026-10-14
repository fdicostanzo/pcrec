# Reading of the vecspike timing slot (vecspike + vecspike2)

Reader lane: kit-manager-spawned reading task, 2026-10-13. Pure log reading: no make, no timing, no builds. All numbers below are computed from the two timing logs and the counter files by the scripts in `readtmp/` (`load.py`, `common.py`, `gen_tables.py`, `a*.py`); the spike reports' predictions are quoted from `lane/vecspike:docs/dev/lanes/vecspike_report.md` section 6 and `lane/vecspike2:docs/dev/lanes/vecspike2_report.md` section 7.

Inputs read:
- `spike1/time.log` (vecspike, 1,549 timed rows, 116 groups), `spike1/v2/time2.log` (vecspike2, 288 rows, 18 groups), `spike1/slot.status` (T1 rc=0 wall 5,585 s, T2 rc=0 wall 1,036 s, both COMPLETE lines present, zero `ANSWER MISMATCH` lines in either log).
- `spike1/counts.tsv`, `spike1/v2/counts.tsv`, `spike1/v2/counts2.tsv` (the no-clock counter builds).
- `slot25c/time.log` (R17-b's ALPHA record) and the r17loss report for the loss context.

## 1. Regime, column meanings, noise floor

### 1.1 Regime

- Box: the Linux dev box (host `frank-desktop`, Ryzen 7 7700X, Zen 4). Governor `performance` (from the log headers). Binaries pinned with `taskset -c 14` (CPU=14), LAUNCHES=5 interleaved launches per group.
- vecspike run (`time.log`): started 17:46:17 UTC, header `load1=3.25` at launch; `time.sh` waits for load1 < 1.5 before every group (up to 20 min), so the per-group state was below 1.5 but the start load was not quiet. Wall 5,585 s. vecspike2 run (`time2.log`): started 19:19:22 UTC, header `load1=1.00`. Wall 1,036 s.
- Population: 8 cells x 9 subjects x 2 modes = 144 groups, of which 28 are skipped by `time.sh` because no variant reaches the site (`uses = 0`: email on 7 of 9 subjects, word-eq on 4 of 9, vm-hat on 2, vm-hat-1 on 1). 116 groups timed (58 `first`, 58 `all`). vecspike2: dfa-hat x 9 subjects x 2 modes = 18 groups.
- `first` = one `rx_search` from 0 (the first match, or the whole-subject scan when there is none). `all` = the find-all loop over the subject. Neither is timed per match: both report ns per pass.
- Not every KEEP row exists in `first`: where the kept variant's holding function assembled identically to its unkept twin, `build.sh` marked it `same_first` and `time.sh` does not time it (V3 in the 8 vm-hat-1 `first` groups, V4 in the 7 vm-hat `first` groups, S3/S4/A3/A4 in the 15 vm-hat and vm-hat-1 `first` groups). Those cells have no `first` row for the kept variants.

### 1.2 Columns

`time.log` / `time2.log` (one row per variant per group):

| column | meaning |
|---|---|
| cell, subject, mode | the group: cell is the R17-b site (dig, email, word-eq, hex-run, bounded, dfa-hat, vm-hat, vm-hat-1); subject is one of slot25c's five (short 40 B, prose64k, digits64k, prose1m, mix64k) or the four real-text ones (docs64k, docs1m, code64k, code1m); mode `first` or `all` |
| var | the variant (table below) |
| ns | ns per pass: the median over the 5 launches of each launch's own 7-round median (each binary calibrates to >= 50 ms) |
| V0 | the same group's walk baseline, ns per pass: slot25c's `deny`, the 256-byte table walk (the "scalar baseline" / "the walk") |
| delta | ns - V0 (negative is faster than the walk) |
| floor | the group's A/A floor, \|V0b - V0\|: V0 is launched twice per round (`V0` and `V0b`, the same binary) |
| per_match | delta / matches (`all` mode only) |
| verdict | `time.sh`'s own: NULL when \|delta\| <= floor, else WIN (delta < 0) or LOSS (delta > 0). This reading writes LOSS as REGRESSION / R |

`counts.tsv` (one counting-build pass, no clock): calls = `rx_search` calls in the pass; uses = `next_candidate` calls (so uses/calls is uses per activation); cold = uses that found the state empty; cache_hit / cache_pass = uses served from the cached mask / whose cached block held no member; xcall = cache-served uses whose block was filled in an EARLIER call (KEEP only); skipped = candidate tests the cache avoided; head_hit / head_bytes = the prologue's scalar head; blocks = block evaluations. `counts2.tsv`: calls, uses, cands (candidates handed to the DFA), blocks.

Variants (vecspike):

| V | width | edit |
|---|---|---|
| V0 | - | the walk (256-byte table), the baseline of every delta |
| V1 | 8 B (SWAR) | R17-b `new` as shipped (= ALPHA) |
| V1x | 8 B | V1 built with `-mavx2` (flag control) |
| V2 | 8 B | alignment prologue: serial scalar head up to the load alignment, then aligned block loads |
| V3 | 8 B | KEEP: the mask state is a caller-held `struct rx_keep` preserved across the calls of one find-all pass |
| V4 | 8 B | V2 + V3 |
| S1 S2 S3 S4 | SSE2, W = 64 (4 x 16 B) | plain / prologue / keep / both |
| A1 A2 A3 A4 | AVX2, W = 64 (2 x 32 B) | plain / prologue / keep / both |

vecspike2 (dfa-hat only; per-position class masks ANDed): P2 = positions 0-1, P3 = 0-2, P4 = 0-3, P3W = 0-2 plus the `\w` context at offset -1 (written PW below); each at `w` (8 B), `s` (SSE2), `a` (AVX2); the baseline for each is that width's P1 (V1, S1, A1), timed again in the same interleave. In the tables a variant's width is its last letter: `P3w`, `P3s`, `P3a`; "8 B" = `w`.

Subject densities and the variant edits are in the two spike reports; they are not repeated here.

### 1.3 Noise floor

What the logs give: only medians (the per-launch spread is not recorded), and one A/A pair per group (V0 vs V0b, the same binary launched twice in every round). So the floor is the A/A pair.

Measured over the 116 vecspike groups, A/A as a fraction of the group's V0 ns: median 0.15%, p75 0.64%, p90 2.3%, p95 4.2%, max 60.8%. Twelve groups have an A/A of exactly 0.00 ns in the log (two equal medians at two decimals), so the log's own NULL verdict is unreachable for them. Eleven groups exceed 2.3%; six exceed 5%: five 64 KiB find-all groups and one 40 ns row (r17loss section 3.4 already described the 64 KiB find-all bimodality):

| group | A/A ns | of V0 |
|---|---|---|
| bounded mix64k all | 32,864 | 60.8% |
| hex-run prose64k all | 21,963 | 36.6% |
| dig digits64k all | 13,608 | 11.2% |
| bounded code64k all | 7,382 | 6.8% |
| vm-hat mix64k all | 1,662 | 6.1% |
| vm-hat docs1m first | 2.15 | 5.4% (V0 = 40 ns) |

vecspike2 A/A: 0.03%-1.78% of V0 over its 18 groups (median 0.29%).

Extra control: V1x is V1 built with `-mavx2` and carries no AVX2 code. Its ns equals V1's within 0.04% (median |V1x - V1| / V1) over the 116 groups; the maximum is 3.4% (hex-run mix64k all, whose own A/A is 3.2%), the next 0.94%, and V1x is NULL against V1 under the strict floor in 116 of 116 groups.

**Floor used in this reading.** A difference d between a variant and a reference is NULL when |d| <= max(group A/A, 2.3% of the reference ns). The 2.3% is the p90 of the A/A distribution and replaces the log's floor only where that floor is smaller (the 12 zero-floor groups and the many groups below 0.5%). For a variant-versus-variant comparison (kept vs unkept, prologue vs plain, P vs P1) the reference is the second variant and the group A/A is the same (an A/A pair is already a difference of two medians). The six unstable groups above are judged by their own (large) A/A. Both counts are shown wherever verdicts are tallied ("log" = `time.sh`'s verdict, "strict" = this floor). A mark `~` in a table means NULL under this floor. Per-use figures are delta / uses with uses from `counts.tsv`. The per-cell medians and ranges use only subjects with uses >= 100; single-use rows (sparse whole-subject scans) are absolute ns, and the per-subject tables mark them (uses = 1).

## 2. The kept vector: value per cell at 8 B / SSE2 / AVX2

Definitions used throughout: "walk" = V0. "Unkept" = the same width without keep (V1, S1, A1). "Kept" = V3, S3, A3. The kept vector can only help in `all` (one state across the calls of a find-all pass); in `first` there is one call and nothing to keep, so `first` rows of a kept variant measure the cost of the machinery itself (2.4).

### 2.1 WIN / REGRESSION / NULL per variant per width (vs the walk)

Rows are variants; each count cell is WIN/REGRESSION/NULL. "(log)" uses `time.sh`'s verdict, "(strict)" this reading's floor. n = number of timed groups for that variant and mode.

| variant | width | edit | first: WIN/REG/NULL (log) | first (strict) | all: WIN/REG/NULL (log) | all (strict) |
|---|---|---|---|---|---|---|
| V1 | 8 B | R17-b as is (SWAR) | 24/34/0 (n=58) | 24/33/1 | 26/29/3 (n=58) | 25/28/5 |
| V1x | 8 B | V1 built with -mavx2 (flag control) | 24/34/0 (n=58) | 24/33/1 | 26/29/3 (n=58) | 25/28/5 |
| V2 | 8 B | alignment prologue | 24/34/0 (n=58) | 23/34/1 | 22/34/2 (n=58) | 22/34/2 |
| V3 | 8 B | kept vector | 17/33/0 (n=50) | 16/32/2 | 22/33/3 (n=58) | 22/32/4 |
| V4 | 8 B | prologue + kept | 17/34/0 (n=51) | 17/34/0 | 22/34/2 (n=58) | 21/33/4 |
| S1 | SSE2 | W=64, 4x16 B | 31/27/0 (n=58) | 31/25/2 | 34/22/2 (n=58) | 34/18/6 |
| S2 | SSE2 | prologue | 31/27/0 (n=58) | 31/27/0 | 34/22/2 (n=58) | 32/21/5 |
| S3 | SSE2 | kept | 15/26/2 (n=43) | 15/26/2 | 41/13/4 (n=58) | 39/13/6 |
| S4 | SSE2 | prologue + kept | 14/29/0 (n=43) | 13/28/2 | 37/17/4 (n=58) | 33/15/10 |
| A1 | AVX2 | W=64, 2x32 B | 33/25/0 (n=58) | 33/21/4 | 40/15/3 (n=58) | 39/14/5 |
| A2 | AVX2 | prologue | 33/24/1 (n=58) | 33/19/6 | 37/17/4 (n=58) | 35/12/11 |
| A3 | AVX2 | kept | 18/25/0 (n=43) | 16/25/2 | 43/13/2 (n=58) | 43/12/3 |
| A4 | AVX2 | prologue + kept | 12/31/0 (n=43) | 12/29/2 | 34/21/3 (n=58) | 31/19/8 |

Same-width comparisons, `all` mode, strict floor (WIN means the first variant is faster than the second):

| comparison | 8 B | SSE2 | AVX2 |
|---|---|---|---|
| kept vs unkept (X3 vs X1) | 6/34/18 | 16/22/20 | 23/18/17 |
| prologue vs plain (X2 vs X1) | 10/32/16 | 10/30/18 | 12/31/15 |
| prologue on top of keep (X4 vs X3) | 18/19/21 | 5/26/27 | 2/35/21 |

Same, `first` mode (a single call): kept vs unkept 2/26/22 (n=50), 0/33/10 (n=43), 0/19/24 (n=43); prologue vs plain 2/27/29, 0/31/27, 12/20/26; prologue on keep 3/26/14, 0/13/30, 6/25/12.

### 2.2 Kept vector, per cell and width (`all` mode)

Columns: unkept vs walk, kept vs walk, kept vs unkept are WIN/REGRESSION/NULL over the cell's `all` subjects. The ns/use columns use only subjects with uses >= 100 (n shown); kept-served % is the share of uses answered from a block filled in an earlier call. "median ns/use: unkept, kept, kept-unkept" are all relative to the walk except the last (kept minus unkept).

| width | cell | n | unkept vs walk W/R/N | kept vs walk W/R/N | kept vs unkept W/R/N | n(uses>=100) | kept-served % (min..max) | median ns/use: unkept, kept, kept-unkept | range of kept-unkept ns/use |
|---|---|---|---|---|---|---|---|---|---|
| 8 B | dig | 9 | 8/0/1 | 8/1/0 | 0/4/5 | 6 | 0..26 | -3.01, -2.79, +0.23 | -0.05 .. +3.69 |
| 8 B | email | 2 | 0/1/1 | 0/2/0 | 0/2/0 | 2 | 0..0 | +0.25, +0.99, +0.74 | +0.70 .. +0.79 |
| 8 B | word-eq | 5 | 0/5/0 | 0/5/0 | 0/5/0 | 5 | 0..6 | +1.29, +1.43, +0.46 | +0.14 .. +0.85 |
| 8 B | hex-run | 9 | 3/5/1 | 1/6/2 | 3/5/1 | 8 | 51..85 | +0.17, +0.75, +0.34 | -1.20 .. +1.53 |
| 8 B | bounded | 9 | 0/8/1 | 0/8/1 | 0/3/6 | 8 | 8..52 | +1.43, +2.14, +0.36 | -0.58 .. +1.28 |
| 8 B | dfa-hat | 9 | 2/7/0 | 2/7/0 | 2/7/0 | 6 | 0..1 | +1.64, +2.48, +0.78 | +0.70 .. +1.00 |
| 8 B | vm-hat | 7 | 4/2/1 | 3/3/1 | 0/7/0 | 7 | 3..5 | -1.05, -0.09, +0.96 | +0.82 .. +1.72 |
| 8 B | vm-hat-1 | 8 | 8/0/0 | 8/0/0 | 1/1/6 | 5 | 0..0 | -3.57, -3.61, -0.05 | -0.41 .. -0.02 |
| SSE2 | dig | 9 | 7/2/0 | 7/2/0 | 0/4/5 | 6 | 0..79 | -11.27, -9.32, +0.40 | +0.20 .. +3.55 |
| SSE2 | email | 2 | 2/0/0 | 2/0/0 | 0/2/0 | 2 | 0..0 | -2.17, -1.23, +0.94 | +0.91 .. +0.97 |
| SSE2 | word-eq | 5 | 2/1/2 | 0/3/2 | 0/4/1 | 5 | 0..36 | +0.06, +0.37, +0.82 | -0.05 .. +1.48 |
| SSE2 | hex-run | 9 | 0/6/3 | 5/3/1 | 9/0/0 | 8 | 91..98 | +0.63, -1.98, -3.74 | -4.23 .. -1.23 |
| SSE2 | bounded | 9 | 1/7/1 | 3/3/3 | 7/0/2 | 8 | 25..93 | +1.85, -0.26, -2.40 | -3.06 .. +0.04 |
| SSE2 | dfa-hat | 9 | 8/1/0 | 8/1/0 | 0/7/2 | 6 | 0..2 | -2.45, -1.58, +0.78 | +0.65 .. +0.97 |
| SSE2 | vm-hat | 7 | 7/0/0 | 7/0/0 | 0/2/5 | 7 | 8..17 | -3.27, -3.20, +0.08 | -0.10 .. +0.14 |
| SSE2 | vm-hat-1 | 8 | 7/1/0 | 7/1/0 | 0/3/5 | 5 | 0..1 | -8.75, -8.52, +0.22 | +0.10 .. +0.39 |
| AVX2 | dig | 9 | 8/1/0 | 6/2/1 | 0/4/5 | 6 | 0..79 | -11.73, -10.29, +0.64 | +0.10 .. +2.71 |
| AVX2 | email | 2 | 2/0/0 | 2/0/0 | 0/2/0 | 2 | 0..0 | -2.15, -1.61, +0.54 | +0.49 .. +0.59 |
| AVX2 | word-eq | 5 | 2/1/2 | 2/3/0 | 0/4/1 | 5 | 0..36 | -0.03, +0.36, +0.91 | +0.08 .. +2.12 |
| AVX2 | hex-run | 9 | 3/4/2 | 5/3/1 | 9/0/0 | 8 | 91..98 | -0.08, -2.31, -2.82 | -3.03 .. -1.57 |
| AVX2 | bounded | 9 | 1/7/1 | 5/3/1 | 7/0/2 | 8 | 25..93 | +0.93, -0.97, -2.02 | -3.30 .. -0.04 |
| AVX2 | dfa-hat | 9 | 8/1/0 | 8/1/0 | 0/7/2 | 6 | 0..2 | -2.62, -1.71, +0.87 | +0.74 .. +1.14 |
| AVX2 | vm-hat | 7 | 7/0/0 | 7/0/0 | 0/0/7 | 7 | 8..17 | -3.80, -3.70, +0.04 | -0.00 .. +0.11 |
| AVX2 | vm-hat-1 | 8 | 8/0/0 | 8/0/0 | 7/1/0 | 5 | 0..1 | -9.02, -9.55, -0.53 | -1.26 .. -0.21 |

Reading, by cell:

- **hex-run** (kept-served 51-85% of uses at 8 B, 91-98% at SSE2/AVX2): the kept vector is where the value is, but only at SIMD width. SSE2: kept beats unkept on 9 of 9 subjects (median -3.74 ns/use, range -4.23 to -1.23); AVX2: 9 of 9 (median -2.82). Against the walk this moves hex-run from 0W/6R/3N to 5W/3R/1N (SSE2) and from 3W/4R/2N to 5W/3R/1N (AVX2). At 8 B kept beats unkept on 3 of 9 (short -0.97, docs64k -1.11, code64k -1.16 ns/use; prose64k -1.20 is NULL because that group's A/A is 36.6%) and loses on 5; the 8 B median is +0.34 ns/use. So the kept 8-byte vector is not the lever for hex-run.
- **bounded** (kept-served 8-52% at 8 B, 25-93% at SSE2/AVX2): SSE2 7 WIN/0 REG/2 NULL (median -2.40 ns/use), AVX2 7/0/2 (-2.02). At 8 B: 0/3/6 (+0.36). The kept SIMD vector turns bounded against the walk from 1W/7R/1N to 3W/3R/3N (SSE2) and 1W/7R/1N to 5W/3R/1N (AVX2). It does not remove the loss on prose: S3 still +2.87 / +2.40 and A3 +2.21 / +1.94 ns/use against the walk on prose64k / prose1m (section 6).
- **dfa-hat** (1 call per pass on prose/digits/mix; 8-466 calls on docs/code; kept-served 0-2%): kept is a loss at every width: +0.78 (8 B), +0.78 (SSE2), +0.87 (AVX2) ns/use median, kept-vs-unkept 0W/7R/2N at the SIMD widths, 2W/7R at 8 B (the two W are the 1-use no-candidate rows, -7.4%: code layout, not keeping).
- **vm-hat** (kept-served 3-5% at 8 B, 8-17% at SSE2/AVX2): kept costs +0.96 ns/use at 8 B (0/7/0) and is NULL at SIMD widths (SSE2 0/2/5, +0.08; AVX2 0/0/7, +0.04).
- **vm-hat-1, dig, email, word-eq** (kept-served 0-26%, email 0): no value at any width. At SSE2/AVX2 the kept-minus-unkept medians are dig +0.40/+0.64, word-eq +0.82/+0.91 and email +0.94/+0.54 ns/use; vm-hat-1 is NULL in 6 of 8 (8 B) and 5 of 8 (SSE2) subjects. AVX2 vm-hat-1 reads 7 WIN/1 REG, but its kept-served share is 0-1%, so those wins cannot be reuse; they are consistent with a code-generation difference between the A3 and A1 holding functions (the logs do not say which).
- **Weights.** Across the 58 `all` groups the kept vector is a net loss at 8 B (6 WIN / 34 REG / 18 NULL against unkept), a split at SSE2 (16/22/20) and a small net win at AVX2 (23/18/17), and every WIN comes from hex-run, bounded or from a 0%-kept-served layout effect (vm-hat-1, dfa-hat no-candidate rows).

### 2.3 Per subject, `all` mode

ns per use relative to the walk (negative = faster than the walk); `~` = within the floor; the "-" columns are kept minus unkept at that width. For single-use rows (uses = 1; the sparse whole-subject scans) the figure is the absolute ns of the pass, not per use. Subjects with a real-text name are the vecspike extension; short/prose64k/digits64k/prose1m/mix64k are slot25c's.

| cell | subject | uses | calls | kept-served % | 8 B V1 | V3 | V3-V1 | SSE2 S1 | S3 | S3-S1 | AVX2 A1 | A3 | A3-A1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dig | short | 1 | 1 | 0 | -4.45 | -3.00 | +1.45 | +9.38 | +10.98 | +1.60 | -0.92 | +0.11~ | +1.03 |
| dig | prose64k | 1 | 1 | 0 | -5203.17 | -4875.87 | +327.30 | -11086.79 | -11085.57 | +1.22~ | -11764.78 | -11762.31 | +2.47~ |
| dig | digits64k | 9055 | 4604 | 26 | +0.89~ | +4.57 | +3.69 | +3.94 | +4.33 | +0.39~ | +3.01 | +4.04 | +1.03~ |
| dig | prose1m | 1 | 1 | 0 | -85215.50 | -77684.42 | +7531.08 | -177637.13 | -177579.89 | +57.24~ | -187910.53 | -187847.38 | +63.15~ |
| dig | mix64k | 16177 | 1380 | 8 | -1.68 | -1.47 | +0.21~ | -1.93 | -1.73 | +0.20~ | -2.00 | +0.34 | +2.34 |
| dig | docs64k | 1479 | 5 | 0 | -3.71 | -3.52 | +0.19~ | -7.88 | -7.53 | +0.35~ | -8.28 | -8.11 | +0.18~ |
| dig | docs1m | 19236 | 190 | 1 | -2.31 | -2.06 | +0.25~ | -14.67 | -11.12 | +3.55 | -15.18 | -12.47 | +2.71 |
| dig | code64k | 527 | 7 | 1 | -11.16 | -10.85 | +0.31~ | -22.89 | -22.33 | +0.56 | -24.17 | -23.93 | +0.24 |
| dig | code1m | 8955 | 541 | 6 | -12.47 | -12.52 | -0.05~ | -24.76 | -24.35 | +0.41 | -25.98 | -25.88 | +0.10~ |
| email | docs1m | 147183 | 1 | 0 | +0.11~ | +0.81 | +0.70 | -2.24 | -1.32 | +0.91 | -2.21 | -1.71 | +0.49 |
| email | code1m | 141122 | 1 | 0 | +0.39 | +1.17 | +0.79 | -2.09 | -1.13 | +0.97 | -2.10 | -1.50 | +0.59 |
| word-eq | mix64k | 14202 | 940 | 6 | +1.29 | +1.43 | +0.14 | +0.42 | +0.37 | -0.05~ | +0.28 | +0.36 | +0.08~ |
| word-eq | docs64k | 9716 | 22 | 0 | +0.45 | +0.89 | +0.43 | +0.06~ | +1.54 | +1.48 | -0.03~ | +2.10 | +2.12 |
| word-eq | docs1m | 158007 | 390 | 0 | +1.31 | +2.16 | +0.85 | -0.88 | -0.03~ | +0.86 | -1.28 | -0.37 | +0.91 |
| word-eq | code64k | 9210 | 26 | 0 | +0.57 | +1.03 | +0.46 | +0.14~ | +0.58 | +0.44 | +0.06~ | +1.07 | +1.01 |
| word-eq | code1m | 143516 | 111 | 0 | +1.42 | +2.27 | +0.85 | -1.00 | -0.18~ | +0.82 | -1.42 | -0.52 | +0.90 |
| hex-run | short | 4 | 4 | 75 | +2.00 | +1.02 | -0.97 | +16.62 | +5.92 | -10.70 | +13.92 | +2.10 | -11.82 |
| hex-run | prose64k | 10454 | 10455 | 85 | +2.62 | +1.43~ | -1.20~ | +4.30 | +0.07~ | -4.23 | +3.26 | +0.24~ | -3.03 |
| hex-run | digits64k | 9057 | 9058 | 51 | +2.27 | +2.53 | +0.27 | +3.91 | +1.75 | -2.17 | +3.07 | +1.14 | -1.94 |
| hex-run | prose1m | 166490 | 166490 | 85 | +0.04~ | +0.45 | +0.41 | +0.18~ | -3.59 | -3.77 | -0.82 | -3.62 | -2.80 |
| hex-run | mix64k | 15102 | 15102 | 69 | -0.79 | +0.74 | +1.53 | +0.30~ | -0.93 | -1.23 | -0.09~ | -1.66 | -1.57 |
| hex-run | docs64k | 12317 | 12317 | 83 | -0.80 | -1.91 | -1.11 | +0.96 | -3.03 | -3.98 | -0.06~ | -2.96 | -2.90 |
| hex-run | docs1m | 189599 | 189599 | 84 | -0.38 | +0.11~ | +0.49 | +0.31 | -3.40 | -3.71 | -0.70 | -3.53 | -2.84 |
| hex-run | code64k | 9952 | 9952 | 84 | +2.69 | +1.53 | -1.16 | +4.25 | +0.16 | -4.09 | +3.20 | +0.25 | -2.95 |
| hex-run | code1m | 160839 | 160839 | 84 | +0.29 | +0.76 | +0.47 | +0.24~ | -3.47 | -3.71 | -0.78 | -3.52 | -2.74 |
| bounded | short | 7 | 8 | 43 | +4.05 | +3.71 | -0.35~ | +12.18 | +4.68 | -7.50 | +10.22 | +3.11 | -7.11 |
| bounded | prose64k | 10079 | 10080 | 45 | +4.08 | +4.47 | +0.39~ | +5.65 | +2.87 | -2.78 | +4.84 | +2.21 | -2.63 |
| bounded | digits64k | 5052 | 437 | 8 | +0.59 | +0.63 | +0.04~ | -0.92 | -0.88 | +0.04~ | -1.13 | -1.17 | -0.04~ |
| bounded | prose1m | 161475 | 161476 | 45 | +3.75 | +4.08 | +0.32~ | +5.22 | +2.40 | -2.82 | +4.32 | +1.94 | -2.38 |
| bounded | mix64k | 13005 | 4007 | 31 | +1.49~ | +1.27~ | -0.22~ | +1.26~ | +0.41~ | -0.85~ | +0.91~ | +0.18~ | -0.74~ |
| bounded | docs64k | 9304 | 9040 | 52 | +0.79 | +2.07 | +1.28 | +2.15 | -0.23~ | -2.37 | +0.94 | -1.05 | -1.99 |
| bounded | docs1m | 147185 | 143033 | 52 | +1.06 | +2.21 | +1.16 | +1.55 | -0.87 | -2.42 | +0.73 | -1.32 | -2.04 |
| bounded | code64k | 8510 | 7979 | 51 | +1.57 | +0.99 | -0.58~ | +2.76 | -0.30~ | -3.06 | +2.42 | -0.88 | -3.30 |
| bounded | code1m | 141122 | 128491 | 52 | +1.38 | +2.52 | +1.14 | +1.30 | -0.75 | -2.05 | +0.48 | -1.25 | -1.73 |
| dfa-hat | short | 3 | 1 | 0 | +0.63 | +1.65 | +1.02 | +6.14 | +7.06 | +0.91 | +2.20 | +3.06 | +0.86 |
| dfa-hat | prose64k | 4717 | 1 | 0 | +1.32 | +2.03 | +0.71 | -0.91 | -0.14 | +0.77 | -1.04 | -0.27 | +0.77 |
| dfa-hat | digits64k | 1 | 1 | 0 | -3289.00 | -3962.98 | -673.98 | -11009.33 | -11011.61 | -2.28~ | -11706.53 | -11703.10 | +3.43~ |
| dfa-hat | prose1m | 75836 | 1 | 0 | +3.15 | +3.97 | +0.82 | -3.79 | -2.83 | +0.97 | -4.11 | -2.97 | +1.14 |
| dfa-hat | mix64k | 1 | 1 | 0 | -3297.13 | -3969.20 | -672.07 | -11020.11 | -11018.44 | +1.67~ | -11714.24 | -11709.60 | +4.64~ |
| dfa-hat | docs64k | 5668 | 8 | 0 | +1.04 | +1.78 | +0.74 | -0.95 | -0.16 | +0.79 | -1.05 | -0.30 | +0.75 |
| dfa-hat | docs1m | 89993 | 182 | 0 | +1.95 | +2.93 | +0.98 | -3.93 | -3.28 | +0.65 | -4.31 | -3.35 | +0.96 |
| dfa-hat | code64k | 5119 | 58 | 1 | +0.96 | +1.67 | +0.70 | -1.13 | -0.33 | +0.81 | -1.25 | -0.50 | +0.74 |
| dfa-hat | code1m | 79608 | 466 | 0 | +2.29 | +3.29 | +1.00 | -3.77 | -3.08 | +0.69 | -3.99 | -2.93 | +1.06 |
| vm-hat | prose64k | 4278 | 126 | 3 | -1.74 | -0.87 | +0.87 | -2.88 | -2.78 | +0.10 | -3.30 | -3.26 | +0.04~ |
| vm-hat | prose1m | 68248 | 2262 | 3 | +0.50 | +2.10 | +1.60 | -5.29 | -5.39 | -0.10~ | -5.79 | -5.79 | -0.00~ |
| vm-hat | mix64k | 6008 | 253 | 4 | -1.05 | -0.09~ | +0.96 | -1.85 | -1.72 | +0.14~ | -2.19 | -2.15 | +0.04~ |
| vm-hat | docs64k | 4096 | 252 | 5 | -1.83 | -0.97 | +0.86 | -3.01 | -2.92 | +0.09 | -3.45 | -3.39 | +0.06~ |
| vm-hat | docs1m | 62693 | 3202 | 4 | +0.38 | +2.00 | +1.62 | -5.67 | -5.78 | -0.10~ | -6.19 | -6.18 | +0.01~ |
| vm-hat | code64k | 3328 | 202 | 5 | -1.79 | -0.97 | +0.82 | -3.27 | -3.20 | +0.08~ | -3.80 | -3.70 | +0.11~ |
| vm-hat | code1m | 53962 | 3104 | 5 | -0.10~ | +1.62 | +1.72 | -6.16 | -6.25 | -0.09~ | -6.71 | -6.67 | +0.04~ |
| vm-hat-1 | short | 2 | 1 | 0 | -2.26 | -1.88 | +0.38 | +3.54 | +3.76 | +0.23~ | -1.09 | -0.41 | +0.68 |
| vm-hat-1 | prose64k | 2210 | 4 | 0 | -3.57 | -3.61 | -0.05~ | -5.23 | -5.02 | +0.22 | -5.64 | -5.87 | -0.23 |
| vm-hat-1 | prose1m | 34121 | 66 | 0 | -2.14 | -2.43 | -0.29 | -8.75 | -8.52 | +0.24 | -9.02 | -9.55 | -0.53 |
| vm-hat-1 | mix64k | 3023 | 19 | 0 | -2.56 | -2.57 | -0.02~ | -3.66 | -3.45 | +0.22 | -4.00 | -4.22 | -0.21 |
| vm-hat-1 | docs64k | 38 | 1 | 0 | -167.33 | -167.59 | -0.25~ | -293.41 | -293.23 | +0.17~ | -305.87 | -307.18 | -1.32 |
| vm-hat-1 | docs1m | 730 | 1 | 0 | -141.10 | -141.13 | -0.03~ | -247.49 | -247.10 | +0.39~ | -257.53 | -258.79 | -1.26 |
| vm-hat-1 | code64k | 14 | 1 | 0 | -451.52 | -451.52 | -0.00~ | -791.88 | -791.71 | +0.18~ | -824.43 | -827.02 | -2.60 |
| vm-hat-1 | code1m | 773 | 1 | 0 | -133.54 | -133.95 | -0.41~ | -232.66 | -232.56 | +0.10~ | -242.32 | -243.41 | -1.09 |

### 2.4 The cost of the machinery with nothing to keep

A `first` row on a 40-byte subject is one call and one use. The kept-minus-unkept difference there is the keep machinery's own fixed cost (the state struct, the `always_inline` `__impl`, the pointer-held state), measured in ns per call:

| cell | 8 B V3-V1 | SSE2 S3-S1 | AVX2 A3-A1 |
|---|---|---|---|
| dig | +0.32 | +2.15 | +0.23~ |
| hex-run | +1.38 | +1.22 | +1.75 |
| bounded | +0.26 | +1.69 | +0.43 |
| dfa-hat | +2.91 | +2.63 | +2.05 |
| vm-hat-1 | not timed (same code) | not timed (same code) | not timed (same code) |

Cells missing from the table do not reach the site on `short`. The same term shows in the multi-call cells where nothing can be reused: dfa-hat (one call; kept-served 0%) pays +0.70 to +1.00 ns/use at 8 B (6 of 6 subjects with uses >= 100), +0.65 to +0.97 at SSE2 and +0.74 to +1.14 at AVX2, and the same figure appears in the `first` rows of the same subjects (for example prose64k first V3-V1 = +3,268 ns over 4,717 uses). In `first` generally the kept variant is a REGRESSION against unkept in 26 of 50 rows (8 B), 33 of 43 (SSE2) and 19 of 43 (AVX2). So the keep has a per-use or per-call cost of order +0.2 to +2.9 ns, and it only pays where reuse saves more than that.

## 3. The alignment prologue

### 3.1 Prologue effect per cell and width (`all` mode)

"prologue alone" = X2 vs X1; "on top of keep" = X4 vs X3. ns/use as before (subjects with uses >= 100).

| width | cell | n | prologue alone X2-X1 W/R/N | n(uses>=100) | median ns/use | range | prologue on top of keep X4-X3 W/R/N | median ns/use |
|---|---|---|---|---|---|---|---|---|
| 8 B | dig | 9 | 0/4/5 | 6 | +0.82 | +0.06 .. +2.07 | 2/4/3 | +1.10 |
| 8 B | email | 2 | 0/2/0 | 2 | +0.87 | +0.71 .. +1.02 | 0/2/0 | +1.39 |
| 8 B | word-eq | 5 | 1/2/2 | 5 | -0.12 | -0.24 .. +1.00 | 2/2/1 | +0.09 |
| 8 B | hex-run | 9 | 4/4/1 | 8 | +1.05 | -1.58 .. +3.11 | 1/1/7 | -0.04 |
| 8 B | bounded | 9 | 4/4/1 | 8 | +0.01 | -1.88 .. +0.99 | 3/3/3 | +0.25 |
| 8 B | dfa-hat | 9 | 0/7/2 | 6 | +1.37 | +0.36 .. +2.46 | 0/3/6 | +0.67 |
| 8 B | vm-hat | 7 | 0/7/0 | 7 | +0.70 | +0.61 .. +1.37 | 6/0/1 | -0.28 |
| 8 B | vm-hat-1 | 8 | 1/2/5 | 5 | +0.09 | -4.09 .. +0.97 | 4/4/0 | +0.63 |
| SSE2 | dig | 9 | 1/2/6 | 6 | +0.11 | -3.11 .. +0.28 | 0/1/8 | +0.08 |
| SSE2 | email | 2 | 0/2/0 | 2 | +0.68 | +0.68 .. +0.68 | 0/2/0 | +0.97 |
| SSE2 | word-eq | 5 | 0/2/3 | 5 | +0.08 | +0.02 .. +0.84 | 2/2/1 | +0.06 |
| SSE2 | hex-run | 9 | 4/5/0 | 8 | +0.95 | -3.39 .. +2.02 | 3/0/6 | -0.08 |
| SSE2 | bounded | 9 | 5/1/3 | 8 | -0.56 | -3.99 .. +0.20 | 0/3/6 | +0.05 |
| SSE2 | dfa-hat | 9 | 0/6/3 | 6 | +0.48 | +0.16 .. +0.92 | 0/6/3 | +0.49 |
| SSE2 | vm-hat | 7 | 0/7/0 | 7 | +0.48 | +0.30 .. +0.54 | 0/7/0 | +0.32 |
| SSE2 | vm-hat-1 | 8 | 0/5/3 | 5 | +0.31 | +0.00 .. +1.82 | 0/5/3 | +0.24 |
| AVX2 | dig | 9 | 1/3/5 | 6 | +0.21 | -4.95 .. +0.42 | 0/5/4 | +0.59 |
| AVX2 | email | 2 | 0/2/0 | 2 | +1.01 | +1.01 .. +1.01 | 0/2/0 | +1.49 |
| AVX2 | word-eq | 5 | 0/2/3 | 5 | +0.07 | +0.04 .. +1.49 | 2/3/0 | +0.25 |
| AVX2 | hex-run | 9 | 2/6/1 | 8 | +1.44 | -2.78 .. +2.23 | 0/3/6 | +0.14 |
| AVX2 | bounded | 9 | 5/2/2 | 8 | -0.60 | -4.46 .. +0.91 | 0/5/4 | +0.58 |
| AVX2 | dfa-hat | 9 | 0/6/3 | 6 | +0.75 | +0.29 .. +1.29 | 0/6/3 | +0.82 |
| AVX2 | vm-hat | 7 | 0/7/0 | 7 | +0.59 | +0.43 .. +0.81 | 0/7/0 | +0.61 |
| AVX2 | vm-hat-1 | 8 | 4/3/1 | 5 | +0.05 | -1.22 .. +0.16 | 0/4/4 | +0.68 |

### 3.2 Per subject: where the head serves and what it does (bounded, hex-run, dfa-hat, word-eq, `all`)

Per-use ns versus the walk, plain -> prologue, with the share of uses answered in the scalar head.

| cell | subject | uses | head-served % | 8 B V1 -> V2 | SSE2 S1 -> S2 | AVX2 A1 -> A2 |
|---|---|---|---|---|---|---|
| bounded | short | 7 | 71 | +4.05 -> +1.85 | +12.18 -> +3.85 | +10.22 -> +2.94 |
| bounded | prose64k | 10079 | 74 | +4.08 -> +2.44 | +5.65 -> +1.66 | +4.84 -> +0.38~ |
| bounded | digits64k | 5052 | 8 | +0.59 -> +0.78 | -0.92 -> -0.72 | -1.13 -> -0.62 |
| bounded | prose1m | 161475 | 75 | +3.75 -> +1.87 | +5.22 -> +1.29 | +4.32 -> +0.30~ |
| bounded | mix64k | 13005 | 31 | +1.49~ -> +1.31~ | +1.26~ -> +0.89~ | +0.91~ -> +0.56~ |
| bounded | docs64k | 9304 | 63 | +0.79 -> +1.78 | +2.15 -> +1.01 | +0.94 -> -0.05~ |
| bounded | docs1m | 147185 | 61 | +1.06 -> +1.64 | +1.55 -> +0.97 | +0.73 -> -0.13~ |
| bounded | code64k | 8510 | 59 | +1.57 -> +0.02~ | +2.76 -> +2.22 | +2.42 -> +3.33 |
| bounded | code1m | 141122 | 58 | +1.38 -> +2.28 | +1.30 -> +1.28 | +0.48 -> +0.25~ |
| hex-run | short | 4 | 25 | +2.00 -> +1.58 | +16.62 -> +11.54 | +13.92 -> +4.41 |
| hex-run | prose64k | 10454 | 38 | +2.62 -> +2.29 | +4.30 -> +2.14 | +3.26 -> +1.20~ |
| hex-run | digits64k | 9057 | 73 | +2.27 -> +0.69 | +3.91 -> +0.52 | +3.07 -> +0.30 |
| hex-run | prose1m | 166490 | 37 | +0.04~ -> +2.47 | +0.18~ -> +1.92 | -0.82 -> +0.87 |
| hex-run | mix64k | 15102 | 68 | -0.79 -> +2.32 | +0.30~ -> +2.31 | -0.09~ -> +2.14 |
| hex-run | docs64k | 12317 | 45 | -0.80 -> -1.44 | +0.96 -> +1.61 | -0.06~ -> +1.47 |
| hex-run | docs1m | 189599 | 45 | -0.38 -> +2.08 | +0.31 -> +1.56 | -0.70 -> +0.64 |
| hex-run | code64k | 9952 | 42 | +2.69 -> +2.14 | +4.25 -> +1.93 | +3.20 -> +4.40 |
| hex-run | code1m | 160839 | 42 | +0.29 -> +2.76 | +0.24~ -> +1.94 | -0.78 -> +1.17 |
| dfa-hat | short | 3 | 0 | +0.63 -> +0.96 | +6.14 -> +6.28 | +2.20 -> +2.37 |
| dfa-hat | prose64k | 4717 | 22 | +1.32 -> +1.79 | -0.91 -> -0.68 | -1.04 -> -0.65 |
| dfa-hat | digits64k | 1 | 0 | -3289.00 -> -3316.38 | -11009.33 -> -11020.29 | -11706.53 -> -11707.56 |
| dfa-hat | prose1m | 75836 | 21 | +3.15 -> +5.42 | -3.79 -> -3.02 | -4.11 -> -2.92 |
| dfa-hat | mix64k | 1 | 0 | -3297.13 -> -3345.87 | -11020.11 -> -11029.42 | -11714.24 -> -11716.65 |
| dfa-hat | docs64k | 5668 | 25 | +1.04 -> +1.40 | -0.95 -> -0.79 | -1.05 -> -0.75 |
| dfa-hat | docs1m | 89993 | 24 | +1.95 -> +4.23 | -3.93 -> -3.20 | -4.31 -> -3.20 |
| dfa-hat | code64k | 5119 | 23 | +0.96 -> +1.37 | -1.13 -> -0.92 | -1.25 -> -0.85 |
| dfa-hat | code1m | 79608 | 22 | +2.29 -> +4.75 | -3.77 -> -2.84 | -3.99 -> -2.70 |
| word-eq | mix64k | 14202 | 31 | +1.29 -> +1.05 | +0.42 -> +0.44 | +0.28 -> +0.31 |
| word-eq | docs64k | 9716 | 64 | +0.45 -> +0.32 | +0.06~ -> +0.09~ | -0.03~ -> +0.03~ |
| word-eq | docs1m | 158007 | 62 | +1.31 -> +1.77 | -0.88 -> -0.19~ | -1.28 -> -0.03~ |
| word-eq | code64k | 9210 | 60 | +0.57 -> +0.45 | +0.14~ -> +0.22 | +0.06~ -> +0.13~ |
| word-eq | code1m | 143516 | 58 | +1.42 -> +2.42 | -1.00 -> -0.17~ | -1.42 -> +0.07~ |

### 3.3 Single-call fixed cost (short, `first`, X2 - X1, ns per call)

| cell | 8 B V2-V1 | SSE2 S2-S1 | AVX2 A2-A1 |
|---|---|---|---|
| dig | +0.05~ | +0.20~ | +0.18~ |
| hex-run | -0.07~ | -0.62~ | +0.20~ |
| bounded | +0.05~ | -0.37~ | -0.16~ |
| dfa-hat | +1.08 | +0.63~ | +0.35~ |
| vm-hat-1 | +0.28 | +0.15~ | +0.18~ |

### 3.4 Reading

- **Where the prologue works: bounded near hits at SIMD width.** On bounded prose the head answers 74-75% of uses (the counters match vecspike section 4: head 74% on prose64k and 75% on prose1m, blocks per use 1.00 -> 0.25 on prose1m). The loss against the walk falls from +4.08/+3.75 (V1, prose64k/prose1m) to +2.44/+1.87 at 8 B (40% / 50% removed), from +5.65/+5.22 to +1.66/+1.29 at SSE2 (71% / 75%) and from +4.84/+4.32 to +0.38~/+0.30~ at AVX2 (92% / 93%, both now NULL against the walk). Bounded docs are the opposite at 8 B (docs64k +0.79 -> +1.78, docs1m +1.06 -> +1.64, code1m +1.38 -> +2.28; code64k +1.57 -> +0.02~), and at AVX2 turn to NULL (docs64k -0.05~, docs1m -0.13~, code1m +0.25~; code64k worsens +2.42 -> +3.33). Bounded totals vs plain: 8 B 4W/4R/1N, SSE2 5/1/3 (median -0.56 ns/use), AVX2 5/2/2 (-0.60).
- **Where it loses.** hex-run: SSE2 4W/5R, AVX2 2W/6R, 8 B 4W/4R; it removes loss on digits64k (-3.39 SSE2, -2.78 AVX2, -1.58 8 B ns/use) and prose64k (-2.16, -2.06, -0.33~) and adds it on the 1 MiB subjects (hex-run prose1m: +1.74 SSE2, +1.70 AVX2, +2.43 8 B; at 8 B docs1m +2.46 and code1m +2.47) although the counters show fewer blocks (1.26 -> 0.76 per use at 8 B). dfa-hat: 0 WIN, 6-7 REG at every width (+0.16 to +2.46 ns/use); vm-hat: 0/7/0 at every width (+0.30 to +1.37) with only 1-2% of uses head-served; dig/word-eq/vm-hat-1 mostly NULL.
- **Fixed cost.** On a single call it is inside the floor everywhere except dfa-hat at 8 B (+1.08 ns), vm-hat-1 at 8 B (+0.28 ns) (table 3.3).
- **Prologue on top of keep (X4 vs X3).** Mostly a loss or NULL once the cache is there: SSE2 5W/26R/27N (hex-run 3/0/6, bounded 0/3/6), AVX2 2W/35R/21N, 8 B 18W/19R/21N (10 of the 18 8 B WINs are vm-hat 6 of 7 and vm-hat-1 4 of 8, cells whose heads serve 0-2% of uses). V4 is worse than V2 on bounded prose at 8 B: +3.11 vs +2.44 (prose64k), +2.71 vs +1.87 (prose1m) ns/use, although V4's counters on prose1m show 60% of uses head-served plus 19% cache-served.


## 4. vecspike2: the multi-position class filter for dfa-hat

Baselines: each arm is compared with its own width's P1 (V1 at 8 B, S1 at SSE2, A1 at AVX2), timed in the same interleave, and with the walk V0. A WIN means faster. The candidate counts (`counts2.tsv`, `all` mode) are identical at the three widths.

### 4.1 Candidates handed to the DFA

| subject | calls | P1 cands | P2 | P3 | P4 | P3W |
|---|---|---|---|---|---|---|
| short | 1 | 2 | 0 | 0 | 0 | 0 |
| prose64k | 1 | 4717 | 562 | 34 | 4 | 11 |
| digits64k | 1 | 0 | 0 | 0 | 0 | 0 |
| prose1m | 1 | 75835 | 9328 | 551 | 52 | 141 |
| mix64k | 1 | 0 | 0 | 0 | 0 | 0 |
| docs64k | 8 | 5668 | 877 | 117 | 45 | 34 |
| docs1m | 182 | 89992 | 10824 | 1570 | 614 | 376 |
| code64k | 58 | 5118 | 757 | 141 | 95 | 73 |
| code1m | 466 | 79608 | 11917 | 1563 | 907 | 718 |

P2 removes 84.5-88.1% of P1's candidates on the six dense subjects and P3 97.2-99.3%.

### 4.2 WIN / REGRESSION / NULL per arm per width

Over the 18 groups (9 subjects x first/all) and over the 12 dense groups (prose, docs, code x first/all). "vs walk" counts the arm against V0 over all 18 groups.

| arm | width | vs own P1 (18 groups) W/R/N | vs own P1 (12 dense groups) W/R/N | vs walk (18 groups) W/R/N |
|---|---|---|---|---|
| V1 (=P1) | 8 B | - | - | 4/14/0 |
| P2w | 8 B | 14/4/0 | 12/0/0 | 14/4/0 |
| P3w | 8 B | 12/4/2 | 12/0/0 | 12/6/0 |
| P4w | 8 B | 7/9/2 | 7/3/2 | 4/14/0 |
| PWw | 8 B | 4/14/0 | 4/8/0 | 4/14/0 |
| S1 (=P1) | SSE2 | - | - | 16/2/0 |
| P2s | SSE2 | 14/4/0 | 12/0/0 | 16/2/0 |
| P3s | SSE2 | 12/6/0 | 12/0/0 | 16/2/0 |
| P4s | SSE2 | 12/6/0 | 12/0/0 | 16/2/0 |
| PWs | SSE2 | 12/6/0 | 12/0/0 | 16/2/0 |
| A1 (=P1) | AVX2 | - | - | 16/2/0 |
| P2a | AVX2 | 12/6/0 | 12/0/0 | 16/2/0 |
| P3a | AVX2 | 12/6/0 | 12/0/0 | 16/2/0 |
| P4a | AVX2 | 12/6/0 | 12/0/0 | 16/2/0 |
| PWa | AVX2 | 12/6/0 | 12/0/0 | 16/2/0 |

### 4.3 Per subject, per width

Cells show the arm's change versus its own P1 in percent (negative = faster; `~` = within the floor). "P1 vs walk" is P1 relative to V0 in percent; "best arm vs walk" names the fastest of P2/P3/P4/P3W (suffix removed) and its change versus V0.


8 B (P1 = V1). Cells: P1 ns; then Delta vs P1 in % (~ = within floor); last column is the walk V0.

| subject | mode | P1 ns | P2 | P3 | P4 | P3W | walk V0 ns | P1 vs walk | best arm vs walk |
|---|---|---|---|---|---|---|---|---|---|
| short | first | 19.0 | -21.6% | +1.8%~ | +35.7% | +58.6% | 17.4 | +9.2% | P2 -14.4% |
| short | all | 18.9 | -22.5% | -0.7%~ | +36.3% | +61.3% | 17.0 | +11.0% | P2 -14.0% |
| prose64k | first | 32920.1 | -36.3% | -24.7% | +1.6%~ | +27.3% | 26923.9 | +22.3% | P2 -22.1% |
| prose64k | all | 32848.9 | -36.2% | -24.2% | +1.8%~ | +27.6% | 26841.0 | +22.4% | P2 -21.9% |
| digits64k | first | 9077.9 | +92.7% | +171.6% | +267.8% | +359.7% | 12358.8 | -26.5% | P2 +41.6% |
| digits64k | all | 9079.0 | +92.8% | +144.7% | +267.9% | +359.6% | 12359.1 | -26.5% | P2 +41.6% |
| prose1m | first | 1606194.5 | -72.4% | -75.3% | -66.6% | -58.2% | 1370524.9 | +17.2% | P3 -71.1% |
| prose1m | all | 1603830.7 | -72.3% | -75.3% | -66.6% | -58.2% | 1369159.2 | +17.1% | P3 -71.0% |
| mix64k | first | 9080.3 | +92.8% | +151.1% | +267.8% | +359.4% | 12366.6 | -26.6% | P2 +41.6% |
| mix64k | all | 9078.1 | +92.8% | +157.3% | +267.8% | +359.4% | 12374.6 | -26.6% | P2 +41.4% |
| docs64k | first | 1844.9 | -29.1% | -28.1% | -4.7% | +18.2% | 1493.3 | +23.5% | P2 -12.4% |
| docs64k | all | 35198.3 | -32.9% | -28.2% | -3.5% | +20.1% | 29404.2 | +19.7% | P2 -19.6% |
| docs1m | first | 1841.7 | -29.3% | -28.2% | -4.9% | +18.0% | 1494.9 | +23.2% | P2 -12.9% |
| docs1m | all | 1764990.1 | -72.4% | -77.0% | -69.2% | -61.7% | 1579598.2 | +11.7% | P3 -74.3% |
| code64k | first | 1656.4 | -26.0% | -20.4% | +9.7% | +36.8% | 1439.2 | +15.1% | P2 -14.8% |
| code64k | all | 33729.3 | -31.2% | -23.1% | +3.4% | +27.9% | 28840.7 | +17.0% | P2 -19.5% |
| code1m | first | 1658.2 | -26.1% | -19.0% | +9.6% | +36.6% | 1437.0 | +15.4% | P2 -14.7% |
| code1m | all | 1598537.2 | -68.2% | -74.4% | -65.6% | -57.3% | 1414978.1 | +13.0% | P3 -71.1% |

SSE2 (P1 = S1). Cells: P1 ns; then Delta vs P1 in % (~ = within floor); last column is the walk V0.

| subject | mode | P1 ns | P2 | P3 | P4 | P3W | walk V0 ns | P1 vs walk | best arm vs walk |
|---|---|---|---|---|---|---|---|---|---|
| short | first | 35.4 | -18.1% | +32.4% | +15.3% | +124.0% | 17.4 | +102.9% | P2 +66.2% |
| short | all | 35.4 | -17.3% | +35.4% | +14.2% | +124.2% | 17.0 | +107.7% | P2 +71.7% |
| prose64k | first | 22375.6 | -73.1% | -77.5% | -69.8% | -56.4% | 26923.9 | -16.9% | P3 -81.3% |
| prose64k | all | 22362.1 | -73.1% | -77.5% | -69.8% | -56.4% | 26841.0 | -16.7% | P3 -81.2% |
| digits64k | first | 1364.6 | +89.1% | +249.3% | +392.4% | +603.9% | 12358.8 | -89.0% | P2 -79.1% |
| digits64k | all | 1364.6 | +89.1% | +249.1% | +392.0% | +604.0% | 12359.1 | -89.0% | P2 -79.1% |
| prose1m | first | 1078187.3 | -90.8% | -92.5% | -89.9% | -85.5% | 1370524.9 | -21.3% | P3 -94.1% |
| prose1m | all | 1077245.3 | -90.8% | -92.5% | -89.9% | -85.5% | 1369159.2 | -21.3% | P3 -94.1% |
| mix64k | first | 1362.1 | +89.4% | +250.0% | +392.7% | +605.1% | 12366.6 | -89.0% | P2 -79.1% |
| mix64k | all | 1362.5 | +89.2% | +250.0% | +392.7% | +604.8% | 12374.6 | -89.0% | P2 -79.2% |
| docs64k | first | 1261.9 | -58.9% | -73.7% | -69.8% | -58.9% | 1493.3 | -15.5% | P3 -77.8% |
| docs64k | all | 23955.2 | -64.2% | -75.5% | -69.8% | -58.0% | 29404.2 | -18.5% | P3 -80.0% |
| docs1m | first | 1258.5 | -58.9% | -73.7% | -69.8% | -58.8% | 1494.9 | -15.8% | P3 -77.9% |
| docs1m | all | 1247638.7 | -81.3% | -92.6% | -90.6% | -87.1% | 1579598.2 | -21.0% | P3 -94.2% |
| code64k | first | 1103.2 | -61.9% | -73.4% | -65.0% | -50.6% | 1439.2 | -23.3% | P3 -79.6% |
| code64k | all | 22990.4 | -63.6% | -71.2% | -63.0% | -51.0% | 28840.7 | -20.3% | P3 -77.1% |
| code1m | first | 1102.8 | -61.7% | -73.3% | -65.0% | -50.5% | 1437.0 | -23.3% | P3 -79.5% |
| code1m | all | 1116872.6 | -77.8% | -91.5% | -88.9% | -84.9% | 1414978.1 | -21.1% | P3 -93.3% |

AVX2 (P1 = A1). Cells: P1 ns; then Delta vs P1 in % (~ = within floor); last column is the walk V0.

| subject | mode | P1 ns | P2 | P3 | P4 | P3W | walk V0 ns | P1 vs walk | best arm vs walk |
|---|---|---|---|---|---|---|---|---|---|
| short | first | 24.0 | +22.6% | +97.0% | +72.1% | +214.5% | 17.4 | +37.6% | P2 +68.6% |
| short | all | 23.6 | +24.9% | +101.3% | +74.9% | +226.6% | 17.0 | +38.6% | P2 +73.1% |
| prose64k | first | 21760.3 | -79.0% | -90.0% | -87.4% | -75.1% | 26923.9 | -19.2% | P3 -91.9% |
| prose64k | all | 21764.3 | -78.9% | -90.0% | -87.4% | -75.1% | 26841.0 | -18.9% | P3 -91.9% |
| digits64k | first | 668.9 | +89.7% | +178.0% | +300.3% | +691.3% | 12358.8 | -94.6% | P2 -89.7% |
| digits64k | all | 668.4 | +89.7% | +178.4% | +300.9% | +691.9% | 12359.1 | -94.6% | P2 -89.7% |
| prose1m | first | 1052977.9 | -92.8% | -96.7% | -95.9% | -91.7% | 1370524.9 | -23.2% | P3 -97.5% |
| prose1m | all | 1053286.6 | -92.8% | -96.7% | -95.9% | -91.7% | 1369159.2 | -23.1% | P3 -97.4% |
| mix64k | first | 668.5 | +89.3% | +178.6% | +300.7% | +691.5% | 12366.6 | -94.6% | P2 -89.8% |
| mix64k | all | 668.0 | +89.4% | +178.8% | +300.8% | +692.0% | 12374.6 | -94.6% | P2 -89.8% |
| docs64k | first | 1233.3 | -63.7% | -84.8% | -86.3% | -76.4% | 1493.3 | -17.4% | P4 -88.7% |
| docs64k | all | 23386.7 | -69.5% | -87.0% | -86.5% | -75.8% | 29404.2 | -20.5% | P3 -89.7% |
| docs1m | first | 1233.8 | -63.6% | -84.8% | -86.2% | -76.4% | 1494.9 | -17.5% | P4 -88.6% |
| docs1m | all | 1201494.1 | -87.0% | -96.1% | -95.8% | -92.4% | 1579598.2 | -23.9% | P3 -97.1% |
| code64k | first | 1070.3 | -67.9% | -87.2% | -84.7% | -71.4% | 1439.2 | -25.6% | P3 -90.5% |
| code64k | all | 22399.8 | -69.3% | -83.3% | -80.8% | -70.0% | 28840.7 | -22.3% | P3 -87.0% |
| code1m | first | 1071.3 | -67.8% | -87.0% | -84.5% | -71.4% | 1437.0 | -25.5% | P3 -90.3% |
| code1m | all | 1101509.9 | -79.2% | -95.5% | -94.8% | -91.1% | 1414978.1 | -22.2% | P3 -96.5% |

### 4.4 Reading

- **Dense subjects (prose, docs, code; 12 groups).** At SSE2 and AVX2 every one of the four arms beats its P1 in 12 of 12 groups. At 8 B P2w and P3w do (12/12 each), P4w does in 7 (3 REG, 2 NULL: prose64k first/all NULL, code64k first/all and code1m first REG) and PWw (the P3W arm at 8 B) in 4 (8 REG: prose64k, docs64k, code64k both modes, docs1m first, code1m first). P3 versus P1: -23% to -77% (8 B), -71% to -93% (SSE2), -83% to -97% (AVX2). Against the walk, the speedup of P3 is 1.1-3.9x (8 B), 4.4-17.1x (SSE2), 7.7-39.2x (AVX2); P1 alone is 0.82-0.89x (8 B: slower than the walk), 1.20-1.27x (SSE2), 1.23-1.31x (AVX2).
- **Best arm.** At SSE2, P3 is the fastest or tied-fastest in 12 of the 12 dense groups (P2 is fastest on short, digits64k and mix64k). At AVX2 P3 or a P3/P4 tie in 10 of 12, P4 alone in 2 (docs64k first and docs1m first, 169 vs 187 and 170 vs 188 ns, the floors 10.1 and 4.4 ns). At 8 B P2 is fastest or tied-fastest in 8 of 12 dense groups (alone on prose64k, code64k, code1m `first` and prose64k, docs64k, code64k `all`; tied with P3 on docs64k and docs1m `first`) and P3 in 6 (alone on prose1m `first` and prose1m, docs1m, code1m `all`; plus the 2 ties). P4 versus P3 (dense `all`) costs +34-35% at 8 B, +23-34% at SSE2, +4-26% at AVX2 (NULL on docs64k and docs1m `all`: +112 and +4,383 ns).
- **The context (P3W).** It is the slowest of the K >= 2 arms on every dense group at all three widths: +66-69% over P3 at 8 B, +70-94% at SSE2, +79-149% at AVX2, and it is REGRESSION against P4 in all 18 dense `all` comparisons (6 subjects x 3 widths). It also hands the DFA fewer candidates than P4 on docs/code (docs1m 376 vs 614) and more than P4 on prose (prose1m 141 vs 52).
- **No-candidate rows (digits64k, mix64k).** Cost grows strictly with K at every width: over P1, P2 +89-93%, P3 +145-250%, P4 +268-393%, P3W +359-692%. At SIMD widths even P3W stays faster than the walk on these two subjects (P2s is 0.21x the walk's ns, P2a 0.10x); at 8 B P2w is 1.42x the walk.
- **Short (40 B).** The SIMD arms use the per-byte tail. In `first`: 8 B P1 19.0 ns, P2 14.9, P3 19.4, P4 25.8, P3W 30.2 (walk 17.4); SSE2 P1 35.4, P2 29.0, P3 46.8, P4 40.8, P3W 79.2; AVX2 P1 24.0, P2 29.4, P3 47.2, P4 41.3, P3W 75.4. The order in K is not monotone at the SIMD widths (P4 < P3), and P2 helps at 8 B and SSE2 but not at AVX2.
- **Prose first-mode.** prose64k has 4,717 P1 candidates and no match, so its `first` regime is the whole-subject scan and behaves as `all`: P2/P3 win at all widths (8 B -36%/-25%; SSE2 -73%/-77%; AVX2 -79%/-90%) and only P4w (+1.6%~) and PWw, the P3W arm at 8 B (+27%), lose.
- **AVX2 versus SSE2 (same arm).** Time ratio AVX2/SSE2 on the dense `all` groups: P1 0.96-0.99, P2 0.67-0.93, P3 0.43-0.57, P4 0.40-0.51, P3W 0.55-0.60; on digits64k/mix64k 0.49 (P1), 0.39-0.55 (P2-P3W). The counts are identical, the V1x control is NULL in 116 of 116 groups, so the `-mavx2` TU effect is not the source.

## 5. Predictions, by id

Verdict key: CONFIRMED / REFUTED / MIXED. Each cites the numbers; "counters" means the no-clock counting builds, "time" the timing logs. Ids follow the order of the numbered lists (V-n = vecspike section 6, item n; V2-n = vecspike2 section 7, item n).

### 5.1 vecspike section 6

**V-1. bounded (all 20 r17loss losses) is V2's case: V2 removes about 3/4 of the loss on prose and about 60% on docs; V3 alone removes less; V4 ~ V2 or slightly better. MIXED, mostly REFUTED in time.**
- Counters CONFIRMED: head-served 74% (prose64k), 75% (prose1m), 61-63% (docs); blocks per use prose1m V1 1.00 -> V2 0.25; V3 xcall 45% (prose), 52% (docs) with 0.65-0.75 blocks/use; V4 head 60% + xcall 19% (prose1m).
- Time at 8 B (ns/use vs walk, loss to remove): prose64k V1 +4.08, V2 +2.44 (40% removed), V3 +4.47 (-9%), V4 +3.11; prose1m +3.75, +1.87 (50%), +4.08, +2.71. Docs: V2 ADDS, docs64k +0.79 -> +1.78, docs1m +1.06 -> +1.64. Code is split (code64k +1.57 -> +0.02~, code1m +1.38 -> +2.28). So "3/4 on prose" and "60% on docs" are refuted at 8 B; "V3 removes less" is true (it removes nothing); "V4 ~ V2 or better" is refuted (V4 is 0.7-0.8 ns/use worse than V2 on prose).
- The prediction's magnitude does hold at the SIMD widths: S2 removes 71%/75% of the prose loss (S1 +5.65/+5.22 -> +1.66/+1.29) and A2 removes 92%/93% (A1 +4.84/+4.32 -> +0.38~/+0.30~).

**V-2. hex-run (17 of 19 losses) is V3's case: 84-85% of uses are served from an earlier call's block; V3 removes most of the +2.2-2.7 ns/use; V2 removes less than half. MIXED.**
- Counters CONFIRMED: kept-served 85% (prose64k/prose1m), 83-84% (docs/code), 51% (digits64k).
- 8 B time: V3 removes 46% on prose64k (+2.62 -> +1.43~) and 43% on code64k (+2.69 -> +1.53), nothing on digits64k (+2.27 -> +2.53, worse); of the other subjects docs64k improves (-0.80 -> -1.91) while prose1m (+0.04~ -> +0.45), mix64k (-0.79 -> +0.74), docs1m (-0.38 -> +0.11~) and code1m (+0.29~ -> +0.76) worsen. V2 removes 13% (prose64k), 20% (code64k) and 70% on digits64k (+2.27 -> +0.69). "V3 removes most" is REFUTED at 8 B; "V2 less than half" holds on prose/code and fails on digits64k.
- The kept vector does remove most of the loss at SIMD width: S3 removes 98% on prose64k (+4.30 -> +0.07~) and 96% on code64k (+4.25 -> +0.16), A3 93% (+3.26 -> +0.24~) and 92% (+3.20 -> +0.25); 55%/63% on digits64k.

**V-3. dfa-hat is one call per pass, so V3 = V1 by construction (xcall 0); only V2 can move it, and its loss should shrink by at most about a fifth. MIXED.**
- Counters: xcall is 0 on prose/digits/mix/short and 4, 72, 29, 211 on docs64k/docs1m/code64k/code1m (0.07-0.6% of uses); calls are 1 on prose/digits/mix/short but 8, 182, 58, 466 on docs64k/docs1m/code64k/code1m, so "one call per pass" holds for the contrived subjects only.
- Time: V3 is not equal to V1: +0.70 to +1.00 ns/use at 8 B on all six subjects with uses >= 100 (prose64k +0.71, prose1m +0.82, docs64k +0.74, docs1m +0.98, code64k +0.71, code1m +1.00), and +2.91 ns on short first; in `first` the same (prose64k first +3,268 ns / 4,717 uses). The prediction anticipated "any V3 delta on dfa-hat is layout": the delta is present where nothing can be kept, so it is a cost of the kept form itself (the logs cannot separate layout from the pointer-held state).
- V2 does not shrink the loss, it grows it: prose64k +1.32 -> +1.79, prose1m +3.15 -> +5.42, docs64k +1.04 -> +1.40, docs1m +1.95 -> +4.23, code64k +0.96 -> +1.37, code1m +2.29 -> +4.75 ns/use. REFUTED.

**V-4. vm-hat / vm-hat-1: neither V2 nor V3 should move them (head <= 2%, xcall <= 5%); deltas past the floor are layout. MIXED.**
- Counters CONFIRMED: head 1-2%, xcall 3-5% (vm-hat); head 0, xcall 0 (vm-hat-1).
- vm-hat: V2-V1 and V3-V1 are REGRESSION in 7 of 7 subjects at 8 B (V2 +0.61 to +1.37, V3 +0.82 to +1.72 ns/use), and the same sign at SSE2/AVX2 for the prologue (0/7/0 at both widths, +0.30 to +0.81). Past the floor, so the prediction's own rule attributes it to layout; the reading cannot separate it from the prologue's head loop, but the `first` rows (single call) of V2 on vm-hat show the same sign (0/7/0).
- vm-hat-1: V2-V1 1W/2R/5N, V3-V1 1W/1R/6N; mostly NULL as predicted.

**V-5. The sparse throughput rows: V2/V3 change nothing for SWAR; S*/A* are where a win comes from; V2's aligned loads can remove only cache-line splits, a small effect on x86. CONFIRMED.**
- The 12 sparse rows (dig prose64k/prose1m/docs64k/docs1m/code64k/code1m, vm-hat-1 docs64k/docs1m/code64k/code1m, dfa-hat digits64k/mix64k, `all`): V2-V1 is NULL in 9, REG in 2 (dig docs1m +19,412 ns = +6.2%, dig code1m +8,191 = +5.1%) and WIN in 1 (vm-hat-1 code1m -3,161 = -3.3%); V3-V1 is NULL in 8, REG in 2 (dig prose64k +327 ns = +4.5%, dig prose1m +7,531 = +6.6%), WIN in 2 (dfa-hat digits64k / mix64k -674 / -672 ns = -7.4%, no candidates, 0% kept-served: layout). The largest effect is 7.4%.
- S1 is 2.05-6.7x faster than V1 on all 12 and A1 2.28-13.6x faster (for example dig prose1m 114,041 -> 21,619 -> 11,346 ns).
- V2's aligned loads at SIMD width: S2-S1 REG in 6, NULL in 6, WIN in 0 (up to +7.1%); A2-A1 REG in 3 (up to +11%), WIN in 4 (vm-hat-1: -4.0%, -7.2%, -7.2%, -7.3%), NULL in 5. So the aligned loads are a small effect, positive only at 32 B on vm-hat-1.

**V-6. W = 64 on dense cells is a trade: S1/A1 should lose on dense near-hit cells, S3/A3 are the SIMD variants that can win them. CONFIRMED, with scope.**
- S1 loses to the walk on bounded in 7 of 9 subjects (REG on short, prose64k, prose1m, docs64k, docs1m, code64k, code1m; WIN digits64k; NULL mix64k), A1 on the same 7; S1 on hex-run in 6 (short, prose64k, digits64k, docs64k, docs1m, code64k), A1 in 4.
- S3 wins hex-run on 5 of 9 (prose1m -3.59, mix64k -0.93, docs64k -3.03, docs1m -3.40, code1m -3.47 ns/use) and A3 on 5 of 9 (-3.62, -1.66, -2.96, -3.53, -3.52). S3 wins bounded on 3 of 9 (digits64k, docs1m, code1m) and A3 on 5 of 9 (digits64k, docs64k, docs1m, code64k, code1m). Bounded prose stays REG (S3 +2.87/+2.40, A3 +2.21/+1.94 ns/use).

**V-7. V1x vs V1 isolates `-mavx2`. CONFIRMED (no effect).** V1x-V1 is NULL in 116 of 116 groups; median |diff| 0.04%, max 3.4% (hex-run mix64k all, whose own A/A is 3.2%). Nothing needs subtracting from the A* rows for the flag.

**V-8. short (40 B) SIMD rows are the MTAIL handicap, not the form. CONFIRMED as an effect; the attribution is not separately timed.** SSE2: S1 loses to the walk in 10 of 10 short groups (+3.5 to +23.6 ns); AVX2: A1 REG in 6 and WIN in 4; 8 B V1: WIN 4 / REG 6. S1 on the other 106 groups: 65 WIN / 33 REG / 8 NULL, so SSE2's loss on short is far above its behaviour elsewhere. The hand edit could not time a word-built tail, so the log cannot isolate the tail from the form.

### 5.2 vecspike2 section 7

**V2-1. P1's dense cells are candidate-bound: S1/A1 gain little over V1; every P2+ arm beats its own P1 at every width on prose/docs/code, in both regimes (the main prediction). MIXED.**
- "S1/A1 gain little over V1": REFUTED. On the 12 dense groups S1 is 29-33% faster than V1 and A1 31-35% faster.
- "Every P2+ arm beats its own P1": CONFIRMED at SSE2 and AVX2 (4 arms x 12 groups = 48/48 each) and for P2w and P3w (12/12 each); REFUTED for P4w (7 WIN / 3 REG / 2 NULL) and PWw, the P3W arm at 8 B (4 / 8 / 0).

**V2-2. P2 removes ~88% of the candidates and should take most of the win at w8. CONFIRMED.** P2 removes 84.5-88.1% (prose1m 75,835 -> 9,328 = 87.7%); on the 12 dense groups at 8 B, P2 delivers 92-100% of the best arm's gain (it is the best arm in 8).

**V2-3. P3 should be best or tied-best; at SIMD P4 ~ P3 (a slight loss) and at w8 P4 loses to P3 by more. MIXED.**
- P3 is best or tied-best on 12 of 12 dense groups at SSE2, 10 of 12 at AVX2 (P4 alone best on docs64k first and docs1m first by 18-19 ns), but only 6 of 12 at 8 B, where P2 is best or tied in 8 (for example prose64k `all`: P2w -11,885 vs P3w -7,935 ns against P1).
- P4 vs P3 on the dense `all` groups is a loss in 10 of 12 SIMD comparisons (the two NULLs are AVX2 docs64k and docs1m): +1.4 to +28.5 us (+23-34%) at SSE2, +0.1 to +8.4 us (+4-26%) at AVX2; at 8 B +8.5 to +139.9 us (+34-35%). The sign is as predicted; the SIMD loss is larger than the predicted 7-17 us on 1 MiB subjects (+24.7 us on docs1m SSE2), and in relative terms the 8 B loss is of the same order as the SIMD loss.

**V2-4. P3W ~ P4 or slightly worse than P3; P3W >= P3 on prose, a wash against P3 on docs/code. REFUTED.** P3W is slower than P3 by +66-69% (8 B), +70-94% (SSE2), +79-149% (AVX2) on all six dense subjects (REG in all 18 comparisons) and slower than P4 in all 18 as well; docs/code are not a wash (P3W - P3 = +2.6 to +274 us). At 8 B (`all`) P3W is also slower than P1 on prose64k, docs64k and code64k (+9,060 / +7,087 / +9,410 ns).

**V2-5. SIMD beats SWAR more as K grows: the P3w vs P3a/P3s gap should exceed the V1 vs S1/A1 gap on dense cells. MIXED.** In ratio, CONFIRMED: w8/SIMD ns ratio at P1 1.41-1.49x (SSE2) rising to 3.92-4.94x at P3 (e.g. prose64k 1.47 -> 4.94). In absolute ns it holds only on the 64 KiB subjects (prose64k gap 10.5 -> 19.9 us, docs64k 11.2 -> 19.4, code64k 10.7 -> 19.3) and fails on the 1 MiB ones (prose1m 527 -> 316 us, docs1m 517 -> 314, code1m 482 -> 314), where P1's gap is candidate time that P3 removes.

**V2-6. Cells with no candidates lose monotonically in K (digits64k, mix64k, and prose in `first`, which has no match). MIXED.** CONFIRMED for digits64k and mix64k at all three widths (+89-93% P2, +145-250% P3, +268-393% P4, +359-692% P3W over P1). REFUTED for prose `first`: prose64k has 4,717 candidates (no match, but a dense candidate stream), so every P2+ arm wins at SIMD and P2/P3 win at 8 B (section 4.4).

**V2-7. `short`: SIMD rows pay the per-byte tail, worse as K grows; P2w may beat V1. MIXED.** P2w beats V1: CONFIRMED (14.9 vs 19.0 ns `first`, and the walk's 17.4). Monotone in K at SIMD: REFUTED (SSE2 29.0 / 46.8 / 40.8 / 79.2 for P2 / P3 / P4 / P3W, AVX2 29.4 / 47.2 / 41.3 / 75.4; P4 < P3, and P2s beats S1 but P2a does not beat A1); P3W is the slowest everywhere.

**V2-8. AVX2 ~ SSE2: the counts are identical, so any difference is the load count (half) and the `-mavx2` TU effect. REFUTED as an equivalence; the stated mechanism holds.** AVX2/SSE2 time ratio 0.96-0.99 on dense P1, but 0.67-0.93 at P2, 0.43-0.57 at P3, 0.40-0.51 at P4 and 0.49 / 0.39-0.55 on digits64k/mix64k. The `-mavx2` flag alone is NULL (V1x, 116 of 116), so the whole difference is the halved load/compare count, as the prediction names it, at a size (up to 2.5x) it did not expect.

## 6. R17-b ALPHA's losing cells: does the kept vector (and/or the prologue) turn them?

### 6.1 The population

ALPHA = slot25c's `new` vs `deny`, 160 rows (both layers, 62 WIN / 87 REGRESSION / 11 NULL). The two layers time the same artifact, so this section uses the OFF layer: its 56 reached groups on the five contrived subjects are 30 REGRESSION / 25 WIN / 1 NULL in slot25c. The spike's V1 (= `new`) reproduces them: against the walk `time.sh` reads it 28 LOSS / 25 WIN / 3 NULL, the same class as slot25c in 54 of the 56 groups; the two differences are hex-run prose1m `all` (slot25c +1,113 ns REG; here +6,952 ns, inside that group's A/A of 10,605 ns) and bounded mix64k `all` (here +19,313 ns, inside an A/A of 32,864 ns). The 30 slot25c REGRESSION groups are "the ALPHA losing cells" below: 16 `first` rows (a single call; nothing for keep to reuse) and 14 `all` rows.

Table: variant minus walk, `first` rows in ns per pass, `all` rows in ns per use (the dfa-hat prose `first` rows are whole-subject passes, so their ns/pass are large). `~` = NULL, `W` = WIN (faster than the walk), blank = REGRESSION.

| cell | subject | mode | uses | slot25c new-deny ns/pass | V1 | V2 | V3 | V4 | S1 | S2 | S3 | S4 | A1 | A2 | A3 | A4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dig | digits64k | first | 7 | +6 | +6.38 | +6.62 | +6.89 | +9.55 | +5.79 | +6.07 | +8.09 | +8.41 | +5.22 | +5.37 | +5.30 | +7.11 |
| dig | mix64k | first | 8 | +7 | +6.63 | +6.51 | +7.24 | +7.31 | +4.95 | +5.50 | +7.67 | +8.01 | +4.50 | +4.93 | +4.77 | +6.60 |
| word-eq | mix64k | first | 20 | +26 | +26.01 | +22.96 | +29.84 | +32.13 | +7.19 | +7.77 | +12.33 | +14.26 | +4.79 | +4.89 | +10.96 | +11.49 |
| word-eq | mix64k | all | 14202 | +18346 | +1.29 | +1.05 | +1.43 | +1.53 | +0.42 | +0.44 | +0.37 | +0.43 | +0.28 | +0.31 | +0.36 | +0.60 |
| hex-run | short | first | 1 | +0 | +0.24 | +0.17 | +1.62 | +1.85 | +23.61 | +22.99 | +24.83 | +24.57 | +7.08 | +7.28 | +8.83 | +9.14 |
| hex-run | short | all | 4 | +8 | +2.00 | +1.58 | +1.02 | +1.04 | +16.62 | +11.54 | +5.92 | +5.56 | +13.92 | +4.41 | +2.10 | +2.35 |
| hex-run | prose64k | first | 1 | +1 | +1.21 | +1.17 | +2.74 | +2.93 | +2.37 | +2.55 | +3.67 | +3.86 | +1.25 | +1.39 | +2.66 | +2.85 |
| hex-run | prose64k | all | 10454 | +27915 | +2.62 | +2.29 | +1.43 ~ | +1.29 ~ | +4.30 | +2.14 | +0.07 ~ | +0.05 ~ | +3.26 | +1.20 ~ | +0.24 ~ | +0.23 ~ |
| hex-run | digits64k | first | 1 | +3 | +2.53 | +2.58 | +3.88 | +4.13 | +3.98 | +4.06 | +5.40 | +5.55 | +2.88 | +2.94 | +4.78 | +5.03 |
| hex-run | digits64k | all | 9057 | +20324 | +2.27 | +0.69 | +2.53 | +1.64 | +3.91 | +0.52 | +1.75 | +1.28 | +3.07 | +0.30 | +1.14 | +1.34 |
| hex-run | prose1m | first | 1 | +2 | +1.96 | +1.92 | +3.47 | +3.67 | +3.12 | +3.31 | +4.44 | +4.58 | +2.29 | +0.77 | +3.48 | +2.29 |
| hex-run | prose1m | all | 166490 | +1113 | +0.04 ~ | +2.47 | +0.45 | +0.51 | +0.18 ~ | +1.92 | -3.59 W | -3.58 W | -0.82 W | +0.87 | -3.62 W | -3.48 W |
| hex-run | mix64k | first | 1 | +2 | +2.16 | +2.13 | +3.69 | +3.87 | +3.32 | +3.50 | +4.61 | +4.81 | +2.21 | +2.33 | +3.61 | +3.80 |
| bounded | short | first | 1 | +3 | +2.85 | +2.90 | +3.11 | +4.19 | +18.69 | +18.32 | +20.38 | +20.64 | +10.75 | +10.59 | +11.18 | +13.09 |
| bounded | short | all | 7 | +28 | +4.05 | +1.85 | +3.71 | +2.49 | +12.18 | +3.85 | +4.68 | +4.63 | +10.22 | +2.94 | +3.11 | +3.54 |
| bounded | prose64k | first | 1 | +5 | +4.89 | +5.91 | +5.52 | +5.98 | +6.65 | +6.28 | +7.02 | +6.93 | +6.22 | +5.52 | +6.07 | +6.60 |
| bounded | prose64k | all | 10079 | +39210 | +4.08 | +2.44 | +4.47 | +3.11 | +5.65 | +1.66 | +2.87 | +2.45 | +4.84 | +0.38 ~ | +2.21 | +2.58 |
| bounded | digits64k | first | 11 | +2 | +2.93 | +3.75 | +2.64 | +8.46 | -16.42 W | -17.03 W | -13.32 W | -12.62 W | -18.77 W | -18.55 W | -18.36 W | -15.07 W |
| bounded | digits64k | all | 5052 | +3224 | +0.59 | +0.78 | +0.63 | +0.88 | -0.92 W | -0.72 W | -0.88 W | -0.81 W | -1.13 W | -0.62 W | -1.17 W | -0.87 W |
| bounded | prose1m | first | 1 | +4 | +3.66 | +3.94 | +3.89 | +4.94 | +4.10 | +5.02 | +5.83 | +6.17 | +4.84 | +0.08 ~ | +5.12 | +1.66 |
| bounded | prose1m | all | 161475 | +599268 | +3.75 | +1.87 | +4.08 | +2.71 | +5.22 | +1.29 | +2.40 | +2.27 | +4.32 | +0.30 ~ | +1.94 | +2.37 |
| bounded | mix64k | first | 3 | +4 | +3.98 | +6.16 | +4.41 | +7.35 | +4.61 | +4.29 | +6.07 | +6.37 | +3.82 | +3.45 | +4.04 | +5.15 |
| bounded | mix64k | all | 13005 | +19264 | +1.49 ~ | +1.31 ~ | +1.27 ~ | +1.34 ~ | +1.26 ~ | +0.89 ~ | +0.41 ~ | +0.45 ~ | +0.91 ~ | +0.56 ~ | +0.18 ~ | +0.45 ~ |
| dfa-hat | short | first | 3 | +2 | +2.07 | +3.15 | +4.98 | +4.52 | +18.51 | +19.14 | +21.14 | +21.24 | +7.01 | +7.36 | +9.06 | +9.58 |
| dfa-hat | short | all | 3 | +2 | +0.63 | +0.96 | +1.65 | +1.62 | +6.14 | +6.28 | +7.06 | +7.08 | +2.20 | +2.37 | +3.06 | +3.13 |
| dfa-hat | prose64k | first | 4717 | +6263 | +6094.58 | +8339.85 | +9362.32 | +9640.72 | -4411.55 W | -3330.66 W | -858.85 W | +255.27 ~ | -5038.58 W | -3166.07 W | -1143.62 W | +828.19 |
| dfa-hat | prose64k | all | 4717 | +6299 | +1.32 | +1.79 | +2.03 | +2.11 | -0.91 W | -0.68 W | -0.14 W | +0.13 | -1.04 W | -0.65 W | -0.27 W | +0.17 |
| dfa-hat | prose1m | first | 75836 | +234456 | +237052.64 | +410817.55 | +307464.95 | +408387.02 | -288795.75 W | -229090.42 W | -226012.59 W | -156315.17 W | -312330.41 W | -222336.45 W | -228759.17 W | -118484.03 W |
| dfa-hat | prose1m | all | 75836 | +231943 | +3.15 | +5.42 | +3.97 | +5.35 | -3.79 W | -3.02 W | -2.83 W | -1.98 W | -4.11 W | -2.92 W | -2.97 W | -1.59 W |
| vm-hat | prose1m | all | 68248 | +33470 | +0.50 | +1.75 | +2.10 | +1.82 | -5.29 W | -4.99 W | -5.39 W | -5.18 W | -5.79 W | -5.31 W | -5.79 W | -5.29 W |

Counts per variant (WIN/REG/NULL against the walk) over the 30 rows:

| variants | first rows (16): WIN/REG/NULL | all rows (14): WIN/REG/NULL | all 30 |
|---|---|---|---|
| V1 | 0/16/0 | 0/12/2 | 0/28/2 |
| V2 | 0/16/0 | 0/13/1 | 0/29/1 |
| V3 | 0/16/0 | 0/12/2 | 0/28/2 |
| V4 | 0/16/0 | 0/12/2 | 0/28/2 |
| S1 | 3/13/0 | 4/8/2 | 7/21/2 |
| S2 | 3/13/0 | 4/9/1 | 7/22/1 |
| S3 | 3/13/0 | 5/7/2 | 8/20/2 |
| S4 | 2/13/1 | 4/8/2 | 6/21/3 |
| A1 | 3/13/0 | 5/8/1 | 8/21/1 |
| A2 | 3/12/1 | 4/6/4 | 7/18/5 |
| A3 | 3/13/0 | 5/7/2 | 8/20/2 |
| A4 | 2/14/0 | 4/8/2 | 6/22/2 |

### 6.2 What turns them

- **17 of the 30 are REGRESSION under every one of the 12 variants**: dig digits64k first, dig mix64k first, word-eq mix64k first and all, hex-run short first and all, hex-run prose64k first, hex-run digits64k first and all, hex-run prose1m first, hex-run mix64k first, bounded short first and all, bounded prose64k first, bounded mix64k first, dfa-hat short first and all. Twelve of the 17 are single-call `first` rows (+0.24 to +26.01 ns at 8 B), and the short rows pair with a handicap that SIMD makes worse (for example bounded short first: +2.85 ns at 8 B, +18.69 (S1) and +10.75 (A1)).
- **Width alone (S1/A1, no keep, no prologue) turns 7 of the 28 REG rows to WIN** at both SSE2 and AVX2: bounded digits64k first and all, dfa-hat prose64k first and all, dfa-hat prose1m first and all, vm-hat prose1m all. None of the 7 needs keep or the prologue.
- **Keep (same width) turns exactly 1 of the 28 REG rows to NULL**, hex-run prose64k `all`, at every width: V3 +1.43~ (from +2.62), S3 +0.07~ (from +4.30), A3 +0.24~ (from +3.26). At 8 B no other REG row is turned, and V3 turns hex-run prose1m `all` (V1 +0.04~) into +0.45 REG, so V3's totals equal V1's (28 REG / 2 NULL each).
- **The prologue turns 0 REG rows at 8 B and SSE2 and 4 at AVX2**, all to NULL: hex-run prose64k all (A2 +1.20~), bounded prose64k all (A2 +0.38~), bounded prose1m first (A2 +0.08~), bounded prose1m all (A2 +0.30~). It also turns rows the other way: hex-run prose1m `all` goes from NULL or WIN (V1 +0.04~, S1 +0.18~, A1 -0.82) to REG at every width (V2 +2.47, S2 +1.92, A2 +0.87), and S4/A4 turn dfa-hat prose64k `all` from WIN (S1 -0.91, A1 -1.04) to REG (+0.13, +0.17).
- **Keep and prologue together (X4) turn nothing that neither turns alone** (0 at every width) and their counts on the 30 rows are no better than keep's alone: S4 6/21/3 and A4 6/22/2, against S3 8/20/2 and A3 8/20/2 (S2 7/22/1, A2 7/18/5).
- **Rows where keep or the prologue reduce the loss without turning it** (`all` rows, ns/use, kept minus unkept): SSE2 keep hex-run short -10.7, prose64k -4.23, digits64k -2.17, prose1m -3.77; bounded short -7.5, prose64k -2.78, prose1m -2.82; AVX2 keep -11.82, -3.03, -1.94, -2.80, -7.11, -2.63, -2.38 for the same rows. Prologue on bounded prose at SIMD: S2-S1 -3.99 (prose64k), -3.93 (prose1m), A2-A1 -4.46, -4.01. After that, S3/A3 still read +2.87/+2.21 (bounded prose64k) and +2.40/+1.94 (bounded prose1m) against the walk.
- **The `first` ALPHA rows (16)** are untouched by keep and prologue: V1..V4 are 0/16/0 for all four; S1..S4 3/13/0, 3/13/0, 3/13/0, 2/13/1 and A1..A4 3/13/0, 3/12/1, 3/13/0, 2/14/0 - the 3 SIMD WINs are the width alone. In `first` the kept variant is a REG against unkept in 26/50 (8 B), 33/43 (SSE2), 19/43 (AVX2) groups, so the kept form is a cost there (section 2.4).
- **Outside ALPHA (the four real-text subjects):** V1 loses to the walk in 33 real-text groups (word-eq docs/code first and all, hex-run docs first and code first and all, bounded docs/code first and all, dfa-hat docs/code first and all, email code1m first and all, vm-hat docs1m all). Against the walk, WIN/REG/NULL over those 33: S1 13/15/5, S2 11/19/3, S3 12/15/6, S4 7/18/8; A1 14/13/6, A2 11/10/12, A3 16/15/2, A4 6/21/6; V1..V4 0/33/0, 0/32/1, 0/32/1, 0/33/0. So SSE2 or AVX2 width alone turns 18 and 20 of the 33; keep leaves the REG count at 15 at SSE2 and raises it from 13 to 15 at AVX2, and the prologue moves it to 19 (S2) and 10 (A2). Kept minus unkept on the real-text `all` rows, ns/use: hex-run docs64k / docs1m / code64k / code1m 8 B -1.11 / +0.49 / -1.16 / +0.47, SSE2 -3.98 / -3.71 / -4.09 / -3.71, AVX2 -2.90 / -2.84 / -2.95 / -2.74; bounded 8 B +1.28 / +1.16 / -0.58~ / +1.14, SSE2 -2.37 / -2.42 / -3.06 / -2.05, AVX2 -1.99 / -2.04 / -3.30 / -1.73; word-eq is REG at every width (+0.43 to +2.12).

## 7. What the reading implies for R17-b (interpretation)

This is interpretation, not a recommendation to build. The kept (preserved) vector does not turn R17-b's 8-byte losses: at 8 B it turns 1 of 28 ALPHA REGRESSION rows and costs +0.2 to +2.9 ns/use even where nothing can be reused (dfa-hat, vm-hat, single-call `first`), so a find-all state that survives `rx_search` calls only pays where the reuse is large and the block wide: hex-run and bounded at SSE2/AVX2 (-2 to -4 ns/use, 91-98% and 25-93% kept-served), where it reduces rather than removes the loss on prose. The alignment prologue helps one pattern, bounded near hits at SIMD width (AVX2 + prologue brings bounded prose from about +4.8/+4.3 ns/use to NULL), and costs elsewhere (hex-run 1 MiB, dfa-hat, vm-hat), so as a per-site flag it would need the near-hit/gap fact rather than being a default. The larger structural fact in the table is that 17 of the 30 ALPHA losses survive all twelve variants - single-call per-use costs, short subjects (made worse by SSE2/AVX2), word-eq and hex-run on digits/mix - and that W = 64 plus multi-position masks are what moves dfa-hat (P3 is 1.1-3.9x, 4.4-17.1x and 7.7-39.2x faster than the walk at 8 B / SSE2 / AVX2, against 0.82-0.89x, 1.20-1.27x, 1.23-1.31x for P1), at the price of +89% (P2) to +692% (P3W) over P1 on cells with no candidates. All of this is one box (Zen 4, CPU 14), medians of five launches with no per-launch spread recorded, and six unstable 64 KiB find-all groups whose rows (hex-run prose64k all, bounded mix64k all, dig digits64k all) carry an A/A of 11-61% and should not carry a conclusion alone.

## Reproduction

`readtmp/` (the only directory written besides this file): `load.py` parses a log; `common.py` loads both logs and counters and defines the strict floor (`FR = 0.023`); `gen_tables.py` writes `tables.json` (the tables inlined above); `a1.py`..`a15.py` are the one-off computations behind individual numbers; `totals.py` the same-width totals; `build.py` assembles this file from `tpl1.md`, `tpl2.md` and `tables.json`. Run any of them with `python3 -I <script>`.
