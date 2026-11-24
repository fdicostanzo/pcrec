#!/usr/bin/env python3
"""tests/core/ucd_wall_check.py ROOT [WORKDIR] -- [DATA-PLAN] A1 THE UCD WALL.

Exactly ONE module understands the Unicode tables' storage format:
`src/parse/ucd_tables.c`, with its header `ucd_tables.h` as the interface.  Its
WRITER (`third_party/ucd-16.0.0/generate.py`) is the only other file that may
name the generated file or its symbols.  The owner's ruling (2026-11-24): "have
it be modular so the format is only understood to the module which provides
an interface".  Run by `ucd_wall_check.sh` (which `run_core_tests.sh` runs).

WHAT IT SCANS.  Every file `git ls-files -co --exclude-standard` lists (a
`find` when ROOT is not a git tree), wherever it lives -- docs/ included, since
about a fifth of docs/ is code -- except files with a PROSE suffix (.md, .txt,
.rst, .tsv, .csv, .html and binary images), the generated census output
(tools/review/out/), build trees, worktrees/ and the ALLOW list below.  Lines
continued with a backslash are joined before any pattern runs, so a splice
cannot hide a name.

WHAT IS AN OFFENDER (a file outside the allow-list that has any of):
  1. the generated file's NAME (derived from the module's own `#include`),
     or a symbol of what the writer EMITS: every `ucd_*` identifier and
     `UCD_GEN_*` macro in the generated file itself -- derived, never typed
     here, so a new array or macro the writer adds is covered the day it
     appears;
  2. a PRIVATE name of the module: every `static` function and `Ucd*` typedef
     in ucd_tables.c (read from the module);
  3. a name of the RETIRED format (`pcrec_uprop[s]_*`, `PCREC_UPROP[S]_*`,
     the old file name);
  4. adjacent string literals are joined first ("ucd_" "tables.inc" is one
     name), so a macro-built include name is caught once it is spelled out;
  5. a non-comment line naming `ucd_tables.c` (an `#include` of the module, or
     any reader of its text);
  6. in a Makefile, an `include`/`-include` directive or `-include`/`-imacros`
     flag on a line that names the generated file or `GEN_TABLES`, and any
     logical line naming the generated file other than the `GEN_TABLES :=`
     assignment or a comment;
  7. a Python/shell `glob` of `*.inc`.
The module must still include the generated file (else the wall guards
nothing).

WHAT A TEXT WALL CANNOT SEE (out of reach, each listed on purpose):
  - an `#include` of a macro whose value is built from non-adjacent pieces
    (96 legitimate `#include HEADER` uses exist, so a bare macro-include
    ban is not available);
  - a path assembled at run time (`os.path.join("src", "parse", name)`), a
    name split into string pieces the preprocessor/interpreter joins, or any
    `eval`: a text scan reads spelled-out names only;
  - a second decoder written from scratch (a LEB128 loop) that never names
    a table symbol or file -- it reads bytes it got from somewhere else;
  - a SECOND generated product under a new name: the needles are derived for
    THIS product.  The general form (a row table, product | owning module |
    interface header, one control per row) is plan row [CASE-TABLES-WALL];
  - a link-level fact (which object holds the blob): plan row, trigger the
    next bypass found in review.

POPULATION AND CONTROL.  The scan must READ (a) more than 500 files and (b)
every non-prose tracked file under src/, lib/ and cli/ (the floor is counted
from `git ls-files` itself, so dropping src/ from the list cannot pass), and
the derived needle must hold at least 15 symbols.  The control runs the WHOLE
pipeline (list generation, the scan, the report) a second time over a tree with
a planted include in mod_uprops.c and must report exactly that file.
"""
import fnmatch
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(sys.argv[1])
WORK = sys.argv[2] if len(sys.argv) > 2 else None

MODULE = "src/parse/ucd_tables.c"
HEADER = "src/parse/ucd_tables.h"
WRITER = "third_party/ucd-16.0.0/generate.py"

# Files that may name the table: the module, its product, its writer, the
# checker itself, the rows that PLANT these shapes, and the retired format's
# design record (docs/design/data_plan/formats.py measured the pair-array
# layout the charter's sizes came from; it parses a file path given on its
# command line and is dead against the live tree).  The Makefile is allowed
# only by the line rules in `scan_makefile`.
ALLOW = [
    MODULE, "src/parse/ucd_tables.inc", WRITER,
    "tests/core/ucd_wall_check.sh", "tests/core/ucd_wall_check.py",
    "tests/mech/sabotages/S357[5-9]_*", "tests/mech/sabotages/S358[7-9]_*",
    "tests/mech/sabotages/S359[0-2]_*",
    "tests/mech/sabotages/S-U12_bare_namespace_is_script.sh",
    "docs/design/data_plan/formats.py",
    # a FROZEN study (studies/CLAUDE.md) written against the retired
    # pcrec_uprops_* interface; never built by pcrec's make
    "studies/linktest_probe/pcre2_check_linked.c",
]
PROSE = (".md", ".txt", ".rst", ".tsv", ".csv", ".html", ".png", ".jpg",
         ".svg", ".pdf", ".gz", ".xz", ".bin", ".z", ".json")
SKIP_PREFIX = ("tools/review/out/", "worktrees/")


def read(path):
    with open(path, "rb") as f:
        text = f.read().decode("latin-1")
    text = text.replace("\\\r\n", "").replace("\\\n", "")
    # adjacent string literals ("ucd_" "tables.inc") are one name to the compiler
    return re.sub(r'"[ \t]*"', "", text)


def list_files(root):
    r = subprocess.run(["git", "-C", root, "ls-files", "-co",
                        "--exclude-standard"], capture_output=True, text=True)
    if r.returncode == 0:
        return [x for x in r.stdout.splitlines() if x]
    out = []
    for d, _dirs, fs in os.walk(root):
        for f in fs:
            out.append(os.path.relpath(os.path.join(d, f), root))
    return sorted(out)


def derive_needles(root):
    """(file-name regex, symbol regex, retired regex) from the module, its
    product and the module's own include line -- nothing typed here."""
    mod = read(os.path.join(root, MODULE))
    m = re.search(r'#\s*include\s+"([^"]+\.inc)"', mod)
    if not m:
        return None
    inc_name = os.path.basename(m.group(1))
    inc = read(os.path.join(root, os.path.dirname(MODULE), m.group(1)))
    stem = os.path.splitext(os.path.basename(MODULE))[0]
    syms = set(re.findall(r"\bucd_[a-z0-9_]+\b", inc))
    syms |= set(re.findall(r"\bUCD_GEN_[A-Z0-9_]+\b", inc))
    syms.discard(stem)
    priv = set(re.findall(r"(?m)^static\s[^;{(]*?\b(ucd_[a-z0-9_]+)\s*\(", mod))
    priv |= set(re.findall(r"\}\s*(Ucd[A-Za-z0-9_]*)\s*;", mod))
    names = re.compile(re.escape(inc_name))
    symre = re.compile(r"\b(?:%s)\b" % "|".join(sorted(map(re.escape, syms | priv))))
    # the RETIRED format's names cannot be derived from anything live: this
    # is the one hand list (the old pair-array interface, from its last tree)
    retired = re.compile(
        r"\bpcrec_uprop_(?:iv|names|names_n)\b|\bPCREC_UPROP_NS_\w*"
        r"|\bpcrec_uprops_(?:row_count|row_name|row_set|span|unicode_version)\b"
        r"|\bPCREC_UPROPS_UNICODE_VERSION\b|uprops_tables\.inc")
    return names, symre, retired, len(syms | priv), stem, inc_name


def is_comment(line):
    s = line.lstrip()
    if re.match(r"#\s*(include|define)\b", s):
        return False
    return s.startswith(("#", "//", "*", "/*", ";"))


def scan_makefile(text, names):
    bad = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#"):
            continue
        directive = re.match(r"-?include\b", s) or re.search(r"-(include|imacros)\b", s)
        if directive and (names.search(s) or "GEN_TABLES" in s):
            bad.append(line)
        elif names.search(s) and not re.match(r"GEN_TABLES\s*:?=", s):
            bad.append(line)
    return bad


def scan_file(rel, text, nd):
    names, symre, retired, _n, stem, _inc = nd
    if rel == "Makefile" or rel.endswith((".mk", "/Makefile")):
        if scan_makefile(text, names):
            return True
    body = text
    if rel == "Makefile":      # a Makefile comment may name the retired file
        body = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
    if symre.search(text) or retired.search(body):
        return True
    if rel != "Makefile" and names.search(text):
        return True
    for line in text.splitlines():
        if (stem + ".c") in line and not is_comment(line):
            return True
        if re.search(r"glob[^\n]*\*\.inc|\*\.inc[^\n]*glob", line):
            return True
    return False


def allowed(rel):
    return any(fnmatch.fnmatchcase(rel, p) for p in ALLOW)


def population(files):
    out = []
    for rel in files:
        if rel.endswith(PROSE) or rel.startswith(SKIP_PREFIX):
            continue
        if rel.startswith("build") or "/build" in rel[:12]:
            continue
        out.append(rel)
    return out


def run_scan(files, base, overlay, nd):
    """Offenders and the number of files read; `overlay` (a directory) wins
    over `base` for any file it holds (the control's planted copy)."""
    off, nread, in_prod = [], 0, 0
    for rel in population(files):
        if allowed(rel):
            continue
        path = os.path.join(overlay, rel) if overlay and os.path.isfile(
            os.path.join(overlay, rel)) else os.path.join(base, rel)
        if not os.path.isfile(path):
            continue
        nread += 1
        if rel.startswith(("src/", "lib/", "cli/")):
            in_prod += 1
        if scan_file(rel, read(path), nd):
            off.append(rel)
    return off, nread, in_prod


passed = failed = 0


def ok(msg):
    global passed
    print("PASS: " + msg)
    passed += 1


def bad(msg):
    global failed
    print("FAIL: " + msg)
    failed += 1


def main():
    nd = derive_needles(ROOT)
    if nd is None:
        bad("ucd wall: %s no longer includes a generated .inc -- the module is "
            "not the reader" % MODULE)
        return
    ok("ucd wall: %s includes %s" % (MODULE, nd[5]))
    if nd[3] < 15:
        bad("ucd wall: only %d symbols derived from the module and its product"
            " -- the needle has stopped looking (K35)" % nd[3])
    else:
        ok("ucd wall: needle derived from the product + module: %d symbols"
           % nd[3])

    files = list_files(ROOT)
    off, nread, in_prod = run_scan(files, ROOT, None, nd)
    want_prod = sum(1 for f in population(files)
                    if f.startswith(("src/", "lib/", "cli/"))
                    and not allowed(f) and os.path.isfile(os.path.join(ROOT, f)))
    if nread < 500 or in_prod != want_prod or want_prod < 100:
        bad("ucd wall: read %d files, %d of the %d under src/lib/cli -- the scan"
            " has stopped looking (K35)" % (nread, in_prod, want_prod))
    elif off:
        bad("ucd wall: files outside the module name the table's file or "
            "symbols: " + " ".join(off))
    else:
        ok("ucd wall: %d files read (%d under src/lib/cli, all of them), none "
           "outside the module + its writer names the table" % (nread, in_prod))

    # CONTROL: the whole pipeline again over a planted tree.  The planted
    # file is read through the overlay; the list is the real list.
    if WORK:
        plant = os.path.join(WORK, "plant")
        victim = "src/parse/mod_uprops.c"
        os.makedirs(os.path.join(plant, os.path.dirname(victim)), exist_ok=True)
        src = read(os.path.join(ROOT, victim))
        src = re.sub(r'(?m)^#include "ucd_tables\.h".*$',
                     '#include "%s"' % nd[5], src, count=1)
        with open(os.path.join(plant, victim), "w", encoding="latin-1") as f:
            f.write(src)
        coff, _n, _p = run_scan(list_files(ROOT), ROOT, plant, nd)
        if coff == [victim]:
            ok("ucd wall control: a planted include of the generated file, "
               "through the whole file list, is reported alone")
        else:
            bad("ucd wall control: the planted include was NOT reported "
                "exactly (got %r) -- the scan cannot fail" % coff)
    print("ucd_wall_check: %d passed, %d failed" % (passed, failed))


main()
sys.exit(1 if failed else 0)
