"""probe_caseless_fold.py -- MEASURED, libpcre2 + in-pcrec.

Charter (b): the caseless backreference compare, which D23 boundary 1
named as the one place caselessness can still cost something at run time
and which D58 named as [M5-SEAM] residue.

Three things the design has to know and only measurement can settle:

  A. WHICH FOLD does an 8-bit NON-UTF libpcre2 apply to a backreference
     compare? The candidates are ASCII-only (52 bytes) and the C
     library's locale tables (which in a Latin-1 locale would fold
     0xC0/0xE0 and friends). pcrec's own base-tier fold is ASCII-only
     and DELIBERATELY so (src/parse/parse.c:195-230, D23) -- if
     libpcre2's default differs, the module inherits a divergence.

  B. WHERE THE OPTION IS READ. `(?i)` is scoped. Is the compare's
     caselessness decided by the option in force at the GROUP or at
     the BACKREFERENCE? This is the same question `Ast.multiline`
     answers for `$` (D62), and the answer decides whether the module
     needs a parse-resolved FIELD or can consult a global.

  C. WHETHER THE COMPARE IS LENGTH-PRESERVING. In the byte encoding it
     trivially is. The measurement that matters for the seam's SIGNATURE
     is what a UTF-8 backend would face, so this arm records the byte
     lengths libpcre2 reports for a caseless compare over non-ASCII
     input in the 8-bit non-UTF build -- the only build pcrec has today.

The in-pcrec arm reads pcrec's OWN fold table by compiling `-i` classes
and diffing the emitted C, which is `cls_casefold`'s behaviour as built
rather than as documented.
"""
import os
import subprocess
import sys
import tempfile

import br_oracle as O

I = O.PCRE2_CASELESS
REPO = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True).stdout.strip()
PCREC = os.path.join(REPO, "build", "pcrec")


def hdr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


def axis_a():
    hdr("A. WHICH BYTES DOES A CASELESS BACKREF COMPARE FOLD?")
    print("For each byte b in 0..255, the pattern `(?i)^(X)Y$` with X = the")
    print("byte and Y = a backref: the subject is `b` followed by CANDIDATE.")
    print("A byte folds iff some OTHER byte c != b makes the backref match.")
    print()
    folds = {}
    rx = O.compile(r"^(.)\1$", I)
    for b in range(256):
        partners = []
        for c in range(256):
            if c == b:
                continue
            subj = bytes([b, c]).decode("latin-1")
            if rx.search(subj) is not None:
                partners.append(c)
        if partners:
            folds[b] = partners
    print("bytes with at least one fold PARTNER under a caseless backref:")
    print("  count = %d" % len(folds))
    ascii_pairs = {b for b in range(0x41, 0x5b)} | {b for b in range(0x61, 0x7b)}
    extra = sorted(set(folds) - ascii_pairs)
    missing = sorted(ascii_pairs - set(folds))
    print("  ASCII letters covered      : %d of 52" % (52 - len(missing)))
    print("  NON-ASCII bytes that fold  : %s"
          % ([hex(b) for b in extra] or "NONE"))
    print("  ASCII letters that do NOT  : %s"
          % ([hex(b) for b in missing] or "none"))
    bad = {b: p for b, p in folds.items() if len(p) != 1}
    print("  bytes with MORE than one partner: %s"
          % ({hex(k): [hex(x) for x in v] for k, v in bad.items()} or "none"))
    print()
    print("VERDICT: the compare's fold is %s"
          % ("ASCII-ONLY, exactly cls_casefold's 52 bytes"
             if not extra and not missing and not bad
             else "NOT the plain ASCII 52-byte swap -- see above"))
    return folds


def axis_a_pcrec(folds):
    hdr("A'. pcrec's OWN fold, read off the compiler rather than the source.")
    if not os.path.exists(PCREC):
        print("build/pcrec ABSENT -- skipping loudly rather than reporting")
        print("agreement this arm did not measure.")
        return
    print("For each byte, `-i` on the singleton class vs the explicit pair:")
    print("byte-identical emitted C means pcrec folds that byte to that")
    print("partner. Disagreements with axis A are listed; silence means the")
    print("two fold sets are the same set.")
    disagree = []
    for b in range(256):
        lit = "\\x%02x" % b
        with tempfile.TemporaryDirectory() as td:
            a = subprocess.run([PCREC, "-p", "rx", "-i", "-o",
                                os.path.join(td, "a.c"), "[%s]" % lit],
                               capture_output=True, text=True, timeout=30)
            if a.returncode != 0:
                continue
            ca = open(os.path.join(td, "a.c")).read()
            # the same class with BOTH cases spelled out
            partner = folds.get(b, [None])[0]
            if partner is None:
                # pcrec folds it iff `-i [b]` differs from plain `[b]`
                p = subprocess.run([PCREC, "-p", "rx", "-o",
                                    os.path.join(td, "b.c"), "[%s]" % lit],
                                   capture_output=True, text=True, timeout=30)
                cb = open(os.path.join(td, "b.c")).read() if p.returncode == 0 else None
                # compare past the stamp lines: the pattern text differs by -i
                if cb is not None and _body(ca) != _body(cb):
                    disagree.append((b, "pcrec FOLDS it, libpcre2 does not"))
                continue
            p = subprocess.run([PCREC, "-p", "rx", "-o",
                                os.path.join(td, "b.c"),
                                "[%s\\x%02x]" % (lit, partner)],
                               capture_output=True, text=True, timeout=30)
            cb = open(os.path.join(td, "b.c")).read() if p.returncode == 0 else None
            if cb is None or _body(ca) != _body(cb):
                disagree.append((b, "pcrec does NOT fold it to 0x%02x" % partner))
    print("  disagreements: %s"
          % ([(hex(b), m) for b, m in disagree] or "NONE -- the two fold sets"
             " are identical over all 256 bytes"))


def _body(c):
    """Strip the per-invocation METADATA so two artifacts compiled from
    different pattern TEXT can be compared on their AUTOMATON alone.

    THIS PROBE'S OWN FIRST FINDING, kept because it is the failure mode the
    project keeps cataloguing: the first version stripped only comment
    lines, so EVERY byte came back "disagrees" -- it was measuring the
    `.flags` stamp (`-i` sets PCREC_CASELESS = 1) and the embedded pattern
    text, not the fold. A confident 256-row disagreement produced by a
    filter that never looked at a transition table is exactly the kind of
    number a design should not be built on. Diffed by hand on one pair
    (`-i '[A]'` vs `'[Aa]'`): the ONLY differing lines are the leading
    comment, the `#include` of the artifact's own header, the pattern
    echo, `.flags`, `.pattern` and `.pattern_len`. Everything else --
    class bitmaps, transition tables, accept arrays -- is byte-identical,
    which is the fact this arm exists to test."""
    keep = []
    for ln in c.splitlines():
        s = ln.strip()
        if s.startswith("*") or s.startswith("/*") or s.startswith("//"):
            continue
        if s.startswith("#include"):
            continue
        if (".flags" in ln or ".pattern" in ln or "pattern_len" in ln
                or "PCREC_VERSION" in ln):
            continue
        keep.append(ln)
    return "\n".join(keep)


def axis_b():
    hdr("B. WHERE IS `(?i)` READ -- at the GROUP or at the BACKREFERENCE?")
    cells = [
        (r"^(?i:(a))\1$",    "aA", "(?i) scoped to the GROUP only"),
        (r"^(?i:(a))\1$",    "aa", "  ... same, exact-case subject"),
        (r"^(a)(?i)\1$",     "aA", "(?i) turned on AFTER the group"),
        (r"^(?i)(a)(?-i)\1$", "aA", "(?i) on at the group, OFF at the backref"),
        (r"^(?i)(a)(?-i)\1$", "aa", "  ... same, exact-case subject"),
        (r"^(a)(?i:\1)$",    "aA", "(?i) scoped to the BACKREF only"),
        (r"^(?i)(a)\1$",     "aA", "(?i) on at both"),
        (r"^((?i)a)\1$",     "aA", "(?i) inside the group, backref outside"),
        (r"^((?i)a)\1$",     "Aa", "  ... other order"),
    ]
    print("%-26s %-6s %-14s %s" % ("pattern", "subj", "libpcre2", "cell"))
    print("-" * 92)
    for pat, subj, note in cells:
        e = O.compile_err(pat)
        if e:
            r = "err %d" % e[0]
        else:
            m = O.compile(pat).search(subj)
            r = "no match" if m is None else str(m[0])
        print("%-26s %-6s %-14s %s" % (pat, repr(subj), r, note))
    print()
    print("If the (?i)-scoped-to-the-BACKREF rows match and the")
    print("(?i)-scoped-to-the-GROUP rows do not, the compare's caselessness")
    print("is a property of the BACKREFERENCE NODE -- a parse-resolved field,")
    print("D62's rule, exactly as `Ast.multiline` is for `$`.")


def axis_c():
    hdr("C. LENGTH. Is the caseless compare length-preserving in 8-bit?")
    cells = [
        (r"(?i)^(ab)\1$",     "abAB"),
        (r"(?i)^(\xdf)\1$",   "\xdf\xdf"),
        (r"(?i)^(ss)\1$",     "ss\xdf"),
        (r"(?i)^(\xdf)\1$",   "\xdfss"),
        (r"(?i)^(\xe0)\1$",   "\xe0\xc0"),
    ]
    print("%-22s %-14s %s" % ("pattern", "subject", "libpcre2"))
    print("-" * 70)
    for pat, subj in cells:
        e = O.compile_err(pat)
        if e:
            r = "err %d" % e[0]
        else:
            m = O.compile(pat, 0).search(subj)
            r = "no match" if m is None else str(m[0])
        print("%-22s %-14s %s" % (repr(pat), repr(subj), r))
    print()
    print("In the 8-bit NON-UTF build every fold pair is one byte to one")
    print("byte, so the compare cannot change length. The rows above are the")
    print("EVIDENCE for that, and the sharp-s row is the counterexample a")
    print("UTF-8 backend would have to handle and this one does not.")


def main():
    if O.SELFCHECK:
        print("ORACLE SELFCHECK FAILED:", O.SELFCHECK)
        return 2
    print("libpcre2 %s (8-bit, NO PCRE2_UTF -- pcrec's own encoding today)"
          % O.version())
    folds = axis_a()
    axis_a_pcrec(folds)
    axis_b()
    axis_c()
    return 0


if __name__ == "__main__":
    sys.exit(main())
