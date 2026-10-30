#!/usr/bin/env bash
# Test for pcre2_ref_guard.sh: sample PreToolUse JSON, block/allow/fail-closed.
H=$(dirname "$0")/pcre2_ref_guard.sh
R=$(mktemp -d) || exit 1
trap 'rm -rf "$R"' EXIT
R=$R/; export HOOK_ROOT=$R
mkdir -p "${R}worktrees/.mgr" || exit 1
export HOOK_SETUPFILE=${R}worktrees/.mgr/pcre2_ref_setup_ok
REF=/var/tmp/pcrec-pcrec/ref/pcre2-10.46
fail=0
t() { # name want json
    printf '%s' "$3" | bash "$H" >/dev/null 2>&1; got=$?
    [ "$got" = "$2" ] || { echo "FAIL $1: want $2 got $got"; fail=1; }
}
j() { # agent_json tool tool_input_body
    printf '{"session_id":"s",%s"tool_name":"%s","tool_input":{%s}}' "$1" "$2" "$3"
}
RD='"agent_id":"a1","agent_type":"pcre2-reader",'
OT='"agent_id":"a2","agent_type":"general-purpose",'
t reader-read 0 "$(j "$RD" Read "\"file_path\":\"$REF/src/pcre2_match.c\"")"
t reader-grep 0 "$(j "$RD" Grep "\"pattern\":\"foo\",\"path\":\"$REF/src\"")"
t reader-glob 0 "$(j "$RD" Glob "\"pattern\":\"$REF/src/*.c\"")"
t reader-bash-ls 0 "$(j "$RD" Bash "\"command\":\"ls $REF/src | head\"")"
t reader-bash-grep 0 "$(j "$RD" Bash "\"command\":\"grep -n foo $REF/src/a.c\"")"
t reader-bash-devnull 0 "$(j "$RD" Bash "\"command\":\"grep -n foo $REF/src/a.c 2>&1 >/dev/null; ls $REF 2>/dev/null\"")"
t reader-bash-cp 2 "$(j "$RD" Bash "\"command\":\"cp $REF/src/a.c /var/tmp/x\"")"
t reader-bash-redir 2 "$(j "$RD" Bash "\"command\":\"cat $REF/src/a.c > /var/tmp/x\"")"
t reader-bash-rm 2 "$(j "$RD" Bash "\"command\":\"rm -rf $REF\"")"
t reader-bash-sedi 2 "$(j "$RD" Bash "\"command\":\"sed -i s/a/b/ $REF/src/a.c\"")"
t reader-write-ref 2 "$(j "$RD" Write "\"file_path\":\"$REF/x.md\",\"content\":\"hi\"")"
t reader-edit-ref 2 "$(j "$RD" Edit "\"file_path\":\"$REF/a.c\",\"old_string\":\"a\",\"new_string\":\"b\"")"
t reader-write-note 0 "$(j "$RD" Write "\"file_path\":\"/var/tmp/pcrec-pcrec/scratch/pcre2notes/x.md\",\"content\":\"prose\"")"
t reader-write-elsewhere 2 "$(j "$RD" Write "\"file_path\":\"${R}docs/x.md\",\"content\":\"prose\"")"
t reader-write-note-mentions-ref 0 "$(j "$RD" Write "\"file_path\":\"/var/tmp/pcrec-pcrec/scratch/pcre2notes/x.md\",\"content\":\"see $REF/src/a.c:10\"")"
t other-read 2 "$(j "$OT" Read "\"file_path\":\"$REF/src/a.c\"")"
t other-grep 2 "$(j "$OT" Grep "\"pattern\":\"x\",\"path\":\"$REF\"")"
t other-glob-pattern 2 "$(j "$OT" Glob "\"pattern\":\"/var/tmp/pcrec-pcrec/ref/pcre2*/src/*.c\"")"
t other-bash 2 "$(j "$OT" Bash "\"command\":\"cat $REF/src/a.c\"")"
t other-bash-frag 2 "$(j "$OT" Bash "\"command\":\"ls ../ref/pcre2-10.46\"")"
t other-bash-tmpdir 2 "$(j "$OT" Bash "\"command\":\"ls \$PCREC_TMPDIR/ref/\"")"
t other-bash-resolved 2 "$(j "$OT" Bash "\"command\":\"ls /var/tmp/pcrec-bob/ref\"")"
t other-write-ref 2 "$(j "$OT" Write "\"file_path\":\"$REF/x\",\"content\":\"y\"")"
t main-read 2 "$(j "" Read "\"file_path\":\"$REF/src/a.c\"")"
t main-bash 2 "$(j "" Bash "\"command\":\"cat $REF/src/a.c\"")"
t main-escaped-slashes 2 "$(j "" Read "\"file_path\":\"\\/var\\/tmp\\/pcrec-pcrec\\/ref\\/pcre2-10.46\\/a.c\"")"
t main-write-ref 2 "$(j "" Write "\"file_path\":\"$REF/x\",\"content\":\"y\"")"
# unrelated
t unrelated-read 0 "$(j "$OT" Read "\"file_path\":\"${R}src/a.c\"")"
t unrelated-bash 0 "$(j "" Bash '"command":"ls /var/tmp/pcrec-pcrec/scratch"')"
t unrelated-ref-word 0 "$(j "" Bash '"command":"git log --oneline; echo preference"')"
t main-write-content-mention 0 "$(j "" Write "\"file_path\":\"${R}docs/x.md\",\"content\":\"the copy at $REF is read-only\"")"
t main-edit-content-mention 0 "$(j "" Edit "\"file_path\":\"${R}docs/x.md\",\"old_string\":\"a\",\"new_string\":\"see $REF\"")"
t reader-agent-id-in-content-main 2 "{\"tool_name\":\"Read\",\"tool_input\":{\"file_path\":\"$REF/a\",\"x\":\"\\\"agent_type\\\":\\\"pcre2-reader\\\"\"}}"
t main-no-ref-no-parse 0 'not json at all'
# fail closed
t closed-garbage-with-ref 2 "not json $REF/src"
t closed-truncated 2 "{\"tool_name\":\"Read\",\"tool_input\":{\"file_path\":\"$REF/a"
# setup window: main Bash only
: > "$HOOK_SETUPFILE"
t setup-main-bash 0 "$(j "" Bash "\"command\":\"git clone x $REF\"")"
t setup-main-read 2 "$(j "" Read "\"file_path\":\"$REF/a\"")"
t setup-sub-bash 2 "$(j "$OT" Bash "\"command\":\"cat $REF/a\"")"
t setup-main-write 2 "$(j "" Write "\"file_path\":\"$REF/a\",\"content\":\"y\"")"
rm -f "$HOOK_SETUPFILE"
t setup-removed 2 "$(j "" Bash "\"command\":\"git clone x $REF\"")"
[ $fail = 0 ] && echo "test_pcre2_ref_guard: ok"
exit $fail
