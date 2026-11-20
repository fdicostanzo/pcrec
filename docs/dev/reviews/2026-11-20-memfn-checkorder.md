# Critic round memfn-checkorder (design, LIGHT), 2026-11-20

Subject: the checkorder timing spike (NOT yet run) under /var/tmp/pcrec-pcrec/scratch/memfn/checkorder/ (decision_rule.md/.body,
spike.py, diffs/, check/sabotage/dry/build/smoke outputs, work/count.json) and box-queue job fcards/jobs/711-kit-checkorder +
common.sh. Frozen 10:25 (92 files, sha256 list in .coord/freeze.sha256; re-verified unchanged at 10:32). Build tree: worktrees/
bconf-night @ f8789cd2e (= main HEAD at freeze and at hand-back). Rulings frozen at decisions.md/plan.md commit 85c5f28e4; no
FREEZE DRIFT at hand-back. Rule sha 74271f120f96b995.

## Lenses as run

| lens | model | one question | why |
|---|---|---|---|
| soundness | opus | answer + bounds safety of REV/REVMEM/ALT/RANK as emitted; can check/sabotage fail on those paths (+ standing sibling/general-form question) | the arms rewrite emitted C; launcher's question 1 |
| rulefair (simulate + measurement) | opus | does write_decision read the frozen rule (drilled on constructed outcomes); are the regimes fair to FRONT | launcher's questions 2 and 3 |
| readiness | sonnet | will the job start (dry run < 30 s at START) and finish cleanly | launcher's question 4 |

All three complete in 4-7 min; files in review/.

## Findings and PROPOSED dispositions

FIX-BEFORE-TIMING (the run would answer a different question than the one asked):

- RULE-1 (rulefair; coordinator-verified PARTLY: mechanism by reading cards.py subject() + count.json, mirror counts are the
  critic's): the near-miss set that ALONE decides CANDIDATE is tilted to reverse order. The cards' near-miss puts the miss at
  the LAST position (cards.py ~l.359, "first k-1 positions, then a byte outside the last set"): worst case for FRONT on scan
  sites (co_dig12 near-miss: FRONT 5.5 chk/B, 0.917 win/B vs REV 0.083/0.083, verified in count.json) and N/A on the window
  sites where the mirror would hurt REV. One-class nm-dXX place several misses per window (RULE-3), FRONT meets the first, REV
  the last. Count-dominance: REV in 95/102 live near-miss cells, REVMEM 82/82. The mirror (miss at the lowest verify position,
  e.g. one-class "##"+m^(W-1)) gives FRONT 7x-64x fewer checks (hex8/16/64, word32, vowel12) and is in no regime, so neither
  the majority nor the LOSS clause can see it. Proposed fix: add a head-miss regime (one-class mirrored near-miss; mixed
  nm-d0/nm-d100) to NEAR, re-build/check, re-freeze the rule body + RULE_SHA before queueing. Alternative if the manager rules
  the set stays: RECORD-ONLY, and decision.md must state the tilt.
- RULE-2 (rulefair; coordinator-verified: co_dig12 near-miss ALT counts == REV counts; FRONT scan resume is `rxa_mf1_c++`):
  every non-FRONT arm changes ORDER and RESUME together; ALT (the "control expected to lose") gets the same jump and
  count-dominates FRONT in 72/102 near-miss cells. A REV CANDIDATE could not be attributed to order. Proposed fix: one more
  arm, ascending order with render()'s existing shift_j resume (shift_j is order-independent), compared with FRONT under the
  same rule; or RECORD-ONLY with the decision worded "failure-informed jump + order", not "order". This is a question-scope
  call for the manager/owner (slug check-order): if the owner asked about ORDER, it is FIX-BEFORE-TIMING.
- READY-1 (readiness; coordinator-verified: no late_gate in 711 or its body): STOP_AT 07:00 is checked only in --ready; if 710
  ends near 07:00, 711 starts and runs ~57 min (cap allows to ~09:00) into the day. Proposed: copy 710's body late gate (start
  refused when now + est > 07:00). Cheap; FIX-BEFORE-TIMING because the box is shared by day.

RECORD-ONLY:

- SOUND-1: REVMEM's guard is "every shift constant", not "one class"; on a nested-class mixed site (hypothetical
  `\d{4}[0-9a-f]{4}`) REVMEM is unsound (hand-executed false match). Unreachable here (REVMEM only on ARMS_ONE). Any later
  reuse must guard on C_k ⊆ C_{k-d}.
- SOUND-2: the "mem" sabotage row (lo+1) witnesses a never-checked lowest position, not the carried memory; the critic's
  ke+1 over-claim and stale-memory plants ARE caught by check (fuzz0-3). Swap or add the row (one line) if spike.py is
  re-pinned anyway for RULE-1/2.
- SOUND-3: all resume-sabotage catches come from the four fuzz seeds (plus short-subject); no timed regime catches one. Doc.
- SOUND-4: at8/uuid13 REV/RANK pay a 256-entry table whose answer is the constant j+1 (the bad-character shift ignores the
  known probe literal): a small handicap for the arm; the arms measure a floor of the resume idea. Caveat line.
- SOUND-5: BOUNDS argued (held by reading every arm text) but unchecked by the gate (one malloc'd buffer; no ASan). Doc.
- RULE-3: one-class nm-dXX are not "failing depths" (several misses per window). Caveat wording (feeds RULE-1).
- RULE-4: the pooled majority is 82 one-class vs 20 mixed cells; print W/T/L per site kind beside the verdict.
- RULE-5: a missing FRONT row silently drops cells (unreachable in the full run; subset runs look like full verdicts).
- RULE-6: a missing count.json key reads as live, not N/A (dry refuses it; decide does not).
- RULE-7: rerows=None prints an un-retimed LOSS as "repeated" (unreachable from measure/decide).
- RULE-8: rule_ok hashes the body only; the md's own rule text is unhashed; decide skips rule_ok.
- READY-2: wait_quiet and mkdir failures exit without the DONE rc=1 line (still a red job).
- READY-3: results.tsv is written only at the end; one perf failure loses the run's table (log keeps the per-rep lines).
- READY-4: any spike.py fix (RULE-1/2, SOUND-2) voids check.pass and RULE_SHA by design: re-run build + check and re-pin
  BEFORE queueing, or the START dry run refuses.
- READY-5: 711 waits on 710; if 710 is never queued, 711 exits 77 at 07:00 silently; keep bconf-night (not wtpruned) until
  711 ends.
- READY-6: no HEAD pin on the tree (binary shas pinned instead); harmless.

## PROBED-AND-HELD (summary; details in each critic file)
- Answer safety of every arm: exhaustive short-record gates (262k-524k records per pattern, every arm v0) all GATE ok; resume
  shift argument and REVMEM absolute memory across probe skips, scan skips, search_from and restarts held; bounds held by reading.
- 44 extra sabotage plants: all non-equivalent ones caught by check.
- write_decision vs the rule text: median/spread over 3 variants, floor, classify boundaries, re-time population, strict pooled
  majority, N/A: 17 constructed-outcome drills, all as the rule says; no per-cell picking.
- Job start: dry run 0.8-0.94 s vs 25 s gnutimeout vs 30 s runner bound; writes nothing but a gitignored __pycache__ in the
  frozen tree; helpers, CPU pin (15), expect regexes, exit codes, disk all held.

## Lessons for the guide
- A timing spike that compares a changed ORDER needs an arm that changes only the order (RULE-2); a "control" arm that shares
  the treatment's other change controls nothing. Candidate addition to the simulate/measurement lens: "for every arm, list
  every axis it changes vs the reference; a verdict attributes only to an axis some arm isolates" (cf. apples-to-apples memory).
- A verdict population built from one inherited regime shape needs its mirror (RULE-1): ask "where should the reference win,
  and is that in the deciding set?"
