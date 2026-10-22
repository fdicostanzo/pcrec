# tests/subst/d27/api

Part of the D27 blinded corpus; see ../CLAUDE.md for the provenance, the
adoption changes and the file list.

substb2: the drivers run the R4 interface; `t.h` carries the spec's recipes
(`sub_all`, `sub_limit`, `mkmap`) and defines `PCREC_SUPPORT_IMPLEMENTATION`;
`build.sh` emits `support.h` and compiles no artifact with `--unset=`.
