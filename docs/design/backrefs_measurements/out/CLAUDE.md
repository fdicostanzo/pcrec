# docs/design/backrefs_measurements/out — archived probe output

Verbatim output of `../probes/`. **Every file here is written by
`../probes/archive.sh`**, so the provenance header cannot drift between them:
probe path and args, the commit the probe was last changed at, the commit and
branch the run was made from, whether the working tree was clean at run time,
the date, and the python3, libpcre2 and gcc versions. Same intent as
`scripts/measure.sh` / `docs/measurements/` (D35), scoped to this lane.

**R32 D1/C14: every header used to say "module `assertions`"** — a copy-paste
leftover from the archiver this lane's was derived from, wrong in all eight
files while their commit refs, dirty lists and content were independently
correct. The stamp is re-scoped and all NINE outputs were re-archived in one
batch from a committed tree.

**Every header says `DIRTY`, and that is inherent to the archiver rather than
sloppiness**: `archive.sh` redirects into the file it is about to stamp, so
the file is already modified when `git status --porcelain` runs. The shipped
`assertions_measurements/out/` headers have the identical property. What
matters is WHAT the dirty list contains — and in every file here it is `out/`
files only: no source, no probe and no design-document edit appears in any of
the nine.

**Evidence for the [M6.5.1] panel (R32), never an oracle.** No check in
`make test` reads anything here; re-run the probe to re-measure.

**R30 M7's rule, inherited: `archive.sh` is the ONLY writer of this
directory.** A hand-written header imitating the archiver is worse than no
header — a reader cannot tell a stamped file from an asserted one without git
archaeology. No file here was hand-written.

## Files

- `publish_discipline.txt` — `probe_publish_discipline.py` (R32 E1). **The
  most consequential file in this directory.** Headline: over **5,808 cells**,
  the emitted model as the design described it at 4cd461f diverges from
  libpcre2 on **138** and produces **40 REVERSED-SPAN cells** — each one a
  `size_t` underflow and an out-of-bounds read in emitted code — while
  PUBLISH-AT-CLOSE gives **0 and 0**. Every divergence is in the re-entry
  class; the 1,452 ordinary-backref cells agree in both models. **The third
  arm is the one that made the fix cheap**: a backref-FREE control of 2,178
  cells agrees in BOTH models, so publication discipline is unobservable
  without a reference and the correction can be scoped to referenced groups
  rather than changing capture semantics for every pattern pcrec compiles.
- `br_semantics.txt` — `probe_br_semantics.py`. **Cell S3 of this file is what
  refuted the design's §3.2** — `(a|b\1)+` on `"ab"` is (0,1) with group 1 =
  (0,1), and the model said (0,2)/(1,2). It was archived here from the first
  day and nothing compared it to the design's claim until R32 did. Headline: **42 cells, 10
  diverging between libpcre2 10.46 and python3 `re`, and all 10 are python
  REFUSING a pattern PCRE2 compiles** (self-references `(a\1)`, forward
  references `\2(a)(b)`, and `^((?i)a)\1$`). The unset rule is confirmed —
  `^(a)?\1$` on `""` is no match — and **2 of the 8 unset cells flip under
  `PCRE2_MATCH_UNSET_BACKREF`**, which is the price of the option the design
  declines. The nested-rewrite cells are the trail's requirement stated as
  answers: `^(?:(a|b)\1)+$` on `"aabb"` is (0,4) with group 1 = **(2,3)**.
- `octal_rule.txt` — `probe_octal_rule.py`. **Axis E is new (R32 E3)**: a
  digit run BEGINNING with 8 or 9 has no octal reading at all (8 and 9 are not
  octal digits, so the re-read consumes zero digits), so PCRE2 reads the whole
  DECIMAL number — and the table's boundary for each run is exactly its own
  decimal value (`\81` needs 81 groups, `\812` needs 812). The count is over
  the WHOLE pattern there, unlike the "so far" count a run WITH an octal
  reading uses: `\81` + 81 groups compiles as a forward reference while
  `\100` + 100 groups reads as octal `'@'`. Rider: **references above `\99`
  exist** (`\100` with 100 groups before is a backref to group 100). Headline
  of the original axes: **the group count is asymmetric.** `\1`..`\9` are always backreferences and count groups over the
  WHOLE pattern (`\1(a)` compiles); `\10`+ count only groups BEFORE the escape
  and fall back to octal otherwise (`\10(a)..(j)` is the byte 0x08, measured
  by discriminator subject, not inferred). `(a)\10` is octal 010, not "backref
  1 then '0'". `\8`/`\9` are backreferences, never octal. `\g10`/`\g{10}` are
  never octal. Axis D: **pcrec's base tier already agrees with libpcre2 on all
  12 class cells**, including `[\400]`'s refusal — the must-not-change
  baseline.
- `spellings.txt` — `probe_spellings.py`. Headline: **20 of 25 spellings
  accepted by libpcre2, only 5 of those also working in python3 3.14** — so
  the base-tier oracle is blind to 15. And the split the registry needs:
  `\g<...>`/`\g'...'` are SUBROUTINE CALLS (`^(a|b)\g<1>$` matches `"ab"`)
  while `\g{...}`/`\g` + digits are backreferences (`^(a|b)\g{1}$` does not).
  `\k<1>`, `\k{1}`, `\kname`, `(?P=1)` and `\g{0}` are compile errors.
- `dupnames.txt` — `probe_dupnames.py`. Three headlines. (1) **libpcre2's own
  `PCRE2_INFO_NAMETABLE` is sorted (name asc, number asc)** —
  `(?<z>1)(?<a>2)(?<z>3)(?<a>4)` reports `a`/2, `a`/4, `z`/1, `z`/3 — which is
  exactly the layout the [M6.5] row rules for `rx_info.groups`, so pcrec
  reproduces a precedent rather than inventing a convention. (2) The duplicate
  check is made **at each DECLARATION against the scoped `(?J)` state there**,
  and an inline `(?-J)` **beats the API `PCRE2_DUPNAMES` bit**
  (`(?J)(?<a>x)(?-J)(?<a>y)` is error 143 with the bit set). (3) The
  resolution rule is **first of the name-run, by ascending number, that is
  SET** — `(?J)^(?<a>x)(?<a>y)\k<a>$` matches `"xyx"` and NOT `"xyy"`, and
  "set" includes set-to-empty.
- `caseless_fold.txt` — `probe_caseless_fold.py`. **R32 C19: axis A used `.`,
  which excludes 0x0a, so it swept 255 bytes while reporting 256; `(?s)` is
  load-bearing here and the count swept is now printed.** Headline: over **all
  256 bytes**, libpcre2's caseless backreference compare in an 8-bit non-UTF build
  folds **exactly the 52 ASCII letters, one partner each, no non-ASCII byte**
  — and pcrec's own `cls_casefold`, read off the shipped compiler on the same
  256 bytes, is the **identical set, zero disagreements**. Axis B: the
  compare's caselessness is the option in force **at the backreference**
  (`^(a)(?i:\1)$` matches `"aA"`; `^(?i:(a))\1$` does not).
- `prefilter_cost.txt` — `probe_prefilter_cost.sh`. Headline: losing the
  prefilter costs **one to two orders of magnitude** on the three idioms where
  it filters — **quote 7.8-21.7x, tag 63.9-159.7x, digits 6.2-20.9x across six
  runs**, so quote the RANGE and never a single run's digits; the hybrid arm
  is multi-modal and the vm-only arm is not. **Two R32 fixes**: the control
  now asserts the two arms stamp the same ENGINE (C13 — a DFA artifact emits
  no stamp at all, so two absent stamps compared equal), and the filler's
  "7-letter words all differ" were seven IDENTICAL letters (C9), so `(\w)\1`
  matched the "nomatch" subject at offset 0; no two adjacent letters are equal
  now, and
  **nothing at all** on the two where the erased approximation matches at
  offset 0 (reported as NOISE, which is a result rather than a failed
  measurement). Both arms compile the identical pattern with the identical
  engine, so the timing is attributable to the prefilter alone.
- `erasure_hazard.txt` — `probe_erasure_hazard.py`. **Revised twice by R32.**
  Headline: across **six** families and **12,786 DISTINCT** subject-family
  pairs (C8: the first version sampled with replacement and reported the draw
  count, inflating three families 31.5x, and carried a `finite` family
  identical to `letter`) the backref-erased approximation **never
  false-negatives** — and its **SPAN differs on 389 / 100 / 220 / 52 / 78
  subjects** in five of the six, so it cannot serve `engine_m4.md` §6.1's
  exact-window role. **The POSITIVE CONTROL is the file's most important
  block** (E2/C12): put a POSITION PREDICATE inside the referenced group and
  **6 of 10 cells ARE false negatives** — `(\ba)\1` matches `"aa"` and
  `(\ba)\ba` does not — so the erasure is a superset only for an
  ASSERTION-FREE group, and the zero column above is a measurement rather than
  a tautology. The probe REFUSES to report if that control finds nothing.
- `expand_cost.txt` — `probe_expand_cost.py`. Two headlines. §0: **a default
  build sends `(abc)(abc)` to the VM naming "capture group at pattern offset
  0"**, and `--no-captures` sends the same pattern to the DFA — so the
  finite-language expansion's entire customer set is `--no-captures`. §1/§2:
  `([a-z]{2})\1`'s 676-word expansion compiles to **321 KB of C**;
  `([a-z]{3})\1`'s 17,576-word expansion is REFUSED at >32,000 DFA states;
  `([a-z]{4})\1`'s 4.1 MB pattern **cannot be passed to a compiler at all**
  (`E2BIG`). Bisected on the shipped compiler: **the largest `|L(G)|` that
  compiles is 10,525**, at 7,116,509 bytes of emitted C and ~2 s of gcc — a
  boundary that REPRODUCES across two independent runs at identical byte
  counts.

Maintenance: update this file when outputs are added/removed.
