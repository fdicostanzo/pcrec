#!/usr/bin/env python3
"""docs/dev/lanes/ic2_movers.py -- lane ic2's zero-mover classifier.

Reads the log of an scripts/emit_sweep.py run (REF = the lane's base built at
abi 90, WORK = the lane) whose mover/asymmetric lists were printed in full,
and says whether every moved or asymmetric row is one the stage-2 change was
allowed to move:

  - an argv/stream row: its pattern holds a callout, `(?C` (module
    `callouts`' artifacts gain the span helpers; a code-c pattern is now a
    module row, so its refusal text changes and the describe modes parse it);
  - a composition row: a tests/code/ file (the `code-header` head line is new);
  - a dumps row: --list-syntax / --list-families (the new code-c row) and
    --list-schema (the new `code-header` line).

Anything else is UNEXPECTED. Prints one line per (stream, kind) and the
trailer `movers: DONE rows=N unexpected=K`; exits 1 when K > 0 or the log
holds no stream at all.
"""
import re
import sys

DUMPS_OK = {"--list-syntax:", "--list-families:", "--list-schema:"}


def main(path):
    stream = mode = None
    rows = {}
    nstreams = 0
    for line in open(path, errors="replace").read().split("\n"):
        m = re.match(r"-- stream: (\S+) --", line)
        if m:
            stream, mode = m.group(1), None
            nstreams += 1
            continue
        if re.match(r"  MOVERS \(", line):
            mode = "movers"
            continue
        if re.match(r"  ASYMMETRIC ROWS \(", line):
            mode = "asymmetric"
            continue
        if re.match(r"  \S", line):
            mode = None
            continue
        if mode and re.match(r"    \S", line):
            key = line.strip()
            if mode == "movers" and not key.endswith(":"):
                continue
            rows.setdefault((stream, mode), []).append(key)
    total = bad = 0
    for (st, md), keys in sorted(rows.items()):
        if st == "dumps":
            off = [k for k in keys if k not in DUMPS_OK]
        elif st == "composition":
            off = [k for k in keys if "/tests/code/" not in k]
        else:
            off = [k for k in keys if "(?C" not in k]
        total += len(keys)
        bad += len(off)
        print(f"{st} {md}: {len(keys)} row(s), {len(off)} unexpected")
        for k in off[:10]:
            print(f"    UNEXPECTED {k[:200]}")
    print(f"movers: DONE rows={total} unexpected={bad if nstreams else 'no-streams'}")
    return 0 if nstreams and bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
