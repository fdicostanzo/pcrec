"""
reviewlib.py -- shared primitives for the tools/review/ metric scripts.

python3 stdlib only. No third-party dependencies, no network, no build.

Provides:
  - PRIMARY_DIRS: the review charter's PRIMARY scope tier (src/, cli/, lib/)
  - iter_source_files(): every .c/.h file under the primary tier, sorted
  - mask_text(): blank out comment and string/char-literal INTERIOR bytes,
    and blank whole preprocessor-directive lines (and their backslash
    continuations), while preserving the exact line/column layout of the
    original file. This is the shared lexical front end every script in
    this directory uses so their line numbers agree with each other and
    with a plain-text `grep`.
  - line_of(): map a character offset in a file's text to a 1-based line
    number, via bisection over precomputed newline offsets.
  - iter_top_level_headers(): the brace-depth walk that finds every
    depth-0-to-depth-0 span in a masked file and classifies each as a
    function definition or something else (struct/enum/initializer/etc).
    function_census.py and clone_candidates.py both build on this so a
    function's [start_line, end_line) here is the SAME span both scripts
    report, which is what lets lens 11's over-length rows join directly
    to lens 1's clone candidates (the charter's ADDENDUM 1 loop).
  - tsv_header(): the "commit + date + row count" evidence header every
    committed tools/review/out/*.tsv file carries, so a truncated file is
    detectable by comparing the stated count against the actual row count.

Validation note (read before trusting this on a new file shape): this
lexer was hand-checked against src/gen/emit_vm.c and src/gen/emit_dfa.c,
the two files with the heaviest use of C string literals to emit
generated-code text (braces/parens/quotes appear INSIDE those string
literals in huge quantity) and the codebase's only multi-line function
signatures and single-line `static inline` bodies. See
function_census.py's module docstring for the exact validation
transcript (10 functions, boundaries checked by hand against `sed`).
"""

from __future__ import annotations

import subprocess
import sys
from bisect import bisect_right
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]

# The review charter's scope tiers (docs/dev/reviews/code_review_criteria_draft.md
# "Scope tiers"). tools/review/ metrics are PRIMARY-tier only unless a script
# says otherwise in its own header.
PRIMARY_DIRS = ("src", "cli", "lib")

_KEYWORD_BLACKLIST = {
    "if", "for", "while", "switch", "return", "sizeof", "struct", "union",
    "enum", "typedef", "do", "else", "goto", "case", "default", "break",
    "continue", "static", "const", "volatile", "extern", "inline", "void",
}


def iter_source_files(dirs=PRIMARY_DIRS, root: Path = REPO_ROOT) -> list[Path]:
    """Every .c/.h file under the given top-level dirs, sorted for a
    deterministic, diffable walk order."""
    out: list[Path] = []
    for d in dirs:
        base = root / d
        if not base.is_dir():
            continue
        for ext in ("*.c", "*.h"):
            out.extend(base.rglob(ext))
    return sorted(set(out), key=lambda p: str(p.relative_to(root)))


def rel(path: Path, root: Path = REPO_ROOT) -> str:
    return str(path.relative_to(root))


def git_commit(root: Path = REPO_ROOT) -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True,
            text=True, timeout=10, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return "UNKNOWN"


def tsv_header(script_name: str, date: str, row_count: int, extra: str = "") -> str:
    """The evidence header every committed out/*.tsv file starts with:
    commit + date + row count, so a truncated file is caught by comparing
    the stated count against a re-count of the body."""
    commit = git_commit()
    extra_s = f" {extra}" if extra else ""
    return (
        f"# {script_name} -- commit {commit} -- generated {date} "
        f"-- rows {row_count}{extra_s}\n"
    )


# ---------------------------------------------------------------------------
# Lexical masking: comments, string/char literals, preprocessor lines.
#
# Three composable stages, because different scripts need different subsets:
#   - strip_comments(): // and /* */ only -- what literal_census.py and
#     include_graph.py want, since a magic number inside a #define body
#     (e.g. arena.c's `#define ABLOCK_MIN (64 * 1024)`) is exactly the
#     class of un-centralized literal lens 3 is chartered to find, and an
#     #include line IS include_graph.py's whole subject.
#   - blank_string_interiors(): additionally blanks string/char literal
#     CONTENT (keeps the quotes) so a brace/paren inside emitted-code text
#     (src/gen/emit_vm.c and emit_dfa.c print C source as strings) cannot
#     perturb a structural brace-depth walk.
#   - blank_preprocessor_lines(): additionally blanks whole preprocessor
#     directive lines, INCLUDING any lines joined to them by a trailing
#     backslash-newline continuation (this is what keeps a multi-line
#     function-like macro body, e.g. `#define REFUSE(...) do { ... }
#     while (0)` spread over several lines, from perturbing a brace-depth
#     walk -- a macro DEFINITION is not part of the surrounding C
#     statement stream).
#   - mask_text() = all three, in that order -- what function_census.py
#     and clone_candidates.py need for structural analysis.
# All four return a string the SAME LENGTH as the input (same newline
# positions), so line numbers computed against the input stay valid
# against the output.
# ---------------------------------------------------------------------------

def strip_comments(text: str) -> str:
    """Blank // and /* */ comment CONTENT (delimiters included), leaving
    everything else -- strings, preprocessor lines, real code -- untouched
    at its original offset."""
    n = len(text)
    out = list(text)
    i = 0
    # This loop must still recognize (and skip over without blanking)
    # string/char literals, purely so a '//' or '/*' BYTE sequence that
    # happens to sit inside a string literal (e.g. a URL in an emitted-
    # code string) is not mistaken for the start of a real comment.
    while i < n:
        c = text[i]
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            j = i
            while j < n and text[j] != "\n":
                out[j] = " "
                j += 1
            i = j
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            out[i] = " "
            out[i + 1] = " "
            j = i + 2
            while j + 1 < n and not (text[j] == "*" and text[j + 1] == "/"):
                if text[j] != "\n":
                    out[j] = " "
                j += 1
            if j + 1 < n:
                out[j] = " "
                out[j + 1] = " "
                i = j + 2
            else:
                if j < n and text[j] != "\n":
                    out[j] = " "
                i = n
            continue
        if c == '"' or c == "'":
            quote = c
            j = i + 1
            while j < n and text[j] != quote:
                if text[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                if text[j] == "\n":
                    break
                j += 1
            if j < n and text[j] == quote:
                j += 1
            i = j
            continue
        i += 1
    return "".join(out)


def blank_string_interiors(text: str) -> str:
    """Given comment-already-stripped text, blank string/char literal
    INTERIORS (quotes kept) so a brace/paren/semicolon printed as generated-
    code TEXT inside a string literal cannot be mistaken for real C
    structure. Leaves everything else untouched."""
    n = len(text)
    out = list(text)
    i = 0
    while i < n:
        c = text[i]
        if c == '"' or c == "'":
            quote = c
            out[i] = " "
            j = i + 1
            while j < n and text[j] != quote:
                if text[j] == "\\" and j + 1 < n:
                    if text[j] != "\n":
                        out[j] = " "
                    j += 1
                    if text[j] != "\n":
                        out[j] = " "
                    j += 1
                    continue
                if text[j] == "\n":
                    # unterminated literal (shouldn't happen in valid C);
                    # stop masking at the line break to stay safe.
                    break
                out[j] = " "
                j += 1
            if j < n and text[j] == quote:
                out[j] = " "
                j += 1
            i = j
            continue
        i += 1
    return "".join(out)


def blank_preprocessor_lines(text: str) -> str:
    """Blank whole preprocessor directive lines (and backslash
    continuations), using line boundaries so we never split a
    multi-byte-safe str. Expects comments already stripped so a `#`
    inside a comment isn't mistaken for a directive."""
    lines = text.split("\n")
    k = 0
    while k < len(lines):
        stripped = lines[k].lstrip()
        if stripped.startswith("#"):
            while True:
                rstripped = lines[k].rstrip()
                cont = rstripped.endswith("\\")
                lines[k] = " " * len(lines[k])
                if not cont or k + 1 >= len(lines):
                    break
                k += 1
        k += 1
    return "\n".join(lines)


def mask_text(text: str) -> str:
    """Full structural mask: strip_comments + blank_string_interiors +
    blank_preprocessor_lines, in that order. What function_census.py and
    clone_candidates.py use for their brace-depth walk. See the section
    docstring above for why each script wants a different subset."""
    return blank_preprocessor_lines(blank_string_interiors(strip_comments(text)))


def newline_offsets(text: str) -> list[int]:
    offs = [-1]
    idx = text.find("\n")
    while idx != -1:
        offs.append(idx)
        idx = text.find("\n", idx + 1)
    return offs


def make_line_of(text: str):
    offs = newline_offsets(text)

    def line_of(pos: int) -> int:
        # 1-based line number containing character offset `pos`.
        return bisect_right(offs, pos)

    return line_of


# ---------------------------------------------------------------------------
# Top-level (depth-0) header classification and the brace-depth walk.
# ---------------------------------------------------------------------------

_IDENT_CHARS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
)


def _find_first_top_level_paren(header: str) -> Optional[tuple[int, int]]:
    """Return (open_idx, close_idx) of the first paren-depth-0 '(' ... ')'
    group in `header`, or None if there isn't one."""
    depth = 0
    start = None
    for idx, ch in enumerate(header):
        if ch == "(":
            if depth == 0:
                start = idx
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and start is not None:
                return (start, idx)
    return None


def classify_header(header: str) -> Optional[str]:
    """Given the accumulated depth-0 text immediately preceding a '{',
    return the function name if this header is a function DEFINITION,
    else None (struct/union/enum body, array/struct initializer, etc).

    Rule (see module docstring / function_census.py for the validation
    behind it): a function header has a top-level '(...)' parameter-list
    group with a plain identifier immediately before it, and no top-level
    '=' before that group (which would mark an initializer instead).
    """
    stripped = header.strip()
    if not stripped:
        return None

    paren = _find_first_top_level_paren(header)
    if paren is None:
        return None
    open_idx, _close_idx = paren

    # No top-level '=' before the parameter list (an initializer, not a
    # function signature). Top-level here means not inside the eventual
    # parens themselves, i.e. anywhere before open_idx.
    before = header[:open_idx]
    if "=" in before:
        return None
    # Reject a stray top-level ';' or '{' having leaked into the buffer
    # (defensive; the caller resets the buffer on those already).
    if ";" in before or "{" in before:
        return None

    j = open_idx - 1
    while j >= 0 and header[j] in " \t\r\n":
        j -= 1
    end = j + 1
    while j >= 0 and header[j] in _IDENT_CHARS:
        j -= 1
    start = j + 1
    if start >= end:
        return None
    name = header[start:end]
    if not name or name[0].isdigit():
        return None
    if name in _KEYWORD_BLACKLIST:
        return None
    return name


@dataclass
class FunctionSpan:
    file: str
    name: str
    start_line: int
    end_line: int
    max_depth: int
    header: str = field(repr=False, default="")


def iter_top_level_headers(text_masked: str, line_of) -> Iterator[tuple]:
    """Walk `text_masked` tracking brace depth. Yields tuples:
      ('func', name, start_line, end_line, max_depth, header_text)
      ('other', None, start_line, end_line, None, header_text)
    for every depth-0 -> depth-0 '{' ... '}' span, in file order.
    Top-level ';'-terminated declarations (no body) produce nothing.
    """
    depth = 0
    header_chars: list[str] = []
    header_start = None
    cur = None  # dict while inside a body
    local_max = 0
    n = len(text_masked)
    for idx in range(n):
        ch = text_masked[idx]
        if depth == 0:
            if ch == "{":
                header = "".join(header_chars)
                name = classify_header(header)
                start_line = line_of(header_start if header_start is not None else idx)
                if name is not None:
                    cur = {"name": name, "start_line": start_line, "header": header}
                else:
                    cur = {"name": None, "start_line": start_line, "header": header}
                depth = 1
                local_max = 1
                header_chars = []
                header_start = None
            elif ch in ";":
                header_chars = []
                header_start = None
            elif ch == "}":
                # stray at depth 0; ignore defensively, reset buffer
                header_chars = []
                header_start = None
            else:
                if ch not in " \t\r\n":
                    if header_start is None:
                        header_start = idx
                    header_chars.append(ch)
                elif header_chars:
                    header_chars.append(ch)
        else:
            if ch == "{":
                depth += 1
                if depth > local_max:
                    local_max = depth
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end_line = line_of(idx)
                    if cur["name"] is not None:
                        yield (
                            "func", cur["name"], cur["start_line"], end_line,
                            local_max, cur["header"],
                        )
                    else:
                        yield (
                            "other", None, cur["start_line"], end_line,
                            local_max, cur["header"],
                        )
                    cur = None
                    local_max = 0
