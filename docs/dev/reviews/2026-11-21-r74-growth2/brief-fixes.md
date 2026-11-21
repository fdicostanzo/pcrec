CRITIC fixes / check adequacy (opus): growth2 (r74)

Read /var/tmp/pcrec-pcrec/scratch/crit-growth2/COMMON.md first; it binds you (scope, read-only, denylist, output).
Your dir: /var/tmp/pcrec-pcrec/scratch/crit-growth2/fixes/ ; findings file fixes/findings.md (PRE-CREATED: append only); ids FIXES-n.

ONE question, two sub-parts:
(a) Is each FIX-NOW ruling in R/rulings/r73-growth.md, section "Rulings (manager, 2026-11-21)", actually DONE in
    SUBJECT's code, each proved by ITS OWN DRILL (not by reading the diff alone)? The list: DEPTH-1+DEPTH-2+VERDICT-7;
    VERDICT-2+VERDICT-3; VERDICT-4; VERDICT-5; VERDICT-6; VERDICT-8; HOUSE-6(5); DEPTH-3; VERDICT-9+HOUSE-5;
    HOUSE-1's control retarget; HOUSE-3's dead block, closed-set check on `stack`, and the dropped columns;
    HOUSE-4's clamp; the two accepted lessons (in .claude/skills/pcrec-critic/SKILL.md: read it at SUBJECT with
    `git show d5257c005:.claude/skills/pcrec-critic/SKILL.md`, the check-adequacy row) and the PLAN rows ruled
    (HOUSE-1 driver deletion + HOUSE-2; the alt_past NOTE on [K154-ALT-1M-MEM]: `git show d5257c005:docs/dev/plan.md`,
    locate rows with `grep -n '^- \[TAG\]'` only). For each item: the drill that would have gone GREEN at BASE
    (use `--harness base` / the BASE tree) and must go RED at SUBJECT, run on both; e.g. for the depth arm, copy
    run_compile_stack.sh's depth-arm block into your dir with the runner call replaced by a fake that prints a
    chosen output and exits a chosen rc (r73 did exactly this), for VERDICT-2/3 a fake driver printing
    `rc=-1 hw=0 msg=internal error: x` and `rc=-9 ...` through a mkcopy main loop, for VERDICT-5 a red cell that
    fails with a different kind, for HOUSE-6(5) a cap above RLIMIT_DATA's hard limit (`ulimit -Hd` in a subshell).
    A fix whose drill stays green at SUBJECT is a finding; so is a fix that is done but CHANGED the rule it
    fixes (e.g. a narrowed PASS that now also rejects a legitimate outcome), and a ruled item not done at all.
(b) The PLANTS (yours alone in this round): the depth arm now judges depth@250 as a LIMIT cell (compile AND build
    and run the matcher) and depth@251 as a stability cell, and the CONTROL runs on growth_driver. For each depth-arm
    plant row (S1339, S1340, S1440, S3470: r73 found them caught by the depth arm; S1336-S1338 by the width arm,
    unchanged, so spot-check one), run the depth cells through `kit/judge_cell.py plant:<ROW> CELLID`: is each row
    still caught (some cell judged FAIL), by how many families, and is any row now caught ONLY by the new matcher
    step or lost? Also run the retargeted control line (copy it from run_compile_stack.sh; CONTROL_STACK is in that
    script) against SUBJECT's growth_driver: does it die by signal, and does a growth_driver whose thread does NOT
    start (e.g. an absurd stack size) land in the right branch?
Probe budget: 4 plant rows x 66 depth cells = 264 cells, + 1 width spot-check, + about 40 fake-driver / mkcopy runs:
cap 350 cell runs total.
Standing questions (yours, one short paragraph at the end): is this the SIBLING of a family (other refusal-is-pass
harnesses in the tree), and the GENERAL FORM + its unlocks (with triggers), not built.
Deliver: append findings as you go; end with `## PROBED-AND-HELD` and `CRITIC COMPLETE`; run lanecheck
(COMMON's command, lens name `fixes`) until DONE; END.
