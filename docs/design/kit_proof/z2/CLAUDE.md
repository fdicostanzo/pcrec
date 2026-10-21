# docs/design/kit_proof/z2/ — step Z2's instruments (`../../kit_proof.md` §6.4, §7)

Lane z2build, 2026-10-21. The SUBJECT is the BUILT compiler (`build/pcrec-harness`
through the `cover` lever, and its trace build `build/z2trace/`, built with
`-DPCREC_CAND_TRACE`); the ORACLE is libpcre2 10.46 through X0's server
(`../x0/x0pcre.c`) or directly (`x1exh.c`); `../conj.py` is the prototype the built
decision must agree with. Nothing here is built or run by `make`; the heavy modes run
as box-queue jobs. The `make test` half of Z2 is `tests/kitproof/`.

- `z2.py` — the driver (docstring = usage): `census` (the trace harness over every
  census pattern at its own flags plus the `-fno-rev-end` arm: the KITPROOF /
  SPANSET / SITESTATED records and conj.py's verdict beside them), `hist` (K35's
  why histogram, the C8 control, the agreement with conj.py), `stated` (X0's
  set-equality check on every SENT statement the census recorded, deduplicated,
  1-in-M), `x1` (X0's part-2 subject families run through the BUILT artifact),
  `exh` (ruling 1's exhaustive cell), `summary`.
- `x1drv.c` — X1's pcrec side: answers x0pcre's `F` question for one built
  artifact (match_api.md §3.1.3's find-all loop). `X1_PLANT=1` reports every
  match end one byte late, X1's own failing-direction control.
- `x1exh.c` — the exhaustive cell: every subject up to MAXLEN over an alphabet,
  every startoffset and the find-all loop, against `pcre2_match`;
  `Z2_EXH_PCRE_PAT` (in z2.py) hands the PCRE2 side a different pattern, the
  control.
- `stated_built.tsv` — the built slice's statements on the in-span witnesses, in
  `x0.py stated`'s format; `out/stated_built.txt` is its run (all green).
- `out/` — the committed transcripts the Z2 report cites (`exh_ruling1_*.txt`,
  the census histogram, the X1 and stated summaries).
