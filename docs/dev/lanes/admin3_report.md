# admin3 — three owed doc/test items (2026-09-22)

1. **Wrong `PCREC_ARTIFACT_ABI` citation.** Both live readers cited
   `src/core/limits.def` (no such row exists); fixed to
   `src/gen/emit_dfa.c:51` in `docs/dev/coding_guide.md` §3.1 and
   `src/gen/CLAUDE.md`. Two more grep hits (`docs/design/reqpos_2b.md:515`,
   `docs/design/CLAUDE.md:2277`) already *describe* the wrong citation as a
   past finding — left unedited.

2. **`run_prechecks.sh` §3 [OPT-REQBYTE] utf8 coverage.** New §3.6, five
   `-e utf8` witnesses in the section's idiom: `é`→"169", `(?i)é`→"195",
   `x(é|è)y`→"121", `a\x{1F600}b`→"98", `(?i)k`→"none" — verified against
   `build/pcrec` first. Check count (the file's own `checks passed:`
   trailer): **113 → 123**. No pinned total exists elsewhere (grepped
   `tests/mech/`, `tests/rxtsource/`) — nothing else to re-pin.

3. **`docs/testing.md` giveup.rxt/-fprefilter prose (~line 3458).** NOT
   stale — live-ran `giveup.rxt`'s axesfix-rewritten witnesses under
   default (2/2 pass, give up) and `-fprefilter` (2/2 fail, `nomatch`),
   exactly the "2 MISMATCH" the prose describes. No edit. A DIFFERENT
   `(a*)*b` witness at ~line 2437 belongs to
   `tests/lib/run_gen_timeout_tests.sh`, not `giveup.rxt` — out of scope,
   flagged not fixed.

**Validation:** `make -j4 CC=gcc-16` clean; `make strict CC=gcc-16` clean;
`make test-prechecks CC=gcc-16` 123/0; `make test-codegen CC=gcc-16` 9/10
(sole red: standing darwin `nm arm_a.o` probe, unrelated). No full `make
test`, per the brief.

Head: `4eed2e5d` (item 2, on `26c7edc3` item 1); item 3 made no commit.
