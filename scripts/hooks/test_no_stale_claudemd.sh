#!/usr/bin/env bash
# Test for no_stale_claudemd.sh: feeds sample JSON, checks block/allow/fail-open.
# Fixture tree is a mktemp dir (TMPDIR, e.g. the session scratchpad) used as
# the hook's NO_STALE_ROOT; removed on exit.
H=$(dirname "$0")/no_stale_claudemd.sh
R=$(mktemp -d) || exit 1
trap 'rm -rf "$R"' EXIT
R=$R/; export NO_STALE_ROOT=$R
mkdir -p "$R/big/sub" "$R/small/sub" || exit 1
head -c 40000 /dev/zero | tr '\0' x > "$R/big/CLAUDE.md"
head -c 100 /dev/zero | tr '\0' x > "$R/small/CLAUDE.md"
fail=0
t() { # name want json
    printf '%s' "$3" | bash "$H" 2>/dev/null; got=$?
    [ "$got" = "$2" ] || { echo "FAIL $1: want $2 got $got"; fail=1; }
}
t big-root-file 2 "{\"tool_name\":\"Read\",\"tool_input\":{\"file_path\":\"${R}big/x.md\"}}"
t big-nested 2 "{\"tool_input\":{\"file_path\":\"${R}big/sub/y.c\"}}"
t big-notebook 2 "{\"tool_input\":{\"notebook_path\":\"${R}big/n.ipynb\"}}"
t small-ok 0 "{\"tool_input\":{\"file_path\":\"${R}small/sub/y.c\"}}"
t outside-ok 0 '{"tool_input":{"file_path":"/home/pcrec/projects/pcrec/docs/x.md"}}'
t no-claudemd-ok 0 "{\"tool_input\":{\"file_path\":\"${R}nonexistent/a.c\"}}"
t failopen-garbage 0 'not json at all'
t failopen-nopath 0 '{"tool_input":{"command":"ls"}}'
t failopen-empty 0 ''
[ $fail = 0 ] && echo "test_no_stale_claudemd: ok"
exit $fail
