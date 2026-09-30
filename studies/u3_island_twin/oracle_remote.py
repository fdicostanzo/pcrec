#!/usr/bin/env python3
"""oracle_remote.py CASE -- the same libpcre2 answers as oracle.py, computed on
the 10.46 REFERENCE box by shipping oracle.py + the data over ssh stdin.
Nothing is written on the remote box.  Prints `idx from rc start end` rows to
stdout and the remote library version to stderr.

  usage: oracle_remote.py PATTERN FLAGS > answers.tsv
"""
import base64
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOST = os.environ.get("REF_HOST", "duxevents@100.69.121.107")


def remote_answers(pattern, flags):
    subj = base64.b64encode(open(os.path.join(HERE, "out", "subjects.bin"), "rb").read()).decode()
    cases = base64.b64encode(open(os.path.join(HERE, "out", "cases.tsv"), "rb").read()).decode()
    src = open(os.path.join(HERE, "oracle.py")).read()
    src = src.split('if __name__ == "__main__":')[0]
    payload = src + '''
import base64, sys, tempfile
_subj = base64.b64decode("%s")
_cases = base64.b64decode("%s")
def _subs(b):
    n = struct.unpack_from("<I", b, 0)[0]; p = 4; out = []
    for _ in range(n):
        L = struct.unpack_from("<I", b, p)[0]; p += 4; out.append(b[p:p+L]); p += L
    return out
_lib = load()
sys.stderr.write("#libpcre2 " + version(_lib) + "\\n")
_cs = [tuple(map(int, l.split("\\t"))) for l in _cases.decode().splitlines() if l]
for r in answers(_lib, %r, %r, _subs(_subj), _cs):
    sys.stdout.write("\\t".join(map(str, r)) + "\\n")
''' % (subj, cases, pattern.encode(), flags)
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", HOST, "python3", "-"], input=payload,
                       capture_output=True, text=True, timeout=600)
    if r.returncode:
        raise SystemExit("remote failed: " + r.stderr[-2000:])
    ver = [l for l in r.stderr.splitlines() if l.startswith("#libpcre2")]
    rows = []
    for l in r.stdout.splitlines():
        i, f, rc, s, e = l.split("\t")
        rows.append((int(i), int(f), rc, int(s), int(e)))
    return (ver[0] if ver else "#libpcre2 ?"), rows


if __name__ == "__main__":
    v, rows = remote_answers(sys.argv[1], sys.argv[2])
    print(v, file=sys.stderr)
    for r in rows:
        print("\t".join(map(str, r)))
