# d27/ — the [DD-14.D27] blinded corpus for module `recursion`

Written by a D27-blinded author who never saw `src/` or `tests/`. The
expectations come from PCRE2's semantics via libpcre2 10.46, never from
pcrec: the corpus tests what the module PROMISES, so it cannot inherit the
implementation's own alphabet of mistakes.

## The corpus

Ten `.rxt` files, all GENERATED — edit `sr_gen.py`'s spec and regenerate,
never the `.rxt` files by hand.

| file | what it pins |
|---|---|
| `sr_spellings.rxt` | every call spelling through the call/reference discriminator; relative and forward resolution (extract §§2.1–2.3) |
| `sr_root.rxt` | `(?R)`/`(?0)`/`\g<0>` re-run the whole pattern, anchors included; the whole-digit-run rule (§2.4, §2.4a) |
| `sr_define.rxt` | `(?(DEFINE)…)` and `(?:X){0}` as one lowering with two spellings (D71 item 4); quantified calls (§2.5, §2.6) |
| `sr_captures.rxt` | a call is capture-transparent: the callee writes, the return restores (§3.1) |
| `sr_atomicity.rxt` | calls are backtrackable, every positive cell paired with the atomic control that must answer the opposite way (§3.2) |
| `sr_wrapped.rxt` | a called group runs as its own region whatever its lexical wrapper is (§3.5) |
| `sr_interactions.rxt` | `\K`, duplicate names, lookarounds, atomic groups, `\G`/`\A`/`\z` against a non-zero startpos (§3.4) |
| `sr_depth.rxt` | left recursion has no compile-time refusal; the guard is a match-time give-up (§3.3, §5) |
| `sr_refusals.rxt` | §5's flat refusal list, existence only, no wording (D26) |
| `sr_email.rxt` | the RFC 5322 specimen, unfactored and factored, on one shared subject list |

## The tools

| file | role |
|---|---|
| `sr_gen.py` | the generator. Holds the whole spec. Every span and group span is filled in from the oracle; the spec supplies only patterns, subjects, startpos values and the author's INTENT, and an intent the oracle contradicts is a hard abort. |
| `sr_check.py` | re-parses the `.rxt` files as TEXT, independently of the emitter, and re-verifies every expectation against libpcre2. |
| `sr_features.py` | two independent arms — a lexical scan of the pattern text, and the compiler asked only whether it refuses — so a block that under-declares a module cannot pass vacuously. |
| `sr_perl.py`, `sr_perl.pl` | the Perl arm (D71 item 5): perl 5.40.1 as a second oracle whose divergences are RECORDED in `PERL_DIVERGENCES.md`, never written as an expectation (D26). |
| `sr_driver.c` | the author's own re-derivation of the documented driver protocol, used only for the two existence questions D27 permits: is this cell refused, and does this deep cell give up. |
| `perl_diverges.txt` | written by `sr_perl.py`, read by `sr_gen.py` to stamp `# perl-diverges` on the affected blocks. |

## Regenerating

    python3 sr_gen.py      # rewrite every .rxt from the spec
    python3 sr_perl.py     # refresh the Perl arm and the divergence table
    python3 sr_gen.py      # stamp the # perl-diverges markers
    python3 sr_check.py    # re-verify every expectation against libpcre2
    python3 sr_features.py # no block under-declares a module

All four are idempotent. **`sr_gen.py` is the ONE exception to "writes
only inside this directory"**, since [K34 landing] 2026-08-24: it also
(re)writes `tests/known_fail/k34_leftrec_giveup.rxt` — see "K34: cells
parked" below. The other three tools are unchanged in that respect.

## [K34 landing fix] 2026-08-24 — the CELL's path assumption, corrected

`sr_gen.py`, `sr_check.py`, `sr_perl.py` and `sr_features.py` each computed
their own repository root as `CELL = os.path.dirname(HERE)` — correct for
the author's D27 CELL (`scripts/mk_d27_cell.sh`'s flat, allowlist-filtered
copy, where `d27/` sat one level above a `docs/` sibling), but one
`dirname` short once landed three levels deep at `tests/recursion/d27/`
(confirmed: running `sr_gen.py` post-merge raised `FileNotFoundError` on
`tests/recursion/docs/design/...`). Fixed at the only place each file made
the assumption (`CELL = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))`),
not by moving files. Worth knowing if a future D27 author's tooling is
landed the same way: the CELL's own relative-path arithmetic does not
survive the move by construction and needs the identical fix.

## K34: eleven cells parked, not written here

`docs/dev/known_issues.md` K34: pcrec `frames` gives up where libpcre2
10.46 reaches a clean, definite NOMATCH on a runaway left recursion whose
callee has a non-recursive alternative (`(a|(?1)a)` and its `b`/`c`-tailed
siblings in `sr_depth.rxt` — NOT the empty-language `((?1)a)`/`(?R)a`
family, which [DD-14.EMPTY] answers correctly and stays live here). `B()`'s
`parked=`/`parked_ref` keyword arguments (see `sr_gen.py`'s own docstring)
move a block's affected CASES — not necessarily the whole block, since a
K34 pattern's MATCH cells are unaffected — out of the live `.rxt` and into
`tests/known_fail/k34_leftrec_giveup.rxt`, rendered by `emit_known_fail`
in the SAME run through the SAME `render_cases` oracle-verifier every live
cell uses, with a pointer comment left at each cell's former position. One
generator run produces both outputs from one in-memory case list, so they
cannot drift apart. Regenerating (`python3 sr_gen.py`) reproduces both
byte-for-byte (idempotency checked both directions, not just on the live
`.rxt` files).

## A NEW finding at this same landing, NOT parked (manager disposition owed)

Merging main's wave E ([DD-14.EMPTY]) changed `((?1)a)` and `(?R)a`'s root
`minw` to the analysis ceiling, so pcrec now answers a clean NOMATCH
instantly for EVERY subject of those two patterns — including `"aaa"`/
`"aaaaaa"`, which `sr_depth.rxt`'s `gu frames "aaa"`/`"aaaaaa"` cells (for
those two patterns only — NOT their `((?1)?a)`/`((?1)*a)` siblings, which
still give up, unaffected by EMPTY since their language is not empty)
expect to give up. MEASURED (`sr_oracle.match_limits`): libpcre2 10.46
still returns `rc -52` on both subjects for both patterns — pcrec's answer
is CORRECT and matches the design's own P-12 ruling, strictly BETTER than
libpcre2's give-up, and the `gu` cells are now stale in exactly the sense
`tests/known_fail/CLAUDE.md`'s `dd14_bc_open.rxt` CELL 3 entry describes
("a give-up is pcrec's own artifact behaviour, never an oracle fact") and
wave E's own commit (`7d1fbc6`) fixed for `tests/recursion/leftrec.rxt`'s
identically-shaped sibling cells. **Not fixed here**: this brief's edit
authorization covers K34 parking only, not this cell's expectation — held
for the manager's ruling (the landing lane's final report has the full
oracle evidence and the precedent commit). `make test`'s d27 section
carries these 4 as its only failures until that ruling lands.
