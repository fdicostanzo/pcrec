# docs/design/where_to_start/ — instruments for `../where_to_start.md`

Lane `startstudy`, 2026-10-06. A STUDY: nothing here is built by `make` or read by
any check. Compile-side and libpcre2-side only; no clock is read.

- `rinner_model.py` — §B's soundness model. Generates `R = P·L·S`, runs the
  reverse-inner tactic (ENG-TACTICS (b)/(c)) with libpcre2 as its two components
  (an end-pinned anchored run of `P` for the reverse walk's start set; an anchored
  run of `R` for the verify) and compares with libpcre2's own unanchored search on
  every startpos and one find-all per subject. Variants: the gated tactic, the
  handoff (`lowerbound`) and give-up (`fallback`) forms, rust's guard, tactic (c)'s
  end, the ungated tactic split by decline reason, the erased-atomic walk, and six
  MUTATIONS. `--selftest` asserts the gated rows are clean, every mutation is
  detected and the ungated tactic is wrong at least once. `--utf8` adds `é`.
  Env `PCRE2_LIB` (default the Homebrew dylib, 10.48 on this Mac).
  Its header records one instrument defect: `pcre2_dfa_match` reports only the
  longest end for a trailing quantifier, so it cannot enumerate `P`'s ends.
- `rinner_model_byte.txt`, `rinner_model_utf8.txt` — the committed transcripts
  (seed 1 × 6,000 byte; seed 2 × 4,000 utf8). ~15 s each on the Mac M1.
- `census.py` — §D's landmark census. Population and `--emit-facts` reader are
  IMPORTED from `../../dev/optloop/artrev/gen/census.py` (loaded by path, so the
  two same-named files cannot shadow each other). Own pattern reader (top-level
  concatenation, rust's `flatten`), landmark classes start / fixed / bounded /
  exact-rev / presence, and three controls: C1 reader self-test, C2 necessity vs
  pcrec's `req_set`, C3 fixed offsets vs pcrec's `kset_walk`.
  Re-run: `PCREC=build/pcrec CORPUS=. BENCH=<pcrec-bench> OUT=<scratch>
  python3 docs/design/where_to_start/census.py --workers 4` (~25 s), then copy
  `summary.txt`/`rows.tsv.gz` here with the provenance header line.
- `summary.txt` — the census output (provenance header first).
- `rows.tsv.gz` — one row per pattern, every column the summary reads (no
  pattern text; `id` names the bench file or corpus file:line).
- `selftest.txt` — C1's transcript.
- `model_1046.txt` — lane `revtwin` (2026-10-06): `rinner_model.py` re-run against the libpcre2 10.46 reference on
  ubuntubudu (script piped over ssh, `PCRE2_LIB` the box's 10.46), byte seed 1 x 6000, utf8 seed 2 x 4000, `--selftest`;
  all 64 rows of both identical to the 10.48 transcripts. Its own header line says so (the script's hard-coded
  "Homebrew" label is the loaded version's, not a claim).
- `twin_dup_param/` — the D77 trigger twin (D151 item 2): twin patch, ledger, identity logs, the two ubuntubudu timing
  runs (summary + raw TSVs), scratch scripts, README with the verdict (NOT MET: the bench cell is at the memchr floor).

