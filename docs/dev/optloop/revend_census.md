# `[OPT-REVEND]` — a REVERSE-FROM-END SEARCH: the D77 census

**Lane `revend`, 2026-10-05.** Census only: nothing under `src/`, `cli/`,
`lib/` or `tests/`; compile-side, plus ONE scratch-tier timing block (§4)
that prices today's linear scan, not a ledger number. Chartered by Frank's
question (2026-10-05): *could the DFA run in reverse from the END of the
subject?* Instruments, verbatim outputs and the Linux provenance:
`docs/dev/optloop/revend/` (its `CLAUDE.md`). Pin: main `6611e541` (abi 61)
plus the lane's probe files; the census ran on ubuntubudu (gcc 15.2, Ryzen
1600) under `nice -n 10`, the Mac being in a full `make test`.

## 0. The headline

* **The idea is sound and exact** (§2): for a pattern every match of which
  ends at `n` (`\z`) or at `n` / `n-1` (`$`, `\Z`), the existing reverse
  machine seeded at `n` (and at `n-1` when `s[n-1] == '\n'`) and run until it
  dies yields the leftmost start `s0` directly; one anchored forward run from
  `s0` then fixes the end and the captures. Work is proportional to the
  match, not the subject, on matching AND non-matching subjects (a subject
  whose last bytes cannot be the pattern's last bytes kills the walk in a
  step).
* **The population it could serve is empty on the bench and thin in the
  corpus.** Of 4,857 patterns probed (344 bench exports, 4,513 `.rxt`
  blocks), 22 bench / 705 corpus are end-pinned. Of those, **the bench has
  17 start-anchored too (`^...$` validators: one attempt at 0, nothing for a
  reverse walk to find), 5 bounded-width (already served by the SHIPPED
  `[OPT-ENDWIN]`, 24-160 ns on 1 MiB), and ZERO start-unanchored
  unbounded-width ones.** The corpus has 33 such patterns (32 + 1 distinct;
  47 + 1 rows), nearly all `eol_engine`/`absolute`/`view_edge` correctness
  witnesses (`a*$`, `.*$`, `[a-z]+\z`), none a real-world idiom.
* **The cost it would remove is real where the idiom exists.** Hand-run on
  Linux over a 1 MiB prose-like subject (scratch tier, §4): `\d+$` 0.87,
  `\w+$` 3.15, `\s+$` 2.5-3.1, `[a-z]+\.txt$` 3.2-3.3, `\s*$` 1.8 ns/B —
  3-3.3 ms per MiB against ~40-160 ns for the same shapes when bounded and
  window-clamped. A reverse-from-end walk would price them at the match
  length (tens of ns): a x10^4-10^5 swing on a 1 MiB subject, in the shape
  `[OPT-ENDWIN]` already produced for the bounded half.
* **Recommendation: file the row, do not schedule it.** D77 asks for a
  measured need; the bench has no cell in this population. The trigger is a
  bench cell (an `anc-tail` family: `\d+$`, `\s+$`, `\w+\z`, `.*\.txt$`) or a
  user-supplied corpus showing the idiom at rank. Mechanism, exactness and
  where it does not help are chartered in the plan row so the build is cheap
  the day the trigger fires.

## 1. Method

`census.py` builds two populations and asks two instruments about every
pattern (sources in `revend/`):

* **bench** — every `bench/*/patterns/*.rx` export in `pcrec-bench`
  (read-only), compiled as the bench's `pcrec-auto` testee does (`--features
  all`; `-e utf8` on the `utf8` set): 269 patterns in the byte sets + 76 in
  the utf8 set = 345; 13 + 3 refuse to compile, none of them end-related
  (`\cG`, `(?C1)`, `\X`, `(*SKIP)`, `(*UCP)`, `\p{InGreek}`, the
  variable-length lookbehind witness).
* **corpus** — every `pattern` block of every shipped `.rxt`
  (`pcrec --list-source`), 4,512 blocks, compiled with the BLOCK'S OWN
  `encoding` (utf8 or byte) and `flags` (`i` as a `(?i)` prefix; `u` is not
  modelled, 9 blocks). `features` is widened to `all` — the census asks about
  the pattern, not whether a gated module is on (379 byte + 30 utf8 blocks
  still refuse: size caps, `\X`-class, unsupported verbs).

Two instruments, cross-checked:

* **PROBE** `revend_probe.c`: links `libpcrec.a`, parses and lowers like
  `compile.c` (`altcls`, `discharge_atomic`, `lower_enc` — the recipe
  `reqrunenc_probe.c` documents and the reason for), and walks the tree with
  a COPY of `src/facts/endwin.c`'s `ew_walk` plus a `(?m)`-`$` level, the
  maximum/minimum width, a leading-unbounded-repeat flag and a `\G` flag.
* **FACTS** `pcrec --emit-facts`: the SHIPPED `end_window` fact (value and
  why), `start_anchor`, and the artifact's decision stamps.

Cross-check (byte encoding, 4,412 rows with a facts row): **0 rows where the
probe says end-pinned and the shipped fact says `not-end-anchored`, and 0 the
other way** (the converse was run on ALL rows, `FACTS_ALL=1`). One
disagreement class, understood: 138 corpus rows the probe calls unbounded
(`^(a|b)\g<1>$`, recursion witnesses) the shipped fact calls bounded, because
the fact reads the post-resolve tree where a subroutine call is expanded and
the probe's pre-resolve walk calls a call's width unbounded. The census
therefore takes bounded-vs-unbounded from the SHIPPED fact on byte rows and
from the probe only under utf8, where the fact hides everything behind
`decline:enc-multibyte`. All 138 are start-anchored, so no class below moves.

## 2. The mechanism, and why it is exact

Today (`src/gen/emit_dfa.c` header; the emitted `<prefix>_search` for `\d+$`,
read in full): ONE forward pass finds the leftmost-first match END with the
unanchored priority DFA, then ONE backward pass with the non-pruning reverse
DFA, seeded at that end and stopping at `search_from`, takes the earliest
accepting position as the START. The reverse pass already exits on a dead
state. The forward pass is the O(subject) term for an end-pinned pattern: a
`last_accept_position == -1` machine cannot stop before the subject's end,
and the candidate-start skip loop only helps while the machine is parked in
state 0.

**Reverse-from-end** replaces the forward pass by a seed. Let `E` be the set
of possible match ends: `{n}` for `\z`, `{n}` plus `{n-1}` when `s[n-1] ==
'\n'` for `$`/`\Z` (this is exactly the `eps` of `[OPT-ENDWIN]`, and the
reverse machine's existing EOL view already knows both positions). Run the
reverse DFA from each `e in E` while `e >= search_from` until it dies; let
`s* = min` accepting position over the seeds.

* **Leftmost start.** Every match ends in `E`, so the set of starts of
  matches is exactly the set of starts of matches ending in `E`, and `s*` is
  its minimum: the leftmost-first match begins at `s*`. (The existing
  forward-then-reverse protocol relies on the same fact in the other
  direction: the earliest start with a match ending at the forward end `e0`
  is the leftmost start, because the leftmost-first match `[s0, e0)` itself
  is among the candidates.)
* **The end and the captures.** At `s*` the END may still be `n` or `n-1`
  (`a*?$` over `"a\n"`: both `[0,1)` and `[0,2)` begin at 0; leftmost-first
  prefers by priority, not by length), and `D77` records the same trap for
  `_match_caps(...) == n`. So the walk yields `s*` ONLY; the span and
  captures come from the artifact's existing anchored entry run at `s*`
  (`rx_match`'s machine for a DFA artifact; the VM for a captures-bearing
  one, over the found span only). That run is O(match), the same shape the
  hybrid already uses for captures.
* **No match.** If every seed dies before accepting, there is no match, with
  no forward pass at all.

**Where it does not help** (each is a census class, §3):

1. **Start-anchored** (`^...$`, class S): the search is one attempt at 0; a
   reverse walk finds the same thing the attempt does. D77's whole-subject
   idiom `(?:P)\z` is this shape (anchored at 0 and at `n`), served by the
   anchored entry.
2. **Bounded width** (class B): `[OPT-ENDWIN]` clamps the start window to
   `n - (maxw+eps)` on both engines, 24 ns flat on 1 MiB. Reverse-from-end
   has nothing to add on byte encodings. **Under utf8 the clamp declines
   (`decline:enc-multibyte`, K49/K50); a reverse walk is the natural
   replacement there**, but no bench or corpus pattern lives in that cell
   (bench utf8: 3 S + 1 start-anchored `^\p{L}{4}$` whose compile stops after
   the probe; corpus utf8: 15 S, 1 B).
3. **Leading unbounded repeat whose run IS the subject** (`.*x$` over a
   single huge line, `[a-z]*$` over an all-letter subject): the reverse
   walk's extent equals the match, which equals the subject. It is no worse
   than today's forward pass (same order) and no better.
4. **`(?m)$`** pins nothing to the subject's end (D62 control 3): 56 corpus
   rows, 1 + 1 bench rows (`syntax/anc-m-dollar`, `utf8/asr-dollar-ml`), all
   out of scope; they are the trailing x2.5 `jit` cell of the gap report and a
   different mechanism (a per-line end walk).
5. **VM-only patterns** (backreferences, `(*pla:...)`, `\g<1>` that stays a
   call, lookaround): no reverse machine to run. 16 of the 48 corpus rows in
   class U are VM-routed.
6. **`\G` anywhere**: the clamp (and this) moves `search_from`; 2 corpus
   rows, declined as `[OPT-ENDWIN]` declines them.
7. **A trailing lookaround** (`item(?= done)`, `abc(?=\z)`): the shipped
   walk declines it and so does this; 44 corpus + 3 bench rows (all `lka-*`)
   are the near-miss population, counted not chased.

**Correctness edges the build must carry** (each is a row of the answer-net,
none is new machinery):

* `$`'s final-newline allowance under the one newline convention that exists
  (LF): two seeds; with DD-11's value-parameter conventions `eps` widens (the
  same constant `EW_EOL_SLACK`), nothing else changes.
* `search_from`: the walk never passes below `search_from` (today's
  `rewind_position <= search_from` stop); `search_from > n` answers 0 before
  anything (existing guard); `search_from == n` and the empty subject fall
  out of the same loop — a nullable pattern (`\s*$`, `x*$`) accepts at the
  seed itself (`\s*$` over a subject ending in a non-space reports an empty match at
  `n`, as the timing block's `nomatch` row does).
* Lookbehind / `\b` at the LEFT boundary and `^` in a branch: the reverse
  machine already carries the left context (it is the machine of today's
  second pass); a `^`-bearing pattern has no reverse machine (ENG_ATTEMPT,
  `emit_dfa.c` header) and so is class S by construction.
* The `\z`-with-`search_from` trap D77 names for the idiom does not arise:
  the seed is `n`, not `search_from`.
* `-e utf8`: seeds at `n` / `n-1` are character boundaries under valid text;
  the walk must step by characters through the reverse machine's own
  boundary handling, and the K49/K50 guard that makes `[OPT-ENDWIN]` decline
  is exactly this obligation. The build must discharge it or keep the decline.
* Captures: the VM runs over the found span (the hybrid's existing
  protocol); nothing about group semantics changes.
* Cap/refusal sets: the reverse machine is already in every DFA artifact with
  `RX_DFA_START "reverse-pass"` (all 140 DFA-engine rows of class B and U carry it); the mechanism adds a loop, not a table, except that a
  `"pinned"` artifact (no reverse machine at all) is excluded, as it is
  for any `^`-free pattern whose start accepts unconditionally.

## 3. The census

All figures: rows / distinct (encoding, pattern, `(?i)`) where stated.
`out/summary.txt` carries the verbatim tables.

### 3.1 Populations and classes

| population | enc | compiled | end-pinned (`$`/`\Z`/`\z`) | S start-anchored | B bounded, start-unanchored | U unbounded, start-unanchored | `\G` | no facts | `(?m)$` |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| bench | byte | 256 | 22 | 17 | 5 | **0** | 0 | 0 | 1 |
| bench | utf8 | 73 | 4 | 3 | 0 | **0** | 0 | 1 | 1 |
| corpus | byte | 3,504 | 705 | 529 | 117 | **48** (47 L + 1 I) | 2 | 9 | 56 |
| corpus | utf8 | 599 | 28 | 26 | 1 | **0** | 0 | 1 | 0 |

Distinct patterns: bench byte 21 of 249 are end-pinned (17 S, 4 B), bench
utf8 4 of 72; corpus byte 523 of 2,904 (403 S, 76 B, 32 UL, 1 UI, 2 G, 9
no-facts), corpus utf8 17 of 420.

**Question (1).** End-pinned patterns: 22 bench byte + 4 bench utf8 rows
(7.5% of the bench's 345); 733 corpus rows (16.2% of 4,512, dominated by
`tests/assertions` and `tests/base`, which exist to test anchors). Suites of
the start-unanchored subset (B and U): bench `syntax` 3 (`anc-dollar`,
`anc-z-lc`, `anc-z-uc`), `litrun` 1 (`ctrl-abc-dollar`), `capability` 1
(`wild-semdiv-dollar-trailing-newline-pcre2`), all `abc$`-shaped; corpus
`assertions` 95, `base` 37, `mrl` 8, `possessify` 8, `captures` 2,
`lookaround` 13, `offsetskip` 2, `recursion` 9, `utf8` 1.

**Question (2).** Bounded vs unbounded among the start-unanchored: bench 5 vs
0; corpus byte 117 vs 48; corpus utf8 1 vs 0. "Dies within a bounded
distance" is, for the pattern, "maximum width finite" (class B, window shipped
for byte). Class U cannot be bounded by the pattern; its reverse walk is
bounded by the SUBJECT's structure instead (a `\d+$` walk runs the trailing
digit run and stops at the first non-digit). Class U splits 47 L (some
alternative begins with an unbounded repeat — `\s*$`, `[a-z]+\z`, `.*=.*$`,
`\w+\b$`) and 1 I (`a.*$`, unbounded only in the interior); L is where the
"leading `.*`" caveat of §2 item 3 bites hardest, and also where the idiom
is (`\s+$`, `\d+$`). Every corpus U pattern is a correctness witness: 33
distinct, listed at the end of `summary.txt`'s generating run (`a*\z`, `.*$`,
`[a-z]*$`, `a*b$`, `\w+\b$`, `[a-z]+@[a-z]+$`, `(a+)$`, ...).

### 3.2 What they get today (question 3)

From the `RX_*` stamps of the facts run (rows):

* **Class B, byte (122 rows with stamps).** Every one is a derived-window
  row (`RX_END_WINDOW` a number) and runs flat; engine `dfa` 108 (107
  `unanchored`: prefilters `memchr-bounded` 49, `byte-class-bounded` 18,
  `none` 15, `offset-set-bounded` 13, `run-pinned-bounded` 12; plus 1
  `attempt`), `vm` 14 (hybrid `*-bounded` prefilters where stamped). The D77
  "final-byte skip gap" is closed for this class by the window clamp itself:
  the Linux block shows `abc$` at 40 ns and `\.txt$` at 80-160 ns on 1 MiB
  against 174,000 / 468,000 ns with `-fno-end-window`.
* **Class U, byte (48 rows).** 32 DFA, 16 VM. `RX_END_WINDOW "none"` on all.
  DFA prefilters: `none` 14, `memchr-bounded` 9, `byte-class-bounded` 9 (the
  `-bounded` spelling is the accept test, not a start bound). **No stamp bounds the forward pass**: the forward
  loop runs to `n` or to a dead state, and a dead state is rare on prose
  (§4).
* **Does a skip loop already make them cheap? No.** The self-loop skip
  (`rx_can_begin_match` while parked in state 0) helps only the stretches
  where the machine IS parked; for `\w+$`/`\s+$` over prose it is parked for
  a few bytes at a time, so the transition loop pays ~3 ns/B (opt3's
  7-cycle load chain, `opt3_dfa_scan_measurement.md`) on most of the subject.
  `.*\.txt$` (`memchr-bounded`) is the cheap one: 0.23 ns/B on the matching
  row, 0.58 on the no-match row.

### 3.3 The bench cells (question 4)

Round-1 report group `round1-c4c70f2c` (O-83), read from the bench's `.tsv`
files with `bench_cells.py` (`bench_cells.tsv`; set-grain medians, throughput
regime = sum over the set's three subjects, 1,376,256 B for `syntax`):

| cell | pcrec auto-caps | jit | rust | note |
|---|---:|---:|---:|---|
| syntax `anc-dollar` throughput | 24.2 ns | 212,011 ns | 80.8 ns | B, ENDWIN |
| syntax `anc-z-lc` throughput | 25.0 ns | 212,949 ns | 79.9 ns | B |
| syntax `anc-z-uc` throughput | 24.3 ns | 211,506 ns | — | B |
| litrun `ctrl-abc-dollar` throughput (27 subjects, 1.77 MB) | 454 ns | 1,218,419 ns | — | B |
| capability `wild-semdiv-dollar-trailing-newline-pcre2` throughput | 42.3 ns | 51,580 ns | 80.8 ns | B |
| syntax `anc-m-dollar` throughput | 555,877 ns | 220,210 ns | 237,374 ns | `(?m)`, NOT this mechanism |
| utf8 `asr-dollar-ml` throughput | 40,734 ns | 2,422,814 ns | 49,864 ns | `(?m)` |

**There is no bench cell where a reverse-from-end search would win**: every
end-pinned start-unanchored cell is class B at the 24-42 ns floor
(x8,800 ahead of `jit`), and every other end-pinned cell is `^...$`. The
S-class cells are at 13-72 ns throughput (the capability validators and the
three utf8 `^`-anchored cells, 40-89 ns against `jit`'s 2.36 ms) except
`pwd-strength-chain` (221 ns) and the known `^(\s+)*$`-family catastrophes
(`evil-alt-nested` throughput 11.7 us and `trim-nested-star` short-search
10.2 ms, auto-caps), which are backtracking costs in a start-anchored VM
attempt that a reverse walk cannot touch. The two cells
slower than a peer (`anc-m-dollar`, x2.5 jit) are the `(?m)` class.

So the potential win at the BENCH today is **zero cells**. The potential win
for the idiom is the §4 block.

## 4. Cost, today (scratch tier, Linux)

`run_timing.sh` + `timedrv.c` + `mksubj.py`, min of 7 `rx_search` calls from
offset 0 over a deterministic 1 MiB prose-like subject (NOT the bench's
`t-1m`; no pinning, no governor control; the figure prices "what a linear
scan costs", with run-to-run spread on this box of a few percent). Verbatim
`timing_linux.txt`:

| pattern | class | end window | no-match subject | matching tail |
|---|---|---|---:|---:|
| `\d+$` | UL | none | 0.868 ns/B (910 us) | 0.864 (905 us) |
| `\w+$` | UL | none | 3.15 (3.30 ms) | 3.15 (3.30 ms) |
| `\s+$` | UL | none | 3.08 (3.23 ms) | 2.53 (2.65 ms) |
| `\s*$` | UL | none | 1.80 (1.89 ms) | 1.80 (1.89 ms) |
| `[a-z]+\.txt$` | UL | none | 3.19 (3.34 ms) | 3.26 (3.42 ms) |
| `.*\.txt$` | UL | none | 0.576 (604 us) | 0.230 (241 us) |
| `\.txt$` | B | 5 | 80 ns | 160 ns |
| `\.txt$ -fno-end-window` | B (denied) | none | 0.446 (468 us) | 0.444 (466 us) |
| `abc$` | B | 4 | 40 ns | — |
| `abc$ -fno-end-window` | B (denied) | none | 0.166 (174 us) | — |

Reading: the unbounded idioms cost 0.2-3.3 ns/B, i.e. 0.24-3.4 ms per MiB,
and a MATCHING subject costs within 2.5x of a non-matching one (the forward
pass cannot stop early; `.*\.txt$` is the extreme at 2.5x). The same shape bounded and clamped is
~10^4-10^5 faster. A reverse-from-end walk's cost on these rows is the
trailing run (4-8 bytes in this subject) plus one anchored forward run:
O(tens of ns), the same order as the bounded-window rows. It is a prediction
read off the machine's structure and the bounded-row twin, not a measured
hand-twin; the hand-twin is the first owed item if the trigger fires.

## 5. What would put it at rank (the trigger)

D77: build under measurement or not at all. This census finds the mechanism
sound, the swing large where the idiom exists, and **the idiom absent from
every population pcrec measures**. The row is filed with its trigger:

1. a bench cell — an `anc-tail` family in `syntax` or a new subbench
   (`\d+$`, `\s+$`, `\w+\z`, `[^/]+$`, `.*\.txt$`, each on a long subject
   with a matching tail and a non-matching one), at which point
   pcrec-vs-`jit` is the reading (PCRE2 does not window an unbounded
   end-anchored search either, so the expected swing is the same x10^4 the
   bounded window produced, in pcrec's favour); OR
2. a real-world pattern census naming the idiom at rank (a log-trim or path
   basename workload) — the bench's `wild-*` capability patterns are all
   `^...$` validators, which is why none appear.

Until then the cheaper open fold stays where D77 put it: the final-byte
skip reasoning about `\z` is moot for the bounded half (shipped) and
irrelevant to the whole-subject half (start-anchored).

## 6. Reproduction

`docs/dev/optloop/revend/CLAUDE.md` lists each file; the commands are in the
scripts' headers. In short, on a Linux box with a built tree:

    gcc -O1 -Ilib -Isrc -o revend_probe docs/dev/optloop/revend/revend_probe.c build/libpcrec.a
    FACTS_ALL=1 PCREC=build/pcrec PROBE=./revend_probe BENCH=<pcrec-bench> \
        CORPUS=<repo> OUT=out python3 docs/dev/optloop/revend/census.py
    python3 docs/dev/optloop/revend/analyze.py out/census_rows.tsv > summary.txt
    BENCH=<pcrec-bench> python3 docs/dev/optloop/revend/bench_cells.py out/census_rows.tsv
    python3 docs/dev/optloop/revend/mksubj.py subj && \
        PCREC=build/pcrec SUBJ=subj WORK=tw docs/dev/optloop/revend/run_timing.sh
