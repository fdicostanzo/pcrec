# predspec6 report: predicates_draft.md rev 6, the type picture folded (design only)

## STATE AT HANDOFF

STATE: done. Branch `lane/predspec6`, from main 41ee4641b. Deliverable: `docs/design/predicates_draft.md` rev 6
(changelog entry first) and this report. Design text only: nothing under `src/`, `cli/`, `lib/`, `memfn/`, `tests/`
or `docs/spec/` touched; COND-FAMILY.md and plan.md not edited. Rulings file `docs/dev/lanes/predspec6_rulings.md`:
empty at every checkpoint; last R-n applied: none. Validation: `make test-plan-lint` in the worktree (checks passed:
2, failed: 0); the pre-commit staged checks passed. Nothing OWED.

Premise test held: `grep -n 'the type picture' docs/design/plan_row_bodies/COND-FAMILY.md` printed one line (846);
the draft's changelog said rev 5. "CF:n" = line n of COND-FAMILY.md at 41ee4641b (879 lines); the ruling was
appended after line 845, so every rev 5 cite is unmoved (`git diff 7da9272b2 41ee4641b` on the file has one hunk,
`@@ -843,3 +843,37 @@`). Ruling points: header CF:846, owner's correction CF:855, (1) CF:858, (2) CF:860, (3)
CF:863, (4) CF:866, (5) CF:873, the manager's TO CHECK list CF:876.

Size: `wc -lc docs/design/predicates_draft.md` = 1,624 lines / 146.6 KB (rev 5: 1,437 / 125.1 KB). Most of the
growth is §13's seven new items and the §5.4 grammar table; no trimming pass was done.

## RULINGS FOLDED

| record line | ruling point | spec section(s) |
|---|---|---|
| CF:858 | two value kinds (rx, macro); a condition is a macro; "filter" is a role; a binding names whatever its expression is (isodate is an rx, CF:855) | §2.1 (rewritten), §2.2 (`!B` a macro), §3.5 (array of MACROS), §5.1 (hole kinds), §14 (no third kind), §13 C19 RESOLVED, O40 lean now follows from the ruling |
| CF:860 | one input rule: a call fills parameters, `&` fills the one subject slot; condition / transform / section defined by which inputs are open | §2.1, §2.3, §2.7, §5.2 |
| CF:863 | comma = "next entry", never logic; `[ ]` any one entry, `( )` all together; `=` labels an entry; `:` constrains an existing label | §5.4 = THE grammar summary (table + entry extent); §3.1, §3.2 (multi-index reading), §3.5, §4.1, §0.1 L3/L23/L47, §13 C5 narrowed, C8 restated, O30 RESOLVED |
| CF:866 | a record is never a value; only in a call (against parameters; a call = the macro applied to ONE record), a condition (against labels; the AND from the record), the left of a binding (design; phase 1 only if needed); the written MAP view, no third view, one-way; the sequence closure not adopted | §5.4, §3.1 (written forms, map literal withdrawn), §4.1, §5.2 (call record, nested-record error), §0.2 (destructuring out: no example needs it), §7 (module kind put in question), §8 (tuple example), §0.1 L43-L46, §13 C25, O41-O47 |
| CF:873 | a search returns an rx: array view = occurrences in order, map view = the search pattern's labels; `d :=` binds the rx, `(x, y) :=` lays a record over its fields | §2.6, §13 C29 (lean A strengthened) |
| CF:876 | the manager's TO CHECK items (not ruled) | §13 O41 (a), C25 + O47 (b), O42 (c); the brief's (d), (e) as O43, O44 |

## EXAMPLES RE-CHECKED

Every §12 case, token by token, against §5.4 (where `,` `( )` `[ ]` `=` `:` may stand) and the two kinds.

| case | verdict | notes |
|---|---|---|
| 12.1 E-JSONL | unchanged | `json.row("ts", json.quoted(...))`: call records, positional; `between("2024-01-01", "2024-03-31")`: call record; `/^${q}$/m`: rx text. The `json := import("json")` and `dates := import(...)` lines read through O46 (what a module is); spelling unchanged |
| 12.2 E-WEEKDAY | unchanged | `join([year = ..., month = /\d\d/ & padded(...), day = ...], sep = "-")`: a `[ ]` array with `=`-labelled entries (group names), each entry running to the next comma (`&` inside the entry, O43), passed to the structural `join`; `sep = "-"` a labelled call entry; `weekday_of($year, $month, $day)` a call record; `(weekday: 6)` a condition record |
| 12.3 E-IPV4 | unchanged | `between(0, 255)` call; `join([octet, octet, octet, octet], sep = ".")`: an array of four equal entries; as an rx it is just `octet`, but `join` reads the spelling (4 entries, §3.4), as in rev 5; `assert := import(...)` via O46; `@assert.some(... & ipv4)` |
| 12.4 E-LUHN | unchanged | no comma outside rx text (`\d{4}(?: ?\d{4}){3}`); `startsWith("4")` call |
| 12.5 E-CAL | unchanged | `days_in($year, $month)` call record; `(day: padded(<=dim))` condition record; `@assert.*` calls |
| 12.6 E-RFC | unchanged | `["Jan", ..., "Dec"]`, `["Mon", ..., "Sun"]`: arrays, any one entry (alternations of names), exactly what is meant; `join([day = ..., mname = month_abbrevs, year = ...], sep = " ")`, `join([wname = ..., rest = textdate], sep = ", ")` as 12.2; `weekday_of($rest.year, ...)` call; `(wname.index: ==wd)` a condition record whose label is a path (`==wd` vs `==$wd` stays C13) |
| 12.7 E-NEAR | unchanged | `within(15, of = "2026-11-14")`: positional then labelled call entries; `param(isodate)`; `join([a = isodate, b = isodate], sep = /\s*,\s*/)` (the comma in the sep is rx text); `days($b) - days($a)`; `(d: between(-15, 15))` |
| 12.8 E-FILE | unchanged | `records(file_text("w.txt", sha256 = "<pin>"), lines)`: nested CALLS (an inner call is an expression, not a nested record); `/^(?<word>[^,]+),(?<w>\d+)$/m` rx text; `word_of(r) := r.word` a definition head (O44 (1)); `each(word_of, rows & (w: >100))`. The library name `records` now collides with the word "record" (O44 (2)) |
| 12.9 E-HTTP | unchanged | `join([name = token, value = fvalue], sep = ":")`; `list_of(header, sep = /\r\n/)`; `occurs.exactly(1, (name: any_case("Host")))`, `occurs.at_most(1, ...)`, `occurs.none((...))`, `count((name: ...))`: a condition written as a call entry passes the condition MACRO (O45); `occurs := import(...)` via O46 |
| 12.10 E-SEP | unchanged | `date_sep(s) := join([year = ..., month = ..., day = ...], sep = s)`: definition head + array + labelled call entry; `each(date_sep, enumerate(/[-\/.]/))` |
| 12.11 E-DEPTH | unchanged | `value_depth(0) :=` / `value_depth(k) :=` definition heads; `/\[(?:${...}(?:,${...})*)?\]/`: the commas are rx text; `json := import(...)` via O46 |
| 12.12 E-CTX | unchanged | `P := /(?<w>\w) (?<x>\w+)/`; `(x: /^S\w*/)`, `(name: /^[A-Z][\w-]*/)`, `(v: ...)`: condition records; `/a${num}/`, `@assert.none(...)`, `padded(/^5/)`, `enumerate(...)`: calls / rx; no comma outside rx text and call records |

Respelled OUTSIDE §12 (the brief asked for §12; these are the other examples the ruling touched): §4.2 `(x = /\d/ |
y = /[a-z]/) & (x: /[0-5]/)` -> `[x = /\d/, y = /[a-z]/] & (x: /[0-5]/)` (the map literal is withdrawn, O42); §8
`lex_ge([major, minor, patch], [1, 4, 0])` -> candidate `version & lex_ge(1, 4, 0)` (C25, O47); §3.1 the map literal
sentence replaced by the labelled array. BROKEN: none.

## CONFLICTS FOUND

No contradiction with an earlier RULED item that could not be reconciled; no section is marked as a conflict. The
places where the ruling met an earlier record entry, and how each reconciles:
- C22 / C8 (RULED, CF:698): "inside a condition literal the COMMA separates conditions ... conjunction = comma". The
  type picture moves the AND from the comma to the record (CF:866 (b)). Every answer is the same; only the
  attribution changes. Reconciled as a restatement (§4.1, O43).
- CF:644 (RULED): "TUPLE CONDITIONS: a LIBRARY macro (`lex_ge([major, minor, patch], [1, 4, 0])`), no syntax". The
  RULED content is "library macro, no syntax"; the example spelling is a placeholder (D193 add. 4) and is the part
  the type picture forbids. Reconciled by keeping the ruling and replacing the spelling (C25).
- CF:608 (Frank's own `assert := import("assert")`) with CF:619 (module = map, a manager LEAN): the binding spelling
  is the owner's; "a map" is the manager's. Under CF:858/866 a module is neither an rx nor a record value. Reconciled
  by O46's lean (a module is a namespace that `:=` names; Frank's spelling unchanged), but this one asks the owner to
  confirm that `:=` may name something that is not a value; if he says a binding names only values, Reading B of O46
  (or a third kind) is back on the table.

## OPEN ITEMS

Each is in §13 with both readings; the lean is mine, nothing decided.
- O41 (brief (a)) `(x)` grouping vs a one-entry record: lean GROUPING in value position; a record is never a value,
  so only the three record positions (call, condition, binding left) have one-entry records, and the position
  decides. §0.1 L44.
- C25 + O47 (brief (b)) tuples: lean `version & lex_ge(1, 4, 0)` as the library shape (call record = the bound
  tuple, subject's labels in group order, count mismatch = compile error); it needs a variable-length call record,
  O47: lean none in phase 1 (use the condition spelling `semver & ((major: >=2) | (major: 1, minor: >=4))`), a
  declared rest parameter later on need. No worked example or library signature needs a tuple or record as a value
  (checked §8 and §12).
- O42 (brief (c)) `[x = /foo/, y = /bar/]` stays as THE spelling of the aligned case; the map literal `(x = /foo/ |
  y = /bar/)` is withdrawn (a record in value position; its one entry would put a label inside a value).
- O43 (brief (d)) the condition binding in record terms: an entry runs to the next comma or close bracket; inside an
  entry `&`/`|` bind tighter than `:` and `=`; answers unchanged; new: `:` outside a record is an error (`P & x: S`,
  `[x: S]`). Lean: adopt as the C22 ruling restated.
- O44 (brief (e)) every other comma: all are call records, condition records, arrays or rx text, unchanged; the
  multi-index is C5 (narrowed: if adopted, `X[1, 3, 5]` = `X[1|3|5]`; `A[i, j]` out, write `A[i][j]`; lean adopt).
  Two places the ruling's position list does not name: definition heads `m(p1, p2) :=` (lean: position (a), the call
  shape that declares the parameters) and the library name `records(...)` colliding with "record" (lean: rename the
  placeholder, e.g. `entries_of`).
- O45 a condition written in value position (argument, array entry, binding): lean it DENOTES ITS CONDITION, the
  macro; the record is its written body; any other record in value position is an error. §0.1 L46.
- O46 what a module is: lean a compile-time namespace named by `:=`, not a value; drop "use a module whole as a
  pattern". See CONFLICTS FOUND for the one owner confirmation it needs.
- Also restated, still open: C18 (named assertions: binding readings out, lean a `name = "..."` call entry), C29
  (`.year` of `x & isodate`: lean A strengthened by CF:873), O40 (number = rx now follows from CF:858; kept open
  because the owner has not said it in so many words).
