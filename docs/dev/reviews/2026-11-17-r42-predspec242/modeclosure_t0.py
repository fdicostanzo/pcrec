import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/modeclosure/work")
from eng import *
f = ekey(lambda: W(Pat(r"(?:(?P<h>\d)?;)*"), h5()), ("h",))
print(f("WHOLE", "3;;"), f("SEARCHED", "3;;"), f("FIND-ALL", "3;7; 7;; 3;"))
f = ekey(lambda: W(Pat(r"(?:(?:(?P<h>\d)?;)*,)*"), h5()), ("h",))
print([f("WHOLE", t) for t in ("3;,,", "3;;,", "3;,7;,", "7;,3;,")])
