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
        bad "§8.5 pattern compiled under byte but NOT utf8: $pat"
        diverge=$((diverge + 1)); diffn=$((diffn + 1)); continue
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
                bad "§8.5 byte/utf8 DIVERGE on ASCII: pat=[$pat] subj=[$subj] -> $out"
                diverge=$((diverge + 1))
            fi
        done
    fi
    diffn=$((diffn + 1))
done < "$WORKDIR/blocks.tsv"

echo "  §8.5 ran $diffn ASCII blocks ($ccfail cc-skipped), $diverge divergences"
if [ "$diverge" -eq 0 ]; then
    ok "§8.5 byte and utf8 artifacts agree on every ASCII subject ($diffn blocks)"
else
    bad "§8.5 $diverge byte/utf8 divergences on ASCII input — likeliest cause: the length-split boundary at 0x7F (§8.5 P-11)"
fi

# ---------------------------------------------------------------------------
# CHK3  THE STAMP CENSUS + DD12a(i) HOT-LOOP SHAPE IDENTITY
#
# For each ASCII pattern already emitted above: (CHK3) record the byte and
# utf8 stamps and confirm the byte stamps are unchanged from the identity
# gate's expectation implicitly (they are the same compiler); the interesting
# half is that on an ASCII pattern the utf8 stamps EQUAL the byte ones, since
# the lowering is the identity below 0x7F. (DD12a-i) the engine bodies are
# byte-identical. A utf8 artifact of an ASCII pattern that stamps differently,
# or whose body differs, would mean an encoding conditional reached a path it
# must not.
# ---------------------------------------------------------------------------
stamp_of() { grep -oE "#define (RX_ENGINE|RX_ENGINE_SEL|RX_DFA_TABLE|RX_VM_STRATS|RX_VM_RUNGS) [^ ]*.*" "$1" 2>/dev/null | LC_ALL=C sort; }
shape_diff=0; stamp_diff=0; shape_checked=0
for d in "$WORKDIR"/b_*; do
    [ -f "$d/b.c" ] && [ -f "$d/u.c" ] || continue
    if ! diff -q <(stamp_of "$d/b.c") <(stamp_of "$d/u.c") >/dev/null 2>&1; then
        stamp_diff=$((stamp_diff + 1))
        echo "  CHK3 stamp differs (ASCII pattern, byte vs utf8): $d" >> "$WORKDIR/stampdiff.txt"
    fi
    # hot-loop shape: compare EXECUTED CODE, not source text. The two artifacts
    # differ in source only by the artifact prefix (`b_`/`B_` vs `u_`/`U_`, in
    # symbol names and the `.h` include) and by orientation-comment prose that
    # legitimately names the byte automaton either way — neither is code. So
    # compile both to `.o` and compare `.text` + `.rodata` bytes with addresses
    # stripped (run_object_neutrality.sh's own instrument): the prefix lives in
    # the symbol table, not in executed bytes, and the embedded pattern string
    # is identical. A real encoding conditional on the hot path would move a
    # `.text` byte. `--engine=vm` and `-e` are already fixed; -O0 keeps the
    # compile fast and the comparison faithful to the emitter's own output.
    shape_checked=$((shape_checked + 1))
    if gen_cc "encshape b $shape_checked" "$CC" -O0 -c -w -I "$d" -o "$d/b.o" "$d/b.c" >/dev/null 2>&1 \
       && gen_cc "encshape u $shape_checked" "$CC" -O0 -c -w -I "$d" -o "$d/u.o" "$d/u.c" >/dev/null 2>&1; then
        objdump -s -j .text -j .rodata "$d/b.o" 2>/dev/null | sed -E 's/^ *[0-9a-f]+ //; 1,2d' > "$d/b.obj"
        objdump -s -j .text -j .rodata "$d/u.o" 2>/dev/null | sed -E 's/^ *[0-9a-f]+ //; 1,2d' > "$d/u.obj"
        if ! diff -q "$d/b.obj" "$d/u.obj" >/dev/null 2>&1; then
            shape_diff=$((shape_diff + 1))
            [ "$shape_diff" -le 3 ] && { echo "== $d"; diff "$d/b.obj" "$d/u.obj" | head -6; } >> "$WORKDIR/shapediff.txt"
        fi
    fi
done
echo "  CHK3 ASCII stamp differences: $stamp_diff (expected 0 — lowering is identity below 0x7F)"
if [ "$stamp_diff" -eq 0 ]; then
    ok "CHK3 every ASCII pattern's utf8 stamps equal its byte stamps"
else
    bad "CHK3 $stamp_diff ASCII patterns stamp differently under utf8 (see stampdiff.txt) — an encoding conditional reached the stamp"
fi
echo "  DD12a(i) hot-loop shape check over $shape_checked ASCII artifacts: $shape_diff differing"
if [ "$shape_diff" -eq 0 ]; then
    ok "DD12a(i) ASCII pattern emits a byte-identical engine body under byte and utf8 (no encoding conditional on the hot path)"
else
    bad "DD12a(i) $shape_diff ASCII artifacts differ in body between byte and utf8 (see shapediff.txt) — the lowering is not the identity below 0x7F, or a conditional leaked"
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
# S-U8  THE CLAMP-STRIDE PROBE
# ---------------------------------------------------------------------------
if pcrec_run "$PCREC" --features all -e utf8 -p rx -o - -- '(a)(?:\x{3b1}){0,3}x' 2>/dev/null \
        | grep -q 'RX_PRUNE_CLAMP_SPAN(scan_position, 1, 2)'; then
    ok "S-U8 the utf8 MRL clamp stride is the encoded length (RX_PRUNE_CLAMP_SPAN ... 1, 2) — the prune counts encoded bytes (§5.6.1)"
else
    bad "S-U8 the expected clamp stride 2 (α's encoded length) is absent — the MRL bound stopped counting encoded bytes"
fi

finish
