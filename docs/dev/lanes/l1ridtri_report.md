# l1ridtri report: cloud recidentity red on L1 merge d68a1294c

## Summary
Class (a): a recorded-baseline gate that L1's intended movers legitimately change. Not scaffolding, not infrastructure. Fix: (B) FILEPIN re-pinned b2d73b6b1 -> d68a1294c in tests/codegen/run_recursion_identity.sh (one line, no heavy run). ABASEPIN stays.

## What recidentity compares
`make test-recursion-identity` (tests/codegen/run_recursion_identity.sh), on 5 axes. (B): whole-file bytes of every call-free corpus pattern vs a build of FILEPIN. (A): the program region ('goto <p>_L0;'..'<p>_accept:') vs ABASEPIN. A landing that moves emitted text on purpose re-pins in its own change.

## The failure
Run 44644238214, shard test.log: (B) differing=49 default (4683 same), 48 vm, 49 noprefilter, 49 nocaptures; (A) differing=0 on every axis; linkage 0; refusal-mismatch 0; stamp-moved 0. Only the first 20 DIFFERS names are printed (head -20).

## Cause
The 20 printed: (?:abc)+d (run_pin rule) plus 19 positive-lookaround patterns. 11 of the 19 are in the l1ffix census observed.tsv as movers (req_byte/req_set/req_whole_run/landmark facts); the other 8, e.g. (?=fgh)\w{3}, (?=kev)[\x01-\x80]{3}, (?=47)\d\d-\d, are not in that older file (it predates later l1wclass and tail work), so I did NOT match each of them to a census row. Program region unchanged (A=0) fits facts-only movement. l1ftri2_report: feature-population c-default 62 movers, every one a census mover. No src/cli/lib/memfn commits since d68a1294c.

## Fix or re-pin
Done: FILEPIN -> d68a1294c with a history comment. ABASEPIN unchanged (A clean). With FILEPIN at the subject's own commit, (B) compares equal by construction.

## STATE AT HANDOFF
Rulings file: empty; none applied. OWED after 07:00 (heavy): confirm the 49 are all census movers by running the gate against the OLD pin (`RECURSION_IDENTITY_FILEPIN=b2d73b6b1 make test-recursion-identity` on d68a1294c, full DIFFERS list via KEEP=1 or a raised head -20) and checking against the l1ftri2 ident_check census; then re-dispatch the recidentity kind on the landed fix via scripts/cloudrun. Nothing dispatched.
