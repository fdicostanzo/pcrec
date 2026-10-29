#!/usr/bin/env python3
"""tests/uprops/uprops_ucdref.py — [UPROP-MORE]'s independent references for
the properties libpcre2 cannot arbitrate (Block, Age) or only partly can
(Bidi_Class, Bidi_Mirrored).

  uprops_ucdref.py names  <ucd-dir> {byte|utf8}   spellings to sweep
  uprops_ucdref.py ext    <ucd-dir> {byte|utf8} <sweep.txt>
  uprops_ucdref.py pyuni  {byte|utf8} <sweep.txt>

`names` prints one `blk=<name>` / `age=<value>` spelling per line, taken from
`Blocks.txt` / `DerivedAge.txt` THEMSELVES (not from the generator or the
generated table), so a block the generator dropped is a name nobody sweeps
only if the data file also lacks it.  Under `byte` only the names with a
member at or below U+00FF are listed (the encoding clamp empties every other
set; the utf8 arm sweeps them all).

`ext` re-reads the same two files and compares each sweep line EXACTLY, then
checks the structure no single line can show: the age sets are disjoint and
`age=NA` completes them to the whole code space, and `blk=NB` (No_Block) is
exactly what the listed blocks leave.  Block and Age have NO libpcre2
differential (PCRE2 refuses both, error 147), so the data file is both source
and only oracle; this is the weak control D178 records, with its structural
mitigation.

`pyuni` is a SECOND, independent control for what python's `unicodedata`
covers when it carries Unicode 16.0.0: Bidi_Mirrored and Bidi_Class for
ASSIGNED code points.  SKIPS LOUDLY on any other python.
"""
import re
import sys
import unicodedata

SURROGATES = range(0xD800, 0xE000)


def universe(enc):
    top = 0xFF if enc == "byte" else 0x10FFFF
    return [c for c in range(top + 1) if c not in SURROGATES]


def ranged(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            rng, value = [p.strip() for p in line.split(";")[:2]]
            ends = rng.split("..")
            lo, hi = int(ends[0], 16), int(ends[-1], 16)
            out.setdefault(value, set()).update(range(lo, hi + 1))
    return out


def sweep_file(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            members = set()
            for tok in parts[1:]:
                lo, hi = tok.split("-")
                members.update(range(int(lo, 16), int(hi, 16) + 1))
            out[parts[0]] = members
    return out


def spell(block_name):
    return "blk=" + block_name.replace(" ", "_")


def cmd_names(ucd, enc):
    low = lambda s: any(c <= 0xFF for c in s)
    for name, cps in sorted(ranged(ucd + "/Blocks.txt").items()):
        if enc == "utf8" or low(cps):
            print(spell(name))
    for value, cps in ranged(ucd + "/DerivedAge.txt").items():
        if enc == "utf8" or low(cps):
            print("age=" + value)
    print("age=NA")
    print("blk=NB")
    return 0


def cmd_ext(ucd, enc, sweep):
    uni = set(universe(enc))
    blocks = ranged(ucd + "/Blocks.txt")
    ages = ranged(ucd + "/DerivedAge.txt")
    got = sweep_file(sweep)
    fails, checked = [], 0
    want = {spell(n): cps & uni for n, cps in blocks.items()}
    want.update({"age=" + v: cps & uni for v, cps in ages.items()})
    listed = set().union(*blocks.values())
    assigned = set().union(*ages.values())
    want["blk=NB"] = uni - listed
    want["age=NA"] = uni - assigned
    for name, members in got.items():
        if name not in want:
            fails.append("%s: swept but not a Blocks.txt / DerivedAge.txt name" % name)
            continue
        checked += 1
        if members != want[name]:
            diff = sorted(members ^ want[name])[:6]
            fails.append("%s: differs from the data file at %s ..." %
                         (name, " ".join("U+%04X" % c for c in diff)))
    # structure, over whatever was swept (the byte arm sweeps a subset)
    ages_got = [(n, m) for n, m in got.items() if n.startswith("age=")]
    seen = {}
    for n, m in ages_got:
        for c in m:
            if c in seen:
                fails.append("%s and %s both contain U+%04X (Age is a function)"
                             % (seen[c], n, c))
                break
            seen[c] = n
    if enc == "utf8":
        if set(seen) != uni:
            fails.append("the age sets do not cover the code space exactly "
                         "(%d of %d)" % (len(seen), len(uni)))
        blk_sets = [m for n, m in got.items() if n.startswith("blk=") and n != "blk=NB"]
        union = set().union(*blk_sets) if blk_sets else set()
        nb = got.get("blk=NB", set())
        if union & nb or (union | nb) != uni:
            fails.append("the blocks and blk=NB do not tile the code space")
    for f in fails:
        print("FAIL: uprops ucdref: " + f)
    if fails:
        return 1
    print("  ok: %s: %d Block/Age sweeps equal the Blocks.txt / DerivedAge.txt "
          "definitions exactly; Age is a function%s" %
          (enc, checked, ", age=NA completes it, blocks + blk=NB tile the space"
           if enc == "utf8" else ""))
    return 0


def cmd_pyuni(enc, sweep):
    if unicodedata.unidata_version != "16.0.0":
        print("SKIP: uprops pyuni: python's unicodedata is %s, not 16.0.0 "
              "(Bidi_Mirrored / Bidi_Class cross-check did not run)"
              % unicodedata.unidata_version)
        return 0
    got = sweep_file(sweep)
    uni = universe(enc)
    fails = []
    bm = got.get("Bidi_Mirrored")
    bcs = {n[3:]: m for n, m in got.items() if n.startswith("bc=")}
    cls_of = {}
    for v, m in bcs.items():
        for c in m:
            cls_of[c] = v
    assigned = 0
    for c in uni:
        ch = chr(c)
        if unicodedata.category(ch) == "Cn":
            if bm is not None and c in bm:
                fails.append("Bidi_Mirrored contains unassigned U+%04X" % c)
            continue
        assigned += 1
        if bm is not None and (c in bm) != bool(unicodedata.mirrored(ch)):
            fails.append("Bidi_Mirrored U+%04X: pcrec %s, unicodedata %s"
                         % (c, c in bm, bool(unicodedata.mirrored(ch))))
        if bcs and cls_of.get(c) != unicodedata.bidirectional(ch):
            fails.append("bc U+%04X: pcrec %s, unicodedata %s" %
                         (c, cls_of.get(c), unicodedata.bidirectional(ch)))
        if len(fails) > 8:
            break
    for f in fails:
        print("FAIL: uprops pyuni: " + f)
    if fails:
        return 1
    print("  ok: %s: Bidi_Mirrored and Bidi_Class agree with python "
          "unicodedata 16.0.0 on all %d assigned code points" % (enc, assigned))
    return 0


def main():
    a = sys.argv[1:]
    if len(a) == 3 and a[0] == "names":
        return cmd_names(a[1], a[2])
    if len(a) == 4 and a[0] == "ext":
        return cmd_ext(a[1], a[2], a[3])
    if len(a) == 3 and a[0] == "pyuni":
        return cmd_pyuni(a[1], a[2])
    sys.stderr.write(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
