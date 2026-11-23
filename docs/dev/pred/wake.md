# Predicate-language manager: wake-up brief

Rewritten 2026-11-23 at the owner's `/close`, sixth predicate-manager session (a discussion session: no lane ran).
Committed docs win on any disagreement.

## State

- Branch `lane/pred-rev28` (worktree `worktrees/pred`); main merged in 2026-11-23 (lint 7,049 / 0 then;
  `make -s test-plan-lint` green). On main already: everything through P-21 (default-export, export-list).
- ON THE BRANCH, MERGED, UNDER REVIEW, NOT RULED: lane predspot's fold of five rulings of 2026-11-22 (argument-default,
  wrapper-export, transform-export, program-options, hole-flags). REVIEW **r84** (number from main; round dir
  `$PCREC_TMPDIR/scratch/crit-predspot1122/`: `review.md` 270 lines, `.coord/process.md`, critic texts in `review/`):
  its draft was NOT read or ruled this session. NOTE: today's argument-label ruling WITHDRAWS two readings that fold
  printed (argument-default readings (a), (b); two-sources' first shape): rule r84 with that in hand; some of its
  findings on those pieces are overtaken.
- IN THE RECORD ONLY, NOT FOLDED: from 2026-11-22 late: capture-export, zero-condition-binding, the spelling notes
  (`[a = A]` as the label set, `[ab = (B | A)]`, `${=rx}`, the third small form). From 2026-11-23: everything below.
- No lane, no cron, nothing in the box queue. P-23 in to_main.md is a NOTICE (array captures touch [CAPTURE-ARRAY] /
  [ARRAY-CAPTURE]); the close notice is P-24.

## READ, IN THIS ORDER

1. The skill, section 2. 2. `core.md`, `library.md`, `parked.md` (this session read core's first half whole and the
rest by heading + statement; library.md and parked.md were NOT read: read them). 3. The record from "2026-11-23 OWNER,
on label-name-hole as first put" to the end (about 25 entries, one day). 4. `journal.md` from "2026-11-23 — sixth
session: wake". 5. `owner.md`. 6. r84's round dir.

## Ruled 2026-11-23 (all in the record; NONE folded)

- THE LABEL PARAMETER (his "lets tentatively work with it": a WORKING DIRECTION, then built on by rulings): a macro
  takes a label, `A(l:) := /(?<:${l}>\d+)/`, `A(l:, B) := [l = B]`; the caller writes the new name (`A(x:) & (x: 5)`),
  so label-reference is met with no source. Same label twice: the standard rules (his observation; run).
- label-parameter-omitted: `_` is the unspecified label (`row(_:, "level", ..)`); no argument is omitted under the
  current call rules; label args are not special by position or requirement. IDEA to park: the empty position
  `row(,"level", ..)`.
- label-parameter-default: yes (a label may be an optional keyword parameter); spelling LEAN `l = ts:`.
- label-kinds: one mark, one meaning (the SETTING kind); the REFERENCE kind (a path to an existing label) is for
  natives, "off limits for users until we see a valid, safe set of rules for it". His `A(x:) := (x: < 2100)` of the
  22nd is the reference kind: it waits.
- capture-twice: (a) the same-label-twice rules (my "error at the second request" withdrawn).
- capture-name: (a) the last step with an optional rename; then OVERTAKEN in shape by the set-side form (below).
- array-capture: yes: the single request gives the LABEL's value (last mention; after a loop the last pass's own
  value, unset on `3;;`), `@x` the ARRAY of settings, UNBUILT. capture-as-pcre (his "perhaps") dropped;
  capture-loop-value CLOSED as the label. The seam (a one-literal program returns PCRE's carried value) is to be STATED.
- argument-export: yes (taken from his "this aligns with my understanding"; told to him): a caller's label on a spot
  holding the caller's in-place argument reads it by the inside rules (`ts.year` in place is legal; from outside
  `line.ts.year` is not: default-export). A BOUND argument seals unless it exports.
- label-in-argument: a label sent inside an in-place argument is ok and passes `_` ("an accepted backdoor into the
  inner pattern- which is almost the whole point").
- argument-label: yes: a label the caller WRITES in its own text inside an argument (a part label, a group of an
  in-place literal, a sent label) is the caller's own, set where the body places the template (once / twice = the
  same-label-twice rules / never = the never-pass warning). His ruled error `B(A) & (A.d: ..)` stands.
- optional-label: yes: `(h?: S)` holds when h is absent or in S (= a default inside the set, member unnamed). THE
  CAPTURE SHAPE IS NOW SET-SIDE: `(h: capture("name"))` requires the label; `(h?: capture("name"))` if present;
  `rx & capture("name")` the stretch (`capture("name")` = `anything` with a request). It REPLACES the morning's
  `capture(path)` operand (that was his LEAN, capture-place) and the `name =` keyword.
His LEANS / not ruled: early capture "no crime"; `l = ts:`; the default way over new syntax ("i don't like adding
syntax and semantics if i don't have to").
My corrections on the record: "ts.year is a compile error as the rules stand" (over-claimed; withdrawn); the
hole-named-label proposal (set aside by the label parameter); one run line written before its run was read
(correction entry appended).

## NEXT, in order

1. RULE r84 (record entry "MANAGER — review r84"), reading each finding against today's withdrawals.
2. ONE opus fix lane for r84 (files the review as `docs/dev/reviews/2026-11-22-r84-predspot1122.md` + directory +
   index line; the spelling notes of the 22nd). Brief pattern: the predfix83 brief; deliver + empty rulings file
   written into the worktree BEFORE launch; `scripts/lanewatch --follow NAME`. Merge ALONE, lint, plan-lint,
   TaskStop; a real `done:` in to_main.md; SendMessage main.
3. ONE opus FOLD lane (ask main for the review number first), pieces: core/operators/bindings/label-variables (the
   label parameter: setting kind, `_`, optional, sent in an argument, the backdoor); core/holes/name (takes a label;
   the `n := "d"` example re-spelled; the k-restrictions proposal is MOOT for labels); core/labels/paths/
   argument-default, two-sources, closed-argument, call-prefix (argument-label; readings (a), (b) withdrawn);
   core/conditions/form + defaults (optional-label; its edges are my proposal: `?` on a joint label, on a value,
   inside a group question = errors for now); lib/structural/capture + add-on, core/labels/export statement 5,
   capture-export, caller-ambiguous, labels-vs-captures (the set-side request; capture-twice; the array request,
   unbuilt; the seam); zero-binding; lib/json sketch (the record has the current program); parked: the empty argument
   position, the reference kind for users. MANAGER READINGS TO TEST are marked in each record entry of the day.
4. Evidence: the day's scratch models are in `$PCREC_TMPDIR/scratch/pred/` (label_name_hole, label_param,
   label_param_twice, msg_two_forms, optional_label, jsonl_exercise): hand-lowered; the lane rebuilds them mechanically.

## The question queue

FIRST: **optional-label-general** (his flag): is `h?` a special form or the general case of an expression left of
`:`; `(h+: blah)`. My note: as a value `$h?` gives the empty text on absence, so `($h?: <5)` fails where `(h?: <5)`
holds; examine with the array spelling (`@x`), which also wants the left side; how the ARRAY capture is requested in
the set-side shape. Then: what he meant by threading the label to `string` (my `body` sketch "was not what i was
thinking"; ASK, do not guess again); the optional-member idiom (`(row(..) | anything)`); duplicate keys; a label
pre-defined as a symbol (his "maybe"); a capture request under `NOT` / `!` (an error: my proposal); what is left of
ambiguity-per-name (macro-name prefixes with several calls: probably only bodies' own fixed labels now).
Older queue unchanged: two-sources' second shape; `hide` / `identity` as provided names; `@options` details; macro
types / declared labels; count-several; zero-in-loop; group-truth; every-pass-spelling; number-in-loop; not-test;
condition-group; `\k<x>` to a label-only group; tuple-parts, default-imports, export-choice, call-forms,
any-case-body. THE SPELLINGS REVIEW (new today: `l:` at a head and a call, `l = ts:`, `_:`, `@x.year` against
`x.@a`, `h?:`, `capture("name")`, `B(d=isodate)` for `B([d = isodate])`, the empty position).
For a pcre2-reader, not him: the members of `(?i)k` in libpcre2 per mode; what a by-name read returns for a
duplicate name (I inferred it from the backreference run; unverified).

## Lessons (cases; rule-shaped ones go to main as proposed skill edits in P-24)

- PASTE run output; never pre-write a run line into the record and run after (one wrong line today, corrected).
- A conclusion carried over from before a ruling changed its premise is a new claim: re-derive it (the JSONL
  finding "labels cannot be exported from inside an argument" was false under the label parameter; he caught it by
  asking "show me why").
- My readings of a ruling that EXTEND it to neighbouring cases (argument-default (a), (b)) are where he later says
  "that was about X, not Y": mark the extension as such when first told to him, with the case it does not cover.
- He prefers reusing a form that exists (defaults, `_`, same-label-twice) over a new one; lead with the existing
  form that already answers, then the shorter spelling of it.
- His questions on a question ("where does row() use the name?", "show me why") usually dissolve it: answer the
  literal question first, with the text, before defending the leaning.
- A discussion session this long (about 14 rulings) leaves a large unfolded backlog: next time start the r84 ruling
  and its lane BEFORE the first question, so lanes run while he answers.
