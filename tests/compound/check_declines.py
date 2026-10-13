#!/usr/bin/env python3
"""tests/compound/check_declines.py -- [COMPOUND] THE DECLINE CONTROLS
(docs/design/compound.md §E.4, chk M5): each candidate's admission verdict,
the FIRST FAILING CONJUNCT'S ID (A1..A5) or `admit`, read off the as-built
walk by RUNNING it (`compound_drive walk`), never imported from the twin.

  check_declines.py DRIVE CASES MANIFEST [--write]

CASES is split_cases.tsv (`id<TAB>enc<TAB>P-hex<TAB>...`), the candidate set;
MANIFEST (declines.tsv) is its recorded verdict per (id, enc), written with
--write and held both ways otherwise. The NAMED CONTROLS below are §E.4's
list re-aimed on the as-built derivation (cpb02 finding 2): each asserts its
recorded id, and a refusal at parse is its own control (A3 is UNREACHED by
an artifact, §B.8; A4 is unreached by construction in the first build: a P
that passes A1-A3 compiles both DFA parts). Floors: A1, A2 and A5 each fail
on at least one candidate or control, and `admit` is populated.
"""
import os, subprocess, sys

# (pattern, enc, expected verdict, why) -- §E.4's controls, re-derived.
CONTROLS = [
    (rb"^a(*COMMIT)b|c", "byte", "refused", "A3: a verb refuses at parse; the refusal is the control (A3 UNREACHED by an artifact, §B.8)"),
    (rb"(?<=^a)b|c$", "byte", "A1", "re-run: P is not on the attempt-all route (the lookbehind-held ^), so A1 decides before the derivation"),
    (rb"(?<=\G)a|b$", "byte", "A1", "re-run: as above; the unkillable \\G never reaches the derivation"),
    (rb"(?m)^a|b$", "byte", "A2", "the derivation declines: (?m)^ is not a floor anchor, nothing is killed"),
    (rb"x(?m:^)a|b$", "byte", "A2", "the same, (?m) scoped to the one node"),
    (rb"^(\s*)\{|\}(\s*)$", "byte", "A1", "P routes the VM (captures under an alternation)"),
    (rb"^a$", "byte", "A1", "a fully anchored P is one attempt already"),
    (rb"^x|\n(?m)^b$", "byte", "A5", "WITHDRAWN as an A2 decline (cpb02 f.2): the derivation kills ^x; Q is not end-pinned"),
    (rb"(?:(?m:^a)|^b)", "byte", "A5", "positive for the derivation; A5 decides"),
    (rb"(?i)^(?:select|union)\b|\bor\s+1=1\s*$", "byte", "admit", "concat-sqli's pin-only shape ships"),
    (rb"^\s+|\s+$", "byte", "admit", "K106's trim"),
    (rb"a{0,4}\A", "byte", "admit", "the floor-only form: Q is never"),
]
FLOOR_IDS = ("A1", "A2", "A5", "admit")


def walk(drive, rows):
    inp = "".join("%s\t%s\t%s\n" % (i, e, p.hex()) for i, e, p in rows)
    r = subprocess.run([drive, "walk"], input=inp.encode(), capture_output=True, timeout=3600)
    if r.returncode:
        sys.exit("FAIL: compound_drive walk exited %d: %s" % (r.returncode, r.stderr.decode()[:300]))
    out = {}
    for ln in r.stdout.decode().splitlines():
        i, v = ln.split("\t")[:2]
        out[i] = v
    return out


def main():
    drive, cases, manifest = sys.argv[1:4]
    write = "--write" in sys.argv
    rows = []
    for ln in open(cases, encoding="ascii"):
        f = ln.rstrip("\n").split("\t")
        if len(f) >= 3:
            rows.append(("%s@%s" % (f[0], f[1]), f[1], bytes.fromhex(f[2])))
    ctl = [("ctl%d" % k, e, p) for k, (p, e, _v, _w) in enumerate(CONTROLS)]
    got = walk(drive, rows + ctl)
    fails = []
    for k, (p, e, want, why) in enumerate(CONTROLS):
        v = got.get("ctl%d" % k, "MISSING")
        print("%-7s %-8s %-40r %s" % ("ok" if v == want else "FAIL", v, p.decode("latin-1")[:40], why))
        if v != want:
            fails.append("control %r: %s, recorded %s (%s)" % (p, want, v, why))
    rec = {i: got.get(i, "MISSING") for i, _e, _p in rows}
    if write:
        with open(manifest, "w", encoding="utf-8") as h:
            h.write("# [COMPOUND] B4 decline list: split_cases.tsv's first failing conjunct per\n"
                    "# (id@enc), RECORDED by tests/compound/check_declines.py --write on the\n"
                    "# as-built walk (compound.md §E.4). Regenerate when a conjunct or the\n"
                    "# derivation moves, and say which rows moved.\n")
            for i in sorted(rec):
                h.write("%s\t%s\n" % (i, rec[i]))
        print("wrote %d rows to %s" % (len(rec), manifest))
    else:
        want = {}
        for ln in open(manifest, encoding="utf-8"):
            if ln.startswith("#") or not ln.strip():
                continue
            i, v = ln.rstrip("\n").split("\t")
            want[i] = v
        for i in sorted(set(rec) | set(want)):
            if rec.get(i) != want.get(i):
                fails.append("%s: recorded %s, manifest %s" % (i, rec.get(i), want.get(i)))
    hist = {}
    for v in list(rec.values()) + [got.get(c, "MISSING") for c, _e, _p in ctl]:
        hist[v] = hist.get(v, 0) + 1
    for need in FLOOR_IDS:
        if not hist.get(need):
            fails.append("no candidate's verdict is %s: that conjunct's decline population is empty (K35)" % need)
    for f in fails[:20]:
        print("FAIL: " + f)
    print("%s: decline controls: %d named controls, %d candidates recorded (verdicts over both: %s); %d failures" %
          ("PASS" if not fails else "FAIL", len(CONTROLS), len(rec),
           " ".join("%s=%d" % kv for kv in sorted(hist.items())), len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
