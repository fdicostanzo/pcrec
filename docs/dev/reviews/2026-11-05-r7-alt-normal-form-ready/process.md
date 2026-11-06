round start 2026-11-05T20:33:35-05:00
SUBJECT doc docs/design/alt_normal_form.md @ 129b61a678b53b3881823d9615d6fc9dedcaf759
BUILD tree main HEAD 08eef8b4b0c0bf242a73e634d7279d8018850e51
RULINGS freeze decisions.md/plan.md as of main 08eef8b4b (decisions last 7f7b7b8f1, plan last db04e56a7)
2026-11-05T20:37:12-05:00 COMMON written; lenses ready(opus) fixind(opus) sound(opus) sim(sonnet); vlookbehind client rev2 merged at 4a0fcc859 pre-launch (no code moved) -> critics told to read rev 2
2026-11-05T20:52:58-05:00 all 4 critics returned in launch turn (~10-15 min each)
- ready (opus): file complete 20:50, DONE; RDY-1..10 (6 CONFIRMED-ish), per-unit verdict READY WITH TEXT FIXES; found 1e NOT landed
- sound (opus): file complete 20:51, DONE; SND-1..5 (SND-1, SND-2, SND-5 CONFIRMED; SND-3/4 SUSPECTED)
- sim (sonnet): file complete 20:46, DONE; SIM-1..7 (all low/doc; U1b pins reproduced exactly)
- fixind (opus): returned without findings file; ONE SendMessage 20:53 asking for it
- overlaps noted: SND-1~RDY-1 (island, two different mechanisms); SND-2 vs RDY-2 (S-m: SND-2 says cannot fail, RDY-2 says value wrong but fails) -> verifier decides
- 21:08 verifier (sonnet) DONE: 16 ids; HOLDS 11, PARTLY 4 (RDY-2 S-m half REFUTED, SND-3, SND-4, RDY-6), 0 not verified except pcrec half of SND-5
- fixind (1st) never wrote a file after the one SendMessage: STALLED (no file, no reply reached me)
- 21:09 fixind2 (opus, fresh, narrowed) launched; wrote findings by 21:16 (FIX-1..8). COORDINATOR ERROR: I did not create fixind2/DELIVER before launch, so it could not pass lanecheck; I wrote DELIVER and ran lanecheck for it after
- FREEZE DRIFT: main 08eef8b4b -> 64ab880aa: plan.md [DEC-RUNG] widened (fact-selected emission family incl. "alt island/chain"); vlookbehind.md rev 2 merged; no src/spec/decisions change
- 21:19 verifier follow-up (SendMessage resume) DONE: FIX-2..6 HOLDS, FIX-7 PARTLY
- 21:22 draft review.md complete; time freeze -> draft ~50 min

## Per lens: raised / verified / severity
- ready: 10 raised; verified HOLDS 6 (1,3,4,5,7,10), PARTLY 2 (2,6), not re-run 2 (8 lists, 9 cites); 3 gate-red-on-correct-build class (1,3 + 7 missing gate)
- sound: 5 raised; HOLDS 3 (1,2,5), PARTLY 2 (3,4 latent/reading); the two highest-value finds of the round (SND-1, SND-2) — both "witness cannot reach/fail"
- sim: 7 raised, all low/doc; U1b pins reproduced exactly; HOLDS 3 verified
- fixind2: 8 raised; HOLDS 5, PARTLY 1, judgment 1, dup 1 (FIX-1 = RDY-5)
- overlaps: RDY-5=FIX-1; RDY-2~FIX-5~SND-2; RDY-6~FIX-7; SIM-3~FIX-7; SND-1 and RDY-1 DISTINCT (island)

## Process observations
- All four critics and the verifier returned in the launch turn (background launch blocked anyway); reading files at once worked.
- The first fix-induced critic used ~220k tokens / 52 tools and wrote NO file, even after one SendMessage (no reply reached me). Cause unknown (no harness refusal reported). The fresh narrowed relaunch with "create the file with its headings IMMEDIATELY, append each finding as found" delivered in 7 min.
- Coordinator error: fixind2 launched without its DELIVER file; it could not pass lanecheck. Coordinator wrote DELIVER after and ran lanecheck (DONE) on its behalf.
- lanewatch --follow --dir on a critic with no worktree printed "GONE" at once (rc 11): unusable for dir-only critics; a foreground file-wait loop was used instead.
- Main moved during the round (vlookbehind rev 2, plan [DEC-RUNG] widened) — freeze drift reported, no finding changed.

## Proposed changes
1. Skill §5 (COMMON template, output format): "Create your findings file WITH its section headings as your FIRST action, and append each finding as soon as it is found." Observation: fixind (1st) spent 52 tool calls and delivered nothing; fixind2 with this sentence in its prompt delivered.
2. Skill §5: "A relaunched critic gets its DELIVER file written BEFORE launch (checklist: dir, DELIVER, prompt)". Observation: fixind2.
3. Skill §5/§6: lanewatch --follow reports GONE immediately for a --dir critic without a worktree; use a file-wait loop on NAME.done, or fix lanewatch's follow mode for --dir. Observation: this round, 21:00.
4. Lens table, soundness: "for a reader that MOVES onto a new record, find every path by which the walk reaches that node kind (see-through helpers included) and put a witness on each path" (SND-1). Fix-induced: "for a rewrite, list every pass that triggers on node kinds the rewrite removes and check the movers table predicts each" (RDY-1). Soundness: "for each witness of step k of a multi-step procedure, execute the CORRECT procedure on it and confirm step k does the work" (SND-2).

## Framework notes
- Fourth design round on this subject; the coordinator pattern again kept the manager's context out of eleven critic/verifier turns. The verifier-by-SendMessage-resume (for a late critic's findings) reused its warm context and cost one 3-min turn instead of a new verifier — worth naming in §6 as the default for a late file.
- The stalled critic shows the pattern's weak point: a nested agent whose final text is lost leaves no trace; only the file discipline makes it recoverable.
