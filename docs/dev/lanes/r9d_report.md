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

## Follow-up r9fu (2026-10-08): the glibc-inside trap per site, and [MEMFN-ENTRYSINK]

Two narrow gaps the manager named after the r9 revision. Each edit is
marked `[r9fu]` in `docs/design/memfn/integration.md`. They are listed in
§R4.9.12 as follow-up rows r9fu-1 and r9fu-2. The new text is §R4.9.7.1
and §R4.9.7.2, plus F-R9-8 and pointed edits in §R4.9.2.1, §R4.9.2.4,
§R4.9.5.1, §R4.9.6, §R4.9.7 and Q-R9-2. DESIGN ONLY: no source edits and
no timed runs.

### Commands

The binary is the kit tip's, read-only: `worktrees/memfn/build/pcrec`,
`lane/memfn-m7` at 01772107. Scratch is `worktrees/r9d/build/r9fu/`
(gitignored). The box is the dev box: gcc 15.2.0, glibc 2.43.

    P=…/worktrees/memfn/build/pcrec
    gnutimeout 60 $P -p rx -o wN.c [--engine=vm] --pattern 'PAT'
    grep -E '^#define RX_(ENGINE|DFA_PREFILTER|REQ_RUN|REQ_HANDOFF|VM_PREFILTER) ' wN.c
    awk '/static inline size_t rx_(reqrun|ofsskip)\(/,/^}/' wN.c | grep -c 'memchr('
    gnutimeout 60 gcc -O2 -I. -c -o wN.o wN.c && nm -u wN.o
    gnutimeout 60 gcc -O2 -S -o - wN.c | grep -cE 'call\s+memchr'
    # R-1's emit vs today's FUNC text:
    diff <(awk '/rx_reqrun\(/,/^}/' w1.c) <(awk '/rx_reqrun\(/,/^}/' docs/design/memfn/probes/twins/gates_d4d9ed90/mi_def.inc)   # identical
    diff <(awk '/rx_reqrun\(/,/^}/' w2.c) <(awk '/rx_reqrun\(/,/^}/' …/us_def.inc)                                               # identical
    # ENTRYSINK hand twin (tw/): prefix.h = R-1's ffl block loop, no lead,
    # literal constants, as file-scope rfx_w16/rfx_w32 under level guards;
    # splice.py puts the rungs at the top of the FUNC (§R4.9.2.1's order)
    python3 -I tw/splice.py w3.c rx_ofsskip '<defs>' '<run eq>' 4 tw/t3.c   # and w1.c -> t1.c
    gnutimeout 60 gcc -O2 [-march=x86-64-v3] -I.. -S tw/tN.c
    # file-scope `static const __v16qi` variant: tw/prefix_fs.h -> t3fs.c

### Witnesses and findings

| witness | site (stamps) | BODY | memchr streams | `nm -u` |
|---|---|---|---|---|
| `(?i)cat` | PRE masked, DFA ASSIGN | fn-pair | 2 | memchr |
| `(?i)union.*?select.*?from` (+ `--engine=vm`) | PRE masked, DFA / no-DFA | fn-pair | 2 | memchr (+ `__stack_chk_fail`) |
| `(?i)\d+cat` `--engine=vm` | PRE masked, no-DFA | fn-pair | 2 | memchr |
| `(?i)(a\|b)+cat` | PRE masked, VM hybrid | fn-pair | 2 | memchr, `__stack_chk_fail` |
| `xyzzy`, `\d+xyzzy`, `[a-z]*select[a-z]*` | PRE exact, DFA | fn-memchr | 1 | memchr |
| `\d+xyzzy` `--engine=vm`, `(a\|b)+xyzzy` | PRE exact, no-DFA / hybrid | fn-memchr | 1 | memchr |
| `(?i)\d+ab/cd`, `(?i)\d+qz#x` | PRE MASKED, non-letter pick | fn-memchr | 1 | memchr |
| `/user\|/users` | OFS run-pinned | fn-memchr | 1 | memchr |

- **Glibc inside, every site.** Every batch-1 FUNC calls glibc `memchr`.
  The run verify is inline word loads, with no memcmp, memrchr or strlen.
- **R-1 and `fn-pair`.** R-1's `emit` column is byte-identical to today's
  `fn-pair` text, so R-1 DID compare against the glibc-backed twin for
  `fn-pair`. Its printed SIMD-on column (`ffl − swar`) used SWAR, which
  is the weaker statement.
- **Sparse picks are not covered.** Both R-1 cells pick a dense letter
  (C/c). A rough calculation (two glibc streams at about 30 B/ns, against
  w16 at about 21 B/ns on union-select) leaves a sparse-pick `fn-pair`
  cell's sign open. The bench must add that cell.
- **R-1 and `fn-memchr`.** There is no same-function cell. The cls-n-uc
  `nosl` columns are glibc-backed, but they set ffl's lead function, at
  AVX2 only, on a dense `i`. That makes them TRIGGER-GRADE.
  - Decision: `over` = `fn-pair` only. `vrun` over `fn-memchr` is filed
    with five cells: rare-pick exact, dense-pick exact, OFS
    `router-prefix-order`, masked non-letter pick, exact VM hybrid.
  - OFS run-pinned (exact-only pin, so always `fn-memchr`) and the exact
    bin leave batch 1.
- **No entry point is assumed.** §R4.9 assumes no function-entry point.
- **Broadcasts in the hand twin (measured).**
  - Literal `set1` becomes `mov imm; movd; pshufd` (SSE2) or `vmovd;
    vpbroadcastd` (v3). It is re-done at each rung entry and again for
    the final block. It is never a `.rodata` load and never hoisted.
  - A file-scope `static const` vector is constant-propagated back to the
    same immediates: 8 / 16 such instructions remain.
  - So plan.md's [MEMFN-ENTRYSINK] sentence "pattern-constant setup needs
    neither: gcc hoists it or it is a constant" does not hold for gcc
    15.2. That row lives in main's plan.md, so correcting it is the
    manager's job.
- **ENTRYSINK candidates.**
  - None in batch 1: every PRE FUNC is called once per `rx_search`, at
    lines 79, 70, 312 and 387 of the witnesses.
  - The ONE candidate is the filed `vrun` over OFS run-pinned. Its
    `rx_ofsskip` runs inside the DFA scan `for (;;)` on every re-seed
    (`/user|/users` l.132).
- **Q list.** Q-R9-2 is refined (the twin's glibc tier is the CPU's, not
  `-march`'s), with the same recommendation. There is no new Q.

### Validation

Docs only. Compiles and `nm`/`-S` reads on scratch artifacts only; no
timed run, no `make`.

## Revision D155 (2026-10-08, same lane)

**Input.** D155 records Frank's rulings on Q-R9-1..9 (main 3b1fd77c). Q-R9-6
is AMENDED: no `#if` inside a function body; per-level `static inline`
helpers selected at file scope; SIMD-off routes through the helper as a
measured abi event. `[MEMFN-RTDISPATCH]` is filed with its terms
(responses.md, `lane/memfn-m7` c9e90c77). DESIGN ONLY: no source edits and
no timed runs. Every edit in integration.md is marked `[D155]`.

### What changed in §R4.9

- **The shape** (§R4.9.2.5).
  - The BODY row's loop becomes `<fn>__body`, unguarded, the one scalar
    spelling.
  - Each rendered rung is a guarded helper `<fn>__w<VW>`. Its entry test
    (the derived reach) falls through by name to the next rendered rung
    or to `__body`.
  - The FUNC itself is the selector. `[rev c]` SUPERSEDED by Q-R9-10
    shape (c): the FUNC is written once and its whole body is the
    `#if`/`#elif`/`#else` chain, one call per arm, written by the seam from
    `levels.def`; the `#else` arm's call is the SIMD-off FUNC's line byte
    for byte (see "rev c text pass" below).
  - The PREFIX slot now renders whole helper definitions only.
  - Names are the FUNC name plus `__body` or `__<stamp token>`. They are
    unique because every FUNC name ends in a fixed pcrec suffix.
  - Nothing is shared between FUNCs. The intrinsics include is written
    once per level per artifact. The stamp is unchanged and lists the
    rendered arms.
- **The abi event** (§R4.9.2.6): step R4e′.0b sits between the zero-mover
  seam and batch 1. It moves +139 B per FUNC, and pcrec's side is RQ-6.
  G1 has four parts:
  - a pcrec-side mover census by id;
  - an un-done text diff that must equal the parent;
  - assembly identity at `-O2` (default and v3);
  - timing ONLY for a non-identical mover.

  Both layers are read: ON == OFF at that step by construction. Q49 is
  amended for this one step.
- **The floor rule restated** (§R4.9.2.3, §R4.9.8).
  - (a) Preprocessed-equal off-target: unchanged.
  - (b) On-target: insertions plus exactly ONE replaced line per SIMD
    FUNC, the selected call. This replaces C-6's insertion-only leg,
    which is impossible under file-scope selection. The count is checked
    against the mover census.
  - (c) The raw source is insertion-only, which makes RQ-3's
    `len − simd_guarded` exact.
  - (d) A brace-depth lint: no directive inside a body. `[rev c]` Now: a
    directive in a body only in the selector shape (whole body = the chain,
    one call per arm, nothing else).
  - Guarded bytes are whole definitions plus directives. Q-R9-9 is RULED
    (a), and `guarded_max` covers the helper, the include share, the
    selector arm and the directives.
- **Runtime dispatch** (§R4.9.3.1, filed, no dispatcher designed).
  - Frequency classes: the PRE window FUNC is INFREQUENT on every
    batch-1 route; the filed OFS `<p>_ofsskip` is FREQUENT (inside the
    DFA scan loop).
  - Target-attribute copies have the same helper text. The selector gains
    an arm for INFREQUENT sites only.
  - The set is data, so it need not cascade. Per-arch artifacts already
    work.
  - The hard problem left to the row: "chosen once" without a mutable
    static (TS-1).
- **Questions.** Q-R9-1..9 are marked RULED in place. `[rev c]` Q-R9-10
  and Q-R9-11 are now RULED too (D155 addendum 1). As raised at the time:
  - **Q-R9-10:** the FUNC-as-selector shape (C) vs an invariant FUNC
    plus `<fn>__level` (A). Recommend C. RULED shape (c), superseding (b).
  - **Q-R9-11:** the frequency class is not `MF_P_INLOOP`: D91 puts OFS
    in budget 1, and overloading the bit would make every SIMD row
    decline OFS. Recommend a `DELEG_SITES` `freq` column, born with
    RTDISPATCH (D77). RULED as recommended (kit-decided).

### Probes (scratch `build/d155/`, gitignored; gcc 15.2.0, glibc 2.43, `taskset -c 12-15`, `gnutimeout 60`)

Inputs: r9fu's twelve kit-tip witness artifacts with a FUNC
(`build/r9fu/w*.c`: eleven PRE `rx_reqrun`, one OFS `rx_ofsskip`). The
FUNC is re-rendered by `gen.py SRC FN {offC,offA,onC,onA} OUT [RUNDEFS]`.
The vector helpers are r9fu's hand twin (R-1's `ffl`, lead removed), with
the reach test as their entry statement. They are not kit renders.

    ./off_identity.sh && ./norm_cmp.sh   # today vs offC/offA, -O2/-O3/-Os -S, .LFB/.LFE renumbered
    ./levels.sh                          # 2 witnesses x {onC,onA,onCu,onCs} x 9 flag sets x {-O0,-O2}, -Wall -Wextra
    ./c18.sh                             # legs (a)/(b) on the new shape
    gcc ... drv.c                        # answer differential, 15,884,000 calls per build

Results (`[r9b]` this block predates shape (c); it was taken on the
file-scope-definitions rendering, the caveat is in "Revision c" below.
`build/d155/` is gitignored scratch; the transcript is the record):
- **SIMD-off assembly vs today.**
  - `-O2` 24/24 IDENTICAL and `-O3` 24/24 IDENTICAL (12 witnesses × 2
    shapes); no helper symbol survives.
  - `-Os`: 18/24.
    - `w8` (`(a|b)+xyzzy`) and `w17` (`(?i)(a|b)+cat`) differ only in a
      symbol name, since gcc keeps the FUNC out of line at `-Os` today
      too.
    - `w10` (`(?i)union.*?select.*?from`, `--engine=vm`) has one
      register swap across two instructions.
  - `-O0`: 1 → 2 calls per FUNC call.
- **Bytes at SIMD-off.** +139 B per FUNC (+141 for `rx_ofsskip`) in
  shape C, and +280 / +284 in shape A.
- **Warnings at every level.** 144 compiles, 0 errors.
  - Flag sets: `-mgeneral-regs-only`, default, v2, sandybridge, v3, v4,
    `-mno-sse2`, `-mavx2 -mno-sse2`, `-mgeneral-regs-only -march=v3`.
  - The only warnings are the planted control: a helper that is unused at
    v3/v4, declared plain `static`, gives `-Wunused-function` in 8 of 8
    compiles. The same helper as `static inline` is silent.
  - `-mavx2 -mno-sse2` defines neither `__SSE2__` nor `__AVX2__`, so the
    w32 guard implies the w16 guard.
- **C18.**
  - (a) EQUAL 12/12.
  - (b) At default, v3 and v4: exactly 1 deleted line, the selected
    call. Inserted: 3,236 lines (default) and about 45.8k (v3/v4).
  - (c) The source diff deletes 0 lines (4/4).
- **On-target code.**
  - At `-O2` every helper inlines into `rx_search` at every level.
  - Instruction counts: `(?i)cat` 336/418 and `/user|/users` 279/363
    (default/v3). The r9fu twin of the withdrawn shape counted 337/423
    and 276/356.
  - Broadcast counts equal r9fu's: `pshufd` 4 at default, `vpbroadcast`
    8 at v3.
- **Answers.** One result hash per witness across today, both OFF shapes
  and both ON shapes, at default, v3, v4 and general-regs.
- **Runtime-dispatch stand-in** (`w1.rt.c`).
  - The w32 helper under the dispatch guard plus `target("avx2")` is the
    same text as the static one apart from the attribute.
  - It compiles clean at default, v3 and general-regs.
  - The target-attributed helpers stay OUT OF LINE at default, so a
    dispatched site pays a call.
  - Leg (a) is EQUAL, and the answers are equal.
- **The routing gate's plants** (`plants.txt`).
  - Making `<fn>__body` plain `static` gives IDENTICAL assembly: not a
    witness.
  - `__attribute__((noinline))` gives 349 changed lines: the witness.

### Validation

Docs only. The scratch compiles and greps above are the only runs; no
timed run and no `make`. Transcripts: `build/d155/{norm_cmp,levels,c18,
diff_answers,bytes,rt,srcdiff,plants}.txt`.

## Revision c: rev c text pass (2026-10-08, same lane, doc-only)

**Input.** D155 addendum 1 (Frank, confirmed to the manager): Q-R9-10 is
RULED shape (c), superseding an intermediate shape (b) (a file-scope level
macro) that was ruled and superseded the same day; Q-R9-11 is RULED
(`freq` column in `DELEG_SITES`, built only when `[MEMFN-RTDISPATCH]`
triggers, not an `MF_P_INLOOP` flag, kit-decided). Revision stays 4.9. No
make, no suites, no measurements: probe numbers taken on the older
file-scope-definitions rendering are labelled as such and are re-measured
by R4e′.0b's G1 and the first batch's C18, not re-claimed.

### Passages changed, by section (docs/design/memfn/integration.md)

- **Short list** (top): the "No `#if` inside a function body" bullet now
  states the addendum's rule, the FUNC written once as a selector, and
  Q-R9-10/11 RULED.
- **§R4.9.2 summary** (floor-rule bullet): "no function body holds a
  directive" becomes "no function that does work", with the selector
  exception.
- **§R4.9.2.1 item 3** (assembly order): the FUNC "is a selector chain at
  file scope" becomes "written once; its whole body is the selector chain".
- **§R4.9.2.3** (floor-rule box, intro and leg (d)): leg (d) allows a `#`
  line in a body only in the selector shape (whole body = the chain, one
  call per arm, nothing else); any other is a C18 failure. "no level
  macro defined" reworded to "no ISA macro defined" (it meant `__SSE2__`
  and kin, not shape (b)'s macro).
- **§R4.9.2.4** (bracketing): selector parts bracketed are the chain
  lines inside the body; the FUNC head, braces and the `#else` call are
  unbracketed. `guarded_max`'s "selector arm" is the chain line plus one
  call. The 84-lines/0-deleted measurement is labelled as taken on the
  superseded rendering.
- **§R4.9.2.5** (the shape): the Frank-quote paragraph gains the addendum's
  verbatim rule; the SIMD-on emitted-text example is rewritten so the FUNC
  appears once with the chain as its whole body (helpers first, FUNC
  last); piece 3 rewritten; piece 2 notes the selector follows the helpers;
  the "alternative shape, Shape A" paragraph is replaced by "Ruled shape
  (c), and what it superseded", with the one sentence recording that (b)
  was ruled then superseded (D155 addendum 1) and the measurement caveat.
- **§R4.9.2.6 / G1 probes** ("C18 on the new shape"): labelled as measured
  on the superseded rendering.
- **§R4.9.3.1** and the **Q-R9-11 cross-references** (finding paragraph,
  "what it must design" list): marked RULED with the `freq` column.
- **§R4.9.8, C18 as amended** (row): leg (d) restated as above; a new
  sabotage plant (a selector arm holding more than its one call, red at
  (d)).
- **§R4.9.10**: lead paragraph now "Q-R9-1..11 are RULED"; Q-R9-9's
  "(NEW)" dropped; Q-R9-10 and Q-R9-11 rewritten as RULED entries with
  the rulings (the (C)/(A) option text removed).
- **§R4.9.12** (D155 items table): intro covers addendum 1; two rows
  added (Q-R9-10, Q-R9-11).
- **`[rev4.9]` note near the end of the file**: "Q-R9-2..8 are OPEN" ->
  RULED.

### Other files fixed

- `memfn/CLAUDE.md` (line 29): "Q-R9-2..9 for Frank" -> Q-R9-1..11 RULED.
- `docs/design/memfn/CLAUDE.md` (rev 4.9 entry): "Q-R9-1..8 are open" and
  the D155 paragraph (selector wording, leg (d), Q-R9-10/11 RULED).
- `docs/design/CLAUDE.md` (memfn entry): "Q-R9-1..9 are ruled ... a
  selector, no `#if` in a body" -> Q-R9-1..11, selector FUNC with the
  chain as its whole body.
- `docs/dev/lanes/CLAUDE.md` (r9d_report entry): "Q-R9-1..8 are for Frank".
- `docs/dev/lanes/r9d_report.md`, D155 section: the selector bullet, leg
  (d), and the Questions bullets carry `[rev c]` marks (history kept, not
  erased).
- Checked and unchanged: `memfn/docs/*.md` (no Q-R9-10/11 or (a)/(b)
  mentions), `docs/dev/plan.md`.

### Greps run (worktree root), final results

    grep -nE 'Shape A|shape A|shape \(a\)|shape \(b\)|\(C\) \*\*The FUNC|\(A\) \*\*An invariant|<fn>__level|Q-R9-10 and Q-R9-11 are (new|NEW)|Q-R9-1[01] \(NEW\)|Q-R9-2\.\.8 are OPEN' \
      docs/design/memfn/integration.md docs/design/memfn/CLAUDE.md docs/design/CLAUDE.md memfn/CLAUDE.md memfn/docs/*.md
    -> 0 hits

    grep -nE 'level macro|_LEVEL' docs/design/memfn/integration.md
    -> only: the ONE sentence recording (b) superseded by (c) (in
       "Ruled shape (c)", plus the Q-R9-10 entry's mention); MF_LEVEL
       (levels.def's own macro, lines ~602-621) and `<PREFIX>_ISA_LEVEL`
       (isa_selection.md's stamp, an unrelated old passage near line 4683).
       No passage presents (a) or (b) as the design or as open.
