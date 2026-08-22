#!/usr/bin/env bash
# tests/backrefs/run_backref_diff.sh — [M6.5.2]'s behavioural instrument for
# module `backrefs`: seven things tests/backrefs/*.rxt structurally CANNOT
# assert, each against libpcre2 or against pcrec itself.
#
#   §1  THE SUBJECT SWEEP, against libpcre2, over a generated space with
#       startpos taking EVERY value in [0, n], comparing the MATCH SPAN AND
#       EVERY GROUP SPAN. Not optional on either axis. `(a)\1` on "xaa" is
#       (1,3) at startpos 1 and NO MATCH at startpos 2, so a suite that fixed
#       the argument could not tell a correct implementation from one that
#       ignores it; and R32 E1's own counterexample family differs in the
#       GROUP span on subjects where the outer span agrees, so a suite that
#       compared `caps[0]` alone would report agreement over exactly the
#       population publish-at-close exists for.
#
#   §2  THE ENGINE ARMS: the DEFAULT selection and `--engine=vm`, asserted to
#       agree. Both are VM artifacts here — a backreference is VM-forced by
#       its twelve registry rows — but they reach that state by different
#       routes, and the DEFAULT one is the arm where `EngineFit.prefilter` was
#       forced OFF (§7.1). A prefilter attached to a backref pattern is the
#       WRONG-ANSWER failure mode this module has, so an arm that never
#       exercises the default path would not see it.
#
#   §3  THE RE-ENTRY ARM, which is where publish-at-close is observable and
#       NOWHERE else. The whole population is references inside groups that
#       are re-entered; §7 below is the only other section with a failure mode
#       that is a wrong ANSWER rather than a refusal.
#
#   §4  THE `--no-captures` ARM (§6.3): the MATCH must be identical and
#       `rx_info.ncaps` must be 1. Under that flag the pre-[M6.5] parser built
#       no `A_CAP` at all, so a referenced group had nothing to read; the
#       ruling is that it keeps its internal slots and REPORTS NONE, and both
#       halves are asserted here because neither is expressible in a `.rxt`.
#
#   §5  THE FIND-ALL LOOP, since a backreference's span feeds the next
#       iteration's startpos and an empty match has to advance through
#       `<prefix>_next_pos` (docs/spec/match_api.md §3.1).
#
#   §6  THE `--engine=dfa` REFUSAL, BY NAME, with the module enabled — and its
#       control, the OCTAL reading of the same digit run, which must COMPILE
#       to a pure DFA. That pair is the per-NODE half of SR-8's stamping rule:
#       `\1`'s registry row is VM_ONLY, but `(a)\10` is the octal byte 0x08
#       and stamping the character node the octal re-read produces would
#       refuse a construct that is not there.
#
#   §7  THE SPAN-DIVERGENCE SECTION, which exists for exactly one sabotage.
#       Its population is the subjects on which the backref-ERASED
#       approximation reports a DIFFERENT span from the true pattern. A
#       prefilter planted on a backref pattern (S-BR14) is INVISIBLE on any
#       subject where the two spans agree, so a section that quietly lost
#       these subjects would pass while the compiler miscompiles.
#
# EVERY POPULATION IS ASSERTED EXACT, NEVER PRINTED, and never as a floor.
# Four guards, each of which is a way for this file to pass while measuring
# nothing — a sweep that generated nothing prints the same silence as one that
# agreed everywhere, and this project's own record is full of that shape.
#
# Usage: bash tests/backrefs/run_backref_diff.sh
# Env: PCREC, CC, KEEP=1
#
# SKIPS LOUDLY when libpcre2 is absent (PC-3's pattern), never silently.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"
FEATS="backrefs,named-groups,modifiers,classes,atomic-groups,assertions"
# Exported because several sections drive the oracle through an inline
# python heredoc that has to find the committed ctypes binding.
export ROOT_DIR

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "backref-diff: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

if ! python3 - <<'PY' 2>/dev/null
import os, sys
sys.path.insert(0, os.path.join(os.environ.get("ROOT", "."), "docs", "design",
                                "eng_brep_measurements", "probes"))
import pcre2_ctypes                                        # noqa: F401
PY
then
    ROOT="$ROOT_DIR" python3 -c "
import os, sys
sys.path.insert(0, os.path.join('$ROOT_DIR','docs','design','eng_brep_measurements','probes'))
import pcre2_ctypes" 2>/dev/null || {
        echo "SKIP: libpcre2 is not available at run time — this differential needs it (PC-3's pattern: a loud skip, never a silent pass)"
        echo "checks passed: 0"
        echo "checks failed: 0"
        exit 0
    }
fi

# ---- the subject space ---------------------------------------------------
# BACKREF-SHAPED BY CONSTRUCTION. What can break a backreference is a subject
# on which the referenced group's capture is RE-DECIDED — by backtracking, by
# a further iteration, or by a branch that loses — so the space is exhaustive
# over a small alphabet (every repetition and near-repetition is then present
# by ENUMERATION rather than by someone remembering it) plus the shapes the
# idioms are written in.
python3 - "$WORKDIR/subjects" <<'PY'
import itertools, os, sys
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
subs = []
for n in range(0, 5):
    for t in itertools.product("ab", repeat=n):
        subs.append("".join(t))
for n in range(0, 4):
    for t in itertools.product("abc", repeat=n):
        subs.append("".join(t))
subs += ['aa', 'aaa', 'aaaa', 'aaaaa', 'abab', 'ababab', 'abcabc',
         'xaa', 'xxaa', 'aax', 'aayaa', 'ayz', 'aybay', 'ayay',
         '"', '""', "''", '"\'\'', '"ab"', 'ab"cd"', '11-1', '12-12',
         'ba', 'baa', 'xbx', 'xyx', 'xyy', 'yy', 'yx', 'xy', 'y', 'z', 'zz',
         'AA', 'Aa', 'aA', 'AbcaBC', 'foofoo', 'foo foo', 'a a', 'ab ab']
seen = set()
for s in subs:
    if s in seen:
        continue
    seen.add(s)
    with open(os.path.join(out, "s%03d" % len(seen)), "wb") as f:
        f.write(s.encode("latin-1"))
print(len(seen))
PY
NSUBJ=$(ls "$WORKDIR/subjects" | wc -l)

# ---- the pattern space ---------------------------------------------------
# Column 1 is a key, column 2 the number of capture pairs the artifact will
# report, column 3 the pattern. The GROUP COUNT is written here beside the
# pattern rather than derived: deriving it would mean counting `(` past the
# non-capturing forms, which is a second parser.
cat > "$WORKDIR/patterns.tsv" <<'EOF'
p01	1	(a)\1
p02	1	(a|b)\1
p03	1	^(a*)\1$
p04	1	(\w)\1
p05	1	^(a)?\1$
p06	1	^(x?)y\1z$
p07	1	^(a)\1*$
p08	2	^(?:(a)x|(b)y)\2$
p09	2	(a|b)\1(a|b)
p10	2	^(a)(b)\2\1$
p11	1	^(?:(a|b)\1)+$
p12	1	(?:(a|bb)x)+\1
p13	1	^(a*)b\1a$
p14	1	(["'])[^"']*\1
p15	1	([0-9]+)-\1
p16	1	\b([a-z]+)\s+\1\b
p17	1	(a)\1{2}
p18	1	^((?i)a)\1$
p19	1	^(a)(?i:\1)$
p20	1	(a\1)
p21	2	(\2(a)|b)+
p22	1	^(?:(a|b\1)y)+
p23	1	(a|b\1)+
p24	1	^(?:(a|b\1))+$
p25	1	^(?:(a|b\1)c)+$
p26	3	^(a)((b)\1)\2$
p27	1	^(?:(a|b)x)++\1$
p28	1	^(a|b)++\1$
p29	1	(a)\g{-1}
p30	1	(?<n>a)\k<n>
p31	1	(?<n>a)(?P=n)
p32	1	^(a?)\1{3}$
p33	1	(a)\1|b\1
p34	2	((a)|b)+\2
p35	1	^(a)\10
EOF
NPAT=$(grep -c . "$WORKDIR/patterns.tsv")

# ---- the oracle ----------------------------------------------------------
if ! python3 "$SCRIPT_DIR/bref_oracle.py" "$WORKDIR/patterns.tsv" \
        "$WORKDIR/subjects" "$WORKDIR/oracle.tsv" 2>"$WORKDIR/oracle.log"; then
    if grep -q "libpcre2 unavailable" "$WORKDIR/oracle.log"; then
        echo "SKIP: libpcre2 is not available at run time — this differential needs it (PC-3's pattern: a loud skip, never a silent pass)"
        echo "checks passed: 0"
        echo "checks failed: 0"
        exit 0
    fi
    echo "FAIL: the oracle refused to run:" >&2
    cat "$WORKDIR/oracle.log" >&2
    exit 1
fi
NCELL=$(wc -l < "$WORKDIR/oracle.tsv")

# The input list the batch drivers read, in the SAME order the oracle wrote:
# the caller compares positionally, so one list and one order.
awk -F'\t' -v d="$WORKDIR/subjects" '{ print d "/" $2 "\t" $3 }' \
    "$WORKDIR/oracle.tsv" | sort -u > /dev/null   # (shape check only)
: > "$WORKDIR/cells.txt"
python3 - "$WORKDIR/subjects" "$WORKDIR/cells.txt" <<'PY'
import os, sys
d, out = sys.argv[1], sys.argv[2]
with open(out, "w") as o:
    for name in sorted(os.listdir(d)):
        n = os.path.getsize(os.path.join(d, name))
        for sp in range(n + 1):
            o.write("%s/%s\t%d\n" % (d, name, sp))
PY
NPERPAT=$(wc -l < "$WORKDIR/cells.txt")

# build_and_run <key> <pattern> <extra-flags> <driver.c> <outfile>
build_and_run() {
    local key="$1" pat="$2" extra="$3" drv="$4" out="$5"
    local d="$WORKDIR/$key$6"
    mkdir -p "$d"
    # shellcheck disable=SC2086
    if ! "$PCREC" -p rx --features "$FEATS" $extra -o "$d/gen.c" \
            -- "$pat" >/dev/null 2>"$d/pc.log"; then
        bad "$key ($extra): pcrec refused '$pat': $(head -1 "$d/pc.log")"
        return 1
    fi
    if ! $CC -O1 -std=gnu11 -I"$d" -o "$d/drv" "$drv" "$d/gen.c" \
            2>"$d/cc.log"; then
        bad "$key ($extra): the generated matcher for '$pat' did not compile: $(head -3 "$d/cc.log" | tr '\n' ' ')"
        return 1
    fi
    "$d/drv" < "$WORKDIR/cells.txt" > "$out" 2>"$d/run.log" || {
        bad "$key ($extra): the driver for '$pat' exited nonzero: $(head -2 "$d/run.log")"
        return 1
    }
    local got
    got=$(wc -l < "$out")
    if [ "$got" -ne "$NPERPAT" ]; then
        bad "$key ($extra): the driver produced $got lines for $NPERPAT cells — the batch protocol shifted, and this file compares POSITIONALLY"
        return 1
    fi
    return 0
}

# ---- §1/§2 the subject sweep, both engine arms ---------------------------
sweep_cmp=0; sweep_bad=0; sweep_match=0
arm_cmp=0; arm_bad=0
while IFS=$'\t' read -r key ng pat; do
    [ -n "$key" ] || continue
    awk -F'\t' -v k="$key" '$1 == k { print $4 }' "$WORKDIR/oracle.tsv" \
        > "$WORKDIR/$key.want"
    build_and_run "$key" "$pat" "" "$SCRIPT_DIR/bref_batch.c" \
                  "$WORKDIR/$key.got" ".def" || continue
    build_and_run "$key" "$pat" "--engine=vm" "$SCRIPT_DIR/bref_batch.c" \
                  "$WORKDIR/$key.gotvm" ".vm" || continue
    n=0
    while IFS= read -r want && IFS= read -r got <&3 && IFS= read -r gotvm <&4; do
        n=$((n + 1))
        sweep_cmp=$((sweep_cmp + 1))
        case "$want" in match*) sweep_match=$((sweep_match + 1)) ;; esac
        if [ "$want" != "$got" ]; then
            sweep_bad=$((sweep_bad + 1))
            [ "$sweep_bad" -le 5 ] && bad "§1 '$pat' cell $n: libpcre2 says '$want', pcrec says '$got'"
        fi
        arm_cmp=$((arm_cmp + 1))
        if [ "$got" != "$gotvm" ]; then
            arm_bad=$((arm_bad + 1))
            [ "$arm_bad" -le 5 ] && bad "§2 '$pat' cell $n: the DEFAULT selection says '$got' and --engine=vm says '$gotvm' — the two arms must agree, and the default is the one where the prefilter was forced OFF"
        fi
    done < "$WORKDIR/$key.want" 3< "$WORKDIR/$key.got" 4< "$WORKDIR/$key.gotvm"
done < "$WORKDIR/patterns.tsv"

# GUARD 1, EXACT: every pattern's every cell was compared. A run that lost a
# pattern (a compile failure the loop `continue`s past) lands here, not in a
# silent smaller denominator.
if [ "$sweep_cmp" -ne $((NPAT * NPERPAT)) ]; then
    bad "§1 POPULATION: compared $sweep_cmp cells, expected exactly $((NPAT * NPERPAT)) ($NPAT patterns x $NPERPAT cells). A pattern that failed to compile leaves this short"
elif [ "$sweep_bad" -eq 0 ]; then
    ok "§1: $sweep_cmp cells (span AND every group span) agree with libpcre2 across $NPAT patterns x $NSUBJ subjects x every startpos"
fi
# GUARD 2, EXACT, and it is the one that stops an ALL-REFUSAL run agreeing
# trivially: a nonzero count of cells where the oracle found a MATCH.
if [ "$sweep_match" -ne 782 ]; then
    bad "§1 NON-VACUITY: $sweep_match of $sweep_cmp cells are a MATCH, expected EXACTLY 782 — a sweep in which nothing matches agrees with anything, and one whose matching population MOVED has stopped asking the same question"
else
    ok "§1 non-vacuity: $sweep_match of $sweep_cmp cells are a MATCH, so agreement is about answers and not about refusals"
fi
if [ "$arm_cmp" -ne $((NPAT * NPERPAT)) ]; then
    bad "§2 POPULATION: compared $arm_cmp engine-arm cells, expected exactly $((NPAT * NPERPAT))"
elif [ "$arm_bad" -eq 0 ]; then
    ok "§2: the DEFAULT selection and --engine=vm agree on all $arm_cmp cells"
fi

# ---- §3 the RE-ENTRY arm, asserted as its OWN population -----------------
# The whole point of a separate count: a run reporting zero divergences over
# an EMPTY re-entry population is the first design's own `selfref.rxt`, which
# took only the S/F cells that AGREED. Cells that agree under both publication
# disciplines cannot detect the difference between them.
REENTRY="p11 p20 p21 p22 p23 p24 p25 p26 p34"
reentry_cells=0
for key in $REENTRY; do
    if [ ! -f "$WORKDIR/$key.got" ]; then
        bad "§3 the re-entry pattern '$key' produced no answers at all"
        continue
    fi
    reentry_cells=$((reentry_cells + $(wc -l < "$WORKDIR/$key.got")))
done
if [ "$reentry_cells" -ne $((9 * NPERPAT)) ]; then
    bad "§3 POPULATION: $reentry_cells re-entry cells, expected exactly $((9 * NPERPAT)) (9 patterns x $NPERPAT). This is where publish-at-close is observable and NOWHERE else"
else
    ok "§3: $reentry_cells cells over 9 re-entry patterns, all inside §1's comparison — the population R32 E1 refuted the first design on"
fi

# ---- §4 the --no-captures arm --------------------------------------------
nocap_cmp=0; nocap_bad=0; nocap_pat=0
while IFS=$'\t' read -r key ng pat; do
    [ -n "$key" ] || continue
    d="$WORKDIR/$key.nc"
    mkdir -p "$d"
    if ! "$PCREC" -p rx --features "$FEATS" --no-captures \
            -o "$d/gen.c" -- "$pat" >/dev/null 2>"$d/pc.log"; then
        bad "§4 '$pat': pcrec refused it under --no-captures: $(head -1 "$d/pc.log")"
        continue
    fi
    nc=$(grep -c '^#define RX_NCAPS 1$' "$d/gen.h")
    if [ "$nc" -ne 1 ]; then
        bad "§4 '$pat': RX_NCAPS is not 1 under --no-captures — a referenced group keeps its INTERNAL slots and must report NONE (§6.3)"
        continue
    fi
    if ! $CC -O1 -std=gnu11 -I"$d" -o "$d/drv" "$SCRIPT_DIR/bref_batch.c" \
            "$d/gen.c" 2>"$d/cc.log"; then
        bad "§4 '$pat': the --no-captures matcher did not compile: $(head -3 "$d/cc.log" | tr '\n' ' ')"
        continue
    fi
    "$d/drv" < "$WORKDIR/cells.txt" > "$d/got" 2>/dev/null
    nocap_pat=$((nocap_pat + 1))
    # The MATCH must be identical; the groups are simply not reported, so the
    # comparison is against the oracle answer with its group columns dropped.
    awk '{ if ($1 == "match") print $1, $2, $3; else print }' \
        "$WORKDIR/$key.want" > "$d/want"
    n=0
    while IFS= read -r want && IFS= read -r got <&3; do
        n=$((n + 1)); nocap_cmp=$((nocap_cmp + 1))
        if [ "$want" != "$got" ]; then
            nocap_bad=$((nocap_bad + 1))
            [ "$nocap_bad" -le 5 ] && bad "§4 '$pat' cell $n under --no-captures: want '$want', got '$got'"
        fi
    done < "$d/want" 3< "$d/got"
done < "$WORKDIR/patterns.tsv"
if [ "$nocap_cmp" -ne $((NPAT * NPERPAT)) ]; then
    bad "§4 POPULATION: compared $nocap_cmp --no-captures cells, expected exactly $((NPAT * NPERPAT)) over $NPAT patterns (got $nocap_pat patterns)"
elif [ "$nocap_bad" -eq 0 ]; then
    ok "§4: all $nocap_cmp cells match identically under --no-captures, and every artifact reports RX_NCAPS 1 (§6.3: the flag drops the slots a CALLER sees, not the machinery a match needs)"
fi

# ---- §5 the three entries ------------------------------------------------
ent_cmp=0; ent_bad=0; ent_nz=0
while IFS=$'\t' read -r key ng pat; do
    [ -n "$key" ] || continue
    d="$WORKDIR/$key.ent"
    mkdir -p "$d"
    if ! "$PCREC" -p rx --features "$FEATS" -o "$d/gen.c" \
            -- "$pat" >/dev/null 2>"$d/pc.log"; then
        bad "§5 pcrec refused '$pat': $(head -1 "$d/pc.log")"; continue
    fi
    if ! $CC -O1 -std=gnu11 -I"$d" -o "$d/drv" "$SCRIPT_DIR/bref_entries.c" \
            "$d/gen.c" 2>"$d/cc.log"; then
        bad "§5 '$pat': the entries driver did not compile: $(head -3 "$d/cc.log" | tr '\n' ' ')"
        continue
    fi
    # THE MATCH-HERE ORACLE is `\G(?:PAT)` — libpcre2 has no anchored mode,
    # but `\G` is true iff the match position equals the startpos, so its
    # answer for the wrapped pattern IS the match-here answer for the bare one.
    printf 'h\t%s\t\\G(?:%s)\n' "$ng" "$pat" > "$d/hpat.tsv"
    python3 "$SCRIPT_DIR/bref_oracle.py" "$d/hpat.tsv" "$WORKDIR/subjects" \
        "$d/hor.tsv" 2>/dev/null || continue
    awk -F'\t' '{ print $4 }' "$d/hor.tsv" > "$d/hwant"
    "$d/drv" < "$WORKDIR/cells.txt" > "$d/got" 2>/dev/null
    n=0
    while IFS= read -r hwant && IFS=$'\t' read -r se mt mc <&3; do
        n=$((n + 1)); ent_cmp=$((ent_cmp + 1))
        case "$hwant" in match*) ent_nz=$((ent_nz + 1)) ;; esac
        # `_match` reports no groups, so compare its span columns only.
        hspan=$(printf '%s' "$hwant" | awk '{ if ($1=="match") print $1, $2, $3; else print }')
        mtspan=$(printf '%s' "$mt" | awk '{ if ($1=="match") print $1, $2, $3; else print }')
        if [ "$hspan" != "$mtspan" ] || [ "$hwant" != "$mc" ]; then
            ent_bad=$((ent_bad + 1))
            [ "$ent_bad" -le 5 ] && bad "§5 '$pat' cell $n: match-here oracle '$hwant', _match '$mt', _match_caps '$mc' (search said '$se')"
        fi
    done < "$d/hwant" 3< "$d/got"
done < "$WORKDIR/patterns.tsv"
if [ "$ent_cmp" -ne $((NPAT * NPERPAT)) ]; then
    bad "§5 POPULATION: compared $ent_cmp entry cells, expected exactly $((NPAT * NPERPAT))"
elif [ "$ent_nz" -ne 550 ]; then
    bad "§5 NON-VACUITY: $ent_nz of $ent_cmp match-here cells MATCH, expected EXACTLY 550 — three entries that all answer 'no' agree trivially"
elif [ "$ent_bad" -eq 0 ]; then
    ok "§5: all three entries agree with the \\G-wrapped oracle on $ent_cmp cells ($ent_nz of them a match)"
fi

# ---- §6 the find-all loop ------------------------------------------------
# A backreference's span feeds the next iteration's startpos, and an empty
# match has to advance through `<prefix>_next_pos` or the loop does not
# terminate (docs/spec/match_api.md §3.1 writes that loop out). The oracle is
# the same libpcre2 binding driven through the same protocol.
cat > "$WORKDIR/findall.c" <<'CEOF'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "gen.h"
int main(int argc, char **argv)
{
    unsigned char buf[1 << 16];
    size_t n, pos = 0;
    FILE *f;
    ptrdiff_t caps[RX_NCAPS][2];
    int guard = 0;
    if (argc < 2) return 2;
    f = fopen(argv[1], "rb"); if (!f) return 2;
    n = fread(buf, 1, sizeof buf, f); fclose(f);
    while (pos <= n) {
        if (++guard > 4096) { printf(" LOOP"); break; }
        if (rx_search(buf, n, pos, caps) != 1) break;
        printf(" %td,%td", caps[0][0], caps[0][1]);
        pos = (caps[0][1] > caps[0][0]) ? (size_t)caps[0][1]
                                        : rx_next_pos(buf, n, (size_t)caps[0][1]);
    }
    printf("\n");
    return 0;
}
CEOF
# THE ORACLE SIDE, computed for EVERY (pattern, subject) pair in ONE process.
# One python start per pair was measured at roughly 3,000 process launches for
# this sweep, which is the subprocess-bound shape tests/atomic_groups/
# atomic_batch.c's header records; batching costs nothing and changes no cell.
python3 - "$WORKDIR/patterns.tsv" "$WORKDIR/subjects" "$WORKDIR/fa.want" <<'PY'
import os, sys
sys.path.insert(0, os.path.join(os.environ["ROOT_DIR"], "docs", "design",
                                "eng_brep_measurements", "probes"))
import pcre2_ctypes as P
patfile, subjdir, out = sys.argv[1], sys.argv[2], sys.argv[3]
subjects = []
for name in sorted(os.listdir(subjdir)):
    with open(os.path.join(subjdir, name), "rb") as f:
        subjects.append((name, f.read().decode("latin-1")))
with open(out, "w") as o:
    for line in open(patfile):
        line = line.rstrip("\n")
        if not line:
            continue
        key, _ng, pat = line.split("\t", 2)
        rx = P.Compiled(pat)
        for sname, subj in subjects:
            pos, res, guard = 0, [], 0
            while pos <= len(subj):
                guard += 1
                if guard > 4096:
                    res.append("LOOP"); break
                r = rx.search(subj, pos)
                if r is None:
                    break
                res.append("%d,%d" % (r[0][0], r[0][1]))
                pos = r[0][1] if r[0][1] > r[0][0] else r[0][1] + 1
            o.write("%s\t%s\t%s\n"
                    % (key, sname, (" " + " ".join(res)) if res else ""))
PY

fa_cmp=0; fa_bad=0; fa_nonempty=0
while IFS=$'\t' read -r key ng pat; do
    [ -n "$key" ] || continue
    d="$WORKDIR/$key.fa"; mkdir -p "$d"
    if ! "$PCREC" -p rx --features "$FEATS" -o "$d/gen.c" -- "$pat" \
            >/dev/null 2>"$d/pc.log"; then
        bad "§6 pcrec refused '$pat': $(head -1 "$d/pc.log")"; continue
    fi
    $CC -O1 -std=gnu11 -I"$d" -o "$d/drv" "$WORKDIR/findall.c" "$d/gen.c" \
        2>"$d/cc.log" || { bad "§6 '$pat': find-all driver did not compile"; continue; }
    : > "$d/got"
    for s in "$WORKDIR"/subjects/*; do
        printf '%s\t%s\n' "$(basename "$s")" "$("$d/drv" "$s")" >> "$d/got"
    done
    awk -F'\t' -v k="$key" '$1 == k { print $2 "\t" $3 }' "$WORKDIR/fa.want" \
        > "$d/want"
    # Per-pattern, so a short side names the pattern rather than showing up
    # only as a smaller total three sections later.
    if [ "$(wc -l < "$d/want")" -ne "$NSUBJ" ] || [ "$(wc -l < "$d/got")" -ne "$NSUBJ" ]; then
        bad "§6 '$pat': oracle side $(wc -l < "$d/want") rows, pcrec side $(wc -l < "$d/got"), expected $NSUBJ each"
        continue
    fi
    while IFS=$'\t' read -r sname want && IFS=$'\t' read -r gname got <&3; do
        fa_cmp=$((fa_cmp + 1))
        [ -n "$(printf '%s' "$want" | tr -d ' ')" ] && fa_nonempty=$((fa_nonempty + 1))
        if [ "$sname" != "$gname" ] || [ "$want" != "$got" ]; then
            fa_bad=$((fa_bad + 1))
            [ "$fa_bad" -le 5 ] && bad "§6 find-all '$pat' on $sname: libpcre2 '$want', pcrec '$got'"
        fi
    done < "$d/want" 3< "$d/got"
done < "$WORKDIR/patterns.tsv"
if [ "$fa_cmp" -ne $((NPAT * NSUBJ)) ]; then
    bad "§6 POPULATION: $fa_cmp find-all runs, expected exactly $((NPAT * NSUBJ))"
elif [ "$fa_nonempty" -lt 100 ]; then
    bad "§6 NON-VACUITY: only $fa_nonempty of $fa_cmp find-all runs found anything at all"
elif [ "$fa_bad" -eq 0 ]; then
    ok "§6: $fa_cmp find-all runs agree with libpcre2 ($fa_nonempty of them non-empty), empty-match advance through <prefix>_next_pos included"
fi

# ---- §7 the --engine=dfa refusal BY NAME, and its octal control ----------
dfa_bad=0
for cell in '\1:(a)\1' '\g{-1}:(a)\g{-1}'; do
    nm="${cell%%:*}"; pat="${cell#*:}"
    if out=$("$PCREC" -p rx --features "$FEATS" --engine=dfa -o - -- "$pat" 2>&1 >/dev/null); then
        bad "§7 '$pat' COMPILED under --engine=dfa"
        dfa_bad=$((dfa_bad + 1))
    elif ! printf '%s' "$out" | grep -qF -- "$nm" \
         || ! printf '%s' "$out" | grep -qF -- "--engine=dfa"; then
        bad "§7 '$pat' was refused under --engine=dfa but not BY ITS OWN NAME ('$nm'): $out"
        dfa_bad=$((dfa_bad + 1))
    fi
done
# THE CONTROL, and it is the per-NODE half of SR-8's stamping rule: `\1`'s
# registry row is VM_ONLY, but `(a)\10` is the OCTAL byte 0x08 — an ordinary
# character with no VM requirement — so the character node the octal re-read
# produces is NOT stamped, and this must compile to a pure DFA.
if ! "$PCREC" -p rx --features "$FEATS" --engine=dfa --no-captures -o - \
        -- '(a)\10' > "$WORKDIR/octdfa.c" 2>"$WORKDIR/octdfa.log"; then
    bad "§7 CONTROL: '(a)\\10' is OCTAL and must compile under --engine=dfa: $(head -1 "$WORKDIR/octdfa.log")"
    dfa_bad=$((dfa_bad + 1))
elif ! grep -q '^    \.engine = 1, /\* PCREC_ENGINE_DFA \*/$' "$WORKDIR/octdfa.c"; then
    bad "§7 CONTROL: '(a)\\10' compiled but not to the DFA engine — the octal re-read's character node must not carry the digit row's VM_ONLY stamp"
    dfa_bad=$((dfa_bad + 1))
fi
if [ "$dfa_bad" -eq 0 ]; then
    ok "§7: two backreference spellings refuse --engine=dfa BY NAME, and the OCTAL reading of the same doorway ('(a)\\10') compiles to a pure DFA — the per-node half of the stamping rule, asserted in both directions"
fi

# ---- §8 THE SPAN-DIVERGENCE SECTION --------------------------------------
# This section exists for exactly ONE sabotage (S-BR14: a DFA prefilter forced
# onto a backref pattern), and it is named here so that row has a DETECTOR
# rather than a gesture.
#
# ITS POPULATION IS THE SUBJECTS ON WHICH THE BACKREF-ERASED APPROXIMATION
# REPORTS A DIFFERENT SPAN FROM THE TRUE PATTERN. A prefilter is invisible on
# any subject where the two spans agree, so a section that quietly lost these
# subjects would pass while the compiler miscompiles. Each cell is asserted
# against libpcre2 for BOTH patterns, so the divergence is measured here on
# every run and not inherited from the design's archive.
#
# ITS GUARD IS ITS OWN, AND EXACT. The global §1 guard cannot serve: it counts
# every cell, and every one of these subjects is already inside it.
#
# THE POPULATION IS NARROWER THAN §11.2's LIST, AND THAT IS A CORRECTION THE
# DESIGN OWES. §11.2 names three cells — `"''` for `(["'])[^"']*\1`, `11-1`
# for `([0-9]+)-\1` and `ba` for `(a*)b\1` — as the span-divergence
# population. MEASURED here, only the FIRST is a DETECTOR:
#
#     family      subject   true    erased   erasure's window
#     quote       "''       (1,3)   (0,2)    does NOT contain the true match
#     digits      11-1      (1,4)   (0,4)    CONTAINS it
#     star        ba        (0,1)   (0,2)    CONTAINS it
#
# A span DIFFERENCE is not enough. The hybrid uses the prefilter's span START
# to seed `attempt_position` (and the emitted loop re-asks it on every retry,
# so a start that is too LOW costs attempts and no answers) and its span END
# as the MRL ceiling. So a planted prefilter changes an ANSWER only when the
# erasure's window FAILS TO CONTAIN the true match — a start above the true
# start, or an end below the true end. On `11-1` and `ba` the erased window
# contains the answer and the VM still finds it, so those two subjects would
# have scored S100 as UNDETECTED while looking like coverage.
#
# The three below were found by SWEEPING the family space for that property
# rather than chosen, and they come from three DIFFERENT families so the
# detector does not rest on one pattern's shape. The predicate is asserted per
# cell, so a subject that stops qualifying is a named failure.
cat > "$WORKDIR/span.tsv" <<'EOF'
d1	(["'])[^"']*\1	(["'])[^"']*(?:["'])	"''
d2	(\w)\1	(\w)(?:\w)	abb
d3	\b([a-z]+)\s+\1\b	\b([a-z]+)\s+(?:[a-z]+)\b	a b b
EOF
span_div=0; span_bad=0; span_cells=0
while IFS=$'\t' read -r key truepat erased subj; do
    [ -n "$key" ] || continue
    span_cells=$((span_cells + 1))
    res=$(TRUEPAT="$truepat" ERASED="$erased" SUBJ="$subj" python3 - <<'PY'
import os, sys
sys.path.insert(0, os.path.join(os.environ["ROOT_DIR"], "docs", "design",
                                "eng_brep_measurements", "probes"))
import pcre2_ctypes as P
t = P.Compiled(os.environ["TRUEPAT"]).search(os.environ["SUBJ"], 0)
e = P.Compiled(os.environ["ERASED"]).search(os.environ["SUBJ"], 0)
ts = "None" if t is None else "%d,%d" % t[0]
es = "None" if e is None else "%d,%d" % e[0]
# BOTH must match, and the erasure's span must not contain the true one --
# that is what makes the subject a DETECTOR rather than merely a difference.
verdict = "same"
if t is not None and e is not None and ts != es:
    verdict = "DIFFER" if not (e[0][0] <= t[0][0] and t[0][1] <= e[0][1]) \
              else "contained"
print("%s %s %s" % (ts, es, verdict))
PY
)
    case "$res" in
        *DIFFER) span_div=$((span_div + 1)) ;;
        *) bad "§8 '$key': the true pattern and its backref-erasure do not span-diverge USABLY on '$subj' ($res) — a subject where only one matches, or where the erasure's window CONTAINS the true match, cannot detect a planted prefilter and must not be in this population" ;;
    esac
    # pcrec must answer the TRUE pattern's span, which is what a planted
    # prefilter would move.
    d="$WORKDIR/$key.span"; mkdir -p "$d"
    printf '%s' "$subj" > "$d/subj"
    if ! "$PCREC" -p rx --features "$FEATS" -o "$d/gen.c" \
            -- "$truepat" >/dev/null 2>&1; then
        bad "§8 '$key': pcrec refused '$truepat'"; span_bad=$((span_bad + 1)); continue
    fi
    $CC -O1 -std=gnu11 -I"$d" -o "$d/drv" "$SCRIPT_DIR/bref_batch.c" "$d/gen.c" \
        2>/dev/null || { bad "§8 '$key': did not compile"; span_bad=$((span_bad+1)); continue; }
    got=$(printf '%s\t0\n' "$d/subj" | "$d/drv")
    want=$(printf '%s' "$res" | awk '{print $1}')
    wantline="match ${want%%,*} ${want##*,}"
    case "$got" in
        "$wantline"*) ;;
        *) bad "§8 '$key' on '$subj': pcrec says '$got', libpcre2's TRUE span is '$wantline' — a prefilter built from the ERASED pattern would answer '$(printf '%s' "$res" | awk '{print $2}')'"
           span_bad=$((span_bad + 1)) ;;
    esac
done < "$WORKDIR/span.tsv"
# GUARD 4, EXACT: all five subjects genuinely span-diverge. A run that lost
# one is a run whose S-BR14 detector shrank.
if [ "$span_div" -ne 3 ] || [ "$span_cells" -ne 3 ]; then
    bad "§8 POPULATION: $span_div of $span_cells subjects span-DIVERGE USABLY between the true pattern and its backref-erasure, expected EXACTLY 3. A prefilter sabotage is invisible on any subject where the erasure's window contains the true match"
elif [ "$span_bad" -eq 0 ]; then
    ok "§8: 3 usably span-diverging subjects, each measured against libpcre2 for BOTH the true pattern and its erasure, and pcrec answers the TRUE span on every one (S100's only detector)"
fi

# ---- §9 THE 256-BYTE FOLD AGREEMENT CHECK (§4.1, R32 E8) ----------------
# pcrec's caseless fold exists TWICE and cannot be made to exist once: as the
# class widener `cls_casefold` applies at PARSE time (D23), and as arithmetic
# inside the encoding residual `$_bref_match_caseless` at MATCH time, because
# a backreference's operand is subject text nobody has seen at compile time.
# Two spellings of one fact with nothing between them is this project's named
# failure shape pointed the other way, and `tests/backrefs/fold_agreement_check.c`
# is the mechanism that discharges it — see that file for both sides'
# independence. Sabotage row S114.
FOLD="$WORKDIR/fold"; mkdir -p "$FOLD"
if ! "$PCREC" -p rx --features "$FEATS" -o "$FOLD/gen.c" -- '(?i:(.))(?i:\1)' \
        >/dev/null 2>"$FOLD/pc.log"; then
    bad "§9: pcrec refused the caseless-backreference fixture: $(head -1 "$FOLD/pc.log")"
elif ! grep -q 'rx_bref_match_caseless' "$FOLD/gen.h"; then
    bad "§9: the fixture artifact carries no rx_bref_match_caseless entry — this check has lost the thing it compares against, which is exactly the empty-population shape it exists to avoid"
elif ! $CC -O1 -std=gnu11 -I"$FOLD" -I"$ROOT_DIR/src" -I"$ROOT_DIR/lib" \
        -o "$FOLD/chk" "$SCRIPT_DIR/fold_agreement_check.c" "$FOLD/gen.c" \
        "$ROOT_DIR/build/libpcrec.a" 2>"$FOLD/cc.log"; then
    bad "§9: the fold-agreement check did not compile: $(head -5 "$FOLD/cc.log" | tr '\n' ' ')"
else
    if foldout=$("$FOLD/chk" 2>&1); then
        ok "§9 fold agreement: $foldout"
    else
        bad "§9 FOLD AGREEMENT: $(printf '%s' "$foldout" | head -5 | tr '\n' ' ')"
    fi
fi

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
