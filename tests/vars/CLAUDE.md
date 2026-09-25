# tests/vars/ — module `vars`' corpus and its own oracle

**[VAR] M10, 2026-09-23.** `${name}` in a pattern, whose bytes the caller
supplies per call. The contract is `docs/spec/vars.md`; the design is
`docs/design/variables_common.md` and `variables_pattern.md`.

## Files

- `basic.rxt` — a variable matches its own bytes. The SET state, the value
  that would be pattern syntax if anything parsed it (it never is —
  `variables_common.md` §4.2's literal rule is the injection boundary), the
  same name twice, a variable under a quantifier and inside an alternation,
  an unknown caller name ignored, a name bound twice (first wins), and
  (`gen_corpus_plan.md` §2's OWED closure, lane varfollow 2026-09-25) the
  LOOKAROUND pair: a variable inside a lookbehind body is REFUSED (its width
  is unbounded, the same rule that refuses a backreference-bearing
  lookbehind), and a variable inside a lookahead body is an ordinary match.
- `unset.rxt` — the UNSET/EMPTY/SET value model and the five operators, now
  EXHAUSTIVE over the full 18-cell state×operator grid (closed by lane
  varfollow, 2026-09-25 — `gen_corpus_plan.md` §2 has the count and the
  correction to which two cells were actually missing). **The cells that
  separate `-` from `:-` and `+` from `:+` are the reason the format has to
  be able to spell EMPTY at all**: bound to `""`, the bare operator does not
  fire and the colon one does, and a format that could not write both could
  not test the distinction they exist for.
- `caseless.rxt` — the caseless compare under both encodings, including the
  KELVIN SIGN in both directions (one value byte against three subject
  bytes, and the reverse), the 1:1 negative control, and the ill-formed-value
  refusals. Its ill-formed-default cell carries a RAW 0xFF byte in its
  `pattern` line; see the comment at that cell for why not `pattern-esc`.
- `verify_vars.py` — **the oracle, and its NAME is the mechanism.**
  `tests/harness/verify_rxt.py`'s `declares_own_oracle` treats a directory
  holding a `verify_*.py` as having one and skips its cells with a COUNTED
  `own-oracle` skip. That is exactly right here because NEITHER standing
  oracle can express a caller variable: python `re` has no such feature, and
  libpcre2 reads `${v}` as an assertion followed by a literal `{`, a spelling
  no subject can match. Scoring these cells against either would report a
  divergence on every one and mean nothing.
- `run_vars_tests.sh` — the section (`make test-vars`), two arms: the corpus
  and the oracle. In `TEST_SECTIONS`, in `tests/lib/san_scripts.txt`, and its
  own `vars` arm in `tests/mech/run_sabotage_matrix.sh`.
- `gen_corpus_plan.md` — §2.5's K35 population census, stated BEFORE the
  fact: the six axes, what gets exhaustive coverage and what gets sampled,
  what is deliberately not an axis, why the generator is declined under D77,
  and the owed list.

## The oracle's technique, and what it does not reach

QUOTEMETA-SPLICE (`variables_common.md` §3.6): replace each `${name}` with
`(?:` + quotemeta(value) + `)` and ask libpcre2 the resulting ORDINARY
pattern. **The wrap is unconditional and it is a RULING** (Frank,
2026-09-23) — a reference is ONE node, so `${x}+` with x = "ab" means
`(?:ab)+` and a bare splice would read `ab+`, making the oracle disagree with
a CORRECT artifact.

The operator forms are evaluated by a SECOND READING of the design's own
table, in python, and the file says so: what is independent there is the
MATCH of the expanded literal, not the expansion. Named per
`docs/dev/learnings.md` §3's rule to say what a control shares with its
subject — this one shares the design table and nothing else.

**Oracle-less by construction, and counted rather than dropped:** every UNSET
cell and every `:?` refusal (there is no PCRE2 spelling for "this literal is
absent" to splice), the UTF-8 validity refusals, and any word that is a
nested reference (resolving one is the mechanism under test). The sweep
FAILS on an empty checked population, because a sweep that checked nothing
reads exactly like a sweep that found nothing wrong.

## Adding a case

`var <name> "<value>"` and `var-unset <name>` are block-scoped and
repeatable, one line per variable; the value carries the existing
quoted-subject escape set. `gu unset-var "<subject>"` is the refusal
expectation. Run `bash tests/vars/run_vars_tests.sh` — both arms, because a
cell the corpus scores green and the oracle has never seen is a cell scored
against its own author.

Maintenance: update this file when files are added/removed or their roles
change.
