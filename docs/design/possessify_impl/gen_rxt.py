#!/usr/bin/env python3
"""Generate the tests/possessify/*.rxt expectations from BOTH oracles.

Expectations are never hand-written: each (pattern, subject) cell's span is
taken from python3 `re` AND from libpcre2 (via ctypes), and a cell the two
disagree on is REPORTED rather than silently resolved.
"""
import ctypes, ctypes.util, re, sys

lib = ctypes.CDLL(ctypes.util.find_library("pcre2-8") or "libpcre2-8.so.0")
lib.pcre2_compile_8.restype = ctypes.c_void_p
lib.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32,
                                ctypes.POINTER(ctypes.c_int),
                                ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
lib.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
lib.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
lib.pcre2_match_8.restype = ctypes.c_int
lib.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t,
                              ctypes.c_size_t, ctypes.c_uint32, ctypes.c_void_p,
                              ctypes.c_void_p]
lib.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
lib.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]


def pcre2_span(pat, subj, ngroups=None):
    """INSTRUMENT NOTE. pcre2_match returns the number of ovector PAIRS it
    filled, which is (highest participating group + 1) -- NOT the pattern's
    group count. Reading only `rc` pairs and stopping makes every trailing
    UNSET group vanish rather than read as unset, which showed up as seven
    phantom "oracle disagreements" on the first run of this generator. Groups
    at or beyond `rc` are unset, and the pattern's own group count is what
    says how many there are."""
    err = ctypes.c_int(); off = ctypes.c_size_t()
    code = lib.pcre2_compile_8(pat.encode(), len(pat.encode()), 0,
                               ctypes.byref(err), ctypes.byref(off), None)
    if not code:
        return "UNCOMPILABLE"
    md = lib.pcre2_match_data_create_from_pattern_8(code, None)
    b = subj.encode("latin-1")
    rc = lib.pcre2_match_8(code, b, len(b), 0, 0, md, None)
    if rc < 0:
        return None
    ov = lib.pcre2_get_ovector_pointer_8(md)
    total = (ngroups + 1) if ngroups is not None else (rc if rc > 0 else 1)
    out = []
    for i in range(total):
        if i >= rc or ov[2 * i] == ctypes.c_size_t(-1).value:
            out.append((-1, -1))
        else:
            out.append((ov[2 * i], ov[2 * i + 1]))
    return tuple(out)


def py_span(pat, subj):
    try:
        rx = re.compile(pat)
    except re.error:
        return "UNCOMPILABLE"
    m = rx.search(subj)
    if not m:
        return None
    out = [m.span(0)]
    for k in range(1, rx.groups + 1):
        s = m.span(k)
        out.append((-1, -1) if s == (-1, -1) else s)
    return tuple(out)


def esc(s):
    o = ""
    for ch in s:
        if ch == '"': o += '\\"'
        elif ch == "\\": o += "\\\\"
        elif ch == "\n": o += "\\n"
        elif ch == "\t": o += "\\t"
        elif 32 <= ord(ch) < 127: o += ch
        else: o += "\\x%02x" % ord(ch)
    return o


def emit(blocks, out):
    disagree = 0
    for header, pat, subjects in blocks:
        out.write("\n")
        for line in header:
            out.write("# " + line + "\n")
        out.write("pattern %s\n" % pat)
        for subj in subjects:
            p = py_span(pat, subj)
            try:
                ng = re.compile(pat).groups
            except re.error:
                ng = None
            q = pcre2_span(pat, subj, ng)
            # Compare only the whole-match span plus the groups both report.
            def norm(v):
                return v if v in (None, "UNCOMPILABLE") else tuple(v)
            span_only = False
            if norm(p) != norm(q):
                # §3.6's rule: a three-way disagreement is INVESTIGATED, not
                # filtered. If the two oracles agree on the SPAN and differ
                # only on a capture slot, the span is still a fact both
                # authorities assert and it stays; the slot is dropped with
                # the divergence recorded in the file, never silently.
                if (p not in (None, "UNCOMPILABLE") and
                        q not in (None, "UNCOMPILABLE") and p[0] == q[0]):
                    span_only = True
                    sys.stderr.write("SLOT-ONLY DISAGREEMENT %r on %r: py=%r pcre2=%r\n"
                                     % (pat, subj, p, q))
                else:
                    sys.stderr.write("ORACLE DISAGREEMENT %r on %r: py=%r pcre2=%r\n"
                                     % (pat, subj, p, q))
                    disagree += 1
                    continue
            if p == "UNCOMPILABLE":
                sys.stderr.write("both oracles refuse %r\n" % pat)
                continue
            if p is None:
                out.write('n "%s"\n' % esc(subj))
            else:
                out.write('m "%s" %d %d\n' % (esc(subj), p[0][0], p[0][1]))
                if span_only:
                    out.write("# ^ SPAN ONLY: the two oracles disagree on this\n"
                              "#   cell's group 1 (python %s, libpcre2 %s) and\n"
                              "#   this is the `(|a){m,n}` family [R24 S-F5]\n"
                              "#   measured as the one where they do. pcrec agreed\n"
                              "#   with libpcre2 on all 15,600 cells of that sweep,\n"
                              "#   so the slot is not pinned here rather than pinned\n"
                              "#   to whichever oracle was asked first.\n"
                              % (p[1:], q[1:]))
                else:
                    for k in range(1, len(p)):
                        out.write("g %d %d %d\n" % (k, p[k][0], p[k][1]))
    return disagree
