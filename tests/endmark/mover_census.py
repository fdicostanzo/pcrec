#!/usr/bin/env python3
"""tests/endmark/mover_census.py -- D164 B3 (lane b3build): which corpus
artifacts move, and is that EXACTLY the rev-end population (endmark.md §R.6.2
item 4, §R.7.3).

Every `pattern`/`pattern-esc` line under tests/ (by `pcrec --list-source`, the
same reading scripts/emit_sweep.py makes; ids are FILE:LINE) is compiled by a
REFERENCE pcrec and a WORKING pcrec, each base (`byte`, `-e utf8`) and each
engine (`auto`, `--engine=vm`), `-o -` on both sides. An artifact MOVES when the
two emitted texts differ. The EXPECTED movers are read off the WORKING build's
own `--emit-facts` (`end_mark`'s `form=` part): the artifacts whose `rev-end`
walk took a form that changes text -- `one-seed`, `tagged`, `two-seed` (its
dropped tie code is the only change, and only where today's walk had one).
`denied` and `overflow` keep today's text. The census fails unless the moved
set and the expected set agree exactly, except where a `two-seed` artifact had
no tie code to drop (listed, not failed).

THE ABI DIGIT MUST NOT DIFFER between the two binaries (build the working side
with the reference's `PCREC_ARTIFACT_ABI`), or every artifact moves.

Usage: mover_census.py REF_PCREC WORK_PCREC TREE OUT_TSV [--jobs N]"""
import concurrent.futures as cf, os, subprocess, sys

def run(argv):
    r = subprocess.run(argv, capture_output=True, timeout=120)
    return r.returncode, r.stdout, r.stderr

def decode_escape(s):
    out = bytearray(); i = 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            n = s[i + 1]
            if n == "t": out += b"\t"; i += 2; continue
            if n == "n": out += b"\n"; i += 2; continue
            if n == "r": out += b"\r"; i += 2; continue
            if n == "\\": out += b"\\"; i += 2; continue
            if n == "x": out.append(int(s[i + 2:i + 4], 16)); i += 4; continue
        out += c.encode("utf-8", "surrogateescape"); i += 1
    return bytes(out)

def corpus(pcrec, tree):
    rows = []
    for d, _, fs in os.walk(os.path.join(tree, "tests")):
        for fn in sorted(fs):
            if not fn.endswith(".rxt"): continue
            f = os.path.join(d, fn)
            rc, out, _ = run([pcrec, "--list-source", f])
            if rc: continue
            for line in out.decode("utf-8", "surrogateescape").splitlines():
                if line.startswith("#") or not line.strip(): continue
                v = line.split("\t")
                if len(v) < 5 or v[0] not in ("pattern", "pattern-esc"): continue
                rows.append(("%s:%s" % (os.path.relpath(f, tree), v[1]), decode_escape(v[4])))
    return rows

def form_of(pcrec, pat, base, eng):
    rc, out, _ = run([pcrec, "--emit-facts", "--features", "all"] + base + eng +
                     ["--pattern", pat.decode("utf-8", "surrogateescape")])
    for line in out.decode("utf-8", "replace").splitlines():
        f = line.split("\t")
        if len(f) > 6 and f[1] == "end_mark":
            for part in f[6].split(","):
                if part.startswith("form="): return part[5:]
    return "-"

def task(ref, work, pid, pat, base, eng):
    argv = ["-p", "rx", "--features", "all"] + base + eng + ["-o", "-", "--pattern",
                                                             pat.decode("utf-8", "surrogateescape")]
    ra, a, _ = run([ref] + argv)
    rb, b, _ = run([work] + argv)
    if ra or rb:
        return pid, pat, base, eng, "refused" if ra == rb else "asymmetric", "-", False
    moved = a != b
    tie = b"revend_tie" in a
    return pid, pat, base, eng, "moved" if moved else "same", form_of(work, pat, base, eng), tie

def main():
    ref, work, tree, out = sys.argv[1:5]
    jobs = int(sys.argv[6]) if len(sys.argv) > 6 and sys.argv[5] == "--jobs" else 12
    pats = corpus(work, tree)
    seen, todo = set(), []
    for pid, pat in pats:
        for base in ([], ["-e", "utf8"]):
            for eng in ([], ["--engine=vm"]):
                key = (pat, tuple(base), tuple(eng))
                if key in seen: continue
                seen.add(key)
                todo.append((pid, pat, base, eng))
    res = []
    with cf.ThreadPoolExecutor(jobs) as ex:
        for r in ex.map(lambda t: task(ref, work, *t), todo):
            res.append(r)
    bad = 0; moved = expected = 0; notie = []
    with open(out, "w") as h:
        h.write("#id\tbase\tengine\tverdict\tform\ttoday_tie\tpattern\n")
        for pid, pat, base, eng, v, form, tie in res:
            exp = form in ("one-seed", "tagged") or (form == "two-seed" and tie)
            h.write("%s\t%s\t%s\t%s\t%s\t%s\t%r\n" % (pid, "utf8" if base else "byte",
                    "vm" if eng else "auto", v, form, int(tie), pat))
            moved += v == "moved"; expected += exp
            if v == "asymmetric":
                bad += 1; print("ASYMMETRIC refusal: %s %r %s %s" % (pid, pat, base, eng))
            elif v == "moved" and not exp:
                bad += 1; print("UNEXPECTED MOVER: %s %r %s %s form=%s" % (pid, pat, base, eng, form))
            elif v == "same" and exp:
                bad += 1; print("EXPECTED MOVER UNMOVED: %s %r %s %s form=%s" % (pid, pat, base, eng, form))
            elif v == "same" and form == "two-seed":
                notie.append(pid)
    print("mover_census: %d compiles, %d moved, %d expected, %d two-seed with no tie code, %d BAD"
          % (len(res), moved, expected, len(notie), bad))
    sys.exit(1 if bad else 0)

main()
