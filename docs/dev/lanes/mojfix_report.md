# mojfix — O-31 finding F4 (raw high-byte literals in pattern text)

**Verdict: NOT A PCREC DEFECT.** No `src/`, `tests/`, or `docs/spec/`
change in this delivery. Root cause isolated to `pcrec-bench`'s own
`testees/pcrec/adapter.py:2961` (read-only to this lane per the scope
mandate) — reported here for the manager to relay via
`inbox_from_pcrec.md`, not fixed by this lane.

## The brief's premise, and why it does not hold

The brief (bench's `2026-09-17-mojibake-span-probe-a770139e.txt`)
characterized F4 as: pattern `\x93[\x20-\x7e]*\x94` with `\x93`/`\x94`
as RAW bytes (authored `pattern-esc "\x93[\\x20-\\x7e]*\x94"` in
`bench/capability/patterns.rxt:810`) answers NOMATCH on all four pcrec
configs (auto-caps, auto-nocaps, vm-caps, vm-in-caps) against subject
`\x93hello\x94`, both engine routes, where PCRE2 and python3 `re` both
match `[0,7)`. That pointed at pcrec's own pattern-ingestion path
(lexer/parser signedness, or a byte-vs-UTF-8 decode confusion).

## Reproduction: pcrec itself is correct on every axis tried

Oracle-confirmed first: `python3 -c "import re; re.search(b'\x93[\x20-\x7e]*\x94', b'\x93hello\x94')"`
→ match `(0, 7)`.

Built `lane/mojfix` at `make -j2 CC=gcc-16` (darwin/arm64, default
`char` UNSIGNED there). Constructed the exact pattern TEXT the .rxt
line decodes to — raw byte `0x93`, literal `[\x20-\x7e]*` (single
backslash, for pcrec's own regex parser to decode as a class), raw
byte `0x94` — and compiled it with `--emit-main` across every engine
axis combination:

| axis | result |
|---|---|
| default (auto, captures on) | match 0 7 |
| `--no-captures` | match 0 7 |
| `--engine=vm` | match 0 7 |
| `--engine=vm --no-captures` | match 0 7 |
| `--engine=dfa` | match 0 7 |

All five correct. Suspecting an ARM-vs-x86 `char`-signedness masking
(darwin/arm64 defaults `char` unsigned; x86_64 Linux, the bench's own
box, defaults it signed — exactly the brief's "prime suspect"),
rebuilt pcrec itself with `-fsigned-char` forced (`make clean; make
CFLAGS='... -fsigned-char'`) and re-ran: still `match 0 7`, both with
the emitter and the emitted artifact compiled `-fsigned-char`.

Then did the same reproduction as a LIGHT PROBE (BOILERPLATE: light
probes only, transcripts archived, never a suite run) on the actual
reference box, using the bench's own PINNED binary at the exact pin
the finding was measured against —
`ssh duxevents@100.69.121.107`,
`/home/duxevents/pcrec-bench/build/pcrec-a770139e/build/pcrec` — with
the identical `--emit-main` CLI reproduction (raw-byte argv via bash
`$'...'`, single compile, single `gcc`, single run): **`match 0 7`.**
Real x86_64 Linux, real signed `char`, the exact pinned commit, the
exact pattern text. pcrec is right.

## What actually happens: pcrec-bench corrupts the pattern bytes before pcrec ever sees them

`testees/pcrec/adapter.py`'s `_compile_one` (the ONE method all four
pcrec configs go through — `Adapter.compile` calls it per form, and
every testee config shares this same compile path, which is exactly
why the finding is uniform across all four configs and both engine
routes) builds the compiler's argv at line 2961:

```python
argv = ([pcrec, "-p", "rx"] + list(cfg.get("flags", []))
        + ["-o", art_c, "--"] + [pattern.decode("latin-1")])
...
proc = subprocess.run(argv, capture_output=True, env=C_ENV, timeout=600)
```

`pattern` is a Python `bytes` object (`b'\x93[\x20-\x7e]*\x94'` for
this witness, coming out of `pcrecbench/rxt_source.py`'s own
`--list-source`-dump decoder). `.decode("latin-1")` turns every byte
`0x93`/`0x94` into the Python `str` codepoints U+0093/U+0094 — REGULAR
Unicode codepoints, not `surrogateescape` sentinels. CPython's POSIX
`subprocess` then re-encodes each `str` argv element back to bytes via
`os.fsencode` (the filesystem encoding, UTF-8 on this box, with
`surrogateescape` error handling). `surrogateescape` only round-trips
a byte that was ITSELF surrogateescape-decoded; a plain-Unicode
codepoint like U+0093 just gets normal UTF-8 encoding — **two bytes**,
`0xC2 0x93`. Verified directly (same box, same Python):

```
python str repr:                '\x93[\\x20-\\x7e]*\x94'
child argv via /proc/self/cmdline: ...\xc2\x93[\\x20-\\x7e]*\xc2\x94\x00
original pattern bytes:            \x93[\\x20-\\x7e]*\x94
```

So pcrec's CLI never receives `0x93`/`0x94` at all — it receives
`0xC2 0x93` / `0xC2 0x94` (the UTF-8 encoding of U+0093/U+0094, a
two-byte-per-original-byte inflation for every byte ≥ 0x80 in the
pattern). **pcrec then correctly compiles the pattern it was actually
handed.** Direct proof, same pinned binary:

```
$ pcrec -o moj_corrupt.c --emit-main -- $'\xc2\x93[\x20-\x7e]*\xc2\x94'
$ ./moj_corrupt $'\x93hello\x94'       # the INTENDED subject bytes
nomatch                                 # correct: pattern requires literal C2 93 lead
$ ./moj_corrupt $'\xc2\x93hello\xc2\x94'  # bytes matching what pcrec was actually told
match 0 9                               # correct
```

NOMATCH on the intended subject is the CORRECT answer to the pattern
pcrec was actually compiling. There is no defect in pattern ingestion,
lowering, or either engine route — the earlier full-axis reproduction
above already established every engine/capture combination is correct
on the RIGHT bytes; this closes the loop by showing pcrec is *also*
correct on the WRONG bytes it was actually given.

This is not a `.rxt`-format ambiguity either: `pcrecbench/rxt_source.py`
already gets the pattern bytes right (it round-trips `--list-source`'s
dump with `errors="surrogateescape"` specifically to survive raw high
bytes — its own module docstring explains why). The corruption is
introduced one layer later, at the `subprocess.run` argv boundary in
`testees/pcrec/adapter.py`, which the bench's probe never instrumented
because its "isolate to pattern ingestion" framing pointed at pcrec by
construction — the probe compared pcrec's OBSERVED BEHAVIOR against
pcre2's, not the ACTUAL BYTES each engine's adapter delivered.

## Recommendation (for pcrec-bench, not built here — read-only mandate)

Either of these round-trips raw bytes ≥ 0x80 correctly through
`subprocess`'s POSIX argv path (both verified directly on the bench's
own box):

- **(a)** pass `pattern` (the raw `bytes` object) directly in the
  `argv` list — CPython's `subprocess` accepts `bytes` argv elements
  on POSIX with no encode/decode step at all. Simplest fix, no round-trip
  to reason about.
- **(b)** if a `str` is required, decode with
  `pattern.decode("utf-8", errors="surrogateescape")` instead of
  `"latin-1"` — this is the ONE decode that inverts exactly what
  `os.fsencode`'s own `surrogateescape` re-encode does.

Filing this as the recommendation text for whichever channel carries
it back to pcrec-bench (`inbox_from_pcrec.md` or equivalent) — this
lane does not write to `pcrec-bench` per the scope mandate.

## Why this lane stops here

Per the brief's own item 5 ("if the diagnosis turns out architectural
... STOP after diagnosis and report — do not redesign") and the scope
mandate (pcrec-bench read-only): the located defect is not merely
architectural, it is not IN pcrec at all. There is nothing to fix, no
corpus population to check for blast radius (nothing in pcrec moved),
no `abi` event, no oracle-verification needed beyond what is already
above. Reclassifying F4 as a bench-harness defect, not a pcrec one, is
the deliverable.

## Validation

No `src/`/`tests/`/`docs/spec/` changes — nothing to validate against
the corpus. Confirmed the worktree still builds clean (`make -j2
CC=gcc-16`, exit 0) before and after the `-fsigned-char` probe build
(discarded, not committed). `git status --short` clean at delivery.
