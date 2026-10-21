# b4prep item 3: main's walk against the slot's walk (grid2read §9 item 2, r17b_prime §3.1a item 3)

Question: is the slot's `walk` arm (the kit compiler under `--memfn=no-pf-terms-mask`, abi 77) the same
text as MAIN's walk (the default compile of a tree with no kit code, abi 81)? Compile-only.

Method: `walkcmp.sh` (here) emits grid2's ten compiler-emitted cells (dig, bounded, dfa-hat, hex-run, word-eq, quad,
wcls, c020, c001, c110; patterns and `--features` from grid2/provcheck.py) with `build/pcrec` of the b4prep worktree
(main plus kit docs; `make -j4`, no kit code change, so its default compile is main's walk) and compares each
`art.c` with `memfn-slot/grid2/art/<cell>/deny/art.c`, which provcheck proved equal to `bin/<cell>/walk/art.c`.
Result table: `walkcmp.tsv`.

| result | cells |
|---|---|
| walk arm == deny artifact (byte copy) | 10 of 10 |
| raw byte-identical | 0 of 10 |
| identical once the abi number is masked | 0 of 10 |
| identical once the abi number AND one new stamp line are accounted for | **10 of 10** |

The whole difference, on every cell, is three lines of `art.c`: `.abi = 81` vs `77` (`rx_info.abi`, plus the
`(abi N)` comment, masked), and one added line `#define RX_COMPOUND "none"` (a stamp macro that landed with the
compound artifact after abi 77; nothing in the file reads it: `grep -c RX_COMPOUND` is 1, the define). The table
walk, the `__next_candidate`-free scan, the `[256]` tables and every executable line are the same bytes. `art.h`
differs only in the `PCREC_RX_ABI_H` value and the two abi-error lines that quote it.

Verdict: **identical in the emitted walk; differs only in the abi stamp and one unread stamp macro.** B4's G1 can read
the slot's walk as main's walk for these ten cells. A different abi number changes no timed instruction.

Not compared: the `o-*` one-byte cells (their `walk` arm is mkvar2-built, with `G2_TICK`/a one-byte table, not a
compiler emission) and the walk inside the dispatch twins. Those are not B4's baseline.
