#!/usr/bin/env bash
# tests/codegen/run_lookaround_identity.sh — module `lookaround`'s BYTE-IDENTITY
# GATE (lookaround_design.md §9.1/§9.2), built at [M6.6.2] WAVE 0 and running
# today in its PURE-REFACTOR mode.
#
# THE CLAIM IT ASSERTS TODAY is stronger than the one it will assert when the
# module lands, and deliberately so. Wave 0 is D70's tagged-union refactor of
# `struct Ast` — ~250 mechanical access-site renames, zero behaviour change,
# no new construct, no new kind, no module. So the claim is not "a
# lookaround-FREE pattern is unmoved"; it is that EVERY pattern is unmoved, on
# every axis, byte for byte, including the ones the compiler REFUSES and
# including the D37 feature stamp. That is what `STRICT_ALL` means below.
#
# WHY THE REFERENCE IS A PINNED COMMIT AND NOT A `-D` KNOB — the same finding
# `run_atomic_identity.sh` and `run_backref_identity.sh` record, and it bites
# harder here than in either. tests/mech/CLAUDE.md measured that a reference
# built from THE TREE'S OWN SOURCES behind a `-D` knob is sabotaged along with
# the subject, so an edit outside the knob's gated region CANCELS (1175/1175
# and 1135/1135, blind, on two separate waves). A refactor has no gated region
# AT ALL: the union either is the layout or it is not, and there is no knob
# that could make one build use `n->rmin` and the other `n->u.rep.rmin` without
# being the refactor itself. So the reference is built by `git archive` from a
# PINNED PRE-REFACTOR COMMIT and shares no sources with the subject.
#
# FOUR AXES (Frank's ASK-4 ruling): `default`, `--engine=vm`, `-fno-prefilter`,
# `--no-captures`. The default alone is blind to most of src/gen/emit_vm.c —
# under it most corpus patterns route to the DFA and never reach the VM
# emitter, which is where 174 of the wave's 249 renamed sites live. The other
# three each reach a lowering the default does not: `--engine=vm` forces the VM
# for everything, `-fno-prefilter` removes the DFA prefilter from the hybrid,
# and `--no-captures` changes which `A_CAP` nodes are born at all.
#
# THE COMPARISON IS ON RAW BYTES, AND THE SWEEP IS PYTHON FOR THAT REASON. Its
# two predecessors compare with `a="$(gen_a ...)"`, and command substitution
# STRIPS TRAILING NEWLINES — so a difference confined to trailing bytes is
# invisible to them. At a pure refactor that is not an acceptable blind spot,
# so the sweep captures stdout, stderr and exit status as bytes and compares
# them exactly.
#
# NO STAMP STRIP UNDER `STRICT_ALL=1`, and that is a rule rather than an
# omission. `run_atomic_identity.sh`'s successors are entitled to normalise the
# D37 feature stamp because a MODULE changes it legitimately. A pure refactor
# changes no module and no feature, so under that mode the stamp must be
# identical too and a difference that is ONLY the stamp is a FINDING to take to
# the manager. **In the default BUCKET mode the three stamp lines ARE stripped,
# and the strip is ASSERTED to remove exactly three** — see "THE STAMP STRIP IS
# NOW ALLOWED" below, which is the wave B+C amendment to this paragraph rather
# than a contradiction of it.
#
# THE POSITIVE CONTROL IS IN TWO PARTS, because "0 differences" between a tree
# and itself is worth exactly nothing:
#   (a) THE REFERENCE IS ASSERTED PRE-REFACTOR — it must contain no `A_LOOK`
#       (the module has not landed) and no `u.rep` (the union has not landed).
#       **Wave B+C adds a THIRD part, (c), which is the one design §9.2 calls
#       "the half that can actually fail": the bearing bucket must be REFUSED
#       IN FULL by the reference (`ctl_bad == 0 && ctl_ok == nb`). Part (b)
#       below is a claim about the SCRIPT; part (c) is a claim about the two
#       COMPILERS, re-answered on every run.**
#       A mistyped pin that resolved to something recent would otherwise build
#       a reference that agrees everywhere and report a clean bill of health.
#   (b) THE GATE IS DEMONSTRATED RED — TWICE, and the two results together are
#       the finding this control produced. The manager's ruling was to use the
#       REAL hazard rather than a synthetic edit, on the reasoning that it is
#       the miscompile the gate exists to catch. Doing so measured something
#       more useful than a red bar.
#
#       CONTROL b1 — THE REAL HAZARD. Remove the `if (n->k == A_REP)` guard
#       from `rd_node` in `src/opt/revdet.c` (the state a naive D70 port lands
#       in), rebuild, and run this script. IT MUST GO RED:
#           default 7, --engine=vm 7, -fno-prefilter 7 differing stdout
#           comparisons; `checks failed: 3`.
#       The differing patterns are exactly the cells written for it —
#       `((H)|I){3}J`, `((H)|b){0,4}c`, `((I)|J){2}K`,
#       `(([\x80-\x8f])|b){0,4}c` and their three siblings in
#       `tests/rungselect/revdet_highbytes.rxt`.
#
#       `--no-captures` reports 0 and that is CORRECT, not a gap: under that
#       flag the `A_CAP` nodes are never born, so the revdet capture
#       reconstruction this bug corrupts is not emitted at all. It is the one
#       axis structurally blind to this hazard, which is the same reason
#       tests/rungselect/CLAUDE.md requires every pattern there to be
#       capture-bearing.
#
#       THIS CONTROL DID NOT ALWAYS GO RED, and the history is why the cells
#       exist — keep it. When the guard was first written this gate reported
#       ZERO differences on all four axes with the guard removed. The arithmetic
#       is why. The union sits at offset +40 and `u.cls.bits` spans +40..+71, so
#       the unguarded clear writes:
#           u.rep.possessive @ +49      -> class bitmap BYTE 9  -> 0x48-0x4F
#           u.rep.revbody    @ +56..+63 -> bitmap BYTES 16-23   -> 0x80-0xBF
#       i.e. it zeroes the reversed body's membership for `H`-`O` and the
#       0x80-0xBF range. At that moment exactly 44 corpus patterns took the
#       reverse-deterministic rung and EVERY ONE was spelled in lowercase
#       ASCII, so not one had a bit in either range: the population could not
#       express the bug. `tests/rungselect/revdet_highbytes.rxt` was written to
#       close that, with cells in BOTH ranges and `g` capture lines.
#
#       WHAT THE BUG ACTUALLY COSTS, measured: under the unguarded build the
#       reversed body's class tests compile to an ALL-ZERO
#       `rx_class_bitmap[32]` (visible by diffing the emitted C), the backward
#       walk can never take them, and the LAST ITERATION'S CAPTURES — which
#       `u.rep.revbody` exists to recover — come back UNSET:
#           `((H)|I){3}J`   on "HHHJ": groups (2,3)(2,3) -> (-1,-1)(-1,-1)
#           `((H)|b){0,4}c` on "HHc" : groups (1,2)(1,2) -> (-1,-1)(-1,-1)
#           `((I)|J){2}K`   on "IJK" : groups (1,2)(0,1) -> (-1,-1)(-1,-1)
#       THE WHOLE-MATCH SPAN IS UNCHANGED in every case, which is why a
#       span-only driver (including `--emit-main`, which prints only
#       capture_spans[0]) sees nothing. Compare all `RX_NCAPS` spans. Mech row
#       S121 is the permanent detector; it scores corpus 61fail/66pass.
#
#       CONTROL b2 — THE SYNTHETIC EDIT, which is what actually proves this
#       script can go red. In `vm_rep`'s mandatory-copies loop
#       (`src/gen/emit_vm.c`, the `for (int i = 0; i < a->u.rep.rmin; i++) {`
#       in the POSSESSIVE arm — NOT unique in the file, so edit BY LINE
#       NUMBER, not with a bare `sed`), swap the one read `a->u.rep.rmin` for
#       `a->u.rep.rmax`:
#
#         python3 - <<'EOF'
#         P="src/gen/emit_vm.c"; L=open(P).read().split("\n")
#         i = next(j for j,x in enumerate(L)
#                  if x.strip() == "for (int i = 0; i < a->u.rep.rmin; i++) {"
#                  and 4000 < j < 4200)
#         L[i] = L[i].replace("a->u.rep.rmin", "a->u.rep.rmax")
#         open(P,"w").write("\n".join(L))
#         EOF
#         make -j12 && bash tests/codegen/run_lookaround_identity.sh   # RED
#         git checkout src/gen/emit_vm.c && make -j12                  # revert
#
#       MEASURED: differing stdout comparisons default 39, --engine=vm 43,
#       -fno-prefilter 39, --no-captures 22 — `checks failed: 4`, one per
#       axis, on patterns like `((?:a{0,2}b)+c)` and `(?:aa|a)++b`. All four
#       axes caught it at DIFFERENT counts, which is the argument for running
#       four: no single axis sees the whole surface.
#
#       WHAT b1 AND b2 SAY TOGETHER: the gate goes red on a REAL miscompile
#       (b1) and on a synthetic emitter edit (b2), on three and four axes
#       respectively. b1's history is the standing warning: a green gate is a
#       statement about THIS POPULATION, and a population can be blind to a
#       real bug in a way that is invisible until someone constructs the cell.
#
# THE BUCKET SPLIT LANDED AT WAVE B+C, AND `STRICT_ALL` NOW DEFAULTS TO 0.
# The strict claim above was true for exactly as long as no pattern in the
# corpus compiled to something the reference cannot build. Wave B+C ends that:
# `(?=`, `(?!` and `(?*` patterns now compile, and the pinned pre-module
# reference REFUSES every one of them, so `STRICT_ALL=1` goes red BY
# CONSTRUCTION on this tree. That is a correct answer to the wrong question,
# and the gate's job from here is the ordinary one every module's identity gate
# has: **a lookaround-FREE pattern's emitted bytes did not move**.
#
#   STRICT_ALL=0  (DEFAULT since wave B+C) -- split the population with the
#                 grammar-aware classifier below, compare only the FREE bucket
#                 for byte identity on all four axes, and use the BEARING
#                 bucket as the refusal-mismatch positive control.
#   STRICT_ALL=1  the PURE-REFACTOR MODE, kept runnable and kept documented.
#                 It is the right mode for a change that adds no construct -- a
#                 rebase of wave 0 onto a moved base, or any later refactor of
#                 the same kind -- and it is the STRONGER claim when it
#                 applies. Do not run it on a tree where a lookaround compiles
#                 and read the red as a finding; the finding is that the mode
#                 does not fit the tree.
#
# THE STAMP STRIP IS NOW ALLOWED, AND ONLY NOW (design §9.1). Wave 0 forbade it
# because that wave changed no module and no feature, so a stamp difference was
# a finding. This wave DOES change what the D37 stamp describes, so the three
# stamp lines are normalised away in bucket mode. **The strip asserts it
# removed EXACTLY THREE lines from each side of every compiled comparison**;
# anything else is a `STAMP FILTER` failure and not a silent normalisation,
# because a strip that quietly removed four lines would be absorbing exactly
# the difference this gate exists to report. STRICT_ALL=1 still strips nothing.
#
# Usage: bash tests/codegen/run_lookaround_identity.sh
# Env: PCREC (default <root>/build/pcrec), CC, KEEP=1, SANFLAGS,
#      LOOKAROUND_IDENTITY_REF (the pin), STRICT_ALL (default 0; see above),
#      JOBS (sweep concurrency, default nproc)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
SANFLAGS="${SANFLAGS:-}"
KEEP="${KEEP:-0}"
STRICT_ALL="${STRICT_ALL:-0}"
JOBS="${JOBS:-$(nproc 2>/dev/null || echo 4)}"

# THE PIN. `eacac76` is [M6.6.2]'s branch point — the last commit before D70's
# tagged union, i.e. the last tree whose `struct Ast` carries the per-kind
# fields at top level. Both halves of control (a) are checked against it below.
REFCOMMIT="${LOOKAROUND_IDENTITY_REF:-eacac76}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "lookaround-identity: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
finish() { echo; echo "checks passed: $pass"; echo "checks failed: $fail"; \
           [ "$fail" -eq 0 ] || exit 1; exit 0; }
die()    { bad "$1"; finish; }

# ---- RETIREMENT GUARD ([DD-14] wave A, 2026-08-24) ------------------------
# Wave A's ABI event (main 0c75c96: PCREC_ERR_RECURSE, ERR_FLOOR -4 -> -5,
# PCREC_ERR_INTERNAL below the floor) changed the emitted `#define` block of
# EVERY artifact. This gate's reference is a PRE-A_LOOK commit BY
# CONSTRUCTION (positive control (a) below refuses anything newer), so no
# valid pin exists on which a post-0c75c96 subject can be byte-identical:
# from that commit on the gate would go red on every cell for a reason that
# is not a regression, and a gate that fails for a non-reason is a
# check-design failure of its own (tests/mech/CLAUDE.md). Its job — D70's
# refactor and [M6.6.2]'s eight waves changing no lookaround-free artifact —
# was served and recorded at [M6.6]'s close (1a8541e). The subroutines
# design's four-axis identity gate (subroutines_design.md §9, [DD-14] wave
# E) succeeds it, pinned at post-wave-A main. Filtering the #define lines
# out of the comparison was considered and rejected: "a filtered gate is a
# check-design failure" is this file's own precedent. So: REFUSE, loudly.
if grep -q 'PCREC_ERR_INTERNAL' "$ROOT_DIR/src/gen/emit_dfa.c" 2>/dev/null; then
    die "RETIRED: the subject tree carries [DD-14] wave A's ABI event (PCREC_ERR_INTERNAL in src/gen/emit_dfa.c), which changed every artifact's #define block; this gate's pre-A_LOOK reference cannot be moved past it (positive control (a)). Its last valid run is recorded at [M6.6]'s close (1a8541e); the [DD-14] identity gate (wave E) is its successor. To re-run it historically, check out a subject before 0c75c96."
fi

# ---- the reference compiler, from the PINNED PRE-REFACTOR COMMIT ----------
REFSRC="$WORKDIR/ref"
mkdir -p "$REFSRC"
if ! git -C "$ROOT_DIR" rev-parse --verify --quiet "$REFCOMMIT^{commit}" >/dev/null; then
    die "the pinned pre-refactor commit $REFCOMMIT does not resolve in this repository — the reference cannot be built, and a gate that cannot build its reference must SAY so rather than skip"
fi
if ! git -C "$ROOT_DIR" archive "$REFCOMMIT" src lib cli \
        | tar -x -C "$REFSRC" 2>"$WORKDIR/arch.log"; then
    die "could not git-archive $REFCOMMIT: $(head -3 "$WORKDIR/arch.log")"
fi

# ---- POSITIVE CONTROL (a): the reference really is PRE-refactor ----------
if grep -rq 'A_LOOK' "$REFSRC/src" 2>/dev/null; then
    die "the reference tree at $REFCOMMIT already contains A_LOOK — that is not a pre-module commit, so every comparison below would be a build against itself"
fi
if grep -rq 'u\.rep\.' "$REFSRC/src" 2>/dev/null; then
    die "the reference tree at $REFCOMMIT already contains \`u.rep.\` — D70's union has ALREADY landed there, so this gate would be comparing the refactor against itself and would report identity no matter what was broken"
fi
ok "positive control (a): the reference at $REFCOMMIT contains neither A_LOOK nor \`u.rep.\` — it is a genuinely PRE-refactor tree, sharing no sources with the subject"

REF="$WORKDIR/pcrec_prerefactor"
REF_SRCS="$(find "$REFSRC/src" -name '*.c' | sort)"
[ -n "$REF_SRCS" ] || die "found no compiler sources in the archived reference tree"
# shellcheck disable=SC2086
if ! $CC -O0 -std=gnu11 -Wall -Wextra -I"$REFSRC/lib" -I"$REFSRC/src" $SANFLAGS \
        -o "$REF" "$REFSRC"/cli/main.c $REF_SRCS 2>"$WORKDIR/refbuild.log"; then
    bad "could not build the pre-refactor reference compiler from $REFCOMMIT:"
    head -20 "$WORKDIR/refbuild.log" >&2
    finish
fi
[ -x "$PCREC" ] || die "subject compiler $PCREC is missing or not executable — run \`make\` first"

# ---- the population ------------------------------------------------------
# Every `pattern` line from every .rxt under tests/ (known_fail included: a
# deferred bug is still a pattern whose emitted bytes must not move), PLUS
# every pattern the reject table exercises. The second half is included
# because this wave's claim covers REFUSALS too — those patterns are the only
# population that exercises the stderr comparison at all, and a refactor that
# moved a diagnostic would otherwise go unseen.
#
# LC_ALL=C on the sort, and it is not a formatting preference: a UTF-8
# collation treats strings differing only in punctuation as EQUAL, and for a
# corpus of regexes punctuation IS the content (R24 M-F1).
PATFILE="$WORKDIR/patterns"
RXTPAT="$WORKDIR/patterns.rxt"
REJPAT="$WORKDIR/patterns.reject"

find "$ROOT_DIR/tests" -name '*.rxt' -print0 \
    | xargs -0 grep -h '^pattern ' \
    | sed 's/^pattern //' > "$RXTPAT"

# The reject table's rows are `reject '<pat>' ...`, `accept '<pat>' ...` and
# `reject_gated <features> '<pat>' ...`. shlex parses the shell quoting rather
# than guessing at it; a row it cannot parse is SKIPPED and counted, never
# silently mangled into a different pattern.
python3 - "$ROOT_DIR/tests/reject/run_reject_tests.sh" "$REJPAT" <<'PY'
import shlex, sys
src, out = sys.argv[1], sys.argv[2]
pats, skipped = [], 0
# Rows may be CONTINUED with a trailing backslash; join them before parsing,
# or shlex chokes on the dangling escape and 11 real reject rows are lost.
raw, joined = open(src, encoding="utf-8", errors="surrogateescape").read(), []
for line in raw.split("\n"):
    if joined and joined[-1].endswith("\\"):
        joined[-1] = joined[-1][:-1] + " " + line.strip()
    else:
        joined.append(line.rstrip())
for line in joined:
    s = line.strip()
    if not (s.startswith("reject ") or s.startswith("accept ")
            or s.startswith("reject_gated ")):
        continue
    try:
        parts = shlex.split(s, comments=True)
    except ValueError:
        skipped += 1; continue
    idx = 2 if parts[0] == "reject_gated" else 1
    if len(parts) > idx:
        pats.append(parts[idx])
    else:
        skipped += 1
open(out, "w", encoding="utf-8", errors="surrogateescape").write(
    "".join(p + "\n" for p in pats))
sys.stderr.write("lookaround-identity: reject table contributed %d patterns "
                 "(%d rows unparseable, skipped)\n" % (len(pats), skipped))
PY

cat "$RXTPAT" "$REJPAT" | LC_ALL=C sort -u > "$PATFILE"
npat=$(grep -c . "$PATFILE" || true)
echo "lookaround-identity: population $npat patterns (.rxt: $(grep -c . "$RXTPAT" || true), reject table: $(grep -c . "$REJPAT" || true), deduped)"

if [ "$npat" -lt 1400 ]; then
    die "population is only $npat patterns (floor 1400) — the gate is not populated, and a zero-difference result over too small a corpus is not the measurement this gate exists to make"
fi

# ---- THE BUCKET SPLIT ([M6.6.2] wave B+C; was the WAVE E HOOK) ------------
# A pattern is lookaround-BEARING if it contains any of the module's spellings.
# It cannot be a substring test: `(?=` inside a character class is three
# literal bytes, `\(?=` is an escaped paren, and `(?<name>` is a NAMED GROUP
# this module does not touch (SR-9 split that byte by TAIL for exactly this
# reason). So the classifier is a grammar-aware scan tracking backslash escapes
# and class depth.
#
# IT FAILS SAFE TOWARD THE BEARING BUCKET, and the CONTROL is what makes that
# safe rather than merely convenient. Over-classifying costs a pattern from the
# identity population — a weaker gate — and would ALSO be caught, loudly,
# because the bearing bucket is asserted to be REFUSED BY THE REFERENCE IN
# FULL: a `(?i)` pattern misfiled as bearing makes `ctl_bad` nonzero and the
# control goes red. UNDER-classifying is the dangerous direction, and it is
# what the scan is written to avoid: a truncated `(?` or `(?<` at end of
# pattern, and any `(*name:` whose name merely CONTAINS "look", go to BEARING
# though no rule above names them.
if [ "$STRICT_ALL" = "1" ]; then
    cp "$PATFILE" "$WORKDIR/sweepfile"
    echo "lookaround-identity: STRICT_ALL=1 — the PURE-REFACTOR mode: the whole population, no bucket split, no stamp strip"
else
python3 "$SCRIPT_DIR/lookaround_classify.py" "$PATFILE" \
        "$WORKDIR/bearing" "$WORKDIR/free" || \
    die "the bucket classifier failed — without a split there is no identity population and no control"

nb=$(grep -c . "$WORKDIR/bearing" || true)
nf=$(grep -c . "$WORKDIR/free" || true)
echo "lookaround-identity: bucket split — $nb lookaround-BEARING, $nf lookaround-FREE"
if [ "$nf" -lt 700 ]; then
    die "only $nf lookaround-FREE patterns (floor 700) — the identity population is too small for a zero-difference result to mean anything"
fi
if [ "$nb" -lt 60 ]; then
    die "only $nb lookaround-BEARING patterns (floor 60) — the POSITIVE CONTROL has no population, so an identical result below would prove nothing"
fi

# ---- THE POSITIVE CONTROL: the reference REFUSES every bearing pattern ----
# "No lookaround exists today, so this module changes nothing for the existing
# population" is TRIVIALLY TRUE and therefore worth nothing (design §9.2). This
# is the half that can actually go red: it proves the reference really is a
# DIFFERENT COMPILER and not a rebuild of this tree compared against itself.
ctl_ok=0; ctl_bad=0
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    if "$REF" --features all -p rx -o - -- "$pat" >/dev/null 2>&1; then
        ctl_bad=$((ctl_bad + 1))
        [ "$ctl_bad" -le 5 ] && echo "  CONTROL: the PRE-MODULE compiler ACCEPTED '$pat'" >&2
    else
        ctl_ok=$((ctl_ok + 1))
    fi
done < "$WORKDIR/bearing"
if [ "$ctl_bad" -eq 0 ] && [ "$ctl_ok" -eq "$nb" ]; then
    ok "positive control: the pre-module reference REFUSES all $ctl_ok lookaround-BEARING patterns — so it really is a different compiler, and the zero-difference result below is a measurement rather than a build compared against itself"
else
    bad "positive control: the pre-module reference COMPILED $ctl_bad of $nb lookaround-bearing patterns. Either the pin is wrong or the classifier OVER-classified (a lookaround-free pattern filed as bearing) — read the accepted patterns above before trusting anything below"
fi
    cp "$WORKDIR/free" "$WORKDIR/sweepfile"
fi

# ---- THE SWEEP -----------------------------------------------------------
python3 - "$PCREC" "$REF" "$WORKDIR/sweepfile" "$WORKDIR" "$STRICT_ALL" "$JOBS" <<'PY'
import subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor

subj, ref, patfile, work, strict, jobs = sys.argv[1:7]
jobs = max(1, int(jobs))
AXES = [("default", []), ("vm", ["--engine=vm"]),
        ("noprefilter", ["-fno-prefilter"]), ("nocaptures", ["--no-captures"])]

pats = [p.rstrip("\n") for p in
        open(patfile, encoding="utf-8", errors="surrogateescape") if p.strip()]
res = open(os.path.join(work, "axis_results"), "w")

def run(binary, args, pat):
    r = subprocess.run([binary, "--features", "all", "-p", "rx"] + args
                       + ["-o", "-", "--", pat],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return r.returncode, r.stdout, r.stderr

# THE D37 FEATURE STAMP, and the strip is ASSERTED rather than trusted (design
# §9.1). In bucket mode this wave legitimately changes what the stamp
# describes, so the three lines are normalised away — but a strip that removed
# four lines, or two, would be absorbing exactly the difference this gate
# exists to report. So `stamp_strip` returns the surviving bytes AND the count
# it removed, every compiled comparison checks that count is 3, and a wrong
# count is its own failure class (`STAMP FILTER`) rather than a quiet pass.
# STRICT_ALL=1 does not strip at all: a pure refactor changes no module and no
# feature, so a stamp difference is a finding there.
STAMP = (b"/* Feature set:", b"#define PCREC_FEATURE_SET",
         b"#define PCREC_FEATURE_MODULES")

def stamp_strip(out):
    keep, removed = [], 0
    for line in out.split(b"\n"):
        if any(line.startswith(m) for m in STAMP):
            removed += 1
        else:
            keep.append(line)
    return b"\n".join(keep), removed

stampbad = 0

fails = 0
for label, args in AXES:
    same = refused_both = 0
    d_status = d_stdout = d_stderr = 0
    log = open(os.path.join(work, "diff." + label), "w",
               encoding="utf-8", errors="surrogateescape")

    def one(pat):
        return pat, run(subj, args, pat), run(ref, args, pat)

    with ThreadPoolExecutor(max_workers=jobs) as ex:
        for pat, (ac, ao, ae), (bc, bo, be) in ex.map(one, pats):
            why = []
            if strict != "1":
                if ao:
                    ao, na_ = stamp_strip(ao)
                    if na_ != 3:
                        stampbad += 1
                        log.write("STAMP FILTER %r :: subject stdout had %d "
                                  "stamp lines, not 3\n" % (pat, na_))
                if bo:
                    bo, nb_ = stamp_strip(bo)
                    if nb_ != 3:
                        stampbad += 1
                        log.write("STAMP FILTER %r :: reference stdout had %d "
                                  "stamp lines, not 3\n" % (pat, nb_))
            if ac != bc: why.append("EXIT(subject=%d reference=%d)" % (ac, bc))
            if ao != bo: why.append("STDOUT(%d vs %d bytes)" % (len(ao), len(bo)))
            # stderr is the refusal text; compared for every pattern under
            # STRICT_ALL, since a refactor may not move a diagnostic either.
            if ae != be: why.append("STDERR")
            if not why:
                if ac != 0: refused_both += 1
                else:       same += 1
                continue
            if "EXIT" in why[0]: d_status += 1
            if any(w.startswith("STDOUT") for w in why): d_stdout += 1
            if "STDERR" in why: d_stderr += 1
            log.write("DIFFERS %r :: %s\n" % (pat, " ".join(why)))
    log.close()

    ndiff = d_status + d_stdout + d_stderr
    print("lookaround-identity[%s]: identical=%d refused-by-both-identically=%d "
          "differing(status=%d stdout=%d stderr=%d)"
          % (label, same, refused_both, d_status, d_stdout, d_stderr))
    res.write("%s\t%d\t%d\t%d\t%d\t%d\n"
              % (label, ndiff, same, refused_both, len(pats), 0))
    if ndiff:
        fails += 1
        print("  [%s] %d comparisons DIFFER between this tree and the "
              "pinned pre-module reference over the lookaround-FREE bucket. "
              "Every one is a finding: this module is not supposed to move a "
              "byte of a pattern that does not use it. (Under STRICT_ALL=1 "
              "the population is the WHOLE corpus and the D37 stamp is not "
              "stripped, so a red there may instead mean the mode does not "
              "fit the tree — see this script's header.)"
              % (label, ndiff), file=sys.stderr)
        with open(os.path.join(work, "diff." + label),
                  encoding="utf-8", errors="surrogateescape") as f:
            for i, line in enumerate(f):
                if i >= 20: print("  ... (more in %s)" % work, file=sys.stderr); break
                print("  " + line.rstrip(), file=sys.stderr)
    else:
        print("  [%s] byte identity under STRICT_ALL=%s: all %d patterns "
              "agree on EXIT STATUS, on stdout (%s) and on stderr, against a "
              "compiler built from the pinned pre-module commit, which shares "
              "no sources with this tree (%d compiled identically, %d refused "
              "identically)"
              % (label, strict, len(pats),
                 "full raw bytes, no stamp strip" if strict == "1"
                 else "past exactly the three D37 stamp lines, asserted",
                 same, refused_both))

res.close()
if stampbad:
    print("  STAMP FILTER: %d stdout captures did not carry exactly three D37 "
          "stamp lines. The strip is asserted, not trusted: a filter that "
          "removes the wrong number of lines is absorbing the difference this "
          "gate exists to report." % stampbad, file=sys.stderr)
sys.exit(1 if (fails or stampbad) else 0)
PY
sweep_rc=$?

# ONE CHECK PER AXIS, counted here rather than inside the sweep so that
# `checks passed` is a count of the claims this gate actually makes.
if [ ! -s "$WORKDIR/axis_results" ]; then
    die "the sweep produced no per-axis results — it died before comparing anything, and a gate that reports nothing must FAIL rather than pass quietly"
fi
nax=0
while IFS=$'\t' read -r label ndiff same refused total _rest; do
    nax=$((nax + 1))
    if [ "$ndiff" -eq 0 ]; then
        if [ "$STRICT_ALL" = "1" ]; then
            ok "[$label] BYTE IDENTITY over all $total patterns (STRICT_ALL=1: the WHOLE population) against the pinned pre-module commit $REFCOMMIT: $same compiled identically, $refused refused identically, 0 differing on exit status, raw stdout (no stamp strip) or stderr"
        else
            ok "[$label] BYTE IDENTITY over all $total lookaround-FREE patterns against the pinned pre-module commit $REFCOMMIT: $same compiled identically, $refused refused identically, 0 differing on exit status, stdout past exactly the three asserted D37 stamp lines, or stderr"
        fi
    else
        if [ "$STRICT_ALL" = "1" ]; then
            bad "[$label] $ndiff of $total comparisons DIFFER from the reference under STRICT_ALL=1. That mode claims the WHOLE population is unmoved, which is FALSE on any tree where a lookaround compiles — check that the mode fits before reading this as a defect"
        else
            bad "[$label] $ndiff of $total lookaround-FREE comparisons DIFFER from the pre-module reference — every one is a finding: this module must not move a byte of a pattern that does not use it"
        fi
    fi
done < "$WORKDIR/axis_results"
if [ "$nax" -ne 4 ]; then
    bad "the sweep reported $nax axes, not the 4 ASK-4 requires (default, --engine=vm, -fno-prefilter, --no-captures) — a missing axis is a missing claim, not a pass"
fi
[ "$sweep_rc" -eq 0 ] || [ "$fail" -ne 0 ] || bad "the sweep exited $sweep_rc but reported no differing axis — treat as a failure rather than a pass"

finish
