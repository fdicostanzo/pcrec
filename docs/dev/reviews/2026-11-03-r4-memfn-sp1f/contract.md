# Critic round memfn-sp1f, lens `contract`

SUBJECT 98145b3d5 (lane/memfn-sp1f), BASE 761521515. Binaries: the SUBJECT
worktree build/pcrec and the BASE archive build/pcrec. Probes are in contract/p/.

## Findings

### CONTRACT-1 (CONFIRMED; doc/contract; effort trivial; blast radius: the `--list-axes` doc column for `fd-d1` plus one options.def comment)
`fd-d1`'s surviving registry text is false, and it disagrees with the spec row.
memfn/src/options.def:63-65 (the dump's doc column) still ends "(ASSERT_ZERO until it routes at B2)".
docs/spec/registry.md §6¶8a calls `fd-d1` "A MOVING deny", and the binary agrees: `build/pcrec -p rx -o o.c --pattern 'x'`
with and without `--memfn=no-fd-d1` gives different bytes (the same holds for `foo\d+bar`).
The group comment directly above (options.def:53-60) is the hunk this lane edited. It keeps "one per
built row the evaluator can score" and "At B1 NO row is routed, so every one is ASSERT_ZERO". After 1f
that group is `fd-d1` alone, and `fd-d1` is DIFFER.
Repro: `build/pcrec --list-axes | grep '^fd-d1'` on either binary.
This is PRE-EXISTING (BASE prints the same text, stale since B2). 1f is still the change that left a
one-member group whose header comment describes four denies. The fix is to reword the doc string
(for example "denied, ... D1w's table walk") and the comment. The doc column is not an emitted
artifact byte, so this is no abi event.

### CONTRACT-2 (CONFIRMED; doc; effort trivial; blast radius: memfn.h public-header comments only)
After 1f, three statements in the public header describe consumers that no longer exist:
- memfn/include/memfn.h:1015-1020 (`mf_hooks.start`) says it is "the knowledge key N's other
  operand ... a row that reads N skips. No rendering reads it before a dispatch row routes (B4/B8)".
  1f deleted the dispatch rows R1/R2 and the N comparator (`FL_N`, finder.c:108). No row needs N
  (the `--finder-rows` listing shows needs only `P`/`PE` on all 10 rows). The hook is still bound
  (compose.c:1125/1241), but its stated purpose is gone.
- memfn.h:1530 `mf_finder_listing.needs`: "the knowledge keys: P E A I M N H". `H` left the
  alphabet at 1a (sp1afix). After 1f, A, M and N (and I) appear on no row either. The 1a precedent
  deleted KN_H from `needs_names` "since no row carried them". 1f keeps KN_A/KN_I/KN_M/KN_N and
  `needs_names "PEAIMN"` (finder.c:60-61, :827) with no carrier, which goes against that precedent.
  This is maintenance, not answer-level: a declared vocabulary no row uses.
- memfn.h:1507 (`mf_form_hash`): "a card naming a form a later step builds: V1 at B4, the W64 rows at
  B6". R8 was the only W64 row, and it is deleted. The comment should say W64 has no row.
The fix is to reword these comments, and either drop the uncarried KN bits or state why they stay.
None of this moves an MF_SITE_ABI or MF_CLASS_V number.

## PROBED-AND-HELD

- **Every carrier refuses the retired names, as the spec states (registry.md §6¶8a, which now names
  `no-fd-r8`/`no-fd-ndisp` as unknown options).** 4 routes, BASE vs SUBJECT:
  - CLI `--memfn=`: `no-fd-r8`, `no-fd-ndisp`, bare `fd-r8`, and the combined lists
    `no-fd-d1,no-fd-r8`, `no-fd-r8,no-fd-d1` and `no-fd-ndisp,no-window-search`. BASE: rc 0
    (bare `fd-r8` gave "option can only be denied"). SUBJECT: rc 1 with
    `pcrec: --memfn=: unknown option 'no-fd-r8' (pattern offset 0)`, which is byte-identical in
    tier and wording to the fd-r0/fd-r5 precedent (probed on both binaries). A valid `no-fd-d1`
    alone is still rc 0. 9 strings × 2 binaries.
  - A config's raw `pcrec --memfn=` line in a .rxt (3 strings): SUBJECT gives
    `FILE:6: target 't': --memfn=: unknown option 'no-fd-ndisp' ...` with rc 1; BASE gives rc 0.
  - CLI `--memfn=no-fd-r8` together with a config `--memfn=no-fd-d1`: rc 0 on both, because the
    config wins silently (cli.md §1.16¶4) and the CLI string is never validated. This matches the
    spec and is not a new hazard.
  - CLI later-wins (`--memfn=no-fd-r8 --memfn=no-fd-d1`): rc 0 on both. Empty `--memfn=`: rc 0.
  - Library `pcrec_options.memfn` (my own driver linked against each libpcrec.a; 6 strings): SUBJECT
    returns -1 with `--memfn=: unknown option 'no-fd-r8'` / `'no-fd-ndisp'`, and BASE returns 0.
    `no-fd-r0` is refused identically on both. `no-fd-d1` and `""` return 0.
  - A .rxt has no carrier besides the config's raw `pcrec` line (cli.md §1.16¶3 lists three
    carriers).
- **The dump matches the spec.** `--list-axes` BASE→SUBJECT differs by exactly the two lines `fd-r8`
  and `fd-ndisp`. The memfn section has 12 rows, which equals §6¶8b's floor of 12, and the name set
  equals the §6¶8a table's (the table lists vrun-w16 before vrun-w32, a pre-existing order
  difference with no reader). Every row's kind, budget and layer matches ¶8a's prose: vrun-* are
  scan/simd, and everything else is any/scalar, so ¶8a's dropped "except `fd-r8`'s `simd`" is
  right. axes_registry_check.sh's floor arm (`rows < floor` fails) is satisfied at 12/12. memfn
  rows add no per-row PASS lines, so run_registry_tests.sh's 245 pin does not move.
- **Byte identity.** 7 patterns × {default, --engine=vm, -fmemfn-simd, --memfn=no-fd-d1,
  --memfn=no-fd-pres-pick}: BASE and SUBJECT are cmp-identical (35, with the 5 `\b` cases refused
  identically on both). BASE `--memfn=no-fd-r8,no-fd-ndisp` equals SUBJECT default on 7 patterns,
  so the old denies really were inert and the refusal loses no artifact a caller could have had.
  42 compiles per binary.
- **Readers of the retired names, by grep of the SUBJECT tree** (excluding lanes/reviews/journals):
  each remaining mention is either history (finder_history, history/claude_md, the r17b_prime and
  span_pick design docs, fdb1's B1 declared-dumps TSV) or a retirement note (finder.c header,
  options.def, memfn.h's ABI 21 entry, include/CLAUDE.md, finder_check.py's RETIRED_DENIES and
  WITHDRAWN_ROWS, memfn_arm.py, emit_sweep.py, scripts/NOTES.md, run_sabotage_matrix.sh, and S917's
  reason). docs/spec, docs/guide and examples have no mention left. `mf_finder_pay`,
  `mf_pay_operands`, `MF_PAY_MAXPT` and `--pay-grid` survive only in retirement notes.
- **`mf_finder_rows` listing** (arm_fixtures built against the SUBJECT libpcrec.a): 10 rows, `unpaid`
  `-` on every row, which matches memfn.h's new comment and memfn/src/CLAUDE.md's "10 rows". The
  OPTION lines no longer include fd-r8/fd-ndisp.
- **MF_SITE_ABI 21 / MF_CLASS_V 7 readers:** every numeric mention outside memfn.h is a historical
  tag (fields.def, kit.h, g2 tests). pcrec reads `pres_row`/`pres_led` as indices into the same
  build's `mf_finder_rows` listing (memfn_sites.c:784-787), so the index shift is consistent by
  construction. `s->abi = MF_SITE_ABI` (formhash.c) reaches no emitted text (byte identity above).
  include/CLAUDE.md and memfn.h's history agree on 21 and 7.
- **D80:** spec hunks are in the same change (¶8, ¶8a, ¶8b). **D174:** no new caller-facing name.
  **pcrec abi:** no emitted byte moved, and cli.md §1.16¶6 says the option is no abi event, so no
  pcrec abi bump is owed. **A caller-visible break?** Yes, a previously accepted string is now
  refused. This follows the fd-r0/fd-r5 precedent (refused as unknown, stated in ¶8a, no alias),
  and it is pre-1.0 (memory pcrec-abi-changes-pre-release). The denies were inert, so a refusal
  replaces a no-op and no answer or artifact is lost. Nothing more is owed beyond the spec
  sentence, which is present.
