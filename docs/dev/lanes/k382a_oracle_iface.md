# K38-2a: the occurrence-oracle interface (kit manager, 2026-11-10)

The hand-off between the generator lane (k382a, which drives the kit's run part)
and the D27 oracle author (k382o, who writes the oracle from the CONTRACT TEXT
alone: span_runs_sheet.md §3.3 items 1-4, integration.md §14.7). Neither side
reads the other's code; this file is the whole seam.

## The record: one TSV row per call of a run part

Tab-separated, one header line `#site\tcall\tsubject\torigin\tomin\tsets\tver_lo\tver_len\tresult\treads`, then rows:

| column | meaning |
|---|---|
| site | an opaque id for the generated site (string, no tabs) |
| call | `entry` or `reentry` |
| subject | the whole subject, lowercase hex, two digits per byte (may be empty) |
| origin | the attempt start (entry: search_from; re-entry: the hook's lo), a decimal integer >= 0 |
| omin | the run span's omin, a signed decimal integer (may be negative) |
| sets | the run's position sets, comma-separated, position 0 first; each set is 64 lowercase hex digits = a 256-bit byte bitmap, bit b of the set (byte b member) at hex digit 63 - b/4, bit b%4 of that digit (i.e. the bitmap as one big-endian 256-bit number) |
| ver_lo, ver_len | the verified extent the kit reported for this site (decimal, ver_lo + ver_len <= number of sets) |
| result | the candidate c the run part yielded (decimal, the subject offset of the run's position 0), or `MISS` |
| reads | every subject offset the run part read during this call, comma-separated decimals (may be empty) |

A run of n positions has its position j at subject offset c + j.

## What the oracle checks (from the contract text, not from this file)

The oracle reads rows from stdin or a file and prints one line per violated row
(`VIOLATION <item> <site> <call> <detail>`), then a trailer
`oracle: rows=R violations=V`, exit 0 iff V is 0. It must refuse (exit 2, a
message) a malformed row rather than skip it, and count every row it checks.
