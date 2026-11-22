freeze 2026-11-21T00:19:45-05:00 SUBJECT=dad0275802cc BASE=694d91dc4214 MAIN=051e78af2 REVIEWED=3f02ca8ab
051e78af228082a0375a5b5efb7efbcd74edf1fc 2026-11-21 00:05:44 -0500
setup: review tree built nice -j2 (~1 min); base + reviewed archives clean-built; 12 plants (11 compiler + S3450 script) built, all apply rc=0, build rc=0 (~4 min total)
kit: reused crit-k147fix kit (pc/cmp/match/oracle/p2probe/apply_plant/build_plants) repointed; cmp.sh gained TA/TB tree selector incl. 'reviewed'
smoke: (?<=qz)x?a: base 613a@1, reviewed 717a@-2, subject 613a@1, plant:S3455 717a (row reaches)
lenses: EMIT (opus, emitted-vs-replaced + contract, 800 compiles), CHECK (opus, check adequacy, owns plants, 500), TRADE (sonnet, trade audit + spec/doc + ruling quotes, 200) = 1500
launch 00:22
returned 00:33
agents: EMIT opus ~10.2 min, 58 tools, file complete, lanecheck DONE; CHECK opus ~10.1 min, 81 tools, complete, DONE; TRADE sonnet ~1.8 min, 25 tools, complete, DONE (16/200 compiles: thin but on point). All three final replies undeliverable (expected; files were the delivery). No resends, no nudges.
findings: EMIT 3 confirmed + 1 held (2 speed: EMIT-2 loss vs BASE x1.57 opt-in flags; EMIT-3 mixed x4.4 loss / x6 win default route); CHECK 3 confirmed + 1 suspected -> held by 3 coordinator plants (V1-M2 1 red, V2-M5 2 red, V3-Fa 11 red); TRADE 4 doc/record. No overlaps beyond EMIT-1/CHECK-2's encoding-keyed best note.
verification: inline (no verifier agent): stamps for EMIT-1/2/3 re-run, perf instructions:u taskset -c 7 -r 3 on EMIT-2/EMIT-3 (direction and order reproduced; English-text figure differs from critic's text), greps for CHECK-1/3, TRADE-1/2/3. ~70 coordinator compiles.
freeze drift: main 051e78af2 -> 2b4e56eab (D201 add. 1, unrelated).
blinding: wtprune --apply output at teardown printed OTHER worktrees' WIP commit subjects (l3feat) into the coordinator context AFTER the draft; no effect on the round. Critics saw none.
draft 00:36; worktree removed.

## Process observations
- Light 3-critic round fit the delta: ~10 min per opus critic, total ~650 of 1,500 compiles.
- The pre-built REVIEWED tree (3f02ca8ab) beside BASE paid off: EMIT's tri-tree compare separated "rule mover" from "reviewed-state mover" directly.
- CHECK's PLANT REQUESTS heading worked: three narrowing mutants decided in ~3 min of coordinator builds.
- The sonnet TRADE critic finished in 1.8 min with 16 compiles; its findings are records-only; the instruction table was (rightly) not re-timed.
- wtprune's report lists every worktree's commits, including denied lanes' WIP subjects.

## Proposed changes
- SKILL §3.2 (code mode): "For a FIX-UP round (scope = REVIEWED..SUBJECT), also build the REVIEWED tree and give the kit a tree selector for it" (EMIT used it on every probe).
- SKILL §5 (check-adequacy brief): "ask the critic for PLANT REQUESTS (exact SAB_BEFORE/AFTER) for single-disjunct mutants of any new predicate; the coordinator builds them before drafting" (r66 CHECK-4).
- critics.md contract lens: "a fact derived from OPTIONS to predict a later route is checked against every forced-on/forced-off row of that route's admission table" (EMIT-2).
- SKILL §6.4: run wtprune with output filtered to the round's own name (pipe to grep crit-TOPIC), so teardown does not print denied lanes' commit subjects.

## Framework notes
- The coordinator verifying inline (stamps + perf + plants) was cheaper than a verifier agent for a light round where every CONFIRMED was a one-call repro; the skill already allows it.
