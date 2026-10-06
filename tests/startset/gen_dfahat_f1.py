#!/usr/bin/env python3
"""tests/startset/gen_dfahat_f1.py -- writes `dfahat_f1.rxt`, the ss3 D6
panel's BLOCKER sound-F1 witnesses (docs/dev/reviews/2026-10-06-r-ss3-panel.md):
seeded patterns where a byte of the start set `S` leaves every seed state
where it is, so `S & E*` dropped a start byte and the old `T == S` build
assertion refused them at default flags. With `T = S` the admission declines
them and the artifact is the deny arm's.

Every answer is libpcre2's (the edge lane's oracle, docs/design/startset/edge/
oracle.c, against the local libpcre2), at EVERY startpos of every subject; the
byte-tier blocks are also python-verified by the harness (verify_rxt.py).

    ORACLE=<built edge oracle> PCREC=build/pcrec python3 tests/startset/gen_dfahat_f1.py

Re-run only to add a witness; the output is committed and reviewed.
"""
import os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", ".."))
PCREC = os.environ.get("PCREC", os.path.join(TREE, "build", "pcrec"))
ORACLE = os.environ["ORACLE"]

# (pattern, rxt flags letters, why, subjects). The first six are the critic's
# witnesses (crit-soundness F1); the rest are the compile-only arm's own finds
# (tests/startset/compile_fuzz.py on the pre-fix compiler), one per shape.
W = [
    (r"(?<=\w) *a", "", "S = {' ', a}: a space keeps the non-word seed AND the word-context thread in ` *`; the hand-twin with T = {a} lost (1,3) on \"x a\"",
     ["x a", "x  a", " a", "a", "xa", "x ", "-- a", "x ab a", "  x a"]),
    (r"(?<=\w)-*a", "", "the same shape over `-`",
     ["x-a", "x--a", "-a", "xa", "--a x-a", "a-a"]),
    (r"(?<=\w) *(?:and|or)\b", "", "the realistic spelling: a word, spaces, a keyword",
     ["cat and dog", "x or", "x  andy or", "and", "x orb or", "ab  or "]),
    (r"(?<!\s) *[a-z]", "", "a negative lookbehind's twin",
     [" a", "x a", "  a", "a", "\tb x", "- -c"]),
    (r"(?<=[ab])\W*?b", "", "193 bytes of S dropped (every non-word byte)",
     ["a b", "a--b", "b", "xb", "a  -b", "c b ab", "bb"]),
    (r"(?<=\w) *(a)", "", "the VM hybrid's prefilter carried the same refusal",
     ["x a", "x  a", " a", "xa", "a a"]),
    (r"(?<!\W) *-", "", "found under -fprefilter-collapse; plain here, collapsed by run_dfahat_checks.sh's second fixture pass",
     ["x -", "x  -", " -", "-", "a-", "--"]),
    (r"(?<![a-])(?<!\W)[ab]*?(?:ab|b)+", "u", "found under --ucp",
     ["xab", "-ab", "cab ab", "b", "ab", "x b"]),
    (r"\b\d*b+", "", "a \\b seed: a digit loop keeps both seeds",
     ["1b", "x 12bb", "b", "a1b", "1 b", "11"]),
    (r"(?<=\s)a*?\n", "", "a lazy loop before a newline",
     [" \n", "x a\n", " aa\n", "\n", "a\n a\n"]),
    (r"(?<=\w)\W*x\b", "", "193 bytes of S dropped, with a trailing \\b",
     ["a x", "a--x", "x", "a xy x", "ax"]),
    (r"(?<=\w)\s*?a", "i", "under -i (both cases of `a` in S)",
     ["x A", "x  a", " a", "xa", "B\ta"]),
]


def esc(s):
    out = []
    for c in s.encode():
        if c == 0x22: out.append('\\"')
        elif c == 0x5c: out.append("\\\\")
        elif c == 0x0a: out.append("\\n")
        elif c == 0x0d: out.append("\\r")
        elif c == 0x09: out.append("\\t")
        elif 0x20 <= c < 0x7f: out.append(chr(c))
        else: out.append("\\x%02x" % c)
    return "".join(out)


def ncaps(pat, flags):
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as d:
        cmd = [PCREC, "--features", "all", "-p", "rx", "-o", os.path.join(d, "o.c"), "--pattern", pat]
        if "i" in flags: cmd.append("-i")
        if "u" in flags: cmd.append("--ucp")
        subprocess.run(cmd, check=True, capture_output=True)
        return int(re.search(r"#define RX_NCAPS (\d+)", open(os.path.join(d, "o.h")).read()).group(1))


def main():
    qs, keys = [], []
    for bi, (pat, fl, _, subs) in enumerate(W):
        opts = "".join(c for c in fl if c in "iu") or "-"
        for si, s in enumerate(subs):
            for p in range(len(s.encode()) + 1):
                k = "%d.%d.%d" % (bi, si, p)
                qs.append("%s\t%s\t%s\t%s\t%d" % (k, opts, pat.encode().hex(), s.encode().hex(), p))
    r = subprocess.run([ORACLE], input="\n".join(qs) + "\n", capture_output=True, text=True, check=True)
    A, ver = {}, None
    for l in r.stdout.splitlines():
        if l.startswith("# pcre2"): ver = l.split()[2]; continue
        k, _, v = l.partition("\t"); A[k] = v
    out = ["# tests/startset/dfahat_f1.rxt -- [START-SET] stage 3: the ss3 D6 panel's BLOCKER",
           "# sound-F1 witnesses (docs/dev/reviews/2026-10-06-r-ss3-panel.md). A byte of the",
           "# start set S leaves every seed state where it is, so `S & E*` dropped a start",
           "# byte and the old `T == S` build assertion REFUSED these at default flags while",
           "# -fno-start-set compiled them. With T = S the admission declines (the byte is",
           "# outside E): each block must COMPILE, and tests/startset/dfahat_checks.py's",
           "# [dfa-deny] holds its artifact byte-identical to the deny arm's.",
           "#",
           "# GENERATED by tests/startset/gen_dfahat_f1.py; every answer is libpcre2's (local",
           "# %s), at every startpos. Byte-tier blocks are python-verified as well; the" % ver,
           "# `flags u` block is libpcre2-only (python has no UCP).", ""]
    for bi, (pat, fl, why, subs) in enumerate(W):
        nc = ncaps(pat, fl)
        out.append("# " + why)
        out.append("pattern " + pat)
        out.append("features all")
        if fl: out.append("flags " + fl)
        for si, s in enumerate(subs):
            for p in range(len(s.encode()) + 1):
                f = A["%d.%d.%d" % (bi, si, p)].split()
                if f[0] == "0": out.append('ns %d "%s"' % (p, esc(s)))
                elif f[0] == "1":
                    out.append('ms %d "%s" %s %s' % (p, esc(s), f[1], f[2]))
                    for g in range(1, nc):
                        out.append("g %d %s %s" % (g, f[1 + 2 * g], f[2 + 2 * g]))
                else: raise SystemExit("unexpected oracle answer %r for %r" % (f, (pat, s, p)))
        out.append("")
    open(os.path.join(HERE, "dfahat_f1.rxt"), "w").write("\n".join(out))


if __name__ == "__main__":
    main()
