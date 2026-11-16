# tests/kitproof/loader.sh -- sourced by run_cover.sh and reach.sh: the ONE
# reading of a cases.tsv FLAGS/PATTERN pair ([COVER-CAP] stage 2,
# docs/design/cover_cap.md §11.6.2), so the check and the sabotage rows'
# REACH probe can never read a row two ways.
#
#   kp_limits PCREC   reads PCREC_DEFAULT_WINDOW_SEARCH_WIDTH (KP_D) and
#                     PCREC_ANCHORED_MAX_STATES (KP_CEIL) from `PCREC
#                     --list-limits` column 2 (the shipped literal). FAIL
#                     LOUD: returns 1 with KP_ERR set when a row is missing
#                     or not a bare decimal, never an empty substitution
#                     (`[0-9a-f]{}`) or `--window-search-width=-1` (K35).
#   kp_flags FLAGS    the pcrec arguments: i -> -i, u -> -e utf8,
#                     R -> -fno-rev-end, W -> --window-search-width=<KP_CEIL - 1>.
#   kp_pat PATTERN    the pattern with @LD1 / @LD (the first D + 1 / D
#                     letters of a..z, cyclic) and @D1 / @D (D + 1 / D)
#                     substituted, D = KP_D.
#   kp_width_verdict N   `cover` iff N <= KP_D, else `decline` (a verdict
#                     row's VALUE `width=N`).

kp_limits() {
    local tsv
    tsv="$("$1" --list-limits 2>/dev/null)" || { KP_ERR="$1 --list-limits failed"; return 1; }
    KP_D="$(awk -F'\t' '$1 == "PCREC_DEFAULT_WINDOW_SEARCH_WIDTH" { print $2 }' <<< "$tsv")"
    KP_CEIL="$(awk -F'\t' '$1 == "PCREC_ANCHORED_MAX_STATES" { print $2 }' <<< "$tsv")"
    case "$KP_D" in ''|*[!0-9]*) KP_ERR="--list-limits: PCREC_DEFAULT_WINDOW_SEARCH_WIDTH is '$KP_D', not a decimal"; return 1 ;; esac
    case "$KP_CEIL" in ''|*[!0-9]*) KP_ERR="--list-limits: PCREC_ANCHORED_MAX_STATES is '$KP_CEIL', not a decimal"; return 1 ;; esac
    [ "$KP_D" -ge 1 ] && [ "$KP_D" -lt "$KP_CEIL" ] || { KP_ERR="--list-limits: width $KP_D outside 1..$((KP_CEIL - 1))"; return 1; }
    return 0
}

kp_flags() {
    local a=""
    case "$1" in *i*) a="$a -i" ;; esac
    case "$1" in *u*) a="$a -e utf8" ;; esac
    case "$1" in *R*) a="$a -fno-rev-end" ;; esac
    case "$1" in *W*) a="$a --window-search-width=$((KP_CEIL - 1))" ;; esac
    echo "$a"
}

kp_letters() {   # N -> the first N letters of a..z, cyclic
    local n="$1" s="" abc="abcdefghijklmnopqrstuvwxyz"
    while [ "${#s}" -lt "$n" ]; do s="$s$abc"; done
    printf '%s' "${s:0:$n}"
}

kp_pat() {
    local p="$1"
    p="${p//@LD1/$(kp_letters $((KP_D + 1)))}"
    p="${p//@LD/$(kp_letters "$KP_D")}"
    p="${p//@D1/$((KP_D + 1))}"
    p="${p//@D/$KP_D}"
    printf '%s' "$p"
}

kp_width_verdict() {
    [ "$1" -le "$KP_D" ] && echo cover || echo decline
}
