#!/usr/bin/env python3
"""kvcensus: the [KIT-VERIFY] proof census (D161 addendum 16; review r2
kitverify-proof §7-§8). COMPILE-ONLY: no subject is timed, gcc is never run.
Single process (the box rule of the lane brief).

Population: the [ARTREV] generalizer's enumerator, IMPORTED by path
(docs/dev/optloop/artrev/gen/census.py: bench_pop, corpus_pop, opts, run):
every pcrec-bench bench/<set>/patterns/*.rx (READ-ONLY; -e utf8 on set utf8)
and every distinct (pattern, encoding, icase) block of tests/**/*.rxt, all at
--features all. Each row is compiled in its NATIVE configuration and, when
that is `byte`, again under `-e utf8` (where the pattern compiles).

Per row and configuration, these compiles (all `-p rx -o -`):
  P  the probe CLI (kvprobe.c: --wrap'd site doors) at default flags: the
     artifact, its stamps and every site pcrec hands the kit, with the kit's
     mf_ask class (proven0, proven_prev) for the same site
  N  the same with -fno-scan-edge: the FORWARD machine as a full table
  D  --engine=dfa --no-captures -fno-scan-edge when N has no anchored machine:
     the LANGUAGE machine (the match-here DFA)
  I  --emit-ir on VM artifacts: the VM program (kvvm.py)
  B  the context BODY (kvctx.py) through D's flags, for context sites

    PCREC=build/pcrec PROBE=build/kv/pcrec-kv BENCH=/home/pcrec/projects/pcrec-bench \\
    CORPUS=. OUT=build/kv/run python3 docs/dev/kvcensus/census.py [--limit N] [--selftest]
"""
import argparse, gzip, importlib.util, json, os, random, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kvdfa, kvvm, kvctx, kvpcre  # noqa: E402

E = os.environ
CORPUS = os.path.abspath(E.get("CORPUS", "."))
_spec = importlib.util.spec_from_file_location(
    "artrev_gen", os.path.join(CORPUS, "docs/dev/optloop/artrev/gen/census.py"))
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)
G.NICE = ["nice", "-n", "19"]
PCREC = G.PCREC = E.get("PCREC", "build/pcrec")
PROBE = E.get("PROBE", "build/kv/pcrec-kv")
G.BENCH = E.get("BENCH", "/home/pcrec/projects/pcrec-bench")
G.CORPUS = CORPUS
OUT = E.get("OUT", "build/kv/run")
KVOUT = os.path.abspath(os.path.join(OUT, "sites_cur.tsv"))

SEARCH = ("OFS", "PF", "MLINE", "PRE")
H_ASSIGN = 1


def opts(r):
    return G.opts(r)


def stamps(c):
    d = {}
    for m in re.finditer(r'^#define (RX_[A-Z0-9_]+) (.*)$', c, re.M):
        d[m.group(1)[3:]] = m.group(2).strip().strip('"')
    return d


def probe(r):
    try:
        os.unlink(KVOUT)
    except FileNotFoundError:
        pass
    env = dict(E, KV_OUT=KVOUT)
    try:
        p = subprocess.run(G.NICE + [PROBE, "-p", "rx"] + opts(r) + ["-o", "-", "--pattern", r["pat"]],
                           capture_output=True, timeout=G.TMO, env=env)
    except subprocess.TimeoutExpired:
        return None, [], "timeout"
    if p.returncode != 0:
        return None, [], p.stderr.decode("utf8", "replace").split("\n")[0][:120]
    sites = []
    if os.path.exists(KVOUT):
        for ln in open(KVOUT, encoding="latin-1"):
            f = ln.rstrip("\n").split("\t")
            if len(f) >= 24 and f[0] == "SITE":
                sites.append(f)
    if sites:   # the size ladder re-emits: keep the LAST attempt's sites
        last = max(int(f[2]) for f in sites)
        sites = [f for f in sites if int(f[2]) == last]
    return p.stdout.decode("latin-1"), sites, None


def compile_c(r, extra, pat=None):
    return G.run([PCREC, "-p", "rx"] + opts(r) + list(extra) + ["-o", "-", "--pattern", pat or r["pat"]])


LANGF = ("--engine=dfa", "--no-captures", "-fno-scan-edge")


def terms(s):
    """`S:off:need:hex;R:off:need:run/mask` -> [(kind, off, len, need, set|None)]"""
    out = []
    if s in ("-", ""):
        return out
    for t in s.split(";"):
        k, off, need, pay = t.split(":", 3)
        if k == "S":
            out.append(("S", int(off), 1, need, kvdfa.hexset(pay)))
        elif k == "R":
            run = pay.split("/")[0]
            out.append(("R", int(off), len(run) // 2, need, bytes.fromhex(run)))
        else:
            out.append((k, int(off), 0, need, None))
    return out


def preds(s):
    if s in ("-", ""):
        return []
    return [(p[0], terms(p[2:-1])) for p in s.split("|")]


def sent(ts):
    return ",".join("%d%s%s" % (o, "+%d" % (n - 1) if n > 1 else "", nd) for k, o, n, nd, _ in ts)


def ctxs_for(A):
    """one representative predecessor per byte class of A, plus the absent one"""
    if not A.seeded:
        return [b""]
    rep = {}
    for b in range(256):
        rep.setdefault(A.bc[b], bytes([b]))
    return [b""] + list(rep.values())


def sample(S, n, rnd):
    out = []
    for _ in range(n):
        out.append(bytes(rnd.choice(sorted(s)) for s in S))
    return out


def controls(r, A, L, wk, rnd):
    """PCRE2 re-asks of the machine's claims; returns dict of counts."""
    res = dict(c1=0, c1f=0, c2=0, c2f=0, c3=0, c3f=0)
    P = kvpcre.Pat(r["pat"], r["icase"], r["enc"] == "utf8")
    if not P.ok():
        res["pcre"] = "refused"
        return res
    cx = ctxs_for(A)
    E_ = L["exact"]
    if E_ > 0:
        for w in sample(L["S"][:E_], 8, rnd):
            res["c1"] += 1
            if not any(P.is_prefix(w, c) for c in cx):
                res["c1f"] += 1
                res.setdefault("c1w", w.hex())
    if L["cex"]:
        ok, bad = L["cex"]
        res["c2"] += 1
        if not any(P.is_prefix(ok, c) for c in cx) or any(P.is_prefix(bad, c) for c in cx):
            res["c2f"] += 1
            res["c2w"] = ok.hex() + "/" + bad.hex()
    if wk:
        for w in sample(L["S"][:wk], 6, rnd):
            res["c3"] += 1
            tail = bytes([rnd.randrange(0x80) if r["enc"] == "utf8" else rnd.randrange(256)])
            if P.match_len(w + tail) != wk:
                res["c3f"] += 1
                res.setdefault("c3w", (w + tail).hex())
            j = rnd.randrange(wk)
            out = sorted(set(range(256)) - L["S"][j])
            if out:
                m = w[:j] + bytes([rnd.choice(out)]) + w[j + 1:]
                res["c3"] += 1
                if P.match_len(m) is not None:
                    res["c3f"] += 1
                    res.setdefault("c3w", m.hex())
    P.free()
    return res


def ctx_check(r, item_far_word, absent_ok, lead_tok, body_S, rnd):
    """PCRE2: the leading \\b/\\B equals its positional rewrite on samples."""
    pat = r["pat"]
    i = pat.find(b"\\" + lead_tok.encode())
    if i < 0:
        return None
    rw = pat[:i] + (b"(?<=\\w)" if item_far_word else b"(?<!\\w)") + pat[i + 2:]
    u8 = r["enc"] == "utf8"
    P, Q = kvpcre.Pat(pat, r["icase"], u8), kvpcre.Pat(rw, r["icase"], u8)
    if not (P.ok() and Q.ok()):
        return None
    n = bad = 0
    for w in sample(body_S, 6, rnd):
        for c in (b"", b"a", b" ", b"_", b"\n", b"7", b"-"):
            n += 1
            if P.match_len(w, c) != Q.match_len(w, c):
                bad += 1
    P.free(); Q.free()
    return n, bad


def analyse(r, cfg, rnd):
    rec = dict(pop=r["pop"], id=r["id"], cfg=cfg, enc=r["enc"], icase=int(r["icase"]))
    c0, sites, err = probe(r)
    if err:
        rec["status"] = "refused: " + err
        return rec, []
    st = stamps(c0)
    rec.update(status="ok", engine=st.get("ENGINE", "?"), prefilter=st.get("DFA_PREFILTER", st.get("VM_PREFILTER", "")),
               handoff=st.get("REQ_HANDOFF", ""), ncaps=st.get("NCAPS", ""))
    c1, e1 = compile_c(r, ["-fno-scan-edge"])
    F = kvdfa.Machine(c1, "forward") if c1 else None
    A = kvdfa.Machine(c1, "anchored") if c1 else None
    src, lpat, L = "N", r["pat"], None
    an = kvctx.strip_anchors(r["pat"])
    if not (A and A.ok):
        c2, e2 = compile_c(r, LANGF)
        A = kvdfa.Machine(c2, "anchored") if c2 else None
        src = "D" if A and A.ok else ("none:" + (e2 or "no-anchored")[:60])
        if not (A and A.ok) and c2:
            Fz = kvdfa.Machine(c2, "forward")
            if Fz.ok and not Fz.seeded and Fz.acc_any[0]:
                src, A = "nullable", None   # the empty match: no position is in every match
                L = dict(S=[], span=0, exact=0, cex=None, Qk={})
        if L is None and not (A and A.ok) and an and an[0]:
            # an attempt-engine pattern (`^`/`\A`/`\G` at the origin, no table):
            # the language from the origin is the body's, the anchor pcrec's edge
            body = an[2] + {"$": b"$", "z": b"\\z", "Z": b"\\Z", "": b""}[an[1]]
            c3, e3 = compile_c(r, LANGF, pat=body)
            A = kvdfa.Machine(c3, "anchored") if c3 else None
            if A and A.ok:
                src, lpat = "anchor-stripped:" + an[0], body
    rec["lang_src"] = src
    if A and A.ok:
        L = kvdfa.lang(A, A.starts())
    if c1:
        st1 = stamps(c1)
        rec["nse_moved"] = int(st1.get("ENGINE") != st.get("ENGINE"))
    vm = None
    if st.get("ENGINE") == "vm":
        ir, e3 = G.run([PCREC, "--emit-ir"] + opts(r) + ["--pattern", r["pat"]])
        vm = kvvm.vm_prefix(ir) if ir else None
    wk = kvdfa.whole(A, L, A.starts()) if L and A is not None else 0
    if L:
        rec.update(span=L["span"], exact=L["exact"], whole=wk, seeded=int(A.seeded) if A else 0,
                   views=int(A.has_views) if A else 0, S0=kvdfa.setstr(L["S"][0]) if L["S"] else "")
        if A is not None:
            rec.update(controls(dict(r, pat=lpat), A, L, wk, rnd))
    if an and an[1]:
        # an END anchor: is the body without it whole-cover? (then a match is
        # the product AND a length compare, pcrec's)
        ce, ee = compile_c(r, LANGF, pat=an[2])
        Ae = kvdfa.Machine(ce, "anchored") if ce else None
        if Ae and Ae.ok:
            Le = kvdfa.lang(Ae, Ae.starts())
            rec["whole_end"] = kvdfa.whole(Ae, Le, Ae.starts())
            rec["anchors"] = an[0] + "/" + an[1]
    # context
    cx = kvctx.parse(r["pat"])
    if cx is not None:
        rec["ctx"] = cx["why"] or "ok"
        if not cx["why"]:
            rec["ctx_lead"] = "".join("[%s]" % k for k, _ in cx["lead"])
            rec["ctx_trail"] = "".join("[%s]" % k for k, _ in cx["trail"])
            cb, eb = compile_c(r, LANGF, pat=cx["body"])
            Ab = kvdfa.Machine(cb, "anchored") if cb else None
            Fb = kvdfa.Machine(cb, "forward") if cb else None
            if Ab and Ab.ok:
                Lb = kvdfa.lang(Ab, Ab.starts())
                u8 = r["enc"] == "utf8"
                ok_all, why = True, []
                lead_far = None
                for it in cx["lead"]:
                    adj = Lb["S"][0] if Lb["S"] else None
                    ok, absent, n = kvctx.expressible(it, adj, u8, kvdfa.W)
                    ok_all &= ok
                    why.append("%s%s" % (it[0], "+" if ok else "x"))
                    if it[0] in ("b", "B") and ok and lead_far is None:
                        lead_far = (it[0], not absent)
                wb = kvdfa.whole(Ab, Lb, Ab.starts())
                for it in cx["trail"]:
                    adj = Lb["S"][wb - 1] if wb else None
                    ok, absent, n = kvctx.expressible(it, adj, u8, kvdfa.W) if it[0] in ("b", "B") \
                        else kvctx.expressible(it, None, u8, kvdfa.W)
                    ok_all &= ok
                    why.append("%s%s" % (it[0], "+" if ok else "x"))
                rec.update(ctx_expr=int(ok_all), ctx_items=" ".join(why), ctx_body_span=Lb["span"],
                           ctx_body_exact=Lb["exact"], ctx_whole=wb if ok_all and wb and not Ab.seeded else 0)
                if Fb and Fb.ok and not Fb.seeded and Lb["exact"]:
                    a = kvdfa.uniform(Fb, Lb["S"], Lb["exact"])
                    rec["ctx_a"] = a[1] if ok_all or not cx["lead"] else 0
                # the real machine's seeded entry: constant under the context set?
                if F and F.ok and F.seeded and len(cx["lead"]) == 1 and lead_far:
                    cset = kvdfa.W if lead_far[1] else frozenset(range(256)) - kvdfa.W
                    s = F.starts(cset, absent=not lead_far[1])
                    rec["ctx_seed_const"] = int(len(s) == 1)
                    if len(s) == 1 and L:
                        rec["ctx_real_a"] = kvdfa.uniform(F, L["S"], L["exact"], s)[1]
                if lead_far and Lb["S"]:
                    k = ctx_check(r, lead_far[1], not lead_far[1], lead_far[0], Lb["S"][:max(1, min(Lb["exact"], 6))], rnd)
                    if k:
                        rec["ctx_ck"], rec["ctx_ckf"] = k
            else:
                rec["ctx_body"] = "nomachine:" + (eb or "")[:50]
    out = []
    other = {}
    for f in sites:
        sid = f[3]
        if sid not in SEARCH:
            other[sid] = other.get(sid, 0) + 1
            continue
        kind = f[7]
        pt, ps, sp = terms(f[14]), preds(f[16]), preds(f[18])
        head = int(f[19])
        handoff = int(f[6])
        if sid == "PRE":
            origin = "landmark" if handoff == H_ASSIGN and head > 0 else "presence"
        elif sid == "MLINE":
            origin = "after-nl"
        else:
            origin = "start"
        P0 = kvdfa.hexset(f[22])
        Pp = kvdfa.hexset(f[23])
        row = dict(pop=r["pop"], id=r["id"], cfg=cfg, enc=r["enc"], engine=rec["engine"], door=f[1],
                   site=sid, op=f[4], kind=kind if kind != "UNSTATED" or sid != "OFS" else "DFA_SCAN",
                   origin=origin, sent=sent(pt) if pt else "|".join(sent(t) for _, t in ps),
                   pred_need=f[10], npres=f[17], head_max=head, proven0=len(P0), proven_prev=len(Pp),
                   ask_rc=f[20])
        if F and F.ok and not F.seeded and sid in ("PF", "OFS") and kind != "VM_ATTEMPT":
            # the forward scan's own escape set (bytes that move row 0): the
            # kit's proven0 must contain it, or the stream drops a restart
            esc = frozenset(b for b in range(256) if F.step(0, b) != 0)
            row["esc_rel"] = ("eq" if P0 == esc else "wider" if esc < P0 else "UNDER-esc"
                              if P0 < esc else "differ")
        if L and origin == "start" and L["S"] and sid in ("PF", "OFS") and len(P0) < 256 \
                and P0 < L["S"][0]:
            origin = row["origin"] = "scan-restart"
        if L and origin in ("start", "after-nl") and L["S"]:
            S0 = L["S"][0]
            row["p0rel"] = ("none" if len(P0) == 256 else "exact" if P0 == S0 else
                            "superset" if S0 <= P0 else "UNDER")
            row.update(span=L["span"], exact=L["exact"], mixed=int(L["exact"] < L["span"]),
                       whole=wk, seeded=int(A.seeded) if A else 0)
        k = row["kind"]
        if k in ("DFA_SCAN", "HYB_PF") and L and origin == "start" and L["exact"] == 0:
            row.update(a_contig=0, a_best=0, a_flags="")
        elif k in ("DFA_SCAN", "HYB_PF") and origin == "scan-restart" and F and F.ok and not F.seeded:
            fb, fc, fs = kvdfa.forward_path(F, P0)
            row.update(a_best=fb, a_contig=fc, a_path=1)
        elif k in ("DFA_SCAN", "HYB_PF") and L and origin == "start":
            if F and F.ok and not F.seeded:
                c, b, fl = kvdfa.uniform(F, L["S"], L["exact"])
                row.update(a_contig=c, a_best=b, a_flags="".join("1" if x else "0" for x in fl))
            else:
                row["a_why"] = "seeded" if F and F.ok else "no-forward"
        elif k == "DFA_HAT":
            row["a_why"] = "seeded"
        elif k == "DFA_ATTEMPT":
            row["a_why"] = "attempt"
        if k in ("VM_ATTEMPT", "HYB_PF") and vm and origin == "start":
            row.update(b_lit=vm[0], b_cls=vm[1], b_rlit=vm[2], b_rcls=vm[3])
            if L and vm[1] > L["exact"] and L["exact"] < kvdfa.CAP:
                row["b_over"] = 1
        out.append(row)
    rec["sites"] = len(out)
    rec["other_sites"] = ",".join("%s=%d" % kv for kv in sorted(other.items()))
    return rec, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default="")
    ap.add_argument("--deadline", default="")   # epoch seconds: stop cleanly
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    rows = G.bench_pop() + G.corpus_pop()
    if a.only:
        rows = [r for r in rows if a.only in r["id"]]
    if a.limit:
        rows = rows[:a.limit]
    rnd = random.Random(0x6b76)
    pf = gzip.open(os.path.join(OUT, "patterns.tsv.gz"), "wt")
    sf = gzip.open(os.path.join(OUT, "sites.tsv.gz"), "wt")
    t0 = time.time()
    n = 0
    stop = float(a.deadline) if a.deadline else 0
    for r in rows:
        cfgs = [("native", r)]
        if r["enc"] == "byte":
            cfgs.append(("utf8", dict(r, enc="utf8")))
        for cfg, rr in cfgs:
            try:
                rec, sites = analyse(rr, cfg, rnd)
            except Exception as ex:   # counted, never silent (K35)
                rec, sites = dict(pop=rr["pop"], id=rr["id"], cfg=cfg, enc=rr["enc"],
                                  icase=int(rr["icase"]), status="error: %r" % (ex,)), []
            rec["pat"] = rr["pat"].hex()
            pf.write(json.dumps(rec) + "\n")
            for s in sites:
                sf.write(json.dumps(s) + "\n")
        n += 1
        if n % 100 == 0:
            print("%d/%d rows %.0fs" % (n, len(rows), time.time() - t0), flush=True)
            pf.flush(); sf.flush()
        if stop and time.time() > stop:
            print("DEADLINE: stopped at %d/%d rows" % (n, len(rows)), flush=True)
            break
    pf.close(); sf.close()
    print("== kvcensus COMPLETE rows=%d/%d %.0fs" % (n, len(rows), time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
