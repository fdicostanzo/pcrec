#!/usr/bin/env python3
"""sbscope census: which single-byte / set scan form each artifact carries today.

Run (from any cwd; nothing is written outside OUT):

    taskset -c 12-15 python3 -I census.py --tree MAIN_TREE --bench BENCH_TREE \
        --out OUT [--jobs 4]

MAIN_TREE is a checkout of main with `build/pcrec` built (read only).
BENCH_TREE is the pcrec-bench checkout (read only: bench/*/patterns/*.rx).

Populations (one compile each, `-p rx --features all -o -`, the stamps read
off the emitted text, nothing written to disk but OUT):
  corpus   every `pattern`/`pattern-esc` line of MAIN_TREE/tests/**/*.rxt,
           enumerated by scripts/emit_sweep.py's own `enumerate_corpus`
           (default encoding and flags: the block's own `flags`/`encoding`
           are NOT applied, emit_sweep's convention)
  bench    every bench/*/patterns/*.rx, raw bytes; the utf8 set under
           `-e utf8` (its subbench.toml), every other set under `byte`
  rwquest  docs/dev/lanes/rwquest/questions.tsv on MAIN_TREE, 177 rows;
           flags mapped: i -> -i, utf -> -e utf8, ucp -> --ucp,
           m -> a `(?m)` prefix, s -> a `(?s)` prefix

Per artifact it records the stamps that name a start-search form, the size
of every 256-entry candidate table the artifact emits, and a SITE list:
  PF:<form>      RX_DFA_PREFILTER on an unanchored DFA body or a VM hybrid's
                 prefilter (route DFA / HYB)
  MLINE          RX_DFA_SCAN "attempt" with RX_DFA_PREFILTER "memchr"
  VMHAT          RX_VM_START_SCAN "first-class"
  PRE:byte|run   RX_REQ_WHY emitted/set-leads (byte = no necessary run)
  LEAD           RX_REQ_WHY from the set-leads row (its leading memchr)
  HANDOFF        RX_REQ_HANDOFF != "none"
Writes OUT/rows.tsv (one row per compile), OUT/summary.txt and
OUT/rwquest_forms.tsv (one row per question). The grouped classes are
`classes_of`'s: SB-* a single-byte search, SET-* a set scan, OFS-* the
offset/run rows (the kit's fn rows pick memchr or the pair), RUN-* a run.
"""
import argparse, collections, glob, os, re, subprocess, sys
from multiprocessing import Pool

STAMPS = ("ENGINE", "VM_PREFILTER", "DFA_SCAN", "DFA_PREFILTER", "DFA_START",
          "VM_START_SCAN", "REQ_BYTE", "REQ_RUN", "REQ_WHY", "REQ_HANDOFF",
          "MEMFN_LIBC", "COMPOUND", "VM_RESEED")
STAMP_RX = re.compile(rb'^#define RX_([A-Z_]+) "?([^"\n]*)"?\s*$', re.M)
TABLE_RX = re.compile(rb'rx_(can_begin_match|start_bytes|start_set)\[256\] = \{([^}]*)\}')
PCREC = None


def compile_one(item):
    pop, ident, argv_extra, pattern = item
    argv = [PCREC, "-p", "rx", "--features", "all"] + argv_extra + ["-o", "-", "--pattern", pattern]
    try:
        r = subprocess.run(argv, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return (pop, ident, "timeout", {}, {})
    if r.returncode != 0:
        return (pop, ident, "refused", {}, {})
    st = {}
    for k, v in STAMP_RX.findall(r.stdout):
        k = k.decode()
        if k in STAMPS:
            st[k] = v.decode()
    tabs = {}
    for name, body in TABLE_RX.findall(r.stdout):
        n = sum(1 for x in body.split(b",") if x.strip() == b"1")
        tabs[name.decode()] = n
    return (pop, ident, "ok", st, tabs)


def sites_of(st, tabs=None):
    """The start-search sites of one artifact (module docstring), plus the
    one-byte refinements: PF one-member forms, HANDOFF:byte|run (the
    landmark), VMHAT:1 (a one-member VM hat table). A compound artifact's
    stamps read "compound" (its parts are not inspected here): COMPOUND."""
    if st.get("COMPOUND") not in (None, "none") or st.get("DFA_PREFILTER") == "compound":
        return ["COMPOUND"]
    s = []
    eng, pf = st.get("ENGINE"), st.get("DFA_PREFILTER")
    if pf is not None:
        if st.get("DFA_SCAN") == "attempt":
            if pf == "memchr":
                s.append("MLINE")
        elif pf != "none":
            route = "HYB" if eng == "vm" else "DFA"
            s.append(f"PF:{route}:{pf}")
    if st.get("VM_START_SCAN") == "first-class":
        s.append("VMHAT")
        if tabs and tabs.get("start_set") == 1:
            s.append("VMHAT:1")
    why = st.get("REQ_WHY")
    norun = st.get("REQ_RUN") in (None, "none")
    if why == "emitted":
        s.append("PRE:" + ("byte" if norun else "run"))
    if st.get("REQ_HANDOFF") not in (None, "none"):
        s.append("HANDOFF:" + ("byte" if norun else "run"))
    return s


ONE_BYTE_PF = ("memchr", "memchr-bounded", "first-memchr-bounded")
SET_PF = ("byte-class", "byte-class-bounded", "first-class-bounded")
OFS_PF = ("offset-set", "offset-set-bounded", "run-pinned", "run-pinned-bounded")


def classes_of(sites):
    """The report's grouped classes (sbscope_report.md section 7)."""
    c = set()
    for x in sites:
        if x.startswith("PF:"):
            _, route, form = x.split(":", 2)
            if form in ONE_BYTE_PF: c.add(f"SB-PF-{route}")
            elif form in SET_PF: c.add(f"SET-PF-{route}")
            elif form in OFS_PF: c.add(f"OFS-{route}")
            elif form == "handoff": c.add("NEXT-HANDOFF")
            else: c.add(f"PF-OTHER:{form}")
        elif x == "MLINE": c.add("SB-MLINE")
        elif x == "VMHAT": c.add("SET-VMHAT")
        elif x == "VMHAT:1": c.add("SB-VMHAT-1")
        elif x == "PRE:byte": c.add("SB-PRE")
        elif x == "PRE:run": c.add("RUN-PRE")
        elif x == "HANDOFF:byte": c.add("SB-HANDOFF")
        elif x == "HANDOFF:run": c.add("RUN-HANDOFF")
        elif x == "COMPOUND": c.add("COMPOUND")
    return c


def corpus_items(tree):
    sys.path.insert(0, os.path.join(tree, "scripts"))
    import emit_sweep  # noqa: E402  (read-only use of its enumerator)
    out = []
    for i, (f, kind, pat) in enumerate(emit_sweep.enumerate_corpus(PCREC, tree, 60)):
        out.append(("corpus", f"{f}#{i}", [], pat))
    return out


def bench_items(bench):
    out = []
    for path in sorted(glob.glob(os.path.join(bench, "bench", "*", "patterns", "*.rx"))):
        setname = path.split(os.sep)[-3]
        with open(path, "rb") as fh:
            raw = fh.read()
        if raw.endswith(b"\n"):
            raw = raw[:-1]
        pat = raw.decode("utf-8", "surrogateescape")
        extra = ["-e", "utf8"] if setname == "utf8" else []
        out.append(("bench", f"{setname}/{os.path.basename(path)[:-3]}", extra, pat))
    return out


def rwquest_items(tree):
    out = []
    path = os.path.join(tree, "docs", "dev", "lanes", "rwquest", "questions.tsv")
    with open(path, encoding="utf-8", errors="surrogateescape") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            row = dict(zip(hdr, line.rstrip("\n").split("\t")))
            flags = [] if row["flags"] in ("-", "") else row["flags"].split(",")
            extra, prefix = [], ""
            for fl in flags:
                if fl == "i": extra.append("-i")
                elif fl == "utf": extra += ["-e", "utf8"]
                elif fl == "ucp": extra.append("--ucp")
                elif fl == "m": prefix += "(?m)"
                elif fl == "s": prefix += "(?s)"
                else: raise SystemExit(f"unmapped flag {fl!r} in {row['id']}")
            out.append(("rwquest", row["id"], extra, prefix + row["pattern"]))
    return out


def main():
    global PCREC
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("--bench", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    PCREC = os.path.join(a.tree, "build", "pcrec")
    items = rwquest_items(a.tree) + bench_items(a.bench) + corpus_items(a.tree)
    os.makedirs(a.out, exist_ok=True)
    with Pool(a.jobs, initializer=_init, initargs=(PCREC,)) as pool:
        res = pool.map(compile_one, items, chunksize=8)
    with open(os.path.join(a.out, "rows.tsv"), "w", encoding="utf-8", errors="surrogateescape") as fh:
        fh.write("pop\tid\tstatus\tsites\ttables\t" + "\t".join(STAMPS) + "\n")
        for pop, ident, status, st, tabs in res:
            fh.write("\t".join([pop, ident, status, ",".join(sites_of(st, tabs)) or "-",
                                ",".join(f"{k}={v}" for k, v in sorted(tabs.items())) or "-"]
                               + [st.get(k, "") for k in STAMPS]) + "\n")
    summarize(res, os.path.join(a.out, "summary.txt"), a.out)


def _init(p):
    global PCREC
    PCREC = p


def summarize(res, path, outdir):
    lines = []
    for pop in ("rwquest", "bench", "corpus"):
        rows = [r for r in res if r[0] == pop]
        ok = [r for r in rows if r[2] == "ok"]
        lines.append(f"== {pop}: {len(rows)} compiles, {len(ok)} ok, "
                     f"{sum(r[2]=='refused' for r in rows)} refused, "
                     f"{sum(r[2]=='timeout' for r in rows)} timeout")
        site, cls, libc = collections.Counter(), collections.Counter(), collections.Counter()
        anysb = anystart = 0
        pfsize, vmsize = collections.Counter(), collections.Counter()
        for _, _, _, st, tabs in ok:
            ss = sites_of(st, tabs)
            cc = classes_of(ss)
            for x in set(ss): site[x] += 1
            for x in cc: cls[x] += 1
            if any(x.startswith("SB-") for x in cc): anysb += 1
            if any(x.startswith(("PF:", "MLINE", "VMHAT")) for x in ss): anystart += 1
            libc[st.get("MEMFN_LIBC", "?")] += 1
            for k, v in tabs.items():
                (pfsize if k in ("can_begin_match", "start_bytes") else vmsize)[_bucket(v)] += 1
        lines.append(f"  artifacts with a start-search site (PF/MLINE/VMHAT): {anystart}")
        lines.append(f"  artifacts with ANY single-byte search (an SB-* class): {anysb}")
        lines.append("  classes:")
        for k, v in sorted(cls.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"    {v:6d}  {k}")
        lines.append("  sites (stamp-level):")
        for k, v in sorted(site.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"    {v:6d}  {k}")
        lines.append("  RX_MEMFN_LIBC:")
        for k, v in sorted(libc.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"    {v:6d}  {k}")
        lines.append("  DFA candidate-table sizes (can_begin_match/start_bytes): "
                     + ", ".join(f"{k}:{v}" for k, v in sorted(pfsize.items())))
        lines.append("  VM hat table sizes (start_set): "
                     + ", ".join(f"{k}:{v}" for k, v in sorted(vmsize.items())))
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    with open(os.path.join(outdir, "rwquest_forms.tsv"), "w") as fh:
        fh.write("id\tstatus\tclasses\tsites\tlibc\n")
        for pop, ident, status, st, tabs in res:
            if pop != "rwquest": continue
            ss = sites_of(st, tabs)
            fh.write(f"{ident}\t{status}\t{','.join(sorted(classes_of(ss))) or '-'}\t"
                     f"{','.join(ss) or '-'}\t{st.get('MEMFN_LIBC', '')}\n")
    print("\n".join(lines))


def _bucket(n):
    for lo, hi, name in ((1, 1, "a:1"), (2, 2, "b:2"), (3, 4, "c:3-4"), (5, 8, "d:5-8"),
                         (9, 16, "e:9-16"), (17, 64, "f:17-64"), (65, 255, "g:65-255")):
        if lo <= n <= hi:
            return name
    return f"z:{n}"


if __name__ == "__main__":
    main()
