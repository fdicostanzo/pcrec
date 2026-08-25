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

All four are idempotent and none of them writes outside this directory.
