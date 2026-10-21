# tests/fuzz — PCRE2-oracle differential fuzzer

Random pattern/subject generator that differentially fuzzes `pcrec` against
a real PCRE2 8-bit oracle (direct-linked since [ORACLE-LINK]/D98,
2026-09-09 — see `pcre2_abi.h`'s own entry below; historically dlopen'd at
runtime, back when this box had no `-dev` package). Plan step M2.5;
promotes the R1 semantics critic's ad-hoc session
tooling into a committed, repeatable tool. The many-seed, many-pattern
CAMPAIGN stays manual/checkpoint-only (`make fuzz`, `campaigns/`) — see
README.md for why. **[M4.7e]** added a FIXED-seed slice that IS wired into
`make test` (`make test-capturediff`, `run_capturediff_gate.sh`) — a
pinned seed is exactly as reproducible as any other differential in this
tree, which is what the manual-only reasoning below does not cover.

## Files

- **pcre2_abi.h** — the shared PCRE2 8-bit binding, shared.
- **pcre2_oracle.c** — the PCRE2 8-bit CLI oracle, now built on pcre2_abi.h.
- **fuzz_driver.c** — subject-from-file driver template for pcrec-generated matchers, owned by this fuzzer (not a reuse of tests/harness/driver.c).
- **fuzz.py** — generator + comparator + runner: `python3 tests/fuzz/fuzz.py [--seed N] [--patterns 300] [--subjects 15] [--keep] [--jobs N]`.
- **README.md** — full usage, exception-list rationale, output-bucket reference, triage process, and documented findings from this tool's build session (a real PCRE2 ...
- **run_capturediff_gate.sh** — **[M4.7e]** the GATE-ON wiring: runs `fuzz.py` at ONE FIXED seed/patterns/subjects (its own argparse defaults, spelled out in the script so ...
- **campaigns/** — **[M4.7e]** committed logs from the AT-SCALE, many-seed capture differential campaign (D35-style provenance: date, HEAD commit, libpcre2 version, seed ...
- **failures/\<timestamp\>/NNNN_\<kind\>/** — repro bundles (pattern.txt, subject.hex/.bin, outputs.txt) written by runs that found divergences.

## Conventions

Exit code 0 iff zero accept/reject and zero content divergences (the DFA
state-cap bucket — review finding A-3, a known unimplemented-VM-fallback
limitation — and oracle-inconclusive `mlimit` count never affect exit
status; nor do the harness-level buckets added this session: pcrec compile
timeout, oracle probe timeout, and pcrec step/frame-budget exhaustion —
see README.md's "Step/frame budget policy"). A divergence always gets a
bundle under `failures/`; triage by reproducing independently of the
fuzzer and minimizing before concluding it's a real engine bug (see
README.md's "Triaging a divergence").

**[SEL-1] (2026-08-28, K40) NARROWED WHAT THE "DFA state-cap" BUCKET CAN
STILL CATCH.** It counts a pcrec compile stderr containing "too complex for
the DFA engine" (the two DFA-side caps in `src/core/limits.h`, state count
and K7's subset-element budget) OR "NFA exceeds" (`PCREC_MAX_NFA_STATES`,
which has no fallback engine and is UNCHANGED by [SEL-1]). Under
`--engine=auto` — `compile_with_pcrec()`'s only mode — the first half is now
a SELECTION OUTCOME rather than a refusal (`docs/spec/tuning.md` §2.11): a
pattern that used to land in this bucket for that reason now compiles as a
VM fallback and lands in the ordinary accept/compare pipeline instead. The
bucket did not stop being meaningful; its population just moved, and moved
ENTIRELY on this fixed seed's own draw (8 -> 0 at seed 1/patterns 300,
`run_capturediff_gate.sh`'s own re-pin). **A NEW, related bucket, "K41
oversize artifact", lives in fuzz.py ITSELF** (revised 2026-08-28, manager
correction): some of those newly-VM-compiled patterns emit a `.c` file past
`K41_OVERSIZE_BYTES` (1,000,000 bytes) — `docs/dev/known_issues.md` K41.
This is classified by the emitted artifact's SIZE, checked before and
independently of whatever `gcc` does with it, deliberately NOT by grepping
gcc's own error text (an earlier version did that and was rejected as a
flaky gate: gcc's CPU-time outcome under D45's fixed budget depends on box
speed/load, so a bucket keyed on it reads differently box to box, while the
artifact's byte count is fully deterministic per `--seed`). `gcc`'s own
outcome on an oversize artifact (compiled / over-budget) is printed for
information only and never affects the plain "gcc compile fails" bucket,
which stays meaningful — a real pcrec-emitted-code compile defect — only
for artifacts under the threshold. See fuzz.py's own comment above
`K41_OVERSIZE_BYTES` and `run_capturediff_gate.sh`'s EXPECT-block comment
for the full derivation and the three-run determinism proof.

(Rest of this section: see the history file.)

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__fuzz.md`.
