# Draft for I-89 — Linux executor bundle (pcrecdev2, I-57 terms)

**Manager: append this (lightly edited, with your own header/timestamp/ack
line) to `/home/duxevents/pcrec-bench/docs/dev/inbox_from_pcrec.md` as I-89.**
Modeled on I-85 (inbox lines 2529-2567) and I-87 (line 2571 on) for register.
Everything below is written as the message TO the executor.

---

## I-89 — EXECUTOR REQUEST (I-57 terms), SLOT ASKED NOT ASSUMED: FOUR
independent blocks — the all-axes answer-identity sweep, [OPT-FIRSTSET]'s
D77 re-run + soundness arm, and the one-pass-DFA M-B timing. Report,
never diagnose.

**Pin.** pcrec main **8d716693** (abi 29) or any docs-only commit on top,
verified by `git diff --stat 8d716693..HEAD -- src lib cli` printing
nothing — if it prints anything, STOP and report what moved rather than
proceeding on an off-pin tree.

**Your checkout.** `/home/duxevents/pcrec` — pull `main`, then
`git worktree add` a scratch worktree at the resulting commit (a NAMED
pin, not a moving branch checkout, so a later `main` push on your machine
cannot shift the tree mid-run).

**Scratch root.** `/tmp/optloop2` — outside both repos, nothing written
in `/home/duxevents/pcrec-bench` anywhere in this ask (it is read-only
reference throughout; every command that reads it is marked).

**Method.** [OPT-5] STEP 0's rule for every TIMED block below: load1 < 0.5
immediately before the phase starts, a calibrated clock, no `perf` (it is
`perf_event_paranoid=4` on your box per `opt5_step0_profile.md` §1). Block
(A) is NOT timed in this sense — it is an answer-identity sweep, and its
own per-axis wall time is asked for informationally, not gated on load1.

---

### 0. Shared setup (run once; blocks (A)/(B)/(C) all use it)

```sh
# 0.1 pin verification + worktree
cd /home/duxevents/pcrec && git fetch origin && git checkout main && git pull
PIN=$(git rev-parse HEAD)
echo "PIN=$PIN"
git diff --stat 8d716693..$PIN -- src lib cli
# EXPECT: no output. Any output means the tree moved under src/lib/cli
# since the pin this ask names -- STOP, report the diff, do not proceed.

export OPT2=/tmp/optloop2 && mkdir -p "$OPT2"
git worktree add --detach "$OPT2/pcrec" "$PIN"
cd "$OPT2/pcrec" && make -j"$(nproc)"

# 0.2 the three throughput subjects (cycle1_analysis.md 0.3's own shape;
#     WRITES NOTHING in pcrec-bench -- this snippet does not call the
#     bench's own generator, which would rewrite a committed manifest)
mkdir -p "$OPT2/subj"
python3 - <<'PY'
import sys, os, hashlib
sys.path.insert(0, "/home/duxevents/pcrec-bench/bench/capability")
import captext as ct
for sid, n, seed in (("t-64k",65536,0xC0FFEE1),("t-256k",262144,0xC0FFEE2),("t-1m",1048576,0xC0FFEE3)):
    b = ct.text(n, seed)
    open(os.path.join(os.environ["OPT2"], "subj", sid + ".bin"), "wb").write(b)
    print(sid, len(b), hashlib.sha256(b).hexdigest())
PY
# EXPECT, byte for byte against bench/capability/manifest_throughput.tsv:
#   t-64k  65536   d2e4f134473cc40a9a4e7df7a30e0efa11f566d96ee990c62cd663a2439c8524
#   t-256k 262144  3cf7b248873da164518b74e039cc2380f39e233b2899716c82c8eb4b7b49b5a7
#   t-1m   1048576 ccbdf7eb97f15776a68b8bbb9d6387870cd01d4796207fb20032958caf9754ee
# A mismatch means the subject changed and every timing below is off-pin: STOP.

# 0.3 clock calibration (opt5_step0_profile.md §1's dependent add-chain)
cat > "$OPT2/clock.c" <<'EOF'
#include <stdio.h>
#include <time.h>
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);
  return t.tv_sec + 1e-9*t.tv_nsec;}
int main(void){volatile long v=0; long N=2000000000L; double t0=now();
  for(long i=0;i<N;i++){ v=v+1; __asm__ volatile("":"+r"(v)); }
  double dt=now()-t0; printf("%.4f GHz (N=%ld, %.3f s)\n", N/dt/1e9, N, dt); return 0;}
EOF
gcc -O2 -o "$OPT2/clock" "$OPT2/clock.c" && for i in 1 2 3 4 5; do "$OPT2/clock"; done
uptime   # load1 must be < 0.5 before any TIMED phase (blocks B, C); discard above 2.0

# 0.4 the shared find-all driver (cycle1_analysis.md 0.5, verbatim)
cat > "$OPT2/findall.c" <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "art.h"
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);
  return t.tv_sec + 1e-9*t.tv_nsec;}
int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"rb"); fseek(f,0,SEEK_END); long n=ftell(f); rewind(f);
  unsigned char*b=malloc(n); if(fread(b,1,n,f)!=(size_t)n) return 2; fclose(f);
  long iters = argc>2 ? atol(argv[2]) : 5;
  ptrdiff_t caps[RX_NCAPS][2];
  double best=1e30; long count=0;
  for(long it=0; it<iters; it++){
    double t0=now(); size_t pos=0; count=0;
    for(;;){ int r=rx_search(b,(size_t)n,pos,caps); if(r==0) break;
             if(r<0){ printf("giveup %d\n", r); break; }
             size_t s=(size_t)caps[0][0], e=(size_t)caps[0][1];
             count++; pos = (e>s)?e:s+1; if(pos>(size_t)n) break; }
    double dt=now()-t0; if(dt<best) best=dt; }
  printf("%-24s n=%ld matches=%ld best=%.9f s  %.4f ns/byte\n",
         argv[1], n, count, best, best*1e9/(double)n);
  return 0; }
EOF
```

Naming convention (cycle1_analysis.md's own): a `base_/arm1_` binary is the
shipped artifact linked against `findall.c`; a `twin_/reseed_/arm2_` binary
is the same artifact with one stated hand edit, built by the identical
`gcc -O2 -I"$OPT2" -o "$OPT2/<name>" "$OPT2/findall.c" "$OPT2/<name>.c"`
line. Any twin/second-arm binary must be answer-checked against its
base/first-arm (`matches=` equal on every subject) before its timing is
read.

---

### (A) THE ALL-AXES ANSWER-IDENTITY SWEEP — `make test-axes`, unrestricted

**Do not run this until either (i) the manager's capability window under
I-87 has closed (their own done-signal — following the O-43/O-44
numbering this is likely to arrive as O-45, or any later message
reporting I-87 complete), or (ii) the manager names a slot explicitly.**
`tests/axes/run_axes.sh` derives its own `PROCS` from `nproc` (Makefile:1483,
`test-axes: all` → `bash tests/axes/run_axes.sh` then
`PROCS=$(nproc) bash tests/codegen/run_form_census.sh`) and runs it
PAIRWISE at `PROCS=ceil(nproc/2)` per pair — it is CPU-heavy across
(effectively) every core for its whole duration and must not overlap the
bench's own capability measurement.

This block is NOT restricted with `AXES=` — the whole axis family, every
bit-flag denial (currently bits 4-30 of `lib/pcrec.h`'s `pcrec_options.flags`,
~27 axes), both `--engine=` directions, and the `[OPT-DIAL]` `--tune=`
positions. On darwin this is MULTI-HOUR (one full `.rxt`-corpus pass per
axis); on Linux it is unmeasured — please report the wall time. Darwin's
own attempt at the whole sweep was killed by a 60-minute wrapper at axis 6
of ~30 (too short a bound, not a finding) — batch 1's three new axes
(`-fno-vm-anchor-bound` `-fno-end-window` `-fno-req-byte`, bits 28-30)
were separately verified RESTRICTED (`AXES=` naming just those three) at
**24,343/24,343 agree, 0 mismatches, each**, at this exact pin. This ask
is the full, unrestricted run that both reproduces that number for those
three axes and extends it to everything else.

```sh
cd "$OPT2/pcrec"
unset AXES   # be certain nothing restricts the sweep
uptime       # informational only for this block; not load1-gated the way B/C are

nohup gnutimeout 6h env -u AXES make test-axes > "$OPT2/axes_full.log" 2>&1 &
disown
echo "launched, pid $!"
```

Poll (this does not block — see §(D) on DO-THEN-FINISH's Linux-side
analogue: report progress, do not sit foreground):

```sh
tail -n 80 "$OPT2/axes_full.log"
```

**What a green run prints** (docs/testing.md "Answer-identity sweep + form
census"; `run_axes.sh`'s own header):

- Per axis: `agree=N budget-bound=N refused-documented=N (floor F)
  lost-other=N mismatches=N gained=N`. On every axis EXCEPT four
  already-documented shapes, EXPECT `mismatches=0 lost-other=0 gained=0`.
  The four documented exceptions (unrelated to this ask, restated so a
  real exception is not mistaken for a new failure): `-fno-counter`
  (REFUSED-DOCUMENTED, the replication-cap patterns in
  `tests/counterk/counterk.rxt`), `-fno-length-prune`/`-fno-prefilter`
  (BUDGET-bound on the K23 ambiguous-decomposition patterns), and
  `-fprefilter` (REFUSED-DOCUMENTED + BUDGET, the do-or-die force-refusal
  on every DFA-selected pattern).
- Final summary line: `run_axes.sh: all axes answer-identical to default
  (documented refusal populations excepted); --vm-entry-shape tier: ...;
  oracle cross-check ...; DIAL-S3 ...` — EXPECT the oracle cross-check
  (`-fno-premul-table` vs. live libpcre2, PC-4) and DIAL-S3 (the `--tune`
  refusal-set control) both to read `OK`.
- Then `tests/codegen/run_form_census.sh`'s own tail: `checks passed: 1`
  `checks failed: 0` and a `census total wall time: Ns` line.

**The verdict that counts** (root CLAUDE.md's situation-index row on
reading a gate): `make`'s own `*** [test-axes` error line if it failed,
never a `sections ran` count and never a bare `grep FAIL`. Report every
per-axis line verbatim, the final summary line, and whether `make` itself
exited 0.

---

### (B) `[OPT-FIRSTSET]` F1 + F2 (`docs/dev/optloop/firstset_design.md` §7)

F3 is **NOT asked** — it waits on F2's answer (whether the soundness arm
refutes the finding), and building it now would be presuming that answer.

**Precondition — build `base_`/`twin_`/`reseed_` for
`wild-codegrammar-json-constant`.** §7's F1/F2 commands assume these three
binaries already exist from an earlier profile pass; this ask is
standalone, so build them here. The `twin_`/`reseed_` hand-edits below are
`[derived — manager to confirm]`: `firstset_design.md` §3/§4 give the edit
as illustrative C, not a literal patch; this lane compiled the real
artifact on darwin first and verified the variable names
(`rx_can_begin_match`, `forward_state`, `rx_forward_seed_state`,
`rx_forward_byte_class`, `scan_position`) and the exact skip-loop text
below match §4.4's repair one-for-one at this pin. If the assert lines in
either Python patcher fire, the artifact's shape has changed since this
draft was written — STOP and report, do not guess a fix.

```sh
export OPT2=/tmp/optloop2
BENCH=/home/duxevents/pcrec-bench   # read-only reference; nothing written here
P=wild-codegrammar-json-constant
cd "$OPT2/pcrec"

build/pcrec --features all --no-captures -p rx -o "$OPT2/$P.c" \
    --pattern "$(cat "$BENCH/bench/capability/patterns/$P.rx")"
cp "$OPT2/$P.h" "$OPT2/art.h"
gcc -O2 -I"$OPT2" -o "$OPT2/base_$P" "$OPT2/findall.c" "$OPT2/$P.c"
"$OPT2/base_$P" "$OPT2/subj/t-1m.bin" 5
# EXPECT ~3.05-3.09 ns/byte (cycle1_analysis.md M3.b/M3.c's own figure for this row)

# twin_: overwrite rx_can_begin_match[256] to {'t','f','n'} only (M3.c's hand-twin)
python3 - "$OPT2/$P.c" "$OPT2/twin_$P.c" <<'PY'
import re, sys
src = open(sys.argv[1]).read()
keep = {ord('t'), ord('f'), ord('n')}
vals = ", ".join("1" if i in keep else "0" for i in range(256))
pat = re.compile(r"(static const unsigned char rx_can_begin_match\[256\] = \{)(.*?)(\};)", re.S)
m = pat.search(src)
assert m, "rx_can_begin_match[256] not found -- artifact shape changed, STOP"
out = src[:m.start()] + m.group(1) + "\n        " + vals + "\n    " + m.group(3) + src[m.end():]
open(sys.argv[2], "w").write(out)
print("twin written:", sys.argv[2])
PY
gcc -O2 -I"$OPT2" -o "$OPT2/twin_$P" "$OPT2/findall.c" "$OPT2/twin_$P.c"
"$OPT2/base_$P" "$OPT2/subj/t-1m.bin" 1
"$OPT2/twin_$P" "$OPT2/subj/t-1m.bin" 1
# CHECK: matches= must be equal on t-1m before F1's timing is read (both
# should read the SAME count on this large, mostly-nomatch subject; F2
# below is where they are expected to legitimately diverge on the small
# context witness).

# reseed_: twin_ plus firstset_design.md §4.4's two-line repair
python3 - "$OPT2/twin_$P.c" "$OPT2/reseed_$P.c" <<'PY'
import sys
src = open(sys.argv[1]).read()
old = ("        if (forward_state == 0 && last_accept_position == (size_t)-1) {\n"
       "            while (scan_position + 1 < subject_length && !rx_can_begin_match[subject[scan_position]]) scan_position++;\n"
       "        }\n")
new = ("        if (forward_state == 0 && last_accept_position == (size_t)-1) {\n"
       "            size_t entry_position = scan_position;\n"
       "            while (scan_position + 1 < subject_length && !rx_can_begin_match[subject[scan_position]]) scan_position++;\n"
       "            if (scan_position > entry_position)\n"
       "                forward_state = rx_forward_seed_state[rx_forward_byte_class[subject[scan_position - 1]]];\n"
       "        }\n")
n = src.count(old)
assert n == 1, f"expected exactly 1 occurrence of the skip-loop block, found {n} -- STOP"
open(sys.argv[2], "w").write(src.replace(old, new, 1))
print("reseed written:", sys.argv[2])
PY
gcc -O2 -I"$OPT2" -o "$OPT2/reseed_$P" "$OPT2/findall.c" "$OPT2/reseed_$P.c"
```

**F1 — THE RE-RUN THAT GATES THE DECLINE RULE.** `cycle1_profile.md` M3.c
read `json-constant`'s twin at 3.4064 ns/byte where its own artifact's
counts predict 1.4408 (`firstset_design.md` §3.4). Re-run exactly, five
trials rather than one, on a load1 < 0.5 box:

```sh
uptime   # must read < 0.5 before this phase
for T in 1 2 3 4 5; do
  "$OPT2/twin_$P" "$OPT2/subj/t-1m.bin" 5
  "$OPT2/base_$P" "$OPT2/subj/t-1m.bin" 5
done
```

EXPECT if the published reading is right: twin ~3.41 ns/byte, base ~3.09,
on every trial. EXPECT if it was a one-sample artefact: twin at or below
~1.6 ns/byte. A twin near 1.44 reproduces `firstset_design.md` §3.1's cost
model and retires the decline rule; a twin reproducing 3.41 refutes the
model, and the missing term must be named before the row proceeds.

**F2 — THE SOUNDNESS ARM (a correctness run, not a timing one).**

```sh
printf 'atrue xnull ' > "$OPT2/subj/ctx.bin"
for B in base_$P twin_$P reseed_$P; do
  "$OPT2/$B" "$OPT2/subj/ctx.bin" 1
done
```

`firstset_design.md` §4.1 states the EXPECT as `matches=0`, `matches=1`,
`matches=0` (base, twin, reseed), reproduced there via
`c2/scanloop_sim.py` — a Python replay of ONLY the forward-scan tables,
not the compiled two-pass `rx_search`.

**This lane built and ran the exact three binaries on darwin (a
verification step, not the timed ask) and got a DIFFERENT result: all
three read `matches=0`.** `rx_search`'s own body (verified by reading the
compiled artifact directly, both files at this pin) is two-pass — the
forward loop's `last_accept_position` is only a candidate END; a REVERSE
walk from there back to `search_from`, over `rx_reverse_*` tables the
`rx_can_begin_match` patch never touches, independently re-derives
`match_start_position` and rejects unless a genuine accepting state is
reached. On this witness the reverse walk correctly finds that
`"atrue"`'s leading `\b` fails (byte before the candidate start is a word
byte) and never sets `match_start_position`, so `rx_search` returns 0
even though the forward pass's `last_accept_position` was the spurious 5
the simulator predicts. **The simulator's forward-only model and the real
two-pass artifact disagree on this exact witness.**

Run it anyway and report the raw `matches=` triple exactly as measured —
this is Linux, a different box, and the point of asking is to have an
independent confirmation rather than trust one darwin run. If Linux also
reads `0,0,0`, that is a finding for the manager to reconcile against
`firstset_design.md` §4 BEFORE F2 is treated as settled (the reverse pass
may be vetoing the very spurious match §4 is built on, which would not
mean the underlying context-loss claim is false, only that this witness
does not reach it end to end — a different witness, or a pattern/route
where the reverse pass cannot supply the missing context, would be
needed). If Linux instead reads `0,1,0` as the note states, that is
worth flagging too — it would mean this lane's darwin build differs from
the design note's assumption in some way not yet identified.

---

### (C) ONE-PASS M-B (`captures_via_dfa_survey.md` §3.6, via
`docs/dev/optloop/onepass_census.md` §5)

What share of a hybrid-exact artifact's time is the VM's second
(capture-assigning) pass. **ARM 1** (`--features all`) is both passes;
**ARM 2** (`--features all --no-captures`) is the same capture-erased
forward+reverse DFA with no VM pass at all — the difference is the second
pass and nothing else.

**Population** — the 17 capture-forced `hybrid` capability patterns
(`docs/dev/optloop/capsurvey_census.tsv`: `RX_VM_PREFILTER "hybrid"` AND
`RX_ENGINE_WHY` containing `"capture group"`), reproduced here as a
literal list so no bench file needs parsing on your end:

```sh
export OPT2=/tmp/optloop2
BENCH=/home/duxevents/pcrec-bench   # read-only reference; nothing written here
cd "$OPT2/pcrec"

PATTERNS="codegrammar-flat codegrammar-xflag date-nested-plus email-nested-plus \
logparse-atomic logparse-atomic-removed numeric-id-nested-plus phone-list-nested-plus \
wild-datetime-moment-iso8601 wild-logparse-syslogbase-expanded \
wild-secrets-aws-access-key-id wild-secrets-github-pat wild-secrets-slack-webhook-url \
wild-secrets-username-password-pair wild-semdiv-empty-alt-repeat-pcre2 \
wild-validator-ipv4-owasp wild-validator-us-zip-owasp"

uptime   # load1 must be < 0.5 before this phase

for P in $PATTERNS; do
  PAT="$(cat "$BENCH/bench/capability/patterns/$P.rx")"

  build/pcrec --features all -p rx -o "$OPT2/mb1_$P.c" --pattern "$PAT"
  cp "$OPT2/mb1_$P.h" "$OPT2/art.h"
  gcc -O2 -I"$OPT2" -o "$OPT2/arm1_$P" "$OPT2/findall.c" "$OPT2/mb1_$P.c"

  build/pcrec --features all --no-captures -p rx -o "$OPT2/mb2_$P.c" --pattern "$PAT"
  cp "$OPT2/mb2_$P.h" "$OPT2/art.h"
  gcc -O2 -I"$OPT2" -o "$OPT2/arm2_$P" "$OPT2/findall.c" "$OPT2/mb2_$P.c"

  # this pattern's own search_short/match subject, from the bench's own
  # COMMITTED expectations.tsv [derived -- manager to confirm this is the
  # "match regime" the survey means; expectations.tsv's only two regime
  # values are search_short/throughput, and search_short/match is the row
  # where a single short-subject search is the whole cost, which reads as
  # the closest match to the survey's wording]
  SID=$(awk -F'\t' -v p="$P" '$1==p && $3=="search_short" && $4=="match"{print $2; exit}' \
        "$BENCH/bench/capability/expectations.tsv")
  echo "== $P  own-subject=$SID"

  for S in t-64k t-256k t-1m; do
    "$OPT2/arm1_$P" "$OPT2/subj/$S.bin" 5
    "$OPT2/arm2_$P" "$OPT2/subj/$S.bin" 5
  done
  if [ -n "$SID" ] && [ -f "$BENCH/bench/capability/subjects/$SID.bin" ]; then
    "$OPT2/arm1_$P" "$BENCH/bench/capability/subjects/$SID.bin" 200
    "$OPT2/arm2_$P" "$BENCH/bench/capability/subjects/$SID.bin" 200
  else
    echo "$P: bench/capability/subjects/$SID.bin not present on this box -- report as MISSING; do NOT run gen_subjects.py to create it (that writes into pcrec-bench)"
  fi
done
```

**Answer-check before any timing is read**: for every pattern and every
subject, `arm1_$P`'s `matches=` must equal `arm2_$P`'s `matches=`
(`--no-captures` erases capture assignment, never the match/no-match
decision or span). A mismatch is reported by pattern/subject, and that
pattern's timing is not read.

**What to report**: the raw `arm1`/`arm2` `best=`/`ns/byte` lines for all
17 patterns × 4 subjects (3 throughput + 1 own), verbatim — the manager
computes each cell's `(arm1 − arm2) / arm1` VM-pass share and applies
`onepass_census.md` §5's decision rule (under ~10% on throughput / ~25% on
`match` is "not the cost"; over half on `match` is "has a target").

---

### (D) Done-signal — what to return

- **(A)**: the full `$OPT2/axes_full.log` transcript (every per-axis
  line, the final `run_axes.sh:` summary line, the census script's
  `checks passed:`/`checks failed:` lines), `make`'s own exit status, and
  the wall time (`time` around the `make test-axes` invocation, or the
  log's own start/end timestamps). Keep `$OPT2` until "I-89 logs fetched".
- **(B)**: F1's five trial pairs (twin/base `ns/byte` each), F2's three
  `matches=` lines, and confirmation the two Python patchers' `assert`
  lines did not fire (or, if they did, the exact assertion message).
- **(C)**: the 17×4×2 raw timing lines plus every `matches=` pair
  checked, and which (if any) `SID` subjects were reported MISSING.
- For every block: the clock calibration lines (5 runs), the `uptime`
  line taken immediately before each TIMED phase (B, C — not A), and the
  subject sha256 lines from setup 0.2.
- Report, never diagnose (I-57). A twin/arm reading outside its stated
  EXPECT is a finding to report exactly as measured, not a defect to
  explain.

**Ordering** (§(A)'s own note restated): (B) and (C) are short — run them
first, in a quiet slot once load1 < 0.5, ideally right after your I-87
capability window closes for other reasons anyway. (A) is the long,
CPU-heavy one — launch it detached (`nohup … & disown`) once (B)/(C) are
done and either I-87's window has closed or the manager names a slot, and
report back once its log shows `sections ran:`-style completion (per
root CLAUDE.md: read `make`'s `*** [` lines for the real verdict, not that
trailer alone).
