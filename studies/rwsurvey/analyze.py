#!/usr/bin/env python3
"""rwsurvey analyzer: read a probe dump (run_survey.py output) and print the
Q2/Q3 shape tables and the Q4 scan-edge reach table.

  analyze.py shapes DUMP        per-code counts: source-level (1-parse), per stage, created-at
  analyze.py hits DUMP CODE     list patterns with CODE at 1-parse (names + detail)
  analyze.py created DUMP       hits that first appear at a later stage than 1-parse
  analyze.py dfa DUMP           Q4 table
  analyze.py gains DUMP         the GAIN lines of patterns with a view-ok gain
"""
import re, sys, collections

STAGES = ["1-parse", "2-hooks", "3-altcls", "4-discharge", "5-select", "6-lower"]


def records(path):
    """yield dict(src, name, rc, pat, attempts=[{ast:{stage:str}, hits:[(stage,code,detail)], dfa:[...], gain:[...]}])"""
    cur = None
    att = None
    with open(path, "rb") as f:
        for raw in f:
            ln = raw.decode("utf-8", "replace").rstrip("\n")
            if ln.startswith("@@\tSRC\t"):
                if cur:
                    yield cur
                c = ln.split("\t")
                cur = dict(src=c[2], name=c[3], rc=None, pat=None, attempts=[])
                att = None
            elif ln.startswith("@@\tCOMPILE\t"):
                att = dict(ast={}, hits=[], dfa=[], gain=[])
                if cur:
                    cur["pat"] = ln.split("\t", 2)[2]
                    cur["attempts"].append(att)
            elif ln.startswith("@@\tRC\t"):
                if cur:
                    cur["rc"] = int(ln.split("\t")[2])
            elif att is not None:
                c = ln.split("\t")
                if c[0] == "AST":
                    att["ast"][c[1]] = c[2]
                elif c[0] == "HIT":
                    att["hits"].append((c[1], c[2], c[3] if len(c) > 3 else ""))
                elif c[0] == "DFA":
                    d = {"name": c[1]}
                    for kv in c[2:]:
                        k, _, v = kv.partition("=")
                        d[k] = int(v)
                    att["dfa"].append(d)
                elif c[0] == "GAIN":
                    att["gain"].append(c[1:])
    if cur:
        yield cur


def norm(detail):
    return re.sub(r"mode=\w+ ", "", detail)


def shapes(path):
    n = 0
    ok = 0
    src_pat = collections.Counter()
    stage_pat = collections.defaultdict(collections.Counter)
    created = collections.Counter()
    for r in records(path):
        n += 1
        if not r["attempts"]:
            continue
        ok += 1
        a = r["attempts"][0]
        by = collections.defaultdict(set)
        for st, code, det in a["hits"]:
            by[st].add((code, norm(det)))
        for code in {c for c, _ in by["1-parse"]}:
            src_pat[code] += 1
        for st in STAGES:
            for code in {c for c, _ in by[st]}:
                stage_pat[st][code] += 1
        for i in range(1, len(STAGES)):
            new = by[STAGES[i]] - by[STAGES[i - 1]]
            for code in {c for c, _ in new}:
                created[(STAGES[i], code)] += 1
    print("patterns: %d records, %d with a probe dump (compiled to the pipeline's first pass)" % (n, ok))
    codes = sorted({c for s in stage_pat.values() for c in s} | set(src_pat))
    print("code\tsource(1-parse)\t" + "\t".join(STAGES))
    for code in codes:
        print(code + "\t%d\t" % src_pat[code] + "\t".join(str(stage_pat[s][code]) for s in STAGES))
    print("-- first appears at a later stage (pattern counts):")
    for (st, code), v in sorted(created.items()):
        print("%s\t%s\t%d" % (st, code, v))


def hits(path, code, stage="1-parse"):
    for r in records(path):
        if not r["attempts"]:
            continue
        a = r["attempts"][0]
        ds = sorted({d for st, c, d in a["hits"] if st == stage and c == code})
        if ds:
            print("%s\t%s\t%s\t%s" % (r["src"], r["name"], r["pat"], " || ".join(ds)))


def created(path):
    for r in records(path):
        if not r["attempts"]:
            continue
        a = r["attempts"][0]
        by = collections.defaultdict(set)
        for st, code, det in a["hits"]:
            by[st].add((code, norm(det)))
        for i in range(1, len(STAGES)):
            for code, det in sorted(by[STAGES[i]] - by[STAGES[i - 1]]):
                print("%s\t%s\t%s\t%s\t%s\t%s" % (STAGES[i], code, r["src"], r["name"], r["pat"], det))


MACH = {"3004": "fwd", "3006": "rev", "405": "anch", "425": "nonempty", "426": "nonempty"}


def machines(a):
    out = []
    xi = 0
    for d in a["dfa"]:
        ln = str(d["line"])
        if ln == "448":
            nm = ["x-fwd", "x-rev", "x-anch"][min(xi, 2)]
            xi += 1
        else:
            nm = MACH.get(ln, "line" + ln)
        out.append((nm, d))
    return out


def dfa(path, filt=None):
    tot = collections.defaultdict(collections.Counter)
    npat = collections.defaultdict(collections.Counter)
    nrec = 0
    for r in records(path):
        if not r["attempts"] or (filt and not r["src"].startswith(filt)):
            continue
        nrec += 1
        a = r["attempts"][-1]          # the attempt that produced the artifact
        for nm, d in machines(a):
            t = tot[nm]
            t["machines"] += 1
            for k in ("mem_one", "mem_one_vok", "mem_set", "mem_set_vok",
                      "gain_self", "gain_self_vok", "gain_chain", "gain_chain_vok"):
                t[k] += d[k]
            p = npat[nm]
            p["has_machine"] += 1
            if d["mem_one"] > 0: p["one"] += 1
            if d["mem_one_vok"] > 0: p["one_vok"] += 1
            if d["mem_set"] > 0: p["set"] += 1
            if d["gain_self"] + d["gain_chain"] > 0: p["gain"] += 1
            if d["gain_self_vok"] + d["gain_chain_vok"] > 0: p["gain_vok"] += 1
            if d["gain_self_vok"] > 0: p["gain_self_vok"] += 1
    print("records with a DFA dump: %d" % nrec)
    hdr = ["machine", "patterns", "pat_one", "pat_one_vok", "pat_gain", "pat_gain_vok", "pat_gainloop_vok",
           "st_one", "st_one_vok", "st_gain_loop", "st_gain_chain", "st_gain_loop_vok", "st_gain_chain_vok"]
    print("\t".join(hdr))
    for nm in sorted(tot):
        t, p = tot[nm], npat[nm]
        print("\t".join(str(x) for x in [nm, p["has_machine"], p["one"], p["one_vok"], p["gain"], p["gain_vok"],
                                         p["gain_self_vok"], t["mem_one"], t["mem_one_vok"], t["gain_self"],
                                         t["gain_chain"], t["gain_self_vok"], t["gain_chain_vok"]]))


def gains(path, only_vok=True):
    for r in records(path):
        if not r["attempts"]:
            continue
        a = r["attempts"][-1]
        names = []
        for nm, d in machines(a):
            if d["gain_self_vok"] + d["gain_chain_vok"] > 0:
                names.append("%s(loop=%d,chain=%d)" % (nm, d["gain_self_vok"], d["gain_chain_vok"]))
        if names:
            print("%s\t%s\t%s\t%s" % (r["src"], r["name"], r["pat"], " ".join(names)))


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "shapes": shapes(sys.argv[2])
    elif m == "hits": hits(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "1-parse")
    elif m == "created": created(sys.argv[2])
    elif m == "dfa": dfa(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif m == "gains": gains(sys.argv[2])
