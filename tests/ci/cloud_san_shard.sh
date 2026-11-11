#!/usr/bin/env bash
# cloud_san_shard.sh TABLE K/N MAKE_TARGET -- one shard of a cloud sanitizer run ([CLOUD-SUITE] C): the scripts of
# shard K (tests/ci/cloud_san_shards.tsv) through the Makefile's locked sanitizer target (SAN_SCRIPTS overridden on
# its command line; the target builds its own instrumented tree and sets both axes' flags). The sanitizer runtimes
# come with the runner's gcc: probed first, and a missing one is a LOUD failure, never a green run that
# instrumented nothing. tests/ci/cloud_san_check.sh holds the shards' sum to tests/lib/san_scripts.txt.
set -u
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../.." && pwd)
tab=${1:?TABLE}; shard=${2:?K/N}; target=${3:?MAKE_TARGET}
case $tab in /*) ;; *) tab=$root/$tab ;; esac
scripts=$(bash "$here/cloud_table.sh" rows "$tab" "$shard" | tr '\n' ' ')
[ -n "${scripts// /}" ] || { echo "cloud_san_shard: shard $shard has NO scripts in $tab" >&2; exit 2; }
p=$(mktemp -d "${TMPDIR:-/var/tmp}/cloud_san.XXXXXX"); trap 'rm -rf "$p"' EXIT
echo 'int main(void) { return 0; }' > "$p/t.c"
gcc -fsanitize=address,undefined,leak "$p/t.c" -o "$p/t" && "$p/t" \
    || { echo "cloud_san_shard: FATAL: this runner's gcc cannot build and run a -fsanitize=address,undefined,leak program (runtimes missing)" >&2; exit 2; }
echo "cloud_san_shard: shard $shard, make $target, SAN_SCRIPTS=\"$scripts\""
exec make -C "$root" -j"$(nproc)" "$target" SAN_SCRIPTS="$scripts"
