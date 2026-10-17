#!/usr/bin/env python3
"""clsmask_candidates: the instrument's validation.

    validate.py WORK SAMPLE_N > results/validation.txt

(1) KNOWN-ANSWER controls: three hand-counted artifacts (forced VM) whose
    per-class counts follow from the emitted program by hand; the expected
    numbers are written here, derived below, and compared exactly.
(2) INDEPENDENT CROSS-CHECK against walk_survey's load instrument
    (studies/walk_survey/: the SAME artifact text compiled -O0 with a
    compiler-inserted hook on every load, attributed to phases by call site,
    a mechanism that shares nothing with this study's source rewrite).
    For each of SAMPLE_N forced-VM byte-domain artifacts with no literal-
    run word compares, no backreference compares, no utf8 class sites and
    zero unwrapped reads, the walk_survey `vm`-phase load count must equal
    this instrument's  sum over program sites of T(site) x reads(form),
    reads = 2 for the bitmap form (it reads the byte twice), 1 otherwise --
    on every subject of a fixed three-text panel.
(3) FAILING-DIRECTION CONTROL: the same cross-check with the instrument
    sabotaged (CS_SABOTAGE=drop-range: the `range` form goes unrecognised,
    its reads uncounted). The check must report mismatches on every sampled
    artifact whose range sites were EVALUATED in the intact run (a range
    site the panel never reaches moves nothing, so it cannot be a witness).
"""
import os, random, subprocess, sys

WORK = os.path.abspath(sys.argv[1]); N = int(sys.argv[2])
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
WS = os.path.join(REPO, "studies", "walk_survey")
PCREC = os.path.join(REPO, "build", "pcrec")
VD = os.path.join(WORK, "validate")
os.makedirs(VD, exist_ok=True)


def sh(cmd, env=None, **kw):
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run(cmd, capture_output=True, env=e, **kw)


def build_cs(c, h, d, env=None):
    """instrument + build; returns (sites rows, meta, binary)"""
    os.makedirs(d, exist_ok=True)
    r = sh([sys.executable, os.path.join(HERE, "instrument.py"), c, d], env=env)
    assert r.returncode == 0, r.stderr
    hb = open(h, "rb").read()
    base = os.path.basename(h)
    for x in (base, "rx.h"):
        open(os.path.join(d, x), "wb").write(hb)
    sl = open(os.path.join(d, "sites.tsv")).read().split("\n")
    meta = sl[0]
    rows = [x.split("\t") for x in sl[2:] if x]
    # one class per site here: the cross-check needs per-site counts only
    open(os.path.join(d, "sc"), "w").write("".join("%s %s %d\n" % (p[0], p[0], p[1] == "start") for p in rows))
    r = sh(["gcc", "-O1", "-w", "-I" + d, "-o", os.path.join(d, "bin"), os.path.join(d, "inst.c"),
            os.path.join(HERE, "cs_drv.c")])
    assert r.returncode == 0, r.stderr[:500]
    return rows, meta, os.path.join(d, "bin"), os.path.join(d, "sc")


def cs_run(b, sc, subs, regime="findall"):
    r = sh(["/usr/bin/gnutimeout", "60", b, sc, regime, "0", "0"] + subs)
    out = []
    for ln in r.stdout.decode().split("\n"):
        if not ln:
            continue
        f = ln.split("\t")
        sites = {} if f[11] == "-" else {int(a): int(b) for a, b in (x.split(":") for x in f[11].split(";"))}
        cls = {} if f[10] == "-" else {int(x.split(":")[0]): [int(y) for y in x.split(":")[1:]] for x in f[10].split(";")}
        out.append(dict(subject=f[0], attempts=int(f[6]), fails=int(f[7]), U_any=int(f[8]), B_any=int(f[9]),
                        sites=sites, cls=cls, nmatch=int(f[5])))
    return out


def ws_run(c, h, d, subs):
    os.makedirs(d, exist_ok=True)
    # wsbuild names the copy rx.c/rx.h: point the artifact's include at it
    c2 = os.path.join(d, "src.c")
    open(c2, "w").write(open(c, errors="replace").read().replace('#include "%s"' % os.path.basename(h), '#include "rx.h"'))
    r = sh([sys.executable, os.path.join(WS, "wsbuild.py"), PCREC, d], env=dict(WS_SRC=c2, WS_HDR=h))
    assert r.returncode == 0, r.stdout + r.stderr
    r = sh(["/usr/bin/gnutimeout", "120", os.path.join(d, "bin"), os.path.join(d, "map"), "findall", "0"] + subs)
    lines = r.stdout.decode().split("\n")
    hdr = lines[0].split("\t")
    return [dict(zip(hdr, x.split("\t"))) for x in lines[1:] if x]


bad = 0
print("# clsmask_candidates instrument validation")
# ---- (1) known-answer controls -------------------------------------------
print("\n## (1) known-answer controls (forced VM, findall)")
kd = os.path.join(VD, "known")
os.makedirs(kd, exist_ok=True)
# Each case: pattern, subject, expected {site-kind-or-class: (T, U)} by hand.
# K1 `\d+` on "ab12cd345": the start skip (set \d) tests a,b (fail),1 (hit)
#    -> attempt at 2: the possessive run tests 1,2,c (3 tests) -> match 2..4;
#    findall resumes at 4: skip tests c,d,3 -> attempt at 6: run tests 3,4,5
#    and stops at the end (no read past n) -> match 6..9; resume at 9 = n.
#    start T = 2+1+2+1 = 6 (a,b,1,c,d,3), program T = 3+3 = 6, U = 6 each.
# K3 `x` on "yyxy": the memchr pre-check finds x; the start skip tests
#    y,y,x (3) -> attempt at 2: the program's literal test reads x (1) ->
#    match 2..3; resume at 3: the pre-check's memchr over "y" fails, so no
#    further skip test. start (3,3), program (1,1), attempts 1.
cases = [
    ("K1", r"\d+", b"ab12cd345", dict(start=(6, 6), prog=(6, 6), attempts=2, nmatch=2)),
    ("K3", r"x", b"yyxy", dict(start=(3, 3), prog=(1, 1), attempts=1, nmatch=1)),
]
for name, pat, subj, exp in cases:
    c = os.path.join(kd, name + ".c")
    r = sh([PCREC, "--engine=vm", "-o", c, "--pattern", pat])
    assert r.returncode == 0, r.stderr
    sp = os.path.join(kd, name + ".subj")
    open(sp, "wb").write(subj)
    rows, meta, b, sc = build_cs(c, c[:-2] + ".h", os.path.join(kd, name))
    res = cs_run(b, sc, [sp])[0]
    st = [int(p[0]) for p in rows if p[1] == "start"]
    pr = [int(p[0]) for p in rows if p[1] != "start"]
    T_s = sum(res["sites"].get(k, 0) for k in st)
    T_p = sum(res["sites"].get(k, 0) for k in pr)
    U_s = sum(res["cls"].get(k, [0, 0, 0])[1] for k in st[:1])
    got = dict(start=(T_s, U_s), prog=(T_p, res["U_any"]), attempts=res["attempts"], nmatch=res["nmatch"])
    ok = got == exp
    bad += not ok
    print("%s %-6s %-12r expected %s got %s -> %s" % (name, pat, subj, exp, got, "OK" if ok else "MISMATCH"))

# ---- (2)/(3) cross-check --------------------------------------------------
panel = [os.path.join(WORK, "panel", x) for x in ("logs__apache_access.log", "code__c.src", "prose__pg1342.txt")]
panel = [p for p in panel if os.path.exists(p)]
cands = []
for ln in open(os.path.join(WORK, "compiled.tsv")).read().split("\n")[1:]:
    f = ln.split("\t")
    if len(f) > 9 and f[7] == "vm" and f[8] == "ok" and f[4] == "byte":
        cands.append(f[0])
random.Random(20261016).shuffle(cands)


def eligible(h):
    d = os.path.join(VD, "probe", h)
    c = os.path.join(WORK, "art", h, "vm.c")
    r = sh([sys.executable, os.path.join(HERE, "instrument.py"), c, d])
    if r.returncode:
        return False
    sl = open(os.path.join(d, "sites.tsv")).read().split("\n")
    rows = [x.split("\t") for x in sl[2:] if x]
    return sl[0] == "#litrun=0 bref=0 unwrapped=0" and rows and not any(p[2] == "ucls" for p in rows) \
        and any(p[1] != "start" for p in rows)


sample = []
for h in cands:
    if len(sample) >= N:
        break
    if eligible(h):
        sample.append(h)
READS = dict(bitmap=2)
RANGE_LIVE = {}   # artifact -> range-site evaluations in the intact run (set by (2))


def crosscheck(label, env):
    global bad
    print("\n## %s" % label)
    print("artifact\tsubject\tws_T_vm\tcs_expected\tunwrapped\tranges\tverdict")
    mism = 0; checked = 0; ranged = 0; ranged_mism = 0
    live = {}
    for h in sample:
        c = os.path.join(WORK, "art", h, "vm.c"); hh = os.path.join(WORK, "art", h, "vm.h")
        rows, meta, b, sc = build_cs(c, hh, os.path.join(VD, label.split()[1], h), env)
        probe = open(os.path.join(VD, "probe", h, "sites.tsv")).read().split("\n")[2:]
        has_range = any(x.split("\t")[2] == "range" for x in probe if x)
        form = {int(p[0]): p[2] for p in rows}
        start = {int(p[0]) for p in rows if p[1] == "start"}
        cs = cs_run(b, sc, panel)
        ws = ws_run(c, hh, os.path.join(VD, "ws", h), panel)
        unw = meta.split("unwrapped=")[1]
        art_m = False
        live[h] = sum(t for x in cs for k, t in x["sites"].items() if form.get(k) == "range")
        for x, y in zip(cs, ws):
            exp = sum(t * READS.get(form[k], 1) for k, t in x["sites"].items() if k not in start)
            got = int(y.get("T_vm", "-1"))
            ok = exp == got
            checked += 1
            if not ok:
                mism += 1; art_m = True
            print("%s\t%s\t%d\t%d\t%s\t%d\t%s" % (h, x["subject"], got, exp, unw, has_range, "OK" if ok else "MISMATCH"))
        hit = RANGE_LIVE.get(h, 0) > 0 if RANGE_LIVE else has_range
        ranged += hit
        ranged_mism += hit and art_m
    print("SUMMARY %s: %d artifact x subject cells, %d mismatches; %d sampled artifacts have a range site%s, %d of them mismatch"
          % (label, checked, mism, ranged, " EVALUATED in the intact run" if RANGE_LIVE else "", ranged_mism))
    if not RANGE_LIVE:
        RANGE_LIVE.update(live)
    return mism, ranged, ranged_mism


m, _, _ = crosscheck("(2) cross-check (instrument intact)", None)
bad += m != 0
m, rg, rgm = crosscheck("(3) sabotage CS_SABOTAGE=drop-range (must go red)", dict(CS_SABOTAGE="drop-range"))
ctl_ok = rg > 0 and rgm == rg
bad += not ctl_ok
print("CONTROL %s: %d/%d range-bearing artifacts detected" % ("OK" if ctl_ok else "FAILED", rgm, rg))
print("\nVERDICT %s" % ("PASS" if bad == 0 else "FAIL (%d)" % bad))
