#!/usr/bin/env python3
"""p1build (docs/dev/lanes/p1build_evidence/): libpcre2 differential of one pattern over every subject up to length N on an alphabet
(plus optional extra subjects), find-all. Usage: lwdiff.py PCREC PATTERN ALPHABET N [pcrec flags...]
Prints: pattern, the artifact's DFA_SCAN stamp, subjects, wrong count, first wrongs."""
import ctypes, ctypes.util, itertools, os, re, struct, subprocess, sys
lib = ctypes.CDLL(ctypes.util.find_library("pcre2-8") or "libpcre2-8.so.0")
lib.pcre2_compile_8.restype = ctypes.c_void_p
lib.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32,
                                ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
lib.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
lib.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
lib.pcre2_match_8.restype = ctypes.c_int
lib.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t,
                              ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
lib.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
lib.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
ANCHORED, NOTEMPTY_ATSTART, UTF, CASELESS = 0x80000000, 0x8, 0x00080000, 0x8

def findall(code, md, subj):
    out, start, opts = [], 0, 0
    while start <= len(subj):
        rc = lib.pcre2_match_8(code, subj, len(subj), start, opts, md, None)
        if rc < 0:
            if opts:
                start, opts = start + 1, 0
                continue
            if rc != -1: out.append("E")
            break
        ov = lib.pcre2_get_ovector_pointer_8(md)
        s, e = ov[0], ov[1]
        out.append("%d,%d" % (s, e))
        start, opts = e, (NOTEMPTY_ATSTART | ANCHORED if s == e else 0)
    return " ".join(out)

def main():
    pcrec, pat, n = sys.argv[1], sys.argv[2], int(sys.argv[4])
    flags = sys.argv[5:]
    enc = "utf-8" if "utf8" in flags else "latin-1"
    alpha = [ch.encode(enc) for ch in sys.argv[3].encode("latin-1").decode("unicode_escape")]
    d = os.path.dirname(os.path.abspath(__file__))
    work = os.path.join(os.environ.get("PCREC_TMPDIR", "/var/tmp/pcrec-" + os.environ.get("USER", "x")),
                        "scratch", "lwdiff", "w%d" % os.getpid())
    os.makedirs(work, exist_ok=True)
    gen = os.path.join(work, "gen.c")
    r = subprocess.run([pcrec, "-p", "rx", "--features", "all", "-o", gen, "--pattern", pat] + flags, capture_output=True, timeout=120)
    if r.returncode:
        print("COMPILE-FAIL", pat, r.stderr.decode()[:200]); sys.exit(1)
    src = open(gen).read()
    scan = (re.search(r'#define RX_DFA_SCAN "([^"]*)"', src) or [0, "-"])[1]
    drv = os.path.join(work, "drv")
    subprocess.run(["gcc", "-O1", "-w", "-I", work, "-o", drv, os.path.join(d, "lwdiff_drv.c")], check=True, timeout=120)
    subjects = [b""]
    for L in range(1, n + 1):
        subjects += [b"".join(t) for t in itertools.product(alpha, repeat=L)]
    extra = os.environ.get("LW_EXTRA")
    if extra:
        subjects += [s.encode("latin-1").decode("unicode_escape").encode("latin-1") for s in extra.split("|")]
    inp = b"".join(struct.pack("<I", len(s)) + s for s in subjects)
    got = subprocess.run([drv], input=inp, capture_output=True, timeout=600).stdout.decode().split("\n")
    opts = (UTF if "utf8" in flags else 0) | (CASELESS if "-i" in flags else 0)
    err, off = ctypes.c_int(), ctypes.c_size_t()
    pb = pat.encode("latin-1") if "utf8" not in flags else pat.encode("utf-8")
    code = lib.pcre2_compile_8(pb, len(pb), opts, ctypes.byref(err), ctypes.byref(off), None)
    assert code, pat
    md = lib.pcre2_match_data_create_from_pattern_8(code, None)
    wrong = []
    for i, s in enumerate(subjects):
        want = findall(code, md, s)
        if got[i].strip() != want:
            wrong.append((s, got[i].strip(), want))
    print("%s\tscan=%s\tsubjects=%d\twrong=%d" % (pat, scan, len(subjects), len(wrong)))
    for w in wrong[:5]:
        print("  WRONG %r pcrec=[%s] pcre2=[%s]" % w)
    subprocess.run(["rm", "-rf", work])
    sys.exit(1 if wrong else 0)

main()
