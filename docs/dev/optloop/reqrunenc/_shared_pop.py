#!/usr/bin/env python3
"""[OPT-REQPOS] THE CENSUS DRIVER — populations in, tier counts out.

Builds the two populations the plan row names, runs `reqpos_probe` over
each, cross-checks the probe's `req_byte` column against batch 1's landed
`RX_REQ_BYTE` stamp, and joins the bench rows against the throughput
subjects' byte census so a tier can be scored where it actually PAYS (the
byte PRESENT, not absent).

Populations
  bench   every `bench/*/patterns/*.rx` export in pcrec-bench (read-only).
  corpus  every `pattern`/`pattern-esc` line of every shipped `.rxt`, via
          `pcrec --list-source`, whose `pattern` column is FIELD-ESCAPED
          in `pcrec_sb_field`'s vocabulary and is DECODED here rather than
          handed back raw (`cycle1_analysis.md`'s own recorded trap: nine
          plausible refusals on patterns the bench compiles at the pin).

Environment
  PCREC      a pcrec build for `--list-source` (any; the dump is stable)
  PCREC_B1   batch 1's build, for the RX_REQ_BYTE cross-check (optional)
  PROBE      the built `reqpos_probe`
  BENCH      pcrec-bench root
  CORPUS     pcrec root (its tests/ tree is walked)
  SUBJ       directory of the regenerated t-*.bin throughput subjects
  OUT        output directory
"""
import os, sys, subprocess, glob, json, collections

E = os.environ
OUT = E.get("OUT", ".")

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

def bench_pop():
    rows = []
    for p in sorted(glob.glob(os.path.join(E["BENCH"], "bench", "*", "patterns", "*.rx"))):
        setname = p.split(os.sep)[-3]
        name = os.path.basename(p)[:-3]
        b = open(p, "rb").read()
        while b.endswith(b"\n"): b = b[:-1]
        if b: rows.append(("%s/%s" % (setname, name), b))
    return rows

def corpus_pop():
    rows, files = [], []
    for root, _d, fs in os.walk(os.path.join(E["CORPUS"], "tests")):
        for f in fs:
            if f.endswith(".rxt"): files.append(os.path.join(root, f))
    for f in sorted(files):
        r = subprocess.run([E["PCREC"], "--list-source", f],
                           capture_output=True, timeout=120)
        if r.returncode != 0: continue
        rel = os.path.relpath(f, E["CORPUS"])
        for ln in r.stdout.split(b"\n"):
            if not ln or ln.startswith(b"#"): continue
            fl = ln.split(b"\t")
            if len(fl) < 5: continue
            if fl[0] not in (b"pattern", b"pattern-esc"): continue
            pat = dec_field(fl[4])
            if not pat or b"\x00" in pat: continue
            rows.append(("%s:%s" % (rel, fl[1].decode()), pat))
    return rows

def run_probe(rows, enc):
    inp = "".join("%s\t%s\n" % (i, p.hex()) for i, p in rows)
    cmd = [E["PROBE"]] + (["-e", "utf8"] if enc == "utf8" else [])
    r = subprocess.run(cmd, input=inp.encode(), capture_output=True, timeout=1800)
    if r.returncode != 0:
        sys.exit("probe failed: %s" % r.stderr.decode()[:400])
    out, hdr = [], None
    for ln in r.stdout.decode().rstrip("\n").split("\n"):
        f = ln.split("\t")
        if hdr is None: hdr = f; continue
        out.append(dict(zip(hdr, f)))
    return out

def stamp_req_byte(pat, tmp):
    """batch 1's own RX_REQ_BYTE, read off an emitted artifact."""
    r = subprocess.run([E["PCREC_B1"], "--features", "all", "--no-captures",
                        "-p", "rx", "-o", tmp, "--pattern", pat.decode("latin-1")],
                       capture_output=True, timeout=120)
    if r.returncode != 0: return None
    for ln in open(tmp, encoding="latin-1"):
        if ln.startswith("#define RX_REQ_BYTE"):
            v = ln.split('"')[1]
            return -1 if v == "none" else int(v)
    return None

def main():
    subj = {}
    if E.get("SUBJ"):
        b = open(os.path.join(E["SUBJ"], "t-1m.bin"), "rb").read()
        subj = collections.Counter(b)

    result = {}
    for popname, rows in (("bench", bench_pop()), ("corpus", corpus_pop())):
        recs = run_probe(rows, "byte")
        by = {r["id"]: r for r in recs}
        for i, p in rows:
            if i in by: by[i]["pattern_hex"] = p.hex()
        result[popname] = list(by.values())
        print("%s: %d patterns, %d probed" % (popname, len(rows), len(recs)),
              file=sys.stderr)

    # utf8 arm over the corpus (the survey's third population, reused here)
    result["corpus_utf8"] = run_probe(corpus_pop(), "utf8")

    # ---- the cross-check: probe req_byte MUST equal batch 1's stamp -------
    xc = {"checked": 0, "agree": 0, "disagree": [], "skipped": 0}
    if E.get("PCREC_B1"):
        tmp = os.path.join(OUT, "_xc.c")
        for r in result["bench"]:
            if not r["id"].startswith("capability/"): continue
            s = stamp_req_byte(bytes.fromhex(r["pattern_hex"]), tmp)
            if s is None: xc["skipped"] += 1; continue
            xc["checked"] += 1
            if s == int(r["req_byte"]): xc["agree"] += 1
            else: xc["disagree"].append([r["id"], s, int(r["req_byte"])])
        for ext in ("", ".h"):
            try: os.remove(tmp.replace(".c", ".c" + ext) if ext else tmp)
            except OSError: pass
        try: os.remove(os.path.join(OUT, "_xc.h"))
        except OSError: pass
    result["_crosscheck"] = xc

    # ---- subject presence for the bench capability rows ------------------
    for r in result["bench"]:
        rb = int(r["req_byte"])
        r["req_present_t1m"] = (subj.get(rb, 0) > 0) if (subj and rb >= 0) else None
        r["req_count_t1m"] = subj.get(rb, 0) if (subj and rb >= 0) else None

    json.dump(result, open(os.path.join(OUT, "reqpos_census.json"), "w"), indent=1)
    # The COMMITTED form is TSV (the tree's own table convention); the JSON
    # is the scratch intermediate this driver hands to the renderers.
    print("crosscheck: %d checked, %d agree, %d disagree, %d skipped"
          % (xc["checked"], xc["agree"], len(xc["disagree"]), xc["skipped"]),
          file=sys.stderr)

if __name__ == "__main__":
    main()
