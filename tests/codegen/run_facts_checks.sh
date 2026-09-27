#!/usr/bin/env bash
# tests/codegen/run_facts_checks.sh — [PATFACTS] (D120/D126): the checks the
# pattern-facts record is born with (docs/design/patfacts/design.md §4.2.3,
# §11.6).
#
# =========================================================================
# 1-2. WHO MAY REACH A DERIVATION (design §4.2.3)
# =========================================================================
# A consumer reads a pattern fact through `src/facts/facts.h`'s accessor. A
# DERIVATION called any other way is a second, unmemoized, undenied path to
# the same answer — the parallel mechanism the record exists to remove. Two
# assertions, and they cover different escapes:
#
#   1. INCLUDE GRAPH. The set of files that `#include "facts/facts_derive.h"`
#      EQUALS the generated owner list — not "is a subset of": an owner that
#      stops including the header means the list names a file that no longer
#      owns anything, and that is a failure too.
#   2. LINK SYMBOLS. No object outside the owner list references (`nm -u`) a
#      symbol that an OWNER object defines (`nm -g`) and `facts.h` does not
#      declare. The symbol set comes from `nm`, never from a list of names, so
#      a hand `extern` that bypasses the header — which (1) cannot see — fails
#      here.
#
# THE OWNER LIST IS GENERATED, from `src/facts/facts.def` as PLAIN TEXT: every
# `.c` file under `src/facts/` plus the sixth field of each `PF_FACT(` line.
# Never through the X-macro expansion, so a preprocessor defect cannot hide a
# row from the check that polices it (design §4.2.3, C4's rule).
#
# WHAT IT CANNOT SEE: a HAND RE-SPELLING — a consumer that writes its own walk
# calls no derivation and includes nothing. `src/facts/CLAUDE.md` names it as
# the residual a reviewer looks for.
#
# =========================================================================
# 3-5. THE `--emit-facts` LISTING (design §11.6 checks 2-4)
# =========================================================================
# Each against an oracle the listing does not share:
#
#   3. COMPLETENESS — one `facts` row per `facts.def` row per encoding. The
#      expected count is the table's PLAIN-TEXT row count (`PF_FACT(` line
#      markers), never the X-macro expansion the printer iterates, so a row
#      the preprocessor or the printer drops cannot vanish from both sides.
#   4. WHY-TRUTHFULNESS — for every DENY flag `src/core/axes.def` spells, a
#      compile under that flag lists `deny:<flag>` on EXACTLY the facts
#      `docs/spec/tuning.md`'s "Facts emptied" line for that flag names, and
#      on no other. The oracle is the hand-written spec (D80), not
#      `facts.def`'s deny column, which is what drives the deny logic — a
#      wrong column would be agreed with by both.
#   5. DECISIONS = STAMPS — the `decisions` section equals the value
#      `#define`s parsed out of the emitted C file by THIS script. The
#      printer skips function-like macros by their `(`; this parser skips the
#      named machinery macros by NAME, so a new function-like macro — or a
#      stamp the printer stops reading — is a failure rather than a silent
#      omission.
#
# Usage: bash tests/codegen/run_facts_checks.sh
# Env: PCREC (default <root>/build/pcrec); the objects are read from
# `$(dirname $PCREC)/obj`, the tree that binary was linked from.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
# [K37] every compiler call below is bounded by `$TIMEOUT_BIN`.
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
# The build directory the binary was linked in (a path computation, not an
# invocation): its `obj/` is what the link assertion reads, and its parent is
# the tree whose facts.def and spec the checks read.
BIN_DIR="${PCREC%/*}"
OBJ_DIR="$(cd "$BIN_DIR" && pwd)/obj"
TREE="$(cd "$BIN_DIR/.." && pwd)"

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

pass=0; fail=0
ok()   { echo "PASS: $1"; pass=$((pass + 1)); }
bad()  { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

DEF="$TREE/src/facts/facts.def"
HDR="$TREE/src/facts/facts.h"

# ---- the owner list, from the table's text --------------------------------
{
    (cd "$TREE" && ls src/facts/*.c 2>/dev/null)
    grep -E '^PF_FACT\(' "$DEF" | awk -F',' '{ gsub(/[ "]/, "", $6); print $6 }'
} | LC_ALL=C sort -u > "$WORKDIR/owners"
nown="$(wc -l < "$WORKDIR/owners" | tr -d ' ')"
nrows="$(grep -cE '^PF_FACT\(' "$DEF")"
echo "REACH: facts.def rows: $nrows; generated owner list: $nown file(s)"
if [ "$nrows" -eq 0 ] || [ "$nown" -eq 0 ]; then
    bad "facts.def yielded no rows or no owners — the owner list is EMPTY, so both assertions below would pass vacuously"
fi
while read -r f; do
    [ -f "$TREE/$f" ] || bad "facts.def names owner '$f', which does not exist"
done < "$WORKDIR/owners"

# ---- 1. include graph -------------------------------------------------------
(cd "$TREE" && grep -rlE '^[[:space:]]*#[[:space:]]*include[[:space:]]+"facts/facts_derive\.h"' \
    src cli lib --include='*.c' --include='*.h' 2>/dev/null) | LC_ALL=C sort -u > "$WORKDIR/includers"
if cmp -s "$WORKDIR/owners" "$WORKDIR/includers"; then
    ok "[facts-include] the includers of facts/facts_derive.h are exactly the $nown owners facts.def names"
else
    bad "[facts-include] includers of facts/facts_derive.h != the owner list generated from facts.def (< owners only, > includers only):"
    diff "$WORKDIR/owners" "$WORKDIR/includers" | grep '^[<>]' >&2
fi

# ---- 2. link symbols --------------------------------------------------------
if ! command -v nm >/dev/null 2>&1; then
    bad "[facts-link] nm is unavailable — the link-symbol assertion cannot be skipped silently"
elif [ ! -d "$OBJ_DIR" ]; then
    bad "[facts-link] no object directory at $OBJ_DIR — build first"
else
    # Mach-O prepends `_` to every C symbol; ELF does not.
    under=""; [ "$(uname -s)" = Darwin ] && under="_"
    grep -oE 'pcrec_[A-Za-z0-9_]+' "$HDR" | LC_ALL=C sort -u > "$WORKDIR/public"
    : > "$WORKDIR/defined"
    while read -r f; do
        o="$OBJ_DIR/${f#src/}"; o="${o%.c}.o"
        if [ ! -f "$o" ]; then bad "[facts-link] owner object $o is missing"; continue; fi
        nm -g "$o" | awk '$2 ~ /^[TDBSCR]$/ { print $3 }' | sed "s/^$under//" >> "$WORKDIR/defined"
    done < "$WORKDIR/owners"
    LC_ALL=C sort -u "$WORKDIR/defined" | LC_ALL=C comm -23 - "$WORKDIR/public" > "$WORKDIR/private"
    nsym="$(wc -l < "$WORKDIR/private" | tr -d ' ')"
    nobj=0; leaks=""
    while read -r o; do
        rel="src/${o#"$OBJ_DIR"/}"; rel="${rel%.o}.c"
        # A STALE object (its source moved or was deleted since the build
        # dir last saw it) is not linked into anything; skip it rather than
        # judge a file that no longer exists.
        [ -f "$TREE/$rel" ] || continue
        grep -qxF "$rel" "$WORKDIR/owners" && continue
        nobj=$((nobj + 1))
        hit="$(nm -u "$o" 2>/dev/null | sed "s/^$under//" | LC_ALL=C sort -u |
               LC_ALL=C comm -12 - "$WORKDIR/private" | tr '\n' ' ')"
        [ -n "$hit" ] && leaks="$leaks $rel: $hit;"
    done < <(find "$OBJ_DIR" -name '*.o' | LC_ALL=C sort)
    echo "REACH: $nsym facts-private symbol(s) defined by the owners; $nobj non-owner object(s) scanned"
    if [ "$nsym" -eq 0 ] || [ "$nobj" -eq 0 ]; then
        bad "[facts-link] no private derivation symbol or no non-owner object — the link assertion is vacuous"
    elif [ -n "$leaks" ]; then
        bad "[facts-link] a non-owner object references a facts-private derivation symbol (a hand extern bypassing facts.h):$leaks"
    else
        ok "[facts-link] no non-owner object references any of the $nsym facts-private symbols"
    fi
fi

# ---- 3-5. the listing -------------------------------------------------------
# Columns are resolved BY HEADER NAME within a named section (the table
# contract's consumer rules), never by position.
sect() { # sect <file> <section> -> "col=value<TAB>..." per data row, header-keyed
    awk -F'\t' -v want="$2" '
        /^#section / { split($0, w, " "); insec = (w[2] == want); hdr = ""; next }
        !insec { next }
        /^#/ { hdr = substr($0, 2); next }
        { n = split(hdr, h, "\t"); line = "";
          for (i = 1; i <= n; i++) line = line (i > 1 ? "\t" : "") h[i] "=" $i;
          print line }' "$1"
}
col() { # col <name> : from stdin "k=v<TAB>..." rows, print field <name>
    awk -F'\t' -v want="$1" '{ for (i = 1; i <= NF; i++) {
        k = substr($i, 1, index($i, "=") - 1);
        if (k == want) print substr($i, index($i, "=") + 1) } }'
}

LISTPAT='/user|/users'
if ! "$TIMEOUT_BIN" 120 "$PCREC" --emit-facts=byte,utf8 --pattern "$LISTPAT" > "$WORKDIR/l2" 2> "$WORKDIR/l2.err"; then
    bad "[facts-complete] --emit-facts=byte,utf8 refused '$LISTPAT': $(cat "$WORKDIR/l2.err")"
else
    sect "$WORKDIR/l2" facts > "$WORKDIR/l2.facts"
    nlist="$(wc -l < "$WORKDIR/l2.facts" | tr -d ' ')"
    echo "REACH: listing facts rows (byte,utf8): $nlist; expected $((2 * nrows))"
    dup="$(col fact < "$WORKDIR/l2.facts" | LC_ALL=C sort | uniq -c | awk '$1 != 2 { print $2 }' | tr '\n' ' ')"
    if [ "$nrows" -eq 0 ]; then
        bad "[facts-complete] facts.def has no rows — the completeness check is vacuous"
    elif [ "$nlist" -ne $((2 * nrows)) ] || [ -n "$dup" ]; then
        bad "[facts-complete] the listing has $nlist facts rows for 2 encodings where facts.def has $nrows rows (each fact must appear once per encoding; off: $dup)"
    else
        ok "[facts-complete] one facts row per facts.def row per encoding ($nrows x 2)"
    fi
fi

# 4. why-truthfulness, over every deny flag axes.def spells.
TUNING="$TREE/docs/spec/tuning.md"
grep -oE '^PCREC_AXIS\([A-Z_0-9]+, *"-fno-[a-z0-9-]+"' "$TREE/src/core/axes.def" |
    grep -oE '"-fno-[a-z0-9-]+"' | tr -d '"' > "$WORKDIR/denyflags"
nflags="$(wc -l < "$WORKDIR/denyflags" | tr -d ' ')"
nclaim=0; wbad=""
while read -r flag; do
    # The flag's own `### 2.N` section, and in it the "Facts emptied" line.
    want="$(awk -v f="\`$flag\`" '
        /^### / { insec = (index($0, f) > 0); next }
        insec && /^\*\*Facts emptied\*\*/ {
            line = $0; sub(/^.*\): */, "", line); gsub(/[`.,]/, " ", line); print line }' "$TUNING" |
        tr ' ' '\n' | grep -v '^$' | LC_ALL=C sort -u | tr '\n' ' ')"
    [ -n "$want" ] && nclaim=$((nclaim + 1))
    if ! "$TIMEOUT_BIN" 120 "$PCREC" --emit-facts "$flag" --pattern "$LISTPAT" > "$WORKDIR/lw" 2> "$WORKDIR/lw.err"; then
        wbad="$wbad $flag: refused ($(head -1 "$WORKDIR/lw.err"));"
        continue
    fi
    got="$(sect "$WORKDIR/lw" facts | awk -F'\t' -v tok="why=deny:$flag" '
        { for (i = 1; i <= NF; i++) if ($i == tok) { for (j = 1; j <= NF; j++)
              if (substr($j, 1, 5) == "fact=") print substr($j, 6) } }' |
        LC_ALL=C sort -u | tr '\n' ' ')"
    [ "$want" = "$got" ] || wbad="$wbad $flag: tuning.md names [${want% }], the listing denies [${got% }];"
done < "$WORKDIR/denyflags"
echo "REACH: $nflags deny flag(s) from axes.def; $nclaim carry a tuning.md \"Facts emptied\" line"
if [ "$nflags" -eq 0 ] || [ "$nclaim" -eq 0 ]; then
    bad "[facts-why] no deny flag or no \"Facts emptied\" claim found — the check is vacuous"
elif [ -n "$wbad" ]; then
    bad "[facts-why] a fact deny's listing disagrees with docs/spec/tuning.md:$wbad"
else
    ok "[facts-why] every one of the $nflags deny flags denies exactly the facts tuning.md says it empties ($nclaim with a claim)"
fi

# 5. decisions = stamps, on a DFA, a hybrid and a VM artifact.
MACHINERY=' TIER_NOTE CHARGE_WORK PRUNE_TOO_SHORT PRUNE_CLAMP_SPAN TRAIL SET PUSH CUT CALL '
nstamp=0; dbad=""
for spec in "dfa|/user|/users|" "hybrid|(a|b)+c|" "vm|(a|b)+\\1c|--features all --engine=vm"; do
    what="${spec%%|*}"; rest="${spec#*|}"; pat="${rest%|*}"; extra="${rest##*|}"
    # shellcheck disable=SC2086
    if ! "$TIMEOUT_BIN" 120 "$PCREC" -p rx -o - $extra --pattern "$pat" > "$WORKDIR/d.c" 2>/dev/null ||
       ! "$TIMEOUT_BIN" 120 "$PCREC" $extra --emit-facts --pattern "$pat" > "$WORKDIR/d.l" 2>/dev/null; then
        dbad="$dbad $what: '$pat' did not compile;"; continue
    fi
    grep -E '^#define (RX_|PCREC_FEATURE_)[A-Za-z0-9_]+' "$WORKDIR/d.c" |
        awk -v mach="$MACHINERY" '{
            name = $2; sub(/\(.*/, "", name);
            short = name; sub(/^RX_/, "", short);
            if (index(mach, " " short " ")) next;
            v = $0; sub(/^#define[ \t]+[A-Za-z0-9_]+(\([^)]*\))?[ \t]*/, "", v);
            print name "\t" v }' > "$WORKDIR/d.want"
    sect "$WORKDIR/d.l" decisions | awk -F'\t' '{ n = ""; v = "";
        for (i = 1; i <= NF; i++) { if (substr($i, 1, 6) == "stamp=") n = substr($i, 7);
                                    if (substr($i, 1, 6) == "value=") v = substr($i, 7) }
        print n "\t" v }' > "$WORKDIR/d.got"
    k="$(wc -l < "$WORKDIR/d.want" | tr -d ' ')"; nstamp=$((nstamp + k))
    [ "$k" -gt 0 ] || dbad="$dbad $what: the emitted file carried no stamp;"
    if ! cmp -s "$WORKDIR/d.want" "$WORKDIR/d.got"; then
        dbad="$dbad $what: decisions != the file's stamps ($(diff "$WORKDIR/d.want" "$WORKDIR/d.got" | grep -c '^[<>]') line(s) differ: $(diff "$WORKDIR/d.want" "$WORKDIR/d.got" | grep '^[<>]' | head -3 | tr '\t\n' ' ;'));"
    fi
done
echo "REACH: $nstamp stamp(s) compared across a DFA, a hybrid and a VM artifact"
if [ -n "$dbad" ]; then
    bad "[facts-decisions]$dbad"
elif [ "$nstamp" -eq 0 ]; then
    bad "[facts-decisions] no stamp compared — the check is vacuous"
else
    ok "[facts-decisions] the decisions section is the emitted file's $nstamp value stamps, in order"
fi

# 6. the query's own plumbing (docs/spec/cli.md §2): a QUERY that takes a
# pattern and no -o, composes with no other query mode, refuses an unknown
# encoding name — each refusal is exit 1 with nothing on stdout.
cbad=""
refuse() { # refuse <label> <args...>
    local label="$1"; shift
    local rc
    "$TIMEOUT_BIN" 60 "$PCREC" "$@" > "$WORKDIR/c.out" 2> "$WORKDIR/c.err"
    rc=$?
    if [ "$rc" -eq 0 ]; then
        cbad="$cbad $label: accepted;"
    elif [ "$rc" -ne 1 ] || [ -s "$WORKDIR/c.out" ] || [ ! -s "$WORKDIR/c.err" ]; then
        cbad="$cbad $label: rc $rc, not a lone diagnostic with exit 1;"
    fi
}
refuse "-o" --emit-facts -o "$WORKDIR/x.c" --pattern abc
refuse "no pattern" --emit-facts
refuse "unknown encoding" --emit-facts=byte,nosuch --pattern abc
refuse "empty list entry" --emit-facts=byte,,utf8 --pattern abc
refuse "with --emit-ir" --emit-facts --emit-ir --pattern abc
refuse "with --count-groups" --emit-facts --count-groups --pattern abc
refuse "with --list-syntax" --emit-facts --list-syntax
refuse "refused pattern" --emit-facts --pattern 'a('
if [ -n "$cbad" ]; then
    bad "[facts-cli]$cbad"
else
    ok "[facts-cli] --emit-facts refuses -o, a missing pattern, an unknown or empty encoding, the other query modes and a refused pattern (8 cases)"
fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
