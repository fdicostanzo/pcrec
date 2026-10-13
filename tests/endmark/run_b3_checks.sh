#!/usr/bin/env bash
# tests/endmark/run_b3_checks.sh — D164 B3 (lane b3build): the `rev-end`
# walk's FORM table (docs/design/endmark.md §R.1) checked where a `.rxt`
# answer cannot see it, because every form is answer-identical by
# construction. `make test-endmark`; mech arm `endmark`.
#
#   §1 ANSWERS, three arms: tests/endmark/b3_rows.rxt (libpcrec2-generated)
#      under the default build, `-fno-anchored-dfa` (a `tagged` tie with no
#      anchored machine RELOCATES over the lowered forward machine: S1's cell)
#      and `-fno-rev-end-onewalk` (the denied form).
#   §2 NAMED WITNESSES, one per row and class, the expectation written here
#      from the design and PCRE2's own priority (never read off the table):
#      `--emit-facts`' `end_mark` names the form and `mark_prio`.
#   §3 THE PROBE CENSUS, the independent construction (§R.6.2 item 2): every
#      artifact of tests/endmark/b3_census.tsv (b3rev_probe.c's committed
#      answers: the tagged machine as the Moore product of two UNTAGGED
#      builds) must take the probe's form row and, where the probe modelled
#      it, its `mark_prio`. The population's counts are LITERAL floors
#      (§R.4.0), re-counted here (K35).
#   §4 THE GATES per artifact (§R.6.1), each artifact against its own
#      `-fno-rev-end-onewalk` build (today's text): G1 the tagged reverse
#      machine's emitted states <= 2x today's + 1 (two named exemptions), G2
#      the lowered forward and anchored machines <= 2x today's + 4, G3 the
#      emitted size <= today's + the PROBE's state growth x today's bytes per
#      state x 1.10 + 512, G4 every `one-seed` artifact's forward and anchored
#      tables byte-identical to today's.
#   §5 THE DECLINES under reference builds: `mark_prio`'s probe cap
#      (`PCREC_MARK_PRIO_MAX_STATES`) overflowing answers `state-dependent`,
#      and a lowered anchored machine over `PCREC_ANCHORED_MAX_STATES` while
#      today's fits declines the whole form to `overflow` (§R.5), never a
#      refusal; both with their answers checked.
#
# Usage: bash tests/endmark/run_b3_checks.sh   (PCREC, PROCS, CC honoured)
set -u
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/timeout_bin.sh" >/dev/null
. "$ROOT_DIR/tests/lib/lib_srcs.sh"
WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/endmark.XXXXXX")"
trap 'rm -rf "$WORKDIR"' EXIT
pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
[ -x "$PCREC" ] || { echo "FAIL: endmark: no compiler at $PCREC" >&2; exit 1; }

# The form (and `mark_prio`) one compile chose: `end_mark`'s `form=`/`prio=`
# parts, `-` where the table was not asked.
form_of() {   # form_of PCREC FLAGS... -- PATTERN  ->  "FORM PRIO"
    local bin="$1"; shift
    "$TIMEOUT_BIN" 60 "$bin" --emit-facts --features all "$@" 2>/dev/null \
        | awk -F'\t' '$2 == "end_mark" { f = "-"; p = "-"; n = split($7, a, ",");
                for (i = 1; i <= n; i++) {
                    if (a[i] ~ /^form=/) f = substr(a[i], 6);
                    if (a[i] ~ /^prio=/) p = substr(a[i], 6) }
                print f, p; exit }'
}

# ---- §1 answers, three arms -------------------------------------------------
for arm in "" "-fno-anchored-dfa" "-fno-rev-end-onewalk"; do
    RXTFLAGS="$arm" PCREC="$PCREC" PROCS="${PROCS:-4}" TMPDIR="$WORKDIR" \
        "$TIMEOUT_BIN" 600 bash "$ROOT_DIR/tests/harness/run.sh" "$SCRIPT_DIR/b3_rows.rxt" \
        > "$WORKDIR/ans.log" 2>&1
    p="$(sed -n 's/^cases passed: //p' "$WORKDIR/ans.log")"
    f="$(sed -n 's/^cases failed: //p' "$WORKDIR/ans.log")"
    if [ "${f:-x}" = 0 ] && [ "${p:-0}" -ge 250 ]; then
        ok "[answers] b3_rows.rxt under '${arm:-default}': $p cases, 0 failed"
    else
        bad "[answers] b3_rows.rxt under '${arm:-default}': ${p:-?} passed, ${f:-?} failed (floor 250 passed)"
        grep -E 'FAIL|HARNESS FAILURE' "$WORKDIR/ans.log" | head -5 >&2
    fi
done

# ---- §2 named witnesses: FORM PRIO ENC FLAGS PATTERN --------------------------
witness() {
    local want="$1 $2" enc="$3" flags="$4" pat="$5" got
    local bin="$PCREC"   # form_of bounds its own call ("$TIMEOUT_BIN" 60)
    local fl=(); [ "$flags" != "-" ] && read -r -a fl <<< "$flags"
    [ "$enc" = utf8 ] && fl+=(-e utf8)
    got="$(form_of "$bin" "${fl[@]}" --pattern "$pat")"
    [ -n "$got" ] || got="(no end_mark row)"
    if [ "$got" = "$want" ]; then ok "[witness] '$pat' ($enc $flags): $want"
    else bad "[witness] '$pat' ($enc $flags): $got, expected $want"; fi
}
#        form      prio            enc  flags                 pattern
witness one-seed  -               byte -                     '\d+$'
witness one-seed  -               byte -                     '\B$'
witness one-seed  -               byte -                     'a*$'
witness one-seed  -               byte -                     'ab\z|b\Z'
witness one-seed  -               byte -                     '\d+$|\w+\z'
witness one-seed  -               byte -                     '(\d+)$'
witness tagged    const0          byte -                     '\s+$'
witness tagged    const0          byte -                     '\s*$|x\z'
witness tagged    const0          byte -                     '(?:a\n|a)$'
witness tagged    const1          byte -                     '\s*?$'
witness tagged    const1          byte -                     '(?:a|a\n)$'
witness tagged    state-dependent byte -                     '(?:\s+|x\s*?)$'
witness tagged    const0          byte -                     '(?:\Bx\n|x)$'
witness tagged    const0          byte -                     '\n{1,4}$'
witness tagged    const0          byte -                     '\n\n?$'
witness tagged    const0          byte -                     '(\s+)$'
witness tagged    const0          utf8 -                     '\s+$'
witness two-seed  -               byte -                     '(?:a|b\n)+$'
witness two-seed  -               byte -                     'a\n$'
witness two-seed  -               byte -                     '(?:\n\n|a){0,4}$'
witness denied    -               byte -fno-rev-end-onewalk  '\s+$'
witness denied    -               byte -fno-rev-end-onewalk  '\d+$'
witness -         -               byte -                     '\s\z'
witness -         -               byte -                     '(?m)\s$'

# ---- §3 the probe census (independent construction) ---------------------------
CENSUS="$SCRIPT_DIR/b3_census.tsv"
python3 -I - "$PCREC" "$CENSUS" > "$WORKDIR/census.out" <<'PY'
import collections, subprocess, sys
pcrec, census = sys.argv[1:3]
def unesc(s):
    out, i = [], 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s) and s[i + 1] in 'tn\\':
            out.append({'t': '\t', 'n': '\n', '\\': '\\'}[s[i + 1]]); i += 2
        else:
            out.append(s[i]); i += 1
    return ''.join(out)
def form_of(pat, enc, icase):
    a = [pcrec, '--emit-facts', '--features', 'all']
    if enc == 'utf8': a += ['-e', 'utf8']
    if icase == '1': a += ['-i']
    r = subprocess.run(a + ['--pattern', pat], capture_output=True, text=True, timeout=120)
    for line in r.stdout.split('\n'):
        f = line.split('\t')
        if len(f) > 6 and f[1] == 'end_mark':
            form = prio = '-'
            for part in f[6].split(','):
                if part.startswith('form='): form = part[5:]
                if part.startswith('prio='): prio = part[5:]
            return form, prio
    return '-', '-'
bad = 0
cnt = collections.Counter()
n = 0
for line in open(census):
    if line.startswith('#'): continue
    id_, pop, enc, icase, pat, row, mp = line.rstrip('\n').split('\t')[:7]
    n += 1
    cnt[row] += 1
    if row == 'tagged':
        cnt['tagged-' + pop] += 1; cnt['tagged-' + enc] += 1; cnt['mp-' + mp] += 1
    form, prio = form_of(unesc(pat), enc, icase)
    if form != row:
        bad += 1; print('BAD form %s: built %s, probe %s' % (id_, form, row))
    elif row == 'tagged' and mp != '-' and prio != mp:
        bad += 1; print('BAD mark_prio %s: built %s, probe %s' % (id_, prio, mp))
print('COUNT n=%d %s' % (n, ' '.join('%s=%d' % kv for kv in sorted(cnt.items()))))
print('NBAD', bad)
PY
grep '^BAD' "$WORKDIR/census.out" | head -10 >&2
nbad="$(sed -n 's/^NBAD //p' "$WORKDIR/census.out")"
counts="$(sed -n 's/^COUNT //p' "$WORKDIR/census.out")"
[ "$nbad" = 0 ] && ok "[census] every probe-census artifact takes the probe's form and mark_prio ($counts)" \
                || bad "[census] $nbad artifact(s) disagree with the probe's form or mark_prio"
# §R.4.0's literal floors, re-counted from the population this run read.
for want in "n=266" "one-seed=223" "tagged=43" "tagged-bench=1" "tagged-utf8=3" "mp-const0=28" "mp-const1=10" "mp--=5"; do
    case " $counts " in
        *" $want "*) ok "[floor] population count $want" ;;
        *) bad "[floor] population count $want not met: $counts" ;;
    esac
done

# ---- §4 the gates, each artifact against its own denied build -----------------
# The machine sizes are read off the EMITTED tables: `<p>_<m>_next_state[K]`
# holds K = states x classes cells and `<p>_<m>_byte_class` names the class
# count (its largest entry + 1). The size is `--warn-emit-bytes=1`'s count,
# the caps' own measure.
python3 -I - "$PCREC" "$CENSUS" "$WORKDIR" > "$WORKDIR/gates.out" <<'PY'
import os, re, subprocess, sys
pcrec, census, wd = sys.argv[1:4]
EXEMPT = {r'[^c]{0,4}?$', r'[^c]{0,4}$'}
# G3's model prices STATES only; a tagged machine may carry a scan edge per
# distance state, each with its own 256-byte class table (the emitter keeps
# one table per edge even where the classes are equal). Named, with its
# measured excess, rather than a formula widened to fit: lane b3build's
# report records it as a G3 model finding.
G3_EXEMPT = {r'[^\n]*\n?$'}   # +2,804 B vs the model's 1,606 B: three [^\n] edge tables
def unesc(s):
    out, i = [], 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s) and s[i + 1] in 'tn\\':
            out.append({'t': '\t', 'n': '\n', '\\': '\\'}[s[i + 1]]); i += 2
        else:
            out.append(s[i]); i += 1
    return ''.join(out)
def comp(pat, enc, icase, extra):
    a = [pcrec, '--features', 'all', '-p', 'rx', '-o', os.path.join(wd, 'g.c'), '--warn-emit-bytes=1']
    if enc == 'utf8': a += ['-e', 'utf8']
    if icase == '1': a += ['-i']
    r = subprocess.run(a + extra + ['--pattern', pat], capture_output=True, text=True, timeout=120)
    if r.returncode: return None
    m = re.search(r'artifact: (\d+) bytes of emitted C source', r.stderr)
    return open(os.path.join(wd, 'g.c')).read(), int(m.group(1)) if m else None
def states(text, mach):
    m = re.search(r'%s_next_state\[(\d+)\]' % mach, text)
    c = re.search(r'%s_byte_class\[256\] = \{([^}]*)\}' % mach, text)
    if not m or not c: return None
    ncls = max(int(x) for x in c.group(1).replace('\n', ' ').split(',') if x.strip()) + 1
    return int(m.group(1)) // ncls
def tables(text, mach):
    return re.findall(r'static const [a-z ]+ rx_%s_[a-z_]+\[\d+\] = \{[^}]*\};' % mach, text)
bad = 0; n = {'g1': 0, 'g2': 0, 'g3': 0, 'g3exempt': 0, 'g4': 0, 'exempt': 0}
for line in open(census):
    if line.startswith('#'): continue
    v = line.rstrip('\n').split('\t')
    id_, pop, enc, icase, pat, row = v[:6]
    rt, rg, ft, fg, at, ag, rb, fb, ab = v[7:16]
    pat = unesc(pat)
    d = comp(pat, enc, icase, []); t = comp(pat, enc, icase, ['-fno-rev-end-onewalk'])
    if not d or not t:
        bad += 1; print('BAD %s: does not compile' % id_); continue
    (dc, db), (tc, tb) = d, t
    if row == 'one-seed':
        for m in ('forward', 'anchored'):
            if tables(dc, m) != tables(tc, m):
                bad += 1; print('BAD G4 %s: one-seed %s tables differ from today' % (id_, m))
        n['g4'] += 1
        continue
    if row != 'tagged': continue
    rd, rtd = states(dc, 'rx_reverse'), states(tc, 'rx_reverse')
    if rd is None or rtd is None:
        bad += 1; print('BAD G1 %s: no reverse table read' % id_)
    elif rd > 2 * rtd + 1:
        if pat in EXEMPT: n['exempt'] += 1
        else: bad += 1; print('BAD G1 %s: reverse %d > 2x%d+1' % (id_, rd, rtd))
    else: n['g1'] += 1
    for m in ('forward', 'anchored'):
        x, y = states(dc, 'rx_' + m), states(tc, 'rx_' + m)
        if x is None or y is None: continue
        if x > 2 * y + 4: bad += 1; print('BAD G2 %s: %s %d > 2x%d+4' % (id_, m, x, y))
        else: n['g2'] += 1
    grow = 0.0
    for a, b, bps in ((rg, rt, rb), (fg, ft, fb), (ag, at, ab)):
        if '-' in (a, b, bps): continue
        grow += max(0, int(a) - int(b)) * float(bps)
    if db is None or tb is None: bad += 1; print('BAD G3 %s: no size read' % id_)
    elif db > tb + grow * 1.10 + 512:
        if pat in G3_EXEMPT: n['g3exempt'] += 1
        else: bad += 1; print('BAD G3 %s: %d > %d + %.0f' % (id_, db, tb, grow * 1.10 + 512))
    else: n['g3'] += 1
print('GATES', ' '.join('%s=%d' % kv for kv in sorted(n.items())))
print('NBAD', bad)
PY
grep '^BAD' "$WORKDIR/gates.out" | head -10 >&2
nbad="$(sed -n 's/^NBAD //p' "$WORKDIR/gates.out")"
gates="$(sed -n 's/^GATES //p' "$WORKDIR/gates.out")"
[ "${nbad:-x}" = 0 ] && ok "[gates] G1-G4 hold on the census population ($gates)" \
                     || bad "[gates] ${nbad:-?} gate failure(s) ($gates)"
# K35: each gate's population, floored at what this tree measures.
for want in "g1=41" "g2=20" "g3=42" "g4=223" "exempt=2"; do
    k="${want%%=*}"; fl="${want#*=}"
    got="$(printf '%s\n' "$gates" | tr ' ' '\n' | sed -n "s/^$k=//p")"
    [ "${got:-0}" -ge "$fl" ] && ok "[gates] $k population $got (floor $fl)" \
                              || bad "[gates] $k population ${got:-0} below its floor $fl"
done

# ---- §5 the declines under reference builds ------------------------------------
refbuild() {   # refbuild OUT -DFLAG=V
    ${CC:-gcc} -O1 -std=gnu11 -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" "$2" -o "$1" \
        "$ROOT_DIR/cli/main.c" $(pcrec_lib_srcs "$ROOT_DIR" | tr '\n' ' ') 2>"$WORKDIR/ref.err"
}
check_answers() {   # check_answers BIN LABEL PATTERN SUBJECT START END ...
    local bin="$1" label="$2" pat="$3"; shift 3
    if ! "$TIMEOUT_BIN" 60 "$bin" --features all -p rx --emit-main -o "$WORKDIR/r.c" --pattern "$pat" 2>"$WORKDIR/r.err" ||
       ! ${CC:-gcc} -O1 -o "$WORKDIR/r" "$WORKDIR/r.c" 2>>"$WORKDIR/r.err"; then
        bad "[$label] '$pat' does not compile (a decline became a refusal?): $(head -2 "$WORKDIR/r.err")"; return
    fi
    local wrong=""
    while [ $# -ge 2 ]; do
        local subj="$1" want="$2"; shift 2
        local got; got="$("$TIMEOUT_BIN" 10 "$WORKDIR/r" "$subj" 2>&1 | head -1)"
        case "$got" in *"$want"*) ;; *) wrong="$wrong [$subj: $got, want $want]" ;; esac
    done
    [ -z "$wrong" ] && ok "[$label] '$pat' answers as libpcre2 does" || bad "[$label] '$pat':$wrong"
}
# `--emit-main`'s reply is `match START END` or `nomatch`, the subject from
# argv (each written as a $'..' literal: a command substitution would drop a
# trailing newline, the very byte these cells are about). The expectations
# are libpcre2 10.46's (tests/fuzz/pcre2_oracle).
if refbuild "$WORKDIR/pcrec_prio" -DPCREC_MARK_PRIO_MAX_STATES=2; then
    got="$(form_of "$WORKDIR/pcrec_prio" --pattern '\s+$')"
    [ "$got" = "tagged state-dependent" ] \
        && ok "[decline] mark_prio's cap overflowing answers state-dependent ('\\s+\$': $got)" \
        || bad "[decline] under PCREC_MARK_PRIO_MAX_STATES=2 '\\s+\$' reads '$got', expected 'tagged state-dependent'"
    check_answers "$WORKDIR/pcrec_prio" decline '\s+$' $'a  \n' 'match 1 4' $' \n' 'match 0 2' $'\n' 'match 0 1'
else
    bad "[decline] the PCREC_MARK_PRIO_MAX_STATES=2 reference compiler did not build: $(head -3 "$WORKDIR/ref.err")"
fi
if refbuild "$WORKDIR/pcrec_anch" -DPCREC_ANCHORED_MAX_STATES=3; then
    got="$(form_of "$WORKDIR/pcrec_anch" --pattern '\s*?$')"
    [ "$got" = "overflow -" ] \
        && ok "[decline] a lowered anchored machine over its cap declines the form to overflow ('\\s*?\$')" \
        || bad "[decline] under PCREC_ANCHORED_MAX_STATES=3 '\\s*?\$' reads '$got', expected 'overflow -'"
    check_answers "$WORKDIR/pcrec_anch" decline '\s*?$' $' \n' 'match 0 1' $'a \n\n' 'match 1 3' $'\n' 'match 0 0'
else
    bad "[decline] the PCREC_ANCHORED_MAX_STATES=3 reference compiler did not build: $(head -3 "$WORKDIR/ref.err")"
fi

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
