# davislic report: license of the Davis et al. 2019 regex corpus

Lane davislic, 2026-11-05. Research only: nothing downloaded except small
metadata/text files (Zenodo API JSON, the repo README/LICENSE) into
`$PCREC_TMPDIR/scratch/davislic/`. The 94 MB corpus file was NOT fetched.

## Summary (plain words)

The corpus is real, public, and its primary record is the authors' artifact
repo plus its Zenodo deposit. The only license text on it is the standard
MIT license (copyright the five authors), which covers their artifact
including the corpus file. The Zenodo license field itself says only
"other-open" (a placeholder, not a license). There is no separate data
license, no terms-of-use and no ethics conditions stated for the corpus.
The open point: the patterns were harvested from other people's packages
and the MIT grant only speaks for the authors' own rights. Conclusion:
**UNCLEAR** for storing the raw pattern list in our repo; **COUNT-ONLY plus
a re-derivation recipe is safe today**. A short email to the authors would
settle it (below). Premise holds: both DOIs found.

## Exact dataset

- Paper: Davis, Michael, Coghlan, Servant, Lee, "Why Aren't Regular
  Expressions a Lingua Franca? An Empirical Study on the Re-use and
  Portability of Regular Expressions", ESEC/FSE 2019, pp. 443-454,
  DOI 10.1145/3338906.3338909 (arXiv 2105.04397 is a 2021 preprint).
  The paper's Reproducibility section: "An artifact containing our survey
  instrument, regex corpus, and analyses is available at
  https://doi.org/10.5281/zenodo.3257777."
- Zenodo concept DOI 10.5281/zenodo.3257777 (always resolves to latest).
  Versions (read from https://zenodo.org/api/records/3257777 and
  .../3264017, metadata only):
  - 10.5281/zenodo.3264017, v1.0, 2019-07-01, sole creator "Jamie Davis"
  - 10.5281/zenodo.3264018, v1.0, published 2019-07-01 (record created
    2019-09-02, latest), five creators (the paper's authors, Virginia Tech
    and Stony Brook), adds a 53-byte `tmp.txt`
  - Title both: "VTLeeLab/LinguaFranca-FSE19: Artifact for the Lingua
    Franca paper, appearing at ESEC/FSE'19"; resource type Software;
    access_right: open.
  - Files: `VTLeeLab/LinguaFranca-FSE19-v1.0.zip`, 34,119,422 bytes,
    md5 8c2193bcf9b6df04c2256dc62d588412 (a zip of the GitHub tag v1.0).
- Authors' repo (now https://github.com/SBULeeLab/LinguaFranca-FSE19,
  formerly VTLeeLab). Corpus file in it:
  `data/production-regexes/uniq-regexes-8.json`, 93,866,742 bytes
  (GitHub contents API), "The 537,806 unique regexes in our corpus,
  spanning 8 programming languages", NDJSON of libLF.Regex objects.
  README: "A polyglot regex corpus of 537,806 unique regexes extracted from
  193,524 projects written in 8 programming languages". (The zip is 34 MB
  and the file 94 MB, so the zip presumably holds it compressed; not
  verified, I did not open the zip.)
- Per-language unique regexes, paper Table 1: JavaScript 150,922; Java
  19,332; PHP 44,237; Python 43,896; Ruby 153,334; Go 22,105; Perl 142,777;
  Rust 2,025; sum 578,628 (537,806 after cross-language dedup). Modules:
  top 25,000 by GitHub stars per registry; all of Perl (CPAN, 31,827) and
  Rust. PHP source registry is Packagist, Perl is CPAN.

## License (primary text)

- Zenodo license field, both versions: `"license": {"id": "other-open"}`.
  That is Zenodo's catch-all label, not a license text. No separate
  license statement in the Zenodo description (it is one line plus a paper link).
- Repo `LICENSE` (raw, verbatim head): "MIT License / Copyright (c) 2019
  James C. Davis, Louis A. Michael IV, Christy A. Coghlan, Francisco
  Servant, and Dongyoon Lee. / Permission is hereby granted, free of
  charge, to any person obtaining a copy of this software and associated
  documentation files (the "Software"), to deal in the Software without
  restriction, including without limitation the rights to use, copy,
  modify, merge, publish, distribute, sublicense, and/or sell copies of the
  Software ... The above copyright notice and this permission notice shall
  be included in all copies or substantial portions of the Software."
  README directory table: "LICENSE | Terms of software release".
- Code vs data: ONE license for the whole artifact tree (no separate data
  license file seen). The README calls the corpus part of "our artifact"
  and describes it as "useful for future regex analysis purposes", i.e.
  the intent is reuse; but the MIT text says "Software and associated
  documentation files", and does not mention data or third-party content.
- Terms of use / ethics: none stated for the corpus in the README, the
  Zenodo record, or the paper's corpus section (the paper's ethics-board
  mention concerns the developer survey). The corpus holds only `pattern`
  and a use-count map, no module names (README: the only populated fields
  are `pattern` and `useCount_registry_to_nModules`), so it carries no
  attribution to the upstream packages.
- Not checked: whether `data/` carries its own LICENSE (README listing
  shows none; the contents API for `production-regexes/` lists only
  README.md, a .py script, static-extractors/, uniq-regexes-8.json).

## Selecting the Perl/PHP slice

Per `data/production-regexes/README.md`: the field is
`useCount_registry_to_nModules`, "indicates the language(s) in which this
pattern was found" (a map from registry to module count; the registry
key spellings, e.g. which string means CPAN or Packagist, were NOT seen
and must be read from the file or lib/libLF.py before use). A pattern can
appear under several registries; take those with a CPAN or Packagist key.
Caveat: the paper extracts statically-declared regexes from source, so a
PHP pattern may carry delimiters/flags as written (not verified).

## Conclusion: UNCLEAR (leaning COUNT-ONLY)

- Safe now: store counts (per-language sizes above, acceptance rates under
  libpcre2 10.46, construct tallies) plus a recipe (DOI, md5 of the zip,
  field name, filter), citing the paper and artifact.
- Raw pattern table in our repo: the authors' MIT grant plausibly allows
  redistribution of their artifact with the copyright and permission notice
  kept, so STORABLE with attribution "Copyright (c) 2019 James C. Davis,
  Louis A. Michael IV, Christy A. Coghlan, Francisco Servant, and
  Dongyoon Lee, MIT License" is defensible for the subset, but (1) the
  patterns are extracted from third-party packages whose licenses the
  authors cannot grant, (2) Zenodo labels it only "other-open", and (3)
  the MIT text names software and documentation, not a dataset. Short
  regex strings are thin on copyright, but we did not rule that, and the
  harvsrc stop rule applies.
- What would settle it: email the contact in the README, davisjam@vt.edu
  (J.C. Davis; "Contact J.C. Davis at davisjam@vt.edu"), asking whether
  `uniq-regexes-8.json` is released under the MIT license and whether
  a filtered subset (Perl/PHP, a few thousand patterns) may be committed
  with attribution. Frank decides whether to send it. Downloading the
  94 MB file for private analysis (not committed) is a separate approval
  and is not blocked by anything read here.

## REFERENCES.md entry (none exists; not edited)

Proposed key `[Davis19]`:

    [Davis19] James C. Davis, Louis G. Michael IV, Christy A. Coghlan,
    Francisco Servant, Dongyoon Lee. "Why aren't regular expressions a
    lingua franca? An empirical study on the re-use and portability of
    regular expressions." ESEC/FSE 2019, pp. 443-454.
    doi:10.1145/3338906.3338909. Artifact: doi:10.5281/zenodo.3257777
    (MIT, https://github.com/SBULeeLab/LinguaFranca-FSE19).

## Method notes and caveats

Web search for the Zenodo page and the paper PDF (via arXiv) were read;
metadata and README/LICENSE were read as raw text with curl and the
Zenodo/GitHub APIs. All page content treated as data. The Zenodo web
page (as opposed to its API JSON) was not rendered; the fetch subagents
returned no usable report. The corpus file and zip were not opened.
