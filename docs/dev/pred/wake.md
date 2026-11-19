# Predicate-language manager: wake-up brief

Rewritten 2026-11-18 about 20:45 box clock, in flight, by the first predicate-manager session. Committed docs win
on any disagreement.

## What happened this session

- Session up on branch `lane/pred-rev28` (worktree `worktrees/pred`, cut from main f9ee6814e); main ACKed (r52 is
  RESERVED for the rev 28 critic round; no need to ask again).
- Frank ruled NINE questions (all recorded verbatim in COND-FAMILY.md, the entries from "2026-11-18 OWNER,
  discussing hole-reads-capture" to "OWNER RULING — same-name-twice", the end of the file):
  hole-reads-capture (the label; a way to the PCRE capture required), number-domain (canonical), padded-width
  (minimum), hole-flags (a hole takes the flags in force; each literal has its own), flags-propagate (yes, with
  override: NO INHERITED FLAGS reversed), unset-in-hole (no string: a regex that matches nothing), construction-line
  (enumerate), value-test (the `if` was illustrative; `when` applies to `$y`), same-name-twice (error at the
  backreference unless `(?J)`).
- Manager's calls (answer-free, told to him): under-construction-class = its own class; dollar-warning WITHDRAWN on
  his question; lift-order = enumerate's order.
- Recorded, NOT ruled: the label-only group `(?<:x>...)` (his 2026-11-09 proposal, found in POSTFACT.md, libpcre2
  rejects the spelling; predicates_future item 32); `padded(rx, length =, pad =)` names; a provided constant for
  the never-matching regex (naming trap: "matches nothing" also means the EMPTY string in the `when` ruling).

## In flight

- NOTHING running. The draft on `lane/pred-rev28` is REVISION 28.1 (review r52 filed at
  `docs/dev/reviews/2026-11-18-r52-predspec28.md`; lanes predspec28 and predspec281 merged and stopped; evidence
  28 of 28). DELIVERED to main as P-2 in `to_main.md` (status line, proposed skill edits). Check `from_main.md`
  and `git log main` for the merge; after it, cut the next branch (`lane/pred-rev29`) from main, or merge main in.
- padded-order is ASKED and mid-discussion: he asked what the "exact width" part is (answered). New fact from
  predspec281: for an INFINITE argument no single body keeps the argument's order (§2.7), so "keeps order" means
  `padded(rx, n)` is a provided function, not a plain macro.
- ELEVEN owner rulings on 2026-11-18 evening (the record has each); the last, numeral-width: canonical.

## READ, IN THIS ORDER

1. The skill, section 2. 2. COND-FAMILY.md from "2026-11-18 OWNER, discussing hole-reads-capture" to the end.
3. `docs/dev/pred/journal.md` (this session's entries). 4. The draft's §R.8 and R.1.16. 5. `owner.md`.

## The question queue (after rev 28)

0. NEW (owner.md has each in plain words; the runs are in the predspec281 report): padded-order,
   numeral-width (full scope; tell him it was corrected twice), flags-in-filter, flags-scope, class-order,
   dollar-diagnostic (a confirm), number-edges, any-case-body, same-name-count, construction-line (b) finite half.
1. (array-in-hole RULED 2026-11-18: a future direction; sent to predspec28 as R1: verify it in the delivery.)
   @y there and what does that mean?"). Possibly an ideas-file item, not a question.
2. construction-line (b): a READ in a count / class / option position.
3. Open since rev 26.1: plus-operands, other-holes, anything-text, zero-in-sequence, group-truth / pass-table,
   number-in-loop, hit-carry-depth, caller-ambiguous, not-test, condition-group, product-order, conditional-spelling.
4. Whatever predspec28's OWNER QUESTIONS LEFT adds (expected: do the general diagnostics fire on
   `/(?<x>\d+)-/ & ($x & <5)`; a duplicate name arriving through a hole or part).
NOT RULED, his PROPOSALS: arrays written with `|` only; the label-only group. THE SPELLINGS REVIEW (one sitting):
now also the carried-capture form, `padded`'s parameter names, the never-matching constant's name, `(?<:x>...)`.
He has NOT yet checked the ANSWERS CHANGED table (draft R.1.16); rev 28 extends it. Offer it.

## Lessons (cases; rules go to main as proposed skill edits via to_main.md)

- His "I proposed X" was TRUE and lived in ANOTHER row body (POSTFACT.md, 2026-11-09). The record grep before
  answering a recollection covers `docs/design/plan_row_bodies/` and the design notes, not COND-FAMILY.md alone.
- He argues from the type: when a proposed rule keys on "plain text vs pattern" or "value vs regex", expect "under
  one type everything is a regex" and test the rule against it BEFORE proposing (hole-flags split, value-test,
  dollar-warning all fell to it).
- A slug answer that restates the candidate in his words ("i meant what you describe ... as") was taken as a
  ruling WITH the reading told to him; he did not object. A remark after a slug question that does not name the
  slug (three in a row on padded-width) was recorded as observation/lean and the slug put back in one line: he
  then answered by slug.
- The `no_cd_worktree` hook blocks any `cd` into worktrees/: use `git -C` and absolute paths from the first command.
