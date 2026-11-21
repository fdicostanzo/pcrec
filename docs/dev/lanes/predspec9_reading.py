# PCRE2's own reading (priority parse) of labels, read through the public API only (ctypes, libpcre2-8).
# Each pattern is matched against the WHOLE value (PCRE2_ANCHORED|PCRE2_ENDANCHORED), as a set position reads it.
# Search hits: the loop (?:.*?(X))* is UNROLLED into nested optionals, one capture group per iteration, so the final
# ovector holds every hit of the priority parse (no callouts, nothing abandoned is recorded).
import ctypes, re
L = ctypes.CDLL("libpcre2-8.so.0")
L.pcre2_compile_8.restype = ctypes.c_void_p
L.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
L.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
L.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_match_8.argtypes = [ctypes.c_char_p.__base__ if False else ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
L.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
L.pcre2_get_ovector_count_8.restype = ctypes.c_uint32
L.pcre2_get_ovector_count_8.argtypes = [ctypes.c_void_p]
ANCH, ENDANCH, UNSET = 0x80000000, 0x20000000, ctypes.c_size_t(-1).value
def m(pat, s):
    e, o = ctypes.c_int(), ctypes.c_size_t()
    code = L.pcre2_compile_8(pat.encode(), len(pat.encode()), 0, ctypes.byref(e), ctypes.byref(o), None)
    assert code, (pat, e.value)
    md = L.pcre2_match_data_create_from_pattern_8(code, None)
    rc = L.pcre2_match_8(code, s.encode(), len(s), 0, ANCH | ENDANCH, md, None)
    if rc < 0: return None
    ov = L.pcre2_get_ovector_pointer_8(md); n = L.pcre2_get_ovector_count_8(md)
    return [None if ov[2*i] == UNSET else (ov[2*i], ov[2*i+1]) for i in range(1, n)]
K = 6
def search_pat(x, mn):
    # mn mandatory iterations, then nested optionals up to K total: the unrolled (?:.*?(x)){mn,}
    req = "".join("(?:.*?(%s))" % x for _ in range(mn))
    opt = ""
    for _ in range(K - mn): opt = "(?:.*?(%s)%s)?" % (x, opt)
    return "(?s)" + req + opt + ".*"
def hits(x, s, mn):
    # groups of x itself (inner groups) are counted: the hit is the first group of each iteration's block
    inner = re.compile(x).groups
    g = m(search_pat(x, mn), s)
    if g is None: return "REJECTED"
    out = []
    for i in range(K):
        sp = g[i * (1 + inner)]
        if sp: out.append("%s@%d" % (s[sp[0]:sp[1]], sp[0]))
    return out
def pyhits(x, s, mn):
    r = re.fullmatch(search_pat(x, mn), s)
    if not r: return "REJECTED"
    inner = re.compile(x).groups; out = []
    for i in range(K):
        a, b = r.span(1 + i * (1 + inner))
        if a >= 0: out.append("%s@%d" % (s[a:b], a))
    return out
print("== search hits, min 0 and 1 (libpcre2 | python re as a second control)")
for x, s in [("ab(?:[xy])", "abx aby abx"), ("ab(?:[xy])", "xyz"), ("aa", "aaa"), ("^err", "err x err"), ("^err", "x err")]:
    for mn in (0, 1):
        print("x=%-12r value=%-14r min=%d  pcre2 %s | re %s" % (x, s, mn, hits(x, s, mn), pyhits(x, s, mn)))
print("== min 2 re-cuts the hits (x = aab|a on 'aab'); find-all control:", re.findall("aab|a", "aab"))
for mn in (0, 1, 2):
    print("x='aab|a' value='aab' min=%d  pcre2 %s | re %s" % (mn, hits("aab|a", "aab", mn), pyhits("aab|a", "aab", mn)))
print("== set-once ambiguous label: (?<a>\\d+)(?<b>\\d+) on 123")
g = m(r"(?<a>\d+)(?<b>\d+)", "123"); print("pcre2 a=%r b=%r" % ("123"[g[0][0]:g[0][1]], "123"[g[1][0]:g[1][1]]))
r = re.fullmatch(r"(?P<a>\d+)(?P<b>\d+)", "123"); print("re    a=%r b=%r" % (r["a"], r["b"]))
print("== contains body (?s).*X.* reads the argument's label at the RIGHTMOST occurrence")
g = m(r"(?s).*ab(?<g>[xy]).*", "abx aby"); print("pcre2 'abx aby' g=%r" % "abx aby"[g[0][0]:g[0][1]])
print("== endsWith body: greedy (?s).*X vs lazy (?s).*?X, label n = \\d+ on ab123")
for p in [r"(?s).*(?<n>\d+)", r"(?s).*?(?<n>\d+)"]:
    g = m(p, "ab123"); print("pcre2 %-20s n=%r" % (p, "ab123"[g[0][0]:g[0][1]]))
print("== extra rows: hit spans with the g label, and (?m)^err")
for x, s in [("ab([xy])", "abx aby abx"), ("(?m:^err)", "err\nerr x\nok")]:
    for mn in (0, 1):
        g = m(search_pat(x, mn), s); inner = re.compile(x).groups; out = []
        for i in range(K):
            sp = g[i*(1+inner)]
            if sp:
                t = "%s@%d" % (s[sp[0]:sp[1]], sp[0])
                if inner: gs = g[i*(1+inner)+1]; t += " g=" + s[gs[0]:gs[1]]
                out.append(t)
        print("x=%r value=%r min=%d pcre2 %s | re %s" % (x, s, mn, out, pyhits(x, s, mn)))
print("== a* on baa (nullable argument), min 0:", hits("a*", "baa", 0), "| re", pyhits("a*", "baa", 0), "| findall", re.findall("a*", "baa"))
