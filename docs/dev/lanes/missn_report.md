# missn report: the kit side of R-6, the `MF_MISS_N` token

Branch lane/missn, cut from lane/memfn-rowcon @ 5f0e926e. Kit-only; pcrec
does not reference the token (R-6, a pcrec lane, adopts it later).

## What was built

- **Token.** `memfn/include/memfn.h`: `extern const char mf_miss_n[]`
  (`MF_NS(miss_n)`, exported `pcrec_mf_miss_n`, C15 clean: the one symbol is
  `R pcrec_mf_miss_n`) and `#define MF_MISS_N ((const char *)mf_miss_n)`.
  Defined in `memfn/src/gate.c` beside its classifier, text `"\x01mfN"`
  (nonsense if ever pasted). Chosen over a string-literal macro because an
  exported array has ONE address no caller's text can have, so no C text
  collides; this is the same shape as the header's other exports (MF_NS
  names), and matches `MF_TOK_ACCEPT/REJECT` in spirit (reserved \x01 text)
  without relying on text compare.
- **Meaning (condition 1).** At the `miss` field in memfn.h: "MF_MISS_N states
  that the miss value is this site's own `n` hook; NULL leaves it UNSTATED
  (R1: a row that needs it declines)". Also updated: fields.def MISS_N class
  text, row_contracts.md §2 example.
- **Classifier.** `cl_miss` (gate.c): the token -> `CL_MISS_N`; the existing
  textual rule (miss text == n text) kept; NULL stays unstated.
- **Resolution.** `kit_miss(h)` (kit.h, static inline): the token resolves to
  `h->n`, anything else is `h->miss`. Every reader goes through it.
- **MF_SITE_ABI / MF_VOCAB: no bump, decision.** memfn.h's rule is "layout
  and meaning of every struct"; the token moves no layout and no existing
  value's meaning (an old caller's NULL / text miss reads as before). It is
  additive. Q-G2-18's bump (3) was a meaning change of an existing field.

## The `miss` reads table

Every `h->miss` / `.miss` / `->miss` read in memfn/ (greps over src, include,
tests), and its disposition:

| site | read | disposition |
|---|---|---|
| gate.c `cl_miss` | NULL test, text compare | token -> MISS_N added; text rule kept |
| generic.c:293 `expr_text` | pasted as `(miss)` | `kit_miss(h)` |
| generic.c:372 ASSIGN `need` | presence | `kit_miss(h)` |
| generic.c:389 ASSIGN on_miss cond `res == (miss)` | pasted | `kit_miss(h)` |
| generic.c:446 ON_CAND `need` | presence | `kit_miss(h)` |
| generic.c:486 ON_CAND `res = (miss);` | pasted | `kit_miss(h)` |
| generic.c:511 ON_CAND on_miss cond | pasted | `kit_miss(h)` |
| generic.c:603 `func_call` arg[4] (miss argument of the call) | pasted as call arg | `kit_miss(h)` (NULL gives the "needs the `miss` hook" refusal) |
| generic.c:646 EXPR RETURN `need` | presence | `kit_miss(h)` |
| ofsskip.c:384 `miss_is_n` (define and use) | NULL test, strcmp with `n` | `kit_miss(h)`; token == n by construction |
| precheck.c | no read of `->miss` (only the contract: serves MISS_N, FM(miss)) | none needed |
| runcmp.c:418 | `FLD_miss` declared MF_ANY, not read | none |
| gate.c trace | prints class names only, never values | none |
| compose.c | no read (the one hit is an error string) | none |
| tests/g2 g2_gen.c `fill_hooks` | sets `h->miss` | `miss_text(4)` returns `MF_MISS_N`; refusal case sets it |
| tests/g2 g2_gen.c refusal `RETURN-without-miss` | sets NULL | unchanged |
| tests/g2 g2_ref.c, g2_driver.c | read `miss_mode` via `g2_missv` | mode 4 -> `n` (the reference's own answer, never kit output) |
| tests/memfn/arm_fixtures.c | `Bounds.miss` | two token fixtures added |

No site pastes the sentinel bytes: all pasting readers use `kit_miss`.

## Coverage (condition 2)

- G2: `miss_mode` 4 = token. `finish_site` converts every mode-0 ("n" text)
  site with an even id to mode 4: no RNG draw is added, so every other
  site is unchanged. `g2_missv(4, n)` = `n`: the expected value is the
  scalar reference's, not a kit output. The token is sent through the same
  paths as any miss: mf_emit, define+use, define+call, on every row the kit
  chooses (generic, and ofsskip/precheck where chosen).
- New refusal case: `RETURN-MISS_N-without-n` (token with `n` NULL refuses
  loudly; the refusal table went 257 -> 258).
- Driver prints `G2 miss token (MF_MISS_N): sites S (RETURN r, ASSIGN a,
  FUNC/RETURN f), checks C (positive P)` and reports a coverage MISSING when a
  shape is absent or only one outcome is seen.
- Floors (run_g2.sh literals, `FLOOR_MT_*`): sites 500, RETURN 130, ASSIGN 45,
  FUNC/RETURN 90, checks 1,800,000. Measured, quick tier: sites 538, RETURN 150,
  ASSIGN 56, FUNC/RETURN 105, checks 2,188,666 (positive 664,920). Site
  counts are tier-independent (same seed); checks floor is the quick count, the
  full run has more.
- Row-level pins (C5, `tests/memfn/pins/arms.tsv`, floor 34 -> 38):
  `ofs-miss-token` (ofsskip) and `pre-lead-handoff-miss-token` (precheck
  ASSIGN), rendered with `miss = MF_MISS_N`. Their digests are the SAME as
  their text-stated twins' (`ofs-miss-n`, `pre-lead-handoff`): the token
  renders as `n`'s text and picks the same arm. `run_arm_pins.sh`: 81 checks
  passed, 0 failed. These are the three N2 cells (ofsskip define and use,
  precheck ASSIGN use) that the token states.

## Results

- G2 --quick, run 1 (floors still 0, measuring): gcc-15, 4044 sites,
  15,560,419 gcc checks passed, 0 failed, 15,945,765 total, W1-W3
  fired, 258 refusal+API cases. The one `coverage-missing 1` is the quick
  tier's documented alignments 4/16 exemption.
- G2 --quick, run 2 (final state, floors armed): rc 0, checks passed
  15,945,765, failed 0, population 4044 sites in 34 batches, floors held.
- `make strict` rc 0. `make -j4` clean. C15/C16 (`run_link_checks.sh`) PASS.
- Zero movers: pcrec does not name the token, and the only behavioural
  change for a non-token `miss` is `kit_miss(h) == h->miss`; `make test`
  and the sweep are not run here (forbidden).

## VALIDATION OWED (the kit manager's slot)

(a) Full G2: `memfn/tests/run_g2.sh` (no `--quick`), `TMPDIR` in a scratch
dir, wrapped in `gnutimeout`; judge: its last lines `checks failed: 0`
and rc 0 (it checks the new `FLOOR_MT_*`).

(b) Zero-mover identity gate, from the worktree/merged tip, on the slot box:

    python3 scripts/emit_sweep.py --ref 5f0e926e > LOG 2>&1
    python3 docs/design/memfn/probes/lxrun/memfn_r4c_gate.py --zero-dumps LOG

The sweep prints `===== REAL RUN` and, after the streams, the gate judge
prints `R4C-GATE PASS` (rc 0); wait for that line (the previous runs took
about 300 s on Linux). `--zero-dumps` because the ref already carries the
memfn-simd rows and this change adds no option row.

## Charter vs committed

- [x] token `MF_MISS_N` public in memfn.h, exported under MF_NS (C15 pass)
- [x] memfn.h states its meaning at `miss`; fields.def MISS_N text;
      row_contracts.md §2 sentence
- [x] classifier maps token to CL_MISS_N; the text rule kept; NULL unstated
- [x] every `miss` read resolved or never pasted; table above
- [x] MF_SITE_ABI decision stated (no bump, additive)
- [x] G2 exercises the token against the reference, floors added; row pins
      for ofsskip and precheck
- [x] CLAUDE.md files: memfn/src, memfn/tests, tests/memfn
- [x] zero movers by construction; sweep OWED
- [x] report; `make strict` 0; G2 --quick twice (the limit)
