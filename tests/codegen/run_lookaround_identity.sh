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
# NO STAMP STRIP, and that is a rule rather than an omission. `run_atomic_
# identity.sh`'s successors are entitled to normalise the D37 feature stamp
# because a MODULE changes it legitimately. Wave 0 changes no module and no
# feature, so the stamp must be identical too. If a run reports differences
# that are ONLY the stamp, that is a FINDING to take to the manager — not a
# strip to add here.
#
# THE POSITIVE CONTROL IS IN TWO PARTS, because "0 differences" between a tree
# and itself is worth exactly nothing:
#   (a) THE REFERENCE IS ASSERTED PRE-REFACTOR — it must contain no `A_LOOK`
#       (the module has not landed) and no `u.rep` (the union has not landed).
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
# THE BUCKET SPLIT IS WAVE E'S, NOT THIS WAVE'S. When module `lookaround`
# actually lands, this script grows a grammar-aware classifier that splits the
# population into lookaround-BEARING and lookaround-FREE, compares only the
# free bucket for identity, and uses the bearing bucket as the refusal-mismatch
# positive control the way `run_atomic_identity.sh` does. The hook is marked
# `WAVE E HOOK` below. It is deliberately NOT built now: at wave 0 the strict
# claim covers the whole population, and a bucket split introduced early is
# exactly the thing that would quietly absorb a real difference.
#
# Usage: bash tests/codegen/run_lookaround_identity.sh
# Env: PCREC (default <root>/build/pcrec), CC, KEEP=1, SANFLAGS,
#      LOOKAROUND_IDENTITY_REF (the pin), STRICT_ALL (default 1; see above),
#      JOBS (sweep concurrency, default nproc)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
SANFLAGS="${SANFLAGS:-}"
KEEP="${KEEP:-0}"
STRICT_ALL="${STRICT_ALL:-1}"
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

# ---- WAVE E HOOK ---------------------------------------------------------
# When module `lookaround` lands, split "$PATFILE" here into a
# lookaround-BEARING and a lookaround-FREE bucket with a grammar-aware
# classifier (the `(?=` `(?!` `(?<=` `(?<!` `(?*` forms, class- and
# escape-aware, failing SAFE into the BEARING bucket), compare only the FREE
# bucket for byte identity, and assert the BEARING bucket as a refusal-mismatch
# positive control — `run_atomic_identity.sh`'s shape exactly. Until then
# STRICT_ALL below covers the whole population, which is the stronger claim.

# ---- THE SWEEP -----------------------------------------------------------
python3 - "$PCREC" "$REF" "$PATFILE" "$WORKDIR" "$STRICT_ALL" "$JOBS" <<'PY'
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
              "pinned pre-refactor reference. This wave changes no module and "
              "no feature, so EVERY difference is a finding — including one "
              "that is only the D37 feature stamp. Do not add a normaliser; "
              "take it to the manager." % (label, ndiff), file=sys.stderr)
        with open(os.path.join(work, "diff." + label),
                  encoding="utf-8", errors="surrogateescape") as f:
            for i, line in enumerate(f):
                if i >= 20: print("  ... (more in %s)" % work, file=sys.stderr); break
                print("  " + line.rstrip(), file=sys.stderr)
    else:
        print("  [%s] byte identity under STRICT_ALL=%s: all %d patterns "
              "agree on EXIT STATUS, on the full raw stdout (no stamp strip) "
              "and on stderr, against a compiler built from the pinned "
              "pre-refactor commit, which shares no sources with this tree "
              "(%d compiled identically, %d refused identically)"
              % (label, strict, len(pats), same, refused_both))

res.close()
sys.exit(1 if fails else 0)
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
        ok "[$label] BYTE IDENTITY over all $total patterns against the pinned pre-refactor commit $REFCOMMIT: $same compiled identically, $refused refused identically, 0 differing on exit status, raw stdout (no stamp strip) or stderr"
    else
        bad "[$label] $ndiff of $total comparisons DIFFER from the pre-refactor reference — every one is a finding at a pure refactor"
    fi
done < "$WORKDIR/axis_results"
if [ "$nax" -ne 4 ]; then
    bad "the sweep reported $nax axes, not the 4 ASK-4 requires (default, --engine=vm, -fno-prefilter, --no-captures) — a missing axis is a missing claim, not a pass"
fi
[ "$sweep_rc" -eq 0 ] || [ "$fail" -ne 0 ] || bad "the sweep exited $sweep_rc but reported no differing axis — treat as a failure rather than a pass"

finish
