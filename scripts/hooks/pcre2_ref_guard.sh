#!/usr/bin/env bash
# scripts/hooks/pcre2_ref_guard.sh -- PreToolUse hook (every tool that takes a
# path or a command), the clean-room wall around the pinned PCRE2 source copy
# (D181, Frank 2026-10-29). Exit 2 blocks, reason on stderr.
#
# The copy lives at /var/tmp/pcrec-<user>/ref/pcre2-<ver>, read-only, never
# built or run, never in the repo. READERS (agent_type pcre2-reader) may read
# it and write prose notes to $PCREC_TMPDIR/scratch/pcre2notes/; WRITERS (the
# main session, every other subagent) never touch it, so nothing is copied.
#
# BLOCKED: any call whose tool_input text (every string value except
#   content/old_string/new_string/new_source, which are payload, not
#   references) names the ref root -- the fragment `ref/pcre2`, `pcrec-*/ref`,
#   `TMPDIR/ref` -- unless agent_type == pcre2-reader. Also blocked for
#   EVERYONE, readers included: Write/Edit/NotebookEdit of a file under the
#   ref root (the copy is read-only), and for a reader a Bash command naming
#   the root together with a write/copy verb (rm mv cp chmod tee dd rsync tar
#   install ln touch truncate, `>`, sed -i, -delete, git clone/checkout/...).
#   A reader's Write/Edit/NotebookEdit must target .../scratch/pcre2notes/.
# FAILS CLOSED for this path class: a call that mentions the ref root but
#   whose JSON cannot be parsed is blocked. A call that mentions neither the
#   ref root nor pcre2-reader exits 0 on a cheap raw-text test.
# ESCAPE (setup window): ROOT/worktrees/.mgr/pcre2_ref_setup_ok, written by
#   the manager for the clone + chmod, removed right after. While present the
#   MAIN session's (no agent_id) Bash calls are admitted.
# Only top-level keys and tool_input's own strings are read; agent_id inside
#   file CONTENT is ignored. HOOK_ROOT / HOOK_REFROOT override ROOT and add a
#   literal ref root to match (the test).
ROOT=${HOOK_ROOT:-/home/pcrec/projects/pcrec/}
SETUP=${HOOK_SETUPFILE:-${ROOT}worktrees/.mgr/pcre2_ref_setup_ok}
in=$(cat)
raw=$(printf '%s' "$in" | tr -d '\\')
RE='ref/pcre2|pcrec-[A-Za-z0-9_.-]*/ref([^A-Za-z0-9_.-]|$)|TMPDIR\}?/ref([^A-Za-z0-9_.-]|$)'
hit() { # text -> 0 if it names the ref root
    printf '%s' "$1" | grep -Eq "$RE" && return 0
    [ -n "${HOOK_REFROOT:-}" ] && case $1 in *"$HOOK_REFROOT"*) return 0 ;; esac
    return 1
}
if ! hit "$raw"; then
    case $raw in *pcre2-reader*) ;; *) exit 0 ;; esac
fi
out=$(printf '%s' "$in" | awk '
BEGIN { DQ = "\""; BS = "\\"; skip["content"]=1; skip["old_string"]=1; skip["new_string"]=1; skip["new_source"]=1 }
{ buf = buf $0 "\n" }
END {
    n = length(buf); depth = 0; key = ""; intool = 0; seen = 0
    for (p = 1; p <= n; p++) {
        c = substr(buf, p, 1)
        if (c == DQ) {
            s = ""
            for (p++; p <= n; p++) {
                c = substr(buf, p, 1)
                if (c == DQ) break
                if (c == BS) { p++; c = substr(buf, p, 1); if (c == "u") { s = s "?"; p += 4; continue } }
                s = s c
            }
            if (c != DQ) { bad = 1; break }
            q = p + 1
            while (substr(buf, q, 1) ~ /[ \t\n\r]/) q++
            if (substr(buf, q, 1) == ":") { if (depth == 1) { key = s; if (key == "tool_input") intool = 1 } else if (intool) key = s; continue }
            if (depth == 1 && key == "agent_id") aid = s
            else if (depth == 1 && key == "agent_type") atype = s
            else if (depth == 1 && key == "tool_name") tname = s
            else if (intool && depth >= 2 && !(key in skip)) {
                txt = txt " " s
                if (depth == 2 && (key == "file_path" || key == "notebook_path")) path = s
            }
            continue
        }
        if (c == "{" || c == "[") { depth++; seen = 1 }
        else if (c == "}" || c == "]") { depth--; if (depth < 2) intool = 0 }
    }
    ok = (!bad && seen && depth == 0) ? 1 : 0
    print ok; print aid; print atype; print tname; print path; print txt
}' 2>/dev/null)
ok=$(printf '%s\n' "$out" | sed -n 1p)
aid=$(printf '%s\n' "$out" | sed -n 2p)
atype=$(printf '%s\n' "$out" | sed -n 3p)
tool=$(printf '%s\n' "$out" | sed -n 4p)
path=$(printf '%s\n' "$out" | sed -n 5p)
txt=$(printf '%s\n' "$out" | sed -n '6,$p')
B="BLOCKED by scripts/hooks/pcre2_ref_guard.sh:"
if [ "$ok" != 1 ]; then
    echo "$B call names the PCRE2 reference copy and its input could not be parsed (fails closed); only a pcre2-reader subagent reads it (docs/dev/pcre2_notes/CLAUDE.md)." >&2
    exit 2
fi
refpath=0; hit "$path" && refpath=1
case $tool in Write|Edit|MultiEdit|NotebookEdit)
    if [ $refpath = 1 ]; then
        echo "$B the PCRE2 reference copy is read-only: no tool writes under it ($path)." >&2; exit 2
    fi
    if [ "$atype" = pcre2-reader ]; then
        case $path in */scratch/pcre2notes/*) ;; *)
            echo "$B a pcre2-reader writes only to \$PCREC_TMPDIR/scratch/pcre2notes/<slug>.md ($path)." >&2; exit 2 ;; esac
    fi ;;
esac
hit "$txt" || exit 0
if [ "$atype" = pcre2-reader ]; then
    case $tool in Bash)
        w=$(printf '%s' "$txt" | sed -E 's/[0-9]*>&[0-9-]//g; s/[0-9]*>[[:space:]]*\/dev\/null//g')
        if printf '%s' "$w" | grep -Eq '(^|[^[:alnum:]_.-])(rm|mv|cp|chmod|chown|tee|dd|rsync|tar|install|ln|touch|truncate)[[:space:]]|>|sed[[:space:]]+(-[A-Za-z]*i|--in-place)|-delete|git[[:space:]]+(clone|fetch|pull|checkout|switch|clean|reset|apply|restore|stash|am)'; then
            echo "$B a pcre2-reader reads the copy; a Bash command naming it with a write/copy verb is refused." >&2; exit 2
        fi ;;
    esac
    exit 0
fi
if [ "$tool" = Bash ] && [ -z "$aid" ] && [ -r "$SETUP" ]; then exit 0; fi
echo "$B the PCRE2 reference copy is read only via a pcre2-reader subagent (agent_type pcre2-reader), whose prose notes land in docs/dev/pcre2_notes/. Writers never open it, so nothing is copied. Spawn a pcre2-reader with ONE named question." >&2
exit 2
