# decfb0 — [DEC-FALLBACK] STEP 0 census (measurement; no compiler change)

Lane `decfb0`, branch `lane/decfb0` from main `9029f5db`, 2026-10-08. Scripts
and full tables: `docs/design/decision_families/decfb0/` (`run_census.sh`,
`results.md`). Nothing under `src/`, `cli/`, `lib/` changed.

## Method
- Corpus: every `pattern` block of `tests/**/*.rxt` read through
  `pcrec --list-source` (as-written pattern, flags, features, encoding,
  engine), de-duplicated on that 5-tuple: **4,792 distinct cases** (4,350
  compile at shipped limits, 442 are `perr`/module-missing refusals). Not
  sampled. `config`-composed features and `budget` are not applied (as-written
  rows only); `include` fragments are covered as the files that own them.
- Attempts: a scratch COPY of src/ with `DECFB` stderr probes in
  `compile_driver` (attempt header, failure arrival, rung taken). The probed
  `plain` build's stdout is byte-identical to `build/pcrec` on all 4,792
  cases (0 BYTES_DIFF). An "attempt" is one pass of the `for (attempt…)` loop,
  so it includes size-term ladder trials and the final re-emission, not just
  DFA/VM builds.
- Variants: `plain` (shipped limits); `lowsize` (`MAX_VM_EMIT_CODE_BYTES=30000`,
  `MAX_EMIT_BYTES=60000`, `SIZE_TERM_THRESHOLD=10000`); `lowdfa`
  (`MAX_AUTO_DFA_ELEMS=3000`); `lowboth`. The lowered values are mine, chosen
  only so the size-cap and [SEL-1] ladders see populations; they are not
  bisected to a witness.

## Facts

### ENGINE_SEL over the corpus (compiled cases)
| (ENGINE, ENGINE_SEL) | plain | lowsize | lowdfa | lowboth |
|---|--:|--:|--:|--:|
| dfa selected | 2247 | 2164 | 2197 | 2158 |
| vm selected | 1748 | 1642 | 1729 | 1638 |
| vm forced | 221 | 215 | 221 | 215 |
| vm declined-nullable-default | 115 | 110 | 115 | 110 |
| dfa size-cap-retry (drop-anchored/premul) | 15 | 51 | 0 | 35 |
| vm size-cap-retry | 1 | 81 | 0 | 75 |
| vm overflowed-dfa | 1 | 1 | 60 | 56 |
| vm collapsed-prefilter | 1 | 1 | 23 | 21 |
| vm overflowed-prefilter | **0** | 0 | 4 | 4 |
| vm declined-nullable | 1 | 1 | 1 | 1 |

At shipped limits `overflowed-prefilter` has no corpus witness; every other
token has at least one. The full (ENGINE, ENGINE_SEL, UNROLL_K_WHY,
VM_PREFILTER, VM_PREFILTER_WHY, VM_PREFILTER_LANG_WHY) tuple tables, per
variant, are in `results.md`. Plain-build tuples: 13 distinct; the dominant
VM ones are `selected/default/hybrid/no counted repeat` (1008),
`selected/default/none` (497), `selected/default/hybrid/exact` (243). UNROLL_K_WHY
at shipped limits is `default` for all VM rows but two `size-model`
(`vm/forced` 1, `vm/declined-nullable-default` 1); `lowsize` adds `cap-rescue` (14),
`size-model` (12), `size-model-declined` (2). `option`, `denied`,
`capacity-declined` have no corpus witness in any variant (they need flags the
corpus blocks do not pass).

### Attempts per compile (all 4,792 cases)
| attempts | plain | lowsize | lowdfa | lowboth |
|--:|--:|--:|--:|--:|
| 1 | 4771 | 4565 | 4702 | 4558 |
| 2 | 17 | 39 | 24 | 45 |
| 3 | 2 | 145 | 64 | 145 |
| 7-9 | 2 | 43 | 2 | 44 |
| total attempts | 4825 | 5402 | 4956 | 5408 |
| beyond the first | 33 (0.7%) | 610 | 164 | 616 |

(1-attempt row includes the 442-463 refusals.) The 7+ rows are the
[ART-SIZE] size-term ladder (trials + final), not fallback rungs. Attempt-
creating transitions by signature, with final ENGINE_SEL, are in `results.md`;
at shipped limits they are: `drop-anchored` x15 (-> dfa size-cap-retry),
`sel1:collapse` x2 (-> collapsed-prefilter, declined-nullable),
`sel1:collapse > sel1:drop` x1 (-> overflowed-dfa), `prefilter-collapse >
drop-prefilter` x1, one size-term-ladder compile (forced).

### §4.1 wasted attempts (collapse predicate differs from its gate)
Measured as: a collapse retry whose NEXT attempt fails again with
`fit.prefilter_collapsed == 0` (the flag is set before the DFA builds,
compile.c:1873, so it is accurate at the failure arrival), i.e. the rebuild
declined the collapse.

| rung | plain | lowsize | lowdfa | lowboth |
|---|--:|--:|--:|--:|
| size-cap `prefilter-collapse` taken | 1 | 95 | 0 | 79 |
|  ... next attempt refused again, NOT collapsed (WASTED) | **1** | **43** | - | **39** |
|  ... next refused again, collapsed (legit; collapsed also too big) | 0 | 41 | - | 31 |
|  ... next compiled, collapsed | 0 | 11 | - | 9 |
| [SEL-1] `retry_collapse` taken | 3 | 3 | 88 | 88 |
|  ... next overflowed again, NOT collapsed (WASTED) | 1 | 1 | **60** | **60** |
|  ... next overflowed again, collapsed (legit) | 0 | 0 | 4 | 4 |
|  ... next size-refused, collapsed | 0 | 0 | 0 | 2 |
|  ... next compiled | 2 | 2 | 24 | 22 |

So the §4.1 drift is **live at shipped limits** (not only in a lowered build):
`(\p{Xwd})` under `-e utf8` takes the size-cap collapse rung, the rebuild
declines it, the same artifact is refused again, then `drop-prefilter` fires.
The [SEL-1] twin (`retry_collapse` omits `pfc_rep` too) wastes 1 attempt at
shipped limits and 60 of 88 under the lowered DFA budget. Not every wasted
[SEL-1] attempt is "the same artifact" as in the size-cap case (the first
attempt's engine was the DFA, the retry builds the VM's prefilter DFAs); the
count above is "collapse was declined at the retry and it overflowed again".
Example wasted size-cap patterns (lowsize): `(?:(?>aa|a))+ab`
(`--features atomic-groups`), `(\\bcat\\b)+` (`assertions`).

The attempt COUNT impact of fixing it, were the predicate to match the gate:
plain -1 compile-pass for 1 case; lowsize -43; lowdfa -60; lowboth -99 of
the 610/164/616 extra attempts. Compile-time cost was not timed.

### §4.5 `--emit-ir` does not know [PF-DROP] (PROBED, lowsize reference)
`pcrec_lowsize --features atomic-groups -p rx --emit-ir --pattern
'(?:(?>aa|a))+ab'` prints `prefilter  no-fno-prefilter  -fno-prefilter --
forced off; the VM scans from search_from itself`, while `-o -` on the same
compile stamps `RX_ENGINE_SEL "size-cap-retry"`, `RX_VM_PREFILTER "none"`,
`RX_VM_PREFILTER_WHY "size cap retry, hybrid 31745 > 30000"`. The caller passed
no `-fno-prefilter`. The CLI also prints the PF-DROP note on stderr. Needs a
lowered-cap build or a >1 MB hybrid; the single natural shipped-limit witness
is `(\p{Xwd})` (-e utf8), whose size-cap-retry artifact exercises the same
path (listing not run on it here).

### §4.6 registry order vs evaluated order (READ + `--list-axes` PROBED)
`--list-axes` `engine-route` rows (all `kind=predicate`), order 1..8: forced,
declined-nullable-default, collapsed-prefilter, declined-nullable,
overflowed-dfa, overflowed-prefilter, size-cap-retry, selected ("always
(fallback)"). `esel_of` (`select_engine.c:965-976`) evaluates: forced,
declined-nullable-default, declined-nullable, size-cap-retry, selected,
collapsed-prefilter, overflowed-dfa, overflowed-prefilter (the true
fallback). Positions that differ: declined-nullable (4 vs 3), size-cap-retry
(7 vs 4), selected (8 vs 5), collapsed-prefilter (3 vs 6), overflowed-dfa (5
vs 7), overflowed-prefilter (6 vs 8). Corpus: no artifact in any of the four
variants has an ENGINE_SEL that the other order would assign differently
(the arms are disjoint on `dfa_disabled`/`size_drop_rung`; `esel_of`
asserts the one cross-case).

## Validation
- Probed build vs `build/pcrec`: 0 byte differences over 4,792 cases (plain).
- `make test` NOT run (no tracked source changed; docs and scripts only).
- Re-run: `docs/design/decision_families/decfb0/run_census.sh` (~1 min).

## Design recommendations (separate; not facts)
- The ladder-table row has real work to do at shipped limits: 33 of 4,792
  corpus compiles take more than one attempt, 17 are `drop-anchored`,
  and 2 of the 33 are a wasted collapse attempt. The table's `applies` for the
  collapse row should be the real gate (`fit.chosen != DFA && pfc_rep &&
  !nullable-unless-forced`), which is the §4.1 fix and the one non-no-mover:
  expect plain -2 attempts (1 size-cap + 1 SEL-1), a compile-time-only move.
- Do the refactor first as a pure no-mover (attempt count/order identical,
  including the wasted ones), pin `results.md`'s plain and low* attempt
  tables as the before/after identity witness (rerun `run_census.sh`; the
  stamp tuples and the attempt signatures must match line for line), then
  land the §4.1 fix as its own change with the delta above as its expected
  size.
- `overflowed-prefilter` and `option`/`denied`/`capacity-declined` have no
  shipped-limit corpus witness; the identity gate for the table needs the
  lowered variants (or flag-passing blocks) to cover them.
- §4.6: making `engine-route` a `list` axis from the fired row removes the
  order disagreement by construction; until then the registry order text is
  wrong about 6 of 8 positions.
