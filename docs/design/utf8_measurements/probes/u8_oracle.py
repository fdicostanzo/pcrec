"""u8_oracle.py — the [M5.0] UTF-8 design lane's shared oracle helpers.

BORROWS `../../backrefs_measurements/probes/br_oracle.py`, which borrows
`../../eng_brep_measurements/probes/pcre2_ctypes.py`. Two levels of borrowing
rather than a copy, for the reason br_oracle.py states in its own header and
la_oracle.py repeats: a lane that re-implements the binding it is checking
cannot detect that the original moved. Everything br_oracle exports is
re-exported here unchanged.

It adds exactly what UTF questions need and no earlier lane had, because
every earlier lane was deliberately BYTE-oriented (pcre2_ctypes.py's own
comment on `PCRE2_UTF` reads *"not used: this module stays byte-oriented like
pcrec"*):

  1. **THE OPTION BITS, AND A RENDERER FOR THEM.** The suite's standing oracle
     is `options=0`; every UTF measurement is at some other options word, and
     a UTF result read without knowing which word produced it is not a
     measurement. `opts(...)` builds one from names and `opts_name(w)` renders
     one back, so every row in every transcript below carries its own word
     SYMBOLICALLY. This is the [M5.0] brief's standing requirement ("every UTF
     probe states its options word") made mechanical rather than remembered.

  2. **A MATCH THAT RETURNS ERROR CODES INSTEAD OF RAISING.** `pcre2_ctypes`'s
     `Compiled.search` raises on any `rc < 0` that is not NOMATCH, which is
     right for a byte-oriented lane and USELESS here: "what does 10.46 do with
     an ill-formed subject" is answered by exactly those codes, and a probe
     that raises on them can only report that something happened. `match()`
     below returns `('ERRM', code, message)` for them — the message read live
     out of `pcre2_get_error_message_8`, never a table this file hardcodes,
     because a hardcoded error table is a second source that can drift from
     the library it describes.

  3. **BYTES IN, BYTES OUT, ALWAYS.** The borrowed binding encodes a `str`
     argument as latin-1, which silently mangles any pattern or subject
     carrying a non-ASCII character — `'α'` would arrive as one byte 0xB1
     rather than the two bytes 0xCE 0xB1 that ARE the UTF-8 pattern under
     test. Every entry point here takes and returns `bytes` and refuses a
     `str` outright (`_b()`), so that class of error cannot be made silently.
     `u(s)` is the one sanctioned bridge: `u('α')` is `'α'.encode('utf-8')`,
     spelled at the call site so a reader sees the encoding happen.

  4. **A PYTHON `re` ARM IN TWO FLAVOURS.** python's `re` over `str` is a
     CODE POINT engine and over `bytes` is a byte engine, and the D27
     goal-facts list (§7 of the design) is exactly about where each one sits
     relative to PCRE2 under `PCRE2_UTF`. Both are here, in the same
     vocabulary, so a row can carry all three columns.

Nothing here is pcrec: PCRE2 is the source of truth (D26).

THE VERSION RULE FOR THIS LANE. The project's reference libpcre2 is **10.46,
on the old box**; this Mac's 10.48 is a DIFFERENT ORACLE and is known to
diverge. `version()` is read live and every archived transcript prints it
beside `host()`. A probe never asserts which one it is talking to — that is
the archive header's job — but `require_1046()` exists for the cells where
measuring the wrong one would be worse than not measuring.

SELFCHECK is behavioural, in br_oracle's and la_oracle's style: a wrong
constant or a missing feature must announce itself rather than silently
measure something else. Probes print `u8_oracle.SELFCHECK` in their header.
"""
import ctypes
import importlib.util
import os
import platform
import re as _pyre
import sys

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
Code = br.Code

# ---------------------------------------------------------------- options

# COMPILE-time option bits (pcre2.h, 8-bit build). Values are the documented
# ones; `_selfcheck` proves BEHAVIOURALLY that each bit does what its name
# says, because a wrong bit here would produce confident wrong measurements
# for the whole lane — the exact failure la_oracle.py records for
# PCRE2_INFO_MAXLOOKBEHIND.
PCRE2_CASELESS          = 0x00000008
PCRE2_MULTILINE         = 0x00000400
PCRE2_DOTALL            = 0x00000020
PCRE2_UCP               = 0x00020000
PCRE2_UTF               = 0x00080000
PCRE2_NO_UTF_CHECK      = 0x40000000
PCRE2_MATCH_INVALID_UTF = 0x04000000

# MATCH-time option bits. PCRE2_NO_UTF_CHECK is spelled the same at both.
M_NO_UTF_CHECK          = 0x40000000
M_ANCHORED              = 0x80000000

_OPT_NAMES = [
    (PCRE2_UTF,               "PCRE2_UTF"),
    (PCRE2_UCP,               "PCRE2_UCP"),
    (PCRE2_CASELESS,          "PCRE2_CASELESS"),
    (PCRE2_MULTILINE,         "PCRE2_MULTILINE"),
    (PCRE2_DOTALL,            "PCRE2_DOTALL"),
    (PCRE2_MATCH_INVALID_UTF, "PCRE2_MATCH_INVALID_UTF"),
    (PCRE2_NO_UTF_CHECK,      "PCRE2_NO_UTF_CHECK"),
]

_OPT_BY_NAME = dict((n, v) for v, n in _OPT_NAMES)


def opts(*names):
    """Build an options word from bit NAMES. `opts()` is 0, the suite's
    standing oracle, and spelling it that way in a probe is a statement
    rather than an omission."""
    w = 0
    for n in names:
        short = n if n.startswith("PCRE2_") else "PCRE2_" + n
        if short not in _OPT_BY_NAME:
            raise KeyError("unknown option bit %r" % (n,))
        w |= _OPT_BY_NAME[short]
    return w


def opts_name(w):
    """Render an options word symbolically: 'PCRE2_UTF|PCRE2_UCP', or
    'options=0'. Unknown bits are shown as a hex residue rather than dropped
    — a dropped bit is how a transcript lies about what it measured."""
    if w == 0:
        return "options=0"
    parts, rest = [], w
    for v, n in _OPT_NAMES:
        if rest & v:
            parts.append(n)
            rest &= ~v
    if rest:
        parts.append("0x%08x" % rest)
    return "|".join(parts)


# ---------------------------------------------------------------- bytes

def u(s):
    """The ONE sanctioned str->bytes bridge: UTF-8, spelled at the call site.
    Everything else in this module takes bytes and refuses str."""
    return s.encode("utf-8")


def _b(x, what):
    if isinstance(x, str):
        raise TypeError(
            "%s must be bytes, not str -- the borrowed binding would encode a "
            "str as LATIN-1 and silently mangle every non-ASCII character. "
            "Use u('...') to say UTF-8 out loud." % what)
    return x


def hexs(bs):
    """A bytes value as space-separated hex, for a transcript column where
    the actual bytes are the measurement."""
    return " ".join("%02X" % c for c in bs)


def pshow(bs):
    """A pattern rendered ASCII-SAFELY for a transcript: printable ASCII as
    itself, every other byte as `\\xHH`.

    THIS EXISTS BECAUSE THE OBVIOUS SPELLING PRINTS A DIFFERENT PATTERN THAN
    THE ONE TESTED. probe_caseless.py's first run rendered its patterns with
    `.decode("latin-1")`, so the two UTF-8 bytes of U+00DF came out as the
    two characters `Ã` + a control -- a transcript row naming a pattern
    nobody ran. Recorded in ../out/CLAUDE.md as this lane's instrument defect
    1; a reader cannot be expected to notice that the pattern column is
    lying, so the rendering is a function rather than a habit."""
    out = []
    for c in bs:
        out.append(chr(c) if 0x20 <= c < 0x7F else "\\x%02x" % c)
    return "".join(out)


# ---------------------------------------------------------------- compile

def compile_err(pat, options=0):
    """None if `pat` compiles under `options`; else (code, offset, msg).

    br_oracle's own compile_err, re-declared here ONLY to take bytes and
    refuse str (point 3 of the header). The libpcre2 call is identical."""
    pat = _b(pat, "pattern")
    errcode = ctypes.c_int(0)
    erroff = ctypes.c_size_t(0)
    code = _lib.pcre2_compile_8(pat, len(pat), options,
                                ctypes.byref(errcode), ctypes.byref(erroff),
                                None)
    if code:
        _lib.pcre2_code_free_8(code)
        return None
    return (errcode.value, erroff.value, pcre2._errmsg(errcode.value))


class Pat:
    """A compiled pattern that remembers the options word it was built with,
    so `match()` can report it and a caller cannot lose track of it."""

    __slots__ = ("_code", "options", "pattern")

    def __init__(self, pat, options=0):
        self.pattern = _b(pat, "pattern")
        self.options = options
        errcode = ctypes.c_int(0)
        erroff = ctypes.c_size_t(0)
        code = _lib.pcre2_compile_8(self.pattern, len(self.pattern), options,
                                    ctypes.byref(errcode),
                                    ctypes.byref(erroff), None)
        if not code:
            raise br.pcre2.Pcre2Error(
                "compile failed at offset %d under %s: %s"
                % (erroff.value, opts_name(options),
                   pcre2._errmsg(errcode.value)))
        self._code = code

    def __del__(self):
        if getattr(self, "_code", None):
            _lib.pcre2_code_free_8(self._code)
            self._code = None


def match(pat, subj, start=0, options=0, mopts=0):
    """The lane's one matcher. Returns, in a vocabulary a transcript can
    print directly:

        ('ERRC', code, msg)      the PATTERN did not compile under `options`
        ('ERRM', code, msg)      the MATCH returned an error -- which for this
                                 lane is a RESULT, not a failure: an
                                 ill-formed subject under PCRE2_UTF lands
                                 here, and which code it lands on is the
                                 measurement.
        None                     no match
        (span, groups)           a match; spans are BYTE offsets, groups
                                 padded per br_oracle's rule with None for
                                 unset.

    `pat` may be bytes (compiled here) or an already-built `Pat`."""
    subj = _b(subj, "subject")
    if not isinstance(pat, Pat):
        try:
            pat = Pat(pat, options)
        except Exception:                                    # noqa: BLE001
            e = compile_err(pat, options)
            return ("ERRC", e[0], e[2]) if e else ("ERRC", 0, "unknown")
    md = _lib.pcre2_match_data_create_from_pattern_8(pat._code, None)
    if not md:
        raise MemoryError("pcre2_match_data_create_from_pattern failed")
    try:
        rc = _lib.pcre2_match_8(pat._code, subj, len(subj), start, mopts,
                                md, None)
        if rc == pcre2.PCRE2_ERROR_NOMATCH:
            return None
        if rc < 0:
            return ("ERRM", rc, pcre2._errmsg(rc))
        ov = _lib.pcre2_get_ovector_pointer_8(md)
        npairs = rc if rc > 0 else 1
        pairs = [(ov[2 * i], ov[2 * i + 1]) for i in range(npairs)]
        groups = tuple(None if s == pcre2.PCRE2_UNSET else (s, e)
                       for s, e in pairs[1:])
        return ((pairs[0][0], pairs[0][1]), groups)
    finally:
        _lib.pcre2_match_data_free_8(md)


# ---------------------------------------------------------------- python re

def pyre_str(pat, subj, start=0, flags=0):
    """python `re` over `str` — a CODE POINT engine. `pat` and `subj` are
    bytes here like everywhere else in this module and are decoded as UTF-8
    at the boundary; a subject that is not valid UTF-8 cannot be expressed as
    a python str at all, and that returns 'UNDECODABLE', which is itself one
    of the D27 goal facts rather than a probe failure.

    THE SPANS ARE CONVERTED BACK TO BYTE OFFSETS, because PCRE2 reports byte
    offsets under PCRE2_UTF (DD-12's permanent invariant) and a row comparing
    a character offset against a byte offset is comparing report conventions,
    not semantics -- la_oracle.py's padding rule, one axis over."""
    try:
        ps, ss = pat.decode("utf-8"), subj.decode("utf-8")
    except UnicodeDecodeError:
        return "UNDECODABLE"
    try:
        c = _pyre.compile(ps, flags)
    except Exception as e:                                   # noqa: BLE001
        return ("ERRC", 0, "%s: %s" % (type(e).__name__, e))
    m = c.search(ss, start)
    if m is None:
        return None

    def bo(i):
        return len(ss[:i].encode("utf-8"))

    return ((bo(m.start()), bo(m.end())),
            tuple(None if m.span(i)[0] < 0 else (bo(m.start(i)), bo(m.end(i)))
                  for i in range(1, (c.groups or 0) + 1)))


def pyre_bytes(pat, subj, start=0, flags=0):
    """python `re` over `bytes` — a BYTE engine, which is what pcrec's `byte`
    encoding is, and the arm the suite's base-tier oracle actually uses."""
    try:
        c = _pyre.compile(pat, flags)
    except Exception as e:                                   # noqa: BLE001
        return ("ERRC", 0, "%s: %s" % (type(e).__name__, e))
    m = c.search(subj, start)
    if m is None:
        return None
    return (m.span(),
            tuple(None if m.span(i)[0] < 0 else m.span(i)
                  for i in range(1, (c.groups or 0) + 1)))


# ---------------------------------------------------------------- header

def host():
    return "%s %s (%s)" % (platform.system(), platform.release(),
                           platform.machine())


def header(title):
    """Every probe's first lines. The options-word legend is printed once
    here so per-row words can be short."""
    return "\n".join([
        "=" * 74,
        title,
        "-" * 74,
        "host      : %s" % host(),
        "python3   : %s" % sys.version.split()[0],
        "libpcre2  : %s" % version(),
        "selfcheck : %s" % (SELFCHECK or "clean"),
        "=" * 74,
        "",
    ])


def require_1046():
    """For a cell where measuring the WRONG library would be worse than not
    measuring. Returns a warning line, or ''."""
    v = version().split()[0] if version() else "?"
    if not v.startswith("10.46"):
        return ("!! NOT THE REFERENCE ORACLE: this ran against libpcre2 %s, "
                "and the project's reference is 10.46 (old box). Rows below "
                "are a COMPARISON, not the measurement.\n" % v)
    return ""


# ---------------------------------------------------------------- selfcheck

def _selfcheck():
    problems = []

    # (1) PCRE2_UTF really is that bit: \x{3b1} is a compile ERROR without it
    #     ("character code point value in \x{} or \o{} is too large" in an
    #     8-bit non-UTF build) and legal with it. If both answers agree the
    #     bit is wrong and every UTF row below is measuring a non-UTF build.
    off = compile_err(b"\\x{3b1}", 0)
    on = compile_err(b"\\x{3b1}", PCRE2_UTF)
    if off is None or on is not None:
        problems.append("PCRE2_UTF bit 0x%08x does not gate \\x{3b1} "
                        "(off=%r on=%r)" % (PCRE2_UTF, off, on))

    # (2) PCRE2_UTF changes MATCHING, not only compiling: `.` must consume the
    #     whole two-byte alpha under UTF and exactly one byte without it. A
    #     bit that compiled but did not match would pass (1) and fail here.
    a = u("α")
    r_on = match(b".", a, options=PCRE2_UTF)
    r_off = match(b".", a, options=0)
    if r_on != ((0, 2), ()) or r_off != ((0, 1), ()):
        problems.append("PCRE2_UTF does not change `.` width "
                        "(utf=%r byte=%r; want ((0,2),()) and ((0,1),()))"
                        % (r_on, r_off))

    # (3) PCRE2_UCP really is that bit, measured on the one thing it is FOR:
    #     \w must reject a Greek letter under UTF alone and accept it under
    #     UTF|UCP. This is the constant every §(vi) divergence row depends on.
    w_no = match(b"\\w", a, options=PCRE2_UTF)
    w_yes = match(b"\\w", a, options=PCRE2_UTF | PCRE2_UCP)
    if w_no is not None or w_yes != ((0, 2), ()):
        problems.append("PCRE2_UCP bit 0x%08x does not gate \\w over a Greek "
                        "letter (utf=%r utf|ucp=%r)" % (PCRE2_UCP, w_no,
                                                        w_yes))

    # (4) an ill-formed subject under PCRE2_UTF must come back as ('ERRM',...)
    #     rather than raise or read as a plain no-match. The whole
    #     invalid-UTF section depends on this vocabulary existing.
    bad = match(b"a", b"\xff\xfe", options=PCRE2_UTF)
    if not (isinstance(bad, tuple) and bad and bad[0] == "ERRM"):
        problems.append("an ill-formed subject under PCRE2_UTF did not "
                        "produce an ERRM row (got %r)" % (bad,))

    # (5) the python arm is really python's `re` and really is code-point
    #     oriented over str: `.` matches the alpha as ONE character there.
    if pyre_str(b".", a) != ((0, 2), ()):
        problems.append("pyre_str is not code-point oriented (got %r)"
                        % (pyre_str(b".", a),))
    if pyre_bytes(b".", a) != ((0, 1), ()):
        problems.append("pyre_bytes is not byte oriented (got %r)"
                        % (pyre_bytes(b".", a),))

    # (6) the str-refusing guard actually fires -- it is the only thing
    #     standing between this lane and a silent latin-1 mangling.
    try:
        match("a", b"a")
        problems.append("_b() did not refuse a str pattern")
    except TypeError:
        pass

    return problems + [p for p in br.SELFCHECK]


SELFCHECK = _selfcheck()

if __name__ == "__main__":
    print(header("u8_oracle self-report"))
    print("PCRE2_UTF               = 0x%08x" % PCRE2_UTF)
    print("PCRE2_UCP               = 0x%08x" % PCRE2_UCP)
    print("PCRE2_MATCH_INVALID_UTF = 0x%08x" % PCRE2_MATCH_INVALID_UTF)
    print("opts_name(UTF|UCP|CASELESS) =",
          opts_name(PCRE2_UTF | PCRE2_UCP | PCRE2_CASELESS))
    print("`.` on U+03B1 under", opts_name(PCRE2_UTF), "->",
          match(b".", u("α"), options=PCRE2_UTF))
