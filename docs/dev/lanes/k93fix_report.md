# Lane k93fix — K93: possessify verdicts inside subroutine-call targets

Branch `lane/k93fix` from main 54c42e36. Tier: opus engine lane.

## 1. Cause

`src/opt/possessify.c`'s `pss_walk` gave a quantifier inside a called group
a verdict computed from the group's LEXICAL follow. The `A_CALL` arm's comment
said the callee "still gets its verdict at its own lexical position, where the
enclosing follow is the real one". That premise is false: every call site
re-runs the group's body (the whole `A_CAP`, or the whole pattern for `(?R)`)
under the follow of the call site. `(a+)b(?1)a` possessified `a+` against
`{b}`, and the call re-ran it against `{a}`. The free discharge
(`src/opt/atomic.c`) asks the same walk through `pcrec_poss_survey`, so it had
the same hole (K93 related item 1).

## 2. Fix — one mechanism for every call kind

- `CallCtx` holds, per GROUP NUMBER (0 = the root), the JOIN of every call
  site's context: the three things `pss_walk` already threads (follow,
  enclosing-loop firsts `encl`, `may_end`).
- On a call-bearing pattern (`pcrec_has_call`), `pss_run` first runs
  CONTEXT-ONLY walks (`P->collect`: no verdict, no marking, no counters). At
  each `A_CALL` the site's context is joined into `cc[target]`. The walks
  iterate until nothing grows. This is needed because a site inside a called
  group sees a context that depends on that group's own join (nested calls,
  recursion). The lattice is finite and the join only widens, so the loop
  terminates.
- The `A_CAP` arm widens its lexical context by `cc[cap.no]`, and so does
  `pss_root` for `cc[0]` (`(?R)`). Every `A_CAP` with that number gets the
  join, which is a superset and the safe direction. The arena's zero is the
  join's identity, so an uncalled group walks under its lexical context
  unchanged.
- A call inside a lookaround body is never reached by `pss_walk`. Such a call
  joins the TOP context (every byte, may end) through a `pcrec_ast_visit` of
  the lookaround.
- **Why one walk under the join is exact:** the verdict is a conjunction
  over contexts. Disjointness from a union of follows is the same as
  disjointness from each one. The lazy conjunct fires if any context may end.
  The exact-count arm reads no context. The follow a nested item sees
  distributes over the union.
- The groups are keyed by number rather than by `u.call.body`. The reason is
  that the free discharge runs before `pcrec_callgraph_build` binds `.body`,
  and both entries share `pss_run`, so the discharge gets the fix with no
  extra code.
- A call-free pattern allocates nothing and walks once. It is byte-identical
  by construction.

## 3. Oracle transcript (libpcre2 10.46, ubuntubudu, light probe)

The probe sent `pcre2_ctypes.py` over ssh stdin and ran `search` from offset
0, once with default options and once with `PCRE2_NO_AUTO_POSSESS`
(0x4000). Reported as `(span, groups)`. Cells where the two options differ
are marked `*`.

```
(a+)b(?1)a        abaa ((0,4),((0,1),))  aabaaa ((0,6),((0,2),))  abaaa ((0,5),((0,1),))  aba None  ab None
(?<n>a{1,3})b(?&n)a  abaa (0,4) g1(0,1); aaabaaaa (0,8) g1(0,3); abaaaaa (0,6) g1(0,1); aaabaaa (0,7) g1(0,3)
(?:(a+)b|x)(?1)a  xaa (0,3) g1 unset; xaaa (0,4); xa None
((?>a+))b(?1)a    abaa None; abaaa None; aba None
(?P<n>a+)b(?P>n)a abaa (0,4) g1(0,1); aabaaa (0,6) g1(0,2)
(a+)b(?-1)a       abaa (0,4); aabaaa (0,6)
(?+1)a(a+)b       aaab (0,4) g1(2,3); aab None; aaaab (0,5) g1(3,4)
(?1)a(a+)b        aaab (0,4) g1(2,3); aab None; aaaab (0,5) g1(3,4)
(a+)b((?1))c(?2)a abacaa (0,6) g(0,1)(2,3); abacaaa (0,7); abaca None; aabaacaaa (0,9) g(0,2)(3,5)
(a+)b(?:x(?1))*a  abxaa (0,5); abxaxaa (0,7); abxa None; aba (0,3)
(a+)b(?1)+a       abaa (0,4); aabaaa (0,6); abaaaa (0,6)
(?:x(?1)a|(a+)b)  xaa (0,3); xaaa (0,4); ab (0,2) g1(0,1); xa None
(\d+)-(?1)5       12-345 (0,6); 1-5 None; 1-55 (0,4)
(a+?)b(?1)        abaa (0,3); aabaaa (0,4); ab None
(a+)b(?=(?1)a)    abaa (0,2); aba None; abaaa (0,2)
(a+)b(?>(?1))a    abaa None; abab None; abaab None
^(b(?1)a|a+)$     baa (0,3); bbaaa (0,5); aaa (0,3); ba None
(?:b(?R)a|a+)   * baa (1,3) vs (0,3); * bbaaa (2,5) vs (0,5); * baaa (1,4) vs (0,4); aaa (0,3); ba (1,2)
(a+)b(?1)c        abac (0,4); aabaac (0,6); abc None; abaa None
([ab]+)c(?1)a     acba (0,4); abcaba (0,6) g1(0,2); acaa (0,4)
(?:(?1)a){2}(a+)b aaaaab (0,6) g1(4,5); aaab None
(a{1,3})b(?1)(?1)a abaaa (0,5); abaaaa (0,6); aabaaaaa (0,8) g1(0,2)
(?1)a((?2))c(a+)b aaacab (0,6) g(2,3)(4,5); aaacaab (0,7) g(2,3)(4,6); aacab None; aaaacaab (0,8) g(3,4)(5,7)
```

The capture groups are written out in full in `tests/recursion/k93.rxt`,
which was generated from this transcript. pcrec was not asked.

pcrec against the oracle:
- **Main 54c42e36** disagreed on 44 of 77 subject cells. All of them are
  NOMATCH or a too-long lazy span, and every block except the atomic ones and
  the `(?R)` block has at least one wrong cell.
- **This branch** agrees with 10.46's default on every cell except the three
  starred `(?R)` cells.

## 4. THE (?R) DIVERGENCE — for Frank's ruling

10.46's auto-possessification is call-aware for numbered and named group
calls: every other block above agrees under both options, including the
recursive `^(b(?1)a|a+)$`. It is NOT call-aware for `(?R)`. This is filed as
upstream U18 in `docs/dev/upstream_issues.md`.

This branch builds the SOUND answer, which is 10.46's
`PCRE2_NO_AUTO_POSSESS` answer. The artifacts whose answer now differs from
PCRE2's default:

- `tests/recursion/k93.rxt`, block `(?:b(?R)a|a+)`: three cells.
  - `baa`: pcrec (0,3), PCRE2 default (1,3).
  - `bbaaa`: (0,5) vs (2,5).
  - `baaa`: (0,4) vs (1,4).

  The unqualified lines are the sound answers. The PCRE2-default answers are
  recorded as `under pcre2-auto-possess` lines, which the harness counts as
  skips. If Frank rules "match PCRE2 default", swap the two and add a
  `(?R)`-specific mode, which this lane did NOT build.
- The existing corpus and the bench: see §5. No existing `.rxt` cell
  changed answer (no existing corpus or bench answer moved (§5's census: every mover outside `k93.rxt` is answer-identical); the full `make test` is the owed confirmation).

## 5. Mover census

Call-free patterns are byte-identical BY CONSTRUCTION (`pss_run` takes the
fixpoint branch only when `pcrec_has_call(root)`, and a call-free walk is the
old walk line for line), so the census is the call-bearing population.

Method: the same compile was done twice, once with the compiler built from
main 54c42e36 and once with this branch, using the same `-o` basename, then
`.c` and `.h` were diffed.
- Flags: `--features all`, at the default engine and at `--engine=vm`.
- Patterns: every corpus `pattern` line spelling a call (345 unique, 690
  compiles, 76 refused by both) and every pcrec-bench pattern spelling one
  (12 unique, 24 compiles, read-only from `bench/*/export/*.rxt`,
  `bench/capability/patterns.rxt`, `bench/utf8/patterns.rxt` and
  `bench/*/patterns/*.rx`).

Results:
- **Corpus: 44 movers = 22 patterns x 2 engines, 0 asymmetric refusals.**
  - 21 of them are this lane's own `k93.rxt` witnesses.
  - The two `k93.rxt` blocks that do NOT move are the controls
    `(a+)b(?1)c` (still possessive) and `(a+)b(?>(?1))a`.
  - The 22nd is `tests/recursion/nocaptures.rxt:76` `^(a(?3)?)(b)((c)?)$`.
    Its `(c)?` LOSES its possessive mark (`RX_VM_STRATS` 0x3 -> 0x2,
    +639 program bytes). The cause: the call `(?3)` sits inside the `?`
    repeat, `pss_rep` puts that repeat body's FIRST into `encl`, and an
    `A_CALL`'s FIRST is every byte. This is sound, and it is answer-identical
    (the file's cells pass). It is a lost possessification. Its two
    pre-existing conservatisms are `pss_rep` adding body FIRST to `encl` even
    for `rmax <= 1` (no restart is possible) and `first_of(A_CALL)` widening
    to every byte (design §4.4a site 19's wave-G item). Neither is touched
    here.
- **Bench: 0 movers** of 24 compiles. No bench artifact changes at all, so
  none can diverge from PCRE2's default because of this fix.
- **Not an abi event:** no emitted scaffolding moves. A changed program for a
  pattern the old analysis miscompiled is the fix. The one non-witness
  mover is a rung choice inside the existing scaffolding. No spec hunk: what
  a pattern matches is PCRE2's semantics already, and no stamp, flag, limit
  or entry changed.

## 6. Tests and checks added

- `tests/recursion/k93.rxt` (23 blocks, 133 case lines, 3 `under` lines),
  hand-written from the transcript (`k69.rxt` precedent). Main fails 86 of
  its 123 original cases; this branch passes 133 of 133.
- `tests/possessify/calls.txt` (23 patterns) is now part of
  `run_possdiff.sh`'s default population. Any pattern file may carry a
  `# features:` line, and in such a file a refusal is a FAIL, not a silent
  skip.
  - This branch: 22 of 22 agreed (10,206 cells, 3 possessified), before the
    23rd pattern was added.
  - Main's binary: 5 diverged.
- `run_possessify_tests.sh` section 8 checks:
  - `(a+)b(?1)c` STILL stamps possessive. This is the "possessify was not
    switched off for call targets" control.
  - `(a+)b(?1)a` and `^(b(?1)a|a+)$` do not stamp possessive.
  - `((?>a+))b(?1)a` on `abaa` is nomatch under `-fno-possessify` (the
    discharge half).

  Main's binary fails 3 of these 4 checks. This branch passes 4 of 4.
- Sabotage rows:
  - S586: the join is never applied (harness on k93.rxt + possdiff).
  - S587: the fixpoint stops after one round. It is caught by the
    `(?1)a((?2))c(a+)b` block, the one witness that needs a second round.
  - S588: calls inside a lookaround join nothing.

  Results (`bash tests/mech/run_sabotage_matrix.sh S58N`, solo, Mac):
  - S586 DETECTED: `reach:ok, corpus:95fail/38pass, possdiff:5fail/173pass`.
  - S587 DETECTED: `reach:ok, corpus:9fail/124pass`. The 9 failures are
    exactly the second-round block's 9 case lines.
  - S588 DETECTED: `reach:ok, corpus:4fail/129pass` (the lookaround block).
- Pins: `tests/rxtsource/run_rxtsource_tests.sh` CENSUS/RUNSH
  +1/+23/+133.

## 7. Validation

Done on the Mac, this branch:
- `make strict CC=gcc-16`: clean.
- `bash tests/harness/run.sh tests/recursion/k93.rxt`: 133 passed, 0 failed,
  3 `under` skips. Main's binary fails 86 of 123 (before the 10 second-round
  lines were added).
- `bash tests/possessify/run_possdiff.sh tests/possessify/calls.txt`: 22
  agreed, 0 diverged, 10,206 cells. Main's binary: 5 diverged.
- `run_possessify_tests.sh` section 8 in isolation: 4 of 4 pass. Main's
  binary fails 3 of 4.
- Whole `run_possessify_tests.sh`: `checks passed: 22`, 0 failed.
- Sabotage S586/S587/S588: all three DETECTED solo (§6).
- Mover census: §5.

OWED (launched detached as the lane's last act, under
`worktrees/.mac-suite.lock`):
- The chain is `make test-codegen`, then `make test` (default sections), then
  `make test-possessify`.
- Log: `worktrees/k93fix-scratch/chain.log`.
- Completion line: `CHAIN DONE` with the three rcs.
- Verdict: per the situation index, read make's
  `*** [(Makefile:N: )?test-X] Error` lines, not the FAIL counts.
- The standing darwin `nm arm_a.o` red in `test-codegen` is expected and not
  this lane's.
- `test-rxtsource` carries the re-pinned census (+1/+23/+133). Its C3
  python-verifier counts (`C3_SKIP`/`C3_SKIP_NOPYTHON`) may also move by
  k93.rxt's no-python cells. If it goes red only on those pins, that is a
  re-pin owed (k69fix's precedent), not a defect.
- The Linux full run is the manager's to schedule.


## Appendix — raw oracle transcript (pattern, subject, 10.46 default, 10.46 PCRE2_NO_AUTO_POSSESS)

```
libpcre2 version: 10.46 2025-08-27
U9 witness a?(?:b){0,4}+a on 'a': None (expected None on PCRE2 10.46)
a{1,3}? on 'aaaa': ((0, 1), ()) (expected (0,1), ())
version 10.46 2025-08-27
(a+)b(?1)a	abaa	((0, 4), ((0, 1),))	((0, 4), ((0, 1),))
(a+)b(?1)a	aabaaa	((0, 6), ((0, 2),))	((0, 6), ((0, 2),))
(a+)b(?1)a	abaaa	((0, 5), ((0, 1),))	((0, 5), ((0, 1),))
(a+)b(?1)a	aba	None	None
(a+)b(?1)a	ab	None	None
(?<n>a{1,3})b(?&n)a	abaa	((0, 4), ((0, 1),))	((0, 4), ((0, 1),))
(?<n>a{1,3})b(?&n)a	aaabaaaa	((0, 8), ((0, 3),))	((0, 8), ((0, 3),))
(?<n>a{1,3})b(?&n)a	abaaaaa	((0, 6), ((0, 1),))	((0, 6), ((0, 1),))
(?<n>a{1,3})b(?&n)a	aaabaaa	((0, 7), ((0, 3),))	((0, 7), ((0, 3),))
(?:(a+)b|x)(?1)a	xaa	((0, 3), ())	((0, 3), ())
(?:(a+)b|x)(?1)a	xaaa	((0, 4), ())	((0, 4), ())
(?:(a+)b|x)(?1)a	xa	None	None
((?>a+))b(?1)a	abaa	None	None
((?>a+))b(?1)a	abaaa	None	None
((?>a+))b(?1)a	aba	None	None
(?P<n>a+)b(?P>n)a	abaa	((0, 4), ((0, 1),))	((0, 4), ((0, 1),))
(?P<n>a+)b(?P>n)a	aabaaa	((0, 6), ((0, 2),))	((0, 6), ((0, 2),))
(a+)b(?-1)a	abaa	((0, 4), ((0, 1),))	((0, 4), ((0, 1),))
(a+)b(?-1)a	aabaaa	((0, 6), ((0, 2),))	((0, 6), ((0, 2),))
(?+1)a(a+)b	aaab	((0, 4), ((2, 3),))	((0, 4), ((2, 3),))
(?+1)a(a+)b	aab	None	None
(?+1)a(a+)b	aaaab	((0, 5), ((3, 4),))	((0, 5), ((3, 4),))
(?1)a(a+)b	aaab	((0, 4), ((2, 3),))	((0, 4), ((2, 3),))
(?1)a(a+)b	aab	None	None
(?1)a(a+)b	aaaab	((0, 5), ((3, 4),))	((0, 5), ((3, 4),))
(a+)b((?1))c(?2)a	abacaa	((0, 6), ((0, 1), (2, 3)))	((0, 6), ((0, 1), (2, 3)))
(a+)b((?1))c(?2)a	abacaaa	((0, 7), ((0, 1), (2, 3)))	((0, 7), ((0, 1), (2, 3)))
(a+)b((?1))c(?2)a	abaca	None	None
(a+)b((?1))c(?2)a	aabaacaaa	((0, 9), ((0, 2), (3, 5)))	((0, 9), ((0, 2), (3, 5)))
(a+)b(?:x(?1))*a	abxaa	((0, 5), ((0, 1),))	((0, 5), ((0, 1),))
(a+)b(?:x(?1))*a	abxaxaa	((0, 7), ((0, 1),))	((0, 7), ((0, 1),))
(a+)b(?:x(?1))*a	abxa	None	None
(a+)b(?:x(?1))*a	aba	((0, 3), ((0, 1),))	((0, 3), ((0, 1),))
(a+)b(?1)+a	abaa	((0, 4), ((0, 1),))	((0, 4), ((0, 1),))
(a+)b(?1)+a	aabaaa	((0, 6), ((0, 2),))	((0, 6), ((0, 2),))
(a+)b(?1)+a	abaaaa	((0, 6), ((0, 1),))	((0, 6), ((0, 1),))
(?:x(?1)a|(a+)b)	xaa	((0, 3), ())	((0, 3), ())
(?:x(?1)a|(a+)b)	xaaa	((0, 4), ())	((0, 4), ())
(?:x(?1)a|(a+)b)	ab	((0, 2), ((0, 1),))	((0, 2), ((0, 1),))
(?:x(?1)a|(a+)b)	xa	None	None
(\d+)-(?1)5	12-345	((0, 6), ((0, 2),))	((0, 6), ((0, 2),))
(\d+)-(?1)5	1-5	None	None
(\d+)-(?1)5	1-55	((0, 4), ((0, 1),))	((0, 4), ((0, 1),))
(a+?)b(?1)	abaa	((0, 3), ((0, 1),))	((0, 3), ((0, 1),))
(a+?)b(?1)	aabaaa	((0, 4), ((0, 2),))	((0, 4), ((0, 2),))
(a+?)b(?1)	ab	None	None
(a+)b(?=(?1)a)	abaa	((0, 2), ((0, 1),))	((0, 2), ((0, 1),))
(a+)b(?=(?1)a)	aba	None	None
(a+)b(?=(?1)a)	abaaa	((0, 2), ((0, 1),))	((0, 2), ((0, 1),))
(a+)b(?>(?1))a	abaa	None	None
(a+)b(?>(?1))a	abab	None	None
(a+)b(?>(?1))a	abaab	None	None
^(b(?1)a|a+)$	baa	((0, 3), ((0, 3),))	((0, 3), ((0, 3),))
^(b(?1)a|a+)$	bbaaa	((0, 5), ((0, 5),))	((0, 5), ((0, 5),))
^(b(?1)a|a+)$	aaa	((0, 3), ((0, 3),))	((0, 3), ((0, 3),))
^(b(?1)a|a+)$	ba	None	None
(?:b(?R)a|a+)	baa	((1, 3), ())	((0, 3), ())
(?:b(?R)a|a+)	bbaaa	((2, 5), ())	((0, 5), ())
(?:b(?R)a|a+)	baaa	((1, 4), ())	((0, 4), ())
(?:b(?R)a|a+)	aaa	((0, 3), ())	((0, 3), ())
(?:b(?R)a|a+)	ba	((1, 2), ())	((1, 2), ())
(a+)b(?1)c	abac	((0, 4), ((0, 1),))	((0, 4), ((0, 1),))
(a+)b(?1)c	aabaac	((0, 6), ((0, 2),))	((0, 6), ((0, 2),))
(a+)b(?1)c	abc	None	None
(a+)b(?1)c	abaa	None	None
([ab]+)c(?1)a	acba	((0, 4), ((0, 1),))	((0, 4), ((0, 1),))
([ab]+)c(?1)a	abcaba	((0, 6), ((0, 2),))	((0, 6), ((0, 2),))
([ab]+)c(?1)a	acaa	((0, 4), ((0, 1),))	((0, 4), ((0, 1),))
(?:(?1)a){2}(a+)b	aaaaab	((0, 6), ((4, 5),))	((0, 6), ((4, 5),))
(?:(?1)a){2}(a+)b	aaab	None	None
(a{1,3})b(?1)(?1)a	abaaa	((0, 5), ((0, 1),))	((0, 5), ((0, 1),))
(a{1,3})b(?1)(?1)a	abaaaa	((0, 6), ((0, 1),))	((0, 6), ((0, 1),))
(a{1,3})b(?1)(?1)a	aabaaaaa	((0, 8), ((0, 2),))	((0, 8), ((0, 2),))
version 10.46 2025-08-27
(?1)a((?2))c(a+)b	aaacab	((0, 6), ((2, 3), (4, 5)))	((0, 6), ((2, 3), (4, 5)))
(?1)a((?2))c(a+)b	aaacaab	((0, 7), ((2, 3), (4, 6)))	((0, 7), ((2, 3), (4, 6)))
(?1)a((?2))c(a+)b	aacab	None	None
(?1)a((?2))c(a+)b	aaaacaab	((0, 8), ((3, 4), (5, 7)))	((0, 8), ((3, 4), (5, 7)))
```
