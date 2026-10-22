# tests/subst/d27/lib

Part of the D27 blinded corpus; see ../CLAUDE.md for the provenance, the
adoption changes and the file list.

`lib/diff_driver.c` and `run_diff.py` drive every case through the R4 recipes
(replace-all, the §6¶4 batch cross-check, the §6¶2 per-match loop, no-gap
element calls) and emit the support unit once per run (substb2).
