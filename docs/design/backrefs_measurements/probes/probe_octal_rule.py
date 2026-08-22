"""probe_octal_rule.py -- MEASURED, libpcre2 (+ pcrec's own class tier).

Charter (d): PCRE2's context-sensitive disambiguation of `\\N` after a
backslash, measured cell by cell rather than transcribed from
pcre2pattern. Four axes, and every one of them is a place the registry's
ten digit rows (src/parse/registry.c:512-521) make a claim this probe
either confirms or refutes:

  A. `\\1`..`\\9` against a varying GROUP COUNT, with the groups BEFORE
     and AFTER the escape -- which decides whether the count is
     "so far" or "in the entire pattern".
  B. `\\10`..`\\99` and the three-digit forms against a varying group
     count -- the octal FALLBACK, and where its ceiling is.
  C. `\\0` and the `\\0dd` family, including the `\\377` / `\\400`
     boundary.
  D. THE CLASS POSITION, which is base syntax in pcrec today
     (FIX-3/K13) -- measured against libpcre2 AND against the built
     `build/pcrec` binary, so the design can say what the module must
     NOT change.

For each cell the fact recorded is PCRE2's COMPILE-TIME verdict (accept,
or the error NUMBER) plus, where it compiles, what it MATCHES -- because
"compiles" does not distinguish a backreference from an octal literal
and the whole question is which one it is. The DISCRIMINATOR subject is
chosen per cell to separate them.

Run with no arguments. `--no-pcrec` skips the axis-D pcrec arm (for a
tree with no build).
"""
import os
import subprocess
import sys
import tempfile

import br_oracle as O

REPO = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True).stdout.strip()
PCREC = os.path.join(REPO, "build", "pcrec")


def verdict(pat):
    e = O.compile_err(pat)
    return "err %d" % e[0] if e else "ok"


def matches(pat, subj):
    if O.compile_err(pat):
        return "-"
    r = O.compile(pat).search(subj)
    return "no" if r is None else str(r[0])


def hdr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


def axis_a():
    hdr("A. \\1..\\9 -- one digit. Group count varied; groups BEFORE vs AFTER.")
    print("%-28s %-9s %s" % ("pattern", "verdict", "note"))
    print("-" * 78)
    rows = []
    for d in "123456789":
        rows.append((r"\%s" % d, "no groups at all"))
        rows.append((r"(a)\%s" % d, "1 group, BEFORE the escape"))
        rows.append((r"\%s(a)" % d, "1 group, AFTER the escape"))
    rows.append((r"(a)(b)(c)(d)(e)(f)(g)(h)(i)\9", "9 groups before"))
    rows.append((r"\9(a)(b)(c)(d)(e)(f)(g)(h)(i)", "9 groups after"))
    for pat, note in rows:
        print("%-28s %-9s %s" % (pat, verdict(pat), note))
    print()
    print("DISCRIMINATOR: does an ACCEPTED one-digit form behave as a")
    print("backreference or as an octal literal?")
    print("  (a)\\1 on 'aa'  -> %s   (backref: (0,2); octal \\1 = 0x01: no)"
          % matches(r"(a)\1", "aa"))
    print("  (a)\\1 on 'a\\x01' -> %s"
          % matches(r"(a)\1", "a\x01"))


def axis_b():
    hdr("B. \\10 and up -- MULTI-DIGIT. The octal fallback and its ceiling.")
    print("%-46s %-9s %s" % ("pattern", "verdict", "note"))
    print("-" * 100)
    g = "".join("(%s)" % c for c in "abcdefghijkl")     # 12 groups
    rows = [
        (r"\10", "no groups; \\10 -> octal 010 = 0x08?"),
        (r"\10(a)", "1 group AFTER"),
        (r"(a)\10", "1 group BEFORE"),
        (g[:10 * 3] + r"\10", "10 groups BEFORE"),
        (r"\10" + g[:10 * 3], "10 groups AFTER"),
        (g[:9 * 3] + r"\10", "9 groups BEFORE (one short)"),
        (r"\12", "no groups; octal 012 = 0x0a"),
        (g + r"\12", "12 groups BEFORE"),
        (r"\12" + g, "12 groups AFTER"),
        (r"\18", "8 is not an octal digit"),
        (r"\19", "9 is not an octal digit"),
        (r"(a)\18", "1 group; \\18 -> ?"),
        (r"\100", "three octal digits = 0x40 '@'"),
        (r"\377", "the documented octal ceiling"),
        (r"\400", "one past \\377"),
        (r"\0400", "\\040 then literal '0'"),
        (r"\1234", "\\123 then literal '4'"),
        (r"\08", "\\0 then literal '8'"),
        (r"\g{10}", "explicit \\g form, no groups"),
        (g[:10 * 3] + r"\g{10}", "explicit \\g form, 10 groups"),
    ]
    for pat, note in rows:
        print("%-46s %-9s %s" % (pat[:46], verdict(pat), note))
    print()
    print("DISCRIMINATORS -- octal or backreference?")
    print("  \\10 on '\\x08'                  -> %s  (octal 010 = BS)"
          % matches(r"\10", "\x08"))
    print("  \\100 on '@'                    -> %s  (octal 100 = '@')"
          % matches(r"\100", "@"))
    print("  \\377 on '\\xff'                 -> %s"
          % matches(r"\377", "\xff"))
    tenb = "".join("(%s)" % c for c in "abcdefghij")
    print("  (a)..(j)\\10 on 'abcdefghijj'   -> %s  (backref to group 10)"
          % matches(tenb + r"\10", "abcdefghijj"))
    print("  (a)..(j)\\10 on 'abcdefghij\\x08' -> %s  (octal reading)"
          % matches(tenb + r"\10", "abcdefghij\x08"))
    print("  (a)\\10 on 'a\\x08'             -> %s  (1 group: octal 010)"
          % matches(r"(a)\10", "a\x08"))
    print("  (a)\\10 on 'aa0'                -> %s  (backref 1 then '0')"
          % matches(r"(a)\10", "aa0"))
    print("  \\10(a)..(j) on '\\x08abcdefghij' -> %s  (octal: groups AFTER"
          " do NOT count)"
          % matches(r"\10" + tenb, "\x08abcdefghij"))
    print("  \\10(a)..(j) on 'jabcdefghij'   -> %s  (backref reading)"
          % matches(r"\10" + tenb, "jabcdefghij"))
    print("  (a)\\18 on 'a\\x018'             -> %s  (octal 01 then '8')"
          % matches(r"(a)\18", "a\x018"))
    print("  (a)\\18 on 'aa8'                -> %s  (backref 1 then '8')"
          % matches(r"(a)\18", "aa8"))
    print("  \\12 with 12 groups AFTER, on the backref subject:")
    g12 = "".join("(%s)" % c for c in "abcdefghijkl")
    print("     \\12(a)..(l) on 'labcdefghijkl' -> %s"
          % matches(r"\12" + g12, "labcdefghijkl"))
    print("     \\12(a)..(l) on '\\nabcdefghijkl' -> %s  (octal 012 = LF)"
          % matches(r"\12" + g12, "\nabcdefghijkl"))


def axis_c():
    hdr("C. \\0 and the \\0dd family -- always octal, never a backreference.")
    print("%-20s %-9s %-14s %s" % ("pattern", "verdict", "matches", "note"))
    print("-" * 78)
    rows = [
        (r"\0", "\x00", "NUL"),
        (r"(a)\0", "a\x00", "a group exists; still octal?"),
        (r"\00", "\x00", ""),
        (r"\000", "\x00", ""),
        (r"\012", "\n", "LF"),
        (r"\0377", "\x1f7", "\\037 then '7'"),
        (r"\o{101}", "A", "the unambiguous \\o{} form"),
        (r"\o{400}", "", "beyond 8-bit"),
    ]
    for pat, subj, note in rows:
        print("%-20s %-9s %-14s %s"
              % (pat, verdict(pat), matches(pat, subj), note))


def axis_d(with_pcrec):
    hdr("D. THE CLASS POSITION -- base syntax in pcrec today (FIX-3/K13).")
    print("%-20s %-9s %-16s %s" % ("pattern", "pcre2", "pcre2 matches",
                                   "pcrec today"))
    print("-" * 78)
    rows = [
        (r"[\1]", "\x01"),
        (r"(a)[\1]", "a\x01"),
        (r"[\10]", "\x08"),
        (r"[\12]", "\n"),
        (r"[\8]", "8"),
        (r"[\9]", "9"),
        (r"[\0]", "\x00"),
        (r"[\377]", "\xff"),
        (r"[\400]", "\x00"),
        (r"[\1-\7]", "\x03"),
        (r"[\k]", "k"),
        (r"[\g]", "g"),
    ]
    for pat, subj in rows:
        p = "-"
        if with_pcrec and os.path.exists(PCREC):
            # A REAL output path, not /dev/null: pcrec writes `<out>.h`
            # beside `<out>`, so /dev/null.h is a permission error that
            # reads as a refusal -- this probe's own first run reported
            # every base-tier class cell as "refuses" for that reason.
            with tempfile.TemporaryDirectory() as td:
                r = subprocess.run(
                    [PCREC, "-p", "rx", "-o", os.path.join(td, "o.c"), pat],
                    capture_output=True, text=True, timeout=30)
            p = "accepts" if r.returncode == 0 else (
                "refuses: " + (r.stderr.strip().splitlines() or [""])[-1][:34])
        print("%-20s %-9s %-16s %s"
              % (pat, verdict(pat), matches(pat, subj), p))
    print()
    print("The pcrec column is the BASE tier (no --features), which is what")
    print("makes it the 'must not change' baseline for module `backrefs`.")


def main():
    if O.SELFCHECK:
        print("ORACLE SELFCHECK FAILED:", O.SELFCHECK)
        return 2
    print("libpcre2 %s" % O.version())
    print("pcrec binary: %s (%s)"
          % (PCREC, "present" if os.path.exists(PCREC) else "ABSENT"))
    axis_a()
    axis_b()
    axis_c()
    axis_d("--no-pcrec" not in sys.argv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
