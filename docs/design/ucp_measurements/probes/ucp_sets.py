#!/usr/bin/env python3
"""ucp_sets.py [LIBPATH] -- SET RELATIONS the [UCP] design rests on.

Each row names two patterns and a mode; both are reduced to their member
set over every code point (surrogates skipped) by ONE pcre2_substitute that
deletes every non-member (studies/ucp_study/classify_remote.py's method,
borrowed), then compared.  Prints sizes, EQUAL/DIFF and the first few
differing code points each way.  Writes nothing; runs over ssh stdin:
    ssh duxevents@100.69.121.107 python3 - /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0 < ucp_sets.py
A row whose two sides are EXPECTED to differ carries `expect=DIFF`; the
vacuity guard at the end reports any such row that came out EQUAL."""
import ctypes, ctypes.util, sys
lib = ctypes.CDLL(sys.argv[1] if len(sys.argv) > 1 else
                  (ctypes.util.find_library("pcre2-8") or "libpcre2-8.so.0"))
F = {"UTF": 0x00080000, "UCP": 0x00020000}
SUB_GLOBAL = 0x100
lib.pcre2_compile_8.restype = ctypes.c_void_p
lib.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
lib.pcre2_substitute_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t,
    ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t,
    ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t)]
buf = ctypes.create_string_buffer(64); lib.pcre2_config_8(11, buf)
print("#version", buf.value.decode())
SUBJ = "".join(chr(c) for c in range(0x110000) if not 0xD800 <= c <= 0xDFFF).encode("utf-8")
OUT = ctypes.create_string_buffer(len(SUBJ) + 16)
_cache = {}
def members(pat, mode):
    key = (pat, mode)
    if key in _cache: return _cache[key]
    opt = 0
    for f in mode.split("|"): opt |= F[f]
    p = ("(?s)(?!(?:%s))." % pat).encode()
    e, eo = ctypes.c_int(), ctypes.c_size_t()
    code = lib.pcre2_compile_8(p, len(p), opt, ctypes.byref(e), ctypes.byref(eo), None)
    if not code: r = "COMPILE-ERROR %d" % e.value
    else:
        n = ctypes.c_size_t(len(OUT))
        rc = lib.pcre2_substitute_8(code, SUBJ, len(SUBJ), 0, SUB_GLOBAL, None, None, b"", 0, OUT, ctypes.byref(n))
        r = ("SUBST-ERROR %d" % rc) if rc < 0 else frozenset(ord(ch) for ch in OUT.raw[:n.value].decode("utf-8"))
    _cache[key] = r; return r
ROWS = [
 # (mode, A, B, what, expect)
 ("UTF|UCP", r"[[:graph:]]", r"[^\p{Z}\p{C}]|(?![\x{61c}\x{180e}\x{2066}-\x{2069}])\p{Cf}", "[:graph:] formula", "EQ"),
 ("UTF|UCP", r"[[:print:]]", r"[^\p{Zl}\p{Zp}\p{C}]|(?![\x{61c}\x{2066}-\x{2069}])\p{Cf}", "[:print:] formula", "EQ"),
 ("UTF|UCP", r"[[:graph:]]", r"[^\p{Z}\p{C}]", "[:graph:] naive (control: Cf matters)", "DIFF"),
 ("UTF|UCP", r"[[:punct:]]", r"\p{P}|(?=[\x00-\x7f])\p{S}", "[:punct:] formula", "EQ"),
 ("UTF|UCP", r"[[:xdigit:]]", r"[0-9A-Fa-f\x{ff10}-\x{ff19}\x{ff21}-\x{ff26}\x{ff41}-\x{ff46}]", "[:xdigit:] formula", "EQ"),
 ("UTF|UCP", r"[[:cntrl:]]", r"\p{Cc}", "[:cntrl:]", "EQ"),
 ("UTF|UCP", r"[[:blank:]]", r"\h", "[:blank:]", "EQ"),
 ("UTF|UCP", r"[[:space:]]", r"\p{Xps}", "[:space:]", "EQ"),
 ("UTF|UCP", r"\s", r"\p{Xsp}", "\\s", "EQ"),
 ("UTF|UCP", r"[[:word:]]", r"\p{Xwd}", "[:word:]", "EQ"),
 ("UTF|UCP", r"\w", r"\p{Xwd}", "\\w", "EQ"),
 ("UTF|UCP", r"[[:alnum:]]", r"\p{Xan}", "[:alnum:]", "EQ"),
 ("UTF|UCP", r"[[:alpha:]]", r"\p{L}", "[:alpha:]", "EQ"),
 ("UTF|UCP", r"[[:digit:]]", r"\p{Nd}", "[:digit:]", "EQ"),
 ("UTF|UCP", r"\d", r"\p{Nd}", "\\d", "EQ"),
 ("UTF|UCP", r"[[:lower:]]", r"\p{Ll}", "[:lower:]", "EQ"),
 ("UTF|UCP", r"[[:upper:]]", r"\p{Lu}", "[:upper:]", "EQ"),
 # complements
 ("UTF|UCP", r"\W", r"[^\p{Xwd}]", "\\W is the complement", "EQ"),
 ("UTF|UCP", r"[\W]", r"\W", "[\\W] in a class", "EQ"),
 ("UTF|UCP", r"[^\w]", r"\W", "[^\\w]", "EQ"),
 ("UTF|UCP", r"[[:^alpha:]]", r"\P{L}", "[:^alpha:]", "EQ"),
 ("UTF|UCP", r"\D", r"\P{Nd}", "\\D", "EQ"),
 ("UTF|UCP", r"\S", r"[^\p{Xsp}]", "\\S", "EQ"),
 # caseless: which sets fold, which are inert
 ("UTF|UCP", r"(?i)[[:lower:]]", r"[[:lower:]]", "(?i) does NOT fold [:lower:] under UCP", "EQ"),
 ("UTF|UCP", r"(?i)[[:upper:]]", r"[[:upper:]]", "(?i) does NOT fold [:upper:] under UCP", "EQ"),
 ("UTF|UCP", r"(?i)\p{Ll}", r"\p{Ll}", "(?i) DOES fold \\p{Ll} (control)", "DIFF"),
 ("UTF|UCP", r"(?i)[^[:lower:]]", r"[^[:lower:]]", "(?i) negated [:lower:] also inert", "EQ"),
 ("UTF|UCP", r"(?i)\w", r"\w", "\\w fold-closed", "EQ"),
 ("UTF|UCP", r"(?i)\W", r"\W", "\\W fold-closed", "EQ"),
 ("UTF|UCP", r"(?i)[[:alpha:]]", r"[[:alpha:]]", "[:alpha:] fold-closed", "EQ"),
 ("UTF|UCP", r"(?i)[[:alnum:]]", r"[[:alnum:]]", "[:alnum:] fold-closed", "EQ"),
 ("UTF|UCP", r"(?i)[[:graph:]]", r"[[:graph:]]", "[:graph:] fold-closed", "EQ"),
 ("UTF|UCP", r"(?i)[[:punct:]]", r"[[:punct:]]", "[:punct:] fold-closed", "EQ"),
 ("UTF|UCP", r"(?i)[[:xdigit:]]", r"[[:xdigit:]]", "[:xdigit:] fold-closed", "EQ"),
 ("UTF|UCP", r"(?i)[[:lower:]x]", r"[[:lower:]xX]", "per-contribution: the x still folds", "EQ"),
 ("UTF|UCP", r"(?i)[\p{Ll}[:lower:]]", r"(?i)\p{Ll}", "union with \\p{Ll} folds that contribution", "EQ"),
 ("UTF", r"(?i)[[:lower:]]", r"[a-zA-Z]", "non-UCP (?i)[:lower:] = ASCII letters only", "EQ"),
 ("UTF", r"(?i)\w", r"[a-zA-Z0-9_]", "non-UCP (?i)\\w = ASCII only (no KELVIN)", "EQ"),
 # the partial-UCP knobs
 ("UTF|UCP", r"(?aW)\w", r"[A-Za-z0-9_]", "(?aW)\\w", "EQ"),
 ("UTF|UCP", r"(?aD)\d", r"[0-9]", "(?aD)\\d", "EQ"),
 ("UTF|UCP", r"(?aS)\s", r"[\t\n\x0b\f\r ]", "(?aS)\\s", "EQ"),
 ("UTF|UCP", r"(?aP)[[:alpha:]]", r"[A-Za-z]", "(?aP)[:alpha:]", "EQ"),
 ("UTF|UCP", r"(?aP)[[:word:]]", r"[A-Za-z0-9_]", "(?aP)[:word:]", "EQ"),
 ("UTF|UCP", r"(?aP)\w", r"\p{Xwd}", "(?aP) does not touch \\w", "EQ"),
 ("UTF|UCP", r"(?aW)[[:word:]]", r"\p{Xwd}", "(?aW) does not touch [:word:]", "EQ"),
 ("UTF|UCP", r"(?aT)[[:digit:]]", r"[0-9]", "(?aT)[:digit:]", "EQ"),
 ("UTF|UCP", r"(?aT)[[:xdigit:]]", r"[0-9A-Fa-f]", "(?aT)[:xdigit:]", "EQ"),
 ("UTF|UCP", r"(?aT)[[:alpha:]]", r"\p{L}", "(?aT) leaves [:alpha:] UCP", "EQ"),
 ("UTF|UCP", r"(?aD)[[:digit:]]", r"\p{Nd}", "(?aD) does not touch [:digit:]", "EQ"),
 ("UTF|UCP", r"(?a)\w", r"[A-Za-z0-9_]", "(?a)\\w", "EQ"),
 ("UTF|UCP", r"(?a)[[:alpha:]]", r"[A-Za-z]", "(?a)[:alpha:]", "EQ"),
 ("UTF|UCP", r"(?aW)(?-aW)\w", r"\p{Xwd}", "(?-aW) unsets", "EQ"),
 ("UTF|UCP", r"(?aW:\w)|\w", r"\p{Xwd}", "(?aW:...) is scoped", "EQ"),
 # an ASCII-restricted set folds by the ASCII fold only: no KELVIN / LONG S
 ("UTF|UCP", r"(?aW)(?i)\w", r"[A-Za-z0-9_]", "(?aW)(?i)\\w = ASCII, ASCII fold", "EQ"),
 ("UTF|UCP", r"(?aW)(?i)\w", r"[A-Za-z0-9_\x{212a}\x{17f}]", "(?aW)(?i)\\w: no KELVIN/LONG S", "DIFF"),
 ("UTF|UCP", r"(?aP)(?i)[[:lower:]]", r"[A-Za-z]", "(?aP)(?i)[:lower:] = ASCII-folded", "EQ"),
 ("UTF|UCP", r"(?aP)(?i)[[:lower:]]", r"[A-Za-z\x{212a}\x{17f}]", "(?aP)(?i)[:lower:]: no KELVIN/LONG S", "DIFF"),
 # UCP WITHOUT UTF is not reachable by this code-point probe (the subject is UTF-8); see ucp_points.py
]
bad = []
for mode, a, b, what, expect in ROWS:
    A, B = members(a, mode), members(b, mode)
    if isinstance(A, str) or isinstance(B, str):
        print("%-8s %-40s A=%s B=%s" % (mode, what, A if isinstance(A, str) else len(A), B if isinstance(B, str) else len(B))); continue
    eq = A == B
    res = "EQUAL" if eq else "DIFF  A-B=%d %s  B-A=%d %s" % (
        len(A - B), ",".join("%X" % c for c in sorted(A - B)[:6]),
        len(B - A), ",".join("%X" % c for c in sorted(B - A)[:6]))
    print("%-8s %-44s |A|=%-7d |B|=%-7d %s" % (mode, what, len(A), len(B), res))
    if (expect == "EQ") != eq: bad.append(what)
print("#rows %d, rows differing from the stated expectation: %d %s" % (len(ROWS), len(bad), bad))
