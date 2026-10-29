# process.md: critic round inline-c (design), coordinator log

- 11:59 coordinator start. Subject frozen: docs/design/inline_c.md at c7522390e
  (blob 89d919bc, identical at e84db280c/362edc976/HEAD 8f4fd7631; `git log -1 -- file`
  returns the WIP commit c7522390e because the later commits did not touch the blob).
- Blinding leak (coordinator): while locating the [INLINE-C] plan row to deny it, a
  `sed -n 228,232p` plus a grep hit printed the denied 2026-10-26 manager-rulings note
  (plan.md (line cited at freeze)). Content: agrees with the note's own 10a recommendations. Not passed to
  any brief. Lesson: the launcher should give the denied range as a line range or the
  coordinator should grep only for the tag line number, never print neighbours.
- Profile: new mechanisms/tables (binding rows, return-table rows, verify eligibility,
  trust rules, tag grammar/end scanner); a caller-facing contract (match_api/rxt/cli
  hunks, trust gate); rulings relied on (Q1-Q8, D38, D36/F7, D26 add.); a build proposal
  (6 stages, abi events); a measurement card (goal 3b, per-fire cost).
- 12:0x COMMON written; 5 lenses chosen: premise+goals (opus), simulate (opus), slot tracing+ruling check+sibling/general-form (opus), contract+trust (opus), cost-and-overlap+measurement (sonnet). Standing questions (sibling of a family; general form + unlocks) assigned to the slot lens.
- 12:20 all five critics returned (durations 5-19 min); every file complete with ## DONE; final replies not delivered (SubagentHandback missing) — files carried everything, no resend needed. Counts: PREM 16, SIM 7, SLOT 19, CON 19, COST 10.
- 12:21 verifier brief written (25 items V1-V25, covering every CONFIRMED finding that would change the design); launching sonnet verifier.
- 12:21-12:27 verifier (sonnet) ran 25 items: 20 HOLDS, 4 PARTLY (V8 shared facts exist but per-arm decisions remain; V9 a compile-REFUSED callouts section turns test-axes RED, only the link-failure path is silent; V15 omission holds, one citation slip; V23 7 free flag bits, not 8), 0 REFUTED. verify.md complete; final reply lost like the critics' (files carried it).
- 12:35 draft review.md written (A1-A9, T1-T7, D1-D21, doc list; all 71 findings mapped); critic texts, verify.md, COMMON and the verify brief copied into review/. No review worktree was created (design mode), so there is nothing to prune. Time from launch to draft: about 36 min.

## Per-lens tally
| lens | model | raised | verified (HOLDS/PARTLY) | primary severities | unique (no other lens) |
|---|---|---|---|---|---|
| PREM | opus | 16 | V1,V3,V4,V5,V6,V7,V8p,V9p,V10 | answer 6, trust 3, design 3, doc 4 | PREM-12 (pre-registered obligations), PREM-11 half |
| SIM | opus | 7 | V1,V2,V22,V25 | answer 4, speed 1, doc 2 | SIM-7; the counted held-sets (4,455 / 120k) |
| SLOT | opus | 19 | V2,V3,V4,V7,V12q,V13,V14,V15p,V16,V17,V21,V23p | answer 5, trust 1, design 7, maint 1, doc 5 | SLOT-4, -8, -10, -11/-16 (with COST-3), -15, -17 |
| CON | opus | 19 | V4,V5,V11,V18,V19,V20,V24 | answer 4, trust 5, design 1, doc 9 | CON-2, -5, -9, -13, -14, -17, -18 |
| COST | sonnet | 10 | V6,V12,V23p | design/speed/maint | COST-2, -4/-5/-6 measurement, -8 overlap |
The six answer clusters (A1-A6) were each found by 2-3 lenses independently; this is heavy overlap but
it is also calibration (a finding re-found blind by a different method is strong).

## Process observations
- All six subagent final replies were lost ("ended without delivering a report through SubagentHandback");
  the files carried everything. The 2026-10-24 lesson (results travel only as files) held a third time,
  with no resend needed because every brief said "create the file, write incrementally, end with ## DONE".
- The critics returned SYNCHRONOUSLY in the coordinator's launch turn although launched with
  run_in_background (the five results arrived in one tool result about 19 minutes later). The monitor and
  nudge machinery of §6.1 was never exercised; the coordinator was blocked but nothing was lost.
- Overlap: PREM, SIM, SLOT and CON each re-found two to four of the same answer clusters. The premise and
  slot lenses overlap most (both read src for "what exists"). This is not over-staffing: every lens also had
  unique findings, and the overlap gave independent confirmation before the verifier ran.
- The verifier's 25-item list was mostly fact-checks of quotes. The two PARTLY verdicts with substance
  (V8, V9) narrowed findings. V9 refuted a consequence that two other readers would have accepted.
- Blinding: the coordinator leaked to itself (see 11:59 entry) by printing context lines around the
  denied plan row. No critic reported an auto-injection or a denied read.
- The lens table had no explicit "trust/adversary" lens; the contract lens carried it because the brief
  folded trust into it. For a feature whose rank-1 goal is trust, that worked, but only because the
  coordinator wrote it into the question.

## Proposed changes
1. SKILL.md §3 step 3 (denylist), add: "To deny a row of plan.md, locate it by `grep -n '^- \[TAG\]'`
   only; never print its neighbours (a `sed -n` around the tag line leaked the denied rulings to the
   coordinator, 2026-10-26 inline-c)." Motivation: the 11:59 leak.
2. SKILL.md §4 lens table, add a row: `D C | a trust boundary (opt-in, gate, untrusted input becomes
   code or a file read) | **adversary** | As the author of an untrusted input, find every path from your
   bytes to code, a file read or a terminal escape that bypasses the gate, including the test harness and
   tooling as entry points | strong`. Motivation: T1-T4 came from folding this into the contract lens by
   hand. The harness laundering (T2) is the kind of path a contract lens without that question misses.
3. SKILL.md §4 premise row, extend the question: "...including every sentence of the form 'the existing X
   already does Y': find X by file:line." Motivation: guide lesson 1 (three failures of that form).
4. SKILL.md §6.1, add: "Critics may return synchronously in the launch turn even when backgrounded; if so,
   read the files at once (the monitor steps are skipped)." Motivation: this round.
5. COMMON template, add to the output section: "If your finding re-finds a fact another lens is likely to
   find (a shared probe), still write it: independent re-finding is calibration." Motivation: overlap
   was useful; keep critics from self-censoring it.

## Framework notes (coordinator pattern)
- Evidence for: the manager stayed out of a ~36-minute round with 71 raw findings, and received one
  consolidated draft with 37 dispositions plus four ruling requests. Blindness held for the critics. The
  coordinator's own blindness failed once (self-inflicted, see proposed change 1).
- The fan-out plus verify plus consolidate pattern fits any "many readers, one judge" task. Here the
  consolidation (71 to 37, with by-id completeness) was the main value the coordinator added beyond
  launching.
- Another fit, from this round's shape: requirements re-validation before a design lane (a coordinator
  fans out PCRE2-probe, codebase-premise and prior-ruling readers over a requirements doc).
  Evidence: three of this round's answer findings (A1, A2, A4) are facts about PCRE2 or the tree that a
  requirements-stage probe could have caught before the design was written.
