#!/usr/bin/env python3
"""bequiv.py [LIBPATH] -- is \\b exactly its lookaround spelling, per libpcre2?

Exhaustive over every string of length 0..MAXLEN on a targeted alphabet
(ASCII word/non-word, multibyte word characters of 2/3/4 bytes including Mn
and Pc members, multibyte non-word characters of 2/3/4 bytes), in three
modes (no flags = bytes, UTF, UTF|UCP).  For each (mode, subject) the set of
positions where the assertion holds is read off ONE global pcre2_substitute
that inserts a marker at every match; two spellings agree iff their marked
outputs are identical.  Writes nothing; runnable over ssh stdin."""
import ctypes, ctypes.util, itertools, sys, hashlib
lib = ctypes.CDLL(sys.argv[1] if len(sys.argv) > 1 else
                  (ctypes.util.find_library("pcre2-8") or "libpcre2-8.so.0"))
UTF, UCP = 0x00080000, 0x00020000
lib.pcre2_compile_8.restype = ctypes.c_void_p
lib.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
lib.pcre2_substitute_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t,
    ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t,
    ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t)]
buf = ctypes.create_string_buffer(64); lib.pcre2_config_8(11, buf)
print("#version", buf.value.decode())
ALPHA = ["a", "_", "5",            # ASCII word
         " ", "-",                 # ASCII non-word
         "é", "٣",       # 2-byte word: L, Nd
         "́",                 # 2-byte word under UCP only: Mn (combining acute)
         "日", "‿",       # 3-byte word: Lo, Pc (undertie)
         "\U00020000",             # 4-byte word: CJK ext B
         " ", "€",       # 2/3-byte non-word: NBSP (Zs), euro (Sc)
         "\U0001f600"]             # 4-byte non-word: So
MAXLEN = int(sys.argv[2]) if len(sys.argv) > 2 else 4
PAIRS = [("\\b", "(?:(?<=\\w)(?!\\w)|(?<!\\w)(?=\\w))"),
         ("\\B", "(?:(?<=\\w)(?=\\w)|(?<!\\w)(?!\\w))")]
out = ctypes.create_string_buffer(4096)
def comp(p, o):
    e, eo = ctypes.c_int(), ctypes.c_size_t()
    c = lib.pcre2_compile_8(p.encode(), len(p.encode()), o, ctypes.byref(e), ctypes.byref(eo), None)
    assert c, (p, e.value)
    return c
def marks(code, s):
    n = ctypes.c_size_t(len(out))
    rc = lib.pcre2_substitute_8(code, s, len(s), 0, 0x100, None, None, b"|", 1, out, ctypes.byref(n))
    assert rc >= 0, rc
    return out.raw[:n.value]
subjects = [ "".join(t).encode() for L in range(MAXLEN + 1) for t in itertools.product(ALPHA, repeat=L)]
print("#subjects", len(subjects), "alphabet", len(ALPHA), "maxlen", MAXLEN)
for mname, mopt in (("none", 0), ("UTF", UTF), ("UTF|UCP", UTF | UCP)):
    for prim, spell in PAIRS:
        a, b = comp(prim, mopt), comp(spell, mopt)
        diffs, h, holds = 0, hashlib.sha1(), 0
        for s in subjects:
            ma, mb = marks(a, s), marks(b, s)
            h.update(ma)
            holds += ma.count(b"|")
            if ma != mb:
                if diffs < 5: print("  DIFF", mname, prim, s, ma, mb)
                diffs += 1
        print("%s\t%s\tsubjects=%d\tpositions-holding=%d\tdisagreements=%d\tsha1(prim marks)=%s" % (
              mname, prim, len(subjects), holds, diffs, h.hexdigest()[:12]))
