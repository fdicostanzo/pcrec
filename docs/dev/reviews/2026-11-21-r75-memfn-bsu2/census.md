# CRITIC census: memfn-bsu2 (r75)

## Findings


### Census record (part a): U2b re-implemented from §2.1's text, run on W/build/pcrec (SUBJECT d9d86e39e)
Script: R/census/u2b.py (written from block_span.md rev 4.1 §2.1 alone, before reading any lane script; I never read one).
Arms: default vs `--memfn=no-span-vector`, both W/build/pcrec, `-p rxa`, SIMD-off default, same `-o x.c` basename in two dirs;
gcc 15.2 `-O2 -c`; `objdump -d --no-show-raw-insn --disassemble=rxa_search`; normalizer = address prefix stripped,
every `<hex> <sym+off>` operand -> one constant token `<SYM>`, whitespace collapsed, §2.1's padding regex removed. Eligible =
default `.c` defines a `_vs<j>__body`. Class list: from tests/memfn/gen_span_seed.py `GRID` (committed, comment says "confirm.py
CLASSES, in its order"; confirm.py itself is in denied kit scratch): hex [0-9a-f], dig [0-9], word \w, vowel [aeiou], nonl [^\n],
hi [\x80-\xbf], af [a-f], ident [A-Za-z0-9_-], upper [A-Z], num [+.0-9]. Results: R/census/res_a.tsv, res_a2.tsv.
(`\b[0-9a-f]{32}\b` needs `--features assertions`; without it the compile is refused, so a census script that forgets it silently
loses the positive control: res_a.tsv rows 1-2 show the refusal.)

| population | compiled | eligible | IDENTICAL | DIFFERS |
|---|---|---|---|---|
| bench 3 x widths 32, 4095 | 6 | 6 | 6 | 0 |
| grid 10 classes x {17..32} @32 | 160 | 128 | 80 eligible + 32 non-movers (32 of 32 byte-identical C) | 48 |
| `\w{501}` @4095 | 1 | 1 | 0 | 1 |
| total | 167 | 135 | 118 | 49 |

DIFFERS list (normalized added+removed lines: difflib default / difflib autojunk=False / GNU diff):
- word `\w{17}`..`\w{32}` (k 16..31): 16 of 16. e.g. `\w{20}` 42 / 20 / 20; `\w{17}` 36/20/20; `\w{32}` 114/20/20.
- vowel `[aeiou]{17}`..`{32}` (k 16..31): 16 of 16. 38 lines at k 16..23, 52 (difflib) / 38 (GNU) at k 24..31. A block reorder
  (an early-exit `ret` tail moved), not the `\w` operand swap.
- ident `[A-Za-z0-9_-]{17}`..`{32}`: 16 of 16, 2 lines each (one `cmp` operand order swap), all tools.
- `\w{501}` @4095: 2 lines (`cmp %rdx,%r8` vs `cmp %r8,%rdx`), all tools (reproduces r68's figure).
IDENTICAL eligible: hex 16, af 16, nonl 16, dig 8, hi 8, upper 8, num 8 (k 24..31), bench 6.
Add. 4 verdicts: bench sites IDENTICAL 6/6 (build does NOT stop); `\w{20}` DIFFERS (floor witness holds); `\w{501}` DIFFERS;
normalizer two-sided control PASSES: `\b[0-9a-f]{32}\b` 3 -> 0 at both widths (3 padding lines exactly, pre-padding count 3
by both difflib modes), `\w{20}` normalized 20 > 0.

### CENSUS-1 CONFIRMED (doc / speed-unmeasured; effort S; blast: the owner's add. 4 record, §2/§2.2 text): the grid's DIFFERS set is 3 classes, not "`\w`-like sets"; `[aeiou]` (vowel) differs at every k
- Repro: `R/census/u2b.py R/census/jobs_a.tsv OUT` (or by hand: `W/build/pcrec -p rxa -o A/x.c --pattern '[aeiou]{20}'` and the same
  with `--memfn=no-span-vector` into B/x.c; `gcc -O2 -c`; objdump rxa_search; §2.1 normalizer): 38 normalized lines differ (GNU diff and
  difflib agree); 16 of 16 k in 16..31. `[A-Za-z0-9_-]` 16 of 16 (2 lines). `\w` 16 of 16.
- Expected per the design text: §2 "On `\w`-like sets it differs ... None of these is in the corpus or the bench" and §2.2 "The fact.
  The wrapper changes gcc's SIMD-off machine code on `\w`-like sets ... and on none of the 3 real sites". The owner was told (§2.2)
  "differs on 2 of 10 probes (`\w{20}`, `\w{32}`)". At the shipped text the probe grid differs on 48 of 128 eligible cells, 3 of the 6
  window classes; vowel is a 5-equality-term set and a different change kind (a ~38-line block reorder of the early-exit tail, not a
  `cmp` operand swap).
- Ruling consequence, not re-litigation: D201 add. 4 says a differing grid shape is REPORTED, so this does not stop the build; but the
  report must name vowel and ident by class and k, and §2/§2.2's "`\w`-like" summary (and any owner-facing line derived from it) is
  now false as a description of the set. The term-count correlate of §2.2 arm 2 gets one more data point (vowel 5 terms: differs;
  ident: differs; upper 1 range, num 3: identical).

### CENSUS-2 CONFIRMED (doc / maintenance; effort XS; blast: every U2b figure quoted by tool): the "46/42 vs 26/22 vs 24/20" figure spread is python difflib's AUTOJUNK heuristic, not the wrapper text
- Repro: the normalized `\w{20}` pair (R/census/work/grid_word_20/{wrap,deny}): `difflib.SequenceMatcher(None,a,b)` opcodes count 42
  (reproduces rev 4's lane figure exactly; pre-padding 44); `SequenceMatcher(..., autojunk=False)` counts 20; GNU diff counts 20.
  Across `\w{17}`..`\w{32}` default difflib wanders 36..120 while autojunk=False and GNU diff read 20 at every k (rxa_search is
  250..430 instructions, above difflib's 200-item autojunk threshold, so frequent lines like `cmp`/`jbe` are junked).
- Consequence: §2.1's "it NAMES its diff tool ... the count differs between them" and §16 item 12's figures are right that tools
  disagree, but the cause is a heuristic, so a "difflib" figure is not even stable across k. The census verdict (IDENTICAL/DIFFERS)
  is unaffected (`a == b` decides it). Fix: the lane's report states `autojunk=False` (or uses GNU diff) and quotes 20 for `\w{20}`.

### CENSUS-3 CONFIRMED (design / speed-unmeasured; effort S to record, M to census; blast: D201 add. 4's premise for every non-gcc-O2 consumer): the 3 REAL bench sites' SIMD-off code is NOT identical under clang or gcc -Os; the census sees only gcc -O2
- Repro (same W/build/pcrec C pair, same basename, §2.1 normalizer; R/census/res_d.tsv): `W/build/pcrec -p rxa -o A/x.c --pattern
  '\d{32}'` and `... --memfn=no-span-vector -o B/x.c ...`; `clang -O2 -c` each (clang 21.1.8); objdump rxa_search; normalize.
  Observed: `\d{32}` 264 lines differ (GNU diff; clang -O3 267) at widths 32 and 4095; `[0-9a-f]{32}` and `\b[0-9a-f]{32}\b`
  12 lines (a range test re-derived: `lea -0x3a/cmp $0xf5/ja` vs `lea -0x30/cmp $0xa/jb`). `gcc -Os`: all 3 sites 5 lines (a
  branch inverted, `mov $0x1,%edx` moved), both widths. HELD: gcc -O1, -O3, -O2 -fPIC, -O2 -march=native: 0 on all 6 cells.
- Expected per D201 add. 4: "the real bench sites' SIMD-off code must be identical or the build stops". §2.1 fixes one compiler
  and one level (gcc -O2); §2 already says "(not shown for clang)" for the w16 claim only. The owner's premise (add. 2, "the function
  goes inline so it's just code organization?") is true on the 3 real sites only for gcc at -O2/-O3/-O1; a clang or -Os consumer of
  the same artifact gets different machine code on every real site, which the census as declared cannot see.
- Grid, same flags (10 classes x {17,20,25,32}, 32 eligible; R/census/res_c.tsv): clang -O2 DIFFERS 28/32 (identical only nonl);
  gcc -Os 32/32; gcc -O3 12/32 (= the -O2 set); gcc -O2 -march=native 12/32 (word/vowel/ident, larger counts).
- Ruling consequence (not re-litigation): either the add. 4 record states its scope as "gcc 15.2 -O2" (and the owner is told the
  real sites move under clang/-Os), or the census gains a clang and an -Os column. No timing is implied (add. 4 cut it).

### CENSUS-4 CONFIRMED (doc / speed-unmeasured; effort XS; blast: §2/§2.2's "hex and [0-9] do not differ" and the term-count correlate): under `-e utf8` the BENCH classes hex and `[0-9]` differ at gcc -O2 on some k; the census is byte-only
- Repro: `W/build/pcrec -p rxa -e utf8 -o A/x.c --pattern '[0-9a-f]{25}'` vs the same with `--memfn=no-span-vector`; gcc -O2;
  normalized diff 10 lines (an early-exit `xor/cmp/jae/mov/ret` tail moved). Also `[0-9a-f]{28}` 13, `[0-9]{25}` 10, `[0-9]{28}` 13,
  `[a-f]{25}`, `[A-Z]{25}`, `[aeiou]{25}` 10 each, `[A-Za-z0-9_-]{20}` 8, `{25}` 12; `\w{17..32}` 18-30 (GNU diff). Hex k 25..30 and
  dig 25..30 at utf8: DIFFERS at {25} and {28} only (R/census/res_b.tsv, res_e.tsv).
- HELD: the 3 bench patterns under `-e utf8` (widths 32 and 4095 for hex): IDENTICAL 4/4. So the add. 4 stop rule is not tripped,
  but the claim that the differing set is a property of the set (`\w`-like, 4 terms) is false: the same 1-2-term set differs or not
  depending on k and encoding. This strengthens §2.2 arm 2's "no compile-time fact keys it" and weakens the term-count correlate.
- utf8 V-site totals sampled (10 classes x {17,20,25,32}): eligible 20, IDENTICAL 9, DIFFERS 11.

### CENSUS-5 CONFIRMED (doc; effort XS; blast: the census report's k > 31 coverage): at width 4095 the differing set beyond `\w{501}` includes `[aeiou]` and `[A-Za-z0-9_-]` at every sampled k 32..1000; the declared population's one k > 31 cell cannot show it
- Repro: `--window-search-width=4095`, window classes x {33,64,65,256,1001}, scan classes x {33,49,65} (R/census/res_b.tsv): DIFFERS
  15/42: word 33/64/65 (20 lines), 256/1001 (2); vowel 33/64/65 (38), 256/1001 (2); ident all 5 (2). IDENTICAL: hex, af, nonl at all
  5 k; dig, hi, upper, num (T-vscan) at 33/49/65 (12 of 12, so T-vscan k 32..64 held at gcc -O2).
- Same root as CENSUS-1; filed separately because §2.1 (3) says the `\w{501}` cell lets "the census see one k > 31 shape": it sees
  one, the set has three.

## PROBED-AND-HELD


### Coverage record (part b), SIMD-off unless named, IDENTICAL/DIFFERS among eligible (GNU diff and difflib verdicts agree everywhere; counts differ only by difflib autojunk, CENSUS-2)
| shape | sampled | eligible | IDENTICAL | DIFFERS |
|---|---|---|---|---|
| `-e utf8` grid {17,20,25,32} | 40 | 20 | 9 | 11 |
| `-e utf8` hex/dig k 25..30 | 12 | 12 | 10 | 2 |
| `-e utf8` bench 3 (+hex @4095) | 4 | 4 | 4 | 0 |
| width 4095 window k 32..1000 | 30 | 30 | 15 | 15 |
| width 4095 T-vscan k 32..64 | 12 | 12 | 12 | 0 |
| `-fmemfn-simd=x86-64` grid {17,20,25,32} | 40 | 32 | 20 | 12 (normalized text EQUAL to the SIMD-off arm's, 40/40 both arms) |
| `-fmemfn-simd=x86-64` bench 3 | 3 | 3 | 3 | 0 |
| clang 21 -O2 grid | 40 | 32 | 4 | 28 |
| gcc -Os grid | 40 | 32 | 0 | 32 |
| gcc -O3 grid | 40 | 32 | 20 | 12 |
| gcc -O2 -march=native grid | 40 | 32 | 20 | 12 |
| bench 3 x 2 widths: clang -O2 / clang -O3 / gcc -Os | 18 | 18 | 0 | 18 |
| bench 3 x 2 widths: gcc -O1 / -O3 / -O2 -fPIC / -O2 -march=native | 24 | 24 | 24 | 0 |

Compiles used: 620 pcrec compiles (310 wrap/deny pairs; cap 700); ~1,020 small cc compiles of those outputs (clang/gcc flag
columns reuse the pcrec outputs, no extra pcrec compiles).

- HELD: bench sites at gcc -O2 IDENTICAL 6/6 (the add. 4 stop rule passes as declared); the normalizer's positive control 3 -> 0
  exactly as §16 item 12 (both widths) and negative control `\w{20}` DIFFERS; 32 of 32 non-movers (dig/hi/upper/num k 16..23)
  byte-identical C; eligible count 128 of the grid exactly as §2.1 predicts (6 window x 16 + 4 scan x 8); `\w{501}` @4095 2 lines
  as r68; `[+.0-9]` IDENTICAL at k 24..31 and 32..64 (§2's "`[+.0-9]{65}` identical" holds); §2's w16 claim (x86-64 == off) held
  on 40 of 40 gcc text pairs; T-vscan at 4095 k 32..64 12/12 identical; gcc -O1/-O3/-fPIC/-march=native leave the bench sites
  identical.
- Not probed: gcc versions other than 15.2; -O0 (inline depth irrelevant for machine-code identity there per always_inline, not run).
- Largest witness reached: `[0-9a-f]{1001}`/`\w{1001}`/`[aeiou]{1001}` at width 4095 (k 1000, the T-vwin upper bound); longest
  rxa_search 1084 normalized instructions (deny arm, `[A-Za-z0-9_-]{256}` and `{1001}` @4095).

CRITIC COMPLETE
