#!/usr/bin/env bash
# tests/reject/run_reject_tests.sh — the mandate's central guarantee, tested.
#
# WHY THIS EXISTS. The project rule is that a construct outside the base tier
# must "fail with a clean 'requires module X' error, never miscompile". Until
# this file, NOTHING checked that. The .rxt corpus cannot: a `perr` block
# requires the python oracle to ALSO fail to compile the pattern, and python
# happily compiles `\d`, `\b`, `(?i)` and most of the rest — so every
# module-routed construct was untestable there, and `# pcre2-only` does not
# help because verify_rxt.py's perr branch does not consult it.
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
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

nrej=0
reject() { # reject <pattern> <expected-substring>
    local pat="$1" want="$2" out rc
    nrej=$((nrej + 1))
    rm -f "$WORKDIR/out.c" "$WORKDIR/out.h"
    out="$("$PCREC" -p rx -o "$WORKDIR/out.c" -- "$pat" 2>&1 >/dev/null)"; rc=$?
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
    ok "reject '$pat' -> $want"
}

naccept=0
accept() { # accept <pattern>   — the control: the table must not pass by rejecting everything
    local pat="$1" out rc
    naccept=$((naccept + 1))
    out="$("$PCREC" -p rx -o "$WORKDIR/ok.c" -- "$pat" 2>&1 >/dev/null)"; rc=$?
    if [ "$rc" -eq 0 ]; then
        ok "accept '$pat' (base tier still compiles)"
    else
        bad "accept '$pat': base-tier construct was REJECTED ($out) — the reject table has swallowed supported syntax"
    fi
}

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

echo
echo "== character-type escapes -> module 'classes' =="
for e in d D s S w W h H v V N; do
    reject "\\$e"     "\\$e requires module 'classes'"
    reject "[\\$e]"   "\\$e in a class requires module 'classes'"
done
reject '[[:alpha:]]' "POSIX class [:...:] requires module 'classes'"
# Names PCRE2 does not know. It rejects all three ("unknown POSIX class name")
# and so do we, so the VERDICT agrees and only the wording differs — but nothing
# covered them, and they are exactly the rows a name-keyed table would have to
# get right (R6 fidelity critic F13: the list is 14 names and case-sensitive).
reject '[[:foo:]]'   "POSIX class [:...:] requires module 'classes'"
reject '[[::]]'      "POSIX class [:...:] requires module 'classes'"
reject '[[:AlPhA:]]' "POSIX class [:...:] requires module 'classes'"
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
# libpcre2 10.46 as well — deliberately not `[::]` or `[:a:]`, which PCRE2
# REJECTS and pcrec wrongly accepts (K3); pinning those would cement the bug.
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

echo
echo "== assertions =="
for e in b A Z z G K; do reject "\\$e" "\\$e requires module 'assertions'"; done

echo
echo "== backreferences =="
for e in k g; do reject "\\$e" "\\$e requires module 'backrefs'"; done
for d in 1 2 8 9; do reject "\\$d" "requires module 'backrefs'"; done

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
reject '(?<=a)'   "requires module 'lookaround/named-groups'"
reject '(?<!a)'   "requires module 'lookaround/named-groups'"
reject "(?'n'a)"  "requires module 'named-groups'"
reject '(?P<n>a)' "requires module 'named-groups'"
reject '(?>a)'    "requires module 'atomic-groups'"
reject '(?#c)'    "requires module 'comments'"
reject '(?C1)'    "requires module 'callouts'"
reject '(?|a)'    "requires module 'branch-reset'"
reject '(?(1)a)'  "requires module 'conditionals'"
reject '(?R)'     "requires module 'recursion'"
reject '(?&n)'    "requires module 'recursion'"
# All ten numeric recursion rows, by hand. Iterating the dump probes them, but
# reads the module name from the same row the parser renders from, so it cannot
# see a wrong name — these nine were the largest block of rows with no
# independent human source (R5 tests critic).
for d in 0 1 2 3 4 5 6 7 8 9; do
    reject "(?$d)" "requires module 'recursion'"
done
# The pattern ENDS at the doorway. `c2 == -1` is also REG_SEL_ANY's value, so
# the lookup lands on the catch-all twice over, and parse.c has always printed
# '?' for the missing byte. Nothing covered this before R5.
reject '(?'       "(??...) requires module 'modifiers'"
reject '(*'       "requires module 'verbs'"
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
# Not verb names at all. PCRE2 rejects both ("(*VERB) not recognized or
# malformed"); pcrec rejects them through the catch-all row. R6 measured that
# the verb doorway is TWO name tables selected by the CASE of the first byte,
# which nothing here can see — these at least pin the verdict.
reject '(*MARKx)'    "requires module 'verbs'"
reject '(*NOTAVERB)' "requires module 'verbs'"

for v in '(*ACCEPT)' '(*FAIL)' '(*F)' '(*COMMIT)' '(*PRUNE)' '(*SKIP)' '(*THEN)' \
         '(*MARK:x)' '(*CR)' '(*LF)' '(*CRLF)' '(*ANYCRLF)' '(*UTF)' '(*UCP)' \
         '(*script_run:a)' '(*sr:a)' '(*atomic:a)'; do
    reject "$v" "requires module 'verbs'"
done

echo
echo "== possessive quantifiers =="
reject 'a*+' "possessive quantifier requires module 'atomic-groups'"
reject 'a++' "possessive quantifier requires module 'atomic-groups'"
reject 'a?+' "possessive quantifier requires module 'atomic-groups'"

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
    out="$("$PCREC" -p rx -o "$WORKDIR/kw.c" -- "$pat" 2>&1 >/dev/null)"; rc=$?
    if { [ "$want" = accept ] && [ "$rc" -eq 0 ]; } || \
       { [ "$want" = reject ] && [ "$rc" -eq 1 ]; }; then
        # verdict pinned; also pin the MESSAGE where one was given. A
        # verdict-only pin says something moved, not that it moved somewhere
        # right (R6 testability critic, T-9).
        if [ "$msg" != "-" ]; then
            case "$out" in
                *"$msg"*) ;;
                *) bad "known-wrong '$pat': verdict unchanged but the DIAGNOSTIC changed. want: $msg ; got: $out"
                   return ;;
            esac
        fi
        ok "known-wrong '$pat' still ${want}s — $why"
    else
        bad "known-wrong '$pat': behaviour CHANGED (expected to $want, rc=$rc). $why. If you fixed K3/K4, move this line into the tables above; if not, you have regressed something"
    fi
}
# K3 — over-acceptance. PCRE2: "POSIX named classes are supported only within a
# class". pcrec compiles it as a five-character class.
pinned '[:alpha:]' accept - \
    "PCRE2 REJECTS it; the ':' row lacks the class-open half of RF_CLASS_DELIM"
# K3 — over-rejection, the same missing row flag seen from the other side.
pinned '[a[:b]'    reject "POSIX class [:...:] requires module 'classes'" \
    "PCRE2 ACCEPTS it; ':' fires without checking for a later ':]'"
pinned '[[:alpha]' reject "POSIX class [:...:] requires module 'classes'" \
    "PCRE2 ACCEPTS it; same missing terminator condition"
# Found 2026-08-10 while adding R6's cheap pins: same family, previously
# unrecorded. `[[:]]` has no ':]' terminator, so PCRE2 reads '[' and ':' as
# ordinary class members and compiles it.
pinned '[[:]]'     reject "POSIX class [:...:] requires module 'classes'" \
    "PCRE2 ACCEPTS it; no ':]' terminator, so the '[:' is ordinary members"
# K4 — the terminator scan runs to the end of the PATTERN, not the class.
pinned '[.a]x.]'   reject "POSIX collating elements are not supported" \
    "PCRE2 ACCEPTS it; the '.]' matched is outside the class"

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
    niter=$((niter + 1))
    rm -f "$WORKDIR/out.c" "$WORKDIR/out.h"
    out="$("$PCREC" -p rx -o "$WORKDIR/out.c" -- "$pat" 2>&1 >/dev/null)"; rc=$?
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
        /^#/ || NF != 12 || $8 == "base" { next }
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
    nexpected=$(awk -F'\t' '!/^#/ && NF == 12 && $8 != "base"' "$WORKDIR/syntax.tsv" | wc -l)
    # `-eq 66`, not `-ge 60`: the floor had six rows of slack, and R6 measured
    # what slack buys — see the summary block below.
    if [ "$niter" -eq "$nexpected" ] && [ "$niter" -eq 66 ]; then
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
# A floor guards a COUNT; the thing worth guarding is a SET. Exact numbers do
# not give you the set either, but they make every deletion deliberate and
# visible in the diff, which is what the slack removed. If you added or removed
# coverage on purpose, update these three numbers in the same commit.
if [ "$nrej" -ne 111 ] || [ "$naccept" -ne 22 ] || [ "$nwrong" -ne 5 ]; then
    echo "reject: COVERAGE CHANGED — $nrej rejections / $naccept controls / $nwrong known-wrong, expected 111 / 22 / 5." >&2
    echo "reject: if that was deliberate, update the expected counts in this file's summary block; if not, coverage was removed" >&2
    exit 1
fi
[ "$fail" -eq 0 ] && exit 0
exit 1
