#!/usr/bin/env bash
# [OPT-FIRSTSET] §4.5 — THE WITNESS RUN (lane fsreconcile, 2026-09-22).
#
# Reproduces everything `firstset_design.md` §4.5 measures, from a pcrec
# build and nothing else.  ANSWERS ONLY: no clock is read anywhere, on
# purpose -- the lane ran on darwin.
#
# Three artifacts per pattern, emitted at three DIFFERENT `-p` prefixes so
# all three link into one comparator:
#   rx   the shipped artifact, untouched
#   tw   the twin: `<p>_can_begin_match` overwritten with the AST-level
#        first-byte set (cycle1_analysis.md M3's narrowing)
#   rs   the twin plus `firstset_design.md` §4.4's two-line re-seed
#
# Env: PCREC (a pcrec build), CC (default gcc-16), OUT (default .)
set -u
PCREC="${PCREC:?set PCREC to a pcrec build}"
CC="${CC:-gcc-16}"
OUT="${OUT:-.}"
HERE="$(cd "$(dirname "$0")" && pwd)"
W="$(mktemp -d)"; trap 'rm -rf "$W"' EXIT

# ---- the two patterns, and the first-byte set each one's narrowing uses.
#      json-constant is firstset_design.md §4.1's own witness pattern; the
#      second is a SHORTER \b-leading pattern whose minimal lost-match
#      witness is 6 bytes rather than 10, which is the only reason an
#      exhaustive sweep can reach it at all.
PAT1='\b(?:true|false|null)\b'; SET1='t,f,n'
PAT2='\b(?:ab|cd)\b';           SET2='a,c'

emit3() {   # emit3 <tag> <pattern> <first-byte set>
    local tag="$1" pat="$2" set="$3" p
    for p in rx tw rs; do
        "$PCREC" --features all --no-captures -p "$p" -o "$W/${tag}_$p.c" \
                 --pattern "$pat" >/dev/null || { echo "compile failed: $pat"; return 1; }
    done
    SET="$set" python3 - "$W/${tag}_tw.c" tw "$W/${tag}_rs.c" rs <<'PY'
import os, re, sys
keep = {ord(c) for c in os.environ["SET"].split(",")}
vals = ", ".join("1" if i in keep else "0" for i in range(256))
def narrow(path, pfx):
    src = open(path).read()
    m = re.search(r"(static const unsigned char %s_can_begin_match\[256\] = \{)(.*?)(\};)" % pfx, src, re.S)
    assert m, "no %s_can_begin_match -- artifact shape changed, STOP" % pfx
    open(path,"w").write(src[:m.start()] + m.group(1) + "\n        " + vals + "\n    " + m.group(3) + src[m.end():])
def reseed(path, pfx):
    src = open(path).read()
    old = ("        if (forward_state == 0 && last_accept_position == (size_t)-1) {\n"
           "            while (scan_position + 1 < subject_length && !%s_can_begin_match[subject[scan_position]]) scan_position++;\n"
           "        }\n") % pfx
    assert src.count(old) == 1, "skip-loop block count %d -- STOP" % src.count(old)
    new = ("        if (forward_state == 0 && last_accept_position == (size_t)-1) {\n"
           "            size_t entry_position = scan_position;\n"
           "            while (scan_position + 1 < subject_length && !%s_can_begin_match[subject[scan_position]]) scan_position++;\n"
           "            if (scan_position > entry_position)\n"
           "                forward_state = %s_forward_seed_state[%s_forward_byte_class[subject[scan_position - 1]]];\n"
           "        }\n") % (pfx, pfx, pfx)
    open(path,"w").write(src.replace(old, new, 1))
narrow(sys.argv[1], sys.argv[2])
narrow(sys.argv[3], sys.argv[4]); reseed(sys.argv[3], sys.argv[4])
PY
}

echo "== [OPT-FIRSTSET] §4.5 witness run"
echo "== pcrec: $("$PCREC" --version 2>&1 | head -1)"
echo

# ---- (1) the structured witness set on json-constant, spans printed.
emit3 j "$PAT1" "$SET1" || exit 1
python3 - > "$W/subjects.txt" <<'PY'
# <ctx> x <keyword> x <tail>.  The ctx column is the whole finding: a WORD
# byte before the keyword is one the narrowed set skips and the shipped set
# does not, and the ` true` tail is what turns a vetoed spurious accept into
# an observably DELETED match.
for c in ("", "a", "_", "9", " ", "-"):
    for k in ("true", "false", "null"):
        for t in ("", " ", "x", " true"):
            print(c + k + t)
PY
for v in rx tw rs; do
    cp "$W/j_$v.h" "$W/art.h"
    V="$(printf '%s' "$v" | tr 'a-z' 'A-Z')"
    $CC -O2 -I"$W" -D"ART_SEARCH=${v}_search" -D"ART_NCAPS=${V}_NCAPS" \
        -o "$W/w_$v" "$HERE/firstset_witness.c" "$W/j_$v.c" || exit 1
done
for v in rx tw rs; do "$W/w_$v" "$W/subjects.txt" > "$W/out_$v.txt"; done
echo "-- (1) structured set, $(wc -l < "$W/subjects.txt" | tr -d ' ') subjects, pattern $PAT1"
echo "   shipped vs narrowed twin:"
diff "$W/out_rx.txt" "$W/out_tw.txt" | sed 's/^/   /' || true
echo "   twin disagreements: $(diff "$W/out_rx.txt" "$W/out_tw.txt" | grep -c '^<')"
echo "   reseed disagreements: $(diff "$W/out_rx.txt" "$W/out_rs.txt" | grep -c '^<')"
echo

# ---- (2) the exhaustive comparator, both patterns.
# The two patterns are swept side by side.  Parallel arrays rather than a
# delimited spec string: every plausible delimiter occurs inside a PCRE.
TAGS=(e1 e2); PATS=("$PAT1" "$PAT2"); SETS=("$SET1" "$SET2")
ALPHAS=("atrue " "abcdx "); MAXLENS=(8 8)
for i in 0 1; do
    tag="${TAGS[$i]}"
    emit3 "$tag" "${PATS[$i]}" "${SETS[$i]}" || exit 1
    sed -e "s/\"json.h\"/\"${tag}_rx.h\"/" -e "s/\"tw.h\"/\"${tag}_tw.h\"/" \
        -e "s/\"rs.h\"/\"${tag}_rs.h\"/" "$HERE/firstset_exhaust.c" > "$W/ex_$tag.c"
    $CC -O2 -I"$W" -o "$W/ex_$tag" "$W/ex_$tag.c" \
        "$W/${tag}_rx.c" "$W/${tag}_tw.c" "$W/${tag}_rs.c" || exit 1
    echo "-- (2) exhaustive, pattern ${PATS[$i]}  alphabet '${ALPHAS[$i]}' maxlen ${MAXLENS[$i]}"
    "$W/ex_$tag" "${ALPHAS[$i]}" "${MAXLENS[$i]}" | tail -3 | sed 's/^/   /'
    echo
done
echo "== done"
