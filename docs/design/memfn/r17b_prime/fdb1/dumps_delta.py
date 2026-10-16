#!/usr/bin/env python3
"""docs/design/memfn/r17b_prime/fdb1/dumps_delta.py REF_BIN BIN [DECLARED]

emit_sweep's stream 5 (the seven registry dumps) with a DECLARED delta (lane
fdb1, R17-b' B1; r17b_prime.md rev 3 §3.4): every surface byte-identical
between REF_BIN and BIN except the declared one, whose difference must be
exactly the declared rows ADDED inside their section (`#section NAME`
headers, as `--list-axes` prints them), each present once, nothing else moved and no
other line removed. A declared row that did NOT arrive is a failure too (the
delta must be the declaration, in both directions). Exits 1 on any failure.
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
    """The `#section NAME` header above line i (the table_contract.md
    shape), "" before the first."""
    for j in range(i, -1, -1):
        if lines[j].startswith("#section "):
            return lines[j].split()[1]
    return ""


def main():
    ref, cur = sys.argv[1], sys.argv[2]
    decl_path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "dumps_declared_B1.tsv")
    declared = set()
    for ln in open(decl_path):
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
            if op != "insert":
                print("FAIL: %s: a %s hunk (ref lines %d-%d), only additions are declared"
                      % (flag, op, i1 + 1, i2)); bad += 1; continue
            for j in range(j1, j2):
                key = (flag, section_of(lb, j), lb[j].split("\t")[0])
                if key in declared and key not in seen:
                    seen.add(key)
                else:
                    print("FAIL: %s: undeclared added line %r (section %s)"
                          % (flag, lb[j][:80], key[1])); bad += 1
        print("%s: %s differs by %d declared added rows"
              % ("PASS" if not bad else "INFO", flag, sum(1 for k in seen if k[0] == flag)))
    for k in sorted(declared - seen):
        print("FAIL: declared row %s did not arrive" % "/".join(k)); bad += 1
    print("dumps delta: %d surfaces, %d declared rows arrived, %d failures"
          % (len(DUMP_SURFACES), len(seen), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
