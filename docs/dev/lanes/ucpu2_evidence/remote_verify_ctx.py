# Runs on the 10.46 reference box: reads cells (JSON on the line after the
# marker) and re-answers each with libpcre2, printing agree/disagree counts.
import ctypes, json, sys
LIB = sys.argv[1]
lib = ctypes.CDLL(LIB)
lib.pcre2_compile_8.restype = ctypes.c_void_p
lib.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
lib.pcre2_match_data_create_8.restype = ctypes.c_void_p
lib.pcre2_match_data_create_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
lib.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
lib.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
lib.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
vb = ctypes.create_string_buffer(64)
lib.pcre2_config_8(11, vb)
md = lib.pcre2_match_data_create_8(32, None)
cells = json.loads(sys.stdin.read().split('@@CELLS@@',1)[1])
agree = dis = 0
for c in cells:
    pat = bytes.fromhex(c['p']); subj = bytes.fromhex(c['s'])
    e, eo = ctypes.c_int(), ctypes.c_size_t()
    code = lib.pcre2_compile_8(pat, len(pat), c['o'], ctypes.byref(e), ctypes.byref(eo), None)
    if not code: got = 'ERR%d' % e.value
    else:
        rc = lib.pcre2_match_8(code, subj, len(subj), c['sp'], 0, md, None)
        if rc == -1: got = None
        elif rc < 0: got = 'RC%d' % rc
        else:
            ov = lib.pcre2_get_ovector_pointer_8(md); got = [ov[0], ov[1]]
    if got == c['w']: agree += 1
    else:
        dis += 1; print('DISAGREE', c, 'got', got)
print('libpcre2 %s: %d agree, %d disagree' % (vb.value.decode(), agree, dis))
