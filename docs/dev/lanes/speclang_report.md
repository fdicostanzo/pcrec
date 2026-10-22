# Lane speclang — [SPEC-LANG]: pcrec's own definition of its pattern language

Lane speclang, opus, 2026-10-21/22. Branch `lane/speclang` off `62ca83389`.
Docs plus one small check under `tests/`; no `src/` edit (NO BUILD GO).

## Deliverables

- `docs/spec/pattern_language.md` — the language spec, numbered from birth
  (10 sections, 49 numbered headings, 128 labelled paragraphs, generated
  contents). Every accepted construct, its meaning, captures, preference
  order, module gate, refusal shape, engine, quantifiability, per encoding
  and option; §9 lists every difference from libpcre2 it states; §10 is the
  construct index (one line per `--list-syntax` row: syntax, module, section).
- `tests/registry/syntax_index_check.py`, run by `run_registry_tests.sh`
  (`make test-registry`): §10 against `pcrec --list-syntax` (missing, extra,
  module, nonexistent section, duplicate), columns resolved by header name,
  with three planted mutations of the real doc checked first.
- `docs/dev/history/pattern_language_record.md` (the record; nothing to move,
  the doc was born facts-only); entries in `docs/spec/CLAUDE.md`,
  `docs/dev/CLAUDE.md`, `docs/dev/history/CLAUDE.md`,
  `tests/registry/CLAUDE.md`; `tests/spec_history/cite_floors.tsv` row
  `pattern_language 1` (2 citations exist at birth, floor = half, rounded up).

**The name is `pattern_language.md`, not the plan row's provisional
`syntax.md`.** `tests/spec_history/spec_cites.py` reads `<stem>[.md]` followed
by up to eight separator characters and `§N` as a citation of that doc, so the
stem `syntax` turned every "...syntax** | §1.2.4" and "`--list-syntax` (§2)"
in the tree into a citation (one dangling: `docs/design/dd13_format/
format_design.md`, a table row ending "explicit syntax** | §1.2.4"). `language`
collides five times the same way. `pattern_language` occurs nowhere else.
The plan row's `refs:` line still names `docs/spec/syntax.md`; the manager
owns plan.md.

## Step 0: the row against today's tree

The row (filed 2026-10-09) is still accurate: nothing defined the language.
What exists since is pointed at, not restated: `cli.md` §1.8 (the fold per
encoding), §1.9 (UCP sets and refusals), §1.17 (the gate), §1.17.1 (property
names); `match_api.md` §5 (captures), §9 (encodings, startpos); `limits.md`
(budgets, UCP widths, left recursion); `vars.md` (module `vars`);
`registry.md` §2 (the index columns). The numbering convention (specnum) is
new since the row and was adopted at birth. [IFACE-PUSH] orders the docs
pass after the interface push; Frank's "1,2,3 go" (2026-10-21) overrides that
for this row.

## Shape choices (answer-free; taken here, one line of reason each)

1. **Generated vs hand-written: hand-written definition + machine-checked
   index, no generated block.** The compliance page already embeds the
   generated registry index; a second copy would be a second home, and
   generating the definition from the registry would certify the language
   from the thing being audited (DOC-DRV's own argument).
2. **Grammar form: a short EBNF for structure and precedence (§3.1), then a
   table per construct family.** Precedence and the brace-quantifier rule are
   grammar facts; everything else is per-construct meaning, gate, engine and
   refusal, which tables state testably and the registry indexes per row.
3. **D26 tiering: §1.3 states four tiers** (answers exact; acceptance and
   owning module exact; pcrec offset exact; wording loose except the
   `requires module 'X'` and other shape markers of §2.4's seven-shape table).
4. **The check that keeps it true: built (small).** §10 vs `--list-syntax`
   both ways plus module and section; it cannot see whether a semantic
   sentence is true — that is the separate D27 adversarial lane's job.

## Coverage

- `--list-syntax`: **142/142 rows** indexed in §10 with their section
  (103 families). The check passes: `syntax-index: 142 registry rows, 142
  index lines, 49 sections: all agree`.
- Base tier (no registry rows): literals, all character escapes, refused
  escapes (the full a-z/A-Z sweep), `.`, classes (ranges, `]`/`-` placement,
  escapes inside, refusals), quantifiers (forms, brace grammar, limits),
  alternation, groups, nesting limit, `^`/`$`.
- Semantics sections: leftmost-first, preference order, empty iterations,
  captures, engines, give-ups.
- Not restated, pointed at: the UCP set definitions and their refusals,
  the property-name vocabulary, `${...}` grammar, the fold tables.

STOP RULE did not fire: every construct's behaviour was discoverable from the
binary (plus `--list-syntax`/`--explain`/`--list-verbs`/`--list-limits`).

## How the sentences were verified

A probe pair in the worktree's `build/probe/` (gitignored, not delivered):
`pq` compiles a pattern with `build/pcrec` + `tests/harness/driver.c` and
prints every group span, beside `p2`, a 30-line libpcre2 10.46 driver at the
§1.2 option mapping. About 330 pattern/subject cells, in batches under 50
compiles, each checked against the queue for quiet-gated jobs first (none
ran). Plus one byte sweep: 21 sets (`\d \s \w \h \v \N .` and the 14 POSIX
classes) × 256 bytes under `byte`, all identical to libpcre2's (§6.1¶5).
Every example in the doc is one of those cells. Python `re` was not used: no
sentence claims python equivalence.

## Defects and findings (candidate K rows; the manager numbers them)

1. **WRONG ANSWER (tier 1). `(?x)` under `-e utf8` does not ignore Unicode
   Pattern_White_Space.** PCRE2 ignores U+0085, U+200E, U+200F, U+2028,
   U+2029 under `(?x)` in UTF mode; pcrec treats them as literals. Repro:
   `pcrec -e utf8 --pattern $'(?x)a b'` on `ab` → no match; libpcre2
   `PCRE2_UTF` → `[0, 2)`. Same for `$'(?x)a\xc2\x85b'` and U+200E. Under
   `byte`, `\x85` IS ignored by both. Documented in §3.2¶2 and §9 item 7.
2. **Ownership disagreement (tier 2). `(?J)`**: `--list-syntax` says module
   `modifiers` (`built`); the refusal says `inline option 'J' (dupnames)
   requires module 'backrefs'`; `--features modifiers` alone refuses it with
   that text and `--features backrefs` alone refuses with `(?J...) requires
   module 'modifiers'` (both are needed). `--explain '(?J)'` reports
   `agree ok` because it compares the live names to themselves, not to the
   row's module. The compliance page says ownership moved to `backrefs`.
   Either the row or the gate is wrong. §9 item 6.
3. **Rejecting accepted syntax (tier 2). Non-ASCII letters in group names
   under `-e utf8`**: `(?<é>a)` is refused ("subpattern name expected");
   libpcre2 10.46 with `PCRE2_UTF` accepts it. §7.5¶1.
4. **Rejecting accepted syntax (tier 2). Whitespace inside `\x{...}`**:
   `\x{ 41}` and `\x{41 }` are refused ("non-hex character"); libpcre2 10.46
   accepts both. §5.2¶1.
5. Low (wording promises a future that cannot come). `\p{Foo}` and
   `\p{InGreek}` with the module enabled say "module 'unicode-props' is
   enabled but \p{...}: this Unicode property is not implemented yet", for
   names no libpcre2 has (`cli.md` §1.17.1 calls them refused names).
6. Low. A malformed `\p` (no name) under `--features all` says "requires
   module 'unicode-props'" although the module is enabled.
7. Low. The `(*...)` catch-all says `requires module 'verbs'` under
   `--features all` too (shape 1 where every other unbuilt module gives
   shape 2). Documented as the exception in §2.4 and §8.1.
8. Low (usability). `--features` cannot add a module to `std1`:
   `--features std1,quoting` is refused as "unknown module 'std1'", while the
   same diagnostic lists `std1` as a valid value; the way is to spell
   `classes,modifiers,quoting`. §2.3¶2.
9. Low. The `(*UTF)a`/`(*UTF8)a` registry rows read `built` = `unbuilt`, yet
   both compile under `-e utf8`; the built probe runs at `byte`, where they
   are refused by design.
10. Documented divergences, not defects (§9): `(?R)` alone answers no match
    where libpcre2 returns its recursion-loop error (-52); `${...}` outside a
    class is refused without module `vars` although PCRE2 reads it as a
    never-matching `$` + literals; a backreference inside a lookbehind is
    refused (`(a)(?<=\1)`; PCRE2 accepts a fixed-length group reference).

## Compliance page: stale rows found (for the next compliance-refresh)

`docs/pcre2_compliance.md` (last refreshed 2026-09-21) should become the
delta against `pattern_language.md`. Stale on the way: Character types says
`\v` `REJECTED → PLANNED` (built, module `classes`, std1) and `\p{..}`
`REJECTED` (OK-GATED in its own Unicode section); Character classes says
`\Q...\E` inside a class `OK` (it needs `quoting`, not in `std1`: OK-GATED);
Substring scan says `(*script_run:...)` etc. `REJECTED`/`—` while
`--list-verbs` marks them `planned`; Quantifiers' "quantifier on `^`/`$`
`OK`" is ambiguous (`^*` and `a$?` are refused by both; `(^)*` is fine); the
Headline's module list and counts predate `quoting`, `recursion`, `ucp`,
`vars`.

## Validation

- `PCREC=build/pcrec python3 tests/registry/syntax_index_check.py` →
  `syntax-index: 142 registry rows, 142 index lines, 49 sections: all agree`.
  Sabotage, run by hand on copies of the doc: a dropped `\d` line plus a
  `\D` module changed to `misc` → `missing \d` and `module \D` reported,
  rc 1; a section changed to §5.77 → `section (a)` reported, rc 1. The three
  built-in plants (missing/extra/module) pass on every run.
- `python3 tests/spec_history/spec_history.py .` (what
  `make test-spec-history` runs) → `checks passed: 173, checks failed: 0`,
  including `pattern_language.md` clean on all five history markers, its
  numbering, contents and citations. The pre-commit gate passed on every
  commit.
- OWED: `make test` (the check joins `test-registry`), queued as boxqueue
  job `690-speclang-test` on this worktree: make, make strict, perfrun make
  test, red-line grep. Log: `worktrees/.boxqueue/{running,done}/*-690-speclang-test/job.log`
  and `job.log.make`; completion line `== 690 step verdict OK`.

## STATE AT HANDOFF

Doc, check, record, CLAUDE.md entries and cite floor committed on
`lane/speclang`. Rulings file `speclang_rulings.md`: no entries (header
only), re-read before each commit. OWED: job `690-speclang-test`. Next:
the D27 adversarial lane (binary + `pattern_language.md` only); a
compliance-refresh to re-point the page as the delta; decisions on findings
1-4 above.
