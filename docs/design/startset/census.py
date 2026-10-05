#!/usr/bin/env python3
"""[START-SET] THE D77 CENSUS (lane startset, 2026-10-05; docs/design/startset.md §2).

Compile-side only: nothing is matched or timed.  pcrec-bench is read, never
written.

Per pattern it records, at the bench's own `pcrec-auto` flags (`--features
all`, `-e utf8` on bench/utf8) AND at `pcrec-vm`'s (`--engine=vm` added):

  * the route stamps read off `--emit-facts`'s decisions section
    (RX_ENGINE, RX_VM_PREFILTER, RX_DFA_PREFILTER, RX_REQ_WHY,
    RX_REQ_HANDOFF) and two record facts (`nullable`, `req_run_maxoff`,
    plus `req_run`/`req_byte` presence);
  * the AST start set from `fs_probe` (this directory): popcount, nullable,
    whether it holds a UTF-8 continuation byte;
  * on the AUTO compile's emitted .c only: the set
    `<p>_can_begin_match` (hex, 32 bytes, bit b = byte b) and whether the forward machine is SEEDED
    (`_forward_seed_state[`), i.e. the DFA consumer's reach
    (firstset_design.md §4.6.3's has_seed, read the same way).

Populations:
  bench    every bench/<set>/patterns/*.rx export (pcrec-bench, read-only)
  corpus   every `pattern`/`pattern-esc` line of every shipped .rxt, via
           `pcrec --list-source` (dec_field: c2/skiproute_census.py's own
           decoder), compiled at byte encoding.

Env: PCREC, PROBE (fs_probe binary), BENCH (pcrec-bench root), CORPUS (pcrec
root), OUT, JOBS (default 8).  Writes census.tsv + census_summary.json.
"""
import collections, concurrent.futures as cf, json, os, re, subprocess, sys, tempfile

E = os.environ
PCREC, PROBE, OUT = E["PCREC"], E["PROBE"], E.get("OUT", ".")
BENCH = E.get("BENCH", "/Users/fdicostanzo/pcrec-bench")
CORPUS = E["CORPUS"]
JOBS = int(E.get("JOBS", "8"))
SETS = {"capability": [], "syntax": [], "utf8": ["-e", "utf8"], "loglines": [],
        "bounded": [], "email": [], "altwide": [], "litrun": []}

def dec_field(b):
    out = bytearray(); i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5c and i + 1 < len(b):
            n = b[i + 1]
            if n == 0x5c: out.append(0x5c); i += 2; continue
            if n == 0x74: out.append(9); i += 2; continue
            if n == 0x6e: out.append(10); i += 2; continue
            if n == 0x72: out.append(13); i += 2; continue
            if n == 0x78 and i + 3 < len(b):
                try: out.append(int(b[i + 2:i + 4], 16)); i += 4; continue
                except ValueError: pass
        out.append(c); i += 1
    return bytes(out)

def bench_pop():
    rows = []
    for sb, extra in SETS.items():
        d = os.path.join(BENCH, "bench", sb, "patterns")
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".rx"):
                rows.append(("bench", sb, fn[:-3], open(os.path.join(d, fn), "rb").read(), extra))
    return rows

def corpus_pop():
    rows, files = [], []
    for root, _d, fs in os.walk(os.path.join(CORPUS, "tests")):
        files += [os.path.join(root, f) for f in fs if f.endswith(".rxt")]
    seen = set()
    for f in sorted(files):
        r = subprocess.run([PCREC, "--list-source", f], capture_output=True, timeout=120)
        if r.returncode: continue
        rel = os.path.relpath(f, CORPUS)
        for ln in r.stdout.split(b"\n"):
            fl = ln.split(b"\t")
            if len(fl) < 5 or fl[0] not in (b"pattern", b"pattern-esc"): continue
            pat = dec_field(fl[4])
            if not pat or b"\x00" in pat or pat in seen: continue
            seen.add(pat)               # DISTINCT pattern texts (K35: say so)
            rows.append(("corpus", "corpus", "%s:%s" % (rel, fl[1].decode()), pat, []))
    return rows

FACT = re.compile(r"^(\S+)\t(\S+)\t\S+\t\S+\t(\S+)\t\S+\t(.*?)\t", re.M)
DEC = re.compile(r"^(\S+)\t(RX_[A-Z0-9_]+)\t(.*)$", re.M)

def facts(pat, extra):
    try:
        r = subprocess.run([PCREC, "--features", "all", *extra, "--emit-facts",
                            "--pattern", pat], capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode: return None
    t = r.stdout.decode("utf8", "replace")
    out = {}
    for line in t.split("\n"):
        f = line.split("\t")
        if len(f) >= 7 and f[0] in ("byte", "utf8") and not f[1].startswith("RX_") and not f[1].startswith("PCREC_"):
            out["f:" + f[1]] = f[6]; out["s:" + f[1]] = f[4]
        elif len(f) == 3 and f[1].startswith("RX_"):
            out[f[1]] = f[2].strip('"')
    return out

def cbm(pat, extra):
    with tempfile.TemporaryDirectory() as d:
        o = os.path.join(d, "a.c")
        try:
            r = subprocess.run([PCREC, "--features", "all", *extra, "-p", "rx", "-o", o,
                                "--pattern", pat], capture_output=True, timeout=300)
        except subprocess.TimeoutExpired:
            return None, None
        if r.returncode or not os.path.exists(o): return None, None
        src = open(o, errors="replace").read()
    m = re.search(r"rx_can_begin_match\[256\] = \{(.*?)\}", src, re.S)
    if not m: return "", int("_forward_seed_state[" in src)
    vals = re.findall(r"\d+", m.group(1))
    bits = bytearray(32)
    for i, v in enumerate(vals[:256]):
        if v != "0": bits[i >> 3] |= 1 << (i & 7)
    return bits.hex(), int("_forward_seed_state[" in src)

def one(row):
    kind, sb, name, pat, extra = row
    # BYTES, never `pat.decode("latin-1")`: subprocess re-encodes a str argv
    # as UTF-8, so every non-ASCII pattern would compile as a DIFFERENT
    # pattern (`[\xce\xb1]` -> `[\xc3\x8e\xc2\xb1]`). The first run of this
    # census did exactly that; the E-subset-of-S control (summarize.py)
    # caught it on 33 rows, all non-ASCII.
    p = pat
    rec = {"kind": kind, "set": sb, "name": name}
    a = facts(p, extra)
    if a is None:
        rec["status"] = "refused"; return rec, pat, extra
    v = facts(p, extra + ["--engine=vm"]) or {}
    rec["status"] = "ok"
    for k in ("RX_ENGINE", "RX_VM_PREFILTER", "RX_DFA_PREFILTER", "RX_REQ_WHY", "RX_REQ_HANDOFF",
              "RX_VM_FRAMELESS", "RX_VM_START"):
        rec["a_" + k] = a.get(k, "")
    for k in ("RX_ENGINE", "RX_VM_PREFILTER", "RX_REQ_WHY"):
        rec["v_" + k] = v.get(k, "")
    rec["nullable"] = a.get("f:nullable", "")
    rec["start_anchor"] = a.get("f:start_anchor", "")
    rec["req_run"] = a.get("f:req_run", "")
    rec["req_byte"] = a.get("f:req_byte", "")
    rec["maxoff"] = a.get("f:req_run_maxoff", "")
    rec["cbm_set"], rec["seeded"] = cbm(p, extra)
    return rec, pat, extra

def probe(rows):
    out = {}
    for enc in ("byte", "utf8"):
        sel = [(i, r) for i, r in enumerate(rows) if (("-e" in r[4]) == (enc == "utf8"))]
        inp = "".join("%d\t%s\n" % (i, r[3].hex()) for i, r in sel)
        cmd = [PROBE] + (["-e", "utf8"] if enc == "utf8" else [])
        res = subprocess.run(cmd, input=inp.encode(), capture_output=True, timeout=3600)
        for ln in res.stdout.decode().split("\n")[1:]:
            f = ln.split("\t")
            if len(f) == 6: out[int(f[0])] = f
    return out

def main():
    rows = bench_pop() + corpus_pop()
    sys.stderr.write("rows %d\n" % len(rows))
    fs = probe(rows)
    recs = [None] * len(rows)
    with cf.ThreadPoolExecutor(JOBS) as ex:
        futs = {ex.submit(one, r): i for i, r in enumerate(rows)}
        for n, fu in enumerate(cf.as_completed(futs)):
            i = futs[fu]; rec, _p, _e = fu.result()
            f = fs.get(i)
            rec["fs_status"] = f[1] if f else "none"
            rec["fs_nullable"] = f[2] if f else ""
            rec["fs_pop"] = f[3] if f else ""
            rec["fs_set"] = f[4] if f else ""
            rec["fs_cont"] = f[5] if f else ""
            rec["pat_hex"] = rows[i][3].hex()
            recs[i] = rec
            if n % 500 == 0: sys.stderr.write("  %d\n" % n)
    cols = ["kind", "set", "name", "status", "a_RX_ENGINE", "a_RX_VM_PREFILTER", "a_RX_DFA_PREFILTER",
            "a_RX_REQ_WHY", "a_RX_REQ_HANDOFF", "a_RX_VM_FRAMELESS", "a_RX_VM_START", "v_RX_ENGINE",
            "v_RX_VM_PREFILTER", "v_RX_REQ_WHY", "nullable", "start_anchor", "req_run", "req_byte",
            "maxoff", "cbm_set", "seeded", "fs_status", "fs_nullable", "fs_pop", "fs_cont", "fs_set",
            "pat_hex"]
    with open(os.path.join(OUT, "census.tsv"), "w") as f:
        f.write("# [START-SET] census, lane startset. Generated by census.py; see docs/design/startset.md §2.\n")
        f.write("\t".join(cols) + "\n")
        for r in recs:
            f.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")

main()
