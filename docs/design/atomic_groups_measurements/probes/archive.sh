#!/bin/sh
# [M6.4.1] Run one probe and archive its output with FULL PROVENANCE.
#
# Every file in ../out/ is written by this script, so the header shape cannot
# drift between them and no archived number can be read without knowing which
# probe, which commit, and which oracle versions produced it. Same intent as
# scripts/measure.sh / docs/measurements/ (D35), scoped to this lane.
#
# Usage: archive.sh OUTNAME PROBE_PATH_RELATIVE_TO_REPO [args...]
#   e.g. archive.sh atomic_semantics.txt docs/design/atomic_groups_measurements/probes/probe_atomic_semantics.py
set -e
OUT=$1; PROBE=$2; shift 2

REPO=$(git rev-parse --show-toplevel)
DEST="$REPO/docs/design/atomic_groups_measurements/out/$OUT"
cd "$REPO"

PCRE2V=$(cd docs/design/eng_brep_measurements/probes 2>/dev/null && python3 -c "
import importlib.util
s = importlib.util.spec_from_file_location('p', 'pcre2_ctypes.py')
m = importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.version())
" 2>/dev/null || echo "not loaded by this probe")

{
  echo "# ============================================================"
  echo "# ARCHIVED PROBE OUTPUT — [M6.4.1] module \`atomic-groups\` design lane"
  echo "# ------------------------------------------------------------"
  echo "# PROBE      : $PROBE"
  echo "# ARGS       : ${*:-(none)}"
  echo "# PROBE LAST CHANGED AT COMMIT: $(git log -1 --format='%h %ad' --date=short -- "$PROBE" 2>/dev/null || echo 'uncommitted')"
  echo "# RUN FROM REPO COMMIT        : $(git rev-parse --short HEAD) ($(git rev-parse --abbrev-ref HEAD))"
  echo "#   working tree at run time  : $(test -z "$(git status --porcelain)" && echo clean || echo 'DIRTY — see below')"
  test -z "$(git status --porcelain)" || git status --porcelain | sed 's/^/#     /'
  echo "# RUN DATE   : $(date -Is)"
  echo "# python3    : $(python3 -V 2>&1 | sed 's/^Python //')"
  echo "# libpcre2   : $PCRE2V"
  echo "# gcc        : $(gcc -dumpversion)"
  echo "# host       : $(uname -sr)"
  echo "# ------------------------------------------------------------"
  echo "# Evidence for the [M6.4.1] panel, never an oracle: no check reads this"
  echo "# file. Re-run the probe to re-measure."
  echo "# ============================================================"
  echo
  case "$PROBE" in
    *.py) python3 "$PROBE" "$@" 2>&1 ;;
    *.sh) sh "$PROBE" "$@" 2>&1 ;;
    *)    "$PROBE" "$@" 2>&1 ;;
  esac
} > "$DEST"
echo "wrote $DEST ($(wc -l < "$DEST") lines)"
