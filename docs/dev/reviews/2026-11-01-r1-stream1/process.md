# process.md — crit-stream1 (design)
- 16:42 coordinator start; freeze recorded (.coord/freeze.sha256); build-landing commit f574eab2d948893f68e72deea294d31b30c702de (main HEAD). Subject is uncommitted scratch copies: no doc commit.
- 16:43 review tree built (nice make -j2, rc=0). 16:45 COMMON written; lenses: premise(opus), soundness(opus), benefit(opus; launcher lenses a+b, goals folded), seam(opus; launcher lens c + slot tracing + ruling check + sibling/general-form standing questions), cost(sonnet; cost-and-overlap).
- All five critics launched in one message; all five returned in the launch turn with "ended without SubagentHandback". Durations: premise 703s, soundness 757s, benefit 297s, seam 587s, cost 187s.
- 16:57 all five files complete; lanewatch DONE rc=0 (5 good markers); freeze re-checked OK. No resends, no nudges. Critics returned in launch turn; their final replies were lost (SubagentHandback missing), files carried everything (as the skill predicts).
- Raised: PREMISE 15, SOUND 14, BENEFIT 9, SEAM 15, COST 8 (61). Overlaps seen: PREMISE-8 = SOUND-5 (row 1 lazy); PREMISE-4 = SEAM-2 (MF_SK_* consumer kind); PREMISE-14 `exact` ~ SEAM-5/SEAM-13; PREMISE-13 = BENEFIT-1/8 (no goals, no F1-F4); PREMISE-3 ~ SEAM-6 (start loops); PREMISE-1 vs BENEFIT-2 tension on X14 (premise: kit already op-keyed; benefit: engine taxonomy in kit header); SEAM-8 ~ COST-7 (CAND-SPAN); SEAM-11 ~ SOUND-8 (callout as erasure).
- Blinding: benefit critic wrote git log --stat subject-line dumps (log.txt) in its own dir; spot-checked, subject lines only. No leak seen.
- 16:58 verifier (opus) launched over 40 ids; returned in launch turn without handback; verify.md complete (40 sections, VERIFY COMPLETE), VERIFY.done 17:06. Verdicts: HOLDS 31, PARTLY 8 (SOUND-7, SOUND-11, PREMISE-1, SEAM-10, SEAM-11, BENEFIT-2, COST-2 + counts), REFUTED 1 (SEAM-8). Count corrections: BENEFIT-2 (critic's git log truncated at 400 merges: 66/207 both-emitter, not 39/115), PREMISE-6 (28 lines/7 files, not 25/6), PREMISE-4 (64 key lines, not 48), COST-1 (44 hunks, not ~60), SEAM-3 (mf_ask call sites 7060/8316/8714).
- 17:08 draft review.md written; critic texts + verify.md copied to review/.

## Per lens
| lens | model | raised | verified HOLDS/PARTLY/REFUTED | top severity | overlaps |
|---|---|---|---|---|---|
| PREMISE | opus | 15 | 10/1/0 (4 not sent) | answer (P-8 dup) / design | SOUND-5, SEAM-2/5/6/13, BENEFIT-1 |
| SOUND | opus | 14 | 9/2/0 (3 DOC not sent) | answer x11 | PREMISE-8, SEAM-11 |
| BENEFIT | opus | 9 | 2/1/0 (6 text-only) | design | PREMISE-13, SEAM-1/14 |
| SEAM | opus | 15 | 8/2/1 | answer x1 (SEAM-4) | PREMISE-4/14, BENEFIT-7, COST-7 |
| COST | sonnet | 8 | 3/1/0 | maintenance/schedule | PREMISE-1 (P-a), SEAM-8 |

## Process observations
- Every agent (5 critics + verifier) "ended without SubagentHandback" yet returned inside the launch turn; the file + lanecheck marker protocol made this a non-event. lanewatch was a one-shot confirmation, not a poll.
- Blinding: the subject cites `runs/`, `today/` etc. under the denied scratch/stream/ tree; critics reproduced the cited runs themselves (PREMISE 12 compiles) — the right outcome, but it cost compiles. A design synthesis that cites its own scratch runs should freeze those run outputs as part of the subject.
- COMMON gave a wrong path for the capture survey (docs/design/ vs docs/dev/optloop/); PREMISE caught it. Coordinator should resolve every cited doc path before writing COMMON.
- BENEFIT's git-log count silently truncated at 400 lines (a pager/limit in its own pipeline); the verifier caught it by recounting. A count claim over git history should state its window's first and last commit.
- The lens table has no row for an OWNER-CRITERIA lens (benefit-is-real against stated owner criteria); the launcher had to request it. It found the round's top design finding together with PREMISE.
- Over-staffing: none; every lens produced unique findings. COST (sonnet) was adequate; its one weakness was precision of detail (hunk count, kind names), both corrected by the verifier.

## Proposed changes
1. SKILL §4 lens table, new row: `| D | owner/launcher-stated benefit criteria | **criteria** | For each stated criterion: does the design DELIVER it (name the mechanism and its test), PARTLY, or only ASSERT it? Is the case argued on the criteria in force at the freeze? | strong |` (motivation: B1/B3-B7, launcher had to add it by hand).
2. SKILL §3.1 design: "If the subject cites its own scratch artifacts (runs, drafts), freeze them as subject copies or tell critics to reproduce; list which." (motivation: denied runs/ cost ~15 compiles to reproduce).
3. COMMON template: "a count over git history states its window (first..last commit) and the command; the verifier recounts" (motivation: BENEFIT-2 truncation).
4. critics.md lessons: the four in review.md "Lessons for the guide".

## Framework notes
- The coordinator pattern fit a design round with no code subject well: one build, five parallel critics, one verifier, a draft in ~25 min wall. The verifier's value was again in correcting magnitudes and refuting one ruling-conflict claim (SEAM-8), not in reruns of answers (all answer witnesses held).
- Where else: the same fan-out fits a SYNTHESIS step itself (merging N blinded drafts): lesson 2 (merges drop conjuncts) suggests the synthesis should be reviewed by a soundness critic diffing source rows vs merged rows before it reaches the owner.
- Time to draft: freeze 16:42 -> draft 17:08 (26 min).
