# process.md — critic round memfn-s3-final (code)

Coordinator start: 2026-10-24 09:36 EDT. SUBJECT cc4f54eb296f035e0e5d9863c680a69721a64875 (lane/memfn-s3pair), BASE 0d3765c87ae412f9a99dc0df1ea56250d6943a55 (= main merge-base; main tip 1030ef437).
Review tree: worktrees/crit-memfn-s3-final (detached SUBJECT). Build queued 09:37 under `scripts/boxlock run` (box held by queue:620-kit-s3-heavy since 09:35).

## Agents
- Compilers: SUBJECT = copy of worktrees/s3pair/build/pcrec (clean tree at cc4f54eb2, binary newer than every source; sha256 5574edea...), copied 09:40 because the review-tree build waits on the box lock (job 620 heavy); BASE = copy of main's build/pcrec (product source unchanged BASE..main tip, emits abi 84).
- Profile: emitted C (cover scan, E-find, PAIR, D-hors); decision tables (Table B/fd_find, wf_brows, wf_dtable, E rows); caller-facing contract (match_api §6.3.4, registry wf-*, tuning ¶3d); pins/floors/sabotage moved (cpset, row_floors, G2 plants, deleted S1251-1256/S922); plain C structure (window.c +1185); rulings relied on (design rev 3.3 DRAFT, D172).
- Lenses (5): emitted-vs-replaced (opus), contract (opus), slot tracing + ruling + goals + previous-findings + standing questions (opus), check adequacy + trade audit folded (sonnet), house rules (sonnet). Trade audit folded into check adequacy to keep 5; house rules kept separate because window.c is the bulk of the diff.
- 09:41 launched 5 critics in one message. First attempt with `name:` failed ("teammates cannot spawn teammates"; the coordinator is itself a team member) -> relaunched unnamed: an extra minute, no other cost.
  | lens | model | agent | ran | end state |
  |---|---|---|---|---|
  | emitted-vs-replaced | opus | a04be59512ae1b38e | 1012 s | file complete (5 findings); final reply NOT delivered ("ended without SubagentHandback") |
  | contract | opus | a3376d096483d5a42 | 964 s | file complete (7); reply not delivered |
  | slot+ruling+goals+prev | opus | a8bcd18236919bc1c | 831 s | file complete (9 + prev-findings tables + standing Qs); reply not delivered |
  | checks+trade | sonnet | ad239c8f7cbf8521d | 346 s | file complete (9); reply not delivered |
  | house | sonnet | a0a704bb3754cab38 | 237 s | file complete (14); reply not delivered |
  All five final replies were lost; all five FILES were complete with PROBED-AND-HELD, so no resend/nudge was needed. Files-as-channel worked exactly as section 1 predicts.
- Blinding: contract critic disclosed that a `sed` range over decisions.md printed D176's section by accident (not used). Slot critic used its allowed exception (r1/r2 + r2 slot critic file). Others: no denied file opened. Slot critic exceeded the ~50-compile batch guidance once (108 compiles, disclosed) while the box held a heavy job.
- 09:58 all files read. Behaviour-level: 0 answer findings (about 5M differential cases across emit/contract/slot vs libpcre2, ASan-clean). Speed: EMIT-1 (PAIR find-all quadratic), EMIT-4 = SLOT-1 (walk where BASE memchr'd; overlap, two lenses), EMIT-2, EMIT-3, SLOT-4 (suspected). Doc: CONTRACT-1..7, EMIT-5 (= CONTRACT-2 overlap), SLOT-5/6/7/9 (SLOT-9 = CONTRACT-7 overlap). Maintenance: SLOT-2/3/8, HOUSE-1..14 (HOUSE-10 = SLOT-3, HOUSE-12 ~ SLOT-2, HOUSE-4 = r1 C14 remainder), CHECK-1..8.
- 09:59 verifier (sonnet, a45dc6e0a2e933eaf) launched over 15 ids; 243 s; verify.md complete; final reply again NOT delivered (6/6 lost this round). Verdicts: HOLDS EMIT-1/2/3/4, CONTRACT-1/2/3/5, EMIT-5, HOUSE-1/6/7, SLOT-2/8, CHECK-1 (reader); REFUTED SLOT-4 (instruction counts).
- 10:04 review-tree build cancelled unrun (TaskStop on my boxlock waiter: it had waited 27 min and job 620 still held the box); no build/ was ever created in the tree.
- 10:10 draft review.md written; critic texts + verify.md + COMMON copied to review/. Worktree removed with `wtprune --apply --force --quiet-min 20 crit-memfn-s3-final` (the default 120-min quiet gate KEEPs a tree checked out 30 min earlier; nothing wrote to it after checkout).
- Per lens: emit 5 raised / 4 verified HOLDS (speed x4, doc x1); contract 7 / 4 HOLDS + 3 read (doc, 1 design-naming); slot 9 / 2 structural HOLDS, 1 REFUTED (SLOT-4), rest reading (speed 1 = EMIT-4, doc 4, maintenance 3); checks 9 / CHECK-1 HOLDS; house 14 / 3 HOLDS. Overlaps: EMIT-4=SLOT-1, EMIT-5=CONTRACT-2, CONTRACT-7=SLOT-9, SLOT-3=HOUSE-10, SLOT-2~HOUSE-12, HOUSE-4/14 = r1 C14 remainder, HOUSE-5 = r1 C5.
- Time to draft: 09:36 freeze -> 10:10 draft (34 min; critics 4-17 min each in parallel, verifier 4 min).

## Process observations
- The coordinator is a TEAM MEMBER here, and `Agent` with `name:` fails for it ("teammates cannot spawn other teammates"). Critics must be launched unnamed, so they cannot be addressed by name and only an agentId works for a resend. This cost one round trip.
- 6/6 final replies were lost ("ended without SubagentHandback"). Files were the only channel and were sufficient: no resend or nudge was needed because COMMON required incremental files ending in PROBED-AND-HELD.
- The skill's "build ONCE under boxlock" collides with a long heavy job: the waiter never got the lock in 27 min. The fallback (a copy of a clean build at the same commit) made the round possible; without it the behaviour lenses would have stalled for the whole of job 620.
- Blinding leak: `sed -n '/D174/,/D17x/p'` over decisions.md printed D176 (the next section). A per-D-row denylist inside one file is fragile.
- Lens table: emitted-vs-replaced was the highest-yield lens (every speed finding). Contract and slot overlapped on naming (D174). House rules on sonnet produced 14 mostly-maintenance items in 4 min, cheap but heavily PLAN/NOTED.
- One critic ran 108 compiles in one batch against COMMON's ~50 guidance while a heavy job held the box. Light, but the guidance was not followed.

## Proposed changes
1. SKILL §5: "Launch critics WITHOUT `name:` (a coordinator that is itself a teammate cannot name spawns); record each agentId in process.md for the one resend." Observation: the first launch failed 5/5.
2. SKILL §3.2: "If the box is held by a heavy job, use the copy fallback FIRST (a clean build at SUBJECT from the lane's tree, checked: tree clean, binary newer than every source, sha recorded), and queue the own-tree build only if no such copy exists." Observation: 27 min lock wait, build never ran.
3. COMMON template, denylist: "A denied D-row inside decisions.md: locate rows with `grep -n '^## D'` and print exact line ranges that END BEFORE the denied row's heading; never a pattern range." Observation: the D176 leak.
4. SKILL §6.4: "wtprune's quiet gate KEEPs a freshly checked-out review tree; use `--quiet-min N` with N just under the tree's age after confirming no agent writes there." Observation: the first prune was KEEP.
5. critics.md (lens table, emitted-vs-replaced row): "on a change to the DEFAULT search, run find-all over one real text and one adversarial text per new find form, BASE vs SUBJECT, by instruction count". Observation: EMIT-1/EMIT-4, both outside the bar's sample.
6. SKILL §5 output format: drop the reliance on the final reply ("final reply at most 150 words" is fine to keep, but the coordinator must never wait on it). Observation: 6/6 lost.

## Framework notes
- One coordinator running 5 critics + 1 verifier delivered a verified draft in 34 minutes, with the manager not woken once. The files-as-channel rule was decisive: every return-message path failed and nothing was lost.
- The coordinator's blindness held: it knew no earlier result, and only the slot lens read r1/r2. That lens's previous-findings table was produced without contaminating the others' independent findings (EMIT-4 and SLOT-1 converged from opposite sides, which is evidence the blinding produced independent confirmations).
- Where else it fits: any fan-out whose outputs need cross-checking before a ruling, e.g. a census or measurement sweep with an independent verifier, or a bench-report triage. The prerequisites are the same: work that travels as files, a verifier that re-runs claims, and a launcher that rules only.
- 10:15 the launcher relayed that the house critic's handback failed with "caller had already exited". Same failure class as the six lost replies above. The round had already finished from files: verifier run, draft written, handed back at 10:12. All critic agents had ended on their own, so there was nothing to stop.
