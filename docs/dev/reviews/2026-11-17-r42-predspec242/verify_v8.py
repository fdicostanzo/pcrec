import sys, re
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/R/tree/docs/dev/lanes/rxmodel_evidence")
import pcre2h as P
num = lambda v: v is not None and re.fullmatch(r"0|[1-9]\d*", v) is not None
late = lambda h, m: num(h) and num(m) and (int(h), int(m)) >= (9, 30)
for hour in (r"\d{1,2}", r"\d", r"\d+"):
    T = r"(?<h>%s)(?::(?<m>\d\d))?" % hour
    for nm, pat in (("plain", T + '(?C"t")'), ("atomic", "(?>" + T + ')(?C"t")'), ("PRUNE", T + '(*PRUNE)(?C"t")'),
                    ("SKIP", T + '(*SKIP)(?C"t")'), ("COMMIT", T + '(*COMMIT)(?C"t")')):
        rx = P.Pcre(pat, {"t": lambda c: not late(c.get("h"), c.get("m"))})
        print("hour %-8s %-6s" % (hour, nm), " ; ".join("`%s` %s" % (t, ["`%s`@%d" % (t[a:b], a) for a, b, _ in rx.findall(t)]) for t in ("9:30", "9:30 8:15", "8:15 9:30 7:00")))
