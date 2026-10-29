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
#       fails; the count is pinned exactly), plus the writers that are not
#       modes, the declared non-table modes (--emit-support, --subst,
#       --analysis, ...), plus the library (lib_check.c);
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
#  (11) the inline-mode measurement card builds and runs (--smoke);
#  (12) the D27 spec-first suite (d27/run.sh, written from the spec by an
#       author denied src/ and tests/), floor 545 passes and no failure,
#       with its CONTROL: the same suite against /bin/true must go red;
#  (13) stage 3 (inline_c.md §1.9, §5.2-§5.6): shared/sha256.c against
#       FIPS 180-4's vectors and pcrec's digest against sha256sum; pinned,
#       upper-case, unpinned and mismatched `include`/`lib` lines; a
#       pinned code-free file still verified; the three-file chain with an
#       unpinned middle; dual chains in both orders; the definition-site
#       view run (and F38's #line, the ASan row); a lib's code-header; a
#       recursive definition refused; `--list-callouts`' rows. Run before
#       arm 12 so the long suite stays last.
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
PCREC="$PCREC" CC="$CC" TMPDIR="$WORK" python3 "$SCRIPT_DIR/verify_code.py" "$SCRIPT_DIR"/*.rxt "$SCRIPT_DIR"/frag/*.rxt
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

# F6 (review 2026-10-27-r1-ic2): the manifest's `allow-code` line is the
# suite invoker's grant, so an EXACT allow-list of the manifests under tests/
# that carry it (rxt_format.md §6¶3), and a second line is a harness failure.
mallow="$(cd "$ROOT_DIR" && find tests -name harness.manifest -exec grep -lE '^[[:space:]]*allow-code([[:space:]]|$)' {} + | LC_ALL=C sort | tr '\n' ' ')"
if [ "$mallow" = "tests/code/frag/harness.manifest tests/code/harness.manifest " ]; then
    ok "only tests/code/ and tests/code/frag/ manifests carry the allow-code grant"
else
    bad "the allow-code grant is carried by: ${mallow:-no manifest} (allowed: tests/code/harness.manifest tests/code/frag/harness.manifest)"
fi
M2="$WORK/m2"; mkdir -p "$M2"
printf 'allow-code c\nallow-code c\n' > "$M2/harness.manifest"
printf 'pattern %s\nm "ab" 0 2\n' "$SEG" > "$M2/two.rxt"
if PCREC="$PCREC" bash "$ROOT_DIR/tests/harness/run.sh" "$M2/" > "$WORK/m2.log" 2>&1; then
    bad "a manifest with two allow-code lines was accepted by the harness"
elif grep -q "second 'allow-code' line" "$WORK/m2.log"; then
    ok "a manifest with two allow-code lines is a harness failure"
else
    bad "a manifest with two allow-code lines failed for another reason: $(grep -m2 -iE 'fail|error' "$WORK/m2.log")"
fi

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
refuse "reached code (an unpinned lib definition's segment) is refused" "lib_code.rxt:1 refused: the lib line at $D/reach.rxt:1 carries no sha256 pin" --allow-code=c --features all -o "$WORK/rdir" "$D/reach.rxt"
[ -e "$WORK/rdir" ] && bad "a refused FILE target wrote $WORK/rdir"
# F7 (review 2026-10-27-r1-ic2): a code-free target BEFORE a code target in
# one file, no grant, -o DIR: the refusal leaves NO file of either target.
printf 'target fr = fr\ntarget cd = cd\n\npattern ab\nname fr\n\npattern %s\nname cd\n' "$SEG" > "$D/two.rxt"
mkdir -p "$WORK/tdir"
if pc -o "$WORK/tdir" "$D/two.rxt" 2> "$WORK/t.log"; then
    bad "a two-target file with an ungranted code target compiled"
elif [ -n "$(ls -A "$WORK/tdir")" ]; then
    bad "a refused two-target build wrote: $(ls "$WORK/tdir" | tr '\n' ' ')"
else
    ok "a refused multi-target build writes no target, the code-free one before it included"
fi

# ---- arm 4: the entry-point table ---------------------------------------------
echo
echo "== [INLINE-C] the entry-point table (inline_c.md 5.9) =="
F="$WORK/ep"; mkdir -p "$F"
printf 'pattern %s\nm "ab" 0 2\n' "$SEG" > "$F/one.rxt"
# The DESCRIBE class parses code without the grant and prints no code text
# unescaped: a segment carrying a newline must not reach the output as a line.
NLSEG='"a(?C`c: int z = 0;\nNLMARK; return RX_PASS;`)b"'
# mode spelling | class (the arguments: ep_args). The CLI_MODE_TABLE modes'
# rows are READ from cli/main.c, the class its last column (review
# 2026-10-27-r1-ic2 F27, landed at [INLINE-C] stage 3): a mode states its
# class where it is declared. The writers that are not modes follow.
EP_TABLE="$(sed -n '/^#define CLI_MODE_TABLE(X)/,/^$/p' "$ROOT_DIR/cli/main.c" \
    | sed -nE 's/^[[:space:]]*X\([^"]*"([^"]+)",[[:space:]]*([A-Z]+)\).*/\1|\2/p' \
    | tr 'A-Z' 'a-z')"
EP_ROWS="$EP_TABLE
--pattern|writes
--pattern-esc|writes
-o -|writes
--emit-main|writes
--trace|writes"
# F20 (review 2026-10-27-r1-ic2): the modes and mode-like options that are
# NOT CLI_MODE_TABLE rows, declared here and run through the same classes
# (the table modes read their class off CLI_MODE_TABLE, F27). `refuses`: a
# compile-less mode that refuses every other option by its presence
# (MODE_ADMITS), the grant included, and runs without it.
NT_ROWS='--emit-support|refuses
--subst|refuses
--subst-file|refuses
--analysis|writes
--measures|writes
--tune|writes
--view|takes'
ep_args() {   # ep_args SPELLING -> ARGS
    case "$1" in
        --explain) ARGS=(--explain '(?C') ;;
        --count-groups|--emit-ir|--emit-facts) ARGS=("$1" --pattern-esc --pattern "$NLSEG") ;;
        --probe-ask) ARGS=(--probe-ask claim "$SEG") ;;
        --list-source) ARGS=(--list-source "$F/one.rxt") ;;
        --list-callouts) ARGS=(--list-callouts "$F/one.rxt") ;;
        --list-analysis|--list-measurements) ARGS=("$1" default) ;;
        'a file operand') ARGS=(-o "$F/w.c" "$F/one.rxt") ;;
        --pattern) ARGS=(-o "$F/w.c" --pattern "$SEG") ;;
        --pattern-esc) ARGS=(-o "$F/w.c" --pattern-esc --pattern "\"$SEG\"") ;;
        '-o -') ARGS=(-o - --pattern "$SEG") ;;
        --emit-main|--trace) ARGS=("$1" -o "$F/w.c" --pattern "$SEG") ;;
        --emit-support) ARGS=(--emit-support -o -) ;;
        --subst) ARGS=(--subst x -o -) ;;
        --subst-file) printf 'x' > "$F/t.tmpl"; ARGS=(--subst-file "$F/t.tmpl" -o -) ;;
        --analysis) ARGS=(--analysis default -o "$F/w.c" --pattern "$SEG") ;;
        --measures) ARGS=(--measures zen4-grid1 -o "$F/w.c" --pattern "$SEG") ;;
        --tune) ARGS=(--tune=min-size -o "$F/w.c" --pattern "$SEG") ;;
        --view) ARGS=(--list-analysis default --view=decoded) ;;
        *) ARGS=("$1") ;;
    esac
}
# Every CLI_MODE_TABLE row must carry a class the arms below know (a mode
# cannot slip by), and every one must reach ep_args.
nmodes=0
while IFS='|' read -r m c; do
    [ -z "$m" ] && continue
    nmodes=$((nmodes + 1))
    case "$c" in takes|describe|writes) ;; *) bad "CLI mode '$m' has class '$c', which the entry-point arm does not know" ;; esac
done <<< "$EP_TABLE"
# EXACT (F20): a mode added to the table moves this number, visibly.
[ "$nmodes" -eq 18 ] || bad "$nmodes CLI modes read from cli/main.c's CLI_MODE_TABLE, expected exactly 18: a mode was added (give it its ep_args arguments and move the pin) or the enumeration stopped reaching it"
[ "$(printf '%s\n' "$EP_ROWS" | wc -l)" -eq 23 ] && [ "$(printf '%s\n' "$NT_ROWS" | wc -l)" -eq 7 ] ||
    bad "the entry-point rows are not 23 table+writer rows and 7 non-table rows"
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
        refuses)
            if [ $r0 -eq 0 ] && [ $r1 -ne 0 ] && [[ "$o1" == *"--allow-code"* ]]; then
                ok "entry '$spell' (compile-less): runs without the grant, refuses it by name"
            else
                bad "entry '$spell' (compile-less): without the grant rc=$r0 '${o0:0:160}'; with it rc=$r1 '${o1:0:160}'"
            fi ;;
    esac
done <<< "$EP_ROWS
$NT_ROWS"
# F8 (review 2026-10-27-r1-ic2): an EXPLICIT empty grant is no grant to a
# describe mode either (one fact, one answer): same output as none at all.
for dm in --count-groups --emit-ir --emit-facts; do
    e0="$(pc "$dm" --pattern "$SEG" 2>&1)"; q0=$?
    e1="$(pc --allow-code= "$dm" --pattern "$SEG" 2>&1)"; q1=$?
    if [ $q0 -eq 0 ] && [ $q1 -eq 0 ] && [ "$e0" = "$e1" ]; then
        ok "describe '$dm': --allow-code= (empty) answers as no grant"
    else
        bad "describe '$dm': no grant rc=$q0, --allow-code= rc=$q1 '${e1:0:160}'"
    fi
done
# F11/F13/F14 (review 2026-10-27-r1-ic2): no fixed bound on a file's
# code-header lines; --help lists both code options; an empty HEADER is a
# shape refusal, not "malloc: Success".
{ for k in $(seq 1 300); do printf 'code-header c "h%d.h"\n' "$k"; done
  printf '\npattern %s\n' "$SEG"; } > "$D/many.rxt"
nh="$(pc --allow-code=c -o - "$D/many.rxt" 2>&1 | grep -cE '^#include "h[0-9]+\.h"')"
[ "$nh" = 300 ] && ok "a file's 300 code-header lines are 300 #include lines" \
    || bad "a file's 300 code-header lines emitted $nh #include lines"
hl="$(pc --help 2>&1)"
if printf '%s\n' "$hl" | grep -q -- '--allow-code' && printf '%s\n' "$hl" | grep -q -- '--code-header'; then
    ok "--help lists --allow-code and --code-header"
else
    bad "--help omits --allow-code or --code-header"
fi
eh="$(pc --code-header c: --pattern a -o - 2>&1)"
if printf '%s\n' "$eh" | grep -q 'wants LANG:HEADER' && ! printf '%s\n' "$eh" | grep -q malloc; then
    ok "--code-header c: is refused by its shape"
else
    bad "--code-header c: said: ${eh:0:160}"
fi

# F15 (review 2026-10-27-r1-ic2): a code site's `verify` refusal names its
# own module, which IS enabled, never "module 'callouts' is enabled".
vo="$(pc --allow-code=c --pattern 'a(?C`c,verify: return RX_PASS;`)b' -o - 2>&1)"
if printf '%s\n' "$vo" | grep -q "module 'code-c' is enabled but the callout attribute 'verify'"; then
    ok "a code site's verify refusal names module code-c"
else
    bad "a code site's verify refusal said: ${vo:0:160}"
fi

# F4 (review 2026-10-27-r1-ic2): a segment's own #defines are not pcrec's
# decisions; --emit-facts lists the stamps above the code block only.
FSEG="$(printf 'a(?C`c: return RX_PASS;\n#define RX_FAKE 1\n#undef RX_CODE_LANGS\n#define RX_CODE_LANGS "zzz"\n`)b')"
fo="$(pc --emit-facts --pattern "$FSEG" 2>&1)"
if printf '%s\n' "$fo" | grep -qE 'RX_CODE_LANGS[[:space:]]+"c"' &&
   ! printf '%s\n' "$fo" | grep -qE 'RX_FAKE|"zzz"|RX_SUBJ'; then
    ok "--emit-facts lists the artifact's stamps and none of a segment's own #defines"
else
    bad "--emit-facts read the code block: $(printf '%s\n' "$fo" | grep -E 'RX_FAKE|zzz|RX_SUBJ|CODE_LANGS' | tr '\n' ' ')"
fi
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
# F12 (review 2026-10-27-r1-ic2): an error inside a macro-set expansion names
# no line past the end of the .rxt (a code-header's #line once stayed in force
# over the macro set: hd.rxt:12 of a 4-line file).
printf 'code-header c <stdint.h>\n\npattern (a)(?C`c: return RX_CAP(1);`)c\nm "ac" 0 2\n' > "$G/hd.rxt"
if (cd "$G" && pc --allow-code=c -o hd.c hd.rxt >/dev/null 2>&1); then
    he="$(cd "$G" && $CC -fsyntax-only hd.c 2>&1)"
    hmax="$(printf '%s\n' "$he" | sed -n 's/.*hd\.rxt:\([0-9][0-9]*\):.*/\1/p' | LC_ALL=C sort -n | tail -1)"
    if [ -n "$hmax" ] && [ "$hmax" -le 4 ] && printf '%s\n' "$he" | grep -q 'hd\.c:'; then
        ok "a diagnostic inside a macro-set expansion names the .c, and the .rxt only at real lines"
    else
        bad "a macro-set diagnostic: highest hd.rxt line ${hmax:-none} of 4: $(printf '%s' "${he:0:300}" | sed -E 's/: (fatal )?error: /: [cc \1error] /g')"
    fi
else
    bad "hd.rxt did not compile under the grant"
fi
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
# THE PUBLIC SET, from sources the emitter does not read (review
# 2026-10-27-r1-ic2 F3: the emitter and this check once both meant "public"
# by the `<PREFIX>_` prefix): per artifact, what its .h defines; and the
# stamp inventory of the contract, match_api.md §6.3.2, one name per line
# with the prefix as PREFIX (`_X` after a first name expands at each of the
# first name's `_` cuts; `<PREFIX>_VAR_<name>` is the family PREFIX_VAR_*).
python3 - "$ROOT_DIR/docs/spec/match_api.md" > "$LM/inv.names" <<'PY'
import re, sys
text = open(sys.argv[1], encoding="utf-8").read()
sec = text[text.index('id="s6-3-2"'):text.index('id="s6-3-3"')]
out = set()
for line in sec.splitlines():
    if not line.startswith("|"):
        continue
    cell = line.split("|")[1]
    toks = re.findall(r"`((?:<PREFIX>|PCREC)?_[A-Z0-9_]+(?:<name>)?|PCREC_[A-Z0-9_]+)`", cell)
    first = None
    for t in toks:
        if t.startswith("<PREFIX>_") or t.startswith("PCREC_"):
            t = t.replace("<PREFIX>", "PREFIX")
            first = t
            out.add(t)
        elif first:
            cuts = [i for i, ch in enumerate(first) if ch == "_"]
            for i in cuts:
                out.add(first[:i] + t)
for n in sorted(out):
    print(n)
PY
ninv="$(wc -l < "$LM/inv.names" | tr -d ' ')"
[ "$ninv" -ge 60 ] || bad "the stamp inventory read from match_api.md §6.3.2 holds only $ninv names: the reader stopped reaching it"
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
    (cd "$LM" && $CC -E -dM "$px.h" 2>/dev/null) | awk '{print $2}' | sed 's/(.*//' | LC_ALL=C sort -u > "$LM/h.m"
    sed "s/^PREFIX_/${upx}_/" "$LM/inv.names" | sed 's/<name>$//' > "$LM/pub.m"
    live="$(LC_ALL=C comm -23 "$LM/pre.m" "$LM/sys.m" | LC_ALL=C comm -23 - "$LM/h.m" \
        | grep -vxF -f "$LM/pub.m" | grep -vE "^(_|${upx}_VAR_)" || true)"
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
# F10 (review 2026-10-27-r1-ic2): an empty group on a NULL subject is SET to
# the span helpers, as it is on "" (unset is len < 0 alone).
pc --allow-code=c -p nu -o "$K/nu.c" --pattern '()(?C`c: return rx_eq(RX_CAP(1), "") ? RX_PASS : RX_FAIL;`)'
cat > "$K/nu_drv.c" <<'C'
#include <stdio.h>
#include "nu.c"
int main(void)
{
    ptrdiff_t c[NU_NCAPS][2];
    int a = nu_search(NULL, 0, 0, c), b = nu_search((const unsigned char *)"", 0, 0, c);
    if (a != 1 || b != 1) { printf("NULL subject %d, empty subject %d\n", a, b); return 1; }
    return 0;
}
C
if $CC $GENCFLAGS -I"$K" -o "$K/nu" "$K/nu_drv.c" 2> "$K/cc.log" && "$TIMEOUT_BIN" 10 "$K/nu"; then
    ok "an empty group on a NULL subject reads as set in the span helpers, as on \"\""
else
    bad "an empty group on a NULL subject: $("$K/nu" 2>&1; head -3 "$K/cc.log" | sed -E 's/: (fatal )?error: /: [cc \1error] /g')"
fi
trap_row() {   # trap_row WHAT PATTERN SUBJECT [other-signal]
    rm -f "$K/tr.c" "$K/tr"
    if ! pc --allow-code=c -p tr --emit-main -o "$K/tr.c" --pattern "$2" 2> "$K/p.log" ||
       ! $CC $GENCFLAGS -O1 -std=gnu11 -o "$K/tr" "$K/tr.c" 2> "$K/cc.log"; then
        bad "$1: did not build: $(cat "$K/p.log" "$K/cc.log" | head -3)"; return
    fi
    "$TIMEOUT_BIN" 10 "$K/tr" "$3" >/dev/null 2>&1
    local rc=$?
    if [ -z "$TRAP_RC" ]; then bad "$1: exit $rc; no __builtin_trap signal is known for $(uname -m)"
    elif [ "${4:-}" = other-signal ]; then
        # The control: a crash by another signal, which the old any-signal
        # test passed and this one must not.
        if [ $rc -gt 128 ] && [ $rc -ne "$TRAP_RC" ]; then ok "$1: exit $rc, told apart from a trap"
        else bad "$1: exit $rc, wanted a non-trap signal"; fi
    elif [ $rc -eq "$TRAP_RC" ]; then ok "$1: traps (exit $rc, $TRAP_SIG)"
    else bad "$1: exit $rc, not __builtin_trap's $TRAP_SIG (exit $TRAP_RC)"; fi
}
# F22 (review 2026-10-27-r1-ic2): the trap rows want __builtin_trap's own
# signal, not any signal (a segfault once passed): ud2 is SIGILL on x86-64,
# brk is SIGTRAP on arm64.
case "$(uname -m)" in
    x86_64|i?86)   TRAP_RC=132; TRAP_SIG=SIGILL ;;
    aarch64|arm64) TRAP_RC=133; TRAP_SIG=SIGTRAP ;;
    *)             TRAP_RC=; TRAP_SIG= ;;
esac
trap_row "a check segment returning 1" 'a(?C`c: return 1;`)b' ab
trap_row "a segment falling off its end" 'a(?C`c: if (RX_POS > 99) return RX_PASS;`)b' ab
trap_row "a segfaulting segment is not a trap (the control)" 'a(?C`c: return *(volatile int *)0;`)b' ab other-signal
# F9 (review 2026-10-27-r1-ic2): a site no match can reach still builds
# under -Werror (its file-local binding is read by no call).
for up in 'a(?:(?C`c: return RX_PASS;`)){0}b' '(?(DEFINE)(?<d>x(?C`c: return RX_PASS;`)))ab'; do
    if pc --allow-code=c --features all -p ur -o "$K/ur.c" --pattern "$up" 2> "$K/p.log" &&
       $CC $GENCFLAGS -Werror -c -o "$K/ur.o" "$K/ur.c" 2> "$K/cc.log"; then
        ok "an unreached code site builds under -Werror: $up"
    else
        bad "an unreached code site breaks -Werror ($up): $(cat "$K/p.log" "$K/cc.log" | head -3 | sed -E 's/: (fatal )?error: /: [cc \1error] /g')"
    fi
done

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

# span-fold (manager ruling 2026-10-27): with a LITERAL z, rx_eq is a length
# compare and fixed-width compares at -O2: no call and no loop (no branch back
# to a label above it), read from the x86-64 assembly.
printf '#include "sp.h"\n__attribute__((noinline)) int sf_eq(rx_span s) { return rx_eq(s, "GET"); }\n' > "$WORK/sf.c"
if [ "$(uname -m)" != x86_64 ]; then
    bad "span-fold: the assembly reader reads x86-64 only, and this machine is $(uname -m)"
elif $CC -O2 -std=gnu11 -S -I"$WORK" -o "$WORK/sf.s" "$WORK/sf.c" 2> "$WORK/sf.log"; then
    # The function's control-flow graph (blocks split at labels; an edge per
    # jump, plus the fall-through unless a block ends in jmp/ret): a cycle
    # is a loop, a backward jump alone is only block layout.
    sfv="$(python3 - "$WORK/sf.s" <<'PY'
import re, sys
body, on = [], False
for line in open(sys.argv[1]):
    t = line.strip()
    if t == "sf_eq:": on = True; continue
    if on and t.startswith(".cfi_endproc"): break
    if on and t and not t.startswith(".") or (on and re.match(r"\.L\w+:", t)): body.append(t)
if not body: print("empty"); sys.exit()
blocks, cur = [["<entry>"]], None
for t in body:
    if re.match(r"\.L\w+:$", t): blocks.append([t[:-1]])
    else: blocks[-1].append(t)
idx = {b[0]: i for i, b in enumerate(blocks)}
out = set()
edges = {i: set() for i in range(len(blocks))}
for i, b in enumerate(blocks):
    last = b[-1].split() if len(b) > 1 else []
    for t in b[1:]:
        op = t.split()
        if op[0].startswith("call"): out.add("call")
        if op[0].startswith("j") and len(op) > 1 and op[1] in idx: edges[i].add(idx[op[1]])
    if not last or last[0] not in ("jmp", "ret") and i + 1 < len(blocks): edges[i].add(i + 1)
state = {}
def dfs(u):
    state[u] = 1
    for v in edges[u]:
        if state.get(v) == 1: out.add("loop")
        elif v not in state: dfs(v)
    state[u] = 2
dfs(0)
print(" ".join(sorted(out)))
PY
)"
    if [ -z "$sfv" ]; then ok "span-fold: rx_eq against a literal compiles to no call and no loop at -O2"
    else bad "span-fold: rx_eq against a literal compiles with: $sfv"; fi
else
    bad "span-fold: sf.c did not compile: $(head -3 "$WORK/sf.log")"
fi

# ---- arm 10: the call form (match_api.md 11.2 1a) -------------------------------
echo
echo "== [INLINE-C] no indirect call through a binding the compiler can see =="
A="$WORK/asm"; mkdir -p "$A"
icalls() { grep -cE '^\s+call\s+\*' "$1"; }
# THE POSITIVE WITNESS (review 2026-10-27-r1-ic2 F21): `n == 0` also holds
# when the site was deleted, so each direct build must also show the callee
# reached from the CALLER's own functions (`<caller>_*`, a segment's
# `<caller>__code*` excluded): its marker store inlined there, or a direct
# call to it. reached ASM CALLER CALLEE-ERE
reached() {
    python3 - "$1" "$2" "$3" <<'PY'
import re, sys
path, caller, callee = sys.argv[1], sys.argv[2], re.compile(sys.argv[3])
fn, hit = None, False
for line in open(path):
    m = re.match(r"([A-Za-z_][A-Za-z0-9_]*):", line)
    if m:
        name = m.group(1)
        fn = name if name.startswith(caller + "_") and not name.startswith(caller + "__code") else None
        continue
    if fn and callee.search(line):
        hit = True
sys.exit(0 if hit else 1)
PY
}
pc --features all -p ua -o "$A/ua.c" --pattern '(\d+)(?C"le3")x'
pc --allow-code=c -p ub -o "$A/ub.c" --pattern '(\d+)(?C`c: extern volatile int ub_mark; ub_mark = 1; return RX_CAP_LEN(1) <= 3 ? RX_PASS : RX_FAIL;`)x'
pc --features all -p oc -o "$A/oc.c" --pattern '25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d'
pc --features all -p uc -o "$A/uc.c" --pattern 'ip=(?C"oc,consume")\.'
cat > "$A/le3.c" <<'C'
volatile int le3_mark;
static ptrdiff_t le3(const rx_ctx *ctx) { le3_mark = 1; return ctx->caps[1][1] - ctx->caps[1][0] <= 3 ? RX_PASS : RX_FAIL; }
const rx_callout_ref rx_callout_le3 = { le3, NULL };
C
printf '#include "ua.c"\n#include "le3.c"\n' > "$A/unity.c"
printf '#include "oc.c"\n#include "uc.c"\nconst rx_callout_ref rx_callout_oc = { oc_match, NULL };\n' > "$A/art.c"
cbad=0
if [ "$(uname -m)" != x86_64 ]; then
    bad "the call-form arm reads x86-64 assembly only, and this machine is $(uname -m)"; cbad=1
fi
for t in 'unity:unity.c:ua:le3_mark|call\s+le3\b' 'embedded:ub.c:ub:ub_mark|call\s+ub__code1\b' \
         'artifact-as-callout:art.c:uc:(call|jmp)\s+oc_match\b' control:ua.c:ua:; do
    [ "$cbad" = 0 ] || break
    name="${t%%:*}"; rest="${t#*:}"; src="${rest%%:*}"; rest="${rest#*:}"
    caller="${rest%%:*}"; wit="${rest#*:}"
    if ! $CC -O2 -std=gnu11 -S -I"$A" -o "$A/$name.s" "$A/$src" 2> "$A/$name.log"; then
        bad "the $name build did not compile: $(head -3 "$A/$name.log")"; cbad=1; continue
    fi
    n="$(icalls "$A/$name.s")"
    if [ "$name" = control ]; then
        # A binding compiled SEPARATELY is called indirectly: the reader sees it.
        [ "$n" -ge 1 ] || { bad "the control (binding in another file) shows no indirect call: the asm reader is blind"; cbad=1; }
    elif [ "$n" -ne 0 ]; then
        bad "the $name build makes $n indirect call(s) through a binding the compiler can see"; cbad=1
    elif ! reached "$A/$name.s" "$caller" "$wit"; then
        bad "the $name build shows no call through its site at all: the callee ($wit) is reached from no ${caller}_ function"; cbad=1
    fi
done
[ "$cbad" = 0 ] && ok "unity, embedded and artifact-as-callout builds reach their bindings directly (the separate-file control calls indirectly)"

# ---- arm 11: the measurement card ------------------------------------------------
echo
echo "== [INLINE-C] the inline-mode measurement card (smoke) =="
if PCREC="$PCREC" CC="$CC" TMPDIR="$WORK" bash "$SCRIPT_DIR/card_inline.sh" --smoke -o "$WORK/card.tsv" &&
   [ "$(grep -c 'UNMEASURED' "$WORK/card.tsv")" -ge 3 ]; then
    ok "the inline-mode card builds and runs every row (smoke: UNMEASURED)"
else
    bad "the inline-mode card did not run: $(cat "$WORK/card.tsv" 2>/dev/null)"
fi
# F19 (review 2026-10-27-r1-ic2): each row reaches what it measures. The
# hit and tail rows fire their segment (fires > 0); the miss row's matcher
# really walks the subject (hits > 0, so the prefilter did not reject it
# unread) and never takes the segment's alternative (fires 0).
cf="$(awk -F'\t' 'NR > 1 {printf "%s=%s/%s ", $1, $4, $5}' "$WORK/card.tsv")"
if [ "$(awk -F'\t' '(($1=="inline:site_hit"||$1=="inline:tail") && $5+0 > 0) ||
                    ($1=="inline:site_miss" && $4+0 > 0 && $5 == "0")' "$WORK/card.tsv" | wc -l)" = 3 ]; then
    ok "the card's rows reach what they measure (hits/fires: $cf)"
else
    bad "a card row does not reach what it measures (hits/fires: ${cf:-no rows})"
fi

# ---- arm 13: stage 3, pinned reached code and the reviewer's view --------------
echo
echo "== [INLINE-C] stage 3: pins, chains, the definition-site view, --list-callouts =="
P3="$WORK/pin"; mkdir -p "$P3"
# (a) the ONE SHA-256 (shared/sha256.c) against FIPS 180-4's vectors.
cat > "$P3/nist.c" <<'C'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "sha256.h"
static int one(const char *what, const unsigned char *d, size_t n, const char *want)
{
    char h[65];
    pcrec_sha256_hex(d, n, h);
    if (strcmp(h, want)) { printf("%s: %s, wanted %s\n", what, h, want); return 1; }
    return 0;
}
int main(void)
{
    int bad = 0;
    bad |= one("empty", (const unsigned char *)"", 0,
               "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    bad |= one("abc", (const unsigned char *)"abc", 3,
               "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    const char *m448 = "abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq";
    bad |= one("448-bit", (const unsigned char *)m448, strlen(m448),
               "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1");
    const char *m896 = "abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmn"
                       "hijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu";
    bad |= one("896-bit", (const unsigned char *)m896, strlen(m896),
               "cf5b16a778af8380036ce59e7b0492370b249b11e8f07a51afac45037afee9d1");
    unsigned char *mil = malloc(1000000);
    if (!mil) return 2;
    memset(mil, 'a', 1000000);
    bad |= one("a million a", mil, 1000000,
               "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0");
    free(mil);
    return bad;
}
C
if $CC -O1 -std=gnu11 -Wall -Wextra -I"$ROOT_DIR/shared" -o "$P3/nist" "$P3/nist.c" \
       "$ROOT_DIR/shared/sha256.c" 2> "$P3/cc.log" && "$TIMEOUT_BIN" 60 "$P3/nist"; then
    ok "shared/sha256.c agrees with the FIPS 180-4 vectors (empty, abc, 448-bit, 896-bit, a million a)"
else
    bad "shared/sha256.c disagrees with a FIPS 180-4 vector: $(cat "$P3/cc.log")"
fi
# (b) pcrec's digest of a file (the one its mismatch refusal names) is
# sha256sum's, over every pinned fixture in the corpus.
zero="$(printf '0%.0s' $(seq 1 64))"
nsum=0
for f in "$SCRIPT_DIR"/frag/pin[0-9]_*.rxt; do
    # A copy beside the entry, named relatively: the refusal's digest must
    # survive pcrec_error.msg's 256 bytes whatever the checkout's path.
    mkdir -p "$P3/dg"; cp "$SCRIPT_DIR"/frag/pin[0-9]_*.rxt "$P3/dg/"
    printf 'include "%s" sha256 %s\n\npattern z\n' "${f##*/}" "$zero" > "$P3/dg/dig.rxt"
    got="$(pc -o "$P3/dig.c" "$P3/dg/dig.rxt" 2>&1 | sed -n 's/.*the file hashes to \([0-9a-f]*\);.*/\1/p')"
    want="$(sha256sum "$f" | cut -c1-64)"
    if [ -n "$got" ] && [ "$got" = "$want" ]; then nsum=$((nsum + 1))
    else bad "pcrec's digest of $f is '${got:-none}', sha256sum says $want"; fi
done
[ "$nsum" -ge 4 ] && ok "pcrec's digest equals sha256sum's over the $nsum pinned corpus files"

# (c) pins on include and lib: pinned, unpinned and mismatched.
cd_seg='a(?C`c: return RX_PASS;`)b'
printf 'pattern %s\nname lc\n' "$cd_seg" > "$P3/lib_code.rxt"
printf 'pattern qq\nname lq\n' > "$P3/lib_plain.rxt"
printf 'pattern %s\n' "$cd_seg" > "$P3/frag_code.rxt"
hl="$(sha256sum "$P3/lib_code.rxt" | cut -c1-64)"
hp="$(sha256sum "$P3/lib_plain.rxt" | cut -c1-64)"
hf="$(sha256sum "$P3/frag_code.rxt" | cut -c1-64)"
mk_lib() {   # mk_lib FILE PIN-OR-EMPTY DEF
    { printf 'lib "%s"%s\ntarget t = u\n\npattern x(?&%s)y\nname u\nfeatures recursion,named-groups\n' \
             "$4" "${2:+ sha256 $2}" "$3"; } > "$1"
}
mk_lib "$P3/l_pin.rxt" "$hl" lc lib_code.rxt
mk_lib "$P3/l_up.rxt" "$(printf '%s' "$hl" | tr a-f A-F)" lc lib_code.rxt
mk_lib "$P3/l_none.rxt" "" lc lib_code.rxt
mk_lib "$P3/l_bad.rxt" "$zero" lc lib_code.rxt
mk_lib "$P3/l_plain_none.rxt" "" lq lib_plain.rxt
mk_lib "$P3/l_plain_bad.rxt" "$zero" lq lib_plain.rxt
yes_build() {   # yes_build WHAT FILE...
    local what="$1"; shift
    if pc --allow-code=c -o "$P3/y.c" "$@" 2> "$P3/y.log"; then ok "$what"
    else bad "$what: refused: $(cat "$P3/y.log")"; fi
}
yes_build "a pinned lib line: the definition's code compiles" "$P3/l_pin.rxt"
yes_build "a pin in upper-case hex is accepted" "$P3/l_up.rxt"
yes_build "an unpinned lib whose definitions hold no code still compiles" "$P3/l_plain_none.rxt"
refuse "an unpinned lib line: the definition's code is refused, naming the line" \
    "lib_code.rxt:1 refused: the lib line at $P3/l_none.rxt:1 carries no sha256 pin" \
    --allow-code=c -o "$R" "$P3/l_none.rxt"
refuse "a lib pin that does not match is refused, naming the digest" \
    "lib \"lib_code.rxt\": sha256 pin mismatch, the file hashes to $hl" \
    --allow-code=c -o "$R" "$P3/l_bad.rxt"
refuse "a pinned file with no code is still verified (and refused when stale)" \
    "the file hashes to $hp" -o "$R" "$P3/l_plain_bad.rxt"
printf 'lib "lib_code.rxt" sha256 %s0\n' "$hl" > "$P3/l_long.rxt"
if pc --list-source "$P3/l_long.rxt" > /dev/null 2> "$P3/ll.log"; then
    bad "a 65-digit pin was accepted"
elif grep -q "exactly 64 hex digits" "$P3/ll.log"; then
    ok "a pin of 65 hex digits is refused by its shape"
else
    bad "a 65-digit pin refused for another reason: $(cat "$P3/ll.log")"
fi
ls_val="$(pc --list-source "$P3/l_up.rxt" | awk -F'\t' '$1 == "lib" {print $4}')"
if [ "$ls_val" = "\"lib_code.rxt\" sha256 $(printf '%s' "$hl" | tr a-f A-F)" ]; then
    ok "--list-source reports the pin as written and verifies nothing"
else
    bad "--list-source's lib value is '$ls_val'"
fi
printf 'include "frag_code.rxt" sha256 %s\n\npattern z\n' "$hf" > "$P3/i_pin.rxt"
printf 'include "frag_code.rxt"\n\npattern z\n' > "$P3/i_none.rxt"
printf 'include "frag_code.rxt" sha256 %s\n\npattern z\n' "$zero" > "$P3/i_bad.rxt"
yes_build "a pinned include line: the fragment's block compiles through --include-block" \
    --include-block "$P3/frag_code.rxt:1" "$P3/i_pin.rxt"
refuse "an unpinned include line: the fragment's code is refused" \
    "the include line at $P3/i_none.rxt:1 carries no sha256 pin" \
    --allow-code=c -o "$R" --include-block "$P3/frag_code.rxt:1" "$P3/i_none.rxt"
refuse "an include pin that does not match is refused" "sha256 pin mismatch" \
    --allow-code=c -o "$R" --include-block "$P3/frag_code.rxt:1" "$P3/i_bad.rxt"
refuse "a stale include pin refuses a file-operand build too" "sha256 pin mismatch" \
    -o "$R" "$P3/i_bad.rxt"
# The corpus's three-file chain with an unpinned middle (S-IC13's witness).
refuse "a three-file chain with an unpinned middle refuses the leaf's code" \
    "the include line at $SCRIPT_DIR/frag/pin2_ok.rxt:5 carries no sha256 pin" \
    --allow-code=c -o "$R" --include-block "$SCRIPT_DIR/frag/pin4_leaf.rxt:6" "$SCRIPT_DIR/frag/pin1_entry.rxt"
yes_build "the pinned fragment of that entry compiles" \
    --include-block "$SCRIPT_DIR/frag/pin2_ok.rxt:7" "$SCRIPT_DIR/frag/pin1_entry.rxt"

# (d) one file reached by two chains, one unpinned: refused in either order.
printf 'pattern c(?C`c: return RX_PASS;`)d\nname dc\n' > "$P3/dual_c.rxt"
hc="$(sha256sum "$P3/dual_c.rxt" | cut -c1-64)"
printf 'lib "dual_c.rxt" sha256 %s\n\npattern aa\nname da\n' "$hc" > "$P3/dual_a.rxt"
printf 'lib "dual_c.rxt" sha256 %s\n\npattern bb\nname db\n' "$hc" > "$P3/dual_b.rxt"
ha="$(sha256sum "$P3/dual_a.rxt" | cut -c1-64)"
for order in ab ba; do
    if [ "$order" = ab ]; then
        l1="lib \"dual_a.rxt\" sha256 $ha"; l2='lib "dual_b.rxt"'; bad_line=2
    else
        l1='lib "dual_b.rxt"'; l2="lib \"dual_a.rxt\" sha256 $ha"; bad_line=1
    fi
    printf '%s\n%s\ntarget t = u\n\npattern x(?&dc)y\nname u\nfeatures recursion,named-groups\n' \
        "$l1" "$l2" > "$P3/dual_$order.rxt"
    refuse "a file reached by a pinned and an unpinned chain is refused ($order order)" \
        "the lib line at $P3/dual_$order.rxt:$bad_line carries no sha256 pin" \
        --allow-code=c -o "$R" "$P3/dual_$order.rxt"
done

# (e) THE DEFINITION-SITE VIEW (§1.9 rows 3b/4): a site in a definition sees
# the definition's groups, numbered as the definition numbers them. The
# caller's own groups 1-3 would read 'x', 'q' and 'y'; the definition's
# group 1 is 'a' and its `w` is its group 2. The definition's text is longer
# than the target's and its code sits past the target's end (F38's ASan
# row: a segment once took its source from the TARGET's text).
cat > "$P3/view_lib.rxt" <<'EOF'
pattern (a)(?<w>b)(?C`c: return ctx->ncap == 3 && RX_SUBJ[RX_CAP_S(1)] == 'a' && RX_G_w == 2 && RX_CAP_LEN(RX_G_w) == 1 && RX_SUBJ[RX_CAP_S(2)] == 'b' && RX_START == 2 ? RX_PASS : RX_FAIL;`)c
name vd
features named-groups
EOF
hv="$(sha256sum "$P3/view_lib.rxt" | cut -c1-64)"
printf 'lib "view_lib.rxt" sha256 %s\ntarget vt = vu\n\npattern (x)(q)(?<w>y)(?&vd)z\nname vu\nfeatures recursion,named-groups\n' \
    "$hv" > "$P3/view.rxt"
cat > "$P3/view_drv.c" <<'C'
#include <stdio.h>
#include "vt.c"
int main(void)
{
    ptrdiff_t c[VT_NCAPS][2];
    int rc = vt_search((const unsigned char *)"--xqyabcz", 9, 0, c);
    if (rc != 1 || c[0][0] != 2 || c[0][1] != 9) { printf("view: rc %d [%td,%td)\n", rc, c[0][0], c[0][1]); return 1; }
    return 0;
}
C
if pc --allow-code=c -o "$P3" "$P3/view.rxt" 2> "$P3/v.log" &&
   $CC $GENCFLAGS -I"$P3" -o "$P3/view" "$P3/view_drv.c" 2>> "$P3/v.log" &&
   "$TIMEOUT_BIN" 10 "$P3/view" >> "$P3/v.log" 2>&1; then
    ok "a site in a definition sees the definition's own groups (ncap 3, group 1 'a', RX_G_w 2)"
else
    bad "the definition-site view: $(sed -E 's/: (fatal )?error: /: [cc \1error] /g' "$P3/v.log" | head -5)"
fi
if grep -q "^#line 1 \"$P3/view_lib.rxt\"" "$P3/vt.c"; then
    ok "a definition's segment names the definition's file in its #line (F38)"
else
    bad "a definition's segment does not name view_lib.rxt in its #line: $(grep '^#line' "$P3/vt.c" | head -3)"
fi
# A lib's code-header lines go with its segment, under its own #line.
printf 'code-header c <stdint.h>\npattern k(?C`c: return (uint8_t)1 ? RX_PASS : RX_FAIL;`)\nname kh\n' > "$P3/hdr_lib.rxt"
hh="$(sha256sum "$P3/hdr_lib.rxt" | cut -c1-64)"
printf 'lib "hdr_lib.rxt" sha256 %s\ntarget kt = ku\n\npattern (?&kh)\nname ku\nfeatures recursion,named-groups\n' "$hh" > "$P3/hdr.rxt"
if pc --allow-code=c -o "$P3/kt.c" "$P3/hdr.rxt" 2> "$P3/k.log" &&
   grep -A1 "^#line 1 \"$P3/hdr_lib.rxt\"" "$P3/kt.c" | grep -q '^#include <stdint.h>' &&
   $CC $GENCFLAGS -c -o "$P3/kt.o" "$P3/kt.c" 2>> "$P3/k.log"; then
    ok "a lib's code-header line is emitted with its segment, at the lib's own line"
else
    bad "a lib's code-header: $(head -3 "$P3/k.log")"
fi
# A definition that reaches itself keeps the refusal (§1.9 row 3a).
printf 'pattern a(?&rd)?(?C`c: return RX_PASS;`)b\nname rd\nfeatures recursion,named-groups\n' > "$P3/rec_lib.rxt"
hr="$(sha256sum "$P3/rec_lib.rxt" | cut -c1-64)"
printf 'lib "rec_lib.rxt" sha256 %s\ntarget rt = ru\n\npattern x(?&rd)y\nname ru\nfeatures recursion,named-groups\n' "$hr" > "$P3/rec.rxt"
refuse "a site in a recursive definition is still refused" "reaches itself through calls" \
    --allow-code=c -o "$R" "$P3/rec.rxt"
# A definition called twice: its site is numbered once and fires repeatedly.
printf 'lib "view_lib.rxt" sha256 %s\ntarget tw = tu\n\npattern (?&vd)-(?&vd)\nname tu\nfeatures recursion,named-groups\n' "$hv" > "$P3/twice.rxt"
tw="$(pc --list-callouts "$P3/twice.rxt" 2>&1 | awk -F'\t' '!/^#/ {print $2 "/" $8}')"
[ "$tw" = "1/repeated" ] && ok "a definition reached by two calls: one site, class repeated" \
    || bad "a definition reached by two calls lists '$tw'"

# (f) --list-callouts: the rows, describe-class, code escaped, verdicts.
printf 'lib "lib_code.rxt"\nlib "view_lib.rxt" sha256 %s\ntarget lt = lu\n\npattern (?&lc)(?&vd)%s\nname lu\nfeatures recursion,named-groups\n' \
    "$hv" "$(printf 'z(?C`c: int t\t= 0; /* \342\200\256 */ return RX_PASS;`)')" > "$P3/lc.rxt"
l0="$(pc --list-callouts "$P3/lc.rxt" 2>&1)"; q0=$?
l1="$(pc --allow-code=c --list-callouts "$P3/lc.rxt" 2>&1)"; q1=$?
rows="$(printf '%s\n' "$l0" | grep -v '^#')"
hdr="$(printf '%s\n' "$l0" | grep '^#target')"
if [ $q0 -eq 0 ] && [ "$l0" = "$l1" ] && [ "$(printf '%s\n' "$rows" | wc -l)" = 3 ] &&
   [ "$hdr" = "$(printf '#target\tsite\tsource\tbinding\tsymbol\tlang\twidth\tclass\tclass_reason\ttrust\tchain\tflag\tcode')" ]; then
    ok "--list-callouts: 3 rows, 13 columns, the same with and without the grant"
else
    bad "--list-callouts: rc $q0/$q1, same=$([ "$l0" = "$l1" ] && echo yes || echo no): ${l0:0:300}"
fi
tr_col() { printf '%s\n' "$rows" | awk -F'\t' -v s="$1" -v c="$2" '$2 == s {print $c}'; }
case "$(tr_col 1 10)" in "refused: the lib line at $P3/lc.rxt:1 carries no sha256 pin") ok "--list-callouts: an unpinned reached site's trust is the refusal" ;; *) bad "row 1 trust: $(tr_col 1 10)" ;; esac
[ "$(tr_col 2 10)" = pinned ] && ok "--list-callouts: a pinned reached site's trust is pinned" || bad "row 2 trust: $(tr_col 2 10)"
[ "$(tr_col 3 10)" = local ] && ok "--list-callouts: the target's own site is local" || bad "row 3 trust: $(tr_col 3 10)"
case "$(tr_col 2 11)" in "$P3/lc.rxt:2 lib \"view_lib.rxt\" sha256 $hv") ok "--list-callouts: the chain names each line and its pin" ;; *) bad "row 2 chain: $(tr_col 2 11)" ;; esac
case "$(tr_col 3 12)" in *U+202E*) ok "--list-callouts: a bidi control is flagged by name, not refused" ;; *) bad "row 3 flag: $(tr_col 3 12)" ;; esac
case "$(tr_col 3 13)" in *'int t\x09= 0; /* \xe2\x80\xae */'*) ok "--list-callouts: the code column numbers every non-printable byte" ;; *) bad "row 3 code: $(tr_col 3 13)" ;; esac
refuse "--list-callouts takes no -o" "takes no pattern and no -o" --list-callouts "$P3/lc.rxt" -o "$R"
refuse "--list-callouts composes with no other mode" "separate query" --list-callouts "$P3/lc.rxt" --list-syntax

# ---- arm 12: the D27 spec-first suite ----------------------------------------------
echo
echo "== [INLINE-C] the D27 spec-first suite (tests/code/d27/) =="
D27_FLOOR=545
d27_run() { # pcrec-binary log
    PCREC="$1" CC="$CC" TMPDIR="$WORK" D27_OUT="$WORK/d27run" "$TIMEOUT_BIN" 1200 \
        bash "$SCRIPT_DIR/d27/run.sh" >"$2" 2>&1
    sed -n 's/^d27: \([0-9]*\) passed, \([0-9]*\) failed$/\1 \2/p' "$2" | tail -1
}
read -r d27p d27f <<<"$(d27_run "${PCREC}" "$WORK/d27.log")"
if [ "${d27f:-x}" = 0 ] && [ "${d27p:-0}" -ge "$D27_FLOOR" ]; then
    ok "the D27 suite: $d27p passed, 0 failed (floor $D27_FLOOR)"
else
    bad "the D27 suite: '${d27p:-none} passed, ${d27f:-none} failed' (want 0 failed, >= $D27_FLOOR passed)"
    grep '^FAIL' "$WORK/d27.log" | head -20 >&2
fi
# the control: a compiler that answers nothing must fail most of the suite
read -r d27cp d27cf <<<"$(d27_run /bin/true "$WORK/d27c.log")"
if [ "${d27cf:-0}" -ge 100 ]; then
    ok "the D27 control (PCREC=/bin/true) goes red: ${d27cf} failed"
else
    bad "the D27 control did not go red (/bin/true: '${d27cp:-none} passed, ${d27cf:-none} failed'): the suite cannot fail"
fi

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
echo "checks skipped: $skip"
[ "$fail" -eq 0 ]
