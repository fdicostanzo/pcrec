# tests/memfn/ — notes (history moved out of CLAUDE.md)

## run_proof.sh / proof_check.c, after D172 S2 commit 6

Since D172 S2 commit 6 (lane wsc6) the prefix facts, context spans, `absent`/`consumable`, `read_floor` and `consumer` are gone from the site, and their refusals, generated context items and SATISFIES cells with them; family A gains the window site's renderer-interface refusals (plant `S1419`); the oracle's floor is the FAILS cell below the subject; plants S1222/S1223/S1226 retired with their code, and S1255/S1256 were declared EQUIVALENT until D172 S3 retired RPT, kit_report_exact and mf_preview (lane s3): their plants, ZK6/ZK7, S1251-S1254, family D's preview checks and family C's preview renders went with them, and a REPORT site stated in terms is now REFUSED on every art (family A, C, D).

## targets

### The kit's CPU target table (lane k0, [XARCH-DEV] unit K0, R-36)
- **run_targets.sh**, **targets_check.c** — `make test-memfn-targets` (in TEST_SECTIONS; seconds; mech arm `memfntargets`, rows S2975-S2980): (1) the kit's table check's verdict (`memfn/tests/check_targets.sh`); (2) the kit's target ENTRIES against the design's rows spelled as literals in targets_check.c (floor 42 PASS lines; the host default list held to `uname -m`; the C spellings reached through `mf_target_c_of`/`mf_family_c_of`); (3) the compile cells: a kit-shaped `#if`-free fixture in the kit's own region and guard texts, 6 gcc + 3 clang cells, answers vs a naive finder, the objdump census, the family guard refusing `-m32` and aarch64 clang. RAN floor 6 gcc cells on x86-64; clang cells SKIPPED and counted where clang is absent. Rev 0's U1 harness (commit 171bdb343), its table now the kit's.
