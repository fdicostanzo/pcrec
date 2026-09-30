# clsid report -- [CLS-TREE] S3's byte-identity instrument (2026-09-29, lane clsid, sonnet)

Branch `lane/clsid`. Delivers `scripts/cls_identity.py` (the D-8 instrument of
`docs/dev/cls_s3_reader_inventory.md` §7/§10), wired as a script (not a make
target), docs (scripts/CLAUDE.md, docs/testing.md "S3 triple-sweep identity
instrument", .gitignore `build-clsid/`). Nothing under `src/`, `cli/`, `lib/`,
`tests/` touched; no compiler hook added.

## Baseline on main (1f0dcda3), two independent builds of one revision

    triples: 15771  {'identical': 13556, 'both-refuse': 2215}     0 movers, 0 asymmetric, 0 timeouts
    by encoding: byte 7513, utf8 8258
    REACH: baseline 1421, candidate 1421 of 8258 utf8 triples  (unmeasured 1437 / 1437)
    CONTROL 1 (instrument, in-memory flip): PASS
    CONTROL 2 (compiler plant, 1,614 triples): 747 movers, all utf8, 0 byte: PASS
    elapsed 856 s at --jobs 2 (includes two `make` builds and the control build)

**main vs main: 15,771/15,771 identical-or-both-refused, REACH 1,421 > 0.**
Populations (before cross-population dedup): corpus-asw 3,584, corpus-x
13,690, bench 1,296, classes 900, witnesses 68. Floors pinned in `PINS`:
triples >= 14,000, REACH >= 1,250 (~90% of measured). Log:
`/tmp/clsid_run2.log` (scratch, not committed); per-triple TSV written to
`<out>/clsid_triples.tsv`.

## Findings

1. **REACH has no compiler stamp; it is read from output by a counterfactual.**
   `lower_class_utf8` returning non-NULL leaves no observable of its own
   (`--emit-facts`/stamps carry no such fact). The instrument uses: the
   `--engine=vm --emit-ir` listing under `-e utf8` differs from the listing
   under `-e byte`. ASCII patterns list identically across encodings, so a
   difference is the lowering firing. It is a LOWER BOUND: a lowering that
   produces byte's own program (`éx`) reads as not reached, and 1,437 utf8
   triples (17%) are `unmeasured` because the forced-VM listing is refused
   (the wide `\p{..}` sets). It can also fire on a char-vs-byte width fact
   that is not a class. **If S3 wants an exact count it needs a stamp
   (e.g. a `RX_`/facts row) -- that is a compiler change, so I did not add
   it; S3's lane or the manager decides.**
2. **`\p{L}+` under `-e utf8` takes ~75 s to compile** (K25/K59 slow zone;
   `\p{L}` alone is 0.1 s). My first run used a 60 s timeout and reported it
   as a TIMEOUT finding; default is now 300 s. It is a pre-existing
   compile-time cliff, not an identity problem, but S3 must not make it worse.
3. **Positive control 2 is anchored, not shared.** The plant is a one-token
   edit (`{ 0x80, 0x7FF, 2 }` -> `0x7FE`) applied to a scratch copy by exact
   match (refuses if the anchor moves); its expected outcome (movers exist, all
   utf8, no byte mover) is stated independently of the compiler's own reach
   claim. 747 of 1,614 triples moved, all utf8.
4. The bench population is read from `/Users/fdicostanzo/pcrec-bench/bench/
   */patterns/*.rx` (read-only); the script skips it loudly if absent, so a
   box without the sibling repo runs a smaller sweep (floors then fail).

## Wiring decision

A script, not `make test` and not a make target: it needs a REFERENCE
revision (the branch point) that `make` has no default for; main-vs-main is
vacuous beyond the baseline; and it costs ~15 min at 2 workers (Mac heavy slot
is another lane's). Same shape and reasoning as `emit_sweep.py`.

## Runtime

Full run 856 s wall at `--jobs 2` (population 15,771 triples x 2 binaries plus
the utf8 listings for REACH; two builds ~1.5 min; control build ~1 min).
`--sample N` gives a ~10 s smoke (floors do not apply).

## Use for S3

    python3 scripts/cls_identity.py --ref <S3-branch-point> --control

The S3 lane runs its own build against its branch point; expected result is
0 movers with REACH >= floor. A deliberately wrong `A_WCLASS` arm should show
up as utf8 movers -- control 2 demonstrates the instrument reports that class
of change.

Validation: COMPLETE for this deliverable (run above). `make test` not run
(no `src/`/`tests/` change).
