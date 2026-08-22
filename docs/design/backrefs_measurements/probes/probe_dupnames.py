"""probe_dupnames.py -- MEASURED, libpcre2 only (python3 `re` has no (?J)).

Charter (e): DUPNAMES, which the [M6.5] row rules is IMPLEMENTED by this
module. Three separate questions, and the design's whole answer depends
on getting the third one exactly right:

  1. THE TABLE. What does libpcre2's own `PCRE2_INFO_NAMETABLE` -- the
     construct `rx_info.groups` mirrors (D59) -- contain and in what
     ORDER when a name is duplicated? The [M6.5] row rules pcrec's own
     layout "(name asc, number asc)"; this arm measures whether that is
     libpcre2's order or a pcrec invention.

  2. THE REFUSAL MATRIX. Exactly which spellings need (?J)/DUPNAMES and
     which are legal without it -- including the case pcre2pattern
     permits without the option (the same name in different branches of
     an alternation) if it exists at all.

  3. THE RESOLUTION RULE. When `\\k<n>` names a DUPLICATED name, which
     of the several groups does the backreference compare against? The
     row states PCRE2's documented behaviour as "the first of the set
     that is SET". This arm builds the cells that separate the
     candidate rules:
        (a) first BY NUMBER that is set
        (b) first in TABLE ORDER that is set
        (c) the LAST one set
        (d) "any one of them" (i.e. it succeeds if ANY matches)
     and the NONE-SET case, and the case where a LATER one is set but an
     EARLIER one is not -- which is the cell that separates (a) from (c)
     and which the row explicitly asks to be verified.
"""
import sys

import br_oracle as O

J = O.PCRE2_DUPNAMES


def verdict(pat, opts=0):
    e = O.compile_err(pat, opts)
    return "err %d" % e[0] if e else "ok"


def run(pat, subj, opts=J):
    if O.compile_err(pat, opts):
        return "-"
    r = O.compile(pat, opts).search(subj)
    return "no match" if r is None else "%s g=%s" % (r[0], list(r[1]))


def hdr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


def q1_table():
    hdr("1. THE NAME TABLE -- libpcre2's own order, duplicated names.")
    pats = [
        r"(?<a>x)(?<a>y)",
        r"(?<b>x)(?<a>y)(?<b>z)",
        r"(?<z>1)(?<a>2)(?<z>3)(?<a>4)",
        r"(?<a>1)(?<aa>2)(?<a>3)",
        r"(?<n>1)|(?<n>2)|(?<n>3)",
    ]
    print("%-34s %s" % ("pattern (compiled with DUPNAMES)",
                        "PCRE2_INFO_NAMETABLE, in table order"))
    print("-" * 78)
    for p in pats:
        e = O.compile_err(p, J)
        if e:
            print("%-34s err %d" % (p, e[0]))
            continue
        print("%-34s %s" % (p, O.compile(p, J).nametable()))
    print()
    print("The pairs are (group NUMBER, name). The [M6.5] row's ruled pcrec")
    print("layout is (name asc, number asc); compare directly.")


def q2_refusals():
    hdr("2. THE REFUSAL MATRIX -- what needs (?J)/PCRE2_DUPNAMES.")
    rows = [
        (r"(?<a>x)(?<a>y)",        "same name, sequential"),
        (r"(?<a>x)|(?<a>y)",       "same name, different ALTERNATION branches"),
        (r"(?:(?<a>x)|(?<a>y))",   "same name, branches inside a group"),
        (r"(?J)(?<a>x)(?<a>y)",    "inline (?J) at the start"),
        (r"(?<a>x)(?J)(?<a>y)",    "inline (?J) AFTER the first declaration"),
        (r"(?J:(?<a>x)(?<a>y))",   "scoped (?J:...)"),
        (r"(?J)(?<a>x)(?<a>y)\k<a>", "(?J) + a backref to the dup name"),
        (r"(?<a>x)(?<A>y)",        "names differing only in CASE"),
        (r"(?P<a>x)(?P<a>y)",      "python spelling, duplicated"),
        (r"(?'a'x)(?'a'y)",        "quoted spelling, duplicated"),
        (r"(?J:(?<a>x))(?<a>y)",   "does (?J:...) SCOPE, or leak to the rest?"),
        (r"(?J:(?<a>x)(?<a>y))(?<a>z)",
         "scoped dup pair, then a THIRD outside the scope"),
        (r"((?J)(?<a>x))(?<a>y)",  "(?J) set inside a group, dup outside"),
        (r"(?-J)(?J)(?<a>x)(?<a>y)", "(?J) after (?-J)"),
        (r"(?J)(?<a>x)(?<a>y)\1", "numeric backref to a dup-named group"),
        # THE SEPARATING CELLS for "checked AT THE DECLARATION" vs
        # "(?J) anywhere in the pattern legalises everything". Named by
        # the design review as missing; measured here rather than argued.
        (r"(?<a>x)(?<a>y)(?J)",    "(?J) AFTER both declarations"),
        (r"(?<a>x)(?<a>y)(?J)\k<a>", "same, plus a by-name reference"),
        (r"(?J)(?<a>x)(?-J)(?<a>y)", "(?J) then (?-J) before the second"),
        (r"(?J)(?<a>x)(?:(?-J)q)(?<a>y)",
         "(?-J) SCOPED AWAY before the second declaration"),
    ]
    print("%-30s %-11s %-11s %s"
          % ("pattern", "options=0", "DUPNAMES", "note"))
    print("-" * 90)
    for p, note in rows:
        print("%-30s %-11s %-11s %s" % (p, verdict(p), verdict(p, J), note))
    print()
    print("NOTE the (?J) row: an INLINE (?J) is a compile option, so whether")
    print("it works without the API bit is itself the measurement.")


def q3_resolution():
    hdr("3. THE RESOLUTION RULE -- which of the duplicates does \\k<a> use?")
    print("Every pattern declares TWO groups named `a` (numbers 1 and 2) and")
    print("then references the name. The subject decides which was SET.")
    print()
    cells = [
        # only the FIRST (number 1) participates
        (r"(?J)^(?:(?<a>x)|(?<a>y))\k<a>$", "xx",
         "only #1 set (x); backref must compare 'x'"),
        (r"(?J)^(?:(?<a>x)|(?<a>y))\k<a>$", "yy",
         "only #2 set (y); EARLIER one UNSET -- the row's key cell"),
        (r"(?J)^(?:(?<a>x)|(?<a>y))\k<a>$", "xy",
         "#1 set to 'x'; does the backref accept 'y'?"),
        (r"(?J)^(?:(?<a>x)|(?<a>y))\k<a>$", "yx",
         "#2 set to 'y'; does the backref accept 'x'?"),
        # BOTH participate -- separates first-by-number from last-set
        (r"(?J)^(?<a>x)(?<a>y)\k<a>$", "xyx",
         "BOTH set (#1='x', #2='y'); 'x' = first-by-number"),
        (r"(?J)^(?<a>x)(?<a>y)\k<a>$", "xyy",
         "BOTH set; 'y' = last-set / highest number"),
        # NEITHER participates
        (r"(?J)^(?:(?<a>x)|(?<a>y)|z)\k<a>$", "z",
         "NEITHER set -- unset-backref semantics for a NAME"),
        (r"(?J)^(?:(?<a>x)|(?<a>y)|z)\k<a>$", "zz",
         "NEITHER set, and there is text to compare"),
        # three duplicates, middle one set
        (r"(?J)^(?:(?<a>p)|(?<a>q)|(?<a>r))\k<a>$", "qq",
         "three dups, the MIDDLE one set"),
        (r"(?J)^(?:(?<a>p)|(?<a>q)|(?<a>r))\k<a>$", "rr",
         "three dups, the LAST one set"),
        # the same questions through the other two spellings
        (r"(?J)^(?:(?<a>x)|(?<a>y))(?P=a)$", "yy", "(?P=a) spelling"),
        (r"(?J)^(?:(?<a>x)|(?<a>y))\g{a}$", "yy", "\\g{a} spelling"),
        (r"(?J)^(?:(?<a>x)|(?<a>y))\k'a'$", "yy", "\\k'a' spelling"),
        (r"(?J)^(?:(?<a>x)|(?<a>y))\k{a}$", "yy", "\\k{a} spelling"),
        # the EMPTY-capture edge: #1 is SET but to a zero-length string.
        # "first SET" then means the backref matches nothing at all, which
        # is a different answer from every "first NON-EMPTY" reading.
        (r"(?J)^(?<a>x?)(?<a>y)\k<a>$", "yy",
         "#1 set to EMPTY, #2 set to 'y' -- first-SET picks the EMPTY one"),
        (r"(?J)^(?<a>x?)(?<a>y)\k<a>$", "y",
         "same, with nothing left to compare"),
        # numeric references are unambiguous even under (?J)
        (r"(?J)^(?:(?<a>x)|(?<a>y))\2$", "yy",
         "NUMERIC \\2 -- names irrelevant, must compare group 2"),
        (r"(?J)^(?:(?<a>x)|(?<a>y))\1$", "yy",
         "NUMERIC \\1 -- group 1 is UNSET here, so this must FAIL"),
    ]
    print("%-38s %-6s %-26s %s"
          % ("pattern", "subj", "result", "what the cell separates"))
    print("-" * 118)
    for pat, subj, note in cells:
        print("%-38s %-6s %-26s %s"
              % (pat[:38], repr(subj), run(pat, subj, J)[:26], note))
    print()
    print("NAMED-GROUP NUMBERING under duplicates, for the reflection table:")
    for p in [r"(?J)(?<a>x)(?<a>y)", r"(?J)(?<a>x)(q)(?<a>y)"]:
        e = O.compile_err(p, J)
        print("  %-26s nametable=%s"
              % (p, "err %d" % e[0] if e else O.compile(p, J).nametable()))


def main():
    if O.SELFCHECK:
        print("ORACLE SELFCHECK FAILED:", O.SELFCHECK)
        return 2
    print("libpcre2 %s ; python3 `re` has NO (?J) and no \\k -- this probe is"
          % O.version())
    print("libpcre2-only BY NECESSITY, which is itself charter (g)'s answer")
    print("for every DUPNAMES cell: the base-tier oracle cannot express one.")
    q1_table()
    q2_refusals()
    q3_resolution()
    return 0


if __name__ == "__main__":
    sys.exit(main())
