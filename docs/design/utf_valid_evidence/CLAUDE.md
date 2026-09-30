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

Added by lane uvrev (2026-09-30), the revision against critic r2:

- `lb.c`, `lbpats.txt`, `cases.txt`, `cases2.txt`, `lb_10.46.txt`,
  `lb_10.48.txt`, `cases2_10.46.txt`: §1.2-§1.4's measurements. `lb.c`
  prints `PCRE2_INFO_MAXLOOKBEHIND` and the MEASURED step-back (the largest
  `startoffset` still refused on `\xff` + 10 × `z`) for each pattern in
  `lbpats.txt`. `cases*.txt` are `pr4.c` rows (`PATTERN|SUBJECT|START`,
  read with `read -r`): the K50-versus-check order, the raw step-back, and
  the `extent` examples. The 10.46 transcripts come from ubuntubudu (light
  compiles, temp dir removed). 10.48 (Mac) is identical on every shared row.
- `utfcheck_bench2.c`, `bench2_run1.txt`, `bench2_run2.txt`: §5's added
  cost rows. (A) is the sparse-non-ASCII subject. (B) is the per-call cost
  on 8 B-4 KiB subjects: the proposed `valid_upto` shape (a raw step-back
  plus the ASCII-fast-path validator, not inlined) against three pcrec
  `-e utf8` `_search` calls. The emit commands are in its header. The
  emitted p1/p2/p3 sources are not kept. Darwin, directional only.
