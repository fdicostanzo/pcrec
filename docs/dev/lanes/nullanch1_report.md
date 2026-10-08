# nullanch1 — [NULLABLE-ANCH] BUILD (2026-10-08)

Lane nullanch1 (opus), branch `lane/nullanch1` from main e6b6c25f (abi 66).
Round 3 rank 3a-1 (D153), alpha tier under D144. STEP 0 is
`docs/dev/lanes/nullanch0_report.md`; its instruments and this lane's sit in
`docs/dev/optloop/nullanch/` (own CLAUDE.md).

## 0. Summary (a fresh agent resumes from here)

- **Built**: the E1 fact `empty_admits` (`src/facts/widths.c`,
  `pcrec_pattern_empty_masks` + `pcrec_empty_masks_admit`; row in
  `facts.def` after `nullable`; forced at the E1 seal; `pf_check_e1` holds it
  to the lowered tree AND to bare nullability on every compile).
  `lang_nullable_declinable` (`src/opt/select_engine.c`) reads it instead of
  `nullable`, both scopes. `nullable` itself and its other readers (the
  collapse gate, `pcrec_startgate_needed`) are unchanged.
- **Movers = the predicted manifest exactly**: 5 patterns of 4,262 compiled
  (corpus + bench), `ESEL declined-nullable-default` 112 -> 107. Facts stream
  moves on every artifact by design (one new row).
- **abi 66 -> 67** (decided from D76/D94 + the [OPT-VEDGE] precedent, §3).
- **Answers**: 0 different over 58.2M (subject, start) calls at full width;
  oracle-first corpus file `tests/base/nullable_anch.rxt` (62 cells).
- **Sabotage**: S611/S612/S613 new, each DETECTED solo, no FATAL.
- **Timing**: §5. Long-match tax filed as K97 (§5).
- **Owed**: the full `make test` + `test-codegen` + recursion identity +
  12 mech rows, armed DETACHED on `worktrees/nullanch1/.lift` (§7).

## 1. The fact

`em_set` returns the set of anchor masks the empty paths carry, one bit per
mask (`EM_NONE`, `EM_S`, `EM_E`, `EM_SE`). Concatenation is the pairwise OR
(`em_cat`), alternation the union, `{0}` is `{mask 0}`, `{m,1}` the body,
any other count the OR-closure (`em_plus`, exact because OR is idempotent),
and `rmin == 0` adds mask 0. `A_BOL`/`A_EOL` non-multiline contribute `EM_S`/
`EM_E`, `A_END` `EM_E`; every other zero-width node, `A_BREF`, `A_VAR` and a
nullable `A_CALL` are mask 0 (always satisfiable, today's answer).
`empty_admits` = some mask is not `EM_SE`.

**Calls**: the walk never follows `u.call.body` (the AST back edge). It reads
`u.call.nonnullable` — the call graph's LEAST fixpoint (K69), published
before the E1 seal — for whether the call has an empty path, and answers mask
0 for which. So a call can only push toward declining, and its nullability is
the same answer `nullable` already trusts. If the walk ever disagreed with
`pcrec_nullable` on whether an empty path exists (the unsound direction: an
empty set on a nullable tree reads "confined" and admits), the E2 seal refuses
the compile; S613 plants exactly that and is DETECTED.

**The count collapse** keeps `rmin == 0` and replaces a body's masks by their
OR-closure, which preserves "every mask is `EM_SE`", so the fact answers for
the rung scope (`declined-nullable`) too.

**Spines** are iterative (K20): both combinators are commutative, so the
left-nested `A_CAT`/`A_ALT` spines fold in any order and recursion is only on
the right items. The switch has no `default:`.

**F1 is kept, on purpose** (brief: token identity is refactor B's). Under
the corrected predicate the nine `^${v...}$` corpus rows would read
`empty_admits` false and move `ENGINE_SEL` from `declined-nullable-default` to
`selected` (prefilter still `none`, `has_var`). That is a partial F1 fix the
brief forbids, and nullanch0's own "112 -> 107" prediction assumed the token
stays. So `lang_nullable_declinable` reads bare `nullable` on a `has_var`
pattern (a `has_var ?` ternary, commented as F1's holder). F1 is now filed as
a known item on the `[DEC-FALLBACK]` row: B rules the token, then drops the
ternary. This is the one special case in the change, and it exists only to
hold a token.

## 2. Movers (`movers.py` -> `movers_result.txt`; emit_sweep)

`movers.py` compiles census.py's population with main's pcrec (built by
emit_sweep from `git archive e6b6c25f`) and the lane's, BEFORE the abi bump
so every byte compares:

| pattern | origin | ENGINE_SEL | VM_PREFILTER |
|---|---|---|---|
| `^(([a-z]+)*)+$` | bench evil-alt-nested | declined-nullable-default -> selected | none -> hybrid |
| `^(\s+)*$` | bench trim-nested-star | same | same |
| `^(a{2,4})?$` | corpus d27_edge | same | same |
| `^(a?)(?1)*$` | corpus sr_define, k69, quantified x2 | same | same |
| `^(?:(?<g>a?)){0}(?&g)*+$` | corpus quantified | same | same |

population 4,666 distinct, both compile 4,262, asymmetric 0;
`declined-nullable-default` ref 112 -> new 107. **EQUAL to the predicted
manifest.**

`scripts/emit_sweep.py --ref e6b6c25f` (same tree, before the bump): c-default
6 movers — the same five patterns as 6 corpus LINES (`quantified.rxt` carries
`^(a?)(?1)*$` twice, lines 64 and 187), each moving exactly `ENGINE_SEL` plus
the prefilter body; c-vm 0, emit-ir 0 (both force `--engine=vm`, where no
prefilter is built), composition 0, dumps 0; **facts 4,925 of 4,925** (the
new `empty_admits` row, declared: the listing is a debug surface whose fact
names are advisory, `facts_listing.md`).

## 3. abi decision: 66 -> 67

D76 / coding guide §3.1: any emitted byte is an abi event. What moves: on the
five movers the `.c` program (prefilter tables, scan, `VM_PREFILTER_LANG`)
and two stamp VALUES. The facts row is listing, not artifact, and alone would
not be one. Precedent: [OPT-VEDGE] (abi 56 -> 57) bumped for a pure
optimization that moved only its movers' stamp values and loop text. Readers
found by grep for `66`: `PCREC_ARTIFACT_ABI`, `run_codegen_tests.sh`'s
`ABI_EXPECT` and ledger message, `match_api.md`'s guard example and §6 change
log, `run_recursion_identity.sh`'s (B) FILEPIN (self-pinned to `8c175f58`,
the lane's last src commit; the manager re-pins to the merge). Other `66`
hits are history. **The memfn kit shares the number**: if another lane takes
67 first, this renumbers at merge.

## 4. Correctness

- **Differential** (`diff1.sh`/`diff1_driver.c` -> `diff1_results.txt`):
  main's default artifact vs the lane's, every subject to length 11-12 over a
  3-letter alphabet holding `\n`, AND every start offset (STEP 0 ran offset 0
  only). Ten rows: the five movers, `^(a*)*$`, `\A(a*)*\z`, and the
  still-declined controls `^(a*)*`, `(a*)*$`, `(?m)^(a*)*$`. **58,219,206
  calls, 0 DIFFERENT, 0 give-ups on either side.**
- **libpcre2 10.46 transcript** (`pcre2_cells.py` -> `pcre2_transcript.txt`):
  38 (pattern, subject, start) cells over the five movers. libpcre2 answers
  `-47` (match limit, U4) on the two give-up subjects; there `nomatch` is
  checked on the language-equal `^[a-z]*$`/`^\s*$` (libpcre2: nomatch) and by
  python once (nomatch, 7.9 s and 107.8 s — filed U19).
- **Corpus** `tests/base/nullable_anch.rxt`: 62 cases, all written FROM the
  oracle. Harness 62/0 at the lane; python verifier 0 fail, 23 skipped
  (`# pcre2-only`: the two call patterns and the two give-up cells). Against
  main's compiler the same file reads **60/2** — the two give-up cells
  (`PCREC_ERR_STEPS`), the K65-direction answer improvement.
- **Structural** (`run_prefilter_collapse.sh` [anch], 13 witnesses): six
  both-anchored nullable patterns keep `hybrid`/`selected`/`empty_admits no`
  (`^(\s+)*$`, `^(([a-z]+)*)+$`, `\A(a*)*\z`, `^(a{2,4})?$`, `^(a|b*)*\Z`,
  `^(a?)(?1)*$`); seven must stay `none`/`declined-nullable-default`/
  `empty_admits yes`: one-sided `^(\s+)*` and `(\s+)*$`, unanchored
  `(\s+)*`, an anchor on some paths only `^(a|$)*`, multiline
  `(?m)^(\s+)*$` and `^(\s+)*(?m:$)`, and `^(a?)(?1)*`. Suite 71/0.
  `run_facts_checks.sh` [facts-e1] gains the `empty_admits` column by hand on
  all 20 witnesses (two new utf8 anchored ones). Suite 8/0.

## 5. Timing (SCRATCH TIER)

TIMING_PLACEHOLDER

## 6. Sabotage, and two pre-existing findings

SABOTAGE_PLACEHOLDER

**Pre-existing, not this change**: `run_recursion_identity.sh` (a battery
gate, not in `make test`) reads 5 FAIL lines at the lane — `[default]`/
`[noprefilter]` (A) "10 call-free patterns emit a DIFFERENT PROGRAM REGION
than ac4917d" (`\w++\b`, `k++\b`, `(?>\w+)\b`, ...) and `[default]`/`[vm]`/
`[noprefilter]` "RX_VM_POSS_ARMS stamped but denying them changes nothing"
(16 under `[vm]`). Every named pattern compiles BYTE-IDENTICALLY (abi digits
aside) under main's and the lane's compilers, on default, `--engine=vm` and
`-fno-prefilter` (45 compiles, 0 differing), so these are [ART-POSS-ARMS]'s
(abi 66) and present on main. The run also hit its 900 s timeout before the
end; the chain reruns it at 3600 s. And `docs/design/start_table/
sabotage_anchors.py` exits 2 on main as on the lane (`UNRESOLVED
S571_deny_map_drops_run_overlap ... src/gen/memfn_sites.c 35`), so it was not
regenerated; `call_graph.py` was (its seed rule now excludes `empty_admits`
with the other E1 shape facts; seeds 15, family 135, inventory_check 150/150).

## 7. Owed, armed detached

CHAIN_PLACEHOLDER
