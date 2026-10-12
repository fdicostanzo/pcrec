#!/usr/bin/env python3
"""[MATCH-SPLIT] STEP-0 survey driver (lane mssurvey, 2026-10-12).  COMPILE-ONLY:
no subject is matched here and no clock is read.  (The libpcre2 controls live in
msoracle.py and the counted-work arm in qwork.py.)

Populations (docs/design/match_split_requirements.md section 6.1), reported
separately: bench, corpus (with the D27/adversarial files flagged), catalog
(realistic_patterns.txt), idioms (idioms.txt, added here), planted (C4).
The population builder is docs/dev/optloop/revend/census.py's, copied (that file
reads its environment at import).

    PCREC=build/pcrec PROBE=build/ms/msprobe BENCH=/path/pcrec-bench \\
    CORPUS=<repo root> OUT=build/ms/out JOBS=3 python3 survey.py [--plant NAME]

Per pattern: the path-class analysis (msclass.py, over msprobe's raw-parse AST),
today's route read from the artifact's STAMPS (`pcrec --emit-facts`'s decisions
section, never emitted comments) plus the emitted `start_max`, the shipped
facts, and the sub-language compiles: the whole tree unparsed (control C-RT),
the FREE part, the END part.
"""
import argparse, collections, concurrent.futures as cf, glob, gzip, hashlib, json
import os, re, subprocess, sys, threading

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import msclass

E = os.environ
PCREC = E.get("PCREC", "build/pcrec")
PROBE = E.get("PROBE", "build/ms/msprobe")
BENCH = E.get("BENCH", "/home/pcrec/projects/pcrec-bench")
CORPUS = E.get("CORPUS", ".")
OUT = E.get("OUT", "build/ms/out")
JOBS = int(E.get("JOBS", "3"))
GNUTIMEOUT = E.get("GNUTIMEOUT", "/usr/bin/gnutimeout")
NICE = ["nice", "-n", "10"]
D27_FILES = ("composition_d27", "/d27/", "matrix.rxt")


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
            rows.append(dict(pop="bench", id=f"{sb}/{os.path.basename(p)[:-3]}", suite=sb,
                             enc="utf8" if sb == "utf8" else "byte", icase=False, adv=False, pat=b))
    return rows


def corpus_pop():
    rows, files = [], []
    for root, _d, fs in os.walk(os.path.join(CORPUS, "tests")):
        files += [os.path.join(root, f) for f in fs if f.endswith(".rxt")]
    for f in sorted(files):
        r = subprocess.run(NICE + [GNUTIMEOUT, "120", PCREC, "--list-source", f], capture_output=True)
        if r.returncode != 0:
            continue
        rel = os.path.relpath(f, CORPUS)
        adv = any(t in rel or t in "/" + rel for t in D27_FILES)
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
            enc = fl[8].decode() or "byte"
            rows.append(dict(pop="corpus", id=f"{rel}:{fl[1].decode()}",
                             suite=rel.split(os.sep)[1] if os.sep in rel else rel,
                             enc="utf8" if enc == "utf8" else "byte", icase="i" in fl[5].decode(),
                             adv=adv, pat=pat))
    return rows


def file_pop(pop, path, named):
    rows = []
    for i, ln in enumerate(open(path, "rb").read().split(b"\n")):
        if not ln or ln.startswith(b"#"):
            continue
        if named:
            nm, _, pat = ln.partition(b"\t")
            rid = nm.decode()
        else:
            pat, rid = ln, f"L{i + 1}"
        if pat:
            rows.append(dict(pop=pop, id=f"{pop}/{rid}", suite=pop,
                             enc="utf8" if rid.endswith("_u8") else "byte", icase=False, adv=False, pat=pat))
    return rows


def planted_pop():
    rows = []
    for i, ln in enumerate(open(os.path.join(HERE, "planted.txt"), "rb").read().split(b"\n")):
        if not ln or ln.startswith(b"#"):
            continue
        f = ln.split(b"\t")
        rows.append(dict(pop="planted", id=f"planted/P{i}", suite="planted", enc="byte", icase=False,
                         adv=False, pat=f[1], expect=f[0].decode(),
                         expect_flags=(f[3].decode() if len(f) > 3 else "")))
    return rows


def text_of(r):
    return (b"(?i)" if r["icase"] else b"") + r["pat"]


# ---- the probe ------------------------------------------------------------------

def run_probe(rows):
    inp = "".join("%d\t%s\t%s\n" % (i, r["enc"], text_of(r).hex()) for i, r in enumerate(rows))
    res = subprocess.run(NICE + [GNUTIMEOUT, "1800", PROBE], input=inp.encode(), capture_output=True)
    out = {}
    for ln in res.stdout.decode("utf8", "replace").split("\n"):
        f = ln.split("\t", 3)
        if len(f) == 4 and f[0].isdigit():
            out[int(f[0])] = f
    return out


# ---- compile layer, cached --------------------------------------------------------

_cache, _cache_lock, _cache_fh = {}, threading.Lock(), None


def cache_open(path):
    global _cache_fh
    if os.path.exists(path):
        for ln in open(path):
            try:
                k, v = json.loads(ln)
                _cache[k] = v
            except ValueError:
                pass
    _cache_fh = open(path, "a")


def cached(kind, enc, text, fn):
    k = hashlib.sha1(kind.encode() + b"\0" + enc.encode() + b"\0" + text).hexdigest()
    with _cache_lock:
        if k in _cache:
            return _cache[k]
    v = fn()
    with _cache_lock:
        _cache[k] = v
        if _cache_fh:
            _cache_fh.write(json.dumps([k, v]) + "\n")
            _cache_fh.flush()
    return v


def pcrec_cmd(enc, text, extra):
    cmd = NICE + [GNUTIMEOUT, "-k", "2", "40", PCREC] + extra + ["--features", "all"]
    if enc == "utf8":
        cmd += ["-e", "utf8"]
    return cmd + ["--pattern", text]


def facts_of(text, enc):
    def go():
        p = subprocess.run(pcrec_cmd(enc, text, ["--emit-facts=" + enc]), capture_output=True)
        if p.returncode != 0:
            why = p.stderr.decode("utf8", "replace").strip().split("\n")[0][:140]
            return dict(refused=("timeout" if p.returncode in (124, 137) else why or "rc%d" % p.returncode))
        d, sect = dict(refused=""), None
        for ln in p.stdout.decode("utf8", "replace").split("\n"):
            if ln.startswith("#section"):
                sect = ln.split()[1]; continue
            if ln.startswith("#") or not ln:
                continue
            f = ln.split("\t")
            if sect == "facts" and len(f) >= 8:
                d["f_" + f[1]] = f[6]
                d["w_" + f[1]] = f[7]
            elif sect == "decisions" and len(f) >= 3:
                d[f[1].replace("RX_", "")] = f[2].strip('"')
        return d
    return cached("facts", enc, text, go)


def startmax_of(text, enc):
    def go():
        p = subprocess.run(pcrec_cmd(enc, text, ["-o", "-"]), capture_output=True)
        if p.returncode != 0:
            return ""
        m = re.search(rb"const size_t start_max = ([^;]*?)\s*(?:/\*[^;]*)?;", p.stdout)
        return m.group(1).decode() if m else "-"
    return cached("smax", enc, text, go)


ROUTE_KEYS = ("ENGINE", "DFA_SCAN", "DFA_PREFILTER", "DFA_START", "VM_PREFILTER", "REQ_BYTE", "END_WINDOW")


def route_sig(d):
    return tuple(d.get(k, "") for k in ROUTE_KEYS) + (d.get("f_start_anchor", ""), d.get("f_end_pin", ""))


# ---- prior mass ----------------------------------------------------------------

def load_prior():
    ppm = [2] * 256
    sect = False
    for ln in open(os.path.join(CORPUS, "src", "findings", "default.rxt")):
        t = ln.split()
        if len(t) == 3 and t[0] == "row" and re.fullmatch(r"[0-9a-f]{2}", t[1]) and len(t[2]) and t[2].isdigit():
            ppm[int(t[1], 16)] = int(t[2])
        if t[:1] == ["analysis"] and t[1:2] not in (["default"],) and sect:
            break
        if t[:2] == ["analysis", "default"]:
            sect = True
    return ppm


def set_mass(val, ppm):
    m = re.fullmatch(r"\d+:([0-9a-f]{64})", val or "")
    if not m:
        return None, None
    bits = bytes.fromhex(m.group(1))
    members = [j * 8 + b for j in range(32) for b in range(8) if bits[j] >> b & 1]
    return len(members), sum(ppm[x] for x in members)


# ---- per row -------------------------------------------------------------------------

def analyze(r, probe_row, ppm):
    r["status"] = "noprobe"
    if probe_row is None:
        return
    _id, status, view, js = probe_row
    r["status"], r["view"] = status, int(view)
    if status != "ok":
        return
    ast = json.loads(js)
    c = msclass.classify(ast)
    order = ["S", "G", "LS", "E", "LE", "F"]
    present = [x for x in order if x in c["classes"]]
    r["mix"] = "+".join(present) if present else "-"
    r["nlive"] = len(c["elems"])
    r["elems"] = ";".join("%d:%d:%d:%d" % e for e in c["elems"])
    r["both"] = int(any(sp and ep for (sp, ep, z, lu) in c["elems"]))
    r["dead"], r["ml_landmark"], r["kreset"] = c["dead"], c["ml_landmark"], c["kreset"]
    r["look_pin"], r["ref"] = ",".join(c["look_pin"]), ",".join(c["ref"])
    red = c["red"]
    r["red"] = "capped" if red is None else ",".join(f"{k}:{v[0]}" for k, v in sorted(red.items()))
    r["z_by_class"] = ",".join(sorted({cl for cl, (sp, ep, z, lu) in zip(c["classes"], c["elems"]) if z == msclass.Z}))
    r["lu_E"] = int(any(cl in ("E", "LE") and lu for cl, (sp, ep, z, lu) in zip(c["classes"], c["elems"])))
    r["lu_Eonly"] = int(any(cl in ("E", "LE") and lu for cl, (sp, ep, z, lu) in zip(c["classes"], c["elems"])))
    r["free_live"] = int("F" in c["classes"])
    t = msclass.sublang_texts(ast)
    r["unparse"] = t.get("unsupported", "ok")
    r["txtA"], r["txtNP"], r["txtE"] = (t.get(k) for k in ("A", "NP", "E")) if "A" in t else (None, None, None)
    r["approx"] = ",".join(t.get("approx", []))
    r["ast_nodes"] = js.count("[")


def compile_row(r, ppm):
    enc = r["enc"]
    text = text_of(r)
    d = facts_of(text, enc)
    r["refused"] = d["refused"]
    if d["refused"] or r["status"] != "ok":
        return
    for k in ROUTE_KEYS + ("ENGINE_SEL", "VM_START_SCAN", "REQ_RUN", "REQ_WHY", "ENGINE_WHY",
                           "VM_PREFILTER_LANG", "VM_RESEED", "DFA_MATCH", "DFA_SCAN_EDGE", "DFA_PREFILTER_OFFSETS"):
        r[k] = d.get(k, "")
    for k in ("start_anchor", "end_pin", "end_window", "empty_admits", "nullable", "start_set", "req_byte"):
        r["f_" + k] = d.get("f_" + k, "")
    r["w_end_pin"] = d.get("w_end_pin", "")
    r["start_max"] = startmax_of(text, enc) if (r["DFA_SCAN"] == "attempt") else ""
    n, mass = set_mass(d.get("f_start_set", ""), ppm)
    r["ss_pop"], r["ss_mass"] = ("" if n is None else n), ("" if mass is None or enc != "byte" else mass)
    # control C-RT: the unparse of the WHOLE tree compiles to the same route
    if r.get("txtA") is not None:
        a = facts_of(r["txtA"].encode("latin-1", "backslashreplace"), enc)
        r["rt"] = "refused" if a["refused"] else ("same" if route_sig(a) == route_sig(d) else "differs")
        r["rt_diff"] = "" if r["rt"] != "differs" else ",".join(
            f"{k}:{d.get(k, d.get('f_'+k[2:], ''))}>{a.get(k, a.get('f_'+k[2:], ''))}"
            for k in ROUTE_KEYS + ("f_start_anchor", "f_end_pin")
            if (d.get(k, "") != a.get(k, "")) and k in ROUTE_KEYS or k.startswith("f_") and d.get(k) != a.get(k))
    else:
        r["rt"] = "unparse:" + r.get("unparse", "")
    # the FREE part (only meaningful when the pattern has a pinned class)
    if r.get("mix", "F") != "F" and r.get("txtNP"):
        f = facts_of(r["txtNP"].encode("latin-1", "backslashreplace"), enc)
        r["fr_refused"] = f["refused"]
        if not f["refused"]:
            for k in ("ENGINE", "DFA_SCAN", "DFA_PREFILTER", "DFA_START", "VM_PREFILTER", "REQ_BYTE"):
                r["fr_" + k] = f.get(k, "")
            r["fr_start_anchor"] = f.get("f_start_anchor", "")
            n2, m2 = set_mass(f.get("f_start_set", ""), ppm)
            r["fr_ss_pop"], r["fr_ss_mass"] = ("" if n2 is None else n2), ("" if m2 is None or enc != "byte" else m2)
            r["fr_start_max"] = startmax_of(r["txtNP"].encode("latin-1", "backslashreplace"), enc) \
                if f.get("DFA_SCAN") == "attempt" else ""
    # the END part
    if r.get("txtE") and r.get("mix", "F") not in ("E", "LE"):
        f = facts_of(r["txtE"].encode("latin-1", "backslashreplace"), enc)
        r["en_refused"] = f["refused"]
        if not f["refused"]:
            r["en_end_pin"], r["en_end_window"] = f.get("f_end_pin", ""), f.get("f_end_window", "")
            r["en_DFA_START"], r["en_DFA_SCAN"] = f.get("DFA_START", ""), f.get("DFA_SCAN", "")


COLS = ["pop", "id", "suite", "enc", "icase", "adv", "status", "view", "refused", "mix", "nlive", "elems", "both",
        "dead", "ml_landmark", "kreset", "look_pin", "ref", "red", "z_by_class", "lu_E", "free_live", "unparse",
        "approx", "ast_nodes",
        "ENGINE", "ENGINE_SEL", "ENGINE_WHY", "DFA_SCAN", "DFA_PREFILTER", "DFA_PREFILTER_OFFSETS", "DFA_START",
        "DFA_MATCH", "DFA_SCAN_EDGE", "VM_PREFILTER", "VM_PREFILTER_LANG", "VM_RESEED", "VM_START_SCAN",
        "REQ_BYTE", "REQ_RUN", "REQ_WHY", "END_WINDOW", "start_max",
        "f_start_anchor", "f_end_pin", "w_end_pin", "f_end_window", "f_empty_admits", "f_nullable",
        "f_start_set", "ss_pop", "ss_mass", "rt", "rt_diff",
        "fr_refused", "fr_ENGINE", "fr_DFA_SCAN", "fr_DFA_PREFILTER", "fr_DFA_START", "fr_VM_PREFILTER",
        "fr_REQ_BYTE", "fr_start_anchor", "fr_start_max", "fr_ss_pop", "fr_ss_mass",
        "en_refused", "en_end_pin", "en_end_window", "en_DFA_START", "en_DFA_SCAN",
        "expect", "expect_flags", "pattern_hex", "txtA_hex", "txtNP_hex", "txtE_hex"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plant", action="append", default=[], help="C4 plant: ml_edge | look_end")
    ap.add_argument("--only-planted", action="store_true")
    ap.add_argument("--out-name", default="ms_rows.tsv.gz")
    a = ap.parse_args()
    msclass.PLANT.update(a.plant)
    os.makedirs(OUT, exist_ok=True)
    cache_open(os.path.join(OUT, "compile_cache.jsonl"))
    rows = []
    if not a.only_planted:
        rows += bench_pop() + corpus_pop()
        rows += file_pop("catalog", os.path.join(CORPUS, "docs/design/eng_brep_measurements/probes/realistic_patterns.txt"), False)
        rows += file_pop("idioms", os.path.join(HERE, "idioms.txt"), True)
    rows += planted_pop()
    ppm = load_prior()
    pr = run_probe(rows)
    print("rows", len(rows), "probed", len(pr), flush=True)
    sys.setrecursionlimit(200000)
    threading.stack_size(512 * 1024 * 1024)
    box = {}

    def work():
        for i, r in enumerate(rows):
            try:
                analyze(r, pr.get(i), ppm)
            except RecursionError:
                r["status"] = "recursion"
        with cf.ThreadPoolExecutor(max_workers=JOBS) as ex:
            list(ex.map(lambda r: compile_row(r, ppm), rows))
        box["done"] = True
    th = threading.Thread(target=work)
    th.start(); th.join()
    path = os.path.join(OUT, a.out_name)
    with gzip.open(path, "wt") as fh:
        fh.write("\t".join(COLS) + "\n")
        for r in rows:
            v = dict(r)
            v["pattern_hex"] = r["pat"].hex()
            for k in ("txtA", "txtNP", "txtE"):
                v[k + "_hex"] = (r.get(k) or "").encode("latin-1", "backslashreplace").hex()
            fh.write("\t".join(str(v.get(k, "")).replace("\t", " ").replace("\n", " ") for k in COLS) + "\n")
    print("wrote", path, len(rows))


if __name__ == "__main__":
    main()
