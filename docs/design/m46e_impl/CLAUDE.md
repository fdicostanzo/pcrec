# docs/design/m46e_impl/ — the [M4.6e] lane: RX_HYBRID_MIN + trie-factored VM switch

[M4.6e]'s two measure-then-implement items, the last substep before M4.6
closes (engine_m4.md §12 ASK-6 and §2.2 item 4 / §6.4's last row). Kept
separate from `m46a_impl/` (budget calibration) and `k24bisect_impl/` (the
`noclone` fix) for the same never-confuse-the-lanes reason those two are
separate directories: this lane measures two DIFFERENT selection questions,
neither of which is a budget default or a bisect.

**Both items are MEASURED-NO. Neither was built.** "Measured, decided NO,
numbers archived" is the brief's own stated fully-successful outcome for
this lane, and both dispositions follow directly from the archived data —
see `out/` for the raw sweeps and `engine_m4.md`'s own annotations (ASK-6,
§2.2 item 4, §6.4's status table) for the reasoning applied in place, which
this file summarizes rather than duplicates.

## Item 1 — RX_HYBRID_MIN (ASK-6)

**The design's question**: is there a subject length `n` below which a
runtime `if (n < RX_HYBRID_MIN)` branch in `<prefix>_search` (the arm at
src/gen/emit_vm.c ~4728-4744 that runs the DFA prefilter before the VM)
should skip straight to VM-only, because two DFA passes cost more than they
save on a short subject? §6.2(b)'s prediction: yes, "low hundreds of bytes",
targeting bench case (i)'s 60-byte regime.

**The measurement's answer**: length is the wrong variable. `probes/hybrid_min.py`
sweeps match OFFSET at fixed `n` across three representative capture-bearing
patterns (case (i)'s own `a(b|c)+d`, case (j)'s own `([01]*)1([01]{8})`, and
a short two-group anchor shape) and separately confirms length-invariance at
fixed offset. Finding: hybrid's ns/call is flat in `n` (the two DFA passes'
fixed call overhead plus a memchr-speed skip, both cheap at these scales);
VM-only's ns/call is flat in `n` too and instead grows with OFFSET (one
computed-goto function call per candidate start position in the naive
`start++` retry loop — not a vectorized skip). The crossover sits at
8-12 bytes of offset for two of the three shapes and never arrives at all
for the third (case (j)'s own pattern — hybrid wins from offset 0). Bench
case (i)'s ACTUAL buffer sits at offset 20, past the crossover: hybrid
measures **65% faster** than VM-only on it, three-run reproducible. A
length-only branch cannot target offset — it would either miss the
win-region entirely (offset-0 matches lose to VM-only identically at n=60
and n=4096) or, set generously enough to catch case (i)'s length, regress
the exact case it exists to protect.

**Disposition**: not built. The seam engine_m4.md §6.2(b) designed stays
exactly as-is — unimplemented, and correctly so, since implementing it on
the designed variable (length) would be a regression generator, not an
optimization. A future lane could revisit an OFFSET-gated version (e.g.
"try VM-only for the first K positions, fall back to the DFA prefilter"),
but that is new design outside this ASK's scope and this lane's mandate.

Files: `probes/hybrid_min.py` (the sweep + methodology note in its own
docstring, including why an MRL-style branch placebo has no referent here —
hybrid and VM-only are two entirely different emitted functions, not two
branches through one), `out/hybrid_min_sweep.txt` (three independent pinned
runs plus the length-invariance table, taskset-pinned, best-of-9, D35
stable name).

## Item 2 — the trie-factored VM alternation switch

**The design's question**: should `vm_alt` (src/gen/emit_vm.c:1783), which
emits an N-branch alternation as a chain of N-1 push+goto tried in
preference order, instead emit a first-byte switch with NO pushes where
branches are pairwise-disjoint on their first byte — the VM-side analog of
the trie factoring `src/ir/nfa.c`'s M2.8 machinery already does for the
DFA/NFA construction path (D9)?

**The measurement's answer**: `probes/trie_switch.py` does two things, per
the brief's bar. First, a static corpus survey (the same eligibility rule
`nfa.c`'s `trie_key()` checks — an A_CAT chain of A_CLASS leaves, approximated
here on literal pattern text): of 1146 corpus pattern lines, 347 (30%) are
capture-bearing (VM-forced, D42.1) and so could even reach `vm_alt`'s chain;
of those, only 49 contain a plain top-level alternation, and only 22 (6.34%
of capture-bearing patterns, 1.92% of the whole corpus) are heuristically
first-byte-disjoint. Neither shipped capture-bearing bench shape (case (j);
case (c)'s own alternation is pinned `--no-captures` and never reaches
`vm_alt` at all) is a hit. Second, a direct measurement of the chain's own
cost, isolated by holding the subject fixed and moving which branch matches:
a 5-way disjoint word alternation costs 18% more at the worst branch
position than the best (about 23 ns of a ~130 ns/call baseline); a 3-way
HTTP-method-style dispatch costs 3-4% more. Real, reproducible across three
independent runs — and narrow.

**Disposition**: not built, on D18 ("an axis must earn itself"). A VM-level
trie switch would be a genuinely new emitter analysis with the same
obligations `src/opt/CLAUDE.md` already documents for every other
strategy-selection axis in this file (a D46 stamp+force pair, a permanent
sabotage-matrix row, interaction with the MRL/possessify/revdet walks that
also visit `A_ALT` nodes) — a real build cost, against a shape that is 6% of
even the adversarial correctness corpus and present in neither of the two
bench floors DD-9 anchors. Revisit under the same evidence gate D50 used to
re-home exact islands to [ENG-ISL] (engine_m4.md §6.3): when [BENCH-1] or
[ENG-PGO] surfaces a real disjoint-alternation-plus-capture customer, not
before.

Files: `probes/trie_switch.py`, `out/trie_switch_sweep.txt` (corpus survey
plus three independent pinned branch-position runs).

## Methodology note (both items)

Both probes reuse `tests/bench/bdriver.c` verbatim (it already is "call
`rx_search` N times on a fixed buffer, time the loop with
`clock_gettime`" — no new timing tool was written) against `pcrec`-generated
artifacts built with existing, already-shipped flags
(`-fno-prefilter`/`PCREC_NO_PREFILTER` from [M4.6f] for item 1; default
build for item 2's branch-position sweep, since the question there is the
chain's own internal cost, not an engine choice). Pinning: `taskset -c 3`
(checked idle via `mpstat -P ALL` before the first run, following the
poisoned-pinned-core incident recorded against [M4.6d]'s lane). Reps:
best-of-9 per timed point (minimum is least contaminated on a shared box,
the mrl_impl precedent). Reproducibility: THREE independent full-sweep
re-runs per probe, fresh processes, same core, load logged at each run's
start — item 1's crossover offset and item 2's chain-overhead percentage
both reproduce to low single-digit relative variance across all three runs
of each probe. Neither probe uses an MRL-style branch placebo; both
docstrings explain why one has no referent for these particular
comparisons (see `probes/hybrid_min.py`'s module docstring for the full
argument).

Maintenance: update this file if either item is revisited and a
different disposition is reached.
