# ucax report

## STATE AT HANDOFF
Branch lane/ucax (from lane/ucfix). Commit 928dd29f6: `tests/axes/run_axes.sh`, `docs/spec/tuning.md`.

- Ruling: cli.md §1.9¶7, "no other engine reads the Unicode word set yet, so under `-e utf8` such a pattern is REFUSED ... `--engine=vm`". The text is `island_refuse`, src/opt/select_engine.c.
- REFUSAL_PATTERN: `--engine=vm` = "--engine=vm excludes: the VM cannot read that word set yet"; `-fno-ctx-node` = "needs the VM engine, which cannot read that word set yet". Floors 4000 and 40 (REFUSAL_FLOOR). The `--engine=vm -fno-start-set` job inherits the first through its component flag.
- [START-SET] product arm: REFUSED rows no longer fail outright. A row passes only if BOTH sides refused and the text matches `REFUSAL_PATTERN[--engine=vm]`; anything else is an UNDOCUMENTED refusal (bad).
- Spec: tuning.md §2.11¶8 and §2.32¶5.
- Control (shown, not a full sweep): the real diagnostic matches the substring; an unrelated refusal (`\b requires module 'assertions'`) does not, so it stays undocumented.
- OWED: local axes unit `AXES=-fno-ctx-node` was still running at handoff, log /var/tmp/pcrec-pcrec/scratch/ucax/ctx.log. Not run locally: `AXES=--engine=vm` and the product arm. The cloud axes run (cloudrun --name ucax) is the proof for all three.
