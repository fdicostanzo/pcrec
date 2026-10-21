# docs/design/kit_proof/x0/ — step X0 of `../../kit_proof.md` §7 (spec §6.4)

X0 checks `../conj.py`'s reading (revision 2.1, the prototype of `MkEnd` + `MkLang`)
against an INDEPENDENT libpcre2 oracle, before Z2. Nothing here is built or run by
`make`, nothing reads a clock, nothing under `src/` is touched. Lane `x0oracle`,
2026-10-21. Results: `results.md`.

- `x0pcre.c` — the libpcre2-8 side: a line-protocol server (`V`, `K`, `P`, `N`, `Q`,
  `T`, `F`; protocol in its header) that knows no reading. `Q` is the per-byte next
  set every check reads: a byte is in it only with a WITNESS, a complete PCRE2 match
  anchored at the origin whose span covers the prefix (a byte that opens or continues
  a UTF-8 character is completed exhaustively over the code points it can begin). The
  plain hard-partial set (`N`) is kept for the record: it OVER-approximates (below).
  Build: `gcc -O2 -std=gnu11 -o build/x0/x0pcre docs/design/kit_proof/x0/x0pcre.c -lpcre2-8`.
- `x0.py` — the driver. `pop` builds the population; `run` runs X0 over it (part 1,
  the per-position per-byte set equality, and part 2, the differential; `--plant`
  sets one of conj.py's `CONJ_PLANT`s, `--self` one of X0's own plants on the plan);
  `plantpop` writes each plant's mover population; `stated` checks STATED sets
  (S1150, S1149) against libpcre2; `summary` folds a result file. Docstring = usage.
- `stated.tsv` — the stated-set rows `stated` reads: S1150's union-narrowing plant and
  S1149's pass-through plant (must read RED), and the correct per-thread / in-span
  slice statements of `ctx_span.md` §3.8 and kit_proof §5.2 (must read green).
- `results.md` — the measured X0 run: population, counts, every red cell classified,
  the plants and X0's self-plants, the oracle defects found and fixed, the regime.
- `out/` — the committed transcripts `results.md` cites (summaries and the plant /
  stated / witness outputs; the per-item JSONL stays in `build/x0/`, regenerable).

Oracle hazards found while building it (each would have produced confident wrong
cells; each is fixed in `x0pcre.c` and recorded in `results.md`):
- hard partial matching reports PARTIAL whenever the subject ends with an assertion
  pending (`(?:a*\b)*b` reads `a` as a prefix of a match no string has);
- under `PCRE2_MATCH_INVALID_UTF` it reports PARTIAL at the end of every valid
  FRAGMENT (`@é`: `"@\xC3@"` reads as a prefix);
- libpcre2 10.46 under `MATCH_INVALID_UTF` answers an `ANCHORED` match that starts
  PAST a leading invalid sequence (`a` on `"\x80a"` from 0 gives (1,2)); every
  anchored probe now requires the match to start at the origin (`K` counts them).

Reproduce from the worktree / repo root with `build/pcrec` and `build/x0/x0pcre` built
(the population and runs compile thousands of patterns: run them under
`scripts/boxlock run`):
`PCREC=build/pcrec python3 -I docs/design/kit_proof/x0/x0.py pop build/x0/pop.jsonl`, then
`... x0.py run build/x0/pop.jsonl build/x0/res.jsonl -j 8`.
