import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/modeclosure")
from mc_lib import *
W, Pat, C, OCC, AND, ZERO = (g(k) for k in ("W", "Pat", "C", "OCC", "AND", "ZERO"))
strings = g("strings")
pool = strings("12 x", 5)
B = re.compile(r"1\d*")
# what PCRE calls the whole match at a callout inside the occurrences loop: start_match .. current position
CO = {"z": lambda c: B.fullmatch(c.stretch()) is not None,
      "zh": lambda c: B.fullmatch(c.get("hh") or "\x00") is not None}
print("Z1 `occurrences(/\\d+/ & B, min=1)` (engine, hit-local &) vs the same with `(0: B)` read as PCRE's group 0 (match start .. here):",
      cmp(enkey(lambda: OCC(AND(Pat(r"\d+"), Pat(r"1\d*")), 1), ()), rxkey(r'(?:[\s\S]*?\d+(?C"z"))+[\s\S]*', CO, ()), pool))
print("Z2 control: the hit-local reading as a regex model (the hit captured, the callout reads it):",
      cmp(enkey(lambda: OCC(AND(Pat(r"\d+"), Pat(r"1\d*")), 1), ()), rxkey(r'(?:[\s\S]*?(?<hh>\d+)(?C"zh"))+[\s\S]*', CO, ()), pool))
