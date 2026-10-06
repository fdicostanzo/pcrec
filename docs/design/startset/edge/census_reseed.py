#!/usr/bin/env python3
"""[START-SET] edge lane: the re-seed FORM on the real population.  For every
census row (../census.tsv) whose auto artifact is a DFA-hat MOVER under the
ruled rule (T = S ∩ E*, admitted iff T ⊊ E), build D0 (conditional re-seed),
D4 (none) and D5 (unconditional, pf_emit_ofs_reseed's form) and sweep each
against the base over every subject on the row's alphabet (../rev2/sweep.py's
alphabet rule), every startpos.  Answers whether S485's plant is answer-visible
on any corpus/bench mover, or only on search_uncond.py's constructed ones.
    census_reseed.py OUT_TSV        Env: PCREC, FSP, W, JOBS"""
import csv, itertools, os, sys, concurrent.futures as cf
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); 
import hat, mut

# ../rev2/sweep.py's bits() and per-row alphabet(), copied VERBATIM (that module runs main() on import)
def bits(h):
    b = bytes.fromhex(h); return {i for i in range(256) if b[i >> 3] >> (i & 7) & 1}

def alphabet(st, S, pat):
    E, cls = set(st["E"]), st["fwd_class"]
    pick = []
    def add(b):
        if b not in pick and len(pick) < 7: pick.append(b)
    pref = lambda xs: sorted(xs, key=lambda b: (not (0x20 < b < 0x7f), b != 10, b))
    for b in pref(S - E)[:2]: add(b)
    seen = {cls[b] for b in pick}
    for b in pref(S & E) + pref(set(range(256)) - S):
        if cls[b] not in seen: add(b); seen.add(cls[b])
    for b in pat:
        if 0x20 < b < 0x7f and chr(b).isalnum(): add(b)
    return pick


def row(job):
    i, r = job
    pat = bytes.fromhex(r["pat_hex"]).decode("utf-8", "surrogateescape")
    b = {"pat": pat, "flags": "", "enc": "utf8" if r["set"] == "utf8" else "byte", "engine": None, "frames": None, "xflags": []}
    d = os.path.join(os.environ["W"], "cr%d" % i)
    try: c = hat.classify(b, d)
    except Exception as e: return (r["kind"], r["name"], "error:" + str(e)[:60])
    if c.get("hat") != "dfa": return (r["kind"], r["name"], "not-a-mover:" + c.get("hat", c["status"]))
    S, m = c["S"], c["m"]; T = S & m["Estar"]
    arts = [("rx", open(c["path"]).read())]
    for p, mode in (("tc", "cond"), ("tn", "none"), ("tu", "uncond")):
        path, _ = hat.compile_block(b, d, p); arts.append((p, hat.dfa_twin(open(path).read(), p, T, mode)))
    exe = mut.build(d, arts)
    st = {"E": sorted(m["E"]), "fwd_class": hat.table(open(c["path"]).read(), "rx_forward_byte_class")}
    alpha = alphabet(st, S, pat.encode("utf-8", "surrogateescape"))
    L = 7 if len(alpha) <= 4 else 6 if len(alpha) <= 6 else 5
    subs = [bytes(t) for n in range(L + 1) for t in itertools.product(alpha, repeat=n)]
    cases = [(p, s) for s in subs for p in mut.starts(b, s)]
    res = mut.run(exe, cases)
    dc, dn, du = (sum(x[k] != x[0] for x in res) for k in (1, 2, 3))
    w = next(("%d %r" % cs for cs, x in zip(cases, res) if x[3] != x[0]), "")
    return (r["kind"], r["name"], "mover", "route=" + (c["vmpf"] or c["engine"]), "|S|=%d" % len(S), "|E|=%d" % len(m["E"]),
            "cases=%d" % len(cases), "cond=%d" % dc, "none=%d" % dn, "uncond=%d" % du, w)

rows = [r for r in csv.DictReader((l for l in open(os.path.join(HERE, "..", "census.tsv")) if not l.startswith("# ")), delimiter="\t")
        if r["status"] == "ok" and r["seeded"] == "1" and r["a_RX_DFA_PREFILTER"] in ("byte-class", "byte-class-bounded")
        and r["fs_nullable"] == "0" and r["fs_set"] and len(bits(r["fs_set"])) < 256]
with cf.ThreadPoolExecutor(int(os.environ.get("JOBS", "4"))) as ex: out = list(ex.map(row, enumerate(rows)))
with open(sys.argv[1], "w") as f:
    for o in out: f.write("\t".join(o) + "\n")
mv = [o for o in out if o[2] == "mover"]
print("rows %d, movers %d, cond>0 %d, none>0 %d, uncond>0 %d" % (len(out), len(mv), sum(o[7] != "cond=0" for o in mv),
      sum(o[8] != "none=0" for o in mv), sum(o[9] != "uncond=0" for o in mv)))
