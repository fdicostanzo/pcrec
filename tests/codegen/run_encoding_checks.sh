#!/usr/bin/env bash
# tests/codegen/run_encoding_checks.sh — [M5.0] STAGE 2's STRUCTURAL AND
# DIFFERENTIAL ACCEPTANCE, the checks the .rxt corpus and the identity gate
# structurally cannot make.
#
# Design: docs/design/utf8_design.md §8.5 (the ASCII-corpus encoding
# differential), §8.1.1 check 3 (the stamp census), §9.2 stage 2 (which lists
# DD-12(7)(a)'s two M5-time structural checks), §2.4.1/§5.6.1 (the clamp
# stride).
#
# FOUR SECTIONS, and each is here for the reason this directory exists — a
# fact no answer comparison can reach:
#
#   §8.5  THE ASCII-CORPUS ENCODING DIFFERENTIAL. Every ASCII-only corpus
#         pattern has a `byte` artifact and a `utf8` artifact, and on an
#         ASCII subject they must give the SAME answer — two independently
#         derived machines (the identity map, and the byte-sequence
#         decomposition's one-byte-"sequence" per character), one expected
#         answer. Together with §8.1's identity gate (the `byte` artifact did
#         not move) this is TRANSITIVE to the pre-M5 compiler over the whole
#         ASCII corpus with no new expectation authored. Its positive control
#         is the exclusion COUNT: the non-ASCII blocks must be excluded by the
#         harness's own DECODE, not by a text scan (§8.5's method note — a
#         text scan reads a `\xNN` subject escape as ASCII and undercounts).
#
#   CHK3  THE STAMP CENSUS (§8.1.1 check 3). Over the corpus compiled under
#         BOTH encodings: no `byte`-encoding artifact's stamps move (that is
#         the identity gate's job and this only re-confirms it cheaply), and
#         every `utf8` artifact whose stamps DIFFER from its `byte` twin is
#         listed with its reason. It is a MANIFEST reviewed as a diff (r49),
#         never a threshold — the only instrument that would see §2.4.1's
#         premultiplied decline, §6.2.1's `[SEL-1]` engine change or §6.4's
#         island claim, none of which changes an answer.
#
#   DD12a THE TWO DD-12(7)(a) STRUCTURAL CHECKS (§9.2). (i) HOT-LOOP SHAPE
#         IDENTITY: an ASCII pattern's `utf8` engine body is byte-identical to
#         its `byte` one, because the lowering is the identity below 0x7F — the
#         structural face of §8.5's answer identity, and the thing that proves
#         no encoding conditional reached the hot path. (ii) THE SECOND-BACKEND
#         VALIDATION of D58's revisit-when names: the seam's ENTRIES TABLE
#         interface is unchanged by the second backend — the four residual
#         entries appear in a `utf8` artifact under the SAME signatures the
#         `byte` backend emits, which is the property [M6.6.2] wave D
#         demonstrated for `back_step` (prediction P-1) now demonstrated for a
#         whole second backend.
#
#   S-U8  THE CLAMP-STRIDE PROBE. `(a)(?:\x{3b1}){0,3}x` under `utf8` emits
#         `RX_PRUNE_CLAMP_SPAN(scan_position, 1, 2)` — the stride 2 IS the
#         encoded length of α, so it is the one readable witness that the MRL
#         prune counts ENCODED bytes (§5.6.1: minw stays bytes and is EXACT
#         per class on the LOWERED tree). Sabotage row S-U8's detector.
#
# THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS (learnings §3):
# §8.5 and CHK3 derive answers/stamps from the EMITTED ARTIFACTS of two
# encodings; the differential's oracle is the OTHER encoding, not pcrec
# reading its own analysis.
#
# LOCAL vs SLOT: the full §8.5 sweep compiles and runs two artifacts per ASCII
# block (~6,600 compiles). ENC_MAX_BLOCKS bounds it for a light local run
# (Frank's rule); ENC_MAX_BLOCKS=0 is the whole corpus, which rides the Linux
# slot. CHK3/DD12a/S-U8 are compile-only and always run in full.
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"

ENC_MAX_BLOCKS="${ENC_MAX_BLOCKS:-250}"   # 0 = whole corpus (slot)
KEEP="${KEEP:-0}"
WORKDIR="$(mktemp -d)"
cleanup() { if [ "$KEEP" = 1 ]; then echo "encoding-checks: KEEP=1 $WORKDIR" >&2
            else rm -rf "$WORKDIR"; fi; }
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
finish() { echo; echo "checks passed: $pass"; echo "checks failed: $fail";
           [ "$fail" -eq 0 ] || exit 1; exit 0; }

if [ ! -x "$PCREC" ]; then bad "pcrec not built: $PCREC"; finish; fi

# ---------------------------------------------------------------------------
# §8.5  THE ASCII-CORPUS ENCODING DIFFERENTIAL
#
# A python helper reuses the harness's OWN parser and subject decoder
# (tests/harness/verify_rxt.py), so "ASCII" is decided by the same decode the
# suite trusts rather than by a text scan (§8.5's method note). It emits, per
# block: the pattern, a features guess, and each subject, tab-separated and
# byte-clean via base64 so a subject's own bytes cannot break the framing.
# ---------------------------------------------------------------------------
python3 - "$ROOT_DIR" "$ENC_MAX_BLOCKS" > "$WORKDIR/blocks.tsv" 2>"$WORKDIR/py.err" <<'PY'
import sys, os, glob, base64
root, maxb = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, os.path.join(root, "tests", "harness"))
import verify_rxt as V

def is_ascii(s): return all(ord(c) < 0x80 for c in s)

ascii_blocks = 0
excl_pat = 0
excl_subj = 0
emitted = 0
files = sorted(glob.glob(os.path.join(root, "tests", "**", "*.rxt"), recursive=True))
for path in files:
    if "/known_fail/" in path:
        continue
    try:
        entries = V.parse_rxt(path)
    except Exception:
        continue
    # group into blocks by pattern
    cur_pat = None
    cur_subj = []   # (want, subject)  want in {m,n,ms,ns}
    cur_ascii = True
    cur_perr = False
    def flush():
        global ascii_blocks, excl_pat, excl_subj, emitted
        if cur_pat is None:
            return
        if cur_perr:
            return
        if not is_ascii(cur_pat):
            excl_pat += 1
            return
        bad_subj = any(not is_ascii(s) for (_w, s) in cur_subj)
        if bad_subj:
            excl_subj += 1
            return
        ascii_blocks += 1
        if maxb and emitted >= maxb:
            return
        emitted += 1
        b = base64.b64encode(cur_pat.encode("latin-1", "surrogateescape")).decode()
        subs = ";".join(w + ":" + base64.b64encode(
            s.encode("latin-1", "surrogateescape")).decode() for (w, s) in cur_subj)
        print("\t".join([b, subs if subs else "-"]))
    for (lineno, kind, data) in entries:
        if kind == "pattern":
            flush()
            # pattern data is (pattern, caseless_bool)
            cur_pat = data[0] if isinstance(data, (tuple, list)) else data
            cur_subj = []
            cur_perr = False
        elif kind == "perr":
            cur_perr = True
        elif kind in ("m", "n", "ms", "ns"):
            # subject column by kind: m (subj,s,e); n bare subj;
            # ms (startpos,subj,s,e); ns (startpos,subj)
            if kind == "m":
                subj = data[0]
            elif kind == "n":
                subj = data if isinstance(data, str) else data[0]
            else:  # ms, ns
                subj = data[1]
            cur_subj.append((kind, subj))
    flush()

sys.stderr.write("ASCII_BLOCKS=%d EXCL_PAT=%d EXCL_SUBJ=%d EMITTED=%d\n"
                 % (ascii_blocks, excl_pat, excl_subj, emitted))
PY
py_rc=$?
if [ "$py_rc" != 0 ]; then
    bad "§8.5 block extraction failed: $(head -3 "$WORKDIR/py.err")"
    finish
fi
census_line="$(grep -o 'ASCII_BLOCKS=[0-9]* EXCL_PAT=[0-9]* EXCL_SUBJ=[0-9]* EMITTED=[0-9]*' "$WORKDIR/py.err")"
eval "$census_line"

# THE POSITIVE CONTROL: the exclusion count, by DECODE not text scan (§8.5).
# The design measured 3,319 ASCII blocks / 1 non-ASCII pattern / 30 non-ASCII
# subjects at its tree. The corpus grows, so this asserts the SHAPE (a small
# nonzero subject-exclusion count that a text scan would read as 0) and floors
# the ASCII population, rather than pinning 3,319 which would go stale.
echo "  §8.5 corpus census: ASCII=$ASCII_BLOCKS excl(pattern)=$EXCL_PAT excl(subject)=$EXCL_SUBJ"
if [ "$ASCII_BLOCKS" -ge 2000 ]; then
    ok "§8.5 ASCII population floor met ($ASCII_BLOCKS >= 2000)"
else
    bad "§8.5 ASCII population $ASCII_BLOCKS below floor 2000 — corpus shrank or the decode broke"
fi
if [ "$EXCL_SUBJ" -ge 1 ]; then
    ok "§8.5 the subject-exclusion count is nonzero ($EXCL_SUBJ) — the decode sees a high byte a text scan reads as \\xNN ASCII (the method note's own trap)"
else
    bad "§8.5 subject exclusions read 0 — the census is counting the instrument (a \\xNN escape as ASCII text) rather than the decoded subject"
fi

# The differential driver: read a byte artifact and a utf8 artifact linked
# under two prefixes, run every subject through both, compare span.
cat > "$WORKDIR/drv.c" <<'DRV'
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "b.h"
#include "u.h"
/* one subject on argv[1] (already the raw bytes), compare b vs u span */
int main(int argc, char **argv)
{
    const unsigned char *s = (const unsigned char *)argv[1];
    size_t n = (size_t)strtoul(argv[2], NULL, 10);
    ptrdiff_t bc[B_NCAPS][2], uc[U_NCAPS][2];
    int rb = b_search(s, n, 0, bc);
    int ru = u_search(s, n, 0, uc);
    (void)argc;
    if (rb != ru) { printf("R %d %d\n", rb, ru); return 2; }
    if (rb == 1 && (bc[0][0] != uc[0][0] || bc[0][1] != uc[0][1])) {
        printf("S %td,%td %td,%td\n", bc[0][0], bc[0][1], uc[0][0], uc[0][1]);
        return 3;
    }
    printf("ok\n");
    return 0;
}
DRV

# [K51] the give-up divergence manifest (see the manifest's own header):
# byte-answers-vs-utf8-typed-give-up on a NAMED pattern is excused, counted
# and printed; everything else on those patterns still fails.
K51_MANIFEST="$ROOT_DIR/tests/codegen/manifests/k51_giveup_divergers.txt"
grep -v '^#' "$K51_MANIFEST" | grep -v '^$' > "$WORKDIR/k51_rows.txt" || true
: > "$WORKDIR/k51_excused_pats.txt"
k51cells=0

diffn=0; diverge=0; ccfail=0
while IFS=$'\t' read -r patb subs; do
    [ -z "$patb" ] && continue
    pat="$(printf '%s' "$patb" | base64 -d)"
    d="$WORKDIR/b_$diffn"; mkdir -p "$d"
    # emit both encodings with features all (ASCII patterns may use modules)
    if ! pcrec_run "$PCREC" --features all -e byte -p b -o "$d/b.c" -- "$pat" >/dev/null 2>&1; then
        continue   # a pattern byte refuses (perr already filtered; a gated
                   # construct under some feature set) — not this check's subject
    fi
    if ! pcrec_run "$PCREC" --features all -e utf8 -p u -o "$d/u.c" -- "$pat" >/dev/null 2>&1; then
        # [K51] the manifest's SECOND face: the same rung loss can inflate the
        # utf8 artifact past the code-bytes cap, so byte COMPILES and utf8
        # REFUSES — excused only for a named manifest pattern, counted with
        # the give-up cells.
        if grep -qxF "$pat" "$WORKDIR/k51_rows.txt"; then
            echo "  §8.5 K51-excused utf8 cap-refusal (byte compiles): $pat"
            k51cells=$((k51cells + 1))
            printf '%s\n' "$pat" >> "$WORKDIR/k51_excused_pats.txt"
        else
            bad "§8.5 pattern compiled under byte but NOT utf8: $pat"
            diverge=$((diverge + 1))
        fi
        diffn=$((diffn + 1)); continue
    fi
    cp "$WORKDIR/drv.c" "$d/drv.c"
    if ! gen_cc "encchk $diffn" "$CC" -O1 -w -I "$d" -o "$d/t" "$d/drv.c" "$d/b.c" "$d/u.c" >/dev/null 2>&1; then
        ccfail=$((ccfail + 1)); diffn=$((diffn + 1)); continue
    fi
    if [ "$subs" != "-" ]; then
        IFS=';' read -ra arr <<< "$subs"
        for cell in "${arr[@]}"; do
            sb="${cell#*:}"
            subj="$(printf '%s' "$sb" | base64 -d)"
            slen="$(printf '%s' "$subj" | wc -c | tr -d ' ')"
            out="$("$d/t" "$subj" "$slen" 2>/dev/null)"
            if [ "$out" != "ok" ]; then
                # [K51] excuse ONLY byte-answers / utf8-typed-give-up on a
                # manifest pattern; the regex pins that exact shape.
                if grep -qxF "$pat" "$WORKDIR/k51_rows.txt" \
                   && printf '%s' "$out" | grep -qE '^R [0-9]+ -[0-9]+$'; then
                    echo "  §8.5 K51-excused give-up divergence: pat=[$pat] subj=[$subj] -> $out"
                    k51cells=$((k51cells + 1))
                    printf '%s\n' "$pat" >> "$WORKDIR/k51_excused_pats.txt"
                else
                    bad "§8.5 byte/utf8 DIVERGE on ASCII: pat=[$pat] subj=[$subj] -> $out"
                    diverge=$((diverge + 1))
                fi
            fi
        done
    fi
    diffn=$((diffn + 1))
done < "$WORKDIR/blocks.tsv"

# [K51] manifest accounting: every row is a claim with two expiry guards.
k51n=$(grep -c '' "$WORKDIR/k51_rows.txt" 2>/dev/null || echo 0)
k51pats=$(LC_ALL=C sort -u "$WORKDIR/k51_excused_pats.txt" | grep -c '' || true)
while IFS= read -r row; do
    [ -z "$row" ] && continue
    rowb64="$(printf '%s' "$row" | base64 | tr -d '\n')"
    if ! grep -q "^$rowb64	" "$WORKDIR/blocks.tsv"; then
        if grep -rqxF "pattern $row" "$ROOT_DIR/tests" --include='*.rxt' 2>/dev/null; then
            echo "  §8.5 K51 manifest row not reached in this slice (ENC_MAX_BLOCKS=$ENC_MAX_BLOCKS; the full sweep covers it)"
        else
            bad "§8.5 K51 manifest row names a pattern no longer in the corpus (STALE — retire or re-point it): $row"
        fi
    elif ! grep -qxF "$row" "$WORKDIR/k51_excused_pats.txt"; then
        bad "§8.5 K51 manifest row was SWEPT and produced no excused give-up cell — K51 may be (partly) fixed: re-measure, then retire the row deliberately: $row"
    fi
done < "$WORKDIR/k51_rows.txt"
echo "  §8.5 K51-excused: $k51cells cell(s) across $k51pats pattern(s) (manifest rows: $k51n)"
echo "  §8.5 ran $diffn ASCII blocks ($ccfail cc-skipped), $diverge divergences"
if [ "$diverge" -eq 0 ]; then
    ok "§8.5 byte and utf8 artifacts agree on every ASCII subject ($diffn blocks)"
else
    bad "§8.5 $diverge byte/utf8 divergences on ASCII input — likeliest cause: the length-split boundary at 0x7F (§8.5 P-11)"
fi

# ---------------------------------------------------------------------------
# CHK3  THE STAMP CENSUS
#
# For each ASCII pattern already emitted above: record the byte and utf8
# stamps and confirm the byte stamps are unchanged from the identity gate's
# expectation implicitly (they are the same compiler); the interesting half
# is that on an ASCII pattern the utf8 stamps EQUAL the byte ones, since the
# lowering is the identity below 0x7F. A utf8 artifact of an ASCII pattern
# that stamps differently would mean an encoding conditional reached a path
# it must not.
# ---------------------------------------------------------------------------
stamp_of() { grep -oE "#define (RX_ENGINE|RX_ENGINE_SEL|RX_DFA_TABLE|RX_VM_STRATS|RX_VM_RUNGS) [^ ]*.*" "$1" 2>/dev/null | LC_ALL=C sort; }
stamp_diff=0
for d in "$WORKDIR"/b_*; do
    [ -f "$d/b.c" ] && [ -f "$d/u.c" ] || continue
    if ! diff -q <(stamp_of "$d/b.c") <(stamp_of "$d/u.c") >/dev/null 2>&1; then
        stamp_diff=$((stamp_diff + 1))
        echo "  CHK3 stamp differs (ASCII pattern, byte vs utf8): $d" >> "$WORKDIR/stampdiff.txt"
    fi
done
echo "  CHK3 ASCII stamp differences: $stamp_diff (expected 0 — lowering is identity below 0x7F)"
if [ "$stamp_diff" -eq 0 ]; then
    ok "CHK3 every ASCII pattern's utf8 stamps equal its byte stamps"
else
    bad "CHK3 $stamp_diff ASCII patterns stamp differently under utf8 (see stampdiff.txt) — an encoding conditional reached the stamp"
fi

# ---------------------------------------------------------------------------
# DD12a(i)  THE HOT-LOOP SHAPE IDENTITY -- REBUILT (K52's repair)
#
# The old instrument compiled both artifacts to `.o` and compared whole-object
# `.text`/`.rodata` bytes: VACUOUS on darwin (`objdump -j .text` matches
# nothing on Mach-O -- every historical green was empty-vs-empty) and WRONG
# EVERYWHERE ELSE (the whole-object scope cannot admit the seam's own
# per-encoding residual bodies or K49's retry advance, which are legitimate
# per-encoding text -- see docs/dev/known_issues.md K52 for the full account).
#
# THE REPAIR OPERATES ON EMITTED SOURCE TEXT, NEVER ON OBJECT BYTES, and that
# choice is what makes a real darwin arm possible at all rather than a second
# attempt at reading a Mach-O section: there is no compiler, no object format
# and no objdump anywhere in this section. Both artifacts are re-emitted with
# the SAME PREFIX ("rx") into per-encoding subdirectories sharing the SAME
# BASENAME ("rx.c") -- run_trie_identity.sh's and run_vm_identity.sh's own
# documented trap (a differing `#include "<name>.h"` line dominating an
# otherwise-identical diff) is avoided BY CONSTRUCTION rather than by a
# post-hoc filter, because there is only one prefix and one basename to write.
#
# THE NAMED ENCODING-OWNED REGIONS -- excised from BOTH texts before the
# compare, never trusted to cancel by accident:
#   (1) each of the four residual entries (next_pos, back_step, bref_match,
#       bref_match_caseless), whose SIGNATURE is identical across backends
#       (D58 P-1, DD12a(ii) below) but whose BODY is the backend's own text by
#       design. Found by the signature line (a closed, four-name list) and
#       swallowed together with its own immediately-preceding descriptive
#       comment (which is prose that legitimately differs -- "byte encoding:
#       one byte is one character..." vs "utf8 encoding: skip forward...").
#   (2) the [K49] unanchored retry advance, the one splice DD-12 (7) admits
#       into shared emitter code outside the entries table (its own comment,
#       in `src/gen/emit_vm.c`, says so: "there is no encoding test here").
#       Anchored on the SAME guard line the K49 advance-agreement check above
#       already uses (`if (attempt_position >= subject_length) return 0;`)
#       through the enclosing block's own closing `    }` -- both anchor lines
#       are confirmed identical text on both backends and are KEPT, not
#       excised; only the span between them is.
#   (3) the `.encoding = N,` scalar in the `rx_info` initializer -- a single
#       field whose VALUE legitimately differs and whose LINE always exists,
#       so it is normalized (value replaced by a placeholder) rather than
#       deleted.
#
# WHY NAIVE PER-SYMBOL OBJECT EXCLUSION WAS TRIED AND REJECTED (K52's own
# finding): under `always_inline` the K49 advance's inlined body SMEARS across
# the VM entry chain at the object level, so a symbol-table exclusion list can
# no longer name "the one function this text lives in" -- the exclusion moves
# with the inliner's mood. Source-text excision, applied BEFORE any compiler
# sees the file, has no inliner to smear across: the K49 splice is one
# physical span in one physical function in the .c text regardless of what
# `-O2` later does to it.
#
# (a) NON-EMPTY BY CONSTRUCTION. `next_pos` is UNCONDITIONAL on every VM and
#     DFA artifact alike (DD-12's own promise), so its excision is required
#     to fire EXACTLY ONCE per side on every compiled pair -- zero is a hard
#     FAIL, never a silent pass. The other three residuals and the retry
#     advance are conditional on the pattern's shape, so three explicit
#     witnesses are added to the swept population (the corpus alone is not
#     trusted to reach all four by luck): `a*` (VM, unanchored -- forces the
#     retry advance, reusing the K49 check's own witness for consistency),
#     `(?i)(?<=a)(b)\1x` (DD12a(ii)'s own witness -- back_step +
#     bref_match_caseless) and its case-sensitive twin `(?<=a)(b)\1x`
#     (back_step + bref_match). Aggregate floors below assert each of the six
#     counters (four residuals, the advance, the encoding field) is reached
#     at least once across the whole run -- a check that never exercised
#     `bref_match` would be dead code passing silently on that population.
# (b) THE NORMALIZATION COUNT IS PINNED AND PRINTED, per pattern: a pattern
#     whose byte and utf8 sides disagree on HOW MANY of a given region they
#     each contain is itself a finding (an asymmetric residual population is
#     not a text mismatch a diff would show -- the two sides could still
#     agree on everything else) and is reported by name rather than folded
#     into the aggregate.
# (c) DARWIN: this whole section reads and writes only `.c` text, so it needs
#     no working section reader on any platform. It is not a SKIP naming a
#     limitation; it is the same instrument on both boxes.
# (d) VALIDATION: a scratch plant of one line of encoding-conditional text
#     into the shared engine body (`src/gen/emit_vm.c`, immediately before the
#     `_accept:` label -- outside every named region above) was built in a
#     throwaway `git archive` tree and confirmed to turn this section red on
#     every VM-selected witness while leaving CHK3, DD12a(ii) and the K49
#     check untouched; see docs/dev/lanes/encchk_report.md for the transcript.
# ---------------------------------------------------------------------------
python3 - "$ROOT_DIR" "$PCREC" "$WORKDIR/blocks.tsv" "$ENC_MAX_BLOCKS" > "$WORKDIR/dd12ai.out" 2>"$WORKDIR/dd12ai.err" <<'PY'
import sys, os, re, subprocess, base64, tempfile, shutil, difflib

root, pcrec, blocks_tsv, max_blocks = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])

SIG_RE = re.compile(r'^(?:size_t|ptrdiff_t)\s+rx_(next_pos|back_step|bref_match|bref_match_caseless)\(')
ENC_RE = re.compile(r'^(\s*\.encoding = )\d+(,\s*)$')
GUARD = 'if (attempt_position >= subject_length) return 0;'

# WIDENS_UNDER_UTF8: a pattern using an unescaped dot or a negated class is
# NOT covered by "the lowering is the identity below 0x7F" -- both mean "any
# code point [not in the set]", which lowers to a class spanning the WHOLE
# encoded space, not the ASCII-restricted one, so the compiled AUTOMATON
# genuinely differs in STATE COUNT and TABLE SHAPE from its byte twin even
# though the two answer identically on every ASCII subject (which is exactly
# what section 8.5 above already confirms for this same population). This
# was MEASURED, not assumed: the check's own first run against the real
# corpus found exactly ten diverging pairs, and every one of them was a
# dot- or negation-bearing pattern (`.*\z`, `[^c]{1,3}\z` and its siblings,
# `\G.` among them) whose class table grew from 2 classes to 14 and whose
# whole state machine grew with it (7 states -> 28 on one witness) -- not a
# stray conditional, a different (and correctly compiled) machine. Scoped
# from the PATTERN TEXT, independent of anything pcrec computes
# (`lookaround_classify.py`'s own rule): a pattern in this bucket is EXCLUDED
# from the strict text-identity claim below (§8.5's answer differential is
# the right instrument for it and already covers it) but COUNTED and
# FLOORED, never silently dropped.
def widens_under_utf8(pat):
    i, n = 0, len(pat)
    in_class = False
    while i < n:
        c = pat[i]
        if c == '\\':
            i += 2
            continue
        if not in_class:
            if c == '[':
                in_class = True
                if i + 1 < n and pat[i + 1] == '^':
                    return True
                i += 1
                continue
            if c == '.':
                return True
        else:
            if c == ']':
                in_class = False
        i += 1
    return False

def excise(text, label):
    lines = text.splitlines(keepends=True)
    counts = {'next_pos': 0, 'back_step': 0, 'bref_match': 0,
              'bref_match_caseless': 0, 'advance': 0, 'encoding': 0}
    out = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        m = SIG_RE.match(line)
        if m:
            name = m.group(1)
            if out and out[-1].rstrip().endswith('*/'):
                k = len(out) - 1
                while k >= 0 and not out[k].lstrip().startswith('/*'):
                    k -= 1
                if k >= 0:
                    del out[k:]
            fi = i
            while fi < n and lines[fi].strip() != '{':
                fi += 1
            if fi >= n:
                print("EXTRACT-FAIL %s: no opening brace for rx_%s" % (label, name))
                sys.exit(2)
            depth, fe = 1, fi + 1
            while fe < n and depth > 0:
                depth += lines[fe].count('{') - lines[fe].count('}')
                fe += 1
            if depth != 0:
                print("EXTRACT-FAIL %s: unbalanced braces for rx_%s" % (label, name))
                sys.exit(2)
            out.append("/* [ENCCHK-DD12A] residual entry %s excised for comparison */\n" % name)
            counts[name] += 1
            i = fe
            continue
        if GUARD in line:
            out.append(line)
            i += 1
            gi = i
            while gi < n and lines[gi].rstrip('\n') != '    }':
                gi += 1
            if gi >= n:
                print("EXTRACT-FAIL %s: no closing brace for the retry advance" % label)
                sys.exit(2)
            out.append("/* [ENCCHK-DD12A] retry advance excised for comparison */\n")
            counts['advance'] += 1
            i = gi
            continue
        me = ENC_RE.match(line.rstrip('\n'))
        if me:
            out.append(me.group(1) + "N" + me.group(2) + "\n")
            counts['encoding'] += 1
            i += 1
            continue
        out.append(line)
        i += 1
    return ''.join(out), counts

def compile_pair(pat, workdir, idx):
    db = os.path.join(workdir, "p%d" % idx, "byte")
    du = os.path.join(workdir, "p%d" % idx, "utf8")
    os.makedirs(db, exist_ok=True)
    os.makedirs(du, exist_ok=True)
    rb = subprocess.run([pcrec, "--features", "all", "-e", "byte", "-p", "rx",
                         "-o", os.path.join(db, "rx.c"), "--", pat],
                        capture_output=True, text=True)
    if rb.returncode != 0:
        return None
    ru = subprocess.run([pcrec, "--features", "all", "-e", "utf8", "-p", "rx",
                         "-o", os.path.join(du, "rx.c"), "--", pat],
                        capture_output=True, text=True)
    if ru.returncode != 0:
        return "byte-only"
    with open(os.path.join(db, "rx.c")) as f:
        tb = f.read()
    with open(os.path.join(du, "rx.c")) as f:
        tu = f.read()
    return (tb, tu)

def main():
    patterns, emitted = [], 0
    with open(blocks_tsv) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            patb = line.split("\t", 1)[0]
            patterns.append(base64.b64decode(patb).decode("latin-1"))
            emitted += 1
            if max_blocks and emitted >= max_blocks:
                break
    # explicit witnesses: guarantee non-vacuity for each named region (a) --
    # the corpus is not trusted to reach all four residuals plus the advance
    # by luck alone.
    patterns += ['a*', '(?i)(?<=a)(b)\\1x', '(?<=a)(b)\\1x']

    workdir = tempfile.mkdtemp(prefix="dd12ai_")
    agg = {'next_pos': 0, 'back_step': 0, 'bref_match': 0,
           'bref_match_caseless': 0, 'advance': 0, 'encoding': 0}
    npairs = nstrict = nwidens = 0
    ndiverge_strict = ndiverge_widens = nbyteonly = nnextpos_bad = 0
    findings = []
    try:
        for idx, pat in enumerate(patterns):
            r = compile_pair(pat, workdir, idx)
            if r is None:
                continue
            if r == "byte-only":
                nbyteonly += 1
                continue
            tb, tu = r
            nb, cb = excise(tb, "byte#%d" % idx)
            nu, cu = excise(tu, "utf8#%d" % idx)
            npairs += 1
            for k in agg:
                agg[k] += cb[k] + cu[k]
            if cb['next_pos'] != 1 or cu['next_pos'] != 1:
                nnextpos_bad += 1
                if len(findings) < 20:
                    findings.append("pat=[%s]: next_pos not exactly 1 per side (byte=%d utf8=%d)"
                                     % (pat, cb['next_pos'], cu['next_pos']))
            for k in ('back_step', 'bref_match', 'bref_match_caseless', 'advance'):
                if cb[k] != cu[k] and len(findings) < 20:
                    findings.append("pat=[%s]: asymmetric %s (byte=%d utf8=%d) -- (b) the normalization count"
                                     % (pat, k, cb[k], cu[k]))
            if cb['encoding'] != 1 or cu['encoding'] != 1:
                if len(findings) < 20:
                    findings.append("pat=[%s]: .encoding field not exactly 1 per side (byte=%d utf8=%d)"
                                     % (pat, cb['encoding'], cu['encoding']))

            widens = widens_under_utf8(pat)
            if widens:
                nwidens += 1
            else:
                nstrict += 1
            if nb != nu:
                if widens:
                    ndiverge_widens += 1
                else:
                    ndiverge_strict += 1
                    if len(findings) < 20:
                        d = list(difflib.unified_diff(nb.splitlines(), nu.splitlines(), lineterm=""))
                        findings.append("pat=[%s] (STRICT bucket -- an encoding conditional reached the hot path): TEXT DIFFERS:\n    "
                                         % pat + "\n    ".join(d[:12]))
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    print("PAIRS=%d STRICT=%d WIDENS=%d DIVERGE_STRICT=%d DIVERGE_WIDENS=%d BYTEONLY=%d NEXTPOS_BAD=%d" %
          (npairs, nstrict, nwidens, ndiverge_strict, ndiverge_widens, nbyteonly, nnextpos_bad))
    for k in ('next_pos', 'back_step', 'bref_match', 'bref_match_caseless', 'advance', 'encoding'):
        print("EXCISED %s=%d" % (k, agg[k]))
    for f in findings:
        print("FINDING " + f)
    return 0

if __name__ == "__main__":
    sys.exit(main())
PY
py12_rc=$?
if [ "$py12_rc" != 0 ]; then
    bad "DD12a(i) the rebuilt instrument itself failed to run: $(head -3 "$WORKDIR/dd12ai.err")"
else
    d12_line="$(grep -o 'PAIRS=[0-9]* STRICT=[0-9]* WIDENS=[0-9]* DIVERGE_STRICT=[0-9]* DIVERGE_WIDENS=[0-9]* BYTEONLY=[0-9]* NEXTPOS_BAD=[0-9]*' "$WORKDIR/dd12ai.out")"
    eval "$d12_line"
    echo "  DD12a(i) pairs compared: $PAIRS (byte-only: $BYTEONLY) — strict-identity bucket: $STRICT, widens-under-utf8 bucket: $WIDENS"
    grep '^EXCISED ' "$WORKDIR/dd12ai.out" | sed 's/^/    /'
    if grep -q '^EXTRACT-FAIL' "$WORKDIR/dd12ai.out" "$WORKDIR/dd12ai.err" 2>/dev/null; then
        bad "DD12a(i) extraction FAILED on at least one artifact (an anchor did not match -- see dd12ai.out/.err): $(grep '^EXTRACT-FAIL' "$WORKDIR/dd12ai.out" "$WORKDIR/dd12ai.err" 2>/dev/null | head -1)"
    elif [ "$PAIRS" -lt 200 ]; then
        bad "DD12a(i) only $PAIRS pairs compared — the population collapsed (floor 200)"
    elif [ "$NEXTPOS_BAD" -gt 0 ]; then
        bad "DD12a(i) $NEXTPOS_BAD pattern(s) did not carry exactly one next_pos residual per side — (a)'s non-empty-by-construction floor failed"
    elif [ "$WIDENS" -eq 0 ]; then
        bad "DD12a(i) the widens-under-utf8 bucket (dot/negated-class patterns) is EMPTY — the exemption is dead code, certifying nothing about the population it exists for"
    elif [ "$STRICT" -lt 150 ]; then
        bad "DD12a(i) only $STRICT pairs took the strict identity path (floor 150) — the widens exemption may be over-classifying"
    else
        # (a) non-vacuity: every named region reached at least once.
        vac=0
        for k in next_pos back_step bref_match bref_match_caseless advance encoding; do
            v="$(grep "^EXCISED $k=" "$WORKDIR/dd12ai.out" | grep -oE '[0-9]+$')"
            if [ "${v:-0}" -eq 0 ]; then
                bad "DD12a(i) region '$k' was never excised across the whole run — dead code, certifying nothing about it"
                vac=1
            fi
        done
        if [ "$DIVERGE_STRICT" -eq 0 ] && [ "$vac" -eq 0 ]; then
            ok "DD12a(i) the engine minus its named encoding-owned regions is byte-identical between byte and utf8 artifacts on $STRICT strict-identity pairs ($WIDENS widens-under-utf8 pairs correctly exempted, source-text comparison, darwin and linux alike)"
        elif [ "$DIVERGE_STRICT" -gt 0 ]; then
            bad "DD12a(i) $DIVERGE_STRICT of $STRICT strict-identity pairs differ OUTSIDE the named encoding-owned regions — an encoding conditional reached the hot path (see dd12ai.out FINDING lines)"
            grep '^FINDING' "$WORKDIR/dd12ai.out" | head -10 | sed 's/^/    /' >&2
        fi
        echo "  DD12a(i) widens-under-utf8 pairs differing (expected — different automaton, not a defect): $DIVERGE_WIDENS of $WIDENS"
    fi
fi

# ---------------------------------------------------------------------------
# DD12a(ii)  THE SECOND-BACKEND VALIDATION OF D58's REVISIT-WHEN NAMES
#
# The seam's ENTRIES TABLE interface is unchanged by the second backend: a
# utf8 artifact carries the four residual entries under the SAME SIGNATURES
# the byte backend emits. Read the four declared signatures out of a byte
# artifact and a utf8 one that USE all four (a lookbehind-and-backref pattern
# forces next_pos + back_step + a bref compare) and require them equal.
# ---------------------------------------------------------------------------
# The witness forces three of the four residual entries: next_pos (always),
# back_step (the lookbehind) and bref_match_caseless (the caseless backref).
# The name-bearing FIRST LINE of each signature is a stable comparable line
# (the bref signatures wrap onto a second line, which a `)`-terminated grep
# would miss). Prefix-normalised, the two backends' lines must be identical —
# the entries-table interface is backend-neutral (D58 P-1).
sigpat='(?i)(?<=a)(b)\1x'
db="$WORKDIR/sigb"; du="$WORKDIR/sigu"; mkdir -p "$db" "$du"
sigs_of() { grep -oE '(size_t|ptrdiff_t) [A-Za-z]+_(next_pos|back_step|bref_match|bref_match_caseless)\(' "$1" \
            | sed -E 's/ [bu]_/ PFX_/' | LC_ALL=C sort -u; }
if pcrec_run "$PCREC" --features all -e byte -p b -o "$db/a.c" -- "$sigpat" >/dev/null 2>&1 \
   && pcrec_run "$PCREC" --features all -e utf8 -p u -o "$du/a.c" -- "$sigpat" >/dev/null 2>&1; then
    nsig="$(sigs_of "$db/a.c" | grep -c .)"
    if diff -q <(sigs_of "$db/a.c") <(sigs_of "$du/a.c") >/dev/null 2>&1 && [ "$nsig" -ge 3 ]; then
        ok "DD12a(ii) the seam's residual entries appear under identical signatures across both backends ($nsig entries; D58 P-1)"
    elif [ "$nsig" -lt 3 ]; then
        bad "DD12a(ii) only $nsig residual entries found in the witness — it did not force back_step + a bref compare"
    else
        bad "DD12a(ii) a residual entry's signature DIFFERS between backends — the entries-table interface is not backend-neutral (D58 revisit event)"
        diff <(sigs_of "$db/a.c") <(sigs_of "$du/a.c") | head >&2
    fi
else
    bad "DD12a(ii) the signature-witness pattern did not compile under both encodings"
fi

# ---------------------------------------------------------------------------
# K49   THE ADVANCE-AGREEMENT CHECK — the emitted unanchored RETRY ADVANCE
#       against the same artifact's own `next_pos`.
#
# WHY IT EXISTS. K49 was an unanchored search retrying at the next BYTE rather
# than the next character boundary, so `(?<!.)` over `CE B1 CE B2` reported a
# match at offset 3 — inside a character. The fix routes the advance through
# the encoding backend (src/gen/enc/, enc.h's `advance` field), which means the
# boundary rule is now spelled TWICE per backend: once as the caller-facing
# `next_pos` entry, and once as inline text spliced into the engine body,
# because DD-12 (7) and sabotage row S68 forbid an engine calling the entry.
#
# TWO SPELLINGS OF ONE RULE NEED A TIE, and this project already has the shape:
# `tests/backrefs/fold_agreement_check.c` ties `enc_byte.c`'s caseless compare
# to `pcrec_ascii_fold` over all 65,536 ordered byte pairs, with the residual
# side read out of an artifact pcrec actually emitted. This does the same for
# the boundary rule, and it reads BOTH sides out of one emitted artifact: the
# inline advance is EXTRACTED FROM THE EMITTED C and compiled as a function,
# and it is compared against that same artifact's linked `next_pos`. A backend
# that changes one spelling and not the other fails HERE, rather than in a
# corpus cell nobody thought to write.
#
# THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS: the two sides come
# from different files of the backend (`advance` vs the `PCREC_ENCE_NEXT_POS`
# entry) and are compared through a compiler, not by reading the emitter.
#
# NON-VACUITY, in both directions, because an alphabet without continuation
# bytes would make this pass on a compiler that never fixed anything: under
# `byte` every answer MUST be `pos + 1` (that is the encoding), and under
# `utf8` at least one answer MUST NOT be, or the sweep never reached a
# multi-byte shape and is certifying nothing.
#
# SCOPE OF THE CLAIM: `pos < n` only. The emitted loop's own guard
# (`if (attempt_position >= subject_length) return 0;`) means the advance is
# never reached at or past the end, so agreement there is not asserted — and
# `next_pos`' documented `pos + 1` answer for `pos >= n` is a promise to the
# find-all caller, not to this loop.
# ---------------------------------------------------------------------------
adv_witness='a*'      # nullable => no prefilter, so no retry-window recompute
                      # follows the advance and the extraction below is exact.
for aenc in byte utf8; do
    d="$WORKDIR/adv_$aenc"; mkdir -p "$d"
    if ! pcrec_run "$PCREC" --engine=vm -e "$aenc" -p a -o "$d/a.c" \
            -- "$adv_witness" >/dev/null 2>&1; then
        bad "K49 the advance witness '$adv_witness' did not compile under -e $aenc"
        continue
    fi
    # Extract the advance: the lines between the loop's own end guard and the
    # close of the for(;;) body. Anchored on emitted text, so a change to the
    # loop's shape breaks the extraction loudly instead of silently matching
    # nothing (the empty-extraction case is caught below).
    awk '/if \(attempt_position >= subject_length\) return 0;/{f=1;next}
         f&&/^    \}/{exit} f' "$d/a.c" > "$d/adv.inc"
    if ! grep -q 'attempt_position' "$d/adv.inc"; then
        bad "K49 the advance could not be extracted from the -e $aenc artifact — the emitted retry loop's shape moved and this check stopped reading it (an empty extraction would otherwise PASS vacuously)"
        continue
    fi
    cat > "$d/agree.c" <<'AGREE'
#include <stddef.h>
#include <stdio.h>
extern size_t a_next_pos(const unsigned char *s, size_t n, size_t pos);

/* The artifact's OWN emitted advance, verbatim, as a callable function. */
static size_t adv_inline(const unsigned char *subject, size_t subject_length,
                         size_t attempt_position)
{
#include "adv.inc"
    return attempt_position;
}

/* One byte per UTF-8 structural role, plus an invalid one: the sweep is
 * exhaustive over THIS alphabet rather than over 256 bytes, because what the
 * rule reads is a byte's ROLE (continuation or not) and nothing else. */
static const unsigned char ALPHA[] = { 0x41, 0xC2, 0xE0, 0xF0, 0x80, 0xBF, 0xFF };
#define NA ((int)(sizeof ALPHA / sizeof ALPHA[0]))

int main(void)
{
    unsigned char s[4];
    long cells = 0, disagree = 0, nontrivial = 0;
    int len;
    for (len = 0; len <= 4; len++) {
        long total = 1, k;
        int i;
        for (i = 0; i < len; i++) total *= NA;
        for (k = 0; k < total; k++) {
            long q = k;
            size_t pos;
            for (i = 0; i < len; i++) { s[i] = ALPHA[q % NA]; q /= NA; }
            for (pos = 0; pos < (size_t)len; pos++) {
                size_t a = adv_inline(s, (size_t)len, pos);
                size_t b = a_next_pos(s, (size_t)len, pos);
                cells++;
                if (a != b) {
                    if (disagree < 5)
                        printf("DISAGREE len=%d pos=%zu advance=%zu next_pos=%zu\n",
                               len, pos, a, b);
                    disagree++;
                }
                if (a != pos + 1) nontrivial++;
            }
        }
    }
    printf("CELLS=%ld DISAGREE=%ld NONTRIVIAL=%ld\n", cells, disagree, nontrivial);
    return disagree ? 1 : 0;
}
AGREE
    if ! gen_cc "encadv $aenc" "$CC" -O1 -w -I "$d" -o "$d/agree" \
            "$d/agree.c" "$d/a.c" >/dev/null 2>&1; then
        bad "K49 the -e $aenc advance-agreement driver did not compile"
        continue
    fi
    aout="$("$d/agree" 2>&1)"; arc=$?
    acells="$(printf '%s\n' "$aout" | sed -n 's/.*CELLS=\([0-9]*\).*/\1/p')"
    antriv="$(printf '%s\n' "$aout" | sed -n 's/.*NONTRIVIAL=\([0-9]*\).*/\1/p')"
    if [ "$arc" != 0 ]; then
        bad "K49 the emitted -e $aenc retry advance DISAGREES with the same artifact's next_pos — the boundary rule has two spellings and they have drifted"
        printf '%s\n' "$aout" | head -6 >&2
        continue
    fi
    ok "K49 the emitted -e $aenc retry advance agrees with the artifact's own next_pos on all $acells cells (pos < n)"
    if [ "$aenc" = byte ]; then
        if [ "${antriv:-1}" -eq 0 ]; then
            ok "K49 non-vacuity control: every -e byte advance IS pos + 1 ($acells cells) — the byte artifact's step did not move"
        else
            bad "K49 the -e byte advance answered something other than pos + 1 on $antriv cell(s) — under this encoding every position is a boundary, so the byte artifact has MOVED"
        fi
    else
        if [ "${antriv:-0}" -ge 1 ]; then
            ok "K49 non-vacuity control: the -e utf8 advance differs from pos + 1 on $antriv of $acells cells — the sweep reached the multi-byte shape the rule is about"
        else
            bad "K49 the -e utf8 advance is pos + 1 EVERYWHERE — either the fix is not in this artifact or the alphabet never produced a continuation byte, and the agreement above certifies nothing"
        fi
    fi
done

# ---------------------------------------------------------------------------
# S-U8  THE CLAMP-STRIDE PROBE
# ---------------------------------------------------------------------------
if pcrec_run "$PCREC" --features all -e utf8 -p rx -o - -- '(a)(?:\x{3b1}){0,3}x' 2>/dev/null \
        | grep -q 'RX_PRUNE_CLAMP_SPAN(scan_position, 1, 2)'; then
    ok "S-U8 the utf8 MRL clamp stride is the encoded length (RX_PRUNE_CLAMP_SPAN ... 1, 2) — the prune counts encoded bytes (§5.6.1)"
else
    bad "S-U8 the expected clamp stride 2 (α's encoded length) is absent — the MRL bound stopped counting encoded bytes"
fi

finish
