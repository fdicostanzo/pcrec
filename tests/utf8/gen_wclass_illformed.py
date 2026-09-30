#!/usr/bin/env python3
"""tests/utf8/gen_wclass_illformed.py -- writes wclass_illformed.rxt, the
[CLS-TREE] S4 ill-formed matrix (docs/design/cls_tree_design.md §6, S4 row).

Every CLASS KIND below x every ILL-FORMED KIND x {default engine, `engine
vm`}. The subject is `x` + the bytes + `y`, so the class must consume exactly
one character between two literals. Every ill-formed subject must NOT match,
and one well-formed member per class must match. That is S4's correctness
seam: the VM's kit route decodes, the byte route (DFA, and the VM under
`-fno-cls-kit`) walks the lowered automaton, and the two must agree on which
bytes form a character.

THE ORACLE IS libpcre2 under PCRE2_UTF|PCRE2_MATCH_INVALID_UTF (utf8_design.md
§2.6's ruling: an ill-formed sequence matches nothing, and that mode is the
barrier semantics pcrec promises), run through `pcre2test`. The generator ALSO
compiles every class with pcrec `--engine=dfa` and requires the DFA's answer
to equal the oracle's, which is the design's own statement of the oracle ("the
DFA's answer is the oracle and must agree"). A disagreement aborts generation
rather than being written down.

Run from the repo root: python3 tests/utf8/gen_wclass_illformed.py
(needs build/pcrec, gcc and pcrec2test on PATH). The output is committed; the
generator is the record of how it was made.
"""
import os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PCREC = os.path.join(ROOT, "build", "pcrec")
CC = os.environ.get("CC", "gcc-16")

# (label, pattern class text, a well-formed MEMBER, a well-formed NON-member or None)
CLASSES = [
    ("pL",        r"\p{L}",                    "\u00e9",      "1"),
    ("PL",        r"\P{L}",                    "\u0661",      "\u00e9"),
    ("pXwd",      r"\p{Xwd}",                  "\u0416",      "-"),
    ("PUnknown",  r"\P{Unknown}",              "\u4e2d",      None),
    ("notA",      r"[^a]",                     "\U00010348",  "a"),
    ("dot",       r".",                        "\u20ac",      None),
    ("range2",    r"[\x{80}-\x{7ff}]",         "\u00e9",      "\u4e2d"),
    ("range3",    r"[\x{800}-\x{ffff}]",       "\u20ac",      "\u00e9"),
    ("range4",    r"[\x{10000}-\x{10ffff}]",   "\U00010348",  "\u4e2d"),
    ("latin1",    r"[\x{e0}-\x{ff}]",          "\u00e9",      "\u00c9"),
    ("mixed",     r"[a\x{e9}\x{4e2d}]",        "\u4e2d",      "b"),
    ("caseless",  r"(?i)[k\x{e9}]",            "\u212a",      "j"),
]

# (label, bytes): every ill-formed kind utf8_design.md §2.6 measured, plus the
# truncations of each sequence length.
BAD = [
    ("stray-cont",   b"\x80"),
    ("stray-cont2",  b"\xbf\xbf"),
    ("trunc2",       b"\xc3"),
    ("trunc3",       b"\xe2\x82"),
    ("trunc4",       b"\xf0\x90\x8d"),
    ("overlong2",    b"\xc0\x80"),
    ("overlong2b",   b"\xc1\xbf"),
    ("overlong3",    b"\xe0\x80\x80"),
    ("overlong4",    b"\xf0\x80\x80\x80"),
    ("surrogate",    b"\xed\xa0\x80"),
    ("surrogate-hi", b"\xed\xbf\xbf"),
    ("above-10ffff", b"\xf4\x90\x80\x80"),
    ("f5-lead",      b"\xf5\x80\x80\x80"),
    ("fe",           b"\xfe"),
]


def esc(bs):
    return "".join(chr(b) if 0x20 <= b < 0x7f and chr(b) not in '"\\' else "\\x%02x" % b
                   for b in bs)


def dfa_answer(pattern, subj, tmp, _built={}):
    """pcrec's own --engine=dfa answer: (start, end) or None. One build per
    pattern (a `--emit-main` binary takes the subject as argv[1])."""
    exe = _built.get(pattern)
    if exe is None:
        exe = os.path.join(tmp, "d%d" % len(_built))
        c = exe + ".c"
        r = subprocess.run([PCREC, "-p", "rx", "-e", "utf8", "--features", "all",
                            "--engine=dfa", "--no-captures", "--emit-main", "-o", c,
                            "--pattern", pattern], capture_output=True)
        if r.returncode != 0:
            raise SystemExit("pcrec --engine=dfa refused %r: %s" % (pattern, r.stderr.decode()))
        subprocess.run([CC, "-O1", "-o", exe, c], check=True)
        _built[pattern] = exe
    r = subprocess.run([exe, subj], capture_output=True)
    out = r.stdout.decode().strip()
    if out.startswith("nomatch"):
        return None
    f = out.split()
    return int(f[1]), int(f[2])


def main():
    blocks = []
    tmp = tempfile.mkdtemp(prefix="wcls_ill_")
    for label, cls, member, nonmember in CLASSES:
        pat = "x" + cls + "y"
        cases = []
        good = b"x" + member.encode() + b"y"
        cases.append(("m", good, (0, len(good))))
        if nonmember is not None:
            cases.append(("n", b"x" + nonmember.encode() + b"y", None))
        for _, bad in BAD:
            cases.append(("n", b"x" + bad + b"y", None))
        # the oracle: pcre2test for the verdict, the DFA for agreement and span
        for kind, subj, span in cases:
            want = pcre2_verdict(pat, subj)
            got = dfa_answer(pat, subj, tmp)
            if (got is not None) != want or (kind == "m") != want:
                raise SystemExit("DISAGREE %s on %r: pcre2 %s dfa %s expected %s"
                                 % (pat, subj, want, got, kind))
            if kind == "m" and got != span:
                raise SystemExit("SPAN %s on %r: dfa %s expected %s" % (pat, subj, got, span))
        for engine in (None, "vm"):
            for grouped in (False, True):
                p = ("x(" + cls + ")y") if grouped else pat
                # A block pcrec REFUSES is not written as cases: it is named
                # in a comment with the refusal, so a later change that
                # retires the refusal is visible here on regeneration.
                argv = [PCREC, "-p", "rx", "-e", "utf8", "--features", "all",
                        "-o", os.path.join(tmp, "probe.c"), "--pattern", p]
                if engine: argv.insert(1, "--engine=" + engine)
                r = subprocess.run(argv, capture_output=True)
                if r.returncode != 0:
                    blocks.append("# %s, %s engine, %s: REFUSED at generation -- %s"
                                  % (label, engine or "default",
                                     "captured" if grouped else "bare",
                                     r.stderr.decode().strip().split("\n")[0][:160]))
                    continue
                b = ["# %s, %s engine, %s" % (label, engine or "default",
                                              "captured" if grouped else "bare"),
                     "# pcre2-only", "pattern " + p, "encoding utf8",
                     "features all"]
                if engine: b.append("engine " + engine)
                for kind, subj, span in cases:
                    if kind == "m":
                        b.append('m "%s" %d %d' % (esc(subj), span[0], span[1]))
                    else:
                        b.append('n "%s"' % esc(subj))
                blocks.append("\n".join(b))
    with open(os.path.join(ROOT, "tests", "utf8", "wclass_illformed.rxt"), "w") as f:
        f.write(HEADER)
        f.write("\n\n".join(blocks) + "\n")


def pcre2_verdict(pattern, subj):
    """True/False from pcre2test under UTF|MATCH_INVALID_UTF. The subject is
    written with `\\xhh` escapes, which pcre2test reads as single BYTES even
    in UTF mode (unlike `\\x{..}`, a code point), so ill-formed input reaches
    the matcher as written."""
    script = "/%s/utf,match_invalid_utf\n" % pattern.replace("/", "\\/")
    script += "".join("\\x%02x" % b for b in subj) + "\n"
    r = subprocess.run(["pcre2test", "-q"], input=script.encode(), capture_output=True)
    out = r.stdout.decode("latin-1")
    if "No match" in out:
        return False
    if " 0: " in out:
        return True
    raise SystemExit("pcre2test gave no verdict for %r on %r:\n%s" % (pattern, subj, out))


HEADER = """# [CLS-TREE] S4 -- THE ILL-FORMED MATRIX (cls_tree_design.md §6, S4 row).
# GENERATED by tests/utf8/gen_wclass_illformed.py; edit that, not this.
#
# Twelve wide-class kinds x fourteen ill-formed byte kinds x {default engine,
# `engine vm`} x {bare, captured}. Each subject is `x`, the bytes, `y`; an
# ill-formed sequence matches NOTHING (utf8_design.md §2.6), so every such
# cell is `n`. One well-formed member per class matches and one non-member
# does not. The VM's kit route decodes each character (`<prefix>_decode`) and
# the byte route walks the lowered automaton; they must reject the same
# bytes, and this file is where they are held to it.
#
# ORACLE: libpcre2 (pcre2test) under PCRE2_UTF|PCRE2_MATCH_INVALID_UTF, and
# the generator additionally requires pcrec's own --engine=dfa answer to agree
# on every cell before writing it (the design's "the DFA's answer is the
# oracle and must agree").

"""

if __name__ == "__main__":
    main()
