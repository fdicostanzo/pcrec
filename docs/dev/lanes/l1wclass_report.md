# l1wclass (lane l1tri, 2026-11-19; renamed: the name l1tri was taken by the 2026-10-11 lane) report

## Summary
test-cpset-structure red (rc=2 is make's Error 1, not a setup fault) was wclass census [5b]: remodel 3 (7581123e4) put `case A_CLASS: case A_WCLASS:` in one label run in desc.c `pcrec_ph_node` and altnf.c `anf_head`.

## Diagnosis
Real structural regression of a gate rule, not an answer change: anf_head_pos returns NULL for A_WCLASS so behaviour is a wall, same as main (main had A_WCLASS in its own arm). The census forbids any shared run textually. Only [5b] failed (24 pass, 1 fail in that section).

## Fix
Separate `case A_WCLASS:` arms in both sites, desc.c via a small static helper ph_leaf. No behaviour or emitted-byte change.

## Re-validation
make -j16 clean; make test-cpset-structure: 29/0, 25/0, 59/0 passed/failed, no Error lines. Control on main not run (main's altnf has the separate arm by inspection).

## STATE AT HANDOFF
Rulings applied: none. Queued runs: none.
OWED: none
