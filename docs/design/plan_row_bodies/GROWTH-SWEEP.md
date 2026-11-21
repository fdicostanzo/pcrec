# [GROWTH-SWEEP] row body

Long-form record for plan.md row [GROWTH-SWEEP]; the row carries the pointer.

## Rulings

- RULING growth-compile-cells (Frank 2026-11-21, his words, answering review r73 VERDICT-1): "the purpose of that section is to test limits and look for crashes. If it compiles, it's not testing limits. Also, if it's failing with a error then later it's not and compiling then that should be alerted as it's not testing limits any more". So every cell is sized past a named limit and a compile is a FAIL (the 742 compile cells are re-sized, never kept as crash-only controls), and a cell that used to refuse and now compiles goes red. MANAGER'S READING (for the owner to check): the 33 depth@250 cells stay, each as the compiling half of a 250/251 pair that tests the depth limit's exact edge, and the pair goes red if 251 compiles.
