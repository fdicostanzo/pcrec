#!/usr/bin/env bash
# docs/dev/optloop/s2a/s2a_chain.sh — [OPT-LITSCAN] S2a's OWED heavy stages,
# serially, detached (the lane ends before they do; docs/dev/lanes/s2a_report.md
# "STATE AT HANDOFF" names each stage's log and completion line).
#
#   BASE=<main pcrec, abi 40>  NEW=<lane pcrec>  JSON=<s1_identity.json>
#   OUT=<log dir>  nohup bash s2a_chain.sh > $OUT/chain.log 2>&1 & disown
#
# Every stage writes $OUT/<stage>.log and appends ONE line to $OUT/chain.log:
# "STAGE <name> rc=<n>". The chain ends with "CHAIN COMPLETE". A stage's
# verdict is its own log (the answer tools' last line; make's `*** [...]
# Error` lines), never the rc alone.
set -u
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
: "${BASE:?}" "${NEW:?}" "${JSON:?}" "${OUT:?}"
mkdir -p "$OUT"
stage() {  # name, command...
    local name="$1"; shift
    echo "STAGE $name START $(date '+%F %T')"
    ( cd "$ROOT" && "$@" ) > "$OUT/$name.log" 2>&1
    echo "STAGE $name rc=$? $(date '+%F %T')"
}

# 1. every mover answer- and give-up-identical against main, all startpos
stage answers env BASE="$BASE" NEW="$NEW" timeout 14400 \
    python3 tests/findings/b1_mover_answers.py "$JSON"

# 2. read safety: a sample of movers under ASan+UBSan, subjects handed over
#    in blocks of exactly their length, plus every prefix (ends inside a run).
python3 - "$JSON" "$OUT/sample.json" <<'PY'
import json, random, sys
d = [r for r in json.load(open(sys.argv[1])) if r["identity"] == "changed"]
random.Random(0x52A).shuffle(d)
lit = [r for r in d if r["pop"] == "corpus" and (r["key"] in (
    "abcdef", "x(abc)defg", "xy(a|ab)c", "a*bcd", "^abc$", "a\\x00b", "\\x001",
    "foo(?:username|password|passphrase)bar", "(?:alpha|alps|alp)x"))]
# + witnesses whose run is NOT necessary (a non-literal sibling branch), so no
# whole-window pre-check or start bound keeps an attempt away from a subject
# ending inside the run (lane s2afix). A NECESSARY run is shielded: rx_reqrun
# proves it occurs at or after search_from and the attempt bound stops short
# of the edge, so the control's plant cannot reach it there.
syn = [{"pop": "corpus", "key": k, "cfg": "vm", "identity": "changed"}
       for k in ("(?:abcdef|x+)y", "(?:abcd|x+)(?:efgh|y+)z", "(?:abc|x+)y")]
json.dump(lit + [r for r in d if r not in lit][:200] + syn, open(sys.argv[2], "w"))
PY
# -fno-builtin-memcmp: gcc expands a constant-length memcmp inline with NO
# ASan instrumentation on its loads, so the first run of this stage could not
# see a run compare's over-read at all (lane s2afix, measured on the control's
# own plant). As a call it goes through ASan's strict memcmp interceptor, which
# checks all L bytes whatever the lowering would have read.
stage asan env BASE="$BASE" NEW="$NEW" PREFIXES=1 \
    CFLAGS="-O1 -std=gnu11 -w -g -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer -fno-builtin-memcmp -DDIFF_EXACT_SUBJECT" \
    ASAN_OPTIONS=detect_leaks=0 timeout 7200 \
    python3 tests/findings/b1_mover_answers.py "$OUT/sample.json"

# 2b. the sweep's POSITIVE CONTROL: the same sweep over the named run
#     witnesses with a compiler whose P8 guard is one byte short
#     (`pos + L - 1 <= n`), which reads one byte past a subject ending inside
#     a run. The stage PASSES only if that sweep FAILS (ASan names the read).
CTL="$OUT/ctl"; rm -rf "$CTL"; mkdir -p "$CTL/tree"
git -C "$ROOT" archive HEAD | tar -x -C "$CTL/tree"
sed -i.bak 's/"    if (scan_position + %d <= subject_length \&\& ", len);/"    if (scan_position + %d - 1 <= subject_length \&\& ", len);/' \
    "$CTL/tree/src/gen/emit_vm.c"
cp "$OUT/sample.json" "$CTL/lit.json"   # the SAME population the asan stage read
stage asan-control-build make -C "$CTL/tree" -j4 CC=gcc-16 build/pcrec
if grep -q 'scan_position + %d - 1 <= subject_length' "$CTL/tree/src/gen/emit_vm.c"; then
    stage asan-control env BASE="$BASE" NEW="$CTL/tree/build/pcrec" PREFIXES=1 \
        CFLAGS="-O1 -std=gnu11 -w -g -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer -fno-builtin-memcmp -DDIFF_EXACT_SUBJECT" \
        ASAN_OPTIONS=detect_leaks=0 timeout 3600 \
        python3 tests/findings/b1_mover_answers.py "$CTL/lit.json"
else
    echo "STAGE asan-control PLANT-DID-NOT-APPLY"
fi

# 3. the acceptance mover (refused at abi 40, compiles at 41 under --engine=vm)
stage accept env BASE="$BASE" bash docs/dev/optloop/s2a/accept_mover.sh

# 4. the new axis, answer-identical over the whole corpus
stage axes env AXES="-fno-lit-run" timeout 14400 bash tests/axes/run_axes.sh

# 5. the two P4 rows S2a widened (S304/S305 were measured by the lane)
for s in S267 S279; do
    stage "mech-$s" timeout 3600 bash tests/mech/run_sabotage_matrix.sh "$s"
done

# 6. the full suite, last
stage maketest timeout 10800 make test CC=gcc-16
echo "CHAIN COMPLETE $(date '+%F %T')"
