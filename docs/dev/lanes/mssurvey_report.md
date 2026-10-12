# mssurvey — [MATCH-SPLIT] STEP 0, the class-mix survey (2026-10-12, lane mssurvey, sonnet)

Branch `lane/mssurvey` from main `35b78793` (abi 75). Compile-only: no clock, no timing; one
counted-work arm (a subject-load COUNT, section 4). Nothing under `src/`. Instruments, TSV and verbatim
outputs: `docs/dev/optloop/matchsplit/` (own CLAUDE.md; `summary.txt`, `qwork.txt`, `oracle.txt`,
`c4.txt`, `ms_rows.tsv.gz`). Design: `docs/design/match_split_requirements.md` section 6, run as written.

## 0. Headline

- **Pin-only population (no free arm; 4a's customer): 35 of 5,703 ok patterns.** Bench 0, catalog 0, corpus 11,
  D27 files 0, **idioms 24** (the hand-written list, see Honesty). **32 of the 35 take
  `attempt` with `start_max = subject_length` today** (the gratuitous forward scan). The 22 named-idiom
  members: `^\s+|\s+$` and 9 trim spellings, the wrapper strip `^\s*\{|\}\s*$` (plus its captured form, on the
  hybrid), quote/bracket/paren/slash/dot strip, comment strip `^#|//.*$`, `(?m)^\s+|\s+$`, `^|end$`, `^|$`.
- **K106's trim shape is quadratic, confirmed by COUNT** (section 4): on `Q . \t*k . Q` the find-all loads
  128,040,002 subject bytes at k = 16,000 (8,001 loads per byte), growth 15.99 per 4x of k, on all 11 trim-family
  DFA-attempt shapes (`^\s+|\s+$`, `(?m)^\s+|\s+$`, its comment variant, `^[ \t]+|[ \t]+$`, `^\s*|\s*$`, `^\W+|\W+$`, `/+`, `.+`,
  nbsp x2, and the 2016 outage's `^[\s\x{200c}]+|[\s\x{200c}]+$` under `-e utf8`). The wrapper strip is NOT
  quadratic (2 loads/byte) but makes one attempt entry per byte per call (16,001-16,003 attempts at k = 16k).
- **A second quadratic population the note did not name: END-only on the VM-only route.** `(\s*)$`, `(a*)$`,
  `(\w\d)*$`, `((a)|(b))*$` ... (10 of 16 measured) show the same 15.99 growth. These are single-class (E-only)
  and a capture or similar puts them on the VM, where `rev-end` does not apply. The controls (`\d+$`, `\s+$`,
  `.*\.txt$`, `\w+\z` on `rev-end`) are constant or linear.
- **Trigger verdict (section 6.5, stated in the note before the count):** START+FREE MET already (witness
  concat-sqli; count (c): 26 S+F patterns, 2 bench = concat-sqli in two sets, 21 on attempt/n).
  No-free-arm: bench-cell leg NOT MET (0 bench patterns); idiom-catalog leg MET BY CONSTRUCTION only (24 idioms I
  wrote, all on attempt/n bar 3) and judged by Frank (Q5). Quadratic risk: MET (non-zero (d), superlinear
  counted work). END+FREE density: NOT MET (no bench E+F; the 42 E/LE+F are corpus/idioms).

## 1. Denominators (K35)

| population | rows | probe-refused | compile-refused | ok | byte | utf8 |
|---|---|---|---|---|---|---|
| bench | 367 | 16 | 9 | 342 | 270 | 72 |
| corpus (non-D27) | 3,870 | 261 | 6 | 3,603 | 2,945 | 658 |
| corpus D27 (`composition_d27`, `d27/`, `matrix.rxt`) | 1,775 | 148 | 5 | 1,622 | 1,622 | 0 |
| catalog (realistic_patterns.txt) | 40 | 0 | 0 | 40 | 40 | 0 |
| idioms (added) | 97 | 1 | 0 | 96 | 94 | 2 |
| **total** | 6,149 | 426 | 20 | **5,703** | | |
| planted (C4, not counted) | 35 | 0 | 0 | 35 | | |

Every count below is over the `ok` column. Recipe control: 0 rows the probe refused that pcrec's compile
accepted. Refusals are pcrec's own diagnostics (variable-length lookbehind 59, repeat errors, gated `\p`, `\K` in
lookaround 19, ...), top ten in `summary.txt` section 0. The bench's 16 probe-refused are its `syntax` cells for
constructs pcrec does not compile (callouts, verbs, `\c`, ...), as the bench itself marks them.

## 2. (a) Mix labels (classes among LIVE paths)

| mix | bench | corpus | D27 | catalog | idioms |
|---|---|---|---|---|---|
| F | 290 | 2,692 | 1,274 | 39 | 1 |
| S | 33 | 432 | 214 | 1 | 22 |
| E | 12 | 303 | 66 | 0 | 18 |
| LS | 2 | 24 | 18 | 0 | 10 |
| LE | 2 | 43 | 1 | 0 | 2 |
| G | 1 | 19 | 20 | 0 | 3 |
| E+F | 0 | 29 | 3 | 0 | 2 |
| S+F | 2 | 12 | 3 | 0 | 9 |
| G+F | 0 | 20 | 2 | 0 | 1 |
| LS+F | 0 | 8 | 0 | 0 | 0 |
| LE+F | 0 | 4 | 0 | 0 | 0 |
| S+E | 0 | 1 | 0 | 0 | 20 |
| LS+LE | 0 | 2 | 0 | 0 | 4 |
| S+E+F | 0 | 0 | 0 | 0 | 4 |
| E+LE, G+LS, G+E, S+LE, S+LS | 0 | 3,2,1,1,1 | 0 | 0 | 0 |
| - (no live path) | 0 | 6 | 21 | 0 | 0 |

The mix-by-route table for all populations (and per population) is `summary.txt` sections 1-2. Reading it:
the bench is 85% free-only, and its only mixed-pin pattern is `wild-waf-crs-942360-concat-sqli` (S+F, in the
`capability` and `sentinel` sets). The bench's single-class pinned cells are `S` (33, `start_max = 0`), `E` (12,
all `rev-end`), `LS` 2, `LE` 2, `G` 1.

## 3. (b) The pin-only population, prominently

35 patterns; by label S+E 21 (1 corpus, 20 idioms), LS+LE 6, E+LE 3, G+LS 2, and G+E, S+LE, S+LS 1 each.
By route: `dfa-attempt[subject_length]` 29, `hybrid-attempt[subject_length]` 2, `dfa-unanchored` 3 (the E+LE,
where both end classes are served by the unanchored scan), plus G+LS/G+E/S+LS on dfa-attempt[n]. 32 of 35 on
attempt/n. The full per-pattern list is in `summary.txt` section 3. Of the corpus's 11, every one is a
hand-built `tests/assertions` witness (`^a|b$` anchors.rxt:55, `(?m)^a|b$` multiline.rxt, `\Ga|(?m)^b` gpos.rxt, ...).

## 4. (c) and (d)

**(c) ATTEMPT with `start_max = subject_length`: 169 of 5,703** (148 DFA, 21 hybrid); other attempt routes
(`start_max` 0 or `search_from`) 475. By mix: LS 54 (the MLINE route; not split material), G+F 21, S+F 21
(bench 2, corpus 10, D27 3, idioms 6), S+E 21, no-live-path 12, LS+F 8, S 7, F-only 7 (see Findings), LS+LE 6,
S+E+F 4, G 3, and singletons. This discharges [OPT-ATTEMPT-SPLIT]'s owed count: its member (S+F on attempt/n) is
**21 patterns, of which 2 bench**. VM-only route: 838 patterns (no `start_max` stamp); mixed members there are few (S+F 5, E+F 2, G+F 2), single-class S 261 and E 45; table in `summary.txt` section 4.

**(d) quadratic risk.** 190 patterns have an end-pinned path led by an unbounded repeat; 29 of them sit on a
route that tries every start (13 are mixed with another class). Work counts (`qwork.txt`; 30 patterns + 6
controls; load count, no clock) at k = 1,000 / 4,000 / 16,000 on `Q . c*k . Q`:
- 11 trim-family shapes on dfa-attempt: T = 502,502 / 8,010,002 / 128,040,002, growth 15.99, attempts 16,003;
  their trailing-run and whole-run subjects are linear (T = n, 2-3 attempts).
- wrapper strip (`dfa` and `hybrid`): T = 2n, growth 4.00, but attempts = n+3 per call.
- VM-only END shapes: 10 of 16 growth 15.99 (e.g. `(\s*)$` 256,064,005 loads at 16k); `(a*)(a*)$` hit the step
  budget (T flat at 1.0e9); two shapes failed to run at 16k (give-up/timeout, not counted); `(.*)$` and
  `(.*)\z` linear.
- controls on `rev-end`: `\d+$`, `.*\.txt$`, `[a-z]+\.txt$`, `\s+$`, `\w+\z`, `a*\z`: constant or linear.
Run byte and terminator were chosen per pattern by search (max T at k = 500); this is an upper-case probe, not a
typical subject.

## 5. (e) density, (f) bench cells, (g) decline predicates

**(e)** 99 mixed patterns have a free class; the free text compiled for all 99. For 72 (byte, both start-sets
known): free start-set mass is >= 10x narrower on 10, >= 2x narrower on 24, within 2x on 38, never wider,
never empty. Route change when the free part is compiled alone: 42 `dfa-attempt[n]` -> unanchored, 11
`hybrid-attempt[n]` -> unanchored, 5 vm-only -> dfa unanchored; **no free part stays on attempt**. Free-part
prefilters: memchr 37, offset-set 18, run-pinned 11, byte-class 7, none 14, against today's mostly `none` (57)
and byte-class-bounded (19).
**(f)** (reused, not re-run: `studies/walk_survey/results/cells_bench.tsv`, pin `5e23b90c`, abi 71): the only
bench cell family with a gratuitous attempt phase is concat-sqli (K11): throughput T/LB 3.145 (14.7M loads vs
4.68M subject bytes), search-short 2.98; the other pinned cells (`anc-m-caret`, `asr-caret-ml`, `anc-g-uc`) have
T/LB 0.0-1.04. That joined weight is the entire bench side of the split.
**(g)** 42 E/LE+F patterns: N1 (route already the free class's own, no START class) 36; END arm unbounded
(END part alone has no `end_window`) 20, bounded 22; N3 (landmark-start END arm, proxy) 14. N2 (find-all density x
walk) and N4/N5 need the primitive / the regime / the size term: stated, not counted.

## 6. Flags (section 6.2)

Dead anchored paths 75 patterns (all corpus: 38 + 37 D27), line anchor away from the edge 3, anchors inside
lookarounds 14 (7 ahead-pos, 7 behind-pos, 2 ahead-neg; all corpus), `\K` on 27 of 1,380 pinned patterns,
redundant pin (structural lower bound) 11 patterns (S 3, G 3, E 5; all corpus), 637 of 1,380 pinned patterns
carry both pins on one path (`^...$`), nullable by class F 557 / S 149 / E 134. Zero of these flags occur in
bench, catalog or idioms except where stated.

## 7. Controls

- **C1 single-class agreement (plumbing)**: S 702 rows, 8 disagree on `start_anchor` (all `OPTIONAL-CONSUMER ^`
  shapes, `a{0,4}\A`, `\w*^\b`, `[a-c]?\Aa`); G 43 / 5; E 399 / 9 (`a$.*`, `x$.*`, `$[^\n]*`, `a$\n`,
  `[a-z]{0,4}\z[a-z]*` : shipped `end_pin` declines, path analysis says E-only); LE 48 / 0; LS 54 / 0; F 4,296 /
  0 on both start_anchor and end_pin. The probe's `ew_walk` copy vs the shipped `end_pin`: 3 disagree, all `\G`
  with an end pin (the shipped fact declines under `\G`). Full list: `summary.txt` section 9. All 22
  disagreements are corpus witnesses where the SHIPPED fact is the conservative side.
- **C2 libpcre2 10.46 soundness** (`oracle.txt`): 1,269 no-free rows (26 `\K` excluded: `\K` moves the reported
  start), 57,040 matches, 0 violations; 951 of the 1,269 rows produced a match (318 never matched on the sampled
  subjects: UNREACHED, so unverified, not verified). Negative control (`--selftest`, every path declared
  E-only): 236 violations, red.
- **C3 free-part identity**: free text 113 rows / 7,244 anchored hits, END text 1,111 rows / 27,657 hits, 0
  violations (never a start the full pattern lacks). **C-RT** (unparse language-identical): 1,091 rows, 71,073 hits,
  0 violations; plus the stamp-level round trip: 5,653 of 5,666 comparable the same route, 7 refused (surrogate
  classes, size cap), 3 differ (`(?J)` duplicate names, `x(?i)ab` prefilter memchr vs handoff, `\p{sc=Greek}`).
- **C4 planted** (`c4.txt`): 35 witnesses green; plant `ml_edge` (line anchor treated as a pin everywhere)
  red on 1, plant `look_end` (lookahead `$` treated as END) red on 2.
- **C5 reach**: UNREACHED labels S+G, LS+E, LS+LE+F, S+LS+E+F (stated empty); every other label has a population,
  bench-reaching ones only F, S, E, LS, LE, G, S+F. **C6** not applicable (all compares are on stamp/fact
  values; the one emitted-text read, `start_max`, is a single `-o -` compile).

## 8. Real-world idioms added (6.1.3)

`docs/dev/optloop/matchsplit/idioms.txt`, 97 patterns, hand-written from memory: trim/strip family (18),
comment handling (9), CSV/TSV fields (4), word-or-edge (5), path/URL/version tails (9), `\G` tokenizers (4),
line filters (7), validators (6), WAF-style rules incl. CRS path traversal (7), degenerate anchors (`^`, `$`, `\A`,
`\z`, `^|$`, `^|end$`, `(?m)^|$`, `^|x`), two `_u8` spellings (the outage's pattern needs a code point above 255).
Honesty: this list is my guess at what people write, so the idiom column proves the shapes EXIST and what pcrec
does with them, not how common they are.

## 9. Findings for the manager

1. **The requirements note mislabels `(?m)^\s+|\s+$`**: its `$` is a LINE end, so the class mix is LS+LE, not
   LS+E (planted P5). A true LS+E is `(?m)^\s+|\s+\z`.
2. **Trim is quadratic on the DFA attempt route AND E-only captured patterns are quadratic on the VM** (section 4).
   The second is outside [MATCH-SPLIT]'s pin-only scope (single class) but has the same cause: nothing walks from n.
   File candidates: K row for the trim shape (Q3), and a separate look at VM-only E-only (10 of 16 measured).
3. **Dead and landmark anchors still force the attempt loop**: F-only patterns on the attempt route are 8 (all corpus): `ab|a\Gb`, `a\Gb|c`, `x\G|y` (dead `\G`, equal to `ab`, `y` ...), `a(?m)^b`, and two
   `(?(DEFINE)...\G/\A...)` wrappers. 75 patterns have dead anchored paths, all corpus; 0 in bench/idioms.
4. **Redundant STARTs**: 11 patterns (`(\A)*`, `(^)*ab`, `a(?:$|.)*`), all corpus; none in the idioms. The
   fact-only move F2 predicts is real but its population is test witnesses only.
5. **Anchors inside lookarounds**: 14, all corpus. The one realistic shape is `(?<=^|,)(\w+)$`
   (stage2_captures.rxt:1325), the CSV field in lookbehind form; and the `(?m)^` spelling
   `\A|(?<=\n)(?!\z)` (tests/ucp/ctxnode.rxt:392) classifies as S plus an unclassified lookbehind path.
6. **The shipped facts are conservative on 22 corpus patterns** (C1): optional consuming prefix before `^`/`\A`/`\G`
   (13) and optional consuming tail after `$`/`\z` (9) read `unanchored`/`end_pin none` although only the
   empty-prefix path is live. One fact generalized to `has/must/free_live` would pick these up.
7. **Unparse round trip catches a route dependence on a non-language field**: `x(?i)ab` and `(?J)` duplicate
   names compile to a different prefilter from the language-identical unparse. Not investigated.
8. **Bench side is thin**: the bench has exactly one pattern (concat-sqli) with a mixed pin class and nothing
   with S+E; the `anc-wrap` wishlist family (6.6) is what would change the bench verdict.
9. The pin-only corpus members are all hand-built witnesses; the probes' structural `redundant` is a floor.

## 10. Honesty and limits

Texts for FREE/END parts are an unparse of the raw tree (control C-RT/C3 validates it; var-bearing patterns 44
and 29 backref-with-multiple-refs are not unparsed). The `lu` (led by an unbounded repeat) and mix labels are by
path analysis, not syntax. Quadratic subjects are probes chosen to maximize work. Counts in section 5(f) are
joined from an older pin. Run/box: Linux dev box, `make -j4`, compiles at 3 workers, no `make test`.
