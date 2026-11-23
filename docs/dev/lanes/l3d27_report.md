# l3d27: blinded D27 witnesses for lookaround unit L3 (lookbehind bytes in the required run)

## Summary

- **136 witnesses** (A join 81, B dead 26, C controls 29), 142 witness x encoding records, 453 pcrec
  compiles (default `--engine=auto`, `--engine=vm` and `--engine=vm -fprefilter` on every record;
  `--engine=dfa` too wherever pcrec accepts it, which was 27 records), **1,180,820 single searches**
  compared against libpcre2-8.
- **Answers: 0 disagreements with PCRE2.** Every search at every start position, over every subject
  and every config, gave the span PCRE2 gives. No give-ups, no compile refusals outside `--engine=dfa`.
- **Soundness: 0 violations.** Every listed run, `req_byte` and `req_set_maxoff` entry was checked
  against every PCRE2 match. No pattern is listed `dead` and still matches.
- **Spec worked examples (4.1.2¶8): all hold**, under every config they name.
- **Listing findings: 4 limits, 2 info.** None of them is unsound. All of them are on the
  `--engine=vm` route. They are F1-F6 under "Listing findings" below.
- Oracle: **libpcre2-8 10.46 2025-08-27** (system `/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0`,
  via python3 ctypes).

## Answers

The method, for each witness and encoding:

1. Build the subjects: the hand subjects, each one wrapped `Z…Z`, the empty subject, and all the
   hand subjects joined by `.`.
2. Ask PCRE2 for `pcre2_match` at **every start position** 0..n (every character boundary under
   utf8). That covers find-all, and also every case where the lookbehind's bytes sit **before the
   start offset**: for example `(?<=foo)bar` over `foobar` from startpos 1, 2 and 3, all `[3,6)`.
   The options are `PCRE2_CASELESS` for `-i`, and `PCRE2_UTF|PCRE2_UCP` for `-e utf8`.
3. Compile with `build/pcrec --features <list> [-i] [-e utf8] <config> -p rx -o out.c`. Link the
   output into a small driver of my own that calls `rx_search(s, n, p, caps)` at the same start
   positions. Compare the return value and `caps[0]`.

Extra subject sets:

- **Exhaustive sets** (A60-A77, C40-C42, B40): every string up to length 5-8 over 2-4 letters. These
  hit self-overlapping and periodic runs (`(?<=ab)ab`, `(?<=aa)aab`, `(?<=aba)ba`) and every
  start-offset placement.
- **Long subjects** (A80-A86): padding of 37, 300 and 1500 bytes, near misses repeated 30 times, and
  matches after long runs of near misses. These exercise the handoff's scan over distance at a
  negative K.

Result: **0 disagreements in 1,180,820 searches** (def 142 records, vm 142, vmpf 142, dfa 27).

The `.rxt` file holds a selection of these cases: an `m`/`n` per subject at offset 0, `ms`/`ns` at
each start position where the answer changes or where a match begins exactly at the start position,
and one `mc` over the joined subject. An exhaustive witness keeps 40 matching and 20 non-matching
subjects. Every block appears twice, once under the default engine and once with `engine vm`. That
is 284 blocks and 13,722 case lines. Long-subject witnesses keep only subjects up to 700 bytes in
the file, and their 1500-byte runs stay in the harness. A second, independent script re-read the file and checked
every case line against libpcre2-8: 0 bad. `pcrec --list-source` parses the file (exit 0).

## Soundness

For each PCRE2 match `[s,e)` with attempt start `a`, and a listed `req_whole_run` R with K =
`req_landmark_maxoff`, R must occur at some `q` with `q + |R| <= e` and `q <= a + K` where K is
numeric. The lower bound depends on K:

- K is negative: `q >= a - LB`, where LB is the witness's declared lookbehind length in bytes. This
  is ¶8: "may BEGIN before the attempt start, inside a positive lookbehind, by at most the
  lookbehind's declared length".
- Otherwise: `q >= a`. The run lies inside the match.

Masked runs and bracketed-class runs were expanded to byte sets.

For `\K` witnesses, the attempt start is the start of the same pattern's match with `\K` removed (at
the same start position), because `\K` does not move the attempt start.

Other checks:

- `req_byte` must occur in `[a, e)`, because it reads only consumed positions.
- Each `req_set_maxoff` member `b:K` must occur at offset `<= K`, before `a` only when K is negative.
- `dead` must mean that PCRE2 finds no match anywhere.

I tested the checker by sabotage: fake listings such as `62617a`@0, a negative `req_set` offset and
a false `dead` were all caught. Result: **0 violations** over all 453 listings.

## Listing findings

None of these is an answer or soundness problem. "LIMIT" means less is joined than the general rule
of ¶8 allows. "INFO" means more is joined than the brief expected, and the join is sound.

- **F1 LIMIT: a run is clipped to 32 positions, and with a long lookbehind it keeps none of the
  consumed bytes (A35, A84).** For `(?<=abcdefghijklmnopqrstuvwxyz0123456789)!` (36 bytes) the vm
  listing is the lookbehind's last 32 bytes at K `-32`, without `!`. Probes show the rule: K is
  clamped at `-32` and the run is the 32 positions from there.
  - With a 33-byte or longer lookbehind, no consumed position survives, even when the consumed part
    has its own run: `(?<=<40 bytes>)ABCDEFGHIJ` lists 32 lookbehind bytes at K `-32` under vm,
    while the default lists `4142…4a`@0.
  - A plain 40-byte literal lists its first 32 bytes, so the cap itself is general and not L3's.
  - The spec states a 24/32 cap for `run_pin` and `req_pieces`, but none for `req_whole_run`.
- **F2 LIMIT: the meet of two lookbehinds does not narrow a wide position (A15).** `(?<=.b)(?<=a.)cd`
  lists `626364`@-1 under vm. The meet `ab` would give `61626364`@-2. `(?<=a.)cd` alone joins
  nothing (`6364`@0), while `(?<=.b)cd` joins `b`. Two lookbehinds that agree byte for byte do meet:
  `(?<=ab)(?<=b)cd` and `(?<=ab)(?<=a.)c` both join. This looks like L1's recorded limit (a wide class
  in a lookbehind body is dropped), now reached through a meet.
- **F3 LIMIT: a lookbehind nested at the START of a lookbehind body blocks the whole item (A17).**
  `(?<=(?<=x)ab)cd` lists `6364`@0 under vm: not even the outer `ab` joins. Likewise
  `(?<=(?<=x)a)b` lists no run. Nested at the END, it joins: `(?<=a(?<=a))bc` gives `616263`@-1 and
  `(?<=x(?<=x))ab` gives `786162`@-1. L1 recorded the lookahead analogue, a lookbehind nested in a
  lookahead.
- **F4 LIMIT: a one-character CLASS lookbehind before a single consumed byte is not joined (A45).**
  `(?<=a|b)c` and `(?<=[ab])c` list no run under vm (landmark `c`@0), and so does the one-cube
  `(?<=[ac])b`. With two consumed bytes it joins: `(?<=[ab])cd` gives `[6162]6364`@-1. A one-BYTE
  lookbehind joins either way: `(?<=a)b` gives `6162`@-1. Possibly a deliberate choice (a class
  position may be too weak to prefer over a single byte), but the spec does not state it.
- **F5 INFO: a variable-length alternation body joins its common-width tail (C03).** `(?<=ab|cde)f`
  lists `[6164][6265]66`@-2 under vm: the last two bytes of each branch, unioned by position. This is
  sound (exhaustively checked), and the spec does not forbid it. The brief expected controls of this
  kind to join nothing. `(?<=a|bc)d` (C04) joins nothing.
- **F6 INFO: a capturing body joins (C05).** `(?<=(foo))bar` lists `666f6f626172`@-3 under vm. This is
  sound and the spec says nothing either way. The brief expected no join.

Observations that are not findings:

- **The default route follows ¶8's re-entry rule exactly.** It joins only where the consumed run is
  empty (`(?<=foo)`, `(?<=ab)a*`) or unbounded with a kept consumed position (`(?<=xyz)a+xyz`,
  `(?<=ab)a+b`). It declines where the lookbehind's run keeps no consumed position:
  `(?<=ab)x*cd` lists `6364`@unbounded.
- **`-fprefilter` under vm lists the consumed run, as ¶8 says.**
- **A lookbehind in the middle of a pattern that reaches before the attempt joins, soundly.**
  `a(?<=ba)b` lists `626162`@-1 (C41, exhaustive).
- **`never_matches` reads `no` on every B witness, the DFA-engine ones included** (`(?<=a)(?<=b)c`
  under auto is a DFA artifact). It is one-sided by its spec, and it is independent of `dead`.
- **A one-byte lookbehind alone, `(?<=a)` (A52), lists nothing.** This is consistent with ¶8, which
  does not list runs shorter than two bytes. I first wrote the claim the other way and corrected it.
  The listing was right.

## Witnesses

The full table is `l3d27_listing.tsv`: one row per witness x encoding x config, with the claim, the
listing (run, K, why, req_set_maxoff, engine, prefilter), the PCRE2 match count, the number of
searches, the answer disagreements, soundness and status. Statuses over 453 rows: 447 PASS, 4 LIMIT,
2 INFO, 0 FAIL.

What the groups cover:

- **A (join, 81 witnesses).**
  - The spec examples, A01-A05.
  - `-i` (A07, A51, A56, A71, A77), and inline `(?i)` only in the body or only after it (A08, A09).
  - utf8: two- and three-byte characters (A10, A11, A49, A72, A83), and utf8 `-i` (A12, A56).
  - Raw bytes (A34), and a 36-byte lookbehind (A35, A84).
  - Nesting (A16, A17, A47).
  - Two lookbehinds at one point (A13-A15, A70).
  - A lookbehind after a group, or in a group's body (A18-A20).
  - `\K` in each place (A21-A23, A67).
  - Atomic groups, outside, inside the body and around the consumed part (A24-A27, A74).
  - A lookbehind on one branch only (A28, A29, A69), and on both branches (A30, A68).
  - Classes and alternations in the body (A31, A32, A45, A46, A50).
  - Optional, variable and repeated consumed parts (A36-A39, A54, A64-A66).
  - `\b` and `^` in the body (A40, A44), a lookahead beside it (A41, A73), and a trailing,
    overlapping lookbehind (A42, A43, A76).
  - The exhaustive stress set A60-A77, and the long-subject set A80-A86.
- **B (dead, 26 witnesses).** Two lookbehinds contradicting each other, and a lookbehind
  contradicting the consumed bytes before or after it. Variants: `-i` (B07, B21, B23, and B25, the
  byte-encoding twin of C24), utf8 (B08, B15), a class (B09, B10), an empty byte class (B16), nesting
  (B11), atomic (B12), a repeat taken at least once (B19), after a capturing group (B20), and one
  exhaustive witness (B40). **All 26 are listed `dead` under every config, and PCRE2 matches none of
  them.**
- **C (controls, 29 witnesses).** Negative lookbehinds (C01, C02, C26, C40), variable-length bodies
  (C03, C04, C08, C27), a capturing body (C05), and a lookbehind after a variable or nullable part
  (C06, C07, C42). Also: optional and `{0}` lookbehinds (C09, C10, C16, C21); a contradiction on one
  branch, under a zero-count repeat, inside a negative assertion or in an optional group (C14, C15,
  C17, C20, C23); `-i` agreeing cases (C18, C24); and a lookahead-only control (C12). **None is
  falsely `dead`. No negative K appears outside the two INFO joins, F5 and F6.**

## Spawn-time disclosure

What I received at spawn:

- The global user `~/.claude/CLAUDE.md` (security rules).
- The project root `CLAUDE.md` of the main tree, in full. It covers the situation index, the
  conventions and the D27 cell rule, and it names `docs/dev/lanes/BOILERPLATE.md`.
- The memory index `MEMORY.md`: about 115 one-line entries on process and project preferences, none
  about L3's code.
- A git-status snapshot of the main tree: branch main, the names of untracked lane deliver files
  (`k146merge`, `k147land`, `land1115d`, `land1116`, `landarch`, `revfile`), and the subjects of the
  last five commits (D201, review r67 k152, K153).
- The names of the other agents in the session (among them `l3feat`, `l3fix`, `l3chk`, `l3enc`,
  `l3tri`, `crit-l3feat`).
- The manager's brief.

What I opened inside the cell: the four spec and design files the brief named, and `build/pcrec`'s
own output (`--help`, `--list-syntax`, `--emit-facts`, generated C).

`REQ-LOOKAROUND.md` (in the cell) carries the L1 landing's summary of L1's D27 listing limits. I read
it and cite it for F2 and F3.

What I touched outside the cell:

- The system libpcre2-8, gcc and python3.
- My scratch directory `/var/tmp/pcrec-pcrec/scratch/l3d27/`.
- A hook's error text, which named `scripts/hooks/no_cd_worktree.sh` (name only).

The cell holds a `.git` directory (timestamp 01:26, one minute after the cell; `ls -a`). I did not
create it, did not open it, and ran no git command.

What I did NOT open: `docs/dev/lanes/BOILERPLATE.md`. It sits outside the cell, and the blinding rule
took precedence. I also opened nothing in `src/`, `tests/`, any other doc, any worktree, the git
history, or any lane report or review.

## STATE AT HANDOFF

**Delivered.** These three files are in the cell:

- `l3d27_witnesses.rxt` (284 blocks, oracle `pcre2/10.46`, parsed by `pcrec --list-source`).
- `l3d27_listing.tsv` (453 rows).
- This report.

The reproduction scripts are in `/var/tmp/pcrec-pcrec/scratch/l3d27/` (not in the cell):

- `run.py`: the PCRE2 bindings and the run parser.
- `wit.py`: the witnesses and their claims.
- `main.py`: runs everything and writes `results.json`.
- `gen.py`: writes the `.rxt` and the TSV.
- `verify_rxt.py`: the independent re-check of the `.rxt`.
- `driver.c`.

`python3 main.py && python3 gen.py` reruns everything in about 16 s.
