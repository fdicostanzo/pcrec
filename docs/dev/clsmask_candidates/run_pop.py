#!/usr/bin/env python3
"""clsmask_candidates stage 2: instrument + run every VM-routed artifact.

    run_pop.py WORK CORPUSDIR [JOBS]

Reads WORK/compiled.tsv (compile_pop.py) and WORK/pop_*.tsv. For every
(key, config) whose artifact is VM-routed (RX_ENGINE "vm"): instrument.py,
the evaluator (byte sets per site), the class assignment (sites with an
identical accepted set share a class; a utf8 code-point class is keyed on
its size + ASCII bitmap), gcc -O1 of inst.c + cs_drv.c, then runs:
  OWN    the pattern's own population subjects -- corpus: its short m/n
         subjects (search) and the three 16 KiB synthetic subjects
         (findall); bench: search_short (search) and throughput (findall);
         rw: its corpus head sample (findall)
  PANEL  a COMMON real-text panel, the same for every artifact (findall):
         64 KiB from each of six [REGIME-CORPUS] files, cut on line ends,
         taken at 1 MiB into the file when the file is larger than 2 MiB
         (to step past the sorted-file head bias)
Env: ONLY (a regex on the first pid; default all), OUT (an output-name
prefix, for a trial run beside the real one).
Every subject is read up to MAXBYTES = 256 KiB. Each run is under
gnutimeout 60 s; a timeout is recorded (rc=TIMEOUT), never skipped.
Writes WORK/static.tsv (one row per site) and WORK/runs.tsv (one row per
subject run). JOBS default 4; the caller pins CPUs (taskset -c 0-3).
"""
import concurrent.futures as cf, os, re, subprocess, sys

WORK, CORP = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
JOBS = int(sys.argv[3]) if len(sys.argv) > 3 else 4
HERE = os.path.dirname(os.path.abspath(__file__))
TO = "/usr/bin/gnutimeout"
MAXB = 256 * 1024
PANEL_FILES = ["logs/apache_access.log", "logs/linux_syslog.log", "code/c.src",
               "prose/pg1342.txt", "markup/python_docs.html", "structured/usgs_2024q1.csv"]


def make_panel():
    d = os.path.join(WORK, "panel")
    os.makedirs(d, exist_ok=True)
    out = []
    for rel in PANEL_FILES:
        p = os.path.join(CORP, rel)
        if not os.path.exists(p):
            continue
        sz = os.path.getsize(p)
        with open(p, "rb") as f:
            if sz > 2 * 1024 * 1024:
                f.seek(1024 * 1024)
                f.readline()
            b = f.read(64 * 1024 + 4096)
        b = b[:64 * 1024]
        k = b.rfind(b"\n")
        if k > 0:
            b = b[:k + 1]
        q = os.path.join(d, rel.replace("/", "__"))
        open(q, "wb").write(b)
        out.append(q)
    return out


PANEL = make_panel()

# own subjects per key
own = {}
for pop in sorted(f for f in os.listdir(WORK) if f.startswith("pop_") and f.endswith(".tsv")):
    lines = open(os.path.join(WORK, pop)).read().split("\n")
    hdr = lines[0].split("\t")
    for ln in lines[1:]:
        if not ln:
            continue
        f = dict(zip(hdr, ln.split("\t")))
        k = (f["enc"], int(f["icase"]), f.get("extra", "").strip(), f["pattern_hex"])
        reg = {"search": "search", "search_short": "search", "findall": "findall",
               "throughput": "findall"}.get(f["regime"])
        if not reg:
            continue
        s = own.setdefault(k, {})
        for x in f["subjects"].split(","):
            if x:
                s.setdefault((reg, x), None)

rows = []
for ln in open(os.path.join(WORK, "compiled.tsv")).read().split("\n")[1:]:
    if not ln:
        continue
    f = ln.split("\t")
    if f[8] == "ok" and f[9] == "vm" and re.search(os.environ.get("ONLY", ""), f[1]):
        rows.append(f)
OUT = os.environ.get("OUT", "")


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, **kw)


def one(f):
    h, pid, npids, srcs, enc, ic, extra, cfg = f[:8]
    pat = f[10]
    d = os.path.join(WORK, "inst", h + "." + cfg)
    os.makedirs(d, exist_ok=True)
    art = os.path.join(WORK, "art", h)
    c = os.path.join(art, cfg + ".c")
    hdr = os.path.join(art, cfg + ".h")
    st, rn = [], []
    tag = [h, cfg, pid]
    r = sh([sys.executable, os.path.join(HERE, "instrument.py"), c, d], timeout=300)
    if r.returncode != 0:
        return [tag + ["INSTFAIL"]], []
    for x in (cfg + ".h", "rx.h"):
        open(os.path.join(d, x), "wb").write(open(hdr, "rb").read())
    r = sh(["gcc", "-O0", "-w", "-I" + d, "-o", os.path.join(d, "ev"), os.path.join(d, "ev.c")], timeout=300)
    if r.returncode != 0:
        return [tag + ["EVFAIL", r.stderr.decode("utf8", "replace")[:200].replace("\n", " ").replace("\t", " ")]], []
    r = sh([TO, "120", os.path.join(d, "ev")])
    sets = {}
    for x in r.stdout.decode().split("\n"):
        p = x.split("\t")
        if len(p) == 3:
            sets[int(p[0])] = (int(p[1]), p[2])
    sl = open(os.path.join(d, "sites.tsv")).read().split("\n")
    meta = sl[0]
    cls, sc = {}, []
    for x in sl[2:]:
        if not x:
            continue
        p = x.split("\t")
        k = int(p[0]); form = p[2]
        n, bm = sets.get(k, (-1, "?"))
        key = ("u%d:%s" % (n, bm)) if form == "ucls" else bm
        role = 1 if p[1] == "start" else 0
        ci = cls.setdefault(("S:" if role else "") + key, len(cls))
        sc.append("%d %d %d" % (k, ci, role))
        st.append(tag + ["site", p[0], p[1], p[2], p[3], p[4], str(ci), str(n), bm, p[5]])
    st.append(tag + ["meta", meta])
    open(os.path.join(d, "sc"), "w").write("\n".join(sc) + "\n")
    r = sh(["gcc", "-O1", "-w", "-I" + d, "-o", os.path.join(d, "bin"), os.path.join(d, "inst.c"),
            os.path.join(HERE, "cs_drv.c")], timeout=600)
    if r.returncode != 0:
        return st + [tag + ["BUILDFAIL", r.stderr.decode("utf8", "replace")[:200].replace("\n", " ").replace("\t", " ")]], []
    k = (enc, int(ic), extra, pat)
    jobs = [("own", reg, x) for (reg, x) in own.get(k, {})] + [("panel", "findall", x) for x in PANEL]
    # short search subjects batch in one process; large ones run alone
    small = [j for j in jobs if j[1] == "search"]
    big = [j for j in jobs if j[1] != "search"]
    groups = ([small] if small else []) + [[j] for j in big]
    for g in groups:
        reg = g[0][1]
        cmd = [TO, "-s", "KILL", "60", os.path.join(d, "bin"), os.path.join(d, "sc"), reg,
               "1" if enc == "utf8" else "0", str(MAXB)] + [j[2] for j in g]
        r = sh(cmd)
        outl = [x for x in r.stdout.decode("utf8", "replace").split("\n") if x]
        for j, x in zip(g, outl):
            rn.append(tag + [j[0], os.path.basename(j[2])] + x.split("\t")[1:])
        for j in g[len(outl):]:
            rn.append(tag + [j[0], os.path.basename(j[2]), "-", reg, "TIMEOUT" if r.returncode in (124, 137) else "RC%d" % r.returncode])
    return st, rn


with open(os.path.join(WORK, OUT + "static.tsv"), "w") as fs, open(os.path.join(WORK, OUT + "runs.tsv"), "w") as fr:
    fs.write("h\tconfig\tpid\trow\tsite\tkind\tform\tlabel\tfn\tclass\tsetsize\tset\tline\n")
    fr.write("h\tconfig\tpid\tsrc\tsubject\tn\tregime\trc\tcalls\tnmatch\tattempts\tfails\tU_any\tB_any\tclasses\tsites\n")
    done = 0
    with cf.ThreadPoolExecutor(JOBS) as ex:
        for st, rn in ex.map(one, rows):
            for x in st:
                fs.write("\t".join(x) + "\n")
            for x in rn:
                fr.write("\t".join(x) + "\n")
            done += 1
            if done % 100 == 0:
                print("progress %d/%d" % (done, len(rows)), flush=True)
                fs.flush(); fr.flush()
print("== clsmask run_pop COMPLETE %d artifacts" % len(rows), flush=True)
