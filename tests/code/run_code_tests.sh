#!/usr/bin/env bash
# tests/code/run_code_tests.sh — module `code-c` ([INLINE-C] stage 2;
# docs/spec/match_api.md §11.9-§11.10, docs/design/inline_c.md §9.1):
# `make test-code`.
#
# ARMS:
#   (1) the corpus: tests/harness/run.sh over this directory (the grant and
#       the user source through harness.manifest; T2 and the fragment rule
#       through t2/ and frag/, whose blocks expect pcrec's refusal);
#   (2) the oracle: verify_code.py, every corpus cell against libpcre2
#       running the same segment text;
#   (3) the refusals: the grant, `features`, the `pcrec` line, an unknown
#       language or attribute, bidi and control bytes, reached code, the
#       `code-header` operand;
#   (4) the entry-point table (inline_c.md §5.9): one row per CLI mode,
#       ENUMERATED from cli/main.c's CLI_MODE_TABLE (a mode with no row
#       fails), plus the writers that are not modes, plus the library
#       (lib_check.c);
#   (5) diagnostics land on the user's line (DT-3.3): a segment's error at
#       its .rxt line and column, a `pattern-esc` segment at its opener's
#       line, `--pattern` at "<command line>", a missing header at its
#       `code-header` line; the `.h` names no user header (DT-3.4);
#   (6) header placement (S-IC30's witness): a header that poisons what a
#       matcher uses compiles, because it comes after the matcher;
#   (7) the live-macro check (§3.2) over a corpus of artifacts;
#   (8) the driver checks: DT-4.1 inline (n >= 1, match [0,3)), a check
#       returning 1 and a segment falling off its end (both trap);
#   (9) the span helpers (span_check.c);
#  (10) the call form (match_api.md §11.2¶1a): no indirect call through a
#       binding in a unity build, an embedded segment, or an artifact used
#       as a callout, read from the assembly; a separately compiled binding
#       as the reader's control;
#  (11) the inline-mode measurement card builds and runs (--smoke).
# Arm 2 SKIPS LOUDLY when libpcre2 is absent (PC-3's shape).
#
# Env: PCREC, CC, GENCFLAGS (the harness's own), LIBA.
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
LIBA="${LIBA:-$ROOT_DIR/build/libpcrec.a}"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra}"

pass=0; fail=0; skip=0
ok()   { echo "PASS: $1"; pass=$((pass + 1)); }
bad()  { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
note() { echo "SKIP: $1" >&2; skip=$((skip + 1)); }

WORK="$(mktemp -d "${TMPDIR:-/tmp}/code_tests.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
pc() { "$TIMEOUT_BIN" 60 "$PCREC" "$@"; }
SEG='a(?C`c: return RX_PASS;`)b'

# ---- arm 1: the corpus ----------------------------------------------------
echo "== [INLINE-C] the code-c corpus =="
if PCREC="$PCREC" bash "$ROOT_DIR/tests/harness/run.sh" "$SCRIPT_DIR/"; then
    ok "the tests/code/ corpus: every case answers what its .rxt file says"
else
    bad "the tests/code/ corpus has failing cases — see above"
fi

# ---- arm 2: the corpus oracle ----------------------------------------------
echo
echo "== [INLINE-C] the corpus against libpcre2 =="
PCREC="$PCREC" CC="$CC" TMPDIR="$WORK" python3 "$SCRIPT_DIR/verify_code.py" "$SCRIPT_DIR"/*.rxt
case $? in
    0) ok "libpcre2, running the same segment text, agrees with every cell in tests/code/" ;;
    3) note "libpcre2 is unavailable: the corpus is scored against its own file only" ;;
    *) bad "libpcre2 disagrees with the corpus, or the sweep checked nothing" ;;
esac

# ---- arm 3: the refusals -----------------------------------------------------
echo
echo "== [INLINE-C] the refusals =="
# refuse WHAT | expected text | pcrec arguments (eval'd; $SEG is the segment)
refuse() {
    local what="$1" want="$2"; shift 2
    local out="$WORK/r.c" err
    rm -f "$out" "${out%.c}.h"
    err="$(pc "$@" 2>&1 >/dev/null)"
    if [ $? -eq 0 ]; then
        bad "$what: pcrec ACCEPTED it"
    elif [[ "$err" != *"$want"* ]]; then
        bad "$what: refused, but without '$want': $err"
    elif [ -e "$out" ] || [ -e "${out%.c}.h" ]; then
        bad "$what: refused, but wrote $out"
    else
        ok "$what"
    fi
}
R="$WORK/r.c"
refuse "no grant: a segment is refused by name" "--allow-code=c" -o "$R" --pattern "$SEG"
refuse "--features all does not grant code (S-IC28)" "--allow-code=c" --features all -o "$R" --pattern "$SEG"
refuse "--features code-c is refused" "module 'code-c' is code" --features code-c -o "$R" --pattern "$SEG"
refuse "--allow-code with an unknown language" "py" --allow-code=py -o "$R" --pattern "$SEG"
refuse "an unknown attribute is refused (S-IC8)" "bogus" --allow-code=c -o "$R" --pattern 'a(?C`c,bogus: return RX_PASS;`)b'
refuse "a bidi control in a segment is refused and named" "U+202E" --allow-code=c -o "$R" \
    --pattern "$(printf 'a(?C`c: return RX_PASS; /* \342\200\256 */`)b')"
refuse "a zero-width space in a segment is refused" "U+200B" --allow-code=c -o "$R" \
    --pattern "$(printf 'a(?C`c: return RX_PASS;\342\200\213`)b')"
refuse "a C0 control byte in a segment is refused" "U+0001" --allow-code=c -o "$R" \
    --pattern "$(printf 'a(?C`c: return RX_PASS;\001`)b')"
# F1 (review 2026-10-27-r1-ic2): the refused set is the UCD's Bidi_Control and
# Default_Ignorable_Code_Point, not a typed list; one member of each beyond
# the old list, at each UTF-8 length, plus the three Unicode line ends. U+3164
# is the exploit's: `int ok<U+3164> = 1; int ok = 0;` reads as one name.
for cpw in '\330\234|U+061C' '\343\205\244|U+3164' '\302\255|U+00AD' \
           '\363\240\201\201|U+E0041' '\342\200\250|U+2028' '\302\205|U+0085'; do
    refuse "the UCD-derived refusal set holds ${cpw#*|}" "${cpw#*|}" --allow-code=c -o "$R" \
        --pattern "$(printf "a(?C\`c: int ok${cpw%|*} = 1; return RX_PASS;\`)b")"
done
# F2: a lone CR, a VT and a FF are line breaks to a terminal that gcc reads
# otherwise (`// x<CR>return RX_FAIL;` compiled the hidden statement).
for cw in '\r|U+000D' '\v|U+000B' '\f|U+000C'; do
    refuse "a segment's ${cw#*|} is refused (reader and compiler split lines differently)" "${cw#*|}" \
        --allow-code=c -o "$R" --pattern "$(printf "a(?C\`c: // x${cw%|*}return RX_FAIL;\n return RX_PASS;\`)b")"
done
if pc --allow-code=c -o "$R" --pattern "$(printf 'a(?C`c: /* caf\303\251 */\r\n return RX_PASS;`)b')" 2> "$WORK/r.log"; then
    ok "CR LF and an ordinary non-ASCII character are accepted"
else
    bad "CR LF or an ordinary non-ASCII character was refused: $(cat "$WORK/r.log")"
fi
refuse "a malformed --code-header operand is refused" "header" --allow-code=c \
    --code-header 'c:"octet.h' -o "$R" --pattern "$SEG"
refuse "--code-header for an unknown language is refused" "language" --allow-code=c \
    --code-header 'py:"x.h"' -o "$R" --pattern "$SEG"
refuse "a code-header with no grant is refused like a segment" "--allow-code" \
    --code-header 'c:"octet.h"' -o "$R" --pattern 'ab'

# .rxt files: a block's `features all`, a config's `features all`, a `pcrec`
# line's --allow-code, a block's `features code-c`, and REACHED code.
D="$WORK/rxt"; mkdir -p "$D"
printf 'pattern %s\nfeatures all\n' "$SEG" > "$D/blk_all.rxt"
printf 'config k\n  features all\ntarget kk = cb with k\n\npattern %s\nname cb\n' "$SEG" > "$D/cfg_all.rxt"
printf 'config k\n  pcrec --allow-code=c\ntarget kk = cb with k\n\npattern %s\nname cb\n' "$SEG" > "$D/cfg_pcrec.rxt"
printf 'pattern %s\nfeatures code-c\n' "$SEG" > "$D/blk_codec.rxt"
printf 'pattern q(?C`c: return RX_PASS;`)r\nname lq\n' > "$D/lib_code.rxt"
printf 'lib "lib_code.rxt"\ntarget = ub\n\npattern z(?&lq)\nname ub\n' > "$D/reach.rxt"
refuse "a block's 'features all' does not grant code" "--allow-code=c" -o "$R" "$D/blk_all.rxt"
refuse "a config's 'features all' does not grant code" "--allow-code=c" -o "$WORK/rdir" "$D/cfg_all.rxt"
refuse "a config's pcrec line cannot carry --allow-code" "--allow-code" --allow-code=c -o "$WORK/rdir" "$D/cfg_pcrec.rxt"
refuse "a block's 'features code-c' is refused" "code-c" --allow-code=c -o "$R" "$D/blk_codec.rxt"
refuse "reached code (a lib definition's segment) is refused" "lib_code.rxt:1 is not allowed" --allow-code=c --features all -o "$WORK/rdir" "$D/reach.rxt"
[ -e "$WORK/rdir" ] && bad "a refused FILE target wrote $WORK/rdir"

# ---- arm 4: the entry-point table ---------------------------------------------
echo
echo "== [INLINE-C] the entry-point table (inline_c.md 5.9) =="
F="$WORK/ep"; mkdir -p "$F"
printf 'pattern %s\nm "ab" 0 2\n' "$SEG" > "$F/one.rxt"
# The DESCRIBE class parses code without the grant and prints no code text
# unescaped: a segment carrying a newline must not reach the output as a line.
NLSEG='"a(?C`c: int z = 0;\nNLMARK; return RX_PASS;`)b"'
# mode spelling | class (the arguments: ep_args)
EP_ROWS='--list-syntax|takes
--list-definitions|takes
--list-verbs|takes
--list-families|takes
--list-axes|takes
--list-limits|takes
--list-schema|takes
--explain|takes
--count-groups|describe
--emit-ir|describe
--emit-facts|describe
--probe-ask|takes
--list-source|takes
--list-analyses|takes
--list-analysis|takes
--list-measurements|takes
a file operand|writes
--pattern|writes
--pattern-esc|writes
-o -|writes
--emit-main|writes
--trace|writes'
ep_args() {   # ep_args SPELLING -> ARGS
    case "$1" in
        --explain) ARGS=(--explain '(?C') ;;
        --count-groups|--emit-ir|--emit-facts) ARGS=("$1" --pattern-esc --pattern "$NLSEG") ;;
        --probe-ask) ARGS=(--probe-ask claim "$SEG") ;;
        --list-source) ARGS=(--list-source "$F/one.rxt") ;;
        --list-analysis|--list-measurements) ARGS=("$1" default) ;;
        'a file operand') ARGS=(-o "$F/w.c" "$F/one.rxt") ;;
        --pattern) ARGS=(-o "$F/w.c" --pattern "$SEG") ;;
        --pattern-esc) ARGS=(-o "$F/w.c" --pattern-esc --pattern "\"$SEG\"") ;;
        '-o -') ARGS=(-o - --pattern "$SEG") ;;
        --emit-main|--trace) ARGS=("$1" -o "$F/w.c" --pattern "$SEG") ;;
        *) ARGS=("$1") ;;
    esac
}
# Every CLI_MODE_TABLE spelling must have a row (a new mode cannot slip by).
modes="$(sed -n '/^#define CLI_MODE_TABLE(X)/,/^$/p' "$ROOT_DIR/cli/main.c" \
         | grep -oE '"[^"]+"\)' | tr -d '")')"
nmodes=0
while IFS= read -r m; do
    [ -z "$m" ] && continue
    nmodes=$((nmodes + 1))
    printf '%s\n' "$EP_ROWS" | grep -qF -- "$m|" || bad "CLI mode '$m' has no row in the entry-point table"
done <<< "$modes"
[ "$nmodes" -ge 15 ] || bad "only $nmodes CLI modes read from cli/main.c's CLI_MODE_TABLE: the enumeration stopped reaching it"
while IFS='|' read -r spell class; do
    rm -f "$F/w.c" "$F/w.h"
    ep_args "$spell"
    o0="$(pc "${ARGS[@]}" 2>&1)"; r0=$?
    w0=0; [ -e "$F/w.c" ] && w0=1
    o1="$(pc --allow-code=c "${ARGS[@]}" 2>&1)"; r1=$?
    case "$class" in
        writes)
            if [ $r0 -ne 0 ] && [[ "$o0" == *"--allow-code=c"* ]] && [ $w0 -eq 0 ] && [ $r1 -eq 0 ]; then
                ok "entry '$spell' (writes C): refused without the grant, compiles with it"
            else
                bad "entry '$spell' (writes C): without the grant rc=$r0 '${o0:0:200}'; with it rc=$r1 '${o1:0:200}'"
            fi ;;
        describe)
            if [ $r0 -eq 0 ] && [ "$o0" = "$o1" ] && ! printf '%s\n' "$o0" | grep -q '^NLMARK'; then
                ok "entry '$spell' (describes): parses code without the grant, prints no code line"
            else
                bad "entry '$spell' (describes): rc=$r0, same-with-grant=$([ "$o0" = "$o1" ] && echo yes || echo no), output '${o0:0:200}'"
            fi ;;
        takes)
            if [ "$r0" = "$r1" ] && [ "$o0" = "$o1" ]; then
                ok "entry '$spell' (takes no pattern): the grant changes nothing"
            else
                bad "entry '$spell' (takes no pattern): the grant changed the answer (rc $r0 vs $r1)"
            fi ;;
    esac
done <<< "$EP_ROWS"
if [ -f "$LIBA" ] && $CC -O1 -I"$ROOT_DIR/lib" -o "$WORK/lib_check" "$SCRIPT_DIR/lib_check.c" "$LIBA" 2> "$WORK/lib.log"; then
    if "$TIMEOUT_BIN" 60 "$WORK/lib_check"; then
        ok "the library: allow_code is the only door"
    else
        bad "the library's grant check failed (above)"
    fi
else
    bad "lib_check.c did not build against $LIBA: $(head -5 "$WORK/lib.log" 2>/dev/null)"
fi

# ---- arm 5: diagnostics on the user's line (DT-3.3, DT-3.4) ------------------
echo
echo "== [INLINE-C] diagnostics land on the user's line =="
G="$WORK/diag"; mkdir -p "$G"
printf '# DT-3.3\n\npattern ab(?C`c: return undeclared_zz;`)c\n' > "$G/err.rxt"
printf '# DT-3.3\n\npattern-esc "a(?C`c: int x = 1;\\n (void)x;\\n return undeclared_pe;`)"\n' > "$G/pe.rxt"
printf 'code-header c "nothere_dt33.h"\n\npattern %s\n' "$SEG" > "$G/miss.rxt"
diag() {   # diag WHAT EXPECT SRC-FILE-OR-PATTERN...
    local what="$1" want="$2"; shift 2
    rm -f "$G/o.c"
    if ! (cd "$G" && pc --allow-code=c -o o.c "$@" >/dev/null 2>&1); then
        bad "$what: pcrec refused the source"; return
    fi
    local e; e="$(cd "$G" && $CC -c -o o.o o.c 2>&1)"
    # This arm's observable IS a compile error, so a mismatch quotes it with
    # the `file:L:C: error:` shape broken: the mech matrix reads that shape
    # in a log as "the plant does not compile" (NOCOMPILE_ERE), which here
    # would turn a detection into an anomaly.
    if [[ "$e" == *"$want"* ]]; then ok "$what"
    else bad "$what: wanted '$want' in: $(printf '%s' "${e:0:300}" | sed -E 's/: (fatal )?error: /: [cc \1error] /g')"; fi
}
diag "a segment's error names its .rxt line and column" "err.rxt:3:25: error" err.rxt
diag "a pattern-esc segment's error names the opener's line" "pe.rxt:3:" pe.rxt
diag "a --pattern segment's error names <command line>" "<command line>:1:17: error" --pattern 'xy(?C`c: return undeclared_cl;`)'
diag "a missing header is reported at its code-header line" "miss.rxt:1:" miss.rxt
pc --allow-code=c -p geo --code-header 'c:"geoip.h"' -o "$G/geo.c" \
    --pattern '\b(\d{1,3}(?:\.\d{1,3}){3})\b(?C`c: return geo_is_private(RX_CAP_P(1), (size_t)RX_CAP_LEN(1)) ? RX_FAIL : RX_PASS;`)' \
    --features all
if grep -q 'geoip.h' "$G/geo.c" && ! grep -q 'geoip.h' "$G/geo.h"; then
    ok "DT-3.4: the .c includes the user header and the .h does not"
else
    bad "DT-3.4: the user header's #include is not in the .c only"
fi

# ---- arm 6: header placement (S-IC30) -----------------------------------------
echo
echo "== [INLINE-C] code headers come after the matcher =="
H="$WORK/hdr"; mkdir -p "$H"
pc --allow-code=c -p ph --code-header 'c:"poison.h"' -o "$H/ph.c" \
    --pattern 'hello(?C`c: return RX_PASS;`)world|[a-z]+@[a-z]+\.com'
# THE TEXT FIRST: the header's #include must follow the matcher's last
# function (the public search entry's definition). Only then is the compile
# asked, so a misplaced header reads as this check, not as a compile error.
inc_at="$(grep -n '^#include "poison.h"' "$H/ph.c" | head -1 | cut -d: -f1)"
fn_at="$(grep -n '^[a-z].*ph_search(const unsigned char' "$H/ph.c" | tail -1 | cut -d: -f1)"
if ! grep -qE 'memchr|memcmp|memcpy' "$H/ph.c"; then
    bad "the poison witness's matcher uses none of the poisoned names: it cannot reach S-IC30"
elif [ -z "$inc_at" ] || [ -z "$fn_at" ] || [ "$inc_at" -le "$fn_at" ]; then
    bad "the code header's #include (line ${inc_at:-none}) does not follow the matcher (ph_search at line ${fn_at:-none})"
elif $CC $GENCFLAGS -I"$SCRIPT_DIR" -c -o "$H/ph.o" "$H/ph.c" 2> "$H/cc.log"; then
    ok "a header poisoning matcher identifiers compiles: it is emitted after the matcher"
else
    bad "a code header reached the matcher: $(head -3 "$H/cc.log")"
fi

# ---- arm 7: the live-macro check (inline_c.md 3.2) ----------------------------
echo
echo "== [INLINE-C] what is live at the segment block =="
LM="$WORK/live"; mkdir -p "$LM"
MSET='RX_SUBJ RX_LEN RX_POS RX_START RX_CAP_SET RX_CAP_S RX_CAP_E RX_CAP_LEN RX_CAP_P RX_CAP RX_USER'
nart=0; lbad=0
while IFS= read -r pat; do
    [ -z "$pat" ] && continue
    nart=$((nart + 1))
    px="lm$nart"
    if ! pc --allow-code=c --features all -p "$px" -o "$LM/$px.c" --pattern "$pat" 2> "$LM/p.log"; then
        bad "the live-macro corpus pattern '$pat' did not compile: $(cat "$LM/p.log")"; lbad=$((lbad + 1)); continue
    fi
    upx="$(printf '%s' "$px" | tr '[:lower:]' '[:upper:]')"
    # The text up to the first segment's own macro set, and the macros its
    # system includes alone define: the difference is what pcrec left live.
    awk '/^#define RX_SUBJ /{exit} {print}' "$LM/$px.c" > "$LM/pre.c"
    grep -hE '^[[:space:]]*#[[:space:]]*include[[:space:]]*<' "$LM/$px.c" "$LM/$px.h" > "$LM/sys.c"
    (cd "$LM" && $CC -E -dM pre.c 2>/dev/null) | awk '{print $2}' | sed 's/(.*//' | LC_ALL=C sort -u > "$LM/pre.m"
    $CC -E -dM "$LM/sys.c" | awk '{print $2}' | sed 's/(.*//' | LC_ALL=C sort -u > "$LM/sys.m"
    live="$(comm -23 "$LM/pre.m" "$LM/sys.m" \
        | grep -vE "^(_|${upx}_|PCREC_|RX_PASS$|RX_FAIL$|RX_ITER_INIT$|RX_NOMATCH$|${upx}_H$)" || true)"
    for m in $MSET; do
        grep -qx "$m" "$LM/pre.m" && live="$live $m"
    done
    if grep -qE '^RX_G_' "$LM/pre.m"; then live="$live $(grep -E '^RX_G_' "$LM/pre.m" | tr '\n' ' ')"; fi
    if [ -n "${live// /}" ]; then
        bad "live at the segment block of '$pat': $live"; lbad=$((lbad + 1))
    fi
    # ...and nothing of the macro set survives the file.
    (cd "$LM" && $CC -E -dM "$px.c" 2>/dev/null) | awk '{print $2}' | sed 's/(.*//' \
        | grep -E '^RX_(SUBJ|LEN|POS|START|CAP|USER|G_)' > "$LM/end.m" && {
        bad "the macro set outlives the file in '$pat': $(tr '\n' ' ' < "$LM/end.m")"; lbad=$((lbad + 1)); }
done <<'EOF'
a(?C`c: return RX_PASS;`)b
(?<yr>\d{4})-(?C`c: return RX_CAP_LEN(RX_G_yr) == 4 ? RX_PASS : RX_FAIL;`)x
(?J)(?:(?<n>a)|(?<n>b))(?C`c: return RX_G_n == 2 ? RX_PASS : RX_FAIL;`)
(a+)+(?C`c: return RX_PASS;`)b(?C`c: return RX_PASS;`)
(?>(a)|ab)(?C`c: return RX_PASS;`)c\1?
(?=a)(\w)(?C`c: return RX_CAP_SET(1) ? RX_PASS : RX_FAIL;`)(?!x)
(?i)ab(?C`c: return RX_PASS;`)c{2,5}+$
(a|b)*?(?C`c: return RX_PASS;`)(?1)
EOF
if [ "$nart" -ge 8 ] && [ "$lbad" -eq 0 ]; then
    ok "over $nart artifacts, only the public contract is live at the segment block, and the macro set ends with the file"
elif [ "$lbad" -eq 0 ]; then
    bad "the live-macro check reached only $nart artifacts"
fi

# ---- arm 8: the driver checks --------------------------------------------------
echo
echo "== [INLINE-C] the driver checks =="
K="$WORK/drv"; mkdir -p "$K"
pc --allow-code=c -p dt --code-header 'c:"dt41.h"' -o "$K/dt.c" \
    --pattern '(\d+)(?C`c: dt41_n++; return RX_PASS;`)x|(\d+)y'
cat > "$K/dt_drv.c" <<'C'
#include <stdio.h>
#include "dt.c"
int main(void)
{
    ptrdiff_t c[DT_NCAPS][2];
    int rc = dt_search((const unsigned char *)"12y", 3, 0, c);
    if (rc != 1 || c[0][0] != 0 || c[0][1] != 3) { printf("DT-4.1: rc %d [%td,%td)\n", rc, c[0][0], c[0][1]); return 1; }
    if (dt41_n < 1) { printf("DT-4.1: the segment never fired\n"); return 2; }
    return 0;
}
C
if $CC $GENCFLAGS -I"$K" -I"$SCRIPT_DIR" -o "$K/dt" "$K/dt_drv.c" 2> "$K/cc.log" && "$TIMEOUT_BIN" 10 "$K/dt"; then
    ok "DT-4.1 inline: a counting segment fired (n >= 1) and the match is [0,3)"
else
    bad "DT-4.1 inline: $(cat "$K/cc.log")"
fi
trap_row() {   # trap_row WHAT PATTERN SUBJECT
    rm -f "$K/tr.c" "$K/tr"
    if ! pc --allow-code=c -p tr --emit-main -o "$K/tr.c" --pattern "$2" 2> "$K/p.log" ||
       ! $CC $GENCFLAGS -O1 -std=gnu11 -o "$K/tr" "$K/tr.c" 2> "$K/cc.log"; then
        bad "$1: did not build: $(cat "$K/p.log" "$K/cc.log" | head -3)"; return
    fi
    "$TIMEOUT_BIN" 10 "$K/tr" "$3" >/dev/null 2>&1
    local rc=$?
    if [ $rc -gt 128 ] && [ $rc -ne 137 ]; then ok "$1: traps (exit $rc)"; else bad "$1: exit $rc, no trap"; fi
}
trap_row "a check segment returning 1" 'a(?C`c: return 1;`)b' ab
trap_row "a segment falling off its end" 'a(?C`c: if (RX_POS > 99) return RX_PASS;`)b' ab

# ---- arm 9: the span helpers ----------------------------------------------------
echo
echo "== [INLINE-C] the span helpers =="
if pc --allow-code=c -p sp -o "$WORK/sp.c" --pattern "$SEG" &&
   $CC $GENCFLAGS -O1 -std=gnu11 -Wall -Wextra -Werror -include "$WORK/sp.h" -o "$WORK/span_check" \
       "$SCRIPT_DIR/span_check.c" 2> "$WORK/sp.log"; then
    if "$TIMEOUT_BIN" 60 "$WORK/span_check"; then
        ok "every span helper agrees with its §11.10 reference"
    else
        bad "a span helper disagrees with its reference (above)"
    fi
else
    bad "span_check.c did not build: $(head -5 "$WORK/sp.log")"
fi

# ---- arm 10: the call form (match_api.md 11.2 1a) -------------------------------
echo
echo "== [INLINE-C] no indirect call through a binding the compiler can see =="
A="$WORK/asm"; mkdir -p "$A"
icalls() { grep -cE '^\s+call\s+\*' "$1"; }
pc --features all -p ua -o "$A/ua.c" --pattern '(\d+)(?C"le3")x'
pc --allow-code=c -p ub -o "$A/ub.c" --pattern '(\d+)(?C`c: return RX_CAP_LEN(1) <= 3 ? RX_PASS : RX_FAIL;`)x'
pc --features all -p oc -o "$A/oc.c" --pattern '25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d'
pc --features all -p uc -o "$A/uc.c" --pattern 'ip=(?C"oc,consume")\.'
cat > "$A/le3.c" <<'C'
static ptrdiff_t le3(const rx_ctx *ctx) { return ctx->caps[1][1] - ctx->caps[1][0] <= 3 ? RX_PASS : RX_FAIL; }
const rx_callout_ref rx_callout_le3 = { le3, NULL };
C
printf '#include "ua.c"\n#include "le3.c"\n' > "$A/unity.c"
printf '#include "oc.c"\n#include "uc.c"\nconst rx_callout_ref rx_callout_oc = { oc_match, NULL };\n' > "$A/art.c"
printf '#include "ua.h"\n#include "le3.c"\n' > "$A/sep_bind.c"
cbad=0
for t in unity:unity.c embedded:ub.c artifact-as-callout:art.c control:ua.c; do
    name="${t%%:*}"; src="${t#*:}"
    if ! $CC -O2 -std=gnu11 -S -I"$A" -o "$A/$name.s" "$A/$src" 2> "$A/$name.log"; then
        bad "the $name build did not compile: $(head -3 "$A/$name.log")"; cbad=1; continue
    fi
    n="$(icalls "$A/$name.s")"
    if [ "$name" = control ]; then
        # A binding compiled SEPARATELY is called indirectly: the reader sees it.
        [ "$n" -ge 1 ] || { bad "the control (binding in another file) shows no indirect call: the asm reader is blind"; cbad=1; }
    elif [ "$n" -ne 0 ]; then
        bad "the $name build makes $n indirect call(s) through a binding the compiler can see"; cbad=1
    fi
done
[ "$cbad" = 0 ] && ok "unity, embedded and artifact-as-callout builds call their bindings directly (the separate-file control calls indirectly)"

# ---- arm 11: the measurement card ------------------------------------------------
echo
echo "== [INLINE-C] the inline-mode measurement card (smoke) =="
if PCREC="$PCREC" CC="$CC" TMPDIR="$WORK" bash "$SCRIPT_DIR/card_inline.sh" --smoke -o "$WORK/card.tsv" &&
   [ "$(grep -c 'UNMEASURED' "$WORK/card.tsv")" -ge 3 ]; then
    ok "the inline-mode card builds and runs every row (smoke: UNMEASURED)"
else
    bad "the inline-mode card did not run: $(cat "$WORK/card.tsv" 2>/dev/null)"
fi

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
echo "checks skipped: $skip"
[ "$fail" -eq 0 ]
