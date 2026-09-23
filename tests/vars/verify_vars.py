#!/usr/bin/env python3
"""tests/vars/verify_vars.py — module `vars`' PATTERN-SIDE ORACLE
([VAR] M10; docs/design/variables_common.md §3.6).

WHAT IT CHECKS, AND WHY IT IS NOT THE CORPUS AGAIN. Every `m`/`n` cell in
tests/vars/ is scored by the harness against an expectation a human wrote.
This program checks those expectations against an INDEPENDENT authority — the
installed libpcre2, driven over a pattern that does not mention variables at
all — so that "the artifact answers what the file says" and "the file says the
right thing" are two claims and not one.

THE TECHNIQUE IS THE QUOTEMETA-SPLICE, and it is §3.6's primary one: replace
each `${name}` with

        (?:  +  quotemeta(value)  +  )

and ask libpcre2 the resulting ordinary pattern. The value carries no
capturing group after quotemeta, so splicing it perturbs no group numbering —
which is what makes D87's textual-composition hazard not apply here (that
hazard is about splicing a CAPTURING sub-pattern's own text).

**THE WRAP IS UNCONDITIONAL AND IT IS A RULING** (Frank, 2026-09-23). A
variable reference is ONE node, so a quantifier, alternation or lookaround
written against `${name}` applies to the WHOLE value: `${x}+` with x = "ab"
means `(?:ab)+`, and a BARE splice would read `ab+` — quantifying only the
last byte and making the oracle disagree with a CORRECT artifact. The same
wrap makes `${x}{2}`, `a|${x}`, `(?=${x})` and `${x}?` splice correctly, and
EMPTY splices to `(?:)`, which PCRE2 accepts. A test that relies on the bare
splice is wrong.

WHAT IT DOES *NOT* REACH, stated per learnings.md §3's rule to name the set a
claim is measured over and ask what is outside it:

  * every UNSET cell, and the `:?` refusals. There is no PCRE2 spelling for
    "this literal is absent" to splice, so those cells are ORACLE-LESS BY
    CONSTRUCTION and are refusal-table rows instead (`gu unset-var`).
  * the UTF-8 validity refusal, for the same reason.
  * any operator whose word is a NESTED reference, because resolving it is
    the mechanism under test rather than something the splice can express.
    Such a block is SKIPPED and COUNTED, never silently dropped.

So this program sweeps exactly the SET and EMPTY population with concrete
values, which is where an independent answer is available at all.

SKIPS LOUDLY when libpcre2 is absent (PC-3's pattern): exit 3 with a message,
never a silent green.

THE NAME IS THE MECHANISM. `tests/harness/verify_rxt.py`'s
`declares_own_oracle` treats a directory holding a `verify_*.py` of its own as
having one, and SKIPS its cells with a counted `own-oracle` skip rather than
scoring them against python `re`. That is exactly right here and it is why
this file is not called `var_oracle.py`: NEITHER standing oracle can express a
caller variable. python `re` has no such feature at all, and libpcre2 reads
`${v}` as an assertion followed by a literal `{` — a spelling no subject can
match (variables_common.md §0.2) — so scoring these cells against either would
report a divergence on every one of them and mean nothing.

Usage: verify_vars.py <file.rxt>...
Prints one PASS/FAIL line per checked cell and a trailer; exit 1 on any
disagreement, 3 when the oracle is unavailable.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "docs", "design",
                                "eng_brep_measurements", "probes"))
try:
    import pcre2_ctypes as P
except Exception as e:                                     # noqa: BLE001
    sys.stderr.write("verify_vars: libpcre2 unavailable: %s\n" % e)
    sys.exit(3)

# The .rxt quoted-subject escape set, decoded the way driver.c's decode()
# does. Spelled here rather than imported because there is no python home for
# it; the FIVE-escape TSV-framing subset plus \xHH is the whole vocabulary
# (docs/spec/rxt_format.md).
_ESC = {'"': '"', '\\': '\\', 'n': '\n', 't': '\t',
        'r': '\r', 'f': '\f', 'v': '\v'}


def unesc(s):
    """Decode a .rxt quoted value's escapes into raw bytes (as latin-1 str)."""
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c != '\\':
            out.append(c)
            i += 1
            continue
        if i + 1 >= len(s):
            out.append('\\')
            break
        n = s[i + 1]
        if n == 'x' and i + 3 < len(s):
            out.append(chr(int(s[i + 2:i + 4], 16)))
            i += 4
            continue
        out.append(_ESC.get(n, n))
        i += 2
    return "".join(out)


def quotemeta(v, utf8):
    """Escape every unit of `v` so PCRE2 reads it as itself.

    UNIFORMLY, never a backslash before the metacharacters only: a
    half-escaped value is a disagreement a reader cannot see.

    THE UNIT DEPENDS ON THE ENCODING, and getting that wrong is how this
    sweep introduced itself. Under `byte` a value is BYTES and `\\xNN` is the
    byte NN. Under PCRE2_UTF, `\\xNN` above 0x7F is the CODE POINT U+00NN and
    NOT the byte — so escaping the Kelvin sign's three UTF-8 bytes
    byte-by-byte produces a pattern for three Latin-1 characters, which
    matched nothing and reported four false disagreements against a correct
    artifact. Under UTF the value is decoded and each code point is spelled
    `\\x{...}`."""
    if utf8:
        return "".join("\\x{%x}" % ord(c)
                       for c in v.encode("latin-1").decode("utf-8"))
    return "".join("\\x%02x" % ord(c) for c in v)


VAR_RE = re.compile(
    r'\$\{(!?)([A-Za-z_][A-Za-z0-9_]*)'      # the `!` and the selector
    r'(?:(:?)([-+?])((?:[^{}\\]|\\.)*))?\}')  # the operator and its word


class Unset(Exception):
    """No splice exists for this reference: the value is UNSET and the form
    does not supply one. The caller counts it rather than dropping it."""


def evaluate(m, env):
    """The five operators, RE-DERIVED from variables_common.md §1.1's table.

    THIS HALF IS NOT LIBPCRE2's ANSWER AND THE FILE SAYS SO. libpcre2 has no
    caller-variable feature, so nothing outside pcrec can tell us what
    `${v:-w}` should expand to; what IS independent here is the MATCH of the
    expanded literal, which is the question the splice hands to libpcre2.
    So this arm is a SECOND READING OF THE SPEC TABLE in a different
    language, checked against the emitted C by way of a real match — worth
    having, and not worth calling an oracle of the operator semantics
    themselves (learnings.md §3: name what a control shares with its
    subject; this one shares the design table and nothing else).

    A nested word is NOT evaluated here: resolving one is the mechanism
    under test, and expressing it would make this arm a re-implementation
    rather than a re-reading. Raises Unset, which the caller counts."""
    name, colon, op, word = m.group(2), m.group(3), m.group(4), m.group(5)
    if word and "${" in word:
        raise Unset(name)                    # nested: not this arm's
    val = env.get(name)                      # absent and explicit-unset agree
    word = unesc_word(word or "")
    empty_counts = (colon == ":")
    fires = val is None or (empty_counts and val == "")
    if op is None:
        if val is None:
            raise Unset(name)                # a bare ${v}: the call refuses
        return val
    if op == "-":
        return word if fires else val
    if op == "+":
        return word if not fires else ""
    if op == "?":
        if fires:
            raise Unset(name)
        return val
    raise Unset(name)


def unesc_word(w):
    """A word's own escape rule (src/core/varexp.c): a backslash makes the
    next byte literal. Spelled separately from `unesc` above because the two
    vocabularies are genuinely different — a `.rxt` quoted value carries
    `\\n`/`\\xHH`, a pattern WORD carries only "the next byte"."""
    out, i = [], 0
    while i < len(w):
        if w[i] == '\\' and i + 1 < len(w):
            out.append(w[i + 1])
            i += 2
        else:
            out.append(w[i])
            i += 1
    return "".join(out)


def splice(pattern, env, utf8):
    """Replace every `${...}` with `(?:` + quotemeta(its value) + `)`.

    Raises Unset when a reference has no value to splice."""
    def sub(m):
        v = evaluate(m, env)
        return "(?:" + quotemeta(v, utf8) + ")"
    out = VAR_RE.sub(sub, pattern)
    if "${" in out:
        # A form this regex did not recognise reached the output unchanged,
        # which would be spliced into libpcre2 as literal text and compared
        # against a real answer -- a FALSE disagreement dressed as a finding.
        # Refusing here is what stops the sweep reporting on a form it does
        # not understand.
        raise Unset("unrecognised ${...} form in %r" % pattern)
    return out


def check_file(path, stats):
    """Sweep one .rxt file's SET/EMPTY cells against the spliced oracle."""
    env, pattern, caseless, utf8, pline = {}, None, False, False, 0
    for lineno, raw in enumerate(open(path, encoding="latin-1"), 1):
        line = raw.rstrip("\n")
        if line.startswith("pattern "):
            env, pattern, caseless, utf8, pline = {}, line[8:], False, False, lineno
        elif line.startswith("pattern-esc ") or line.startswith("#") or not line.strip():
            if line.startswith("pattern-esc "):
                # Its value carries escapes this sweep would have to decode
                # into the PATTERN, which is a second decoder for a
                # population of one. Counted, not dropped.
                pattern = None
                stats["skip_esc"] += 1
            continue
        elif line.startswith("var-unset "):
            env[line.split()[1]] = None
        elif line.startswith("var "):
            m = re.match(r'var\s+([A-Za-z_][A-Za-z0-9_]*)\s+"(.*)"\s*$', line)
            if m and m.group(1) not in env:      # FIRST binding wins
                env[m.group(1)] = unesc(m.group(2))
        elif line.startswith("encoding "):
            utf8 = line.split()[1] == "utf8"
        elif line.startswith("gu unset-var "):
            # ORACLE-LESS BY CONSTRUCTION, and COUNTED so the trailer's own
            # arithmetic says how much of the corpus this technique does not
            # reach rather than leaving it to be inferred from a difference
            # between two numbers nobody prints.
            stats["skip_unset"] += 1
        elif line.startswith(("m ", "n ")):
            if pattern is None:
                continue
            m = re.match(r'([mn])\s+"(.*?)"(?:\s+(\d+)\s+(\d+))?\s*$', line)
            if not m:
                continue
            subj = unesc(m.group(2))
            pat = pattern
            if pat.startswith("^(?i)"):
                pat, caseless = "^" + pat[5:], True
            try:
                spliced = splice(pat, env, utf8)
            except Unset:
                stats["skip_op"] += 1
                continue
            # The two option bits, spelled here rather than read off the
            # binding: `pcre2_ctypes` is deliberately BYTE-ORIENTED (its own
            # comment on PCRE2_UTF says "not used: this module stays
            # byte-oriented like pcrec") and carries no CASELESS at all.
            # These are PCRE2's own documented values and they are the two
            # this sweep needs; adding them to the shared binding would
            # change what that module is for.
            PCRE2_CASELESS = 0x00000008
            PCRE2_UTF_BIT  = 0x00080000
            opts = 0
            if caseless:
                opts |= PCRE2_CASELESS
            if utf8:
                opts |= PCRE2_UTF_BIT
            try:
                rx = P.compile(spliced, opts)
                got = rx.search(subj, 0)
            except Exception as e:                          # noqa: BLE001
                print("FAIL %s:%d oracle could not answer %r: %s"
                      % (path, lineno, spliced, e))
                stats["fail"] += 1
                continue
            want_match = m.group(1) == "m"
            if want_match:
                ok = got is not None and got[0] == (int(m.group(3)), int(m.group(4)))
            else:
                ok = got is None
            if ok:
                stats["pass"] += 1
            else:
                print("FAIL %s:%d pattern %r spliced %r subject %r: "
                      "file says %s, libpcre2 says %s"
                      % (path, lineno, pattern, spliced, subj,
                         line.split()[0], got))
                stats["fail"] += 1


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: verify_vars.py <file.rxt>...\n")
        return 2
    stats = {"pass": 0, "fail": 0, "skip_op": 0,
             "skip_unset": 0, "skip_esc": 0}
    for path in sys.argv[1:]:
        check_file(path, stats)
    print("verify_vars: libpcre2 %s" % P.version())
    print("checked: %d agree, %d disagree" % (stats["pass"], stats["fail"]))
    print("oracle-less by construction: %d refusal cell(s), "
          "%d no-splice-exists, %d pattern-esc"
          % (stats["skip_unset"], stats["skip_op"], stats["skip_esc"]))
    # [MECH-REACH] A SWEEP THAT CHECKED NOTHING READS EXACTLY LIKE A SWEEP
    # THAT FOUND NOTHING WRONG, so an empty checked population is a failure
    # here (K35). The floor is deliberately a SHAPE-derived minimum and not
    # the current count: tests/vars/ carries several files of plain SET
    # cells, so anything under ten means the extraction stopped reaching
    # them rather than that the corpus shrank.
    if stats["pass"] < 10:
        print("FAIL: the sweep checked only %d cell(s) — its extraction has "
              "stopped reaching the corpus, which reads identically to "
              "finding nothing wrong ([MECH-REACH]/K35)" % stats["pass"])
        return 1
    return 1 if stats["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
