#!/usr/bin/env bash
# run_composition.sh — R-3(a)'s HOOK: the D27-blinded composition corpus
# against the rev-2.1 prototype (lane possarms21 left it; the blinded author's
# file is NOT read by that lane).
#
# Runs tests/harness/run.sh over the given .rxt file(s) FOUR times with the
# prototype binary, every expectation in the file being the oracle's
# (10.46-verified by its author):
#   denied/default   no arm variable, default route   (== main)
#   armed/default    PROTO_ARM_A=1 PROTO_ARM_B=1, default route
#   denied/vm        no arm, RXTFLAGS=--engine=vm
#   armed/vm         arms on, RXTFLAGS=--engine=vm (the arms are VM-only, so
#                    this is the pass that exercises them on a pattern the
#                    default route sends to the DFA)
# and reports, per route, the cells that FAIL ARMED but PASS DENIED (an arm
# divergence: the verdict), the cells failing in both (an expectation or a
# pre-existing defect: listed, never attributed to the arms), and those
# failing denied only.  It then counts the file's REACH: how many distinct
# patterns the arms actually mark (`possessify marked`, --engine=vm --emit-ir,
# armed vs denied) -- a corpus the arms never fire on is not evidence.
#
# Usage (from anywhere):
#   PROTO=<scratch>/build/pcrec run_composition.sh FILE.rxt [FILE.rxt...]
# where <scratch> is a copy of main with proto_rev21.patch applied and built
# (`patch -p1 < proto_rev21.patch && make CC=gcc-16`).
# Env: PROTO (required), PROCS (harness parallelism, default 1),
#      OUT (dir for the four logs; default a mktemp dir under TMPDIR, kept).
# Exit: 0 = no divergence and the arms fired on >= 1 pattern; 1 = a
# divergence; 2 = setup error; 3 = no divergence but ZERO reach (vacuous).
set -u
export LC_ALL=C
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$HERE/../../../.." && pwd)
P="${PROTO:?PROTO=<rev-2.1 prototype pcrec> required}"
[ -x "$P" ] || { echo "run_composition: $P is not executable" >&2; exit 2; }
[ $# -ge 1 ] || { echo "usage: PROTO=... $0 FILE.rxt..." >&2; exit 2; }
for f in "$@"; do [ -f "$f" ] || { echo "run_composition: no file $f" >&2; exit 2; }; done
OUT="${OUT:-$(mktemp -d "${TMPDIR:-/tmp}/compo.XXXXXX")}"; mkdir -p "$OUT"
ARMS="PROTO_ARM_A=1 PROTO_ARM_B=1"

pass() {   # name, env, rxtflags
    # shellcheck disable=SC2086
    env $2 PCREC="$P" RXTFLAGS="$3" PROCS="${PROCS:-1}" \
        bash "$ROOT/tests/harness/run.sh" "${FILES[@]}" > "$OUT/$1.out" 2> "$OUT/$1.err"
    echo "$1	rc=$?	$(grep -E '^cases (passed|failed):' "$OUT/$1.out" | tr '\n' ' ')"
    # one key per failing cell: file:line: message (record_fail's own form)
    grep -E '^[^ ]+\.rxt:[0-9]+: ' "$OUT/$1.err" | LC_ALL=C sort -u > "$OUT/$1.fail"
}
FILES=("$@")
echo "# run_composition: PROTO=$P  logs in $OUT"
pass denied_default "" ""
pass armed_default  "$ARMS" ""
pass denied_vm      "" "--engine=vm"
pass armed_vm       "$ARMS" "--engine=vm"

div=0
for r in default vm; do
    a="$OUT/armed_$r.fail"; d="$OUT/denied_$r.fail"
    comm -23 "$a" "$d" > "$OUT/DIVERGE_$r.txt"
    comm -12 "$a" "$d" > "$OUT/both_$r.txt"
    comm -13 "$a" "$d" > "$OUT/denied_only_$r.txt"
    n=$(wc -l < "$OUT/DIVERGE_$r.txt" | tr -d ' ')
    echo "route=$r  ARMS-DIVERGE=$n  fail-both=$(wc -l < "$OUT/both_$r.txt" | tr -d ' ')  denied-only=$(wc -l < "$OUT/denied_only_$r.txt" | tr -d ' ')"
    [ "$n" -eq 0 ] || { sed 's/^/  DIVERGE /' "$OUT/DIVERGE_$r.txt" | head -50; div=1; }
done

# REACH: distinct (pattern, encoding, -i) whose possessify marks the arms move
reach=$(python3 -B - "$P" "${FILES[@]}" <<'PY'
import subprocess, sys, os
P = sys.argv[1]; seen = set(); fire = 0; tot = 0
def dec(b):  # pcrec_sb_field's escapes inverted (census.py's dec_field)
    out = bytearray(); i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5c and i + 1 < len(b):
            n = b[i + 1]
            m = {0x5c: 0x5c, 0x74: 9, 0x6e: 10, 0x72: 13}
            if n in m: out.append(m[n]); i += 2; continue
            if n == 0x78 and i + 3 < len(b):
                try: out.append(int(b[i + 2:i + 4], 16)); i += 4; continue
                except ValueError: pass
        out.append(c); i += 1
    return bytes(out)
def marked(o, pat, env):
    e = dict(os.environ); e.update(env)
    r = subprocess.run([P] + o + ["--engine=vm", "--emit-ir", "--pattern", pat],
                       capture_output=True, env=e, timeout=120)
    for ln in r.stdout.split(b"\n"):
        f = ln.split(b"\t")
        if f[0] == b"possessify": return f[1]
    return None
for fn in sys.argv[2:]:
    r = subprocess.run([P, "--list-source", fn], capture_output=True, timeout=120)
    for ln in r.stdout.split(b"\n"):
        if ln.startswith(b"#section"): break
        if not ln or ln.startswith(b"#"): continue
        fl = ln.split(b"\t")
        if len(fl) < 9 or fl[0] not in (b"pattern", b"pattern-esc"): continue
        pat = dec(fl[4])
        key = (pat, fl[8], b"i" in fl[5])
        if key in seen or not pat: continue
        seen.add(key); tot += 1
        o = ["--features", "all"] + (["-i"] if b"i" in fl[5] else []) + \
            (["-e", "utf8"] if fl[8] == b"utf8" else [])
        a = marked(o, pat, {"PROTO_ARM_A": "1", "PROTO_ARM_B": "1"})
        d = marked(o, pat, {})
        if a and d and a != d: fire += 1
print("%d %d" % (fire, tot))
PY
)
echo "reach: the arms move possessify marks on ${reach% *} of ${reach#* } distinct patterns"
[ "$div" -eq 0 ] || exit 1
[ "${reach% *}" -gt 0 ] 2>/dev/null || { echo "run_composition: VACUOUS — the arms fired on no pattern" >&2; exit 3; }
exit 0
