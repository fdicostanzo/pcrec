#!/usr/bin/env bash
# Test for no_commit_all.sh: feeds sample PreToolUse JSON (the shape
# no_cd_worktree.sh gets), checks block (exit 2) / allow (0) / fail-open.
H=$(dirname "$0")/no_commit_all.sh
fail=0
t() { # name want command
    local j
    j=$(printf '%s' "$3" | sed 's/\\/\\\\/g; s/"/\\"/g' | awk '{ printf "%s%s", (NR > 1 ? "\\n" : ""), $0 }')
    printf '{"session_id":"s","tool_name":"Bash","tool_input":{"command":"%s"}}' "$j" | bash "$H" 2>/dev/null; got=$?
    [ "$got" = "$2" ] || { echo "FAIL $1: want $2 got $got"; fail=1; }
}
# blocked
t a 2 'git commit -a -m x'
t all 2 'git commit --all -m x'
t am 2 'git commit -am "msg"'
t avm 2 'git commit -avm "msg"'
t qa 2 'git commit -qa -m x'
t a-after-m 2 'git commit -m x -a'
t dash-C 2 'git -C /home/pcrec/projects/pcrec/worktrees/x commit -a -m x'
t dash-c 2 'git -c user.name=x commit -a -m x'
t and 2 'make strict && git commit -am x'
t semi 2 'git status; git commit -a -m x'
t pipe 2 'echo y | git commit -a -F -'
t newline 2 $'git add f\ngit commit -a -m x'
t subshell 2 '(git commit -am x)'
t cmdsubst 2 'echo $(git commit -a -m x)'
t if-then 2 'if true; then git commit -a -m x; fi'
t amend-a 2 'git commit --amend -a --no-edit'
t heredoc-then-a 2 $'git commit -m "$(cat <<\'EOF\'\nline -a\nEOF\n)" -a'
# allowed
t msg-text 0 'git commit -m "fix -a flag handling"'
t msg-text2 0 "git commit -m 'use --all here'"
t msg-arg-separate 0 'git commit -m -a'
t amend 0 'git commit --amend --no-edit'
t amend-m 0 'git commit --amend -m "x"'
t named 0 'git commit -m x -- src/a.c docs/b.md'
t named-C 0 'git -C /x commit -m x -- a.c'
t add-A 0 'git add -A'
t add-A-commit 0 'git add f && git commit -m x'
t m-cluster-a 0 'git commit -ma'
t log-a 0 'git log -a'
t other-sub 0 'git -C /x status -a'
t echo-quoted 0 'echo "git commit -a"'
t heredoc-msg 0 $'git commit -m "$(cat <<\'EOF\'\nsubject\n\nbody with git commit -a and -a text\nEOF\n)"'
t doubledash 0 'git commit -- -a'
t file-opt 0 'git commit --file msg.txt -- a.c'
# fail open
t failopen-garbage 0 'x'
for j in 'not json' '' '{"tool_input":{"file_path":"/x"}}'; do
    printf '%s' "$j" | bash "$H" 2>/dev/null; [ $? = 0 ] || { echo "FAIL failopen '$j'"; fail=1; }
done
[ $fail = 0 ] && echo "test_no_commit_all: ok"
exit $fail
