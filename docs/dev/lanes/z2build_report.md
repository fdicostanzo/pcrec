# z2build — [KIT-VERIFY] U1 step Z2 (docs/design/kit_proof.md §7, rev 2.2)

Lane z2build (opus), 2026-10-21. Branch `lane/z2build`, worktree
`worktrees/z2build`, base main `ec10382cf` (abi 82) with lane/x0fix merged
(`fc926a603`, kit_proof rev 2.2). Build go: Frank 2026-10-21 ("both you and kit
please proceed", then "Proceed through all items").

## STATE AT HANDOFF

- **Built and committed** (7 commits, `bc665f16d..dc74f4f98`, plus this report's
  commit). No abi event, no deny or force bit, no D/K id taken.
- **Light checks green** on the lane tip (below). **Heavy checks QUEUED, verdicts
  OWED**: boxqueue jobs `540-z2build-sweep`, `541-z2build-maketest`,
  `542-z2build-mech`, `543-z2build-x1` (job files in
  `worktrees/z2build/build/z2s/jobs/`). The sweep started 15:12 EDT. Each
  ends with an `== z2build <name> COMPLETE` line in its job.log and writes
  its logs under `worktrees/z2build/build/z2land/` (sweep, make test, mech)
  or `build/z2x1/` (census, X1, stated).
- **Rulings file**: read at every checkpoint; last entry read is **ruling 1**
  (X0 passed on rev 2.2; decide `(?:[a-z]{0,3}\z|x)[0-9]{3}` exhaustively on the
  built artifact). Done: decided, 0 differences (below).
- Do not prune `worktrees/z2build` before the four jobs end; the jobs build and
  read it.

## What was built

| piece | where | note |
|---|---|---|
| harness lever `--harness=kit-proof` | `cli/main.c`, `src/core/internal.h` (`PcrecHarnessOptions.kit_proof`, `pcrec_kit_proof_routed`) | set only through `pcrec_harness_compile`; default and trace builds decline `cover` |
| `mf_preview(art, "R-26.6")` | `src/gen/memfn_sites.c` `pcrec_memfn_art` | after `mf_reach`, routed compiles only |
| span_facts first slice (UL-0) | `src/facts/kset.c` (`pcrec_span_walk`), `facts.def`/`facts.h`/`facts.c` | the k-set walk extended to an exact per-thread subset walk: in-span `A_CTX` narrows per thread, the true set (view-gated eol bytes, x0fix's R2 ruling); declines named (`erased-nfa`, `end-mark`, nullable, dead); budget `PCREC_SPAN_WALK_SUBSETS` (limits.def, UNMEASURED label) |
| `--emit-facts` row `span_facts` | `src/dump/facts_dump.c`, `docs/spec/facts_listing.md` §4.1.2¶7c | the spec hunk |
| MkLang / MkEnd / MkKnown | `src/facts/facts.h`, `src/gen/known.h`, `known.c` | MkEnd reads A from the EMITTED entry on both arms, with scan edges |
| `cover_conj[]` C1-C14 | `src/gen/known.c` | first failing row = the `why`; C8's disagreement is an internal error in the trace build |
| `cover` LOCATE row, `emit_cover` | `src/gen/emit_dfa.c` | after `rev-end`; REPORT site `DELEG_COVER`; the DEFAULT build holds the kit's defined class to the stated sets (`pcrec_cover_proof_diff`, any difference an internal error) |
| true `exact_len` over the SENT sets | `src/gen/memfn_sites.c` `pcrec_memfn_span0_stated` | every start-origin FIND site; was `_today` (exact_len 0) |
| compound.c field reads (§2.6) | `src/core/compound.c`, `compile.c` | A1 reads the row's NEXT ask, A5 `end_seeded` |
| trace records | `KITPROOF`, `SPANSET`, `SITESTATED` under `PCREC_KIT_PROOF_TRACE` | the census and stated-check inputs |
| `make test-kitproof` | `tests/kitproof/` (new; CI shard 1, weight ESTIMATED) | 24 verdicts, 6 facts, 55 answers (393 cells) against libpcre2 10.46's committed answers |
| C17 | `tests/memfn/site_manifest.tsv` row COVER (`delegated`), `site_census.py` `PASS_CONFIGS` | see deviation 2 |
| sabotage rows | S1130-S1141, S1144, S1148, S1149; S512 and S894 re-pinned/re-aimed | mech arm `kitproof` |
| instruments | `docs/design/kit_proof/z2/` | X1 driver, exhaustive cell, census/stated/hist |

## Measured on the lane (light)

- `make strict` clean; `test-spec-history`, `test-plan-lint`, `test-memfn-deleg`
  (14/0, after moving `emit_cover`'s `mf_result` to the arena: C10 rule 4),
  `test-memfn-manifest` (13/0), `test-kitproof` (88/0), `test-registry`,
  `test-memfn-finder`: all rc 0. Lever fence 3 checks + 4 controls green.
  Sabotage anchors: 894 rows, all resolve. VALIDATE_ONLY on the 71 queued rows:
  all valid. Every new row's REACH probe reads its expected value on the clean
  tree.
- **Ruling 1 decided**: `(?:[a-z]{0,3}\z|x)[0-9]{3}` reads `cover` k=4 (S_d =
  `x`,`[0-9]`x3) on both encodings. Every subject of length 0..8 over
  {a, z, x, 0, 9, \n, #} (6,725,601 subjects), every startoffset and the
  find-all loop against libpcre2 10.46: **0 differences in 66,243,390 cells,
  native and utf8 alike** (`docs/design/kit_proof/z2/out/exh_ruling1_*.txt`).
  The control (the PCRE2 side handed `(?:[a-z]{0,3}|x)[0-9]{3}`) reads 2,984
  differences at length 5. No conjunct declines it.
- The built slice's statements on the five in-span witnesses are green against
  libpcre2 10.46 by `x0.py stated` (`out/stated_built.txt`), including
  `[ab](?<=a)c|bc` at exact_len 2, where `x0/stated.tsv`'s slice row stated 0
  (both sound; the product {a,b}x{c} is exact).
- Default-build identity was spot-checked earlier in the lane (800 base-corpus
  compiles plus 42 samples, byte-identical with main's build/pcrec); the full
  proof is the queued sweep.
- X1 smoke (7 items): 0 differences beyond X0's U1 class; X1's own plant
  (`X1_PLANT=1`, ends one byte late) reads red.

## Owed (queued)

1. `540-z2build-sweep`: emit_sweep vs `fc926a603`, streams c-default/c-vm/
   emit-ir/composition, `--arms start`, `--variant all`: **0 movers expected**.
   MEASURED for the first part before handoff (`build/z2land/sweep/main.log`):
   c-default, c-vm, emit-ir 0 movers over 5,811 argv patterns (5,357-5,358
   compiled), composition 0 movers over 387 files, self-check passed.
   Then facts and dumps as a MEASUREMENT: declared deltas are the new
   `span_facts` row on every `--emit-facts` listing and the
   `PCREC_SPAN_WALK_SUBSETS` row of `--list-limits`; nothing else should move.
2. `541-z2build-maketest`: perfrun make test (shape 4,2).
3. `542-z2build-mech`: 71 rows (the 15 new, S512, S894, and 54 re-runs the
   diff derives: rows anchored in a definition `fc926a603..HEAD` changes, on a
   changed `.def`/`.h`, or on the C17 manifest/census and the lever fence).
   Every new row is expected DETECTED; S1139 and S1141 are the two I am least
   sure of (S1139 is C9 dropped alone, not the design's two edits; S1141's
   hybrid may decline at C4 before the plant matters). An UNDETECTED there is
   a finding about the plant, not the code.
4. `543-z2build-x1`: the census (13,956 items: K35's why histogram, the C8
   control, agreement with conj.py), X1 over X0's 1,433-item population, and
   the stated check on 1-in-4 of the census's SENT statements. Expected: C8
   internal errors 0, agreement with conj.py on cover-vs-not (any disagreement
   is a design/code disagreement and a stop-rule item), X1 0 red beyond U1.

## Deviations from the design and the brief

1. **`cover` declares no kit ask (`kask`)**: its predicate reads `pcrec_cover`,
   whose C13 asks the kit; declared as a LOCATE→LOCATE read it would be a
   self-edge the read graph's cycle check refuses.
2. **C17: the row is `delegated`, not `pending`.** A `pending` row whose
   emitter spells no search form fails rule 4 (stale), and `emit_cover` spells
   none (the kit writes the FIND). A `delegated` row must be reached by the
   corpus pass, which never compiled through the harness. Fix, general: the
   traced binary is now linked as the harness (`-DPCREC_HARNESS`; with no
   lever it compiles as build/pcrec) and every corpus pattern runs under each
   row of `site_census.PASS_CONFIGS` (default, kit-proof). C17_ROW_FLOOR
   13 -> 14, S512 re-pinned. **This widens the lever fence's allowlist** by
   `tests/memfn/site_census.py` and `tests/kitproof/` (precedent:
   `tests/memfn/run_arm_reach.sh`): main's call.
3. The slice states the TRUE set and exact products the design text called
   0 (deviation in the sound direction, libpcre2-checked).
4. Two new decline reasons in the facts listing (`decline:erased-nfa`,
   `decline:end-mark`), in the spec hunk.
5. Not built at Z2: the out-of-span context records (the D168 producer half),
   CK-1/CK-7/CK-10, and the C13 refusal-detail split (C13 reports `refused`).
   Rows S1142/S1143 (design: ship UNREACHED) and S1150 (PROPOSED, not
   allocated) have no row file: S1150's plant (union instead of per-thread
   narrowing) is not one anchored edit in the walk; its detectors (the facts
   rows, X0's stated check) are in place. S1145 is B1's (the deny); S1146 and
   S1147 are kit-side.
6. X1 grows its subject families from conj.py's plan (as X0 did); the oracle
   is still libpcre2. Patterns of X0's U1 class (a `{0}`-quantified anchor
   group, upstream_issues.md U1) are reported apart.
7. One slip: I copied the site manifest into `/tmp` for a scratch comparison
   and removed it a few seconds later.

## Not mine, seen in passing

`boxqueue status` shows main's `120-main-postmerge` FAILED with
`POPULATION-SHORT: done ran=none declared=1` (its job.log lacked the
`== postmerge COMPLETE` line), verdict GREEN.
