#!/usr/bin/env python3
"""
Dev tool (not part of the harness-run deliverable): builds the .rxt files in
this directory by querying real libpcre2 (via lib_pcre2.py) for every
expectation at construction time, so every m/n/ms/ns/g/gp line is correct
by construction. oracle.py is the independent re-checker a reviewer runs
against the *committed* .rxt text -- it does not import or trust this
script. Re-run this file only to regenerate; hand-edits to the .rxt files
are expected to happen too and oracle.py is what re-validates those.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_pcre2 as P

HERE = os.path.dirname(os.path.abspath(__file__))


def esc_subject(b: bytes) -> str:
    out = []
    for byte in b:
        if byte == 0x22:
            out.append('\\"')
        elif byte == 0x5C:
            out.append('\\\\')
        elif byte == 0x0A:
            out.append('\\n')
        elif byte == 0x09:
            out.append('\\t')
        elif byte == 0x0D:
            out.append('\\r')
        elif byte == 0x0C:
            out.append('\\f')
        elif byte == 0x0B:
            out.append('\\v')
        elif 0x20 <= byte < 0x7F:
            out.append(chr(byte))
        else:
            out.append('\\x%02x' % byte)
    return ''.join(out)


class Gen:
    def __init__(self, path, header_comment):
        self.path = path
        self.lines = [header_comment, ""]
        self.n_blocks = 0
        self.n_cases = 0

    def raw(self, text=""):
        self.lines.append(text)

    def block(self, pattern, features=None, flags_i=False, comment=None):
        self.n_blocks += 1
        if comment:
            self.raw(f"# {comment}")
        self.raw(f"pattern {pattern}")
        if flags_i:
            self.raw("flags i")
        if features:
            self.raw(f"features {features}")
        return pattern.encode('utf-8'), flags_i

    def case(self, pat_bytes, subject: bytes, startpos=0, caseless=False, groups=None,
              note=None, expect_nomatch=None):
        """Query the oracle live and emit the matching m/n/ms/ns (+g) line(s).
        expect_nomatch, if given (True/False), is a self-check: raises if the
        oracle's verdict doesn't match what the case was designed to
        demonstrate, so a wrong assumption is caught at generation time
        rather than silently landing in the corpus."""
        self.n_cases += 1
        try:
            r = P.match(pat_bytes, subject, startpos, caseless)
        except P.Pcre2CompileError as e:
            raise RuntimeError(f"case() called on a pattern libpcre2 REJECTS: "
                                f"{pat_bytes!r} -- {e}") from e
        subj_str = esc_subject(subject)
        if note:
            self.raw(f"# {note}")
        if r is None:
            if expect_nomatch is False:
                raise RuntimeError(f"expected a MATCH but oracle says no match: "
                                    f"{pat_bytes!r} on {subject!r} @{startpos}")
            if startpos == 0:
                self.raw(f'n "{subj_str}"')
            else:
                self.raw(f'ns {startpos} "{subj_str}"')
        else:
            if expect_nomatch is True:
                raise RuntimeError(f"expected NO MATCH but oracle found one: "
                                    f"{pat_bytes!r} on {subject!r} @{startpos} -> {r}")
            s, e = r[0]
            if startpos == 0:
                self.raw(f'm "{subj_str}" {s} {e}')
            else:
                self.raw(f'ms {startpos} "{subj_str}" {s} {e}')
            if groups:
                for slot in groups:
                    pair = r[slot] if slot < len(r) else None
                    if pair is None:
                        self.raw(f'g {slot} -1 -1')
                    else:
                        self.raw(f'g {slot} {pair[0]} {pair[1]}')
        return r

    def blank(self):
        self.raw("")

    def perr_oracle(self, pattern, features=None, comment=None):
        """A perr block whose rejection is checked against libpcre2 itself
        (a genuine PCRE2 syntax error, in scope for the oracle)."""
        self.n_blocks += 1
        err = P.compile_error(pattern.encode('utf-8'))
        if err is None:
            raise RuntimeError(f"perr_oracle: libpcre2 ACCEPTS {pattern!r}, expected a reject")
        if comment:
            self.raw(f"# {comment} (libpcre2 error {err[0]}: {err[2]})")
        self.raw(f"pattern {pattern}")
        if features:
            self.raw(f"features {features}")
        self.raw("perr")

    def perr_gate(self, pattern, features=None, comment=None):
        """A perr block asserting pcrec's OWN feature-gate refusal -- not a
        PCRE2 concept, so oracle.py skips it (marked via the comment line
        immediately above `pattern`, per its own convention)."""
        self.n_blocks += 1
        if comment:
            self.raw(f"# {comment}")
        self.raw("# pcrec-gate-only")
        self.raw(f"pattern {pattern}")
        if features:
            self.raw(f"features {features}")
        self.raw("perr")

    def write(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.lines).rstrip('\n') + '\n')
        print(f"wrote {self.path}: {self.n_blocks} blocks, {self.n_cases} m/n cases")


# ============================================================================
# File 1: \A \z \Z -- absolute anchors
# ============================================================================
g = Gen(os.path.join(HERE, "anchors_abs.rxt"), """\
# tests/assertions/d27/anchors_abs.rxt -- D27-blinded corpus for \\A, \\z, \\Z.
#
# Author was blind to pcrec's src/ and existing tests/ (D27); every
# expectation here is computed from real libpcre2 (see ../oracle.py, which
# re-checks this file mechanically -- do not hand-edit a number without
# re-running it). options=0 throughout except where `flags i` appears.
#
# \\A: start of subject, unconditionally, regardless of startpos.
# \\z: end of subject, unconditionally.
# \\Z: end of subject, OR immediately before a final newline that is the
#      subject's very last byte (PCRE2's carve-out; a second trailing
#      newline defeats it -- measured below, not assumed).""")

pat, cl = g.block(r'\Aabc', features='assertions',
                   comment='\\A anchors to absolute offset 0 -- unaffected by startpos (contrast base ^, which has the same rule; match_api.md S3.1).')
g.case(pat, b"abc", 0)
g.case(pat, b"xabc", 0, expect_nomatch=True)
g.case(pat, b"xabc", 1, note='startpos=1 does NOT relocate \\A\'s anchor to 1 -- still requires absolute 0.', expect_nomatch=True)
g.case(pat, b"abcabc", 3, note='same point: a second literal "abc" at offset 3 is not "the start of the subject".', expect_nomatch=True)
g.blank()

pat, cl = g.block(r'\A(cat|dog)', features='assertions', comment='\\A composed with alternation.')
g.case(pat, b"cat", 0, groups=[1])
g.case(pat, b"dog", 0, groups=[1])
g.case(pat, b"xcat", 0, expect_nomatch=True)
g.case(pat, b"catcat", 0, groups=[1])
g.blank()

pat, cl = g.block(r'\A[a-c]+', features='assertions', comment='\\A composed with a character class + quantifier.')
g.case(pat, b"cba123", 0)
g.case(pat, b"123abc", 0, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'(\Aa)+', features='assertions',
                   comment='\\A inside a repeated group: only the FIRST iteration can ever be at offset 0, so + can never take a second iteration -- placement x quantifier interaction.')
g.case(pat, b"aaa", 0, groups=[1])
g.case(pat, b"a", 0, groups=[1])
g.case(pat, b"", 0, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'x\Ay', features='assertions',
                   comment='mid-pattern placement: \\A after a mandatory non-empty literal can NEVER hold (offset would have to be both >=1 and ==0) -- an unsatisfiable pattern, not a syntax error.')
g.case(pat, b"xy", 0, expect_nomatch=True)
g.case(pat, b"", 0, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'ab\A', features='assertions', comment='trailing placement: same unsatisfiability from the other side.')
g.case(pat, b"ab", 0, expect_nomatch=True)
g.case(pat, b"", 0, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'\zabc', features='assertions',
                   comment='leading \\z: "abc" would have to occupy zero bytes at the subject\'s end -- unsatisfiable (contrast \\A leading, which IS satisfiable).')
g.case(pat, b"abc", 0, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'abc\z', features='assertions', comment='\\z trailing -- the ordinary, satisfiable placement.')
g.case(pat, b"abc", 0)
g.case(pat, b"abcx", 0, expect_nomatch=True)
g.case(pat, b"xabc", 0)
g.case(pat, b"xabc", 1)
g.case(pat, b"xabc", 4, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'(a\z)+', features='assertions',
                   comment='\\z inside a repeated group: only an iteration landing on the LAST byte can hold, so + effectively collapses to exactly one iteration at the end.')
g.case(pat, b"aaa", 0, groups=[1])
g.case(pat, b"a", 0, groups=[1])
g.case(pat, b"", 0, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'a\Z', features='assertions',
                   comment='\\Z basics, including the ONE-trailing-newline carve-out and its failure to extend to two.')
g.case(pat, b"a", 0)
g.case(pat, b"a\n", 0, note='single trailing newline: carve-out applies.')
g.case(pat, b"a\n\n", 0, note='TWO trailing newlines: carve-out does NOT apply -- \\Z only recognizes being immediately before the subject\'s very last byte when that byte is a newline, not before a run of them.', expect_nomatch=True)
g.case(pat, b"ab", 0, expect_nomatch=True)
g.case(pat, b"aa", 1, note='startpos=1, \\Z with the found "a" ending exactly at the subject end.')
g.blank()

pat, cl = g.block(r'a\Z', features='assertions', comment='\\Z under CRLF: this build\'s libpcre2 default newline convention is LF-only (measured via pcre2_config_8(PCRE2_CONFIG_NEWLINE) -- see README), so \\r\\n is NOT recognized as one newline unit here; the carve-out looks only for a lone final \\n.')
g.case(pat, b"a\r\n", 0, expect_nomatch=True, note='"a" can only match at offset 0-1; \\Z there sees "\\r\\n" (2 bytes) remaining, not a bare final newline -- fails under LF-only convention.')
g.blank()

# Direct \Z vs \z vs (non-multiline) $ comparison triad -- $ needs no module.
for subj, label in [(b"a", "no trailing newline"),
                     (b"a\n", "one trailing newline"),
                     (b"a\n\n", "two trailing newlines")]:
    pat_z, _ = g.block(r'a\Z', features='assertions', comment=f'triad cell ({label}): \\Z')
    g.case(pat_z, subj, 0)
    g.blank()
    pat_lz, _ = g.block(r'a\z', features='assertions', comment=f'triad cell ({label}): \\z')
    g.case(pat_lz, subj, 0)
    g.blank()
    pat_dollar, _ = g.block(r'a$', comment=f'triad cell ({label}): bare $ (base syntax, no module needed) -- non-multiline $ is documented as \\Z-equivalent; this is the direct check.')
    g.case(pat_dollar, subj, 0)
    g.blank()

pat, cl = g.block(r'\Aabc\z', features='assertions',
                   comment='\\A and \\z together == whole-subject-exact-match.')
g.case(pat, b"abc", 0)
g.case(pat, b"abcd", 0, expect_nomatch=True)
g.case(pat, b"xabc", 0, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'\A', features='assertions', comment='empty subject.')
g.case(pat, b"", 0)
pat, cl = g.block(r'\z', features='assertions', comment='empty subject.')
g.case(pat, b"", 0)
pat, cl = g.block(r'\Z', features='assertions', comment='empty subject.')
g.case(pat, b"", 0)
g.blank()

pat, cl = g.block(r'abc\z', features='assertions', comment='boundary of subject: startpos == subject length.')
g.case(pat, b"abc", 3, expect_nomatch=True, note='searching from the very end can never find a nonempty 3-byte match.')
g.blank()

g.write()

# ============================================================================
# File 2: \b \B -- word boundary
# ============================================================================
g = Gen(os.path.join(HERE, "word_boundary.rxt"), """\
# tests/assertions/d27/word_boundary.rxt -- D27-blinded corpus for \\b, \\B.
#
# \\b: a transition between a word char ([A-Za-z0-9_], ASCII, no module
#      dependency on 'classes') and a non-word char (or subject edge).
# \\B: the complement -- NOT such a transition.
# The byte immediately BEFORE startpos is part of the boundary computation
# even though it is before where the search begins (match_api.md's
# startpos contract): a search starting mid-subject still "sees" context.""")

pat, cl = g.block(r'\bcat\b', features='assertions', comment='\\b framing a whole word.')
g.case(pat, b"cat", 0)
g.case(pat, b"a cat sat", 0)
g.case(pat, b"concatenate", 0, expect_nomatch=True, note='"cat" mid-word on both sides -- no boundary at either end.')
g.case(pat, b"cats", 0, expect_nomatch=True, note='trailing \\b fails: s continues the word.')
g.case(pat, b"cat.", 0)
g.blank()

pat, cl = g.block(r'\Bcat', features='assertions', comment='\\B: "cat" NOT preceded by a boundary (mid-word only).')
g.case(pat, b"concatenate", 0)
g.case(pat, b"cat", 0, expect_nomatch=True, note='subject-start IS a boundary (edge counts), so \\B fails here.')
g.case(pat, b" cat", 0, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'\bcat', features='assertions', comment='startpos>0: the byte BEFORE startpos still governs the boundary test, even though the search begins later.')
g.case(pat, b"cat", 0)
g.case(pat, b"xcat", 1, note='byte before offset 1 is "x" (word char); "c" is also a word char -- NO boundary at 1, even though the search starts exactly there.', expect_nomatch=True)
g.case(pat, b" cat", 1, note='byte before offset 1 is a space -- boundary exists at 1.')
g.blank()

pat, cl = g.block(r'\Bcat', features='assertions', comment='startpos>0, mirrored for \\B.')
g.case(pat, b"xcat", 1)
g.case(pat, b" cat", 1, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'\b\w+\b', features='classes,assertions',
                   comment='\\b composed with \\w+ (module classes) -- cross-module composition axis.')
g.case(pat, b"  hello  ", 0)
g.case(pat, b"", 0, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'\b(cat|dog)\b', features='assertions', comment='\\b composed with alternation + group.')
g.case(pat, b"a dog ran", 0, groups=[1])
g.case(pat, b"a doghouse", 0, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'(\bcat\b)+', features='assertions', comment='\\b composed with a quantified group.')
g.case(pat, b"cat", 0, groups=[1])
g.case(pat, b"catcat", 0, expect_nomatch=True, note='no boundary between the two "cat"s -- \\b\\b framing fails to iterate here.')
g.blank()

pat, cl = g.block(r'[a-c]\B', features='assertions', comment='\\b/\\B composed with a character class.')
g.case(pat, b"ab", 0)
g.case(pat, b"a ", 0, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'\b', features='assertions', comment='empty subject: no word char anywhere -- no possible transition, \\b never holds.')
g.case(pat, b"", 0, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'\B', features='assertions', comment='empty subject: vacuously "not a boundary" at position 0.')
g.case(pat, b"", 0)
g.blank()

pat, cl = g.block(r'\b', features='assertions', comment='subject-start and subject-end edges both count as boundaries when adjacent to a word char.')
g.case(pat, b"a", 0)
g.case(pat, b"a", 1, note='startpos at the very end, byte before is a word char, nothing after -- edge counts as a boundary too.')
g.case(pat, b" ", 0, expect_nomatch=True, note='no word char adjacent anywhere -- no boundary exists in an all-non-word subject.')
g.blank()

pat, cl = g.block(r'(?i)\bcat\b', features='modifiers,assertions',
                   comment='\\b under caseless matching -- word-char classification is unaffected by case folding. Caselessness is spelled INLINE ((?i), module \'modifiers\') rather than via the .rxt `flags i` directive: the in-tree libpcre2 checker that re-verifies this directory on every `make test` is deliberately pinned at options=0 with no caseless mode (project-wide: "adopting any flag is a deliberate re-measurement event"), so a `flags i` cell here would be unverifiable by that checker even though it is oracle-true. The inline spelling keeps the same coverage intent (caseless composed with \\b) fully checkable at options=0 by any PCRE2 oracle, in-tree or this one.')
g.case(pat, b"CAT", 0)
g.blank()

g.write()

# ============================================================================
# File 3: (?m) -- multiline ^ and $, scoping, toggling
# ============================================================================
g = Gen(os.path.join(HERE, "multiline.rxt"), """\
# tests/assertions/d27/multiline.rxt -- D27-blinded corpus for (?m).
#
# IMPORTANT pcrec-specific finding (see ../README.md FINDINGS): (?m) is
# gated by TWO modules in pcrec, not one. The group syntax "(?m...)" itself
# is base to module 'modifiers' (already default-enabled via std1); the
# MULTILINE MATCHING EFFECT is separately gated by module 'assertions'.
# `features modifiers,assertions` is required for every positive cell
# below; the gating/ directory-adjacent perr cells in gating.rxt exercise
# each partial combination on its own.
#
# (?m) makes ^ match at the start of the subject AND immediately after
# every internal newline; $ matches at the end of the subject (or before a
# trailing newline, like non-multiline $/\\Z) AND immediately before every
# internal newline. Verified against real libpcre2 throughout.""")

FEAT = 'modifiers,assertions'

pat, cl = g.block(r'(?m)^a', features=FEAT, comment='multiline ^ at subject start (ordinary case).')
g.case(pat, b"a", 0)
g.case(pat, b"xa", 0, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'(?m)^b', features=FEAT, comment='multiline ^ after an internal newline.')
g.case(pat, b"a\nb", 0)
g.case(pat, b"a\nb", 2)
g.blank()

pat, cl = g.block(r'(?m)a$', features=FEAT, comment='multiline $ before an internal newline.')
g.case(pat, b"a\nb", 0)
g.blank()

pat, cl = g.block(r'(?m)^$', features=FEAT, comment='multiline ^$ matching an EMPTY line between two newlines.')
g.case(pat, b"a\n\nb", 0)
g.case(pat, b"a\n\nb", 2)
g.blank()

pat, cl = g.block(r'(?m)^', features=FEAT, comment='every ^ position, walked one startpos at a time -- one trailing newline.')
g.case(pat, b"a\n", 0)
g.case(pat, b"a\n", 1)
g.case(pat, b"a\n", 2, expect_nomatch=True,
       note='right after the SINGLE trailing newline, at the true subject end: NOT a valid ^ position -- the mirror of \\Z\'s "final newline" carve-out (a) above, this time for ^ rather than $. Cross-verified in isolated subprocess calls (README FINDINGS) after an unrelated transient ctypes read looked otherwise once.')
g.blank()

pat, cl = g.block(r'(?m)^', features=FEAT,
                   comment='every ^ position -- TWO trailing newlines. Position 2 (between the two \\n bytes) is NOT the subject\'s final newline -- it is a genuine internal empty-line start and DOES count. Position 3 (true end, right after the SECOND/final \\n) is the same carve-out as the single-newline case above and does NOT count.')
g.case(pat, b"a\n\n", 0)
g.case(pat, b"a\n\n", 1, note='unanchored from 1: the nearest valid ^ ahead is position 2 (an internal empty line), not 1 itself.')
g.case(pat, b"a\n\n", 2, note='position 2 itself: valid -- it is followed by more subject (the second \\n), so it is not the end-of-subject carve-out.')
g.case(pat, b"a\n\n", 3, expect_nomatch=True, note='position 3: true subject end, immediately after the FINAL newline -- carve-out applies, no match.')
g.blank()

pat, cl = g.block(r'(?m:^a)$', features=FEAT, comment='SCOPED (?m:...): multiline applies only to the ^ inside the group; the $ OUTSIDE the group is still non-multiline (subject-end/before-final-newline only).')
g.case(pat, b"xa\nb", 0, expect_nomatch=True,
       note='the scoped ^a can only hold at offset 0 (char is "x", fails) or offset 3 (right after the internal \\n, char is "b", fails) -- never matches "a" at all.')
g.case(pat, b"a\nb", 0, expect_nomatch=True,
       note='scoped ^a DOES match at offset 0 ("a" at subject start); but the outer, non-multiline $ then has to hold at offset 1, where "\\nb" remains -- not end-of-subject and not immediately before a bare trailing newline, so $ fails and the whole pattern fails.')
g.blank()

pat, cl = g.block(r'^a(?m:$)', features=FEAT, comment='mirror of the above: ^ OUTSIDE the group stays non-multiline (subject start only), $ INSIDE is multiline.')
g.case(pat, b"a\nb", 0)
g.blank()

pat, cl = g.block(r'(?m)^a(?-m)^b', features=FEAT, comment='mid-pattern (?-m) toggling OFF: after the switch, ^ reverts to non-multiline (subject-start only) for the REST of the pattern.')
g.case(pat, b"a\nb", 0, expect_nomatch=True, note='second ^ (now non-multiline) cannot hold at offset 2, only at absolute offset 0 -- and offset 0 is already consumed by the first ^a.')
g.blank()

pat, cl = g.block(r'(?m)^a(?-m:^b)', features=FEAT, comment='(?-m:...) as a SCOPED off-switch (contrast the unscoped (?-m) above): identical outcome here since nothing follows the group.')
g.case(pat, b"a\nb", 0, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'(?m)^(a|b)$', features=FEAT, comment='(?m) composed with alternation + a capturing group, per line.')
g.case(pat, b"x\na\nc", 0, groups=[1])
g.case(pat, b"x\na\nc", 2, groups=[1])
g.blank()

pat, cl = g.block(r'(?m)^a+$', features=FEAT, comment='(?m) composed with a quantifier.')
g.case(pat, b"x\naaa\nc", 2)
g.blank()

pat, cl = g.block(r'(?m)^[a-c]$', features=FEAT, comment='(?m) composed with a character class.')
g.case(pat, b"x\nb\nc", 2)
g.blank()

pat, cl = g.block(r'(?m)^a$', features=FEAT, comment='\\A and \\Z are UNAFFECTED by (?m) -- there is no multiline variant of either; this block is the ^$ pair for direct contrast against the next two blocks.')
g.case(pat, b"x\na\nc", 2)
g.blank()

pat, cl = g.block(r'(?m)\Aa', features=FEAT, comment='\\A stays absolute-start-only even with (?m) active.')
g.case(pat, b"x\na\nc", 2, expect_nomatch=True)
g.case(pat, b"a\nc", 0)
g.blank()

pat, cl = g.block(r'(?m)a\Z', features=FEAT, comment='\\Z stays end-of-subject-only (with its usual single-trailing-newline carve-out) even with (?m) active -- it does NOT gain per-line semantics.')
g.case(pat, b"x\na\nc", 2, expect_nomatch=True, note='"a" at offset 2 is followed by "\\nc", not the subject end or a bare trailing newline -- \\Z fails even though (?m)^$ would have matched here.')
g.case(pat, b"x\nc\na", 4)
g.blank()

g.write()

# ============================================================================
# Shared: the find-all loop (docs/spec/match_api.md S3.1), used for both
# \G and \K loop coverage below. The advance is off the match's own START
# (caps[0][0]) for an empty match, NOT off the loop's own position variable
# -- getting this backwards was caught and fixed during generation (see
# README FINDINGS / dev notes): it silently produced extra, wrong hops
# until cross-checked against match_api.md's own worked \K examples
# ("ab\\K over 'ababab' reports 2,2 6,6").
# ============================================================================
def findall_loop(pat_bytes, subject, caseless=False, max_hops=12):
    p = 0
    n = len(subject)
    hops = []
    while p <= n and len(hops) < max_hops:
        r = P.match(pat_bytes, subject, p, caseless)
        if r is None:
            hops.append((p, None))
            break
        s, e = r[0]
        hops.append((p, r))
        p = e if e > s else (s + 1)
    return hops


def emit_loop(g, pat, subject, groups=None):
    """Emit one block's worth of ms/ns cases replaying the find-all loop by
    hand (the .rxt format has no native find-all primitive -- see README)."""
    hops = findall_loop(pat, subject)
    for p, r in hops:
        if r is None:
            if p == 0:
                g.raw(f'n "{esc_subject(subject)}"')
            else:
                g.raw(f'ns {p} "{esc_subject(subject)}"')
        else:
            s, e = r[0]
            if p == 0:
                g.raw(f'm "{esc_subject(subject)}" {s} {e}')
            else:
                g.raw(f'ms {p} "{esc_subject(subject)}" {s} {e}')
            if groups:
                for slot in groups:
                    pair = r[slot] if slot < len(r) else None
                    if pair is None:
                        g.raw(f'g {slot} -1 -1')
                    else:
                        g.raw(f'g {slot} {pair[0]} {pair[1]}')
    g.n_cases += len(hops)
    return hops


# ============================================================================
# File 4: \G -- first matching position, nonzero startpos, find-all loop
# ============================================================================
g = Gen(os.path.join(HERE, "gstart.rxt"), """\
# tests/assertions/d27/gstart.rxt -- D27-blinded corpus for \\G.
#
# \\G asserts "current position == the startpos this search call was given".
# Under docs/spec/match_api.md S3.1's find-all loop (which threads its
# resume position as the next call's startpos), that makes \\G mean
# "contiguous with the previous match" -- a TOKENIZER, stopping at the
# first gap, in contrast to a \\G-free pattern which is a scanner. The
# .rxt format has no native find-all primitive, so a loop is replayed by
# hand as a sequence of ms/ns cases at the positions the loop itself would
# visit (see mkcorpus.py's emit_loop/findall_loop, which implements
# match_api.md's exact algorithm -- including the "advance off the match's
# own START on an empty match" rule, not off the loop variable).""")

pat, cl = g.block(r'\Ga', features='assertions', comment='\\G at a specific nonzero startpos: matches iff the pattern holds AT that exact offset.')
g.case(pat, b"xa", 1)
g.case(pat, b"xa", 0, expect_nomatch=True, note='\\G requires the CURRENT startpos to equal itself -- trivially true at whatever startpos is given -- but the match must begin exactly there; at startpos=0 the subject starts with "x", not "a".')
g.case(pat, b"axa", 2)
g.blank()

pat, cl = g.block(r'\G.', features='assertions', comment='find-all loop, one character at a time (base "." needs no extra module) -- the plain tokenizer case.')
emit_loop(g, pat, b"abc")
g.blank()

pat, cl = g.block(r'\G(cat|dog)', features='assertions', comment='find-all loop composed with alternation + a capturing group: two full hops, then the gap stops it.')
emit_loop(g, pat, b"catdog", groups=[1])
g.blank()

pat, cl = g.block(r'\G\w+', features='classes,assertions',
                   comment='the exact worked example docs/spec/match_api.md S3.1 cites: \\G\\w+ is a TOKENIZER on "ab ab ab", reporting only the first token and then stopping at the space (a \\G-free \\w+ would be a scanner and find all three).')
emit_loop(g, pat, b"ab ab ab")
g.blank()

pat, cl = g.block(r'\G\d+', features='classes,assertions', comment='find-all loop composed with a quantified class, several real hops before the gap.')
emit_loop(g, pat, b"12 34 5x6")
g.blank()

pat, cl = g.block(r'\Ga\Kb', features='assertions', comment='\\G composed with \\K: \\G still requires contiguity from the PREVIOUS match end, but \\K still resets what gets REPORTED as this match\'s own start.')
g.case(pat, b"ab", 0, note='single call, not a loop: \\G holds at startpos=0 (subject start), "a" consumes to 1, \\K resets the report marker to 1, "b" consumes to 2 -- reported span is [1,2), not [0,2).')
g.blank()

pat, cl = g.block(r'\Ga', features='assertions', comment='empty subject / boundary of subject for \\G.')
g.case(pat, b"", 0, expect_nomatch=True)
g.case(pat, b"a", 1, expect_nomatch=True, note='startpos == subject length: \\G holds trivially (current pos == startpos), but there is no "a" left to consume.')
g.blank()

pat, cl = g.block(r'\G', features='assertions', comment='bare \\G, empty subject: current pos (0) trivially equals startpos (0).')
g.case(pat, b"", 0)
g.blank()

g.write()

# ============================================================================
# File 5: \K -- resetting the reported match start
# ============================================================================
g = Gen(os.path.join(HERE, "kreset.rxt"), """\
# tests/assertions/d27/kreset.rxt -- D27-blinded corpus for \\K.
#
# \\K resets the REPORTED start of the match (caps[0][0] / ovector[0]) to
# the current position, without affecting: what already-closed capturing
# groups recorded (checked below), whether the match is anchored, or how
# far the engine has actually consumed. It has NO effect on any group's
# own span -- only on the whole-match report. Multiple \\K in one
# alternative: the LAST one executed on the winning path wins. \\K inside
# a quantified group: the FINAL iteration's \\K wins. options=0 throughout;
# every case cross-checked against real libpcre2.""")

pat, cl = g.block(r'a\Kb', features='assertions', comment='basic \\K: reported start moves past "a".')
g.case(pat, b"ab", 0)
g.case(pat, b"xab", 0)
g.blank()

pat, cl = g.block(r'(a\K)b', features='assertions', comment='\\K INSIDE a group, at the group\'s own close: the group\'s own span is UNCHANGED by \\K (it still reports what it captured); only the overall report moves.')
g.case(pat, b"ab", 0, groups=[1])
g.blank()

pat, cl = g.block(r'(a)\Kb', features='assertions', comment='\\K AFTER a closed group: same non-effect on the group\'s own span, from the other side.')
g.case(pat, b"ab", 0, groups=[1])
g.blank()

pat, cl = g.block(r'a\Kb\Kc', features='assertions', comment='MULTIPLE \\K in sequence: only the LAST one executed on the winning path determines the report.')
g.case(pat, b"abc", 0)
g.blank()

pat, cl = g.block(r'(a\Kb|c\Kd)', features='assertions', comment='\\K inside EACH branch of an alternation: whichever branch wins, ITS \\K governs -- and the group\'s own span still covers the whole alternative regardless.')
g.case(pat, b"ab", 0, groups=[1])
g.case(pat, b"cd", 0, groups=[1])
g.blank()

pat, cl = g.block(r'(a\K)+b', features='assertions', comment='\\K under a QUANTIFIER: each iteration resets the marker, so only the FINAL iteration\'s \\K survives into the report -- the group itself (per R22 cross-iteration rules, not \\K-specific) retains its LAST iteration\'s own span too.')
g.case(pat, b"aaab", 0, groups=[1])
g.case(pat, b"ab", 0, groups=[1])
g.blank()

pat, cl = g.block(r'\A(a\Kb)+\z', features='assertions', comment='\\K under a quantifier, anchored both ends: reported start is the LAST iteration\'s \\K position, group span is the LAST iteration\'s own match.')
g.case(pat, b"abab", 0, groups=[1])
g.blank()

pat, cl = g.block(r'\b\K\w+', features='classes,assertions', comment='\\K immediately after a zero-width assertion (\\b): no visible difference from \\b alone here (both zero-width, same position) -- included as the "immediately after a boundary" placement case.')
g.case(pat, b"  cat  ", 0)
g.blank()

pat, cl = g.block(r'(?m)^a\Kb$', features='modifiers,assertions', comment='\\K composed with (?m): resets the report within one multiline-delimited line.')
g.case(pat, b"ab\nc", 0)
g.case(pat, b"a\nab\nc", 2)
g.blank()

pat, cl = g.block(r'ab\K', features='assertions', comment='\\K producing an EMPTY reported span after consuming real bytes (match_api.md S3.1\'s own headline example for why the find-all loop\'s empty-match arm keys off caps[0][0], not the loop variable).')
g.case(pat, b"ababab", 0)
g.blank()

pat, cl = g.block(r'ab\K', features='assertions', comment='find-all loop over the same pattern: exactly the two hops docs/spec/match_api.md S3.1 quotes verbatim ("2,2 6,6") -- reproduced here from a fresh libpcre2 measurement, not copied from the doc.')
emit_loop(g, pat, b"ababab")
g.blank()

pat, cl = g.block(r'a\Kb', features='assertions', comment='find-all loop, non-empty \\K reports throughout ("1,2 3,4 5,6" per the same spec passage).')
emit_loop(g, pat, b"ababab")
g.blank()

pat, cl = g.block(r'a\Kb', features='assertions', comment='empty subject / boundary: \\K needs something to consume up to it in this pattern, so an empty subject cannot match at all.')
g.case(pat, b"", 0, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'\K', features='assertions', comment='bare \\K alone: zero-width, always succeeds at the position it\'s tried, report start/end both equal that position.')
g.case(pat, b"", 0)
g.case(pat, b"xyz", 0)
g.blank()

g.write()

# ============================================================================
# File 6: cross-construct composition (2+ of the eight together)
# ============================================================================
g = Gen(os.path.join(HERE, "composition.rxt"), """\
# tests/assertions/d27/composition.rxt -- D27-blinded corpus: constructs
# from the assertions module composed with EACH OTHER (not just with
# alternation/quantifiers/groups/classes, which every other file in this
# corpus already exercises alongside its own primary construct).""")

pat, cl = g.block(r'\A\bfoo\b\z', features='assertions', comment='\\A + \\b + \\b + \\z: the whole subject must be exactly one word "foo".')
g.case(pat, b"foo", 0)
g.case(pat, b"xfoo", 0, expect_nomatch=True)
g.case(pat, b"foo!", 0, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'(?m)^\bfoo\b$', features='modifiers,assertions', comment='(?m) + \\b + \\b, per line.')
g.case(pat, b"x\nfoo\ny", 0)
g.case(pat, b"x\nfoo\ny", 2)
g.blank()

pat, cl = g.block(r'\Gcat\Kdog', features='assertions', comment='\\G + \\K together: \\G pins the whole match\'s start to the call\'s startpos; \\K then moves only what gets REPORTED.')
g.case(pat, b"catdog", 0)
g.blank()

pat, cl = g.block(r'\B\Kcat', features='assertions', comment='\\B + \\K: reset placed right after a negative boundary check.')
g.case(pat, b"concatenate", 0)
g.blank()

pat, cl = g.block(r'\A(a\Kb)+\z', features='assertions', comment='\\A + \\K-under-quantifier + \\z, cross-checked against the single-construct file\'s own version of this pattern (kreset.rxt) -- included here for the composition axis explicitly.')
g.case(pat, b"abab", 0, groups=[1])
g.case(pat, b"ababx", 0, expect_nomatch=True)
g.blank()

pat, cl = g.block(r'(?m)^\Ga', features='modifiers,assertions', comment='(?m)^ + \\G together: both must hold at the same position -- \\G pins it to startpos, ^ additionally requires a real line start there.')
g.case(pat, b"a", 0)
g.case(pat, b"x\na", 2)
g.case(pat, b"x\nxa", 3, expect_nomatch=True, note='\\G holds trivially at startpos=3 (equals itself), but (?m)^ does not -- offset 3 is mid-line, not right after the \\n at offset 1.')
g.blank()

pat, cl = g.block(r'\b(?:cat|dog)\B', features='assertions', comment='\\b (leading, positive) + \\B (trailing, negative) on the SAME word: word must start at a boundary and continue past its nominal end without one.')
g.case(pat, b"cats", 0)
g.case(pat, b"cat dog", 0, expect_nomatch=True, note='"cat" ends at a boundary (space follows) -- \\B fails there; "dog" ends at true subject end, also a boundary -- \\B fails there too. Neither alternative can satisfy the trailing \\B.')
g.blank()

g.write()

# ============================================================================
# File 7: syntax-error spellings PCRE2 itself rejects (oracle-checked)
# ============================================================================
g = Gen(os.path.join(HERE, "syntax_errors.rxt"), """\
# tests/assertions/d27/syntax_errors.rxt -- spellings that are genuine PCRE2
# SYNTAX errors (libpcre2 rejects at compile time), not merely pcrec
# feature-gate refusals. Every perr block here is checked by ../oracle.py
# against libpcre2's own compile verdict -- see the per-block comment for
# the exact libpcre2 errorcode/message it measured. Contrast gating.rxt,
# where the perr blocks are pcrec POLICY (module-gating) rather than PCRE2
# syntax facts, and are marked `# pcrec-gate-only` so oracle.py skips them
# rather than mis-scoring pcrec's own design choice as a PCRE2 fact.
#
# The common thread below: every bare zero-width assertion in this module
# is UNREPEATABLE -- PCRE2 error 109 ("quantifier does not follow a
# repeatable item"), the same error a bare quantified ^ already gets
# (docs/testing.md's own U-series note). All eight are checked, greedy and
# lazy forms both, plus one \\K-specific restriction (error 199) that
# exists independently of pcrec's own module-implementation status.""")

for tok, name in [(r'\A', 'A'), (r'\z', 'z'), (r'\Z', 'Z'), (r'\b', 'b'),
                   (r'\B', 'B'), (r'\G', 'G'), (r'\K', 'K')]:
    g.perr_oracle(tok + '*', features='assertions', comment=f'\\{name} is a bare zero-width assertion -- unrepeatable, greedy *.')
    g.perr_oracle(tok + '+', features='assertions', comment=f'\\{name} unrepeatable, greedy +.')
    g.perr_oracle(tok + '?', features='assertions', comment=f'\\{name} unrepeatable, greedy ?.')
    g.perr_oracle(tok + '{2,3}', features='assertions', comment=f'\\{name} unrepeatable, bounded {{2,3}}.')
    g.perr_oracle(tok + '*?', features='assertions', comment=f'\\{name} unrepeatable, LAZY *? -- laziness does not change the "nothing to repeat" verdict.')
    g.blank()

g.perr_oracle(r'(?m)*', features='modifiers,assertions', comment='an inline-option group is likewise unrepeatable as a bare token.')
g.blank()

g.perr_oracle(r'(?<=a\Kb)c', features='assertions,lookaround',
              comment='\\K specifically is forbidden inside ANY lookaround (PCRE2 error 199), independent of the "nothing to repeat" family above. pcrec today refuses this pattern anyway (lookaround is UNIMPLEMENTED -- module enabled but "(?<...) is not implemented yet", a different diagnostic) -- both are nonzero exit so this perr passes either way; once lookaround lands, this cell is the one that starts checking whether pcrec ALSO enforces PCRE2\'s own \\K-in-lookaround restriction rather than silently mismatching it.')
g.blank()

g.write()

# ============================================================================
# File 8: feature-gate refusal direction (pcrec policy, not PCRE2 syntax)
# ============================================================================
g = Gen(os.path.join(HERE, "gating.rxt"), """\
# tests/assertions/d27/gating.rxt -- MOD-0.3c feature-gating, the refusal
# direction the brief asked for: without --features assertions (or,
# for (?m), the RIGHT combination of modules), each construct must be
# refused naming the missing module; with it, it must compile.
#
# pcrec-specific finding (see ../README.md FINDINGS): (?m) needs BOTH
# 'modifiers' (for the inline-option GROUP SYNTAX itself, already
# default-enabled via std1) and 'assertions' (for the MULTILINE MATCHING
# EFFECT) -- neither module alone is sufficient, and the two failure modes
# report genuinely different diagnostics (measured below). This is a
# two-module construct, unlike the other seven in this corpus, and the
# brief's "each construct... must refuse naming the module" (singular)
# does not quite fit it -- the four gating cells for (?m) below are the
# reason this file documents the shape explicitly rather than folding it
# into a one-line-per-construct table.
#
# Every perr block in this file is `# pcrec-gate-only`: it is pcrec POLICY
# (a module gate), not a PCRE2 syntax fact, so ../oracle.py skips it rather
# than mis-scoring a design choice as if it were a PCRE2 compile verdict
# (libpcre2 has no module system and accepts all eight constructs
# unconditionally at options=0).""")

g.raw("# --- \\A \\z \\Z \\b \\B \\G \\K: refused without module 'assertions' ---")
g.blank()
for tok, name in [(r'\A', 'A'), (r'\z', 'z'), (r'\Z', 'Z'), (r'\b', 'b'),
                   (r'\B', 'B'), (r'\G', 'G'), (r'\K', 'K')]:
    g.perr_gate(tok + 'x', comment=f'\\{name}, DEFAULT features (std1 = classes,modifiers): refused, names module \'assertions\'. (bare \\{name} alone, with nothing to match after it, is also refused the same way -- this uses a trailing literal only so the same spelling is reusable as a positive-compile smoke pattern below.)')
    g.blank()
for tok, name in [(r'\A', 'A'), (r'\z', 'z'), (r'\Z', 'Z'), (r'\b', 'b'),
                   (r'\B', 'B'), (r'\G', 'G'), (r'\K', 'K')]:
    g.perr_gate(tok + 'x', features='none', comment=f'\\{name}, --features none: refused, same as default (assertions was never in std1).')
    g.blank()

g.raw("# --- \\A \\z \\Z \\b \\B \\G \\K: compile cleanly WITH module 'assertions' ---")
g.blank()
for tok, name, subj, s, e in [
    (r'\Ax', 'A', b"x", 0, 1), (r'x\z', 'z', b"x", 0, 1), (r'x\Z', 'Z', b"x", 0, 1),
    (r'\bx', 'b', b"x", 0, 1), (r'x\By', 'B', None, None, None),  # handled specially below
    (r'\Gx', 'G', b"x", 0, 1), (r'x\K', 'K', b"x", 1, 1),
]:
    if tok == r'x\By':
        pat, cl = g.block(tok, features='assertions', comment=f'\\{name} compiles and matches with module \'assertions\' enabled.')
        g.case(pat, b"xy", 0)
        g.blank()
        continue
    pat, cl = g.block(tok, features='assertions', comment=f'\\{name} compiles and matches with module \'assertions\' enabled.')
    g.case(pat, subj, 0)
    g.blank()

g.raw("# --- (?m): the two-module construct ---")
g.blank()

g.perr_gate(r'(?m)^a', comment='(?m), DEFAULT features (std1 includes \'modifiers\', so the (?m...) GROUP parses) -- but its MULTILINE EFFECT is refused, naming module \'assertions\' specifically (not \'modifiers\', which is already satisfied). Distinct diagnostic text from the next cell -- see README FINDINGS for both, verbatim.')
g.blank()
g.perr_gate(r'(?m)^a', features='none', comment='(?m), --features none: refused at the GROUP SYNTAX itself this time, naming module \'modifiers\' -- a different failure point than the std1-default cell above, because now neither module is enabled.')
g.blank()
g.perr_gate(r'(?m)^a', features='modifiers', comment='(?m), --features modifiers only (no assertions): same failure point as the std1-default cell above (group syntax is fine, multiline effect is refused) -- confirms it is \'modifiers\' alone that was already doing the work in the default-features cell, not some other std1 member.')
g.blank()
g.perr_gate(r'(?m)^a', features='assertions', comment='(?m), --features assertions only (no modifiers): refused at the GROUP SYNTAX -- the mirror of the previous cell, confirming BOTH modules are independently necessary and neither is sufficient alone.')
g.blank()

pat, cl = g.block(r'(?m)^a', features='modifiers,assertions', comment='(?m) compiles and matches only with BOTH modules enabled together.')
g.case(pat, b"a", 0)
g.blank()

g.write()
print("=== ALL FILES DONE ===")
