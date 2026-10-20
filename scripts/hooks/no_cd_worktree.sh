#!/usr/bin/env bash
# scripts/hooks/no_cd_worktree.sh -- PreToolUse(Bash) hook, registered in the
# project's .claude/settings.json (apply_here.md proposal 4; owner-approved
# 2026-10-20). A `cd` in a Bash command MOVES THE SESSION'S WORKING DIRECTORY
# (for in-process lanes too) and persists to the next command; 25+ manager
# slips (merges and commits landing in the wrong tree) came from it. Exit 2
# blocks the call, with a one-line reason on stderr.
#
# BLOCKED (outside quotes, at depth 0 -- not inside ( ... ) or $( ... )):
#   cd <path containing worktrees/>        (any form, also alone)
#   cd X && ... / cd X; ... / cd X || ... / cd X <newline> ...   (chaining)
# ALLOWED:
#   a plain `cd` / `cd /repo/root` / `cd $D` as the WHOLE command;
#   `git -C worktrees/x ...` and absolute paths (no cd at all);
#   a cd inside a quoted string (ssh host 'cd x && make', bash -c "cd ..."):
#     it runs elsewhere or in a child shell, never moves the session -- the
#     hook does not look inside quotes (a deliberate gap: `bash -c "cd
#     worktrees/x && ..."` is not caught);
#   a cd in a subshell, `(cd "$d" && make)` / `for d in ..; do (cd "$d" ..);
#     done` / `$(cd x && pwd)`: the subshell's cwd dies with it, so nothing
#     persists. (A non-subshell `for ..; do cd "$d" && ..; done` IS chaining
#     and is blocked.)
# Fails OPEN on anything it cannot parse (no tool_input.command, no awk
# output): a hook bug must never lock the tool. Bash + one awk, no jq/python
# (~3 ms). The JSON string is decoded for \n \t \" \\ \/ only.
exec awk '
BEGIN { BS = "\\"; DQ = "\"" }
{ buf = buf $0 "\n" }
END {
    i = index(buf, DQ "tool_input" DQ); if (!i) exit 0
    rest = substr(buf, i)
    j = index(rest, DQ "command" DQ); if (!j) exit 0
    rest = substr(rest, j + 9)
    k = index(rest, DQ); if (!k) exit 0
    rest = substr(rest, k + 1)
    n = length(rest); cmd = ""
    for (p = 1; p <= n; p++) {
        c = substr(rest, p, 1)
        if (c == DQ) break
        if (c == BS) {
            p++; c = substr(rest, p, 1)
            if (c == "n") c = "\n"; else if (c == "t") c = "\t"
            else if (c == "u") { cmd = cmd "?"; p += 4; continue }
        }
        cmd = cmd c
    }
    # tokenize: words (quotes removed) and separators ; & | newline ( )
    n = length(cmd); nt = 0; cur = ""; have = 0; q = ""
    for (p = 1; p <= n; p++) {
        c = substr(cmd, p, 1)
        if (q != "") {
            if (c == q) q = ""
            else if (c == BS && q == DQ) { p++; cur = cur substr(cmd, p, 1) }
            else cur = cur c
            continue
        }
        if (c == "\047" || c == DQ) { q = c; have = 1; continue }
        if (c == BS) { p++; cur = cur substr(cmd, p, 1); have = 1; continue }
        if (c == " " || c == "\t") { if (have) { t[++nt] = "W" cur; cur = ""; have = 0 } continue }
        if (c == ";" || c == "&" || c == "|" || c == "\n" || c == "(" || c == ")") {
            if (have) { t[++nt] = "W" cur; cur = ""; have = 0 }
            if (c == "&" || c == "|") { if (substr(cmd, p + 1, 1) == c) p++ }
            if (nt > 0 && t[nt] == "S" && c != "(" && c != ")") continue
            t[++nt] = (c == "(" || c == ")") ? c : "S"
            continue
        }
        if (c == "#" && !have) { while (p < n && substr(cmd, p + 1, 1) != "\n") p++; continue }
        cur = cur c; have = 1
    }
    if (have) t[++nt] = "W" cur
    depth = 0; start = 1
    for (x = 1; x <= nt; x++) {
        y = t[x]
        if (y == "(") { depth++; start = 1; continue }
        if (y == ")") { if (depth > 0) depth--; start = 0; continue }
        if (y == "S") { start = 1; continue }
        w = substr(y, 2)
        if (start && (w == "then" || w == "do" || w == "else" || w == "{" || w == "!" || w == "builtin" || w == "command")) continue
        if (start && depth == 0 && (w == "cd" || w == "pushd")) {
            z = x + 1; arg = ""
            while (z <= nt && substr(t[z], 1, 1) == "W") { a = substr(t[z], 2); if (a !~ /^-/ && arg == "") arg = a; z++ }
            if (arg ~ /(^|\/)worktrees(\/|$)/) block("cd into a worktrees/ path")
            if (hasS(x)) block("cd chained with another command")
        }
        start = 0
    }
    exit 0
}
function hasS(x,   z) {
    # a separator after this cd statement followed by any further token
    z = x + 1
    while (z <= nt && substr(t[z], 1, 1) == "W") z++
    if (z > nt || t[z] != "S") return 0
    while (z <= nt && t[z] == "S") z++
    return (z <= nt)
}
function block(why) {
    printf "BLOCKED by scripts/hooks/no_cd_worktree.sh: %s moves the session cwd; use absolute paths or git -C <dir> (a (cd X && ...) subshell is fine).\n", why > "/dev/stderr"
    exit 2
}
'
