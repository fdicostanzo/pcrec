# third_party/ — vendored outside data, and the shape it lives in

Data files this project did not author, kept in the tree because something is
DERIVED from them at build time. Chartered by Frank's ruling on
`docs/design/utf8_design.md` §14 ASK 2 (2026-09-04) — *"agreed, reluctantly"*
— together with its extension §3.3.2: **do not architect as if the first
source is the only source there will ever be.**

## The index

| source | what it is | what derives from it |
|---|---|---|
| `ucd-16.0.0/` | the Unicode Character Database at 16.0.0 | `src/parse/uprops_tables.inc` — module `unicode-props`' general-category interval tables |

One row per source. Add a row in the same change that adds a directory.

## The rule this directory exists to make general

**A DATA SOURCE COMPILES TO GENERATED TABLES.** That is the whole of the
derivation step, stated in a form that does not mention Unicode — because a
rule spelled `ucd_to_intervals` would have to be renamed the day a second
source arrives, which is exactly the re-plumbing the ruling exists to prevent.
`src/parse/cls_bits.inc` (generated from libpcre2 censuses by
`tests/probes/probe_cls_bits.c`) is the same shape predating this directory,
and `[DD-11]`/D85 already rules such a file a DERIVED artifact.

`make gen-tables` runs every source's derivation. `make test` runs each one's
`--check` mode instead, which regenerates in memory and fails if the committed
output has drifted — so a hand-edited `.inc` is a red suite rather than a
surprise six months later.

## Two properties, and neither is about Unicode

1. **ONE DIRECTORY PER SOURCE, VERSION IN THE DIRECTORY NAME.** Two versions
   of one source can coexist during a bump, and nothing has to be renamed to
   make that true. A version bump is a deliberate act with a deliberate diff,
   which is `docs/dev/decisions.md` D26's "a version bump is a re-measurement
   event" applied to data.

2. **`PROVENANCE.md` NAMES WHAT DERIVES FROM THE SOURCE**, not only where the
   source came from. That is the direction a maintainer actually needs (*"this
   table looks wrong — what produced it, and from what?"*) and the direction a
   licence audit needs. Nothing but a human reads it.

Each source directory therefore holds: the vendored files UNMODIFIED, a
`PROVENANCE.md`, and a `generate.py` — the generator lives WITH its source so
that the file naming what derives from the data and the file doing the
deriving cannot drift apart.

## What is deliberately NOT here

**PCRE2's testdata.** `utf8_design.md` §3.3.2 says this directory should
"retro-fit" it into the same shape; MEASURED 2026-09-06, **this repository has
never vendored PCRE2 testdata at all** — there is no `third_party/` before
this change and no `*testdata*` anywhere in the tree. The design's sentence
describes a repository state that does not exist. Recorded here rather than
silently dropped, because the retro-fit was one of the ruling's stated
obligations and a future reader will look for it.

**Anything a generated artifact carries.** Nothing in here reaches a user's
compiled matcher. The Unicode tables are compile-time data inside
`libpcrec.a`; an artifact carries the LOWERED AUTOMATON, which is a machine
over bytes and holds no property data at all. The one future exception is
named in advance: `utf8_design.md` §4.6(b)'s caseless-backreference fold
table, which folds at MATCH time and so cannot fold away at compile time
([M5.0] stage 4's territory, not shipped here).
