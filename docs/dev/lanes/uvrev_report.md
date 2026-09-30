# uvrev: [UTF-VALID] design note revised against critic r2

Lane `uvrev` (opus, design only), 2026-09-30. Branch `lane/uvrev`, from
`lane/k73utf` (`bd1be543`). Nothing under `src/`, `cli/`, `lib/` or
`tests/` changed, and no `make` was run. Scratch was in `/tmp/claude-uvrev/`.
There were two light probe rounds on ubuntubudu (tailnet, libpcre2 10.46,
temp dir removed).

## Deliverable

`docs/design/utf_valid_design.md`, still PROPOSED. It was rewritten against
`docs/dev/reviews/2026-09-30-r2-utf-valid-contract.md`. §9 of the note maps
every finding F1-F8 to its change. The new evidence is in
`docs/design/utf_valid_evidence/`, and its CLAUDE.md is updated.

## What changed, per finding

- **F1**: the entry is now `<prefix>_valid_upto(s, n, startpos)`. It does
  the artifact's own LB step-back, so the caller passes the same `startpos`
  as the refused call and gets PCRE2's offset.
- **F2**: measured on 10.46, 37 patterns, with `INFO_MAXLOOKBEHIND` equal
  to the measured step-back on every one. LB = the max over lookbehind
  widths (per assertion, in characters), plus 1 for each of `\b`, `\B`,
  **`\A`**, `[[:<:]]`, `[[:>:]]`. The critic missed `\A`. `\Ab|c` on
  `\xffc` from 1 is -23, where a range starting at `startpos` would match.
  `^`, `(?m)^`, `$`, `\Z`, `\z`, `\G`, `\X`, `\R` and `\K` count 0. Nested
  reads do NOT accumulate (`(?<=(?<=..)a)b` = 2), and dead DEFINE bodies
  count. Because `A_BOL` merges `\A` with `^` and `(?<=C)` becomes `A_CTX`,
  the fact must be a parse-time running max written by the hooks, finalized
  by `pcrec_postresolve` for pending widths.
- **F3**: a dedicated raw continuation skip, not `back_step`. The pinned
  rows are listed.
- **F4**: the K50 guard runs first, then the check (PCRE2's order, measured
  on 10.46). Q10 is answered. The check is emitted at exactly the
  `pcrec_emit_startpos_guard` call sites, so the order is structural.
- **F5**: `extent` is written up as a real contract. It refuses iff an
  ill-formed sequence begins in `[f, e]`. I made `e` INCLUSIVE because the
  critic's `[f, e)` has an empty-match hole: `x*` on `\xff` would never
  check the byte in a find-all loop. With the inclusive `e`, a find-all loop
  run to completion refuses exactly when PCRE2's first call does, with
  PCRE2's offset, and the matches before the bad byte are delivered first.
  The note covers the scratch-caps cost (plus splitting the DFA entry body
  into a wrapper and an inner body), the VM/hybrid coverage (post-hoc
  wrapper, all engines), optimizer independence, and why `scan` breaks
  `make test-axes`. **Recommendation: build `whole`, and record `extent`
  unbuilt** behind a named D77 trigger. `whole`'s find-all escape
  (`valid_upto(s, n, 0)` once, then loop on the DEFAULT artifact) needs one
  artifact, not two.
- **F6**: contracts are option values (`off` | `whole` | later `extent`).
  No mechanism table exists, and the fused sink is not a mechanism for
  either contract. **For the manager**: plan.md's [UTF-VALID] row still says
  "rows of ONE first-match table". That framing should be dropped. The
  plan.md edit is yours; this lane did not touch plan.md.
- **F7**: `valid_upto` is in EVERY artifact (Q4). The identity claim is
  corrected. The name is encoding-neutral. Six subject-taking entries (the
  three `_in` forms are the rest), and the non-guard ones propagate. -9
  PROPAGATES at composed sites (Q11). It is the second contract axis,
  excluded from the identity sweep by name, with its own oracle arm. The
  harness/oracle file list is included. python3 strict decode is an
  independent offset oracle: its `UnicodeDecodeError.start` equals PCRE2's
  startchar on 13/13 sequence kinds.
- **F8**: re-measured with `utfcheck_bench2.c`, two runs, darwin,
  directional only. The sparse-accented rates are 0.12 / 0.34 / 0.90 ns/B at
  one `é` per 256 / 64 / 16 B. On per-call small subjects (8 B-4 KiB), the
  precheck costs 1.0x-1.4x a SCANNING `_search` call, and 10x-13x a call a
  pre-check answers. The LB step-back is unmeasurable (5.8 vs 6.0 ns at
  8 B). The ratios against sublinear calls ("17x", "12%", "3x-7x") are
  withdrawn. The fast path's 10-15% loss on dense non-ASCII is reported.
  The DFA-validator row is dropped.

## Validation

Design-only. Every cited PCRE2 row was measured on 10.46, and each 10.46 row
was re-run on 10.48 with identical results (`lb_10.46.txt`, `lb_10.48.txt`,
`cases2_10.46.txt`). The bench self-checks passed on both runs. There is no
make/test obligation, and nothing is owed.

## Open for Frank

The note's §8 has 11 questions, each with a recommendation. The ones that
decide the build are Q1 (PCRE2's range with the measured LB), Q2 (`whole`
now, `extent` recorded) and Q4 (`valid_upto` in every artifact).
