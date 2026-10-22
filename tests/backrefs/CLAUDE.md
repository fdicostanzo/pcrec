# tests/backrefs — module `backrefs` ([M6.5.2])

Every backreference spelling (`\1`..`\N`, `\g` in its brace/bare forms, `\k` in
its three, `(?P=name)`), PCRE2's octal disambiguation at the atom position, and
`(?J)`/DUPNAMES with the resolution rule that makes it mean anything. Design:
`docs/design/backrefs_design.md`, panel-approved at R32
(`docs/dev/reviews/2026-08-22-r32-backrefs-design.md`).

**A backreference is not a class-membership test, and every file here follows
from that.** Everything else pcrec compiles is a 256-bit bitmap or a position
predicate — which is why caselessness folds away at parse time (D23) and why
the DFA can carry every other construct. A backreference compares SUBJECT TEXT
against SUBJECT TEXT at a pair of positions the backtracking state holds at
that instant. So it is VM-only, it cannot have a prefilter, its caseless form
is the encoding seam's second residual entry, and the thing most likely to be
wrong about an implementation is WHICH pair of positions it reads.

## Files

- **numeric.rxt** — `\1`..`\9` and above: the UNSET rule (PCRE2 FAILS an unset reference, it does not match empty — `^(a)?\1$` on `""` is no match), the EMPTY rule (a ...
- **octal.rxt** — §5's four ordered questions, each with a DISCRIMINATOR subject so "it compiled" is never mistaken for "it is a backreference". The ASYMMETRY is the ...
- **octal_class.rxt** — the CLASS position, run with the module ENABLED. Every cell is a MUST-NOT-CHANGE pin: inside a class a backreference is impossible, so `\0`..`\7` ...
- **selfref.rxt** — self-references, forward references, **and the RE-ENTRY class, which is this file's reason for existing.** `(a|b\1)+` on "ab" is libpcre2 (0,1) with ...
- **nested.rxt** — the trail as behaviour.
- **spellings.rxt** — every spelling, and the `\g` doorway's OTHER construct.
- **caseless.rxt** — WHERE the `(?i)` is read and WHAT the compare folds.
- **caseless_ucp.rxt** ([K94]) — the caseless compare under `--ucp` in the byte encoding: Latin-1 pairs fold (`(\xe9)\1` on `\xe9\xc9`), `\xb5 \xdf \xff` and `\xd7/\xf7` ...
- **dupnames.rxt** — `(?J)`'s scoping rule (checked AT EACH DECLARATION against the scoped state, which four separating cells establish) and §8.3's resolution rule, plus ...
- **gated.rxt** — what each partial enable buys, and the class column that does not move.
- **run_backref_diff.sh** — ten sections, five EXACT population guards.
- **run_dupnames_diff.sh** — §8.3 swept rather than sampled, and checked THREE ways: pcrec against libpcre2, an INDEPENDENTLY WRITTEN model of the rule against libpcre2, ...
- **bref_batch.c / bref_entries.c** — the batch drivers, one process per (pattern, arm) rather than per cell.
- **bref_oracle.py** — the libpcre2 side in one process, with the group list PADDED to the requested count (libpcre2 truncates trailing unset pairs, so without padding the ...
- **fold_agreement_check.c** — the mechanism that discharges R32 E8. pcrec's ASCII fold exists TWICE and cannot be made to exist once (a parse-time class widener; ...
- **fold_agreement_ucp_check.c** ([K94]) — the `--ucp` BYTE half, run as `run_backref_diff.sh` §9c: the shipped `$_span_match_caseless` of an artifact compiled `--ucp` ...
- **fold_agreement_utf8_check.c** — the same obligation for the `utf8` encoding ([M5.0] stage 4, `utf8_design.md` §4.6), run as `run_backref_diff.sh` §9b.

## THE CORPUS IS GENERATED, and that is a property rather than a convenience

`gen_corpus.py` wrote every expectation in every `.rxt` here by driving the
cell through libpcre2 10.46 BEFORE it was written, and drove python3 `re` over
the same cells in the same pass. A block carries `# pcre2-only` exactly where
python diverged or could not compile the pattern — **computed, never
declared** — with the first divergence and the cell count recorded above the
marking.

That matters more here than anywhere else in the tree, because this module has
the largest oracle divergence pcrec has met. python `re` refuses EVERY
self-reference and EVERY forward reference at compile time, has no `\g`, no
`\k` and no `(?J)` at all, rejects the `(?<n>...)` declaring spelling, and
refuses `(?i)` anywhere but the pattern start — which is exactly where the two
cells that decide WHERE the caseless flag is read live. R32 C3 found the first
test plan marking two of these files python-verifiable IN THE DIRECTION THAT
LOSES THE ORACLE; computing the marking removes the species.

Re-run it after changing a cell list:

    python3 tests/backrefs/gen_corpus.py     # rewrites the .rxt files in place

Current census, from that run: **255 cells, 55 blocks python-verified, 65
`# pcre2-only`, 31 `perr`.** `python3 tests/harness/verify_rxt.py
tests/backrefs/` passes on the python-verifiable half; `bash
tests/harness/run.sh tests/backrefs/*.rxt` passes 681/681 over this
directory's own cells (2026-10-08, s670cell; the 455/455 and 234/234 this
sentence carried predate caseless_ucp.rxt and the S670 cells).

(Rest of this section: see the history file.)

## What is deliberately NOT here

- **`nocaps.rxt`.** The `.rxt` format has no `--no-captures` directive, and the
  facts that axis needs are pcrec-only reflection assertions (`RX_NCAPS`
  is 1) rather than match spans. `run_backref_diff.sh` §4 carries it, and
  says so.
- **`\g<...>` / `\g'...'` as accept cells.** They are SUBROUTINE CALLS, module
  `recursion`, and they appear here only as `perr` blocks recording what
  libpcre2 answers and why pcrec refuses.
- **A `PCREC_MATCH_UNSET_BACKREF` arm.** Measured and declined (§3.3): 2 of the
  8 unset cells flip under the bit, and implementing it means a second emitted
  shape for one construct selected by an option pcrec does not have.

- Also (one-line entries for these are in the history file): `d27`.

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__backrefs.md`.
