#!/usr/bin/env python3
"""docs/dev/lanes/s3_evidence/cover_pick_witness.py -- lane s3 trailing checks, item 3(a): the
PAIR arm of tests/codegen/run_encoding_checks.sh's cover_pick reader (the WIP of 36422a84e),
read FROM THE FILE THE SUITE RUNS (the reader's definitions are sliced out of the script's
python heredoc and exec'd, never copied), held to its own job on real artifacts:

    python3 -I cover_pick_witness.py SCRIPT PCREC

Rows, on `(?i)\\bcat\\b` (byte: the C/c pair at +0; utf8: the T/t pair at +2):
  real byte/utf8     one search clause each, its (K, bytes) equal to the stamps' declaration
  normalized         after cover_pick both sides' window statements are byte-identical
  stamp-moved        utf8 with RX_REQ_RUN's offset rewritten @2 -> @0: the pick disagrees
  byte-moved         utf8 with the first stream's byte 84 -> 85: the pick disagrees
  k-split            utf8 with the back-off `-= 2` -> `-= 3`: K is not one number (-1), red
Trailer `== cover_pick witness COMPLETE: rows=6 ok=N`; exit 0 iff N == 6.
"""
import re
import subprocess
import sys

src = open(sys.argv[1]).read()
code = "\n".join(
    [m.group(0) for m in re.finditer(r"^(?:REQBYTE|REQRUN)_STAMP_VAL_RE = .*$", src, re.M)] +
    [src[src.index("COVER_SCAN_RE = re.compile("):src.index("def excise(text, label")]])
ns = {"re": re}
exec(code, ns)
cover_pick, stamped = ns["cover_pick"], ns["cover_pick_stamped"]


def art(enc):
    return subprocess.run([sys.argv[2], "--features", "all", "-p", "rx", "-e", enc, "-o", "-",
                           "--pattern", r"(?i)\bcat\b"], capture_output=True, text=True).stdout


def agrees(t):
    _, picks = cover_pick(t)
    k, want = stamped(t)
    return len(picks) == 1 and picks[0][1] == want and (k is None or picks[0][0] == k), picks, (k, want)


ok = 0
tb, tu = art("byte"), art("utf8")
for name, t, want in (("real byte", tb, True), ("real utf8", tu, True),
                      ("stamp-moved", tu.replace('"434154@2/dfdfdf"', '"434154@0/dfdfdf"'), False),
                      ("byte-moved", tu.replace("rx_mf1_c + 2, 84,", "rx_mf1_c + 2, 85,", 1), False),
                      ("k-split", tu.replace("rx_mf1_c -= 2;", "rx_mf1_c -= 3;", 1), False)):
    got, picks, decl = agrees(t)
    ok += got == want
    print("%-12s want %-5s got %-5s picks %s stamps %s" % (name, want, got, picks, decl))
nb, nu = cover_pick(tb)[0], cover_pick(tu)[0]
wl = [[ln for ln in x.splitlines() if ln.startswith("    scan_position = ({")] for x in (nb, nu)]
same = wl[0] == wl[1] and len(wl[0]) == 1
ok += same
print("normalized   window statements identical after cover_pick: %s" % same)
print("== cover_pick witness COMPLETE: rows=6 ok=%d" % ok)
sys.exit(0 if ok == 6 else 1)
