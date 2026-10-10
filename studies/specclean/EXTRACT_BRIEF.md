# Claims-extraction brief (specclean lane)

SCOPE MANDATE: touch ONLY files inside /home/pcrec/projects/pcrec/worktrees/specclean/studies/specclean/ (write exactly the one output file your task names). Read anything in /home/pcrec/projects/pcrec/worktrees/specclean. Do not run make, git commit, or write anywhere else (no /tmp). Subagents you spawn inherit this mandate.

TASK: extract every NORMATIVE CLAIM from a slice of a spec document into a TSV — a safety net for a rewrite. The document is /home/pcrec/projects/pcrec/worktrees/specclean/studies/specclean/match_api.old.md (a frozen snapshot; line numbers refer to it).

A claim = a statement of what the generated artifact or the pcrec library API DOES, GUARANTEES, REQUIRES of a caller, or a value/signature/invariant/scope rule (e.g. "<prefix>_search returns 0 on no match and leaves caps untouched", "PCREC_ERR_UTF is -9", "RX_VM_START is emitted on every VM artifact and never on a pure-DFA artifact", "a caller must test the frame size before dividing"). Also include MEASURED facts the contract rests on (kind M), e.g. "measured: a 684-byte subject matches, 686 gives PCREC_ERR_FRAMES".

NOT a claim: pure history ("X was added at abi 40", "this used to read", "before [ABI-NS] it was spelled..."), process/panel/ruling narrative, rationale prose, and pointers ("see tuning.md §2.3"). BUT: inside history blocks, a sentence that states a CURRENT fact (e.g. "-fno-cls-kit denies the whole kit, the atom table included", "the two bits are masked out of rx_info.flags") IS a claim — extract it with kind H. Past-state facts ("through abi 54 the fill ran at the top") are NOT claims. When in doubt whether a statement is still current, include it with kind H and prefix the claim text with "CHECK:".

Granularity: one atomic fact per row; split compound sentences; EVERY row of a value table (value + meaning) is its own claim; a C code block quoting declarations yields one claim per declared symbol/field/macro value; for a stamp macro, its scope rule (which artifacts carry it), its type (token/count/mask), whether it has an rx_info mirror, and what a consumer may / may NOT conclude are separate claims. Aim for completeness over brevity — a missed claim defeats the purpose.

OUTPUT: studies/specclean/claims_<PARTID>.tsv (in the worktree above), tab-separated, NO header row, columns:
  id <TAB> old_line <TAB> kind <TAB> claim
id = <PARTID>-NNNN (zero-padded sequence), old_line = the line number where the claim's sentence starts, kind = N (normative), M (measured evidence), H (current fact found inside a history block). claim = a self-contained paraphrase in present tense, one line, no tabs, naming the entry/macro/field explicitly (never "it"). Keep each claim under ~300 chars.

Read your slice carefully in full (Read tool, offset/limit, ~300 lines at a time). When done, reply with the row count and a count by kind. Then END.
