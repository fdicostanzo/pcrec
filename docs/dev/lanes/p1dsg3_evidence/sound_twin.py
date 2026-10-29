#!/usr/bin/env python3
"""Lane p1dsg3 (2026-10-29): the per-hit tactic re-run on rev 2's CHANGED hit-stream rule (r5 SOUND-2:
every occurrence of L at or after search_from, OVERLAPPING occurrences included), with its control.

An independent model (libpcre2-8 only, shares no code with pcrec or with the r5 critics' drivers):
  hits      every j >= sf with subject[j:j+|L|] == L, ascending; `--nov` resumes after a hit instead
            (j += |L|), the sabotage the fact wording forbids;
  s*(j)     the smallest s in [sf, j] where (?:P)L matches EXACTLY subject[s:j+|L|] (pcre2 ANCHORED +
            ENDANCHORED on the subject cut at j+|L|): ML's walk floored at sf;
  verify    ONE anchored attempt of R at s*(j) (stage 1's G4: S reads no group of P);
  guard     G0 (never fires): pure per-hit, the reach guard's LOWER never taken.
find-all restarts at the previous match end (R is never nullable: L is non-empty). Truth: libpcre2
find-all of R. Exhaustive over every subject up to length N on the alphabet.
Usage: python3 -I sound_twin.py P L S ALPHABET N [--nov]"""
import itertools, sys
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import cells as C   # the ctypes binding and find-all (libpcre2-8)

ENDANCHORED = 0x20000000


def compile_(pat):
    import ctypes
    err, off = ctypes.c_int(), ctypes.c_size_t()
    code = C.lib.pcre2_compile_8(pat, len(pat), 0, ctypes.byref(err), ctypes.byref(off), None)
    assert code, pat
    return code, C.lib.pcre2_match_data_create_from_pattern_8(code, None)


def match_at(cm, subj, start, opts):
    code, md = cm
    rc = C.lib.pcre2_match_8(code, subj, len(subj), start, opts, md, None)
    if rc < 0:
        return None
    ov = C.lib.pcre2_get_ovector_pointer_8(md)
    return ov[0], ov[1]


def perhit(R, PL, L, subj, nov):
    out, sf = [], 0
    while sf <= len(subj):
        j, found = sf, None
        while True:
            j = subj.find(L, j)
            if j < 0:
                break
            cut = subj[:j + len(L)]
            s = next((s for s in range(sf, j + 1)
                      if match_at(PL, cut, s, C.ANCHORED | ENDANCHORED) is not None), None)
            if s is not None:
                m = match_at(R, subj, s, C.ANCHORED)
                if m is not None:
                    found = m
                    break
            j += len(L) if nov else 1
        if found is None:
            break
        out.append(found)
        sf = found[1]
    return out


def main():
    P, L, S, alpha, n = sys.argv[1].encode(), sys.argv[2].encode(), sys.argv[3].encode(), sys.argv[4].encode(), int(sys.argv[5])
    nov = "--nov" in sys.argv
    R = compile_(b"(?:" + P + b")" + L + S)
    PL = compile_(b"(?:" + P + b")" + L)
    subjects = wrong = matches = 0
    first = None
    for k in range(n + 1):
        for t in itertools.product(alpha, repeat=k):
            subj = bytes(t)
            truth = C.findall(b"(?:" + P + b")" + L + S, subj)
            got = perhit(R, PL, L, subj, nov)
            subjects += 1
            matches += len(truth)
            if got != truth:
                wrong += 1
                first = first or (subj, truth, got)
    print("R=(?:%s)%s%s L=%s alphabet=%s n<=%d stream=%s: subjects %d, truth matches %d, WRONG %d%s" % (
        P.decode(), L.decode(), S.decode(), L.decode(), alpha.decode(), n, "non-overlapping (sabotage)" if nov
        else "every occurrence", subjects, matches, wrong,
        "" if not first else "; first: %r pcre2 %s per-hit %s" % first))


if __name__ == "__main__":
    main()
