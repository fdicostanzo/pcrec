#!/usr/bin/env python3
"""twin_rerun.py -- [UCP] U3 lane ucpu3b: the island hand-twin's correctness
set (studies/u3_island_twin/subjects.py: correctness() x cases(), 31,168
(subject, startpos) cases) re-run against the REAL build, every twin case.

    twin_rerun.py PCREC WORKDIR [CASE...]      (default: every case)

Each case's pattern is compiled by PCREC under `-e utf8 --features all`
((*UCP) prepended where the twin's flags carry UCP), linked with a small
driver, and every case's answer compared with the resolved libpcre2 under the
twin's flags (UTF|MATCH_INVALID_UTF, + UCP). An answer that is an EMPTY match
beside an ill-formed byte on either side is match_api.md §9.5's documented
divergence of pcrec's byte machines; such cells are COUNTED apart, never
passed silently. Prints one TSV row per case: case, route (RX_DFA_SCAN or
the engine), cases, differing, 9.5 cells. Writes only under WORKDIR.
"""
import ctypes
import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "studies", "u3_island_twin"))
import subjects as twin_subjects  # noqa: E402

CASES = {   # studies/u3_island_twin/check.py's PATTERNS, verbatim
    "c1": (r"[\x{100}-\x{2000}]+", "UTF|MIU"),
    "c3": (r"[\x{100}-\x{FFFF}]+", "UTF|MIU"),
    "nd": (r"\p{Nd}+", "UTF|MIU"),
    "l": (r"\p{L}+", "UTF|MIU"),
    "xwd": (r"\p{Xwd}+", "UTF|MIU"),
    "x1": (r"(?<=[\x{100}-\x{2000}])x", "UTF|MIU"),
    "x2": (r"(?<![\w\x{C0}-\x{24F}\x{370}-\x{52F}])[\w\x{C0}-\x{24F}\x{370}-\x{52F}]+(?![\w\x{C0}-\x{24F}\x{370}-\x{52F}])", "UTF|MIU"),
    "x3": (r"\b\w+\b", "UTF|UCP|MIU"),
    "x3b": (r"\b\p{Xwd}+\b", "UTF|UCP|MIU"),
}
F = {"UTF": 0x00080000, "UCP": 0x00020000, "MIU": 0x04000000}

DRIVER = r"""
#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include "a.h"
int main(void) {
    uint32_t h[2];
    static unsigned char buf[1 << 20];
    while (fread(h, 4, 2, stdin) == 2) {
        if (h[0] && fread(buf, 1, h[0], stdin) != h[0]) return 2;
        ptrdiff_t caps[64][2];
        int rc = rx_search(buf, h[0], h[1], caps);
        if (rc == 1) printf("1 %td %td\n", caps[0][0], caps[0][1]);
        else printf("%d\n", rc);
    }
    return 0;
}
"""


def lib_():
    lib = ctypes.CDLL("libpcre2-8.so.0")
    lib.pcre2_compile_8.restype = ctypes.c_void_p
    lib.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32,
                                    ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
    lib.pcre2_match_data_create_8.restype = ctypes.c_void_p
    lib.pcre2_match_data_create_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
    lib.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t,
                                  ctypes.c_size_t, ctypes.c_uint32, ctypes.c_void_p,
                                  ctypes.c_void_p]
    lib.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
    lib.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
    return lib


def bad_mask(s):
    bad = [False] * len(s)
    i = 0
    while i < len(s):
        b0 = s[i]
        ln = (1 if b0 < 0x80 else 2 if b0 & 0xE0 == 0xC0 else 3 if b0 & 0xF0 == 0xE0
              else 4 if b0 & 0xF8 == 0xF0 else 0)
        ok = False
        if ln and i + ln <= len(s):
            try:
                ok = len(s[i:i + ln].decode("utf-8")) == 1
            except UnicodeDecodeError:
                ok = False
        if ok:
            i += ln
        else:
            bad[i] = True
            i += 1
    return bad


def exempt(s, ans):
    f = ans.split()
    if len(f) != 3 or f[1] != f[2]:
        return False
    p = int(f[1])
    bad = bad_mask(s)
    return (p < len(s) and bad[p]) or (p > 0 and bad[p - 1])


def main():
    pcrec, work = sys.argv[1], sys.argv[2]
    want_cases = sys.argv[3:] or list(CASES)
    os.makedirs(work, exist_ok=True)
    with open(os.path.join(work, "drv.c"), "w") as f:
        f.write(DRIVER)
    lib = lib_()
    md = lib.pcre2_match_data_create_8(64, None)
    subs = twin_subjects.correctness()
    pairs = twin_subjects.cases(subs)
    print("case\troute\tcases\tdiffering\tmatch_api_9.5_cells")
    total_bad = 0
    for case in want_cases:
        pat, flags = CASES[case]
        opts = 0
        for k in flags.split("|"):
            opts |= F[k]
        full = ("(*UCP)" if opts & F["UCP"] else "") + pat
        err, off = ctypes.c_int(), ctypes.c_size_t()
        code = lib.pcre2_compile_8(pat.encode(), len(pat.encode()), opts,
                                   ctypes.byref(err), ctypes.byref(off), None)
        d = os.path.join(work, case)
        os.makedirs(d, exist_ok=True)
        r = subprocess.run([pcrec, "-p", "rx", "-e", "utf8", "--features", "all",
                            "--pattern", full, "-o", os.path.join(d, "a.c")],
                           capture_output=True, text=True)
        if r.returncode:
            print("%s\tREFUSED\t0\t0\t0\t%s" % (case, r.stderr.strip()))
            continue
        src = open(os.path.join(d, "a.c")).read()
        m = re.search(r'#define RX_DFA_SCAN "([^"]*)"', src)
        route = m.group(1) if m else re.search(r'#define RX_ENGINE "([^"]*)"', src).group(1)
        r = subprocess.run(["gcc", "-O1", "-I", d, "-o", os.path.join(d, "drv"),
                            os.path.join(work, "drv.c"), os.path.join(d, "a.c")],
                           capture_output=True, text=True)
        if r.returncode:
            print("%s\tGCC-FAILED\t0\t0\t0" % case)
            total_bad += 1
            continue
        blob = bytearray()
        want = []
        for i, sp in pairs:
            s = subs[i]
            blob += struct.pack("<II", len(s), sp) + s
            rc = lib.pcre2_match_8(code, s, len(s), sp, 0, md, None)
            if rc == -1:
                want.append("0")
            elif rc < 0:
                want.append("E%d" % rc)
            else:
                ov = lib.pcre2_get_ovector_pointer_8(md)
                want.append("1 %d %d" % (ov[0], ov[1]))
        r = subprocess.run([os.path.join(d, "drv")], input=bytes(blob), capture_output=True)
        got = r.stdout.decode().splitlines()
        nbad = nex = 0
        with open(os.path.join(d, "mismatch.txt"), "w") as mf:
            for (i, sp), w, g in zip(pairs, want, got):
                if w == g:
                    continue
                if exempt(subs[i], w) or exempt(subs[i], g):
                    nex += 1
                    continue
                nbad += 1
                mf.write("%r\t%d\tpcre2=%s\tpcrec=%s\n" % (subs[i], sp, w, g))
        if len(got) != len(pairs):
            nbad += abs(len(pairs) - len(got))
        total_bad += nbad
        print("%s\t%s\t%d\t%d\t%d" % (case, route, len(pairs), nbad, nex))
    return 1 if total_bad else 0


if __name__ == "__main__":
    sys.exit(main())
