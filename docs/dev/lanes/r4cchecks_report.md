# r4cchecks -- R-4 / R4c lane CHECKS (2026-10-06, sonnet)

Branch `lane/r4cchecks` (cut from `lane/memfn-r4c`). Touches only `tests/`,
`Makefile`, `docs/testing.md`, `docs/dev/lanes/`; nothing under `src/`, `lib/`,
`cli/` or `memfn/src/`. Box: Mac M1, gcc-16. Verdicts here are directional (the
Linux box is the reference).

## 1. Checks: population, state, controls

| check | entry point | population counted | state |
|---|---|---|---|
| C4 arch-blindness | `make test-memfn-arch` (`run_arch_blind.sh`, `arch_blind_check.py`) | 15 hits in 11 (scope,file,class) groups: code 1, doc 1, tests 13; allowlist 11 rows / 15 hits; plants per class (this box): see below | LIVE |
| C12 form ratchet | `make test-memfn-forms` (`form_checks.py`, `c12_ceilings.tsv`) | 26 forms in 12 groups: memchr 8 (emit_dfa.c), memcmp 1 (runcmp.c), runcmp-words 4, runcmp-bytes 2, walk-stmt 2, walk-open 3, walk-fmt 1, walk-back 1, span-index 3, span-decode 1; 12 ceiling rows | LIVE |
| C13 on_cand | same section | on_cand producers under src/cli/lib: 0 | UNREACHED, printed with its reason; turns FAIL the day a producer exists with C13 unbuilt (S527) |
| C14 shape bounds | same section | limits.def PCREC_OFSK_MAX_SET 4, memfn.h MF_MAX_TERM 8 (needs 5); 3 asserts (MF_MAX_TERM, npred u16, MF_MAX_BACK >= 1) compiled against `core/internal.h` + `memfn.h` | LIVE, plus a control: MF_MAX_TERM lowered to 4 must make the assert fire |
| C17 rule 2 (dynamic half) | `make test-memfn-manifest` (`site_census.py`, `site_manifest_check.py`) | kit calls under src/: 0; delegated rows: 0; 4 selftest lines on a SYNTHETIC caller | UNREACHED, loud ("declared UNREACHED (K35), NOT passed"); a delegated row with no caller is a FAIL; goes live at REPLACE |
| VM hybrid handoff reach floor | `make test-memfn-reach` (`run_handoff_reach.sh`) | 3/3 witnesses reached (floor 3) | LIVE |

Controls that do not share a source with what they control:
- C4: the allowlist's total floor `C4_ALLOW_FLOOR=15` is a literal in the script;
  plants are derived from the compiler (`cc -dM -E` ISA-flag diffs, resource
  headers, `-dumpmachine`); a class with zero plants is RED; the hex-escape
  negative control. Classes 7-9 are structural and use author-chosen synthetic
  plants (printed as such). Plants on this box (gcc-16/arm64, flags accepted
  `-march=native -mcpu=native -march=armv8.2-a+sve -march=armv8-a+crc+crypto`):
  class1 6, class2 8, class3 8, class4 4, class5 4, class6 2, class7 3, class8 1,
  class9 2. The held-out plants FOUND REAL GAPS in my first regexes on this box
  (AES, CRYPTO, SHA2, FP16_VECTOR_ARITHMETIC as ISA stems; `vshlq_n_u64`), which
  I widened; Linux may find more (the claim is narrowed exactly as §17.5 says).
- C12: `C12_CEIL_ROWS_FLOOR=12` is a literal; rows are ceilings in both
  directions (a stale high ceiling is red, so a blind lexer is red, never green).
- C17 rule 2: selftest = call discovery ignoring comment/string decoys, verdict
  logic (unlisted caller and unreached delegated row each fail), and the shim
  end to end on a synthetic caller. The full path (traced build + 300-pattern
  corpus pass) was proven once on a SCRATCH tree with a planted caller in
  `pcrec_memfn_stamps_render` and STAY flipped to `delegated`: traced build ok,
  108/108 compiles, 108 kit calls (1 per compile), verdict PASS; with the row
  not naming the caller: rule 2 FAIL without building. Not committed (scratch).

## 2. C17 re-key and census, as built

Rule 2 now keys on `\bmf_(define|emit)\s*\(` (comments/strings blanked, calls
attributed to the enclosing function). The "site" is the calling pcrec function,
mapped through each `delegated` row's emitters + companions (Q4: after REPLACE
the emitters column names the site builders). Over a corpus compile pass through
a traced build (the caller files recompiled with a test-owned shim, relinked over
a copy of `build/libpcrec.a`; no tracing hook in `src/`), every calling function
must be named by a delegated row and every delegated row must be rendered at
least once (a vacuous delegation fails). Corpus floor: 100 compiles of a
300-pattern deterministic sample of the `.rxt` `pattern` lines.

## 3. Sabotage evidence (all run from the committed HEAD bbf79863, scratch under build/scratch)

`bash tests/mech/run_sabotage_matrix.sh S5NN`, one row per run, each
`unexpected 0, undetected 0, unreached 0`:

| id | what | arm | result |
|---|---|---|---|
| S518 | ISA name (class 1) in emit_dfa.c | memfnarch | DETECTED, reach ok, 1fail/11pass |
| S519 | intrinsic (class 3) | memfnarch | DETECTED, reach ok |
| S520 | `#include` of a kit-internal header (class 9) | memfnarch | DETECTED, reach ok |
| S521 | `strcmp` on form_id (class 7) | memfnarch | DETECTED, reach ok |
| S522 | allowlist row inflated (stale) | memfnarch | DETECTED, pop ok |
| S523 | hex-escape exclusion removed | memfnarch | DETECTED, reach ok, 2fail/10pass |
| S524 | `memchr(` re-added in a listed emitter (C17 rule 1 stays green on purpose) | memfnforms | DETECTED, reach ok |
| S525 | vocabulary stops seeing memchr (C12 STALE) | memfnforms | DETECTED, pop ok |
| S526 | MF_MAX_TERM 8 -> 4 | memfnforms | DETECTED, reach ok |
| S527 | `on_cand` token with C13 unbuilt | memfnforms | DETECTED, reach ok |
| S528 | `if (0) mf_define(...)` in an unlisted function (rule 2 key) | memfnmanifest | DETECTED, reach ok (2/2) |
| S529 | `req_handoff_applies` declines the VM engine (no answer moves) | memfnreach | DETECTED, reach ok |

IDS USED: S518-S529 (the whole remainder of the kit's block S510-S529; highest on
main/branches was S517). New mech arms (closed vocabulary, registered in the
matrix driver's header comment and `case`): `memfnarch`, `memfnforms`,
`memfnreach`. Rows spell their ISA words from two shell variables because C4
scans `tests/mech/sabotages/`. Not built: a floor-only C4 row (deleting an
allowlist row always trips the NEW-hit rule first; the floor guards a
simultaneous deletion of row and hit); a C14 `limits.def`-raise row.
`[SABANCHOR]` (`scripts/m6read_check_sab_anchors.py`): 475 sabotages, 492 anchor
sites, all resolve. `make strict`: clean.

## 4. The witness

`tests/litscan/gen_handoff.py` +3 cases (regenerated `handoff.rxt`, purely
additive: +311 lines): `(ab)c?userpass` (handoff 3), `(x)?userz` (1),
`(?i)(cat)s?dog` (0, pair arm), each on the default and `engine vm` routes,
byte encoding, oracles python `re` AND libpcre2 (must agree; the generator
stops otherwise). Harness run of the whole file with this tree's build:
`bash tests/harness/run.sh tests/litscan/handoff.rxt` -> cases passed 2414,
failed 0 (the new cells included). `tests/memfn/run_handoff_reach.sh` asserts
each artifact has `RX_ENGINE "vm"`, `RX_VM_PREFILTER "hybrid"`,
`RX_REQ_HANDOFF "<k>"`, `handoff_position = rx_reqrun(` feeding the first
`rx_prefilter(`, the pair arm's locals for the third, and that the pattern is a
row of `handoff.rxt`.

## 5. What CORE / the manager need

- REPLACE edits (one number each): `tests/memfn/c12_ceilings.tsv` emit_dfa.c
  memchr 8 -> 2 (and any walk/runcmp row it removes); flips PRE/OFS/SETREST to
  `delegated` and re-points their emitters to the site builders (rule 3 then
  holds non-vacuously, rule 2 goes live and needs `build/libpcrec.a`: the
  section now depends on `all`). Rows that become fewer than 13 / 12 lower
  `C17_ROW_FLOOR` / `C12_CEIL_ROWS_FLOOR` in the same commit.
- S511 (stale pending row) is anchored in `emit_req_one_byte`; it must be
  re-aimed at a still-pending emitter when PRE goes delegated (scope.md §3).
- A new `src/` file that mentions an arch word or includes a kit-internal
  header is red in C4 by design; `memfn_stamps.c`/`axes_dump.c` include only
  `memfn.h` (class 9 clean).

## 6. OWED

- `make test` (full) -- not run; command: `make test CC=gcc-16 TMPDIR=...`.
  Each new section was run alone and is green: `make test-memfn-arch` 12/0 (11 s),
  `test-memfn-forms` 4/0 (0.4 s), `test-memfn-reach` 4/0, `test-memfn-manifest`
  26/0 (with `all`).
- Linux (ubuntubudu, gcc 15.x) run of C4: plants are box-dependent and may expose
  more class gaps; and of `test-memfn-forms`/`reach`.
- The I2 driver (waits for main's C0 `emit_sweep.py --extra`); I2's reach witness
  is the three handoff patterns above.
- C17's census over the REAL corpus with real callers: only provable at REPLACE.

## 7. Charter vs committed

- C4 with allowlist counted at birth: DONE (15 hits / 11 rows).
- C12 born with today's ceilings, single obvious literal per row: DONE (memchr 8, memcmp 1; 12 rows).
- C13 UNREACHED with reason printed: DONE (and red when a producer appears).
- C14 as §17 defines: DONE (+ control).
- C17 re-key to `mf_(define|emit)`, corpus-pass census, UNREACHED loudly: DONE (selftest + scratch end-to-end).
- VM hybrid handoff witness .rxt row + reach floor: DONE.
- Sabotage rows for the new checks: DONE, S518-S529, all DETECTED.
- tests/memfn/CLAUDE.md, tests/mech/CLAUDE.md, tests/CLAUDE.md, tests/litscan/CLAUDE.md, docs/testing.md, docs/dev/lanes/CLAUDE.md row: DONE.
- I2 driver: NOT BUILT (instructed). C5/C10: not in this lane.
