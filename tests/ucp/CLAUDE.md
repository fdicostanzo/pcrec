# tests/ucp — module `ucp` ([UCP] U1, docs/design/ucp_design.md, D130)

PCRE2_UCP's semantics: `(*UCP)` / `--ucp` / `.rxt` `flags u`. The `.rxt`
files ride `test-corpus` like every module's; `make test-ucp`
(`run_ucp_tests.sh`) runs the three checks the corpus cannot be.

## Oracle rule — this directory declares its own

python `re` has no PCRE2_UCP, so `verify_rxt.py` skips this directory (it
carries a `verify_*.py`, the declaration `tests/assertions/` set the precedent
for) and every `flags u` block anywhere. **`verify_ucp.py`** re-checks every
cell against the resolved libpcre2 on every `make test-ucp`, with the block's
options spelled as PCRE2's own verbs inside the pattern (`(*UTF)`, `(*UCP)`,
`(?i)` after the leading verb run) because the shared CLI oracle
(`tests/fuzz/pcre2_oracle.c`) is pinned at options = 0. Every expectation was
GENERATED from libpcre2 10.48 and then re-verified against the 10.46
reference (1,540 / 1,540 agree; transcript
`docs/dev/lanes/ucpu1_evidence/verify_10.46.txt`). `perr` blocks are counted,
not checked: they are pcrec's capability refusals.

## Files

- `sets_utf8.rxt` — the NARROW UCP sets under `-e utf8` (`\d \D \s \S`,
  `[:digit:] [:xdigit:] [:space:] [:blank:] [:cntrl:]`), both polarities, at
  an atom and in a class, `(*UCP)` / `(*UTF)(*UCP)` either order / `flags u`,
  with no-UCP controls.
- `knobs.rxt` — `(?aD)/(?aS)/(?aW)/(?aP)/(?aT)/(?a)`, their unsets, scope and
  `(?^)` survival; `(?aW)` reaching `\b`/`\B`.
- `caseless.rxt` — the ASCII-restricted fold (`(?aW)(?i)\w` never reaches
  U+212A), fold-closed narrow sets, per-contribution folding.
- `byte.rxt` — the byte tier: Latin-1 UCP sets (all narrow), the Latin-1 fold
  (T2's `latin1` row), `[:lower:]`/`[:upper:]` fold-inert.
- `refusals.rxt` — `perr` only: the wide sets under utf8, UCP `\b`/`\B` under
  both encodings, `--ucp` without the module, `(*UTF)` under byte, the
  position and repeat rules for the verbs.
- `verify_ucp.py` — the oracle above.
- `ucp_sets.py` — the UCP set POPULATION (construct, DEFK_SET spelling,
  wide-under-utf8), the ONE list both the capture and the comparison read.
- `build_ucp_store.py` — captures `oracle_store/libpcre2-10.46-ucp/` over one
  light ssh session (tests/oracle/remote_adapter.py, `ucp=True`).
- `ucp_compare.py` — every UCP set pcrec builds, swept over every code point
  (tests/uprops/uprops_sweep.c, reused), EXACT against the committed store;
  the wide utf8 sets must be refused by name with construct==spelling in the
  store standing in; the refusal partition and population (23 compared, 9
  refused) pinned.
- `latin1_fold_check.c` + `latin1_fold_10.46.tsv` — `pcrec_fold_latin1`
  against 10.46's UCP|CASELESS relation over all 256×256 byte pairs (112
  partner pairs). Failing-direction controls measured at landing: the ASCII
  fold reads 60 disagreements, the utf8 fold 10.
- `run_ucp_tests.sh` — the section driver (`make test-ucp`).

## Maintenance

When U2/U3/U4 lift a refusal, move the block out of `refusals.rxt` into a
real-cells file (generated from libpcre2, re-verified on 10.46), and update
`ucp_sets.py`'s `wide_utf8` column and `ucp_compare.py`'s population pin in
the same change.
