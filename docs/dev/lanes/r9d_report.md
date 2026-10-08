# Lane r9d — memfn R-9, the R4e′ design pass (the SIMD layer, D147 addendum 11)

Lane r9d (opus), 2026-10-08. Branch `lane/r9d`, cut from kit branch
`lane/memfn-r9` at main 5ddd2f04. DESIGN ONLY: no source, no emitted
byte, no `make test`, no timed run. The only commands run on the box
were reads: `lscpu`, `/proc/cpuinfo`, sysfs topology and governor, and
`gcc -dM -E` macro sets.

## Delivered

- `docs/design/memfn/integration.md` REVISION 4.9:
  - a new top-level §R4.9, with subsections R4.9.0-R4.9.11;
  - `[rev4.9]` marks in place at §R4.3.2 (cascades), §R4.3.3 (the
    carried-levels grammar), §2.2 (`SCAN_ROWS`), §8.6 (K-6/K-7), §17.3
    (C9 on a box with no clang), §22 R4e′ (REPLACED) and R4f, and §23;
  - the header's revision paragraph.
- `memfn/CLAUDE.md` and `docs/design/memfn/CLAUDE.md`: rev 4.9 pointers.
- No companion doc. The Q list and the requests sit at the end of §R4.9
  (§R4.9.10, §R4.9.11), beside the revision they belong to.

## The design, in brief

- **SCAN_ROWS.** The kit's existing form tables (`arms[]`, `rc_row`).
  SIMD forms are rows beside the scalar arms. Each row declares its
  layer, an ISA level from a kit-private `levels.def` (guard, derived
  width, implied rung, stamp token) and its own `--memfn=no-<row>` deny.
  The walk adds two policy tests (`INERT:PORTABLE`, `INERT:SIZE`), a
  budget test and a static-reach test to the existing deny and contract
  gates.
- **The floor rule.** A SIMD-on rendering is the SIMD-off rendering plus
  text inside level guards: a dispatch prefix in the scalar function's
  body, with the level helpers above it. So the scalar arm is every
  ladder's floor and its one spelling. C18 checks this with the
  preprocessor at `-mgeneral-regs-only` (verified on this box to define
  no `__SSE2__`).
- **Short spans** fall to the next rung at a derived reach, `VW + T`.
  Cut-overs above it are measured. The run-time cascade is a separate,
  filed row (x86-64 Linux/ELF, a probe trigger, Q-R9-8).
- **The axis** `-fmemfn-simd` is BUILT and inert (R4c AXIS). pcrec owes
  `--memfn=` (RQ-1), and other requests depending on rulings and
  measurements (RQ-2..5).
- **The regime.**
  - Verdict box: the Linux dev box (Q-R9-1).
  - One logical CPU, with its SMT sibling idle.
  - One binary per arm.
  - Every arm at each live `-march` level, against SIMD-off at the same
    `-march` and against the row it displaces.
  - Floor = DENY vs OFF; a new placement band for per-call cells.
  - A D149 table for every constant.
- **The bar** is per row and per live level. There is a named-benefit
  path. Acceptance records go in `tests/memfn/simd_accept.tsv`, and C19
  re-opens them on a scalar change.
- **Batch 1:** the pre-check composite's window run with no lead, rows
  `vrun-w32`/`vrun-w16`, on R-1's union-select and mod-i cells.
  Everything else is filed with the cell it lacks.

## Findings worth carrying (§R4.9.1)

1. **F-R9-1.** R-1's pc16 column ran the SCALAR path in every `ffl`
   cell at both widths (`n − pos < VW + T`). Its "16 B AVX2 losses" and
   its 16 B "wins" (−1.69..+0.68 ns, stable across three launches) are
   per-binary placement of one scalar loop. That is two to thirty-four
   times R-1's own floor at the same cell.
2. **F-R9-2.** R-1's SIMD-on reading subtracted an SSE2-build `swar`
   from an AVX2-build `ffl`, so it crossed `-march`.
3. **F-R9-3.** Against the CURRENT scalar layer (`emit`, or the
   lead-first `swlf` that R4d would ship), userpass's vector forms are
   NULL on throughput and LOSE per call. That is why the lead shape is
   out of batch 1 (K-1).
4. **F-R9-4.** The verdict box changed. pcrec's Linux box is a 7700X
   (Zen 4, x86-64-v4) with no quiet-box floor yet. R-1 is Zen 1, so its
   numbers are trigger-grade only.
5. **F-R9-5.** SIMD-on text is longer, and pcrec has length-predicated
   selections (the VM entry-shape knee, `fit_rungs[]`). So the switch
   could move a rung or the refusal set. C-SEL measures that before any
   fix is built (RQ-3).
6. **F-R9-6.** pcrec carries no `--memfn=` string, so no kit row has a
   reachable OFF arm today.
7. **F-R9-7.** opt3's DFA candidate skip skips 0 bytes per entry on real
   text. That is negative evidence for a PF byte-set SIMD skip.

## Open for Frank

Q-R9-1..8, in §R4.9.10, each with a recommendation. The manager runs the
D6 panel next.

## Validation

None applicable: docs only, no build. Every number in §R4.9 was copied
from the committed R-1 transcripts (`docs/design/memfn/probes/out/twins/
r4b/linux/readings.gcc.md` and `tb.gcc-*.txt`) or from
`linux_results.md`. Every box fact was read on 2026-10-08.

## Revision after panel r9 (2026-10-08, same lane)

Input: the D6 panel r9 (`docs/dev/reviews/2026-10-08-r9-memfn-simd.md`,
critics in `2026-10-08-r9-memfn-simd/`; 43 findings: 2 BLOCKER, 20 MAJOR,
21 MINOR) with the manager's dispositions, and the rulings that postdate
the first draft: D144 addendum 4, D147 addenda 11-13 (13 PRELIMINARY,
read from main 26297b6c), M6 = VMSTRIDE at `MF_SITE_ABI` 8. The kit tip
(`lane/memfn-m7`) was read READ-ONLY for the facts the base lacked; it was
not edited. DESIGN ONLY again: the only commands run were reads and one
`gcc -dM -E` probe (`-mx32` and `-m32 -msse2` both define `__SSE2__`,
`-mx32` also `__x86_64__`, so the level guards exclude `__ILP32__`).

### What changed

- **§R4.9 rewritten in place**, still revision 4.9, every edit marked
  `[r9 <id>]` (119 marks). The header, §R4.3.2/§R4.3.3, §2.2, §8.6,
  §17.3, §22 R4e′/R4f and §23 marks are updated to match.
- **F-1 (BLOCKER), the seam.** Step R4e′.0, kit-only and zero-mover,
  makes `ofs_fn_define`'s body a first-match table `fn_rows[]` with a SLOT
  column: BODY (the two scalar loops, `fn-pair`/`fn-memchr`, which are
  today's inline `b >= 0` branch moved into rows) and PREFIX (born empty).
  The seam passes the calling SITE into the walk, asks BODY first, and
  assembles the slots in a fixed order, so no row calls or wraps another.
  SIMD rows are PREFIX rows with an `over` column (the BODY rows they may
  sit over) and a `rungs` list (the same-form rows their dispatch names),
  so the ladder is data, not a walk-on. Reach: every FUNC part, i.e.
  `<p>_reqrun` (PRE window, every route), `<p>_reqrun_whole` (PRE whole
  run, never reached by batch 1) and `<p>_ofsskip` (OFS; `run-pinned`
  reached when the k-set is the run alone, `offset-set` never). OFS
  run-pinned, which R-1 never timed, gets its own pre-registered cell
  (bench run-pinned artifacts exist, `router-prefix-order`'s `/user` the
  named witness), with a structural exclusion on `op` as the fallback. No
  pcrec part is needed for the seam: the kit owns the renderer (RQ-0).
- **M-1 (BLOCKER), reframed by D144 addendum 4.** Two tiers. Tier U
  (kit probes, lane alphas, dev-box `taskset`, the Mac) is directional and
  decides triggers, constants to submit and a veto. Tier O is a
  pcrec-bench run, pre-registered, on EACH box that executes the level
  (w16 and w32: ubuntubudu AND the dev box; w64: the dev box; aarch64: the
  Mac under addendum 8). The bench submission (§R4.9.5.1) is requested
  through the pcrec manager BEFORE acceptance; the kit never writes to
  pcrec-bench.
- **The rest, by theme:** T defined once as `max_reach(pred)` with the
  reach derived from the highest read (C-1); one shared kit walk for
  `arms[]`, `rc_row` and `fn_rows[]`, `policy`/`budget` as `fields.def`
  fields with the existing `DECLINED` verdict, one deny carrier with
  `MF_D_RUN_OVERLAP` the named legacy exception (F-2, F-3, F-12);
  selection neutrality by construction (`simd_open`/`simd_close` sink ops,
  pcrec's length readers subtract guarded bytes, RQ-3) and D84's caps as
  Q-R9-9 (C-3); the cascade guard with `__SSE2__` and above the full
  ladder (C-4); G2's multi-hit/near-miss/`pos` axes, per-path plants and
  coverage floors, poisoning (C-5, C-10); C18's insertion-only on-target
  leg (C-6); intrinsics included inside the guard (C-7, F-10); guards with
  `__x86_64__`, C9-x86 at six macro sets (C-8); the null population as
  the noise band, the alignment relink withdrawn (M-5, M-6); bins by
  cause, no "< 8" exclusion (M-7, C-11); the record's states and C19 as a
  never-red STALE detector bound to transcripts (M-2, M-8, F-11); one
  `simd` sweep arm with named projections (F-5); the filed list re-read
  against the kit tip (F-7) and F-6 recorded as decided NO.

### Questions for Frank (§R4.9.10)

- Q-R9-1 RESOLVED by D144 addendum 4 (nothing to rule).
- Q-R9-2 (revised): each row at each level it targets, on every bench box
  running that level; a loss on any blocks the level, a win on one is
  needed; a row may land as a CANDIDATE before its bench reading.
  Recommend yes.
- Q-R9-3: KB as a pcrec fact (`plan_pos2`). Recommend (a).
- Q-R9-4 (revised): a measured named benefit with no timing loss is
  accepted; code space is never such a benefit for these SIMD rows.
- Q-R9-5: a re-opened comparison never blocks a scalar change (C19 →
  STALE). Recommend no-block.
- Q-R9-6: the floor rule. Recommend yes.
- Q-R9-7: one deny per (form, width) through the one carrier. Recommend.
- Q-R9-8: admit the cascade's libgcc link dependency under SIMD-on,
  x86-64 Linux/ELF, under C-4's guard, spec-stated. Recommend admit.
- Q-R9-9 (new): D84's caps EXCLUDE guarded bytes, with a per-row constant
  bound (`guarded_max`) checked by G2. Recommend exclude.

### Not applied, and why

Nothing. 42 ids applied as dispositioned; F-6 decided NO and applied as
that decision (§R4.9.12). Two things are left to the manager because this
lane may not write them: relaying the F-6 decision to the kit's
`responses.md` as the answer to R-10's Q-R10-10, and reconciling this
revision's 4.9 with the kit tip's 4.8 `[M7]` text at merge (F-9).

### For whoever resumes

- The seam (R4e′.0) is the next request, kit-only and zero-mover. Its
  census (an `MF_TRACE` build counting `fn` walks by customer and
  predicate shape) is what names the OFS run-pinned and VM-hybrid bins'
  cells.
- D147 addendum 13 is preliminary and invites R-9's panel to propose a
  better regime; §R4.9.6 and Q-R9-2 are that proposal.

### Validation

None applicable: docs only, no build, no timed run.
