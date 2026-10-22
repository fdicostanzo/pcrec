#!/usr/bin/env python3
"""docs/design/memfn/r17b_prime/b4p/dumps_delta.py REF_BIN BIN [DECLARED]

emit_sweep's stream 5 (the registry dumps, scripts/emit_sweep.py
DUMP_SURFACES) with R17-b' B4''s DECLARED delta (lane b4p), checked BOTH WAYS:
every surface byte-identical between REF_BIN and BIN except the declared rows,
which must be REMOVED from their `#section` (each exactly once) with every
other line kept in order. A declared row that did not leave, an undeclared line
that left, and any ADDED or changed line each fail. Earlier lanes' instruments
(../fdb1, ../b3b) declared additions and changes; B4' declares removals only.
Exits 1 on any failure.
"""
import difflib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "../../../../.."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from emit_sweep import DUMP_SURFACES  # noqa: E402  (the one surface list)


def section_of(lines, i):
    """The `#section NAME` header above line i, "" before the first."""
    for j in range(i, -1, -1):
        if lines[j].startswith("#section "):
            return lines[j].split()[1]
    return ""


def main():
    ref, cur = sys.argv[1], sys.argv[2]
    path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "dumps_declared_B4p.tsv")
    declared = set()
    for ln in open(path):
        if ln.startswith("#") or not ln.strip():
            continue
        declared.add(tuple(ln.rstrip("\n").split("\t")))
    bad, seen = 0, set()
    for flag in DUMP_SURFACES:
        a = subprocess.run([ref, flag], capture_output=True)
        b = subprocess.run([cur, flag], capture_output=True)
        if a.returncode or b.returncode:
            print("FAIL: %s rc %d / %d" % (flag, a.returncode, b.returncode)); bad += 1; continue
        if a.stdout == b.stdout:
            print("PASS: %s byte-identical" % flag); continue
        la = a.stdout.decode().splitlines()
        lb = b.stdout.decode().splitlines()
        sm = difflib.SequenceMatcher(a=la, b=lb, autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal":
                continue
            if op != "delete":
                print("FAIL: %s: a %s hunk (ref lines %d-%d), only removals are declared"
                      % (flag, op, i1 + 1, i2)); bad += 1; continue
            for i in range(i1, i2):
                key = (flag, section_of(la, i), la[i].split("\t")[0])
                if key in declared and key not in seen:
                    seen.add(key)
                else:
                    print("FAIL: %s: undeclared removed line %r (section %s)"
                          % (flag, la[i][:80], key[1])); bad += 1
        print("%s: %s differs by %d declared removed rows"
              % ("PASS" if not bad else "INFO", flag, sum(1 for k in seen if k[0] == flag)))
    for k in sorted(declared - seen):
        print("FAIL: declared row %s did not leave" % "/".join(k)); bad += 1
    print("dumps delta: %d surfaces, %d declared rows left, %d failures"
          % (len(DUMP_SURFACES), len(seen), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
