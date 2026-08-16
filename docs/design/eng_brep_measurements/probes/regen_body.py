"""regen_body.py — unparse a python3 `re` parse-tree fragment back into
regex source text.

WHY THIS EXISTS. Task B item 2 (nestedlazy lane brief) asks for a
DIFFERENTIAL over the real .rxt/realistic-set populations' possessifiable
quantifiers, not just the census counts `probe_possess_corpus.py` already
produces. A real pattern's surrounding syntax (backreferences, named
groups, lookarounds, inline flags, ...) is not needed to test whether ONE
quantifier's own verdict is sound -- S2.2's rule is a function of the
quantifier's BODY, its (lo, hi) count, its preference, and its computed
FOLLOW, nothing else about the rest of the pattern -- so this module
unparses just the BODY (the `av[2]` sequence `walk()`/`first_and_nullable()`
already extract for every MAX_REPEAT/MIN_REPEAT/POSSESSIVE_REPEAT row) into
a minimal, semantically equivalent, standalone regex fragment. That sidesteps
writing a general unparser for python's whole `re` grammar (backrefs,
lookaround, conditionals, inline-flag groups, ...), which is both a much
bigger job and unnecessary risk for this task: a body containing any of
those constructs is DECLINED by the analysis today regardless of the
`$`/follow question (see below), so it never reaches "possessifiable" and
this module never needs to round-trip it.

SCOPE, and why it is complete for what actually reaches "possessifiable".
`first_and_nullable()` (probe_possess.py) explicitly models LITERAL,
NOT_LITERAL, ANY, IN, SUBPATTERN, ATOMIC_GROUP, BRANCH, nested
MAX_REPEAT/MIN_REPEAT/POSSESSIVE_REPEAT, and AT (which it widens to
ALL-bytes-nullable=False rather than declining outright). Every OTHER
opcode (GROUPREF, GROUPREF_EXISTS, ASSERT, ASSERT_NOT, a bare CATEGORY
outside IN, ...) falls through to `first_and_nullable`'s final
`return ALL, True` -- widened AND marked nullable -- which makes
`base_ok = uniq and not bn` False for every arm INCLUDING exact-count, so a
body containing any of those can never be declared possessifiable by the
CURRENT analysis. This module therefore only needs to handle exactly the
opcode set `first_and_nullable` models without declining outright, and
raises `Unsupported` (caught and counted by the caller, never silently
skipped) if it ever meets anything else -- which would mean either a body
this module has not seen before, or that `first_and_nullable` grew a new
case this module needs to be told about too.
"""
import re._constants as C

_ESCAPE_OUTSIDE_CLASS = set(".^$*+?{}[]\\|()")
_ESCAPE_INSIDE_CLASS = set("]\\^-")

_CATEGORY_ESCAPES = {
    "CATEGORY_DIGIT": r"\d", "CATEGORY_NOT_DIGIT": r"\D",
    "CATEGORY_WORD": r"\w", "CATEGORY_NOT_WORD": r"\W",
    "CATEGORY_SPACE": r"\s", "CATEGORY_NOT_SPACE": r"\S",
    "CATEGORY_UNI_DIGIT": r"\d", "CATEGORY_UNI_NOT_DIGIT": r"\D",
    "CATEGORY_UNI_WORD": r"\w", "CATEGORY_UNI_NOT_WORD": r"\W",
    "CATEGORY_UNI_SPACE": r"\s", "CATEGORY_UNI_NOT_SPACE": r"\S",
}
_AT_ESCAPES = {
    "AT_BEGINNING": "^", "AT_BEGINNING_LINE": "^", "AT_MULTILINE": "^",
    "AT_END": "$", "AT_END_LINE": "$",
    "AT_BEGINNING_STRING": r"\A", "AT_END_STRING": r"\Z",
    "AT_BOUNDARY": r"\b", "AT_UNI_BOUNDARY": r"\b", "AT_LOC_BOUNDARY": r"\b",
    "AT_NON_BOUNDARY": r"\B", "AT_UNI_NON_BOUNDARY": r"\B",
    "AT_LOC_NON_BOUNDARY": r"\B",
}


class Unsupported(Exception):
    """Raised for any construct outside the modeled set (see module
    docstring): the caller counts and reports these, never guesses."""


def _byte_char(b):
    return bytes([b]).decode("latin-1")


def _escape_literal(b, in_class):
    ch = _byte_char(b)
    escset = _ESCAPE_INSIDE_CLASS if in_class else _ESCAPE_OUTSIDE_CLASS
    if 32 <= b < 127:
        return ("\\" + ch) if ch in escset else ch
    return "\\x%02x" % b


def _category_escape(cat):
    name = str(cat)
    if name in _CATEGORY_ESCAPES:
        return _CATEGORY_ESCAPES[name]
    raise Unsupported("unmapped CATEGORY %r" % (cat,))


def _at_escape(at):
    name = str(at)
    if name in _AT_ESCAPES:
        return _AT_ESCAPES[name]
    raise Unsupported("unmapped AT %r" % (at,))


def _unparse_in(av):
    """av is the IN opcode's own argument: a list of (op, arg) items --
    NEGATE, LITERAL, RANGE, CATEGORY."""
    neg = False
    parts = []
    for iop, iav in av:
        if iop is C.NEGATE:
            neg = True
        elif iop is C.LITERAL:
            parts.append(_escape_literal(iav, in_class=True))
        elif iop is C.RANGE:
            lo, hi = iav
            parts.append(_escape_literal(lo, in_class=True) + "-" +
                          _escape_literal(hi, in_class=True))
        elif iop is C.CATEGORY:
            parts.append(_category_escape(iav))
        else:
            raise Unsupported("IN member opcode %r" % (iop,))
    return "[" + ("^" if neg else "") + "".join(parts) + "]"


def _unparse_item(op, av):
    if op is C.LITERAL:
        return _escape_literal(av, in_class=False)
    if op is C.NOT_LITERAL:
        return "[^" + _escape_literal(av, in_class=True) + "]"
    if op is C.ANY:
        return "."
    if op is C.IN:
        return _unparse_in(av)
    if op is C.AT:
        return _at_escape(av)
    if op is C.SUBPATTERN:
        _, add_flags, del_flags, sub = av
        if add_flags or del_flags:
            raise Unsupported("inline-flag group (add=%r del=%r)"
                               % (add_flags, del_flags))
        return "(?:" + unparse(sub) + ")"
    if op is C.ATOMIC_GROUP:
        return "(?>" + unparse(av) + ")"
    if op is C.BRANCH:
        _, branches = av
        return "(?:" + "|".join(unparse(b) for b in branches) + ")"
    if op in (C.MAX_REPEAT, C.MIN_REPEAT, C.POSSESSIVE_REPEAT):
        lo, hi, body = av
        hi_txt = "" if hi is C.MAXREPEAT else str(hi)
        count = "{%d,%s}" % (lo, hi_txt)
        suffix = {C.MIN_REPEAT: "?", C.POSSESSIVE_REPEAT: "+"}.get(op, "")
        return unparse(body) + count + suffix
    raise Unsupported("opcode %r" % (op,))


def unparse(seq):
    return "".join(_unparse_item(op, av) for op, av in seq)


if __name__ == "__main__":
    import re
    import re._parser as P
    cases = [r"a", r"[ab]", r"(a|b)", r"(a|ab)", r"(?:ab)", r"(?:a|bc)",
             r"[^c]", r"(?:a|)", r"b*", r"(?:ab|a)", r"\d", r"[a-z\d]",
             r"a{2,3}?", r"(a{1,2}){0,3}", r"^a$", r"\ba\B", r"\Aa\Z"]
    bad = 0
    for c in cases:
        parsed = P.parse(c)
        out = unparse(parsed)
        # Semantic check, not textual: re-parse the regenerated text and
        # confirm python compiles it and it matches the same set of short
        # strings the original does, over the case's own alphabet.
        import itertools
        alphabet = "abcd\n"
        ok = True
        try:
            r1, r2 = re.compile(c), re.compile(out)
        except re.error as e:
            print("REGEN DOES NOT COMPILE: %r -> %r (%s)" % (c, out, e))
            bad += 1
            continue
        for n in range(0, 4):
            for tup in itertools.product(alphabet, repeat=n):
                s = "".join(tup)
                if bool(r1.fullmatch(s)) != bool(r2.fullmatch(s)):
                    ok = False
                    print("SEMANTIC MISMATCH: %r -> %r on %r" % (c, out, s))
                    break
            if not ok:
                break
        status = "ok" if ok else "MISMATCH"
        if not ok:
            bad += 1
        print("%-20r -> %-20r [%s]" % (c, out, status))
    print("bad:", bad, "/", len(cases))
