import ctypes, json, sys
lib=ctypes.CDLL("/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0")
lib.pcre2_compile_8.restype=ctypes.c_void_p
lib.pcre2_compile_8.argtypes=[ctypes.c_char_p,ctypes.c_size_t,ctypes.c_uint32,ctypes.POINTER(ctypes.c_int),ctypes.POINTER(ctypes.c_size_t),ctypes.c_void_p]
lib.pcre2_match_data_create_8.restype=ctypes.c_void_p
lib.pcre2_match_data_create_8.argtypes=[ctypes.c_uint32,ctypes.c_void_p]
lib.pcre2_match_8.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_void_p]
lib.pcre2_get_ovector_pointer_8.restype=ctypes.POINTER(ctypes.c_size_t)
lib.pcre2_get_ovector_pointer_8.argtypes=[ctypes.c_void_p]
buf=ctypes.create_string_buffer(64); lib.pcre2_config_8(11,buf); print("#version",buf.value.decode())
md=lib.pcre2_match_data_create_8(4,None)
cells=json.loads(sys.stdin.read()); ok=bad=0
for path,ln,pat,subj,want in cells:
    p=pat.encode('utf-8'); s=bytes.fromhex(subj)
    e,eo=ctypes.c_int(),ctypes.c_size_t()
    code=lib.pcre2_compile_8(p,len(p),0,ctypes.byref(e),ctypes.byref(eo),None)
    if not code: got="ERR%d"%e.value
    else:
        rc=lib.pcre2_match_8(code,s,len(s),0,0,md,None)
        if rc==-1: got=None
        elif rc<0: got="RC%d"%rc
        else:
            ov=lib.pcre2_get_ovector_pointer_8(md); got=[ov[0],ov[1]]
    if got==want: ok+=1
    else: bad+=1; print("DISAGREE",path,ln,pat,subj,want,got)
print("10.46 verify: %d agree, %d disagree"%(ok,bad))
