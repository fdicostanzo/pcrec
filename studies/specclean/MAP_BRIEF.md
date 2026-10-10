# Claims-mapping brief (specclean lane)

SCOPE MANDATE: write ONLY inside /home/pcrec/projects/pcrec/worktrees/specclean/studies/specclean/ (your one output file, plus scratch files under studies/specclean/probe_tmp/ if you run probes). Read anything in /home/pcrec/projects/pcrec/worktrees/specclean. You may RUN /home/pcrec/projects/pcrec/worktrees/specclean/build/pcrec (with -o pointing into probe_tmp/) and gcc to probe behaviour, with TMPDIR=studies/specclean/probe_tmp. Never run make, never git commit, never write /tmp or anywhere else. Subagents inherit this mandate.

CONTEXT: docs/spec/match_api.md was rewritten facts-only. The OLD text is studies/specclean/match_api.old.md. Normative claims were extracted from the old text into studies/specclean/claims_<PART>.tsv (columns: id, old_line, kind, claim). Your job: for EVERY row of your claims file, find where the NEW docs/spec/match_api.md states that fact.

For each claim decide one status:
- MAPPED: the new doc states the same fact (possibly reworded, possibly merged with others). Give the new line number where it is stated.
- POINTED: the new doc deliberately defers the fact to another spec doc it names at that spot (e.g. "tuning.md §2.17's table") AND that other doc states it (check it: grep docs/spec/tuning.md, limits.md, vars.md, findings.md, cli.md). Give the new line of the pointer and the other doc's file:line.
- HISTORY: on re-reading, the claim is not a current-behaviour fact (it is past-state history, process, or a statement about an old artifact) — say why in the note.
- SUPERSEDED: the old claim is no longer true of the shipped artifact and the new doc states the current truth instead. Give the new line AND evidence that the new statement is the live behaviour (a build/pcrec probe output, or src/ file:line).
- UNMAPPED: the new doc does not state it anywhere. Say in the note whether you believe it is still TRUE (and why — src file:line or probe), or FALSE.
Claims prefixed "CHECK:" are uncertain; verify them against src/ or a probe before choosing.

Be strict: MAPPED only when a reader of the new doc would learn the same fact. A fact that is only implied, or only true of a narrower case, is UNMAPPED (note what is missing). Numbers must match (if old and new numbers differ, it is SUPERSEDED or UNMAPPED, with evidence).

OUTPUT: studies/specclean/map_<PART>.tsv, tab-separated, NO header, one row per input claim in input order:
  id <TAB> status <TAB> new_line <TAB> note
(new_line empty for HISTORY/UNMAPPED; note one line, no tabs, under ~300 chars).
Method: read the new doc fully once (Read tool, ~400 lines at a time), then go through your claims; use grep -n on the new doc to locate keywords. When done, reply with counts per status and the ids of every UNMAPPED and SUPERSEDED row. Then END.
