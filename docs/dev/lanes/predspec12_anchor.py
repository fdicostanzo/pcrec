# predspec12: the ONE anchoring rule (CF:1001-1024) checked on libpcre2-8 through its public API (ctypes) and on
# Python's `re` as a second engine. FILTER position = the value matched WHOLE (PCRE2_ANCHORED|PCRE2_ENDANCHORED;
# Python re.fullmatch); FINAL pattern = searched in the subject (no options; Python re.search). Library bodies are
# spliced as rev 12 writes them: contains/search = (?:(?s:.*?)(?<hit>(?:x))){min,}(?s:.*), startsWith = (?:x)(?s:.*),
# endsWith = (?s:.*?)(?:x), anchored = ^(?:x)$. Python spells PCRE's \z as \Z and (?<n>..) as (?P<n>..).
import ctypes, re
L = ctypes.CDLL("libpcre2-8.so.0")
L.pcre2_compile_8.restype = ctypes.c_void_p
L.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
L.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
L.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
L.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
ANCH, ENDANCH = 0x80000000, 0x20000000
def pcre(pat, s, whole):
    e, o = ctypes.c_int(), ctypes.c_size_t()
    code = L.pcre2_compile_8(pat.encode(), len(pat.encode()), 0, ctypes.byref(e), ctypes.byref(o), None)
    assert code, (pat, e.value)
    md = L.pcre2_match_data_create_from_pattern_8(code, None)
    rc = L.pcre2_match_8(code, s.encode(), len(s), 0, (ANCH | ENDANCH) if whole else 0, md, None)
    if rc < 0: return "no match"
    ov = L.pcre2_get_ovector_pointer_8(md)
    return "match (%d,%d)" % (ov[0], ov[1])
def py(pat, s, whole):
    p = pat.replace(r"\z", r"\Z").replace("(?<hit>", "(?P<hit>")
    r = re.fullmatch(p, s) if whole else re.search(p, s)
    return "match (%d,%d)" % r.span() if r else "no match"
S = lambda x, mn: "(?:(?s:.*?)(?<hit>(?:%s))){%d,}(?s:.*)" % (x, mn)
rows = [
  ("contains(/err$/)  filter", S("err$", 1), "err\n", True),
  ("contains(/err\\z/) filter", S(r"err\z", 1), "err\n", True),
  ("endsWith(\"err\")   filter", "(?s:.*?)(?:err)", "err\n", True),
  ("contains(/^err/)  filter", S("^err", 1), "x err", True),
  ("contains(/^err/)  filter", S("^err", 1), "err x", True),
  ("startsWith(\"err\") filter", "(?:err)(?s:.*)", "err x", True),
  ("/err$/ directly   filter", "err$", "err\n", True),
  ("/err$\\n/ directly filter", "err$\n", "err\n", True),
  ("anchored(/foo/)   filter", "^(?:foo)$", "foo", True),
  ("anchored(/foo/)   filter", "^(?:foo)$", "foo\n", True),
  ("/foo/ directly    filter", "foo", "foo\n", True),
  ("anchored(/foo/)   final ", "^(?:foo)$", "foo\n", False),
  ("/\\Afoo\\z/         final ", r"\A(?:foo)\z", "foo\n", False),
  ("anchored(/foo/)   final ", "^(?:foo)$", "xfoo", False),
  ("startsWith(\"5\") as /^5/ filter (rejected form)", "^5", "57", True),
  ("startsWith(\"5\") = /5.*/  filter", "(?:5)(?s:.*)", "57", True),
]
for name, pat, s, whole in rows:
    print("%-48s %-46r on %-9r pcre2: %-14s | re: %s" % (name, pat, s, pcre(pat, s, whole), py(pat, s, whole)))
