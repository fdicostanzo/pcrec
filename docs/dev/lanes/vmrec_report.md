# vmrec: [VMREC] step (a), the record-first VM emitter refactor (lane report)

Lane vmrec (opus), 2026-10-29. Binding sources: docs/dev/lanes/vmcons3_report.md
(rev 3) and docs/dev/reviews/2026-10-29-r9-vmcons3.md with its manager rulings
(build go for (a); FIX-6 moves the lexer, helper registry, FL and CEN to (c);
r8/r6/r3 stand). Rulings file vmrec_rulings.md: empty at every read (last read 2026-10-30
08:20); no entry applied. Resumed 2026-10-30 as vmrec2 (same lane, same
branch) after the token pause.

## Summary

BUILT; byte identity OWED to the queued gate. Every byte the VM matcher
body receives now comes from a typed record's renderer in src/gen/vm_stmt.c;
emit_vm.c builds records (92 builder call sites) and no longer holds the
body buffer at all (`StrBuf *b` is gone from `Vm`; `VmBody` is opaque). The
matcher's whole span, including the guarded `__match_notempty` copy, is one
`vm_stmt_frame` call with its own row tiling. Tiling is strict: any write
outside a renderer is an internal error at the next record. No abi bump, no
flag bit, no answer, stamp or listing change intended; the identity gate
(E1, job 740-vmrec-ident, 69 arms) is the proof and has not run yet.

Hand evidence so far: 32 spot patterns x 4 arms (default, `--engine=vm`,
`-fcomments`, `--no-captures`) = 128 compiles byte-identical to main
de89af4cb (C, header, stderr, rc); emit_sweep trials at `--limit` 20-40 (the C, VM and
listing streams, composition, a utf8 arm and one memfn arm) 0 movers, 0
asymmetric; `make strict` clean. The STOP RULE did not fire: every site
class was expressible without changing a byte, and the main merge
conflicted nowhere in emit_vm.c.

## Rev 3.1 patch

Applies r9's FIX-NOW items that bind (a). One disposition row each.

| item | disposition in (a) |
|---|---|
| SOUND-1 (template collisions; text is no discriminator) | The kind is the discriminator, never the text: each record carries its `VmKind`, set by its builder and checked by its renderer (`vm_renders`). Declared collision: SPAN init-only and SPAN_MOVE seed print identical bytes (`<p>_span_cursor = scan_position;`); they stay distinct records. The span cursor is NOT a `VmLocal` member, so no LSET can write it; only SPAN/SPAN_MOVE/SEEK(SPAN_COMMIT) touch it. A pairwise template-collision census is a reader, so it moves to (c) with CEN. |
| SOUND-5 (post-render rewrites) | The class-table respell is the ONE declared post-render exception (`vm_stmt_respell`): it tiles before, then rewrites whole, then CLOSES the body (a later build is an internal error). It only re-spells recorded reads (an unrecorded match is an internal error). RT, when built, reads the render-time domain (record offsets before respell). Tiling counts appends and truncations by uncut length only; a same-length overwrite is outside its reach (stated, not claimed). Nesting rule: a record's renderer may call delegated writers (kit, class kit, call-site table) inside its own span; no record renders inside another. |
| FIX-1 (the trail-write population) | "Trail-write records" = SET, SNAPSHOT, RESTORE: three kinds sharing one `<P>_SET` line printer. SET refuses a self-copy source (that is a SNAPSHOT); SNAPSHOT derives its source from the slot; RESTORE derives `run->trail[...+j]` from j. The nset / emitted_set / K2 / K4 / listing-set-op counters stay on emit_vm.c's primitive at today's program points (no reader moves in (a)). |
| FIX-7 (E1 population) | E1 adds the 14 `--memfn=no-NAME` arms and `.rxt`-source compiles (the corpus `.rxt` files compiled as sources, not only `--pattern`) to default, VM, nocaptures, the deny axes and `-fcomments`; compared byte for byte against the merge parent, main de89af4cb (trailgc landed, abi 93), built in scratch (ref2/). |
| FIX-8 (zero gates print populations) | Every zero gate in (a) (ST: no raw body write outside vm_stmt.c; identity diffs) prints the population it examined beside its zero, against an independent count (ST: the count of emit_vm.c's former body print sites from main, 132; identity: artifact count from the corpus file list, not from the sweep's own loop). |

Amended E-list for (a): E1 identity as above; E2-E4 as rev 3; E5 (census)
moved to (c) with CEN; E6 RT in the render-time domain, if built; E7 the
structural sabotages S1840-S1849.

## What was built

- **src/gen/vm_stmt.h / vm_stmt.c** (new, 328 + 1,439 lines): 29 record
  kinds, `vm_kind_rows[]` (one row and ONE renderer per kind; a renderer
  refuses a record of another kind), the builders, fragments (text, class
  kit, memfn kit pieces), targets (label with or without the K134
  checkpoint, fail, return), guard spellings with a stack, the SET
  self-copy refusal, `vm_stmt_respell` (closes the body), the listing-free
  readers (`vm_stmt_text`, `vm_stmt_program_bytes`), and `vm_stmt_frame`
  with `vm_fr_guarded_copy` (moved from emit_vm.c with their comments).
- **src/gen/emit_vm.c** (14,573 -> 14,201 lines): every body print became a
  builder call; the primitives keep their counters and listing events at
  their program points (`vm_lbl`, `vm_trail_check`, `vm_jump_tgt`,
  `vm_goto`, `vm_fail`, `vm_push_at`, `vm_set`/`vm_snapshot`/`vm_restore`,
  `vm_work`, `vm_cut`); compound sites pass operand structs (`VmBrefOps`,
  `VmVarOps`, `VmCalloutOps`); `vm_emit_guarded_matcher` deleted;
  `vm_emit_search_body`'s matcher span became one `VmFrame` + one call.
  `vm_run_compare`'s hook union moved to the arena (KIT pieces keep it).
- **Makefile**: vm_stmt.o in the memfn.h and callsite_rows.h dependency
  groups; emit_vm.o and vm_stmt.o depend on vm_stmt.h and clskit.h;
  run_stmt_writer.sh in `test-codegen`.
- **src/gen/CLAUDE.md** names vm_stmt.c (the deleted-runcmp line moved to
  NOTES.md for room).

## Byte identity (E1-E7)

| # | evidence | state |
|---|---|---|
| E1 | `scripts/emit_sweep.py --ref-bin ref2 (main de89af4cb) --bin lane`: arm `base` (all six streams incl. composition = the `.rxt`-source compiles, dumps, facts; self-check on; floors applied), `--arms start`, then one arm each for `--trace`, `--no-captures`, `-e utf8`, the 14 `--memfn=no-NAME` (FIX-7), every `-f` flag `--list-axes` prints (50 today: 44 deny plus the force/comments/simd/utf-check flags), and a `-DPCREC_SIMD_WITNESS` build of both sides (`--ref de89af4cb --tree-rev HEAD`, every 4th pattern). 69 arms; one line per arm in `job.log.ident`; zero failed arms is the bar | OWED: job 740-vmrec-ident |
| E2 | `make test-memfn-guarded` (in make test): the witness build's `RX_VM_PROGRAM_BYTES` and knee unchanged | OWED: job 741-vmrec-test. Main's own stale simd-form floor (5 < 6, fsfix lane) reads red here too until fsfix lands |
| E3 | `make strict`, `make test` (test-codegen with ST), `make test-recursion-identity-locked` | strict GREEN (by hand, 2026-10-30); the rest OWED: job 741-vmrec-test. Main de89af4cb's known reds (test-memfn-guarded floor; test-code's truncated long-path refusal) are not this lane's |
| E4 | tiling: 0 internal errors | every E1 compile: a tiling failure is a refusal on the lane side only, so it shows as `asymmetric` there |
| E5 | census | moved to (c) with CEN (r9 FIX-6) |
| E6 | renderer round-trip RT | NOT BUILT (optional in (a); its independent reader is (c)'s). S1845 is scored by the corpus instead |
| E7 | sabotages S1840-S1849 | built, each probed by hand on a planted build; scored by job 742-vmrec-mech |

Not covered, for the manager: E1's design row also named every pcrec-bench
pattern text with its flags. The lane did not read the bench's catalogue
(bench questions go through the bench dev); a pattern list from the bench
can be fed to the same sweep with `--patterns-file`.

## Structural checks and sabotages

**ST** `tests/codegen/run_stmt_writer.sh` + `stmt_writer_scan.py` (static,
no compiles; in `make test-codegen`; mech arm `stmtwriter`, registered
before S1840). Over the C text of every .c/.h under src/, cli/, lib/
(comments and literals blanked): `vmsb` is named only in vm_stmt.c,
internal.h's field and the driver's five lifecycle lines (free, ctx bind,
comment tier, size abort, the open-comment balance list); `struct VmBody {`
only in vm_stmt.c; vm_stmt.h returns no StrBuf. Populations printed: 110
files (independent count: git ls-files, 110), 111,798 lines, and three
positive controls (1 / 1 / 5 / 1 allowed mentions). The population it
replaces: 132 body print calls in main's emit_vm.c, now 92 builder calls
(compound sites take one call where they took several prints).

**Sabotages** (each planted, compiled -Wall -Wextra clean, and probed by
hand on a planted build; scored by job 742):

| row | plant | net | probe |
|---|---|---|---|
| S1840 | raw `pcrec_sb_puts(&job->vmsb, ";")` after each label (M12) | stmtwriter, codegen | internal error (33 bytes where 32); scan names emit_vm.c |
| S1841 | the same as a NONESSENTIAL comment line (M12, comment tier) | stmtwriter, codegen | internal error (the uncut clock counts the dropped bytes); scan |
| S1842 | raw csb print between two frame rows (M13) | codegen | internal error (span written outside its frame rows) |
| S1843 | goto row's renderer dropped | codegen | internal error (kind has no renderer) |
| S1844 | goto and fail renderers swapped | codegen | internal error (renderer handed the wrong kind) |
| S1845 | BRANCH renders the next label (M14) | harness tests/backrefs | nested.rxt 28 failed / 8 passed |
| S1846 | SNAPSHOT built as SET (M7) | harness tests/recursion | internal error (self-copy refused) on `^(a|b(?1))$` and C6 |
| S1847 | inline-braced GUARD closed as braced | harness rungselect.rxt | internal error (guard close mismatch) |
| S1848 | a record built after the respell | clspack, harness clspack_atoms.rxt | internal error (record after close) on S403's witness |
| S1849 | emit_comb.c names `vmsb` (no byte moves) | stmtwriter only | scan names emit_comb.c |

**Re-aimed anchors**: 30 anchors in 29 rows sat in rewritten text (the
anchor survey over all 148 emit_vm.c/vm_stmt.c anchors, before and after).
Each re-aim keeps its row's intent at the new site and says so in a dated
`# RE-AIMED` comment: 9 only moved file (the text is now a renderer's or
the frame's, unchanged: S105 S109 S115 S273 S145 S146 S1297 S36 S1651), the
rest re-spelled at the builder or renderer that now carries the same fact.
S51's old AFTER named a local the [M6-READ] rename had retired (it no
longer compiled); its re-aim plants the removal the row describes. Every
plant compiles; `VALIDATE_ONLY` passes all 39 rows. Scored by job 743.
Three re-aimed rows carry warnings their AFTER text already had on main
(S105, S146: a format argument count; S36: `\&` escapes); unchanged.

## Cost

- Source: +2,713 / -847 over 52 files against main (vm_stmt.c/.h 1,767 new
  lines, of which about 500 are the moved frame, guarded copy and their comments; emit_vm.c
  -372 net; the rest tests, sabotages and docs).
- Compile time: one spot measure under the full suite's load (40 VM
  compiles of one four-branch pattern per side, twice): main 1.72-1.96
  ms/compile, lane 2.16-2.23 ms/compile. Noisy (box at load 10), not a
  verdict; the records (one arena VmStmt per statement, fragments copied
  into the arena) are the expected source. The identity arms' `elapsed`
  lines measure it over the corpus.
- No abi event, no flag bit, no new stamp.

## STATE AT HANDOFF

- Branch lane/vmrec, all work committed (WIP commits per site class; this
  report last). Merge parent: main de89af4cb. Not merged to main.
- OWED (queued as this lane's last act, owner vmrec, each gated off
  19:00-00:00 and chained):
  1. 740-vmrec-ident: E1, 69 emit_sweep arms; verdict line
     `ident: arms failed N` in job.log.ident (per-arm logs
     /var/tmp/pcrec-pcrec/scratch/vmrec/e1.ARM.log). Any failed arm is a
     byte that moved: a bug in the refactor, never a re-pin.
  2. 741-vmrec-test: strict, recursion identity (FILEPIN unmoved), make
     test (E2, E3, ST). Main's known reds (memfn-guarded floor, test-code
     long-path truncation) are expected until fsfix lands.
  3. 742-vmrec-mech: S1840-S1849.
  4. 743-vmrec-mechre: the 29 re-aimed rows.
- For the manager: landing (a) needs E1 green; then a D number for "the
  record is the source" and the guide's emission-primitive entry ("one
  builder per kind"), both outside a lane's files. E1's bench-text arm is
  not covered (see Byte identity).
- Last ruling applied: none (vmrec_rulings.md empty).
