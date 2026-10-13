#!/usr/bin/env python3
"""tests/endmark/b3diff.py -- D164 B3 (lane b3build): the BUILT compiler's
answers against libpcre2 10.46 (endmark.md §R.6.2: "the twins' libpcre2
differentials re-run against the BUILT compiler").

For each pattern (one per line of PATFILE: `pattern<TAB>utf8|byte`, or a bare
pattern = byte), every arm in ARMS (a space-separated pcrec flag set; `-` is the
default build) is compiled by PCREC into one TU with a driver that calls
`<p>_search` at EVERY start position (every character boundary under utf8) of
every subject, group spans included. libpcre2 answers the same cells through
docs/design/endmark/pcre2.py (options UTF under utf8). A cell differs when the
whole-match span or any group span differs. Subjects: every string up to
LEN over the alphabet `ab \\n1x/` (byte) or `aé \\n` (utf8), plus the
pattern's own literal bytes.

Usage: b3diff.py PCREC PATFILE SCRATCH [--len N] [--arms "ARM1|ARM2"]
Exit 1 on any difference; prints one summary line per arm and the first
differences."""
import itertools, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "docs", "design", "endmark"))
import pcre2  # noqa: E402

DRIVER = r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "rx.h"
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "rb");
    int utf8 = argv[2][0] == 'u';
    unsigned long len;
    static unsigned char buf[1 << 16];
    ptrdiff_t caps[RX_NCAPS][2];
    while (fscanf(f, "%lu:", &len) == 1) {
        if (len) fread(buf, 1, len, f);
        fgetc(f);
        for (unsigned long sp = 0; sp <= len; sp++) {
            if (utf8 && sp < len && buf[sp] >= 0x80 && buf[sp] <= 0xBF) continue;
            int rc = rx_search(buf, len, sp, caps);
            printf("%lu", sp);
            if (rc == 1) for (int g = 0; g < RX_NCAPS; g++)
                printf(" %td %td", caps[g][0], caps[g][1]);
            else if (rc == 0) printf(" -");
            else printf(" E%d", rc);
            putchar('\n');
        }
        puts("#");
    }
    return 0;
}
'''

def subjects(pat, utf8, maxlen):
    alpha = ["a", "é", " ", "\n"] if utf8 else ["a", "b", " ", "\n", "1", "x", "/"]
    out = set()
    for n in range(maxlen + 1):
        for t in itertools.product(alpha, repeat=n):
            out.add("".join(t))
    lits = "".join(ch for ch in pat if ch.isalnum() or ch in "./_-")[:6]
    if lits:
        for p in ["", "a", "\n"]:
            for s in ["", "\n", "\n\n", " \n"]:
                out.add(p + lits + s)
    return sorted(out, key=lambda s: (len(s), s))

def run(pcrec, pat, utf8, arm, subs, scratch):
    os.makedirs(scratch, exist_ok=True)
    flags = [] if arm == "-" else arm.split()
    args = [pcrec, "-p", "rx", "-o", os.path.join(scratch, "rx.c"), "--features", "all"]
    if utf8: args += ["-e", "utf8"]
    r = subprocess.run(args + flags + ["--pattern", pat], capture_output=True, timeout=120)
    if r.returncode != 0:
        return None, r.stderr.decode(errors="replace").strip()
    with open(os.path.join(scratch, "drv.c"), "w") as h:
        h.write(DRIVER)
    exe = os.path.join(scratch, "drv")
    r = subprocess.run(["gcc", "-O1", "-w", "-I", scratch, "-o", exe,
                        os.path.join(scratch, "drv.c"), os.path.join(scratch, "rx.c")],
                       capture_output=True, timeout=300)
    if r.returncode != 0:
        return None, "gcc: " + r.stderr.decode(errors="replace")[:400]
    sf = os.path.join(scratch, "subj")
    with open(sf, "wb") as h:
        for s in subs:
            b = s.encode("utf-8")
            h.write(b"%d:" % len(b) + b + b"\n")
    r = subprocess.run([exe, sf, "u" if utf8 else "b"], capture_output=True, timeout=600)
    res, cur = [], []
    for line in r.stdout.decode().split("\n"):
        if line == "#":
            res.append(cur); cur = []
        elif line:
            v = line.split()
            sp = int(v[0])
            if v[1] == "-": cur.append((sp, None))
            elif v[1].startswith("E"): cur.append((sp, "give-up " + v[1]))
            else: cur.append((sp, [(int(v[i]), int(v[i + 1])) for i in range(1, len(v), 2)]))
    return res, None

def main():
    pcrec, patfile, scratch = sys.argv[1:4]
    maxlen, arms = 4, ["-"]
    rest = sys.argv[4:]
    while rest:
        if rest[0] == "--len": maxlen = int(rest[1]); rest = rest[2:]
        elif rest[0] == "--arms": arms = rest[1].split("|"); rest = rest[2:]
        else: sys.exit("unknown argument " + rest[0])
    pats = []
    for line in open(patfile, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"): continue
        v = line.split("\t")
        pats.append((v[0], len(v) > 1 and v[1] == "utf8"))
    bad = 0
    for arm in arms:
        cells = diffs = refused = 0
        for pat, utf8 in pats:
            subs = subjects(pat, utf8, maxlen)
            got, err = run(pcrec, pat, utf8, arm, subs, scratch)
            if got is None:
                refused += 1
                print("  [%s] %r refused: %s" % (arm, pat, err[:200]))
                continue
            code = pcre2.Code(pat, utf=utf8)
            for s, ans in zip(subs, got):
                b = s.encode("utf-8")
                for sp, mine in ans:
                    cells += 1
                    ref = code.match(b, sp)
                    if mine is not None and not isinstance(mine, str):
                        mine = mine[:len(ref)] if ref else mine
                    if ref != mine:
                        diffs += 1
                        if diffs <= 8:
                            print("  DIFF [%s] %r utf8=%s subj=%r sp=%d pcrec=%s pcre2=%s"
                                  % (arm, pat, utf8, s, sp, mine, ref))
        print("b3diff arm %-28s patterns %d refused %d cells %d DIFF %d"
              % (arm, len(pats), refused, cells, diffs))
        bad += diffs
    sys.exit(1 if bad else 0)

main()
