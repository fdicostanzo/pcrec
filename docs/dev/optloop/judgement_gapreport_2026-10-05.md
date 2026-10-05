Judgement for the second [OPT-GAPREPORT] instance (lane o83read,
2026-10-05). The ranking is by gap × breadth × realism (D119-filtered),
against pcre2-jit first. The input is report group `round1-c4c70f2c`
(bench O-83).

**Read this first: the instrument fix.** `extract.py` keyed pcrec cells by
short testee name. A cross-pin report group, which is every re-pin window,
carries pcrec at two pins, so the last row in the TSV won, cell by cell.
This instance's first render mixed `fc719ca4` and `c4c70f2c` numbers: it
showed union-select at the old 0.724 ns/B where the pin reads 0.338.

- **The fix.** `extract.py` now keeps only the newest pin, named by the
  report header's `null_band: pcrec OLD -> NEW`. Two pins without that line
  exit with an error.
- **Validation.** `--check` stays OK (its fixture is single-pin).
- **The first instance is unaffected.** `gapreport_2026-10-03.md` read
  single-pin `fc719ca4` groups.
- **litrun joined `gapconfig.SETS`.** It has a jit column only, no scalar
  ceilings.

**What moved since 2026-10-03:**

- CI's union-select: x16.6 → x7.74 behind jit (C3's win).
- K82 (B) made two groups worse:
  - CI's mod-i/mod-r: x2.27/x2.30 → x3.84/x3.91;
  - DENSE's cls-fold-pair: x1.81 → x3.05.
- BCLS lost its `cls-upto-*` match cells to [OPT-VEDGE].
- Every other group is unchanged within its band: START-SET, CTX,
  NULLABLE-ANCH, U8-PICK, CARET, LKA, BACKTRACK, SCAN-SIMD, WIDE-ALT.

Round 1's four items did not touch those groups, and none was aimed at them.

**Ranked groups where pcrec trails, each mapped to its plan row:**

| # | group | cells / gap (peer, else ceiling) | realism | row | judgement |
|---|---|---|---|---|---|
| 1 | START-SET (FS-DFA + FS-VM) | 18 cells, 5 sets; aws-access-key-id **x43.9** (interp x18.8 faster than pcrec), quoted-delim x21.7, balanced-parens x9.1, loglines stack-frame x4.85 | real (loglines, capability) | [OPT-FIRSTSET] + [OPT-VMSEED] (D124: one question, two consumers) | **Still #1, unchanged.** Largest, broadest and clearly algorithmic. Litrun adds a second aws cell (x5.31). |
| 2 | CTX | 10; loglines level-context **x3.83** (rust x10.5), bounded ctx-* x1.5 | real (loglines) | [OPT-VMLIT] trigger; [ENG-TACTICS]; [CTX-PREFILTER] | Profile first, as on 10-03. C1 moved the bounded ctx-* hybrids by 0.5-2.7%, not their gap. |
| 3 | CI + DENSE's fold cells (K82 cause B) | mod-i/mod-r **x3.84/x3.91**, cls-fold-pair x3.05, cls-pair-ctl x1.15 | synthetic (syntax) + utf8 | K82 (B): the HANDOFF (built on `lane/k82hbuild`, abi 61, Linux alpha owed); forced-VM half: [OPT-VMSEED] | **Round 2's first item is already built.** Predicted to return mod-i to about x2.3 and cls-fold-pair to about x1.8 (`litscan_k82h.md` §3.2). The remaining CI gap is union-select x7.74 / slack x6.59 vs jit, rust-only on the ceiling side: SIMD territory. |
| 4 | NULLABLE-ANCH | 2; evil-alt-nested **x5.98** jit / x38 re2; trim-nested-star x3.0 jit / **x1081 re2** | capability | **NEW, still unfiled** (10-03 slated it; no plan row exists) | File the row. A compile-side census first, as 10-03 said. |
| 5 | U8-PICK | 10 utf8 cells; pcrec leads jit, trails re2/rust x1.2-x15.7 (lit-sharp-s) | utf8 | **NEW, still unfiled** | File the row. The cheap two-artifact twin (`-e byte` vs `-e utf8` of one literal) first. |
| 6 | SEL-LIT (NEW this instance) | 5 litrun cells; lit-l40 x3.20, lit-l31 x2.72, lit-l16 x1.74, lit-l8 x1.62, lit-l7 x1.18 behind jit | synthetic (litrun's adversarial densities) | [SEL-COST] (a new measured bucket); [OPT-VMLIT] | The evidence is pcrec's OWN forced VM, which the mechanical "algorithmic" column cannot see (litrun has no scalar comparator). The VM beats auto on every literal length (x1.4-x4.7) and beats jit on l7/l16/l31/l40. A SELECTION gap, not a missing engine. Unknown whether the sign holds on real text: see the measurement below. |
| 7 | CARET | 2; concat-sqli re2-longest x5.39 | capability | [OPT-ATTEMPT-SPLIT], [ENG-ABS-CARET] | Unchanged; a round-3 candidate. |
| 8 | LKA | 9; lkb-neg x3.47, lka-pos/verb x3.21 | syntax | [OPT-HYB-RESEED-XCALL] (held), [CTX-PREFILTER] | Unchanged by round 1 (A2 was dropped). C1 moved lka-verb's forced VM (0.910 → 0.626 ns/B), not auto. |
| — | SCAN-SIMD / WIDE-ALT | 20 / 31 cells; rust-only | mixed | [OPT-SIMD], [MEMFN] | SIMD-phase deferral (D119), as on 10-03. litrun `alt-foo-tails` x8.20 is filed here (synthetic; the scan byte `f` is dense in litrun's subjects); [MEMFN]'s two-byte kernels are its lever. |
| — | BACKTRACK | 14; x1.17-x3.00, interp slower everywhere | — | none | FUNDAMENTAL (D119). |
| — | BCLS, CALL-FLOOR, ENDWIN-ENC | ns-scale or small | — | [OPT-NEG], [OPT-ENDWIN-ENC] | Null-scale, so nothing is filed (D144 addendum 1). email `floor` whole-subject (+1.3 ns per call vs rust) joins CALL-FLOOR. |
| — | K82-AT-PIN | userpass x9.62 jit | capability | K82 (A), FIXED at abi 60 | Not a candidate. k82alpha measured the cure (0.0168 ns/B). The bench re-measures it at the next pin. |

**What would settle each open question:**

- **SEL-LIT.** A desk read of every bench cell where `pcrec-vm` beats
  `pcrec-auto` on a literal-led DFA artifact, across capability, syntax,
  utf8 and litrun. The data is already in the reports' vm-caps arms; no
  build is needed. If the sign holds only on litrun's synthetic densities,
  it closes as synthetic.
- **CI after the handoff.** The `alpha_k82h.sh` Linux alpha.
- **NULLABLE-ANCH and U8-PICK.** Their census and twin respectively, as on
  2026-10-03.

**Where pcrec leads** is unchanged in shape: 515 ahead, 20 level, 96 behind
vs jit. utf8 and altwide lead everywhere.

**What could not be judged:**

- litrun has no scalar ceiling.
- The four K83 cells (clang) are not in this bench at all.
- The 22 patterns pcrec has no record for (§4) are unchanged from 10-03.
