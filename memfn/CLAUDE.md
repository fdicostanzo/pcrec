# memfn/ — pcrec-memory-functions, the in-tree kit

`[MEMFN]` (docs/dev/plan.md). Frank's rulings 2026-10-05:
- D146: the kit is a DELEGATE, not a price market;
- D147: layers;
- D147 addenda 1-9:
  - Q35-Q42 and Q50 ruled;
  - ONE SIMD switch, OFF by default;
  - every search site migrates, under a checked manifest;
  - Q51/Q52 rejected;
  - Q43-Q46, Q48 and Q49 ruled; Q47 refined: the kit's own option
    namespace (below).
- D147 addendum 10: Q53-Q55 ruled as recommended (the libc record's
  refined form; N7 `pending`; `MEMFN_FORMS` attributed outside the
  artifact).

The design of record is `docs/design/memfn/integration.md` (rev 4.9;
read its §R4.9, then §R4.8 and §R4.7, first). §R4.9 (R-9, lane r9d,
2026-10-08) is the SIMD layer's design pass under D147 addendum 11.
Revised after the D6 panel r9 (43 findings, §R4.9.12): a zero-mover step
R4e′.0 first makes the FUNC part PRE and OFS share (`ofs_fn_define`) a
first-match table `fn_rows[]` with BODY and PREFIX slots; SIMD forms are
PREFIX rows of it, with a layer, an ISA level (`src/levels.def`, born with
batch 1) and their own `--memfn=` deny, under one shared walk. A SIMD
rendering is the SIMD-off rendering plus guarded text (the floor rule).
Verdicts are two-tier (D144 addendum 4): kit timings are unofficial; an
official verdict is a pcrec-bench run on each box a level targets,
requested through the pcrec manager (the kit never writes to the bench).
The first batch (`vrun-w32`/`vrun-w16`) is there, and Q-R9-1..11 are RULED (D155 and addendum 1: a function that does work never contains `#if`; a selector's whole body may be the `#if` chain, one call per arm). §R4.8 is M1b's contract (R-5:
`stamp_int`, `run_cmp` retired, `MF_SITE_ABI` 4). R4h prep (2026-10-08,
Q-R4h-1 (a)) made it 5: `mf_site.count_by_caller`, the caller-owned ADVANCE
counter; it also added the ADVANCE hooks' shape classes (fields.def) and
recorded Q-G2-5 ruled (memfn.h), all kit-only with no pcrec byte moved.
M4 prep (R-7, 2026-10-08, Q-R7-1/2/3) made it 6: a FIND whose every term
reads below its candidate has its range bounded by its reads (it reaches
`n`), `MF_EMPTY_AT_N` (empty only as lo == n over a non-NULL subject) and
the `on_miss` class LOOP_EXIT (`break;`, which the generic row never
serves), plus the row `pf_memchr_back` that M4's `(?m)^` skip takes; again
kit-only, no pcrec byte moved. M7 prep (R-8, 2026-10-08, Q-R8-2/4/5/9) made
it 7 and `MF_VOCAB` 3: the op `MF_OP_MISMATCH` (F8, the encoding seam's
span-compare LOOP, a statement site inside pcrec's own residual function),
the handoff `MF_H_ON_DIFF`, the term kind `MF_T_REF`, the fact
`mf_site.fold_kind` (NONE/ASCII/UCP) and the hooks `ref`/`reflen`/`fold`
(pcrec's fold TEXT, `@` the byte); one renderer (`src/mismatch.c`) as two
rows, the generic row (exact and expression folds) and `mismatch_inplace`
(the in-place fold); kit-only, no pcrec byte moved.
§R4.7 holds the kit's contract after G2, the kit session's rulings on
G2's F1-F3 and Q-G2-1..17. This file is the working agreement for the
subtree.

**Status: R4a, the code skeleton** (lane memfnskel; integration.md §22).
`include/memfn.h`, the composer, the generic scalar row, K1's reference
functions and an empty `src/options.def` are built into `libpcrec.a` by
pcrec's Makefile (`KITSRCS`/`KITFLAGS`), and `--list-axes` prints the
registry as its `memfn` section. pcrec CALLS nothing else: no emitter
renders through the kit, so no artifact byte moved. C15/C16 hold the link
(`tests/memfn/run_link_checks.sh`). The site manifest + C17 and G2's first
tests are R4a's other lanes. G2 (`tests/`, D27-blinded lane memfng2)
found F1-F3; lane memfnfix fixed them, made the contract's edge refuse
loudly (§R4.7), and wired G2 into make: `make test-memfn-g2` (the quick
tier, a `make test` section) and `make test-memfn-g2-full` (opt-in).

## What the kit is

pcrec describes a search SITE (`mf_site`: an operation over a predicate,
pcrec's proven facts — span bounds, anchoring, density hints — and text
hooks) and the kit returns the C text for that site (D146). The kit owns
EVERY choice inside the site: scalar forms, SWAR, libc calls, loop-free
short-span forms, ISA arms. pcrec does no cost comparison and carries no
architecture knowledge. When pcrec needs compound work ("this check
followed by this check", a scan fused with a verify or a handoff), the
kit provides it.

Stand-alone, the kit is also a product: bespoke high-speed memory
functions (K3: a CLI and reference functions). pcrec's requests come
first; K3 second.

## The layers (D147) — binding on every kit change

- **ONE SIMD switch** (D147 addenda 6-7): `-fno-memfn-simd` /
  `-fmemfn-simd`, axis `memfn-simd`, OFF BY DEFAULT until the SIMD hold
  (D91/D119) lifts. Turning it on by default is its own ruled event.
  - **OFF:** the artifact is PORTABLE C (plain C, SWAR on ordinary
    integers, libc calls, loop-free forms) and runs on any target.
  - **ON:** the artifact is hardware-optimized for a specific CPU and
    MAY NOT EXECUTE ELSEWHERE.
  - What sits inside ON is THIS KIT's per-site choice: forms, ISA
    levels, a run-time CASCADE between levels (K-6: only where it beats
    the single-level form, and named with its dispatch cost:
    `__builtin_cpu_supports` is 0.4-0.6 ns on Linux x86 and wrong on
    Darwin), and the fallback.
  - pcrec sends one bit (`MF_P_PORTABLE_ONLY` when the switch is off)
    and nothing else. There is no `portable`/`native`/`baseline`
    profile and no `--isa=` axis.
- **The scalar layer** is pcrec's algorithm (what is searched, the plan,
  handoffs, fused predicates) plus the kit's SCALAR ARMS: every form the
  kit renders with the switch OFF. SWAR and libc calls are scalar layer
  (Q50). The scalar arms are LIVE, improvable code, forever. A
  scalar-layer change is accepted on SIMD-OFF measurements.
- **The SIMD layer** is what the kit adds with the switch ON. It must
  beat the CURRENT best scalar layer on its own merits, never an old
  or frozen scalar. A scalar improvement re-opens the comparison: the
  SIMD form is re-measured against it.
- **Every acceptance reading** for a change that touches searching
  reports BOTH layers: SIMD-off and SIMD-on.
- **Kit forms obey D149** (integration.md §8.6 K-7): every unroll
  width, block size and cut-over is measured, derived or left to the
  compiler, or labelled in place as `UNMEASURED DEFAULT:`.
- **No frozen baseline.** pcrec's pre-migration text is a per-migration-
  step byte-identity COMPARATOR only (the shadow comparator and the
  movers-by-ID gate at that step). It is not a permanent arm, not the
  SIMD-off arm, and it never pins the scalar layer.
- **Every kit change that moves bytes carries its own deny** (D144 item
  4): a row of the kit's OWN option registry, `src/options.def`, reached
  as `--memfn=no-NAME`; that deny is the change's alpha OFF arm. See
  "The kit's option namespace" below.
- Kit work and pcrec scalar work proceed in parallel.

## The kit's option namespace (D147 addendum 9, Q47 refined)

- pcrec has exactly ONE axis for the kit: `-fno-memfn-simd` /
  `-fmemfn-simd`. Every per-form switch is the KIT'S: `--memfn=<opt>
  [,<opt>…]`, a string pcrec carries and passes through UNINTERPRETED
  (`mf_site.opts`). `no-NAME` denies row NAME; a bare `NAME` forces it,
  for rows declared `MF_OPT_PAIR`. The kit validates the string
  (`mf_opts_check`) and its refusal text is shown unchanged.
- The registry is `src/options.def`, an X-macro: `MF_OPT(name, kind,
  budget, layer, doc)`. `name` is kit-owned and arch-blind; `kind` is
  `MF_OPT_DENY` or `MF_OPT_PAIR`; `budget` is `MF_B_SCAN`/`MF_B_LOOP`/
  `MF_B_ANY` (D91); `layer` is `MF_L_SCALAR` or `MF_L_SIMD` (which
  acceptance reading owns the row; a SIMD row is inert at
  `-fno-memfn-simd`). The accessor is `mf_options(size_t *n)`. What is
  printed and what is parsed are one table.
- **A kit change that moves a byte adds its row in the same commit.**
  The row is that change's OFF arm.
- `pcrec --list-axes` prints pcrec's axes, then a `memfn` section
  (`table_contract.md` §Sections) read from `mf_options()`. It is the
  ONE enumeration point for `test-axes`, the identity gates and the
  registry check.
- **The independent control** is a floor on that section's member count,
  pinned as a literal in `docs/spec/` (it shares no source with
  `options.def`). Raise it in the change that adds a row. It is born
  with the first row (R4d), so the check is UNREACHED until then.

## The boundary with pcrec

| pcrec owns | the kit owns |
|---|---|
| WHICH sites are delegated (`DELEG_SITES`, by semantic operation, never by cost) | the code for each delegated site |
| the predicate's facts (PATFACTS' territory: offsets, byte sets, runs, spans, anchoring) and density hints | the plan over those facts (from M5), the form, the fallback |
| the SIMD switch's state (`-fmemfn-simd` or not) | what SIMD-on means in code: forms, levels, cascades, fallback |
| the CHECKED SITE MANIFEST (`tests/memfn/site_manifest.tsv`, C17): every emitted search site `delegated` or `pending` | the delegated sites' code; the `MEMFN_FORMS`/`MEMFN_LIBC` stamp values for them |
| the hooks' text (subject, bounds, `on_miss`, escapers, table names) | everything between the hooks |
| the guard: pcrec's own timing, kit change on vs its deny, both layers | its own exhaustive tests (G2) and its own timed control (K-5) |

pcrec's sources reach the kit only through `memfn/include/memfn.h`. The
kit links nothing from `src/`, `cli/` or `lib/`. Generated artifacts
never depend on the kit: what reaches them is TEXT, so self-containment
holds.

**Every search site migrates here** (Q42 reversed: completeness, a
ruled D77 exception). Each step is zero-mover. The memchr ratchet
(C12) ends at 0 outside the kit, and C17 at 0 pending. A kit change
that MOVES bytes still needs its measured trigger and G1 alpha at both
layers.

**The stamps** (Q39, addenda 3 and 6). Both go on every artifact:
- `<PREFIX>_MEMFN_FORMS` is `none` iff the artifact is identical to its
  SIMD-off compile, else the forms used, with carried levels;
- `<PREFIX>_MEMFN_LIBC` lists the libc functions the search code calls
  (spelling: Q53).

Neither carries a kit version. Both are born in R4a′.

**A kit byte move is a pcrec abi event, in the SAME commit.** A kit
change that moves any byte pcrec emits lands with pcrec's abi bump, its
re-pins (readers found by grep, D76/D94), its stamp values, its
`docs/spec/` hunk where caller-observable (D80) and its G1 alpha (both
layers). That atomicity is why the kit is in-tree (Q36); a split commit
is a delivery failure. After a migration step, edits to a migrated
pcrec emitter are kit work here, not edits under `src/gen/`.

## Symbols, licence, provenance

- Every external symbol goes through `MF_NS(name)` → `pcrec_mf_name`
  in-tree (`mf_name` in an extracted build). Internal functions are
  `static`. libpcrec exports only `pcrec_`-prefixed names (C15).
- Licence: **0BSD** for the kit's own text (`LICENSE`, D145's list).
  Text translated from Rust `memchr` takes that crate's `Unlicense` arm;
  MIT/BSD/Apache text is ideas-only. Every source file whose text can
  reach an artifact carries an SPDX line and a provenance header (C16);
  `PROVENANCE.md` (born at R4a) tabulates file → source → licence →
  what derives from it.

## Process

- **Requests: two files, one writer each (D78).**
  `docs/requests.md` — pcrec manager → kit; the ONLY writer is the pcrec
  manager, a single-file `[requests]` commit on main. `docs/responses.md`
  — kit → pcrec manager; the ONLY writer is the kit session, a single-
  file `[responses]` commit on the kit's branch, merged by the manager.
  A request is on main before the kit lane that serves it is briefed.
- **Journal:** `docs/journal.md`, the kit's own append-only dated record.
  pcrec's `docs/dev/dev_journal.md` gets a line when a kit change merges.
- **Session:** a dedicated long-lived kit session may work this subtree,
  in its OWN worktree under `worktrees/`, never merging to main itself
  (`docs/wake.md` is its orientation file). It runs as
  `/pcrec-memfn-manager` (`.claude/skills/pcrec-memfn-manager/SKILL.md`):
  the kit's manager, directing its own lanes off its own branch.
- Kit lanes are ordinary pcrec lanes: `docs/dev/lanes/BOILERPLATE.md`,
  the box rules, one heavy suite at a time, Linux verdicts only (D144
  addendum 1; the Mac is directional).

## Standing design questions (docs/design/CLAUDE.md), for every kit design

1. **Measurement regime** — every kit measurement names its regime
   (throughput vs per-call, hit-dense vs hit-sparse, compiler, box); a
   choice must hold in every regime its site can be in (K-1). Verdicts
   are Linux, `taskset`-pinned, calibrated loops, absolute deltas against
   a floor (D144 addendum 1); both layers reported (D147).
2. **Independent control** — G1 is pcrec's timing of the change against
   its own deny, population from a pcrec-side artifact diff (never the
   kit's `moved`); G2 checks against the scalar byte loop and a GENERATED
   predicate space, never another output of the kit's generator.
3. **What moves when data is regenerated** — the kit's measured data
   (`data/*` with its `generate.py`, born when first needed) moves
   emitted bytes: every regeneration that moves a byte is a pcrec abi
   event (integration.md §21.3).

## Layout

- `README.md` — the stand-alone pitch, licence, status.
- `LICENSE` — 0BSD.
- `docs/` — the ledger pair, the journal, the session wake template
  (its own CLAUDE.md).
- `PROVENANCE.md` — file → source → licence → what derives from it, one
  row per file under `include/` and `src/` (C16 compares the two).
- `include/` — `memfn.h`, the one header pcrec includes (R4a).
- `src/` — K2 composer, the generic scalar row, K1 reference functions,
  `options.def` (born empty) and its accessor/parser (R4a); the scalar
  arms arrive with the migration steps.
- `tests/` — G2, the kit's own tests (R4a's blinded lane).

## Slot runs of `make test` ([TT-JTUNE], 2026-10-08)
The kit's slot runs of the full suite go through `scripts/perfrun --label NAME
-- LOGFILE` instead of a raw `make -k -jN -Otarget test` (it rotates the
parallelism shape, records the timing in the shared ledger, and returns make's
rc unchanged). Read a red with its `LOGFILE.perfrun` note first: K44-ONLY and
LOAD-SUSPECT reds are re-run solo per section, not charged to the kit. See
docs/dev/lanes/BOILERPLATE.md and docs/dev/ttune_measurement.md.
