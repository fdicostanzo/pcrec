#!/usr/bin/env python3
"""docs/design/memfn/r17b_prime/b3b/dumps_delta.py REF_BIN BIN [DECLARED]

emit_sweep's stream 5 (the registry dumps, scripts/emit_sweep.py
DUMP_SURFACES) with R17-b' B3b's DECLARED delta (lane b3b; r17b_prime.md rev
3 §3.1 row B3b, §3.4): every surface byte-identical between REF_BIN and BIN
except the declared lines, checked BOTH WAYS. fdb1's dumps_delta.py held
additions only; B3b also CHANGES two axis-table rows (`req-admit`'s
`dominated` and `set-leads`, re-sourced to the memfn kit's PRES rows), so a
row of the axis table (the lines before the first `#section`) is keyed by
(axis, candidate) and compared CELL BY CELL against the columns its
declaration names, and a `#section` adds rows only. A declared line that did
not move, an undeclared cell or line that did, a reordered or removed row:
each fails. Exits 1 on any failure.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "../../../../.."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from emit_sweep import DUMP_SURFACES  # noqa: E402  (the one surface list)


def split(text):
    """(header, {(axis, cand): cells}, [axis keys in order], {section: [lines]})"""
    head, rows, order, secs, cur = None, {}, [], {}, None
    for ln in text.splitlines():
        if ln.startswith("#section "):
            cur = ln.split()[1]
            secs[cur] = []
            continue
        if cur is not None:
            secs[cur].append(ln)
            continue
        if ln.startswith("#"):
            head = ln.lstrip("#").split("\t")
            continue
        c = ln.split("\t")
        k = (c[0], c[2]) if len(c) > 2 else (ln, "")
        rows[k] = c
        order.append(k)
    return head, rows, order, secs


def main():
    ref, cur = sys.argv[1], sys.argv[2]
    path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "dumps_declared_B3b.tsv")
    adds, changes = set(), {}
    for ln in open(path):
        if ln.startswith("#") or not ln.strip():
            continue
        surf, sec, kind, key, cols = ln.rstrip("\n").split("\t")
        if kind == "add":
            adds.add((surf, sec, key))
        else:
            a, c = key.split("/", 1)
            changes[(surf, a, c)] = set(cols.split(","))
    bad, seen_add, seen_ch = 0, set(), set()
    for flag in DUMP_SURFACES:
        a = subprocess.run([ref, flag], capture_output=True)
        b = subprocess.run([cur, flag], capture_output=True)
        if a.returncode or b.returncode:
            print("FAIL: %s rc %d / %d" % (flag, a.returncode, b.returncode)); bad += 1; continue
        if a.stdout == b.stdout:
            print("PASS: %s byte-identical" % flag); continue
        ha, ra, oa, sa = split(a.stdout.decode())
        hb, rb, ob, sb = split(b.stdout.decode())
        if ha != hb or oa != ob:
            print("FAIL: %s: the axis table's header or row order moved" % flag); bad += 1
        for k in oa:
            if k not in rb:
                continue
            diff = {ha[i] for i in range(min(len(ra[k]), len(rb[k]))) if ra[k][i] != rb[k][i]}
            if len(ra[k]) != len(rb[k]):
                diff.add("(column count)")
            if not diff:
                continue
            want = changes.get((flag, k[0], k[1]))
            if want is None or diff != want:
                print("FAIL: %s: row %s/%s changed %s, declared %s"
                      % (flag, k[0], k[1], sorted(diff), sorted(want) if want else "nothing"))
                bad += 1
            else:
                seen_ch.add((flag, k[0], k[1]))
        if sorted(sa) != sorted(sb):
            print("FAIL: %s: the section set moved (%s -> %s)" % (flag, sorted(sa), sorted(sb))); bad += 1
        for sec in sa:
            la, lb = sa[sec], sb.get(sec, [])
            if [x for x in lb if x in la] != la:
                print("FAIL: %s: section %s lost or reordered a line" % (flag, sec)); bad += 1
            for x in lb:
                if x in la:
                    continue
                key = (flag, sec, x.split("\t")[0])
                if key in adds and key not in seen_add:
                    seen_add.add(key)
                else:
                    print("FAIL: %s: section %s: undeclared added line %r" % (flag, sec, x[:80])); bad += 1
        print("%s: %s: %d declared rows added, %d declared rows changed"
              % ("PASS" if not bad else "INFO", flag,
                 sum(1 for k in seen_add if k[0] == flag), sum(1 for k in seen_ch if k[0] == flag)))
    for k in sorted(adds - seen_add):
        print("FAIL: declared added row %s did not arrive" % "/".join(k)); bad += 1
    for k in sorted(set(changes) - seen_ch):
        print("FAIL: declared changed row %s did not change" % "/".join(k)); bad += 1
    print("dumps delta: %d surfaces, %d added + %d changed declared rows moved, %d failures"
          % (len(DUMP_SURFACES), len(seen_add), len(seen_ch), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
