# [OPT-VEDGE] — the view-tolerant scan edge (lane vedge, 2026-10-03, opus)

Round 1 of the [OPTLOOP] cycle under D144, third item (it replaces
[SEL-COST]; see docs/design/sel_cost.md T1). Branch `lane/vedge`, from main
2f1d9120. Built under its own deny bit, `-fno-view-edge`
(`PCREC_NO_VIEW_EDGE`, bit 42). abi 55 -> 56.

## Summary (resume from here)

- **STEP 1 confirmed the mechanism, but relaxing precondition (3) accounts for
  only half of the witness.** At 2f1d9120, `(?:[a-z]{0,2048})\z` stamps edge
  `none` and the same pattern without `\z` stamps `range` (the M3 probe pair,
  re-run). Relaxing (3) on the forward machine alone halves the loss. The
  other half is the REVERSE machine: its counting chain is view-free, but
  precondition (6) refuses it because the chain head is the start state's END
  view target. The row therefore ships TWO relaxations under one flag: (a) the
  (3) relaxation, and (b) a trim for (6)-refused heads.
- **Result (Mac scratch, directional).** On the `cls-upto-N\z` family, the
  default build beats `-fno-view-edge` by 3.1-4.4x on whole-subject calls for
  N >= 64 (1.3-2.1x at N = 4/16). Example: `(?:[a-z]{0,4096})\z` goes from
  145 / 16,767 / 9,653 to 46 / 3,822 / 2,851 ns per call (subjects: 40
  letters, 4 KiB of letters, 64 KiB of words). The forced VM measures 20 /
  1,915 / 14,177, so the remaining ~2x loss on letter-run subjects is the
  reverse pass existing at all. That part is not this row's.
- **[ART-SIZE]:** 1 of the 143 warned bench artifacts retires
  (`cls-upto-2048\z` utf8, 310,030 -> 188,156 B). The O-12 pair shrinks but
  stays warned: `cls-upto-4096\z` byte goes 476,963 -> 259,123 and utf8
  600,847 -> 354,044. The row's "the two size warns retire" needs a SECOND
  mechanism, which this lane prototyped and measured (§4). It is filed as
  [OPT-ENDTERM] and NOT built here.
- **Regressions to file as D144 issue rows** (§5): small per-call costs of
  +0.7 to +4 ns on short, non-matching whole-subject calls, on movers whose
  start state became a head (`(?:\d{4})\z` 5.7 -> 9.5 ns on 40 letters).
  These are the scan edge's known fixed entry term (O-12 ask (ii)), newly
  reached by these artifacts.
- **Validation:** see §6. `make strict`, `test-registry` and the census are
  green. The full corpus and the deny-axis identity sweep are OWED (§6).

## 1. STEP 1 — the measurement

`build/pcrec --features all -p rx -o - --pattern P` at 2f1d9120:

| pattern | bytes | scan edge | start | match |
|---|---|---|---|---|
| `(?:[a-z]{0,2048})\z` | 234,310 | none | reverse-pass | search-filter |
| `(?:[a-z]{0,2048})` | 12,127 | range | pinned | unwrapped |
| `(?:[a-z]{0,256})\z` | 55,838 | none | reverse-pass | unwrapped |
| `(?:[a-z]{0,4096})\z` | 465,735 (warned) | none | reverse-pass | search-filter |

Reading the emitted tables of `(?:[a-z]{0,256})\z`:

- FORWARD (770 rows): three families. (A) is the search chain: exit to s0,
  plain accept 0, END view to an accepting row. (C) is those accepting END
  view targets. (B) is a second chain reachable only from C's transitions.
  Precondition (3) refuses every A member.
- REVERSE (258 rows): the start row has NO transitions and reaches the
  view-free, accepting counting chain only through its END view. The chain's
  natural head is therefore a view target, and precondition (6) refuses it.
  Because `haspred` marks its successor, no later head exists, so the whole
  reverse chain is lost.

Prototype timings, ns/call (40 letters / 4 KiB letters / 64 KiB words), same
box and load as in §3:

| `(?:[a-z]{0,4096})\z` | short | l4k | prose64k | bytes |
|---|---|---|---|---|
| base | 134.7 | 15,294 | 8,925 | 465,729 |
| (a) relax (3), forward only | 79.0 | 8,130 | 2,605 | 363,072 |
| (a)+(b) | 44.9 | 3,978 | 2,802 | 247,889 |
| (a)+(b)+(c) [OPT-ENDTERM] prototype | 42.5 | 3,570 | 2,622 | 14,499 |
| forced VM | 20.2 | 1,915 | 14,177 | 12,590 |

So the mechanism explains the witness once (b) is added, apart from the
reverse pass's own cost. The manager was told mid-lane (interim message).

## 2. Design deltas against opt5_step2_twopass.md §2

The design said: "relax (3) to 'the only view is the END view, and the scan's
own exit at `pos == n` evaluates it'". As built (src/opt/scanedge.c):

1. **Direction is an input.** `pcrec_scanedge_dfa` gains `end_is_exit`. It is
   true for the forward and anchored machines (their loop selects the END view
   at `n`, probes the accept bit, and breaks before any step). It is false for
   the reverse machine, which STARTS at `n` and steps from the view-selected
   state, with the edge path running before the view select. S440 plants
   `true` for the reverse machine; `[a-z]{2,4}(?:\z|[a-z])` then loses 23
   cells.
2. **No emitter change.** The emitted edge block already falls through to the
   view select, so a run that stops at `n` with the state left at the head
   gets the head's END view evaluated. That is sound iff every member's END
   view has the same accept bit. `end_acc_of` joins chain compatibility as
   `same_shape`, beside the plain bit and the exit. The one thing the block
   does at `n` without the view is record the run's plain bit when the run
   stopped there. That is wrong only for plain=1 over END=0, so `member_ok`
   refuses such a member. The bound-reached `if (acc(F)) record(pos)` line has
   the same property, and F goes through the same `member_ok`.
3. **(b), the (6) trim**, is not in the design. A view-target head is left as
   an ordinary state, and the chain starts at its class successor when that
   successor's only way in is the head (`indeg == 1`, so it is nobody's view
   or seed target). Every step into the new head is then an ordinary step that
   the stop test sees. The trim is limited to (6). The (8) reseed refusal is
   unchanged, so the flag stays view-scoped.
4. On a view-free machine `end_acc_of == acc_of`, so every pre-row chain is
   unchanged. `-fno-view-edge` restores the old pass byte for byte, and the
   bit is masked out of `rx_info.flags`.

## 3. Movers

- **Corpus** (3,440 distinct `pattern` lines, `--features all`, default vs
  `-fno-view-edge`, same binary): 34 artifacts move, +43,135 B in total. All
  are `\z`/`\Z`/`$` forms, and most gain an edge block of a few hundred bytes.
  The list is in the scratch TSV; the shapes are `a\z`, `a{0,4}$`,
  `(?m)a{0,4}$`, `\b\w+\z`, `[^c]{1,3}\z`, `.*\z` and view_edge.rxt's own.
- **Bench patterns** (1,356 = every bench pattern raw and as `(?:P)\z`, at
  byte and utf8): 161 move, all of them `\z` forms. 106 gain their first edge
  (edge != none goes 351 -> 457). The `cls-upto-*\z` ladder shrinks
  (e.g. 2048 byte 245,538 -> 139,634). Small patterns grow by 0.5-6 KB of edge
  code.

## 4. [ART-SIZE] and the second mechanism ([OPT-ENDTERM], filed, not built)

Warned bench artifacts (over 250,000 B): 143 at base, 142 with this row. The
one retired is `cls-upto-2048\z` utf8. N1 routing (12) and search-filter
(139) are unchanged. `search-filter` is decided from the anchored machine's
build-time state count, before this pass runs, so the row's "search-filter
band shrinks" consequence does NOT follow from this mechanism.

The size half needs **forward END-view targets to be terminal**. On a
machine whose walk exits at `n`, a state reached ONLY as an END view target
is never stepped from. Its transitions are dead weight, and so is any family
reachable only through them (the B family above, 2N rows on the witness).
The prototype did three things: a reachability walk over transitions and EOL
links, clearing transitions on END-only targets, and merging those targets by
accept signature. Measured with (a)+(b)+(c):

- `cls-upto-4096\z` byte 476,963 -> 25,733 B, utf8 600,847 -> 27,760 B.
- Warned 143 -> 138: the O-12 pair, `cls-upto-2048\z` utf8, `pw-8-64\z`
  utf8 and `prp-n\z` utf8 retire.
- BUT four warned artifacts GROW: `unp-p-lc\z`/`prp-l\z` utf8 492,977 ->
  783,246, `unp-p-uc\z`/`prp-notl\z` 508,737 -> 775,862, and `cnt-64\z`
  827,202 -> 913,683. Not diagnosed; the likely suspect is a size-cap-ladder
  rung choosing differently.
- It touches every `(?:P)\z` artifact's forward table (35 corpus movers on its
  own).

Proposed row: **[OPT-ENDTERM] — terminal END-view targets on exit-at-`n`
machines.** Its own deny bit, minimization-adjacent (it belongs before
`pcrec_minimize_dfa`, so minimization does the merge), and an ART-SIZE
customer list taken from the numbers above. Its trigger is the growth
diagnosis. Not scheduled (D77).

## 5. Timing (alpha, D144)

**Mac scratch, DIRECTIONAL.** Apple M1, gcc-16 `-O2`. The box was heavily
loaded (load average 15-38) by this lane's own validation suites and other
lanes. `docs/design/sel_cost/percall.c`: median of 7 rounds, ns per
whole-subject `rx_search(s, n, 0)`. Default vs `-fno-view-edge` from ONE
binary (e43b4cbb). Answers were checked equal on every cell (span printed).

Witness family `(?:[a-z]{0,N})\z` (pcrec-bench `bounded/cls-upto-N`), short /
l4k / prose64k:

| N | default | `-fno-view-edge` | ratio (l4k) |
|---|---|---|---|
| 4 | 10.3 / 10.1 / 10.0 | 13.5 / 13.5 / 10.4 | 1.34 |
| 16 | 25.5 / 25.4 / 18.0 | 54.3 / 53.9 / 30.4 | 2.12 |
| 64 | 45.2 / 68.8 / 49.3 | 145.9 / 239.4 / 141.8 | 3.48 |
| 256 | 45.4 / 254.8 / 180.9 | 143.8 / 1,014.7 / 597.3 | 3.98 |
| 1024 | 45.4 / 961.5 / 718.3 | 145.5 / 4,071.8 / 2,380.9 | 4.23 |
| 2048 | 45.3 / 1,909.8 / 1,420.9 | 144.7 / 8,142.1 / 4,827.4 | 4.26 |
| 4096 | 46.3 / 3,822.4 / 2,851.3 | 144.9 / 16,767.1 / 9,653.3 | 4.39 |

Other bench movers (subjects: short; `dig40` = 40 digits; `mix4k` = 4 KiB
over `ab:12 \n`; `hex4k`; prose64k):

| pattern | default | deny | reading |
|---|---|---|---|
| `(?:\w+)\z` | 38 / 39 / 4,937 / 2,799 / 105,316 | 116 / 116 / 7,946 / 10,939 / 222,328 | win 1.6-3.9x |
| `(?:[0-9a-f]{32})\z` | 45 / 41 / 37 / 41 / 33 | 41 / 118 / 49 / 119 / 27 | win on runs; +4-5 ns on short/prose |
| `(?:.{3,8})\z` | 16 / 16 / 15 / 16 / 16 | 28 / 28 / 22 / 29 / 29 | win 1.5-1.8x |
| `(?:\d{16})\z` | 13.5 / 26 / 21 / 21 / 13 | 9.8 / 55 / 16 / 22 / 10 | win 2.1x on digits; **+3.7-4.6 ns elsewhere** |
| `(?:\d{4})\z` | 9.5 / 10.8 / 9.4 / 7.8 / 9.4 | 5.7 / 14 / 5.8 / 8.7 / 5.8 | **+3.6-3.8 ns on non-digits** |
| `(?::)\z` (floor) | 5.1 everywhere | 4.4 everywhere | **+0.7 ns** |
| base10num-grok `\z` | 21 / 156 / 4,566 / 6,074 / 22,332 | 22 / 156 / 3,590 / 5,943 / 22,122 | **mix4k +27%** |

The regressing cells are whole-subject calls with no run to count. In
`(?:\d{4})\z`, the forward start state (non-accepting, END-viewed, a
self-loop on non-digits) is now a bounded chain head. The loop enters
through the edge path, and every non-digit step returns to it through the
stop test. That is [OPT-5] STEP 1's per-search entry term (O-12 ask (ii),
`year4` x1.07-1.11), newly reached. The plain `\d{4}` already pays a version
of it (16.4 vs 15.8 ns on the same subject). Per D144 rule 3, these become
issue rows if the Linux reading confirms them, and `-fno-view-edge` is the
interim switch.

**Linux commands for the manager** (ubuntubudu, pinned, after
`git -C ~/pcrec fetch` and a worktree at the lane tip; `$P` is that tree's
`build/pcrec`; percall.c and the subjects generated as in §7):

```
cd <tree> && make -j4 && S=<scratch> && P=$PWD/build/pcrec
for n in 4 16 64 256 1024 2048 4096; do
  pat="(?:$(cat ~/pcrec-bench/bench/bounded/patterns/cls-upto-$n.rx))\\z"
  for fl in "" -fno-view-edge; do
    $P --features all -p rx $fl -o $S/m.c --pattern "$pat"
    gcc -O2 -o $S/drv docs/design/sel_cost/percall.c $S/m.c -Ilib
    for s in short l4k prose64k dig40; do echo "$n ${fl:-default} $s $(taskset -c 2 $S/drv $S/$s)"; done
  done
done
# same loop over: syntax/cls-w bounded/dig-exact-16 bounded/year4 bounded/hex32
#   bounded/floor capability/wild-logparse-base10num-grok utf8/qnt-dot-bounded
#   (each as "(?:P)\z"), subjects short dig40 mix4k hex4k prose64k
# noise floor: run the default arm 3x and report the max/min spread per cell
```

## 6. Validation (Mac, each in the background, verdict from make's `*** [` lines)

| run | result | log |
|---|---|---|
| `make strict` | green | `<scratch>/v_strict.log` |
| `make test-registry` (after the 171 -> 174 re-pin) | green | `v2_test-registry.log` |
| `make test-codegen` | first run: red only on run_scan_edge_census (2 manifest rows, re-pinned; see below) and darwin `nm arm_a.o` (accepted). Re-run: see handback | `v_test-codegen.log`, `v2_test-codegen.log` |
| `tests/codegen/run_scan_edge_census.sh` standalone | 20 passed, 0 failed (section (6) included); also 20/0 against the S440 plant, as expected (structural, not direction) | — |
| `tests/harness/run.sh tests/assertions/view_edge.rxt` | 2,703/0 default and under `RXTFLAGS=-fno-view-edge`; 2,680/23 against the S440 plant | — |
| `make test-rxtsource`, `test-assertions`, `test-recursion-identity`, mech `S440` | chained after codegen; see handback | `v2_*.log`, `v2_mech_S440.log` |
| `make test-corpus` (default) and `make test-axes AXES=-fno-view-edge` | **OWED** (armed detached as the lane's last act) | `v3_test-corpus.log`, `v3_test-axes.log` |

The census re-pin: `\b\w+\b\z` forward edges 1 -> 2 and `\b\w+\z` 1 -> 3. Both
are END-view `\w` chains this row admits. Their answers are covered by
tests/assertions/wordb_*.rxt and are part of the owed corpus run.

Pins moved: `PCREC_ARTIFACT_ABI` 56; `ABI_EXPECT=56` and its message;
match_api.md §2 quote and §6 log; the recursion-identity FILEPIN 35a9e2b4 ->
41aec745 (the lane's own src commit, the self-pin convention); registry axes
count 171 -> 174; registry.md's `--list-axes` line 106/37 -> 112/39 (it
was stale at 110/38 on main); tuning.md §2.37, the flags table and §2.18;
cli.md's flag list.

## 7. Owed

1. The corpus run and the deny-axis identity sweep (§6), with logs named
   there.
2. Linux pinned alpha timing (§5 commands).
3. The mech row S440's own matrix figure (chained; see handback).
4. [OPT-ENDTERM], filed in §4, not scheduled.
5. Regression rows for the short-call fixed term, if Linux confirms them.

Witness generator (tests/assertions/view_edge.rxt): python3 `re`, with
`search(s, pos)` for every start position. PCRE `\z` is translated to
`\Z`, PCRE `\Z` to `(?=\n?\Z)`, and `$` is left unchanged. The patterns and
subjects are listed in the file itself.
