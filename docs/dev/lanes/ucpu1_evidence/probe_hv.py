import ctypes
lib=ctypes.CDLL("/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0")
lib.pcre2_compile_8.restype=ctypes.c_void_p
lib.pcre2_compile_8.argtypes=[ctypes.c_char_p,ctypes.c_size_t,ctypes.c_uint32,ctypes.POINTER(ctypes.c_int),ctypes.POINTER(ctypes.c_size_t),ctypes.c_void_p]
lib.pcre2_match_data_create_8.restype=ctypes.c_void_p
lib.pcre2_match_data_create_8.argtypes=[ctypes.c_uint32,ctypes.c_void_p]
lib.pcre2_match_8.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_void_p]
buf=ctypes.create_string_buffer(64); lib.pcre2_config_8(11,buf)
print("# K72 probe: \\h and \\v under PCRE2_UTF (no UCP), libpcre2 %s; pattern ^\\h$ / ^\\v$ anchored" % buf.value.decode())
PCRE2_UTF=0x00080000
md=lib.pcre2_match_data_create_8(4,None)
def try1(pat, subj_utf8, label):
    p=pat.encode()
    e,eo=ctypes.c_int(),ctypes.c_size_t()
    code=lib.pcre2_compile_8(p,len(p),PCRE2_UTF,ctypes.byref(e),ctypes.byref(eo),None)
    if not code:
        print("%s ERR%d"%(label,e.value)); return
    rc=lib.pcre2_match_8(code,subj_utf8,len(subj_utf8),0,0,md,None)
    print("%s rc=%d"%(label,rc))
# U+3000 IDEOGRAPHIC SPACE (Zs), UTF-8: E3 80 80 -- pcrec's byte-set \h does not carry it
try1(r"^\h$", bytes.fromhex("e38080"), "h-U+3000")
# U+00A0 NO-BREAK SPACE, UTF-8: C2 A0 -- pcrec's \h DOES carry this one (Latin-1 range)
try1(r"^\h$", bytes.fromhex("c2a0"), "h-U+00A0")
# ordinary ASCII space and tab, should agree everywhere
try1(r"^\h$", b" ", "h-ASCII-space")
try1(r"^\h$", b"\t", "h-ASCII-tab")
# U+2028 LINE SEPARATOR, UTF-8: E2 80 A8 -- \v candidate
try1(r"^\v$", bytes.fromhex("e280a8"), "v-U+2028")
try1(r"^\v$", b"\n", "v-ASCII-LF")
