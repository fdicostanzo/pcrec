#!/usr/bin/env python3
"""
literal_census.py -- numeric and string literals in the PRIMARY review
tier (src/, cli/, lib/), with file:line and a context snippet, for lens 3
(docs/dev/reviews/code_review_criteria_draft.md: "magic numbers, inline
strings, config centralization ... anchored to the EXISTING convention:
limits.def is the ruled home").

Usage:
    python3 tools/review/literal_census.py [--out PATH] [--freq-out PATH]

Masking: uses reviewlib.strip_comments() ONLY -- comments blanked, but
PREPROCESSOR LINES AND STRING CONTENT ARE LEFT INTACT, unlike
function_census.py/clone_candidates.py's full mask_text(). Both of those
differences matter here: a magic number inside a #define body (e.g.
src/core/arena.c's `#define ABLOCK_MIN (64 * 1024)`) is exactly the
un-centralized-literal shape lens 3 is chartered to find, so preprocessor
lines must NOT be blanked away; and a string literal's actual TEXT (a
diagnostic message, a format string) is the whole point of the string
half of this census, so its content must survive, not be replaced with
blanks the way the structural masker needs to for brace-safety.

The `src/core/limits.def`/`src/core/limits.h` EXCLUSION the charter asks
for ("excluding limits.def-derived spellings where identifiable") turns
out to need no special-case code: `limits.def` is not a `.c`/`.h` file,
so it is never in reviewlib.iter_source_files()'s walk at all, and every
module's own reference to a limits.def row is via the X-macro
`#include "core/limits.def"` pattern (see src/parse/mod_backrefs.c's own
comment on this) -- a PREPROCESSOR DIRECTIVE whose #include'd numeric
VALUES never appear as text inside the referencing .c file itself (this
script does not run a preprocessor; it is a pure text scan). So every
numeric literal this census reports is, by construction, one that is
NOT routed through limits.def -- confirmed by grep: `src/core/limits.def`
itself is never a `file` value (it is not a .c/.h file, so
iter_source_files() never walks it), and `src/core/limits.h` (the X-macro
scaffolding header, a REAL .h file) contributes exactly one row, the
`#include "core/limits.def"` PATH STRING itself -- no numeric limit VALUE
ever appears as census text anywhere in the tree.

Two outputs:
  1. literal_census.tsv -- one row per literal occurrence:
       file  line  kind  literal  context
     `kind` is NUM or STR (CHR char-literals are folded into STR: same
     admissibility question, "should this be a named/shared spelling").
     `context` is the source line, comment-stripped, trimmed and capped
     at 160 chars.
  2. literal_value_freq.tsv -- the SAME rows grouped by (kind, literal),
     count and distinct-file count, sorted by count descending. This is
     the A5 evidence rule's direct instrument: a literal repeated
     verbatim across N files with no shared name is lens 3's headline
     finding shape, and this file is what a "the string/number X appears
     N times, never through limits.def" citation points at.

Known imprecision (documented rather than silently accepted, per the
validation bar): the numeric-literal regex does not attempt full C
grammar (it will not distinguish a genuine numeric literal from, say, a
digit sequence inside an unusual macro-pasted token); reviewed by hand
against a sample -- see VALIDATION below. This is a census for human
review, not a compiler; false positives are expected to be rare and are
the reviewing lens's problem to filter, exactly as literal `0`/`1`/`2`
occurrences (extremely common and mostly uninteresting) are left IN the
census rather than guessed at and filtered -- filtering by magnitude
here would be a judgment call the charter reserves for the lens, not
the metric artifact ("Judgment calls marked as such").

VALIDATION (hand-checked 2026-09-17): ten literal_census.tsv rows read
against their source file at the stated line -- five numeric (including
src/core/arena.c:6's `64 * 1024` ABLOCK_MIN two-literal line, confirmed
NOT routed through limits.def by reading the file's own header comment)
and five string (including a repeated diagnostic-format string found via
literal_value_freq.tsv, confirmed a real un-shared duplicate by reading
both call sites). All ten matched their source line exactly, no
off-by-one, no truncated context. The validation pass caught a real bug
in the first draft: the numeric branch appended `m.group(2)` (the suffix
capture) a SECOND time onto `m.group(0)` (which already includes it),
turning `1u` into `1uu` -- visible immediately in literal_value_freq.tsv
as a `1uu` row with count 69 that had no plausible C reading. Fixed by
using `m.group(0)` alone; the frequency table's suffix-bearing rows now
read as real C spellings (`1u`, `1U`, `1UL`, ...).
"""
from __future__ import annotations

import argparse
import datetime
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reviewlib as rl  # noqa: E402

_NUM_RE = re.compile(
    r"""(?<![\w.])(
        0[xX][0-9a-fA-F]+          # hex
      | 0[0-7]+                    # octal (leading zero, no 8/9/./e)
      | \d+\.\d+(?:[eE][+-]?\d+)?  # float with fraction
      | \.\d+(?:[eE][+-]?\d+)?     # float, no leading digit
      | \d+[eE][+-]?\d+            # float, exponent only
      | \d+                        # plain integer
    )([uUlL]{0,3}[fF]?)(?![\w.])""",
    re.VERBOSE,
)

_STR_RE = re.compile(r'"(?:[^"\\]|\\.)*"')
_CHR_RE = re.compile(r"'(?:[^'\\]|\\.)*'")

CONTEXT_CAP = 160


def scan_file(path: Path) -> list[tuple]:
    text = path.read_text(encoding="utf-8", errors="replace")
    stripped = rl.strip_comments(text)
    relpath = rl.rel(path)
    rows = []
    for lineno, line in enumerate(stripped.split("\n"), start=1):
        if not line.strip():
            continue
        # Strings/chars first (so a numeric-looking substring inside one
        # is not double-reported as a numeric literal too).
        str_spans = []
        for m in _STR_RE.finditer(line):
            str_spans.append(m.span())
            rows.append((relpath, lineno, "STR", m.group(0), line))
        for m in _CHR_RE.finditer(line):
            str_spans.append(m.span())
            rows.append((relpath, lineno, "STR", m.group(0), line))

        def inside_str(pos):
            return any(a <= pos < b for a, b in str_spans)

        for m in _NUM_RE.finditer(line):
            if inside_str(m.start()):
                continue
            rows.append((relpath, lineno, "NUM", m.group(0), line))
    return rows


def make_context(line: str) -> str:
    ctx = line.strip()
    if len(ctx) > CONTEXT_CAP:
        ctx = ctx[: CONTEXT_CAP - 3] + "..."
    return ctx


def collect() -> list[tuple]:
    rows = []
    for path in rl.iter_source_files():
        rows.extend(scan_file(path))
    # sort deterministically: file, line, kind, literal
    rows.sort(key=lambda r: (r[0], r[1], r[2], r[3]))
    return rows


def write_census(rows, out_path: Path):
    date = datetime.date.today().isoformat()
    header = rl.tsv_header("literal_census.py", date, len(rows))
    with out_path.open("w", encoding="utf-8") as f:
        f.write(header)
        f.write("\t".join(["file", "line", "kind", "literal", "context"]) + "\n")
        for file_, line, kind, literal, raw_line in rows:
            f.write(
                f"{file_}\t{line}\t{kind}\t{literal}\t{make_context(raw_line)}\n"
            )


def write_freq(rows, out_path: Path):
    counts: dict = defaultdict(lambda: [0, set()])
    for file_, _line, kind, literal, _raw in rows:
        counts[(kind, literal)][0] += 1
        counts[(kind, literal)][1].add(file_)
    items = sorted(
        counts.items(), key=lambda kv: (-kv[1][0], -len(kv[1][1]), kv[0])
    )
    date = datetime.date.today().isoformat()
    header = rl.tsv_header("literal_census.py --freq-out", date, len(items))
    with out_path.open("w", encoding="utf-8") as f:
        f.write(header)
        f.write("\t".join(["kind", "literal", "count", "distinct_files", "sample_files"]) + "\n")
        for (kind, literal), (count, files) in items:
            sample = ",".join(sorted(files)[:5])
            if len(files) > 5:
                sample += f",...(+{len(files) - 5})"
            f.write(f"{kind}\t{literal}\t{count}\t{len(files)}\t{sample}\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out", default=str(rl.REPO_ROOT / "tools/review/out/literal_census.tsv")
    )
    ap.add_argument(
        "--freq-out",
        default=str(rl.REPO_ROOT / "tools/review/out/literal_value_freq.tsv"),
    )
    args = ap.parse_args()
    rows = collect()
    out_path = Path(args.out)
    freq_path = Path(args.freq_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_census(rows, out_path)
    write_freq(rows, freq_path)
    n_num = sum(1 for r in rows if r[2] == "NUM")
    n_str = sum(1 for r in rows if r[2] == "STR")
    print(
        f"literal_census: {len(rows)} literals ({n_num} numeric, {n_str} "
        f"string/char) written to {out_path}; frequency table at {freq_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
