"""gen_acc.py OUT [LINES] : the subst set's access-log stream prefix (bench/subst/logsim.py, read-only import);
the first LINES lines (default 17,500 = acc-small, whose sha256 the manifest pins)."""
import sys, hashlib
sys.path.insert(0, '/home/pcrec/projects/pcrec-bench/bench/subst')
import logsim
n = int(sys.argv[2]) if len(sys.argv) > 2 else 17500
h = hashlib.sha256()
with open(sys.argv[1], 'wb') as f:
    for line in logsim.stream(n, logsim.Planted()):
        f.write(line); h.update(line)
print(h.hexdigest())
