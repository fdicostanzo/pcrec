# alphas2 — START-SET stage 2 (VM hat) Linux alpha, read

Lane `alphas2` (sonnet), 2026-10-06. Measurement and reading only; nothing
under `src/`, `tests/`, `docs/spec/`. Raw data:
`docs/dev/optloop/startset/alpha_s2_results/` (README names pin/box/load/when).

## 0. Verdict

- **No wrong answer anywhere.** `check: rc=0`: all 88 subject SHAs OK, W cells
  differ from BASE with DENY == BASE, C cells program-identical, base/new/deny
  answer identically on every subject (including the dense and short-call ones).
- **Every IMPROVE cell on a throughput subject is met**, by 5-15x the noise
  floor, and **reproduced** in a second full timing pass (deltas within 1-2%
  of run 1 on every real mover).
- **Four do-not-regress losses, all reproduced in run 2, all past the floor**
  (D144 item 3: issue rows, not reverts), listed in §3 for the manager:
  L1 `quoted-delim` on the match-dense subject, L2 `a(\w)\1` at d = 33%/80%,
  L3 the short-call quoted-delim cell where the subject starts with a quote
  (+14..+17 ns/call on 4 of 75 subjects), L4 (minor, sub-1.4%) the forced-VM
  guard cells `union-select-vm` / `ci-ascii-ctl-vm`.
- The `C` (auto null band) cells read as program-identical; their sub-0.001
  ns/B "REGRESSION" verdicts are instrument noise (§2.4), not findings.

## 1. Protocol facts

BASE `f3c726d7` (abi 61), NEW `57db5152` (abi 62), DENY = NEW `-fno-start-set`.
ubuntubudu (Ryzen 5 1600), gcc 15.2.0, glibc 2.43 (`ldd` 2.43-2ubuntu2.4),
`taskset -c 2`, scalar layer only, governor schedutil / boost=1. Driver from main
`eacde3dc` (pushed to the box as a temp branch; removed, with its worktree and
work dir, after the run). Pre-run box state: `df -h /` 13 GB free (>= 5 GB OK).
**Load precondition**: the first `uptime` read load1 0.58 (15-min avg 1.06) with
nothing runnable; I sampled it for ~2 minutes, it decayed to 0.31 with an idle
process table, and I launched. The driver's own per-cell gate (load1 < 0.5 before
every cell) governs the readings; run 1's header printed load1=0.90 (the
build's own tail), run 2's 0.15. This is a deviation from "stop if >= 0.5 at
start" and is disclosed here.

Run 1 (`all`) is the manager's queued command. Run 2 (`time`, same artifacts)
was added by this lane as a reproducibility pass: ~14 min, no cost to the box.
Instrument caveat in the results README (a mistaken, killed duplicate launch).

## 2. Per-cell reading (run 1 / run 2; ns/B unless stated; delta = new-base)

The script's verdict compares |new-base| to a single-sample |deny-base|. That
floor is fragile (see §2.4); I read each cell against a sanity band built from the
identical-program control cells (largest control |delta|: 0.0009 ns/B; union-srch
short-call median |delta| 0.11 ns/call, p90 0.29, with a consistent -0.1..-0.3
negative bias = arm order, since NEW and DENY run after BASE).

### 2.1 IMPROVE, VM at auto (§7 table: quoted-delim, balanced-parens-rec, bak-k-named)

| cell | subject | base | new | delta (r1 / r2) | reading |
|---|---|---|---|---|---|
| quoted-delim | cap t-64k | 5.608 | 0.704 | -4.904 / -4.902 | improve MET |
| quoted-delim | cap t-1m | 5.674 | 0.718 | -4.955 / -4.988 | improve MET (run-1 deny was noisy, 7.11, floor 1.44; run 2 floor 0.04) |
| quoted-delim | **dense:quoted** | 10.079 | 10.917 | **+0.838 / +0.908** | **REGRESSION (L1)**, deny == base (9.99), floor 0.09 / 0.02 |
| balanced-parens | cap t-64k / t-1m | 3.695 / 3.725 | 0.808 / 0.849 | -2.887 / -2.876 | improve MET |
| balanced-parens | dense:paren | 8.643 | 8.108 | -0.535 / -0.461 | improve MET (small) |
| bak-k-named | syn t-64k / t-1m | 0.815 / 0.854 | 0.607 / 0.631 | -0.208 / -0.223 | improve MET (first Linux reading of this cell) |
| bak-k-named | dense:tag | 2.910 | 2.867 | -0.042 / -0.037 | improve MET but small, floor 0.010 |

SHORT-CALL (quoted-srch, 75 `search_short` subjects of quoted-delim-match,
absolute ns/call): 71 of 75 subjects improve by 11 to 474 ns (base 18-528 ns ->
new 7-54 ns; e.g. floor-hit 18.5 -> 7.1, sec-github-pat 528 -> 54), in both runs.
**Four subjects regress (L3)**, the ones whose first byte is already a candidate:

| subject | base | new | delta r1 / r2 | floor r1 / r2 |
|---|---|---|---|---|
| br-quoted-delim `'single quoted'` | 127.2 | 142.9 | +15.7 / +17.1 | 0.64 / 0.51 |
| cg-key-colon `"key":` | 46.9 | 63.7 | +16.8 / +16.7 | 0.02 / 0.16 |
| lp-quoted `"quoted text"` | 113.3 | 128.0 | +14.7 / +14.1 | 0.05 / 0.79 |
| lp-quoted-escaped `"say \"hi\" now"` | 149.4 | 156.0 | +6.7 (NULL: floor 9.9) / +13.9 (REGRESSION) | 9.9 / 1.35 |

Against the control band (0.3 ns/call) these are 50x out. DENY == BASE on all
four, so it is the hat's per-call seek, which finds the candidate at offset 0
and saves nothing (the K88 shape the §7 short-call cell exists for). The seek
costs about 14-17 ns per call there on this libc.

### 2.2 IMPROVE, `--engine=vm` (mod-i, mod-r, cls-fold-pair, cls-pair-ctl, ci-strasse, aws)

All MET, identical in both runs to <= 0.01 ns/B:
mod-i 3.48/3.57 -> 1.45/1.52 (-2.04); mod-r same (-2.04/-2.05);
cls-fold-pair 1.90/1.97 -> 1.15/1.22 (-0.745); cls-pair-ctl 1.91/1.98 -> 1.16/1.24
(-0.744); ci-strasse 3.37/3.45 -> 0.78/0.81 (-2.60/-2.63); aws forced-VM
6.94/7.03 -> 0.399/0.398 (-6.54/-6.63). Floors <= 0.006. The K82 forced-VM
losses §7 names (+0.64..+2.02 ns/B) are each more than cancelled on this
box (cls-fold-pair/-ctl gain 0.745 against a K82 loss as small as +0.64).

### 2.3 DO-NOT-REGRESS

- **Auto null band (C cells: floor-byte, high-byte-run, uuid-near-miss,
  union-select, ci-ascii-control)**: NEW, BASE and DENY are program-identical under
  the normalization (check passed), so no optimization can have moved them.
  Measured |delta| <= 0.0009 ns/B (<= 0.46% on the largest). Script verdicts
  include REGRESSION on high-byte-run (+0.00015/+0.00018 r1, +0.00045/+0.00004 r2),
  union-select 64k (+0.00066 r1 / -0.00135 r2), ci-ascii-ctl 64k (+0.00058 /
  +0.00087), union-select 1m (-0.00016 / +0.00018): these flip sign between runs or
  stay below 0.5%, on identical code. Reading: NULL. The only reproducible,
  same-sign one is ci-ascii-ctl t-64k (+0.0006..0.0009, 0.3-0.5%) on identical code:
  a binary-layout offset, listed in §3 only so the manager can see it was noticed.
- **Same cells under `--engine=vm` (W guard cells)**: floor-byte-vm null
  (|d| <= 0.00001). union-select-vm: t-64k +0.0017/+0.0026 (+0.6..1.0%), t-1m
  -0.0045/-0.0046 (-1.3% win); ci-ascii-ctl-vm: t-64k -0.0002/+0.0001 null, t-1m
  +0.0011/+0.0009 (+0.4%). Reproducible, mixed sign across the two sizes, at most
  1.3% of ~0.26 ns/B: **L4, not recommended for a row** (listed because it clears
  the script floor and reproduces).
- **Dense-S guards**: doubled-word -0.838/-0.718 (r1), -0.925/-0.885 (r2) and
  bak-1 -0.444/-0.518, -0.434/-0.507: sign 0 expected, **better than expected**
  (4-5%, 4%); no regression. (deny == base, so it is the NEW program text.)
- **`a(\w)\1` d = 33% / 80% (match-dense, §7's cost-F1 loss regime)**: **L2.**
  d33 4.330 -> 4.857 (+0.526 / +0.520); d80 4.845 -> 5.217 (+0.372 / +0.377).
  Expected sign 0 or -; reproduces the Mac's ×0.9 in direction (here +12% / +7.7%
  of base). deny == base, floors 0.0003-0.009.
- `e(\w)\1` on prose (d 8.5%): +0.002 / -0.0015, floor 0.004-0.009: NULL, as §7
  predicted.
- `|S|` = 255 `.`-led: -0.017 / -0.011 (win, 0.4%): no regression.
- **S == REQ_BYTE hit-dense** (`(q)\1q` on `qa qb qqx q `): base 4.335 -> 2.700
  (-1.635 / -1.638): a clear win. The loss this cell was built to expose (the
  pre-check and the seek reading the same byte; the trigger of the filed VM-hat
  dominance/handoff row) **did not appear** on this subject, so that row's
  trigger is not met by this cell. One synthetic subject, stated as such.
- **nested-comment-rec** (pre-check dominated): 0.01676 -> 0.01676/0.01678,
  |delta| <= 0.00001: NULL, as predicted.

### 2.4 Instrument notes (so the verdict column is not over-read)

1. The floor is one sample of |deny-base|; on cells where deny happens to land
   within 1e-5 of base the floor is ~0 and any layout wiggle reads REGRESSION/WIN.
   Across the 75 union-srch (identical-program) cells, the script's verdicts were
   53/15/7 WIN/NULL/REGRESSION in run 1 and 44/22/9 in run 2. So a WIN/REGRESSION
   in a C or sub-0.003 ns/B cell means nothing by itself; I read against the
   control band instead.
2. `new` runs second in each launch round: union-srch shows a consistent
   -0.1..-0.3 ns/call bias on identical programs. It does not touch any finding
   above (the smallest real short-call regression is 6.7 ns, run 1; 13.9, run 2).
3. Run 1's t-1m quoted-delim deny cell (7.11) was a noisy sample (run 2: 5.71 base,
   floor 0.04). Run 2's floors are generally tighter (load1 0.15 vs 0.90 at start).

## 3. Items for the manager (not filed; evidence above, raw in results dir)

| id | cell | delta (r1 / r2) | kind |
|---|---|---|---|
| L1 | quoted-delim, dense:quoted (JSON strings) | +0.838 / +0.908 ns/B (10.08 -> 10.92) | an IMPROVE cell regressing on the match-dense subject (cost-F3's subject class). Not a wrong answer. |
| L2 | a(\w)\1 d33, d80 | +0.526/+0.520 and +0.372/+0.377 ns/B | the cost-F1 loss regime, expected sign 0/-, got + |
| L3 | quoted-srch short-call, 4 subjects starting with a quote | +14..+17 ns/call | the K88 per-call seek cost on hit-at-offset-0 subjects; 71 of 75 subjects improve |
| L4 | union-select-vm 64k, ci-ascii-ctl-vm 1m | +0.0017..0.0026 / +0.0009..0.0011 ns/B (<= 1.3%), mixed sign across sizes | forced-VM guard cells; recommend NULL-in-substance |

Also noted, not a defect: `ci-ascii-ctl` t-64k +0.0006..0.0009 ns/B on a
program-identical C cell (layout).

No disaster (D144 item 3): no wrong answer, no size/compile blowup observed (the
build and check steps ran clean).

## 4. Open / not done

- `-fmemfn-simd` layer: not built at this pin; scalar only (stated in the driver header).
- bak-k-named's dense:tag gain is small (-0.04) and its improve evidence is the
  syn throughput subjects; no libc-layer split applies.
- The lane did not repeat the three-run protocol beyond the second pass; two
  runs agree on every real delta to within ~2%.
- The box repo held a temp ref `alphas2-main` and a worktree
  `worktrees/alphas2` (and the work dir under it): all removed; `git worktree list`
  on the box is back to its prior 6 entries.
