# tests/codegen — structural assertions on generated code

Asserts that behavior-preserving optimizations are actually PRESENT in the
emitted C. These are not correctness tests (the .rxt corpus owns correctness);
they exist because checkpoint review R2 (finding R2-PR3) showed that three M2
optimizations — self-loop skip states, the anchored fast path, and DFA
minimization — could each be COMPLETELY disabled with zero signal from
`make test` or `make bench`. Behavior-preserving work needs structural tests
or it has no regression net at all.

## Files

- **run_cand_oracle.sh** + **cand_oracle_witnesses.tsv** — ([KIT-VERIFY] Z2: a row only the test harness's lever routes, `cover`, is reached by witnesses whose FLAGS carry ...
- **run_cand_rows.sh** + **cand_rows_check.py** — ([OPT-REVEND] L0 adds **[cand-no-row-pointer]**, F-2's revert as a grep row: no comparison against `&cand_rows[...]` and ...
- **runcmp_check.py** — [OPT-LITSCAN] S4 C1 (lane s4build, 2026-10-03, abi 56): the RUN COMPARE's structural checks (`memfn/src/runcmp.c` since [MEMFN] M1b, before it ...
- **reqcube_check.py** — [OPT-LITSCAN] S4 C3 (lane c3build, 2026-10-03, abi 59): THE CASELESS NECESSARY RUN's structural checks (`docs/design/litscan_s4.md` §5.4), run by ...
- **run_case_spelling_identity.sh** — [CASESPELL] (2026-10-23): patterns differing ONLY in the letter case of their caseless text emit the same matcher (declared spelling groups x dfa/vm x byte/utf8; emitted C identical after an exact, count-checked pattern-echo mask, gcc -O2 `.text` identical; two positive controls that must differ). In `make test-codegen`.
- **run_prefix_invariance.sh** — K79 (lane k7980, 2026-09-30, abi 54): no SELECTION reads the prefix.
- **run_nomatch_caps.sh** + **nomatch_caps_driver.c** — K78 (lane k78, 2026-09-30, abi 55): match_api.md §3.1/§3.3's caps contract on every entry that takes a caps array ...
- **run_trie_identity.sh** — DIFFERENTIAL codegen check for the M2.8 alternation trie (R3.3).
- **run_vm_identity.sh** — [M4.5b] THE ZERO-REGRESSION GATE (engine_m4.md §5.4, §13 P-7: "this one should be a GATE, not a prediction").
- **run_endvar_identity.sh** — [M6.2] wave A's BYTE-IDENTITY GATE, the `run_trie_identity.sh` shape one closure view over.
- **run_wordctx_identity.sh** — [M6.2] wave B's BYTE-IDENTITY GATE, the same shape one axis over.
- **run_mlinectx_identity.sh** — [M6.2] wave C's BYTE-IDENTITY GATE, the third in the family.
- **run_gstart_identity.sh** — [M6.2] wave D's BYTE-IDENTITY GATE, the fourth in the family and **the one whose REFERENCE KNOB IS PLACED DIFFERENTLY, for a measured reason** ...
- **run_ir_listing.sh** — [M4.5c] DD-8's VM program listing (`--emit-ir`) held to the ARTIFACT it describes. engine_m4.md §10's constraint is that the dump derive from the ...
- **run_longprefix_sweep.sh** — [REVW.1] wave 1 stage 0's long-prefix full-corpus sweep (2026-09-18), an OPT-IN tool (`run_object_neutrality.sh`'s "not in `make test`, ...
- **run_lookaround_identity.sh** / **lookaround_classify.py** — [M6.6.2] module `lookaround`'s BYTE-IDENTITY GATE and the grammar-aware classifier that splits its ...
- **run_dfa_stamps.sh** — [DD-13] (2026-08-25), widened by [DD-13c]: the D46 SELECTION STAMPS (`RX_ENGINE`, `RX_DFA_SCAN`, `RX_DFA_PREFILTER`; `docs/spec/match_api.md` ...
- **run_premul_table.sh** — [OPT-3] (2026-08-26) the PRE-MULTIPLIED DFA TRANSITION TABLE (`docs/design/premultiplied_dfa_table.md`, `docs/spec/tuning.md` §2.13), held to ...
- **run_offset_skip.sh** — [OPT-K] (2026-08-28) the OFFSET-k CANDIDATE-START SKIP (`docs/design/offset_k_skip.md`, `docs/spec/tuning.md` §2.14), held to the artifact ...
- **run_anchored_match.sh** — [ENG-ABS] (2026-08-29) the ANCHORED MATCH-HERE FORM (`docs/design/anchored_match_unwrapped.md`, `docs/spec/tuning.md` §2.15), held to the ...
- **run_search_pinned.sh** + **searchpin_driver.c** — [OPT-5] STEP 2 (2026-09-02) the START-PINNED SEARCH (`docs/design/opt5_step2_twopass.md`, `docs/spec/tuning.md` ...
- **run_inline_capability.sh** — [CC-DIFF] STEP 2 (2026-09-04), the CAPABILITY PROBE: does the compiler about to build an artifact ALREADY inline the VM entry chain, or ...
- **run_entry_shape_identity.sh** + **entry_shape_driver.c** — [CC-DIFF] STEP 2 (2026-09-04), the VM ENTRY-SHAPE LADDER'S ANSWER-IDENTITY GATE. `--vm-entry-shape=1..4` ...
- **run_facts_checks.sh** — [PATFACTS] step 3.0 (D126, 2026-09-26): the pattern-facts record's own checks (`docs/design/patfacts/design.md` §4.2.3).
- **run_prechecks.sh** — [OPTLOOP.1] batch 1 (D119, 2026-09-22): THE WHOLE-WINDOW PRE-CHECKS' structural gate, `make test-prechecks`, its own section for ...
- **run_vm_frameless.sh** — [OPT-VMFL] STEP 0 (2026-09-02) `<PREFIX>_VM_ FRAMELESS`, held to the VM PROGRAM'S OWN `goto *` COUNT rather than to the `has_push` bool that ...
- **run_dfa_uniform_fold.sh** — [CC-DIFF] STEP 1 (b) (2026-09-03) the UNIFORM-TABLE FOLD and its `<PREFIX>_DFA_UNIFORM_FOLDS` stamp, held to the artifact's own text rather ...
- **run_scan_edge_dispatch.sh** — [OPT-EDGE] STEP 1 (2026-09-03) the SHARED-SENTINEL EDGE DISPATCH: that the scan edge costs the loop's GENERIC PATH nothing.
- **run_form_census.sh** — [CHK-2] piece 3 (2026-08-26) THE FORM CENSUS: compiles every `.rxt` corpus pattern twice (default engine, and `--engine=vm` forced where ...
- **run_tiered_entry.sh** + **tier_driver.c** — [OPT-1] (2026-08-25) the TWO-TIER DEFAULT ENTRY (`docs/design/two_tier_entry.md`, `docs/spec/match_api.md` §10.9).
- **run_codegen_tests.sh** — greps ONE ENGINE'S BODY (extracted by entry name; see below) for each optimization's signature (skip tables + skip loop, `start_max = 0` for ...
- **run_size_term.sh** — [ART-SIZE]/D84's structural check (2026-08-29).
- **run_prefilter_collapse.sh** — [OPT-4]/K39's structural check (2026-08-29).
- **run_rev_end.sh** — LOCATE's `rev-end` row held to the artifact (in `make test-codegen`; mech arm `revend`). §1 named witnesses: the stamp, `rx_info.scan`, the walk's ...
- **run_start_landing.sh** + **landing_hostile_driver.c** — RECOVER's two new rows held to the artifact (`docs/design/start_landing.md` §7.3; its own section, `make` ...
- `run_object_neutrality.sh` — section "[M6-READ] `run_object_neutrality.sh` — the two-compiler gate" (history file)
- `run_atomic_identity.sh` — section "[M6.4.2] `run_atomic_identity.sh`, and the ONE gate here whose reference is a PINNED COMMIT" (history file)
- `run_backref_identity.sh` — section "[M6.5.2] the `[M6.5-DUPNAMES]` block, and `run_backref_identity.sh`" (history file)
- `run_n1_budget.sh` — section "`run_n1_budget.sh` — [LIM-2] N1's structural check (2026-09-04)" (history file)
- `run_encoding_identity.sh`, `run_cpset_structure.sh` — section "[M5.0] stage 1's PAIR: `run_encoding_identity.sh` (RETIRED 2026-09-05) + `run_cpset_structure.sh`" (history file)
- `run_tune_dial.sh` — section "`run_tune_dial.sh` — [OPT-DIAL]'s MECHANISM-STATE CROSS-CHECK (2026-09-17)" (history file)
- `run_recursion_identity.sh` — section "[DD-14] waves D+E — `run_recursion_identity.sh`, opt-in as `make test-recursion-identity`" (history file)
- `run_scan_edge_census.sh` — section "`run_scan_edge_census.sh` — [OPT-EDGE] STEP 1.1's population (2026-09-04)" (history file)
- `run_encoding_checks.sh` — section "[M5.0] stage 2's structural + differential acceptance: `run_encoding_checks.sh`" (history file)
- `run_comment_escape.sh` — section "`run_comment_escape.sh` — pcrec-bench O-31 finding F1's regression net (2026-09-17)" (history file)
- `run_comments_axis.sh` — section "`run_comments_axis.sh` — [EMIT-VERB]'s axis check (2026-09-19)" (history file)
- `run_cls_fold_agreement.sh`, `fold_pairs_dump.c` — section "`run_cls_fold_agreement.sh` + `fold_pairs_dump.c` — the VM class-fold" (history file)
- `run_clspack.sh` — section "`run_clspack.sh` — [OPT-CLSPACK]'s shared atom table (2026-09-30)" (history file)
- `run_wclass_census.sh`, `wclass_census.py` — section "`run_wclass_census.sh` + `wclass_census.py` — [CLS-TREE] S3's A_WCLASS checks (2026-09-29)" (history file)
- `run_fallback_table.sh` — section "`run_fallback_table.sh` — the fallback tables' artifact-side check ([decfb B0], lane decfbB0b, 2026-10-08)" (history file)
- `cand_oracle_unreached.tsv` — the UNREACHED witnesses table read with `run_cand_oracle.sh`.
- `manifests/` — pinned byte/line manifests read by the identity and structure checks.
- `run_prechecks.sh` §5 `<PREFIX>_REQ_WHY` ([OPT-PRECHECK-ADMIT], 2026-09-23, abi 30 -> 31): the ADMISSION of §3's and §4's pre-checks, ruled by Frank as G1 + G2 (G3 dropped on x86_64 measurement); neither decline is answer-detectable, so this file is where they are defended.

## TRAPS THIS DIRECTORY HAS PAID FOR — read before writing a `sed` or resolving a `CC`

| about to… | know this |
|---|---|
| write a `sed` in a check | **this box's `sed` is BSD sed and GNU-only constructs SILENTLY NO-OP** — no error, exit 0, text unchanged. `\b` and `\|`-inside-`\(...\)` are the two MEASURED instances, both of which sat red here since the Mac move while naming an emitter change that had not happened (`docs/testing.md`, "The `sed` binary itself"). Spell it portably, never `case $(uname)` — the harness runs these on Linux too |
| resolve a `CC` in a script here | source `tests/lib/cc_resolve.sh` BEFORE your own defaulting — it acts only when `CC` is unset, so an assignment above it makes it a no-op. `run_codegen_tests.sh` was the tree's last straggler, and the cost was the GCC-SPECIFIC [K24] block being asked of Apple clang |
| believe a check that says the emitter drifted | rule out the TOOL first. Both traps above reported exactly that, and both were wrong |

## Conventions

Every check must be validated against a deliberate sabotage: disable the
optimization in a scratchpad build and confirm the check FAILS. A structural
test that passes under sabotage is worse than no test — it certifies nothing
while looking like coverage. Sabotage the SPECIFIC branch under test, not the
feature containing it. When adding an optimization to src/gen or src/opt, add
its check here in the same change.

Validated sabotages for run_trie_identity.sh. **Record the exact edit, not just
the count** — the first version of this table carried a number produced by a
contaminated tree (two sabotages stacked, because a `git checkout` revert
silently failed inside a non-git tarball copy) and another that was never
measured at all:

| sabotage (exact edit) | .rxt | @200 | @500 |
|---|---|---|---|
| `return n;` as the first statement of `disjoint_run_len` | 2 | 21 | 64 |
| in rule 1, hoist every accept to the front instead of partitioning the list around each (keep removing them from the list) | 16 | 38 | 94 |
| `TRIE_ENABLED = 0` in the shipped build | 0 | 0 | 0 — only the CONTROLS fire |
| `elig[j] = TRIE_ENABLED && nbr >= 100 && trie_key(...)` | 0 | 0 | 0 — only the 4- and 8-branch controls fire |

Do NOT use the naive rule-1 sabotage (skip the accept split, change nothing
else): it leaves items with `len == depth` in the list for rule 2, which then
reads `seq + depth*32` past the allocated key — a 32-byte arena over-read, so
the count is unstable between builds (171 and 176 observed for the same edit).
The hoist form above is memory-safe by construction.

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__codegen.md`.
