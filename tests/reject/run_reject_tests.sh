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
reject '(?1)'     "requires module 'recursion'"
reject '(?&n)'    "requires module 'recursion'"
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
echo "== Summary =="
echo "rejections checked: $nrej"
echo "accept controls:    $naccept"
echo "checks passed: $pass"
echo "checks failed: $fail"
if [ "$nrej" -lt 90 ] || [ "$naccept" -lt 18 ]; then
    echo "reject: TABLE SHRANK — $nrej rejections / $naccept controls is below the floor; coverage was removed" >&2
    exit 1
fi
[ "$fail" -eq 0 ] && exit 0
exit 1
