#!/usr/bin/env bash
# tests/codegen/run_fallback_table.sh — the FALLBACK TABLES' ARTIFACT-SIDE
# CHECK (docs/design/dec_fallback.md rev 2, §4.2 B0 item 11; §4.3a; §4.4;
# §4.5). Written at B0 (decfbB0b), BEFORE any table exists.
#
# =========================================================================
# INDEPENDENCE (learnings §3: a control must not share a source with what it
# controls). Every expectation below is HAND-WRITTEN from what today's
# compiler (42ab7c25 + B0) was observed to stamp, one witness at a time. The
# script never reads T1-T4, never reads the registry dump (`--list-axes`),
# and never reads a src/ function to learn a value. The ONE other source it
# reads is docs/spec/match_api.md §6.3's hand-written value sets, through the
# registry check's own extractors (tests/lib/spec_extract.sh — one
# implementation, moved there, not copied). Stamps are read from the
# ARTIFACT (the generated C), never from a flag or from the compiler's
# stderr.
#
# =========================================================================
# WHAT THIS DEFENDS. B replaces the fallback ladder's scattered derivations
# (`esel_of`, the PFLW ternary, `cx.size_term_why =`, `VM_PREFILTER_WHY`)
# with tables whose cells spell the stamps. The registry check's two SOURCE
# legs (axes_registry_check.sh: pcrec_engine_sel_name's returns, and the
# `cx.size_term_why =` chain) retire at B5 because from then on the token
# comes from a table cell and the leg's two sides would share the spelling
# function. They may retire ONLY behind the leg in section (b): the stamps
# every witness ACTUALLY EMITS, held to match_api.md's hand-written sets with
# K35 floors. It is green from B0, before anything moves, so a red at B5 is
# B's.
#
# THREE HALVES (§4.2 B0 item 11), plus B3's (e) (B2's (d) retired at B5):
#   (a) SEQUENCES — each witness's expected fallback-row sequence, read from
#       the trace build's `fallback` records (`-DPCREC_CAND_TRACE`, B1): one
#       `row@labels` per arrival, in arrival order, plus the post-row state
#       field a sabotage row targets on three witnesses; and the final
#       `admit`/`attrib`/`gate` record of one witness per row the corpus
#       reaches. Landed at B1 (decfbB1), hand-written from what B1's base
#       was observed to print.
#   (b) THE OBSERVED-STAMP LEG — each of the 8 `RX_ENGINE_SEL` and 7
#       `RX_UNROLL_K_WHY` values is stamped by at least one witness (the K35
#       floor, per value), and the OBSERVED set EQUALS the spec's set (both
#       directions: a value stamped that the spec does not list, and a value
#       the spec lists that no witness stamps).
#   (d) RETIRED at B5 (dec_fallback.md §4.2 B5, A's C5 precedent): B2's
#       both-derivations oracle ran every witness through the trace build in
#       both orders and failed on a `CANDORACLE` line. B3 retired its T1
#       arrival and notes sites, B4 its T2 admit and admit-listing sites, and
#       B5, which deleted the last old derivations (`esel_of`'s ternary, the
#       PFLW ternary, `cx.size_term_why =`, `VM_PREFILTER_WHY`'s SDR test),
#       the rest (`gate`, `stwhy`, `attrib`, `pfwhy`) with the oracle. What
#       holds each token to its old value from B5 on: (a)'s `gate`/`attrib`
#       records (hand-written) and the trace compare against the parent,
#       (b)'s ENGINE_SEL/UNROLL_K_WHY witnesses, (c)'s PFLW/PFWHY texts, and
#       scripts/emit_sweep.py's byte streams against the parent.
#   (e) THE DROP NOTES (B3): each size-cap rung that fires prints its
#       stderr note, in rung order, and a compile that drops nothing prints
#       none. The expected lines are HAND-WRITTEN in full (Frank's
#       2026-09-17 ruling's text), read off stderr, never off the table's
#       `note` cells. Landed at B3 (decfbB3), when the notes became a loop
#       over the fired record.
#   (c) `RX_VM_PREFILTER_LANG_WHY`'s six forms and `RX_VM_PREFILTER_WHY`,
#       each with a witness and its hand-written text. The two forms that
#       carry a BYTE figure (`size cap retry, exact N > M`, `... hybrid N >
#       M`) are compared by SHAPE with the cap literal and `N > M` checked
#       numerically: the byte figure moves on every emitted-text abi event,
#       and a full-text pin would go red on unrelated work. The NFA-state
#       form (`dfa overflow retry, exact nfa N`) is compared in FULL: N is
#       an NFA state count, stable under emitted-text changes.
#
# REFERENCE COMPILERS (built ONCE, here, the way run_size_term.sh builds its
# lowered compilers — source list from tests/lib/lib_srcs.sh, never a glob;
# hard-fail on an empty list). Three, because three witnesses have a natural
# population of ZERO at the shipped limits:
#   lowdfa   -DPCREC_MAX_AUTO_DFA_ELEMS=3000      overflowed-prefilter
#   lowsize  -DPCREC_MAX_VM_EMIT_CODE_BYTES=30000 -DPCREC_MAX_EMIT_BYTES=60000
#            -DPCREC_SIZE_TERM_THRESHOLD=10000    cap-rescue,
#                                                 size-model-declined
#   lowthr   -DPCREC_SIZE_TERM_THRESHOLD=1000     capacity-declined
#
# Usage: bash tests/codegen/run_fallback_table.sh
# Env:   PCREC (default <root>/build/pcrec), CC (tests/lib/cc_resolve.sh),
#        KEEP=1 keeps the workdir.
set -u
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
MATCHAPI="${MATCHAPI:-$ROOT_DIR/docs/spec/match_api.md}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"     # [K37] pcrec_run: every compile bounded
. "$ROOT_DIR/tests/lib/cc_resolve.sh"      # [MACPORT] a real GNU gcc (Apple's bare gcc is clang)
. "$ROOT_DIR/tests/lib/lib_srcs.sh"        # the library's source list
. "$ROOT_DIR/tests/lib/spec_extract.sh"    # the registry check's extractors, ONE implementation
export WATCHDOG_SECTION="fallbacktable"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/fallbacktable.XXXXXX")"
cleanup() { [ -n "${KEEP:-}" ] || rm -rf "$WORK"; }
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# stamp NAME FILE — the artifact's `#define RX_NAME "value"`, quotes stripped;
# empty when the artifact carries no such line. Anchored on the trailing
# space, so `VM_PREFILTER_WHY` never reads `VM_PREFILTER_LANG_WHY`.
stamp() { sed -n "s/^#define RX_$1 \"\(.*\)\"\$/\1/p" "$2" | head -1; }

# --- the reference compilers, built once ------------------------------------
lsrcs=$(pcrec_lib_srcs "$ROOT_DIR" | tr '\n' ' ')
if [ -z "$lsrcs" ]; then
    bad "the library source list is EMPTY: no reference compiler can be built (a glob that found nothing must not read as a pass)"
fi
build_ref() {   # build_ref NAME CFLAGS...  -> $WORK/pcrec_NAME
    local n="$1"; shift
    # shellcheck disable=SC2086
    $CC -O1 -std=gnu11 -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" "$@" \
        -o "$WORK/pcrec_$n" "$ROOT_DIR/cli/main.c" $lsrcs 2>"$WORK/ref_$n.err" \
        || echo "BUILDFAIL" > "$WORK/ref_$n.fail"
}
if [ -n "$lsrcs" ]; then
    build_ref lowdfa  -DPCREC_MAX_AUTO_DFA_ELEMS=3000 &
    build_ref lowsize -DPCREC_MAX_VM_EMIT_CODE_BYTES=30000 -DPCREC_MAX_EMIT_BYTES=60000 \
                      -DPCREC_SIZE_TERM_THRESHOLD=10000 &
    build_ref lowthr  -DPCREC_SIZE_TERM_THRESHOLD=1000 &
    wait
    for n in lowdfa lowsize lowthr; do
        if [ -e "$WORK/ref_$n.fail" ] || [ ! -x "$WORK/pcrec_$n" ]; then
            bad "the $n reference compiler failed to build: $(head -1 "$WORK/ref_$n.err")"
        else
            ok "the $n reference compiler built"
        fi
    done
fi
REF_lowdfa="$WORK/pcrec_lowdfa"; REF_lowsize="$WORK/pcrec_lowsize"; REF_lowthr="$WORK/pcrec_lowthr"

# --- (a)'s TRACE compilers, built once (B1) ----------------------------------
# The same source list and flags as above plus `-DPCREC_CAND_TRACE`, one per
# limit set (a) reads. Kept SEPARATE from the three reference compilers
# above: (b)/(c) read artifacts from untraced builds, so a trace build that
# moved a byte (scripts/emit_sweep.py --trace's own check) could not reach
# their verdicts.
if [ -n "$lsrcs" ]; then
    build_ref trplain   -DPCREC_CAND_TRACE &
    build_ref trlowdfa  -DPCREC_CAND_TRACE -DPCREC_MAX_AUTO_DFA_ELEMS=3000 &
    build_ref trlowsize -DPCREC_CAND_TRACE -DPCREC_MAX_VM_EMIT_CODE_BYTES=30000 \
                        -DPCREC_MAX_EMIT_BYTES=60000 -DPCREC_SIZE_TERM_THRESHOLD=10000 &
    build_ref trlowboth -DPCREC_CAND_TRACE -DPCREC_MAX_VM_EMIT_CODE_BYTES=30000 \
                        -DPCREC_MAX_EMIT_BYTES=60000 -DPCREC_SIZE_TERM_THRESHOLD=10000 \
                        -DPCREC_MAX_AUTO_DFA_ELEMS=3000 &
    wait
    for n in trplain trlowdfa trlowsize trlowboth; do
        if [ -e "$WORK/ref_$n.fail" ] || [ ! -x "$WORK/pcrec_$n" ]; then
            bad "the $n trace compiler failed to build: $(head -1 "$WORK/ref_$n.err")"
        else
            ok "the $n trace compiler built"
        fi
    done
fi
REF_trplain="$WORK/pcrec_trplain"; REF_trlowdfa="$WORK/pcrec_trlowdfa"
REF_trlowsize="$WORK/pcrec_trlowsize"; REF_trlowboth="$WORK/pcrec_trlowboth"

# compile WITNESS_ID COMPILER-KEY PATTERN [args...] — writes $WORK/ID.c; the
# pattern is passed via --pattern (never a positional file operand).
compile() {
    local id="$1" key="$2" pat="$3"; shift 3
    if [ "$key" = default ]; then
        pcrec_run "$PCREC" -p rx --features all "$@" -o "$WORK/$id.c" --pattern "$pat" \
            >/dev/null 2>"$WORK/$id.err"
    else
        local bin="REF_$key"; bin="${!bin}"
        pcrec_run "$bin" -p rx --features all "$@" -o "$WORK/$id.c" --pattern "$pat" \
            >/dev/null 2>"$WORK/$id.err"
    fi
}

# The overflowed-prefilter witness: an unrolled `(?:a|b)` ladder under a
# trailing `*` with 12 explicit copies. Under the shipped limits it is
# `selected`; under lowdfa the auto DFA attempt overflows AND the prefilter
# pair overflows after it. (Spelled out, not `{11}`: a counted repeat takes
# the SEL1 collapse route instead and stamps `collapsed-prefilter`.)
AB12=''; for _i in 1 2 3 4 5 6 7 8 9 10 11 12; do AB12="$AB12(?:a|b)"; done
OVFPF="(x)(?:a|b)*a${AB12#(?:a|b)}"

# =========================================================================
# (a) SEQUENCES — every witness's fallback rows, from the trace build
# =========================================================================
echo "== (a) sequences: each witness's fallback rows, in arrival order (the B1 trace) =="

# trace_sane LABEL RC TRACE-FILE — a trace-build compile must neither print a
# `CANDORACLE` line (one of §1.9's invariants failed: pcrec_fit_invariant_fail)
# nor die by a signal. B2-B4's (d) ran this leg on its own witness set; since
# B5 it rides every (a) compile, the suite's in-tree check of the invariants.
trace_sane() {
    if grep -q '^CANDORACLE' "$3"; then
        bad "$1: $(grep -m1 '^CANDORACLE' "$3" | tr '\t' ' ')"; return 1
    fi
    if [ "$2" -ge 128 ]; then bad "$1: died with rc $2"; return 1; fi
}

# fseq ID TRACE-KEY RC EXPECTED PATTERN [args...]
# EXPECTED is the hand-written `row@labels > row@labels ...` sequence of the
# compile's `CANDTRACE fallback` records ("(none)": no arrival at all), RC
# `ok` or `refused`. A trace compiler that prints NO fallback record on a
# witness expected to arrive is a FAIL like any other mismatch: a record
# site that stopped printing reads as "(none)" and never as a pass.
fseq() {
    local id="$1" key="$2" erc="$3" want="$4" pat="$5"; shift 5
    local bin="REF_$key" rc got
    bin="${!bin}"
    pcrec_run "$bin" -p rx --features all "$@" -o "$WORK/$id.c" --pattern "$pat" \
        >/dev/null 2>"$WORK/$id.trace"
    rc=$?
    trace_sane "sequence $id [$key $* '$pat']" "$rc" "$WORK/$id.trace" || return
    got="$(awk -F'\t' '$1 == "CANDTRACE" && $2 == "fallback" { split($4, w, " ");
            s = s (s == "" ? "" : " > ") w[1] "@" $3 } END { print (s == "" ? "(none)" : s) }' \
            "$WORK/$id.trace")"
    if [ "$erc" = ok ] && [ "$rc" -ne 0 ]; then
        bad "sequence $id [$key $* '$pat']: refused (rc $rc), expected to compile; rows: $got"; return
    elif [ "$erc" = refused ] && [ "$rc" -eq 0 ]; then
        bad "sequence $id [$key $* '$pat']: compiled, expected a refusal; rows: $got"; return
    fi
    [ "$got" = "$want" ] && ok "sequence $id [$key $*]: $want" \
                         || bad "sequence $id [$key $* '$pat']: rows '$got', expected '$want'"
}
# fstate ID N FIELD=VALUE — the N-th fallback record (1-based) of witness ID's
# last fseq run carries the post-row state field FIELD=VALUE.
fstate() {
    local id="$1" n="$2" want="$3" got
    got="$(awk -F'\t' -v n="$n" '$1 == "CANDTRACE" && $2 == "fallback" && ++k == n { print $4 }' \
            "$WORK/$id.trace")"
    case " $got " in
        *" $want "*) ok "sequence $id record $n carries $want" ;;
        *) bad "sequence $id record $n: '$got' does not carry $want" ;;
    esac
}

W_OVF='^(?:(?:a|b)*a(?:a|b){20})?$'          # the DFA overflows, then the prefilter
W_SEL1='(1{0,30}?[^]abc][^abc]){28,30}0+|a'   # the collapsed prefilter survives
W_LOOK='x(?!a)(?!b)(?!c)(?!d)(?!e)(?!f)(?!g)(?!h)(?!i)(?!j)(?!k)(?!l)(?!m)(?!n)(?!o)(?!p)(?!q)'
W_TOWER='(?:(?:(?:(?:(?:(?:a|b){41}){41}){41}){41}){41}){41}'
W_NEST8='((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}'
# [DEC-COLLAPSE-WASTE] (abi 69): a collapse rung is offered only where it can
# help, so W_OVF (nullable, not empty_admits: class (ii)), W_LOOK and OVFPF
# (no counted repeat: class (i)) now go straight to `sel1-drop`. The two
# witnesses below keep the rows a REAL collapse attempt fires: W_LOOKR's
# counted `y{2,3}` makes the collapse a different machine, which still
# overflows on the lookaheads (collapse, then drop); W_OVFNN is W_OVF made
# non-nullable, so its rung is taken under -fno-prefilter too (T2's
# overflow-drop at SEL1 scope, the force_off disjunct).
W_LOOKR="${W_LOOK}y{2,3}"
W_OVFNN='^(?:a|b)*a(?:a|b){20}$'
# T1 rows 3-4 ([SEL-1]), arrival label `overflow`
fseq seq-sel1c    trplain ok 'sel1-collapse@overflow'                          "$W_SEL1"
fstate seq-sel1c 1 'cr=1'
fseq seq-sel1cd   trplain ok 'sel1-collapse@overflow > sel1-drop@overflow'     "$W_LOOKR"
fstate seq-sel1cd 1 'latch=1/0'
fstate seq-sel1cd 2 'cr=0'
fstate seq-sel1cd 2 'latch=1/0'
fseq seq-ovfii    trplain ok 'sel1-drop@overflow'                              "$W_OVF"
fstate seq-ovfii 1 'cr=0'
fstate seq-ovfii 1 'latch=1/0'
fseq seq-look     trplain ok 'sel1-drop@overflow'                              "$W_LOOK"
fseq seq-sel1d    trplain ok 'sel1-drop@overflow'                              "$W_OVF" -fno-prefilter-collapse
fseq seq-fofsel1  trplain ok 'sel1-collapse@overflow'                          "$W_SEL1" --size-cap=refuse
fseq seq-nopfsel1 trplain ok 'sel1-collapse@overflow'                          "$W_OVFNN" -fno-prefilter
fseq seq-ovfpf    trlowdfa ok 'sel1-drop@overflow'                             "$OVFPF"
# T1 rows 6-9 (the size-cap ladder), arrival label `size`
fseq seq-pfcdrop  trplain ok 'drop-prefilter@size'                             '(\p{Xwd})' -e utf8
fstate seq-pfcdrop 1 'restart=1'
# seq-pfdrop holds row 6's deny bit (S648). Since [DEC-COLLAPSE-WASTE]
# `(\p{Xwd})` has no collapsible repeat, so row 6 is not offered with or
# without the bit and the old witness read the same either way (dectri,
# 2026-10-09). `(\p{Xwd}{1,3})` takes prefilter-collapse at shipped limits
# (gate-sizecap below); the bit must keep it to drop-prefilter alone.
fseq seq-pfdrop   trplain ok 'drop-prefilter@size'                             '(\p{Xwd}{1,3})' -e utf8 -fno-prefilter-collapse
fseq seq-pfc      trplain ok 'prefilter-collapse@size'                         '^(\p{Xwd}{1,3})?$' -e utf8 -fprefilter
fseq seq-pfclow   trlowsize ok 'prefilter-collapse@size'                       '(?:a\K){2,}b'
fseq seq-pfcbcat  trlowsize ok 'drop-prefilter@size'                          '(\bcat\b)+' -e utf8
fseq seq-pfcd2    trlowsize ok 'prefilter-collapse@size > drop-prefilter@size' '(\bcat\b){2,}' -e utf8
fstate seq-pfcd2 2 'restart=1'
fseq seq-anch     trplain ok 'drop-anchored@size'                              '\p{L}' -e utf8
fseq seq-premul   trlowboth ok 'drop-anchored@size > drop-premul@size'         '(*UCP)(?i)[\dk]' -e utf8
fseq seq-premuls  trlowsize ok 'drop-anchored@size > drop-premul@size'         '(*UCP)(?i)[\dk]' -e utf8
# T1 row 2 (the size term's trial catch), label `other`
fseq seq-trial    trplain ok 'size-term-trial@other > size-term-trial@other > size-term-trial@other' \
                  "$W_TOWER" --engine=vm
fseq seq-trialref trlowsize refused 'size-term-trial@other > size-term-trial@other > refuse@size' "$W_NEST8"
# T1 row 10 (refuse) under every label it is asked on
fseq seq-refovf   trplain refused 'refuse@overflow'                            '(?:ab){0,16000}' --engine=dfa
fseq seq-refsize  trplain refused 'refuse@size'                                '(\p{Xwd})' -e utf8 --size-cap=refuse
fseq seq-refother trplain refused 'refuse@other'                               '\A*'
fseq seq-refpf    trplain refused 'refuse@other'                               "$W_OVF" -fprefilter
# no arrival at all
fseq seq-none     trplain ok '(none)'                                          '(a)b'
fseq seq-nonevm   trplain ok '(none)'                                          "$W_OVF" --engine=vm

# frec ID TRACE-KEY SLOT WANT PATTERN [args...] — the LAST `SLOT` record of
# the compile (the final attempt's) reads `route|row-field` == WANT. The
# other three slots B4/B5 hold to their parent (`admit` = T2's row and
# verdict, `attrib` = the ENGINE_SEL token and the row whose cell gave it,
# `gate` = T3's row and PFLW), one witness per row the corpus reaches. Since
# B4 (`admit`) and B5 (`attrib`, `gate`) each record prints the WALK's row,
# so these hand-written rows check the walks directly.
frec() {
    local id="$1" key="$2" slot="$3" want="$4" pat="$5"; shift 5
    local bin="REF_$key" got
    bin="${!bin}"
    pcrec_run "$bin" -p rx --features all "$@" -o "$WORK/$id.c" --pattern "$pat" \
        >/dev/null 2>"$WORK/$id.trace"
    trace_sane "record $id [$key $slot $* '$pat']" "$?" "$WORK/$id.trace" || return
    got="$(awk -F'\t' -v s="$slot" '$1 == "CANDTRACE" && $2 == s { x = $3 "|" $4 } END { print x }' \
            "$WORK/$id.trace")"
    [ "$got" = "$want" ] && ok "record $id [$key $slot $*]: $want" \
                         || bad "record $id [$key $slot $* '$pat']: last $slot record '$got', expected '$want'"
}
frec adm-default  trplain admit 'none|default pf=1'            '(a)b'
frec adm-nulex    trplain admit 'none|nullable-exact pf=0'     '(a)*'
# [DEC-VAR-ATTRIB]: `var` is a construct row ahead of the nullability and
# flag rows, so a nullable variable pattern and a -fno-prefilter one take it
# too (until abi 69: `var-nullable`, and `forced-off` under the flag).
frec adm-varnul   trplain admit 'none|var pf=0'                '^${v}$'
frec adm-var      trplain admit 'none|var pf=0'                'a${v}b'
frec adm-varoff   trplain admit 'none|var pf=0'                'a${v}b' -fno-prefilter
frec adm-bref     trplain admit 'none|backref pf=0'            '(a)\1'
frec adm-call     trplain admit 'none|linked-call pf=0'        '(a|b(?1)c)+'
frec adm-nulcol   trplain admit 'sel1|nullable-collapsed pf=0' '(?:ab){0,16000}'
frec adm-ovf      trplain admit 'none|overflow-drop pf=0'      "$W_OVF"
frec adm-ovfsel1  trplain admit 'sel1|overflow-drop pf=0'      "$W_OVFNN" -fno-prefilter
frec adm-fon      trplain admit 'none|forced-on pf=1'          '(a)b' --engine=vm -fprefilter
frec adm-sizedrop trplain admit 'none|size-dropped pf=0'       '(\p{Xwd})' -e utf8
frec adm-sizedcol trlowsize admit 'sizecap|size-dropped pf=0'  '(\bcat\b){2,}' -e utf8
frec adm-fonsc    trplain admit 'sizecap|forced-on pf=1'       '^(\p{Xwd}{1,3})?$' -e utf8 -fprefilter
frec att-forced   trplain attrib '-|forced from=forced'                       '(a)b' --engine=vm
frec att-sel      trplain attrib '-|selected from=none'                       '(a)b'
frec att-dnd      trplain attrib '-|declined-nullable-default from=admit'     '(a)*'
frec att-varnul   trplain attrib '-|selected from=none'                       '^${v}$'
frec att-dn       trplain attrib '-|declined-nullable from=admit'             '(?:ab){0,16000}'
frec att-cpf      trplain attrib '-|collapsed-prefilter from=sel1-collapse'   "$W_SEL1"
frec att-ovfdfa   trplain attrib '-|overflowed-dfa from=sel1-drop'            "$W_OVF"
frec att-ovfpf    trlowdfa attrib '-|overflowed-prefilter from=sel1-drop'     "$OVFPF"
# att-ovfcd/att-scpfd: the giving row is the SECOND fired row (S626). Since
# [DEC-COLLAPSE-WASTE] att-ovfdfa/att-ovfpf fire sel1-drop alone, so the first
# fired row and the giving row coincide there (dectri, 2026-10-09).
frec att-ovfcd    trplain attrib '-|overflowed-dfa from=sel1-drop'            "$W_LOOKR"
frec att-scpfd    trlowsize attrib '-|size-cap-retry from=drop-prefilter'     '(\bcat\b){2,}' -e utf8
frec att-scpfc    trlowsize attrib '-|size-cap-retry from=prefilter-collapse' '(?:a\K){2,}b'
frec att-scanch   trplain attrib '-|size-cap-retry from=drop-anchored'        '\p{L}' -e utf8
frec att-scpf     trplain attrib '-|size-cap-retry from=drop-prefilter'       '(\p{Xwd})' -e utf8
frec gate-sel1    trplain gate 'sel1|rung pflw=sel1'         "$W_SEL1"
frec gate-sizecap trplain gate 'sizecap|rung pflw=sizecap'   '(\p{Xwd}{1,3})' -e utf8
frec gate-forced  trplain gate 'none|forced pflw=forced'     '(x)?a{0,4}\Gb' -fprefilter-collapse
frec gate-nul     trplain gate 'none|nullable pflw=nullable' '^(a{2,9})*$' -fprefilter-collapse
# (gate-nulsel1, T3 `nullable` at SEL1 scope on W_OVF, went with
# [DEC-COLLAPSE-WASTE]: it WAS class (ii), the rung that rebuilt the exact
# machine. T3 `nullable` is reached only under -fprefilter-collapse now.)
frec gate-exact   trplain gate 'none|exact pflw=exact'       '(a){2,3}b'
frec gate-norep   trplain gate 'none|no-rep pflw=no-rep'     '(a)b'

# =========================================================================
# (b) THE OBSERVED-STAMP LEG
# =========================================================================
echo "== (b) observed-stamp leg: every ENGINE_SEL and UNROLL_K_WHY value, stamped by a witness =="

# One line per witness: the stamp it ACTUALLY carried (empty = no such line).
: > "$WORK/obs_sel"; : > "$WORK/obs_why"

# wit ID COMPILER EXPECT_SEL EXPECT_WHY PATTERN [args...]
# EXPECT_* are HAND-WRITTEN per witness ("-" = this witness does not
# constrain that macro, e.g. a witness chosen for the other one). A
# witness's stamps count toward the observed sets whether or not it is
# constrained, but a witness that does not compile, or whose stamp differs
# from its hand-written expectation, is a FAIL (the witness stopped reaching
# its site — [MECH-REACH]).
wit() {
    local id="$1" key="$2" esel="$3" ewhy="$4" pat="$5"; shift 5
    if ! compile "$id" "$key" "$pat" "$@"; then
        bad "witness $id [$key $* '$pat']: the compile refused, so the path was never reached: $(head -1 "$WORK/$id.err")"
        return
    fi
    local gs gw; gs="$(stamp ENGINE_SEL "$WORK/$id.c")"; gw="$(stamp UNROLL_K_WHY "$WORK/$id.c")"
    printf '%s\n' "$gs" >> "$WORK/obs_sel"; printf '%s\n' "$gw" >> "$WORK/obs_why"
    if [ "$esel" != "-" ]; then
        [ "$gs" = "$esel" ] && ok "witness $id [$key $* '$pat']: ENGINE_SEL is '$esel'" \
                            || bad "witness $id [$key $* '$pat']: ENGINE_SEL is '$gs', expected '$esel'"
    fi
    if [ "$ewhy" != "-" ]; then
        [ "$gw" = "$ewhy" ] && ok "witness $id [$key $* '$pat']: UNROLL_K_WHY is '$ewhy'" \
                            || bad "witness $id [$key $* '$pat']: UNROLL_K_WHY is '$gw', expected '$ewhy'"
    fi
}

# NEST8: run_size_term.sh's nested-repeat family, the size term's own witness.
NEST8='((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}'

# ENGINE_SEL, eight values (docs: the same decision as a TOKEN)
wit sel-selected      default 'selected'                  default '(a)b'
wit sel-forced        default 'forced'                    default '(a)b' --engine=vm
wit sel-declnulldef   default 'declined-nullable-default' default '(a)*'
wit sel-ovfdfa        default 'overflowed-dfa'            default '^(?:(?:a|b)*a(?:a|b){20})?$'
wit sel-collapsedpf   default 'collapsed-prefilter'       default '(1{0,30}?[^]abc][^abc]){28,30}0+|a'
wit sel-declnull      default 'declined-nullable'         default '(?:ab){0,16000}'
wit sel-sizecap       default 'size-cap-retry'            default '(\p{Xwd})' -e utf8
wit sel-ovfpf         lowdfa  'overflowed-prefilter'      default "$OVFPF"
# UNROLL_K_WHY, seven values (docs: `<PREFIX>_UNROLL_K_WHY`)
wit why-default       default '-' 'default'               'a(b|c)+d'
wit why-option        default '-' 'option'                'a(b|c)+d' --unroll=4
wit why-denied        default '-' 'denied'                'a(b|c)+d' -fno-size-term
wit why-sizemodel     default '-' 'size-model'            "$NEST8"
wit why-caprescue     lowsize '-' 'cap-rescue'            '(?:a\K){0,10}ab'
wit why-sizemodeldecl lowsize '-' 'size-model-declined'   '(?:a\K){0,10}b'
wit why-capacitydecl  lowthr  '-' 'capacity-declined'     '(((?:a{0,2}b)+c){0,20}d){0,20}e' --engine=vm

# --- the spec's hand-written sets, through the registry's extractors -------
spec_sel="$(extract_md_table_values "$MATCHAPI" "<!-- value-set: RX_ENGINE_SEL -->")"
spec_why="$(extract_md_table_values "$MATCHAPI" "<!-- value-set: RX_UNROLL_K_WHY -->")"

# K35 fail-closed: an extraction that found nothing (or the wrong number)
# must not read as "equal to the empty observation".
nsel=$(printf '%s\n' "$spec_sel" | grep -c .); nwhy=$(printf '%s\n' "$spec_why" | grep -c .)
[ "$nsel" -eq 8 ] && ok "K35: match_api.md's ENGINE_SEL set extracted, $nsel values (expected 8)" \
                  || bad "K35: match_api.md's ENGINE_SEL set has $nsel values, expected 8 (anchor stopped matching, or the spec grew a value: re-derive the witness list)"
[ "$nwhy" -eq 7 ] && ok "K35: match_api.md's UNROLL_K_WHY set extracted, $nwhy values (expected 7)" \
                  || bad "K35: match_api.md's UNROLL_K_WHY set has $nwhy values, expected 7 (anchor stopped matching, or the spec grew a value: re-derive the witness list)"

# floor + equality for one macro. $1 macro, $2 spec set, $3 obs file
check_observed() {
    local macro="$1" spec="$2" obsf="$3" v n
    # floor: every spec value has >= 1 witness that stamped it
    for v in $spec; do
        n=$(grep -cxF -- "$v" "$obsf")
        [ "$n" -ge 1 ] && ok "[$macro] floor: '$v' stamped by $n witness(es)" \
                       || bad "[$macro] floor: NO witness stamps '$v' (the spec lists it; a value nothing reaches is unchecked)"
    done
    # the other direction: every observed non-empty value is in the spec
    for v in $(grep . "$obsf" | sort -u); do
        grep -qxF -- "$v" <<< "$spec" \
            && ok "[$macro] observed '$v' is in match_api.md's set" \
            || bad "[$macro] observed value '$v' is NOT in match_api.md's hand-written set"
    done
}
check_observed RX_ENGINE_SEL    "$spec_sel" "$WORK/obs_sel"
check_observed RX_UNROLL_K_WHY  "$spec_why" "$WORK/obs_why"

# =========================================================================
# (c) RX_VM_PREFILTER_LANG_WHY's six forms and RX_VM_PREFILTER_WHY
# =========================================================================
echo "== (c) RX_VM_PREFILTER_LANG_WHY (six forms) and RX_VM_PREFILTER_WHY =="

# pflw ID FORM-LABEL EXPECTED-FULL-TEXT PATTERN [args]
pflw() {
    local id="$1" label="$2" want="$3" pat="$4"; shift 4
    if ! compile "$id" default "$pat" "$@"; then
        bad "PFLW '$label': the compile of '$pat' refused: $(head -1 "$WORK/$id.err")"; return
    fi
    local got; got="$(stamp VM_PREFILTER_LANG_WHY "$WORK/$id.c")"
    [ "$got" = "$want" ] && ok "PFLW '$label': '$pat' $* stamps \"$want\"" \
                         || bad "PFLW '$label': '$pat' $* stamps \"$got\", expected \"$want\""
}
pflw pflw-exact    'exact'                      'exact'                       '(a){2,3}b'
pflw pflw-norep    'no counted repeat'          'no counted repeat'           '(a)b'
pflw pflw-nullable 'nullable collapsed language' 'nullable collapsed language' '^(a{2,9})*$' -fprefilter-collapse
pflw pflw-forced   'forced'                     'forced'                      '(x)?a{0,4}\Gb' -fprefilter-collapse
# the NFA-state form: FULL text (N is an NFA state count, stable)
pflw pflw-sel1     'dfa overflow retry, exact nfa N' 'dfa overflow retry, exact nfa 1899' \
                   '(1{0,30}?[^]abc][^abc]){28,30}0+|a'

# the byte-figure forms: SHAPE, cap literal, and N > cap checked numerically
# (a full-text pin of N would go red on every emitted-text abi event).
shape() {   # shape ID MACRO LABEL KIND(exact|hybrid) PATTERN [args]
    local id="$1" macro="$2" label="$3" kind="$4" pat="$5"; shift 5
    if ! compile "$id" default "$pat" "$@"; then
        bad "$macro '$label': the compile of '$pat' refused: $(head -1 "$WORK/$id.err")"; return
    fi
    local got n m; got="$(stamp "$macro" "$WORK/$id.c")"
    if printf '%s\n' "$got" | grep -Eq "^size cap retry, $kind [0-9]+ > 1000000\$"; then
        n="$(printf '%s\n' "$got" | sed -n "s/^size cap retry, $kind \([0-9]*\) > \([0-9]*\)\$/\1/p")"
        m="$(printf '%s\n' "$got" | sed -n "s/^size cap retry, $kind \([0-9]*\) > \([0-9]*\)\$/\2/p")"
        if [ "$n" -gt "$m" ]; then
            ok "$macro '$label': \"$got\" has the shape, the cap literal 1000000, and N > cap"
        else
            bad "$macro '$label': \"$got\": the first figure $n is not greater than the cap $m"
        fi
    else
        bad "$macro '$label': \"$got\" does not match ^size cap retry, $kind [0-9]+ > 1000000\$"
    fi
}
shape pflw-sizecap VM_PREFILTER_LANG_WHY 'size cap retry, exact N > M' exact '(\p{Xwd}{1,3})' -e utf8
# RX_VM_PREFILTER_WHY: the hybrid DROP form (the size cap refused the hybrid
# and the retry dropped the prefilter), same shape rule.
shape pwhy-sizecap VM_PREFILTER_WHY 'size cap retry, hybrid N > M' hybrid '(\p{Xwd})' -e utf8
# [decfbB3] the same drop with the collapse denied, so drop-prefilter is the
# FIRST size rung to fire: its own `sets` carry is then the only source of the
# figures (on the default witness prefilter-collapse carried them first, and a
# drop row that stopped carrying still printed that earlier attempt's N > M).
shape pwhy-sizecap-first VM_PREFILTER_WHY 'size cap retry, hybrid N > M (first rung)' hybrid \
      '(\p{Xwd})' -e utf8 -fno-prefilter-collapse

# RX_VM_PREFILTER_WHY is the DROP form's alone: absent where a prefilter
# survives (it explains a "none", never a hybrid).
if compile pwhy-absent default '(a)b' && [ -z "$(stamp VM_PREFILTER_WHY "$WORK/pwhy-absent.c")" ]; then
    ok "RX_VM_PREFILTER_WHY is absent on a surviving hybrid ('(a)b')"
else
    bad "RX_VM_PREFILTER_WHY appears on a surviving hybrid ('(a)b'), or the witness refused"
fi

# =========================================================================
# (e) THE DROP NOTES (B3)
# =========================================================================
echo "== (e) the drop notes: each fired size-cap rung's stderr note, in rung order =="

NOTE_HEAD='pcrec: note: the emitted-size cap forced a smaller artifact: dropped'
NOTE_TAIL='. Raise --max-emit-bytes/--max-emit-code-bytes to keep the faster form, or accept the fit.'
N_ANCH="$NOTE_HEAD the optional anchored match-here machine -- loses the [OPT-2] fast path -- <prefix>_match falls back to search-and-filter, which the anchored machine exists specifically to avoid (docs/design/anchored_match_unwrapped.md)$NOTE_TAIL"
N_PREM="$NOTE_HEAD the premultiplied DFA transition table -- slower per-byte scan dispatch, measured ~1.27x on scan-bound subjects (docs/dev/opt3_dfa_scan_measurement.md)$NOTE_TAIL"
N_PF="$NOTE_HEAD the VM hybrid's prefilter -- the VM tries every start position itself, measured up to ~4x slower where matches are sparse (docs/dev/lanes/pfdrop_report.md)$NOTE_TAIL"

# fnotes ID WANT PATTERN [args...] — the compile (default build) succeeds and
# its stderr's drop-note lines, in order, are exactly WANT (newline-joined
# full lines; empty: no drop note at all).
fnotes() {
    local id="$1" want="$2" pat="$3"; shift 3
    if ! compile "$id" default "$pat" "$@"; then
        bad "notes $id ['$pat' $*]: refused: $(head -1 "$WORK/$id.err")"; return
    fi
    local got; got="$(grep -F -- "$NOTE_HEAD" "$WORK/$id.err")"
    [ "$got" = "$want" ] && ok "notes $id ['$pat' $*]: $(printf '%s\n' "$want" | grep -c . ) drop note(s), as hand-written" \
                         || bad "notes $id ['$pat' $*]: drop notes differ from the hand-written lines: '$got'"
}
fnotes note-anch  "$N_ANCH"            '\p{L}' -e utf8
fnotes note-premul "$N_ANCH
$N_PREM"                                '[^\p{C}\p{M}\p{P}]' -e utf8
fnotes note-pf    "$N_PF"              '(\p{Xwd})' -e utf8
fnotes note-pfc   ""                   '^(\p{Xwd}{1,3})?$' -e utf8 -fprefilter
fnotes note-sel1  ""                   "$W_SEL1"
fnotes note-none  ""                   '(a)b'

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
