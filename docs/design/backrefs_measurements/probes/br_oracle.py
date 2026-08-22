"""br_oracle.py -- the [M6.5.1] lane's shared oracle helpers.

BORROWS `../../eng_brep_measurements/probes/pcre2_ctypes.py` rather than
carrying a second copy of the ctypes binding (the rule
`probe_z_oracle.py` set: a lane that re-implements the binding it is
checking cannot detect that the original moved).

It adds exactly TWO things that binding does not expose and that this
lane's questions need:

  1. `compile_err(pat, options)` -> (code, offset, message) or None.
     The octal-disambiguation question (charter (d)) is answered by
     PCRE2's COMPILE-TIME error NUMBER (115 "reference to non-existent
     subpattern" vs 164 "octal value greater than \\377" vs acceptance),
     and `Compiled.__init__` collapses every failure into one exception
     string. The number is the fact; the wording is D26 tier 3.

  2. `PCRE2_DUPNAMES` / `PCRE2_CASELESS` / `PCRE2_MATCH_UNSET_BACKREF`
     option bits, and `substring_nametable(code)` -- the name table
     libpcre2 builds, which charter (e) compares pcrec's own ruled
     `rx_info.groups` layout against.

Nothing here is pcrec: PCRE2 is the source of truth (D26).
"""
import ctypes
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_BINDING = os.path.normpath(os.path.join(
    _HERE, "..", "..", "eng_brep_measurements", "probes", "pcre2_ctypes.py"))

_spec = importlib.util.spec_from_file_location("pcre2_ctypes", _BINDING)
pcre2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pcre2)

_lib = pcre2._lib

# Compile-time option bits (pcre2.h, 8-bit build). Values are the documented
# stable ABI constants; each one is CHECKED at import by a behavioural probe
# below rather than trusted, because this box has no pcre2.h to read them
# from (the -dev package is absent -- pcre2_ctypes.py's own header says so).
PCRE2_CASELESS            = 0x00000008
PCRE2_DUPNAMES            = 0x00000040
PCRE2_MATCH_UNSET_BACKREF = 0x00000200

PCRE2_INFO_NAMECOUNT      = 17
PCRE2_INFO_NAMEENTRYSIZE  = 18
PCRE2_INFO_NAMETABLE      = 19

_lib.pcre2_pattern_info_8.restype = ctypes.c_int
_lib.pcre2_pattern_info_8.argtypes = [ctypes.c_void_p, ctypes.c_uint32,
                                      ctypes.c_void_p]


def version():
    return pcre2.version()


def compile_err(pat, options=0):
    """None if `pat` compiles under `options`; else (code, offset, msg)."""
    if isinstance(pat, str):
        pat = pat.encode("latin-1")
    errcode = ctypes.c_int(0)
    erroff = ctypes.c_size_t(0)
    code = _lib.pcre2_compile_8(pat, len(pat), options,
                                ctypes.byref(errcode), ctypes.byref(erroff),
                                None)
    if code:
        _lib.pcre2_code_free_8(code)
        return None
    return (errcode.value, erroff.value, pcre2._errmsg(errcode.value))


class Code:
    """A compiled pattern that keeps its raw handle, so pattern_info can be
    asked about it. Wraps pcre2_ctypes.Compiled for matching."""

    def __init__(self, pat, options=0):
        self.c = pcre2.Compiled(pat, options)

    @property
    def _code(self):
        return self.c._code

    def search(self, subject, start=0):
        return self.c.search(subject, start)

    def nametable(self):
        """[(number, name), ...] in libpcre2's OWN table order -- the thing
        charter (e) compares pcrec's ruled (name asc, number asc) layout
        against. Never sorted here: the order IS the measurement."""
        cnt = ctypes.c_uint32(0)
        siz = ctypes.c_uint32(0)
        ptr = ctypes.c_void_p(0)
        _lib.pcre2_pattern_info_8(self._code, PCRE2_INFO_NAMECOUNT,
                                  ctypes.byref(cnt))
        _lib.pcre2_pattern_info_8(self._code, PCRE2_INFO_NAMEENTRYSIZE,
                                  ctypes.byref(siz))
        _lib.pcre2_pattern_info_8(self._code, PCRE2_INFO_NAMETABLE,
                                  ctypes.byref(ptr))
        out = []
        if not ptr.value:
            return out
        base = ctypes.cast(ptr, ctypes.POINTER(ctypes.c_ubyte))
        for i in range(cnt.value):
            off = i * siz.value
            num = (base[off] << 8) | base[off + 1]
            name = bytearray()
            j = off + 2
            while base[j] != 0:
                name.append(base[j])
                j += 1
            out.append((num, bytes(name).decode("latin-1")))
        return out


def compile(pat, options=0):                        # noqa: A001
    return Code(pat, options)


def _selfcheck():
    """The option-bit values above are ASSERTED BEHAVIOURALLY, because a
    wrong constant would silently measure the wrong feature -- this lane's
    version of `probe_wswitch_alarm.sh` refusing to report zero when it
    compiled nothing."""
    problems = []
    # DUPNAMES: '(?<a>x)(?<a>y)' is error 143 without it and compiles with it.
    if compile_err(r"(?<a>x)(?<a>y)") is None:
        problems.append("duplicate names compile WITHOUT PCRE2_DUPNAMES?!")
    if compile_err(r"(?<a>x)(?<a>y)", PCRE2_DUPNAMES) is not None:
        problems.append("PCRE2_DUPNAMES bit 0x40 does not enable dupnames")
    # CASELESS: 'a' must match 'A' only with the bit.
    if compile(r"a").search("A") is not None:
        problems.append("'a' matched 'A' with no CASELESS?!")
    if compile(r"a", PCRE2_CASELESS).search("A") is None:
        problems.append("PCRE2_CASELESS bit 0x08 does not enable caseless")
    # MATCH_UNSET_BACKREF is a COMPILE option in PCRE2 (it changes what an
    # unset backref means); '(a)?\1' on '' must differ with the bit.
    off = compile(r"^(a)?\1$").search("")
    on = compile(r"^(a)?\1$", PCRE2_MATCH_UNSET_BACKREF).search("")
    if off is not None or on is None:
        problems.append(
            "PCRE2_MATCH_UNSET_BACKREF bit 0x200 does not behave as expected "
            "(off=%r on=%r)" % (off, on))
    return problems


SELFCHECK = _selfcheck()

if __name__ == "__main__":
    print("libpcre2:", version())
    print("selfcheck problems:", SELFCHECK or "none")
    print("nametable of (?<b>x)(?<a>y):",
          compile(r"(?<b>x)(?<a>y)").nametable())
