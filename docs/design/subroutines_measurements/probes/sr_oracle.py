"""sr_oracle.py -- the [DD-14] lane's shared oracle helpers.

BORROWS `../../lookaround_measurements/probes/la_oracle.py`, which borrows
`../../backrefs_measurements/probes/br_oracle.py`, which borrows
`../../eng_brep_measurements/probes/pcre2_ctypes.py`. Three levels of
borrowing rather than a copy, for the reason br_oracle.py states first: a
lane that re-implements the binding it is checking cannot detect that the
original moved. Everything la_oracle exports (`compile`, `compile_err`,
`search`, `pyre`, `pyre_search`, `ngroups`, `maxlookbehind`, `version`, the
option bits) is re-exported here unchanged.

It adds exactly THREE things this lane's questions need and no earlier lane
had:

  1. `match_limits(pat, subj, start, depth=, match=, heap=)` -- a match under
     a MATCH CONTEXT whose depth/match/heap limits are set, returning the RAW
     pcre2_match return code on failure instead of collapsing it to None.
     The whole of §5's depth-capacity question is "what does PCRE2 do when a
     recursion runs deep", and `Compiled.search` RAISES on every negative rc
     other than NOMATCH -- so an unbounded recursion would come back as a
     python exception rather than as the measured code -53
     (PCRE2_ERROR_DEPTHLIMIT). A give-up must be a CELL, not a traceback.

  2. `callout_trace(pat, subj, start)` -- a `pcre2_set_callout` callback that
     records, at every `(?C1)` in the pattern, the CURRENT ovector, the
     current subject offset and PCRE2's own `callout_number`. This is the
     only instrument that can see the capture state DURING a call rather
     than after it, which is what separates "the callee never wrote the
     slots" from "the callee wrote them and the return restored them" --
     two hypotheses with the SAME after-the-fact measurement and completely
     different emitted code (§4.1).

  3. `depth_of(pat, subj)` -- the smallest `depth_limit` under which `pat`
     still matches `subj`, by bisection. PCRE2's depth limit is the only
     published proxy for "how deep did that recursion go", and §5's capacity
     ruling needs the SHAPE of that number in the subject, not one value.

Nothing here is pcrec: PCRE2 is the source of truth (D26).

SELFCHECK is behavioural, in br_oracle's and la_oracle's style: a wrong
constant or a symbol that silently does nothing must announce itself rather
than measure the wrong feature. la_oracle's own defect log is the reason --
two of its three added constants were wrong at the value a reader would take
from the documentation's list order. Probes print `sr_oracle.SELFCHECK` in
their header.
"""
import ctypes
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_LA = os.path.normpath(os.path.join(
    _HERE, "..", "..", "lookaround_measurements", "probes", "la_oracle.py"))

_spec = importlib.util.spec_from_file_location("la_oracle", _LA)
la = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(la)

br = la.br
pcre2 = la.pcre2
_lib = la._lib

# Re-exports, so a probe imports ONE module.
version = la.version
compile_err = la.compile_err
compile = la.compile                                        # noqa: A001
search = la.search
ngroups = la.ngroups
maxlookbehind = la.maxlookbehind
pyre = la.pyre
pyre_search = la.pyre_search
compile_err_mvlb = la.compile_err_mvlb
PCRE2_CASELESS = la.PCRE2_CASELESS
PCRE2_DUPNAMES = la.PCRE2_DUPNAMES
PCRE2_MATCH_UNSET_BACKREF = la.PCRE2_MATCH_UNSET_BACKREF

PCRE2_UNSET = pcre2.PCRE2_UNSET
PCRE2_ERROR_NOMATCH = -1

# The documented stable negative match-error codes this lane reads back. Each
# is ASSERTED BEHAVIOURALLY in _selfcheck() -- a wrong value here would turn
# "PCRE2 refused to go that deep" into an unexplained number.
PCRE2_ERROR_MATCHLIMIT = -47
PCRE2_ERROR_DEPTHLIMIT = -53
PCRE2_ERROR_HEAPLIMIT = -63

_lib.pcre2_match_context_create_8.restype = ctypes.c_void_p
_lib.pcre2_match_context_create_8.argtypes = [ctypes.c_void_p]
_lib.pcre2_match_context_free_8.restype = None
_lib.pcre2_match_context_free_8.argtypes = [ctypes.c_void_p]
_lib.pcre2_set_depth_limit_8.restype = ctypes.c_int
_lib.pcre2_set_depth_limit_8.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
_lib.pcre2_set_match_limit_8.restype = ctypes.c_int
_lib.pcre2_set_match_limit_8.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
_lib.pcre2_set_heap_limit_8.restype = ctypes.c_int
_lib.pcre2_set_heap_limit_8.argtypes = [ctypes.c_void_p, ctypes.c_uint32]


def _mk_context(depth=None, match=None, heap=None):
    mc = _lib.pcre2_match_context_create_8(None)
    if not mc:
        raise MemoryError("pcre2_match_context_create_8 failed")
    if depth is not None:
        _lib.pcre2_set_depth_limit_8(mc, depth)
    if match is not None:
        _lib.pcre2_set_match_limit_8(mc, match)
    if heap is not None:
        _lib.pcre2_set_heap_limit_8(mc, heap)
    return mc


def match_limits(pat, subj, start=0, depth=None, match=None, heap=None,
                 options=0):
    """('ERR', compile-error) | ('rc', n) for a negative pcre2_match return
    other than NOMATCH | None for no match | (span, groups).

    The point of this entry is that a GIVE-UP IS A VALUE. `Compiled.search`
    raises Pcre2Error on rc < 0 other than NOMATCH, so a recursion that blows
    the depth limit arrives as a traceback; here it arrives as
    ('rc', -53) and can sit in a table."""
    if isinstance(pat, str):
        patb = pat.encode("latin-1")
    else:
        patb = pat
    if isinstance(subj, str):
        subj = subj.encode("latin-1")
    errcode = ctypes.c_int(0)
    erroff = ctypes.c_size_t(0)
    code = _lib.pcre2_compile_8(patb, len(patb), options,
                                ctypes.byref(errcode), ctypes.byref(erroff),
                                None)
    if not code:
        return ("ERR", (errcode.value, erroff.value,
                        pcre2._errmsg(errcode.value)))
    mc = _mk_context(depth, match, heap)
    md = _lib.pcre2_match_data_create_from_pattern_8(code, None)
    try:
        rc = _lib.pcre2_match_8(code, subj, len(subj), start, 0, md, mc)
        if rc == PCRE2_ERROR_NOMATCH:
            return None
        if rc < 0:
            return ("rc", rc)
        ov = _lib.pcre2_get_ovector_pointer_8(md)
        npairs = rc if rc > 0 else 1
        pairs = [(ov[2 * i], ov[2 * i + 1]) for i in range(npairs)]
        groups = [None if s == PCRE2_UNSET else (s, e) for s, e in pairs[1:]]
        n = ngroups(pat, options) or 0
        while len(groups) < n:
            groups.append(None)
        return ((pairs[0][0], pairs[0][1]), groups[:n])
    finally:
        _lib.pcre2_match_data_free_8(md)
        _lib.pcre2_match_context_free_8(mc)
        _lib.pcre2_code_free_8(code)


def depth_of(pat, subj, lo=1, hi=100000, options=0):
    """The SMALLEST depth_limit under which `pat` still matches `subj`, by
    bisection, or None if it does not match even at `hi` (and 'nomatch' if it
    genuinely does not match at all).

    REACHABILITY GUARD: if the pattern matches at `lo` the answer is `lo` and
    the bisection measured nothing about depth -- the caller is told so by
    getting `lo` back and is expected to check it, and _selfcheck() pins a
    cell whose answer is strictly inside the interval."""
    top = match_limits(pat, subj, depth=hi, options=options)
    if isinstance(top, tuple) and top and top[0] == "ERR":
        return ("ERR", top[1])
    if top is None:
        return "nomatch"
    if isinstance(top, tuple) and top[0] == "rc":
        return ("rc", top[1])
    a, b = lo, hi
    while a < b:
        mid = (a + b) // 2
        r = match_limits(pat, subj, depth=mid, options=options)
        ok = not (r is None or (isinstance(r, tuple) and r and r[0] == "rc"))
        if ok:
            b = mid
        else:
            a = mid + 1
    return a


# ---- callouts -------------------------------------------------------------
#
# pcre2_callout_block's 8-bit layout, from pcre2.h's PCRE2_STRUCTURE_LIST.
# The FIELD OFFSETS are what matter and they are ASSERTED behaviourally in
# _selfcheck() (a pattern whose callout must report offset_vector[0..1] of a
# known group). A wrong offset here reads a neighbouring field and reports a
# confident wrong capture state, which is exactly la_oracle's MAXLOOKBEHIND
# defect one struct over.
class _CalloutBlock(ctypes.Structure):
    _fields_ = [
        ("version", ctypes.c_uint32),
        ("callout_number", ctypes.c_uint32),
        ("capture_top", ctypes.c_uint32),
        ("capture_last", ctypes.c_uint32),
        ("offset_vector", ctypes.POINTER(ctypes.c_size_t)),
        ("mark", ctypes.c_void_p),
        ("subject", ctypes.c_void_p),
        ("subject_length", ctypes.c_size_t),
        ("start_match", ctypes.c_size_t),
        ("current_position", ctypes.c_size_t),
        ("pattern_position", ctypes.c_size_t),
        ("next_item_length", ctypes.c_size_t),
        ("callout_string_offset", ctypes.c_size_t),
        ("callout_string_length", ctypes.c_size_t),
        ("callout_string", ctypes.c_void_p),
        ("callout_flags", ctypes.c_uint32),
    ]


_CALLOUT_FN = ctypes.CFUNCTYPE(ctypes.c_int,
                               ctypes.POINTER(_CalloutBlock),
                               ctypes.c_void_p)
_lib.pcre2_set_callout_8.restype = ctypes.c_int
_lib.pcre2_set_callout_8.argtypes = [ctypes.c_void_p, _CALLOUT_FN,
                                     ctypes.c_void_p]


def callout_trace(pat, subj, start=0, options=0, ncap=None, limit=4096):
    """Run `pat` against `subj` and return (result, trace), where `trace` is a
    list of one dict per callout FIRING, in firing order:

        {'n': callout_number, 'pos': current_position,
         'top': capture_top, 'caps': [(s,e)|None, ...]}

    `caps` is read from the LIVE offset_vector at the instant of the callout
    -- group 1..ncap, `None` for a pair PCRE2 has left unset. That is the
    only way to see what a called group's captures look like WHILE the call
    is running, which §4.1 needs and no after-the-fact measurement gives."""
    if isinstance(pat, str):
        patb = pat.encode("latin-1")
    else:
        patb = pat
    if isinstance(subj, str):
        subj = subj.encode("latin-1")
    if ncap is None:
        ncap = ngroups(pat, options) or 0
    errcode = ctypes.c_int(0)
    erroff = ctypes.c_size_t(0)
    code = _lib.pcre2_compile_8(patb, len(patb), options,
                                ctypes.byref(errcode), ctypes.byref(erroff),
                                None)
    if not code:
        return (("ERR", (errcode.value, erroff.value,
                         pcre2._errmsg(errcode.value))), [])
    trace = []

    def _cb(blkp, _data):
        b = blkp.contents
        if len(trace) < limit:
            ov = b.offset_vector
            top = b.capture_top
            caps = []
            for i in range(1, ncap + 1):
                if i < top:
                    s, e = ov[2 * i], ov[2 * i + 1]
                    caps.append(None if s == PCRE2_UNSET else (s, e))
                else:
                    caps.append(None)
            trace.append({"n": int(b.callout_number),
                          "pos": int(b.current_position),
                          "top": int(top),
                          "caps": caps})
        return 0

    cb = _CALLOUT_FN(_cb)
    mc = _lib.pcre2_match_context_create_8(None)
    _lib.pcre2_set_callout_8(mc, cb, None)
    md = _lib.pcre2_match_data_create_from_pattern_8(code, None)
    try:
        rc = _lib.pcre2_match_8(code, subj, len(subj), start, 0, md, mc)
        if rc == PCRE2_ERROR_NOMATCH:
            res = None
        elif rc < 0:
            res = ("rc", rc)
        else:
            ov = _lib.pcre2_get_ovector_pointer_8(md)
            npairs = rc if rc > 0 else 1
            pairs = [(ov[2 * i], ov[2 * i + 1]) for i in range(npairs)]
            groups = [None if s == PCRE2_UNSET else (s, e)
                      for s, e in pairs[1:]]
            while len(groups) < ncap:
                groups.append(None)
            res = ((pairs[0][0], pairs[0][1]), groups[:ncap])
        return (res, trace)
    finally:
        _lib.pcre2_match_data_free_8(md)
        _lib.pcre2_match_context_free_8(mc)
        _lib.pcre2_code_free_8(code)


def _selfcheck():
    problems = []

    # (1) SUBROUTINE CALLS EXIST AT ALL in this libpcre2 and python has none.
    # If either half of this is wrong every table below is measuring
    # something other than what it says.
    if compile_err(r"(a)(?1)") is not None:
        problems.append("libpcre2 refused (a)(?1) -- this build has no "
                        "subroutine calls and NOTHING in this lane is "
                        "measurable")
    if pyre(r"(a)(?1)")[1] is None:
        problems.append("python `re` ACCEPTED (a)(?1) -- pyre is not python")

    # (2) the depth limit really gates, and the error code is -53. A
    # recursion 5 deep must fail at depth 1 and succeed at a large depth.
    deep = match_limits(r"^(a(?1)?b)$", "aaabbb", depth=100000)
    shallow = match_limits(r"^(a(?1)?b)$", "aaabbb", depth=1)
    if not (isinstance(deep, tuple) and deep and deep[0] == (0, 6)):
        problems.append("(a(?1)?b) did not match aaabbb at depth 100000: %r"
                        % (deep,))
    if not (isinstance(shallow, tuple) and shallow
            and shallow[0] == "rc" and shallow[1] == PCRE2_ERROR_DEPTHLIMIT):
        problems.append("depth_limit=1 did not give PCRE2_ERROR_DEPTHLIMIT "
                        "(%d); got %r -- either the setter does nothing or "
                        "the code is wrong"
                        % (PCRE2_ERROR_DEPTHLIMIT, shallow))
    # and the match limit's code, from a different mechanism entirely.
    ml = match_limits(r"^(a+)+$", "a" * 24 + "b", match=1000)
    if not (isinstance(ml, tuple) and ml and ml[0] == "rc"
            and ml[1] == PCRE2_ERROR_MATCHLIMIT):
        problems.append("match_limit did not give PCRE2_ERROR_MATCHLIMIT "
                        "(%d); got %r -- the subject must be one the pattern "
                        "CANNOT match, or the cell measures a fast success"
                        % (PCRE2_ERROR_MATCHLIMIT, ml))
    # and the SAME cell at a huge match limit must reach the answer, or the
    # row above proves nothing about the LIMIT.
    ml_hi = match_limits(r"^(a+)+$", "a" * 18 + "b", match=100000000)
    if ml_hi is not None:
        problems.append("the match-limit control cell did not reach a plain "
                        "no-match at a huge limit: %r" % (ml_hi,))

    # (3) depth_of() lands STRICTLY INSIDE its interval on a cell whose
    # answer is known to be neither endpoint -- the reachability guard.
    d = depth_of(r"^(a(?1)?b)$", "aaabbb", lo=1, hi=100000)
    if not isinstance(d, int) or d <= 1 or d >= 100000:
        problems.append("depth_of bisection is vacuous: %r" % (d,))

    # (4) THE CALLOUT BLOCK'S FIELD OFFSETS. `(a)(?C1)b` on "ab" must fire
    # exactly one callout, at current_position 1, with group 1 = (0,1). A
    # wrong `offset_vector` offset reads a neighbouring pointer and either
    # segfaults or reports garbage; a wrong `current_position` reports a
    # plausible-looking wrong number, which is the dangerous half.
    res, tr = callout_trace(r"(a)(?C1)b", "ab")
    if not (isinstance(res, tuple) and res and res[0] == (0, 2)):
        problems.append("callout probe pattern did not match: %r" % (res,))
    if len(tr) != 1:
        problems.append("expected 1 callout firing, got %d" % len(tr))
    elif not (tr[0]["n"] == 1 and tr[0]["pos"] == 1
              and tr[0]["caps"] == [(0, 1)]):
        problems.append("callout block layout wrong: %r" % (tr[0],))
    # (4b) a SECOND cell that separates `current_position` from
    # `start_match` and `pattern_position` -- all three are size_t neighbours
    # and a one-field slip reads a plausible number. Here the three differ.
    res2, tr2 = callout_trace(r"a(b)(?C7)c", "xabc", start=0)
    if not (len(tr2) == 1 and tr2[0]["n"] == 7 and tr2[0]["pos"] == 3
            and tr2[0]["caps"] == [(2, 3)]):
        problems.append("callout separator cell wrong: %r" % (tr2,))

    return problems + la.SELFCHECK


SELFCHECK = _selfcheck()

if __name__ == "__main__":
    print("libpcre2:", version())
    print("selfcheck problems:", SELFCHECK or "none")
    print("depth_of ^(a(?1)?b)$ / aaabbb:",
          depth_of(r"^(a(?1)?b)$", "aaabbb"))
    print("callout_trace (a)(?C1)(?1)(?C2) / aa:",
          callout_trace(r"(a)(?C1)(?1)(?C2)", "aa"))
