# altland — landing of [RUN-POS-SET] stages 1/2p/2b (lane/altbuild), 2026-11-07, sonnet

## Merge
- Premise: `lane/altbuild` = bc10e148b36728dc3809827d52347a164c4e0961 (as briefed).
- `git merge --no-ff lane/altbuild` (run alone): ONE conflict, `docs/dev/history/claude_md/docs__dev__lanes.md` (both sides' lane index lines appended; kept both). `tests/memfn/c4_allowlist.tsv`, `src/core/internal.h`, `src/gen/emit_vm.c`, `Makefile` auto-merged. No src/ or abi conflict. Merge sha **f77ed1130** (abi 97 over main's 96).
- Identity pins: FILEPIN and ABASEPIN re-pinned from c9dca3c84 to f77ed1130 (commit follows the merge).

## Checks
- `make -j8`: clean. `make strict`: "whole tree compiles clean with -Werror -Wshadow".
- `make test-registry`: rc=0, no `*** [test-` line (log: /var/tmp/pcrec-pcrec/scratch/altland/registry.log).
- `scripts/plan_lint.sh` (= test-plan-lint): 319 rows, 0 violations.
- OWED (the 19:00-01:00 hold blocks further solo runs; the first foreground run of test-codegen was left unread): test-codegen, test-memfn-arch (C4_ALLOW_FLOOR literal in tests/memfn/run_arch_blind.sh is 26; the allowlist count may need recomputing if this goes red), test-rxtsource, test-recursion-identity at f77ed1130. Queued as one job: KEY `main-altland-solo` (prio 50, cap 5400 s), script /var/tmp/pcrec-pcrec/scratch/altland/jobs/altland-solo.

## Plan items filed
- [RUN-POS-SET] status: stages 1/2p/2b LANDED. (No rows named [ALT-NF] exist in plan.md; [RUN-POS-SET] is the stage tracker and stays `started`: 2a, 3, 3m remain.)
- New rows: [ALT-NF-CHK] (CHK-1, CHK-3, CHK-4, TRD-3 pair test), [ALT-NF-SPINE] (SLOT-2 wider family, SLOT-5), [ALT-ISL-HOPELESS] (TRD-4, D77-held), [ALT-REQ-PIECES] (TRD-5 headroom).
- SLOT-8 member list added to [ISL-PRICE]. NOTED items need no row.
- Ledger: full_suite_ledger.md MAJOR line; D177 row 5 fires, row 4 now fires too (majors abi 94-97).
- Owed: compliance refresh (docs/pcre2_compliance.md, `compliance-refresh` skill).

## STATE AT HANDOFF
Merged and committed on main; not pushed unless stated by the handback. rulings file: none.
OWED: none (queued job main-altland-solo and the compliance refresh are the manager's to read)
