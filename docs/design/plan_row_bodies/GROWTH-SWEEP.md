# [GROWTH-SWEEP] row body

Long-form record for plan.md row [GROWTH-SWEEP]; the row carries the pointer.

## Rulings

- RULING growth-compile-cells (Frank 2026-11-21, his words, answering review r73 VERDICT-1): "the purpose of that section is to test limits and look for crashes. If it compiles, it's not testing limits. Also, if it's failing with a error then later it's not and compiling then that should be alerted as it's not testing limits any more". So every cell is sized past a named limit and a compile is a FAIL (the 742 compile cells are re-sized, never kept as crash-only controls), and a cell that used to refuse and now compiles goes red. MANAGER'S READING (for the owner to check): the 33 depth@250 cells stay, each as the compiling half of a 250/251 pair that tests the depth limit's exact edge, and the pair goes red if 251 compiles.
- DISCUSSION (Frank 2026-11-21, his words, after the ruling above): "consider: have the test go past the limit as the stability test then have a test go just before and call it a limit test with different criteria". The manager's proposed shape (open, slug limit-test-criteria): pairs across a limit that has a stated value; the stability cell (past it) PASSES on a clean refusal by that limit; the limit cell (just before it) PASSES only if it compiles and its matcher runs; either cell crossing over (the stability cell compiling, the limit cell refusing) is red. Memory-cap cells have no sharp "just before" and stay stability-only. Not yet a ruling.
