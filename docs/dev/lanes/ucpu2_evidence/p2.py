import ctypes, sys
LIB = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith(('.so.0','.dylib','.so')) else '/opt/homebrew/lib/libpcre2-8.dylib'
lib = ctypes.CDLL(LIB)
lib.pcre2_compile_8.restype = ctypes.c_void_p
lib.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
lib.pcre2_match_data_create_8.restype = ctypes.c_void_p
lib.pcre2_match_data_create_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
lib.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
lib.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
lib.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
md = lib.pcre2_match_data_create_8(32, None)
UTF=0x00080000; UCP=0x00020000; CASELESS=0x8; MIU=0x04000000
def oracle(opts, pat, subj, start=0):
    e, eo = ctypes.c_int(), ctypes.c_size_t()
    code = lib.pcre2_compile_8(pat, len(pat), opts, ctypes.byref(e), ctypes.byref(eo), None)
    if not code: return 'ERR%d' % e.value
    rc = lib.pcre2_match_8(code, subj, len(subj), start, 0, md, None)
    if rc == -1: return None
    if rc < 0: return 'RC%d' % rc
    ov = lib.pcre2_get_ovector_pointer_8(md)
    return (ov[0], ov[1])
