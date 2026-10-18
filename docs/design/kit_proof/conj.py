"""kit_proof.md rev 2 §1.1: the `cover_conj[]` table, PROTOTYPED, and the population recount.

Each conjunct is a named row read in order; the first that fails is the `why`
(first-match, the split_conj[] shape). The machine conjuncts read the EMITTED
anchored machine through kvdfa (docs/dev/kvcensus/kvdfa.py), the same reader
the census and the k3-sound critic used: this is a RECOUNT, not an
independent control (the control is X1, libpcre2, §6.4).

usage:
  python3 -I conj.py census SITES.tsv.gz PATTERNS.tsv.gz      # recount (§1.2)
  python3 -I conj.py witnesses < FLAGS<TAB>PATTERN lines       # one verdict per line
  python3 -I conj.py rarm PATTERNS.tsv.gz                       # default vs -fno-rev-end
FLAGS: '-' or any of i (caseless), u (-e utf8), R (-fno-rev-end).
Environment: PCREC (default build/pcrec). Compiles only; times nothing.
"""
import collections, gzip, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "dev", "kvcensus"))
import kvdfa  # noqa: E402

PCREC = os.environ.get("PCREC", "build/pcrec")
CAP = kvdfa.CAP


def compile_c(pat, fl):
    a = [PCREC, "-p", "rx", "--features", "all", "-fno-scan-edge"]
    if "i" in fl: a.append("-i")
    if "u" in fl: a += ["-e", "utf8"]
    if "R" in fl: a.append("-fno-rev-end")
    a += ["-o", "-", "--pattern", pat]
    try:
        p = subprocess.run(["nice", "-n", "19", "gnutimeout", "30"] + a, capture_output=True)
    except FileNotFoundError:
        p = subprocess.run(["nice", "-n", "19", "timeout", "30"] + a, capture_output=True)
    return p.stdout.decode("latin-1") if p.returncode == 0 else None


def stamp(c, k):
    m = re.search(r'#define RX_%s "([^"]*)"' % k, c)
    return m.group(1) if m else ""


# ---- the conjuncts: (id, statement, function(state) -> bool) ---------------
# `st` is filled as rows pass (the machine, the walk, the context sets).

def k_finisher(st):
    # the FINISHER route is CR_DFA (cand_finish_of): engine dfa, scan not the
    # attempt route (CR_ATTEMPT dropped from stage 1, sound M3 / family M5)
    return stamp(st["c"], "ENGINE") == "dfa" and stamp(st["c"], "DFA_SCAN") != "attempt"


def k_earlier(st):
    # an earlier LOCATE row (`empty`, `rev-end`) is selected: not a conjunct of
    # cover, the table's order; counted so the population is complete
    return stamp(st["c"], "DFA_SCAN") not in ("empty", "rev-end")


def k_gstart(st):
    # no \G node on the route's machine (the gstart seed table is not emitted)
    return "_gstart_seed_state" not in st["c"]


def k_machine(st):
    st["A"] = A = kvdfa.Machine(st["c"], "anchored")
    return A.ok


def k_entry(st):
    # e(⊥) is the EMITTED entry constant X of `search_from ? seed[..] : X`
    # (sound M1), never row 0; the seeded entries must be ONE live row r0
    A, c = st["A"], st["c"]
    if not A.seeded:
        st.update(r0=0, Cm1=frozenset(range(256)), absB=True)
        return True
    m = re.search(r"anchored_state = search_from \? rx_anchored_seed_state\[.*?\] : (-?\d+);", c)
    if not m:
        return False
    x = A.norm(int(m.group(1)))
    ent = collections.defaultdict(set)
    for b in range(256):
        e = A.seed[A.bc[b]]
        if e is not None and e in A.live:
            ent[e].add(b)
    if len(ent) != 1:
        return False
    r0 = next(iter(ent))
    if x == r0:
        absB = True
    elif x is None or x not in A.live:
        absB = False
    else:
        return False
    st.update(r0=r0, Cm1=frozenset(ent[r0]), absB=absB)
    return True


def k_width(st):
    L = st["L"] = kvdfa.lang(st["A"], {st["r0"]})
    st["k"] = L["span"]
    return 1 <= L["span"] < CAP and bool(L["Qk"])


def k_exact(st):
    return st["L"]["exact"] == st["k"]


def walk_rows(st):
    rows = set(q for T in st["L"]["Qk"] for q in T)
    return rows


def k_eol(st):
    # no eol_view on the walk at depth k (below k nothing accepts in any form,
    # which lang() already required): an eol-view accept is NOT an end
    # (sound B1), so the row declines rather than choosing a reading
    A = st["A"]
    v = A.views.get("eol_view")
    if not v:
        return True
    return all(v[q] is None or v[q] == q for q in walk_rows(st))


def k_end(st):
    # every row at depth k accepts and none has a live successor (O2)
    A = st["A"]
    for q in walk_rows(st):
        if not A.acc_any[q]:
            return False
        if any(t is not None and t in A.live for t in A.next[q]):
            return False
    return True


def acc_classes(A, q):
    if A.by_class is not None:
        return frozenset(cl for cl in range(A.ncl) if A.by_class[q][cl])
    return frozenset(range(A.ncl)) if A.acc[q] else frozenset()


def acc_at_end(A, q):
    v = A.views.get("end_view")
    if v and v[q] is not None and A.acc[v[q]]:
        return True
    return A.acc[q]


def k_after(st):
    # the rows at k agree on C_k (class-indexed accept) and on the absent rule
    A = st["A"]
    rows = walk_rows(st)
    sets = set(acc_classes(A, q) for q in rows)
    ends = set(acc_at_end(A, q) for q in rows)
    if len(sets) != 1 or len(ends) != 1:
        return False
    cls = next(iter(sets))
    st.update(Ck=frozenset(b for b in range(256) if A.bc[b] in cls), absA=ends.pop())
    return bool(st["Ck"]) or st["absA"]


def k_utf8(st):
    return "u" not in st["fl"] or not any(0x80 <= b < 0xC0 for b in st["L"]["S"][0])


COVER_CONJ = [
    ("finisher-dfa",  "the finisher route is CR_DFA", k_finisher),
    ("earlier-row",   "(order) no earlier LOCATE row applies", k_earlier),
    ("no-gstart",     "no \\G node on the route's machine", k_gstart),
    ("anchored-A",    "the anchored machine A is built", k_machine),
    ("entry-const",   "one live seeded entry; e(⊥) the emitted constant", k_entry),
    ("fixed-width",   "1 <= k < 32, nothing accepts below k", k_width),
    ("exact",         "the language is S_0 x .. x S_{k-1}", k_exact),
    ("no-eol-view",   "no eol view on the walk at k", k_eol),
    ("end-at-k",      "every row at k accepts, no live successor", k_end),
    ("after-agree",   "the rows at k agree on C_k and the absent rule", k_after),
    ("utf8-start",    "S_0 holds no continuation byte (utf8)", k_utf8),
]


def verdict(pat, fl):
    c = compile_c(pat, fl)
    if c is None:
        return "refused", None
    st = dict(c=c, fl=fl)
    for cid, _, fn in COVER_CONJ:
        if not fn(st):
            return cid, st
    return "cover", st


def census(sites_path, pats_path):
    sites = [json.loads(l) for l in gzip.open(sites_path, "rt")]
    pats = [json.loads(l) for l in gzip.open(pats_path, "rt")]
    start = collections.defaultdict(list)
    for s in sites:
        if s.get("origin") == "start":
            start[(s["pop"], s["id"], s["cfg"])].append(s)
    print("## A. stage-1 SITES (census, origin start, whole > 0) by FINISHER route")
    a = collections.Counter()
    for k, ss in start.items():
        for s in ss:
            if s.get("whole", 0) > 0:
                fin = "CR_DFA" if s["engine"] == "dfa" else "CR_VM (hybrid/VM)"
                a[(k[0], k[2], fin, s["kind"], s["site"])] += 1
    for k, v in sorted(a.items(), key=str):
        print("sites", *k, v)
    tot = collections.Counter()
    for k, v in a.items():
        tot[(k[0], k[1], k[2])] += v
    for k, v in sorted(tot.items(), key=str):
        print("total", *k, v)
    print("## B. cover_conj[] over every census whole-cover / context-join PATTERN")
    print("##    (machine read by kvdfa; first failing conjunct = why)")
    hist = collections.Counter()
    cover = collections.Counter()
    for p in pats:
        src = "whole" if p.get("whole") else ("ctx" if p.get("ctx_whole") and p.get("ctx_expr") == 1 else None)
        if not src:
            continue
        has_site = (p["pop"], p["id"], p["cfg"]) in start
        fl = ("i" if p.get("icase") else "") + ("u" if p.get("enc") == "utf8" else "")
        why, st = verdict(bytes.fromhex(p["pat"]).decode("latin-1"), fl or "-")
        if why == "cover" and not has_site:
            why = "no-start-site"
        hist[(p["pop"], p["cfg"], src, why)] += 1
        if why == "cover":
            cover[(p["pop"], p["cfg"], src)] += 1
    for k, v in sorted(hist.items(), key=str):
        print("why", *k, v)
    for k, v in sorted(cover.items(), key=str):
        print("cover", *k, v)
    print("## E. stage-1 sites whose SENT span 0 covers fewer positions than k (family B1:")
    print("##    exact_len is stated over the SENT sets, min(k, sent))")
    e = collections.Counter()
    for k, ss in start.items():
        for s in ss:
            if s.get("whole", 0) > 0 and s["engine"] == "dfa":
                n = sent_positions(s.get("sent", ""))
                e[(k[0], k[2], s["site"], "sent<k" if n < s["span"] else "sent>=k")] += 1
    for k, v in sorted(e.items(), key=str):
        print("sent", *k, v)


def sent_positions(sent):
    """kvcensus `sent` (`0R,1+3O`, ...) -> the number of span-0 positions sent"""
    n = 0
    for t in sent.split(","):
        if not t or t == "-":
            continue
        t = t.rstrip("RO")
        n += int(t.split("+")[1]) + 1 if "+" in t else 1
    return n


def witnesses():
    for ln in sys.stdin:
        ln = ln.rstrip("\n")
        if not ln or ln.startswith("#"):
            continue
        fl, pat = ln.split("\t", 1)
        why, st = verdict(pat, fl)
        extra = ""
        if why == "cover":
            extra = "k=%d absB=%s absA=%s" % (st["k"], st["absB"], st["absA"])
        print("%-3s %-24s %-14s %s" % (fl, pat, why, extra))


def rarm(pats_path):
    """every census DFA-engine pattern whose verdict moves under -fno-rev-end:
    the population sound B1 names (end-anchored bodies that become start-origin
    CR_DFA sites when the earlier `rev-end` row is denied)"""
    pats = [json.loads(l) for l in gzip.open(pats_path, "rt")]
    h, ex = collections.Counter(), collections.defaultdict(list)
    for p in pats:
        if p.get("engine") != "dfa":
            continue
        fl = ("i" if p.get("icase") else "") + ("u" if p.get("enc") == "utf8" else "")
        pat = bytes.fromhex(p["pat"]).decode("latin-1")
        w0, _ = verdict(pat, fl or "-")
        w1, _ = verdict(pat, fl + "R")
        if w0 != w1:
            h[(p["pop"], p["cfg"], w0, w1)] += 1
            if len(ex[(w0, w1)]) < 4:
                ex[(w0, w1)].append(pat[:40])
    print("## C. verdict moves under -fno-rev-end (default -> denied)")
    for k, v in sorted(h.items(), key=str):
        print("rarm", *k, v)
    for k, v in sorted(ex.items(), key=str):
        print("e.g.", *k, " ".join(repr(x) for x in v))


if __name__ == "__main__":
    if sys.argv[1] == "census":
        census(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "rarm":
        rarm(sys.argv[2])
    else:
        witnesses()
