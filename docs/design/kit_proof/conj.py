"""kit_proof.md rev 2.1 §1.1: the `cover_conj[]` table, PROTOTYPED, and the population recount.

Each conjunct is a named row read in order; the first that fails is the `why`
(first-match, the split_conj[] shape). The machine conjuncts read the EMITTED
anchored machine through kvdfa (docs/dev/kvcensus/kvdfa.py), the same reader
the census and the k3-sound critic used: this is a RECOUNT, not an
independent control (the control is X1, libpcre2, §6.4).

Rows here, in order, against the note's ids [r3rc M-A, m8]: C1 finisher-dfa,
then `earlier-row` (the LOCATE order, not a conjunct; counted so the
population is complete), C3, C4, C6, C7, C8, C9, C10, C11, C12. C2
`origin-start` is RETIRED (rev 2.1, UL-n1): the census applies nothing after
the table, so the `why` histogram is first-match in this order. C5
`unmarked-A` is NOT here: it is an assertion with no population (§1.1), and
an unmarked A is what every compile this script reads emits today. C8 here is
the MACHINE half only (`exact` = machine-inexact); the producers-disagree half
needs `span_facts`, which is unbuilt (family M2 PARTIAL, owed at Z2). C13/C14
are the kit's and are not here.

CONJ_PLANT=c9-depth-k in the environment restores revision 2's C9 (eol views
tested at depth k only), the K1 plant witnesses.txt's `ab|a$\n` rows turn red.
The other CONJ_PLANT values are kit_proof.md §6.3's plants on the reading, for
X0 (`x0/`) to turn red; each is off unless named, and the default reading is
unchanged by them:
  cm1-all        S1130  C_{-1} stated as every byte
  c8-skip        S1131  C8 skipped (exact_len := k)
  c10-drop       S1132  C10's no-live-successor test dropped
  absb-flip      S1133  absent-before flipped
  absa-flip      S1134  absent-after flipped
  c9-eol-as-end  S1139  C9 dropped AND an eol view at k read as the end
  e0-row0        S1140  e(⊥) := row 0, not the emitted constant (both arms)

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
PLANT = os.environ.get("CONJ_PLANT", "")


def compile_c(pat, fl):
    a = [PCREC, "-p", "rx", "--features", "all", "-fno-scan-edge"]
    if "i" in fl: a.append("-i")
    if "u" in fl: a += ["-e", "utf8"]
    if "R" in fl: a.append("-fno-rev-end")
    a += ["-o", "-", "--pattern"]
    # the pattern goes to argv as its own BYTES (latin-1 round trip): a str
    # argument would be re-encoded as UTF-8 and the compile would read a
    # different pattern (this instrument's own first-run defect, 2026-10-18)
    argv = [os.fsencode(x) for x in ["nice", "-n", "19", "gnutimeout", "30"] + a] + [pat.encode("latin-1")]
    p = subprocess.run(argv, capture_output=True)
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
    # e(⊥) is the EMITTED entry constant X (sound M1), never row 0, on BOTH
    # arms: unseeded `anchored_state = X;`, seeded `search_from ? seed[..] : X`
    # (rev 2.2, X0's R1: `\Zx` writes X = 2, and row 0 is the eol view's
    # target). kvdfa reads X (Machine.entry); the seeded entries must be ONE
    # live row r0
    A = st["A"]
    if not A.entry_read:
        return False
    x = A.entry
    if PLANT == "e0-row0":
        x = 0   # S1140: row 0 read as e(⊥), not the emitted constant X (both arms)
    if not A.seeded:
        if x is None or x not in A.live:
            return False
        st.update(r0=x, Cm1=frozenset(range(256)), absB=True)
        plant_before(st)
        return True
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
    plant_before(st)
    return True


def plant_before(st):
    if PLANT == "cm1-all":
        st["Cm1"] = frozenset(range(256))   # S1130
    if PLANT == "absb-flip":
        st["absB"] = not st["absB"]         # S1133


def k_width(st):
    L = st["L"] = kvdfa.lang(st["A"], {st["r0"]})
    st["k"] = L["span"]
    return 1 <= L["span"] < CAP and bool(L["Qk"])


def k_exact(st):
    # C8's MACHINE half (why `exact` = machine-inexact, [r3rc m2]); the
    # producers-disagree half compares span_facts' S_d, unbuilt here
    if PLANT == "c8-skip":
        return True   # S1131: exact_len := k
    return st["L"]["exact"] == st["k"]


def walk_rows(st):
    rows = set(q for T in st["L"]["Qk"] for q in T)
    return rows


def rows_by_depth(st):
    """the live rows at each depth 0..k from r0 (depth k = walk_rows)"""
    A = st["A"]
    Q, out = {st["r0"]}, []
    for _ in range(st["k"] + 1):
        out.append(Q)
        Q = {t for q in Q for b in range(256) for t in [A.step(q, b)]
             if t is not None and t in A.live}
    return out


def k_eol(st):
    # [r3rc K1] no row at depth 0..k carries a non-identity eol view. At k an
    # eol-view accept is NOT an end (sound B1); BELOW k a mid-pattern
    # non-multiline `$`/`\Z` followed by a consumed `\n` is a transition
    # only under the eol view, invisible to the plain walk (`ab|a$\n`), so
    # the row declines rather than choosing a reading
    A = st["A"]
    v = A.views.get("eol_view")
    if not v or PLANT == "c9-eol-as-end":
        return True
    depths = [walk_rows(st)] if PLANT == "c9-depth-k" else rows_by_depth(st)
    return all(v[q] is None or v[q] == q for Q in depths for q in Q)


def k_end(st):
    # every row at depth k accepts and none has a live successor (O2)
    A = st["A"]
    for q in walk_rows(st):
        if not A.acc_any[q]:
            return False
        if PLANT == "c10-drop":
            continue   # S1132: the no-live-successor test dropped
        if any(t is not None and t in A.live for t in A.next[q]):
            return False
    return True


def acc_classes(A, q):
    if A.by_class is not None:
        return frozenset(cl for cl in range(A.ncl) if A.by_class[q][cl])
    return frozenset(range(A.ncl)) if A.acc[q] else frozenset()


def acc_at_end(A, q):
    if PLANT == "c9-eol-as-end":
        # S1139's second edit: an eol view at k read as the end
        e = A.views.get("eol_view")
        if e and e[q] is not None and A.acc[e[q]]:
            return True
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
    if PLANT == "absa-flip":
        st["absA"] = not st["absA"]   # S1134
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
    ("no-eol-view",   "no eol view on the walk at depth 0..k", k_eol),
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
        hist[(p["pop"], p["cfg"], src, why)] += 1
        if why == "cover":
            # C2 `origin-start` is retired [r3rc M-A]; the admitted patterns
            # with no start-origin census site are U-ctxorigin's, now in U1
            cover[(p["pop"], p["cfg"], src, "start-site" if has_site else "no-start-site")] += 1
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
