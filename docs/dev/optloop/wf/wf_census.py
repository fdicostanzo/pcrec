#!/usr/bin/env python3
"""[WORD-FOLD] THE D77 CENSUS DRIVER — populations in, run-length tables out.

Builds the same two populations `docs/dev/optloop/c2/reqpos_census.py`
built (corpus via `pcrec --list-source`, bench via `bench/*/patterns/*.rx`,
read-only against pcrec-bench), runs `wf_run_probe` over each, and writes
the raw joined rows as JSON for `wf_report.py` to render tables from.

Environment
  PCREC   a pcrec build for `--list-source` (any; the dump is stable)
  PROBE   the built `wf_run_probe`
  BENCH   pcrec-bench root (read-only)
  CORPUS  pcrec root (its tests/ tree is walked)
  OUT     output directory
"""
import os, sys, subprocess, glob, json

E = os.environ
OUT = E.get("OUT", ".")


def dec_field(b: bytes) -> bytes:
    """`pcrec_sb_field`'s escape vocabulary, inverted (src/core/sb.c)."""
    out = bytearray(); i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5c and i + 1 < len(b):
            n = b[i + 1]
            if n == 0x5c: out.append(0x5c); i += 2; continue
            if n == 0x74: out.append(9);    i += 2; continue
            if n == 0x6e: out.append(10);   i += 2; continue
            if n == 0x72: out.append(13);   i += 2; continue
            if n == 0x78 and i + 3 < len(b):
                try: out.append(int(b[i + 2:i + 4], 16)); i += 4; continue
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


def main():
    result = {}
    for popname, rows in (("bench", bench_pop()), ("corpus", corpus_pop())):
        recs = run_probe(rows, "byte")
        by = {r["id"]: r for r in recs}
        for i, p in rows:
            if i in by:
                by[i]["pattern_hex"] = p.hex()
                by[i]["is_caseless"] = int(b"(?i)" in p or b"(?i:" in p)
        result[popname] = list(by.values())
        print("%s: %d patterns, %d probed" % (popname, len(rows), len(recs)),
              file=sys.stderr)

    # utf8 arm over the corpus, matching reqpos_census's third population.
    crows = corpus_pop()
    recs = run_probe(crows, "utf8")
    by = {r["id"]: r for r in recs}
    for i, p in crows:
        if i in by:
            by[i]["pattern_hex"] = p.hex()
            by[i]["is_caseless"] = int(b"(?i)" in p or b"(?i:" in p)
    result["corpus_utf8"] = list(by.values())
    print("corpus_utf8: %d patterns, %d probed" % (len(crows), len(recs)),
          file=sys.stderr)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "wf_census.json"), "w") as f:
        json.dump(result, f)
    print("wrote %s/wf_census.json" % OUT, file=sys.stderr)


if __name__ == "__main__":
    main()
