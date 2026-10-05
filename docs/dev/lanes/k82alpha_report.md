# k82alpha — K82 (A)+(C) Linux alpha, read (2026-10-05, lane lxread, opus)

Reads `alpha_k82.sh all` from lane lxrun's serial quiet-box driver (`scratch_lx/run_lx1005.sh`
item 1 on ubuntubudu: AMD Ryzen 5 1600, gcc 15.2.0, `taskset -c 2`, 5 launches x 5 passes, >= 50 ms
loops) under D144 + addendum 1: ABSOLUTE deltas beside the floor; inside the floor = NULL; ns-scale
never a percentage of a short call. BASE = c4c70f2c (abi 59; `src/ lib/ cli/` identical to 940fa06e,
checked by `git diff`), NEW = eb6fe6139 (main, abi 60), DENY = NEW `-fno-req-set-lead` (bit 45).
Transcript archived verbatim: `docs/dev/optloop/s4/k82alpha_lx.txt`. Labels below are the script's
(WIN / NULL / REGRESSION = past the floor); the readings are mine. Not merged, not pushed.

`check: rc=0`: every cell's kind held (A: DENY == BASE modulo the abi digits; P: DENY == NEW; C: all
three equal) and every arm answered identically. All 101 subjects regenerated sha256-OK.

## Verdicts (summary)

| cell | kind | verdict |
|---|---|---|
| `userpass` | A | **WIN, K82's headline cured.** -0.925..-0.947 ns/B; NEW 0.0167-0.0168 = the pre-C3 program's 0.0167-0.0168 (r1alpha `c3.out`). Prediction (k82diag §4.3, -0.92) met exactly. |
| `alt-shared` | P | **WIN, cause (C) mostly cured.** -0.065 / -0.089 / -0.091 ns/B; recovers ~80% of C3's +0.079..+0.112 loss. Residual vs the pre-C3 run below (a cross-run reading, not a K-row). |
| `cls-n-uc` | A | **REGRESSION past the floor, a K-row: draft K85 below.** +0.025 / +0.031 / +0.031 ns/B (floor <= 0.0009; ~7x the byte-identical controls' spread). The Mac's one watch item (+0.019..+0.030) confirmed. |
| `stack-frame` | A | NULL (layout-scale): -0.0026..+0.0050 ns/B, two WIN two REG labels, all within the controls' spread except 1024k-hit's +0.0050 (0.5% of 0.94), at its edge. |
| `cls-h`, `cls-s-lc`, `cls-v`, `mod-s` | A | NULL (cls-s-lc 1m a small WIN, -0.0043). Every delta <= 0.0034 ns/B, inside the controls' spread; Mac's `mod-s` +0.035 at 256k did not reproduce (+0.0013). |
| C3's customers (`union-nocaps`/`-caps`, `ci-ascii-ctl`) | C | Unchanged program, win KEPT: union-select 0.257 / 0.316 / 0.348 ns/B (= r1alpha's NEW), deltas <= 0.0007. |
| cause (B) (`mod-i`, `cls-fold-pair`, `ci-strasse`) | C | Unchanged program, K82 (B) still OPEN at the r1alpha level (mod-i 1.57-1.67, cls-fold-pair 0.89-1.03, ci-strasse 0.76-0.80 ns/B). Their REG labels (<= +0.0038) are the instrument. |
| `union-srch` (75 short subjects, per call) | C | Unchanged program: 59 NULL / 8 WIN / 8 REG, sum -9.5 ns, the instrument. K82's short-call entry term (~10.06 ns cells) is untouched, as designed. |

## 1. The control spread

The C cells are byte-identical in all three arms, so their |new - base| is the run's own noise beyond
the per-cell floor. Throughput: <= 0.0038 ns/B (`ci-strasse` 64k +0.0038, `kvquoted-ctl` hit -0.0038,
`cls-fold-pair` 64k +0.0035, `mod-i` 64k +0.0026), with `levelctx-ctl` 256k at +0.0115 inside its own
0.016 floor. Per call: up to +0.29 ns (`v-uuid-valid`), `la-currency` +0.27, `waf-sleep` +0.21, all
labelled REGRESSION on identical programs. A delta below ~0.004 ns/B (throughput) or ~0.3 ns/call
reads as NULL here whatever its label (C1's r1read §2 found the same second floor, 0.013 ns/B there).

## 2. A cells (set-leads movers; floor = |DENY - BASE|), ns/B

| cell | subject | base | new | delta | floor | label | read |
|---|---|---|---|---|---|---|---|
| userpass | cap 64k / 256k / 1m | 0.9635 / 0.9533 / 0.9417 | 0.0168 / 0.0167 / 0.0168 | -0.947 / -0.937 / -0.925 | 0.0005 / 0.0089 / 0.0006 | WIN x3 | cured |
| stack-frame | log 64k-f / 256k-f / 1024k-f / 1024k-hit | 0.3024 / 0.3544 / 0.3800 / 0.9426 | 0.3038 / 0.3528 / 0.3774 / 0.9476 | +0.0014 / -0.0016 / -0.0026 / +0.0050 | 0.0002 / 0.0008 / 0.0001 / 0.0006 | REG/WIN/WIN/REG | NULL |
| cls-h | syn 64k / 256k / 1m | 0.1130 / 0.1556 / 0.2029 | 0.1136 / 0.1551 / 0.2028 | +0.0006 / -0.0006 / -0.0002 | 0.0007 / 0.00004 / 0.0005 | NULL/WIN/NULL | NULL |
| **cls-n-uc** | syn 64k / 256k / 1m | 0.5148 / 0.5767 / 0.6423 | 0.5397 / 0.6078 / 0.6731 | **+0.0249 / +0.0311 / +0.0308** | 0.0009 / 0.0005 / 0.0004 | REG x3 | **REGRESSION** |
| cls-s-lc | syn 64k / 256k / 1m | 0.4522 / 0.5108 / 0.5341 | 0.4523 / 0.5099 / 0.5298 | +0.0001 / -0.0009 / -0.0043 | 0.0011 / 0.0002 / 0.0002 | NULL/WIN/WIN | NULL, 1m small win |
| cls-v | syn 64k / 256k / 1m | 0.2406 / 0.2906 / 0.3301 | 0.2392 / 0.2931 / 0.3302 | -0.0014 / +0.0024 / +0.00003 | 0.0004 / 0.0005 / 0.00001 | WIN/REG/REG | NULL |
| mod-s | syn 64k / 256k / 1m | 0.2518 / 0.3037 / 0.3383 | 0.2484 / 0.3051 / 0.3392 | -0.0034 / +0.0013 / +0.0009 | 0.0017 / 0.0007 / 0.0001 | WIN/REG/REG | NULL |

Against the Mac directional read (k82fix_report §7): userpass Mac -0.62..-0.74 (Mac base was lower,
0.65-0.77); every exact-run row-4 mover read "inside or at the edge" there and is NULL here EXCEPT
`cls-n-uc`, the cell §7 flagged.

### `cls-n-uc`: what moved (emitted-text reading; not measured as a mechanism)

Pattern `it\Nm`. The whole artifact diff is the abi digits plus three lines at the top of
`rx_search`:

    if (subject_length <= search_from ||
        !memchr(subject + search_from, 109, subject_length - search_from))
        return 0;

i.e. set-leads admits a one-shot `memchr('m')` in FRONT of the unchanged `rx_reqrun` (`memchr('i')` +
`memcmp "it"`). On the syn subjects `m` is 2.2% of bytes and `i` 3.0%, so the admission's "strictly
rarer than the run's scan member" holds — but `m` is present in every remaining subject, so the
check never rejects and is a pure added call per `rx_search`. The find-all makes one call per match,
one match per ~380 B (179 / 681 / 2,733 matches on 64k / 256k / 1m, counted with python `re`); +0.03
ns/B x 380 B = ~11.5 ns per call. The same box's [MEMFN] callcost (`docs/design/memfn/linux_results.md`
§1) prices one fresh glibc `memchr` at 3.54-4.13 ns up to 64 B (miss) and 4.13 / 4.97 ns for a hit at
offset 0 (independent / dependent), so the added call explains roughly 4-5 ns of the ~11.5; the rest is
NOT explained by this reading (candidates, unmeasured: the restart's lost overlap with the run
search, or the extra branch's mispredicts). The six
other row-4 movers carry the same three lines (`stack-frame` `)`, `mod-s`/`cls-v` `m`, `cls-s-lc`
`c`, `cls-h` `=`); they are NULL because their matches are sparser on their subjects (fewer calls per
byte), not because the check is cheaper. So the admission predicate prices RARITY (the byte rate)
rather than the check's EXPECTED BENEFIT (its probability of rejecting the remaining subject) against
its per-call cost — the same pricing gap K82's own (A) cause had, here on the opposite side.

### Draft K-row (for the manager to file; K84 is taken)

> **K85 — OPEN (2026-10-05, found by lane lxread's read of the K82 (A)+(C) Linux alpha, abi 60, bit
> 45) — the set-leads pre-check costs a fresh `memchr` per search call on match-dense text where its
> lead byte is never absent: `cls-n-uc` +0.025..+0.031 ns/B (~5%).** Witness: this report §2
> (BASE c4c70f2c abi 59, NEW eb6fe6139, DENY = NEW `-fno-req-set-lead`, DENY == BASE; floors <=
> 0.0009, control spread <= 0.004). Suspected cause: `req_admits[]`'s `set-leads` row admits on
> "set pick strictly rarer than the run's scan member" (2.2% `m` vs 3.0% `i`), which says nothing
> about whether the one-shot check can reject; ~11.5 ns/call at one match per ~380 B, of which a fresh glibc
> `memchr` (3.5-5 ns on this box) is about 40%. Interim:
> `-fno-req-set-lead` (bit 45). Cross-ref: K82 (B)'s handoff / expected-cost design
> (`docs/design/litscan_k82h.md`, `litscan_k82b.md`) is where a rejection-probability term would
> live; [MEMFN]'s binding-form criterion prices the call. Disposition per D144: an issue row, not a
> revert (the same row cures `userpass` by 0.93 ns/B).

## 3. P cell (`alt-shared`, the PICK NONE mover; floor = |DENY - NEW|), ns/B

| subject | base (abi 59) | new | delta | floor | pre-C3 (r1alpha `c3.out`, a588c668) | new - pre-C3 |
|---|---|---|---|---|---|---|
| u8 64k | 0.1438 | 0.0792 | -0.0645 | 0.0002 | 0.0661 | +0.0131 |
| u8 256k | 0.1949 | 0.1057 | -0.0893 | 0.0003 | 0.0843 | +0.0213 |
| u8 1m | 0.2259 | 0.1350 | -0.0909 | 0.0001 | 0.1145 | +0.0205 |

WIN on all three (Mac -0.071..-0.128). Today's BASE reproduces r1alpha's C3 NEW closely (0.144 /
0.195 / 0.226 vs 0.145 / 0.196 / 0.226), so the two runs are comparable in level; the residual
+0.013..+0.021 ns/B against the pre-C3 program is a CROSS-RUN difference (different day, different
arm set), larger than either run's floor and than this run's control spread. It is a reading, not a
K-row: the fix's NONE argmin pick is not byte-for-byte the pre-C3 guard (k82fix_report: PICK's NONE
answer is the uniform-mass argmin, ties to the rightmost), so a small residual is plausible. To size it
inside one run, the next alpha that touches this cell should add a fourth arm, NEW
`-fno-req-run-fold` (bit 44, the pre-C3 guard), to `alpha_k82.sh`'s P kind.

## 4. C cells (unchanged programs)

- **C3's customers**: union-nocaps 0.2571 / 0.3157 / 0.3479 and union-caps 0.2573 / 0.3161 / 0.3480
  ns/B NEW, = r1alpha's NEW (0.257 / 0.315 / 0.348); ci-ascii-ctl 0.194 / 0.234 / 0.267. Deltas
  <= 0.0007 ns/B. The C3 win on its predicted customers is untouched by the fix.
- **Cause (B) movers** (`mod-i`, `cls-fold-pair`, `ci-strasse`): NEW == BASE == DENY; levels mod-i
  1.572 / 1.666 / 1.635, cls-fold-pair 0.893 / 0.999 / 1.026, ci-strasse 0.762 / 0.778 / 0.799 ns/B
  — the r1alpha C3 NEW levels, i.e. K82 (B)'s +0.08..+0.70 ns/B regression stands as filed, owned by the
  handoff row (litscan_k82h.md). (`mod-r`, `cls-pair-ctl` are not cells of this block.)
- **Controls** `kvquoted-ctl`, `levelctx-ctl`: the spread of §1.
- **union-srch** per call: 8 WIN (largest -2.26 `rd-email-near-miss`, floor 2.08; -0.30
  `rec-comment-nested`; -0.17 `la-email-nodup`; -0.13 `sd-empty-alt-hit`; -0.11 `dt-prose-month`; and
  three <= 0.03), 8 REG (`v-uuid-valid` +0.29, `la-currency` +0.27, `waf-sleep` +0.21, `dt-iso8601`
  +0.13, `waf-comment-obfuscation` +0.03, and three <= +0.003), 59 NULL. Identical programs: all
  instrument. K82 diag §2's short-call entry term (the pair arm's two fresh `memchr`, the ~10.06 ns
  cells) is untouched by design.

## Caveats

- One box, one CPU, 5 launches per cell. The time step's header line reads `load1=1.29` at 12:53:55Z
  (the build had just finished; the per-cell load wait gates later cells, as in r1read's caveat).
- BASE is the abi-59 main as of the K82 ruling (c4c70f2c), the main clone's own HEAD; its compiler
  sources are identical to the 940fa06e the script names.
- `cls-n-uc`'s mechanism and the "sparser matches" reading of the other six row-4 movers are readings of
  the emitted text plus a python match count, not a counted-gate measurement (k82diag's `cnt_pre.h` twin
  would measure it).
- The `alt-shared` residual compares two runs; see §3 for the in-run arm that would size it.

## Re-ran / changed

Nothing re-timed or re-run on the box (it was running `make mech` in the main clone during this read;
only light reads: two artifact diffs, one python match count over the alpha's own subjects, tool
versions). Files written: this report, `docs/dev/optloop/s4/k82alpha_lx.txt` (+ its CLAUDE.md entry).
