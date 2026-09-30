# [UTF-VALID] — an opt-in subject UTF-8 validity check (DESIGN NOTE, PROPOSED)

Lane `k73utf`, 2026-09-29; revised by lane `uvrev`, 2026-09-30, against
the contract critic `docs/dev/reviews/2026-09-30-r2-utf-valid-contract.md`
(findings F1-F8; §9 maps each finding to its change). This is a design note
only. Nothing is built. Charter: `docs/dev/plan.md` [UTF-VALID]. Frank,
2026-09-29: *"a default-off check for valid subject utf. either precheck
whole subject or check as you move forward (dfa?)"*. Evidence is in
`utf_valid_evidence/`, which has its own CLAUDE.md.

## 0. Summary and recommendation

- **Today** every `-e utf8` artifact is invalid-tolerant. An ill-formed
  sequence matches nothing, and nothing reports it (ASK 1). K73 makes the
  start of the search follow PCRE2_MATCH_INVALID_UTF too. PCRE2's own
  default is the opposite: it validates the subject and refuses an invalid
  one with an error code and an offset.
- **The option names a CONTRACT, and there are two sound ones** (§2):
  - `whole`: PCRE2's contract. Before any attempt, the call refuses if an
    ill-formed sequence begins in `[startpos − LB, n)`.
  - `extent`: Frank's "check as you move forward", in a form that does not
    depend on the optimizer. After the engine answers, the call refuses if an
    ill-formed sequence begins in `[startpos − LB, e]`, where `e` is the
    match end, or `n` when there is no match.
  They give different answers on the same input, so they are two VALUES of
  one option, not rows of one mechanism table (§3). The third shape, the
  REJECT sink fused into the DFA's scan (`scan`), is rejected as a contract.
  What it refuses depends on which bytes the optimizer let the scan read
  (§2.3).
- **Recommend building `whole` first, and recording `extent` with its
  contract and cost but not building it** until a caller needs single-artifact
  linear find-all (§2.4). `whole` is PCRE2's per-call contract, it runs
  before the engine, and it needs no scratch captures. Its quadratic
  find-all has PCRE2's own escape: validate once with the exported entry,
  then loop on the default, non-checking artifact.
- **The offset entry takes `startpos`, not `from`** (F1).
  `<prefix>_valid_upto(s, n, startpos)` does the artifact's own lookbehind
  step-back, so it checks exactly the bytes the wrapper checks.
- **LB is PCRE2's `max_lookbehind` fact, measured on 10.46** (§1.4). It is
  not only the lookbehind widths. `\b`, `\B`, `\A`, `[[:<:]]` and `[[:>:]]`
  each count 1. `^`, `$`, `\G`, `\X`, `\R` and `\K` count 0. Nested reads do
  not accumulate.
- **The step-back is a raw continuation-byte skip** (F3), not `back_step`.
  **PCRE2's order is measured** (F4): the K50 mid-character guard fires
  BEFORE the validity check. pcrec adopts that order.
- **It is an abi event when built, and default-off artifacts move too**
  (§6): the stamp, the result code, and the exported entry. The first
  version's "moves by exactly the stamp line" was wrong (F7).
- **Cost** (darwin, directional, §5). On a SCANNING call the precheck costs
  about as much as the call itself on sparse-accented text (1.0x-1.4x per
  call, 8 B to 4 KiB). On a call a prefilter or pre-check answers, it turns
  a sublinear call into an O(n) one. That is why it stays default-off.

## 1. PCRE2's contract, measured

Probes: `utf_valid_evidence/pr4.c` (one call) and `lb.c` (the step-back
per pattern) under PCRE2_UTF, checking ON, on libpcre2 **10.46**
(ubuntubudu, light compiles: `utfcheck_10.46.txt`, `lb_10.46.txt`). Every
10.46 row was re-run on 10.48 (Mac) and matches (`lb_10.48.txt`).

### 1.1 The checked range

| case | 10.46 |
|---|---|
| `a` on `a\xff` from 0 | **error** -23, offset 1. There is a match at (0,1) BEFORE the bad byte, and the call still refuses. The check is not limited to what the match read. |
| `a` on `xa\xffz` | error, offset 2 |
| `b` on `\xffab` from 2 | match (2,3). Bytes BEFORE `startoffset − LB` are not checked. |
| `(?<=a)b` on `\xffab` from 2 | match. LB is 1, so the check starts at 1, and the bad byte is at 0. |
| `(?<=..)b` on `\xffab` from 2 | **error**, offset 0. LB 2 reaches the bad byte. |
| `(?<=a\|bc)d` on `\xffbcd` from 3 | match. LB is the MAX over branches (2), so the check starts at 1. |
| truncated / overlong / surrogate / > U+10FFFF / isolated 0x80 | errors -3 / -17 / -16 / -15 / -22, each at the offset of the sequence's first byte |
| `a` on `\xc3\xa9a` from 1 | -36 BADUTFOFFSET. With checking ON, a mid-character start is an error. |
| `a` on `\xa9a\xff` from 5 (> n) | -33 BADOFFSET, before any check |

**PCRE2's contract**: if `startoffset > n`, BADOFFSET. Otherwise, if
`subject[startoffset]` is a continuation byte, BADUTFOFFSET. Otherwise
`[f, n)` must be well-formed, where `f` is `startoffset` stepped back LB
characters by §1.3's rule. If it is not, the call returns a UTF error whose
offset is the first byte of the first ill-formed sequence at or after `f`.
No match is attempted first. D26 applies: pcrec owes the refusal and the
offset, not PCRE2's twenty error codes.

### 1.2 The order: the mid-character guard comes first (F4, Q10 answered)

| case | 10.46 |
|---|---|
| `a` on `\xc3\xa9\xffa` from 1 | **-36**. The bad byte at 2 is never reported. |
| `a` on `\x80\xa9a` from 1 | -36. A stray continuation with no lead before it is still -36, not -22. |
| `(?<=a)b` on `\xc3\xa9\xffb` from 1 | -36 |
| `a` on `\xa9a\xff` from 1 | -23 at 2. The start is on a non-continuation byte, so the check runs. |
| `(?<=a)b` on `\x80b` from 1 | -22 at 0. The step-back reaches a bad byte. |

PCRE2 tests "is `subject[startoffset]` a continuation byte" BEFORE it
validates, and without validating. pcrec's K50 guard is the same O(1) test,
so **pcrec runs the K50 guard first, then the check.** The guard is cheaper,
it refuses before the O(n) pass, and the order removes a divergence from the
spec hunk. At `startpos == 0` K50 exempts the call, and the check then
refuses a leading continuation byte at offset 0, as PCRE2 does
(`\x80b` from 0: -22 at 0). K73's offset-0 skip becomes unobservable under
the check: a subject that begins with a continuation byte is refused before
any search. `startpos > n` keeps pcrec's existing answer (`_search` 0,
`_match` -1). The check does not run there. PCRE2's -33 is §3.1's existing
stated divergence and is not new.

### 1.3 The step-back is a raw continuation skip (F3)

PCRE2's walk, measured: per character, step back one byte, then skip back
over ALL continuation bytes to the first non-continuation byte. It does not
validate, it has no length bound, and it clamps at 0.

| case | 10.46 |
|---|---|
| `(?<=a)b` on `\x80\x80\x80b` from 3 | -22 at **0**. A 1-byte step would start at 2 and report 2. |
| `(?<=a)b` on `a\x80\x80b` from 3 | -22 at 1 |
| `(?<=a)b` on `\xff\xc3\xa9\xa9b` from 4 | -22 at **3**. The walk stops at the lead `c3` (offset 1), and 1..2 is well-formed. |

pcrec's `back_step` (`src/enc/enc_utf8.c`) is the wrong primitive. It
validates each stepped-over run, it stops after 3 continuation bytes, and on
exactly the ill-formed inputs this check exists for it answers
`BACK_STEP_NONE`. Mapping NONE to `f = 0` would report `ff` at 0 in the last
row instead of PCRE2's 3. So the step-back is its own four-line loop,
`while (k-- && f > 0) { f--; while (f > 0 && (s[f] & 0xC0) == 0x80) f--; }`,
emitted inside `<prefix>_valid_upto` (§4.3). **Pinned**: the refusal
(refuse versus answer) and the offset, on every row above. Both are
reproducible exactly with this loop.

### 1.4 What LB is: PCRE2's `max_lookbehind`, by measurement (F2)

`lb.c` compares `PCRE2_INFO_MAXLOOKBEHIND` with the MEASURED step-back
(subject `\xff` + 10 × `z`, and the largest `startoffset` that still
refuses) for 37 patterns on 10.46. The two agree on every pattern:

| LB | patterns (10.46) |
|---|---|
| **max body width, per assertion** | `(?<=a)b` 1, `(?<!a)b` 1, `(?<=..)b` 2, `(?<=a\|bc)d` 2, `(?<=a{1,3})b` 3, `(?<=\x{100})b` 1 (characters, not bytes), `(?<=\R)b` 2, `(a)(?<=\1)b` 1, `(*naplb:..)b` 2 |
| **1: `\b` `\B`** | `\bb`, `\Bb`, `b\b`, `(*UCP)\bb`, `(?=\b)b`, `(?(DEFINE)(?<x>\b))b(?&x)` |
| **1: `\A`** | `\Ab`. Measured on both versions. `\Ab\|c` on `\xffc` from 1 is -23 at 0, where a range starting at `startpos` would match `c` at (1,2). |
| **1: `[[:<:]]` `[[:>:]]`** | `[[:<:]]b`, `b[[:>:]]` (PCRE2 spells them with `\b`) |
| **0** | `b`, `^b`, `(?m)^b`, `b$`, `b\Z`, `b\z`, `\Gb`, `\Xb`, `\Rb` (outside a lookbehind), `a\Kb` |
| **no accumulation** | `(?<=(?<=..)a)b` 2 (the inner one reads 3 back), `(?<=\b..)b` 2, `(?<=\ba)b` 1, `b(?<=...)` 3, `(?:\b\|(?<=...))b` 3 |
| **every occurrence counts** | an unreferenced `(?(DEFINE)(?<x>(?<=...)))b` is 3. Conditions count: `(?(?<=..)b\|c)` 2. |

So **LB = the max over the pattern's constructs of: each lookbehind's
maximum branch width in characters, taken per assertion and not added
through nesting; and 1 for each `\b`, `\B`, `\A`, `[[:<:]]`, `[[:>:]]`.**
It is a fact about the SOURCE, and dead code counts.

**Where pcrec gets it.** The tree cannot supply it after parsing. `\A` and
`^` are one kind (`A_BOL`, `src/parse/mod_assertions.c`), but LB counts
`\A` and not `^`. `(?<=C)` is recognized into `A_CTX` in `src/opt`, and a
DEFINE body may be dropped. So LB is a parse-time running max, as it is in
PCRE2: the hooks that parse `\A`/`\b`/`\B`/POSIX word boundaries raise it to
1, and the lookaround hook raises it to the assertion's max width. A body
whose widths are PENDING (DD-14.LB, `A_CALL` inside) is finalized by
`pcrec_postresolve`, which already fills those widths. This is one fact
with one writer per construct, not a lookbehind-only rule with a word-
boundary special case.

**What the no-accumulation rule leaves unchecked, in PCRE2 too.** An inner
lookbehind or a `\b` inside a lookbehind can read bytes before `f`. PCRE2
reads them unvalidated (formally undefined). pcrec gives its invalid-
tolerant answer there, because an ill-formed byte is no character. The two
agreed on both rows probed (`(?<=(?<=..)a)b` on `\xffzab` from 3: no match;
`(?<=\ba)b` on `\xffab` from 2: (2,3)). Copying PCRE2's LB rather than the
true reach is deliberate. A larger LB would refuse subjects PCRE2 accepts.

## 2. The contracts

Notation: `f` = `startpos` stepped back LB characters (§1.3), computed
only when `startpos <= n`. "A sequence begins in X" = the walk from `f`
meets an ill-formed sequence whose first byte is in X. A sequence that
begins inside X is validated in full, even where its tail passes X's end.
Both contracts run AFTER the K50 guard (§1.2) and leave `caps` untouched on
refusal (§3.1's rule for every negative return).

### 2.1 `whole`: the precheck

**Refuse with `PCREC_ERR_UTF` iff a sequence begins in `[f, n)`.** This is
checked before any attempt. If the range is well-formed, the call proceeds
exactly as today.

It promises that an answer (match or no match) is given only for a subject
whose checked range is well-formed. So every answer is also the
PCRE2_UTF answer. §1.4 names the one residual: reads before `f` that PCRE2
does not check either.

Mechanism: one call to `<prefix>_valid_upto(s, n, startpos)` at the entry,
right after the K50 guard. It is engine-independent: the DFA, the VM and
the hybrid are covered identically, because none of them has started.

### 2.2 `extent`: check as you move forward, as a function of the answer (F5)

**The engine answers first. Then the call refuses with `PCREC_ERR_UTF` iff
a sequence begins in `[f, e]`, where `e` is the reported match end
(`caps[0][1]`; `ctx->pos + len` for the anchored entries), or `[f, n)` when
there is no match.** The sequence at `e` itself (when `e < n`) is included.
Give-ups (`[FLOOR, -2]`) and `PCREC_ERR_INTERNAL` pass through unchecked,
because the engine answered nothing.

Why `e` is inclusive: it closes the empty-match hole. `x*` on `\xff` from 0
matches (0,0), and the find-all loop then steps to `next_pos(0) = 1`. With
`[f, e)` the byte `\xff` would lie in no call's range. With `[f, e]` the
first call refuses. The character at `e` is also the one a trailing `\b`,
`$` or one-character lookahead reads.

**What it promises.**

- **Per call, it is weaker than PCRE2**, and only in one direction: an
  ill-formed sequence after the match's end is not reported by that call.
  `a` on `a b\xff` from 0 matches (0,1), where PCRE2 refuses. (`a` on
  `a\xff` is refused, because the byte at `e` is checked.) A lookahead that
  reads past `e + 1` character is also not covered: `a(?=..)` answers from
  the invalid-tolerant semantics.
- **Per loop, it equals PCRE2.** Take a find-all loop (match_api §3.1) run
  from 0 to completion. Each call starts at `e` of the previous one, or one
  character later (`next_pos`). That character is covered by the inclusive
  `e`, and `f ≤ startpos`. So the checked ranges tile `[0, n)`, and the last,
  no-match call checks to `n`. The loop meets `PCREC_ERR_UTF` iff PCRE2's
  first call refuses the subject. `<prefix>_valid_upto(s, n, startpos)` on
  the refusing call returns PCRE2's offset, because every byte before the
  refusing call's range was already checked clean. The one observable
  difference is that the matches before the bad byte have been DELIVERED.
  That is exactly "check as you move forward".
- **It is optimizer-independent.** `f` is a pattern fact plus `startpos`.
  `e` is a function of the answer, which is already asserted answer-
  identical across every axis. So the refusal set does not move with
  prefilters, skip loops, pre-checks or the engine choice. This is the
  property `scan` (§2.3) lacks.
- **It is engine-independent.** It is a post-hoc test in the entry wrapper,
  so the DFA, the VM and the hybrid are covered identically. There is no
  product automaton, no state-count growth, and no K53/K59 refusal-set
  hazard.
- **It runs the engine on possibly ill-formed input.** That is legal only
  because pcrec's semantics are defined on every byte string (invalid
  tolerance, match_api §3.1). PCRE2 cannot offer this shape, because its
  NO_UTF_CHECK on an invalid subject is undefined behaviour. So it is a
  pcrec-only contract, stated as ours, not PCRE2's.

**What it costs.**

- **Captures must be scratch.** On a refusal, `caps` must be untouched. But
  the refusal is decided after the engine has written its captures. So the
  wrapper passes the body a stack `ptrdiff_t [NCAPS][2]` and copies it out
  only when the check passes. A caller's `caps == NULL` gets the scratch
  too, because the wrapper needs `e`. On the DFA that costs nothing new: the
  emitted `_search` computes the match end and start whether or not `caps`
  is NULL. Whether any VM path skips work for `caps == NULL` must be
  measured by a build lane. The other option, relaxing §3.1 to "caps
  unspecified on -9", is rejected. It would be the first negative return
  with an exception to the untouched rule, and a D80 contract regression.
- **The DFA body has to be split into an inner body and a wrapper.** Today
  `<prefix>_search` IS the scan body. Every return path would need `e`
  routed out, so the check needs a wrapper around an inner function. That
  is emitted scaffolding, and it is the same abi event as §6.
- **Per call**: a no-match call validates `[f, n)`, the same as `whole`
  (the scan read all of it anyway). A matching call validates `[f, e]`:
  the bytes the search skimmed before the match, plus the match, plus one
  sequence. The copy-out is `NCAPS` pairs.
- **Find-all is linear**: about `n + m·(LB + 1)` characters for `m`
  matches, against `whole`'s O(n·m).

### 2.3 `scan`: the REJECT sink fused into the DFA — rejected as a contract

Under `-e utf8` the DFA's byte classes already separate continuation bytes
from leads (`UPC_NOSTART`). A validity automaton has 9 states. Its product
with the forward machine, with REJECT routed to an error sink, would detect
ill-formedness in the same table step the scan already pays. What it can
promise is *"refuse iff the bytes the forward scan actually READ contain an
ill-formed sequence"*. That read set R is an implementation fact:

- **Every byte-skipping mechanism removes bytes from R**: the memchr and
  offset-set prefilters, the `REQ_BYTE`/`REQ_RUN` pre-checks, the scan
  edge's run loop, the pinned search, and the end-window clamp. The same
  subject would be refused by one pcrec version and accepted by the next.
- **It breaks `make test-axes` by construction.** Every deny/force axis is
  asserted answer-identical over the whole corpus. A fused check whose
  refusal depends on which prefilter ran fails that sweep on every
  ill-formed cell, unless the check denies them all and gives up most of
  the DFA's speed. This is the repo-native form of the argument.
- **R is not `[f, e]` either.** The forward scan reads past the match end
  to find the longest match, so it would refuse where `extent` answers.
  And it skips bytes before the match, so it would answer where `extent`
  refuses. So the sink is not a mechanism for `extent` either. It is a
  third contract, and an unsound one.
- **No VM coverage.** The VM's class tests fail on an ill-formed sequence
  without distinguishing it from a non-match.
- **Its cost moves into state count, not time.** The start family grows by
  about 8 states, which counts against `PCREC_MAX_DFA_STATES_*` and the
  emitted-size caps. So it can MOVE THE REFUSAL SET, the K53/K59 hazard class.

Frank's "(dfa?)" is answered this way: the incremental shape is sound only
when it is defined by the answer (`extent`), and then it needs no DFA.

### 2.4 `whole` versus `extent`, and the recommendation

| | `whole` | `extent` |
|---|---|---|
| per-call contract | PCRE2's | weaker than PCRE2 past `e` (one direction) |
| a find-all loop run to completion | PCRE2's refusal and offset | PCRE2's refusal and offset, with the matches before the bad byte already delivered |
| engine coverage | all (pre-engine) | all (post-engine, wrapper) |
| optimizer-independent / test-axes | yes / yes | yes / yes |
| `caps` untouched on refusal | free | needs scratch caps + copy-out |
| emitted shape | one call after the K50 guard | a wrapper around every entry body, `e` routed out |
| engine sees ill-formed input | never, under the flag | yes (defined, invalid-tolerant) |
| find-all cost | O(n·m); escape: validate once + default artifact | O(n + m·LB) |

**Recommend `whole`, built first; `extent` recorded here, not built.**
The reasons, in order:

1. `whole` is PCRE2's per-call contract. A caller who opts in gets the
   answer PCRE2 gives, and the spec hunk states no new semantics.
2. It is the smaller build: one call at an existing site, and none of
   `extent`'s scaffolding (scratch caps, split bodies, `e` routing).
3. Its find-all cost has a complete escape without a runtime flag, and it
   is PCRE2's own idiom. The caller validates once with
   `<prefix>_valid_upto(s, n, 0)`, then loops on the DEFAULT (non-checking)
   artifact. That is one artifact, not two, because the entry is carried by
   every artifact (§4.3). It answers the critic's "doubles emitted code"
   worry: a find-all caller never needs the checking artifact.
4. D77: `extent`'s one advantage is linear find-all ON a checking artifact,
   with streaming delivery. No caller has measured a need for it.
   **Trigger**: a caller (or a bench row) that needs per-call checking and
   runs find-all on it, where validation dominates. When that happens,
   `extent` is a second VALUE of the same option, and its contract above
   needs no redesign.

## 3. No mechanism table (F6)

The first version said "one option, two contracts, one first-match table",
with `scan-fused` and `precheck` as rows. That table was not sound:

- Rows of a first-match table must be answer-identical, as the
  `dfa_pfs[]`/`DFA_SELECT` idiom is. `precheck` refuses `a` on `a\xff`, and
  the fused sink accepts it. So the rows were two contracts wearing one
  name, and the promise that "a `scan` artifact that cannot take row 3 is
  never refused" really meant "`scan` may refuse more than R", which is no
  contract at all.
- The fused row's predicate read other tables' results (the route, the
  prefilter choice), and its product changes the state count those tables
  consume. That is circular.

**The revised structure**: the option's VALUE is the contract
(`off` | `whole` | later `extent`). Contracts that change answers are
option values, never rows. Each contract has exactly ONE mechanism today:
`whole` has the entry precheck, and `extent` has the wrapper post-check. The
encoding decides whether it is `inert` (`byte`). That is a boolean, not a
selection table, and the note no longer pretends otherwise. A mechanism
table appears only if a contract gains a second, answer-identical mechanism.
None is in view: §2.3 shows the fused sink is not one. The plan.md row's
"rows of ONE first-match table" framing should be dropped for this design
(the manager's edit).

## 4. The caller surface

### 4.1 The switch: a compile-time contract axis

D18 compiles options away, so the switch is an axis in `axes.def`: default
off, spelled `-futf-check` (the `whole` contract), with a `pcrec_options`
field and a config directive. `-futf-check=extent` is reserved for §2.2 and
refused until it is built. A runtime switch would need an `rx_ctx` layout
change and a new `<prefix>_search` parameter. §4.4's escape makes it
unnecessary.

**It is a CONTRACT axis, the second one** (F7.5). `axes.def`'s block today
reads "the one axis that is NOT answer-identical ([K50])". It becomes "the
contract axes", with two rows. Like K50's, the bit is not masked out of
`rx_info.flags`. `make test-axes` must not sweep it for identity, because
the corpus carries ill-formed subjects (`tests/utf8/k73_startskip.rxt`'s 86
cells, for a start). It is excluded by name, with an asserted-present guard
(`run_axes.sh`'s `PCREC_FORCE_PREFILTER` idiom), and it gets its own arm
(§7). Under `byte` the axis is **inert** (stamp `"inert"`), matching
`-fno-startpos-guard`'s precedent (tuning.md §2.23).

### 4.2 The result code and where it is returned

- **One code, `PCREC_ERR_UTF` (-9)**, below `PCREC_ERR_FLOOR`. It is not a
  give-up, and it is in the family of `_STARTPOS` (-7) and `_UNSET_VAR`
  (-8), in the shared `PCREC_RX_ABI_H` block. `-9` is unused today (the
  critic grepped `lib/`, the spec, and every lane worktree's `pcrec.h`).
- **The entries (F7.3).** Six entries take a subject: `_search`, `_match`,
  `_match_caps` (match_api §1), and their buffer forms `_search_in`,
  `_match_in`, `_match_caps_in` (§10). `_info` and `_next_pos` take none.
  **The check is emitted at exactly the call sites of
  `pcrec_emit_startpos_guard`, right after it**, whether or not that
  primitive emits text there (under `-fno-startpos-guard` it emits nothing,
  but the site is the same). So the site set is the guard's by
  construction, and §1.2's order is structural. Today those sites are:
  the DFA's `_search` and unwrapped `_match` bodies, and the VM's three
  `_run` bodies. Every other entry DELEGATES and PROPAGATES the code:
  `_match_caps` over `_match` on the DFA, and the `_in` forms over their
  plain forms or the same `_run`. The spec hunk says so, as match_api
  already does for `PCREC_ERR_INTERNAL`. A VM FRAMES-escalation restart
  ([OPT-1], §10.9) re-enters `_run`. The build lane must place the check so
  a restart does not validate twice, or state the double pass as cost.
- **Composed call sites (F7.4).** The below-the-floor rule says a composed
  call site TRAPS on any code below −5, because for -6/-7 a composed callee
  seeing one means the engine broke its own rule. `-9` is the first
  below-floor code that is **caller-data-dependent**. A checking callee
  handed the caller's own subject can legitimately refuse it, because its
  LB may reach before the outer call's range. So **a composed site
  PROPAGATES -9 and does not trap.** No composed sites are emitted today.
  The spec's K50 consequences list gains this line now, so the first
  producer inherits it.

### 4.3 The offset: `<prefix>_valid_upto(s, n, startpos)` (F1, F7.2)

```c
size_t <prefix>_valid_upto(const unsigned char *s, size_t n, size_t startpos);
```

It returns the first byte of the first ill-formed sequence at or after `f`,
where `f` is `startpos` stepped back by THIS artifact's LB (§1.3, §1.4), or
`n` if there is none. `startpos > n` returns `n`. Under `byte` the body is
`return n;`.

- **It takes `startpos`, not `from` (F1).** The first version's
  `utf_invalid_at(s, n, from)` could not report a lookbehind-window error:
  a caller passing `from = startpos` starts inside the valid tail and gets
  `n` (`(?<=..)b` on `\xffab` from 2). The step-back now lives inside the
  entry, byte for byte what the wrapper checks. The caller passes the SAME
  `startpos` it passed the refused call, and gets PCRE2's offset. Under
  `extent` the same call returns the offset too, because the first bad
  sequence at or after `f` lies in `[f, e]` by the refusal.
- **The name is encoding-neutral (F7.2)**, like `_next_pos`. "Valid up to
  `n`" reads correctly in a `byte` artifact.
- **Every artifact carries it, whatever the flag (F7.1).** It is the
  find-all escape (§4.4), and that escape runs on the DEFAULT artifact. A
  caller's code must also survive a recompile under another encoding, which
  is why the error constants are emitted everywhere too (match_api §4). So
  default-off artifacts DO move: one exported function with its prototype
  and doc comment (plus `[VAR]`'s re-spelling, below), and the stamp. The
  first version's "every artifact moves by exactly the stamp line" and
  "default-off costs nothing" were wrong. `artifact_size_log.tsv` will record
  the growth. The alternative is emitting it only under the flag (or on
  request). That keeps default artifacts unchanged, but it removes the
  find-all escape from exactly the artifact that escape needs. **Q4.**
- **One validator, three callers.** The precheck calls it. The caller calls
  it for the offset. `[VAR]`'s `$_var_valid(v, len)` becomes
  `$_valid_upto(v, len, 0) == len`, so the tree has one spelling of
  "well-formed UTF-8" (Q7). Like `var_valid`, it is not engine-callable:
  the entry wrapper calls it once per call (DD-12 (7)'s terms).

### 4.4 Find-all under `whole`

match_api §3.1's loop calls `<prefix>_search` once per match. Each call
validates `[f, n)`, so `m` matches cost O(n·m) validation bytes. PCRE2 has
the same property and documents NO_UTF_CHECK for every call after the
first. pcrec's spec hunk gives the equivalent: call
`<prefix>_valid_upto(s, n, 0)` once, refuse or proceed, then run the loop on
an artifact compiled WITHOUT `-futf-check`. A stateful "already validated
up to" cursor inside the artifact is forbidden by the reentrancy contract
(§5.3). `extent` is the single-artifact answer, when it is needed (§2.4).

## 5. Cost, measured (darwin, directional)

Instruments: `utf_valid_evidence/utfcheck_bench.c` (first version: three
64 MiB subjects) and `utfcheck_bench2.c` (this revision: the sparse
subject, and per-call cost on small subjects). Both use strict validators
whose stopping offsets are pinned to libpcre2's. Each figure is the best of
7, from two runs each (`bench_run{1,2}.txt`, `bench2_run{1,2}.txt`), with
gcc-16 -O2 at a load average of 6-10. This is standalone C at a fixed `-O2`,
not the artifact's own build flags, and not Linux, which is the perf box.
The figures are directional only (house rule), and the recommendation does
not rest on them.

**Validator rate, ns/byte, 64 MiB:**

| subject | bytewise | 8-byte ASCII fast path |
|---|---|---|
| ASCII | 0.64 | **0.04** |
| sparse: one `é` per ~256 B | 0.69 | **0.12** |
| sparse: one `é` per ~64 B | 0.77 | **0.34** |
| sparse: one `é` per ~16 B (accented prose) | 0.99 | 0.90 |
| CJK, 8/9 three-byte | 0.88 | 1.01 |
| random ~1/3 two-byte (branch-predictor worst case) | 2.21 | 2.53 |

**Per call on small subjects, ns** (windows of the one-per-~64 B buffer,
each starting on a character boundary; runs 1 and 2):

| subject size | `valid_upto` (LB 0) | `valid_upto` (LB 1) | `jumpz` `_search` (scanning) | `\bfox\b` `_search` (scanning) | `[a-z]+@[a-z]+` `_search` (pre-check answers) |
|---|---|---|---|---|---|
| 8 B | 6.0 / 5.9 | 5.8 / 5.8 | 5.9 / 5.9 | 6.6 / 6.7 | 4.3 / 4.4 |
| 32 B | 16.5 / 16.6 | 16.7 / 16.4 | 11.5 / 11.4 | 12.4 / 12.6 | 4.6 / 4.8 |
| 128 B | 57 / 57 | 58 / 58 | 42 / 42 | 44 / 44 | 7.7 / 7.9 |
| 512 B | 193 / 194 | 190 / 194 | 174 / 170 | 179 / 176 | 16 / 16 |
| 4 KiB | 1392 / 1408 | 1413 / 1429 | 1301 / 1360 | 1655 / 1674 | 109 / 112 |

What the numbers say, and what they do not (F8):

- **Against a scanning call, the precheck costs about as much as the call
  itself** on sparse-accented text: 1.0x-1.4x per call at every size from
  8 B to 4 KiB. So `whole` roughly doubles a scanning call there. On pure
  ASCII it is far cheaper (0.04 ns/B against a scan's ~0.33).
- **Against a call a prefilter or pre-check answers**, the ratio has no
  fixed value. That call is sublinear in `n` (`[a-z]+@[a-z]+` at 109 ns per
  4 KiB), and the precheck is O(n). The first version's "17x" and "1.6x"
  were ratios against sublinear calls, and they are withdrawn. The honest
  statement is qualitative: the check turns a sublinear call into a linear
  one, 10x-13x on these sizes.
- **Fixed per-call cost is small, and the step-back is invisible.** An
  8-byte call costs about 6 ns, the same as an 8-byte scanning call.
  Adding the LB-1 raw step-back changes nothing measurable (5.8 vs 6.0).
  So find-all's per-call overhead is the validated LENGTH, O(n·m) under
  `whole`, not a constant.
- **The ASCII fast path** wins 16x on ASCII, 5.8x at one non-ASCII
  character per 256 B and 2.3x at one per 64 B. It is about even at one
  per 16 B, and it LOSES 10-15% on dense non-ASCII (CJK, random mix). The
  first version reported only the 16x. Net: keep it (Q8), because mostly-
  ASCII text is the common case. SIMD (the simdutf family) is the lever for
  the dense rows, and it stays LAST (memory `pcrec-post-spine-direction`).
- **Dropped from the decision inputs**: the byte-class-DFA validator row
  (a flat ~1.95 ns/B). It priced a separate DFA walk, which no contract
  proposes any more (§2.3).

## 6. Is it an abi event? Yes, once, when built

These move every artifact, default-off ones included:

1. `PCREC_ERR_UTF` joins the shared `PCREC_RX_ABI_H` block.
2. A `<PREFIX>_UTF_CHECK` selection stamp, `"inert" | "off" | "whole"`,
   unconditional per the §6.3 family-(a) rule.
3. `<prefix>_valid_upto` with its prototype and doc comment, in every
   artifact (Q4). On `[VAR]` artifacts, `var_valid` is re-spelled on it.

It needs the full D76/D94 ritual: the readers of the abi number found BY
GREP, the identity-gate re-pin, and the suites that count (registry,
codegen, rxtsource). `rx_info` could mirror the stamp. D77 says not until a
runtime reader exists.

## 7. What building `whole` would touch (for pricing)

- `src/enc/enc_utf8.c`: the `valid_upto` entry (raw step-back + validator
  with the ASCII fast path), and `var_valid` rebased on it.
  `src/enc/enc_byte.c`: the trivial body.
- The LB fact: a parse-context running max, written by the `\A`/`\b`/`\B`/
  POSIX-word-boundary hooks and by the lookaround hook, and finalized by
  `pcrec_postresolve` for pending widths (§1.4). It reaches the emitter as
  a macro inside `valid_upto`'s body.
- `axes.def` (the contract-axes block), `lib/pcrec.h`, the `cli` flag, the
  config directive, and the `-futf-check=extent` refusal.
- One emitter primitive, `pcrec_emit_utf_check`, called at every
  `pcrec_emit_startpos_guard` call site, right after it (§4.2).
- Spec hunks (D80): match_api §1 (the new per-artifact name), §3.1/§3.2/
  §3.3 (the code, propagation, the order), §3.1.1's sibling for
  `valid_upto`, §4 (the -9 paragraph, and the composed-site PROPAGATE line
  in the K50 consequences list), §6 (the stamp), and §10 (the `_in` forms
  propagate). Also tuning.md (the axis, its inert-under-`byte` rule), the
  cli spec, `docs/spec/rxt_format.md`, and the find-all idiom (§4.4).
- **Harness and oracle** (F7.5; `[VAR]`'s -8 needed the same):
  `tests/harness/driver.c`, `run.sh`, `verify_rxt.py`; the `rxt_format.md`
  spelling of a per-block `-futf-check` and of a refusal cell (code +
  offset); `tests/codegen/run_codegen_tests.sh`, `run_encoding_checks.sh`,
  `run_cpset_structure.sh`; and `tests/resource/run_resource_tests.sh`.
  Every one of them names `PCREC_ERR_UNSET_VAR` today. The harness must
  name -9 rather than mislabel it, as it once mislabelled -7 as "VM budget
  exhausted" (k73utf report F2).
- **Oracles.** (1) libpcre2 **10.46**, PCRE2_UTF checking ON, pinned
  transcripts for §1's rows. That includes §1.2's order rows and §1.3's
  step-back rows, and every §1.4 LB row as a refuse/answer pair at
  `startpos = LB` and `LB + 1`. (2) An INDEPENDENT base-tier oracle for the
  offset: python3's strict `bytes.decode('utf-8')`, whose
  `UnicodeDecodeError.start` equals PCRE2's startchar on all 13 probed
  sequence kinds (truncated, overlong, surrogate, > U+10FFFF, 0xF5+,
  isolated continuation; checked this lane). The LB step-back is
  transcribed separately in python, from §1.3's rule, not from the C.
- **Checks.** A generated ill-formed family, differential against both
  oracles. A `byte`-inert identity arm. The default-off identity, stated
  honestly: every artifact moves by exactly the stamp line PLUS the
  `valid_upto` block, and nothing else. `test-axes`' own arm for the
  contract axis: on each corpus cell, `-futf-check` gives the default
  answer iff python's oracle finds the cell's checked range well-formed,
  and otherwise -9 with the oracle's offset. The named exclusion from the
  identity sweep is asserted present. A failing-direction plant for each of
  the three validator callers, and sabotage rows. The highest S-id is
  checked ON MAIN at build time.

## 8. Questions for Frank

1. **The checked range: PCRE2's `[startpos − LB, n)`**, with LB as §1.4
   measures it (lookbehind widths per assertion, plus 1 for `\b`/`\B`/`\A`/
   POSIX word boundaries, dead code included, no accumulation), and the raw
   continuation-skip walk of §1.3? *Recommend yes. It is PCRE2's contract,
   and the fact is one parse-time running max.* The alternative,
   `[startpos, n)`, diverges refuse-versus-answer on every `\b` pattern with
   a bad byte just before `startpos`, which is a common pattern class.
2. **Which contract: build `whole` now, and record `extent` (§2.2) with its
   contract and cost but not build it** until a caller needs linear
   find-all on a checking artifact (the §2.4 trigger)? *Recommend yes.*
   `extent` is your "check as you move forward" in a form whose answers do
   not move with the optimizer. The DFA-fused sink (`scan`) is rejected as
   a contract, because its refusals depend on which bytes the prefilters
   skip, and it would break `make test-axes` by construction (§2.3). If you
   want the streaming shape now, `extent` is buildable as specified. The
   price is scratch captures and a wrapper split of the DFA entry bodies.
3. **A compile-time contract axis**, `-futf-check` (the `whole` value;
   `=extent` reserved), default off, excluded by name from the identity
   sweep with its own oracle arm, beside K50's axis? *Recommend yes (D18).*
4. **`<prefix>_valid_upto(s, n, startpos)` in EVERY artifact** (the
   find-all escape runs on the default artifact; `byte` returns `n`), and
   not only in checking artifacts? *Recommend every artifact.* This is the
   one place where default-off artifacts grow by a function.
5. **One code**, `PCREC_ERR_UTF` (-9), and not PCRE2's per-kind codes?
   *Recommend one (D26).*
6. **Find-all under `whole`**: document "validate once with `valid_upto`,
   loop on the default artifact", as PCRE2 documents NO_UTF_CHECK?
   *Recommend yes.* It needs one artifact, not two.
7. **One validator** for the precheck, the offset entry and `[VAR]`'s
   `var_valid`, in the same abi event? *Recommend yes.*
8. **The ASCII fast path** in the emitted validator? It wins 2.3x-16x on
   ASCII and sparse text and loses 10-15% on dense non-ASCII. *Recommend
   yes.* SIMD stays out.
9. **Under `byte`**, is the flag inert (stamp `"inert"`) or refused?
   *Recommend inert, following `-fno-startpos-guard`'s precedent.*
10. **Order**: the K50 guard first, then the check, as PCRE2 does (§1.2,
    measured on 10.46)? *Recommend yes.* A mid-character `startpos` is
    `PCREC_ERR_STARTPOS` whether or not the subject is valid, and
    `startpos > n` keeps today's answer, with no check.
11. **`-9` at a future composed call site PROPAGATES, and does not trap**
    (§4.2), recorded in the spec now? *Recommend yes.* It is the first
    below-floor code caused by caller data rather than an engine fault.

## 9. The critic's findings, and what changed

| finding | disposition |
|---|---|
| F1 offset entry cannot report a lookbehind-window error | **Accepted.** `valid_upto(s, n, startpos)` does the step-back itself (§4.3). |
| F2 LB includes `\b`/`\B` | **Accepted and extended by measurement**: `\A` and `[[:<:]]`/`[[:>:]]` also count; no accumulation; dead DEFINE bodies count; the fact is parse-time because `A_BOL` merges `\A` with `^` (§1.4). |
| F3 raw continuation skip, not `back_step` | **Accepted.** A dedicated loop; the pinned offsets are listed (§1.3). |
| F4 order: K50 before the check | **Accepted.** Q10 answered by measurement (§1.2). |
| F5 `extent` as a contract | **Accepted as a costed option value** (§2.2): contract, inclusive `e` (which closes an empty-match hole the finding's `[f, e)` had), scratch caps, loop-level equivalence with PCRE2, the test-axes argument against `scan` (§2.3). Compared in §2.4; `whole` recommended. |
| F6 not one table | **Accepted.** Contracts are option values; no mechanism table exists today (§3). |
| F7.1 identity claim | **Accepted.** Default-off artifacts move by the entry and the stamp (§4.3, §6, §7). |
| F7.2 name | **Accepted**: `valid_upto`. |
| F7.3 which entries | **Corrected in both directions**: six entries take a subject (the three `_in` forms, match_api §10, are the rest). The check sits at the K50 guard's sites, and the others propagate (§4.2). |
| F7.4 below-floor trap | **Accepted.** -9 propagates at a composed site (§4.2, Q11). |
| F7.5 contract axis and harness work | **Accepted** (§4.1, §7). |
| F7.6 -9 free | Recorded (§4.2). |
| F8 cost method | **Accepted and re-measured.** The sublinear-denominator ratios are withdrawn. The sparse subject and small-subject per-call rows are added. The fast path's losses are reported. The DFA-validator row is dropped (§5). |
| "startpos > n" (critic, edge) | Stated: today's answer, no check (§1.1, §1.2). |
