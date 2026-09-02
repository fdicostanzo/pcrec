# Known issues — confirmed pcrec bugs (deferred fixes)

Confirmed correctness bugs in pcrec itself (distinct from docs/dev/upstream_issues.md,
which tracks OTHER engines). Each has a minimal repro and a scheduled fix. Repros
live in tests/known_fail/ (NOT run by `make test`, so the suite stays honest about
what it certifies) and become passing regressions when fixed. That directory is
EMPTY as of 2026-08-15: no confirmed bug is currently deferred with a repro on
file.

Status: `deferred` (scheduled) | `fixing` | `fixed` (moved to a passing corpus).

---

## K1 — FIXED 2026-08-09 (R2)

Zero-width `$` lost priority to a consuming alternative in a repeated group.
Root cause turned out to be general, not `$`-specific: `clo_visit` cut the
ε-path re-entering a loop-entry split, so an empty iteration never reached the
loop exit and never took its rightful priority. Same defect as R2-S1.
**Fix:** loop-entry states are marked in the NFA; on ε re-entry the closure
follows the loop EXIT once (PCRE's empty-iteration rule). Regressions moved to
tests/base/review_r2.rxt (passing). Note the original entry's scoping claim
("ENG_ATTEMPT only") was WRONG — the bug was live in both engines.

---

## K2 — FIXED 2026-08-22 by module 'backrefs' ([M6.5.2]); confirmed [SPEC-1.10], 2026-08-30 (found 2026-08-09, R4 critic pass)

pcrec's diagnostic for `\1`..`\9` describes a PCRE2 behaviour that does not
exist. It reads:

    $ build/pcrec -p rx -o /dev/null '\1'
    pcrec: \1 (backreference/octal) requires module 'backrefs' (pattern offset 0)

"backreference/octal" implies PCRE2 falls back to an octal escape when the
referenced group is absent. It does not — that is Perl/PCRE1 behaviour. Measured
against libpcre2 10.46 via pcre2_compile_8:

    \1  \7  \8  \9   -> error 115 "reference to non-existent subpattern"
    (a)\1  (a)(b)(c)\3 -> accepted
    (a)\2             -> error 115
    \0  \012  \o{101}  -> accepted (the genuine octal forms)

So a SINGLE digit `\1`..`\9` is unconditionally a backreference, and `\0` —
which shares the same diagnostic — can never be one at all, since there is no
group 0.

**R6 CORRECTION, 2026-08-10 — the paragraph above generalised from single digits
and is wrong about the rest.** For a MULTI-digit sequence the reading depends on
the running capture count. Re-measured independently:

    (a)\12                           vs "a\n"           -> match   (octal 012)
    (a)\12                           vs "aa2"           -> nomatch
    (a)(b)...(l)\12  (twelve groups)  vs "abcdefghijkll" -> match   (backref 12)

Same three bytes, opposite constructs, decided by how many capture groups the
parser has seen SO FAR — a forward declaration does not count. So
"(backreference/octal)" is not simply wrong: it is RIGHT for `\ddd` and for
`\0`, and wrong only for a bare single digit.

That makes the fix subtler than this entry first implied. **The correct message
is not a constant** — it depends on parser state the doorway cannot see (D24's
"THE LIMIT OF THE TABLE"). Module 'backrefs' must carry a running capture count
and choose the diagnostic after consulting it.

**Severity: cosmetic today.** pcrec rejects all ten either way, so nothing
miscompiles; the message merely misdescribes PCRE2. It is recorded because the
message becomes wrong ADVICE once module 'backrefs' exists, and because
src/parse/registry.c's notes now state the correct semantics while parse.c still
prints the old text — a divergence that must be resolved rather than forgotten.

**Not fixed then on purpose:** SR-2's acceptance bar was byte-identical output
across the corpus, and changing this string earlier would have broken that
proof for no correctness gain. **Fix with:** module 'backrefs' (or SR-6),
splitting `\0` from `\1`..`\9`. No tests/known_fail/ repro: the behaviour was
always a rejection, not a wrong match, so there was no failing regression to
ratchet.

**FIXED, confirmed [SPEC-1.10] 2026-08-30.** Module 'backrefs' shipped
2026-08-22 ([M6.5.2]) with no FIXED marker on this entry — the drift
`docs/dev/spec_survey.md`'s STALE-OR-WRONG #2 flagged. Re-measured against a
live `build/pcrec`: the GATE-CLOSED default (no `--features`) is UNCHANGED —
`build/pcrec -p rx -o /dev/null '\1'` still prints the identical
`"\1 (backreference/octal) requires module 'backrefs' (pattern offset 0)"`
text, which is correct and expected on its own terms (D26: "requires module
'X' discharges the obligation in full", independent of what the message
says once the module exists) and was never this entry's complaint. What the
entry actually needed checked is the ENABLED case ("the message becomes
wrong ADVICE once module 'backrefs' exists"), and it now reads correctly:

    $ build/pcrec -p rx --features backrefs -o /dev/null '\1'
    pcrec: \1 refers to capture group 1, but this pattern has 0 (pattern offset 0)

No trace of the old "(backreference/octal)" wording; the message states the
real PCRE2-115-class fact (a reference to a capture group that does not
exist) rather than the Perl/PCRE1 octal-fallback behaviour that never
applied. The `\0`/`\1..\9` split this entry called for is live too: under
the same `--features backrefs`, `\1` refuses as above while `\0` proceeds
PAST the parser entirely (not a backreference at all — the same compile
attempt fails only later, at the output-write step, on an unrelated
artifact of the `/dev/null` probe target, not on parsing or diagnosis).
`src/parse/mod_backrefs.c`'s "THE OCTAL RULE IS FOUR ORDERED QUESTIONS"
(`src/parse/CLAUDE.md`) is where that split lives structurally. No
`tests/known_fail/` regression existed to flip.

---

## K3 — FIXED 2026-08-10 (FIX-2)

**Fixed by giving the `:` row `RF_CLASS_DELIM`**, the flag its two neighbours
already had, plus a new `open_msg` field for the one thing that genuinely
differs by position. Both halves went at once, as this entry said they must:
the over-ACCEPTANCE (`[:alpha:]` compiled a matcher for `{: a l p h}`) and the
over-REJECTION (`[a[:b]`, `[[:alpha]`, `[[:]` refused although PCRE2 compiles
them). All five known-wrong pins in tests/reject/ fired on the way past and have
graduated into the normal tables.

**The schema question this entry left for Frank was answered by D26, and the
answer was smaller than the question.** A fifth doorway kind (`RK_CLASSOPEN`)
was proposed because PCRE2 uses different WORDING at a class's own bracket. D26
makes wording tier 3, so that reason evaporated — but a real tier-2 distinction
survived it: inside a class the construct is one PCRE2 SUPPORTS (name the
module), and at the class's own bracket it is one PCRE2 will never accept (name
no module, because none can make it legal). One field, `open_msg`, encodes that.
No new kind, no `RK_COUNT` change, no sweep change.

**And FIX-2 closed the doorway's own over-promise while it was there**
(R8/C4-7): the 14 POSIX class names — 16, once the differential found
`[[:<:]]` and `[[:>:]]` — are now a measured table, so `[[:foo:]]` is "unknown
POSIX class name" rather than a promise that module `classes` will implement it.

Historical record follows.

## K3 — as recorded when OPEN, found 2026-08-10 (SR-2 sabotage validation)

pcrec ACCEPTS `[:alpha:]` as an ordinary five-character class. PCRE2 rejects it.

    $ build/pcrec -p rx -o /dev/null '[:alpha:]'     # accepted
    pcre2:  compile error at offset 0: POSIX named classes are supported
            only within a class

**This is the third find of one shape**, after `\v` and the POSIX collating
elements: pcrec assigns a meaning to a pattern PCRE2 refuses, and python `re` —
the base-tier oracle — accepts it too, so the corpus is structurally unable to
notice. Measured against libpcre2 10.46, not inferred:

    [:alpha:]  [::]  [:ab:]c  [:^alpha:]  [:a:]  [:foo:]  -> ERROR at offset 0
    [:alpha]   [:alpha:x]  [:a.]  [=a:]  [:]              -> accepted
    [^:alpha:]                                            -> accepted
    [x[:alpha:]]  [[:alpha:]]                             -> accepted (POSIX class)

The rule is one pcrec already implements for the two other delimiters: at a
class's OWN opening bracket, `:` behaves exactly like `.` and `=` — it opens a
delimiter-pair construct when the matching `:]` appears later, and a negated
class suppresses it because `^` sits between the bracket and the delimiter.
pcrec has `RF_CLASS_DELIM` rows for `.` and `=` and none for `:`. The 2026-08-09
survey that found the collating bug read `[[.` and `[[=` and did not read `[:`
at class open.

**How it surfaced is the part worth keeping.** Nothing found this by reading the
spec. SR-2 introduced an `at_class_open` guard to preserve existing behaviour,
and the sabotage battery reported that DELETING that guard changes 0 of 4173
hashed emission cases and breaks no test in the suite. A branch no test can see
was the signal; the divergence was what sat behind it. "Which of my new branches
is invisible?" is a question worth asking of every change.

**Severity: over-acceptance**, which D24 rates as seriously as under-acceptance —
pcrec compiles a matcher for a pattern PCRE2 would refuse, so a caller migrating
from PCRE2 gets silent behaviour where they expected a compile error. It cannot
miscompile a pattern PCRE2 accepts.

**The open question in this entry is now measured, and it is a SECOND bug with
the same root cause.** `[a[:b]` was recorded above as unmeasured. Two R5 critics
measured it independently:

    [a[:b]  [[:b]  [[:alpha]  [[:]  [[:a]  [[:^a]  [x[:a]y]   -> PCRE2 ACCEPTS
                                                               -> pcrec REJECTS
                  "POSIX class [:...:] requires module 'classes'"

So the `:` row is missing BOTH halves of `RF_CLASS_DELIM`, and each half is a
bug in the opposite direction: without the class-open half pcrec over-ACCEPTS
`[:alpha:]`, and without the terminator half it over-REJECTS `[a[:b]`. The
second is the one that costs users today — `[a[:b]` is a pattern a person
plausibly writes, and pcrec answers it by naming a module that has nothing to do
with it. It also does NOT go away when module 'classes' lands: the recognition
rule is wrong, not the implementation status.

**Fix (both halves, one change):** give the `:` row the delimiter-pair rule the
`.` and `=` rows already have. Note the diagnostic differs by position — PCRE2
says "POSIX named classes are supported only within a class" at a class's own
bracket and treats `[[:alpha:]]` as a real POSIX class — so one row cannot carry
both messages, and the natural shape is a fifth doorway kind for the class-open
position. That is a D24 schema decision and wants Frank's steer.

**Not fixed in SR-2 on purpose:** SR-2's acceptance bar is byte-identical output,
and this is a behaviour change. Fix it with K4, which lives in the same loop.

---

## K4 — FIXED 2026-08-10 (FIX-2)

**All three scan rules landed together, as this entry insisted.** The scan now
stops at the end of the CLASS rather than the end of the pattern.

**Rule 3 is the one worth reading this entry's wording for.** It says "skip `\]`
and `\\` as a unit", and that is exact. I implemented it twice as something
looser — first "skip any `\X`", then "suppress only a class-ending `]`" — and
PC-3's generated sweep refuted both within minutes. Four measured patterns
separate the three candidate rules, and no weaker rule gets all four:

    [[.\.]]      REJECT   `\.` is NOT a unit, so `.]` closes the pair
    [[.a\\]x.]   accept   `\\` IS a unit, so the `]` is unescaped and ends
                          the class before `.]` is reached
    [a[.b\].]    REJECT   `\]` IS a unit, so that `]` does not end the class
    [[.b].]      accept   a bare `]` ends the class

All four are pinned in tests/reject/, two of them in the MANIFEST as the only
rows ruling out each wrong rule.

**Rule 2 was nearly shipped as an invisible branch.** Deleting it changes no
VERDICT — pcrec rejects the same patterns either way — so a 1680-pattern
generated differential stayed at zero failures without it. What it changes is
the error OFFSET: with it, `[[.a[.b.].]` blames offset 4, the inner opener PCRE2
actually recognises; without it, offset 1, the outer bracket PCRE2 abandoned.
Now pinned. See D26's note on why "don't chase PCRE2's offsets" does not mean
"offsets don't matter".

Historical record follows.

## K4 — as recorded when OPEN, found 2026-08-10 (R5 critics, two independently)

`RF_CLASS_DELIM`'s terminator scan runs to the end of the PATTERN, not the end
of the character class, so a `.]` or `=]` anywhere later — including well
outside the class — makes an ordinary `[.` look like a collating element.
pcrec rejects patterns PCRE2 compiles:

    [.a]x.]   [.a]$.]   x[.a]y.]   [=a]x=]   [a[.b]c.]   [a[.b]xy.]
    [[.a].]   [.a].]    [a[.b]c]d.]           -> PCRE2 ACCEPTS, pcrec REJECTS

`[a[.b]c]d.]` is the sharpest: the `.]` pcrec matched sits at offset 9, outside
the class, which closed at offset 7. The scan reads past the construct's own
boundary.

Measured against PCRE2 10.46, whose rule has three parts the current loop has
none of. Abort the scan when you meet: an unescaped `]` (the class ended); a `[`
followed by the same delimiter (a NESTED opener wins — `[[:a[:alpha:]]` compiles
in PCRE2 because it abandons the outer opener and recognises the inner one); and
skip `\]` and `\\` as a unit. **The three must land together** — adding the `]`
rule without the escape rule flips `[a[.b\].]` from correct rejection to
over-acceptance.

**Pre-existing, not an SR-2 regression:** SR-2 moved `reject_collating`'s loop
verbatim, so the byte-identity proof correctly reported no change. That is worth
stating plainly, because it is the honest limit of an identity proof — **it
cannot see a bug that both sides share.**

**Why the defence missed it:** all seven collating accept-controls in
tests/reject/ put the class at the END of the pattern. Not one appends anything
after the closing `]`, which is exactly the shape that fails. The comment above
them says over-rejection "is the opposite failure and just as wrong" — and that
is the failure they do not cover. Add accept-controls with trailing text in the
same change.

---

## K5 — FIXED 2026-08-10 (FIX-1) — was a MISCOMPILE

A `{m,n}` count above 65535 is silently reinterpreted as literal text.
`try_quant` treats the overflow as "not a quantifier", restores the cursor, and
`{` becomes a literal. PCRE2 raises error 105, "number too big in {} quantifier".

    a{65536}   a{0,65536}   a{100000}   -> PCRE2 error 105; pcrec ACCEPTS

And it does not merely accept — it compiles a matcher for a DIFFERENT LANGUAGE.
The emitted code matches the eight literal characters `a{65536}` and does not
match a run of `a`s. This is the one class the project charter rules out:
"unsupported constructs must fail with a clean error, never miscompile". A user
who writes `a{70000}` gets working, wrong code and no diagnostic.

The boundary is correctly placed on the other side — `a{65535}` is a quantifier
to both engines. Base-tier defect: no registry row and no "requires module"
diagnostic stands between the user and it.

**Fix (FIX-1).** `try_quant` now REMEMBERS the overflow instead of declining on
it, and raises "number too big in {m,n} quantifier" only where it would have
returned true. That two-phase shape is not a nicety — it is what PCRE2 does, and
skipping it over-reaches. Measured against libpcre2 10.46:

    a{65536}  a{100000}  a{0,65536}  a{65536,}  a{,65536}
    a{65535,65536}  a{65536,1}  a{99999999999999999999}   -> error 105
    a{65536   a{65536x}  a{65536,x}                       -> COMPILE, literal

Two orderings that had to be measured rather than guessed: **too-big beats
out-of-order** (`a{65536,1}` is 105, not 104 — and the clamped accumulator makes
it look out-of-order internally, so getting this backwards is a live mistake),
and the reported offset is where the offending number's digits ran out, which
is why each number's end position is kept separately. pcrec's offsets now match
PCRE2's exactly on all eight.

**One inconsistency this introduces, deliberately left alone:** the neighbouring
"numbers out of order" error still reports the `{`, where PCRE2 reports the
closing `}` (`a{3,1}` → pcrec offset 1, PCRE2 offset 5). Aligning it is a
behaviour change to a message that predates this work and wants its own
decision, not a silent ride-along.

**Coverage:** 8 rows in `tests/reject/` pinning the DIAGNOSTIC, 8 corpus `perr`
blocks (7 marked `# pcre2-only` — see U5), 3 over-reach accept-controls, and
`(?:){65535}` pinning the boundary itself. Sabotage-validated: reverting the fix
costs 9 reject + 9 corpus checks; raising the overflow where it is DETECTED
rather than CONFIRMED costs 3 + 5; moving the ceiling to 65534 costs exactly
1 — the boundary pin, and nothing else in the repo.

---

## K6 — FIXED 2026-08-10 (FIX-1) — was a MISCOMPILE

A well-formed `{m,n}` with nothing to quantify is silently literal text.
`try_quant` is only ever called from `p_rep`, AFTER an atom has been parsed, so
a `{` reached by `p_atom` is never tested for quantifier-hood at all.

    {1}   {2,3}   {,5}   {1,}   {1}a   a|{1}   ({1})   (?:{1})
        -> PCRE2 error 109 "quantifier does not follow a repeatable item"
        -> pcrec ACCEPTS, and matches the literal characters

pcrec already has the correct behaviour for `*`, `+` and `?` in that position
(`*a` is rejected at offset 0, agreeing with PCRE2) and is missing it only for
`{`. The discriminator is exactly "did it parse as a quantifier", which
`try_quant` already computes and nobody asks in atom position.

**The fix must not over-reach.** The MALFORMED brace forms are literal in both
engines and must keep compiling: `a{`, `a{}`, `a{,}`, `a{1`, `}`.

**Fix (FIX-1).** `p_atom` gained a `case '{'` beside the existing `* + ?` case.
It rewinds to the `{`, asks `try_quant`, and fails with error 109 only if the
answer is yes; otherwise the `{` is consumed as a literal exactly as before. The
over-reach guard is structural rather than a second list: "malformed" IS
"`try_quant` declined", so the two rules cannot drift apart.

`try_quant` may also fail from inside, and that turns out to be the order PCRE2
uses — measured, `{65536}` is 105 and `{3,1}` is 104, neither is 109. A fix that
asked "is anything repeatable" first would answer all twelve plain cases
correctly and both of these wrongly. Offsets match PCRE2 throughout, because
PCRE2 reports the closing `}` and that is where `try_quant` leaves the cursor.

**Coverage:** 12 rows in `tests/reject/` (10 plain + the two precedence cases),
12 corpus `perr` blocks — python `re` calls these "nothing to repeat", so no
oracle exclusion was needed — and 11 malformed-brace accept-controls with
literal-match corpus cases behind them. Sabotage-validated: reverting the fix
costs 12 reject + 12 corpus checks; the over-reach ("any `{` in atom position is
an error") costs 13 + 18.

---

## K8 — FIXED 2026-08-10 (R7, same checkpoint it was found in) — was a MISCOMPILE

pcrec did not accept SPACE or TAB inside a `{m,n}` quantifier. PCRE2 10.46 does,
following Perl 5.34, so every such pattern was silently demoted to literal text.

    a{ 1}   a{1 }   a{ 1 }   a{1, 2}   a{1 ,2}   a{<TAB>1}
        -> PCRE2: a quantifier; matches ONE 'a'
        -> pcrec: five or more literal characters

**Found by R7's spec critic, and how it was found is the point.** The session's
own 49 hand-picked probes missed it completely, because in QUANTIFIER position
both engines exit 0 — a verdict-only comparison sees nothing, and only the
compiled language differs. The critic generated the brace space combinatorially
instead of listing it, and got 90 verdict disagreements in ATOM position (`{ 1}`
is PCRE2 error 109, pcrec accepted it) plus the silent pair above. It is the
same class as K5 and K6, undetected by the same instrument that had just been
used to certify them.

**The rule, measured gap by gap against libpcre2 10.46 rather than inferred:**

    tolerated bytes:  0x20 space, 0x09 tab — and NO others. 0x0a 0x0b 0x0c 0x0d
                      and 0xa0 all leave the brace literal in both engines.
    positions:        all four gaps, `{` _ m _ `,` _ n _ `}`, any run, mixed.
    never:            inside a number (`a{1 2}` is literal, not `a{12}`), and
                      never in place of one (`a{ }`, `a{ , }`, `a{ ,}` stay
                      literal exactly as `a{}` and `a{,}` do).

**Fix:** a four-line `skip_quant_space` called at exactly those four gaps. Both
"never" clauses fall out of skipping only at the gaps, so there is no second
rule to keep in step. The calls sit AFTER each `end_m`/`end_n` assignment
because PCRE2 reports the offset where the DIGITS ran out — `a{65536 }` is
error 105 at offset 7, the space itself, not at the `}`.

**The oracle situation is the `\v` shape again**: python `re` reads every one of
these as literal, agreeing with the bug, so the tolerated forms cannot be
python-verified (U6) and carry `# pcre2-only`. The bytes that must NOT be
skipped agree with python and are verified normally.

**One test-design trap, recorded because it cost a sabotage to find.** The
obvious corpus guard — `pattern a{\n1}` — does not guard anything. A `.rxt`
pattern line cannot carry a raw control byte, and `\n` written in a pattern is
an escape pcrec decodes in ATOM position, long after `try_quant` has looked at
the brace and seen a backslash. Substituting `isspace()` for the real test left
every such case passing. The working guard needs a raw byte and a discriminating
shape (`a{<LF>65536}` compiles iff the byte is not skipped) and lives in
`tests/reject/`, where bash can supply the byte.

Sabotage-validated: reverting all four gaps costs 5 reject + 12 corpus checks;
`isspace()` costs 4; dropping one gap costs 1 + 4; skipping digits at the gaps
costs 25 + 57; moving the skip before `end_m` costs 1.

---

## K7 — FIXED 2026-08-18 ([M4.7b])

**Resolution — and the headline is that this entry's own diagnosis was wrong
about where the memory went.** Every measurement below is reproduced, but the
sentence "`{0,n}` builds an optional chain that blows past the memory the cap
was meant to bound" located the cost in the wrong stage. The chain is fine; the
NFA BUILDER's bookkeeping about it was not.

**1. The bounded-OPTIONAL blowup was one line in `src/ir/nfa.c`.** The `X{m,n}`
tail loop (the nested `(X(X(X)?)?)?` lowering) rebuilt its out-patch set from
scratch on every iteration: `patch_join(b, &w.out, &cat.out)` copied a list that
grows by one element per copy into a freshly allocated array, so building the
tail cost Theta((n-m)^2) in arena traffic while the STATE count — the only thing
`PCREC_MAX_NFA_STATES` watches — stayed linear. That gap is the whole of K7's
"the cap cannot be reached by the shape that needs it": there was nothing for
any cap to object to. `frag_cat2` two functions up already inherited its right
operand's array instead of copying it; the fix applies that same idiom here
(`Frag w = { s, cat.out };`). A Patch is an unordered SET of dangling edges —
`patch_to` writes one target into every entry and reads nothing about order —
and `nst` is called in exactly the same places, so the NFA is bit-identical.
MEASURED, before -> after:

    a{0,8000}     664 MB          ->  7.6 MB
    a{0,16000}    2.71 GB         ->  10.4 MB
    a{0,20000}    4.68 GB, 14.2 s ->  13.2 MB, 10.8 s
    a{0,40000}    SIGKILL/SIGABRT ->  refused 0.1 s / 16.8 MB (32000-state cap)
    a{0,65535}    SIGKILL         ->  refused 0.1 s / 10.6 MB (NFA 131072 cap)

Both caps this entry said were unreachable are now reached, in a tenth of a
second, by the shapes that need them.

**2. The EXACT-count form had a SECOND, unrelated quadratic**, which this entry
never saw because it degraded "cleanly" — at 2.1 GB. Unanchored `a{n}` has n+1
DFA states whose state-SETS average n/2 (the start self-loop keeps every chain
position live), so the subset construction's memory is Theta(n^2) while its
state count is linear: `a{20000}` interned 200,050,000 list elements for 845 MB
and 63 s and COMPILED. `PCREC_MAX_SUBSET_ELEMS` (src/core/limits.h, 48,000,000
= the test corpus's measured maximum doubled) charges elements in `intern()` as
they are interned, so the refusal happens DURING construction. `a{65535}`:
2.1 GB / 12.3 s -> 216 MB / 0.9 s. This one NARROWS what compiles — bisected,
`a{9795}` compiles and `a{9796}` refuses — and limits.h says so in full.

The two families' boundaries are now both measured and both land on the cap
that describes them: `a{0,31999}` compiles and `a{0,32000}` refuses on the
DFA STATE cap; `a{9795}` compiles and `a{9796}` refuses on the SUBSET-ELEMENT
bound; and at 65535 the bounded-optional form is caught earlier still, by the
NFA state cap during construction. Note `a{0,65535}` misses the NFA cap by only
a couple of states (2n+1 for the tail, plus the unanchored wrap and accept), so
raising PCREC_MAX_NFA_STATES slightly would let PCRE2's largest legal bounded
repeat through — deliberately NOT done here, because that cap governs every
pattern and its blast radius is a separate decision.

**3. The caller-abort, which was the worst item on this list.** Seven
malloc-failure sites called `abort()`, so a caller who set a memory limit had
their process killed with no diagnostic. All seven now report through
`ctx_nomem()` (src/core/compile.c) — "out of memory compiling this pattern" —
by giving `Arena` and `StrBuf` a back-pointer to the owning `Ctx`. The error
path already freed everything wholesale (`job_cleanup`), so the blast radius was
small: the only allocations the Job does not own are `pcrec_minimize_dfa`'s five
local tables, which now free by hand before failing. `src/parse/syntax_dump.c`'s
detached `StrBuf`s keep the abort deliberately — they belong to no compile and
have no `pcrec_error` to report through. `DFA_INVARIANT` keeps its abort too: it
is a "cannot happen" check, not an allocation failure.

**Tests.** `tests/resource/run_resource_tests.sh` (new suite, `make
test-resource`), 19 checks in three sections — bounded outcome under a
peak-tree-RSS ceiling and CPU/wall budgets via `scripts/watchdog`; a positive
control for the allocator paths under a binding `ulimit -v`; and one check per
BOUND that each shape reaches the cap describing it. Sabotage-validated three
ways, each catching only its own section: reverting `ctx_nomem` to `abort()`
fails 4 checks, reverting the nfa.c line fails 10, neutralizing
`PCREC_MAX_SUBSET_ELEMS` fails 4. Byte-identity verified across all 572
compiling corpus patterns plus 20 bounded-repeat shapes: 572/572 identical
artifacts, 35/35 refusals with identical diagnostics, zero verdict changes.

**Not fixed, and separately filed as K25:** `a{0,25000}` still takes ~15 s, and
a MEASURED 15.3 s of that is `pcrec_minimize_dfa`, against 0.03 s for parse, NFA
build and both subset constructions combined. That is Moore partition refinement
needing O(n) rounds on an n-state chain — an optimization pass this lane did not
touch, with bounded memory and guaranteed termination. It is a compile-TIME
cost, not the resource exhaustion K7 is about.

**docs/pcre2_compliance.md reconciled** — the two wrong claims this entry
recorded are identified and corrected in the `a{0,65535}` row itself.

---

_Original entry, kept for the history:_

A large BOUNDED repeat exhausts memory and the process is SIGKILLed, instead of
reaching the DFA state cap that exists to prevent exactly this.

    $ build/pcrec -p rx -o /tmp/o.c 'a{0,65535}'
    Killed                                          # rc 137, empty stderr

**Re-measured 2026-08-10 by a spec-first writer (D27), with two consequences
this entry did not previously record.** `a{65535}` does reach its clean "too
complex" diagnostic — but only after 23.9 s and 2.1 GB RSS, and under a 2 GB
address-space limit `pcrec_compile` ABORTS THE CALLER'S PROCESS with no
diagnostic at all. pcrec is a library; killing the caller is a worse failure
than the SIGKILL recorded below, because a caller that set a limit did so
precisely to avoid this. `a{0,20000}` compiles at 4.7 GB / 49.5 s. The writer
also found TWO CLAIMS IN docs/pcre2_compliance.md that are wrong as written
about this boundary — reconcile them when K7 is fixed.

Measured on a pinned build of `c38934c`, so it PREDATES FIX-1 and is not a
regression from it:

    a{0,65535}   a{,65535}   a{1,65535}   a{0,40000}   -> SIGKILL (rc 137)
    a{0,20000}                                         -> compiles, rc 0
    a{65535}                                           -> clean rc 1,
        "pattern too complex for the DFA engine (>32000 states)"

So the EXACT-count form degrades cleanly and the bounded-optional form does not:
`{0,n}` builds an optional chain that blows past the memory the cap was meant to
bound, before the cap is ever consulted.

**Threshold narrowed by R7's spec critic under `ulimit -v 6000000`**, and the
numbers are worse than "it dies above 40000":

    a{0,20000}              4.68 GB peak RSS, 15.2 s   -> ACCEPTED
    a{0,25000}                                         -> SIGABRT (cap hit)
    a{0,30000}                                         -> SIGKILL
    a{0,32001} .. a{0,65535}                           -> SIGABRT (cap hit)

The `>32000 states` guard is therefore UNREACHABLE for this shape — the process
dies of memory before the state count is consulted — and the last form that
succeeds already costs 4.7 GB. That is the sharper statement of the bug: not
"large repeats crash" but "the cap that exists to prevent this cannot be
reached by the shape that needs it".

No crash of a different shape was found: nested small counts
(`((((a{16}){16}){16}){16})`, `(a{200}){200}`) and exponential subset blowups
reject cleanly with the DFA-guard message once given enough memory.

**Severity: not a miscompile.** No wrong code is emitted and nothing is silently
accepted; the failure is loud, just not clean. It still violates the softer half
of the mandate — a caller gets no diagnostic, no exit code they can interpret,
and on a memory-constrained machine the OOM killer may pick a different victim
entirely.

**Not fixed now on purpose:** FIX-1's scope is the two miscompiles, and the fix
here is a size estimate BEFORE construction (or the M4 VM engine), which is a
design decision about where the cap lives rather than a parser bug. No
`tests/known_fail/` repro: a SIGKILL is not a `perr` (the harness correctly
treats rc >= 124 as a crash, not a rejection), so pinning it needs a
purpose-built check. **Fix with:** M4, or a bounded-repeat pre-estimate.

---

_Four open issues: K2 (cosmetic), K3 and K4 (over-rejection / over-acceptance in
the class-bracket doorway, one fix — FIX-2), and K25 (compile TIME in DFA
minimization, filed 2026-08-18 out of K7's fix). K7 itself is FIXED as of
2026-08-18 ([M4.7b]). **No open MISCOMPILE remains** — K5 and K6 were fixed on 2026-08-10 by FIX-1, and K8 by R7's critic
panel the same day. Note that K8 was found in the checkpoint review OF the K5/K6
fix, in the same function, by an instrument the fix itself had not used: worth
remembering before treating a construct as finished. Performance and
architecture debt lives in docs/dev/plan.md; other engines' bugs in
docs/dev/upstream_issues.md._


## K9 — OPEN, found 2026-08-10 (D27 spec-first writer, contract lens)

`pcrec_compile()` takes a NUL-TERMINATED pattern and no length, so a pattern
containing a NUL byte is silently TRUNCATED and the compile reports SUCCESS for
a different pattern than the caller passed.

    pattern "a\0b" (3 bytes)  ->  pcrec compiles `a`, returns 0
    libpcre2 (given the length) ->  compiles the real 3-byte pattern

This is not reachable through argv or through a line-based corpus, which is why
no existing test could express it — `tests/registry/pcre2_check.c`'s
`check_embedded_nul` probes the VERB doorway and says so explicitly, noting that
"pcrec's public entry point takes a NUL-terminated pattern". That comment
recorded the limitation; nothing recorded that it produces a WRONG SUCCESS
rather than a clean refusal, which is the part that matters under the mandate.

Two honest options, and the choice is a public-API decision rather than a bug
fix: take a length in the public API (a breaking change, and DD-3 territory), or
document that patterns are NUL-terminated AND refuse a pattern whose declared
extent the compiler cannot verify. Doing neither leaves a silent wrong compile
in the library's front door.

**Scheduled:** with DD-3 (generated-API versioning/compat policy), because both
are changes to the public contract and should be decided together.

**API HALF LANDED 2026-08-17 ([M4.7c], lane/m47c):** `rx_info` already carried
`pattern_len` (D44.5, landed 2026-08-14 at the [M4.4] match-API freeze,
`src/gen/emit_dfa.c`'s `emit_info_def` — `.pattern_len = %zu` off `cx->patlen`,
the same `strlen()` at the `pcrec_compile()` entry that decides what gets
compiled) — the field this entry asked for existed in the shipped emitter
before this row was ever opened as a plan step; what M4.7c added is the
TESTING this entry's own repro needed and never got: `tests/cli/run_cli_tests.sh`
case16 is the direct library-API probe (an embedded-NUL buffer built byte by
byte, since argv cannot carry one through to `pcrec_compile()`) that PINS the
truncation this entry describes AND asserts it is now detectable — the exact
"a\0b" (3 bytes) compiles as "a" (1 byte) repro above, with the artifact's own
`rx_info.pattern_len` reading `1`, honestly reporting what was actually
compiled rather than what the caller intended. `tests/codegen/run_codegen_tests.sh`
adds the general structural coverage: `pattern_len` is the pattern's ordinary
byte count, and — the cell that would have caught a field that quietly
reported the MATCHED-byte count instead of the SOURCE-byte count — `'a\nb'`
(4 source bytes: `a`, `\`, `n`, `b`) stamps `pattern_len = 4`, not 3 (the
bytes the matcher itself walks). Contract text: docs/design/match_api_m4.md
§5's `rx_info` layout table already carries `pattern_len` at D44.5's own
ruling; no further contract-text change was needed here, and [M4.7f]'s spec
graduation inherits it as-is. **STILL OPEN**: the compile-ENTRY half (a length
parameter on `pcrec_compile()` itself, so the compiler can refuse a pattern
whose declared extent it cannot verify, rather than silently truncating and
succeeding) stays with DD-3, unchanged by this landing — a caller must still
know to check `pattern_len` against its own intended length; nothing in
`pcrec_compile()`'s signature enforces that yet.

## K10 — FIXED 2026-08-12 (MOD-0.6 phase 2, the K10 slice)

**Resolution.** `RF_CLASS_INVALID` removed from the `{U+` row
(`src/parse/registry.c`, the `\N{U+0041}` row) — the one-flag fix this entry
always said it was. `[\N{U+41}]` now falls through to the ordinary `RS_MODULE`
in-class branch in `ext.c` and reads `\N in a class requires module
'unicode-props'` at the same offset as before (measured: offset unchanged,
1/2/3 for the three repro cells below — `ext.c`'s in-class branches share one
`at`). Bare `\N` in a class is UNCHANGED (`registry.c:310`'s row correctly
keeps the flag; err 171 stays permanent). **The TEST is what this entry always
said was the real work**: the in-class sweep's one-byte-of-tail blindness
(the fourth net below) is closed in the SAME commit by extending
`registry_check.c`'s sweep to probe every tailed/body-carrying row through its
own `syntax` field wrapped in `[...]` — see `docs/design/design_notes_mod06.md` §4
for the design and `tests/registry/CLAUDE.md` for what landed. Reject-pins for
the new message + offset are in `tests/reject/run_reject_tests.sh`; mech
sabotage `S31` re-flags the row and is caught by the extended sweep.

**Original finding, kept for the history** (R10 panel, C1, found 2026-08-11 —
while probing the ambiguity guard). `\N{U+hhhh}` inside a character class was
refused as permanently-invalid, when PCRE2 recognises it. A tier-2 error,
EXACT under D26: pcrec answered REFUSE where the correct answer is "requires
module 'unicode-props'".

**Repro** (measured 2026-08-11, `build/pcrec` at 2aca7dd):

    $ build/pcrec -o /dev/null -- '[\N{U+41}]'
    pcrec: \N is not valid inside a character class (pattern offset 1)
    $ build/pcrec -o /dev/null -- '[x\N{U+41}]'
    pcrec: \N is not valid inside a character class (pattern offset 2)
    $ build/pcrec -o /dev/null -- '[a-\N{U+41}]'
    pcrec: \N is not valid inside a character class (pattern offset 3)

libpcre2 10.46, every class position including range endpoint and after `^`:

    [\N]           err 171  \N is not supported in a class      <- genuinely not a construct
    [\N{U+41}]     err 193  \N{U+dddd} is supported only in Unicode (UTF) mode
    [x\N{U+41}]    err 193
    [\N{U+41}x]    err 193
    [a-\N{U+41}]   err 193
    [^\N{U+41}]    err 193

Error 171 for bare `\N` is a real refusal. Error 193 for `\N{U+...}` is PCRE2
parsing it as an ordinary class member and then refusing the MODE — a code point
is a perfectly good class member.

**The defect.** `src/parse/registry.c:257-259`, the `{U+` row, carries
`RF_CLASS_INVALID`. It should not. The flag's definition is "PCRE2 forbids this
construct INSIDE a character class, permanently — no option, no version, no
future in which it means anything", and **the row's own `note` says the
opposite**: *"PCRE2 error 193 outside UTF mode, which is recognition, not
rejection"*. The row states 193 is recognition and then wears the flag meaning
permanent refusal.

Provenance: R9/SPEC-classes-F1 added `RF_CLASS_INVALID` to ten escapes —
`A B G K Z z C R X N` — and it landed on an eleventh row that is not one of the
ten. The bare `\N` row correctly has it; the `{U+` row inherited it.

**Fix.** Remove `RF_CLASS_INVALID` from that row. `ext.c:104-105` then answers
`\N in a class requires module 'unicode-props'`, which is the CLAIM PCRE2's 193
warrants. **The fix is one flag; the TEST is the work**, which is why this is
recorded rather than patched in the same commit as a design review.

**Why four independent nets all miss it, which is the part worth keeping**
(updated at MOD-0.2, 2026-08-11, when the first net was retired — its
successors miss it the same way, so the count of blind nets did not shrink):

- `check_tail_precedence` asked which ROW is selected; the right row IS
  selected. RETIRED at MOD-0.2, and its successors inherit the blindness for
  the same reason: `check_row_ranks` asks whether a tailed row can WIN and
  `check_arbitration_liveness` asks how often more than one recogniser
  ANSWERS — K10 is a wrong FLAG on a correctly-selected row, invisible to
  every question about selection.
- The MOD-0.2 ambiguity defect (née the R10/D29 guard) asks how many
  recognisers answer at the winning rank. One answers.
- `registry_check.c:875-876` **EXEMPTS `RF_CLASS_INVALID` rows from the in-class
  sweep by design** (`skip_flag` — RF_CLASS_INVALID since MOD-0.3d, when the
RF_CLASS_BASE half became the separate `excuse_base_cport` boolean) — so the
  flag exempts the row from the one check that would have contradicted it. A
  control that takes its scope from the field it is controlling.
- The in-class sweep's template is `"[\\%c]"`, one byte of tail context, so it
  can only ever probe `[\N]` and never `[\N{U+41}]`.
- PC-3 probes this row once, in the ATOM position only.

`tests/registry/CLAUDE.md`'s claim "`\N{U+hhhh}` versus `\N` are no longer
unswept" was true only in the atom position until this fix; the class-position
half is what MOD-0.6's tail-sweep extension (§4 of the design note) closes.

## K11 — FIXED 2026-08-11 (MOD-0.1's returned-claims epilogue, D33 §5)

**Resolution.** The four doorways now RETURN their terminal answer as an
`ExtResult` (a tagged value: `EXT_NOT_MINE`, or `EXT_REFUSAL` carrying the
diagnostic formatted at claim time), and every call site consumes the value —
`pcrec_ext_finish` is the one epilogue that renders a refusal, and each site
ends in a loud internal-error wall for any outcome it does not handle. The
`noreturn` declarations and the fall-off-the-end call sites are gone, so the
UB this entry records is structurally unrepresentable: there is no discarded
register value to relaunch and no unreachable end to fall off. Re-ran this
entry's own repro shape against the new contract (scratch tree, stub selector
`q` made to return an unhandled outcome, no other change): `a\qb` and
`[a\qb]` both exit 1 with "internal error: escape doorway returned an
unhandled outcome" at the escape's offset, deterministically, no output file
— where the old shape silently miscompiled the first and crashed the
compiler on the second. Diagnostics byte-identical across the change: a
952-pattern differential over every registry probe, every corpus pattern and
per-doorway byte sweeps compared (exit, stdout, stderr, out.c, out.h)
against the pre-epilogue build with zero differences (instrument
sabotage-validated: one reworded message → 10 caught).

**Still owed elsewhere, on purpose:** the flagged-not-reproduced hazard below
(`esc_class_value`'s value feeding `cls_set`'s 32-byte bitmap with no range
check) is NOT discharged by this fix — nothing returns a scalar yet. The
call-site wall's comment assigns the range check to the first module whose
class port returns one, with a probe that is false today (D33 §9.3).

The original entry follows, unedited, as the record of what the defect was.

## K11 (original entry) — OPEN, found 2026-08-11 (R11 panel, M4 — while probing the returning-doorway contract)

**`pcrec_ext_escape`'s two call sites are UNDEFINED BEHAVIOUR the moment that
doorway starts returning a value**, and the two behave differently in the same
binary. Recorded now rather than at MOD-0.1 because it is a CONFIRMED,
reproduced defect that the design work deliberately scoped OUT, and prose in a
design document is not where a live defect belongs.

**Latent today, and that is the only reason it is not a bug report.** Every path
in `pcrec_ext_escape` ends in `ctx_fail`, and the function is declared
`noreturn`, so no input can reach it. It becomes reachable the moment the first
semantic port lands — `unicode-props` (`\p{...}`), `classes` (`\v`) and any
assertion module all eventually need that doorway to return.

**The defect is in the CALL-SITE SHAPE**, not in any one row, so it applies to
all 41 `RK_ESC` rows and every future one. Both call sites invoke the doorway as
the LAST STATEMENT of a value-returning function with **no `return` in front of
it** — legal only because `noreturn` makes falling off the end unreachable:

    src/parse/parse.c:132-140   esc_atom          returns Ast *
    src/parse/parse.c:145-155   esc_class_value   returns int

**Repro** (scratch copy of the tree; declaration changed from `void ... noreturn`
to a value-returning form, one sentinel selector byte `q` made to return a stub
node; no other change):

    a\qb      exit 0, COMPILES, and the stub node reaches the emitted matcher —
              the discarded pointer is relaunched as esc_atom's own return value
              out of %rax by calling-convention coincidence.  5/5 runs.
    [a\qb]    *** SIGSEGV, exit 139 — build/pcrec, the COMPILER ITSELF, crashes
              before emitting anything.  3/3 runs. ***

gcc emits `-Wreturn-type: control reaches end of non-void function` at BOTH
sites — and the build still exits 0, because there is no `-Werror` by default
(`make strict` would catch it). This is the only doorway where the compiler says
anything at all: `pcrec_ext_group` and `pcrec_ext_verb` produce ZERO warnings
for the identical change, because discarding a return value is silent in C.

**Why this is worse than the group doorway's discard** (which MOD-0.1 fixes):
that one is well-defined C — deterministically the same wrong answer on every
platform. This is UB, and it is not even self-consistent across its own two call
sites in one binary. A different compiler, optimisation level or register
allocation could flip which site crashes and which silently corrupts.

**A related hazard, FLAGGED AND NOT REPRODUCED:** `esc_class_value`'s return
feeds `cls_set(a->cls, (unsigned)lo)` in `p_class` with **no range check between
them**, and `cls_set` indexes `b[c >> 3]` into a 32-byte array. A UB-tainted
`int` arriving there is a memory-safety question, not merely a correctness one.
This run happened to segfault before reaching that path. Worth its own probe
independent of this entry.

**Scheduled:** with the first module that needs doorway 1 to return — currently
MOD-0.6 (`unicode-props`), whichever lands first. **MOD-0.1 deliberately does
NOT fix it** (R11 disposition 6 / M4's ruling): MOD-0.1 owns `p_group_body`'s
discard, which is inseparable from building the interface, and bundling a
second, differently-shaped doorway fix into a large refactor is how a regression
hides. **But note `pcrec_ext_verb` shares `p_group_body` with the group doorway
and IS in MOD-0.1's scope** — see R11 disposition 12; a fix touching only the
`?` branch ships incomplete.

## K12 — FIXED 2026-08-11 (MOD-0.1's endpoint-rule slice, design §16 as R14-corrected)

**Resolution.** p_class implements the five-step evaluation order PCRE2's
5,041-pair sweep established — low's own error → high pair-open short-circuit
→ high's own error → either endpoint certifiably SET-shaped → "invalid range
in character class" → scalar ordering — using the two mechanisms the earlier
slices built for it: the returned-claims epilogue lets the range logic SEE a
doorway refusal before it fires (a claim carries `ep_set_certain`, §16.3(e)'s
verdict-shape payload), and the measured `class_expect` column is what
certifies SET-shape. Certification is deliberately scoped to rows whose
measured value covers EVERY form that reaches them: the ten char-type escapes
(the construct is its selector byte) and the bracket doorway's known POSIX
names (both sides, so `[[:alpha:]-z]` and mid-class `[x[:alpha:]-z]` are 150's
analogue too). Body-dependent rows keep the module promise — `[0-\p{Foo}]` is
PCRE2 147, not 150, so certifying `\p` would trade an over-promise for a
wrong verdict; the boundary is pinned in tests/reject/ and owned by
unicode-props' first WIDE producer (MOD-0.6 landed recogniser-only, 2026-08-12,
and deliberately kept this boundary — design_notes_mod06.md §8.2). Every cell measured first (tests/probes/probe_endpoint_k12.c,
42 cells), ten failing-then-passing pins plus seven boundary pins and two
accept-controls (counts 265/99/65, three MANIFEST entries); the 952-pattern
differential vs the pre-slice build shows exactly the one changed cell it
contains. `pcrec_ext_class_pair_opens` survives as the (bracket, high)
deviating cell's predicate, exactly as R14 ruled.

The original entry follows, unedited.

## K12 (original entry) — OPEN, found 2026-08-11 (D33 design conversation, while probing the range-endpoint rule)

**A class-type escape at a range endpoint is answered with a module promise
where PCRE2 says the range is permanently invalid.** SPEC-FA implemented the
endpoint rule for the BRACKET shape and not for the ESCAPE shape.

**Repro** (measured 2026-08-11 against libpcre2 10.46 via `tests/fuzz/pcre2_abi.h`;
`build/pcrec` at 5173a82):

                    PCRE2                       pcrec
    [0-\d]      err 150 invalid range     "\d in a class requires module 'classes'"
    [0-\p{L}]   err 150 invalid range     "\p in a class requires module 'unicode-props'"
    [a-\d] [\d-x] [a-\v] [\w-z] [\d-\w]   all err 150 in PCRE2

Controls, where pcrec is already correct and must stay so:

    [\d]        COMPILES in PCRE2 (a class member, not an endpoint)
    [\x41-z]    COMPILES — a SCALAR escape is a legal endpoint
    [a-\x41]    err 108 range out of order — i.e. accepted AS a range
    [0-\N{U+41}] err 193, the construct's own mode error, NOT 150 — scalar-shaped
    [0-\q]      err 103, the escape's own error — no construct claimed

**Severity: not a miscompile, and the wording is not the point.** Both engines
reject all of these, so nothing is compiled wrongly and no user gets a wrong
matcher. Two things make it worth recording:

1. pcrec names a module for a pattern that will NEVER compile. `[0-\d]` must
   still be rejected after module `classes` lands. That is the over-promise
   FIX-2 removed for `[[:foo:]]`, in a place SPEC-FA did not reach.
2. **The guard is the unimplemented-ness.** pcrec is right today only because
   `\d` is refused before `parse.c:213`'s range code can look at it. That code
   is `int hi = esc_class_value(cx)` with `lo > hi` and
   `for (i = lo; i <= hi; i++)` behind it. **MOD-0.2 (`classes`) removes the
   guard**, and at that moment a set-shaped value arrives in an `int`.

This is the exact shape `docs/dev/plan.md:577` already records for `(?xx)[a- ]`, one
construct over: *"pcrec is safe today only because `(?x)` is rejected outright
as 'requires module modifiers' — the guard IS the unimplemented-ness, and this
step removes it."*

**Fix:** D33 §6 — the endpoint rule becomes "did a port claim, and is the ROW'S
SHAPE set-valued", a static column covering the bracket and escape shapes with
one rule. Do not fix it as an escape-specific special case: that is the
"fixing the narrowest instance and calling it the class" error, and it would
leave a third shape (a future set-valued construct at some other doorway)
unguarded again.

**Scheduled:** with MOD-0.1 if D33 is adopted (the rule falls out of the shape
column), otherwise with MOD-0.2 (`classes`), which is the step that makes it
live. No `tests/known_fail/` repro: the current behaviour is a rejection with a
misleading message, not a wrong match, so there is no failing regression to
ratchet — the pins belong in `tests/reject/`.

## K13 — FIXED 2026-08-11 ([FIX-3], the first src/ change of the module era)

**Resolution.** `esc_class_value` now implements the class position's real
semantics, measured cell-by-cell against libpcre2 10.46 first
(tests/probes/probe_fix3.c — 41 cells, predictor stated before the run, zero
disagreements): `\0`..`\7` open an octal escape (up to three octal digits;
above `\377` it is PCRE2 error 151 with wording and offset reproduced), and
`\8` `\9` `\g` `\k` are the LITERAL characters — the complete fallback set
over all 62 `[\c]` probes. Tails re-enter the class as ordinary members
(`[\k<n>]` matches k `<` n `>`) and decoded escapes are ordinary range
endpoints (`[0-\k]`, `[\1-\7]`), with no extra code. The twelve registry rows
carried `RF_CLASS_BASE` (retired at MOD-0.3d, 2026-08-12: the same
semantics are the rows' own BASE class ports now, and the doorway IS
entered at class position, the port answering whatever the enabled set
says) — originally the doorway was never entered at class position —
exactly the `\b` shape — and registry_check's derived in-class expectation
flipped from "requires module" to "compiles" with the flag. Pins:
tests/base/class_escape_fallbacks.rxt (127 cases, written first and watched
fail — 122 failing pre-fix, the 5 `perr` blocks already failing for the wrong
reason) plus the `[\400]`/`[\777]`/`[\377]` boundary rows in tests/reject/
(the only home of the new diagnostic's text). The ATOM position is untouched.
One planned-divergence note: the fix landed BEFORE MOD-0.1's byte-identity
bar, per Frank's §18.4 ruling, so the bar measures true identity with no K13
exception entry. Original entry below, kept for the analysis.

**Historical entry (found 2026-08-11, R13 panel, C4/F21 and C3/F6; independently reproduced by the author):**

**Twelve escape rows answer the CLASS position with the wrong module.** pcrec
promises module `backrefs` for constructs that module can never implement,
because at class position they are not backreferences at all. Tier 2 under D26,
where the standard is exact.

**Repro** (measured 2026-08-11; `build/pcrec` at `5173a82`, libpcre2 10.46 via
`tests/fuzz/pcre2_abi.h`; every libpcre2 line below was re-run by the author,
not taken from the panel):

                    libpcre2                      pcrec
    [\8]        matches "8" — LITERAL     "\8 in a class requires module 'backrefs'"
    [\1]        matches "\001" — OCTAL    "\1 in a class requires module 'backrefs'"
    [\12]       octal 012                 "\1 in a class requires module 'backrefs'"
    [\k]        matches "k", not "\"      "\k in a class requires module 'backrefs'"
    [\g]        matches "g"               "\g in a class requires module 'backrefs'"
    [0-\k]      a RANGE 0x30..0x6b        "\k in a class requires module 'backrefs'"

The rows: the ten `ESC_DIGIT` rows (`\0`..`\9`) plus `\g` and `\k`.

**Three distinct wrongnesses behind one message:**

1. `[\8]` — `8` is not an octal digit, so libpcre2 falls back to the LITERAL
   character `8`. pcrec's base grammar already implements literals.
2. `[\1]`, `[\12]` — octal, which is not module `backrefs` under any reading.
   A backreference is not a class member and never can be.
3. `[\k]`, `[\g]` — libpcre2's `check_escape` treats these inside a class as a
   bad escape falling through to **the literal letter**. There is no construct
   to attribute at all.

**Severity: over-promise, not a miscompile — today.** All twelve are refused, so
nothing wrong is emitted. Two things make it worth recording:

- It is the over-promise FIX-2 removed for `[[:foo:]]`, surviving at the escape
  doorway. Module `backrefs` landing does not make `[\k]` legal; it is two
  literals.
- **It becomes a tier-1 MISCOMPILE the day `backrefs` lands**, if the class
  position is not fixed first: a real `\k` handler would be handed `[\k<n>]` and
  emit a backreference matcher for a pattern that means `[k<n>]` — a wrong
  matcher arriving *because* the module was implemented.

**Why every net misses it, which is K10's list again:**

- `check_table_to_parser` derives the expected in-class string from the row's
  own `module` (`registry_check.c:544`) — the control shares its source with
  what it controls.
- the in-class sweep's template is `"[\\%c]"`, one byte of tail, so `[\12]` is
  unreachable (`registry_check.c:875`) — the same one-byte template that hid K10.
- PC-3 probes each row's `syntax` — `\1` — at the ATOM position only.

**Related and smaller, same family:** `\0` carries module `backrefs` at the ATOM
position too, and `\0` can never be a backreference — there is no group 0. K2
records the diagnostic half of this.

**Fix:** with module `backrefs` / the octal-vs-backref row split (K2, and the
extension design's §10.7). **Do not re-attribute the rows without an in-class
sweep that carries a TAIL** — that is K10's warning, and this entry is what
happens when it is not heeded. No `tests/known_fail/` repro: the current
behaviour is a rejection with a wrong module name, not a wrong match, so the
pins belong in `tests/reject/`.

## K14 — FIXED 2026-08-11 (MOD-0.1's first slice, the D34 item-1 ruling)

**Resolution.** The missing axis is now a COLUMN: `Roadmap` — ROADMAP_PLANNED
/ ROADMAP_NEVER, with ROADMAP_NONE meaning "unset" so registry_check can
require the §17.2 pairings (RS_MODULE rows must declare one; RS_REJECTED must
pair with NEVER; RS_BASE must carry none). It lives on `RegRow` AND on
`VerbName` (per-name with the row's value as default — `(*COMMIT)` is NEVER
while `(*pla:...)` is a planned lookaround in verb spelling). A NEVER
construct in a form PCRE2 would accept now answers
"... is outside pcrec's scope and no module will implement it (see
docs/pcre2_compliance.md)" — real, refused, names no module; malformed forms
keep PCRE2's own form errors. 17 verb names (the five backtracking verbs +
MARK's synonym, the four LIMIT_*, the four NO_* knobs, the two casing
options, scs/scan_substring) and the `(?C` row carry it. The one-source
direction is CHECKED, not generated (R14/C2-F8): `compliance_section.py
--names` asserts prose-OUT-OF-SCOPE ⇔ ROADMAP_NEVER in both directions — and
its first run caught `LIMIT_RECURSION` in the tables but missing from the
survey's row. Pins: 14 rows in tests/reject/ (failing first), two manifest
entries; both dumps carry the column (15-field --list-syntax — 13 at K14
landing, MOD-0.1's later slices appended quantifiable and class_expect the
same day — 5-field --list-verbs, consumers updated). Original entry below, kept for the
analysis.

**Historical entry (found 2026-08-11, R13 panel, C5/F13; verified independently by the author):**

**pcrec names a module for constructs its own compliance survey says will never
be implemented.** D26's tier-2 row says this in as many words
(`docs/dev/decisions.md:1457`):

> **exact.** Naming a module that will never implement a construct is a defect;
> so is rejecting syntax PCRE2 accepts

**Repro** (measured 2026-08-11, `build/pcrec` at `5173a82`):

    (*COMMIT)         -> (*...) requires module 'verbs'
    (*PRUNE)          -> (*...) requires module 'verbs'
    (*SKIP)           -> (*...) requires module 'verbs'
    (*MARK:x)         -> (*...) requires module 'verbs'
    (*LIMIT_MATCH=3)  -> (*...) requires module 'verbs'
    \d                -> \d requires module 'classes'      <- ACTIVELY PLANNED (MOD-0.2)

The first five and the last are **indistinguishable to a caller**, and they are
opposite promises.

`docs/pcre2_compliance.md:301` says of the backtracking verbs, in its own words:

> `OUT-OF-SCOPE` — these are DEFINED in terms of a backtracking engine's search
> order [...] A simulation engine explores all alternatives at once, so there is
> no backtracking tree to prune. PCRE2's own DFA matcher supports none of them.

and `:221` of the `LIMIT_*` family:

> `OUT-OF-SCOPE` — these bound a BACKTRACKING search. pcrec is O(n) by
> construction, so there is nothing to limit.

These are **architectural exclusions under D22, not backlog.** Module `verbs`
will exist — it is MOD-0.4 — but it will never implement these constructs, so
naming it is precisely the defect D26 defines.

**Weaker, same family, recorded for completeness:** `(?C1)` answers "requires
module 'callouts'", and `pcre2_compliance.md:307` marks callouts `OUT-OF-SCOPE`
*"for now [...] Revisit only with a concrete customer"*. That is a genuine
"not yet" rather than a "never", so it is a lesser instance — but a caller
cannot tell it from either of the other two.

**The missing distinction is an AXIS, not a status** (C5/F13). Three axes are
needed and the table has two:

    1. what PCRE2 does        RS_BASE / RS_MODULE / RS_REJECTED
    2. what this compile does  enabled / disabled     (proposed, not built)
    3. what pcrec will EVER do  will implement / never will   <-- ABSENT

Axis 3 is a fact about pcrec's roadmap: it is not a fact about PCRE2, so axis 1
cannot hold it, and it is not a fact about one compile, so axis 2 cannot hold
it. `docs/design/extension_design.md` §7.2 proposes `RS_NOT_OFFERED` on axis 1 and
considers a permanently-disabled name on axis 2; **both are category errors and
neither supplies the missing axis.**

**Severity: over-promise, not a miscompile.** Every one of these is refused, so
nothing wrong is emitted. It is recorded because it is tier 2 and EXACT under
D26, because the fact is already written down correctly in
`docs/pcre2_compliance.md` and contradicted by the diagnostic — two homes for
one fact, one of them wrong — and because it is the SAME over-promise shape as
K12, K13 and FIX-2's `[[:foo:]]`, now at a third doorway.

**Fix:** with the status/axis question in `docs/design/extension_design.md` §7.2 and
§10.1, which is Frank's to answer. The verb rows need an answer that names no
module; `REJECTED`'s existing "agreement IS compliance" wording is close, but
these are constructs PCRE2 DOES support and pcrec will not — a combination the
vocabulary has no slot for. No `tests/known_fail/` repro: the behaviour is a
rejection with a misleading module name, so the pins belong in `tests/reject/`.

## K15 — RULED ACCEPTABLE 2026-08-12 (Frank; D26 tier 2), found 2026-08-12 (R18 panel, engine critic — the sweep-template-misses-the-boundary lesson, third recurrence)

**A verb "name" longer than 128 bytes made of NON-identifier bytes gets the
name-too-long diagnostic where libpcre2 answers "not recognized".** Tier 2
under D26 (the message CATEGORY for a refused construct, no accept/reject
divergence — the engine critic verified a non-identifier run can never match
a table entry, so pcrec always refuses either way). Pre-existing: the move to
mod_verbs.c was byte-identical; this was measured against the migrated tree
and re-confirmed against the pre-move logic.

**Root shape:** `pcrec_verb_name_extent_scan` (scans.c) terminates only on
`)`, `:`, `=`, EOF — every other byte, including space, `*`, `(`, 0x80+, is
"name". libpcre2's own name scan stops at the first non-alnum/`_` byte.
The two agree on every message for runs UNDER the cap; they part company
exactly when a non-identifier run crosses the 128-byte boundary.

**Repro** (measured 2026-08-12, `build/pcrec` at 8e7597d, libpcre2 10.46):

    (* + 130 spaces + )   pcrec: subpattern name is too long (maximum 128 code units)
                          libpcre2: err 160 "(*VERB) not recognized or malformed" at offset 2
    (* + 127 spaces + )   BOTH: not recognized / unknown-name (control: under the cap, they agree)
    (* + 129 x 'A' + )    BOTH: subpattern name is too long — exact text match
                          (control: the 128-byte rule itself is right for identifier names)

**Why every net misses it:** PC-3's only length-boundary generator
(`pool_from_lengths`, pcre2_check.c source 4) builds its 126-130-length
candidates from repeated `A`/`a` — pure identifiers; the mutation pool edits
short names only. The generators structurally cannot express "long AND
non-identifier", the same class as R16's `\N` empty-row lesson and R17's
`(?%c`-always-emits-a-byte lesson.

**RULED, 2026-08-12 (Frank): acceptable, tier 2 per D26.** The linked pair
above landed in the same session, in order: `pool_from_lengths`
(`tests/registry/pcre2_check.c`) now generates non-identifier fillers
(space, `*`, 0x80) across the 126-130 boundary; PC-3 was run with the
generator live and NO guard, and confirmed to FAIL on exactly this cell (78
mismatches, all of them the too-long/not-recognized category split
measured above, zero elsewhere) — the failing-direction measurement the
ruling needed before an exclusion could be trusted; THEN `k15_excluded()`
was added, scoped as narrowly as the ruling allows — only the category
comparison for over-cap non-identifier runs. The two controls this entry
already names stay routed through the ordinary comparison and both still
agree: under-cap non-identifier runs (both "not recognized"), and over-cap
IDENTIFIER runs (both "too long", exact text). Documented at
docs/pcre2_compliance.md's Backtracking control verbs section.

**The extent-vs-cap interaction in `pcrec_verb_name_extent_scan` is left
AS-IS, deliberately** — this ruling accepts the message-CATEGORY
difference; it does not fix the scan. Remeasure when SR-6's real verb
handler lands (module `verbs` first produces, and the extent scan's
semantics get remeasured anyway regardless of this entry) — the original
schedule note stands.

## K16 — RULED ACCEPTABLE-UNTIL-PRODUCER 2026-08-12 (Frank; D26 tier 2), found 2026-08-12 (R19 panel, engine critic — the sweep-template lesson's FOURTH recurrence, one level deeper than K15's)

**pcrec's `\p{...}`/`\P{...}` body scanner never detects libpcre2's
"malformed body byte" class: 164 of 256 possible body bytes are ERR 146
("malformed \P or \p sequence") to libpcre2 the instant they appear —
blamed at the bad byte, ignoring even the 48-char cap — where pcrec scans
past them, folds them into the name buffer, and answers its own
unknown-name/generic category at the scan-completion offset.** Tier 2 under
D26: no producer exists, both engines refuse every such pattern, and module
attribution (`unicode-props`) is correct either way; only the refusal
CATEGORY and OFFSET diverge.

**The malformed set (measured 2026-08-12, libpcre2 10.46, full 256-byte
census of the sole body byte in `\p{X}`):** 0x00-0x08, 0x0E-0x1F (C0
controls other than the whitespace five), `!` `"` `#` `$` `%` (0x21-0x25),
`{` `|` `~` DEL (0x7B/7C/7E/7F), and ALL of 0x80-0xFF. The other 92 bytes
are ERR 147 (dispatched, unknown name) — pcrec's own bucket, agreement.

**Repro** (HEAD a42d604):

    \p{!}       libpcre2: err 146 at 4      pcrec: not-recognised text at 5
    \p{L!}      libpcre2: err 146 at 5      pcrec: generic module text at 6
    47A + '!'   libpcre2: err 146 at 51     pcrec: its own 48-cap fires at 52
                (libpcre2 stops at the byte;  (same "malformed" WORD, wrong
                 the cap never engages)        reason, wrong offset)

**Why every net missed it:** three instruments independently stop at the
brace boundary — the design note's insignificant-byte census tested four
candidate bytes; `probe_uprops.c` swept all 256 TAIL bytes but never the
BODY byte; `check_uprops_differential` generates well-formed-by-construction
cells and says so in its own comment. K15 was the length axis; this is the
content axis of the same lesson.

**RULED (Frank, 2026-08-12, R19 close): acceptable tier 2, fix DEFERRED to
the first unicode-props producer** — when the scanner's buffer gains a real
consumer, the whole algorithm gets remeasured anyway, and the fix (a
measured malformed-byte class table mirroring PCRE2's accepted-name-byte
set, body-byte census like the tail already got) lands with it. Until then:
`tests/reject/`'s `\p{!}`/`\p{9}`/`\p{=}`/`\p{Script=Latin}` pins claim
PCREC'S OWN current behavior (stability, not oracle agreement), and the
divergence is documented in docs/pcre2_compliance.md. **LINKED PAIR, K15's
shape: `check_uprops_differential` must NOT gain malformed-body generation
until this is fixed** — it would fail on the divergence it newly sees; its
well-formed-only scope is deliberate and its comment says so. Forward risk
recorded: a producer built directly on the accumulated buffer without the
malformed-byte check would treat `\p{Sc!ript}` as a lookup miss rather than
a shape PCRE2 never dispatches past — the K12/K13 "guard is the
unimplemented-ness" pattern.

## K17 — FIXED 2026-08-14, found 2026-08-14 (R21 panel, engine critic — the P-1 probe the M4 engine design itself requested)

**A live tier-1 MISCOMPILE in the shipped DFA: leftmost-first priority is
lost for a lazy nullable prefix followed by a nested nullable star inside
an outer star.** K1's 2026-08-09 fix (empty iteration must reach the loop
exit with its rightful priority) did not generalise to this shape.

**Repro** (HEAD ee4a244):

    pattern (?:b*?(?:a*)*)*   subject "ab"
      pcrec  : MATCH span [0,2)
      pcre2  : MATCH span [0,1)
      python : MATCH span [0,1)

Both oracles agree; pcrec's lazy `b*?` wrongly consumes the `b` after the
empty outer iteration should have terminated the loop at pos 1.
Capture-INDEPENDENT (the `(b*?(a*)*)*` capturing form is identical), so
this is the priority subset construction, not erasure.

**Shrunk family (R21 engine critic):** diverges — `(b*?(a*)*)*`,
`(b*?(a*)+)*`, `(b??(a*)*)*`, `(b*?([a]*)*)*`, `(b*?(a*|b*)*)*`.
Does NOT diverge — `(b*?(a*)*)+` (outer +), `(b*?(a+)*)*` (inner
non-nullable), `(b*?(a*)*)` (no outer star), `(b*a*)*` (greedy prefix).
Requires all three: lazy nullable prefix, nullable inner star, outer `*`.
Absent from the corpus (no .rxt pairs a lazy quantifier with a nested
star). Random-sweep context: 910/910 span agreements with libpcre2 on
seed-5 generated capture patterns; only this family diverged.

**Why it matters beyond itself:** it refutes the STRUCTURAL form of
engine_m4.md §6.1's exactness claim (the capture-erased DFA hands the VM
an EXACT span) — the erasure half held under attack; the semantic half
(D3's priority construction computes leftmost-first exactly) is where
this lives. M4.6's DFA-prefilter hybrid would publish the wrong span with
matching-wrong capture offsets, so the FIX IS A PRECONDITION for the
hybrid, and M4.5's internal differential (span(VM) == span(DFA) over the
corpus with a three-way oracle) is the regression net.

**Scheduled:** fix in the DFA priority construction before [M4.6]
(tracked in the R21 review's disposition table); the failing repro joins
tests/known_fail/ with the fix round.

**FIXED 2026-08-14 (k17-fix lane, one commit on branch `k17-fix` carrying the
fix and its guard tests together).** `src/ir/dfa.c` `clo_visit`: the
empty-iteration redirect is no longer a ONE-SHOT. K1's fix followed a loop
entry's exit edge only on the FIRST ε re-arrival per closure (`cl->reent`, a
second generation-stamped mark array); that extra condition has no semantic
reading. The rule is a property of the ARRIVAL, not of the loop — a second
ε-arrival at the same loop entry is a second iteration that consumed nothing,
and it must end the loop exactly like the first.

**Mechanism, measured on the repro's own NFA** (states as pcrec numbers them
for `(?:b*?(?:a*)*)*`: 0 = outer `*` entry, 1 = `b*?` entry, 3 = `(?:a*)*`
entry, 4 = `a*` entry, 6 = ACCEPT). Closing the pre-set `{4}` — the position
after "a" — walks 4 → exit → 3, and 3's own empty iteration spends the
one-shot on the way to 0. The outer star then opens iteration 2, whose lazy
`b*?` PREFERS to skip, which re-arrives at 3 — and with the one-shot spent
that ε-path died. So the `b`-consuming thread (NFA state 2) was appended to
the DFA state's priority list AHEAD of the ACCEPT that the empty outer
iteration should have reached, giving the accepting two-state machine that
matches [0,2). With the redirect firing again, 3 → exit → 0 → (0 is seen,
so it redirects too) → ACCEPT lands first, accept-pruning cuts the `b`
thread, and the span is [0,1).

**Termination did not need the one-shot**, which is why removing it is safe
rather than merely lucky: a state is EXPANDED at most once per closure
(`seen`), so an unbounded walk would need an infinite suffix of redirects
alone — and the redirect graph (loop entry → its continuation) only ever
points outward past the loop, so it is acyclic and every redirect chain is
bounded by loop-nesting depth. `reent` is deleted outright; the marks array
is half the size it was. Compile time measured unchanged on twelve
nested-star/nullable-alternation shapes (worst ratio 1.06, noise).

**Why every net missed it** (house tradition; this one is the R2-M1 lesson
one level deeper, and the answer is NOT that anything excluded the shape):

1. **The corpus never had it — the code author's alphabet, D27's lesson.**
   Measured over the 612 `pattern` lines in `tests/` before this fix: 44 use
   a lazy quantifier, and only 3 of those 44 also contain a quantified group
   with a quantifier inside it. All 3 are in review_r2.rxt and all 3 are
   R2-M1's own shape — a lazy quantifier over an alternation of LITERALS
   (`(?:ab|a){0,2}?b`). Not one paired a lazy NULLABLE prefix with a nested
   NULLABLE star, and not one put that under an outer star. Tests written
   from the fix that was just made inherit the shape of that fix.

2. **The fuzzer could produce it and never did — probability, not
   exclusion.** This is worth stating precisely because the tempting
   conclusion is that a filter hid it, and no filter did: the fuzzer
   compares EXACT SPANS against libpcre2, its grammar can generate every
   piece, and nothing in `EXCLUDED FROM GENERATION` touches this class. It
   needs four independent draws to land together — a quantified group, whose
   body STARTS with a lazy nullable quantifier, followed by a nested nullable
   quantified group, with an outer star over the whole thing — and then a
   subject short enough to expose it. Joint probability ~1e-4..1e-5 per
   pattern. The existing R2 trap templates did not help, because they encode
   R2-M1's overlapping-prefix ALTERNATION, which is the level above this one.

3. **What did find it was a probe aimed at a named blind spot.** The R21
   engine critic ran the refutation that engine_m4.md §6.1's own P-1 asked
   for — "the capture-erased DFA hands the VM an exact span" — instead of
   sampling more of the same space. Seed 5 gave 910/910 agreement and said
   nothing; the family fell out of seed 99. A claim the design marked
   BELIEVED is a better place to point an instrument than a bigger random
   sample, and this file's own history says so repeatedly (K15, K16).

**Countermeasure, landed with this fix:** K17-family TRAP TEMPLATES in
`tests/fuzz/fuzz.py` (six rows beside the R2 ones), which move the class from
~1e-4 of generated patterns to a measured **4%** — 50% of trap draws, traps
being 8% of patterns. They are sabotage-validated in the direction that
matters: exhaustively expanded, the six rows give 111 distinct patterns, and
against the PRE-fix compiler those produce 28 divergences over 1887
pattern/subject cells, against the post-fix compiler 0. The second half of
the countermeasure is the three-way differential gate ruled at D44 (any 2-1
split with pcrec in the minority is a bug, never an oracle exclusion) — the
mechanism that stops the next one being explained away.

**Guard tests:** `tests/base/review_r21.rxt`, 120 cases — the six diverging
family members, one nesting level deeper (`(?:b*?(?:(?:a*)*)*)*`, which
needs the redirect a THIRD time), a witness the post-fix random sweep found
independently, and the four non-diverging neighbours as over-reach controls.
Every expectation generated from python3 `re` and re-measured against
libpcre2 10.46: 120/120 pairs, both oracles, zero disagreements.

**Validation:** the ten-pattern family check — this entry's six diverging
shapes and four neighbours, on ten subjects each — went 18 divergences → 0
with all four neighbours still correct. Random
differential sweep vs python3 `re`, 2400 generated base-tier patterns × 16
subjects over 8 seeds = 38,400 comparisons: **0 cells of K17's shape
remaining, and 14 cells across 4 patterns that are K18 (below)** — every one
of those 14 measured identical on the pre-fix binary, so the fix moved
nothing away from the oracle.

The load-bearing check is the old-binary-vs-new-binary isolation, which asks
the right question directly — not "is pcrec correct" but "did this diff move
any span, and in which direction". 7 seeds × 408 patterns × 18 subjects =
**50,400 cells: 294 changed, 294 of those 294 old-wrong → new-right, 0
regressed, 0 both-wrong.** (The 294 is inflated by the eight positive-control
patterns being re-injected on every seed; the point of the count is the
direction, which is unanimous.)

**Blast radius by EMITTED SOURCE** — the stronger net, and the one
run_trie_identity.sh's comment argues for over subject sampling, because it
cannot miss a difference that the sampled subjects happen not to reach.
Emitting C with the pre-fix and post-fix compilers over 4500 generated
patterns: **4477 byte-identical, 23 differing** — of which 18 are the six
injected controls re-emitted on each of three seeds, so only FIVE generated
patterns changed at all:

    ((?:([^a]{0,2})|(?:[a-c])??)+)*      (?:((?:[ab]{1,2}|[^a]*?){1,2}){2,})*
    c?(?:(?:a?)+|[ab]{2,})*              ((?:(?:[a-c]*|.*)+?)+)*
    ((?:(a*){1,2}|[a-c]{1,2}){2,})*

Across all 23, 76 span cells moved, 76 of 76 toward the oracle, 0 regressed,
0 both-wrong. So the fix's reach is precisely the shape it was aimed at, and
for 99.5% of the sampled language the compiler emits the same bytes it did
before. Full `make test` green, `make strict` clean.

The first isolation attempt reported "0 changed" over 36,000 cells and was
DISCARDED rather than reported: its generator used a broader quantifier
alphabet and never produced a K17 shape at all, so it was a control that
could not have failed — the recurring lesson in this file about checks that
share a blind spot with the thing they check.

**IT DID NOT CLOSE THE CLASS — see K18.** The sweep that validated this fix
also found a structurally distinct sibling that this fix does not reach and
never did: `(?:(?:a|b*?)?)*` on "ab", still [0,2) against both oracles'
[0,1). K17's "requires all three: lazy nullable prefix, nullable inner
star, outer `*`" was a description of the shrunk family, not of the defect
class. Do not read this entry as evidence that the priority construction is
now exact.

---

## K18 — FIXED 2026-08-15, found 2026-08-14 (the K17 fix's own validation sweep)

**A second live tier-1 MISCOMPILE in the shipped DFA, the same root design
fact as K1/K17 and NOT fixed by either: the empty-iteration redirect cannot
be reached through an ALREADY-SEEN NON-LOOP epsilon state.** K17 widened
when the redirect fires AT a loop entry; this shape dies one state short of
ever arriving at one.

**Repro** (k17-fix HEAD, i.e. WITH the K17 fix applied):

    pattern (?:(?:a|b*?)?)*   subject "ab"
      pcrec  : MATCH span [0,2)
      pcre2  : MATCH span [0,1)
      python : MATCH span [0,1)

**Mechanism.** For `(?:(?:a|b*?)?)*` pcrec builds 0 = outer `*` entry
(exit → ACCEPT), 6 = the `?` split, 5 = the alternation split, 2 = `a`,
3 = `b*?` entry, 4 = `b`, and **1 = an N_EPS, the outer star's loop-back
edge**. Closing the pre-set `{1}` — the position after "a" — marks state 1
seen immediately, since it IS the entry point. The walk then reaches the
alternation, emits thread 2, and tries `b*?`, whose lazy PREFERRED branch is
its exit — and that exit edge points at state 1. (**The load-bearing word is
PREFERRED, not lazy** — R23 S8, see the correction below the control list: a
greedy nullable arm written FIRST reaches the same state the same way.)
State 1 is seen and is not
a loop entry, so `clo_visit` returns dead, one hop short of state 0, whose
redirect would have produced the ACCEPT. Thread 4 (`b`) is emitted instead,
ahead of the ACCEPT reached afterwards, and the DFA over-consumes.

**Diverging family (measured):** `(?:(?:a|b*?)?)*`, `((?:a|b*?)?)*`,
`(?:(a|b*?)?)*`, `(?:(?:a+|b*?)?)*`, `(?:(?:a|b??)?)*`, `(?:(?:a?|b*?)?)*`,
`(?:(?:a|b*?)?)+` (on "aab"/"aabb"), `(?:(?:[a]|[b]*?)?)*`,
`(?:(?:a|c|b*?)?)*`. **BOTH ENGINES** — `^(?:(?:a|b*?)?)*` diverges
identically on ENG_ATTEMPT, which is K1's R2-S1a lesson repeating: do not
scope this to one engine without measuring.
**Does NOT diverge** (each removes one ingredient; these are EMPIRICAL
controls — the mechanism above was traced only on the minimal repro, so do
not read a cause into any single row): `(?:(?:a|b*)?)*` and `(?:(?:a|b?)?)*`
(greedy inner), `(?:(?:b*?|a)?)*` (lazy branch preferred),
`(?:(?:a|b*?)*)*` (inner `*` not `?`), `(?:(?:a|b*?))*` (no `?` wrapper),
`(?:(?:a|b*?)?)` (no outer quantifier), `(?:a(?:b*?)?)*` (concatenation, not
alternation), `(?:(?:a|)?)*` (an empty alternative instead of a lazy
quantifier). Note that unlike K17, an outer `+` does NOT save the shape.

> **CORRECTION 2026-08-15 [R23 S8]: two of those parenthesised causes are
> wrong, and their mirror images are LIVE MISCOMPILES.** The rows above still
> measure as stated — each of those patterns really does answer correctly —
> but the reason given for three of them is ARM ORDER, not the ingredient
> named. The defect does not need laziness. It needs the arm whose exit edge
> lands on the already-seen ε state to be the PREFERRED one, and a GREEDY
> nullable arm achieves that simply by being written FIRST:
>
>     (?:(?:b*|a)?)*        "ba"   pcrec [0,2)  both oracles [0,1)   <- "greedy inner", swapped
>     (?:(?:b?|a)?)*        "ba"   pcrec [0,2)  both oracles [0,1)   <- ditto
>     (?:(?:(?:b|)|a)?)*    "ba"   pcrec [0,2)  both oracles [0,1)   <- an EMPTY arm, no quantifier
>     (?:(?:b?|a)(?:b?|d))* "ba"   pcrec [0,2)  both oracles [0,1)   <- CONCATENATION of two
>                                                                       nullable alternations
>
> So "greedy inner" does not save the shape (arm order did), "an empty
> alternative instead of a lazy quantifier" does not save it (arm order did),
> and "concatenation, not alternation" does not save it either. Both oracles
> agree on all four; the divergence is pcrec's. All four are fixed by the
> design note's recommended repair, which covers this sub-case already — the
> defect here is in this entry's CHARACTERISATION and in the acceptance
> corpus, not in the repair.
>
> **Consequence for the corpus below.** All 15 patterns in the .rxt file are
> the lazy shape and its only two non-lazy entries are CONTROLS, so none of
> the four witnesses above is on file. The rewrite lane's guard corpus owes an
> ARM-ORDER axis: every diverging shape in both orders, greedy and lazy
> nullable arms (`k18_memo_design.md` §1.5 and §5 item 1). They are NOT added
> to `tests/known_fail/` here — the ratchet counts that file, and the rewrite
> lane re-scopes the corpus when it moves it live.
>
> This entry's own warning — "do not read a cause into any single row" — was
> right, and was not enough: the causes were written into the parentheses
> anyway, and a reader building a corpus from them built a lazy-only one.

One of these controls is worth reading before trusting the others: for
`(?:(?:b*?|a)?)*` the closure at the position after "a" fails in EXACTLY the
way traced above — thread `b` ahead of the ACCEPT — and the pattern is
correct anyway, because the preferred lazy branch makes the START state
accept an empty match, so both pcrec and both oracles answer [0,0) and the
broken closure is never consulted. A control passing does not mean the
mechanism is absent there; it means the mechanism is not observable there.

**It is reachable by accident, not just by construction.** The four witnesses
below are what a 38,400-comparison random sweep threw up on its own, before
any shrinking; they are recorded because the shrunk repro above makes the
shape look more contrived than it is. All four measured IDENTICAL on the
pre-K17-fix binary, so they are this defect and not fallout from that fix.
The first three are visibly the `(...?)*` shape; the fourth is listed as
same-SIGNATURE (over-consumes by exactly the trailing byte) rather than
same-mechanism, because only the minimal repro's NFA was traced.

    (?:(?:(?:a+|[a-c]*?)?|(?:a+){2,})?)*   "ab"   [0,2) vs [0,1)
    ((?:(?:a?){1,3}?|.+?)*)+?              "ab"   [0,2) vs [0,1)
    ((?:(?:c{1,3}?|.*?)|(b{1,3}?)+?)?)*    "cba"  [0,2) vs [0,1)
    (?:(?:b+|[^a]??)+?(?:a?|[^a]+)+|b{3})+ "abc"  [0,3) vs [0,2)

**Why the K17 fix cannot reach it, and what a real fix costs.** Both bugs are
the same underlying fact: **`clo_visit`'s `seen` set is a GLOBAL per-closure
memo, but the empty-iteration rule makes a closure's result depend on which
loop iterations are currently OPEN on the walk's own path.** Dedup by NFA
state alone conflates two arrivals that the backtracker would treat
differently. K17 was the sub-case where the conflated state is itself a loop
entry, and there the redirect is a complete repair; K18 is the sub-case where
it is an ordinary ε state on the way to one, and no rule stated at loop
entries can see it. The principled fix is to key the closure memo on
(state, open-loop-set) rather than on state alone — a path-sensitive closure,
with the open set maintained as a properly-nested stack. That is a real
rewrite of `clo_visit` with a real compile-time-blowup risk (the memo must
distinguish contexts without losing the dedup that R2-A4's quadratic fix
bought), which is why it is NOT bundled with K17's one-line change.

**Severity: tier 1, same as K17** — a wrong span from the shipped compiler,
both oracles agreeing against pcrec, capture-independent. It carries the same
consequence K17's entry records for M4: it is a precondition for [M4.6]'s
DFA-prefilter hybrid, which would publish this wrong span with matching-wrong
capture offsets, and M4.5's span(VM) == span(DFA) internal differential is
the net that must catch it.

**Repro on file:** `tests/known_fail/k18_empty_exit_through_seen_eps.rxt`
(165 cases: the eight diverging shapes plus seven over-reach controls that
pass today and must still pass after a fix). Every expectation generated
from python3 `re` and re-measured against libpcre2 10.46 — 165/165 pairs,
both oracles, zero disagreements.

**Scheduled:** ASSIGNED by the manager at R21 close (2026-08-14):
DESIGN-FIRST, before [M4.6] opens — a short design note measuring the
compile-time cost of the (state, open-loop-set) memo (the lane's sketch
of the naive path-local version was exponential on `(?:a*|b*){20}`-class
shapes, so the design must find the bounded formulation or a narrower
sound rule), panel-eyed with whatever review gates M4.6's start, then the
rewrite as its own lane with K17's validation methodology (blast-radius
emitted-source diff + isolation sweep with an injected positive control).
Until then: the known_fail ratchet holds it visible; [M4.5]'s three-way
span differential is the net; [M4.6] does NOT open with K18 unfixed
(same precondition status as K17, R21 review E-1 disposition).

**DESIGN NOTE DELIVERED 2026-08-15: `docs/design/k18_memo_design.md`**
(PROPOSED, **AMENDED PER R23** — `docs/dev/reviews/2026-08-15-r23-k18-memo.md`;
the rewrite lane has NOT opened and this entry stays OPEN). It recommends the
(state, open-loop-context) memo this entry sketched, plus an empty-context
fast path, and it settles three things this entry left as expectations:

* **The cost is polynomial, and smaller than the note first reported.** The
  note's original Θ(d⁴) cost law and its 39 s worst case were a PROTOTYPE BUG
  (R23 S16: `clo_visit` restored the open-loop stack's depth but not its
  entries), not a property of the design. Re-measured on the fixed prototype:
  the deepest pattern the parser accepts — 250 nested nullable stars —
  compiles in **0.35 s** against the shipped compiler's 0.004 s, contexts fit
  d²/2 and redirects d³/3, the corpus maximum depth is 4, and aggregate
  inflation is **x1.004 expansions / x0.996 visits**. This entry's "real
  compile-time-blowup risk" is real but small, and **no threshold is proposed
  or needed** — the note's §6 ruling request is WITHDRAWN.
* **The exponential the entry attributes to the naive path-local version is
  CONFIRMED, and it is the absence of the memo, not the path-sensitivity.**
  MEASURED Θ(2ⁿ) on `(?:a*|b*){n}`, out of budget at n=22.
* **This file's 165 cases are NOT a sufficient acceptance criterion.** A
  two-line alternative (an already-seen ordinary ε walked through rather than
  killing the walk) passes all 165 and is still wrong: over a dense
  18,858-pattern sweep it differs from the recommended design on 83 patterns /
  98 cells, and the oracle agrees with the recommended design on 98 of 98.
  Every one is a `{0,2}`-bodied shape — the same conflation happening at a
  SPLIT instead of at an ε, which is a THIRD sub-case of the root fact and is
  not covered by the family recorded above. The rewrite lane owes those 83 a
  guard corpus.
* **A FOURTH sub-case, added by R23 S8: the ingredient is the PREFERRED
  alternation arm, not laziness** — see the correction under this entry's own
  control list. The guard corpus therefore also owes an ARM-ORDER axis, and
  the note's §5 item 1 specifies it.

**FIXED 2026-08-15 (k18-rewrite lane, branch `k18-rewrite`).** `src/ir/dfa.c`:
the epsilon closure is now PATH-SENSITIVE. The memo is keyed on (state,
OPEN-LOOP CONTEXT) and the empty-iteration redirect fires on "this loop is
OPEN on my path" rather than on "this state has been seen somewhere in this
closure" — the design note's prototype A2, unchanged in semantics.

**Mechanism.** A context is an interned chain: ctx 0 is the empty open-loop
stack, every other ctx is (parent ctx, loop-entry state). Taking a loop's BODY
edge opens the loop (interning a child context); a redirect pops the
re-arrived loop AND everything above it by moving to that context's parent.
The memo suppresses a re-arrival only at the same (state, ctx), so the second
arrival at K18's already-seen ε state — which is now in a DIFFERENT context —
survives, reaches the outer loop entry one hop later, and redirects to the
ACCEPT at the priority position the empty iteration earns.

Three properties of the implementation are worth reading before editing it:

* **The empty-context fast path is not optional.** With the stack empty,
  (state, 0) and `state` are the same key, so ctx 0 keeps the pre-K18
  per-state stamp array. Without it a fuzz-found pattern did byte-identical
  work 7x slower, all of it one hash probe replacing one array access 15.7
  million times (note §2a).
* **`clo_walk` has NO recursion.** The design as prototyped descends once per
  CONTEXT rather than once per state, which measures 31,377 C frames at the
  parser's 250-paren nesting cap against the old closure's 253 — ~7 MB of the
  default 8 MB stack, and an outright stack overflow under AddressSanitizer at
  nesting depth 210 (§5 item 12, the one defect R23's own re-measurement
  found). The split's preferred branch now pushes its deferred branch onto an
  explicit LIFO instead, so C-stack depth no longer depends on the pattern.
  `tests/base/k18_deep_nesting.rxt` is the guard, since the rest of the corpus
  tops out at loop-nesting depth 4.
* **The chain is immutable, and that is load-bearing.** The design's hardest
  prototype bug (R23 S3) was a frame restoring the open-loop stack's depth but
  not its ENTRIES, which silently lost redirects — the very defect being
  repaired, reintroduced by the repair. A deferred branch here carries its
  context as one interned int that nothing can rewrite, so the bug is not
  expressible. Both of §3's invariants ship as live `DFA_INVARIANT` aborts:
  the redirect's open loop is the chain top, and no already-open loop is ever
  pushed.

**Guard corpus** (`tests/base/`, moved and grown in the same commit as the fix
— the known-fail ratchet enforces that pairing):

* `k18_empty_exit_through_seen_eps.rxt` — the original 165 acceptance cases,
  moved out of `tests/known_fail/` (26 of which failed before this fix);
* `k18_arm_order.rxt` — 54 patterns / 667 cases, the R23 S8 axis: every
  diverging shape in BOTH alternation orders, greedy as well as lazy nullable
  arms, the empty-alternative and concatenation forms that contain no lazy
  quantifier at all, and nine over-reach controls including K17's own repro;
* `k18_split_shapes.rxt` — 83 patterns / 609 cases, the `{0,2}`-bodied family
  where the conflation happens at a SPLIT rather than an ε. This is the file
  that matters most: the cheap two-line candidate repair passes all 165 of the
  acceptance cases and gets all 98 of these cells wrong;
* `k18_deep_nesting.rxt` — 8 patterns / 24 cases, the resource guard above;
  also the deliberate GROW-PATH test for the three tables the repair adds
  (31,627 contexts against initial capacities of 64 and 256), which neither
  the corpus nor the fuzzer would otherwise drive past their first
  allocation;
* `k18_cost_gates.rxt` — 6 patterns / 29 cases whose point is COMPILE TIME
  rather than spans, riding the harness's own per-invocation pcrec budget:
  the fuzz-found witness that caught the design prototype's 7x
  constant-factor regression on byte-identical work (a `perr` block — every
  binary refuses it on the DFA state cap AFTER building 32,000 states), and
  bounded-repeat × nullable-loop swept in k, the family that runs at
  open-loop depth 1 and would therefore be invisible to any depth-based gate.

1,329 new cases, every expectation generated from python3 `re` AND libpcre2
10.46 with **zero disagreements** (D44's three-way rule). The full `.rxt`
corpus goes **1,704 → 3,198 cases**.

**Non-vacuity, per file, measured by running the PRE-FIX compiler against the
new corpus** — a guard corpus its own bug passes is a control that could not
have failed:

| file | cases | pre-fix failures | post-fix |
|---|---|---|---|
| `k18_empty_exit_through_seen_eps.rxt` | 165 | 26 | 0 |
| `k18_arm_order.rxt` | 667 | **62** | 0 |
| `k18_split_shapes.rxt` | 609 | **63** | 0 |
| `k18_deep_nesting.rxt` | 24 | 0 | 0 |
| `k18_cost_gates.rxt` | 29 | 0 | 0 |

The last two files are the deliberate exceptions and are marked as such: they
guard RESOURCE classes, so their failure modes are a stack overflow under
`make asan` and a blown compile budget, not a wrong span. They are
sabotage-validated in those directions instead — the design's own prototype,
built with the identical asan flags, dies with `stack-overflow` at nesting
depth 210 and 250 where the shipped repair compiles both (0.84 s at 250 under
asan), and the same prototype takes 13.5 s on the cost file's `perr` witness
against the shipped 0.62 s.

The K18 fuzz TRAP TEMPLATES (`tests/fuzz/fuzz.py`, nine rows beside K17's
six) are validated the same way and in the direction that matters:
exhaustively expanded they give 64 distinct patterns / 543 cells, **56
divergences against the pre-fix compiler and 0 against the fixed one**. Both
fuzzer seeds run to completion on the fixed compiler with 0 content
divergences, 0 accept/reject divergences and **0 pcrec compile timeouts of
400 patterns each** — a compile that never finishes is invisible to a
differential that compares answers, so the budget is reported as a count.

**Validation.** Emitted-source blast radius against the pre-fix compiler:
**622 corpus patterns, 555 accepted by both, 547 byte-identical, 8 differing,
0 accepted by only one — and the 8 are exactly the eight K18 shapes**, which
is the design note's §4.2 prediction reproduced pattern for pattern. Over the
lane's dense 18,858-pattern shape space: 18,609 identical, **249 differing**.
Changed-cell direction against python3 `re`, both sweeps: **251 changed cells,
251 old-wrong → new-right, 0 regressed, 0 both-wrong** (226 on the shape
space, reproducing §4.3 digit for digit; 25 on the eight corpus patterns).
Full `make test` green with the corpus grown by 1,494 cases (the 1,329 new
plus the 165 activated); `make strict`,
`make ubsan`, `make asan` (the deep-nesting case included), `make lint`,
`make bench`, `make mech` green; the trie-identity gate run explicitly, since
a path-sensitive closure over an epsilon graph the M2.8 trie CHANGES is
exactly what that gate's erasure argument was not written for.

**What this does NOT close.** The class is K1/K17/K18's shared root fact, and
this repair addresses that fact rather than a shape — but the same sentence
was written about K17. The honest statement is narrower: the closure now
computes the empty-iteration rule as stated, the three known sub-cases (arrival
AT a loop entry, arrival THROUGH a seen ε state, conflation at a SPLIT) are
one mechanism, and the corpus above covers all three in both arm orders.

---

## K19 — FIXED 2026-08-15, found 2026-08-15 (D45's own ruling; the battery that pegged cc1 for 100+ minutes)

**A shipped compiler defect in [M4.5b]'s VM emitter: a bounded repeat over a
choice-bearing body emits megabytes of C that no cap stopped, and gcc's
compile time on that shape is superlinear.**

Not a miscompile — the emitted matcher is CORRECT. The defect is
DISPROPORTION between what the author writes and what the compiler emits, and
its consequence is a build that never finishes.

**Repro** (before the fix):

    $ build/pcrec -p rx -o /tmp/o.c '((a)|b){0,4000}c'   # 16 characters
    $ wc -l /tmp/o.c
    113545 /tmp/o.c                                       # 3.5 MB
    $ gcc -O2 -c /tmp/o.c                                 # minutes
    $ gcc -O1 -fsanitize=undefined -c /tmp/o.c            # 100+ minutes

`PCREC_MAX_VM_NODES` did not stop it: it refused `(a|b){0,65535}` and let this
through, which is what D45's consequence 1 records as the gap.

**Why the emitted size is linear in a number written in three characters:**
engine_m4.md §3.3's ruled reading is that a bounded repeat REPLICATES its body
(PCRE2's own semantics — each copy is an independent opportunity to match), so
`{0,N}` over a body containing an alternation costs N copies of that body's
code.

**Why gcc goes superlinear on it**, measured (project box, 2026-08-15; the full
curves are in docs/testing.md's battery section): the cost tracks the number of
ADDRESS-TAKEN LABELS, not the label count. At the same size, `(a×2000)b` emits
2004 labels with ZERO address-taken labels and compiles in 2.70 s at -O2, while
`((a)|b){0,200}c`'s 2003 labels with 400 address-taken labels take 11.21 s.
Each `&&label` becomes a potential successor of the VM's single `goto *`, so the
indirect edge's fan-out is what gcc's dataflow goes superlinear in. It is R1
A-3's computed-goto cliff, reached from the VM side — which REFUTES
engine_m4.md §2.1 and §13's P-6 ("the VM should therefore never approach" it)
and answers §12's ASK-7 unbidden.

**Fixed** by `PCREC_MAX_VM_REPEAT_COPIES = 64` (src/core/limits.h), checked in
the pre-pass BEFORE emission, with a diagnostic that names the replication
count, the limit, and the two ways out. The number is measured: at 64 copies
the worst allowed artifact costs 1.40 s at -O2 (28% of D45's 5 s plain budget)
and 2.30 s under UBSan; 128 copies would sit at 92% of the plain budget.

The cap is on REPLICATION rather than total size on purpose. A first draft
capped total resume points and refused a 200-branch capture-bearing keyword
alternation, which is entirely healthy — its size is proportionate to the
pattern. Sabotage S44.

**Residual, open and recorded**: a very long capture-bearing LITERAL still
emits a large artifact with zero resume points (20,000 characters → 2.3 MB,
>180 s at both -O1 and -O2), bounded only by `PCREC_MAX_VM_NODES` at 131,072 —
far above what the compile budget absorbs. That shape is proportionate to the
pattern, so the replication cap correctly does not see it, and D45's harness
wrapper now catches it loudly instead of hanging. Lowering the node cap would
refuse patterns that work today and is a ruling, not a fix.

---

## K20 — FIXED 2026-08-15, found 2026-08-15 (while probing K19's boundary)

**A shipped CRASH in [M4.5b]'s VM emitter: unbounded C recursion on the AST
spine, SIGSEGV on the default path with no special flag.**

    $ build/pcrec -p rx -o /tmp/o.c "($(python3 -c "print('a'*20000)"))"
    Segmentation fault (core dumped)          # rc 139, empty stderr

The threshold tracks `ulimit -s` — 8 MB crashes at ~20,000 characters, 2 MB at
~6,000, 64 MB survives — which is what identifies it as stack exhaustion
rather than anything subtler. Capture-bearing patterns only (the VM path);
larger sizes were masked on the default path because the DFA state cap fires
first, but `--engine=vm` crashed at every size above the threshold.

**Root cause**: three pre-pass functions added at [M4.5b] — `vm_nullable`,
`vm_count_slots` and `vm_cost` — recursed on `A_CAT`/`A_ALT` children, so a
left-leaning spine of N elements recursed N deep.

**This is DD-10 / D10 / R1 R-2's bug class for the THIRD time.** `src/ir/nfa.c`
flattens its `A_CAT`/`A_ALT` spines iteratively for exactly this reason and
says so in a comment; `vm_emit` (the emitter proper) was written to match; the
three helper functions beside it were not, and nothing in the tree could see
the difference because no test compiles a 20,000-character pattern.

**Fixed** by flattening all three iteratively, matching nfa.c. Verified at a
1 MB stack: a 100,000-character capture-bearing literal now compiles, where
8 MB previously failed at 20,000 — the recursion is gone, not merely deeper.

**The lesson worth keeping** is not "flatten spines" — the tree already knew
that — it is that the rule was recorded against ONE function rather than
against the AST shape, so the next three functions to walk the same shape
inherited nothing. Any new walk over `A_CAT`/`A_ALT` needs the same treatment,
and `vm_nullable` now carries the comment that says so.

## K21 — FIXED 2026-08-15 (found same day, R23 semantics critic S15; triaged by a follow-up read-only probe)

**The `--emit-main` convenience `main()` treats `<prefix>_search`'s
three-valued return as a boolean, so VM step/frame-budget exhaustion
(RX_ERR_STEPS/RX_ERR_FRAMES, both negative and both C-truthy) is reported
as a successful match with UNINITIALIZED capture-span output.**

**Repro:**

    pattern: (?:(?:(?:(c??){0,4}?(?:d{0,2}?a{0,2}){1,2}){0,3})+.(?:(d{0,2}){2,3}((?:[a-c]{1,2}?|b*?){1,2})?){0,2})*
    subject: "" (this pattern exhausts the step budget on every subject tried,
                 up to length 3)
    the --emit-main binary prints: match 32768 140721206985752  (varies run to run)
    correct behaviour: rx_search returns RX_ERR_STEPS (-2); there is no match
                       to report

Minimal ingredient: any pattern whose VM-emitted `rx_search` exhausts
`RX_STEP_BUDGET`/`RX_BT_FRAMES` on the tested subject. Two more witnesses
(R23 appendix, S15; probe findings) show the same mechanism producing
small plausible-looking wrong numbers instead of obvious garbage — zeroed
stack bytes printed as `match 0 0` — which makes this bug easy to mistake
for a semantic miscompile. Do not triage a "plausible but wrong span from
an emit-main binary" as a priority/closure bug without first ruling out
RX_ERR_STEPS/FRAMES by checking the raw `rx_search` return code (the probe
itself chased that false lead partway).

**Mechanism.** `pcrec_emit_main` (src/gen/emit_dfa.c:993, shared by both
emitters): `if (%s(...caps)) { printf("match ...", caps[0][0], caps[0][1]);`.
The search's give-up path returns the negative sentinel BEFORE calling
`rx_caps_out`, so `main()`'s stack `caps` array is never written; C
truthiness makes -2/-3 take the match branch and print uninitialized
memory. `tests/fuzz/fuzz_driver.c:130-133` already discriminates the
sentinels correctly (the fuzzfix arc's fix) — `pcrec_emit_main` is a
separate call site that arc did not touch. DFA-only artifacts never return
the sentinels, so the bug is VM-artifact-only.

**Severity.** Not a wrong match from the engine — `rx_search` itself
returns the correct sentinel — but the CLI-facing convenience `main()`
fabricates match data when the honest answer is "budget exhausted", which
is worse than silence (D26 tier-1-adjacent).

**Fix direction.** Branch three ways in `pcrec_emit_main` (rc==1 match,
rc==0 nomatch, rc<0 a distinct give-up line + distinct exit code),
matching fuzz_driver.c; plus a test that forces a budget exhaustion under
--emit-main and pins the three-way stdout. Scheduled: immediate small
lane (2026-08-15, R23 close), not deferred.

**Fix landed 2026-08-15.** `pcrec_emit_main` (src/gen/emit_dfa.c) now
captures `rc = %s(...)` and branches on the VALUE: `rc == 1` prints
`match START END` and exits 0 (unchanged), `rc == 0` prints `nomatch` and
exits 1 (unchanged), and `rc < 0` prints a one-word honest give-up line —
`steps` or `frames`, distinguishing which sentinel fired, via the
`%s_ERR_STEPS`/`%s_ERR_FRAMES` macros the same emitted file already
defines — and exits 3, a code that collides with neither match/nomatch
(0/1) nor this same `main()`'s own usage-error exit (2). The wording
mirrors `tests/fuzz/fuzz_driver.c`'s existing `"steps"`/`"frames"` tone
(D26: the exact word is ours to choose; kept short, stable, and
consistent with the driver that already got this right).

Pinned by `tests/cli/run_cli_tests.sh` case15: two small, reliable
witnesses driven to their own limit exactly the way
`tests/vm/run_vm_tests.sh` §4/§4.5 already do — `(a*)*b` under
`--engine=vm --step-budget=50` (step budget) and `((a)|b)*c` under
`--engine=vm --backtrack-frames=4` (frame capacity) — each asserting the
exact stdout line and exit code 3, PLUS the non-firing controls (the same
two patterns under an ample budget/capacity still print an honest
`match START END`), so a give-up path that fired unconditionally could
not pass silently. Verified FAILING against the pre-fix emitter first
(4 of case15's 10 assertions fail — exactly the give-up-path ones; the
match/nomatch and control assertions stay green either way), then
verified green again after restoring the fix. No consumer of the old
two-line `match `/`nomatch` --emit-main contract was found scanning
tests/, scripts/, docs/ for a parser that would choke on the new third
line — the existing green tests never reached the give-up path before
this fix.

**Class closure (2026-08-15, same lane, on review request; 4 of 4
fixed).** K21 is one instance of a recorded SHAPE — `if (rx_search(...))`,
testing a three-valued return as a boolean, so a negative give-up
sentinel takes the match branch under C truthiness — not a one-off in
`pcrec_emit_main` alone. Per the K20 lesson (record against the shape,
not the site), the other known readers of `rx_search`'s return were
surveyed:

- `tests/fuzz/fuzz_driver.c` — already correct (the fuzzfix arc,
  `c225a9f`/`7e27c19`): discriminates `found == 1`/`== 0`/
  `RX_ERR_STEPS`/`RX_ERR_FRAMES` explicitly.
- `tests/harness/driver.c` — HAD the bug (`if (found) { ...caps... }`),
  now FIXED in this same lane: discriminates explicitly, prints
  `steps`/`frames` and exits 3 on a give-up (matching
  `pcrec_emit_main`'s exit-code choice for cross-site consistency), and
  `tests/harness/run.sh`'s per-case loop gained an explicit `trc -eq 3`
  branch treating it as a HARD harness-level failure, the same shape as
  its existing timeout/crash branches — never compared against a
  `match`/`nomatch` expectation. Verified live: the pre-fix driver
  against a `--engine=vm --step-budget=50` artifact printed a fabricated
  `match` line with garbage capture spans; the fixed driver correctly
  prints `steps` and exits 3 on the identical artifact/subject.
  Dormant over the base .rxt corpus (no `flags`/`features` directive can
  select `--engine=vm` or a tiny budget), so no .rxt test was added — see
  the driver's own comment and docs/testing.md's driver-protocol section.
- `tests/registry/pc4_driver.c` — HAD the bug too
  (`if (rx_search(s, len, 0, caps))`), independently of the `89ccd89`
  "sibling" fix in the fuzzfix arc, which fixed a DIFFERENT bug in this
  same file (the `caps[RX_NCAPS][2]` stack-array sizing hazard, since this
  driver is compiled once against a throwaway pattern and reused across
  the PC-4 sweep) — `89ccd89` never touched the truthiness check, so this
  file was genuinely still open when it was first flagged here 2026-08-15.
  **NOW FIXED, same day, same lane.** pc4_driver.c is a DIFFERENTIAL
  driver, not a match/nomatch-only one, so the fix follows a different
  shape from the other three: `pc4_check.c` (the libpcre2 side) already
  had a bucket for a NON-comparable outcome — `mlimits`, libpcre2's own
  match-time give-up, counted separately, excluded from `cells`, never
  compared as a verdict, asserted zero. pc4_driver.c now discriminates
  `found == 1`/`== 0`/otherwise explicitly and prints `giveup steps`/
  `giveup frames` for that subject instead of a fabricated verdict;
  `pc4_check.c` gained the symmetric `pcrec_giveups` bucket, checked
  BEFORE the match/nomatch comparison so a give-up can never enter it as
  a fabricated match, and asserted zero alongside `mlimits`. Verified two
  ways: (1) directly — PC-4's real 271-subject set has nothing long
  enough to burn a tiny step/frame budget, so a scratch driver using the
  identical discrimination logic against a `--engine=vm --step-budget=50`/
  `--backtrack-frames=4` artifact was run standalone, correctly printing
  `giveup steps`/`giveup frames`; (2) `pc4_check.c`'s new branch verified
  in the FAILING direction by splicing one synthetic `giveup steps` line
  into a real `\d` sweep's results file — `cells` dropped by exactly 1,
  `pcrec_giveups` fired naming the count, and no spurious match/nomatch
  disagreement appeared for that cell. The real `run_pc4.sh` sweep is
  unaffected (still dormant: DFA-only pattern space) — unchanged
  273/232/41/62,872/0 populations. See tests/registry/CLAUDE.md for the
  full account.

## K22 — OPEN, found 2026-08-16 (possessify lane, while probing pass compile-time on large bodies)

Nested bounded repeats HANG THE COMPILER with no diagnostic — but ONLY
under `--engine=vm`. `vm_count_slots` (src/gen/emit_vm.c) walks the
replicated copy tree, so nesting depth d costs Θ(2^d) work BEFORE
`PCREC_MAX_VM_NODES` can fire; on the DEFAULT path the NFA 131072-state
cap refuses every such pattern instantly (0.11 s) and is an ACCIDENTAL
guard — `--engine=vm` skips building the NFA/DFA pair entirely (R21
E-6's prefilter-off behavior), so nothing bounds the walk.

Minimal repro (exact patterns + timing sweep + reproduce-loop:
docs/design/possessify_impl/k22_repro.txt; verified on main 949f867
with zero possessify symbols AND by the manager's own run at merge):
a `(?:...){0,2}` tower at depth 15 (140 chars) compiles in 0.32 s;
depth 20–30 refuses cleanly but increasingly slowly (11.82 s at depth
30 — the REFUSAL itself is already exponential); depth ≥35 hangs >30 s
with no diagnostic. Not adversary-tier only in theory: a 365-character
pattern is user-writable.

Tier: robustness (D22) — a pathological pattern must fail honestly,
never hang. The harness is protected (D45 bounds pcrec's own invocation
at 20 s in-suite); an end user on `--engine=vm` is not.

Fix direction, two halves: (1) the REAL fix is [ENG-BREP]'s counter-K
step, which eliminates replication for exactly these shapes (the copy
tree stops existing); (2) the interim guard is a cheap PRODUCT check —
multiply the nesting-path copy counts BEFORE walking (the exact
known-risk interaction eng_brep_design.md §7 names: "replication
factors MULTIPLY and v.maxcopies records only the max") and refuse
above a bound with a D26-tier diagnostic. Scheduled: with [ENG-BREP]'s
counter-K step, or as a small standalone guard lane if that step is
far. Related: the step-budget blind spot recorded in the [ENG-BREP]
plan row (same lane, same session) is the RUNTIME sibling of this
COMPILE-TIME gap — both are "possessification/replication moved work
where an existing budget cannot see it". (That sibling's fix of record
has since MOVED, 2026-08-17: the E-5-shaped entry charge was refuted by
the counter-K lane's measurement — R25 §7.2 — and the ruled fix is the
counter-K design note §7.4's forward-work meter under F-2 settlement 4,
its own bound/field/error code; decisions.md D47 SECOND ADDENDUM.)

**INTERIM GUARD LANDED 2026-08-16 (rung-select lane); the entry stays
OPEN because half (1) is still owed.** `vm_count_slots` now carries a
running PRODUCT of the replication factors down the nesting path and
refuses above `PCREC_MAX_VM_REPLICATION_PRODUCT` (src/core/limits.h)
BEFORE it recurses. The bound is `PCREC_MAX_VM_NODES`'s own value, and
that identity is the guard's whole safety argument rather than a number
to tune: every replicated copy costs at least one `vm_charge`, so the
product is a LOWER BOUND on the emitted node count and the guard can only
move a refusal EARLIER, never widen one. MEASURED (committed and
re-runnable: `docs/design/rungselect_impl/k22_sweep.sh`, outputs
`k22_sweep_{before,after}.txt`) — depth 15 compiles before and after;
depth 30 goes 11.82 s → 0.12 s; depth 35 and 40 go from HANG >30 s to
0.12 s. Depth 18 did not move and refuses through the NODE cap in 0.72 s
both times, because the tower's innermost `(?:a){0,2}` takes the cursor
rung and replicates nothing, so a depth-*d* tower's product is 2^(d−1)
and 18's sits exactly at the limit rather than over it. Pinned by
`tests/vm/run_vm_tests.sh`, where `timeout 5` IS the assertion (a plain
exit-code check would have passed on the defect, since depth 30 already
"refused" before the guard) and a depth-15 positive control leads,
because a guard that refuses everything also makes the hang go away.
The REAL fix, half (1), is unchanged and still owed: [ENG-BREP]'s
counter-K step, which stops the copy tree from existing for these shapes.
The reverse-deterministic rung landed the same day does NOT discharge it —
it declines nested quantifiers by scope bound (single-level only), so a
`{0,2}` tower still replicates.

## K23 — FIXED 2026-08-17, found 2026-08-16 (D27 blinded quantifier corpus): exact-minimum ambiguous-decomposition boundary exhausts the step budget on a 100-byte ordinary input

`(a{10,20}){10,50}` against `'a' * 100` — exactly the minimum total, the
ONLY valid decomposition (10 outer x inner minimum 10; 11 outer would need
110 bytes) — makes the compiled VM matcher return `RX_ERR_STEPS` against
the default 1,000,000-step budget instead of the match. python `re` (the
oracle) answers instantly: span (0,100), group 1 (90,100). Reproduced by
the manager at merge on HEAD's build (exit 3, "steps"). The boundary is
NARROW: 99 bytes reports nomatch in <1 ms (min-total check fails fast);
150+ bytes matches instantly (greedy satisfies an unambiguous
decomposition). The give-up itself is DESIGNED behavior (DD-2/D22:
honest RX_ERR_STEPS, not a hang or wrong answer) — the issue is the
search-space explosion that makes a 100-byte non-adversarial input hit it.

D27 author's characterization (probed black-box, recorded so the fix lane
does not re-derive it): inner-range WIDTH and total interact — `(a{10,12}){10,50}`
(width 2) at 100 matches instantly; `(a{10,15}){10,40}` (width 5) at 100
exhausts; reducing the outer max alone (`{10,30}` vs `{10,50}`) does NOT
avoid it, so it is not simply proportional to the outer ceiling.

NOT fixed by counter-K (choice points are identical across all K by
design — the emission strategy changes size, not the decomposition
space). Candidate mechanisms live with the OPT waves (memoization /
decomposition pruning) or [M4.6]'s engine-selection work; owning
milestone [M4.6] until a better owner exists. Regression:
`tests/known_fail/d27_nested_min_boundary.rxt` (ratchet-watched); the
99/500/1000-byte siblings stay live in `tests/base/d27_nesting.rxt`.

**K23 CLOSED 2026-08-17 ([M4.6d], the mrl lane).** THE FIX IS
MINIMUM-REMAINING-LENGTH (MRL) PRUNING, adopted by D51 ruling 1 on the
twice-panel-verified design note (`docs/design/k23_impl/k23_design.md`; the
build outcome is that note's §14). At every point where the emitted VM commits
to a subject position it now knows a compile-time lower bound on the bytes any
accepting continuation must still consume, and a position with fewer bytes
left is cut before a choice point is pushed for it. On the exemplar the search
goes from **10.6 M steps (`RX_ERR_STEPS`) to ≤1**, with the capture vector
identical to python's and to the unpruned build's; `((a{2,4}){5,10}){5,20}` at
50 bytes goes from 11,906,349,370 steps to ≤1. The bound is the same variable
the explosion is: it BITES at slack 0, where the tree is worst, and is vacuous
where slack is large.

Soundness is PREFERENCE-BLIND and that is why it is a fix rather than a
heuristic: `minrest` bounds whether an accepting continuation EXISTS, which is
a property of the LANGUAGE and therefore order-invariant, so a subtree it
deletes contained no leaf any preference order could have selected. Validated
as a pcrec-vs-pcrec differential against `-fno-length-prune`
(`tests/mrl/run_mrldiff.sh`): **202,458 cells, 0 divergences**, across strides
1-3, subject lengths on and off the iteration lattice, all four greedy/lazy
combinations, and BOTH ceiling forms.

**Three things in this entry's own text are corrected rather than rewritten,
because the design note measured them:**

- "python `re` answers instantly" is true of the exemplar and false of its
  mechanism. Python explores the SAME tree — its measured times track the
  closed form's node counts within 5% over four size steps — and takes 2.8 s
  one size up, 31 s two up and 370 s three up. pcrec's honest refusal was the
  better behaviour by D22's own bar; K23's justification is "answer a question
  we can answer cheaply", not "catch up to python".
- "The boundary is NARROW" is right about the number and wrong about the
  variable: it is narrow in SLACK (`n − p·m`), not in `n`, and the decay from
  the peak is geometric over ~50 bytes rather than a cliff (8.0 M steps still
  at 5 bytes of slack).
- The stated class is WIDER than the live one. An exact-count inner
  (`(a{6,6}){3,17}`) is possessified today, the outer takes the fixed-stride
  cursor rung, and the shape costs 0 steps at every length — so K23's live
  population was inner width ≥ 1, and the [ENG-BREP] ladder had already
  disposed of the width-0 edge before this fix existed.

The ratchet's resident moved to `tests/base/d27_nested_min_boundary.rxt` in
the same change, which is what the ratchet exists to force. The **D27 corpus of
record** for the ambiguous-decomposition region is
`tests/base/d27_k23_ambiguous_decomposition.rxt`, authored blinded in the
`d27k23` cell; `tests/mrl/` is the implementation lane's own test directory
and deliberately does not duplicate that region. The episode worth keeping:
the owed `(a{1,3}){65}` family FAILED the build lane's first implementation
and located a real gap on the counter rung (one body copy serves every trip,
so the compile-time follow-min tops out at `K + residue`, 9 where the truth is
65). The differential agreed, the structural checks agreed and the
step-collapse acceptance cell agreed, because all three were derived from the
same model the bug was in — which is why the mechanism now has an acceptance
cell of its own (`tests/mrl/run_mrl_tests.sh` §1b) rather than resting on a
corpus this lane does not own.
D51 ruling 3's step-budget move (10^6 → 5×10^8) lands with this change and
NOT before, so the test that flips says what it means: the defect is fixed,
not outspent.

**K22 CLOSED 2026-08-16 (F-1 ruling, decisions.md D47 ADDENDUM,
twenty-seventh session).** The two halves resolve separately: the HANG
half was fixed by the interim product guard above (landed with
rung-select, pinned in tests/vm/run_vm_tests.sh — refusal in 0.12 s at
every depth). The "these shapes should COMPILE" half is NOT a bug under
the ruling: Frank ruled strict eng_brep_design.md §4.5 (K is one
per-artifact constant in v1, no per-quantifier variation), so the
small-count tower family's ruled behavior IS the guard's fast honest
refusal (D22's bar), and compiling them is re-homed as the charter of
plan row [ENG-CLAMP] (deferred; carries the counterk lane's respecified
bottom-up-product algorithm and clamp_arith.py probe as its seed). The
prior sentence in this entry claiming counter-K "stops the copy tree
from existing for these shapes" was REFUTED by the counter-K lane's own
analysis regardless of the ruling (R25 E1: at K=8 every tower count
sits below K and replicates; only a per-quantifier downshift reaches
them) — the record is corrected here rather than rewritten above.

## K24 — pattern-specific DFA throughput regression on the alternation-trie shape, ~1.3x below its D12 floor (found 2026-08-17, [M4.6b] bench lane, during the case (c)/(i) engine-drift investigation)

`(alpha|beta|gamma|delta|epsilon)` compiled `--no-captures` (ENGM_DFA,
verified by the new per-case engine assertion) measures 294.381/304.309
MB/s on two independent quiet-box confirms against its 388.615 MB/s
floors.tsv reference (captured 2026-08-09, reconfirmed ~385-390 on
2026-08-11 runs) — reproducibly ~1.3x slow, with a 1.13-1.16x spread
where this case's history is 1.02-1.06x. NOT the engine-selection drift
(that was cases (c)/(i) silently routing to the VM hybrid under D42.1's
captures-default, fixed 2026-08-17 by pinning + per-case engine
assertions — see tests/bench/compare/CLAUDE.md's finding writeup): this
residual reproduces WITH the pin confirmed stamping ENGM_DFA. Every
other DFA case in the same full-grid run matched or beat its floor, so
it is pattern-specific — the multi-branch keyword-alternation shape is
the M2.8 trie's home turf, and the landing window (2026-08-11 →
2026-08-17: K18's path-sensitive closure rewrite of src/ir/dfa.c is the
prime suspect by file; possessify/revdet/counter-K touch only the VM
emitter) brackets the bisect. REPRODUCER: `CASES=c` via
tests/bench/compare/compare.sh on a quiet box (load-check per its
conventions); the floor row is DELIBERATELY LEFT at 388.615 so gate.sh
reports (c) RED as the live flag until this closes.

**ROOT CAUSE FOUND 2026-08-17 (k24bisect lane, merged cb6c708 —
full evidence docs/design/k24bisect_impl/k24_bisect_note.md):** first
bad = 1dbb6ce, the [M4.4] API break — NOT K18 (exonerated: the emitted
DFA for this pattern is byte-identical from 1dbb6ce to HEAD). The
mechanism is COMPILER LAYOUT, not our algorithm: adding
rx_match/rx_match_caps as same-TU callers of rx_search triggers gcc
-O2's PARTIAL-INLINING pass to split rx_search into a trampoline +
rx_search.part.0 carrying the scan loop; the loop's instructions are
identical before/after, but the split placement is layout-sensitive.
CAUSALLY PROVEN: same gen.c, same driver, -fno-partial-inlining alone
recovers 389.6-391.8 from 288.6-293.8 (pinned, 10 trials, <1% spread);
nm confirms the .part symbol vanishes. Corollary symptom: once split,
the SAME binary measures 287-397 UNPINNED — bench floors must pin
(probe + compare conventions carry this). FIX IS A DESIGN CALL, open:
keep rx_search monolithic (attribute lever on the wrappers or the
entry, e.g. noipa on the cold wrappers), control hot/cold layout, or
accept + re-floor; AND the same-TU-wrapper shape exists in EVERY VM
artifact too (match/match_caps call search), so the fix lane must
audit whether the VM hot path is also being split. Owner: [M4.6]
close-out (a RED D12 floor is M4.6's business). Correctness is
unaffected (the .rxt corpus and the trie's output-preserving
differential are green) — this is a D12/D18 throughput regression, not
a miscompile. Owner: manager triage; bisect queued. Found because
[M4.6b] added a NEW floor-gated case and re-ran the whole matrix —
compare/'s floors are in no battery leg (now marked ages-freely, with
the engine assertions as the cheap in-run tripwire).

**K24 CLOSED 2026-08-17 (k24fix lane).** THE FIX IS ONE ATTRIBUTE IN THE
EMITTED TEXT: `__attribute__((noclone))` on `<prefix>_search`, emitted by
`emit_search_head` in src/gen/emit_dfa.c — the ONE site that serves both the
DFA artifact's exported entry and the VM hybrid's `static` prefilter, so both
engines' DFA scan code is covered by a single emission point. It has to live
in the emitted artifact rather than in pcrec's own build: pcrec cannot dictate
its users' CFLAGS, and `-fno-partial-inlining` (the bisect's causal control)
is a flag only the artifact's compiler-invoker can pass. `noclone` forbids
exactly the one thing gcc's partial-inlining pass needs — duplicating the
function body — and the resulting assembly is **byte-identical** to the same
source built `-O2 -fno-partial-inlining`, which is the strongest available
statement that the lever reproduces the control and changes nothing else.

VERIFICATION (the number recovered; the floor was NOT touched). `floors.tsv`
case (c) stays at 388.615/0.900, and a full 10-case `gate.sh` run measures
**391.063 MB/s at spread 1.02x** — back above the floor, and back to this
case's *historical* 1.02x-1.06x tightness rather than the 1.13x-1.16x the
split produced. Head-to-head selection evidence, all on compare.sh's own
build line (`gcc -O2 -std=gnu11 -Wall -Wextra -Werror` + `eng_pcrec.c`),
`taskset -c 2`, 10 trials, medians, quiet box (load5 0.19-0.26):

| lever | median MB/s | `.part` clone still in `nm`? |
|---|---|---|
| none (the K24 state) | 293.500 | SPLIT |
| `-fno-partial-inlining` (bisect's control) | 391.646 | mono |
| `noipa` on the two cold WRAPPERS | 292.721 | SPLIT — **no effect** |
| `noinline` on the two cold WRAPPERS | 295.315 | SPLIT — **no effect** |
| `cold` on the wrappers | 397.076 | SPLIT — recovers by luck |
| `hot` on `<prefix>_search` | 397.589 | SPLIT — recovers by luck |
| `hot` on search + `cold` on wrappers | 288.745 | SPLIT — **WORSE than nothing** |
| **`noclone` on `<prefix>_search` (CHOSEN)** | **391.061** | **mono** |
| `optimize("no-partial-inlining")` on search | 390.873 | mono |
| `noipa` on `<prefix>_search` | 390.786 | mono |

Three findings in that table are worth more than the choice it settles:

1. **THE OBVIOUS FIX DOES NOT WORK, and the reason corrects this entry's own
   root-cause wording.** Marking the two cold wrappers `noipa`/`noinline`
   leaves the split standing and the throughput at ~293. The entry above says
   the wrappers "trigger" the split, which reads as though the split were a
   decision about those callers; it is not. gcc's `pass_split_functions` runs
   on the CALLEE and does not consult its callers' attributes, so severing IPA
   at the call site cannot un-split the callee. The wrappers' ARRIVAL is still
   what dated the regression to 1dbb6ce (the bisect stands), but the denial
   has to be spelled at `<prefix>_search` itself.
2. **LAYOUT STEERING IS NOT A FIX.** `hot` on the search entry, or `cold` on
   the wrappers, each recover the number (397) while leaving the split in
   place — and the two TOGETHER measure 288.745, worse than doing nothing.
   That is the mechanism refusing to be steered: the cost is placement in one
   particular link, and a stranger's link is not this one. Any future reader
   tempted to swap the attribute for a hot/cold pair should read that row
   first.
3. `optimize("no-partial-inlining")` and `noipa` on the entry both work.
   `noclone` was chosen over them as the smallest denial that is about the
   mechanism: the `optimize` attribute replaces the function's whole
   optimization environment to fix one pass, and `noipa` would additionally
   forbid the VM hybrid's inlining of this same emitter's `static` prefilter
   into `<prefix>_search` — an inline gcc performs today (verified: `nm` shows
   no `<prefix>_prefilter` symbol in a VM artifact, before or after this fix,
   because it is fully inlined; `noclone` does not disturb that).

Portability, with measured and read kept apart: gcc 15.2.0 (the box's
compiler) ACCEPTS `noclone` under `-Wattributes -Werror` with no
ignored-attribute diagnostic — checked rather than assumed, because an
attribute gcc merely ignored would make this fix a no-op that still looked
landed. GCC's manual has documented it since 4.5 (read, not measured), and it
sits inside the gcc-dialect mandate the emitter already lives under (computed
goto, `__builtin_expect`). There is no clang on the box, so clang's treatment
is UNMEASURED and recorded as such rather than assumed either way.

**THE VM-ARTIFACT AUDIT (the charter's second half): the VM hot path is NOT
being split, and the brief's premise for why it might be is wrong.** VM
artifacts do NOT have the match/match_caps → search wrapper shape: emit_vm.c's
`<prefix>_match` and `<prefix>_match_caps` call the `static`
`<prefix>_match_impl` DIRECTLY, and `<prefix>_search` calls it too — so the VM's
`search` has zero in-TU callers and is not a wrapper target at all. Measured
across a 25-pattern sweep (14 DFA, 11 VM), compiled with the bench build line
and audited with `nm` for every `.part`/`.constprop`/`.isra` clone:

- BEFORE the fix: **13 of 14 DFA artifacts carried `rx_search.part.0`** — the
  split was never specific to case (c)'s pattern; only its measured COST was.
  **0 of 11 VM artifacts carried any clone.**
- AFTER the fix: **zero clones anywhere**, both engines.
- The one DFA artifact that was never split is `^abc`, and the reason is the
  same structural one that protects the VM: it is the ENG_ATTEMPT
  computed-goto engine (5 `goto *` sites). gcc cannot outline a function whose
  labels are address-taken — they bind to one function — so a computed-goto
  matcher is unsplittable by construction. The VM's hot loop is exactly that
  shape (engine_m4.md §2.7: one function per pattern, one indirect jump at the
  fail label), which is WHY the VM was never at risk. That is a property of
  the VM's design, not luck, but it is also not a property anything checks, so
  it is recorded here rather than relied on silently.
- The attribute nonetheless rides the VM's `static` prefilter, since that is
  the same `emit_search_head` output and the same split-eligible table-driven
  shape. Measured neutral on the capture-bearing hybrid case (j): 150.237 MB/s
  before, 150.433 after (floor 150.369, spread ≤1.01x either way).

Measurement archive: docs/design/k24bisect_impl/k24_fix_note.md (this lane's
head-to-head, the sweep tables and the reproduction recipe), alongside the
bisect lane's k24_bisect_note.md that the fix answers.


## K25 — OPEN, found 2026-08-18 ([M4.7b], while pinning K7's resource bounds)

DFA MINIMIZATION, not construction, is what a long-chain pattern spends its
compile time on, and its cost is quadratic in the state count with nothing
watching it.

Measured on `a{0,25000}`, per pipeline stage, after K7's fix:

    parse           +0.00 s
    NFA build       +0.01 s
    subset fwd      +0.01 s
    subset rev      +0.01 s
    minimize fwd    +7.50 s        <-
    minimize rev    +7.76 s        <-
    emit            +0.02 s

15.3 s of 15.4 s, against 0.03 s for everything K7's accounting bounds. The
cause is `src/opt/minimize.c`'s Moore partition refinement: each round is
O(n * ncls) and the number of ROUNDS is O(n) on a chain, because a chain
distinguishes exactly one more level per round. `a{0,n}` after the unanchored
wrap is precisely that shape, so the pass is Theta(n^2 * ncls).

**Why K7's fix does not cover it, and why no budget added there would have.**
K7's two bounds count what the SUBSET CONSTRUCTION stores and the NFA builder
allocates. This pass runs after both, on a machine they have already sized and
approved: `a{0,25000}` interns 50,000 state-set elements (linear — there is
nothing for `PCREC_MAX_SUBSET_ELEMS` to object to) and its NFA is 50,002 states
against a 131,072 cap. A closure-WORK budget was built and measured during
[M4.7b] specifically to see whether it would catch this, and it does not:
`a{0,25000}` spends 300,024 closure steps against a corpus maximum of
240,508,032. The budget was reverted rather than shipped, because a bound with
no shape that trips it is unpopulated machinery (D18/OS-0/D53).

**Severity: low, and it is a COST not a failure.** Memory is bounded (13 MB),
termination is guaranteed, the answer is correct, and the pass is
behaviour-preserving by construction — worst case it is slow. It is filed
because it is now the binding constraint on `tests/resource/`'s CPU budget,
which sits at 45 s purely to accommodate it and carries a note to come back
down to ~10 s when this is fixed.

**Second case, consistent but NOT attributed:** `(?:abcdefghij){3000}` compiles
in 216 s at 203 MB (measured both before and after [M4.7b] — 153 s on the
pre-lane binary on a quieter box, so this is pre-existing and unchanged). Its
state count and chain shape fit this cause, but no per-stage timing was taken
for it. Run the same stage-timing instrument on it before assuming it is the
same bug; if it is not, it is a third growth law and deserves its own entry.

**Fix candidates, unranked:** Hopcroft's algorithm (O(n log n), a drop-in
replacement for the same interface); or a cheap pre-pass that collapses chains
before refinement, which is narrower but targets exactly the shape that hurts.
Neither is urgent.

## K26 — OPEN, found 2026-08-18 ([M4.7b] lane, via a positive control on its own leak check)

**LeakSanitizer is silently a NO-OP on this box, so `make asan`'s
documented leak coverage has never actually run.** Under the battery's
exact options (`ASAN_OPTIONS=detect_leaks=1 LSAN_OPTIONS=""`), a
control program that deliberately leaks 12,345 bytes exits 0 and
reports nothing. `/proc/sys/kernel/yama/ptrace_scope` is 1, the likely
cause (LSan's stop-the-world tracer). ASan proper is unaffected and
works (measured: forced-allocation-failure runs report real errors).

This is a TEST-INFRASTRUCTURE gap, not a pcrec bug — filed here so the
"asan+lsan both axes" claim in docs/testing.md cannot be read as
evidence about leaks. Every "no leaks" claim to date that rested on a
green `make asan` was resting on nothing; reasoned claims (e.g.
[M4.7b]'s job_cleanup-frees-wholesale argument) stand on their own
reasoning only.

**Fix direction, and the obligation either way:** the battery gains a
POSITIVE LEAK CANARY — a deliberately-leaking control that must be
REPORTED for the leak tier to count as running, so a no-op LSan turns
into a loud failure instead of silent green (the exact check-design
lesson: the lane found this only because it ran a positive control on
its own check). Enabling LSan itself may need ptrace_scope=0 or an
attach-permitting environment — SYSTEM CONFIG, outside the repo
mandate: Frank rules on any host change. Until then the canary keeps
the gap visible and the testing.md text carries the caveat.

Repro: compile any program that mallocs and exits without freeing;
run under the battery's ASAN_OPTIONS; observe exit 0, no report.

## K27 — FIXED 2026-08-18 ([M5-SEAM], the emitter-touching wave this was scheduled for; found 2026-08-18 by the [M4.7g]/R29 fix lane's UBSan probe)

Found 2026-08-18 by the [M4.7g]/R29 fix lane's UBSan probe (the C7
subject-contract verification). docs/spec/match_api.md §3.1 states —
correctly, and now with measurement — that `s` may be NULL when
`n == 0`. On that input the emitted unanchored search body executes
`memchr(s + pos, c, n - pos)` with `s == NULL, pos == 0, n == 0`
(src/gen/emit_dfa.c's memchr prefilter line), and UBSan reports "null
pointer passed as argument 1, which is declared to never be null".
Behavior is CORRECT on every tested toolchain (both engines return 0;
ASan clean; the artifact never dereferences), but it is technical UB in
EMITTED code on a documented-legal input — a user compiling a generated
matcher under their own -fsanitize=undefined sees pcrec's name on the
report.

Invisible to the suite because the harness never passes s == NULL; the
`make ubsan` battery is green for exactly that reason (its
generated-code axis runs the corpus, and the corpus has no NULL-subject
case). Sibling in shape to the R29 C17 filing (extern "C" guards):
first-hour integration friction in emitted text, emitter-owned.

Fix shape: one guard in the emitted prefilter (`n - pos` zero-check
before the memchr call, or `s ? memchr(...) : NULL`), plus a
NULL-subject case in the ubsan battery's generated-code axis so the fix
is pinned. Scheduled: next emitter-touching wave (the [OPT-A] byte-test
spelling menu touches the same emission site, or M4-CALLOUTS/M6,
whichever lands first). Repro: compile any pattern, gcc
-fsanitize=undefined the artifact with a driver calling
<prefix>_search(NULL, 0, 0, NULL).

**Fix landed 2026-08-18 ([M5-SEAM]).** `emit_unanchored`
(src/gen/emit_dfa.c) emits `if (pos >= n) return 0;` immediately above the
single-escape-byte `memchr` line, on the NON-EOL arm only. Two things about
that shape are worth stating rather than inferring:

- **It changes no answer.** `memchr` over a zero-length range returns NULL,
  and the very next emitted line is `if (!q) return 0;` — so the guard is
  exactly the branch the unguarded form reached one line later. This is a
  UB removal, not a behaviour change, and the whole-corpus output diff is
  one added line per affected artifact.
- **The EOL arm needed no guard and did not get one.** Its own
  `if (pos + 1 < n)` bound already implies `n > 0`, hence (by the §3.1
  subject contract) `s != NULL`. Adding a redundant guard there would have
  made the two arms look like they rest on the same argument when only one
  of them does.

**Pinned by** `tests/codegen/run_codegen_tests.sh`'s `[K27]` check, which
compiles a memchr-prefilter artifact, links a driver calling
`<prefix>_search(NULL, 0, 0, NULL)` and `<prefix>_next_pos(NULL, 0, 0)`,
RUNS it, and requires `0 1`. Placement is the point: that script is already
in both the `make ubsan` and `make asan` suite lists, so under the
sanitizer battery the run is instrumented and the UB is a hard failure,
while under plain `make test` the same check pins the answers. That is
precisely the gap this entry recorded — the battery was green because the
corpus never passes `s == NULL`, so the instrumented axis had nothing to
see. The check also fails loudly if its fixture stops carrying a memchr
prefilter at all, rather than passing vacuously.

**Both directions measured at landing.** Guarded artifact under
`gcc -fsanitize=undefined -fno-sanitize-recover=all`: clean, `search` 0 and
`next_pos` 1. The SAME artifact with the guard line stripped back out:
`runtime error: null pointer passed as argument 1, which is declared to
never be null` at the memchr line — so the probe is watching, not merely
silent.

## K28 — FIXED 2026-08-19 ([M6.2] REPAIR SLICE, the own-slice fix it was scheduled for; found 2026-08-19 by the [M6.2] wave B lane, first REACHED by its corpus; defect pre-existing, confirmed on merge base c23662e)

**An anchored pattern whose DFA is one dead state emits C that fails the
harness's own default GENCFLAGS** (`-O1 -std=gnu11 -Wall -Wextra -Werror`):
gcc inlines the always-returns-0 `<prefix>_search` into the
`<prefix>_match` wrapper and then reports the wrapper's local `caps` array
as maybe-uninitialized — even though the wrapper's `found != 1` test makes
the read unreachable. The artifact's ANSWERS are correct (always nomatch);
this is a warnings-cleanliness defect in emitted code, which D26/`make
strict`'s own bar treats as real because a downstream consumer compiling
with `-Werror` sees a build failure.

**Minimal repro** (manager re-verified 2026-08-19 on main):

    build/pcrec -p rxd -o dead.c -- '^a^b'
    gcc -c -O1 -Wall -Wextra -Werror dead.c    # maybe-uninitialized, FAILS

**Opt-level-dependent, and -O1 is the one that matters:** fires at `-O1`
ONLY (`-O0`/`-O2`/`-O3`/`-Os` all clean — measured all five), and `-O1` is
exactly `tests/harness/run.sh`'s default GENCFLAGS, so any corpus pattern
of this shape is a suite build failure. That is also why it survived
undetected: no pre-wave-B corpus pattern compiles to a single dead state.
`^a^b` is a base-tier reproducer; wave B's corpus is the first to REACH
the shape naturally (`^\Bfoo`, `^\Bo`, `^a\bb`), and those three cells
are named and excluded in tests/assertions/wordb_engattempt.rxt's own
header (~line 33; wordb.rxt's ENG_ATTEMPT-half shard, split 2026-08-21)
with live equivalents in their place.

**[M6.2 wave C] adds a FOURTH spelling and it is a different construct**:
`a(?m)^b` — a multiline `^` after a consumed byte, which cannot match for
the same reason `^a^b` cannot, so the shape is reached by `(?m)` as well as
by `\b`. Named and excluded in tests/assertions/multiline.rxt's own header,
with the live equivalents `a(?m)$` and `a(?m)^b|c` in its place. Worth noting
for the fix's scheduling: each wave that lands a new BOT-family or
context assertion adds spellings that reach this shape, so the exclusion
list grows monotonically until the wrapper is fixed.

**[M6.2 wave D] adds a FIFTH and SIXTH, and they are the prediction above
coming true a third time**: `a\Gb` and `x\G` — a `\G` after a consumed byte,
which cannot match because one transition means `pos > startpos`. Named and
excluded in tests/assertions/gpos.rxt's own header, with `ab|a\Gb`,
`a\Gb|c`, `a\Gb|\Gz` and `x\G|y` in their place (the same impossibility
carried on a live sibling branch, so the automaton survives and the artifact
is warnings-clean). **They are ASSERTED, not merely excluded**:
tests/assertions/run_gstart_diff.sh §4 sweeps them against libpcre2 over
every subject at every startpos, compiling at `-O2` where K28 does not fire —
so the shape is pinned even though the corpus cannot hold it. That is the
pattern later waves should follow rather than dropping the cells.

**[M6.2 wave E] ADDS NOTHING, AND THE PREDICTION ABOVE IS THEREFORE
BOUNDED RATHER THAN MONOTONIC.** Wave C's note says "each wave that lands a
new BOT-family or context assertion adds spellings that reach this shape, so
the exclusion list grows monotonically until the wrapper is fixed", and waves
C and D both confirmed it. `\K` does not, and the reason sharpens the rule
rather than refuting it: this shape needs a pattern that CANNOT MATCH, and
every previous spelling got there by asserting something impossible after a
byte was consumed (`^`/`(?m)^`/`\G` after a transition). `\K` asserts
nothing — it cannot fail — so no placement of it makes a pattern
unsatisfiable, and no `\K` shape reaches a single dead state. The list
stands at SIX spellings and the repair slice's scope is unchanged.
The corrected rule for whoever schedules the fix: it is not "one per wave",
it is **one per construct that can make a pattern impossible**, which is
exactly the BOT-family and context assertions, and module `assertions` has
now landed all of them.

**Fix sketch and why it is deferred:** initialize the wrapper's `caps`
(or restructure the wrapper so gcc sees the dominance) — a one-line
emitter change whose blast radius is EVERY artifact in the tree, so it
wants its own slice with the byte-identity churn accounted, not a rider
on a feature wave. **Scheduled:** its own small row before the [M6.2]
module close, so the excluded wordb.rxt cells can be reinstated with the
module's D27 corpus.

---

**FIXED 2026-08-19, [M6.2] repair slice.** The sketch's FIRST option is
what shipped and the second was MEASURED UNAVAILABLE, which is the part
worth keeping: `src/gen/emit_dfa.c` now emits
`ptrdiff_t caps[<PREFIX>_NCAPS][2] = {{0}};` under a one-line artifact
comment naming this entry. Restructuring was tried first and does not
work — splitting `if (found != 1 || (size_t)caps[0][0] != ctx->pos)`
into two `if`s leaves the `-O1` report exactly where it was, so the
dominance gcc cannot see is not the short-circuit and the initializer is
the smallest thing that silences it.

**THE ENTRY ABOVE NAMED ONE SITE AND THERE ARE THREE**, which the
`-Werror` build had hidden by stopping at the first: with `-Wall -Wextra`
and no `-Werror`, the dead artifact reports the same defect in
`<prefix>_match` (2 reports), `<prefix>_match_caps` (3) and the
standalone `main()` (2). `<prefix>_match_caps` and `main()` were never
mentioned in this entry or in any corpus header. All three are the same
declaration emitted from `emit_match_def`, `emit_match_caps_def` and
`pcrec_emit_main`, and all three carry the initializer now. The VM's own
wrappers need nothing — they call `<prefix>_match_impl` directly and
declare no local `caps` array.

**Verification.** The entry's own repro (`^a^b`, `-p rxd`) compiles clean
at `-O0`, `-O1`, `-O2`, `-O3` AND `-Os` under `-Wall -Wextra -Werror` —
all five, so the fix did not trade the report to another level — and so
does the `--emit-main` form, which is what reaches the third site. Also
clean under the sanitizer GENCFLAGS path
(`-fsanitize=undefined -fno-sanitize-recover=all` and
`-fsanitize=address`, at `-O1` and `-O2`). Answers are unchanged: the
initializer is only ever read on a path `found != 1` already excludes.
A `RX_NCAPS > 1` artifact (a VM build with four capture slots) is clean
too, so `{{0}}` raises no `-Wmissing-braces` at any width.

**THE SIX EXCLUDED CORPUS SPELLINGS ARE BACK**, in the same change and
oracle-verified against libpcre2 through `tests/assertions/verify_pcre2.py`:
`^\Bfoo`, `^\Bo`, `^a\bb` (wordb.rxt, +216 cells — now tests/assertions/
wordb_engattempt.rxt's shard, split 2026-08-21), `a(?m)^b`
(multiline.rxt, +45), `a\Gb` and `x\G` (gpos.rxt, +30). Each file's own
header is rewritten from "absent, and here is why" to "back, and here is
what fixed it". The LIVE equivalents stay in place — they carry the same
impossibility on a sibling branch that keeps the automaton alive, which
is a different emitted shape and its own coverage — and
`run_gstart_diff.sh` §4 keeps asserting the class at `-O2` over its own
generated sweep.

**The list closed at SIX and wave E's correction was right.** Wave C
predicted one spelling per wave; wave E corrected it to one per construct
that can make a pattern IMPOSSIBLE, and module `assertions` had landed
all of them by then. Nothing was added after wave D.

## K29 — FIXED 2026-08-22 in [M6.4.2] (found the same day by R31 panel critic r31eng, read-only, on the shipped binary at 4c5f508/036acd6 lineage; defect pre-existing since [ENG-BREP]'s counter rung)

**What.** The VM emitter's counter rung has an UNBOUNDED arm that tails
into the plain frames star: `vm_counter_fits` accepts `rmax < 0` when
`rmin >= K` (`src/gen/emit_vm.c:695`), `vm_counter_rep` allocates and
writes the cut mark (`:3310`, `:3334-3336`), then at `:3355-3358`
(`if (unbounded) { vm_star(v, cur, a, next); return; }`) hands the tail
to `vm_star`, which never reads `a->possessive`. So when possessify's
§2.2 verdict marks such a repeat, the artifact stamps `RX_VM_STRATS 0x1`
(POSSESSIVE) and allocates `RX_SLOT_CUT_MARK0`, writes it once, and
READS IT NOWHERE — no `RX_CUT(` is emitted. Reproduced:
`build/pcrec -p rx --engine=vm --no-captures '(?:ab|b){8,}c'` (also
`{9,}`, and `(?:abc|bc){8,}d`); the bounded twin `(?:ab|b){8,12}c`
emits 5 cut calls.

**Severity today: MEDIUM, observability only.** Answers are unaffected
because possessification is proof-gated (the cut it fails to emit would
delete only provably-dead frames). But it is a D46 stamp that lies
(STRATS says POSSESSIVE on an artifact with no cut), a dead slot in
`RX_NSLOTS`, and the frame/trail budget `vm_cost_rep` computes for the
possessive path is not the path emitted.

**Why it mattered NOW.** [M6.4]'s design (RULE 3) lifts user-written
possessives `X{n,}+` onto the same rungs; through this arm a SEMANTIC
possessive would emit an ordinary backtracking star and answer the
UNCUT language — a miscompile. The fix therefore travelled with [M6.4.2]
(R31 E2 disposition), and its ORDERING was ruled: the K29 fix lands
BEFORE the lift, because landing the lift first turns an observability
defect into a wrong answer. Until it landed the free-discharge
measurement in atomic_groups_design.md §5.3 was NOT contaminated — it
reads the stamp as a proxy for the VERDICT, which the stamp faithfully
reports; it was the emitted code the stamp was unfaithful to.

**THE FIX (2026-08-22, [M6.4.2] slice 2).** `vm_counter_rep`'s unbounded
arm now emits the exit cut in the tail rather than handing it to
`vm_star` bare: the star is emitted with its `next` pointing at a new
label that cuts back to the mark and then takes the continuation. The
star's exits ALL land there — its MRL test, its empty-iteration guard,
and the pop of any frame it pushed — so one cut at that label discards
the whole loop's frames AND the mandatory phase's, back to the mark
recorded before any of them. `resume_depth >= mark` holds because the
mark is set before the first push.

**MEASURED, `--engine=vm --no-captures`, RX_CUT call sites before -> after:**

    (?:ab|b){8,}c        0 -> 1
    (?:ab|b){9,}c        0 -> 1
    (?:abc|bc){8,}d      0 -> 1
    (?:ab|b){8,12}c      5 -> 5     (the bounded twin, unmoved)
    a{8,}b               0 -> 0     (the CURSOR rung: frameless, owes no cut)

and every ANSWER identical to the pre-fix compiler's and to libpcre2's
over 35 cells. `[M6.4-ATOMIC rule 5]` in tests/codegen/ is the
per-dispatch-path structural check E2 asked for: six paths x both
preferences, each naming which cut-equivalence answer its path gives, so
a future rung change cannot silently drop a path the way this one was
dropped.

**IT CHANGES EMITTED BYTES, and the identity gate says how much.** The
fix moves the artifact for every `X{n,}` with `n >= K` and a positive
§2.2 verdict — patterns with no atomic construct in them. `[M6.4.2]`'s
byte-identity gate (tests/codegen/run_atomic_identity.sh) measured the
corpus overlap at ZERO: no `.rxt` pattern anywhere under tests/ is in
that family, so the gate asserts a flat zero difference and needed no
exception bucket.

## K30 — CLOSED 2026-08-24 ([M6.6.2] wave F) — `run_reject_tests.sh`'s `--list-syntax` section runs UNSHARDED in every shard, so a sabotage row's reject figure depends on the inner shard width

**Symptom.** Sabotage S18-tsv-empty (pcrec_syntax_tsv returns "" early)
measured `reject:5fail` in every matrix through 2026-08-22, `reject:4fail`
in the 2026-08-23 PROCS=4 full matrix and `reject:3fail` at PROCS=6 — i.e.
shards + 1. Those earlier matrices ran the inner reject suite at 4 shards
by the [TT-8] PROCS leak; the fixed matrix derives INNER_PROCS = ncpu/PROCS
(3 at PROCS=4, 2 at PROCS=6), so the figure now moves with PROCS.

**Cause.** tests/reject/run_reject_tests.sh:1752-1754 — the `--list-syntax`
dump and its "produced no dump … every check below would pass vacuously"
guard sit OUTSIDE the `callidx % SHARD_TOTAL` gate that `reject()`/
`accept()` use, so every shard child runs the dump and, under S18, every
shard reports that guard's failure once. [TT-2]'s "same Summary counts at
any PROCS" claim is therefore false for this section under this sabotage
(true for the healthy tree: the guard passes in every shard and the per-row
probes below it ARE gated).

**Consequence.** The matrix's documented "byte-identical to a PROCS=1 run"
property holds only for rows whose suites are shard-independent; S18 is the
one known exception. Not a detection defect — S18 is DETECTED at every
width.

**Fix (small).** Run the dump once and shard its row loop like the rest, or
confine the guard to shard 0 (a `[ "$SHARD_INDEX" -eq 0 ]` around the `bad`).
Then re-measure S18 at PROCS=1/4/6 — the figure should be constant — and
drop this entry. Lands with the next reject-table change or [TT-8]'s close.

**CLOSED 2026-08-24, [M6.6.2] wave F** — the next reject-table change, as
predicted. **The SECOND remedy is the one that was available and the first
one is not**, which is worth recording because the entry offered them as
alternatives: every shard child runs its OWN slice of the `row_reject` loop
and needs its own `probe.tsv` to do it, so a shard that skipped the dump
would skip its rows and the section's global coverage assertion would then
correctly report that the table was not covered. The dump therefore stays
per-shard (it is one `--list-syntax` call) and only the vacuity `bad` moved
inside a gate — `[ -z "${REJECT_SHARD_TOTAL:-}" ]`, the idiom the BADROW
report and the coverage-count assertion in the same section already use,
which is a plain PROCS=1 run or the top-level dispatcher after aggregation
and never a child.

**MEASURED, at the two widths the entry asked for**, single-row mech runs on
the fixed tree (`run_sabotage_matrix.sh S18`):

| | S18-tsv-empty's reject figure | verdict |
|---|---|---|
| before (PROCS=4, INNER_PROCS=3) | `reject:4fail` | DETECTED |
| before (PROCS=6, INNER_PROCS=2) | `reject:3fail` | DETECTED |
| **after (PROCS=4)** | **`reject:1fail/454pass`** | DETECTED |
| **after (PROCS=6)** | **`reject:1fail/454pass`** | DETECTED |

The figure is now CONSTANT across the widths and the pass count is identical
too, so [TT-2]'s "same Summary counts at any PROCS" claim is true for this
section again. Detection never changed — S18 was DETECTED at every width
before and after; what changed is that the number a reader compares between
matrices no longer moves with the harness's own parallelism.


## K31 — OPEN (watch item, 2026-08-24, thirty-eighth session) — two unreproducible one-off suite failures under concurrent load

**Symptom.** Twice in one night, a suite failed once under heavy concurrent
load and was clean on immediate re-run with nothing changed:
(1) `run_vm_identity.sh` reported `REFUSAL MISMATCH: default refused,
--no-captures accepted: (ab|cd)(ef|gh)` during waveE's `make test` while a
full mech matrix and the identity gate ran concurrently — the pattern
compiles clean under every axis on re-run and under the pinned reference;
(2) the post-D+E battery's `make san` stage exited Error 1 immediately
after the harness stage (`parallel: 134 of 134 file workers reported`)
while other suites ran concurrently — the full clean re-run on the same
sha (6cf861c-era main) is green end to end (`san rc=0`, zero reports,
both axes; log scratchpad archived in the journal's part-14 addendum).

**Suspects, none confirmed.** /tmp is a 7.6G tmpfs shared by every
concurrent suite's scratch (waveE's hypothesis); a transient under
memory/pid pressure; or a real load-dependent race in a suite driver
(worst case). Neither failure was caught in the act.

**Watch instruction.** A THIRD instance gets an investigation lane, not a
re-run: capture the failing tree's /tmp usage, dmesg tail, and the
failing suite's whole log before anything is re-run. Until then, a
single-suite failure during concurrent batteries is re-run once before
being treated as real — and a re-run pass does NOT close the incident,
it lands here.

**Milestone.** None scheduled; watch item. Revisit if a third instance
appears or when [TT-5]'s chain work next touches suite concurrency.
**ADDENDUM 2026-08-24 (thirty-ninth session).** Two more load-shaped
one-offs, this time EXPLAINED and not counted as a third K31 instance:
with three lanes' suites plus two mech sweeps on 12 cores (load average
31), `tests/resource`'s 45 s compile-CPU-cap check failed on
`[a-z]{0,30000}` / `(a|b){0,30000}` in two lanes' `make test`, and one
lane lost `((a)|ab){4000}c` to the harness compile timeout (exit 124, 29
cascaded cases). Both were clean solo; the A/B control (main's reference
binary ALSO blows the cap under that load, 53 s vs 49 s) pins it on the
box. Both patterns are the K32 shape. Manager rule adopted: ONE heavy
suite (make test / san / mech) on the box at a time; lanes run targeted
rows, the manager runs the battery on the merged tree.

## K32 — OPEN (2026-08-24, thirty-ninth session) — the DFA PREFILTER's NFA replicates bounded repeats, so `X{n}` compiles in O(n²) time and O(n) artifact even when the VM lowers it as a constant-size counter rung

**Symptom.** `((a)|ab){4000}c` compiles in 4.8 s / 112 MB RSS / 404 KB
artifact by default and in 0.00 s / 2 MB / 25 KB under `--no-prefilter`
or `--engine=vm`. MEASURED n = 500/1000/2000/4000 → 0.05/0.21/0.90/4.02 s
(~4× per doubling: quadratic); the artifact grows linearly and every
growing line is a DFA table row. The VM body is constant: `// counter
rung, {4000,4000}, K=8` — counter-K already made the MATCHER
replication-free. The cost is entirely the prefilter's construction.

**Cause.** `src/ir/nfa.c:655-675` Thompson-replicates a bounded repeat
(`for (i = rmin; i < rmax; i++)` copies of the body) for the DFA side;
subset construction over an O(n)-state NFA whose DFA states are O(n)
position sets is O(n²), and the resulting O(n)-state DFA is emitted as
tables. For this shape the prefilter buys nothing — every candidate is
re-scanned by the VM anyway.

**Fix shape (unruled).** A count CLAMP in the prefilter ONLY: `X{n}` ⊆
`X{k}X*` for any k ≤ n is a SUPERSET, so thinning the prefilter's count
to a small k (or dropping the prefilter above a threshold, as `backrefs`
and the coming `recursion` module already do by predicate) is sound and
bounds construction to O(k²). Match semantics untouched; the identity
gate's byte-identity control applies below the threshold. Candidate
home: [ENG-THIN]/[ENG-CLAMP]'s neighbourhood; ruling needed on the
threshold and on whether the clamp is a stamp the artifact reports.

**Fix shape, second half (Frank's question 2026-08-24 ~11:0x, "can we
add a loop to the DFA prefilter?").** A DFA cannot count without states;
a "loop" is a counter register, i.e. a counting automaton — which pcrec
already has in the VM's counter rung (the reason the VM-only compile is
0.00 s). Two roles, two answers: (a) as a PREFILTER the clamp above is
the whole fix (superset, no semantic change, a compile/selectivity trade
stamped on the artifact); (b) as the MATCHER (capture-free
`--engine=dfa`, `a{4000}b`) exactness forbids a clamp, so engine
selection should ROUTE counts above a threshold to the VM's counter rung
— the same routing closes K25's Moore-minimization chain. Counting-set
automata (Turoňová/Holík et al., PLDI 2020) noted as the parked
[ENG-*]-class alternative, not proposed. Rulings needed: the two
thresholds; whether the clamp is stamped.

**Guards today.** `tests/resource`'s compile-CPU cap (45 s) and D45's
harness compile bound catch the runaway; `tests/counterk/counterk.rxt:1807`
is the endgame cell (libpcre2 refuses it outright, error 120).

**Milestone.** None scheduled; parked for Frank's ruling. Found while
explaining a load-induced compile timeout on exactly this cell.

## K33 — OPEN, NARROWED (2026-08-24, thirty-ninth session; found by the [DD-14.FB] spec lane. NARROWED 2026-08-25 by [OPT-1], fortieth session) — a call-bearing VM artifact's default entries SIGSEGV on a musl-default 128 KB thread stack for a subject deep enough to escalate to the deep tier

**NARROWED 2026-08-25 BY [OPT-1], AND THE OLD SYMPTOM SENTENCE IS NOW
FALSE.** This entry used to say the default entries "segfault on a 2-byte
subject" — on ANY subject. `[OPT-1]`'s two-tier entry
(`docs/design/two_tier_entry.md`) moved the stamped default storage off
`<prefix>_search`'s own frame and onto a `noinline` `<prefix>_search_deep`
that only a `PCREC_ERR_FRAMES` give-up reaches. Re-MEASURED, `gcc
-fstack-usage`, same artifact: `rx_search` **3,184 B**, `rx_search_deep`
**131,216 B**. So on a musl-default 128 KB thread that artifact now
**matches every subject the fast tier holds** and faults only on one deep
enough to escalate. `tests/thread/run_stackdepth_tests.sh` arm D pins the
narrowing behaviourally (the same entry that dies in arm A matches "ab" on
the same thread); arm A still pins the death.

**It is NARROWED, not closed, and the remedy is unchanged.** Which subjects
escalate is a property of the pattern and the subject, so a caller cannot
bound it in advance; `_in` is still the only way to get a guarantee. The
DEEP path is still 131,216 + 3,184 B and still does not fit.

**Symptom (as narrowed).** MEASURED: `rx_search`/`rx_match`/`rx_match_caps`
of a call-bearing VM artifact, called from a thread with musl's default
128 KB stack, segfault on a subject that exhausts the fast tier (the
684-byte `a^342 b^342`). `docs/spec/match_api.md` §5.3's concurrency
contract ("any number of threads may call the same artifact's entry points
concurrently") is FALSE today for that artifact class on that platform for
such subjects; §5.3 carries the measured shipped-behaviour paragraph and
its [OPT-1] re-measurement.

**Cause.** `gcc -fstack-usage`: the DEEP PATH is 131,216 B for a
call-bearing artifact (CORRECTED 2026-08-25 by [SPEC-1.1]'s re-measurement via `make test-stackdepth`; the 131,296 B figure first recorded here was the spec lane's pre-code-half number. [OPT-1], same date: this number is now `rx_search_deep`'s frame, not `rx_search`'s — the entry's own is 3,184 B, and the quantity that decides whether a deep call fits is entry + deep) (the run struct: 2048 resume frames × 40 B + 3072
trail entries + slots = 131,144 B), 98,512 B for the unbounded call-free
one (just UNDER 128 KB). The two per-frame call fields wave B+C added
(`call_top`, `call_ret`) took a resume frame 24 → 40 B; 2048 × 16 =
32,768 B is exactly what crosses the ceiling. Arrived with [DD-14] wave
B+C (67e40b9). glibc's 8 MB default thread stack is unaffected.

**Remedy — HALF SHIPPED (2026-08-25, [DD-14.FB] code half).** The `_in`
entries exist: `<prefix>_search_in`/`_match_in`/`_match_caps_in` take a
`<prefix>_buffers` descriptor and put the two arrays wherever the caller
says (`docs/spec/match_api.md` §10). MEASURED on the shipped emitter:
`rx_search_in`'s own frame is **144 B** (312 B for the whole call chain)
against `rx_search`'s **131,216 B**, and the same 684-byte subject that
kills the default entry on a 128 KB thread MATCHES through `_search_in`
on that same thread.

**The DEFAULT path's DEEP TIER is NOT fixed and will not be**, which is why
this entry stays OPEN rather than closing. Its storage stays on the C stack
because every other home is closed (a static fails TS-1/§5.3; a
thread-local fails reentrancy; allocation is forbidden by construction), so
the only things that would fix it are a smaller stamped default — **D73
ruled KEEP 2048/3072** — or the caller compiling with
`--backtrack-frames`. [OPT-1] changed WHEN that storage is reached, not how
big it is or where it lives. So the standing advice is unchanged and now has
a supported spelling: a caller on a musl-default thread stack, or any
small-stack thread, must call an `_in` entry with its own storage, or
compile the pattern with a smaller capacity.

**Pinned, in both directions.** `tests/thread/run_stackdepth_tests.sh`
(target `make test-stackdepth`, in `make test`) reproduces the crash as a
`KNOWN:` line every run, asserts the remedy matches on the same thread,
and carries a CAUSAL control — the unbounded but call-FREE `(a|aa)+b`,
whose 98,432 B deep path fits, on the same driver and subject — so the
difference between crashing and not is the frame size and nothing else.
**The script FAILS if the default entry ever stops dying** on the DEEP
subject, because this entry would then be describing something that is no
longer true. [OPT-1] added arm D, which pins the NARROWING in the same run:
the same entry matching a 2-byte subject on the same thread.

**Milestone.** Remedy: [DD-14.FB] code half, done. Narrowing: [OPT-1],
done. Deep path: closed only by a future ruling that revisits D73.

## K34 — RULED: DOCUMENTED DIVERGENCE (D74, Frank 2026-08-25; was OPEN 2026-08-24, found by the [DD-14.D27] blinded author) — pcrec GIVES UP (`frames`) on a runaway left recursion where libpcre2 10.46 CONCLUDES (a clean nomatch); PCRE2's recursion-loop rule is subtler than "same position = error"

**Symptom.** `(a|(?1)a)b` on "a" / "aaa" / "": libpcre2 returns a clean
NOMATCH (rc PCRE2_ERROR_NOMATCH, not −52); on "ab" both match (0,2) g1
(0,1). pcrec answers "ab" correctly and returns `PCREC_ERR_FRAMES` on
every non-matching subject. Same for `(a|(?1)a)c`. Plain `(a|(?1)a)` is
fine. MEASURED by the blinded author and re-measured by the manager
through sr_oracle.py: `(a|(?1)a)b`/"a" → None; `^(a|(?1)a)$`/"aaaaa" →
(0,5); `^(a|(?1)a)$`/"aaaaab" → −52 "nested recursion at the same subject
position"; `^((?1)a)$`/"a" → −52; `^(a?(?1)b)$`/"ab" → −52. So 10.46
returns −52 for SOME same-position runaways and a clean nomatch for
OTHERS, and matches a 199-deep same-position recursion when a base case
exists (design §3.3). The rule that separates the three is NOT the one
subroutines_design.md §3.3 refuted (the naive "refuse any same-position
re-entry") and is not documented in this project.

**Class.** A give-up where the oracle concludes: not a false answer (D26
tier: what a pattern MATCHES is exact; a give-up says nothing), but a
DD-2/D22 robustness gap — and a corpus cell that cannot be written
except as the finding (the D27 corpus's sr_depth.rxt carries 12 `n`/`m`
cells for this shape that FAIL by design until it is resolved). The
inverse also exists: `((?1)?a)` and `((?1)*a)` on "a" — pcrec matches
(0,1) where libpcre2 returns −52 (pcrec arguably better; no expectation
writable).

**RULE PINNED (2026-08-24, lane srK34; docs/design/subroutines_measurements/
out/recurse_loop.txt, 65/65 cells; §3.3 amended).** pcre2_match.c's
OP_RECURSE returns −52 iff ALL of: inside some active recursion; a
NEAREST ancestor recursion of the SAME group exists; the subject pointer
equals that ancestor's caller's pointer (zero cursor progress); PCRE2's
`last_used_ptr` high-water mark (the furthest byte ANY opcode has
examined, bumped on backtrack-returns and assertion completions) is ALSO
unchanged; and PCRE2_DISABLE_RECURSELOOP_CHECK is off. A failed base-case
alternative that peeks one byte further defers the guard indefinitely —
which is why 199 same-position recursions can match and why the
UNANCHORED runaways get a clean nomatch. MEASURED on the built module:
class 1 (pcrec `frames` where PCRE2 concludes): `(a|(?1)a)b` on
'a'/'aa'/'b'/'' and `^(a|(?1)a)$` on 'aaaaab' — the D27 corpus's 11
parked cells; the empty-language roots (`^((?1)a)$`, `^((?R)a)$`) answer
NOMATCH since wave E's root-minw guard; class 2 (pcrec matches where
PCRE2 −52s): `((?1)?a)`, `((?1)*a)` on 'a'. RECOMMENDATION (lane, not yet
ruled): do NOT adopt PCRE2's guard — a faithful copy needs a stored
subject pointer AND a `last_used_ptr` equivalent threaded through every
fail-and-return site of the emitted artifact, not an O(1) per-callee
slot; keep the give-up as pcrec's documented answer (OK-LIMITED's second
limit kind) and the 11 cells parked under the ratchet.

**What was needed.** MEASURE PCRE2's actual loop rule (pcre2_match.c's
recursion-loop check: when does a same-position re-entry fail the path,
when does it return −52, when is it allowed) on a probe matrix, then
decide whether pcrec adopts the same rule as a general mechanism (it
would have to preserve §3.3's 199-deep match and [DD-14.EMPTY]'s
nomatch for empty-language callees). Until then the twelve cells stay
red in the D27 corpus's triage as pcrec-wrong-by-capability.

**Milestone.** [DD-14] close triage decides its home (a follow-on row
under the module, chartered from the measurement).

**RULING (D74, Frank, 2026-08-25).** Not adopted; the give-up stays as
the documented answer, the 11 cells stay parked under the ratchet. The
runaway is a property of the PATTERN (zero-progress left recursion;
`(a(?1)?)b` is the same language and concludes) — the remedy is an
OPTIONAL ahead-of-time analysis that names it, parked as plan row
[PAT-LINT]. This entry stays as the record of the divergence; it is not
an open bug.

## K35 — OPEN (2026-08-24, found by the [DD-14] wave G lane) — a pattern-population pipeline that sorts in the AMBIENT LOCALE drops punctuation-distinct patterns: `run_vm_identity.sh` has been checking 1,660 of 2,610 corpus patterns

**Symptom.** `tests/codegen/run_vm_identity.sh` builds its population with
`find tests -name '*.rxt' | grep '^pattern ' | sed … | sort -u`. Under
`en_US.UTF-8`, `sort` collates at a level that IGNORES PUNCTUATION, so
`a{0,0}b` and `(a){0,0}b` compare EQUAL and `-u` drops one. MEASURED:
the same extraction yields 1,660 patterns in the ambient locale and
2,610 under `LC_ALL=C`. The check's capture-free / capture-bearing
populations, its byte-identity claim and its `RX_NCAPS => VM` claim were
stated over 64% of the corpus with nothing saying so. On the full
population the check is GREEN (675/675 capture-free identical, 325
capture-bearing, 1,610 refused by both) — nothing hid a failure; what
hid was a third of the corpus.

**How it surfaced (the reusable part).** Not as a failure: wave G's
dead-group exception produced a list of FOUR patterns enumerable
independently of the check, and the check only ever saw three. A check
whose population comes from a pipeline nobody counts cannot report that
the pipeline lost a third of it — the controls-sharing-a-source lesson,
arriving through the shell rather than the compiler.
`run_lookaround_identity.sh` already carried `LC_ALL=C` with a comment
saying it is not a formatting preference; the older script predates it.

**Survey (manager, 2026-08-24 ~23:3x; `grep -c sort` vs `grep -c
LC_ALL=C` over tests/**/run_*.sh):** unguarded — `run_vm_identity.sh`
(fixed by wave G), `run_object_neutrality.sh` (5 sorts, 0 guarded),
`run_backref_diff.sh` (3, 0), `run_codegen_tests.sh` (11, 0),
`run_recursion_identity.sh` (2, 1); and every script reading "sort×3 /
LC_ALL=C×2" (altdiff, endvar/backref/atomic/gstart/wordctx/mlinectx
identity, mrldiff, possdiff, rungdiff) has ONE sort to inspect. Not
every sort is a `-u` over pattern text — the audit decides per site.

**Follow-up (srG, ~23:3x) — WRONG ABOUT ALL FOUR SUITES; CORRECTED AT THE
[DD-14] CLOSE, 2026-08-25 (srClose), BY MEASUREMENT.** It read: "The
IDENTICAL idiom … sits in FOUR DIFFERENTIAL SUITES:
tests/mrl/run_mrl_tests.sh:394, tests/possessify/run_possdiff.sh:241,
tests/counterk/run_counterkdiff.sh:293,
tests/rungselect/run_rungselect_tests.sh:241 — 950 of 2,610 patterns (36%)
silently dropped from each." **Each of those four scripts carries a
top-level `export LC_ALL=C`** — at lines 36, 35, 66 and 34 respectively,
unshadowed, above every sort site — and `git log -S 'export LC_ALL=C'` puts
each export in the commit that CREATED its script (6a2f875, 23684e1,
3b0bf91, b14f369), years of lane-time before this issue was filed. Four
more scripts are in the same already-guarded state (altdiff, mrldiff,
rungdiff, possessify_tests), plus altcls_tests, counterk_tests,
prefilter_tests. So there was no ~57% population growth to harvest in any
of them and no restored differential to triage. **The follow-up was
derived by grepping for the IDIOM and not for the GUARD, which is the
same shape as the defect it was describing: a conclusion drawn from a
pipeline nobody counted.** The read on the DROPPED SIDE below is still
right, and the defect is still real and still current — MEASURED on this
tree 2026-08-25, the corpus extraction gives 1,784 patterns ambient
against 2,758 under `LC_ALL=C` — it simply did not live where the
follow-up said. WHERE IT DID LIVE, found by the close's own per-site
audit: `tests/codegen/run_object_neutrality.sh:75`, the identical idiom
fully unguarded, measured 1,798 ambient against 2,772 under `LC_ALL=C`,
so every object-code-neutrality verdict that script had ever printed was
stated over 65% of the corpus. Fixed at the close, with the measurement in
the site's comment and a stated, floored population (2,772; floor 2,630)
in its summary. AND THE DROPPED SIDE IS THE STRUCTURED
HALF: collation ignores punctuation, so each collision's survivor is the
spelling WITHOUT it and the parenthesised / quantified / assertion-
bearing spelling is the one lost (`(((a)|b){0,4})c`, `((?!(a))z)`, …) —
exactly the shapes the possessify / revdet / counter-K / MRL rungs
exist to exercise. The hazard was ALREADY WRITTEN DOWN ONCE, at
tests/cli/run_cli_tests.sh:786 (`a?+` and `a++` compare equal), and
recurred five times: the "a lesson recorded in one file does not reach
the next author" shape, not a discovery. Each of the four is a one-word
fix that grows a differential's population by ~57% and may surface real
cells — each gets ITS OWN commit and its own triage.

**Remedy — DONE at the [DD-14] close, 2026-08-25 (srClose).** Three
layers, because two of them were already there when the defect recurred
and neither caught it:
1. **Per site.** 51 `sort` sites across 24 scripts gained an `LC_ALL=C`
   prefix (tests/backrefs, tests/bench + bench/compare, tests/codegen ×11,
   tests/harness, tests/known_fail, tests/recursion, tests/spec_mod0 ×3,
   tests/thread). Populations re-measured per site: only
   `run_object_neutrality.sh` LOSES ROWS (1,798 → 2,772); the `find … |
   sort` file lists (177 `.rxt`, 35 `.c`) keep every row but change ORDER
   between locales, which matters wherever a reference build's file order
   has to reproduce.
2. **The general fix (Frank's ruling).** `export LC_ALL=C` at the top of
   `tests/lib/run_group.sh` and `tests/harness/run.sh`, so nothing
   underneath them inherits the ambient locale.
3. **A CHECK, which is the layer that was missing.** `run_codegen_tests.sh`
   sweeps every `tests/**/run_*.sh` for a `sort` used as a command word and
   fails naming any site not guarded at its own site or by an export ABOVE
   it — the position is load-bearing, and the check tests it. Measured
   2026-08-25: 62 sites across 53 scripts, all guarded; floors of 50/40
   make a collapsed sweep a FAILURE rather than a pass. Validated in all
   three directions before landing: green on the tree, RED on an unguarded
   site, RED on a script whose export was moved BELOW its sorts, and RED on
   an empty population.

**Milestone.** [DD-14.CLOSE] item 7 — CLOSED.

(The wrong 2026-08-24 follow-up survey — and the unqualified Survey paragraph above it — was the MANAGER's work, not srG's (srG found the defect; the manager surveyed the exposure and got it wrong); the correction above is the close lane's measurement. Method lesson kept in docs/dev/dev_journal.md and the check-design memory: a grep for the hazard is not a survey of the exposure — check the enclosing scope.)

## K36 — OPEN (2026-08-25, found by r36's engine critic; pre-existing) — `rx_L3` restores read the trail before the call-frame bounds guard

In VM artifacts with subroutine calls, the region-exit restore at `rx_L3`
reads `run->trail[run->resume_stack[run->call_top].trail_mark + 0..2]`
three lines BEFORE `if (rx_call_frame >= run->resume_cap) return
RX_R_INTERNAL;`. If `call_top` were ever `RX_CALL_TOP_NONE` ((size_t)-1)
the guard would report the inconsistency after three wild reads. The
ordering is IDENTICAL at 08ddcbd (pre-[DD-14.FB]); wave FB only changed
the guard's operand. Not reachable by any known pattern (the guard is an
internal-consistency tripwire, never observed firing). Fix: hoist the
guard above the three reads — costs nothing. Owner: the next emit_vm.c
change in that region; not a release blocker.

## K37 — FIXED 2026-08-25 (srRun2, [CHK-1]; found by the manager's battery on 17469b6) — `run_recursion_diff.sh` runs the COMPILER unbounded, and sabotage row S159 makes it loop forever

In the full matrix (PROCS=6) row S159 (`mark-follows-body`, src/opt/atomic.c — pcrec_bref_mark's A_CALL arm descending into u.call.body)
compiled `((?1)*a)` for 49 min 58 s of CPU at 100% before the manager
killed the process by PID: the sabotaged emitter never terminates on that
pattern, and `tests/recursion/run_recursion_diff.sh` invokes `pcrec` with
NO timeout (the D45 wrapper bounds gcc and generated matchers; the
compiler call itself is bare). Two consequences: (a) a non-terminating
sabotaged COMPILER is invisible to the row — no verdict, only a hang
until `make mech`'s own 7200 s gnutimeout would have killed all 180 rows'
evidence; (b) the same hole exists for a real compiler bug reached by any
differential script that calls `pcrec` bare. Fix: wrap every harness
invocation of the compiler in `"$TIMEOUT_BIN"` with a stated budget
(D45's compile budget is the obvious one), and audit every tests/**/*.sh
for bare `build/pcrec` calls (the K35 survey's five pipelines are the
place to start). S159's verdict on this run is whatever the matrix
recorded after the kill (probably DETECTED via the failed arm) — re-run
the row solo after the fix to pin its real signature.
**UPDATE 2026-08-25 ~07:16 (srMech, merged ae9c98c):** the 14 bare
`pcrec` calls in tests/recursion/ are now under `"$TIMEOUT_BIN"
"$(pcrec_timeout_secs)"` (run_recursion_diff.sh 8, run_frame_buffer.sh 3,
run_specimen_identity.sh 3); S159 solo afterwards: DETECTED, corpus 451
fail / 1,239 pass, recdiff 8 / 7 — the hangs are 20 s bounded timeouts,
most failures the back-edge walk overflowing the stack. STILL OPEN, two
halves: (a) run_recursion_diff.sh's generated-code compiles (`$CC
$GENCFLAGS`) and matcher runs (`"$d/t" < cells`) carry NO bound at all
where tests/harness/run.sh bounds both; (b) the survey: 45 files / 347
bare `pcrec` call sites outside tests/recursion/ (tests/cli 124,
codegen 50, ir_listing 16, …; full line-numbered list was kept at the
session scratchpad — regenerate with a grep over tests/**/*.sh). Owner:
the close lane records; a mech/harness lane fixes (one `pcrec_run`
helper sourced everywhere, not 347 edits).

**CLOSED 2026-08-25 (srRun2, continuing srRun's died-mid-task WIP; [CHK-1]
item (a)/(c)).** Both STILL OPEN halves above are done, plus the sweep
tool's own gap the population regeneration found.

`pcrec_run` (`tests/lib/gen_timeout.sh`) is the ONE helper every script
now routes a compiler invocation through — cheap `"$TIMEOUT_BIN"
"$(pcrec_timeout_secs)"` by default (~2.5ms/call, MEASURED), routed
through `scripts/watchdog` instead (~171ms/call, MEASURED — the wall +
tree-RSS + CPU + `build/watchdog.log`-line mechanism `gen_run` already
uses) only when the invocation's own pattern is CALL-BEARING or the
caller passes `--hostile` — that ~68x multiplier is why watchdog is not
the unconditional default, exactly the tradeoff `gen_run`'s own header
already documents for its high-count inner loops.

**The sweep**, regenerated per the ruling's own instruction
(`grep -nE '(^|[^a-zA-Z_/])(build/pcrec|\$PCREC|"\$PCREC")' tests/**/*.sh`,
filtered for comments/assignments/existence-tests/already-guarded lines):
41 remaining bare sites after the manager's 38-file WIP commit landed
(the mechanical sweep tool, `sweep.py`'s `TOKEN_RE`, required command
position after `^ | ; & (` or an if/elif/while/`!` keyword — a set that
does not include `{ `, so every ONE-LINER FUNCTION DEFINITION of the
shape `gen_a() { "$PCREC" ... }` was invisible to it; that shape recurred
9 times, 6 of the 8 `tests/codegen/*_identity.sh` scripts having never
sourced `gen_timeout.sh` at all before this fix). Plus one
`bash -c "... exec \"$PCREC\" ..."` in `tests/cli/run_cli_tests.sh`
case8, bounded with the outer-`"$TIMEOUT_BIN"` shape `gen_cc` already
uses for an arbitrary `bash -c` compile (`pcrec_run`'s function form
cannot reach across that fork). Final population, all 44 touched files
`bash -n` clean: **55 scripts / 427 compiler-token sites, 372 guarded
directly, 31 in a reasoned allowlist (env-var prefixes onto self-
recursive or python-worker invocations, diagnostic messages, argument
passes, a grep pattern string), 0 unaccounted for** — asserted going
forward by `tests/codegen/run_codegen_tests.sh`'s "[K37] THE
BARE-COMPILER-CALL GUARD IS STRUCTURAL" check (floors 40 scripts / 380
sites), validated red (a planted bare call named exactly) then green.

`tests/recursion/run_recursion_diff.sh`'s OTHER half — the `$CC
$GENCFLAGS` compiles and `"$d/t"` matcher runs, 4 and 3 sites — now route
through `gen_cc`/`gen_run` the same way `tests/harness/run.sh` already
does; `make test-recursion` afterward: **10 passed / 0 failed**, wall
4m42s (`§3: 1836 cells`, `§5: 28458 cells`, 0 disagreements either way —
unchanged from before this fix, confirming the bound changed nothing
about the answers). S159 solo (`bash tests/mech/run_sabotage_matrix.sh
S159`) re-run after this fix: see the manager's own re-run for the
current signature — the compiler invocation itself was already bounded
by srMech's earlier fix (merged ae9c98c), so this fix's own contribution
to that row is the downstream compile/run bound, not the hang itself.

**NOT FIXED, a genuinely separate finding this sweep surfaced and did NOT
silently absorb**: `tests/registry/compliance_section.py` and
`tests/vm/vm_oracle.py` both call the compiler via python's
`subprocess.run()` with NO `timeout=` at all
(`tests/recursion/run_lookbehind_call_sweep.py`'s `pcrec_compile()`
likewise) — the identical S159-class hazard, one level down, outside a
textual sweep over bash source and outside this ruling's own stated scope
(a grep over `tests/**/*.sh`). `tests/fuzz/fuzz.py`'s own compiler calls,
by contrast, already carry `PCREC_TIMEOUT` throughout. A K37b candidate,
not created here.

## K38 — FIXED 2026-08-26 (srK38) — the VM emitter's fixed-size NAME BUFFERS truncate identifiers at long prefixes: an artifact with a 60-character prefix (the documented maximum) does not compile

**Symptom.** `build/pcrec -p p1234…(60 chars) --engine=vm --features all
-o x.c 'a(b)+c'` emits C in which several `<prefix>_…` identifiers are
cut short (`…_sp` → `…234`, a class-guard expression loses its `]`), so
`gcc` fails with "undeclared" / "expected ']'". `cli/main.c`'s
`valid_prefix` and `src/core/limits.h`'s `PCREC_MAX_PREFIX_LEN = 60`
accept the prefix; docs/spec/cli.md §1 promises it. The DFA path was not
checked; a short prefix (`rx`) is byte-identical to before.

**Cause.** src/gen/emit_vm.c builds emitted names into fixed buffers —
`char nm[48]` (~:864, ~:2695), `entrypos[32]` (~:3085), and until
2026-08-26 `frames_sentinel[64]` (srTier's, fixed at the same time:
`PCREC_MAX_PREFIX_LEN + 32`) — via `snprintf`, which truncates silently.
gcc's `-Wformat-truncation` flagged only the sentinel because the
others are built through helpers it cannot see through.

**Class.** A miscompile (not a give-up) reachable only through a
prefix longer than any test uses — every corpus artifact is `rx`. The
spec's promise is exact (cli.md §1) and false at the boundary.

**Fix (general).** Size every emitted-name buffer from
`PCREC_MAX_PREFIX_LEN` (one macro for "a prefixed name": limit + the
longest suffix + NUL), sweep `emit_vm.c`/`emit_dfa.c` for `char
[a-z_]+\[[0-9]+\]` buffers that receive a prefix, and add a tests/cli
case that emits AND COMPILES a 60-character-prefix artifact on both
engines (a spec-first witness: the promise is the test). Sonnet-sized;
not started.

**FIXED 2026-08-26 (srK38).** `src/core/limits.h` gains
`PCREC_MAX_EMIT_NAME_LEN = PCREC_MAX_PREFIX_LEN + 96` (one macro for
every buffer that builds an emitted name/sub-expression from the prefix,
sized generously over the worst OBSERVED content — a slot expression,
`<prefix>_<slot-name>`, at up to 108 bytes at the 60-char maximum).
Reproduced FIRST with a real 60-char prefix run through `gcc -Wall
-Wextra` (case3's own pattern `'a'` was too small to reach any of it),
which found the family the symptom above only guessed at: `nm[48]` and
`entrypos[32]` (named in the original report) turned out NOT to carry
the prefix and needed no change; the real offenders were `vm_slot_expr`'s
caller-supplied `sl[64]` (×2, the lookaround/lookbehind restore sites —
this is the `…_sp` → `…234` truncation the symptom described, though the
manager's diagnosis of WHICH buffer misattributed it), the possessive/lazy
span-cursor family (`byte[64]`, `cx[64]` ×2, `cur[64]`, `val[96]` ×2), the
reverse-deterministic rung's `rv[80]`/`cur[96]`, `byte[80]`
(`subject[<rv-cursor> - 1]`), and — the sharpest finding — `ga[64]`/
`gs[64]` (`%s_revdet_group_span`/`%s_revdet_group_seen`) truncating to the
IDENTICAL wrong string (both share their first 18 suffix bytes), which is
why the group-span WRITE and the group-seen FLAG collapsed onto one name
in the emitted C, and why `val[64]` in the separate recovery loop (same
formula) never showed as a DISTINCT gcc error — its truncated text was
byte-for-byte `ga`'s, and gcc reports an undeclared identifier once per
function. `emit_dfa.c`'s one prefix-carrying buffer (`residual[96]`,
`<prefix>_next_pos`) was never observed truncating (a DFA-engine sweep
with a 60-char prefix compiled clean) but was widened to the same macro
for consistency rather than left on its own hand-picked size. Widening
`rv`/`cur` also moved gcc's OWN `-Wformat-truncation` worst-case estimate
for two downstream buffers that embed them (`pv[112]`, `cnt[192]` ×2,
both revdet frame-mark/prev-position sites) past their old sizes — a
second-order effect of generous sizing, fixed by widening those two
alongside. Output is BYTE-IDENTICAL for every in-range prefix: swept
1,784 corpus patterns × {`"rx"`, a 1-char prefix} × {auto, vm} = 7,136
compiles, reference binary vs fixed binary, 0 differences (stdout/
stderr/exit code all compared). Witness: tests/cli/run_cli_tests.sh
case17 (two rich patterns — one exercising every confirmed VM buffer in
one compile via a lookbehind+lookahead+backreference+possessive+captured-
span+captured-alternation pattern, one DFA-only — at both the 60-char
and 1-char prefix boundaries, both engines); verified DETECTING by
running the harness against a pre-fix binary: the VM/60-char cell goes
red with exactly this issue's symptom (undeclared `_SL`, `expected ']'`,
undeclared `_re`/`_rv`) while the DFA and 1-char cells correctly stay
green. `make test-codegen` and `make test-cli` green afterward
(287/287 CLI cases, `make strict` clean).

## K39 — RE-SCOPED, NOT CLOSED (2026-08-29, Frank's ruling B) — count-BOUNDED at the default, count-INDEPENDENT under `-fprefilter-collapse`; the VM HYBRID's inlined DFA prefilter SCALES WITH A BOUNDED-REPEAT COUNT: `((a)|b){0,4000}c` emits 1,994 lines at the default vs 869 for `{0,400}`, while the VM body itself is count-independent (573 lines at any count with the prefilter off)

**Symptom.** MEASURED at 32890e2 (before the day's scaffolding): default
engine (auto = VM + hybrid prefilter) `{0,400}` 869 lines, `{0,4000}`
1,994 lines, `{0,40000}` refused (NFA state cap 131,072 — the pattern's
own NFA, a different limit); `--engine=vm` (prefilter none) 573 lines
for every count; `-fno-prefilter` likewise. The 1,125-line difference is
the inlined DFA scan of the prefilter, which is built from a language
that carries the repeat count.

**Why it matters.** [ENG-BREP]'s claim — the counter rung makes the
count irrelevant to the emitted size — is true of the VM body and FALSE
of the default artifact; the two size checks (tests/vm, tests/codegen/
run_ir_listing.sh) asserted `lines < 2000` and passed by 6 lines of
slack until [OPT-1]/[DD-13c]'s six scaffolding lines consumed it
(2026-08-26 battery). Both checks now compare `{0,4000}` against
`{0,400}` with the prefilter denied (the claim) and PRINT the auto sizes
(this issue). Cost: compile time + artifact size proportional to the
count for every hybrid VM artifact with a bounded repeat.

**Fix candidate ([OPT-4], not started).** A candidate-start prefilter
only needs "can a match BEGIN here" — a count-INDEPENDENT language (the
pattern's first-byte class / a count-collapsed pattern, e.g. the repeat
lowered to `{0,1}` or `*` for prefilter purposes). Building the hybrid's
DFA from that instead of the full pattern would make the artifact
count-independent again and shrink compile time; the identity gates
(answers unchanged; a prefilter is answer-identity-preserving by D46's
rule) are the control. A loop item: charter from a bench row that shows
the cost, per D77.

---

**CLOSED 2026-08-29 by [OPT-4], and this is what closed it.** The fix candidate
above is what was built, in the second of its two forms: above a measured
budget the hybrid's forward AND reverse machines are built from the
count-collapsed lowering — every `A_REP` with `rmin > 1 || rmax > 1` as
`X{min(rmin,1),}` — a superset whose soundness proof never mentions the count
(`docs/design/prefilter_count_independence.md` §3). It acts on the LOWERING,
upstream of both directions, because this issue's own one-line diagnosis
undercounted the population: for `((a)|b){0,400}c` the `Sigma*` wrap absorbs
the bound and only the REVERSE machine carries the count, while
`foo((a)|b){0,1000}bar` carries it in both, so a fix confined to one direction
would have missed half the corpus.

**THE SYMPTOM, RE-MEASURED at the close.** This issue was filed on `{0,400}`
against `{0,4000}` at 869 and 1,994 lines. At the default today both artifacts
are **1,026 lines — delta 0** — and in bytes 22,728 against 22,731 code bytes,
the three-byte difference being the literal `400` against `4000` in the emitted
prose. With `-fno-prefilter-collapse` the same pair is 1,225 against 3,025
lines, which is this issue's defect intact and is the control proving the
equality above is the collapse rather than an artefact.

**Held by a check, not by this entry.** `tests/codegen/run_prefilter_collapse.sh`
asserts the count-independence on the DEFAULT artifact (the one a user gets)
with its failing-direction control, the stamp against BYTES over seven
witnesses, the H3 ceiling consequence on every collapsed corpus artifact, the
macro's IFF over 2,772 patterns, and a form census that bands the population on
both sides. 36 assertions, all green at d4d439e.

**Costs, measured rather than waived** (`docs/spec/tuning.md` §2.17's table and
the design note §7): the collapse buys size and compile time and it PAYS in
candidate starts — the named worst case, `((a)|b){0,400}c` on 100,000 `a` then
`c`, runs 9.24 s / 99,601 VM attempts collapsed against 0.000011 s / 1 attempt
exact, same answer. `-fno-prefilter-collapse` recovers today's artifact byte
for byte, and `-fprefilter-collapse` forces the collapse below the knee.

**RE-OPENED AS RE-SCOPED, 2026-08-29, BY FRANK'S RULING B — read this instead
of the paragraph above it.** The close above was measured against the KNEE
default (collapse whenever the exact NFA exceeded 128 states). The merge
battery then found what that default cost, on a corpus cell rather than on a
benchmark: `(a{1,3}){65}` in `tests/base/d27_k23_ambiguous_decomposition.rxt`
collapsed at 392 exact NFA states, lost its `prefilter-window` ceiling, and
went from answering `0,100 90,100` in 0.00 s to returning `PCREC_ERR_STEPS`
after **13.34 s** on its broken-run subjects. Answer identity was not violated
(D46 is about an unbounded step budget) but a documented caller-visible bound
was, on a pattern that compiled fine.

Frank re-ruled the default to **B, fallback-only**, and K39's status follows:

- **At the DEFAULT the artifact is count-BOUNDED, by the emitted-size CAPS
  and nothing else.** The prefilter is the pattern's own language; when the
  caps refuse the resulting artifact, `compile_driver` retries once with the
  count-collapsed prefilter and ships that instead. So the size still moves
  with the count — `((a)|b){0,4000}c` is larger than `{0,400}` — but it cannot
  run away, because the cap is what triggers the retry.
- **Count-INDEPENDENCE is reachable, under `-fprefilter-collapse`**, which
  collapses wherever a collapsible repeat exists. That is the flag's whole
  purpose now.
- So K39's symptom is BOUNDED rather than removed, and the issue is re-scoped
  rather than closed. `tests/codegen/run_prefilter_collapse.sh` §1 asserts both
  halves separately, which is the shape of the ruling: the force cell proves
  count-independence, the default cell proves a capped artifact still ships.

The knee is deleted — there is no `PCREC_PREFILTER_EXACT_NFA_STATES` any more
and deliberately nothing in its place, because under ruling B the caps are the
only quantity that decides. The bar sweep that chose 128 is kept in
`docs/design/prefilter_count_independence.md` §4 as the record of a decision
that was REVERSED, and §10 carries the ruling chain (A, the corpus regression,
B).

## K40 — CLOSED 2026-08-28 (lane sel1) — under `--engine=auto`, a DFA build that overflows a cap REFUSES the whole compile instead of falling back to the VM, even when the pattern's own DFA-erasure is only being built as the VM's auto-selected PREFILTER MERGE-REVIEW LANDING FIX (manager, 2026-08-28, on f75a33f): the retry left the refused build's diagnostic in `err->msg`, so a successful fallback returned 0 beside "pattern too complex…" (library probe: rc=0, msg set); `compile_driver` now clears `err` on the retry path — probe rc=0, msg empty.

**Symptom.** `build/pcrec -p rx --features all --engine=auto -o out.c
'\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:timeout|timed out|refused|denied|
unreachable)\b'` refused "pattern too complex for the DFA engine (>32000
states; try --engine=vm)" in 0.52 s; `--engine=vm` (no prefilter) compiled
the same pattern in 0.00 s. Reproduced on main c60679b, filed as plan row
[SEL-1] (bench O-7 item 6, ask iii; Frank ruled 2026-08-28).

**Cause.** `src/opt/select_engine.c` chooses an engine (and, for a VM
choice under `auto`, derives whether to attach a capture-erased DFA
prefilter) from the AST ALONE, before any automaton exists — it has no way
to know a cap will overflow. `src/core/compile.c` then built the DFA pair
unconditionally whenever `fit.chosen == ENGM_DFA || fit.prefilter`, and
`src/ir/dfa.c`'s two "pattern too complex" `ctx_fail` sites `longjmp`
straight to the ONE recovery point in the compiler (`compile_driver`'s
`setjmp`), aborting the whole compile — including a case where the DFA
being built was never the chosen ENGINE at all, only an auto-selected
optimisation (the prefilter) that D46/§4.7 already documents as safe to
drop (a backreference or a subroutine call already drop it the same way,
for a different reason).

**Class.** A resource refusal reached through the WRONG mechanism (D22's
kind of refusal, delivered as if it were a construct the engine cannot
honour) rather than a miscompile — every answer pcrec DID produce for this
pattern family was correct; the defect is a compile that should have
succeeded and did not.

**Fix.** `Ctx` gains `dfa_disabled`/`dfa_overflowed`/`dfa_overflow_why`
(`src/core/internal.h`; the last two set by the two `dfa.c` sites,
unconditionally and cheaply, immediately before their existing `ctx_fail`
— the diagnostic text for `--engine=dfa`/`-fprefilter` is UNCHANGED).
`compile_driver` (`src/core/compile.c`) becomes a bounded ONE-SHOT RETRY
loop (`COMPILE_MAX_ATTEMPTS = 2`) around the existing single `setjmp`: on
an eligible overflow (`cx.dfa_overflowed`, `--engine=auto`, no
`-fprefilter`) it reruns the whole pipeline once with `dfa_disabled` set.
`src/opt/select_engine.c` gains one more row in its existing
`forces_captures`/`forces_registry` fixpoint, `forces_dfa_overflow`
(excludes `ENGM_DFA` and supplies `RX_ENGINE_WHY`'s text when
`dfa_disabled`), and the SAME flag folds into the prefilter derivation
(`has_bref || has_call || cx->dfa_disabled` all silently drop it) — one
mechanism, not a try/catch at the `ctx_fail` site and not a second
selector. `src/gen/emit_vm.c`'s `--emit-ir` listing gets its own arm for
the same reason the backreference/call routes needed one ([M6.5.2]/[DD-14
wave E]'s precedent): without it, a dropped auto-selected-prefilter's `;
prefilter` line falsely named `--engine=vm`. Verified: the witness now
compiles under `auto` (`RX_ENGINE "vm"`, `RX_ENGINE_WHY "dfa overflowed:
>32000 states..."`, `RX_VM_PREFILTER "none"`
— **`"none"` was true when this was written and is not any more: [OPT-4] STEP 3
(2026-08-29) put a rung BEFORE the drop, so this same witness now stamps
`RX_VM_PREFILTER "hybrid"` / `LANG "count-collapsed"` /
`LANG_WHY "dfa overflow retry, exact nfa 462"` and runs 2.4-3.4x faster on the
bench's throughput subjects. The rest of this entry is unaffected: the ENGINE
fallback K40 describes is exactly what still happens, and the drop remains the
outcome when the collapsed machine overflows too or when
`-fno-prefilter-collapse` is passed. See docs/spec/tuning.md §2.5**); `--engine=dfa` and
`--engine=vm -fprefilter` still refuse with the unchanged diagnostic;
`tests/base/k18_cost_gates.rxt`'s fuzz-found witness (a DIFFERENT pattern
that hits the same cap, with a live capture so the VM was already chosen
and only its auto-prefilter overflowed) moved from a `perr` block to two
oracle-verified match cases for the identical reason. `make strict` clean;
targeted `tests/vm`, `tests/prefilter`, `tests/cli`, `tests/codegen/
run_dfa_stamps.sh`, and the full `tests/base/` corpus (3,603/3,603) all
green; a targeted `-fsanitize=address,undefined` build of the compiler
showed no leak/UB on the retry path. The full `make test` battery was not
run by this lane (box rule: one heavy suite at a time; flagged for the
manager to run at merge).

## K41 — CLOSED 2026-08-29 ([OPT-4] STEP 3, lane opt4b) — both witnesses now compile under the DEFAULT caps; the entry below is the [ART-SIZE] disposition it was closed from

**[ART-SIZE]'S DISPOSITION, read this before the original entry below.** The
emitted-size caps and the unroll ladder (D84; `docs/design/
artifact_size_term.md`) change what both witnesses do, by DIFFERENT
mechanisms, and the distinction is the point:

- **Witness 1 is FIXED.** Its size IS counter-rung body replication, which is
  exactly what the size term's ladder acts on: the term selects `K=1` and the
  artifact goes from **2,004,449 bytes to 116,511** (comment-excluded
  1,719,349 → 87,118), with gcc's own cost following it from 55.13 s to about
  1 s. It compiles, it is no longer oversize, and it re-enters the fuzz gate's
  ordinary accept/compare population.
- **Witness 2 is REFUSED, not fixed.** Its size is its PREFILTER — 3,108
  computed-goto states and 34,188 jump-table entries against only 552 VM nodes
  — which `K` cannot touch (K=1 saves 8.7 %). Both caps refuse it: 670,650
  code bytes against a 500,000 limit and 1,220,606 total against 1,000,000.
  That is the correct outcome (it costs gcc **66.92 s at -O2**, 6.7× D45's
  budget) but it is a REFUSAL, and the pattern that produced it is still a
  pattern pcrec cannot compile.

**RE-CHECKED AND CLOSED 2026-08-29 per this row's own revisit clause, from a
gate RUN.** [OPT-4] shrank witness 2's prefilter, which is exactly the trigger
the clause named, and the outcome is measured rather than predicted:

- **Witness 2 is ACCEPTED under the DEFAULT caps.** Its exact forward NFA is
  3,423 states against a budget of 128, so the prefilter is built from the
  count-collapsed language and the artifact goes from **671,039 code bytes
  (REFUSED)** to **152,302 ACCEPTED** — 189,701 total against the 1,000,000
  limit — stamping `RX_ENGINE "vm"`,
  `RX_VM_PREFILTER_LANG "count-collapsed"`,
  `RX_VM_PREFILTER_LANG_WHY "exact nfa 3423 > 128"`. gcc `-O2 -c` falls from
  **66.92 s to 2.04 s** (99 MB), comfortably inside D45's budget. The design
  note predicted ~158,601 code bytes before the code existed; the actual is
  within 4 %.
- **The mechanism is confirmed, not merely correlated.** Compiling the same
  witness with `-fno-prefilter-collapse` still REFUSES, with the identical
  671,039-byte message. The prefilter was the cost, the collapse is what
  removed it, and the deny flag reproduces the defect on demand.
- **It is not just smaller, it is RIGHT.** With witness 2 back in the fuzz
  gate's accept/compare population, `content divergences` and `accept/reject
  divergences` are both still **0** across all 15 of its subjects. A superset
  prefilter that had broken H1 (sound rejection) or H2 (start is a lower
  bound) would surface there and essentially nowhere else in the suite.

**THE GATE PINS MOVED, RE-DERIVED FROM A RUN** (not from the arithmetic that
predicted them), and witness 2 leaves the oversize/refusal accounting by a
THIRD route — not fixed by a smaller body like witness 1, not refused like its
own previous state, but compiled: `both accept` 182 -> **183**,
`emitted-size cap` 1 -> **0**, `subject pairs compared` 2730 -> **2745**,
`oracle inconclusive` 3 -> **3** (unchanged). The `emitted-size cap` bucket is
pinned at 0 rather than deleted: it and its diversion still exist and still
matter, and a pin of 0 is the statement that at this fixed seed nothing
currently refuses — a fact that can regress.

**What remains true and is NOT closed by this.** Witness 1's shape (counter-rung
body replication) is fixed by [ART-SIZE]'s ladder, not by this row, and the
underlying VM lowering still replicates for nested bounded repeats — the caps
are what stand between that and a gcc the user waits on. K41 is closed because
both of its witnesses compile within the documented budgets, not because the
lowering became cheap.

**STILL CLOSED AFTER FRANK'S RULING B (2026-08-29), BY A DIFFERENT MECHANISM,
AND THAT IS THE INTERESTING PART.** The close above was measured under the knee
default, where witness 2 collapsed because its exact NFA was 3,423 states.
Ruling B deleted the knee, so nothing about this pattern's SHAPE makes it
collapse any more — instead the exact artifact is built, the code cap REFUSES
it at 670,952 bytes, and `compile_driver`'s size rung retries with the
collapsed prefilter and ships it. The artifact stamps
`RX_VM_PREFILTER_LANG_WHY "size cap retry, exact 670952 > 500000"`, which is
the rung naming the comparison that triggered it.

So the outcome is unchanged and the reason is better: witness 2 is rescued
because its artifact was too big, which is what K41 was always about, rather
than because a state count crossed a threshold that had nothing to do with the
cap. `-fno-prefilter-collapse` still refuses it — that flag now denies the
rungs, and observing this refusal is the main thing it buys a caller.

**PROVED FROM A GATE RUN, not from arithmetic** (the manager's standing rule
for this row): `tests/fuzz/run_capturediff_gate.sh` PASSES with every pinned
count unchanged — `both accept` 183, `emitted-size cap` 0, `subject pairs
compared` 2745, `oracle inconclusive` 3 — and `content divergences` and
`accept/reject divergences` are both still **0**. Witness 2 is in the compare
population and answers identically to PCRE2 on all 15 of its subjects under the
new mechanism, which is the evidence the size rung produces a correct artifact
and not merely a small one.

---

**The [ART-SIZE] disposition, kept because it is what the close was measured
from.** K41 was re-scoped rather than closed at that point: Its original fix direction — "a
VM-side emitted-PROGRAM-SIZE cap in `src/core/limits.h`, refusing before
emission" — is built, and the caps refuse just before the file is written
rather than before emission (there is no pre-emission node count; see the
design note's §2.2a). What remains open is witness 2's MECHANISM: the VM
hybrid's inlined prefilter scaling with a bounded-repeat count, which is
**[OPT-4]/K39's** to shrink. D84's own revisit clause says witness 2 should
pass under the default caps once [OPT-4] lands, and that is the trigger to
re-check this row and the gate pin below.

**THE FUZZ-GATE PIN MOVES 2 → 0, AND NOT BECAUSE THE SHAPES DISAPPEARED.**
`tests/fuzz/fuzz.py` classifies the oversize bucket by emitted `.c` size
alone, so witness 1 leaves it by SHRINKING (116,511 bytes, an order of
magnitude under the 1,000,000 classifier) and witness 2 leaves it by being
REFUSED (there is no artifact to classify). Re-derive the coupled counts from
a gate RUN rather than by arithmetic — witness 1 re-enters the accept/compare
population and witness 2 does not — and note that a refusal needs its own
bucket: `fuzz.py` gained `size_cap` on `state_cap`'s precedent, because a
documented ceiling doing its job is not an accept/reject divergence and would
otherwise be counted as one.

---

## K41 — the ORIGINAL entry (2026-08-28, found by the manager's [SEL-1] landing battery, tests/fuzz/run_capturediff_gate.sh) — a VM artifact for a deeply-nested, wide bounded-repeat pattern can exceed D45's gcc compile-time budget, and [SEL-1] is what UNHID it rather than caused it

**Symptom, identified by the deterministic property (manager correction,
2026-08-28): SIZE, not gcc's CPU-time outcome on a given box.** The VM
artifact for a deeply-nested, wide bounded-repeat pattern can emit a `.c`
file well past 1,000,000 bytes — `tests/fuzz/fuzz.py`'s own
`K41_OVERSIZE_BYTES` threshold, checked BEFORE and INDEPENDENTLY of
whether gcc happens to compile it in time on a given box (a fixed
CPU-second `ulimit` against box speed is timing-sensitive; the emitted
artifact's byte count is not — deterministic per `--seed`, the property
this bucket is now classified by, verified byte-identical across three
consecutive runs of the gate). At the fuzz gate's fixed `--seed 1
--patterns 300` slice, exactly TWO patterns cross the threshold:

    1{1,}b1{0}1{2,3}?|(c0{1}.)|((\n.*|.{2}|(?:a{2,3}|0{0,30}cc|c{0,3}bc{2,3}){1,}){5,10}.{2,}|[a-c-e]{1,}?|a$b){28,30}[a-z0-9]{28,30}(\n[^abc]{28,30}?){1,}

(2,004,449 bytes at this measurement — close to, not identical to, an
earlier 2,004,778-byte reading; harmless drift from unrelated emitter
changes between measurements, not a second finding) and

    (?:(0{28,30}|[\n\t]?(?:c{1}?c{28,30}?a|1{1,}a{0,30}0|c){5,10}?\n){0,3}?b[\x6]|[^abc]b(0{2,}[\]]|(b{0,30}a??|a{0,3}?\n)[-a]|^))a?|a(\n{1,2}b{1,2}|0)??a{0,30}$

(1,250,766 bytes) — the second pattern was invisible to the gate's
earlier, gcc-error-text-based classification because it happens to
compile within this box's gcc budget today, so it never produced a
`GCC-FAIL` line at all; it would have gone on being silently compared
like any ordinary pattern despite being every bit as oversize as the
first. This is the concrete case for classifying by size: **gcc's own
compile outcome is a CONSEQUENCE on a given box, not the defining
symptom** — the first witness has been observed both ways (see below),
and the second compiles fine on the landing box but is not thereby "not
K41". `--engine=auto` compiles the first witness (`RX_ENGINE "vm"`,
`RX_ENGINE_WHY "capture group at pattern offset 18"`, `RX_VM_PREFILTER
"none"`); `--engine=vm` produces the byte-identical artifact. Manually
forcing `gcc -O2 -c` on that artifact (a higher optimization level than
the fuzz harness's own `-O0` default) reports `gcc: internal compiler
error: CPU time limit exceeded`, MEASURED: 52.9 s / 540 MB — the
consequence, on that box at that optimization level, of the artifact's
size, not an independent fact about the pattern.

**Cause.** The pattern's `{28,30}`-repeated alternation over a nested
`{5,10}`-repeated body replicates enormously under the VM's bounded-repeat
lowering (`docs/design/engine_m4.md` §3.3: no counter, no suppression test
— [ENG-BREP]'s counter rung does not reach every nested shape), and
nothing in `src/gen/emit_vm.c` bounds the emitted PROGRAM SIZE the way
`src/core/limits.h`'s DFA-side caps bound state counts. Before [SEL-1] this
specific pattern's auto-selected PREFILTER's capture-erased DFA overflowed
`PCREC_MAX_DFA_STATES_TABLE` first and the compile REFUSED — so the VM body
that gcc chokes on was never emitted at all. [SEL-1] (K40) makes that
overflow a fallback rather than a refusal, so the VM artifact now ships,
and IT is what exceeds D45's gcc budget. This is not a defect in [SEL-1]'s
own mechanism (every answer the VM artifact WOULD produce, if gcc could
finish, is correct) — it is a pre-existing VM-emission gap the DFA
refusal happened to mask for this one shape, discovered because the mask
came off.

**Class.** A TEST-HARNESS-VISIBLE resource limit (D45's gcc compile-time
budget), not a pcrec correctness defect and not a caller-visible refusal —
`build/pcrec` itself compiles the pattern in well under a second; the cost
is entirely in gcc's own back end compiling the emitted C.

**Fix direction, chartered separately (not built here).** A VM-side
emitted-PROGRAM-SIZE cap in `src/core/limits.h`, refusing before emission
the way the DFA-side caps already refuse before emission — `PCREC_MAX_VM_
NODES`/`PCREC_MAX_VM_REPEAT_COPIES`/`PCREC_MAX_VM_REPLICATION_PRODUCT`
bound the same family already but did not catch this shape; the new
budget needs its own measurement of where a legitimate pattern's emitted
size tops out, the same way K7/[M4.7b]'s subset-element budget was sized
from a measured corpus maximum rather than guessed.

**Interim handling (this lane, `tests/fuzz/run_capturediff_gate.sh`),
REVISED 2026-08-28 (manager correction).** An earlier version of this
handling classified the gate's K41 bucket by grepping gcc's own error
text ("CPU time limit exceeded" / "internal compiler error") — rejected
as a flaky gate design: a bucket pinned at exactly 1 that reads 0 or 1
depending on whether gcc crosses its fixed CPU-second `ulimit` by a
couple of seconds is red on one box and green on another, and trains
reviewers to ignore it. `tests/fuzz/fuzz.py` now classifies "K41 oversize
artifact" by the emitted `.c`'s byte SIZE alone (`K41_OVERSIZE_BYTES`,
checked before and independently of gcc), which is fully deterministic
per `--seed` — verified byte-identical across three consecutive solo
runs of the gate. That bucket is pinned to EXACTLY 2 (both witnesses
above), asserted separately from the ordinary "gcc compile fails" bucket
(pinned at 0 — a gcc failure OUTSIDE the size-classified bucket stays a
real FAILURE, never absorbed by this row's allowance). gcc's own outcome
on each oversize witness (compiled / over-budget) is read from fuzz.py's
summary as INFORMATION ONLY, printed with the witness pattern named
(`K41-WITNESS pattern=... size=... gcc=...`) but never a pass/fail
signal — this design has no bucket left whose correctness depends on
gcc's CPU-time luck. Pulling both witnesses fully out of the ordinary
accept/compare pipeline also moved three other pinned counts
arithmetically (both accept 183->181, subject pairs compared 2745->2715,
oracle inconclusive 3->0 — see `run_capturediff_gate.sh`'s own EXPECT
comment for the derivation). A movement of the K41 bucket to 0 means
neither witness reaches its shape any more (K41 closed, or the
generator/seed changed — re-derive, do not silently widen); a movement
above 2 means a NEW pattern is oversize and the gate stays RED naming
it, with the count, the witness pattern, and this K-row cited in the
failure message — never a silent allowlist.

## K42 — STRUCTURAL RESIDUAL (acknowledged by Frank 2026-08-30, D89 item 5): composition's absolute references and colliding names have NO EXTERNAL ORACLE

[DD-13b.W1]'s composer re-bases a library's group numbers into the
caller's space (w1_impl.md §2.5) and resolves name collisions by lexical
scope (D87). libpcre2 can check the COMPOSED TEXT's capture count and
ovector (check W-8), but only over the population W-1 generates — and a
D27-blinded test author shares exactly those oracles, so blinding buys
no independence here. The controls that exist: the composed text is
itself an independent re-derivation the composer is compared against
(F10), and the identity gate. This is a limit of the test surface, not
a known miscompile; it is recorded so that a future "W-8 is green"
claim is read at its true scope (W-1's population) and not as proof
over absolute references or collisions in general. Not [DD-13b.W1.3]'s
to discharge. Closes when an oracle independent of pcrec's own
composer exists (a second composer, or PCRE2 gaining library
composition — neither planned).

## K43 — INFRASTRUCTURE (2026-09-01, forty-ninth session, found by battery 8's `make test LINTGEN=1` stage): the LINTGEN axis is RED on this box's gcc 15 — `-fanalyzer` false positives (CWE-457) on VM artifacts whose driver calls the anchored entry, plus the traced-artifact and rung-boundary build cases

`make test LINTGEN=1` fails in five sections (encseam, vm, registry's
definitions-oracle, codegen's [DD-14.FB] --trace check, cli before its
witness moved) with `-Werror=analyzer-use-of-uninitialized-value` at
`RX_SET`'s trail-save line (`run->trail[...].saved_value =
slot_values[(slot_)]`) inside `<prefix>_match_anchored`.

**MEASURED FALSE POSITIVE, and PRE-EXISTING**: `<prefix>_run_state_init`
initializes every slot (`for (i = 0; i < NSLOTS; i++) slot_values[i] =
PCREC_UNSET;`) before any program byte runs, so the flagged read is
covered; gcc 15's analyzer cannot prove the loop covers the index through
these drivers' call shapes. Reproduced IDENTICALLY on the pre-merge tree
(e8ef9c8 archive build: `pcrec -p fa -o fa.c '(a*)*'` + the encseam
find-all driver + `-fanalyzer -Werror` = the same CWE-457 at the same
macro), so the cc/o42 merges did not cause it — battery 8's stage was
simply the first in some time to actually exercise LINTGEN over these
sections (the ruling in docs/testing.md "Battery integration" says
battery-grade `make test` adopts LINTGEN=1; recent green batteries
evidently ran it plain, or gcc's analyzer has moved since SAN-1's
2026-08-13 measurement — R5-Q1's "a newer gcc's new opinion" applied to
the analyzer axis).

**Interim disposition (manager, 2026-09-01): the battery's test stage
runs PLAIN `make test`; LINTGEN=1 stays opt-in and is expected red on
gcc 15 until this entry is fixed.** Fix directions, unruled: (a) per-site
`-fanalyzer` suppressions or a documented exclusion list for the known
driver shapes; (b) an emitted-code change making the init provable
(e.g. `= {0}`-style aggregate init — an abi-relevant emitted-bytes
change, D76); (c) revisit on a newer gcc. Repro:
`build/pcrec -p fa -o fa.c '(a*)*' && gcc -O1 -std=gnu11 -Wall -Wextra
-Werror -fanalyzer -Itests/encseam -o drv tests/encseam/findall_driver.c
fa.c`.

## K44 — INFRASTRUCTURE (2026-09-01, forty-ninth session, batteries 8b/8c/w12): ONE load-marginal compile cell reds full-parallelism batteries, green solo every time — counterk.rxt:1807's `((a)|ab){4000}c`

Three consecutive full `make -k -j12 test` runs (batteries 8b, 8c, and
w12's) each failed EXACTLY ONE corpus cell on a compile-time wall/CPU
budget, and in three of three diagnoses the cell was GREEN SOLO with its
compile cost UNCHANGED against the pre-merge tree: counterk.rxt:1807
(`((a)|ab){4000}c`, pcrec-compile exit 124; 3.06 s solo vs 3.31 s
pre-merge) twice, and tests/resource's `(a|b){0,30000}` 45 s-CPU
watchdog once (30/30 solo). Mechanism: the battery's -j12 × PROCS
oversubscription inflates wall AND CPU accounting ([TT-10]'s finding)
past budgets sized for a quiet box; the cli `--warn-emit-bytes`
comment's "3-5x under -j12" is the same class.

STANDING DISPOSITION (manager): a battery test stage red on EXACTLY one
of these cells, green solo, is GREEN-BY-DIAGNOSIS — record the solo
number, cite this entry, do not re-pin anything (lesson 3 checked each
time: the bytes did not move). FIX DIRECTIONS, unruled: (a) route the
harness's per-pattern pcrec compiles through tests/lib/load_guard.sh's
third outcome (INCONCLUSIVE-under-load, the [TT-10] shape) so a loaded
box says "inconclusive" instead of "failed"; (b) run battery test
stages at reduced PROCS (measured: PROCS=6 still red once); (c) accept
and document. Whoever takes (a) should re-read learnings §3 first — an
inconclusive that absorbs real regressions is worse than this noise.

## K45 — INFRASTRUCTURE (2026-09-02, fiftieth session, found by lane opt5i's `make test-axes`): `make test-axes` is RED ON MAIN for [ART-SIZE.2]'s nested-repeat tower — five axes report `refused_undoc=2` on tests/size/size_term.rxt:34-35, pre-existing since fa9b6d4 (2026-08-29)

The block `(?:(?:(?:(?:(?:(?:a|b){41}){41}){41}){41}){41}){41}` carries
`engine vm` precisely so the NFA is never built (its own comment: found
by writing the cell without it and watching it fail for the wrong
reason). run_axes.sh layers each axis's RXTFLAGS on top of the block's
own flags, and for FIVE axes that defeats the `engine vm` shortcut or
moves the refusal onto a limit the axis does not list: `-fno-counter`
(bit 6: the nested-replication limit, 2,825,761 > 131,072),
`-fprefilter` (9) and `--engine=dfa` (§2.11) (the NFA state cap,
131,072), `-fno-altcls-merge` (10) (the VM emitted-node cap), and
`-fno-size-term` (18) (the emitted-code cap). Zero MISMATCHES on any
axis; every failure is an UNDOCUMENTED-REFUSAL line, i.e. a
documentation/exclusion gap, not an answer defect. MEASURED by opt5i:
main's own compiler (5496ca6, built from `git archive`) produces the
identical refusal message under all five flags; `git diff` on tests/size
between the branch point and the lane is empty.

WHY IT WENT UNNOTICED: `make test-axes` is OPT-IN and NOT a stage of
battery_v4 (test → strict → san → lint → mech); the last full test-axes
sweep recorded in the journal predates fa9b6d4. A pre-existing red on an
opt-in suite stays invisible until a lane runs the suite for its own
axis — which is what happened.

DISPOSITION (manager, 2026-09-02): NOT opt5i's to fix (another row's
witness; not folded into an abi bump). A separate landing item after the
STEP 2 merge, on [ART-SIZE.2]'s row: EITHER an axis-documented-limit
entry for the nested-replication / state-cap / node-cap family on that
block OR the harness's axis-exclusion marking for a block whose `engine`
line is load-bearing — read run_axes.sh's documented-limits mechanism
and choose the one that keeps the block's purpose intact. Until then a
`make test-axes` run reports these five AXIS FAILs and nothing else on a
clean tree; a lane's OWN axis is judged on its own line. OPEN QUESTION
for Frank: whether test-axes joins the battery (it is ~70 min at
PROCS=nproc) or stays opt-in with this entry as its standing caveat.
