# K49 fix lane — WIP diagnosis (in progress)

Reproduced. VM: emitted `rx_search_run`'s `attempt_position++` (src/gen/emit_vm.c:11201).
DFA: `\B` under -e utf8 over "a\xce\xb1" from startpos 0 reports (2,2), mid-character,
with NO retry loop in the artifact — the start-anywhere self-loop is byte-granular.
Both engines answer (2,2); fixing only the VM would create a cross-engine divergence.
