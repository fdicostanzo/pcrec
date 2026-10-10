#!/usr/bin/env python3
"""tests/revend/verify_stage2.py -- re-check tests/revend/stage2_captures.rxt
against libpcre2, INDEPENDENTLY of gen_stage2.py: it reads the WRITTEN file
(its own small parser for the restricted vocabulary the generator emits:
pattern / flags / encoding / features / m n ms ns / g) and re-asks the oracle
every question, whole-match span AND every group slot. Nothing is imported
from the generator, so a transcription fault between table and file shows.

Usage: verify_stage2.py ORACLE_BIN SCRATCH_DIR [FILE]
ORACLE_BIN is tests/fuzz/pcre2_oracle.c built against libpcre2-8 (compiles at
options=0; `flags i` / `flags u` / `encoding utf8` are carried as a (?i) /
(*UCP) / (*UTF) prefix on the pattern text). Exit 0 = every cell agrees."""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))

def unesc(s):
    out = bytearray()
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            n = s[i + 1]
            if n == "x":
                out.append(int(s[i + 2:i + 4], 16)); i += 4; continue
            out += {"n": b"\n", "t": b"\t", "r": b"\r", '"': b'"', "\\": b"\\"}[n]
            i += 2
        else:
            out += c.encode(); i += 1
    return bytes(out)

def ask(binp, scratch, pre, pat, subj, sp):
    f = os.path.join(scratch, "vsubj")
    open(f, "wb").write(subj)
    r = subprocess.run([binp, pre + pat, f, str(sp)], capture_output=True, timeout=60)
    return r.stdout.decode().split()

def main():
    binp, scratch = sys.argv[1:3]
    path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "stage2_captures.rxt")
    os.makedirs(scratch, exist_ok=True)
    pat = None; i = u = utf8 = False
    cur = None; npass = nfail = 0; ngroups = 0
    def fail(ln, msg):
        nonlocal nfail
        nfail += 1
        print("FAIL %s:%d: %s" % (path, ln, msg))
    for ln, line in enumerate(open(path, encoding="utf-8").read().split("\n"), 1):
        if line.startswith("pattern "):
            pat = line[8:]; i = u = utf8 = False; cur = None
        elif line.startswith("flags "):
            i = "i" in line[6:]; u = "u" in line[6:]
        elif line.startswith("encoding "):
            utf8 = line.split()[1] == "utf8"
        elif line.startswith(("m ", "n ", "ms ", "ns ")):
            kind, rest = line.split(" ", 1)
            sp = 0
            if kind in ("ms", "ns"):
                sp, rest = rest.split(" ", 1); sp = int(sp)
            m = re.match(r'"((?:[^"\\]|\\.)*)"(.*)$', rest)
            subj = unesc(m.group(1)); tail = m.group(2).split()
            pre = ("(*UTF)" if utf8 else "") + ("(*UCP)" if u else "") + ("(?i)" if i else "")
            ans = ask(binp, scratch, pre, pat, subj, sp)
            if kind[0] == "n":
                cur = None
                if ans == ["nomatch"]: npass += 1
                else: fail(ln, "file says nomatch, libpcre2 says %s" % " ".join(ans))
            else:
                want = list(map(int, tail))
                if ans[:1] == ["match"] and list(map(int, ans[1:3])) == want:
                    npass += 1; cur = list(map(int, ans[1:]))
                else:
                    cur = None; fail(ln, "file says %s, libpcre2 says %s" % (want, " ".join(ans)))
        elif line.startswith("g "):
            _, k, s, e = line.split()
            k = int(k)
            if cur is None or 2 * k + 1 >= len(cur) or [cur[2 * k], cur[2 * k + 1]] != [int(s), int(e)]:
                fail(ln, "group %s %s %s disagrees with libpcre2 (%s)" % (k, s, e, cur))
            else:
                ngroups += 1
    print("verify_stage2: %d cells agree, %d group slots agree, %d FAIL" % (npass, ngroups, nfail))
    sys.exit(1 if nfail else 0)

main()
