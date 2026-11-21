# Critic compA findings (round r59 preddoc3)

## Findings


### COMPA-1  CONFIRMED   severity: doc   effort: M
where: parked_details.md (all 39 entries); record 1433 (first-rest PARKED), 1514 (modifier-lift), 1474 (default-set), 1544 (zero-pass-record), 1585 (label-twice "unofficially parked")
what: parked_details.md carries ZERO `rulings:` items and 38 of 39 empty `slugs:` lines. Every owner ruling that PARKED an idea (or ruled the part that stays in the language while the rest is parked) is reachable only as prose copied from the ideas file under `history:`, never as a `rulings:` item with a record title. Use 2 of the format ("every ruling bearing on a piece is reached from the piece, and from the SLUG he answered under") fails for the whole parked file: `entry first-rest`, `entry modifier-lift`, `entry zero-pass-record` resolve nothing by slug.
evidence: `grep -c` of rulings items per file (census script, appendix A): core_details 209, library_details 46, parked_details 0. `grep -cE '^slugs: *$' parked_details.md` = 38 of 39 entries. Example parked/ideas/first-rest: `slugs:` empty, `rulings:` empty, the owner's words "Let's park first/rest but keep it in the wings ..." only inside history (record 1433 "2026-11-16 OWNER RULING — first-rest: PARKED, kept in the wings").
proposed fix: for each parked piece whose ideas-file STATUS names an owner ruling or remark, add the `rulings:` item (date, verbatim words, record title) and the slug (first-rest, modifier-lift, default-set (record sense), zero-pass-record, retire-paused, label-twice, match-context (explainer), mark-in-none (macro-warning), whole-text/atomic, rx-module, array-in-hole `${@y}` ...). Appendix B lists the slugs.

### COMPA-2  CONFIRMED   severity: doc   effort: M
where: core/conditions/form, core/conditions/defaults, core/diagnostics/warnings (row `pcrec.default.unused`), library.md lib/.../between (tuple bounds); record 1441, 1474, 1483, 1503, 1362
what: the 2026-11-16 joint-condition rulings whose content is LIVE in the base files are cited by no `rulings:` item and no later cited entry supersedes them: set-arity (1441: "Set arity: yes. It's clean" — the tuple set behind the joint entry `(h, m): R` in core/conditions/form), default-set (1474: "We can punt, as you say, and throw an error" — core/conditions/defaults says "A default is one string; a default of several strings is a compile error", citing only default-scope and colon-scope), unset-component / default-unused (1483: "unset-component: yes", "default-unused: agree" — the absent-label-fails rule and the `pcrec.default.unused` warning, whose row cites only "the accepted list"), two-orders (1503: "keep both", the whole-tuple vs per-part compare), tuple-value (1362: "I am ok with the tuple as a value").
evidence: census appendix A, missing rows 1362, 1441, 1474, 1483, 1503. core_details.md core/conditions/defaults `rulings:` = default-scope + colon-scope only (lines 665-667); core.md line 474 states the default-set rule.
proposed fix: add the five rulings items to the pieces that state their rules (form: set-arity, record-is-product already there; defaults: default-set, unset-component; warnings: default-unused; between: two-orders; whichever piece holds the tuple value: tuple-value), or, if the one-type ruling (match-is-rx) superseded any of them, say so in a `rejected:`/history line naming that cited entry.

### COMPA-3  CONFIRMED   severity: doc   effort: S
where: record 1949 "2026-11-16 OWNER RULINGS — drop-mark, default-value, source-row; default-scope to a lane"; and the five rulings it retired: 1727 match-context, 1739 zero-pass-empty, 1759 domain-scope, 1776 mark-narrows, 1817 mark-in-none
what: drop-mark ("Drop-mark: yes": the optional mark is OUT of the language) is the entry that retires five earlier owner rulings, and it is itself cited nowhere in `rulings:`; so the five retired rulings fail both arms of the test (not cited, and their superseding entry not cited). default-value ("Default-value: yes": a default may be any text) and source-row ("Source-row: yes") in the same entry are likewise uncited. The documents mention drop-mark only in parked_details history (5 times, as "drop-mark 21:49").
evidence: census appendix A; `grep -c drop-mark core_details.md library_details.md` = 0 / 0.
proposed fix: cite 1949 on the piece that says an absent label never matches / a default stands in (core/conditions/two-valued or core/conditions/defaults) with `rejected:` lines for the optional mark (by owner ruling, drop-mark) naming the five retired slugs.

### COMPA-4  CONFIRMED   severity: doc   effort: S
where: lib/search/anchored and core/filters/and (library_details.md line 323; core_details core/filters/and); record 1048 "2026-11-15 CORRECTION and RULING (Frank, to session 133, ~21:20)"
what: lib/search/anchored's ruling for EXACT ENDS cites the quote "Anchored def: agree." from the 20:55 entry, but the record's 21:20 entry CORRECTS that entry: "his "Anchored def: agree" answered the manager's EARLIER statement ... his words: "The anchored comment was to a previous statement. What does new anchored suggestion mean."", and it is the 21:20 entry that records "RULED = `anchored` has EXACT ends". The correcting entry is cited by no `rulings:` item anywhere (the anchored entry calls it only "the correction entry" in a `rejected:` line). Its part (b) is also an owner ruling with no citation: "&: both sides filter and warn if anchor. Agree but test if it makes sense" (both operands of `&` are filter roles; an explicit anchor in an operand warns) — the content of core/filters/and and the `pcrec.anchor.whole` row.
evidence: census appendix A row 1048 missing; library_details.md 323 and 328 quoted above; record 1048-1062.
proposed fix: on lib/search/anchored add the 1048 item ("The anchored comment was to a previous statement..." with record "2026-11-15 CORRECTION and RULING") and mark the 20:55 quote as the corrected one; add 1048 (b) to core/filters/and (and the warnings row).

### COMPA-5  CONFIRMED   severity: doc   effort: S
where: core/diagnostics/warnings row `pcrec.anchor.whole` ("the accepted list"); record 1103 "2026-11-15 RULING — the anchor warning keys off the ROLE, never a transform's name" and 1150 "2026-11-15 RULING — the anchor warning has no exemption for macro-body text"
what: two standing owner rulings that define WHERE the anchor warning fires ("padded is a simple macro so the warning shouldn't key off of the name"; "warn-in-macro-body: yes") are cited nowhere; library_details mentions warn-in-macro-body only in a history line ("rev 15, warn-in-macro-body"). No later entry reverses them (the 11-17 warnings ruling accepted the list; it does not restate the role rule). The slugs warn-in-macro-body / anchor-warn-scope sit on no `slugs:` line (appendix B).
evidence: census appendix A rows 1103, 1150; `grep -n "keys off\|macro-body" *_details.md` = only library_details 334 (history).
proposed fix: cite both on core/diagnostics/warnings (or a split piece for the anchor warning) with slug warn-in-macro-body.

### COMPA-6  CONFIRMED   severity: doc   effort: M
where: the paused field-reference / tuple-compare direction; record 1223 (tuple compare names), 1250 (tuple-arg-order), 1268 (no bare field reference), 1304 (label-section: the sigil), 1329 (looped-compare: warn), 1336 (OWNER DIRECTION — PAUSE), 1560 (library-not-syntax), 1573 (retire-paused)
what: eight owner entries, six of them rulings, form one chain that ends in retire-paused ("agree to split. But the pause on ^ is indefinite and requires real value other than 'override a users own *'"): the `lex_` names, the argument order and the first-library slot RETIRED, the other-side sigil PAUSED indefinitely, the 11-14 tuple-as-library-macro ruling WITHDRAWN by name (library-not-syntax). None of the eight is cited in any `rulings:` field, so neither the retired rulings nor their superseding entry reach the documents; and the paused sigil, a direction NOT in the language with an owner-stated trigger, has no parked piece of its own (parked/ideas/field-count is only one use of it; its `rulings:` and `slugs:` are empty). Also 1268 (1) "definitely not a bare reference" is a standing refusal with no `rejected:` home.
evidence: census appendix A; `grep -c "retire-paused\|library-not-syntax\|label-section\|tuple-arg-order\|looped-compare" core_details.md library_details.md` = 0; parked.md has no sigil piece.
proposed fix: a parked piece `parked/ideas/other-side-sigil` (or `parked/directions/...`) citing 1304 and 1573 with the trigger in his words; cite 1560 and 1573 on the library piece that took the tuple compare (`between` with tuple bounds) as `rejected:` lines (lex_ names, arg order — by owner ruling, retire-paused); cite 1268 (1) as a rejected candidate on core/conditions/form.

### COMPA-7  CONFIRMED   severity: doc   effort: S
where: lib/search/occurrences (library_details 392), core/labels/labels-vs-captures (core_details ~447-454), core/holes (edge-assertion history, core_details 919); record 2004 all-question, 2323 last-pass-default, 713 Q1 foundation
what: three standing rulings are named in prose but never cited as `rulings:` items: all-question ("all-question: retire"; REVISITED, not reversed, by the named every-pass form per the draft R.9), last-pass-default ("last-pass-default: regex. I want to have the method of achieving the alternative meanings defined and tested" — narrowed, not reversed; its second sentence is a standing instruction no piece carries), Q1 foundation ("1. agree": edge assertions in set positions are a compile error; NARROWED by hole-reading, widened by operand-context, not withdrawn). Each appears only as "by owner ruling — <slug>" in a `rejected:` line or in history.
evidence: census appendix A rows 713, 2004, 2323; core_details 447 "regex's carried value ... (last-pass-default: regex) — by owner ruling"; library_details 392 "`all` was retired (all-question)".
proposed fix: add the three items (verbatim, record titles) to the pieces that rest on them.

### COMPA-8  CONFIRMED   severity: doc   effort: S
where: core/conditions/form + core/values/one-type (core_details 589, 759); core/principles/regex-default; core/labels/export; parked/ideas/capability-optins; record 1832, 1912, 2188, 2160, 1384, 3513
what: owner entries whose heading is not "RULING" but which RULE, DIRECT or ANSWER A SLUG, cited nowhere:
 - 1832 "OWNER DIRECTION — conditions are their own kind" ("conditions are the bastard child of macros and patterns. What they need is to be themselves") and 1912 "OWNER ANSWER, CORRECTED BY HIM — condition-kind". core_details 759 says the opposite of the record: "the condition and the macro stay their own kinds (the lane predspec27's reading; no line of the rulings names them) — UNTESTED"; core_details 589 calls "a condition is a value of its own kind" the draft's reading. The owner's direction names it.
 - 2188 "OWNER DIRECTION — decide the open choices by a REGEX MODEL where one exists": his method, the ground of regex-default and of every "regex model" reading; core/principles/regex-default cites only the 11-17 model remark and regex-settles.
 - 2160 "OWNER — a library element beyond the user's level is an ERROR" (the record says "RULED for libraries"); no piece cites it (capability opt-ins are parked with empty rulings).
 - 1384 "tuple-anywhere: yes" (slug answered); 3513 "OWNER confirms the reading of `[_ = A]`" ("RULED, the reading confirmed"; core/labels/export cites the 3500ish clarifying entry, not the confirmation).
evidence: census appendix A, tier-2 list (uncited OWNER entries, method in appendix); core_details.md 759 quoted.
proposed fix: cite 1832 (class: DIRECTION) and 1912 on the piece stating a condition is its own kind and remove "no line of the rulings names them"; add 2188 as a `principle` item (class: DIRECTION) to regex-default or a new principle; cite 2160 on the capability piece; 1384 and 3513 on their pieces.

### COMPA-9  CONFIRMED   severity: design   effort: S
where: core.md core/modules/positional (`ruled 2026-11-16`) vs parked.md parked/ideas/tuple-apart; record 1411 "2026-11-16 OWNER — reaching a tuple's parts is REOPENED; he wants the "use it whole" case heard"; draft §13 line 9128 (**tuple-parts** OPEN)
what: core/modules/positional is status `ruled`, citing only the 09:50 "Yes" (record: "2026-11-16 OWNER CONFIRMATION — a tuple on the left of a binding takes it apart"). Eight minutes later the owner REOPENED it: "Nothing is set in stone. I'd like to hear it out. So It's the set that makes it an item so you can't break it apart without changing its meaning", RECORD "(1) the 09:50 confirmation is NOT a closed ruling: both positions ... are to be laid out and he decides". The frozen draft keeps it OPEN as **tuple-parts** ("asked again when a use appears"). The slug tuple-parts is on no `slugs:` line, the reopening entry is cited nowhere, and the same construct is simultaneously a parked idea (parked/ideas/tuple-apart, "A binding that names the parts of one tuple value"). The 2026-11-19 MANAGER withdrawal entry (record 5474), which the details entry leans on, also never mentions the 09:58 reopening.
evidence: core.md 1051-1059; core_details 1422-1432; record 1411-1419; draft 9128-9132; slug census appendix B row tuple-parts (homed: none).
proposed fix: status `open tuple-parts` on core/modules/positional (body: the two positions, his reason against access), cite 1411 and 1420; or, if the manager reads the 09:50 Yes as standing, put the question to the owner (tuple-parts) rather than mark it ruled; reconcile with parked/ideas/tuple-apart (one home).

### COMPA-10  CONFIRMED   severity: doc   effort: S
where: core_details.md slugs lines of core/principles/regex-default (and 6 more pieces citing regex-settles), core/labels/labels-vs-captures, core/conditions/form, core/conditions/defaults, core/conditions/two-valued, core/filters/complement, core/model/match, core/labels/paths; library_details lib/search/anchored, lib/modifiers/json-quoted, lib/modifiers/unpadded, lib/modifiers/any-case
what: 15 slugs whose ANSWER is quoted in a `rulings:` item (the slug word is inside his quoted words) on a piece, yet the slug is on NO `slugs:` line anywhere, so `entry <slug>` resolves nothing and use 2 ("reached ... from the SLUG he answered under") fails: regex-settles (quoted on 7 pieces, e.g. core/principles/regex-default whose slugs line is "branch-scope branch-order sql-picture"), after-loop-read (core/labels/labels-vs-captures), colon-scope (form, defaults), default-scope (defaults), label-twice (form), record-is-product (form), not-is-complement and mark-in-none (two-valued, complement), row-is-match (core/model/match), read-out (core/labels/paths), anchored-in-hole (lib/search/anchored, core/holes/pattern), cut-json-quoted, cut-unpadded, primitive-transforms (any-case).
evidence: slug census appendix B, column "quoted-on"; e.g. core_details 583 `"condition-not : yes allow not"` homes condition-not, but 582 `"colon-scope: yes with refinement ..."` on the same entry leaves colon-scope off its `slugs:` line (577: "condition-not condition-or dollar-condition label-twice-warn").
proposed fix: add each to the `slugs:` line of the piece that decides it (regex-settles to core/principles/regex-default, the others to the pieces named; a slug quoted on two pieces goes on a `shared:` line or on the deciding one).

### COMPA-11  CONFIRMED   severity: doc   effort: M
where: all three details files; draft §13 and the changelog; record
what: 34 question slugs asked of or answered by the owner (record and/or the frozen draft's question lists) are on no `slugs:` line AND are not quoted in any `rulings:` item: set-arity, tuple-value, tuple-anywhere, tuple-compare, tuple-names, tuple-arg-order, tuple-parts, two-orders, modifier-lift, unset-component, default-unused, joint-loops, pairing-loop, optional-as-loop, zero-pass-record, zero-pass-empty, match-context, domain-scope, mark-narrows, mark-under-not, mark-range, label-section, looped-compare, library-not-syntax, retire-paused, macro-arguments, bound-reference, reference-index, one-witness, default-reaches-dollar, drop-mark, all-question, last-pass-default, warn-in-macro-body / anchor-warn-scope. Most belong to the 11-16 joint-condition / optional-mark era; they are RULED, RETIRED or PAUSED, not dead questions, and several still carry live rules (COMPA-2) or a parked direction (COMPA-6). For the retired ones the documents give no slug route to "why is the optional mark not in the language" (drop-mark) or "why no lex_ names" (retire-paused).
evidence: slug census appendix B (ment = mention counts per file; most are 0 everywhere).
proposed fix: home each: live ones on their deciding piece (COMPA-2), retired ones on the piece whose `rejected:` line records the retirement (drop-mark's five on the defaults/two-valued piece; retire-paused's on the sigil parked piece or `between`), parked ones on their parked piece; draft-only manager questions closed by entailment (one-witness, default-reaches-dollar, mark-under-not, mark-range) on a `shared:` line of core_details or on the piece they were closed into.

### COMPA-12  CONFIRMED   severity: doc   effort: S
where: core_details core/modules/default-set/members (`slugs: default-set`, status `open default-set`); core/conditions/defaults; parked/ideas/default-set; record 1474 vs 5303
what: ONE slug word names TWO different questions. The record's 2026-11-16 **default-set** ("a default of several strings is an error, for now") is RULED and decides core/conditions/defaults (and parks parked/ideas/default-set); the 2026-11-19 manager queued a NEW question under the same word ("the rest of the set is a question for him, **default-set**, not asked now", record 5303) about the default-IMPORTED module set. The documents home `default-set` only on the new question; `entry default-set` therefore lands a reader asking about label defaults on the module set, and the ruled 11-16 answer is reachable by neither slug nor citation.
evidence: `grep -n default-set COND-FAMILY.md` = 1474 and 5303 only; slug homes appendix B.
proposed fix: rename the new question (e.g. default-imports) in the documents and the record's tags, and home the 11-16 default-set on core/conditions/defaults with its ruling item (COMPA-2).

### COMPA-13  SUSPECTED   severity: doc   effort: S
where: core_details core/conditions/defaults (`slugs: nullable-meaning`), core/conditions/pass-start-read (`slugs: ... pass-list-read`)
what: two slugs homed on a piece that does not decide them. nullable-meaning (what a nullable `occurrences` argument means) sits on core/conditions/defaults, whose own readings line admits "nullable-meaning ... is lib/search/occurrences' fact, not this piece's — the slug stays here"; core/diagnostics/nullable-hit and lib/search/occurrences are the deciding pieces. pass-list-read (what `$h` reads AFTER the pattern when h is set in a loop: "unqualified it is the last pass as standard pcre"; then the `$x` ruling) is homed on pass-start-read (a condition read before its group inside a pass), not on core/values/reads (Reading a label), which states the `$x` rule.
evidence: core_details 664, 672, 650, 656; record 2661.
proposed fix: move nullable-meaning to lib/search/occurrences (or core/diagnostics/nullable-hit); move pass-list-read to core/values/reads with its ruling item (record 2661, narrowed by the `$x` ruling).

ERRATUM to COMPA-10/11 counts (appendix B is authoritative): COMPA-10 lists 14 slugs (not 15; `anthing-text` is the owner's typo of the homed anything-text); COMPA-11 lists 35 slugs (warn-in-macro-body and anchor-warn-scope counted separately).

## Appendix A — RULINGS CENSUS (built from the record only; the documents used only for the diff)

Method (re-runnable; scripts in `/var/tmp/pcrec-pcrec/scratch/crit-preddoc3/compA/s/`):
- `timeout 60 python3 -I census.py` parses the record into ENTRIES by the lint's own title rule (a `## `/`### ` heading, or a bold `**YYYY-MM-DD ...**` opener starting a paragraph, joined to its closing `**`, trailing `.` dropped, blanks collapsed): 334 entries. It also parses every `- ` item under `rulings:` in the three details files (255 items: core 209, library 46, parked 0) and takes the cited title from `(record: "` to the last `")`.
- `timeout 60 python3 -I match.py r` applies MY RULE and matches (a citation matches the whole title or the part before its first ` (`, as the lint does).
- MY RULE for a ruling entry: the title contains RULING / RULINGS / RULED (any case), is not a MANAGER entry, and does not disclaim itself ("not a ruling", "no ruling", "not rulings", "not yet a ruling", "nothing ruled", "NOT ruled", "not asked as a ruling", "no owner words"). Tier 2 (method `match.py o`): owner entries whose title lacks the word but which rule, direct or answer a slug, read by hand from the uncited list (COMPA-8).
- The design note's own census said "155 ruling entries"; my rule gives 144 (different rule: I exclude leans/ideas/discussions and MANAGER entries; the difference is not a finding).

COUNTS: expected 144; cited directly 111; held by a later CITED superseding entry 6; MISSING 27.

| record line | entry (short) | disposition |
|---|---|---|
| 713 | 11-14 RULING — Q1 foundation | MISSING (narrowed, not withdrawn) COMPA-7 |
| 1048 | 11-15 CORRECTION and RULING (anchored exact ends; `&` both sides filter + warn) | MISSING COMPA-4 |
| 1103 | 11-15 RULING — anchor warning keys off the ROLE | MISSING COMPA-5 |
| 1150 | 11-15 RULING — no exemption for macro-body text | MISSING COMPA-5 |
| 1223 | 11-15 RULING — tuple compare names | MISSING; supersessor 1573 uncited COMPA-6 |
| 1250 | 11-15 RULING — tuple compare argument order | MISSING; supersessor 1573 uncited COMPA-6 |
| 1268 | 11-15 RULING + IDEA — no bare field reference | MISSING COMPA-6 |
| 1304 | 11-16 RULING — the other-side sigil | MISSING; paused by 1573 (uncited) COMPA-6 |
| 1329 | 11-16 RULING — a compare over looped labels warns | MISSING; moved by 1493 (uncited) COMPA-6 |
| 1362 | 11-16 RULING + REQUEST — tuple as a value | MISSING COMPA-2 |
| 1433 | 11-16 RULING — first-rest: PARKED | MISSING (parked, rulings empty) COMPA-1 |
| 1441 | 11-16 RULING — set-arity | MISSING (live) COMPA-2 |
| 1474 | 11-16 RULING — default-set (several-string default an error) | MISSING (live) COMPA-2, COMPA-12 |
| 1483 | 11-16 RULINGS — unset-component; default-unused | MISSING (live) COMPA-2 |
| 1493 | 11-16 RULING — joint-loops | HELD: reversed for bare joints by after-loop-read / branchings reset (both cited; draft R.9) |
| 1503 | 11-16 RULING — two-orders | MISSING (live) COMPA-2 |
| 1514 | 11-16 RULING — modifier-lift | MISSING (ruled part live; rest parked) COMPA-1 |
| 1544 | 11-16 RULING — zero-pass-record | MISSING COMPA-1 |
| 1560 | 11-16 RULING — library-not-syntax | MISSING COMPA-6 |
| 1573 | 11-16 RULING — retire-paused | MISSING COMPA-6 |
| 1594 | 11-16 RULING — pairing-loop part 1 | HELD (as 1493) |
| 1696 | 11-16 RULING — optional-as-loop | HELD (as 1493) |
| 1727 | 11-16 RULING — match-context | MISSING; retired by 1949 (uncited) COMPA-3 |
| 1739 | 11-16 RULING — zero-pass-empty | MISSING; retired by 1949 (uncited) COMPA-3 |
| 1759 | 11-16 RULING — domain-scope | MISSING; retired by 1949 (uncited) COMPA-3 |
| 1776 | 11-16 RULING — mark-narrows | MISSING; retired by 1949 (uncited) COMPA-3 |
| 1817 | 11-16 RULING — mark-in-none: LEFT AS IS | MISSING; retired by 1949 (uncited) COMPA-3 |
| 1949 | 11-16 RULINGS — drop-mark, default-value, source-row | MISSING COMPA-3 |
| 2004 | 11-16 RULING — all-question: retire | MISSING COMPA-7 |
| 2323 | 11-17 RULING — last-pass-default: regex | MISSING (narrowed, not reversed) COMPA-7 |
| 2423 | 11-17 RULING — labels match every pass ... | HELD: superseded by after-loop-read (cited) |
| 2661 | 11-17 RULING — pass-list-read | HELD: narrowed by the `$x` ruling + `${@y}` (both cited); slug misplaced COMPA-13 |
| 2785 | 11-17 RULING — shared-label | HELD: revised by label-flow (cited) |

Tier 2 uncited owner entries judged to rule/direct/answer (COMPA-8): 1384, 1832, 1912, 2160, 2188, 3513. Tier 2 judged NOT rulings (read): 2557 (he corrected it to "an observation"), 4674 (recollection; record says nothing new ruled), 5087/5108/5119 (doubt/observation; the documents carry the manager's call as `reading`, core/spellings/condition-parentheses), 5179 and 5195-5224 (requests about documents), 5259 doc-shape (form; its language LEAN is cited on lib/control/peek), 5333 (lean). The 11-13/11-14 "(Frank)" entries before the slug era (37 uncited) were NOT checked one by one: population named, not probed.

## Appendix B — SLUG CENSUS (built from the frozen draft and the record only)

Method: `timeout 60 python3 -I slugs.py` collects every bold lower-case kebab token `**slug**` in the draft's changelog (lines 5-662), §R.8 (3096-3558), §R.9 (3559-3735), §13 (7979-9214), and in the record (bold tokens, `(slug X)`, `Asked X`, and `"X:` at the head of his quoted words); then every word on a `slugs:`/`shared:` line of the three details files. The per-slug diff (mentions per file; titles cited; rulings items whose quoted words contain the slug) is the inline python run in the session (re-run: load slugs.json + data.json, as in the finding evidence).

COUNTS: candidate tokens 192; spelling variants of a homed slug or a superseded alias 4 (absents-hold, anthing-text, import-symbol, number-edge) -> 188 questions; homed on a `slugs:` line 128 (plus 3 homed slugs not in my sources: group-truth, inner-label-read, bare-condition-labels — manager slugs after the draft, not findings); NOT homed 60:
- 14 answered and QUOTED in a rulings item but not on any `slugs:` line (COMPA-10): regex-settles, after-loop-read, colon-scope, default-scope, label-twice, record-is-product, not-is-complement, mark-in-none, row-is-match, read-out, anchored-in-hole, cut-json-quoted, cut-unpadded, primitive-transforms.
- 35 neither homed nor quoted (COMPA-11): set-arity, tuple-value, tuple-anywhere, tuple-compare, tuple-names, tuple-arg-order, tuple-parts, two-orders, modifier-lift, unset-component, default-unused, joint-loops, pairing-loop, optional-as-loop, zero-pass-record, zero-pass-empty, match-context, domain-scope, mark-narrows, mark-under-not, mark-range, label-section, looped-compare, library-not-syntax, retire-paused, macro-arguments, bound-reference, reference-index, one-witness, default-reaches-dollar, drop-mark, all-question, last-pass-default, warn-in-macro-body, anchor-warn-scope.
- 11 HELD: numbered-duplicate, sequence-numbers (replaced by number-names, homed); hole-member-kind (folded into value-is-pattern, homed); absent-holds (a DIRECTION superseded by absent-rule, cited on core/principles/no-absence); doc-shape, definition-lane, mark-design, joint-condition (process/exploration slugs, no language piece decides them); condition-kind (answered; its home is COMPA-8's fix); searched-complement (asked 11-16 per record 2000; I did not trace its answer — UNVERIFIED, likely dissolved by row-is-match).
Homed on a piece that does not decide it: default-set (collision, COMPA-12), nullable-meaning and pass-list-read (COMPA-13). Collision found: default-set names two questions (record 1474 and 5303).

## PROBED-AND-HELD
- 111 of 144 ruling entries are cited by at least one `rulings:` item; every one of the 255 citations resolves to a record title (0 unresolved, `match.py u`), agreeing with the lint's L4.
- All 2026-11-19 OWNER RULING entries after the draft (other-holes 4834 through import-several 5451: other-holes, negated-class-hole, anything-text, zero-in-sequence, padded-lazy-sparse, the four import-symbols rulings, import-several) are cited; so are padded-order, flags-scope, class-order, dollar-diagnostic, number-edges, same-name-count, plus-operands. The post-draft timing gap is closed for RULING entries.
- 6 uncited ruling entries are properly superseded by a cited later entry (appendix A HELD rows), and the documents' `rejected:` lines name the supersession for shared-label, pass-list-read and last-pass-default's reading.
- 128 slugs are homed, and spot-checked homes (product-order on core/holes/pattern + count, empty-search-error on core/model/modes, rx-module on core/patterns/sequence, other-holes on core/holes/class, when-peek shared) decide their slug.
- The 11 held slugs in appendix B.
- Correction to appendix A tier 2: doc-shape's peek LEAN is carried on lib/control/peek as a `readings:`/history line (library_details 141, 146), NOT as a `rulings:` item; it is a lean, so no finding.
- Not probed: the 37 pre-slug 11-13/11-14 "(Frank)" entries one by one; verbatim accuracy of quotes (the RULING lens's).

CRITIC COMPLETE
