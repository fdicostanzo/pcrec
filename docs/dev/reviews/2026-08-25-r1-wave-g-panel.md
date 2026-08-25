# 2026-08-25 r1 — [DD-14] wave G read-only critic panel (pre-merge)

Subject: lane/srG at 2219dda (26 commits on 85361cd; 43 files). Two
read-only critics (D6): critG-engine (opus; engine/codegen axis) and
critG-checks (sonnet; checks/gates/docs axis). Neither ran `make`; the
engine critic used the worktree's prebuilt binary and gcc into the
scratchpad only. Manager read: lib/pcrec.h, limits.h, compile.c, Makefile,
.gitignore, cli/main.c.

## Findings and dispositions

| # | axis | severity | finding | disposition |
|---|------|----------|---------|-------------|
| E1 | engine | BLOCKING (refusal regression) | Two computations of a splice's \|W\| disagree: `spl_nw[i]` (emit_vm.c:7305-7316, capture half only) sizes the reservation at vm_count_slots (:2436); `u.call.nsave = rgn_nw[i]` (:7448-7500) unions in reached LINKED targets' seven per-copy families; vm_splice allocates from the latter (:5845) and :5852 fires. `(?:(a{2,5}(?1)?b)((?1)c)){0}(?2)` → "splice save block overflowed (7 of 6 slots)"; compiles with `-fno-splice-calls`. Corpus: 113 artifacts SPLICED>0, 37 LINKED>0, **0 with both** — every bar structurally blind. | FIX before merge (one mechanism for the number) + oracle cells with both linkages + a population assertion ≥ N; re-anchor S177 etc. Sent to srG 01:4x. |
| E2 | engine | doc-mismatch | emit_vm.c:7068-7075 justifies the pass reorder by "possessify calls pcrec_minw" — possessify.c never does; the reorder is sound for a different reason (selection's only new read is u.call.link). | fix the argument (rider) |
| E3 | engine | wrong-diagnostic | `--emit-ir '(a){0}b'` refuses with "requests no captures. Add a capturing group" (compile.c:318-322) — retired implication; hits the specimen population. | fix message (rider) |
| E4 | engine | doc-mismatch | emit_dfa.c:805-814 comment: want_caps ⇒ VM-selected; counterexample `(?:(?<g>a)){0}(?&g)b`. Value right, reason wrong. | fix comment (rider) |
| E5 | engine | nit | dead-group predicate prunes on rmax==0 (atomic.c:702) vs vm_count_slots rmin==0&&rmax==0 (emit_vm.c:2472). | one predicate (rider) |
| C1 | checks | should-fix | run_vm_identity.sh population floor 100 predates K35; 1,660 sails through. | FIXED eafec65 (floor 2480 = ~95% of 2,610, K35 named) |
| C2 | checks | should-fix | run_specimen_identity.sh: no D45 wrapping on gcc/matcher runs. | FIXED 07552a0 (gen_cc/gen_run; `gen_breached` keys on watchdog 122..125 — a first version counted NOMATCH exit 1 as 148 breaches) |
| C3 | checks | should-fix | CLAUDE.md omissions: cli/, lib/, src/core/, tests/prefilter/. | FIXED 2219dda |
| C4 | checks | nit | elision_control counted a blank subject (44 = 4×11). | FIXED 2219dda (guard; floor 40 = 4×10) |

Refuted-and-held (recorded so the next panel does not re-run them): the
eligibility budget on five angles (ordering, lexical sites, saturation,
cycle members, drop-loop ties); the narrowed-W nesting theorem under four
constructions; backtracking into a completed splice (trailed vm_set);
atomic/possessive around the site; nfa.c exactness (150 randomized
patterns vs python `re` on hand-inlined text, 0 divergences); elision
partial-on-DFA impossible (forces_captures is whole-pattern); A==B floor
cannot pass on all-refused; named 4-pattern elision exception in both
directions; RXTFLAGS default byte-identical; sabotage anchors byte-exact;
ABI: one new public flag (bit 13), [ABI-NS] count unmoved, spec defers to
the header.

## Verdict
Both critics: merge-with-fixes. Merge waits on E1's fix commit + cells.
