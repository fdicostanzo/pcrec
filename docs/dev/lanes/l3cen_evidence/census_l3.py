#!/usr/bin/env python3
"""span_arms unit L3's CENSUS (docs/design/span_arms.md rev 3.3 §14.4 L3
"Census (first)", D191 addendum 1): the BACK row's predicted movers at the
unit's base (main f8789cd2e, L1 landed), over every `.rxt` pattern under
tests/ and the bench file docs/dev/lanes/sae1_evidence/bench_patterns.txt.

THE RULE (built from §14.4 L3 / D-4 / D-6 / D-11 text, not from any L3 code,
which does not exist):

  TOP's BACK row: when the ROOT's left guard `lg` (the lookbehind item's
  terms that pass the root's left edge, offsets -1, -2, ... contiguous, each
  inside the run domain: 1..128 members) has `lg.n > 0` and `lg.n <= lb_bytes`
  (encoding byte: lb_bytes = lb_max; a lookbehind's own terms never exceed
  its declared length, so the cap holds for every candidate the model builds),
  the candidate is `lg ++ head` at offset -lg.n, where `head` is the maximal
  stretch of exact, in-domain consumed positions from the root's start. `++`
  keeps the FIRST positions and the stored run is bounded (32 positions): a
  candidate whose lg alone fills the bound has an EMPTY consumed extent
  (`(?<=a{32})b`). The row's `++ rg` clause is L2's and is not modelled: a
  lookahead's right leftovers are ignored. `best` is the better of the
  default consumed run and the candidate by `rn_choice_rows`: information
  first (8 - ceil(log2 |S|) per position), then rarity/offset/content ties;
  the model decides on information and COUNTS exact-information ties apart.

  The model's scanner/classes are census_l1.py's (L1's census instrument:
  census_e1/e2 scanner, exact-set positions, nested items). Under-approximations
  are COUNTED, never predicted as moves: a top-level alternation root (each
  branch has its own lg; the ALT combine of BACK candidates is not modelled),
  a lookbehind whose body the model cannot read (backreference, variable
  width past its first term), `(?x)`, `(?i)`, callouts, verbs, conditionals,
  recursion and calls (abstained).

OBSERVATION (reference compiler = the base build; the same method as L1's
census): the candidate is SPELLED as a pattern (lg's sets, then head's
sets), compiled with `--emit-facts=byte`, and its listed `req_whole_run` is
the predicted run; today's facts and emitted stamps (RX_REQ_WHY,
RX_REQ_HANDOFF, RX_DFA_SCAN, RX_DFA_PREFILTER, RX_VM_PREFILTER) are read from
the pattern itself. Mover classes: `new-run` (today none), `narrower-run`
(today a run, the candidate has strictly more information), `landmark-K`
(req_landmark_maxoff moves to -t), `handoff`/`why`/`prefilter`/`cover` are
read off today's stamps of the movers (which routes the moved fact reaches).

usage: census_l3.py PCREC TREE BENCH_FILE OUT_DIR [--jobs N]
"""
import concurrent.futures as cf
import importlib.util
import math
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("census_l1", os.path.join(HERE, "../l1build_evidence/census_l1.py"))
L1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L1)
E1, E2 = L1.E1, L1.E2
ABSTAINS = L1.ABSTAINS
Pos, Look, Res, ZERO, WALL = L1.Pos, L1.Look, L1.Res, L1.ZERO, L1.WALL
is_pos, in_domain, count_exact = L1.is_pos, L1.in_domain, L1.count_exact
STORE = 32            # the stored run bound (PCREC_MAX_REQ_RUN_SCAN)
TIMEOUT = 60


def meet_seq_lg(slots, res):
    """census_l1.meet_seq, returning (never, left leftovers, right leftovers)."""
    never = False
    left = {}; right = {}
    for ci, sl in enumerate(slots):
        if not isinstance(sl, Look):
            continue
        for direction in (1, -1):
            d = 0 if direction == 1 else -1
            idx = ci + 1 if direction == 1 else ci - 1
            while d in sl.terms:
                g = sl.terms[d]
                if not in_domain(g):
                    break
                while 0 <= idx < len(slots) and (slots[idx] == ZERO or isinstance(slots[idx], Look)):
                    idx += direction
                if idx < 0 or idx >= len(slots):
                    off = d - count_exact(slots, ci, direction)
                    side = right if direction == 1 else left
                    prev = side.get(off)
                    side[off] = g if prev is None else (prev & g)
                    if prev is not None and not side[off]:
                        never = True
                    d += direction
                    continue
                t = slots[idx]
                if not is_pos(t) or not in_domain(t.set):
                    break
                m = t.narrow & g
                if not m:
                    never = True
                else:
                    t.narrow = m
                idx += direction; d += direction
    return never, left, right


def model(p):
    """-> dict(kind, lg [sets], head [sets], never, limits). kind: 'back' | 'none' | 'altroot'."""
    if b"(?x" in p or b"(?i" in p or re.search(rb"\(\?[a-zA-Z-]*i[a-zA-Z-]*[:)]", p):
        raise L1.Abstain("(?x) or (?i)")
    E2.scan(p)
    br = E1.alts(p, 0, len(p))
    if len(br) > 1:
        return {"kind": "altroot", "lg": [], "head": [], "limits": ["alternation root"]}
    res = Res()
    slots, nv = L1.flatten(p, br[0][0], br[0][1], res, True)
    nv2, left, right = meet_seq_lg(slots, res)
    lg = []
    k = -1
    while k in left and in_domain(left[k]):
        lg.append(left[k]); k -= 1
    lg.reverse()                       # offset -t .. -1
    if nv or nv2:
        # an empty meet: the root is NEVER (L1's dead fact); no BACK candidate is stated
        return {"kind": "dead", "lg": [], "head": [], "limits": sorted(set(res.limits)), "never": True}
    if not lg:
        return {"kind": "none", "lg": [], "head": [], "limits": sorted(set(res.limits)), "never": nv or nv2}
    head = []
    for x in slots:
        if x == ZERO or isinstance(x, Look):
            continue
        if not is_pos(x) or not in_domain(x.narrow):
            break
        head.append(x.narrow)
    return {"kind": "back", "lg": lg, "head": head, "limits": sorted(set(res.limits)), "never": nv or nv2}


def spell(sets):
    return b"".join(L1.spell_set(s) for s in sets)


# ---- run listing parse (information)

def parse_run(v):
    """req_whole_run listing -> list of position sizes, or None."""
    if not v or v == "none":
        return None
    text, _, mask = v.partition("/")
    sizes = []; i = 0; k = 0
    while i < len(text):
        if text[i] == "[":
            j = text.index("]", i); body = text[i + 1:j]; i = j + 1
            n = 0; q = 0
            while q < len(body):
                lo = int(body[q:q + 2], 16); q += 2
                hi = lo
                if q < len(body) and body[q] == "-":
                    hi = int(body[q + 1:q + 3], 16); q += 3
                n += hi - lo + 1
            sizes.append(n)
        else:
            m = int(mask[2 * k:2 * k + 2], 16) if mask else 0xff
            sizes.append(2 ** (8 - bin(m).count("1")))
            i += 2
        k += 1
    return sizes


def info(sizes):
    if sizes is None:
        return 0
    return sum(8 - math.ceil(math.log2(n)) if n <= 128 else 0 for n in sizes)


def facts(pcrec, pat, field=("req_whole_run", "req_landmark_maxoff", "req_byte")):
    try:
        r = subprocess.run([pcrec, "-p", "rx", "--features", "all", "--emit-facts=byte", "--pattern", pat],
                           capture_output=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return None
    rows = {}; sec = None
    for line in r.stdout.decode("utf-8", "surrogateescape").splitlines():
        if line.startswith("#section "):
            sec = line.split()[1]; continue
        if line.startswith("#") or sec != "facts":
            continue
        x = line.split("\t")
        if x[1] in field and x[0] == "byte":
            rows[x[1]] = x[6]
    return rows


def stamps(pcrec, pat, scratch):
    out = os.path.join(scratch, "t%d_%d.c" % (os.getpid(), id(pat) & 0xffff))
    try:
        r = subprocess.run([pcrec, "-p", "rx", "--features", "all", "--pattern", pat, "-o", out],
                           capture_output=True, timeout=TIMEOUT)
        if r.returncode != 0:
            return None
        txt = open(out, "rb").read().decode("latin-1")
    except (subprocess.TimeoutExpired, OSError):
        return None
    finally:
        try:
            os.unlink(out)
        except OSError:
            pass
    d = {}
    for k in ("REQ_WHY", "REQ_HANDOFF", "REQ_RUN", "DFA_SCAN", "DFA_PREFILTER", "VM_PREFILTER"):
        m = re.search(r'#define\s+RX_%s\s+"([^"]*)"' % k, txt)
        d[k] = m.group(1) if m else None
    return d


def esc(b):
    return b.decode("latin-1").encode("unicode_escape").decode()


def one(args):
    ref, src, pat, scratch = args
    rec = {"src": src, "pat": pat}
    try:
        m = model(pat)
    except ABSTAINS as e:
        rec["abstain"] = str(e); return rec
    except Exception as e:
        rec["abstain"] = "scanner: %s" % type(e).__name__; return rec
    rec.update(m)
    if m["kind"] != "back":
        return rec
    lg, head = m["lg"], m["head"]
    t = len(lg)
    rec["t"] = t
    today = facts(ref, pat)
    if today is None:
        rec["refused"] = True; return rec
    rec["today"] = today
    # the stored bound: ++ keeps the FIRST positions
    cand = (lg + head)[:STORE]
    cons = (max(0, min(len(head), STORE - t)))
    rec["cons_empty"] = cons == 0
    rec["cand_spelling"] = spell(cand)
    rc = facts(ref, rec["cand_spelling"])
    crun = rc.get("req_whole_run") if rc else None
    rec["cand_run"] = crun
    ti = info(parse_run(today.get("req_whole_run")))
    ci = info(parse_run(crun))
    rec["info_today"], rec["info_cand"] = ti, ci
    moved = []
    if crun and crun != "none" and ci > 0:
        # the candidate must actually carry the lookbehind's positions: its listed run
        # is the spelling's best; require it to cover lg (its length >= t)
        sz = parse_run(crun)
        if sz is not None and len(sz) >= t:
            if ci > ti:
                moved.append("new-run" if today.get("req_whole_run") in (None, "none") else "narrower-run")
            elif ci == ti:
                rec["tie"] = True
    if moved:
        moved.append("landmark-K")
        rec["pred_K"] = -t
        rec["st"] = stamps(ref, pat, scratch)
    rec["moved"] = moved
    return rec


EXPECT = [   # §14.2's L3 rows: (pattern, expected mover?, expected run text / K)
    (b"(?<=foo)bar", True, "666f6f626172", -3),
    (b"(?<=ab|b)c", True, "6263", -1),
    (b"(?<=ab)ab[a-z]*q", True, "61626162", -2),
    (b"(?<=qz)ab", True, "717a6162", -2),
    (b"(?<=e{10})eeeeeqzx", True, "65" * 15 + "717a78", -10),
    (b"(?<=foo)bar(\\w)\\1", True, None, -3),
    (b"(?<=foobar)\\d*x", True, "666f6f626172", -6),
    (b"(?<=foo)", True, "666f6f", -3),
    (b"(?<=a{32})b", True, None, -32),
    (b"(?<=a)a(\\w)\\1", True, None, -1),
    (b"(?<=foo)bar(?=baz)", True, "666f6f626172", -3),
    (b"xyz(?<=yz)abc", False, None, None),
    (b"(?<=fo{1,3})bar", False, None, None),
    (b"[ac][ac]cc(?<=acc)(?<=cc)d", False, None, None),
    (b"bar(?=baz)", False, None, None),
    (b"xy[ac]b(?:(?<=ab)b|c)", False, None, None),
]


def check_expect(ref, scratch):
    lines = []; bad = 0
    for pat, exp, run, K in EXPECT:
        r = one((ref, "expect", pat, scratch))
        if "abstain" in r:
            lines.append("  EXPECT %-34s ABSTAIN %s" % (pat.decode(), r["abstain"])); bad += 1; continue
        got = bool(r.get("moved"))
        ok = got == exp
        # a BACK candidate that exists but is not a mover is also reported
        detail = " kind=%s t=%s cand_run=%s today_run=%s tie=%s" % (
            r["kind"], r.get("t"), r.get("cand_run"), (r.get("today") or {}).get("req_whole_run"), r.get("tie"))
        if exp and run and r.get("cand_run") and not r["cand_run"].startswith(run):
            ok = False
        if exp and K is not None and r.get("pred_K") != K and got:
            ok = False
        bad += not ok
        lines.append("  EXPECT %-34s %s expect_mover=%s model_mover=%s%s" % (
            pat.decode(), "ok  " if ok else "DIFF", exp, got, detail))
    return lines, bad


def main():
    a = sys.argv[1:]
    jobs = 8
    if "--jobs" in a:
        k = a.index("--jobs"); jobs = int(a[k + 1]); del a[k:k + 2]
    ref, tree, bench_file, out = a
    t0 = time.time()
    os.makedirs(out, exist_ok=True)
    scratch = os.path.join(out, "tmp"); os.makedirs(scratch, exist_ok=True)
    pop = L1.population(ref, tree, bench_file)
    seen = {}
    for src, pat in pop:
        seen.setdefault(pat, []).append(src)
    # a text is bench if any of its sources is bench; corpus if any is corpus
    cands = [(ref, srcs, pat, scratch) for pat, srcs in seen.items() if b"(?<=" in pat]
    work = [(ref, srcs[0], pat, scratch) for (_, srcs, pat, _) in cands]
    with cf.ThreadPoolExecutor(jobs) as ex:
        recs = list(ex.map(one, work))
    for r in recs:
        srcs = seen[r["pat"]]
        r["in_corpus"] = any(s.startswith("corpus:") for s in srcs)
        r["in_bench"] = any(s.startswith("bench:") for s in srcs)
        r["srcs"] = srcs
    def cnt(rs, pred=lambda r: True):
        rs = [r for r in rs if pred(r)]
        return "%d (corpus-only %d, bench %d, both %d)" % (
            len(rs), sum(1 for r in rs if r["in_corpus"] and not r["in_bench"]),
            sum(1 for r in rs if r["in_bench"]), sum(1 for r in rs if r["in_bench"] and r["in_corpus"]))
    absn = [r for r in recs if "abstain" in r]
    read = [r for r in recs if "abstain" not in r]
    back = [r for r in read if r["kind"] == "back"]
    movers = [r for r in back if r.get("moved")]
    lines = [
        "population: %d rows (%d corpus, %d bench), %d distinct texts; with a positive lookbehind text `(?<=`: %d"
        % (len(pop), sum(1 for s, _ in pop if s.startswith("corpus:")), sum(1 for s, _ in pop if s.startswith("bench:")),
           len(seen), len(recs)),
        "abstained: %s" % cnt(absn),
        "read by the model: %s" % cnt(read),
        "  alternation root (BACK combine not modelled, counted): %s" % cnt(read, lambda r: r["kind"] == "altroot"),
        "  never (L1's dead rows; no BACK candidate): %s" % cnt(read, lambda r: r["kind"] == "dead"),
        "  no left leftover (no lg: the lookbehind sits inside consumed context or a wall): %s" % cnt(read, lambda r: r["kind"] == "none"),
        "  BACK candidate exists (lg.n > 0): %s" % cnt(read, lambda r: r["kind"] == "back"),
        "    base compiler refuses: %s" % cnt(back, lambda r: r.get("refused")),
        "    candidate not better than today's run (information): %s" % cnt(back, lambda r: not r.get("refused") and not r.get("moved") and not r.get("tie")),
        "    information TIE (rarity decides, not modelled): %s" % cnt(back, lambda r: r.get("tie") and not r.get("moved")),
        "PREDICTED MOVERS: %s" % cnt(movers),
    ]
    for c in ("new-run", "narrower-run", "landmark-K"):
        lines.append("  %-14s %s" % (c, cnt(movers, lambda r, c=c: c in r["moved"])))
    lines.append("  empty consumed extent among movers: %s" % cnt(movers, lambda r: r["cons_empty"]))
    # route classes from today's stamps
    def st(r, k): return (r.get("st") or {}).get(k)
    lines.append("  routes of the movers (today's stamps):")
    lines.append("    cover route (RX_DFA_SCAN cover): %s" % cnt(movers, lambda r: st(r, "DFA_SCAN") == "cover"))
    lines.append("    prefilter run-pinned (RX_DFA_PREFILTER): %s" % cnt(movers, lambda r: st(r, "DFA_PREFILTER") == "run-pinned"))
    pf = {}
    for r in movers:
        k = "dfa=%s vm=%s" % (st(r, "DFA_PREFILTER"), st(r, "VM_PREFILTER"))
        pf[k] = pf.get(k, 0) + 1
    lines.append("    prefilter stamps (dfa/vm): " + "; ".join("%s: %d" % kv for kv in sorted(pf.items())))
    why = {}
    for r in movers:
        k = "why=%s handoff=%s scan=%s" % (st(r, "REQ_WHY"), st(r, "REQ_HANDOFF"), st(r, "DFA_SCAN"))
        why[k] = why.get(k, 0) + 1
    lines.append("    why/handoff/scan stamps: " + "; ".join("%s: %d" % kv for kv in sorted(why.items())))
    lines.append("  dead (never) movers: 0 by construction (BACK adds a candidate; the never bit is L1's)")
    for r in sorted(movers, key=lambda r: r["srcs"][0]):
        lines.append("  MOVER [%s] %s moved=%s t=%d today_run=%s cand_run=%s stamps=%s" % (
            ",".join(sorted({s.split(":")[0] for s in r["srcs"]})) + ":" + r["srcs"][0].split(":", 1)[1][-40:],
            esc(r["pat"]), "+".join(r["moved"]), r["t"], r["today"].get("req_whole_run"), r["cand_run"],
            "/".join("%s" % st(r, k) for k in ("REQ_WHY", "REQ_HANDOFF", "DFA_SCAN", "DFA_PREFILTER", "VM_PREFILTER"))))
    for r in sorted([r for r in back if not r.get("moved")], key=lambda r: r["srcs"][0]):
        lines.append("  BACK-NOT-MOVED [%s] %s t=%s today_run=%s cand_run=%s tie=%s refused=%s" % (
            r["srcs"][0][:50], esc(r["pat"]), r.get("t"), (r.get("today") or {}).get("req_whole_run"), r.get("cand_run"),
            r.get("tie"), r.get("refused")))
    for r in sorted([r for r in read if r["kind"] == "altroot"], key=lambda r: r["srcs"][0]):
        lines.append("  ALTROOT [%s] %s" % (r["srcs"][0][:50], esc(r["pat"])))
    ab = {}
    for r in absn:
        ab[r["abstain"]] = ab.get(r["abstain"], 0) + 1
    lines.append("abstentions by reason: " + ", ".join("%s %d" % kv for kv in sorted(ab.items())))
    el, bad = check_expect(ref, scratch)
    lines.append("§14.2 / §14.4 L3 expected rows (%d, %d disagreements):" % (len(EXPECT), bad))
    lines += el
    if not read:
        verdict = "STOP (empty population)"
    elif not movers:
        verdict = "STOP (0 predicted movers)"
    else:
        verdict = "PROCEED (%d predicted movers: %s)" % (len(movers), cnt(movers))
    lines.append("CENSUS-VERDICT: " + verdict)
    lines.append("== census COMPLETE: %d predicted movers, %d expectation disagreements, %.0f s" % (len(movers), bad, time.time() - t0))
    with open(os.path.join(out, "summary.txt"), "w") as h:
        h.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return (1 if bad else 0) | (2 if verdict.startswith("STOP") else 0)


if __name__ == "__main__":
    sys.exit(main())
