"""substr4 probe: libpcre2-8 10.46 pcre2_substitute under SUBSTITUTE_EXTENDED."""
import sys, ctypes as C
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../tests/subst/d27/lib'))
import ref_pcre2 as R
L = R.L
S_EXT = 0x200
L.pcre2_get_error_message_8.argtypes = [C.c_int, C.c_char_p, C.c_size_t]
def msg(rc):
    b = C.create_string_buffer(256); L.pcre2_get_error_message_8(rc, b, 256); return b.value.decode()
def sub(pat, tpl, subj, opts=S_EXT, copt=0):
    err, off = C.c_int(), R.SZ()
    code = L.pcre2_compile_8(pat, len(pat), copt, C.byref(err), C.byref(off), None)
    assert code, pat
    md = L.pcre2_match_data_create_from_pattern_8(code, None)
    buf = C.create_string_buffer(4096); ol = R.SZ(4096)
    rc = L.pcre2_substitute_8(code, subj, len(subj), 0, R.S_GLOBAL | R.S_OVF | opts, md, None, tpl, len(tpl), buf, C.byref(ol))
    L.pcre2_match_data_free_8(md); L.pcre2_code_free_8(code)
    if rc < 0: return 'ERR %d (%s) at %d' % (rc, msg(rc), ol.value)
    return '%r n=%d' % (buf.raw[:ol.value], rc)
def main():
    U = R.S_UNSET_EMPTY
    cases = [
     # unset / empty / set with :- and :+
     (b'(a)?b', b'[${1:-D}]', b'b ab'),
     (b'(a?)b', b'[${1:-D}]', b'b ab'),
     (b'(a)?b', b'[${1:+S:N}]', b'b ab'),
     (b'(a?)b', b'[${1:+S:N}]', b'b ab'),
     (b'(a)?b', b'[${1:+S}]', b'b ab'),
     (b'(?<n>a)?b', b'[${n:-D}|${n:+S:N}]', b'b ab'),
     # without colon
     (b'(a)?b', b'[${1-D}]', b'b ab'),
     (b'(a)?b', b'[${1+S:N}]', b'b ab'),
     (b'(a)?b', b'[${1:=D}]', b'b ab'),
     (b'(a)?b', b'[${1:?D}]', b'b ab'),
     # nesting
     (b'(a)?(c)?b', b'[${1:-$2}]', b'b cb ab'),
     (b'(a)?(c)?b', b'[${1:-${2:-z}}]', b'b cb ab'),
     (b'(a)?(c)?b', b'[${1:+<$1>:${2:+<$2>:none}}]', b'b cb ab'),
     (b'(a)?b', b'[${1:-x$$y}]', b'b'),
     # escapes inside text
     (b'(a)?b', b'[${1:-a\\:b\\}c}]', b'b'),
     (b'(a)?b', b'[${1:+x\\:y:z}]', b'b ab'),
     (b'(a)?b', b'[${1:-a:b}]', b'b'),
     (b'(a)?b', b'[${1:+a}b:c}]', b'b ab'),
     # unknown group
     (b'(a)?b', b'[${9:-D}]', b'b'),
     (b'(a)?b', b'[${9:+S:N}]', b'b'),
     (b'(a)?b', b'[${z:-D}]', b'b'),
     # unset plain under extended, with and without UNSET_EMPTY
     (b'(a)?b', b'[$1]', b'b'),
     # escapes
     (b'b', b'<\\n\\t\\x41\\x{42}\\101\\\\\\$>', b'abc'),
     (b'b', b'<\\a\\e\\f\\r\\0>', b'abc'),
     (b'b', b'<\\q>', b'abc'),
     (b'b', b'<\\Qa$1\\E>', b'abc'),
     (b'b', b'<\\o{101}\\cA\\N{U+41}>', b'abc'),
     (b'b', b'<\\1>', b'abc'),
     (b'(b)', b'<\\1|\\g1|\\g{1}>', b'abc'),
     # case forcing
     (b'(\\w+) (\\w+)', b'\\U$1\\E $2', b'hello world'),
     (b'(\\w+) (\\w+)', b'\\u$1 \\l$2', b'hello WORLD'),
     (b'(\\w+) (\\w+)', b'\\U$1 x \\L$2 Y\\E z', b'hello WORLD'),
     (b'(\\w+) (\\w+)', b'\\u\\L$1 \\l\\U$2', b'hELLO world'),
     (b'(\\w+) (\\w+)', b'\\L\\u$1 \\U\\l$2', b'hELLO world'),
     (b'(\\w+)', b'\\Uab${1:-x}cd', b'hello'),
     (b'(\\w+)?!', b'\\U${1:-def}', b'!'),
     (b'(\\w+)?!', b'\\U${1:+y$1:no}', b'hi!'),
     (b'(\\w+)', b'\\u', b'hello'),
     (b'(\\w+)', b'\\u\\u$1', b'hello'),
     (b'(\\w*)', b'\\u$1', b'1abc'),
     (b'(\\w+)', b'\\E$1', b'hello'),
     # \u then literal
     (b'(\\w+)', b'\\uxyz$1', b'hello'),
     # case on $$
     (b'(\\w+)', b'\\U$$', b'hello'),
    ]
    for p, t, s in cases:
        print('%-22r %-34r %-12r -> %s' % (p, t, s, sub(p, t, s)))
    print('--- UNSET_EMPTY')
    for p, t, s in [(b'(a)?b', b'[$1]', b'b'), (b'(a)?b', b'[${1:-D}]', b'b'), (b'(a)?b', b'[${9}]', b'b')]:
        print('%-22r %-34r %-12r -> %s' % (p, t, s, sub(p, t, s, S_EXT | U)))
    print('--- UTF case')
    for p, t, s in [(b'(\\w+)', '\\U$1'.encode(), 'straße ıx'.encode()),
                    (b'(.+)', '\\U$1'.encode(), 'straße ıx ǆ'.encode()),
                    (b'(.+)', '\\L$1'.encode(), 'Kİ'.encode()),
                    (b'(.+)', '\\u$1'.encode(), 'ǆx'.encode()),]:
        print('%-22r %-34r %-12r -> %s' % (p, t, s, sub(p, t, s, S_EXT, R.UTF)))


if __name__ == '__main__':
    main()
