#!/usr/bin/env python3
"""Per-function static instruction counts of an object (objdump -d).  Usage: fn_counts.py X.o [...]"""
import subprocess, sys, re
for o in sys.argv[1:]:
    d = subprocess.run(["objdump", "-d", "--no-show-raw-insn", o], capture_output=True, text=True).stdout
    cur = None; cnt = {}
    for l in d.splitlines():
        m = re.match(r"[0-9a-f]+ <(.+)>:", l)
        if m: cur = m.group(1); cnt[cur] = 0; continue
        if cur and re.match(r"\s+[0-9a-f]+:", l): cnt[cur] += 1
    print(o, "total", sum(cnt.values()))
    for k, v in sorted(cnt.items(), key=lambda x: -x[1]): print("  %-28s %d" % (k, v))
