#!/usr/bin/env python3
"""classify_remote.py -- the same question as classify.c, asked in ONE
pcre2_substitute call per (pattern, mode): delete every character of an
all-code-points subject that does NOT match P, what remains is P's member
set.  Runs over ssh stdin (writes nothing on the remote box).  Pattern list
follows the marker line.  Output format equals classify.c's."""
import ctypes, ctypes.util, sys
lib = ctypes.CDLL(sys.argv[1] if len(sys.argv) > 1 else
                  (ctypes.util.find_library("pcre2-8") or "libpcre2-8.so.0"))
UTF, UCP, DOTALL = 0x00080000, 0x00020000, 0x00000020
SUB_GLOBAL, SUB_OVERFLOW_LENGTH = 0x100, 0x1000
lib.pcre2_compile_8.restype = ctypes.c_void_p
lib.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32,
                                ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
lib.pcre2_substitute_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t,
    ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t,
    ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t)]
buf = ctypes.create_string_buffer(64)
lib.pcre2_config_8(11, buf)  # PCRE2_CONFIG_VERSION
print("#version", buf.value.decode())
subj = "".join(chr(c) for c in range(0x110000) if not 0xD800 <= c <= 0xDFFF).encode("utf-8")
out = ctypes.create_string_buffer(len(subj) + 16)
for line in sys.stdin.read().split("\n"):
    if not line or line.startswith("#"): continue
    for name, opt in (("UTF", UTF), ("UTF|UCP", UTF | UCP)):
        pat = ("(?s)(?!(?:%s))." % line).encode()
        e, eo = ctypes.c_int(), ctypes.c_size_t()
        code = lib.pcre2_compile_8(pat, len(pat), opt, ctypes.byref(e), ctypes.byref(eo), None)
        if not code:
            print("%s\t%s\tCOMPILE-ERROR %d" % (line, name, e.value)); continue
        n = ctypes.c_size_t(len(out))
        rc = lib.pcre2_substitute_8(code, subj, len(subj), 0, SUB_GLOBAL, None, None, b"", 0, out, ctypes.byref(n))
        if rc < 0: print("%s\t%s\tSUBST-ERROR %d" % (line, name, rc)); continue
        cps = [ord(ch) for ch in out.raw[:n.value].decode("utf-8")]
        ivs, lo, prev = [], None, None
        for c in cps:
            if lo is None: lo = prev = c; continue
            if c == prev + 1 or (prev == 0xD7FF and c == 0xE000): prev = c; continue
            ivs.append("%X-%X," % (lo, prev)); lo = prev = c
        if lo is not None: ivs.append("%X-%X," % (lo, prev))
        print("%s\t%s\t%d\t%s" % (line, name, len(cps), "".join(ivs)))
