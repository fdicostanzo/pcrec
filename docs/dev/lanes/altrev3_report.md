# altrev3 report: docs/design/alt_normal_form.md REV 3 (text only)

Lane altrev3 (sonnet), base `783a45ec0`, worktree `worktrees/altrev3`, branch `lane/altrev3`.
Applies the RULED readiness review `docs/dev/reviews/2026-11-05-r7-alt-normal-form-ready.md`
(+ `verify.md`). Changes are tagged `(r7: ID)` inline; section 15 gained an r7 disposition table
and a "Readiness after rev 3" paragraph. Only `docs/design/alt_normal_form.md` and this report
changed. No src/cli/lib/memfn/tests edits.

## What changed (by finding)
- SND-1: premise test done first. `vm_isl_words`' A_ALT walk (`emit_vm.c:4115-4120`) and A_CAT walk
  (`:4139-4144`) step the left child through `pcrec_ast_seethru` (`internal.h:2322-2326`), so a class
  at a spine head never reaches the `A_WCLASS` arm (right slots do). Stage 1 now states an
  island-local step that stops at `A_WCLASS` (model: `vm_seethru`, `emit_vm.c:1587`);
  `pcrec_ast_seethru` stays (the chain-size walk `:4211-4222` needs it). S-i / S-i2 re-picked to a
  right slot (`x(?:1[éà]|q2|r3)y` 1, `x(?:1[éè]|q2|r3)y` 0), a head-variant count witness added,
  U4's prediction re-derived (equality inside an enclosing alternation, bare classes the only movers).
- RDY-1: bare-class island loss listed as a third D186 choice-cell family, bit 10 restores; U1 island
  row, U4, predicted movers, section 11 row.
- RDY-3: B0 part 1 adds `--dumps-declared-rows=--list-axes:altcls-merge` (two-row key caveat noted).
- SND-2: S-m replaced by `(?:ab\b|ad\b)`; the "remainder re-merge" claim re-worded in 2.2(5), 3.3 step 2,
  2b movers; `(?:abx|aby|abz)q` now `MERGES 1`/`FACTORED 0`.
- RDY-2: lowering merges not counted (stage 1), stamp unit at 2b = branch lists where M folded
  (`x(?:a|b|cd|e|f)y` 2 -> 1 is a listed stamp mover).
- RDY-4: 4.7 fence re-stated; 1e not landed; 2p bound only through stage 1.
- RDY-5=FIX-1, FIX-2 (two head columns + WRITES table + leak witness S-L), FIX-3, FIX-4, RDY-6, RDY-7,
  RDY-8+FIX-5 (bit-10 readers, 2b readers, depth limit `PCREC_MAX_ALTCLS_FACTOR_DEPTH` kept and
  re-worded, grep rule for 2p mech rows), SIM-3 (incremental structure + declared work bound row).
- DOC: SND-3, SND-4, SND-5, SIM-1, SIM-2, SIM-4..7, RDY-9, RDY-10, FIX-6 (carried to 2a), FIX-7, FIX-8.

## Probes (build at `783a45ec0`, worktree `make -j4`, utf8 `--engine=vm -fno-cls-kit`)
Islands/stamps today: `x(?:[éà]1|q2|r3)y` 1; `x(?:1[éà]|q2|r3)y` 1; `x(?:1[éè]|q2|r3)y` 0;
`x(?:[éà]|q2|r3)y` 1; `a[éÉ]b` 1; `(?i)xé+y` ISLANDS 2 RUNGS 0x4u; `(?:abx|aby|abz)q` MERGES 0/FACTORED 1;
`(?:ab\b|ad\b)` 0/1; `x(?:a|b|cd|e|f)y` MERGES 2; `(?<=foo)bar` req_run `626172@0`. All match the review.

## Cites changed (verified at 783a45ec0)
`vm_det_seq` :1885 -> :1883; `emit_dfa.c:3214` -> `emit_altcls_macros` :468 (call :15699);
`kindrow.def` -> `src/core/kindrow.def`; `req.c` lookbehind sentence is :55-60 (not :47-52).

## Not verified / judgment calls
- Hand-executed only (nothing built): S-m's new witness, S-L, `FACTORED 2` for `(?:ab\b|ad\b)`,
  `x(?:a|b|cd|e|f)y` -> MERGES 1 under the 2b unit.
- FIX-7 island budget equivalence stated as a requirement (U4 equality is the check); counter not read.
- Home choice for the module (FIX-4): `src/facts/` carve-out, per the ruling's first option; `src/core/` remains the alternative.
- `[RUN-POS-SET]` status line untouched (staging unchanged). §13 q5 stays OPEN.

## STATE AT HANDOFF
Committed on `lane/altrev3`; clean tree. Rulings file `docs/dev/lanes/altrev3_rulings.md` was empty at
every checkpoint (no entries applied). No STOP-RULE items: every fix was text.
