#!/usr/bin/env python3
"""mk_inputs.py OUTDIR [BENCH_ROOT] -- the two inputs the wafread twins need.

  OUTDIR/match.bin  t-64k with WAF/secret keyword spellings spliced in at
                    seeded random points (seed 7): the throughput subjects
                    carry ZERO matches for all five cells, so an answer
                    check on them alone is vacuous. python `re` counts on
                    it (the oracle, 2026-09-25): dbnames 7, union-select 9,
                    sleep-benchmark 6, split 10.
  OUTDIR/split.rx   concat-sqli with its one ^-anchored top-level arm
                    deleted (5 -> 4 arms, 1460 -> 291 bytes): the same
                    edit as cycle1_profile.md M5.b (51_M5b_patternedit.log).
"""
import os, random, sys
out = sys.argv[1]; R = sys.argv[2] if len(sys.argv) > 2 else "/Users/fdicostanzo/pcrec-bench"
base = open(os.path.join(R, "bench/capability/throughput/t-64k.bin"), "rb").read()
ins = [b" UNION all SeLeCt a FROM b\n", b" union select from ", b"x union\nselect from", b" sleep(1) ",
       b"BENCHMARK(1000000,md5(1))", b" SLEEP (x)", b" information_schema ", b"DB_NAME (", b" pg_toast ",
       b" sqlite_temp_master ", b"schema_name ", b"xinformation_schema", b" select char(", b"\" as x from",
       b"1 union all ", b"(load_file(", b"' regexp ;", b"end);", b"UPDATE t set", b"alter table ",
       b"https://hooks.slack.com/services/T12345678/B12345678/abcdefghijklmnopqrstuvwx",
       b"HTTPS://HOOKS.SLACK.COM/services/Tabcdefgh/Babcdefgh/abcdefghijklmnopqrstuvwx"]
random.seed(7); buf = bytearray(); pos = 0
while pos < len(base):
    step = random.randint(200, 2000); buf += base[pos:pos + step]; pos += step
    buf += random.choice(ins)
open(os.path.join(out, "match.bin"), "wb").write(b"1 union select from x\n" + bytes(buf))
pat = open(os.path.join(R, "bench/capability/patterns/wild-waf-crs-942360-concat-sqli.rx")).read().strip()
arms, d, cls, i, cur = [], 0, False, 0, 0
while i < len(pat):
    c = pat[i]
    if c == "\\": i += 2; continue
    if cls:
        if c == "]": cls = False
    elif c == "[": cls = True
    elif c == "(": d += 1
    elif c == ")": d -= 1
    elif c == "|" and d == 0: arms.append(pat[cur:i]); cur = i + 1
    i += 1
arms.append(pat[cur:])
keep = [a for a in arms if not a.startswith("^")]
open(os.path.join(out, "split.rx"), "w").write("|".join(keep))
print("match.bin + split.rx: %d -> %d arms, %d -> %d bytes" % (len(arms), len(keep), len(pat), len("|".join(keep))))
