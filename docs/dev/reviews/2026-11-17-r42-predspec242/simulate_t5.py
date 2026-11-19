import sys, itertools
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/simulate/wk")
sys.path.insert(1, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/R/tree/docs/dev/lanes/rxmodel_evidence")
from ev import M
import pcre2h
CASES = [
 ("backtracked in pass", r"(?:(?:(?<a>\d)q|\d)r;)*", "1qr;2r;3"),
 ("lookahead in pass", r"(?:(?=(?<a>\d\d))\d;)*", "12;"),
 ("neg lookahead in pass", r"(?:(?!(?<a>1))\d;)*", "12;"),
 ("atomic in pass", r"(?:(?>(?<a>\d)?)\d?;)*", "12;"),
 ("ub1 in loop (REP)", r"(?:(?<h>\d)?;)*", "37;"),
 ("{0,2}", r"(?:(?<h>\d)?;){0,2}", "37;"),
 ("{2}", r"(?:(?<h>\d)?;){2}", "37;"),
 ("{2,3}", r"(?:(?<h>\d)?;){2,3}", "37;"),
 ("nested", r"(?:(?:(?<h>\d)?;)*,)*", "37;,"),
 ("branch reset", r"(?:(?|(?<a>\d)x|y(?<a>\d)|z))*", "xyz"),
 ("lazy loop", r"(?:(?<h>\d)?;)*?", "37;"),
 ("alt in loop", r"(?:(?<a>\d)|(?<b>[a-z]))*", "3q"),
 ("two groups one optional", r"(?:(?<h>\d)(?<m>:\d)?,)*", "3:,"),
 ("nested optional loop", r"(?:(?<h>\d)(?:-(?<k>\d))*,)*", "3-,"),
]
tot = 0
for name, pat, alpha in CASES:
    mk = M(pat); lib = pcre2h.Pcre(pat)
    bad_cap = []; parts = 0; set_differ = []; n = 0
    for L in range(0, 6):
        for tup in itertools.product(alpha, repeat=L):
            s = "".join(tup)
            st = next(mk.paths(s, 0, len(s)), None)
            r = lib.match(s, 0, pcre2h.PCRE2_ANCHORED | pcre2h.PCRE2_ENDANCHORED)
            if (st is None) != (r is None): bad_cap.append((s, "holds", st is not None, r is not None)); continue
            if st is None: continue
            n += 1
            for nm in mk.P.names:
                c = mk.cap(st, nm); lc = r[2].get(nm)
                if c != lc: bad_cap.append((s, nm, c, lc))
                lb = mk.lab(st, nm)
                if lb != lc:
                    parts += 1
                    if lb is not None: set_differ.append((s, nm, lb, lc))
    tot += n
    print("%-24s %-34s texts matched %4d | my capture vs libpcre2 mismatches %d %s | label != capture %d, of which label SET %d %s" % (
        name, pat, n, len(bad_cap), bad_cap[:2], parts, len(set_differ), set_differ[:2]))
print("total matched texts", tot)
