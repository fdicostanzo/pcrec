# predspec10 report: predicates_draft.md rev 9 -> rev 10

Lane predspec10 (opus), 2026-11-15, branch `lane/predspec10`, base main 19b44df32. Design document only; no build.
Subject: `docs/design/predicates_draft.md`. Inputs: review `docs/dev/reviews/2026-11-15-r10-predspec9.md` (its
DISPOSITIONS RULED), the owner's COND-FAMILY.md entries CF:962-996, and (via the rulings file, R-1) CF:997-1000 on main.

## STATE AT HANDOFF

- Rev 10 of the draft complete and committed on `lane/predspec10` (WIP commits b75e9977a, c8cdbbbb3, 287289b5e and
  the final commit carrying this report). Not merged.
- Rulings file `docs/dev/lanes/predspec10_rulings.md`: last applied **R-1** (the per-match rule for a label that never
  ran is RULED, CF:997-1000; marked RULED BY ACCEPTANCE in §4.2, §4.3 table, §2.6, §8, L55/L56/L65, O28, changelog,
  §0 rulings table, §15; dropped from the owner questions).
- Also delivered: the critic texts copied to `docs/dev/reviews/2026-11-15-r10-predspec9/` (census, fixA, fixB,
  simulate, verify, process); `docs/dev/reviews/CLAUDE.md` gained the r10 line (one old line moved to
  `docs/dev/history/claude_md/docs__dev__reviews.md` to stay under 12 KB); two sentences in
  `.claude/skills/pcrec-critic/SKILL.md` (hand mapping under FREEZE DRIFT; the simulate lens applies each case in
  the program's REAL MODE).
- `make test-plan-lint` in the worktree: `checks passed: 2, checks failed: 0`.
- Oracles used: Python `re` and libpcre2 10.46 through its public API (scratch
  `/var/tmp/pcrec-pcrec/scratch/predspec10/`); no PCRE2 source read.

## FINDINGS FIXED

Every review id, with where it is fixed (section numbers of the draft).

- SIM-1 (backref/conditional inside a search argument): §2.6 THE TWO ARGUMENT REFUSALS, §0.1 L62, §8, O53.
- SIM-2 (an iteration's labels from PCRE's raw capture state): §2.6 THE ITERATION'S OWN VALUES, §4.3, manager list (6).
- SIM-3 (unscoped `(?s)` gaps leak into the hole): §2.6 scoped body `/(?:(?s:.*?)(?<hit>${x})){${min},}(?s:.*)/`, §8 bodies with `(?:${s})`, §8 status.
- SIM-4 ("as sets both are the values with a substring" false for anchored x): §2.6 scoped to anchor-free arguments; §8.
- SIM-5 (`$` before a final newline): §11 THE FILTERED SPAN (`$` the exact end), §0.1 L63.
- SIM-6 (cases checked whole-subject, not in real mode): §12 REV 10 RE-CHECK, E-HTTP anchored, §0.1 L66, §0.1 MODE OF THE ANSWERS.
- FIXA-1 (transform vs filter modifier): §0.3 glossary, §2.6 status, §2.7 heading and naming rule scope.
- FIXA-2 + CENSUS-10 (`[n]` by position): §3.2 tool 1, §4.3, §5.4 `[ ]` row, §0.1 L64.
- FIXA-3 + CENSUS-1 (`$` on a repeated label, one meaning): §4.1, §4.3 rule, §5.4 `$` row.
- FIXA-4 (destructuring against the argument's groups, not the body's): §0.1 L50, O55.
- FIXA-5 + CENSUS-13 (`count` as entry count): §5.4 `[ ]` row "the entry count", §3.4.
- FIXA-6 (statuses of `count(...)`, `*`/`%`): §12 census rows, §8.
- FIXA-7 (metadata collision still "open"): §3.1/§3.2 tool 4 (ERROR, manager's call), §5.4 status.
- FIXA-8 (O31 "third" rule): O31 "second".
- FIXA-9 (§0.1 STATUS two owners for L53; ERROR missing): §0.1 STATUS rewritten.
- FIXA-10 (n+2 counter cite): §4.3 cites CF:685.
- FIXA-11 (a) "after `.*`" -> §11; (b) O50(c) "never rejects" only with `min = 0`; (c)-(e) §2.6/§5.4 `:` row/E-FILE.
- FIXB-1 (membership extensional, condition reads the spelling): §4.5 new paragraph, §2.2, §3.4, §0.1 L25/L60, SAME rows re-checked in §0.1 STATUS.
- FIXB-2 (boundary stated per match): §4.2 THE BOUNDARY rewritten, §4.3 table, §0.1 L56/L65; now RULED (R-1).
- FIXB-3 (answer move under `contains` one definition): §0.1 L58, §2.6, manager list (8).
- FIXB-4 (two transforms in one chain, `hit`): O55 rev 10 paragraph (readings A'/B'/C', lean A').
- FIXB-5 (hedged words marked RULED): §0 status-mark criterion; "before any build go" now the record's LEAN (§4.5, §4.6, O57).
- FIXB-6 (the independent control's counter source): O57 and §0 standing question 2 (a counting libpcre2 callout, lower bound).
- FIXB-7 (a) O28 lead fixed; (b) O28 lead; (c) §4.4 per-label check restated as a guard; (d) §4.5 IN SEARCH MODE THE CONDITION SELECTS THE SPAN.
- FIXB-8 (PLAN: zero-iteration half too thin): O28 restated; then overtaken by R-1 (RULED, CF:997-1000).
- FIXB-9 (NOTED, general forms): §13 FAMILIES, the two proposals with unlocks, costs and triggers (the first's trigger went the other way; the second's fired, unification the manager's to schedule).
- CENSUS-2 (`${` inside rx text): §11 THE MARKS INSIDE `/.../`, §0 G3 counts, §5.4 preamble and `${ }` row.
- CENSUS-3 (group-name hole position): §5.3, §5.4 `${ }` row, §11 typed positions.
- CENSUS-4 (defaults have no home): §5.2 `name = default` in a head, §5.4 `=` row.
- CENSUS-5 (E-DEPTH's multi-clause form): §7, §12.11 marked NOT YET WELL-FORMED, census row, O21 pointer.
- CENSUS-6 (`=` as let): the one let-style use (`x = /aab|a/`, O58) respelled `:=`; the remaining `name = /.../` uses are array entry names (one meaning, §5.4 `=` row).
- CENSUS-7 (`@warn`/`@export`): §5.1 effect built-ins, §5.4 `@` row.
- CENSUS-8 (`$&`/`$_` reserved with no meaning): §5.1 reservation dropped (D77).
- CENSUS-9 (`:` takes a field path): §5.4 `:` row (label, metadata, iteration index; E-FILE).
- CENSUS-11 ("value" for the filtered text): §0.3 glossary (value vs span); respelled in §0.1 L56/L60/L63/L65/L66, §0.1 mode paragraph, §2.6, §4.5, §4.4, §11, the §0 rulings row. Owner quotations keep his word. Not every one of the 144 remaining `value` words was audited one by one; those left are the kind sense or quotations as far as checked.
- CENSUS-12 ("run-time parameter"): "run-time input" in §0.3, §2.1, §6.1, §11, §12.7, O-list (9 sites).
- CENSUS-14 (`index =` and `label =` collide with metadata; warning names in code): §5.3 `start =`, O55 `hit_name =`, §7.1 warning names as strings.
- CENSUS-15 (ordinal slot ambiguity): §5.3 ordinal passed BY NAME (`ordinal = "i"`), manager list (10).
- CENSUS-16 (`some`/`none` shared names; `@each`): §5.6 note, `@assert.each` lean, O22.
- CENSUS-17 (one meaning per position; `#`): §5.4 header and `#` row.

## RULINGS FOLDED

- CF:962-971: `min` is 0 or 1 (RULED; other values a compile error, LEAN) -> §2.6, §8, L57, O58 RESOLVED; the ambiguity warning only for the author's own text (RULED) -> §4.5, §7.1, O59 RESOLVED.
- CF:972-988 (the five items): reading one hit needs captures (RULED) -> §4.3, O50; ONE measured budget, no thresholds (RULED) -> §4.6, §8, O39 RESOLVED; a count is a numeral string, `even()` applies (RULED) -> §2.1, §4.3 table, §8, O40 RESOLVED; `&` in rx text all or nothing by module/option (RULED) -> §11, §5.4, C23 RESOLVED, G3; whole rx in a hole when off (`${/.../ & blah}`) -> §11, §2.3/§5.1 guard sentences. Manager leans (switch OFF by default, `\&` literal both modes) -> O60 (LEAN).
- CF:989-996: filters anchored at both ends; `contains`/`search` remove it; `^`/`$` in their argument are the span's ends; `contains(/^err/)` = starts with; the `31` example -> §11 THE FILTERED SPAN, §2.6, §8, L17, O49 RESOLVED.
- CF:997-1000 (rulings R-1): a condition on a label that never ran is decided PER MATCH -> §4.2, §4.3, §2.6, §8, L55/L56/L65, O28.
- Review r10 DISPOSITIONS RULED (the manager's picks) -> DECIDED BY THE MANAGER list (5)-(10) in §13, each LEAN (manager).

## EXAMPLES RE-CHECKED

Each §12 case applied in its REAL mode (searched unless the program anchors):
- E-WEEKDAY, E-LUHN, E-RFC, E-NEAR (a)-(c), E-SEP: UNCHANGED (fixed-width or delimited, searched = whole).
- E-CAL: UNCHANGED (isodate is 10 characters, so are the subjects); `isodate := (as in 12.2)` respelled as a comment.
- E-JSONL: UNCHANGED (anchored line by line by its own `/^${q}$/m`); `contains` now exposes `hit`, no condition reads it.
- E-FILE: UNCHANGED (already stated searched).
- E-IPV4: answer ADDED for search mode: `01.2.3.4` -> `1.2.3.4` (beside `256.1.1.1` -> `56.1.1.1`); Python `re` checked.
- E-HTTP: RESPELLED (`block := headers & occurs...`, then `/\A${block}\z/`); unanchored, `Host: a\r\nhost: b` would MATCH `Host: a` (answer moved); anchored, the expected answers hold; a third expectation added.
- E-DEPTH: MARKED not yet well-formed (multi-clause definition, O21); its answers unchanged as text.
- E-CTX-1, E-CTX-7 and the agreeing look-alike: UNCHANGED (reported span is the whole subject); E-CTX-2..6: compile errors, unchanged.
- §0.1 rows: L17, L25, L34 (searched reports `12`), L48-L59 restated; L60-L66 new, each witness run under libpcre2 10.46 and/or Python `re` (greedy a=`12`, lazy a=`1`; `A|B` l=`a`, `B|A` l=`aa`; `contains(/err$/)` on `err\n` true raw, false with `\z`; SIM-2 ovector; scoped search body agrees with the old one on all 7 non-nullable hand-check rows at `min` 0 and 1).

## OPEN ITEMS

Owner questions in plain words, each with an example and the lean:

1. Should the rx-ampersand switch be off by default? Off: a pasted PCRE pattern like `a&b` keeps meaning a literal
   ampersand, and an intersection inside a pattern is written `${/(\d+)/ & <256}`. On: `(\d+)&${ <256 }` works as
   written and a literal ampersand is `\&`. Lean: off by default, and `\&` means a literal in both modes.
2. Told, not asked (confirm you are content): under the one-reading rule, two spellings of the same language can
   answer differently once a condition reads a label. `/(?<a>\d+)(?<b>\d+)/ & (a: "1")` rejects `123`, the lazy
   `/(?<a>\d+?)(?<b>\d+)/ & (a: "1")` accepts it. Lean: accept this as the price of one answer everywhere; the
   ambiguity warning names the label.
3. Two searches in one condition both offer the label `hit`: in `contains("a") & contains("b") & some((hit: ...))`,
   which hit is meant? Lean: an "ambiguous label" compile error that names both, with a per-call hit name as the fix
   when a real case needs both.
4. Should `startsWith`/`endsWith` become `search` with an anchored argument now that your anchoring ruling makes them
   conveniences? `startsWith(x)` = `contains(/^(?:x)/)`. Lean: yes, but only after question 3 is answered, because
   each would then carry a `hit` label.
5. Should a searched program with a count condition warn? `headers & occurs.exactly(1, (name: "Host"))` searched in a
   block with two Host lines reports the shorter one-line span. Lean: no warning yet; write such programs anchored
   (E-HTTP now is), and add a warning only if a real case trips on it.
