# tests/lib/assoc.sh — [MACPORT] a single-implementation, STRING-keyed
# associative-map shim, for the handful of `declare -A`-shaped maps in this
# tree whose keys are genuinely strings (filenames, feature-set text, C
# macro names, CLI flag spellings) rather than pcrec's more common
# numeric-PID pattern (scripts/safekill's own arrays are always PID/PGID-
# keyed and are fixed there by switching `declare -A` to `declare -a` under
# a bash-version guard instead — see that script's own comment; a real
# associative array is needless when every key is already a valid array
# subscript).
#
# WHY THIS EXISTS. This box's /bin/bash is 3.2.57 (macOS's last GPLv2
# release, 2007; no newer bash is installed, and installing one is outside
# this lane's mandate) and bash 3.2 has NO associative arrays at all —
# verified on this box: `declare -A x=()` errors "declare: -A: invalid
# option", and does not abort the script (no `set -e` anywhere in this
# tree), so execution continues with `x` never having been created and the
# first `x[$stringkey]=...` write either silently misbehaves (a numeric key
# auto-vivifies a normal INDEXED array, which is why scripts/safekill's
# always-numeric keys happen to survive unshimmed) or, under `set -u`
# (every file needing this shim has it), hard-crashes with "unbound
# variable" the moment a non-numeric subscript is evaluated in arithmetic
# context. tests/harness/run.sh — the harness nearly every suite in this
# tree runs through — has three such maps; requiring a bash upgrade for
# THIS file specifically would have meant no suite could run at all on this
# box pending that upgrade, so the shim exists to unblock validation now
# and is deliberately reusable rather than a one-off patch.
#
# API (NAME is always a bare literal identifier at the call site, never
# derived from untrusted input; KEY may be any string):
#   assoc_new  NAME           reset/declare NAME as an empty map
#   assoc_set  NAME KEY VAL
#   assoc_get  NAME KEY       echoes the value, or "" if absent (never fails)
#   assoc_has  NAME KEY       exit 0/1, no output
#   assoc_keys NAME           one key per line, in INSERTION order (not
#                             sorted — same non-guarantee bash's own `-A`
#                             iteration order carries)
#   assoc_count NAME          number of keys, printed with no trailing newline
#
# ON BASH 4+ (a normal Linux dev box, or a future upgraded darwin box):
# every call is a thin pass-through to a REAL global `declare -A` array
# named `__assoc_NAME` — the identical data structure the original inline
# `arr[$key]=val` syntax used, so a Linux run's behavior is unchanged bit
# for bit; the branch below is the only place that differs.
#
# ON BASH 3.2 (this box, today): each key is hex-encoded — `od -An -tx1`
# over the whole string in one shot, never a per-character loop and never
# an `eval` on unescaped caller text — into a scalar variable name
# `__assoc_NAME_v_kHEX`, plus a presence flag `__assoc_NAME_has_kHEX` (a
# scalar rather than bash's `${var+x}` unset-test on the value itself,
# since an explicitly-set-to-empty-string value must still count as
# present). A companion INDEXED array `__assoc_NAME_keys` (bash 3.2 has
# always supported plain indexed arrays — this project's whole `nproc`/
# `CC` resolver family already leans on that) records each ORIGINAL key
# once, in insertion order, the one thing the mangled scalars alone cannot
# answer.

if [ "${BASH_VERSINFO:-0}" -ge 4 ] 2>/dev/null; then
    _ASSOC_NATIVE=1
else
    _ASSOC_NATIVE=0
fi

# _assoc_mangle KEY — hex-encode KEY into a bash-identifier-safe suffix.
# `od`+`tr`, not a per-character loop: one pair of subprocess calls per key
# regardless of length, and no character-class branching to keep in sync
# with what a bash identifier actually allows.
_assoc_mangle() {
    local hex
    hex="$(od -An -tx1 <<<"$1" | tr -d ' \t\n')"
    printf 'k%s' "$hex"
}

assoc_new() {
    local name="$1"
    if [ "$_ASSOC_NATIVE" -eq 1 ]; then
        eval "declare -gA __assoc_$name=()"
    else
        eval "__assoc_${name}_keys=()"
    fi
}

assoc_set() {
    local name="$1" key="$2" val="$3"
    if [ "$_ASSOC_NATIVE" -eq 1 ]; then
        eval "__assoc_$name[\$key]=\$val"
    else
        local mk
        mk="$(_assoc_mangle "$key")"
        if ! eval "[ \"\${__assoc_${name}_has_$mk:-}\" = 1 ]"; then
            eval "__assoc_${name}_keys+=(\"\$key\")"
            eval "__assoc_${name}_has_$mk=1"
        fi
        eval "__assoc_${name}_v_$mk=\$val"
    fi
}

assoc_get() {
    local name="$1" key="$2"
    if [ "$_ASSOC_NATIVE" -eq 1 ]; then
        eval "printf '%s' \"\${__assoc_$name[\$key]:-}\""
    else
        local mk
        mk="$(_assoc_mangle "$key")"
        eval "printf '%s' \"\${__assoc_${name}_v_$mk:-}\""
    fi
}

assoc_has() {
    local name="$1" key="$2"
    if [ "$_ASSOC_NATIVE" -eq 1 ]; then
        eval "[ -n \"\${__assoc_$name[\$key]+x}\" ]"
    else
        local mk
        mk="$(_assoc_mangle "$key")"
        eval "[ \"\${__assoc_${name}_has_$mk:-}\" = 1 ]"
    fi
}

assoc_keys() {
    local name="$1"
    if [ "$_ASSOC_NATIVE" -eq 1 ]; then
        eval "printf '%s\n' \"\${!__assoc_$name[@]}\""
    else
        eval "printf '%s\n' \"\${__assoc_${name}_keys[@]}\""
    fi
}

assoc_count() {
    local name="$1"
    if [ "$_ASSOC_NATIVE" -eq 1 ]; then
        eval "printf '%s' \"\${#__assoc_$name[@]}\""
    else
        eval "printf '%s' \"\${#__assoc_${name}_keys[@]}\""
    fi
}
