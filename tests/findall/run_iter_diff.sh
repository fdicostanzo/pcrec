#!/usr/bin/env bash
# tests/findall/run_iter_diff.sh -- [FINDALL-NEXT] the find-all iterator's
# ANSWER DIFFERENTIAL against libpcre2's global iteration (findall_iter.md
# §6.7). Every (pattern, encoding) group of a cell file is compiled on each
# engine arm (auto, --engine=vm, and --engine=dfa where the pattern takes the
# DFA), linked with iter_drv.c and libpcre2-8, and run over the group's
# subjects; iter_drv.c prints one verdict per subject (its header).
#
# A DIFF is a failure. GIVEUP (the iterator ended with a code where libpcre2
# answered, its loop agreeing) is counted apart and is a failure unless the
# group's flags carry -futf-check, whose refusal of an ill-formed subject is
# the documented difference (match_api.md §9). SKIP (libpcre2 refused) is
# counted. Two populations are floored, so the check cannot go green on a
# compiler that stopped exercising what it is for: the RETRY cells (subjects
# where the iterator's answer differs from match_api.md §3.1.3's loop, i.e.
# where the NOTEMPTY_ATSTART retry decided a match) and the compiled groups.
# [FINDALL-NEXT] I4: each subject's R= field lists the reach tokens of the I4
# arms (iter_drv.c's header); every token named in REACH_NEED must be reached
# on at least one cell (K35: a sabotage row whose witness never meets its
# condition is UNREACHED, findall_iter_i2.md §5.4), and the counts print.
# A give-up is documented under -futf-check (an ill-formed subject) and under
# --step-budget (the cells that end the iteration mid-batch, S1311's witness).
#
# usage: run_iter_diff.sh [CELLS.tsv ...]   (default: cells.tsv beside this)
#   cells: ENC<TAB>FLAGS<TAB>PATTERN<TAB>SUBJECT, the pattern as written, the
#   subject in the .rxt subject-escape vocabulary (\t \n \r \\ \xNN); '#'
#   lines are comments.
# env: PCREC, CC, GENCFLAGS, PROCS (default 8), MIN_RETRY (default 25),
#   MIN_GROUPS (default 20), ARMS (default "auto vm dfa"), KEEP=1,
#   REACH_NEED (default: every I4 token but kmaxcap/frefused, which only an
#   -DRX_FOREACH_PAIRS=8 build reaches)
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
PROCS="${PROCS:-8}"
MIN_RETRY="${MIN_RETRY:-25}"
MIN_GROUPS="${MIN_GROUPS:-20}"
ARMS="${ARMS:-auto vm dfa}"
REACH_NEED="${REACH_NEED:-n3m4 split gumid done63 vmcaps2 f1 f2 fstopend n0fresh n0bound n0ended fcount2 fcount63 fabi}"
KEEP="${KEEP:-0}"
export WATCHDOG_SECTION="${WATCHDOG_SECTION:-findall}"
# the oracle's flags, once (tests/lib/resolve_pcre2.sh: pkg-config, else a
# bare -lpcre2-8 probe); the workers inherit them
if [ -z "${PCRE2_AVAILABLE:-}" ]; then
    . "$ROOT_DIR/tests/lib/resolve_pcre2.sh"
    export PCRE2_AVAILABLE PCRE2_CFLAGS PCRE2_LIBS
fi

# ---- worker: one group file, every arm -------------------------------------
if [ "${1:-}" = "--group" ]; then
    g="$2"
    d="${g%.cells}"
    mkdir -p "$d.w"
    IFS=$'\t' read -r enc flags pat < "$d.head"
    [ "$flags" = - ] && flags=""
    oenc=byte; [ "$enc" = utf8 ] && oenc=utf
    for arm in $ARMS; do
        a="$d.w/$arm"; mkdir -p "$a"
        eng=""; [ "$arm" = auto ] || eng="--engine=$arm"
        # shellcheck disable=SC2086
        if ! pcrec_run "$PCREC" --features all -p rx -e "$enc" $flags $eng \
                -o "$a/rx.c" --pattern "$pat" 2> "$a/compile.err"; then
            # a DFA arm the pattern cannot take is not a cell; any other
            # refusal is reported with the group, never silently dropped
            if [ "$arm" = dfa ]; then echo "ARMSKIP"; continue; fi
            echo "REFUSED	$arm	$(head -1 "$a/compile.err")"
            continue
        fi
        retry=0
        grep -q '_ITER_RETRY "none"' "$a/rx.c" || retry=1
        # the stamp against the text that does the retry (match_api.md
        # §6.3.13): the VM accept guard, else a retry machine, else neither
        st="$(grep -o '_ITER_RETRY "[a-z-]*"' "$a/rx.c" | head -1 | cut -d'"' -f2)"
        if grep -q 'run->notempty && scan_position' "$a/rx.c"; then want=vm-guard
        elif grep -q '^static.*rx__retry(' "$a/rx.c"; then want=dfa-root
        else want=none; fi
        [ "$st" = "$want" ] || echo "STAMPBAD	$arm	$pat: ITER_RETRY is '$st', the text says '$want'"
        echo "STAMP	$arm	$st"
        # shellcheck disable=SC2086
        if ! gen_cc "findall:$pat:$arm" "$CC" $GENCFLAGS -DPFX=rx -DPFXU=RX \
                -DHDR='"rx.h"' -I"$a" $PCRE2_CFLAGS "$a/rx.c" "$SCRIPT_DIR/iter_drv.c" \
                $PCRE2_LIBS -o "$a/drv" 2> "$a/cc.err"; then
            echo "CCFAIL	$arm	$(head -3 "$a/cc.err" | tr '\n' ' ')"
            continue
        fi
        gen_run "findall:$arm" "$a/drv" "$pat" "$oenc" "$retry" < "$d.subj" \
            > "$a/out" 2> "$a/run.err"
        rc=$?
        if [ "$rc" -ne 0 ]; then echo "RUNFAIL	$arm	rc=$rc $(head -1 "$a/run.err")"; continue; fi
        echo "GROUP	$arm"
        while IFS= read -r line; do
            v="${line%%	*}"
            I="$(printf '%s\n' "$line" | cut -f2)"; L="$(printf '%s\n' "$line" | cut -f4)"
            [ "${I#I=}" != "${L#L=}" ] && echo "RETRYCELL	$arm"
            echo "$v	$arm	$enc	$flags	$pat	$line"
        done < "$a/out"
    done
    exit 0
fi

command -v "$CC" >/dev/null || { echo "FAIL: findall: no C compiler '$CC'" >&2; exit 1; }
if [ "$PCRE2_AVAILABLE" != "1" ]; then
    echo "SKIP: findall: libpcre2-8 not resolvable (tests/lib/resolve_pcre2.sh); the iterator differential has no oracle" >&2
    exit 0
fi

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-findall.XXXXXX")"
cleanup() { if [ "$KEEP" = "1" ]; then echo "findall: KEEP=1, $WORKDIR" >&2; else rm -rf "$WORKDIR"; fi; }
trap cleanup EXIT

[ "$#" -gt 0 ] || set -- "$SCRIPT_DIR/cells.tsv"
# group the cells by (enc, flags, pattern), in first-seen order
python3 -I - "$WORKDIR" "$@" <<'EOF' || { echo "FAIL: findall: cannot read the cell files" >&2; exit 1; }
import sys, os
out = sys.argv[1]
groups = {}
for f in sys.argv[2:]:
    for ln in open(f, encoding="latin-1"):
        ln = ln.rstrip("\n")
        if not ln or ln.startswith("#"):
            continue
        enc, flags, pat, subj = ln.split("\t")
        groups.setdefault((enc, flags, pat), []).append(subj)
for i, ((enc, flags, pat), subjs) in enumerate(groups.items()):
    base = os.path.join(out, "g%05d" % i)
    open(base + ".head", "w", encoding="latin-1").write("%s\t%s\t%s\n" % (enc, flags or "-", pat))
    open(base + ".subj", "w", encoding="latin-1").write("".join(s + "\n" for s in subjs))
    open(base + ".cells", "w").write("")
EOF

ls "$WORKDIR"/g*.cells | xargs -P "$PROCS" -n 1 bash "$0" --group > "$WORKDIR/all.out"

ngroups="$(grep -c '^GROUP' "$WORKDIR/all.out")"
nok="$(grep -c '^OK' "$WORKDIR/all.out")"
ngu="$(grep -c '^GIVEUP' "$WORKDIR/all.out")"
nskip="$(grep -c '^SKIP' "$WORKDIR/all.out")"
nill="$(grep -c "^ILLFORMED" "$WORKDIR/all.out")"
nretry="$(grep -c '^RETRYCELL' "$WORKDIR/all.out")"
nroot="$(grep -c '^STAMP	.*	dfa-root$' "$WORKDIR/all.out")"
nguard="$(grep -c '^STAMP	.*	vm-guard$' "$WORKDIR/all.out")"
fail=0
# both retry forms reached, or the stamp check reads one side of nothing
[ "$nroot" -ge 1 ] && [ "$nguard" -ge 1 ] ||
    { echo "FAIL: findall: $nroot dfa-root and $nguard vm-guard artifacts: a retry form is not reached" >&2; fail=1; }
while IFS= read -r l; do echo "FAIL: findall: $l" >&2; fail=1; done \
    < <(grep -E '^(DIFF|REFUSED|CCFAIL|RUNFAIL|STAMPBAD)' "$WORKDIR/all.out" | head -40)
# a give-up is the documented difference only under -futf-check
while IFS= read -r l; do echo "FAIL: findall: undocumented give-up: $l" >&2; fail=1; done \
    < <(grep '^GIVEUP' "$WORKDIR/all.out" | awk -F'\t' '$4 !~ /-futf-check|--step-budget/' | head -20)
[ "$ngroups" -ge "$MIN_GROUPS" ] || { echo "FAIL: findall: $ngroups compiled groups, floor $MIN_GROUPS" >&2; fail=1; }
[ "$nretry" -ge "$MIN_RETRY" ] || { echo "FAIL: findall: $nretry retry cells, floor $MIN_RETRY: the retry is not being exercised" >&2; fail=1; }
echo "findall: groups=$ngroups ok=$nok giveup=$ngu skip=$nskip illformed=$nill retry-cells=$nretry dfa-root=$nroot vm-guard=$nguard"
reach=""
for t in $REACH_NEED; do
    c="$(grep -E '^(OK|GIVEUP|ILLFORMED|DIFF)	' "$WORKDIR/all.out" | grep -cE "	R=([^	]* )?$t( |	|\$)")"
    reach="$reach $t=$c"
    [ "$c" -ge 1 ] || { echo "FAIL: findall: reach token '$t' met on 0 cells: its sabotage witness is UNREACHED (K35)" >&2; fail=1; }
done
echo "findall: reach$reach"
if [ "$fail" -ne 0 ]; then
    echo "FAIL: findall: the iterator differential is red" >&2
    exit 1
fi
echo "PASS: findall: the iterator answers libpcre2's global iteration"
