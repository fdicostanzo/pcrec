# memfn/ — pcrec-memory-functions, the in-tree kit

`[MEMFN]` (docs/dev/plan.md). Frank's rulings 2026-10-05: D146 (the kit
is a DELEGATE, not a price market), D147 (layers), Q35/Q36 (the
integration.md §8+§14 contract is the design of record; the kit lives
IN-TREE here). The design of record is `docs/design/memfn/integration.md`
(rev 4.2); this file is the working agreement for the subtree.

**Status: no code yet.** This directory is the skeleton set up by lane
memfnsetup. Nothing here is built, linked or tested by pcrec's `make`.
The first code (`memfn.h`, the generic scalar row, K1 reference
functions, the Makefile wiring) lands with R4a (integration.md §22),
not before it (D77: build under measurement).

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

- **The scalar layer** is pcrec's algorithm (what is searched, the plan,
  handoffs, fused predicates) plus the kit's SCALAR ARMS: every form the
  kit renders when `memfn-native` is not taken (portable text: scalar,
  SWAR, libc, loop-free). The scalar arms are LIVE, improvable code,
  forever. A scalar-layer change is accepted on SIMD-OFF measurements.
- **The SIMD layer** is the kit's native (ISA) arms. It must beat the
  CURRENT best scalar layer on its own merits — never an old or frozen
  scalar. A scalar improvement re-opens the comparison: the SIMD form is
  re-measured against it.
- **Every acceptance reading** for a change that touches searching
  reports BOTH layers: SIMD-off and SIMD-on.
- **No frozen baseline.** pcrec's pre-migration text is a per-migration-
  step byte-identity COMPARATOR only (the shadow comparator and the
  movers-by-ID gate at that step). It is not a permanent arm, not the
  SIMD-off arm, and it never pins the scalar layer.
- **Every kit change that moves bytes carries its own deny** (D144 item
  4), published by the kit's switch table as `--memfn-deny=NAME`; that
  deny is the change's alpha OFF arm.
- Kit work and pcrec scalar work proceed in parallel.

## The boundary with pcrec

| pcrec owns | the kit owns |
|---|---|
| WHICH sites are delegated (`DELEG_SITES`, by semantic operation, never by cost) | the code for each delegated site |
| the predicate's facts (PATFACTS' territory: offsets, byte sets, runs, spans, anchoring) and density hints | the plan over those facts (from M5), the form, the fallback |
| the profile request (`memfn-native` taken or not) | what `portable` and `native` mean in code |
| the hooks' text (subject, bounds, `on_miss`, escapers, table names) | everything between the hooks |
| the guard: pcrec's own timing, kit change on vs its deny, both layers | its own exhaustive tests (G2) and its own timed control (K-5) |

pcrec's sources reach the kit only through `memfn/include/memfn.h`. The
kit links nothing from `src/`, `cli/` or `lib/`. Generated artifacts
never depend on the kit: what reaches them is TEXT, so self-containment
holds.

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
  (`docs/wake.md` is its orientation file).
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
- `include/` — `memfn.h`, the one header pcrec includes (planned, R4a).
- `src/` — K1 primitives, K2 composer, the scalar arms (planned).
- `tests/` — G2, the kit's own tests (planned).
