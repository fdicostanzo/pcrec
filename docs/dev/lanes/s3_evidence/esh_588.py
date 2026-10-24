#!/usr/bin/env python3
"""docs/dev/lanes/s3_evidence/esh_588.py -- a D-hors site's EXPECTED SHIFT under the byte-rate prior
(job 588's "D-hors admission (E[sh])" reading; Frank's ruling 2026-10-23 on the S3 review's fix C:
measure D-hors's admission instead of declining on max(sh) == 1).

    python3 -I esh_588.py --pcrec BIN [--prior PPM.tsv] PATTERN...     one TSV row per pattern
    import esh_588; esh_588.site(bin, pattern_bytes, prior)            the same, as a dict

For the pattern's DEFAULT artifact (`-p rx --features all`), from pcrec's own text alone:
  sh[256]   the file-scope D-hors table `rx_mf<N>_sh[256]` (absent: the site is not D-hors)
  E[sh]     sum over bytes b of rate[b] * sh[b] / 1e6: the expected skip per probe when the probed
            byte is drawn from the prior (1.000 exactly where every shift is 1)
  max(sh)   the table's largest shift
  stop      the stop set D-one finds: the `--memfn=no-window-skip` artifact's E-find walk condition
            (`while (c < n && !(COND)) c++`) for the same rx_mf<N>, evaluated by gcc over all 256
            bytes inside a copy of that artifact (so any table it reads is in scope); or the byte
            of a `memchr(` find
  mass      sum over the stop set of rate[b], capped at 1e6: presence.c kit_set_mass's arithmetic,
            the quantity D-hors's HORS_MIN admission reads
The PRIOR is tests/findings/default_ppm.tsv (byte, ppm; sums to 1e6): the default byte-rate the kit
reads (src/findings/default.rxt normalizes to it).
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.normpath(os.path.join(here, "../../../.."))
PRIOR = os.path.join(TREE, "tests/findings/default_ppm.tsv")


def prior(path=PRIOR):
    rate = [0] * 256
    for ln in open(path):
        if ln.strip() and not ln.startswith("#"):
            b, p = ln.split()[:2]
            rate[int(b)] = int(p)
    return rate


def compile_c(bin_, pat, outdir, tag, *flags):
    c = os.path.join(outdir, tag + ".c")
    r = subprocess.run([bin_, "-p", "rx", "--features", "all", *flags, "-o", c, "--pattern", pat],
                       capture_output=True, timeout=60)
    return c if r.returncode == 0 else None


def balanced(text, i):
    """The text of the parenthesized group opening at text[i] == '(' (exclusive), and its end."""
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
            if depth == 0:
                return text[i + 1:j], j
    return None, -1


def stop_set(c_path, n, outdir):
    """The stop set (256 bools) of rx_mf<n>'s D-one walk in the artifact at c_path, or None."""
    text = open(c_path, encoding="latin-1").read()
    s, c = "rx_mf%d_s" % n, "rx_mf%d_c" % n
    m = re.search(r"memchr\(%s \+ %s, (\d+)," % (s, c), text)
    if m:
        return [b == int(m.group(1)) for b in range(256)]
    key = "while (%s < rx_mf%d_n && !" % (c, n)
    i = text.find(key)
    if i < 0:
        return None
    cond, _ = balanced(text, i + len(key))
    if cond is None:
        return None
    ev = os.path.join(outdir, "stop_eval.c")
    with open(ev, "w", encoding="latin-1") as f:
        f.write(text)
        f.write("\n#include <stdio.h>\nstatic int esh_stop(unsigned char x)\n{\n"
                "    const unsigned char *%s = &x; size_t %s = 0;\n    return %s;\n}\n"
                "int main(void)\n{\n    for (int b = 0; b < 256; b++) putchar(esh_stop((unsigned char)b) ? '1' : '0');\n"
                "    putchar('\\n');\n    return 0;\n}\n" % (s, c, cond))
    exe = os.path.join(outdir, "stop_eval")
    r = subprocess.run(["gcc", "-O0", "-w", "-I", outdir, "-o", exe, ev], capture_output=True, timeout=120)
    if r.returncode != 0:
        return None
    out = subprocess.run([exe], capture_output=True, timeout=30).stdout.decode().strip()
    return [ch == "1" for ch in out] if len(out) == 256 else None


def site(bin_, pat, rate):
    """{hors, esh, maxsh, mass, why} for one pattern (bytes)."""
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as d:
        c = compile_c(bin_, pat, d, "a")
        if c is None:
            return {"hors": 0, "why": "compile failed"}
        text = open(c, encoding="latin-1").read()
        m = re.search(r"static const unsigned char rx_mf(\d+)_sh\[256\] = \{([^}]*)\}", text)
        if not m:
            return {"hors": 0, "why": "no _sh[256] table (not D-hors)"}
        n = int(m.group(1))
        sh = [int(x) for x in m.group(2).split(",")]
        if len(sh) != 256:
            return {"hors": 0, "why": "a malformed _sh table"}
        esh = sum(rate[b] * sh[b] for b in range(256)) / 1e6
        c1 = compile_c(bin_, pat, d, "noh", "--memfn=no-window-skip")
        st = stop_set(c1, n, d) if c1 else None
        if st is None:
            return {"hors": 1, "esh": esh, "maxsh": max(sh), "mass": None, "why": "stop set not read"}
        mass = min(1000000, sum(rate[b] for b in range(256) if st[b]))
        return {"hors": 1, "esh": esh, "maxsh": max(sh), "mass": mass, "nstop": sum(st), "why": ""}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pcrec", required=True)
    ap.add_argument("--prior", default=PRIOR)
    ap.add_argument("patterns", nargs="+")
    a = ap.parse_args()
    rate = prior(a.prior)
    print("#pattern\thors\tE[sh]\tmax(sh)\tstop_mass_ppm\tstop_bytes\twhy")
    for p in a.patterns:
        r = site(a.pcrec, p.encode("latin-1"), rate)
        print("%s\t%d\t%s\t%s\t%s\t%s\t%s" % (
            p, r["hors"], "%.3f" % r["esh"] if "esh" in r else "-", r.get("maxsh", "-"),
            r["mass"] if r.get("mass") is not None else "-", r.get("nstop", "-"), r["why"]))


if __name__ == "__main__":
    sys.exit(main())
