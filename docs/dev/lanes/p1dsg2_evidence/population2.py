#!/usr/bin/env python3
"""Lane p1dsg2 (2026-10-29): the admission-table census RE-RUN under rev 1 (review r1 S1, A1, S5).

What changed from p1dsg_evidence/population.py (rev 0), each with its review id:
  [r1 S1]  THE LANDMARK CHOICE RULE: every admissible inner landmark of the pattern is classified by
           the rev-1 table and the FIRST by (deciding row rank, then rarity ratio descending, then
           leftmost position) is the pattern's landmark. Rev 0 took tiers.py's best-by-tier pick.
  [r1 A1]  UNIQUE forms corrected to what the (state, class) rule reproduces (unique_rule.py): a
           `\\b` FIRST in P and P non-nullable after it; the `(?m)^` form is gone (row `bot`).
  [r1 A1]  NEW ROW `bot`: P holds a BOT-family node (\\A, \\G, non-multiline ^, multiline ^); pcrec
           builds no reverse machine for it (pcrec_nfa_has_bot), so W declines.
  [r1 D3/S2] row `fixed` becomes `next-landmark` (the selected NEXT row already enters from a
           landmark or a fixed offset). The BUILD reads NEXT's selection (CAND_READ); this
           parse-only census APPROXIMATES it by P's width (fixed: offset-set/run-pinned; bounded:
           handoff) and says so. Bench rows are corrected from their stamps by bench_stamps.sh.
  [r1 S5]  `fixed` under utf8 uses the BYTE width only where every item is ASCII-scoped; otherwise
           the census marks the row width-unknown (no claim).
Rows not computable without a compile (route, A built, W overflow, deny, utf8 non-ASCII L[0]) are
listed by the report and counted by the stage-1 census (OWED, boxlock), not here.
Env as tiers.py (PCREC, CORPUS); P1_F the rarity factor (default 2, UNMEASURED). --selftest runs the
hand rows; --sabotage choice (rev 0's pick) must FAIL them."""
import argparse, collections, importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("tiers", os.path.join(HERE, "..", "revwalk_evidence", "tiers.py"))
T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
R = T.R
WORD = set(b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz")
F = float(os.environ.get("P1_F", "2"))
SABOTAGE = None
ORDER = ["no-split", "bot", "g1", "next-landmark", "branches", "rarity", "excl-cand", "excl-lower",
         "factor-free", "plain-shared", "fallback"]
RANK = {r: i for i, r in enumerate(["excl-cand", "excl-lower", "factor-free", "plain-shared", "rarity",
                                    "next-landmark", "branches", "g1", "bot", "fallback", "no-split"])}


def has_bot(items):
    for it in items:
        if it[0] == "zw" and (it[1] == "anch" or it[2:3] == ("^m",)):
            return True
        if it[0] == "grp" and any(has_bot(a) for a in it[1]):
            return True
        if it[0] == "rep" and has_bot([it[1]]):
            return True
    return False


def unique_starts(pit):
    """The sufficient forms the (state, class) rule reproduces (unique_rule.py): fixed width, or a
    `\\b` FIRST in P followed by a non-nullable, word-only rest."""
    if pit is None:
        return False
    lo, hi, al, fl = R.seq_props(pit)
    if hi is not None and lo == hi:
        return True
    body = list(pit)
    if not body or body[0][:2] != ("zw", "ctx") or body[0][2] != "\\b":
        return False
    rest = [x for x in body[1:] if x[0] != "zw"]
    rlo, _rhi, ral, _ = R.seq_props(rest)
    return rlo > 0 and bool(ral) and ral <= WORD


def candidates(tree, utf8, icase):
    """tiers.decide's loop, returning EVERY landmark candidate instead of its best pick."""
    tree = T.strip_one_group(tree)
    branches = [R.flatten(a, True) for a in tree]
    per = [R.cands_of(sp, "max") for sp in branches]
    if not any(per):
        return []
    common = set(per[0])
    for d in per[1:]:
        common &= set(d)
    first = set()
    for sp in branches:
        try:
            eps, tr, s0, _e = R.build_nfa(sp, utf8)
            for q in T.eclose(eps, {s0}):
                for cs, _ in tr[q]:
                    first |= cs
        except R.Cap:
            first = set(T.ALL)
    key_ppm = R.ppm(first) if first else R.ppm(T.ALL)
    out = []
    for key in common:
        run = list(key)
        scan = min(R.ppm(r) for r in run)
        res = []
        for bi, sp in enumerate(branches):
            ch = None
            for start, _r in per[bi][key]:
                c = T.classify_p(sp[:start], run, utf8, icase)
                c["S_refs"] = T.refs_back(sp[start + len(run):])
                c["_pit"] = sp[:start]
                c["_pos"] = start
                if ch is None or (c["tier"] != "T0" and (ch["tier"] == "T0" or T.TIER_RANK[c["tier"]] < T.TIER_RANK[ch["tier"]])):
                    ch = c
            res.append(ch)
        if all(c["tier"] == "T0" for c in res):
            continue
        tier = max((c["tier"] for c in res if c["tier"] != "T0"), key=lambda t: T.TIER_RANK[t])
        out.append(dict(
            tier=tier, strong=all(c["tier"] == "T0" or c["strong"] for c in res),
            excl=all(c["tier"] == "T0" or c["excl"] for c in res),
            ratio=key_ppm / max(1, scan), nbr=len(res), srefs=any(c["S_refs"] for c in res),
            L="".join(chr(min(r)) if 32 <= min(r) < 127 else "\\x%02x" % min(r) for r in run),
            _pit=res[0]["_pit"] if len(res) == 1 else None, pos=min(c["_pos"] for c in res),
            bot=any(has_bot(c["_pit"]) for c in res), unb=max(c.get("unb", 0) for c in res),
            pfixed=all(c["tier"] == "T1" for c in res)))
    return out


def admission(c):
    if c["bot"]:
        return "bot"
    if c["tier"] == "G1":
        return "g1"
    if c["pfixed"] or not c["unb"]:
        return "next-landmark"        # census approximation of CAND_READ(NEXT) (docstring)
    if c["nbr"] > 1:
        return "branches"
    if c["ratio"] < F:
        return "rarity"
    if c["excl"]:
        if c["srefs"] and not unique_starts(c["_pit"]):
            return "excl-lower"
        return "excl-cand"
    if c["strong"]:
        return "factor-free"
    if c["tier"] == "T2":
        return "plain-shared"
    return "fallback"


def choose(cands):
    """THE LANDMARK CHOICE RULE (rev 1 [r1 S1]): the deciding row's rank, then rarity, then leftmost."""
    if SABOTAGE == "choice":
        best = max(cands, key=lambda c: (c["ratio"], -T.TIER_RANK[c["tier"]]))
        return admission(best), best
    rows = [(RANK[admission(c)], -c["ratio"], c["pos"], i) for i, c in enumerate(cands)]
    k = min(rows)
    return admission(cands[k[3]]), cands[k[3]]


def classify(r):
    pat = r["pat"]
    try:
        rd = T.Reader(pat, r["icase"], r["enc"] == "utf8", r["mline"])
        tree = rd.parse()
    except (R.Unparsed, IndexError, ValueError, RecursionError):
        return "uncounted", {}
    if T.anchored(T.strip_one_group(tree)):
        return "no-split", {}
    if rd.approx:
        return "uncounted", {}
    try:
        cands = candidates(tree, r["enc"] == "utf8", r["icase"])
    except (R.Cap, RecursionError):
        return "uncounted", {}
    if not cands:
        return "no-split", {}
    return choose(cands)


HAND = [  # (pattern, expected row, expected landmark)
    (rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "excl-cand", "@"),
    (rb"\b(\w+)=[^&]*&(?:[^&]*&)*\1=", "excl-cand", "="),            # [r1 S1]: '=' over '&'
    (rb"(\w+)=[^&]*&(?:[^&]*&)*\1=", "excl-lower", "&"),       # rank tie: the rarer landmark
    (rb"\b(\w*)=x\1", "excl-lower", "=x"),                             # [r1 A1] nullable: not unique
    (rb"(?:^|-)([\w-]+)=\1\b", "bot", "="),                            # [r1 A1] positional
    (rb"(?:\G|-)([\w-]+)=\1\b", "bot", "="),
    (rb"(a+)X\1", "excl-lower", "X"),
    (rb"\b[a-z_][a-z0-9_]{0,31}=\"(?:[^\"\\]|\\.)*\"", "next-landmark", "=\""),  # bounded P: handoff
    (rb"ab[0-9]@x", "next-landmark", "@x"),
    (rb"(?>a+)@", "g1", "@"),
    (rb"\S+@\S+", "plain-shared", "@"),
    (rb"^\w+@", "no-split", ""),
]


def selftest():
    ok = True
    for pat, want, wl in HAND:
        row, d = classify({"pat": pat, "icase": False, "enc": "byte", "mline": False})
        good = row == want and (not wl or d.get("L") == wl)
        ok &= good
        print("%-4s %-55s %-14s L=%-5s (want %s L=%s)" % ("ok" if good else "FAIL", pat.decode()[:55], row,
                                                         d.get("L", ""), want, wl))
    return ok


def main():
    global SABOTAGE
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--sabotage", choices=["choice"])
    a = ap.parse_args()
    SABOTAGE = a.sabotage
    if a.selftest or a.sabotage:
        ok = selftest()
        if a.sabotage:
            print("sabotage %s: selftest %s (it must FAIL)" % (a.sabotage, "PASSED: UNDETECTED" if ok else "failed: detected"))
            sys.exit(1 if ok else 0)
        sys.exit(0 if ok else 1)
    pops = {"corpus": T.corpus_pop(), "bench": T.bench_pop()}
    for name, pop in pops.items():
        cnt = collections.Counter(); ex = collections.defaultdict(list); moved = 0
        for r in pop:
            row, d = classify(r)
            cnt[row] += 1
            if row in ("excl-cand", "excl-lower") or name == "bench" and row not in ("no-split", "uncounted"):
                ex[row].append("%s L=%s ratio=%.2f" % (r["id"], d.get("L", ""), d.get("ratio", 0)))
        print("## %s: %d patterns" % (name, len(pop)))
        print("| row | patterns |")
        print("|---|---|")
        for o in ORDER + ["uncounted"]:
            print("| %s | %d |" % (o, cnt[o]))
        for o in ORDER:
            if ex[o]:
                lim = ex[o] if name == "bench" else ex[o][:12]
                print("%s %s (%d): %s" % (name, o, len(ex[o]), "; ".join(lim)))
        print()


if __name__ == "__main__":
    main()
