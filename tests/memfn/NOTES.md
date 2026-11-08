# tests/memfn/ — notes (history moved out of CLAUDE.md)

## run_proof.sh / proof_check.c, after D172 S2 commit 6

Since D172 S2 commit 6 (lane wsc6) the prefix facts, context spans, `absent`/`consumable`, `read_floor` and `consumer` are gone from the site, and their refusals, generated context items and SATISFIES cells with them; family A gains the window site's renderer-interface refusals (plant `S1419`); the oracle's floor is the FAILS cell below the subject; plants S1222/S1223/S1226 retired with their code, and S1255/S1256 were declared EQUIVALENT until D172 S3 retired RPT, kit_report_exact and mf_preview (lane s3): their plants, ZK6/ZK7, S1251-S1254, family D's preview checks and family C's preview renders went with them, and a REPORT site stated in terms is now REFUSED on every art (family A, C, D).

## targets

### The kit's CPU target table (lane k0, [XARCH-DEV] unit K0, R-36)
- **run_targets.sh**, **targets_check.c** — `make test-memfn-targets` (in TEST_SECTIONS; seconds; mech arm `memfntargets`, rows S2975-S2981): (1) the kit's table check's verdict (`memfn/tests/check_targets.sh`); (2) the kit's target ENTRIES against the design's rows spelled as literals in targets_check.c (floor 42 PASS lines; the host default list held to `uname -m`; the C spellings reached through `mf_target_c_of`/`mf_family_c_of`); (3) the compile cells: a kit-shaped `#if`-free fixture in the kit's own region and guard texts, 6 gcc + 3 clang cells, answers vs a naive finder, the objdump census, the family guard refusing `-m32` and aarch64 clang. RAN floor 6 gcc cells on x86-64; clang cells SKIPPED and counted where clang is absent. Rev 0's U1 harness (commit 171bdb343), its table now the kit's.

## run_targets.sh part 4 ([XARCH-DEV] U3, lane u3tgt 2026-11-08)
Real `pcrec -fmemfn-simd=TARGET` artifacts of `(?i)cat` (portable, x86-64,
x86-64-v3) at gcc / -march=native / -march=x86-64-v2 / -mno-sse2 / clang,
answers held to a naive caseless finder; the v3 object's ymm census; a
region-stripped v3 artifact must refuse at the default -march; the guard must
refuse gcc -m32 and clang aarch64. v3 cells are built but not run on a CPU
without AVX2. `simd_bounds.tsv`'s `target-text` row bounds the guard + region.

## simdfloor ([XARCH-DEV] U2+U3, lane u3floor 2026-11-08)

The target seam removed every CPU `#if`, so C18 was re-aimed rather than
retired (target_seam.md §6.4 had proposed retiring it). The population is
every corpus cell at `-fmemfn-simd=T` for each target T whose family has a
level (x86-64, x86-64-v3 today), against `-fno-memfn-simd`. simd_levels.c
dumps the levels AND the targets with their C text (region open/close, the
family guard, hex), so the lint's admitted spellings are the kit's own. Leg
(a) (off-target preprocessing) retired with the `#if` arms; leg (c) now
allows one replaced call per SIMD FUNC; C9's nm leg expects the called helper
at every `-march` cell (the region supplies the ISA). Five artifact plants
run on every target's first mover. Floors are per target and per level
(`FLOORS`). routing_shape.py admits the one-call selector naming a level
helper defined above it (libc_census reads it too). target_text.py is the ONE
reader of the target's own text (table, admission, the cut, `aside`): simdfloor's
lint cuts with it, and libc_census's movers half (R4) compares ON to the default
with that text set aside, so no check carries a second copy of the spellings.
