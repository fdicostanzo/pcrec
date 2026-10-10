# revpred -- predicted [OPT-REVEND] values for the bench's acceptance cells

Lane revpred, 2026-10-10, analysis only (NO timing runs: another heavy run
holds the box). Answers pcrec-bench O-91 ask (2): state predicted values for
the 15 tail cells (`\d+$`, `\w+\z`, `\s+$`, `[a-z]+\.txt$`, `.*\.txt$` x
`t-tail-{digits,txt,space}-1m`) plus `\s+$` x `t-trim-nearmiss-16k`, before
the AFTER window. BEFORE pin `a15fb77b` (abi 72), AFTER pin `7388f1c0` (abi 73,
[OPT-REVEND] L1 + L2 with stage 2). Branch `lane/revpred`.

## 1. Result

All 20 patterns x form artifacts (5 patterns x caps/nocaps x 2 pins) were
emitted with the bench's own flags and the stamps read. At `7388f1c0` EVERY
tail cell routes through rev-end; the forward scan over the body is gone, so
the cost stops depending on the body size and becomes the cost of reading the
tail line backwards.

| stamp | before `a15fb77b` | after `7388f1c0` |
|---|---|---|
| `RX_ENGINE` | `dfa` | `dfa` |
| `RX_DFA_SCAN` | `unanchored` | `rev-end` |
| `RX_DFA_START` | `reverse-pass` | `reverse-pass` |
| `RX_DFA_PREFILTER` | `byte-class-bounded` (`\d+$`, `\w+\z`, `\s+$`, `[a-z]+\.txt$`); `memchr-bounded` (`.*\.txt$`) | `none` (all five) |
| `RX_DFA_MATCH` | `unwrapped` | `unwrapped` |
| `RX_VM_PREFILTER` | not emitted (DFA artifact) | not emitted |
| `RX_DFA_SCAN_EDGE` | `range` (`\d+$`), `bitmap` (`\w+\z`, `\s+$`), `none` (the two `.txt$` patterns) | identical at both pins; the rev-end walk's run loop uses it |

The caps and nocaps artifacts of each pattern are byte-identical but for the
header include line and `.flags` (0 vs 4): every pattern has `ngroups 0`, so
there is no capture work and no finisher span work on the caps route
(`ncaps 1`, group 0 only, written straight from the walk). The same stamps
hold on both routes. The predictions are therefore ONE set of numbers for
auto-caps and auto-nocaps; if the two routes differ in the AFTER window by
more than the bench's route-to-route spread on these cells (O-91: under 1% on the 1 MiB cells), that is a finding.

Predicted AFTER values are **7-98 ns per call** (table below) against O-91's
0.21-2.85 ms: predicted ratios 2,100x to 420,000x, 10x to 4,300x on the
16 KiB near-miss cells. The old 0.70 / 2.15 / 1.69 / 2.72 / 0.20 ns/B rates
stop being meaningful: the cell no longer scales with the body, and ns/B on a
1 MiB body will read 0.00001-0.0001.

## 2. Per-cell table

Columns: reverse steps = bytes the reverse DFA consumes from the end until it
dies or reaches `search_from` (independent semantic model, section 3);
loads = subject loads counted by instrumenting the emitted artifact over the
bench's find-all loop (all calls, including the second call that starts at
the match end); calls = `rx_search` calls the driver's find-all loop makes
(matches + 1, so a matching cell makes 2); O-91 = auto-caps / auto-nocaps
median ns (reports/...subject-grain.tsv). Predicted = section 4's formula.
Anchored forward re-run (the tie's `verify-at`): NONE on any cell, since the
tie needs a final `\n` and none of the four bodies ends in one (the walk
never takes its second seed; instrumented, calls and loads confirm).

| pattern | body | reverse steps | loads (inst.) | O-91 before, caps ns | before, nocaps ns | predicted ns (low-high) | predicted ratio caps (x) | match |
|---|---|---|---|---|---|---|---|---|
| `\d+$` | t-tail-digits-1m | 9 | 12 (2 calls) | 737,204 | 738,658 | 19-60 | 12,390-38,000 | yes |
| `\d+$` | t-tail-txt-1m | 1 | 2 (1 call) | 736,695 | 733,151 | 7-24 | 31,349-108,338 | no |
| `\d+$` | t-tail-space-1m | 1 | 2 (1 call) | 734,780 | 738,771 | 7-24 | 31,267-108,056 | no |
| `\w+\z` | t-tail-digits-1m | 9 | 10 (2 calls) | 2,252,451 | 2,252,219 | 19-60 | 37,856-116,106 | yes |
| `\w+\z` | t-tail-txt-1m | 4 | 5 (2 calls) | 2,250,659 | 2,252,959 | 13-42 | 53,587-167,960 | yes |
| `\w+\z` | t-tail-space-1m | 1 | 1 (1 call) | 2,210,646 | 2,229,677 | 7-24 | 94,070-325,095 | no |
| `\s+$` | t-tail-digits-1m | 1 | 2 (1 call) | 1,776,397 | 1,775,515 | 7-24 | 75,591-261,235 | no |
| `\s+$` | t-tail-txt-1m | 1 | 2 (1 call) | 1,776,333 | 1,776,298 | 7-24 | 75,589-261,225 | no |
| `\s+$` | t-tail-space-1m | 4 | 7 (2 calls) | 1,776,192 | 1,776,046 | 13-42 | 42,290-132,552 | yes |
| `\s+$` | t-trim-nearmiss-16k | 1 | 2 (1 call) | 29,061 | 29,048 | 7-24 | 1,237-4,274 | no |
| `[a-z]+\.txt$` | t-tail-digits-1m | 1 | 2 (1 call) | 2,851,861 | 2,852,071 | 7-24 | 121,356-419,391 | no |
| `[a-z]+\.txt$` | t-tail-txt-1m | 11 | 13 (2 calls) | 2,843,731 | 2,845,820 | 22-66 | 42,763-130,446 | yes |
| `[a-z]+\.txt$` | t-tail-space-1m | 1 | 2 (1 call) | 2,851,656 | 2,851,589 | 7-24 | 121,347-419,361 | no |
| `.*\.txt$` | t-tail-digits-1m | 1 | 2 (1 call) | 209,510 | 209,720 | 7-24 | 8,915-30,810 | no |
| `.*\.txt$` | t-tail-txt-1m | 20 | 23 (2 calls) | 210,015 | 209,873 | 33-98 | 2,143-6,442 | yes |
| `.*\.txt$` | t-tail-space-1m | 1 | 2 (1 call) | 209,706 | 209,810 | 7-24 | 8,924-30,839 | no |

Extra (not requested), the other four patterns on t-trim-nearmiss-16k:

| pattern | body | reverse steps | loads (inst.) | O-91 before, caps ns | before, nocaps ns | predicted ns (low-high) | predicted ratio caps (x) | match |
|---|---|---|---|---|---|---|---|---|
| `\d+$` | t-trim-nearmiss-16k | 1 | 2 (1 call) | 5,821 | 5,838 | 7-24 | 248-856 | no |
| `\w+\z` | t-trim-nearmiss-16k | 2 | 3 (2 calls) | 5,868 | 5,880 | 11-35 | 168-533 | yes |
| `[a-z]+\.txt$` | t-trim-nearmiss-16k | 1 | 2 (1 call) | 230 | 229 | 7-24 | 10-34 | no |
| `.*\.txt$` | t-trim-nearmiss-16k | 1 | 2 (1 call) | 228 | 233 | 7-24 | 10-34 | no |

The same bodies, before pin, by counted subject loads (the WORK of the forward
scan, cross-check only, not a price): `\d+$` 1.069 M, `\w+\z` 1.371 M,
`\s+$` 1.209 M, `[a-z]+\.txt$` 1.189 M, `.*\.txt$` 34,949 (+ an uncounted libc
memchr over the body), and 16,385-16,388 on the 16 KiB near-miss (0 for the
last two, whose required-byte memchr rejects). Over O-91's ns that is
0.69 / 1.64 / 1.47 / 2.40 ns per counted load: the old per-byte rates, which
the AFTER cells replace by a count of at most 23 steps.

## 3. Method

1. **Bodies.** `bench/capability/gen_throughput_subjects.py` (read only) and
   `captext.py` + `pcrecbench/periodic.py` were copied to the scratchpad
   (`worktrees/revpred-scratch`, gitignored) and the bench's own
   `extra_subjects()` re-run there. The sha256 of all eight generated
   subjects match `manifest_throughput.tsv` (checked for the four used:
   `t-tail-digits-1m` 06a2c180..., `t-tail-txt-1m` e1fc06ff...,
   `t-tail-space-1m` 9d6c1908..., `t-trim-nearmiss-16k` 41783dc6...; lengths
   1,048,522 / 1,048,527 / 1,048,522 / 16,385). Each ends: prose line
   `...\n` + tail line (`total 20250614`, `saved to report.txt`,
   `end of file` + 3 spaces); the near-miss is 16 KiB of `\s` bytes + `x`.
2. **Compile.** Worktrees `revpred-a15fb77b`, `revpred-7388f1c0`, `make
   -j16`. Per the bench's `configs.toml` `pcrec-auto` / `pcrec-nocaps`:
   `build/pcrec -p rx -fcomments --features all [--no-captures] -o X.c
   --pattern PAT`. Stamps read from the emitted `#define`s and `.scan` /
   `.search_form` in `rx_info`.
3. **What the bench times.** Throughput regime = `--find-all`
   (adapter.py `measure`; timed.c): `rx_search` from 0, then from the match
   end while it matches, until no match or `pos > len`. So a matching cell
   is TWO calls (the second, from `search_from == n`, does no steps).
4. **Walked bytes, two ways.** (a) Instrumentation: each emitted artifact
   copied, `subject[` rewritten to `(counter++, subject)[`, compiled with a
   find-all driver mirroring timed.c, run on the real bodies: reports spans,
   calls and loads. (b) A Python model from the pattern semantics and the
   body: for a run class (`\d`, `\w`, `\s`) steps = trailing run + the
   dying byte; for `[a-z]+\.txt$` steps = the reversed `.txt` prefix matched
   + 1 on a mismatch, else 4 + the lowercase run + the dying byte; for
   `.*\.txt$` 4 + the last line's length + the `\n` that kills it. Agreement
   is within 3 loads on ALL 20 cells (loads = steps + the end-of-line view
   reads + the range-edge loop's double reads); all 20 cells, not three:
   e.g. `\d+$` x digits: 8 digits + the space = 9 steps, 12 loads over 2
   calls; `[a-z]+\.txt$` x txt: `.txt` + `report` + the space = 11, 13 loads;
   `.*\.txt$` x txt: `.txt` + 15 + `\n` = 20, 23 loads. The spans (and
   match/no-match) of every cell agree with python `re` (`\z` as `\Z`) and
   across both pins.
5. **Price.** Section 4.

## 4. Assumptions and price

`ns = F + rate x steps + extra_calls x C`

- **F, the per-call fixed cost.** Low 5.6 ns: O-91's own floor, the
  immediate-return pcrec cells in the same window on the same 1 MiB and
  16 KiB bodies (`base10num-near-miss` 5.61 ns on `t-tail-*-1m` and
  `t-trim-nearmiss-16k`; a one-compare reject inside the find-all loop on
  the bench's `timed_run`). High 20 ns: that floor + 5 ns because rev-end's
  function is not a one-compare reject (seed loop, state init, a view check
  per position, two returns) + 10 ns for the instrument term. O-91's
  annotation (O-94/O-95): the grown driver added +40-50 ns on 7 of 9 tested
  short-call movers, cell dependent; [B133]'s isolated `timed.c` is meant to
  remove it, and the 5.6 ns floor was itself measured under the grown driver
  and shows no such term, so I do not add 40-50 ns; I add 10 ns to the high
  end as slack and state that a short cell reading above ~60 ns with a flat
  control is the instrument, not rev-end (section 5).
- **rate, per reverse step.** 1.2-3.5 ns. Source: the window's own DFA
  rates on this Ryzen 5 1600: the old forward range/bitmap scans cost
  0.69-2.72 ns per counted load (section 2), the mixed-run subject 3.53
  ns/B; a dependent table step (class load, next-state load, stop test) is
  the same chain. The run loops (`\d+$`'s range edge) run faster than a
  table step; I price all steps at the table rate (conservative).
- **C, an extra call**: 3 ns low, 8 ns high (the second find-all call from
  `n`: call, init, one view check, `return 0`).
- **Not priced:** a cold tail. The harness calibrates to ~50 ms per cell
  (`probe_iterations` then `iterations`, record `calibration`), so tens of
  thousands of iterations re-read the same 1-2 cache lines of the tail:
  L1-hot. A single cold read is ~100 ns once, amortised away.
- **Not a mover:** nothing in this change touches `rx_match*`, only the
  search entry. The forced-VM cells (O-91 d) are untouched by rev-end except
  on VM hybrids with an exact inlined body (stage 2), which none of these
  patterns select (route is `engine=dfa`).

Because the cells are 7-100 ns, the report reads best in ABSOLUTE ns, not
ratio: the ratio is 1/(a few ns) and moves by 3x on a 5 ns layout shift.
Rank the cells on the steps column.

## 5. What would falsify it

- Any tail cell on a 1 MiB body above ~150 ns (or a body-size-dependent AFTER
  value across `t-tail-*-1m`): rev-end did not run in the bench's build
  (artifact stamp `RX_DFA_SCAN` is not `rev-end`), or the artifact was built
  with `-fno-rev-end`; check the stamp first.
- Caps and nocaps differing by more than that spread on a cell: a finisher
  or tie ran on one route only; the artifacts are identical here, so that
  would be a bench build difference.
- A short cell (7-24 ns predicted) reading 40-60 ns while the sentinel set
  (O-95's [B133]) and the pcre2-jit control are flat: an instrument term, not
  pcrec. Read against the sentinels first.
- Ordering: the cells must order by steps (`.*\.txt$` x txt, 20 steps, the
  slowest; `[a-z]+\.txt$` x txt 11; the 1-step no-match cells all equal within
  noise). A no-match cell slower than a matching one of the same pattern
  would falsify the "per-call floor + steps" model.
- `\s+$` x `t-trim-nearmiss-16k` above ~150 ns: the walk did not die at the
  `x`. (`\s+$`'s reverse walk reads 1 byte there, not 16 KiB: if the AFTER
  value scales with the 16 KiB, the build is not rev-end.)

## 6. Draft paragraph for the bench inbox (facts only)

> pcrec predictions for [OPT-REVEND]'s acceptance cells (AFTER pin
> 7388f1c0, abi 73; BEFORE a15fb77b, abi 72; your O-91 values are the
> BEFORE). Every one of the 15 tail cells, auto-caps and auto-nocaps, stamps
> `engine=dfa, RX_DFA_SCAN=rev-end, RX_DFA_START=reverse-pass,
> RX_DFA_PREFILTER=none, RX_DFA_MATCH=unwrapped` at 7388f1c0 (before:
> `unanchored` with `byte-class-bounded`, `memchr-bounded` for
> `.*\.txt$`). The caps and nocaps artifacts are identical but for the
> flags word, so one prediction covers both. The walk reads the tail line
> from the end until the reverse DFA dies: 1 step on the no-match cells, 9
> (`\d+$`, `\w+\z` on digits), 4 (`\w+\z` on txt, `\s+$` on space), 11
> (`[a-z]+\.txt$` on txt), 20 (`.*\.txt$` on txt) steps on the matching
> cells (instrumented loads on your subject bytes, sha-verified against
> manifest_throughput.tsv: 2-23 loads; a model from the pattern semantics
> agrees within 3 on all 20 cells). No anchored re-run (no body ends in a
> newline). Your find-all loop makes a second, step-free call after a match.
> Predicted ns per call, range low-high: no-match cells 7-24; `\w+\z`
> x t-tail-txt, `\s+$` x t-tail-space 13-42; `\d+$` and `\w+\z` x
> t-tail-digits 19-60; `[a-z]+\.txt$` x t-tail-txt 22-66; `.*\.txt$` x
> t-tail-txt 33-98; `\s+$` x t-trim-nearmiss-16k 7-24 (from 29,061). Price =
> 5.6 ns call floor (your own immediate-return cells in the same window)
> + 1.2-3.5 ns per step + 3-8 ns for the second call, with slack for
> instrument terms; predicted ratios 2,100x-420,000x on the 1 MiB cells,
> 1,200x-4,300x on `\s+$` x t-trim-nearmiss-16k. A 1 MiB cell above ~150 ns
> or varying with body size means rev-end did not run; a short cell at 40-60
> ns with flat sentinels is the instrument. Full derivation:
> docs/dev/lanes/revpred_report.md.

## 7. Files and cleanup

Scratch (gitignored): `worktrees/revpred-scratch/` (regenerated subjects,
emitted artifacts, instrumented copies, `inst/run.sh`, `table.py`). Scratch pin
worktrees `revpred-a15fb77b`, `revpred-7388f1c0` (detached, built).
