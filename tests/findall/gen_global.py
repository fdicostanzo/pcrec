#!/usr/bin/env python3
# tests/findall/gen_global.py -- [FINDALL-NEXT] writes global.rxt, the `mg`
# corpus (rxt_format.md §1.7.1), FROM libpcre2's answers, never pcrec's.
#
# THE COUNTS ARE INDEPENDENT of the iterator differential (iterchk, CHK-8):
# each is libpcre2's own global iteration, read as the match count of
# `pcre2_substitute(.., PCRE2_SUBSTITUTE_GLOBAL, replacement "")` in a small
# oracle program this script writes and builds (no hand-written loop, no
# artifact, nothing of iter_drv.c). For every byte group of cells.tsv it
# writes one block: an `mg` line per subject with that count and, where the
# artifact cannot report an empty span (iter_drv.c's L == I on the artifact:
# the `_ITER_RETRY "none"` stamp), an `mc` line with the same count (the
# §3.1.3 loop must agree; elsewhere `mc` is the corpus's existing protocol
# question and stays with the files that ask it). iter_drv.c's `G=` field is
# read for one thing only, the cell's skip rule (a subject libpcre2's loop
# refuses); the generator also cross-checks the substitute count against it
# and stops on a disagreement. The `# pcre2-only` marking is COMPUTED: a
# block carries it where python `re.finditer` cannot compile the pattern or
# disagrees on any subject (the first such subject is named on stderr).
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

ORACLE_C = r"""
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* usage: g_count PATTERN < hex-subject lines; prints, per line, the number of
 * matches pcre2_substitute(GLOBAL, "") makes, or -1 (error). */
int main(int argc, char **argv)
{
    static char line[1 << 16];
    static unsigned char s[1 << 15], out[1 << 15];
    int ec; PCRE2_SIZE eo;
    pcre2_code *re = pcre2_compile((PCRE2_SPTR)argv[1], strlen(argv[1]), 0, &ec, &eo, NULL);
    while (fgets(line, sizeof line, stdin)) {
        size_t n = 0, l = strcspn(line, "\n");
        for (size_t i = 0; i + 1 < l; i += 2) {
            char h[3] = { line[i], line[i + 1], 0 };
            s[n++] = (unsigned char)strtoul(h, NULL, 16);
        }
        PCRE2_SIZE ol = sizeof out;
        int rc = re ? pcre2_substitute(re, s, n, 0, PCRE2_SUBSTITUTE_GLOBAL, NULL, NULL,
                                       (PCRE2_SPTR)"", 0, out, &ol) : -1;
        printf("%d\n", rc);
    }
    return 0;
}
"""

blocks = []
with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as d:
    oc = os.path.join(d, "g_count.c")
    open(oc, "w").write(ORACLE_C)
    oracle = os.path.join(d, "g_count")
    subprocess.run([CC, "-O1", oc, "-lpcre2-8", "-o", oracle], check=True)
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
        cnt = subprocess.run([oracle, pat], input="".join(unesc(s).encode("latin-1").hex() + "\n" for s in subjs),
                             capture_output=True, text=True, check=True).stdout.split()
        try:
            py = re.compile(pat)
        except re.error:
            py = None
        only = py is None
        lines = []
        for s, row, c in zip(subjs, out.splitlines(), cnt):
            f = dict(x.split("=", 1) for x in row.split("\t")[1:4])
            if f["G"] == "-":
                continue
            g = int(c)
            if g != len(re.findall(r"\(", f["G"])):
                sys.exit("gen_global: %r on %r: substitute count %d, iter_drv G= %s" % (pat, s, g, f["G"]))
            sv = unesc(s)
            if py is not None and sum(1 for _ in py.finditer(sv)) != g and not only:
                only = True
                print("gen_global: pcre2-only: %r on %r (libpcre2 %d, python differs)" % (pat, s, g), file=sys.stderr)
            lines.append("mg %s %d" % (rxt_quote(sv), g))
            if retry == "0":
                lines.append("mc %s %d" % (rxt_quote(sv), g))
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
