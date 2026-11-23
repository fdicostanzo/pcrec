# Predicate-language manager: wake-up brief

Rewritten 2026-11-23 at the owner's `/close`, seventh predicate-manager session (two reviews ruled and filed, two
folds, about 20 rulings). Committed docs win on any disagreement.

## State

- Branch `lane/pred-rev28` (worktree `worktrees/pred`), tip = the close commit. Lint 8,502 / 0; `make -s
  test-plan-lint` green.
- ON MAIN (merged by main, P-25 and P-26): everything through zero-open, label-hole-full and closing-own-label;
  reviews r84 and r86 ruled, applied, filed.
- ON THE BRANCH, MERGED, NOT REVIEWED, NOT DELIVERED: lane predfold1123b's fold (tip 3c6462b24 holds it): count-
  unspecified, unspecified-rule, call-forms, repeat-head, binding-as-label, label-doors (the five lines at the
  head of the labels section, one ownership table), the withdrawn reading (a) of label-parameter-omitted. Its
  report: `docs/dev/lanes/predfold1123b_report.md`; evidence `docs/dev/lanes/predfold1123b_evidence/` (18 / 0; 25
  plants caught). The last REVIEWED tip is 7b61fd62a (on main): main must not merge past it until r88 is filed.
- REVIEW NUMBER r88 is reserved by main for this fold (topic predfold1123b). NOT launched.
- No lane, no cron, nothing in the box queue. Every lane of the day is stopped (predfix84, predfold1123, predfix86,
  predfold1123b, both coordinators).

## READ, IN THIS ORDER

1. The skill (main edited it today: P-17..P-26 merged; lanes poll single-process evidence runs with bounded waits).
2. `core.md`, `library.md`, `parked.md` on the branch, in parts (core is past 2,300 lines): the labels section is
   NEW at its head (the five lines, the ownership table).
3. The record from "2026-11-23 MANAGER — review r84 (predspot1122)" to the end (the whole seventh session, about
   50 entries). The rulings, by slug: optional-place (his "Before the colon"; the `?:` operator his lean),
   label-forward, capture-negated (no effect under a negation), zero-in-loop (b), binding-fixed (a principle),
   zero-open (all four), label-hole-full, count-unspecified, unspecified-rule, call-forms (four lines),
   repeat-head (head (i)), closing-own-label, binding-as-label (his four conditions), label-doors (five lines).
4. `docs/dev/lanes/predfold1123b_report.md` (ANSWERS CHANGED; OWNER QUESTIONS LEFT).
5. `journal.md` from "2026-11-23 — seventh session: wake"; `owner.md`.

## NEXT, in order

1. LAUNCH r88: coordinator `crit-predfold1123b` (opus, background; the pcrec-critic skill, design mode), subject
   `lane/pred-rev28` frozen at its tip, scope `git diff 7b61fd62a..<tip> -- docs/design/predicates/`, the record
   range = every entry after "OWNER RULING — zero-open" through "OWNER RULING — label-doors". Denylist as r86's
   launch prompt (the lane reports, docs/dev/pred/, earlier pred reviews, the scratch dirs). Lenses: RULING (diff
   each ruling's ASKED statement against the documents: the r86 lesson), EXAMPLES / mode closure with the
   EXPANSION drill, FIX-INDUCED + general form, a NAMES grid over the new ownership table (every cell: one
   sentence, the engine agrees), CHECK adequacy, and the owner's standing item passed on by main: a PARALLELISM
   review of the evidence model (its full run is over ten minutes, single process).
2. Rule r88 (a record entry), ONE opus fix lane (it files the review), merge, lints, P-27 `done:`, tell main.
3. Start step 1 BEFORE the first question to the owner.

## What the fold changed that he has NOT been told in so many words (tell him first)

- `rx.repeat(x, min = 1)` is now EXACTLY one (head (i): max defaults to min); "at least one" is written
  `min = 1, max = _`; the plurals were re-spelled. Follows from repeat-head; worth one line to him.
- The library under binding-as-label: `peek(A)`, `atomic(A)`, `hits(A)`, `occurrences(A)`, `when(A, ..)`,
  `identity(A)` REFUSE the argument's name (`A.d`), because a body that LISTS its spot has made a label (my reading
  (b), not ruled); the reads are `peek.d`, `hits.hit.d`, `when.h`. Slug list-is-label: ASK.
- A body using its argument both alone and labelled: `A.d` now reads the ALONE spot (slug both-uses); placed twice
  alone: the last mention (slug pair-twice-alone). Both my readings: ask or confirm.
- The lane refuted two lines of my spot-read-name working (written before condition 4 existed); neither is in the
  documents.

## The question queue

FIRST: **list-is-label** (above; it decides six library reads). Then both-uses, pair-twice-alone (one question).
Then **capture-in-set** (a request inside `|` / `&` of a set: my leaning a compile error for now).
Then: optional-entry-edges (the optional entry on a joint or a value: errors for now by his ruling; candidate (b)
breaks the record identity on `,9`); optional-label-general (his FLAG, open, his two leans its state);
owner-reads-blank; the three flags questions of r84 (options-position: his own words "in future bindings" answer
the position half: say so, do not ask it; option-hole-explicit; options-reach-constants); from the play-out: a
map written in place, a user macro taking a macro (budget or kinds), keywords before positionals (ruled no for
now in call-forms line 2); the optional-member idiom and duplicate keys (library statements, mine to write);
a label pre-defined as a symbol (his "maybe"); `hide` / `identity` as provided names; macro types / declared
labels; count-several; group-truth; every-pass-spelling; number-in-loop; not-test; condition-group; tuple-parts
(now with a second client: a tuple spread over a call), default-imports, export-choice, any-case-body.
THE SPELLINGS REVIEW grew: `?:`, `l:`, `_:`, `l = ts:` (a CALL spelling), `@x.year`, `capture("name")`,
`B(d=isodate)`, the unspecified mark, a compile-time conditional's `?` `:` against `?:`, `padded_to`.
For a pcre2-reader, not him: the members of `(?i)k` per mode; what a by-name read returns for a duplicate name.

## Lessons (cases; the rule-shaped ones went to main in P-26 and are in the skill)

- A fold brief QUOTES each ruling's ASKED statement, edges included; my summary of a ruling is not a source
  (r86 A1, A8 were my summaries; predfold1123b was briefed the new way and refuted two of my own lines).
- A lone underscore VANISHES in his chat UI: fenced code blocks, or the word "underscore" (memory saved).
- "I believe" / "I suppose" from him is a belief: CHECK THE RECORD and show him what it reverses before taking it
  (closed-argument (a) today; it ended in binding-as-label, his own better rule).
- His one-line questions on a question keep dissolving it (two-sources: "isn't the A.h not visible bare?"):
  before asking, apply the ruled sentences literally to the example and see whether anything is left to ask.
- When he asks for a restatement, give the rule in one quoted sentence, then ONE program that shows every line.
- A lane that says "the run will notify me" is about to idle: tell it at once to poll with bounded waits (three
  nudges today); the skill now carries the rule for briefs.
- Lanes echo their hand-back as a late idle notification after the merge: say "an echo, nothing new", once.
