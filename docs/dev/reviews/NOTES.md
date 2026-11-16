
## [FINDALL-NEXT] lane iterland: additions carried from lane/itertri (verbatim)

- `2026-10-21-r1-findall-i2.md` — light D6 panel (i2crit-chk checks/gate sonnet, i2crit-sem semantics/macro opus, i2crit-fam family/ABI/unlocks opus) on [FINDALL-NEXT] `findall_iter_i2.md` revision 1 (lane i2design; `next_n` + `RX_FOREACH`). No blocker; the macro text and the PCRE2/K75 equivalence were confirmed by hand. 21 findings plus a simplification: no A/A floor, no positive gain cell, and c6 explained by assumption (chk-1..3); the entry_shape arm was not an oracle; no batch-boundary sabotage; witnesses and reach were missing (chk-5..7); a start-4 fill scans bytes past an early stop; `rc` after a break; the call-count formula (sem-1..3); a separate `NEXT_N` entry breaks ".next_n NULL ⇔ .next NULL" (fam-1); flip to one body `__one` (fam-2); keep revision 3's stage numbers (fam-3). All ACCEPT / NOTE / UNLOCK (the manager, 2026-10-21); Q1-Q4 settled as the manager's call. Applied by revision 2 (lane i2rev); the disposition table is at the top, the critics' text verbatim below it.


## Index entries moved out of CLAUDE.md (merge of lane/memfn-mfind, 2026-11-15; size limit)

- `2026-11-12-r1-s1.md` (+ dir) — CODE round (post-landing) on set S1 (NEVER-MATCH empty artifact + FIND-MINW): no answer-level finding; FIX-NOW spec/comment/check items (CONTRACT-1/2/3, DFAMINW-1, NMSOUND-1/3, CHECKS-2..5), applied by lane s1fix.
- `2026-11-10-r1-docfmt.md` (+ dir) — DESIGN round on docs/design/doc_index_format.md rev 1 (index + details format): NOT READY; addendum census/ownership (F1), no G4 instrument (F2), currency vs faithfulness (F3); all dispositions ruled as proposed, applied in rev 2.
- `2026-11-10-r2-docfmt2.md` (+ dir) — RE-CHECK of doc_index_format.md rev 2: T1 ready with text fixes; 1.0 not ready (plain-line markers missed, per-owner multiset passes wrong splits); all ruled as proposed (R2-24 by the owner), applied in rev 3.
- `2026-11-06-r4-vlookbehind-code.md` (+ dir) — CODE round on lookbehind stage 1 (lane/vlbbuild): no answer/speed finding; FIX-NOW refusal shape (F1), four broken sabotage rows, missing lblow guard (hang under plant), DD12a key.
- `2026-11-06-r3-vlookbehind-ready.md` (+ dir) — LAST re-check of vlookbehind rev 4 (the $_fwd_step seam entry): READY WITH TEXT FIXES, applied by the stage-1 build lane.
- `2026-11-06-r2-vlookbehind-recheck.md` (+ dir) — RE-CHECK of docs/design/vlookbehind.md rev 3: READY WITH TEXT FIXES (F1 the bounded step is a second encoding splice: seam entry ruled; F2-F7 text).
- `2026-11-06-r1-arev-recheck.md` (+ dir) — RE-CHECK of docs/design/stream/arev.md rev 1: NOT READY (A1 `(?<*` row drops later branches, 1,702 of 552,900 cells; A2 the NFA cap refuses compiles range accepts; A3 read set); S1/S1M ready with text fixes.
- `2026-11-05-r7-alt-normal-form-ready.md` (+ dir) — readiness re-check of docs/design/alt_normal_form.md rev 2: READY WITH TEXT FIXES (stages 1/2p/2b; seethru hides the island's new set reading; merge deletes bare-class islands; dead S-m witness).
- `2026-11-05-r6-vlookbehind-recheck.md` (+ dir) — RE-CHECK of docs/design/vlookbehind.md rev 1: READY WITH TEXT FIXES (V1 trail sizing: vm_cost_look's constant 2 vs one entry per candidate); 76.7M-case literal interpreter 0 diffs.
- `2026-11-05-r5-arev.md` (+ dir) — DESIGN round on docs/design/stream/arev.md rev 0 (A-REV: one reverse automaton kind, lookbehind client): NOT READY, text rev 1; answer-level: `\G`/`^` in a lookbehind branch, per-branch yes/no; owner questions on the first cross-engine piece and proof-vs-speed trigger.
- `2026-11-05-r4-alt-normal-form-recheck.md` (+ dir) — RE-CHECK of docs/design/alt_normal_form.md rev 1: stages 1/2p ready with text fixes; 2b not ready (side effects between merged branches, `(?:ab|a\Kd|ad)`; two sibling-merge specs); flag-bit budget and D187 hull questions to the owner.
- `2026-11-05-r3-vlookbehind.md` (+ dir) — DESIGN round on docs/design/vlookbehind.md rev 0 (bounded variable lookbehind); NOT READY, text-only rev 1 (F1 retry-frame answer bug, stage-2 reference rules, 65535 ceiling, F12 fold is a width-selected emission); answers Frank's cap and back/forward-reference questions.
- `2026-11-05-r1-memfn-sp1d.md` (+ dir) — CODE round on span_pick unit 1d (one candidate builder, kit_pick_takes, T-VERIFY step list, purity harness, WCAND trace), coordinator round + verifier; no answer/speed findings, FIX-NOW F1-F7/F9/F11, F8 R21 recipe for main.
- `2026-11-05-r2-memfn-sp1e.md` (+ dir) — CODE round on span_pick unit 1e (one T-FIND walk, D-hors as fd's first row, declared renderer rows, wfD->fd row map, MF_CLASS_V 8), coordinator round + verifier; no answer/speed findings; FIX-NOW F1-F8/F11/F13/F14; PLAN F5+F9 one renderer table at 3.0.
- `2026-11-06-r5-altcode.md` (+ dir) — code round on the alternation normal form build (lane/altbuild 4cc816446); EMIT-1/2/3 speed fixes ruled FIX-NOW.
- `2026-11-06-r4-memfn-span-cards.md` (+ dir) — DESIGN round on docs/design/memfn/span_cards.md rev 0 (span_pick stage 2: cost cards, producer, noise channel, set format 2), coordinator round + verifier; NOT READY, rev 1 + re-check; no answer or byte finding; DEFAULTS reading to main; CONTRACT-5 (loader accepts value past MF_MEASURE_MAX) to main.
- `2026-11-06-r5-memfn-span-cards-recheck.md` (+ dir) — RE-CHECK of span_cards.md rev 1 (fix-induced + readiness + measurement + ruling), coordinator round + verifier; NOT READY as a whole: S2a/S2b ready with text fixes, S2c-S2e need rev 1.1 + a 2-critic re-check; EMBED/POLICY to main; DEFAULTS (B) had no record.
- `2026-11-06-r6-memfn-span-cards-recheck2.md` (+ dir) — 2-critic RE-CHECK (readiness + measurement) of span_cards.md rev 1.1, S2c-S2e; NOT READY: S2c/S2d ready with text, S2e after rev 1.2 (READY-1 base leaves `inputs`; a kit run record; deps recorded).
- `2026-11-06-r7-memfn-span-cards-ready.md` (+ dir) — one readiness critic on span_cards rev 1.2's diff: S2c/S2d/S2e READY with text fixes (READY-1..9, applied as rev 1.3 in S2c's first commit).
- `2026-11-06-r8-memfn-s2a.md` (+ dir) — CODE round on span_pick stage 2 unit S2a (noise channel, set format 2, MF_SITE_ABI 24); no answer/speed finding, zero movers held; FIX-NOW SEAM-1 (handed value missing from the digest) + checks/spec/house items.
- `2026-11-07-r1-xarch.md` (+ dir) — DESIGN round on docs/design/memfn/target_seam.md rev 0 (per-target variants, [XARCH-DEV]); coordinator + 6 critics + verifier; no answer finding; build failures under `-march=native`/clang (F3) and a stem collision (F4); FIX-NOW rev 1; CPU variant ruled a compound part (F6).

## Index entries moved out of CLAUDE.md (lane file28, 2026-11-16; size limit)

- `2026-11-06-r9-memfn-s2c.md` (+ dir) — CODE round on span_pick stage 2 unit S2c (the producer): emission byte-identical; harness-fidelity findings G1-G4 + window items; NOT READY until the FIX-NOW set lands; new lens row.
- `2026-11-06-r10-memfn-s2rev14.md` — one critic on span_cards rev 1.4 (fix-induced + fidelity + simulate), relayed by message: READY for window 2 with listed fixes; REV14-1 a consistent negative sign passes as zero, REV14-2 uncapped r, REV14-3 null_check substring; fixes on lane/memfn-s2c14fix.

## Index entries moved out of CLAUDE.md (lane file29, 2026-11-16; size limit)

- `2026-11-07-r11-memfn-s2rev15.md` — span_cards rev 1.5 critic (fused fact fidelity, est-commit bypass, value = max(0, med)); window 2 FULL accepted.
- `2026-11-07-r12-memfn-planframe1.md` (+ `2026-11-07-r12-memfn-planframe1/`) — plan_frame rev 1 (span_pick unit 3.0) critic: 5 opus lenses + verifier, F1-F34; not ready, rev 2 with text fixes; search/stream/check triple confirmed.
- `2026-11-07-r13-memfn-planframe2.md` (+ `2026-11-07-r13-memfn-planframe2/`) — plan_frame rev 2.1 readiness re-check: one readiness critic per unit plus fix-induced, R1-R28; 3.0a ready with text fixes, 3.0b after the R1/R2 shape rulings.
- `2026-11-08-r1-spanarms.md` (+ dir) — DESIGN round on docs/design/span_arms.md rev 0 (REP/EMPTY/LOOKAROUND arms): REP+EMPTY ready with text fixes; LOOKAROUND not ready (F1 guard met at the arm, F2 propagation, F15 D168); rev 1 by lane spanarms2.
