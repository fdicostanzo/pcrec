#!/usr/bin/env bash
# tests/memfn/run_link_checks.sh — [MEMFN] R4a: C15 and C16, the two checks
# born with the kit's link into libpcrec (docs/design/memfn/integration.md
# §20.3). `make test-memfn-link`; a `make test` section.
#
# C15 — libpcrec exports only `pcrec_` names. The kit is linked INTO
#   libpcrec.a, so its symbols ship inside every program that links pcrec;
#   an unprefixed `mf_emit` there is a symbol a user's program may already
#   define. Every global defined symbol of the archive must begin `pcrec_`
#   (the kit's are `pcrec_mf_*`, through MF_NS), save the allowlist
#   (tests/memfn/c15_allowlist.txt), born EMPTY: the archive measured 0
#   exceptions at the build commit (457 globals, 26 of them the kit's).
#
#   Its controls, each sharing no source with what it checks:
#   - the symbols come from `nm` over the BUILT archive, never from source;
#   - a PROBE archive compiled here, holding one `pcrec_` symbol and one
#     planted unprefixed one, must yield exactly the planted one (the
#     sabotage witness, run every time, which also learns this platform's
#     symbol decoration: Mach-O's leading `_`);
#   - the population is counted and floored (K35): an `nm` that silently
#     read nothing would otherwise pass. FLOOR 200, under half the 457
#     measured: it answers "did extraction break", not "the right ones";
#   - REACH: the kit's own entry `pcrec_mf_options` (the one pcrec calls)
#     must be among them, or C15 is not looking at an archive with the kit;
#   - every allowlist entry must still be exported (an exception that
#     stopped being reached is a filter that quietly stopped matching).
#
# C16 — every kit file whose text can reach an artifact carries an SPDX
#   line with an id from D145's list and a provenance header, and
#   memfn/PROVENANCE.md tabulates it. Scope: every file under memfn/include
#   and memfn/src, by `find` (a CLAUDE.md excepted), a superset of "can
#   reach an artifact" on purpose. D145's list is spelled HERE, from
#   docs/dev/decisions.md D145 (0BSD, Unlicense, CC0-1.0), sharing no source
#   with the files or the table.
#
#   Its controls:
#   - the file headers and PROVENANCE.md are two hand-written sources that
#     must agree, both directions (a file with no row, a row with no file)
#     and on the licence;
#   - a SYNTHETIC kit dir built here plants each defect once (no SPDX, an
#     MIT SPDX, no Provenance line, a file with no row, a row with no file,
#     a licence that disagrees with its row) and must be flagged for exactly
#     those six;
#   - the population is counted and floored at 1 (K35).
#
# What neither sees: C15 reads one archive, build/libpcrec.a (LIB=
# overrides), not a shared library or a sanitizer tree's copy; C16 reads
# headers by line shape, so an SPDX id spelled inside a comment's prose on
# line 1 would pass.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck source=../lib/cc_resolve.sh
. "$ROOT_DIR/tests/lib/cc_resolve.sh"
LIB="${LIB:-$ROOT_DIR/build/libpcrec.a}"
KITDIR="${KITDIR:-$ROOT_DIR/memfn}"
ALLOW="$ROOT_DIR/tests/memfn/c15_allowlist.txt"
NM="${NM:-nm}"
C15_FLOOR=200
D145_IDS="0BSD Unlicense CC0-1.0"

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-memfn-link.XXXXXX")"
trap 'rm -rf "$WORKDIR"' EXIT
pass=0; fail=0
ok()  { echo "PASS: $*"; pass=$((pass + 1)); }
bad() { echo "FAIL: $*"; fail=$((fail + 1)); }
finish() {
    echo
    echo "checks passed: $pass"
    echo "checks failed: $fail"
    [ "$fail" -eq 0 ]
    exit $?
}

# ---- C15 ------------------------------------------------------------------

# Every global DEFINED symbol of archive $1, with the platform decoration
# $2 (the leading `_` or nothing) removed, one per line, sorted.
c15_globals() {
    "$NM" -g --defined-only "$1" 2>"$WORKDIR/nm.err" \
        | awk -v dec="$2" 'NF >= 3 { s = $3; if (dec != "" && index(s, dec) == 1) s = substr(s, length(dec) + 1); print s }' \
        | LC_ALL=C sort -u
}

echo "== C15: libpcrec exports only pcrec_ names =="
# The probe: one prefixed symbol, one planted unprefixed one.
cat > "$WORKDIR/probe.c" <<'EOF'
int pcrec_c15_probe_ok(void) { return 1; }
int c15_probe_planted(void) { return 2; }
EOF
"$CC" -c -o "$WORKDIR/probe.o" "$WORKDIR/probe.c"
ar rcs "$WORKDIR/probe.a" "$WORKDIR/probe.o"
raw="$("$NM" -g --defined-only "$WORKDIR/probe.a" | awk 'NF >= 3 { print $3 }')"
if printf '%s\n' "$raw" | grep -qx '_pcrec_c15_probe_ok'; then
    DEC="_"
elif printf '%s\n' "$raw" | grep -qx 'pcrec_c15_probe_ok'; then
    DEC=""
else
    bad "[C15 probe] $NM did not list the probe's own symbol pcrec_c15_probe_ok -- the extractor cannot see a symbol it was handed; nothing below would mean anything"
    finish
fi
probe_bad="$(c15_globals "$WORKDIR/probe.a" "$DEC" | grep -v '^pcrec_' || true)"
if [ "$probe_bad" = "c15_probe_planted" ]; then
    ok "[C15 witness] the probe archive's planted unprefixed symbol is the one flagged (decoration '${DEC}')"
else
    bad "[C15 witness] expected exactly c15_probe_planted flagged in the probe archive, got: '${probe_bad}'"
fi

if [ ! -f "$LIB" ]; then
    bad "[C15] $LIB is not built"
    finish
fi
c15_globals "$LIB" "$DEC" > "$WORKDIR/globals"
nglob="$(wc -l < "$WORKDIR/globals" | tr -d ' ')"
nkit="$(grep -c '^pcrec_mf_' "$WORKDIR/globals" || true)"
if [ "$nglob" -lt "$C15_FLOOR" ]; then
    bad "[C15 population] $nglob global defined symbols in $LIB, under the floor $C15_FLOOR -- nm read less than the archive holds ($(head -2 "$WORKDIR/nm.err"))"
else
    ok "[C15 population] $nglob global defined symbols in $LIB ($nkit of them the kit's pcrec_mf_*), floor $C15_FLOOR"
fi
if grep -qx 'pcrec_mf_options' "$WORKDIR/globals"; then
    ok "[C15 reach] the kit is in the archive (pcrec_mf_options, the entry --list-axes calls)"
else
    bad "[C15 reach] pcrec_mf_options is not exported by $LIB -- the archive does not carry the kit, so C15 says nothing about it"
fi

grep -v '^[[:space:]]*\(#\|$\)' "$ALLOW" > "$WORKDIR/allow" || true
nallow="$(wc -l < "$WORKDIR/allow" | tr -d ' ')"
offenders="$(grep -v '^pcrec_' "$WORKDIR/globals" | LC_ALL=C comm -23 - <(LC_ALL=C sort -u "$WORKDIR/allow") || true)"
if [ -z "$offenders" ]; then
    ok "[C15] every global defined symbol of $LIB begins pcrec_ ($nallow allowlisted exception(s))"
else
    bad "[C15] $LIB exports symbol(s) without the pcrec_ prefix -- a kit symbol not spelled through MF_NS, or a pcrec symbol not prefixed: $(printf '%s ' $offenders)"
fi
stale="$(LC_ALL=C sort -u "$WORKDIR/allow" | LC_ALL=C comm -23 - "$WORKDIR/globals" || true)"
if [ -z "$stale" ]; then
    ok "[C15 allowlist] every allowlist entry is still exported ($nallow entries)"
else
    bad "[C15 allowlist] allowlisted symbol(s) no longer exported -- delete them from $ALLOW: $(printf '%s ' $stale)"
fi

# ---- C16 ------------------------------------------------------------------

# Prints one line per C16 offense for kit dir $1 against table $2.
c16_scan() {
    local kit="$1" table="$2" f rel id lic
    find "$kit/include" "$kit/src" -type f ! -name CLAUDE.md 2>/dev/null \
        | sed "s|^$kit/||" | LC_ALL=C sort > "$WORKDIR/c16_files"
    awk -F'|' '/^\| *`/ { f = $2; gsub(/[ `]/, "", f); l = $4; gsub(/ /, "", l); print f "\t" l }' \
        "$table" | LC_ALL=C sort > "$WORKDIR/c16_rows"
    while IFS= read -r rel; do
        f="$kit/$rel"
        id="$(head -5 "$f" | sed -n 's/.*SPDX-License-Identifier: *\([A-Za-z0-9.+-]*\).*/\1/p' | head -1)"
        if [ -z "$id" ]; then
            echo "$rel: no SPDX-License-Identifier line in its first 5 lines"
        elif ! printf ' %s ' "$D145_IDS" | grep -q " $id "; then
            echo "$rel: SPDX id '$id' is not on D145's list ($D145_IDS)"
        fi
        head -10 "$f" | grep -q 'Provenance:' \
            || echo "$rel: no 'Provenance:' line in its first 10 lines"
        lic="$(awk -F'\t' -v r="$rel" '$1 == r { print $2 }' "$WORKDIR/c16_rows")"
        if [ -z "$lic" ]; then
            echo "$rel: no row in PROVENANCE.md"
        elif [ -n "$id" ] && [ "$lic" != "$id" ]; then
            echo "$rel: PROVENANCE.md says '$lic', the file says '$id'"
        fi
    done < "$WORKDIR/c16_files"
    cut -f1 "$WORKDIR/c16_rows" | LC_ALL=C comm -23 - "$WORKDIR/c16_files" \
        | sed 's/$/: a PROVENANCE.md row names a file that does not exist/'
}

echo
echo "== C16: every kit source file carries a D145 SPDX id and its provenance =="
# The witness: a synthetic kit with each defect planted once.
SYN="$WORKDIR/syn"
mkdir -p "$SYN/include" "$SYN/src"
printf '/* SPDX-License-Identifier: 0BSD\n * Provenance: original\n */\n' > "$SYN/include/good.h"
printf '/* no licence line\n * Provenance: original\n */\n' > "$SYN/src/nospdx.c"
printf '/* SPDX-License-Identifier: MIT\n * Provenance: original\n */\n' > "$SYN/src/mit.c"
printf '/* SPDX-License-Identifier: 0BSD\n */\n' > "$SYN/src/noprov.c"
printf '/* SPDX-License-Identifier: 0BSD\n * Provenance: original\n */\n' > "$SYN/src/norow.c"
printf '/* SPDX-License-Identifier: Unlicense\n * Provenance: memchr\n */\n' > "$SYN/src/disagree.c"
cat > "$SYN/PROVENANCE.md" <<'EOF'
| file | source | licence | what derives from it |
|---|---|---|---|
| `include/good.h` | original | 0BSD | x |
| `src/nospdx.c` | original | 0BSD | x |
| `src/mit.c` | original | 0BSD | x |
| `src/noprov.c` | original | 0BSD | x |
| `src/disagree.c` | original | 0BSD | x |
| `src/gone.c` | original | 0BSD | x |
EOF
syn_out="$(c16_scan "$SYN" "$SYN/PROVENANCE.md")"
# Flagged files, one line per offense: mit.c twice (off D145's list AND off
# its row), the other five once, good.h never.
got="$(printf '%s\n' "$syn_out" | cut -d: -f1 | LC_ALL=C sort | tr '\n' ' ')"
want="src/disagree.c src/gone.c src/mit.c src/mit.c src/noprov.c src/norow.c src/nospdx.c "
if [ "$got" = "$want" ]; then
    ok "[C16 witness] the synthetic kit's six planted defects are flagged (mit.c twice: off D145's list and off its row) and its clean file is not"
else
    bad "[C16 witness] the synthetic kit was not flagged as planted (want: $want). Got:"
    printf '%s\n' "$syn_out" | sed 's/^/    /'
fi

out="$(c16_scan "$KITDIR" "$KITDIR/PROVENANCE.md")"
nfiles="$(wc -l < "$WORKDIR/c16_files" | tr -d ' ')"
if [ "$nfiles" -lt 1 ]; then
    bad "[C16 population] no files found under $KITDIR/include or $KITDIR/src -- nothing was checked"
else
    ok "[C16 population] $nfiles kit file(s) in scope under $KITDIR/include and $KITDIR/src"
fi
if [ -z "$out" ]; then
    ok "[C16] every kit file carries a D145 SPDX id and a Provenance line, and PROVENANCE.md agrees file for file ($nfiles rows)"
else
    bad "[C16] kit provenance defects:"
    printf '%s\n' "$out" | sed 's/^/    /'
fi

finish
