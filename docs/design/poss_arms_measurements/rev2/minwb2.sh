#!/usr/bin/env bash
# minwb2.sh LABEL BINARY ENVSPEC PATTERN SUBJECTFILE [extra pcrec flags...]
# The minimum --work-budget at which the artifact ANSWERS (anything but the
# `work` give-up) on SUBJECTFILE, by bisection, `--engine=vm`, step budget at
# its default.  FAILS LOUDLY (exit 2) on a compile error or an unrecognised
# outcome -- B-M3: the rev-1 minwb.sh read a failed compile as an answer.
# (Outcomes go through a file, never `$(...)`: an `exit` inside a command
# substitution leaves only the subshell, which is how a loud failure goes quiet.)
# Prints: LABEL <TAB> min <TAB> outcome-at-min <TAB> outcome-at-min-1
set -u
lab="$1"; bin="$2"; envs="$3"; pat="$4"; subj="$(cat "$5")"; shift 5
extra=("$@")
W=$(mktemp -d "${TMPDIR:?}/minwb.XXXXXX"); trap 'rm -rf "$W"' EXIT
outcome() {  # budget -> $W/out holds the artifact's output line
    # shellcheck disable=SC2086
    if ! env $envs "$bin" -p rx --engine=vm --features all --work-budget="$1" \
            ${extra[@]+"${extra[@]}"} --emit-main -o "$W/m.c" --pattern "$pat" 2>"$W/e"; then
        echo "minwb2: pcrec failed at budget $1: $(head -1 "$W/e")" >&2; exit 2; fi
    gcc-16 -w -O1 -o "$W/m" "$W/m.c" 2>"$W/ce" || { echo "minwb2: gcc failed at budget $1" >&2; exit 2; }
    "$W/m" "$subj" > "$W/out"
    case "$(cat "$W/out")" in match*|"no match"|nomatch|work) ;;
        *) echo "minwb2: unrecognised outcome '$(cat "$W/out")' at budget $1" >&2; exit 2 ;; esac
}
lo=1; hi=1000000
outcome $hi; [ "$(cat "$W/out")" != work ] || { echo "minwb2: gives up WORK even at $hi" >&2; exit 2; }
while [ $lo -lt $hi ]; do
    mid=$(( (lo + hi) / 2 ))
    outcome $mid
    if [ "$(cat "$W/out")" = work ]; then lo=$((mid + 1)); else hi=$mid; fi
done
outcome $lo; at="$(cat "$W/out")"
if [ $lo -gt 1 ]; then outcome $((lo - 1)); below="$(cat "$W/out")"; else below="-"; fi
printf '%s\t%s\t%s\t%s\n' "$lab" "$lo" "$at" "$below"
