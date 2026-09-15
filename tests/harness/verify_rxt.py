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
tests/harness/run.sh can check it yet. See docs/testing.md.

[C3 THREE-WAY VERDICT, 2026-09-10/11, lane pyrole] `docs/design/
c3_three_way.md` is the design note; read it before touching any of the
logic below. Python is narrowed to a TRANSCRIPTION-ERROR TRIPWIRE: its only
remaining actionable value is INDEPENDENCE from the .rxt expectations (most
of which were themselves written FROM libpcre2 answers), not correctness
against PCRE2 (D26 is the compatibility target, not python `re`). So a
python-vs-expectation disagreement is no longer scored a FAILURE by itself
— it consults the COMMITTED oracle store (`tests/oracle/oracle_store.py`,
`oracle_store/`, never a live library at check time) for a PCRE2 answer to
the same question. Three outcomes, `_verdict_match_at`/`_verdict_captures`
below: the store CONFIRMS the expectation (python was simply wrong, or
python-version-sensitive, or genuinely inexpressive of PCRE2's semantics —
counted in a separate, always-printed INFO bucket, never a failure, no gate
on its count — modelled on `tests/thread/run_stackdepth_tests.sh`'s `record()`
bucket); the store COVERS the question and DISAGREES TOO (neither oracle
matches the expectation — a real transcription-tripwire FAILURE); or the
store does not cover the question at all (a STORE-UNCOVERED clean miss —
falls back to today's python-only verdict, i.e. FAILURE, counted in its own
bucket so the population is visible rather than silently absorbed into an
ordinary failure)."""
import hashlib
import re
import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.normpath(os.path.join(_HERE, "..", "base"))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "tests", "oracle"))
import oracle_store as _ora  # noqa: E402

# The C3 store instance this check consults (`tests/rxtsource/
# build_c3_store.py`, `docs/design/c3_three_way.md`). A LOCAL Homebrew
# capture, committed as a deliberate, briefed exception to `oracle_store/
# CLAUDE.md`'s usual "only the reference version is committed" rule — see
# that script's own header for why the exception is safe (OracleId.version
# makes a box with a DIFFERENT local libpcre2 a clean miss, never a false
# confirmation).
C3_STORE_ROOT = os.path.join(_ROOT, "oracle_store")
C3_STORE_ORACLE_NAME = "libpcre2"
C3_STORE_ORACLE_VERSION = "10.48"

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


# ---------------------------------------------------------------------------
# [C3 THREE-WAY VERDICT] the committed oracle store, consulted ONLY when
# python's own verdict already disagrees with the corpus expectation — see
# the module docstring and docs/design/c3_three_way.md. Never a live
# library call (the store's whole point); a StoreCorruption from
# oracle_store.lookup() is NOT caught here and propagates as a hard script
# failure, per that module's own rule ("never silently absorbed").
# ---------------------------------------------------------------------------

def _c3_oracle_id(caseless):
    return _ora.OracleId(C3_STORE_ORACLE_NAME, C3_STORE_ORACLE_VERSION,
                          caseless=caseless)


def _store_match_at(pattern, subject, startpos, caseless):
    """Look up a `match-at` question. Returns `('match', (start, end))`,
    `('nomatch', None)`, or `None` (a clean miss: no committed answer for
    this exact question, i.e. STORE-UNCOVERED — includes a stored `giveup`
    answer, which this check has no use for and cannot confirm anything
    with)."""
    ans = _ora.lookup(C3_STORE_ROOT, _c3_oracle_id(caseless), 'match-at',
                       pattern=pattern, subject=subject, startpos=startpos)
    if ans is None:
        return None
    verdict, start_s, end_s, _giveup_code = ans
    if verdict == 'match':
        return ('match', (int(start_s), int(end_s)))
    if verdict == 'nomatch':
        return ('nomatch', None)
    return None


def _store_captures(pattern, subject, startpos, nslots, caseless):
    """Look up a `captures` question. Returns a list of `nslots` `(s, e)`
    tuples (slot 0 is the whole match, matching `.rxt`'s own `g`/`gp` slot
    numbering), or `None` (STORE-UNCOVERED)."""
    ans = _ora.lookup(C3_STORE_ROOT, _c3_oracle_id(caseless), 'captures',
                       pattern=pattern, subject=subject, startpos=startpos,
                       nslots=nslots)
    if ans is None:
        return None
    (pairs_str,) = ans
    nums = [int(x) for x in pairs_str.split()] if pairs_str else []
    return [(nums[2 * i], nums[2 * i + 1]) for i in range(len(nums) // 2)]


def _verdict_match_at(pattern, subject, startpos, caseless, expect_match,
                       expect_span):
    """The three-way verdict for an `m`/`n`/`ms`/`ns` cell whose python
    answer already disagrees with `expect_match`/`expect_span`. Returns one
    of `'confirmed'` (INFO, not a failure), `'disagrees'` (a real FAILURE —
    neither oracle matches the expectation) or `'uncovered'` (STORE-
    UNCOVERED — falls back to a FAILURE, today's python-only verdict), plus
    a short human-readable description of the store's own answer for the
    message."""
    looked_up = _store_match_at(pattern, subject, startpos, caseless)
    if looked_up is None:
        return 'uncovered', None
    verdict, span = looked_up
    if expect_match:
        ok = (verdict == 'match' and span == expect_span)
        desc = ("match %r" % (span,)) if verdict == 'match' else 'nomatch'
    else:
        ok = (verdict == 'nomatch')
        desc = ("match %r" % (span,)) if verdict == 'match' else 'nomatch'
    return ('confirmed' if ok else 'disagrees'), desc


def _verdict_captures(pattern, subject, startpos, slot, caseless,
                       expect_span):
    """The three-way verdict for a `g`/`gp` cell. `nslots` is derived from
    `slot` (`slot + 1` pairs — slot 0 is always the whole match, matching
    the store's own `((a)|ab){0,12}?c` capture questions), not carried by
    the caller, so every `.rxt` slot number maps onto exactly one store
    question shape."""
    pairs = _store_captures(pattern, subject, startpos, slot + 1, caseless)
    if pairs is None:
        return 'uncovered', None
    got = pairs[slot]
    return ('confirmed' if got == expect_span else 'disagrees'), got


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


def _findall_protocol(compiled, subj, encoding):
    r"""`docs/spec/match_api.md` §3.1's find-all loop, in python, counting
    matches. TRANSCRIBED from the spec's own C, like `tests/harness/
    driver.c`'s copy and `tests/encseam/findall_driver.c`'s — if the three
    ever differ, one of them has stopped meaning what the spec says.

    THE ADVANCE OFF AN EMPTY MATCH IS OFF THE MATCH'S OWN START, not off the
    loop variable: an empty match can be found at a position LATER than the
    one searched from, and advancing off `pos` is exactly where the bench's
    `pos = max(end, pos+1)` formula double-counts it (`(?=a)` on `"xax"` is
    1, not 2).

    THE ONE-CHARACTER STEP IS `<prefix>_next_pos` BY REFERENCE and this leg
    cannot call it, so it carries SW7's normative spelling instead: from
    `pos + 1`, skip bytes in the range 0x80-0xBF. That is a second
    implementation and it is paid for by a differential — the same cell is
    counted by driver.c's C loop and by leg A's own parse — which is the
    distinction §2.21 draws against the `printf %b` decoder it refuses one
    production over: a second implementation WITH a differential is a cost,
    one without is a defect."""
    n = len(subj)
    pos = 0
    count = 0
    while pos <= n:
        mo = compiled.search(subj, pos)
        if mo is None:
            break
        count += 1
        st, en = mo.span()
        if en > st:
            pos = en
        else:
            pos = st + 1
            if encoding == 'utf8':
                while pos < n and 0x80 <= ord(subj[pos]) <= 0xBF:
                    pos += 1
    return count


def _fail(path, lineno, cls, msg):
    """[DD-13b.W23.2] THE DIAGNOSTIC CLASS TAG, this leg's own copy of
    src/parse/rxt_source.c's `rxt_fail` format -- `[class] file:line: msg`,
    the tag LEADING. The three-leg differential (tests/rxtsource/) reads
    the bracketed word off each leg's own stderr and compares it, never
    the sentence beside it (D26 governs wording, not the tag). The four
    classes are format_design.md §2.25.5's: structure-attachment /
    unknown-token-in-scope / schema-constraint / value-shape."""
    raise ValueError(f"[{cls}] {path}:{lineno}: {msg}")


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
    with open(path, 'rb') as f:
        raw_bytes = f.read()
    # [DD-13b.W23.2, §1.8 FOLD-IN 1] A NUL BYTE ANYWHERE IN THE FILE IS
    # DETECTED HERE, ONCE, BEFORE ANY LINE IS READ -- matching leg A's
    # whole-file scan ahead of the line split, and NOT the `.decode`-time
    # crash this leg's `surrogateescape` reading would otherwise turn it
    # into. §1.8 item 3's rule: the NUL rule has ONE SCOPE in all three
    # legs, the whole file, before any line is interpreted -- a
    # decoder-scoped test (only inside a quoted subject) would miss a NUL
    # inside a `#` comment line, which is `nul_in_comment.rxtin`'s point.
    if b'\x00' in raw_bytes:
        _fail(path, 0, 'value-shape', 'embedded NUL byte in .rxt source file')
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
    # [DD-13b.W23.2 FIX] `.splitlines()` treats VT/FF and several other
    # Unicode line-break characters as separators, not only `\n` -- the
    # exact control bytes `ctrl_bytes.rxtin` (sem1, the r46 panel's own
    # BLOCKER) carries literally inside a `pattern` line. `readlines()`
    # (what this used to be) splits on `\n` alone; `.split('\n')` matches
    # that, at the cost of one harmless trailing '' entry when the file
    # ends in a newline, which the blank-line skip below already treats
    # as inert.
    lines = raw_bytes.decode('utf-8', errors='surrogateescape').split('\n')
    results = []
    pcre2_only_next = False
    seen_pattern = False
    seen_names = {}
    # [DD-13b.W23.3] the SUBJECT-ID namespace is PER FILE (format_design
    # §2.18: "the physical file that writes the line"), so a fragment's
    # ids are the fragment's.
    subject_ids = {}
    # [DD-13b.W23.2] THE ATTACHMENT ARM's own state (S1, format_design
    # §1.2.1): the immediately preceding NON-INDENTED content line's own
    # first token and line number -- the PARENT an indented line under it
    # would attach to.
    last_kind = None
    last_kind_line = 0
    cur_desc_line = 0
    # [DD-13b.W23.3] THE ATTACHMENT STACK (leg A's `RxtFrame` stack, S1) and
    # S3's OPAQUE REGION, in the same two shapes tests/harness/run.sh
    # carries them and for the same reasons. `att` is one entry per open
    # level, `(indent, is_open_subtree)`; level 0 is the file at indent 0.
    # The stack is what makes a DEDENT checkable: a line popping back must
    # land EXACTLY on an open level, which is what turns a mis-indented line
    # inside an `ext` body into a local error naming its own line.
    #
    # THE PROSE REGION IS DELIBERATELY NOT THE STACK'S BUSINESS: a region's
    # lines may be RAGGED (all three legs accept that — `prose_ragged`), so
    # the stack's exact-indent rule would refuse a shape leg A accepts. Its
    # extent is leg A's `read_prose_region`: to the first CONTENT line whose
    # indent is <= the opener's, a BLANK, or a COMMENT; a whitespace-only
    # line ends nothing and is bytes.
    att = [(0, False)]
    last_indent = 0
    last_was_content = False
    last_opens_scope = False
    last_opens_tree = False
    # THE DEDENT IS A BYTE COUNT TAKEN FROM THE FIRST REGION LINE, K57
    # reproduced deliberately in all three legs (see run.sh's `prose_take`).
    prose = None      # None, or {'ind', 'lines', 'dedent', 'owner', 'line'}
    PROSE_KINDS = ('description', 'license-note', 'adaptation',
                   'attribution', 'note')

    def prose_finish():
        """Close the open region. A `|` with NO continuation under it is a
        structure error in leg A (`read_prose_region`'s own refusal) and is
        one here: the value of a `|` IS the indented lines below it."""
        nonlocal prose, cur_desc_line
        pr, prose = prose, None
        if not pr['lines']:
            _fail(path, pr['line'], 'structure-attachment',
                  "block scalar '|' has no indented continuation lines "
                  "(a '|' value is the indented lines below it)")
        if pr['owner'] == 'description':
            results.append((pr['line'], 'description', '\n'.join(pr['lines'])))

    for lineno, raw_line in enumerate(lines, 1):
        line = raw_line.rstrip('\n')
        # [DD-13b.W23.3] S3 FIRST, because "opaque" means exactly that: S0
        # does not classify a region's lines, S1 does not attach them and no
        # arm tokenises them. The line that ENDS the region is not consumed
        # — it falls through and is read as whatever it is.
        if prose is not None:
            if line == '' or line.startswith('#'):
                prose_finish()
            elif line.strip() == '' or (len(line) - len(line.lstrip(' '))) > prose['ind']:
                if prose['dedent'] < 0:
                    prose['dedent'] = len(line) - len(line.lstrip(' \t'))
                prose['lines'].append(line[prose['dedent']:])
                continue
            else:
                prose_finish()
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
        # [DD-13b.W23.3] S0, split three ways as leg A splits it: a BLANK
        # line and a COMMENT each CLOSE every open attachment and return to
        # indent 0; a WHITESPACE-ONLY line is INERT and disturbs nothing.
        # Before this step all three were one `continue`, which was correct
        # while nothing could be open.
        if line == '' or line.startswith('#'):
            del att[1:]
            last_was_content = False
            last_indent = 0
            last_kind = None
            last_opens_scope = last_opens_tree = False
            continue
        if line.strip() == '':
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
        #
        # [DD-13b.W23.2] THE ATTACHMENT ARM RUNS FIRST -- S1, ahead of
        # first-token dispatch (format_design §1.2.1), and it is why the
        # indentation test moved above the not-seen_pattern block rather
        # than staying where it was, below every other check. Under the
        # OLD order an indented line before the first `pattern` reached
        # the not-seen_pattern branch first and raised its "before any
        # pattern block" message -- the right VERDICT, the wrong CLASS
        # (`indent_pre_body.rxtin` needs structure-attachment, not
        # unknown-token-in-scope). Nothing this build's BLOCK scope
        # declares admits a child, so an indented line is ALWAYS a
        # structural error: before the first `pattern` there is no
        # PARENT at all; once a block is open the parent is the
        # immediately preceding CONTENT line, which takes no
        # continuation. A leading TAB never opens an indent at all (S0),
        # checked first, before either question is asked.
        cur_ind = len(line) - len(line.lstrip(' '))
        if line[cur_ind:cur_ind + 1] == '\t':
            _fail(path, lineno, 'structure-attachment',
                  "indentation is spaces; this line is indented with a "
                  "TAB (a tab inside a value is still data, but a tab "
                  "in the indentation has no agreed depth)")
        # [DD-13b.W23.3] S1 — ATTACHMENT, over the stack. A deeper line is a
        # CHILD of the line above and is admitted only when that line's kind
        # says so; a shallower one POPS back and must land EXACTLY on an
        # open level.
        if last_was_content and cur_ind > last_indent:
            if att[-1][1] or last_opens_tree:
                att.append((cur_ind, True))
            elif last_opens_scope:
                att.append((cur_ind, False))
            elif not seen_pattern and len(att) == 1:
                _fail(path, lineno, 'structure-attachment',
                      "an indented line appears before any pattern block "
                      "(nothing is open to attach it to)")
            elif last_kind:
                # [DD-13b.W23.2 FINDING] leg A's OWN `rxt_source.c:1169`
                # files this under RXTD_STRUCTURE, not
                # RXTD_SCHEMA_CONSTRAINT -- the fixture table in
                # `w23_impl.md` §3.2 says `indent_under_m.rxtin` should be
                # schema-constraint, and the DELIVERED W23.1 code disagrees
                # with its own design note. Legs B and C match leg A (the
                # schema table is leg A's, deliberately -- §2.25.5); the
                # discrepancy is reported rather than improvised past.
                _fail(path, lineno, 'structure-attachment',
                      f"indented line continues nothing ('{last_kind}' "
                      f"takes no continuation, declared on line {last_kind_line})")
            else:
                _fail(path, lineno, 'structure-attachment',
                      "indented line continues nothing (the declaration "
                      "above it takes no continuation)")
        else:
            while len(att) > 1 and cur_ind < att[-1][0]:
                att.pop()
            if cur_ind != att[-1][0]:
                if not seen_pattern and len(att) == 1:
                    _fail(path, lineno, 'structure-attachment',
                          "this line is indented and nothing above it "
                          "is open to attach it to (a blank line, a comment "
                          "or the start of the file closes every attachment)")
                # [DD-13b.W23.3] A RAGGED DEDENT IS ITS OWN SENTENCE, in
                # all three legs: a line closing back to a depth NOBODY
                # OPENED is a different mistake from "the line above takes
                # no continuation", and inside an OPEN SUBTREE the shared
                # sentence named a rule the subtree does not have.
                _fail(path, lineno, 'structure-attachment',
                      f"this line is indented {cur_ind}, which closes back "
                      f"to a depth nothing opened (the enclosing level is "
                      f"indented {att[-1][0]}); indentation must return to "
                      f"a depth already open")
        last_indent = cur_ind
        last_was_content = True
        last_opens_scope = last_opens_tree = False
        body = line[cur_ind:]
        last_kind = body.split(None, 1)[0].split('=')[0] if body.split() else None
        last_kind_line = lineno

        # [DD-13b.W23.3] INSIDE A CONSUMED BODY NOTHING IS DISPATCHED.
        # `provenance` and `variant` bodies are schema-checked by leg A
        # alone (`validated_by: pcrec` on every row in those scopes — the
        # RECOGNISE-vs-VALIDATE split format_design §2.14 states and §2.24's
        # D4 table publishes) and an `ext` body is interpreted by nobody.
        # What legs B and C owe is the EXTENT. A body line whose value is a
        # bare `|` still opens a prose region — a `variant`'s `note |` sits
        # at indent 2 and its continuation must not escape — but NEVER
        # inside an OPEN SUBTREE, where a bare `|` is the literal byte.
        if len(att) > 1:
            if not att[-1][1] and last_kind in PROSE_KINDS:
                if body[len(last_kind):].strip(' \t') == '|':
                    prose = {'ind': cur_ind, 'lines': [], 'dedent': -1,
                             'owner': '', 'line': lineno}
            continue
        line = body
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
                _fail(path, lineno, 'unknown-token-in-scope',
                      f"'{first}' line before any pattern block -- a body "
                      "directive has no open block to attach to (matches "
                      "tests/harness/run.sh's and src/parse/rxt_source.c's "
                      "own refusal of this line)")
        if line.startswith('pattern '):
            seen_pattern = True
            cur_desc_line = 0
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
                _fail(path, lineno, 'value-shape',
                      f"unknown flag letter(s) {v!r} (only 'i' is defined)")
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
                _fail(path, lineno, 'value-shape',
                      f"'name' wants a definition name (got {v!r})")
            if v in seen_names:
                _fail(path, lineno, 'schema-constraint',
                      f"duplicate block name {v!r} (already "
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
            # [DD-13b.W23.2, §1.8 FOLD-IN 1] A SECOND `description` LINE IN
            # ONE BLOCK IS REFUSED, naming both lines -- [RXTNUL]'s own gap
            # for legs B and C, closed at leg A already
            # (`docs/design/dd13_format/rxtnul_report.md`). `cur_desc_line`
            # is reset to 0 at every `pattern` line below.
            if cur_desc_line:
                _fail(path, lineno, 'schema-constraint',
                      f"a pattern block has one 'description' (already "
                      f"given on line {cur_desc_line})")
            cur_desc_line = lineno
            if v.strip(' \t') == '|':
                # [DD-13b.W23.3] THE `|` FORM IS ACCEPTED NOW. The reversal
                # is W23.1's, not this step's: format_design §1.2.5 widened
                # a block `description` to the full `prose-value` production
                # the day the grammar became two layers, because the rule
                # that forbade it here ("a pattern block's lines are not
                # indented") was a LEXICAL rule and there is no lexical
                # layer left for it to live in. Leg A has accepted it since
                # W23.1 (`block_scalar_in_body.rxtin`); this is legs B and C
                # catching up rather than a second decision. The region's
                # own `results` row is appended when it CLOSES, because its
                # value is not known until then.
                prose = {'ind': 0, 'lines': [], 'dedent': -1,
                         'owner': 'description', 'line': lineno}
            else:
                results.append((lineno, 'description', v))
        elif line.startswith('export '):
            # [DD-13b.W1.3] THE DEFINITION'S DECLARED INTERFACE (D89
            # addendum point 2). A `config-list` of GROUP names — plain
            # identifiers, because a group name is PCRE2's grammar and not
            # the file-namespace one a block `name` uses since this step.
            #
            # RECORDED, NOT ACTED ON: what a block exports changes what a
            # COMPOSED artifact delivers, and this oracle verifies a block
            # against python `re` on its own text. It is parsed here so the
            # three `.rxt` parsers stay comparable on a line all three see —
            # the C1 differential's whole purpose.
            v = line[len('export '):].strip()
            parts = [e.strip() for e in v.split(',')]
            if not v or not all(IDENT_RE.match(e) for e in parts):
                _fail(path, lineno, 'value-shape',
                      f"'export' wants a comma-separated list of group "
                      f"names (got {v!r})")
            results.append((lineno, 'export', ', '.join(parts)))
        elif line.startswith('encoding '):
            # [DD-13b.W1.1 r46sem finding 19] see the 'name' arm above --
            # the same "leg C accepts a strict superset" gap.
            v = line[len('encoding '):].strip()
            if not ident_ok(v):
                _fail(path, lineno, 'value-shape',
                      f"'encoding' wants an identifier (got {v!r})")
            results.append((lineno, 'encoding', v))
        elif line.startswith('engine '):
            # [DD-13b.W1.1 r46sem finding 4, RULED] ONLY `vm` FOR W1.1 --
            # see src/parse/rxt_source.c's twin comment. Leg C used to
            # accept 'dfa' too, while leg B (tests/harness/run.sh) already
            # refused it -- the D80 defect this step's remedy targets.
            v = line[len('engine '):].strip()
            if v != 'vm':
                _fail(path, lineno, 'value-shape',
                      f"unknown 'engine' value {v!r} (only vm is defined)")
            results.append((lineno, 'engine', v))
        elif line.startswith('budget '):
            v = line[len('budget '):].strip()
            if v.startswith('steps='):
                results.append((lineno, 'budget', ('steps', int(v[6:]))))
            elif v.startswith('frames='):
                results.append((lineno, 'budget', ('frames', int(v[7:]))))
            else:
                _fail(path, lineno, 'value-shape',
                      f"unknown 'budget' spec {v!r} (want steps=<n> or frames=<n>)")
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
                _fail(path, lineno, 'value-shape',
                      "'gu internal' is refused: PCREC_ERR_INTERNAL is the "
                      "artifact catching its own inconsistency, never a "
                      "planned outcome a .rxt block may expect")
            if code not in ('steps', 'frames', 'work', 'recurse'):
                _fail(path, lineno, 'value-shape',
                      f"unknown 'gu' code {code!r} (want steps, frames, "
                      "work or recurse)")
            subj, tail = parse_quoted(rest[len(code):].lstrip())
            if tail.strip() != '':
                _fail(path, lineno, 'value-shape',
                      f"unexpected trailing content on gu line: {tail.strip()!r}")
            results.append((lineno, 'gu', (code, subj)))
        elif line.startswith('m "'):
            rest = line[2:]  # keep leading quote
            subj, tail = parse_quoted(rest)
            tail = tail.strip()
            parts = tail.split()
            if len(parts) != 2:
                _fail(path, lineno, 'value-shape', f"bad m line tail {tail!r}")
            start, end = int(parts[0]), int(parts[1])
            results.append((lineno, 'm', (subj, start, end)))
        elif line.startswith('n "'):
            rest = line[2:]
            subj, tail = parse_quoted(rest)
            tail = tail.strip()
            if tail != '':
                _fail(path, lineno, 'value-shape',
                      f"unexpected trailing content on n line: {tail!r}")
            results.append((lineno, 'n', subj))
        elif line.startswith('ms '):
            p, rest = parse_startpos_tail(line, 'ms ')
            subj, tail = parse_quoted(rest)
            tail = tail.strip()
            parts = tail.split()
            if len(parts) != 2:
                _fail(path, lineno, 'value-shape', f"bad ms line tail {tail!r}")
            start, end = int(parts[0]), int(parts[1])
            results.append((lineno, 'ms', (p, subj, start, end)))
        elif line.startswith('ns '):
            p, rest = parse_startpos_tail(line, 'ns ')
            subj, tail = parse_quoted(rest)
            tail = tail.strip()
            if tail != '':
                _fail(path, lineno, 'value-shape',
                      f"unexpected trailing content on ns line: {tail!r}")
            results.append((lineno, 'ns', (p, subj)))
        elif line.startswith('gp '):
            try:
                slot, start, end = parse_group_tail(line, 'gp ')
            except ValueError as e:
                _fail(path, lineno, 'value-shape', str(e))
            results.append((lineno, 'gp', (slot, start, end)))
        elif line.startswith('g '):
            try:
                slot, start, end = parse_group_tail(line, 'g ')
            except ValueError as e:
                _fail(path, lineno, 'value-shape', str(e))
            results.append((lineno, 'g', (slot, start, end)))
        # ---- [DD-13b.W23.3] THE BLOCK-SCOPED W23 ARMS ----
        elif line.startswith('pattern-esc '):
            # THE SECOND BLOCK OPENER (format_design §2.19). Its value is
            # the DECODED bytes, by THE SAME EIGHT-ESCAPE TABLE this file
            # already uses for subjects (`decode_subject`) — not a second
            # vocabulary. Leg B passes the encoded text through to pcrec's
            # own decoder and this leg decodes with the table it has; the
            # two are the same eight escapes and the differential is what
            # keeps them so. `\x00` is refused BY NAME citing K9, exactly as
            # leg A refuses it: the compile entry takes no pattern length,
            # so a NUL-bearing pattern would compile as its prefix and
            # report success.
            seen_pattern = True
            cur_desc_line = 0
            raw = line[len('pattern-esc '):].strip()
            if len(raw) < 2 or raw[0] != '"' or raw[-1] != '"':
                _fail(path, lineno, 'value-shape',
                      "an escaped pattern is double-quoted text "
                      f"(got {raw!r})")
            try:
                pat = decode_subject(raw[1:-1])
            except ValueError as e:
                _fail(path, lineno, 'value-shape', f"'pattern-esc': {e}")
            if '\x00' in pat:
                _fail(path, lineno, 'value-shape',
                      "'\\x00' is refused (K9): the compile entry takes no "
                      "pattern length, so a NUL-bearing pattern compiles as "
                      "its prefix and reports success. Lifts with "
                      "rx_info.pattern_len")
            results.append((lineno, 'pattern', (pat, pcre2_only_next)))
            # [DD-13b.W23.3] THE DUMP CARRIES THE TEXT AS WRITTEN, and the
            # split is deliberate and reported: the ORACLE needs the DECODED
            # bytes (that is what the block matches) while the `--dump`
            # differential compares leg B against leg C, and leg B CANNOT
            # decode — §2.19 forbids a bash decoder outright, so the only
            # spelling both harness legs can produce for this column is the
            # source text. Leg A reports the DECODED text in that column
            # (`rxt_source.c`'s `pattern-esc` arm), so the three do NOT all
            # agree here; the population at this pin is ZERO (no corpus file
            # carries the keyword and the fixtures are `.rxtin`), and the
            # column that settles it is the `esc` column W23.4 adds.
            results.append((lineno, 'pattern_src', raw))
            pcre2_only_next = False
        elif line.startswith('mc '):
            # `mc "<subject>" <n>` / `mc @file:"…" <n>` — the FIND-ALL COUNT
            # (format_design §2.21). The rule is match_api.md §3.1's shipped
            # protocol; this leg VERIFIES it by running that protocol loop
            # in python, and NEVER `re.finditer`, which differs on an
            # empty-preferring pattern (`a*?` over "aaa": 7 against 4).
            rest = line[len('mc '):].lstrip()
            if rest.startswith('@file:'):
                subj, tail = _parse_file_subject(path, lineno, rest, subject_ids)
            else:
                subj, tail = parse_quoted(rest)
            tail = tail.strip()
            if not tail.isdigit():
                _fail(path, lineno, 'value-shape',
                      f"bad mc line tail {tail!r} (want a match count)")
            results.append((lineno, 'mc', (subj, int(tail))))
        elif (line.startswith('m @file:') or line.startswith('n @file:')
              or line.startswith('ms ') and '@file:' in line
              or line.startswith('ns ') and '@file:' in line):
            # [DD-13b.W23.3, H15] A `@file:` SUBJECT on an ordinary case
            # line. The bytes are the FILE'S, byte-exact — which is the
            # whole point, since an inline subject cannot carry a NUL at all
            # and the escape table has no spelling that survives argv.
            kw = line.split(None, 1)[0]
            rest = line[len(kw):].lstrip()
            pos = 0
            if kw in ('ms', 'ns'):
                num, rest = rest.split(None, 1)
                pos = int(num)
                rest = rest.lstrip()
            subj, tail = _parse_file_subject(path, lineno, rest, subject_ids)
            tail = tail.strip()
            if kw in ('m', 'ms'):
                parts = tail.split()
                if len(parts) != 2:
                    _fail(path, lineno, 'value-shape', f"bad {kw} line tail {tail!r}")
                results.append((lineno, 'm' if kw == 'm' else 'ms',
                                (subj, int(parts[0]), int(parts[1])) if kw == 'm'
                                else (pos, subj, int(parts[0]), int(parts[1]))))
            else:
                if tail != '':
                    _fail(path, lineno, 'value-shape',
                          f"unexpected trailing content on {kw} line: {tail!r}")
                results.append((lineno, 'n' if kw == 'n' else 'ns',
                                subj if kw == 'n' else (pos, subj)))
        elif line.startswith('under '):
            # [DD-13b.W23.3] `under <convention> <case-line>` — A COUNTED,
            # LABELLED SKIP AND NEVER A SILENT ONE (format_design §2.17).
            # Scoring a second correct answer is the CONSUMER's act: it
            # requires knowing pcrec's own convention BY NAME, which is
            # engine knowledge an oracle harness must not hold. AR-3's
            # failure mode is exactly a skip nobody counted, so the line is
            # recognised, its shape checked, and the skip counted in main().
            rest = line[len('under '):].lstrip()
            conv = rest.split(None, 1)[0] if rest.split() else ''
            wrapped = rest[len(conv):].lstrip()
            if not NAME_RE.match(conv):
                _fail(path, lineno, 'value-shape',
                      f"'under' wants a convention name (got {conv!r})")
            wkind = wrapped.split(None, 1)[0] if wrapped.split() else ''
            if wkind not in ('m', 'n', 'ms', 'ns', 'mc'):
                _fail(path, lineno, 'value-shape',
                      "'under <convention>' wraps an m/n/ms/ns/mc case line "
                      f"(got {wrapped!r})")
            results.append((lineno, 'under', conv))
        elif line.startswith('tag '):
            # [DD-13b.W23.3] `tag` — a LIST of bare LABELS or `key=value`
            # items with no whitespace in either half (§2.15; r58 R3 removed
            # the quoted `tag-prose` alternative). RECOGNISED and
            # VALUE-CHECKED; the VOCABULARY half (`closed per-key`) is leg
            # A's, since every W23 row reads `validated_by: pcrec`.
            v = line[len('tag '):].strip()
            items = [x for x in re.split(r'[\s,]+', v) if x]
            if not items or not all(
                    IDENT_RE.match(x.split('=', 1)[0]) and not x.endswith('=')
                    for x in items):
                _fail(path, lineno, 'value-shape',
                      f"'tag' wants labels or key=value items (got {v!r})")
            results.append((lineno, 'tag', v))
        elif line.startswith('oracle '):
            # [DD-13b.W23.3] `oracle <engine-ref>[/<version>]` (§2.9).
            # RECOGNISED and SHAPE-CHECKED; naming an oracle this script
            # cannot reach is a LABELLED SKIP, never a refusal — python `re`
            # is the one oracle here and a block naming another is stating a
            # true fact about somebody else's runner.
            v = line[len('oracle '):].strip()
            if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*(/[A-Za-z0-9._-]+)?$', v):
                _fail(path, lineno, 'value-shape',
                      "'oracle' wants an engine reference, optionally "
                      f"'/<version>' (got {v!r})")
            results.append((lineno, 'oracle', v))
        elif line == 'provenance':
            # [DD-13b.W23.3] A SUB-BLOCK OPENER. Legs B and C RECOGNISE the
            # record and CONSUME its body without reading it; pcrec
            # VALIDATES it (format_design §2.14's last paragraph, published
            # per-row as `validated_by: pcrec`). What this arm owes is the
            # EXTENT — `last_opens_scope` is what tells S1 the indented
            # lines below have somewhere to attach.
            last_opens_scope = True
        elif line.startswith('variant '):
            v = line[len('variant '):].strip()
            if not NAME_RE.match(v):
                _fail(path, lineno, 'value-shape',
                      "'variant' wants a testee name -- a letter or '_' then "
                      f"letters, digits, '_', '-' or '.' (got {v!r})")
            last_opens_scope = True
        elif line.startswith('ext '):
            # [DD-13b.W23.3] `ext <consumer>` — THE AUX PRODUCTION, and the
            # cheapest of the three: it opens an OPEN SUBTREE inside which
            # nothing is dispatched by any leg. No key is validated, no
            # value normalised, no row counted — so a body key colliding
            # with a format keyword (`pattern`, `m`, `provenance`) produces
            # NO extra block, NO extra case and NO record anywhere, which is
            # §2.27.3's graduation rule made structural rather than
            # promised.
            v = line[len('ext '):].strip()
            if not NAME_RE.match(v):
                _fail(path, lineno, 'value-shape',
                      "'ext' wants a consumer name -- a letter or '_' then "
                      f"letters, digits, '_', '-' or '.' (got {v!r})")
            last_opens_tree = True
        else:
            # [DD-13b.W23.2] unknown-token-in-scope: the first token has
            # no schema row in this scope at all -- the same fact leg A's
            # `unknown_token()` and leg B's catch-all now state.
            _fail(path, lineno, 'unknown-token-in-scope',
                  f"unrecognized line: {line!r}")
    # [DD-13b.W23.3] END OF FILE CLOSES AN OPEN PROSE REGION, leg A's third
    # `read_prose_region` boundary. Without it a region running to the last
    # line of the file would never yield its value and an EMPTY one would
    # never be refused — silent in both directions.
    if prose is not None:
        prose_finish()
    return results


# [DD-13b.W23.3] `@file:"path" [as <id>] [sha256 <hex64>]` — H15/H6, the
# leg-C half. The bytes are read BYTE-EXACT and carried as one python
# character per byte (`latin-1`), which is the same representation
# `decode_subject`'s own `\xHH` arm produces, so an `@file:` subject and an
# inline one are the same kind of object to every check below.
#
# THE DIGEST IS CHECKED BY WHATEVER READS THE SUBJECT (§2.18) and this leg
# reads it, so it checks. The `as` binding is validated by leg B, which owns
# the per-file id namespace; duplicating the map here would be a second
# place one rule lives, and the differential compares the legs' VERDICTS.
def _parse_file_subject(path, lineno, rest, subject_ids):
    m = re.match(r'@file:"([^"]*)"(.*)$', rest)
    if not m:
        _fail(path, lineno, 'value-shape',
              f"'@file:' wants a double-quoted path (got {rest!r})")
    rel, tail = m.group(1), m.group(2).lstrip()
    m2 = re.match(r'as[ \t]+([A-Za-z_][A-Za-z0-9_.-]*)(.*)$', tail)
    sid = m2.group(1) if m2 else None
    if m2:
        tail = m2.group(2).lstrip()
    want_sha = None
    m3 = re.match(r'sha256[ \t]+([0-9a-fA-F]{64})(.*)$', tail)
    if m3:
        want_sha, tail = m3.group(1).lower(), m3.group(2).lstrip()
    elif re.match(r'sha256([ \t]|$)', tail):
        _fail(path, lineno, 'value-shape', "'sha256' wants exactly 64 hex digits")
    abspath = rel if os.path.isabs(rel) else os.path.join(os.path.dirname(path), rel)
    try:
        with open(abspath, 'rb') as fh:
            raw = fh.read()
    except OSError:
        _fail(path, lineno, 'value-shape',
              f"'@file:' names no readable file: {rel!r} (resolved to {abspath!r})")
    if want_sha is not None:
        got = hashlib.sha256(raw).hexdigest()
        if got != want_sha:
            _fail(path, lineno, 'value-shape',
                  f"'@file:\"{rel}\"' sha256 MISMATCH: the line says "
                  f"{want_sha}, the file is {got}")
    # THE BINDING IS A FUNCTIONAL DEPENDENCY, NOT A UNIQUENESS KEY: every
    # case line naming a subject restates `as <id>`, so equal keys with
    # EQUAL values is the NORMAL spelling and only equal keys with UNEQUAL
    # values is an error. `unique-by` would have refused this production's
    # own documented normal form on its second occurrence (§2.18, r57
    # S-BL1(c)); the refusal names BOTH lines.
    if sid is not None:
        prev = subject_ids.get(sid)
        if prev is None:
            subject_ids[sid] = (abspath, want_sha, lineno)
        elif prev[0] != abspath or prev[1] != want_sha:
            _fail(path, lineno, 'schema-constraint',
                  f"subject id {sid!r} is re-bound to a different (path, "
                  f"sha256) than on line {prev[2]} -- a subject id is a "
                  "FUNCTIONAL binding, so restating the SAME binding is "
                  "normal and a conflicting one is not")
    return raw.decode('latin-1'), tail


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
        # [DD-13b.W1.3] `export` APPENDED after `perr` — see run.sh's twin
        # comment for why appending rather than inserting.
        print('block\t%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (
            path, blk['line'], blk['name'], rxt_escape(blk['desc']),
            rxt_escape(blk['pat']), blk['flags'], blk['features'],
            blk['only'], blk['encoding'], blk['engine'],
            blk['steps'], blk['frames'], blk['perr'], blk['exports']))
        for c in cases:
            print('case\t%s\t%d\t%s\t%d\t%s' % (path, c[0], c[1], c[2], c[3]))

    for lineno, kind, data in entries:
        if kind == 'pattern':
            flush()
            del cases[:]
            blk = {'line': lineno, 'pat': data[0], 'name': '', 'desc': '',
                   'flags': '', 'features': '', 'only': '', 'encoding': '',
                   'engine': '', 'steps': '', 'frames': '', 'perr': '',
                   'exports': ''}
            continue
        if blk is None:
            continue
        if kind == 'flags':        blk['flags'] = data
        elif kind == 'features':   blk['features'], blk['only'] = data[0], ('1' if data[1] else '')
        elif kind == 'name':       blk['name'] = data
        elif kind == 'description':blk['desc'] = data
        elif kind == 'pattern_src': blk['pat'] = data
        elif kind == 'encoding':   blk['encoding'] = data
        elif kind == 'export':     blk['exports'] = data
        elif kind == 'engine':     blk['engine'] = data
        elif kind == 'budget':
            blk['steps' if data[0] == 'steps' else 'frames'] = str(data[1])
        elif kind == 'perr':       blk['perr'] = '1'
        elif kind in ('m', 'ms', 'n', 'ns', 'gu', 'mc'):
            # leg B stores `ms`/`ns` under `m`/`n` with an explicit
            # startpos, which is not a loss: the format DEFINES m/n as
            # ms/ns with P fixed at 0 (docs/spec/rxt_format.md), so the
            # two spellings of one case must dump identically.
            if kind == 'm':    cases.append([lineno, 'm', 0, ''])
            elif kind == 'mc': cases.append([lineno, 'mc', 0, ''])
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


def _rxt_head_probe(path):
    """The first token of the first non-comment, non-blank line, or ''
    for a file with no content -- the SAME cheap test tests/harness/
    run.sh's own `rxt_head_probe` runs, kept in that one shape so this
    leg and leg B cannot silently disagree about what "head-bearing"
    means."""
    try:
        with open(path, 'rb') as f:
            raw = f.read()
    except OSError:
        return ''
    for line in raw.decode('utf-8', errors='surrogateescape').split('\n'):
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        return s.split(None, 1)[0]
    return ''


_RXT_LS_CACHE = {}


def _rxt_list_source(path):
    """pcrec --list-source's raw stdout, cached by REALPATH so no file's
    head is parsed twice in one process (discover()'s subtraction pass
    below is the one caller today). None on failure. `os.path.realpath`
    is python's own `realpath(3)` binding -- the SAME symlink-resolving
    semantics `src/parse/rxt_source.c`'s `include` row `name` column
    comes from, which is the identity this cache's key must agree with
    (tests/harness/run.sh's own `rxt_realpath` needed the identical fix
    after a LOGICAL `cd`+`pwd` silently disagreed with it on a box where
    /tmp is a symlink)."""
    import subprocess
    key = os.path.realpath(path)
    if key in _RXT_LS_CACHE:
        return _RXT_LS_CACHE[key]
    pcrec = os.environ.get('PCREC', os.path.join(_ROOT, 'build', 'pcrec'))
    try:
        r = subprocess.run([pcrec, '--list-source', path],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    out = r.stdout.decode('utf-8', errors='surrogateescape')
    _RXT_LS_CACHE[key] = out
    return out


def discover(args):
    """A directory argument is searched RECURSIVELY (os.walk), matching
    tests/assertions/verify_pcre2.py's own discovery and NOT this
    script's historical one-level glob.

    The glob was the defect r45chk's N1 named: `verify_rxt.py tests`
    matched `tests/*.rxt`, of which there are none, so it verified ZERO
    files and exited reporting success. A discovery that can silently
    narrow to nothing and still read as a pass is the one property this
    script must not have -- see --min-files below for the other half.

    [DD-13b.W23.3a] ENTRY-SET SUBTRACTION (w23_impl.md §1.10.2 rule 3):
    a file this walk turns up that is ALSO the resolved target of some
    OTHER discovered file's `include` line is not counted here -- it is
    part of that file's closure, and leg B (tests/harness/run.sh) is
    where the closure actually gets WALKED (this leg structurally cannot
    open an `include`-bearing entry at all: `include` sits in
    `head_words` above, so parse_rxt raises its head-bearing ValueError
    on the entry itself, exactly as it always has for `lib`/`target`/
    `config` -- the seam ruling, UNCHANGED). What this leg owes is
    narrower than leg B's: not double-counting a fragment that happens
    to ALSO be independently `.rxt`-discoverable, which is the corpus
    control's own claim ("entries == CENSUS_FILES") and the only thing
    THIS leg's population can get wrong."""
    files = []
    named = set()
    for a in args:
        if os.path.isdir(a):
            for root, _dirs, names in os.walk(a):
                files += [os.path.join(root, n) for n in names
                          if n.endswith('.rxt')]
        else:
            files.append(a)
            named.add(a)
    files = sorted(files)

    included_by = {}
    for f in files:
        probe = _rxt_head_probe(f)
        if not probe or probe == 'pattern':
            continue
        out = _rxt_list_source(f)
        if out is None:
            continue
        for line in out.split('\n'):
            if not line or line.startswith('#'):
                continue
            cols = line.split('\t')
            if len(cols) < 3 or cols[0] != 'include':
                continue
            target = cols[2]
            if not target:
                continue
            included_by.setdefault(target, f)

    kept = []
    for f in files:
        rp = os.path.realpath(f)
        if rp in included_by:
            if f in named:
                print(f"{f}: named, absorbed into {included_by[rp]}",
                      file=sys.stderr)
            continue
        kept.append(f)
    return kept


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
                 'perr-python-accepts', 'own-oracle', 'under-convention')
    tot_pass = tot_fail = tot_skip = tot_info = tot_storeuncovered = 0
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
            elif line.startswith('INFO='):
                # "INFO=<n> (...)" -- take the leading integer only.
                got['info'] = int(line[len('INFO='):].split(' ', 1)[0])
            elif line.startswith('STOREUNCOVERED='):
                got['storeuncovered'] = int(
                    line[len('STOREUNCOVERED='):].split(' ', 1)[0])
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
        tot_info += got.get('info', 0)
        tot_storeuncovered += got.get('storeuncovered', 0)
        for key in SKIP_KEYS:
            tot_reason[key] += got.get(key, 0)
        # a child's own failure/info detail is already on its stdout.
        # [C3 THREE-WAY VERDICT] an INFO cell must surface even on an
        # otherwise-clean (returncode 0, fail 0) child — "always printed"
        # cannot depend on whether the same file also happened to fail.
        if got['fail'] or got.get('info', 0) or r.returncode != 0:
            for ln in out.splitlines():
                if ln.startswith('===') or ln.startswith('  line '):
                    print(ln)

    print()
    print("=== Summary ===")
    print(f"PASS={tot_pass} FAIL={tot_fail}")
    print(f"INFO={tot_info} (python-divergent, pcre2-confirmed; never a failure)")
    print(f"STOREUNCOVERED={tot_storeuncovered} (of {tot_fail} FAIL above; the rest are real store-confirmed disagreements)")
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
    # [C3 THREE-WAY VERDICT] a python-vs-expectation disagreement the C3
    # oracle store CONFIRMS (i.e. PCRE2 agrees with the expectation, python
    # alone was wrong) is counted here, separately from PASS/FAIL/SKIP —
    # never a failure, always printed, no gate on its count. Modelled on
    # tests/thread/run_stackdepth_tests.sh's `record()` bucket: a fourth
    # verdict that is neither a pass, a fail, nor a skip.
    total_info = 0
    # Of the failures counted in total_fail, how many are STORE-UNCOVERED
    # (the C3 store has no committed answer for this exact question, so the
    # verdict fell back to today's python-only FAILURE) rather than a real
    # transcription-tripwire disagreement (the store covers the question
    # AND disagrees with the expectation too). Counted so the population is
    # visible rather than silently folded into an ordinary failure — see
    # docs/design/c3_three_way.md.
    total_storeuncovered = 0
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
    # [DD-13b.W23.3] `under`'s COUNTED, LABELLED SKIP. Its own bucket
    # rather than a share of an existing one: an `under` line is a real
    # expectation this oracle declines to score for a stated reason
    # (scoring a second correct answer needs pcrec's convention BY NAME),
    # and AR-3's failure mode is exactly a skip nobody counted.
    total_skip_under = 0
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
        skipped_under = 0
        mc_count = 0
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
        # [DD-13b.W23.3] the BLOCK's declared encoding, tracked for exactly
        # one consumer: `mc`'s empty-match advance. SW7 makes that advance
        # normative on ill-formed UTF-8 ("from pos + 1, skip bytes in the
        # range 0x80-0xBF"), so a leg reimplementing the protocol has to
        # know which encoding the block asked for. Nothing else here reads
        # it -- the `encoding` directive stays a pcrec-side axis.
        cur_encoding = ''
        file_failures = []
        file_info = []

        for lineno, kind, data in entries:
            if kind == 'pattern':
                cur_pattern, cur_skip = data
                cur_pattern_lineno = lineno
                compile_error = None
                compiled = None
                cur_reflags = 0
                cur_encoding = ''
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

            if kind == 'encoding':
                cur_encoding = data
            if kind in ('name', 'description', 'encoding', 'engine',
                        'budget', 'frames_buffer', 'tag', 'oracle',
                        'pattern_src'):
                # [DD-13b.W23.3] `tag` and `oracle` join the list for the
                # same reason every other member is on it: they are BLOCK
                # DECLARATIONS with no meaning for python `re`. `tag` is
                # metadata whose vocabulary half is leg A's; `oracle` names
                # an engine THIS SCRIPT IS NOT — python is its one oracle —
                # so recognising the declaration and continuing is the
                # honest answer, and a block does not stop being
                # python-verifiable because it names somebody else's
                # reference engine. They are PARSED and value-checked at
                # parse time (a control that refuses to read a line is no
                # control for it) and then deliberately ignored here.
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

            if kind == 'under':
                # [DD-13b.W23.3] `under <convention>` — A COUNTED, LABELLED
                # SKIP (format_design §2.17). Scoring a second correct
                # answer per convention would need this script to know
                # pcrec's own convention BY NAME, which is engine knowledge
                # an oracle must not hold; the bench's runner is the scorer.
                # Counted rather than ignored: AR-3's failure mode is
                # exactly a skip nobody counted.
                skipped += 1
                skipped_under += 1
                continue

            if kind == 'mc':
                # [DD-13b.W23.3] `mc` — THE FIND-ALL COUNT, verified by
                # RUNNING `docs/spec/match_api.md` §3.1's PROTOCOL LOOP in
                # python and NEVER by `re.finditer` (format_design §2.21).
                # The two disagree on an empty-PREFERRING pattern — `a*?`
                # over "aaa" is 4 by the protocol and 7 by `finditer`,
                # because finditer implements PCRE2's NOTEMPTY retry, a span
                # set pcrec's own entry points cannot express. Reaching for
                # `finditer` here would therefore import a divergence rather
                # than check for one.
                mc_count += 1
                subj, want = data
                if compiled is None:
                    skipped += 1
                    skipped_no_python += 1
                    continue
                got = _findall_protocol(compiled, subj, cur_encoding)
                if got == want:
                    total_pass += 1
                else:
                    file_failures.append((lineno, f"pattern {cur_pattern!r} subject {subj!r}: expected {want} find-all match(es) but the §3.1 protocol reports {got}"))
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
                    if mo is None or mo.span() != (start, end):
                        got_desc = "no match" if mo is None else f"span {mo.span()}"
                        v, desc = _verdict_match_at(
                            cur_pattern, subj, 0, bool(cur_reflags & re.IGNORECASE),
                            True, (start, end))
                        if v == 'confirmed':
                            file_info.append((lineno, f"pattern {cur_pattern!r} subject {subj!r}: python got {got_desc} (expected match [{start},{end})); the C3 oracle store CONFIRMS the expectation ({desc}) -- informational, not a failure"))
                            total_info += 1
                            continue
                        elif v == 'uncovered':
                            total_storeuncovered += 1
                            file_failures.append((lineno, f"STORE-UNCOVERED: pattern {cur_pattern!r} subject {subj!r}: expected match [{start},{end}) but python got {got_desc}"))
                        else:
                            file_failures.append((lineno, f"pattern {cur_pattern!r} subject {subj!r}: expected match [{start},{end}) but python got {got_desc} AND the C3 oracle store disagrees too ({desc})"))
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
                        v, desc = _verdict_match_at(
                            cur_pattern, subj, 0, bool(cur_reflags & re.IGNORECASE),
                            False, None)
                        if v == 'confirmed':
                            file_info.append((lineno, f"pattern {cur_pattern!r} subject {subj!r}: python got match {mo.span()} (expected no match); the C3 oracle store CONFIRMS the expectation ({desc}) -- informational, not a failure"))
                            total_info += 1
                            continue
                        elif v == 'uncovered':
                            total_storeuncovered += 1
                            file_failures.append((lineno, f"STORE-UNCOVERED: pattern {cur_pattern!r} subject {subj!r}: expected no match but python got {mo.span()}"))
                        else:
                            file_failures.append((lineno, f"pattern {cur_pattern!r} subject {subj!r}: expected no match but python got {mo.span()} AND the C3 oracle store disagrees too ({desc})"))
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
                    if mo is None or mo.span() != (start, end):
                        got_desc = "no match" if mo is None else f"span {mo.span()}"
                        v, desc = _verdict_match_at(
                            cur_pattern, subj, p, bool(cur_reflags & re.IGNORECASE),
                            True, (start, end))
                        if v == 'confirmed':
                            file_info.append((lineno, f"pattern {cur_pattern!r} subject {subj!r} startpos {p}: python got {got_desc} (expected match [{start},{end})); the C3 oracle store CONFIRMS the expectation ({desc}) -- informational, not a failure"))
                            total_info += 1
                            continue
                        elif v == 'uncovered':
                            total_storeuncovered += 1
                            file_failures.append((lineno, f"STORE-UNCOVERED: pattern {cur_pattern!r} subject {subj!r} startpos {p}: expected match [{start},{end}) but python got {got_desc}"))
                        else:
                            file_failures.append((lineno, f"pattern {cur_pattern!r} subject {subj!r} startpos {p}: expected match [{start},{end}) but python got {got_desc} AND the C3 oracle store disagrees too ({desc})"))
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
                        v, desc = _verdict_match_at(
                            cur_pattern, subj, p, bool(cur_reflags & re.IGNORECASE),
                            False, None)
                        if v == 'confirmed':
                            file_info.append((lineno, f"pattern {cur_pattern!r} subject {subj!r} startpos {p}: python got match {mo.span()} (expected no match); the C3 oracle store CONFIRMS the expectation ({desc}) -- informational, not a failure"))
                            total_info += 1
                            continue
                        elif v == 'uncovered':
                            total_storeuncovered += 1
                            file_failures.append((lineno, f"STORE-UNCOVERED: pattern {cur_pattern!r} subject {subj!r} startpos {p}: expected no match but python got {mo.span()}"))
                        else:
                            file_failures.append((lineno, f"pattern {cur_pattern!r} subject {subj!r} startpos {p}: expected no match but python got {mo.span()} AND the C3 oracle store disagrees too ({desc})"))
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
                            v, store_got = _verdict_captures(
                                cur_pattern, last_case_subj, last_case_pos,
                                slot, bool(cur_reflags & re.IGNORECASE),
                                (start, end))
                            if v == 'confirmed':
                                file_info.append((lineno, f"pattern {cur_pattern!r} subject {last_case_subj!r} startpos {last_case_pos}: group slot {slot} python got {got} (expected ({start},{end})); the C3 oracle store CONFIRMS the expectation ({store_got}) -- informational, not a failure"))
                                total_info += 1
                                continue
                            elif v == 'uncovered':
                                total_storeuncovered += 1
                                file_failures.append((lineno, f"STORE-UNCOVERED: pattern {cur_pattern!r} subject {last_case_subj!r} startpos {last_case_pos}: group slot {slot} expected ({start},{end}) but python got {got}"))
                            else:
                                file_failures.append((lineno, f"pattern {cur_pattern!r} subject {last_case_subj!r} startpos {last_case_pos}: group slot {slot} expected ({start},{end}) but python got {got} AND the C3 oracle store disagrees too ({store_got})"))
                        else:
                            total_pass += 1
                            continue
            total_fail += 1

        per_file_counts[fname] = (m_count, n_count, ms_count, ns_count, perr_count, g_count, gp_count, len(file_failures), len(file_info))
        total_skip += skipped
        total_skip_pcre2_only += skipped_pcre2_only
        total_skip_giveup += skipped_giveup
        total_skip_composed += skipped_composed
        total_skip_no_python += skipped_no_python
        total_skip_perr_accept += skipped_perr_accept
        total_skip_own_oracle += skipped_own_oracle
        total_skip_under += skipped_under
        if skipped:
            print(f"  {fname}: {skipped} case(s) skipped, not python-verifiable "
                  f"(pcre2-only {skipped_pcre2_only}, give-up {skipped_giveup}, "
                  f"composed {skipped_composed}, no-python-expression "
                  f"{skipped_no_python}, perr-python-accepts "
                  f"{skipped_perr_accept}, own-oracle {skipped_own_oracle}, "
                  f"under-convention {skipped_under})")
        # [C3 THREE-WAY VERDICT] ALWAYS PRINTED, per file, same shape as the
        # FAILURES block below -- an informational cell that is silent by
        # default is exactly the "quiet bucket" shape this project's own
        # K35 lesson warns about (docs/dev/learnings.md §3).
        if file_info:
            print(f"=== {fname}: {len(file_info)} INFO (python-divergent, pcre2-confirmed by the C3 oracle store; NOT failures) ===")
            for lineno, msg in file_info:
                print(f"  line {lineno}: {msg}")
        if file_failures:
            print(f"=== {fname}: {len(file_failures)} FAILURES ===")
            for lineno, msg in file_failures:
                print(f"  line {lineno}: {msg}")

    print()
    print("=== Summary ===")
    grand_m = grand_n = grand_ms = grand_ns = grand_p = grand_g = grand_gp = grand_f = grand_i = 0
    for fname in sorted(per_file_counts):
        m_count, n_count, ms_count, ns_count, perr_count, g_count, gp_count, fails, infos = per_file_counts[fname]
        grand_m += m_count; grand_n += n_count
        grand_ms += ms_count; grand_ns += ns_count
        grand_p += perr_count; grand_f += fails
        grand_g += g_count; grand_gp += gp_count
        grand_i += infos
        total = m_count + n_count + ms_count + ns_count + perr_count + g_count + gp_count
        status = "OK" if fails == 0 else f"{fails} FAIL"
        if infos:
            status += f" ({infos} INFO)"
        print(f"  {fname:28s} m={m_count:3d} n={n_count:3d} ms={ms_count:3d} ns={ns_count:3d} perr={perr_count:3d} g={g_count:3d} gp={gp_count:3d} total={total:3d}  [{status}]")
    print()
    grand_total = grand_m + grand_n + grand_ms + grand_ns + grand_p + grand_g + grand_gp
    print(f"TOTAL: m={grand_m} n={grand_n} ms={grand_ms} ns={grand_ns} perr={grand_p} g={grand_g} gp={grand_gp} cases={grand_total}")
    print(f"PASS={total_pass} FAIL={total_fail}")
    # [C3 THREE-WAY VERDICT] the fourth, always-printed, never-gated bucket
    # (docs/design/c3_three_way.md): python disagreed with the corpus
    # expectation and the committed C3 oracle store CONFIRMS the
    # expectation is right anyway -- counted so the population is visible,
    # never folded into PASS (python did not verify it) or FAIL (PCRE2, the
    # compatibility target, agrees with pcrec).
    print(f"INFO={total_info} (python-divergent, pcre2-confirmed; never a failure)")
    # Of FAIL above, how many are a STORE-UNCOVERED clean miss (the C3 store
    # has no committed answer for this exact question) rather than a real
    # disagreement the store also confirms is wrong. A nonzero count here
    # is not itself an alarm -- it is exactly today's python-only verdict,
    # preserved as the safe fallback -- but a growing one names exactly
    # which cells `tests/rxtsource/build_c3_store.py` should grow to cover.
    print(f"STOREUNCOVERED={total_storeuncovered} (of {total_fail} FAIL above; the rest are real store-confirmed disagreements)")
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
          f"own-oracle={total_skip_own_oracle} "
          f"under-convention={total_skip_under})")
    if grand_f == 0:
        print("ALL CHECKS PASSED (100%)")
    else:
        print(f"{grand_f} FAILURES REMAIN")
        sys.exit(1)


if __name__ == '__main__':
    main()
