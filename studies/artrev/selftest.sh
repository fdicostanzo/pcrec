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


echo; echo "== 8. HARDENED IDENTITY: shrunken resources + THE GIVE-UP RULE + window start + livelock bound"
expect "identity vm null drives the _in shapes (the HAVE_IN compile fix)" 0 $A identity vm null --battery 200 --pcre2-sample 0
echo "$OUT" | grep -Eq '[1-9][0-9]* `_in` search lines driven' && ok "_in search lines are driven (not zero)" || bad "no _in lines driven"
has "shrunk phase runs by default" "shrunken resources (0/1 frames"
has "shrunk phase counts the original's give-ups" "original gives up on"
echo "-- a twin that answers WRONG where the original gives up must FAIL; a CORRECT one must PASS; one that gives up where the original answers must FAIL"
for k in giveup_wrong giveup_right giveup_lost; do
  expect "new ctl_$k" 0 $A twin vm ctl_$k --new
  python3 $HERE/selftest_twins.py "$S/vm/arms/ctl_$k" $k
  expect "seal ctl_$k" 0 $A twin vm ctl_$k --seal --control
done
expect "give-up repaired WRONG: identity FAILS (oracle rejects the fabricated answer)" 1 $A identity vm ctl_giveup_wrong --battery 300 --pcre2-sample 0
has "giveup_wrong" "GIVE-UP RULE VIOLATED"
has "giveup_wrong" "REPAIR DISAGREES with libpcre2"
expect "give-up repaired RIGHT (full buffers retried): identity PASSES under the give-up rule" 0 $A identity vm ctl_giveup_right --battery 300 --pcre2-sample 0
echo "$OUT" | grep -Eq '[1-9][0-9]* give-up repair\(s\) of which [1-9][0-9]* checked against libpcre2' && ok "the repairs were counted AND checked against libpcre2" || { bad "no checked repairs reported"; echo "$OUT" | grep repair | head -3; }
expect "twin GIVES UP where the original answers: identity FAILS" 1 $A identity vm ctl_giveup_lost --battery 300 --pcre2-sample 0
has "giveup_lost" "twin GIVES UP where the original answers"
echo "-- the unit of the rule on synthetic transcripts"
python3 - <<PY
import sys; sys.path.insert(0, "$HERE")
import identity as I
o = b"SI.f0t0\t0\t0\t-3\t-2\t-2\nSI.f1t0\t0\t0\t1\t0\t1\nF\t0\t0\t-2\t-2\t-2\nM\t0\t0\t-1\nN\t0\t0\t5\n"
ok_t = b"SI.f0t0\t0\t0\t1\t0\t1\nSI.f1t0\t0\t0\t1\t0\t1\nF\t0\t0\t1\t0\t1\nF\t0\t5\t0\t-2\t-2\nM\t0\t0\t-1\nN\t0\t0\t5\n"
g = I.giveup_compare(o, ok_t)
assert not g["fails"], g["fails"]
assert len(g["repairs"]) == 2 and len(g["twin_only"]) == 1, (len(g["repairs"]), len(g["twin_only"]))
lost = b"SI.f0t0\t0\t0\t-3\t-2\t-2\nSI.f1t0\t0\t0\t-3\t-2\t-2\nF\t0\t0\t-2\t-2\t-2\nM\t0\t0\t-1\nN\t0\t0\t5\n"
assert any("GIVES UP" in w for w, _, _ in I.giveup_compare(o, lost)["fails"])
diff = o.replace(b"SI.f1t0\t0\t0\t1\t0\t1", b"SI.f1t0\t0\t0\t1\t0\t2")
assert any("answers differ" in w for w, _, _ in I.giveup_compare(o, diff)["fails"])
nv = o.replace(b"N\t0\t0\t5", b"N\t0\t0\t6")
assert any("N/V" in w for w, _, _ in I.giveup_compare(o, nv)["fails"])
other = o.replace(b"SI.f0t0\t0\t0\t-3", b"SI.f0t0\t0\t0\t-2")      # a different give-up code is still a give-up
assert not I.giveup_compare(o, other)["fails"]
print("give-up rule unit cases ok")
PY
[ $? = 0 ] && ok "give-up rule: repair / lost / differ / N-V / code-move" || bad "give-up rule unit cases"
echo "-- window start (a hybrid artifact: the prefilter + verifying attempt shape)"
python3 - <<'PY'
import os, random
r = random.Random(11)
open("%s/subj_log.txt" % os.environ["ARTREV_ROOT"], "wb").write(
    b"".join(r.choice([b"ERROR disk timeout\n", b"FATAL x refused ", b"INFO fine\n", b"ERROR ok\n", b"xx ", b"timeout "]) for _ in range(900)))
PY
expect "gen hyb (internal prefilter)" 0 $A gen hyb --pcrec "$PCREC" --flags=--no-captures --pattern '\b(?:ERROR|FATAL)\b.{0,40}?\b(?:timeout|refused)\b'
expect "twin hyb null" 0 $A twin hyb null --null
HYBID="--subject $S/subj_log.txt --battery 300 --pcre2-sample 0 --match-example 'ERROR x timeout' --match-example 'FATAL refused'"
expect "identity hyb null PASSES incl. the window phase" 0 eval "$A identity hyb null $HYBID"
has "hyb window" "prefilter windows compared"
expect "new ctl_early" 0 $A twin hyb ctl_early --new
python3 $HERE/selftest_twins.py "$S/hyb/arms/ctl_early" start_early
expect "seal ctl_early" 0 $A twin hyb ctl_early --seal --control
expect "a start-too-early twin (answers identical) FAILS by the window differential" 1 eval "$A identity hyb ctl_early $HYBID"
has "start_early" "start differences"
echo "$OUT" | grep -q "FIRST DIFFERENCE" && bad "start_early should be invisible to answer identity (it differed)" || ok "start_early is invisible to answer identity: only the window differential catches it"
expect "new ctl_earlyloop" 0 $A twin hyb ctl_earlyloop --new
python3 $HERE/selftest_twins.py "$S/hyb/arms/ctl_earlyloop" start_early_loop
expect "seal ctl_earlyloop" 0 $A twin hyb ctl_earlyloop --seal --control
expect "the unconditionally-early start twin is also caught (by the window differential)" 1 eval "$A identity hyb ctl_earlyloop $HYBID"
has "earlyloop" "start differences"
expect "new ctl_hang" 0 $A twin vm ctl_hang --new
python3 $HERE/selftest_twins.py "$S/vm/arms/ctl_hang" hang
expect "seal ctl_hang" 0 $A twin vm ctl_hang --seal --control
T0=$(date +%s)
expect "a HANGING twin FAILS FAST (the livelock bound, not the 900 s timeout)" 1 env ARTREV_LIVELOCK_FLOOR=5 bash -c "$A identity vm ctl_hang --battery 200 --pcre2-sample 0"
T1=$(date +%s)
has "hang" "LIVELOCK"
[ $((T1-T0)) -lt 120 ] && ok "livelock failed in $((T1-T0)) s" || bad "livelock took $((T1-T0)) s"
echo "-- iteration shortcuts cannot reach timing"
expect "new ctl_part" 0 $A twin hyb ctl_part --new
expect "seal ctl_part" 0 $A twin hyb ctl_part --seal --control
expect "identity with --skip-window logs PASS-PARTIAL" 0 eval "$A identity hyb ctl_part $HYBID --skip-window"
has "partial" "PASS-PARTIAL"
expect "time refuses a PASS-PARTIAL identity" 3 $A time hyb --arms orig,null,ctl_part --subject cell=$S/subj_log.txt --rounds 3 --gate-override
has "partial refused" "no PASSING identity"


echo; echo "== 9. REAL twins on the pinned A09 fixture (lane rvA09, 2026-10-06)"
FX=$HERE/fixtures/a09_pin57db5152; A09D=$TREE/docs/dev/optloop/artrev/A09
mkdir -p "$S/a09/arms/orig" "$S/a09/arms/orig2"
cp "$FX/artifact.c" "$FX/artifact.h" "$FX/meta.json" "$S/a09/"
for d in orig orig2; do cp "$FX/artifact.c" "$FX/artifact.h" "$S/a09/arms/$d/"; done
A09ID="--subject $(ls $A09D/edge_subjects/e-*.bin | head -150 | tr '\n' '@' | sed 's/@/ --subject /g' | sed 's/ --subject $//') --battery 200 --pcre2-sample 0 --match-example 'ERROR x timeout' --match-example 'CRIT timed out'"
expect "a09: L4 r2 applies (control)" 0 $A twin a09 L4_r2 --patch "$A09D/twins/L4.r2.patch" --control
expect "a09: L4 r3 applies (control)" 0 $A twin a09 L4_r3 --patch "$A09D/twins/L4.r3.patch" --control
expect "a09: ctlL4e (start one EARLY) applies (control)" 0 $A twin a09 ctlL4e --patch "$A09D/controls/ctlL4e.r1.patch" --control
expect "a09: L4 r2 (answers where the original gives up with 0 frames/trail) PASSES the give-up rule" 0 eval "$A identity a09 L4_r2 $A09ID --skip-window"
echo "$OUT" | grep -Eq '[1-9][0-9]* give-up repair\(s\) of which [1-9][0-9]* checked against libpcre2' && ok "a09 L4 r2: its repairs were found, counted, and equal libpcre2's" || { bad "a09 L4 r2: no checked repairs"; echo "$OUT" | grep -i "repair\|shrunk" | head; }
expect "a09: L4 r2 FAILS --strict-giveup (it changes the limits behaviour)" 1 eval "$A identity a09 L4_r2 $A09ID --skip-window --strict-giveup"
has "a09 strict" "strict-giveup"
expect "a09: L4 r3 (capacity guard added) is exact even under --strict-giveup" 0 eval "$A identity a09 L4_r3 $A09ID --skip-window --strict-giveup"
expect "a09: ctlL4e (the livelocking early start) FAILS FAST, no 900 s timeout" 1 env ARTREV_LIVELOCK_FLOOR=10 bash -c "$A identity a09 ctlL4e $A09ID"
T9=$?


echo; echo "== 10. LAYOUT CONTROL: the pad-shift arms (charter S4; k87twin_align.sh's method)"
python3 - <<PY
import os, subprocess, sys
sys.path.insert(0, "$HERE")
import common as C, timing as T
meta = C.load_meta("vm")
names = T.make_pad_arms("vm", ["orig"], [16, 32, 48, 64])
addrs = {}
for arm in ["orig"] + names:
    exe = C.compile_arm(meta, os.path.join(C.art_dir("vm"), "arms", arm), "id")
    out = subprocess.run(["nm", exe], capture_output=True, text=True).stdout.split("\n")
    a = [int(l.split()[0], 16) for l in out if l.split() and l.split()[-1] in ("_art_search", "art_search")]
    addrs[arm] = a[0]
base = addrs["orig"]
moved = {n: (addrs[n] - base) for n in names}
print("art_search offsets vs orig:", moved)
assert all(v % 64 != 0 for v in moved.values()), moved
assert len(set(v % 64 for v in moved.values())) == 4, moved
PY
[ $? = 0 ] && ok "pad arms MOVE the code: 4 distinct code offsets (mod 64) vs the original" || bad "pad arms do not move the code"
expect "--pads with fewer than 4 offsets is refused" 2 $A time vm --arms orig,null --pads 16,32 --subject cell=$S/subj_dense.txt --rounds 3 --gate-override
expect "pads must be multiples of 16" 2 $A time vm --arms orig,null --pads 16,32,48,50 --subject cell=$S/subj_dense.txt --rounds 3 --gate-override
expect "time with the layout control: orig/orig2/null/ctl_slow, pads 16-64 on orig and ctl_slow" 0 $A time vm --arms orig,orig2,null,ctl_slow --pads 16,32,48,64 --pad-arms orig,ctl_slow --subject cell=$S/subj_dense.txt --rounds 7 --gate-override
has "layout" "layout: pad-median"
has "layout" "no pad control for this arm"
RUN=$(ls -d $S/vm/timing/* | tail -1)
[ "$(awk -F'\t' '$1=="cell" && $2=="ctl_slow" {print $11}' "$RUN/summary.tsv")" = LOSS ] && ok "the slowed twin still reads LOSS with the layout control" || bad "slowed twin lost its LOSS under the pad control"
grep -q "orig@p16" "$RUN/raw.tsv" && ok "pad arms were timed in the same interleaved rounds" || bad "no pad rows in raw.tsv"
python3 - <<PY
import sys; sys.path.insert(0, "$HERE")
import timing
def rows(arm, xs): return [{"subject": "s", "arm": arm, "round": i, "ns": x} for i, x in enumerate(xs)]
base = [10.0, 10.1, 9.9, 10.05, 9.95, 10.0, 10.02, 9.98, 10.01, 9.99, 10.0]
def mk(extra):
    R = rows("orig", base) + rows("null", [x + 0.03 for x in base])
    for arm, shift in extra.items():
        R += rows(arm, [x + shift for x in base])
    return R
arms = ["orig", "null", "X", "orig@p16", "orig@p32", "orig@p48", "orig@p64", "X@p16", "X@p32", "X@p48", "X@p64"]
def verdict(shifts):
    S = timing.summarize(mk(shifts), arms)
    timing.apply_layout(S, arms)
    return S["s"]["X"]["verdict"]
clean = {"X": -1.0, "orig@p16": 0.0, "orig@p32": 0.0, "orig@p48": 0.0, "orig@p64": 0.0, "X@p16": -1.0, "X@p32": -1.0, "X@p48": -1.0, "X@p64": -1.0}
# 1: a clean 10% win at every pad is a WIN
assert verdict(clean) == "WIN", verdict(clean)
# 2: the same median win, but the ORIGINAL itself swings 1.5 ns across pads: layout alone moves more than the win
swing = dict(clean, **{"orig@p16": 1.5, "orig@p48": -1.5})
assert verdict(swing) == "NOISE", verdict(swing)
# 3: wins at three pads, loses at one paired pad (the win rides one layout)
flip = dict(clean, **{"X@p64": 0.4})
assert verdict(flip) == "NOISE", verdict(flip)
# 4: a clean slowdown is a LOSS
loss = {k: (2.0 if k.startswith("X") else v) for k, v in clean.items()}
assert verdict(loss) == "LOSS", verdict(loss)
print("layout verdict unit cases ok")
PY
[ $? = 0 ] && ok "layout verdicts: clean WIN, layout-swing NOISE, one-pad-flip NOISE, clean LOSS" || bad "layout verdict unit cases"

echo; echo "== summary: $((N-FAILS))/$N checks passed, $FAILS failed"
[ $FAILS = 0 ]
