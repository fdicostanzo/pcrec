#!/usr/bin/env python3
"""
function_census.py -- every C function in the PRIMARY review tier
(src/, cli/, lib/), LENGTH-RANKED descending, for the code-review lenses
(docs/dev/reviews/code_review_criteria_draft.md).

Usage:
    python3 tools/review/function_census.py [--out PATH]

Run from anywhere; paths resolve off the repo root (reviewlib.REPO_ROOT).
Deterministic: same commit in, byte-identical TSV out (files walked in
sorted order, ties broken by file then start_line).

Output: tools/review/out/function_census.tsv, columns
    file  start_line  end_line  span_lines  code_lines  max_depth  name

`code_lines` (non-blank, non-comment-only lines in [start_line, end_line])
is what the row is RANKED BY, descending -- per the ratification
ADDENDUM 2, this is the whole population in PRIORITY order, not a
filtered "over-N" list; a downstream lens works this ranking top-down and
states where it stopped. `span_lines` (end_line - start_line + 1) is kept
alongside because it is what a reader sees scrolling the file, and the two
occasionally diverge a lot on comment-heavy functions (see clone_candidates.py
and literal_census.py, which both cite file:line spans from THIS file's
`file`/`start_line`/`end_line` triple as their join key).

Why not ctags: this box's /usr/bin/ctags is BSD ctags (`illegal option --`,
no -f pipe to JSON, no end-line, no nesting-depth output) -- unusable for a
census that needs spans and depth, not just start lines. Per the charter's
own fallback clause ("prefer your own brace/state parser over ctags if
ctags proves unreliable on gcc-dialect C"), this script uses reviewlib's
brace/state walk instead. It specifically handles the two gcc-dialect
features that would break a naive regex scan: computed-goto labels
(`&&Lname`, `goto *ptr`) are ordinary statement text with no special
brace/paren shape, so they need no special case at all; and every
generated-code STRING LITERAL the emitters build (src/gen/emit_vm.c and
emit_dfa.c print C source as strings, heavily using braces/parens/quotes
INSIDE those strings) is lexically masked before any brace is counted, so
a `pcrec_sb_printf(c, "... { ... }\n", ...)` call two levels deep in the real
tree does not perturb the real depth count.

VALIDATION (hand-checked 2026-09-17, ten functions across the smallest
and one of the largest files in the tier, by reading `sed -n` output at
the reported boundaries and counting braces by eye):
  - src/core/arena.c: pcrec_arena_alloc (8-33, depth 3: body/outer-if/inner-if)
    and pcrec_arena_free (35-44, depth 2: body/while) -- the file's only two
    functions, both boundaries exact against `cat -n`.
  - src/gen/emit_vm.c (11,575 lines, the file the charter cites for
    "300-527-line functions"):
      * vm_rolef: a PROTOTYPE-then-DEFINITION pair (line 754 ends in
        `__attribute__((format(...)));`, discarded as a declaration;
        line 756 is the real definition) -- census correctly reports
        756-770, not 754, proving the `;`-terminated-header discard path.
      * vm_label: `static int vm_label(Vm *v) { return v->nlabel++; }`,
        a single-LINE function -- census reports 772-772 (start==end).
      * vm_cursor_fits: a signature split across TWO lines (the
        parameter list wraps) -- census reports the FIRST line of the
        signature (1706) as start_line, not the line the `{` sits on
        (1708), and 1716 as the true closing brace.
      * vm_emit: 7129-7643 (515 lines) -- exactly inside the charter's
        cited 300-527 range, independent confirmation the parser is
        finding what the charter's own spot-check found.
      * pcrec_emit_vm: 8539-11575 (3,037 lines) -- the file's true LAST
        top-level construct, running to EOF with nothing defined after
        it; confirmed genuine (not a brace-tracking bug swallowing the
        rest of the file) by grepping for any column-0 signature between
        8539 and EOF (none) and reading the file's literal last lines.
  - src/core/internal.h: cls_set/cls_has, two `static inline` one-liners
    at 1031/1032 -- census reports 1031-1031 and 1032-1032, matching a
    direct grep of the two lines exactly.
  - lib/pcrec.h (the pure public header, ALL declarations, no bodies):
    census reports ZERO functions -- the one file in the tier this
    should be true of, confirming the `;`-only-header path doesn't
    misfire into inventing bodies.
  - cli/main.c: spot-checked `usage()` (99-263, depth 1) against the
    file directly -- one large `fputs(multi-line-string-literal, f);`
    statement, no nested blocks, matching the reported depth exactly.
"""
from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reviewlib as rl  # noqa: E402


def census() -> list[tuple]:
    rows = []
    for path in rl.iter_source_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        masked = rl.mask_text(text)
        line_of = rl.make_line_of(text)
        lines = text.split("\n")
        masked_lines = masked.split("\n")
        relpath = rl.rel(path)
        for kind, name, start, end, depth, _header in rl.iter_top_level_headers(
            masked, line_of
        ):
            if kind != "func":
                continue
            code_lines = 0
            for ln in range(start, end + 1):
                if ln - 1 < len(masked_lines) and masked_lines[ln - 1].strip():
                    code_lines += 1
            rows.append((relpath, start, end, end - start + 1, code_lines, depth, name))
    # Rank by code_lines descending (ADDENDUM 2: priority order over the
    # WHOLE population). Ties broken by file/start_line for determinism.
    rows.sort(key=lambda r: (-r[4], r[0], r[1]))
    return rows


def write_tsv(rows: list[tuple], out_path: Path) -> None:
    date = datetime.date.today().isoformat()
    header = rl.tsv_header("function_census.py", date, len(rows))
    with out_path.open("w", encoding="utf-8") as f:
        f.write(header)
        f.write(
            "\t".join(
                ["file", "start_line", "end_line", "span_lines", "code_lines",
                 "max_depth", "name"]
            )
            + "\n"
        )
        for relpath, start, end, span, code_lines, depth, name in rows:
            f.write(f"{relpath}\t{start}\t{end}\t{span}\t{code_lines}\t{depth}\t{name}\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out", default=str(rl.REPO_ROOT / "tools/review/out/function_census.tsv")
    )
    args = ap.parse_args()
    rows = census()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_tsv(rows, out_path)
    total_files = len({r[0] for r in rows})
    over_100 = sum(1 for r in rows if r[4] > 100)
    print(
        f"function_census: {len(rows)} functions across {total_files} files "
        f"({over_100} with code_lines > 100), written to {out_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
