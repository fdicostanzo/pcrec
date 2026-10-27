# ic1badvice report: the `once` refusal says whether its fix changes what the pattern matches

## Summary
Frank's ruling ("go with 3 ... the user could use the assistance") is built. The `once` refusal now comes from ONE declared first-match table in `src/opt/callout.c` (`co_culprit_rows`). The table has one row per culprit kind: lazy quantifier, quantifier, alternation, subroutine call, non-atomic lookahead, non-atomic lookbehind. Each row carries the construct's name, its clause, its fix and a text for each of the three verdicts on that fix. The verdict answers one question for every kind: would sealing this construct, `(?>X)` in its place, change any match? It answers in one of three ways:

- `that does not change what it matches` (PROVEN SAME);
- `that loses a match (offset 0 of "S"); drop `once` to keep it: the site then fires on each retry` (PROVEN CHANGES, with a witness subject the compiler built and checked);
- `that may change what it matches` (UNPROVEN).

A lazy quantifier is offered no seal. Its advice is to drop `once` or rewrite.

Acceptance does not change: the reading rule still decides which sites are refused. The verdict runs only when a message is wanted, which means a `once` refusal or `--emit-ir`'s note. An accepted compile never runs it. No emitted byte moves: `scripts/emit_sweep.py --ref 7033296a1` gives c-default/c-vm/facts/composition/stderr/dumps movers=0. The only movers are the 12 callout patterns' `--emit-ir` notes, and those are the new text.

The check has 24 rows and 31 fixes, the manager's 13 probe fixes included, all run against libpcre2. Every printed verdict agrees with what the fixes actually match. All seven new sabotages go red.

## Advice table
`co_culprit_rows` (first match on the node kind and its sub-kind: `!u.rep.greedy` or `u.look.behind`):

| row | name | fix | verdicts |
|---|---|---|---|
| A_REP lazy | the lazy quantifier | drop `once` (the site then fires on each retry) or rewrite: X++ is greedy and (?>X+?) keeps only its shortest run | none: no seal offered |
| A_REP | the quantifier | make it possessive (X++) or use (?>...) | same / changes / unproven |
| A_ALT | the alternation | wrap it in (?>...) | same / changes / unproven |
| A_CALL | the subroutine call | wrap it in (?>...) | changes / unproven (never same) |
| A_LOOK ahead | the non-atomic lookaround (keeps INNER live) | use (?=...) or wrap it: (?>(?*...)) | same / unproven (never changes) |
| A_LOOK behind | the non-atomic lookaround (keeps INNER live) | use (?<=...) or wrap it: (?>(?<*...)) | same / unproven |

All the seal rows share their verdict texts today (`CO_SAME`/`CO_CHANGES`/`CO_UNPROVEN`). The columns stay per row, so a row can say something different later.

The texts are short because a refusal must fit `pcrec_error.msg[256]`, a fixed public ABI field. The first wording was 270+ bytes and was truncated mid-verdict. `co_site` now computes the room the head leaves. `co_culprit` drops the witness clause (never the verdict) when the whole message would not fit. Example: a 100-character pattern still says "that loses a match", without the subject.

FINDING, fixed: the old lookaround fix text offered `(?!...)` as a replacement for `(?*...)`, but that is the NEGATION. The fix is now `(?=...)` (`(?<=...)`) or `(?>(?*...))`. The spec table is corrected to match.

## Verdict source
`co_seal_verdict(w, c)` returns SAME when the proof below holds. It returns CHANGES when the witness builder finds a subject, and UNPROVEN otherwise. If both the proof and the witness fire, that is an internal error: they are two independent computations of one fact.

- PROVEN SAME, quantifier and alternation: this is the free discharge's own proof (`pcrec_poss_survey`, the possessify §2.2 verdict that `pcrec_discharge_atomic` uses), asked about a HYPOTHETICAL cut. `co_seal_same` rewrites the culprit in place for the survey and then restores it:
  - a quantifier becomes `A_ATOMIC(rep)`, i.e. `X{m,n}+`;
  - anything else becomes `A_ATOMIC(A_REP{1,1}(X))`, which matches what `(?>X)` matches, so the exact-count arm answers it (a unique-iteration body has one way to match).

  Every non-consuming check site is blanked to `A_EMPTY` for the survey. The comparison is about the pattern with every check passing, and a site in the follow is otherwise opaque to the survey, as `\b` is. The survey declines calls, so a call is never SAME.
- PROVEN SAME, non-atomic lookaround (manager ruling R1): the proof built here. A lookaround consumes nothing, so a retry into it reaches the continuation at the same position, and the continuation already failed from there. The retry is invisible when the body holds:
  - no live capture (`pcrec_has_live_capture`);
  - no `\K`;
  - no callout site;
  - no call (the callee can hold any of these).

  This is checked by `co_look_retry_inert`, an exhaustive no-`default:` switch. A backtracking verb has no producer, and a new node kind is a compile error there.
- PROVEN CHANGES: `co_seal_witness`, a bounded builder. It applies only when the whole pattern is one line of single characters: `P X R`. P and R are classes, read through groups, atomic groups and never-run groups; check sites count as passing, `^`/`\A` may come first and `\z` last. X is the culprit, whose ways must be class sequences:
  - an alternation's branches;
  - a greedy quantifier's counts, from most down;
  - a call stands for its group's body.

  The builder makes the subject `p W r`: a later way W as written, each character picked to also fit the earlier way it competes with. It then evaluates the sealed attempt, which takes only the first way that matches. The subject is a witness only when that sealed attempt fails. As written, the attempt matches by construction.
- UNPROVEN: everything else. The STOP-RULE write-up for calls follows (R1: calls stay UNPROVEN). A call SAME proof would need the survey to analyse the callee's body under the call SITE's follow, sealed as `(?>body)`. The K93 call-site contexts already compute that follow (`cc_join`). What is missing is a survey entry that reports a hypothetical cut on a callee reached only through the call, plus the capture-transparency of a call (`pcrec_has_live_capture`'s A_CALL arm) so that captures set in the callee do not count. The probe's `(?&w)@b` with `w=a+` would then read SAME.

## Probe rows
The manager's 13 fixes, with libpcre2's relation (searches from every start, subjects over the row's alphabet up to length 5) and the printed verdict. `@` is `(?C"x,once")`:

| pattern | fix | libpcre2 | printed verdict |
|---|---|---|---|
| `a+@ab` | `a++`, `(?>a+)` | differs (`aab`) | loses a match (offset 0 of "aab") |
| `a+?@b` | `(?>a+?)` | differs | lazy: no seal offered |
| `a+?@b` | `a++` | same | lazy: no seal offered |
| `a*?@ab` | `a*+`, `(?>a*?)` | differs | lazy: no seal offered |
| `(?:a\|ab)@c` | `(?>a\|ab)` | differs (`abc`) | loses a match (offset 0 of "abc") |
| `(?&w)@ab`, w=a+ | `(?>(?&w))` | differs (`aab`) | loses a match (offset 0 of "aab") |
| `(?*(a+))@\1ab` | `(?=(a+))`, `(?>(?*(a+)))` | differs | may change (live capture) |
| `a+@b` | `a++`, `(?>a+)` | same | does not change |
| `(?:a\|b)@c` | `(?>a\|b)` | same | does not change |
| `(?&w)@b`, w=a+ | `(?>(?&w))` | same | may change (calls stay UNPROVEN) |
| `(?*a+)@a+c` | `(?=a+)`, `(?>(?*a+))` | same | does not change (R1 proof) |

No printed verdict contradicts libpcre2. The only gaps are UNPROVEN rows whose fix is in fact harmless (`(?&w)@b`, `a+@a*b`, `(?:a|ab)@b*c`, `(?*a+%)@a+c`, the call-in-lookaround row), and the check shows them as such.

## Tests
- `tests/callouts/advice_check.py` (+ `advice_drv.c`) is arm 7 of `run_callouts_tests.sh`. It has 24 rows and 31 fixes. Per row it checks four things:
  - the refusal names the construct and the row's verdict, and the `--emit-ir` note is inside the refusal;
  - each fix compiles with `once`, and no anchored attempt fires the site more than once;
  - each fix's matches against the as-written pattern (callouts removed), by libpcre2 through co_oracle, an oracle that shares no code with the analysis, match the row's pinned relation;
  - the PRINTED verdict holds whatever the row declared: a printed SAME must have every fix equal everywhere, and a printed witness must match at 0 as written and not with the fix.

  A declared reach set fails when a row kind stops reaching a verdict. Reached: quantifier same/changes/unproven; lazy noseal; alternation same/changes/unproven; call changes/unproven; lookaround same/unproven.
  - Standalone `python3 tests/callouts/advice_check.py`: 120 passed, 0 failed (~3 s).
- Arm 5 rows re-worded: the lazy row names "the lazy quantifier" and "drop `once`", and the lookaround fix texts are the new ones.
- `make test-callouts` (run_callouts_tests.sh, all seven arms, on the R1 head): 101 passed, 0 failed, 0 skipped. `tests/codegen/run_ir_listing.sh`: 164 passed, 0 failed.
- `tests/codegen/manifests/ir_listing_baseline/3ed51727.ir` (`(a+)(?C"q")b(?C7)`) is re-pinned. Only its two note lines moved, by design.
- Sabotages S1670-S1676, each planted into a scratch archive of HEAD with only advice_check run. All went red:
  - S1670 (always SAME): 27 FAIL, 12 of them the reality check;
  - S1671 (no witness): 9;
  - S1672 (survey sees sites): 3;
  - S1673 (lazy row lost): 2;
  - S1674 (false witness): 6, one a call row whose fake witness libpcre2 refutes;
  - S1675 (lookaround ignores captures): 3;
  - S1676 (lookaround ignores sites): 1.

  S1665 and S1666 are re-aimed onto the new lines. Fields are valid for all 9, and REACH_ONLY reads 9/9 reached. The full mech rows are owed in the job.
- Spec: `match_api.md` §11.8¶3 (table: lazy row split out, lookaround fix corrected, pointer to ¶3a), the new §11.8¶3a (the warning that a fix can change matches, plus the three verdicts and what each means) and §11.8¶3b (when each is said). `ir_listing.md` §3.7¶2 points at it, and so does `docs/design/inline_c.md`. `make test-spec-history`: green.
- `make strict`: clean.

## STATE AT HANDOFF
Rulings file: R1 applied (the lookaround proof is built; calls stay UNPROVEN; the witness builder is approved and every printed subject is one the test runs). Branch lane/ic1b, commits from 2137b8cc3 on, over 7033296a1. Light validation ran under the box lock before 00:05: `make strict` clean, `make test-callouts` 101/0/0, `run_ir_listing.sh` 164/0, emit_sweep movers=0 on every emitted stream. OWED, queued with not-before 2026-10-27T12:00: 560-ic1badvice-test (build, strict, the movers census vs the merge-base 9e0500443, full make test), 561-ic1badvice-mech (39 rows incl. S1670-S1676), 562-ic1badvice-axes.
