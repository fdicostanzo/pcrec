#!/usr/bin/env bash
# tests/assertions/run_kreset_diff.sh — [M6.2] WAVE E's behavioural instrument
# for `\K`: four things tests/assertions/kreset.rxt structurally cannot
# assert, each against libpcre2.
#
#   §1  THE SUBJECT SWEEP, both pcrec engines against libpcre2 over a
#       generated space with startpos taking EVERY value in [0, n]. The
#       `.rxt` corpus pins chosen cells; this sweeps. The startpos axis is
#       swept exhaustively for wave D's reason applied to a different
#       quantity: `\K` moves the REPORTED START, which is the one number in
#       the match API a nonzero startpos also moves, so a sweep that fixed
#       the argument could not tell "the VM reported its `\K` write" from
#       "the prefilter's span start was written out" (§6.3 rule 1).
#
#   §2  THE THREE ENTRIES, which is R30 E8's obligation and the reason this
#       script exists at all. A `.rxt` block drives `<prefix>_search` and
#       compares one span; §6.3 rule 3's hazard is in the OTHER TWO entries
#       and in a number no span comparison contains — the CONSUMED LENGTH.
#       See "the match-here oracle" below, which is the part of this script
#       worth reading before the code.
#
#   §3  THE ADVANCE, stated as a property rather than as a cell reference:
#       on `ab\K` the reported span is (2,2) and the consumed length is 2.
#       A D38 callout advances by the entry's RETURN, so an entry deriving
#       that return from `caps` would return 0 here and a callout loop would
#       never move. This is asserted by name because it is the one cell in
#       the module whose failure is an infinite loop in somebody else's code.
#
#   §4  THE `--engine=dfa` REFUSAL (§6.3 rule 2, D44.6). `\K` is the first
#       construct in the tree to reach that branch of the override, which was
#       written at [M4.5b] and described in src/opt/select_engine.c as "empty
#       BY POPULATION, not by omission" ever since.
#
# THE MATCH-HERE ORACLE IS `\G`, AND THAT IS THE IDEA THIS SCRIPT TURNS ON.
# `<prefix>_match`/`<prefix>_match_caps` answer about EXACTLY `ctx->pos`, and
# `tests/fuzz/pcre2_oracle` has no anchored mode to ask libpcre2 the same
# question with. But PCRE2 already has a spelling for "match here and nowhere
# else": `\G` is true iff `pos == startpos`, so libpcre2's answer for
# `\G(?:PAT)` at startpos `sp` IS the match-here answer for `PAT` at `sp` —
# from libpcre2's own engine, with no arithmetic of this script's own. Two
# things then fall out for free, and they are precisely §6.3 rule 3's two
# halves:
#
#     the FILTER   libpcre2 matching `\G(?:PAT)` at `sp` means a genuine
#                  anchored match exists there, so `<prefix>_match` must
#                  return >= 0. On `a\Kb` at 0 it does, and the DFA-shaped
#                  entry §6.3 quotes returns -1 — the landing condition's
#                  exact cell, produced by an oracle rather than asserted.
#     the RETURN   the oracle's match END minus `sp` IS the consumed length,
#                  because the match began at `sp` by construction. That
#                  number is generally NOT `end - start` on a `\K` pattern,
#                  which is what makes it a real second assertion instead of
#                  a restatement of the span.
#
# The wrap is `\G(?:PAT)` and not `\GPAT`: a top-level alternation would
# otherwise bind only its first branch to the `\G`, silently turning the
# oracle into a different question for exactly the patterns §2 cares most
# about.
#
# THERE IS NO SECOND ORACLE FOR `\K` ITSELF, for wave D's reason one construct
# over: python3 `re` has no `\K` at all (`re.compile(r"a\Kb")` raises `bad
# escape \K`). What §0 does with python is what wave D does — drive it over
# the sweep's own `\K`-FREE CONTROL patterns, same subjects, same startpos
# values, same oracle invocation, so a wrong startpos convention or a subject
# that lost a byte shows up there and nowhere else. That is all a second
# oracle can say about a construct it cannot express.
#
# Usage: bash tests/assertions/run_kreset_diff.sh
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
    if [ "$KEEP" = "1" ]; then echo "kreset-diff: KEEP=1, temp dir: $WORKDIR" >&2
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
# ALTERNATION-RICH AND REPEAT-RICH BY CONSTRUCTION, which is `\K`'s analogue
# of wave C's newline-rich rule and wave D's gap-rich one. The cells that can
# break `\K` are the ones where a `\K` is crossed on a path that LOSES, so the
# subject set has to contain the near-misses that force a retreat: runs of the
# loop body followed by something the follow cannot take, and prefixes shared
# between an alternation's branches.
python3 - "$WORKDIR/subjects" <<'PY'
import itertools, os, sys
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
alpha = "abx"
subs = []
# EXHAUSTIVE up to length 3 over {a, b, x} — 40 subjects. Exhaustive rather
# than curated so every "run of a, then the wrong byte" prefix the retreat
# cells need is present by ENUMERATION rather than by someone remembering it.
# Length 4 was measured and CUT: it quadruples the sweep for shapes the
# curated list below already covers, and the cost is real — every cell here
# costs TWO oracle subprocesses (the pattern and its `\G(?:...)` match-here
# twin) plus two driver runs, so this sweep is subprocess-bound rather than
# compute-bound and its size is a scheduling decision, not a thoroughness one.
for n in range(0, 4):
    for t in itertools.product(alpha, repeat=n):
        subs.append("".join(t))
# LENGTH 5-8, over the alphabets the composed and capture patterns are
# written in, plus the newline shapes `\Z`/`$`/`(?m)$` need.
subs += ["aaaab", "aaabb", "ababc", "ababab", "abcabc", "aabbcc",
         "xaaab", "xxaaab", "axc", "xaxc", "abcd", "xabcd",
         "ab\n", "a\nb", "ab\nab", "\nab", "abab\n", "a\nab",
         " ab ", "ab ab", "x ab", "foo", "xfoo", "foobar"]
# LONGER: a run long enough that a greedy loop retreats many times before the
# follow succeeds, and one where it never does.
subs += ["a" * 16 + "b", "a" * 16 + "ab", "a" * 24, "ab" * 12,
         ("ab" * 8) + "c", "a" * 12 + "x" + "a" * 12]
for i, s in enumerate(subs):
    with open(os.path.join(out, "s%04d" % i), "wb") as f:
        f.write(s.encode("latin-1"))
print(len(subs))
PY
NSUBJ=$(ls "$WORKDIR/subjects" | wc -l)
if [ "$NSUBJ" -lt 60 ]; then
    bad "subject generation produced only $NSUBJ subjects — the sweep has no space"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# ---- the patterns --------------------------------------------------------
# THREE CLASSES, and the classification is data here rather than a rule
# applied later, because §2 and §3 assert different things about each.
#
#   kreset   contains a `\K`                -> the population under test
#   zerolen  a `\K` at the END of the match -> reported start == reported end
#            while bytes were consumed; §3's own population
#   control  no `\K` at all                 -> §0's python plumbing arm
PATSPEC=(
    "kreset:a\\Kb"
    "kreset:\\Kab"
    "kreset:a\\Kb\\Kc"
    "kreset:(?:a\\K|ax)c"
    "kreset:(?:ab\\K|a)b"
    "kreset:(?:a\\Kb|ab\\Kc)d"
    "kreset:a\\Kb|c"
    "kreset:(?:a\\K)*ab"
    "kreset:(?:a\\K)*b"
    "kreset:(?:a\\Kb)*c"
    "kreset:(?:a\\K){2,}b"
    "kreset:(?:a\\K)?b"
    "kreset:(?:a\\K|b)+c"
    "kreset:(a)\\K(b)"
    "kreset:(a\\K)*b"
    "kreset:a{2,4}\\Kb"
    "kreset:[ab]*\\K[bc]+"
    "kreset:(?:ab)+\\Kc"
    "kreset:a\\Kb\\z"
    "kreset:a\\Kb\\Z"
    "kreset:a\\Kb\$"
    "kreset:\\ba\\Kb\\b"
    "kreset:\\Ga\\Kb"
    "kreset:a\\Kb|\\Gc"
    "kreset:(?m)^a\\Kb"
    "zerolen:ab\\K"
    "zerolen:ab\\Kc?"
    "zerolen:a*\\K"
    "zerolen:(?:a\\Kb)*\\K"
    "control:a?b"
    "control:[ab]+"
    "control:a|b"
    "control:(?:ab)+c"
)

gen() { # gen <outdir> <prefix> <pattern> [extra pcrec args]
    local d="$1" pfx="$2" pat="$3"; shift 3
    mkdir -p "$d"
    "$PCREC" --features all -p "$pfx" "$@" -o "$d/gen.c" -- "$pat" 2>"$d/err" || return 1
    $CC -O2 -I"$d" -c -o "$d/gen.o" "$d/gen.c" 2>>"$d/err" || return 1
}

# =========================================================================
# §0 + §1  THE SUBJECT SWEEP
# =========================================================================
npat=0; ncells=0; ndiff=0; nvm=0; nskip=0; nwrite=0
: > "$WORKDIR/diffs.txt"
: > "$WORKDIR/oracle.tsv"
sitelist=""
for spec in "${PATSPEC[@]}"; do
    cls="${spec%%:*}"; pat="${spec#*:}"
    d="$WORKDIR/p$npat"; npat=$((npat + 1))
    if ! gen "$d" rx "$pat"; then
        bad "could not build a default-engine artifact for '$pat': $(head -2 "$d/err")"
        continue
    fi
    $CC -O2 -I"$d" -o "$d/t" "$ROOT_DIR/tests/fuzz/fuzz_driver.c" "$d/gen.o" \
        2>>"$d/err" || { bad "could not link the default driver for '$pat'"; continue; }
    dv="$d/vm"
    if ! gen "$dv" rx "$pat" --engine=vm; then
        bad "could not build a --engine=vm artifact for '$pat': $(head -2 "$dv/err")"
        continue
    fi
    $CC -O2 -I"$dv" -o "$dv/t" "$ROOT_DIR/tests/fuzz/fuzz_driver.c" "$dv/gen.o" \
        2>>"$dv/err" || { bad "could not link the VM driver for '$pat'"; continue; }

    # THE POPULATION CHECK, read off the ARTIFACT rather than assumed — the
    # discipline run_mline_diff.sh and run_gstart_diff.sh both apply to their
    # own machinery. A sweep over `\K` patterns whose artifacts never emitted
    # the trailed write and the `\K`-aware caps_out would be green against a
    # `\K` that compiled to nothing at all.
    site="none"
    if grep -q 'RX_SET(0, (ptrdiff_t)pos)' "$d/gen.c" \
       && grep -q 'w->stv\[0\] != PCREC_UNSET' "$d/gen.c"; then
        site="write+capsout"; nwrite=$((nwrite + 1))
    elif grep -q 'RX_SET(0, (ptrdiff_t)pos)' "$d/gen.c"; then
        site="write-ONLY"
    elif grep -q 'w->stv\[0\] != PCREC_UNSET' "$d/gen.c"; then
        site="capsout-ONLY"
    fi
    sitelist="$sitelist  $(printf '%-8s %-20s' "$cls" "$pat") $site
"

    for f in "$WORKDIR"/subjects/*; do
        len=$(wc -c < "$f")
        for sp in $(seq 0 "$len"); do
            want="$("$ORACLE" "$pat" "$f" "$sp" 2>/dev/null)"
            case "$want" in
                "match "*|nomatch) ;;
                *) nskip=$((nskip + 1)); continue ;;
            esac
            # THE MATCH-HERE ORACLE, asked in the same pass so §2 never
            # re-queries libpcre2 for a cell §1 already has an answer for.
            hwant="$("$ORACLE" "\\G(?:$pat)" "$f" "$sp" 2>/dev/null)"
            printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$cls" "$pat" "$(basename "$f")" \
                "$sp" "$want" "$hwant" >> "$WORKDIR/oracle.tsv"
            # PER-PATTERN too, and this is a runtime decision rather than
            # bookkeeping: §2 drives 2 engines x every \K pattern, and reading
            # the whole sweep's TSV once per (pattern, engine) is a shell loop
            # over millions of lines it then discards. One file per pattern
            # turns that into exactly the cells that pattern owns.
            printf '%s\t%s\t%s\t%s\n' "$(basename "$f")" "$sp" "$want" "$hwant" \
                >> "$d/cells.tsv"
            got="$("$d/t" "$f" "$sp" 2>/dev/null)"
            ncells=$((ncells + 1))
            if [ "$got" != "$want" ]; then
                ndiff=$((ndiff + 1))
                printf 'DEFAULT %s [%s] startpos %s: pcrec %s / libpcre2 %s\n' \
                    "$pat" "$(basename "$f")" "$sp" "$got" "$want" >> "$WORKDIR/diffs.txt"
            fi
            gotv="$("$dv/t" "$f" "$sp" 2>/dev/null)"
            nvm=$((nvm + 1))
            if [ "$gotv" != "$want" ]; then
                ndiff=$((ndiff + 1))
                printf 'VM      %s [%s] startpos %s: pcrec %s / libpcre2 %s\n' \
                    "$pat" "$(basename "$f")" "$sp" "$gotv" "$want" >> "$WORKDIR/diffs.txt"
            fi
        done
    done
done

printf 'kreset-diff: the \\K machinery each pattern'\''s artifact emitted:\n%s' "$sitelist"

NK=$(printf '%s\n' "${PATSPEC[@]}" | grep -c -v '^control:')
if [ "$nwrite" -ge "$NK" ]; then
    ok "population: all $nwrite \\K patterns emitted BOTH halves of the machinery — the trailed \`RX_SET(0, pos)\` write and the \`\\K\`-aware \`caps_out\` that reads slot 0. Either half alone is a build the sweep below would pass over: a write nothing reads reports the prefilter's start, and a reader with no writer reports it too"
else
    bad "population: only $nwrite of $NK \\K patterns emitted both halves of the \\K machinery (see the table above). The sweep below would be green against a \\K that compiled to nothing."
fi

# THE DEFAULT ENGINE IS THE HYBRID HERE, and that is the point of running it:
# under `auto` a `\K` artifact gets the capture-erased DFA as a prefilter, so
# `start` in `caps_out` IS the reverse pass's answer. §6.3 rule 1 says that
# number must never be written out when a `\K` was crossed, and this arm is
# where a build that wrote it disagrees with libpcre2. `--engine=vm` turns the
# prefilter OFF (R21 E-6), so the two arms are genuinely two derivations.
if [ "$ndiff" -eq 0 ]; then
    ok "§1 differential: $ncells default-engine (hybrid, prefilter LIVE) cells and $nvm --engine=vm (prefilter OFF) cells over $npat patterns x $NSUBJ subjects x every startpos in [0, n] agree with libpcre2 exactly"
else
    bad "§1 differential: $ndiff cells disagree with libpcre2:"
    head -30 "$WORKDIR/diffs.txt" >&2
fi

# ---- §0: the plumbing arm ------------------------------------------------
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
    cls, pat, name, sp, want, hwant = line.rstrip("\n").split("\t", 5)
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
    ok "§0 plumbing: python3 re and libpcre2 agree on all $npy cells of the \\K-FREE control patterns (${npyskip:-0} \\K cells skipped — python has no \\K at all, U11d) — the oracle is being driven correctly, which is all a second oracle can say about a construct it cannot express"
else
    bad "§0 plumbing: python3 re and libpcre2 disagree on ${npybad:-?} of ${npy:-?} control cells. That is a claim about THIS SCRIPT, not about pcrec — check the startpos convention and the subject bytes before believing anything above:"
    grep '^PYDIFF ' "$WORKDIR/py.txt" >&2
fi

# =========================================================================
# §2  THE THREE ENTRIES (R30 E8; assertions_design.md §6.3 rule 3)
# =========================================================================
# Both engines are driven even though a `\K` pattern is always VM-forced, and
# that is not redundancy: `--engine=vm` additionally turns the PREFILTER off,
# and `<prefix>_match_caps` reads the same `caps_out` the search entry does.
# A build whose `caps_out` was right only when a prefilter had run would pass
# one arm and fail the other.
ent_cells=0; ent_bad=0; ent_nz=0; ent_lenmismatch=0
: > "$WORKDIR/entdiffs.txt"
ei=0; pidx=-1
for spec in "${PATSPEC[@]}"; do
    cls="${spec%%:*}"; pat="${spec#*:}"
    pidx=$((pidx + 1))
    [ "$cls" = "control" ] && continue
    [ -s "$WORKDIR/p$pidx/cells.tsv" ] || { bad "entries: §1 recorded no cells for '$pat' (index $pidx) — the two sections have drifted apart"; continue; }
    for eng in "" "--engine=vm"; do
        d="$WORKDIR/e$ei"; ei=$((ei + 1))
        # shellcheck disable=SC2086
        if ! gen "$d" ke "$pat" $eng; then
            bad "entries: could not build '$pat' ${eng:-auto}: $(head -2 "$d/err")"
            continue
        fi
        $CC -O2 -I"$d" -o "$d/t" "$SCRIPT_DIR/kreset_entries.c" "$d/gen.o" \
            2>>"$d/err" || { bad "entries: could not link the driver for '$pat' ${eng:-auto}: $(head -5 "$d/err")"; continue; }

        # ONE DRIVER PROCESS PER ARTIFACT, and one awk process to compare —
        # not one of each per CELL. The first draft of this section spawned
        # about six processes per cell (the driver plus a `sed` and four
        # `cut`s), and the whole section then cost 9m18s wall against 2m22s
        # user: three quarters of the time was spent NOT running anything
        # under test. Nothing about WHAT is compared changed; only how many
        # times the shell forks to compare it.
        #
        # THE TWO STREAMS ARE MATCHED POSITIONALLY, which is safe only because
        # the driver emits exactly one line per input line and hard-fails
        # otherwise (see kreset_entries.c's batch loop). The awk below asserts
        # the two line counts agree anyway, because "positionally" is exactly
        # the assumption that turns a dropped line into 23,000 wrong answers
        # reported against the wrong cells.
        awk -F'\t' -v d="$WORKDIR/subjects/" '{print d $1 " " $2}' \
            "$WORKDIR/p$pidx/cells.tsv" > "$d/in.txt"
        "$d/t" < "$d/in.txt" > "$d/out.txt" 2>/dev/null \
            || { bad "entries: the driver for '$pat' ${eng:-auto} failed on its batch input"; continue; }
        nin=$(wc -l < "$d/in.txt"); nout=$(wc -l < "$d/out.txt")
        if [ "$nin" -ne "$nout" ]; then
            bad "entries: the driver for '$pat' ${eng:-auto} returned $nout lines for $nin cells — the positional match below would report every answer against the wrong cell"
            continue
        fi
        eval "$(awk -v pat="$pat" -v eng="${eng:-auto}" -v out="$d/out.txt" \
                    -v diffs="$WORKDIR/entdiffs.txt" '
        BEGIN { FS = "\t"; cells = 0; bad = 0; nz = 0; lenmis = 0 }
        {
            name = $1; sp = $2 + 0; hwant = $4;
            if ((getline line < out) <= 0) { bad++; next }
            cells++;
            # The driver prints:  search ... | match <r> | caps <r> [<s> <e>]
            nseg = split(line, seg, / \| /);
            split(seg[2], m, " "); mret = m[2] + 0;
            ncap = split(seg[3], c, " ");   # c[1] == "caps"
            chl = c[2] + 0; chs = c[3] + 0; che = c[4] + 0;
            if (hwant == "nomatch") {
                # THE ORACLE SAYS NO ANCHORED MATCH AT sp. Both match-here
                # entries must say so too, and what this direction catches is
                # an entry that stopped filtering AT ALL rather than one
                # filtering on the wrong number.
                if (mret != -1 || ncap != 2 || chl != -1) {
                    bad++;
                    printf "OVER-ACCEPT %s %s [%s] sp %d: libpcre2 \\G(?:pat) says nomatch; entries say %s\n",
                           pat, eng, name, sp, line >> diffs;
                }
                next;
            }
            split(hwant, h, " "); os = h[2] + 0; oe = h[3] + 0;
            wlen = oe - sp;
            # THE FILTER HALF: a genuine anchored match exists here, so
            # neither entry may reject it. This is exactly the cell §6.3
            # names — `a\Kb` at ctx->pos == 0 — and the DFA-shaped entry it
            # quotes returns -1 on it.
            if (mret != wlen) {
                bad++;
                printf "FILTER/RETURN %s %s [%s] sp %d: <prefix>_match returned %d, consumed length is %d (libpcre2 \\G(?:pat) = %s)\n",
                       pat, eng, name, sp, mret, wlen, hwant >> diffs;
            }
            # THE CAPS ENTRY: the same length, plus the \K-adjusted span.
            if (chl != wlen || chs != os || che != oe) {
                bad++;
                printf "CAPS %s %s [%s] sp %d: match_caps gave len %d span (%d,%d); libpcre2 \\G(?:pat) gives len %d span (%d,%d)\n",
                       pat, eng, name, sp, chl, chs, che, wlen, os, oe >> diffs;
            }
            # THE NON-VACUITY COUNTER, and it is what stops this section
            # reading as a restatement of §1: count the cells where the
            # consumed length and the reported span WIDTH genuinely differ.
            # Those are the only cells that can tell a caps-derived return
            # from a position-derived one.
            if (wlen != oe - os) {
                nz++;
                if (mret == oe - os) lenmis++;
            }
        }
        END {
            printf "ent_cells=$((ent_cells + %d)); ent_bad=$((ent_bad + %d));",
                   cells, bad;
            printf " ent_nz=$((ent_nz + %d)); ent_lenmismatch=$((ent_lenmismatch + %d))\n",
                   nz, lenmis;
        }' "$WORKDIR/p$pidx/cells.tsv")"
    done
done

if [ "$ent_bad" -eq 0 ] && [ "$ent_cells" -gt 1000 ]; then
    ok "§2 entries: $ent_cells cells over both engines — \`<prefix>_match\` and \`<prefix>_match_caps\` agree with libpcre2's answer for \`\\G(?:pat)\` at the same offset, on the FILTER (an anchored match at ctx->pos is never rejected), the RETURN (the consumed length, not the reported span's width) and the SPAN (the \\K-adjusted one). R30 E8's obligation, both entries, both engines"
else
    bad "§2 entries: $ent_bad cells wrong out of $ent_cells:"
    head -20 "$WORKDIR/entdiffs.txt" >&2
fi

# THE NON-VACUITY HALF. Without it, §2 could be passing entirely on cells
# where the consumed length happens to equal the reported width — which is
# every cell of every `\K`-free pattern in the tree, and is what makes this
# obligation look already-discharged when it is not.
if [ "$ent_nz" -gt 100 ]; then
    ok "§2 non-vacuity: $ent_nz of those cells have a consumed length DIFFERENT from the reported span's width (the \\K was crossed), so the RETURN assertion above is a second fact and not a restatement of the SPAN one — and $ent_lenmismatch of them returned the span width, which is the number that must be 0"
else
    bad "§2 non-vacuity: only $ent_nz cells had the consumed length differ from the reported width. §6.3 rule 3's return-value half is being asserted on a population that cannot distinguish the two derivations."
fi

# =========================================================================
# §3  THE ADVANCE (D38's callout contract)
# =========================================================================
# NAMED, because a failure here is an infinite loop in a caller rather than a
# wrong answer, and a cell reference would not say that. `ab\K` on "ab" at 0:
# PCRE2 reports (2,2) and two bytes were consumed. A D38 callout advances by
# `<prefix>_match`'s return, so that return must be 2. An entry returning
# `caps[0][1] - caps[0][0]` returns 0 and the caller never moves.
d="$WORKDIR/adv"
if gen "$d" ke 'ab\K' && $CC -O2 -I"$d" -o "$d/t" "$SCRIPT_DIR/kreset_entries.c" "$d/gen.o" 2>>"$d/err"; then
    printf 'ab' > "$WORKDIR/advsubj"
    line="$("$d/t" "$WORKDIR/advsubj" 0 2>/dev/null)"
    mret=$(printf '%s' "$line" | sed 's/.*| match \([-0-9]*\).*/\1/')
    capspart="${line##*| caps }"
    cs=$(printf '%s' "$capspart" | cut -d' ' -f2)
    ce=$(printf '%s' "$capspart" | cut -d' ' -f3)
    if [ "$mret" = "2" ] && [ "$cs" = "2" ] && [ "$ce" = "2" ]; then
        ok "§3 advance: 'ab\\K' at ctx->pos 0 REPORTS the empty span (2,2) and RETURNS the consumed length 2. The two numbers differ by the whole match, which is what a D38 callout's advance depends on — \`caps[0][1] - caps[0][0]\` would be 0 here and the caller would never move"
    else
        bad "§3 advance: 'ab\\K' at 0 gave [$line]. Want the match entry returning 2 (bytes consumed) and match_caps reporting the span (2,2). If the return is 0 the entry is deriving it from caps — assertions_design.md §6.3 rule 3's second half."
    fi
else
    bad "§3 advance: could not build the 'ab\\K' fixture: $(head -3 "$d/err")"
fi

# =========================================================================
# §4  THE --engine=dfa REFUSAL (§6.3 rule 2; D44.6)
# =========================================================================
# BOTH DIRECTIONS, because a refusal test alone goes green on a compiler that
# has stopped accepting `\K` at all — the failure mode this milestone is
# otherwise full of. And the message must name the CONSTRUCT: the captures
# branch's `--no-captures` advice would be a lie here, since no flag makes a
# `\K` pattern DFA-compilable.
ref_out="$("$PCREC" --features assertions --engine=dfa -p rx -o "$WORKDIR/ref.c" -- 'a\Kb' 2>&1)"
ref_rc=$?
if [ "$ref_rc" -eq 0 ]; then
    bad "§4 refusal: 'a\\Kb' COMPILED under --engine=dfa. \\K has no DFA path at all (assertions_design.md §6.1), and D44.6's rule is that a request the pattern cannot honour is REFUSED, never silently downgraded"
elif ! printf '%s' "$ref_out" | grep -q '\\K' \
     || ! printf '%s' "$ref_out" | grep -q -- '--engine=dfa'; then
    bad "§4 refusal: 'a\\Kb' under --engine=dfa was refused but not BY ITS OWN NAME: $ref_out"
elif [ -e "$WORKDIR/ref.c" ]; then
    bad "§4 refusal: the refusal still wrote an output file"
elif ! "$PCREC" --features assertions -p rx -o "$WORKDIR/ok.c" -- 'a\Kb' >/dev/null 2>&1; then
    bad "§4 refusal: 'a\\Kb' does not compile on the DEFAULT engine either, so the refusal above proves nothing about \\K's routing"
else
    ok "§4 refusal: 'a\\Kb' compiles on the default engine and REFUSES under --engine=dfa naming the construct ($ref_out) — the first population src/opt/select_engine.c's second override branch has ever had, and it ran unchanged from [M4.5b]"
fi

# =========================================================================
# §5  THE FIND-ALL LOOP (docs/spec/match_api.md §3.1)
# =========================================================================
# `\K` is the first construct that can make a match report an EMPTY span after
# consuming bytes, and §3.1's loop has a separate arm for an empty span. So the
# question "does the documented caller protocol still terminate, still make
# progress, and still report what PCRE2 reports" is a NEW question at wave E,
# and it is not expressible as a `.rxt` cell — a block drives ONE search.
#
# THE ORACLE IS libpcre2 DRIVEN THROUGH THE SAME LOOP, wave D's rule and for
# wave D's reason: writing the expected token lists by hand would make this a
# check on somebody's arithmetic. The driver is `gstart_findall.c`, REUSED
# rather than copied — it is a transcription of §3.1 and the claim here is
# about §3.1, so a second transcription would prove nothing about the first.
#
# WHAT THE EMPTY ARM COSTS IS PART OF THE EXPECTATION, not a defect: on
# `ab\K` over "ababab" both sides report `2,2 6,6`, because after the empty
# reported span at 2 the loop advances ONE CHARACTER FROM THE REPORTED START
# (to 3) rather than from the match end (4), so the match beginning at 2 is
# not offered again. That is the loop the spec documents, running on both
# sides; a check that expected `2,2 4,4 6,6` would be asserting a different
# protocol.
FA_PATS=('ab\K' 'ab\Kc?' 'a\Kb' '\Ka' '(?:a\K)*b' 'a\Kb|c' '[ab]*\K[bc]+' 'a*\K')
FA_SUBJ=("abab" "ababab" "ab" "xabab" "aaab" "abcabc" "" "b" "aabbcc" "xaxbxc")
fa_cells=0; fa_diff=0; fa_empty=0
: > "$WORKDIR/fadiffs.txt"
fi_n=0
for pat in "${FA_PATS[@]}"; do
    d="$WORKDIR/fa$fi_n"; fi_n=$((fi_n + 1))
    if ! gen "$d" fa "$pat"; then
        bad "find-all: could not build an artifact for '$pat': $(head -2 "$d/err")"
        continue
    fi
    $CC -O2 -I"$d" -o "$d/t" "$SCRIPT_DIR/gstart_findall.c" "$d/gen.o" \
        2>>"$d/err" || { bad "find-all: could not link the driver for '$pat': $(head -5 "$d/err")"; continue; }
    for sj in "${FA_SUBJ[@]}"; do
        printf '%s' "$sj" > "$WORKDIR/fasubj"
        got="$("$d/t" "$WORKDIR/fasubj" 2>/dev/null)"
        # THE ORACLE'S OWN RUN OF THE SAME LOOP. Bounded at 64 reports so a
        # protocol bug that stops making progress fails as a DIVERGENCE here
        # rather than as a hang in a test suite.
        want="$(python3 - "$ORACLE" "$pat" "$WORKDIR/fasubj" <<'PY'
import subprocess, sys
oracle, pat, path = sys.argv[1], sys.argv[2], sys.argv[3]
n = len(open(path, "rb").read())
p = 0; out = []
while p <= n and len(out) < 64:
    r = subprocess.run([oracle, pat, path, str(p)],
                       capture_output=True, text=True).stdout.strip()
    if not r.startswith("match"): break
    a, b = int(r.split()[1]), int(r.split()[2])
    out.append((a, b))
    p = b if b > a else a + 1
print(" ".join("%d,%d" % t for t in out))
PY
)"
        fa_cells=$((fa_cells + 1))
        # THE EMPTY-ARM POPULATION, counted from the ORACLE's answers rather
        # than from pcrec's: a build that never reported an empty span must
        # not be able to make its own coverage claim. A reported `s,e` with
        # s == e is the loop's empty arm being taken.
        fa_empty=$((fa_empty + $(printf '%s' "$want" | tr ' ' '\n' \
            | awk -F, 'NF == 2 && $1 == $2 { c++ } END { print c + 0 }')))
        if [ "$got" != "$want" ]; then
            fa_diff=$((fa_diff + 1))
            printf 'FINDALL %s [%s]: pcrec [%s] / libpcre2-through-the-same-loop [%s]\n' \
                "$pat" "$sj" "$got" "$want" >> "$WORKDIR/fadiffs.txt"
        fi
    done
done
if [ "$fa_diff" -eq 0 ] && [ "$fa_cells" -gt 50 ] && [ "$fa_empty" -gt 5 ]; then
    ok "§5 find-all: $fa_cells runs of docs/spec/match_api.md §3.1's loop agree span for span with libpcre2 driven through the SAME loop, and $fa_empty of the reported matches are EMPTY spans the loop's empty arm had to handle ('ab\\K' over \"ababab\" is 2,2 6,6 on both sides) — the population no .rxt cell can reach, counted from the ORACLE so pcrec cannot vouch for its own coverage"
elif [ "$fa_diff" -eq 0 ] && [ "${fa_empty:-0}" -le 5 ]; then
    bad "§5 find-all: $fa_cells runs agree, but only $fa_empty EMPTY reported spans occurred across all of them. This section exists for the arm \\K makes reachable; with that population near zero it is a second copy of §1 wearing a different name."
else
    bad "§5 find-all: $fa_diff of $fa_cells runs disagree with libpcre2 driven through the same loop:"
    head -20 "$WORKDIR/fadiffs.txt" >&2
fi

# =========================================================================
# §6  `--no-captures` STILL REPORTS THE `\K` START
# =========================================================================
# NAMED, because the two options sound like they conflict and they do not.
# `--no-captures` is the generation axis that drops GROUP slots (RX_NCAPS 1,
# D42.1's inverse); the WHOLE-MATCH span is not a group and is delivered on
# every artifact. So a `\K` pattern compiled `--no-captures` is still
# VM-forced — `\K` is not a capture, it changes what is REPORTED — and still
# reports the post-`\K` start.
#
# It is asserted here rather than in the corpus because no `.rxt` block can
# pass the flag (`flags` maps `i` and nothing else), which is the same reason
# run_assertions_tests.sh §2b exists one construct family over. And it is
# asserted in BOTH halves: that the engine is still the VM (a build that let
# `--no-captures` route a `\K` pattern to the DFA would have to drop the
# construct silently) and that the ANSWER is still libpcre2's.
d="$WORKDIR/nocap"
if gen "$d" rx 'a\Kb' --no-captures \
   && $CC -O2 -I"$d" -o "$d/t" "$ROOT_DIR/tests/fuzz/fuzz_driver.c" "$d/gen.o" 2>>"$d/err"; then
    eng=$(grep -m1 '#define RX_ENGINE ' "$d/gen.c" | sed 's/.*"\(.*\)".*/\1/')
    printf 'ab' > "$WORKDIR/ncsubj"
    got="$("$d/t" "$WORKDIR/ncsubj" 0 2>/dev/null)"
    want="$("$ORACLE" 'a\Kb' "$WORKDIR/ncsubj" 0 2>/dev/null | awk '{print $1, $2, $3}')"
    if [ "$eng" != "vm" ]; then
        bad "§6 --no-captures: 'a\\Kb' compiled to engine '$eng', not the VM. \\K is not a capture — dropping group slots cannot make its reported start derivable on the DFA, so this artifact has lost the construct"
    elif [ "$got" != "$want" ]; then
        bad "§6 --no-captures: 'a\\Kb' on \"ab\" gave [$got], libpcre2 gives [$want]. The whole-match span is not a group; --no-captures must not touch it"
    else
        ok "§6 --no-captures: 'a\\Kb' still routes to the VM and still reports the post-\\K start ($got) — the flag drops GROUP slots, and the whole-match span is not a group"
    fi
else
    bad "§6 --no-captures: could not build the 'a\\Kb' --no-captures fixture: $(head -3 "$d/err")"
fi

echo
echo "== Summary =="
echo "  §1 sweep     patterns $npat  subjects $NSUBJ  default cells $ncells  vm cells $nvm  divergences $ndiff  oracle-skipped $nskip"
echo "  §2 entries   cells $ent_cells  wrong $ent_bad  length-differs-from-span $ent_nz"
echo "  §5 find-all  runs $fa_cells  divergences $fa_diff"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
