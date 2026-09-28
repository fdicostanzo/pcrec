#!/usr/bin/env python3
"""census.py PCREC TREE BENCH OUT.tsv [EXTRA-FLAGS...] -- the §A/§C/§D population census.

Population: every `pattern`/`pattern-esc` block of every .rxt under
TREE/tests and TREE/examples (via PCREC --list-source, head-row defaults for
encoding/flags applied; `config`/`with` cascades NOT resolved), plus every
BENCH/bench/*/patterns/*.rx (encoding utf8 for bench/utf8, byte otherwise).
Per UNIQUE (pattern, encoding, caseless) it records the lexical UCP-relevant
features and the engine stamps of one `--features all` compile.  For every
\\b/\\B-bearing pattern it ALSO compiles (a) under -e utf8 and (b) the
lookaround rewrite (\\b, \\B outside classes -> their spellings) under the
pattern's own encoding.  Writes one TSV row per unique pattern."""
import os, re, subprocess, sys, concurrent.futures as cf
PCREC, TREE, BENCH, OUT = sys.argv[1:5]
EXTRA = sys.argv[5:]   # e.g. --no-captures: the second census (§D)
LB  = rb"(?:(?<=\w)(?!\w)|(?<!\w)(?=\w))"
LBB = rb"(?:(?<=\w)(?=\w)|(?<!\w)(?!\w))"

def decode_escape(s):   # the --list-source vocabulary: \t \n \r \\ \xNN (emit_sweep.py's)
    out, b, i = bytearray(), s.encode("utf-8", "surrogateescape"), 0
    while i < len(b):
        c = b[i]
        if c == 0x5C and i + 1 < len(b):
            n = b[i + 1]
            if n in b"tnr\\":
                out.append({ord('t'): 9, ord('n'): 10, ord('r'): 13, 0x5C: 0x5C}[n]); i += 2; continue
            if n == ord('x') and i + 3 < len(b):
                try: out.append(int(b[i + 2:i + 4], 16)); i += 4; continue
                except ValueError: pass
        out.append(c); i += 1
    return bytes(out)

def scan(p):
    """Lexical features + the \\b-rewritten pattern.  Tracks classes (POSIX
    names, a leading ']' literal), \\Q..\\E, and escapes with braces."""
    f, out, i, n, incls = set(), bytearray(), 0, len(p), False
    if re.match(rb"^(\(\*[A-Z_]+(=\d+)?\))*", p):
        for v in re.findall(rb"\(\*([A-Z_]+)", re.match(rb"^(\(\*[A-Z_]+(=\d+)?\))*", p).group(0)):
            f.add("verb:" + v.decode())
    while i < n:
        c = p[i]
        if c == 0x5C and i + 1 < n:
            e = chr(p[i + 1])
            if e == 'Q':
                j = p.find(b"\\E", i + 2); j = n if j < 0 else j + 2
                out += p[i:j]; i = j; continue
            tok_end = i + 2
            if e in "pPxNgko" and tok_end < n and p[tok_end] == ord('{'):
                k = p.find(b"}", tok_end); tok_end = n if k < 0 else k + 1
            if e in "pP": f.add("p")
            if not incls and e in "bB":
                f.add(e); out += LB if e == 'b' else LBB; i = tok_end; continue
            if e in "wWdDsShHvVR": f.add({"W": "w", "D": "d", "S": "s", "H": "h", "V": "v"}.get(e, e))
            out += p[i:tok_end]; i = tok_end; continue
        if not incls and c == ord('['):
            incls = True; out.append(c); i += 1
            if i < n and p[i] == ord('^'): out.append(p[i]); i += 1
            if i < n and p[i] == ord(']'): out.append(p[i]); i += 1
            continue
        if incls and c == ord('[') and p[i + 1:i + 2] == b":":
            k = p.find(b":]", i + 2)
            if k > 0:
                f.add("posix:" + p[i + 2:k].lstrip(b"^").decode("latin-1")); out += p[i:k + 2]; i = k + 2; continue
        if incls and c == ord(']'):
            incls = False; out.append(c); i += 1; continue
        if not incls and c == ord('(') and p[i + 1:i + 2] == b"?":
            m = re.match(rb"\(\?([a-zA-Z^]*)(-[a-zA-Z]*)?[:)]", p[i:])
            if m and b"i" in m.group(1): f.add("i")
        if c >= 0x80: f.add("nonascii")
        out.append(c); i += 1
    return f, bytes(out)

def stamps(pat, enc, ci):
    argv = [PCREC, "-p", "rx", "-e", enc, "--features", "all", "-o", "-"] + EXTRA + ["--pattern", pat]
    if ci: argv.insert(1, "-i")
    try:
        r = subprocess.run(argv, capture_output=True, timeout=180)
    except subprocess.TimeoutExpired:
        return ("TIMEOUT", "", "")
    if r.returncode != 0:
        return ("REFUSED", "", r.stderr.decode("utf-8", "replace").strip().splitlines()[0][:160] if r.stderr else "")
    head = r.stdout[:20000].decode("utf-8", "replace")
    g = lambda k: (re.search(r'#define RX_%s "((?:[^"\\]|\\.)*)"' % k, head) or [None, ""])[1]
    return (g("ENGINE"), g("ENGINE_SEL"), g("ENGINE_WHY"))

pop = []   # (source, id, pattern bytes, enc, ci)
for root in ("tests", "examples"):
    for dp, _, fns in os.walk(os.path.join(TREE, root)):
        for fn in sorted(fns):
            if not fn.endswith(".rxt"): continue
            path = os.path.join(dp, fn)
            r = subprocess.run([PCREC, "--list-source", path], capture_output=True)
            if r.returncode: continue
            hd_enc, hd_flags, seen_pat = "", "", False
            for line in r.stdout.decode("utf-8", "surrogateescape").splitlines():
                if line.startswith("#") or not line.strip(): continue
                fl = line.split("\t")
                if len(fl) < 10: continue
                if fl[0] in ("pattern", "pattern-esc"):
                    seen_pat = True
                    enc = fl[8] or hd_enc or "byte"; flags = fl[5] or hd_flags
                    pop.append(("corpus", "%s:%s" % (os.path.relpath(path, TREE), fl[1]), decode_escape(fl[4]), enc, "i" in flags))
                elif not seen_pat and fl[0] == "encoding": hd_enc = fl[3]
                elif not seen_pat and fl[0] == "flags": hd_flags = fl[3]
for dp in sorted(os.listdir(os.path.join(BENCH, "bench"))):
    pd = os.path.join(BENCH, "bench", dp, "patterns")
    if not os.path.isdir(pd): continue
    for fn in sorted(os.listdir(pd)):
        if fn.endswith(".rx"):
            pop.append(("bench", "%s/%s" % (dp, fn[:-3]), open(os.path.join(pd, fn), "rb").read().rstrip(b"\n"),
                        "utf8" if dp == "utf8" else "byte", False))
uniq = {}
for s in pop: uniq.setdefault((s[2], s[3], s[4]), []).append(s)
print("population rows", len(pop), "unique (pattern,enc,ci)", len(uniq), file=sys.stderr)

def work(key):
    pat, enc, ci = key
    feats, rew = scan(pat)
    if b"\x00" in pat: return key, feats, ("SKIP-NUL", "", ""), None, None
    try: pats = pat.decode("utf-8")
    except UnicodeDecodeError: pats = pat.decode("utf-8", "surrogateescape")
    st = stamps(pats, enc, ci)
    u8 = rw = None
    if feats & {"b", "B"}:
        u8 = st if enc == "utf8" else stamps(pats, "utf8", ci)
        rw = stamps(rew.decode("utf-8", "surrogateescape"), enc, ci)
    return key, feats, st, u8, rw

with cf.ThreadPoolExecutor(3) as ex, open(OUT, "w") as o:
    o.write("sources\tn_rows\tenc\tci\tfeatures\tengine\tsel\twhy\tb_utf8_engine\tb_rewrite_engine\tb_rewrite_why\tpattern\n")
    for k, (key, feats, st, u8, rw) in enumerate(ex.map(work, list(uniq))):
        pat, enc, ci = key
        srcs = uniq[key]
        o.write("\t".join([",".join(sorted({s[0] for s in srcs})), str(len(srcs)), enc, "i" if ci else "",
                           " ".join(sorted(feats)), st[0], st[1], st[2].replace("\t", " "),
                           u8[0] if u8 else "", rw[0] if rw else "", (rw[2] if rw else "").replace("\t", " "),
                           srcs[0][1] + " " + pat.decode("utf-8", "backslashreplace").replace("\t", "\\t").replace("\n", "\\n")[:200]]) + "\n")
        if k % 500 == 0: print("done", k, file=sys.stderr, flush=True)
