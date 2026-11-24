# dptri report (triage of RED 200-dpfix-test)

## Summary
The one red section of 200-dpfix-test (87/87 sections ran, rc=2) was `test-registry`
(`make[1]: *** [Makefile:654: test-registry] Error 1`, build/dpfix_test.log:2454). Every other section green.
Cause: a stale expectation the branch owed, not a regression and not a box effect. Fixed in dbf4497de.

## Diagnosis
tests/registry/limits_check.sh failed 6 checks (log lines 2342-2347): the six `#define PCREC_UCD_NS_*`
numeric constants added in src/parse/ucd_tables.h:34-39 were on neither limits.def nor the LIMIT / NON-LIMIT allowlist.
No emitted bytes involved. The check ran in isolation after the fix: 44 passed, 0 failed.
Main at the merge-base has no such header, so the section is green there by construction (not run separately; nothing to compare).

## Class
- Defect class: a new file introduces numeric constants and the branch did not disposition them in the D107 numeric-constant scan.
- House rule broken: D107 / limits_check.sh 3a ("every numeric constant is a limits.def row or on an allowlist").
- Sibling count: the check itself is the population scan (scans every numeric #define/enum under src/, cli/, lib/); after the fix 0 undispositioned remain (44/44). Grep used: `command grep -rnE "#define +[A-Z_]+ +[0-9]+u?\b" src lib cli --include=*.h` plus the check's own masked scan.
- Class-level fix shape: the allowlist entry plus its documented "kind" paragraph (here a TENTH KIND, namespace bits of a generated table's row mask, the SIXTH kind's shape). Done. A future landing that adds a header with numeric constants should run `bash tests/registry/limits_check.sh` standalone (seconds) before queueing.

## Fix
tests/registry/limits_check.sh: six names added to the NON-LIMIT allowlist and a TENTH KIND comment. No src/ change, no emitted-byte change, no new mechanism.

## STATE AT HANDOFF
- Cancelled before editing: 201-dpfix-mech and 202-dpfix-sweep (both pending); 200-dpfix-test had already ended red.
- Queued (all refuse after 19:30): 200-dptri-test (the deliver owed key), PLUS EXTRA keys 200-dptri-mech and 200-dptri-sweep (same bodies as the cancelled dpfix ones, labels renamed). They queue behind 200-k155fix2-sweep.
- I did not run `make test-registry` under boxlock (box held by k155fix2-sweep); the limits check itself was run directly and is clean. The full `make test` is OWED: key dptri-test, log build/dptri_test.log in the dpcompact worktree.
- Rulings file dptri_rulings.md: empty at last read.
- Uncommitted noise: docs/dev/artifact_size_log.tsv is a test-run byproduct, not committed.

dirty-ok: docs/dev/lanes/dptri_deliver.txt
