"""common.py -- shared helpers for the [M6.6.3] D27 lookaround corpus.

Written by the blinded author, from docs/testing.md's .rxt format
description directly -- NOT by importing or copying any harness/verifier
code that might live under tests/ in the real tree (which this cell does
not contain and which the brief forbids reading). This is the "re-derive
your own .rxt writer/checker from THIS DOCUMENT directly" instruction.

Also loads docs/design/lookaround_measurements/probes/la_oracle.py, the
provided libpcre2 10.46 ctypes oracle, and re-exports python3 `re`
wrappers. Every expectation this corpus writes is derived by calling into
this module's oracle functions -- never recalled, never guessed.
"""
import importlib.util
import os
import re as _pyre

_HERE = os.path.dirname(os.path.abspath(__file__))
_ORACLE = os.path.normpath(os.path.join(
    _HERE, "..", "docs", "design", "lookaround_measurements", "probes",
    "la_oracle.py"))

_spec = importlib.util.spec_from_file_location("la_oracle", _ORACLE)
la = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(la)

assert not la.SELFCHECK, "la_oracle self-check failed: %r" % (la.SELFCHECK,)


# ---------------------------------------------------------------------------
# .rxt escaping, derived from docs/testing.md's table exactly:
#   \"  \\  \n  \t  \r  \f  \v  \xHH   -- no others recognized.
# ---------------------------------------------------------------------------
def rxt_escape(s):
    """Encode a python str of codepoints 0..255 (latin-1 byte values) as an
    .rxt double-quoted subject body, using only the escapes docs/testing.md
    lists. Printable ASCII (0x20-0x7E) other than '"' and '\\' passes
    through literally; everything else uses the listed named escapes or
    \\xHH."""
    named = {'"': '\\"', '\\': '\\\\', '\n': '\\n', '\t': '\\t',
             '\r': '\\r', '\f': '\\f', '\v': '\\v'}
    out = []
    for ch in s:
        o = ord(ch)
        if ch in named:
            out.append(named[ch])
        elif 0x20 <= o <= 0x7E:
            out.append(ch)
        else:
            out.append("\\x%02X" % o)
    return '"' + "".join(out) + '"'


class Block:
    """One .rxt pattern block being assembled."""

    def __init__(self, pattern, features, flags=""):
        self.pattern = pattern
        self.features = features          # e.g. "lookaround" or
                                           # "lookaround,backrefs"
        self.flags = flags                # "" or "i"
        self.lines = []                   # already-formatted body lines
        self.is_perr = False

    def perr(self):
        self.is_perr = True
        return self

    def m(self, subject, start, end):
        self.lines.append('m %s %d %d' % (rxt_escape(subject), start, end))
        return self

    def n(self, subject):
        self.lines.append('n %s' % (rxt_escape(subject),))
        return self

    def ms(self, p, subject, start, end):
        self.lines.append('ms %d %s %d %d' % (p, rxt_escape(subject),
                                                start, end))
        return self

    def ns(self, p, subject):
        self.lines.append('ns %d %s' % (p, rxt_escape(subject)))
        return self

    def g(self, slot, start, end):
        self.lines.append('g %d %d %d' % (slot, start, end))
        return self

    def gunset(self, slot):
        self.lines.append('g %d -1 -1' % (slot,))
        return self

    def render(self, comment=None):
        out = []
        if comment:
            for cl in comment.splitlines():
                out.append('# ' + cl if cl else '#')
        out.append('features %s' % (self.features,))
        if self.flags:
            out.append('flags %s' % (self.flags,))
        out.append('pattern %s' % (self.pattern,))
        if self.is_perr:
            out.append('perr')
        else:
            out.extend(self.lines)
        return "\n".join(out) + "\n"


class RxtFile:
    def __init__(self, path):
        self.path = path
        self.blocks = []          # list of (Block, comment_or_None)
        self.pcre2only_count = 0
        self.python_count = 0
        self.perr_count = 0

    def add(self, block, comment=None, pcre2_only=False):
        if block.is_perr:
            self.perr_count += 1
            pcre2_only = False    # never write the marker on a perr block
        elif pcre2_only:
            self.pcre2only_count += 1
        else:
            self.python_count += 1
        self.blocks.append((block, comment, pcre2_only))
        return block

    def write(self, header):
        with open(self.path, "w") as f:
            f.write(header)
            f.write("\n")
            for block, comment, pcre2_only in self.blocks:
                if pcre2_only:
                    f.write("# pcre2-only\n")
                f.write(block.render(comment))
                f.write("\n")
        return self.path

    def block_count(self):
        return len(self.blocks)

    def cell_count(self):
        """Count of m/n/ms/ns lines (not counting g/gp), across all blocks."""
        n = 0
        for block, _, _ in self.blocks:
            if block.is_perr:
                n += 1  # the perr itself is the one assertion in that block
            else:
                for l in block.lines:
                    if l.split(" ", 1)[0] in ("m", "n", "ms", "ns"):
                        n += 1
        return n


# ---------------------------------------------------------------------------
# Oracle helpers used by every generator.
# ---------------------------------------------------------------------------
def pcre2_search(pat, subj, start=0):
    """la.search() result, already in (span, groups)/None/"ERR" form."""
    return la.search(pat, subj, start)


def py_search(pat, subj, start=0):
    return la.pyre_search(pat, subj, start)


def pcre2_ok(pat):
    return la.compile_err(pat) is None


def py_ok(pat):
    return la.pyre(pat)[1] is None
