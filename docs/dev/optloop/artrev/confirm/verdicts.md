# [ARTREV] S4 confirmer verdicts (lane artconf, 2026-10-06)

Reportable timing: ubuntubudu (AMD Ryzen 5 1600, Linux 7.0, gcc 15.2.0 `-O2 -fPIC`, load1 about 0.0-1.3),
11 interleaved rounds, pad-shift layout control at pads 16..112 (7 pads) for orig and every candidate.
Artifacts regenerated at pin 57db5152 (abi 62) with a compiler built AT that sha; all four sha256 equal
`pilot_pins.tsv` before anything else. Verdicts are copied from the harness `summary.txt` (rule: WIN/LOSS only past
max(null deviation, arm IQR, orig IQR, both pad spreads), same sign plain and at EVERY paired pad). Units ns/B, lower is better.
Raw: `raw/<A>_<run>/{raw.tsv,summary.tsv,summary.txt}`; joined tables `confirmed_A01.tsv`, `confirmed_A09.tsv`,
`confirmed_A07.tsv`; identity `identity.tsv` + `idlogs/`.

Runs: pass 1 (no pads, all arms) A01/A09/A07; pass 2 (pads, candidates) A01 `002`, A09 `002`, A07 `002`; A07 pass 2 was
RE-RUN as `003_pass2b` because in `002` the control `orig2` read LOSS (-1.00%) on the dense generality row (CELL row
clean). `003` has orig2/null NOISE on every row of every subject and is the A07 verdict run; all 14 A07 CELL verdicts
agree between `002` and `003` (`confirmed_A07_replicate_run002.tsv`). Timing runs per arm revision: at most 3 (bound met).

## Identity gate (Mac, hardened, plain AND --san)
26 arms x {plain, san} = 52 runs, all PASS. Give-up repairs (orig gives up, twin answers; each oracle-checked vs libpcre2
10.48): A01 0 on all; A09 0 on all (L4 r3, L1 r2 final); A07: a_L1/a_L6/b_L1 0; a_L2/b_L2 5,380; a_L3-L5, b_L3-L6
294,884; `poss` 50,168 (of the original's 294,884 give-ups; the rest give up in both). `--strict-giveup --skip-window`
FAILS for exactly those 10 arms with repairs (`identity.tsv`, mode strict) and passes the rest by construction:
they "change the limits behaviour" (tag `changes-giveup-surface`). Window-start differential on A09: 342,690 windows, 0 diffs.

## A01 loglines_stack_frame (DFA find-all; cell = 12 throughput subjects; orig 0.455 ns/B)
| lead | cell median | vs orig | pad spread / thr | paired | verdict | dense | sparse | repairs |
|---|---|---|---|---|---|---|---|---|
| L1 rare-byte '(' anchor | 0.126 | +0.329 (-72.2%) | 0.041 / 0.056 | 7/7 | WIN | WIN | WIN | 0 |
| L2 memchr 't' | 0.377 | +0.065 (-14.6%) | p1 only | - | NOISE | NOISE | NOISE | 0 |
| L3 backward scan, no reverse DFA | 0.419 | +0.036 (-7.8%) | 0.067 / 0.071 | 5/7 | NOISE | WIN | NOISE | 0 |
| L4 skip first re-skip | 0.479 | -0.037 (+8.4%) | p1 only | - | NOISE | NOISE | NOISE | 0 |
null dev 0.039; orig2 +6.5%, null +8.5% (both NOISE). L2/L4 stopped at pass 1 (NOISE, below threshold). L3 is a dense-only
(regime) win (dense row WIN); the cell verdict is NOISE.

## A09 loglines_level_context (hybrid; cell = 12 subjects; orig 3.060 ns/B; null dev 0.019)
| lead | cell median | vs orig | pad spread / thr | paired | verdict | dense | sparse | repairs |
|---|---|---|---|---|---|---|---|---|
| L1 skip {0,29} with 'O'/'T' memchr streams (r2) | 0.157 | -94.9% | 0.051 / 0.211 | 7/7 | WIN | WIN | WIN | 0 |
| L2 same skip, scalar table loop | 0.739 | -75.9% | 0.115 / 0.231 | 7/7 | WIN | WIN | WIN | 0 |
| L3 after-level exit table | 3.001 | -1.9% | 0.599 / 0.599 | 0/7 | NOISE | WIN (+6.0%) | NOISE | 0 |
| L4 skip VM when window is the answer (r3) | 3.757 | +22.8% slower | 0.635 / 0.635 | 7/7 | LOSS | WIN (+47%) | LOSS | 0 |
| L5 frameless lazy step | 3.029 | -1.0% | 0.113 / 0.211 | 1/7 | NOISE | WIN (+21%) | NOISE | 0 |
| L6 combination (L1 r2+L3+L4 r3+L5) | 0.140 | -95.4% | 0.031 / 0.211 | 7/7 | WIN | WIN | WIN | 0 |
L4 and L5 are regime-dependent: they win on hit-dense subjects and lose or tie on the cell's fail/syslog subjects, where the L1
skip is what matters. L3's pad spread (0.6 ns/B, 20% of orig) says layout alone swings that twin.

## A07 capability_doubled_word (VM+backref; cell = t64k,t256k,t1m; orig 17.39 ns/B; null dev 0.027) -- run 003
| arm | idea | cell median | vs orig | pad spread / thr | paired | verdict | dense | sparse | repairs |
|---|---|---|---|---|---|---|---|---|---|
| poss | hand-possessified `\b(\w++)\b\s++\1\b` | 7.37 | -57.6% | 1.78 / 1.78 | 7/7 | WIN | WIN | WIN | 50,168 |
| a_L1 | word-start filter | 13.50 | -22.3% | 0.64 / 0.90 | 7/7 | WIN | WIN | WIN | 0 |
| a_L2 | drop give-back frames | 11.34 | -34.8% | 1.06 / 1.06 | 7/7 | WIN | WIN | WIN | 5,380 |
| a_L3 | straight-line attempt | 8.54 | -50.9% | 1.68 / 1.68 | 7/7 | WIN | WIN | WIN | 294,884 |
| a_L4 | fused search (L1+L3) | 3.48 | -80.0% | 0.74 / 1.11 | 7/7 | WIN | WIN | WIN | 294,884 |
| a_L5 | + 256-byte table | 2.89 | -83.4% | 1.15 / 1.38 | 7/7 | WIN | WIN | WIN | 294,884 |
| a_L6 | counters in locals | 17.39 | -0.05% | 0.25 / 0.52 | 0/7 | NOISE | WIN (+2.5%) | WIN (+1.9%) | 0 |
| b_L1 | word-start filter | 13.40 | -22.9% | 0.93 / 0.93 | 7/7 | WIN | WIN | WIN | 0 |
| b_L2 | delete give-back frames | 11.24 | -35.4% | 1.14 / 1.23 | 7/7 | WIN | WIN | WIN | 5,380 |
| b_L3 | + plain RX_SET stores | 10.15 | -41.6% | 1.35 / 1.35 | 7/7 | WIN | WIN | WIN | 294,884 |
| b_L4 | L1+L2+L3 + inline | 5.10 | -70.7% | 0.53 / 0.53 | 7/7 | WIN | WIN | WIN | 294,884 |
| b_L5 | + restart past dead spans | 4.57 | -73.7% | 0.68 / 0.68 | 7/7 | WIN | WIN | WIN | 294,884 |
| b_L6 | + 256-byte tables | 4.48 | -74.2% | 0.78 / 0.78 | 7/7 | WIN | WIN | WIN | 294,884 |
The "a_L6 NOISE on the cell" reading: its ~2% effect is consistent in sign on dense, sparse and t1m but t64k (noisy: pad spread
3.8 ns/B) keeps the cell median inside the threshold. Stacked arms are verdicts of the stack vs orig; the increment of the last
member (e.g. tables on top of a_L4: 3.48 -> 2.89) was not isolated by a separate arm (no single-member arms were asked for except
a_L1-L3/b_L1-L3). `poss` (the SHIPPED emitter, pin compiler, `RX_VM_FRAMELESS 1`, `RX_VM_ENTRY_SHAPE "inline"`, zero `RX_PUSH`
uses) equals about b_L2+inline in effect, between b_L3 and b_L4.

## Scratch vs confirmed
Only rvA07b timed anything on the Mac (scratch, -20/-45/-53/-72% for L1-L4 cumulative). Linux: b_L1 -22.9%, b_L2 -35.4%,
b_L3 -41.6%, b_L4 -70.7%: same verdict (WIN) on 4/4, magnitudes smaller for L2/L3 (-45/-53 scratch). Agreement of the lane's
scratch verdict with the confirmed one: 4 of 4 (A07b); no scratch verdicts existed for the other 22 leads.

## Harness findings (for artcollect's plan)
1. `confirm_plan.md` section 1 exports `ARTREV_REMOTE_CC=gcc` for the whole session, but `common.py` uses it for LOCAL
   compiles too (shrunk-budget rebuild): on the Mac `gcc` is clang and the A07/A09 identity runs failed with "indirect goto".
   Unset it for identity, export it only for `time` (all 52 identity runs were done that way; a first batch that failed
   was discarded and re-run entirely).
2. `time`'s `summary.tsv` omits the layout columns; `studies/artrev/confirm_collect.py` (new, this lane) reads `summary.txt`.
3. Whole confirmation took about 21 min of box wall (7 timing runs), not the planned 1 h 15.
