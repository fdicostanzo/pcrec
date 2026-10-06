#!/usr/bin/env python3
# lane alphas3: render the two timing passes of alpha_s3.sh and alpha_s3_g1.py
# side by side (run 1 / run 2) as markdown tables. Usage:
#   summarize.py main  out.time1.log out.time2.log
#   summarize.py g1    out.g1time1.log out.g1time2.log
import sys


def rows_main(path):
    out = {}
    for ln in open(path):
        if ln.startswith("#") or ln.startswith("cell"):
            continue
        f = ln.split()
        if len(f) < 9:
            continue
        # cell subject unit base new deny new-base floor verdict
        out[(f[0], f[1])] = dict(base=float(f[3]), new=float(f[4]), deny=float(f[5]),
                                 d=float(f[6]), floor=float(f[7]), v=f[8])
    return out


def rows_g1(path):
    out = {}
    hdr = None
    for ln in open(path):
        if ln.startswith("#"):
            continue
        f = ln.rstrip("\n").split("\t")
        if f[0] == "id":
            hdr = f
            continue
        if hdr is None or len(f) < len(hdr):
            continue
        r = dict(zip(hdr, f))
        out[(r["id"], r["subject"])] = r
    return out


def num(x):
    try:
        return float(x)
    except ValueError:
        return float("nan")


def main_tab(a, b):
    print("| cell | subject | base | new | deny | d r1 | d r2 | floor r1 / r2 | verdict r1 / r2 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for k in a:
        x, y = a[k], b.get(k)
        print("| %s | %s | %.4f | %.4f | %.4f | %+.4f | %s | %.4f / %s | %s / %s |" % (
            k[0], k[1], x["base"], x["new"], x["deny"], x["d"],
            ("%+.4f" % y["d"]) if y else "-", x["floor"], ("%.4f" % y["floor"]) if y else "-",
            x["v"], y["v"] if y else "-"))


def g1_tab(a, b):
    print("| id | kind | nT/nE | subject | base | new | deny | noreq | keep | new-base r1/r2 | new-keep r1/r2 | floor r1/r2 | null(new-noreq) r1/r2 | text== | verdict r1 / r2 |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k in a:
        x, y = a[k], b.get(k)
        def pair(col, fmt="%s"):
            return "%s / %s" % (x[col], y[col] if y else "-")
        print("| %s | %s | %s/%s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s / %s |" % (
            x["id"], x["kind"], x["nT"], x["nE"], x["subject"], x["base"], x["new"], x["deny"], x["noreq"], x["keep"],
            pair("new-base"), pair("new-keep"), pair("floor"), pair("nullband"), x["textsame"],
            x["verdict"], y["verdict"] if y else "-"))


if __name__ == "__main__":
    kind, p1 = sys.argv[1], sys.argv[2]
    p2 = sys.argv[3] if len(sys.argv) > 3 else None
    if kind == "main":
        main_tab(rows_main(p1), rows_main(p2) if p2 else {})
    else:
        g1_tab(rows_g1(p1), rows_g1(p2) if p2 else {})
