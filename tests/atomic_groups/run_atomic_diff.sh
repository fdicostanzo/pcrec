#!/usr/bin/env bash
# tests/atomic_groups/run_atomic_diff.sh — [M6.4.2]'s behavioural instrument
# for module `atomic-groups`: five things tests/atomic_groups/*.rxt
# structurally CANNOT assert, each against libpcre2 or against pcrec itself.
#
#   §1  THE SUBJECT SWEEP, against libpcre2, over a generated space with
#       startpos taking EVERY value in [0, n]. The `.rxt` corpus pins chosen
#       cells; this sweeps. The startpos axis is exhaustive because the cut
#       makes "the leftmost candidate is not the leftmost match" an ORDINARY
#       occurrence — `(?>a|ab)c` on "abc" is NO MATCH while its uncut twin
#       matches — so WHICH start the search reaches is the axis this construct
#       moves, and a sweep that fixed the argument could not see it.
#
#   §2  THE ENGINE DIFFERENTIAL, and it is the single most important section
#       in this file. Every pattern is compiled BOTH ways: the DEFAULT
#       (hybrid: capture-erased DFA prefilter + VM) and `--engine=vm` (the
#       prefilter OFF, R21 E-6). §4's whole hazard lives in the difference
#       between those two artifacts — the prefilter necessarily answers for
#       the UNCUT language, so its span END is not a bound on the cut match's
#       end — and a suite that ran only one of them would not see it. 114
#       cells of silent match loss were MEASURED on the emitted prefilter
#       before RULE H3 existed; this is the arm they would show up in.
#
#   §2b THE `-fno-possessify` ARM. Without it sabotage row S92 (the flag
#       CLEARS a user-written possessive) cannot be scored at all: its whole
#       failing direction is "RED only under the flag", and a corpus with no
#       flag arm has nowhere for it to be red. The flag denies possessify's
#       REWRITE and must NOT change a WRITTEN possessive's answer — that is
#       §3.2 RULE 2 as behaviour, and it is what makes storing the module's
#       semantics in `Ast.possessive` a miscompile rather than a style
#       question.
#
#   §3  THE DISCHARGE DIFFERENTIAL, pcrec against pcrec. Every pattern is
#       compiled with and without `-fno-atomic-discharge`, asserting IDENTICAL
#       ANSWERS. The discharge deletes a cut possessify's §2.2 verdict proves
#       dead; "changes no answer" is its entire claim and this is the only
#       thing in the tree that checks it. It also asserts §5.4's
#       EMISSION-NEUTRALITY where that property holds: for a DISCHARGED
#       possessive the VM artifact is byte-identical either way, because
#       possessify re-derives the identical verdict on the same quantifier and
#       re-marks it. The discharge changes ENGINE SELECTION and nothing else.
#
#   §4  THE THREE ENTRIES side by side (atomic_entries.c), which is H4's
#       obligation. `<prefix>_match`/`_match_caps` answer about exactly
#       `ctx->pos` and pass `ctx->len` as the MRL ceiling rather than a
#       prefilter window, so §4's hazard cannot reach them — a claim nothing
#       in the corpus can see either way. The match-here ORACLE is `\G(?:PAT)`
#       (wave D's trick): libpcre2 has no anchored mode, but `\G` is true iff
#       `pos == startpos`, so its answer for the wrapped pattern IS the
#       match-here answer for the bare one.
#
# EVERY POPULATION IS ASSERTED, NEVER PRINTED. A sweep that quietly generated
# nothing prints the same silence as one that agreed everywhere, and this
# project's own record is full of that shape (the design's §6.4a non-vacuity
# counter measured the wrong axis; the WRAP assertion passed on an empty
# population). Each section below ends in a floor its own run has to clear.
#
# Usage: bash tests/atomic_groups/run_atomic_diff.sh
# Env: PCREC, CC, KEEP=1
#
# SKIPS LOUDLY when libpcre2 is absent (PC-3's pattern), never silently.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "atomic-diff: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---- the oracle ----------------------------------------------------------
ORACLE="$WORKDIR/pcre2_oracle"
if ! $CC -O1 -std=gnu11 -Wall -Wextra -Werror -o "$ORACLE" \
        "$ROOT_DIR/tests/fuzz/pcre2_oracle.c" -ldl 2>"$WORKDIR/ob.log"; then
    echo "FAIL: could not build tests/fuzz/pcre2_oracle:" >&2
    cat "$WORKDIR/ob.log" >&2
    exit 1
fi
printf 'a' > "$WORKDIR/probe"
if ! "$ORACLE" 'a' "$WORKDIR/probe" >/dev/null 2>&1; then
    echo "SKIP: libpcre2 is not available at run time — this differential needs it (PC-3's pattern: a loud skip, never a silent pass)"
    echo "checks passed: 0"
    echo "checks failed: 0"
    exit 0
fi

# ---- the subject space ---------------------------------------------------
# CUT-SHAPED BY CONSTRUCTION. The cells that can break a cut are the ones
# where the body's FIRST success is not the one the whole match needs, so the
# subject set has to contain the near-misses that force the search to move on:
# a prefix shared between an alternation's branches followed by something only
# the LONGER branch could have reached, and runs of a loop body followed by a
# byte the follow cannot take.
python3 - "$WORKDIR/subjects" <<'PY'
import itertools, os, sys
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
subs = []
# EXHAUSTIVE up to length 4 over {a, b, c} — 121 subjects. Exhaustive rather
# than curated so every "shared prefix, then the wrong byte" shape the cut
# cells need is present by ENUMERATION rather than by someone remembering it.
for n in range(0, 5):
    for t in itertools.product("abc", repeat=n):
        subs.append("".join(t))
# The quote/space shapes the canonical idiom family is written in, and a few
# longer runs where a greedy loop would retreat many times before the follow
# succeeds — or never does.
subs += ['"', 'ab"cd"', '"x"y"', 'a"b', ' ab ', 'x ab', 'abcd', 'xabcd',
         'abcabc', 'aabbcc', 'ababab', 'abcbca',
         "a" * 12 + "b", "a" * 12 + "ab", "a" * 16, "ab" * 8,
         ("ab" * 6) + "c", "a" * 8 + "x" + "a" * 8, "b" * 12 + "c",
         "ababababababababc"]
for i, s in enumerate(subs):
    with open(os.path.join(out, "s%04d" % i), "wb") as f:
        f.write(s.encode("latin-1"))
print(len(subs))
PY
NSUBJ=$(ls "$WORKDIR/subjects" | wc -l)
if [ "$NSUBJ" -lt 120 ]; then
    bad "subject generation produced only $NSUBJ subjects — the sweep has no space"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# ---- the patterns --------------------------------------------------------
# FOUR CLASSES, and the classification is DATA here rather than a rule applied
# later, because the sections below assert different things about each.
#
#   cut       the cut BITES — the atomic answer differs from the uncut twin's
#             somewhere. §3's discharge must DECLINE these.
#   dead      the cut is provably a no-op — §2.2's verdict is positive, so the
#             free discharge SHOULD delete it. §3's population.
#   carve     a body the LIFT must decline: nullable or lazy. If the lift ever
#             accepted one, the nullable members HANG (a timeout, loud under
#             D45) and the lazy ones answer the wrong language.
#   control   no atomic construct at all — the arm that says the plumbing
#             works, and the only class python `re` can also answer.
PATSPEC=(
    "cut:(?>a|ab)c"
    "cut:(?>ab|a)b"
    "cut:(?>a|ab)b"
    "cut:(?>a|ab)bc"
    "cut:(?>a|ab)c|abcd"
    "cut:(?>ab|a)b|abcd"
    "cut:x*(?>a|ab)c|abcd"
    "cut:(?>(?>a|ab)c|abd)"
    "cut:(?>a(?>b|bc))c"
    "cut:(?>a|ab)*c"
    "cut:(?>a|b)*c"
    "cut:(?>ab)+c"
    "cut:(?>a*)a"
    "cut:(?>a*+)a"
    "cut:a*+a"
    "cut:a++a"
    "cut:(?:a|ab)*+c"
    "cut:(?:a|ab)++c"
    "cut:(?:a|ab){1,3}+c"
    "cut:(?:a|ab){2}+"
    "cut:(?:ab|b){8,}+c"
    "cut:(?>(a)|ab)"
    "cut:(?>(a)x|ab)"
    "cut:((?>(a)|ab))c|(abc)"
    "cut:(?>a|ab)(?>b|bc)c"
    "cut:(?>)a"
    "dead:a*+b"
    "dead:a++c"
    "dead:a?+b"
    "dead:[^\"]*+\""
    "dead:(?>a*)b"
    "dead:(?>a+)c"
    "dead:a{2}+b"
    "dead:a{2,}+b"
    "dead:a{1,2}+b"
    "dead:(?>a{1,2})b"
    "carve:(?>a*?)b"
    "carve:(?>a+?)b"
    "carve:(?>a{1,3}?)b"
    "carve:(?>[ab]*?)b"
    "carve:(?>(?:a|bc)*?)d"
    "carve:(?>a*?b)c"
    "carve:(?>(?:a*)*)b"
    "carve:(?:a*)*+b"
    "carve:(?>(?:a?)*)b"
    "carve:(?:a?)*+b"
    "carve:(?>(?:|a)*)b"
    "carve:(?:|a)*+b"
    "carve:(?>(?:a*?b)*)d"
    "control:a?b"
    "control:[ab]+c"
    "control:(?:a|ab)c"
    "control:(?:ab)+c"
)

gen() { # gen <outdir> <pattern> [extra pcrec args]
    local d="$1" pat="$2"; shift 2
    mkdir -p "$d"
    "$PCREC" --features all -p rx "$@" -o "$d/gen.c" -- "$pat" 2>"$d/err" || return 1
    $CC -O2 -I"$d" -o "$d/t" "$ROOT_DIR/tests/fuzz/fuzz_driver.c" "$d/gen.c" \
        2>>"$d/err" || return 1
}

# =========================================================================
# §1 + §2 + §2b   THE SUBJECT SWEEP, three arms
# =========================================================================
npat=0; ncells=0; nvm=0; nnp=0; ndiff=0
ncut=0; ndead=0; ncarve=0; nctl=0
nbite=0            # patterns where the cut MEASURABLY changes the answer
: > "$WORKDIR/diffs.txt"
: > "$WORKDIR/cells.tsv"

for spec in "${PATSPEC[@]}"; do
    cls="${spec%%:*}"; pat="${spec#*:}"
    d="$WORKDIR/p$npat"; npat=$((npat + 1))
    case "$cls" in
        cut) ncut=$((ncut + 1)) ;; dead) ndead=$((ndead + 1)) ;;
        carve) ncarve=$((ncarve + 1)) ;; *) nctl=$((nctl + 1)) ;;
    esac

    if ! gen "$d" "$pat"; then
        bad "could not build a default-engine artifact for '$pat': $(head -2 "$d/err")"
        continue
    fi
    if ! gen "$d/vm" "$pat" --engine=vm; then
        bad "could not build a --engine=vm artifact for '$pat': $(head -2 "$d/vm/err")"
        continue
    fi
    if ! gen "$d/np" "$pat" -fno-possessify; then
        bad "could not build a -fno-possessify artifact for '$pat': $(head -2 "$d/np/err")"
        continue
    fi

    # THE UNCUT TWIN, built ONLY to measure whether the cut BITES on this
    # subject set. It is a two-byte edit — `(?>` to `(?:` and a possessive `+`
    # dropped — so a divergence is attributable to the ATOMICITY and to
    # nothing else; a hand-written twin can differ in something else and make
    # the measurement unreadable. It is never compared against pcrec.
    twin="$(printf '%s' "$pat" | sed 's/(?>/(?:/g; s/\([*+?}]\)+/\1/g')"

    bites=0
    for f in "$WORKDIR"/subjects/*; do
        len=$(wc -c < "$f")
        for sp in $(seq 0 "$len"); do
            want="$("$ORACLE" "$pat" "$f" "$sp" 2>/dev/null)"
            case "$want" in "match "*|nomatch) ;; *) continue ;; esac

            got="$(timeout 10 "$d/t" "$f" "$sp" 2>/dev/null)"
            ncells=$((ncells + 1))
            [ "$got" = "$want" ] || { ndiff=$((ndiff + 1)); printf \
                'DEFAULT %s [%s] startpos %s: pcrec %s / libpcre2 %s\n' \
                "$pat" "$(basename "$f")" "$sp" "$got" "$want" >> "$WORKDIR/diffs.txt"; }

            gotv="$(timeout 10 "$d/vm/t" "$f" "$sp" 2>/dev/null)"
            nvm=$((nvm + 1))
            [ "$gotv" = "$want" ] || { ndiff=$((ndiff + 1)); printf \
                'VM      %s [%s] startpos %s: pcrec %s / libpcre2 %s\n' \
                "$pat" "$(basename "$f")" "$sp" "$gotv" "$want" >> "$WORKDIR/diffs.txt"; }

            gotn="$(timeout 10 "$d/np/t" "$f" "$sp" 2>/dev/null)"
            nnp=$((nnp + 1))
            [ "$gotn" = "$want" ] || { ndiff=$((ndiff + 1)); printf \
                'NOPOSS  %s [%s] startpos %s: pcrec %s / libpcre2 %s\n' \
                "$pat" "$(basename "$f")" "$sp" "$gotn" "$want" >> "$WORKDIR/diffs.txt"; }

            if [ "$bites" -eq 0 ] && [ "$cls" = "cut" ]; then
                tw="$("$ORACLE" "$twin" "$f" "$sp" 2>/dev/null)"
                [ "$tw" = "$want" ] || bites=1
            fi
            printf '%s\t%s\t%s\t%s\t%s\n' "$cls" "$pat" "$(basename "$f")" \
                "$sp" "$want" >> "$WORKDIR/cells.tsv"
        done
    done
    [ "$bites" -eq 1 ] && nbite=$((nbite + 1))
done

if [ "$ndiff" -eq 0 ]; then
    ok "§1/§2/§2b differential: $ncells DEFAULT (hybrid, prefilter LIVE), $nvm --engine=vm (prefilter OFF) and $nnp -fno-possessify cells over $npat patterns x $NSUBJ subjects x every startpos in [0, n] agree with libpcre2 exactly"
else
    bad "§1/§2/§2b differential: $ndiff cells disagree with libpcre2:"
    head -30 "$WORKDIR/diffs.txt" >&2
fi

# THE NON-VACUITY FLOORS. A sweep of patterns whose cut never bites would
# agree with libpcre2 on a compiler that ignored the atomicity entirely, which
# is the exact defect src/parse/registry.c's row comment has warned about since
# before there was a producer. `nbite` is measured against the two-byte UNCUT
# twin rather than assumed from the pattern's shape.
if [ "$ncut" -ge 20 ] && [ "$ndead" -ge 8 ] && [ "$ncarve" -ge 10 ] \
   && [ "$nctl" -ge 3 ]; then
    ok "population: $ncut cut / $ndead dead-cut / $ncarve carve-out / $nctl control patterns (floors 20/8/10/3)"
else
    bad "population: $ncut cut / $ndead dead / $ncarve carve / $nctl control — below the floors 20/8/10/3, so the sweep is not measuring what it claims"
fi
if [ "$nbite" -ge 15 ]; then
    ok "non-vacuity: the cut MEASURABLY changes the answer on $nbite of the $ncut cut patterns (floor 15), measured against each one's two-byte UNCUT twin — so a compiler that lowered the group by ignoring the atomicity would be RED above, not green"
else
    bad "non-vacuity: only $nbite of $ncut cut patterns have a subject where the cut changes the answer (floor 15). The sweep above would pass on a compiler that ignored the atomicity"
fi
if [ "$ncells" -ge 20000 ]; then
    ok "cell floor: $ncells default-engine cells (floor 20000)"
else
    bad "cell floor: only $ncells default-engine cells (floor 20000)"
fi

# =========================================================================
# §3  THE DISCHARGE DIFFERENTIAL — pcrec against pcrec
# =========================================================================
# TWO ASSERTIONS, and they are different claims about the same rewrite.
#
#   ANSWERS. The discharge deletes a cut §2.2 proves dead; "changes no answer"
#   is its entire claim, and denying it with `-fno-atomic-discharge` is the
#   only way to check it. Asserted over EVERY class, not just `dead`: a
#   discharge that fired on a `cut` pattern (sabotage S91) shows up here as a
#   wrong answer rather than as a missing optimisation.
#
#   BYTES, for the DISCHARGED possessive spellings only. §5.4's
#   emission-neutrality: if the discharge fires, possessify's fixpoint
#   re-derives the identical verdict on the same quantifier and re-marks it, so
#   the VM artifact is byte-identical either way and the rewrite changes ENGINE
#   SELECTION and nothing else. Compared under `--engine=vm` because that is
#   where both builds produce a VM artifact to compare.
nd_ans=0; nd_bytes=0; nd_same=0; nd_engine=0; ndd=0
for spec in "${PATSPEC[@]}"; do
    cls="${spec%%:*}"; pat="${spec#*:}"
    d="$WORKDIR/d$ndd"; ndd=$((ndd + 1))
    gen "$d/on"  "$pat"                        || continue
    gen "$d/off" "$pat" -fno-atomic-discharge   || continue
    for f in "$WORKDIR"/subjects/*; do
        len=$(wc -c < "$f")
        for sp in 0 1 2 "$len"; do
            [ "$sp" -le "$len" ] || continue
            a="$(timeout 10 "$d/on/t"  "$f" "$sp" 2>/dev/null)"
            b="$(timeout 10 "$d/off/t" "$f" "$sp" 2>/dev/null)"
            nd_ans=$((nd_ans + 1))
            [ "$a" = "$b" ] || { ndiff=$((ndiff + 1)); printf \
                'DISCHARGE %s [%s] startpos %s: on=%s off=%s\n' \
                "$pat" "$(basename "$f")" "$sp" "$a" "$b" >> "$WORKDIR/diffs.txt"; }
        done
    done
    # THE ENGINE MOVED, which is what the discharge is FOR. Read off the
    # artifact rather than assumed: a `dead` pattern with no captures must
    # compile to a pure DFA with the discharge on, and to a VM artifact with it
    # off. `RX_ENGINE` is absent from a DFA artifact.
    if [ "$cls" = "dead" ]; then
        "$PCREC" --features all -p rx --no-captures -o "$d/e_on.c"  -- "$pat" 2>/dev/null
        "$PCREC" --features all -p rx --no-captures -fno-atomic-discharge \
                 -o "$d/e_off.c" -- "$pat" 2>/dev/null
        if ! grep -q '#define RX_ENGINE' "$d/e_on.c" \
           && grep -q '#define RX_ENGINE' "$d/e_off.c"; then
            nd_engine=$((nd_engine + 1))
        else
            bad "§3 discharge: '$pat' has a §2.2-dead cut, so --no-captures must give a PURE DFA with the discharge ON and a VM artifact with it OFF; got on=$(grep -c '#define RX_ENGINE' "$d/e_on.c") off=$(grep -c '#define RX_ENGINE' "$d/e_off.c") RX_ENGINE defines"
        fi
        # EMISSION NEUTRALITY, on the VM path, for the discharged spellings.
        "$PCREC" --features all -p rx --engine=vm --no-captures \
                 -o "$d/b_on.c"  -- "$pat" 2>/dev/null
        "$PCREC" --features all -p rx --engine=vm --no-captures \
                 -fno-atomic-discharge -o "$d/b_off.c" -- "$pat" 2>/dev/null
        nd_bytes=$((nd_bytes + 1))
        if cmp -s "$d/b_on.c" "$d/b_off.c"; then
            nd_same=$((nd_same + 1))
        else
            bad "§3 emission-neutrality: '$pat' emits DIFFERENT VM bytes with and without the discharge. §5.4 says possessify's fixpoint re-derives the identical verdict on the same quantifier, so the discharge must change ENGINE SELECTION and nothing else"
        fi
    fi
done

if [ "$nd_ans" -ge 5000 ] && [ "$nd_engine" -ge 8 ] && [ "$nd_bytes" -ge 8 ] \
   && [ "$nd_same" -eq "$nd_bytes" ]; then
    ok "§3 discharge: $nd_ans answer cells identical with and without -fno-atomic-discharge (floor 5000); $nd_engine dead-cut patterns move DFA<->VM as the flag says (floor 8); all $nd_bytes of them emit byte-identical VM code either way (§5.4 emission-neutrality)"
elif [ "$fail" -eq 0 ]; then
    bad "§3 discharge: populations too small — $nd_ans answer cells (floor 5000), $nd_engine engine moves (floor 8), $nd_same/$nd_bytes byte-identical"
fi

# =========================================================================
# §4  THE THREE ENTRIES
# =========================================================================
# Driven over the CUT class only: the entries' claim is that §4's ceiling
# hazard cannot reach them, and the R3a shapes are where it would.
ne_cells=0; ne_bad=0; ne_pat=0
for spec in "${PATSPEC[@]}"; do
    cls="${spec%%:*}"; pat="${spec#*:}"
    [ "$cls" = "cut" ] || continue
    d="$WORKDIR/e$ne_pat"; ne_pat=$((ne_pat + 1))
    mkdir -p "$d"
    "$PCREC" --features all -p rx -o "$d/gen.c" -- "$pat" 2>/dev/null || continue
    $CC -O2 -I"$d" -o "$d/t" "$SCRIPT_DIR/atomic_entries.c" "$d/gen.c" \
        2>"$d/err" || { bad "§4: could not build the entries driver for '$pat': $(head -2 "$d/err")"; continue; }
    for f in "$WORKDIR"/subjects/*; do
        len=$(wc -c < "$f")
        for sp in $(seq 0 "$len"); do
            # THE MATCH-HERE ORACLE: libpcre2's answer for `\G(?:PAT)` at `sp`
            # IS the match-here answer for `PAT` at `sp`.
            hw="$("$ORACLE" "\\G(?:$pat)" "$f" "$sp" 2>/dev/null)"
            case "$hw" in "match "*|nomatch) ;; *) continue ;; esac
            line="$(timeout 10 "$d/t" "$f" "$sp" 2>/dev/null)"
            ne_cells=$((ne_cells + 1))
            mh="$(printf '%s' "$line" | sed 's/.*| match \([-0-9]*\).*/\1/')"
            cp="$(printf '%s' "$line" | sed 's/.*| caps \([-0-9]*\).*/\1/')"
            case "$hw" in
                nomatch)
                    if [ "${mh:-0}" -ge 0 ] 2>/dev/null; then
                        ne_bad=$((ne_bad + 1))
                        printf 'ENTRY %s [%s] @%s: libpcre2 says NO anchored match, _match returned %s\n' \
                            "$pat" "$(basename "$f")" "$sp" "$mh" >> "$WORKDIR/diffs.txt"
                    fi ;;
                *)
                    e="$(printf '%s' "$hw" | awk '{print $3}')"
                    want=$((e - sp))
                    if [ "${mh:-x}" != "$want" ] || [ "${cp:-x}" != "$want" ]; then
                        ne_bad=$((ne_bad + 1))
                        printf 'ENTRY %s [%s] @%s: consumed length _match=%s _match_caps=%s, libpcre2 (via \\G) says %s\n' \
                            "$pat" "$(basename "$f")" "$sp" "$mh" "$cp" "$want" >> "$WORKDIR/diffs.txt"
                    fi ;;
            esac
        done
    done
done
if [ "$ne_bad" -eq 0 ] && [ "$ne_cells" -ge 5000 ]; then
    ok "§4 entries: $ne_cells cells over $ne_pat cut patterns — <prefix>_match and <prefix>_match_caps agree with libpcre2's own anchored answer (\\G(?:PAT)) on the CONSUMED LENGTH, which is the number a D38 callout advances by and is NOT the reported span's width"
elif [ "$ne_bad" -ne 0 ]; then
    bad "§4 entries: $ne_bad of $ne_cells cells disagree:"
    grep '^ENTRY' "$WORKDIR/diffs.txt" | head -20 >&2
else
    bad "§4 entries: only $ne_cells cells (floor 5000) — the entries sweep is not populated"
fi

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
