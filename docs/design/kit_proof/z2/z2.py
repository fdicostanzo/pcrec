"""Z2's instruments, kit_proof.md §7 Z2 / §6.4 (lane z2build).

The SUBJECT here is the BUILT compiler (build/pcrec-harness and its trace
build); the ORACLE is libpcre2 10.46 through X0's server (x0/x0pcre.c), which
knows no reading; conj.py (kvdfa over the emitted anchored machine) is the
PROTOTYPE the built decision must agree with. None of the three shares code
with src/gen/known.c or src/facts/kset.c.

  census OUT.jsonl [-j N]   the trace harness over every census pattern at its own
                            flags, plus the -fno-rev-end arm of every DFA one: the
                            KITPROOF / SPANSET / SITESTATED records, rc, and
                            conj.py's verdict beside them
  hist CENSUS.jsonl         K35: the why histogram (the denominator), the C8
                            control (producers-disagree internal errors, and how
                            many decisions reached C8), the agreement with conj.py
  stated CENSUS.jsonl [--mod M]   X0's stated-set check on every SENT statement the
                            census recorded (SPANSET: the slice; SITESTATED: a FIND
                            site's exact_len), deduplicated; 1-in-M of them
  x1 POP.jsonl OUT.jsonl [-j N]   X1: X0's part-2 subject families run through the
                            BUILT harness artifact (rx_search at every startoffset,
                            the find-all loop) against pcre2_match; POP is X0's
                            population (x0.py pop)
  exh FLAGS PATTERN [ALPHA_HEX] [MAXLEN]   ruling 1's exhaustive cell: every subject
                            up to MAXLEN over ALPHA, every startoffset, find-all
  summary X1.jsonl          fold an x1 run

Env: H (build/pcrec-harness), HT (build/z2trace/pcrec-harness), PCREC
(build/pcrec, conj.py's compiler), X0PCRE (build/x0/x0pcre), Z2OUT (scratch dir,
default build/z2x1). Run from the repo (or worktree) root; heavy modes under the
box queue.
"""
import collections, gzip, hashlib, json, os, random, subprocess, sys, time, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "x0"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "dev", "kvcensus"))
import conj  # noqa: E402
import x0    # noqa: E402

H = os.environ.get("H", "build/pcrec-harness")
HT = os.environ.get("HT", "build/z2trace/pcrec-harness")
OUT = os.environ.get("Z2OUT", "build/z2x1")
KV = os.path.join(HERE, "..", "..", "..", "dev", "kvcensus")
PCRE2_LIBS = ["-lpcre2-8"]


def hargs(binary, fl):
    a = [binary, "--harness=kit-proof", "-p", "rx", "--features", "all"]
    if "i" in fl: a.append("-i")
    if "u" in fl: a += ["-e", "utf8"]
    if "R" in fl: a.append("-fno-rev-end")
    return a


def item_key(pat):
    """a per-pattern scratch directory name: the whole pattern's digest"""
    return hashlib.sha1(pat).hexdigest()


def run_c(argv, pat, env=None, timeout="60"):
    """argv + the pattern as its own BYTES (conj.py's first-run lesson)"""
    full = [os.fsencode(x) for x in ["nice", "-n", "19", "gnutimeout", timeout] + argv] + [pat]
    return subprocess.run(full, capture_output=True, env=env)


def records(err):
    """the trace records, each ending in the compound part's role (`-`: the
    compile itself; a part's compile prints its records into its parent's
    stream, so a record is attributed by its role, never by its position)"""
    kp, sp, st = [], [], []
    for ln in err.decode("latin-1").splitlines():
        f = ln.split("\t")
        if f[0] == "KITPROOF":
            kp.append((f[1], int(f[2][2:]), int(f[3][7:]), f[4]))
        elif f[0] == "SPANSET":
            sp.append((int(f[1]), f[2], f[3]))
        elif f[0] == "SITESTATED":
            st.append((int(f[1]), f[2], f[3]))
    return kp, sp, st


def decision(kp):
    """the compile's own cover decision: its LAST record of role `-` (a compile may
    decide more than once, retries; the last is the shipped attempt's), or None"""
    own = [x for x in kp if len(x) < 4 or x[3] == "-"]
    return own[-1] if own else None


def oracle_pattern(pat, role):
    r"""the pattern PCRE2 is asked about for a statement made by `role`'s compile.
    `\K` is dropped everywhere: it moves PCRE2's reported start (x0pcre counts an
    anchored match not starting at the origin as none) and never what matches,
    while a statement is about the ATTEMPT origin a FIND site's candidate is.
    For the split's Q part (`q`, src/opt/derive.c: P with its floor anchors
    killed, searched only past the floor) `\G` becomes `(?!)`; `^`/`\A` are false
    there by the context (`absent-before` is not asked). A lexical rewrite: an
    escape is copied whole, `\Q..\E`, classes and `(?#..)` verbatim."""
    out, i, n = bytearray(), 0, len(pat)
    while i < n:
        c = pat[i]
        if pat.startswith(b"(?#", i):
            j = pat.find(b")", i)
            j = n if j < 0 else j + 1
            out += pat[i:j]; i = j
        elif pat.startswith(b"\\Q", i):
            j = pat.find(b"\\E", i + 2)
            j = n if j < 0 else j + 2
            out += pat[i:j]; i = j
        elif c == 0x5C and i + 1 < n:
            e = pat[i + 1]
            if e == ord("K"):
                pass
            elif e == ord("G") and role == "q":
                out += b"(?!)"
            else:
                out += pat[i:i + 2]
            i += 2
        elif c == ord("["):
            j = i + 1
            if j < n and pat[j] == ord("^"): j += 1
            if j < n and pat[j] == ord("]"): j += 1
            while j < n and pat[j] != ord("]"):
                if pat[j] == 0x5C: j += 1
                elif pat.startswith(b"[:", j):
                    k = pat.find(b":]", j + 2)
                    if k > 0: j = k + 1
                j += 1
            out += pat[i:j + 1]; i = j + 1
        else:
            out.append(c); i += 1
    return bytes(out)


# ------------------------------------------------------------------ census
def _census_one(a):
    fl, pat_hex = a
    pat = bytes.fromhex(pat_hex)
    env = dict(os.environ, PCREC_KIT_PROOF_TRACE="1")
    p = run_c(hargs(HT, fl) + ["-o", "-", "--pattern"], pat, env)
    kp, sp, st = records(p.stderr)
    r = dict(fl=fl, pat=pat_hex, rc=p.returncode, kp=kp, span=sp, site=st)
    if p.returncode:
        r["err"] = [l for l in p.stderr.decode("latin-1").splitlines() if not l.startswith(("CANDTRACE", "KITPROOF", "SPANSET", "SITESTATED", "CAND"))][-3:]
    try:
        r["conj"] = conj.verdict(pat.decode("latin-1"), fl)[0]
    except Exception as e:  # noqa: BLE001
        r["conj"] = "conj-error:%s" % type(e).__name__
    return r


def census(out_path, j):
    pats = [json.loads(l) for l in gzip.open(os.path.join(KV, "patterns.tsv.gz"), "rt")]
    flags = lambda p: ("i" if p.get("icase") else "") + ("u" if p.get("enc") == "utf8" else "")
    jobs = set()
    for p in pats:
        jobs.add((flags(p) or "-", p["pat"]))
        if p.get("engine") == "dfa":
            jobs.add((flags(p) + "R", p["pat"]))
    jobs = sorted(jobs)
    from multiprocessing import Pool
    t0 = time.time()
    with Pool(j) as pool, open(out_path, "w") as f:
        for r in pool.imap(_census_one, jobs, chunksize=4):
            f.write(json.dumps(r) + "\n")
    print("census items=%d sec=%.0f" % (len(jobs), time.time() - t0))
    print("z2 census: DONE rc=0")


def _load(path):
    return [json.loads(l) for l in open(path)]


def hist(path):
    rs = _load(path)
    enc = lambda fl: "utf8" if "u" in fl else "native"
    arm = lambda fl: "R" if "R" in fl else "default"
    why = collections.Counter()
    first = collections.Counter()
    c8_reach = c8_fail = rc_other = cover = 0
    agree = collections.Counter()
    dis = []
    past_c8 = ("no-eol-view", "end-at-k", "after-agree", "utf8-start", "report-served", "proven")
    for r in rs:
        key = (enc(r["fl"]), arm(r["fl"]))
        errs = " ".join(r.get("err", []))
        if r["rc"]:
            if "producers-disagree" in errs:
                c8_fail += 1
                why[key + ("C8/producers-disagree(internal)",)] += 1
            else:
                rc_other += 1
                why[key + ("rc!=0",)] += 1
            continue
        # one KITPROOF per decision; the compile's own last one (a part's are not it)
        dk = decision(r["kp"])
        w = dk[0] if dk else "not-asked"   # an earlier LOCATE row, or no DFA route
        why[key + (w,)] += 1
        first[(key[0], w.split("/")[0])] += 1
        if w == "cover" or w.split("/")[0] in past_c8:
            c8_reach += 1
        if w == "cover":
            cover += 1
        h = (w == "cover")
        c = (r["conj"] == "cover")
        agree[(h, c)] += 1
        if h != c and len(dis) < 40:
            dis.append((r["fl"], bytes.fromhex(r["pat"]).decode("latin-1")[:60], w, r["conj"]))
    print("## K35: the population every decision is counted over")
    print("items %d  (compiled %d, rc!=0 %d of which C8 internal %d)" % (
        len(rs), len(rs) - rc_other - c8_fail, rc_other + c8_fail, c8_fail))
    print("## why histogram (encoding, arm, first failing conjunct / detail), last decision of the compile")
    for k, v in sorted(why.items(), key=lambda kv: (kv[0][0], kv[0][1], -kv[1])):
        print("why", *k, v)
    print("## by conjunct id (both arms)")
    for k, v in sorted(first.items(), key=lambda kv: (kv[0][0], -kv[1])):
        print("conj", *k, v)
    print("## C8 control (kit_proof §6.4): two producers compared on every decision past C7")
    print("c8 reached=%d  producers-disagree internal errors=%d" % (c8_reach + c8_fail, c8_fail))
    print("## agreement with conj.py (cover vs not): (harness, conj) -> count")
    for k, v in sorted(agree.items()):
        print("agree harness=%s conj=%s %d" % (k[0], k[1], v))
    for d in dis:
        print("disagree", *d, sep="\t")
    print("cover %d" % cover)


# ------------------------------------------------------------------ stated
def _stated_one(a):
    (fl, pat_hex, L, sets, role), kind = a
    S = [frozenset(int(x, 16) for x in s.split(",") if x) for s in sets.split(";")]
    if role not in ("-", "q"):
        return dict(kind=kind, fl=fl, pat=pat_hex, L=L, role=role, unchecked=1, nodes=0, unk=0, bad=0)
    # the failing-direction control: Z2_STATED_CONTROL=raw asks PCRE2 about the
    # pattern as written and from every context, the pre-z2fix check (must read red)
    raw = os.environ.get("Z2_STATED_CONTROL") == "raw"
    pat = bytes.fromhex(pat_hex)
    if not _O.compile(fl, pat if raw else oracle_pattern(pat, role)):
        return None
    # a statement is the HULL over every previous byte (the slice's roots and a
    # site's sets both are), so the PCRE2 tree is grown under the union of
    # contexts: x0's seeded site arm, witnesses within exact + 8 bytes; a byte
    # whose witness search runs out is INCONCLUSIVE and compared on neither side
    r1 = x0.part1_site(_O, dict(S=[sorted(x) for x in S], exact=L, seeded=True), "u" in fl,
                       random.Random(7), absent=raw or role != "q")
    return dict(kind=kind, fl=fl, pat=pat_hex, L=L, role=role, nodes=r1.nodes, unk=r1.unknown,
                bad=len(r1.bad), e=r1.bad[:2])


def stated(path, mod, j):
    rs = _load(path)
    seen = {}
    for r in rs:
        if r["rc"]:
            continue
        for kind, rows in (("slice", r["span"]), ("site", r["site"])):
            for row in rows:
                L, sets, role = (list(row) + ["-"])[:3]
                if L <= 0:
                    continue
                fl = r["fl"].replace("R", "") or "-"
                seen.setdefault((fl, r["pat"], L, sets, role), kind)
    items = sorted(seen.items())
    alln = len(items)
    items = [it for i, it in enumerate(items) if i % mod == 0]
    O = x0.Oracle()
    print("## stated sets (SENT) against %s: %d distinct statements, %d checked (1-in-%d)" % (
        O.version(), alln, len(items), mod))
    O.close()
    from multiprocessing import Pool
    red = unk = n = 0
    kinds = collections.Counter()
    roles = collections.Counter()
    unchecked = 0
    with Pool(j, initializer=_x1_init) as pool:
        for r in pool.imap_unordered(_stated_one, items, chunksize=1):
            if r is None:
                continue
            if r.get("unchecked"):
                unchecked += 1
                print("UNCHECKED part role %s" % r["role"], r["kind"], r["fl"],
                      bytes.fromhex(r["pat"]).decode("latin-1")[:50])
                continue
            n += 1
            kinds[r["kind"]] += 1
            roles[r["role"]] += 1
            unk += r["unk"]
            if r["bad"]:
                red += 1
                print("RED", r["kind"], r["role"], r["fl"], bytes.fromhex(r["pat"]).decode("latin-1")[:50],
                      "L=%d" % r["L"], json.dumps(r["e"][0]))
    print("stated checked=%d (%s; by part role %s) red=%d inconclusive-bytes=%d unchecked-parts=%d" % (
        n, ", ".join("%s %d" % kv for kv in sorted(kinds.items())),
        ", ".join("%s %d" % kv for kv in sorted(roles.items())), red, unk, unchecked))
    print("z2 stated: DONE rc=%d" % (1 if red or unchecked or not n else 0))
    return 1 if red or unchecked or not n else 0


# ------------------------------------------------------------------ X1
def build_art(fl, pat, d):
    """the default-build harness artifact + x1drv; -> (ok, why) and the trace verdict"""
    os.makedirs(d, exist_ok=True)
    c = os.path.join(d, "a.c")
    p = run_c(hargs(H, fl) + ["-o", c, "--pattern"], pat)
    if p.returncode:
        return False, "compile:" + p.stderr.decode("latin-1")[-200:]
    drv = os.path.join(d, "drv")
    g = subprocess.run(["nice", "-n", "19", "gnutimeout", "120", "gcc", "-O1", "-std=gnu11", "-include",
                        os.path.join(d, "a.h"), "-o", drv, os.path.join(HERE, "x1drv.c"), c],
                       capture_output=True)
    if g.returncode:
        return False, "gcc:" + g.stderr.decode("latin-1")[-300:]
    return True, drv


def scan_of(cfile):
    for ln in open(cfile, encoding="latin-1"):
        if ln.startswith("#define RX_DFA_SCAN "):
            return ln.split('"')[1]
    return ""


class Drv:
    def __init__(self, path):
        self.p = subprocess.Popen([path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
                                  bufsize=1 << 16)

    def search(self, s):
        self.p.stdin.write(s.hex() + "\n")
        self.p.stdin.flush()
        a, b = self.p.stdout.readline().rstrip("\n").split("|")

        def one(x):
            if x == "-":
                return None
            if x.startswith("e"):
                return x
            u, v = x.split(":")
            return (int(u), int(v))
        return [one(x) for x in a.split(",")], [one(x) for x in b.split(",") if x]

    def close(self):
        self.p.stdin.close()
        self.p.wait()


def x1_item(it, O):
    t0 = time.time()
    pat, fl = bytes.fromhex(it["pat"]), it["fl"]
    utf = "u" in fl
    res = dict(fl=fl, pat=it["pat"], role=it["role"])
    env = dict(os.environ, PCREC_KIT_PROOF_TRACE="1")
    p = run_c(hargs(HT, fl) + ["-o", "-", "--pattern"], pat, env)
    kp, _, _ = records(p.stderr)
    dk = decision(kp)
    res["why"] = dk[0] if dk else ("trace-rc%d" % p.returncode if p.returncode else "not-asked")
    if res["why"] != "cover":
        return res
    res["k"] = dk[1]
    # keyed on the WHOLE pattern: a 20-byte prefix key let two concurrent workers
    # share one directory, so an item could read another pattern's artifact (z2fix)
    d = os.path.join(OUT, "items", "%s_%s" % (fl, item_key(pat)))
    ok, drv = build_art(fl, pat, d)
    if not ok:
        res["why"] = "build-failed"
        res["e"] = drv
        return res
    res["scan"] = scan_of(os.path.join(d, "a.c"))
    if not O.compile(fl, pat):
        res["why"] = "pcre-refused"
        return res
    rd, _ = x0.reading(pat, fl)
    res["conj"] = rd["why"]
    if rd["why"] != "cover":
        # the subjects are grown from conj.py's plan; with no plan, from the PCRE2 tree
        plan = dict(S=[], k=res["k"], Cm1=[], absB=True, Ck=[], absA=True)
    else:
        plan = rd["plan"]
    rnd = random.Random(zlib.crc32((fl + it["pat"]).encode()))
    lits = x0.text_literals(pat)
    litb = set(b for l in lits for b in l)
    if rd["why"] == "cover":
        _, levels, W = x0.part1_cover(O, plan, utf, rnd, litb)
    else:
        levels, W = [], []
    plan["_S"] = [frozenset(x) for x in plan["S"]] or [frozenset(range(256))] * plan["k"]
    plan["_Cm1"], plan["_Ck"] = frozenset(plan["Cm1"]), frozenset(plan["Ck"])
    subj = x0.subjects(plan, utf, rnd, W, levels, lits, pat)
    D = Drv(drv)
    cells = bad = 0
    first = []
    for s in subj:
        ps, fa_p = O.search(s)
        pa, fa_a = D.search(s)
        for sf in range(len(s) + 1):
            if utf and sf < len(s) and 0x80 <= s[sf] < 0xC0:
                continue
            cells += 1
            if pa[sf] != ps[sf]:
                bad += 1
                if len(first) < 6:
                    first.append(dict(s=s.hex(), sf=sf, pcrec=pa[sf], pcre=ps[sf]))
        cells += 1
        if fa_a != fa_p:
            bad += 1
            if len(first) < 6:
                first.append(dict(s=s.hex(), sf="findall", pcrec=fa_a, pcre=fa_p))
    D.close()
    res.update(subjects=len(subj), cells=cells, bad=bad, e=first, sec=round(time.time() - t0, 2))
    return res


_O = None


def _x1_init():
    global _O
    _O = x0.Oracle()


def _x1_work(it):
    try:
        return x1_item(it, _O)
    except Exception as e:  # noqa: BLE001
        return dict(fl=it["fl"], pat=it["pat"], role=it["role"], why="x1-error", e=repr(e)[:300])


def x1(pop_path, out_path, j):
    items = [json.loads(l) for l in open(pop_path)]
    items = [it for it in items if it["role"] != "site"]
    from multiprocessing import Pool
    t0 = time.time()
    with Pool(j, initializer=_x1_init) as pool, open(out_path, "w") as f:
        for r in pool.imap_unordered(_x1_work, items, chunksize=1):
            f.write(json.dumps(r) + "\n")
            f.flush()
    print("x1 items=%d sec=%.0f" % (len(items), time.time() - t0))
    return summary(out_path)


def summary(path):
    rs = _load(path)
    why = collections.Counter()
    cells = bad = subj = 0
    reds, u1 = [], []
    for r in rs:
        why[(("utf8" if "u" in r["fl"] else "native"), r["why"].split("/")[0])] += 1
        if "cells" in r:
            cells += r["cells"]; bad += r["bad"]; subj += r["subjects"]
            if r["bad"]:
                # X0's U1 class (docs/dev/upstream_issues.md U1): a {0}-quantified
                # anchor group anchors PCRE2's whole pattern; PCRE2 is wrong there
                (u1 if x0.u1_shape(bytes.fromhex(r["pat"])) else reds).append(r)
    print("## X1 over %d items" % len(rs))
    for k, v in sorted(why.items()):
        print("why", *k, v)
    print("x1 cover-artifacts=%d subjects=%d cells=%d bad=%d" % (
        sum(1 for r in rs if "cells" in r), subj, cells, bad))
    print("x1 red-beyond-U1=%d u1-class=%d (cells %d)" % (len(reds), len(u1), sum(r["bad"] for r in u1)))
    for r in reds[:20]:
        print("RED", r["fl"], bytes.fromhex(r["pat"]).decode("latin-1")[:60], json.dumps(r["e"][:2]))
    errs = [r for r in rs if r["why"] in ("x1-error", "build-failed")]
    for r in errs[:10]:
        print("ERR", r["why"], r["fl"], bytes.fromhex(r["pat"]).decode("latin-1")[:60], r.get("e", "")[:200])
    print("z2 x1: DONE rc=%d" % (1 if reds or errs else 0))
    return 1 if reds or errs else 0


# ------------------------------------------------------------------ exhaustive
def exh(fl, pat, alpha, maxlen):
    d = os.path.join(OUT, "exh_%s_%s" % (fl, item_key(pat)))
    os.makedirs(d, exist_ok=True)
    c = os.path.join(d, "a.c")
    env = dict(os.environ, PCREC_KIT_PROOF_TRACE="1")
    p = run_c(hargs(HT, fl) + ["-o", "-", "--pattern"], pat, env)
    kp, _, _ = records(p.stderr)
    print("trace decision:", kp)
    p = run_c(hargs(H, fl) + ["-o", c, "--pattern"], pat)
    assert p.returncode == 0, p.stderr
    print("RX_DFA_SCAN", scan_of(c))
    exe = os.path.join(d, "exh")
    g = subprocess.run(["gcc", "-O2", "-std=gnu11", "-include", os.path.join(d, "a.h"), "-o", exe,
                        os.path.join(HERE, "x1exh.c"), c] + PCRE2_LIBS, capture_output=True, text=True)
    assert g.returncode == 0, g.stderr
    # the failing-direction control: Z2_EXH_PCRE_PAT hands the PCRE2 side a
    # different pattern, which must read diffs > 0
    pp = os.environ.get("Z2_EXH_PCRE_PAT")
    pp = pp.encode("latin-1") if pp else pat
    r = subprocess.run([exe, fl.replace("R", "") or "-", pp.hex(), alpha.hex(), str(maxlen)],
                       capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    print("z2 exh: DONE rc=%d" % r.returncode)
    return r.returncode


if __name__ == "__main__":
    a = sys.argv[1:]
    jj = int(a[a.index("-j") + 1]) if "-j" in a else 8
    if a[0] == "census":
        census(a[1], jj)
    elif a[0] == "hist":
        hist(a[1])
    elif a[0] == "stated":
        # the verdict is the exit status too (a job that execs this reads it)
        sys.exit(stated(a[1], int(a[a.index("--mod") + 1]) if "--mod" in a else 1, jj))
    elif a[0] == "x1":
        sys.exit(x1(a[1], a[2], jj))
    elif a[0] == "summary":
        sys.exit(summary(a[1]))
    elif a[0] == "exh":
        alpha = bytes.fromhex(a[3]) if len(a) > 3 else b"azx09\n#"
        sys.exit(exh(a[1], a[2].encode("latin-1"), alpha, int(a[4]) if len(a) > 4 else 8))
