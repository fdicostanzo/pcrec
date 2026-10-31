#!/usr/bin/env python3
"""Lane p1dsg3 (2026-10-29): the rev-2 TEST CELLS' expectations, oracle-verified (libpcre2-8 10.46
find-all through ctypes, the reference oracle on this box), and each cell's stage-1 route read off
pcrec's own stamps at this tree's HEAD (one compile per cell).

A cell is (pattern, subject, flags). find-all is PCRE2's global iteration: after an empty match
retry at the same offset with NOTEMPTY_ATSTART|ANCHORED, else advance one character (byte here: no
cell is utf8). Usage: PCREC=build/pcrec python3 -I cells.py"""
import ctypes, ctypes.util, os, re, subprocess, sys, tempfile

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
lib.pcre2_config_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
ANCHORED, NOTEMPTY_ATSTART = 0x80000000, 0x00000008


def version():
    buf = ctypes.create_string_buffer(64)
    lib.pcre2_config_8(11, buf)   # PCRE2_CONFIG_VERSION
    return buf.value.decode()


def findall(pat, subj):
    err, off = ctypes.c_int(), ctypes.c_size_t()
    code = lib.pcre2_compile_8(pat, len(pat), 0, ctypes.byref(err), ctypes.byref(off), None)
    assert code, "pcre2 compile failed: %r" % pat
    md = lib.pcre2_match_data_create_from_pattern_8(code, None)
    out, start, opts = [], 0, 0
    while start <= len(subj):
        rc = lib.pcre2_match_8(code, subj, len(subj), start, opts, md, None)
        if rc < 0:
            if opts:
                start, opts = start + 1, 0
                continue
            break
        ov = lib.pcre2_get_ovector_pointer_8(md)
        s, e = ov[0], ov[1]
        out.append((s, e))
        start, opts = e, (NOTEMPTY_ATSTART | ANCHORED if s == e else 0)
    return out


def stamps(pat):
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
        out = os.path.join(td, "a.c")
        cmd = [os.environ["PCREC"], "-p", "rx", "--features", "all", "-o", out, "--pattern", pat.decode("latin-1")]
        rc = subprocess.run(cmd, capture_output=True, timeout=120).returncode
        src = open(out).read() if rc == 0 else ""
    g = lambda k: (re.search(r'#define RX_%s "([^"]*)"' % k, src) or [None, "-"])[1]
    return "%s/%s locate=%s next=%s match=%s" % (g("ENGINE"), g("VM_PREFILTER"), g("DFA_SCAN"),
                                                 g("DFA_PREFILTER"), g("DFA_MATCH"))


# (finding, pattern, subject, expected find-all, what the cell asserts)
CELLS = [
    ("SLOT-4", rb"(?![a-z]*b)[a-z]+@x", b"ba@x", [(1, 4)],
     "a VM-hybrid prefilter body declines at L1 `finisher-dfa` (PRE), before ML is built"),
    ("SLOT-4", rb"(?=[a-z]*b)[a-z]+@x$", b"ab@x", [(0, 4)],
     "a LOCATE row IS selected on a hybrid's CR_DFA body today (rev-end): why L1 must read the finisher"),
    ("SOUND-2", rb"[0-9]*aa[bc]", b"00000aaabb", [(6, 9)],
     "the hit stream carries OVERLAPPING occurrences; the non-overlapping sabotage answers NOMATCH"),
    ("SOUND-1", rb"((?:xy)?ab)=\1", b"xyab=aba", [(2, 7)],
     "stage 2 net: UNIQUE's reach is one-or-more steps; the one-step reading picks F1 and answers NOMATCH"),
    ("SLOT-1", rb'\b[a-z_][a-z0-9_]{0,31}="(?:[^"\\]|\\.)*"', b'k="v" ab="c\\"d"', [(0, 5), (6, 15)],
     "kv-quoted: L6 reads NEXT_cf = handoff, so the walk declines (`next-landmark`) in BOTH worlds"),
    ("A2 cell 4", rb"[a-z]+@(?:[a-z]+@)*[a-z]+!", b"a@" * 8, [],
     "the reach guard's witness (rev 1 cell 4), scaled down for the answer; the timing form is (a@)^65536"),
]


def main():
    print("# libpcre2-8 %s; pcrec %s" % (version(), os.environ["PCREC"]))
    print("# finding | pattern | subject | expected (pcre2 find-all) | pcrec stage-1 stamps | asserts")
    bad = 0
    for fid, pat, subj, want, what in CELLS:
        got = findall(pat, subj)
        ok = got == want
        bad += not ok
        print("%s | %s | %s | %s%s | %s | %s" % (fid, pat.decode("latin-1"), subj.decode("latin-1"), got,
                                                "" if ok else " (EXPECTED %s)" % want, stamps(pat), what))
    print("# cells %d, oracle disagreements with the stated expectation %d" % (len(CELLS), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
