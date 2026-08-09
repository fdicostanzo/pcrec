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

_One open cosmetic issue (K2). Performance and architecture debt lives in
docs/plan.md; other engines' bugs in docs/upstream_issues.md._
