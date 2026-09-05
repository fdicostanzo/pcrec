# docs/design/utf8_measurements — the [M5.0] lane's instruments

Probes and archived output for `../utf8_design.md`, the UTF-8 milestone's
design gate. Same shape as `../lookaround_measurements/` and its siblings, and
it BORROWS rather than copies: `probes/u8_oracle.py` loads
`../../backrefs_measurements/probes/br_oracle.py`, which loads
`../../eng_brep_measurements/probes/pcre2_ctypes.py`. Two levels of borrowing,
no second binding — a lane that re-implements the binding it is checking
cannot detect that the original moved.

## WHAT IS DIFFERENT ABOUT THIS LANE, and read it before any number

**The reference oracle is on another machine.** libpcre2 10.46 lives on the
old box; this Mac's library is a different version, and PC-3 measured the two
diverging on the day this lane opened. So unlike every earlier gate here,
**the oracle probes do not run where the repository is.**

They run over `ssh`, and the mechanism has one property worth stating:
**nothing is written on the old box.** `probes/bundle.py` embeds the borrowed
oracle chain verbatim (as `repr()` of each file's source) plus an `importlib`
shim, so the whole program arrives on **stdin** and the same import chain
executes the same bytes on the far end. Edit `pcre2_ctypes.py` and the next
bundle carries the edit — which is the property borrowing was for, preserved
across a machine boundary.

**Every archived file names the ORACLE HOST in its header**, beside the usual
commit/version block, because for this lane a number without that line cannot
be read at all.

**A LOCAL RUN MEASURES A THIRD LIBRARY.** On this Mac,
`ctypes.util.find_library("pcre2-8")` resolves to **miniconda's** libpcre2 —
version **10.37** — not Homebrew's 10.48 and not the reference 10.46. A
`--local` run is a deliberate version comparison and says so in its header;
read the probe's own `libpcre2:` line, which reports what actually answered,
never the archiver's `local host` line.

## The instruments

- `probes/u8_oracle.py` — the lane's oracle helper. Re-exports br_oracle's
  surface and adds the four things UTF questions need and no earlier lane had,
  because every earlier lane was deliberately byte-oriented (`pcre2_ctypes.py`
  says so at its own `PCRE2_UTF` constant: *"not used: this module stays
  byte-oriented like pcrec"*): the option bits **with a renderer**, so every
  row carries its options word symbolically rather than by memory; a `match()`
  that **returns error codes instead of raising**, because for this lane an
  ill-formed subject's error code IS the measurement; a **bytes-in/bytes-out
  discipline** that refuses a `str` outright (the borrowed binding encodes
  `str` as latin-1, which would silently turn the two UTF-8 bytes of `α` into
  one byte 0xB1); and a python `re` arm in **both** flavours, `str` and
  `bytes`, since python has a different engine per subject type and the whole
  D27 list turns on which one a cell needs. `SELFCHECK` is behavioural and
  runs at import — six checks, each asserting a constant does what its name
  says rather than trusting the value.
- `probes/bundle.py` — the remote-payload builder described above. Its
  docstring carries the borrowing argument in full.
- `probes/archive.sh` — the ONLY writer of `out/` (R30 finding M7: a header
  hand-written to imitate the archiver is *"worse than absent provenance"*).
  `--local` selects the comparison mode; `.sh` probes are always local because
  they measure pcrec, which is built here.
- `probes/probe_premises.sh` — the pcrec side on HEAD: the refusals, the
  registry rows, and the three source sites `../utf8_design.md` argues
  against, quoted from the tree rather than paraphrased.
- `probes/probe_invalid.py` — charter (i): invalid UTF-8 in three modes.
  Deliberately does NOT measure `PCRE2_NO_UTF_CHECK` over an ill-formed
  subject: PCRE2 documents that as undefined behaviour, and a measurement of
  UB is one build's accident rather than evidence for a design.
- `probes/probe_uprops.py` — charter (ii): 114 `\p` spellings, the
  UTF-gating question, and an **interval census swept from the oracle itself**
  (all 1,114,112 code points against a compiled `^\p{X}$`) rather than from
  python's `unicodedata`, which carries a different Unicode version. Also
  DERIVES PCRE2's own Unicode version by sweeping `pcre2_config_8` slots —
  this box has no `pcre2.h`, so a guessed enum that returns something
  version-shaped is exactly the confident-wrong-measurement shape
  `la_oracle.py` records for `PCRE2_INFO_MAXLOOKBEHIND`.
- `probes/probe_caseless.py` — charter (iii)/[DD-1]. Every cell is an
  ANCHORED whole-subject match, so a partial hit cannot be misread as a
  successful fold.
- `probes/probe_width.py` — charter (iv): the lookbehind width UNIT, and the
  seam's other entries at their boundary cells. Re-runs `la_oracle.py`'s own
  three-cell guard on `PCRE2_INFO_MAXLOOKBEHIND` so this probe's copy of that
  derived index is not an unchecked one.
- `probes/probe_divergence.py` — charter (vi): 28 cells × four columns, with
  the verdict computed from the columns so the design's §7 list is DERIVED
  from the run rather than transcribed.
- `probes/probe_sizing.py` — charter (v): the byte-automaton construction,
  built from scratch and **self-checked before it is believed** (10,916 sample
  points; it caught a real construction bug at 5,460 mismatches before any
  number left the probe). Stdlib only, no oracle: the question is a property
  of the construction, and answering it with libpcre2 would measure libpcre2's
  automaton rather than the one pcrec would build.
- `out/` — archived output; see its own CLAUDE.md, which carries the FOUR
  instrument defects this lane found by running its own probes.

## Every claim's mark

`../utf8_design.md` §0.1 defines MEASURED / STRUCTURAL / ARGUED / ASSERTED and
every cell in the document carries one. **A number in `out/` is evidence for
the panel, never an oracle**: no check in the suite reads these files. Re-run
the probe to re-measure.

Maintenance: update this file when probes are added/removed or change roles.
