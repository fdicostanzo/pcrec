# kclose report (lane/memfn-kclose, cut from main 7d74499bc)

## Summary

SEAM-2 is fixed (kit refuses an UNSTATED `mf_akind.present`, G2 case, sabotage S3015, zero emitted bytes). R-13 owed b is done as wording only (not emitted text). R-13 owed a (TRACE_VARIANT_RECORDS_FLOOR) is NOT done: it is a measurement that needs `emit_sweep --variant all --bases byte --trace`, which the box hold forbids; OWED with the exact command. Commit 27843c24e.

## SEAM-2

- Confirmed open at 7d74499bc: the only reader of `mf_akind.present` is `kit_byte_rate` (memfn/src/presence.c:52-55), which compares to `MF_KIND_PRESENT` and returns NULL for anything else, so an UNSTATED zero silently took the NONE row. Nothing in `mf_art_begin` checked it.
- Fix: `analysis_check` in memfn/src/compose.c, called from `mf_art_begin` after `measures_check`: refuses a kind whose presence is not PRESENT/ABSENT, and `kinds` NULL with `nkinds > 0`, through `kit_fail` ("mf_art_begin: the analysis object is refused: ..."). Same shape as `measures_check`.
- pcrec always states it: `analysis_invariant` (src/gen/memfn_sites.c) already fails the compile on an UNSTATED offer, and `akind_state_map` maps only PRESENT/ABSENT onward. Verified by the sample below.
- Test: G2 api block (memfn/tests/g2/g2_gen.c, after the noise cases): zero-initialized and state 3 refused; ABSENT and PRESENT accepted.
- Sabotage S3015 (tests/mech/sabotages/S3015_kit_accepts_unstated_kind_present.sh; id taken above k382a's S3012): plants `if (0) return ...` on the refusal. Planted by hand (the matrix run waited on the box lock held by the full suite and was safekilled): `run_g2_gate.sh` went RED, "generator stage: 2 failure(s)" (the two refusal cases). Reverted; clean tree re-ran green. Matrix run of S3015 is OWED to job 569.
- BASE(7d74499bc)-vs-tip single compiles: 60 (20 patterns x default, `-fmemfn-simd`, `-fmemfn-simd=x86-64-v3`), each in its own dir to avoid the `#include "b.h"` name diff: 0 differences in .c/.h/stderr/rc.

## R-13 owed items

- a. TRACE_VARIANT_RECORDS_FLOOR: OWED, not changed (scripts/emit_sweep.py:2903 stays). It is measured by the working side of `scripts/emit_sweep.py --variant all --bases byte --trace`, pasted in by a reviewed re-pin (min of base and tip per arm). That is a full sweep, so it is outside this box window. The kit manager queues it.
- b. Stale wording: no "no SIMD form exists" text reaches generated C. Checked the three named sites: lib/pcrec.h already reads correctly (no stale text there); src/dump/axes_dump.c strings are `--list-axes` output only (the CLI listing, not an artifact); src/core/axes.def and tests/memfn/libc_census.py are comments/docstrings. Fixed: axes.def comment, two axes_dump.c strings (a comment and the `-fmemfn-simd` row description), libc_census.py docstring and one comment. `--list-axes` text changed for the `memfn-simd` row: not pinned by any test or spec I could find (grepped tests/, docs/spec, docs/guide); the identity sweeps list `--list-axes` as the usual mover. `studies/` claims left alone (adopted, not edited). No abi event.

## Checks

- `nice make -j2`: green. `make strict`: green.
- `test-memfn-finder`, `test-memfn-rows`, `test-memfn-link`: rc=0, 0 failed.
- G2 gate family (`memfn/tests/run_g2_gate.sh`): 9 passed, 0 failed (also RED under the plant, above). `make test-memfn-g2` (quick family, niced, whole section incl. simd and any families): rc=0, 0 FAIL lines (log /var/tmp/pcrec-pcrec/scratch/memfn/kclose/g2q.log).
- Anchors: 1226 sabotages, all anchors resolve.
- `make test-codegen`: ONE failure, [K37] tests/doc_lint/run_doc_lint.sh:33 (`mktemp` unbounded). Not mine: that file is unchanged from BASE (git diff 7d74499bc -- tests/doc_lint is empty); it is a main-side red. Everything else PASS.
- BASE-vs-tip compile sample: 60 compiles, 0 diffs.

## Gate jobs

Dir /var/tmp/pcrec-pcrec/scratch/memfn/kclose/jobs/, numbers 560-569, keys kit-kclose-{strict,ident1-3,reach,test,plants,mech1-3}: TREE worktrees/kclose, BASE 7d74499bc, fresh BASE binary at /var/tmp/pcrec-pcrec/scratch/memfn/kclose/base/build/pcrec (git archive, niced), S3015 added to mech shard 3 (26 rows). All ten `--dry-run` rc=0. NOT queued. Note: the ident/reach/test/plants bodies are the k381g ones re-pointed; their K38-1-specific text and the runcallers plants are unchanged.

## Charter-vs-committed checklist

- SEAM-2 confirmed with cite, fixed, refusal text, G2 case, sabotage row red on plant, zero bytes on sample: committed (27843c24e).
- R-13 owed a: NOT done (measurement; OWED, command above).
- R-13 owed b: checked not emitted; wording fixed: committed.
- Checks and gate jobs: as listed; gate jobs are scratch files, not committed.
- Not done: the mech matrix run of S3015 (box lock), the ident/mech/test gates (not queued by charter).

## STATE AT HANDOFF

Branch lane/memfn-kclose, tip committed, tree clean. OWED (for the kit manager, no run in flight): (1) TRACE_VARIANT_RECORDS_FLOOR re-measure: `scripts/emit_sweep.py --variant all --bases byte --trace` on a free box, then a reviewed re-pin. (2) The queued gates 560-569 (mech shard 3 includes S3015's matrix run). Nothing else.
