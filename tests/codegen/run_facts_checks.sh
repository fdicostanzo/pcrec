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
# =========================================================================
# 7. THE E1 FACTS AGAINST THE PATTERN'S OWN STRUCTURE (step 3.2, design §3)
# =========================================================================
# The kind mask and nullability are sealed on the STRUCTURAL tree and
# re-derived on the LOWERED one at the E2 seal, where a disagreement refuses
# the compile with an internal error (`src/facts/facts.c`'s
# `pf_check_e1`). This check is that cross-check's detector and the E1 rows'
# oracle at once: every witness below must COMPILE under its encoding, and
# its listing's `kinds`/`nullable` values must equal the ones written here BY
# HAND from the pattern's structure — never read off the compiler.
#
# REACH: the cross-check can only disagree where the lowering REWRITES the
# tree, which is `-e utf8` with a class above U+007F; the witnesses are
# chosen so every kind bit and both nullability answers sit on such a tree.
# The check counts those witnesses, and fails if any `PF_KIND_*` bit
# `src/facts/facts.h` declares has no witness (a new bit arrives with one).
#
# =========================================================================
# 8. THE E3 FACTS: THE SEAL IS PER BRANCH, THE DECLINE NAMES THE ROUTE
#    (step 3.4, design §3 and §4.5)
# =========================================================================
# `kset_walk` and `run_pin` are sealed (E3) inside `compile_driver`'s
# ENG_UNANCH arm alone. Every other route answers them `absent` with a
# decline naming the route: `decline:attempt-unwrapped-nfa` (ENG_ATTEMPT —
# a forward NFA exists, never wrapped) or `decline:no-forward-nfa` (a VM
# route with no DFA scan). THE ROUTE ORACLE IS THE ARTIFACT, not the record:
# each witness's `RX_DFA_SCAN` stamp is read out of the emitted `.c` file
# (`unanchored`, `attempt`, or no stamp at all), and the E3 rows' status and
# `why` must be the ones that route implies. The witness's route is ALSO
# written by hand, so a witness that drifts to another route fails rather
# than silently re-testing a covered one; REACH requires all three routes.
# On the sealed route the walk and the pin must equal the values written BY
# HAND from the pattern (never read off the compiler). One witness is the
# pin's WIDENED DOMAIN (design §9 "Why 3.4 is flagged" (i)): the pin is set
# on an artifact whose forward scan has no offset-0 prefilter, and no pass
# asked for it — every pin reader carries the kind gate.
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
# THE NODE-GRAIN CARVE-OUT (src/facts/CLAUDE.md; docs/design/alt_normal_form.md
# §3.5 r7 FIX-4): a file here that is a pure function over a subtree, reading
# no sealed fact, is not a derivation owner. Its own header is its public
# surface (the opt layer calls it: the owner's code-point call site), and it
# must NOT include facts_derive.h, which is checked below.
CARVE="src/facts/desc.c"
{
    (cd "$TREE" && ls src/facts/*.c 2>/dev/null) | grep -vxF "$(printf '%s\n' $CARVE)"
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

for f in $CARVE; do
    if [ ! -f "$TREE/$f" ]; then
        bad "[facts-include] the carve-out names '$f', which does not exist"
    elif grep -qE '^[[:space:]]*#[[:space:]]*include[[:space:]]+"facts/facts_derive\.h"' "$TREE/$f"; then
        bad "[facts-include] carve-out '$f' includes facts_derive.h: a node-grain pure function reads no sealed fact"
    fi
done

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
    # The owner-defined symbols facts.h DOES declare: the accessors every
    # consumer legitimately calls. The control below joins against them.
    LC_ALL=C sort -u "$WORKDIR/defined" | LC_ALL=C comm -12 - "$WORKDIR/public" > "$WORKDIR/accessors"
    nobj=0; leaks=""; nacc=0
    while read -r o; do
        rel="src/${o#"$OBJ_DIR"/}"; rel="${rel%.o}.c"
        # A STALE object (its source moved or was deleted since the build
        # dir last saw it) is not linked into anything; skip it rather than
        # judge a file that no longer exists.
        [ -f "$TREE/$rel" ] || continue
        grep -qxF "$rel" "$WORKDIR/owners" && continue
        nobj=$((nobj + 1))
        # The NAME is the LAST field: Mach-O `nm -u` prints the bare name,
        # GNU nm prints `U name` behind an indent. Reading the whole line
        # joined nothing on ELF, so this assertion was vacuous on Linux
        # until lane r1mtriage (2026-10-05, S297 UNDETECTED there only).
        nm -u "$o" 2>/dev/null | awk '{ print $NF }' | sed "s/^$under//" |
            LC_ALL=C sort -u > "$WORKDIR/undef"
        hit="$(LC_ALL=C comm -12 "$WORKDIR/undef" "$WORKDIR/private" | tr '\n' ' ')"
        [ -n "$hit" ] && leaks="$leaks $rel: $hit;"
        nacc=$((nacc + $(LC_ALL=C comm -12 "$WORKDIR/undef" "$WORKDIR/accessors" | wc -l)))
    done < <(find "$OBJ_DIR" -name '*.o' | LC_ALL=C sort)
    echo "REACH: $nsym facts-private symbol(s) defined by the owners; $nobj non-owner object(s) scanned; $nacc accessor reference(s) joined"
    if [ "$nsym" -eq 0 ] || [ "$nobj" -eq 0 ]; then
        bad "[facts-link] no private derivation symbol or no non-owner object — the link assertion is vacuous"
    elif [ "$nacc" -eq 0 ]; then
        # THE PARSE'S OWN CONTROL: the same `nm -u` read that would find a
        # leak must find the consumers' LEGITIMATE accessor calls. Zero means
        # the read joins nothing, and a zero-leak PASS would be vacuous.
        bad "[facts-link] no non-owner object references any facts.h accessor — the nm -u parse joins nothing, so the link assertion is vacuous"
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
        insec && /^(<a id="[^"]*"><\/a>\[[^]]*\] )?\*\*Facts emptied\*\*/ {
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
# ITER_INIT is the shared ABI block's iterator initializer ([FINDALL-NEXT] I1):
# a caller macro and no decision.
MACHINERY=' TIER_NOTE CHARGE_WORK PRUNE_TOO_SHORT PRUNE_CLAMP_SPAN TRAIL TRAIL_CHECK SET PUSH CUT CALL ITER_INIT '
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

# 7. the E1 facts. One witness per line, TAB-separated (a pattern holds `|`):
# E1W, encoding, pattern, kinds, nullable, empty_admits. `kinds` is the
# listing's comma-joined member list in bit order, or `none`. `empty_admits`
# ([NULLABLE-ANCH]) is `no` where the pattern is not nullable and where every
# empty path crosses a non-multiline start AND end anchor; the last two rows
# are that pair on a lowering-rewritten tree.
#
# [K69] THE CALL ROWS (the last six) are nullability that runs THROUGH A
# CALL, so they read `pcrec_nullable`'s `A_CALL` arm, i.e. the call graph's
# published `nonnullable`. The four `no` rows are the fixpoint's LEAST side:
# `(a|(?1))`'s group is `{a}` (a greatest fixpoint reads it nullable), and the
# other three are non-nullable only through a call whose answer must exist
# at the E1 seal (lane pf35's M2). The two `yes` rows are the other side: a
# nullable callee, directly and through a second call (g -> h = b?). By
# hand from the patterns; the answers are libpcre2 10.46's
# (tests/recursion/k69.rxt). Sabotage S318 (every call nullable) and S319
# (no call nullable) each turn one side red.
# [INLINE-C] 1b: `a(?C1)b` witnesses the `callout` bit (a check site:
# zero-width, so neither nullable nor empty-admitting through it).
# [UCP] U2: the byte lookaround row was `a?(?=b)`; a one-character body is
# T3's context node now (no `lookaround` kind — the prefilter reads it
# exactly), so the witness is two characters wide to stay a lookaround.
printf '%s\n' \
    'E1W	byte	abc	none	no	no' \
    'E1W	byte	a?(?=bc)	lookaround	yes	yes' \
    'E1W	utf8	\x{3b1}	none	no	no' \
    'E1W	utf8	[\x{3b1}-\x{3c9}]	none	no	no' \
    'E1W	utf8	\x{3b1}?	none	yes	yes' \
    'E1W	utf8	[\x{3b1}\x{3b2}]*	none	yes	yes' \
    'E1W	utf8	(\x{3b1})\1	bref,live_capture	no	no' \
    'E1W	utf8	(a|(?1)\x{3b1})	linked_call,live_capture	no	no' \
    'E1W	utf8	x${v}\x{3b1}	var	no	no' \
    'E1W	utf8	(?>\x{3b1}|\x{3b1}b)c	atomic	no	no' \
    'E1W	utf8	(?=\x{3b1})a*	lookaround	yes	yes' \
    'E1W	utf8	\x{3b1}{2,5}	collapsible_rep	no	no' \
    'E1W	byte	a(?C1)b	callout	no	no' \
    'E1W	byte	(a|(?1))	linked_call,live_capture	no	no' \
    'E1W	byte	(a)?(?1)	live_capture	no	no' \
    'E1W	byte	(?:(a)|)(?1)	live_capture	no	no' \
    'E1W	utf8	(?(DEFINE)(?<g>a))(?&g)	none	no	no' \
    'E1W	byte	(?(DEFINE)(?<g>a?))(?&g)	none	yes	yes' \
    'E1W	utf8	(?(DEFINE)(?<g>(?&h)|a)(?<h>b?))(?&g)	none	yes	yes' \
    'E1W	utf8	^\x{3b1}*$	none	yes	no' \
    'E1W	utf8	^\x{3b1}*	none	yes	yes' > "$WORKDIR/e1w"
nwit=0; nlow=0; ebad=""
: > "$WORKDIR/e1kinds"
while IFS=$'\t' read -r _ enc pat wkinds wnull wadmit; do
    nwit=$((nwit + 1))
    # A lowering-REWRITTEN tree: -e utf8 and some `\x{H}` above U+007F.
    if [ "$enc" = utf8 ]; then
        for h in $(grep -oE '\\x\{[0-9a-fA-F]+\}' <<< "$pat" | tr -d '\\x{}'); do
            if [ $((16#$h)) -gt 127 ]; then nlow=$((nlow + 1)); break; fi
        done
    fi
    tr ',' '\n' <<< "$wkinds" >> "$WORKDIR/e1kinds"
    if ! "$TIMEOUT_BIN" 120 "$PCREC" --features all -e "$enc" --emit-facts --pattern "$pat" > "$WORKDIR/e1.l" 2> "$WORKDIR/e1.err"; then
        ebad="$ebad $enc '$pat': refused ($(head -1 "$WORKDIR/e1.err"));"
        continue
    fi
    sect "$WORKDIR/e1.l" facts > "$WORKDIR/e1.f"
    gk="$(grep -F "$(printf 'fact=kinds\t')" "$WORKDIR/e1.f" | col value)"
    gn="$(grep -F "$(printf 'fact=nullable\t')" "$WORKDIR/e1.f" | col value)"
    ga="$(grep -F "$(printf 'fact=empty_admits\t')" "$WORKDIR/e1.f" | col value)"
    [ "$gk" = "$wkinds" ] || ebad="$ebad $enc '$pat': kinds [$gk], by hand [$wkinds];"
    [ "$gn" = "$wnull" ]  || ebad="$ebad $enc '$pat': nullable [$gn], by hand [$wnull];"
    [ "$ga" = "$wadmit" ] || ebad="$ebad $enc '$pat': empty_admits [$ga], by hand [$wadmit];"
done < "$WORKDIR/e1w"
# The bits are the rows of facts.h's `PF_KIND_ROWS` X-list (one `X(NAME,
# "name")` row per bit since lane ic1bfix, 2026-10-26; the enum is generated
# from it), so the population is counted off those rows.
nbits="$(grep -cE '^[[:space:]]*X\([A-Z_]+,[[:space:]]*"' "$HDR")"
ncov="$(grep -v '^none$' "$WORKDIR/e1kinds" | LC_ALL=C sort -u | wc -l | tr -d ' ')"
echo "REACH: $nwit E1 witness(es), $nlow under utf8 with a class the lowering rewrites; $ncov of $nbits PF_KIND_* bit(s) witnessed"
if [ "$nwit" -eq 0 ] || [ "$nlow" -eq 0 ] || [ "$nbits" -eq 0 ]; then
    bad "[facts-e1] no witness, no lowering-rewritten witness or no PF_KIND_* bit found — the check is vacuous"
elif [ "$ncov" -ne "$nbits" ]; then
    bad "[facts-e1] $ncov kind(s) witnessed where facts.h declares $nbits PF_KIND_* bits — a bit has no witness"
elif [ -n "$ebad" ]; then
    bad "[facts-e1] the E1 facts disagree with the pattern's structure, or the E1 cross-check refused:$ebad"
else
    ok "[facts-e1] $nwit witnesses compile and list the kind mask, nullability and empty_admits written by hand ($nlow on a lowering-rewritten tree; all $nbits kind bits)"
fi

# 8. the E3 facts. One witness per line, TAB-separated: E3W, extra flags
# (`-` for none), pattern, the route by hand (`RX_DFA_SCAN`'s value, or
# `none` where the artifact has no DFA scan), and on the sealed route the
# walk and the pin by hand (`-` elsewhere). The walk is the listing's
# spelling: a singleton offset as its byte in decimal, a wider set as `[N]`.
# The pin is `run_pin`'s rendering: `o`, or `o:at+len` when its exact stretch
# is narrower than the run window (C3, docs/spec/facts_listing.md). Since C3
# (abi 59) `/abcd[xy]/user`'s run is the 8-byte masked window `/abcd[xy]/u`
# (the {x,y} cube joins it), so its pin at 6 keeps the exact stretch `/u`
# (6:6+2) where abi 58's exact run `/user` read `6`; since R-38 K38-2 the pin
# reads the WHOLE run `/abcd[xy]/user` (no cut window), so its exact stretch
# at 6 is `/user` again, 6:6+5. `\zabc` is the widened-
# domain witness (a pin on an artifact whose NEXT row is `none`); since
# [REQ-HANDOFF-L1] (abi 75) its run handoff re-enters (`handoff`), so it is
# compiled under `-fno-req-handoff` to stay on that domain. Since D172 S3 the
# fixed-width `abc` and `/abcd[xy]/user` are `cover` artifacts by default (no
# forward scan), so they are compiled under the cover row's deny,
# `--memfn=no-window-search` (registry.md §6¶8a), to stay on the unanchored route.
# Since [LANDWALK] stage 1 (abi 95) `\zabc` takes the `landmark-walk` LOCATE
# row under `-fno-req-handoff` (its landmark `c` is rarer than NEXT's start
# set), so it also carries the walk's deny, `-fno-landmark-walk` (tuning.md
# §2.54), to stay on the widened domain's unanchored route.
printf '%s\n' \
    'E3W	--memfn=no-window-search	abc	unanchored	97,98,99	0' \
    'E3W	--memfn=no-window-search	/abcd[xy]/user	unanchored	47,97,98,99,100,[2],47,117,115,101,114	6:6+5' \
    'E3W	-fno-req-run --memfn=no-window-search	/abcd[xy]/user	unanchored	47,97,98,99,100,[2],47,117,115,101,114	none' \
    'E3W	--engine=vm -fprefilter	abc+d	unanchored	97,98,99,[2]	0' \
    'E3W	-fno-req-handoff -fno-landmark-walk	\zabc	unanchored	97,98,99	0' \
    'E3W	-	^abc	attempt	-	-' \
    'E3W	--engine=vm -fprefilter	^foo(?=bar)baz	attempt	-	-' \
    'E3W	-	(a)\1b	none	-	-' > "$WORKDIR/e3w"
nwit3=0; nwide=0; e3bad=""
: > "$WORKDIR/e3routes"
while IFS=$'\t' read -r _ xf pat wroute wwalk wpin; do
    nwit3=$((nwit3 + 1))
    [ "$xf" = - ] && xf=""
    # shellcheck disable=SC2086
    if ! "$TIMEOUT_BIN" 120 "$PCREC" --features all $xf -p rx -o - --pattern "$pat" > "$WORKDIR/e3.c" 2>/dev/null ||
       ! "$TIMEOUT_BIN" 120 "$PCREC" --features all $xf --emit-facts --pattern "$pat" > "$WORKDIR/e3.l" 2> "$WORKDIR/e3.err"; then
        e3bad="$e3bad '$pat': refused;"; continue
    fi
    route="$(sed -n 's/^#define RX_DFA_SCAN "\(.*\)"$/\1/p' "$WORKDIR/e3.c")"
    [ -n "$route" ] || route=none
    echo "$route" >> "$WORKDIR/e3routes"
    if [ "$route" != "$wroute" ]; then
        e3bad="$e3bad '$pat': the artifact's route is [$route], by hand [$wroute];"; continue
    fi
    case "$route" in
        unanchored) wst=derived; wwhy="" ;;
        attempt)    wst=absent;  wwhy="decline:attempt-unwrapped-nfa" ;;
        *)          wst=absent;  wwhy="decline:no-forward-nfa" ;;
    esac
    sect "$WORKDIR/e3.l" facts > "$WORKDIR/e3.f"
    for fact in kset_walk run_pin; do
        row="$(grep -F "$(printf 'fact=%s\t' "$fact")" "$WORKDIR/e3.f")"
        gst="$(col status <<< "$row")"; gwhy="$(col why <<< "$row")"; gval="$(col value <<< "$row")"
        [ "$gst" = "$wst" ] && [ "$gwhy" = "$wwhy" ] ||
            e3bad="$e3bad '$pat' ($route): $fact is [$gst/$gwhy], the route implies [$wst/$wwhy];"
        if [ "$route" = unanchored ]; then
            want="$wwalk"; [ "$fact" = run_pin ] && want="$wpin"
            [ "$gval" = "$want" ] || e3bad="$e3bad '$pat': $fact [$gval], by hand [$want];"
        elif [ -n "$gval" ]; then
            e3bad="$e3bad '$pat' ($route): an absent $fact lists a value [$gval];"
        fi
    done
    # The widened domain: a pin no pass asked for, on an artifact with no
    # offset-0 prefilter to carry an offset row.
    prow="$(grep -F "$(printf 'fact=run_pin\t')" "$WORKDIR/e3.f")"
    if [ "$route" = unanchored ] && [ "$(col value <<< "$prow")" != none ] &&
       grep -q '^#define RX_DFA_PREFILTER "none"$' "$WORKDIR/e3.c"; then
        nwide=$((nwide + 1))
        [ "$(col used <<< "$prow")" = no ] ||
            e3bad="$e3bad '$pat': a pin on a DFA_PF_NONE artifact was ASKED by a pass (a reader without the kind gate);"
    fi
done < "$WORKDIR/e3w"
nroutes="$(LC_ALL=C sort -u "$WORKDIR/e3routes" | wc -l | tr -d ' ')"
echo "REACH: $nwit3 E3 witness(es) over $nroutes of 3 route(s); $nwide on the pin's widened domain"
if [ "$nwit3" -eq 0 ] || [ "$nroutes" -ne 3 ] || [ "$nwide" -eq 0 ]; then
    bad "[facts-e3] the witnesses reach $nroutes of the 3 routes and $nwide widened-domain pin(s) — the check is vacuous where it is short"
elif [ -n "$e3bad" ]; then
    bad "[facts-e3] the E3 facts disagree with the artifact's route or the pattern:$e3bad"
else
    ok "[facts-e3] $nwit3 witnesses: E3 is derived on the unanchored route alone, each other route declines by name, and the walk and pin are the ones written by hand ($nwide widened-domain pin, asked by no pass)"
fi

# 9. [START-LANDING] SL1 THE HAND-WITNESS TABLE (start_landing.md §7.2,
# [r2 SL-C8]). `land_char` (Λ, the one-character fact) and `width` (the byte
# width interval) are listed EXACTLY as written here, by hand, from the
# definitions (§2.4, §3.1) — never read off either walk, so the table shares no
# source with the build or with the design's prototype probe. One witness per
# line, TAB-separated: enc, pattern, land_char (the value `one-char` /
# `one-char+guard` where it holds, else its `decline:` why), width.
# `+guard`: a first byte above the encoding's one-byte repertoire, §2.5.
# `a\bb`'s Λ is `assert-after` by §2.4's definition (an assertion before the
# accept); the design's table wrote "(empty engine)" there, which names the
# route RECOVER takes, not the fact. REACH: every decline the fact can name
# except `dead-start` (a start closure with no consumer, no accept and no
# assertion, which no pattern this parser builds produces; the decline is the
# safe answer for a malformed machine) has a witness.
printf '%s\n' \
    'byte	\w+	one-char	[1,inf)' \
    'byte	ab	decline:alive-not-accept	[2,2]' \
    'byte	\b\w+	decline:assert-at-start	[1,inf)' \
    'byte	\w+\b	decline:assert-after	[1,inf)' \
    'byte	x*y	decline:alive-not-accept	[1,inf)' \
    'byte	abcd	decline:alive-not-accept	[4,4]' \
    'byte	a\bb	decline:assert-after	[2,2]' \
    'byte	(?s).+	one-char	[1,inf)' \
    'byte	a*	decline:nullable	[0,inf)' \
    'byte	a|bc	decline:alive-not-accept	[1,2]' \
    'utf8	.	one-char+guard	[1,4]' \
    'utf8	é	one-char+guard	[2,2]' \
    'utf8	.{3,8}	decline:alive-not-accept	[3,32]' \
    'utf8	[a-zé]+	one-char+guard	[1,inf)' \
    'utf8	\w+	one-char	[1,inf)' > "$WORKDIR/slw"
nsl=0; slbad=""
: > "$WORKDIR/slwhy"
while IFS=$'\t' read -r enc pat wland wwidth; do
    nsl=$((nsl + 1))
    case "$wland" in decline:*) echo "$wland" >> "$WORKDIR/slwhy" ;; esac
    if ! "$TIMEOUT_BIN" 120 "$PCREC" --features all -e "$enc" --emit-facts --pattern "$pat" > "$WORKDIR/sl.l" 2> "$WORKDIR/sl.err"; then
        slbad="$slbad $enc '$pat': refused ($(head -1 "$WORKDIR/sl.err"));"; continue
    fi
    sect "$WORKDIR/sl.l" facts > "$WORKDIR/sl.f"
    lrow="$(grep -F "$(printf 'fact=land_char\t')" "$WORKDIR/sl.f")"
    wrow="$(grep -F "$(printf 'fact=width\t')" "$WORKDIR/sl.f")"
    case "$(col status <<< "$lrow")" in
        derived)  gland="$(col value <<< "$lrow")" ;;
        declined) gland="$(col why <<< "$lrow")" ;;
        *)        gland="[$(col status <<< "$lrow")/$(col why <<< "$lrow")]" ;;
    esac
    gwidth="$(col value <<< "$wrow")"
    [ "$gland" = "$wland" ] || slbad="$slbad $enc '$pat': land_char [$gland], by hand [$wland];"
    [ "$gwidth" = "$wwidth" ] || slbad="$slbad $enc '$pat': width [$gwidth], by hand [$wwidth];"
done < "$WORKDIR/slw"
nslwhy="$(LC_ALL=C sort -u "$WORKDIR/slwhy" | wc -l | tr -d ' ')"
echo "REACH: $nsl [START-LANDING] witness(es), $nslwhy of 4 reachable land_char decline(s) witnessed"
if [ "$nsl" -eq 0 ] || [ "$nslwhy" -ne 4 ]; then
    bad "[facts-sl1] the hand table reaches $nslwhy of the 4 reachable declines — the check is vacuous where it is short"
elif [ -n "$slbad" ]; then
    bad "[facts-sl1] land_char/width disagree with the hand table:$slbad"
else
    ok "[facts-sl1] $nsl witnesses list land_char and width exactly as the definitions give them (all 4 reachable declines)"
fi

# ---- [RUN-POS-SET] stage 2p: the piece set ----------------------------------
# `req_pieces` (docs/design/alt_normal_form.md §3.4; facts_listing.md
# §4.1.2) on witnesses whose values are an INDEPENDENT model's
# (docs/dev/lanes/altbuild_evidence/p2_model.py, CaseFolding.txt and UTF-8
# alone: ci-moskva and the Kelvin fold class are in its population; the byte
# row is two strings by hand), plus one witness per decline. A CAT product
# that keeps only the shortest group (S-p) loses ci-moskva's widths 13-15.
ob='a|bb|ccc|dddd|eeeee|ffffff|ggggggg|hhhhhhhh|iiiiiiiii|jjjjjjjjjj|kkkkkkkkkkk'
printf '%s\n' \
    'utf8	(?i)москва	12:[208][156,188][208][158,190][208,209][129,161][208][154,186][208][146,178][208][144,176]|13:[208][156,188][208,225][158,178,190][130,208,209,225][129,161,178,208,209][129,131,161,208][154,186,208][154,186,225][178,208][128,146,178][208][144,176]|14:[208][156,188][208,225][158,178,190][130,225][178,208,209,225][129,131,161,178][131,208][154,186,208][154,186,225][178,208][128,146,178][208][144,176]|15:[208][156,188][225][178][130][225][178][131][208][154,186][225][178][128][208][144,176]' \
    'utf8	(?i)abcdKefgh	9:[65,97][66,98][67,99][68,100][75,107][69,101][70,102][71,103][72,104]|11:[65,97][66,98][67,99][68,100][226][132][170][69,101][70,102][71,103][72,104]' \
    'utf8	a|é|日|😀	1:[97]|2:[195][169]|3:[230][151][165]|4:[240][159][152][128]' \
    'byte	a(?:bc|d)e	3:[97][100][101]|4:[97][98][99][101]' \
    'byte	abc	decline:one-group' \
    'byte	x.*y	decline:not-fixed-width' \
    "byte	$ob	decline:over-bound" > "$WORKDIR/pw"
npw=0; pwbad=""
: > "$WORKDIR/pwhy"
while IFS=$'\t' read -r enc pat want; do
    npw=$((npw + 1))
    case "$want" in decline:*) echo "$want" >> "$WORKDIR/pwhy" ;; esac
    if ! "$TIMEOUT_BIN" 120 "$PCREC" --features all -e "$enc" --emit-facts --pattern "$pat" > "$WORKDIR/pw.l" 2> "$WORKDIR/pw.err"; then
        pwbad="$pwbad $enc '$pat': refused ($(head -1 "$WORKDIR/pw.err"));"; continue
    fi
    sect "$WORKDIR/pw.l" facts > "$WORKDIR/pw.f"
    prow="$(grep -F "$(printf 'fact=req_pieces\t')" "$WORKDIR/pw.f")"
    case "$(col status <<< "$prow")" in
        derived)  got="$(col value <<< "$prow")" ;;
        declined) got="$(col why <<< "$prow")" ;;
        *)        got="[$(col status <<< "$prow")/$(col why <<< "$prow")]" ;;
    esac
    [ "$got" = "$want" ] || pwbad="$pwbad $enc '$pat': req_pieces [$got], the model's [$want];"
done < "$WORKDIR/pw"
npwhy="$(LC_ALL=C sort -u "$WORKDIR/pwhy" | wc -l | tr -d ' ')"
echo "REACH: $npw [RUN-POS-SET] piece witness(es), $npwhy of 3 req_pieces decline(s) witnessed"
if [ "$npw" -eq 0 ] || [ "$npwhy" -ne 3 ]; then
    bad "[facts-pieces] the witness table reaches $npwhy of the 3 declines — the check is vacuous where it is short"
elif [ -n "$pwbad" ]; then
    bad "[facts-pieces] req_pieces disagrees with the model:$pwbad"
else
    ok "[facts-pieces] $npw witnesses list req_pieces exactly as the independent model gives it (all 3 declines)"
fi

# [REQ-EMPTYCAT] span_arms E1 (§3.7): THE WALK'S RESTORED ARM and its
# `harness:` token (facts_listing.md §4.1.3¶4a). Through build/pcrec-harness
# alone (the lever is not a caller's): under the `empty` arm the walk runs T2
# row 1's old form, so the witness's run is cut in two again, and the walk
# facts the arm can change (walk_arms.def) plus every fact derived from them
# name the arm; a fact it cannot change (`req_set`) keeps its plain why; the
# default build lists the unit's run and no token; an unknown arm is refused.
# The value under the lever is what shows the arm ACTS (a lever the walk
# ignored lists the token over the new run, S1907); the derived rows show the
# token travels along the asks (S1908). Expectations by hand from T2 (`(?:\b)*`
# is the unit, so the default joins `abcd` and `efgh`) and the run choice's
# rows (req.c `rn_choice_rows`): the cut halves tie on information, and the
# builtin prior's rarer scan byte breaks it, `b` (9886 ppm) over `g` (13375),
# so the old form keeps `abcd`; under utf8 (NONE) the nearer `abcd` wins.
# `req_whole_run` is DERIVED (it reads the prior), so its why is the rule.
HBIN="$BIN_DIR/pcrec-harness"
AP='abcd(?:\b)*efgh'
abad=""
arow() { grep -F "$(printf 'fact=%s\t' "$1")" "$2"; }
if [ ! -x "$HBIN" ]; then
    abad=" $HBIN is missing (make builds it);"
elif ! "$TIMEOUT_BIN" 120 "$PCREC" --features all --emit-facts --pattern "$AP" > "$WORKDIR/ad.l" 2> "$WORKDIR/ad.err" ||
     ! "$TIMEOUT_BIN" 120 "$HBIN" --features all --harness=restore=empty --emit-facts --pattern "$AP" > "$WORKDIR/ar.l" 2> "$WORKDIR/ar.err"; then
    abad=" '$AP' refused ($(head -1 "$WORKDIR/ad.err" "$WORKDIR/ar.err" 2>/dev/null | tr '\n' ' '));"
else
    sect "$WORKDIR/ad.l" facts | grep -F "$(printf 'encoding=byte\t')" > "$WORKDIR/ad.f"
    sect "$WORKDIR/ar.l" facts | grep -F "$(printf 'encoding=byte\t')" > "$WORKDIR/ar.f"
    printf '%s\n' \
        'ad	req_whole_run	6162636465666768	rate:builtin-prior' \
        'ar	req_whole_run	61626364	harness:empty' \
        'ar	req_byte	-	harness:empty' \
        'ar	req_pieces	-	harness:empty' \
        'ar	req_set	-	' > "$WORKDIR/aw"
    while IFS=$'\t' read -r side fact wval wwhy; do
        r="$(arow "$fact" "$WORKDIR/$side.f")"
        gval="$(col value <<< "$r")"; gwhy="$(col why <<< "$r")"
        [ "$wval" = "-" ] || [ "$gval" = "$wval" ] || abad="$abad $side $fact value [$gval], want [$wval];"
        [ "$gwhy" = "$wwhy" ] || abad="$abad $side $fact why [$gwhy], want [$wwhy];"
    done < "$WORKDIR/aw"
    grep -qF 'harness:' "$WORKDIR/ad.f" && abad="$abad the default build lists a harness: token;"
    if "$TIMEOUT_BIN" 60 "$HBIN" --harness=restore=empty+nosuch --emit-facts --pattern "$AP" > /dev/null 2>&1; then
        abad="$abad an unknown arm ('nosuch') was accepted;"
    fi
    # The error names the bad arm alone, not the rest of the list.
    "$TIMEOUT_BIN" 60 "$HBIN" --harness=restore=bogus+empty --emit-facts --pattern "$AP" 2>&1 > /dev/null |
        grep -qF "(no arm 'bogus')" || abad="$abad the refusal does not name the bad arm alone;"
    "$TIMEOUT_BIN" 60 "$HBIN" --harness=restore=emp --emit-facts --pattern "$AP" > /dev/null 2>&1 &&
        abad="$abad a prefix of an arm ('emp') was accepted;"
    # CHECK-2/3: the lever's reach on the ARTIFACT (not only the listing), on
    # another encoding, on the m>=1 half of row 1 (default and lever), and on
    # a SPLIT artifact, whose compound part must take the same arms
    # (compound.c's part compile; the parent's stamp alone would stay green
    # with a half-restored artifact). Hand values from T2: a width-0 body
    # joins its neighbours at any m, and the old form is the gap (m=0) or the
    # best-only copy (m>=1); its equal halves go to the rarer scan byte (`b`
    # over `g`, `b` over `c`) or, under utf8's NONE, to the nearer. The `rep`
    # arm rides the same part path: `xy(?:ab){2}zw` in the part restores to
    # its best-only copy, whose three 2-byte runs go to the rarest, `zw`; and
    # E2's `zero` arm: `abcd\Befgh` in the part restores to the cut, whose
    # equal halves go to the rarer scan byte, `abcd`.
    # tag, encoding, pattern, arm?, RX_REQ_RUN-line prefix (RX_ top, RX__Q_ part)
    printf '%s\n' \
        'RX_REQ_RUN	byte	abcd(?:\b)*efgh	empty	61626364' \
        'RX_REQ_RUN	byte	abcd(?:\b)*efgh	-	6162636465666768' \
        'RX_REQ_RUN	utf8	abcd(?:\b)*efgh	empty	61626364' \
        'RX_REQ_RUN	utf8	abcd(?:\b)*efgh	-	6162636465666768' \
        'RX_REQ_RUN	byte	ab(?:\B){3}cd	-	61626364' \
        'RX_REQ_RUN	byte	ab(?:\B){3}cd	empty	6162' \
        'RX_REQ_RUN	byte	abcd(?:)+efgh	-	6162636465666768' \
        'RX_REQ_RUN	byte	abcd(?:)+efgh	empty	61626364' \
        'RX__Q_REQ_RUN	byte	^a|abcd(?:\b)*efgh$	-	6162636465666768' \
        'RX__Q_REQ_RUN	byte	^a|abcd(?:\b)*efgh$	empty	61626364' \
        'RX__Q_REQ_RUN	byte	^a|abcd\Befgh$	-	6162636465666768' \
        'RX__Q_REQ_RUN	byte	^a|abcd\Befgh$	zero	61626364' \
        'RX__Q_REQ_RUN	byte	^a|xy(?:ab){2}zw$	-	7879616261627a77' \
        'RX__Q_REQ_RUN	byte	^a|xy(?:ab){2}zw$	rep	7a77' > "$WORKDIR/ac"
    nac=0
    while IFS=$'\t' read -r mac enc pat arm want; do
        nac=$((nac + 1)); larm=(); [ "$arm" = "-" ] || larm=("--harness=restore=$arm")
        if ! "$TIMEOUT_BIN" 120 "$HBIN" --features all -e "$enc" "${larm[@]}" -p rx --emit-main -o "$WORKDIR/ac.c" --pattern "$pat" > /dev/null 2> "$WORKDIR/ac.err"; then
            abad="$abad '$pat' [$enc/$arm] refused ($(head -1 "$WORKDIR/ac.err"));"; continue
        fi
        # the run's bytes only: since R-38 K38-2 the `@` is the searching
        # site's (span_runs_sheet.md §4.1's table), not the arm's to move
        got="$(sed -n "s/^#define $mac \"\(.*\)\"\$/\1/p" "$WORKDIR/ac.c" | head -1 | sed 's/@[0-9]*//')"
        [ "$got" = "$want" ] || abad="$abad '$pat' [$enc/$arm] $mac [$got], want [$want];"
    done < "$WORKDIR/ac"
    echo "REACH: $nac restored-arm artifact cells (top, utf8, m>=1, split part under empty and rep)"
fi
# span_arms E2: the `zero` arm runs T3's rows E-4 and E-5 in today's form
# (the CUT), so a witness holding one node of each (`\B`, E-4; a positive
# lookbehind, E-5) lists today's run `xyz` again under it, where the default
# joins all seven bytes across both. A row that ignored the arm lists all seven
# bytes `78797a61626364` (E-4's, S1928) or `78797a6162` (E-5's) instead. Expectations by hand from T3.
ZP='xyz(?<=yz)ab\Bcd'
if [ -x "$HBIN" ] && [ -z "$abad" ]; then
    if ! "$TIMEOUT_BIN" 120 "$PCREC" --features all --emit-facts --pattern "$ZP" > "$WORKDIR/zd.l" 2> "$WORKDIR/zd.err" ||
       ! "$TIMEOUT_BIN" 120 "$HBIN" --features all --harness=restore=zero --emit-facts --pattern "$ZP" > "$WORKDIR/zr.l" 2> "$WORKDIR/zr.err"; then
        abad="$abad '$ZP' refused ($(head -1 "$WORKDIR/zd.err" "$WORKDIR/zr.err" 2>/dev/null | tr '\n' ' '));"
    else
        sect "$WORKDIR/zd.l" facts | grep -F "$(printf 'encoding=byte\t')" > "$WORKDIR/zd.f"
        sect "$WORKDIR/zr.l" facts | grep -F "$(printf 'encoding=byte\t')" > "$WORKDIR/zr.f"
        printf '%s\n' \
            'zd	req_whole_run	78797a61626364	rate:builtin-prior' \
            'zr	req_whole_run	78797a	harness:zero' \
            'zr	req_byte	-	harness:zero' \
            'zr	req_pieces	-	harness:zero' \
            'zr	req_set	-	' > "$WORKDIR/zw"
        while IFS=$'\t' read -r side fact wval wwhy; do
            r="$(arow "$fact" "$WORKDIR/$side.f")"
            gval="$(col value <<< "$r")"; gwhy="$(col why <<< "$r")"
            [ "$wval" = "-" ] || [ "$gval" = "$wval" ] || abad="$abad $side $fact value [$gval], want [$wval];"
            [ "$gwhy" = "$wwhy" ] || abad="$abad $side $fact why [$gwhy], want [$wwhy];"
        done < "$WORKDIR/zw"
        grep -qF 'harness:' "$WORKDIR/zd.f" && abad="$abad the default build lists a harness: token for '$ZP';"
    fi
fi
# span_arms E2 took T3 row E-1 (an `A_EMPTY` node, the unit) and restores it
# under the `empty` arm: `abcd()efgh` lists the cut's halves again under it,
# whose equal information goes to the rarer scan byte (R1's `rn_choice_rows`),
# `abcd`, and the default joins all eight bytes (S1929: E-1's row ignores the
# arm).
EP='abcd()efgh'
if [ -x "$HBIN" ] && [ -z "$abad" ]; then
    if ! "$TIMEOUT_BIN" 120 "$PCREC" --features all --emit-facts --pattern "$EP" > "$WORKDIR/ed.l" 2> /dev/null ||
       ! "$TIMEOUT_BIN" 120 "$HBIN" --features all --harness=restore=empty --emit-facts --pattern "$EP" > "$WORKDIR/er.l" 2> /dev/null; then
        abad="$abad '$EP' refused;"
    else
        sect "$WORKDIR/ed.l" facts | grep -F "$(printf 'encoding=byte\t')" > "$WORKDIR/ed.f"
        sect "$WORKDIR/er.l" facts | grep -F "$(printf 'encoding=byte\t')" > "$WORKDIR/er.f"
        printf '%s\n' \
            'ed	req_whole_run	6162636465666768	rate:builtin-prior' \
            'er	req_whole_run	61626364	harness:empty' > "$WORKDIR/ew"
        while IFS=$'\t' read -r side fact wval wwhy; do
            r="$(arow "$fact" "$WORKDIR/$side.f")"
            gval="$(col value <<< "$r")"; gwhy="$(col why <<< "$r")"
            [ "$gval" = "$wval" ] || abad="$abad $side $fact value [$gval], want [$wval];"
            [ "$gwhy" = "$wwhy" ] || abad="$abad $side $fact why [$gwhy], want [$wwhy];"
        done < "$WORKDIR/ew"
    fi
fi
echo "REACH: 3 restored-arm witnesses ('$AP' empty, '$EP' empty, '$ZP' zero), $(cat "$WORKDIR/aw" "$WORKDIR/ew" "$WORKDIR/zw" 2>/dev/null | wc -l) listing cells"
if [ -n "$abad" ]; then
    bad "[facts-arm] the walk's restored arm or its harness: token is wrong:$abad"
else
    ok "[facts-arm] under --harness=restore=empty the walk runs T2 row 1's and T3 E-1's old forms, under restore=zero T3's E-4/E-5 cut, and their facts name the arm; the default lists the units' runs"
fi

# [REPEAT-RUN] span_arms R1 (§3, T2 rows 2-3): A REPEAT IS ITS COPIES, on the
# listing. Expectations by hand from T2 and the description's cat:
#   - `xy(?:ab){2}zw` is `xyababzw`; under `--harness=restore=rep` (build/
#     pcrec-harness) today's best-only copy again, whose three 2-byte runs
#     `xy`, `ab`, `zw` tie on information and go to the rarest scan byte
#     (`rn_choice_rows`: `z`, 498 ppm), with the token on the walk facts and
#     none on `req_set` (S1921: a row that the arm no longer passes over keeps
#     the new run); the same for T2 row 3, `xy(?:ab){1,2}zw` (`abzw` by
#     default, the `xyab`/`abzw` tie to the rarer `z`; `zw` restored; S1922);
#   - a body that is not `all` saturates at TWO copies (`rr_pow_count`):
#     `(?:ab[0-9]cd){3}` is the join `cdab` (S1923 stops at one copy: `ab`);
#   - W-R5: `(?:abc){20}` unrolls ceil(32/3) = 11 copies, so the run is the
#     storage bound's 32 positions, (abc)^10 ab (S1918 stops one copy short:
#     30 positions, sound, seen only here);
#   - the pieces are the body's copies for an EXACT repeat only:
#     `(?:a|bc){2}` is three widths (2 `aa`, 3 the hull of `abc` and `bca`,
#     4 `bcbc`); `(?:ab){20}(?:c|de)` keeps each group's last 32 positions at
#     widths 41 and 42 (S1920: the saturated copies add no width); a variable
#     repeat stays `not-fixed-width`.
RP='xy(?:ab){2}zw'
rbad=""; nrw=0
rget() { # rget <bin> <arm-or-empty> <pattern> <fact> -> "value<TAB>why" (byte)
    local arm=()
    [ -n "$2" ] && arm=("--harness=restore=$2")
    "$TIMEOUT_BIN" 120 "$1" --features all "${arm[@]}" --emit-facts --pattern "$3" > "$WORKDIR/rp.l" 2> "$WORKDIR/rp.err" ||
        { printf 'REFUSED\t%s\n' "$(head -1 "$WORKDIR/rp.err")"; return; }
    sect "$WORKDIR/rp.l" facts | grep -F "$(printf 'encoding=byte\t')" | arow "$4" /dev/stdin > "$WORKDIR/rp.r"
    printf '%s\t%s\n' "$(col value < "$WORKDIR/rp.r")" "$(col why < "$WORKDIR/rp.r")"
}
if [ ! -x "$HBIN" ]; then
    rbad=" $HBIN is missing (make builds it);"
else
    while IFS=$'\t' read -r bin arm pat fact want wwhy; do
        nrw=$((nrw + 1))
        b="$PCREC"
        [ "$bin" = h ] && b="$HBIN"
        [ "$arm" = - ] && arm=""
        got="$(rget "$b" "$arm" "$pat" "$fact")"
        gval="${got%%$'\t'*}"; gwhy="${got#*$'\t'}"
        [ "$wwhy" = - ] && wwhy=""
        [ "$gval" = "$want" ] || rbad="$rbad '$pat'${arm:+ restore=$arm} $fact value [$gval], want [$want];"
        [ "$gwhy" = "$wwhy" ] || rbad="$rbad '$pat'${arm:+ restore=$arm} $fact why [$gwhy], want [$wwhy];"
    done <<RPEOF
p	-	$RP	req_whole_run	7879616261627a77	rate:builtin-prior
h	rep	$RP	req_whole_run	7a77	harness:rep
h	rep	$RP	req_pieces	none	harness:rep
h	rep	$RP	req_set	97,98,119,120,121,122	-
p	-	(?:abc){20}	req_whole_run	6162636162636162636162636162636162636162636162636162636162636162	rate:builtin-prior
p	-	xy(?:ab){1,2}zw	req_whole_run	61627a77	rate:builtin-prior
h	rep	xy(?:ab){1,2}zw	req_whole_run	7a77	harness:rep
p	-	(?:ab[0-9]cd){3}	req_whole_run	63646162	rate:builtin-prior
p	-	(?:a|bc){2}	req_pieces	2:[97][97]|3:[97,98][98,99][97,99]|4:[98][99][98][99]	-
h	rep	(?:a|bc){2}	req_pieces	none	harness:rep
p	-	(?:ab){20}(?:c|de)	req_pieces	41@9:[98][97][98][97][98][97][98][97][98][97][98][97][98][97][98][97][98][97][98][97][98][97][98][97][98][97][98][97][98][97][98][99]|42@10:[97][98][97][98][97][98][97][98][97][98][97][98][97][98][97][98][97][98][97][98][97][98][97][98][97][98][97][98][97][98][100][101]	-
p	-	xy(?:ab){1,2}zw	req_pieces	none	decline:not-fixed-width
RPEOF
fi
echo "REACH: $nrw [REPEAT-RUN] listing cell(s)"
if [ "$nrw" -eq 0 ] || [ -n "$rbad" ]; then
    bad "[facts-rep] the power arm's listing is wrong:${rbad:- no cell was read}"
else
    ok "[facts-rep] $nrw cells: an exact repeat lists its copies (run and pieces), the storage bound's 32 positions at W-R5, and --harness=restore=rep the old form"
fi

# [REPEAT-RUN] the lever's REACH on a `.rxt` FILE compile (sar1mrg pairb,
# 2026-11-10): `--harness=restore=` reached `--pattern` but not
# `compile_sources`, so every file-path sweep under a restored arm ran the new
# form (vacuous). `(a{3,5}){3,6}` is an R1 mover: by default the run is
# emitted; restored (old form) it is `dominated`. The FILE compile must answer
# as the `--pattern` compile does, under the arm and without it.
if [ ! -x "$HBIN" ]; then
    bad "[facts-rep-file] $HBIN is missing (make builds it)"
else
    fbad=""
    printf 'pattern (a{3,5}){3,6}\nm "aaaaaaaaa" 0 9\n' > "$WORKDIR/fr.rxt"
    for arm in "" "--harness=restore=rep"; do
        mkdir -p "$WORKDIR/fr.d"; rm -f "$WORKDIR/fr.d"/*
        "$TIMEOUT_BIN" 120 "$HBIN" --features all $arm "$WORKDIR/fr.rxt" -o "$WORKDIR/fr.d" > /dev/null 2>&1 || fbad="$fbad file compile ${arm:-default} refused;"
        "$TIMEOUT_BIN" 120 "$HBIN" --features all $arm -p rx --emit-main -o "$WORKDIR/fr.p.c" --pattern '(a{3,5}){3,6}' > /dev/null 2>&1 || fbad="$fbad pattern compile ${arm:-default} refused;"
        fl="$(grep -hE 'define RX_REQ_(RUN|WHY) ' "$WORKDIR/fr.d"/*.c | tr '\n' ' ')"
        pl="$(grep -hE 'define RX_REQ_(RUN|WHY) ' "$WORKDIR/fr.p.c" | tr '\n' ' ')"
        [ -n "$fl" ] && [ "$fl" = "$pl" ] || fbad="$fbad ${arm:-default}: file [$fl] pattern [$pl];"
        case "$arm" in
            "") case "$fl" in (*emitted*) ;; (*) fbad="$fbad default does not emit the run;" ;; esac ;;
            *)  case "$fl" in (*dominated*) ;; (*) fbad="$fbad restore=rep did not restore the old form;" ;; esac ;;
        esac
    done
    if [ -n "$fbad" ]; then
        bad "[facts-rep-file] the harness lever does not reach a .rxt file compile like --pattern:$fbad"
    else
        ok "[facts-rep-file] --harness=restore=rep reaches a .rxt FILE compile as it reaches --pattern (R1 mover, default and restored)"
    fi
fi

# [facts-tie] span arms R1's tie rule has its own restore arm (`restore=tie`,
# src/facts/walk_arms.def): `abcd.efgh` holds two required 4-byte runs of equal
# information. By default the RARER one is stamped (`abcd` on the default
# rate table); restored, the predecessor's choice (the later, `efgh`). Both the
# --pattern compile and a .rxt FILE compile must answer so. (R-38 K38-2: the
# stamp's `@` is the searching site's; this `cover` artifact's window search
# may read a position outside the stamped run, so the `@` is optional here.)
if [ ! -x "$HBIN" ]; then
    bad "[facts-tie] $HBIN is missing (make builds it)"
else
    tbad=""
    printf 'pattern abcd.efgh\nm "abcdXefgh" 0 9\n' > "$WORKDIR/ft.rxt"
    for arm in "" "--harness=restore=tie"; do
        mkdir -p "$WORKDIR/ft.d"; rm -f "$WORKDIR/ft.d"/*
        "$TIMEOUT_BIN" 120 "$HBIN" --features all $arm "$WORKDIR/ft.rxt" -o "$WORKDIR/ft.d" > /dev/null 2>&1 || tbad="$tbad file compile ${arm:-default} refused;"
        "$TIMEOUT_BIN" 120 "$HBIN" --features all $arm -p rx --emit-main -o "$WORKDIR/ft.p.c" --pattern 'abcd.efgh' > /dev/null 2>&1 || tbad="$tbad pattern compile ${arm:-default} refused;"
        fl="$(grep -hE 'define RX_REQ_RUN ' "$WORKDIR/ft.d"/*.c | tr '\n' ' ')"
        pl="$(grep -hE 'define RX_REQ_RUN ' "$WORKDIR/ft.p.c" | tr '\n' ' ')"
        [ -n "$fl" ] && [ "$fl" = "$pl" ] || tbad="$tbad ${arm:-default}: file [$fl] pattern [$pl];"
        case "$arm" in
            "") case "$fl" in (*'"61626364'[@\"]*) ;; (*) tbad="$tbad default does not stamp the rarer run;" ;; esac ;;
            *)  case "$fl" in (*'"65666768'[@\"]*) ;; (*) tbad="$tbad restore=tie did not restore the predecessor's run;" ;; esac ;;
        esac
    done
    if [ -n "$tbad" ]; then
        bad "[facts-tie] the tie arm is wrong:$tbad"
    else
        ok "[facts-tie] --harness=restore=tie reaches --pattern and a .rxt FILE compile alike (abcd.efgh: rarer run by default, the predecessor's restored)"
    fi
fi

# [facts-ahead] [RUN-POS-SET] stage 3 and stage 2a rule (1), AHEAD of the
# landing that brings memfn Part D (rps3b, manager ruling 2026-11-13): two
# test-only levers of build/pcrec-harness walk in the landing's form.
# `run-pos-sets` is the stage-3 DOMAIN (a run position any set of at most
# 128 members, no cube clause); `alt-union-run` is alt_normal_form.md §6's
# `rr_alt` row 1 (every branch `all`, equal untruncated width: the
# alternation is `all`, its run the per-position union). The default build
# is the interim domain with row 1 off, so each lever cell has its default
# twin. Every cell is one today's kit ACCEPTS (the `--emit-facts` compile is
# a real compile and the kit refuses a run whose derived find is not at its
# scan position, K-1); the cells it refuses today go green only after the
# landing and are listed in docs/dev/lanes/rps3b_report.md, OWED. Rule (1)'s
# cells deny altcls (bits 10, 11), which otherwise factors the alternation
# into a class before the walk sees it. Expectations by hand from req.c's
# rules (the memo's §3 table and alt_normal_form §5 stage 2a's predicted
# movers); `xy(?:ab|abc)zw` is S-c, the unequal-width control that row 1
# must never claim.
abad=""; nah=0
aget() { # aget <levers> <denies> <enc> <pattern> -> the req_whole_run value
    local lv=() dn=()
    case "$1" in (*sets*) lv+=(--harness=run-pos-sets) ;; esac
    case "$1" in (*alt*) lv+=(--harness=alt-union-run) ;; esac
    [ "$2" = noaltcls ] && dn=(-fno-altcls-merge -fno-altcls-factor)
    "$TIMEOUT_BIN" 120 "$HBIN" --features all "${lv[@]}" "${dn[@]}" -e "$3" --emit-facts --pattern "$4" > "$WORKDIR/ah.l" 2> "$WORKDIR/ah.err" ||
        { printf 'REFUSED(%s)' "$(head -1 "$WORKDIR/ah.err")"; return; }
    sect "$WORKDIR/ah.l" facts | grep -F "$(printf 'encoding=%s\t' "$3")" | arow req_whole_run /dev/stdin | col value
}
if [ ! -x "$HBIN" ]; then
    abad=" $HBIN is missing (make builds it);"
else
    while IFS=$'\t' read -r lv dn enc pat want; do
        nah=$((nah + 1))
        got="$(aget "$lv" "$dn" "$enc" "$pat")"
        [ "$got" = "$want" ] || abad="$abad [$lv $dn $enc] '$pat' req_whole_run [$got], want [$want];"
    done <<'AHEOF'
-	-	byte	\d{3}-\d{4}	none
sets	-	byte	\d{3}-\d{4}	[30-39][30-39][30-39]2d[30-39][30-39][30-39][30-39]
-	-	byte	[a-z]{8}	none
sets	-	byte	[a-z]{8}	[61-7a][61-7a][61-7a][61-7a][61-7a][61-7a][61-7a][61-7a]
-	-	byte	xy/users\d+	78792f7573657273
sets	-	byte	xy/users\d+	78792f7573657273[30-39]
sets	-	byte	\w+@example\.com	[30-3941-5a5f61-7a]406578616d706c652e636f6d
sets	-	byte	GET /[a-z]+ HTTP	[61-7a]2048545450
-	-	utf8	(?i)xyzłw	58595ac5/dfdfdfff
sets	-	utf8	(?i)xyzłw	[5878][5979][5a7a]c5[8182][5777]
-	noaltcls	byte	abcd(?:ab|ab)efgh	616263646162
alt	noaltcls	byte	abcd(?:ab|ab)efgh	61626364616265666768
-	noaltcls	byte	(?:ab|Ab)(?:cd|Cd)(?:ef|Ef)	41624364/dfffdfff
alt	noaltcls	byte	(?:ab|Ab)(?:cd|Cd)(?:ef|Ef)	416243644566/dfffdfffdfff
-	noaltcls	byte	xy(?:ab|ac)zw	61627a77/fffeffff
alt	noaltcls	byte	xy(?:ab|ac)zw	787961627a77/fffffffeffff
alt	noaltcls	byte	xy(?:abc|abd)zw	78796162
sets	noaltcls	byte	xy(?:abc|abd)zw	6162[6364]7a77
sets+alt	noaltcls	byte	xy(?:abc|abd)zw	78796162[6364]7a77
sets+alt	noaltcls	byte	xy(?:ab|abc)zw	78796162
AHEOF
fi
echo "REACH: $nah [facts-ahead] listing cell(s)"
if [ "$nah" -eq 0 ] || [ -n "$abad" ]; then
    bad "[facts-ahead] the landing-form levers list the wrong run:${abad:- no cell was read}"
else
    ok "[facts-ahead] $nah cells: run-pos-sets walks the stage-3 domain, alt-union-run makes an equal-width all-branch alternation all (and never an unequal one), each beside its default twin"
fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
