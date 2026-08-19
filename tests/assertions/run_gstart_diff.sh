#!/usr/bin/env bash
# tests/assertions/run_gstart_diff.sh — [M6.2] WAVE D's behavioural
# instrument for `\G`: four things tests/assertions/gpos.rxt structurally
# cannot assert, each against libpcre2.
#
#   §1  CONTIGUITY THROUGH THE FIND-ALL LOOP. `\G`'s meaning under
#       docs/spec/match_api.md §3.1 is "contiguous with the previous match"
#       (assertions_design.md §4.3), and a `.rxt` block drives ONE search.
#       `\G\w+` on "ab cd" reports (0,2) from a single search whether or not
#       the `\G` is honoured on the SECOND call — and the second call is what
#       separates a tokenizer from a scanner.
#
#   §2  THE SUBJECT SWEEP, both pcrec engines against libpcre2 over a
#       generated space with startpos taking EVERY value in [0, n]. The
#       `.rxt` corpus pins chosen cells; this sweeps.
#
#   §3  THE TWO ENTRIES (R30 E8's replacement obligation), SCOPED. A
#       fully-`\G` pattern's `search` and match-here entries must AGREE; a
#       partial-`\G` pattern's must DISAGREE at `startpos > 0`. Asserting
#       either rule over both classes would be red on correct behaviour.
#
#   §4  THE IMPOSSIBLE SHAPES `a\Gb` AND `x\G`, which are absent from
#       gpos.rxt BY NAME because they are K28 spellings — a single-dead-state
#       artifact is not warnings-clean under the harness's `-O1` GENCFLAGS
#       (docs/dev/known_issues.md K28, measured `-O1`-only). This script
#       compiles at `-O2`, where K28 does not fire, so the shapes are
#       asserted here instead of going unasserted.
#
# THERE IS NO SECOND ORACLE IN THIS SCRIPT AND THAT IS THE STRONGEST ORACLE
# STATEMENT IN THE MODULE. Wave C's run_mline_diff.sh runs python3 `re`
# beside libpcre2 — not to judge pcrec (D26 makes libpcre2 the truth) but to
# catch this kind of script driving the oracle WRONGLY, since python shares no
# code with libpcre2. **python has no `\G` at all**: `re.compile(r"\G")`
# raises `bad escape \G`, and there is no flag or rewriting that expresses it.
# So that arm cannot run on the patterns under test. What it CAN still do is
# validate the plumbing, and §0 below is that: the same subjects, the same
# startpos values, the same oracle invocation, over the `\G`-FREE CONTROL
# patterns this sweep already carries. A wrong startpos convention or a
# subject that lost a byte shows up there and nowhere else.
#
# Usage: bash tests/assertions/run_gstart_diff.sh
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
    if [ "$KEEP" = "1" ]; then echo "gstart-diff: KEEP=1, temp dir: $WORKDIR" >&2
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
# WORD-BOUNDARY-RICH AND GAP-RICH BY CONSTRUCTION, which is `\G`'s analogue of
# wave C's newline-rich rule. `\G`'s find-all meaning is about where a match
# ENDS and the next one is asked to begin, so a subject set with no internal
# gaps would measure only the first iteration — the mistake §3.7.1 records
# under a different construct (a probe whose subject had no newline in it and
# measured nothing).
python3 - "$WORKDIR/subjects" <<'PY'
import itertools, os, sys
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
alpha = "ab x"          # two word bytes, a non-word byte, a space
subs = []
# EXHAUSTIVE up to length 3 over {a, b, x, ' '} — 85 subjects. Exhaustive
# rather than curated so every gap placement (leading, trailing, doubled,
# absent, adjacent to a token) is present by ENUMERATION rather than by
# someone remembering to add it.
for n in range(0, 4):
    for t in itertools.product(alpha, repeat=n):
        subs.append("".join(t))
# LENGTH 4-8, curated to the shapes exhaustion at those lengths would be spent
# on: tokens separated by single and multiple gaps, and the `foo`/`bar`
# alphabet the partial-`\G` patterns are written over.
subs += ["xfoo bar", "foo bar", "barfoo", " foo bar", "foo  bar", "ab cd ef",
         "ab  cd", " ab cd ", "aaa bbb", "a b c d", "abcd", "    ", "a   b",
         "foofoo", "xfoofoo", "12 34 56", "1234", "\nfoo", "foo\nbar",
         "a\nb\nc"]
# LONGER ONES: a run long enough that a find-all loop takes many trips, and
# one whose FIRST token is followed immediately by a gap (where a contiguous
# tokenizer must stop after ONE match and a scanner would keep going).
subs += ["ab" * 16, ("tok " * 8).strip(), "aaaaaaaa bbbbbbbb",
         "a" + " " * 20 + "b", "x" * 40, "ab cd" + " " * 8 + "ef"]
for i, s in enumerate(subs):
    with open(os.path.join(out, "s%04d" % i), "wb") as f:
        f.write(s.encode("latin-1"))
print(len(subs))
PY
NSUBJ=$(ls "$WORKDIR/subjects" | wc -l)
if [ "$NSUBJ" -lt 100 ]; then
    bad "subject generation produced only $NSUBJ subjects — the sweep has no space"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# ---- the patterns --------------------------------------------------------
# THREE CLASSES, and the classification is what §3 asserts on, so it is data
# here rather than a rule applied later.
#
#   full     every branch carries `\G`   -> start_max = startpos, entries AGREE
#   partial  some branch does not        -> start_max = n, entries DISAGREE
#   dead     `\G` after a consumed byte  -> never matches (§4)
#   control  no `\G` at all              -> the python plumbing arm (§0)
PATSPEC=(
    "full:\\G"
    "full:\\Gfoo"
    "full:\\Gx"
    "full:\\Ga+"
    "full:\\Gab"
    "full:\\G[ab]+"
    "full:\\Gabc|\\Gxy"
    "full:\\G(?:a|b)+"
    "full:\\Ga|\\Gb"
    "full:\\A\\Gx"
    "partial:\\Gfoo|bar"
    "partial:\\Ga|b"
    "partial:x|\\Gy"
    "partial:\\Gab|b"
    "partial:\\G[ab]+|xx"
    # THE D63-PREFILTER POPULATION, and its absence was a real gap. Sabotage
    # S82 (the prefilter bounded at `start > 0` instead of `start > startpos`)
    # is reachable ONLY by a pattern carrying BOTH a `(?m)^` branch — which is
    # what makes the candidate set narrow enough to emit a memchr — and a `\G`
    # branch, which is what puts a live state at `start == startpos` that the
    # derivation never looked at. The first draft of this sweep had neither
    # spelling, so S82 scored `gstartdiff: 0 fail` against a sabotage that
    # loses matches, and only tests/assertions/gpos.rxt section 5 caught it.
    # A sweep that does not contain the shape its own soundness bound protects
    # is the population failure S48 and S78 both record, one instrument over.
    "partial:(?m)^a|\\Gb"
    "partial:\\Ga|(?m)^b"
    "partial:\\Gxy|(?m)^ab"
    "dead:a\\Gb"
    "dead:x\\G"
    "dead:ab\\Gc"
    "control:foo"
    "control:[ab]+"
    "control:a|b"
)

gen() { # gen <outdir> <prefix> <pattern> [extra pcrec args]
    local d="$1" pfx="$2" pat="$3"; shift 3
    mkdir -p "$d"
    "$PCREC" --features all -p "$pfx" "$@" -o "$d/gen.c" -- "$pat" 2>"$d/err" || return 1
    $CC -O2 -I"$d" -c -o "$d/gen.o" "$d/gen.c" 2>>"$d/err" || return 1
}

# =========================================================================
# §0 + §2  THE SUBJECT SWEEP
# =========================================================================
# STARTPOS TAKES EVERY VALUE IN [0, n], not the two values wave C's sweep
# used. For `(?m)` a couple of startpos values suffice because the construct's
# truth is a fact about the SUBJECT; `\G`'s truth is a fact about the
# ARGUMENT, so a sweep that fixes the argument measures nothing about the
# construct. This is the same reason gpos.rxt is written almost entirely in
# `ms`/`ns` cells.
npat=0; ncells=0; ndiff=0; nvm=0; nskip=0; nthree=0
: > "$WORKDIR/diffs.txt"
: > "$WORKDIR/oracle.tsv"
dispatchlist=""
for spec in "${PATSPEC[@]}"; do
    cls="${spec%%:*}"; pat="${spec#*:}"
    d="$WORKDIR/p$npat"; npat=$((npat + 1))
    if ! gen "$d" rx "$pat"; then
        bad "could not build a DFA artifact for '$pat': $(head -2 "$d/err")"
        continue
    fi
    $CC -O2 -I"$d" -o "$d/t" "$ROOT_DIR/tests/fuzz/fuzz_driver.c" "$d/gen.o" \
        2>>"$d/err" || { bad "could not link the DFA driver for '$pat'"; continue; }
    dv="$d/vm"
    if ! gen "$dv" rx "$pat" --engine=vm; then
        bad "could not build a VM artifact for '$pat': $(head -2 "$dv/err")"
        continue
    fi
    $CC -O2 -I"$dv" -o "$dv/t" "$ROOT_DIR/tests/fuzz/fuzz_driver.c" "$dv/gen.o" \
        2>>"$dv/err" || { bad "could not link the VM driver for '$pat'"; continue; }

    # THE POPULATION CHECK, read off the artifact rather than assumed — the
    # same discipline run_mline_diff.sh applies to its scan-avoidance
    # mechanisms. A sweep over `\G` patterns whose artifacts never emitted the
    # three-way start dispatch would be green against a dispatch that is
    # wrong everywhere.
    dis="none"
    if grep -q '(start == startpos)' "$d/gen.c"; then dis="three-way"; nthree=$((nthree + 1))
    elif grep -q 'const size_t start_max = startpos' "$d/gen.c"; then dis="startpos-anchored"; nthree=$((nthree + 1))
    fi
    dispatchlist="$dispatchlist  $(printf '%-8s %-18s' "$cls" "$pat") $dis
"

    for f in "$WORKDIR"/subjects/*; do
        len=$(wc -c < "$f")
        for sp in $(seq 0 "$len"); do
            want="$("$ORACLE" "$pat" "$f" "$sp" 2>/dev/null)"
            case "$want" in
                "match "*|nomatch) ;;
                *) nskip=$((nskip + 1)); continue ;;
            esac
            printf '%s\t%s\t%s\t%s\t%s\n' "$cls" "$pat" "$(basename "$f")" "$sp" "$want" \
                >> "$WORKDIR/oracle.tsv"
            got="$("$d/t" "$f" "$sp" 2>/dev/null)"
            ncells=$((ncells + 1))
            if [ "$got" != "$want" ]; then
                ndiff=$((ndiff + 1))
                printf 'DFA %s [%s] startpos %s: pcrec %s / libpcre2 %s\n' \
                    "$pat" "$(basename "$f")" "$sp" "$got" "$want" >> "$WORKDIR/diffs.txt"
            fi
            gotv="$("$dv/t" "$f" "$sp" 2>/dev/null)"
            nvm=$((nvm + 1))
            if [ "$gotv" != "$want" ]; then
                ndiff=$((ndiff + 1))
                printf 'VM  %s [%s] startpos %s: pcrec %s / libpcre2 %s\n' \
                    "$pat" "$(basename "$f")" "$sp" "$gotv" "$want" >> "$WORKDIR/diffs.txt"
            fi
        done
    done
done

printf 'gstart-diff: the start dispatch each pattern'\''s DFA artifact emitted:\n%s' "$dispatchlist"

if [ "$nthree" -ge 10 ]; then
    ok "population: $nthree of $npat patterns emitted a \\G-aware start dispatch (a three-way \`start == startpos\` arm, or the \`start_max = startpos\` anchored form) — the sweep is exercising the machinery this wave added, not passing over patterns it never touched"
else
    bad "population: only $nthree of $npat patterns emitted a \\G-aware start dispatch. The sweep below would be green against a dispatch that is wrong on every pattern."
fi

if [ "$ndiff" -eq 0 ]; then
    ok "§2 differential: $ncells DFA cells and $nvm VM cells over $npat patterns x $NSUBJ subjects x every startpos in [0, n] agree with libpcre2 exactly"
else
    bad "§2 differential: $ndiff cells disagree with libpcre2:"
    head -30 "$WORKDIR/diffs.txt" >&2
fi

# ---- §0: the plumbing arm ------------------------------------------------
# python3 `re` against LIBPCRE2's OWN ANSWERS on the `\G`-FREE control
# patterns only. It says nothing about `\G` and is not meant to: what it can
# see is THIS SCRIPT driving the oracle wrongly — a startpos convention, a
# subject that lost a byte — because python shares no code with libpcre2. The
# `\G` patterns are SKIPPED and COUNTED, never silently passed.
python3 - "$WORKDIR/oracle.tsv" "$WORKDIR/subjects" > "$WORKDIR/py.txt" 2>&1 <<'PY'
import os, re, sys
tsv, subdir = sys.argv[1], sys.argv[2]
cache = {}
def subj(name):
    if name not in cache:
        cache[name] = open(os.path.join(subdir, name), "rb").read().decode("latin-1")
    return cache[name]
n = bad = skipped = 0
rxs = {}
for line in open(tsv):
    cls, pat, name, sp, want = line.rstrip("\n").split("\t", 4)
    if cls != "control":
        skipped += 1
        continue
    if pat not in rxs:
        rxs[pat] = re.compile(pat)
    m = rxs[pat].search(subj(name), int(sp))
    got = "nomatch" if m is None else "match %d %d" % (m.start(), m.end())
    n += 1
    if got != want:
        bad += 1
        if bad <= 10:
            print("PYDIFF %r [%s] startpos %s: python %s / libpcre2 %s"
                  % (pat, name, sp, got, want))
print("PYSTATS %d %d %d" % (n, bad, skipped))
PY
read -r _ npy npybad npyskip <<< "$(grep '^PYSTATS ' "$WORKDIR/py.txt")"
if [ "${npybad:-1}" -eq 0 ] && [ "${npy:-0}" -gt 1000 ]; then
    ok "§0 plumbing: python3 re and libpcre2 agree on all $npy cells of the \\G-FREE control patterns (${npyskip:-0} \\G cells skipped — python has no \\G at all, U11c) — the oracle is being driven correctly, which is all a second oracle can say about a construct it cannot express"
else
    bad "§0 plumbing: python3 re and libpcre2 disagree on ${npybad:-?} of ${npy:-?} control cells. That is a claim about THIS SCRIPT, not about pcrec — check the startpos convention and the subject bytes before believing anything above:"
    grep '^PYDIFF ' "$WORKDIR/py.txt" >&2
fi

# =========================================================================
# §1  CONTIGUITY THROUGH THE FIND-ALL LOOP
# =========================================================================
# THE ORACLE IS libpcre2 DRIVEN THROUGH THE SAME LOOP, not a list of expected
# spans. PCRE2's global iteration IS "call again with start_offset at the
# previous match's end", so the oracle for §3.1's loop is that loop with
# `pcre2_match` in it — which is what the shell loop below does with
# pcre2_oracle. Writing the expected token lists by hand would make this a
# check on somebody's arithmetic.
FA_PATS=('\G\w+' '\G[ab]+' '\Gfoo' '\G' '\Gfoo|bar' '\Ga|b' '[ab]+' '\w+')
fa_diff=0; fa_cells=0
: > "$WORKDIR/fadiffs.txt"
fi_n=0
# The named cell below addresses two of these artifacts by DIRECTORY, and the
# directories are recorded here as the loop builds them rather than derived
# from a hardcoded index. An index would still fail loudly if FA_PATS were
# reordered (the expected span lists would not match), but it would fail
# saying the wrong thing.
declare -A FA_DIR
for pat in "${FA_PATS[@]}"; do
    d="$WORKDIR/fa$fi_n"; fi_n=$((fi_n + 1))
    FA_DIR["$pat"]="$d"
    if ! gen "$d" fa "$pat"; then
        bad "find-all: could not build an artifact for '$pat': $(head -2 "$d/err")"
        continue
    fi
    $CC -O2 -I"$d" -o "$d/t" "$SCRIPT_DIR/gstart_findall.c" "$d/gen.o" \
        2>>"$d/err" || { bad "find-all: could not link the driver for '$pat': $(head -5 "$d/err")"; continue; }
    for f in "$WORKDIR"/subjects/*; do
        # THE ORACLE LOOP, §3.1's advance rule with libpcre2 as the matcher.
        # The empty-match advance is `+ 1`, which is what `fa_next_pos` is
        # under the byte encoding (tests/encseam/ is what pins that identity;
        # here it is a transcription, and the two agreeing is the point).
        len=$(wc -c < "$f"); p=0; want=""
        while [ "$p" -le "$len" ]; do
            r="$("$ORACLE" "$pat" "$f" "$p" 2>/dev/null)"
            case "$r" in "match "*) ;; *) break ;; esac
            s0=$(printf '%s' "$r" | cut -d' ' -f2)
            e0=$(printf '%s' "$r" | cut -d' ' -f3)
            want="$want${want:+ }$s0,$e0"
            if [ "$e0" -gt "$s0" ]; then p="$e0"; else p=$((s0 + 1)); fi
        done
        got="$("$d/t" "$f" 2>/dev/null)"
        fa_cells=$((fa_cells + 1))
        if [ "$got" != "$want" ]; then
            fa_diff=$((fa_diff + 1))
            printf 'FINDALL %s [%s]: pcrec "%s" / libpcre2-through-the-loop "%s"\n' \
                "$pat" "$(basename "$f")" "$got" "$want" >> "$WORKDIR/fadiffs.txt"
        fi
    done
done

if [ "$fa_diff" -eq 0 ] && [ "$fa_cells" -gt 500 ]; then
    ok "§1 contiguity: $fa_cells find-all runs over ${#FA_PATS[@]} patterns agree, span for span, with libpcre2 driven through the SAME §3.1 loop — \\G under that loop means \"contiguous with the previous match\", which is PCRE2's global-iteration semantics"
else
    bad "§1 contiguity: $fa_diff of $fa_cells find-all runs differ from libpcre2 through the same loop:"
    head -20 "$WORKDIR/fadiffs.txt" >&2
fi

# THE NAMED CELL, spelled out because the sweep above would report a
# divergence without saying what the property WAS. `\G[ab]+` over
# "ab cd ef"-shaped input must stop at the first gap; the `\G`-free twin must
# not. If the two ever produce the same list, `\G` has stopped meaning
# anything under the loop and every cell above is still green.
printf 'ab ab ab' > "$WORKDIR/tok"
tokg="$("${FA_DIR['\G[ab]+']}/t" "$WORKDIR/tok" 2>/dev/null)"
tokp="$("${FA_DIR['[ab]+']}/t" "$WORKDIR/tok" 2>/dev/null)"
if [ "$tokg" = "0,2" ] && [ "$tokp" = "0,2 3,5 6,8" ]; then
    ok "§1 named cell: \`\\G[ab]+\` on \"ab ab ab\" reports ONLY \"$tokg\" (it stops at the first gap) where the \\G-free \`[ab]+\` reports \"$tokp\" — the tokenizer/scanner distinction, which is the whole content of §4.3"
else
    bad "§1 named cell: \`\\G[ab]+\` on \"ab ab ab\" reported \"$tokg\" (expected \"0,2\") and \`[ab]+\` reported \"$tokp\" (expected \"0,2 3,5 6,8\")"
fi

# =========================================================================
# §3  THE TWO ENTRIES (R30 E8), SCOPED
# =========================================================================
# `<prefix>_match_caps` needs a VM artifact to be interesting on a
# capture-bearing pattern, but every pattern here is capture-free and the DFA
# artifact exports the entry unconditionally (F1). Both engines are driven,
# because §9.3's own correction is that the two match-here entries do NOT
# share a shape: the DFA's wraps `rx_search` plus a start filter, the VM's
# calls `rx_match_impl` directly. A test of one is not a test of the other.
ent_agree=0; ent_dis=0; ent_bad=0; ent_cells=0
: > "$WORKDIR/entdiffs.txt"
ei=0
for spec in "${PATSPEC[@]}"; do
    cls="${spec%%:*}"; pat="${spec#*:}"
    [ "$cls" = "full" ] || [ "$cls" = "partial" ] || continue
    for eng in "" "--engine=vm"; do
        d="$WORKDIR/e$ei"; ei=$((ei + 1))
        # shellcheck disable=SC2086
        if ! gen "$d" ge "$pat" $eng; then
            bad "entries: could not build '$pat' ${eng:-auto}: $(head -2 "$d/err")"
            continue
        fi
        $CC -O2 -I"$d" -o "$d/t" "$SCRIPT_DIR/gstart_entries.c" "$d/gen.o" \
            2>>"$d/err" || { bad "entries: could not link the driver for '$pat' ${eng:-auto}: $(head -5 "$d/err")"; continue; }
        for f in "$WORKDIR"/subjects/*; do
            len=$(wc -c < "$f")
            for sp in $(seq 0 "$len"); do
                line="$("$d/t" "$f" "$sp" 2>/dev/null)"
                sres="${line%% | *}"; hres="${line#* | }"
                ent_cells=$((ent_cells + 1))
                # The two entries AGREE on this cell when `search` found its
                # match AT the requested offset with the length the match-here
                # entry consumed, or when both found nothing.
                agree=0
                case "$sres" in
                    "search 1 "*)
                        ss=$(printf '%s' "$sres" | cut -d' ' -f3)
                        se=$(printf '%s' "$sres" | cut -d' ' -f4)
                        case "$hres" in
                            "here "*)
                                hl=$(printf '%s' "$hres" | cut -d' ' -f2)
                                if [ "$hl" -ge 0 ] 2>/dev/null &&
                                   [ "$ss" = "$sp" ] && [ "$((ss + hl))" = "$se" ]; then agree=1; fi ;;
                        esac ;;
                    "search 0")
                        case "$hres" in "here -1") agree=1 ;; esac ;;
                esac
                if [ "$cls" = "full" ]; then
                    if [ "$agree" = "1" ]; then ent_agree=$((ent_agree + 1))
                    else
                        ent_bad=$((ent_bad + 1))
                        printf 'FULL-\\G DISAGREEMENT %s %s [%s] startpos %s: %s\n' \
                            "$pat" "${eng:-auto}" "$(basename "$f")" "$sp" "$line" \
                            >> "$WORKDIR/entdiffs.txt"
                    fi
                else
                    if [ "$agree" = "1" ]; then ent_agree=$((ent_agree + 1))
                    else ent_dis=$((ent_dis + 1)); fi
                fi
            done
        done
    done
done

if [ "$ent_bad" -eq 0 ] && [ "$ent_cells" -gt 500 ]; then
    ok "§3 entries, FULLY-\\G half: every cell of every fully-\\G pattern has \`search\` and the match-here entry agreeing, on BOTH engines ($ent_cells cells total across both classes; $ent_agree agreed). This is R30 E8's replacement obligation: \`startpos\` IS threaded to the match-here entry — it is \`ctx->pos\` — so a pattern pinned to \`startpos\` in every branch cannot tell the two entries apart"
else
    bad "§3 entries: $ent_bad cells of FULLY-\\G patterns had the two entries disagree, which they must not:"
    head -20 "$WORKDIR/entdiffs.txt" >&2
fi

# THE OTHER HALF, and it is the reason §10 says to SCOPE this test. A partial
# `\G` pattern legitimately DISAGREES: `search` may find the `\G`-free branch
# at a later offset where the match-here entry, asked about one position,
# reports nothing. An unscoped "the entries agree" assertion would be RED ON
# CORRECT BEHAVIOUR here, so the disagreement is asserted to EXIST rather than
# tolerated.
if [ "$ent_dis" -gt 0 ]; then
    ok "§3 entries, PARTIAL-\\G half: $ent_dis cells where the two entries DISAGREE, as they must — \`search\` reports a \\G-free branch found at a later offset and the match-here entry rejects it through its start filter. This is also where §4.2's three start states are distinguishable from outside"
else
    bad "§3 entries, PARTIAL-\\G half: ZERO disagreeing cells over the partial-\\G patterns. Either the sweep never reached a startpos where the \\G-free branch matches later, or the match-here entry has stopped filtering by start — the second is a real defect and this half of the test exists to catch it."
fi

# =========================================================================
# §4  THE IMPOSSIBLE SHAPES
# =========================================================================
# `a\Gb` and `x\G` are absent from gpos.rxt by name (K28: a single-dead-state
# artifact is not warnings-clean under the harness's `-O1` GENCFLAGS). They
# are asserted here, where the compile is at `-O2`. The `dead:` class above
# already swept them against libpcre2 over every subject and startpos; this
# block states the PROPERTY, so a future change that made one of them match
# something fails with a sentence rather than with a cell reference.
# THE ORACLE ANSWERS ARE READ OFF §2's OWN TSV, not re-queried. §2 already
# asked libpcre2 about every one of these cells and recorded the answer; a
# second sweep would be ~1,300 more oracle subprocesses producing data this
# script already holds — and, worse, a second independent query that could
# quietly disagree with the one the differential was judged against. What is
# asserted here is that the `dead:` CLASSIFICATION is right, which is a
# property of those recorded answers.
dead_hits=0
dead_cells=$(awk -F'\t' '$1 == "dead"' "$WORKDIR/oracle.tsv" | wc -l)
while IFS=$'\t' read -r cls pat name sp want; do
    [ "$cls" = "dead" ] || continue
    case "$want" in "match "*)
        dead_hits=$((dead_hits + 1))
        echo "  libpcre2 MATCHED the supposedly-impossible '$pat' on $name at $sp: $want" >&2 ;;
    esac
done < "$WORKDIR/oracle.tsv"
if [ "$dead_hits" -eq 0 ] && [ "${dead_cells:-0}" -gt 300 ]; then
    ok "§4 impossible shapes: libpcre2 reports NO MATCH on all $dead_cells recorded cells of \`a\\Gb\`, \`x\\G\` and \`ab\\Gc\` — every subject at every startpos — and §2's sweep above found pcrec agreeing on every one of them — a \\G after a consumed byte is unsatisfiable, and it falls out of the subset construction with no special case (§4.2)"
else
    bad "§4 impossible shapes: libpcre2 matched $dead_hits cells of a pattern this wave classifies as impossible. The CLASSIFICATION is wrong, not pcrec — fix the PATSPEC class and re-derive §4.2's argument before touching any code."
fi

echo
echo "== Summary =="
echo "  §2 sweep     patterns $npat  subjects $NSUBJ  DFA cells $ncells  VM cells $nvm  divergences $ndiff  oracle-skipped $nskip"
echo "  §1 find-all  runs $fa_cells  divergences $fa_diff"
echo "  §3 entries   cells $ent_cells  agree $ent_agree  legitimate-disagreements $ent_dis  bad $ent_bad"
echo "  §0 plumbing  python-verified control cells $npy  disagreements $npybad"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
