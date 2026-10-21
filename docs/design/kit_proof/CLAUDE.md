# docs/design/kit_proof/ — evidence for `../kit_proof.md` ([KIT-VERIFY] U1)

Compile-side evidence only: nothing here is built or run by `make`, nothing was timed.

- `counts.py` — REVISION 1's population counts, read from the committed kvcensus run
  (`docs/dev/kvcensus/sites.tsv.gz`, `patterns.tsv.gz`). Kept as revision 1's record.
  Its stage-1 table keyed on the LOCATOR route and so counted VM-finisher hybrids
  (k3-sound M2); revision 2's counts come from `conj.py`.
- `counts.txt` — its output at main `a016b3bfa` (census pin `2523cfe4b`).
- `conj.py` — REVISION 2's instrument, revised for REVISION 2.1 (lane u1rev21): the
  `cover_conj[]` table of `../kit_proof.md` §1.1 written as code (one function per
  conjunct, first failing row = the `why`), over the EMITTED anchored machine read by
  `docs/dev/kvcensus/kvdfa.py`. Rows in order: C1, `earlier-row` (the LOCATE order,
  counted), C3, C4, C6-C12. C2 is RETIRED (rev 2.1) and the census applies nothing after
  the table, so the `why` histogram is first-match in table order; admitted patterns are
  labelled `start-site`/`no-start-site` as a count only. C5 is not here (no population).
  C8 is the machine half only (`span_facts` is unbuilt). C9 tests every depth 0..k
  (rev 2.1, K1); `CONJ_PLANT=c9-depth-k` in the environment restores revision 2's
  depth-k-only C9, the K1 plant (S1136). Modes: `census` (stage-1 sites by FINISHER
  route; the table over every census whole-cover / context-join pattern; sites whose
  sent span 0 is shorter than `k`), `rarm` (verdicts that move under `-fno-rev-end`),
  `witnesses` (one verdict per `FLAGS<TAB>PATTERN` line). Shares kvdfa with the census
  and the k3-sound critic, so it is a RECOUNT, not an independent control. Reproduce
  from the repo root, with `build/pcrec` built:
  `PCREC=build/pcrec python3 -I docs/design/kit_proof/conj.py census docs/dev/kvcensus/sites.tsv.gz docs/dev/kvcensus/patterns.tsv.gz`
  (about 10 s; `rarm` about 3 min under `nice -n 19`). Its first run passed the pattern
  to argv as a Python `str`, which is re-encoded as UTF-8, so non-ASCII patterns
  compiled as different bytes (8 utf8-born corpus patterns read `exact`); the pattern
  now goes to argv as its own bytes.
- `conj.txt` — `conj.py`'s output (all four sections) at main `fa322a7f6` (rev 2.1).
  Against revision 2's run at `542b0cecb` it moves only by C2's retirement (B: every
  `no-start-site` row now reads `cover`) and by the three K1 witnesses (D); the admitted
  set is unchanged (1,197 distinct patterns). Section D gains three lines appended by lane
  ctxspan2 (main `3b0f87b55`, `[r4 B9]`): `ctx_span.md`'s in-span witnesses, machine half only.
  Lane ctxspan21 (main `fd1d1fc98`, `[r4rc R2]`) appended two more lines AS TEXT, not run
  (bench timing window): the per-thread witnesses; lane x0oracle (2026-10-21) ran them
  (both `cover k=2`). `conj.py` also gains the `CONJ_PLANT`s of §6.3 for X0 (S1130-S1134,
  S1139, S1140; off unless named; the default reading and `conj.txt` A-D are unchanged).
- `witnesses.txt` — the witness list `conj.txt` D reads, with rev 2.1's K1 rows
  (`ab|a$\n`, `ab|a\Z\n`, `ab|a$\n\z`: DECLINE at `no-eol-view`; `cover` and wrong
  under the plant), and r4's three in-span witnesses (`a(?=b)[a-z]`, `\w(?=\d)\w`,
  `[a-z0-9_ ]\b[a-z ]`; plant S1149's). And revision 2.1's two per-thread witnesses
  (`a(?=b)[a-z]|ac`, `[ab](?<=a)c|bc`; plant S1150's, `[r4rc R2]`); lane x0oracle ran them:
  both `cover k=2` on the machine half.
- `x0/` — step X0 (§7, spec §6.4): an independent libpcre2 oracle (`x0pcre.c`), the
  driver (`x0.py`), the stated-set rows (`stated.tsv`) and the measured run
  (`results.md`, `out/`). Own CLAUDE.md.
- `cover_twin.py` — the SIZE-ONLY hand twin of §2.4: rewrites an artifact's
  `rx_search` into the `cover` entry. Measured once on `foobar` (main `a016b3bfa`,
  gcc 15.2 `-O2 -c`, dev box): `.text` 2,047 → 1,425 bytes, `rx_search` 100 → 61
  instructions (`-S`, the site inlined in both). Not a timing, not a verdict.
