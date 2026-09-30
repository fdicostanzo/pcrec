# U3 island hand-twin (ucp_design.md UD-6 / UD-7 b-island)

Lane `u3twin`, 2026-09-30, branch `lane/u3twin` from main `89067472`. Harness and
twins: `studies/u3_island_twin/` (own CLAUDE.md). Nothing under `src/`.

STATUS: correctness half COMPLETE (Mac). Timing half OWED (ubuntubudu, needs
"TIMING GO" and a quiet box; see the resume recipe at the end). No D77 verdict
is given here because none is supported yet.

## 1. What was built

The island of ucp_design.md s3.1-3.5 as generated C ("hand-twin"), per case
and per vector producer (kit lambda=4, page3w, bitmap1):
ASCII bytes step exactly as today through a byte-class table; every non-ASCII
byte is one class NA whose cell is an island token in the reserved top range
(dead = -1 too, so `(unsigned)st >= FLOOR` is the only stop compare, none added
on the ASCII path); the island decodes with the stage-4 decoder (verbatim),
takes the membership vector (ill-formed byte = BOT, one byte, in no set),
resumes at `tgt[q][v]`. The reverse pass uses the REPAIRED back_step. Forward
is seeded from the character before `search_from` (back_step + vector). A
state's accept can depend on the next character (H7): answered per ASCII class
by a class-indexed table and per non-ASCII vector inside the island
(`acc_isl[q][v]`). Self-loop folds apply only to non-accepting states.

Two construction routes:
- F1 (a consuming wide class, an all-byte artifact exists): the machine is
  COMPUTED from pcrec's own flat byte tables (delta of the byte machine over
  every reachable boundary state and every non-ASCII code point, grouped by
  byte-class sequence; atoms = columns; BOT = delta on byte 0xFF); the set's
  non-ASCII intervals are read back off the atoms, so twin and base cannot
  disagree about the set.
- F2 (context set not byte-expressible, no all-byte form): machines derived by
  hand in both directions (`f2.py`).

| case | pattern | today's form | twin |
|---|---|---|---|
| c1 | `[\x{100}-\x{2000}]+` | all-byte DFA | F1 |
| c3 | `[\x{100}-\x{FFFF}]+` | all-byte DFA | F1 (surrogate control only) |
| nd | `\p{Nd}+` | all-byte DFA | F1 |
| l | `\p{L}+` | all-byte DFA (default cap DROPS premul + anchored; raised-cap arm bd) | F1 |
| xwd | `\p{Xwd}+` | all-byte DFA (mixed tables) | F1 |
| x1 | `(?<=[\x{100}-\x{2000}])x` | VM hybrid (auto), forced VM | F2 |
| x2 | `(?<![W])[W]+(?![W])`, W = `\w` + U+C0-24F, U+370-52F | VM hybrid, forced VM | F2 |
| x3 | `\b\w+\b` with UCP (W = Xwd) | REFUSED (no baseline) | F2 |

x2 is a \b-shaped pattern with a wide context spelled as lookarounds so a pcrec
baseline exists; x3 is the real UCP \b, answer-checked against libpcre2 only.
Fairness: x1's twin carries the necessary-byte whole-window pre-check pcrec
stamps today (`RX_REQ_BYTE`); without it the twin loses 80x on CJK text to a
memchr it should have.

## 2. Correctness (Mac, complete)

31,168 (subject, startpos) cases over 6,806 subjects (edge code points of every
set, random text, and the ill-formed matrix: truncated 2/3/4-byte, overlong
incl. of ASCII word chars, surrogate, > U+10FFFF, stray continuation, 0xFF,
lead + too many continuations), each searched from every boundary (short
subjects) or a sample.

- Every arm (today's artifact, raised-cap artifact, forced VM, three twins) vs
  libpcre2 **10.46** (reference box, light ssh ctypes run, UTF|MIU, +UCP for
  x3): **0 differing in every case**. Arm-vs-arm: 0. Table:
  `studies/u3_island_twin/results/correctness_10.46.tsv`.
- ASan+UBSan on the driver (exact-length subject copies): clean, all cases.
- Local libpcre2 10.48 shows 14-15 differences on x3 only, all at code points
  Unicode 17 assigned (e.g. U+1AD1, U+0CDC); pcrec's UCD is 16.0.0 and 10.46
  agrees exactly. Not a twin defect.
- REACH (`results/reach.tsv`): the kit4 twin enters an island 17k-78k times
  and decodes an ill-formed byte 2k-20k times per case over this set.
- FAILING-DIRECTION CONTROLS (`results/controls.tsv`), planted into a twin's
  source: overlong accepted (c1 233, x1 18), BOT read as a member (c1 1,737,
  x2 3,801), predicate off by one (c1 505), back_step length test removed
  (x2 218, x1 15), seed ignored (x1 279, x2 673), H7 accept column zeroed
  (x2 9,342): all DETECTED. NOT detected, each for a stated structural reason:
  c3 surrogate (the exact predicate excludes surrogates by construction, so a
  decoder that accepts them still lands on "out"), x2 overlong (an overlong
  ASCII form decodes below U+80, outside the non-ASCII predicate, and BOT and
  out share a column in these machines), c1 back-len (c1 has no context read
  and its reverse walk never crosses `from`; x1 and x2 see the defect).
  These three defects are unreachable for these patterns; they need a
  complement-shaped set to become observable.

## 3. Timing (ubuntubudu): OWED

Protocol (house): all arms built before any timing; 1-minute load polled for
< 0.5 before EACH (case x regime) unit, up to 600 s, refusal not caveat; 11
rounds, arms interleaved with rotating start; answers checksummed every round
and compared across arms; median and per-round range; null control `bc` (the
same source as `bb` under another prefix) and bb's own spread set the noise
floor; ratio vs bb. Regimes: ascii prose, latin1-heavy prose (~8% non-ASCII
chars), cjk, mixed. Find-all loop, ns per code point.

## 4. Verdict against the D77 bar: OWED (needs section 3)

## 5. Resume recipe

    scp/ssh only into /home/duxevents/pcrec/.u3twin_scratch/
    tar xzf u3twin_bundle.tgz   (build: studies/u3_island_twin/bundle.sh)
    python3 run_bench.py --cc gcc --rounds 11 --out results/bench_ubuntubudu.tsv
    python3 summarize.py results/bench_ubuntubudu.tsv results/bench_summary.tsv
    rm -rf /home/duxevents/pcrec/.u3twin_scratch
