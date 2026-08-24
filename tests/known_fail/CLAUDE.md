# tests/known_fail — deferred-bug regressions (expected to fail)

`.rxt` files here assert the **correct** behaviour for bugs that are CONFIRMED
but deliberately deferred rather than fixed now; each one has an entry in
`docs/dev/known_issues.md` with a minimal repro and the milestone that owns it.
`tests/harness/run.sh` excludes this directory from its default discovery, so
`make test` stays green and honest — a known bug does not get to look fixed,
and it does not get to break the build either.

## Files

- **d27_nested_min_boundary.rxt** — K23 (2026-08-16): `(a{10,20}){10,50}`
  on the exact-minimum 100-byte subject returns `RX_ERR_STEPS` where the
  oracle answers span (0,100)/group (90,100) instantly. Asserts the correct
  behaviour per this directory's contract; owning milestone [M4.6]. Found by
  the D27 blinded quantifier corpus (its live siblings: `tests/base/d27_*.rxt`).
- **(previously empty)** — from 2026-08-15 until K23, no confirmed bug was deferred with a
  repro on file, which the ratchet treats as a legitimate good state (it
  reports "nothing to ratchet" and exits 0). The last resident was
  `k18_empty_exit_through_seen_eps.rxt`, which moved to `tests/base/` when K18
  was fixed; it is worth reading as the worked example of this directory's
  contract, because the ratchet is what forced the move and the
  `known_issues.md` close to land in the SAME commit. Three sibling files
  joined it there (arm-order, `{0,2}` split shapes, deep nesting) — a deferred
  bug's repro is written from the bug as FOUND, and the fix lane owes the axes
  that repro's own alphabet could not reach
- **run_known_fail.sh** — the "fixed by accident" ratchet (R2-PR8). Runs each
  `.rxt` here and INVERTS the verdict: still-failing is expected, and a file
  that has started PASSING is flagged and fails the script. Part of
  `make test`. An empty directory exits 0.

## Conventions

Adding a deferred bug: write the `.rxt` asserting the behaviour PCRE actually
has (oracle-verified, same as any other corpus file), put it here, and add the
`docs/dev/known_issues.md` entry naming the owning milestone. Never weaken an
expectation to make a bug look fixed.

Removing one: when the ratchet flags a file, MOVE it into the matching
`tests/<module>/` directory so the fix gains a live regression, close the
`known_issues.md` entry, and journal it — a fix nobody intended is worth
understanding, because its scope may be accidental too.

Maintenance: update this file when the directory's contents or contract change.

## `dd14_bc_open.rxt` — [DD-14] wave B+C's three OPEN cells (2026-08-24)

Three cells, each because a **RULING is owed** rather than a bug is open —
`u9_atomic.rxt`'s shape, and for the reason this directory's own header gives:
excluded from `make test` so the suite stays honest, RUN by the ratchet so a
cell that starts passing FIRES. Their former positions in
`tests/recursion/`'s generated corpus carry comment stanzas pointing here,
written by `gen_corpus.py`'s `parked=` argument so the two cannot drift.

**CELL 1 — a left recursion whose language is EMPTY: give up, or answer?**
`^(a?(?1)b)$` is `X = a? X b`, which has no base case, so no subject can
match. libpcre2 answers `rc -52` (its own nested-recursion guard); pcrec
answers NOMATCH, in constant time; the corpus expects `gu frames`. **Both are
refusals of the same subject**, and design §5.9 scores exactly that pair
"agreed in kind". pcrec answers at all because §4.4b's `minw` Kleene fixpoint
gives the callee INFINITY and §12 P-12 RULES the MRL prune read that as "no
position can match".

**AND THE CLASS ANSWERS TWO WAYS, which is what needs ruling.** The two
SIBLING cells in `leftrec.rxt` — `^((?1)a)$` and the indirect two-node cycle —
are the same empty-language class and DO give up, because neither carries a
quantifier for an MRL bound to hang on. So which answer a left recursion gets
depends on whether the pattern happens to contain a quantifier, and that is
not a fact about recursion.

**CELLS 2 and 3 — a call inside a LOOKBEHIND, over-rejected.** pcrec refuses
both where 10.46 accepts and matches: a tier-2 OVER-REJECTION, never a
miscompile. **The cause is TIMING, not the width analysis.** `pcrec_maxw`'s
`A_CALL` arm answers `PCREC_W_UNBOUNDED`, which §3.4(d) makes EXACT for a
recursive callee (10.46 refuses that itself, err 125) and a sound
over-estimate for every other — and tightening it for an ACYCLIC callee needs
the call graph, while `la_widths` (src/parse/mod_lookaround.c) runs INSIDE THE
PARSE HOOK, where it must, because that is the only place with a pattern
OFFSET to refuse at. The graph does not exist until every call is resolved at
end of parse and every rewriting pass has run. **So no `A_CALL` arm of
`pcrec_maxw` can make these compile**; design §3.4(d) says the width analysis
descends into the callee and does not say when it runs.

**The fix a ruling would order** is a DEFERRED WIDTH RE-CHECK: the parse hook
records the lookbehind (and its offset) instead of refusing when its body
carries a call, and a pass after `pcrec_callgraph_build` recomputes the widths
and refuses then. That is a change to a landed module's core plus a new
`u.look` field for the diagnostic's offset, which wave B+C did not take on.
