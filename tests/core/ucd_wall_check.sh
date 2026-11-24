#!/usr/bin/env bash
# tests/core/ucd_wall_check.sh ROOT [WORKDIR] — [DATA-PLAN] A1 THE UCD WALL:
# exactly ONE module understands the Unicode tables' storage format
# (src/parse/ucd_tables.c, with its header's interface), and its WRITER
# (third_party/ucd-16.0.0/generate.py) is the only other file that may name
# the generated file or its symbols.  The owner's ruling (2026-11-24): "have it
# be modular so the format is only understood to the module which provides an
# interface".
#
# WHAT IT SCANS: every file `git ls-files -co --exclude-standard` lists (or,
# for the control's plant tree, `find`) except prose (*.md, docs/), the
# generated census output (tools/review/out/), and the allow-list below.  A
# file outside the allow-list that contains the generated file's name, any of
# its private symbols, or a symbol of the format it REPLACED is an offender.
# The Makefile is allowed the one line that makes the .inc a prerequisite; the
# mech sabotage rows for this check (S3575-S3579) must name what they plant,
# and S-U12's row anchors on the module's lookup line.
#
# CONTROL AND POPULATION: the scan is re-run on a plant tree (a copy of
# mod_uprops.c with the include planted) and must report it; and it must have
# READ more than 500 files, or it has stopped looking (K35).
set -u
export LC_ALL=C
ROOT="$1"
W="${2:-$(mktemp -d)}"
pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1"; fail=$((fail + 1)); }

# The needle, assembled from pieces so this file does not match itself.
a='ucd_tables''\.inc'
b='\bucd_(iv_blob|set_off|set_n|name_blob|row_name|row_ns|row_set|row_ci_set)\b'
c='UCD_GEN_'
d='pcrec_uprop_(iv|names)|PCREC_UPROP_NS_|uprops_tables''\.inc'
NEEDLE="$a|$b|$c|$d"

ALLOW='^(src/parse/ucd_tables\.(c|inc)|third_party/ucd-16\.0\.0/generate\.py|Makefile|tests/core/ucd_wall_check\.sh|tests/mech/sabotages/(S357[5-9]_.*|S-U12_bare_namespace_is_script\.sh))$'

# scan LISTFILE BASE: prints offender files; counts files read into $W/nread
scan() {
    local list="$1" base="$2" n=0 f
    while IFS= read -r f; do
        case "$f" in *.md|docs/*|tools/review/out/*|build*/*|worktrees/*) continue;; esac
        printf '%s\n' "$f" | grep -Eq "$ALLOW" && continue
        [ -f "$base/$f" ] || continue
        n=$((n + 1))
        grep -Eq "$NEEDLE" "$base/$f" 2>/dev/null && echo "$f"
    done < "$list"
    echo "$n" > "$W/nread"
}

mkdir -p "$W"
if git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1; then
    git -C "$ROOT" ls-files -co --exclude-standard > "$W/list"
else
    (cd "$ROOT" && find . -type f | sed 's|^\./||') > "$W/list"
fi
off="$(scan "$W/list" "$ROOT")"
nread="$(cat "$W/nread")"
if [ "$nread" -lt 500 ]; then
    bad "ucd wall: only $nread files read — the scan has stopped looking (K35)"
elif [ -n "$off" ]; then
    bad "ucd wall: files outside the module name the table's file or symbols: $(echo "$off" | tr '\n' ' ')"
else
    ok "ucd wall: $nread files read, none outside src/parse/ucd_tables.c + its generator names the generated file or its symbols"
fi

# the module itself must still be the one reader (else the wall guards nothing)
if grep -q 'include "ucd_tables.inc"' "$ROOT/src/parse/ucd_tables.c"; then
    ok "ucd wall: src/parse/ucd_tables.c includes the generated file"
else
    bad "ucd wall: src/parse/ucd_tables.c no longer includes ucd_tables.inc — the module is not the reader"
fi

# the control: a planted include in another parse file must be reported
mkdir -p "$W/plant/src/parse"
sed 's|^#include "ucd_tables.h".*|#include "ucd_tables.inc"|' \
    "$ROOT/src/parse/mod_uprops.c" > "$W/plant/src/parse/mod_uprops.c"
echo "src/parse/mod_uprops.c" > "$W/plant.list"
if [ "$(scan "$W/plant.list" "$W/plant")" = "src/parse/mod_uprops.c" ]; then
    ok "ucd wall control: a planted include of the generated file is reported"
else
    bad "ucd wall control: a planted include of the generated file was NOT reported — the scan cannot fail"
fi
echo "ucd_wall_check: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
