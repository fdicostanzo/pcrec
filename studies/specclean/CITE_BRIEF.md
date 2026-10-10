# Citation re-pointing brief (specclean lane)

SCOPE MANDATE: edit ONLY the files listed in your assignment, inside /home/pcrec/projects/pcrec/worktrees/specclean, plus your one log file studies/specclean/cites_<PART>.tsv. Never run make, never git commit, never write /tmp or anywhere outside the worktree. Subagents inherit this mandate.

CONTEXT. docs/spec/match_api.md was rewritten facts-only. Its OLD text is studies/specclean/match_api.old.md (citations made before today refer to it, or to an even older version). The NEW doc has explicit anchors; studies/specclean/ANCHORS.txt lists every anchor with its line and first words. Read ANCHORS.txt fully first, and skim the new doc's headings (grep -n '^##' docs/spec/match_api.md).

YOUR JOB: for every citation of match_api.md in your files, make it point at the right place in the NEW doc.

Citation forms you will meet: `match_api.md:1234`, `match_api.md:1234-1260`, `match_api.md §6.3`, `` `docs/spec/match_api.md` §3.1 ``, `match_api.md's §5.3`, `match_api.md 3.1` / `S3.1` / `SS6.3` (in shell strings), `match_api §6`.

SECTION NUMBERS that still mean the same topic in the new doc (leave such a citation as it is, status VALID): §1, §2, §3, §3.1 (the search entry, its returns/caps rules, the FIND-ALL loop), §3.1.1 (next_pos), §3.1.2 (valid_upto), §3.2, §3.3, §3.4, §3.5 (give-ups across entries / codes propagate), §3.6 (the (?:P)\z idiom), §4, §5, §5.1, §5.2, §5.3 (concurrency, stack headroom/K33), §6 (rx_info fields, the abi rule, flags), §6.1, §6.3 (stamp macros), §7, §8, §8.0, §8.1, §8.2 (pcrec_options), §10, §10.1-§10.4, §10.6-§10.9.

TOPICS THAT MOVED (re-point these, status REPOINTED):
- old §3.1 text about startpos being a character boundary, the K50 guard, -fno-startpos-guard, -fstartpos-guard=align, the offset-0 rule (K73), -futf-check / LB / step-back / order / the D142 clip divergence, "positions the engine generates": now §9 — use §9.2 `#startpos`, `#startpos-align`, §9.3 `#offset-zero`, §9.4 `#utf-check`, `#utf-check-clip`, §9.5 `#engine-positions`. (The find-all loop itself STAYS §3.1 `#find-all`; the K75 aligned advance is in `#find-all`.)
- old §6 text on composition / delivered groups -> §5.5 `#composition`; on the named-group index, sort key, nnames/groups -> §5.4 `#named-groups`; old §6.0 (duplicate names) -> `#dup-name-algorithm`; old §6.2 -> `#rx-info-counts`.
- old §6's `abi` CHANGE LOG (the list of bumps "rx_info.abi was N ..."; old lines 2309-3553) -> docs/dev/history/abi_changelog.md (a record); the abi RULE and the current number -> `match_api.md#abi`.
- old §8.2 text on the encodings (byte/utf8, per-call encoding, PCREC_ENC_*) -> §9.1 `#encodings-compiled`; old §8.2 options struct/flags -> stays §8.2 (`#options`, `#options-flags`, `#options-features`).
- old §9 (provenance / pre-v1 posture) -> `match_api.md#pre-v1` (NOTE: §9 now means encodings, so every old "§9" citation MUST be re-pointed).
- old §10.5 (concurrency of buffers) -> §5.3 `#concurrency`.
- old §3's [OPT-1] tiered-entry cost model -> §10.9 `#tiered-entry-cost`; old §4's "two attempts / twice the budget" -> `#budget-per-call`.
- old header/revision notes, old §3.5's design-vs-shipped history, the verification ledger -> docs/dev/history/match_api_record.md.
- old §6.3 stamp material -> the stamp's own anchor (`#stamp-<name>`, see ANCHORS.txt), §6.3.
- old [ART-SIZE] size-term macros (end of old §10.9) -> `#stamp-unroll-k` / `#stamp-max-emit`.

LINE-NUMBER citations (`match_api.md:N`) ALL get re-pointed: line numbers are not stable. Determine the cited TOPIC from (a) the citing text's own words, and (b) the old doc at that line (studies/specclean/match_api.old.md) — but a citation in a file written weeks ago may refer to an OLDER version of the doc whose lines differed; if (a) and (b) disagree, trust (a). Replace with the anchor form: `docs/spec/match_api.md#anchor` (keep whatever path prefix the citation had; you may keep a §N beside it, e.g. `match_api.md §9.2 (#startpos)` is fine, but the anchor is what must be there). If the cited content is history that moved, point at the docs/dev/history file instead.

HISTORICAL FILES (docs/dev/dev_journal.md, docs/dev/lanes/*_report.md and *_log.md, docs/dev/reviews/**, docs/dev/plan_completed.md, docs/dev/decisions.md, dated design-panel records): re-point when the topic is clear from context; do NOT rewrite the surrounding prose. If the topic cannot be determined, leave the citation unchanged and log it LEFT-UNRESOLVED with why.

CODE AND TESTS: in src/ and lib/ edit COMMENTS only. NEVER change a C string literal in src/ that is emitted into generated artifacts (e.g. text inside pcrec_sb_puts/pcrec_sb_printf/"..." emitted strings): that is an abi event. If an emitted string cites match_api.md, log it LEFT-EMITTED and do not touch it. In tests/ you may change comments and human-readable message strings (bad "..."/ok "..."/SAB_DOC_FIGURE), but NEVER a string some code compares against, greps for, or a test anchor; when unsure, leave it and log LEFT-UNSURE.

LOG: studies/specclean/cites_<PART>.tsv, tab-separated, no header, one row per citation occurrence:
  file <TAB> line <TAB> old citation text <TAB> new citation text (or same) <TAB> status (VALID / REPOINTED / LEFT-UNRESOLVED / LEFT-EMITTED / LEFT-UNSURE) <TAB> short note
Find your citations with: grep -noE "match_api(\.md)?(\`|'s)*[,:]? ?(§|S|SS)? ?[0-9][0-9.]*(-[0-9]+)?" FILE  (and also look for "match_api" mentions with a § a few words later on the same line). Edit with the Edit tool. When done, reply with counts per status and END.

GENERATED FILES: never edit a file that a tool writes (anything under tools/review/out/, docs/measurements/, oracle_store/, a design note's `out/` or `*_measurements/` directory, any `.tsv`/`.txt` probe or census output). Log each of their citations LEFT-GENERATED.

YOUR FILES: the list in studies/specclean/part<PART>.txt (one path per line, relative to the worktree root).
