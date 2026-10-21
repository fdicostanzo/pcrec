#!/usr/bin/env bash
# docs/design/findall_iter/twin/parity.sh — [FINDALL-NEXT] the PRE-BUILD PARITY GATE's run
# (lane parity, 2026-10-21; findall_iter.md §5.3 revision 3, §6.9's "parity slot").
#
#   parity.sh build  OUT          subjects, artifacts, twins, every (arm, regime) binary
#   parity.sh gate   OUT [quick]  THE ANSWER GATE, before any clock: (G1) run_twin.sh's 60-cell
#                                 case table on the off, shared and fill twins under ASan+UBSan
#                                 (skipped by `quick`); (G2) every timing binary's `check`
#                                 answer equal to L_old's, per subcell and regime; (G3) L_old
#                                 equal to python `re` (parity_expect.py, no pcrec source);
#                                 (G4) R2 binaries call the artifact through the PLT, R1 ones
#                                 do not. Any disagreement exits 3: the run stops before timing.
#   parity.sh time   OUT L T N    L launches; per launch, per subcell, per regime, every arm
#                                 once in a rotated order, pinned (taskset) to PARITY_CPU;
#                                 each arm calibrates reps to T ns per sample, takes N samples,
#                                 reports their median ns per find-all -> OUT/results.tsv
#   parity.sh verdict OUT         parity_verdict.py over results.tsv
#   parity.sh run    OUT          build, gate, time 5 20000000 7, verdict (the queued job)
#   parity.sh smoke  OUT          build, quick gate, NO clock (the lane's no-clock smoke run)
#   parity.sh calib  OUT          build, quick gate, ONE launch at a small target: wall per
#                                 launch, printed as the cap estimate's input
#
# Cells, arms and regimes are §5.3's (the cells file below and ARMS). Arm decisions, stated:
#   L_old, L_new, A: today's §3.1.3 loop over the plain artifact, three SEPARATE compiles and
#     links of the same source. For the pre-build run L_new IS L_old's build (§5.3 names the
#     twin only for I, B64, I_shared and N64), so L_new/L_old and A/L_new are both A/A pairs;
#     the floor is A against L_new, as §5.3 defines it.
#   L_tw (added, reported, never gated): the same loop over the TWIN's thin `_search` (its
#     body moved into `__find`), the pre-build proxy for "the cost the refactor puts on
#     `_search` itself".
#   I (batch cell off, K = 1), N64 (off build), I_shared (off, --shared: the `-2` layout),
#   B64 (batch cell fill, 64-entry region), I_fill (added, reported: the fill build at K = 1,
#   what the fill cell costs a caller that binds no region).
# Regimes: R1 the artifact object linked statically; R2 the artifact as a -fPIC shared object
#   (one per arm, so no two arms share a mapping), called through the PLT. gcc -O2 throughout.
set -u
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TREE=$(cd "$here/../../../.." && pwd)
PCREC=${PCREC:-$TREE/build/pcrec}
CORPUS=${CORPUS:-$(cd "$TREE" && git rev-parse --path-format=absolute --git-common-dir | xargs dirname)/worktrees/.corpus}
CPU=${PARITY_CPU:-7}
. "$TREE/tests/lib/timeout_bin.sh" 2>/dev/null
TO=${TIMEOUT_BIN:-timeout}
CC=${CC:-gcc}
ARMS="L_old L_new A L_tw I N64 I_shared B64 I_fill"
REGIMES="R1 R2"
# the prose source (rwcorpus's manifest pin) and the two derived slices: bytes
# [64 KiB, 64 KiB + 1 MiB) of Moby-Dick (past the Gutenberg header), and that slice's first 4 KiB
PROSE_SRC=prose/pg2701.txt
PROSE_SHA=b5e88b71a1cda068e9ab1d94344c9d932338ba6da1a66def97a1aecd9cfcc87d
PROSE1M_SHA=1b46c694e04bc49d715bf051a1a6472bda42a2db8007a9c3ac3761bcefdae8ec
PROSE4K_SHA=a5bb46fd928ff878adfa4fb6d4e5d23fb2fc525d1a8ced5c337080e954feb508

say() { printf '%s\n' "$*"; }
die() { say "parity: $*" >&2; exit 2; }

arm_def() { case $1 in L_old|L_new|A|L_tw) echo ARM_LOOP;; I|I_shared|I_fill) echo ARM_ITER;;
                       B64) echo ARM_BATCH;; N64) echo ARM_NEXTN;; esac; }
arm_obj() { case $1 in L_old) echo plain_old;; L_new) echo plain_new;; A) echo plain_aa;;
                       L_tw|I|N64) echo twin_off;; I_shared) echo twin_shared;; B64|I_fill) echo twin_fill;; esac; }

# id  pattern-key  subject  stop        (§5.3's cells; a cell with several N is several subcells)
cells() {
cat <<'EOF'
c1-64	pa	a64	0
c1-4k	pa	a4k	0
c1-1m	pa	a1m	0
c2-a	pa	s_a	0
c2-b	pa	s_b	0
c2-e	pa	s_e	0
c3-4k	pw	prose4k	0
c3-1m	pw	prose1m	0
c4	pc	a4k	0
c5	pw	s_x	0
c6	pd	b4k	0
c7	pa	a4k	3
EOF
}
# key  pcrec flags  pattern
pats() {
cat <<'EOF'
pa	-	a
pw	-	\w+
pc	-	(a)
pd	--engine=dfa	^a|b
EOF
}

waitall() {   # LABEL PID...: wait for every pid; a failure names LABEL
    local label=$1 p bad=0; shift
    for p in "$@"; do wait "$p" || bad=1; done
    [ $bad = 0 ] || say "parity: $label failed" >&2
    return $bad
}
sibling_of() { cat "/sys/devices/system/cpu/cpu$1/topology/thread_siblings_list" 2>/dev/null | tr ',' '\n' | grep -vx "$1" | head -1; }
cpustat() { awk -v c="cpu$1" '$1==c{t=0; for(i=2;i<=NF;i++) t+=$i; print t, $5+$6}' /proc/stat; }

preflight() {
    [ -x "$PCREC" ] || die "no compiler at $PCREC (make in $TREE first)"
    command -v taskset >/dev/null || die "no taskset"
    command -v python3 >/dev/null || die "no python3"
    [ -f "$CORPUS/$PROSE_SRC" ] || die "no prose subject $CORPUS/$PROSE_SRC (rwcorpus fetch.sh)"
    local sha; sha=$(sha256sum < "$CORPUS/$PROSE_SRC" | cut -c1-64)
    [ "$sha" = "$PROSE_SHA" ] || die "prose source sha $sha != manifest pin $PROSE_SHA"
    [ -d "/sys/devices/system/cpu/cpu$CPU" ] || die "no cpu$CPU"
    local sib; sib=$(sibling_of "$CPU")
    [ -n "$sib" ] || die "cpu$CPU has no SMT sibling listed (topology unreadable)"
    printf '%s\n' "$sib"
}

build() {
    local O=$1 sib; sib=$(preflight) || exit 2
    mkdir -p "$O"/{subj,art,bin,obj} || die "mkdir $O"
    export TMPDIR=$O/tmp; mkdir -p "$TMPDIR"
    local S=$O/subj
    head -c 64 /dev/zero | tr '\0' a > "$S/a64"
    head -c 4096 /dev/zero | tr '\0' a > "$S/a4k"
    head -c 1048576 /dev/zero | tr '\0' a > "$S/a1m"
    head -c 4096 /dev/zero | tr '\0' b > "$S/b4k"
    printf a > "$S/s_a"; printf b > "$S/s_b"; : > "$S/s_e"; printf x > "$S/s_x"
    tail -c +65537 "$CORPUS/$PROSE_SRC" | head -c 1048576 > "$S/prose1m"
    head -c 4096 "$S/prose1m" > "$S/prose4k"
    [ "$(sha256sum < "$S/prose1m" | cut -c1-64)" = "$PROSE1M_SHA" ] || die "prose1m slice sha moved"
    [ "$(sha256sum < "$S/prose4k" | cut -c1-64)" = "$PROSE4K_SHA" ] || die "prose4k slice sha moved"
    cells > "$O/cells.tsv"
    : > "$O/stamps.txt"
    local pk flags pat
    while IFS=$'\t' read -r pk flags pat; do
        [ "$flags" = - ] && flags=""
        local A=$O/art/$pk; mkdir -p "$A"
        # shellcheck disable=SC2086
        (cd "$A" && "$PCREC" -p "$pk" $flags -o "$pk.c" --pattern "$pat") || die "pcrec refused $pat"
        cp "$here/iter_abi.h" "$A/"
        python3 -I "$here/mktwin.py" "$pk" "$A/$pk.c" "$A/twin_off.c" || die "mktwin off $pk"
        python3 -I "$here/mktwin.py" "$pk" "$A/$pk.c" "$A/twin_shared.c" --shared || die "mktwin shared $pk"
        python3 -I "$here/mktwin.py" "$pk" "$A/$pk.c" "$A/twin_fill.c" --fill || die "mktwin fill $pk"
        local PU; PU=$(echo "$pk" | tr a-z A-Z)
        # shellcheck disable=SC2086
        local null; null=$("$PCREC" $flags --emit-facts --pattern "$pat" | awk -F'\t' '$1=="byte" && $2=="nullable"{print $7}')
        { printf '%s\t%s\t%s\tnullable=%s\t' "$pk" "${flags:--}" "$pat" "$null"
          grep -hE "^#define ${PU}_(ENGINE|DFA_SCAN|DFA_START|DFA_PREFILTER|NCAPS) " "$A/$pk.c" "$A/$pk.h" | sort -u | awk '{printf "%s=%s ", $2, $3}'
          grep -o 'body linkage: [^;]*' "$A/twin_off.c" | head -1; } >> "$O/stamps.txt"
        [ "$null" = no ] || die "pattern $pat is nullable: the plain twin does not apply (retry machinery)"
        # the compiles of one pattern run concurrently, then its links (the dry run's 30 s bound)
        local o pids=() arm
        for o in plain_old plain_new plain_aa twin_off twin_shared twin_fill; do
            local src=$A/$o.c; case $o in plain_*) src=$A/$pk.c;; esac
            $CC -O2 -c -o "$O/obj/$pk.$o.o" -I"$A" "$src" & pids+=($!)
            $CC -O2 -fPIC -shared -o "$O/obj/lib${pk}_$o.so" -I"$A" "$src" & pids+=($!)
        done
        waitall "compile $pk" "${pids[@]}" || exit 2
        pids=()
        mkdir -p "$O/bin/R1/$pk" "$O/bin/R2/$pk"
        for arm in $ARMS; do
            o=$(arm_obj "$arm")
            $CC -O2 -Wall -Wextra -o "$O/bin/R1/$pk/$arm" -D"$(arm_def "$arm")" -DPFX="$pk" -DPFXU="$PU" \
                -DHDR="\"$pk.h\"" -I"$A" "$here/tdrv.c" "$O/obj/$pk.$o.o" & pids+=($!)
            $CC -O2 -Wall -Wextra -o "$O/bin/R2/$pk/$arm" -D"$(arm_def "$arm")" -DPFX="$pk" -DPFXU="$PU" \
                -DHDR="\"$pk.h\"" -I"$A" "$here/tdrv.c" -L"$O/obj" -l"${pk}_$o" -Wl,-rpath,"$O/obj" & pids+=($!)
        done
        waitall "link $pk" "${pids[@]}" || exit 2
    done < <(pats)
    # cell 6 must be the attempt-scan artifact whose body keeps a static label table (§5.3)
    grep -q '^pd	.*PD_DFA_SCAN="attempt".*body linkage: static noinline (static label table)' "$O/stamps.txt" \
        || die "cell 6's stamp is not DFA_SCAN \"attempt\" with a static-label body: $(grep '^pd' "$O/stamps.txt")"
    say "== parity build: 4 artifacts, $(ls "$O"/bin/R1/*/* | wc -l) R1 + $(ls "$O"/bin/R2/*/* | wc -l) R2 binaries, cpu$CPU (sibling cpu$sib)"
    sed 's/^/   stamp /' "$O/stamps.txt"
}

gate() {
    local O=$1 quick=${2:-} bad=0
    export TMPDIR=$O/tmp; mkdir -p "$TMPDIR"
    if [ "$quick" != quick ]; then
        local m e
        for m in off shared fill; do
            e=""; [ $m = shared ] && e="TWIN_SHARED=1"; [ $m = fill ] && e="TWIN_FILL=1"
            env TWIN_ASAN=1 $e "$TO" 900 bash "$here/run_twin.sh" "$TREE" "$O/twin_$m" > "$O/twin_$m.out" 2>&1
            local okn tot; okn=$(grep -c '^CASE.* OK ' "$O/twin_$m.out"); tot=$(grep -c '^CASE' "$O/twin_$m.out")
            if tail -1 "$O/twin_$m.out" | grep -q 'ALL OK' && [ "$okn" = 60 ] && [ "$tot" = 60 ]; then
                say "   G1 twin $m: $okn/$tot cases OK (ASan+UBSan)"
            else say "   G1 twin $m: MISMATCH ($okn/$tot OK; $O/twin_$m.out)"; bad=1; fi
        done
    else say "   G1 skipped (quick)"; fi
    python3 -I "$here/parity_expect.py" "$O/cells.tsv" "$O/subj" > "$O/expect.tsv" || { say "   G3 parity_expect.py failed"; bad=1; }
    local cid pk subj stop arm r ref exp got
    : > "$O/check.tsv"
    while IFS=$'\t' read -r cid pk subj stop; do
        exp=$(awk -F'\t' -v c="$cid" '$1==c{print $2}' "$O/expect.tsv")
        for r in $REGIMES; do
            ref=$("$O/bin/$r/$pk/L_old" check "$O/subj/$subj" "$stop")
            [ "$ref" = "$exp" ] || { say "   G3 $cid $r: L_old '$ref' != python re '$exp'"; bad=1; }
            for arm in $ARMS; do
                got=$("$O/bin/$r/$pk/$arm" check "$O/subj/$subj" "$stop")
                printf '%s\t%s\t%s\t%s\n' "$cid" "$r" "$arm" "$got" >> "$O/check.tsv"
                [ "$got" = "$ref" ] || { say "   G2 $cid $r $arm: '$got' != L_old '$ref'"; bad=1; }
            done
        done
    done < "$O/cells.tsv"
    say "   G2/G3 $(wc -l < "$O/check.tsv") binary answers checked against L_old and python re"
    local plt=0 noplt=0 b
    for b in "$O"/bin/R2/*/*; do objdump -d "$b" | grep -qE 'call.*<(pa|pw|pc|pd)_(search|next|next_n)@plt>' && plt=$((plt + 1)); done
    for b in "$O"/bin/R1/*/*; do objdump -d "$b" | grep -qE 'call.*<(pa|pw|pc|pd)_[a-z_]+@plt>' || noplt=$((noplt + 1)); done
    local nb; nb=$(ls "$O"/bin/R2/*/* | wc -l)
    if [ "$plt" = "$nb" ] && [ "$noplt" = "$nb" ]; then say "   G4 R2: $plt/$nb call the artifact through the PLT; R1: $noplt/$nb do not"
    else say "   G4 PLT structure: R2 $plt/$nb via PLT, R1 $noplt/$nb direct"; bad=1; fi
    if [ $bad = 0 ]; then say "== parity ANSWER GATE: PASSED"; return 0; fi
    say "== parity ANSWER GATE: FAILED (no timing)"; return 3
}

timing() {
    local O=$1 L=$2 T=$3 N=$4 sib; sib=$(sibling_of "$CPU")
    local res=$O/results.tsv
    printf 'launch\tcell\tregime\tarm\tns\tmin_ns\treps\tcount\tload1\tsib_busy_pct\n' > "$res"
    local l cid pk subj stop r i arm out s0 s1 ci=0 na; na=$(echo $ARMS | wc -w)
    for l in $(seq 1 "$L"); do
        say "   launch $l/$L load1=$(cut -d' ' -f1 /proc/loadavg) $(date -Iseconds)"
        ci=0
        while IFS=$'\t' read -r cid pk subj stop; do
            ci=$((ci + 1))
            local regs=$REGIMES; [ $(( (l + ci) % 2 )) = 1 ] && regs="R2 R1"
            for r in $regs; do
                local rot=$(( (l + ci) % na )) k=0 order=""
                for arm in $ARMS $ARMS; do k=$((k + 1)); [ $k -gt $rot ] && [ $k -le $((rot + na)) ] && order="$order $arm"; done
                for arm in $order; do
                    s0=$(cpustat "$sib")
                    out=$(taskset -c "$CPU" "$O/bin/$r/$pk/$arm" time "$O/subj/$subj" "$stop" "$T" "$N") \
                        || { say "   time $cid $r $arm: driver failed"; return 1; }
                    s1=$(cpustat "$sib")
                    local busy; busy=$(awk -v a="$s0" -v b="$s1" 'BEGIN{split(a,x," "); split(b,y," "); t=y[1]-x[1]; i=y[2]-x[2]; printf "%.1f", (t > 0 ? 100*(t-i)/t : 0)}')
                    # out: ns M min M reps R count C
                    set -- $out
                    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$l" "$cid" "$r" "$arm" "$2" "$4" "$6" "$8" \
                        "$(cut -d' ' -f1 /proc/loadavg)" "$busy" >> "$res"
                done
            done
        done < "$O/cells.tsv"
    done
    say "   timing: $(($(wc -l < "$res") - 1)) rows in $res"
}

cmd=${1:-}; O=${2:-}
[ -n "$cmd" ] && [ -n "$O" ] || { sed -n '2,40p' "$0" >&2; exit 64; }
O=$(mkdir -p "$O" && cd "$O" && pwd) || die "cannot make $O"
cd "$O" || die "cannot enter $O"       # nothing this script runs writes to the caller's cwd
case $cmd in
    build) build "$O" ;;
    gate) gate "$O" "${3:-}" ;;
    time) timing "$O" "${3:?launches}" "${4:?target ns}" "${5:?samples}" ;;
    verdict) python3 -I "$here/parity_verdict.py" "$O/results.tsv" ;;
    smoke)
        build "$O" && gate "$O" quick || exit $?
        say "== parity smoke: build and answer gate only, no clock read" ;;
    calib)
        build "$O" && gate "$O" quick || exit $?
        t0=$(date +%s.%N); timing "$O" 1 "${PARITY_CALIB_NS:-2000000}" 3 || exit 1; t1=$(date +%s.%N)
        awk -v a="$t0" -v b="$t1" 'BEGIN{printf "== parity calib: one launch at 2 ms x 3 samples took %.1f s\n", b-a}' ;;
    run)
        say "== parity START $(date -Iseconds) tree=$TREE head=$(git -C "$TREE" rev-parse --short HEAD) cpu=$CPU gcc=$($CC -dumpfullversion)"
        build "$O" || exit 2
        gate "$O" || exit 3
        timing "$O" 5 20000000 7 || exit 1
        python3 -I "$here/parity_verdict.py" "$O/results.tsv" || exit 1 ;;
    *) die "unknown command $cmd" ;;
esac
