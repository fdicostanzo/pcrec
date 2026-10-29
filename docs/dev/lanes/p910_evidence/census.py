#!/usr/bin/env python3
"""p910 census (COMPILE-ONLY: no subject matched, no clock read).

Populations: corpus = every pattern / pattern-esc row of tests/**/*.rxt (via
`pcrec --list-source`, deduplicated by text+encoding+icase); bench = every
pcrec-bench bench/*/patterns/*.rx plus capability's patterns.rxt rows.
Per pattern, ONE compile (`--features all -o -`, the bench's flags), and the
emitted C is read for:
  P9  the forward unanchored scan's idle-state skip: `skip0` = the skip is
      gated on `forward_state == 0`; `nseed` = distinct values of the
      `<p>_forward_seed_state` table (>= 2: a leading context-reading
      assertion gives a second idle state the skip never covers);
      `seedstay` = bytes the non-zero seed state stays on (its self-loop).
  P10 the stamps RX_REQ_WHY / RX_REQ_BYTE / RX_ENGINE / RX_DFA_SCAN.
Env: PCREC, CORPUS (repo root), BENCH, OUT (tsv path), JOBS.
"""
import concurrent.futures as cf, glob, os, re, subprocess, sys

E = os.environ
PCREC = E.get("PCREC"); CORPUS = E.get("CORPUS"); BENCH = E.get("BENCH")
OUT = E.get("OUT"); JOBS = int(E.get("JOBS", "2"))
TO = ["/usr/bin/gnutimeout", "-k", "2", "60"]


def dec_field(b):
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


def corpus_pop():
    rows, seen, files = [], set(), []
    for root, _d, fs in os.walk(os.path.join(CORPUS, "tests")):
        files += [os.path.join(root, f) for f in fs if f.endswith(".rxt")]
    for f in sorted(files):
        r = subprocess.run(TO + [PCREC, "--list-source", f], capture_output=True)
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
            enc = "utf8" if fl[8].decode() == "utf8" else "byte"
            ic = "i" in fl[5].decode()
            key = (pat, enc, ic)
            if key in seen:
                continue
            seen.add(key)
            rows.append(dict(pop="corpus", id=f"{rel}:{fl[1].decode()}", enc=enc, icase=ic, pat=pat))
    return rows


def bench_pop():
    rows = []
    for p in sorted(glob.glob(os.path.join(BENCH, "bench", "*", "patterns", "*.rx"))):
        sb = p.split(os.sep)[-3]
        b = open(p, "rb").read().rstrip(b"\n")
        if b and b"\x00" not in b:
            rows.append(dict(pop="bench", id=f"{sb}/{os.path.basename(p)[:-3]}",
                             enc="utf8" if sb == "utf8" else "byte", icase=False, pat=b))
    have = {r["id"] for r in rows}
    cap = os.path.join(BENCH, "bench", "capability", "patterns.rxt")
    r = subprocess.run(TO + [PCREC, "--list-source", cap], capture_output=True)
    for ln in r.stdout.split(b"\n"):
        fl = ln.split(b"\t")
        if len(fl) < 9 or fl[0] not in (b"pattern", b"pattern-esc"):
            continue
        name = fl[2].decode() or f"L{fl[1].decode()}"
        rid = f"capability/{name}"
        if rid in have:
            continue
        pat = dec_field(fl[4])
        if pat and b"\x00" not in pat:
            rows.append(dict(pop="bench", id=rid, enc="utf8" if fl[8].decode() == "utf8" else "byte",
                             icase="i" in fl[5].decode(), pat=pat))
    return rows


STAMPS = ("REQ_WHY", "REQ_BYTE", "REQ_RUN", "ENGINE", "ENGINE_SEL", "DFA_SCAN", "DFA_PREFILTER",
          "VM_PREFILTER", "VM_START", "DFA_START")


def one(r):
    text = (b"(?i)" if r["icase"] else b"") + r["pat"]
    cmd = ["nice", "-n", "10"] + TO + [PCREC, "--features", "all", "-p", "rx", "-o", "-"]
    if r["enc"] == "utf8":
        cmd += ["-e", "utf8"]
    p = subprocess.run(cmd + ["--pattern", text], capture_output=True)
    o = dict(pop=r["pop"], id=r["id"], enc=r["enc"], icase=int(r["icase"]), pat_hex=r["pat"].hex())
    if p.returncode != 0:
        o["refused"] = "timeout" if p.returncode in (124, 137) else "rc%d" % p.returncode
        return o
    c = p.stdout.decode("latin-1")
    for s in STAMPS:
        m = re.search(r"^#define RX_%s (.*)$" % s, c, re.M)
        o[s] = m.group(1).strip().strip('"') if m else "-"
    o["skip0"] = int("if (forward_state == 0 && last_accept_position == (size_t)-1)" in c)
    m = re.search(r"rx_forward_seed_state\[(\d+)\] = \{([^}]*)\}", c)
    seeds = sorted({int(x) for x in m.group(2).replace("\n", " ").split(",") if x.strip()}) if m else []
    o["nseed"] = len(seeds)
    o["seeds"] = ",".join(map(str, seeds))
    # each non-zero seed: how many bytes it stays on, and whether every other
    # byte leaves by ONE door (scan-shaped, src/opt/scanedge.c precondition 1)
    shapes = []
    try:
        i = c.index("rx_forward_seed_state[")
        f0 = c.rfind("static int rx_prefilter(", 0, i)
        f0 = f0 if f0 >= 0 else c.rfind("\nint rx_search(", 0, i)
        def arr(name):
            m2 = re.search(r"%s\[(\d+)\] = \{([^}]*)\}" % name, c[f0:])
            return [int(x) for x in m2.group(2).replace("\n", " ").split(",") if x.strip()]
        cls = arr("rx_forward_byte_class"); nxt = arr("rx_forward_next_state")
        ncls = max(cls) + 1
        pm = re.search(r'^#define RX_DFA_TABLE "premultiplied"', c, re.M) is not None
        for sd in seeds:
            if sd == 0:
                continue
            base = sd if pm else sd * ncls
            tr = [nxt[base + cls[b]] for b in range(256)]
            stay = sum(1 for t in tr if t == sd)
            exits = {t for t in tr if t != sd}
            shapes.append("%d:%d:%s" % (sd, stay, "scan" if len(exits) == 1 else "x%d" % len(exits)))
    except (ValueError, AttributeError, IndexError):
        if seeds:
            shapes.append("unread")
    o["seedshape"] = ";".join(shapes)
    return o


def main():
    rows = corpus_pop() + bench_pop()
    if E.get("LIMIT"): rows = [r for r in rows if r["pop"] == "bench"][:int(E["LIMIT"])]
    cols = ["pop", "id", "enc", "refused", "skip0", "nseed", "seeds", "seedshape"] + list(STAMPS) + ["icase", "pat_hex"]
    with open(OUT, "w") as f, cf.ThreadPoolExecutor(JOBS) as ex:
        f.write("\t".join(cols) + "\n")
        for o in ex.map(one, rows):
            f.write("\t".join(str(o.get(k, "")) for k in cols) + "\n")
    print("census rows", len(rows), file=sys.stderr)


main()
