#!/usr/bin/env bash
# scripts/hooks/no_commit_all.sh -- PreToolUse(Bash) hook, registered in the
# project's .claude/settings.json beside no_cd_worktree.sh ([HOOK-GUARDS],
# Frank 2026-10-25). `git commit -a` / `--all` sweeps every tracked change
# into the commit, including another session's or lane's uncommitted edits
# (memory pcrec-no-commit-a-during-landing; a bench slip via `git -C` in a
# live lane worktree). Exit 2 blocks the call, one-line reason on stderr.
#
# BLOCKED (at any command position, also after && ; | newline ( ) ):
#   git commit -a | --all | -am | -avm | -qa ...  (a short-flag cluster with
#   `a` before an argument-taking letter m F C c t), `git -C DIR commit -a`,
#   `git -c k=v commit -a`.
# ALLOWED: flag text inside a message (-m "x -a"), --amend, `git add -A`
#   (a separate rule), commit with named paths, and anything quoted as a
#   whole (bash -c "git commit -a": a deliberate gap, as in no_cd_worktree.sh).
# Fails OPEN on anything it cannot parse. Bash + one awk, no jq/python.
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
    start = 1
    for (x = 1; x <= nt; x++) {
        y = t[x]
        if (y == "(" || y == "S") { start = 1; continue }
        if (y == ")") { start = 0; continue }
        w = substr(y, 2)
        if (start && (w == "then" || w == "do" || w == "else" || w == "{" || w == "!" || w == "builtin" || w == "command" || w == "exec")) continue
        if (start && w == "git") scan(x + 1)
        start = 0
    }
    exit 0
}
function scan(z,   a, c, ch) {
    # git global options, then the subcommand
    while (z <= nt && substr(t[z], 1, 1) == "W") {
        a = substr(t[z], 2)
        if (a == "-C" || a == "-c" || a == "--git-dir" || a == "--work-tree" || a == "--namespace") { z += 2; continue }
        if (a ~ /^-/) { z++; continue }
        break
    }
    if (z > nt || substr(t[z], 1, 1) != "W" || substr(t[z], 2) != "commit") return
    z++
    while (z <= nt && substr(t[z], 1, 1) == "W") {
        a = substr(t[z], 2)
        if (a == "--") return
        if (a == "--all") block()
        if (a ~ /^--(message|file|author|date|template|reuse-message|reedit-message|fixup|squash|cleanup|trailer|gpg-sign)$/) { z += 2; continue }
        if (a ~ /^--/) { z++; continue }
        if (a ~ /^-/) {
            for (c = 2; c <= length(a); c++) {
                ch = substr(a, c, 1)
                if (ch == "a") block()
                # an argument-taking letter ends the cluster; a bare one takes the next word
                if (index("mFCct", ch)) { if (c == length(a)) z++; break }
                if (ch == "S" || ch == "u") break
            }
        }
        z++
    }
}
function block() {
    print "BLOCKED by scripts/hooks/no_commit_all.sh: git commit -a/--all sweeps in other sessions edits; commit named paths instead (git commit -m msg -- path ...)." > "/dev/stderr"
    exit 2
}
'
