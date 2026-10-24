#!/usr/bin/env python3
"""docs/dev/lanes/cfcount/census.py -- lane cfcount's MOVER + SIZE CENSUS for
lane/corefix's abi event 82 -> 87 (rulings R1 and R3 in corefix_rulings.md):
every corpus artifact that moves between main and the lane is attributed to
K128, K129 or the counter fix (`vm_counter_fits` keeps `X+` off the counter
rung at K=1), and every artifact's size is compared.

    python3 -I census.py --base BIN --mid BIN --new BIN --tree DIR --out FILE [--jobs N]

BASE is main a53296894's pcrec, MID the lane before the counter fix
(e18de0412: K128 + K129 only), NEW the lane with it. Over every distinct
corpus pattern (scripts/emit_sweep.py's enumeration), seven arms: the .c at
the default engine, under -e utf8 and at --engine=vm, the VM listing
(--emit-ir), the facts listing, and the .c and listing at --engine=vm
--unroll=1 (the counter fix's own K). abi digits are mapped 87 -> 82 before
comparing; rc and stderr are compared too.

ATTRIBUTION, per arm, in two steps (no mover is diffed by hand):
  BASE -> MID is corefix's: allowed only for a K128 or K129 pattern, classed
    exactly as corefix/census.py does (from MID's listing and .c).
  MID -> NEW is the counter fix's: allowed only for a CFC pattern on an arm
    built at K=1. CFC = MID's `--unroll=1` listing has a counter-rung row for
    an unbounded `{1,}` (the shape the fix takes off the rung); an arm is at
    K=1 when it is a k1 arm or when MID's or NEW's default .c stamps
    RX_UNROLL_K 1 (the size term chose it).
  Anything else that moves is UNEXPECTED, and so is a CFC pattern whose k1 .c
  did NOT move MID -> NEW (the fix did not reach it).

SIZE: the .c bytes of the three default arms, BASE vs NEW and MID vs NEW;
every growth above 2% is listed (`grow` rows), as is every growth above 10%
from the counter fix alone (MID -> NEW; the lane's stop rule).

Trailer: `== cfcount census COMPLETE: patterns=P compiles=C movers=M
unexpected=U grow2=G stop10=S`; exit 0 iff U == 0 and S == 0.
"""
import argparse
import concurrent.futures
import os
import re
import subprocess
import sys

ABI = [(b"(abi 87)", b"(abi 82)"), (b"(PCREC_RX_ABI_H + 0) != 87", b"(PCREC_RX_ABI_H + 0) != 82"),
       (b"#define PCREC_RX_ABI_H 87", b"#define PCREC_RX_ABI_H 82"), (b"    .abi = 87,", b"    .abi = 82,")]
K128_MARK = b"the last mandatory iteration: record where it began"
K129_MARK = b"_vars_resolve("
CFC_ROW = re.compile(rb"^L\d+\tcounter\tcounter rung, \{1,\}, ", re.M)
K1_STAMP = b"\n#define RX_UNROLL_K 1\n"

ARMS = [
    ("c-default", ["-p", "rx", "--features", "all", "-o", "-"]),
    ("c-utf8", ["-p", "rx", "--features", "all", "-e", "utf8", "-o", "-"]),
    ("c-vm", ["-p", "rx", "--features", "all", "--engine=vm", "-o", "-"]),
    ("ir", ["--features", "all", "--engine=vm", "--emit-ir"]),
    ("facts", ["--features", "all", "--emit-facts=byte,utf8"]),
    ("c-vm-k1", ["-p", "rx", "--features", "all", "--engine=vm", "--unroll=1", "-o", "-"]),
    ("ir-k1", ["--features", "all", "--engine=vm", "--unroll=1", "--emit-ir"]),
]
SIZED = ("c-default", "c-utf8", "c-vm")


def norm(out):
    for a, b in ABI:
        out = out.replace(a, b)
    return out


def run(argv, timeout=60):
    try:
        r = subprocess.run(argv, capture_output=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -9, b"", b"TIMEOUT"


def first_diff(a, b):
    la, lb = a.split(b"\n"), b.split(b"\n")
    for i in range(max(len(la), len(lb))):
        x = la[i] if i < len(la) else b"<eof>"
        y = lb[i] if i < len(lb) else b"<eof>"
        if x != y:
            return "line %d: a=%r b=%r" % (i + 1, x[:100], y[:100])
    return ""


def differ(x, y):
    """What moved between two (rc, out, err) results, '' if nothing."""
    what = []
    if x[0] != y[0]:
        what.append("rc %d->%d" % (x[0], y[0]))
    if norm(x[1]) != norm(y[1]):
        what.append("bytes " + first_diff(norm(x[1]), norm(y[1])))
    if norm(x[2]) != norm(y[2]):
        what.append("stderr " + first_diff(norm(x[2]), norm(y[2])))
    return "; ".join(what)


def one(task):
    base, mid, new, pat = task
    res = {}
    for arm, flags in ARMS:
        res[arm] = tuple(run([b] + flags + ["--pattern", pat]) for b in (base, mid, new))
    m_ir, m_cvm, m_irk1 = res["ir"][1][1], res["c-vm"][1][1], res["ir-k1"][1][1]
    cls = "K128" if K128_MARK in m_ir else "K129" if K129_MARK in m_cvm else "other"
    cfc = bool(CFC_ROW.search(m_irk1))
    k1_default = any(K1_STAMP in res[a][i][1] for a in SIZED for i in (1, 2))
    rows, unexpected = [], []
    for arm, _ in ARMS:
        b, m, n = res[arm]
        d1, d2 = differ(b, m), differ(m, n)
        if d1:
            rows.append((cls, arm, "base->mid", d1))
            if cls == "other":
                unexpected.append((cls, arm, "base->mid", d1))
        if d2:
            at_k1 = arm.endswith("-k1") or k1_default
            tag = "CFC" if cfc and at_k1 else "other"
            rows.append((tag, arm, "mid->new", d2))
            if tag == "other":
                unexpected.append((tag, arm, "mid->new", d2))
    if cfc and not differ(res["c-vm-k1"][1], res["c-vm-k1"][2]):
        unexpected.append(("CFC", "c-vm-k1", "mid->new", "CFC shape did NOT move"))
    sizes = {arm: tuple(len(r[1]) if r[0] == 0 else None for r in res[arm]) for arm in SIZED}
    return pat, cls, cfc, k1_default, rows, unexpected, sizes


def pct(a, b):
    return 100.0 * (b - a) / a if a else 0.0


def main():
    ap = argparse.ArgumentParser()
    for k in ("base", "mid", "new", "tree", "out"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(a.tree, "scripts"))
    import emit_sweep  # noqa: E402  (the corpus enumeration, one implementation)
    corpus = emit_sweep.enumerate_corpus(a.new, a.tree, 60)
    pats = sorted(set(p for _, _, p in corpus))
    if a.limit:
        pats = pats[:a.limit]
    tally, unexpected, rows, grow, stop = {}, [], [], [], []
    tot = {arm: [0, 0, 0] for arm in SIZED}
    ncfc = nk1 = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for pat, cls, cfc, k1d, r, u, sizes in ex.map(
                one, [(a.base, a.mid, a.new, p) for p in pats], chunksize=8):
            ep = emit_sweep.encode_escape(pat)
            ncfc += cfc
            nk1 += k1d
            tally.setdefault(cls, {"patterns": 0})["patterns"] += 1
            for tag, arm, step, what in r:
                key = "%s %s" % (tag, step)
                tally.setdefault(key, {})
                tally[key][arm] = tally[key].get(arm, 0) + 1
                rows.append((tag, arm, step, ep, what))
            unexpected += [(t, arm, s, ep, w) for t, arm, s, w in u]
            for arm, (sb, sm, sn) in sizes.items():
                if None in (sb, sm, sn):
                    continue
                for i, v in enumerate((sb, sm, sn)):
                    tot[arm][i] += v
                if pct(sb, sn) > 2.0:
                    grow.append(("grow", arm, "base->new %+.2f%% (%d->%d)" % (pct(sb, sn), sb, sn), ep))
                if pct(sm, sn) > 2.0:
                    grow.append(("grow", arm, "mid->new %+.2f%% (%d->%d)" % (pct(sm, sn), sm, sn), ep))
                if pct(sm, sn) > 10.0:
                    stop.append(("STOP", arm, "mid->new %+.2f%% (%d->%d)" % (pct(sm, sn), sm, sn), ep))
    with open(a.out, "w", encoding="utf-8", errors="backslashreplace") as f:
        f.write("# cfcount census: base=%s mid=%s new=%s patterns=%d\n#tag\tarm\tstep\tpattern\tmoved\n"
                % (a.base, a.mid, a.new, len(pats)))
        for r in unexpected + stop + rows:
            f.write("\t".join(x.replace("\t", "\\t").replace("\n", "\\n") for x in r) + "\n")
        for g in grow:
            f.write("\t".join(x.replace("\t", "\\t").replace("\n", "\\n") for x in g) + "\n")
    print("census: corpus rows %d, distinct patterns %d; CFC shape %d; default-K=1 artifacts %d"
          % (len(corpus), len(pats), ncfc, nk1))
    for cls in ("K128", "K129", "other"):
        print("  class %-5s patterns %5d" % (cls, tally.get(cls, {"patterns": 0})["patterns"]))
    for key in sorted(k for k in tally if " " in k):
        print("  movers %-16s %s" % (key, "  ".join("%s=%d" % (arm, tally[key].get(arm, 0))
                                                      for arm, _ in ARMS)))
    for arm in SIZED:
        b, m, n = tot[arm]
        print("  size %-9s base %d  mid %d  new %d  (base->new %+.3f%%, mid->new %+.3f%%)"
              % (arm, b, m, n, pct(b, n), pct(m, n)))
    for g in grow:
        print("  GROW>2%% %s %s: %s" % (g[1], g[2], g[3]))
    for s in stop:
        print("  STOP>10%% %s %s: %s" % (s[1], s[2], s[3]))
    for u in unexpected[:20]:
        print("  UNEXPECTED %s %s %s %s: %s" % u)
    print("== cfcount census COMPLETE: patterns=%d compiles=%d movers=%d unexpected=%d grow2=%d stop10=%d"
          % (len(pats), 3 * len(pats) * len(ARMS), len(rows), len(unexpected), len(grow), len(stop)))
    return 0 if not unexpected and not stop else 1


if __name__ == "__main__":
    sys.exit(main())
