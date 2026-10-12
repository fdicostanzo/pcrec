#!/usr/bin/env python3
"""[COMPOSITE] design lane mscomp: the split twin (hand-composed, light).

For each case: compile the plain artifact (today, prefix rxp), the floor part
\\G(?:P) (rxf) and Q (rxq: given, or P with its floor anchors textually killed
to (?!)), write the controller, link with diff.c (libpcre2-8 10.46 as the
oracle) and run every startpos + find-all over generated subjects.

  twin.py PCREC CASES.tsv OUTDIR [--literal]
CASES.tsv: id <TAB> enc <TAB> pattern_hex <TAB> q_hex|auto
"""
import itertools, os, random, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GT = "/usr/bin/gnutimeout"


def kill(p: bytes):
    """P -> Q: \\G (REQUIRED: Q's own \\G would read Q's search_from), \\A and
    absolute ^ (optional: dead past the floor anyway, killed for Q's route)
    outside classes become (?!). Conservative: under (?m) ^ is kept; with a
    lookbehind \\A and ^ are kept, and a \\G declines the composite."""
    if re.search(rb"\(\?[a-z-]*x", p):
        return p
    lookbehind = b"(?<=" in p or b"(?<!" in p
    if lookbehind and b"\\G" in p:
        return None                       # a \G Q cannot kill: the composite declines
    keep_caret = lookbehind or re.search(rb"\(\?[a-zA-Z^-]*m", p) is not None
    out, i, cls = bytearray(), 0, False
    while i < len(p):
        c = p[i:i + 1]
        if c == b"\\" and i + 1 < len(p):
            two = p[i:i + 2]
            if two == b"\\Q":
                j = p.find(b"\\E", i + 2)
                j = len(p) if j < 0 else j + 2
                out += p[i:j]; i = j; continue
            if not cls and (two == b"\\G" or (two == b"\\A" and not lookbehind)):
                out += b"(?!)"; i += 2; continue
            out += two; i += 2; continue
        if cls:
            if c == b"]": cls = False
            out += c; i += 1; continue
        if c == b"[":
            cls = True; out += c; i += 1
            if p[i:i + 1] == b"^": out += b"^"; i += 1
            if p[i:i + 1] == b"]": out += b"]"; i += 1
            continue
        if c == b"^" and not keep_caret:
            out += b"(?!)"; i += 1; continue
        out += c; i += 1
    return bytes(out)


def floor_of(p: bytes):
    m = re.match(rb"((?:\(\*[A-Z_0-9=]+\))*)", p)
    head = m.group(1)
    return head + b"\\G(?:" + p[len(head):] + b")"


def subjects(p: bytes, enc):
    lits = sorted(set(ch for ch in p if 32 <= ch < 127 and chr(ch).isalnum()))[:4]
    alpha = [b" ", b"\n", b"x"] + [bytes([c]) for c in lits]
    alpha += [b"{", b"}", b"\t"] if (b"{" in p or b"\\s" in p) else []
    if enc == "utf8": alpha += [b"\xc3\xa9", b"\x80"]
    alpha = alpha[:7]
    out = [b""]
    for L in range(1, 5):
        out += [b"".join(t) for t in itertools.product(alpha, repeat=L)]
    rnd = random.Random(1)
    for _ in range(300):
        out.append(b"".join(rnd.choice(alpha) for _ in range(rnd.randint(5, 24))))
    return out


def run(cmd, **kw):
    return subprocess.run([GT, "120"] + cmd, capture_output=True, **kw)


def case(pcrec, cid, enc, pat, q, wd, literal):
    os.makedirs(wd, exist_ok=True)
    E = ["-e", "utf8"] if enc == "utf8" else []
    base = [pcrec, "--features", "all"] + E
    for pre, name, text in (("rxp", "plain", pat), ("rxf", "floor", floor_of(pat)), ("rxq", "q", q)):
        r = run(base + ["-p", pre, "-o", f"{wd}/{name}.c", "--pattern", text])
        if r.returncode:
            return f"{cid}\tREFUSED-{name}\t{r.stderr.decode(errors='replace').strip()[:120]}"
    has_g = "1" if b"\\G" in pat else "0"
    open(f"{wd}/ctrl.c", "w").write(open(f"{HERE}/ctrl.c.in").read().replace("@HAS_G@", has_g))
    cc = ["gcc", "-O1", "-std=gnu11", "-w", f"-DUTF={1 if enc == 'utf8' else 0}", "-I", wd] + \
         (["-DLITERAL"] if literal else []) + \
         ["-o", f"{wd}/t", f"{HERE}/diff.c", f"{wd}/ctrl.c", f"{wd}/floor.c", f"{wd}/q.c", f"{wd}/plain.c", "-lpcre2-8"]
    r = run(cc)
    if r.returncode:
        return f"{cid}\tBUILD-FAIL\t{r.stderr.decode(errors='replace').strip()[:200]}"
    stamps = {}
    for name in ("plain", "q"):
        src = open(f"{wd}/{name}.c", errors="replace").read()
        m = re.search(r'#define RX[PQ]_ENGINE "(\w+)"', src); e = m.group(1) if m else "?"
        m = re.search(r'#define RX[PQ]_DFA_SCAN "([\w-]+)"', src); sc = m.group(1) if m else "-"
        stamps[name] = f"{e}/{sc}"
    subj = b"\n".join(s.hex().encode() for s in subjects(pat, enc)) + b"\n"
    r = run([f"{wd}/t", pat.hex()], input=subj)
    return f"{cid}\t{enc}\tplain={stamps['plain']}\tq={stamps['q']}\t{r.stdout.decode().strip()}"


def main():
    pcrec, cases, out = sys.argv[1:4]
    literal = "--literal" in sys.argv
    for ln in open(cases):
        if not ln.strip() or ln.startswith("#"): continue
        cid, enc, ph, qh = ln.rstrip("\n").split("\t")
        pat = bytes.fromhex(ph)
        q = kill(pat) if qh == "auto" else bytes.fromhex(qh)
        if q is None:
            print(f"{cid}\t{enc}\tDECLINED (a \\G inside a lookbehind)", flush=True); continue
        print(case(pcrec, cid, enc, pat, q, os.path.join(out, re.sub(r"[^\w.-]", "_", cid)), literal), flush=True)


if __name__ == "__main__":
    main()
