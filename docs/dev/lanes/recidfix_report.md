# recidfix — fixing the identity gate's empty population

THE RED (as briefed): after the [VAR] MVP merge (809aab12),
`make test-recursion-identity` read 2 passed / 12 failed, every FAIL the
same shape — "compiled 0 of  call-bearing patterns", "only 0 patterns
compared identical (floor 700) — the sweep is not populated".

## Cause, confirmed

`tests/codegen/run_recursion_identity.sh`'s corpus lister reads every
`tests/**/*.rxt` pattern line via plain `open(src)`. Module `vars`' own
corpus deliberately carries a raw non-UTF-8 byte in a pattern line
(`^${v:-\xff}$`), which `open()` cannot decode — one `UnicodeDecodeError`
killed the classifier before it wrote a single pattern to either output
file, so every downstream count read zero. Exactly the defect class
`vartriage_report.md` already fixed in three `[M6.2]` identity scripts
(`run_endvar_identity.sh` etc.); this script reads the corpus the same
way and was not among those three, so the manager's guessed FOURTH READER
was right.

## Fix

Same shape vartriage used: `errors="surrogateescape"` on both the read and
the write `open()` — round-trips the exact original byte, verified, not a
re-encoding of it. `FILEPIN` re-pinned `6ef76820` → `809aab12` (D76): the
first commit reachable from main carrying abi 32
(`PCREC_ARTIFACT_ABI`, bumped by `41e9aa38` on `lane/varmvp`).

## Result — the described bug is fixed and verified

Corpus 3187 patterns (313 call-bearing, 2874 call-free). Positive controls
PASS on all four axes. Comparison **(B) whole-file vs the pin is CLEAN on
every axis** (same=2561/2562, differing=0, refusal-mismatch=0,
stamp-moved=0). `[ART-SIZE] SIZE_TERM_REGION_MOVERS` fired live again
(4/4) with no re-derivation needed — the population restore alone
resolved it.

## Found, not fixed: comparison (A) has a real, unrelated divergence

With a real population, **(A) program-region vs the frozen pre-module pin
`ac4917d`** now reports 170 call-free patterns differing on all four axes
— e.g. `(?*(a|ab))\1$`, `(*napla:(a|ab))\1$`, every lookaround-alias +
backreference shape.

**Root-caused, not merely observed.** Built `ac4917d`'s reference compiler
directly and diffed `(?*(a|ab))\1$`'s program region (same `-p rx` prefix
both sides, per this file's own trap list): the ONLY difference is

```
rx_bref_match(subject, subject_length, (size_t)ref_start, (size_t)ref_end, ...)
vs
rx_span_match(subject, subject_length, subject + (size_t)ref_start,
              (size_t)(ref_end - ref_start), ...)
```

This is the varmvp lane's own ruled rename — commit `d93aa931`, "[VAR] M6
RULING: one seam entry pair serving two constructs, not a sibling pair" —
which changed the backreference-compare call's name AND its argument
shape (two offsets → pointer+length) so it could serve both `\1`-style
backreferences and `${name}` variable matching. A corpus-wide count of
`\1`..`\9`-bearing patterns (165) closely matches the reported 170,
corroborating that the whole differing population is this one rename.

This gate is opt-in (`make test-recursion-identity`, not in `make test`),
so it appears never to have run with a real population since the rename
landed — nothing caught it. It is a legitimate, ruled, scaffolding-shaped
change, not a defect.

**Filed rather than fixed here.** The file already has an established
shape for exactly this class of known, ruled divergence — named exception
buckets read off the artifact (`island-moved`, `fold-moved`,
`size-term-moved`), each with its own non-vacuity arm. Building a correct
`bref-fn-renamed`-shaped bucket (deriving the exact backreference-bearing
population from the artifact rather than from pattern text, verifying it
covers exactly the 170 and nothing else, adding the matching
`-stamped-but-deny-is-a-noop` arm) is check-design work
(`docs/dev/learnings.md` §3: "controls sharing a source with what they
control") that does not fit this lane's time box or brief, and rushing it
risks exactly the "control shares a source with what it controls" trap
this house has been bitten by before. Left for a ruling on the bucket's
exact shape.

## Validation

`bash tests/codegen/run_recursion_identity.sh` (CC=gcc-16, foreground,
bounded): `checks passed: 8 / checks failed: 4` — all four failures are
the (A)-vs-`ac4917d` comparisons on default/vm/noprefilter/nocaptures, for
the one root-caused reason above. `linkage` and `elision` axes (which do
not compare against `ac4917d`) are clean. Log:
`worktrees/recidfix/build/recid.log`.
