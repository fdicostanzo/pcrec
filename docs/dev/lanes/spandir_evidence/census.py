#!/usr/bin/env python3
"""spandir census: span-able shapes in forward vs reverse automata.

Lane spandir (opus, 2026-11-06), study only.  READ-ONLY on the tree: runs
build/pcrec (--list-source, -o FILE) and writes only under --out.  No gcc,
no timing.  Pattern loading is scensus's (docs/dev/lanes/scensus_evidence/
census.py, load_corpora/list_rxt), copied so this script stands alone.

Measurements (one compile of the emitted C per item, counted from the TEXT):
  T  every artifact (default engine, --features all): per MACHINE, the
     distinct [OPT-5] scan edges (bounded / unbounded) and stay skips
     (M2.1) that were EMITTED.  A machine walks reverse iff its loop spells
     `rewind_position` (the reverse DfaDir objects: reverse, landmark).
     Covers the DFA engine's machines AND the VM artifacts' capture-erased
     prefilter pair, which is the same emitter.
  R  revdet backward walks (W4): artifacts with an `_rv<N>_cursor` walk,
     and the longest run of line-adjacent identical backward class steps
     (`if (cur > floor && (TEST)) { cur--; goto ..}`), i.e. an exact count
     of one class replicated by vm_rev_emit's A_REP arm.  APPROXIMATION.
  L  lookbehind branches: every top-level branch of every lookbehind body
     in the population, compiled ALONE as a pattern with --engine=dfa
     --no-captures.  Its REVERSE machine is the proxy for the branch's
     reverse automaton (A-REV 3.1 row 2/3); its FORWARD machine is reported
     beside it.  PROXY: inline flags set outside the lookbehind are lost;
     the reverse machine is RECOVER's (built for a forward accept), not the
     hand-off's, which differs only in the seed (cursor vs forward end).
     LFLAGS deny the start rows that skip the reverse pass, so the reverse
     machine is always walked and its edges are emitted.

Plants are compiled by the same code; a mismatch makes the run RED.
Final line: `spandir-census: COMPLETE ...` or `spandir-census: RED ...`.
Usage: census.py --root WORKTREE --out DIR [--bench DIR] [--limit N]
"""
import argparse, collections, os, re, subprocess, sys, tempfile

def run(pcrec, args, timeout=40):
    try:
        r = subprocess.run([pcrec] + args, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")


def esc_arg(p):
    out = []
    for ch in p:
        o = ord(ch)
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif 32 <= o < 127:
            out.append(ch)
        else:
            for b in ch.encode("utf-8", "surrogateescape"):
                out.append("\\x%02x" % b)
    return "\"" + "".join(out) + "\""


def unesc(v):
    return re.sub(r"\\(x[0-9a-fA-F]{2}|.)", lambda m: {"t": "\t", "n": "\n", "r": "\r",
                  "\\": "\\"}.get(m.group(1)) if m.group(1)[0] != "x" and m.group(1) in "tnr\\"
                  else (chr(int(m.group(1)[1:], 16)) if m.group(1)[0] == "x" else m.group(0)), v)


def list_rxt(pcrec, path, pop):
    rc, out, err = run(pcrec, ["--list-source", path], timeout=60)
    if rc != 0:
        return []
    hdr, rows = None, []
    for line in out.splitlines():
        if line.startswith("#kind\t"):
            hdr = line[1:].split("\t")
        elif line.startswith("#section"):
            break
        elif hdr and line and not line.startswith("#"):
            f = line.split("\t")
            d = dict(zip(hdr, f + [""] * (len(hdr) - len(f))))
            if d["kind"] in ("pattern", "pattern-esc"):
                rows.append({"pat": unesc(d["pattern"]), "i": "i" in d.get("flags", ""),
                             "enc": d.get("encoding", "") if d.get("encoding", "") in ("byte", "utf8") else "",
                             "pop": pop, "src": "%s:%s" % (path, d["line"])})
    return rows


def load_corpora(root, bench, pcrec):
    ents = []
    for dp, dn, fn in os.walk(os.path.join(root, "tests")):
        dn.sort()
        for f in sorted(fn):
            if f.endswith(".rxt"):
                ents += list_rxt(pcrec, os.path.join(dp, f), "corpus")
    b = os.path.join(bench, "bench")
    if os.path.isdir(b):
        for sub in sorted(os.listdir(b)):
            p = os.path.join(b, sub, "patterns.rxt")
            if os.path.isfile(p):
                ents += list_rxt(pcrec, p, "bench")
            ex = os.path.join(b, sub, "export")
            if os.path.isdir(ex):
                for f in sorted(os.listdir(ex)):
                    if f.endswith(".rxt"):
                        ents += list_rxt(pcrec, os.path.join(ex, f), "bench")
        up = os.path.join(b, "unusual", "patterns")
        if os.path.isdir(up):
            for f in sorted(os.listdir(up)):
                if f.endswith(".rx"):
                    t = open(os.path.join(up, f), "rb").read().decode("utf-8", "replace").rstrip("\n")
                    ents.append({"pat": t, "i": False, "enc": "", "pop": "bench",
                                 "src": os.path.join(up, f)})
    seen, out = set(), []
    for e in ents:
        k = (e["pop"], e["pat"], e["i"], e["enc"])
        if k not in seen and "\x00" not in e["pat"]:
            seen.add(k)
            out.append(e)
    return out


# ------------------------------------------------------------ emitted C ----
EDGE = re.compile(r"if \((\w+)_state == (\S+) && "
                  r"(scan_position < subject_length|rewind_position > search_from) && ")
STAY = re.compile(r"while \(\((scan_position < subject_length|scan_position \+ 1 < subject_length"
                  r"|rewind_position > search_from)\) && \(\w+?_(\w+)_stay(\d+)\[")
RVSTEP = re.compile(r"if \((\w+_rv\d+_cursor) > [^&]+ && \((.*)\)\) \{ \1--; goto")


def count_c(text):
    """-> dict of counters for one emitted artifact"""
    c = collections.Counter()
    lines = text.splitlines()
    edges = {}
    for i, ln in enumerate(lines):
        m = EDGE.search(ln)
        if m:
            d = "rev" if m.group(3).startswith("rewind") else "fwd"
            bounded = any("scan_run_length" in x for x in lines[i + 1:i + 4])
            edges[(m.group(1), m.group(2))] = (d, bounded)
    for (mach, st), (d, b) in edges.items():
        c["edge_%s_%s" % (d, "bounded" if b else "unbounded")] += 1
        c["edge_mach_%s" % mach] += 1
    stays = set()
    for ln in lines:
        m = STAY.search(ln)
        if m:
            d = "rev" if m.group(1).startswith("rewind") else "fwd"
            stays.add((m.group(2), m.group(3), d))
    for mach, k, d in stays:
        c["stay_%s" % d] += 1
        c["stay_mach_%s" % mach] += 1
    # revdet: distinct walks, longest run of identical adjacent backward steps
    walks, best, run_len, prev = set(), 0, 0, None
    for ln in lines:
        m = RVSTEP.search(ln)
        if m:
            walks.add(m.group(1))
            key = (m.group(1), m.group(2))
            run_len = run_len + 1 if key == prev else 1
            prev = key
            best = max(best, run_len)
        elif ln.strip().startswith(("rx_L", "}", "{", "goto ")) or not ln.strip():
            continue                          # labels and the step's fail jump do not break a run
        else:
            prev, run_len = None, 0
    c["revdet_walks"] = len(walks)
    c["revdet_maxrun"] = best
    for ln in lines[:60]:
        m = re.match(r'#define \w+_ENGINE "(\w+)"', ln)
        if m:
            c["engine_" + m.group(1)] = 1
    return c


def compile_c(pcrec, pat, i, enc, extra, tmp):
    if os.path.exists(tmp):
        os.unlink(tmp)
    args = ["--features", "all"] + (["-i"] if i else []) + (["-e", enc] if enc else []) + \
        extra + ["-p", "rx", "-o", tmp, "--pattern-esc", "--pattern", esc_arg(pat)]
    rc, out, err = run(pcrec, args)
    if rc != 0 or not os.path.exists(tmp):
        return None, (err.strip().splitlines() or ["rc=%d" % rc])[0][:100]
    with open(tmp, encoding="utf-8", errors="replace") as fh:
        return count_c(fh.read()), ""


# ------------------------------------------------------- lookbehind bodies -
LB_OPEN = re.compile(r"\(\?<[=!*]|\(\*(?:plb|nlb|naplb|positive_lookbehind|negative_lookbehind"
                     r"|non_atomic_positive_lookbehind):")


def group_end(s, j):
    """index just past the ')' closing the group whose body starts at j; None if unbalanced"""
    depth, k, n = 1, j, len(s)
    while k < n:
        ch = s[k]
        if ch == "\\":
            if s[k + 1:k + 2] == "Q":
                e = s.find("\\E", k + 2)
                k = n if e < 0 else e + 2
                continue
            k += 2
            continue
        if ch == "[":
            k += 1
            if s[k:k + 1] == "^":
                k += 1
            if s[k:k + 1] == "]":
                k += 1
            while k < n and s[k] != "]":
                if s[k] == "\\":
                    k += 2
                elif s[k:k + 2] == "[:":
                    e = s.find(":]", k + 2)
                    k = n if e < 0 else e + 2
                else:
                    k += 1
            k += 1
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return k + 1
        k += 1
    return None


def split_top(body):
    """top-level '|' split, same lexical rules as group_end"""
    out, depth, k, start, n = [], 0, 0, 0, len(body)
    while k < n:
        ch = body[k]
        if ch == "\\":
            k += 2
            continue
        if ch == "[":
            # class skip: find the closing ']' honoring escapes
            k += 1
            if body[k:k + 1] == "^":
                k += 1
            if body[k:k + 1] == "]":
                k += 1
            while k < n and body[k] != "]":
                k += 2 if body[k] == "\\" else 1
            k += 1
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "|" and depth == 0:
            out.append(body[start:k])
            start = k + 1
        k += 1
    out.append(body[start:])
    return out


def lookbehind_branches(pat):
    res = []
    for m in LB_OPEN.finditer(pat):
        j = m.end()
        e = group_end(pat, j)
        if e is None:
            continue
        for br in split_top(pat[j:e - 1]):
            res.append(br)
    return res


# The L proxy forces RECOVER's reverse pass so the REVERSE machine is always
# walked and its edges emitted: the start rows that skip it (pinned, width,
# landing) and the other reverse walks (rev-end, landmark) are denied.
LFLAGS = ["--engine=dfa", "--no-captures", "-fno-start-pinned", "-fno-start-width",
          "-fno-start-landing", "-fno-rev-end", "-fno-landmark-walk"]


PLANTS = [
    # (kind, pattern, {counter: (op, value)})
    ("T", r"[a-z]{3,10}@", {"edge_fwd_bounded": (">=", 1), "edge_rev_bounded": (">=", 1),
                           "edge_mach_forward": (">=", 1), "edge_mach_reverse": (">=", 1)}),
    ("T", r"foo[a-z]*=.*bar", {"stay_fwd": (">=", 1), "stay_rev": (">=", 1)}),
    ("T", r"([a-z]|[0-9]X){0,8}", {"edge_fwd_bounded": ("==", 0), "edge_rev_bounded": ("==", 0),
                                  "edge_fwd_unbounded": ("==", 0), "edge_rev_unbounded": ("==", 0)}),
    ("T", r"(?:(a)b|(c)d){1,8}e", {"revdet_walks": ("==", 1)}),
    ("T", r"(?:(a)bb|(c)d){1,8}e", {"revdet_walks": ("==", 1), "revdet_maxrun": (">=", 2)}),
    ("L", r"a{1,254}b", {"edge_rev_bounded": (">=", 1)}),
    ("L", r"a{1,255}", {"edge_rev_bounded": (">=", 1)}),   # needs LFLAGS: its default start is `landing`
    ("L", r"ab|c", {"edge_rev_bounded": ("==", 0), "edge_rev_unbounded": ("==", 0), "stay_rev": ("==", 0)}),
]


def check(c, want):
    bad = []
    for k, (op, v) in want.items():
        got = c.get(k, 0)
        if (op == ">=" and got < v) or (op == "==" and got != v):
            bad.append("%s=%d want %s%d" % (k, got, op, v))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--bench", default="/home/pcrec/projects/pcrec-bench")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    pcrec = os.path.join(a.root, "build", "pcrec")
    os.makedirs(a.out, exist_ok=True)
    tmp = os.path.join(a.out, "artifact.c")
    red = []

    for kind, pat, want in PLANTS:
        extra = LFLAGS if kind == "L" else []
        c, why = compile_c(pcrec, pat, False, "", extra, tmp)
        if c is None:
            red.append("plant %s %r refused: %s" % (kind, pat, why))
            continue
        bad = check(c, want)
        if bad:
            red.append("plant %s %r: %s" % (kind, pat, "; ".join(bad)))

    ents = load_corpora(a.root, a.bench, pcrec)
    if a.limit:
        ents = ents[:a.limit]
    tot = {p: collections.Counter() for p in ("corpus", "bench")}
    has = {p: collections.Counter() for p in ("corpus", "bench")}
    status = {p: collections.Counter() for p in ("corpus", "bench")}
    ex = collections.defaultdict(list)
    lb = []
    rows = open(os.path.join(a.out, "artifacts.tsv"), "w")
    rows.write("pop\tsrc\tengine\tedge_fwd_b\tedge_fwd_u\tedge_rev_b\tedge_rev_u\tstay_fwd\tstay_rev"
               "\trevdet_walks\trevdet_maxrun\tpattern\n")
    for e in ents:
        p = e["pop"]
        c, why = compile_c(pcrec, e["pat"], e["i"], e["enc"], [], tmp)
        if c is None:
            status[p]["refused"] += 1
        else:
            status[p]["ok"] += 1
            eng = "dfa" if c.get("engine_dfa") else ("vm" if c.get("engine_vm") else "other")
            status[p]["engine_" + eng] += 1
            tot[p].update(c)
            for k in ("edge_fwd_bounded", "edge_fwd_unbounded", "edge_rev_bounded",
                      "edge_rev_unbounded", "stay_fwd", "stay_rev", "revdet_walks"):
                if c.get(k):
                    has[p][k] += 1
                    if len(ex[(p, k)]) < 3:
                        ex[(p, k)].append(e["pat"][:80])
            if c.get("revdet_maxrun", 0) >= 2:
                has[p]["revdet_run>=2"] += 1
                if len(ex[(p, "revdet_run>=2")]) < 3:
                    ex[(p, "revdet_run>=2")].append(e["pat"][:80])
            rows.write("\t".join([p, e["src"], eng] + [str(c.get(k, 0)) for k in (
                "edge_fwd_bounded", "edge_fwd_unbounded", "edge_rev_bounded", "edge_rev_unbounded",
                "stay_fwd", "stay_rev", "revdet_walks", "revdet_maxrun")]
                + [e["pat"].replace("\t", "\\t").replace("\n", "\\n")[:200]]) + "\n")
        for br in lookbehind_branches(e["pat"]):
            lb.append((p, e, br))
    rows.close()

    # L: lookbehind branches, distinct (pop, branch, i, enc)
    seen, lbrows = set(), []
    lbt = {p: collections.Counter() for p in ("corpus", "bench")}
    with open(os.path.join(a.out, "lookbehind_branches.tsv"), "w") as fh:
        fh.write("pop\tsrc\tstatus\tedge_fwd_b\tedge_fwd_u\tedge_rev_b\tedge_rev_u\tstay_fwd\tstay_rev\tbranch\n")
        for p, e, br in lb:
            k = (p, br, e["i"], e["enc"])
            if k in seen:
                continue
            seen.add(k)
            lbt[p]["branches"] += 1
            c, why = compile_c(pcrec, br, e["i"], e["enc"], LFLAGS, tmp)
            if c is None:
                lbt[p]["refused"] += 1
                fh.write("%s\t%s\trefused:%s\t\t\t\t\t\t\t%s\n" % (p, e["src"], why, br))
                continue
            lbt[p]["ok"] += 1
            for kk in ("edge_fwd_bounded", "edge_fwd_unbounded", "edge_rev_bounded",
                       "edge_rev_unbounded", "stay_fwd", "stay_rev"):
                if c.get(kk):
                    lbt[p]["has_" + kk] += 1
            fh.write("\t".join([p, e["src"], "ok"] + [str(c.get(kk, 0)) for kk in (
                "edge_fwd_bounded", "edge_fwd_unbounded", "edge_rev_bounded", "edge_rev_unbounded",
                "stay_fwd", "stay_rev")] + [br]) + "\n")

    L = []
    for p in ("corpus", "bench"):
        L.append("[%s] patterns %d: compiled %d (dfa %d, vm %d), refused %d" % (
            p, sum(status[p][x] for x in ("ok", "refused")), status[p]["ok"],
            status[p]["engine_dfa"], status[p]["engine_vm"], status[p]["refused"]))
        for k in ("edge_fwd_bounded", "edge_fwd_unbounded", "edge_rev_bounded", "edge_rev_unbounded",
                  "stay_fwd", "stay_rev", "revdet_walks"):
            L.append("[%s] %-20s artifacts-with %5d   total %5d   e.g. %s" % (
                p, k, has[p][k], tot[p][k], " | ".join(ex[(p, k)])))
        L.append("[%s] %-20s artifacts-with %5d   e.g. %s" % (
            p, "revdet_run>=2", has[p]["revdet_run>=2"], " | ".join(ex[(p, "revdet_run>=2")])))
        mach = sorted((k[len("edge_mach_"):], v) for k, v in tot[p].items() if k.startswith("edge_mach_"))
        smach = sorted((k[len("stay_mach_"):], v) for k, v in tot[p].items() if k.startswith("stay_mach_"))
        L.append("[%s] edges by machine: %s" % (p, ", ".join("%s=%d" % x for x in mach)))
        L.append("[%s] stays by machine: %s" % (p, ", ".join("%s=%d" % x for x in smach)))
        L.append("[%s] lookbehind branches %d: dfa-compiled %d, refused %d; with fwd bounded edge %d, "
                 "fwd unbounded %d, REV bounded edge %d, REV unbounded %d, fwd stay %d, REV stay %d" % (
                     p, lbt[p]["branches"], lbt[p]["ok"], lbt[p]["refused"],
                     lbt[p]["has_edge_fwd_bounded"], lbt[p]["has_edge_fwd_unbounded"],
                     lbt[p]["has_edge_rev_bounded"], lbt[p]["has_edge_rev_unbounded"],
                     lbt[p]["has_stay_fwd"], lbt[p]["has_stay_rev"]))
    L.append("plants %d, red %d" % (len(PLANTS), len(red)))
    for r in red:
        L.append("RED: " + r)
    if red:
        L.append("spandir-census: RED %d" % len(red))
    else:
        L.append("spandir-census: COMPLETE plants=%d corpus=%d bench=%d lb_branches=%d" % (
            len(PLANTS), sum(status["corpus"].values()) - status["corpus"]["engine_dfa"]
            - status["corpus"]["engine_vm"] - status["corpus"]["engine_other"],
            sum(status["bench"].values()) - status["bench"]["engine_dfa"]
            - status["bench"]["engine_vm"] - status["bench"]["engine_other"],
            lbt["corpus"]["branches"] + lbt["bench"]["branches"]))
    with open(os.path.join(a.out, "summary.txt"), "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L))
    if os.path.exists(tmp):
        os.unlink(tmp)
    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main())
