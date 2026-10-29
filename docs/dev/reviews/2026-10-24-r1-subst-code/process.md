# process.md — critic round subst (code), coordinator log

- 12:05 subject frozen: SUBJECT 1222b31be (lane/substland), BASE 6ec3a2108; 160 files, +16794/-77, 52 commits.
- 12:06-12:10 review worktree worktrees/crit-subst built under boxlock (rc 0); BASE built from git archive in /tmp/claude-1001/crit-subst/base (rc 0) for the emitted lens's before/after.
- Profile: emitted C (new emit_subst.c + touched emit_dfa/lower_enc/definitions/enc); caller-facing contract (subst_api.md 1063 lines, cli.md, match_api.md); checks (50 sabotage rows, subst sections, d27 harness, limits_check); plain C structure (emit_subst.c 1200, subst_template.c 616, cli/main.c +176). No performance claim/re-pin found in the file list (no floors/pins files touched except cite_floors.tsv, c4_allowlist.tsv, ci shards) -> no trade-audit lens; check-adequacy covers those.
- Denylist addition by coordinator: tests/subst/d27/substd27_report.md (a D27 author's report shipped in the diff) and the two docs/dev/reviews/*subst* files the diff adds.
- 12:12 five critics launched in one message (Agent tool; `name` param refused for a teammate: "roster is flat", relaunched unnamed): tpl (opus, a7615c381362e88ae), iface (opus, ab991a6bcc72f17a2), emit (opus, aff3832522c2d1412), checks (sonnet, a242245979458b115), house (sonnet, ac04c7fb040002cd6).
- The Agent calls returned SYNCHRONOUSLY despite run_in_background (all five finished inside the one tool call, ~4.5-9.6 min each); each ended "without delivering a report through SubagentHandback" — the file channel carried everything, as the skill predicts. No resend or nudge needed: all five files complete with ## DONE.
- Per lens: tpl 4 findings (1 answer, 2 doc, 1 size); iface 9 (5 doc, 4 design); emit 6 (3 speed, 1 size, 1 design/answer-tier, 1 maint) + 0-byte-diff result over 72+6+58 pre-existing compiles; checks 8 (maint/doc); house 11 (maint).
- 12:18 all five critic files read (complete, ## DONE). Verifier (sonnet, a7bad62c1370b01e6) launched 12:19, returned 12:23 (again synchronous, again no SubagentHandback; file complete). Verified: 24 ids HOLDS, CHK-3 PARTLY (d27/cli/cli.sh:69 does refuse-test $65536), IFACE-4 HOLDS with a correction (the MISMATCH codes are STATED in §10¶7: a design argument, not an undocumented defect). Not reached: HOUSE-4 five-site count, HOUSE-1 copy count, CHK-3 BIND mapping, CHK-6 mutant run.
- 12:30 review.md drafted (38 ids). Worktree removed 12:31 via `scripts/wtprune --apply --force --quiet-min 1 crit-subst` (the default 120-min quiet gate KEPT it because my own build was <120 min old; nothing was running in it; status clean). Time to draft: ~25 min from freeze.
- Blinding: no leak noticed. Two soft spots: the diff itself ships two docs/dev/reviews/*subst* files and tests/subst/d27/substd27_report.md (denied in COMMON, but a `git diff --stat` shows their names); the design docs cite lane rulings by name (critics were told to test cited claims rather than open them). The house critic wrote one scratch file outside its lens dir (/tmp/claude-1001/crit-subst/out_house_t.c): inside the round's scratch, harmless.

## Per lens
| lens | model | raised | verified | top severity | overlaps |
|---|---|---|---|---|---|
| TPL | opus | 4 | 2 checked, 2 HOLDS (TPL-2/3 doc not re-run) | answer (TPL-1) | — |
| IFACE | opus | 9 | 4 HOLDS (4 w/ correction, 5, 7, 9) | design | IFACE-8 explains IFACE-4; IFACE-9 is the source of IFACE-1 |
| EMIT | opus | 6 | 4 HOLDS (1, 2, 4, 5) | speed + answer-tier ruling | EMIT-6 = HOUSE-7 cleanup; EMIT-4 sibling of [DATA-PLAN] |
| CHK | sonnet | 8 | 7 HOLDS/PARTLY | maintenance (a false DETECTED) | CHK-7 vs IFACE's probed-held options |
| HOUSE | sonnet | 11 | 8 HOLDS by quote | maintenance | — |

## Process observations
- The Agent tool refused `name` for agents launched by a teammate coordinator ("roster is flat"); unnamed launches worked. The skill's §2 tells the MANAGER to name the coordinator, but §5 implies naming critics; the coordinator cannot. Cost: one failed tool call.
- `run_in_background: true` did not detach: the five-critic launch blocked the coordinator for ~10 min and returned all five together, and the verifier blocked ~4.5 min. Harmless here (nothing else to do), but it means the coordinator cannot SendMessage a stuck critic mid-run; the §6 "resend / nudge" ladder is unreachable. The file channel was sufficient: no critic needed a resend.
- No critic delivered a SubagentHandback; every result travelled as a file. The skill's "everything that matters travels as FILES" was exactly right.
- Splitting the contract into two opus lenses (template answers vs interface) paid: they found disjoint sets (TPL-1 answer bug vs IFACE naming/codes), and TPL's full-Unicode sweep is a probe no other lens would have run.
- The emitted lens found the answer-tier ruling question (EMIT-5) from a table read: the "emitted vs replaced" brief asking for a pcre2 baseline produced both the speed table and the quirk list.
- wtprune's quiet gate keeps a review worktree the coordinator built itself <120 min ago; the skill's §6.4 command fails as written for any round shorter than two hours.
- The lens table had no row for "a spec sentence pinning an upstream version vs current D-rows"; EMIT-5 was found by luck of reading.

## Proposed changes
1. Skill §6.4: `scripts/wtprune --apply --force --quiet-min 1 crit-<topic>` (motivation: the default quiet gate KEPT the round's own freshly built tree; nothing else writes there).
2. Skill §5: "Launch critics UNNAMED (a teammate cannot name agents); record each agentId in process.md. Launches may return synchronously; plan the round as fan-out-then-read, not poll." (motivation: the name refusal and the blocking launch above.)
3. Skill §4 lens table, check adequacy row: append "transplant every emitted-text sabotage plant onto a real artifact and compile it with the suite's GENCFLAGS: a plant that fails -Werror scores DETECTED without its witness" (motivation: CHK-1).
4. Skill §4, contract row: append "and every spec sentence that pins an upstream version or behaviour, checked against the CURRENT D-rows (rulings move)" (motivation: EMIT-5 vs the same-day D26 addendum).
5. COMMON template: list the diff's own review/report files by path in the denylist (the diff can SHIP earlier reviews and lane reports; here two reviews and a d27 report rode in the diff).

## Framework notes
- One coordinator, five critics, one verifier: ~25 min freeze-to-draft, the manager's context untouched until the hand-back; the coordinator saw ~1,000 lines of critic text and condensed it to one review. Evidence the pattern fits large code subjects: 160 files / 16.8k lines profiled to five lenses with explicit NOT COVERED lists.
- The verifier earned its place again: one PARTLY (CHK-3's "unpinned" was pinned in d27) and one correction of framing (IFACE-4 is stated in §10¶7). Without it two findings would have reached the manager overstated.
- The synchronous launch makes the coordinator a pure batch step (launch all, read all, verify, draft); it fits any fan-out whose items are independent and whose outputs are files, e.g. a compliance-refresh survey or a multi-arm measurement sweep.
