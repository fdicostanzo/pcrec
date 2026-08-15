# R22 — [M4.5d] D27-blinded capture author: delivery review (2026-08-15)

## Delivery

Cell author (m45d-capauthor, sonnet, allowlist: match_api_m4.md +
docs/testing.md + prebuilt binary; tests/fuzz REMOVED from the default
cell allowlist by the manager — its trap templates carry the K17/K18
alphabet the blinding exists to exclude): 85 m/ms cases + 145
group-expectation lines across three .rxt files (priority/iteration,
participation/zero-width, structure/anchors/misc), 72 distinct patterns,
every value derived from python3 `re` by two independent scripts
(generator + from-scratch reverifier), zero mismatches. Binary used for
ACCEPT/REJECT only, never to derive a value. gp used uniformly (reading
RX_NCAPS off gen.h would derive a fact from the implementation).

## Result against the real build

After normalizing inline comments (below): **230/230 checks pass, all
145 group lines LIVE against the VM (pending 0)** — a spec-blind
derivation agrees with the [M4.5b] implementation on every cell,
including transient-match-then-unset groups, empty-final-iteration
overwrites, and three population levels of one pattern. The D27
instrument's other outcome: not a K17-style miscompile this time, but
the strongest independent capture-correctness evidence the project has.

## Findings and dispositions

1. **Cross-iteration capture RETENTION unstated** (author finding 1):
   in ((a)|(b))* on "ab", the branch NOT taken in the final iteration
   retains its earlier-iteration value (g2=[0,1)) rather than reading
   unset. TRUE but stated NOWHERE in match_api_m4.md.
   **Three-way arbitration run this session (probe via
   tests/fuzz/pcre2_abi.h): python `re` and libpcre2 10.46 UNANIMOUS;
   pcrec agrees (cases pass).** Disposition: contract-text gap —
   annotated at match_api_m4.md §2.2 (this review), full wording pass
   owed at M4.7's post-run review. NOT an upstream_issues row (no
   disagreement exists).
2. **Empty-final-iteration overwrite** (author finding 2): (a*)*/(a?)*
   on "aaa" report g1=(3,3), an empty final iteration overwriting a
   non-empty earlier one. Same arbitration: unanimous, pcrec agrees.
   Same disposition as (1); the author's caution about
   cross-implementation history is noted but the three engines we
   answer to agree.
3. **Inline comments** (found at landing): the author wrote `m ... # why`
   inline; testing.md grants comment status only to LINES STARTING with
   `#` and the parser hard-errors on the rest (correct per its own
   spec). All 230 initially failed on parse. Disposition: comments
   hoisted to standalone lines by the manager (content preserved);
   testing.md gains an explicit "no inline comments" sentence.
4. **Cell hygiene** (author-reported): cellwork/ contained a leftover
   probe.h from the manager's own cell-verification (cleanup glob
   `probe.c*` missed the paired header). Exposure: an ABI header sample
   for a(b|c)+d, RX_NCAPS=2 — nothing beyond the allowlisted contract
   doc. No values derived from it. Lesson: verify a cell is pristine
   AFTER any manager probing; probe outside cellwork/.
5. **Default cell allowlist is stale** for post-M4.5 authors: contains
   tests/fuzz/probes/spec_mod0, no docs. This cell was hand-curated;
   scripts/mk_d27_cell.sh's list should be revisited before the next
   D27 lane (left as a note, not changed mid-session).

## Population effect

corpus 1449 -> 1679 (+85 m/ms + 145 activated g lines... counted as
230 checks by the harness; see the landing commit for the exact
accounting line).
