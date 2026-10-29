#!/usr/bin/env bash
# scripts/check_pcre2_note.sh NOTE.md -- the clean-room wall's gate (D181).
# A pcre2-reader's note is PROSE about PCRE2 behaviour. This rejects what an
# accidental paste of source looks like; it is the least that catches one, not
# a proof of cleanliness (the reader's brief and the manager's read are the
# rest). Exit 0 clean, 1 with `file:line: reason` lines, 2 usage.
# Rejects: fenced code blocks; #define/#include/#if lines; brace-only line
# ends; call-or-assignment statements ending in `;`; runs of C operators
# (-> && || == != << >> += -= ++); PCRE2-internal identifier shapes: ALL_CAPS
# with an underscore that is not a public PCRE2_* name, lowercase_with_
# underscores of three or more words, pcre2_*_8/_16/_32 suffixed names, PRIV.
# File citations (name.c:123, name.h) are stripped before the identifier test.
set -u
[ $# -eq 1 ] && [ -r "$1" ] || { echo "usage: check_pcre2_note.sh NOTE.md" >&2; exit 2; }
awk '
function bad(why) { printf "%s:%d: %s\n", FILENAME, NR, why; rc = 1 }
/^[[:space:]]*(```|~~~)/ { bad("fenced code block"); next }
/^[[:space:]]*#[[:space:]]*(define|include|if|ifdef|ifndef|endif|undef|pragma)([^A-Za-z0-9_]|$)/ { bad("preprocessor line"); next }
/(^[[:space:]]*[{}][[:space:]]*$)|(\{[[:space:]]*$)|(^[[:space:]]*\}[;,]?)/ { bad("brace block") }
/[A-Za-z0-9_\])][[:space:]]*(\([^)]*\))?[[:space:]]*;[[:space:]]*$/ && /[(=]/ { bad("statement ending in semicolon") }
/->|&&|\|\||==|!=|<<|>>|\+=|-=|\+\+/ { bad("C operator run") }
{
    l = $0
    gsub(/[A-Za-z0-9_.\/-]+\.[ch]:[0-9]+([-,][0-9]+)*/, " ", l)
    gsub(/[A-Za-z0-9_\/-]+\.[ch]([^A-Za-z0-9_]|$)/, " ", l)
    while (match(l, /[A-Za-z_][A-Za-z0-9_]*/)) {
        w = substr(l, RSTART, RLENGTH); l = substr(l, RSTART + RLENGTH)
        if (w ~ /^PRIV$/) bad("internal identifier " w)
        else if (w ~ /^[A-Z][A-Z0-9]*_[A-Z0-9_]+$/ && w !~ /^PCRE2_[A-Z0-9_]+$/) bad("internal-looking constant " w)
        else if (w ~ /^pcre2_[a-z0-9_]+_(8|16|32)$/) bad("width-suffixed internal " w)
        else if (w ~ /^[a-z][a-z0-9]*_[a-z0-9]+_[a-z0-9_]+$/ && w !~ /^pcre2_/) bad("internal-looking identifier " w)
    }
}
END { exit rc }
' "$1"
