# tests/assertions — module `assertions` ([M6.2])

The module's own corpus and its two non-`.rxt` checks. **WAVE A only so far**:
`\A`, `\Z` and `\z` are built; `\b` `\B` `(?m)` `\G` `\K` are recognised,
attributed and refused, and land in later waves
(`docs/design/assertions_design.md` §10).

## THE ORACLE RULE IS DIFFERENT HERE, and it is the first thing to know

CLAUDE.md's project-wide rule is that expectations are oracle-verified with
python3 `re`. **For `\Z` that rule produces WRONG expectations, silently.**
MEASURED, both oracles, by the [M6.1] design lane and reproduced by this one:

| pattern | subject | libpcre2 10.46 | python 3.14 |
|---|---|---|---|
| `b\Z`  | `"ab\n"`  | `(1, 2)` | `None` — no match at all |
| `a*\Z` | `"aaa\n"` | `(0, 3)` | `(4, 4)` — a different SPAN |

**python's `\Z` IS PCRE2's `\z`.** python has no single escape for PCRE2's
`\Z`; the only spelling is `(?=\n?\Z)`, which needs module `lookaround`. Both
divergences run in the dangerous direction — python reports no match, or a
shorter one, exactly where PCRE2 matches — so a cell written from python would
encode `\z` and this suite would go green on a `\Z`-compiled-as-`\z`
miscompile.

**Every block whose pattern contains `\Z` therefore carries `# pcre2-only`**
(which makes `tests/harness/verify_rxt.py` skip it) and is verified against
libpcre2 by `verify_pcre2.py` instead. The rule is applied to every `\Z` block
whether or not this directory's own subject set happens to expose the
divergence on it: a subject added later must not silently start lying. `\A`
and `\z` blocks are python-verifiable and are deliberately NOT marked — python
3.14's `\z` has PCRE2's meaning and its `\A` has PCRE2's absolute semantics
under `pos`, checked cell for cell at 0 divergences.

Recorded as `docs/dev/upstream_issues.md` U11, per the standing rule that
every oracle exclusion has an entry there.

## Files

- **absolute.rxt** — `\A`, `\Z`, `\z`: the three-way position distinction
  (`b\Z` on `"ab\n"` matches at `(1,2)`, `b\z` does not, `b$` agrees with
  `\Z`), the bare assertions at every position of fifteen subject shapes,
  `startpos` behaviour (`\A` is absolute offset 0 — it is A_BOL, the node `^`
  builds — so it is not satisfied at a nonzero `startpos`), anchored literals,
  quantifier interactions, alternation and grouping, and the syntax refusals
  with the module ENABLED (a bare quantified anchor is PCRE2 error 109 and a
  GROUPED one compiles; both halves are here, because a rule tested in one
  direction is not tested). Every expectation produced by libpcre2 through
  `tests/fuzz/pcre2_oracle`, never written by hand.
- **gate.rxt** — the D47.5 possessification gate from the assertions side
  (`assertions_design.md` §8; D62). The `$`-follow shapes `eng_brep_design.md`
  §2.5 measures safe, the same shapes with `\z` and with `\Z` in the follow,
  and the FAILING DIRECTION (`\A`/`^` in the follow, which must make the
  analysis decline). It cannot see whether a quantifier was possessified —
  that is what `run_assertions_tests.sh`'s STRATS check is for — and it cannot
  see the scoped-`(?m)` miscompile at all, because `(?m)` does not compile
  yet. **D62's controls 1 and 2 (the widened scoped test cells, the permanent
  flag-reader sabotage) belong to WAVE C**, where the flag can actually be
  true and those rows can actually go red; writing them now would be a check
  with no failing direction.
- **verify_pcre2.py** — the libpcre2 oracle for this directory's corpus.
  IMPORTS `tests/harness/verify_rxt.py`'s `.rxt` parser rather than copying it
  (one implementation of the file format) and builds
  `tests/fuzz/pcre2_oracle.c` rather than carrying a third ctypes binding (one
  libpcre2 access path, the one PC-3 and the fuzzer already share). SKIPS
  LOUDLY when libpcre2 is absent — exit 0 with a skip line, never a silent
  pass.
- **run_assertions_tests.sh** — the three things a `.rxt` file structurally
  cannot check, run by `make test-assertions`:
  1. the libpcre2 re-verification above;
  2. the CONTROL under `tests/reject/`'s two-answer pins — the three
     constructs this wave builds must COMPILE with the gate open. The refusal
     TEXTS live in tests/reject/ (the house home for "which module does a
     diagnostic name", both gate states adjacent in its `== assertions ==`
     section); what cannot live there is the fact that stops the
     "is not implemented yet" rows measuring an EMPTY module rather than a
     partly-landed one;
  3. the D47.5 exemption ACTUALLY FIRING, read off the artifact's own
     `<PREFIX>_VM_STRATS` stamp in both directions — `\z`/`\Z`/`$` in the
     follow must possessify, `\A`/`^` must not. A possessified quantifier and
     a backtracking one match identically by construction, so `gate.rxt` stays
     green either way; the stamp is the only thing that can see it.

## What guards what, and why none of it substitutes for another

Four instruments touch this module and they see different things:

| instrument | sees |
|---|---|
| `tests/harness/run.sh` over `*.rxt` | what pcrec's emitted matcher ANSWERS |
| `verify_rxt.py` | whether the non-`\Z` expectations describe python `re` |
| `verify_pcre2.py` | whether ALL of them describe libpcre2 — the only check that can validate a `\Z` cell |
| `run_assertions_tests.sh` | the gate's two answers, and whether the possessification exemption fired |

and one more lives outside this directory entirely:
`tests/codegen/run_endvar_identity.sh`, the byte-identity gate for the claim
that `\z`'s third closure view costs a `\z`-free pattern nothing. Its failing
direction is sabotage S69 — the design's own refuted first draft, restored.

## Maintenance

Update this file when files are added or removed. When a later wave lands a
construct, the pair to move together is: `tests/reject/`'s `reject_gated
assertions` row for it (delete — it is built now) and this directory's own
cells (add). Leaving the first behind turns a true statement into a false one
the day the producer lands, which is exactly the `(?J)` wording history
recorded in `src/parse/mod_modifiers.c`.
