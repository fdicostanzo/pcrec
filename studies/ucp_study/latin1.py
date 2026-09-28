#!/usr/bin/env python3
"""latin1.py [LIBPATH] -- UCP WITHOUT UTF: which of the 256 bytes do \\w \\d
\\s and the caseless fold reach?  (What a (*UCP) under -e byte would owe.)"""
import ctypes, ctypes.util, sys
lib = ctypes.CDLL(sys.argv[1] if len(sys.argv) > 1 else (ctypes.util.find_library("pcre2-8") or "libpcre2-8.so.0"))
lib.pcre2_compile_8.restype = ctypes.c_void_p
lib.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
lib.pcre2_match_data_create_8.restype = ctypes.c_void_p
lib.pcre2_match_data_create_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
lib.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t,
    ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
buf = ctypes.create_string_buffer(64); lib.pcre2_config_8(11, buf); print("#version", buf.value.decode())
md = lib.pcre2_match_data_create_8(4, None)
UCP = 0x00020000
def members(pat, opt):
    e, eo = ctypes.c_int(), ctypes.c_size_t()
    c = lib.pcre2_compile_8(pat, len(pat), opt, ctypes.byref(e), ctypes.byref(eo), None)
    return [b for b in range(256) if lib.pcre2_match_8(c, bytes([b]), 1, 0, 0, md, None) >= 0]
for p in (rb"^\w$", rb"^\d$", rb"^\s$", rb"^[[:alpha:]]$", rb"^[[:punct:]]$"):
    for name, o in (("none", 0), ("UCP", UCP)):
        m = members(p, o)
        print("%-16s %-4s %3d  high(>=0x80): %s" % (p.decode(), name, len(m), " ".join("%02X" % b for b in m if b >= 0x80)[:200]))
fold = 0
for b in range(0x80, 0x100):
    pat = b"(?i)^\\x{%02x}$" % b
    fold += len([x for x in members(pat, UCP) if x != b])
print("UCP caseless: high bytes with a non-self fold partner (pairs counted from each side):", fold)
