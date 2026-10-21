#!/usr/bin/env bash
# tests/knowledge/run_measures_tests.sh — [MEASURE-SET] M0: the MEASURES
# kind's round trip, store and loading (docs/design/measure_sets.md rev 3
# §3, §8.3, §9.6; docs/spec/measures.md is the contract). Called by
# run_knowledge_tests.sh (`make test-knowledge`), whose trailer adds its counts.
#
#   STORE   every measure_store/<id>/<rev>/set.tsv: R4 (the committed file IS
#           its canonical view), R5 (pcrec's decoded view of the stored set =
#           ks_ref.py's decode of the FILE), its index.tsv row (sha-256 by
#           sha256sum, digest by ks_ref), DEFAULTS read by awk against the
#           listing's `default_for` and against DEFAULTS.log's last row per
#           class, and the EMBEDDED store (meas_store_check.c: the embedded
#           text = the file, the pre-parse = a fresh parse of that text).
#   ROUND   every mfixtures.py `ok/` set: R1 (the item digest of its
#           canonical view, re-loaded), R2 (the canonical view is a fixed
#           point), R3 (ks_ref.py reads the file and its canonical view as one
#           document) and R5; the canonical view compiles as `--measures=FILE`.
#   REFUSE  every `bad/` set refuses with its class's text (§7); a decoded
#           view fed back refuses as a FILE and through `-I`.
#   LOAD    the default compile stamps `""` with `rx_info.measures` equal to
#           the macro; `-I`, `NAME@REV`, the S2 mismatch, the shadow rule, an
#           unknown name; the config line and fill-only; the `pcrec`-line
#           refusal; the flag's reach.
#   CONTROLS R5 on a decode with two rows swapped, R3 on a canonical view with
#           its `cells` dropped (R1's digest unmoved by that edit).
#
# Population floors (K35): store sets >= 1, ok fixtures = 4, bad fixtures >= 20.
set -u
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
LIBA="${PCREC%/*}/libpcrec.a"
CC="${CC:-gcc}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT
pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
REF="python3 -I $SCRIPT_DIR/ks_ref.py"
LM() { pcrec_run "$PCREC" "$@"; }
item_digest() { awk -F'\t' '/^#section /{s = ($0 == "#section item")} s && $1 ~ /^[0-9]+$/ {print $2}' "$1"; }

# ---- STORE ----------------------------------------------------------------
nstore=0
for f in "$ROOT_DIR"/measure_store/*/*/set.tsv; do
    [ -f "$f" ] || continue
    nstore=$((nstore + 1))
    rev="$(basename "$(dirname "$f")")"; id="$(basename "$(dirname "$(dirname "$f")")")"
    if LM --list-measurements="$id@$rev" > "$WORKDIR/canon" 2> "$WORKDIR/err" &&
       cmp -s "$WORKDIR/canon" "$f"; then
        ok "store $id@$rev: R4, the committed file is its canonical view"
    else
        bad "store $id@$rev: R4 — the canonical view differs from the committed file ($(head -c 200 "$WORKDIR/err"))"
    fi
    LM --list-measurements="$id@$rev" --view=decoded > "$WORKDIR/cdec" 2>/dev/null
    $REF decode "$f" > "$WORKDIR/pdec"
    if cmp -s "$WORKDIR/cdec" "$WORKDIR/pdec"; then
        ok "store $id@$rev: R5, pcrec's decode = the independent reader's ($(wc -l < "$WORKDIR/cdec") lines)"
    else
        bad "store $id@$rev: R5 — decoded views differ: $(diff "$WORKDIR/pdec" "$WORKDIR/cdec" | head -4 | tr '\n' ' ' | cut -c1-300)"
    fi
    sha="$(sha256sum "$f" | cut -d' ' -f1)"; dig="$($REF digest "$f")"
    row="$(awk -F'\t' -v i="$id" -v r="$rev" '$1 == i && $2 == r' "$ROOT_DIR/measure_store/index.tsv")"
    if [ -n "$row" ] && [ "$(printf '%s' "$row" | cut -f10)" = "$sha" ] &&
       [ "$(printf '%s' "$row" | cut -f9)" = "$dig" ] &&
       grep -q "$sha" "$(dirname "$f")/PROVENANCE.md"; then
        ok "store $id@$rev: index.tsv and PROVENANCE.md carry its sha-256 and digest"
    else
        bad "store $id@$rev: index.tsv/PROVENANCE.md disagree with the file (sha $sha, digest $dig)"
    fi
done
[ "$nstore" -ge 1 ] && ok "store: $nstore set(s) (floor 1)" || bad "store: no set under measure_store/ (K35)"

# DEFAULTS by awk, against the listing and the log
LM --list-measurements > "$WORKDIR/index" 2>/dev/null
dbad=0; ndef=0
while IFS="$(printf '\t')" read -r cls ir; do
    case "$cls" in ''|\#*) continue ;; esac
    ndef=$((ndef + 1))
    lid="${ir%@*}"; lrev="${ir#*@}"
    got="$(awk -F'\t' -v i="$lid" -v r="$lrev" '/^#section /{s = ($0 == "#section sets")} s && $1 == i && $2 == r {print $8}' "$WORKDIR/index")"
    last="$(awk -F'\t' -v c="$cls" '$2 == c {v = $4} END {print v}' "$ROOT_DIR/measure_store/DEFAULTS.log")"
    [ "$got" = "$cls" ] || { dbad=1; echo "  default $cls -> $ir: the listing's default_for reads '$got'" >&2; }
    [ "${last%%:*}" = "$ir" ] || { dbad=1; echo "  default $cls -> $ir: DEFAULTS.log's last row names '$last'" >&2; }
done < "$ROOT_DIR/measure_store/DEFAULTS"
if [ "$dbad" -eq 0 ] && [ "$ndef" -ge 1 ]; then
    ok "DEFAULTS ($ndef row(s), read by awk) = the build's default_for = DEFAULTS.log's last row per class"
else
    bad "DEFAULTS disagrees with the built pointer table or with DEFAULTS.log ($ndef rows)"
fi

# the embedded store
if "$CC" -std=gnu11 -O1 -I"$ROOT_DIR/src" -I"$ROOT_DIR/lib" -o "$WORKDIR/msc" \
       "$SCRIPT_DIR/meas_store_check.c" "$LIBA" 2> "$WORKDIR/cc.err"; then
    mkdir -p "$WORKDIR/emb"
    if "$WORKDIR/msc" "$WORKDIR/emb" > "$WORKDIR/emb.lst"; then
        ebad=0; nemb=0
        while IFS="$(printf '\t')" read -r name dig rows; do
            nemb=$((nemb + 1))
            f="$ROOT_DIR/measure_store/${name%@*}/${name#*@}/set.tsv"
            cmp -s "$WORKDIR/emb/$name.text" "$f" || { ebad=1; echo "  $name: embedded text != $f" >&2; }
            cmp -s "$WORKDIR/emb/$name.pre" "$WORKDIR/emb/$name.fresh" || { ebad=1; echo "  $name: pre-parse != a fresh parse of the embedded text" >&2; }
        done < "$WORKDIR/emb.lst"
        if [ "$ebad" -eq 0 ] && [ "$nemb" -eq "$nstore" ]; then
            ok "embedded store: $nemb set(s), text = file and pre-parse = fresh parse"
        else
            bad "embedded store: $nemb embedded against $nstore committed, or a text/pre-parse mismatch (make gen-measures)"
        fi
    else
        bad "embedded store: meas_store_check refused"
    fi
else
    bad "embedded store: meas_store_check.c does not compile: $(head -3 "$WORKDIR/cc.err" | tr '\n' ' ')"
fi

# ---- ROUND ----------------------------------------------------------------
STORE_SET="$(ls "$ROOT_DIR"/measure_store/*/*/set.tsv | head -1)"
python3 -I "$SCRIPT_DIR/mfixtures.py" "$STORE_SET" "$WORKDIR/fx"
nok=0
for f in "$WORKDIR"/fx/ok/*.tsv; do
    n="$(basename "$f" .tsv)"; nok=$((nok + 1))
    if ! LM --list-measurements="$f" > "$WORKDIR/$n.c1" 2> "$WORKDIR/$n.err"; then
        bad "$n: does not load: $(head -c 300 "$WORKDIR/$n.err")"; continue
    fi
    LM --list-measurements="$f" --view=decoded > "$WORKDIR/$n.d0" 2>/dev/null
    LM --list-measurements="$WORKDIR/$n.c1" > "$WORKDIR/$n.c2" 2>/dev/null
    LM --list-measurements="$WORKDIR/$n.c1" --view=decoded > "$WORKDIR/$n.d1" 2>/dev/null
    d0="$(item_digest "$WORKDIR/$n.d0")"; d1="$(item_digest "$WORKDIR/$n.d1")"
    [ -n "$d0" ] && [ "$d0" = "$d1" ] && ok "$n: R1, the canonical view re-loads to digest $d0" \
        || bad "$n: R1 — digest $d0 then $d1"
    cmp -s "$WORKDIR/$n.c1" "$WORKDIR/$n.c2" && ok "$n: R2, the canonical view is a fixed point" \
        || bad "$n: R2 — the canonical view of the canonical view moved"
    $REF doc "$f" > "$WORKDIR/$n.doc0"; $REF doc "$WORKDIR/$n.c1" > "$WORKDIR/$n.doc1"
    cmp -s "$WORKDIR/$n.doc0" "$WORKDIR/$n.doc1" && ok "$n: R3, the independent reader reads file and canonical view as one document" \
        || bad "$n: R3 — documents differ: $(diff "$WORKDIR/$n.doc0" "$WORKDIR/$n.doc1" | head -4 | tr '\n' ' ' | cut -c1-300)"
    $REF decode "$f" > "$WORKDIR/$n.pd"
    cmp -s "$WORKDIR/$n.d0" "$WORKDIR/$n.pd" && ok "$n: R5, pcrec's decode = the independent reader's" \
        || bad "$n: R5 — $(diff "$WORKDIR/$n.pd" "$WORKDIR/$n.d0" | head -4 | tr '\n' ' ' | cut -c1-300)"
    if LM --measures="$WORKDIR/$n.c1" -o "$WORKDIR/$n.out.c" --pattern 'ab+c' 2> "$WORKDIR/$n.cerr"; then
        ok "$n: its canonical view compiles as --measures=FILE"
    else
        bad "$n: its canonical view does not load as --measures=FILE: $(head -c 300 "$WORKDIR/$n.cerr")"
    fi
done
[ "$nok" -eq 4 ] && ok "round trip: 4 fixtures" || bad "round trip: $nok fixtures, expected 4 (K35)"
# fx-messy normalizes to fx-store: one document, one canonical view but the id
sed 's/^id\tfx-messy$/id\tfx-store/' "$WORKDIR/fx-messy.c1" > "$WORKDIR/messy.as.store"
cmp -s "$WORKDIR/messy.as.store" "$WORKDIR/fx-store.c1" && ok "fx-messy's canonical view is fx-store's (order, comments, unknown column, absent key normalized)" \
    || bad "fx-messy does not normalize to fx-store: $(diff "$WORKDIR/fx-store.c1" "$WORKDIR/messy.as.store" | head -4 | tr '\n' ' ')"

# ---- REFUSE ---------------------------------------------------------------
nbad=0
while IFS="$(printf '\t')" read -r n sub; do
    [ -n "$n" ] || continue
    nbad=$((nbad + 1))
    if LM --list-measurements="$WORKDIR/fx/bad/$n.tsv" > /dev/null 2> "$WORKDIR/b.err"; then
        bad "refuse $n: the set LOADED"
    elif grep -qF -- "$sub" "$WORKDIR/b.err"; then
        ok "refuse $n: '$sub'"
    else
        bad "refuse $n: refused without '$sub': $(head -c 300 "$WORKDIR/b.err")"
    fi
done < "$WORKDIR/fx/bad/EXPECT.tsv"
[ "$nbad" -ge 20 ] && ok "refusals: $nbad classes (floor 20)" || bad "refusals: $nbad classes, under the floor 20 (K35)"
if LM --measures="$WORKDIR/fx/bad/digest.tsv" -o "$WORKDIR/x.c" --pattern a 2> "$WORKDIR/b.err"; then
    bad "a bad set as --measures= compiled"
else
    ok "a bad set as --measures= refuses the compile"
fi
LM --list-measurements=zen4-grid1 --view=decoded > "$WORKDIR/fed.tsv" 2>/dev/null
mkdir -p "$WORKDIR/fedI"; cp "$WORKDIR/fed.tsv" "$WORKDIR/fedI/zen4-grid1.measures.tsv"
if ! LM --measures="$WORKDIR/fed.tsv" -o "$WORKDIR/x.c" --pattern a 2> "$WORKDIR/b.err" &&
   grep -q "derived view" "$WORKDIR/b.err" &&
   ! LM -I "$WORKDIR/fedI" --measures=zen4-grid1 -o "$WORKDIR/x.c" --pattern a 2> "$WORKDIR/b2.err" &&
   grep -q "derived view" "$WORKDIR/b2.err"; then
    ok "a decoded view fed back refuses as a FILE and through -I, naming the derived section"
else
    bad "a decoded view fed back was accepted, or refused without naming its section"
fi

# ---- LOAD -----------------------------------------------------------------
LM -o "$WORKDIR/d.c" --pattern 'a(b|c)+d' 2>/dev/null
mac="$(sed -n 's/^#define RX_MEASURES \(.*\)$/\1/p' "$WORKDIR/d.c")"
ini="$(sed -n 's/^    \.measures = \(.*\),$/\1/p' "$WORKDIR/d.c")"
if [ "$mac" = '""' ] && [ "$ini" = "$mac" ]; then
    ok "a default compile stamps RX_MEASURES \"\" and rx_info.measures is the same text (no reader consults a set)"
else
    bad "the default compile stamps RX_MEASURES '$mac' with rx_info.measures '$ini'"
fi
I="$WORKDIR/fx/idir"
expect_ok()  { if LM "$@" -o "$WORKDIR/x.c" --pattern a 2> "$WORKDIR/l.err"; then ok "loads: $*"; else bad "should load: $* ($(head -c 200 "$WORKDIR/l.err"))"; fi; }
expect_bad() { local sub="$1"; shift
    if LM "$@" -o "$WORKDIR/x.c" --pattern a 2> "$WORKDIR/l.err"; then bad "should refuse: $*"
    elif grep -qF -- "$sub" "$WORKDIR/l.err"; then ok "refuses: $* ('$sub')"
    else bad "refuses $* without '$sub': $(head -c 200 "$WORKDIR/l.err")"; fi; }
expect_ok --measures=zen4-grid1
expect_ok --measures=zen4-grid1@1
expect_ok -I "$I" --measures=mine
expect_ok --measures="$STORE_SET"
expect_bad "has no committed rev 2" --measures=zen4-grid1@2
expect_bad "unknown measurement set 'nosuch' (searched: -I $I, the built-in store)" -I "$I" --measures=nosuch
expect_bad "defines no measurement set 'other'" -I "$I" --measures=other
expect_bad "carries mine@1, not mine@2" -I "$I" --measures=mine@2
expect_bad "has no committed rev 7" --measures="$WORKDIR/fx/shadow/rev7.tsv"
expect_bad "is a committed measurement set with different values" --measures="$WORKDIR/fx/shadow/values.tsv"
expect_bad "cannot open" --measures=./no-such-file.tsv
# the config line and fill-only
printf 'config c\n    measures zen4-grid1@1\n\ntarget t = p with c\n\npattern ab+c\nname p\n' > "$WORKDIR/f.rxt"
if LM --measures=./no-such-file.tsv -o "$WORKDIR/f.c" "$WORKDIR/f.rxt" 2> "$WORKDIR/f.err" &&
   grep -q "CLI --measures ./no-such-file.tsv and this file's measures zen4-grid1@1 disagree; using the file's value (--measures is fill-only)" "$WORKDIR/f.err"; then
    ok "the config's measures line wins over --measures and the note names both (fill-only)"
else
    bad "fill-only broken: the CLI value won or no note ($(head -c 300 "$WORKDIR/f.err"))"
fi
printf 'config c\n    measures ./no-such-file.tsv\n\ntarget t = p with c\n\npattern ab+c\nname p\n' > "$WORKDIR/g.rxt"
if ! LM -o "$WORKDIR/g.c" "$WORKDIR/g.rxt" 2> "$WORKDIR/g.err" && grep -q "cannot open" "$WORKDIR/g.err"; then
    ok "a config's measures line is the set its target compiles under"
else
    bad "a config's measures line was not read"
fi
printf 'config c\n    pcrec --measures=zen4-grid1\n\ntarget t = p with c\n\npattern ab+c\nname p\n' > "$WORKDIR/h.rxt"
if ! LM -o "$WORKDIR/h.c" "$WORKDIR/h.rxt" 2> "$WORKDIR/h.err" && grep -q "'pcrec' may not carry '--measures'" "$WORKDIR/h.err"; then
    ok "a config's pcrec line may not carry --measures"
else
    bad "a pcrec line carrying --measures was not refused"
fi
if ! LM --measures=zen4-grid1 --list-syntax > /dev/null 2> "$WORKDIR/q.err" &&
   ! LM --list-measurements --pattern a > /dev/null 2>> "$WORKDIR/q.err"; then
    ok "--measures with a query, and --list-measurements with a pattern, are refused"
else
    bad "--measures reached a query, or --list-measurements took a pattern"
fi

# ---- CONTROLS -------------------------------------------------------------
c="$WORKDIR/fx-rich"
awk 'NR == 30 {h = $0; next} NR == 31 {print; print h; next} {print}' "$c.d0" > "$WORKDIR/ctl_swap"
if ! cmp -s "$WORKDIR/ctl_swap" "$c.pd"; then
    ok "control: R5 fails on a decode with two rows swapped"
else
    bad "control: R5 cannot see two swapped rows"
fi
awk '/^#section cells/ {skip = 1} /^#section members/ {skip = 0} !skip || /^#section cells/ || /^#cell/' "$c.c1" > "$WORKDIR/ctl_cells.tsv"
$REF doc "$WORKDIR/ctl_cells.tsv" > "$WORKDIR/ctl_cells.doc"
d2="$($REF digest "$WORKDIR/ctl_cells.tsv")"
if ! cmp -s "$WORKDIR/ctl_cells.doc" "$c.doc0" && [ "$d2" = "$(item_digest "$c.d0")" ]; then
    ok "control: R3 sees a canonical view with its cells dropped, which leaves R1's digest unmoved"
else
    bad "control: dropping the cells is invisible to R3, or moved the digest"
fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
