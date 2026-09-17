#!/usr/bin/env bash
# tests/codegen/run_comment_escape.sh -- pcrec-bench O-31 finding F1: a
# pattern whose own bytes contain a comment-closing STAR THEN SLASH must
# not corrupt the emitted C. The DFA emitter's per-state "shortest input"
# legend (src/gen/emit_dfa.c's emit_state_legend) wrote a byte-class
# representative straight into a `/* ... */` block comment with no check
# for the comment-closing sequence, so a WAF rule whose own text is the
# literal SQL-comment-obfuscation bytes that open then close a comment with
# only "!" between (id wild-waf-crs-942500-comment-obfuscation in
# pcrec-bench's bench/capability/patterns.rxt) corrupted the artifact from
# that point on -- a missing terminating string quote cascading into
# undeclared-identifier errors, a genuine C COMPILE FAILURE.
#
# A SECOND, RELATED HAZARD surfaced while building this regression net: a
# SLASH THEN STAR embedded in a pattern's bytes trips gcc's `-Wcomment`
# (it looks like an attempted nested comment), and the harness's own
# GENCFLAGS default IS `-Wall -Wextra -Werror` (tests/harness/run.sh),
# so that warning is exactly as fatal to a real build as the first
# hazard's missing terminator -- on a pattern that never trips the first
# hazard at all. This script's checks use that same default.
#
# THE FIX is `emit_comment_safe_byte` (src/gen/emit_dfa.c), the one shared
# primitive every comment site writing pattern-derived text now goes
# through: printable ASCII passes through unless doing so would complete
# either ordering of the pair with the byte just rendered, in which case
# (like every other non-printable byte) it becomes a fixed `\xNN`.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # pcrec_run bounds every call below

pass=0; fail=0
ok()  { printf 'PASS: %s\n' "$1"; pass=$((pass+1)); }
bad() { printf 'FAIL: %s\n' "$1"; fail=$((fail+1)); }
GENCFLAGS_TEST="-Wall -Wextra -Werror -O1"   # tests/harness/run.sh's own default

# The pattern's raw bytes, once PCRE-parsed, are the literal six bytes
# `/*!*/ ` -- the WAF witness's own SQL-comment-obfuscation spelling,
# every metacharacter escaped so the byte sequence survives into the
# compiled machine's state-legend example untouched.
WITNESS='a\/\*!\*\/b'
# A SLASH-STAR with nothing later to close it: isolates the SECOND hazard
# (-Wcomment) from the first, which this witness alone cannot trip.
OPENONLY='a\/\*b'

# --- 0. baseline: a hazard-free pattern compiles fine (sanity) -------------
if pcrec_run "$PCREC" -p rx --engine=dfa -o "$WORK/base.c" -- 'abc' >"$WORK/base.log" 2>&1 \
   && "$CC" $GENCFLAGS_TEST -c -o "$WORK/base.o" "$WORK/base.c" 2>"$WORK/base.cc.err"; then
    ok "baseline: a hazard-free pattern compiles cleanly (sanity)"
else
    bad "baseline: hazard-free pattern failed to compile: $(cat "$WORK/base.log" "$WORK/base.cc.err" 2>/dev/null | head -5)"
fi

# --- 1. THE F1 WITNESS compiles as a DFA artifact ---------------------------
if pcrec_run "$PCREC" -p rx --engine=dfa -o "$WORK/waf.c" -- "$WITNESS" >"$WORK/waf.log" 2>&1; then
    ok "F1 witness '$WITNESS' compiles (pcrec itself accepts the pattern)"
else
    bad "F1 witness '$WITNESS' failed at pcrec: $(cat "$WORK/waf.log")"
fi

# --- 2. NON-VACUITY: the hazard bytes actually reached the state legend ----
# `d->rep[]` for the class covering `*` renders "*" literally (it is not
# itself a comment hazard); the very next class in the shortest-input walk
# is `/`, which -- IF this check reached the emitter's escaper at all --
# must render as the hex escape `\x2f`, never as a bare `/` immediately
# after that `*`. This is the exact byte pair the bug corrupted.
if grep -q '\*\\x2f' "$WORK/waf.c" 2>/dev/null; then
    ok "F1 witness: the hazard byte pair reached emit_comment_safe_byte and was hex-escaped (\\x2f)"
else
    bad "F1 witness: no '*\\x2f' escape found in the artifact -- either the fix did not fire or the witness no longer exercises the hazard"
fi

# --- 3. AND THE EMITTED FILE HAS NO RAW STAR-SLASH INSIDE THE STATE LEGEND -
# A bare, un-escaped comment-closer inside the "shortest input" quoted
# example is exactly what broke compilation. Scan every quoted example on
# a state-legend row for a literal star immediately followed by a slash.
if [ -f "$WORK/waf.c" ]; then
    if grep -nE '^\s*\*\s+[0-9]+\s+"[^"]*\*/' "$WORK/waf.c" >"$WORK/badrow.txt" 2>/dev/null; then
        bad "F1 witness: found a raw, unescaped star-slash inside a state-legend quoted example: $(cat "$WORK/badrow.txt")"
    else
        ok "F1 witness: no raw star-slash inside any state-legend quoted example"
    fi
else
    bad "F1 witness: no artifact to scan (pcrec did not produce one)"
fi

# --- 4. THE ARTIFACT ACTUALLY COMPILES WITH GCC — the real regression net --
# The bar is the harness's own default GENCFLAGS ("-Wall -Wextra -Werror"),
# so this is definitive: a comment terminated early corrupts every byte the
# emitter wrote afterward, which shows up as exactly the cascade O-31 F1
# reported (missing terminating string quote, undeclared identifiers).
if [ -f "$WORK/waf.c" ] && "$CC" $GENCFLAGS_TEST -c -o "$WORK/waf.o" "$WORK/waf.c" 2>"$WORK/waf.cc.err"; then
    ok "F1 witness: emitted artifact COMPILES under the harness's own GENCFLAGS (the actual bug)"
else
    bad "F1 witness: emitted artifact FAILED TO COMPILE: $(head -10 "$WORK/waf.cc.err" 2>/dev/null)"
fi

# --- 5. AND IT ANSWERS CORRECTLY (oracle: the literal bytes /*!*/ ) --------
if pcrec_run "$PCREC" -p rx --engine=dfa --emit-main -o "$WORK/wafm.c" -- "$WITNESS" >/dev/null 2>&1 \
   && "$CC" -O1 -o "$WORK/wafm" "$WORK/wafm.c" 2>"$WORK/wafm.cc.err"; then
    got1="$("$WORK/wafm" 'a/*!*/b' 2>/dev/null)"
    got2="$("$WORK/wafm" 'nomatch' 2>/dev/null)"
    if [ "$got1" = "match 0 7" ] && [ "$got2" = "nomatch" ]; then
        ok "F1 witness: the compiled matcher answers correctly (a/*!*/b -> (0,7); a hazard-free subject -> nomatch)"
    else
        bad "F1 witness: wrong answer: got1='$got1' (want 'match 0 7'), got2='$got2' (want 'nomatch')"
    fi
else
    bad "F1 witness: could not build/run the --emit-main binary: $(head -5 "$WORK/wafm.cc.err" 2>/dev/null)"
fi

# --- 6. THE SECOND HAZARD, ISOLATED: a SLASH-STAR with no closer -----------
# `-Wcomment` fires on the OPEN half alone, with no `*/` anywhere in the
# pattern to trip the first hazard -- this is the check that would have
# stayed green if only the STAR-SLASH half of emit_comment_safe_byte had
# been built.
if pcrec_run "$PCREC" -p rx --engine=dfa -o "$WORK/open.c" -- "$OPENONLY" >"$WORK/open.log" 2>&1 \
   && "$CC" $GENCFLAGS_TEST -c -o "$WORK/open.o" "$WORK/open.c" 2>"$WORK/open.cc.err"; then
    ok "open-comment witness '$OPENONLY' compiles under the harness's own GENCFLAGS (-Wcomment does not fire)"
else
    bad "open-comment witness '$OPENONLY' failed: $(cat "$WORK/open.log" "$WORK/open.cc.err" 2>/dev/null | head -10)"
fi

# --- 7. A THIRD, SIMPLER WITNESS: a character class holding both bytes -----
# `[*/]` puts the raw two-byte sequence in the pattern's own SOURCE TEXT
# (not merely in a derived state-legend example), independently exercising
# the top-of-file banner comment's escaper (emit_pattern_comment) and the
# orientation-block map paragraph -- both refactored onto the same shared
# primitive.
CLS='a[*/]b'
if pcrec_run "$PCREC" -p rx --engine=dfa --emit-main -o "$WORK/cls.c" -- "$CLS" >"$WORK/cls.log" 2>&1 \
   && "$CC" $GENCFLAGS_TEST -o "$WORK/clsbin" "$WORK/cls.c" 2>"$WORK/cls.cc.err"; then
    ok "class witness '$CLS' compiles cleanly"
    g1="$("$WORK/clsbin" 'a*b' 2>/dev/null)"
    g2="$("$WORK/clsbin" 'a/b' 2>/dev/null)"
    g3="$("$WORK/clsbin" 'axb' 2>/dev/null)"
    if [ "$g1" = "match 0 3" ] && [ "$g2" = "match 0 3" ] && [ "$g3" = "nomatch" ]; then
        ok "class witness: answers correctly on both class members and the non-member"
    else
        bad "class witness: wrong answers: g1='$g1' g2='$g2' g3='$g3'"
    fi
else
    bad "class witness '$CLS' failed: $(cat "$WORK/cls.log" "$WORK/cls.cc.err" 2>/dev/null | head -5)"
fi

echo "checks passed: $pass  checks failed: $fail"
[ "$fail" -eq 0 ]
