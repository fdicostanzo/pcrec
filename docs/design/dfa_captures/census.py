#!/usr/bin/env python3
"""[dfacap] The capture-cause census behind dfa_captures_research.md §3.

Compile-side only: no subject is matched, nothing is timed. Every number is a
COUNT read off the compiler's own stamps (`--emit-facts`' decisions section).

Population: every `pattern`/`pattern-esc` block of every tests/**/*.rxt
(via `pcrec --list-source`), plus pcrec-bench's patterns (read-only): the
sub-benches with a patterns.rxt via --list-source, the others' *.rx exports.
Deduplicated on the pattern bytes (the first block's flags/encoding kept),
which keeps the sweep near the brief's ~6000-compile budget.

Pass 1: `--features all` (the shipped default: captures on, engine auto).
Pass 2: only for rows whose RX_ENGINE_WHY names a capture group, the SAME
compile with `--no-captures`: the compiler's own answer to "what engine would
this pattern get if captures cost nothing", and its next reason if still VM.

    PCREC=build/pcrec TESTS=tests BENCH=/path/to/pcrec-bench/bench \
    nice -n 10 python3 census.py > census.tsv

Columns: src name enc flags ncaps engine why prefilter engine_nc why_nc
         textscan pattern_esc
`textscan` is a TEXT heuristic over the pattern (marked as such in the memo):
the VM-only construct spellings present besides captures, and `capinlook`
when a capturing `(` sits inside a lookaround body.
"""
import os, re, subprocess, sys

PCREC = os.environ.get("PCREC", "build/pcrec")
TESTS = os.environ.get("TESTS", "tests")
BENCH = os.environ.get("BENCH", "")
COLS = ("kind line name value pattern flags features features_only encoding "
        "engine budget_steps budget_frames with from pcrec export tags oracle "
        "esc tune").split()


def dec(b):
    out = bytearray(); i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5c and i + 1 < len(b):
            n = b[i + 1]
            m = {0x5c: 0x5c, 0x74: 9, 0x6e: 10, 0x72: 13}
            if n in m:
                out.append(m[n]); i += 2; continue
            if n == 0x78 and i + 3 < len(b):
                try:
                    out.append(int(b[i + 2:i + 4], 16)); i += 4; continue
                except ValueError:
                    pass
        out.append(c); i += 1
    return bytes(out)


def list_source(path):
    r = subprocess.run([PCREC, "--list-source", path], capture_output=True,
                       timeout=120)
    rows = []
    for l in r.stdout.split(b"\n"):
        if l.startswith(b"#") or not l.strip():
            continue
        f = l.split(b"\t")
        if len(f) < len(COLS):
            continue
        d = dict(zip(COLS, f))
        if d["kind"] not in (b"pattern", b"pattern-esc"):
            continue
        rows.append((d["name"].decode("utf8", "replace"), dec(d["pattern"]),
                     d["flags"].decode(), d["encoding"].decode()))
    return rows


def population():
    seen, pats = {}, set()

    def add(pat, fl, enc, tag):
        if pat not in pats:
            pats.add(pat); seen[(pat, fl, enc)] = tag
    for root, _, files in os.walk(TESTS):
        for fn in sorted(files):
            if fn.endswith(".rxt"):
                p = os.path.join(root, fn)
                for name, pat, fl, enc in list_source(p):
                    add(pat, fl, enc, ("corpus", name))
    if BENCH:
        for sb in sorted(os.listdir(BENCH)):
            d = os.path.join(BENCH, sb)
            rxt = os.path.join(d, "patterns.rxt")
            if os.path.isfile(rxt):
                for name, pat, fl, enc in list_source(rxt):
                    add(pat, fl, enc, ("bench:" + sb, name))
                continue
            pd = os.path.join(d, "patterns")
            if os.path.isdir(pd):
                for fn in sorted(os.listdir(pd)):
                    if fn.endswith(".rx"):
                        with open(os.path.join(pd, fn), "rb") as fh:
                            pat = fh.read()
                        add(pat, "", "", ("bench:" + sb, fn[:-3]))
    return seen


def compile_facts(pat, fl, enc, nocaps):
    a = [PCREC, "--features", "all", "--emit-facts", "-p", "rx"]
    if "i" in fl:
        a.append("-i")
    if enc in ("utf8", "utf-8") or "u" in fl:
        a += ["-e", "utf8"]
    if nocaps:
        a.append("--no-captures")
    a += ["--pattern", pat]
    try:
        r = subprocess.run(a, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return {"RX_ENGINE": "TIMEOUT"}
    if r.returncode != 0:
        msg = r.stderr.decode("utf8", "replace").strip().split("\n")[0]
        return {"RX_ENGINE": "REFUSED", "RX_ENGINE_WHY": msg}
    st = {}
    for l in r.stdout.decode("utf8", "replace").split("\n"):
        f = l.split("\t")
        if len(f) == 3 and f[1].startswith("RX_"):
            st.setdefault(f[1], f[2].strip('"'))
    return st


LOOK_OPEN = re.compile(rb"\(\?(?:=|!|<=|<!|\*|<\*)|\(\*(?:pla|plb|nla|nlb|positive_look|negative_look|napla|naplb|non_atomic)[a-z_]*:")


def textscan(p):
    t = []
    if re.search(rb"\(\?>|[*+?}]\+", p): t.append("atomic")
    if re.search(rb"\\[1-9]|\\g\{?-?[0-9]|\\k[<{']|\(\?P=", p): t.append("bref")
    if re.search(rb"\(\?(?:R|[+-]?[0-9]+\)|&|P>)|\\g<|\\g'", p): t.append("call")
    if re.search(rb"\\K", p): t.append("kreset")
    if re.search(rb"\(\*[A-Z]", p): t.append("verb")
    if re.search(rb"\(\?\(", p): t.append("cond")
    if LOOK_OPEN.search(p): t.append("look")
    # a capturing `(` inside a lookaround body (bracket depth walk, rough)
    i, depth, look_at = 0, 0, []
    while i < len(p):
        c = p[i:i + 1]
        if c == b"\\":
            i += 2; continue
        if c == b"[":
            j = i + 1
            if p[j:j + 1] == b"^": j += 1
            if p[j:j + 1] == b"]": j += 1
            while j < len(p) and p[j:j + 1] != b"]":
                j += 2 if p[j:j + 1] == b"\\" else 1
            i = j + 1; continue
        if c == b"(":
            if LOOK_OPEN.match(p, i):
                look_at.append(depth)
            elif look_at and (p[i + 1:i + 2] != b"?" or p[i + 1:i + 3] in (b"?<", b"?P", b"?'")) \
                    and p[i + 1:i + 3] not in (b"?<=", b"?<!") and p[i + 1:i + 2] != b"*":
                if "capinlook" not in t: t.append("capinlook")
            depth += 1
        elif c == b")":
            depth -= 1
            if look_at and look_at[-1] == depth:
                look_at.pop()
        i += 1
    return ",".join(t)


def main():
    pop = population()
    print("\t".join("src name enc flags ncaps engine why prefilter engine_nc "
                    "why_nc textscan pattern_esc".split()))
    n = 0
    for (pat, fl, enc), (src, name) in pop.items():
        s = compile_facts(pat, fl, enc, False); n += 1
        eng, why = s.get("RX_ENGINE", ""), s.get("RX_ENGINE_WHY", "")
        e2 = w2 = ""
        if eng == "vm" and why.startswith("capture group"):
            s2 = compile_facts(pat, fl, enc, True); n += 1
            e2, w2 = s2.get("RX_ENGINE", ""), s2.get("RX_ENGINE_WHY", "")
        esc = pat.decode("latin-1").encode("unicode_escape").decode()
        print("\t".join([src, name, enc, fl, s.get("RX_NCAPS", ""), eng,
                         why.replace("\t", " "), s.get("RX_VM_PREFILTER", ""),
                         e2, w2.replace("\t", " "), textscan(pat), esc]))
    print("# compiles: %d, population: %d" % (n, len(pop)), file=sys.stderr)


if __name__ == "__main__":
    main()
