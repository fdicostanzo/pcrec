# CRITIC FIDELITY (opus): r76 memfn-bsu3

Read /var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu3/COMMON.md first. Your lens dir: .../crit-memfn-bsu3/fidelity/
Findings file (pre-created, APPEND only): .../crit-memfn-bsu3/fidelity.md. Deliver file: .../fidelity_deliver.txt.

## Your ONE question
Is the shipped text the timed text (G-2, §6 F2), and what does the new SIMD-on path do worse or
differently than the path it replaces (BASE's SIMD-on artifact, whose V selector calls `__body`)?
- sub-part (a) F2 re-run: the routed cells of 710's grid (§6: 6 window classes x 11 k in 16..1000 and
  4 scan classes x 4 k in 24..64, from confirm.py `CLASSES`, `SITE_EXPECT`, `KS_OLD`, `KS_NEW`; the
  timed sources are `R/710/work/src/<class><k>.avx2-loop.c`). Emit the SHIPPED artifact
  (`-fmemfn-simd=x86-64-v3 --window-search-width=4095`, as §6 says), `gcc -std=gnu11 -O2 -w -c`,
  `objdump -d` of `rx_search` vs the timed file's `rxa_search`, addresses and symbol names
  normalized (write your normalizer down and show it holds on a known-identical pair). Count the
  routed set yourself from the shipped build and report any cell where your count disagrees with 82.
- sub-part (b) consumer-flag columns: for a representative subset (at least the 3 real bench sites
  `[0-9a-f]{32}`, `\b[0-9a-f]{32}\b`, `\d{32}`, plus one cell per class at B = 16 and B = 32),
  shipped-vs-timed AND shipped-vs-BASE machine code under gcc -O2, gcc -O3, gcc -Os, clang -O2 and gcc
  -O2 -march=native; also gcc -O0 (does every V function inline away; what does -O0 do with
  always_inline inside the `#pragma GCC target` region, and with clang's `pragma clang attribute`?).
  Report a table: cell x flag -> IDENTICAL / DIFFERS (diff size, instruction count delta in rx_search,
  any call left un-inlined, any spill or reload in the hot loop). A DIFFERS is not a defect by
  itself: say what differs and whether 710's timing could still speak for it.
Speed: no timing runs (the box has other jobs); static instruction counts and shapes only. If you want
one dynamic count, `perf stat -e instructions:u` pinned `taskset -c 7`, at most 10 runs total.

Compile cap: 500 compiles. State your matrix product before running it. Do not plant anything.
