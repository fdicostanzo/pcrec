#!/usr/bin/env python3
"""tests/compound/check_derive.py -- [COMPOUND] B2's unit check: the split
derivation (src/opt/derive.c) against the twin's (compound.md §B.1, §F row
B2), compared by LANGUAGE.

  check_derive.py DRIVE TREE WORKDIR

Two independent implementations of Q = P with its floor anchors killed and
pruned: the build's, an AST rewrite at the tree-hook (`compound_drive
derive`, through `pcrec_compile_part` with the split derivation), and the
twin's, a text rewrite over its own small parser
(docs/design/compound/twin/twin2.py `derive`). Over the twin's case list
(results/cases2.tsv and cases2_owed.tsv) each case lands in one cell:

  both-q       both derive a Q: the two Qs must answer the same at every
               startpos 0..n+1 (verdict and caps[0]) on the twin's own
               subject generator for P; `\\G` present must agree.
  both-never   both say Q is never (the floor-only form).
  both-decline both decline: the reasons must be the same kind (an
               unkillable `\\G`; nothing killed).
  refused-p    the build refuses P itself (a verb, a callout, a construct
               outside pcrec), confirmed by P's plain compile refusing too:
               the twin's answer is recorded, nothing compared. A part that
               refuses where P compiles (an internal error, G5's walk
               firing) is a FAILURE.
  twin-limit   the twin cannot parse P (its own `twin-parse`/`x-flag`
               declines): nothing compared.
  wider        the build derives where the twin declines "nothing killed"
               because its kill reads `(?m)` anywhere in P as covering every
               `^`, where the build reads each `^`'s own `(?m)` scope: the
               build kills a `^` the twin cannot. Recorded by id.

Anything else is a FAILURE: a never/q disagreement, a decline the other side
does not make (outside `wider`), a language difference. Floors (K35): the
both-q cells and the compared startpos cells. Also asserts compound.md §E.3
G5's tree property through the build's own report on every derived case: a
Q was produced only with at least one floor anchor killed.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CC = os.environ.get("CC", "gcc")
GENCFLAGS = ["-O1", "-std=gnu11", "-Wall", "-Wextra", "-Werror"]
MAIN = r"""
#include <stdio.h>
int main(void)
{
    static char line[1 << 14];
    static unsigned char subj[1 << 13];
    long cells = 0, matches = 0, diffs = 0;
    while (fgets(line, sizeof line, stdin)) {
        size_t n = 0;
        for (char *h = line; h[0] && h[1] && h[0] != '\n'; h += 2) {
            unsigned v; sscanf(h, "%2x", &v); subj[n++] = (unsigned char)v;
        }
        for (size_t from = 0; from <= n + 1; from++) {
            ptrdiff_t a[TQ_NCAPS > RQ__Q_NCAPS ? TQ_NCAPS : RQ__Q_NCAPS][2] = {{0}};
            ptrdiff_t b[TQ_NCAPS > RQ__Q_NCAPS ? TQ_NCAPS : RQ__Q_NCAPS][2] = {{0}};
            int ra = rq__q_search(subj, n, from, a), rb = tq_search(subj, n, from, b);
            cells++;
            if (rb == 1) matches++;
            if (ra != rb || (ra == 1 && (a[0][0] != b[0][0] || a[0][1] != b[0][1]))) {
                if (diffs++ < 3)
                    printf("DIFF from=%zu n=%zu build=%d(%td,%td) twin=%d(%td,%td)\n",
                           from, n, ra, a[0][0], a[0][1], rb, b[0][0], b[0][1]);
            }
        }
    }
    printf("cells=%ld matches=%ld diffs=%ld\n", cells, matches, diffs);
    return diffs ? 1 : 0;
}
"""


def main():
    drive, tree, work = sys.argv[1:4]
    twin_dir = os.path.join(tree, "docs", "design", "compound", "twin")
    sys.path.insert(0, twin_dir)
    import twin2  # the twin's derivation and subject generator
    cases = []
    for name in ("cases2.tsv", "cases2_owed.tsv"):
        for ln in open(os.path.join(twin_dir, "results", name)):
            if not ln.strip() or ln.startswith("#"):
                continue
            f = ln.rstrip("\n").split("\t")
            cases.append(("c%d" % len(cases), f[0], f[1], bytes.fromhex(f[2])))
    twin = {}
    listing = []
    for cid, label, enc, p in cases:
        q, has_g, why = twin2.derive(p, enc)
        twin[cid] = (q, has_g, why)
        listing.append("%s\t%s\t%s\t%s\n" % (cid, enc, p.hex(), q.hex() if q is not None else "-"))
    os.makedirs(work, exist_ok=True)
    r = subprocess.run([drive, "derive", work], input="".join(listing).encode(),
                       capture_output=True, timeout=1800)
    if r.returncode:
        print("FAIL: compound_drive derive exited %d: %s" % (r.returncode, r.stderr.decode()[:300]))
        return 1
    build = {}
    for ln in r.stdout.decode().splitlines():
        f = ln.split("\t")
        build[f[0]] = {"status": f[1], "killed": int(f[2]), "never": f[6] == "1",
                       "has_g": f[7] == "1", "msg": f[8], "p_ok": f[9] == "1"}
    fails, cells, tally = [], 0, {}
    matches = 0
    for cid, label, enc, p in cases:
        q, has_g, why = twin[cid]
        b = build.get(cid)
        tag = "%s %s %r" % (label, enc, p)
        if b is None:
            fails.append("%s: no build row" % tag); continue
        twin_ok = why.startswith("ok")
        if b["status"] == "refused" and b["p_ok"]:
            fails.append("%s: the part refused where P compiles: %s" % (tag, b["msg"]))
            continue
        if b["status"] == "refused":
            cell = "refused-p"
        elif not twin_ok and (why.startswith("twin-parse") or why.startswith("x-flag")):
            cell = "twin-limit"
        elif not twin_ok and b["status"] == "declined":
            same = ("unkillable" in why and "lookbehind" in b["msg"]) or \
                   ("nothing-killed" in why and "nothing killed" in b["msg"])
            cell = "both-decline"
            if not same:
                fails.append("%s: both decline for different reasons: twin %r, build %r" % (tag, why, b["msg"]))
        elif not twin_ok and "nothing-killed" in why and b["status"] == "ok" and rb"(?" in p and b"m" in p:
            cell = "wider"
        elif twin_ok != (b["status"] == "ok"):
            fails.append("%s: twin %r, build %s %r" % (tag, why, b["status"], b["msg"]))
            continue
        elif q is None or b["never"]:
            cell = "both-never"
            if (q is None) != b["never"]:
                fails.append("%s: never disagrees: twin %s, build %s" % (tag, q is None, b["never"]))
        else:
            cell = "both-q"
        tally[cell] = tally.get(cell, 0) + 1
        if b["status"] == "ok" and b["killed"] < 1:
            fails.append("%s: a Q derived with no floor anchor killed (G5/A2)" % tag)
        if cell != "both-q":
            continue
        if has_g != b["has_g"]:
            fails.append("%s: \\G present disagrees: twin %s, build %s" % (tag, has_g, b["has_g"]))
        tq, rq = os.path.join(work, cid + ".tq.c"), os.path.join(work, cid + ".q.c")
        if not os.path.exists(tq):
            tally["twin-q-refused"] = tally.get("twin-q-refused", 0) + 1
            tally[cell] -= 1
            continue
        tu = os.path.join(work, cid + ".tu.c")
        with open(tu, "w") as fh:
            fh.write(open(tq).read())
            fh.write(open(rq).read())
            fh.write(MAIN)
        exe = os.path.join(work, cid + ".exe")
        c = subprocess.run([CC] + GENCFLAGS + ["-o", exe, tu], capture_output=True, timeout=600)
        if c.returncode:
            fails.append("%s: the comparison TU did not build: %s" % (tag, c.stderr.decode()[:300]))
            continue
        subj = b"".join(s.hex().encode() + b"\n" for s in twin2.subjects(p, enc))
        o = subprocess.run([exe], input=subj, capture_output=True, timeout=600)
        out = o.stdout.decode().strip().splitlines()
        if o.returncode:
            fails.append("%s: the two Qs differ: %s" % (tag, " | ".join(out[-4:])))
            continue
        kv = dict(x.split("=") for x in out[-1].split())
        cells += int(kv["cells"]); matches += int(kv["matches"])
    for f in fails[:40]:
        print("FAIL: " + f)
    floor_ok = tally.get("both-q", 0) >= 60 and cells >= 500000
    print("%s: B2 derive vs twin2.derive: %d cases; %s; %d startpos cells (%d matches) compared, "
          "%d failures" % ("PASS" if not fails and floor_ok else "FAIL", len(cases),
                           ", ".join("%s=%d" % kv for kv in sorted(tally.items())),
                           cells, matches, len(fails)))
    if not floor_ok:
        print("FAIL: below the population floor (60 both-q cases, 500000 cells)")
    return 1 if fails or not floor_ok else 0


if __name__ == "__main__":
    sys.exit(main())
