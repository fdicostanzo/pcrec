#!/usr/bin/env bash
# tests/families/module_diff.sh — the shared body of the [FEAT-FAMILIES]
# pre-move differentials (run_quoting_diff.sh, run_named_diff.sh): one module's
# patterns against libpcre2, over an exhaustive small-alphabet subject space
# with startpos taking EVERY value, comparing the match span AND every group
# span (the sweep shape of tests/backrefs/run_backref_diff.sh §1, whose oracle
# and batch driver this reuses rather than copies).
#
# Caller sets (all required): LABEL FEATS PATTERNS (key<TAB>ngroups<TAB>pattern)
# REFUSALS (key<TAB>pattern; pcrec and libpcre2 must AGREE on accept/refuse,
# message wording is D26's lowest tier and is not compared) ALPHA MAXLEN
# EXTRA_SUBJECTS (a newline-separated list) EXPECT_CELLS EXPECT_MATCH
# EXPECT_REFUSE (the populations are asserted EXACT, never a floor: a sweep that
# lost patterns or matched nothing prints the same silence as one that agreed).
#
# SKIPS LOUDLY when libpcre2 is absent. Env: PCREC, CC, KEEP=1.
set -u
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
. "$ROOT_DIR/tests/lib/resolve_pcre2.sh"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11}"
export ROOT_DIR
WORKDIR="$(mktemp -d)"
trap '[ "${KEEP:-0}" = 1 ] && echo "$LABEL: KEEP=1, $WORKDIR" >&2 || rm -rf "$WORKDIR"' EXIT
pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
skip() { echo "SKIP: libpcre2 is not available at run time (loud skip, never a silent pass)"
         echo "checks passed: 0"; echo "checks failed: 0"; exit 0; }
BREF="$ROOT_DIR/tests/backrefs"

python3 - "$WORKDIR/subjects" "$ALPHA" "$MAXLEN" "$EXTRA_SUBJECTS" <<'PY' || exit 1
import itertools, os, sys
out, alpha, maxlen, extra = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
os.makedirs(out, exist_ok=True)
subs = ["".join(t) for n in range(maxlen + 1) for t in itertools.product(alpha, repeat=n)]
subs += extra.split("\n") if extra else []
seen = []
for s in subs:
    if s not in seen:
        seen.append(s)
for i, s in enumerate(seen, 1):
    open(os.path.join(out, "s%04d" % i), "wb").write(s.encode("latin-1"))
PY
printf '%s\n' "$PATTERNS" | sed '/^$/d' > "$WORKDIR/patterns.tsv"
printf '%s\n' "$REFUSALS" | sed '/^$/d' > "$WORKDIR/refusals.tsv"
python3 "$BREF/bref_oracle.py" "$WORKDIR/patterns.tsv" "$WORKDIR/subjects" \
        "$WORKDIR/oracle.tsv" 2>"$WORKDIR/oracle.log" || {
    grep -q "libpcre2 unavailable" "$WORKDIR/oracle.log" && skip
    echo "FAIL: oracle refused to run:" >&2; cat "$WORKDIR/oracle.log" >&2; exit 1; }
python3 - "$WORKDIR/subjects" "$WORKDIR/cells.txt" <<'PY'
import os, sys
d, out = sys.argv[1], sys.argv[2]
with open(out, "w") as o:
    for name in sorted(os.listdir(d)):
        for sp in range(os.path.getsize(os.path.join(d, name)) + 1):
            o.write("%s/%s\t%d\n" % (d, name, sp))
PY
NPERPAT=$(wc -l < "$WORKDIR/cells.txt")
NPAT=$(wc -l < "$WORKDIR/patterns.tsv")

cmp_n=0; cmp_bad=0; match_n=0
while IFS=$'\t' read -r key ng pat; do
    d="$WORKDIR/$key"; mkdir -p "$d"
    awk -F'\t' -v k="$key" '$1 == k { print $4 }' "$WORKDIR/oracle.tsv" > "$d/want"
    # shellcheck disable=SC2086
    if ! pcrec_run "$PCREC" -p rx --features "$FEATS" -o "$d/gen.c" --pattern "$pat" \
            >/dev/null 2>"$d/pc.log"; then
        bad "$key: pcrec refused '$pat' (libpcre2 compiles it): $(head -1 "$d/pc.log")"; continue
    fi
    if ! $CC $GENCFLAGS -I"$d" -o "$d/drv" "$BREF/bref_batch.c" "$d/gen.c" 2>"$d/cc.log"; then
        bad "$key: generated matcher for '$pat' did not compile: $(head -3 "$d/cc.log" | tr '\n' ' ')"; continue
    fi
    "$d/drv" < "$WORKDIR/cells.txt" > "$d/got" 2>"$d/run.log" || { bad "$key: driver failed"; continue; }
    if [ "$(wc -l < "$d/got")" -ne "$NPERPAT" ]; then bad "$key: driver line count shifted"; continue; fi
    n=0
    while IFS= read -r want && IFS= read -r got <&3; do
        n=$((n + 1)); cmp_n=$((cmp_n + 1))
        case "$want" in match*) match_n=$((match_n + 1)) ;; esac
        if [ "$want" != "$got" ]; then
            cmp_bad=$((cmp_bad + 1))
            [ "$cmp_bad" -le 8 ] && bad "'$pat' cell $n ($(sed -n "${n}p" "$WORKDIR/cells.txt" | sed "s|$WORKDIR/subjects/||")): libpcre2 '$want', pcrec '$got'"
        fi
    done < "$d/want" 3< "$d/got"
done < "$WORKDIR/patterns.tsv"
if [ "$cmp_n" -ne "$EXPECT_CELLS" ]; then
    bad "POPULATION: compared $cmp_n cells, expected exactly $EXPECT_CELLS ($NPAT patterns x $NPERPAT cells; a pattern that failed to build leaves this short)"
elif [ "$cmp_bad" -eq 0 ]; then
    ok "$LABEL sweep: $cmp_n cells (span and every group span) agree with libpcre2, $NPAT patterns"
fi
if [ "$match_n" -ne "$EXPECT_MATCH" ]; then
    bad "NON-VACUITY: $match_n matching cells, expected exactly $EXPECT_MATCH"
else ok "$LABEL non-vacuity: $match_n matching cells"; fi

# ---- refusal agreement: accept/refuse only ---------------------------------
python3 - "$WORKDIR/refusals.tsv" "$WORKDIR/refuse_oracle.tsv" <<'PY' 2>"$WORKDIR/ro.log" || { grep -q unavailable "$WORKDIR/ro.log" && skip; cat "$WORKDIR/ro.log" >&2; exit 1; }
import os, sys
sys.path.insert(0, os.path.join(os.environ["ROOT_DIR"], "docs", "design", "eng_brep_measurements", "probes"))
try:
    import pcre2_ctypes as P
except Exception as e:
    sys.stderr.write("unavailable %s\n" % e); sys.exit(3)
with open(sys.argv[2], "w") as o:
    for line in open(sys.argv[1]):
        key, pat = line.rstrip("\n").split("\t", 1)
        try:
            P.Compiled(pat.encode("utf-8"), 0); r = "accept"
        except Exception:
            r = "refuse"
        o.write("%s\t%s\n" % (key, r))
PY
ref_n=0; ref_bad=0
while IFS=$'\t' read -r key pat; do
    ref_n=$((ref_n + 1))
    want=$(awk -F'\t' -v k="$key" '$1 == k { print $2 }' "$WORKDIR/refuse_oracle.tsv")
    if pcrec_run "$PCREC" -p rx --features "$FEATS" -o "$WORKDIR/r.c" --pattern "$pat" >/dev/null 2>&1; then got=accept; else got=refuse; fi
    if [ "$want" != "$got" ]; then ref_bad=$((ref_bad + 1)); bad "refusal $key '$pat': libpcre2 $want, pcrec $got"; fi
done < "$WORKDIR/refusals.tsv"
if [ "$ref_n" -ne "$EXPECT_REFUSE" ]; then bad "POPULATION: $ref_n refusal patterns, expected exactly $EXPECT_REFUSE"
elif [ "$ref_bad" -eq 0 ]; then ok "$LABEL accept/refuse agrees with libpcre2 on all $ref_n patterns"; fi
echo "checks passed: $pass"; echo "checks failed: $fail"
[ "$fail" -eq 0 ]
