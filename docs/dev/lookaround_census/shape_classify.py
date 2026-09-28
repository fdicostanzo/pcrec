#!/usr/bin/env python3
"""shape_classify.py -- a from-scratch PCRE-lite width/complexity parser,
used to classify every lookaround OCCURRENCE in a pattern by SHAPE, per the
lacensus brief (docs/dev/lanes/BOILERPLATE.md-governed, team-lead brief
2026-09-28): does the DFA's position-VIEW mechanism (bounded-context
lookaround as a predicate, ucp_study.md S:D) reach it.

Not derived from pcrec's own AST -- this is an independent parse over the
PATTERN TEXT, deliberately, so the classifier is not just re-reading the
compiler's own routing decision (which is exactly what RX_ENGINE_WHY's
known offset/kind-mismatch bug, ucp_study.md S:G.2, warns against trusting
alone). Verified by the hand sample in lookaround_census.md S5.

Shapes, worst-first (a pattern is classified by its worst OCCURRENCE):
  e - the lookaround's BODY contains a capturing group, a backreference, a
      subroutine call, OR a nested lookaround (worst: unmodeled by a pure
      subject-position predicate -- captures/backrefs need the VM's
      capture/backtrack state, calls need expansion, a nested lookaround is
      itself a second occurrence and this rule keeps the parent's shape at
      least as bad as its child's).
  d - unbounded width (an unbounded quantifier, or \\X, reaches the body).
  c - bounded but VARIABLE width (min != max, both finite).
  b - FIXED width k (min == max), but not a single atom of width 1.
  a - FIXED width 1 as a SINGLE atom: one character, one class ([...] or a
      POSIX name inside one), one escape shorthand (\\d \\w \\s \\D \\W \\S
      \\h \\H \\v \\V \\p{...} \\P{...} \\N), or `.`.  No alternation, no
      concatenation, no quantifier -- "C is one character or class"
      (Frank's spelling in the brief), matched textually as well as by
      width so an alternation of two one-char branches (not a single C)
      does not count.

Six accepted lookaround spellings (src/parse/mod_lookaround.c's la_rows,
the only ones pcrec's own parser elects -- alpha `(*pla:` etc. spellings are
ALIASES the registry resolves to these before this module ever sees them,
so the census's own alpha-spelling regex is kept only as an extra net):
  (?=   lookahead   positive atomic
  (?!   lookahead   negative atomic
  (?*   lookahead   positive NON-atomic
  (?<=  lookbehind  positive atomic
  (?<!  lookbehind  negative atomic
  (?<*  lookbehind  positive NON-atomic
"""
import re

INF = None  # unbounded max

# ---- backref / call lexical families, mirrored from studies/ucp_study/
# census_analyze.py's FAM table (already vetted by that study) so the two
# classifiers agree on what counts as "a backreference" / "a call": ----
RE_BACKREF = re.compile(rb"\\[1-9]|\\k[<{']|\\g\{?-?\d|\(\?P=|\\g\{[A-Za-z_]")
RE_CALL = re.compile(rb"\(\?R\)|\(\?[+-]?\d+\)|\(\?&|\(\?P>|\\g<|\\g'")
ALPHA_LOOK = re.compile(
    rb"\(\*(pla|nla|plb|nlb|napla|naplb|positive_lookahead|negative_lookahead|"
    rb"positive_lookbehind|negative_lookbehind|"
    rb"non_atomic_positive_look(?:ahead|behind)):"
)


class ParseError(Exception):
    pass


def _char_len(data, i):
    """UTF-8 byte width of the character starting at data[i] (1 if the lead
    byte is malformed -- this is a census over TEXT, not a UTF-8 validator;
    ill-formed bytes just count as one byte each, same policy as an
    unrecognised escape below)."""
    c = data[i]
    if c < 0x80:
        return 1
    if c >= 0xF0:
        return 4
    if c >= 0xE0:
        return 3
    if c >= 0xC0:
        return 2
    return 1


def _skip_class(data, i):
    """i is the index of '['. Returns index just past the matching ']'."""
    n = len(data)
    j = i + 1
    if j < n and data[j] == 0x5E:  # ^
        j += 1
    if j < n and data[j] == ord(']'):  # a leading ] is a literal member
        j += 1
    while j < n:
        c = data[j]
        if c == 0x5C:  # backslash: escaped pair, skip both (handles \] \\ etc.)
            j += 2
            continue
        if c == ord('[') and j + 1 < n and data[j + 1] in b":.=":
            k = data.find(bytes([data[j + 1], ord(']')]), j + 2)
            j = (k + 2) if k > 0 else j + 1
            continue
        if c == ord(']'):
            return j + 1
        j += 1
    return n  # unterminated: treat as running to end


def _quant(data, i, atom_min, atom_max, single_atom):
    """i is just past an atom/group.  Consumes a trailing quantifier if
    present and returns (new_min, new_max, new_i, consumed_quant: bool)."""
    n = len(data)
    if i >= n:
        return atom_min, atom_max, i, False
    c = data[i]

    def lazy_possessive(j):
        if j < n and data[j] in b"?+":
            return j + 1
        return j

    if c == ord('?'):
        return 0, atom_max, lazy_possessive(i + 1), True
    if c == ord('*'):
        return 0, (0 if atom_max == 0 else INF), lazy_possessive(i + 1), True
    if c == ord('+'):
        return atom_min, (0 if atom_max == 0 else INF), lazy_possessive(i + 1), True
    if c == ord('{'):
        m = re.match(rb"\{(\d*)(,?)(\d*)\}", data[i:])
        if not m or (not m.group(1) and not m.group(3)):
            return atom_min, atom_max, i, False  # not a quantifier -- a literal '{'
        lo = int(m.group(1)) if m.group(1) else 0
        has_comma = bool(m.group(2))
        if not has_comma:
            hi = lo
        elif m.group(3):
            hi = int(m.group(3))
        else:
            hi = None
        j = i + m.end()
        new_min = atom_min * lo
        if atom_max == 0:
            new_max = 0
        elif hi is None:
            new_max = INF
        elif atom_max is INF:
            new_max = INF
        else:
            new_max = atom_max * hi
        return new_min, new_max, lazy_possessive(j), True
    return atom_min, atom_max, i, False


# escape -> (min, max, charlike) for the shorthand classes; every other
# escape not listed here is handled specially in _term().
_ESC_CLASS_1 = set(b"dDwWsShHvVN")  # single-char shorthand classes; \N alone
                                    # ("not \\N{...}") is "any char but \\n"


def _term(data, i, end, ctx, occurrences, in_look):
    """Parses ONE quantified atom/group starting at data[i] (i < end).
    Returns (min, max, flags:set, single_atom:bool, next_i)."""
    n = end
    c = data[i]

    if c == ord('('):
        return _group(data, i, ctx, occurrences, in_look)

    if c == ord('['):
        j = _skip_class(data, i)
        mn, mx, k, _ = _quant(data, j, 1, 1, True)
        return mn, mx, set(), (k == j), k

    if c == ord('.'):
        mn, mx, k, _ = _quant(data, i + 1, 1, 1, True)
        return mn, mx, set(), (k == i + 1), k

    if c in b"^$":
        mn, mx, k, _ = _quant(data, i + 1, 0, 0, False)
        return mn, mx, set(), False, k

    if c == 0x5C:  # backslash
        if i + 1 >= n:
            return 1, 1, set(), True, i + 1  # trailing lone backslash: treat as literal
        e = data[i + 1]
        ec = chr(e)

        if ec == 'Q':
            j = data.find(b"\\E", i + 2, end)
            body_end = end if j < 0 else j
            close = end if j < 0 else j + 2
            text = data[i + 2:body_end]
            if not text:
                return 0, 0, set(), False, close
            nchars = 0
            p = 0
            while p < len(text):
                p += _char_len(text, p)
                nchars += 1
            # a trailing quantifier binds only to the LAST character of the
            # \Q..\E run (PCRE2's own rule); the other nchars-1 are fixed
            # literal atoms with no quantifier possible.
            head_chars = nchars - 1
            mn, mx, k, consumed = _quant(data, close, 1, 1, True)
            single_atom = (nchars == 1) and not consumed
            return head_chars + mn, (INF if mx is INF else head_chars + mx), set(), single_atom, k

        if ec == 'K':
            return 0, 0, set(), False, i + 2

        if ec in "bBAZzG":
            return 0, 0, set(), False, i + 2

        if ec == 'R':
            mn, mx, k, _ = _quant(data, i + 2, 1, 2, False)
            return mn, mx, set(), False, k

        if ec == 'X':
            mn, mx, k, _ = _quant(data, i + 2, 1, INF, False)
            return mn, mx, {'unbounded-atom-X'}, False, k

        if ec in "pP":
            j = i + 2
            if j < n and data[j] == ord('{'):
                kend = data.find(b"}", j, end)
                j = end if kend < 0 else kend + 1
            elif j < n:
                j += 1  # \pL short form
            mn, mx, k, consumed = _quant(data, j, 1, 1, True)
            return mn, mx, set(), (k == j), k

        if RE_BACKREF.match(data[i:end]):
            m = RE_BACKREF.match(data[i:end])
            j = i + m.end()
            mn, mx, k, _ = _quant(data, j, 0, INF, False)
            return mn, mx, {'backref'}, False, k

        if ec == 'g' and i + 2 < n and data[i + 2] in b"<'":
            close_c = ord('>') if data[i + 2] == ord('<') else ord("'")
            kend = data.find(bytes([close_c]), i + 3, end)
            j = end if kend < 0 else kend + 1
            mn, mx, k, _ = _quant(data, j, 0, INF, False)
            return mn, mx, {'call'}, False, k

        if ec == 'N' and i + 2 < n and data[i + 2] == ord('{'):
            # \N{U+HHHH} / \N{name}: a named/numeric character reference --
            # ONE literal character, not the bare-\N "any char but \n" class.
            kend = data.find(b"}", i + 3, end)
            j = end if kend < 0 else kend + 1
            mn, mx, k, consumed = _quant(data, j, 1, 1, True)
            return mn, mx, set(), (k == j), k

        if e in _ESC_CLASS_1:
            j = i + 2
            mn, mx, k, consumed = _quant(data, j, 1, 1, True)
            return mn, mx, set(), (k == j), k

        if ec == 'x':
            j = i + 2
            if j < n and data[j] == ord('{'):
                kend = data.find(b"}", j, end)
                j = end if kend < 0 else kend + 1
            else:
                j += min(2, end - j)
            mn, mx, k, consumed = _quant(data, j, 1, 1, True)
            return mn, mx, set(), (k == j), k

        # any other \X (escaped literal punctuation, \0, octal, \n \t \r \f \a
        # \e etc.): one literal character, width 1
        mn, mx, k, consumed = _quant(data, i + 2, 1, 1, True)
        return mn, mx, set(), (k == i + 2), k

    # plain literal character (possibly multi-byte UTF-8)
    clen = _char_len(data, i)
    j = i + clen
    mn, mx, k, consumed = _quant(data, j, 1, 1, True)
    return mn, mx, set(), (k == j), k


_LOOK_KIND = {
    (ord('='), False): ('lookahead', '+', True),
    (ord('!'), False): ('lookahead', '-', True),
    (ord('*'), False): ('lookahead', '+', False),
    (ord('='), True): ('lookbehind', '+', True),
    (ord('!'), True): ('lookbehind', '-', True),
    (ord('*'), True): ('lookbehind', '+', False),
}


_ALPHA_LOOK_KIND = {
    "pla": ("lookahead", "+", True), "positive_lookahead": ("lookahead", "+", True),
    "nla": ("lookahead", "-", True), "negative_lookahead": ("lookahead", "-", True),
    "napla": ("lookahead", "+", False), "non_atomic_positive_lookahead": ("lookahead", "+", False),
    "plb": ("lookbehind", "+", True), "positive_lookbehind": ("lookbehind", "+", True),
    "nlb": ("lookbehind", "-", True), "negative_lookbehind": ("lookbehind", "-", True),
    "naplb": ("lookbehind", "+", False), "non_atomic_positive_lookbehind": ("lookbehind", "+", False),
}
_ALPHA_LOOK_RE = re.compile(
    rb"\((\*)(" + b"|".join(k.encode() for k in _ALPHA_LOOK_KIND) + rb"):"
)


def _group(data, i, ctx, occurrences, in_look):
    """i is the index of '('. Returns (min, max, flags, single_atom, next_i)."""
    n = len(data)
    end_all = len(data)

    ma = _ALPHA_LOOK_RE.match(data[i:end_all])
    if ma:
        # (*pla:...), (*nla:...), etc.: the alpha spellings mod_lookaround.c
        # accepts as ALIASES resolving to the same six constructs -- handled
        # structurally here (not just by the FAM lexical net) so the census
        # does not silently mis-tag tests/lookaround/alpha_spellings.rxt.
        kind, pol, atomicf = _ALPHA_LOOK_KIND[ma.group(2).decode()]
        j = i + ma.end()
        depth = 1
        k = j
        while k < end_all and depth:
            if data[k] == 0x5C:
                k += 2; continue
            if data[k] == ord('['):
                k = _skip_class(data, k); continue
            if data[k] == ord('('):
                depth += 1
            elif data[k] == ord(')'):
                depth -= 1
                if depth == 0:
                    break
            k += 1
        close = min(k, end_all)
        bmn, bmx, bflags = _parse_alt(data, j, close, ctx, occurrences, True)
        occ = dict(kind=kind, polarity=pol, atomic=atomicf, offset=i,
                   body=data[j:close], min=bmn, max=bmx, flags=set(bflags),
                   nested=in_look, single_atom=ctx.get('_last_single', False))
        occurrences.append(occ)
        outer_flags = {'nested_look'} if in_look else set()
        return 0, 0, outer_flags, False, close + 1

    if i + 1 >= n or data[i + 1] != ord('?'):
        # plain capturing group: (...)
        j = i + 1
        depth = 1
        k = j
        while k < end_all and depth:
            if data[k] == 0x5C:
                k += 2
                continue
            if data[k] == ord('['):
                k = _skip_class(data, k)
                continue
            if data[k] == ord('('):
                depth += 1
            elif data[k] == ord(')'):
                depth -= 1
                if depth == 0:
                    break
            k += 1
        close = min(k, end_all)
        mn, mx, flags = _parse_alt(data, j, close, ctx, occurrences, in_look)
        flags = set(flags) | {'capture'}
        mn2, mx2, kk, consumed = _quant(data, close + 1 if close < end_all else close, mn, mx, False)
        return mn2, mx2, flags, False, kk

    # (?...
    behind = (i + 2 < n and data[i + 2] == ord('<') and i + 3 < n and data[i + 3] in b"=!*")
    if behind:
        sel = data[i + 3]
        body_start = i + 4
    else:
        sel = data[i + 2] if i + 2 < n else 0
        body_start = i + 3

    if (sel, behind) in _LOOK_KIND:
        kind, pol, atomicf = _LOOK_KIND[(sel, behind)]
        j = body_start
        depth = 1
        k = j
        while k < end_all and depth:
            if data[k] == 0x5C:
                k += 2
                continue
            if data[k] == ord('['):
                k = _skip_class(data, k)
                continue
            if data[k] == ord('('):
                depth += 1
            elif data[k] == ord(')'):
                depth -= 1
                if depth == 0:
                    break
            k += 1
        close = min(k, end_all)
        bmn, bmx, bflags = _parse_alt(data, j, close, ctx, occurrences, True)
        occ = dict(kind=kind, polarity=pol, atomic=atomicf, offset=i,
                   body=data[j:close], min=bmn, max=bmx, flags=set(bflags),
                   nested=in_look, single_atom=ctx.get('_last_single', False))
        occurrences.append(occ)
        outer_flags = {'nested_look'} if in_look else set()
        # a lookaround construct itself is a zero-width assertion in the
        # ENCLOSING expression
        return 0, 0, outer_flags, False, close + 1

    # named capturing group: (?<name>...) / (?P<name>...) / (?'name'...)
    m = re.match(rb"\(\?P?<[^>=!*][^>]*>|\(\?P?'[^']*'", data[i:end_all])
    if m:
        j = i + m.end()
        depth = 1
        k = j
        while k < end_all and depth:
            if data[k] == 0x5C:
                k += 2
                continue
            if data[k] == ord('['):
                k = _skip_class(data, k)
                continue
            if data[k] == ord('('):
                depth += 1
            elif data[k] == ord(')'):
                depth -= 1
                if depth == 0:
                    break
            k += 1
        close = min(k, end_all)
        mn, mx, flags = _parse_alt(data, j, close, ctx, occurrences, in_look)
        flags = set(flags) | {'capture'}
        mn2, mx2, kk, _ = _quant(data, close + 1 if close < end_all else close, mn, mx, False)
        return mn2, mx2, flags, False, kk

    # (?P=name) named backref
    if data[i:i + 4] == b"(?P=":
        kend = data.find(b")", i, end_all)
        j = end_all if kend < 0 else kend + 1
        mn, mx, k, _ = _quant(data, j, 0, INF, False)
        return mn, mx, {'backref'}, False, k

    # calls: (?R) (?N) (?+N) (?-N) (?&name) (?P>name)
    if RE_CALL.match(data[i:end_all]):
        mcall = RE_CALL.match(data[i:end_all])
        if data[i:i + 3] == b"(?&" or data[i:i + 4] == b"(?P>":
            kend = data.find(b")", i, end_all)
            j = end_all if kend < 0 else kend + 1
        else:
            j = i + mcall.end()
        mn, mx, k, _ = _quant(data, j, 0, INF, False)
        return mn, mx, {'call'}, False, k

    # (?>...) atomic group, (?:...) non-capturing, (?i:...) modifier group
    m2 = re.match(rb"\(\?[>:]|\(\?[a-zA-Z^\-]*:", data[i:end_all])
    if m2:
        j = i + m2.end()
        depth = 1
        k = j
        while k < end_all and depth:
            if data[k] == 0x5C:
                k += 2
                continue
            if data[k] == ord('['):
                k = _skip_class(data, k)
                continue
            if data[k] == ord('('):
                depth += 1
            elif data[k] == ord(')'):
                depth -= 1
                if depth == 0:
                    break
            k += 1
        close = min(k, end_all)
        mn, mx, flags = _parse_alt(data, j, close, ctx, occurrences, in_look)
        mn2, mx2, kk, _ = _quant(data, close + 1 if close < end_all else close, mn, mx, False)
        return mn2, mx2, flags, False, kk

    # bare modifier-only group: (?i) (?-i) (?im) with no body, no colon
    m3 = re.match(rb"\(\?[a-zA-Z\^\-]*\)", data[i:end_all])
    if m3:
        return 0, 0, set(), False, i + m3.end()

    # conditional: (?(...)yes|no)  -- rare inside a lookaround body; modelled
    # conservatively as COMPLEX (flagged, not width-modelled), per the
    # module's header note.
    if data[i:i + 3] == b"(?(":
        depth = 1
        k = i + 1
        while k < end_all and depth:
            if data[k] == 0x5C:
                k += 2
                continue
            if data[k] == ord('['):
                k = _skip_class(data, k)
                continue
            if data[k] == ord('('):
                depth += 1
            elif data[k] == ord(')'):
                depth -= 1
                if depth == 0:
                    break
            k += 1
        close = min(k, end_all)
        mn2, mx2, kk, _ = _quant(data, close + 1 if close < end_all else close, 0, INF, False)
        return 0, INF, {'complex-conditional'}, False, kk

    # unrecognised '(?...' shape: flag complex, skip to the matching close
    depth = 1
    k = i + 1
    while k < end_all and depth:
        if data[k] == 0x5C:
            k += 2
            continue
        if data[k] == ord('['):
            k = _skip_class(data, k)
            continue
        if data[k] == ord('('):
            depth += 1
        elif data[k] == ord(')'):
            depth -= 1
            if depth == 0:
                break
        k += 1
    close = min(k, end_all)
    mn2, mx2, kk, _ = _quant(data, close + 1 if close < end_all else close, 0, INF, False)
    return 0, INF, {'complex-unrecognised'}, False, kk


def _parse_seq(data, i, end, ctx, occurrences, in_look):
    mn = mx = 0
    flags = set()
    natoms = 0
    last_single = False
    while i < end:
        if data[i] == ord('|'):
            break
        amn, amx, aflags, asingle, ni = _term(data, i, end, ctx, occurrences, in_look)
        mn += amn
        mx = INF if (mx is INF or amx is INF) else mx + amx
        flags |= aflags
        natoms += 1
        last_single = asingle
        i = ni
    single_atom = (natoms == 1) and last_single
    return mn, mx, flags, single_atom, i


def _parse_alt(data, i, end, ctx, occurrences, in_look):
    branches = []
    j = i
    while True:
        mn, mx, flags, single, nj = _parse_seq(data, j, end, ctx, occurrences, in_look)
        branches.append((mn, mx, flags, single, j, nj))
        j = nj
        if j < end and data[j] == ord('|'):
            j += 1
            continue
        break
    mn = min(b[0] for b in branches)
    mx = INF if any(b[1] is INF for b in branches) else max(b[1] for b in branches)
    flags = set()
    for b in branches:
        flags |= b[2]
    single = (len(branches) == 1) and branches[0][3]
    ctx['_last_single'] = single
    return mn, mx, flags


def classify_pattern(pattern_bytes):
    """Parses `pattern_bytes` (the RAW, untruncated pattern) and returns the
    list of lookaround occurrence dicts (see _group's `occ`), each with a
    'shape' key added ('a'..'e') and, for shape 'b', a 'k' key."""
    occurrences = []
    ctx = {}
    try:
        _parse_alt(pattern_bytes, 0, len(pattern_bytes), ctx, occurrences, False)
    except (IndexError, RecursionError):
        return None  # unparsed: caller falls back to REFUSED/UNPARSED bucket
    # 'unbounded-atom-X' (a bare \X in the body) is a note, not its own
    # category: \X always sets max=INF, so it already routes to shape 'd'
    # below without special-casing.
    COMPLEX = {'capture', 'backref', 'call', 'nested_look',
               'complex-conditional', 'complex-unrecognised'}
    for occ in occurrences:
        f = occ['flags']
        mn, mx = occ['min'], occ['max']
        if f & COMPLEX:
            occ['shape'] = 'e'
        elif mx is INF:
            occ['shape'] = 'd'
        elif mn != mx:
            occ['shape'] = 'c'
        elif mx == 1 and occ['single_atom']:
            occ['shape'] = 'a'
        else:
            occ['shape'] = 'b'
            occ['k'] = mx
    return occurrences


_ORDER = {'e': 4, 'd': 3, 'c': 2, 'b': 1, 'a': 0}


def worst_shape(occurrences):
    if not occurrences:
        return None
    return max((o['shape'] for o in occurrences), key=lambda s: _ORDER[s])


if __name__ == "__main__":
    import sys
    for line in sys.stdin:
        pat = line.rstrip(b"\n" if isinstance(line, bytes) else "\n")
        if isinstance(pat, str):
            pat = pat.encode("utf-8", "surrogateescape")
        occs = classify_pattern(pat)
        if occs is None:
            print("UNPARSED\t" + pat.decode("utf-8", "backslashreplace"))
            continue
        w = worst_shape(occs)
        print("%s\t%d\t%s" % (w, len(occs), pat.decode("utf-8", "backslashreplace")[:100]))
