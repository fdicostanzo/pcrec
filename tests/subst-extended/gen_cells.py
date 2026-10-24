"""tests/subst-extended/gen_cells.py -- writes tests/subst-extended/cells.tsv
(see that directory's CLAUDE.md). Each `same` cell's EXPECT is
pcre2_substitute's own answer (libpcre2-8 10.46 by ctypes; EXTENDED, GLOBAL
when LIMIT is all, OVERFLOW_LENGTH, UNSET_EMPTY unless strict,
UTF|MATCH_INVALID_UTF under utf8); the other cells state their expectation
here by hand. argv[1] is the oracle store's case map, the source of the
whole-map cells' subjects.

Usage, from the repo root:
  python3 -I tests/subst-extended/gen_cells.py \
      oracle_store/libpcre2-10.46-utf/case-map.tsv > tests/subst-extended/cells.tsv
"""
import sys, ctypes as C
L = C.CDLL('libpcre2-8.so.0')
SZ = C.c_size_t
L.pcre2_compile_8.restype = C.c_void_p
L.pcre2_compile_8.argtypes = [C.c_char_p, SZ, C.c_uint32, C.POINTER(C.c_int), C.POINTER(SZ), C.c_void_p]
L.pcre2_match_data_create_from_pattern_8.restype = C.c_void_p
L.pcre2_match_data_create_from_pattern_8.argtypes = [C.c_void_p, C.c_void_p]
L.pcre2_substitute_8.restype = C.c_int
L.pcre2_substitute_8.argtypes = [C.c_void_p, C.c_char_p, SZ, SZ, C.c_uint32, C.c_void_p, C.c_void_p, C.c_char_p, SZ, C.c_char_p, C.POINTER(SZ)]
UTF, MIU, CASELESS = 0x80000, 0x04000000, 0x8
G, UE, OVF, EXT = 0x100, 0x400, 0x1000, 0x200

def p2(pat, tpl, subj, utf, strict, limit):
    err, off = C.c_int(), SZ()
    code = L.pcre2_compile_8(pat, len(pat), (UTF | MIU) if utf else 0, C.byref(err), C.byref(off), None)
    assert code, pat
    md = L.pcre2_match_data_create_from_pattern_8(code, None)
    buf = C.create_string_buffer(1 << 17); ol = SZ(1 << 17)
    o = OVF | EXT | (0 if strict else UE) | (G if limit == 'all' else 0)
    rc = L.pcre2_substitute_8(code, subj, len(subj), 0, o, md, None, tpl, len(tpl), buf, C.byref(ol))
    return rc, buf.raw[:ol.value]

def enc(b):
    o = []
    big = len(b) > 1000      # the whole-map cells: UTF-8 as is, a quarter the size
    for x in b:
        if x == 0x5C: o.append('\\\\')
        elif 0x20 <= x < 0x7F or (big and x >= 0x80): o.append(chr(x))
        else: o.append('\\x%02x' % x)
    return ''.join(o)

U = lambda s: s.encode('utf-8')
UPPER = b''.join(chr(int(l.split('\t')[0], 16)).encode('utf-8') for l in [])  # filled below

# (id, flags, pattern bytes, template bytes, tmpl prefix, strict, limit, subject bytes, expect|None, p2, label, reach)
cells = []
def same(cid, pat, tpl, subj, reach='-', utf=False, strict=False, limit='all', flags=None):
    cells.append((cid, flags or ('-e utf8' if utf else '-'), pat, tpl, 'utf8:ext:' if utf else 'ext:',
                  strict, limit, subj, None, 'same', '-', reach))
def fixed(cid, pat, tpl, subj, expect, p2, label, reach='-', utf=False, strict=False, limit='all', flags=None, pre=None):
    cells.append((cid, flags or ('-e utf8' if utf else '-'), pat, tpl, pre if pre is not None else ('utf8:ext:' if utf else 'ext:'),
                  strict, limit, subj, expect, p2, label, reach))

W = rb'(\w+)'
# ---- the case table's witnesses, subst_api.md §2¶13a ----
same('t1', W, rb'\Ua\ubc', b'x', 'casetable,S1531')
same('t2', W, rb'\L\uabc', b'x', 'casetable')
same('t3', W, rb'\u\U\Lab', b'x', 'casetable,S1530')
same('t4', W, rb'\u\Uab', b'x', 'casetable')
same('t5', W, rb'\l\Uab', b'x', 'casetable')
same('t6', W, rb'\U\uab', b'x', 'casetable')
same('t7', W, rb'\U\L\uab', b'x', 'casetable')
same('t8', W, rb'\Ua\Lb\ucd', b'x', 'casetable')
same('t9', W, rb'\UaB\EcD', b'x', 'casetable')
same('t10', W, rb'\u\E$1', b'hELLo', 'casetable')
same('t11', W, rb'\L\u$1', b'hELLo', 'casetable')
# ---- §2¶13b ----
W2 = rb'(\w+) (\w+)'
same('m1', W2, rb'\U$1\E $2', b'hello world')
same('m2', W2, rb'\U$1 x \L$2 Y\E z', b'hello WORLD')
same('m3', W2, rb'\u\L$1 \l\U$2', b'hELLO world')
same('m4', W2, rb'\L\u$1 \U\l$2', b'hELLO world')
same('m5', rb'(b)(c)?', rb'\u${2:-x}', b'abd', 'cond')
same('m6', rb'(b)(c)?', rb'${2:-\Ux}y', b'abd', 'cond')
same('m7', rb'(b)(c)?', rb'\U${2:+$2:\Ezz}y', b'abd', 'cond')
same('m8', rb'(b)', rb'\U\Qa$\E$1', b'abc')
# ---- more case corners (measured in the probes) ----
same('c1', rb'(b)', rb'\U\x61\Qbc\E', b'abc', 'esc')
same('c2', rb'(b)', rb'\u$$a', b'abc')
same('c3', rb'(b)(x?)', rb'[\u$2y]', b'abc', 'S1532')
same('c4', rb'(b)', rb'\u\u$1', b'abc')
same('c5', rb'(b)', rb'\u\l$1', b'abc')
same('c6', rb'(b)', rb'\Ua\E${1:+x\Uy:z}w', b'abc', 'cond')
same('c7', rb'b', rb'\U$`|$' + b"'" + rb'|$_|$&|$0', b'abc')
same('c8', rb'(?<nm>b)', rb'\U$nm${nm}\1', b'abc')
same('c9', rb'(.+)', rb'\U$1', b'ab\xe0\xc0Zq', 'S1537')
same('c10', rb'(.+)', rb'\L$1', b'AB\xe0\xc0zQ')
same('c11', rb'(b)', rb'\u${1:+:y}z', b'abc', 'cond')
same('c12', rb'(a)|(b)', rb'<${2:+\U$2:\l$1}>', b'xAaBby', 'cond')
same('c13', rb'(\w)', rb'\U$1\E-$1', rb'ab', '-', strict=True)
same('cdense', rb'a', rb'\U[$0]', b'xa' * 300)
# ---- utf8 case: the mapping, §2¶14 ----
same('u1', rb'(.+)', U(r'\U$1'), U('straße'), 'S1533,S1534', utf=True)
# every code point libpcre2 maps, from the oracle store's own case-map rows
# (oracle_store/libpcre2-10.46-utf/case-map.tsv), never from pcrec's table
cps = {}
for ln in open(sys.argv[1]):
    if ln.startswith('#'): continue
    f = ln.rstrip('\n').split('\t')
    cps[f[1]] = [int(x.split('>')[0], 16) for x in f[3].split()]
allcp = sorted(set(cps['upper']) | set(cps['lower']))
SUBJ = ''.join(chr(c) for c in allcp).encode('utf-8')
same('bup', rb'.+', U(r'\U$0'), SUBJ, 'bound,S1534', utf=True)
same('blow', rb'.+', U(r'\L$0'), SUBJ, 'bound', utf=True)
same('bone', rb'.', U(r'\u$0\l$0'), SUBJ, '-', utf=True)
same('btwo', rb'..', U(r'\L\u$0|\U\l$0'), SUBJ, '-', utf=True)
same('u2', rb'b', U(r'\u\x{e9}'), b'abc', 'esc', utf=True)
same('u3', rb'b', U(r'\Uß\Eß'), b'abc', '-', utf=True)
same('u4', rb'(.+)', U(r'\L$1'), U('ȺẞK') + b'I' + U('İ'), '-', utf=True)
same('u5', rb'(.+)', U(r'\u$1|\l$1'), U('ǆǄ'), '-', utf=True)
same('u6', rb'(.+)', U(r'\U$1'), U('ıǅ'), '-', utf=True)
same('u7', rb'(\S+)', U(r'\u\L$1'), U('éCOLE ÉCOLE'), '-', utf=True)
fixed('u8', rb'b', U(r'\Uß'), b'abc', 'a' + enc('ß'.encode()) + 'c:1', 'same', '-', '-', pre='ext:')
fixed('encbind', rb'(b)', rb'\U$1', b'abc', 'check:MISMATCH:-1', 'na', '-', 'S1539', flags='-e utf8', pre='ext:')
# ---- ill-formed UTF-8 under case forcing: pcrec's own (§2¶14a; libpcre2 crashes, §9 row 19) ----
fixed('ill1', rb'b', rb'\U$_', b'ab\xffc', 'out:aAB\\xffC\\xffc:1', 'na', '-', 'illcase', utf=True)
fixed('ill2', rb'a', rb'[\u$_]', b'\xffab', 'out:\\xff[\\xffab]b:1', 'na', '-', 'illcase', utf=True)
fixed('ill3', rb'(.)', rb'\U$' + b"'", b'c\xc3\xa0\xff', 'out:\\xc3\\x80\\xff\\xff\\xff:2', 'na', '-', 'illcase', utf=True)
# ---- conditionals, §2¶8-¶9 ----
same('k1', rb'(a)|(b)', rb'[${1:-x}${2:-y}]', b'ab', 'cond,S1535')
same('k2', rb'(a)|(b)', rb'[${1:+A$1:U}]', b'abc', 'cond,S1535')
same('k3', rb'(a)|(b)|c', rb'${1:+<$1>:${2:+<$2>:none}}', b'abc', 'cond,S1535')
same('k4', rb'(a)?b', rb'${1:-a:b}', b'b ab', 'cond')
same('k5', rb'(a)?b', rb'${1:+a:b:c}', b'b ab', 'cond')
same('k6', rb'(a)?b', rb'${1:-\Qa}b\E}', b'b ab', 'cond')
same('k7', rb'(a)?b', rb'${1:+a\Q:\Eb:c}', b'b ab', 'cond')
same('k8', rb'(a)?b', rb'${1:+\:a\:b:\:c}', b'b ab', 'cond')
same('k9', rb'(a)?b', rb'${1:-\}}', b'b ab', 'cond')
same('k10', rb'(a)?b', rb'${1:-{x}}', b'b ab', 'cond')
same('k11', rb'(a)?b', rb'${1:-$$}', b'b ab', 'cond')
same('k12', rb'(a)?b', rb'${01:-x}', b'b ab', 'cond')
same('k13', rb'b', rb'${0:-x}${0:+y:z}', b'abc', 'cond')
same('k14', rb'(?<n>a)?b', rb'${n:-x}${n:+y:z}', b'b ab', 'cond')
same('k15', rb'(a)?b', rb'${1:-}${1:+}${1:+:}|', b'b ab', 'cond')
same('k16', rb'(a)?b', rb'${1:-$_$`$' + b"'" + rb'$&}', b'xb ab', 'cond')
same('k17', rb'(a)?b', rb'\Q${1:-x}\E', b'b', 'cond')
same('k18', rb'(a)?(b)', rb'${1:-\U$2}x', b'b ab', 'cond')
same('k19', rb'(a)?(b)', rb'${1:+$1$2$1$2:-}', b'b ab', 'cond,S1535')
same('k20', rb'(a)|(b)', rb'${1:+x:y}', b'ab', 'cond', strict=True)
fixed('k21', rb'(a)|(b)|(c)', rb'${1:-$2}', b'c', 'rc:UNSET', 'rc:-55', 'subst_api.md 9 row 5: the same class (pcre2 -55)', 'cond', strict=True)
fixed('k22', rb'(a)|(b)|(c)', rb'\U${1:-$2}', b'aac', 'rc:UNSET', 'rc:-55', 'subst_api.md 9 row 5: the same class (pcre2 -55)', 'cond', strict=True)
nest10 = b'${1:+' * 10 + b'x' + b'}' * 10
same('nest10', rb'(a)?b', nest10, b'ab b', 'nest')
nest10b = b'${1:+a:' * 10 + b'x' + b'}' * 10
same('nest10b', rb'(a)?b', nest10b, b'ab b', 'nest')
# ---- escapes, §2¶10-¶12 ----
same('e1', rb'b', rb'[\x41\x4\o{101}\o{ 102 }\x{ 43 }\cA\ca\c[\c?\c1]', b'abc', 'esc')
same('e2', rb'b', rb'[\0\01\012\0123\08\0377]', b'abc', 'esc')
same('e3', rb'b', rb'[\a\b\e\f\n\r\t\v]', b'abc', 'esc')
same('e4', rb'b', rb'[\$\\\:\}\{\.\ ]', b'abc', 'esc')
same('e5', rb'(b)', rb'[\Qa$1\E\E\E\Qb]', b'abc', 'esc')
same('e6', rb'(b)(c)', rb'[\2\1]', b'abcd', 'esc')
same('e7', rb'b', U(r'[\x{100}\N{U+e9}\o{400}\x{0000000041}\N{U+0041}]'), b'abc', 'esc', utf=True)
same('e8', rb'b', rb'[\xe9\o{351}]', b'abc', 'esc')
same('e9', rb'b', U(r'[\xe9\o{351}\é]'), b'abc', 'esc', utf=True)
same('e10', rb'b', rb'[\c>\c \c~\c\]', b'abc', 'esc')
# ---- an escape's value binds the template to its encoding (§2¶5, review TPL-1) ----
for cid, tpl in (('x1', rb'<\xe9>'), ('x2', rb'<\x{e9}>'), ('x3', rb'<\x{100}>'),
                 ('x4', rb'<\N{U+41}>'), ('x5', rb'<\o{351}>')):
    fixed(cid, rb'(b)', tpl, b'ab', 'check:MISMATCH:-1', 'na', '-', 'encesc,S1580', pre='utf8:ext:')
fixed('x6', rb'(b)', rb'<\xe9>', b'ab', 'check:MISMATCH:-1', 'na', '-', 'encesc', flags='-e utf8', pre='ext:')
fixed('x7', rb'(b)', rb'<\x41\o{102}\cC>', b'ab', None, 'same', '-', 'encesc', pre='utf8:ext:')
fixed('x8', rb'(b)', rb'<\x41\o{102}\cC>', b'ab', None, 'same', '-', 'encesc', flags='-e utf8', pre='ext:')

out = ['# tests/subst-extended/cells.tsv -- module subst-extended\'s cells (subst_api.md',
       '# §2¶7-¶14a, §4¶7-¶8, §4¶14, §4¶22), in tests/subst/run_subst_tests.py\'s columns:',
       '# ID FLAGS PATTERN TEMPLATE STRICT LIMIT SUBJECT VARS EXPECT P2 LABEL REACH',
       '# Every `same` EXPECT is libpcre2-8 10.46\'s pcre2_substitute answer with',
       '# SUBSTITUTE_EXTENDED; the ill-formed-UTF-8 case cells are pcrec\'s own (P2 na:',
       '# libpcre2 crashes on them, §9 row 19).']
for (cid, flags, pat, tpl, pre, strict, limit, subj, expect, p2w, label, reach) in cells:
    if expect is None:
        rc, o = p2(pat, tpl, subj, '-e utf8' in flags, strict, limit)
        assert rc >= 0, (cid, rc)
        expect = 'out:%s:%d' % (enc(o), rc)
    elif expect.endswith(':1') and not expect.startswith(('out:', 'rc:', 'check:')):
        expect = 'out:' + expect
    elif expect.startswith('out:') and not expect.rsplit(':', 1)[-1].isdigit():
        expect += ':1'
    for x in (pat, tpl):
        assert b'\t' not in x and b'\n' not in x
    tp = pre + tpl.decode('latin-1')
    out.append('\t'.join([cid, flags, pat.decode('latin-1'), tp, 'strict' if strict else 'blank', limit,
                          enc(subj), '-', expect, p2w, label, reach]))
sys.stdout.buffer.write(('\n'.join(out) + '\n').encode('latin-1'))
