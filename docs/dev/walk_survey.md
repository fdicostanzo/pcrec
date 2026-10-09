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

@@HEADLINE@@

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
  - Size: 367 patterns, 914 (pattern, regime) rows, 62,868 subject runs.
  - Configs: `default` and `nocaps` (`--no-captures`), plus `anch` (`\A(?:P)`, the
    anchored-attempt reference) where the match regime runs.
- **CORPUS** (`pop_corpus.py`): every distinct pattern block of every shipped `.rxt`, with
  the block's own encoding and `i` flag. Subjects:
  - the block's own inline m/n subjects;
  - three synthesized 16 KiB subjects from a deterministic prose filler: `FILLER+M` (a match
    near the end), `M+FILLER` (a match at the start), `FILLER+N`.
  - Size: @@CORPUS_POP@@.

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
  upper estimate for the scan classes (K5-K7). Every top class is therefore re-timed by an
  answer-checked hand-twin (§3).

## 2. Instrument validation (`results/validation.txt`, `validate.sh`)

The instrument was validated before any population number was read.

| case | expectation | measured |
|---|---|---|
| 1 KNOWN GRATUITOUS: `\d+$`, 1 MiB prose + `" 12345"` | about `n` bytes against a 6-byte answer | `T` = 1,048,585, `U` = `n`; skip 1,048,572, fwd 6, rev 7 |
| 2 its [OPT-REVEND] form-C twin (`revend_twin/mktwin.py`, an independent transformer) | the match alone | `T` = 8 (rev 7 + the twin's seed test) |
| 3 KNOWN TIGHT: `^abc` on a 1 MiB subject beginning `abc` / not | about 3 / 1 | `T` = 4 / 1 |
| 3 `abc` with its one match at the end | the forward lower bound, by memchr | `U` = `n`−1, `T_scan` = `n`−2 |
| 4 PLANTED (failing direction): `^abc` plus one planted forward pass, and plus one planted reverse pass | `n` extra each, visible as an unclaimed site | `T` = 1,048,580, `unk` = 1,048,576, both |
| 5 INDEPENDENT COUNT: gcov line counts of `\d+$`'s artifact on case 1's subject | skip and forward counts equal | skip-loop line 1,048,572 = instrument skip 1,048,572; forward-step line 5 = instrument fwd 6 − the one end-view load |
| 6 CLASS MEASURES RESPOND: K4 on `\w+` (artifact vs the landing twin), K5 on `(?i)cat` over lowercase (fold vs `-fno-req-run-fold`) | the twin/arm reads 0 | `land_rev` 73,727 → 0, `T` 172,030 → 98,303; `A_pre` 97,624,809 → 0 |

@@BODY@@
