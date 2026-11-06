"""cmp.py PCREC CASES.tsv -- pcrec (--emit-main + gcc -O1) vs libpcre2-8 10.46.
TSV: enc <TAB> pattern <TAB> subject-hex-or-text.  Subject 'hex:..' = bytes.
utf8: PCRE2_UTF|PCRE2_UCP|PCRE2_MATCH_INVALID_UTF.  Prints first-match spans."""
import ctypes, subprocess, sys, os, hashlib
L = ctypes.CDLL("/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0")
L.pcre2_compile_8.restype = ctypes.c_void_p
L.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
L.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
L.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_match_8.restype = ctypes.c_int
L.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t,
    ctypes.c_size_t, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
L.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
UTF, UCP, MIU = 0x00080000, 0x00020000, 0x04000000

def p2(enc, pat, subj):
    e = ctypes.c_int(); o = ctypes.c_size_t()
    opts = (UTF | UCP | MIU) if enc == "utf8" else 0
    pb = pat.encode()
    code = L.pcre2_compile_8(pb, len(pb), opts, ctypes.byref(e), ctypes.byref(o), None)
    if not code: return "ERR%d" % e.value
    md = L.pcre2_match_data_create_from_pattern_8(code, None)
    rc = L.pcre2_match_8(code, subj, len(subj), 0, 0, md, None)
    if rc < 0: return "nomatch"
    ov = L.pcre2_get_ovector_pointer_8(md)
    s = "(%d,%d)" % (ov[0], ov[1])
    caps = ["(%d,%d)" % (ov[2*i], ov[2*i+1]) if ov[2*i] != (1<<64)-1 else "-" for i in range(1, rc)]
    return s + ("" if not caps else "[" + " ".join(caps) + "]")

def pc(pcrec, enc, pat, subj, scratch):
    h = hashlib.sha1((enc + pat).encode()).hexdigest()[:12]
    c = os.path.join(scratch, h + ".c"); x = os.path.join(scratch, h)
    if not os.path.exists(x):
        r = subprocess.run([pcrec, "--features", "all", "-e", enc, "-p", "rx", "--emit-main", "-o", c,
                            "--pattern", pat], capture_output=True, text=True)
        if r.returncode: return "CERR:" + r.stderr.strip()[:60]
        subprocess.run(["gcc", "-O1", "-o", x, c], check=True)
    r = subprocess.run([x, subj], capture_output=True)
    out = r.stdout.decode(errors="replace").split()
    if out[:1] == ["match"]: return "(%s,%s)" % (out[1], out[2])
    return "nomatch"

pcrec, cases = sys.argv[1], sys.argv[2]
scratch = os.path.join(os.path.dirname(os.path.abspath(cases)), "bin")
os.makedirs(scratch, exist_ok=True)
for line in open(cases, encoding="utf-8"):
    if not line.strip() or line.startswith("#"): continue
    enc, pat, s = line.rstrip("\n").split("\t")
    subj = bytes.fromhex(s[4:]) if s.startswith("hex:") else s.encode()
    a = p2(enc, pat, subj); b = pc(pcrec, enc, pat, subj, scratch)
    print("%s\t%-28s\t%-12r\tpcre2=%s\tpcrec=%s\t%s" % (enc, pat, subj, a, b, "OK" if a.split("[")[0] == b else "DIFF"))
