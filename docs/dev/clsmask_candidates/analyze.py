#!/usr/bin/env python3
"""clsmask_candidates stage 3: per-artifact columns, the score, the ranking.

    analyze.py WORK OUTDIR

Reads WORK/compiled.tsv, WORK/static.tsv, WORK/runs.tsv and each VM
artifact's own --emit-ir / --emit-facts / emitted-C stamps. Writes:
  OUTDIR/artifacts.tsv.gz  one row per VM-routed artifact (config auto|vm),
                           every column below
  OUTDIR/top_vm.tsv, top_auto.tsv   the ranked top 20 per config
  OUTDIR/population.txt    the K35 population ledger
and prints the summary the memo quotes.

COLUMNS (letters = the brief's items):
 (a) ncls        distinct byte classes the VM PROGRAM tests (sites whose
                 predicates accept the same byte set = one class; literal
                 bytes and fold pairs are classes of size 1/2 and counted
                 apart: ncls_multi = classes of size >= 3, ncls_lit = size 1)
     nsites      program test sites; classes = "size x sites" per class
 (b) nrun        run sites (span-loop `while`, counted or not); nrun_poss =
                 those whose IR strategies row says POSSESSIFIED; strats =
                 the RX_VM_STRATS stamp; possessify = the IR summary m/n
 (c) on the PANEL (six 64 KiB real texts, the same for every artifact) and
     on the artifact's OWN subjects, summed over subjects:
     tpb    program class tests per subject byte  (T_prog / n)
     rev    re-visit factor  T_prog / U_any  (1 = every tested position
            tested once; >1 = backtracking or overlapping attempts re-test)
     cov    coverage  U_any / (64 * B_any): of the 64-byte blocks the
            program touches, the fraction of positions it tests
     runsh  share of program tests made at run sites
     spb    start-skip tests per byte (the attempt loop; forced VM only)
     att, fails  attempts and rx_fail arrivals per KiB (context only)
 (d) exp    expensive forms present: bitmap (table load), atom, ucls
            (utf8 code-point class), big (a class of >= 32 bytes)
 (e) start  the start set (--emit-facts start_set) and `shared`: yes when
            it equals the OR of the program classes that are subsets of
            it (one classify of the program's own classes also yields the
            start mask), `part` when some program class is a subset of it
            but the OR falls short, `no` otherwise
THE SCORE (stated, explicit; built from (b), (c), (e) only):
    serv = R + V + A   in tests per KiB of subject, where
       R = run-site tests            (each becomes a bit read or part of
                                      one ctz(~mask) advance)
       V = T_prog - U_any            (re-visits: a cached mask answers them)
       A = start-skip tests if shared == yes, else 0  (ctz over the start
           mask replaces the skip loop with the same classify)
    capped at T_prog + A (R and V can count one test twice)
    score = serv * cov_panel   (discounted by the fraction of each
           classified block the program actually uses)
Ranking uses the PANEL numbers (comparable across patterns); OWN numbers
are shown beside them.
"""
import collections, gzip, os, re, sys

WORK, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.makedirs(OUT, exist_ok=True)


def tsv(p):
    lines = open(p, errors="replace").read().split("\n")
    hdr = lines[0].split("\t")
    for ln in lines[1:]:
        if ln:
            yield dict(zip(hdr, ln.split("\t")))


comp = {}
for r in tsv(os.path.join(WORK, "compiled.tsv")):
    comp[(r["h"], r["config"])] = r

sites = collections.defaultdict(list)
meta = {}
fails = {}
for ln in open(os.path.join(WORK, "static.tsv"), errors="replace").read().split("\n")[1:]:
    f = ln.split("\t")
    if len(f) < 4:
        continue
    k = (f[0], f[1])
    if f[3] == "site":
        sites[k].append(dict(site=int(f[4]), kind=f[5], form=f[6], label=f[7], cls=int(f[9]),
                             size=int(f[10]), set=f[11]))
    elif f[3] == "meta":
        m = dict(x.split("=") for x in f[4].lstrip("#").split())
        meta[k] = {a: int(b) for a, b in m.items()}
    else:
        fails[k] = f[3]

runs = collections.defaultdict(list)
for r in tsv(os.path.join(WORK, "runs.tsv")):
    runs[(r["h"], r["config"])].append(r)


def bits(hexs):
    try:
        b = bytes.fromhex(hexs)
    except ValueError:
        return None
    return int.from_bytes(b, "little")


def ir_info(h, cfg):
    p = os.path.join(WORK, "art", h, cfg + ".ir")
    poss, kinds, summ = {}, {}, {}
    if not os.path.exists(p):
        return poss, summ
    sect = None
    for ln in open(p, errors="replace").read().split("\n"):
        if ln.startswith("#section"):
            sect = ln.split()[1]; continue
        if not ln or ln.startswith("#"):
            continue
        f = ln.split("\t")
        if sect == "strategies" and len(f) >= 3:
            poss[f[0]] = "POSSESSIFIED" in f[2] or f[1] == "possessive"
        elif sect == "summary" and len(f) >= 2:
            summ[f[0]] = f[1]
    return poss, summ


def stamp(h, cfg, name):
    p = os.path.join(WORK, "art", h, cfg + ".c")
    m = re.search(r'^#define RX_%s ("?)([^"\n]*)\1\s*$' % name, open(p, errors="replace").read(200000), re.M)
    return m.group(2) if m else ""


def start_set(h, cfg):
    p = os.path.join(WORK, "art", h, cfg + ".facts")
    if not os.path.exists(p):
        return None, None
    for ln in open(p, errors="replace").read().split("\n"):
        f = ln.split("\t")
        if len(f) >= 7 and f[1] == "start_set":
            if f[4] != "derived" or ":" not in f[6]:
                return None, f[6] or f[4]
            n, hx = f[6].split(":", 1)
            return bits(hx), int(n)
    return None, None


def agg(rs):
    a = collections.Counter()
    cls = collections.Counter(); clsU = collections.Counter(); clsB = collections.Counter()
    st = collections.Counter()
    to = 0
    for r in rs:
        if r.get("rc") in ("TIMEOUT",) or r.get("n") in (None, "-"):
            to += 1; continue
        if r["rc"] and r["rc"].startswith("RC"):
            to += 1; continue
        a["n"] += int(r["n"]); a["att"] += int(r["attempts"]); a["fails"] += int(r["fails"])
        a["U"] += int(r["U_any"]); a["B"] += int(r["B_any"]); a["nmatch"] += int(r["nmatch"])
        if r["classes"] != "-":
            for x in r["classes"].split(";"):
                c, t, u, b = (int(y) for y in x.split(":"))
                cls[c] += t; clsU[c] += u; clsB[c] += b
        if r["sites"] != "-":
            for x in r["sites"].split(";"):
                s, t = (int(y) for y in x.split(":"))
                st[s] += t
    return a, cls, clsU, clsB, st, to


rows = []
for (h, cfg), c in comp.items():
    if c["rc"] != "ok" or c["engine"] != "vm":
        continue
    k = (h, cfg)
    S = sites.get(k, [])
    prog = [s for s in S if s["kind"] != "start"]
    startsites = [s for s in S if s["kind"] == "start"]
    pcls = {}
    for s in prog:
        pcls.setdefault(s["cls"], dict(size=s["size"], set=s["set"], n=0, forms=set(), kinds=set()))
        pcls[s["cls"]]["n"] += 1
        pcls[s["cls"]]["forms"].add(s["form"]); pcls[s["cls"]]["kinds"].add(s["kind"])
    poss, summ = ir_info(h, cfg)
    runsites = [s for s in prog if s["kind"] in ("run_c", "run_u")]
    nrun_poss = sum(1 for s in runsites if poss.get(s["label"], False))
    ss, ssn = start_set(h, cfg)
    shared = "?"
    if ss is not None:
        sub = [bits(v["set"]) for v in pcls.values() if bits(v["set"]) is not None and "ucls" not in v["forms"]]
        sub = [b for b in sub if b and (b & ~ss) == 0]
        orr = 0
        for b in sub:
            orr |= b
        shared = "yes" if sub and orr == ss else ("part" if sub else "no")
    exp = set()
    for v in pcls.values():
        if "bitmap" in v["forms"]: exp.add("bitmap")
        if "atom" in v["forms"]: exp.add("atom")
        if "ucls" in v["forms"]: exp.add("ucls")
        if v["size"] >= 32 and "ucls" not in v["forms"]: exp.add("big")
    row = dict(h=h, config=cfg, pid=c["pid_first"], npids=c["npids"], sources=c["sources"], enc=c["enc"],
               icase=c["icase"], extra=c["extra"], pattern=bytes.fromhex(c["pattern_hex"]).decode("utf8", "replace"),
               status=fails.get(k, "ok"), unwrapped=meta.get(k, {}).get("unwrapped", ""),
               litrun=meta.get(k, {}).get("litrun", ""), bref=meta.get(k, {}).get("bref", ""),
               ncls=len(pcls), ncls_multi=sum(1 for v in pcls.values() if v["size"] >= 3 or "ucls" in v["forms"]),
               ncls_lit=sum(1 for v in pcls.values() if v["size"] == 1), nsites=len(prog),
               classes=",".join("%sx%d" % ("u" if "ucls" in v["forms"] else v["size"], v["n"])
                                for v in sorted(pcls.values(), key=lambda v: -v["n"])),
               nrun=len(runsites), nrun_poss=nrun_poss, strats=stamp(h, cfg, "VM_STRATS"),
               possessify=summ.get("possessify", ""), prefilter=stamp(h, cfg, "VM_PREFILTER"),
               start_scan=stamp(h, cfg, "VM_START_SCAN"),
               startsize=ssn if ss is not None else (ssn or ""), shared=shared, exp="+".join(sorted(exp)) or "-")
    runkinds = {s["site"] for s in runsites}
    pclsids = set(pcls)
    startcls = {s["cls"] for s in startsites}
    startids = {s["site"] for s in startsites}
    for part in ("panel", "own"):
        a, cls, clsU, clsB, st, to = agg([r for r in runs.get(k, []) if r["src"] == part])
        n = a["n"]
        Tp = sum(t for c2, t in cls.items() if c2 in pclsids)
        Ts = sum(t for s2, t in st.items() if s2 in startids)
        Tr = sum(t for s2, t in st.items() if s2 in runkinds)
        kib = n / 1024.0 if n else 0
        cov = a["U"] / (64.0 * a["B"]) if a["B"] else 0.0
        R = Tr; V = max(0, Tp - a["U"]); A = Ts if shared == "yes" else 0
        serv = min(R + V, Tp) + A
        pre = part + "_"
        row.update({pre + "n": n, pre + "timeouts": to, pre + "nmatch": a["nmatch"],
                    pre + "tpb": round(Tp / n, 4) if n else "",
                    pre + "rev": round(Tp / a["U"], 3) if a["U"] else "",
                    pre + "cov": round(cov, 3) if a["B"] else "",
                    pre + "runsh": round(Tr / Tp, 3) if Tp else "",
                    pre + "spb": round(Ts / n, 4) if n else "",
                    pre + "att_kib": round(a["att"] / kib, 2) if kib else "",
                    pre + "fails_kib": round(a["fails"] / kib, 2) if kib else "",
                    pre + "R_kib": round(R / kib, 2) if kib else "", pre + "V_kib": round(V / kib, 2) if kib else "",
                    pre + "A_kib": round(A / kib, 2) if kib else "",
                    pre + "score": round(serv / kib * cov, 2) if kib else 0.0})
        # the busiest program class: its own coverage and re-visit
        if cls:
            top = max((c2 for c2 in cls if c2 in pclsids), key=lambda c2: cls[c2], default=None)
            if top is not None:
                row[pre + "topcls"] = "%sx%d" % ("u" if "ucls" in pcls[top]["forms"] else pcls[top]["size"], pcls[top]["n"])
                row[pre + "topcls_tpb"] = round(cls[top] / n, 4) if n else ""
                row[pre + "topcls_cov"] = round(clsU[top] / (64.0 * clsB[top]), 3) if clsB[top] else ""
    rows.append(row)

cols = list(dict.fromkeys(k2 for r in rows for k2 in r))
with gzip.open(os.path.join(OUT, "artifacts.tsv.gz"), "wt") as f:
    f.write("\t".join(cols) + "\n")
    for r in rows:
        f.write("\t".join(str(r.get(c2, "")).replace("\t", " ").replace("\n", "\\n") for c2 in cols) + "\n")

SHOW = ["pid", "pattern", "config", "enc", "classes", "nrun", "nrun_poss", "strats", "possessify", "prefilter",
        "panel_tpb", "panel_rev", "panel_cov", "panel_runsh", "panel_spb", "startsize", "shared", "exp",
        "panel_R_kib", "panel_V_kib", "panel_A_kib", "panel_score", "own_tpb", "own_rev", "own_cov", "own_score",
        "panel_att_kib", "panel_fails_kib", "npids", "sources"]


def top(cfg, k=20):
    seen = set(); out = []
    for r in sorted((r for r in rows if r["config"] == cfg), key=lambda r: -float(r.get("panel_score") or 0)):
        key = (r["pattern"], r["enc"], r["icase"])
        if key in seen:
            continue
        seen.add(key); out.append(r)
        if len(out) == k:
            break
    with open(os.path.join(OUT, "top_%s.tsv" % cfg), "w") as f:
        f.write("rank\t" + "\t".join(SHOW) + "\n")
        for i, r in enumerate(out, 1):
            f.write("%d\t" % i + "\t".join(str(r.get(c2, "")).replace("\t", " ") for c2 in SHOW) + "\n")
    return out


for cfg in ("vm", "auto"):
    top(cfg)

# ---- K35 population ledger ---------------------------------------------
L = []
keys = {}
for (h, cfg), c in comp.items():
    keys.setdefault(h, c)
src = collections.Counter()
for c in keys.values():
    for s in c["sources"].split(","):
        src[s] += 1
L.append("distinct pattern keys (enc, icase, extra, pattern): %d" % len(keys))
L.append("  keys per source (a key in two sources counts in both): " + ", ".join("%s %d" % kv for kv in sorted(src.items())))
for cfg in ("auto", "vm"):
    cc = collections.Counter((c["rc"], c["engine"]) for (h, cf), c in comp.items() if cf == cfg)
    L.append("config %s: " % cfg + ", ".join("%s/%s %d" % (a, b or "-", n) for (a, b), n in sorted(cc.items())))
for cfg in ("auto", "vm"):
    rs = [r for r in rows if r["config"] == cfg]
    L.append("config %s VM-routed artifacts analysed: %d; instrument status: %s" % (
        cfg, len(rs), dict(collections.Counter(r["status"] for r in rs))))
    L.append("  with unwrapped subject reads > 0: %d; with literal-run compares: %d; with backref compares: %d" % (
        sum(1 for r in rs if r["unwrapped"] not in ("", 0)), sum(1 for r in rs if r["litrun"] not in ("", 0)),
        sum(1 for r in rs if r["bref"] not in ("", 0))))
    L.append("  with zero program class sites: %d; with >= 1 run site: %d; with >= 1 multi-byte class (size>=3 or utf8): %d" % (
        sum(1 for r in rs if r["nsites"] == 0), sum(1 for r in rs if r["nrun"] > 0), sum(1 for r in rs if r["ncls_multi"] > 0)))
    L.append("  subject runs with a timeout/abnormal exit: panel %d, own %d" % (
        sum(r.get("panel_timeouts", 0) for r in rs), sum(r.get("own_timeouts", 0) for r in rs)))
    L.append("  start set shared with program classes: %s" % dict(collections.Counter(r["shared"] for r in rs)))
    L.append("  expensive forms: %s" % dict(collections.Counter(r["exp"] for r in rs).most_common(8)))
open(os.path.join(OUT, "population.txt"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
