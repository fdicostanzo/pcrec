# docs/design/where_to_start/ — instruments for `../where_to_start.md`

Lane `startstudy`, 2026-10-06. A STUDY: nothing here is built by `make` or read by
any check. Compile-side and libpcre2-side only; no clock is read.

- `rinner_model.py` — §B's soundness model. Generates `R = P·L·S`, runs the
  reverse-inner tactic (ENG-TACTICS (b)/(c)) with libpcre2 as its two components
  (an end-pinned anchored run of `P` for the reverse walk's start set; an anchored
  run of `P·L·S` for the verify) and compares with libpcre2's own unanchored search on
  every startpos and one find-all per subject. Variants: the gated tactic, the
  handoff (`lowerbound`) and give-up (`fallback`) forms, rust's guard, tactic (c)'s
  end, the ungated tactic split by decline reason, the erased-atomic walk, six
  MUTATIONS, the FLOORED walk (`floor`, sound; `floor_end`, reported unsound) and four
  NEGATIVE CONTROLS (`neg_factor*`, `neg_border*`). The gate has G2's THREE arms
  (D151 add. 5, lane `rinmodel`): fixed width; `¬(bytes(L) ⊆ alphabet(P))`; and the
  FACTOR-FREE arm (no string of P contains L as a factor AND L border-free), decided
  on P's automaton by `factor_witness` (a product of P's NFA with L's KMP automaton),
  with rows keyed `[factor-free]` for the splits only it admits. `--selftest` asserts
  the gated rows are clean, every mutation is detected, the ungated tactic and the
  negative controls are wrong at least once. `--utf8` adds `é`; `--arms literal`
  switches the third arm off (reproduces the pre-arm transcripts); `--xl` adds
  longer and bordered literals; `--check-arm N` cross-checks the arm's decision
  procedure against brute-force enumeration with python `re` and the generator's
  own bookkeeping; `--shaped N` runs the altwide/sfx-shaped and `[a-z]+xy` cases.
  Env `PCRE2_LIB` (default the Homebrew dylib; 10.46 on the Linux dev box is
  `/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0`).
  Its header records one instrument defect: `pcre2_dfa_match` reports only the
  longest end for a trailing quantifier, so it cannot enumerate `P`'s ends.
- `rinner_model_byte.txt`, `rinner_model_utf8.txt` — the committed transcripts
  (seed 1 x 6,000 byte; seed 2 x 4,000 utf8), REGENERATED 2026-10-11 by lane `rinmodel`
  against libpcre2 10.46 with the third arm on; `rinner_model_byte_xl.txt` (seed 3),
  `rinner_model_utf8_xl.txt` (seed 5 x 6,000), `rinner_model_shaped.txt` (`--shaped 200
  --seed 7`) and `rinner_model_checkarm.txt` (`--check-arm 3000`, seeds 5/6). ~15 s each.
  Report: `../../dev/lanes/rinmodel_report.md`.
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

