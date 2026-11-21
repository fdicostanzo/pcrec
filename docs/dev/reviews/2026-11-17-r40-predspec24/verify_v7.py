import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/verify")
from vlib import *
LP_ = r"(?:(?P<h>\d+)(?::(?P<m>\d\d))?,)*"
J = lambda: C(("h", "m"), lambda h, m: num(h) and num(m) and (int(h), int(m)) == (10, 45))
prog = lambda: W(Pat(LP_), J())
co = {"j": lambda c: num(c.get("h")) and num(c.get("m")) and (int(c.get("h")), int(c.get("m"))) == (10, 45)}
rx = P.Pcre(r'(?:(?<h>\d+)(?::(?<m>\d\d))?,)*(?C"j")', co)
for t in ("9:45,10,", "10,9:45,", "10:45,"):
    print(repr(t), "engine rev24", eng(prog, ("h", "m"))("WHOLE", t), "| engine rev23.2 (per pass)", eng(prog, ("h", "m"), "23.2")("WHOLE", t) is not None,
          "| PCRE2", rx.whole(t))
