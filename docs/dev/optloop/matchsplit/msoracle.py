#!/usr/bin/env python3
"""[MATCH-SPLIT] STEP-0 controls that share NO source with pcrec's analysis: libpcre2 10.46.

  C2  independent soundness -- every pattern the classifier says has NO free part: libpcre2's
      find-all over sampled subjects must report only matches that satisfy the pins of SOME live
      path (S: start 0; G: start == the call's search_from; LS: start 0 or after '\\n' and not at
      n; E: end n, or n-1 before a final '\\n'; LE: end at a '\\n' or n).  A violation = the
      classifier is wrong.
  C3  free-part identity -- the FREE text and the END text, compiled alone, must match (anchored
      at p) only where the full pattern matches (anchored at p): never a start the full pattern
      lacks.
  C-RT the unparse of the whole tree is language-identical to the original (anchored match spans
      at every position agree on the sampled subjects) -- what makes C3's texts meaningful.

    python3 msoracle.py ms_rows.tsv.gz [--seed N] [--subjects N]
"""
import csv, gzip, random, re, sys, os, collections
csv.field_size_limit(sys.maxsize)
sys.path.insert(0, "/home/pcrec/projects/pcrec/worktrees/mssurvey/docs/design/eng_brep_measurements/probes")
import ctypes
import pcre2_ctypes as P

L = P._lib
ANCHORED, UTF = 0x80000000, 0x00080000
_cc = {}


def comp(pat, utf):
    k = (pat, utf)
    if k not in _cc:
        try:
            _cc[k] = P.Compiled(pat, UTF if utf else 0)
        except P.Pcre2Error:
            _cc[k] = None
    return _cc[k]


def match_at(code, subj, start, opts):
    md = L.pcre2_match_data_create_from_pattern_8(code._code, None)
    try:
        rc = L.pcre2_match_8(code._code, subj, len(subj), start, opts, md, None)
        if rc < 0:
            return None if rc == P.PCRE2_ERROR_NOMATCH else "err"
        ov = L.pcre2_get_ovector_pointer_8(md)
        return (ov[0], ov[1])
    finally:
        L.pcre2_match_data_free_8(md)


def findall(code, subj):
    out, pos, n = [], 0, len(subj)
    while pos <= n:
        m = match_at(code, subj, pos, 0)
        if m is None or m == "err":
            break
        out.append((pos, m[0], m[1]))
        pos = m[1] + 1 if m[1] == m[0] else m[1]
    return out


def alphabet(pat, utf=False):
    s = set(" \nx")
    for ch in pat.decode("latin-1"):
        if ch.isalnum() or ch in " .,;:-_/#!\"'@=+*?":
            s.add(ch)
    if b"\\s" in pat or b"\\W" in pat: s |= set(" \t\n")
    if b"\\d" in pat: s |= set("0123456789")
    if b"\\w" in pat: s |= set("abcZ_9")
    if b"\\S" in pat or b"\\D" in pat: s |= set("ab1")
    s.discard("\x00")
    if utf:
        s = {c for c in s if ord(c) < 0x80}
    return sorted(s)


EDGE = [b"", b"\n", b" ", b"  ", b"x", b"x\n", b" x ", b"\n\n", b"a\nb", b" \n ", b"x \n", b"\nx"]


def subjects(pat, rng, k, utf=False):
    al = alphabet(pat, utf)
    out = list(EDGE)
    for _ in range(k):
        n = rng.randint(0, 12)
        out.append("".join(rng.choice(al) for _ in range(n)).encode("latin-1"))
    return out


def pins_ok(elem, s, e, p, subj):
    sp, ep = elem
    n = len(subj)
    if sp & 1 and s != 0: return False
    if sp & 2 and s != p: return False
    if sp & 4 and not (s == 0 or (subj[s - 1:s] == b"\n" and s < n)): return False
    if ep & 1 and not (e == n or (e == n - 1 and subj[n - 1:n] == b"\n")): return False
    if ep & 2 and e != n: return False
    if ep & 4 and not (e == n or subj[e:e + 1] == b"\n"): return False
    return True


def main():
    path = sys.argv[1]
    seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 1
    k = int(sys.argv[sys.argv.index("--subjects") + 1]) if "--subjects" in sys.argv else 120
    rng = random.Random(seed)
    rows = list(csv.DictReader(gzip.open(path, "rt"), delimiter="\t"))
    C = collections.Counter()
    bad = []
    print("libpcre2", P.version())
    for r in rows:
        if r["status"] != "ok" or r["refused"]:
            continue
        utf = r["enc"] == "utf8"
        pat = bytes.fromhex(r["pattern_hex"])
        full_pat = (b"(?i)" if r["icase"] == "True" else b"") + pat
        full = comp(full_pat, utf)
        if full is None:
            C["libpcre2-refuses-original"] += 1
            continue
        elems = [tuple(int(x) for x in e.split(":")) for e in r["elems"].split(";") if e]
        subj = None
        # C2: pin-only rows
        if r["mix"] not in ("F", "-") and "F" not in r["mix"].split("+") and int(r.get("kreset") or 0):
            C["c2-excluded-kreset"] += 1      # \\K moves the reported start: the classes talk about the attempt start
        elif r["mix"] not in ("F", "-") and "F" not in r["mix"].split("+"):
            C["c2-rows"] += 1
            subj = subjects(pat, rng, k, utf)
            viol = None
            seen_here = 0
            for attempt in range(4):          # rows that match nothing get more (and longer) subjects
                if attempt:
                    if seen_here:
                        break
                    subj = subjects(pat, rng, k * 4, utf)
                for sj in subj:
                    for (p, s, e) in findall(full, sj):
                        C["c2-matches"] += 1
                        seen_here += 1
                        elems_ = [(0, 1)] if "--selftest" in sys.argv else [(el[0], el[1]) for el in elems]
                        if not any(pins_ok(el_, s, e, p, sj) for el_ in elems_):
                            viol = (sj, p, s, e); break
                    if viol: break
                if viol: break
            C["c2-rows-with-a-match"] += 1 if seen_here else 0
            if viol:
                C["c2-violations"] += 1
                bad.append(("C2", r["id"], pat.decode("latin-1"), viol))
        # C3 / C-RT
        for key, lab in (("txtNP_hex", "c3-free"), ("txtE_hex", "c3-end"), ("txtA_hex", "c-rt")):
            t = bytes.fromhex(r[key]) if r.get(key) else b""
            if not t or (key != "txtA_hex" and r["mix"] in ("F",)):
                continue
            if key == "txtA_hex" and rng.random() > 0.2:
                continue
            sub = comp(t, utf)
            if sub is None:
                C[lab + "-libpcre2-refuses-text"] += 1
                continue
            C[lab + "-rows"] += 1
            subj = subj or subjects(pat, rng, k, utf)
            viol = None
            for sj in subj[:60]:
                for p in range(len(sj) + 1):
                    ms = match_at(sub, sj, p, ANCHORED)
                    mf = match_at(full, sj, p, ANCHORED)
                    if key == "txtA_hex":
                        if ms != mf:
                            viol = (sj, p, ms, mf); break
                    elif ms is not None and ms != "err" and mf is None:
                        viol = (sj, p, ms, mf); break
                    if ms is not None and ms != "err":
                        C[lab + "-hits"] += 1
                if viol: break
            if viol:
                C[lab + "-violations"] += 1
                bad.append((lab, r["id"], pat.decode("latin-1"), viol))
    for k_, v in sorted(C.items()):
        print("%-34s %d" % (k_, v))
    for b in bad[:40]:
        print("VIOLATION", b)


if __name__ == "__main__":
    main()
