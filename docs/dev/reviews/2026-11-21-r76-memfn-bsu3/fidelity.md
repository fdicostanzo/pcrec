# CRITIC FIDELITY: r76 memfn-bsu3

## Findings

None. Every probe on this lens held (see PROBED-AND-HELD). No defect against U3 at any routed cell or consumer-flag column measured.

## PROBED-AND-HELD

Tools (all in `fidelity/bin/`): `nd.py` (normalizer), `f2.py` (sub-part a), `fb.py` (sub-part b). Raw tables: `fidelity/f2/f2.tsv`, `fidelity/fb/fb.tsv`; every normalized listing is kept beside its object (`*.nd`).

**Normalizer (`nd.py OBJ FN`), written down:** `objdump -dr --no-show-raw-insn --disassemble=FN`; addresses dropped; alignment nops dropped (`nop/nopw/nopl/xchg %ax,%ax`, with `data16/cs/ds` prefixes); jump targets inside FN -> instruction index (`@iN`, first instruction at/after the target); other symbol targets -> `<sym>` with the prefix `rx_|rxa_` -> `P_` and `.constprop/.isra/.part/.cold.N` suffixes dropped; relocation lines folded into the preceding instruction as `R<type:sym>` (same prefix fold); rip-relative displacements -> `RIP`; `#` comments dropped. Compared on a .o (`-c`), not a linked exe.
- Holds on a known-identical pair: the SHIPPED `[0-9a-f]{17}` artifact emitted with `-p rx` vs `-p rxa` (same compiler, same args), gcc -O2: the two normalized `rx_search`/`rxa_search` listings are byte-identical (56 lines; `cmp` clean).
- Sensitive: shipped hex16 vs timed hex20 differ in 68 lines; shipped hex32 vs timed hex40 in 64 lines (only k's immediates and the block count move), so a 0-line diff is not a normalizer blind spot.

**(a) F2 re-run. CONFIRMED identical, 82 of 82.** `python3 -I -B fidelity/bin/f2.py` over all 130 cells of 710's grid (10 `CLASSES` x 13 k = `KS_OLD`+`KS_NEW`, pattern `atom{k+1}`, built from confirm.py's own literals). For each cell: SHIPPED artifact = `kit/emit.sh subject X.c --features all -fmemfn-simd=x86-64-v3 --window-search-width=4095 --pattern 'atom{k+1}'`; the Pattern line checked on all 130 (0 bad); the site kind read the way confirm.py `base_text` reads it (`_mf1_sh[` present = window) matched `SITE_EXPECT` on 130/130.
- Routed set counted from the SHIPPED build (a cell is routed iff the artifact holds a `_vs0__w32(` call and `RX_MEMFN_FORMS "span-vector@w32"`): **82**, and it is EXACTLY confirm.py's `TABLE` (window 16..1000 = 6 x 11 = 66; scan 24..64 = 4 x 4 = 16). No cell where my count disagrees with 82; the other 48 cells carry `RX_MEMFN_FORMS "none"`.
- Each routed cell: `gcc -std=gnu11 -O2 -w -c` of the shipped .c and of `R/710/work/src/<cell>.avx2-loop.c`, `nd.py` on `rx_search` vs `rxa_search`: **82 IDENTICAL, 0 DIFFERS** (listing sizes 53..98 instructions). 164 compiles.

**(b) Consumer-flag columns.** Cells: one per class at B = 16 and B = 32 (window classes k 16 and 32, scan classes k 24 and 32: hex, dig, word, vowel, nonl, hi, af, ident, upper, num = 20 grid cells) plus the 3 bench sites `[0-9a-f]{32}`, `\b[0-9a-f]{32}\b`, `\d{32}` (k 31, B 16, all three routed `span-vector@w32` at SUBJECT, `none` at BASE whose selector `return rx_mf1_vs0__body(...)`). Pattern lines checked on all 46 emitted files. Matrix product stated before running: (a) 82 x 2 = 164; (b) 20 grid x 5 flags x 3 trees - 40 reused gO2 objects + 3 bench x 5 x 2 + -O0 6 = 314 planned. Actual: 500 compiles used (cap 500), because 80 subject compiles failed at the preprocessor in a first pass (my copy omitted the artifact's `.h`; rerun), so shipped-vs-timed at gcc -Os and gcc -O2 -march=native was DROPPED to hold the cap (shipped-vs-BASE kept at every flag).

| comparison | gcc -O2 | gcc -O3 | gcc -Os | clang -O2 | gcc -O2 -march=native |
|---|---|---|---|---|---|
| SHIPPED vs TIMED (20 grid cells) | 20/20 IDENTICAL | 20/20 IDENTICAL | not run (cap) | 20/20 IDENTICAL | not run (cap) |
| SHIPPED vs BASE (23 cells) | 23/23 DIFFERS (by design: V vs H64) | 23/23 DIFFERS | 23/23 DIFFERS | 23/23 DIFFERS | 23/23 DIFFERS |

What the SHIPPED-vs-BASE DIFFERS is, every cell and flag (from `fb.tsv`'s stats columns: instructions in `rx_search`, calls, stack-memory operands, vector operands):
- SHIPPED `rx_search` is SMALLER in all 115 (cell, flag) pairs: 44..108 instructions vs BASE's 60..537 (e.g. hex32 gO2 58 vs 260; ident32 cO2 60 vs 521; `\b[0-9a-f]{32}\b` gO2 107 vs 532; bench `[0-9a-f]{32}` gO2 70 vs 253, `\d{32}` 61 vs 156). Smallest margin: nonl16 (gO2 58 vs 64; cO2 47 vs 60), the 255-byte set whose H64 chain is one compare per byte.
- Calls left in `rx_search`: 0 in every SHIPPED and every BASE listing at every flag (no un-inlined `__w32`, `__w32_b`, selector or intrinsic).
- Spills/reloads: 0 `(%rsp)`/`(%rbp)` memory operands in every SHIPPED listing (and every BASE one) at every flag; the hot loop holds no stack traffic.
- Vector operands: SHIPPED 15..19 at B = 32 (one ymm block), 26..30 at B = 16 with K 24/31 (two xmm blocks); BASE 0 (3 at -march=native: gcc vectorizes BASE's scalar result store).
- `-march=native` (Zen 4, AVX-512 on): the SHIPPED block compiles to EVEX forms inside the x86-64-v3 region (hex32: `vpternlogq $0xa8` replaces the `vpor`+`vpand`, `vpxorq`/`vpandq`, `vpbroadcastd %ecx`), one instruction shorter, still ymm, 0 zmm, 0 calls. 710 timed at plain `-O2`, so this column's code is not the timed code; it is the consumer's own ISA choice (the same happens to any intrinsic text), and D144 puts SIMD verdicts on the bench, so it is not a U3 defect.
- Whether 710's timing speaks: at gcc -O2 (82/82), gcc -O3 and clang -O2 (20/20 each) the shipped machine code IS the timed machine code; at -Os and -march=native the shipped text was not compared with the timed text (cap), only shown to inline fully with no spills.

**gcc -O0 / clang -O0** (`-std=gnu11 -O0 -Wall -Wextra -c`, hex16 B16, dig24 B16, hex32 B32; 6 compiles): rc 0 and 0 warnings on both compilers (the `unused` on `__body` holds for clang); `nm`: 0 symbols of the `_vs0` family in all 6 objects, i.e. `always_inline` inside `#pragma GCC target` (gcc) and under `#pragma clang attribute push(target(...), apply_to = function)` (clang) inlines every V function at -O0; `rx_search` holds 6 `pshufb` and 0 `call` in all 6; ymm 0 at B = 16 on both compilers; at B = 32 gcc 138, clang 276. This is the C18 -O0 rule's (1)+(2) shape on clang too, which §16 item 10 drilled on gcc only.

Witness sizes reached: k 16..1000 (pattern length 17..1001) in (a); k 16..32 (17..33) in (b), plus the bench sites at k 31. No subjects were run on this lens (static machine-code comparison only; answers are another lens's question).

Case counts: 130 cells classified, 82 F2 comparisons, 60 shipped-vs-timed consumer comparisons, 115 shipped-vs-BASE comparisons, 6 -O0 objects, 2 normalizer controls; 500 compiles; 0 timing runs, 0 perf runs.

CRITIC COMPLETE
