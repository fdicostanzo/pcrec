#!/usr/bin/env bash
# statusline.sh — pcrec's project-local Claude Code status line.
#
# Reads the session JSON Claude Code pipes on stdin (documented at
# https://code.claude.com/docs/en/statusline) and does two jobs.
#
#   1. DISPLAY — one line:
#        🧠 Opus  ·  ⚡ high  ·  ctx 330k/400k (83%)  ·  5h 23% ⏳2h41m  ·  7d 41%  ·  main ↑2 *3  ·  q:210-alttri2-test
#      ctx = tokens in the context window against the owner's auto-compact
#      ceiling (~/.claude/settings.json `autoCompactWindow`, read-only, that one
#      key), else the input's own context_window figures. ctx and 5h recolor by
#      threshold (green <70, yellow 70-89, red 90+); ⏳ counts down to the 5h
#      reset. Tail: main ahead/behind origin and dirty count of this repo (git
#      only), and the box-queue running job (one token from scripts/boxqueue
#      status). Both tail tokens come from a short-TTL cache refreshed by a
#      detached job, so the render never waits on git or the queue.
#
#   2. SNAPSHOTS — on EVERY refresh, under $PCREC_TMPDIR/statusline/
#      (scripts/tmpdir.sh; default /var/tmp/pcrec-<user>), atomically
#      (temp + rename):
#        session-<session_id>.json  the full stdin JSON plus `captured_at`
#                                   (epoch seconds); session-local values
#        usage-latest.json          the account-wide rate_limits fields
#                                   (null when absent) plus session_id and
#                                   captured_at, written unconditionally so
#                                   staleness is diagnosable
#      session-*.json older than 7 days are pruned. Nothing is written under
#      ~/.claude. Consumers: scripts/gestalt.
#
# Configured by the PROJECT .claude/settings.json:
#   "statusLine": { "type": "command",
#                   "command": "\"$CLAUDE_PROJECT_DIR\"/scripts/statusline.sh",
#                   "refreshInterval": 30 }
# Env: PCREC_STATUSLINE_USER_SETTINGS overrides the settings file read for
# autoCompactWindow (self-test).
#
# NOTE: never `set -e` — a non-zero exit blanks the status line. We always
# print something and exit 0, degrading gracefully when fields are absent.

set -uo pipefail

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
. "$here/tmpdir.sh" 2>/dev/null
SNAP_DIR="${PCREC_TMPDIR:-/var/tmp/pcrec-$(id -un)}/statusline"
mkdir -p "$SNAP_DIR" 2>/dev/null || true

input=$(cat)
now=$(date +%s)

# --- One jq pass -> display fields, one value per line (empty lines kept so an
# empty effort does not shift the columns). Percentages floor to ints; -1 = absent.
F=()
while IFS= read -r _fl || [ -n "$_fl" ]; do F+=("$_fl"); done < <(
  printf '%s' "$input" | jq -r '
    (.model.display_name // "?"),
    (.effort.level // ""),
    (.context_window.used_percentage // 0 | floor),
    (if .rate_limits.five_hour.used_percentage != null
       then (.rate_limits.five_hour.used_percentage | floor) else -1 end),
    (.rate_limits.five_hour.resets_at // 0),
    (if .rate_limits.seven_day.used_percentage != null
       then (.rate_limits.seven_day.used_percentage | floor) else -1 end),
    (.session_id // ""),
    (.context_window.context_window_size // 0),
    ((.context_window.current_usage // null) as $u
       | if $u == null then -1
         else (($u.input_tokens // 0) + ($u.cache_creation_input_tokens // 0)
               + ($u.cache_read_input_tokens // 0)) end)
  ' 2>/dev/null
)
MODEL=${F[0]:-?}; EFFORT=${F[1]:-}; CTX=${F[2]:-0}
FIVE_PCT=${F[3]:--1}; FIVE_RESET=${F[4]:-0}; SEVEN_PCT=${F[5]:--1}
SID=${F[6]:-}; WIN=${F[7]:-0}; USED=${F[8]:--1}

# --- Snapshots (every refresh) ---
atomic_write() { # $1 = dest; content on stdin
  local tmp="$1.$$.tmp"
  if cat > "$tmp" 2>/dev/null; then mv -f "$tmp" "$1" 2>/dev/null || rm -f "$tmp" 2>/dev/null
  else rm -f "$tmp" 2>/dev/null; fi
}
case "$SID" in *[!A-Za-z0-9_-]*) SID="" ;; esac
if [ -n "$SID" ]; then
  printf '%s' "$input" | jq -c --argjson t "$now" '. + {captured_at: $t}' 2>/dev/null \
    | atomic_write "$SNAP_DIR/session-$SID.json"
fi
printf '%s' "$input" | jq -c --argjson t "$now" '{
    five_hour: (if .rate_limits.five_hour.used_percentage != null
                  then { used_percentage: .rate_limits.five_hour.used_percentage,
                         resets_at:       .rate_limits.five_hour.resets_at } else null end),
    seven_day: (if .rate_limits.seven_day.used_percentage != null
                  then { used_percentage: .rate_limits.seven_day.used_percentage,
                         resets_at:       .rate_limits.seven_day.resets_at } else null end),
    session_id:  (.session_id // null),
    captured_at: $t
  }' 2>/dev/null | atomic_write "$SNAP_DIR/usage-latest.json"
find "$SNAP_DIR" -maxdepth 1 -name 'session-*.json' -mtime +7 -delete 2>/dev/null || true

# --- Display helpers ---
RESET='\033[0m'; BOLD='\033[1m'; DIM='\033[2m'
YELLOW='\033[33m'; CYAN='\033[36m'
SEP="${DIM}  ·  ${RESET}"

color_for() { # $1 = pct (int) -> ANSI color by threshold
  if   [ "$1" -ge 90 ]; then printf '\033[31m'
  elif [ "$1" -ge 70 ]; then printf '\033[33m'
  else                       printf '\033[32m'
  fi
}

fmt_reset() { # $1 = reset epoch -> "2h41m" / "41m" / "" (absent/past)
  local r="$1" rem h m
  rem=$(( r - now ))
  if [ "$r" -le 0 ] || [ "$rem" -le 0 ]; then return; fi
  h=$(( rem / 3600 )); m=$(( (rem % 3600) / 60 ))
  if [ "$h" -gt 0 ]; then printf '%dh%02dm' "$h" "$m"; else printf '%dm' "$m"; fi
}

# --- ctx: tokens against the owner's auto-compact ceiling ---
USER_SETTINGS="${PCREC_STATUSLINE_USER_SETTINGS:-$HOME/.claude/settings.json}"
ACW=$(timeout 1 jq -r '.. | objects | .autoCompactWindow? // empty' "$USER_SETTINGS" 2>/dev/null | head -1)
case "$ACW" in ''|*[!0-9]*) ACW="" ;; esac
case "$WIN" in ''|*[!0-9]*) WIN=0 ;; esac
case "$USED" in ''|-|*[!0-9-]*) USED=-1 ;; esac
CEIL=${ACW:-$WIN}
CTX_TXT="${CTX}%"
if [ "$USED" -ge 0 ] && [ "${CEIL:-0}" -gt 0 ]; then
  CTX=$(( USED * 100 / CEIL )); [ "$CTX" -gt 100 ] && CTX=100
  CTX_TXT="$(( USED / 1000 ))k/$(( CEIL / 1000 ))k (${CTX}%)"
fi

# --- Tail: repo + queue state, cached (TTL 20 s), refreshed detached ---
main=$(dirname "$(git -C "$here" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)")
[ -d "$main/.git" ] || main=$(cd "$here/.." && pwd)
TAIL_CACHE="$SNAP_DIR/tail.cache"; TAIL_LOCK="$SNAP_DIR/tail.lock"
cmt=0; [ -f "$TAIL_CACHE" ] && cmt=$(stat -c %Y "$TAIL_CACHE" 2>/dev/null || echo 0)
lmt=0; [ -f "$TAIL_LOCK" ] && lmt=$(stat -c %Y "$TAIL_LOCK" 2>/dev/null || echo 0)
if [ $(( now - cmt )) -ge 20 ] && [ $(( now - lmt )) -ge 30 ]; then
  : > "$TAIL_LOCK" 2>/dev/null || true
  (
    ab=$(timeout 2 git -C "$main" rev-list --left-right --count main...origin/main 2>/dev/null)
    ahead=${ab%%[[:space:]]*}; behind=${ab##*[[:space:]]}
    dirty=$(timeout 2 git -C "$main" status --porcelain 2>/dev/null | grep -c .)
    job=$(timeout 1 bash "$here/boxqueue" status 2>/dev/null \
      | sed -n 's/^running: [^ ]*\/\([^/ ]*\) .*/\1/p' | head -1)
    printf '%s\t%s\t%s\t%s\n' "${ahead:-?}" "${behind:-?}" "${dirty:-0}" "$job" \
      | atomic_write "$TAIL_CACHE"
    rm -f "$TAIL_LOCK" 2>/dev/null
  ) >/dev/null 2>&1 </dev/null &
  disown 2>/dev/null || true
fi
TAIL=""
if [ -f "$TAIL_CACHE" ]; then
  IFS=$'\t' read -r T_AHEAD T_BEHIND T_DIRTY T_JOB < "$TAIL_CACHE"
  TAIL="main"
  [ "${T_AHEAD:-0}" != 0 ] && TAIL="${TAIL} ↑${T_AHEAD}"
  [ "${T_BEHIND:-0}" != 0 ] && TAIL="${TAIL} ↓${T_BEHIND}"
  if [ "${T_DIRTY:-0}" != 0 ]; then TAIL="${YELLOW}${TAIL} *${T_DIRTY}${RESET}"
  else TAIL="${CYAN}${TAIL}${RESET}"; fi
  [ -n "${T_JOB:-}" ] && TAIL="${TAIL}${SEP}${DIM}q:${T_JOB}${RESET}"
fi

# --- Compose the line ---
OUT="🧠 ${BOLD}${MODEL}${RESET}"
[ -n "$EFFORT" ] && OUT="${OUT}${SEP}⚡ ${EFFORT}"
OUT="${OUT}${SEP}ctx $(color_for "$CTX")${CTX_TXT}${RESET}"

if [ "$FIVE_PCT" -ge 0 ]; then
  OUT="${OUT}${SEP}5h $(color_for "$FIVE_PCT")${FIVE_PCT}%${RESET}"
  REM=$(fmt_reset "$FIVE_RESET")
  [ -n "$REM" ] && OUT="${OUT} ⏳${REM}"
else
  OUT="${OUT}${SEP}${DIM}5h --${RESET}"
fi
[ "$SEVEN_PCT" -ge 0 ] && OUT="${OUT}${SEP}7d $(color_for "$SEVEN_PCT")${SEVEN_PCT}%${RESET}"
[ -n "$TAIL" ] && OUT="${OUT}${SEP}${TAIL}"

printf '%b\n' "$OUT"
exit 0
