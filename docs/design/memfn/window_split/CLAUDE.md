# docs/design/memfn/window_split/ — the window family split's census instruments

Instruments of `../window_split.md` (lane wsplitd, 2026-11-24). Read-only over a tree's
`memfn/src`; python3 only, run with `-I`; never built or run by `make`. Every count the note
quotes names the command that produced it from these files at T a0f13ad83.

- `ents.py FILE.c` — the top-level entities of a C file (kind, name, lines, static), comments and
  string literals blanked first. Imported by the others.
- `census.py SRC SPEC [-v] [--calls|--bodies]` — for a cut SPEC: the names that cross a file
  boundary (statics, types/macros/enumerators, kit.h names), each new file's public names, the
  name cost per boundary, and the file cycles.
- `kitgraph.py SRC SPEC [FILE..]` — the kit's whole file call graph after the cut (function bodies
  only) and its cycles; `DROP="a.c b.c"` removes files; FILE args print their edges.
- `bucket.py SPEC` — stdin `row<TAB>line` (window.c lines, e.g. anchor_map.py output) to new files.
- `home.py SRC SPEC` — stdin names (window.c/presence.c definitions) to new files.
- `plants.py ROOT` — every window.c/presence.c G2 plant and its FROM text's line (0 = stale).
- `cut.spec` — the proposed cut as a pure move (`NEWFILE <- SRCFILE a-b ...`, `ent:NAME`).
