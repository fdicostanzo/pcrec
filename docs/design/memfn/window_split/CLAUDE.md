# docs/design/memfn/window_split/ — the window family split's instruments

Instruments of `../window_split.md` (rev 1 lane wsplitd, rev 2 lane wsplitd2, rev 2.1 lane wsplitd3,
2026-11-24).
Read-only over a tree's `memfn/src`; python3 run with `-I`, plus `gcc-16 -fsyntax-only`; never built
or run by `make`. Every count the note quotes names the command that produced it from these files
at B a0742283a (code equal to rev 1's T a0f13ad83). Nothing here writes into the repo: the
assembler writes a scratch tree (`$PCREC_TMPDIR/scratch/<lane>/asm`) and refuses `memfn/src`.

THE CUT AND ITS ASSEMBLY (rev 2, r95 lesson 1)

- `cut.spec` — the cut (`NEWFILE <- SRCFILE a-b ...`, `ent:NAME`; `window.h <-` items win over file
  ranges, `-` drops); census-readable.
- `files.spec` — each new file's title line and, where it differs from the default, its Provenance.
- `window_h.in` — the private header's template (`@TYPES@`, `@DECLS@`) and the `@export` /
  `@new` name list by defining file.
- `edits.spec` — the unit's renames (H3, U2b) and FROM/TO edit blocks (O3, A2-A5, O1, W13, U2b).
- `assemble.py ROOT OUT [--pure]` — writes OUT/memfn/{src,include} as the tip; rules R1-R7 in the
  note §11.1; `--pure` skips edits.spec and the accessors (the control).
- `syncheck.sh OUT [CC]` — `-fsyntax-only` of every OUT .c, strict flags + `-Wmissing-prototypes`,
  plain and `-DMF_TRACE`, then the four white-box drivers; prints PASS/FAIL and a tally.
- `unused.py DIR FILE..` — file statics never named outside their definition (syntax-only's gap).

THE CHECKS OVER A TREE

- `binders.py ROOT TREE [RUNNERS_ROOT] [--compile]` — the re-aim table: every mech SAB_BEFORE, G2
  plant FROM, purity `old`, decider census row and rows_check.py PLANTS edit KEYED to B's eight
  edited files or any file the unit creates (cut.spec's left sides; rev 2.1, r98 R3), found in TREE
  (OK, `OK*` after the unit's re-spellings, STALE, AMBIGUOUS); each population has a floor (its
  size at B: 187/75/49/67/4; `FLOOR_<POP>=` overrides); `--compile` (CC from the environment only)
  plants each AFTER/TO into its new file and `-fsyntax-only`s it. TREE = ROOT is its control; per
  commit ROOT = TREE = the commit. Drilled in the note §7.8.
- `repoint.py BINDERS_OUT` — the per-unit re-point lists (note §8.1, r98 R5) from a binders.py run
  over the assembled tip, grouped by the commit that moves each text.
- `w32reach.py BIN TREE [--floor=byte=N,utf8=M]` — G2 arm 3's reach counter (r98 R11): corpus
  patterns whose `-fmemfn-simd=x86-64-v3` artifact holds `span-vector@w32`, per base; reads
  `scripts/emit_sweep.py`'s corpus enumeration; text only, any host.
- `rekey.py ROOT BINDERS_OUT` — the decider census map at the tip (re-keyed rows + the unit's new
  members), for `decider_census.py --map`.
- `tables.py DIR FILE..` — Goal 1's population: file-scope tables/objects named in another file's
  function bodies.

THE NAME CENSUSES (rev 1; blind spots in the note §13.1)

- `ents.py FILE.c` — top-level entities (kind, name, lines, static), comments/strings blanked.
- `census.py SRC SPEC [-v] [--calls|--bodies]` — crossing names, public names, boundary costs,
  file cycles for a cut SPEC.
- `kitgraph.py SRC SPEC [FILE..]` — the kit's file call graph after a cut and its cycles; `DROP=`.
- `bucket.py SPEC`, `home.py SRC SPEC` — window.c lines / definitions to their new files.
- `plants.py ROOT` — rev 1's window.c/presence.c plant lister; SUPERSEDED by `binders.py` (r95 W22:
  its regex cannot read a tip key).
