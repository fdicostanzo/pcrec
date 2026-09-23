# I-89 block (A) — the unrestricted all-axes answer-identity sweep

Raw transcript of `make test-axes` (unrestricted, `AXES=` unset), executed
by the bench executor per `docs/dev/optloop/linux_ask_i89.md` block (A),
run on ubuntubudu (Ryzen 5 1600) at pcrec main **8d716693** (abi 29,
batch 1's merge). Launched 2026-09-23T07:17:58Z (pid 81637, `nohup
gnutimeout 6h env -u AXES make test-axes`), log last write 09:36:16Z —
wall ~2h18m (the 6h bound did not fire). `make` exit rc=0, zero `*** [`
lines anywhere. Fetched by `scp` from `/tmp/optloop2/axes_full.log` the
same morning (pcrec-bench outbox O-47, `[B76]`).

Verdict: 35 axis passes (baseline + 27 bit-flag axes bits 4-30 +
`--engine={vm,dfa}` + `--vm-entry-shape={3,4}` + `--tune={-2,-1,1,2}`) over
24,343 keys each, all `lost-other=0 mismatches=0 gained=0`. Final
`run_axes.sh:` summary line present and OK; oracle cross-check (PC-4 vs
live libpcre2) OK; DIAL-S3 (tune refusal-set) OK; `tests/codegen/
run_form_census.sh` trailer `checks passed: 1 / checks failed: 0`, census
wall 250s.

**This is the transcript `axes_reconciliation_2026-09-23.md` reads its
per-axis evidence from** — every `agree=`/`budget-bound=`/
`refused-documented=` figure cited there is `grep`-verifiable in
`axes_full.log` at the line the memo names. See that memo for why O-47's
own prose "Facts beside your stated EXPECTs" paragraph reads differently
from this same transcript's own verbatim per-axis table (which O-47 also
reproduced correctly).

Files:
- `axes_full.log` — the full 491-line transcript, verbatim from
  `/tmp/optloop2/axes_full.log`.
