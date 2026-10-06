#!/usr/bin/env python3
"""[OPT-REVEND] census driver: end-anchored population, bounded vs unbounded,
and what each pattern gets today.  COMPILE-SIDE ONLY: no subject is matched,
no clock is read.

Populations
  bench   every bench/<set>/patterns/*.rx in pcrec-bench (read-only), compiled
          the way the bench's `pcrec-auto` testee does (--features all; -e utf8
          on the `utf8` set).
  corpus  every `pattern` block of every shipped .rxt (pcrec --list-source),
          compiled with the BLOCK'S OWN options: its `encoding` column (utf8 |
          byte), `flags` (i -> (?i) prefix; u -> counted, ucp not modelled),
          `features` replaced by `all` (a superset -- the census asks about the
          pattern, not whether a gated module is on).

Two instruments, cross-checked:
  PROBE   revend_probe.c: a copy of src/facts/endwin.c's ew_walk (multiline `$`
          kept as its own level) + max/min width + leading-unbounded flag.
  FACTS   `pcrec --emit-facts`: the SHIPPED end_window fact (value + why) and
          the artifact's decision stamps.  A row the probe calls end-anchored
          (view 1/2) must not read decline:not-end-anchored in FACTS and vice
          versa; disagreements are counted and listed, not hidden.

    PCREC=build/pcrec PROBE=./revend_probe BENCH=/path/pcrec-bench \
    CORPUS=/path/pcrec OUT=dir python3 census.py
"""
import glob, json, os, subprocess, sys, collections, concurrent.futures as cf

E = os.environ
PCREC, PROBE, BENCH, CORPUS, OUT = (E["PCREC"], E["PROBE"], E["BENCH"],
                                    E["CORPUS"], E["OUT"])
NICE = ["nice", "-n", "10"] if E.get("NICE", "1") == "1" else []
os.makedirs(OUT, exist_ok=True)


def dec_field(b):
    """pcrec_sb_field's escape vocabulary, inverted (src/core/sb.c)."""
    out = bytearray(); i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5c and i + 1 < len(b):
            n = b[i + 1]
            m = {0x5c: 0x5c, 0x74: 9, 0x6e: 10, 0x72: 13}
            if n in m: out.append(m[n]); i += 2; continue
            if n == 0x78 and i + 3 < len(b):
                try: out.append(int(b[i + 2:i + 4], 16)); i += 4; continue
                except ValueError: pass
        out.append(c); i += 1
    return bytes(out)


def bench_pop():
    rows = []
    for p in sorted(glob.glob(os.path.join(BENCH, "bench", "*", "patterns", "*.rx"))):
        sb = p.split(os.sep)[-3]
        b = open(p, "rb").read().rstrip(b"\n")
        if b and b"\x00" not in b:
            rows.append(dict(pop="bench", id=f"{sb}/{os.path.basename(p)[:-3]}",
                             suite=sb, enc="utf8" if sb == "utf8" else "byte",
                             icase=False, ucp=False, pat=b))
    return rows


def corpus_pop():
    rows = []
    files = []
    for root, _d, fs in os.walk(os.path.join(CORPUS, "tests")):
        files += [os.path.join(root, f) for f in fs if f.endswith(".rxt")]
    for f in sorted(files):
        r = subprocess.run([PCREC, "--list-source", f], capture_output=True, timeout=120)
        if r.returncode != 0:
            continue
        rel = os.path.relpath(f, CORPUS)
        for ln in r.stdout.split(b"\n"):
            if ln.startswith(b"#section"):
                break
            if not ln or ln.startswith(b"#"):
                continue
            fl = ln.split(b"\t")
            if len(fl) < 9 or fl[0] not in (b"pattern", b"pattern-esc"):
                continue
            pat = dec_field(fl[4])
            if not pat or b"\x00" in pat:
                continue
            flags = fl[5].decode()
            enc = fl[8].decode() or "byte"
            rows.append(dict(pop="corpus", id=f"{rel}:{fl[1].decode()}",
                             suite=rel.split(os.sep)[1] if os.sep in rel else rel,
                             enc="utf8" if enc == "utf8" else "byte",
                             icase="i" in flags, ucp="u" in flags, pat=pat))
    return rows


def run_probe(rows):
    inp = "".join("%d\t%s\t%s\n" % (i, r["enc"],
                  (b"(?i)" + r["pat"] if r["icase"] else r["pat"]).hex())
                  for i, r in enumerate(rows))
    res = subprocess.run(NICE + [PROBE], input=inp.encode(), capture_output=True,
                         timeout=3600)
    out = {}
    for ln in res.stdout.decode().split("\n")[1:]:
        f = ln.split("\t")
        if len(f) < 8:
            continue
        out[int(f[0])] = dict(status=f[1], view=int(f[2]), cwmax=int(f[3]),
                              minw=int(f[4]), lead_unb=int(f[5]),
                              gstart=int(f[6]), look_tail=int(f[7]))
    return out


def facts(r):
    cmd = NICE + [PCREC, "--emit-facts=" + r["enc"], "--features", "all"]
    if r["icase"]:
        cmd.append("-i")
    if r["enc"] == "utf8":
        cmd += ["-e", "utf8"]
    cmd += ["--pattern", r["pat"]]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return {"refused": "timeout"}
    if p.returncode != 0:
        return {"refused": p.stderr.decode("utf8", "replace").split("\n")[0][:120]}
    d = {}
    sect = None
    for ln in p.stdout.decode("utf8", "replace").split("\n"):
        if ln.startswith("#section"):
            sect = ln.split()[1]; continue
        if ln.startswith("#") or not ln:
            continue
        f = ln.split("\t")
        if sect == "facts" and len(f) >= 8 and f[1] == "end_window":
            d["ew_status"], d["ew_value"], d["ew_why"] = f[4], f[6], f[7]
        elif sect == "facts" and len(f) >= 7 and f[1] == "nullable":
            d["nullable"] = f[6]
        elif sect == "facts" and len(f) >= 7 and f[1] == "start_anchor":
            d["start_anchor"] = f[6]
        elif sect == "decisions" and len(f) >= 3:
            d[f[1].replace("RX_", "")] = f[2].strip('"')
    return d


def main():
    rows = bench_pop() + corpus_pop()
    pr = run_probe(rows)
    for i, r in enumerate(rows):
        r.update(pr.get(i, dict(status="noprobe", view=0, cwmax=-1, minw=0,
                                lead_unb=0, gstart=0, look_tail=0)))
    # FACTS_ALL=1 also asks the shipped fact about the probe's view-0 rows:
    # the converse of the cross-check (probe says "not anchored", fact says
    # anchored) -- a drifted ew_walk copy would hide there.
    sel = (lambda r: r["status"] == "ok") if E.get("FACTS_ALL") == "1" else \
          (lambda r: r["status"] == "ok" and r["view"] in (1, 2, 3))
    anch = [r for r in rows if sel(r)]
    with cf.ThreadPoolExecutor(max_workers=int(E.get("JOBS", "2"))) as ex:
        for r, d in zip(anch, ex.map(facts, anch)):
            r["facts"] = d
    with open(os.path.join(OUT, "census_rows.tsv"), "w") as fh:
        keys = ["pop", "id", "suite", "enc", "icase", "status", "view", "cwmax", "minw",
                "lead_unb", "gstart", "look_tail", "ew_status", "ew_why", "ew_value",
                "nullable", "start_anchor", "ENGINE", "DFA_SCAN", "DFA_PREFILTER", "DFA_START",
                "DFA_MATCH", "DFA_SCAN_EDGE", "REQ_BYTE", "REQ_RUN", "REQ_WHY",
                "VM_PREFILTER", "pattern_hex"]
        fh.write("\t".join(keys) + "\n")
        for r in rows:
            f = r.get("facts", {})
            vals = dict(r); vals.update(f)
            vals["pattern_hex"] = r["pat"].hex()
            fh.write("\t".join(str(vals.get(k, "")) for k in keys) + "\n")
    print("rows", len(rows), "anchored", len(anch))


if __name__ == "__main__":
    main()
