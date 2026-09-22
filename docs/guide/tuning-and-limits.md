# Tuning and limits

pcrec's defaults are chosen to be reasonable for most patterns without
any tuning. This chapter covers the levers available when a default
doesn't fit, and the limits you might actually hit.

## `--tune=N` — the speed/size dial

```sh
build/pcrec -o out.c --pattern '...' --tune=speed
```

`--tune` takes an ordinal from `-2` to `+2` (or a mnemonic alias:
`min-size`, `size`, `balanced` (the default, `0`), `speed`, `max-speed`)
and moves a single dial across several optimization decisions at once —
size-leaning positions favor a smaller artifact, speed-leaning positions
favor a faster one. Every position answers **identically**: `--tune`
never changes what a pattern matches or whether it's accepted, only how
much size or speed pcrec spends getting there. The exact policy table is
pinned in [`docs/spec/tuning.md`](../spec/tuning.md) §5 and changes only
by a deliberate, documented ruling — never silently as measurements come
in — so a given `--tune` value keeps meaning the same thing across
releases.

If you set an explicit `-f`/`-fno-` flag (below) on an axis the dial also
touches, your explicit flag wins.

## The `-f`/`-fno-` flag family

A larger family of individual optimization switches exists
(`-fno-possessify`, `-fno-prefilter`, and others) for finer control than
the dial gives you, or for testing and diagnosis. Most don't appear in
`--help` — they're a tuning and testing surface, not top-level features —
and the full roster with what each one does lives in
[`docs/spec/tuning.md`](../spec/tuning.md); this guide doesn't
reproduce the list because it changes more often than this page should.

## `--engine`

`--engine=dfa|vm|auto` (default `auto`) picks the matching strategy.
`auto` chooses per-pattern and only falls back to the backtracking VM
when a pattern actually needs it (captures, backreferences, or
constructs the pure DFA can't express). `dfa` and `vm` are explicit
requests: if the pattern can't be honored that way, pcrec **refuses**
rather than silently doing something else — you always know which
engine you got.

## Limits a caller can hit, and the remedy

| you hit… | means | fix |
|---|---|---|
| a compile-time refusal citing a state or element count | the pattern is too complex to build under the DFA/subset-construction budgets | `--engine=vm`, or raise the specific `--max-*` flag `--list-limits` names |
| an emitted-size refusal | the generated C would exceed pcrec's size ceiling | see below |
| `PCREC_ERR_STEPS` / `_WORK` at run time | the VM's backtracking/work budget ran out on this subject | `--step-budget=N` / `--work-budget=N`, or accept the give-up as a real answer for a hostile subject |
| `PCREC_ERR_FRAMES` at run time | the recursion/backtrack depth ceiling was reached | supply your own buffer via the `_in` entries (see [using the matcher from C](using-the-matcher-from-c.md)) |

`build/pcrec --list-limits` prints every numeric limit pcrec enforces,
its default, and how (if at all) to override it — that's the
authoritative, current list; this table is only the shape of the
categories.

### Emitted-size refusals

pcrec bounds how large a piece of generated C it will write, as a
failsafe rather than a routine constraint — almost nothing in pcrec's own
test corpus comes close to either limit. If you hit one anyway, pcrec has
already tried dropping anything optional the artifact didn't strictly
need and retried before refusing, so a refusal means that wasn't enough.
In rough order of what to try:

1. **Raise the limit** (`--max-emit-bytes=N` / `--max-emit-code-bytes=N`)
   if the size itself is fine. For a real build, put the override in the
   `.rxt` source's `config` block rather than on the command line, so it
   travels with the pattern.
2. **Force a smaller unroll factor** (`--unroll=1`) if the pattern
   replicates a large bounded repeat — this is the biggest single lever
   for that shape, at a small runtime cost.
3. **Change the engine** — `--no-captures`/`--engine=dfa` drops the VM
   body; `--engine=vm` drops the DFA prefilter — where either is most of
   the size.
4. **Split or rewrite the pattern.** Nested repetition counts multiply,
   so a count inside a nest costs far more than the same count at the top
   level.

`--warn-emit-bytes=N` gives you a non-fatal heads-up before you hit a
hard refusal, on an artifact that's getting large but still compiles.
Full detail, including how to read the stamps that say which term
produced the bytes: [`docs/spec/limits.md`](../spec/limits.md) §8.

### The recursion depth ceiling, worked

A generated matcher never allocates — its backtracking storage is a
fixed-size stack frame, sized at compile time. That gives every
recursive or deeply backtracking pattern a hard depth ceiling, expressed
as a subject **size** rather than a count, and it can be smaller than
you'd expect: a default build of `^(a(?1)?b)$` matches subjects up to
684 bytes and gives up (`PCREC_ERR_FRAMES`) at 686. That's not a bug —
it's the trade for a guarantee libpcre2 doesn't give you: the same
pattern refuses a runaway, non-matching input in constant time, where a
general backtracking engine can spend seconds or minutes on one. The
remedy is the caller-provided buffer entries (`_search_in` and friends,
covered in [using the matcher from C](using-the-matcher-from-c.md)) — a
caller who supplies its own, larger storage can raise this ceiling as
far as it's willing to reserve. This matters most on a small-stack
thread (musl's 128 KB default is the documented case): the default
entries are sized to fit comfortably there for ordinary matches, but a
deep escalation on such a thread needs the `_in` form to get a
guarantee rather than very good odds.

## Next

- What a give-up or a refusal actually returns, and how to tell the
  three separate small-integer vocabularies apart:
  [troubleshooting](troubleshooting.md).
