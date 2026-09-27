#!/usr/bin/env bash
# tests/findings/run_findings_tests.sh — [FINDINGS] B1: the findings seam's
# DATA, STORE, STAMP and STRUCTURE, checked against sources the compiler does
# not share (docs/design/findings/design.md §8.1, §11.4, §11.6, §11.7, §13 B1).
#
#   §1 VALUES    the shipped library's normalization of the embedded default
#                equals tests/findings/default_ppm.tsv (RUNEST's own dump of
#                the table B1 replaced), sums to 1,000,000 with no byte under
#                the floor; and the §2.5 test vectors agree with an
#                INDEPENDENT python implementation (findings_ref.py) written
#                from the spec, never from the C. Replaces
#                run_offset_skip.sh's old §1.
#   §2 EMBED     every src/findings/<name>.rxt is in the store, and the text
#                the library returns is the committed file byte for byte; no
#                store name lacks a file (§8.1 [r2 A-3]).
#   §3 AGREEMENT the PRE-PARSED table a compile reads equals a fresh parse of
#                the embedded text by the library's own reader, block for
#                block (§13 B1 (3): generated from the same text, checked).
#   §4 STAMP     `<PREFIX>_FINDINGS` on real artifacts of both engines: the
#                digest equals findings_ref.py's over default_ppm.tsv; `-e
#                utf8` stamps `byte-rate=none`; a compile that asks nothing
#                stamps ""; and `rx_info.findings` mirrors the macro (§11.6).
#   §5 STRUCTURE structural_check.py (§6.3, §11.7): no reader tests a rate,
#                no rate table outside src/core/findings.c, no table pointer
#                in a *Sel struct.
#
# Verdict: this script's own `checks failed: 0` line, and under make, the
# absence of `*** [test-findings] Error` (BOILERPLATE, r2 S-F13).
set -u
export LC_ALL=C   # [K35] every sort below compares structured names
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37] pcrec_run / gen_cc
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT
pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
REF="python3 $SCRIPT_DIR/findings_ref.py"

PROBE="$WORKDIR/probe"
if ! gen_cc "findings probe" "$CC" -O0 -Wall -Wextra -Werror ${SANFLAGS:-} \
        -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" -o "$PROBE" \
        "$SCRIPT_DIR/findings_probe.c" "${LIBPCREC:-$ROOT_DIR/build/libpcrec.a}" \
        2>"$WORKDIR/probe.log"; then
    bad "could not build the findings probe against build/libpcrec.a: $(head -3 "$WORKDIR/probe.log")"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# =========================================================================
# §1 VALUES
# =========================================================================
"$PROBE" table > "$WORKDIR/table.txt"
dline="$(grep '^default ' "$WORKDIR/table.txt" | head -1)"
if [ -z "$dline" ]; then
    bad "§1 the pre-parsed store has no 'default' block"
else
    echo "$dline" | awk '{print $6}' | tr ',' ' ' > "$WORKDIR/dcounts"
    "$PROBE" normalize < "$WORKDIR/dcounts" > "$WORKDIR/dppm"
    awk -F'\t' '!/^#/ && NF==2 {print $2}' "$SCRIPT_DIR/default_ppm.tsv" | tr '\n' ' ' \
        | sed 's/ $//' > "$WORKDIR/want"
    if [ "$(cat "$WORKDIR/dppm")" = "$(cat "$WORKDIR/want")" ]; then
        ok "§1 the embedded default normalizes to default_ppm.tsv entry for entry (256 bytes)"
    else
        bad "§1 the embedded default does NOT normalize to default_ppm.tsv — the default is no longer the table B1 replaced (design §0.7)"
    fi
    read -r tot mn < <(tr ' ' '\n' < "$WORKDIR/dppm" | awk '{t+=$1; if(NR==1||$1<m)m=$1} END{print t, m}')
    if [ "$tot" = "1000000" ] && [ "$mn" -ge 2 ]; then
        ok "§1 the default's byte-rate sums to exactly 1,000,000 ppm and no byte is under the 2 ppm floor"
    else
        bad "§1 the default's byte-rate sums to $tot with minimum $mn — the cost model reads it as a probability (offset_k_skip.md §4.1)"
    fi
fi
$REF vectors > "$WORKDIR/vec"
nvec="$(wc -l < "$WORKDIR/vec" | tr -d ' ')"
"$PROBE" normalize < "$WORKDIR/vec" > "$WORKDIR/vec.c"
$REF normalize < "$WORKDIR/vec" > "$WORKDIR/vec.py"
if [ "$nvec" -ge 3 ] && cmp -s "$WORKDIR/vec.c" "$WORKDIR/vec.py"; then
    ok "§1 the §2.5 test vectors ($nvec: all-equal, one-nonzero, negative residue) agree with the independent python normalization"
else
    bad "§1 the §2.5 test vectors disagree with findings_ref.py (or none ran: $nvec):"
    diff "$WORKDIR/vec.c" "$WORKDIR/vec.py" | head -4 >&2
fi
printf '%s\n' "$(printf '0 %.0s' $(seq 256) | sed 's/ $//')" | "$PROBE" normalize > "$WORKDIR/zero"
if grep -q '^error -1$' "$WORKDIR/zero"; then
    ok "§1 an all-zero block is refused (-1), never normalized to a table"
else
    bad "§1 an all-zero block normalized to '$(head -c 60 "$WORKDIR/zero")' — design §2.5 step 1 makes it a hard error"
fi

# =========================================================================
# §2 EMBED
# =========================================================================
"$PROBE" names | sort > "$WORKDIR/names"
( cd "$ROOT_DIR/src/findings" && ls *.rxt | sed 's/\.rxt$//' | sort ) > "$WORKDIR/files"
if [ -s "$WORKDIR/files" ] && cmp -s "$WORKDIR/names" "$WORKDIR/files"; then
    ok "§2 the store's names are exactly src/findings/*.rxt ($(wc -l < "$WORKDIR/files" | tr -d ' '))"
else
    bad "§2 the store's names differ from src/findings/*.rxt:"; diff "$WORKDIR/names" "$WORKDIR/files" >&2
fi
while read -r n; do
    "$PROBE" text "$n" > "$WORKDIR/t.$n"
    if cmp -s "$WORKDIR/t.$n" "$ROOT_DIR/src/findings/$n.rxt"; then
        ok "§2 the embedded '$n' is src/findings/$n.rxt byte for byte ($(wc -c < "$WORKDIR/t.$n" | tr -d ' ') bytes)"
    else
        bad "§2 the embedded '$n' differs from src/findings/$n.rxt — the embed dropped, truncated or mis-escaped a byte (design §8.1)"
    fi
done < "$WORKDIR/files"

# =========================================================================
# §3 AGREEMENT
# =========================================================================
"$PROBE" reparse > "$WORKDIR/reparse.txt"
nb="$(wc -l < "$WORKDIR/table.txt" | tr -d ' ')"
if [ "$nb" -ge 1 ] && cmp -s "$WORKDIR/table.txt" "$WORKDIR/reparse.txt"; then
    ok "§3 the pre-parsed table equals the library reader's parse of the embedded text ($nb block(s): bundle, kind, line, serves, 256 counts)"
else
    bad "§3 the pre-parsed table ($nb block(s)) and a fresh parse of the embedded text DISAGREE:"
    diff <(cut -c1-120 "$WORKDIR/table.txt") <(cut -c1-120 "$WORKDIR/reparse.txt") | head -6 >&2
fi

# =========================================================================
# §4 STAMP
# =========================================================================
want_digest="$($REF digest "$SCRIPT_DIR/default_ppm.tsv")"
lib_digest="$("$PROBE" default-digest)"
if [ "$lib_digest" = "$want_digest" ]; then
    ok "§4 the library's default digest $lib_digest equals the independent FNV-1a-64 over default_ppm.tsv"
else
    bad "§4 the library's default digest '$lib_digest' is not the reference '$want_digest' (design §7's byte layout)"
fi
# stamp_of FILE -> the macro's value; info_of FILE -> the initializer's
stamp_of() { sed -n 's/^#define RX_FINDINGS "\(.*\)"$/\1/p' "$1"; }
info_of()  { sed -n 's/^    \.findings = "\(.*\)",$/\1/p' "$1"; }
check_stamp() { # check_stamp LABEL EXPECT pcrec-args...
    local lbl="$1" want="$2"; shift 2
    local f="$WORKDIR/s.c"
    if ! pcrec_run "$PCREC" -p rx -o "$f" "$@" >/dev/null 2>&1; then
        bad "§4 [$lbl] did not compile: $*"; return
    fi
    local s i n
    s="$(stamp_of "$f")"; i="$(info_of "$f")"
    n="$(grep -c '^#define RX_FINDINGS ' "$f")"
    if [ "$n" = 1 ] && [ "$s" = "$want" ] && [ "$i" = "$s" ]; then
        ok "§4 [$lbl] RX_FINDINGS \"$s\" and rx_info.findings agree"
    else
        bad "§4 [$lbl] RX_FINDINGS x$n \"$s\" / rx_info.findings \"$i\", expected \"$want\" on both"
    fi
}
check_stamp "byte, DFA"       "byte-rate=default:$want_digest" --pattern 'GET /index\.html'
check_stamp "byte, VM"        "byte-rate=default:$want_digest" --features all --pattern '(a)x\1y'
check_stamp "utf8, DFA"       "byte-rate=none"                 -e utf8 --pattern 'GET /index\.html'
check_stamp "utf8, VM"        "byte-rate=none"                 -e utf8 --features all --pattern '(a)x\1y'
# Nothing asked: the necessary-byte facts denied (so no pick asks) on a
# pattern with no DFA prefilter (so the offset-k selection never runs).
check_stamp "nothing asked"   ""                               -fno-req-byte --pattern '^abc'
# Asked by the offset-k selection alone (the pick denied): the stamp is
# rendered after the LAST reader, so this ask is not lost (design §6.4 rule 2).
check_stamp "offset-k only"   "byte-rate=default:$want_digest" -fno-req-byte --pattern 'abc'

# =========================================================================
# §5 STRUCTURE
# =========================================================================
while IFS= read -r line; do
    case "$line" in
        PASS:*) ok "§5 ${line#PASS: }" ;;
        FAIL:*) bad "§5 ${line#FAIL: }" ;;
    esac
done < <(python3 "$SCRIPT_DIR/structural_check.py" "$ROOT_DIR" 2>&1)


# =========================================================================
# §6 RESOLUTION ([B2]; design §4, §5, §9, §11.5) — the stops, the chain,
# the CLI surface and the listings, against fixtures res_fixtures.py writes
# fresh. Every expected digest is findings_ref.py's (a regex over the
# fixture's `row` lines, normalized and digested in python), never the
# compiler's own.
# =========================================================================
R="$WORKDIR/res"
python3 "$SCRIPT_DIR/res_fixtures.py" "$R"
bdig() { $REF bundle-digest "$@"; }            # bdig FILE [NAME]
anystamp() { sed -n 's/^#define [A-Z0-9_]*_FINDINGS "\(.*\)"$/\1/p' "$1"; }
DDEF="$want_digest"                            # the store default's (§4)
# res_stamp LABEL EXPECT pcrec-args... : compiles to one artifact and holds
# its <PREFIX>_FINDINGS to EXPECT. stderr is kept in $WORKDIR/res.err.
res_stamp() {
    local lbl="$1" want="$2"; shift 2
    local f="$WORKDIR/r.c" got
    rm -f "$f"
    if ! pcrec_run "$PCREC" -p rx -o "$f" "$@" >/dev/null 2>"$WORKDIR/res.err"; then
        bad "§6 [$lbl] did not compile: $(head -c 200 "$WORKDIR/res.err")"; return 1
    fi
    got="$(anystamp "$f")"
    if [ "$got" = "$want" ]; then ok "§6 [$lbl] stamps \"$got\""
    else bad "§6 [$lbl] stamped \"$got\", expected \"$want\""; return 1; fi
}
# res_refuse LABEL NEEDLE pcrec-args... : must refuse, naming NEEDLE.
res_refuse() {
    local lbl="$1" needle="$2"; shift 2
    if pcrec_run "$PCREC" -p rx -o "$WORKDIR/r.c" "$@" >/dev/null 2>"$WORKDIR/res.err"; then
        bad "§6 [$lbl] compiled; it must refuse naming '$needle'"
    elif grep -qF -- "$needle" "$WORKDIR/res.err"; then
        ok "§6 [$lbl] refuses: $(head -c 160 "$WORKDIR/res.err" | tr '\n' ' ')"
    else
        bad "§6 [$lbl] refused without naming '$needle': $(head -c 200 "$WORKDIR/res.err")"
    fi
}
PAT='(x?)([a-z]+)+Z.@\1'
FEAT="--features all"
# #1 S1 over S2 over S3
res_stamp "#1 S1: the compiling file's bundle over -I's" \
    "byte-rate=shadow:$(bdig "$R/s1_shadow.rxt" shadow)" $FEAT -I "$R/A" "$R/s1_shadow.rxt"
res_stamp "#1 S2: -I's bundle for a --pattern compile (R12, #16)" \
    "byte-rate=shadow:$(bdig "$R/A/shadow.rxt")" $FEAT -I "$R/A" --analysis shadow --pattern "$PAT"
res_stamp "#1 S2 over S3: an -I default.rxt answers an explicit 'default'" \
    "byte-rate=default:$(bdig "$R/A/default.rxt")" $FEAT -e utf8 -I "$R/A" --analysis default --pattern "$PAT"
# #2 -I order is the search order
res_stamp "#2 -I A -I B finds A's" "byte-rate=ord:$(bdig "$R/A/ord.rxt")" \
    $FEAT -I "$R/A" -I "$R/B" --analysis ord --pattern "$PAT"
res_stamp "#2 -I B -I A finds B's" "byte-rate=ord:$(bdig "$R/B/ord.rxt")" \
    $FEAT -I "$R/B" -I "$R/A" --analysis ord --pattern "$PAT"
# #3 self-shadow: `default` including <default> resolves from the NEXT stop
res_stamp "#3 self-include resolves past its own stop (byte: the store's default)" \
    "byte-rate=default:$DDEF" $FEAT -e byte -I "$R/A" --analysis default --pattern "$PAT"
# #4 a non-self cycle; #5 the depth limit
res_refuse "#4 a non-self include cycle" "include cycle: cyca -> cycb -> cyca" \
    $FEAT -I "$R/A" --analysis cyca --pattern "$PAT"
res_refuse "#5 a nine-link chain" "PCREC_MAX_FIND_CHAIN" \
    $FEAT -I "$R/A" --analysis d1 --pattern "$PAT"
res_stamp "#5 an eight-link chain is within the limit" \
    "byte-rate=d2:$(bdig "$R/A/d2.rxt")" $FEAT -I "$R/A" --analysis d2 --pattern "$PAT"
# #6 unknown name, the stops listed
res_refuse "#6 an unknown name lists the stops" "searched: -I $R/A, the built-in store" \
    $FEAT -I "$R/A" --analysis nosuch --pattern "$PAT"
# #7 fall-through, one bundle per file, exact-case names
if res_stamp "#7 an -I file with no such bundle falls through to the next" \
    "byte-rate=lib:$(bdig "$R/B/lib.rxt")" $FEAT -I "$R/A" -I "$R/B" --analysis lib --pattern "$PAT"; then
    if grep -qF "$R/A/lib.rxt defines no analysis 'lib'" "$WORKDIR/res.err"; then
        ok "§6 [#7] the fall-through prints its note naming the file"
    else
        bad "§6 [#7] the fall-through printed no note: $(head -c 200 "$WORKDIR/res.err")"
    fi
fi
res_refuse "#7 an -I file with two bundles" "defines 2 analyses" \
    $FEAT -I "$R/A" --analysis two --pattern "$PAT"
res_refuse "#7 'Mixed.rxt' never answers 'mixed' (exact directory entry)" "unknown analysis 'mixed'" \
    $FEAT -I "$R/A" --analysis mixed --pattern "$PAT"
# #8 a name defined twice in the compiling file
res_refuse "#8 a bundle name defined twice in one file" "dup" $FEAT "$R/dup.rxt"
# #9 a planted default.rxt moves nothing that did not name it (F-11)
mkdir -p "$WORKDIR/p9a" "$WORKDIR/p9b"
if pcrec_run "$PCREC" -p rx -o "$WORKDIR/p9a/x.c" $FEAT --pattern "$PAT" >/dev/null 2>&1 &&
   pcrec_run "$PCREC" -p rx -o "$WORKDIR/p9b/x.c" $FEAT -I "$R/A" --pattern "$PAT" >/dev/null 2>&1 &&
   cmp -s "$WORKDIR/p9a/x.c" "$WORKDIR/p9b/x.c"; then
    ok "§6 [#9] an -I dir holding default.rxt leaves an unnamed compile byte-identical (the terminal is by identity)"
else
    bad "§6 [#9] an -I dir holding default.rxt MOVED an artifact that named no analysis (design §0.6)"
fi
# #10 an explicit include <default> reaches the store and is not repeated
"$PCREC" --list-analysis withdef -I "$R/B" > "$WORKDIR/l10" 2>&1
n10="$(awk '/^#section chain/{s=1;next} /^#section/{s=0} s&&!/^#/' "$WORKDIR/l10" | wc -l | tr -d ' ')"
if [ "$n10" = 2 ] && awk -F'\t' '$1=="1"&&$2=="default"&&$3=="store"{f=1} END{exit !f}' "$WORKDIR/l10"; then
    ok "§6 [#10] include <default> reaches the store's default, and the terminal is not added twice (2 links)"
else
    bad "§6 [#10] the chain of 'withdef' has $n10 link(s), expected withdef + the store's default"
fi
# #11 per-(query, encoding) fall-through: one query, one block (F-5's detector)
res_stamp "#11 byte falls through to the next link's block" \
    "byte-rate=default:$DDEF" $FEAT -e byte -I "$R/B" --analysis withdef --pattern "$PAT"
res_stamp "#11 utf8 answers from the bundle's own block" \
    "byte-rate=withdef:$(bdig "$R/B/withdef.rxt")" $FEAT -e utf8 -I "$R/B" --analysis withdef --pattern "$PAT"
# the no-query note (design §9): the SELECTED chain declares nothing under -e
if pcrec_run "$PCREC" -p rx -o "$WORKDIR/r.c" $FEAT -e utf8 -I "$R/A" --analysis byteonly --pattern "$PAT" >/dev/null 2>"$WORKDIR/res.err" &&
   grep -qF "analysis 'byteonly' declares no query under -e utf8" "$WORKDIR/res.err" &&
   [ "$(anystamp "$WORKDIR/r.c")" = "byte-rate=none" ]; then
    ok "§6 [note] a selected chain declaring nothing under -e utf8 notes it and stamps byte-rate=none"
else
    bad "§6 [note] no 'declares no query' note, or a wrong stamp: $(head -c 200 "$WORKDIR/res.err")"
fi
# #12 the fill-only CLI (F-8) and the config-variant spelling (design §3.2)
mkdir -p "$WORKDIR/o12"
if pcrec_run "$PCREC" $FEAT -I "$R/A" --analysis shadow -o "$WORKDIR/o12" "$R/fill.rxt" >/dev/null 2>"$WORKDIR/res.err"; then
    s_cfg="$(anystamp "$WORKDIR/o12/t_cfg.c")"; s_none="$(anystamp "$WORKDIR/o12/t_none.c")"
    s_plain="$(anystamp "$WORKDIR/o12/t_plain.c")"
    d_ord="$(bdig "$R/A/ord.rxt")"; d_sh="$(bdig "$R/A/shadow.rxt")"
    if [ "$s_cfg" = "byte-rate=ord:$d_ord" ] && [ "$s_none" = "byte-rate=shadow:$d_sh" ] &&
       [ "$s_plain" = "byte-rate=shadow:$d_sh" ]; then
        ok "§6 [#12] --analysis FILLS the two targets whose configs name none, and the config variant's 'ord' wins its target"
    else
        bad "§6 [#12] fill-only broken: t_cfg=\"$s_cfg\" (want ord) t_none=\"$s_none\" t_plain=\"$s_plain\" (want shadow)"
    fi
    if grep -qF "target 't_cfg': CLI --analysis shadow and this file's analysis ord disagree" "$WORKDIR/res.err"; then
        ok "§6 [#12] the disagreeing target gets the file-wins note"
    else
        bad "§6 [#12] no fill-only disagreement note: $(head -c 200 "$WORKDIR/res.err")"
    fi
else
    bad "§6 [#12] fill.rxt did not compile: $(head -c 200 "$WORKDIR/res.err")"
fi
res_refuse "#12 --analysis in a config's pcrec line" "may not carry '--analysis'" $FEAT "$R/pcrecline.rxt"
# #13 R13: the same invocation from two cwds, explicit paths
mkdir -p "$WORKDIR/c13a" "$WORKDIR/c13b"
( cd "$WORKDIR/c13a" && "$PCREC" -p rx -o x.c $FEAT -I "$R/A" --analysis ord --pattern "$PAT" ) >/dev/null 2>&1
( cd "$R" && "$PCREC" -p rx -o "$WORKDIR/c13b/x.c" $FEAT -I "$R/A" --analysis ord --pattern "$PAT" ) >/dev/null 2>&1
if [ -s "$WORKDIR/c13a/x.c" ] && cmp -s "$WORKDIR/c13a/x.c" "$WORKDIR/c13b/x.c"; then
    ok "§6 [#13] the same invocation from two working directories is byte-identical (no ambient state, R13)"
else
    bad "§6 [#13] the artifact depends on the working directory"
fi
# #14 R20: a provenance edit moves nothing; a one-row edit moves the stamp (F-3)
for k in 1 2 3; do mkdir -p "$WORKDIR/p14_$k"
    pcrec_run "$PCREC" -p rx -o "$WORKDIR/p14_$k/x.c" $FEAT -I "$R/P$k" --analysis prov --pattern "$PAT" >/dev/null 2>&1
done
if [ -s "$WORKDIR/p14_1/x.c" ] && cmp -s "$WORKDIR/p14_1/x.c" "$WORKDIR/p14_2/x.c"; then
    ok "§6 [#14] a provenance-only edit (retrieved) moves no artifact byte (R20)"
else
    bad "§6 [#14] a provenance-only edit MOVED the artifact — the digest covers provenance (design §7)"
fi
if [ "$(anystamp "$WORKDIR/p14_1/x.c")" != "$(anystamp "$WORKDIR/p14_3/x.c")" ] &&
   [ "$(anystamp "$WORKDIR/p14_3/x.c")" = "byte-rate=prov:$(bdig "$R/P3/prov.rxt")" ]; then
    ok "§6 [#14] a one-row edit moves the stamp to the edited bundle's digest (R22)"
else
    bad "§6 [#14] a one-row edit did not move the stamp as its digest predicts"
fi
# #15 R7: a shipped bundle copied into -I gives an identical artifact
mkdir -p "$R/C" "$WORKDIR/p15"
cp "$ROOT_DIR/src/findings/default.rxt" "$R/C/default.rxt"
if pcrec_run "$PCREC" -p rx -o "$WORKDIR/p15/x.c" $FEAT -I "$R/C" --analysis default --pattern "$PAT" >/dev/null 2>&1 &&
   cmp -s "$WORKDIR/p9a/x.c" "$WORKDIR/p15/x.c"; then
    ok "§6 [#15] the shipped default copied into -I compiles byte-identically to no analysis at all (R7)"
else
    bad "§6 [#15] a byte-identical copy of the shipped default moved the artifact"
fi
# #17 R18: the listing's resolution digest IS the stamp's, and the reference's
"$PCREC" --list-analysis ord -I "$R/A" > "$WORKDIR/l17" 2>/dev/null
l17="$(awk -F'\t' '/^#section resolution/{s=1;next} /^#section/{s=0} s&&$1=="byte-rate"&&$2=="byte"{print $7}' "$WORKDIR/l17")"
res_stamp "#17 the compile under the same resolution" "byte-rate=ord:$l17" $FEAT -I "$R/A" --analysis ord --pattern "$PAT"
if [ "$l17" = "$(bdig "$R/A/ord.rxt")" ]; then
    ok "§6 [#17] --list-analysis's resolution digest $l17 equals the independent reference's (R18)"
else
    bad "§6 [#17] --list-analysis's resolution digest '$l17' is not findings_ref.py's"
fi
# #18 every embedded bundle lists (parses in the no-filesystem mode, normalizes)
while IFS=$'\t' read -r n _; do
    case "$n" in '#'*|'') continue ;; esac
    if "$PCREC" --list-analysis "$n" >/dev/null 2>"$WORKDIR/res.err"; then
        ok "§6 [#18] the embedded '$n' lists (parses, normalizes)"
    else
        bad "§6 [#18] the embedded '$n' does not list: $(head -c 200 "$WORKDIR/res.err")"
    fi
done < <("$PCREC" --list-analyses)
# #19 is §2 above: every embedded text is its committed file, byte for byte.
# #20 the per-target view: named_by, and each resolution digest = the stamp
mkdir -p "$WORKDIR/o20"
"$PCREC" --list-analysis "$R/view.rxt" -I "$R/A" --analysis ord > "$WORKDIR/l20" 2>/dev/null
nb20="$(awk -F'\t' '/^#section targets/{s=1;next} /^#section/{s=0} s&&!/^#/{print $1":"$4}' "$WORKDIR/l20" | tr '\n' ' ')"
if [ "$nb20" = "t_cfg:config t_fill:cli-fill " ]; then
    ok "§6 [#20] the per-target view names each target's analysis source ($nb20)"
else
    bad "§6 [#20] the per-target view reads '$nb20', expected 't_cfg:config t_fill:cli-fill'"
fi
if pcrec_run "$PCREC" $FEAT -I "$R/A" --analysis ord -o "$WORKDIR/o20" "$R/view.rxt" >/dev/null 2>&1; then
    v20=0
    for t in t_cfg t_fill; do
        d="$(awk -F'\t' -v t="$t" '/^#section resolution/{s=1;next} /^#section/{s=0} s&&$1==t&&$2=="byte-rate"&&$3=="byte"{print $5":"$8}' "$WORKDIR/l20")"
        [ "byte-rate=$d" = "$(anystamp "$WORKDIR/o20/$t.c")" ] || v20=1
    done
    if [ "$v20" = 0 ]; then ok "§6 [#20] each target's resolution row is its artifact's stamp"
    else bad "§6 [#20] a target's resolution row disagrees with its compiled stamp"; fi
else
    bad "§6 [#20] view.rxt did not compile"
fi
# #21 R27a: the analyzer's output lists through --list-analysis, and its
# digest is the reference's (the freq/cpfreq equal-digest half waits for
# `cpfreq`, B5)
mkdir -p "$R/AN"
if python3 "$ROOT_DIR/scripts/pcrec_analyze.py" --name ana --retrieved 2026-09-27 --scan freq \
        "$SCRIPT_DIR/fixtures/basic.txt" > "$R/AN/ana.rxt" 2>"$WORKDIR/res.err" &&
   "$PCREC" --list-analysis ana -I "$R/AN" > "$WORKDIR/l21" 2>>"$WORKDIR/res.err" &&
   [ "$(awk -F'\t' '/^#section resolution/{s=1;next} /^#section/{s=0} s&&$1=="byte-rate"&&$2=="byte"{print $7}' "$WORKDIR/l21")" = "$(bdig "$R/AN/ana.rxt")" ]; then
    ok "§6 [#21] the analyzer's output resolves through --list-analysis -I with the reference digest (R27a)"
else
    bad "§6 [#21] the analyzer's output does not round-trip: $(head -c 200 "$WORKDIR/res.err")"
fi
# #22 (F-9) the consumption record belongs to ONE compile: in one invocation,
# a target that asks nothing after one that asked stamps "", not the first's
mkdir -p "$WORKDIR/o22"
if pcrec_run "$PCREC" $FEAT -o "$WORKDIR/o22" "$R/multi.rxt" >/dev/null 2>"$WORKDIR/res.err" &&
   [ "$(anystamp "$WORKDIR/o22/t_asks.c")" = "byte-rate=default:$DDEF" ] &&
   [ -z "$(anystamp "$WORKDIR/o22/t_quiet.c")" ] &&
   grep -q '_FINDINGS ""' "$WORKDIR/o22/t_quiet.c"; then
    ok "§6 [#22] a target asking nothing after one that asked stamps \"\" (the record is per compile)"
else
    bad "§6 [#22] the second target's stamp is \"$(anystamp "$WORKDIR/o22/t_quiet.c" 2>/dev/null)\" — a consumption record leaked across compiles (design §6.4)"
fi
# the -I lift's other half: still refused where nothing resolves (r2 M-S7)
if "$PCREC" -I "$R/A" --list-syntax >/dev/null 2>&1; then
    bad "§6 [-I] -I with --list-syntax was accepted; it resolves no bundle"
else
    ok "§6 [-I] -I is refused where nothing resolves a bundle (--list-syntax)"
fi

# =========================================================================
# §7 REACH ([B2]; design §11.1 [r2 S-F3]) — each fire-<reader> bundle must
# still MOVE its reader's stamp on its recorded population; a zero is red.
# =========================================================================
while IFS=$'\t' read -r tag b n rest; do
    [ "$tag" = REACH ] || continue
    if [ "$n" -gt 0 ]; then ok "§7 $b moves its reader on $n $rest artifact-configs (REACH)"
    else bad "§7 $b moves its reader on NOTHING ($rest) — it proves nothing about answer identity"; fi
done < <(PCREC="$PCREC" python3 "$SCRIPT_DIR/gen_adversarial.py" reach 2>&1)

# =========================================================================
# §8 WITNESSES ([B2]; design §11.9) — one constructed pattern + bundle per
# reader C1-C4, both values pinned.
# =========================================================================
while IFS=$'\t' read -r v rest; do
    case "$v" in PASS) ok "§8 $rest" ;; FAIL) bad "§8 $rest" ;; esac
done < <(PCREC="$PCREC" python3 "$SCRIPT_DIR/gen_adversarial.py" witness 2>&1)

# =========================================================================
# §9 GIVE-UP IDENTITY ([B2]; design §6.2a, §11.2 F-12/F-13) — a rate may not
# switch a give-up. K65's repro (a framed VM artifact, no DFA in front) must
# answer NOMATCH on subjects lacking either necessary member, under the
# default, under a bundle making `Z` the rarest member (pick Z), under one
# making `@` rarest (pick @), and under fire-c3 — on both encodings. A
# give-up (exit 3) here is a transition a speed choice caused.
# =========================================================================
gu_fail=0; gu_n=0
for enc in byte utf8; do
    for an in "" pickz picka fire-c3; do
        dir="$R/A"; [ "$an" = fire-c3 ] && dir="$SCRIPT_DIR/adversarial"
        args=(); [ -n "$an" ] && args=(-I "$dir" --analysis "$an")
        exe="$WORKDIR/gu_${enc}_${an:-default}"
        if ! pcrec_run "$PCREC" -p rx -e "$enc" $FEAT --step-budget=10000 --emit-main \
                "${args[@]}" -o "$exe.c" --pattern "$PAT" >/dev/null 2>&1 ||
           ! gen_cc "findings giveup witness" "$CC" -O1 -o "$exe" "$exe.c" >/dev/null 2>&1; then
            bad "§9 the K65 witness did not build under ${an:-default}/$enc"; gu_fail=1; continue
        fi
        for s in aaaaaaaaaaaaaaaaZb aaaaaaaaaaaaaaaaaZb aaaaaaaaaaaaaaaa@b aaaaaaaaaaaaaaaaa@b; do
            gu_n=$((gu_n + 1))
            "$exe" "$s" >/dev/null 2>&1; rc=$?
            if [ "$rc" != 1 ]; then
                bad "§9 K65 witness under ${an:-default}/$enc on '$s' exits $rc, want 1 (NOMATCH) — a rate switched a give-up"
                gu_fail=1
            fi
        done
    done
done
[ "$gu_fail" = 0 ] && ok "§9 the K65 witness answers NOMATCH on all $gu_n cells (4 analyses x 2 encodings x 4 subjects): 0 give-up transitions"

# =========================================================================
# §10 THE SAMPLED ANSWER-IDENTITY SLICE ([B2]; design §11.1, [r2 S-F1]):
# a fixed slice of the corpus under EVERY adversarial bundle, through
# tests/axes/run_axes.sh's own answer comparison — answers identical to the
# default AND no give-up transition, the second counted as its own
# population (GIVEUP1) and required to be ZERO. The whole corpus under every
# bundle is the FINDINGS axis of `make test-axes` (AXES=--analysis).
# =========================================================================
SLICE=(tests/base/k65_precheck_whole_set.rxt tests/base/k66_precheck_whole_run.rxt
       tests/harness/giveup.rxt tests/offsetskip tests/litscan/litrun.rxt
       tests/base/alternation.rxt)
if [ "${FINDINGS_SKIP_SLICE:-0}" = 1 ]; then
    echo "INFO: §10 skipped (FINDINGS_SKIP_SLICE=1)"
else
    ( cd "$ROOT_DIR" && AXES="--analysis" SKIP_ORACLE=1 PCREC="$PCREC" \
          bash tests/axes/run_axes.sh "${SLICE[@]}" ) > "$WORKDIR/slice.log" 2>&1
    slice_rc=$?
    nax="$(grep -c 'giveup1-unallowed=' "$WORKDIR/slice.log")"
    ngu="$(grep -o 'giveup1-unallowed=[0-9]*' "$WORKDIR/slice.log" | awk -F= '{t+=$2} END{print t+0}')"
    nmm="$(grep -o ' mismatches=[0-9]*' "$WORKDIR/slice.log" | awk -F= '{t+=$2} END{print t+0}')"
    nag="$(grep -o 'agree=[0-9]*' "$WORKDIR/slice.log" | awk -F= '{t+=$2} END{print t+0}')"
    nbundles="$(ls "$SCRIPT_DIR"/adversarial/*.rxt | wc -l | tr -d ' ')"
    if [ "$slice_rc" = 0 ] && [ "$nax" = "$nbundles" ] && [ "$ngu" = 0 ] && [ "$nmm" = 0 ] && [ "$nag" -gt 0 ]; then
        ok "§10 the sampled slice under all $nax adversarial bundles: $nag answers agree, mismatches=0, give-up transitions (GIVEUP1)=0"
    else
        bad "§10 the sampled slice: rc=$slice_rc bundles=$nax/$nbundles agree=$nag mismatches=$nmm GIVEUP1=$ngu — see:"
        grep -E 'AXIS FAIL|giveup1-unallowed' "$WORKDIR/slice.log" | head -20 >&2
    fi
fi

# =========================================================================
# §11 THE TABLE CONTRACT ([B2]; table_contract.md, design §5.2 [r2 M-S10]):
# both listings are producers AT BIRTH — every section's rows carry exactly
# its header's field count, and a TAB in a user bundle's prose is escaped
# rather than splitting its row.
# =========================================================================
. "$ROOT_DIR/tests/lib/table.sh"
"$PCREC" --list-analyses > "$WORKDIR/t11a" 2>/dev/null
"$PCREC" --list-analysis tabq -I "$R/A" > "$WORKDIR/t11b" 2>/dev/null
"$PCREC" --list-analysis "$R/view.rxt" -I "$R/A" --analysis ord > "$WORKDIR/t11c" 2>/dev/null
t11=0
table_check_truthfulness "$WORKDIR/t11a" >/dev/null 2>"$WORKDIR/t11.err" || t11=1
for sec in chain resolution freq declarations provenance; do
    table_check_truthfulness "$WORKDIR/t11b" "$sec" >/dev/null 2>>"$WORKDIR/t11.err" || t11=1
done
for sec in targets chain resolution; do
    table_check_truthfulness "$WORKDIR/t11c" "$sec" >/dev/null 2>>"$WORKDIR/t11.err" || t11=1
done
if [ "$t11" = 0 ]; then
    ok "§11 --list-analyses and both --list-analysis views: every section's rows match their header's field count"
else
    bad "§11 a listing row's field count differs from its header: $(head -c 300 "$WORKDIR/t11.err")"
fi
if grep -qF 'has\x09a tab' "$WORKDIR/t11b"; then
    ok "§11 a TAB in a bundle's question is escaped as \\x09 in the declarations section"
else
    bad "§11 a TAB in a bundle's question was not escaped (table_contract.md producer rule 5)"
fi

echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
