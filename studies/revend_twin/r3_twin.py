#!/usr/bin/env python3
"""studies/revend_twin/r3_twin.py -- [OPT-REVEND] L2's WINDOW-IDENTITY TWIN,
stage 2 and stage 1 together (locate_finish.md §4.3, §5 L3; LR-S2, LR-S4;
lane revbuild). Drives r3_driver.c over a population.

For each pattern: compile A (default: the `rev-end` walk) and B
(`-fno-rev-end`: the composite) with the SAME pcrec build, wrap each in its own
translation unit (B's `<p>_reset_for_next_attempt` is not instrumented; A's is,
counting E-VR traversals), link with r3_driver.c and libpcre2-8, and run every
subject over the pattern's alphabet up to MAXLEN characters at every
character-boundary offset. Reports per pattern: the artifact class (A's
`RX_DFA_SCAN`, engine, `RX_VM_RESEED` -- `exact` is the exact hybrid, the
LR-S4 stratum), window/answer/oracle differences and the E-VR count.

  python3 -I studies/revend_twin/r3_twin.py PCREC OUTDIR [--extra FILE] [--stage2-rxt FILE]

The population is every block of tests/revend/stage2_captures.rxt (its own
flags and encoding) plus r3_patterns.tsv. Exit 1 on any difference, on a
nonzero E-VR count on an exact hybrid, or on an empty stratum the design
names (exact hybrid, superset hybrid, DFA-only), so a population that stopped
reaching a class is a failure, not a pass (K35).
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def stage2_blocks(path):
    blocks = []
    for line in open(path, encoding="utf-8", errors="surrogateescape"):
        line = line.rstrip("\n")
        if line.startswith("pattern "):
            blocks.append({"pat": line[8:], "flags": "", "enc": "byte"})
        elif blocks and line.startswith("flags "):
            blocks[-1]["flags"] = line.split()[1]
        elif blocks and line.startswith("encoding "):
            blocks[-1]["enc"] = line.split()[1]
    return blocks


def extra_rows(path):
    rows = []
    for line in open(path, encoding="utf-8"):
        if not line.strip() or line.startswith("#"):
            continue
        name, enc, flags, alpha, pat = line.rstrip("\n").split("\t")
        rows.append({"pat": pat, "flags": "" if flags == "-" else flags, "enc": enc,
                     "alpha": alpha.replace("\\n", "\n"), "name": name})
    return rows


def alphabet(row):
    if row.get("alpha"):
        return row["alpha"]
    lits = []
    for ch in re.sub(r"\\[a-zA-Z]|\[\^?|\{[0-9,]*\}|\(\?[<=!:]*|[()|*+?.$^\]]", "", row["pat"]):
        if ch.isalnum() and ch not in lits:
            lits.append(ch)
    base = lits[:2] + ["1", " ", "\n"]
    if row["enc"] == "utf8":
        base.append("é")
    out = []
    for c in base:
        if c not in out:
            out.append(c)
    return "".join(out[:5])


def oracle(row):
    pat, opts = row["pat"], ""
    if "i" in row["flags"]:
        opts += "i"
    if row["enc"] == "utf8":
        opts += "u"
    if "u" in row["flags"]:
        pat = "(*UCP)" + pat
    return pat, opts or "-"


def compile_art(pcrec, row, prefix, outc, extra):
    argv = [pcrec, "--features", "all", "-p", prefix, "-o", outc]
    if row["enc"] == "utf8":
        argv += ["-e", "utf8"]
    if "i" in row["flags"]:
        argv += ["-i"]
    if "u" in row["flags"]:
        argv += ["--ucp"]
    if "N" in row["flags"]:
        argv += ["-fno-anchored-dfa"]
    argv += extra + ["--pattern", row["pat"]]
    r = subprocess.run(argv, capture_output=True)
    return r.returncode == 0


def stamp(text, name):
    m = re.search(r'#define [A-Z0-9_]+_%s "([^"]*)"' % name, text)
    return m.group(1) if m else "-"


def wrapper(tag, prefix, cfile, text, count_evr):
    up = prefix.upper()
    if count_evr:
        text = text.replace("%s_reset_for_next_attempt(run);" % prefix,
                            "%s_reset_for_next_attempt(run); twin_evr_A++;" % prefix)
    open(cfile, "w").write("extern long twin_evr_A;\n" + text)
    haspf = ("static int %s_prefilter(" % prefix) in text
    return (
        '#include "%s"\n'
        "int twin%s_search(const unsigned char *s, size_t n, size_t f, ptrdiff_t (*c)[2])"
        " { return %s_search(s, n, f, c); }\n"
        "int twin%s_pf(const unsigned char *s, size_t n, size_t f, ptrdiff_t (*w)[2])"
        " { %s }\n"
        "int twin%s_ncaps(void) { return %s_NCAPS; }\n"
    ) % (os.path.basename(cfile), tag, prefix, tag,
         ("return %s_prefilter(s, n, f, w);" % prefix) if haspf else "(void)s; (void)n; (void)f; (void)w; return -9;",
         tag, up)


def main():
    args = sys.argv[1:]
    pcrec, out = os.path.abspath(args[0]), os.path.abspath(args[1])
    extra = os.path.join(HERE, "r3_patterns.tsv")
    s2 = os.path.join(HERE, "..", "..", "tests", "revend", "stage2_captures.rxt")
    if "--extra" in args:
        extra = args[args.index("--extra") + 1]
    if "--stage2-rxt" in args:
        s2 = args[args.index("--stage2-rxt") + 1]
    os.makedirs(out, exist_ok=True)
    pop = [dict(b, name="s2:%d" % i) for i, b in enumerate(stage2_blocks(s2))] + extra_rows(extra)
    strata = {}
    bad = 0
    with open(os.path.join(out, "r3_results.tsv"), "w") as res:
        res.write("#name\tenc\tflags\tclass\tcells\tpf_cells\twin_diff\tans_diff\tora_diff\tevr\tpattern\n")
        for k, row in enumerate(pop):
            d = os.path.join(out, "p%03d" % k)
            os.makedirs(d, exist_ok=True)
            ca, cb = os.path.join(d, "A.c"), os.path.join(d, "B.c")
            if not (compile_art(pcrec, row, "pa", ca, []) and
                    compile_art(pcrec, row, "pb", cb, ["-fno-rev-end"])):
                res.write("%s\t%s\t%s\trefused\t\t\t\t\t\t\t%s\n" % (row["name"], row["enc"], row["flags"], row["pat"]))
                continue
            ta, tb = open(ca).read(), open(cb).read()
            scan, eng, reseed = stamp(ta, "DFA_SCAN"), stamp(ta, "ENGINE"), stamp(ta, "VM_RESEED")
            if scan != "rev-end":
                cls = "not-rev-end"
            elif eng == "dfa":
                cls = "dfa-only"
            elif "static int pb_prefilter(" not in tb:
                cls = "hybrid-vs-unprefiltered"   # a size cap dropped B's prefilter
            elif reseed == "exact":
                cls = "exact-hybrid"
            else:
                cls = "superset-hybrid"
            open(os.path.join(d, "wa.c"), "w").write(wrapper("A", "pa", ca, ta, True))
            open(os.path.join(d, "wb.c"), "w").write(wrapper("B", "pb", cb, tb, False))
            exe = os.path.join(d, "drv")
            cc = subprocess.run(["gcc", "-O1", "-w", "-o", exe, os.path.join(HERE, "r3_driver.c"),
                                 os.path.join(d, "wa.c"), os.path.join(d, "wb.c"), "-lpcre2-8"],
                                capture_output=True, text=True)
            if cc.returncode:
                bad += 1
                res.write("%s\t%s\t%s\tbuild-failed\t\t\t\t\t\t\t%s\n" % (row["name"], row["enc"], row["flags"], row["pat"]))
                sys.stderr.write("BUILD %s: %s\n" % (row["pat"], cc.stderr[:400]))
                continue
            alpha = alphabet(row)
            nlet = len(alpha)
            maxlen = 7 if nlet <= 3 else 6 if nlet <= 4 else 5
            opat, oopt = oracle(row)
            r = subprocess.run([exe, alpha, str(maxlen), opat, oopt], capture_output=True, text=True,
                               timeout=600)
            m = re.search(r"cells (\d+) win_diff (\d+) ans_diff (\d+) ora_diff (\d+) evr (\d+) pf_cells (\d+)", r.stdout)
            if not m:
                bad += 1
                res.write("%s\t%s\t%s\tdriver-failed\t\t\t\t\t\t\t%s\n" % (row["name"], row["enc"], row["flags"], row["pat"]))
                continue
            cells, wd, ad, od, evr, pfc = map(int, m.groups())
            fail = wd or ad or od or (cls == "exact-hybrid" and evr)
            if fail:
                bad += 1
                sys.stderr.write("DIFF %s [%s]: %s\n%s" % (row["pat"], cls, m.group(0), r.stderr))
            st = strata.setdefault(cls, [0, 0, 0, 0, 0, 0])
            for i, v in enumerate((1, cells, wd, ad, od, evr)):
                st[i] += v
            res.write("%s\t%s\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%s\n" % (
                row["name"], row["enc"], row["flags"] or "-", cls, cells, pfc, wd, ad, od, evr, row["pat"]))
    print("stratum\tpatterns\tcells\twin_diff\tans_diff\tora_diff\tevr")
    for cls in sorted(strata):
        print("%s\t%s" % (cls, "\t".join(str(v) for v in strata[cls])))
    for need in ("exact-hybrid", "superset-hybrid", "dfa-only"):
        if need not in strata:
            print("EMPTY STRATUM: %s" % need)
            bad += 1
    print("FAILURES: %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
