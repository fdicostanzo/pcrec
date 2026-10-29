# pcre2wall report

## Summary
The clean-room wall is built (D181): a guard hook, a `pcre2-reader` agent type, a prose-note checker, a notes directory with its rules, and docs. Ruling R1 (cite in source what was leaned on heavily) is applied across D181, the notes CLAUDE.md, the root situation-index row, the reader body, `docs/dev/guide/coding.md` 4.1a and a new `[PCRE2src]` entry in REFERENCES.md. Nothing under `src/`, `cli/`, `lib/` changed. No PCRE2 source was read, downloaded or copied. D number used: D181 (highest on main was D180).

## Premise test
`scripts/hooks/lane_writes_in_worktree.sh` documents and parses top-level `agent_id` and `agent_type` (present only inside a subagent). The new hook reads the same two keys and a fixture with `"agent_type":"pcre2-reader"` is distinguished from `general-purpose` and from the main session. Premise holds; no stop needed. Caveat: a real `pcre2-reader` run has not been exercised live (the copy does not exist yet); the first reader run after the clone is the live check.

## The guard hook
`scripts/hooks/pcre2_ref_guard.sh`, registered in `.claude/settings.json` as the first PreToolUse entry with matcher `.*` (every tool; a cheap raw-text test exits 0 unless the call mentions the ref root or `pcre2-reader`).
- Names the ref root = tool_input string values (except content/old_string/new_string/new_source) matching `ref/pcre2`, `pcrec-*/ref`, or `TMPDIR/ref`, plus an optional `HOOK_REFROOT` literal (test).
- Blocked for the main session and every agent_type except `pcre2-reader`. The scan includes Agent prompts, so briefs to a reader must not name the path (stated in the notes CLAUDE.md).
- Blocked for EVERYONE, readers included: Write/Edit/MultiEdit/NotebookEdit of a path under the root. A reader's Write/Edit must target `*/scratch/pcre2notes/*`. A reader's Bash naming the root with a write/copy verb (rm mv cp chmod tee dd rsync tar install ln touch truncate, `>` other than `2>&1`/`>/dev/null`, sed -i, -delete, git clone/checkout/...) is refused.
- Fails closed: a call that mentions the root but whose JSON does not parse (garbage, truncated) is blocked.
- Setup window (my addition, needed because the hook also blocks the manager's clone): `worktrees/.mgr/pcre2_ref_setup_ok`, manager-written, admits the MAIN session's Bash only; remove it after the chmod.

## The reader agent type
`.claude/agents/pcre2-reader.md`: model sonnet, tools Read, Grep, Glob, Bash, Write. One question per run, prose only, no code or internal identifiers (public names and `file:line` citations at the tag only), READ/DOCUMENTED/INFERRED tags on claims, note written only to `$PCREC_TMPDIR/scratch/pcre2notes/<slug>.md`, runs the checker, never becomes a writer. Ends the note with a "Cited by" section (R1 back-reference).

## Notes and the checker
`docs/dev/pcre2_notes/CLAUDE.md` holds the wall rules, how a note crosses (reader writes, checker passes, manager commits, writers cite the note never the copy) and the R1 citation rule. `scripts/check_pcre2_note.sh NOTE.md` rejects: fenced blocks, preprocessor lines, brace-only/brace-ending lines, statement lines ending in `;` containing `(` or `=`, C operator runs (`-> && || == != << >> += -= ++`), `PRIV`, ALL_CAPS_WITH_UNDERSCORE not `PCRE2_*`, `pcre2_*_8/16/32`, and lowercase_snake identifiers of three or more words that are not `pcre2_*`. File citations (`name.c:123`, `name.h`) are stripped first. The identifier rules are heuristics: a public non-`pcre2_` three-word lowercase name would be rejected and has to be reworded.

## Tests and sabotage
- `scripts/hooks/test_pcre2_ref_guard.sh`: 40 cases (reader allowed; reader copy/redirect/rm/sed -i refused; other subagent blocked; main blocked; escaped slashes; Bash text and fragment forms; unrelated allowed; content-only mention allowed; write under root blocked for all; fail-closed garbage/truncated; setup window). Wired by `scripts/tests/hooks.test` (now also runs the other two hook fixture tests; `scripts/Makefile` gets a dependency line). `hooks.test`: 40 passed.
- `scripts/tests/check_pcre2_note.sh.test`: one clean prose note passes; 15 planted pasted-code shapes fail; 4 public-name/citation/semicolon-prose cases pass.
- Sabotage (copies in scratch): drop the `/dev/null` strip, disable fail-closed, un-skip content, setup window for all agents each turn a test red. Disabling the explicit write-under-root block alone stays green because the writer fallthrough and the reader's pcre2notes rule also block it (defence in depth, no independent witness).
- I did NOT run the whole `make -C scripts test` (it started every script self-test and I killed it); only the two tests above.

## Docs updated
Root CLAUDE.md (one situation-index row), scripts/CLAUDE.md (hooks line, kept under 4096), docs/testing.md (hook paragraph), docs/dev/decisions.md (D181), docs/dev/guide/coding.md (4.1a), REFERENCES.md (`[PCRE2src]`), docs/dev/pcre2_notes/CLAUDE.md (new). `make test-claudemd-size` equivalent (`check_claudemd_size.sh --all`) is clean.

## Clone procedure
Run by the manager AFTER this branch is merged (so the hook and the agent exist), as the main session:
```
touch /home/pcrec/projects/pcrec/worktrees/.mgr/pcre2_ref_setup_ok
mkdir -p /var/tmp/pcrec-pcrec/ref
git clone --depth 1 --branch pcre2-10.46 https://github.com/PCRE2Project/pcre2.git /var/tmp/pcrec-pcrec/ref/pcre2-10.46
git -C /var/tmp/pcrec-pcrec/ref/pcre2-10.46 rev-parse HEAD     # record the commit in D181
chmod -R a-w /var/tmp/pcrec-pcrec/ref/pcre2-10.46
rm /home/pcrec/projects/pcrec/worktrees/.mgr/pcre2_ref_setup_ok
```
Note: the tag sits on the commit the clone prints; `.git` inside the copy is part of the read-only tree. Do not open any file in it. Then spawn one `pcre2-reader` with a question and no path in the prompt.

## STATE AT HANDOFF
Branch lane/pcre2wall committed, tree clean after commit. Last rulings entry applied: R1. Both tests green; full scripts suite not run (not needed). Nothing owed.
