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

So `\1`..`\9` are unconditionally backreferences, and `\0` — which shares the
same diagnostic — can never be a backreference at all, since there is no group 0.

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

## K5 — OPEN, found 2026-08-10 (R5 spec critic) — a MISCOMPILE

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

---

## K6 — OPEN, found 2026-08-10 (R5 spec critic) — a MISCOMPILE

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

---

_Five open issues: K2 (cosmetic), K3 and K4 (over-rejection / over-acceptance in
the class-bracket doorway, one fix), K5 and K6 (base-tier MISCOMPILES, the class
the charter forbids). K5 and K6 are the two to fix first. Performance and
architecture debt lives in docs/plan.md; other engines' bugs in
docs/upstream_issues.md._
