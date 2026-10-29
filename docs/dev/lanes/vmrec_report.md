# vmrec: [VMREC] step (a), the record-first VM emitter refactor (lane report)

Lane vmrec (opus), 2026-10-29. Binding sources: docs/dev/lanes/vmcons3_report.md
(rev 3) and docs/dev/reviews/2026-10-29-r9-vmcons3.md with its manager rulings
(build go for (a); FIX-6 moves the lexer, helper registry, FL and CEN to (c);
r8/r6/r3 stand). Rulings file vmrec_rulings.md: empty at every read so far
(last read 2026-10-29 16:30); no entry applied.

## Summary

IN PROGRESS (WIP handoff, token pause). The record module
(src/gen/vm_stmt.h/.c: 29 kinds, kind table, one renderer per kind, tiling
builder, respell as the one declared post-render rewrite, the one-call
frame with its own row tiling and the guarded copy) is written and compiles
clean (-Wall -Wextra, with and without PCREC_SIMD_WITNESS). It is NOT yet
called: emit_vm.c still prints its body directly, so the build is
unchanged in behaviour. Site conversion, identity, checks and sabotages are
still owed; see STATE AT HANDOFF.

## Rev 3.1 patch

Applies r9's FIX-NOW items that bind (a). One disposition row each.

| item | disposition in (a) |
|---|---|
| SOUND-1 (template collisions; text is no discriminator) | The kind is the discriminator, never the text: each record carries its `VmKind`, set by its builder and checked by its renderer (`vm_renders`). Declared collision: SPAN init-only and SPAN_MOVE seed print identical bytes (`<p>_span_cursor = scan_position;`); they stay distinct records. The span cursor is NOT a `VmLocal` member, so no LSET can write it; only SPAN/SPAN_MOVE/SEEK(SPAN_COMMIT) touch it. A pairwise template-collision census is a reader, so it moves to (c) with CEN. |
| SOUND-5 (post-render rewrites) | The class-table respell is the ONE declared post-render exception (`vm_stmt_respell`): it tiles before, then rewrites whole, then CLOSES the body (a later build is an internal error). It only re-spells recorded reads (an unrecorded match is an internal error). RT, when built, reads the render-time domain (record offsets before respell). Tiling counts appends and truncations by uncut length only; a same-length overwrite is outside its reach (stated, not claimed). Nesting rule: a record's renderer may call delegated writers (kit, class kit, call-site table) inside its own span; no record renders inside another. |
| FIX-1 (the trail-write population) | "Trail-write records" = SET, SNAPSHOT, RESTORE: three kinds sharing one `<P>_SET` line printer. SET refuses a self-copy source (that is a SNAPSHOT); SNAPSHOT derives its source from the slot; RESTORE derives `run->trail[...+j]` from j. The nset / emitted_set / K2 / K4 / listing-set-op counters stay on emit_vm.c's primitive at today's program points (no reader moves in (a)). |
| FIX-7 (E1 population) | E1 adds the 14 `--memfn=no-NAME` arms and `.rxt`-source compiles (the corpus `.rxt` files compiled as sources, not only `--pattern`) to default, VM, nocaptures, the deny axes and `-fcomments`; compared with `cmp` against the merged base (ebe416424) built in scratch. |
| FIX-8 (zero gates print populations) | Every zero gate in (a) (ST: no raw body write outside vm_stmt.c; identity diffs) prints the population it examined beside its zero, against an independent count (ST: the count of emit_vm.c's former body print sites from main, 132; identity: artifact count from the corpus file list, not from the sweep's own loop). |

Amended E-list for (a): E1 identity as above; E2-E4 as rev 3; E5 (census)
moved to (c) with CEN; E6 RT in the render-time domain, if built; E7 the
structural sabotages S1840-S1849.

## What was built

So far: src/gen/vm_stmt.h (record types, builders, frame facts) and
src/gen/vm_stmt.c (renderers, kind table `vm_kind_rows[]`, `vm_build` with
tiling and the missing-row refusal, guard spelling stack, SET self-copy
refusal, `vm_stmt_respell`, `vm_stmt_frame` moved from
`vm_emit_search_body`'s matcher span + `vm_emit_guarded_matcher`). No
analysis machinery (no lexer, registry, verdicts, statement ids).

## Byte identity (E1-E7)

Not run yet. Reference binary: /var/tmp/pcrec-pcrec/scratch/vmrec/ref/build/pcrec
(git archive of ebe416424, built). Tool: scripts/emit_sweep.py with
`--ref-bin` and the FIX-7 arms.

## Structural checks and sabotages

Not built yet. Planned S1840-S1849: raw body print; comment-tier raw print;
raw csb print inside the frame; kind row removed; renderer swapped; BRANCH
wrong target (RT); snapshot built as SET; GUARD/GUARD_END spelling mismatch;
record after respell; ST violation. Sabotage anchors in emit_vm.c: baseline
of 134 anchors (all valid) in scratch anchors_base.tsv; ~53 sit in regions
the conversion rewrites and need intent-preserving re-aims.

## Cost

Not measured yet (compile-time cost of records: arena per record ~ sizeof
VmStmt; owed with the identity run).

## STATE AT HANDOFF

- Branch lane/vmrec at the WIP commit carrying vm_stmt.h/.c and this report;
  base ebe416424 = main 29efe73cd + lane/trailgc ffd1f578e (abi 93). When
  trailgc lands on main, `git merge main` alone, main's side on conflicts.
- Next: convert emit_vm.c body sites (survey with line numbers in the lane
  transcript; primitives first: vm_lbl, vm_trail_check, vm_jump, vm_goto,
  vm_fail, vm_push_at, vm_set, vm_work_at, vm_cut, vm_mrl_test; then
  islands/spans, cursor rung, revdet, calls/regions, ctx rows, compounds,
  vm_emit_node blocks, accept; then the frame call replacing
  vm_emit_search_body's span and vm_emit_guarded_matcher). Replace `v->b`
  with a `VmBody *`; `vm_run_compare`'s stack `PcrecMfU` must move to the
  arena (KIT pieces copy hooks). Makefile deps for vm_stmt.o; src/gen/CLAUDE.md.
- Known check to make at conversion: the frame text in vm_stmt_frame was
  copied from emit_vm.c 12948-13446 by hand; diff it against the original
  before deleting the original.
- Owed: identity sweep, ST/RT/sabotages, make strict/test-codegen, the
  queued vmrec-ident / vmrec-test / vmrec-mech jobs, history index row,
  lanecheck.
