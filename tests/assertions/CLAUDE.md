# tests/assertions — module `assertions` ([M6.2])

The module's own corpus and its two non-`.rxt` checks. **WAVES A AND B so
far**: `\A`, `\Z`, `\z`, `\b` and `\B` are built; `(?m)` `\G` `\K` are
recognised, attributed and refused, and land in later waves
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
- **wordb.rxt** — [M6.2] WAVE B: `\b` and `\B`. **The `ms`/`ns` cells are what
  makes this file different from `absolute.rxt`, and they are not decoration.**
  `\b`/`\B` are the module's first CONTEXT assertions — their truth at a
  position depends on the bytes on EITHER SIDE of it — while
  `<prefix>_search(s, n, startpos, caps)` searches `s[startpos, n)` and
  `s[startpos-1]` sits OUTSIDE that window and INSIDE the subject. A
  `startpos > 0` cell is therefore the only thing in this corpus that can see
  mechanism 4 (`assertions_design.md` §3.8) at all, and 5 of that section's 10
  measured cells differ between searching from `startpos` and searching the
  SLICE — in BOTH directions, so no conservative reading exists.
  **The LEADING `\B` cells at `startpos > 0` carry §3.8.3.1's reverse
  TERMINATION defect, which a leading-`\b` population structurally cannot
  see**: `\b`'s blind assumption (no left context means non-word) coincides
  with its own truth condition, so a `\b`-only suite reports clean against an
  implementation that throws matches away. The named cell is `\Bfoo` on
  `"xfoo"` at startpos 1 → `(1,4)`, and sabotage S74 is its failing direction.
  Also here: both-ended and interior forms, the empty-match family (`\b`,
  `\bx*` — whose start state ACCEPTS, which is what §3.6.1's widened
  `start_acc` is about), composition with `$`/`\z`/`\Z` (§3.6.2's two axes),
  and an ENG_ATTEMPT block, since a `^` routes the pattern to the
  computed-goto engine where §3.6's table and §3.8's seed take a different
  emitted shape. Every expectation libpcre2-produced. **THREE ANCHORED CELLS
  ARE DELIBERATELY ABSENT and the file's own header says which and why** —
  `^\Bfoo`, `^\Bo`, `^a\bb` are never-matching patterns whose emitted C trips
  a PRE-EXISTING `-Werror=maybe-uninitialized` in the `<prefix>_match`
  wrapper (base-tier reproducer `^a^b`, measured on the pre-wave compiler);
  live equivalents stand in their place.
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
  2. the CONTROL under `tests/reject/`'s two-answer pins — the constructs the
     module has BUILT must COMPILE with the gate open (wave B added `\b`/`\B`
     here as it deleted their rows over there, in the same change; both a
     LEADING and a TRAILING spelling of each, because the two reach different
     machinery — the forward seed and the reverse one — and a control that
     only ever compiled the leading form would not notice the reverse half
     failing to build). The refusal
     TEXTS live in tests/reject/ (the house home for "which module does a
     diagnostic name", both gate states adjacent in its `== assertions ==`
     section); what cannot live there is the fact that stops the
     "is not implemented yet" rows measuring an EMPTY module rather than a
     partly-landed one;
  3. the D47.5 exemption ACTUALLY FIRING, read off the artifact's own
     `<PREFIX>_VM_STRATS` stamp in both directions — `\z`/`\Z`/`$` in the
     follow must possessify, `\A`/`^`/`\b`/`\B` must not. A possessified
     quantifier and a backtracking one match identically by construction, so
     `gate.rxt` stays green either way; the stamp is the only thing that can
     see it. Wave B's own rows are the last two: the exemption rests on UPWARD
     CLOSURE and a word boundary is closed in NEITHER direction (`\w{0,4}\b`
     on "abcd" is a boundary at the maximal exit 4 and not at the retreat 3),
     so `\b` must take `^`'s arm and not `$`'s;
  4. [M6.2 wave B] that the COMPOSED STATE BUDGET (§3.5.1) REFUSES rather
     than miscompiling, on BOTH caps — `PCREC_MAX_DFA_STATES_TABLE` for
     ENG_UNANCH and the 3.2x tighter `PCREC_MAX_DFA_STATES_GOTO` for
     ENG_ATTEMPT, which §3.4.1 discloses the design's whole corpus
     measurement was blind to. The check pins the PROPERTY (states-cap
     diagnostic, no output file written) and not the boundary's location: the
     located boundary is a MEASUREMENT and lives in
     `docs/design/assertions_measurements/out/wordctx_budget.txt`. Its
     control is the same family an order of magnitude smaller, which must
     compile.

## What guards what, and why none of it substitutes for another

Four instruments touch this module and they see different things:

| instrument | sees |
|---|---|
| `tests/harness/run.sh` over `*.rxt` | what pcrec's emitted matcher ANSWERS |
| `verify_rxt.py` | whether the non-`\Z` expectations describe python `re` |
| `verify_pcre2.py` | whether ALL of them describe libpcre2 — the only check that can validate a `\Z` cell |
| `run_assertions_tests.sh` | the gate's two answers, and whether the possessification exemption fired |

and three more live outside this directory entirely.
`tests/codegen/run_endvar_identity.sh` is the byte-identity gate for the claim
that `\z`'s third closure view costs a `\z`-free pattern nothing; its failing
direction is sabotage S69 — the design's own refuted first draft, restored.
`tests/codegen/run_wordctx_identity.sh` is wave B's, for the much larger claim
that the alphabet refinement, the second closure, the class-indexed accept and
the third start state cost a `\b`-free pattern nothing (sabotage S71). And
`tests/codegen/run_codegen_tests.sh`'s `[M6.2-WORDB]` block carries three
rules no correctness test can see — no accept table indexed at `pos == n`
(§3.6.2, sabotage S73), no `sfound` recorded blind at the reverse boundary by
ANY writer including the skip's (§3.8.3.1, sabotage S72), and exactly one
word-set spelling per artifact (§7.2 item 3).

## Maintenance

Update this file when files are added or removed. When a later wave lands a
construct, the pair to move together is: `tests/reject/`'s `reject_gated
assertions` row for it (delete — it is built now) and this directory's own
cells (add). Leaving the first behind turns a true statement into a false one
the day the producer lands, which is exactly the `(?J)` wording history
recorded in `src/parse/mod_modifiers.c`.
