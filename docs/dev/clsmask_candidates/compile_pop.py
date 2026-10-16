#!/usr/bin/env python3
"""clsmask_candidates stage 1: compile every distinct pattern of the merged
populations under two configs and keep the compiler's OWN outputs.

    compile_pop.py PCREC WORK POP.tsv... > WORK/compiled.tsv

Distinct key = (enc, icase, extra args, pattern bytes). Configs:
  auto  -- default selection (what a user gets)
  vm    -- --engine=vm (the VM forced; no DFA prefilter, so the attempt
           loop is the VM's own)
both with `--features all` (the bench's pcrec-auto testee does the same) and
the pattern passed through `--pattern-esc`. Per (key, config) the emitted C
goes to WORK/art/<h>/<config>.c, and `--emit-ir` / `--emit-facts` listings
beside it (the IR listing only when the artifact is VM-routed). Rows:
  h pid_first npids sources enc icase extra config rc engine pattern_hex
`rc` = ok | REFUSED (pcrec exit != 0, first stderr line in WORK/art/<h>/<config>.err).
Runs -j4 (box rule), each pcrec call under gnutimeout 120 s.
"""
import concurrent.futures as cf, hashlib, os, re, subprocess, sys

PCREC, WORK = sys.argv[1], os.path.abspath(sys.argv[2])
TO = "/usr/bin/gnutimeout"


def esc(b):
    o = []
    for c in b:
        if c == 0x5c: o.append("\\\\")
        elif c == 0x22: o.append('\\"')
        elif 0x20 <= c < 0x7f: o.append(chr(c))
        else: o.append("\\x%02x" % c)
    return "".join(o)


keys = {}
for pop in sys.argv[3:]:
    src = os.path.basename(pop).replace("pop_", "").replace(".tsv", "")
    lines = open(pop).read().split("\n")
    hdr = lines[0].split("\t")
    for ln in lines[1:]:
        if not ln:
            continue
        f = dict(zip(hdr, ln.split("\t")))
        k = (f["enc"], int(f["icase"]), f.get("extra", "").strip(), bytes.fromhex(f["pattern_hex"]))
        g = keys.setdefault(k, dict(pids=[], srcs=set()))
        if f["pid"] not in g["pids"]:
            g["pids"].append(f["pid"])
        g["srcs"].add(src)


def hkey(k):
    return hashlib.sha1(repr(k).encode()).hexdigest()[:16]


def one(k):
    enc, ic, extra, pat = k
    h = hkey(k)
    d = os.path.join(WORK, "art", h)
    os.makedirs(d, exist_ok=True)
    base = ["--features", "all"] + extra.split()
    if enc == "utf8" and "-e" not in extra.split():
        base += ["-e", "utf8"]
    if ic:
        base.append("-i")
    pa = ["--pattern-esc", "--pattern", '"' + esc(pat) + '"']
    out = []
    for cfg in ("auto", "vm"):
        args = base + (["--engine=vm"] if cfg == "vm" else [])
        c = os.path.join(d, cfg + ".c")
        r = subprocess.run([TO, "120", PCREC] + args + ["-o", c] + pa, capture_output=True)
        if r.returncode != 0:
            open(os.path.join(d, cfg + ".err"), "wb").write(r.stderr[:2000])
            out.append((h, cfg, "REFUSED", "")); continue
        eng = re.search(r'^#define RX_ENGINE "(\w+)"', open(c, errors="replace").read(), re.M)
        eng = eng.group(1) if eng else "?"
        if eng == "vm":
            r = subprocess.run([TO, "120", PCREC, "--emit-ir"] + args + pa, capture_output=True)
            open(os.path.join(d, cfg + ".ir"), "wb").write(r.stdout)
        r = subprocess.run([TO, "120", PCREC, "--emit-facts"] + args + pa, capture_output=True)
        open(os.path.join(d, cfg + ".facts"), "wb").write(r.stdout)
        out.append((h, cfg, "ok", eng))
    return k, out


print("h\tpid_first\tnpids\tsources\tenc\ticase\textra\tconfig\trc\tengine\tpattern_hex")
with cf.ThreadPoolExecutor(int(os.environ.get("JOBS", "4"))) as ex:
    for k, rows in ex.map(one, sorted(keys)):
        g = keys[k]
        for h, cfg, rc, eng in rows:
            print("\t".join([h, g["pids"][0], str(len(g["pids"])), ",".join(sorted(g["srcs"])),
                             k[0], str(k[1]), k[2], cfg, rc, eng, k[3].hex()]), flush=True)
