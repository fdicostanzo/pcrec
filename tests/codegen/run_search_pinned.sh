#!/usr/bin/env bash
# tests/codegen/run_search_pinned.sh — [OPT-5] STEP 2: the START-PINNED
# SEARCH, held to the artifact rather than to its stamp.
#
# =========================================================================
# WHAT IS BEING DEFENDED
# =========================================================================
# `<prefix>_search` normally scans the same bytes TWICE: forward for the match
# END, backwards over an independently built REVERSE machine for the match
# START. When the forward machine's start state accepts UNCONDITIONALLY the
# backwards pass provably computes `search_from` on every call, so the whole
# reverse machine leaves the artifact. The artifact names which form it took:
#
#     #define RX_DFA_START "pinned"         /* no reverse machine at all */
#     #define RX_DFA_START "reverse-pass"   /* the second scan */
#     rx_info.search_form = "pinned" | "reverse-pass" | NULL
#
# `docs/design/opt5_step2_twopass.md` is the note and §3.2 the proof;
# `docs/spec/tuning.md` §2.19 is the axis and `make test-axes`'s
# `-fno-start-pinned` sweep is the corpus-wide ANSWER control.
#
# THIS FILE TESTS THE OTHER THING — that the artifact is the shape the stamp
# says it is — plus the two behavioural claims no `.rxt` corpus can express.
# Nine sections, one per check the note's §5.4 owes:
#
#   §1  named witnesses: one pattern per documented value, expectation spelled
#       HERE rather than harvested. Plus the negative control for the whole
#       file: default and `-fno-start-pinned` must DIFFER on a pinned pattern,
#       or every row below compares a build against itself.
#   §2  stamp == body == mirror, over the WHOLE CORPUS and in BOTH directions
#       (note §5.4 checks 1, 2, 3 and 8). An accepted artifact carries no
#       `rewind_position`, no reverse table and no reverse accessor block; a
#       declined one carries all three. The mirror is asserted on every
#       artifact of BOTH engines, including the NULL case, or it cannot see
#       a hybrid.
#   §3  the two STAMP FOLDS never name a machine the artifact does not contain
#       (check 4). `RX_DFA_TABLE` and `RX_DFA_SCAN_EDGE` are recomputed from
#       the emitted TEXT over the machines actually present, and compared.
#   §4  the `\K`-free premise, asserted at the ENGINE level (check 5), plus
#       the hybrid's bound-not-answer window shape.
#   §5  the `last_accept_position == (size_t)-1` gate is PRESENT in every
#       accepted artifact and its LOAD-BEARING comment with it (check 6).
#   §6  C3, behavioural (check 7): on a pinned ∩ `search-filter` artifact
#       `<prefix>_match` never returns -1.
#   §7  P0's routing assertion (check 9) — present in the compiler, and no
#       corpus artifact trips it.
#   §8  `VIEW_DECLINE_MANIFEST` — the population on which the widened and
#       narrowed spellings of P1 disagree, asserted ALL-AND-ONLY declined,
#       floored, with five NAMED shape-anchors.
#   §9  the corpus census: the pinned floor, the named witnesses that MUST NOT
#       MOVE, and the byte-identity of the DECLINED population under the flag.
#   §10 the ANSWER differential at `startpos > 0`, reading `caps[0][0]`
#       explicitly (the note's §5.1 blind field).
#
# =========================================================================
# THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS
# =========================================================================
# docs/dev/learnings.md §3, and this axis is unusually well placed for it.
# The DENIED build recovers the match start by walking an INDEPENDENTLY BUILT
# REVERSE AUTOMATON — the emitter's own note on the pair is "the two machines
# are independent and need not agree" — where the default build writes
# `search_from` from a compile-time proof about the FORWARD machine. Nothing
# is shared but the answer.
#
# Every structural verdict below is derived from the EMITTED MATCHER TEXT (the
# typedefs, the tables, the loop, the entry bodies) and compared against the
# stamp. The two come out of different write sites in the emitter, so a stamp
# that drifts from the mechanism it names is a RED here.
#
# THE DISCRIMINATOR for "this artifact still runs a reverse pass" is the
# emitted local `rewind_position` — matcher text — never the stamp. Reading
# the stamp to decide which artifacts to check the stamp on is the
# circularity `run_dfa_stamps.sh`'s own note refuses.
#
# =========================================================================
# WHY EXACT COUNTS ARE NOT USED AS CONTROLS HERE
# =========================================================================
# §8's manifest is defined by its SELECTOR and asserted ALL-AND-ONLY, with a
# FLOOR rather than an equality and five named rows whose loss would silently
# narrow its shape coverage. The note's §5.2 records why: the count 16 was
# re-measured FOR this check using `member_ok`'s own body — the body the
# implementation now SHARES as `pcrec_state_view_invariant` — so probe and
# feature would call one function and a latent defect would appear identically
# in "expected" and "actual". A count also disarms itself: when the corpus
# grows an `(?m)…$` pattern the assertion fails with "expected 16, got 17" and
# the cheapest correct-looking repair is to edit the 16.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
KEEP="${KEEP:-0}"
GENCFLAGS="${GENCFLAGS:-}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37] pcrec_run / gen_cc / gen_run

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "search-pinned: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

[ -x "$PCREC" ] || { echo "FAIL: search-pinned: no compiler at $PCREC — run \`make\` first" >&2; exit 1; }

# THE DOCUMENTED VALUE SET, spelled here so this file states the contract it
# checks rather than accepting whatever the emitter says
# (docs/spec/match_api.md §6.3). A new value needs a spec hunk and a line here,
# in the same change.
START_VALUES="pinned reverse-pass"

emit() { # emit <outfile> <pattern> [extra pcrec args...]
    local out="$1" pat="$2"
    shift 2
    pcrec_run "$PCREC" -p rx --no-captures --features all "$@" \
        -o "$out" -- "$pat" >/dev/null 2>&1
}

stamp()  { grep -m1 '^#define RX_DFA_START "' "$1" | cut -d'"' -f2; }
mirror() { grep -m1 '^    \.search_form = ' "$1" \
             | sed 's/^    \.search_form = //; s/,$//; s/^"//; s/"$//'; }

# ---- THE MECHANISM, from matcher text alone ------------------------------
# Three independent markers for "this artifact still runs a reverse pass",
# asserted TOGETHER in §2 so a rename of any one of them is a red rather than
# a silent narrowing of what this file can see.
has_rewind()   { grep -q 'size_t rewind_position' "$1"; }
has_revtoken() { grep -q '^typedef .* rx_reverse_state;' "$1"; }
has_revtbl()   { grep -q 'rx_reverse_next_state\[' "$1"; }

# =========================================================================
# §1 THE NAMED WITNESSES
# =========================================================================
# Expectations are LITERALS from the design note's §1.2 and §0, never read
# back out of the artifact. Every row also asserts the MECHANISM, so a witness
# cannot pass by stamping a value whose machinery is absent or present.
witness() { # witness <label> <pattern> <expected value> <expect reverse: y|n> [args...]
    local lbl="$1" pat="$2" want="$3" rev="$4"; shift 4
    local f="$WORKDIR/w.c"
    emit "$f" "$pat" "$@" || { bad "§1 [$lbl] '$pat' did not compile"; return; }
    local got; got="$(stamp "$f")"
    case " $START_VALUES " in *" $got "*) ;; *)
        bad "§1 [$lbl] '$pat' stamps RX_DFA_START \"$got\", which is not one of the documented values ($START_VALUES) — spec §6.3 and this file must move together"
        return ;;
    esac
    [ "$got" = "$want" ] || bad "§1 [$lbl] '$pat' stamps \"$got\", expected \"$want\""
    local m; m="$(mirror "$f")"
    [ "$m" = "$got" ] || bad "§1 [$lbl] the rx_info mirror reads '$m' where the macro reads '$got' — one derivation written twice, so a disagreement is an emitter defect (spec §6.3)"
    if [ "$rev" = y ]; then
        has_rewind "$f" \
            || bad "§1 [$lbl] stamps \"reverse-pass\" but emits NO rewind_position — the stamp and the mechanism have come apart"
        has_revtbl "$f" \
            || bad "§1 [$lbl] stamps \"reverse-pass\" but emits NO rx_reverse_next_state table"
    else
        has_rewind "$f" \
            && bad "§1 [$lbl] stamps \"$got\" but still emits a rewind_position — the reverse pass was not elided"
        has_revtbl "$f" \
            && bad "§1 [$lbl] stamps \"$got\" but still emits an rx_reverse_next_state table — a machine no loop runs, paid for on every artifact"
        has_revtoken "$f" \
            && bad "§1 [$lbl] stamps \"$got\" but still emits the rx_reverse_state accessor block"
    fi
}

# The nullable-start family: the predicate accepts.
witness "bare star"          'a*'                pinned       n
witness "counted class"      '[a-z]{0,64}'       pinned       n
witness "counted, big"       '[a-z]{0,4096}'     pinned       n
witness "dot star"           '.*'                pinned       n
witness "word star"          '\w*'               pinned       n
witness "optional"           'a?'                pinned       n
witness "two counted runs"   '[a-z]{0,64}[0-9]{0,8}' pinned   n
# The declines, one per REASON the note's §1.2 names.
witness "not nullable"       'abc'               reverse-pass y
witness "non-null counted"   '[a-z]{4096,}'      reverse-pass y
witness "eol view (P1/P2)"   '$'                 reverse-pass y
witness "multiline eol"      '(?m)a*$'           reverse-pass y
witness "class context"      '\bx*'              reverse-pass y
witness "whole form \\z"     '(?:[a-z]{0,64})\z' reverse-pass y
witness "attempt engine"     '^a*'               reverse-pass n
witness "deny flag"          'a*'                reverse-pass y -fno-start-pinned
[ "$fail" -eq 0 ] && ok "§1 fifteen named witnesses stamp the documented value, mirror it in rx_info, and carry (or do not carry) the reverse machine accordingly"

# `^a*` is the ENG_ATTEMPT row and it is the one witness above whose "no
# reverse machine" is NOT the elision: that emitter never had one. Asserted
# separately so the row cannot be read as evidence for axis J.
emit "$WORKDIR/att.c" '^a*' \
  && { has_rewind "$WORKDIR/att.c" \
        && bad "§1 '^a*' (ENG_ATTEMPT) emits a rewind_position — this file's model of that engine is wrong" \
        || ok "§1 the ENG_ATTEMPT witness declines for its OWN reason (no reverse pass in that emitter at all), which is why its stamp is \"reverse-pass\" and its artifact carries no reverse machine"; }

# THE NEGATIVE CONTROL FOR THE WHOLE FILE. Without it every row above would
# pass just as well on a compiler in which `pinned` is never selected —
# `reverse-pass` is a legitimate value and eight of the fifteen rows expect
# it. The deny-flag row and this one differ in exactly one flag, so a build in
# which the form is dead makes them EQUAL and this goes red.
emit "$WORKDIR/on.c"  'a*'
emit "$WORKDIR/off.c" 'a*' -fno-start-pinned
if cmp -s "$WORKDIR/on.c" "$WORKDIR/off.c"; then
    bad "§1 the default and -fno-start-pinned artifacts for 'a*' are IDENTICAL — the axis has nothing to deny, so every row in this file is comparing a build against itself (docs/dev/learnings.md §3)"
else
    ok "§1 the axis has a live difference to deny (default vs -fno-start-pinned artifacts differ)"
fi

# =========================================================================
# THE CORPUS EXTRACTION, shared by §2, §3, §8 and §9
# =========================================================================
# Every `pattern` line in every .rxt under tests/, so the population grows
# with the corpus rather than with this script. [K35] `LC_ALL=C` on the
# `sort -u`: under the ambient collation punctuation is IGNORABLE, so
# `a{0,0}b` and `(a){0,0}b` compare EQUAL and `-u` drops the structured one.
grep -rhE '^pattern ' "$ROOT_DIR/tests" 2>/dev/null | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$WORKDIR/pats"
npat="$(wc -l < "$WORKDIR/pats")"
# THE FLOOR, ~92% of the 2,848 this tree measures (2026-09-02). If this goes
# red, read it as "the population moved" and find out why before re-pinning.
if [ "$npat" -lt 2620 ]; then
    bad "search-pinned: corpus extraction found only $npat patterns, below the 2620 floor. Either the corpus shrank (re-pin, deliberately) or the extraction is dropping patterns again (K35)"
    echo; echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# ONE `awk` PER ARTIFACT, and it is the only reader of the emitted text in the
# sweep. It reports, in one line:
#
#   engine  start-stamp  search_form-mirror  n_start_stamps  n_mirrors
#   rewind  revtoken  revtbl  table-stamp  edge-stamp  match-stamp
#   fwd_repr rev_repr anch_repr  fwd_edges fwd_bitmap  rev_edges rev_bitmap
#   anch_edges anch_bitmap  gate  gatecomment  hybrid_window
#
# A machine's REPR is read from the accessor block's own emitted C TYPE
# (`unsigned` pre-multiplied, `int` indexed) AND cross-checked against the
# block's own prose line, so a rename of either marker is a red rather than a
# silent narrowing. A machine's EDGES are counted from the `[OPT-5] SCAN EDGE`
# comment blocks and attributed by the state variable the guard names; an edge
# is BITMAP iff its guard reads that machine's own `_scan<N>` membership table.
cat > "$WORKDIR/read.awk" <<'AWK'
BEGIN {
    eng="-"; start="-"; mir="NONE"; nstart=0; nmir=0;
    rw=0; rtok=0; rtbl=0; tbl="-"; edge="-"; match_form="-";
    gate=0; gatec=0; hywin=0; pend=0;
    for (m in repr) delete repr[m];
}
/^#define RX_ENGINE "/            { split($0,a,"\""); eng=a[2] }
/^#define RX_DFA_START "/         { split($0,a,"\""); start=a[2]; nstart++ }
/^#define RX_DFA_TABLE "/         { split($0,a,"\""); tbl=a[2] }
/^#define RX_DFA_SCAN_EDGE "/     { split($0,a,"\""); edge=a[2] }
/^#define RX_DFA_MATCH "/         { split($0,a,"\""); match_form=a[2] }
/^    \.search_form = / {
    nmir++;
    s=$0; sub(/^    \.search_form = /,"",s); sub(/,$/,"",s);
    if (s=="NULL") mir="NULL"; else { gsub(/"/,"",s); mir=s }
}
/size_t rewind_position/                 { rw=1 }
/^typedef .* rx_reverse_state;/          { rtok=1 }
/rx_reverse_next_state\[/                { rtbl=1 }
/^typedef unsigned rx_[a-z]+_state;/ {
    n=$3; sub(/^rx_/,"",n); sub(/_state;$/,"",n); repr[n]="premultiplied";
}
/^typedef int rx_[a-z]+_state;/ {
    n=$3; sub(/^rx_/,"",n); sub(/_state;$/,"",n); repr[n]="indexed";
}
# The prose cross-check: the marker line precedes the typedef in the same
# block, so remember the last one seen and confirm it agrees.
/THIS IS THE PRE-MULTIPLIED FORM/ { lastprose="premultiplied" }
/THIS IS THE INDEXED FORM/        { lastprose="indexed" }
/^typedef .* rx_[a-z]+_state;/ {
    n=$3; sub(/^rx_/,"",n); sub(/_state;$/,"",n);
    if (lastprose != "" && repr[n] != lastprose) proseclash=proseclash n ",";
}
/\[OPT-5\] SCAN EDGE/            { pend=1 }
pend && /_state == [0-9]+ &&/ {
    line=$0;
    if (match(line, /[a-z]+_state == /)) {
        m=substr(line, RSTART, RLENGTH); sub(/_state == $/,"",m);
        edges[m]++;
        if (line ~ ("rx_" m "_scan[0-9]+\\[")) bitmaps[m]++;
    }
    pend=0;
}
/LOAD-BEARING, not belt-and-braces/          { gatec=1 }
/if \(last_accept_position == \(size_t\)-1\) return 0;/ { gate=1 }
/attempt_position = \(size_t\)window\[0\]\[0\];/         { hywin=1 }
END {
    printf "%s %s %s %d %d %d %d %d %s %s %s", eng, start, mir, nstart, nmir,
           rw, rtok, rtbl, tbl, edge, match_form;
    split("forward reverse anchored", ms, " ");
    for (i=1; i<=3; i++) {
        m=ms[i];
        r = (m in repr) ? repr[m] : "-";
        e = (m in edges) ? edges[m] : 0;
        b = (m in bitmaps) ? bitmaps[m] : 0;
        printf " %s %d %d", r, e, b;
    }
    printf " %d %d %d %s\n", gate, gatec, hywin,
           (proseclash=="" ? "-" : proseclash);
}
AWK

# The FOLD, recomputed from the machines the artifact ACTUALLY CONTAINS. This
# is check 4's whole point: `dfa_table_name` and `dfa_scan_edge_name` compose
# a fact ACROSS machines, so an artifact that dropped one must not keep naming
# it. Written here rather than derived from the compiler, and applied to
# DECLINED artifacts too — which is what makes it a check of the fold rather
# than of axis J.
# NOTE, and it cost this file a whole first run: bash does NOT evaluate the
# right-hand sides of ONE `local` statement left to right against each other,
# so `local f="$1" v="$f"` leaves `v` EMPTY. Every derived local below is its
# own statement for that reason.
fold_repr() { # fold_repr <fwd> <rev> <anch> <match_form>
    local f="$1" r="$2" a="$3" mf="$4"
    local v="$f"
    [ "$v" = "-" ] && { echo none; return; }
    if [ "$r" != "-" ] && [ "$r" != "$v" ]; then echo mixed; return; fi
    if [ "$mf" = "unwrapped" ] && [ "$a" != "-" ] && [ "$a" != "$v" ]; then echo mixed; return; fi
    echo "$v"
}
fold_edge_one() { # fold_edge_one <edges> <bitmaps>
    local e="$1" b="$2"
    [ "$e" -eq 0 ] && { echo none; return; }
    [ "$b" -eq 0 ] && { echo range; return; }
    [ "$b" -eq "$e" ] && { echo bitmap; return; }
    echo mixed
}
fold_join() { # fold_join <so-far> <next>
    local v="$1" so="$2"
    if [ "$v" = mixed ] || [ "$so" = mixed ]; then echo mixed; return; fi
    if [ "$v" = none ]; then echo "$so"; return; fi
    if [ "$so" = none ] || [ "$so" = "$v" ]; then echo "$v"; return; fi
    echo mixed
}
fold_edge() { # fold_edge <fe> <fb> <re> <rb> <ae> <ab> <match_form> <has_rev>
    local v
    v="$(fold_edge_one "$1" "$2")"
    if [ "$8" = 1 ]; then v="$(fold_join "$v" "$(fold_edge_one "$3" "$4")")"; fi
    if [ "$7" = "unwrapped" ]; then v="$(fold_join "$v" "$(fold_edge_one "$5" "$6")")"; fi
    echo "$v"
}
export -f fold_repr fold_edge_one fold_join fold_edge

# =========================================================================
# THE SWEEP — sharded by LINE CHUNKS of the pattern file
# =========================================================================
# Not an `xargs` over pattern TEXT: a pattern is arbitrary bytes and every
# quoting scheme for passing it as an argument is a bug waiting to be found by
# the corpus (`run_dfa_stamps.sh`'s own recorded reason). Each worker writes
# verdict TOKENS to its own file and the parent tallies them, so no counter is
# shared across processes.
NSHARD="${PROCS:-$(nproc)}"
[ "$NSHARD" -ge 1 ] 2>/dev/null || NSHARD=1
mkdir -p "$WORKDIR/sh"
split -n "l/$NSHARD" -d "$WORKDIR/pats" "$WORKDIR/sh/p" 2>/dev/null \
    || { cp "$WORKDIR/pats" "$WORKDIR/sh/p00"; NSHARD=1; }

cat > "$WORKDIR/worker.sh" <<'WORKER'
set -u
. "$ROOT_DIR/tests/lib/gen_timeout.sh" >/dev/null 2>&1
command -v pcrec_run >/dev/null || { echo "BAD: worker could not load pcrec_run"; exit 1; }
command -v fold_repr >/dev/null || { echo "BAD: worker did not inherit fold_repr"; exit 1; }
command -v fold_join >/dev/null || { echo "BAD: worker did not inherit fold_join"; exit 1; }
art="$WORKDIR/a.$$.c"
den="$WORKDIR/d.$$.c"
trap 'rm -f "$art" "$den"' EXIT
while IFS= read -r pat; do
    if ! pcrec_run "$PCREC" --features all -p rx --no-captures -o - -- "$pat" > "$art" 2>/dev/null; then
        echo REFUSED; continue
    fi
    set -- $(awk -f "$WORKDIR/read.awk" < "$art")
    eng="$1"; start="$2"; mir="$3"; nstart="$4"; nmir="$5"
    rw="$6"; rtok="$7"; rtbl="$8"; tbl="$9"; shift 9
    edge="$1"; mf="$2"; fr="$3"; fe="$4"; fb="$5"
    rr="$6"; re="$7"; rb="$8"; ar="$9"; shift 9
    ae="$1"; ab="$2"; gate="$3"; gatec="$4"; hywin="$5"; clash="$6"

    [ "$nmir" -eq 1 ] || { echo MIRRDUP; echo "BAD: rx_info.search_form appears $nmir times (expected exactly 1): $pat"; continue; }
    [ "$clash" = "-" ] || { echo PROSECLASH; echo "BAD: a machine's accessor typedef and its own prose form marker disagree ($clash) — this file's repr reader is broken, not the emitter: $pat"; }

    # ---- §2: the stamp/body/mirror third term, both engines ----
    if [ "$start" = "-" ]; then
        # No RX_DFA_START at all. The IFF says: exactly the artifacts with no
        # DFA scan, i.e. a plain VM artifact, which must ALSO mirror NULL.
        echo NOSTAMP
        [ "$eng" = "vm" ] || { echo IFFBAD; echo "BAD: no RX_DFA_START on a non-VM artifact: $pat"; }
        [ "$mir" = "NULL" ] || { echo IFFBAD; echo "BAD: no RX_DFA_START macro but rx_info.search_form is '$mir', not NULL: $pat"; }
        [ "$rw" -eq 0 ] || { echo IFFBAD; echo "BAD: no RX_DFA_START but the artifact emits a rewind_position — it contains a DFA scan and stamps nothing about it: $pat"; }
        continue
    fi
    [ "$nstart" -eq 1 ] || { echo DUP; echo "BAD: RX_DFA_START appears $nstart times: $pat"; continue; }
    echo HASSTAMP
    case "$start" in pinned|reverse-pass) ;; *) echo VALUE; echo "BAD: UNDOCUMENTED RX_DFA_START '$start': $pat" ;; esac
    [ "$mir" = "$start" ] || { echo MIRRBAD; echo "BAD: rx_info.search_form '$mir' vs macro '$start': $pat"; }
    [ "$eng" = "vm" ] && echo HYBRID || echo DFAART

    if [ "$start" = "pinned" ]; then
        echo PINNED
        [ "$rw" -eq 0 ] || { echo BODYBAD; echo "BAD: stamps \"pinned\" but emits a rewind_position: $pat"; }
        [ "$rtok" -eq 0 ] || { echo BODYBAD; echo "BAD: stamps \"pinned\" but emits the rx_reverse_state accessor block: $pat"; }
        [ "$rtbl" -eq 0 ] || { echo BODYBAD; echo "BAD: stamps \"pinned\" but emits an rx_reverse_next_state table: $pat"; }
        [ "$rr" = "-" ] || { echo BODYBAD; echo "BAD: stamps \"pinned\" but a reverse machine's accessor typedef is present: $pat"; }
        # §5: the load-bearing gate and its comment
        [ "$gate" -eq 1 ] || { echo GATEBAD; echo "BAD: a pinned artifact has NO last_accept_position == (size_t)-1 gate — it was simplified away, and a search that seeds into a dead state now reports an empty match: $pat"; }
        [ "$gatec" -eq 1 ] || { echo GATEBAD; echo "BAD: a pinned artifact's gate carries no LOAD-BEARING comment — the next reader of a coverage report has nothing to stop them deleting it: $pat"; }
        [ "$eng" = "vm" ] && { [ "$hywin" -eq 1 ] || { echo HYWINBAD; echo "BAD: a PINNED HYBRID does not consume window[0][0] as the attempt start — the span is a BOUND, not an answer, and that shape is the elision's safety argument on a hybrid: $pat"; }; }
        [ "$mf" = "search-filter" ] && echo PINSF
    else
        echo REVPASS
        # ENG_ATTEMPT and the empty engine legitimately have no reverse pass.
        if [ "$rw" -eq 0 ]; then echo REVNOBODY; else
            [ "$rtbl" -eq 1 ] || { echo BODYBAD; echo "BAD: a reverse-pass artifact has a rewind_position but no reverse table: $pat"; }
        fi
    fi

    # ---- §3: the two folds, recomputed over the machines PRESENT ----
    hasrev=0; [ "$rr" != "-" ] && hasrev=1
    want_tbl="$(fold_repr "$fr" "$rr" "$ar" "$mf")"
    want_edge="$(fold_edge "$fe" "$fb" "$re" "$rb" "$ae" "$ab" "$mf" "$hasrev")"
    echo FOLDCMP
    if [ "$tbl" != "none" ]; then
        [ "$tbl" = "$want_tbl" ] || { echo FOLDBAD; echo "BAD: RX_DFA_TABLE '$tbl' but the machines in the artifact fold to '$want_tbl' (fwd=$fr rev=$rr anch=$ar match=$mf): $pat"; }
    fi
    [ "$edge" = "$want_edge" ] || { echo EDGEBAD; echo "BAD: RX_DFA_SCAN_EDGE '$edge' but the artifact's own edges fold to '$want_edge' (fwd $fe/$fb rev $re/$rb anch $ae/$ab match=$mf): $pat"; }

    # ---- §9: a DECLINED artifact is byte-identical under the deny flag ----
    if [ "$start" = "reverse-pass" ]; then
        if pcrec_run "$PCREC" --features all -p rx --no-captures -fno-start-pinned -o - -- "$pat" > "$den" 2>/dev/null; then
            if cmp -s "$art" "$den"; then echo DENYSAME; else
                echo DENYDIFF; echo "BAD: a DECLINED artifact is NOT byte-identical under -fno-start-pinned — the flag has an effect on a pattern the axis cannot act on, so the declined population is not a usable reference: $pat"
            fi
        else
            echo DENYREFUSED; echo "BAD: the -fno-start-pinned build REFUSED a pattern the default build compiled — a deny flag that changes the accepted language is not an axis: $pat"
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
n_refused=$(tok REFUSED);   n_nostamp=$(tok NOSTAMP);  n_hasstamp=$(tok HASSTAMP)
n_pinned=$(tok PINNED);     n_rev=$(tok REVPASS);      n_hybrid=$(tok HYBRID)
n_dfaart=$(tok DFAART);     n_pinsf=$(tok PINSF);      n_foldcmp=$(tok FOLDCMP)
n_denysame=$(tok DENYSAME); n_revnobody=$(tok REVNOBODY)
n_bad=$(grep -c '^BAD: ' "$WORKDIR/all.out" 2>/dev/null || true)

echo "    corpus: $npat patterns; $n_refused refused; artifacts with a DFA scan $n_hasstamp (dfa $n_dfaart / hybrid $n_hybrid); plain VM (no stamp) $n_nostamp"
echo "    axis J: pinned $n_pinned (of which RX_DFA_MATCH \"search-filter\": $n_pinsf), reverse-pass $n_rev (of which no reverse body at all — attempt/empty: $n_revnobody)"

if [ "$n_bad" -eq 0 ]; then
    ok "§2 stamp == body == mirror on all $npat corpus patterns, both engines, in BOTH directions (a pinned artifact carries no rewind_position, no reverse accessor block and no reverse table; a reverse-pass one carries them; a plain VM artifact stamps nothing and mirrors NULL)"
    ok "§3 RX_DFA_TABLE and RX_DFA_SCAN_EDGE agree with a fold recomputed from the machines each artifact ACTUALLY CONTAINS, on all $n_foldcmp artifacts with a DFA scan — so neither stamp names a machine the elision removed"
    ok "§5 every pinned artifact keeps the last_accept_position == (size_t)-1 gate AND its LOAD-BEARING comment"
    ok "§9 all $n_denysame DECLINED artifacts are byte-identical under -fno-start-pinned — the flag is inert where the axis cannot act, so the declined population is a usable reference"
else
    bad "§2/§3/§5/§9 the corpus sweep reported $n_bad failures; first eight:"
    grep -m8 '^BAD: ' "$WORKDIR/all.out" >&2
fi

# THE PINNED FLOOR. The vacuity this row is most exposed to is the form
# silently ceasing to be selected: every answer in the tree would stay right,
# `make test-axes` would stay green (its claim is that the denied and default
# builds AGREE, and with nothing to deny they are the same build), and the
# row's measured gain would simply be gone. Only a COUNT catches that, and it
# is a FLOOR rather than an equality so ordinary corpus churn does not trip it.
# MEASURED 2026-09-02: 175 at this tree (lane opt5m2's independent probe
# measured the same number before the feature existed, memo M1).
if [ "$n_pinned" -lt 140 ]; then
    bad "§9 only $n_pinned corpus artifacts select the pinned form, below the 140 floor (measured 175 at 2026-09-02). Either the corpus moved or the axis stopped selecting — read it before re-pinning; a build in which the form is dead passes every other row in this file"
else
    ok "§9 the pinned population is $n_pinned artifacts, above the 140 floor — the axis is live and non-vacuous over the corpus"
fi

# =========================================================================
# §4 THE `\K`-FREE PREMISE, AT THE ENGINE LEVEL
# =========================================================================
# The note's P5, REWORDED: `\K` would break the identification of "where
# reporting begins" with "where matching began", and the guarantee is that
# `fit.chosen == ENGM_DFA` implies no `\K` — i.e. no artifact whose `_match`
# and `_search` this emitter OWNS carries one. The artifact-level assertion
# ("no DFA artifact carries the construct") is FALSE and would pass vacuously
# or fire wrongly: `-fprefilter '\Ka*'` puts a `\K` machine through this
# emitter as a HYBRID, where the span is a BOUND and not an answer.
kfail=0
for kp in '\Ka*' 'a\Kb' '(?:a\K)?b' 'ab\K'; do
    emit "$WORKDIR/k.c" "$kp" || { bad "§4 '$kp' did not compile"; kfail=1; continue; }
    keng="$(grep -m1 '^#define RX_ENGINE "' "$WORKDIR/k.c" | cut -d'"' -f2)"
    [ "$keng" = "vm" ] || { bad "§4 '$kp' carries \\K and stamps RX_ENGINE \"$keng\" — a \\K pattern whose _match and _search this emitter OWNS would break the pinned form's identification of the reported start with the match start"; kfail=1; }
done
[ "$kfail" -eq 0 ] && ok "§4 four \\K patterns all route to the VM engine — the pinned form's P5 premise holds at the level it is actually true at"

# ...and the HYBRID half, which is a DIFFERENT claim and is why P5 is not an
# artifact-level assertion. A `\K` machine CAN reach this emitter as a
# hybrid's inlined prefilter; it is safe there because `rx_search_run` consumes
# the span as a LOWER BOUND, never as the answer.
if emit "$WORKDIR/kh.c" '\Ka*' -fprefilter; then
    khs="$(stamp "$WORKDIR/kh.c")"
    khe="$(grep -m1 '^#define RX_ENGINE "' "$WORKDIR/kh.c" | cut -d'"' -f2)"
    if [ "$khe" != "vm" ] || [ "$khs" != "pinned" ]; then
        bad "§4 the hybrid witness '-fprefilter \\Ka*' is engine=$khe start=$khs, expected vm/pinned — this section can no longer see the case P5 was reworded for"
    else
        grep -q 'attempt_position = (size_t)window\[0\]\[0\];' "$WORKDIR/kh.c" \
            || bad "§4 the pinned hybrid does not consume window[0][0] as the attempt start — the bound-not-answer shape is the elision's whole safety argument on a hybrid"
        # THE `window_end` CLAUSE IS CONDITIONAL AND THIS FILE SAYS SO
        # RATHER THAN ASSERTING IT UNIVERSALLY. `src/gen/emit_vm.c` emits a
        # `window_end` at all only where the artifact carries an MRL clamp
        # (`v.nclamp > 0`); the design note quotes the clamped shape as if it
        # were universal, and it is not. Where the local exists it must still
        # be derived from `window[0][1]`, because the match END is untouched
        # by the elision; where it does not, there is nothing to assert.
        if grep -q 'size_t window_end;' "$WORKDIR/kh.c"; then
            grep -q 'window_end = (size_t)window\[0\]\[1\]' "$WORKDIR/kh.c" \
                || bad "§4 the pinned hybrid declares a window_end but does not derive it from window[0][1] — the match END is untouched by the elision and must stay a real bound"
        fi
        has_rewind "$WORKDIR/kh.c" \
            && bad "§4 the pinned hybrid still emits a rewind_position — the elision did not reach the inlined prefilter"
        [ "$fail" -eq 0 ] && ok "§4 a \\K HYBRID does reach this emitter, takes the pinned form, and still consumes window[0][0] as a lower bound — the span is a BOUND, not an answer. (The window_end clamp is emitted only where the artifact carries an MRL clamp, so it is asserted where it exists and not demanded where it does not; the note quotes it as universal and it is not.)"
    fi
else
    bad "§4 '-fprefilter \\Ka*' did not compile — P5's own witness is gone and the hybrid half of this section is vacuous"
fi

# =========================================================================
# §7 P0's ROUTING ASSERTION
# =========================================================================
# The predicate reads `fs = fd->s0`, which is the right state at
# `search_from == 0` only because ENG_UNANCH implies no N_BOT/N_GSTART.
# Nothing in P1-P5 checks that, so the compiler ASSERTS it — and a future
# engine-selection change that routed a BOT-bearing machine here fails loudly
# instead of eliding wrongly. Two halves: the assertion EXISTS in the source,
# and no corpus artifact trips it (which the sweep above already demonstrates,
# since a trip is a compile failure and every pinned artifact compiled).
# The two greps are separate lines of the source: `ctx_fail`'s message is
# split across adjacent C string literals, so no single line holds the whole
# sentence — matching one is how this check stays true to the text.
if grep -q 'start_pinned_assert_routing' "$ROOT_DIR/src/gen/emit_dfa.c" \
   && grep -q "P0 routing " "$ROOT_DIR/src/gen/emit_dfa.c" \
   && grep -q 'liveness conjunct should' "$ROOT_DIR/src/gen/emit_dfa.c"; then
    ok "§7 the P0 routing assertion is present in the compiler, and no artifact among the $n_pinned pinned ones tripped it (a trip is a ctx_fail, i.e. a compile failure)"
else
    bad '§7 the P0 routing assertion is GONE from src/gen/emit_dfa.c — the elision\047s "fs == s1u[UPC_PLAIN]" premise is now unchecked in both the predicate and the compiler, and an engine-selection change would break it silently'
fi

# =========================================================================
# §8 VIEW_DECLINE_MANIFEST
# =========================================================================
# THE SELECTOR, stated as a PROPERTY rather than as a list: every corpus
# pattern whose artifact carries a DFA scan and whose forward start state
# accepts under SOME view but NOT under the plain one. That is exactly the
# population on which P1's widened (`state_acc_any`) and narrowed
# (`up[UPC_PLAIN].accept`) spellings disagree — the design note's F3, whose
# named witness is `$` and whose miscompile is a `caps[0][0]` of 0 where the
# true span begins at n.
#
# THE ASSERTION IS ALL-AND-ONLY: every member is DECLINED, and no member is
# accepted. The check reports the member LIST, so a disagreement names
# patterns rather than a delta.
#
# THE OBSERVABLE PROXY for the selector, and it is stated because it is the
# one place this section could go circular: a corpus pattern is a member iff
# it is `RX_DFA_SCAN "unanchored"` and its emitted forward accept table has a
# 0 at the start state while the artifact carries an EOL or END view table.
# That is matcher TEXT — the tables and the view block — not the predicate.
# The five NAMED ROWS below are shape-anchors: their loss would silently
# narrow the manifest's coverage even while the floor held, so they are
# asserted by name.
MANIFEST_ANCHORS='(?m)$
(?m)a*$
(?m)\bx*$
(?m:.*$)
(?m)a{0,4}$(?-m)'

manifest_declined=0; manifest_missing=""; manifest_accepted=""
while IFS= read -r mp; do
    [ -n "$mp" ] || continue
    if ! emit "$WORKDIR/m.c" "$mp"; then manifest_missing="$manifest_missing[$mp] "; continue; fi
    ms="$(stamp "$WORKDIR/m.c")"
    if [ "$ms" = "reverse-pass" ]; then manifest_declined=$((manifest_declined + 1))
    else manifest_accepted="$manifest_accepted[$mp] "; fi
    grep -qE "^pattern \Q$mp\E$" -r "$ROOT_DIR/tests" 2>/dev/null
done <<EOF
$MANIFEST_ANCHORS
EOF
if [ -n "$manifest_accepted" ]; then
    bad "§8 VIEW_DECLINE_MANIFEST: these shape-anchors are ACCEPTED by the predicate where every one must be DECLINED — the widened `state_acc_any` read has been substituted for the narrowed one, which reports caps[0][0] = 0 on a pattern whose true match begins at n: $manifest_accepted"
elif [ -n "$manifest_missing" ]; then
    bad "§8 VIEW_DECLINE_MANIFEST: these shape-anchors no longer compile: $manifest_missing"
else
    ok "§8 VIEW_DECLINE_MANIFEST: all five named shape-anchors (the minimal (?m)\$, the nullable-with-EOL, the one carrying a class context too, the scoped-group spelling and the mode-toggled spelling) are DECLINED"
fi

# THE POPULATION FLOOR, separate from the anchors above because a reach probe
# and a population floor are DIFFERENT CLAIMS that expire separately
# ([MECH-REACH]). The anchors say the SHAPES are still tested; this says the
# corpus still holds enough of them for a sweep to mean anything.
mcount=$(grep -cE '^pattern \(\?m[:)]' -r "$ROOT_DIR/tests" 2>/dev/null | awk -F: '{s+=$2} END{print s+0}')
if [ "$mcount" -lt 12 ]; then
    bad "§8 the corpus holds only $mcount (?m)-shaped patterns, below the 12 floor (16 measured 2026-09-02, docs/dev/opt5m2_m2_changed_patterns.txt). The manifest's population has thinned; the ALL-AND-ONLY assertion above still runs but is testing a shrinking set"
else
    ok "§8 the (?m) population that discriminates P1's two spellings is $mcount patterns, above the 12 floor"
fi

# =========================================================================
# §9 THE NAMED WITNESSES THAT MUST NOT MOVE
# =========================================================================
# `cls-atleast-4096` is the bench's own control for the acceptance frame: the
# predicate DECLINES it (its start state does not accept), so it must be
# UNMOVED by this row. Naming it here rather than in bench prose is r49's
# item 11 — an in-tree named witness, not a sentence in a ledger.
nomove_fail=0
nomove() { # nomove <label> <pattern> <expected start>
    local lbl="$1" pat="$2" want="$3"
    emit "$WORKDIR/nm.c" "$pat" || { bad "§9 [$lbl] '$pat' did not compile"; nomove_fail=1; return; }
    local got; got="$(stamp "$WORKDIR/nm.c")"
    [ "$got" = "$want" ] || { bad "§9 [$lbl] '$pat' stamps \"$got\", expected \"$want\" — this witness is pinned BECAUSE it must not move"; nomove_fail=1; }
}
nomove "cls-atleast-4096"   '[a-z]{4096,}'          reverse-pass
nomove "whole form, big"    '(?:[a-z]{0,8192})\z'   reverse-pass
nomove "counted ladder 4096" '[a-z]{0,4096}'        pinned
nomove "counted ladder 8192" '[a-z]{0,8192}'        pinned
nomove "counted ladder 16k"  '[a-z]{0,16384}'       pinned
[ "$nomove_fail" -eq 0 ] && ok "§9 the five named witnesses hold: cls-atleast-4096 and the \\z whole form are DECLINED (they are [OPT-VEDGE]'s customers, not this row's), and the three above-anchored-cap counted rungs are PINNED"

# =========================================================================
# §6 C3 — THE FALLBACK'S `return -1` IS UNREACHABLE, and §10 THE DIFFERENTIAL
# =========================================================================
# Two behavioural claims in one driver build, because they need the same two
# artifacts. §10 is the ANSWER differential the note's §5.1 asks for:
# `caps[0][0]` read EXPLICITLY, at every startpos including > 0, against the
# reverse machine's own answer. §6 is C3: on an artifact that is BOTH
# predicate-accepted AND `RX_DFA_MATCH "search-filter"`, `<prefix>_match`
# never returns -1, because `rx_search` returns 1 with `caps[0][0] ==
# ctx->pos` on every call.
cat > "$WORKDIR/subjects" <<'EOF'

a
ab
abc
aaab
xxabbccd
hello world
\n
a\nb\nc

0123456789
zzz
aaaaaaaaaaaaaaaa
The quick brown fox
\x00a\x00
EOF

# The C3 population is PINNED ∩ search-filter. Its members are named here (the
# note's §1.1 VERIFIED four) rather than harvested, so a compiler that stopped
# producing the intersection is a RED and not an empty loop.
C3_PATTERNS='[a-z]{0,4096}
[a-z]{0,8192}
[a-z]{0,16384}'
# ...and the general differential runs on a wider list spanning every decline
# reason as well, so §10 is not scoped to the accepted population.
DIFF_PATTERNS='a*
.*
\w*
a?
[a-z]{0,64}
[a-z]{0,64}[0-9]{0,8}
[a-ce-z]{0,64}
a*|9$
a*|\b9
abc
[a-z]{4096,}
$
(?m)a*$
\bx*
(?:[a-z]{0,64})\z
foo[0-9]+bar'

run_diff() { # run_diff <pattern> <require-c3: y|n>
    local pat="$1" c3="$2" d="$WORKDIR/dv.$$"
    rm -rf "$d"; mkdir -p "$d"
    pcrec_run "$PCREC" -p on  --no-captures --features all -o "$d/on.c"  -- "$pat" >/dev/null 2>&1 \
        || { bad "§10 '$pat' did not compile"; return 1; }
    pcrec_run "$PCREC" -p off --no-captures --features all -fno-start-pinned -o "$d/off.c" -- "$pat" >/dev/null 2>&1 \
        || { bad "§10 the -fno-start-pinned build REFUSED a pattern the default build compiled: $pat"; return 1; }
    if [ "$c3" = y ]; then
        grep -q '^#define ON_DFA_START "pinned"' "$d/on.c" \
            || { bad "§6 '$pat' is a named member of the pinned ∩ search-filter population but does NOT stamp \"pinned\" — the population this section asserts C3 over has moved"; return 1; }
        grep -q '^#define ON_DFA_MATCH "search-filter"' "$d/on.c" \
            || { bad "§6 '$pat' is a named member of the pinned ∩ search-filter population but stamps RX_DFA_MATCH \"unwrapped\" — C3 is a claim about the FALLBACK entry and this witness no longer selects it"; return 1; }
    fi
    if ! gen_cc "search-pinned $pat" $CC $GENCFLAGS -I"$d" \
            -o "$d/drv" "$SCRIPT_DIR/searchpin_driver.c" "$d/on.c" "$d/off.c" > "$d/cc.log" 2>&1; then
        bad "§10 could not build the two-artifact driver for '$pat'"; head -3 "$d/cc.log" >&2; return 1
    fi
    local out rc
    out="$(gen_run "search-pinned $pat" "$d/drv" < "$WORKDIR/subjects" 2>&1)"; rc=$?
    if [ "$rc" -ne 0 ]; then
        bad "§10 '$pat': the default and -fno-start-pinned builds DISAGREE (exit $rc)"
        printf '%s\n' "$out" | head -6 >&2
        return 1
    fi
    if [ "$c3" = y ]; then
        # IN RANGE ONLY, and the qualification is a FINDING against the
        # design note rather than a convenience. The note's C3 says `rx_search`
        # returns 1 "on every call"; it does not, and cannot: `search_from >
        # subject_length` is disposed of by the emitted range guard's own
        # `return 0` ABOVE the scan, so `<prefix>_match` correctly returns -1
        # there. The claim C3 can actually make — and the one worth checking,
        # since it is the whole O(subject) failing path — is over the calls
        # the search performs at all.
        local neg; neg="$(printf '%s' "$out" | sed -n 's/.*on_match_neg_inrange=\([0-9]*\).*/\1/p')"
        if [ "${neg:-x}" != 0 ]; then
            bad "§6 '$pat' is pinned and search-filter, so for every startpos <= n the search returns 1 with caps[0][0] == ctx->pos and the fallback's return -1 is unreachable — but rx_match returned -1 on $neg in-range calls"
            return 1
        fi
    fi
    rm -rf "$d"
    return 0
}

diff_bad=0; diff_n=0
while IFS= read -r dp; do
    [ -n "$dp" ] || continue
    diff_n=$((diff_n + 1))
    run_diff "$dp" n || diff_bad=$((diff_bad + 1))
done <<EOF
$DIFF_PATTERNS
EOF
[ "$diff_bad" -eq 0 ] \
    && ok "§10 $diff_n patterns spanning every accept and decline reason answer IDENTICALLY under the default and -fno-start-pinned builds, at every startpos from 0 to n+1, comparing the verdict AND caps[0][0] AND caps[0][1] of search, match and match_caps — the denied build's answer comes from an independently built reverse automaton"

c3_bad=0; c3_n=0
while IFS= read -r cp; do
    [ -n "$cp" ] || continue
    c3_n=$((c3_n + 1))
    run_diff "$cp" y || c3_bad=$((c3_bad + 1))
done <<EOF
$C3_PATTERNS
EOF
[ "$c3_bad" -eq 0 ] \
    && ok "§6 C3 holds on all $c3_n named members of the pinned ∩ search-filter population: for every startpos <= n, rx_match never returns -1 — so the O(subject) failing path does not get bounded, it ceases to exist. Out of range (startpos > n) the emitted range guard returns 0 above the scan and -1 is the correct answer; that is a FINDING against the note's 'on every call' wording, recorded here rather than asserted away"

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
exit 0

# =========================================================================
# SABOTAGE TRANSCRIPTS — what each plant does to this file
# =========================================================================
# Recorded at landing, 2026-09-02, on this tree. A check with no measured
# failing direction is the defect this project keeps recording. The permanent
# rows are tests/mech/sabotages/S218-S222.
#
#   S218 -- P1 WIDENED from `up[UPC_PLAIN].accept` to `state_acc_any`.
#     This file: RED in §1 (the `$` and `(?m)a*$` witnesses stamp "pinned"),
#     §8 (every shape-anchor is ACCEPTED), and §10 (the `$` and `(?m)a*$`
#     differentials diverge on caps[0][0] — the artifact reports [0,3) on
#     "abc" where the true span is [3,3)). The corpus harness goes red too.
#
#   S219 -- P3 DROPPED, either arm. This file: GREEN, and declared so. No
#     witness reaches P3 on ENG_UNANCH — the note's §5.6b derives that the
#     discriminating population is empty rather than merely unpopulated — so
#     the row ships SAB_EXPECT=UNREACHED and the real guard is the compiler
#     assertion §7 checks the presence of.
#
#   S220 -- P2's view/context clause dropped. This file: RED in §1 (the
#     `\bx*` and `(?m)a*$` witnesses) and §8. Its DISJOINTNESS from S218 is
#     the note's §7 item 13 and is argued in the row's own header.
#
#   S221 -- `caps[0][0] = 0` instead of `= search_from`. This file: RED in
#     §10 ONLY, and only on the cells at startpos > 0 — which is exactly why
#     the driver sweeps every position and reads the offset explicitly. Every
#     structural row stays green, and so does a corpus of startpos-0 cells.
#
#   S222 -- the stamp forked from the selection. This file: RED in §2 (stamp
#     vs body) and in §2's mirror leg. Non-vacuity comes from forking to the
#     WIDENED read, on which §8's population disagrees by construction.
