import ctypes, sys, os
exec(open('/tmp/ucpu1s/p2.py').read().split("md = lib")[0])
lib.pcre2_match_data_create_8.restype = ctypes.c_void_p
md = lib.pcre2_match_data_create_8(4, None)
def oracle(opts, pat, subj):
    e, eo = ctypes.c_int(), ctypes.c_size_t()
    code = lib.pcre2_compile_8(pat, len(pat), opts, ctypes.byref(e), ctypes.byref(eo), None)
    if not code: return 'ERR%d' % e.value
    rc = lib.pcre2_match_8(code, subj, len(subj), 0, 0, md, None)
    if rc == -1: return None
    if rc < 0: return 'RC%d' % rc
    ov = lib.pcre2_get_ovector_pointer_8(md)
    return (ov[0], ov[1])
def esc(b):
    out=''
    for c in b:
        if c == 0x22: out += '\\"'
        elif c == 0x5c: out += '\\\\'
        elif 0x20 <= c < 0x7f: out += chr(c)
        else: out += '\\x%02x' % c
    return '"'+out+'"'
def block(out, pat, enc, flags, feats, subjects, note=None):
    opts = 0
    if enc == 'utf8': opts |= 0x00080000
    if 'u' in flags: opts |= 0x00020000
    if 'i' in flags: opts |= 0x8
    pb = pat.encode('utf-8')
    if note: out.append('# ' + note)
    out.append('# pcre2-only')
    out.append('pattern ' + pat)
    if enc: out.append('encoding ' + enc)
    if flags: out.append('flags ' + flags)
    if feats: out.append('features ' + feats)
    for s in subjects:
        sb = s.encode('utf-8') if isinstance(s, str) else s
        r = oracle(opts, pb, sb)
        if r is None: out.append('n ' + esc(sb))
        elif isinstance(r, tuple): out.append('m %s %d %d' % (esc(sb), r[0], r[1]))
        else: raise SystemExit('oracle %s on %r %r' % (r, pat, sb))
    out.append('')
def perr(out, pat, enc, flags, feats, note):
    out.append('# ' + note)
    out.append('pattern ' + pat)
    if enc: out.append('encoding ' + enc)
    if flags: out.append('flags ' + flags)
    if feats: out.append('features ' + feats)
    out.append('perr'); out.append('')
