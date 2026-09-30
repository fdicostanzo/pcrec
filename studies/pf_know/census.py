#!/usr/bin/env python3
"""[PF-KNOW] (D140) — THE STATIC CENSUS.

For every pattern of three populations, compile it with the tree's own
`pcrec` (default engine, `--features all`) and read, off the EMITTED C:
the engine / prefilter stamps, every `static const` table with its size,
and — for question 2 — whether the DFA prefilter's byte-class partition
REFINES each VM class bitmap (if it does, the VM could index the DFA's
256-byte map and test a bitmap over DFA classes instead of over bytes).
Then run `segprobe` on the same pattern and join the two by id.

Populations:
  corpus   every `pattern`/`pattern-esc` line of every shipped `.rxt`
           under tests/ (the reqpos/onepass censuses' own enumeration).
  bench    every `bench/*/patterns/*.rx` of the READ-ONLY sibling
           pcrec-bench checkout (BENCH env; skipped if absent).

Environment: PCREC PROBE CORPUS OUT [BENCH] [JOBS]
Writes OUT/census.tsv and OUT/summary.json.  No clock is read anywhere.
"""
import os, sys, re, glob, json, subprocess, tempfile, collections
from concurrent.futures import ThreadPoolExecutor

E = os.environ
PCREC, PROBE, CORPUS, OUT = E["PCREC"], E["PROBE"], E["CORPUS"], E["OUT"]
BENCH = E.get("BENCH")
JOBS = int(E.get("JOBS", "4"))

def dec_field(b: bytes) -> bytes:
    """`pcrec_sb_field`'s escape vocabulary, inverted (src/core/sb.c)."""
    out = bytearray(); i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5c and i + 1 < len(b):
            n = b[i+1]
            if n == 0x5c: out.append(0x5c); i += 2; continue
            if n == 0x74: out.append(9);    i += 2; continue
            if n == 0x6e: out.append(10);   i += 2; continue
            if n == 0x72: out.append(13);   i += 2; continue
            if n == 0x78 and i + 3 < len(b):
                try: out.append(int(b[i+2:i+4], 16)); i += 4; continue
                except ValueError: pass
        out.append(c); i += 1
    return bytes(out)

def corpus_pop():
    rows, files = [], []
    for root, _d, fs in os.walk(os.path.join(CORPUS, "tests")):
        for f in fs:
            if f.endswith(".rxt"): files.append(os.path.join(root, f))
    for f in sorted(files):
        r = subprocess.run([PCREC, "--list-source", f], capture_output=True, timeout=120)
        if r.returncode != 0: continue
        rel = os.path.relpath(f, CORPUS)
        for ln in r.stdout.split(b"\n"):
            if not ln or ln.startswith(b"#"): continue
            fl = ln.split(b"\t")
            if len(fl) < 5 or fl[0] not in (b"pattern", b"pattern-esc"): continue
            pat = dec_field(fl[4])
            if not pat or b"\x00" in pat: continue
            rows.append(("corpus", "%s:%s" % (rel, fl[1].decode()), pat))
    return rows

def bench_pop():
    rows = []
    if not BENCH: return rows
    for p in sorted(glob.glob(os.path.join(BENCH, "bench", "*", "patterns", "*.rx"))):
        setname = p.split(os.sep)[-3]
        name = os.path.basename(p)[:-3]
        b = open(p, "rb").read()
        while b.endswith(b"\n"): b = b[:-1]
        if b and b"\x00" not in b: rows.append(("bench", "%s/%s" % (setname, name), b))
    return rows

STAMPS = ["ENGINE", "ENGINE_WHY", "VM_PREFILTER", "VM_PREFILTER_LANG", "VM_PREFILTER_LANG_WHY",
          "VM_FRAMELESS", "NCAPS", "VM_START", "DFA_PREFILTER", "DFA_SCAN", "DFA_SCAN_EDGE",
          "DFA_TABLE", "VM_CLS_KIT", "VM_CLS_ATOMS", "VM_CLS_FOLDS", "VM_LIT_RUNS", "VM_RESEED",
          "REQ_WHY", "VM_PRUNE_CEILING", "VM_ALT_ISLANDS", "VM_ENTRY_SHAPE", "VM_PROGRAM_BYTES",
          "VM_RUNGS", "VM_STRATS"]
TABLE_RE = re.compile(rb"static const (unsigned char|unsigned short|unsigned int|unsigned long|"
                      rb"uint8_t|uint16_t|uint32_t|signed char|short|int|char) "
                      rb"(rx_\w+)\[(\d+)\](?:\[(\d+)\])? = \{([^}]*)\}", re.S)
ELEM_BYTES = {b"unsigned char": 1, b"uint8_t": 1, b"signed char": 1, b"char": 1,
              b"unsigned short": 2, b"uint16_t": 2, b"short": 2,
              b"unsigned int": 4, b"uint32_t": 4, b"int": 4, b"unsigned long": 8}

def parse_ints(body):
    return [int(x) for x in re.findall(rb"-?\d+", body)]

def bitmap_set(vals):
    s = set()
    for b in range(256):
        if (vals[b >> 3] >> (b & 7)) & 1: s.add(b)
    return s

def refines(bclass, cset):
    """Does the byte->class map `bclass` refine the byte set `cset`?  i.e. is
    every class wholly inside or wholly outside the set."""
    inside = {}
    for b in range(256):
        c = bclass[b]; m = b in cset
        if c in inside and inside[c] != m: return False
        inside[c] = m
    return True

def compile_one(rec):
    kind, ident, pat = rec
    fd, tmp = tempfile.mkstemp(suffix=".c", dir=OUT); os.close(fd)
    args = [PCREC, "--features", "all", "-p", "rx", "-o", tmp, "--pattern", pat]
    row = {"pop": kind, "id": ident, "pattern": pat.decode("latin-1")}
    try:
        r = subprocess.run(args, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        row["status"] = "timeout"; return row
    if r.returncode != 0:
        row["status"] = "refused"
        row["diag"] = r.stderr.decode("latin-1").strip().split("\n")[0][:120]
        for f in (tmp, tmp[:-2] + ".h"):
            try: os.unlink(f)
            except OSError: pass
        return row
    src = open(tmp, "rb").read()
    for f in (tmp, tmp[:-2] + ".h"):
        try: os.unlink(f)
        except OSError: pass
    row["status"] = "ok"
    row["emitted_bytes"] = len(src)
    st = dict(re.findall(rb"^#define RX_(\w+) (.*)$", src, re.M))
    for k in STAMPS:
        v = st.get(k.encode(), b"-").decode("latin-1").strip()
        row[k] = v.strip('"')
    # tables
    tabs = []
    for m in TABLE_RE.finditer(src):
        ty, name, n1, n2, body = m.groups()
        n = int(n1) * (int(n2) if n2 else 1)
        tabs.append((name.decode(), ELEM_BYTES.get(ty, 1) * n, body, ty))
    fam = collections.Counter(); famn = collections.Counter()
    dfa_bclass = {}; vm_bitmaps = []
    for name, nbytes, body, ty in tabs:
        if name.endswith("_byte_class"):
            key = "dfa_byte_class"; dfa_bclass[name] = parse_ints(body)
        elif name.endswith("_next_state"): key = "dfa_next_state"
        elif name.endswith("_is_accepting"): key = "dfa_accept"
        elif name.endswith("can_begin_match") or "_ofs" in name or "_cand" in name: key = "dfa_prefilter"
        elif re.match(r"rx_class_bitmap\d+$", name): key = "vm_bitmap"; vm_bitmaps.append(parse_ints(body))
        elif name == "rx_class_atoms": key = "vm_atoms"
        elif "atom" in name: key = "vm_atomset"
        elif "wcls" in name or "kit" in name: key = "vm_wcls"
        elif "scan" in name or "edge" in name: key = "dfa_scan_edge"
        else: key = "other:" + name
        fam[key] += nbytes; famn[key] += 1
    row["tables"] = ";".join("%s=%d/%d" % (k, famn[k], fam[k]) for k in sorted(fam))
    row["dfa_nmachines"] = len(dfa_bclass)
    row["vm_nbitmaps"] = len(vm_bitmaps)
    fwd = dfa_bclass.get("rx_forward_byte_class") or dfa_bclass.get("rx_prefilter_forward_byte_class")
    if fwd is None and dfa_bclass:
        fwd = next(iter(dfa_bclass.values()))
    if fwd is not None:
        ncls = max(fwd) + 1
        row["dfa_nclasses"] = ncls
        if vm_bitmaps:
            ok = [refines(fwd, bitmap_set(v)) for v in vm_bitmaps]
            row["share_refined"] = sum(ok); row["share_total"] = len(ok)
            row["share_saved_bytes"] = sum(32 - (ncls + 7) // 8 for o in ok if o)
    return row

def run_probe(rows):
    inp = "".join("%s\t%s\n" % (i, p.hex()) for _k, i, p in rows)
    r = subprocess.run([PROBE], input=inp.encode(), capture_output=True, timeout=1800)
    if r.returncode != 0: sys.exit("probe failed: " + r.stderr.decode()[:400])
    out, hdr = {}, None
    for ln in r.stdout.decode("latin-1").rstrip("\n").split("\n"):
        f = ln.split("\t")
        if hdr is None: hdr = f; continue
        d = dict(zip(hdr, f)); out[d["id"]] = d
    return out, hdr

def main():
    os.makedirs(OUT, exist_ok=True)
    rows = corpus_pop() + bench_pop()
    # de-duplicate by (pop, pattern) keeping the first id
    seen, uniq = set(), []
    for r in rows:
        k = (r[0], r[2])
        if k in seen: continue
        seen.add(k); uniq.append(r)
    rows = uniq
    print("population: %d rows (%s)" % (len(rows), dict(collections.Counter(r[0] for r in rows))), file=sys.stderr)
    probe, phdr = run_probe(rows)
    with ThreadPoolExecutor(JOBS) as ex:
        comp = list(ex.map(compile_one, rows))
    cols = ["pop", "id", "status", "emitted_bytes"] + STAMPS + \
           ["tables", "dfa_nmachines", "dfa_nclasses", "vm_nbitmaps", "share_refined", "share_total", "share_saved_bytes"] + \
           [h for h in phdr if h not in ("id", "status")] + ["pattern"]
    with open(os.path.join(OUT, "census.tsv"), "w") as f:
        f.write("\t".join(cols) + "\n")
        for c in comp:
            p = probe.get(c["id"], {})
            d = dict(p); d.update(c)
            f.write("\t".join(str(d.get(k, "-")).replace("\t", " ").replace("\n", "\\n") for k in cols) + "\n")
    # summary
    ok = [dict(probe.get(c["id"], {}), **c) for c in comp if c["status"] == "ok"]
    def cnt(pred): return sum(1 for r in ok if pred(r))
    S = {}
    S["compiled"] = len(ok); S["refused"] = len(comp) - len(ok)
    S["by_pop"] = dict(collections.Counter(r["pop"] for r in ok))
    S["engine"] = dict(collections.Counter((r["pop"], r["ENGINE"]) and "%s/%s" % (r["pop"], r["ENGINE"]) for r in ok))
    S["vm_prefilter"] = dict(collections.Counter("%s/%s/%s" % (r["pop"], r["VM_PREFILTER"], r["VM_PREFILTER_LANG"]) for r in ok if r["ENGINE"] == "vm"))
    hyx = [r for r in ok if r["VM_PREFILTER"] == "hybrid" and r["VM_PREFILTER_LANG"] == "exact"]
    hyo = [r for r in ok if r["VM_PREFILTER"] == "hybrid" and r["VM_PREFILTER_LANG"] != "exact"]
    vmn = [r for r in ok if r["ENGINE"] == "vm" and r["VM_PREFILTER"] != "hybrid"]
    def seg(rows, key):
        c = collections.Counter()
        for r in rows:
            v = int(r.get(key, 0) or 0)
            c["0" if v == 0 else "1-2" if v <= 2 else "3-7" if v <= 7 else "8+"] += 1
        return dict(c)
    for name, rs in (("hybrid_exact", hyx), ("hybrid_over", hyo), ("vm_noprefilter", vmn)):
        S[name] = {
            "n": len(rs),
            "by_pop": dict(collections.Counter(r["pop"] for r in rs)),
            "lead_tests": seg(rs, "lead_tests"),
            "trail_tests": seg(rs, "trail_tests"),
            "lead_or_trail_nonzero": sum(1 for r in rs if int(r.get("lead_tests", 0) or 0) + int(r.get("trail_tests", 0) or 0) + int(r.get("lead_zw", 0) or 0) > 0),
            "lead_sets_nonzero": sum(1 for r in rs if int(r.get("lead_sets", 0) or 0) > 0),
            "det_all": sum(1 for r in rs if r.get("det_all") == "1"),
            "choice_free": sum(1 for r in rs if r.get("choice_free") == "1"),
            "frameless": sum(1 for r in rs if r.get("VM_FRAMELESS") == "1"),
            "maxw_bounded": sum(1 for r in rs if r.get("maxw", "0").isdigit() and int(r["maxw"]) < 1099511627776),
            "lead_tests_sum": sum(int(r.get("lead_tests", 0) or 0) for r in rs),
            "minw_sum": sum(int(r.get("minw", 0) or 0) for r in rs),
        }
    both = [r for r in ok if r.get("dfa_nmachines", 0) and (r.get("vm_nbitmaps", 0) or "vm_atoms" in r.get("tables", ""))]
    S["q2"] = {
        "artifacts_with_dfa_and_vm_tables": len(both),
        "hybrid_artifacts": cnt(lambda r: r["VM_PREFILTER"] == "hybrid"),
        "hybrid_with_vm_bitmaps": cnt(lambda r: r["VM_PREFILTER"] == "hybrid" and r.get("vm_nbitmaps", 0)),
        "hybrid_with_atoms": cnt(lambda r: r["VM_PREFILTER"] == "hybrid" and "vm_atoms" in r.get("tables", "")),
        "hybrid_with_kit": cnt(lambda r: r["VM_PREFILTER"] == "hybrid" and r.get("VM_CLS_KIT", "0") not in ("0", "-")),
        "bitmaps_total": sum(r.get("share_total", 0) for r in both),
        "bitmaps_refined_by_dfa_fwd": sum(r.get("share_refined", 0) for r in both),
        "artifacts_all_refined": sum(1 for r in both if r.get("share_total") and r.get("share_refined") == r.get("share_total")),
        "bytes_saved_if_shared": sum(r.get("share_saved_bytes", 0) for r in both),
        "vm_bitmap_bytes_in_hybrids": sum(32 * r.get("vm_nbitmaps", 0) for r in both),
        "dfa_nclasses_hist": dict(collections.Counter(("<=8" if r["dfa_nclasses"] <= 8 else "<=16" if r["dfa_nclasses"] <= 16 else "<=32" if r["dfa_nclasses"] <= 32 else ">32") for r in both if "dfa_nclasses" in r)),
    }
    json.dump(S, open(os.path.join(OUT, "summary.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps(S, indent=1, sort_keys=True))

if __name__ == "__main__":
    main()
