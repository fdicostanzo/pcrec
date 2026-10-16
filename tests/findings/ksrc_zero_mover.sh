#!/usr/bin/env bash
# tests/findings/ksrc_zero_mover.sh OLD_PCREC NEW_PCREC — [KNOW-SRC] K1/K2's
# RESOLUTION zero-mover witness (docs/design/measure_sets.md rev 3 §9.7):
# every resolution surface the knowledge module took over, run under two
# binaries from the same working directory, compared BYTE FOR BYTE — exit
# code, stdout and stderr, and every artifact a file operand writes.
#
#   1  the analysis stops: res_fixtures.py's -I fixtures (S2 of another name
#      falling through WITH its note, a two-bundle file refusing, an unknown
#      name's stop list, the case-exact entry, `-I d/`'s join, include
#      cycles/depth, a bad name), each under -I A -I B and -I B -I A;
#   2  the listings: --list-analyses, and --list-analysis in both
#      classifications (a NAME and a FILE spelling) over the shipped bundles
#      and the fixtures;
#   3  the fill-only CLI on the fixtures' config files (the note's text);
#   4  `lib` resolution: every .rxt/.rxtin under tests/rxtsource/ and
#      tests/definitions/ compiled as a file operand, with no --lib-path and
#      with the fixture directory as one (the existence refusal's text and
#      every resolved library's artifacts).
#
# Not run by `make`: it is the K1 and K2 gates' instrument, needs two
# binaries, and is cheap (a few hundred compiles). The emitted-artifact
# corpus is scripts/emit_sweep.py's, not this script's. Prints one line per
# DIFF and a summary; exit 0 iff every case is identical AND the population
# is at least its floor (an empty run must not read as identical, K35).
set -u
export LC_ALL=C
OLD="$1"; NEW="$2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
W="$(mktemp -d)"
trap 'rm -rf "$W"' EXIT
python3 "$SCRIPT_DIR/res_fixtures.py" "$W/r"
R="$W/r"
n=0; ndiff=0
FLOOR=150

# one ARGS...: both binaries, from $R, artifacts into a fresh dir each.
one() {
    local side bin
    for side in old new; do
        [ $side = old ] && bin="$OLD" || bin="$NEW"
        rm -rf "$W/$side"; mkdir -p "$W/$side/o"
        ( cd "$R" && "$bin" "${@//@OUT@/$W/$side/o}" ) \
            > "$W/$side/stdout" 2> "$W/$side/stderr"
        echo "rc=$?" >> "$W/$side/stdout"
        # the output dir's path is the only byte the two sides may differ by
        sed -i "s#$W/$side/o#@OUT@#g" "$W/$side/stdout" "$W/$side/stderr"
    done
    n=$((n + 1))
    if ! diff -r "$W/old" "$W/new" > "$W/d" 2>&1; then
        ndiff=$((ndiff + 1))
        echo "DIFF: $*"; head -8 "$W/d" | sed 's/^/    /'
    fi
}

PAT='(x?)([a-z]+)+Z.@\1'
for dirs in "-I A -I B" "-I B -I A" "-I A/ -I B/" "-I $R/A"; do
    for name in shadow ord default cyca d1 d2 d9 lib two other mixed Mixed \
                withdef byteonly tabq prov nosuch Bad 9x ""; do
        # shellcheck disable=SC2086
        one $dirs --features all -p rx -o - --analysis "$name" --pattern "$PAT"
        # shellcheck disable=SC2086
        one $dirs --features all -p rx -e utf8 -o - --analysis "$name" --pattern "$PAT"
    done
    for name in default log weblog shadow ord lib two Mixed nosuch; do
        # shellcheck disable=SC2086
        one $dirs --list-analysis "$name"
    done
    # shellcheck disable=SC2086
    one $dirs --list-analyses
    for f in s1_shadow.rxt dup.rxt fill.rxt pcrecline.rxt view.rxt multi.rxt \
             A/two.rxt B/lib.rxt nonexistent.rxt; do
        # shellcheck disable=SC2086
        one $dirs --list-analysis "$f"
        # shellcheck disable=SC2086
        one $dirs --features all "$f" -o @OUT@
        # shellcheck disable=SC2086
        one $dirs --features all --analysis ord "$f" -o @OUT@
        # shellcheck disable=SC2086
        one $dirs --features all --analysis shadow "$f" -o @OUT@
    done
done
one --list-analyses
one -I P1 --analysis prov -p rx -o - --pattern abc

while IFS= read -r f; do
    one --features all "$f" -o @OUT@
    one --features all --lib-path "$(dirname "$f")" "$f" -o @OUT@
    one --features all --lib-path "$ROOT_DIR/tests/rxtsource/fixtures/" "$f" -o @OUT@
done < <(find "$ROOT_DIR/tests/rxtsource" "$ROOT_DIR/tests/definitions" \
              -name '*.rxt' -o -name '*.rxtin' | sort)

echo "ksrc_zero_mover: $n cases, $ndiff differ (floor $FLOOR)"
[ "$n" -ge "$FLOOR" ] && [ "$ndiff" = 0 ]
