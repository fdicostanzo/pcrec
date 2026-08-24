#!/usr/bin/env bash
# tests/recursion/run_recursion_diff.sh — [DD-14] wave B+C's behavioural
# instrument for module `recursion`: the things `tests/recursion/*.rxt`
# structurally CANNOT assert.
#
#   §1  THE `--no-captures` AXIS, which the corpus's own CLAUDE.md names as
#       OWED and cannot express: **no `.rxt` directive for that flag exists
#       anywhere in the tree**. Design §4.3's whole claim lives on this axis —
#       a call names a group exactly as a reference does, so `pcrec_bref_mark`
#       must mark `u.call.target` or `--no-captures` DELETES group 1's `A_CAP`
#       out from under `(a)(?1)` and the call has no body. Both halves are
#       asserted: the group's SLOTS survive in the emitted C, and the matcher
#       still gives the right answer while reporting `RX_NCAPS 1`. S-SR10's
#       one-hop cell and S-SR11a's two-hop cell are the population, and the
#       two-hop one is here because §4.3's WITHDRAWN transitivity clause
#       claimed to need a fixpoint for exactly that shape.
#
#   §2  THE DEPTH CAPACITY AND ITS CODE (design §5.6, D71.1). A `.rxt` `gu`
#       cell can assert THAT a pattern gives up; nothing can measure WHERE the
#       artifact's honest ceiling actually is, and the ceiling is the number
#       §14 ASK 2 is about. This section bisects `^(a(?1)?b)$` over a^n b^n,
#       reports the largest n that MATCHES, and asserts that one step beyond
#       it the answer is the typed give-up rather than a wrong `nomatch` —
#       which is the failure direction S-SR7 (an under-charged `2*|W|` of
#       trail) produces and no corpus cell can see, because a corpus cell has
#       to pick a length in advance.
#
#   §3  THE SUBJECT SWEEP, against libpcre2, over a generated call population
#       with startpos taking EVERY value in [0, n], comparing the MATCH SPAN
#       AND EVERY GROUP SPAN. Both axes are load-bearing here for reasons one
#       construct over from `backrefs`': the GROUP spans are where §5.3's
#       restore set is observable at all (design §5.3's own prototype found
#       `W` incomplete by reading `g1 = (1,4)` on a match whose SPAN was
#       right — "a wrong span on a correct match, which no `m`/`n`
#       expectation catches and only a `g` line does"), and STARTPOS is where
#       `reset_for_next_attempt`'s `call_top` line is observable, since an
#       attempt that inherited the previous attempt's activation returns
#       through a dead frame.
#
#   §4  THE `--engine=dfa` REFUSAL, BY NAME, and its CONTROL. The refusal
#       alone goes green on a compiler that stopped accepting calls entirely,
#       so the same pattern must COMPILE on the default engine in the same
#       section — `check_engine_capability`'s own both-directions rule, here
#       for a construct whose 24 rows that check now demands witnesses for.
#
# IT REUSES `tests/backrefs/bref_oracle.py` AND `tests/backrefs/bref_batch.c`
# rather than copying them, which is `tests/lookaround/`'s own decision one
# module over and D24's standing rule against a second home for one fact.
# Neither is backref-specific: the oracle takes `<key>\t<ngroups>\t<pattern>`
# and sweeps every startpos over a subject directory, and the driver takes
# `<subject-file>\t<startpos>` on stdin and prints the span plus every
# `RX_NCAPS` group pair.
#
# EVERY POPULATION IS ASSERTED EXACT, NEVER PRINTED AND NEVER AS A FLOOR. A
# sweep that generated nothing prints the same silence as one that agreed
# everywhere, and this project's own record is full of that shape.
#
# Usage: bash tests/recursion/run_recursion_diff.sh
# Env: PCREC, CC, GENCFLAGS, KEEP=1
#
# SKIPS LOUDLY when libpcre2 is absent (PC-3's pattern) — and only §3 skips:
# §1, §2 and §4 need no oracle at all and RUN, so a box with no libpcre2 still
# gets the sections that defend this module's own artifact properties.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11}"
ORACLE="$ROOT_DIR/tests/backrefs/bref_oracle.py"
BATCH="$ROOT_DIR/tests/backrefs/bref_batch.c"
FEATS="recursion,named-groups,backrefs,atomic-groups,assertions,classes,modifiers,lookaround"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "recursion-diff: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
finish() { echo; echo "checks passed: $pass"; echo "checks failed: $fail"; \
           [ "$fail" -eq 0 ] || exit 1; exit 0; }
die()    { bad "$1"; finish; }

[ -x "$PCREC" ] || die "compiler $PCREC is missing or not executable — run \`make\` first"
[ -f "$ORACLE" ] || die "the shared libpcre2 oracle $ORACLE is missing"
[ -f "$BATCH" ]  || die "the shared batch driver $BATCH is missing"

# =========================================================================
# §1 THE `--no-captures` AXIS (design §4.3)
# =========================================================================
# A CALL TARGET MUST JOIN THE MARKED SET. P10 MEASURED that `--no-captures`
# deletes the `A_CAP` wrapper of every group nothing references, so without
# `pcrec_bref_mark`'s `A_CALL` arm the call in `(a)(?1)` would have no body at
# all. Two cells, and the SECOND is the one §4.3's withdrawn transitivity
# clause claimed to need a fixpoint for: a call from INSIDE group 1 to group 3
# is an `A_CALL` node in the tree, so the whole-tree walk reaches it wherever
# it sits and the arm is `mark[target] = true` with no descent.
nc_case() {
    local label="$1" pat="$2" grp="$3" subj="$4" want="$5"
    local d="$WORKDIR/nc$grp$RANDOM"
    mkdir -p "$d"
    if ! "$PCREC" --features "$FEATS" -p rx --no-captures --emit-main \
            -o "$d/gen.c" -- "$pat" 2>"$d/err"; then
        bad "[$label] --no-captures build refused: $(head -1 "$d/err")"
        return
    fi
    # HALF ONE: the SLOTS survive. The group is deleted by `br_strip_caps`
    # unless the mark set holds it, and a deleted group emits no slot legend
    # entry and no write — which is visible in the artifact and in nothing
    # else, because the ANSWER can still be right by accident on a subject the
    # callee's own text happens to match.
    if ! grep -q "RX_SLOT_GROUP${grp}_START" "$d/gen.c"; then
        bad "[$label] group $grp's slots are GONE under --no-captures: the call target was not marked, so \`br_strip_caps\` deleted the A_CAP the call needs (design §4.3)"
        return
    fi
    # HALF TWO: the artifact reports NO captures and still MATCHES. §6.3's
    # ruling is that the flag drops the slots a CALLER can see, not the
    # machinery a match needs.
    local ncaps
    ncaps="$(grep -m1 '^#define RX_NCAPS' "$d/gen.h" 2>/dev/null || \
             grep -m1 '^#define RX_NCAPS' "$d/gen.c")"
    ncaps="${ncaps##* }"
    if [ "$ncaps" != "1" ]; then
        bad "[$label] --no-captures artifact reports RX_NCAPS $ncaps, not 1"
        return
    fi
    # shellcheck disable=SC2086
    if ! $CC $GENCFLAGS -o "$d/t" "$d/gen.c" 2>"$d/cerr"; then
        bad "[$label] the --no-captures artifact does not compile: $(head -1 "$d/cerr")"
        return
    fi
    local got
    got="$("$d/t" "$subj" 2>&1 | head -1)"
    if [ "$got" != "$want" ]; then
        bad "[$label] --no-captures answer is '$got', expected '$want'"
        return
    fi
    ok "[$label] under --no-captures group $grp keeps its slots, the artifact reports RX_NCAPS 1, and '$subj' still answers '$want'"
}

nc_case "no-captures one-hop"  '^(a|b)(?1)$'          1 "ab"   "match 0 2"
nc_case "no-captures two-hop"  '^(a(?3))(b)((c))$'    3 "acbc" "match 0 4"

# =========================================================================
# §2 THE DEPTH CAPACITY, AND THE CODE IT ANSWERS WITH (design §5.6, D71.1)
# =========================================================================
# `^(a(?1)?b)$` needs one activation per `a`, so the largest n it matches IS
# the artifact's honest reach, expressed in the unit a caller can act on: a
# SUBJECT SIZE. §5.6 is emphatic that a depth is not a number a caller can
# read, and §14 ASK 2 asks Frank to pick this ceiling with both implied
# subject sizes stated beside it — so this section MEASURES the number rather
# than pinning one, and asserts only the two properties that must hold
# whatever it is.
DEPTH_PAT='^(a(?1)?b)$'
d="$WORKDIR/depth"
mkdir -p "$d"
if ! "$PCREC" --features "$FEATS" -p rx --emit-main -o "$d/gen.c" -- "$DEPTH_PAT" \
        2>"$d/err"; then
    bad "[depth] $DEPTH_PAT does not compile: $(head -1 "$d/err")"
else
    # shellcheck disable=SC2086
    if ! $CC $GENCFLAGS -o "$d/t" "$d/gen.c" 2>"$d/cerr"; then
        bad "[depth] the artifact does not compile: $(head -1 "$d/cerr")"
    else
        answer() { "$d/t" "$(python3 -c "print('a'*$1+'b'*$1)")" 2>&1 | head -1; }
        # DOUBLING then BISECTION, not a linear walk: the reach is a capacity
        # and capacities are large. The doubling stops at 4096, which is well
        # past any value RX_RESUME_FRAMES can support at 2048 frames — a probe
        # that never reached the limit and printed a confident number for it is
        # this design lane's OWN recorded instrument defect (§0.3 item 2), so
        # the ceiling of the search is asserted to have been CROSSED.
        lo=1; hi=1
        while [ "$hi" -le 4096 ]; do
            case "$(answer "$hi")" in match*) lo=$hi; hi=$((hi * 2));; *) break;; esac
        done
        if [ "$hi" -gt 4096 ]; then
            bad "[depth] the doubling search reached n=$lo without the artifact giving up — the probe never found the ceiling and must not report one (design §0.3 defect 2)"
        else
            while [ $((hi - lo)) -gt 1 ]; do
                mid=$(((lo + hi) / 2))
                case "$(answer "$mid")" in match*) lo=$mid;; *) hi=$mid;; esac
            done
            beyond="$(answer "$hi")"
            ok "[depth] $DEPTH_PAT matches a^n b^n up to n=$lo (a $((2*lo))-byte subject) and answers '$beyond' at n=$hi"
            case "$beyond" in
                *frames*|*giveup*|*error*)
                    ok "[depth] one step past the ceiling the artifact GIVES UP with a typed code rather than answering nomatch — D71.1's default-artifact story (PCREC_ERR_FRAMES; PCREC_ERR_RECURSE is the diagnostic axis's)" ;;
                nomatch*)
                    bad "[depth] at n=$hi the artifact answers 'nomatch' on a subject the pattern MATCHES — a capacity reported as a wrong answer is the one failure mode D22 rules out, and it is what an under-charged 2*|W| of trail (S-SR7) produces" ;;
                *)
                    bad "[depth] at n=$hi the artifact answered '$beyond', which is neither a match nor a give-up" ;;
            esac
        fi
    fi
fi

# =========================================================================
# §4 THE `--engine=dfa` REFUSAL AND ITS CONTROL
# =========================================================================
# BOTH DIRECTIONS, for `check_engine_capability`'s own reason: a refusal test
# alone goes green on a compiler that had simply stopped accepting the
# construct. A call-bearing pattern is `VM_ONLY` STRUCTURALLY — the language
# `^(a(?1)?b)$` generates is a^n b^n, which is not regular (design §8.1) — so
# there is no flag that makes it DFA-compilable and the refusal must name the
# CONSTRUCT rather than advise `--no-captures`.
# `-o /dev/null` IS NOT AVAILABLE HERE and the reason is a measured instrument
# defect from this module's own design lane (§0.3 item 5): pcrec derives the
# paired header's name from the output path, so `-o /dev/null` asks for
# `/dev/null.h` and every COMPILING cell reads "Permission denied". The design
# lane published three cells that way before catching it.
dfa_out="$("$PCREC" --features "$FEATS" -p rx --engine=dfa -o "$WORKDIR/dfa.c" -- '(a)(?1)' 2>&1)"
case "$dfa_out" in
    *"(?1"*|*"recursion"*)
        ok "[engine] --engine=dfa on '(a)(?1)' refuses naming the construct: $dfa_out" ;;
    *)
        bad "[engine] --engine=dfa on '(a)(?1)' answered '$dfa_out', which does not name the construct" ;;
esac
if "$PCREC" --features "$FEATS" -p rx -o "$WORKDIR/ctl.c" -- '(a)(?1)' 2>/dev/null; then
    ok "[engine] the CONTROL: the same pattern compiles on the default engine, so the refusal above is about the ENGINE and not about the construct having stopped being accepted"
else
    bad "[engine] '(a)(?1)' does not compile on the default engine — the refusal above proves nothing"
fi

# =========================================================================
# §3 THE SUBJECT SWEEP AGAINST LIBPCRE2 — the only section that needs an oracle
# =========================================================================
if ! python3 -c "
import sys, os
sys.path.insert(0, os.path.join('$ROOT_DIR', 'docs', 'design',
                                'eng_brep_measurements', 'probes'))
import pcre2_ctypes" 2>"$WORKDIR/oracle.log"; then
    echo "SKIP: libpcre2 is not available, so §3's subject sweep cannot run:"
    sed 's/^/  /' "$WORKDIR/oracle.log"
    echo "SKIP: §1, §2 and §4 above DID run — this is a partial skip, not a skipped script"
    finish
fi

SUBJDIR="$WORKDIR/subjects"
mkdir -p "$SUBJDIR"
i=0
# The alphabet is the corpus's own, plus the shapes each measured claim needs:
# `abab`/`aabb`/`aaabbb` for the nesting depth, `azabc` for §3.5's W3 (the
# callee must GIVE BACK though its lexical home is atomic), `xzyc` for W2,
# `qyx`/`qyy` for §3.4(c)'s dupnames split, and the leading `x` family so
# STARTPOS is a real axis rather than a formality.
for s in "" "a" "b" "ab" "ba" "aa" "abab" "aabb" "aaabbb" "abb" "aab" \
         "abc" "xzyc" "xzc" "azabc" "azc" "qyx" "qyy" "xab" "xxabab" \
         "aabbaabb" "aaa" "aaaa" "ac"; do
    printf '%s' "$s" > "$SUBJDIR/$(printf 's%02d' "$i")"
    i=$((i + 1))
done
NSUBJ=$i
[ "$NSUBJ" -eq 24 ] || die "the subject set is $NSUBJ files, not the 24 this script's population guard is computed against"

run_arm() {
    local pat="$1" extra="$2" out="$3"
    local d="$WORKDIR/arm$RANDOM$RANDOM"
    mkdir -p "$d"
    # shellcheck disable=SC2086
    if ! "$PCREC" --features "$FEATS" -p rx $extra -o "$d/gen.c" -- "$pat" \
            2>"$d/err"; then
        echo "COMPILE-FAIL"; sed 's/^/    /' "$d/err" >&2; return 1
    fi
    local ncaps
    ncaps="$(grep -m1 '^#define RX_NCAPS' "$d/gen.h" | awk '{print $3}')"
    # shellcheck disable=SC2086
    if ! $CC $GENCFLAGS -I"$d" -o "$d/t" "$BATCH" "$d/gen.c" 2>"$d/cerr"; then
        echo "CC-FAIL"; head -5 "$d/cerr" >&2; return 1
    fi
    : > "$WORKDIR/cells"
    for f in "$SUBJDIR"/*; do
        local n
        n=$(wc -c < "$f")
        local sp=0
        while [ "$sp" -le "$n" ]; do
            printf '%s\t%d\n' "$f" "$sp" >> "$WORKDIR/cells"
            sp=$((sp + 1))
        done
    done
    "$d/t" < "$WORKDIR/cells" > "$out" || return 1
    echo $((ncaps - 1))
}

run_oracle() {
    local pat="$1" ng="$2" out="$3"
    printf 'k\t%d\t%s\n' "$ng" "$pat" > "$WORKDIR/patline"
    python3 "$ORACLE" "$WORKDIR/patline" "$SUBJDIR" "$WORKDIR/otsv" \
        2>"$WORKDIR/oerr" || return 1
    cut -f4 "$WORKDIR/otsv" > "$out"
}

CELLS=0
compare_one() {
    local pat="$1" label="${2:-$1}"
    local ng
    ng="$(run_arm "$pat" "" "$WORKDIR/mine")" || {
        bad "[$label] pcrec could not build the artifact"; return 1; }
    case "$ng" in *FAIL*) bad "[$label] $ng"; return 1;; esac
    run_oracle "$pat" "$ng" "$WORKDIR/theirs" || {
        bad "[$label] the libpcre2 oracle failed: $(head -2 "$WORKDIR/oerr")"
        return 1; }
    local a b
    a=$(wc -l < "$WORKDIR/mine"); b=$(wc -l < "$WORKDIR/theirs")
    if [ "$a" -ne "$b" ]; then
        bad "[$label] pcrec produced $a answers and the oracle $b — a positional comparison over unequal lists compares the wrong cells"
        return 1
    fi
    if ! diff -q "$WORKDIR/mine" "$WORKDIR/theirs" >/dev/null; then
        bad "[$label] $(diff "$WORKDIR/mine" "$WORKDIR/theirs" | grep -c '^<') of $a cells DIFFER from libpcre2"
        diff "$WORKDIR/mine" "$WORKDIR/theirs" | head -8 >&2
        return 1
    fi
    CELLS=$((CELLS + a))
    return 0
}

# THE POPULATION, and every row is a MEASURED claim of the design rather than
# a shape somebody liked. It is written here rather than extracted from the
# corpus because the corpus's own cells are already oracle-generated: what
# this section adds is the STARTPOS and GROUP axes over the same shapes, which
# is where the restore set and the per-attempt reset become observable.
SWEEP_FAIL=0
while IFS='|' read -r label pat; do
    [ -z "$label" ] && continue
    compare_one "$pat" "$label" || SWEEP_FAIL=1
done <<'ROWS'
§2.1 the call/reference discriminator|(a|b)(?1)
§2.3 relative, backward|^(a)(b)(?-1)$
§2.3 relative, forward|^(?+1)(a|b)$
§2.4 the root re-runs the anchors|^(a(?R)?b)$
§2.4 a group call does not|^(a(?1)?b)$
§3.1 the callee writes, the return restores|^((a)(?1)?(b))$
§3.1 the callee INHERITS|^(a)(b\1)(?2)$
§3.2 the isolated atomicity discriminator|^(?:(?<g>a|ab)){0}(?&g)c$
§3.2 retry across a return, at depth|^(?:(?<g>a(?&g)?b|x|xy)){0}(?&g)$
§3.5 W2 retry inside a negative lookahead|^(?!(z|zy))x(?1)c$
§3.5 W3 give back inside an atomic group|^(?>(a|ab))z(?1)c$
§4.4c a rung-bearing callee under {0}|^(?:(a?)){0}(?1)*b$
§5.2 the clobber sequence|^(?:(?<g>x|xy)){0}(?&g)(?&g)y$
§5.3b axis P, the PENDING family|^(a(?1)?b)\1$
§5.3b axis C, the CUT_MARK family|^((?>a(?1)?))a$
§5.3b axis C's non-atomic control|^((?:a(?1)?))a$
ROWS

if [ "$SWEEP_FAIL" -eq 0 ]; then
    [ "$CELLS" -eq 1632 ] || die "§3 compared $CELLS cells, not the 1632 this guard is computed against — the sweep's population moved and a smaller one is how this section passes while measuring less"
    ok "§3: $CELLS cells over 16 patterns x $NSUBJ subjects x every startpos (102 cells per pattern), span AND every group span, 0 disagreements with libpcre2 10.46"
fi

finish
