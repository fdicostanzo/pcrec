# CRITIC check: memfn-bsu5 (r79)

## Findings


### CHECK-1 (CONFIRMED, answer/maintenance, small, claim 4): the span-vector hash is blind to the b=16 block, the shipped V text of ALL THREE real C6 cells
`span-vector`'s ONE instance is the hex set at k 40, so `vs_w32_block` renders b = 32 only (`b = k >= WF_VBLK_MAX ? 32 : 16`).
The real cells hex32, hexb32 and dig32 are k 31 and the bound cells hex17 (k16) and dig25 (k24) are k < 32, so their V text is the
b = 16 (`__m128i`, `_mm_*`) block, which no instance renders. Plant PV16b (`<` -> `<=` only where b = 16; the finder ran it, rc=0,
0 FAIL) and PV16 (`"_mm"` -> `"_mmX"`): `fx --hash` span-vector = a9efa02907d0645b, IDENTICAL to subject, while
`pcrec -p rxa --features all --window-search-width=32 -fmemfn-simd=x86-64-v3` emitted C MOVES at c6_hex32, c6_hexb32, c6_dig32,
c6_hex17, c6_dig25 (8 patterns compared, at SUBJECT vs plant: PV16 and PV16b move exactly these 5). So a change of V's text at every
cell the card's real-pattern rule reads can leave kit-grid@8's `deps` unstaled. Needs: one more instance (k 24, b = 16) or a per-b
instance list in block_span.md §8 `deps` ("the canonical instance" names one). The finder passed PV16b (rc=0): no check reads a
b = 16 text. Min witness: pattern `[0-9a-f]{32}` (k 31), width 32.

### CHECK-2 (CONFIRMED, answer, small, claim 4): mf_form_hash alpha-renames every identifier not in `kept[]`, and the `_mm*` intrinsics are not kept, so an intrinsic swap is invisible even INSIDE the covered b = 32 block
`fx --hash-text` over the instance's own site text (`fx --site-text span-vector`), one sed each: `_mm256_cmpeq_epi8` -> `_mm256_cmpgt_epi8`,
`_mm256_srli_epi16` -> `_mm256_srli_epi32`, `_mm256_loadu_si256` -> `_mm256_load_si256`: hash a9efa02907d0645b UNCHANGED (all three
change what V computes or its alignment contract). A swap onto a name already present moves it by the first-occurrence numbering
(or -> and: 31dc185e...), and a changed immediate (`set1_epi8(15)` -> `(14)`) moves it. Plant PV32 (`"_mm256"` -> `"_mm256X"`, every
b = 32 intrinsic renamed) is SAME on the hash, SILENT-MOVE on the text at hex33, hex1001, dig65 (the three b = 32 cells). This is the
pre-existing normalization (D-row for R-MS3: "a rename keeps the hash"; it covers mfind-w16/-w32 identically), but claim 4 says
"stales when the V text changes" and V's text IS intrinsic names. Cheapest fix: add the `_mm*`/`__m*` families (a prefix rule, or
the intrinsic names V uses) to `kept[]`; an abi-neutral change that re-stales every stored kit-grid hash that folds an intrinsic
(mfind-w16/w32's: a re-measure event, so a decision for main, not a quiet edit).

### CHECK-3 (CONFIRMED, doc/maintenance, small, claim 4 second half): the hash moves on non-V text
The instance text is 31 lines: the 256-entry skip table `mf_mf1_sh` (line 1), the window driver loop `pos = ({ ... for (;;) ... })`
(line 31) and `__body` plus the selector around V. Plant PBODY (`__body` parenthesized) moves the hash and the text of all 8 cells
(fine: shipped). But an edit of the window DRIVER or the skip table stales the row though V's block is unchanged, and the scan
cells (dig32, dig25, dig65: the R7w SCAN driver, a different loop) are not covered by the window driver the instance renders. Not a
wrong answer (over-staling is the safe side); §8 should say "stales on the whole window site's text", not "on V's".

### CHECK-4 (CONFIRMED by text, speed/doc, small, claim 4 + claim 5): the clang card C6c's V arm is the SIMD-OFF wrapper, whose selector text the x86-64-v3 instance does not render
At no SIMD flag the selector is `return rxa_mf1_vs0__body(...)` (check/off/o.c line 67); the instance's selector (site.txt line 28) is
`return ...__w32(...)`. The hash instance is x86-64-v3 only, so a change confined to the SIMD-off selector/wrapper path moves C6c's
three off-clang V cells (the card's clang arms) and stales nothing; kit-grid@8's dim says `layer` `on` only with C6c "below" yet the
row has the one `deps`. Witness not built (would need a plant in fn_selector's off branch; the text difference is shown above).

### CHECK-5 (CONFIRMED, maintenance, small, sub-part (b)): `check_c6` tests the PRESENCE of text, not that the shipped site reaches V, and has no self-test
`check_c6` is called only from `cmd_dry` (cards.py:1185); no selftest control (grep: no `C6` in `cmd_selftest`), unlike C1-C5's
(F15)/(G7) controls, so a regression of the regexes passes silently. With a monkeypatched `cards.artifact` on edited copies of the
real hex32 V text (`check/probe_c6.py`), check_c6 returns 0 failures for: selector rewritten to `return __body(...)` (w32 defined,
never called), the site never calling the selector (the `_vs[0-9]+\(` regex matches the DEFINITION), `__w32_b`'s body replaced by
`return 1;`, the loop condition inverted, and `__w32` present only in a comment. It does fail for a deny arm carrying V text. The
card would then time V-shaped dead code against H64 as "V". The dry's own answer-gate (ok 1863 etc.) catches the wrong-answer
ones, not the dead-code ones; the dead-selector one is answer-identical by construction. A reach control would be: the call site
(`pos = ({`) line contains `_vs[0-9]+(`, and the selector's body contains `__w32(` at the `on` layer.

### CHECK-6 (nit): FORM_INSTANCE_FLOOR is 14, instances are now 16 (15 before U5)
The floor never moved with U5; the exact set check (`want_all - seen`) covers a missing instance, so the floor is dead weight.

### CHECK-7 (SUSPECTED, nit): facts for the new entry (`fx --facts span-vector -`) read `f_set_shape` and say `hit: a byte of members`, `table -`; nothing states the stretch's k 40 or that this is a block span. Not pinned anywhere I found; the facts reader is outside this lens.

## Plant compare table (shipped emitted C, 8 C6 patterns at on/their width; hash = `fx --hash` span-vector)
| plant | edit | hash | text moves at | class |
|---|---|---|---|---|
| PV32 | b=32 intrinsic prefix | SAME | hex33, hex1001, dig65 | SILENT-MOVE |
| PV16 | b=16 intrinsic prefix | SAME | hex32, hexb32, dig32, hex17, dig25 | SILENT-MOVE |
| PV32b | b=32 loop `<=` | MOVES | hex33, hex1001, dig65 | LOUD (hash) / finder green (no stored row) |
| PV16b | b=16 loop `<=` | SAME | hex32, hexb32, dig32, hex17, dig25 | SILENT-MOVE (finder rc=0) |
| PBODY | `__body` return parenthesized | MOVES | all 8 | LOUD (hash); finder green |
| S2930 | pair row := walk's | SAME (span-vector) | none | SAME; DETECTED by finder_check (4 FAIL: row reached pf_walk; two ids one text; edit left hash; fold), plus check C STALE lines on zen4-grid3@1 `pair` rows |

## PROBED-AND-HELD (check)
- S2930: DETECTED (finder rc=1, 4 FAIL lines + check C STALE on pair rows); subject rc=0 (28926 checks, 0 failed); PBODY, PV16b, PV32b finder rc=0, 0 FAIL: the suite does not read V's text (no stored kit-grid@8 row), the claim rests on the hash alone (CHECK-1/2).
- `m6read_check_sab_anchors.py` on the review tree: 1387 sabotages, 1446 anchor sites, all resolve; only S2930 (re-aimed), S2933 (loop line untouched) and S2931 (`verify_cmp` row untouched) quote formhash.c/kit-grid.tsv. §10.2 "At U5" is right on all three; S2931's "unchanged by an append" is loose (a comment block was inserted mid-file too), still anchored.
- `hash_edits` row `i += 32` -> `i += 31`: the site exists once; edit/foldedit hashes differ from base (aa81... vs a9ef...); `hash_mode` id list includes span-vector; FORM_IDS row token `span-vector@w32` matches the renderer's own assert; CARD_FORMDEP_COUNT 21 equals the finder's count ("check C: 21 cards").
- check_c6 real artifacts: 11 pairs, 0 failures; it correctly fails a deny arm carrying V text.
- Compile budget: 56 pcrec compiles + 3 deny, 0 gcc.
CRITIC COMPLETE
