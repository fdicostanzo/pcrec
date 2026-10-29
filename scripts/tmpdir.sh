# scripts/tmpdir.sh — the ONE definition of pcrec's temporary-file root.
#
# Why (Frank 2026-10-28): /tmp on the Linux dev box is a small RAM tmpfs with a
# per-user quota; killed mech runs and lane scratch filled it and a `make test`
# went red with gcc "Disk quota exceeded". /var/tmp is on the disk.
#
# PCREC_TMPDIR  the root; default /var/tmp/pcrec-<user> (per user, mode 0700,
#               created on first use). Override with PCREC_TMPDIR=...
# TMPDIR        forced to PCREC_TMPDIR for everything sourcing this file (a
#               caller's TMPDIR=/tmp does NOT win; the override is PCREC_TMPDIR).
#               The Makefile gets the same value via `sh scripts/tmpdir.sh
#               --print` and exports it to every recipe.
# scratch/<lane>/  lane scratch (docs/dev/lanes/BOILERPLATE.md).
#
# Sourced (POSIX sh, no bashisms) it sets and exports the two variables and
# defines pcrec_tmp_prune; executed with --print it prints the root (created);
# executed with --prune [DAYS] it runs the prune.
#
# PRUNE: removes entries older than PCREC_TMP_PRUNE_DAYS (UNMEASURED default 3
# days; nobody has measured how long a legitimate run keeps scratch) that hold
# no recent file and that no process has as cwd or open. Candidates are the
# root's direct children and, inside scratch/, its direct children. It touches
# nothing outside the root, and refuses an empty / relative / "/" root.

pcrec_tmp_root() {
    if [ -z "${PCREC_TMPDIR:-}" ]; then
        PCREC_TMPDIR=/var/tmp/pcrec-$(id -un)
    fi
    ( umask 077; mkdir -p "$PCREC_TMPDIR" ) 2>/dev/null
    export PCREC_TMPDIR
}

pcrec_tmp_prune() {
    _pp_root=${PCREC_TMPDIR:-}
    _pp_days=${1:-${PCREC_TMP_PRUNE_DAYS:-3}}    # UNMEASURED default
    case "$_pp_root" in /?*) ;; *) return 0 ;; esac
    [ "$_pp_root" != / ] && [ -d "$_pp_root" ] || return 0
    _pp_busy=$(mktemp "$_pp_root/.busy.XXXXXX") || return 0
    # every cwd / open file of every readable process
    # (find, not readlink: uutils readlink drops all but one operand)
    find /proc/[0-9]*/cwd /proc/[0-9]*/fd/ -maxdepth 1 -type l -printf '%l\n' 2>/dev/null > "$_pp_busy"
    for _pp_e in "$_pp_root"/* "$_pp_root"/scratch/*; do
        [ -e "$_pp_e" ] || continue
        [ "$_pp_e" = "$_pp_root/scratch" ] && continue
        case "$_pp_e" in "$_pp_root"/?*) ;; *) continue ;; esac
        [ -n "$(find "$_pp_e" -mtime "-$_pp_days" -print -quit 2>/dev/null)" ] && continue
        if awk -v p="$_pp_e" 'index($0, p) == 1 { c = substr($0, length(p) + 1, 1); if (c == "" || c == "/") { f = 1; exit } } END { exit !f }' "$_pp_busy"; then
            continue
        fi
        rm -rf -- "$_pp_e"
    done
    rm -f "$_pp_busy"
}

pcrec_tmp_root
TMPDIR=$PCREC_TMPDIR
export TMPDIR

case "${1:-}" in
    --print) [ "${0##*/}" = tmpdir.sh ] && echo "$PCREC_TMPDIR" ;;
    --prune) [ "${0##*/}" = tmpdir.sh ] && pcrec_tmp_prune "${2:-}" ;;
esac
