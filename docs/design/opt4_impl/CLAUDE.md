# docs/design/opt4_impl/ — the [OPT-4] STEP 3 lane's probes

Lane `opt4b`, 2026-08-29. Measurement material behind
`../prefilter_count_independence.md` §§7-8 (the count-collapsed hybrid
prefilter, K39). Kept separate from `artsize_impl/` for the reason every
`*_impl/` directory is separate: a reader must be able to tell which lane's
run produced which number, and these two rows measure the SAME artifacts for
DIFFERENT reasons — [ART-SIZE] asked whether a cap would REFUSE a pattern,
[OPT-4] can only ever make an artifact smaller and therefore asks the opposite
question, whether it moved an artifact it had no business moving.

**READ THIS FIRST if you are about to compare two artifacts for byte
identity.** Emit with `-o -`, never with `-o FILE`. The artifact `#include`s
its own header by NAME, so two builds written to different paths differ on
that one line and every row reads as changed. It is not hypothetical: the
first run of this lane's corpus-delta harness reported all 60 control
artifacts as "changed" with a byte delta of exactly 0, which is the signature
of this mistake (the two include lines happened to be the same length). The
delta being zero is what makes it survivable; a harness that only printed
"changed" would have reported a corpus-wide regression that does not exist.

**AND IF YOU ARE ABOUT TO READ A TIMING NUMBER OFF THIS BOX.** The bench
throughput subjects re-timed with the SAME binary five times ran 1.81 / 1.81 /
2.13 / 2.15 / 2.17 ns/byte on `t-b-no-at` — a 20 % spread. A three-iteration
after/before pair on that noise showed an apparent 2x "regression" between two
artifacts this lane had already proven byte-identical. Interleave the
variants, use enough iterations, and check identity first: if the artifacts
are the same file, the timing question is answered and does not need measuring.

- `probes/bench_identity.sh` — the NOTHING-MOVES survey over pcrec-bench's own
  patterns. Emits the same population `artsize_impl/probes/bench_acceptance.sh`
  established is the right one (18 pattern files — three under
  `bench/email/patterns/`, eleven under `bench/loglines/patterns/`, and the
  four `email_specimen/*.rx` in THIS repo the bench pins copies of) against the
  three flag sets `testees/pcrec/configs.toml` pins, for 54 emits, and asserts
  each is byte-identical to its `-fno-prefilter-collapse` twin. READ-ONLY in
  the bench: it reads pattern files under `$BENCH_ROOT` and writes nothing
  there (CLAUDE.md's scope mandate — one writer each way, and this lane is not
  the bench's). Result at the close: **54 of 54 byte-identical, 0 moved**,
  which is the design note §8's "bench stamps unchanged" line held to the
  population [ART-SIZE] established rather than to the 14 the note first
  guessed.

Ephemeral measurement scripts (the cost driver with its spliced VM-attempt
counter, the corpus-delta and STEP-0 harnesses) stayed in the session
scratchpad rather than landing here: they instrument a GENERATED artifact by
patching it, which is a one-off diagnostic and not a probe anyone should re-run
against a future tree expecting the same line to be there. Their numbers are in
`../prefilter_count_independence.md` §§7-8 and `docs/spec/tuning.md` §2.17.
