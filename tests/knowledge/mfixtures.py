#!/usr/bin/env python3
"""tests/knowledge/mfixtures.py STORE_SET OUTDIR -- the measures kind's test
fixtures ([MEASURE-SET] M0), written per run and never committed.

From the committed store set it writes, under OUTDIR:

  ok/      sets that must LOAD (R1-R3, R5):
           fx-store   the store set under a fresh id
           fx-messy   the same rows out of order, cards reversed, header keys
                      shuffled, an unknown column, comments, blank lines and
                      an absent optional key: loads to fx-store's document
           fx-rich    a small set exercising what the store set does not:
                      cells, a fitted interp-log2 row over cells, a derived
                      ratio and a min over rows, a null row, negative values,
                      a pcrec-owned row, tags, and a source with `"`, `\\`, `?`
                      and a non-ASCII byte
           fx-env     an envelope (composite 1) with its members section
  bad/     one set per refusal class of docs/spec/measures.md §7, each named
           for its class; `bad/EXPECT.tsv` lists file and a substring the
           refusal must contain
  idir/    `-I` fixtures: mine.measures.tsv (id mine), other.measures.tsv
           (id mine: an S2 mismatch)
  shadow/  a set reusing the store's id at an uncommitted rev with the
           store's digest (must refuse), and one at the store's rev with one
           value changed and its digest recomputed (must refuse)

Digests are computed with ks_ref.py's (the independent reader's) function;
the C loader recomputes and refuses a mismatch, so a wrong digest here is a
red fixture, never a silent pass.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ks_ref  # noqa: E402


def parse(text):
    """[(section, header line, [row lines])] preserving the file's text."""
    out, cur = [], None
    for ln in text.split("\n"):
        if ln.startswith("#section "):
            cur = [ln[9:], None, []]
            out.append(cur)
        elif cur is None or not ln:
            continue
        elif ln.startswith("#"):
            if not cur[2]:
                cur[1] = ln
        else:
            cur[2].append(ln)
    return out


def render(secs, lead="# fixture\n"):
    t = lead
    for name, hdr, rows in secs:
        t += "#section %s\n%s\n" % (name, hdr)
        for r in rows:
            t += r + "\n"
    return t


def header_set(secs, key, value):
    for s in secs:
        if s[0] == "header":
            s[2] = [r if r.split("\t")[0] != key else key + "\t" + value for r in s[2]]


def redigest(path):
    doc = ks_ref.load(path)
    d = ks_ref.digest(doc)
    text = open(path, encoding="utf-8").read()
    secs = parse(text)
    header_set(secs, "values_digest", d)
    header_set(secs, "rows", str(len(doc["rows"])))
    write(path, render(secs))


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


RICH = """# a rich fixture
#section header
#key\tvalue
format\t1
id\tfx-rich
rev\t3
class\tidk
tier\tsynthetic
composite\t0
members\t
unit_key\tkit.beta.WALK.SCAN
method\tfx@1
rows\t0
values_digest\t0000000000000000
#section cards
#owner\tquantity\tver\tdims\tunit\tsubject\tlengths\tlaunches\trounds\taa_rule\tgate_e6\tenv\tdeps
kit\tbeta\t1\tform;kind\tratio\tstreamed\t-\t5\t5\t-\t-\t-\t-
kit\tsaving\t1\tform;vs\tratio\tderived\t-\t-\t-\t-\t-\t-\t-
kit\tgstar\t1\tform\tbytes\tstreamed\t-\t5\t5\t-\t-\t-\t-
kit\th3a\t1\t-\tbytes\tsynthetic\t-\t-\t-\t-\t-\t-\t-
pcrec\tc_call\t1\tkind\twalkbytes\tfresh\t-\t5\t5\t-\t-\t-\t-
#section rows
#key\tunit\tvalue_e6\tabs_ns_e6\tnoise_e6\tn\tstatus\tderivation\tinputs\tdeps\ttags\tsource
kit.beta.WALK.SCAN\tratio\t1000000\t189200\t1730\t25\tmeasured\t-\t-\tkit:form.walk=00ff\tlayer=off;subject=streamed\tthe unit row
kit.beta.V1.SCAN\tratio\t571882\t108200\t-\t25\tmeasured\t-\t-\t-\t-\tsrc "quoted" \\\\ back? §2.1
kit.saving.V1.WALK\tratio\t-428118\t-\t-\t-\tderived\tdiff\tkit.beta.V1.SCAN;kit.beta.WALK.SCAN\t-\t-\tnegative on purpose
kit.saving.V1.MIN\tratio\t571882\t-\t-\t-\tderived\tmin\tkit.beta.V1.SCAN;kit.beta.WALK.SCAN\t-\t-\t-
kit.gstar.V1\tbytes\t10800000\t-\t-\t-\tfitted\tinterp-log2\tg32;g64\t-\t-\tbracketed by two cells
kit.h3a\tbytes\t\t-\t-\t-\tnull\t-\t-\t-\t-\tbelow the NULL rule
pcrec.c_call.DFA\twalkbytes\t-12\t-\t-\t-\tmeasured\t-\t-\t-\t-\ta pcrec row
#section cells
#cell\tgroup\tarm\tlength\tlaunch\tround\tns_e6
g32\tgstar\tV1\t32\t1\t1\t5000
g64\tgstar\tV1\t64\t1\t1\t4100
g16\tgstar\tV1\t16\t2\t1\t6200
#section members
#member\tunit_key\tunit_abs_ns_e6\tbox
"""

ENV = """#section header
#key\tvalue
format\t1
id\tfx-env
rev\t1
class\tx86-64-v3
tier\tsynthetic
composite\t1
members\tfx-a@1:00000000000000aa;fx-b@2:00000000000000bb
unit_key\tkit.beta.WALK.SCAN
method\tfx@1
rows\t0
values_digest\t0000000000000000
#section cards
#owner\tquantity\tver\tdims\tunit\tsubject\tlengths\tlaunches\trounds\taa_rule\tgate_e6\tenv\tdeps
kit\tbeta\t1\tform;kind\tratio\tstreamed\t-\t5\t5\t-\t-\tmax\t-
#section rows
#key\tunit\tvalue_e6\tabs_ns_e6\tnoise_e6\tn\tstatus\tderivation\tinputs\tdeps\ttags\tsource
kit.beta.WALK.SCAN\tratio\t1000000\t-\t-\t-\tmeasured\t-\t-\t-\t-\t-
kit.beta.V1.SCAN\tratio\t600000\t-\t-\t-\tderived\tenv-max\t-\t-\t-\tmax over members
#section members
#member\tunit_key\tunit_abs_ns_e6\tbox
fx-a@1:00000000000000aa\tkit.beta.WALK.SCAN\t189200\tbox a
fx-b@2:00000000000000bb\tkit.beta.WALK.SCAN\t201000\tbox b
"""


def bad_sets(base):
    """(name, text, substring) for each refusal class."""
    def edit(f):
        secs = parse(base)
        f(secs)
        return render(secs)

    def hdr(k, v):
        return edit(lambda s: header_set(s, k, v))

    def rowfix(i, col, v):
        def f(secs):
            for s in secs:
                if s[0] == "rows":
                    cols = s[1][1:].split("\t")
                    c = s[2][i].split("\t")
                    c[cols.index(col)] = v
                    s[2][i] = "\t".join(c)
        return edit(f)
    out = [
        ("cr", base.replace("\n", "\r\n", 3), "CR or NUL"),
        ("fieldcount", base.replace("format\t1", "format\t1\textra", 1), "fields where section"),
        ("unknownsec", base + "#section bogus\n#a\n1\n", "unknown section"),
        ("derived", base + "#section stale\n#a\n1\n", "derived view"),
        ("unknownkey", hdr("format", "1") .replace("format\t1\n", "format\t1\nbogus\tx\n", 1), "unknown header key"),
        ("format", hdr("format", "2"), "format 2"),
        ("badid", hdr("id", "Bad_Id"), "is not a set name"),
        ("badrev", hdr("rev", "01"), "is not a positive decimal"),
        ("tier", hdr("tier", "gold"), "tier 'gold'"),
        ("missingkey", hdr("method", ""), "missing or empty"),
        ("rowcount", hdr("rows", "1"), "header rows 1"),
        ("digest", hdr("values_digest", "0123456789abcdef"), "but the rows hash to"),
        ("keygrammar", rowfix(0, "key", "kit..x"), "key grammar"),
        ("owner", rowfix(0, "key", "bench.beta.A1.DFA_SCAN.r0e1c1"), "owner 'bench'"),
        ("nocard", rowfix(0, "key", "kit.nosuch.A1"), "has no card"),
        ("arity", rowfix(0, "key", "kit.beta.A1.DFA_SCAN"), "dimension tokens"),
        ("unit", rowfix(0, "unit", "furlongs"), "not in the unit table"),
        ("status", rowfix(0, "status", "guessed"), "status 'guessed'"),
        ("emptyval", rowfix(0, "value_e6", ""), "empty value_e6"),
        ("spelling", rowfix(0, "value_e6", "+5"), "one decimal spelling"),
        ("derivation", rowfix(0, "derivation", "ratio"), "names derivation"),
    ]
    return out


def main(store_set, outdir):
    base = open(store_set, encoding="utf-8").read()
    ok = os.path.join(outdir, "ok")
    # fx-store
    secs = parse(base)
    header_set(secs, "id", "fx-store")
    write(os.path.join(ok, "fx-store.tsv"), render(secs, "# pcrec measurement set (spec: docs/spec/measures.md)\n"))
    # fx-messy
    secs = parse(base)
    header_set(secs, "id", "fx-messy")
    for s in secs:
        if s[0] == "header":
            s[2] = [r for r in s[2] if not r.startswith("libc\t")]
            s[2] = s[2][::-1]
        if s[0] == "cards":
            s[2] = s[2][::-1]
        if s[0] == "rows":
            s[1] = s[1] + "\textra"
            s[2] = [r + "\tjunk" for r in s[2][1::2] + s[2][0::2]]
    t = render(secs, "# a messy file\n\n# with comments\n")
    t = t.replace("#section rows\n", "\n#section rows\n# a comment before the header\n", 1)
    write(os.path.join(ok, "fx-messy.tsv"), t)
    # fx-rich, fx-env
    for name, text in (("fx-rich", RICH), ("fx-env", ENV)):
        p = os.path.join(ok, name + ".tsv")
        write(p, text)
        redigest(p)
    # bad
    bad = os.path.join(outdir, "bad")
    exp = []
    for name, text, sub in bad_sets(base):
        write(os.path.join(bad, name + ".tsv"), text)
        exp.append("%s\t%s" % (name, sub))
    write(os.path.join(bad, "EXPECT.tsv"), "\n".join(exp) + "\n")
    # -I
    secs = parse(base)
    header_set(secs, "id", "mine")
    write(os.path.join(outdir, "idir", "mine.measures.tsv"), render(secs))
    write(os.path.join(outdir, "idir", "other.measures.tsv"), render(secs))
    # shadow: an uncommitted rev with the store's digest; the store's rev with
    # other values
    secs = parse(base)
    header_set(secs, "rev", "7")
    write(os.path.join(outdir, "shadow", "rev7.tsv"), render(secs))
    secs = parse(base)
    for s in secs:
        if s[0] == "rows":
            c = s[2][0].split("\t")
            c[2] = str(int(c[2]) + 1)
            s[2][0] = "\t".join(c)
    p = os.path.join(outdir, "shadow", "values.tsv")
    write(p, render(secs))
    redigest(p)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
