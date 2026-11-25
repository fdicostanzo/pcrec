# arvfile report (docs only)

## Summary
Recorded D204, filed the kit architecture review's suggestions (ARV-1..18) as plan rows, rewrote [SP1D-KITSPLIT-SEAMS] to its seam facts, and added the note's section-6 register rows to architecture.md part 3. Validation: `make -s test-plan-lint` 0 violations (434 rows, selftest 45 plants); `scripts/check_claudemd_size.sh --all` within limits. Nothing under memfn/ edited.

## D204
docs/dev/decisions.md, end of file: the owner's two messages verbatim (to the kit via /q, 2026-11-24), the accepted readings ((A) at NEON V's trigger, split BEFORE NEON V, primitives move once to a file taking kit_mass), the file interface rule (table + its search functions in one file, table static, public names only those), what it overtakes ([IR-FORM] member (4) "do not split now", for window.c at this trigger only), and "yes on trigger" = direction; the build go comes at design delivery after r95 (memfn-winsplit).

## Plan rows
Under [KIT-ARCH-STEP] (now: stage 2 DONE, stage 3 in force), as children, state not-started: [KIT-WINSPLIT] (ARV-5+9+16, waits on the design note, r95 and the owner's build go), ARV-1-NONE-NOTED, ARV-2-KIT-HISTORY, ARV-3-CALLER-CLASS, ARV-4-DRIFT (main's), ARV-6-SELECTOR-WRITER, ARV-7-TEXTBUF-LEAF, ARV-8-REACH-TABLES, ARV-10-ONE-DENY, ARV-11-SPELLING-HALF, ARV-12-RENDERER-IFACE, ARV-18-SECOND-MECHS. Leave-its in Deferred with triggers: ARV-13, ARV-14 (its own per-member triggers, not Q36), ARV-15, ARV-17. ARV-10's next: names that registry.md section 6 para 7 is NOT amended here (main's, only if an options row is taken). ARV-1 and ARV-18's register rows are written; ARV-1's row asks main to delete it after review; ARV-18 still owes P2's census row (the kit's).

## Register rows
architecture.md part 3, rows 31-51: 2 noted (ARV-1), 10 implement-then-replace (ARV-18, rows 33-42), 43 KIT-WINSPLIT, 44 spelling/selector, 45 layer order, 46 REACH, 47 deny, 48 renderer interface, 49-51 noted (ARV-14). KINDS OF ROW sentence updated. No existing ruling changed; the note's row-10 WHERE drift is already correct in the register (memfn.h:308). Noted rows' commit column reads "commit at landing" for main to fill.

## STATE AT HANDOFF
OWED: none
Done; complete. Rulings file arvfile_rulings.md was empty at the last re-read.
