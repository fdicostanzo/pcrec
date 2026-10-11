# D-F loss triage (slot21), read-only

Sources: run/raw.tsv, run/meta.tsv, run/art/<cell>/{DEFAULT,NOPAD,FULL}/rx.c and rx_v{1,3}.o (objdump of the existing .o only; no compile, no timing). Scripts: tmp/dftri/a.py, b.py.

## Bottom line
- The losses are NOT launch outliers (7 of 10 are consistent in all 3 launches with sub-1% spreads) and NOT the guard margin moving iterations into the final block (arithmetic below).
- The sparse/gate losses sit in the kit's own SIMD main loop (reqrun scan), whose per-byte instruction stream is identical between arms. The residual difference is code layout / loop alignment (m10: FULL's hot-loop head is exactly 64B-aligned; DEFAULT's straddles a 64B line) plus launch-level bimodality (v11). They are level-specific (v3 only) and, for the biggest cluster, appear in NOPAD too (trim-only arm, same shape as FULL), which a logic cost cannot explain.
- A second, smaller cluster (v05, v13, v07) follows the padded form (D-N positive) but is 64k-only for v05 (1m is flat), so it is a fixed-per-call cost, not per-byte; it is modest (+7..+17%) and not yet explained.
- Verdict: layout/alignment artifact + a small genuine per-call pad cost on a few cells; not a verify-logic regression. One cheap re-run settles it (end).

## Per-loss table (medians over 3 launches; per-launch D vs F delta; N-F, D-N, other level)
Per-launch D-F computed as DEFAULT_Lk/FULL_Lk - 1 (ns, launch k). "sp" = reported reading spread of DEFAULT/FULL for that launch.

| cell: pattern | regime/lvl | D med | F med | D-F med | per-launch D-F (L1/L2/L3) | spreads D / F | N-F | D-N | D-F other level (same regime) |
|---|---|---|---|---|---|---|---|---|---|
| m10: `(?i)\bcat\b` | gate/tail-1m v3 | 18611 | 15086 | +23.4 | +28.4 / +23.4 / +18.3 | 0.2-0.3 / 0.1,0.1,21.6 | +32.3 | -6.8 | v1 -8.8 |
| m10 | sweep/sparse-1m v3 | 19183 | 15861 | +20.9 | +13.0 / +21.9 / +22.9 | 0.1-0.4 / 0.0-0.4 | +27.9 | -5.5 | v1 -4.9 |
| m12: `(?i)(cat)s?dog` | sweep/sparse-64k v3 | 1238 | 1017 | +21.7 | +21.9 / +22.8 / +19.8 | 0.1,1.4,0.1 / 0.0,0.6,2.5 | +33.7 | -8.9 | v1 -4.8 |
| v03: `(?i)(?>abc)` | gate/tail-1m v3 | 717819 | 596433 | +18.8 | +17.4 / +20.4 / +17.3 | 0.7,5.4,1.6 / 0.3,0.5,6.9 | +34.4 | -11.6 | v1 +1.3 |
| v11: `(?i)foobar` | gate/tail-64k v3 | 16888 | 14343 | +17.7 | +1.9 / +18.4 / +17.8 | 0.4-0.6 / 29.7-34.0 | +29.8 | -9.3 | v1 -1.5 |
| v05: `((?i:abc))` | gate/tail-64k v3 | 20666 | 17662 | +17.0 | +16.4 / +17.0 / +16.4 | 0.3-1.2 / 0.5-1.9 | +6.0 | +10.4 | v1 +3.4 |
| v05 | space128 v3 | 21996 | 19587 | +12.3 | +12.9 / +12.3 / +7.4 | 0.0-0.7 / 0.4-2.1 | +4.45 | +7.5 | v1 +2.4 |
| v05 | sweep/sparse-64k v3 | 17104 | 15422 | +10.9 | +10.5 / +12.1 / +11.2 | 1.0-1.7 / 0.3-1.7 | +2.65 | +8.05 | v1 +5.4 |
| v07: `(?:(?i:ab)S\|(?i:abs))` | gate/tail-64k v1 | 30569 | 25143 | +21.6 | +9.7 / +21.9 / +14.8 | 3.9-5.6 / 3.0-23.9 | +14.8 | +5.9 | v3 -19.4 |
| v13: `(?:(?i:sab)\|S(?i:ab))` | sweep/dense-64k v1 | 26372 | 23681 | +11.4 | +15.3 / +11.8 / +7.1 | 2.5-7.4 / 0.3-21.2 | +6.8 | +4.2 | v3 -4.0 |

Reading the table:
- Consistent and tight (not noise, not one launch, outside own spread): m10 (both), m12, v03, v05 (all three). These 7 rows are deterministic losses of the artifact as built.
- Within or near own spread: v07 (FULL L1 spread 23.9%, DEFAULT 4-6%, L1 delta only +9.7), v13 (FULL spreads 11-21%, delta falls 15 -> 7 across launches), v05 space128 L3. These are weak.
- v11 is bimodal: DEFAULT L1 14671 (= FULL level) vs 16967/16888; NOPAD L3 14344 vs 18622/18676. Same code, different launch, 15-30% apart. FULL's own spread is 30-34% every launch. Launch-level mode, not a code effect.
- Every v3-only loss (m10, m12, v03, v11) has the opposite level (v1) within -9..+1: the same C structure compiled as w16 shows no loss. A logic/algorithm cost would appear at both levels.

## Q2: full diff DEFAULT vs FULL emitted .c (identical in all 7 cells' structure; only constants differ)
Each rx_reqrun__w16 and __w32 gets exactly these changes (checked m10, m12, v03, v05, v07, v11, v13):
1. Declarations added before the loop: `uint32_t pw, pk, pt;` (v11: `uint64_t`) + two `memcpy(&pk/&pt, "<const>", 4|8)`. Compile-time constants; pk/pt become immediates (objdump: `and ecx,0xdf0000; cmp ecx,0x540000`), pw a plain `mov ecx, DWORD PTR [..]`. So the memcpy load IS a single mov; no register pressure from pk/pt.
2. Main guard `i + L + E <= n`: `i+19` vs `i+18` (w16), `i+35` vs `i+34` (w32); v11 `+23` vs `+21`, `+39` vs `+37`. E=1 (4-byte pw over a 3-byte run) or E=2 (8-byte over 6).
3. Control-flow restructure: FULL = `if (guard) {m=..} else {final-block m, i=f}` then ONE shared `while (m) {verify}; i += W`. DEFAULT = `if (guard) {m=..; while(m){padded verify}; i+=W; continue;}` then a SECOND copy of the verify loop for the final block. The verify loop is therefore duplicated and the main path ends in `continue`.
4. Final block: DEFAULT adds the clamp `if (f > i) f = i;` (FULL has no clamp; FULL's final block is entered only when the guard failed so f<=i already). Final-block verify stays the unpadded `rx_w2`/`rx_w4` trimmed form in DEFAULT.
5. Verify predicate: trimmed single `rx_w2(subject+cand+k) & mask == tgt` (or the padded pw form) vs FULL's two-compare whole-run form.
6. `RX_SIMD_GUARDED_BYTES` changes (0xe48 vs 0xc06 in m10): a constant in a macro, not on the hot path (spec/ABI-visible only).
Nothing else (no change in the vector body, masks, broadcasts, search/gate wrapper, or non-reqrun code).

Assembly of the hot loop (m10 v3, from the existing rx_v3.o):
- FULL: head 0x80 (mod64 = 0); `vpand,vpand,vpcmpeqb,vpcmpeqb,vpand,vpmovmskb,test; jne cb (not taken); jmp 220 (taken); 220: add r14,0x20; lea; cmp; jae 80 (taken)`. 2 taken branches/iter, loop lives in 2 cache lines.
- DEFAULT: head 0x7d (mod64 = 61, the first 7-byte vpand straddles the 0x80 line boundary); `...test; je c4 (taken); c4: add; lea; cmp; jae 7d (taken)`. Also 2 taken branches/iter, same instruction count, but body spans 3 lines (0x7d..0xcf) and the entry instruction straddles a line.
- NOPAD (trim only; same shape as FULL): head 0x6a/0x77, mod64 = 42/55; times between DEFAULT and FULL's worst.
Heads (mod 64, .o-relative; .text is align 64 so these survive linking if rx.o is first): m10 D 61 / N 42 / F 0 (times 18.6k / 20.0k / 15.1k, monotone with misalignment); m12 58/45/55; v03,v05 D 49 / N 39 / F 53; v11 N=F=24 (yet N-F +29.8: bimodal); v07, v13 (v1) D=N, F +4. So alignment is a strong fit for m10 only; for the others the head offsets do not separate the arms, so it is a hypothesis, not a proof.

## Q3: does the loss follow the pad or the trim?
- Cluster A (m10, m12, v03, v11; all v3): N-F is the big number (+28..+34) and D-N is NEGATIVE (-5..-12). NOPAD (trim only, FULL's loop shape) is the SLOWEST arm and DEFAULT is partly better than it. That cannot be a padded-word cost (pad is what makes D faster than N here). FULL is the fast outlier; the trim and the pad are both "losing" against a lucky layout. Also m10/m12 show the same ~+20..+35% at pc256/pc1024 (many candidates), so the same arm ordering extends into a verify-heavy regime, but m10 v1 and the other regimes at v3 show ~0..-5%.
- Cluster B (v05 x3, v13, v07; v05/v13 small, mostly v1/v3 mix): D-N positive (+4..+10), N-F small (+3..+15). Follows the padded form. v05's loss is present at 64k regimes (gate/tail-64k, space128, sparse-64k, dense-64k: +10..+17) and ABSENT at 1m (gate/tail-1m +2.1, sparse-1m -2.7, dense-1m -1.7): a per-byte main-loop cost would scale to 1m. A fixed-per-call cost (a few us, not by bytes) is what appears; this fits the final block or call prologue, not the verify.
- Level: Cluster A is v3-only; Cluster B is on both levels for v05 (+2..+5 at v1).

## Q4: hypotheses, ranked by evidence
1. Layout / loop alignment (+ launch-level bimodality), strongest. m10: a monotone relation between the hot-loop head alignment and time across the three arms with an identical instruction stream; NOPAD (shape == FULL) loses +28..+34 while DEFAULT is better than NOPAD; v3-only; v11 shows the same code at two speeds in different launches. The slot's null bands (floors ~2%) come from byte-identical cells, which cannot see layout noise between differently-sized binaries, so a 20% layout swing is invisible to them.
2. Per-call fixed cost in the padded form (cluster B: v05 64k-only). Plausible mechanisms: the second copy of the verify loop + the clamp changes final-block code or its branch-predictor state; the extra register-resident constants. Unproven; magnitude 3us out of 20us on v05's 64k cells.
3. Noise / one outlier launch: explains v07 (FULL spread 24%, delta 9.7/21.9/14.8), v13 and v05 space128 L3, and half of v11; does NOT explain m10, m12, v03, v05 gate (all 3 launches same sign, sub-1.5% spreads).
4. Guard margin moving iterations into the final block: REJECTED by arithmetic. E=1 (w16/w32) changes the guard from `i+18/34 <= n` to `i+19/35 <= n`; with i advancing in multiples of the block width and starting at pos, at most the last block of a call changes sides, with probability ~E/W (1/16 or 1/32 for E=1; 2/16 for v11) and a cost of one block. On a 64k subject that is at most 1 block of 2048-4096; on 1m 1 of 32768. The block count is the same either way (the final block runs once per call in both arms: for n=65536 and pos aligned, i = n-32 fails both guards; `f>i` clamp only triggers when the guard failed). Cannot yield +20%.
5. u64 memcpy load not a single mov: REJECTED from the existing .o: `mov ecx, DWORD PTR [r12+rax]; and ecx,imm; cmp ecx,imm` (w32/v3). v1/v11 u64 not disassembled but `memcpy(&x,p,8)` with gcc is a mov by construction.

## What single cheap re-run settles it
Re-time ONLY the 7 cells m10, m12, v03, v05, v07, v11, v13 at v3 (+v1 for v07, v13), arms DEFAULT/NOPAD/FULL, with the harness's launch count raised to 5 and arm order shuffled per launch (kills ordering and launch-mode), and compile every arm with `-falign-functions=64 -falign-loops=32` (GENCFLAGS or per-cell CFLAGS in the harness). Read:
- If cluster A's D-F and N-F collapse to within ~2-3%: it is layout, and no kit change is needed (the null-band method needs a layout-control column).
- If cluster B (v05 at 64k) stays +10..+17% under forced alignment: it is a real per-call cost of the padded form; the next artifact to compare is v05's final-block asm (obj in run/art/v05/*/rx_v3.o).
Cost: roughly 7 cells x ~12 regimes x 3 arms x 5 launches x 0.26 s = ~5.5 min of readings plus 21 small compiles; one core pinned (cpus 12-15), compatible with the box rules once slot22 is done.

---
Kit manager, 2026-10-11, Frank's direction: no compiler-flag fixes for these losses. The forced-alignment
re-run is DIAGNOSTIC ONLY, if run at all; nothing ships flags. The fix path is a survey of the loss items
for an emit-time predicate (a first-match decline row from pcrec's facts). Lane losssurv, read-only.
