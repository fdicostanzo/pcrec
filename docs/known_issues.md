# Known issues — confirmed pcrec bugs (deferred fixes)

Confirmed correctness bugs in pcrec itself (distinct from docs/upstream_issues.md,
which tracks OTHER engines). Each has a minimal repro and a scheduled fix. Repros
live in tests/known_fail/ (NOT run by `make test`, so the suite stays honest about
what it certifies) and become passing regressions when fixed.

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

## K2 — OPEN, deferred to module 'backrefs' (found 2026-08-09, R4 critic pass)

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

**Not fixed now on purpose:** SR-2's acceptance bar is byte-identical output
across the corpus, and changing this string would break that proof for no
correctness gain. **Fix with:** module 'backrefs' (or SR-6), splitting `\0` from
`\1`..`\9`. No tests/known_fail/ repro: the current behaviour is a rejection,
not a wrong match, so there is no failing regression to ratchet.

---

## K3 — OPEN, found 2026-08-10 (SR-2 sabotage validation)

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

## K4 — OPEN, found 2026-08-10 (R5 critics, two independently)

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

## K7 — OPEN, found 2026-08-10 (FIX-1, while probing the 65535 boundary)

A large BOUNDED repeat exhausts memory and the process is SIGKILLed, instead of
reaching the DFA state cap that exists to prevent exactly this.

    $ build/pcrec -p rx -o /tmp/o.c 'a{0,65535}'
    Killed                                          # rc 137, empty stderr

Measured on a pinned build of `c38934c`, so it PREDATES FIX-1 and is not a
regression from it:

    a{0,65535}   a{,65535}   a{1,65535}   a{0,40000}   -> SIGKILL (rc 137)
    a{0,20000}                                         -> compiles, rc 0
    a{65535}                                           -> clean rc 1,
        "pattern too complex for the DFA engine (>32000 states)"

So the EXACT-count form degrades cleanly and the bounded-optional form does not:
`{0,n}` builds an optional chain that blows past the memory the cap was meant to
bound, before the cap is ever consulted. The threshold sits between 20000 and
40000 and was not narrowed further.

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
the class-bracket doorway, one fix — FIX-2), K7 (a large bounded repeat is
SIGKILLed rather than diagnosed; not a miscompile). **No open MISCOMPILE
remains** — K5 and K6 were fixed on 2026-08-10 by FIX-1. Performance and
architecture debt lives in docs/plan.md; other engines' bugs in
docs/upstream_issues.md._
