#!/usr/bin/env python3
"""docs/dev/lanes/s3_evidence/diff_r2.py -- the widened PAIR's answer differential (code
review r2 R2-1, lane s3pair): generated window patterns whose stop is a TWO-BYTE set (any two
bytes: a non-cube pair, a case pair outside a run stretch, a pair in a lookaround), compiled by
pcrec at both layers, every artifact built with AddressSanitizer + UBSan, and a find-all over
generated subjects compared with Python `re` (bytes patterns: ASCII semantics, as pcrec's byte
encoding).

    python3 -I diff_r2.py --pcrec BIN --out DIR [--patterns N] [--subjects K] [--seed S]

THE POPULATION is counted from each artifact's OWN text, never assumed: a pattern is a WITNESS
iff its default artifact reads `RX_DFA_SCAN "cover"` and renders B-pair (`_mfN_ha < `); the
tally prints witnesses / patterns and the cases over witnesses, and the run FAILS when the
witness cases are fewer than 1,000 (K35: a population nobody counts). A pattern that is not a
witness is still compared (a control).
Find-all: from p = 0, search at p; on a match [s, e) record it and continue at s + 1; else stop.
Python's `Pattern.search(subject, p)` reads lookbehind and \\b context before p, as rx_search does.
Trailer: `== diff_r2 COMPLETE: patterns=P witnesses=W cases=C witness_cases=WC bad=B`; exit 0
iff B == 0 and WC >= 1000.
"""
import argparse
import os
import random
import re
import subprocess
import sys

COMMON = "eatoinsr"           # frequent English letters: never the stop
RARE = "qjxzkvQJXZ-:[]#@"      # two of these make the stop

DRIVER = r"""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int hexv(int c) { return c <= '9' ? c - '0' : c - 'a' + 10; }
int main(void)
{
    static char line[8192];
    static unsigned char s[4096];
    while (fgets(line, sizeof line, stdin)) {
        size_t n = 0;
        for (char *p = line; p[0] && p[1] && p[0] != '\n'; p += 2) s[n++] = (unsigned char)(hexv(p[0]) * 16 + hexv(p[1]));
        unsigned char *b = malloc(n ? n : 1);
        memcpy(b, s, n);
        size_t pos = 0;
        while (pos <= n) {
            ptrdiff_t caps[RX_NCAPS][2] = {{0}};
            int rc = rx_search(b, n, pos, caps);
            if (rc != 1) { if (rc != 0) printf("rc%d ", rc); break; }
            printf("%td-%td ", caps[0][0], caps[0][1]);
            pos = (size_t)caps[0][0] + 1;
        }
        printf("\n");
        free(b);
    }
    return 0;
}
"""


def esc(ch):
    return re.escape(ch)


def pair(rng):
    a, b = rng.sample(RARE, 2)
    return a, b


def cls(a, b):
    body = "".join("\\" + c if c in "-:[]^\\" else c for c in (a, b))
    return "[" + body + "]"


def gen_pattern(rng):
    """One window pattern with a two-byte set somewhere and frequent literals elsewhere."""
    a, b = pair(rng)
    if rng.random() < 0.25:                 # a case pair, often outside a run stretch
        c = rng.choice("qjxzkv")
        a, b = c, c.upper()
    kind = rng.choice(["core", "core", "core", "ahead", "behind", "word", "case"])
    left = "".join(rng.choice(COMMON) for _ in range(rng.randint(0, 3)))
    right = "".join(rng.choice(COMMON) for _ in range(rng.randint(0, 3)))
    if kind == "core":
        mid = cls(a, b)
        if rng.random() < 0.3:
            mid += rng.choice(["\\d", "[a-f]", ".", "[^q]"])
        return left + mid + right
    if kind == "ahead":
        return (left + right or rng.choice(COMMON)) + "(?=" + cls(a, b) + ")"
    if kind == "behind":
        return "(?<=" + cls(a, b) + ")" + (left + right or rng.choice(COMMON))
    if kind == "word":
        return "\\b" + left + cls(a, b) + right + "\\b"
    c = rng.choice("qjxzkv")
    return "(?i)" + left + c + right + rng.choice(["\\b", "(?=[0-9])", "[0-9]", ""])


def gen_subject(rng, pat_bytes):
    n = rng.randint(0, 40)
    pool = list(COMMON + RARE + " 019") + [chr(0xC4), chr(0xE4)]
    s = [rng.choice(pool) for _ in range(n)]
    if pat_bytes and n and rng.random() < 0.6:          # plant pattern-like bytes
        k = rng.randrange(n)
        lit = [c for c in pat_bytes if c.isalnum() or c in RARE]
        for j, c in enumerate(lit[: n - k]):
            s[k + j] = c
    return "".join(s).encode("latin-1")


def py_findall(rx, subj):
    out, pos = [], 0
    while pos <= len(subj):
        m = rx.search(subj, pos)
        if not m:
            break
        out.append("%d-%d" % m.span())
        pos = m.start() + 1
    return " ".join(out) + (" " if out else "")


def run(argv, **kw):
    return subprocess.run(argv, capture_output=True, **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pcrec", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--patterns", type=int, default=120)
    ap.add_argument("--subjects", type=int, default=30)
    ap.add_argument("--seed", type=int, default=20261023)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    os.makedirs(a.out, exist_ok=True)
    drv = os.path.join(a.out, "driver.inc")
    with open(drv, "w") as f:
        f.write(DRIVER)
    pats, seen = [], set()
    while len(pats) < a.patterns:
        p = gen_pattern(rng)
        if p not in seen:
            seen.add(p)
            pats.append(p)
    witnesses = cases = wcases = bad = 0
    for i, p in enumerate(pats):
        try:
            rx = re.compile(p.encode("latin-1"))
        except re.error:
            continue
        subs = [gen_subject(rng, p) for _ in range(a.subjects)]
        want = [py_findall(rx, s) for s in subs]
        feed = "".join(s.hex() + "\n" for s in subs).encode()
        is_w = False
        for layer, flags in (("off", []), ("simd", ["-fmemfn-simd"])):
            c = os.path.join(a.out, "p%d_%s.c" % (i, layer))
            r = run([a.pcrec, "-p", "rx", "--features", "all"] + flags + ["-o", c, "--pattern", p])
            if r.returncode:
                print("COMPILE-REFUSED %r %s: %s" % (p, layer, r.stderr.decode()[:200]))
                bad += 1
                continue
            text = open(c, "rb").read()
            if layer == "off":
                is_w = b'RX_DFA_SCAN "cover"' in text and re.search(rb"_mf\d+_ha < ", text) is not None
            with open(c, "a") as f:
                f.write('\n#include "driver.inc"\n')
            exe = c[:-2]
            r = run(["gcc", "-std=gnu11", "-O1", "-march=native", "-g", "-fsanitize=address,undefined",
                     "-fno-sanitize-recover=all", "-I", a.out, "-o", exe, c])
            if r.returncode:
                print("GCC-FAILED %r %s: %s" % (p, layer, r.stderr.decode()[:300]))
                bad += 1
                continue
            r = run([exe], input=feed, timeout=60)
            got = r.stdout.decode().split("\n")[:len(subs)]
            if r.returncode:
                print("RUN-FAILED %r %s rc=%d: %s" % (p, layer, r.returncode, r.stderr.decode()[:300]))
                bad += 1
                continue
            for s, w, g in zip(subs, want, got):
                cases += 1
                wcases += is_w
                if w != g:
                    bad += 1
                    print("DIFF %r %s subject=%s want=%r got=%r" % (p, layer, s.hex(), w, g))
        witnesses += is_w
        print("%s\t%s" % ("WITNESS" if is_w else "control", p))
    ok = bad == 0 and wcases >= 1000
    print("== diff_r2 COMPLETE: patterns=%d witnesses=%d cases=%d witness_cases=%d bad=%d"
          % (len(pats), witnesses, cases, wcases, bad))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
