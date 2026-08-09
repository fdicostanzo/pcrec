# Known issues — confirmed pcrec bugs (deferred fixes)

Confirmed correctness bugs in pcrec itself (distinct from docs/upstream_issues.md,
which tracks OTHER engines). Each has a minimal repro and a scheduled fix. Repros
live in tests/known_fail/ (NOT run by `make test`, so the suite stays honest about
what it certifies) and become passing regressions when fixed.

Status: `deferred` (scheduled) | `fixing` | `fixed` (moved to a passing corpus).

---

## K1 — zero-width `$` loses priority to a consuming alternative in a repeated group

- **Status**: deferred → fix with the assertions module (M6), or a dedicated
  empty-width-iteration correctness pass, whichever lands first.
- **Minimal repro**: pattern `(?:$|[^abc]){2,}` on subject `XY$\n` (4 bytes,
  trailing newline) → pcrec: match [0,4); PCRE2 10.46 and python `re`: match
  [0,3). At the final `\n` (an EOL position) the group's first/highest-priority
  `$` alternative matches zero-width and must win; pcrec instead takes the
  lower-priority `[^abc]` consuming the `\n`.
- **Trigger shape (precise)**: a quantified group `(?:$|C){m,}` (or `+`/`*`)
  where alternative `C` can match the subject's final newline, applied to a
  subject ending in `\n`. If `C` cannot match `\n` (e.g. `.`), both engines
  agree — so `(?:$|.){2,}` on `bb\n` is NOT affected.
- **Root cause**: `src/ir/dfa.c` closure. `(?:...){m,}` builds an ε-cycle
  through the star-split; the zero-width `$` iteration loops back to the
  already-`seen` star-split and is cut off before reaching the group-exit
  ACCEPT. So the closure never learns the `$` path accepts (higher priority),
  and the lower-priority consuming thread wrongly survives pruning. This is the
  classic empty-iteration-in-repeat problem (PCRE allows one empty iteration to
  terminate the loop); pcrec's priority-DFA lacks empty-loop handling.
- **Scope**: pre-existing (present since the M1 attempt engine; NOT a
  regression from M2). Confined to the ENG_ATTEMPT engine (mid-pattern `$`);
  assertion-free patterns are unaffected. Sits squarely in two areas already
  documented as deferred: empty-capable groups under quantifiers (see
  tests/base generation restrictions) and full mid-pattern `$` generality (M6).
- **Found**: 2026-08-09 by the M2.5 differential fuzzer (seed 3), minimized to
  the case above.
- **Detection**: the fuzzer excludes this shape from generation (documented in
  tests/fuzz/fuzz.py) so it doesn't drown newly-discovered divergences; remove
  that exclusion when K1 is fixed.

---

Maintenance: add an entry when a confirmed pcrec bug is deferred rather than
fixed immediately; move it to a passing regression and delete the entry (or
mark `fixed`) once resolved. Cross-reference the scheduling milestone in
docs/plan.md.
