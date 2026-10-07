# cgtri — triage of the two `make test-codegen` reds on main (cda5a360)

Lane cgtri, opus, 2026-10-07. Branch `lane/cgtri` from `cda5a360`.
Trigger: the manager's `make test-codegen` on main
(`worktrees/.mgr-scratch/cg.log`) failed two checks. Both are exposed by
`tests/possessify/composition_d27.rxt` (D27-blinded, merged at `5f91ab71`
without a test-codegen run). **Neither is a compiler defect. No K-entry filed,
no `src/` change, no abi event.** Both are check-side: one stale manifest and
one check whose predicate was broader than the precondition it claims to
restate.

## (1) `[agreement] the empty-engine bucket differs from its named manifest`

- **Check:** `tests/codegen/run_dfa_stamps.sh`, `EMPTY_MANIFEST` (an exact
  named list of the patterns whose DFA search is one `return 0`).
- **Cause:** 17 new corpus patterns, all from `composition_d27.rxt`, land
  in the bucket: `(?:a{1,2}\b){2}` `-+\Bb` `-{1,3}?\Ba` `.{0,2}?(?!a)a`
  `[a-]{1,3}(?=\w)-` `[a-c]+\bB` `[a-c]{0,}?(?=a)\W` `[ab]?(?!\w)\w`
  `\W+(?<!\W)` `\W+(?<=\w)` `\b(?:\w+\b)+\B` `\d+(?<=\W)\b` `\s+(?<=a)b`
  `\s{2}\B\w` `\w+(?<=\W)` `\w{1,3}(?=a)\W` `a{1,3}?(?=\w)\W`. Nothing was
  missing.
- **Class:** STALE MANIFEST, not a misclassification. I re-derived each one
  rather than copying the `only:` list. Each is a contradiction: either a
  `\b`/`\B` between two bytes whose word-ness refutes it, or a one-character
  lookaround whose class is disjoint from (or the complement of) the
  adjacent consumed byte. These are U2 context-node shapes or the existing
  `a\bb` shape, sitting behind a quantifier. As an independent control,
  every one of the 17 blocks in the corpus file has only `n`/`ns` cells
  recorded from libpcre2 10.46: 11 cells each and zero `m`. A script parsed
  this out of the `.rxt`, and the pcrec emitter was not involved.
- **Fix:** I added the 17 to `EMPTY_MANIFEST` with a comment that names
  their source and the two emptiness families. The manifest goes from 50 to
  67 entries.

## (2) `[scan-edge-census] '(?:\b(?1)|x)(a+)': ... precondition (8) did not fire`

- **Check:** `tests/codegen/run_scan_edge_census.sh` §4, P3. It covers
  forward machines that have an offset-set or run-pinned (RESEEDING)
  prefilter and a seed table, and asserts "carries ANY scan edge" == 0.
- **What precondition (8) actually is:** `src/opt/scanedge.c` ~l.409, as
  narrowed at [OPT-EDGE] STEP 1.1. It is `prefilter_reseeds && seedtgt[s]`,
  so it refuses a head **only when the reseed can install it**, meaning the
  head is a seed-family value other than `s0`. The emitter's read-back
  `dfa_form_derive` (`src/gen/emit_dfa.c` ~l.8841) checks exactly that.
  P3's "any edge" is STEP 1's un-narrowed rule. It held only while P2's
  edge-carrying population was empty, which the census header itself
  recorded ("the narrowed (8) has an EMPTY population").
- **The artifact:** `RX_DFA_PREFILTER "offset-set-bounded"`. The seed table
  `{0, 4, 4, 4}` installs cells 0 (s0) and 4. The one forward edge is on
  cell 12, the accepting `aa` state with a self-loop on `a`. Cell 12 is not
  a seed value, so (8) correctly does not fire, and the emitter's own
  read-back agrees (the compile succeeds). The reseed runs only when
  `forward_state == 0`, so it can never overwrite cell 12 either.
- **Is the artifact wrong?** No. For answers I took the corpus block (8 m/n
  plus ms/ns cells), which passes on main. I also ran an extra differential:
  1,500 random subjects over `{a,x,-,b,1,' '}`, lengths 0..9, comparing a
  `--emit-main` build against libpcre2 **10.46** (version string verified,
  ctypes on ubuntubudu, light probe at 15:04 EDT). The result was
  **1,500/1,500 identical**, with 296 matches.
- **Cause attribution:** the call `(?1)` plus `\b` gives a reseeding seeded
  machine, and `a+` gives a self-loop edge. This is a new population that
  the corpus never had before. It is not caused by K93, R4c/M1b or C2, so no
  bisect was needed: the check is wrong on its own definition.
- **Class:** CHECK DEFECT (over-broad predicate). No K-entry.
- **Fix:** I narrowed P3 to (8)'s own question. A new helper,
  `seeded_heads_on`, counts edge heads (the `if (<m>_state == K` under an
  `[OPT-5] SCAN EDGE` marker) that are values of `rx_<m>_seed_state[]`
  other than the start cell (the entry seed's `: K;` fallback). Machines
  with an edge on an unseedable head are now counted and named as a new
  FINDING, **P2e**, so the population the narrowing excludes stays visible
  (K35). The header comment and `tests/codegen/CLAUDE.md` say so.
- **Failing direction of the helper:** validated by planting into the
  witness artifact.
  - Head cell put into the seed table: 1.
  - Edge head moved onto seed value 4: 1.
  - Edge head moved onto the start cell 0: 0 (exempt, as in (8)).
  - Clean: 0.

## Validation

- `make strict`: clean (`strict: whole tree compiles clean with -Werror
  -Wshadow`).
- `make test-codegen` on the lane tip: see the handback.
  Log: `worktrees/cgtri-scratch/cg.log`, completion line `EXIT <rc>`.

## Files

- `tests/codegen/run_dfa_stamps.sh`: manifest +17, with a comment.
- `tests/codegen/run_scan_edge_census.sh`: `seeded_heads_on`, narrowed P3,
  P2e finding, and the §4 comment.
- `tests/codegen/CLAUDE.md`: a census note.
