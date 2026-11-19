# defscope — the scope of a default, every option attacked alike (lane report)

EXPLORATION, rules nothing (owner, COND-FAMILY 2026-11-16 21:49: "Default-scope: is that oddity the only thing against
it? I'd like a lane to consider the options. See if either choice has problems."). Deliverable:
`docs/design/condition_kind.md` Part III (the note's own revision; Parts I-II kept as delivered, the header names the
three parts). Evidence: `docs/dev/lanes/defscope_evidence/` (`defscope_options.py`, `defscope_options.out`,
CLAUDE.md). No edit to `predicates_draft.md` (rev 22) or to any ruling.

## STATE AT HANDOFF

- Branch `lane/defscope`, cut from main @ dc23763d4; the tip is the last commit on the branch.
- Delivered: Part III of `docs/design/condition_kind.md` (III.0-III.8) and its header line; `defscope_evidence/`
  (script, forward output, CLAUDE.md); this report and its history-index line in
  `docs/dev/history/claude_md/docs__dev__lanes.md`. `docs/design/CLAUDE.md` unchanged (the note's role is unchanged).
- PREMISE TEST passed: from `$PCREC_TMPDIR/scratch/defscope/`, lane condkind2's commands (`rev22_ref.py`, then
  `condkind2_nomark.py`) reproduced the committed `condkind2_nomark.out` (ORDER aside; `diff` empty).
- Rulings file `docs/dev/lanes/defscope_rulings.md`: re-read before each commit and before this report: EMPTY (no R-n
  applied).
- Nothing built; `make` not run. Every run under `timeout`, from the scratch dir, each under a minute.

OWED: none.

## THE OPTIONS

In the owner's model (a statement over the source; `P & c` = `select * from (P) t where c`; absent = NULL; a default
= COALESCE) the scope is where the COALESCE sits:
- (a1) PER CONDITION: a where-test COALESCE, its own `$` included (rev 22 as written, with (e2.1)).
- (a2) PER ENTRY: the default fills its label's slot in the test that names it; a `$x` always reads the row; a record
  is exactly the AND of its entries. (The lane's statement of (a) without the manager's (e2.1).)
- (b) WHOLE STATEMENT: a select-list COALESCE LIFTED to the statement's base; one value per label (a second is an
  error). Statement = the program after inlining named programs (macros expand per use), each complemented operand
  its own statement (b1) or receiving the outer defaults (b2).
- (c) POSITIONAL: the model read literally (`(P where c1) where c2`): the default reaches later conditions only. The
  SQL model alone gives (c), not (b): (b) needs a lifting rule.
- (d) per record / joint = (a1).
- (e) DECLARED at the label's definition in the pattern: one value for every program on that pattern.
- (f) tests local, `$` reads the statement's default (review r30 I's option (ii)).

## PROBLEMS OF EACH

The full battery table is Part III.2 (every cell a run count and witness). The worst of each:
- (a1): two different defaults for one label are legal: `(h = 0: <5) & (h = 9: >7)` over `/a(?<h>\d)|b(?<k>\d)|c/`
  holds on the 11 h-absent subjects (`c`) though no value fits both; record vs `&` split 9 of 110 (`-1`); a default
  does not follow its label into a later reader (`when`'s consequent 45 vs 54, a computed label 100 vs 110, a named
  program's reuse 3 vs 14).
- (a2): the split is 0 of 110 (the cross-label question is the joint `((a = 0, b): a < 10 & b > a)`, 54); the
  two-defaults oddity (11 of 21) and "does not follow its label" stay; reverses the manager's default-reaches-dollar.
- (b): ADDING A CONDITION ADMITS: `(h: <5)` holds on 5 of 21; add `(h = 0: <9)` (which alone admits all 21) and 16
  hold; 1,666 of 68,328 (program, added condition) pairs admit (0 under (a)); Part II's "never admits" (0 of 11,388)
  was run with a local default. Also `S & q1` and `S & !q1` both hold on 11 of 21 (b1), or a complemented program reads
  its context (b2); reuse of a named program under another default is an error (15,460 of the 68,328 pairs); an
  unmarked condition's answer moves with a default elsewhere (5,618 of 44,946 cases); computed labels (110 vs 100)
  and the zero-pass row (310 vs 300) need rules.
- (c): `&` stops commuting: 771 of 6,300 two-condition cases move when swapped (rev 22 §2.2 says the order never
  matters); a later default is silently dead; 3,421 of 68,328 admit when the added condition is written first.
- (e): one declaration per pattern reproduces 266 of 339 programs (73 need a value their pool-mates do not); no
  condition keeps "absence fails" beside a declared default (`(h: <5)` with h declared 0 holds on 14).
- (f): one label has two values in one statement: `(b: >$a) & (a: <10) & (a = 0: <10)` on `-1` FAILS (`$a` reads 0,
  the test reads absent); adding `(a = 0: <10)` to `(b: >$a)` admits 9 of 110.
- Rewrite of Part II's 339 programs: (a) 336, (b) 334 (not the one-witness pair, which needs `h = 1` in one condition
  and `h = 8` in the other), (c) 334 in every order, (e) 266, (f) 336; no sentinel needed under (a) or (b) (0).
- "ALL" (Part III.3): A2, "every pass passes c, none needed" (SQL's ALL), equals the intent "every hit's g is `a`,
  possibly none" on 0 of 127 (as rev 22's sentinel spelling; the plain condition 7, the set complement alone 94: rev
  22's own engine-run numbers reproduced); A1 (= c) retires `all`. Recommended A2, the manager's to restate (no owner
  word needed).

## RUNS

From `$PCREC_TMPDIR/scratch/defscope/` (W = the worktree root):

    timeout 300 python3 -I W/docs/dev/lanes/condkind_evidence/rev22_ref.py rev22_ref.tsv
    timeout 900 python3 -I W/docs/dev/lanes/condkind2_evidence/condkind2_nomark.py rev22_ref.tsv > premise.out   # premise: diff vs committed .out empty
    timeout 900 python3 -I W/docs/dev/lanes/defscope_evidence/defscope_options.py rev22_ref.tsv > fwd.out
    DEFSCOPE_SWAP=1 timeout 900 python3 -I W/docs/dev/lanes/defscope_evidence/defscope_options.py rev22_ref.tsv > swap.out
    diff <(grep -v '^ORDER:' fwd.out) <(grep -v '^ORDER:' swap.out)           # 0 lines: SWAP-IDENTICAL
    DEFSCOPE_SABOTAGE=1 (forward and swapped) -> diff 46 lines ((b) evaluated positionally in engine order: e.g. record vs `&` 0 vs 9, admits 1,666 vs 3,354)

`fwd.out` is committed as `defscope_evidence/defscope_options.out`; every count quoted is from it after the swap run
printed the same lines. Not quoted: the output's "35 / 15" count of LOCAL rewrites repeating a default (it counts the
first rewrite found, not a minimal one).

## QUESTIONS FOR THE OWNER

One, in Part III.5 with its full option-by-problem table; a reply either way wanted.
- **default-scope** (what a default IS: a value for one test, or the label's value in the statement). Example:
  `(h = 0: <9) & (h: <5)` on `c` of `/a(?<h>\d)|b(?<k>\d)|c/`: per test FAILS (as `(h: <5)` alone), whole statement
  HOLDS (adding a condition let a subject in). LEANING: per test, per-entry form (a2): order-free, never admits,
  record = `&` exact (0 of 110), read a condition alone. Cost: two different defaults for one label stay legal (11 of
  21); a default does not follow its label into `$`, computed labels or `when`'s consequent (the joint condition is
  the spelling); the manager's default-reaches-dollar reverses.

## LEFT OPEN

- A warning for two different defaults on one label in one statement (under (a)): not designed.
- (b)'s two open definitions (computed label from the coalesced or raw value; the zero-pass row) counted, not chosen.
- Searched mode of a default: unchanged, not re-run.
- `$` populations: one pool (AB, 110); (e) has no spelling and was run as "the program's written values declared".
- No critic round run (the manager launches it).
