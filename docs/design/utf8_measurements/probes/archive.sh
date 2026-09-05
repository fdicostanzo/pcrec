#!/bin/sh
# [M5.0] Run one probe and archive its output with FULL PROVENANCE.
#
# Every file in ../out/ is written by this script — the rule
# docs/design/assertions_measurements/ learned the hard way (R30 finding M7: a
# header HAND-WRITTEN to imitate the archiver is "worse than absent
# provenance", because a reader cannot tell stamped from asserted without git
# archaeology). Same intent as scripts/measure.sh / docs/measurements/ (D35),
# scoped to this lane.
#
# THIS LANE'S ADDITION TO THE HOUSE HEADER IS THE **ORACLE HOST**, and it is
# not decoration. The project's reference libpcre2 is 10.46 and it is on the
# OLD BOX; this Mac carries a different one and they are known to diverge. So
# an archived UTF number is meaningless without knowing which machine's
# library produced it, and this script puts that in the header rather than
# trusting a probe to say so.
#
# Usage:
#   archive.sh OUT.txt PROBE.py [--local] [args...]
#
#   Default is REMOTE: the probe is bundled (bundle.py) and piped into
#   `ssh <OLD BOX> python3 -`, so it executes against libpcre2 10.46 and
#   NOTHING IS WRITTEN on that machine. --local runs it here instead, which
#   is how the deliberate version-comparison rows are produced; the header
#   says which, and the probe's own `libpcre2:` line (printed by
#   u8_oracle.header) says which library actually answered.
#
#   A .sh probe is always local: those measure pcrec, which is built here.
set -e
OUT=$1; PROBE=$2; shift 2

MODE=remote
case "$1" in --local) MODE=local; shift ;; esac
case "$PROBE" in *.sh) MODE=local ;; esac

OLDBOX=duxevents@192.168.1.100
REPO=$(git rev-parse --show-toplevel)
DEST="$REPO/docs/design/utf8_measurements/out/$OUT"
PROBES="docs/design/utf8_measurements/probes"
cd "$REPO"

# The timeout binary: this box's bare `timeout` IS GNU coreutils 9.11
# (verified at lane start -- unlike the old box, whose CLAUDE.md row about
# uutils `timeout` does not apply here). Every probe is bounded.
TO="timeout 600"

{
  echo "# ============================================================"
  echo "# ARCHIVED PROBE OUTPUT — [M5.0] UTF-8 design lane"
  echo "# ------------------------------------------------------------"
  echo "# PROBE      : $PROBES/$(basename "$PROBE")"
  echo "# ARGS       : ${*:-(none)}"
  echo "# RUN MODE   : $MODE"
  if [ "$MODE" = remote ]; then
    echo "# ORACLE HOST: $OLDBOX (the REFERENCE libpcre2 10.46)"
    echo "#   mechanism : bundle.py | ssh ... 'python3 -' — the program"
    echo "#               arrives on stdin; nothing is written on that box."
  else
    echo "# ORACLE HOST: this machine ($(uname -sm))"
    echo "#   NOTE      : this is NOT the reference oracle unless the"
    echo "#               libpcre2 line below reads 10.46. A local run is a"
    echo "#               deliberate version COMPARISON, or a pcrec probe."
  fi
  # r54 meas-3: THE `|| echo uncommitted` FALLBACK NEVER FIRED. `git log` on a
  # path that has never been tracked EXITS 0 with EMPTY stdout — it is not an
  # error to ask about a path with no history — so `||` tested the wrong
  # thing and the field came out BLANK on every transcript archived before the
  # probes were committed (see out/sizing.txt's first archive). A blank field
  # reads as a formatting glitch; "uncommitted" reads as the fact it is. The
  # test has to be on EMPTINESS, not on exit status. (R30 M7's rule one turn
  # further: a provenance line that can go silently blank is the same defect
  # as a hand-written one.)
  PROBE_COMMIT=$(git log -1 --format='%h %ad' --date=short -- "$PROBES/$(basename "$PROBE")" 2>/dev/null)
  echo "# PROBE LAST CHANGED AT COMMIT: ${PROBE_COMMIT:-UNCOMMITTED (this probe is not tracked at the run commit below — the transcript pins nothing)}"
  echo "# RUN FROM REPO COMMIT        : $(git rev-parse --short HEAD) ($(git rev-parse --abbrev-ref HEAD))"
  echo "#   working tree at run time  : $(test -z "$(git status --porcelain)" && echo clean || echo 'DIRTY — see below')"
  test -z "$(git status --porcelain)" || git status --porcelain | sed 's/^/#     /'
  # `date -Is` is GNU-only and this box's `date` is BSD (it fails with
  # "invalid argument 's' for -I"). Spelled out so the header is identical on
  # either platform rather than empty on one of them.
  echo "# RUN DATE   : $(date +%Y-%m-%dT%H:%M:%S%z)"
  echo "# local python3 : $(python3 -V 2>&1 | sed 's/^Python //')  (the BUNDLER's)"
  echo "# local gcc     : $(gcc-16 -dumpversion 2>/dev/null || echo n/a)"
  echo "# local host    : $(uname -sr)"
  echo "# ------------------------------------------------------------"
  echo "# The probe's own header below states the python3, the libpcre2 and"
  echo "# the host that actually ANSWERED — read those, not these, for any"
  echo "# oracle claim. These name the machine that LAUNCHED the run."
  echo "#"
  echo "# Evidence for the [M5.0] panel, never an oracle: no check reads this"
  echo "# file. Re-run the probe to re-measure."
  echo "# ============================================================"
  echo
  case "$MODE:$PROBE" in
    local:*.py) $TO python3 "$PROBES/$(basename "$PROBE")" "$@" 2>&1 ;;
    local:*.sh) $TO sh "$PROBES/$(basename "$PROBE")" "$@" 2>&1 ;;
    remote:*)   $TO sh -c "python3 '$PROBES/bundle.py' '$(basename "$PROBE")' $* | ssh -o ConnectTimeout=10 -o BatchMode=yes $OLDBOX 'python3 -'" 2>&1 ;;
  esac
} > "$DEST"
echo "wrote $DEST ($(wc -l < "$DEST") lines)"
