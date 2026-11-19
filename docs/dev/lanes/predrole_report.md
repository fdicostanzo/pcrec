# predrole report

## STATE AT HANDOFF
Branch lane/predrole, committed. Rulings file empty: last R-n applied: none. Validation complete, nothing owed.

## WHAT CHANGED
- scripts/session_role: registers and `--get` returns role `pred` (usage 64 for others, as before); header updated. Premise test: `session_role pred abc123` with a scratch HOOK_ROLES_DIR registered after the change.
- scripts/hooks/post_compact.sh: `pred)` case naming the predicate-language manager, telling it to re-read docs/dev/pred/wake.md in full, then from_main.md and the end of COND-FAMILY.md, and refresh pred/owner.md. Inlines the wake (worktrees/pred copy preferred, to WORK QUEUE, 6000 bytes max) and pred/owner.md when readable (same lookup, 2500 bytes max); total about 9 KB worst case against the main role's 5000 + owner view and the kit's 7000, under the 10,000 inline limit. No-role help text names pred.
- scripts/hooks/monitor_unread.sh: role pred exits before monread (prints nothing, consumes nothing); no-role notice names pred.
- scripts/gestalt: unchanged. Read: the three `case $r in main|kit)` sites (gone-session, context, transcript size) skip a pred role file; the session line shows a `[pred]` label for a live pred session, harmless. No GONE line for pred.
- Docs: scripts/INDEX.md (3 lines), scripts/NOTES.md (role paragraph), pcrec-predicate-manager SKILL.md section 1 step 1 reworded; scripts/CLAUDE.md names no roles, unchanged. Lanes history index line added.

## TESTS
Extended scripts/tests/hookrole.test (the existing self-test of all three scripts): pred register/--get round trip, unknown role file still exits 1, monitor_unread silent with no cursor moved or created for pred, post_compact for pred names and inlines the wake and owner (not the others'), branch copy preferred, no-role text names pred.
- `bash scripts/tests/hookrole.test`: `hookrole.test: 22 passed, 0 failed`
- `bash scripts/test_queuemon.sh`: `queuemon test: 49 passed, 0 failed`
- `make -s strict`: clean.

## NOT DONE
Nothing. No hook registration or settings change (none needed: the hooks are already registered). docs/dev/pred/owner.md does not exist yet, so the owner inlining is exercised only by the scratch test.
