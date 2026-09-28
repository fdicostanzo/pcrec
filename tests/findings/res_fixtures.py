#!/usr/bin/env python3
"""tests/findings/res_fixtures.py DIR — writes the RESOLUTION fixture tree
([FINDINGS] B2; docs/design/findings/design.md §4, §11.5) into DIR, for
run_findings_tests.sh §6 to compile against.

One file, written fresh every run, rather than a committed tree of bundle
files: every fixture is a few lines here, the SHAPE each one exercises is
readable in one place, and a fixture cannot drift from the script that reads
it because the script writes it. Each bundle's counts are distinct, so every
answer is identifiable by its digest alone (findings_ref.py computes that
digest independently of the compiler).

    DIR/A, DIR/B        two -I directories, searched in either order
    DIR/*.rxt           compiling files (stop S1) and parse-refusal cases
"""
import os
import sys


def bundle(name, rows, encs="byte,utf8", include=None, retrieved="2026-09-27",
           extra=""):
    """One analysis bundle with one `freq` block, as `.rxt` text."""
    out = [f"analysis {name}"]
    if include:
        out.append(f"    include <{include}>")
    out += ["    freq",
            f"        question fixture '{name}'",
            "        reader byte-rate",
            "        analyzer tests/findings/res_fixtures.py",
            "        encoding bytes",
            f"        serves byte-rate when {encs} via unigram"]
    for b in sorted(rows):
        out.append(f"        row {b:02x} {rows[b]}")
    out += ["        provenance",
            "            source authored",
            f"            retrieved {retrieved}"]
    return "\n".join(out) + "\n" + extra


def rows(seed):
    """A distinct sparse count table per fixture: `seed` shifts the peak."""
    return {0x61 + (seed % 26): 5000 + seed, 0x20: 900 + seed, 0x2f: 17 + seed,
            0x5a: 3 + seed, 0x40: 7 * seed + 1}


PAT = "\ntarget t = p with c\n\npattern (x?)([a-z]+)+Z.@\\1\nname p\n"


def main(d):
    a, b = os.path.join(d, "A"), os.path.join(d, "B")
    for x in (a, b):
        os.makedirs(x, exist_ok=True)
    w = lambda p, t: open(p, "w").write(t)
    # #1 S1 over S2 over S3: `shadow` in the compiling file AND in A.
    w(os.path.join(d, "s1_shadow.rxt"),
      bundle("shadow", rows(1)) + "config c\n    analysis shadow\n" + PAT)
    w(os.path.join(a, "shadow.rxt"), bundle("shadow", rows(2)))
    # #2 -I order.
    w(os.path.join(a, "ord.rxt"), bundle("ord", rows(3)))
    w(os.path.join(b, "ord.rxt"), bundle("ord", rows(4)))
    # #3/#9 a user `default` that includes the shipped one (include_next),
    # serving utf8 only, so `byte` falls through to the store's default.
    w(os.path.join(a, "default.rxt"),
      bundle("default", rows(5), encs="utf8", include="default"))
    # #4 a non-self include cycle.
    w(os.path.join(a, "cyca.rxt"), bundle("cyca", rows(6), include="cycb"))
    w(os.path.join(a, "cycb.rxt"), bundle("cycb", rows(7), include="cyca"))
    # #5 a nine-link chain d1 -> ... -> d9 (the limit is 8 before the terminal).
    for i in range(1, 10):
        w(os.path.join(a, f"d{i}.rxt"),
          bundle(f"d{i}", rows(10 + i), include=f"d{i + 1}" if i < 9 else None))
    # #7 fall-through: A/lib.rxt is a library (no bundle), B/lib.rxt answers.
    w(os.path.join(a, "lib.rxt"), "pattern abc\nname libdef\n")
    w(os.path.join(b, "lib.rxt"), bundle("lib", rows(20)))
    w(os.path.join(a, "two.rxt"), bundle("two", rows(21)) + bundle("other", rows(22)))
    w(os.path.join(a, "Mixed.rxt"), bundle("mixed", rows(23)))
    # #8 a name defined twice in the compiling file.
    w(os.path.join(d, "dup.rxt"), bundle("dup", rows(24)) + bundle("dup", rows(25)))
    # #10/#11 an explicit include <default>, serving utf8 only.
    w(os.path.join(b, "withdef.rxt"),
      bundle("withdef", rows(26), encs="utf8", include="default"))
    # the no-query note: a byte-only bundle on a utf8 compile.
    w(os.path.join(a, "byteonly.rxt"), bundle("byteonly", rows(27), encs="byte"))
    # #12 the fill-only CLI and the config-variant spelling (design §3.2).
    w(os.path.join(d, "fill.rxt"),
      "config base\n    flags i\n"
      "config exp from base\n    analysis ord\n"
      "target t_cfg = p with exp\n"
      "target t_none = p with base\n"
      "target t_plain = p\n\npattern abc\nname p\n")
    w(os.path.join(d, "pcrecline.rxt"),
      "config c\n    pcrec --analysis ord\n" + PAT)
    # #14 R20: a provenance-only edit, and a one-row edit.
    os.makedirs(os.path.join(d, "P1"), exist_ok=True)
    os.makedirs(os.path.join(d, "P2"), exist_ok=True)
    os.makedirs(os.path.join(d, "P3"), exist_ok=True)
    w(os.path.join(d, "P1", "prov.rxt"), bundle("prov", rows(30)))
    w(os.path.join(d, "P2", "prov.rxt"), bundle("prov", rows(30), retrieved="1999-01-01"))
    r3 = dict(rows(30))
    r3[0x7a] = 1
    w(os.path.join(d, "P3", "prov.rxt"), bundle("prov", r3))
    # #20 the per-target view: config analysis, CLI fill, none.
    w(os.path.join(d, "view.rxt"),
      bundle("mine", rows(31)) +
      "config c\n    analysis mine\n"
      "target t_cfg = p with c\n"
      "target t_fill = p\n\npattern abc\nname p\n")
    # #22 two targets in ONE invocation, the second asking nothing: its
    # stamp must be "" — the consumption record is per compile (and per
    # attempt), never carried from the target before it (F-9).
    w(os.path.join(d, "multi.rxt"),
      "config q\n    pcrec -fno-req-byte\n"
      "target t_asks = p1\n"
      "target t_quiet = p2 with q\n\n"
      "pattern abc\nname p1\n\npattern ^abc\nname p2\n")
    # §11 the table contract's escaping: a question carrying a TAB.
    w(os.path.join(a, "tabq.rxt"),
      bundle("tabq", rows(32)).replace("question fixture 'tabq'",
                                       "question has\ta tab"))
    # F-12's witnesses: K65's repro under two bundles, one making `Z` the
    # rarest necessary member, one making `@` rarest (the pick moves, the
    # answer and the give-up must not).
    zrare = {x: 1000 for x in range(256)}
    zrare[0x5a] = 1
    arare = {x: 1000 for x in range(256)}
    arare[0x40] = 1
    w(os.path.join(a, "pickz.rxt"), bundle("pickz", zrare))
    w(os.path.join(a, "picka.rxt"), bundle("picka", arare))


if __name__ == "__main__":
    main(sys.argv[1])
