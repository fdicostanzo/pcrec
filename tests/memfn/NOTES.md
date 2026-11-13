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
Part 4b's F1 checks (lane u3d27, D27 region suite F1, ruling R2): two v3
compound controls (`^\s+|\s+$`, plain and `--emit-main`) and a v3 `--trace`
VM artifact hold no `#include` inside the
region, include no header twice, and every part's guarded count reads 0; the
`--emit-main` compound's count equals a plain `--emit-main` `abc` artifact's
(the target's text alone). Red on the pre-fix build; rows S1896-S1899.
`target_text.moved_out` sets OFF's copy of a moved header aside (simdfloor,
libc_census's movers half).

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
- policy_check.c (unit U2 fix, R-37): the kit refuses a site policy bit outside MF_P_KIT_NAMED at mf_define, hex in mf_art_error (unconditional since review 2026-11-08 r5 X-5 deleted the staging switch; linked against the library since); public header only; built by run_finder.sh (floor 4); S3000's detector.

## run_wreply.sh (moved verbatim from CLAUDE.md, lane u3d27, 2026-11-09)

- **run_wreply.sh** — the window family's REPLY check (D172 S2; wsc4, inverted at commit 5, reduced at commit 6 when the planner's pick and the inverse harness lever were deleted): every witness stamps its NEXT row at the default flags and compiles at five flag sets (K35 floors on cases and keys); REACH through a perturbed tree copy (RESEED unstated: no offset-set row, at least five witnesses moved; R stated under `-fno-run-prefilter`: the RE-SEED refusal fires); `--plants` S1413-S1414 each red (S1412 retired with the pick). Opt-in, no make target; ~10 s plus a tree build; takes the box lock.

## run_rank.sh / rank_check.py (full index entry, moved 2026-11-10 for the 12 KB limit)

- **run_rank.sh**, **rank_check.py** — (R17-a, lane r17a: the same probe build also carries N4's door assertion, `find_door` in src/gen/emit_dfa.c: where a defined FIND's ... SINCE D172 S2 COMMIT 6 (lane wsc6, the kit manager's R1) THE CLAIM IS INVERTED: pcrec hands the kit NO ranking (the ranking and `plan_hint` are the kit's renderer interface, written by the window family's translation), so every predicate of every PRE/OFS site carries rank_n 0 and names no RUN term; pcrec's ranking (`ofs_pred_rank`, `pcrec_find_run_rank`) and its rows S731-S737 retired, and S1420 (a ranking stated on a pre-check part) is the claim's failing direction. N4's door stays.

## Purity harness (memfn plan_frame.md 3.0b, lane b30b, 2026-11-12)

`arm_fixtures --purity` asks each site NONE and framed (DEFINE) between interleaved defines and
compares the WHOLE reply with a fresh art's (memcmp; `pur_diff` names the first differing member,
or "padding"). Every ask goes through `pur_ask`: the COUNTING HOOKS (every stated callback counts;
the call fixtures state all six: fn_name, table_name, note, note_tag, member, on_cand) and the
COUNTING ARENA (every purity art allocates through `pur_alloc`) must read 0 across the ask. The
arena's populations are counted (a framed E-find ask picking PAIR; a REPORT site refused under
`no-window-search`, reaching `why_room`), a count of 0 a named failure. The call fixtures
(`pur_call_fixtures`): UNSTATED and every call above EMIT refused (S); NONE's frame part zero (T)
and blind to frame fields and `def`; NONE and framed agree on the decision group
(`offsetof(mf_wreply, framed)`); EMIT walks DEFINE|USE (U: `pur_pf_site`, where the PF memchr row
serves the define and declines a non-jump `on_miss` at USE, so mf_define renders E-stmt and mf_emit
E-find); the site's `--memfn=` options reach a framed ask (I: REPORT under no-window-search refused;
under no-fd-d1 search LIBC iff the define's text calls memchr); the SAME-CLASS-DIFFERENT-TEXT
fixture (AD: STMT/ASSIGN, STMT/ON_MISS and the PF site asked with EMIT, each text hook renamed
within its class, miss = n's text and MF_MISS_N by address included; one class-breaking case
counted). `--purity-control` prints hex dumps of each site's NONE and framed replies after one
define, its STMT EMIT replies, and the PF site's. run_finder.sh also runs `fxt --purity` (the
MF_TRACE kit: the agreement at every purity define) and pins its E-func (81) and E-generic (8)
define counts EXACT; its control (E-func declined in `e_legacy_holds`) moved no purity check and
took E-func to 0 (b30b_report.md).
