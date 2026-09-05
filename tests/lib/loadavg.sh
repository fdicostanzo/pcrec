# tests/lib/loadavg.sh — [MACPORT] ONE implementation of "read the box's
# load average", the same single-implementation shape tests/lib/
# timeout_bin.sh established for TIMEOUT_BIN.
#
# WHY THIS EXISTS. `/proc/loadavg` is Linux-only; this project's other
# supported box (macOS/arm64) has no `/proc` at all. Every call site in the
# tree that reads it already degrades gracefully in ONE of two ways — a
# `2>/dev/null || echo 0` fallback (tests/size/run_size_log.sh,
# tests/lib/load_guard.sh) or an unguarded `read ... < /proc/loadavg`
# (tests/harness/run.sh's SIZELOG timing line) that would hard-error on a
# box with no such file — but "falls back to 0" throws away a real,
# available number on darwin (`sysctl -n vm.loadavg` reports it directly),
# and an unguarded read is simply a bug on this box. This file gives every
# such site a REAL reading on both platforms instead of a silent zero.
#
# load1 — the 1-minute load average, bare (e.g. "2.74").
# load3 — all three averages, space-separated, in `/proc/loadavg`'s own
#         "1min 5min 15min" order (e.g. "1.61 2.74 2.64") — the shape
#         scripts/battery.sh's trailer line and a few `uptime`-adjacent log
#         lines want.
# Both print "0"/"0 0 0" (never fail) if neither source is readable, so a
# box this project does not target degrades the same way the pre-existing
# `|| echo 0` call sites already did — a loud failure here would fail a
# build over a cosmetic log field, which is the wrong tradeoff.

_loadavg_darwin() {
    # macOS's own format: "{ 1.61 2.74 2.64 }" — strip the braces, awk
    # does the rest. `sysctl -n` alone (no `vm.loadavg` grep dance) is the
    # whole call; no subprocess chain to keep in sync with a format that
    # has not changed across any Darwin version this project has seen.
    sysctl -n vm.loadavg 2>/dev/null | tr -d '{}'
}

load1() {
    local raw
    if [ -r /proc/loadavg ]; then
        raw="$(cut -d' ' -f1 /proc/loadavg 2>/dev/null)"
    else
        raw="$(_loadavg_darwin | awk '{print $1}')"
    fi
    printf '%s' "${raw:-0}"
}

load3() {
    local raw
    if [ -r /proc/loadavg ]; then
        raw="$(cut -d' ' -f1-3 /proc/loadavg 2>/dev/null)"
    else
        raw="$(_loadavg_darwin | awk '{print $1, $2, $3}')"
    fi
    printf '%s' "${raw:-0 0 0}"
}
