import ctypes, ctypes.util
lib=ctypes.CDLL(ctypes.util.find_library('pcre2-8') or 'libpcre2-8.so.0')
lib.pcre2_compile_8.restype=ctypes.c_void_p
lib.pcre2_compile_8.argtypes=[ctypes.c_char_p,ctypes.c_size_t,ctypes.c_uint32,ctypes.POINTER(ctypes.c_int),ctypes.POINTER(ctypes.c_size_t),ctypes.c_void_p]
lib.pcre2_match_data_create_from_pattern_8.restype=ctypes.c_void_p
lib.pcre2_match_data_create_from_pattern_8.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
lib.pcre2_match_8.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_void_p]
lib.pcre2_substring_copy_byname_8.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.POINTER(ctypes.c_size_t)]
def get(pat,subj):
    e=ctypes.c_int(); o=ctypes.c_size_t()
    c=lib.pcre2_compile_8(pat.encode(),len(pat.encode()),0,ctypes.byref(e),ctypes.byref(o),None)
    md=lib.pcre2_match_data_create_from_pattern_8(c,None)
    sb=ctypes.create_string_buffer(subj.encode()); r=lib.pcre2_match_8(c,sb,len(subj),0,0xA0000000,md,None)
    if r<0: return 'NOMATCH'
    buf=ctypes.create_string_buffer(16); n=ctypes.c_size_t(16)
    rc=lib.pcre2_substring_copy_byname_8(md,b'h',buf,ctypes.byref(n))
    return (rc, buf.value)
for pat,s in [('(?J)(?<h>\\d)(?:;(?<h>\\d))?', '7;3'), ('(?J)(?<h>\\d)(?:;(?<h>\\d))?', '7'), ('(?J)(?:(?<h>\\d);)?(?<h>\\d)', '3')]:
    print(repr(pat), repr(s), get(pat,s))
