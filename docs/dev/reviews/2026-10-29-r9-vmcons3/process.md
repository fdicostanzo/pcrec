# process.md — critic round vmcons3 (design short re-check), coordinator log

- 15:08 coordinator start. Subject frozen: docs/dev/lanes/vmcons3_report.md @ 62980551b (snapshot subject_vmcons3_report.md, identical to main 362f8e2e1's copy).
- Build-landing commit: main 362f8e2e1 + lane/trailgc ffd1f578e (not yet merged; lands first). Main src/cli/lib/memfn == design base 26804bd46 (no commits touch them since), so no cited-code drift from the freeze.
- Review tree worktrees/crit-vmcons3: detached at main, `git merge --no-commit lane/trailgc`; 10 conflicts (docs/tests + src/gen/emit_dfa.c abi line) taken from trailgc's side (abi 93). `nice make -j2` unlocked, rc 0 at ~15:10. (Same slip as r8: build log first written to the $PCREC_TMPDIR root; moved to scratch/crit-vmcons3/build.log.)
- Lenses (manager-named): soundness (opus; enumeration + mis-typed-record clauses; focused on where rev 3 still lexes), fix-induced (opus; standing questions sibling-of-family and general form + unlocks folded in as its tail). Verifier opus.
- Denylist: lanes/ except the subject, its evidence, rev 2 and rev 1 reports; reviews except r3/r6/r8 .md; other worktrees and scratch (incl. scratch/vmcons3, crit-vmcons2); git log bodies; box queue; plan.md beyond a tag line.
- 15:11 COMMON + DELIVER files written; lanecheck parse dry-checked (rc 1, report missing, as expected).
- 15:11 launched sound (opus) and fixind (opus), unnamed, background, one message. Both returned in the launch turn (fixind ~14.5 min / 65 tool uses, DONE 15:24; sound ~24 min / 121 tool uses, DONE 15:33); final replies lost ("ended without SubagentHandback") as expected; files + .done markers carried everything. No resend or nudge.
- sound: 8 findings, all CONFIRMED; answer-level rule-as-written twins (for (c), not stock): SOUND-3 (clean kit-window slot write, 1:-1,-1), SOUND-6 (stride-k "class" reading, abc NOMATCH), SOUND-8 (stale RESTORE ordinal passes the slot-sequence S-6, 1:-1,8). Structural: SOUND-1 (SPAN init-only == LSET bytes), SOUND-2 (render-time placeholder domain \x01q makes R2-R4 dead), SOUND-4 (macro FRAMES exits + CALLOUT cursor write not in rows), SOUND-5 (respell truncate-regrow; nesting rule for tiling; same-length overwrite), SOUND-7 (uncut vs text offsets mis-slice windows under default comments).
- fixind: 12 findings (9 CONFIRMED-structural, 1 SUSPECTED, 2 tail). FIX-1 (SNAPSHOT/RESTORE drop out of "SET record" counters: nset/margin/emitted_set), FIX-2 (K2 omits program_bytes/entry-shape/frame lines), FIX-3 (= SOUND-1), FIX-4 (registry filled after the walk; respell; census domain), FIX-5 (kit purity column crosses D146/D147), FIX-6 (lexer+registry built ahead of reader: move to (c), D77), FIX-7 (E1 misses memfn arms, .rxt-source compiles, 60-byte prefix), FIX-8 (E4/E5 zero-count controls share source), FIX-9 (RESTORE renderer text wrong at R_c), FIX-10 (sibling fields), FIX-11 (text readers + name tables families), FIX-12 (record-then-render general form).
- Overlaps: SOUND-1 = FIX-3; SOUND-5 ~ FIX-4(ii) (respell); SOUND-2 ~ FIX-4(iii) (census lexed FINAL text, not render-time); SOUND-8 ~ FIX-9 (RESTORE ordinal/renderer); SOUND-3's decode out-parameter ~ FIX-5 (declared purity).
- 15:37 verifier launched (opus). Returned in the launch turn (~8 min, 71 tool uses); final reply lost as expected; verify.done at ~15:43. 11 HOLDS, 2 PARTLY (SOUND-6: rule 3 says "first-byte", the row does not; FIX-7: the 60-byte-prefix part REFUTED, emitters see the 2-byte placeholder), FIX-2 HOLDS stronger (PROGRAM_BYTES stamp moves on every DELETE). All 3 answer twins rebuilt from its own emission (SOUND-6 with a different D shape), base = libpcre2 on every subject. One citation fix: CALLOUT lines 9082/9146-9148, not 9055/9141-9143.
- 15:44 review.md drafted (r9 free); COMMON, critic texts, VERIFY_BRIEF and verify.md copied to review/. 15:44 review worktree removed via `wtprune --apply --force --quiet-min 1 crit-vmcons3` (uncommitted merge diff saved by wtprune to worktrees/.wtprune.force/crit-vmcons3-20261029T154454.diff, its standard behaviour; safe to delete). No box load after ~15:40; nothing near the 19:00 window.
- Time launch-to-draft: 33 minutes (critics 22, verifier 8, drafting 3). Zero manager turns.
- Blinding: no denied file opened by any agent (all three say so). The lane's run.sh hard-codes `worktrees/vmcons3` for the watchdog path (the critic repointed its copy; a nit for the evidence, not a leak).

## Per lens

| lens | raised | CONFIRMED | verified | answer-level (twins, for (c)) | overlaps |
|---|---|---|---|---|---|
| soundness | 8 | 8 | 7 HOLDS, 1 PARTLY | SOUND-3, SOUND-6 (PARTLY), SOUND-8 | SOUND-1=FIX-3; SOUND-2~FIX-4(iii); SOUND-5~FIX-4(ii); SOUND-8~FIX-9; SOUND-3~FIX-5 |
| fix-induced | 12 | 9 structural + 1 SUSPECTED + 2 tail | 7 HOLDS, 1 PARTLY, 4 judgment | none | as above |

## Process observations

- Third two-opus-lens + opus-verifier re-check of this subject; fastest yet (33 min), zero delivery failures, files + .done markers carried everything.
- The enumeration and mis-typed-record clauses again closed the class they target: no printing-operand mis-typing survived. The holes moved to (1) post-render rewrites and check DOMAINS, (2) NON-PRINTING operands, (3) denylist-shaped rules over untyped text. The lens table's soundness row does not ask about either of the first two; soundness found them because the brief's "Method" told it to try each axis and name each check's text domain (r8 proposed change 3, put into this COMMON).
- The fix-induced lens's FIX-6 (move the lexer out of (a)) is the round's highest-leverage proposal: it is a scope judgment, not a defect, and only a lens asking "what does each addition cost / who reads it" finds it.
- Overlap again high (5 pairs) on structure: the defect class is real.
- Verifier's reading-judgment duty (r6 change 3) paid off: it downgraded SOUND-6 to PARTLY by citing the design's own rule-3 sentence, and refuted FIX-7(3) from the placeholder mechanism.

## Proposed changes

1. **pcrec-critic SKILL.md, soundness row** — append: "...and list every transform applied to the text AFTER a record renders it (post-passes, prefix/placeholder rewrites, copies) and which domain each check reads (render-time, final, offsets in which units); and for every operand an analysis reads, whether it PRINTS: a non-printing operand needs a non-text detector." Observation: SOUND-2/5/7 (domains), SOUND-1/6/8 (non-printing).
2. **COMMON template, Method** — keep r8's axis/domain sentence (it worked); add: "For a rule over untyped text, try writes and exits that are not spelled the way the rule's examples are (a builtin, a pointer alias, a statement expression, a macro, an out-parameter)." Observation: SOUND-3's 15 shapes.
3. **docs/dev/guide/critics.md lessons** — the four in review.md.

## Framework notes

- 2026-10-29 vmcons3: fourth same-day coordinator round on this design family; 33 min launch-to-draft, zero manager turns, 3 answer twins + 15 structural findings, all verified independently. Rounds on successive revisions are getting cheaper (r6 ?, r8 42 min, r9 33 min) while still finding a real class each time: the coordinator pattern scales to iterated design review. The pattern of "each revision closes the named class and exposes the next one down" (existence -> kind -> domain/non-printing) suggests the coordinator should, in its draft, name the NEXT likely class for the following revision, so the manager can ask the design lane to pre-empt it.
