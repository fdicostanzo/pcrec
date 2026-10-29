#!/usr/bin/env python3
"""Lane p1dsg (2026-10-29): the UNIQUE-START refinement of G4, checked against libpcre2.

Claim (report, "Admission table" row excl-cand): where S reads a group of P (G4 fails), one anchored
attempt per landmark hit at s*(j) = min starts(j) is still exact IF starts(j) never holds two
positions.  LF-E1's failure needs a second, larger member that succeeds where s* fails.

For R = P.L.S given as three texts, on random subjects at every startpos lo:
  tactic: for each occurrence j >= lo of L (ascending): starts(j) = { s in [lo, j] : P matches
          exactly subject[s:j] in context } (libpcre2, an ANCHORED end-pinned run of
          (?:P)(?<=\\A[\\s\\S]{j}) at s); if non-empty, ONE anchored libpcre2 run of R at min starts(j);
          its match is the answer.  None: NOMATCH.
  truth:  libpcre2's own unanchored search of R from lo.
The walk is never pcrec's: both components and the oracle are libpcre2, and the start-selection logic
under test (the per-hit min and the occurrence order) shares no code with libpcre2's search loop.
Rows marked unique must be 0 wrong; the NEGATIVE rows (starts not unique, S reads P) must be wrong at
least once, which shows the rule is load-bearing.  The max-start variant is reported, not gated
(on a unique row it cannot differ from the tactic).
Also counted: the largest |starts(j)| seen per row (a unique row must never exceed 1).
Env PCRE2_LIB (default the box's 10.46).  Usage: python3 unique_model.py [--subjects 400] [--seed 1]"""
import argparse, ctypes, os, random, sys

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
ANCHORED, MULTILINE = 0x80000000, 0x400
MD = LIB.pcre2_match_data_create_8(64, None)
_cache = {}


def comp(pat, opts=0):
    k = (pat, opts)
    if k not in _cache:
        e, o = ctypes.c_int(), SZ()
        c = LIB.pcre2_compile_8(pat, len(pat), opts, ctypes.byref(e), ctypes.byref(o), None)
        if not c:
            raise ValueError("compile %r" % pat)
        _cache[k] = c
    return _cache[k]


def match(code, subj, start, opts=0):
    rc = LIB.pcre2_match_8(code, subj, len(subj), start, opts, MD, None)
    if rc < 0:
        return None if rc == -1 else ("ERR", rc)
    ov = LIB.pcre2_get_ovector_pointer_8(MD)
    return tuple(ov[i] for i in range(2 * rc))


def version():
    buf = ctypes.create_string_buffer(64)
    LIB.pcre2_config_8(11, buf)
    return buf.value.decode()


# (P, L, S, flags, unique?) -- unique rows must be 0 wrong; non-unique rows with a reference into P
# are the NEGATIVE controls (LF-E1's shape) and must be wrong at least once.
ROWS = [
    (rb"\b(\w+)", b"=", rb"[^&]*&(?:[^&]*&)*\1=", 0, True),       # bench dup-param-detect
    (rb"\b(\w+)", b" ", rb"\1\b", 0, True),
    (rb"\b(\w+)", b"=", rb"\1", 0, True),
    (rb"\b([a-z]+)\d*", b"@", rb"\1", 0, True),
    (rb"^(\w+)", b":", rb".*\1", MULTILINE, True),
    (rb"([a-c]{2})", b"x", rb"\1", 0, True),                        # fixed width: unique by width
    (rb"\b(a+b*)", b"=", rb"\1a", 0, True),
    (rb"(\w+)", b" ", rb"\1", 0, False),                            # bench bak-1: NEGATIVE
    (rb"(a+)", b"X", rb"\1", 0, False),                             # LF-E1's witness: NEGATIVE
    (rb"(\w+)", b"=", rb"[^&]*&(?:[^&]*&)*\1=", 0, False),          # dup-param without \b: NEGATIVE
]


def run(args):
    rnd = random.Random(args.seed)
    print("libpcre2 %s; seed %d; %d subjects per row, every startpos" % (version(), args.seed, args.subjects))
    ok = True
    for P, L, S, fl, uniq in ROWS:
        R = b"(?:" + P + b")" + L + b"(?:" + S + b")"
        code = comp(R, fl)
        al = sorted(set(b"ab=&x X:@1-\n") | set(L)) + [ord("a")] * 8   # weighted toward runs of a
        checks = wrong = wrong_max = maxw = 0
        wit = []
        for _ in range(args.subjects):
            subj = bytearray(rnd.choice(al) for _ in range(rnd.randint(0, 16)))
            for _k in range(rnd.randint(1, 3)):
                p = rnd.randint(0, len(subj)); subj[p:p] = L
            subj = bytes(subj)
            occ = [j for j in range(len(subj) - len(L) + 1) if subj[j:j + len(L)] == L]
            for lo in range(len(subj) + 1):
                truth = match(code, subj, lo)
                got = got_max = None
                for j in occ:
                    if j < lo:
                        continue
                    pin = comp(b"(?:" + P + b")(?<=\\A[\\s\\S]{%d})" % j, fl)
                    st = [s for s in range(lo, j + 1) if match(pin, subj, s, ANCHORED)]
                    maxw = max(maxw, len(st))
                    if not st:
                        continue
                    if got is None:
                        m = match(code, subj, min(st), ANCHORED)
                        if m:
                            got = m
                    if got_max is None:
                        m = match(code, subj, max(st), ANCHORED)
                        if m:
                            got_max = m
                    if got is not None and got_max is not None:
                        break
                checks += 1
                if got != truth:
                    wrong += 1
                    if len(wit) < 2:
                        wit.append("%r lo=%d: truth %s, tactic %s" % (subj, lo, truth, got))
                if got_max != truth:
                    wrong_max += 1
        if uniq:
            good = wrong == 0 and maxw <= 1
        else:
            good = wrong > 0
        ok &= good
        print("%-4s %-8s R=%-44s checks %6d wrong %4d  max|starts| %d  max_start-mutant wrong %d"
              % ("ok" if good else "FAIL", "unique" if uniq else "NEGATIVE", R.decode(), checks, wrong, maxw, wrong_max))
        for w in wit:
            print("        e.g. " + w)
    print("UNIQUE MODEL: %s" % ("PASS" if ok else "FAIL"))
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--subjects", type=int, default=400)
    ap.add_argument("--seed", type=int, default=1)
    sys.exit(0 if run(ap.parse_args()) else 1)
