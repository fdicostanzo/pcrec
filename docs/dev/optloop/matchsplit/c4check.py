#!/usr/bin/env python3
"""C4 planted classes: every planted pattern must land in its expected mix label and carry the
expected flag (dead / look / ml / red:K).  Exit 1 on any miss.  Usage: c4check.py ms_rows.tsv.gz"""
import csv, gzip, sys
csv.field_size_limit(sys.maxsize)
bad = 0; n = 0
for r in csv.DictReader(gzip.open(sys.argv[1], "rt"), delimiter="\t"):
    if r["pop"] != "planted":
        continue
    n += 1
    pat = bytes.fromhex(r["pattern_hex"]).decode("latin-1")
    ok = r["mix"] == r["expect"]
    fl = r["expect_flags"]
    why = ""
    if "dead" in fl and not int(r["dead"] or 0): ok = False; why += " no-dead-flag"
    if "look" in fl and not r["look_pin"]: ok = False; why += " no-look-flag"
    if "ml" in fl and not int(r["ml_landmark"] or 0): ok = False; why += " no-ml-flag"
    if "red:S" in fl and "S:all" not in r["red"]: ok = False; why += " no-redundant-S(" + r["red"] + ")"
    print(("ok  " if ok else "FAIL"), "%-6s expect %-6s got %-6s %s%s" % (r["id"], r["expect"], r["mix"], pat, why))
    bad += not ok
print("c4: %d planted, %d wrong" % (n, bad))
sys.exit(1 if bad else 0)
