# Features and modules

pcrec supports the base PCRE grammar plus a growing set of the wider PCRE
construct family — named groups, assertions and lookaround, atomic groups
and possessive quantifiers, backreferences, recursion, Unicode
properties, `(*VERB)`s, and more. Each of these lives behind a **module**
you turn on explicitly. This is a deliberate design choice, not a
limitation to work around: an unsupported construct always refuses
cleanly, naming the module that would add it, and never miscompiles.

## `--features`

```sh
build/pcrec -o out.c --pattern '(?<=a)b' --features lookaround
```

`--features` takes a comma-separated list of module names, or one of
three special values:

- `std1` — a small, frozen default set (this is what a bare `pcrec`
  invocation with no `--features` flag uses).
- `all` — every module this build ships.
- `none` — base grammar only.

If a pattern needs a module you haven't enabled, pcrec refuses with
`requires module 'X'`, naming the module — never a cryptic parse failure.
That message is a complete, permanent answer under pcrec's compatibility
standard: it tells you exactly what to add, even when the module isn't
built yet (in which case adding it to `--features` won't help — check
whether it's shipped, next).

**In your own program, via the library**, this is `pcrec_options.features`
— same vocabulary, same three special values, but with a NULL default
that means something different from the CLI's bare default. See
[using the library](using-the-library.md) for that trap.

## What's shipped vs planned

Not every module PCRE2 has an equivalent for has a producer in pcrec
yet. To find out what's actually built:

```sh
build/pcrec --list-syntax
```

prints a machine-readable table of every construct pcrec's registry
knows about, with a `built` column. The human-readable version of the
same information, organized by PCRE2's own syntax reference and kept in
sync with the compiler so it can't drift, is
[`docs/pcre2_compliance.md`](../pcre2_compliance.md) — start there if
you want to know "does pcrec support X" for a specific piece of syntax
rather than reading a registry dump.

## Ask pcrec about one construct

```sh
build/pcrec --explain '\p{L}'
```

tells you which module owns a piece of syntax, whether it's built, and
what pcrec's parser actually does when it sees it — a quick way to check
a single construct without digging through the compliance page. `--list-syntax`,
`--list-verbs`, `--list-definitions`, and friends are the other built-in
reference surfaces; `docs/spec/cli.md` §2 documents each one.

## The compatibility standard, in one paragraph

PCRE2 is the source of truth for what a construct means and whether it's
real — not a byte-for-byte target pcrec must reproduce. What a pattern
**matches**, and whether a construct is real PCRE2 syntax naming the
right module, are exact claims. The exact **wording** of a diagnostic for
something pcrec hasn't built yet is not promised — `requires module 'X'`
discharges that in full. If a message's exact phrasing surprises you,
that's expected; if pcrec matches something incorrectly, or claims a
construct doesn't exist when it does, that's a real bug — see
[troubleshooting](troubleshooting.md) for where to report it.

## Next

- What happens when a pattern compiles but is expensive or huge:
  [tuning and limits](tuning-and-limits.md).
- Reading a refusal you didn't expect: [troubleshooting](troubleshooting.md).
