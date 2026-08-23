"""la_oracle.py -- the [M6.6.1] lane's shared oracle helpers.

BORROWS `../../backrefs_measurements/probes/br_oracle.py`, which in turn
borrows `../../eng_brep_measurements/probes/pcre2_ctypes.py`. Two levels of
borrowing rather than a copy, for the reason br_oracle.py states: a lane that
re-implements the binding it is checking cannot detect that the original
moved. Everything br_oracle exports (`compile`, `compile_err`, `version`,
`Code`, the option bits, `nametable`) is re-exported here unchanged.

It adds exactly THREE things this lane's questions need and no earlier lane
had:

  1. `set_max_varlookbehind(n)` / `compile_err_mvlb(pat, n)` --
     `pcre2_set_max_varlookbehind_8` on a COMPILE CONTEXT (PCRE2 >= 10.43).
     The lookbehind LENGTH RULE cannot be measured without it: 10.46 accepts
     a VARIABLE-length lookbehind up to a per-context cap whose DEFAULT is
     what the charter asks this lane to find. Probing only the default would
     report the cap as a property of the construct rather than of the
     context.

  2. `PCRE2_INFO_MAXLOOKBEHIND` -- the compiled pattern's own answer to "how
     far back can this pattern need to look", which is exactly the quantity
     §3's back-step and §5's prefilter both need and the only one PCRE2
     publishes. Read as a fact, never as a design input.

  3. `pyre(pat)` -- python 3.x `re` compiled or its error, so every cell in
     the construct table can carry BOTH oracles in one row and the D27
     goal-facts list (§7) is a projection of the same measurement rather
     than a second run.

Nothing here is pcrec: PCRE2 is the source of truth (D26).

SELFCHECK is behavioural, in br_oracle's own style: a wrong constant or a
missing symbol must announce itself rather than silently measure the wrong
feature. Probes print `la_oracle.SELFCHECK` in their header.
"""
import ctypes
import importlib.util
import os
import re as _pyre

_HERE = os.path.dirname(os.path.abspath(__file__))
_BR = os.path.normpath(os.path.join(
    _HERE, "..", "..", "backrefs_measurements", "probes", "br_oracle.py"))

_spec = importlib.util.spec_from_file_location("br_oracle", _BR)
br = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(br)

pcre2 = br.pcre2
_lib = br._lib

# Re-exports, so a probe imports ONE module.
version = br.version
compile_err = br.compile_err
compile = br.compile                                        # noqa: A001
Code = br.Code
PCRE2_CASELESS = br.PCRE2_CASELESS
PCRE2_DUPNAMES = br.PCRE2_DUPNAMES
PCRE2_MATCH_UNSET_BACKREF = br.PCRE2_MATCH_UNSET_BACKREF

# PCRE2_INFO_MAXLOOKBEHIND's numeric index, DERIVED BY SWEEP rather than
# quoted: this box has no pcre2.h (br_oracle.py's header says so), the value
# a reader would guess from the documentation's list order is 23, and 23 reads
# a DIFFERENT FIELD here -- it answered 0 for `(?<=abc)x`, which is the shape
# of a wrong-constant measurement that reports confidently. The sweep over
# indices 0..31 found exactly one index answering 3 / 0 / 2 for
# `(?<=abc)x` / `abc` / `(?<=ab)x`, and _selfcheck() re-asserts those three
# cells plus one that separates it from MINLENGTH on every import.
PCRE2_INFO_MAXLOOKBEHIND = 15

_HAVE_MVLB = hasattr(_lib, "pcre2_set_max_varlookbehind_8")
if _HAVE_MVLB:
    _lib.pcre2_compile_context_create_8.restype = ctypes.c_void_p
    _lib.pcre2_compile_context_create_8.argtypes = [ctypes.c_void_p]
    _lib.pcre2_compile_context_free_8.restype = None
    _lib.pcre2_compile_context_free_8.argtypes = [ctypes.c_void_p]
    _lib.pcre2_set_max_varlookbehind_8.restype = ctypes.c_int
    _lib.pcre2_set_max_varlookbehind_8.argtypes = [ctypes.c_void_p,
                                                   ctypes.c_uint32]


def compile_err_mvlb(pat, maxvlb, options=0):
    """compile_err(), but under a compile context whose max_varlookbehind is
    `maxvlb`. Returns None when it compiles, else (code, offset, msg).

    Raises RuntimeError when the runtime predates 10.43 -- a probe must not
    silently report the DEFAULT cap's answers as if it had set the cap."""
    if not _HAVE_MVLB:
        raise RuntimeError("libpcre2 has no pcre2_set_max_varlookbehind_8 "
                           "(needs >= 10.43); this cell cannot be measured")
    if isinstance(pat, str):
        pat = pat.encode("latin-1")
    ccontext = _lib.pcre2_compile_context_create_8(None)
    try:
        _lib.pcre2_set_max_varlookbehind_8(ccontext, maxvlb)
        errcode = ctypes.c_int(0)
        erroff = ctypes.c_size_t(0)
        code = _lib.pcre2_compile_8(pat, len(pat), options,
                                    ctypes.byref(errcode),
                                    ctypes.byref(erroff), ccontext)
        if code:
            _lib.pcre2_code_free_8(code)
            return None
        return (errcode.value, erroff.value, pcre2._errmsg(errcode.value))
    finally:
        _lib.pcre2_compile_context_free_8(ccontext)


def maxlookbehind(pat, options=0):
    """PCRE2's own PCRE2_INFO_MAXLOOKBEHIND for `pat`, in CHARACTERS.
    None when the pattern does not compile."""
    c = None
    try:
        c = br.compile(pat, options)
    except Exception:                                       # noqa: BLE001
        return None
    out = ctypes.c_uint32(0)
    rc = _lib.pcre2_pattern_info_8(c._code, PCRE2_INFO_MAXLOOKBEHIND,
                                   ctypes.byref(out))
    if rc != 0:
        return None
    return out.value


def search(pat, subj, start=0, options=0):
    """(span, groups) or None. `groups` is [(s,e), ...] for groups 1..N with
    (-1,-1) for an unset one, exactly the shape bref_oracle.py reports."""
    try:
        c = br.compile(pat, options)
    except Exception:                                       # noqa: BLE001
        return "ERR"
    r = c.search(subj, start)
    if r is None:
        return None
    return r


def pyre(pat):
    """(compiled, None) or (None, 'error text') for python3 `re`."""
    try:
        return (_pyre.compile(pat), None)
    except Exception as e:                                  # noqa: BLE001
        return (None, "%s: %s" % (type(e).__name__, e))


def pyre_search(pat, subj, start=0):
    """python's answer in the same vocabulary as search(): 'ERR', None, or
    (span, groups)."""
    c, err = pyre(pat)
    if err:
        return "ERR"
    m = c.search(subj, start)
    if m is None:
        return None
    return (m.span(),
            [m.span(i) for i in range(1, (c.groups or 0) + 1)])


def _selfcheck():
    problems = []
    # (1) the max_varlookbehind symbol, and that it actually gates.
    if not _HAVE_MVLB:
        problems.append("no pcre2_set_max_varlookbehind_8 (libpcre2 < 10.43): "
                        "the length-rule cells cannot be measured")
    else:
        # `(?<=a{1,4})` needs 4; a cap of 1 must REFUSE it and a cap of 4 must
        # accept it. If both answers are the same the setter did nothing and
        # every cap cell below would be reporting the default.
        lo = compile_err_mvlb(r"(?<=a{1,4})x", 1)
        hi = compile_err_mvlb(r"(?<=a{1,4})x", 4)
        if lo is None or hi is not None:
            problems.append(
                "pcre2_set_max_varlookbehind_8 does not gate as expected "
                "(cap1=%r cap4=%r)" % (lo, hi))
    # (2) PCRE2_INFO_MAXLOOKBEHIND: the index must read the field whose value
    # is 3 for `(?<=abc)x` and 0 for `abc`. A wrong index gives a wrong pair.
    cells = [(r"(?<=abc)x", 3), (r"abc", 0), (r"(?<=ab)x", 2),
             (r"(?<=abcde)x", 5)]
    got = [(p, maxlookbehind(p), want) for p, want in cells]
    if any(g != w for _, g, w in got):
        problems.append("PCRE2_INFO_MAXLOOKBEHIND index %d gives %r"
                        % (PCRE2_INFO_MAXLOOKBEHIND,
                           [(p, g, w) for p, g, w in got]))
    # `abc` answering 0 rather than 3 is what separates this index from
    # MINLENGTH, which is the field a one-cell check would confuse it with.
    # (3) the python side is really python's `re`, not a re-export of pcre2:
    # `(?<=a|bc)` is a PCRE2-legal pattern python REFUSES. If this passes,
    # `pyre` is bound to the wrong engine.
    if pyre(r"(?<=a|bc)x")[1] is None:
        problems.append("python `re` accepted (?<=a|bc) -- pyre is not python")
    if compile_err(r"(?<=a|bc)x") is not None:
        problems.append("libpcre2 REFUSED (?<=a|bc) -- oracle disagrees with "
                        "the premise the length-rule section is built on")
    return problems + br.SELFCHECK


SELFCHECK = _selfcheck()

if __name__ == "__main__":
    print("libpcre2:", version())
    print("has max_varlookbehind setter:", _HAVE_MVLB)
    print("selfcheck problems:", SELFCHECK or "none")
    print("maxlookbehind of (?<=abcd)x:", maxlookbehind(r"(?<=abcd)x"))
