#!/usr/bin/env python3
# tests/findall/gen_global.py -- [FINDALL-NEXT] writes global.rxt, the `mg`
# corpus (rxt_format.md §1.7.1), FROM libpcre2's answers, never pcrec's.
#
# For every byte group of cells.tsv it compiles the pattern once (to build
# iter_drv.c, whose `G=` field is libpcre2's global loop and `L=` field is
# match_api.md §3.1.3's loop over the artifact), and writes one block: an
# `mg` line per subject with libpcre2's global count and an `mc` line with
# the loop's count where the artifact cannot report an empty span (there the
# two counts are equal; elsewhere `mc` is the corpus's existing protocol
# question and stays with the files that ask it). The `# pcre2-only` marking
# is COMPUTED: a block carries it where python `re.finditer` cannot compile
# the pattern or disagrees on any subject.
#
# usage: python3 -I gen_global.py PCREC_BIN CC OUT.rxt   (run from the tree root)
import os
import re
import subprocess
import sys
import tempfile

PCREC, CC, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
HERE = os.path.dirname(os.path.abspath(__file__))


def unesc(s):
    out, i = [], 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            c = s[i + 1]
            if c in "tnr\\":
                out.append({"t": "\t", "n": "\n", "r": "\r", "\\": "\\"}[c]); i += 2; continue
            if c == "x" and i + 3 < len(s):
                out.append(chr(int(s[i + 2:i + 4], 16))); i += 4; continue
        out.append(s[i]); i += 1
    return "".join(out)


def rxt_quote(s):
    o = []
    for ch in s:
        b = ord(ch)
        if ch == '"': o.append('\\"')
        elif ch == "\\": o.append("\\\\")
        elif ch == "\n": o.append("\\n")
        elif ch == "\t": o.append("\\t")
        elif ch == "\r": o.append("\\r")
        elif b < 0x20 or b > 0x7E: o.append("\\x%02x" % b)
        else: o.append(ch)
    return '"' + "".join(o) + '"'


groups = {}
for ln in open(os.path.join(HERE, "cells.tsv"), encoding="latin-1"):
    ln = ln.rstrip("\n")
    if not ln or ln.startswith("#"):
        continue
    enc, flags, pat, subj = ln.split("\t")
    if enc == "byte" and not flags:
        groups.setdefault(pat, []).append(subj)

blocks = []
with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as d:
    for pat, subjs in groups.items():
        c = os.path.join(d, "rx.c")
        if subprocess.run([PCREC, "--features", "all", "-p", "rx", "-o", c, "--pattern", pat],
                          capture_output=True).returncode:
            continue
        retry = "0" if '_ITER_RETRY "none"' in open(c).read() else "1"
        drv = os.path.join(d, "drv")
        subprocess.run([CC, "-O1", "-DPFX=rx", "-DPFXU=RX", '-DHDR="rx.h"', "-I", d, c,
                        os.path.join(HERE, "iter_drv.c"), "-lpcre2-8", "-o", drv], check=True)
        out = subprocess.run([drv, pat, "byte", retry], input="".join(s + "\n" for s in subjs),
                             capture_output=True, text=True, encoding="latin-1", check=True).stdout
        try:
            py = re.compile(pat)
        except re.error:
            py = None
        only = py is None
        lines = []
        for s, row in zip(subjs, out.splitlines()):
            f = dict(x.split("=", 1) for x in row.split("\t")[1:4])
            if f["G"] == "-":
                continue
            g = len(re.findall(r"\(", f["G"]))
            sv = unesc(s)
            if py is not None and sum(1 for _ in py.finditer(sv)) != g:
                only = True
            lines.append("mg %s %d" % (rxt_quote(sv), g))
            if retry == "0":
                lines.append("mc %s %d" % (rxt_quote(sv), len(re.findall(r"\(", f["L"]))))
        blocks.append((pat, only, lines))

with open(OUT, "w", encoding="latin-1") as o:
    o.write("# tests/findall/global.rxt -- [FINDALL-NEXT] the `mg` corpus (rxt_format.md\n"
            "# section 1.7.1): libpcre2 10.46's GLOBAL count per subject, checked through\n"
            "# <prefix>_next. Written by tests/findall/gen_global.py from libpcre2's\n"
            "# answers; `# pcre2-only` is computed (python re.finditer cannot compile\n"
            "# the pattern or disagrees). `mc` lines sit where the pattern cannot\n"
            "# report an empty span, so the two counts must agree. Regenerate:\n"
            "#   python3 -I tests/findall/gen_global.py build/pcrec cc tests/findall/global.rxt\n")
    for pat, only, lines in blocks:
        o.write("\n")
        if only:
            o.write("# pcre2-only\n")
        o.write("pattern %s\nfeatures all\n" % pat)
        o.write("".join(l + "\n" for l in lines))
print("gen_global: %d blocks" % len(blocks))
