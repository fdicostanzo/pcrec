# docs/measurements — archived probe output reports (D35)

Full output of the design-measurement probes in `tests/probes/`, archived
verbatim with a source-information header (date, repo commit, libpcre2
version, gcc version). Written by `scripts/measure.sh <probe>`; never
hand-edited.

Why these exist (Frank, 2026-08-12): the probe SOURCES have always been
committed so quoted numbers are reproducible, but the raw outputs were
session-scratch — R18 noted the MOD-0.4 byte-identity sweep's evidence
survived only as prose. An archived report makes a re-measurement a `git
diff`: what changed under a new libpcre2 or a probe edit is visible in one
command.

Filenames are STABLE per probe (`<probe>.txt`, not dated) so that diff
works; the date is a header line and the history is git log.

Two rules:

- **A report is evidence, never an oracle.** No check may read these files;
  the live re-measured checks (tests/registry/) are the strong form, and a
  committed snapshot nobody re-runs is exactly the stale-record failure
  this project keeps finding. Reviews and design notes cite these reports;
  code does not.
- **Re-measure deliberately.** Regenerate a report when its probe changes,
  when the oracle version changes (a D26-addendum re-measurement event), or
  when a review needs current evidence — and commit the diff with a note on
  what moved and why. A drive-by regeneration with an unexplained diff is a
  finding, not housekeeping.

Reports present:

- `probe_quant.txt` — the §18.3 quantifiability determinism cells (also the
  convention's validation run, 2026-08-12).
- `probe_uprops.txt` — MOD-0.6's \p/\P measurement (archived at the
  milestone's merge; see tests/probes/CLAUDE.md's probe_uprops.c entry).

Maintenance: update this file when reports are added/removed.
