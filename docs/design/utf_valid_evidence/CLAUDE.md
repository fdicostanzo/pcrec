# docs/design/utf_valid_evidence/ — [UTF-VALID] design note's evidence

Reproduction pieces for `../utf_valid_design.md` (lane k73utf, 2026-09-29).
Text and C sources only; there are no binaries.

- `pr4.c`, `utfcheck_10.46.txt`: the libpcre2 10.46 probe (PCRE2_UTF,
  checking ON) and its transcript. They are §1's contract measurement: the
  checked range is `[startoffset − maxlookbehind, n)`, and the error offset
  is the first ill-formed sequence's first byte. Light probe on ubuntubudu.
- `utfcheck_bench.c`, `bench_run1.txt`, `bench_run2.txt`: §5's validator
  cost (bytewise, ASCII-fast-path and byte-class-DFA strict validators,
  plus memchr/bytesum references) over three 64 MiB subjects. Two runs,
  darwin, directional only. The self-check pins each validator's
  first-bad offset to libpcre2's.
- `scanbench.c`, `scan_ref.txt`: §5's pcrec reference rates (three `-e
  utf8` artifacts timed on the same ASCII subject).
