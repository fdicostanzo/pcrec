# vmlmerge — main (RQ-3, abi 71) merged into VMLAZY (abi 72), kit request R-12

Lane vmlmerge (2026-10-09, opus, light). Branch `lane/vmlmerge`, cut from
`lane/memfn-vmlazy` (41281588). Merge of main `631771b7` = `fd295ec0`;
FILEPIN self-pin = `9abebf34`; this report on top.

## 1. Conflicts and resolutions

| file | resolution |
|---|---|
| `src/gen/emit_dfa.c` | `PCREC_ARTIFACT_ABI 72` (this branch's) |
| `docs/spec/match_api.md` guard example | 72 |
| `docs/spec/match_api.md` §6 | 72 entry (now "bumped it from 71 ... `71` is RQ-3's, landed first") above RQ-3's 71 entry (turned to "was `71`", content intact) above 70 |
| `tests/codegen/run_codegen_tests.sh` | `ABI_EXPECT=72`; ledger message = main's (ending at RQ-3 70->71) + VMLAZY's transition re-spelled `71 -> 72` |
| `tests/codegen/run_recursion_identity.sh` | both SELF-PIN comment blocks (RQ-3's, then a VMLAZY one); FILEPIN re-pinned to the merge `fd295ec0` in its own commit `9abebf34` |
| `tests/mech/sabotages/S693_abi_not_bumped.sh` | BEFORE 72, AFTER 71 (the parent's number, the row's convention), SAB_DESC and a re-aim note |
| `docs/dev/lanes/CLAUDE.md` | both sides' entries |

Also: `tests/codegen/CLAUDE.md`'s VMLAZY entry notes the landed 71 -> 72.
Auto-merged without conflict: `emit_vm.c`, `src/gen/CLAUDE.md`,
`tests/memfn/CLAUDE.md`. `make -j8` and `make strict` green on the merge.

## 2. Readers of the number, by grep

`git grep -nIE '\babi[ :=_"(]*7[012]\b|abi.{0,3}7[012]\b|ABI_EXPECT=|ABI_H 7[012]|!= 7[012]\b|ARTIFACT_ABI 7[012]'`
(lanes/journal/design/reviews/plan excluded), after the merge:
- CURRENT-abi readers, all 72 (6 sites): `emit_dfa.c:54`, `match_api.md:301/302/305`
  (guard example), match_api §6 head entry, `run_codegen_tests.sh:3042`
  `ABI_EXPECT`, S693 BEFORE.
- History, left: `limits.md:797`, `match_api.md:4173`, `tuning.md:2035`,
  `src/gen/CLAUDE.md:1129`, `tests/codegen/CLAUDE.md:3806` (RQ-3 at 71);
  `cpset_structure.sh:907`, `run_resource_tests.sh:744`, `emit_sweep.py:1847`
  (dated re-pin notes); `memfn/docs/{requests,responses,wake}.md` (dated
  ledger lines); `decisions.md:6666`; `studies/revend_twin/` (committed
  study artifacts at abi 70, never built by make); the vmlazy-era
  `70 -> 72` notes in `tests/mech/CLAUDE.md`, `tests/memfn/{CLAUDE.md,
  c12_ceilings.tsv}`, S693 header.

## 3. Second reader class (byte counts)

`test-cpset-structure` (EMITTED_BYTES [3]), `test-resource` (K59 rung),
`test-memfn-arms` (C5 pins): all GREEN unchanged on the merge — nothing to
re-pin. RQ-3's +52 B and VMLAZY's lazy-prefix bytes do not meet in any
pinned witness.

`emit_sweep.py` VARIANT_PINS (not a make target; full population is the
slot's): measured on the 114 unique lazy movers of
`docs/design/memfn/probes/vmlazy/out/movers.tsv`, `--ref 631771b7
--tree-rev HEAD --variant lowsize|lowboth --bases byte`, PARTIAL population
(logs in the session scratchpad, not kept):
- asymmetric = 0 on every stream (no refusal flips).
- `(a{2,3}?){2,3}` at the LOWERED cap now drops its VM hybrid's prefilter
  (size-cap note on stderr; emit-ir-auto base `yes-collapsed` 2 -> 1,
  `no-size-cap` 6 -> 7; lowboth 3 -> 2 / 6 -> 7).
- `c{1,}?(?:$|[\n\t]+?01{1,2}|[^abc]){2,}` is refused on both sides; the
  refusal's byte figure 31706 -> 31938.
- `-fprefilter` arm: 7 listing movers, `refused` 86 -> 87, `yes-collapsed`
  2 -> 1.
So the lowsize/lowboth cells' `yes-collapsed` counts can fall by 1 and
`no-size-cap`/`refused` rise by 1: a full `--variant all` run at the slot
must re-measure, and re-pin only by its measurement (§5 OWED).

## 4. Check verdicts (taskset -c 12-15, gnutimeout)

Verdict by `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`:
- `make test-recursion-identity`: **RED** — `make: *** [Makefile:1058:
  test-recursion-identity] Error 1`; checks passed 9, failed 4:
  `[default] (A) 53`, `[vm] (A) 114`, `[noprefilter] (A) 53`,
  `[nocaptures] (A) 28` call-free patterns "emit a DIFFERENT PROGRAM REGION
  than ac4917d for a reason no ruling has recorded". Every listed pattern is
  a lazy cursor pattern (`(?:ab){3,}?`, `(?:a+?)+?b`, `((a{1,2}?){1,2}){1,2}`,
  ...), and 114 = the unique pattern count of vmlazy's movers.tsv (set
  equality not checked: the gate's diff lists live in its temp dir; rerun
  with `KEEP=1`). Cause: NORMALIZE re-spells the lazy rmin prefix INSIDE the
  VM program body, the span (A) compares against the pre-module pin. Example,
  `(?:ab){3,}? --engine=vm`, main vs merge:
  ```
  -    rx_span_cursor = scan_position;            (hoisted before the block)
  -        while (it_ < 3UL) {
  -            if (!(rx_span_cursor + 2 <= subject_length && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98))) goto rx_fail;
  -            rx_span_cursor += 2; it_++;
  +        rx_span_cursor = scan_position;
  +        while ((rx_span_cursor + 2 <= subject_length) && it_ < 3ULL && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98)) {
  +            rx_span_cursor += 2;
  +            it_++;
  +    if ((ptrdiff_t)rx_span_cursor < slot_values[2] + 6) goto rx_fail;
  ```
  No ruled bucket admits it (NORMALIZE has no deny axis). The precedent for
  exactly this class is R4h's SEVENTH NAMED EXCEPTION, `adv_layout_canon`: a
  two-sided canonicalizer applied before every comparison, with a
  non-vacuity census. An EIGHTH exception canonicalizing the new lazy prefix
  (cursor init + capped scan + reach test) back to the old counted loop is
  the likely shape. It is a check-design change: NOT done here, a ruling
  for the managers. The vmlazy lane never ran this gate (§8 step 2 was the
  slot's), which is how it surfaced only now.
- GREEN (rc=0, no `*** [test-` line): test-codegen, test-registry,
  test-rxtsource, test-resource, test-cpset-structure, test-memfn-arms,
  test-memfn-stamps, test-memfn-rows, test-memfn-manifest,
  test-memfn-deleg, test-memfn-forms, test-memfn-reach.
- Mech S693 solo (`bash tests/mech/run_sabotage_matrix.sh S693`):
  `codegen:2fail/328pass DETECTED`; `== mech run COMPLETE: 1 rows
  (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0, ...) at
  9abebf34 ==`.

## 5. Owed

1. The recursion-identity (A) ruling and its implementation (eighth
   exception or other), then the gate re-run: 16/0 expected only after it.
2. Full-population `emit_sweep --variant all` at the slot; lowsize/lowboth
   emit-ir-auto/stderr tallies may move by 1 (§3).
3. The rest of vmlazy_report §8 (G1 census at the merge, identity gate,
   N2, G2 full, perfrun, mech rows, anchors).
