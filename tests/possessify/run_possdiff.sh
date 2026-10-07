#!/usr/bin/env bash
# tests/possessify/run_possdiff.sh — the [ENG-BREP] possessification
# differential (eng_brep_design.md §5.1, the row's PRIMARY validation
# requirement).
#
# For each pattern it compiles TWO artifacts from the same pattern text — one
# with the possessification rewrite, one with `-fno-possessify` — links both
# into one driver, and sweeps subjects comparing the span, every capture slot
# and the failure surface. The denied build is the shipped semantics, so any
# disagreement is a bug by construction. See possdiff_driver.c's header.
#
# THE SUBJECT GENERATOR IS THE PART THAT CAN SILENTLY MEASURE NOTHING, and
# D47.6 is why this file says so out loud. The [ENG-BREP] lane's own archived
# sweep reported 20 "false declines" that turned out to be 20 GENUINE
# divergences: its random-subject alphabet was "abcd " and every z-prefixed
# pattern in its family was therefore swept essentially without its prefix, so
# the discriminating subjects were never generated. The rule that came out of
# it, applied here: subjects are built FROM THE PATTERN'S OWN CHARACTERS, and
# the discriminating family is PREFIX + REPEATED BODY. A generator whose
# alphabet omits a pattern character measures the generator.
#
# Usage: run_possdiff.sh [--corpus] [--reach FILE] [--manifest FILE] [patternfile ...]
#   With no argument it runs tests/possessify/patterns.txt and
#   tests/possessify/calls.txt (K93: quantifiers inside call targets) and the
#   [ART-POSS-ARMS] section: the arms_*.txt populations, arms_reach.tsv and
#   arms_manifest.tsv (docs/design/poss_arms.md 8.1).
#   A pattern file may carry ONE `# features: <list>` line; every pattern in
#   that file is then compiled, on both sides, with `--features <list>`.
#   It may also carry ONE `# flags: <list>` line (-e utf8, --ucp, -i), applied
#   to BOTH sides beside it, and ONE `# route: default` line, which compiles
#   side A on the DEFAULT engine route instead of --engine=vm (the route-flip
#   witnesses: an arm-discharged atomic group goes to the DFA; side B stays
#   the denied VM build, so the comparison is DFA-route answers against VM
#   answers). No TAB column: a pattern may begin with a space.
#   A file whose basename starts `arms_` is swept with subjects_exh.py's
#   EXHAUSTIVE subjects (every string of length <= 4 over the pattern's
#   case-flip-closed alphabet) instead of subjects_for's bespoke families.
#   `--reach FILE` (pattern TAB subject [TAB flags]) is checked BEFORE
#   anything is compiled: every pair must be IN the exhaustive sweep, or the
#   run fails (a witness the sweep cannot reach proves nothing).
#   `--manifest FILE` (name TAB want-stamp TAB flags-or-'-' TAB pattern) is
#   the NAMED FLOOR: each row's armed artifact must stamp exactly RX_VM_POSS_ARMS
#   = want, and `--emit-ir`'s marked count armed vs each deny flag must move
#   iff that arm's bit is wanted; a row that stops firing fails BY NAME.
#   `--corpus` additionally derives and sweeps every .rxt corpus pattern the
#   analysis gives a positive verdict on.
# Env: PCREC (compiler), CC, GENCFLAGS (the sanitizer battery's hook),
#      POSSDIFF_KEEP=1 to keep the work directory.

set -e

# LC_ALL=C for the alphabet extraction below: `sort -u` under a UTF-8 locale
# merges characters its collation considers equal, which would quietly shrink
# the subject alphabet this sweep is built from. R24 M-F1's cause, and this
# lane hit it in its sibling script (see run_possessify_tests.sh's own note).
export LC_ALL=C

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"   # [MACPORT] resolves a real GNU gcc when bare gcc is Apple clang

# D45: every compile of GENERATED C in this tree runs under the one shared
# budget, and exceeding it is a loud failure naming the case rather than a
# hang. This suite compiles two artifacts per pattern, so it is exactly the
# kind of site the ruling is about.
#
# EXECUTION is bounded too (gen_run, same file): one driver run per pattern,
# which internally sweeps every subject for that pattern -- a per-pattern
# site, not a hundreds-of-runs inner loop, so it goes through the watchdog
# rather than a bare timeout.
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="possdiff"

WORKDIR=$(mktemp -d "${TMPDIR:-/tmp}/possdiff.XXXXXX")
cleanup() { [ -n "$POSSDIFF_KEEP" ] || rm -rf "$WORKDIR"; }
trap cleanup EXIT

pass=0; fail=0; skipped=0
cells_total=0
poss_patterns=0
reach_ok=0; reach_total=0
man_ok=0; man_total=0
flipped=0

ok()  { pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---------------------------------------------------------------------------
# The subject sweep for one pattern, built from the pattern's own alphabet.
#
# Three families, and each exists because it discriminates something:
#   - the pattern's literal bytes, repeated at every length up to 8. This is
#     D47.6's "prefix + repeated body" family, the one whose absence hid the
#     lazy defect;
#   - those bytes with one character DELETED and one DOUBLED, which is what
#     moves a loop off its boundary count (m-1, m, m+1, n-1, n, n+1 fall out
#     of this without having to parse the pattern's own {m,n});
#   - a handful of fixed adversarial subjects (empty, a byte outside the
#     pattern's alphabet, a newline) so a pattern whose alphabet is tiny still
#     gets its failure paths walked.
subjects_for() {
    pat="$1"
    # The pattern's own characters, minus regex metacharacters: what a loop
    # can actually consume. `tr -d` rather than a class so a pattern
    # containing a `]` cannot break the extraction.
    # `-` LAST in the delete set: anywhere else `tr` reads it as a range
    # endpoint, which on this set is `]-,` and warns rather than deleting.
    alpha=$(printf '%s' "$pat" | tr -d '\\^$.|?*+(){}[],0123456789-' | \
            fold -w1 | sort -u | tr -d '\n')
    [ -n "$alpha" ] || alpha=ab
    # Digits get their own representative when the pattern mentions a digit
    # class, since \d{4} has no literal digit in its text at all.
    case "$pat" in *'\d'*|*'[0-9'*|*'0-9]'*) alpha="${alpha}7" ;; esac

    printf '\n'                       # the empty subject
    printf 'q\n'                      # outside almost every alphabet
    printf '\\n\n'                    # a newline, for the $ family

    # every single character, and runs of each up to length 8
    i=1
    len=$(printf '%s' "$alpha" | wc -c)
    while [ "$i" -le "$len" ]; do
        c=$(printf '%s' "$alpha" | cut -c"$i")
        r=""
        n=1
        while [ "$n" -le 8 ]; do
            r="$r$c"
            printf '%s\n' "$r"
            printf '%s%s\n' "$r" "q"
            n=$((n + 1))
        done
        i=$((i + 1))
    done

    # the whole alphabet as one string, repeated -- the "prefix + repeated
    # body" shape, which is what carries a prefix character into the sweep
    w="$alpha"
    n=1
    while [ "$n" -le 6 ]; do
        printf '%s\n' "$w"
        printf '%sq\n' "$w"
        w="$w$alpha"
        n=$((n + 1))
    done

    # the alphabet with one character doubled at each position, which walks a
    # bounded loop across its own boundary counts
    i=1
    while [ "$i" -le "$len" ]; do
        c=$(printf '%s' "$alpha" | cut -c"$i")
        printf '%s%s%s\n' "$alpha" "$c" "$alpha"
        i=$((i + 1))
    done
}

one_pattern() {
    pat="$1"
    d="$WORKDIR/p$pass$fail$skipped$$"
    rm -rf "$d"; mkdir -p "$d"
    enga="--engine=vm"; [ "$route" = default ] && enga=""

    # --engine=vm on BOTH sides. Two reasons, and the second is the one that
    # matters: it forces every pattern onto the VM (so a capture-free pattern
    # is swept too, rather than silently routing to the DFA where
    # possessification never runs), and it turns the DFA prefilter OFF, so the
    # comparison is of the VM's own derivation rather than of a window the DFA
    # handed both sides (R21 E-6).
    if ! pcrec_run "$PCREC" -p pa $enga $feat_args $flag_args -o "$d/pa.c" --pattern "$pat" \
            >/dev/null 2>"$d/err_a"; then
        # A file that declares its modules declared what its patterns need,
        # so a refusal there is a population silently lost, not a cell.
        if [ -n "$feats" ]; then
            bad "'$pat': refused under --features $feats: $(head -1 "$d/err_a")"
            return 0
        fi
        skipped=$((skipped + 1))
        return 0                       # a pattern pcrec refuses is not a cell
    fi
    if ! pcrec_run "$PCREC" -p pb --engine=vm -fno-possessify $feat_args $flag_args -o "$d/pb.c" --pattern "$pat" \
            >/dev/null 2>"$d/err_b"; then
        bad "'$pat': the possessified build compiled and the DENIED one did not"
        return 0
    fi

    # DO-OR-DIE (D47.3): the denied artifact must not carry a possessive stamp.
    # Asserted against the ARTIFACT, never against the flag having been passed
    # — that is the whole point of the stamp existing.
    if ! grep -q '^#define PB_VM_STRATS ' "$d/pb.c"; then
        bad "'$pat': the denied artifact carries no PB_VM_STRATS stamp at all"
        return 0
    fi
    # [ABI-NS] (D60): PCREC_VM_STRAT_POSSESSIVE lives in the paired `.h`
    # (SPLIT output, since possdiff_driver.c #includes "pa.h"/"pb.h"
    # directly) — the shared PCREC_RX_ABI_H block is emitted once into the
    # header, never into the .c passed to $PCREC's -o. Reading it from the
    # .c alone silently found nothing and made every artifact read as
    # "not possessified" (found live, 2026-08-18).
    pb_strats=$(sed -n 's/^#define PB_VM_STRATS 0x\([0-9a-f]*\)u$/\1/p' "$d/pb.c")
    # PCREC_VM_STRAT_POSSESSIVE is [ABI-NS]/D60 universal: emitted
    # UNCONDITIONALLY on every artifact. An empty read means the
    # extraction is broken (wrong file/spelling), never a legitimate "no"
    # -- HARD-FAIL rather than let `0x$pb_strats & 0x` silently evaluate
    # to 0, which is exactly what turned this suite's own do-or-die check
    # and the possessified-count into false negatives (found live,
    # 2026-08-18: this empty-arithmetic path is what made "0 of 155
    # possessified" read as a clean run).
    pb_poss=$(sed -n 's/^#define PCREC_VM_STRAT_POSSESSIVE *0x\([0-9a-f]*\)u$/\1/p' "$d/pb.h")
    if [ -z "$pb_poss" ]; then
        echo "FATAL: PCREC_VM_STRAT_POSSESSIVE not found in $d/pb.h" >&2
        exit 1
    fi
    if [ $(( 0x$pb_strats & 0x$pb_poss )) -ne 0 ]; then
        bad "'$pat': -fno-possessify was passed and the artifact still stamps POSSESSIVE (D47.3 do-or-die)"
        return 0
    fi

    pa_strats=$(sed -n 's/^#define PA_VM_STRATS 0x\([0-9a-f]*\)u$/\1/p' "$d/pa.c")
    pa_poss=$(sed -n 's/^#define PCREC_VM_STRAT_POSSESSIVE *0x\([0-9a-f]*\)u$/\1/p' "$d/pa.h")
    if [ -n "$pa_strats" ] && [ -z "$pa_poss" ]; then
        echo "FATAL: PCREC_VM_STRAT_POSSESSIVE not found in $d/pa.h" >&2
        exit 1
    fi
    this_poss=0
    if [ -n "$pa_strats" ] && [ $(( 0x$pa_strats & 0x$pa_poss )) -ne 0 ]; then
        this_poss=1
        poss_patterns=$((poss_patterns + 1))
    fi

    # shellcheck disable=SC2086
    if ! gen_cc "possdiff '$pat'" $CC -O1 -Wall -Wextra -std=gnu11 $GENCFLAGS \
                -I "$d" -o "$d/t" "$SCRIPT_DIR/possdiff_driver.c" \
                "$d/pa.c" "$d/pb.c"; then
        printf '%s\n' "$GEN_CC_LOG" > "$d/cc"
        bad "'$pat': the two-artifact driver did not compile"
        cat "$d/cc" >&2
        return 0
    fi

    if [ "$exhaustive" = 1 ]; then
        # shellcheck disable=SC2086
        python3 -B "$SCRIPT_DIR/subjects_exh.py" "$pat" $flags > "$d/subj"
    else
        subjects_for "$pat" > "$d/subj"
    fi
    if [ "$route" = default ]; then
        # The route-flip file's NON-VACUITY: side A must really be on the DFA.
        eng=$(sed -n 's/^#define PA_ENGINE "\([a-z]*\)".*/\1/p' "$d/pa.c" | head -1)
        if [ "$eng" != dfa ]; then
            bad "'$pat': the route-flip witness did not go to the DFA by default (engine=${eng:-?})"
            return 0
        fi
        flipped=$((flipped + 1))
    fi
    # A plain stdin redirect on the gen_run call works ONLY because watchdog
    # spawns its child with an explicit `<&0` (see scripts/watchdog's spawn
    # comment): a backgrounded job in a job-control-less shell otherwise gets
    # /dev/null stdin, and this site's first wiring silently fed the driver
    # an EMPTY subject sweep — 0 cells compared while "0 diverged" stayed
    # green, exactly this file's own D47.6 "measured nothing" failure mode,
    # caught only against the recorded 77725-cell baseline. If this count
    # ever drops to ~0 with everything green, suspect stdin first.
    if out=$(gen_run "possdiff '$pat'" "$d/t" < "$d/subj" 2>"$d/diverge"); then
        n=$(printf '%s' "$out" | sed -n 's/^cells \([0-9]*\) .*/\1/p')
        cells_total=$((cells_total + ${n:-0}))
        ok
    else
        bad "'$pat' (possessified=$this_poss): $(head -4 "$d/diverge" | tr '\n' ' ')"
        cells_total=$((cells_total + 0))
    fi
    [ -n "$POSSDIFF_KEEP" ] || rm -rf "$d"
}

# `--corpus` sweeps the .rxt CORPUS's verdict-positive patterns instead of (or
# as well as) the designed family. The row's validation asks for both, and they
# are different populations: patterns.txt is built to exercise the RULE's own
# arms and refutations, while the corpus is what pcrec is actually asked to
# compile — adversarial by construction, and the place a shape nobody designed
# for turns up. The list is derived at run time from the pass's own census line
# rather than kept as a second file that could go stale against the analysis.
if [ "${1:-}" = "--corpus" ]; then
    shift
    derived="$WORKDIR/corpus_positive.txt"
    : > "$derived"
    # [DD-8] THE LISTING IS TABLE-CONTRACT TSV NOW. The column indices are
    # resolved BY NAME once, from a probe listing, and the per-pattern read
    # is then one `awk` — the same process count the old `sed -n` cost, so a
    # ~4,000-pattern derivation loop pays nothing for the conversion. A
    # renamed section or column is a LOUD failure here, at the hoist, rather
    # than an empty string every iteration that reads like "no pattern in
    # the corpus selects this rung".
    . "$ROOT_DIR/tests/lib/table.sh"
    probe="$WORKDIR/probe.ir"
    if ! pcrec_run "$PCREC" --engine=vm --emit-ir --pattern '(a)b' > "$probe" 2>/dev/null; then
        echo "possdiff: could not produce a probe --emit-ir listing" >&2; exit 2
    fi
    fact_i="$(table_col_index "$probe" fact summary)" || exit 2
    val_i="$(table_col_index "$probe" value summary)" || exit 2
    grep -rhs '^pattern ' "$ROOT_DIR/tests" --include='*.rxt' | sed 's/^pattern //' \
        | sort -u > "$WORKDIR/all.txt"
    while IFS= read -r cp; do
        [ -n "$cp" ] || continue
        # [DD-8] `possessify`'s value is `marked/total`; the old line was
        # `; possessify   N of M ...`. The marked half is what this arm wants.
        n="$(pcrec_run "$PCREC" --engine=vm --emit-ir --pattern "$cp" 2>/dev/null \
             | awk -F'\t' -v ki="$fact_i" -v vi="$val_i" '
                 /^#section summary$/ { s = 1; next }
                 /^#section /         { s = 0; next }
                 s && $ki == "possessify" { split($vi, p, "/"); print p[1] }')"
        [ -n "$n" ] && [ "$n" -gt 0 ] 2>/dev/null && printf '%s\n' "$cp" >> "$derived"
    done < "$WORKDIR/all.txt"
    echo "possdiff: derived $(wc -l < "$derived") verdict-positive corpus patterns"
    set -- "$derived" "$@"
fi

# ---- the [ART-POSS-ARMS] section's three instruments ---------------------
ARMS_ENV_FILES="$SCRIPT_DIR/arms_core.txt $SCRIPT_DIR/arms_utf8.txt \
$SCRIPT_DIR/arms_utf8i.txt $SCRIPT_DIR/arms_ucp.txt $SCRIPT_DIR/arms_i.txt \
$SCRIPT_DIR/arms_routeflip.txt"

reach_file=""; manifest_file=""
while [ $# -gt 0 ]; do
    case "$1" in
    --reach)    reach_file="$2"; shift 2 ;;
    --manifest) manifest_file="$2"; shift 2 ;;
    *) break ;;
    esac
done

files="$*"
if [ -z "$files" ]; then
    files="$SCRIPT_DIR/patterns.txt $SCRIPT_DIR/calls.txt $ARMS_ENV_FILES"
    reach_file="${reach_file:-$SCRIPT_DIR/arms_reach.tsv}"
    manifest_file="${manifest_file:-$SCRIPT_DIR/arms_manifest.tsv}"
fi

# REACH, before anything is compiled: a (pattern, witness) pair the sweep
# cannot generate would make its sabotage row undetectable by construction.
# Subject in the driver's escape form; flags are the pair's own.
if [ -n "$reach_file" ]; then
    [ -f "$reach_file" ] || { echo "run_possdiff.sh: no such reach file: $reach_file" >&2; exit 2; }
    while IFS=$'\t' read -r rp rs rfl; do
        case "$rp" in ''|'#'*) continue ;; esac
        reach_total=$((reach_total + 1))
        # shellcheck disable=SC2086
        if python3 -B "$SCRIPT_DIR/subjects_exh.py" --reach "$rs" "$rp" $rfl; then
            reach_ok=$((reach_ok + 1))
        else
            bad "REACH MISS: witness subject '$rs' is not in the exhaustive sweep of '$rp' $rfl"
        fi
    done < "$reach_file"
fi

# The marked count of `--emit-ir`'s `possessify` fact (value `marked/total`),
# read by column NAME as --corpus does. $1 = pattern, rest = flags.
ir_marked() {
    p="$1"; shift
    pcrec_run "$PCREC" "$@" --emit-ir --pattern "$p" 2>/dev/null \
        | awk -F'\t' -v ki="$fact_i" -v vi="$val_i" '
            /^#section summary$/ { s = 1; next }
            /^#section /         { s = 0; next }
            s && $ki == "possessify" { split($vi, p, "/"); print p[1] }'
}

# The NAMED MANIFEST (the floor). Population >= 1 is not a floor: it passes
# while every arm is dead. Each row names a pattern, the exact arm stamp its
# armed artifact must carry (bit 0x1 A0, 0x2 A1, 0x4 B; 0 = a witness that
# must NOT fire), and the marked-count movement against each deny flag:
# armed > -fno-poss-ctx-follow iff want & 3, armed > -fno-poss-bref-first iff
# want & 4. Two readings of one fact (the stamp and the IR count) so neither
# is a control sharing a source with the other. A row that stops firing fails
# BY NAME.
manifest_check() {
    . "$ROOT_DIR/tests/lib/table.sh"
    probe="$WORKDIR/probe.ir"
    pcrec_run "$PCREC" --engine=vm --emit-ir --pattern '(a)b' > "$probe" 2>/dev/null \
        || { echo "possdiff: could not produce a probe --emit-ir listing" >&2; exit 2; }
    fact_i="$(table_col_index "$probe" fact summary)" || exit 2
    val_i="$(table_col_index "$probe" value summary)" || exit 2
    while IFS=$'\t' read -r mname mwant mfl mpat; do
        case "$mname" in ''|'#'*) continue ;; esac
        man_total=$((man_total + 1))
        [ "$mfl" = "-" ] && mfl=""
        md="$WORKDIR/man"; rm -rf "$md"; mkdir -p "$md"
        # shellcheck disable=SC2086
        if ! pcrec_run "$PCREC" -p ma --engine=vm --features all $mfl -o "$md/ma.c" \
                --pattern "$mpat" >/dev/null 2>"$md/err"; then
            bad "MANIFEST '$mname': the armed build refused: $(head -1 "$md/err")"
            continue
        fi
        got=$(sed -n 's/^#define MA_VM_POSS_ARMS 0x\([0-9a-f]*\)u$/\1/p' "$md/ma.c")
        if [ -z "$got" ]; then
            bad "MANIFEST '$mname': the armed artifact carries no MA_VM_POSS_ARMS stamp"
            continue
        fi
        want=$(( mwant ))
        if [ $(( 0x$got )) -ne "$want" ]; then
            bad "MANIFEST '$mname': arm stamp is 0x$got, the manifest pins $mwant ($mpat)"
            continue
        fi
        # shellcheck disable=SC2086
        m_arm=$(ir_marked "$mpat" --engine=vm --features all $mfl)
        # shellcheck disable=SC2086
        m_noa=$(ir_marked "$mpat" --engine=vm --features all $mfl -fno-poss-ctx-follow)
        # shellcheck disable=SC2086
        m_nob=$(ir_marked "$mpat" --engine=vm --features all $mfl -fno-poss-bref-first)
        if [ -z "$m_arm" ] || [ -z "$m_noa" ] || [ -z "$m_nob" ]; then
            bad "MANIFEST '$mname': could not read the --emit-ir marked count ($m_arm/$m_noa/$m_nob)"
            continue
        fi
        wa=0; [ $(( want & 3 )) -ne 0 ] && wa=1
        wb=0; [ $(( want & 4 )) -ne 0 ] && wb=1
        da=0; [ "$m_arm" -gt "$m_noa" ] && da=1
        db=0; [ "$m_arm" -gt "$m_nob" ] && db=1
        if [ "$da" -ne "$wa" ] || [ "$db" -ne "$wb" ]; then
            bad "MANIFEST '$mname': marked armed=$m_arm denyA=$m_noa denyB=$m_nob, the stamp $mwant wants A-moves=$wa B-moves=$wb"
            continue
        fi
        man_ok=$((man_ok + 1))
    done < "$manifest_file"
}
if [ -n "$manifest_file" ]; then
    [ -f "$manifest_file" ] || { echo "run_possdiff.sh: no such manifest: $manifest_file" >&2; exit 2; }
    manifest_check
fi

for f in $files; do
    [ -f "$f" ] || { echo "run_possdiff.sh: no such pattern file: $f" >&2; exit 2; }
    # The file's module set, unquoted on purpose at the use sites: empty
    # expands to no argument at all.
    feats="$(sed -n 's/^# features: *//p' "$f" | head -1)"
    feat_args="${feats:+--features $feats}"
    flags="$(sed -n 's/^# flags: *//p' "$f" | head -1)"
    flag_args="$flags"
    route="$(sed -n 's/^# route: *//p' "$f" | head -1)"
    exhaustive=0
    case "$(basename "$f")" in arms_*) exhaustive=1 ;; esac
    while IFS= read -r pat; do
        case "$pat" in ''|'#'*) continue ;; esac
        one_pattern "$pat"
    done < "$f"
done

echo "possdiff: $pass patterns agreed, $fail diverged, $skipped refused by pcrec"
echo "possdiff: $poss_patterns of $pass had at least one POSSESSIFIED quantifier"
echo "possdiff: $cells_total pattern-subject-startpos cells compared"
if [ -n "$reach_file" ]; then
    echo "possdiff: reach $reach_ok/$reach_total witness pairs inside the exhaustive sweep"
    [ "$reach_ok" -eq "$reach_total" ] || fail=$((fail + 1))
fi
if [ -n "$manifest_file" ]; then
    echo "possdiff: manifest $man_ok/$man_total rows fire as pinned"
    [ "$man_ok" -eq "$man_total" ] || fail=$((fail + 1))
fi
echo "possdiff: $flipped route-flip witnesses compiled to the DFA on side A"

# NON-VACUITY, the control this check needs as much as the check itself. An
# instrument that compares two identical artifacts agrees on everything and
# measures nothing; if no pattern in the file possessified, the sweep proved
# only that the compiler is deterministic.
if [ "$poss_patterns" -eq 0 ] && [ "$pass" -gt 0 ]; then
    echo "FAIL: not one pattern possessified -- this sweep compared identical artifacts and measured nothing" >&2
    fail=$((fail + 1))
fi

[ "$fail" -eq 0 ] || exit 1
