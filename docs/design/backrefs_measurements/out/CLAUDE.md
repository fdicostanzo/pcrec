# docs/design/backrefs_measurements/out — archived probe output

Verbatim output of `../probes/`. **Every file here is written by
`../probes/archive.sh`**, so the provenance header cannot drift between them:
probe path and args, the commit the probe was last changed at, the commit and
branch the run was made from, whether the working tree was clean at run time,
the date, and the python3, libpcre2 and gcc versions. Same intent as
`scripts/measure.sh` / `docs/measurements/` (D35), scoped to this lane.

**Evidence for the [M6.5.1] panel (R32), never an oracle.** No check in
`make test` reads anything here; re-run the probe to re-measure.

**R30 M7's rule, inherited: `archive.sh` is the ONLY writer of this
directory.** A hand-written header imitating the archiver is worse than no
header — a reader cannot tell a stamped file from an asserted one without git
archaeology. No file here was hand-written.

## Files

- `br_semantics.txt` — `probe_br_semantics.py`. Headline: **42 cells, 10
  diverging between libpcre2 10.46 and python3 `re`, and all 10 are python
  REFUSING a pattern PCRE2 compiles** (self-references `(a\1)`, forward
  references `\2(a)(b)`, and `^((?i)a)\1$`). The unset rule is confirmed —
  `^(a)?\1$` on `""` is no match — and **2 of the 8 unset cells flip under
  `PCRE2_MATCH_UNSET_BACKREF`**, which is the price of the option the design
  declines. The nested-rewrite cells are the trail's requirement stated as
  answers: `^(?:(a|b)\1)+$` on `"aabb"` is (0,4) with group 1 = **(2,3)**.
- `octal_rule.txt` — `probe_octal_rule.py`. Headline: **the group count is
  asymmetric.** `\1`..`\9` are always backreferences and count groups over the
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
- `caseless_fold.txt` — `probe_caseless_fold.py`. Headline: over **all 256
  bytes**, libpcre2's caseless backreference compare in an 8-bit non-UTF build
  folds **exactly the 52 ASCII letters, one partner each, no non-ASCII byte**
  — and pcrec's own `cls_casefold`, read off the shipped compiler on the same
  256 bytes, is the **identical set, zero disagreements**. Axis B: the
  compare's caselessness is the option in force **at the backreference**
  (`^(a)(?i:\1)$` matches `"aA"`; `^(?i:(a))\1$` does not).
- `prefilter_cost.txt` — `probe_prefilter_cost.sh`. Headline: losing the
  prefilter costs **6.2x to 130x** on the three idioms where it filters (the
  ratio is stable in order of magnitude, not in its digits — four runs during
  the lane spanned 6.2-21.7x, 64-157x and 6.2-20.9x), and
  **nothing at all** on the two where the erased approximation matches at
  offset 0 (reported as NOISE, which is a result rather than a failed
  measurement). Both arms compile the identical pattern with the identical
  engine, so the timing is attributable to the prefilter alone.
- `erasure_hazard.txt` — `probe_erasure_hazard.py`. Headline: across seven
  families and ~28,000 subject-family pairs the backref-erased approximation
  **never false-negatives (0 in all seven)** — so it is a sound `nomatch`
  rejector — and its **SPAN differs on 367 / 100 / 786 / 1785 / 1785 / 2525
  subjects** in six of the seven, so it cannot serve `engine_m4.md` §6.1's
  exact-window role. The `tag` family reports 0 span differences over 24
  positives. Read the span EXAMPLES in the file: they are the concrete
  miscompiles a hybrid would produce.
- `expand_cost.txt` — `probe_expand_cost.py`. Two headlines. §0: **a default
  build sends `(abc)(abc)` to the VM naming "capture group at pattern offset
  0"**, and `--no-captures` sends the same pattern to the DFA — so the
  finite-language expansion's entire customer set is `--no-captures`. §1/§2:
  `([a-z]{2})\1`'s 676-word expansion compiles to **321 KB of C**;
  `([a-z]{3})\1`'s 17,576-word expansion is REFUSED at >32,000 DFA states;
  `([a-z]{4})\1`'s 4.1 MB pattern **cannot be passed to a compiler at all**
  (`E2BIG`). Bisected on the shipped compiler: **the largest `|L(G)|` that
  compiles is 10,525**, at 7.1 MB of emitted C and 2.0 s of gcc.

Maintenance: update this file when outputs are added/removed.
