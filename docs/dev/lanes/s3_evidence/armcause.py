#!/usr/bin/env python3
"""docs/dev/lanes/s3_evidence/armcause.py -- job 600's sweep_start reds, cause by pattern.

    python3 -I armcause.py --bin BIN --tree DIR [--jobs N] [--out FILE]

For each emit_sweep DIFFER_PINS arm job 600 read short (ARMS below), over every distinct corpus
pattern (emit_sweep's own enumeration), compiles BASE and BASE+FLAG on the c-default stream twice:
at the default build and under the cover row's deny `--memfn=no-window-search` (the build before S3 but
for the abi digits). Per arm it prints the DIFFER and start-STAMP counts on both builds, the
LEAVERS (differ under the deny, not by default) and how many of them are default-cover patterns
(BASE's default artifact stamps RX_DFA_SCAN "cover"), the JOINERS (the reverse), and the shortest
default movers that are NOT cover (the candidates for a re-chosen manifest, eight shortest). The cause "S3 routes N fixed-width
patterns to cover" holds for an arm iff every leaver is cover and there is no joiner.
"""
import argparse
import concurrent.futures
import os
import sys

ARMS = [("byte", "-fno-offset-skip"), ("byte", "-fno-run-prefilter"), ("byte", "-fno-start-set"),
        ("byte", "-fno-req-handoff"), ("byte", "-fno-req-run"), ("byte", "-fno-req-run-fold"),
        ("byte", "-fmemfn-simd"), ("utf8", "-fno-offset-skip"), ("utf8", "-fno-run-prefilter"),
        ("utf8", "-fno-start-set"), ("utf8", "-fno-req-handoff"), ("utf8", "-fno-req-run"),
        ("utf8", "-fno-req-run-fold"), ("utf8", "-fmemfn-simd"),
        ("byte", "--memfn=no-pres-set-lead"), ("utf8", "--memfn=no-pres-set-lead"),
        ("byte", "--memfn=no-fd-pres-g1"), ("utf8", "--memfn=no-fd-pres-g1"),
        ("byte", "--memfn=no-fd-pres-pick"), ("utf8", "--memfn=no-fd-pres-pick")]
DENY = "--memfn=no-window-search"


def merged(flags, deny):
    """FLAGS plus DENY with every --memfn= folded into ONE list: the CLI's last --memfn= wins."""
    rows = [f[len("--memfn="):] for f in flags + deny if f.startswith("--memfn=")]
    rest = [f for f in flags + deny if not f.startswith("--memfn=")]
    return rest + (["--memfn=" + ",".join(rows)] if rows else [])
COVER = b'#define RX_DFA_SCAN "cover"'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--jobs", type=int, default=16)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(a.tree, "scripts"))
    import emit_sweep as es  # noqa: E402
    pats = sorted(set(p for _, _, p in es.enumerate_corpus(a.bin, a.tree, 60)))

    def c(p, args):
        ok, out, _ = es.compile_stream_c(a.bin, p, 60, extra=args)
        return out if ok else None

    def job(p):
        res, memo = [], {}

        def cb(args):
            k = tuple(args)
            if k not in memo:
                memo[k] = c(p, args)
            return memo[k]
        for base, flag in ARMS:
            bargs = list(es.ARM_BASES[base])
            row = []
            for deny in ([], [DENY]):
                b0 = cb(bargs + deny)
                b1 = c(p, bargs + merged(flag.split(), deny))
                differ = b0 is not None and b1 is not None and b0 != b1
                stamp = differ and bool(es.start_keys_moved(es.stamps_of(b0), es.stamps_of(b1)))
                row.append((differ, stamp, b0 is not None and COVER in b0))
            res.append(row)
        return p, res

    t = {k: {"d": 0, "s": 0, "od": 0, "os": 0, "leave": 0, "leave_cover": 0, "join": 0,
             "sleave": 0, "sleave_cover": 0, "sjoin": 0, "man": []} for k in ARMS}
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for p, res in ex.map(job, pats, chunksize=4):
            for k, ((d, s, cov), (od, os_, _)) in zip(ARMS, res):
                r = t[k]
                r["d"] += d; r["s"] += s; r["od"] += od; r["os"] += os_
                if od and not d:
                    r["leave"] += 1; r["leave_cover"] += cov
                if d and not od:
                    r["join"] += 1
                if os_ and not s:
                    r["sleave"] += 1; r["sleave_cover"] += cov
                if s and not os_:
                    r["sjoin"] += 1
                if d and not cov:
                    r["man"] = sorted(r["man"] + [(len(p), p)])[:8]
    lines = ["#base\tflag\tdiffer\tstamp\tdiffer_deny\tstamp_deny\tleavers\tleavers_cover\tjoiners"
             "\tstamp_leavers\tstamp_leavers_cover\tstamp_joiners\tnoncover_movers\tcause_holds"]
    for k in ARMS:
        r = t[k]
        holds = (r["leave"] == r["leave_cover"] and r["join"] == 0
                 and r["sleave"] == r["sleave_cover"] and r["sjoin"] == 0)
        lines.append("\t".join(str(x) for x in (k[0], k[1], r["d"], r["s"], r["od"], r["os"],
                                                  r["leave"], r["leave_cover"], r["join"],
                                                  r["sleave"], r["sleave_cover"], r["sjoin"],
                                                  " ".join(es.encode_escape(m) for _, m in r["man"]) or "-",
                                                  "yes" if holds else "NO")))
    text = "\n".join(lines) + "\n"
    sys.stdout.write(text)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
    print("== armcause COMPLETE: patterns=%d arms=%d" % (len(pats), len(ARMS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
