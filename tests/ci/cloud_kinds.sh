#!/usr/bin/env bash
# cloud_kinds.sh -- reads tests/ci/cloud_kinds.tsv, the ONE declared table of cloud-run kinds ([CLOUD-SUITE] B).
# The workflow's plan job, scripts/cloudrun and tests/ci/cloud_gather.sh all go through here; none names a kind.
#
#   cloud_kinds.sh kinds                  the declared kinds, one per line
#   cloud_kinds.sh suite-kinds            the kinds whose `suite` column is 1, one per line (scripts/cloudrun --suite)
#   cloud_kinds.sh get KIND FIELD         one field of a kind's row (exit 2: undefined kind or field)
#   cloud_kinds.sh shards KIND            "1/N 2/N .. N/N" (N from the shards column; `table` = selector's `# shards=`)
#   cloud_kinds.sh command KIND K/N       the shard command with {shard}, {selector} and {rows} filled in. {rows} = the
#                                         comma-separated ids a run was NAMED over: the part after `rows.` of the branch's
#                                         NAME (scripts/cloudrun --rows spells it `NAME.rows.ID_ID_..`), read from
#                                         $CLOUD_BRANCH or, on a runner, $GITHUB_REF_NAME; empty if the name has none
#   cloud_kinds.sh takes-rows KIND        exit 0 if the kind's command has a {rows} placeholder (what --rows is allowed on)
#   cloud_kinds.sh owner-ok KIND OWNER    exit 0 if OWNER may start KIND, else 2
#   cloud_kinds.sh population KIND       the kind's population-check command, {selector} filled in ({sections} left for the caller)
#   cloud_kinds.sh plan KIND OWNER        key=value lines for the plan job: shards, matrix (JSON), max_parallel,
#                                         limit_min, needs; exit 2 (message on stderr) for an undefined kind or a
#                                         refused owner
# KINDS_TSV overrides the table path (the tests plant a copy); ROOT overrides the tree the selector is read from.
set -u
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
root=${ROOT:-$(cd "$here/../.." && pwd)}
tsv=${KINDS_TSV:-$here/cloud_kinds.tsv}
cols="kind command selector shards max_parallel limit_min needs owners population measured reweight_margin setup_s reweigh suite"

die() { echo "cloud_kinds: $*" >&2; exit 2; }
row() { awk -F'\t' -v k="$1" '/^#/ || $1 == "kind" {next} $1 == k {print; found=1; exit} END {exit !found}' "$tsv"; }
field() { # KIND FIELD
    local i=0 c n=0
    for c in $cols; do i=$((i+1)); [ "$c" = "$2" ] && n=$i; done
    [ "$n" -gt 0 ] || die "no field '$2' (fields: $cols)"
    row "$1" | awk -F'\t' -v n="$n" '{print $n}' || return 1
}
need_kind() { row "$1" >/dev/null || die "kind '$1' is not declared in $(basename "$tsv") (declared: $(cmd_kinds | tr '\n' ' '))"; }
cmd_kinds() { awk -F'\t' '/^#/ || $1 == "kind" || !NF {next} {print $1}' "$tsv"; }
cmd_shards() {
    local n sel i out=""
    n=$(field "$1" shards); sel=$(field "$1" selector)
    if [ "$n" = table ]; then
        n=$(sed -n 's/^# shards=//p' "$root/$sel" 2>/dev/null | head -1)
        case $n in ''|*[!0-9]*) die "no '# shards=N' line in $sel" ;; esac
    fi
    case $n in ''|*[!0-9]*|0) die "kind '$1': shard count '$n' is not a positive integer" ;; esac
    i=1; while [ "$i" -le "$n" ]; do out="$out${out:+ }$i/$n"; i=$((i+1)); done; echo "$out"
}
cmd_owner_ok() {
    local o; o=$(field "$1" owners)
    [ "$o" = '*' ] && return 0
    case ",$o," in *",$2,"*) return 0 ;; esac
    return 2
}

case "${1:-}" in
kinds) cmd_kinds ;;
suite-kinds) for k in $(cmd_kinds); do [ "$(field "$k" suite)" = 1 ] && echo "$k"; done ;;
get) [ $# -eq 3 ] || die "usage: get KIND FIELD"; need_kind "$2"; field "$2" "$3" ;;
shards) need_kind "${2:-}"; cmd_shards "$2" ;;
command) need_kind "${2:-}"; c=$(field "$2" command); s=$(field "$2" selector)
    br=${CLOUD_BRANCH:-${GITHUB_REF_NAME:-}}; rw=""
    case $br in cloud/*/*/*.rows.*|cloud/*/*/rows.*) rw=$(printf '%s' "${br##*rows.}" | tr '_' ',' | tr -c 'A-Za-z0-9,\n-' '?') ;; esac
    c=${c//\{selector\}/$s}; c=${c//\{rows\}/$rw}; echo "${c//\{shard\}/${3:?shard K/N}}" ;;
takes-rows) need_kind "${2:-}"; case $(field "$2" command) in *'{rows}'*) exit 0 ;; *) exit 2 ;; esac ;;
population) need_kind "${2:-}"; c=$(field "$2" population); echo "${c//\{selector\}/$(field "$2" selector)}" ;;
owner-ok) need_kind "${2:-}"; cmd_owner_ok "$2" "${3:-}" ;;
plan) need_kind "${2:-}"
    cmd_owner_ok "$2" "${3:-}" || die "owner '${3:-}' may not start kind '$2' (owners: $(field "$2" owners))"
    sh=$(cmd_shards "$2") || exit 2
    echo "shards=$sh"
    echo "matrix=$(printf '"%s",' $sh | sed 's/^/[/; s/,$/]/')"
    echo "max_parallel=$(field "$2" max_parallel)"
    echo "limit_min=$(field "$2" limit_min)"
    echo "needs=$(field "$2" needs)" ;;
*) sed -n '2,/^set -u/p' "$0" | sed '$d; s/^# \{0,1\}//'; exit 64 ;;
esac
