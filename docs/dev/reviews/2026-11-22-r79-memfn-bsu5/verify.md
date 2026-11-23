# verify.md: r79 memfn-bsu5, coordinator inline verification (quote claims and one-call repros)

## CHECK-1 (F1): HOLDS
plants PV16b / PV32b (kit/build_plants2.py): `run.sh plant:PV16b fx --hash` span-vector a9efa02907d0645b == subject; PV32b 39a9c54c4594026a (moves).
`run.sh plant:PV16b pcrec -p rxa --features all --window-search-width=32 -fmemfn-simd=x86-64-v3 --pattern '[0-9a-f]{32}'` vs subject: line 90 `i + 16 < 31` -> `i + 16 <= 31` (+ RXA_SIMD_GUARDED_BYTES). finder/PV16b.log rc=0, 0 failed. Plant compiler exit 0.

## FIDELITY-1 (F4): HOLDS
.coord/v/v1.py: subject('c6_hexb32', R, 1 MiB, seed 1), count c with (c==0 or s[c-1] non-word) and s[c+31] hex: near-miss 0, near-miss-in 1, hit-dense 31775; alphabet of both miss regimes `0-9a-f z`. Artifact a_5c811767a5e1d1bd.c (Pattern: \b[0-9a-f]{32}\b) line 400: left-\b test `&&` before `rxa_mf1_vs0(`.

## MEAS-1 / MEAS-5 (F2): HOLDS (the shared-pool fact)
`arm_flags('H64') == arm_flags('H64.b') == (build/pcrec, ['--memfn=no-span-vector'])`; `pool_variants(textkey)` is a function of the text key alone (cards.py pool_variants). No code computes an A/A rate (grep H64: arm_flags, CARDS, check_c6 only; meas critic).

## MEAS-2 (F7): HOLDS
cards.py pool_variants (hash of "pool|textkey"), pool_size_refusal (n != 4 refused).

## MEAS-6 (F8): HOLDS
`awk '/^```$/{n++; next} n==1' R/decision_rule_710.md | sha256sum | cut -c1-16` = 6351bff3901e3955; whole-file sha 624faced24c2addb.

## SLOT-1 (F3): HOLDS
`hasattr(cards, 'align_variants_of')` False.

## SLOT-2 (F9): HOLDS
cards.LOOP_RE over dry/run/art/*.c: 22 artifacts, 2 match, both `Pattern: [0-9a-f]{1001}`.

## CHECK-2 (F15): HOLDS
`fx --site-text span-vector` (31 lines) -> `fx --hash-text` a9efa02907d0645b; sed cmpeq->cmpgt: a9efa02907d0645b (unchanged); sed set1_epi8(15)->(14): 4abb1a1b51c13494 (moves).

## SLOT-6 (F17): HOLDS
`fx --facts span-vector`: `shape window-span`, `hit a byte of \`members\``, no k row.

## FIDELITY-2 vs MEAS-7 (F12): PARTLY (FIDELITY-2)
Read regimes_of's docstring: "plus near-miss-in at C6's WINDOW sites where k + 1 <= 255 (710's definition: the cards' near-miss never calls the span there ...)": "there" = k + 1 <= 255; at k 1000 the plain near-miss reaches the span (MEAS-7 depth model, 0..745). The deviation from §8's text stands; the reason does hold.

VERIFY COMPLETE
