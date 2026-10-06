#!/usr/bin/env bash
# selftest.sh -- [ARTREV] harness self-test, INCLUDING THE FAILING DIRECTION.
#   bash studies/artrev/selftest.sh 2>&1 | tee studies/artrev/selftest.log
# Needs: a pcrec binary (PCREC=...; default build/pcrec of this tree, else the
# main checkout's), gcc (ARTREV_CC; default gcc-16 on the Mac), python3,
# libpcre2-8 (the sample check; the run says loudly if it is absent).
# Scratch: build-artrev/_selftest (own ARTREV_ROOT).  Timing here uses
# --gate-override (honoured only because ARTREV_SELFTEST=1 is set below) and a
# reduced round count: it tests the MECHANISM, not any speed.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
TREE=$(cd "$HERE/../.." && pwd)
PCREC=${PCREC:-$TREE/build/pcrec}
[ -x "$PCREC" ] || PCREC=$(git -C "$TREE" rev-parse --git-common-dir | sed 's#/\.git$##')/build/pcrec
[ -x "$PCREC" ] || { echo "no pcrec binary (set PCREC=)"; exit 2; }
export ARTREV_CC=${ARTREV_CC:-$(command -v gcc-16 >/dev/null && echo gcc-16 || echo gcc)}
export ARTREV_ROOT=$TREE/build-artrev/_selftest
rm -rf "$ARTREV_ROOT"; mkdir -p "$ARTREV_ROOT"
A="python3 $HERE/artrev.py"
export ARTREV_SELFTEST=1
# the selftest must not be blocked by (nor touch) a REAL suite lock: point the lock path at a
# path that does not exist; section 6 points it at fake locks to prove the refusal.
export ARTREV_SUITE_LOCK_PATH=$ARTREV_ROOT/no-such-suite.lock
FAILS=0; N=0
ok()   { N=$((N+1)); echo "PASS [$N] $1"; }
bad()  { N=$((N+1)); FAILS=$((FAILS+1)); echo "FAIL [$N] $1"; }
# expect NAME EXPECTED_RC CMD...   (captures output into $OUT)
expect() { local what=$1 want=$2; shift 2; OUT=$("$@" 2>&1); local rc=$?
  if [ "$rc" = "$want" ]; then ok "$what (rc $rc)"; else bad "$what: wanted rc $want, got $rc"; echo "$OUT" | tail -8 | sed 's/^/      | /'; fi; }
has()  { if echo "$OUT" | grep -q -- "$2"; then ok "$1: output carries '$2'"; else bad "$1: output lacks '$2'"; echo "$OUT" | tail -6 | sed 's/^/      | /'; fi; }

echo "== host $(uname -sm), $($ARTREV_CC --version | head -1), pcrec $($PCREC --version 2>&1 | head -1)"
python3 - <<'PY'
import random
r = random.Random(7)
open("%s/subj_dense.txt" % __import__("os").environ["ARTREV_ROOT"], "wb").write(
    b"".join(r.choice([b"abd", b"abcd", b"xx", b"ab", b"acd ", b"zzzz "]) for _ in range(6000)))
open("%s/subj_sparse.txt" % __import__("os").environ["ARTREV_ROOT"], "wb").write(
    b"".join(r.choice([b"xx", b"zzzz ", b"qq ", b"abd "]) for _ in range(6000)))
PY
S=$ARTREV_ROOT

echo; echo "== 1. generation records pin / abi / gcc / lines"
expect "gen VM artifact with captures" 0 $A gen vm --pcrec "$PCREC" --pattern 'a(b|c)+d'
has "gen vm" "engine=vm"
expect "gen DFA no-captures artifact" 0 $A gen dfa --pcrec "$PCREC" --pattern '[a-z]+@[a-z]+\.com' --flags=--no-captures
has "gen dfa" "engine=dfa"
for k in pin abi gcc "gen line" "asm line" compile; do
  grep -q "^$k" "$S/vm/GENERATION.txt" && ok "GENERATION.txt records '$k'" || bad "GENERATION.txt lacks '$k'"; done
[ -s "$S/vm/artifact.s" ] && ok "asm written ($(wc -l < "$S/vm/artifact.s") lines)" || bad "no asm"

echo; echo "== 2. null twin: identity PASS (plain and ASan+UBSan), both engines"
expect "twin vm null" 0 $A twin vm null --null
expect "identity vm null (corpus+battery+libpcre2)" 0 $A identity vm null --corpus --battery 600 --block 16 --subject "$S/subj_dense.txt"
has "identity vm null" "IDENTITY PASS"
expect "identity vm null --san" 0 $A identity vm null --battery 300 --san --pcre2-sample 0
expect "twin dfa null" 0 $A twin dfa null --null
expect "identity dfa null" 0 $A identity dfa null --battery 600 --block 8 --subject "$S/subj_dense.txt"

echo; echo "== 3. FAILING DIRECTION: wrong twins must FAIL identity"
expect "new ctl_wrong" 0 $A twin vm ctl_wrong --new
python3 $HERE/selftest_twins.py "$S/vm/arms/ctl_wrong" wrong_end
expect "seal ctl_wrong (a control)" 0 $A twin vm ctl_wrong --seal --control
expect "identity of a wrong-END twin FAILS" 1 $A identity vm ctl_wrong --battery 600 --pcre2-sample 0
has "wrong-end" "FIRST DIFFERENCE"
expect "new ctl_wrongcap" 0 $A twin vm ctl_wrongcap --new
python3 $HERE/selftest_twins.py "$S/vm/arms/ctl_wrongcap" wrong_cap
expect "seal ctl_wrongcap" 0 $A twin vm ctl_wrongcap --seal --control
expect "identity of a wrong-CAPTURE twin FAILS" 1 $A identity vm ctl_wrongcap --battery 600 --pcre2-sample 0
has "wrong-cap" "C	"
expect "time refuses an arm whose identity did not pass" 3 $A time vm --arms orig,null,ctl_wrong --subject cell=$S/subj_dense.txt --rounds 3 --gate-override

echo; echo "== 4. FAILING DIRECTION: SIMD / flag-bearing patches must be REJECTED"
for w in include neon_include builtin_ia32 builtin_neon vector_size pragma_target pragma_optimize attr_optimize attr_target mm_call; do
  $A twin vm ctl_simd --new >/dev/null 2>&1
  python3 $HERE/selftest_twins.py "$S/vm/arms/ctl_simd" "simd:$w"
  expect "SIMD twin '$w' rejected" 4 $A twin vm ctl_simd --seal --control
  has "SIMD '$w'" "forbids"
  [ -d "$S/vm/arms/ctl_simd" ] && bad "rejected arm dir left behind" || ok "rejected arm dir removed"
done
# the same rejection through the --patch route
( cd "$S" && cp vm/artifact.c orig.c && cp vm/artifact.c simd.c && printf '#include <immintrin.h>\n' >> simd.c
  diff -u --label a/artifact.c --label b/artifact.c orig.c simd.c > simd.patch ; true )
expect "SIMD patch via --patch rejected" 4 $A twin vm ctl_simdp --patch "$S/simd.patch" --control
expect "a header edit (ABI change) is rejected" 4 bash -c "$A twin vm ctl_hdr --new >/dev/null && echo '/* x */' >> $S/vm/arms/ctl_hdr/artifact.h && $A twin vm ctl_hdr --seal --control"

echo; echo "== 5. FAILING DIRECTION: a slowed (answer-identical) twin must time as LOSS, null as NOISE"
expect "new ctl_slow" 0 $A twin vm ctl_slow --new
python3 $HERE/selftest_twins.py "$S/vm/arms/ctl_slow" slow
expect "seal ctl_slow" 0 $A twin vm ctl_slow --seal --control
expect "slowed twin is answer-identical (identity PASS)" 0 $A identity vm ctl_slow --battery 400 --pcre2-sample 100
expect "gate override refused outside selftest" 5 env -u ARTREV_SELFTEST $A time vm --arms orig,orig2,null,ctl_slow --subject cell=$S/subj_dense.txt --rounds 3 --gate-override
has "gate override outside selftest" "refused outside the selftest"
expect "time vm: orig/orig2/null/ctl_slow, 2 subjects, 7 rounds" 0 $A time vm --arms orig,orig2,null,ctl_slow --subject cell=$S/subj_dense.txt --subject sparse=$S/subj_sparse.txt --rounds 7 --gate-override
echo "$OUT" | sed -n '/^subject cell/,$p' | sed 's/^/      | /'
RUN=$(ls -d $S/vm/timing/* | tail -1)
v() { awk -F'\t' -v s="$1" -v a="$2" '$1==s && $2==a {print $11}' "$RUN/summary.tsv"; }
[ "$(v cell ctl_slow)" = LOSS ] && ok "slowed twin reads LOSS on cell" || bad "slowed twin read '$(v cell ctl_slow)' on cell"
[ "$(v sparse ctl_slow)" = LOSS ] && ok "slowed twin reads LOSS on sparse" || echo "NOTE sparse reads '$(v sparse ctl_slow)' (few matches => few calls => small effect; informational)"
[ "$(v cell null)" = NOISE ] && ok "null twin reads NOISE" || bad "null twin read '$(v cell null)'"
[ "$(v cell orig2)" = NOISE ] && ok "original-recompiled reads NOISE" || bad "orig2 read '$(v cell orig2)'"
grep -q GATE-OVERRIDE "$S/vm/iterations.tsv" && ok "gate override is logged in the ledger" || bad "override not logged"
grep -q GATE-OVERRIDE-SELFTEST "$RUN/raw.tsv" && ok "gate override stamped in the raw TSV header" || bad "no stamp in raw TSV"
echo "-- verdict rule on synthetic rounds (WIN / LOSS / NOISE; the null deviation widens the band)"
python3 - <<PY
import sys; sys.path.insert(0, "$HERE")
import timing
def rows(arm, xs): return [{"subject": "s", "arm": arm, "round": i, "ns": x} for i, x in enumerate(xs)]
base = [10.0, 10.1, 9.9, 10.05, 9.95, 10.0, 10.02, 9.98, 10.01, 9.99, 10.0]
R = rows("orig", base) + rows("orig2", [x + 0.01 for x in base]) + rows("null", [x + 0.03 for x in base]) \
  + rows("fast", [x - 1.0 for x in base]) + rows("slow", [x + 1.0 for x in base]) + rows("tiny", [x - 0.02 for x in base]) \
  + rows("noisyfast", [9.0, 11.5, 8.7, 11.0, 8.9, 10.9, 9.2, 11.2, 9.0, 11.1, 9.1])
S = timing.summarize(R, ["orig", "orig2", "null", "fast", "slow", "tiny", "noisyfast"])["s"]
# tiny (-0.02) sits inside the null twin's own +0.03 deviation: NOISE; noisyfast is faster by median but its IQR swallows it
want = {"fast": "WIN", "slow": "LOSS", "null": "NOISE", "orig2": "NOISE", "tiny": "NOISE", "noisyfast": "NOISE"}
bad = [(k, S[k]["verdict"], v) for k, v in want.items() if S[k]["verdict"] != v]
print("synthetic verdicts:", {k: S[k]["verdict"] for k in want})
sys.exit(1 if bad else 0)
PY
[ $? = 0 ] && ok "synthetic WIN/LOSS/NOISE verdicts as the charter's rule" || bad "synthetic verdicts"

echo; echo "== 6. locks and gates REFUSE (never caveat)"
echo > "$S/fake.lock"
expect "suite lock (FILE form) refuses" 5 env ARTREV_SUITE_LOCK_PATH="$S/fake.lock" $A time vm --arms orig,null --subject cell=$S/subj_dense.txt --rounds 3 --gate-override
has "suite lock" "mac-suite\|suite is running"
mkdir -p "$S/fake.lockd"
expect "suite lock (DIRECTORY form) refuses" 5 env ARTREV_SUITE_LOCK_PATH="$S/fake.lockd" $A time vm --arms orig,null --subject cell=$S/subj_dense.txt --rounds 3 --gate-override
mkdir -p "$S/.timing.lock"; echo $$ > "$S/.timing.lock/pid"
expect "a held build-artrev/.timing.lock refuses" 5 $A time vm --arms orig,null --subject cell=$S/subj_dense.txt --rounds 3 --gate-override
rm -rf "$S/.timing.lock"
expect "load gate refuses (load1 above the gate)" 7 $A time vm --arms orig,null --subject cell=$S/subj_dense.txt --rounds 3 --load-max 0.0001 --max-load-wait 2
[ "$(grep -c "	time	null	" $S/vm/iterations.tsv)" = 1 ] && ok "a load-gate refusal is not logged as an attempt" || bad "load refusal was logged"
expect "--remote refuses outside 08:00-19:00" 5 $A time vm --arms orig,null --subject cell=$S/subj_dense.txt --remote ubuntubudu --hour-override 23
has "remote hours" "by-day-only"
expect "--hour-override refused outside the selftest" 5 env -u ARTREV_SELFTEST $A time vm --arms orig,null --subject cell=$S/subj_dense.txt --remote ubuntubudu --hour-override 10 --dry-run
has "hour override outside selftest" "refused outside the selftest"
expect "--remote dry-run prints the commands (daytime)" 0 $A time vm --arms orig,orig2,null --subject cell=$S/subj_dense.txt --remote ubuntubudu --hour-override 10 --dry-run
has "dry-run" "BatchMode=yes"
has "dry-run" "gnutimeout"
has "dry-run" "scratch_lx/artrev"
has "dry-run" "watchdog"

echo; echo "== 7. BOUNDS: <=6 leads, <=4 revisions per lead, <=3 timing runs per revision"
expect "gen bnd" 0 $A gen bnd --pcrec "$PCREC" --pattern 'abd'
expect "null twin bnd" 0 $A twin bnd null --null
expect "identity bnd null" 0 $A identity bnd null --battery 100 --pcre2-sample 0
for k in 1 2 3 4 5 6; do $A twin bnd L$k --new >/dev/null; $A twin bnd L$k --seal >/dev/null && echo "  lead L$k sealed"; done
expect "SEVENTH lead is refused" 3 bash -c "$A twin bnd L7 --new >/dev/null; $A twin bnd L7 --seal"
has "7th lead" "BOUND"
for k in 2 3 4; do $A twin bnd L1 --new >/dev/null 2>&1; rm -rf "$S/bnd/arms/L1"; $A twin bnd L1 --new >/dev/null; $A twin bnd L1 --seal >/dev/null && echo "  L1 revision $k sealed"; done
expect "FIFTH revision of a lead is refused" 3 bash -c "rm -rf $S/bnd/arms/L1; $A twin bnd L1 --new >/dev/null; $A twin bnd L1 --seal"
has "5th revision" "BOUND"
echo "-- timing-run bound on a fresh revision (L2, rev 1)"
expect "identity bnd L2" 0 $A identity bnd L2 --battery 100 --pcre2-sample 0
for k in 1 2 3; do expect "timing run $k of L2 rev1" 0 $A time bnd --arms orig,null,L2 --subject cell=$S/subj_dense.txt --rounds 3 --gate-override; done
expect "FOURTH timing run of one revision is refused" 3 $A time bnd --arms orig,null,L2 --subject cell=$S/subj_dense.txt --rounds 3 --gate-override
has "4th timing run" "BOUND"
echo "  -- ledger:"; $A ledger bnd | sed 's/^/      | /'
echo "-- an UNLOGGED hand edit cannot be timed"
echo '/* sneaky */' >> "$S/bnd/arms/L3/artifact.c"
expect "unsealed edit of L3 refused by time" 3 $A time bnd --arms orig,null,L3 --subject cell=$S/subj_dense.txt --rounds 3 --gate-override
has "unsealed edit" "unlogged edit"

echo; echo "== summary: $((N-FAILS))/$N checks passed, $FAILS failed"
[ $FAILS = 0 ]
