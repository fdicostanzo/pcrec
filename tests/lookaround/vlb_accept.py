#!/usr/bin/env python3
"""tests/lookaround/vlb_accept.py — gate 3 of [VLOOKBEHIND] stage 1
(docs/design/vlookbehind.md §6 gate 3): pcrec's lookbehind ACCEPT SET stays
inside libpcre2 10.46's, and pcrec's per-branch "one length" judgment equals
libpcre2's own at `max_varlookbehind = 0`.

Two checks over one generated population (K35: counted, pinned by the caller):

  ACCEPT   every pattern pcrec compiles, libpcre2 (default compile context,
           max_varlookbehind 255) compiles. One stated divergence: an
           unbounded repeat of a ZERO-WIDTH body inside a lookbehind branch
           (`(?:)*`, `(?:\\b)*`, ...), which pcrec accepts and libpcre2 refuses
           with err 125 (pattern_language.md §7.4). Those cells are IN the
           population, classified by the generator (never by either answer)
           and counted on their own line.
  CLASSIFY for every pattern both accept (the divergent class excluded),
           pcrec's judgment that some lookbehind branch VARIES (a `width
           LO..HI` branch label in `--emit-ir`, role text 1) holds exactly when
           libpcre2 refuses the pattern at max_varlookbehind = 0. libpcre2 at 0
           accepts exactly the lookbehinds with no varying branch, so this is
           the independent check that pcrec's width range is exact (§5.2).

Also counted, never failed: patterns libpcre2 accepts and pcrec refuses (the
stage-2 backreference rows), so a growing gap is visible.

Usage: vlb_accept.py <pcrec>     (needs PCREC_PCRE2_PATH like every oracle user)
Prints `vlb_accept: total=N both=N divergent=N pcre2only=N bad=N` on the last
line; every bad cell above it. Exit 1 on any bad cell.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "docs", "design",
                                "eng_brep_measurements", "probes"))
import pcre2_ctypes as P                                    # noqa: E402

FEATS = ("lookaround,backrefs,atomic-groups,assertions,classes,modifiers,"
         "named-groups,recursion")
VARIES = re.compile(r"\blookbehind branch \d+ of \d+, width \d+\.\.\d+")

SPELL = ["(?<=%s)x", "(?<!%s)x", "(?<*%s)x", "(*naplb:%s)x"]

# (body, zero-width-unbounded-repeat?) — the class is declared HERE, by shape.
BODIES = [
    ("a", False), ("ab", False), ("a|bc", False), ("ab|cd", False),
    ("a{2}", False), ("a{1,2}", False), ("a{0,2}", False), ("a?", False),
    ("ab?", False), ("(a|bc)", False), ("(?:a|bc)d", False),
    ("(?:ab|cd)e", False), ("(?:a{1,2}){2}", False), ("(?:a|b){3}", False),
    ("a(?=b)", False), ("a{1,2}(?!c)", False), ("(?<=b)a", False),
    ("(?<=b{1,2})a", False), ("(?>a|ab)", False), ("a{1,2}+", False),
    ("a++", False), ("a*", False), ("a+", False), ("a{2,}", False),
    ("\\d{1,3}", False), ("[ab]{0,4}", False), ("\\ba{1,2}", False),
    ("^a{1,2}", False), ("\\Ga", False), ("(?i)a{1,2}", False),
    ("a|(?:b|cd)", False), ("(?:)", False), ("(?:a{0})", False),
    ("(a)(?:b|c)", False), ("a{255}", False), ("a{1,255}", False),
    ("a{1,256}", False), ("a{256}|b", False), ("a{255}|b{1,2}", False),
    ("a{256}|b{1,2}", False), ("a{300}|b{1,2}", False),
    ("a{65535}", False), ("a{65535}b", False), ("a{65536}", False),
    ("(?:a{1000}){65}", False), ("(?:a{1000}){66}", False),
    ("(?:a{1000}){65}|b{1,2}", False),
    ("(?:)*", True), ("(?:\\b)*", True), ("(?:)+", True),
    ("(?:(?=b))*", True), ("(?:a{0})*", True), ("a(?:)*", True),
    ("(?:(?=b))*a{1,2}", True), ("a{1,2}(?:\\b)+", True),
]

# Whole patterns: calls to bounded groups (the [DD-14.LB] reversal), the
# stage-2 backreference rows, and UTF-8 boundary cells (mode, pattern, zw).
EXTRA = [
    ("byte", "^(?(DEFINE)(?<g>a|ab))ab(?<=(?&g))$", False),
    ("byte", "^(?:(?<g>a|ab)){0}ab(?<=(?&g))$", False),
    ("byte", "(?(DEFINE)(?<g>ab))(?<=(?&g))x", False),
    ("byte", "(?(DEFINE)(?<g>a{1,2}))(?<=(?&g)|c)x", False),
    ("byte", "(a)(?<=\\1)x", False),
    ("byte", "(a|bc)(?<=\\1)x", False),
    ("byte", "(?<=a{1,2})x|(?<=b)y", False),
    ("byte", "(?<=a)(?<=b{1,2})x", False),
    ("utf8", "(?<=é{1,255})x", False),
    ("utf8", "(?<=é{1,256})x", False),
    ("utf8", "(?<=é|bc)x", False),
    ("utf8", "(?<=éé)x", False),
    ("utf8", "(?<=.{1,3})x", False),
    ("utf8", "(?<=\\X)x", False),
]


def population():
    rows = []
    for body, zw in BODIES:
        for sp in SPELL:
            rows.append(("byte", sp % body, zw))
    return rows + EXTRA


def pcrec_judge(pcrec, mode, pat):
    """None if pcrec refuses (the DEFAULT route, `-o -`), else True/False:
    some lookbehind branch varies, read from the VM listing (`--emit-ir`
    lists the VM program only, so it is asked under --engine=vm; a pattern
    the default route accepts and the listing cannot describe is "NOJUDGE",
    a bad cell, never a silent False)."""
    enc = "byte" if mode == "byte" else "utf8"
    base = [pcrec, "--features", FEATS, "-e", enc, "--pattern", pat]
    r = subprocess.run(base + ["-o", "-"], capture_output=True, timeout=30)
    if r.returncode != 0:
        return None
    r = subprocess.run(base + ["--engine=vm", "--emit-ir"],
                       capture_output=True, timeout=30)
    if r.returncode != 0:
        return "NOJUDGE"
    return bool(VARIES.search(r.stdout.decode("utf-8", "replace")))


def pcre2_accepts(mode, pat, mvlb):
    opts = 0 if mode == "byte" else P.PCRE2_UTF
    try:
        P.compile(pat if mode == "byte" else pat.encode("utf-8"), opts, mvlb)
        return True
    except P.Pcre2Error:
        return False


def main():
    pcrec = sys.argv[1]
    total = both = divergent = pcre2only = bad = 0
    for mode, pat, zw in population():
        total += 1
        mine = pcrec_judge(pcrec, mode, pat)
        theirs = pcre2_accepts(mode, pat, None)
        if mine is None:
            if theirs:
                pcre2only += 1
            continue
        if not theirs:
            if zw:
                divergent += 1
            else:
                bad += 1
                print("ACCEPT\t%s\t%s\tpcrec compiles, libpcre2 refuses"
                      % (mode, pat))
            continue
        if zw:
            # Accepted by both: not the stated class's shape after all, a
            # generator error, never a pass.
            bad += 1
            print("CLASS\t%s\t%s\tdeclared zero-width class, both accept"
                  % (mode, pat))
            continue
        both += 1
        if mine == "NOJUDGE":
            bad += 1
            print("NOJUDGE\t%s\t%s\tpcrec compiles, --engine=vm --emit-ir "
                  "refuses" % (mode, pat))
            continue
        at0 = pcre2_accepts(mode, pat, 0)
        if mine == at0:
            bad += 1
            print("CLASSIFY\t%s\t%s\tpcrec varies=%s, libpcre2@0 accepts=%s"
                  % (mode, pat, mine, at0))
    print("vlb_accept: total=%d both=%d divergent=%d pcre2only=%d bad=%d"
          % (total, both, divergent, pcre2only, bad))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
