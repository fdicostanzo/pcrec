#!/usr/bin/env python3
"""tests/partlayout/run_partlayout.py -- [ENTRY-TABLE] E1's CHECKS
(docs/design/compound_entries.md §3.6; docs/spec/tuning.md §2.51-§2.53).

Every row of the part-layout tables is reached by SETTING ITS CONTROL on a
corpus artifact with a subject of its class (D163 addendum 11); each section
names its independent control:

  1  OBJECT    witnesses x controls through evaluator.py, which shares no code
               with the tables: expected layouts from an attribute-stripped
               call graph, the owners' attributes, the hand class/rank maps
               and tuning.md §5.4's preset rows, judged on the real object's
               `nm` (shared = one local symbol, inline = absent, no clone)
               and on the expected `<PREFIX>_PART_LAYOUT`/`_WHY` stamps.
               Every --tune position runs here too: with every preset cell a
               dagger, each must resolve to T0 and carry no stamp.
  2  FIXTURES  precedence and held-request rows written BY HAND (fixtures.tsv):
               the row each subject stopped at (`--emit-facts`) and the stamps.
  3  DISJOINT  on VM witnesses at every entry rung: the functions a control
               changes are subjects only (never A1's), each on a `static`
               definition (LK-9; gcc 15.2 accepts `inline always_inline` on
               an exported callee under -fPIC, so the text is the check).
  4  GCC       H1/H2 by construction: gcc refuses always_inline on the attempt
               route's label-table body and on a framed computed-goto body.
  5  CENSUS    over population.txt x controls: every attribute an artifact
               carries belongs to a writer in writers.tsv (an unlisted writer
               fails); every subject reaches exactly one row; each row's
               population per control is counted against a floor (K35); the
               encoding seam is never non-copyable.
  6  NEUTRAL   the same population and nearcap.txt: under every control the
               refusal, every `#define <PREFIX>_*` but `_TUNE`/`_PART_LAYOUT*`
               and the size figures a decision read (`--warn-emit-bytes`'s
               note) equal the no-control compile's (I5), and the all-auto
               control set is byte-identical to no control (T0).
  7  T2        UNREACHED, stated: no compile carries a measurement set, so
               `theta_hot` is never `none` and row T2 (and TM) has no witness.

Prints PASS/FAIL lines and `checks passed:`/`checks failed:`; exit 1 on any
failure. Env: PCREC (default build/pcrec), CC (default gcc), JOBS (8),
TMPDIR for scratch.
"""
import concurrent.futures as cf
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PCREC = os.environ.get("PCREC", os.path.join(ROOT, "build", "pcrec"))
CC = os.environ.get("CC", "gcc")
JOBS = int(os.environ.get("JOBS", "8"))
SPEC = os.path.join(ROOT, "docs", "spec", "tuning.md")
TMP = tempfile.mkdtemp(prefix="partlayout.", dir=os.environ.get("TMPDIR") or None)

passed = failed = 0


def check(ok, msg):
    global passed, failed
    if ok:
        passed += 1
        print("PASS: " + msg)
    else:
        failed += 1
        print("FAIL: " + msg)


def run(argv, **kw):
    return subprocess.run(argv, capture_output=True, text=True, errors="replace", **kw)


def decode(s):
    """--list-source's escapes: \\\\ \\t \\n \\r \\xNN."""
    out, i = [], 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            c = s[i + 1]
            if c in "\\tnr":
                out.append({"\\": "\\", "t": "\t", "n": "\n", "r": "\r"}[c])
                i += 2
                continue
            if c == "x":
                out.append(chr(int(s[i + 2:i + 4], 16)))
                i += 4
                continue
        out.append(s[i])
        i += 1
    return "".join(out)


def rows(path):
    for line in open(path, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        yield line.rstrip("\n").split("\t")


def pats(path):
    return [decode(l.rstrip("\n")) for l in open(path, encoding="utf-8")
            if not l.startswith("#") and l.strip()]


def flags_of(cell):
    return [] if cell == "-" else cell.split()


def compile_c(pattern, args, out):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return run([PCREC, "-p", "rx", "--features", "all"] + args + ["-o", out, "--pattern", pattern])


def facts(pattern, args):
    r = run([PCREC, "--features", "all"] + args + ["--emit-facts", "--pattern", pattern])
    if r.returncode:
        return None
    sec, parts, ctl = None, [], []
    for line in r.stdout.split("\n"):
        if line.startswith("#section "):
            sec = line.split()[1]
            continue
        if not line or line.startswith("#"):
            continue
        if sec == "part-layout":
            parts.append(line.split("\t"))
        elif sec == "part-layout-controls":
            ctl.append(line.split("\t"))
    return parts, ctl


def stamps(text):
    lay = re.search(r'^#define RX_PART_LAYOUT "([^"]*)"', text, re.M)
    why = re.search(r'^#define RX_PART_LAYOUT_WHY "([^"]*)"', text, re.M)
    return (lay.group(1) if lay else None), (why.group(1) if why else None)


# ---- 1 OBJECT ----------------------------------------------------------------

CONTROLS = [
    [], ["--part-layout=prefilter:auto,compound:auto,find:auto,wrap:auto",
         "--part-residual=auto", "--part-inline-rank=none"],
    ["--part-layout=prefilter:inline"], ["--part-layout=prefilter:shared"],
    ["--part-layout=prefilter:auto"], ["--part-layout=compound:inline"],
    ["--part-layout=compound:shared"], ["--part-residual=shared"],
    ["--part-residual=inline"], ["--part-residual=auto"],
    ["--part-inline-rank=R3"], ["--part-inline-rank=R2"], ["--part-inline-rank=R0"],
    ["--part-inline-rank=none"], ["--part-inline-rank=measured"],
    ["--part-layout=prefilter:shared", "--part-inline-rank=R2"],
    ["--part-inline-rank=R2", "--part-residual=shared"],
    ["--part-layout=prefilter:auto", "--part-residual=inline"],
    ["--part-layout=find:inline,wrap:shared"],
    ["--tune=min-size"], ["--tune=size"], ["--tune=balanced"], ["--tune=speed"],
    ["--tune=max-speed"], ["--tune=speed", "--part-residual=inline"],
]


def sec_object():
    jobs = []
    wit = list(rows(os.path.join(HERE, "witnesses.tsv")))
    for w in wit:
        for i, c in enumerate(CONTROLS):
            wd = os.path.join(TMP, "ev", w[0], str(i))
            argv = [sys.executable, os.path.join(HERE, "evaluator.py"), PCREC, SPEC, wd,
                    w[3], w[4], w[2]] + flags_of(w[1]) + c
            jobs.append((w[0], c, argv))
    with cf.ThreadPoolExecutor(JOBS) as ex:
        res = list(ex.map(lambda j: (j, run(j[2])), jobs))
    by = {}
    laid = 0
    for (wid, c, _), r in res:
        ok = r.returncode == 0
        by.setdefault(wid, []).append((ok, c, r.stdout.strip() + r.stderr.strip()))
        if ok and re.search(r"=(shared|inline)\b", r.stdout):
            laid += 1
    for wid, outs in by.items():
        bad = [o for o in outs if not o[0]]
        check(not bad, "object: witness %s, %d control settings judged on the real object%s"
              % (wid, len(outs), "" if not bad else ": " + " | ".join(b[2] for b in bad[:4])))
    # The reach: the matrix must lay a part out (shared or inline) on a good
    # share of its runs, or it judged nothing: 85 of 225 measured at landing
    # (the rest are T0 settings, held parts and the tune positions).
    check(laid >= 60, "object: %d of %d runs expected a part shared or inlined (floor 60)"
          % (laid, len(res)))


# ---- 2 FIXTURES -------------------------------------------------------------

def sec_fixtures():
    for f in rows(os.path.join(HERE, "fixtures.tsv")):
        fid, fl, pattern, ctl, want_rows, want_stamp, want_why = f
        args = flags_of(fl) + ctl.split()
        got = facts(pattern, args)
        r = compile_c(pattern, args, os.path.join(TMP, "fx", fid, "x.c"))
        if got is None or r.returncode:
            check(False, "fixture %s: the compile refused" % fid)
            continue
        parts, _ = got
        have = {p[1]: p[6].split()[0] for p in parts if p[2] != "owned"}
        want = dict(kv.split("=") for kv in want_rows.split(","))
        text = open(os.path.join(TMP, "fx", fid, "x.c")).read()
        lay, why = stamps(text)
        ok = (all(have.get(k) == v for k, v in want.items()) and
              lay == (None if want_stamp == "-" else want_stamp) and
              why == (None if want_why == "-" else want_why))
        check(ok, "fixture %s: rows %s, stamp %r, why %r%s" % (
            fid, want_rows, want_stamp, want_why,
            "" if ok else " -- got rows %s, stamp %r, why %r" % (have, lay, why)))


# ---- 3 DISJOINT -------------------------------------------------------------

SUBJ = re.compile(r"^rx(_prefilter|__[a-z0-9]+_search)$")


def heads(text):
    """{function: head line} for every top-level definition head."""
    out = {}
    for l in text.split("\n"):
        if l.startswith((" ", "\t", "#")) or l.rstrip().endswith(";"):
            continue
        m = re.match(r"^(?:static\s+)?(?:inline\s+)?(?:__attribute__\(\(\w+\)\)\s+)*"
                     r"[\w\s\*]*?\b(rx\w*)\(", l)
        if m:
            out[m.group(1)] = l
    return out


def sec_disjoint():
    wit = [w for w in rows(os.path.join(HERE, "witnesses.tsv"))]
    ctls = [["--part-residual=shared"], ["--part-residual=inline"],
            ["--part-layout=prefilter:inline,compound:shared"], ["--part-inline-rank=R0"]]
    seen = bad = 0
    msgs = []
    for w in wit:
        for shape in ([], ["--vm-entry-shape=1"], ["--vm-entry-shape=2"],
                      ["--vm-entry-shape=3"], ["--vm-entry-shape=4"]):
            base = flags_of(w[1]) + shape
            r0 = compile_c(w[2], base, os.path.join(TMP, "dj", "b", "x.c"))
            if r0.returncode:
                continue
            h0 = heads(open(os.path.join(TMP, "dj", "b", "x.c")).read())
            for c in ctls:
                r1 = compile_c(w[2], base + c, os.path.join(TMP, "dj", "a", "x.c"))
                if r1.returncode:
                    bad += 1
                    msgs.append("%s %s: refused" % (w[0], c))
                    continue
                h1 = heads(open(os.path.join(TMP, "dj", "a", "x.c")).read())
                for fn in set(h0) | set(h1):
                    if h0.get(fn) == h1.get(fn):
                        continue
                    seen += 1
                    if not SUBJ.match(fn) or not (h1.get(fn) or "").startswith("static "):
                        bad += 1
                        msgs.append("%s %s %s: %s" % (w[0], " ".join(shape), c, fn))
    check(bad == 0 and seen > 0,
          "disjoint: %d changed definition heads under a control, every one a static subject "
          "(never an A1 entry-chain function)%s" % (seen, "" if not bad else ": " + "; ".join(msgs[:5])))


# ---- 4 GCC ------------------------------------------------------------------

def plant_inline(pattern, fn, flags):
    c = os.path.join(TMP, "gcc", fn + ".c")
    r = compile_c(pattern, flags, c)
    if r.returncode:
        return None
    t = open(c).read()
    t2, n = re.subn(r"^static ((?:\w+ )*?)(\w+ \**)%s\(" % re.escape(fn),
                    r"static inline __attribute__((always_inline)) \1\2%s(" % fn,
                    t, count=1, flags=re.M)
    if not n:
        return None
    open(c, "w").write(t2)
    return run([CC, "-O2", "-c", c, "-o", c + ".o"])


def sec_gcc():
    r = plant_inline("^(a)b", "rx_prefilter", [])
    check(r is not None and r.returncode != 0 and "can never be copied" in r.stderr,
          "gcc: always_inline on the attempt route's prefilter (a static label table) is "
          "refused, \"can never be copied\" (H1)")
    r = plant_inline("(a|ab)(c|bcd)(d*)", "rx_match_anchored", [])
    check(r is not None and r.returncode != 0 and "can never be inlined" in r.stderr,
          "gcc: always_inline on a framed VM body (a computed goto) is refused, \"can never be "
          "inlined\" (H2)")


# ---- 5 CENSUS ---------------------------------------------------------------

CENSUS_CTLS = [
    [], ["--part-residual=shared"], ["--part-residual=inline"], ["--part-inline-rank=R2"],
    ["--part-layout=prefilter:shared,compound:inline"],
    ["--part-layout=prefilter:auto", "--part-residual=inline"],
    ["--part-layout=prefilter:inline"], ["--part-inline-rank=measured"],
    ["--part-inline-rank=R3"],
]
# The row floors: per-row totals summed over CENSUS_CTLS on population.txt,
# MEASURED at the lane's landing (T0 828, P2 658, P3 1379, P4-P6 123 each,
# P7 182, P8 123, P9 123, P10 64), each cut to about half, so a floor is a
# reach claim and not a pin.
ROW_FLOORS = {"T0": 400, "P2": 300, "P3": 650, "P4": 60, "P5": 60, "P6": 60,
              "P7": 90, "P8": 60, "P9": 60, "P10": 30}


def load_writers():
    out = []
    for w in rows(os.path.join(HERE, "writers.tsv")):
        out.append((w[0], w[1], re.compile(w[2])))
    return out


def attributes(text):
    """[(kind, name)] for every attribute occurrence in the artifact."""
    lines = text.split("\n")
    out = []
    for i, l in enumerate(lines):
        if l.startswith("#"):
            continue
        if l.strip() == "__attribute__((noclone))":
            j = i + 1
            while j < len(lines) and lines[j].startswith("#"):
                j += 1
            m = re.search(r"\b(rx\w*)\(", lines[j])
            out.append(("noclone", m.group(1) if m else "?"))
            continue
        if l.startswith((" ", "\t")):
            continue
        kinds = re.findall(r"\b(always_inline|noinline)\b", l)
        if not kinds and not l.startswith("static inline "):
            continue
        m = re.search(r"\b(rx\w*)\(", re.sub(r"__attribute__\(\(\w+\)\)", "", l))
        name = m.group(1) if m else "?"
        for k in (kinds or ["static-inline"]):
            out.append((k, name))
    return out


def census_one(job):
    pattern, ctl, idx, ci = job
    wd = os.path.join(TMP, "cs", str(idx), str(ci))
    r = compile_c(pattern, ctl, os.path.join(wd, "x.c"))
    if r.returncode:
        return (idx, ci, None, None, r.stderr)
    text = open(os.path.join(wd, "x.c")).read()
    f = facts(pattern, ctl)
    return (idx, ci, attributes(text), f, "")


def sec_census(pop):
    writers = load_writers()
    jobs = [(p, c, i, ci) for i, p in enumerate(pop) for ci, c in enumerate(CENSUS_CTLS)]
    with cf.ThreadPoolExecutor(JOBS) as ex:
        res = list(ex.map(census_one, jobs))
    unlisted, rowcount, multi, nosubj = {}, {}, [], set()
    reached = set()
    seam_bad = []
    for idx, ci, attrs, f, err in res:
        if attrs is None:
            continue
        for kind, name in attrs:
            pname = re.sub(r"^rx", "P", name)
            if not any(k == kind and rx.match(pname) for _, k, rx in writers):
                unlisted.setdefault((kind, pname), pop[idx])
        if f is None:
            continue
        parts, ctl = f
        subj = [p for p in parts if p[2] != "owned"]
        if subj:
            reached.add(idx)
        names = [p[1] for p in subj]
        if len(names) != len(set(names)):
            multi.append(pop[idx])
        for p in subj:
            rid = p[6].split()[0]
            rowcount[rid] = rowcount.get(rid, 0) + 1
    check(not unlisted, "census: every attribute in %d artifacts belongs to a writer in "
          "writers.tsv%s" % (len(res), "" if not unlisted else ": unlisted " + "; ".join(
              "%s on %s (%r)" % (k, n, p) for (k, n), p in list(unlisted.items())[:5])))
    check(not multi, "census: every subject reaches exactly one row (one record each)%s"
          % ("" if not multi else ": " + "; ".join(map(repr, multi[:3]))))
    lost = [pop[i] for i in range(len(pop)) if i not in reached]
    check(not lost and len(pop) >= 380,
          "census: all %d population patterns still carry a subject (floor 380)%s"
          % (len(pop), "" if not lost else ": lost " + "; ".join(map(repr, lost[:3]))))
    line = ", ".join("%s %d" % (k, rowcount.get(k, 0))
                     for k in ("T0", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10"))
    low = [k for k, fl in ROW_FLOORS.items() if rowcount.get(k, 0) < fl]
    check(not low, "census: row populations over %d settings: %s (P1 is the owned rows; "
          "every floor met%s)" % (len(CENSUS_CTLS), line, "" if not low else ", BELOW: " + ",".join(low)))
    print("NOTE: row population per setting is in %s" % os.path.join(TMP, "cs"))


def sec_seam():
    pats_ = ["(a)\\1", "(?i)(ab)\\1", "(?<=ab)c", "(a)\\1x", "(\\w+) \\1"]
    bad, seen = [], 0
    for enc in ([], ["-e", "utf8"]):
        for p in pats_:
            c = os.path.join(TMP, "seam", "x.c")
            r = compile_c(p, enc, c)
            if r.returncode:
                continue
            t = open(c).read()
            for m in re.finditer(r"^static inline [^\n]*\b(rx_(?:span_match\w*|back_step|decode|"
                                 r"bref_match\w*))\(([^\n]*\n)(.*?)^}", t, re.M | re.S):
                seen += 1
                if re.search(r"&&\w", m.group(3)) or "goto *" in m.group(3):
                    bad.append(m.group(1))
    check(seen > 0 and not bad, "seam: %d encoding-seam bodies, none with a label table or a "
          "computed goto (copyable inside P1)%s" % (seen, "" if not bad else ": " + ",".join(bad)))


# ---- 6 NEUTRAL --------------------------------------------------------------

NEUTRAL_CTLS = [["--part-residual=shared"], ["--part-residual=inline"],
                ["--part-inline-rank=R0", "--part-layout=compound:inline"],
                ["--part-inline-rank=measured"]]
ALL_AUTO = ["--part-layout=prefilter:auto,compound:auto,find:auto,wrap:auto",
            "--part-residual=auto", "--part-inline-rank=none"]


def defines(text):
    return sorted(l for l in text.split("\n") if l.startswith("#define RX_")
                  and not l.startswith(("#define RX_TUNE ", "#define RX_PART_LAYOUT")))


def neutral_one(job):
    pattern, idx = job
    wd = os.path.join(TMP, "nt", str(idx))
    base = compile_c(pattern, ["--warn-emit-bytes=1"], os.path.join(wd, "b", "x.c"))
    note = lambda r: re.findall(r"large artifact: \d+ bytes of emitted C source \(\d+ of code\)",
                                r.stderr)
    bt = open(os.path.join(wd, "b", "x.c")).read() if base.returncode == 0 else None
    bad = []
    for c in NEUTRAL_CTLS:
        r = compile_c(pattern, ["--warn-emit-bytes=1"] + c, os.path.join(wd, "a", "x.c"))
        if (r.returncode == 0) != (base.returncode == 0):
            bad.append("%s: refusal moved" % c)
            continue
        if r.returncode:
            continue
        if note(r) != note(base):
            bad.append("%s: decision sizes %s != %s" % (c, note(r), note(base)))
        if defines(open(os.path.join(wd, "a", "x.c")).read()) != defines(bt):
            bad.append("%s: a stamp moved" % c)
    r = compile_c(pattern, ALL_AUTO, os.path.join(wd, "a", "x.c"))
    if base.returncode == 0:
        b2 = compile_c(pattern, [], os.path.join(wd, "b", "x.c"))
        if r.returncode or open(os.path.join(wd, "a", "x.c")).read() != \
                open(os.path.join(wd, "b", "x.c")).read():
            bad.append("all-auto: not byte-identical to no control")
    return idx, base.returncode == 0, bad


def sec_neutral(pop, near):
    allp = pop + near
    with cf.ThreadPoolExecutor(JOBS) as ex:
        res = list(ex.map(neutral_one, [(p, i) for i, p in enumerate(allp)]))
    bad = [(allp[i], b) for i, ok, b in res if b]
    compiled = sum(1 for _, ok, _ in res if ok)
    check(not bad and compiled >= 380,
          "neutral: %d artifacts (%d near-cap) under %d controls: the refusal, every stamp but "
          "_TUNE/_PART_LAYOUT* and the decision sizes unmoved; all-auto byte-identical%s"
          % (compiled, len(near), len(NEUTRAL_CTLS),
             "" if not bad else ": " + "; ".join("%r %s" % (p, b[0]) for p, b in bad[:4])))


def main():
    if not os.path.exists(PCREC):
        sys.exit("run_partlayout: no pcrec at %s" % PCREC)
    pop = pats(os.path.join(HERE, "population.txt"))
    near = pats(os.path.join(HERE, "nearcap.txt"))
    print("== 1 object (the independent evaluator)")
    sec_object()
    print("== 2 fixtures (hand-written precedence and held rows)")
    sec_fixtures()
    print("== 3 disjoint (A1 and the layout rows)")
    sec_disjoint()
    print("== 4 gcc (H1/H2 by construction)")
    sec_gcc()
    print("== 5 census (writers, totality, row populations, the seam)")
    sec_census(pop)
    sec_seam()
    print("== 6 neutral (I5 and T0)")
    sec_neutral(pop, near)
    print("== 7 T2")
    print("UNREACHED: rows TM and T2 -- no compile carries a measurement set ([MEASURE-SET] M0 "
          "is not built), so theta_hot is never a rank or `none`; `measured` always takes T1, "
          "which section 1 and fixtures `measured-*` check")
    print()
    print("checks passed: %d" % passed)
    print("checks failed: %d" % failed)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
