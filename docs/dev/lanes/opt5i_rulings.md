# opt5i rulings (manager → lane; poll at each tick; uncommitted — never add to git)

R1 (2026-09-02 ~15:2x EDT, Frank: "Ship now"): ADD ONE VM-ROUTE STAMP TO
YOUR abi 16 EVENT — `RX_VM_FRAMELESS` (0/1), exactly as drafted in
docs/dev/optvmfl_step0.md §4.2 on main (merged 6fa1c66; read §4.1-§4.4):
a §6.3 (b)-family macro, VM route only, UNCONDITIONAL (never absent on a
VM or hybrid artifact; not defined on a pure-DFA artifact), its value
read from `has_push` at the stamp's own definition site in emit_vm.c
(the same `v.emitted_push || v.has_linked_calls` the fail label reads —
one derivation, two readers of the SAME bool; do NOT recompute from
`v.npush`), NO rx_info mirror (RX_DFA_TABLE precedent, §4.1). Land with
it: the docs/spec/match_api.md §6.3 entry (its IFF: "1 iff the artifact's
VM program emits no RX_PUSH site and no linked call, i.e. the fail label
has no pop-and-resume dispatch"), the tuning.md line if §4.2 names one,
a tests/codegen structural check (every VM/hybrid artifact defines it;
value 1 ⇔ the artifact text contains no `goto *`; value 0 ⇔ it does —
over the corpus + `-fprefilter` force axis), and it rides your abi 15→16
bump and (B) re-pin — NO separate bump. Reason it rides yours: a second
abi event right behind yours would cost a second union battery for one
macro. Record it in your report's acceptance table as its own row. If
this conflicts with anything in your charter, say so in the log and do
the stamp LAST.

R2 (~15:3x EDT, box load): the bench runs three `make check` bursts (10-15
min CPU each) and serial scratch compiles over the next ~2-3 h. If a
`make test` compile cell reds under load, re-run that cell SOLO before
believing it — K44 (docs/dev/known_issues.md) is the standing disposition
for the load-marginal cell; do not diagnose it as your change until the
solo run agrees. Check `uptime` before your test-axes run and prefer a
moment with load < 2.
