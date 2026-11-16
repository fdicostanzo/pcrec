import sys
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec20/simulate")
from eng import pc, VER, DIS, PROBES
print(VER)
P = r"(?(DEFINE)(?<o>\d{1,3}))(?&o)\.(?&o)"
for s in ["1.2", "192.168", "1234.5", "a.b"]:
    print(repr(s), pc(P, s, ["o"], pyok=False))
