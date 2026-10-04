import sys, os, hashlib, importlib.util, io, contextlib
bench, out = sys.argv[1], sys.argv[2]
def load(setname, mod):
    d = os.path.join(bench, "bench", setname)
    sys.path.insert(0, d)
    spec = importlib.util.spec_from_file_location(setname + "_" + mod, os.path.join(d, mod + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
def committed(setname, mf):
    man = {}
    for ln in open(os.path.join(bench, "bench", setname, mf)):
        f = ln.rstrip("\n").split("\t")
        if len(f) >= 3 and f[0] != "id":
            man[f[0]] = f[2]
    return man
bad = 0
for tag, setname in (("cap", "capability"), ("syn", "syntax"), ("u8", "utf8"), ("log", "loglines")):
    d = os.path.join(out, tag); os.makedirs(d, exist_ok=True)
    g = load(setname, "gen_throughput_subjects")
    with contextlib.redirect_stdout(io.StringIO()):
        if setname == "loglines":
            g.main(["--out", d])
        else:
            g.OUT, g.MANIFEST = d, os.path.join(d, "manifest_throughput.tsv")
            g.main()
    man = committed(setname, "manifest_throughput.tsv")
    for sid, sha in man.items():
        p = os.path.join(d, sid + ".bin")
        ok = os.path.exists(p) and hashlib.sha256(open(p, "rb").read()).hexdigest() == sha
        print("%s:%s %s" % (tag, sid, "OK" if ok else "SHA-MISMATCH")); bad += not ok
# the per-call subjects: capability's short subjects named for union-select
g = load("capability", "gen_subjects")
man = committed("capability", "manifest.tsv")
want = {ln.split("\t")[1] for ln in open(os.path.join(bench, "bench/capability/expectations.tsv"))
        if ln.startswith("wild-waf-crs-942270-union-select\t") and "\tsearch_short\t" in ln}
d = os.path.join(out, "short"); os.makedirs(d, exist_ok=True)
for sid, _desc, body in g.build():
    if sid in want:
        ok = man.get(sid) == hashlib.sha256(body).hexdigest()
        open(os.path.join(d, sid + ".bin"), "wb").write(body)
        print("short:%s %s" % (sid, "OK" if ok else "SHA-MISMATCH")); bad += not ok
sys.exit(1 if bad else 0)
