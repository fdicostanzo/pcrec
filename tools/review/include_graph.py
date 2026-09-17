#!/usr/bin/env python3
"""
include_graph.py -- the #include graph over src/{core,parse,ir,opt,gen}/,
cli/, lib/, plus a layer matrix testing the nominal core->parse->ir->opt->gen
order for back-edges (lens 6, docs/dev/reviews/code_review_criteria_draft.md:
"is there a clean core->parse->ir->opt->gen order or cross-reference?").

Usage:
    python3 tools/review/include_graph.py [--out-edges PATH]
        [--out-matrix PATH] [--out-backedges PATH]

Method: a plain regex scan for `#include "..."` (local/quoted) and
`#include <...>` (system) lines across every .c/.h file in the tier
(reviewlib.iter_source_files() -- the SAME file set function_census.py
walks). No preprocessing, no compilation: this is what the SOURCE TEXT
says it includes, which is what a human reader (and this review) cares
about -- not what a particular build's -D flags would make a
conditionally-compiled #include resolve to. A quoted include is resolved
against this repo's OWN include path, matching gcc's actual quoted-
include search order: the INCLUDING file's own directory first (this
caught a real early-draft gap -- see resolve_local()'s docstring), then
this repo's `-I` list, taken directly from the Makefile
(`ALLFLAGS = ... -Ilib -Isrc`, checked -- `git log`/`grep` this file if
that ever changes): `lib/<path>` is tried before `src/<path>`.

Layers and the nominal order: lib (public API surface, depended on by
everything, should depend on nothing internal) -> core -> parse -> ir ->
opt -> gen -> cli (the top consumer -- nothing should depend on it). The
charter's own phrase names five of these (core->parse->ir->opt->gen);
lib and cli are placed at the two ends because that is their role in the
architecture (APPROACH.md), not because the charter enumerated them --
stated explicitly here since it is a judgment call, not a measurement.
A BACK-EDGE is a resolved, LOCAL include from a LOWER-numbered layer to
a strictly HIGHER-numbered one -- i.e. an EARLIER pipeline stage reaching
INTO a stage that runs after it (e.g. `core` including something from
`parse`, or `parse` including something from `gen`). The common,
EXPECTED direction is the other way: `gen`/`opt`/`ir`/`parse` all
routinely include `core` (it is the shared foundation -- `Ast` itself is
defined in src/core/internal.h, confirmed by reading it) and that is
FORWARD, not a back-edge, under this definition. Anything TO `lib` is
never a back-edge (lib sits below even `core`); anything FROM `cli` is
never a back-edge (cli is the top consumer, index 6, nothing is higher).
Same-layer edges are never back-edges. System includes (`<...>`) are
recorded in the edge list for completeness but never participate in the
layer matrix or the back-edge count -- they're not part of this tree's
own dependency order.

Three outputs:
  1. include_edges.tsv -- every #include statement found: from_file,
     line, spelling, kind (LOCAL/SYSTEM), resolved_to (or UNRESOLVED),
     from_layer, to_layer.
  2. include_layer_matrix.tsv -- a from_layer x to_layer count matrix
     over LOCAL resolved edges only, in nominal order, so a reader can
     see the whole shape at once (which layers touch which) without
     reading 300 edge rows.
  3. include_backedges.tsv -- just the back-edges, one row per violating
     edge, file:line + resolved target, for direct citation.

VALIDATION (hand-checked 2026-09-17): the include_edges.tsv row for
`src/gen/emit_vm.c`'s own `#include "core/internal.h"` line resolves to
`src/core/internal.h` (confirmed the file exists at that path) with
from_layer=gen, to_layer=core -- a FORWARD edge per the nominal order,
correctly not flagged in include_backedges.tsv. Every row of
include_backedges.tsv (see the script's own headline count) was read by
opening both files at the cited line: all are `src/core/*` files
including something from `src/parse/`, confirmed by grep to be the same
few named headers repeated across call sites (see the review report for
the exact list) -- i.e. real, structural, not a scan artifact.
"""
from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reviewlib as rl  # noqa: E402

LAYER_ORDER = ["lib", "core", "parse", "ir", "opt", "gen", "cli"]
LAYER_INDEX = {name: i for i, name in enumerate(LAYER_ORDER)}

_INCLUDE_RE = re.compile(r'^\s*#\s*include\s*([<"])([^>"]+)[>"]')


def layer_of(relpath: str) -> str:
    if relpath.startswith("lib/"):
        return "lib"
    if relpath.startswith("cli/"):
        return "cli"
    for name in ("core", "parse", "ir", "opt", "gen"):
        if relpath.startswith(f"src/{name}/"):
            return name
    return "other"


def resolve_local(inc_path: str, root: Path, from_dir_rel: str) -> str | None:
    """Resolve a quoted #include the way gcc actually does: the INCLUDING
    file's own directory is searched first, then the -I list (this repo's
    Makefile: `-Ilib -Isrc`). Skipping the same-directory step was an
    early-draft bug that reported false UNRESOLVED rows for
    `src/parse/definitions.c`/`mod_uprops.c`'s bare `"parse_mods.h"`
    spelling (same-directory as the includer), while every OTHER module
    file spells it `"parse/parse_mods.h"` relative to `-Isrc` -- both are
    valid C, and both must resolve to the SAME target file."""
    same_dir = root / from_dir_rel / inc_path
    if same_dir.is_file():
        return rl.rel(same_dir.resolve())
    for base in ("lib", "src"):
        cand = root / base / inc_path
        if cand.is_file():
            return f"{base}/{inc_path}"
    return None


def scan() -> list[tuple]:
    rows = []
    root = rl.REPO_ROOT
    for path in rl.iter_source_files():
        relpath = rl.rel(path)
        from_layer = layer_of(relpath)
        text = path.read_text(encoding="utf-8", errors="replace")
        stripped = rl.strip_comments(text)
        for lineno, line in enumerate(stripped.split("\n"), start=1):
            m = _INCLUDE_RE.match(line)
            if not m:
                continue
            delim, inc_path = m.group(1), m.group(2)
            if delim == "<":
                rows.append(
                    (relpath, lineno, inc_path, "SYSTEM", "<system>", from_layer, "external")
                )
                continue
            resolved = resolve_local(inc_path, root, str(Path(relpath).parent))
            if resolved is None:
                rows.append(
                    (relpath, lineno, inc_path, "LOCAL", "UNRESOLVED", from_layer, "unresolved")
                )
            else:
                to_layer = layer_of(resolved)
                rows.append(
                    (relpath, lineno, inc_path, "LOCAL", resolved, from_layer, to_layer)
                )
    rows.sort(key=lambda r: (r[0], r[1]))
    return rows


def write_edges(rows, out_path: Path):
    date = datetime.date.today().isoformat()
    header = rl.tsv_header("include_graph.py", date, len(rows))
    with out_path.open("w", encoding="utf-8") as f:
        f.write(header)
        f.write(
            "\t".join(
                ["from_file", "line", "spelling", "kind", "resolved_to",
                 "from_layer", "to_layer"]
            )
            + "\n"
        )
        for row in rows:
            f.write("\t".join(str(x) for x in row) + "\n")


def write_matrix(rows, out_path: Path):
    counts = {(a, b): 0 for a in LAYER_ORDER for b in LAYER_ORDER}
    for _f, _ln, _sp, kind, _res, from_layer, to_layer in rows:
        if kind != "LOCAL" or to_layer not in LAYER_INDEX or from_layer not in LAYER_INDEX:
            continue
        counts[(from_layer, to_layer)] += 1
    total_edges = sum(
        v for (a, b), v in counts.items()
    )
    date = datetime.date.today().isoformat()
    header = rl.tsv_header(
        "include_graph.py --out-matrix", date, len(LAYER_ORDER),
        extra=f"local_edges={total_edges}",
    )
    with out_path.open("w", encoding="utf-8") as f:
        f.write(header)
        f.write("from_layer\\to_layer\t" + "\t".join(LAYER_ORDER) + "\n")
        for a in LAYER_ORDER:
            f.write(a + "\t" + "\t".join(str(counts[(a, b)]) for b in LAYER_ORDER) + "\n")


def write_backedges(rows, out_path: Path):
    back = []
    for f_, ln, sp, kind, res, from_layer, to_layer in rows:
        if kind != "LOCAL":
            continue
        if from_layer not in LAYER_INDEX or to_layer not in LAYER_INDEX:
            continue
        if LAYER_INDEX[from_layer] < LAYER_INDEX[to_layer]:
            back.append((f_, ln, sp, res, from_layer, to_layer))
    date = datetime.date.today().isoformat()
    header = rl.tsv_header("include_graph.py --out-backedges", date, len(back))
    with out_path.open("w", encoding="utf-8") as f:
        f.write(header)
        f.write(
            "\t".join(["from_file", "line", "spelling", "resolved_to",
                       "from_layer", "to_layer"])
            + "\n"
        )
        for row in back:
            f.write("\t".join(str(x) for x in row) + "\n")
    return back


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out-edges", default=str(rl.REPO_ROOT / "tools/review/out/include_edges.tsv")
    )
    ap.add_argument(
        "--out-matrix",
        default=str(rl.REPO_ROOT / "tools/review/out/include_layer_matrix.tsv"),
    )
    ap.add_argument(
        "--out-backedges",
        default=str(rl.REPO_ROOT / "tools/review/out/include_backedges.tsv"),
    )
    args = ap.parse_args()
    rows = scan()
    edges_path = Path(args.out_edges)
    matrix_path = Path(args.out_matrix)
    back_path = Path(args.out_backedges)
    edges_path.parent.mkdir(parents=True, exist_ok=True)
    write_edges(rows, edges_path)
    write_matrix(rows, matrix_path)
    back = write_backedges(rows, back_path)
    n_unresolved = sum(1 for r in rows if r[4] == "UNRESOLVED")
    print(
        f"include_graph: {len(rows)} #include statements, "
        f"{n_unresolved} unresolved local includes, {len(back)} back-edges "
        f"-- edges:{edges_path} matrix:{matrix_path} backedges:{back_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
