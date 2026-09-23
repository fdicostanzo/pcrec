# lane `c2design` — cycle-2 design notes (2026-09-22, opus, docs-only)

Branch `lane/c2design` from `65bb94b7`. Nothing under `src/`/`cli/`/`lib/`/
`tests/`/`docs/spec/`; nothing written in pcrec-bench (read-only: its pattern
exports and `gen_throughput_subjects.py`). No suite, no timing, no clock. The
only thing compiled is a four-line `memcmp` probe in the scratchpad
(`gcc-16 -O2 -S`) — `reqpos_2b.md` §3.2. Every other number is a count off
committed artifacts (`optloop/c2/reqpos_census.tsv`, `run_selectivity.txt`,
`subject_freq.json`, `cycle1_rows.tsv`) or the shipped source.

**VERDICTS.** `docs/design/reqbyte_freq_pick.md` — **BUILD over the SHIPPED
static prior**, one `abi` event, no new axis bit, no new accessor, no
findings-file plumbing. `docs/design/reqpos_2b.md` — **BUILD tier 2b** (its own
axis bit, a `REQ_RUN` stamp, landing as ONE `abi` event with the pick); tier 2
stays declined and is not even a precondition.

## What the census missed (each note's §0 carries it in full)

1. **The static byte-frequency prior ALREADY SHIPS**, with a consumer, a sum
   check and a header naming this exact hook: `src/opt/prefix_k.c:91`'s
   `byte_freq_ppm_tbl` behind `pcrec_byte_freq_ppm`, read by `[OPT-OFSK]`,
   asserted at 1,000,000 by `run_offset_skip.sh` §1, with D83's findings file
   named as "a second implementation of THIS ONE FUNCTION." Deliverable 1 is
   therefore a one-function change, not a findings-file row.
2. **That prior already delivers all three of `reqpos_census.md` §5's
   whole-call wins**, and of the 12 `capability` patterns whose pick moves,
   **11 move to a strictly rarer byte in the bench's own 1 MiB subject, 1
   absent→absent, 0 commoner** — out-of-sample, since `prefix_k.c` deliberately
   did not fit the table to that text.
3. **`firstset_design.md` §5.2's accessor is refuted by the tree**: a
   `double`-returning parallel to `pcrec_byte_freq_ppm`, where that file's own
   rule is "Integers, not doubles: the selection must be bit-reproducible
   across boxes." A private set-summer, `set_ppm`, already exists (`:302`).
4. **§5.1 understates what is open on `freq` by two items**: name resolution
   (as stated), AND nothing reads a `freq` block's `row` lines into a table at
   all, AND there is no CLI surface (a `--pattern` compile opens no `.rxt`, so
   D83's `--exemplar FILE` has no implementation). None blocks the pick.
5. **"Three whole-call answers on the table" counts wins and losses together.**
   Only `nested-comment-rec` is a LOSING cell (ranks 9, 20); the other two are
   rows pcrec already wins (ratios 0.3674, 0.5605). The honest D119 improve
   population for the pick is **0.4294 weighted**, not 1.4617.
6. **Tier 2b reads no position relative to the match start** — the delta is
   internal to the run, so `dmin`/`dmax`/`run_pmin`/`run_pmax` go unread and
   the four `capability` runs with `run_pmax = -1` are served. **Tier 2 is not
   a precondition for 2b in any sense.**
7. **2b's decline rule cannot come from `freq`, by arithmetic**: an
   independence product over the run's members over-predicts the measured gain
   by 5× / 8× / **3,257×** on the three finite-gain rows — a 650× spread no
   constant fits. A run's density is joint; `freq` is marginal.
8. **A run's gain is not a function of its length**: the population's longest
   finite-gain run, `loglines/http-5xx`'s 8-byte `" HTTP/1."`, has gain
   **1.00×** while `/user`'s five bytes have 119.0×.
9. **Constant-length `memcmp` beats the row's `memcpy`-into-`uint64` sketch,
   measured**: one load + one compare at L ∈ {4,8}, no call at L ∈ {3,4,8,11},
   reading only the L bytes the run occupies — so `[WORD-FOLD]`'s over-read
   worry never arises in event 1 (the masked form is event 2, gated).
10. **The pick rule is a PRECONDITION for 2b's cost story**: the run form's
    per-candidate cost is the density of the byte it `memchr`s, and on
    `logparse-atomic` today's pick is the SPACE (121,963/MiB) where the prior
    picks the COLON (9,070) — in the very cell whose run gain is 1.00×.
11. **`A`'s index within the run is not in the census** (`pick_in_run` is a
    boolean) and it is 0 on 7/68 bench and 12/734 corpus patterns. One owed
    census column before any fixture can be pinned.
12. **`coding_guide.md` §3.1 and `src/gen/CLAUDE.md:25` cite the wrong file for
    `PCREC_ARTIFACT_ABI`** — it is `src/gen/emit_dfa.c:51`; `limits.def` has no
    such row. A writer following the abi ritual's own citation opens the wrong
    file. Flagged, not fixed.
13. **Bit 31 is the last bit spellable `1u << N`** in `lib/pcrec.h`'s flags
    enum. Storage is fine (`uint64_t`); the SPELLING is what moves, and the
    `1ull` widening reaches `axes_registry_check.sh`, whose bit table is
    derived by grepping `PCREC_(NO|FORCE)_`.

## Open questions

`reqbyte_freq_pick.md` §9 (six): ship over the shipped prior now (rec. yes);
13.60% of the corpus as an `abi` 29 → 30 event for a two-cell bar (rec. yes);
mint `PCREC_NO_FREQ_PICK` (rec. no, keep it a value); replace `tuning.md`
§2.27's "matching PCRE2's own choice" sentence (rec. replace); open the
findings-file row now (rec. wait); guard the absent→present hazard (rec. no
guard, measure it — §7 item 2).

`reqpos_2b.md` §9 (six): accept BUILD-2b / DECLINE-2 (rec. yes); ship with no
decline rule (rec. yes); truncate a long run to 8 (rec. yes); take bit 31 or do
the `1ull` widening here (rec. the widening); one `abi` event with the pick
(rec. one); pull `[WORD-FOLD]` forward (rec. wait).

## Validation

COMPLETE for a docs-only lane — no build, suite or sabotage run applies. The
prior's sum was re-verified by parsing the shipped array (1,000,000); the
`memcmp` lowering is reproducible in one command (`reqpos_2b.md` §7 item 3),
and re-running it on the Linux reference toolchain is item 3 of that note's own
owed list, not this lane's. Commits: `eb28addd`, `4f8a2cc8`, plus the
`docs/design/CLAUDE.md` entries and this report. NOTHING OWED.
