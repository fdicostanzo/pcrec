# Predicate-language manager: wake-up brief

Rewritten 2026-11-19 (box clock, about 23:50), at /close of the third predicate-manager session. Committed docs
win on any disagreement.

## State

- Branch `lane/pred-rev28` (worktree `worktrees/pred`). Main merged P-14 (74f70152e: seven rulings folded, review
  r61 filed and applied). AFTER P-14 the branch carries three more HAND FOLDS, not yet through a critic round:
  flags-in-filter (both sides inherit), its confirmation flags-before-and ("the environment of the hole sets the
  default options for the expression inside"), and flags-warning (row `pcrec.flags.filter`). P-15 is the close
  notice and names them. NOTHING running; no crons; every lane and coordinator stopped. Lane worktrees predloop,
  predasc, predfix61 are merged (prune is main's, promised for the morning with the P-14 skill edits).
- The language is defined by `docs/design/predicates/` (core, library, parked, each with `_details.md`); lint
  `python3 -I scripts/pred_doc_lint.py` (5,267 checks, 0 failed at close: RUN IT BEFORE NAMING A TIP). The record is
  `docs/design/plan_row_bodies/COND-FAMILY.md` (each entry has a `tags:` line).
- Reviews of this work: r54, r56, r57, r59, r60, r61 (`docs/dev/reviews/2026-11-19-r61-predfold1119.md`; its PLAN
  residuals with triggers are in the file: one piece for the label namespace and one for captures is the shape of
  the NEXT document pass).

## READ, IN THIS ORDER

1. The skill, section 2. 2. `core.md`, `library.md` whole, `parked.md` scanned. 3. The record from "2026-11-19
OWNER, on bare-condition-labels: a bare condition in a hole is the same condition just after the rx literal" to
the end (this session). 4. `journal.md` from "2026-11-19 (box date) — third predicate-manager session". 5.
`owner.md`. 6. r61's review file (residual list, and RULING.md's ruling table in its directory).

## Ruled this session (all in the record and the pieces)

- bare-condition-labels: a bare condition in a hole sees the labels VISIBLE in the surrounding rx, each as it
  stands at the hole; unset the first time through a loop; a name no group carries is a compile error.
- looped-warning: the warning on labels that can repeat is REMOVED (reverses "looped-compare: warn").
- hole-export: a part's public labels pass out of a binding through a hole and the sequence operator alike; a `_`
  part label or `[_ = A]` still closes them (that clause is MY reading, marked).
- array-scope: the array of a label is "by the scope of the entire rx"; a part label limits it (his `x.@a`).
- class-positions + quantified-order: a lift is the nested loop over each operand's `enumerate`, first operand
  outermost, for every function; PCRE's priority order inside a quantified operand; a class enumerates LOWEST TO
  HIGHEST (he ruled "descending" then reversed it the same evening); nothing sorted unless the user sorts. So
  `\d + 1` is `1|2|..|10` and bare SEARCHED `x10` gives `1`; between `\b`s it gives `10`.
- flags-in-filter / flags-before-and: the hole's environment sets the default options for the expression inside;
  the sides of an `&` take the flags FIRST (`[a-z]x & [A-Z]x` is nothing alone and matches under `(?i)` in a hole).
- flags-warning: warn at the hole "when it works" (the sides-first result differs from the expression alone with
  the flag on its result); never where the expression reads `$x`.
- Not rulings: `longest_first(X)` is MY placeholder for his requested shorthand of
  `sort(X, by = "length", order = "desc")`; `lengthSorted()` was his idea.

## The question queue (one per turn; grep the record AND read the same-day later entries first)

In the order I would take them: class-value (what "lowest to highest" is for a class that is not digits; reading
today ascending codepoint; quick); the four from r61: flat-read-outside (his "I can't access x y z flat because
it's ambiguous and therefore an error" against the rules, where a flat read across `|` is legal: he never answered
my correction), bare-nested-scope (lexical or composed rx for a hole's readers when its literal is itself
inserted), array-vs-passes (do `some` / `count` / `occurs` / `h[k]` read the array of settings or the passes),
class-hole-order (a class-member hole's values under a lift); then the older queue: group-truth, number-in-loop,
zero-in-loop, caller-ambiguous, not-test, condition-group, tuple-parts, default-imports, export-choice, call-forms,
every-pass-spelling, any-case-body (held by me). `scripts/entry -g . -p predicates --state open` lists the pieces
(15). Older, not yet pieces: hit-carry-depth, conditional-spelling, the `r`/`a` flags, sequence-operand flags.
NOT asked (his direction on macros): limited, between's body, list_of, param, within, upperStart. His PROPOSALS not
ruled: arrays written with `|` only; the label-only group. THE SPELLINGS REVIEW (one sitting) is still owed.
Manager's calls owed: warning names; whether `pcrec.label.unset` also fires on an always-unset read (r61
GENERAL-10's side question).

## Owed before the next delivery

A critic round on the three post-P-14 hand folds (ask main for the number first), with the readings listed in
their record entries tested: a binding inside a binding in a flagged hole; a bound `&` as a sequence operand at
program level; `m` and `s` under the warning's comparison; compile-time judgements of a binding alone (assert,
enumerate, never-match) against its use in a flagged hole.

## Asked of main (P-14, applied "in the morning")

The [COND-FAMILY] status line; r61's critic-skill changes; my proposed skill rule (a manager fold QUOTES his scope
words and never widens them; a reading listed "for the next lane to test" is folded as a reading); pruning the
three lane worktrees. Check `from_main.md` and `git log main` at wake.

## Lessons (cases)

- My hand folds WIDENED his words three times in one evening ("the whole surrounding rx", "the inside view less
  the private names", "the test can never pass"); r61's answer-level findings were those. Quote his scope words; a
  consequence I derive is a marked reading in the base and an item in `readings:`.
- A hand model runs the model's INTENT: I told him `123` for a lazy + greedy lift from a model that enumerated
  count by count; the lane's mechanical one gave `12`, and the answer moved again when he reversed the class
  order. Anything about ORDER goes through a mechanical model before it is said.
- Before asking, the record often already answers (bare-condition-labels: hit-carry's and pass-start-read's
  witnesses had the shape); ask it as a confirmation with the quotes, and he corrects fast.
- When he restates a rule in his own words, RUN his sentence at the edges (hole last / middle / first) and show
  where it parts; he then says which he meant.
- A proposal of his that collides with a ruled rule: show ONE witness pair (same set, two spellings, two
  answers); he rules in one turn ("That's a good one!").
- A ruling that moves several pieces went to an opus lane each time (predloop, predasc), a single ruling was
  folded by me; the critic round then found more in my hand folds than in the lanes' work.
- A fold that supersedes a lane's rule leaves that lane's committed evidence red (predloop's model): mark its
  citations superseded in the same fold.
- Lanes: NO BACKGROUND JOBS, runs under 110 s per command (a sabotage loop gets batched); never `--no-verify`;
  never `git reset --hard`. A lane's hand-back and idle notices can arrive long after its merge: check, do nothing.
