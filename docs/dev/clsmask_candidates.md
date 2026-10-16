# Class-mask candidates for [VM-CLSMASK]

**Lane `clscand`, 2026-10-16. MEASUREMENT ONLY: nothing under `src/`, `cli/`, `lib/` or
`tests/` changes.** Pin: main `353249282` (abi 78), Linux dev box (Ryzen 7700X, gcc 15.2),
CPUs 0-3 only. pcrec-bench `25480b47`, read only (a `git archive` copy with its subject
generators run in the copy). The [REGIME-CORPUS] cache is `worktrees/.corpus`. Instrument,
populations, scripts and verbatim results are in `docs/dev/clsmask_candidates/` (see its
`CLAUDE.md`). No timing is reported anywhere. Every count is a count of tests the emitted
code makes.

Frank asked, before any design: *find the best candidate patterns for [VM-CLSMASK]*, the
VM reading precomputed per-class truth vectors instead of testing bytes. Context:
plan.md [VM-CLSMASK] / [POS-PARALLEL] / [SPAN-ISEL], memfn/docs/ideas.md 2026-10-11, and
docs/dev/walk_survey.md.

## 0. Answers first

1. **The best candidates are `\w`-token patterns that the VM runs with its own attempt
   loop.** Examples: `(\w+) \1`, `\b\w+(?=,\s+and\b)`, `\b(\w+)\s+\1\b`, `\w+\z`. Second
   come line-length and negated-class runs (`(?m)^.{400,}$`,
   `(?m)^(?!.*\bINFO\b).*$`), then dense hex/digit token spans (`loglines/ipv6`, `uuid`,
   `hex32`, the digit ladders).
   - The `\w` family has all three of the row's levers at once:
     - an EXPENSIVE class: the 63-byte `\w` set, emitted as a 32-byte bitmap table load
       plus shift and mask;
     - RUNS: 30-82% of its tests are span-loop tests (82% for `(\w+) \1`), i.e.
       future `ctz(~mask)` sites;
     - RE-VISITS: a re-visit factor of 2.7-4.5, because each attempt inside a word
       re-runs `\w+` to the word's end.
   - The VM touches 87-94% of the positions in every 64-byte block it touches, so a
     whole-block classify is nearly fully used (Frank's BATCHING point).
   - The start set is that same `\w` class, so one classify also drives the attempt
     loop's skip (Frank's AMORTIZATION point).
   - Several of these patterns are VM-routed under `auto` (backrefs, lookaround), with no
     prefilter. So these are cells a user gets today, not only forced-VM cells (§4).
2. **ipv4 `(\d{1,3}\.){3}\d{1,3}` is a GOOD ILLUSTRATION and a MEDIOCRE CANDIDATE.**
   - Under `auto` (the artifact a user gets) it is no VM-CLSMASK candidate at all. The
     hybrid prefilter hands the VM exact windows, and the VM makes **0.011 class tests per
     subject byte** with a re-visit factor of 1.14. Its cost is the DFA locate, which is
     [SPAN-ISEL]'s locator question, not this row's.
   - Under `--engine=vm` it ranks **83rd of 475** real, non-rescan artifacts, with score
     645 against the leaders' ~4,400.
     - Its strongest term is the attempt loop's start skip: 0.99 `\d` tests per byte,
       start set = the program's own `\d` class. That is Frank's amortization case in its
       purest form.
     - Its program tests are 0.73/B (1.13/B on apache logs), with re-visit 3.5. Coverage
       is only 0.37 on mixed text: digits are sparse, so a classified block is a third
       used.
     - One structural note (§5): only 1 of its 4 `\d{1,3}` run sites is possessified.
       The three inside the `{3}` group keep giveback frames even though `\d` and `\.`
       are disjoint, which is where most of its re-visits come from.
3. **Recommended timing candidates** (§6), five shapes:
   - `(\w+) \1`: expensive class, run, attempt overlap. Auto = VM.
   - `(?m)^(?!.*\bINFO\b).*$`: a lookahead re-walk of every line, nullable start, no
     start mask. Auto = VM.
   - `(?m)^.{400,}$`: a pure long run over a 255-byte class, the `ctz` showcase. Forced
     VM.
   - `loglines/ipv6`: 16 hex runs and dense re-visits. Forced VM; also a [SPAN-ISEL]
     locator cell.
   - ipv4 itself: the reference row Frank named. Forced VM only.
4. **Population facts that shape the design** (§2):
   - On real patterns under forced VM, the ATTEMPT LOOP's start skip makes MORE class
     tests than the whole VM program: 0.48 vs 0.33 tests per subject byte. Under auto it
     is 0.10 vs 0.31.
   - Of the program's tests on real auto-VM patterns, 68% are on 17-64-byte classes
     (`\w`-like bitmaps) and 59% on run sites.
   - utf8 code-point classes never reach a run site. Every one is a decode + class call
     per character, so a utf8 mask needs a different stage 1 (as [POS-PARALLEL] already
     says).
   - The quadratic re-scan patterns (re-visit ≥ 8: `\S+@\S+`, `.*\.txt$`, csv5, …) would
     top any raw ranking. They are ranked apart (§4.3) because a mask only makes the same
     quadratic cheaper per byte.

## 1. Method

### 1.1 What is measured, and from what

Everything is read from the compiler's own output: the emitted C, `--emit-ir`,
`--emit-facts` and the stamps. Nothing is re-derived from pattern text.

- **Sites.** `instrument.py` finds every VM BYTE TEST in the emitted `rx_match_anchored`
  (the VM program) and in `rx_search_run` (the attempt loop). A site is one occurrence of
  one of the emitted predicate forms. Each form was enumerated from all 4,883 forced-VM
  artifacts before the instrument was written:

  | form | emitted text | example |
  |---|---|---|
  | bitmap | `((rx_class_bitmapK[(subject[E]) >> 3] >> ((subject[E]) & 7)) & 1)` | `\w`, `[^,\n]` |
  | range | `((unsigned)(subject[E] - L) <= Wu)` | `\d`, `[a-z]` |
  | fold | `((subject[E] \| 0x20) == V)` | caseless letter |
  | eq / le | `subject[E] == V`, `subject[E] <= V` | literal byte |
  | atom | `rx_class_atomK(subject[E])` | the shared atom table |
  | switch | `switch (subject[E]) { case … }` | alternation dispatch |
  | start | `rx_start_set[subject[E]]` | the attempt loop's skip |
  | ucls | `rx_wclsK(cp_)` after `rx_decode` | a utf8 code-point class |

  Each site's KIND comes from its emitted line:
  - `run_c` / `run_u`: a counted or unbounded span-loop `while`;
  - `step`: a consuming single test;
  - `cstep`: a cursor-rung iteration test;
  - `peek`: lookahead, a guard, or dispatch;
  - `behind`: a read left of the position, as in lookbehind or `\b`'s left half;
  - `start`.

  Literal-run word compares (`rx_wN`/`memcmp`) and backreference compares are not class
  tests. They are counted statically, not instrumented. An audit counts every
  `subject[` read the instrument did not wrap: **0 in every artifact**.
- **Classes.** `ev.c` is the unmodified artifact plus an evaluator. It runs each site's
  own predicate text, with the subject read replaced by the byte, over all 256 bytes. For
  utf8 classes it runs over all 1,114,112 code points. Sites whose accepted sets are equal
  form one class. The artifact's own tables and helpers decide membership.
- **Counts.** `inst.c` wraps the first subject read of each predicate as
  `RXCS(site, pos)`. It also counts attempts (`rx_match_anchored` entries) and `rx_fail`
  arrivals (backtracks and failed attempts). `cs_drv.c` runs the bench's find-all loop,
  or one search for short subjects, at `-O1`. It reports per class the tests `T`, the
  unique positions `U` and the distinct 64-byte blocks `B`, plus U/B over the union of
  program classes. The start skip is kept as its own class.
- **Possessify** (b) is the IR listing's `strategies` row for the run site's label
  (`POSSESSIFIED`), plus the `RX_VM_STRATS` stamp and the IR summary's `possessify m/n`.
- **Start set** (e) is the `start_set` fact. `shared = yes` when it equals the OR of the
  program classes that are subsets of it, i.e. one classify of the program's own classes
  also yields the start mask. `part` means some program class is a subset but the OR
  falls short.

### 1.2 Populations (K35: who counts what)

| population | built by | what | count |
|---|---|---|---|
| corpus | `studies/walk_survey/pop_corpus.py` (reused verbatim) | every distinct `.rxt` pattern block, own encoding and `i` flag, its m/n subjects + three 16 KiB synthesized subjects | 4,816 keys |
| bench | `studies/walk_survey/pop_bench.py` | every `bench/<set>/patterns/*.rx`, the loader's `search_short` + `throughput` subjects | 344 keys |
| rw | `pop_rw.py` | every rwquest question (177) over a 256 KiB head sample of its first corpus file | 177 questions, 173 keys (4 duplicate patterns); 5 keys REFUSED by pcrec |
| ref | `pop_ref.py` | ipv4 `(\d{1,3}\.){3}\d{1,3}` (not carried verbatim elsewhere; `bounded/dotted4` is its non-capturing twin) over loglines throughput + rw L02/L03 | 1 key |

Notes on the populations:
- A key is (encoding, `i`, extra args, pattern). The 5,283 distinct keys include
  overlaps; a key in two sources counts in both.
- `compile_pop.py` compiles each key twice, `auto` and `--engine=vm`, both with
  `--features all`:
  - **auto:** 2,199 VM-routed (2,682 DFA, 402 refused);
  - **vm:** 4,883 VM-routed (400 refused).
- `run_pop.py` instruments every VM-routed artifact:
  - 20 per config fail to BUILD. All 20 are `tests/vars/*` artifacts, whose `rx_search`
    takes the module's variable arguments, which the driver does not speak.
  - That leaves 2,179 auto and 4,863 vm artifacts, with 0 timeouts and 0 abnormal exits
    over every subject run.
- **REAL** = a key carried by bench, rw or ref (whatever else carries it): 118 auto,
  490 vm. Of these, 1 / 15 are RESCAN (below), leaving 117 auto and 475 vm ranked.
- Subjects:
  - The **PANEL** is the same for every artifact, so rates compare across patterns: 64
    KiB from each of six [REGIME-CORPUS] files (apache access log, linux syslog, C
    source, Austen prose, python docs HTML, USGS CSV), taken 1 MiB in when the file is
    larger than 2 MiB.
  - The **OWN** subjects are the pattern's population subjects. Every subject is read up
    to 256 KiB.

### 1.3 The score (explicit; built from (b), (c), (e) only)

Per KiB of panel subject:

- **R** = tests at run sites. Each becomes a bit read, or part of one `ctz(~mask)`
  advance.
- **V** = `T_prog − U_any`, the re-visits that a cached mask answers.
- **A** = start-skip tests if `shared = yes`, else 0. A `ctz` over the start mask replaces
  the skip loop with no extra classify.
- **serv** = min(R + V, T_prog) + A. R and V can count one test twice.
- **score** = serv × cov, where **cov** = `U_any / (64 × B_any)`, the fraction of each
  touched block the program actually tests. It discounts patterns whose whole-block
  classify would be mostly wasted.

(d), the expensive class forms, is shown beside the score and NOT folded into it. A
`\w` bitmap test costs more than a range test, which strengthens the `\w` family's lead.
Pricing that is a timing question.

**RESCAN.** An artifact whose panel re-visit factor is ≥ 8 is ranked apart. Its attempt
loop re-reads a whole tail per start (quadratic), and that is owned by the walk rows
([OPT-REVEND], [OPT-ATTEMPT-SPLIT], walk_survey K10/K11). Counts: 131 vm / 50 auto
artifacts, almost all D27 adversarial corpus patterns.

## 2. The population, in tests

Source: `results/census.txt`, panel subjects, every artifact of the slice summed.

| slice | artifacts | program tests / B | start-skip tests / B | by form | by kind | by class size |
|---|---|---|---|---|---|---|
| vm, REAL non-RESCAN | 475 | 0.328 | **0.482** | bitmap 42%, range 23%, eq 13%, switch 11%, ucls 7% | run 50% (u 28, c 22), step 21%, peek 18%, behind 10% | 17-64: 52%, 3-16: 16%, 1: 13% |
| auto, REAL non-RESCAN | 117 | 0.305 | 0.105 | **bitmap 76%**, eq 14%, range 6%, ucls 3% | **run 59%**, step 24% | **17-64: 68%** |
| vm, all non-RESCAN | 4,732 | 0.500 | 0.572 | bitmap 47%, eq 36%, range 8% | step 30%, run 35% | 1: 36%, 17-64: 38% |
| vm, all (with RESCAN) | 4,863 | 11.39 | 0.570 | — | — | — |

Reading the table:
- **The start skip.** Under forced VM it is the single largest class-test consumer on
  real patterns, more than the program itself. On 277 of 475 real artifacts the start
  set equals an OR of program classes (`shared = yes`). Frank's "one classify serves
  both" is therefore the common case, not a special one.
- **The VM's run sites.** 3,377 statically (vm). The IR possessifies **47.5%** of them
  (40.4% under auto). The `RX_VM_STRATS` stamps over the vm artifacts read 0x0 2,284,
  0x2 1,304, 0x1 1,115, 0x3 180.
- **The re-scans.** The plain sum (11.4 tests/B) is 23× the non-RESCAN sum: the 131
  quadratic artifacts carry 96% of all program tests. Any unsliced ranking reads them,
  not the row's population.
- **utf8 classes** (`ucls`): 508 static sites, every one a `step`, none a run. Real utf8
  VM work under auto is small: 6 real auto artifacts carry a ucls site, the busiest at
  0.42 tests/B on its own text.

## 3. Instrument validation (`results/validation.txt`, VERDICT PASS)

1. **Known answers, hand-counted from the emitted program.** Both match exactly.
   - `\d+` on `ab12cd345`: start skip T=6 U=6, program T=6 U=6, attempts 2.
   - `x` on `yyxy`: the memchr pre-check, then start T=3, program T=1, attempts 1.
2. **Independent cross-check.** 40 sampled forced-VM byte-domain artifacts (no literal-run
   or backref compares, no utf8 sites) × 3 panel texts = 120 cells.
   - walk_survey's load instrument (`studies/walk_survey/`) compiles the SAME artifact
     text at `-O0` with a compiler-inserted hook on every load and attributes loads to
     phases by call site. It shares nothing with this source rewrite.
   - Its `vm`-phase load count must equal Σ over program sites of T × reads(form), with
     bitmap = 2 reads and the rest 1.
   - **0 mismatches**, on counts from 0 to 920,526.
3. **Failing-direction control.** `CS_SABOTAGE=drop-range` makes the instrument blind to
   the `range` form.
   - The same cross-check reports mismatches on **4 of 4** sampled artifacts whose range
     sites were evaluated in the intact run.
   - A range site that the panel never reaches moves nothing, so it is no witness. The
     first draft of this control counted such sites and read 1/2. That is recorded as the
     reason for the "evaluated" condition.
   - The unwrapped-read audit also fires on the sabotaged build, a second detector.

## 4. The ranked candidates

Column guide:
- **tests/B**: program class tests per panel byte.
- **re-visit**: T/U.
- **cov**: fraction of touched blocks' positions tested.
- **start skip/B**: the attempt loop's skip tests per byte.
- **R, V, A**: per KiB (§1.3).
- **own**: tests/B and score on the pattern's own subjects.
- **att, fails / KiB**: today's VM cost as context, not timing.
- **classes** is `setsize x sites`: `63` is `\w`, `255`/`254` are `.`/`[^x]`, `16` is
  hex, `10` is `\d`.

### 4.1 Forced VM (`--engine=vm`), REAL populations, RESCAN excluded (`results/top_vm_real.tsv`)

| # | pattern | source | classes (size x sites) | runs (poss) | tests/B | re-visit | cov | start skip/B | start set, shared | exp | R | V | A | **score** | own tests/B, score | att, fails /KiB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `(?J)(?:(?<w>the)\|(?<w>\w+)) \k<w>` | syntax/mod-j-uc | 63x1,1x1 | 1 (1) | 3.95 | 4.511 | 0.875 | 0.9937 | 63, yes | big+bitmap | 3322 | 3148 | 1018 | **4432** | 3.5426, 4356 | 720, 1438 |
| 2 | `(?P<t>\w+) (?P=t)` | syntax/bak-py | 63x1,1x1 | 1 (1) | 3.9478 | 4.509 | 0.875 | 0.9937 | 63, yes | big+bitmap | 3322 | 3146 | 1018 | **4430** | 3.5381, 4353 | 720, 718 |
| 3 | `(\w+) \1` | syntax/bak-1 | 63x1,1x1 | 1 (1) | 3.9478 | 4.509 | 0.875 | 0.9937 | 63, yes | big+bitmap | 3322 | 3146 | 1018 | **4430** | 3.5381, 4353 | 720, 718 |
| 4 | `(\w+) \g{-1}` | syntax/bak-g-rel | 63x1,1x1 | 1 (1) | 3.9478 | 4.509 | 0.875 | 0.9937 | 63, yes | big+bitmap | 3322 | 3146 | 1018 | **4430** | 3.5381, 4353 | 720, 718 |
| 5 | `(?m)^(?!.*\bINFO\b).*$` | rw/L24 | 63x4,1x2,255x2 | 2 (0) | 4.0386 | 4.039 | 0.999 | 0.0 | nullable, ? | big+bitmap | 2048 | 3112 | 0 | **4133** | 3.9338, 4028 | 26, 1050 |
| 6 | `\w+\z` | capability/tail-word-eoz | 63x1 | 1 (1) | 3.2594 | 3.707 | 0.879 | 1.0 | 63, yes | big+bitmap | 3338 | 2437 | 1024 | **3834** | 90.4519, 90679 | 724, 724 |
| 7 | `\b\w+(?=,\s+and\b)` | rw/P13 | 63x5,1x1,6x1 | 2 (0) | 3.0239 | 3.237 | 0.934 | 0.9982 | 63, yes | big+bitmap | 928 | 2140 | 1022 | **3820** | 3.1481, 4095 | 723, 1450 |
| 8 | `\b(\w+)\b\s+\1\b` | tests/possessify/possessify.rxt:… | 63x7,6x1 | 2 (2) | 2.8837 | 3.068 | 0.94 | 0.998 | 63, yes | big+bitmap | 1155 | 1990 | 1022 | **3735** | 2.8761, 3847 | 723, 722 |
| 9 | `\b(\w+)\s+\1\b` | rw/L18 | 63x5,6x1 | 2 (2) | 2.541 | 2.703 | 0.94 | 0.998 | 63, yes | big+bitmap | 1155 | 1639 | 1022 | **3406** | 2.6617, 3558 | 723, 722 |
| 10 | `(?m)^.{400,}$` | rw/L27 | 1x2,255x1 | 1 (0) | 1.9036 | 1.904 | 0.999 | 0.9174 | 255, yes | big+bitmap | 1023 | 925 | 939 | **2886** | 1.9934, 3061 | 926, 926 |
| 11 | `\b\w+ly\b` | rw/P07 | 63x5,1x1,1x1 | 1 (0) | 1.8766 | 3.238 | 0.904 | 0.6365 | 63, yes | big+bitmap | 556 | 1328 | 652 | **2292** | 3.2617, 4247 | 449, 898 |
| 12 | `(?m)^.{121,}$` | rw/C27 | 1x2,255x1 | 1 (0) | 1.5067 | 1.507 | 0.999 | 0.5186 | 255, yes | big+bitmap | 1023 | 519 | 531 | **2072** | 1.9558, 3019 | 518, 515 |
| 13 | `[a-z]{4096,}` | bounded/cls-atleast-4096 | 26x1 | 1 (1) | 2.1376 | 3.47 | 0.623 | 1.0 | 26, yes | - | 2189 | 1558 | 1024 | **2001** | 1.5428, 1773 | 510, 510 |
| 14 | `(?:(?:[0-9a-f]{1,4}:){4,7}[0-9a-f]{1,4}\|(?:[0…` | loglines/ipv6 | 16x16,1x15 | 16 (2) | 2.8123 | 5.717 | 0.497 | 1.0 | 16, yes | bitmap | 1770 | 2376 | 1024 | **1940** | 4.6734, 3755 | 309, 1690 |
| 15 | `\b(?:[a-z]+\.)+[A-Z]\w*(?:Exception\|Error)\b` | rw/L10 | 63x5,26x2,1x2,26x1,1x… | 3 (0) | 1.878 | 2.839 | 0.669 | 1.0 | 26, yes | big+bitmap | 508 | 1246 | 1024 | **1858** | 2.5779, 2237 | 510, 900 |
| 16 | `\b[A-Za-z]+(?:-[A-Za-z]+)+\b` | rw/P14 | 63x4,52x3,1x2 | 3 (3) | 1.6443 | 2.51 | 0.732 | 0.8763 | 52, yes | big+bitmap | 590 | 1013 | 897 | **1831** | 2.4209, 3204 | 493, 493 |
| 17 | `"([^"\\]+)"\s*:\s*` | capability/codegrammar-flat | 1x2,6x2,254x1,1x1 | 3 (3) | 0.7214 | 1.098 | 0.998 | 0.6661 | 1, yes | big+bitmap | 692 | 66 | 682 | **1418** | 0.3912, 793 | 16, 16 |
| 18 | `(?x)\n  "                     # opening quote\…` | capability/codegrammar-xflag | 1x2,6x2,254x1,1x1 | 3 (3) | 0.7214 | 1.098 | 0.998 | 0.6661 | 1, yes | big+bitmap | 692 | 66 | 682 | **1418** | 0.3912, 793 | 16, 16 |
| 19 | `(?m)\w-\r?$` | rw/P27 | 63x1,1x1,1x1,1x1 | 1 (0) | 1.4283 | 1.623 | 0.88 | 1.0 | 63, yes | big+bitmap | 7 | 561 | 1024 | **1401** | 1.5059, 1500 | 724, 731 |
| 20 | `(?m)\w-$` | rw/P19 | 63x1,1x1,1x1 | 0 (0) | 1.4215 | 1.615 | 0.88 | 1.0 | 63, yes | big+bitmap | 0 | 555 | 1024 | **1389** | 1.5041, 1496 | 724, 724 |

The 20 rows group into four families:
- the **`\w` / letter token** (rows 1-4, 6-9, 11, 15-16, 19-20): a 63-byte bitmap class,
  start shared, re-visit 1.6-4.5, coverage 0.67-0.94;
- **line runs** over `.` (rows 5, 10, 12): coverage ≈ 1, half the tests at the run site;
- **long class runs** (row 13 `[a-z]{4096,}`, rows 17-18 `"([^"\\]+)"`);
- **hex spans** (row 14 `loglines/ipv6`: 16 run sites, re-visit 5.7).

Below the top 20 (`results/artifacts.tsv.gz` has all):
- uuid / hex32 / iso-ts / the digit ladders sit at ranks 52-131 (score 340-960);
- ipv4 `ref/ipv4-cap` is rank 83 (645), `rw/L02` `\b(?:\d{1,3}\.){3}\d{1,3}\b` rank 85
  (631), `rw/L03` (strict octets) rank 80 (698).

### 4.2 `auto` (what a user gets), REAL populations, RESCAN excluded (`results/top_auto_real.tsv`)

| # | pattern | source | classes (size x sites) | runs (poss) | tests/B | re-visit | cov | start skip/B | start set, shared | exp | R | V | A | **score** | own tests/B, score | att, fails /KiB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `(?J)(?:(?<w>the)\|(?<w>\w+)) \k<w>` | syntax/mod-j-uc | 63x1,1x1 | 1 (1) | 3.95 | 4.511 | 0.875 | 0.9937 | 63, yes | big+bitmap | 3322 | 3148 | 1018 | **4432** | 3.5426, 4356 | 720, 1438 |
| 2 | `(?P<t>\w+) (?P=t)` | syntax/bak-py | 63x1,1x1 | 1 (1) | 3.9478 | 4.509 | 0.875 | 0.9937 | 63, yes | big+bitmap | 3322 | 3146 | 1018 | **4430** | 3.5381, 4353 | 720, 718 |
| 3 | `(\w+) \1` | syntax/bak-1 | 63x1,1x1 | 1 (1) | 3.9478 | 4.509 | 0.875 | 0.9937 | 63, yes | big+bitmap | 3322 | 3146 | 1018 | **4430** | 3.5381, 4353 | 720, 718 |
| 4 | `(\w+) \g{-1}` | syntax/bak-g-rel | 63x1,1x1 | 1 (1) | 3.9478 | 4.509 | 0.875 | 0.9937 | 63, yes | big+bitmap | 3322 | 3146 | 1018 | **4430** | 3.5381, 4353 | 720, 718 |
| 5 | `(?m)^(?!.*\bINFO\b).*$` | rw/L24 | 63x4,1x2,255x2 | 2 (0) | 4.0386 | 4.039 | 0.999 | 0.0 | nullable, ? | big+bitmap | 2048 | 3112 | 0 | **4133** | 3.9338, 4028 | 26, 1050 |
| 6 | `\b(\w+)\b\s+\1\b` | tests/possessify/possessify.rxt:… | 63x7,6x1 | 2 (2) | 2.8837 | 3.068 | 0.94 | 0.998 | 63, yes | big+bitmap | 1155 | 1990 | 1022 | **3735** | 2.8761, 3847 | 723, 722 |
| 7 | `\b(\w+)\s+\1\b` | rw/L18 | 63x5,6x1 | 2 (2) | 2.541 | 2.703 | 0.94 | 0.998 | 63, yes | big+bitmap | 1155 | 1639 | 1022 | **3406** | 2.6617, 3558 | 723, 722 |
| 8 | `\b\w+(?=,\s+and\b)` | rw/P13 | 63x5,1x1,6x1 | 2 (0) | 1.9563 | 2.094 | 0.934 | 0.0 | 63, yes | big+bitmap | 928 | 1047 | 0 | **1844** | 2.0662, 2040 | 176, 903 |
| 9 | `(\w)(\w)\2\1` | syntax/bak-2 | 63x2 | 0 (0) | 1.4034 | 1.605 | 0.874 | 0.9943 | 63, yes | big+bitmap | 0 | 541 | 1018 | **1364** | 1.5236, 1531 | 719, 717 |
| 10 | `[a-z]{0,32768}` | bounded/cls-upto-32768 | 26x1 | 1 (1) | 1.1176 | 1.118 | 0.999 | 0.0 | nullable, ? | - | 1144 | 120 | 0 | **1144** | 0.9807, 981 | 634, 0 |
| 11 | `a?+a` | tests/atomic_groups/d27/possessi… | 1x2 | 1 (1) | 0.9373 | 1.961 | 0.625 | 0.0 | 1, yes | - | 480 | 470 | 0 | **594** | 1.843, 1781 | 480, 480 |
| 12 | `\b(the\|a\|an\|of\|to\|is\|in)\s+\1\b` | rw/C19 | 63x4,2x2,2x2,2x2,2x2,… | 1 (1) | 0.6098 | 1.83 | 0.337 | 1.0 | 8, yes | big+bitmap | 33 | 283 | 1024 | **452** | 0.7244, 565 | 165, 349 |
| 13 | `(["'])(?:(?!\1)[^\\]\|\\.)*\1` | capability/quoted-delim-match | 2x1,255x1,1x1,255x1 | 0 (0) | 0.3037 | 1.35 | 0.538 | 0.7216 | 2, yes | big+bitmap | 0 | 81 | 739 | **441** | 0.0119, 172 | 10, 308 |
| 14 | `(\d)(\d)(\d)\3\2\1` | capability/phone-palindrome-6 | 10x3 | 0 (0) | 0.3694 | 1.8 | 0.365 | 0.9984 | 10, yes | - | 0 | 168 | 1022 | **435** | 0.2605, 209 | 147, 147 |
| 15 | `<([a-zA-Z][\w:-]*)(?:\s[^>]*)?>.*?</\1\s*>` | capability/tag-pair-match | 1x2,6x2,1x2,52x1,65x1… | 3 (2) | 0.3281 | 2.15 | 0.921 | 0.0271 | 1, yes | big+bitmap | 57 | 180 | 28 | **244** | 0.0001, 0 | 3, 135 |
| 16 | `(?<p>\((?:[^()]\|(?&p))*\))` | syntax/rec-name | 1x2,254x2,1x2 | 0 (0) | 0.1478 | 1.389 | 0.301 | 0.6806 | 1, yes | big+bitmap | 0 | 42 | 697 | **222** | 0.0066, 18 | 6, 18 |
| 17 | `(\((?:[^()]\|(?1))*\))` | syntax/rec-1 | 1x2,254x2,1x2 | 0 (0) | 0.1478 | 1.389 | 0.301 | 0.6806 | 1, yes | big+bitmap | 0 | 42 | 697 | **222** | 0.0066, 18 | 6, 18 |
| 18 | `\((?:[^()]\|(?R))*\)` | tests/startset/vmhat.rxt:15 | 1x2,254x2,1x2 | 0 (0) | 0.1478 | 1.389 | 0.301 | 0.6806 | 1, yes | big+bitmap | 0 | 42 | 697 | **222** | 0.0165, 42 | 6, 18 |
| 19 | `(?>(?<!\\)(?>"(?>\\.\|[^\\"]+)+"\|""\|(?>'(?>\…` | capability/wild-logparse-quoteds… | 1x7,255x6,1x4,1x4,1x4… | 6 (0) | 0.3208 | 1.107 | 0.589 | 0.0 | 3, yes | big+bitmap | 289 | 32 | 0 | **189** | 0.0171, 3 | 8, 24 |
| 20 | `(?<![0-9.+-])(?>[+-]?(?:(?:[0-9]+(?:\.[0-9]+)?…` | capability/wild-logparse-base10n… | 10x3,1x2,13x1,2x1 | 4 (4) | 0.3155 | 1.498 | 0.374 | 0.0 | 13, yes | bitmap | 236 | 107 | 0 | **121** | 0.2132, 46 | 44, 31 |

Under `auto`, only 117 real artifacts are VM-routed. 59 of them make any class test on the
panel, and the median score is 0. The VM work that remains has three sources:
- patterns forced into the VM WITHOUT a usable prefilter: backrefs (rows 1-4, 6-7, 9,
  12-15), lookaround (rows 5, 8, 19-20) and recursion (rows 16-18);
- one bounded run, `[a-z]{0,32768}` (row 10);
- the rest are short finishers.

This is the population where [VM-CLSMASK] would change what users get. The leaders are the
same `\w`-token cells as 4.1, and `(?m)^(?!.*\bINFO\b).*$` (a real log question, prefilter
`none`, 4.0 tests/B: the lookahead walks each line, then `.*` walks it again).

### 4.3 RESCAN, ranked apart (`results/top_{vm,auto}_rescan.tsv`)

Re-visit ≥ 8 on the panel. 15 real vm artifacts and 1 real auto artifact:
- `\b(\w+)=[^&]*&(?:[^&]*&)*\1=` (re-visit 500; auto = VM);
- `altwide/ci-256` (217; its 84-literal switch re-dispatches per start);
- `rw/S05` (89), `bounded/csv5` (46), `.*\.txt$` (129), `.{80,}` (17), `\S+@\S+` (31).

The rest are D27 adversarial corpus patterns at re-visit 10³-10⁴. Masks would turn each
re-read into a bit read, and a `ctz` advance over a run would shorten each re-scan by up to
64x. But the quadratic stays. These belong to the attempt-split / revend rows, and they
should not be read as this row's evidence. One exception is worth a sentence: on `csv5`
and `S05`, the re-scanned spans are bounded-negated-class runs (`[^,\n]{0,32}`,
`[^,]*`). A run-advance by `ctz` is the cheap part of either fix.

## 5. Is ipv4 a good candidate?

**Not under `auto`, and only middling under the forced VM.** The numbers, from the
compiler's output:

| ipv4 `(\d{1,3}\.){3}\d{1,3}` | auto (hybrid prefilter) | forced VM |
|---|---|---|
| classes the program tests | `\d` (4 run sites), `.` (3 step sites) | same |
| run sites possessified (IR) | 1 of 4; possessify 2/3; `RX_VM_STRATS` 0x3 | same |
| program tests / B, panel (own) | **0.011** (0.021) | 0.73 (1.13) |
| re-visit, panel (own) | 1.14 (1.13) | 3.53 (3.27) |
| coverage | 0.17 | 0.37 (0.35) |
| start-skip tests / B | 0 (the DFA locates) | **0.99**, start set = `\d`, shared |
| attempts, fails / KiB, panel | 0.7, 0 | 142, 450 |
| score (rank of 475 / 117) | 1.7 | 645 (rank 83) |

**Under auto**, the capture-erased DFA pair hands the VM an exact window. The VM then only
finishes known matches: about 15 tests per match, no backtracking. Any byte-level win for
ipv4 under `auto` lives in the LOCATOR, which is [SPAN-ISEL]'s question. That agrees with
the [VM-CLSMASK] row's own FORCES paragraph: for dense-class, no-rare-literal patterns the
locator may dominate.

**Under the forced VM**, ipv4 shows each lever, none of them strongly:
- **(e) amortization.** The attempt loop tests `\d` at 99% of bytes, and the program's
  own class IS the start set. One classify really would serve both, and this is ipv4's
  largest term.
- **(b) runs.** 58% of program tests are run tests, but runs are at most 3 long. A
  `ctz(~D>>p)` saves at most 2 tests per run, against a block-valid check.
- **(c) re-visits, 3.5.** These come from overlapping attempts inside digit groups
  (`1234.5.6.7` is tried from `1`, `2`, `3`, `4`) and from giveback. Only 1 of 4
  `\d{1,3}` run sites is possessified: the three inside `(…\.){3}` keep their retreat
  frames although `\d` and `\.` are disjoint. Read the IR's `strategies` table: L6/L13/L20
  are `backtracking`, L2 is `possessive`. A possessify gap there (if it is one; not
  investigated) would remove part of the re-visit term before any mask does.
- **Coverage 0.37.** On mixed text, digits are sparse, so a whole-block classify is about
  a third used. On digit-dense text (apache logs, own subjects) it barely moves (0.35),
  because the VM skips non-digit positions by the start skip, not by the program.

Verdict: ipv4 is the right **teaching** example (all three mechanisms visible, possessify
partly proven, start set shared). It is not where a timing run would show the most. Keep
it as the reference cell Frank named, beside stronger shapes.

## 6. Recommended timing candidates (five shapes)

| # | pattern | route | why this shape | counts (panel) |
|---|---|---|---|---|
| T1 | `(\w+) \1` (bench `syntax/bak-1`) | **auto = VM**, no prefilter | EXPENSIVE class (`\w` bitmap) + possessified RUN + attempt OVERLAP; start shared | 3.95 tests/B, re-visit 4.5, cov 0.88, start 0.99/B |
| T2 | `(?m)^(?!.*\bINFO\b).*$` (rw/L24) | **auto = VM**, prefilter none | LOOKAHEAD re-walk: each line walked twice over `.`; nullable start, so NO start mask: isolates the program-side benefit | 4.04 tests/B, re-visit 4.0, cov 1.00 |
| T3 | `(?m)^.{400,}$` (rw/L27) | forced VM (auto = DFA) | pure long RUN over a 255-byte class: the `ctz(~mask)` showcase; every block fully used | 1.90 tests/B, run share 0.53, cov 1.00 |
| T4 | `loglines/ipv6` | forced VM (auto = DFA) | MANY small hex classes, 16 counted run sites, dense re-visit; also [SPAN-ISEL]'s no-rare-literal locator shape | 2.81 tests/B, re-visit 5.7, cov 0.50 |
| T5 | ipv4 `(\d{1,3}\.){3}\d{1,3}` | forced VM (auto = hybrid) | the named reference: start-mask amortization dominant, short runs, sparse coverage | 0.73 tests/B + 0.99 start/B, re-visit 3.5, cov 0.37 |

Each candidate should be timed in two consumption forms, as the [VM-CLSMASK] row's trigger
already names them: the mask read bit-at-a-time, and the mask consumed by `ctz`. That
needs targeted hardware and a bench slot. A utf8/`\w` cell is NOT recommended from this
census: no utf8 class reaches a run site today (§2), so the utf8 cell would test a stage 1
that does not yet have a consumer.

## 7. Side findings (not acted on)

- **The start skip is the largest class-test consumer under forced VM** (0.48/B vs the
  program's 0.33/B on real patterns). [ideas.md 2026-10-10]'s "the VM attempt loop's
  start-set skip: a scalar, re-entered, undelegated prefilter" is therefore the BIGGEST
  single consumer of a start mask, independent of the program-side design.
- **ipv4's inner `\d{1,3}` stays backtracking** (above). This is a question for the
  possessify owner, not a filed claim.
- **utf8 classes never take a run site** in today's VM. They are frames-rung decode+class
  steps, so a utf8 run optimisation precedes any utf8 mask.
- The 20 `tests/vars/*` artifacts per config could not be driven: their `rx_search` takes
  variable arguments. They are excluded and counted (§1.2).

## 8. What this does NOT show

- No time. Tests per byte are not nanoseconds. A bit read costs about what a range test
  costs. The row's own FORCES paragraph says the batch only pays when the mask is
  consumed by word ops, or when it replaces an expensive class. The score counts the
  tests a mask COULD serve, never what serving them costs.
- Classify cost is not modelled beyond the coverage discount. k classes × blocks touched
  is in the data (`classes`, `B`) for a design lane to price.
- The panel is ASCII-heavy text (no non-English file). utf8 rows rank on their own
  subjects only.
- The RESCAN threshold (re-visit ≥ 8) is a stated cut, not a derived one. Moving it moves
  only which table a row lands in.

## 9. Reproduce

`docs/dev/clsmask_candidates/run_all.sh` from the repo root after `make`. Inputs:
pcrec-bench read-only, and the corpus cache. Work goes to `build/cs` (gitignored).
Regenerating moves every number here. Committed outputs are in `results/`.
