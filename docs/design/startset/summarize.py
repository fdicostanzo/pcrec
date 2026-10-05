#!/usr/bin/env python3
"""[START-SET] census summary (docs/design/startset.md §2). Reads census.tsv,
writes census_summary.json and prints the tables the note quotes.

Classification, per artifact (every row reads the census's own columns):

  route     auto: dfa | hybrid | vm-none;  forced (--engine=vm): vm-none
  anchored  start_anchor != unanchored (one attempt; [OPT-ANCHOR-VM] owns it)
  FS        the AST start set is a necessary condition: fs_nullable == 0 and
            fs_pop < 256
  RUN       a necessary run with a FINITE window offset bound (req_run_maxoff
            numeric) -- the K82 handoff's fact
  DFA-NARROW  (dfa / hybrid only) the machine is SEEDED and T = S_ast & E is a
            proper subset of E = the emitted can_begin_match: the DFA hat's
            reach (firstset_design.md 4.6.3's population, read per set)

Density: the share of capability's t-1m throughput subject (pcrec-bench,
read-only, its sha256 checked against the bench manifest) whose byte is in
the set -- the skip loop's L = (1-d)/d input (firstset_design.md 3.1).
"""
import collections, csv, hashlib, json, os, sys

CENSUS = sys.argv[1]
OUT = sys.argv[2]
BENCH = os.environ.get("BENCH", "/Users/fdicostanzo/pcrec-bench")
SUBJ = os.path.join(BENCH, "bench/capability/throughput/t-1m.bin")

subj = open(SUBJ, "rb").read()
sha = hashlib.sha256(subj).hexdigest()
man = open(os.path.join(BENCH, "bench/capability/manifest_throughput.tsv")).read()
assert sha in man, "t-1m.bin does not match the bench manifest -- STOP"
hist = collections.Counter(subj)
N = len(subj)

def bits(h):
    if not h: return None
    b = bytes.fromhex(h)
    return {i for i in range(256) if b[i >> 3] >> (i & 7) & 1}

def dens(s):
    return sum(hist[b] for b in s) / N if s is not None else None

rows = [r for r in csv.DictReader((l for l in open(CENSUS) if not l.startswith("# ")), delimiter="\t")]
ok = [r for r in rows if r["status"] == "ok"]

def route(r, forced=False):
    e, p = (r["v_RX_ENGINE"], r["v_RX_VM_PREFILTER"]) if forced else (r["a_RX_ENGINE"], r["a_RX_VM_PREFILTER"])
    if e == "dfa": return "dfa"
    if e == "vm": return "hybrid" if p == "hybrid" else "vm-none"
    return "refused"

def cls(r):
    fs = bits(r["fs_set"])
    c = {}
    c["anchored"] = r["start_anchor"] not in ("unanchored", "")
    c["FS"] = r["fs_nullable"] == "0" and len(fs) < 256
    c["RUN"] = r["maxoff"].isdigit()
    c["run_any"] = r["req_run"] not in ("none", "")
    c["fs_pop"] = len(fs)
    e = bits(r["cbm_set"])
    c["E_pop"] = len(e) if e is not None else -1
    c["DFA_NARROW"] = bool(r["seeded"] == "1" and e is not None and c["FS"] and (fs & e) < e)
    c["T_pop"] = len(fs & e) if (e is not None and c["FS"]) else -1
    c["d_S"] = dens(fs) if c["FS"] else None
    c["d_E"] = dens(e) if e else None
    c["d_T"] = dens(fs & e) if (e and c["FS"]) else None
    return c

summary = {"subject_sha256": sha, "subject_bytes": N}
detail = []
for kind in ("bench", "corpus"):
    R = [r for r in rows if r["kind"] == kind]
    K = [r for r in R if r["status"] == "ok"]
    S = {"rows": len(R), "compiled": len(K)}
    for forced in (False, True):
        tag = "forced_vm" if forced else "auto"
        rt = collections.Counter(route(r, forced) for r in K)
        S[tag + "_routes"] = dict(rt)
        pop = [r for r in K if route(r, forced) == "vm-none"]
        cc = [cls(r) for r in pop]
        un = [c for c in cc if not c["anchored"]]
        S[tag + "_vmnone"] = {
            "total": len(pop), "anchored": sum(c["anchored"] for c in cc),
            "unanchored": len(un),
            "FS": sum(c["FS"] for c in un), "RUN": sum(c["RUN"] for c in un),
            "FS_and_RUN": sum(c["FS"] and c["RUN"] for c in un),
            "FS_only": sum(c["FS"] and not c["RUN"] for c in un),
            "RUN_only": sum(c["RUN"] and not c["FS"] for c in un),
            "neither": sum(not c["FS"] and not c["RUN"] for c in un),
            "run_present_unbounded": sum(c["run_any"] and not c["RUN"] for c in un),
            "FS_pop_le_1": sum(c["FS"] and c["fs_pop"] <= 1 for c in un),
            "FS_pop_le_3": sum(c["FS"] and c["fs_pop"] <= 3 for c in un),
            "FS_pop_le_16": sum(c["FS"] and c["fs_pop"] <= 16 for c in un),
        }
    dh = [r for r in K if route(r) in ("dfa", "hybrid")]
    cc = [(r, cls(r)) for r in dh]
    S["dfa_hat"] = {
        "dfa_or_hybrid": len(dh),
        "seeded": sum(r["seeded"] == "1" for r in dh),
        "seeded_with_skip": sum(r["seeded"] == "1" and c["E_pop"] > 0 for r, c in cc),
        "narrow": sum(c["DFA_NARROW"] for r, c in cc),
        "narrow_dfa": sum(c["DFA_NARROW"] and route(r) == "dfa" for r, c in cc),
        "narrow_hybrid": sum(c["DFA_NARROW"] and route(r) == "hybrid" for r, c in cc),
        "narrow_T_singleton": sum(c["DFA_NARROW"] and c["T_pop"] == 1 for r, c in cc),
        "fs_cont_bytes_nonzero": sum(r["fs_cont"] not in ("0", "") for r in K),
    }
    summary[kind] = S
    for r in K:
        c = cls(r)
        detail.append({"kind": kind, "set": r["set"], "name": r["name"], "auto": route(r),
                       "forced": route(r, True), **{k: v for k, v in c.items()}})

json.dump({"summary": summary, "detail": [d for d in detail if d["kind"] == "bench"]},
          open(OUT, "w"), indent=1, sort_keys=True)
print(json.dumps(summary, indent=1, sort_keys=True))

# the gap report's START-SET cells, one line each
CELLS = [("capability", "wild-secrets-aws-access-key-id"), ("capability", "wild-codegrammar-json-constant"),
         ("capability", "wild-secrets-github-pat"), ("loglines", "stack-frame"), ("loglines", "bignum"),
         ("syntax", "asr-wb"), ("syntax", "asr-nwb"), ("utf8", "asr-b-ascii"),
         ("capability", "quoted-delim-match"), ("capability", "balanced-parens-rec"),
         ("syntax", "bak-k-named"), ("capability", "wild-waf-crs-942140-dbnames"),
         ("loglines", "hex32-id"), ("litrun", "wild-secrets-aws-access-key-id")]
print("\nSTART-SET cells:")
idx = {(d["set"], d["name"]): d for d in detail if d["kind"] == "bench"}
for k in CELLS:
    d = idx.get(k)
    if not d: print(k, "MISSING"); continue
    f = lambda x: "-" if x is None else "%.4f" % x
    print("%-11s %-34s auto=%-7s forced=%-7s FS=%d |S|=%3d |E|=%3d |T|=%3d narrow=%d RUN=%d d_S=%s d_E=%s d_T=%s" % (
        k[0], k[1], d["auto"], d["forced"], d["FS"], d["fs_pop"], d["E_pop"], d["T_pop"], d["DFA_NARROW"],
        d["RUN"], f(d["d_S"]), f(d["d_E"]), f(d["d_T"])))
