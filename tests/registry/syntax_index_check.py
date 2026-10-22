#!/usr/bin/env python3
r"""syntax_index_check.py -- docs/spec/pattern_language.md §10 against `pcrec --list-syntax`.

pattern_language.md is the hand-written definition of the pattern language; its §10 is a
table with one line per `--list-syntax` row: the row's `syntax`, its `module`
and the pattern_language.md section that defines it.  The two sources are independent
(the registry is printed by the compiler, the table is written by hand), and
this check holds them equal:

  missing   a registry row has no index line (a construct the doc omits)
  extra     an index line names no registry row (a construct that went away)
  module    an index line's module differs from the row's
  section   an index line names a section the doc does not have
  dup       an index line appears twice

Columns are resolved by header name (docs/spec/table_contract.md).  Before
judging the real inputs the check runs itself on three planted mutations of
the real doc (a line dropped, a line added, a module changed) and fails unless
each is reported: a comparison that reads nothing, or reads both sides the
same wrong way, cannot pass.

  PCREC=build/pcrec python3 tests/registry/syntax_index_check.py [DOC]
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOC = os.path.join(ROOT, "docs", "spec", "pattern_language.md")

HEADING = re.compile(r"^#{2,6}\s+(\d+[a-z]?(?:\.\d+[a-z]?)*)\.?\s")
INDEX_HEAD = re.compile(r"^#{2,6}\s+(?:<a[^>]*></a>\s*)?\d+\.?\s+Construct index\s*$")
CELL_CODE = re.compile(r"^`(.*)`$")


def registry_rows(pcrec):
    out = subprocess.run([pcrec, "--list-syntax"], capture_output=True, text=True, check=True).stdout
    lines = out.split("\n")
    header = None
    rows = []
    for ln in lines:
        if not ln:
            continue
        if ln.startswith("#"):
            header = ln[1:].split("\t")
            continue
        f = ln.split("\t")
        rows.append((f[header.index("syntax")], f[header.index("module")]))
    return rows


def split_cells(line):
    r"""Cells of a markdown table line, honouring `\|` inside a cell."""
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    cells, cur, i = [], "", 0
    while i < len(body):
        if body[i] == "\\" and i + 1 < len(body) and body[i + 1] == "|":
            cur += "|"
            i += 2
            continue
        if body[i] == "|":
            cells.append(cur.strip())
            cur = ""
        else:
            cur += body[i]
        i += 1
    cells.append(cur.strip())
    return cells


def unquote(cell):
    m = CELL_CODE.match(cell)
    return m.group(1) if m else cell


def read_doc(text):
    """(sections, index lines) of a pattern_language.md text."""
    sections = set()
    index = []
    in_index = False
    for ln in text.split("\n"):
        if ln.startswith("#"):
            m = HEADING.match(ln)
            if m:
                sections.add(m.group(1))
            in_index = bool(INDEX_HEAD.match(ln))
            continue
        if in_index and ln.startswith("|"):
            cells = split_cells(ln)
            if len(cells) != 3 or cells[0] == "syntax" or set(cells[0]) <= set("-: "):
                continue
            index.append((unquote(cells[0]), unquote(cells[1]), cells[2].lstrip("§")))
    return sections, index


def compare(rows, sections, index):
    problems = []
    reg = {}
    for syn, mod in rows:
        reg[syn] = mod
    seen = {}
    for syn, mod, sec in index:
        seen[syn] = seen.get(syn, 0) + 1
        if seen[syn] == 2:
            problems.append("dup      %s" % syn)
        if syn not in reg:
            problems.append("extra    %s (no --list-syntax row has this syntax)" % syn)
        elif reg[syn] != mod:
            problems.append("module   %s: index says '%s', registry says '%s'" % (syn, mod, reg[syn]))
        if sec not in sections:
            problems.append("section  %s: §%s is not a section of pattern_language.md" % (syn, sec))
    for syn, _ in rows:
        if syn not in seen:
            problems.append("missing  %s (registry row with no pattern_language.md §10 line)" % syn)
    return problems


def selftest(rows, text):
    """Plant three mutations of the real doc; each must be reported."""
    sections, index = read_doc(text)
    if not index:
        return ["selftest: the real doc has no index lines to mutate"]
    first = index[0]
    plants = {
        "missing": [l for l in index if l is not first],
        "extra": index + [("\\planted-construct", "", first[2])],
        "module": [(first[0], first[1] + "-planted", first[2])] + index[1:],
    }
    out = []
    for kind, mutated in plants.items():
        if not any(p.startswith(kind) for p in compare(rows, sections, mutated)):
            out.append("selftest: a planted '%s' mutation was not reported" % kind)
    return out


def main():
    doc = sys.argv[1] if len(sys.argv) > 1 else DOC
    pcrec = os.environ.get("PCREC", os.path.join(ROOT, "build", "pcrec"))
    rows = registry_rows(pcrec)
    text = open(doc, encoding="utf-8").read()
    sections, index = read_doc(text)
    fails = []
    if not rows:
        fails.append("population: --list-syntax printed no rows")
    if not index:
        fails.append("population: pattern_language.md has no §10 index lines")
    fails += selftest(rows, text)
    fails += compare(rows, sections, index)
    for f in fails:
        print("FAIL: syntax-index: " + f, file=sys.stderr)
    if fails:
        return 1
    print("syntax-index: %d registry rows, %d index lines, %d sections: all agree"
          % (len(rows), len(index), len(sections)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
