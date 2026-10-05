# k82halpha — K82 (B) HANDOFF Linux alpha + K85 re-measure, read (2026-10-05, lane k82halpha, sonnet; read only)

Reads the Linux run lx1006 (`scratch_lx/lx1006.log`: `WTBUILD_RC=0`, `ALPHA_K82H_RC=0`, `K85_RC=0`,
`ALL_DONE`; ubuntubudu, AMD Ryzen 5 1600, gcc 15.2.0, `taskset -c 2`, 5 launches x 5 passes, loops >= 50 ms)
under D144 + addendum 1 (ABSOLUTE deltas beside the floor; inside the floor = NULL; ns-scale never a
percentage of a short call) and addendum 3's per-change alpha bar. Item 1 = `alpha_k82h.sh all`: BASE =
cdc50d5b (main before the handoff merge, abi 60 = `f116cff5^1`), NEW = 3481682b (wt_main; `src/ lib/ cli/`
identical to the merge f116cff5 by `git diff`, abi 61), DENY = NEW `-fno-req-handoff` (bit 46). Item 2 =
`lx1006_alpha_k85.sh` (cls-n-uc cell only), BASE c4c70f2c (abi 59), NEW = the abi-61 build, DENY = NEW
`-fno-req-set-lead`. Transcripts archived verbatim: `docs/dev/optloop/s4/k82halpha_lx.txt` (item 1) and
`docs/dev/optloop/s4/k85alpha_lx.txt` (item 2 + the driver log). Labels are the script's (WIN / NULL /
REGRESSION = past the cell's own floor); the readings are mine. Nothing re-timed or re-run; only reads (log
files, artifact diffs, one python match count over `lit-l31`'s subject).

`check: rc=0` (item 1): every `W` cell's NEW carries a numeric `RX_REQ_HANDOFF` and differs from BASE, DENY ==
BASE modulo the abi digits and DENY's `"none"` line, both `C` cells (union-select caps/nocaps) and
`level-context` are unchanged under the normalization, every arm answered identically. All 101 subjects
regenerated sha256-OK. Item 2's `check` is rc=1, which is a defect of the K85 script, not of the compiler:
see section 3.

## Verdicts (summary)

| cell | kind | verdict |
|---|---|---|
| cause (B): `mod-i`, `mod-r`, `cls-fold-pair`, `cls-pair-ctl`, `ci-strasse` | W | **WIN, cause (B) cured.** -0.85 / -0.82 (mod-i/mod-r), -0.35 / -0.42 (cls-fold-pair/pair-ctl), -0.075 / -0.18 (ci-strasse); floors <= 0.012. NEW is at or below the pre-C3 level on all five (cross-run reading, section 2). |
| C3's customers: `union-caps`/`-nocaps` (C), `ci-ascii-ctl` (W), `slack` (W) | C/W | **KEPT.** union-select deltas <= 0.0007 ns/B (unchanged program); ci-ascii-ctl -0.004 / -0.003 (a small win); slack <= 0.0002 (NULL). |
| (A)/(C) re-reads: `userpass`, `alt-shared` | W | `userpass` stays cured (0.0168 = 0.0168, delta +0.00001); `alt-shared` WIN -0.022 / -0.042 ns/B (0.079 -> 0.057, 0.135 -> 0.093): the residual k82alpha_report §3 noted is now past. |
| `stack-frame` (W) | W | **WIN on the dense hit subject**: 0.9475 -> 0.5570 (-0.391); the two fail subjects NULL (<= 0.0001). |
| six outside movers (`sfx-64`, `kv-quoted`, `asr-wb`, `anc-m-caret`, `lkb-pos`, `lit-l31`) | W | five WIN (`kv-quoted` hit 3.49 -> 0.112, -3.38; `sfx-64` -1.40 / -0.34; `asr-wb` -0.13 / -0.14; `anc-m-caret` -0.034 / -0.025; `lkb-pos` -0.002 / -0.003, tiny); **`lit-l31` `mat-l31` REGRESSES +0.149 ns/B (floor 0.011, ~13x), ~+4.6 ns per match: the one loss past the floor, draft K88 below.** |
| `level-context` control (C) | C | NULL (<= 0.031, inside its own 0.032 floor at 64k). |
| short calls: `union-srch` (control, 75 subjects) | C | NULL by reading: 44 NULL / 12 WIN / 19 REG labels on an UNCHANGED program, REG <= +0.446 ns (`waf-union`). Instrument. |
| short calls: `modi-srch` (mod-i, 75) | W | 33 NULL / 25 WIN / 17 REG. Real wins (`waf-benign` -10.5, `waf-concat` -10.2, `br-doubled-word` -3.1); one loss past the floor: `v-us-zip-plus4` +0.877 (11.55 -> 12.42, floor 0.009); the other 16 REG are <= +0.092, inside the control's spread. |
| short calls: `ciascii-srch` (ci-ascii-ctl, 75) | W | 21 NULL / 18 WIN / 36 REG. Wins `sec-slack-webhook` -30.5, `v-uuid-valid`/`-badnibble` -9.1 / -8.3; the 36 REG are a +0.01..+0.37 ns step (see section 4), layout-scale, symmetric with -0.3 steps on the 3.85 ns cells. |

**Handoff accepted: YES** against litscan_k82h.md §4.5's expected reading, with one named exception
(`lit-l31`/`mat-l31`, an "outside mover" that was to be "null or better") and one short-call cell
(`modi-srch` `v-us-zip-plus4`). No wrong answer, DENY reproduces BASE on every cell.

## 1. The floors and the control spread

`W` cells' floor is |DENY - BASE|; the programs are the same, so it is the run's own noise beyond the loop.
Throughput: <= 0.0020 ns/B on every W cell except `ci-strasse` 64k (0.0122: BASE 0.7720, DENY 0.7598) and
`levelctx-ctl` 64k (0.0316). The byte-identical C cells' spread: union-select caps/nocaps |new - base| <=
0.0007 ns/B; `levelctx-ctl` <= 0.031 (its 64k cell is the noisy one, as in k82alpha_report §1). Per call:
`union-srch` runs an unchanged program in all three arms and still reads up to +0.446 ns (`waf-union`), +0.327
(`waf-concat`), +0.176 (`lp-num-neg-dec`), with a handful of noisy spikes in BASE (`br-quoted-delim` BASE
24.9 / NEW 12.2 / DENY 10.07, `rd-phone-list-hit` 24.9 / 12.3 / 10.35, floors 14.9 / 14.5). A per-call delta
below ~0.45 ns therefore reads as NULL here whatever its label (k82alpha_report found ~0.3; this run is a
little noisier, header `load1=1.26`).

## 2. Throughput cells (ns/B)

| cell | subject | base (abi 60) | new | delta | floor | label | read |
|---|---|---|---|---|---|---|---|
| mod-i | syn 64k / 1m | 1.5710 / 1.6346 | 0.7167 / 0.8159 | -0.854 / -0.819 | 0.0003 / 0.0020 | WIN x2 | cause (B) cured |
| mod-r | syn 64k / 1m | 1.5734 / 1.6355 | 0.7177 / 0.8158 | -0.856 / -0.820 | 0.0016 / 0.0002 | WIN x2 | cured |
| cls-fold-pair | syn 64k / 1m | 0.8899 / 1.0252 | 0.5418 / 0.6024 | -0.348 / -0.423 | 0.0016 / 0.00005 | WIN x2 | cured |
| cls-pair-ctl | syn 64k / 1m | 0.8933 / 1.0250 | 0.5436 / 0.6025 | -0.350 / -0.423 | 0.0010 / 0.0003 | WIN x2 | cured |
| ci-strasse | u8 64k / 1m | 0.7720 / 0.7987 | 0.6975 / 0.6217 | -0.075 / -0.177 | 0.0122 / 0.0019 | WIN x2 | cured (64k delta is 6x its floor) |
| ci-ascii-ctl | u8 64k / 1m | 0.1938 / 0.2667 | 0.1896 / 0.2632 | -0.0042 / -0.0035 | 0.0006 / 0.0002 | WIN x2 | customer kept, small win |
| union-caps | cap 64k / 1m | 0.2581 / 0.3477 | 0.2575 / 0.3478 | -0.0007 / +0.0001 | 0.0002 / 0.00001 | WIN/REG | NULL (unchanged program) |
| union-nocaps | cap 64k / 1m | 0.2575 / 0.3479 | 0.2572 / 0.3477 | -0.0003 / -0.0002 | 0.0003 / 0.00001 | WIN x2 | NULL |
| slack | cap 64k / 1m | 0.2241 / 0.2497 | 0.2239 / 0.2496 | -0.0002 / -0.0001 | 0.0001 / 0.0001 | WIN/NULL | NULL |
| userpass | cap 64k / 1m | 0.01677 / 0.01679 | 0.01678 / 0.01680 | +0.00001 / +0.00001 | <= 0.00001 | REG/NULL | NULL, (A)'s cure holds |
| alt-shared | u8 64k / 1m | 0.0794 / 0.1346 | 0.0571 / 0.0928 | -0.0224 / -0.0417 | 0.0004 / 0.0006 | WIN x2 | win |
| stack-frame | log 64k-f / 1024k-f / 1024k-hit | 0.3030 / 0.3771 / 0.9475 | 0.3029 / 0.3771 / 0.5570 | -0.0001 / +0.0001 / **-0.3905** | 0.00004 / 0.0001 / 0.0005 | WIN/NULL/WIN | dense hit halves |
| sfx-64 | aw 128k sparse / dense | 3.6804 / 3.5394 | 2.2836 / 3.2037 | -1.397 / -0.336 | 0.0083 / 0.0023 | WIN x2 | outside mover, win |
| lit-l31 | lr mat-l31 / fbf-l31 | 4.5429 / 0.18007 | 4.6917 / 0.18057 | **+0.1488** / +0.0005 | 0.0110 / 0.00016 | **REG** / REG | **mat-l31: a loss past the floor**; fbf-l31 +0.3%, instrument |
| kv-quoted | log 64k-f / 1024k-f / 1024k-hit | 0.02590 / 0.03007 / 3.4895 | 0.02602 / 0.03005 / 0.1116 | +0.0001 / -0.00002 / **-3.378** | 0.0002 / 0.00002 / 0.00007 | NULL/NULL/WIN | hit 31x faster |
| asr-wb | syn 64k / 1m | 0.7868 / 0.8367 | 0.6544 / 0.6959 | -0.132 / -0.141 | 0.0010 / 0.0001 | WIN x2 | outside mover, win |
| anc-m-caret | syn 64k / 1m | 0.3031 / 0.3098 | 0.2691 / 0.2845 | -0.034 / -0.025 | 0.0004 / 0.0003 | WIN x2 | win |
| lkb-pos | syn 64k / 1m | 0.3620 / 0.4535 | 0.3599 / 0.4500 | -0.0021 / -0.0035 | 0.0009 / 0.0003 | WIN x2 | tiny win |
| levelctx-ctl | log 64k-f / 1024k-f / 1024k-hit | 2.6539 / 2.7121 / 2.9729 | 2.6848 / 2.7114 / 2.9733 | +0.031 / -0.0006 / +0.0004 | 0.032 / 0.0005 / 0.0004 | NULL/WIN/NULL | NULL |

(The alpha's cell list carries two sizes (64k, 1m) for the syn/u8/cap cells, not the three of
alpha_k82.sh; `stack-frame`, `kv-quoted`, `levelctx-ctl` carry fail-64k, fail-1024k and hit-1024k.)

**Pre-C3 comparison (cross-run, a reading and not a verdict).** The pre-C3 levels r1read recorded (ns/B,
three sizes) are `mod-i`/`mod-r` 0.94-0.99, `cls-fold-pair`/`cls-pair-ctl` 0.57-0.61, `ci-strasse`
0.666-0.694, `alt-shared` 0.066-0.115. Today's NEW is 0.717 / 0.816, 0.542 / 0.602, 0.697 / 0.622 and
0.057 / 0.093. So cause (B) is not only cured but `mod-i`/`mod-r` now run ~0.2 ns/B BELOW the pre-C3 program
(the handoff starts the DFA at the run's hit rather than at `search_from`, which the pre-C3 program never
did), `cls-fold-pair`/`-ctl` and `ci-strasse` sit at the pre-C3 level (`ci-strasse` 64k +0.003..+0.03 over
its range, 1m below it), and `alt-shared` is below it. Today's BASE reproduces r1alpha's C3 NEW and
k82alpha's BASE levels (mod-i 1.571 / 1.635 vs 1.57-1.67; cls-fold-pair 0.890 / 1.025), so the two runs are
comparable in level.

### `lit-l31` `mat-l31`: the one loss, emitted-text reading

Pattern `abcdefghijklmnopqrstuvwxyzABCDE` (31 bytes, K = 23). The artifact diff BASE -> NEW is the abi
digits, `#define RX_REQ_HANDOFF "23"`, and the run pre-check turning
`if (rx_reqrun(...) >= subject_length) return 0;` into

    size_t handoff_position = rx_reqrun(...);
    if (handoff_position >= subject_length) return 0;
    if (handoff_position - search_from > 23) handoff_position -= 23; else handoff_position = search_from;

with `scan_position = handoff_position`. `mat-l31` is 65,534 B holding 2,114 matches exactly 31 B apart
(python `re`), i.e. every `rx_search` call finds its match AT `search_from`: the handoff cannot skip
anything (`handoff_position - search_from` is 0, so the `else` arm takes `search_from`, the BASE start), and
the added work is ~4 instructions plus one more live `size_t` across the `rx_reqrun` call. +0.1488 ns/B x 31
B = ~+4.6 ns per call on a ~141 ns call (the same `mat` subjects' `fbf-l31`, no match, moves +0.0005). The
`kv-quoted`/`stack-frame`/`sfx-64` hit subjects are the opposite regime (matches far from `search_from`,
where the handoff pays). The unaided cost of four instructions is well under 4.6 ns, so the cause is
probably the call's register/layout shape and NOT measured as a mechanism here (candidates, unmeasured:
the extra live value spilling, the dependent subtract-compare-select on the call's return path; a
`cnt_pre.h`-style twin would measure it). It is a back-to-back-match population (one match per K+8 bytes), the
densest a literal can be; the design census put `lit-l31` among the six outside movers and called the read
"null or better", which this cell is not.

### Draft K-row (for the manager to file; K88 is the next free number, K87 is the O-83 draft)

> **K88 — OPEN (2026-10-05, found by lane k82halpha's read of the K82 (B) handoff Linux alpha, abi 61, bit
> 46) — the handoff costs a few ns per search call on a match-dense literal where it cannot skip: `lit-l31`
> `mat-l31` +0.149 ns/B (~+3.3%, ~+4.6 ns per match).** Witness: this report §2 (BASE cdc50d5b abi 60, NEW
> 3481682b, DENY = NEW `-fno-req-handoff`, DENY == BASE; floor 0.011, control spread <= 0.004). Matches are 31
> B apart so `handoff_position == search_from` on every call and the rewrite is pure added work; the same
> pattern's no-match subject moves +0.0005. Interim: `-fno-req-handoff` (bit 46). Disposition per D144: an
> issue row, not a revert (the same row cures cause (B) by 0.35..0.86 ns/B and halves `stack-frame`'s dense
> hit, -3.4 ns/B on `kv-quoted`'s). Re-measure before designing anything; cross-ref [MEMFN]'s fused kernel.

## 3. K85: cls-n-uc after the handoff

`lx1006_alpha_k85.sh` is `alpha_k82.sh`'s cls-n-uc cell with BASE c4c70f2c (abi 59), NEW the abi-61 build and
DENY `-fno-req-set-lead` ONLY. That is the wrong deny for abi 61: `cls-n-uc` (`it\Nm`) is now a HANDOFF mover
too (`RX_REQ_HANDOFF "0"`, K = 0: the run `it` is at offset 0 from the match start), so DENY keeps the
handoff, `DENY != BASE`, the script's own `check` prints `A-CELL WRONG cls-n-uc: want NEW != BASE, DENY ==
BASE` (rc=1), and the script's floor (|DENY - BASE|, 0.15-0.20) is the handoff's own effect, not noise, so
every verdict it printed reads NULL. The artifact diffs (read on the box) show the exact relationships:
BASE -> NEW is the abi digits, `RX_REQ_HANDOFF "0"`, the three-line set-leads `memchr('m')` pre-check
(unchanged from abi 60) AND the handoff rewrite; BASE -> DENY is the same without the three `memchr` lines;
so **NEW vs DENY differs by exactly the set-leads pre-check**, which is the K85 quantity.

| subject | base (abi 59) | new | deny (`-fno-req-set-lead`) | new - base | **new - deny** | prior K85 (abi 60 vs 59 base) |
|---|---|---|---|---|---|---|
| syn 64k | 0.5146 | 0.3880 | 0.3649 | -0.1267 | **+0.0231** (6.3% of deny) | +0.0249 |
| syn 256k | 0.5779 | 0.4363 | 0.4021 | -0.1416 | **+0.0342** (8.5%) | +0.0311 |
| syn 1m | 0.6424 | 0.4772 | 0.4412 | -0.1652 | **+0.0360** (8.2%) | +0.0308 |

**K85 PERSISTS.** The set-leads pre-check still costs +0.023..+0.036 ns/B on `cls-n-uc`, the same
magnitude as the +0.025..+0.031 the abi-60 alpha measured (BASE reproduces: 0.5146 / 0.5779 / 0.6424 against
0.5148 / 0.5767 / 0.6423), ~12-14 ns per match at one match per ~380 B (consistent with the prior ~11.5 ns).
The handoff does not remove it: the `memchr('m')` runs in FRONT of `rx_reqrun`, still never rejects on this
text (`m` is present in every remaining subject), and is one fresh libc call per search call regardless of
where the run's hit is handed off. What the handoff does change is the net: `cls-n-uc` is now 0.127..0.165
ns/B FASTER than abi 59 (-25%), because the DFA starts at the run's hit (`it`, K = 0) instead of at
`search_from`. K85's own words ("regression vs abi 59") are therefore no longer true of the shipped build;
the pre-check's own cost is still there against `-fno-req-set-lead`.

The NEW - DENY pair has no floor of its own in this run (the script's floor is the wrong pair). The same
box and protocol read same-program floors <= 0.002 ns/B on every W cell above (0.0001-0.0020), so the
0.023-0.036 delta is >= 10x any floor measured here; I call it a persistent regression on that reading. A
re-run that settles it with the script's own machinery needs a deny pair: DENY = NEW `-fno-req-set-lead`
against a fourth arm NEW `-fno-req-set-lead -fno-req-handoff` (== BASE), or simply NEW vs DENY with DENY'
= NEW `-fno-req-set-lead` run twice. The fix to the script is two lines (DENYFLAGS adds `-fno-req-handoff`
for `cls-n-uc`'s A-kind check, or a P-kind cell as `alt-shared`'s).

## 4. Per-call cells (ns/call, absolute; instrument floor of section 1)

- **`union-srch`** (the control, program unchanged across arms): 75 subjects, 44 NULL / 12 WIN / 19 REG, sum
  of new - base -28.9 ns (dominated by two noisy BASE spikes of ~12 ns each; DENY ~ NEW). Every REG is
  <= +0.446 ns. Instrument.
- **`modi-srch`** (`mod-i`, a mover on union-select's subjects): 25 WIN / 33 NULL / 17 REG, sum -23.1. Wins:
  `waf-benign` -10.54 (45.7 -> 35.2, floor 0.065), `waf-concat` -10.19 (floor 0.003), `br-doubled-word`
  -3.14 (26.6 -> 23.5). The loss: `v-us-zip-plus4` +0.877 (11.547 -> 12.424, floor 0.009), DENY back at 11.538
  (a real step, ~3 cycles, one subject; the pre-check passes and the handoff adds its compare). The other 16
  REG: +0.001..+0.092, inside the control's spread. K82's old fixed ~10 ns entry term is untouched by the
  handoff, as designed.
- **`ciascii-srch`** (`ci-ascii-ctl`): 36 REG / 21 NULL / 18 WIN, sum -53.0. Big wins where the handoff pays
  (`sec-slack-webhook` -30.5 (78.4 -> 47.9), `v-uuid-valid` -9.1, `v-uuid-badnibble` -8.3, `waf-*` -0.1..-0.5).
  The 36 REG are a quantized step: BASE/DENY 11.24-11.30, NEW 11.52-11.56 (+0.2..+0.30 ns, 27 cells; five more
  at +0.37 `br-dup-param`, ~+0.01-0.09 elsewhere), while the 3.85 ns cells move the other way (-0.29..-0.31, 7
  cells: `cg-array-begin`, `cg-string-escape`, `floor-hit`, `nu-lead-no-cont`, `nu-lead-with-cont`, 4.67 ->
  4.31 `nu-high-byte`). A ~0.28 ns step (~1 cycle at 3.4 GHz) in both directions is layout/alignment of the
  changed program, not a cost that scales with the call; it sits inside the control's 0.45 ns spread. NOT filed
  (D144 addendum 1: it clears the cell-wise DENY-BASE floors, but its sign is mixed and its size one cycle).
  The manager may overrule that reading; if so the witness is the `ciascii-srch` block of the transcript.

## Caveats

- One box, one CPU, 5 launches per cell. Item 1's header reads `load1=1.26` at 19:16Z (the build had just
  finished; the per-cell load wait gates later cells), item 2's `load1=1.01` at 19:26Z.
- The alpha timed 64k and 1m only for the syn/u8/cap cells (alpha_k82.sh timed 64k/256k/1m).
- The `lit-l31` mechanism and the `ciascii-srch` layout reading are readings of emitted text and of the
  pattern of deltas, not counted-gate measurements.
- Item 2's NEW - DENY pair has no floor of its own (section 3); the persistence verdict rests on same-protocol
  floors of other cells and on the pair differing by exactly the three set-leads lines.
- The `pcrec: warning: large artifact` lines in the transcript are `sfx-64`'s (552 KB emitted, 43 KB code),
  not a finding of this alpha.

## Recommended wording (for the manager; known_issues/plan are NOT edited here)

- **K82:** append to the (B) sentence: "**(B) HANDOFF LINUX ALPHA READ 2026-10-05 (lane k82halpha, abi 61,
  `-fno-req-handoff` bit 46, BASE cdc50d5b, NEW 3481682b, `docs/dev/lanes/k82halpha_report.md`):
  cause (B) CURED — `mod-i`/`mod-r` -0.85/-0.82, `cls-fold-pair`/`-ctl` -0.35/-0.42, `ci-strasse` -0.075/-0.18
  ns/B (floors <= 0.012), at or below the pre-C3 levels; C3's customers kept (`union-select` <= 0.0007,
  `ci-ascii-ctl` -0.004), `userpass` cured, `alt-shared` -0.022/-0.042, six outside movers: five win
  (`kv-quoted` hit -3.38, `sfx-64` -1.40, `stack-frame` hit -0.39), one loss (K88: `lit-l31` mat +0.149);
  short calls: wins up to -30 ns, one cell +0.88 (`modi-srch` `v-us-zip-plus4`), the rest inside the control
  spread. DENY == BASE on every cell, 0 answer defects. K82 CLOSED as fixed; the residual is K88 and the
  pair arm's ~10 ns fixed entry term (Q7, [MEMFN]'s binding-form criterion)."**
- **K85:** append: "**RE-MEASURED after the handoff (2026-10-05, lane k82halpha): the set-leads pre-check
  STILL costs +0.023..+0.036 ns/B on `cls-n-uc` against `-fno-req-set-lead` (the arms differ by exactly the
  three `memchr('m')` lines), the same magnitude as before; the handoff does not remove it, but `cls-n-uc`
  is now 0.127..0.165 ns/B FASTER than abi 59 (K = 0 handoff), so it is no longer a regression against
  abi 59. Still OPEN, deferred; next lever is [REQ-HANDOFF-L1] (the one-byte gate's hit handed off) or
  [MEMFN]'s fused scan+verify. The Linux script `lx1006_alpha_k85.sh` needs `-fno-req-handoff` in its deny
  (or a fourth arm) to give the pair its own floor.**"
- **plan:** a row for K88 under [OPTLOOP] with D77 trigger "a bench cell with back-to-back matches on a
  handoff-mover literal"; [REQ-HANDOFF-L1]'s trigger is now also K85's persistence.

## Re-ran / changed

Nothing re-timed or re-run (reads only: the lx1006 logs and artifacts on ubuntubudu, two `diff`s per cell
of emitted C, one python match count over `lit-l31`'s subjects, `git` revisions). Files written: this
report, `docs/dev/optloop/s4/k82halpha_lx.txt`, `docs/dev/optloop/s4/k85alpha_lx.txt` (+ their
`docs/dev/optloop/s4/CLAUDE.md` entries).
