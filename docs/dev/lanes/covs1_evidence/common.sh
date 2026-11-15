# sourced by every covs1 job script (lane covs1, [COVER-CAP] stage 1)
TREE=/home/pcrec/projects/pcrec/worktrees/covs1f
MAIN=/home/pcrec/projects/pcrec
BASE=91bae2d98                      # the lane's branch point (main)
SC=/var/tmp/pcrec-pcrec/scratch/covs1f
BQ="$MAIN/scripts/boxqueue"
evening_hold() {   # Frank's 20:00-01:00 hold, exit 75 inside it
    local h=$((10#$(date +%H)))
    if [ "$h" -ge 20 ] || [ "$h" -lt 1 ]; then echo "evening hold 20:00-01:00"; exit 75; fi
}
ready_after() {    # --ready: the hold, then KEY green
    evening_hold
    [ -n "${1:-}" ] && exec bash "$BQ" after "$1"
    exit 0
}
# the BASELINE compiler: the branch point with its abi digits raised to 108
# (an abi bump moves every artifact's stamp; the sweep then compares the
# rest, the ic2 precedent), plus its trace build:
# $SC/ref/build/{pcrec,pcrec-harness}, $SC/ref/build/z2trace/
ref_build() {
    if [ -x "$SC/ref/build/pcrec" ] && [ -x "$SC/ref/build/z2trace/pcrec-harness" ]; then return 0; fi
    rm -rf "$SC/ref.new"; mkdir -p "$SC/ref.new"
    git -C "$MAIN" archive "$BASE" | tar -x -C "$SC/ref.new" || return 1
    sed -i 's/^#define PCREC_ARTIFACT_ABI 107$/#define PCREC_ARTIFACT_ABI 108/' "$SC/ref.new/src/gen/emit_dfa.c"
    grep -q '^#define PCREC_ARTIFACT_ABI 108$' "$SC/ref.new/src/gen/emit_dfa.c" || { echo "ref abi patch failed"; return 1; }
    make -s -C "$SC/ref.new" -j16 all >"$SC/ref.build.log" 2>&1 || return 1
    make -s -C "$SC/ref.new" -j16 BUILD_DIR=build/z2trace CFLAGS="-O2 -g -DPCREC_CAND_TRACE" all >>"$SC/ref.build.log" 2>&1 || return 1
    rm -rf "$SC/ref"; mv "$SC/ref.new" "$SC/ref"
}
tree_build() {
    make -s -C "$TREE" -j16 all >/dev/null 2>&1 || return 1
    make -s -C "$TREE" -j16 BUILD_DIR=build/z2trace CFLAGS="-O2 -g -DPCREC_CAND_TRACE" all >/dev/null 2>&1
}
