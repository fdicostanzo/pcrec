# r24 — [MEMFN] R-24: `mf_prov` carries the answering block's `bytes` and `fidelity` (MF_SITE_ABI 14 -> 15)

Lane r24 (sonnet, 2026-10-17), branch `lane/r24` cut from `lane/memfn-r23` (e09748b9b). No pcrec abi event, no
`MF_VOCAB` move, zero artifact movers. Stacked on R-23; nothing from E-1 (`lane/e1build`) was imported.

## What changed

- `memfn/include/memfn.h`: `mf_prov` gains, appended after `digest` and in the request's order, `uint64_t bytes`
  (the exemplar byte count the answering block declares, 0 when it declares none) and `uint8_t fidelity`
  (new `mf_prov_fidelity`: `MF_FID_UNSTATED = 0`, `VERBATIM`, `ADAPTED`, `SYNTHESIZED`). `MF_SITE_ABI` 15 with its
  history sentence. The enumerator spelling and values are window_contract.md rev 3.1 §3.1's.
- `src/gen/memfn_sites.c` / `.h`: `pcrec_memfn_prov_stanza(mf_prov *, bytes, fidelity-token)`, the mapping. A row
  table (`prov_fidelity_rows[]`), one row per token; NULL is the UNSTATED zero; a word outside the set returns -1 and
  writes nothing (the caller refuses; the schema closes the set at parse, so a miss is pcrec's own defect).
- Check: `tests/memfn/prov_check.c` (layout `_Static_assert`s and the mapping driver), built by `run_finder.sh`,
  held by `tests/memfn/finder_check.py` family L; `arm_fixtures.c` gains `--fd-site SITE --fd-an FID`.
- Sabotage: **S1092**, arm `memfnfinder`.
- CLAUDE.md files: memfn/, memfn/include/, src/gen/, tests/memfn/, tests/mech/, docs/dev/lanes/ (index).

## 1. The fidelity vocabulary's source

`src/parse/rxt_schema.def:278`, the PROVENANCE row `fidelity`: `closed fidelity verbatim adapted synthesized`
(`build/pcrec --list-schema` line 89 prints it; docs/spec/rxt_format.md:908). The same closure is the `adaptation`
row's rule at `:279` ("required-if fidelity != verbatim"). It is also carried as a string in `RxtFindBlock.fidelity`
(`src/core/internal.h:6114`) and printed by `src/parse/rxt_source.c:4771` and `src/dump/findings_dump.c:246`. No C enum of
the tokens exists in pcrec on this base: the mapping table is the first enumerated spelling, so check family L reads
the closed set off `--list-schema` and holds the table to it in both directions. The schema requires the row only under
a PATTERN block (data blocks, the exemplars E-1 reads, state none: `UNSTATED`).

## 2. What the base has, and what E-1's merge must wire

On this base **no analysis object is built** (`grep mf_analysis src/` is empty; `mf_art_begin` is handed NULL), and
`PcrecFindTblBlock` (src/core/findings.h) carries no provenance stanza. So there was no existing pcrec mapping for
`mf_prov` to extend. The new function IS the mapping; nothing on this base calls it (the check does). I did not read
`lane/e1build`'s code into the tree; reading it (read-only) shows its shape: `PcrecFindTblBlock.prov_bytes`
(`unsigned long long`) and `.prov_fidelity` (`const char *`, NULL if none), `PcrecFindOffer.bytes`/`.fidelity`, and
`pcrec_memfn_analysis_build` in `src/gen/memfn_sites.c` filling `k[i].prov.source/bundle/digest`.

E-1's merge must wire exactly:

1. In `pcrec_memfn_analysis_build`, where `k[i].prov.digest = o.digest;` is set, add
   `if (pcrec_memfn_prov_stanza(&k[i].prov, o.bytes, o.fidelity)) pcrec_ctx_fail(cx, 0, "internal error: ...");`
   (the two lines the request names; `o.bytes` is `unsigned long long`, `o.fidelity` the stanza's token or NULL).
2. Its `KSRCTRACE object` record already prints `o->bytes` and `o->fidelity`; it can keep doing so (they are the
   same facts) or read the kit-side fields back.
3. E-1's `analysis_invariant` already requires `bytes == 0` under PRIOR_NONE; the fidelity of a PRIOR_NONE or ABSENT
   kind is UNSTATED by this mapping when the offer's token is NULL.
4. Drop `PcrecFindTblBlock.prov_fidelity`'s own validation if it has one: the closed-set check lives in this mapping
   and in the schema, and a duplicate set would be a second spelling of the vocabulary.
5. D162 add. 4 / E-1's D2 (`synthesized` stated as `MF_PROV_PRIOR_AUTHORED`, never `measured`) is pcrec's `source`
   mapping, independent of `fidelity`; this change leaves it alone and the kit never re-derives it from `fidelity`.

## 3. No kit row reads either field (by grep)

`grep -rnE 'mf_prov|mf_akind|MF_FID_|fidelity|->prov\b|\.prov\b' memfn/src` is **empty**. The kit's only touches of
the analysis object are `kit.h:256` (`const mf_analysis *an;`) and `compose.c` (`art->an = an;`, "DECLARED (E-1): no
row reads it before B3a"). The finder check (family L) repeats the grep every run (zero hits required) and renders two
sites (`set10`, `byte1t`) on the plain and the `-DMF_TRACE` driver with no analysis object and with one stating each
fidelity (UNSTATED, the three tokens, and an out-of-enum 9), demanding byte-identical stdout and stderr (the traced
shadow's records included). The kit does not validate the field either (an out-of-enum value is accepted unread);
a future reader that refuses one changes that check, deliberately.

## 4. abi readers (MF_SITE_ABI), found by grep

`grep -rnE 'SITE_ABI|site abi' memfn src cli lib tests scripts docs/spec Makefile` (and for the literal 14 near it).
Readers of the CURRENT NUMBER, re-pinned: `memfn/include/memfn.h` (the macro and its history sentence),
`memfn/include/CLAUDE.md` ("carries `MF_SITE_ABI` 14" -> 15, history clause added), `memfn/CLAUDE.md` (R-24 paragraph).
Every site builder writes `s->abi = MF_SITE_ABI` by name (formhash.c, src/gen/memfn_sites.c, tests/memfn/arm_fixtures.c)
and the kit checks `abi != MF_SITE_ABI`; G2's `abi-mismatch` uses `MF_SITE_ABI + 1`. Hits that cite 14 as a value are
dated history comments ("since MF_SITE_ABI 14", R-23's refusal text in `compose.c:498`, `gate.c:540`, G2's
`g2_gen.c`, S1089/S919) and stay true. `docs/spec` has no reader. The layout is additionally pinned by literal offsets
in `prov_check.c` (source 0, bundle 8, digest 16, bytes 24, fidelity 32 on LP64): the first reader of the *layout*
(rather than the number) in the tree. The kit ledgers (memfn/docs/) are the kit manager's.

## 5. Fixtures and sabotage

- finder_check.py family L (40 new checks, section 908 -> 948: 1 vocabulary + 3 tokens + 1 reached set + 1 NULL + 7 outside words + 6 byte values + 1 kit grep + 20 renders): the closed set read off the schema
  equals the contract's three tokens; each token maps to its own nonzero enumerator (1, 2, 3), the set of reached
  enumerators is exactly {1,2,3}; NULL -> UNSTATED with bytes 0; seven outside words refused with the sentinels
  untouched; six `bytes` values (0, 1, 999,960, 1,000,000, 2^40+7, 2^63+5) pass through exactly; the kit-source grep;
  the 2 sites x 5 fidelity values x 2 drivers render comparisons.
- **S1092** (`tests/mech/sabotages/S1092_prov-stanza-drops-fidelity.sh`): the mapping writes `MF_FID_UNSTATED`
  whatever token the block declares. Solo `tests/mech/run_sabotage_matrix.sh S1092` at 649d0f294:
  **DETECTED, `memfnfinder:4fail/944pass`** (the three tokens plus the reached-enumerator set), `== mech run COMPLETE:
  1 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0)`.

## 6. Validation (Linux dev box, `taskset -c 12-15`, `-j4`; logs `build/land/`, chain `build/land/chain.sh`)

Tip under test 649d0f294 (the report commit adds no code). Verdict reading: no
`\*\*\* \[(Makefile:[0-9]+: )?test-` line in any section log (every `verdict-lines=0` below).

| step | result |
|---|---|
| make, make strict | rc 0, rc 0 (`-Werror -Wshadow` clean) |
| test-memfn-finder | 948 passed / 0 failed (R-23 base 908 + family L's 40) |
| test-memfn-arms / rows / forms / deleg | 383/0, 232/0, 5/0, 5/0 |
| test-memfn-stamps / guarded / simdfloor / rank | 25/0, 10/0, 51/0, 15/0 |
| test-memfn-manifest / link / reach / arch | 11/0, 8/0, 4/0, 15/0 |
| test-registry | 79 / 0 |
| test-cand-oracle | 100 / 0 |
| test-spec-history | 145 / 0 |
| test-codegen | rc 0 (5 min 18 s) |
| test-memfn-g2 (quick) | 52,987,697 checks / 0 failed |
| `MEMFN_REACH_ONLY=1 AXES=--memfn bash tests/axes/run_axes.sh` | `memfn arm: OK`, 257 passed / 0 failed |
| mech S1092 (solo) | DETECTED, 4fail/944pass |

emit_sweep (`--ref-bin` = build of e09748b9b via `git archive` into `build/ref/`, `--no-self-check`, streams
`c-default,c-vm,emit-ir,composition,facts,emit-ir-auto,stderr` (+`dumps` on the plain arm); every stream
`movers=0 asymmetric=0`, no tag or differ floor tripped; argv population 5,790 per arm, 386 composition files):

| arm | wall | composition producing / artifacts | movers |
|---|---|---|---|
| plain (+ dumps) | 1 min 26 s | 37 / 106 | 0 |
| `--extra=-fmemfn-simd` | 1 min 50 s | 37 / 106 | 0 |
| `--extra=-fcomments` | 2 min 00 s | 37 / 106 | 0 |
| `-e utf8` (`--no-differ-floor`) | 2 min 11 s | 36 / 104 | 0 |
| `--engine=vm` (`--no-differ-floor`) | 1 min 38 s | 37 / 86 | 0 |
| `--arms start` | 13 min 32 s | 37 / 106 | 0 |

**Zero artifact movers on every arm.**

## 7. OWED (heavy; none run, none expected to move)

Full `make test`; the derived mech rows (the 51+ anchored memfn rows are untouched: this change edits no kit `.c`; only
`memfn/include/memfn.h`, `src/gen/memfn_sites.c` (a new function appended after `pcrec_memfn_window_is_candidate`) and
tests, so SABANCHOR in `make test-codegen` passed); G2 full (`make test-memfn-g2-full`); the N2 census; the
`--variant`, trace and rwquest / synthetic-set arms of fdb2's chain (not part of this brief).

Process notes: all scratch under `build/tmp`/`build/scratch` (TMPDIR set); the sabotage matrix's own scratch is under
`$TMPDIR`. Nothing outside the worktree was written. Bare `sleep` polling loops in a foreground call hit the tool's
120 s default once; the chain itself was detached (`nohup setsid`).

## 8. Charter checklist (R-24)

| R-24 landing bar | status |
|---|---|
| `mf_prov.bytes` (0 when the block declares none) and `fidelity` (closed token enum, UNSTATED zero, values = pcrec's findings vocabulary), appended not reordered | done (`memfn.h`; vocabulary source `rxt_schema.def:278`; offsets pinned) |
| pcrec's mapping in src/gen/memfn_sites.c fills both from the block | done as far as the base allows: `pcrec_memfn_prov_stanza`; no analysis object exists on this base, so nothing calls it; E-1's two wiring lines are in §2 |
| one MF_SITE_ABI event with its readers found by grep | 14 -> 15, §4 |
| zero artifact movers on every emit_sweep arm | done (6 arms, §6) |
| a G2/finder fixture stating each fidelity value | done (finder family L: UNSTATED, verbatim, adapted, synthesized, plus an out-of-enum value) |
| no kit row READS the two fields before B3a | stated and grep-checked (§3), re-checked by family L every run |
| one sabotage row (S1092) | DETECTED solo |
