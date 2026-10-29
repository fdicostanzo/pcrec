#!/usr/bin/env bash
# tests/codegen/run_start_landing.sh — [START-LANDING] the two RECOVER rows
# that know the match start without walking back, held to the artifact
# (docs/design/start_landing.md §7.3; run_search_pinned.sh's sibling).
#
# =========================================================================
# WHAT IS BEING DEFENDED
# =========================================================================
# `<prefix>_search` finds where a match ENDS with the forward scan and, by
# default, where it BEGAN with a backwards pass over an independently built
# REVERSE machine. Two rows answer the second question without that pass:
#
#   end-minus-width  every match is W bytes (the `width` fact's [W,W]), so
#                    the start is the verified end minus W;
#   landing          every one-character path from the pattern's start ends
#                    dead or accepting (the `land_char` fact, Λ), so the
#                    start is where the NEXT block last landed — with, where a
#                    first byte is above the one-byte repertoire, §2.5's
#                    post-loop SKIP to the first character start at or after
#                    it (an ill-formed sequence matches nothing).
#
# Each is proved to return EXACTLY today's reverse-pass start on every call,
# so the control is the build that denies all three rows answering without
# the reverse pass (`-fno-start-pinned -fno-start-width -fno-start-landing`):
# its answer comes from the independently built reverse automaton, and the
# two share nothing but the answer (docs/dev/learnings.md §3).
#
# Sections (the design's §7.3 list):
#   §1  hand witnesses, expectations LITERAL, each under every deny arm;
#   §2  stamp <=> body <=> mirror over the corpus, from matcher TEXT;
#   §3  the population floors (a dead row passes every other section);
#   §4  deny identity: an artifact a row did not take is byte-identical under
#       its deny; the PRODUCT arm's artifacts all carry the reverse machine;
#   §5  every-startpos answer differential, default vs the triple deny, on the
#       witnesses and on the ill-formed tokens;
#   §6  the oracle-verified corpus file tests/utf8/landing_illformed.rxt
#       (libpcre2 under UTF|MATCH_INVALID_UTF; run by test-corpus) REACHES the
#       guarded landing on every block;
#   §H  the STANDING HOSTILE CELL: utf8 `.` and `\p{L}+`, find-all over 1 MiB
#       of a lead byte then `a`, under a 10 s wall bound, the answer checked.
#
# THE DISCRIMINATORS ARE MATCHER TEXT, never the stamp: `size_t
# rewind_position` (the reverse pass), `landing_position = scan_position;`
# (the record), `last_accept_position - <W>;` (the subtraction) and
# `_decode(subject, subject_length, landing_position` (the guard).
#
# Every compile passes `-fcomments` for run_search_pinned.sh's measured
# reason (the code is byte-identical with and without comments).
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
KEEP="${KEEP:-0}"
GENCFLAGS="${GENCFLAGS:-}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
. "$ROOT_DIR/tests/lib/procs_default.sh"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
. "$ROOT_DIR/tests/lib/shard_split.sh"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "start-landing: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

[ -x "$PCREC" ] || { echo "FAIL: start-landing: no compiler at $PCREC — run \`make\` first" >&2; exit 1; }

DENY3="-fno-start-pinned -fno-start-width -fno-start-landing"

emit() { # emit <outfile> <prefix> <pattern> [extra pcrec args...]
    local out="$1" p="$2" pat="$3"
    shift 3
    pcrec_run "$PCREC" -p "$p" --no-captures --features all -fcomments "$@" \
        -o "$out" --pattern "$pat" >/dev/null 2>&1
}
stamp()  { grep -m1 "^#define ${2:-RX}_DFA_START \"" "$1" | cut -d'"' -f2; }
mirror() { grep -m1 '^    \.search_form = ' "$1" \
             | sed 's/^    \.search_form = //; s/,$//; s/^"//; s/"$//'; }
has_rewind()  { grep -q 'size_t rewind_position' "$1"; }
has_record()  { grep -q 'landing_position = scan_position;' "$1"; }
has_minus()   { grep -qE 'size_t match_start_position = last_accept_position - [0-9]+;' "$1"; }
has_guard()   { grep -q '_decode(subject, subject_length, landing_position' "$1"; }

# =========================================================================
# §1 THE HAND WITNESSES
# =========================================================================
# One row per witness and deny arm: encoding, pattern, the arm's flags, and
# the expected `RX_DFA_START`, every one a LITERAL from the design's §7.3 §1
# (never harvested from the artifact). `a\bb` is the EMPTY engine: its path
# asks no RECOVER, so it stamps the absence value. The mechanism is asserted
# with the stamp, so a row cannot pass on a stamp whose machinery is absent.
# D172 S3 (job 600): `abcd` and `[a-z]` are fixed-width windows, `cover`
# artifacts by default (RX_DFA_START "attempt-start", no RECOVER row asked;
# run_dfa_stamps.sh holds that witness), so their rows carry the cover row's
# deny `--memfn=no-window-search`, which renders the build before S3.
W1="$WORKDIR/w1"
printf '%s\n' \
    'byte	abcd	--memfn=no-window-search	end-minus-width' \
    'byte	abcd	--memfn=no-window-search -fno-start-width	reverse-pass' \
    'byte	abcd	--memfn=no-window-search -fno-start-landing	end-minus-width' \
    'byte	\w+	-	landing' \
    'byte	\w+	-fno-start-width	landing' \
    'byte	\w+	-fno-start-landing	reverse-pass' \
    'utf8	.	-	landing' \
    'utf8	.	-fno-start-landing	reverse-pass' \
    'utf8	\w+	-	landing' \
    'byte	[a-z]	--memfn=no-window-search	end-minus-width' \
    'byte	[a-z]	--memfn=no-window-search -fno-start-width	landing' \
    'byte	[a-z]	--memfn=no-window-search -fno-start-width -fno-start-landing	reverse-pass' \
    'byte	(?s).	-	end-minus-width' \
    'byte	(?s).	-fno-start-width	reverse-pass' \
    'byte	a\bb	-	attempt-start' \
    'byte	x*y	-	reverse-pass' \
    'byte	a*	-	pinned' \
    'byte	a*	-fno-start-pinned	reverse-pass' \
    'byte	(?!a)	-	end-minus-width' \
    'byte	(?!a)	-fno-start-width	reverse-pass' > "$W1"
w1bad=""; nw1=0
while IFS=$'\t' read -r enc pat flags want; do
    nw1=$((nw1 + 1))
    [ "$flags" = - ] && flags=""
    f="$WORKDIR/w1.c"
    # shellcheck disable=SC2086
    if ! emit "$f" rx "$pat" -e "$enc" $flags; then w1bad="$w1bad [$enc '$pat' $flags: refused]"; continue; fi
    got="$(stamp "$f")"
    [ "$got" = "$want" ] || { w1bad="$w1bad [$enc '$pat' $flags: stamps '$got', expected '$want']"; continue; }
    m="$(mirror "$f")"
    [ "$m" = "$got" ] || w1bad="$w1bad [$enc '$pat' $flags: mirror '$m' vs macro '$got']"
    case "$got" in
        end-minus-width)
            has_minus "$f" && ! has_rewind "$f" && ! has_record "$f" \
                || w1bad="$w1bad [$enc '$pat' $flags: end-minus-width without its subtraction alone]" ;;
        landing)
            has_record "$f" && ! has_rewind "$f" \
                || w1bad="$w1bad [$enc '$pat' $flags: landing without its record, or with a reverse pass]"
            # The guard iff a first byte is above the one-byte repertoire:
            # utf8 `.` yes; `\w+` (ASCII without UCP) and every byte pattern no.
            if [ "$enc" = utf8 ] && [ "$pat" = . ]; then
                has_guard "$f" || w1bad="$w1bad [utf8 '.': landing WITHOUT its guard]"
            else
                has_guard "$f" && w1bad="$w1bad [$enc '$pat': a guard on an ASCII start set]"
            fi ;;
        reverse-pass)
            has_rewind "$f" && ! has_record "$f" && ! has_minus "$f" \
                || w1bad="$w1bad [$enc '$pat' $flags: reverse-pass without its reverse pass alone]" ;;
        attempt-start)
            grep -q '^    return 0;$' "$f" || w1bad="$w1bad [$enc '$pat': the empty engine has no bare return 0]" ;;
        pinned) ;;
    esac
done < "$W1"
[ -z "$w1bad" ] && ok "§1 $nw1 witness rows (eight witnesses x their deny arms) stamp the literal value, mirror it, and carry exactly their mechanism" \
    || bad "§1 witnesses:$w1bad"
# Under -futf-check the searched range is proven well-formed, so the guard is
# dead and is not emitted (D156 addendum 4 Q2 item 3).
if emit "$WORKDIR/uc.c" rx . -e utf8 -futf-check && [ "$(stamp "$WORKDIR/uc.c")" = landing ]; then
    has_guard "$WORKDIR/uc.c" && bad "§1 utf8 '.' under -futf-check still emits the landing guard" \
        || ok "§1 utf8 '.' under -futf-check takes landing with NO guard (the contract proves the range well-formed)"
else
    bad "§1 utf8 '.' under -futf-check does not compile to landing"
fi

# =========================================================================
# THE CORPUS EXTRACTION and the sweep (§2, §3, §4)
# =========================================================================
grep -rhE '^pattern ' "$ROOT_DIR/tests" 2>/dev/null | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$WORKDIR/pats"
npat="$(wc -l < "$WORKDIR/pats")"
if [ "$npat" -lt 2620 ]; then
    bad "start-landing: corpus extraction found only $npat patterns, below the 2620 floor (run_search_pinned.sh's): the population shrank or the extraction is dropping patterns (K35)"
    echo; echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
NSHARD="${PROCS:-$PROCS_DEFAULT}"
[ "$NSHARD" -ge 1 ] 2>/dev/null || NSHARD=1
mkdir -p "$WORKDIR/sh"
shard_split "$NSHARD" "$WORKDIR/pats" "$WORKDIR/sh/p" || exit 1
NSHARD="$SHARD_COUNT"

cat > "$WORKDIR/worker.sh" <<'WORKER'
set -u
. "$ROOT_DIR/tests/lib/gen_timeout.sh" >/dev/null 2>&1
art="$WORKDIR/a.$$.c"; den="$WORKDIR/d.$$.c"
trap 'rm -f "$art" "$den"' EXIT
cc1() { pcrec_run "$PCREC" --features all -fcomments -p rx --no-captures "$@" -o - --pattern "$pat"; }
while IFS= read -r pat; do
    cc1 > "$art" 2>/dev/null || { echo "REFUSED"; continue; }
    start="$(grep -m1 '^#define RX_DFA_START "' "$art" | cut -d'"' -f2)"
    [ -n "$start" ] || { echo "NOSTAMP"; continue; }
    mir="$(grep -m1 '^    \.search_form = ' "$art" | sed 's/^    \.search_form = //; s/,$//; s/^"//; s/"$//')"
    [ "$mir" = "$start" ] || { echo "BAD: mirror '$mir' vs macro '$start': $pat"; }
    eng="$(grep -m1 '^#define RX_ENGINE "' "$art" | cut -d'"' -f2)"
    rw=0; grep -q 'size_t rewind_position' "$art" && rw=1
    rec=0; grep -q 'landing_position = scan_position;' "$art" && rec=1
    sub=0; grep -qE 'size_t match_start_position = last_accept_position - [0-9]+;' "$art" && sub=1
    grd=0; grep -q '_decode(subject, subject_length, landing_position' "$art" && grd=1
    echo "START-$start-$eng"
    # ---- §2 stamp <=> body, both directions ----
    case "$start" in
        landing)
            [ "$rec" = 1 ] && [ "$rw" = 0 ] && [ "$sub" = 0 ] || echo "BAD: \"landing\" rec=$rec rewind=$rw sub=$sub: $pat"
            [ "$grd" = 1 ] && echo "GUARD-$eng" ;;
        end-minus-width)
            [ "$sub" = 1 ] && [ "$rw" = 0 ] && [ "$rec" = 0 ] && [ "$grd" = 0 ] || echo "BAD: \"end-minus-width\" sub=$sub rewind=$rw rec=$rec guard=$grd: $pat" ;;
        *)
            [ "$rec" = 0 ] && [ "$sub" = 0 ] && [ "$grd" = 0 ] || echo "BAD: \"$start\" carries a new row's mechanism rec=$rec sub=$sub guard=$grd: $pat" ;;
    esac
    # ---- §4 deny identity, and the product arm ----
    for arm in "-fno-start-width" "-fno-start-landing"; do
        took=0
        [ "$arm" = -fno-start-width ] && [ "$start" = end-minus-width ] && took=1
        [ "$arm" = -fno-start-landing ] && [ "$start" = landing ] && took=1
        [ "$took" = 1 ] && continue
        if cc1 $arm > "$den" 2>/dev/null; then
            cmp -s "$art" "$den" && echo "DENYSAME" || echo "BAD: a row the artifact did not take moved it under $arm: $pat"
        else
            echo "BAD: $arm REFUSED a pattern the default compiled: $pat"
        fi
    done
    if [ "$start" = landing ] || [ "$start" = end-minus-width ]; then
        if cc1 -fno-start-width -fno-start-landing > "$den" 2>/dev/null; then
            ps="$(grep -m1 '^#define RX_DFA_START "' "$den" | cut -d'"' -f2)"
            if [ "$ps" = reverse-pass ] && grep -q 'size_t rewind_position' "$den"; then echo "PRODUCT-R"
            else echo "BAD: the product arm stamps '$ps' (or no reverse pass) on a $start artifact: $pat"; fi
            if [ "$start" = landing ] && cc1 -fno-start-landing > "$den" 2>/dev/null &&
               [ "$(grep -m1 '^#define RX_DFA_START "' "$den" | cut -d'"' -f2)" = reverse-pass ]; then
                echo "LANDONLY"
            fi
        else
            echo "BAD: the product arm REFUSED a pattern the default compiled: $pat"
        fi
    fi
done
WORKER
export ROOT_DIR PCREC WORKDIR
for i in $(seq 0 $((NSHARD - 1))); do
    f="$(printf '%s/sh/p%02d' "$WORKDIR" "$i")"
    [ -f "$f" ] || continue
    bash "$WORKDIR/worker.sh" < "$f" > "$WORKDIR/out.$i" 2>&1 &
done
wait
cat "$WORKDIR"/out.* > "$WORKDIR/all.out" 2>/dev/null
tok() { grep -c "^$1\$" "$WORKDIR/all.out" 2>/dev/null || true; }
n_land=$(( $(tok START-landing-dfa) + $(tok START-landing-vm) ))
n_emw=$(( $(tok START-end-minus-width-dfa) + $(tok START-end-minus-width-vm) ))
n_landvm=$(tok START-landing-vm); n_emwvm=$(tok START-end-minus-width-vm)
n_guard=$(( $(tok GUARD-dfa) + $(tok GUARD-vm) ))
n_denysame=$(tok DENYSAME); n_prod=$(tok PRODUCT-R); n_landonly=$(tok LANDONLY)
n_bad=$(grep -c '^BAD: ' "$WORKDIR/all.out" 2>/dev/null || true)
echo "    $npat patterns: landing $n_land (hybrid $n_landvm, guarded $n_guard), end-minus-width $n_emw (hybrid $n_emwvm); deny-identical $n_denysame; product arm reaches the reverse pass on $n_prod"
if [ "$n_bad" -eq 0 ]; then
    ok "§2 stamp == body == mirror over $npat corpus patterns: a landing artifact carries the record and no reverse machine, an end-minus-width one the subtraction and no reverse machine, every other stamp neither new mechanism"
    ok "§4 deny identity: all $n_denysame artifacts a row did not take are byte-identical under that row's deny, and the product arm (-fno-start-width -fno-start-landing) puts every one of the $n_prod new-row artifacts back on the reverse pass"
else
    bad "§2/§4 the corpus sweep reported $n_bad failures; first eight:"
    grep -m8 '^BAD: ' "$WORKDIR/all.out" >&2
fi

# =========================================================================
# §3 THE FLOORS
# =========================================================================
# A dead row passes every section above (nothing to compare, nothing to
# deny), so the populations are FLOORED. MEASURED on this sweep's own flags
# (--features all --no-captures, the corpus's pattern lines without their
# blocks' encodings) at lane slbuild's tree, 2026-10-10: landing 211,
# end-minus-width 1,406, product-arm reach 1,617 over 4,647 patterns; each
# floor is ~80% of the measured count. `landonly` is the rows where
# -fno-start-landing alone reaches the reverse pass (end-minus-width did not
# apply), and `guard` the landings that carry the guard (a `-e utf8` pattern
# line in the corpus compiles here under byte, so the guarded population
# comes from §1, §5 and §6, and this floor is 0 by construction).
# S3 RE-PIN (lane s3, job 600, 2026-10-23): D172 S3 routes the fixed-width
# windows to `cover` by default (RX_DFA_START "attempt-start"), so they leave
# end-minus-width and with them the product arm's reach. MEASURED at the S3
# tree (ba6ebf720's job 600, 4,870 patterns): end-minus-width 510 (was
# floor 1,124), product-arm reach 705 (was 1,290); pinned AT the measured
# value. Landing (195) stays above its floor and is untouched.
FLOOR_LAND=${FLOOR_LAND:-168}
FLOOR_EMW=${FLOOR_EMW:-510}
FLOOR_PROD=${FLOOR_PROD:-705}
if [ "$n_land" -lt "$FLOOR_LAND" ] || [ "$n_emw" -lt "$FLOOR_EMW" ] || [ "$n_prod" -lt "$FLOOR_PROD" ]; then
    bad "§3 the populations fell below their floors: landing $n_land (floor $FLOOR_LAND), end-minus-width $n_emw (floor $FLOOR_EMW), product-arm reach $n_prod (floor $FLOOR_PROD) — the corpus moved or a row stopped selecting; read it before re-pinning"
else
    ok "§3 landing $n_land >= $FLOOR_LAND, end-minus-width $n_emw >= $FLOOR_EMW, product-arm reach $n_prod >= $FLOOR_PROD (landing-only deny reach $n_landonly)"
fi

# =========================================================================
# §5 THE EVERY-STARTPOS ANSWER DIFFERENTIAL
# =========================================================================
# tests/codegen/searchpin_driver.c, `on` the default build and `off` the
# triple deny: search, match and match_caps at every startpos 0..n+1, the
# verdict and caps[0] compared. The subjects include every fixed ill-formed
# token the design's pool keeps (§5.5, SL-E4: lone continuation, truncated
# leads, FF, overlongs, a surrogate, > U+10FFFF, F5, lead runs) around
# well-formed characters.
cat > "$WORKDIR/subjects" <<'EOF'

a
abcd
xabcdx abcd
aab
hello world
x*y xxy y
\x00a\x00
\xc3a
\xc3\xc3\xa9
\xe2\x82a
\xf0\x9f\x98a
\xed\xa0\x80a
\xc0\x80a
\xc3
\xe2\x82
\x80
\xff\xfea
\xf5\x80\x80\x80a
\xf4\x90\x80\x80a
\xe0\x80\x80a
\xc3\xa9\xc3\xa9x
a\xc3a\xe2\x82\xacb
\x80\xc3\xa9z\xf0\x9f\x98\x80
EOF
# D172 S3 (job 600): `abcd` is a cover artifact by default now (still a
# differential: cover against the reverse pass), so `ab|cd` joins as the third
# end-minus-width row the floor counts (not a window: no cover).
DIFF_ROWS='byte	abcd
byte	ab|cd
byte	\w+
byte	(?s).
byte	[a-z]+\d*
byte	a|bc
byte	x*y
byte	(?!a)
byte	a*
utf8	.
utf8	\p{L}+
utf8	[a-zé]+
utf8	é
utf8	.x?
utf8	\w+
utf8	é(?:x$)?'
dbad=""; dn=0; dland=0; demw=0
while IFS=$'\t' read -r enc pat; do
    [ -n "$pat" ] || continue
    dn=$((dn + 1))
    d="$WORKDIR/dv"; rm -rf "$d"; mkdir -p "$d"
    emit "$d/on.c" on "$pat" -e "$enc" || { dbad="$dbad [$enc '$pat': default refused]"; continue; }
    # shellcheck disable=SC2086
    emit "$d/off.c" off "$pat" -e "$enc" $DENY3 || { dbad="$dbad [$enc '$pat': triple deny refused]"; continue; }
    case "$(stamp "$d/on.c" ON)" in landing) dland=$((dland + 1)) ;; end-minus-width) demw=$((demw + 1)) ;; esac
    [ "$(stamp "$d/off.c" OFF)" = reverse-pass ] || [ "$(stamp "$d/off.c" OFF)" = attempt-start ] \
        || dbad="$dbad [$enc '$pat': the reference stamps '$(stamp "$d/off.c" OFF)']"
    if ! gen_cc "start-landing $pat" $CC $GENCFLAGS -I"$d" -o "$d/drv" \
            "$SCRIPT_DIR/searchpin_driver.c" "$d/on.c" "$d/off.c" > "$d/cc.log" 2>&1; then
        dbad="$dbad [$enc '$pat': driver did not build]"; continue
    fi
    out="$(gen_run "start-landing $pat" "$d/drv" < "$WORKDIR/subjects" 2>&1)" \
        || dbad="$dbad [$enc '$pat': DISAGREES: $(printf '%s' "$out" | head -2 | tr '\n' ' ')]"
done <<EOF
$DIFF_ROWS
EOF
if [ -n "$dbad" ]; then
    bad "§5 the default and triple-deny builds disagree:$dbad"
elif [ "$dland" -lt 7 ] || [ "$demw" -lt 3 ]; then
    bad "§5 the differential reached only $dland landing and $demw end-minus-width artifacts (floors 7 / 3): the witnesses moved off the rows"
else
    ok "§5 $dn patterns ($dland landing, $demw end-minus-width) answer IDENTICALLY to the triple-deny build's reverse pass at every startpos of $(wc -l < "$WORKDIR/subjects") subjects with every fixed ill-formed token — verdict and caps[0] of search, match and match_caps"
fi

# =========================================================================
# §6 THE ORACLE-VERIFIED CORPUS FILE REACHES THE GUARD
# =========================================================================
# tests/utf8/landing_illformed.rxt's cells are libpcre2's (its generator,
# gen_landing_illformed.py) and test-corpus runs them. Its REACH is held here:
# every block's pattern takes `landing` WITH the guard under utf8, or the file
# stopped testing what it was generated for.
LF="$ROOT_DIR/tests/utf8/landing_illformed.rxt"
nb=0; rbad=""
while IFS= read -r lp; do
    nb=$((nb + 1))
    emit "$WORKDIR/lf.c" rx "$lp" -e utf8 || { rbad="$rbad ['$lp': refused]"; continue; }
    [ "$(stamp "$WORKDIR/lf.c")" = landing ] && has_guard "$WORKDIR/lf.c" || rbad="$rbad ['$lp': $(stamp "$WORKDIR/lf.c"), guard=$(has_guard "$WORKDIR/lf.c" && echo y || echo n)]"
done < <(sed -n 's/^pattern //p' "$LF")
ncell="$(grep -cE '^(ms|ns) ' "$LF")"
if [ "$nb" -lt 4 ] || [ "$ncell" -lt 100 ] || [ -n "$rbad" ]; then
    bad "§6 landing_illformed.rxt: $nb blocks / $ncell cells (floors 4 / 100); off the guarded landing:$rbad"
else
    ok "§6 landing_illformed.rxt: all $nb blocks take the guarded landing ($ncell libpcre2-generated cells, run by test-corpus)"
fi

# =========================================================================
# §H THE STANDING HOSTILE CELL
# =========================================================================
# 1 MiB of one lead byte, then `a`: one match, at (1048576, 1048577). The
# linear skip takes milliseconds; revision 1's re-entering restart took
# ~13 min (start_landing.md §2.5.5). The 10 s bound is CHOSEN with three
# orders of margin each way (§8.4), and a firing bound is the finding.
K=1048576
hbad=""; hn=0
for pat in . '\p{L}+'; do
    d="$WORKDIR/h"; rm -rf "$d"; mkdir -p "$d"
    emit "$d/on.c" on "$pat" -e utf8 || { hbad="$hbad ['$pat': refused]"; continue; }
    [ "$(stamp "$d/on.c" ON)" = landing ] && has_guard "$d/on.c" || { hbad="$hbad ['$pat' is not the guarded landing]"; continue; }
    gen_cc "start-landing hostile" $CC $GENCFLAGS -O2 -I"$d" -o "$d/h" \
        "$SCRIPT_DIR/landing_hostile_driver.c" "$d/on.c" > "$d/cc.log" 2>&1 \
        || { hbad="$hbad ['$pat': driver did not build]"; continue; }
    for lead in c3 e2 f0; do
        hn=$((hn + 1))
        got="$("$TIMEOUT_BIN" 10 "$d/h" "$lead" "$K")"; rc=$?
        if [ "$rc" -eq 124 ]; then hbad="$hbad ['$pat' over 1 MiB of 0x$lead: the 10 s bound FIRED — a quadratic guard]"
        elif [ "$got" != "1 $K $((K + 1))" ]; then hbad="$hbad ['$pat' over 0x$lead: '$got', expected '1 $K $((K + 1))']"; fi
    done
done
[ -z "$hbad" ] && [ "$hn" -eq 6 ] \
    && ok "§H the hostile cell: utf8 '.' and '\\p{L}+' find one match over 1 MiB of each of three lead bytes then 'a', inside the 10 s bound" \
    || bad "§H hostile cell ($hn runs):$hbad"

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
