# process.md — crit-arev (design), coordinator opus
- 19:45 freeze: arev.md + roadmap.md @ dd89fa9bb0ed1c63e7fed35a972927887f97add4; build tree main HEAD f15f30f25482fd07625d27b401a6c4352d88ea7e. Rulings freeze decisions.md @7f7b7b8f1, plan.md @7ddfbfa95 (as of f15f30f25).
- no code drift src/lib/cli/memfn/docs/spec 7cebea04e..f15f30f25 (arev's anchor) — checked.
- arev.md's branch did NOT contain vlookbehind rev 1 (bc9d1eb8f not ancestor of dd89fa9bb); critics told rev 1 is in force.
- review tree worktrees/crit-arev, nice make -j2 unlocked: rc 0 (~19:43).
- compile spelling check: plain -p rx refused lookaround; --features all needed (COMMON corrected before briefing). (?<=a|bc)x compiles, (?<=a+)x refused.
- oracle_probe copied from crit-vlookbehind tools (vlbinv source); (?<=(?>a|ab)b)x on abbx -> nomatch.
- lenses: owner (owner criteria + goals, opus), premise (opus), soundness (opus), slots (slot tracing + ruling check + standing questions sibling/general-form+unlocks, opus), seam (seam round trip, opus). Not run: simulate (no rule over a corpus), measurement (no measured quantity proposed beyond §4.2 pricing; folded into owner's cost question), cost-and-overlap folded into owner.
- critics launched ~19:45 (5, opus, background, unnamed); all five RETURNED IN THE LAUNCH TURN (~19:48-19:54), each "ended without SubagentHandback" but every findings.md complete and every crit-*.done present. No resend, no nudge.
  owner 10 findings (4 min), premise 9 (8 min), soundness 4 (9 min), slots 17 + standing Qs (10 min), seam 12 (9 min).
- overlap observed: PREMISE-1=SEAM-2 (W2 arms bypass emit_reverse_block); PREMISE-2=SLOT-3=SEAM-9a (xrdfa swap); PREMISE-3=SLOT-13 (W1 tag); PREMISE-4=SEAM-5 (vm_charge); SOUND-1=SLOT-5 (\G); PREMISE-6=SEAM-7b (first not in renderer); PREMISE-7=SLOT-1 (direction-neutral / DfaForm); PREMISE-9=SLOT-15=OWNER-8 (ratchet recipes count names); OWNER-1=SEAM-3/SEAM-4 (C text in record); OWNER-4/SLOT-14 (rev 1 one row, gate absent); OWNER-10=SLOT-14b ([LB-EXIST] filed); SOUND-4~SEAM-9b (exactness fact incomplete: has_bot / prune).
- conflict to resolve: SLOT P&H "emit_reverse_block 3 callers, W1-W3 share one body: held" vs PREMISE-1 (2 of W2's 3 arms call emit_scan_loop directly). Both statements can be true; verifier quotes.
- 19:55-20:04 verifier (opus, 1 agent, 23 items): 18 HOLDS, 4 PARTLY (SEAM-10, SLOT-11, OWNER-7, SEAM-2's answer half REFUTED by an unadmitted arm), 0 not verified. Returned in launch turn; verify.md complete with VERIFY COMPLETE; crit-verify.done present.
- coordinator re-ran the one crafted-input REFUTED (a\n?$ on "a\n"): first attempt used $(printf) which strips the trailing newline (my error: (0,1) vs oracle [0-1] both on "a"); redone with $'a\n': (0,2), (1,3) = libpcre2. Refutation holds.
- freeze drift at hand-back: none (decisions/plan/stream/vlookbehind/src unchanged f15f30f25..82d95943c).
- review worktree removed via wtprune --apply --force --quiet-min 1 (REMOVED). Draft review.md ~20:15; 29 consolidated findings from 52 critic ids.

## Per lens
| lens | raised | verified HOLDS/PARTLY | severity mix | unique (not found by another lens) |
|---|---|---|---|---|
| owner | 10 | 6 checked: 5 H, 1 P | design 8, doc 2 | OWNER-2/3/6/7/9 |
| premise | 9 | 8 checked, all H | design/doc | PREMISE-4/5/6/8 (PREMISE-4 also seam) |
| soundness | 4 + 7 held cells | 4 H | answer 3, doc 1 | SOUND-2, SOUND-3 |
| slots | 17 + D-table + SQs | 8 checked: 7 H, 1 P | design/maint/doc, 1 answer (=SOUND-1) | SLOT-2/4/6/7/9/10/16/17 |
| seam | 12 | 4 checked: 3 H, 1 P | design, 1 answer claim refuted | SEAM-1/8/10/11/12 |

## Process observations
- All six agents returned in the launch turn (background requested) with "no SubagentHandback" notices; files and .done markers were complete every time, so lanewatch was not needed. The FILE-based delivery rule carried the round.
- Overlap was heavy (12 consolidations) between premise, slots and seam: all three read §1/§2.1 against the same code. Five strong lenses on one 430-line note is at the top of the range; premise + seam could have been one critic with two questions, but each found unique items, so not over-staffed in yield, only in tokens.
- The client-drift catch (arev's branch lacked vlookbehind rev 1) came from a coordinator ancestry check that the skill does not require; it seeded F5.
- The skill's compile-spelling check paid off again: -p rx without --features all refused lookaround; COMMON corrected before briefing.
- My own crafted-input re-run had a shell bug (command substitution $(...) strips trailing newlines); a re-run must use $'...' or a file for newline-terminated subjects.

## Proposed changes
1. Skill §3.1 (design): "For each client design document the subject names, check `git merge-base --is-ancestor <client's last commit on main> <subject commit>`; if not, tell critics which client version is in force at the build commit." (Motivation: F5, five findings.)
2. Skill §4 soundness row: "when the design reads a fact recorded for one direction/host from a NEW direction/host, enumerate direction- and position-dependent constructs (\G, \K, absent-prev context, start offset) and check each is recorded; a widening record cannot see narrowings" (Motivation: F1/F2; slots found F1 independently only via A-FACTS' start pin.)
3. COMMON template: "a newline-terminated subject is passed as $'...\n', never via $(printf ...)" (Motivation: coordinator's own re-run bug.)
4. Lens table: for a design note that proposes a record AND re-describes today's code, consider folding premise + seam round trip into one critic with two questions, or tell seam to skip §1 premise checks (12 of 52 ids were duplicates of premise).

## Framework notes
- The coordinator pattern held under load (two other rounds + a mech job): build unlocked under nice took ~1 min; whole round ~35 min wall from freeze to draft. Blinding held: no critic cited the denylisted lane report (OWNER-8 noticed the questions were missing BECAUSE it was denied, which is itself a useful blindness signal: a design that depends on its lane report for its questions is not self-contained).
- Nested agents' final replies never arrived as text but files always did; the file-first rule is necessary, and the SubagentHandback notice should be read as "check the file", never as a failure.
