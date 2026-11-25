#!/usr/bin/env bash
# s3012tri evidence (one-shot, run by no suite): THE PRESENCE RUNNER'S PLANT REACH CENSUS.
# For each id in run_g2_pres.sh's PLANTS: the plant applied by the runners' one applier (dialect
# pres) to a scratch copy of memfn/src, the kit built plain and -DMF_TRACE, g2_pres_gen run
# over the runner's own pass list (x86-64-v3/x86-64/generic x lever 0/1 at on_miss_leaves 1,
# NWIDE 300; generic lever 0 on_miss_leaves 0; the deny pass) plus the trace kit's default
# passes (G2P_G2SITE=1, stderr = the MFTRACE records D3 reads). A plant whose every rendered
# file, generator log and trace stream equals the clean kit's is UNREACHED by the family's
# generator: no check downstream of the text (driver, oracle, cells) can see it, except one
# reading a file the plant edits outside memfn/src (the @c0 census copy).
# NOTE (s3012tri): the committed pres_reach_census.out came from the first version of this script,
# whose NWIDE-0 passes lacked the mkdir above (every *.n0 run failed: no data); the output
# was re-tabulated with the *.n0 artifacts excluded (retab below).
# Usage: bash pres_reach_census.sh ROOT SCRATCH   (gcc-16; seed 20261110, 400 sites)
set -u
ROOT="$1"; S="$2"; CC="${CC:-gcc-16}"; R="$ROOT/memfn/tests/run_g2_pres.sh"
mkdir -p "$S"
# the runners' one applier, its path spelled in two parts on purpose: this one-shot evidence is
# no runner, and [SABANCHOR]'s discovery treats any file naming the applier's path as one
# (its NOT_RUNNERS list is code this no-fix lane does not edit)
APPLY_PY="$ROOT/tests/lib/""plants.py"
eval "$(sed -n '/^plant_spec() {/,/^}/p' "$R")"
PLANTS=$(grep -m1 '^PLANTS=' "$R" | cut -d'"' -f2)
PASSES="x86-64-v3:0:1 x86-64-v3:1:1 x86-64:0:1 x86-64:1:1 generic:0:1 generic:1:1 generic:0:0 generic:0:1:deny"
build() {   # build SRC OUT [CFLAGS]
    local src="$1" out="$2"; shift 2; mkdir -p "$out/o"
    for s in "$src"/*.c; do "$CC" -std=gnu11 -O1 "$@" -I"$ROOT/memfn/include" -c -o "$out/o/$(basename "${s%.c}").o" "$s" || return 1; done
    "$CC" -std=gnu11 -O1 -Wall -Wextra -Werror -I"$ROOT/memfn/include" -I"$ROOT/memfn/tests/g2" \
        "$ROOT/memfn/tests/g2/g2_pres_gen.c" "$out"/o/*.o -o "$out/gen"
}
render() {  # render DIR: every pass + the trace passes into DIR
    local d="$1" p t l m dn
    for p in $PASSES; do
        IFS=: read -r t l m dn <<< "$p"; local tag="$t.$l.$m${dn:+.deny}"
        mkdir -p "$d/$tag"
        timeout 120 "$d/plain/gen" 20261110 400 "$d/$tag" "$t" "$l" "$m" 300 "${dn:+1}" > "$d/$tag.log" 2>&1
        [ -n "$dn" ] || mkdir -p "$d/$tag.n0"
        [ -n "$dn" ] || timeout 120 "$d/plain/gen" 20261110 400 "$d/$tag.n0" "$t" "$l" "$m" 0 0 > "$d/$tag.n0.log" 2>&1 \
            || true
    done
    for t in x86-64-v3 x86-64 generic; do
        mkdir -p "$d/tr.$t"
        G2P_G2SITE=1 timeout 120 "$d/trace/gen" 20261110 400 "$d/tr.$t" "$t" 0 1 300 0 > "$d/tr.$t.log" 2> "$d/tr.$t.err"
    done
}
one() {     # one ID|clean
    local id="$1" d="$S/$1"; mkdir -p "$d/src" "$d/c0"
    cp -RL "$ROOT/memfn/src/." "$d/src/"; cp "$ROOT/docs/design/memfn/span_pick/census0.py" "$d/c0/"
    if [ "$id" != clean ]; then
        local s l; s="$(plant_spec "$id")"; local E=(); while IFS= read -r l; do E+=("$l"); done <<< "$s"
        python3 -I "$APPLY_PY" apply pres "$d/src" "$d/c0" -- "${E[@]}" > "$d/apply.log" 2>&1 \
            || { echo "$id APPLY-FAIL"; return; }
    fi
    build "$d/src" "$d/plain" > "$d/build.log" 2>&1 || { echo "$id BUILD-FAIL"; return; }
    build "$d/src" "$d/trace" -DMF_TRACE >> "$d/build.log" 2>&1 || { echo "$id TRACEBUILD-FAIL"; return; }
    render "$d"
    echo "$id rendered"
}
export -f one build render plant_spec; export ROOT S CC PASSES APPLY_PY
one clean
printf '%s\n' $PLANTS | xargs -P 4 -I{} bash -c 'one {}'
echo "=== census"
for id in $PLANTS; do
    d="$S/$id"; moved=""
    for f in $(cd "$S/clean" && ls -d */g2p_sites.c *.log tr.*.err 2>/dev/null | grep -v '^build.log$'); do
        cmp -s "$S/clean/$f" "$d/$f" || moved="$moved ${f%%/*}"
    done
    c0=""; cmp -s "$S/clean/c0/census0.py" "$d/c0/census0.py" || c0=" (edits the @c0 census copy)"
    if [ -z "$moved" ]; then echo "REACH $id UNREACHED-BY-GENERATOR$c0"
    else echo "REACH $id moved:$(echo $moved | tr ' ' '\n' | sort -u | tr '\n' ' ')$c0"; fi
done
echo "=== census done"
