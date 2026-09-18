#!/usr/bin/env python3
"""
fragment_census.py -- every `char <ident>[<size-expr>]` declaration in a
named file, classified into the three sizing categories
`docs/dev/reviews/lens_reports/emitvm_second_pass.md` (EP2) section 4
found in src/gen/emit_vm.c, plus a catch-all for anything that fits none
of them:

  (a) bare integer literal            char val[160]
  (b) bare PCREC_MAX_EMIT_NAME_LEN    char nm[PCREC_MAX_EMIT_NAME_LEN]
  (c) anything else (derived constant + literal margin, a bare OTHER
      macro, or any more complex expression)   char cnt[PCREC_MAX_EMIT_NAME_LEN + 64]

Chartered by lane w2census ([REVW.2] row "emit_dfa.c third-category
census FIRST") to (1) reproduce EP2's emit_vm.c population as a
cross-check on the instrument, and (2) run the SAME instrument over
src/gen/emit_dfa.c, which EP2 named but never measured.

python3 stdlib only, no third-party deps, no network, no build --
tools/review/ convention. Unlike this directory's other five scripts,
this one does NOT walk the whole PRIMARY tier: it takes explicit file
paths on the command line, because the census is chartered against two
named files, not a tree-wide sweep (see tools/review/CLAUDE.md).

Method (see docs/dev/w2census.md for the full writeup, including the
one-declarator discrepancy this script's per-DECLARATOR resolution finds
against EP2's reported emit_vm.c total):

1. Lexically mask the file with reviewlib.mask_text() (comments blanked,
   string-literal interiors blanked, preprocessor lines blanked) so a
   `char foo[123]`-shaped byte sequence PRINTED AS EMITTED-CODE TEXT
   inside an sb_printf/snprintf format string -- both emit_vm.c and
   emit_dfa.c do this constantly -- is never mistaken for a real C
   declaration in the reviewed file's own source.
2. Scan the masked text for the token `char` (word-bounded) and, from
   there, consume forward to the matching top-level `;` (bracket-depth
   aware, so a `[...]` size expression or a `{...}` initializer cannot
   end the statement early). This is a STATEMENT, and it may run across
   more than one source line.
3. Split the statement's declarator list on top-level commas. Each part
   matching `IDENT [ EXPR ] (= INIT)?` is a `char`-array DECLARATOR;
   parts that don't match (e.g. `char *p = ...`, a pointer declarator)
   are not scratch buffers of the kind this census is chartered to find
   and are silently excluded -- a declaration statement contributing
   zero array declarators is not counted at all.
4. Classify each declarator's own size expression independently (a
   statement CAN mix categories across its own declarators -- flagged in
   the output rather than forced into one bucket; see the MIXED note in
   docs/dev/w2census.md).
5. Attribute each declarator's line to its enclosing function via
   reviewlib.iter_top_level_headers()'s brace-depth walk (the same
   function-boundary walk function_census.py and clone_candidates.py
   use), so a struct-field declaration -- which has no enclosing
   function -- reads as such rather than being silently misattributed.

Usage:
    python3 tools/review/fragment_census.py FILE [FILE...] [--out PATH]

Prints a per-declarator table plus per-file and combined totals to
stdout; --out additionally writes the same rows as a TSV with this
directory's standard evidence header (commit + date + row count).
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import reviewlib as R  # noqa: E402

# The two categories EP2 section 4 named explicitly; anything that isn't
# one of these two shapes is category (c) -- "derived constant + literal
# margin", a bare OTHER macro, or anything more complex. Category (c) is
# deliberately a catch-all, not a fixed list of shapes: the repaired
# stage-3 acceptance criterion this census supports ("ANY size
# expression, excluding only Vm.up by name") is exactly the point --
# nothing here narrows it back down to a fixed pattern list.
_BARE_INT_RE = re.compile(r"^\s*(?:0[xX][0-9a-fA-F]+|\d+)[uUlL]*\s*$")
_K38_MACRO = "PCREC_MAX_EMIT_NAME_LEN"

CATEGORY_LABEL = {
    "a": "(a) bare integer literal",
    "b": "(b) bare " + _K38_MACRO,
    "c": "(c) anything else (derived constant + margin, other bare macro, ...)",
}


def classify(expr: str) -> str:
    e = expr.strip()
    if _BARE_INT_RE.match(e):
        return "a"
    if e == _K38_MACRO:
        return "b"
    return "c"


def find_enclosing_functions(masked: str, line_of):
    """Returns a sorted list of (start_line, end_line, name_or_None) for
    every depth-0 '{'...'}' span reviewlib's walk finds -- function
    bodies AND non-function bodies (struct/union/initializer), so a
    declaration inside neither (true top-level, or a struct field with
    no enclosing FUNCTION) can be told apart from one inside a real
    function."""
    spans = []
    for kind, name, start_line, end_line, _depth, _header in R.iter_top_level_headers(
        masked, line_of
    ):
        spans.append((start_line, end_line, name if kind == "func" else None))
    spans.sort()
    return spans


def enclosing_function(spans, line: int):
    # Spans are depth-0-to-depth-0, i.e. non-nested at this granularity
    # (reviewlib's walk only tracks brace depth, not a full parse), so a
    # line found inside more than one would indicate a nested top-level
    # span, which the walk does not produce; linear scan is fine at this
    # file size and this script's one-shot, read-only nature.
    for start_line, end_line, name in spans:
        if start_line <= line <= end_line:
            return name
    return None


def scan_file(path: Path):
    """Returns (rows, stmt_count) where rows is a list of dicts, one per
    char-array DECLARATOR found in `path`, and stmt_count is the number
    of char DECLARATION STATEMENTS that contributed at least one such
    declarator (a statement contributing zero array declarators --
    e.g. `char *p = arena_alloc(...);` -- is not counted)."""
    text = path.read_text()
    masked = R.mask_text(text)
    line_of = R.make_line_of(masked)
    spans = find_enclosing_functions(masked, line_of)

    rows = []
    stmt_count = 0
    char_re = re.compile(r"(?<![\w])char\s+")
    n = len(masked)
    for m in char_re.finditer(masked):
        start = m.start()
        j = m.end()
        depth = 0
        while j < n:
            ch = masked[j]
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
            elif ch == ";" and depth == 0:
                break
            j += 1
        stmt_text = masked[start:j]
        stmt_line = line_of(start)

        body = stmt_text[len("char") :].strip()
        parts = []
        depth = 0
        cur = []
        for ch in body:
            if ch == "," and depth == 0:
                parts.append("".join(cur))
                cur = []
                continue
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
            cur.append(ch)
        parts.append("".join(cur))

        decls = []
        for p in parts:
            dm = re.match(
                r"^\s*([A-Za-z_]\w*)\s*\[([^\]]*)\]\s*(=.*)?$", p.strip()
            )
            if dm:
                decls.append((dm.group(1), dm.group(2).strip()))
        if not decls:
            continue

        stmt_count += 1
        stmt_cats = set()
        func = enclosing_function(spans, stmt_line)
        for ident, expr in decls:
            cat = classify(expr)
            stmt_cats.add(cat)
            rows.append(
                {
                    "file": R.rel(path),
                    "line": stmt_line,
                    "function": func or "(struct field / file scope)",
                    "ident": ident,
                    "expr": expr,
                    "category": cat,
                }
            )
        if len(stmt_cats) > 1:
            for r in rows[-len(decls):]:
                r["mixed_statement"] = True
        for r in rows[-len(decls):]:
            r.setdefault("mixed_statement", False)

    return rows, stmt_count


def print_table(rows):
    if not rows:
        print("(no char <ident>[<expr>] declarators found)")
        return
    w_file = max(len("file"), max(len(r["file"]) for r in rows))
    w_line = max(len("line"), max(len(str(r["line"])) for r in rows))
    w_func = max(len("function"), max(len(r["function"]) for r in rows))
    w_ident = max(len("ident"), max(len(r["ident"]) for r in rows))
    fmt = f"{{:<{w_file}}}  {{:>{w_line}}}  {{:<{w_func}}}  {{:<{w_ident}}}  {{:<3}}  {{}}"
    print(fmt.format("file", "line", "function", "ident", "cat", "size expr (+ MIXED flag)"))
    for r in rows:
        mixed = "  [MIXED STATEMENT]" if r.get("mixed_statement") else ""
        print(fmt.format(r["file"], r["line"], r["function"], r["ident"], r["category"], r["expr"] + mixed))


def print_totals(rows, stmt_count, label):
    cats = {"a": 0, "b": 0, "c": 0}
    for r in rows:
        cats[r["category"]] += 1
    total_decl = sum(cats.values())
    print(f"\n-- totals: {label} --")
    print(f"  declaration statements (>=1 char-array declarator): {stmt_count}")
    print(f"  declarators: {total_decl}")
    for cat in ("a", "b", "c"):
        print(f"    {CATEGORY_LABEL[cat]}: {cats[cat]}")
    mixed = [r for r in rows if r.get("mixed_statement")]
    if mixed:
        mixed_stmts = sorted({(r["file"], r["line"]) for r in mixed})
        print(
            f"  MIXED-category statements (declarators span more than one "
            f"category): {len(mixed_stmts)} statement(s), "
            f"{len(mixed)} declarator(s) -- see rows flagged [MIXED STATEMENT]"
        )
        print(
            "  (per-STATEMENT category counts below assign a PURE statement "
            "to its one category and count each MIXED statement separately "
            "-- it is not double-counted into any pure bucket)"
        )
    # Per-statement (not per-declarator) category breakdown, for direct
    # comparison against a report that pins its floor at STATEMENT
    # granularity (e.g. emitvm_second_pass.md section 4's table).
    by_stmt: dict[tuple, set] = {}
    for r in rows:
        key = (r["file"], r["line"])
        by_stmt.setdefault(key, set()).add(r["category"])
    pure_stmt_counts = {"a": 0, "b": 0, "c": 0}
    pure_decl_counts = {"a": 0, "b": 0, "c": 0}
    mixed_stmt_count = 0
    for key, cats_here in by_stmt.items():
        if len(cats_here) == 1:
            (cat,) = cats_here
            pure_stmt_counts[cat] += 1
        else:
            mixed_stmt_count += 1
    for r in rows:
        key = (r["file"], r["line"])
        if len(by_stmt[key]) == 1:
            pure_decl_counts[r["category"]] += 1
    print(f"\n  per-statement breakdown (PURE statements only, {label}):")
    for cat in ("a", "b", "c"):
        print(
            f"    {CATEGORY_LABEL[cat]}: {pure_stmt_counts[cat]} statements / "
            f"{pure_decl_counts[cat]} declarators"
        )
    if mixed_stmt_count:
        print(f"    MIXED: {mixed_stmt_count} statement(s)")


def write_tsv(rows, out_path: Path):
    lines = [R.tsv_header("fragment_census.py", str(datetime.date.today()), len(rows))]
    lines.append("file\tline\tfunction\tident\tcategory\texpr\tmixed_statement\n")
    for r in rows:
        lines.append(
            "\t".join(
                [
                    r["file"],
                    str(r["line"]),
                    r["function"],
                    r["ident"],
                    r["category"],
                    r["expr"],
                    "1" if r.get("mixed_statement") else "0",
                ]
            )
            + "\n"
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(lines))
    print(f"\nwrote {out_path} ({len(rows)} rows)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="+", help="source file(s) to census")
    ap.add_argument("--out", type=Path, default=None, help="also write a TSV here")
    args = ap.parse_args()

    all_rows = []
    for f in args.files:
        path = Path(f).resolve()
        if not path.is_file():
            print(f"error: not a file: {f}", file=sys.stderr)
            return 2
        rows, stmt_count = scan_file(path)
        print(f"\n=== {R.rel(path)} ===")
        print_table(rows)
        print_totals(rows, stmt_count, R.rel(path))
        all_rows.extend(rows)

    if len(args.files) > 1:
        combined_stmts = len(
            {(r["file"], r["line"]) for r in all_rows}
        )
        print_totals(all_rows, combined_stmts, "COMBINED (" + " + ".join(args.files) + ")")

    if args.out:
        write_tsv(all_rows, args.out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
