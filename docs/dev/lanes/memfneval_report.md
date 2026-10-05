# Lane memfneval: report

[MEMFN] R1c. This lane (opus) did design only. It worked in worktree
`worktrees/memfneval` on branch `lane/memfneval`, from main e2f57982.
Deliverable: `docs/design/memfn/isa_evaluation.md`.

## What it is

Frank asked, on 2026-10-04, for "the best approach to arch selection crossed
with the use case", and suggested that the parked selection utility (the
[V-E]/[ART-MGR] organizer) could pick among artifacts by arch.

The note's §1 is a matrix. Its six approaches:
- A0 baseline;
- A1 a per-call test;
- A2 a library's dispatch-once;
- A3 a declared-ISA artifact;
- A4 a hybrid;
- A5 (d), multi-artifact selection.

Its six use cases:
- U1 a library call;
- U2a/U2b a prefilter kernel and an in-loop kernel;
- U3 unknown CPUs;
- U4 a known box;
- U5 many artifacts;
- U6 a `.so` plugin.

Every cell records legality, cost, failure mode, complexity and size. Costs
cite memfnisa's Mac numbers or are marked OWED with their U-number.

§2 designs (d):
- the pick sites P1-P4;
- the stamp, which needs only `isa` and `isa_family`, with the variant group
  held catalog-side;
- the cost of N variants;
- how it composes with the clean-fail check;
- hazards H-a to H-g;
- dependencies.

§3 is the verdict, a deployment-level first-match table, and the Linux
measurements L-1 to L-6. §4 holds Q7-Q11. §5 is the [ART-MGR] cross-note,
ready to paste.

## Verdict, in one paragraph

One mechanism wins. The unit is the declared-ISA artifact: one level,
stamped, every kernel inlined, no dispatch inside. The choice between
levels is made above it, by one of three:
- the caller (a known box);
- the L1 catalog (a variant group, a pure `pick(group, level)` first-match,
  the caller holding the result);
- the L2 loader (it picks from the sidecar before `dlopen`).

A memfn library keeps its own dispatch. The per-call hybrid is HELD as the
size-dialed alternative for unknown CPUs, pending U-9. Per-call tests are
dominated everywhere they are legal.

## Findings worth carrying

- **The ISA marker breaks a static (d) catalog.** The marker is OR-merged
  across the linked object (BELIEVED), so a v3 variant carrying it makes the
  whole program refuse to load on v1. Under L2 the marker is per-`.so`
  instead, a second fence.
- **One question is not in `linux_run.sh` or `isanote.sh`.** Does a plain
  `-march=x86-64-v3` object get the marker unasked on ubuntubudu's
  toolchain? (L-4)
- **The cheapest decisive measurement is also missing from `linux_run.sh`.**
  It is L-2: today's artifacts compiled at `-march=x86-64-v3` against the
  baseline, timed on the bench's own cells. It is the D77 trigger for
  building the stamp before any memfn kernel exists.
- **K79 and K80 are both fixed (abi 54), and both were (d)'s
  prerequisites.** K79's canonical placeholder prefix makes variants differ
  only in what `--isa` moves.

## Validation

This was design only, so no build or test was run. No emitted byte, `src/`
file or spec file changed. CLAUDE.md index entries were updated in
`docs/design/memfn/` and `docs/design/`.

## Owed

- The L-2 brief (manager or pcrecdev2).
- An `isanote.sh` row for a plain `-march=x86-64-v3` object (L-4), to be
  added before or after the pending `linux_run.sh`. This lane did not edit
  memfnisa's script.
- Frank's rulings on Q7-Q11.
