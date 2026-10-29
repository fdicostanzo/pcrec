# p10model — a cost model of P10's deferred presence check

STATE: done (arithmetic only; no compile, no box load). Model: `docs/dev/lanes/p10model_evidence/model.py`
(`python3 -I model.py`, stdlib, ~1 s); its full output: `p10model_evidence/model_out.txt`. Every
number below is read from that output. Source of the twin numbers: `docs/dev/lanes/p910_report.md`
("P10 stamps and twin", "P10 design"); the adaptive record: `docs/design/memfn/walk_vs_v1_record.md`.

## Summary

1. **Calibration holds, so the stop rule did not fire.** Of 12 twin rows (3 variants each) the
   model reproduces `today` to <1% (it is `a*L + F`), `pre` and `paced` to within 8% on 10 rows.
   Worst misses: `email t-hyb-digits-4k` pre -25.5% / paced -12.8% (the measured 4 KiB `pre` is 135
   instructions above `m*n`; unexplained, flagged), `iso trim-nearmiss-16k` pre -9.8%. One row is
   NOT reproduced: `iso` witness A (30,000 whitespace, 1 MiB absent): measured paced = today
   (x1.00), model x0.94-1.06 of today... i.e. the model predicts a check cost the twin did not pay
   (the whitespace run is probably a stay/scan edge that the "table steps only" counting rule
   never counts; the model has no such notion). That row is carried as an OUTLIER, not hidden.
   The cycle-only hazard gains: iso model x48.1 vs measured x49.1; email model x33.2 vs measured
   x27.2 (C and F in cycles are UNMEASURED guesses, 20 and 40). The codegen multipliers
   (g_pre 1.25, g_paced 1.375 on email; 1.05 on iso) and the per-route F are FITTED to the `witness
   C` and prose rows, so those rows are not independent checks; the hazard, nearmiss, 1 MiB and
   digits rows are.
2. **Worst case (cycles, n >= 4096, ratio to the hindsight best of {today, pre}; one call):**
   today x69 (email) / x195 (iso) [the hazard]; pre x998 [1 MiB, byte at the end]; paced K=6,
   D0=16 x2.08 / x4.04; K=7 x2.84 / x2.52; K=8 x4.67 / x2.31; derived (below) x2.00 / x2.00;
   online-doubling x2.19 / x2.55. Against `today` (the G3 bar): paced K=6 x1.92 / x1.36 in cycles,
   x2.13 / x1.72 in INSTRUCTIONS (the codegen term is most of it). The worst input for paced is
   always the same shape: byte present only at the very end (or absent), attempt alive just past
   the checkpoint (`L = (n-s)>>K + 1`).
3. **The constants are derivable by one rule, and 16/6 are not it.** Pay-as-spent: run the check
   when the attempt has spent what the check would cost, `b = floor((C + m*R) / (a*g))`, R = n-s.
   It yields K = round(log2(a*g/m)) = 6 for email (r = 69), 8 for iso (r = 195), and D0 = C/(a*g)
   (3-8 steps at C = 20 cycles, UNMEASURED; 1 step in instructions). A single K=6 is 2.1x worst on
   email but 4.0x on iso. See "The constants derived".
4. **D0 = 16 is the more expensive constant on real-sized subjects, not K.** Line-per-call text
   (70-110 B lines) is dominated by the attempt's fixed cost F, and check-first wins there
   (twin measurement agrees: shorts sum auto 13,374 / pre 9,144 / paced 12,843). Model, prose
   lines, ratio to hindsight (instr/email): today 9.5, paced K6 9.4, derived 2.2, pre 1.03.
5. **Find-all memory** removes the repeated scans (retry loop with byte absent: 2.8x -> 0.01x of
   per-call hindsight) but needs caller- or artifact-held state that does not exist (match_api.md
   §5.2¶6) and a subject-identity reset. Recommendation: not now.
6. **Streaming:** `rest>>K` and "absent -> no match" are both WRONG with unknown n (a wrong answer,
   not a slowdown, in the model: byte at 600,000, attempt would match, B = 4 KiB or 64 KiB). The
   safe form never rejects before the final chunk; the benefit with unknown n is exactly zero
   (hazard x69.4 -> x69.5) at +0.8% overhead. State the rule over the call's declared window now.
7. **Adaptive record:** P10 avoids (2) and (5) and is exposed to (1)/(3) only through the codegen
   term and through hardware drift in r; (4) is unmeasured here. Section "Lessons".

## The model

Units are whatever the rates are in; four parameter sets (`ROUTES`): instructions and cycles, for
the email (DFA attempt) and iso8601 (hybrid prefilter attempt) routes.

| symbol | meaning | source |
|---|---|---|
| a | attempt cost per generic table step | 8.0 / 9.0 instr; 2.64 / 7.4 cycles (p910) |
| m | memchr cost per byte | 0.0945 instr (fits `pre` on 60 KiB and 1 MiB); 0.038 cycles |
| C | memchr call cost (fixed) | 7 instr (fits `pre` on 60 KiB); 20 cycles UNMEASURED |
| F | attempt fixed cost when it runs to its own end | 112 / 146 instr (the prose rows); 40 cycles UNMEASURED |
| g_pre, g_paced | codegen multiplier on the attempt loop, a SEPARATE term | 1.25 / 1.375 email, 1.05 iso (instr); 1.0 in cycles ("0% cycles" in p910) |

A call is (start s, length n, attempt depth L, matched, p = first required byte >= s or None).
Strategies: `today` = F + a L; `pre` = C + m*scan, then (if present) F + g_pre a L; `paced(b)` =
the attempt for b steps, then once C + m*scan, absent -> stop, present -> rest at a g_paced;
`b` = max(D0, R>>K) or the derived formula; `+mem` (find-all memory); `online` = geometric
checks at D0*2^j scanning the next c*r bytes each (frontier kept, each byte scanned once).
Hindsight optimum per call = min(today, pre) when the byte is absent, else today. Answer
identity is by construction (an absent byte proves no match; the attempt would die).

## Scenarios

Calibration table: `model_out.txt` first block (`== CALIBRATION`). Sweep (`== SWEEP`): n in
{32 .. 1 MiB} x p in {absent, 0, 4, n/100, n/2, n-1} x 20 attempt depths around every candidate
checkpoint x matched/not: 8 sizes, 4 parameter sets.

Worst ratios, one call (cycles; `vs opt` is n >= 4096, `vs opt all n` includes 32..1024):

| strategy | email vs opt | iso vs opt | email vs today | iso vs today | vs opt, all n (email / iso) |
|---|---:|---:|---:|---:|---:|
| paced K5 D0=16 | 3.17 | 7.08 | 1.46 | 1.18 | 3.88 / 7.47 |
| paced K6 D0=16 | 2.08 | 4.04 | 1.92 | 1.36 | 3.88 / 7.47 |
| paced K7 | 2.84 | 2.52 | 2.84 | 1.66 | 3.88 / 7.47 |
| paced K8 | 4.67 | 2.31 | 4.67 | 2.31 | 4.67 / 7.47 |
| paced K6 D0=64 | 2.08 | 4.04 | 1.92 | 1.34 | 9.32 / 22.9 |
| derived | 2.00 | 2.00 | 1.92 | 1.66 | 2.88 / 2.58 |
| online (D0=16) | 2.19 | 2.55 | 2.10 | 2.03 | 3.88 / 7.47 |

In instructions (the codegen term included): paced K6 x2.82 / x2.57 vs opt, x2.13 / x1.72 vs
today (worst at `n=1 MiB, p=n-1, L=16385`); on short subjects the instruction ratio vs hindsight
is x28.7 / x29.7 at `n=32, L=16, absent` (`pre` rejects at 10 instructions, `paced` first runs
16 steps and F). That is the short-subject cost of D0, and derived D0 cuts it to x9.4 / x15.5.

Real-text-like (line per call, n ~ Exp(mean 70 / 110 / 40) for prose / logs / code; attempt
depth Exp(6 / 25 / 12), 2% / 15% / 10% survive the line; byte on 3% / 60% / 85% of lines),
total over 2,000 calls, ratio to per-call hindsight, instr/email (cyc/email in brackets):

| kind | today | pre | paced K6 | derived |
|---|---:|---:|---:|---:|
| prose | 9.5 (2.4) | 1.03 (1.03) | 9.4 (2.2) | 2.2 (2.0) |
| logs | 1.68 (1.46) | 1.20 (1.15) | 1.58 (1.24) | 1.31 (1.21) |
| code | 1.16 (1.13) | 1.16 (1.27) | 1.33 (1.15) | 1.22 (1.20) |

The losses are on dense, predictable text, exactly where the adaptive record put them: on code
lines `paced` is +15% over today in INSTRUCTIONS (codegen term g = 1.375 on every step plus a
check on lines where the byte is present) and about +2% in cycles; derived is +7% over today in
cycles on code because it checks at entry and C and F are unmeasured guesses. Whole 1 MiB
buffers (one call): prose / log with the attempt dying early cost paced x1.14 / x1.30 of today
(instr); the hazard x2.82 of opt (x84.7 for today).

Sensitivity of the bound to the machine: paced K6, attempt dying just past the checkpoint, byte
absent, vs today: x1.92 as measured, x2.84 with memchr twice as slow per byte, x4.68 at four
times (a Zen 1 2x128-bit memchr on small buffers may be near the first). The bound is
`1 + 2^K/r`, so it is a statement about this box's `r`, not about the algorithm.

## The constants derived

Rule: the check is worth running when the attempt has already spent what the check will cost.
`b = floor((C + m*R)/(a*g))` bytes of attempt. In the large-R limit this is `R/r` with
`r = a*g/m`; for small R it is `C/(a*g)`. Ski-rental: the worst case vs hindsight is 2 (the
`n>=4096` rows of "derived": 2.00), which is also the lower bound for any deterministic schedule.

- **K**: power-of-two approximation of r: email r = 69.5 -> K = 6 (6.1); iso r = 195 -> K = 8
  (7.6). Fixed K = 6 on iso is x4.04 vs hindsight (x1.36 vs today); K = 7 x2.52; K = 8 x2.31. The
  K = 5 vs 6 question of p910 §6 is answered by r, per route; selflip's r = 53 gives K = 6 too
  (log2 53 = 5.7). Rule: `K = round(log2 r)`, route-stamped, derived from rates that are
  measured data (measure_store shape, D166), not limits.def.
- **D0**: `C/(a*g)`: with C = 20 cycles (UNMEASURED) email 7.6 steps, iso 2.7; at C = 120 cycles
  45 / 16 steps. In instructions C = 7 gives < 1 step (then `b = 0` below R ~ 40 bytes, i.e.
  check first). So 16 is neither measured nor derived: it sits inside the unmeasured range and
  two bench routes disagree by 3x. A per-call-site cost card (one measured memchr call on 1-64
  byte windows) is the missing datum; the model flags C and F as the controlling UNMEASURED
  inputs of every short-subject number here.
- The rule is the fixed formula, not an estimator: R is the declared window, a/m/C/g are stamped
  constants.

## Find-all memory

Scenarios (`== FIND-ALL`, instr/email, ratio to per-call hindsight; < 1 beats the stateless
optimum): retry loop (caller emulates an unanchored search with the anchored attempt, byte absent,
attempt dies just past each call's bound): paced 2.8, derived 2.0, with memory 0.01 (one scan
answers every later start; it proves absence from the first scanned start s0 for all s >= s0).
Tail of a subject (rest small, D0 floor, 1,000 calls of 30 steps): paced 3.4 -> with memory 0.03.
Remembered presence (byte at 1990, 90 starts before it, attempts of 40): 1.63 -> 1.29. Tokenizer
with the byte inside every match, dense byte, short attempts: no change (1.18-1.22: memory does not
help, the check never fires). So memory removes repeated scans only for call sequences with
repeated starts before one proof point; it never helps the single-call hazard.
Costs: two words of state (absent_from, found_pos) plus a subject identity (pointer, n) to reset
on, held by the caller or in a context object; pcrec has none (match_api.md §5.2¶6), and a state
reused with a different subject is a WRONG ANSWER, a stronger failure than the record's stranded
mode. The model charges 2 units per call. Per-call stateless P10 is already bounded; the
sequence worst case multiplies it by the number of calls but each call stays <= x2 of its own
hindsight, so the memory is an optimization of a bounded cost, not a bound.

## Streaming

Model (`== STREAMING`, cyc/email, n = 1 MiB, chunk B in {4 KiB, 64 KiB, 1 MiB}; the attempt can
read only buffered bytes; absence in the buffer is not proof):

- **naive paced** (R := buffered length, absent -> no match): "hazard" rejects at the first chunk
  (right answer by luck); the case byte at 600,000 and a match at 600,001 returns no match: a
  WRONG ANSWER at B = 4 KiB and 64 KiB. `rest>>K` shrinks with the buffer so D0 floors the
  bound and the check fires per chunk, and "absent -> no match" turns a necessary condition
  into a verdict on data not yet seen.
- **safe paced** (same checkpoint, reject only if the scanned window reaches the final chunk):
  correct; hazard x69.5 vs today x69.4 (no benefit, n unknown), dies-at-5000 x1.19 at B = 64 KiB.
- **online doubling** (check at consumed c = D0*2^j, scan up to c*r bytes from a kept frontier,
  each byte once, reject only on a final-chunk proof): hazard x70.0 (+0.8% over today), prose
  x1.00, worst over L at B = 64 KiB x2.08 of today (at L = 65). With the whole subject buffered
  (B = 1 MiB) it matches paced: hazard x2.09 vs x2.08. For known n it is a near-duplicate of
  paced (same result within 1% on the hazard), so only the streaming entry needs it.
- Information-theoretic floor: with n unknown, no schedule can reject a long absent subject
  before the end arrives; the check only buys something when a lookahead buffer holds the final
  chunk.

What P10 should state NOW so a later streaming entry does not inherit a wrong rule: (1) the
checkpoint is a function of the remaining length of the DECLARED subject window of one call, never
of a buffer; (2) "absent from [start, end) -> no match" is valid only because that window is the
whole remaining subject, which §5.2¶6 already says (no window state); (3) the stamp says the
check is a pure function of (start, n, stamped rates), carries no state across calls, and stays
exact; (4) a streaming entry derives its own schedule keyed to consumed bytes and rejects only
on an end-of-stream proof.

## Lessons from the adaptive record

P10's claim "never switches, estimates nothing, one exact test at a formula-fixed point":
- Survives: no mode switch (the attempt always continues), one exact necessary-condition test,
  no run-time observation of the subject. Every scenario above kept answers identical.
- Does not fully survive: "estimates nothing". The bound depends on stamped rates (`r`); the
  worst case moves with the box (x1.92 -> x2.84 at memchr 2x slower). That is a compile-time
  estimate of hardware, not an adaptive one, but it makes the guarantee conditional on the card.

Per failure:
1. *Free observation / standalone mode costs.* The analogue is the codegen term: the loop with
   the checkpoint is not today's loop (8.0 -> 11.1 instr/B, 0% cycles on this box). The model
   carries it as g and shows it dominates the instruction-level worst case (x2.13 vs today) and
   the code-line loss (+15% instructions). EXPOSED, mitigated only by the build gate.
2. *Mode carried across calls.* Stateless P10: not exposed. `+mem` IS exposed (stale state on a
   new subject = wrong answer). Do not build `+mem` without a reset rule.
3. *The deciding property is unknown at compile time and losses are on dense predictable text.*
   EXPOSED in the same shape: real-text rows show the loss on code/log lines. Bounded (<= ~x1.15
   cycles on the modelled text), not zero.
4. *Size.* NOT MEASURED here (no compiles). The record's per-KB test is open: the checkpoint is
   a counter, a compare and one cold call per admitted artifact; the card must measure bytes.
5. *Near-duplicates.* paced vs derived differ only in constants; online equals paced for known
   n. Keep one row; do not carry `online` until streaming exists.

Generalization (candidates only, no deep dive): the schedule "exact cheap test vs carry on,
check when the attempt's spend equals the check's cost" applies wherever a necessary condition
can be tested in O(R) at memchr-like cost against an attempt of unknown depth: (a) a required
literal RUN (memmem, `_REQ_RUN`) instead of a byte; (b) a required byte SET / the rarest of
several necessary bytes; (c) the end-anchored case: a required last byte or suffix at `n-1`
(O(1), check-first always, no schedule needed); (d) the minimum-length test `n-s < minlen` (O(1),
always first); (e) the hybrid prefilter's own verify before a DFA locate; (f) find-all
"next candidate exists" before restarting an unanchored scan. Only (a), (b), (e) have a
rate-ratio schedule; (c) and (d) are exact O(1) and need none. Exposure to the record: same as
P10: rates stamped, no switch; each needs its own r from a card.

## Questions

1. D0: the model cannot choose 16 vs ~8 vs derived without the memchr call cost C in cycles on
   1-64 byte windows and the attempt's fixed cost F; this is a one-card measurement (single
   process, no sweep). File it on the P10 card, or accept 16 labelled UNMEASURED DEFAULT?
2. K per route (6 email, 8 iso) vs one K: the model prefers per-route; is a route-stamped rate
   in measure_store acceptable, or one K = 7 (email x2.84, iso x2.52, never worse than x2.9)?
3. Is the "iso witness A" mismatch (paced = today although the attempt outlives the bound) worth
   a lane? It suggests the checkpoint counts table steps only and the stay-run bytes are free.
4. Streaming: agree to state items (1)-(4) of "Streaming" in the P10 design and spec stamp text now?
