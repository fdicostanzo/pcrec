# process.md: critic round memfn-bspan (design), review r67, coordinator crit-memfn-bspan

## Freeze (2026-11-21 00:38-00:44)
- SUBJECT: docs/design/memfn/block_span.md rev 2 at aaa1b3227 (lane/bspan2 HEAD 814a44106 = + report OWED line, denied).
- BUILD TREE: lane/memfn-k1108 03ce1ee3b; worktrees/crit-memfn-bspan, nice make -j2 rc 0 (00:40); + build/libpcrec_mftrace.a, bin/pcrec-harness-mftrace linked by hand (cc -O2 -DPCREC_HARNESS cli/main.c libpcrec_mftrace.a).
- main HEAD 5c1ccef7e; diff 03ce1ee3b..5c1ccef7e over memfn/src src docs/spec tests: EMPTY. Subject base 10cdf0654..03ce1ee3b over same: EMPTY.
- RULINGS FREEZE: decisions.md/plan.md at main 5c1ccef7e (last touch cbbb41ecd: D201 add. 2). D201 at decisions.md:10299, add.1 :10306, add.2 :10307. R-47 at kit requests.md:981; ack responses.md:3648.
- FREEZE NOTE: R-1..R-4, scan-scope, wrap-deny: records only in denied bspan*_rulings.md / denied journal; coordinator did not read them.
- Review number: r67 (r66 l3fix is the last 2026-11-21 file in any branch; launcher said "next free").
- Evening hold (20:00-01:00): round is light work; critics told no timing, no make, compile caps.
- Round dir was absent at start.

## Lenses (5)
| lens | model | question | why |
|---|---|---|---|
| SOUND | opus | V form + wrapper answer-identical, hand-executed with kept guards; compile matrix | design ships emitted-text pseudo-code + proof of identity (soundness row; design-mode COMMON rule: one lens hand-executes pseudo-code) |
| PREMISE | opus | every "today the tree does X" and assumption true at build tree; + slot tracing / one table per slot / selector family; all callers of the emitting functions | new table + mechanism (premise, slot tracing) |
| SIM | sonnet | the table run over population + bound re-sweep; §0.1/§11/§17 numbers recomputed | a selection rule (simulate) |
| MEAS | opus | each measurement/check/plant can fail, one axis per arm; existing sabotage rows on refactored functions | measured quantities + checks + 4 new sabotage rows (measurement, check adequacy) |
| SIZE | opus | SHIP-SIZE (launcher-requested) + goals + rulings (verbatim quotes) + cost/overlap + general form/unlocks with triggers | launcher lens; build proposal; rulings relied on |
Standing questions: sibling-of-family -> PREMISE; general form + unlocks -> SIZE.
Drill assignment: pseudo-code hand-exec -> SOUND; plants -> MEAS; owner-quote verification -> SIZE; callers of emitting function -> PREMISE; k definition/bounds -> SIM.

## Agents
| agent | id | model | launch | end | final state |
|---|---|---|---|---|---|
| SOUND | a9f80a000cb8ba53e | opus | 00:45 | ~01:02 | file complete, lanecheck DONE; final reply undelivered (expected); own-C cap overrun ~38 (338/300), self-reported |
| PREMISE | aba2f336ca8652b49 | opus | 00:45 | ~00:57 | file complete, DONE; appended its own CORRECTION to PREMISE-3 (a render-time precedent exists: runcmp) |
| SIM | a185d196920e66ad3 | sonnet | 00:45 | ~00:49 | file complete, DONE (4 min) |
| MEAS | aedc9abffef99e4d0 | opus | 00:45 | ~01:00 | file complete, DONE |
| SIZE | ae400cd1274c10a16 | opus | 00:45 | ~00:52 | file complete, DONE |
All five returned within the launch turn (the Agent calls blocked until completion despite run_in_background); no resend, no nudge, no stall.
Verifier: none launched; coordinator verified inline (17 items, verify.md), allowed by §6.2 (quote/grep claims + one-call repros; one re-run of a critic's machine-code files).
Draft: review.md at ~01:15; review worktree removed with wtprune 01:17.

## Per lens: findings raised / verified / severity
- SOUND 5 (4 CONFIRMED verified, 1 SUSPECTED): design 1, build 1, doc/answer-if-literal 1, scope 1, doc 1. Overlaps: SOUND-2 with PREMISE-1/MEAS-11; SOUND-4 with PREMISE-6; SOUND-5 with MEAS-6/PREMISE-9.
- PREMISE 10 (+1 self-correction): design 4, maintenance 2, doc 3, speed/design 1. Unique: PREMISE-3/4/5/7/8/10.
- SIM 4: doc 3, design 1. All overlap others except SIM-4 (utf8).
- MEAS 12: design 9, answer-latent 1, maintenance 1, doc 1. Unique: MEAS-2/3/4/5/8/9/10/12.
- SIZE 9: design 4, size 2, doc 3. Unique: SIZE-2..9.
- Severity of the round: 0 answer-level design defects; 1 latent answer (F-8); 1 text-level answer-if-literal (F-5).

## Blinding
- No leak noticed. The coordinator did not read any denied file. The FREEZE NOTE (R-1..R-4, scan-scope, wrap-deny recorded only in denied files) meant the ruling lens could not verify those three; SIZE checked D201's verbatim quotes only.
- The round dir's kit and COMMON named the census script's text-proxy "scan" definition (as a FACT of the data's columns); three lenses then found the LIBC site independently. That sentence was a description of the column, not a suspicion, but it pointed at the place: borderline. Recorded.

## Process observations
- The 5 Agent calls with run_in_background returned only at completion (each ~4-17 min), in one turn. Harmless here (every file complete), but the coordinator could not monitor or nudge mid-run; nested background did not behave as background.
- The MF_TRACE harness (bin/pcrec-harness-mftrace, ~1 min to build) and kit/site.py (fd row + k per site) carried the round: every population and pick finding (F-2, F-4, F-18, F-19) came from its fd column. The census's text proxy is what hid the LIBC site; a trace-record kit removes the proxy.
- The anchor map (kit/anchors_window.txt) was written ad hoc (no anchors.py exists in the tree); two lenses used it for F-9 within minutes.
- SOUND overran its own-C cap (12 compiles per real-site case); the brief's product line should have said "20 sites x 12 compiles = 240 + unit".
- The first `make` of the review tree was refused by the auto-mode classifier when backgrounded with a parallel copy command; the foreground retry ran (the background one had in fact completed).
- Lenses well-sized: no lens returned empty; the one sonnet lens (SIM) finished in 4 minutes with 4 good findings.

## Proposed changes
1. SKILL §5 run kit, design mode: "When the subject keys a rule on kit picks (finder row, frame), build the MF_TRACE harness (`make build/libpcrec_mftrace.a` + one cc link of cli/main.c with -DPCREC_HARNESS) and ship a per-site facts script (frame row, fd row, k) in the kit; never let a census's text proxy stand in for the pick" (r67: the proxy hid a LIBC site; the trace kit found it in 3 lenses).
2. SKILL §3.2 / §5: name `tools`-less anchor mapping: "if no anchor-map tool exists, the coordinator writes the function spans of every function the design moves/retires and the sabotage rows anchored in them into kit/anchors_*.txt" (r67 F-9: five rows the note never named).
3. critics.md, premise lens: "A claim that an existing CHECK is 'unchanged' when the subject adds text of a NEW spelling is tested by running the check's own regexes/legs on a hand-built instance" (r67 F-1: found by three lenses; the docstring said yes, the regex said no).
4. COMMON template: state compile caps as a product per probe case (r67 SOUND overran).

## Framework notes
- The coordinator pattern worked at full width with zero resends: five narrow lenses, pre-created files, lanecheck. Inline verification was cheaper than a verifier for 17 quote/grep/one-call items.
- A launcher-requested lens (SHIP-SIZE) composed cleanly with goals + rulings + general-form-with-triggers in one opus brief; its cut list was concrete because it ran its own census (SIZE-2), not only a count of surfaces.

## Time to draft
Freeze 00:38 -> critics launched 00:45 -> all complete 01:02 -> verified 01:10 -> draft 01:15. ~37 minutes.
