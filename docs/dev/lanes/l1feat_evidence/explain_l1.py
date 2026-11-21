#!/usr/bin/env python3
"""span_arms L1's compare, the DISAGREEMENTS EXPLAINED (lane l1feat): every
row compare_l1.py lists as OBSERVED-ONLY or UTF8-ONLY is put in one class by
a MECHANICAL test, never by reading it; a row no class's test accepts is
UNEXPLAINED (a STOP). The classes, each with its test:

  leaf-dead   the empty-class leaf (span_arms §14.4 L1, D-9; "the census lists
              them apart", §14.3): listed `dead`, with no lookaround of any
              spelling in the text, and still `dead` under
              `--harness=restore=look` (build/pcrec-harness), so the never bit
              is not the item's.
  spelling    a positive lookaround spelled `(?*`, `(*pla:`, `(*plb:`,
              `(*positive_lookahead:` etc. (the census population reads `(?=`
              and `(?<=` only, census_l1.py `has_pos_look`): rewritten to
              `(?=` / `(?<=` (`(*napla:` and `(?*` are the non-atomic forms;
              the walk reads a body's bytes, which atomicity does not move),
              the feature lists the SAME byte facts for the rewrite, and the
              model, run on the rewrite, predicts the observed byte movers.
  rep-copy    a guard meets a variable repeat's first or last COPY (span arms
              R1's split `X^m . gap`: the head is the first copy, the tail the
              last); the model reads a variable repeat as a WALL
              (census_l1.py `flatten`). Test: with the repeat's copies taken
              away (`--harness=restore=rep`, its old best-only form) the item
              moves nothing: the byte facts equal those under
              `--harness=restore=rep+look`.
  utf8-only   no byte fact moves; the utf8 compile moved. The model reads
              byte only. Test: the byte facts are equal (by construction of
              the class) and the utf8 `req_whole_run` why is `dead`, the
              utf8 run otherwise unchanged.

usage: explain_l1.py COMPARE_TXT BASE_PCREC WORK_PCREC WORK_HARNESS OUT_FILE
rc 0 when every row is explained.
"""
import importlib.util
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("compare_l1", os.path.join(HERE, "compare_l1.py"))
CMP = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CMP)
C = CMP.C

LOOKAROUND = re.compile(rb"\(\?(<?[=!]|\*|<\*)|\(\*(n?a?p?l[ab]|positive_look|negative_look|non_atomic_positive_look)")
REWRITE = [(rb"(*non_atomic_positive_lookahead:", b"(?="), (rb"(*non_atomic_positive_lookbehind:", b"(?<="),
           (rb"(*positive_lookahead:", b"(?="), (rb"(*positive_lookbehind:", b"(?<="),
           (rb"(*napla:", b"(?="), (rb"(*naplb:", b"(?<="), (rb"(*pla:", b"(?="), (rb"(*plb:", b"(?<="),
           (rb"(?<*", b"(?<="), (rb"(?*", b"(?=")]


def byte_facts(pcrec, pat, extra=()):
    try:
        r = subprocess.run([pcrec, "--features", "all"] + list(extra) + ["--emit-facts=byte,utf8", "--pattern", pat],
                           capture_output=True, timeout=C.TIMEOUT)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode:
        return None
    out = {}; sec = None
    for line in r.stdout.decode("utf-8", "surrogateescape").splitlines():
        if line.startswith("#section "):
            sec = line.split()[1]; continue
        if line.startswith("#") or sec != "facts":
            continue
        x = line.split("\t")
        if x[1] in CMP.WATCH:
            out[(x[0], x[1])] = (x[6], x[7])
    return out


def vals(f, enc="byte"):
    return {k[1]: v[0] for k, v in f.items() if k[0] == enc}


def main():
    cmp_txt, base, work, harn, out = sys.argv[1:]
    rows = []
    for l in open(cmp_txt, encoding="utf-8", errors="surrogateescape"):
        m = re.match(r"\s+(OBSERVED-ONLY|UTF8-ONLY) (\S+) (.*?) (observed|utf8-facts)=", l)
        if m:
            pat = m.group(3).encode("latin-1", "surrogateescape").decode("unicode_escape").encode("latin-1")
            rows.append((m.group(1), m.group(2), pat, l.strip()))
    cls = {}; lines = []; bad = 0
    for kind, src, pat, raw in rows:
        b, w = byte_facts(base, pat), byte_facts(work, pat)
        verdict = None
        if b is None or w is None:
            verdict = "UNEXPLAINED (a build refused)"
        elif kind == "UTF8-ONLY":
            bu, wu = vals(b, "utf8"), vals(w, "utf8")
            if vals(b) == vals(w) and w[("utf8", "req_whole_run")][1] == "dead" and bu == wu:
                verdict = "utf8-only"
        else:
            dead = w[("byte", "req_whole_run")][1] == "dead" and b[("byte", "req_whole_run")][1] != "dead"
            if dead and not LOOKAROUND.search(pat):
                h = byte_facts(harn, pat, ["--harness=restore=look"])
                if h and h[("byte", "req_whole_run")][1] == "dead":
                    verdict = "leaf-dead"
            if verdict is None and any(o in pat for o, _ in REWRITE):
                q = pat
                for o, n in REWRITE:
                    q = q.replace(o, n)
                wq = byte_facts(work, q)
                if wq is not None and vals(wq) == vals(w) and \
                   (wq[("byte", "req_whole_run")][1] == "dead") == dead:
                    r = C.one((base, "rewrite", q, True)) if C.has_pos_look(q) else {}
                    mv = set(r.get("moved", []))
                    ob = CMP.obs_byte_set({"work": {k: ("",) + v for k, v in w.items()},
                                           "base": {k: ("",) + v for k, v in b.items()}})
                    if mv and mv == ob:
                        verdict = "spelling"
                    elif "abstain" in r:
                        lines.append("  NOTE rewrite %s abstained: %s" % (C.esc(q), r["abstain"]))
            if verdict is None:
                h = byte_facts(harn, pat, ["--harness=restore=rep"])
                hl = byte_facts(harn, pat, ["--harness=restore=rep+look"])
                if h is not None and hl is not None and vals(h) == vals(hl):
                    verdict = "rep-copy"
        if verdict is None:
            verdict = "UNEXPLAINED"
        cls[verdict] = cls.get(verdict, 0) + 1
        if verdict.startswith("UNEXPLAINED"):
            bad += 1
        lines.append("  %-11s %s %s" % (verdict, src, C.esc(pat)))
    head = ["rows read: %d" % len(rows)] + ["  %s: %d" % kv for kv in sorted(cls.items())]
    lines = head + lines + ["== explain COMPLETE: %d unexplained" % bad]
    open(out, "w").write("\n".join(lines) + "\n")
    print("\n".join(head)); print(lines[-1])
    for l in lines:
        if "UNEXPLAINED" in l or "NOTE" in l:
            print(l)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
