"""probe.py PCREC CASES.tsv -- one row per (pattern, subject): libpcre2-8 10.46
(ctypes) and pcrec (`-p rx` + a counting driver, gcc -O1), each reporting the
overall span, every capture group, the callout count and (libpcre2) the mark.
TSV: enc <TAB> pattern <TAB> subject ('hex:..' = bytes).  utf8 = UTF|UCP|
MATCH_INVALID_UTF.  pcrec compiles with --features all; a refused pattern
prints CERR (verbs are outside pcrec's scope: libpcre2-only rows).
Lane altrev2 (2026-11-05); extends altrev1_evidence/cmp.py with captures for
pcrec, callout counts and marks."""
import ctypes, subprocess, sys, os, hashlib, re
L = ctypes.CDLL("/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0")
L.pcre2_compile_8.restype = ctypes.c_void_p
L.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
L.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
L.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_match_context_create_8.restype = ctypes.c_void_p
L.pcre2_match_context_create_8.argtypes = [ctypes.c_void_p]
CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
L.pcre2_set_callout_8.restype = ctypes.c_int
L.pcre2_set_callout_8.argtypes = [ctypes.c_void_p, CB, ctypes.c_void_p]
L.pcre2_match_8.restype = ctypes.c_int
L.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t,
    ctypes.c_size_t, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
L.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
L.pcre2_get_ovector_count_8.restype = ctypes.c_uint32
L.pcre2_get_ovector_count_8.argtypes = [ctypes.c_void_p]
L.pcre2_get_mark_8.restype = ctypes.c_char_p
L.pcre2_get_mark_8.argtypes = [ctypes.c_void_p]
UTF, UCP, MIU = 0x00080000, 0x00020000, 0x04000000
UNSET = (1 << 64) - 1
NCALL = [0]
def _cb(block, data):
    NCALL[0] += 1
    return 0
CBF = CB(_cb)

def caps_str(pairs):
    return "[" + " ".join("-" if s < 0 else "(%d,%d)" % (s, e) for s, e in pairs) + "]" if pairs else ""

def p2(enc, pat, subj):
    e = ctypes.c_int(); o = ctypes.c_size_t()
    opts = (UTF | UCP | MIU) if enc == "utf8" else 0
    pb = pat.encode()
    code = L.pcre2_compile_8(pb, len(pb), opts, ctypes.byref(e), ctypes.byref(o), None)
    if not code: return "ERR%d" % e.value
    md = L.pcre2_match_data_create_from_pattern_8(code, None)
    mc = L.pcre2_match_context_create_8(None)
    L.pcre2_set_callout_8(mc, CBF, None)
    NCALL[0] = 0
    rc = L.pcre2_match_8(code, subj, len(subj), 0, 0, md, mc)
    mk = L.pcre2_get_mark_8(md)
    tail = " co=%d" % NCALL[0] + (" mark=%s" % mk.decode() if mk else "")
    if rc < 0: return "nomatch" + tail
    ov = L.pcre2_get_ovector_pointer_8(md)
    n = L.pcre2_get_ovector_count_8(md)
    pairs = [(-1, -1) if ov[2*i] == UNSET or i >= rc else (ov[2*i], ov[2*i+1]) for i in range(1, n)]
    return "(%d,%d)" % (ov[0], ov[1]) + caps_str(pairs) + tail

DRV = r'''
#include <stdio.h>
#include <string.h>
#include "%s.h"
static int ncall;
static ptrdiff_t co(const rx_ctx *c) { (void)c; ncall++; return 0; }
%s
int main(int argc, char **argv) {
    unsigned char b[512]; size_t n = 0; const char *h = argc > 1 ? argv[1] : "";
    for (; h[0] && h[1] && n < sizeof b; h += 2) { unsigned v; sscanf(h, "%%2x", &v); b[n++] = (unsigned char)v; }
    ptrdiff_t caps[RX_NCAPS][2];
    int rc = rx_search(b, n, 0, caps);
    if (rc == 1) {
        printf("(%%td,%%td)", caps[0][0], caps[0][1]);
        if (RX_NCAPS > 1) {
            printf("[");
            for (int i = 1; i < RX_NCAPS; i++) {
                if (caps[i][0] < 0) printf("%%s-", i > 1 ? " " : "");
                else printf("%%s(%%td,%%td)", i > 1 ? " " : "", caps[i][0], caps[i][1]);
            }
            printf("]");
        }
    } else if (rc == 0) printf("nomatch"); else printf("giveup%%d", rc);
    printf(" co=%%d\n", ncall);
    return 0;
}
'''

def pc(pcrec, enc, pat, subj, scratch):
    h = "p" + hashlib.sha1((enc + "\0" + pat).encode()).hexdigest()[:12]
    c = os.path.join(scratch, h + ".c"); x = os.path.join(scratch, h)
    if not os.path.exists(x):
        r = subprocess.run(["timeout", "60", pcrec, "--features", "all", "-e", enc, "-p", "rx", "-o", c,
                            "--pattern", pat], capture_output=True, text=True)
        if r.returncode: return "CERR:" + r.stderr.strip().replace("pcrec: ", "")[:70]
        hdr = open(os.path.join(scratch, h + ".h")).read()
        binds = re.findall(r"extern const rx_callout_ref (\w+);", hdr)
        defs = "\n".join("const rx_callout_ref %s = { co, 0 };" % b for b in binds)
        d = os.path.join(scratch, h + "_drv.c")
        open(d, "w").write(DRV % (h, defs))
        subprocess.run(["gcc", "-O1", "-I", scratch, "-o", x, c, d], check=True)
    r = subprocess.run(["timeout", "20", x, subj.hex()], capture_output=True)
    return r.stdout.decode(errors="replace").strip()

pcrec, cases = sys.argv[1], sys.argv[2]
scratch = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(cases)), "bin")
os.makedirs(scratch, exist_ok=True)
for line in open(cases, encoding="utf-8"):
    if not line.strip(): continue
    if line.startswith("#"): print(line.rstrip("\n")); continue
    enc, pat, s = line.rstrip("\n").split("\t")
    subj = bytes.fromhex(s[4:]) if s.startswith("hex:") else s.encode()
    a = p2(enc, pat, subj); b = pc(pcrec, enc, pat, subj, scratch)
    same = "CERR" if b.startswith("CERR") else ("OK" if a.split(" mark=")[0] == b else "DIFF")
    print("%s\t%-30s\t%-10r\tpcre2=%s\tpcrec=%s\t%s" % (enc, pat, subj, a, b, same))
