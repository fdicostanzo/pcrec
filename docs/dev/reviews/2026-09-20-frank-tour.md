# Frank's guided tour of the refactored tree — the list

Started 2026-09-20 (seventy-second session), the day after the code-review
refactor closed. Frank reads source files and asks questions; items land here
only when both agree. His lens: **readability, clarity, maintainability** —
not functionality or methodology. Each item names the file, the observation,
the agreed shape, and the proof that it changed nothing. Items are chartered
as lanes from here (plan rows cite `[TOUR-n]`).

## [TOUR-1] src/gen/emit_vm.c — pcrec_emit_vm reads at three altitudes at once

**Observation (Frank):** the function creates a `Vm` and spends a long
stretch setting it up before any emission; "could those activities be cleanly
put into an init_vm type function?" — then, applying the consistent-altitude
idiom: if it starts with an init and a plan, the last section should be a
subfunction too.

**Measured at 11ff5f51:** the function spans 9388-12196; 1,106 code lines
under 1,644 comment lines. The setup phase (9449-9660) is 44 code lines
under 162 comment lines and sets ~12 fields (cx/b/p, ngroups + pend_of via
the backreference marks, tracing, unroll_k, mrl, mrl_win, fmin, up, cg /
has_calls / nregion); nothing in it depends on anything computed later; its
only shared local is `GenNames g` (pointer parameter).

**Agreed shape, three parts:**
1. `vm_init(Vm *v, Ctx *cx, Ast *root, GenNames *g)` — 9449-9660.
2. Finish the plan extraction — 9661-9942 (slot counts, per-region passes,
   the totals, the caller-buffer sizing surface and fast-tier capacities);
   `vm_plan_capacities` (wave 2) already owns the capacity policy.
3. The emission tail as one function per SECTION OF THE ARTIFACT, in the
   artifact's order: prologue (9943-9974), `vm_emit_stamps` (9975-10620,
   ~650 lines, the most self-contained — start here), `vm_emit_storage`
   (10767-11115: storage types, sentinels, work charge, MRL forms, the
   PUSH/CALL macros), `vm_emit_search_body` (11116-11875: wiring, resets,
   the walk, fail label, the search entry with guards and retry advance),
   `vm_emit_entries` (11876-12121), epilogue (12122-12196: residual, info,
   listing, size publications). pcrec_emit_vm becomes eight or nine calls.

**Design question the lane answers, not assumes:** which locals cross the
seams (`tiered`, `fwd_entries`, `ncaps`, `bufs`, `mguard`, ...). Each moves
either into `Vm` as a PLANNED FACT or into a small per-phase struct the
earlier phase returns (the `VmCaps` precedent). `Vm` must not become a bag of
every local.

**And the essays:** the setup's 162 comment lines are mostly history (the
DD-14.EMPTY root-width comment alone is 55 lines, half of it a correction of
a correction). coding_guide.md §4.2: comments carry the invariant and the
why-not-the-alternative; HISTORY goes to docs with a pointer. Prune each
essay to its invariant + a pointer to the decision/plan row it narrates. This
is what actually shortens the file.

**Proof:** `scripts/emit_sweep.py --ref <branch point>` byte-identical on all
five streams (as every wave 2 step); anchors 285/285 re-aimed per row; not an
abi event. Tier: opus (engine code).
