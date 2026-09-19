#!/usr/bin/env bash
# tests/registry/limits_check.sh — [LIM-1] THE REGISTRY CHECK for
# `pcrec --list-limits` (D90): CODE (the dump) vs SPEC
# (docs/spec/limits.md §3) in one direction, plus the INDEPENDENT-SOURCE
# detector D90 itself asks for — a bare numeric #define/enum member outside
# src/core/limits.def that LOOKS like a policy limit (docs/dev/learnings.md
# §3: "a control must not share a source with what it controls" — this
# script's second half reads the TREE, never limits.def, for that reason).
#
# THREE PARTS:
#
#   1. ROW COUNT, pinned by NAME MANIFEST rather than by a bare number
#      (docs/dev/learnings.md §3: "exact counts disarm themselves via their
#      own failure message; the fix is a manifest naming irreplaceable
#      rows"). A row silently dropped from limits.def still fails even if
#      some OTHER row was added the same day and the raw count happens to
#      hold.
#   2. DUMP -> docs/spec/limits.md §3/§8, forward only: every row whose
#      `anchor` column names a section has its VALUE, comma-grouped the way
#      limits.md itself writes large numbers, findable as a literal
#      substring within THAT section's own text (extracted between its
#      heading and the next heading at the same or higher level) — never
#      the whole document, so a coincidental match in an unrelated section
#      does not pass silently. This is the derivation limits.md §3 promises
#      ("every number... verified against the shipped surface... the
#      command that produced each re-measurement is recorded"): the command
#      is now `pcrec --list-limits`, and this check is what makes that a
#      standing fact rather than a one-time claim. Reverse (every limits.md
#      §3/§8 number traces to a row) is NOT attempted as a blind sweep —
#      that document's own prose is full of MEASURED WITNESS numbers (byte
#      counts of specific artifacts, timings, corpus sizes) that are not
#      limit VALUES at all, and a blind number scan over free prose is
#      exactly the "population nobody counts" shape docs/dev/learnings.md
#      §3 (K35) warns about. The anchor->row assignment was built by hand
#      from a full read of limits.md (docs/dev/lanes/lim1_report.md records
#      it); this check is what stops a FUTURE edit from breaking the
#      forward half silently.
#   3. dump-vs-CODE: every numeric `#define`/enum-member whose NAME matches
#      a policy-limit shape (MAX/CAP/LIMIT/BUDGET/_LEN/DEPTH/NEST) anywhere
#      under src/, cli/, lib/ OUTSIDE src/core/limits.def itself must be one
#      of limits.def's own 45 names, OR be on the small NAMED, CITED
#      allowlist below — every one of which is a constant limits.h's own
#      header comment already excludes BY RULE ("local algorithmic bounds
#      whose correctness argument lives beside them", "structural
#      constants") or an API sentinel value (not the limit itself). A row
#      that is neither is the sabotage shape S208 exists to catch: a new
#      policy number introduced as a bare literal instead of a table row.
#
# Usage: bash tests/registry/limits_check.sh
# Env: PCREC (default build/pcrec), LIMITSMD (default docs/spec/limits.md),
#   ROOT (default the repo root), KEEP=1 is accepted for symmetry with the
#   sibling scripts (nothing here needs a temp dir).

set -u
export LC_ALL=C   # K35 — see tests/harness/run.sh's own header for why

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37]: pcrec_run bounds the call below
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
LIMITSMD="${LIMITSMD:-$ROOT_DIR/docs/spec/limits.md}"

if [ ! -x "$PCREC" ]; then
    echo "limits_check: $PCREC not built — run 'make' first" >&2
    exit 1
fi
if [ ! -f "$LIMITSMD" ]; then
    echo "limits_check: $LIMITSMD not found" >&2
    exit 1
fi

npass=0
nfail=0
ok()   { npass=$((npass + 1)); echo "PASS: $1"; }
bad()  { nfail=$((nfail + 1)); echo "FAIL: $1" >&2; }

DUMP="$(pcrec_run "$PCREC" --list-limits)"
DATA="$(printf '%s\n' "$DUMP" | grep -v '^#')"

# ---------------------------------------------------------------------------
# 1. ROW COUNT, by manifest
# ---------------------------------------------------------------------------
n="$(printf '%s\n' "$DATA" | grep -vc '^$' || true)"
NAMES="$(printf '%s\n' "$DATA" | cut -f1 | sort)"
EXPECT_NAMES="$(cat <<'EOF' | sort
PCREC_MAX_PREFIX_LEN
PCREC_MAX_EMIT_NAME_LEN
PCREC_DFA_OVERFLOW_WHY_LEN
PCREC_MAX_NFA_STATES
PCREC_MAX_DFA_STATES_GOTO
PCREC_MAX_DFA_STATES_TABLE
PCREC_MAX_TABLE_ENTRIES
PCREC_MAX_SUBSET_ELEMS
PCREC_MAX_AUTO_DFA_ELEMS
PCREC_MAX_VM_NODES
PCREC_MAX_VM_REPEAT_COPIES
PCREC_MAX_VM_REPLICATION_PRODUCT
PCREC_DEFAULT_UNROLL_K
PCREC_MAX_POSSESS_POSITIONS
PCREC_MAX_REVDET_BODY_GROUPS
PCREC_MAX_ALTCLS_FACTOR_DEPTH
PCREC_MAX_REPEAT
PCREC_MAX_GROUP_DEPTH
PCREC_MAX_GROUP_NAME
PCREC_VERB_NAME_MAX
PCREC_VERB_LIMIT_ACC_MAX
PCREC_UPROP_NAME_MAX
PCREC_MAX_SPLICE_NODES
PCREC_MAX_SPLICE_TOTAL
PCREC_ANCHORED_MAX_STATES
PCREC_MAX_VM_EMIT_CODE_BYTES
PCREC_DEFAULT_WARN_EMIT_BYTES
PCREC_MAX_EMIT_BYTES
PCREC_SIZE_TERM_THRESHOLD
PCREC_SIZE_TERM_BAR
VM_DEFAULT_STEP_BUDGET
VM_DEFAULT_WORK_BUDGET
VM_DEFAULT_RESUME_FRAMES
VM_DEFAULT_TRAIL_FRAMES
VM_MAX_AUTO_RESUME_FRAMES
VM_MAX_AUTO_TRAIL_FRAMES
VM_ISL_MIN_BRANCHES
VM_ISL_MIN_BRANCHES_PREFIXED
VM_ISL_MAX_WORDS
VM_ISL_MAX_BYTES
VM_ISL_MAX_DEPTH
VM_ISL_BYTES_PER_NODE
VM_ISL_BYTES_PER_CHAIN_NODE
VM_ISL_SIZE_FACTOR
PCREC_PREFIX_K_MAX
PCREC_OFSK_MAX_SET
PCREC_MINW_MAX
PCREC_MAX_SCAN_EDGES
PCREC_MIN_SCAN_CHAIN
PCREC_STARTPOS_GUARD_TEXT_MAX
VM_INLINE_CHAIN_MAX_BYTES
RC_NUMBER_MAX
BR_NUMBER_MAX
LA_MSG_MAX
RXT_CONFIG_NAME_MAX
RXT_TARGET_PREFIX_MAX
RXT_TARGET_DEF_MAX
RXT_FROM_NEST_MAX
EOF
)"

if [ "$n" -eq 58 ] && [ "$NAMES" = "$EXPECT_NAMES" ]; then
    ok "[count] --list-limits reports all 58 named rows, exactly the manifest this script carries"
else
    bad "[count] --list-limits reports $n row(s); manifest mismatch — a row was added, removed or renamed. Diff:"
    diff <(printf '%s\n' "$EXPECT_NAMES") <(printf '%s\n' "$NAMES") >&2 || true
fi

# ---------------------------------------------------------------------------
# 2. DUMP -> docs/spec/limits.md, forward (anchored rows only)
# ---------------------------------------------------------------------------
# Comma-group an integer the way limits.md's own prose does (500000000 ->
# 500,000,000). Values below 1000 are never comma-grouped in that document
# and are searched bare.
group() {
    local v="$1" neg=""
    case "$v" in -*) neg="-"; v="${v#-}";; esac
    if [ "${#v}" -le 3 ]; then printf '%s%s' "$neg" "$v"; return; fi
    printf '%s' "$neg"
    echo "$v" | rev | sed -E 's/([0-9]{3})/\1,/g' | sed 's/,$//' | rev
}

# Extract ONE section's own text: from its heading line to the next heading
# at the same or shallower level (### vs ##), so a value search cannot
# stray into a neighbouring section that happens to share a substring.
section_text() {
    local anchor="$1"
    awk -v anchor="$anchor" '
        BEGIN { insect = 0; level = 0 }
        /^#+ / {
            m = match($0, /^#+/)
            thislevel = RLENGTH
            hdr = $0
            sub(/^#+ */, "", hdr)
            if (insect && thislevel <= level) { insect = 0 }
            if (!insect) {
                # match "3.1 Foo", "3 The numbers", "8 Emitted..." etc at
                # the START of the heading text (section number then a
                # space or end-of-line), so "3.1" does not match "3.10".
                if (hdr ~ ("^" anchor "([ .]|$)")) { insect = 1; level = thislevel; next }
            }
        }
        insect { print }
    ' "$LIMITSMD"
}

anchored="$(printf '%s\n' "$DATA" | awk -F'\t' '$6 != ""')"
miss=0
while IFS=$'\t' read -r name value unit kind override anchor desc; do
    [ -z "$name" ] && continue
    sect="$(section_text "$anchor")"
    if [ -z "$sect" ]; then
        bad "[doc] $name cites limits.md section '$anchor' — no such heading found"
        miss=1
        continue
    fi
    g="$(group "$value")"
    if printf '%s' "$sect" | grep -qF "$g"; then
        ok "[doc] $name = $value ($g) appears in limits.md §$anchor"
    else
        bad "[doc] $name = $value ($g) NOT found in limits.md §$anchor — the table and the doc have drifted"
        miss=1
    fi
done <<< "$anchored"
[ "$miss" -eq 0 ] || nfail=$((nfail))  # (bad() already counted each; nothing to add)

# ---------------------------------------------------------------------------
# 3. dump-vs-CODE: EVERY numeric constant in the tree is DISPOSITIONED
# ---------------------------------------------------------------------------
# D107 (Frank, 2026-09-17; built [REVW.4] wave 4, 2026-09-19) INVERTED this
# arm. It used to grep for a CEILING VOCABULARY in the constant's NAME
# (`MAX|_MIN_|CAP|LIMIT|BUDGET|THRESHOLD|_LEN|DEPTH|NEST`) and check only what
# that vocabulary reached. The vocabulary missed a live constant TWICE —
# `VM_ISL_MIN_BRANCHES` (r53/[ENG-ISL]) and then lens 3's F1 population of 14,
# headed by `SIZE_TERM_BAR_DEFAULT` and `C_MEMCHR` — and BOTH repairs widened
# the vocabulary, which is the patch that fails again the next time a knee is
# spelled `WEIGHT` or `BIAS`. The filter's KIND is what was wrong. So:
#
#   THE SCAN IS NOT KEYED ON THE NAME AT ALL. It takes EVERY object-like
#   `#define NAME <numeric literal>` and EVERY explicitly numeric-valued enum
#   member under src/, cli/ and lib/, and requires each one to be a
#   `limits.def` row, on the LIMIT allowlist, or on the NON-LIMIT allowlist.
#   A constant that is on none of the three FAILS. "Every number is
#   dispositioned" is what D90's own text always claimed; this is the first
#   version of this arm for which it is true.
#
# WHAT THE SCAN CANNOT SEE, stated because §5 item 4 of docs/dev/
# coding_guide.md says a filter must say so (this arm is that rule's own
# motivating instance, so it had better):
#
#   (i)  A constant whose value is an EXPRESSION rather than a literal —
#        `COMPILE_MAX_ATTEMPTS = 3 + 2 * (SIZE_TERM_LADDER_N + 1) + 1 +
#        SDR_MAX` (compile.c) is invisible here, and deliberately: a value
#        DERIVED from other named values is not a bare number given a name,
#        which is the shape D90 is about. It was on the old allowlist and is
#        not on either new one, because an allowlist entry the scan never
#        reaches is a lie the ARM 3c vacuity check below now refuses.
#   (ii) An ORDINAL ENUM's members. An enum whose explicit initializers are
#        exactly 0, 1, 2, ... in member order is NUMBERING ITS OWN MEMBERS:
#        delete every initializer and not one value changes, so none of those
#        numbers can be a policy. That rule is STRUCTURAL, not lexical — it
#        asks what the number does, never what it is called — and it is what
#        keeps this arm from firing on all 56 of this tree's discriminated-
#        union tag enums. Its blind spot is exact and small: a real policy
#        number that happens to sit at its own ordinal position inside an
#        otherwise-ordinal enum (`enum { FOO = 0, ROUNDS = 1 };`). One
#        NON-ordinal member re-arms the WHOLE enum — every numeric member of
#        it is scanned, which is why all four `SDR_*` rows appear on an
#        allowlist below over `SDR_MAX = 2` alone.
#   (iii) Text that is not C: comments and string-literal interiors are masked
#        before anything is matched, so the ten `#define PCREC_VM_RUNG_*`
#        lines emit_dfa.c PRINTS INTO ITS ARTIFACTS are not read as pcrec's
#        own constants. Without the mask this arm would report ten failures
#        about a file it cannot fix.
#
# THREE SUB-ARMS, because a classifier alone can go quiet:
#   3a  every scanned constant is a row, on the LIMIT allowlist, or on the
#       NON-LIMIT allowlist;
#   3b  the scan found at least SCAN_FLOOR constants (K35: a masker or an awk
#       program that silently stops matching otherwise reads GREEN, having
#       classified an empty population perfectly);
#   3c  every allowlist name on BOTH lists was actually reached by the scan
#       ([MECH-REACH]: an entry that matches nothing is either a stale name
#       or a scan that stopped reaching its site, and both look like a pass).
#
# THE LIMIT ALLOWLIST — limit-SHAPED numbers excluded from limits.def BY RULE,
# each argued at its own site, never silently:
#   TRIE_MAX_RDEPTH, MAX_GROUPS (src/ir/nfa.c)     — limits.h's own header:
#     "local algorithmic bounds whose correctness argument lives beside
#     them... moving those here would separate a bound from the reason it
#     is sound"
#   ABLOCK_MIN (src/core/arena.c), PCREC_HASH64_MUL (src/ir/dfa.c) — the same
#     header's OTHER exclusion, "structural constants do not [belong here]":
#     an arena block size (its own example, verbatim) and the FNV-1a 64-bit
#     prime, which is a fact about a published hash function and not a choice
#     pcrec could make differently
#   LEGEND_MAX_STATES, LEGEND_MAX_EXAMPLE (emit_dfa.c) — a DEBUG LISTING's
#     own truncation width, not a promise about what pcrec accepts/rejects
#   VM_MAX_STRIDE, VM_FAST_TIER_BYTES, VM_FAST_TIER_MIN (emit_vm.c) —
#     emitter-internal rung-selection knobs with their own proofs beside
#     them (src/gen/CLAUDE.md's [OPT-1] section for the FAST_TIER pair)
#   VM_MRL_DYN_MAX (emit_vm.c) — a soundness-preserving retreat on a
#     runtime follow-min EXPRESSION LENGTH, with its own correctness
#     argument at the constant ("the arithmetic must be right where nobody
#     is watching"); unreachable on anything pcrec compiles today, and not
#     a bound on what pcrec accepts/rejects/promises
#   SELECT_MAX_ROUNDS (select_engine.c) — a bounded-loop iteration cap with a
#     from-day-one-bound argument at the loop itself (src/core/CLAUDE.md's
#     [SEL-1] section), not a value a pattern can be measured against
#   C_MEMCHR, C_BITMAP, C_VERIFY, C_ENTER, C_MISPRED, MATERIAL_NUM,
#     MATERIAL_DEN (src/opt/prefix_k.c) — D107's seven "argued at site"
#     dispositions, admitted here for the first time. They are the COST MODEL
#     of one comparison (relative cycle weights for four prefilter shapes, a
#     branch-mispredict charge, and the 2/1 materiality ratio), carrying 12
#     lines of derivation at their own site. None is a value a pattern is
#     measured against: they are the coefficients of a ranking, and changing
#     one changes which prefilter WINS, never what pcrec accepts or refuses.
#     Each is one term of a single expression, so moving them into
#     `limits.def` would scatter a formula across two files — the mirror
#     image of the reason TRIE_MAX_RDEPTH stays put.
#
# THE NON-LIMIT ALLOWLIST — numbers that are not bounds at all. D107 names
# three kinds and the population needed a fourth:
#   SENTINELS (a reserved value the surrounding type cannot otherwise mean):
#     PREMUL_DEAD (emit_dfa.c, the pre-multiplied table's dead cell),
#     REG_SEL_ANY (internal.h), PCREC_DFA_DEAD (internal.h),
#     PCREC_RXT_WAVE_RESERVED (internal.h, the reserved-wave marker)
#   API ENUM VALUES (a value the public header PROMISES, so it is a contract
#     rather than a policy): PCREC_ENGINE_DFA/PCREC_ENGINE_VM (lib/pcrec.h,
#     also spelled into every artifact), the five PCREC_TUNE_* dial positions
#     (D103's pinned contract — the NUMBER -2..+2 is the surface), and the two
#     `_DEFAULT`/`_NONE` budget pairs, which are 0/-1 request codes meaning
#     "use the compiled-in default" / "no budget"; the real defaults are
#     VM_DEFAULT_STEP_BUDGET / VM_DEFAULT_WORK_BUDGET, both IN the table
#   SCHEMA VERSIONS: PCREC_RXT_WAVE_BUILT (internal.h)
#   THE FOURTH KIND — CARDINALITIES AND ORDINALS whose enum the (ii) rule
#     re-armed: VM_NRUNG (how many rungs exist, i.e. an array's length),
#     SDR_NONE/SDR_NO_ANCHORED/SDR_NO_PREMUL/SDR_MAX (the drop ladder's rung
#     ordinals plus its own highest-rung marker, which is what makes the enum
#     non-ordinal), and TRIE_ENABLED (a 0/1 BUILD SWITCH, not a magnitude).
#     These are numbers nothing can be measured against by construction.
SCAN_FLOOR=30

TMP3="$(mktemp -d "${TMPDIR:-/tmp}/limits_check.XXXXXX")"
trap '[ -n "${KEEP:-}" ] || rm -rf "$TMP3"' EXIT

# (a) MASK: blank C comments (line and block, including multi-line) and the
# INTERIORS of string/char literals, preserving line numbering, and prefix
# every line with FILE:LINE. Everything downstream reads this stream, never
# the raw source — see (iii) above.
cat > "$TMP3/mask.awk" <<'AWKEOF'
{
    line = $0; out = ""; i = 1; n = length(line)
    while (i <= n) {
        c = substr(line, i, 1); d = substr(line, i, 2)
        if (inblock) {
            if (d == "*/") { inblock = 0; out = out "  "; i += 2 }
            else { out = out " "; i++ }
            continue
        }
        if (d == "/*") { inblock = 1; out = out "  "; i += 2; continue }
        if (d == "//") { while (i <= n) { out = out " "; i++ }; continue }
        if (c == "\"" || c == "'") {
            q = c; out = out q; i++
            while (i <= n) {
                e = substr(line, i, 1)
                if (e == "\\") { out = out "  "; i += 2; continue }
                if (e == q) { out = out q; i++; break }
                out = out " "; i++
            }
            continue
        }
        out = out c; i++
    }
    print FILENAME ":" FNR ":" out
}
AWKEOF

# (b) ENUM WALK over the masked stream: emit every numeric-valued member of
# every NON-ORDINAL enum (rule (ii) above). Brace-depth tracked so a nested
# initializer list cannot be read as a member boundary.
cat > "$TMP3/enums.awk" <<'AWKEOF'
{
  p1 = index($0, ":"); file = substr($0, 1, p1 - 1); r = substr($0, p1 + 1)
  p2 = index(r, ":"); lno = substr(r, 1, p2 - 1); txt = substr(r, p2 + 1)
  if (file != prevfile) { state = 0; depth = 0; nm_i = 0; prevfile = file }
  i = 1; n = length(txt)
  while (i <= n) {
    rest = substr(txt, i)
    if (state == 0) {
      if (rest ~ /^enum[^A-Za-z0-9_]/) { state = 1; i += 4; continue }
      i++; continue
    }
    if (state == 1) {
      c = substr(txt, i, 1)
      if (c == "{") { state = 2; depth = 1; buf = ""; nm_i = 0; i++; continue }
      if (c == ";" || c == "(") { state = 0; i++; continue }
      i++; continue
    }
    c = substr(txt, i, 1)
    if (c == "{") depth++
    else if (c == "}") {
      depth--
      if (depth == 0) { take(file, lno, buf); emit(); buf = ""; state = 0; i++; continue }
    }
    if (c == "," && depth == 1) { take(file, lno, buf); buf = ""; i++; continue }
    buf = buf c; i++
  }
}
function take(f, l, b,   nm, val) {
  gsub(/^[ \t]+|[ \t]+$/, "", b); if (b == "") return
  if (!match(b, /^[A-Za-z_][A-Za-z0-9_]*/)) return
  nm = substr(b, RSTART, RLENGTH); val = ""
  if (match(b, /=[ \t]*\(?-?[0-9]+[uUlL]*\)?[ \t]*$/)) {
    val = substr(b, RSTART + 1); gsub(/[ \t()uUlL]/, "", val)
  } else if (b ~ /=/) { val = "X" }
  E_f[nm_i] = f; E_l[nm_i] = l; E_n[nm_i] = nm; E_v[nm_i] = val; nm_i++
}
function emit(   j, ordinal) {
  ordinal = 1
  for (j = 0; j < nm_i; j++) if (E_v[j] != "" && E_v[j] != (j "")) { ordinal = 0; break }
  if (!ordinal)
    for (j = 0; j < nm_i; j++)
      if (E_v[j] != "" && E_v[j] != "X")
        print E_f[j] ":" E_l[j] ":enum member " E_n[j] " = " E_v[j] "\t" E_n[j]
  nm_i = 0
}
AWKEOF

find "$ROOT_DIR/src" "$ROOT_DIR/cli" "$ROOT_DIR/lib" \
     \( -name '*.c' -o -name '*.h' \) -print0 2>/dev/null \
  | sort -z | xargs -0 awk -f "$TMP3/mask.awk" > "$TMP3/masked.txt"

# object-like `#define NAME <numeric literal>` (a leading `(` allowed, so
# `#define REG_SEL_ANY (-1)` and `#define ABLOCK_MIN (64 * 1024)` are seen)
grep -E ':[[:space:]]*#[[:space:]]*define[[:space:]]+[A-Za-z_][A-Za-z0-9_]*[[:space:]]+\(?-?[0-9]' \
    "$TMP3/masked.txt" \
  | sed -E 's@^(.*:[0-9]+:)[[:space:]]*#[[:space:]]*define[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]+@\1#define \2 @' \
  | awk -F: '{ nm = $0; sub(/^.*#define /, "", nm); sub(/ .*$/, "", nm); print $0 "\t" nm }' \
  > "$TMP3/scan.txt"
awk -f "$TMP3/enums.awk" "$TMP3/masked.txt" >> "$TMP3/scan.txt"

# The two allowlists. Every name here is argued in the comment block above.
LIMIT_ALLOWLIST="TRIE_MAX_RDEPTH
MAX_GROUPS
ABLOCK_MIN
PCREC_HASH64_MUL
LEGEND_MAX_STATES
LEGEND_MAX_EXAMPLE
VM_MAX_STRIDE
VM_FAST_TIER_BYTES
VM_FAST_TIER_MIN
VM_MRL_DYN_MAX
SELECT_MAX_ROUNDS
C_MEMCHR
C_BITMAP
C_VERIFY
C_ENTER
C_MISPRED
MATERIAL_NUM
MATERIAL_DEN"

NONLIMIT_ALLOWLIST="PREMUL_DEAD
REG_SEL_ANY
PCREC_DFA_DEAD
PCREC_RXT_WAVE_RESERVED
PCREC_ENGINE_DFA
PCREC_ENGINE_VM
PCREC_TUNE_MIN_SIZE
PCREC_TUNE_SIZE
PCREC_TUNE_BALANCED
PCREC_TUNE_SPEED
PCREC_TUNE_MAX_SPEED
PCREC_STEP_BUDGET_DEFAULT
PCREC_STEP_BUDGET_NONE
PCREC_WORK_BUDGET_DEFAULT
PCREC_WORK_BUDGET_NONE
PCREC_RXT_WAVE_BUILT
VM_NRUNG
SDR_NONE
SDR_NO_ANCHORED
SDR_NO_PREMUL
SDR_MAX
TRIE_ENABLED"

TABLE_NAMES="$NAMES"
SCANNED_NAMES="$(cut -f2 "$TMP3/scan.txt" | sort -u)"
nscan="$(grep -c . "$TMP3/scan.txt" || true)"

# --- 3a: every scanned constant is dispositioned ---------------------------
bad_hits=0
while IFS=$'\t' read -r site ident; do
    [ -z "$ident" ] && continue
    grep -qxF "$ident" <<< "$TABLE_NAMES" && continue
    grep -qxF "$ident" <<< "$LIMIT_ALLOWLIST" && continue
    grep -qxF "$ident" <<< "$NONLIMIT_ALLOWLIST" && continue
    bad "[code] $site -- '$ident' is a numeric constant outside limits.def and is on NEITHER allowlist. Make it a limits.def row, or add it to the LIMIT allowlist (a bound excluded by limits.h's own rule) or the NON-LIMIT allowlist (a sentinel, API enum value, schema version or cardinality) WITH ITS REASON"
    bad_hits=$((bad_hits + 1))
done < "$TMP3/scan.txt"
if [ "$bad_hits" -eq 0 ]; then
    ok "[code] all $nscan numeric #define/enum-member constants under src/, cli/ and lib/ are dispositioned — a limits.def row, the LIMIT allowlist, or the NON-LIMIT allowlist. The scan is NOT keyed on the constant's name (D107)"
fi

# --- 3b: the scan is not vacuous (K35) -------------------------------------
if [ "$nscan" -ge "$SCAN_FLOOR" ]; then
    ok "[code-floor] the scan reached $nscan constants, at or above its floor of $SCAN_FLOOR"
else
    bad "[code-floor] the scan reached only $nscan constant(s), below its floor of $SCAN_FLOOR — the masker or the enum walk has stopped matching, and an empty population classifies perfectly"
fi

# --- 3c: no allowlist entry the scan never reaches ([MECH-REACH]) ----------
unreached=""
while IFS= read -r a; do
    [ -z "$a" ] && continue
    grep -qxF "$a" <<< "$SCANNED_NAMES" || unreached="$unreached $a"
done <<< "$LIMIT_ALLOWLIST
$NONLIMIT_ALLOWLIST"
if [ -z "$unreached" ]; then
    ok "[code-reach] every one of the $(printf '%s\n%s\n' "$LIMIT_ALLOWLIST" "$NONLIMIT_ALLOWLIST" | grep -c .) allowlist names was actually reached by the scan — no entry is excusing a constant that is no longer there, and none is masking a site the scan stopped reaching"
else
    bad "[code-reach] allowlist name(s) the scan never reached:$unreached — either the constant is gone (drop the entry) or the scan no longer reaches its site (fix the scan, do not drop the entry)"
fi

echo
echo "== Summary =="
echo "checks passed: $npass"
echo "checks failed: $nfail"
[ "$nfail" -eq 0 ]
