#!/usr/bin/env bash
# tests/reject/run_reject_tests.sh — the mandate's central guarantee, tested.
#
# WHY THIS EXISTS. The project rule is that a construct outside the base tier
# must "fail with a clean 'requires module X' error, never miscompile". Until
# this file, NOTHING checked that. The .rxt corpus cannot: a `perr` block
# asserts only THAT the pattern is rejected, never WHY, and the module name is
# the whole point (assertion 2 below).
#
# CORRECTED 2026-08-10 (FIX-1). This comment used to add a second reason — that
# a `perr` block also needs the PYTHON oracle to fail, and that `# pcre2-only`
# cannot rescue it "because verify_rxt.py's perr branch does not consult it".
# The first half is true; the second is FALSE, and it was never measured. The
# skip test at verify_rxt.py:218 sits BEFORE the perr branch at :222, so a
# `# pcre2-only` block's perr line is skipped like any other case. Measured:
# tests/base/syntax_errors.rxt now carries seven such blocks for K5 and
# verify_rxt.py reports them as skipped while run.sh still asserts every one
# against pcrec. So the mechanism exists — it just cannot assert a NAME, which
# is why this file is still the only home for that.
#
# The gap was not hypothetical. `\v` was decoded as vertical tab (0x0B) when
# PCRE2 defines it as vertical WHITESPACE (0x0a 0x0b 0x0c 0x0d 0x85) — a silent
# miscompile that survived because python `re` reads `\v` as 0x0B too, so the
# base-tier oracle agreed with the bug. It was found by reading the PCRE2
# syntax reference against the parser, not by any test. This file is the net
# that should have caught it.
#
# WHAT IT ASSERTS, per construct:
#   1. pcrec exits exactly 1 — not 0 (accepted, i.e. possibly miscompiled) and
#      not >=124 (crash/timeout). A crash must never satisfy a rejection
#      expectation (the same rule the .rxt harness applies to perr, R1 P-C1).
#   2. the diagnostic contains the expected text, normally "requires module
#      'NAME'". Getting the NAME right matters: it is the caller's only
#      pointer to what would implement the construct.
#   3. no output file is left behind by a failed compile.
#
# Usage: bash tests/reject/run_reject_tests.sh
# Env: PCREC (default <root>/build/pcrec), KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
KEEP="${KEEP:-0}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "reject: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
seen=""   # every pattern that actually PASSED a check, for the manifest below
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

nrej=0
reject() { # reject <pattern> <expected-substring> [display-label]
    # `timeout` on every invocation is load-bearing, not defensive (R7/T-11):
    # this file's header promises rc >= 124 is a failure, and without it that
    # branch was UNREACHABLE — pcrec cannot return 124 on its own, so a hanging
    # or ballooning compile hung the suite instead of failing it. Not
    # hypothetical: dropping the `big_n` raise turns three of the K5 rows into
    # legal multi-GB bounded repeats, and a critic observed a 6.5 GB allocation
    # inside an un-timeout-ed call here.
    local pat="$1" want="$2" show="${3:-$1}" out rc
    # A logged pattern containing a NEWLINE splits `seen` into two lines, and
    # the duplicate detector then compares fragments — a two-line pattern whose
    # halves read like unrelated single-line rows reports a FALSE duplicate for
    # rows that are not duplicated at all (R9/C4V-1). `accept()` has carried a
    # display label for this hazard since it was written; `reject()` did not,
    # and the duplicate detector is what made the omission matter. Third
    # argument is that label. Refusing the newline outright rather than only
    # offering the label is deliberate: an optional guard that must be
    # remembered is the same shape as the bug.
    case "$show" in
        *"
"*) bad "reject: a logged pattern contains a newline, which would split the coverage log and confuse the duplicate check. Pass a single-line display label as the third argument"
            return ;;
    esac
    # An EMPTY `want` silently turns assertion 2 back into assertion 1. The text
    # check below is `case "$out" in *"$want"*`, and `*""*` matches every string
    # — so a blanked expectation degrades "rejected for the stated reason" to
    # "rejected at all", passes, and prints `PASS: reject 'X' -> ` with nothing
    # after the arrow, which nothing greps for. Getting the NAME right is this
    # file's entire reason to exist over a `perr` block, so refuse the call
    # rather than let it pass vacuously (R9/C4-1). A genuinely MISSING argument
    # is already loud — `set -u` kills the script — it is the empty string that
    # is quiet. The iterated path guards its own inputs the same way, at the
    # `$3 == "" || $11 == ""` BADROW check.
    #
    # BLANK-ONLY, not merely empty. `[ -z "$want" ]` was the first version and a
    # critic defeated it with a single space: every diagnostic this compiler
    # prints is an English sentence, so `want=" "` is a substring of all of them
    # and asserts nothing (R9/C4V-2). A tab does NOT currently defeat it — no
    # message contains one — but that is a property of today's message corpus,
    # not of the guard, so the guard rejects all whitespace.
    #
    # What this canNOT do, stated rather than implied: a short but non-blank
    # expectation like `:` or `pcrec` is equally uninformative and equally
    # legal. No length or content floor distinguishes a lazy expectation from a
    # legitimately short one, so the guard stops at "asserts literally nothing"
    # and review is what covers the rest.
    case "$want" in
        *[![:space:]]*) ;;
        *) bad "reject '$show': expected-substring is empty or all whitespace. Every pcrec diagnostic contains a space, so that asserts only that pcrec exited 1 — name the diagnostic"
           return ;;
    esac
    # AND THE BLANK GUARD WAS NOT ENOUGH EITHER (R9/C4V-4). Every diagnostic this
    # compiler prints has the identical envelope `pcrec: <message> (pattern
    # offset N)`. A critic ran the whole suite, collected all 200 real
    # diagnostics, and measured which `want` literals match all of them:
    # `:`, `pcrec`, `pattern offset`, `(`, `)` and the single letters
    # a e s n r t o are each 200/200. None is blank, so none was caught.
    #
    # The discriminating rule is not a LENGTH floor — `:` is one character and
    # `(pattern offset 4)` is eighteen, and 31 rows legitimately pin an offset
    # with that suffix, so no floor separates them. What distinguishes them is
    # that everything dangerously generic lives entirely inside the CONSTANT
    # part. So: reject a `want` that is a substring of the envelope itself. It
    # asserts nothing about which construct or module was named.
    # `(pattern offset 4)` is not a substring of it — the digit is real content —
    # so the offset-pinning rows are unaffected.
    case "pcrec: (pattern offset )" in
        *"$want"*)
            bad "reject '$show': expected-substring \"$want\" is part of the envelope EVERY pcrec diagnostic has (\"pcrec: ... (pattern offset N)\"), so it matches all 200 of them and names no construct. Assert the message, not the frame"
            return ;;
    esac
    nrej=$((nrej + 1))
    rm -f "$WORKDIR/out.c" "$WORKDIR/out.h"
    out="$(timeout 60 "$PCREC" -p rx -o "$WORKDIR/out.c" -- "$pat" 2>&1 >/dev/null)"; rc=$?
    if [ "$rc" -eq 0 ]; then
        bad "reject '$pat': ACCEPTED (exit 0) — an unsupported construct was compiled instead of diagnosed, which is the miscompile the mandate forbids"
        return
    fi
    if [ "$rc" -ne 1 ]; then
        bad "reject '$pat': exit $rc (crash or timeout), not a clean exit-1 rejection"
        return
    fi
    case "$out" in
        *"$want"*) ;;
        *) bad "reject '$pat': wrong diagnostic. want substring: $want ; got: $out"
           return ;;
    esac
    if [ -f "$WORKDIR/out.c" ] || [ -f "$WORKDIR/out.h" ]; then
        bad "reject '$pat': rejected but still wrote an output file"
        return
    fi
    seen="$seen
$show"
    ok "reject '$show' -> $want"
}

naccept=0
accept() { # accept <pattern> [display-label]
    # The control: the table must not pass by rejecting everything.
    # The optional label is for patterns containing RAW control bytes, which
    # would otherwise put a newline or a non-UTF-8 byte into this script's own
    # output and break anything that reads it as text.
    local pat="$1" show="${2:-$1}" out rc
    naccept=$((naccept + 1))
    rm -f "$WORKDIR/ok.c" "$WORKDIR/ok.h"
    out="$(timeout 60 "$PCREC" -p rx -o "$WORKDIR/ok.c" -- "$pat" 2>&1 >/dev/null)"; rc=$?
    if [ "$rc" -ge 124 ]; then
        bad "accept '$show': exit $rc — timed out or was killed, which is not 'compiles'"
        return
    fi
    if [ "$rc" -ne 0 ]; then
        bad "accept '$show': base-tier construct was REJECTED ($out) — the reject table has swallowed supported syntax"
        return
    fi
    # Exit 0 is not the whole claim (R7/T-10). reject() makes three assertions
    # and this made ONE, so "compiles" meant only "did not say no" — a pcrec
    # that exited 0 and emitted nothing would have satisfied all 45 controls.
    # The `rm` above is as load-bearing as the test: without it a stale file
    # from the previous accept satisfies this vacuously.
    if [ ! -s "$WORKDIR/ok.c" ]; then
        bad "accept '$show': exit 0 but no non-empty output was written — 'compiles' has to mean something was emitted"
        return
    fi
    seen="$seen
$show"
    ok "accept '$show' (base tier still compiles)"
}

# ---- a class-opening construct as a RANGE ENDPOINT (R9/SPEC-FA) ----
# PCRE2 error 150. pcrec read the `[` as an ordinary literal upper bound and
# EMITTED A MATCHER — the silent wrong matcher the mandate forbids, 546
# instances in a 1,530-pattern sweep, and invisible to every suite here.
#
# WHY IT WAS INVISIBLE, which is the part worth keeping: `a` is 0x61 and `[` is
# 0x5b, so `[a-[:digit:]]` is rejected as an out-of-order range long before the
# endpoint matters — and every range in this repository is `a`-based. The bug
# needed a lower bound BELOW `[`. It was found by a test writer working from the
# spec with no sight of the code, which is why the alphabet was `0-` and not
# `a-`. A test derived from the implementation inherits the implementation
# author's alphabet.
reject '[0-[:digit:]]'  "invalid range in character class"
reject '[*-[..]]'       "invalid range in character class"
reject '[A-[=b=]]'      "invalid range in character class"
reject '[0-[.a.]]'      "invalid range in character class"
reject '[0-[:foo:]]'    "invalid range in character class"   # position beats the name
reject '[0-[:digit:]'   "invalid range in character class"   # class never closes
# And the accept-controls that pin where the boundary is NOT. The test is the
# construct's own recognition rule, not "the byte is `[`": each of these has a
# `[` in the endpoint and no pair that closes, and libpcre2 compiles all four.
accept '[0-[a]'
accept '[0-[]'
accept '[0-[:]'
accept '[0-[:digit]'
echo "== base tier must still compile (control) =="
# Without these, a parser that rejected EVERYTHING would score 100% below.
accept 'abc'
accept 'a|b'
accept '(a)(?:b)'
accept 'a*b+c?d{2,3}e{2,}f{3}'
accept 'a*?b+?'
accept '[a-z^]'
accept '[^a-z]'
accept '.'
accept '^a$'
accept '\n\t\r\f\a\e'
accept '\x41\x2e'   # \x{...} is NOT base tier — it is in the reject table below
accept '\.\*\+\?\[\]\(\)\{\}\|\^\$\\'

# The MALFORMED braces, and they are load-bearing rather than decorative.
# K6's fix rejects a `{` in ATOM position only when it parses as a quantifier;
# the obvious over-reach — "a `{` where no atom precedes it is an error" —
# passes every K6 rejection row below and breaks all of these. Every one
# compiles as ordinary literal text in libpcre2 10.46, measured, not assumed.
accept 'a{'
accept 'a{}'
accept 'a{,}'
accept 'a{1'
accept 'a{2,3,4}'
accept '}'
accept '{'
accept '{}'
accept '{,}'
accept '{1'
accept '{}{1}'      # literal `{`, then a `}` quantified by {1} — PCRE2 compiles it
# K5's over-reach guard, the same shape one level down: a count above 65535 in
# a form that is NOT a quantifier stays literal. If the overflow were judged
# where it is DETECTED rather than where the quantifier is CONFIRMED, these
# three would become errors and PCRE2 accepts all three.
accept 'a{65536'
accept 'a{65536x}'
accept 'a{65536,x}'
# ...and the SECOND number's half of the same guard, which was missing until
# R7/T-5 measured it: all three rows above overflow the FIRST number, so
# hoisting the `big_n` raise above its decline test — the identical mistake,
# mirrored — rejected five patterns libpcre2 compiles with every suite green.
# A guard that is symmetric in the code needs coverage that is symmetric too.
accept 'a{1,65536x}'
accept 'a{,65536x}'
accept 'a{1,65536'
accept '{1,65536x}'
# The BOUNDARY itself, which nothing else pins: 65535 is a legal count, so an
# off-by-one in K5's ceiling turns this into "number too big". The empty group
# is what makes it cheap — `a{65535}` would need 65535 NFA states and dies on
# the DFA cap long before it could say anything about the parser. libpcre2
# answers error 120 "regular expression is too large" here, which is PCRE2's
# own size ceiling rather than a syntax verdict (the same class tests/fuzz/
# already excludes), so the comparison legitimately stops at pcrec's parser.
accept '(?:){65535}'
# K8's over-reach guard: PCRE2 skips SPACE and TAB inside `{...}` and NO other
# whitespace. `isspace()` would have been the obvious spelling and is wrong.
#
# This has to live here rather than in the corpus, and the reason is worth
# keeping. A `.rxt` pattern line cannot carry a raw control byte — a newline
# ends the line, and `\n` WRITTEN in a pattern is an escape that pcrec decodes
# in atom position, long after try_quant has already declined the brace. So a
# corpus case spelled `a{\n1}` exercises the escape decoder and never shows
# try_quant a newline at all. Measured: with `isspace()` substituted for the
# real test, every such corpus case still passes and this file still passed
# too until these five rows existed.
#
# The discriminating shape is a TOO-BIG count behind the byte. If the byte were
# skipped the count would be read and rejected (105); because it is not, the
# whole brace is literal text and compiles. libpcre2 10.46 compiles all five.
#
# Only the four C0 bytes, deliberately. A 0xa0 row was written first — it would
# guard against an `isspace()` under a Latin-1 locale — and then removed,
# because this box's `timeout` (see the wrapper in accept()) rejects invalid
# UTF-8 in argv and exits 125, and the row measured nothing anyway: the
# `isspace()` sabotage costs 4 checks, all of them C0. If you re-add a
# high-byte row, it cannot go through `timeout`.
for b in 'n:\n' 'r:\r' 'v:\v' 'f:\f'; do
    accept "$(printf "a{${b#*:}65536}")" "a{<${b%%:*}>65536}"
done

echo
echo "== character-type escapes -> module 'classes' =="
for e in d D s S w W h H v V; do
    reject "\\$e"     "\\$e requires module 'classes'"
    reject "[\\$e]"   "\\$e in a class requires module 'classes'"
done
# `\N` is the exception and PCRE2 is the reason: the ATOM is a real construct
# module `classes` will implement, and INSIDE a class PCRE2 forbids it outright
# (error 71) and always will. So the two positions get two different KINDS of
# answer, and the in-class one must promise no module (R9/SPEC-classes-F1).
reject '\N'    "\N requires module 'classes'"
reject '[\N]'  "\N is not valid inside a character class"

# The other nine escapes PCRE2 forbids inside a class, same rule, error 107.
# The atom is real and owed a module; the in-class position is not a construct,
# so naming one there is the over-promise D26 calls a defect. Found by a test
# writer reading the spec with no sight of src/ — the knowledge was already in
# the `\N` row's own note, in a field nothing reads.
for e in A B G K Z z C R X; do
    reject "[\\$e]"  "\\$e is not valid inside a character class"
done
# ...and the control that keeps the rule from swallowing the whole doorway:
# `\b` inside a class is BASE syntax (backspace), and `\d` is a real construct
# PCRE2 supports there, so it still names its module. Both directions pinned.
accept '[\b]'
reject '[[:alpha:]]' "POSIX class [:...:] requires module 'classes'"
reject '[[:^alpha:]]' "POSIX class [:...:] requires module 'classes'"   # ^ negates
reject '[[:xdigit:]]' "POSIX class [:...:] requires module 'classes'"
# NAMES PCRE2 DOES NOT KNOW, and these three rows CHANGED at FIX-2 — which is
# the comment that used to sit here being right in advance. It said they "are
# exactly the rows a name-keyed table would have to get right (R6 fidelity
# critic F13: the list is 14 names and case-sensitive)". FIX-2 built that table,
# so pcrec no longer promises module 'classes' for a name no module can ever
# implement; it says what libpcre2 says. Case-sensitivity is pinned by
# `[[:AlPhA:]]`, which R6 added for precisely this moment.
reject '[[:foo:]]'    "unknown POSIX class name"
reject '[[::]]'       "unknown POSIX class name"
reject '[[:AlPhA:]]'  "unknown POSIX class name"
reject '[[:ALPHA:]]'  "unknown POSIX class name"
reject '[[:^foo:]]'   "unknown POSIX class name"
reject '[[:al pha:]]' "unknown POSIX class name"
# ...and the POSITION rule wins over the NAME rule, which is libpcre2's own
# order: an unknown name at a class's own bracket is still the position error,
# because the construct is in the wrong place before its name comes up.
reject '[:foo:]'      "POSIX class [:...:] is only valid inside a character class"
reject '\x{41}'      "\\x{...} requires module 'unicode-props'"

# POSIX collating elements / equivalence classes. PCRE2 REJECTS these rather
# than treating them as literals, so rejecting them IS compliance and the
# message deliberately mirrors PCRE2's own. pcrec accepted all of these
# silently until 2026-08-09, as a class of literal `[` `.` `a` characters —
# a pattern PCRE2 refuses, given a meaning PCRE2 never assigns it.
#
# The trigger requires a matching `.]` / `=]` terminator, so the forms without
# one are ORDINARY class members and must still compile. Those live in the
# accept list below, and they matter more than the rejections: over-rejecting
# here would break patterns that PCRE2 accepts, which is the opposite failure
# and just as wrong. Every row on both sides was checked against libpcre2 10.46.
for p in '[.a.]' '[=a=]' '[[.a.]]' '[[=a=]]' '[..]' '[.a.b.]' '[x[.a.]y]' '[a[=b=]c]'; do
    reject "$p" "POSIX collating elements are not supported"
done
accept '[.a]'    # no terminator -> ordinary members
accept '[=a]'
accept '[.]'
accept '[[.]'
accept '[a[.b]'
accept '[^.a.]'  # `^` sits between the bracket and the delimiter
accept '[a.b.]'  # the `.` is not preceded by `[`
# DOORWAY 4a — the class's OWN bracket as the opener. Every other probe of this
# doorway in the whole repo (the corpus, the rows above, and registry_check's
# `[[%ca%c]]` sweep template) puts a literal `[` between the class bracket and
# the delimiter byte, so all of them test 4b and NONE tests 4a. That is why
# deleting SR-2's `at_class_open` guard changed 0 of 4173 hashed cases and broke
# no test: the guard was not invisible, it was simply never entered (R5
# behaviour critic, FINDING 1). These two enter it, and both are accepted by
# libpcre2 10.46 as well.
#
# The clause that stood here — "deliberately not `[::]` or `[:a:]`, which PCRE2
# REJECTS and pcrec wrongly accepts (K3); pinning those would cement the bug" —
# described the tree before FIX-2. K3 is fixed and both patterns are now pinned
# as rejections in the K3 section below, which is where that sentence should
# have been updated (R9). This is also the only home for these two rows: FIX-2
# added a second copy of both in that section, and the duplicate check above is
# what surfaced it.
accept '[:]'
accept '[:a]'
# The `]` half of "a matching `.]` appears later". Every other control here
# either has no second delimiter or has a real `.]`, so replacing the
# terminator test with a bare `pat[i] == c2` was invisible to the whole suite
# (R5 tests critic, F-7b). PCRE2 accepts this one.
accept '[.a.b]'

# A letter with NO registry row falls through to "unknown escape", and the
# IN-CLASS spelling is a separate message that no test reached before R5 —
# deleting it changed nothing anywhere in the suite.
reject '\q'   "unknown escape \\q"
reject '[\q]' "unknown escape \\q in class"

# The five escapes below are REAL PCRE2 constructs (\U and \u under ALT_BSUX;
# \F, \L, \l in no mode — PCRE2 error 137 groups all five with \N{name}) that
# pcrec currently answers through the same rowless fall-through as \q, because
# there was nowhere to put "real construct, mode not offered" (R11
# disposition 14; extension design §7.1). The design gives all five ROWS with a
# status of their own. These pins are what make that change arrive as a
# deliberate edit here rather than a silent rewording — the atom and in-class
# spellings are separate messages, per letter (A1, approved 2026-08-11).
for e in U u F L l; do
    reject "\\$e"   "unknown escape \\$e"
    reject "[\\$e]" "unknown escape \\$e in class"
done

echo
echo "== assertions =="
for e in b A Z z G K; do reject "\\$e" "\\$e requires module 'assertions'"; done

echo
echo "== backreferences =="
for e in k g; do reject "\\$e" "\\$e requires module 'backrefs'"; done
# ALL TEN digits, by hand. It was `for d in 1 2 8 9`, and R6's testability
# critic used the gap: it deleted the rows for 0,3,4,5,6,7 — chosen precisely
# because those six were covered ONLY by dump iteration — bumped the exact row
# count as registry_check's own failure message invites, re-ran
# compliance_section.py --write as ITS failure message invites, and every suite
# passed. `\3` then reported "unknown escape \3", i.e. pcrec claiming it is not
# a PCRE construct at all. An exact count disarms itself for anyone who follows
# the instructions; a hand-written row does not.
for d in 0 1 2 3 4 5 6 7 8 9; do reject "\\$d" "requires module 'backrefs'"; done

echo
echo "== unicode properties, quoting, misc escapes =="
reject '\p{L}' "\\p requires module 'unicode-props'"
reject '\P{L}' "\\P requires module 'unicode-props'"
reject '\Q'    "\\Q requires module 'quoting'"
reject '\E'    "\\E requires module 'quoting'"
reject '\R'    "\\R requires module 'misc'"
reject '\X'    "\\X requires module 'misc'"
reject '\C'    "\\C requires module 'misc'"
reject '\cA'   "\\c requires module 'misc'"
reject '\o{101}' "\\o requires module 'misc'"

echo
echo "== (?...) constructs =="
reject '(?=a)'    "requires module 'lookaround'"
reject '(?!a)'    "requires module 'lookaround'"
# The three lookbehind TAILS on `<`, split from the named group at Q2/SR-9.
# These read 'lookaround/named-groups' until then — a compound module name that
# was a true sentence and an inexact answer, where D26 makes attribution tier 2.
# Measured over all 256 tails: exactly `=`, `!` and `*` are lookaround and every
# other byte is the named-group path. Hand-written HERE because that is the only
# check of a module NAME — libpcre2 can say the construct exists and can never
# say pcrec should call it 'lookaround'.
reject '(?<=a)'   "requires module 'lookaround'"
reject '(?<!a)'   "requires module 'lookaround'"
reject '(?<*a)'   "requires module 'lookaround'"
reject '(?<n>a)'  "requires module 'named-groups'"
# `(?P` is three constructs and three modules, and answered 'named-groups' for
# all three until Q2 (R8/C4-7, re-derived independently by a spec-first writer).
reject '(?P=n)'   "requires module 'backrefs'"
reject '(?P>n)'   "requires module 'recursion'"
# ...and every other tail after `(?P` is PCRE2 error 141 with its own message,
# which the byte-keyed row promised a module for. Found by the tail sweep this
# step added, not by the plan.
reject '(?PX)'    "unrecognized character after (?P"
# The relative subroutine calls. Both fell to the `(?` catch-all and were called
# 'modifiers'; `(?+N)` and `(?-N)` are the relative spellings of `(?1)`..`(?9)`,
# which this table has always called 'recursion'.
reject '(?+1)'    "requires module 'recursion'"
reject '(a)(?-1)' "requires module 'recursion'"
# `-` is the one byte at this doorway carrying two modules, which is why it has
# ten digit tails AND a bare row rather than a compound name.
reject '(?-i)'    "requires module 'modifiers'"
# The extended character class, the third misattribution: a class with set
# operations, not an option setting.
reject '(?[[a]])' "requires module 'classes'"
reject "(?'n'a)"  "requires module 'named-groups'"
reject '(?P<n>a)' "requires module 'named-groups'"
reject '(?>a)'    "requires module 'atomic-groups'"
reject '(?#c)'    "requires module 'comments'"
# K14's group-doorway instance: callouts are OUT-OF-SCOPE in the survey
# ("revisit only with a concrete customer"), so the row is ROADMAP_NEVER and
# the diagnostic must not promise module 'callouts'.
reject '(?C1)'    "(?C...) is outside pcrec's scope and no module will implement it"
reject '(?|a)'    "requires module 'branch-reset'"
reject '(?(1)a)'  "requires module 'conditionals'"
reject '(?R)'     "requires module 'recursion'"
reject '(?&n)'    "requires module 'recursion'"
# `(?*...)` is the NON-ATOMIC positive lookahead, not an option setting. It was
# answered "requires module 'modifiers'" by the `(?` catch-all until R8/C4-8,
# while pcrec's own verb table already knew `(*napla:...)` and
# docs/pcre2_compliance.md already called it non-atomic lookaround — three
# homes, one disagreeing, which is the `\v` bug's exact shape. Hand-written
# here because the iterated probe reads the module from the same row the parser
# renders from and so cannot see a wrong name.
reject '(?*a)'    "requires module 'lookaround'"
# All ten numeric recursion rows, by hand. Iterating the dump probes them, but
# reads the module name from the same row the parser renders from, so it cannot
# see a wrong name — these nine were the largest block of rows with no
# independent human source (R5 tests critic).
for d in 0 1 2 3 4 5 6 7 8 9; do
    reject "(?$d)" "requires module 'recursion'"
done
# The pattern ENDS at the doorway. `c2 == -1` is also REG_SEL_ANY's value, so
# the lookup lands on the catch-all twice over. Until Q2 that catch-all promised
# module 'modifiers' and this pin read "(??...) requires module 'modifiers'" —
# a module promised for a truncated pattern, with a `??` in it because there was
# no byte to print. The catch-all now agrees with PCRE2 that no construct begins
# here. Both versions REJECT; the difference is the promise, which is tier 2.
reject '(?'       "unrecognized character after (? or (?-"
# THE Q2 ROWS. 217 of the 255 probeable bytes after `(?` were told a pcrec module
# would implement syntax libpcre2 rejects outright (error 111). A sample is
# pinned by hand here because PC-3's generated differential and this table fail
# differently: the differential proves the POPULATION agrees with libpcre2, and
# these prove the SENTENCE, which libpcre2 cannot judge.
reject '(?q)'     "unrecognized character after (? or (?-"
reject '(?Z)'     "unrecognized character after (? or (?-"
reject '(?~)'     "unrecognized character after (? or (?-"
# ...and the same over-promise one level down, which splitting the catch-all
# into eleven option-letter rows did NOT fix: the row is chosen by the first
# byte, so `(?iZ)` still promised 'modifiers' until the doorway read the whole
# option RUN. Found while writing the differential, not before it.
reject '(?iZ)'    "unrecognized character after (? or (?-"
reject '(?-Z)'    "unrecognized character after (? or (?-"
reject '(?i-Z)'   "unrecognized character after (? or (?-"
reject '(?aPP)'   "unrecognized character after (? or (?-"
# The other direction, and the mirror mistake: these ARE option settings PCRE2
# recognises (error 194, "invalid hyphen in option setting"), so refusing them a
# module would be an UNDER-promise. The first version of the run rule got this
# wrong for 24 shapes and the differential refused it.
reject '(?i-m-s)' "requires module 'modifiers'"
reject '(?^-i)'   "requires module 'modifiers'"
reject '(?--D)'   "requires module 'modifiers'"
# `a` takes exactly one ASCII-restrict sub-option, which is invisible to any
# rule derived from single letters: `(?aP)` compiles and `(?aPP)` is error 111.
reject '(?aP)'    "requires module 'modifiers'"
# `(*` used to be answered "requires module 'verbs'" here. Q1 changed it, and
# the change is a correction: PCRE2 reads a bare `(*` as `(` followed by a
# quantifier with nothing to quantify (error 109), and there is no verb name at
# all to route to a module. Pinned as its own row rather than merged with the
# other quantifier rows because THIS one is the doorway declining.
reject '(*'       "quantifier does not follow a repeatable item"
reject '(?i)a'    "requires module 'modifiers'"
reject '(?-i)a'   "requires module 'modifiers'"
reject '(?i:a)'   "requires module 'modifiers'"
reject '(?s)a'    "requires module 'modifiers'"
reject '(?m)a'    "requires module 'modifiers'"
reject '(?x)a'    "requires module 'modifiers'"

echo
echo "== (*...) verbs, option settings and script runs =="
# These used to report "quantifier does not follow a repeatable item", which is
# a clean rejection of something that is not a quantifier — technically correct
# behaviour, useless diagnosis.
#
# THE TWO ROWS BELOW CHANGED THEIR EXPECTED TEXT AT Q1, and the old text was
# the bug. `(*MARKx)` and `(*NOTAVERB)` are not verb names; PCRE2 rejects both
# with "(*VERB) not recognized or malformed", and pcrec used to answer
# "requires module 'verbs'" — promising a module that will never implement them,
# because there is nothing to implement. R6 recorded that the doorway is TWO
# name tables selected by the CASE of the first byte and that nothing here could
# see it. Q1 built the tables; these rows now pin which one answered.
#
# Everything below is hand-written on purpose. tests/registry/pcre2_check.c
# sweeps ~75k generated names against libpcre2 and is a far wider net — but it
# is a net woven from libpcre2's own binary, and if that library is missing it
# SKIPS. These rows are what still holds when it does.
#
# MEASURE THAT CLAIM RATHER THAN BELIEVING IT (R8/C3-F1). A critic deleted verb
# rows one at a time on a box with PC-3 disabled: deleting `F`, `NO_JIT` or
# `scs` fails here, and deleting `LIMIT_HEAP` or `naplb` failed NOTHING. So the
# rows below pin one name per FORM GROUP — there are five — rather than one per
# name, and the honest statement is that the other 26 names are covered by PC-3
# alone. Do not read this block as "the verb tables are pinned".
reject '(*MARKx)'    "(*VERB) not recognized or malformed"
reject '(*NOTAVERB)' "(*VERB) not recognized or malformed"
reject '(*ACCPET)'   "(*VERB) not recognized or malformed"
reject '(*)'         "quantifier does not follow a repeatable item"
# The lower table: PCRE2 picks it by the case of the first byte and says
# something different. `(*accept)` is not `(*ACCEPT)` misspelt — it is a lookup
# in a table that has no ACCEPT.
reject '(*accept)'   "(*alpha_assertion) not recognized"
reject '(*pla)'      "(*alpha_assertion) not recognized"
reject '(*SCRIPT_RUN:a)' "(*VERB) not recognized or malformed"
# Real names in a form PCRE2 does not accept. Each of these is a DIFFERENT rule
# in the table, and each was measured against libpcre2 10.46 rather than read:
reject '(*MARK)'          "(*MARK) must have an argument"   # the one name with its own message
reject '(*:)'             "(*MARK) must have an argument"   # (*:...) is a MARK synonym
reject 'a(*CR)'           "(*VERB) not recognized or malformed"  # options are start-only
reject '(*CR:x)'          "(*VERB) not recognized or malformed"  # ... and take no argument
reject '(*LIMIT_MATCH)'   "(*VERB) not recognized or malformed"  # ... but LIMIT_* needs =n
reject '(*LIMIT_MATCH=x)' "(*VERB) not recognized or malformed"  # ... and n must be digits
reject '(*ACCEPT:x'       "(*VERB) not recognized or malformed"  # a name-run arg needs its ')'
reject '(*ACCEPT'         "(*VERB) not recognized or malformed"
# LEFTMOST ERROR WINS, pinned deliberately rather than left to be rediscovered
# (R8/C2). libpcre2 rejects `(*FAIL)*` with "quantifier does not follow a
# repeatable item" — the verb is real, but PCRE2 will not quantify it — while
# pcrec answers about the construct it met FIRST and never reads the `*`. That
# is pcrec's rule at every doorway, not a verb-doorway defect: `\d{3,1}` is
# "requires module 'classes'" here and "numbers out of order" in PCRE2, and has
# been since the registry existed. Both rows are here so that if anyone ever
# changes it, they change it ON PURPOSE.
reject '(*FAIL)*'         "requires module 'verbs'"
reject '\d{3,1}'          "requires module 'classes'"
# The THIRD leftmost-policy witness, ruled by Frank 2026-08-11 (§18.2 of the
# extension design): `(a)(?(1)x|y|z)` is PCRE2 error 127 — more than two
# branches, PERMANENTLY invalid, a defect module 'conditionals' can never
# repair — and pcrec still answers with the module name, because pcrec reports
# the LEFTMOST construct it cannot handle and does not read a disabled
# construct's body to rank its defects. "This is not an exercise in emulating
# the exact interface of pcre2." The exact E127 becomes part of the
# conditionals module's landing bar instead.
reject '(a)(?(1)x|y|z)'   "requires module 'conditionals'"
# THE TWO BOUNDARIES, both found by the R8 panel and both pinned on BOTH SIDES.
# A boundary row on one side only says a number exists, not where it is.
# `=digits` has a MAGNITUDE rule, not a length one: libpcre2 refuses while
# accumulating, one digit before its 32-bit counter would overflow.
reject '(*LIMIT_MATCH=4294967289)' "is outside pcrec's scope and no module will implement it"
reject '(*LIMIT_MATCH=4294967290)' "(*VERB) not recognized or malformed"
reject '(*LIMIT_MATCH=00000000000000000001)' "is outside pcrec's scope and no module will implement it"
# A verb NAME over 128 bytes is a LENGTH complaint in PCRE2, not a "no such
# name" one, and it is the same complaint from both name tables.
name128="$(printf 'A%.0s' $(seq 1 128))"
name129="$(printf 'A%.0s' $(seq 1 129))"
lname129="$(printf 'a%.0s' $(seq 1 129))"
reject "(*$name128)"  "(*VERB) not recognized or malformed"
reject "(*$name129)"  "subpattern name is too long (maximum 128 code units)"
reject "(*$lname129)" "subpattern name is too long (maximum 128 code units)"

for v in '(*ACCEPT)' '(*FAIL)' '(*F)' '(*ACCEPT:)' '(*CR)' '(*LF)' '(*CRLF)' \
         '(*ANYCRLF)' '(*UTF)' '(*UCP)' '(*NUL)' '(*BSR_UNICODE)' '(*NOTEMPTY)' \
         '(*script_run:a)' '(*sr:a)' '(*atomic:a)' '(*pla:a)' \
         '(*naplb:a)' '(*negative_lookbehind:a)' \
         '(*atomic:)' 'a(*ACCEPT)'; do
    reject "$v" "requires module 'verbs'"
done
# THE K14 FIX (MOD-0.1, 2026-08-11; ruled at design §17.2 / D34 item 1).
# These names are real PCRE2 syntax that pcrec's own compliance survey calls
# OUT-OF-SCOPE — the backtracking verbs (defined in terms of a backtracking
# tree a simulation engine does not have), the LIMIT_* family (they bound a
# backtracking search), the PCRE2-internals knobs, the Unicode-casing options,
# scan-substring, and (?C) callouts. Promising "module 'verbs'" for them was
# K14: naming a module that will never implement a construct, which D26's
# tier-2 row calls a defect in as many words. The disposition is a COLUMN
# (ROADMAP_NEVER, per-row and per-VerbName), the diagnostic names no module,
# and compliance_section.py asserts prose-OUT-OF-SCOPE <=> ROADMAP_NEVER in
# both directions so the survey and the table cannot drift apart. A malformed
# FORM of a NEVER name keeps PCRE2's own form error — the roadmap answer is
# only for constructs PCRE2 would accept ('(*MARK)' bare still gets "must
# have an argument"; 'a(*CR)' still gets the position error).
for v in '(*COMMIT)' '(*PRUNE)' '(*SKIP)' '(*THEN)' '(*MARK:x)' \
         '(*LIMIT_MATCH=1)' '(*LIMIT_HEAP=1)' '(*TURKISH_CASING)' \
         '(*NO_JIT)'; do
    reject "$v" "is outside pcrec's scope and no module will implement it"
done
reject '(*:x)'    "(*MARK) is outside pcrec's scope and no module will implement it"   # the MARK synonym resolves to MARK's row
reject '(*scs:x)' "(*scs) is outside pcrec's scope and no module will implement it"    # lower table carries the column too

# THE FIVE GRADUATED K3/K4 ROWS (FIX-2, 2026-08-10). Each was a `pinned`
# known-wrong line until the fix landed; each is now an ordinary expectation.
# Kept in one block, with its history, because a reader who finds `[[:]]` in a
# reject table deserves to know it was once the opposite.
reject '[:alpha:]' "POSIX class [:...:] is only valid inside a character class"
reject '[::]'      "POSIX class [:...:] is only valid inside a character class"
reject '[:a:]'     "POSIX class [:...:] is only valid inside a character class"
# ...and the OTHER half of the same flag, which was an over-REJECTION: nothing
# closes the pair, so PCRE2 reads ordinary members and so must pcrec.
accept '[a[:b]'
accept '[[:alpha]'
accept '[[:]]'
accept '[[:]'
# `[:]` and `[:a]` belong here too — they are the 4a doorway's accept-controls —
# but they are asserted ONCE, in the doorway-4a section above, with the R5
# FINDING 1 provenance that explains why they exist. FIX-2 added a second copy
# here; a duplicate gives the MANIFEST a spare and inflates the counts (R9/C4-2).
# K4's terminator scan. Every one of these has the `.]` or `=]` OUTSIDE the
# class, which is the shape the old scan could not see.
accept '[.a]x.]'
accept '[=a]x=]'
accept '[a[.b]c]d.]'
accept '[[.a].]'
accept '[.a].]'
# ...and the escape rule, which is why the three had to land together: the `]`
# that ends the scan here is one a backslash was hiding, so a `]`-rule without
# an escape-rule turns this correct rejection into an over-acceptance. The `[.`
# form of that is the rule-3 discriminator eleven lines down and is NOT repeated
# here — it used to be, and the duplicate is what made the MANIFEST's claim
# about it false (R9/C4-2). `[=` is the same statement at the other delimiter.
reject '[a[=b\]=]'  "POSIX collating elements are not supported"
# K4's RULE 3, and these four are the only thing that distinguishes it from the
# two weaker rules I tried first. It is "`\]` and `\\` are units", not "skip any
# `\X`" and not "suppress only a class-ending `]`" — each weaker rule gets one of
# these four wrong, and all four came from PC-3's generated sweep rather than
# from anyone's reading.
reject '[[.\.]]'      "POSIX collating elements are not supported"   # \. is NOT a unit
accept '[[.a\\]x.]'                                                  # \\ IS a unit
reject '[a[.b\].]'    "POSIX collating elements are not supported"   # \] IS a unit
accept '[[.b].]'                                                     # a bare ] ends it
accept '[[.b\]]'
reject '[[:\:]]'      "unknown POSIX class name"
# The two class-bracket constructs that are not classes at all: zero-width word
# boundary assertions. My hand-written list of fourteen names missed both, and
# the generated differential found them on its first run.
reject '[[:<:]]'      "POSIX class [:...:] requires module 'classes'"
reject '[[:>:]]'      "POSIX class [:...:] requires module 'classes'"
reject '[[:^<:]]'     "unknown POSIX class name"   # ^ negates a CLASS; these are not
# A NESTED opener wins: PCRE2 abandons the outer one and recognises the inner.
# THESE THREE PIN THE OFFSET, and that is the whole point of them. Rule 2 of
# K4's scan changes NOTHING about the verdict — with it or without it pcrec
# rejects all three — so it was an INVISIBLE branch, which is the shape R5 and
# R7 both got burned by. What it changes is WHICH CONSTRUCT gets blamed: with
# rule 2 the error points at the inner opener (offset 4), which is the one PCRE2
# recognises; without it, at the outer bracket PCRE2 abandoned (offset 1).
# Deleting rule 2 leaves tests/registry/pcre2_check.c's 1680-pattern sweep at
# zero failures, because that sweep compares VERDICTS. These rows are what sees
# it. (PCRE2 reports offset 9 here — it points at the end. pcrec's convention is
# the construct START and D26 puts the exact number in tier 3; pointing at the
# right construct is the part worth having.)
reject '[[.a[.b.].]'  "POSIX collating elements are not supported (pattern offset 4)"
reject '[a[.b[.c.].]' "POSIX collating elements are not supported (pattern offset 5)"
reject '[[=a[=b=]=]'  "POSIX collating elements are not supported (pattern offset 4)"

echo
echo "== possessive quantifiers =="
reject 'a*+' "possessive quantifier requires module 'atomic-groups'"
reject 'a++' "possessive quantifier requires module 'atomic-groups'"
reject 'a?+' "possessive quantifier requires module 'atomic-groups'"

echo
echo "== base-grammar MISCOMPILES, fixed 2026-08-10 (K5, K6) =="
# The only rows in this file with no registry row behind them, and the reason
# they are here rather than only in the corpus is worth stating: a `.rxt` `perr`
# block asserts a REJECTION, and for these two the REASON is the whole fix.
# Both were the class the charter forbids — a quantifier silently reinterpreted
# as literal text, compiling a matcher for a different language than the pattern
# named, with no diagnostic at all. Being base-grammar errors they carry PCRE2's
# own wording rather than a "requires module" name.
#
# Every verdict below was measured against libpcre2 10.46.

# K5 — a count above 65535 is PCRE2 error 105. The overflow is remembered and
# raised only where try_quant would have succeeded, so it must reach all three
# of its return paths, not just `{m}`.
#
# THESE ROWS PIN THE OFFSET, and that is deliberate: `try_quant` keeps a
# separate end position for each of the two numbers for no other purpose, and
# until 2026-08-10 NOTHING in the repo asserted an error offset at all (R7,
# C2/T-0 — `grep -rn "pattern offset" tests/` returned nothing). Every offset
# below equals the one libpcre2 10.46 reports for the same pattern, so these
# are a conformance claim and not just a change detector. Note which byte each
# one lands on: the first number's end may be a `}` or a `,`, and the second
# number's end is a different variable.
reject 'a{65536}'       "number too big in {m,n} quantifier (pattern offset 7)"
reject 'a{100000}'      "number too big in {m,n} quantifier (pattern offset 8)"
reject 'a{0,65536}'     "number too big in {m,n} quantifier (pattern offset 9)"
reject 'a{65536,}'      "number too big in {m,n} quantifier (pattern offset 7)"
reject 'a{,65536}'      "number too big in {m,n} quantifier (pattern offset 8)"
reject 'a{65535,65536}' "number too big in {m,n} quantifier (pattern offset 13)"
# Too-big beats out-of-order — measured: PCRE2 answers 105 here, not 104. The
# clamped accumulator makes `a{65536,1}` look out-of-order internally, so
# checking in the other order is a live mistake, not a hypothetical one. The
# offset also discriminates: 7 is the FIRST number's end, which is the one that
# overflowed.
reject 'a{65536,1}'     "number too big in {m,n} quantifier (pattern offset 7)"
# Twenty digits. NOTE what this does and does not buy (R7/T-3): it pins the
# OFFSET, which the clamp would otherwise get wrong, and it exercises the same
# too-big path `a{100000}` does. It does NOT test the clamp's actual purpose —
# `big_m` is sticky and ctx_fail fires before `m` is read, so removing the
# clamp changes no observable output at all. The signed-overflow UB it prevents
# is only visible to a UBSan build, which this repo does not have.
reject 'a{99999999999999999999}' "number too big in {m,n} quantifier (pattern offset 22)"

# K6 — a well-formed quantifier with nothing to quantify is PCRE2 error 109.
# `*`, `+` and `?` were always rejected in this position; `{` was not, because
# try_quant is only reached from p_rep, AFTER an atom.
#
# The offsets are pinned here too, and they carry a claim of their own: PCRE2
# reports the CLOSING BRACE, which is exactly where try_quant leaves the cursor,
# so `cx->pos - 1` is a conformance decision rather than a convenience. Each
# value below matches libpcre2 10.46 on the same pattern.
reject '{1}'      "quantifier does not follow a repeatable item (pattern offset 2)"
reject '{2,3}'    "quantifier does not follow a repeatable item (pattern offset 4)"
reject '{,5}'     "quantifier does not follow a repeatable item (pattern offset 3)"
reject '{1,}'     "quantifier does not follow a repeatable item (pattern offset 3)"
reject '{0}'      "quantifier does not follow a repeatable item (pattern offset 2)"
reject '{1}a'     "quantifier does not follow a repeatable item (pattern offset 2)"
reject 'a|{1}'    "quantifier does not follow a repeatable item (pattern offset 4)"
reject '({1})'    "quantifier does not follow a repeatable item (pattern offset 3)"
reject '(?:{1})'  "quantifier does not follow a repeatable item (pattern offset 5)"
reject '{1}{2}'   "quantifier does not follow a repeatable item (pattern offset 2)"
# The ORDER between the three brace diagnostics in atom position, which is also
# measured: PCRE2 answers 105 for a too-big count and 104 for an out-of-order
# pair, NOT 109. A fix that asked "is anything repeatable" first would pass
# every K6 row above and get both of these wrong.
reject '{65536}'  "number too big in {m,n} quantifier (pattern offset 6)"
# K8 (found by R7's spec critic, fixed in the same checkpoint) — PCRE2 skips
# SPACE and TAB in each of the four gaps inside `{...}`, so both rules above
# have to see THROUGH the whitespace. These rows also pin the offsets, which is
# where the subtlety lives: PCRE2 reports where the DIGITS ran out, so trailing
# whitespace does not move it (`a{65536 }` is offset 7, the space itself) while
# leading whitespace does (`a{ 65536}` is offset 8, the `}`).
reject 'a{ 65536}' "number too big in {m,n} quantifier (pattern offset 8)"
reject 'a{65536 }' "number too big in {m,n} quantifier (pattern offset 7)"
reject '{ 65536}'  "number too big in {m,n} quantifier (pattern offset 7)"
reject '{ 1}'      "quantifier does not follow a repeatable item (pattern offset 3)"
reject 'a{3, 1}'   "numbers out of order in {m,n} quantifier (pattern offset 6)"
# the p_rep path takes the same offset, and it is pre-existing code
reject 'a{3,1}'    "numbers out of order in {m,n} quantifier (pattern offset 5)"
reject 'ab{5,2}'   "numbers out of order in {m,n} quantifier (pattern offset 6)"
# Out-of-order reported the `{` until R7 (offset 0 here) where PCRE2 reports
# the `}`. It was the only one of the three brace diagnostics whose offset
# disagreed, and two critics flagged it independently; aligned deliberately.
reject '{3,1}'    "numbers out of order in {m,n} quantifier (pattern offset 4)"
# FIX-3 (K13, 2026-08-11) — the in-class octal escape's 8-bit ceiling. With the
# twelve class-position fallbacks implemented ([\1] is octal, [\8] [\9] [\g]
# [\k] are literals — the accept side lives in
# tests/base/class_escape_fallbacks.rxt, 127 oracle-verified cases), the class
# decoder gained the first NEW base-grammar diagnostic since K8: a consumed
# octal value above \377 cannot be a byte. PCRE2 error 151, wording AND offset
# reproduced — the offset is where the digits ran out, measured on both cells
# by tests/probes/probe_fix3.c. The boundary is pinned on BOTH sides, per the
# K5 lesson (a boundary row on one side says a number exists, not where it
# is): \377 is the largest legal value, so an off-by-one in the ceiling flips
# the accept-control, and the .rxt perr blocks beside these assert only THAT
# [\400] fails — this is the only home for the message.
reject '[\400]' "octal value is greater than \377 in 8-bit non-UTF-8 mode (pattern offset 5)"
reject '[\777]' "octal value is greater than \377 in 8-bit non-UTF-8 mode (pattern offset 5)"
accept '[\377]'

echo
echo "== KNOWN-WRONG, pinned so a change is VISIBLE (K3, K4) =="
# These assert what pcrec does TODAY, and what it does today is WRONG. They are
# not certifications — each line records a measured disagreement with libpcre2
# 10.46 that is deliberately unfixed, so that changing it produces a signal
# instead of silence.
#
# WHY THIS EXISTS. tests/known_fail/ is the project's ratchet for deferred bugs,
# and it structurally cannot hold any of these: a `.rxt` `perr` block requires
# the PYTHON oracle to fail too, and python `re` accepts every pattern below.
# That is the same blindness that let the bugs exist (R5 F-4).
#
# WHAT IT BUYS. An R5 critic replaced the `RF_CLASS_DELIM` flag test with `if
# (1)` — a one-token edit that FIXES K3 and the `[a[:b]` half of it, moving
# pcrec strictly closer to PCRE2 — and all seven suites stayed green. The suite
# could not tell K3-fixed from K3-unfixed in either direction. Now it can.
#
# WHEN YOU FIX K3/K4: these lines must move to the normal accept/reject tables
# above, in the same commit. A failure here means "you changed the behaviour" —
# check it against libpcre2, then move the line. It does not mean "you broke
# something".
nwrong=0
pinned() { # pinned <pattern> <accept|reject> <expected-msg-or-dash> <why it is wrong>
    local pat="$1" want="$2" msg="$3" why="$4" rc out
    nwrong=$((nwrong + 1))
    out="$(timeout 60 "$PCREC" -p rx -o "$WORKDIR/kw.c" -- "$pat" 2>&1 >/dev/null)"; rc=$?
    if { [ "$want" = accept ] && [ "$rc" -eq 0 ]; } || \
       { [ "$want" = reject ] && [ "$rc" -eq 1 ]; }; then
        # verdict pinned; also pin the MESSAGE where one was given. A
        # verdict-only pin says something moved, not that it moved somewhere
        # right (R6 testability critic, T-9).
        case "$msg" in
            *[![:space:]]*) ;;
            *) bad "known-wrong '$pat': blank expected message. Use '-' to pin the VERDICT only and say so, or name the diagnostic — a blank string matches any output (R9/C4-1, C4V-2)"
               return ;;
        esac
        if [ "$msg" != "-" ]; then
            case "$out" in
                *"$msg"*) ;;
                *) bad "known-wrong '$pat': verdict unchanged but the DIAGNOSTIC changed. want: $msg ; got: $out"
                   return ;;
            esac
        fi
        seen="$seen
$pat"
        ok "known-wrong '$pat' still ${want}s — $why"
    else
        bad "known-wrong '$pat': behaviour CHANGED (expected to $want, rc=$rc). $why. If you fixed K3/K4, move this line into the tables above; if not, you have regressed something"
    fi
}
# EMPTY, and that is the point: all five lines that stood here were K3 and K4,
# and FIX-2 (2026-08-10) fixed both. Each one fired on the way past — "behaviour
# CHANGED... if you fixed K3/K4, move this line into the tables above" — which
# is the mechanism working exactly as designed, and each has moved into the
# normal accept/reject tables where it is now an ordinary expectation rather
# than a pinned defect.
#
# Keep this block and its helper. A known-wrong pin is how this project records
# a defect it has decided not to fix yet WITHOUT letting the defect become
# invisible, and the next one will want the same machinery. The helper is
# validated by the five that just graduated.

echo
echo "== every registry row covers itself (SR-4) =="
# Iterate `pcrec --list-syntax` and probe EVERY non-base row with its own
# `syntax` field. This is the half of SR-4 that makes the table load-bearing:
# a construct added to src/parse/registry.c is tested here the moment its row
# exists, with no edit to this file, so coverage cannot lag the table.
#
# WHAT THIS CANNOT DO, and why the hand-written rows above are still here.
# SR-4's plan text said to iterate the dump INSTEAD of them. That trade was not
# taken, because it gives away the property that matters most. Since SR-2 the
# module names live in exactly ONE place — the registry — and the parser renders
# its diagnostics from it. A test that reads the same table and asks "does the
# diagnostic match the table" therefore cannot see a WRONG module name: change
# `\d`'s row from `classes` to `misc` and the parser and this loop agree
# perfectly, in unison, about the wrong answer.
#
# The hand-written rows are a SECOND, HUMAN source for that name. That is the
# same rule the accept-controls follow and the same lesson the trie-identity
# check learned: a control must not share a source with the thing it controls.
# So the two layers do different jobs — iteration guarantees COVERAGE (no row
# escapes a probe), the hand-written table guarantees CORRECTNESS (the name a
# caller is given is one a human wrote down independently). Neither subsumes
# the other, and the maintenance cost of the second one IS the check.
#
# Three things iteration structurally cannot reach, which is the R4 warning
# restated with its consequence: `\x{...}` and the possessive `+` have NO row
# (they are sub-cases of base constructs, deliberately — see D24), and the
# in-class spelling of an escape (`[\d]`) is a different diagnostic from the
# atom spelling that the `syntax` field probes. All three are covered above,
# by hand, and iteration must never be read as covering them.
niter=0
row_reject() { # like reject(), but counted separately so the floors stay honest
    local pat="$1" want="$2" out rc
    # Same empty-expectation trap as reject() (R9/C4-1). The BADROW filter below
    # already drops dump rows with an empty `expect` field, so this is the
    # second line rather than the first — but it is the line that survives
    # someone rewriting the awk.
    case "$want" in
        *[![:space:]]*) ;;
        *) bad "row '$pat': blank 'expect' text reached row_reject — it would match any output (R9/C4V-2)"
           return ;;
    esac
    niter=$((niter + 1))
    rm -f "$WORKDIR/out.c" "$WORKDIR/out.h"
    out="$(timeout 60 "$PCREC" -p rx -o "$WORKDIR/out.c" -- "$pat" 2>&1 >/dev/null)"; rc=$?
    if [ "$rc" -ne 1 ]; then
        bad "row '$pat': exit $rc, not a clean exit-1 rejection"
        return
    fi
    case "$out" in
        *"$want"*) ;;
        *) bad "row '$pat': diagnostic does not contain the dump's own 'expect' text. want: $want ; got: $out"
           return ;;
    esac
    if [ -f "$WORKDIR/out.c" ] || [ -f "$WORKDIR/out.h" ]; then
        bad "row '$pat': rejected but still wrote an output file"
        return
    fi
    ok "row '$pat' -> $want"
}

"$PCREC" --list-syntax > "$WORKDIR/syntax.tsv" 2>"$WORKDIR/syntax.err"
if [ ! -s "$WORKDIR/syntax.tsv" ]; then
    bad "--list-syntax produced no dump ($(cat "$WORKDIR/syntax.err")) — every check below would pass vacuously"
else
    # Field extraction goes through awk, NOT `IFS=$'\t' read -r a b c...`.
    # Tab is IFS *whitespace*, so bash collapses runs of it and strips leading
    # and trailing ones: any row with an empty field shifts every column after
    # it, and the loop then compares the wrong strings while still reporting
    # PASS/FAIL as though it were working. That is precisely how this section
    # first "ran" — it read each row's `note` as its `expect` and iterated the
    # one base row it was supposed to skip.
    #
    # Two columns are enough, and neither may be empty. A row whose `syntax` or
    # `expect` is blank is reported as a bad row rather than silently probed
    # with an empty pattern or matched against an empty substring — the latter
    # matches ANY diagnostic and would pass while testing nothing.
    awk -F'\t' '
        /^#/ || NF != 15 || $8 == "base" { next }
        $3 == "" || $11 == "" { print "BADROW\t" $0 > "/dev/stderr"; next }
        { print $3 "\t" $11 }
    ' "$WORKDIR/syntax.tsv" 2>"$WORKDIR/badrows.txt" > "$WORKDIR/probe.tsv"

    if [ -s "$WORKDIR/badrows.txt" ]; then
        bad "dump rows with an empty syntax or expect field: $(wc -l < "$WORKDIR/badrows.txt")"
        cat "$WORKDIR/badrows.txt" >&2
    fi

    while IFS=$'\t' read -r syntax expect; do
        row_reject "$syntax" "$expect"
    done < "$WORKDIR/probe.tsv"

    # The loop must have seen every non-base row: a `read` that silently stops
    # early would make this whole section quietly shrink to nothing.
    nexpected=$(awk -F'\t' '!/^#/ && NF == 15 && $8 != "base"' "$WORKDIR/syntax.tsv" | wc -l)
    # `-eq 66`, not `-ge 60`: the floor had six rows of slack, and R6 measured
    # what slack buys — see the summary block below.
    # 67 -> 99 at Q2/SR-9 (100 rows, of which `(?:` is the one base row).
    if [ "$niter" -eq "$nexpected" ] && [ "$niter" -eq 99 ]; then
        ok "iterated every non-base row in the dump ($niter)"
    else
        bad "iterated $niter rows, dump has $nexpected non-base rows (floor 60) — the iteration is not covering the table"
    fi
fi

echo
echo "== Summary =="
echo "rejections checked: $nrej"
echo "rows iterated:      $niter"
echo "accept controls:    $naccept"
echo "known-wrong pinned: $nwrong"
echo "checks passed: $pass"
echo "checks failed: $fail"
# EXACT counts, not floors. These were `-lt 90` and `-lt 18` against 93 and 19
# actual, and an R5 critic showed what three checks of slack buys an attacker:
# delete `\R`, `\X` and `\C`, then change `\R`'s registry row from 'misc' to
# 'classes', and pcrec tells the caller to enable the WRONG module — the one
# fact the diagnostic exists to carry — with all seven suites green. The
# registry conformance check cannot object because since SR-2 both sides read
# the same row, and the feature/module bijection stays consistent.
#
# A floor guards a COUNT; the thing worth guarding is a SET.
#
# THE COUNT ALONE IS NOT ENOUGH, and R7/T-7 measured exactly how it fails. A
# critic moved the 65535 ceiling to 65534 — rejecting every legal count at the
# documented boundary — then deleted the single row that caught it and bumped
# the expected count by one, which is what THIS FILE'S OWN FAILURE MESSAGE
# invites. `make test` went green in a two-line diff. The count made the
# deletion visible in the diff; it did not make it fail. That is the same
# "exact counts disarm themselves" hazard R6 recorded, and a number cannot fix
# it because the number is what the attacker is told to edit.
#
# So the rows whose absence would be silent are named HERE, by pattern. A
# manifest is not a count: deleting the row makes this fail, and the failure
# message does not tell you to edit a number. Keep it short — it is for rows
# that are the ONLY check of something, not for coverage in general.
# AND THE MANIFEST ASSUMES EVERY ROW IS UNIQUE, so enforce that rather than
# assume it. `seen` is a flat log of every pattern that passed ANY check, and
# `must_have` only asks whether a pattern appears in it — so a row that is
# written TWICE has a spare. Delete either copy and the manifest still finds the
# other, which is precisely the "delete the row, bump the count" attack the
# manifest exists to defeat, with the count edit made unnecessary.
#
# Measured: `[a[.b\].]` was written twice, and it was the ONLY duplicated
# pattern in this file. A critic deleted one copy, bumped the exact count 201 →
# 200 exactly as the failure message below forbids, and the suite went green
# with one of the two witnesses for K4's rule 3 physically gone (R9/C4-2).
#
# A pattern cannot legitimately appear twice: it is either accepted or rejected,
# never both, and asserting the same thing twice also inflates the exact counts.
dupes="$(printf '%s\n' "$seen" | sed '/^$/d' | LC_ALL=C sort | LC_ALL=C uniq -d)"
if [ -n "$dupes" ]; then
    while IFS= read -r d; do
        [ -z "$d" ] && continue
        bad "duplicate row: '$d' is asserted more than once. A duplicated row gives the MANIFEST a spare copy, so deleting the real check goes undetected — and it inflates the exact counts. Keep one."
    done <<DUPES
$dupes
DUPES
else
    ok "no pattern is asserted twice (the MANIFEST's uniqueness assumption holds)"
fi

manifest_missing=0
must_have() { # must_have <pattern> <why it is irreplaceable>
    # Match a WHOLE recorded line, not a substring. `[:alpha:]` is a substring
    # of the unrelated row `[[:alpha:]]`, so a substring test would have made
    # this entry silently vacuous — the exact failure mode the manifest exists
    # to prevent, found while writing it.
    case "
$seen
" in
        *"
$1
"*) ;;
        *) echo "reject: MANIFEST — no check exercised '$1'." >&2
           echo "reject:   why it must exist: $2" >&2
           echo "reject:   do NOT satisfy this by editing a count; restore the row." >&2
           manifest_missing=1 ;;
    esac
}
must_have '(?:){65535}' \
    "the only check in the repo that sees an off-by-one in K5's 65535 ceiling"
must_have 'a{1,65536x}' \
    "the only check of the big_n half of K5's over-reach guard (R7/T-5)"
must_have 'a{65536x}' \
    "the big_m half of the same guard"
must_have '[:alpha:]' \
    "K3's over-ACCEPTANCE: pcrec compiled this into a matcher for {: a l p h}"
must_have '[a[:b]' \
    "K3's over-REJECTION, the same missing flag from the other side"
must_have '[\N]' \
    "R9/SPEC-classes-F1: the in-class position of a REAL construct that PCRE2 forbids there permanently. Without it, promising module 'classes' for [\\N] returns unnoticed"
must_have '[0-[:digit:]]' \
    "R9/SPEC-FA: a class construct as a range ENDPOINT is PCRE2 error 150, and pcrec emitted a matcher for it. The only reject row for a tier-1 miscompile found by spec-first testing"
must_have '[0-[:digit]' \
    "R9/SPEC-FA: the accept side of the same rule — the test is whether the PAIR CLOSES, not whether the byte is '['. Without this the fix could over-reject every '[' endpoint and nothing would notice"
must_have '[a[.b\].]' \
    "the ONLY row where K4's escape rule is load-bearing; without it this flips to over-acceptance"
must_have '[a[.b]c]d.]' \
    "K4's sharpest case: the '.]' matched sits outside the class that closed before it"
must_have '[[.a[.b.].]' \
    "the ONLY check of K4's nested-opener rule; it is invisible to every verdict-level sweep"
must_have '[[:AlPhA:]]' \
    "the only pin that the 14 POSIX class names are CASE-SENSITIVE"
must_have '[:foo:]' \
    "the only pin that POSITION beats NAME: wrong place is reported before unknown name"
must_have '[[.a\\]x.]' \
    "the ONLY case that rules out 'suppress only a class-ending ]' for K4 rule 3"
must_have '[[.\.]]' \
    "the ONLY case that rules out 'skip any \\X' for K4 rule 3"
must_have '[[:<:]]' \
    "a class-bracket construct that is a word-boundary ASSERTION, not a class"
must_have 'a{2,3,4}' \
    "the only malformed-brace control with a SECOND comma"
# Q1's outcomes. Each of these five is the ONLY hand-written check of one rule,
# and all five are answered far more broadly by tests/registry/pcre2_check.c —
# which SKIPS without libpcre2 installed. That is exactly when a manifest earns
# its keep: it names what stops being covered on a box the wide net cannot run.
must_have '(*NOTAVERB)' \
    "the only pin that a name PCRE2 does not have is NOT promised a module (Q1)"
must_have '(*accept)' \
    "the only pin of the LOWER verb table — the case of the first byte picks it"
must_have '(*MARK)' \
    "the only pin of a verb name carrying its own message rather than the generic one"
must_have 'a(*CR)' \
    "the only pin that a start-of-pattern option is invalid away from the start"
must_have '(*)' \
    "the only pin that an empty verb name is a quantifier error, not a verb"
must_have '(*FAIL)*' \
    "the only pin that pcrec reports the LEFTMOST error, where libpcre2 reports a later one"
must_have '(a)(?(1)x|y|z)' \
    "the leftmost policy RULED (2026-08-11, design §18.2): a permanently-invalid body (PCRE2 E127) behind a disabled doorway still gets the module answer; exact E127 is the conditionals module's landing bar"
must_have '(*LIMIT_MATCH=4294967290)' \
    "the only pin of the =digits MAGNITUDE boundary; 4294967289 beside it is the control"
must_have '\U' \
    "representative of the five rowless REAL escapes (\\U \\u \\F \\L \\l) the extension design §7.1 plans to give rows — their fall-through wording is otherwise the project's only unguarded diagnostic surface (R11 disposition 14, A1)"
must_have '[\400]' \
    "the only pin of the in-class octal \\377 ceiling's DIAGNOSTIC (FIX-3/K13) — the .rxt perr beside it asserts only that the pattern fails, and '[\\377]' is its accept-side boundary control"
must_have '(*scs:x)' \
    "the only pin that the LOWER verb table carries the ROADMAP_NEVER column too (K14) — every other NEVER pin is an upper-table name"
must_have '(?C1)' \
    "the only pin of ROADMAP_NEVER at the GROUP doorway (K14) — deleting it leaves the callouts row free to resume promising its module"
if [ "$manifest_missing" -ne 0 ]; then
    echo "reject: one or more irreplaceable checks are gone — see above" >&2
    exit 1
fi

# Exact numbers do not give you the set either, but they make every deletion
# deliberate and visible in the diff, which is what the slack removed. If you
# added or removed coverage on purpose, update these three numbers in the same
# commit — and check first whether the row belongs in the manifest above.
#
# 201 → 200 and 59 → 57 on 2026-08-10 (R9/C4-2), and this is the one kind of
# count edit that is legitimate: three rows were DUPLICATES, not coverage.
# `[a[.b\].]`, `[:]` and `[:a]` were each asserted twice, so those three checks
# were counted twice while testing nothing extra — and the spare copy is what
# made the MANIFEST unable to notice the real row being deleted. The duplicate
# detector above now fails if it happens again, which is what makes lowering
# these numbers safe rather than the very move this file warns about.
if [ "$nrej" -ne 248 ] || [ "$naccept" -ne 63 ] || [ "$nwrong" -ne 0 ]; then
    echo "reject: COVERAGE CHANGED — $nrej rejections / $naccept controls / $nwrong known-wrong, expected 248 / 63 / 0." >&2
    echo "reject: if that was deliberate, update the expected counts in this file's summary block; if not, coverage was removed" >&2
    exit 1
fi
[ "$fail" -eq 0 ] && exit 0
exit 1
