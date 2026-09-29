import ctypes
lib=ctypes.CDLL("/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0")
lib.pcre2_compile_8.restype=ctypes.c_void_p
lib.pcre2_compile_8.argtypes=[ctypes.c_char_p,ctypes.c_size_t,ctypes.c_uint32,ctypes.POINTER(ctypes.c_int),ctypes.POINTER(ctypes.c_size_t),ctypes.c_void_p]
lib.pcre2_match_data_create_8.restype=ctypes.c_void_p
lib.pcre2_match_data_create_8.argtypes=[ctypes.c_uint32,ctypes.c_void_p]
lib.pcre2_match_8.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_void_p]
buf=ctypes.create_string_buffer(64); lib.pcre2_config_8(11,buf)
md=lib.pcre2_match_data_create_8(4,None)
print("# PCRE2_UCP|PCRE2_CASELESS (no UTF) caseless partners of each byte; libpcre2 %s; pattern ^\\xHH$ anchored, all 256 subjects" % buf.value.decode())
for x in range(256):
    p=("^\\x%02x$"%x).encode()
    e,eo=ctypes.c_int(),ctypes.c_size_t()
    code=lib.pcre2_compile_8(p,len(p),0x00020000|0x8,ctypes.byref(e),ctypes.byref(eo),None)
    ys=[y for y in range(256) if y!=x and lib.pcre2_match_8(code,bytes([y]),1,0,0,md,None)>=0]
    if ys: print("%02x\t%s"%(x," ".join("%02x"%y for y in ys)))
