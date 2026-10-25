#!/usr/bin/env bash
# Test for lane_writes_in_worktree.sh: sample PreToolUse JSON, block/allow/
# fail-open. Fixture ROOT and escape file live in a mktemp dir (TMPDIR).
H=$(dirname "$0")/lane_writes_in_worktree.sh
R=$(mktemp -d) || exit 1
trap 'rm -rf "$R"' EXIT
R=$R/; export HOOK_ROOT=$R
mkdir -p "${R}worktrees/.mgr" || exit 1
export HOOK_ALLOWFILE=${R}worktrees/.mgr/main_write_ok
fail=0
t() { # name want json
    printf '%s' "$3" | bash "$H" 2>/dev/null; got=$?
    [ "$got" = "$2" ] || { echo "FAIL $1: want $2 got $got"; fail=1; }
}
j() { # agent_json path [tool_input_extra]  (agent_json may be empty)
    printf '{"session_id":"s",%s"tool_name":"Write","tool_input":{%s"file_path":"%s"}}' "$1" "$3" "$2"
}
A='"agent_id":"ag1","agent_type":"general-purpose",'
t sub-main-tree 2 "$(j "$A" "${R}src/a.c")"
t sub-main-docs 2 "$(j "$A" "${R}docs/x.md")"
t sub-edit-after 2 "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"${R}src/a.c\"},\"agent_id\":\"ag1\"}"
t sub-notebook 2 "{\"agent_id\":\"ag1\",\"tool_input\":{\"notebook_path\":\"${R}n.ipynb\"}}"
t sub-worktree-ok 0 "$(j "$A" "${R}worktrees/lane/src/a.c")"
t sub-outside-ok 0 "$(j "$A" "/scratch/x.txt")"
t sub-relative-ok 0 "$(j "$A" "src/a.c")"
t main-session-ok 0 "$(j "" "${R}src/a.c")"
t main-with-agent-type-ok 0 "$(j '"agent_type":"claude",' "${R}src/a.c")"
# agent_id text inside file CONTENT must not make the main session look like a subagent
t content-agent-id-ok 0 "{\"tool_name\":\"Write\",\"tool_input\":{\"content\":\"\\\"agent_id\\\":\\\"zz\\\"\",\"file_path\":\"${R}src/a.c\"}}"
# a path-looking string in content must not be taken as the path
t content-path-ignored 2 "{\"agent_id\":\"ag1\",\"tool_input\":{\"content\":\"\\\"file_path\\\":\\\"/elsewhere\\\"\",\"file_path\":\"${R}src/a.c\"}}"
# escape file
echo "# comment" > "$HOOK_ALLOWFILE"
t esc-comment-only 2 "$(j "$A" "${R}src/a.c")"
echo "other" > "$HOOK_ALLOWFILE"
t esc-other-id 2 "$(j "$A" "${R}src/a.c")"
echo "ag1" > "$HOOK_ALLOWFILE"
t esc-id 0 "$(j "$A" "${R}src/a.c")"
echo "agent_type:general-purpose" > "$HOOK_ALLOWFILE"
t esc-type 0 "$(j "$A" "${R}src/a.c")"
echo "agent_type:" > "$HOOK_ALLOWFILE"
t esc-empty-type 2 "$(j '"agent_id":"ag1",' "${R}src/a.c")"
echo "*" > "$HOOK_ALLOWFILE"
t esc-star 0 "$(j "$A" "${R}src/a.c")"
rm -f "$HOOK_ALLOWFILE"
t esc-removed 2 "$(j "$A" "${R}src/a.c")"
# fail open
t failopen-garbage 0 'not json at all'
t failopen-empty 0 ''
t failopen-nopath 0 '{"agent_id":"ag1","tool_input":{"command":"ls"}}'
[ $fail = 0 ] && echo "test_lane_writes_in_worktree: ok"
exit $fail
