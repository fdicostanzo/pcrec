# r23 — [MEMFN] R-23: `mf_site.body` is a STATED fact (MF_SITE_ABI 13 -> 14)

Lane r23 (sonnet, 2026-10-17), branch `lane/r23` off `lane/memfn-r23` (c55d9f63d). Kit + pcrec builders in one
change set, so the field is never unstated in between. No pcrec abi event, no `MF_VOCAB` move, no layout move.

## What changed

- The enum already had `MF_BODY_UNSTATED = 0` (R-19, abi 12; the renumbering R-23 asks for was done then). What was
  missing was the refusal and the removal of the default: pcrec's common constructor wrote ONESHOT over the zero.
- `memfn/src/compose.c` `site_check` REFUSES `body == UNSTATED` (`mf_define` and the define-time query `mf_ask`
  both go through it), alongside the existing PARAM-reserved and out-of-enum refusals. Modeled on `need`'s
  `pred_kinds` refusal (B2).
- `pcrec_memfn_site` (src/gen/memfn_sites.c) no longer writes `body`; each builder states ONESHOT.
- `MF_SITE_ABI` 14, with the history sentence and the `mf_body` / field comments.

## Reader list found by grep (memfn/src, memfn/include, tests)

| reader | what it does with `body` |
|---|---|
| memfn/src/compose.c `site_check` | enum range, PARAM reserved, **UNSTATED refused (new)** |
| memfn/src/gate.c `cl_body` | classifier for the finder rows' `uses` (R1, R2, R8); its -1 (UNSTATED) arm is now unreachable behind `site_check` (comment says so) |
| memfn/src/finder.c rows' `FM(body)` uses + `FLD_body`; fields.def ONESHOT/PARAM classes | gate vocabulary only; reached after `site_check` |
| memfn/src/formhash.c `canon` | a kit-side BUILDER (the form hash's synthetic site); already stated ONESHOT |
| memfn/include/memfn.h | declaration and comments |

The refusal is the one reader that decides; the gate/finder readers only see stated values now.

## Builder list found by grep (every caller of `pcrec_memfn_site`, every `mf_site` initialization)

pcrec: `pcrec_memfn_span_site` (N7) and `pcrec_memfn_advance_site` (STAY / EDGE / VMSPAN / VMSTRIDE) in
src/gen/memfn_sites.c; `req_site_define` (DELEG_PRE), `find_site` (PF / hat / MLINE, also the readers' constructors)
and `ofs_site_define` (DELEG_OFS) in src/gen/emit_dfa.c; `vm_run_site` (DELEG_VMRUN) in src/gen/emit_vm.c. Six
callers of the constructor, all now state `s->body = MF_BODY_ONESHOT`. No other `mf_site` allocation exists in
src/, cli/, lib/.
Kit/tests: tests/memfn/arm_fixtures.c `base_site` (every fixture's constructor) and `fd_pf_site` (explicit);
G2's `g2_win` fills ONESHOT at the kit call the way it fills `need` (`g2_body_fill`, g2_gen.c and g2_simd_gen.c).

## abi readers re-pinned

MF_SITE_ABI is read by: memfn/include/memfn.h (the macro and its history), memfn/CLAUDE.md, memfn/include/CLAUDE.md
(both carried "13"), every site builder through `s->abi = MF_SITE_ABI` (formhash.c, pcrec's constructor, G2 /
fixtures) and the kit's `abi != MF_SITE_ABI` checks. No test, pin, spec sentence or manifest cites the number 13 as a
value (grep for `SITE_ABI.{0,6}13` found only dated history comments, left as history); G2's `abi-mismatch` uses
`MF_SITE_ABI + 1`. docs/spec has no reader. The suites that count (registry, codegen, G2, rows) moved nothing.
The kit ledgers (memfn/docs/responses.md, journal.md) are the kit manager's.

## Fixtures and sabotage

- G2 (refusal family, g2_gen.c): `body-unstated` (fill off), `body-param-reserved`, `body-out-of-enum`, over a
  baseline that states ONESHOT through the fill; the whole generated population renders with ONESHOT stated.
- finder_check.py family I rewritten: every body value is stated once — UNSTATED, PARAM and out-of-enum (9) are
  REFUSED naming `body` (new `--fd-site` fixtures `set10-param`, `set10-bodyoor`; `set10-nobody` left FD_SITES),
  ONESHOT is accepted and R1's gate does not name `body`.
- **S1089** (tests/mech/sabotages/): the `site_check` refusal removed; arm `memfnfinder`; solo `run_sabotage_matrix.sh S1089`
  at tip e0f739f01: **DETECTED, memfnfinder 1fail/907pass**. S1090 unused.
- **S919 RETIRED as declared UNREACHED** (not asked for; forced): its plant (the gate reads an UNSTATED body as
  ONESHOT) acts on a state no site reaches any more. Same retirement shape as S685 (SAB_REACH_POP on the finder
  check's old `body:R1:UNSTATED` line; solo run: UNREACHED (EXPECTED), reads NOW REACHED if it returns). Say if
  you would rather delete the row.
- tests/mech/CLAUDE.md, run_sabotage_matrix.sh's arm note, memfn/, memfn/include/, memfn/src/, tests/memfn/,
  src/gen/ CLAUDE.md updated.

## Validation (Linux dev box, `taskset -c 12-15`, `-j4`; logs in `build/land/`)

Verdict reading: `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` is empty for every section below.

| step | result |
|---|---|
| make, make strict | clean, `-Werror -Wshadow` |
| test-codegen | rc 0 (3 min 27 s) |
| test-registry | rc 0 |
| test-memfn-finder | 908 passed / 0 failed (was 894+ at B2: the body family replaced two checks, FD_SITES lost one site) |
| test-memfn-rows | rc 0 |
| test-memfn-g2 (quick) | 52,987,697 checks / 0 failed |
| test-cand-oracle, test-spec-history | rc 0 |
| also: test-memfn-arms / deleg / manifest / forms / link / stamps / reach | all rc 0 |
| emit_sweep vs `--ref-bin` = build of c55d9f63d (`git archive` into build/ref/) | see next table |
| `MEMFN_REACH_ONLY=1 AXES=--memfn bash tests/axes/run_axes.sh` | 257 passed / 0 failed ("memfn arm: OK") |

emit_sweep (argv 5,790 per arm, composition files 386; every stream `movers=0 asymmetric=0`, all tag and differ floors held):

| arm | wall | composition producing / artifacts | movers |
|---|---|---|---|
| plain (+ dumps) | 73 s | 37 / 106 | 0 |
| `--arms start` | 11 min | 37 / 106 | 0 |
| `--extra=-fmemfn-simd` | 1.6 min | 37 / 106 | 0 |
| `--extra=-fcomments` | 1.7 min | 37 / 106 | 0 |
| `-e utf8` | 2 min | 36 / 104 | 0 |
| `--engine=vm` | 1.4 min | 37 / 86 | 0 |

Self-check (ref vs ref) was skipped (`--no-self-check`, chain.sh's flags); every stream's REACH is the argv
population above, not an empty one. The landing bar (zero artifact movers on every arm) is met.

## OWED (heavy; none run, none expected to move)

full `make test`; the derived mech rows (the 51+ anchored memfn rows are untouched: this change edits compose.c /
gate.c comments and one line in `site_check`, so only rows anchoring `compose.c` text near line 496 could re-aim —
SABANCHOR in `make test-codegen` passed); G2 full (`make test-memfn-g2-full`); N2 census. The `--variant`, trace
and rwquest / synthetic-set arms of fdb2's chain were not part of this brief and were not run.

Process notes: `tests/mech/run_sabotage_matrix.sh` writes its scratch under `$TMPDIR` — I set it to
`build/scratch` after the first S1089 run used the default (/tmp); that first run's scratch dir was removed by the
script itself (verified absent). Nothing else was written outside the worktree.

## Charter checklist (R-23)

| R-23 landing bar | status |
|---|---|
| `body` zero is UNSTATED, no reader treats it as a body | done (enum already; `site_check` refuses; gate arm unreachable) |
| every kit reader refuses an UNSTATED site | done (single deciding reader, `site_check`, covers mf_define and mf_ask) |
| constructor no longer writes ONESHOT; pcrec builders state it, same commit | done (6 builders) |
| MF_SITE_ABI 13 -> 14, readers by grep | done (above) |
| zero artifact movers, every emit_sweep arm incl. the --memfn arms | done (6 arms + memfn reach arm) |
| G2/finder fixture stating every body value | done (finder family I, G2 refusal cases) |
| one sabotage row, UNSTATED body must be refused | S1089 DETECTED |
