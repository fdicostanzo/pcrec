# process.md — critic round r38s (design, readiness), coordinator crit-r38s

## Freeze (2026-11-09T09:50-05:00)
- SUBJECT doc: docs/design/memfn/span_runs_sheet.md rev 0, last touched by 0de3cadec (lane/memfn-r38s HEAD, rev-parsed).
- Build tree: lane/u3mech 404cff6ea (subject branch's base; merge-base confirmed). main 791e592d3 is NOT an ancestor of u3mech (main has 5+ commits not on u3mech: span_arms §12b, D191, R-38).
- s30a: lane/memfn-s30a e95cd7aef; its own changes = 73075a9d1..e95cd7aef (merge-base with u3mech 73075a9d1; s30a lacks U3).
- Client docs: span_arms.md rev 2.2 + §12a/§12b and R-38 at main 791e592d3 (in force at freeze); plan_frame.md rev 2.2 only on s30a (absent at 404cff6ea and at main).
- Rulings frozen at main 791e592d3; decisions.md/plan.md last touched 6a7fd9b04.
- Ruling records: D191 decisions.md:10119; §12a span_arms.md:1182; §12b span_arms.md:1194; R-38 requests.md:859 (clarification commit 791e592d3); D157:9381, D172:9896, D186:10032, D187:10059, D142:8948, D153:9258.
- Review tree worktrees/crit-r38s at 404cff6ea, built once nice make -j2 rc=0 (~1 min).
- Probe spellings checked: --features lookaround needed for (?=, (?<=; --emit-facts; -e utf8; -I tests/findings/adversarial --analysis=uniform (from review tree); --memfn=no-fd-pres-pick. Oracle: docs/design/eng_brep_measurements/probes/pcre2_ctypes.py (libpcre2 10.46 ctypes).

## Agents
- 4 critics launched 09:52 (unnamed, background, opus): rulings (ruling check + owner criteria + goals; Q1-Q3), seam (seam round trip + slot tracing + standing questions; Q5, Q6), readiness (readiness; Q4), soundness (soundness: §3.3/§3.4 rules + witnesses/controls reach).
- All four returned IN the launch turn (~7-10 min each: 501s, 440s, 571s, 430s), files complete, lanecheck .done present for all. No resends, no nudges. Final replies lost (harness: "ended without SubagentHandback") — files carried everything (the skill's FILES rule held).
- Findings raised: rulings 10 + Q1-Q3; seam 8 (1 SUSPECTED) + Q5,Q6; readiness 12 + verdict + Q4; soundness 9 (1 SUSPECTED).
- Overlaps: Goal1/prefilter second decider (RULINGS-9, SEAM-5); spec hunks/REQ_BYTE (RULINGS-5, READINESS-2, -12); Q2 (a) undefined when scan outside extent (RULINGS Q2, READINESS-10, SOUNDNESS-8); nterm/window-member refusals missing from §5.1 (RULINGS-8, SEAM-6); C4 lever missing (READINESS-8, SOUNDNESS-7, SEAM-3); C1 unreachable on default route (RULINGS-4b, SOUNDNESS-3); Q1 movers (RULINGS-7, READINESS-11).
- Ruling re-diff at critics' return (10:02): no FREEZE DRIFT.
- Verifier (opus) launched 10:03, returned in launch turn (~6 min, 80 tool uses), verify.md complete + VERIFY COMPLETE + lanecheck DONE. 19 items: all HOLD except SOUNDNESS-2 PARTLY (one oracle line refuted: `(?=barbaz)` from 1 on `barbaz` is NOMATCH; coordinator re-ran it: holds as refuted; (6,6) is on `barbazbarbaz`), SEAM-5 PARTLY (rules share tie direction; differ by verify-NO EXACT restriction).
- Draft written ~10:15; review worktree removed via wtprune --force --quiet-min 1; no FREEZE DRIFT at hand-back (main still 791e592d3).
- Time to draft: ~25 min from launch of critics.

## Process observations
- Four narrow opus briefs all delivered complete files in 7-10 min; no resends. Each brief carried one question with two sub-parts, as the skill now requires.
- Overlap was high (seven consolidated clusters found by 2-3 lenses each), mainly between rulings/readiness/soundness on Q2 and the controls. A readiness round on an interface sheet invites overlap because every lens reads the same §2.4/§3.5 tables; acceptable as corroboration.
- The most valuable finding (F2: the reply is a site/route decision) came from the seam lens reading the DEFINE's code for its inputs, not the sheet's input list.
- The soundness lens's answer-level find (F1 product cover) came from asking "what does `exact` mean" with today's --emit-facts mask output; no simulation needed.
- All final replies were lost ("ended without SubagentHandback"); files carried everything. The skill's FILES rule held fully.
- Probe spelling gap: lookaround needs `--features lookaround`; checking it before briefing saved every critic a refusal.

## Proposed changes
- Skill §4 seam round trip lens: add "enumerate the inputs the DEFINE (the later renderer) reads from code, and compare them with the inputs the design lists for any earlier/pure ask; a purity claim covers the function, not the decision" (motivation: F2/SEAM-1-2).
- Skill §4 soundness lens: add "for any rule that drops a finish or check on a proof, ask for the SUFFICIENCY fact and list every match OUTPUT (captures, \K, MARK, call mode) as a precondition" (motivation: F1).
- COMMON template: a "feature flags needed by the probe patterns" line (e.g. --features lookaround), checked by one compile.

## Framework notes
- Coordinator pattern, 4 critics + 1 verifier, all returned in the launch turn: the whole round ran in ~25 min of coordinator wall time with two waits. The pattern fits interface-sheet readiness rounds well: the coordinator's freeze (three trees: subject, build tree, parallel unit) is the part the manager could not have delegated blind.
