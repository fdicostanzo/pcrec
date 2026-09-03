#!/usr/bin/env python3
"""Cross-verify .rxt corpus files against python's `re` module (the base-tier
oracle, decisions.md D4). Usage: verify_rxt.py [files-or-dirs...]; default is
<repo>/tests/base. A comment line `# pcre2-only` immediately before a
`pattern` line skips python verification for that block (used where python re
diverges from real PCRE, e.g. quantified anchors — see docs/testing.md).

[M4.5a] `g <slot> <start> <end>` / `gp <slot> <start> <end>` capture-group
expectation lines (attached to the most recent `m`/`ms` case) are checked
against python re's `match.span(slot)`, identically for 'g' (live) and 'gp'
(pending-VM) — pending-ness is a fact about what pcrec's CURRENT compiled
artifact can deliver (RX_NCAPS), which this oracle has no notion of and does
not need; it verifies the EXPECTATION itself, independent of whether
tests/harness/run.sh can check it yet. See docs/testing.md."""
import re
import sys
import os

BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "base"))

def decode_subject(s):
    # s is the raw text between the outer quotes (quotes already stripped)
    out = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == '\\':
            if i + 1 >= n:
                raise ValueError("trailing backslash in subject")
            nc = s[i+1]
            if nc == '"':
                out.append('"'); i += 2
            elif nc == '\\':
                out.append('\\'); i += 2
            elif nc == 'n':
                out.append('\n'); i += 2
            elif nc == 't':
                out.append('\t'); i += 2
            elif nc == 'r':
                out.append('\r'); i += 2
            elif nc == 'f':
                out.append('\f'); i += 2
            elif nc == 'v':
                out.append('\v'); i += 2
            elif nc == 'x':
                if i + 3 >= n:
                    raise ValueError("bad \\xHH escape")
                hexpart = s[i+2:i+4]
                out.append(chr(int(hexpart, 16)))
                i += 4
            else:
                raise ValueError(f"unknown subject escape \\{nc}")
        else:
            out.append(c)
            i += 1
    return ''.join(out)

def parse_quoted(line):
    """line starts with a double-quote; return (decoded_subject, rest_of_line_after_closing_quote)."""
    assert line[0] == '"'
    i = 1
    raw = []
    n = len(line)
    while i < n:
        c = line[i]
        if c == '\\':
            if i + 1 >= n:
                raise ValueError("trailing backslash before end of line in subject")
            raw.append(line[i:i+2])
            i += 2
        elif c == '"':
            # end of quoted subject
            rest = line[i+1:]
            return decode_subject(''.join(raw)), rest
        else:
            raw.append(c)
            i += 1
    raise ValueError("unterminated quoted subject: " + line)


def parse_startpos_tail(line, prefix):
    """line starts with `<prefix> ` (e.g. 'ms '); return (P, rest_of_line)
    where rest_of_line starts at the quoted subject."""
    rest = line[len(prefix):].lstrip()
    i = 0
    n = len(rest)
    while i < n and rest[i].isdigit():
        i += 1
    if i == 0:
        raise ValueError(f"missing startpos in {prefix!r} line: {line!r}")
    p = int(rest[:i])
    tail = rest[i:].lstrip()
    return p, tail


def parse_group_tail(line, prefix):
    """line starts with `<prefix> ` ('g ' or 'gp '); return (slot, start, end)
    from the remaining `<slot> <start> <end>` tail. RX_UNSET is '-1 -1' in
    BOTH slots — one -1 without the other is a hard parse error, matching
    tests/harness/run.sh's own check."""
    rest = line[len(prefix):].strip()
    parts = rest.split()
    if len(parts) != 3:
        raise ValueError(f"bad {prefix.strip()!r} line tail {rest!r}")
    slot, start, end = int(parts[0]), int(parts[1]), int(parts[2])
    if (start == -1) != (end == -1):
        raise ValueError(f"RX_UNSET must be -1 in BOTH slots, not one: {rest!r}")
    return slot, start, end


# [DD-13b.W1.1 / H4] THE COMPOSED-BLOCK SKIP, and it is STRUCTURAL and
# COUNTED rather than a caught `re.error` (w1_impl DECIDED (4)). python
# `re` has no subroutine call at all -- "not different semantics, an
# ABSENCE" -- so a block whose pattern calls a definition by name cannot
# be verified here, and catching the exception would also swallow every
# genuine corpus typo that happens to raise the same error.
#
# The predicate is: the file declares a block `name`, AND this block's
# pattern carries a by-name reference. Both halves are needed -- a
# by-name reference in a file with no definitions is an ordinary
# unresolvable pattern and should FAIL, not skip.
#
# ITS POPULATION IS ZERO TODAY and this file says so rather than letting
# a green run imply coverage: no corpus file declares a `name`, so the
# skip never fires. It is built now because the SKIP TOTAL is what C3
# compares, and a total that has never had a second contributor is a
# number with one input.
BY_NAME_REF = re.compile(r"\(\?&|\(\?P>|\\g<[A-Za-z_]|\\g'[A-Za-z_]")


def has_by_name_reference(pat):
    return BY_NAME_REF.search(pat) is not None


# [DD-13b.W1.1] THE OWN-ORACLE RULE, implementing a contract the spec has
# stated all along and nothing implemented, because this script never ran.
#
# docs/spec/rxt_format.md: "A directory may name its own additional or
# REPLACEMENT oracle instead of (or beside) the default. tests/assertions/
# is the one directory in the tree whose oracle rule differs by design: it
# carries verify_pcre2.py, a libpcre2 differential that re-checks every
# cell -- marked and unmarked -- on every make test, because several of
# its constructs (\Z, \G, \K) have no python equivalent at all."
#
# MEASURED, and this is why it matters: the first corpus-wide run of this
# oracle produced exactly FIVE genuine answer disagreements, and ALL FIVE
# are in tests/assertions/ -- `a\Z` against "a\n" (python's \Z is PCRE2's
# \z) and `(?m)^` at end-of-subject. Every one is the documented
# divergence, in the one directory documented as having it, already
# covered by libpcre2 at 10,120 cells on every make test.
#
# A DECLARATION, NOT A PATH LIST. The rule is "the directory carries its
# own verifier", discovered by looking -- not `if 'assertions' in path`.
# A new module directory that needs the same treatment gets it by
# following the precedent the spec already points at, with no edit here.
# This script itself is excluded, or tests/harness/ would exempt its own
# giveup.rxt from the oracle that lives beside it.
_OWN_ORACLE_CACHE = {}


def declares_own_oracle(path):
    """True when this file's directory, or any ancestor up to tests/,
    carries a verifier of its own (verify_*.py that is not this script)."""
    d = os.path.dirname(os.path.abspath(path))
    stop = os.path.dirname(BASE_DIR)          # <repo>/tests
    me = os.path.basename(os.path.abspath(__file__))
    seen = []
    while True:
        if d in _OWN_ORACLE_CACHE:
            hit = _OWN_ORACLE_CACHE[d]
            break
        seen.append(d)
        try:
            names = os.listdir(d)
        except OSError:
            names = []
        hit = any(n.startswith('verify_') and n.endswith('.py') and n != me
                  for n in names)
        if hit or d == stop or os.path.dirname(d) == d:
            break
        d = os.path.dirname(d)
    for x in seen:
        _OWN_ORACLE_CACHE[x] = hit
    return hit


IDENT_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

# [DD-13b.W1.3] LEG C OF A THREE-LEG GRAMMAR. A DEFINITION NAME IS NOT AN
# IDENTIFIER any more, and the two rules must stay two: `ident_ok` still
# governs `encoding` (a C identifier, and a value pcrec maps to a backend),
# while `name_ok` governs a block's `name`, which lives in the FILE
# namespace (w1_impl DECIDED (7)) and admits `-` and `.` after the first
# byte -- the manager's ruling on the bench's O-13 section 4(a), where all
# but a handful of pattern ids carry a `-`.
#
# THE THREE LEGS MOVE TOGETHER OR C1 GOES RED, which is what C1 is for:
# leg A is `src/parse/rxt_source.c`'s `defname_ok`, leg B is
# `tests/harness/run.sh`'s `^name[[:space:]]+(...)` arm, leg C is here.
# `-`/`.` are admitted only after the first byte because the name -> prefix
# mapping (`-`/`.` -> `_`) cannot repair a leading one.
NAME_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_.-]*$')


def ident_ok(s):
    """A C identifier. Still the rule for `encoding`; NOT the rule for a
    block `name` since [DD-13b.W1.3] -- see `name_ok`."""
    return bool(IDENT_RE.match(s))


def name_ok(s):
    """The same rule as src/parse/rxt_source.c's `defname_ok`: a definition
    name, which is neither a PCRE2 group name nor (yet) a C identifier."""
    return bool(NAME_RE.match(s))


def prefix_from_name(s):
    """The same mapping as src/parse/rxt_source.c's
    `pcrec_rxt_prefix_from_name`: `-` and `.` become `_`. Not injective --
    that is what the duplicate-prefix refusal exists for."""
    return s.replace('-', '_').replace('.', '_')


def parse_rxt(path):
    """Yield (lineno, kind, data) tuples. kind in {'pattern','m','n','ms','ns','perr','g','gp'}."""
    # [DD-13b.W1.1 r46sem finding 17] `errors='surrogateescape'` makes this
    # parser BYTE-CLEAN like legs A and B, rather than crashing on the
    # first invalid-UTF-8 byte anywhere in the file. Legs A and B both
    # treat bytes opaquely (`rxt_source.c` reads "rb"; bash's `read -r` is
    # byte-clean) and the .rxt escape vocabulary is explicitly byte-
    # oriented ("the escape exists to protect the FRAMING, not to
    # transcode the content", docs/spec/rxt_format.md). `surrogateescape`
    # round-trips every byte through a str without raising, which is the
    # python-native way to keep that property; it does not make this
    # parser understand non-ASCII text, only stop crashing on it.
    with open(path, 'r', encoding='utf-8', errors='surrogateescape') as f:
        lines = f.readlines()
    results = []
    pcre2_only_next = False
    seen_pattern = False
    seen_names = {}
    for lineno, raw_line in enumerate(lines, 1):
        line = raw_line.rstrip('\n')
        if line.strip() == '# pcre2-only':
            pcre2_only_next = True
            continue
        # [DD-13b.W1.1 r46sem finding 15] A WHOLE-LINE-BLANK TEST, not an
        # exact-empty one. `line == ''` missed a line of pure whitespace
        # (docs/spec/rxt_format.md: "Blank lines are ignored", with no
        # carve-out for one that is not literally zero bytes), so a line
        # of two spaces reached the indentation check below and raised —
        # the one parser of three that disagreed with the spec on this.
        # `line.strip() == ''` covers both without changing how an
        # INDENTED COMMENT is treated: a line like `  # x` has a non-empty
        # `.strip()` (`'# x'`), so it still falls through to the
        # indentation check exactly as it did before, matching legs A/B's
        # refusal of an indented `#` (column 1 is the only comment
        # column).
        if line.strip() == '' or line.startswith('#'):
            continue
        # [DD-13b.W1.1] THE HEAD IS NOT THIS PARSER'S, AND IT SAYS SO.
        # The head ends at the first `pattern` line, and pcrec owns its
        # grammar (w1_impl §1.1's seam ruling: the head has exactly ONE
        # parser, and giving this file a second -- a FOURTH in the tree --
        # is precisely what that ruling exists to prevent). So a
        # head-bearing file is REFUSED BY NAME here rather than
        # mis-parsed, and rather than this oracle growing a head reader it
        # would then have to keep in step with pcrec's.
        #
        # MEASURED FREE: 0 of the corpus's 179 files carry a head, so no
        # file reaches this today. It is W1.3's job to close, when a
        # composed file first needs oracling; until then a loud refusal is
        # the honest answer and a silent misparse is not.
        #
        # [DD-13b.W1.1 r46sem finding 16] AND EVERY OTHER FIRST TOKEN,
        # once the file is confirmed headless. A line before any
        # `pattern` that is not one of the named HEAD words used to fall
        # through to its own ordinary branch below (`flags`, `features`,
        # `encoding`, `engine`, `budget`, `perr`, `m`, ...), get appended
        # to `results`, and then be silently DROPPED by `dump_file`'s
        # `if blk is None: continue` — a body directive with no open
        # block to attach to, exactly the shape legs A and B both refuse
        # loudly (`'X' line before any pattern block`, `run.sh`'s
        # `have_block` guard generalisation). The one legitimate case —
        # this line really is a HEAD declaration in a head-bearing file —
        # is exactly the named-word branch just above, so anything that
        # reaches here is the bug shape and not a legitimate head.
        if not seen_pattern:
            first = line.split(None, 1)[0] if line.split() else ''
            head_words = ('lib', 'target', 'config', 'description',
                          'include', 'use', 'oracle', 'tag', 'freq')
            if first in head_words:
                raise ValueError(
                    f"{path}:{lineno}: '{first}' is a file-level (HEAD) "
                    "declaration, and this oracle reads the BODY only -- the "
                    "head grammar has one parser, pcrec's `--list-source`. A "
                    "head-bearing .rxt file is not verifiable by this script "
                    "in this build (DD-13b W1.1; W1.3 closes it)")
            if first != 'pattern':
                raise ValueError(
                    f"{path}:{lineno}: '{first}' line before any pattern "
                    "block -- a body directive has no open block to attach "
                    "to (matches tests/harness/run.sh's and "
                    "src/parse/rxt_source.c's own refusal of this line)")
        if line.startswith(' ') or line.startswith('\t'):
            raise ValueError(
                f"{path}:{lineno}: a pattern block's lines are not indented "
                "(indentation is continuation, and that is a head rule)")
        if line.startswith('pattern '):
            seen_pattern = True
            pat = line[len('pattern '):]
            results.append((lineno, 'pattern', (pat, pcre2_only_next)))
            pcre2_only_next = False
        elif line == 'perr':
            results.append((lineno, 'perr', None))
        elif line.startswith('flags '):
            # [DD-13b.W1.1 r46sem finding 3] VALIDATED AT PARSE TIME, not
            # only in main()'s oracle-check loop below (which the `--dump`
            # path, leg C of the C1 differential, never runs) -- only 'i'
            # is defined (docs/spec/rxt_format.md, tests/harness/run.sh's
            # own arm), and leg C used to accept ANY value here with no
            # check at all, silently mapping only 'i' to re.IGNORECASE and
            # treating everything else as a no-op flag string that meant
            # nothing to python and nothing to the differential either.
            v = line[len('flags '):].strip()
            if v != 'i':
                raise ValueError(f"{path}:{lineno}: unknown flag letter(s) "
                                 f"{v!r} (only 'i' is defined)")
            results.append((lineno, 'flags', v))
        elif line.startswith('features '):
            # [DD-13b.W1] `features only <list>` (M14): the list REPLACES
            # what a config would union in rather than adding to it. The
            # python oracle has no module gate either way (see main), so
            # what this branch is for is that the LINE must parse -- a
            # third parser of the same grammar cannot be a control for the
            # other two on lines it refuses to read.
            v = line[len('features '):].strip()
            only = False
            if v.startswith('only ') or v == 'only':
                only = True
                v = v[len('only'):].strip()
            results.append((lineno, 'features', (v, only)))
        elif line.startswith('name '):
            # [DD-13b.W1.1 r46sem finding 19 / finding 20] leg C used to
            # validate strictly LESS than legs A and B here -- no
            # identifier check at all, so `name 9bad` parsed clean where
            # leg A refuses it ("'name' wants an identifier") and leg B's
            # `[A-Za-z_][A-Za-z0-9_]*` arm doesn't match at all (falling to
            # its own catch-all hard error). A leg that accepts a strict
            # SUPERSET of what its siblings accept can only ever witness a
            # disagreement in one direction. Also enforces the spec's
            # NAME UNIQUENESS rule (finding 20): `name` is in the FILE
            # namespace and must be unique within the file -- previously
            # enforced only by pcrec (`src/parse/rxt_source.c`), which
            # `tests/harness/run.sh` never calls for a headless file (all
            # 179 corpus files today), so nothing in the tree enforced it
            # for the population that actually reaches this oracle.
            v = line[len('name '):].strip()
            if not name_ok(v):
                raise ValueError(f"{path}:{lineno}: 'name' wants a definition "
                                 f"name (got {v!r})")
            if v in seen_names:
                raise ValueError(
                    f"{path}:{lineno}: duplicate block name {v!r} (already "
                    f"named on line {seen_names[v]})")
            seen_names[v] = lineno
            results.append((lineno, 'name', v))
        elif line.startswith('description '):
            # THE ONE-LINE FORM ONLY in a pattern block, matching
            # tests/harness/run.sh and src/parse/rxt_source.c: the `|`
            # block scalar is indented continuation and a pattern block's
            # lines are not indented (format_design §1.2 vs §1.3 -- the
            # body's rule wins, since 3,265 blocks depend on it).
            v = line[len('description '):]
            if v.strip() == '|':
                raise ValueError(f"{path}:{lineno}: a pattern block's "
                                 "'description' takes the one-line form only: "
                                 "'|' is a head form")
            results.append((lineno, 'description', v))
        elif line.startswith('encoding '):
            # [DD-13b.W1.1 r46sem finding 19] see the 'name' arm above --
            # the same "leg C accepts a strict superset" gap.
            v = line[len('encoding '):].strip()
            if not ident_ok(v):
                raise ValueError(f"{path}:{lineno}: 'encoding' wants an "
                                 f"identifier (got {v!r})")
            results.append((lineno, 'encoding', v))
        elif line.startswith('engine '):
            # [DD-13b.W1.1 r46sem finding 4, RULED] ONLY `vm` FOR W1.1 --
            # see src/parse/rxt_source.c's twin comment. Leg C used to
            # accept 'dfa' too, while leg B (tests/harness/run.sh) already
            # refused it -- the D80 defect this step's remedy targets.
            v = line[len('engine '):].strip()
            if v != 'vm':
                raise ValueError(f"{path}:{lineno}: unknown 'engine' value "
                                 f"{v!r} (only vm is defined)")
            results.append((lineno, 'engine', v))
        elif line.startswith('budget '):
            v = line[len('budget '):].strip()
            if v.startswith('steps='):
                results.append((lineno, 'budget', ('steps', int(v[6:]))))
            elif v.startswith('frames='):
                results.append((lineno, 'budget', ('frames', int(v[7:]))))
            else:
                raise ValueError(f"{path}:{lineno}: unknown 'budget' spec "
                                 f"{v!r} (want steps=<n> or frames=<n>)")
        elif line.startswith('frames-buffer='):
            results.append((lineno, 'frames_buffer', line[len('frames-buffer='):]))
        elif line.startswith('gu '):
            # [DD-14 wave A] a typed GIVE-UP expectation. It is recognised
            # here and SKIPPED as an oracle question, never ignored: python
            # `re` has no notion of a step or frame budget at all, so there
            # is nothing for it to verify and the skip is counted rather
            # than silently dropped (a population nobody counts is not a
            # population). `gu internal` is refused by name, exactly as
            # run.sh refuses it -- nothing may EXPECT an internal error.
            rest = line[len('gu '):].lstrip()
            code = rest.split(' ', 1)[0].split('\t', 1)[0]
            if code == 'internal':
                raise ValueError(f"{path}:{lineno}: 'gu internal' is refused: "
                                 "PCREC_ERR_INTERNAL is the artifact catching "
                                 "its own inconsistency, never a planned "
                                 "outcome a .rxt block may expect")
            if code not in ('steps', 'frames', 'work', 'recurse'):
                raise ValueError(f"{path}:{lineno}: unknown 'gu' code {code!r} "
                                 "(want steps, frames, work or recurse)")
            subj, tail = parse_quoted(rest[len(code):].lstrip())
            if tail.strip() != '':
                raise ValueError(f"{path}:{lineno}: unexpected trailing "
                                 f"content on gu line: {tail.strip()!r}")
            results.append((lineno, 'gu', (code, subj)))
        elif line.startswith('m "'):
            rest = line[2:]  # keep leading quote
            subj, tail = parse_quoted(rest)
            tail = tail.strip()
            parts = tail.split()
            if len(parts) != 2:
                raise ValueError(f"{path}:{lineno}: bad m line tail {tail!r}")
            start, end = int(parts[0]), int(parts[1])
            results.append((lineno, 'm', (subj, start, end)))
        elif line.startswith('n "'):
            rest = line[2:]
            subj, tail = parse_quoted(rest)
            tail = tail.strip()
            if tail != '':
                raise ValueError(f"{path}:{lineno}: unexpected trailing content on n line: {tail!r}")
            results.append((lineno, 'n', subj))
        elif line.startswith('ms '):
            p, rest = parse_startpos_tail(line, 'ms ')
            subj, tail = parse_quoted(rest)
            tail = tail.strip()
            parts = tail.split()
            if len(parts) != 2:
                raise ValueError(f"{path}:{lineno}: bad ms line tail {tail!r}")
            start, end = int(parts[0]), int(parts[1])
            results.append((lineno, 'ms', (p, subj, start, end)))
        elif line.startswith('ns '):
            p, rest = parse_startpos_tail(line, 'ns ')
            subj, tail = parse_quoted(rest)
            tail = tail.strip()
            if tail != '':
                raise ValueError(f"{path}:{lineno}: unexpected trailing content on ns line: {tail!r}")
            results.append((lineno, 'ns', (p, subj)))
        elif line.startswith('gp '):
            try:
                slot, start, end = parse_group_tail(line, 'gp ')
            except ValueError as e:
                raise ValueError(f"{path}:{lineno}: {e}")
            results.append((lineno, 'gp', (slot, start, end)))
        elif line.startswith('g '):
            try:
                slot, start, end = parse_group_tail(line, 'g ')
            except ValueError as e:
                raise ValueError(f"{path}:{lineno}: {e}")
            results.append((lineno, 'g', (slot, start, end)))
        else:
            raise ValueError(f"{path}:{lineno}: unrecognized line: {line!r}")
    return results


# [DD-13b.W1.1] LEG C of the C1 parse differential. Same row schema as
# tests/harness/run.sh's `--dump` (leg B); the projection each pair of
# legs is compared on lives in tests/rxtsource/run_rxtsource_tests.sh.
#
# It is written as its OWN pass over `entries` rather than threaded
# through the oracle loop below, so the dump reports what THIS PARSER
# read and cannot be perturbed by -- or perturb -- what the oracle then
# decides about it.
DUMP_CTRL = {c: '\\x%02x' % c for c in list(range(0x01, 0x20)) + [0x7f]}
DUMP_CTRL[0x09] = '\\t'
DUMP_CTRL[0x0a] = '\\n'
DUMP_CTRL[0x0d] = '\\r'


def rxt_escape(s):
    r"""The .rxt format's own subject-escape vocabulary (\t \n \r \\ \xNN),
    docs/spec/rxt_format.md -- the same one src/parse/rxt_source.c and
    tests/harness/run.sh emit. Backslash first, or the escapes we add
    would themselves be re-escaped."""
    out = []
    for ch in s:
        b = ord(ch)
        if ch == '\\':
            out.append('\\\\')
        elif b in DUMP_CTRL:
            out.append(DUMP_CTRL[b])
        else:
            out.append(ch)
    return ''.join(out)


def dump_file(path, entries):
    """One `block` row per pattern block and one `case` row per
    expectation, in file order. `perr` is a BLOCK field, not a case row,
    because leg B models it that way (a perr block has no m/n lines and
    the pattern text is the whole test) and the two must agree."""
    blk = None
    cases = []

    def flush():
        if blk is None:
            return
        print('block\t%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (
            path, blk['line'], blk['name'], rxt_escape(blk['desc']),
            rxt_escape(blk['pat']), blk['flags'], blk['features'],
            blk['only'], blk['encoding'], blk['engine'],
            blk['steps'], blk['frames'], blk['perr']))
        for c in cases:
            print('case\t%s\t%d\t%s\t%d\t%s' % (path, c[0], c[1], c[2], c[3]))

    for lineno, kind, data in entries:
        if kind == 'pattern':
            flush()
            del cases[:]
            blk = {'line': lineno, 'pat': data[0], 'name': '', 'desc': '',
                   'flags': '', 'features': '', 'only': '', 'encoding': '',
                   'engine': '', 'steps': '', 'frames': '', 'perr': ''}
            continue
        if blk is None:
            continue
        if kind == 'flags':        blk['flags'] = data
        elif kind == 'features':   blk['features'], blk['only'] = data[0], ('1' if data[1] else '')
        elif kind == 'name':       blk['name'] = data
        elif kind == 'description':blk['desc'] = data
        elif kind == 'encoding':   blk['encoding'] = data
        elif kind == 'engine':     blk['engine'] = data
        elif kind == 'budget':
            blk['steps' if data[0] == 'steps' else 'frames'] = str(data[1])
        elif kind == 'perr':       blk['perr'] = '1'
        elif kind in ('m', 'ms', 'n', 'ns', 'gu'):
            # leg B stores `ms`/`ns` under `m`/`n` with an explicit
            # startpos, which is not a loss: the format DEFINES m/n as
            # ms/ns with P fixed at 0 (docs/spec/rxt_format.md), so the
            # two spellings of one case must dump identically.
            if kind == 'm':    cases.append([lineno, 'm', 0, ''])
            elif kind == 'n':  cases.append([lineno, 'n', 0, ''])
            elif kind == 'ms': cases.append([lineno, 'm', data[0], ''])
            elif kind == 'ns': cases.append([lineno, 'n', data[0], ''])
            else:              cases.append([lineno, 'gu', 0, ''])
        elif kind in ('g', 'gp'):
            # attached to the most recent m/ms case, in leg B's own
            # `slot,start,end,pending;` accumulation order. A g line with
            # no such case is a parse failure the oracle reports; here it
            # is simply not attachable, and the row it would have joined
            # is absent -- which the differential sees as a difference.
            for c in reversed(cases):
                if c[1] == 'm':
                    c[3] += '%d,%d,%d,%d;' % (data[0], data[1], data[2],
                                              1 if kind == 'gp' else 0)
                    break
    flush()


def discover(args):
    """A directory argument is searched RECURSIVELY (os.walk), matching
    tests/assertions/verify_pcre2.py's own discovery and NOT this
    script's historical one-level glob.

    The glob was the defect r45chk's N1 named: `verify_rxt.py tests`
    matched `tests/*.rxt`, of which there are none, so it verified ZERO
    files and exited reporting success. A discovery that can silently
    narrow to nothing and still read as a pass is the one property this
    script must not have -- see --min-files below for the other half."""
    files = []
    for a in args:
        if os.path.isdir(a):
            for root, _dirs, names in os.walk(a):
                files += [os.path.join(root, n) for n in names
                          if n.endswith('.rxt')]
        else:
            files.append(a)
    return sorted(files)


# [DD-13b.W1.1] THE PER-FILE WALL BOUND, and the reason it had to exist
# before this oracle could be wired to the corpus at all.
#
# MEASURED: `tests/base/d27_k23_ambiguous_decomposition.rxt` does not
# finish. Its pattern is `(a{1,3}){65}` and its subjects run to 100+
# `a`s; python `re` is a BACKTRACKING engine, so finding a decomposition
# of exactly 65 groups over a run of 70 is exponential. 64 characters
# answers instantly, 70 does not return. That file is a D27 BLINDED
# corpus written to probe ambiguous decomposition — it is doing its job,
# and python is the wrong engine to ask.
#
# So the first corpus-wide run of this oracle hangs, forever, inside
# `make test`. `docs/spec/rxt_format.md` already states the house rule
# this violates — "every compile and every matcher run in the harness is
# bounded (D45)... Exceeding a bound is a loud, named FAILURE, never a
# hang or a silent skip" — and the reason nobody had applied it here is
# that this script had never run.
#
# WHY A SUBPROCESS AND NOT `signal.alarm`: a long `re.search` is a single
# C call that never returns to the interpreter, so SIGALRM cannot
# interrupt it. The handler would not run until the search finished,
# which is the thing that does not happen. A child process can be killed.
#
# The bound is PER FILE rather than per case because that is what a
# process boundary costs least: one python startup per file (~30 ms over
# 179 files) instead of one per case (26,691 of them).
def run_supervised(files, timeout, min_files, allow_timeouts=0):
    """Re-invoke this script once per file under a wall bound, and
    aggregate. A file that overruns is NAMED and COUNTED, never silently
    dropped and never allowed to hang the suite.

    [DD-13b.W1.1 r46sem finding 6 / chk 8] `allow_timeouts` is the
    caller's explicit tolerance for the PINNED count of files known to
    overrun today (docs/spec/rxt_format.md's house rule, quoted below,
    applies to a timeout as much as to any other bound). A bound exceeded
    used to be neither pass, fail, nor skip and left the exit status
    entirely alone -- loud on stdout, silent on the one channel a caller
    actually checks."""
    import subprocess

    SKIP_KEYS = ('pcre2-only', 'giveup', 'composed', 'no-python-expression',
                 'perr-python-accepts', 'own-oracle')
    tot_pass = tot_fail = tot_skip = 0
    tot_reason = {k: 0 for k in SKIP_KEYS}
    timed_out = []
    crashed = []

    for path in files:
        try:
            r = subprocess.run(
                [sys.executable, os.path.abspath(__file__), path],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out.append(path)
            print(f"=== {os.path.basename(path)}: ORACLE BOUND EXCEEDED "
                  f"({timeout}s) — not python-verifiable in bounded time ===")
            continue
        out = r.stdout.decode('utf-8', 'replace')
        got = {}
        for line in out.splitlines():
            if line.startswith('PASS=') and ' FAIL=' in line:
                a, b = line.split(' FAIL=')
                got['pass'] = int(a[len('PASS='):]); got['fail'] = int(b)
            elif line.startswith('SKIP='):
                head = line[len('SKIP='):].split(' ', 1)[0]
                got['skip'] = int(head)
                # keyed by NAME, so a reason added to the child's output
                # is aggregated here without an edit — and one that
                # DISAPPEARS shows up as a zero rather than as a silently
                # dropped column.
                for key in SKIP_KEYS:
                    tag = key + '='
                    if tag in line:
                        got[key] = int(line.split(tag)[1]
                                       .split(')')[0].split()[0])
        if 'pass' not in got:
            crashed.append(path)
            print(f"=== {os.path.basename(path)}: ORACLE DID NOT REPORT "
                  f"(exit {r.returncode}) ===")
            for ln in out.splitlines()[-8:]:
                print(f"  {ln}")
            continue
        tot_pass += got['pass']; tot_fail += got['fail']
        tot_skip += got.get('skip', 0)
        for key in SKIP_KEYS:
            tot_reason[key] += got.get(key, 0)
        # a child's own failure detail is already on its stdout
        if got['fail'] or r.returncode != 0:
            for ln in out.splitlines():
                if ln.startswith('===') or ln.startswith('  line '):
                    print(ln)

    print()
    print("=== Summary ===")
    print(f"PASS={tot_pass} FAIL={tot_fail}")
    print(f"FILES={len(files)}")
    print("SKIP=%d (%s)" % (tot_skip, ' '.join(
        "%s=%d" % (k, tot_reason[k]) for k in SKIP_KEYS)))
    # NAMED EVERY RUN, not merely counted: a bound that is exceeded
    # silently is a file nobody verifies and nobody remembers.
    print(f"TIMEOUT={len(timed_out)} (per-file bound {timeout}s)")
    for pth in timed_out:
        print(f"  not python-verifiable in bounded time: {pth}")
    if crashed:
        print(f"CRASHED={len(crashed)}")
        for pth in crashed:
            print(f"  oracle did not report: {pth}")
    if min_files and len(files) < min_files:
        return 1
    # [DD-13b.W1.1 r46sem finding 6, BLOCKER-ADJACENT MUST-FIX] AN ORACLE
    # BOUND EXCEEDED IS A LOUD FAILURE, per docs/spec/rxt_format.md:
    # "Exceeding a bound is a loud, named FAILURE, never a hang or a
    # silent skip." `timed_out` used to be excluded from this return's
    # condition entirely -- printed, named, and then absent from the exit
    # status, so a SECOND file timing out anywhere other than this
    # script's own pinned caller (which separately asserts `C3_TIMEOUT`)
    # read as a clean exit 0. `allow_timeouts` is the caller's explicit,
    # counted tolerance -- never a blanket exemption -- so exceeding IT
    # is still loud.
    if len(timed_out) > allow_timeouts:
        return 1
    return 1 if (tot_fail or crashed) else 0


def main():
    args = sys.argv[1:]
    dump = False
    min_files = 0
    file_timeout = 0
    allow_timeouts = 0
    rest = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--dump':
            dump = True
        elif a == '--min-files':
            i += 1
            if i >= len(args):
                print("verify_rxt.py: --min-files needs a number",
                      file=sys.stderr)
                sys.exit(2)
            min_files = int(args[i])
        elif a == '--file-timeout':
            i += 1
            if i >= len(args):
                print("verify_rxt.py: --file-timeout needs seconds",
                      file=sys.stderr)
                sys.exit(2)
            file_timeout = float(args[i])
        elif a == '--allow-timeouts':
            # [DD-13b.W1.1 r46sem finding 6] the caller's EXPLICIT, COUNTED
            # tolerance for files known to overrun --file-timeout today.
            # Default 0: a timeout is a failure unless the caller says
            # otherwise, naming how many. See run_supervised's own comment.
            i += 1
            if i >= len(args):
                print("verify_rxt.py: --allow-timeouts needs a number",
                      file=sys.stderr)
                sys.exit(2)
            allow_timeouts = int(args[i])
        else:
            rest.append(a)
        i += 1

    if rest:
        files = discover(rest)
    else:
        files = discover([BASE_DIR])
    if not files:
        print("No .rxt files found")
        sys.exit(1)

    # THE SHORT-LIST HARD FAIL ([M5-SEAM]'s shape, r45chk N1's condition).
    # The floor is a PINNED literal supplied by the caller, never derived
    # from the discovery it is checking -- a control that shares a source
    # with what it controls is this project's signature check-design
    # failure (docs/dev/learnings.md §3). So a discovery that narrows --
    # a glob that stops matching, a directory renamed, a find that lost a
    # path -- goes RED here instead of verifying fewer files and printing
    # ALL CHECKS PASSED.
    if min_files and len(files) < min_files:
        print(f"verify_rxt.py: DISCOVERY TOO SHORT -- found {len(files)} "
              f".rxt file(s), expected at least {min_files}. This is a "
              f"discovery failure, not a clean run: a narrowed corpus must "
              f"never read as a pass. If the corpus legitimately shrank, "
              f"the caller's pinned census is what to change.", file=sys.stderr)
        sys.exit(1)

    if dump:
        for path in files:
            dump_file(path, parse_rxt(path))
        return

    # THE BOUND IS ONLY ARMED FOR A MULTI-FILE RUN. A developer iterating
    # on one file gets the in-process path unchanged — same output, no
    # subprocess, and no bound to be surprised by. The corpus wiring in
    # tests/rxtsource/ is what passes --file-timeout, because that is the
    # invocation that must never be able to hang `make test`.
    if file_timeout > 0 and len(files) > 1:
        sys.exit(run_supervised(files, file_timeout, min_files, allow_timeouts))

    total_pass = 0
    total_fail = 0
    # [DD-13b.W1.1 / r45chk F13(d)] THE SKIP TOTAL. Until now this script
    # printed a per-file skip line only `if skipped:` and no aggregate at
    # all, so "the same number of cases were skipped" -- which is the
    # load-bearing half of the oracle re-run check, since a loose skip
    # predicate skips blocks it should have verified -- had nothing to
    # read. The total is broken out BY REASON because the reasons have
    # different populations and different owners, and one number moving
    # while another moves the other way would otherwise cancel.
    total_skip = 0
    total_skip_pcre2_only = 0
    total_skip_giveup = 0
    total_skip_composed = 0
    total_skip_no_python = 0
    total_skip_perr_accept = 0
    total_skip_own_oracle = 0
    per_file_counts = {}

    for path in files:
        fname = os.path.basename(path)
        entries = parse_rxt(path)
        # a whole-FILE fact, so it is taken over the whole entry list
        # rather than accumulated as blocks go by: a `name` may be
        # declared on a block AFTER the one that references it.
        file_has_name = any(k == 'name' for _, k, _ in entries)
        cur_pattern = None
        cur_pattern_lineno = None
        compiled = None
        compile_error = None
        m_count = n_count = ms_count = ns_count = perr_count = 0
        g_count = gp_count = 0
        # [M4.5a] the most recent m/ms case in the CURRENT block, so a
        # following g/gp line knows what subject/startpos to re-search —
        # last_case_kind is 'm' (an m/ms case is live), 'n' (an n/ns case
        # came instead — g/gp after it is a hard error, no captures on a
        # no-match assertion), or None (no case yet in this block).
        last_case_kind = None
        last_case_subj = None
        last_case_pos = None
        skipped = 0
        skipped_pcre2_only = 0
        skipped_giveup = 0
        skipped_composed = 0
        skipped_no_python = 0
        skipped_perr_accept = 0
        skipped_own_oracle = 0
        file_own_oracle = declares_own_oracle(path)
        cur_skip = False
        cur_composed_skip = False
        # [DD-13b.W1.1 r46sem finding 5 / chk 1, FIXED] `file_has_name` was
        # computed ONCE, correctly, as a whole-file scan a few lines above
        # (`any(k == 'name' for _, k, _ in entries)`) -- and then
        # immediately RE-INITIALIZED to False here, shadowing it for the
        # entire per-line loop below and defeating the exact invariant the
        # comment up there asserts (a `name` declared on a block AFTER the
        # one that references it). `cur_name` was written at the 'name'
        # branch below and never read anywhere -- dead, removed with it.
        cur_reflags = 0
        file_failures = []

        for lineno, kind, data in entries:
            if kind == 'pattern':
                cur_pattern, cur_skip = data
                cur_pattern_lineno = lineno
                compile_error = None
                compiled = None
                cur_reflags = 0
                last_case_kind = None
                last_case_subj = None
                last_case_pos = None
                cur_composed_skip = (file_has_name and
                                     has_by_name_reference(cur_pattern))
                if not cur_skip and not cur_composed_skip:
                    try:
                        compiled = re.compile(cur_pattern)
                    except re.error as e:
                        compile_error = e
                continue

            if kind in ('name', 'description', 'encoding', 'engine',
                        'budget', 'frames_buffer'):
                # [DD-13b.W1] W1's new block-scoped directives, plus the
                # two [DD-14] ones this oracle never learned. None has a
                # meaning for python `re`: `name`/`description` are
                # metadata, `encoding` is D58's per-artifact axis,
                # `engine`/`budget`/`frames-buffer=` size and select
                # pcrec's own machinery. They are PARSED (a control that
                # refuses to read a line is no control for it) and then
                # deliberately ignored. `file_has_name` is NOT set here
                # (r46sem finding 5): it is a whole-FILE fact, computed
                # once above from the full entry list, precisely so a
                # `name` declared on a LATER block still counts for a
                # composed-block skip on an EARLIER one that references
                # it by name -- setting it per-line here would only ever
                # be correct AFTER the declaring line has been reached.
                continue

            if kind == 'features':
                # per-block enabled-module list (MOD-0.3c). The python oracle
                # is deliberately unaffected: python re has no module gate,
                # and every construct the gate can open either means the same
                # thing in python (\d \s \w and friends — verified as
                # usual) or cannot be expressed there at all, in which case
                # the block carries # pcre2-only exactly like any other
                # python-inexpressible pattern. An EMPTY list is a corpus
                # typo, refused like an unknown flag letter.
                if not data[0]:
                    file_failures.append((lineno, "empty features list"))
                continue

            if kind == 'flags':
                # per-block compile options; re-compile the current block's
                # pattern under them. re.ASCII is not optional here: without it
                # python's IGNORECASE folds Unicode (K/Kelvin sign, long s),
                # which would make this oracle disagree with pcrec's
                # deliberately ASCII-only fold and silently mis-verify the
                # base tier. Unicode folding is DD-1/M5.
                #
                # [DD-13b.W1.1 r46sem finding 3] parse_rxt (above) now
                # REFUSES anything but 'i' at parse time, so `data` is
                # guaranteed 'i' by the time it reaches here -- the
                # duplicate check this arm used to carry is unreachable
                # and removed rather than left as a second copy of a rule
                # with one home.
                cur_reflags = re.IGNORECASE | re.ASCII
                if not cur_skip:
                    compile_error = None
                    compiled = None
                    try:
                        compiled = re.compile(cur_pattern, cur_reflags)
                    except re.error as e:
                        compile_error = e
                continue

            if cur_pattern is None:
                file_failures.append((lineno, f"{kind} line with no preceding pattern block"))
                continue

            if file_own_oracle:
                # THE DIRECTORY DECLARES ITS OWN ORACLE (see
                # declares_own_oracle above and docs/spec/rxt_format.md).
                # Its cells are verified by that oracle, on every make
                # test; re-checking them here against an engine the spec
                # names as the WRONG one for them would manufacture
                # disagreements the spec predicts. Counted, so "which
                # files does the python oracle actually cover" has an
                # answer rather than an assumption.
                skipped += 1
                skipped_own_oracle += 1
                continue

            if cur_skip:
                skipped += 1
                skipped_pcre2_only += 1
                continue

            if cur_composed_skip:
                skipped += 1
                skipped_composed += 1
                continue

            if kind == 'gu':
                # a typed GIVE-UP is a fact about pcrec's own budgets, which
                # this oracle has no notion of. Counted, never ignored.
                skipped += 1
                skipped_giveup += 1
                continue

            if kind == 'perr':
                perr_count += 1
                if compile_error is None:
                    # pcrec refuses this pattern and python accepts it.
                    # That is two engines with different grammars, not
                    # evidence about whether pcrec's refusal is right —
                    # python accepting `(?<a>x)`-shaped input says nothing
                    # about PCRE2 semantics. Counted, never scored.
                    skipped += 1
                    skipped_perr_accept += 1
                    continue
                else:
                    total_pass += 1
                    continue
            elif kind == 'm':
                m_count += 1
                subj, start, end = data
                last_case_kind = 'm'
                last_case_subj = subj
                last_case_pos = 0
                if compiled is None:
                    # NO OPINION IS NOT DISAGREEMENT. python `re` has no
                    # (?(DEFINE), no (?1) subroutine call, no PCRE2 (?<n>
                    # spelling, no \g<>, no (?J), no possessive quantifier.
                    # A pattern it cannot compile yields no python verdict
                    # at all, so there is nothing to agree or disagree
                    # with, and scoring it as a FAILURE conflates "python
                    # says otherwise" with "python cannot be asked".
                    # MEASURED on the first corpus-wide run: 1,814 of
                    # 1,847 reported failures were this, drowning the 5
                    # that were real. COUNTED and PINNED, so a population
                    # that grows is visible.
                    skipped += 1
                    skipped_no_python += 1
                    continue
                else:
                    mo = compiled.search(subj)
                    if mo is None:
                        file_failures.append((lineno, f"pattern {cur_pattern!r} subject {subj!r}: expected match [{start},{end}) but got no match"))
                    elif mo.span() != (start, end):
                        file_failures.append((lineno, f"pattern {cur_pattern!r} subject {subj!r}: expected span ({start},{end}) but got {mo.span()}"))
                    else:
                        total_pass += 1
                        continue
            elif kind == 'n':
                n_count += 1
                subj = data
                last_case_kind = 'n'
                last_case_subj = None
                last_case_pos = None
                if compiled is None:
                    # NO OPINION IS NOT DISAGREEMENT. python `re` has no
                    # (?(DEFINE), no (?1) subroutine call, no PCRE2 (?<n>
                    # spelling, no \g<>, no (?J), no possessive quantifier.
                    # A pattern it cannot compile yields no python verdict
                    # at all, so there is nothing to agree or disagree
                    # with, and scoring it as a FAILURE conflates "python
                    # says otherwise" with "python cannot be asked".
                    # MEASURED on the first corpus-wide run: 1,814 of
                    # 1,847 reported failures were this, drowning the 5
                    # that were real. COUNTED and PINNED, so a population
                    # that grows is visible.
                    skipped += 1
                    skipped_no_python += 1
                    continue
                else:
                    mo = compiled.search(subj)
                    if mo is not None:
                        file_failures.append((lineno, f"pattern {cur_pattern!r} subject {subj!r}: expected no match but got {mo.span()}"))
                    else:
                        total_pass += 1
                        continue
            elif kind == 'ms':
                ms_count += 1
                p, subj, start, end = data
                last_case_kind = 'm'
                last_case_subj = subj
                last_case_pos = p
                if compiled is None:
                    # NO OPINION IS NOT DISAGREEMENT. python `re` has no
                    # (?(DEFINE), no (?1) subroutine call, no PCRE2 (?<n>
                    # spelling, no \g<>, no (?J), no possessive quantifier.
                    # A pattern it cannot compile yields no python verdict
                    # at all, so there is nothing to agree or disagree
                    # with, and scoring it as a FAILURE conflates "python
                    # says otherwise" with "python cannot be asked".
                    # MEASURED on the first corpus-wide run: 1,814 of
                    # 1,847 reported failures were this, drowning the 5
                    # that were real. COUNTED and PINNED, so a population
                    # that grows is visible.
                    skipped += 1
                    skipped_no_python += 1
                    continue
                else:
                    mo = compiled.search(subj, p)
                    if mo is None:
                        file_failures.append((lineno, f"pattern {cur_pattern!r} subject {subj!r} startpos {p}: expected match [{start},{end}) but got no match"))
                    elif mo.span() != (start, end):
                        file_failures.append((lineno, f"pattern {cur_pattern!r} subject {subj!r} startpos {p}: expected span ({start},{end}) but got {mo.span()}"))
                    else:
                        total_pass += 1
                        continue
            elif kind == 'ns':
                ns_count += 1
                p, subj = data
                last_case_kind = 'n'
                last_case_subj = None
                last_case_pos = None
                if compiled is None:
                    # NO OPINION IS NOT DISAGREEMENT. python `re` has no
                    # (?(DEFINE), no (?1) subroutine call, no PCRE2 (?<n>
                    # spelling, no \g<>, no (?J), no possessive quantifier.
                    # A pattern it cannot compile yields no python verdict
                    # at all, so there is nothing to agree or disagree
                    # with, and scoring it as a FAILURE conflates "python
                    # says otherwise" with "python cannot be asked".
                    # MEASURED on the first corpus-wide run: 1,814 of
                    # 1,847 reported failures were this, drowning the 5
                    # that were real. COUNTED and PINNED, so a population
                    # that grows is visible.
                    skipped += 1
                    skipped_no_python += 1
                    continue
                else:
                    mo = compiled.search(subj, p)
                    if mo is not None:
                        file_failures.append((lineno, f"pattern {cur_pattern!r} subject {subj!r} startpos {p}: expected no match but got {mo.span()}"))
                    else:
                        total_pass += 1
                        continue
            elif kind in ('g', 'gp'):
                # [M4.5a] capture-group expectation, oracle-verified against
                # python re's match.span(slot) regardless of the 'g'/'gp'
                # (live/pending-VM) distinction — pending-ness is a property
                # of what pcrec's CURRENT artifact can deliver (RX_NCAPS),
                # never of whether the expectation itself is correct, so this
                # oracle checks BOTH kinds identically.
                if kind == 'gp':
                    gp_count += 1
                else:
                    g_count += 1
                slot, start, end = data
                if last_case_kind != 'm':
                    file_failures.append((lineno, f"'{kind}' line with no preceding m/ms case in this block"))
                elif compiled is None:
                    skipped += 1
                    skipped_no_python += 1
                    continue
                else:
                    mo = compiled.search(last_case_subj, last_case_pos)
                    if mo is None:
                        file_failures.append((lineno, f"pattern {cur_pattern!r} subject {last_case_subj!r} startpos {last_case_pos}: preceding case implies a match but oracle found none, cannot check group slot {slot}"))
                    elif slot > compiled.groups:
                        file_failures.append((lineno, f"pattern {cur_pattern!r}: group slot {slot} exceeds pattern's group count ({compiled.groups})"))
                    else:
                        got = mo.span(slot)
                        if got != (start, end):
                            file_failures.append((lineno, f"pattern {cur_pattern!r} subject {last_case_subj!r} startpos {last_case_pos}: group slot {slot} expected ({start},{end}) but got {got}"))
                        else:
                            total_pass += 1
                            continue
            total_fail += 1

        per_file_counts[fname] = (m_count, n_count, ms_count, ns_count, perr_count, g_count, gp_count, len(file_failures))
        total_skip += skipped
        total_skip_pcre2_only += skipped_pcre2_only
        total_skip_giveup += skipped_giveup
        total_skip_composed += skipped_composed
        total_skip_no_python += skipped_no_python
        total_skip_perr_accept += skipped_perr_accept
        total_skip_own_oracle += skipped_own_oracle
        if skipped:
            print(f"  {fname}: {skipped} case(s) skipped, not python-verifiable "
                  f"(pcre2-only {skipped_pcre2_only}, give-up {skipped_giveup}, "
                  f"composed {skipped_composed}, no-python-expression "
                  f"{skipped_no_python}, perr-python-accepts "
                  f"{skipped_perr_accept}, own-oracle {skipped_own_oracle})")
        if file_failures:
            print(f"=== {fname}: {len(file_failures)} FAILURES ===")
            for lineno, msg in file_failures:
                print(f"  line {lineno}: {msg}")

    print()
    print("=== Summary ===")
    grand_m = grand_n = grand_ms = grand_ns = grand_p = grand_g = grand_gp = grand_f = 0
    for fname in sorted(per_file_counts):
        m_count, n_count, ms_count, ns_count, perr_count, g_count, gp_count, fails = per_file_counts[fname]
        grand_m += m_count; grand_n += n_count
        grand_ms += ms_count; grand_ns += ns_count
        grand_p += perr_count; grand_f += fails
        grand_g += g_count; grand_gp += gp_count
        total = m_count + n_count + ms_count + ns_count + perr_count + g_count + gp_count
        status = "OK" if fails == 0 else f"{fails} FAIL"
        print(f"  {fname:28s} m={m_count:3d} n={n_count:3d} ms={ms_count:3d} ns={ns_count:3d} perr={perr_count:3d} g={g_count:3d} gp={gp_count:3d} total={total:3d}  [{status}]")
    print()
    grand_total = grand_m + grand_n + grand_ms + grand_ns + grand_p + grand_g + grand_gp
    print(f"TOTAL: m={grand_m} n={grand_n} ms={grand_ms} ns={grand_ns} perr={grand_p} g={grand_g} gp={grand_gp} cases={grand_total}")
    print(f"PASS={total_pass} FAIL={total_fail}")
    # the two numbers C3 pins. FILES is here for the same reason the skip
    # total is: a check that compares "the same verified count" against a
    # run that silently discovered fewer files is comparing two different
    # populations and cannot tell.
    print(f"FILES={len(files)}")
    # EVERY EXCLUSION IS COUNTED AND NAMED BY ITS REASON. The reasons
    # have different owners and different populations, and one moving
    # while another moves the other way would otherwise cancel in a
    # single total — which is the whole failure mode a skip count exists
    # to catch.
    print(f"SKIP={total_skip} "
          f"(pcre2-only={total_skip_pcre2_only} "
          f"giveup={total_skip_giveup} "
          f"composed={total_skip_composed} "
          f"no-python-expression={total_skip_no_python} "
          f"perr-python-accepts={total_skip_perr_accept} "
          f"own-oracle={total_skip_own_oracle})")
    if grand_f == 0:
        print("ALL CHECKS PASSED (100%)")
    else:
        print(f"{grand_f} FAILURES REMAIN")
        sys.exit(1)


if __name__ == '__main__':
    main()
