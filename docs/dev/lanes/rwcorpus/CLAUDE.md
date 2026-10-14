# rwcorpus/ — real-world subject corpus: fetch + manifest ([REGIME-CORPUS] step 1)

Lane `rwcorpus` (2026-10-13). The committed deliverable is the RECIPE, never
the bytes: the corpus lives in `worktrees/.corpus/` (gitignored, sibling of
the worktrees; `CORPUS=` overrides). Nothing copyrighted is committed.

- `sources.tsv` — every raw download: class, path under the class dir, URL, license, retrieval date (hand-maintained).
- `fetch.sh` — sequential, `gnutimeout`-bounded download of what is missing, then `prep.py`, then `manifest.py --check`; `--write-manifest` re-pins.
- `prep.py` — derives subject files from the raw archives (tar/zip READ only, nothing executed): concatenations, 40 MiB caps at line boundaries, scrubbing (IPv4 -> hashed 10.x.y.z, e-mails, rhost=/user=, ftpd reverse-DNS) for logs/code/markup/structured. Run as `python3 -I`.
- `manifest.py` — builds / checks `manifest.tsv` (class, file, bytes, sha256, url, license, date). Rows marked VOLATILE (USGS feeds) only warn on drift.
- `manifest.tsv` — the pin: raw rows (URL) + derived rows ("derived by prep.py from ...").
- `shape.py` — per-file shape facts (feeds `../rwcorpus_report.md`).
- `PROVENANCE.md` — licensing basis, PII handling, what was skipped.

Downloads are untrusted data. This directory writes no pattern or question:
a separate blinded agent does that (plan row [REGIME-CORPUS]).
