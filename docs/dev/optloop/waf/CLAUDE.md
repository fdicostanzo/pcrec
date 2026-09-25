# docs/dev/optloop/waf/ — S3 WAF attribution instruments (lane wafread)

The instruments behind `../waf_attribution.md` (compare_stack.md §6.1 S3).
They are reproduction pieces. Nothing here times anything on darwin. Every
script reads `/Users/fdicostanzo/pcrec-bench` read-only (or the `BENCH_ROOT`
it is given) and writes only to the OUTDIR it is handed. §4 of the reading
is the Linux executor block that uses these files to take the owed timings.

## Files

- `waf_numbers.py` / `waf_numbers.txt` — every non-twin number the reading
  cites:
  - set-grain ns/B per testee for the five cells, from the capability@0.1
    report TSVs (value / 1,376,256);
  - the subject census: candidate-set densities, per-letter case counts,
    keyword and bigram presence, bytes/word.
- `stamp_join.sh` / `stamp_join.txt` — compiles all 64 capability patterns
  with the auto-nocaps flag set and joins their route stamps to pcrec
  `b1885a83`'s bench ns/B. It is the source of the 63-byte `\b` cluster in
  §3.4.
- `mk_inputs.py OUTDIR` — writes two files:
  - `match.bin`: t-64k with WAF/secret keyword spellings spliced in at seed
    7. The throughput subjects hold zero matches, so an answer check on them
    alone is vacuous. python `re` counts: dbnames 7, union-select 9,
    sleep-benchmark 6, split 10.
  - `split.rx`: concat-sqli minus its `^` arm, the same edit as I-85 M5.b.
- `mk_twin.py` — builds a hand-twin from a SHIPPED artifact. Each twin moves
  one variable:
  - `plainloop` deletes the forward scan's skip/stay dispatch chain, so the
    DFA steps every byte (re2's shape);
  - `ciprecheck RUN LETTER` inserts a whole-window caseless necessary-run
    pre-check: two leapfrogged `memchr` streams over LETTER's two cases, plus
    a `|0x20` compare of RUN. RUN must be all ASCII letters.
- `spans.c` — the answer driver. It uses the find-all loop of
  `cycle1_analysis.md` §0.5's `findall.c` and prints every span.
- `check.sh BASE.c TWIN.c SUBJECT...` — span-for-span identity of a twin
  against its base. It prints `SAME`/`DIFF` and exits 1 on any DIFF.
  Validated in the failing direction twice (2026-09-25):
  - a wrong run (`unions`) gave union-select 9 → 0;
  - a skip table that skips `d`/`D`/`i` gave dbnames 7 → 2.

## Validation done here (darwin, answers only)

- Every `plainloop` twin (dbnames, split, union-select, sleep-benchmark) and
  every `ciprecheck` twin (`union u`, `from f`, `from m`, `select c`) is SAME
  on t-64k/t-256k/t-1m and on `match.bin`.
- The match counts on `match.bin` equal python `re`'s.
