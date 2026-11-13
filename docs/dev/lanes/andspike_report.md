# andspike — PCRE2-callout exact-span oracle for X & Y and predicates: report

Lane `andspike`, opus, 2026-11-12, Linux dev box (7700X). Spike only: no
`src/`, `cli/`, `lib/`, `tests/` or `memfn/` edit. Branch `lane/andspike`.
Deliverable: `studies/andspike/` (code, cases, sweeps, committed results).
PCRE2 10.49 (2026-09-28) from the oracle build under `$PCREC_TMPDIR/oracle/`,
used through its installed `pcre2.h` and man pages only (D181: no source read).

## STATE AT HANDOFF

- STATE: done. Every number below is in a committed file under
  `studies/andspike/results/`.
- Rulings file `docs/dev/lanes/andspike_rulings.md`: last entry read and
  applied is R1 (callout test-corpus ideas: FINDINGS F10).
- Premise test passed: `(?:a|ab)(?C1)` from offset 0 of `abc` reports ends 1
  then 2, in that order (`results/cases.txt`, first row).
- Runs: Frank's evening hold was in force for the whole lane (20:53-21:25),
  so every run was ONE niced Python process and no sweep had more than 200
  generated patterns (or pattern triples). The longest run is `sweep.py cross`
  at 136 s, almost all of it in the Python reference matcher (F2). Nothing was
  queued and nothing is owed. Larger sweeps (more patterns, length-6 subjects,
  a 3-letter alphabet) were NOT run. F9 lists them as what a production
  version would run.
- Reproduce: `make -C studies/andspike` (targets `cases predicates cost
  sweeps`); scratch only under `$PCREC_TMPDIR/scratch/andspike/`.

## FINDINGS

**F1. The idea works. PCRE2 plus one end callout is an exact-span oracle,
and X & Y and predicates can be built on it.** The pattern is compiled as
`LEAD (?:X)(?(R)|(?C1))` with `PCRE2_NO_AUTO_POSSESS | NO_START_OPTIMIZE |
NO_DOTSTAR_ANCHOR` (pcre2callout "Missing callouts"). It is matched ANCHORED
at start offset i over the whole subject. A callout that records the position
and returns 1 lists every end X reaches from i, in X's preference order (`ends`).
A callout that returns 0 only at position j answers "does X match exactly
[i, j)?" (`spans`). LEAD is X's own leading start-of-pattern options, such as
`(*UTF)`, hoisted out of the group. X & Y is built two ways
(`studies/andspike/spanoracle.py`):
- **A (`and_sets`).** Our own loop over leftmost starts. At each start, take
  the first end in X's order that Y's `spans` accepts.
- **B (`and_inline`).** ONE unanchored PCRE2 run of X. X's end callout runs
  Y's `spans` as a nested `pcre2_match`, and a leading `(?(R)|(?C2))`
  records the attempt start. PCRE2 itself owns the start loop, bump-along
  and every verb. Nested matching inside a callout works.

Both use the manager's leaning rule: leftmost start, then X's preference
order among the ends Y also accepts. `results/cases.txt` has 61 rows: 51 PASS
against hand-derived values, 0 FAIL, and 10 PROBE rows that record behaviour
the docs leave open. The premise test is its first row.

**F2. Independent cross-checks on the regular subset: 0 disagreements in
64,200 enumerations** (`results/cross.txt`). The run used 200 generated
patterns (depth 2, alphabet {a,b}, `.`, `[ab]`, groups with and without
capture, `|`, and greedy and lazy `* + ? {0,2} {1,2} {2}`). Each was run
against every {a,b} string of length 5 or less, at every start. The oracle's
end list was compared with:
- the end SET from python `re.fullmatch(X, s, i, j)`;
- the end ORDER from `refmatch.py`, my own backtracker, which shares no code
  with PCRE2;
- the end ORDER rebuilt by PCRE2 WITHOUT callouts (`lookahead_order`). The
  k-th end is PCRE2's own match of `(?:X)(?!E1|...|Ek-1)`, where
  `Ej = (?s:.{r})\z` pins a position by the characters left after it;
- for every j, `spans` and its callout-free twin `(?:X)(?=(?s:.{r})\z)`.

Controls (learnings §3: each check must be able to fail):
- `ANDSPIKE_SABOTAGE=order` reverses the list. Over 50 patterns, 6,142 of
  16,050 differ on the two ORDER checks and 0 on the set checks, as designed.
- `drop` loses the last end. 10,138 of 16,050 differ on all five checks.
- The `opt` column (default options vs NO_OPT) cannot catch either sabotage,
  because both of its sides go through the sabotaged code. It shares a
  source with what it controls, so its 0 counts only for what F3 says.

Cost: one pattern took 127 s, and nearly all of that was the Python
reference. For the same pattern on 5-character subjects the oracle took
0.04-0.06 s, at up to 66,694 callouts.

**F3. NO_AUTO_POSSESS is load-bearing for the brief's plain form, and my
recursion guard happens to hide that.** At default options, `a+(?C1)` on
`aaa` enumerates only `[3]`, against `[3,2,1]` with NO_OPT. `[ab]*` gives
`[2]` against `[2,1,0]`, and `(\d+)` gives `[4]` against `[4,3,2,1]`.
PCRE2 10.49 auto-possessifies a repeat that the end callout directly follows,
so callouts do not block it. With the guarded wrapper
`(?:X)(?(R)|(?C1))` the default and NO_OPT lists agreed in all 64,200
enumerations: the conditional group seems to block auto-possessification.
That 0 is a property of the wrapper, not a general fact. A production oracle
sets the three options anyway. The start optimizations are harmless for an
END callout, because every reported end already needs X to match. They
still cost time: `(?:a+)+b` on `a^20` takes 20 ms enumerated with NO_OPT,
while the default first match takes 0.03 ms because it sees there is no `b`.

**F4. The algebraic laws** (`results/laws.txt`). 200 generated (X, Y, Z)
triples were checked over every {a,b} subject of length 4 or less.
- **X & X = X.** `and_sets(X, X)` equals PCRE2's own unanchored search of X:
  6,200/6,200.
- **X & (?s:.*) = X.** Same measure: 6,200/6,200.
- **Distribution.** As sets, `ends(Y|Z) = ends(Y) U ends(Z)` at every start:
  25,800/25,800. X & (Y|Z) equals the leaning rule applied to that union:
  6,200/6,200.
- **A = B.** The two implementations agree: 6,200/6,200.
- **Commutativity.** X & Y and Y & X report the same leftmost START
  6,200/6,200 times, but the same reported MATCH only 5,568 times. **632 (10.2%)
  differ.** The span sets commute; the leaning rule does not, because it uses
  X's order (Q2).

**F5. The hard cases** (`results/cases.txt`). Each is described with the
semantics it forces; the questions are collected in F7.
- **Lookaround reaching outside the span.** The oracle sees the real context:
  `(?<=a)b` & `b` on `ab` = [1,2), and `a(?=b)` & `a` = [0,1) on `ab`
  but none on `ac`. `a\b` and `a$` do not span [0,1) of `ab` in context, but
  do when isolated (`spans(..., isolated=True)` runs Y on the substring).
- **Backreferences.** `(a+)\1` on `a^6` gives ends [6,4,2], and & `a{4}` =
  [0,4). Each operand is compiled alone, so Y's `\1` is Y's own group 1. A
  backreference from one operand to the other cannot be expressed.
- **`\K`.** The pcre2callout page says `start_match` reflects `\K`. In 10.49
  it does NOT, both through the API and in pcre2test's callout display:
  `foo\Kbar` shows start 0 at its end callout. Implementation B records the
  attempt start with its own leading callout, so it does not depend on this.
  The & span is the ATTEMPT span: `foo\Kbar` & `.*` on `xfoobar` = [1,7),
  and `foo\Kbar` & `bar` on `foobar` = none. pcrec's own callout view says
  the same (`match_api.md` §11.3¶4: `caps[0]` is the attempt start, not a
  `\K`-moved one).
- **Empty matches** behave: `(?:)|a` gives ends [0,1], and `a?` & `b*` on
  `a` = [0,0) under both implementations.
- **Atomic and possessive groups hide ends, as they should.** `(?>a|ab)`
  gives ends [1], so `(?>a|ab)` & `ab` on `ab` = none, although `ab` is in
  L(a|ab). `a*+` gives [3]. `(?=(a|ab))\1` gives [1], because a lookahead is
  atomic. Consequence: **& intersects the ends PCRE2 can REACH, not the
  languages**.
- **(*ACCEPT)** outside an assertion ends the match without passing the end
  callout. It is detected (`status = accept-bypass`), not enumerated. Inside
  a lookahead it only ends the assertion and is harmless.
- **(*COMMIT) and (*SKIP).** A and B DISAGREE. `a(*COMMIT)|b` & `b` on `ab`:
  A = [1,2), B = none. `aa(*SKIP)b|a` & `a` on `aab`: A = [1,2), B = none
  (SKIP moves the next start to 2). A's own start loop cannot honour them.
  B gives PCRE2's semantics of "X followed by an opaque check".
  `a(*COMMIT)|ab` enumerates only [1], so the set view loses ends.
- **(*PRUNE)** at a fixed start acts like COMMIT. A and B agree here, but
  the set view still loses the ends behind it.
- **(*THEN)** is harmless: it only moves to the next alternative.
- **Recursion.** `\((?:[^()]|(?R))*\)` on `(a(b))` gives ends [6]. WITHOUT
  the `(?(R)|...)` guard, the plain `(?:X)(?C1)` gives **[5]**: the callout
  fires at the end of the inner `(?R)` and its failure then kills the real
  end 6. The guard is required. It misreads a pattern that has a group
  NAMED `R` (pcre2pattern "Checking for pattern recursion"), so such
  patterns are a stated exclusion. Subroutine calls such as `(a|b)(?1)` are
  fine.
- **UTF.** `.+` on `é€a` gives byte ends [6,5,2], and starts are only at
  character boundaries ([0,2,5,6]). The lookahead route counts the remaining
  length in characters. A and B agree.
- **Match limits.** See F6.

**F6. Cost.** Enumeration forces PCRE2 through EVERY path, so it pays the
whole backtracking tree, not the first-match cost (`results/cost.txt`).

| pattern, subject | callouts | time | first match alone |
|---|---|---|---|
| `(a\|a)*`, `a^16` | 131,071 | 43 ms | 0.03 ms |
| `(a\|a)*`, `a^20` | stopped at the 2M callout cap | 655 ms | 0.04 ms |
| `(a\|aa)*`, `a^20` | 28,656 (Fibonacci growth) | 11 ms | 0.02 ms |
| `a*a*a*`, `a^20` | 1,771 | 0.6 ms | 0.005 ms |

`spans` on an end that cannot be reached is the same full search:
`(a|a)*b` over `a^20` hits a 1M match limit in 7.5 ms. Both bounds work:
the callout cap returns `status=cap` and keeps the ends found so far, and
the match limit returns `limit`. **A production oracle must treat cap/limit
as INCONCLUSIVE: drop the row and count the dropped rows** (K35). It should
also keep subjects short, about 10 characters or fewer for ambiguous
patterns.

**F7. The semantics questions the spike forces, each with a recommendation.**
- **Q1 Context.** Do lookarounds, `\b`, `^` and `$` inside an operand see the
  whole subject, or only the span? **Recommend: the whole subject (in
  context).** That is how PCRE2 treats every subpattern, it is what both
  implementations compute, and a product automaton reading the real subject
  gets it for free. "Isolated" is a different operator; offer it later, by
  name, if it is ever wanted.
- **Q2 Which match is reported.** **Recommend the leaning rule: leftmost
  start, then X's order among the ends Y accepts.** It is exactly PCRE2's
  meaning of "X followed by a check that Y matches [start, here)", so B
  computes it with no new semantics. State plainly that & commutes as a
  span set and in its start, but NOT in its reported match (F4: 10.2% of
  generated pairs). Longest-end and shortest-end rules would each need a
  new notion of order that PCRE2 cannot check.
- **Q3 Atomic and possessive operands.** **Recommend the operational
  meaning: & sees the ends PCRE2 reaches.** It matches PCRE2's own atomic
  lookahead behaviour. Consequence for the DFA route: an operand whose
  atomicity changes its end set must stay on the VM, or the possessive rule
  (tuning.md §2.1) must prove it changes nothing.
- **Q4 `\K` inside an operand.** **Recommend refusing it by name in v1.**
  PCRE2 itself refuses `\K` in lookarounds by default since 10.38. If it is
  ever admitted, the & span is the attempt span (F5) and the reported start
  is X's.
- **Q5 Verbs.** **Recommend refusing (*ACCEPT), (*COMMIT), (*SKIP) and
  (*PRUNE) inside & operands in v1:** ACCEPT bypasses the check, and the
  others make the set and operational views disagree (F5). (*THEN) is
  harmless but goes with them for simplicity until a need is measured.
- **Q6 Captures and backreferences across operands.** **Recommend: each
  operand's own backreferences are fine. Refuse a backreference that
  reaches into the other operand.** Report X's captures from the chosen
  path. Number groups textually across the whole `X&Y` pattern. Y's
  captures would come from Y's first path to j, which the spike does not
  report yet (`spans` would have to return Y's ovector).
- **Q7 `(?R)` inside an operand.** In PCRE2 it means the whole pattern, but
  each operand is compiled alone here, so the oracle reads it as "this
  operand". **Recommend refusing (?R) inside & operands** until someone wants
  it; subroutine calls to named or numbered groups stay.
- **Q8 Predicates.** A predicate is tested at X's end, on the captures as they
  stand there (a repeated group holds its last iteration). It picks the first
  path in PCRE2's order that satisfies it, and that may be a SHORTER match:
  `(\d+)` with `int($1) <= 255` on `999 1234` = [0,2) "99". **Recommend
  documenting this and showing `\b` in the examples.** Do not add an
  implicit token rule.

**F8. Predicates** (`results/predicates.txt`).
- **Demos.** 8 hand-derived demos pass:
  - `(\d+)` / `int($1) <= 255` / `1234` → [0,3);
  - `\b(\d+)\b` / `999 12 300 255` → [4,6);
  - `(\w+)=(\w+)` / `$1 == $2` / `a=b x=x` → [4,7);
  - `(a+)(a+)` / `len($1) == 2*len($2)` → $1 = [0,4), $2 = [4,6);
  - capture persistence across iterations in `(?:(a)|b)+`.
- **Sweep.** 200 patterns with 2 or more groups, a 5-predicate family,
  every {a,b} subject of length 4 or less, anchored at 0 and unanchored:
  12,400 agree and 0 differ (5,045 matches found) with `refmatch`'s
  first-satisfying path, which is independent of PCRE2.
- **Control.** `ANDSPIKE_SABOTAGE=pred` ignores the predicate: 1,203 of
  3,100 differ.
- **Evaluator.** The predicate evaluator is a whitelisted Python expression
  over `$1..$9`. It is a stand-in, not a syntax proposal.

**F9. How the oracle fits Frank's testing chain, and what a production
version would be.**
1. **Oracle: PCRE2 plus callouts.** It produces the expected match for any
   `X&Y` or predicate row whose operands avoid the F7 exclusions. B gives the
   answer and A is a self-check (`A == B`), together with the
   `X&X = X` and `X&(?s:.*) = X` laws, at generation time.
2. **pcrec VM with callouts.** For predicates this largely EXISTS already.
   `match_api.md` §11.6¶1 promises that a PURE callee gets the
   backtracking-order answer, which is exactly what the predicate oracle
   computes. §11.10's `rx_in` is `int($1) <= 255`. `tests/callouts/co_oracle.c`
   already drives libpcre2 with callouts and the same NO_OPT trio. So
   "prove the VM with callouts" for predicates means behaviour rows in
   `tests/callouts/behaviors.h` checked against co_oracle. For &, the VM's
   natural form is B's shape: at X's end, an exact-span sub-match of Y over
   [attempt start, pos), in context. pcrec has no public exact-span entry,
   and none is needed: §3.6's `(?:P)\z` idiom on a truncated subject would
   give a THIRD semantics, left context only. It must be VM-internal, like a
   lookahead with an end check.
3. **DFA product.** For regular operands with no atomics, verbs, backrefs or
   `\K`, the oracle's end SET equals language membership (F2's `re` column,
   0 differences). The product DFA therefore gives the span set directly, and
   the reported match needs X's priority order: a priority/tagged DFA for X
   (capspike's TDFA) with Y as a plain DFA filter at accept. **Compare the DFA
   with the VM** on large generated populations: both are pcrec, so this is
   cheap and needs no PCRE2. **Compare the DFA with the oracle** on the
   stored rows; that is the only check independent of pcrec's parser.
4. **Minimal production version** (memory pcrec-test-harness-minimal).
   Extend `tests/callouts/co_oracle.c` with two modes, `ends` (enumerate)
   and `and` (B's nested check, plus A as a self-check). That is about 100
   lines of C, and it reuses that directory's build and its
   skip-when-libpcre2-is-absent logic. A test directory for the & module
   would have `m`/`n` cells verified by it. Its reject-table rows would be
   the F7 exclusions. Its generator-side self-checks would be A == B, the
   two identity laws and the controls. Inconclusive rows (cap/limit) are
   counted, not hidden. No Python binding ships.
5. **Sweeps NOT run** (evening hold): more than 200 patterns, length-6
   subjects, the 3-letter alphabet {a,b,c}, and lookaround or backreference
   operands in the generator. The generated population covers only the
   regular subset; everything beyond it rests on the hand cases in F5.

**F10. Test-corpus ideas for pcrec's CALLOUTS module (ruling R1).** These are
ideas only; no tests were added.
- **Veto-set rows from ONE end enumeration.** For a pattern, a subject and a
  callout at the tail, PCRE2's ordered end list fixes the expected answer
  for EVERY callee that vetoes a set V of positions: the first end not in V.
  - Tests: §11.6¶1's backtracking-order promise, densely.
  - Expectations: one NO_OPT enumeration per (pattern, subject) through
    co_oracle.
  - Size: 200 patterns × 31 subjects gives about 6k orders, and
    many vetoes each.
  - .rxt today: partly. A veto set needs a per-case callee parameter.
    Either fixed rows in `behaviors.h` ("veto even", "veto ≤ k") expressible
    now, or a new block field naming the veto set.
- **Optimization-sensitive rows.** F3's `a+(?C1)`, `[ab]*(?C1)` and
  `(\d+)(?C1)` give a different PCRE2 answer at default options and at NO_OPT.
  - Tests: §11.6¶2's statement that pcrec gives the NO_OPT answer.
  - Expectations: co_oracle with and without `--default`, keeping the rows
    where the two differ.
  - Size: generated, likely tens of patterns.
  - .rxt today: yes, as ordinary cells, with the default-differs fact noted
    in the verifier.
- **Sites inside atomic groups and lookaheads.**
  - Tests: a veto inside `(?>a+(?C1))b` retries the group's inner choices
    until the group completes, and never after. The same for `(?=a+(?C1))`.
  - Expectations: co_oracle.
  - Size: about 10 hand rows.
  - .rxt today: yes.
- **Recursion refusal at the pattern tail.** F5 shows that in PCRE2 an end
  site is reached from inside `(?R)` (the [5]-not-[6] result).
  - Tests: §11.1¶1 refuses a site that a recursion reaches; this is a
    reject-table row for `\((?:[^()]|(?R))*\)(?C1)`.
  - Size: a handful of rows.
  - .rxt today: yes (the reject form).
- **`\K` and the attempt start.** In `foo\K(?C1)bar`, the view's `caps[0][0]`
  must be the attempt start.
  - Tests: §11.3¶4. The row pins pcrec against the pcre2callout text, which
    says otherwise but which 10.49 does not follow.
  - Size: 1-3 rows.
  - .rxt today: a `checks.c`-style driver check, since no cell shows the view.
- **Predicate rows.** For example, `(\d+)(?C"le255")` bound to `rx_in(RX_CAP(1),
  0, 255)`, run over digit strings.
  - Tests: the predicate chain's VM step.
  - Expectations: co_oracle with the same behaviour.
  - Size: tens of rows.
  - .rxt today: yes, given behaviour rows in `behaviors.h`.
- **Callout argument forms.** Numbered 0-255, every string delimiter, a
  doubled delimiter, and a site inside a conditional (`(?(R)|(?C1))`, the
  guard this spike relies on).
  - .rxt today: `shapes.rxt` already covers the delimiters. The
    conditional-site row would be new, if pcrec admits `(?(R)`.
