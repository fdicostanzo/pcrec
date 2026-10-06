#!/usr/bin/env python3
# lane alphas3: the hat's set T and its density d (fraction of subject bytes in
# T) for every mover cell alpha_s3_g1.py built, per subject. The F3 reading
# (startset.md §4.4) is that the re-seed's cost is least amortized where d is
# high, so the regressing movers should be the dense ones. Run on the box after
# `alpha_s3_g1.py build`: S2A=<work dir> python3 alpha_s3_density.py > density.tsv
import os, re, sys
S2A = os.environ.get("S2A", "/tmp/s3alpha_startset")
os.chdir(S2A)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("S2A", S2A)
import alpha_s3_g1 as g  # noqa: E402  (cells(), subj_path(), table_count())


def tset(text):
    m = re.search(r'static const unsigned char rx_start_bytes\[256\] = \{\n((?:.*\n)*?)\s*\};', text)
    if m:
        v = [int(x) for x in re.findall(r"\d+", m.group(1))]
        if len(v) == 256:
            return {b for b in range(256) if v[b]}
    m = re.search(r'memchr\(subject \+ scan_position, (\d+), ', text)
    return {int(m.group(1))} if m else None


print("id\tsubject\tnT\tn_subject\td_T")
for c in g.cells():
    t = tset(open("g1/art/%s/new/art.c" % c["key"], encoding="latin-1").read())
    for s in c["subjects"]:
        data = open(g.subj_path(s), "rb").read()
        cnt = sum(1 for b in data if t is not None and b in t)
        print("%s\t%s\t%s\t%d\t%.5f" % (c["id"], s, len(t) if t is not None else "-", len(data),
                                       cnt / len(data) if data else 0))
