#!/usr/bin/env python3
"""Lane revwalk (2026-10-29): the TACTIC MODEL for the chain tiers (T2/T3) on REAL patterns.

For every corpus/bench pattern tiers.py admits at T2 or T3 (single top-level branch, byte encoding,
the landmark L excluded from P's alphabet or factor-free), it runs the reverse-walk tactic on generated
subjects at every startpos and compares with libpcre2's own unanchored search:

  for each occurrence j >= lo of L, ascending:
      s = the SMALLEST position in [lo, j] the segment walk accepts (never below lo; a leading context
          item (\\b \\B (?m)^) is evaluated at the accepted position, reading s-1 even when s == lo)
      if s exists and libpcre2's ANCHORED match of the whole pattern at s succeeds: that is the answer
  none: NOMATCH

The walk is the SEGMENT walk (Walk below): tiers.py's segmentation of P, each segment a back-scan over
its alphabet followed by its count rule, a start accepted only inside a segment every earlier segment
of which is nullable; the content of a non-plain inner segment is left to the anchored verify.  So the
model checks the tier's exactness conditions (forced boundaries, the possible-outer rule, exclusion,
no floor at the previous occurrence, context at the start) on a form the kit could implement.
The oracle is libpcre2 (PCRE2_LIB; the box's 10.46), whose search loop shares no code with the walk;
P's automaton comes from rincensus's NFA builder (validated there against rinner_model.py, C2).

Mutations (each must be DETECTED, i.e. wrong at least once):
  max_start   take the LARGEST accepted position
  no_ctx      ignore the leading context item
  no_max      ignore a segment's maximum count
Reported, not gated: the chain rows WITHOUT a strong arm (the walk exact, the exclusion missing) run
ungated.  For a plain run (B{m,M}) the exclusion is a COST condition, not a correctness one (report,
"Exactness conditions"), so 0 wrong there is expected.

Usage: PCREC=build/pcrec CORPUS=. PCRE2_LIB=/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0 \\
       python3 model.py [--subjects 40] [--seed 1]
"""
import argparse, collections, ctypes, importlib.util, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("tiers", os.path.join(HERE, "tiers.py"))
T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
R = T.R

LIB = ctypes.CDLL(os.environ.get("PCRE2_LIB", "/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0"))
SZ = ctypes.c_size_t
LIB.pcre2_compile_8.restype = ctypes.c_void_p
LIB.pcre2_compile_8.argtypes = [ctypes.c_char_p, SZ, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int),
                                ctypes.POINTER(SZ), ctypes.c_void_p]
LIB.pcre2_match_data_create_8.restype = ctypes.c_void_p
LIB.pcre2_match_data_create_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
LIB.pcre2_match_8.restype = ctypes.c_int
LIB.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, SZ, SZ, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
LIB.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(SZ)
LIB.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
LIB.pcre2_config_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
ANCHORED, CASELESS, MULTILINE, DOTALL = 0x80000000, 0x8, 0x400, 0x20
MD = LIB.pcre2_match_data_create_8(256, None)
WORD = T.G.W


def version():
    buf = ctypes.create_string_buffer(64); LIB.pcre2_config_8(11, buf); return buf.value.decode()


def comp(pat, opts):
    e, o = ctypes.c_int(), SZ()
    return LIB.pcre2_compile_8(pat, len(pat), opts, ctypes.byref(e), ctypes.byref(o), None)


def match(code, subj, start, opts=0):
    rc = LIB.pcre2_match_8(code, subj, len(subj), start, opts, MD, None)
    if rc < 0:
        return None if rc == -1 else ("ERR", rc)
    ov = LIB.pcre2_get_ovector_pointer_8(MD)
    return tuple(ov[i] for i in range(2 * rc))


def ctx_ok(kind, subj, s):
    if kind is None:
        return True
    if kind == "^m":
        return s == 0 or subj[s - 1] == 10
    a = s > 0 and subj[s - 1] in WORD
    b = s < len(subj) and subj[s] in WORD
    return (a != b) if kind == "\\b" else (a == b)


class Walk:
    """the SEGMENT walk of the report's T2/T3 rows: per segment (walk order) a back-scan over its alphabet,
    then its count rule; accepts only where every earlier segment is nullable."""

    def __init__(self, pit, utf8):
        body = list(pit); self.ctx = None
        while body and body[0][0] == "zw":
            if body[0][1] == "ctx":
                self.ctx = body[0][2]
            body = body[1:]
        self.segs = []
        segs = T.segments(body)
        for k, q in enumerate(segs):
            lo, hi, al, _f = R.seq_props(q)
            po = all(R.seq_props(segs[t])[0] == 0 for t in range(k))
            g = dict(kind=T.seg_kind(q), alph=al, m=lo, M=hi, po=po)
            if g["kind"] == "chain":
                mt, ma, lv, st, cl = T.reverse_dfa(q, False)
                cmap = [0] * 256
                for ci, c in enumerate(cl):
                    for b_ in c:
                        cmap[b_] = ci
                g["dfa"] = (mt, ma, lv, st, cmap)
            self.segs.append(g)
        _m, _M, al, _f = R.seq_props(body)
        self.classes = [frozenset(al), frozenset(set(range(256)) - set(al))]

    def starts(self, subj, j, lo, mut):
        ctx = None if mut == "no_ctx" else self.ctx
        pos = j; acc = []
        for k in range(len(self.segs) - 1, -1, -1):
            g = self.segs[k]
            e = pos
            while pos > lo and subj[pos - 1] in g["alph"]:
                pos -= 1
            b = pos; ext = e - b
            M = None if mut == "no_max" else g["M"]
            if g["kind"] == "plain":
                if g["po"]:
                    s0 = b if M is None else max(b, e - M)
                    for s in range(s0, e - g["m"] + 1):
                        if ctx_ok(ctx, subj, s):
                            acc.append(s)
                            if mut != "max_start":
                                break
                if ext < g["m"] or (M is not None and ext > M):
                    break
            elif g["kind"] == "fixed":
                if ext < g["m"]:
                    break
                if g["po"]:
                    s = e - g["m"]
                    if ctx_ok(ctx, subj, s):
                        acc.append(s)
                if ext != g["m"]:
                    break
            elif g["kind"] == "chain":
                # the segment's own reverse automaton over its extent [b, e): accepts where it accepts
                mt, ma, lv, q, cmap = g["dfa"]
                p2 = e; full = False
                while True:
                    if ma[q] and g["po"] and ctx_ok(ctx, subj, p2):
                        acc.append(p2)
                    if p2 == b:
                        full = ma[q]; break
                    q2 = mt[q][cmap[subj[p2 - 1]]]
                    if q2 not in lv:
                        break
                    q = q2; p2 -= 1
                if not full:
                    break
            else:
                if ext < g["m"]:
                    break
        if not acc:
            return None
        return max(acc) if mut == "max_start" else min(acc)


def occurrences(subj, run, lo):
    n = len(run)
    return [j for j in range(lo, len(subj) - n + 1) if all(subj[j + t] in run[t] for t in range(n))]


def tactic(code, walk, run, subj, lo, mut, lower=False):
    """CAND per occurrence; with `lower` (G4 fails: S reads a group of P) the first non-empty walk's start
    is a LOWER bound handed to the ordinary search (D151's LOWER mapping, where_to_start.md section 2.2)"""
    for j in occurrences(subj, run, lo):
        s = walk.starts(subj, j, lo, mut)
        if s is None:
            continue
        if lower:
            return match(code, subj, s)
        m = match(code, subj, s, ANCHORED)
        if m:
            return m
    return None


def alphabet(walk, run, pat):
    al = set()
    for c in walk.classes + [frozenset(g["alph"]) for g in walk.segs]:
        cs = sorted(c)
        if cs:
            al.update(cs[:1] + cs[-1:] + cs[len(cs) // 2:len(cs) // 2 + 1])
    for r in run:
        al.update(r)
    al.update(b for b in pat if 32 <= b < 127)
    al.update(b"\n -.a0A_")
    return sorted(al)


def run_pop(rows, args, gated=True, muts=(None, "max_start", "no_ctx", "no_max"), nsub=None):
    rnd = random.Random(args.seed)
    nsub = nsub or args.subjects
    res = {m: collections.Counter() for m in muts}
    wit = {m: [] for m in muts}
    npat = 0
    for r, o in rows:
        flags = (CASELESS if r["icase"] else 0) | (MULTILINE if r["mline"] else 0)
        code = comp(r["pat"], flags)
        if not code:
            continue
        try:
            walk = Walk(o["_pit"], False)
        except R.Cap:
            continue
        npat += 1
        run = [set(x) for x in o["_run"]]
        al = alphabet(walk, run, r["pat"])
        lit = bytes(min(x) for x in run)
        for _ in range(nsub):
            n = rnd.randint(0, 28)
            subj = bytearray(rnd.choice(al) for _ in range(n))
            for _k in range(rnd.randint(1, 3)):
                p = rnd.randint(0, len(subj)); subj[p:p] = lit
            subj = bytes(subj)
            for lo in range(0, len(subj) + 1):
                truth = match(code, subj, lo)
                for m in muts:
                    got = tactic(code, walk, run, subj, lo, m, lower=o["srefs"])
                    res[m]["checks"] += 1
                    if got != truth:
                        res[m]["wrong"] += 1
                        if len(wit[m]) < 3:
                            wit[m].append("%s on %r lo=%d: truth %s, tactic %s" % (r["id"], subj, lo, truth, got))
    return npat, res, wit


EXTRA = [  # hand witnesses for the context, count and outer rules (the corpus holds few)
    rb"\B[a-z]+@x", rb"(?m)^[a-z]+@", rb"\b[a-z]+[0-9]*@", rb"[a-z]{2,4}@", rb"x?[a-z]{2,3}[0-9]@",
    rb"(?:ab)?[0-9]+@", rb"=[a-c][a-z]+@", rb"\bat (?:[a-z_][a-z0-9_]*\.){2,}[a-z_][a-z0-9_]*\(", rb"a*[0-9]{1,2}@",
    rb"(?:foo)?bar[0-9]*@", rb"\B[0-9]{2}@",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subjects", type=int, default=40)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    pop = T.corpus_pop() + T.bench_pop()
    adm, neg = [], []
    for r in pop:
        if r["enc"] != "byte":
            continue
        o = T.row_of(r, keep=True)
        if o.get("stage") != "landmark" or o.get("tier") not in ("T2", "T3") or o.get("_pit") is None:
            continue
        if o["strong"] and o["comp"]:
            adm.append((r, o))
        elif not o["strong"]:
            neg.append((r, o))
    extra = []
    for pat in EXTRA:
        r = dict(pop="extra", id="extra:" + pat.decode("latin-1"), enc="byte", icase=False, mline=pat.startswith(b"(?m)"), pat=pat)
        o = T.row_of(r, keep=True)
        if o.get("stage") == "landmark" and o.get("tier") in ("T2", "T3") and o["strong"] and o["comp"]:
            extra.append((r, o))
        else:
            print("EXTRA witness not admitted (check tiers.py): %s %s" % (pat, o.get("tier", o.get("stage"))))
    print("libpcre2 %s; seed %d; %d subjects per pattern, every startpos" % (version(), args.seed, args.subjects))
    n, res, wit = run_pop(adm, args)
    ne, rese, wite = run_pop(extra, args, nsub=args.subjects * 25)
    for m in res:
        res[m].update(rese[m]); wit[m] = (wite[m] + wit[m])[:3]
    print("ADMITTED T2/T3 (byte, single branch): %d corpus/bench patterns x %d subjects + %d hand witnesses x %d subjects"
          % (n, args.subjects, ne, args.subjects * 25))
    for m in res:
        print("  %-10s checks %d wrong %d%s" % (m or "tactic", res[m]["checks"], res[m]["wrong"],
                                                "" if m is None else ("  DETECTED" if res[m]["wrong"] else "  NOT DETECTED")))
        for w in wit[m]:
            print("      e.g. " + w)
    n2, res2, wit2 = run_pop(neg, args, muts=(None,))
    print("NEGATIVE CONTROL: chain, NO strong arm (ungated): %d patterns" % n2)
    print("  tactic     checks %d wrong %d%s" % (res2[None]["checks"], res2[None]["wrong"],
                                                  "  (the exclusion shown necessary here)" if res2[None]["wrong"] else
                                                  "  (exclusion NOT shown necessary on this population: reported, not gated)"))
    for w in wit2[None]:
        print("      e.g. " + w)
    ok = res[None]["wrong"] == 0 and all(res[m]["wrong"] for m in res if m)
    print("MODEL: %s" % ("PASS" if ok else "FAIL"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
