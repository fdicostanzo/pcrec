# EXECUTIVE SUMMARY — the optimization loop, cycle 2 batch 2 (2026-09-23)

For Frank. Batch 2 landed two mechanisms — [OPT-FREQPICK] (the necessary
byte picked by argmin over the shipped byte-frequency prior) and
[OPT-REQPOS] tier 2b (the necessary literal run) — as one `abi` 29→30
event, parked on `lane/optimpl2`. The bench's after-measurement (O-49) is
read against the D119 bar in
`docs/dev/optloop/cycle2_batch2_reading.md`; a follow-on Linux
measurement (O-50) answers a question left over from batch 1. Numbers
cite that reading's sections.

## 1. FINDINGS

| mechanism | target | before → after (absolute) | D119 verdict | defect found | disposition |
|---|---|---|---|---|---|
| **[OPT-FREQPICK]** | `nested-comment-rec`, thr, 4/4 configs | 9.28–9.75 ms → 23,118–23,152 ns, predicted **23,113 ns** (§4.4) | **MEETS** | `wild-validator-email-owasp`: **+27,010% to +52,757%** — the pick moves to an ABSENT byte on a ONE-ATTEMPT artifact, an effect the design note itself classified as a gain (§4.2) | DEFAULT-ON, and a PRECONDITION on `[OPT-PRECHECK-ADMIT]` merging |
| **[OPT-REQPOS] tier 2b** | `wild-secrets-github-pat`, thr, vm-caps/vm-in-caps | 5.39–5.86 ms → 125,586–129,145 ns, predicted **~125,300 ns** (§4.4) — 2/4 MEET; the DFA route's +3.3%/+3.8% sits inside the null band | **targets MEET, carve-out clause FAILS** | `router-prefix-order` / `keyword-prefix-order`: the run loop costs one `memchr` CALL per occurrence of its SCAN BYTE, not of the run — **124× and 4.7×** call amplification, **+80.83% and +59.7%** (§4.1, §4.3) | DEFAULT-ON WITH THE ADMISSION FIX; open a cycle-3 row for the run-form dominance rule |

Of I-95's 17 missing target rows (§3): **6 are removed outright** by the
already-built but unmerged admission fix (`[OPT-PRECHECK-ADMIT]`, lane
`admitimpl`, `cb437f26`, abi 31); **6 are the run mechanism's own
defect** the fix does not reach; **5 were already at the measurement
floor** before the batch started and could not have improved (both
bytes of `</` occur zero times in the subject — the design note lists
these as carve-outs, never targets). Only **2 of the 17** lie outside
this pin pair's own null band, and both are `router-prefix-order`'s DFA
route.

O-50 (§6a), a follow-on Linux measurement on `nested-comment-rec` at the
batch-1 pin, confirms the pre-check itself was a real cost there
(−15.35% on deletion) but that moving it to the entry wrappers (G3, the
placement mechanism batch 1 left open) does not recover the deletion's
full gain — **G3 placement is retired for good**. The question is moot
at the batch-2 pin regardless: the frequency pick already moves this
pattern's byte to `*`, collapsing the artifact to the floor on its own,
and the fix keeps the win.

## 2. SURPRISES

Three, each a prediction whose sign or scope was wrong before any
measurement (§9).

**A. The ledger's largest movement was predicted backwards.**
`wild-validator-email-owasp`'s +27,010%..+52,757% floor jump is a cell
the design note lists among effects that "are gains" — it read an
absent required byte as a one-pass answer without asking whether the
artifact had an attempt loop to skip. On a ONE-ATTEMPT artifact, absent
is the worst case, not the best: the whole-window scan replaces an exit
that was already O(1) (§4.2).

**B. The named falsifier was confounded, and its sign is not
informative.** `logparse-atomic` was chosen to test the no-decline-rule
question, but it is `^`-anchored, so the admission fix deletes its
ENTIRE pre-check — the cell chosen to answer the run-rate question has
no run check left to have a rate about. Its largest regression (+41.82%
on a 49 ns baseline) is numerically indistinguishable from a
program-identical null cell of the same size (+41.09% on 52 ns). The
cell that can actually answer the question, `keyword-prefix-order`
(+59.7%, the ledger's largest carve-out regression), was never named
(§4.3).

**C. The admission fix's own scoping inverts the cost it was built to
avoid.** G1's one-byte dominance rule — sound on its own reasoning —
declines the CHEAP form of `router-prefix-order`'s pre-check (315
`memchr` calls) and admits the EXPENSIVE form (39,098 calls). The same
comparison on `keyword-prefix-order` is 9,470 against 44,135 (§6).

## 3. IMPACT

The run scan loop costs one `memchr` CALL per occurrence of its SCAN
BYTE, not of the run, which the design note prices the other way; on
`router-prefix-order` that is a 124× call amplification and **97% of a
+80.8% regression**, reproduced by an exact clock-free model with one
free parameter (7.72 ns/call) carried unchanged from cycle 1 (§4.1).

Cycle 1's free null control is larger this cycle: **131 of 192
artifact-configs are program-identical** across the pin, and **34 of 34
named non-target regressions sit on them**, one at +41.09% — for the
second cycle running, the within-window IQR is the wrong noise model
for a two-window comparison (§1).

**Recommended dispositions, yours to rule (§7):** `[OPT-FREQPICK]`
**default-on**, a precondition on `[OPT-PRECHECK-ADMIT]` merging (it
carries the +52,757% hazard until the fix lands). `[OPT-REQPOS]` tier
2b **default-on with the admission fix**, plus a cycle-3 row for the
run-form dominance rule. The no-decline-rule question is **NOT
answered** by this ledger — its named falsifier is confounded and the
cell that could resolve it was never measured; do not treat the trigger
as fired. A `--tune` position remains the wrong instrument for either
mechanism: the losses are an admission defect with a named predicate,
not a size/speed trade.

## 4. NEXT STEPS

**Merge `[OPT-PRECHECK-ADMIT]`** — a precondition on shipping the pick,
not an improvement on it.

**Open a cycle-3 row for the run-form dominance rule.** Its statistic
compares two counts the compiler already holds (the prefilter's own
scan-byte occurrence count against the pre-check's), not a corpus rate;
not built here (D77, §6).

**Send I-102, I-103, I-104 to the bench (§8):**

| ask | asks for |
|---|---|
| I-102 | the admission fix's acceptance cells, extended by batch 2, with the six meeting targets carried as explicit no-move controls |
| I-103 | the one three-artifact timing block that decides the run-form dominance rule — no new pcrec build needed, both axes already ship |
| I-104 | a standing null-control band in every capability report, with this lane's own population offered to the bench |

**A process lesson on how targets get named in inbox asks.** Two
discrepancies between I-95's ask and the design notes it cites:
`tag-depth3-bound`/`tag-pair-match` were **carve-outs** in
`reqpos_2b.md` §6.2 ("both bytes of `</` are ABSENT... their whole-call
answer is already won"), not targets — promoting them cost five of the
seventeen misses on rows the design never claimed and could not have
won (§4.5). And the phrase **"the pick's one losing cell,"** applied to
`nested-comment-rec` in I-95's prose, appears in NEITHER design note —
both name it among "the largest gain this note can claim" (§4.4). An
ask that restates a design note's own target/carve-out classification,
rather than re-deriving it, would not have produced either misreading.
