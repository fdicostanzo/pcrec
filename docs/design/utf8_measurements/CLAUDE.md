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
  **[r54] `source_shas()` + the header's SOURCE SHA BLOCK.** `bundle.py` had
  always computed a `_BUNDLED_SHA` of every borrowed file and embedded it in
  the payload, and **nothing read it** — so no archived transcript named the
  bytes that produced it, and the archiver's commit line could not stand in
  because `utf8_measurements/` was untracked at every commit the first round
  stamped. `header()` now prints the hashes in one of two LABELLED modes:
  `bundled` (read out of the payload's own `__main__` globals — the hashes of
  the bytes that actually executed on the far end, and the authoritative
  case) and `local` (hashed from disk here, weaker by construction, and the
  label says so rather than letting a reader assume otherwise). Verified
  agreeing across the machine boundary: `probe_width.py` prints the identical
  four hashes run locally and run over `ssh`.
- `probes/bundle.py` — the remote-payload builder described above. Its
  docstring carries the borrowing argument in full. **Unchanged at r54** —
  the defect was never in this file: it computed the right thing and the
  consumer did not exist.
- `probes/archive.sh` — the ONLY writer of `out/` (R30 finding M7: a header
  hand-written to imitate the archiver is *"worse than absent provenance"*).
  `--local` selects the comparison mode; `.sh` probes are always local because
  they measure pcrec, which is built here.
  **[r54] THE `PROBE LAST CHANGED AT COMMIT` FIELD COULD GO SILENTLY BLANK.**
  Its `git log … || echo uncommitted` fallback **never fired**: `git log` on a
  path that has never been tracked exits **0** with empty stdout — asking
  about a path with no history is not an error — so the `||` tested exit
  status where the fact lives in EMPTINESS. Every transcript archived before
  the probes were committed carried a blank field, which reads as a formatting
  glitch rather than as "this transcript pins nothing". Now an explicit
  emptiness test whose message says so. **This is R30 M7's rule one turn
  further on**: a provenance line that can go blank is the same defect as one
  hand-written to imitate the archiver, because in both cases the reader
  cannot tell stamped from absent.
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
  points, 0 mismatches, reproduced at every re-run). Stdlib only, no oracle:
  the question is a property of the construction, and answering it with
  libpcre2 would measure libpcre2's automaton rather than the one pcrec would
  build. (The lane's "caught a real construction bug at 5,460 mismatches"
  story is a LANE ANECDOTE about a build that no longer exists and that no
  transcript captured — r54 meas-4 re-marked it ASSERTED in the design, since
  it had been sitting under the same MEASURED banner as the 0.)
  **[r54] SECTIONS (h)-(k), THE BINDING CAPS' OWN UNITS.** The probe sized in
  STATES and **none of the caps that binds an emitted DFA is denominated in
  states** (r54 E6). It now also computes, per machine: the `eqclasses`
  partition `ncls` by `src/ir/dfa.c`'s own rule (two bytes are one class iff
  every MINIMIZED state sends them to the same target — minimized, because
  minimization runs before emission and the raw machine's alphabet is not the
  one any cap sees); the premultiplied entry count `min-states × ncls` against
  `PREMUL_MAX_ENTRIES`; the same with `dfa.c:173`'s `\b` word refinement
  applied; and the interned state-set ELEMENT count against K7's
  `PCREC_MAX_SUBSET_ELEMS`. **The verdict column reads `premul`/`PLAIN`, not
  `fits`/`REFUSES`, and the distinction is deliberate**: `emit_dfa.c:2522`
  sits inside `dfa_premul`, an `[ENG-FORM]`/D82 FORM-SELECTION predicate, so
  exceeding it removes the pre-multiplied table from the candidate list and
  costs `[OPT-3]`'s measured 1.27× — it is **not** a compile refusal, and a
  transcript saying "REFUSES" would be a confidently wrong label of exactly
  the kind this directory's `out/CLAUDE.md` catalogues. The minimization is
  computed **once** and shared with the cap block rather than re-run, so the
  addition costs nothing on the two rows (`\p{L}`, `\w`) whose run time is why
  the phase budget exists.
- `out/` — archived output; see its own CLAUDE.md, which carries the FOUR
  instrument defects this lane found by running its own probes.

## Every claim's mark

`../utf8_design.md` §0.1 defines MEASURED / STRUCTURAL / ARGUED / ASSERTED and
every cell in the document carries one. **A number in `out/` is evidence for
the panel, never an oracle**: no check in the suite reads these files. Re-run
the probe to re-measure.

Maintenance: update this file when probes are added/removed or change roles.
