# The gratuitous-walk survey

**Lane `walksurvey`, 2026-10-09. SURVEY + MEASUREMENT ONLY: nothing under `src/` changes.**
Pin: main `5e23b90c` (abi 71), Linux dev box (Ryzen 7700X, gcc 15.2). pcrec-bench at
`76e13c1d`, read only. Instrument, populations, drivers and verbatim results:
`studies/walk_survey/` (its `CLAUDE.md`). Every count below comes from
`studies/walk_survey/analyze.py` over the committed raw rows.

Frank, 2026-10-09: *"do a survey of existing patterns and see if there is another class
where we are doing gratuitous walks besides the end anchored ones."*

A GRATUITOUS WALK (the brief's definition): the artifact touches bytes, or steps a machine
over bytes, or repeats a pass over bytes, that the answer does not need given facts known at
compile time. [OPT-REVEND]'s `\d+$` is the motivating case: today's artifact walks 1 MiB
forward and then the match backward; the answer needs the match alone.

## 0. Answers first

**Yes. One large class is unowned (K4, with its fixed-width sibling K3), one latent
quadratic cliff is unowned (K5), one wide but shallow class is unowned (K5m), and three of
the brief's candidates are refuted.** Ranked by bench impact
(§3):

1. **K4, the reverse pass re-deriving a start the forward scan already landed on.** This is
   the biggest unowned class (FINISHER).
   - On a token-shaped find-all (`\w+`, utf8 `.`, `\p{L}+`), every match starts where the
     start-byte skip loop stopped, yet RECOVER's `reverse-pass` row walks each match back to
     find that start.
   - Population: 176 of 343 bench patterns (51%) and 1,362 corpus patterns. On bench
     throughput cells, 85.7% of all reverse-pass bytes are landing starts.
   - Twin: an answer-identical hand-twin (start = landing) is **20-42% faster** on three
     bench throughput cells (two runs; 34-42% except one noisy `\w+` reading).
   - **K3**, the fixed-width sibling (start = end − w; Frank's own D156 point), is
     **36-37% faster** on a dense literal find-all.
   - Both are RECOVER-slot rows that know the start without walking (F1).
2. **K1 (end-pinned, [OPT-REVEND]) and K11 (the attempt scan, [OPT-ATTEMPT-SPLIT])** are
   real and already owned. This survey adds the byte view: K11 re-reads 2.15 B/B.
3. **K5m, find-all re-entry.** Each call re-reads its predecessor's lookahead, and a
   bounded-width pattern steps past a final state. It reaches the most patterns (62% bench,
   67% corpus) but is about one byte per call. Bench estimate 21.7 ms (upper), concentrated
   in dense utf8 cells. Unowned; BOONIES (F4).
4. **K12 (+ K7), the forward machine stepping where a rare inner landmark could be
   scanned.** 23 bench patterns (`loglines/ipv6`, `altwide/sfx-*`, `\S+@\S+`), est 15.8 ms.
   This is [ENG-TACTICS]' reverse-inner population, now measured (F3).
5. **K5, a LATENT QUADRATIC in the caseless required-run gate under find-all.**
   - The S4 two-stream arm restarts both `memchr` streams on every call. When one case
     variant is absent from the text (lowercase prose or logs), each call scans to the end.
   - `(?i)cat` on 1 MiB of lowercase text is **~200x** slower than `-fno-req-run-fold`
     (190-210 ms vs 0.95-1.02 ms); `(?i)error` on a lowercase log is **23-26x** slower.
   - The bench's subjects hide it (both variants occur), so its bench weight is small. 11
     bench and 61 corpus patterns carry the arm. A known-issues entry and a linear fix shape
     are F2.
6. **Refuted as populations:**
   - start-anchored reverse (K2: 0 cells; [OPT-5] STEP 2 covers it);
   - the match regime re-deriving a known start (K8: real, but microseconds on the bench's
     ≤ 5 KB match subjects);
   - the hybrid VM re-walking the DFA-proved span (K9: required for captures, 2.7% of its
     cells' loads).
   - K6, multi-stream pre-check scans, is real but `memchr`-cheap.
   - K10, VM backtracking, is the largest byte count and is the algorithm, not a pass.

The instrument counts every subject load of the compiled artifact by phase (§1). It was
validated before use (§2):
- the known gratuitous `\d+$`: 1,048,585 bytes against its REVEND twin's 8;
- tight cases: 4 and 1 bytes;
- two planted passes: each seen, at `n` extra;
- gcov: the skip count agrees exactly, and the forward count differs by its one end-view load;
- K4/K5's own measures: they drop to 0 under the twin or arm that removes the walk.

## 1. Method

### 1.1 The instrument: every subject load, by phase

`studies/walk_survey/wsdrv.c` + `wsbuild.py`. The artifact is compiled with
`-O0 -fsanitize=kernel-address --param asan-instrumentation-with-call-threshold=0
--param asan-stack=0 --param asan-globals=0`. With the call threshold at 0, gcc turns every
load into a call to `__asan_load{1,2,4,8,16,N}_noabort(addr)`. In the kernel flavour those
callbacks are the user's to define, so the driver defines them. A load whose address falls
inside the subject buffer is counted. The subject sits in its own exact-size allocation, so
nothing past its end counts. The libc scanners an artifact may call (`memchr`, `memrchr`,
`memcmp`, `memmem`) are interposed with `-fno-builtin-<fn>` on the artifact. Each counts the
bytes its own semantics must examine: `memchr` reads `[p, hit]`, or the whole range on a miss.

Each load is attributed to a PHASE through its call site:

- `wsbuild.py` finds every hook call site in the linked binary with `objdump`;
- `addr2line -i` names the emitted source line and the inline chain;
- `classify()` maps that to a phase using only identifiers the emitter writes.

| phase | what the emitted text says |
|---|---|
| `pre` | the search wrapper's pre-checks: presence `memchr`, `<p>_reqrun` |
| `skip` | candidate skipping ahead of a machine: `rx_can_begin_match`, start-byte tables, `memchr` in the forward search, `rx_ofsskip` |
| `fwd` | the forward DFA: `forward_*`, `scan_position`, computed-goto targets, seed states |
| `rev` | the reverse DFA: `reverse_*`, `rewind_position` |
| `anc` | the anchored match-here machine: `anchored_*` |
| `vm` | the VM: `rx_L` labels, span cursors, class atoms and bitmaps, backref compare |
| `endw` | the end-window clamp |
| `misc` | utf8 boundary bookkeeping: the K50 startpos guard, `next_pos`, `valid_upto`, `back_step`, `decode` |

A load inside a small non-inlined helper (`-O0`: `rx_w2`, `rx_forward_step`, ...) is
attributed through its CALLER: the helper's own sites map to `up`, and the hook uses
`__builtin_return_address(1)`. Every site and its phase is written to `sites.tsv`. Loads
through a site no rule claims are counted as `unk`: **50,872 of 1,579,887,968 bench loads
(0.003%)**.

Per subject and regime, the driver reports:
- `T`: loads, as bytes;
- `U`: unique bytes;
- per phase: `T_`, `U_`, the extent, and `A_` (bytes read PAST the call's match end, summed
  over calls);
- the pairwise phase overlaps;
- `land_rev`: the reverse bytes of calls whose match START is the first byte the forward
  machine stepped in that call;
- `m_gap` (`wsdrv5.c`): forward-machine bytes stepped before the call's match start.

The regimes are the bench's own:
- `search`: one `rx_search` from 0;
- `findall`: the bench's loop, which advances to the match end, or one character past an
  empty match;
- `match`: `rx_match_caps` at 0, whole-subject iff the length is `n`.

**Why this instrument.** The alternatives were a counter-twin per artifact (mktwin-style:
one hand transformer per emitted form, and the forms number in the dozens) and gcov line
counts (no per-call or per-byte view, and no attribution of a `memchr`). Load hooks are
sound by construction: every load the compiled artifact performs passes through one. They
are attributed from the artifact's own text, they need no per-form code, and they see
per-byte multiplicity.

The `-O0` choice: at `-O2` gcc merges a skip loop's last load with the forward step's first
load, which smears attribution between phases. At `-O0` every source-level load is its own
call. The one place this inflates a count is that the landing byte is read once by the skip
test and once by the first forward step (`K0` below). The analysis subtracts that byte and
does not count it as a walk.

### 1.2 Populations (every count from a committed script)

- **BENCH** (`pop_bench.py`): the cells are every `bench/<set>/patterns/*.rx` export ×
  every regime its `subbench.toml` declares × the subjects that regime sees (the loader's
  `subjects_for()` rule). The patterns are compiled the way the bench's `pcrec-auto` testee
  compiles them: `--features all`, plus `-e utf8` on the utf8 set. The subjects come from
  the set's own generators, run in a `git archive` copy.
  - Size: 367 patterns, 913 (pattern, regime) rows, 62,868 subject runs (default + nocaps).
  - Configs: `default` and `nocaps` (`--no-captures`), plus `anch` (`\A(?:P)`, the
    anchored-attempt reference) where the match regime runs.
- **CORPUS** (`pop_corpus.py`): every distinct pattern block of every shipped `.rxt`, with
  the block's own encoding and `i` flag. Subjects:
  - the block's own inline m/n subjects;
  - three synthesized 16 KiB subjects from a deterministic prose filler: `FILLER+M` (a match
    near the end), `M+FILLER` (a match at the start), `FILLER+N`.
  - Size: 4,563 pattern blocks (4,171 with a live default-config compile; 371 refused by pcrec, 20 failed the instrumented
  build), 160,377 rows.

The corpus run resumed after a stall on a ReDoS witness. It resumed with a 20M VM step
budget (`run_rest.sh`): the instrumented VM is about 50x slower, and the corpus's
exponential witnesses otherwise sit at the time limit. A give-up is a row like any other.

### 1.3 Lower bound, classes, impact

- **The lower bound.** The answer's own information, independent of pcrec:
  - an unanchored search must examine `[search_from, e)` on a match and the whole remainder
    on none;
  - an end-pinned one only the span and one byte;
  - a start-anchored one only `[0, e)`;
  - a find-all at least `n` (every byte once).
- **Each class** is a predicate on stamps, facts and phase columns, plus a gratuitous-byte
  count `G` (`analyze.py`'s docstring defines all of them). K1 subsumes the reverse and gate
  classes on the same cell. K9 (the capture finisher) and K10 (VM backtracking) are reported
  but not summed: K9 is required wherever captures are delivered, and K10 is the VM's
  algorithm, not a pass that a compile-time fact removes.
- **Impact.** `est_ns = (the bench's own set-grain pcrec median for the cell) × G/T`. The
  medians come from the newest report per set (capability@0.2 at `255bcdd8`; the 2026-10-05
  round-1 group at `c4c70f2c`; Ryzen 1600). Both pins are older than this survey's, so
  impact is a WEIGHT for ranking, not a prediction. The model assumes a uniform per-byte cost
  across phases. A `memchr` byte is roughly 30x cheaper than a DFA step, so the estimate is an
  upper estimate for the scan classes (K5-K7). The top unowned classes are therefore re-timed
  by answer-checked hand-twins (§4, §5); K1 and K11 carry their own rows' timings.

## 2. Instrument validation (`results/validation.txt`, `validate.sh`)

Validated on these cases with the FINAL instrument, the one that produced every number
quoted here. An earlier exploratory pass was re-run in full after the instrument's last
change: bench K1-K11 reproduce byte for byte between the two final bench passes.

| case | expectation | measured |
|---|---|---|
| 1 KNOWN GRATUITOUS: `\d+$`, 1 MiB prose + `" 12345"` | about `n` bytes against a 6-byte answer | `T` = 1,048,585, `U` = `n`; skip 1,048,572, fwd 6, rev 7 |
| 2 its [OPT-REVEND] form-C twin (`revend_twin/mktwin.py`, an independent transformer) | the match alone | `T` = 8 (rev 7 + the twin's seed test) |
| 3 KNOWN TIGHT: `^abc` on a 1 MiB subject beginning `abc` / not | about 3 / 1 | `T` = 4 / 1 |
| 3 `abc` with its one match at the end | the forward lower bound, by memchr | `U` = `n`−1, `T_scan` = `n`−2 |
| 4 PLANTED (failing direction): `^abc` plus one planted forward pass, and plus one planted reverse pass | `n` extra each, visible as an unclaimed site | `T` = 1,048,580, `unk` = 1,048,576, both |
| 5 INDEPENDENT COUNT: gcov line counts of `\d+$`'s artifact on case 1's subject | skip and forward counts equal | skip-loop line 1,048,572 = instrument skip 1,048,572; forward-step line 5 = instrument fwd 6 − the one end-view load |
| 6 CLASS MEASURES RESPOND: K4 on `\w+` (artifact vs the landing twin), K5 on `(?i)cat` over lowercase (fold vs `-fno-req-run-fold`) | the twin/arm reads 0 | `land_rev` 73,727 → 0, `T` 172,030 → 98,303; `A_pre` 97,624,809 → 0 |

## 3. The ranked class table

Ranked by BENCH IMPACT first. That is `est_ms`: the sum over the auto-caps testee's cells of
`median × G/T`, an upper estimate for scan classes. Corpus breadth is second. `G/n` is
gratuitous bytes per subject byte on the representative subjects. "twin" is the
answer-checked hand-twin timing of §5 (`results/twin_timing*.txt`, scratch tier: Ryzen
7700X, one core, a box at load1 11-12 from other lanes, best of 5, two runs).

| rank | class | D156 role | bench cells / patterns (auto-caps) | est_ms (upper) | representative G/n | twin | corpus patterns | owner row |
|---|---|---|---|---|---|---|---|---|
| 1 | **K4** reverse pass re-derives a start the forward scan LANDED on | finisher | 284 / 176 (51% of bench patterns) | 50.9 | utf8 `.` 1.00, `\w+` 1.16, `\p{L}+` 0.81 | **−20..−42%** (3 patterns, 2 runs) | 1,362 (32.7%) | **none**: RECOVER slot / D156 FINISH, F1 |
| 2 | K1 end-pinned walks the whole subject | locator | 23 / 12 | 30.9 | `t-tail-*` 1.03-1.31 | revend form C: 1,048,585 → 8 bytes | 142 (3.4%) | [OPT-REVEND] (D156) |
| 3 | K11 DFA attempt scan re-reads overlapping attempts | locator | 24 / 20 (one pattern carries it) | 24.9 | `942360-concat-sqli` 2.15 | the row's own: 8.83 vs re2 1.62 ns/B | 130 (3.1%) | [OPT-ATTEMPT-SPLIT] |
| 4 | K5m find-all re-entry re-reads the lookahead (K5mb: bounded-width final-state overstep) | locator | 213 / 213 (K5mb 154) | 21.7 (1 byte/call: upper) | utf8 `\B` 1.08, utf8 `.` 0.71 | not twinned | 2,807 (67.3%) | **none**: F4 (BOONIES) |
| 5 | **K12** the forward machine steps where a rare inner landmark could be scanned (with K7: a pre-check scanned the bytes first) | locator | K12 38 / 23 (static census 24); K7 161 / 92 | 15.8 (K12, excl. K1 overlap) + 6.1 (K7) | `loglines/ipv6` 0.64, `altwide/sfx-*` 0.79, `\S+@\S+` 1.12 | not twinned | K12 118 (static), K7 734 (17.6%) | [ENG-TACTICS] (D151 reverse-inner), F3 |
| 6 | K6 one call scans the same bytes once per stream | locator gate | 126 / 68 | 4.6 (memchr: upper) | `union-select` 1.12, `ci-ascii-control` 1.03 | — | 293 (7.0%) | [MEMFN] kernels |
| 7 | **K3** fixed-width reverse: start = end − w | finisher | 130 / 74 | 3.7 | `lit-l2` 0.28, `year4` 0.19 | **−36..−37%** (`abcd`) | 1,002 (24.0%) | D156 rule; [OPT-5-PERIODK] part; F1 |
| 8 | **K5** the caseless run gate restarts every find-all call: LATENT QUADRATIC | locator gate | 3 / 3 trigger; 11 at risk | 2.7 on the bench | `mod-i` 3.05 | **200x / 23-26x off-bench** | 32 trigger, 61 at risk | [OPT-LITSCAN] S4; F2 (known-issues) |
| — | K9 hybrid finisher re-walk | finisher | 82 / 55 | 2.7 | 0.1 | — | 1,140 | required for captures |
| — | K8 match regime re-derives a known start | locator | 20 / 20 | 0.01 | 0.98 on ≤ 5 KB | — | 393 | [ENG-ABS] fallback; no action |
| — | K2 start-anchored reverse | finisher | 0 | 0 | — | — | 0 | [OPT-5] STEP 2 (shipped) |
| — | K10 VM backtracking re-reads | both | 97 / 64 | 95.3 | backrefs 5-8 | — | 1,252 | algorithmic: not a gratuitous pass |

The verdicts on the brief's candidate list:
- CONFIRMED: K4 and K3 (the reverse pass where the start is already known), K5/K6/K7 (the
  pre-check family), K5m (find-all re-entry), K11, K12.
- REFUTED as a population today:
  - K2, start-anchored reverse: zero cells. [OPT-5] STEP 2's `pinned` start covers it.
  - K8, the match regime re-deriving a known start: real per cell, but on the bench's short
    subjects it is worth microseconds in total.
  - K9, the hybrid re-walking the DFA-proved span: required for captures, and 2.7% of the
    cells' loads.
- NOT GRATUITOUS: K10, the VM's backtracking re-reads. It is the largest byte count and the
  largest estimate, but it is the backtracking algorithm on backreference patterns.
  Recorded, not ranked.
- `(?:P)\z` whole-subject forms are K1 (end-pinned) or K8 (the match regime) instances, not
  a class of their own.

## 4. Per-class evidence

### K4: the reverse pass re-derives a start the forward scan landed on (FINISHER)

**What.** RECOVER's `reverse-pass` row walks every match back from its end, but the match
began at the first byte the forward machine stepped in that call: the start-byte skip loop's
landing. `wsdrv`'s per-call landing test counts it. For each call it records the lowest
offset the `fwd` phase touched; when that offset equals the reported start, the call's
reverse bytes are `land_rev`.

**Population.**
- Bench: 284 auto-caps cells (570 with nocaps), 176 patterns (`results/counts.txt`).
- Of the 199 throughput cells that run a reverse pass at all:
  - 79 land on EVERY match;
  - 96 land on at least 90% of matches;
  - 36 land on none.
- **85.7% of all reverse-pass bytes on throughput cells are landing-start bytes.**
- Corpus: 1,362 of 4,171 patterns (32.7%), on the synthesized subjects.

**Excess.** The dense token find-alls are the bulk:
- utf8 `.` (`cls-dot`): K4 1.00 B/B, T/LB 4.13;
- `\p{L}+`: 0.81, T/LB 2.30;
- `\w+` (`cls-w`, `mod-a`): 1.16, T/LB 2.76.

**Twin** (`landtwin.py`: record the skip loop's landing, delete the reverse block, start =
landing). Answer-identical (span checksum) on the bench's own throughput subjects:

| pattern | run 1: today → twin | run 2: today → twin | change |
|---|---|---|---|
| `\w+`, syntax `t-1m` | 3.02 → 2.43 ms | 3.54 → 2.16 ms | −20% / −39% (the noisiest cell) |
| utf8 `.`, utf8 `t-1m` | 8.14 → 5.36 ms | 7.95 → 5.17 ms | −34% / −35% |
| utf8 `\p{L}+`, utf8 `t-1m` | 5.46 → 3.32 ms | 5.49 → 3.18 ms | −39% / −42% |

**What makes it exact.**
- A landing `L` is the first candidate at or after `search_from`. If any match starts at
  `L`, the leftmost-first match starts at `L`, and the unanchored forward DFA's reported end
  is that match's end. So "a match starts at `L`" is the whole condition.
- Two sufficient forms:
  1. A COMPILE-TIME FACT: the anchored machine's state after any single start-set byte, in
     the landing's start view, is accepting. This holds for `C+`, `C`, `C{1,n}` and
     `C+D*`-shaped token patterns, and fails for literals and for a leading assertion.
  2. Without the fact, run the ANCHORED machine from `L` (the [ENG-ABS] match-here machine
     most artifacts already carry). If it accepts, the span is exact with no reverse pass.
     If it dies, continue unanchored from `L`+1. That costs an anchored attempt per false
     landing, so it is a selection question, not a free win.
- The 36 throughput cells with no landings show where form 2 would only cost.

**Owner.** No row. The slot is start_table.md's RECOVER ("given a match END, where does it
start?"), whose rows today are `reverse-pass` and `pinned`. In D156's frame it is a FINISH
choice: with the typed result "exact span" the finisher is nothing. Filing suggestion: §7 F1.

### K1: end-pinned patterns walk the whole subject (LOCATOR, known)

**Population.**
- Bench: 23 auto-caps cells, 12 patterns (start-anchored `^...$` excluded: one attempt at 0
  is already their locator). Five are the `t-tail-*` throughput cells at G/n 1.03-1.31:
  - `tail-word-eoz` 9.8 ms against a best of 394 ns;
  - `tail-ext-lower-txt` 8.8 ms;
  - `tail-space-eol` 7.9 ms;
  - `tail-digits-eol` 3.7 ms;
  - `tail-dotstar-txt` 0.86 ms.
- Corpus: 142 of 4,171 patterns (3.4%) with a measured excess (revend_census.md counts the end-pinned population itself).

**Owner.** [OPT-REVEND] (D156; `docs/design/revend.md` rev 2, form C). This survey adds
nothing to its design. Its twin, run through this instrument, is validation case 2:
1,048,585 → 8 bytes.

### K11: the DFA attempt scan re-reads overlapping attempts (LOCATOR)

**Population.**
- Bench: 24 auto-caps cells. One pattern carries the cost: `wild-waf-crs-942360-concat-sqli`
  (`^` on some branches, so `RX_DFA_SCAN "attempt"`). Its forward attempts re-read 2.15 B/B
  over the 4.6 MB throughput set: 36.5 ms against a best of 3.6 ms, and 1.94 B/B on its
  short-search cells.
- Corpus: 130 of 4,171 patterns (3.1%).

**Owner.** [OPT-ATTEMPT-SPLIT] (ratified 2026-09-22, not started; its row already names this
witness at 8.83 ns/B). This survey supplies the byte view: two of every three bytes the
attempt scan reads are re-reads.

### K5m (and K5mb): find-all re-entry re-reads the machine's lookahead (LOCATOR)

**What.** Each find-all call reads bytes past its match end, and the next call reads them
again, because the API is stateless:
- an unbounded pattern reads one byte to end the match (`\w+` sees the space);
- a BOUNDED-width pattern steps past a final state (K5mb: utf8 `.` reads the next lead
  byte);
- a lookbehind pattern re-reads its seed context byte before `search_from` (in the
  residual, §6).

**Population.**
- Bench: 213 auto-caps throughput cells, 2.3% of their loads; 154 patterns K5mb.
- Concentrated where matches are dense:
  - utf8 `\B` (`asr-b-midchar`, nullable: one call per position): 1.08 B/B, 12.7 ms against
    a best of 0.9 µs;
  - utf8 `.` and its siblings: 0.70-0.71 B/B.
- Corpus: 2,807 of 4,171 patterns (67.3%) on find-all, 1,750 of them K5mb.

**Owner.** None.
- The cross-call half needs caller-owned state: [OPT-HYB-RESEED-XCALL] is the existing
  caller-owned cross-call hint row, the nearest precedent.
- The final-state half is emission-local: test "this accepting state has no live
  transition" before stepping.
- Filing suggestion: §7 F4. The estimate is an upper one (one byte per call); measure before
  building.

### K7 and K12: the forward machine steps bytes a landmark scan already proved or could skip (LOCATOR)

**K7: a pre-check scanned the bytes, then the engine re-stepped them.** Bench: 161
auto-caps cells.
- `\S+@\S+` (`cls-s-uc`): the presence `memchr('@')` scans every gap, then the forward DFA
  steps the same gap, 0.97 B/B.
- `email/orig` and `email/factored`: 0.28.
- `bak-k-named`: 0.83.

**K12: the inner landmark.** `k12_census.py` lists the patterns with a necessary byte or run
at least 16x narrower than the start set, on the DFA route or a VM hybrid: 24 of 343 bench patterns and 118 of 4,191 corpus patterns (`results/k12_*.tsv`).
`m_gap` (`wsdrv5.c`) counts the forward machine's bytes stepped before each call's match
start. A reverse-inner walk would replace those steps with one `memchr` for the landmark.
Measured: 38 auto-caps bench cells on 23 patterns. Excluding the cells K1
already owns, the estimate is 15.8 ms. The top cells:

| cell | G/n | today | best other |
|---|---|---|---|
| `loglines/ipv6` throughput | 0.64 | 10.5 ms | 7.5 ms |
| `altwide/sfx-64` (a shared suffix) | 0.79 | 3.2 ms | 0.85 ms |
| `altwide/sfx-256` | 0.80 | 3.0 ms | 2.3 ms |
| `\S+@\S+` (`syntax/cls-s-uc`) | 1.12 (K7 0.97 on the same bytes) | 3.0 ms | 2.9 ms |

Corpus: the static census's 118 patterns. The corpus ran without `m_gap`, so its K12 is
counted statically and not measured.

**Owner.** [ENG-TACTICS] (D151's reverse-inner, re-scoped 2026-10-06 as one `handoff-rev`
row after the start-table fold; on the next [OPTLOOP] cycle's candidate list). The K82
HANDOFF (`RX_REQ_HANDOFF`) is the bounded case already shipped: it starts the body at
`c − K` when the run's offset is bounded. K7's cells are the unbounded remainder, where the
gate's work is still discarded.

### K6: one call scans the same bytes once per stream (LOCATOR gate)

**What.** The pre-check runs one `memchr` per case variant (the S4 pair arm) or per
required-set byte (`rq_set[]` presence), each over the same bytes.

**Population.**
- Bench: 126 auto-caps cells.
- `wild-waf-crs-942270-union-select`: 1.12 B/B (2.12 total, no match anywhere).
- `ci-ascii-control`: 1.03.
- `bak-k-named`: 0.85.
- Corpus: 293 of 4,171 patterns (7.0%).

**Cost.** `memchr` bytes: a fraction of a DFA step each. The est_ms of 4.6 is an upper
bound.

**Owner.** [MEMFN]: a `memchr2`/`memchr3`-shaped kernel is one pass. K85 is the same
family's per-call term.

### K5: the folded-run gate restarts every find-all call, a LATENT QUADRATIC (LOCATOR gate)

**What.** `litscan_s4.md` §2.3.4's two-stream arm (a caseless required run, e.g.
`RX_REQ_RUN "434154@0/dfdfdf"` for `(?i)cat`) works as follows:
- it keeps one pending hit per case variant (`ha`, `hb`);
- it starts every call with `fresh = 1`, so both streams are searched from `search_from`.

When one variant is ABSENT from the text (the uppercase one in lowercase prose or logs), its
`memchr` runs to `n` on EVERY call. A find-all is then `O(n × matches)`.

**Bench.** Three cells (`mod-i`, `mod-r`, `ci-strasse`), G/n up to 3.05. On the bench's own
subjects both variants occur often enough that the fold still wins: `(?i)cat` on syntax
`t-1m` takes 552 / 542 µs against 741 / 695 µs with `-fno-req-run-fold`.

**Off the bench** (`run_twins.sh`, answer-identical):

| pattern, subject | fold (today) | `-fno-req-run-fold` | ratio |
|---|---|---|---|
| `(?i)cat`, 1 MiB lowercase (47,663 matches) | 190 / 210 ms | 0.95 / 1.02 ms | 200x / 206x |
| `(?i)error`, a 1 MiB lowercase log (3,038 matches) | 12.5 / 13.5 ms | 0.48 / 0.60 ms | 26x / 23x |

**Population.** Every caseless required run on the pair arm: 11 of 343 bench patterns (three trigger on the bench's own subjects), 61 of 4,171 corpus patterns (32 trigger on the synthesized subjects).

**Owner.** [OPT-LITSCAN] S4 (C3). K82 (closed) fixed C3's measured regressions through the
handoff, but this is a different mechanism that the bench's subjects do not trigger.
Filing suggestion: §7 F2 (a known-issues entry with a fix shape).

### K3: a fixed-width pattern's start follows from its end (FINISHER)

**Population.**
- Bench: 130 auto-caps cells, 74 patterns. G/n up to 0.30 on dense literal find-alls
  (`litrun lit-l2..l8`, `year4`).
- Corpus: 1,002 of 4,171 patterns (24.0%).

**Twin** (`landtwin.py --fixed 4`, start = end − 4): `abcd` find-all on `litrun mat-l4`
goes 342 → 215 µs and 335 → 214 µs in the two runs (−36..−37%), answer-identical.

**Owner.** D156 states the rule: "A fixed-width pattern's span is fully determined by the
end". [OPT-5-PERIODK] carries the counted-repeat special case ("multi-edge reverse-pass
elision, start = end − SUM(count_i)"). No row carries the general one. Filing suggestion:
§7 F1, as K4's sibling RECOVER row.

### Small or refuted

| class | measured | disposition |
|---|---|---|
| K2 start-anchored reverse | 0 bench cells; 0 in the corpus | [OPT-5] STEP 2's `pinned` start covers it |
| K8 match-regime overread | 20 auto-caps cells: 7 `search-filter` DFA `_match`es and VM routes scan for a start the anchored question does not need, G/n up to 0.98. The bench's match subjects are ≤ 5 KB, so est 0.01 ms. Corpus: 393 of 4,171 patterns (9.4%) | the size-cap fallback [ENG-ABS] already documents; no action until a long-subject match cell exists |
| K9 hybrid finisher re-walk | 82 auto-caps cells, 2.7% of their loads | required for captures |
| K10 VM re-reads | 97 auto-caps cells, the largest bytes: the backreference family (`bak-*`, `doubled-word`, `mod-j-uc`) at T/LB 7-10 | the backtracking algorithm, not a pass a fact removes; recorded |

## 5. The twins (`results/twin_timing.txt`, `results/twin_timing_run2.txt`)

Scratch tier:
- Ryzen 7700X, `taskset` to one core;
- other lanes loading the box (load1 11-12 at the start of each run);
- best of 5 (best of 3 for K5), three interleaved repeats per run, two runs eleven minutes
  apart.

Every line carries a span checksum, and each twin's checksum equals its artifact's on every
line. The tables quote each run's best repeat. The `\w+` cell's two readings (−20% / −39%)
show the box's noise: quote the range, not a point.

## 6. The residual: what no class explains

The top residual cells (`results/summary.txt`) are:
- **bench**:
  - `utf8/asr-lb-class` (`(?<=[\x{400}-\x{4FF}])\s`, `misc` 2.06 B/B): the VM lookbehind
    decodes each candidate's previous character, plus the utf8 start-scan's continuation
    skips;
  - the backreference family's VM start scan (`skip` ~0.97 B/B, which the find-all lower
    bound already counts once).
- **corpus**: dense-match find-alls of lookbehind-context patterns (`(?<!\s) *[a-z]`,
  `\W*(?<!\W)\w`) at ~2.3 forward loads per byte. Per call they read the lookbehind seed byte
  before `search_from`, the match, and one byte past it: K5m's re-entry family on its other
  side.

The residual holds no further class. Its top cells are the VM's own lookbehind decoding and
the re-entry family above, and below them it falls under 1 B/B.

## 7. Filing suggestions (SUGGESTIONS ONLY: no plan, decision or known-issues edit here)

- **F1. ONE row: RECOVER entries that know the start without walking (K4 and K3).**
  - `landing`: start = the forward scan's landing, admitted by the compile-time fact "every
    start-set byte, in its start view, takes the anchored machine to an accepting state".
  - `end-minus-width`: start = end − w for a fixed-width pattern.
  - Both are first-match rows in `dfa_search_starts[]` ahead of `reverse-pass`, both are
    exact, and both hand START to the CALLER. They are siblings, which is why they are filed
    as one row and not as two special cases (memory `pcrec-forest-for-trees`).
  - The non-fact form of `landing` (an anchored attempt at each landing) is a selection
    question, to measure separately.
  - The locate × finish design lane D156 charters is the natural owner.
  - Measured: −20..−42% on the token find-alls (−36..−37% for `end-minus-width`), and 85.7%
    of reverse bytes on bench throughput cells.
- **F2. A known-issues entry for K5** (performance cliff, no wrong answer):
  - Repro: `(?i)cat` / `(?i)error` find-all on lowercase text, ~200x / 23-26x against
    `-fno-req-run-fold`.
  - Fix shape (unmeasured): bound each stream's search by the other stream's pending hit,
    `memchr(B)` over `[pos, ha)` only, and treat "not found before `ha`" as "no B hit before
    the candidate". Each call's scans then end at the next candidate, and a find-all is
    linear again.
  - Owner [OPT-LITSCAN] S4. Its sabotage witness is the lowercase find-all above, bounded
    by a watchdog.
- **F3. K7/K12's population to [ENG-TACTICS].** The census list (`results/k12_*.tsv`'s k12=1
  rows) and the bench `m_gap` cells as the row's measured population. No new row.
- **F4. A BOONIES-tier row for K5m.** Find-all re-entry state and the final-state overstep.
  Trigger: a bench cell where re-entry exceeds 10% of the cell time. Today the top cell is
  `asr-b-midchar` at an UPPER estimate of 37%.
- **Not filed:**
  - K11: [OPT-ATTEMPT-SPLIT] exists; this survey's number goes to it.
  - K1: [OPT-REVEND].
  - K6: [MEMFN] kernels.
  - K8, K9, K10, K2: §4.

## 8. Limits

- **Source-level loads at `-O0`.** gcc `-O2` may keep a byte in a register. K0, the one such
  case found, is subtracted.
- **Scanner interposers count semantic bytes.** glibc `memchr` reads aligned blocks: more
  bytes, at about 1/30 the cost each. The per-phase byte counts are a WALK measure, not a
  time measure. Times come from the twins.
- **Impact is a weight.** It uses older-pin medians from another machine and a uniform
  per-byte cost. K4 leads the next class by 1.6x, and the twins confirm it independently of
  the weight. Below K4 the classes sit within a factor of 2.5 of each other (K1 30.9, K11
  24.9, K5m 21.7, K12 15.8), so read that order as soft.
- **The corpus's synthesized subjects** (16 KiB of prose around the block's own subject)
  measure breadth, not cost. The corpus's G/n are not bench numbers.
- **The corpus resume** ran the patterns after the first ~1,800 (in population order) with a
  20M VM step budget. The first ~1,800 ran at the default 500M.
- **The phase classifier** reads emitted identifiers. A future emitter rename shows up as
  `unk` loads, counted and reported (0.003% bench, 0.09% corpus), never silently
  misattributed.

## 9. Reproduction

```
PCREC=$PWD/build/pcrec PROBE=<revend_probe built against build/libpcrec.a> \
  BENCHCOPY=<git archive of pcrec-bench with its generators run> studies/walk_survey/run_all.sh
studies/walk_survey/run_rest.sh                        # the corpus resume + bench under wsdrv5
python3 studies/walk_survey/k12_census.py build/pcrec work/pop_bench.tsv  > work/k12_bench.tsv
python3 studies/walk_survey/k12_census.py build/pcrec work/pop_corpus.tsv > work/k12_corpus.tsv
python3 studies/walk_survey/analyze.py work/res_bench5.tsv work/res_corpus.tsv work/bench_times.tsv OUT \
  work/k12_bench.tsv work/k12_corpus.tsv
PCREC=build/pcrec ./studies/walk_survey/validate.sh
PCREC=build/pcrec BENCHCOPY=... ./studies/walk_survey/run_twins.sh
```


