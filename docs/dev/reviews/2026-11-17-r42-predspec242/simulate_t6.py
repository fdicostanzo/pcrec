import sys, itertools
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/simulate/wk")
sys.path.insert(1, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/R/tree/docs/dev/lanes/rxmodel_evidence")
from ev import M
import pcre2h
CASES = [
 ("backtracked in pass", r"(?:(?:(?<a>\d)q|\d)r;)*", ["1qr;", "2r;", "3qr;", "4r;"]),
 ("lookahead in pass", r"(?:(?=(?<a>\d)q)?\d.;)*", ["1q;", "2r;", "3q;"]),
 ("atomic+backtrack", r"(?:(?>(?<a>\d)|x)\d?y;)*", ["1y;", "12y;", "x2y;", "xy;"]),
 ("nested 3 deep", r"(?:(?:(?:(?<h>\d)?;)*,)*\.)*", ["3;,.", ",.", ";.", "7;;,.", "."]),
]
for name, pat, items in CASES:
    mk = M(pat); lib = pcre2h.Pcre(pat)
    bad = 0; parts = 0; sd = []; n = 0
    for L in range(0, 5):
        for tup in itertools.product(items, repeat=L):
            s = "".join(tup)
            st = next(mk.paths(s, 0, len(s)), None)
            r = lib.match(s, 0, pcre2h.PCRE2_ANCHORED | pcre2h.PCRE2_ENDANCHORED)
            if (st is None) != (r is None): bad += 1; continue
            if st is None: continue
            n += 1
            for nm in mk.P.names:
                c = mk.cap(st, nm); lc = r[2].get(nm)
                if c != lc: bad += 1
                lb = mk.lab(st, nm)
                if lb != lc:
                    parts += 1
                    if lb is not None: sd.append((s, nm, lb, lc))
    print("%-22s %-36s texts %4d | capture mismatches vs libpcre2 %d | label != capture %d, label SET among them %d %s" % (name, pat, n, bad, parts, len(sd), sd[:2]))
