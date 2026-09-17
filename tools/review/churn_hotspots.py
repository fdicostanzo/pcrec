#!/usr/bin/env python3
"""
churn_hotspots.py -- git-log-derived churn x current size, the hotspot
join (docs/dev/reviews/code_review_criteria_draft.md, "Metric artifacts":
"churn x size hotspots (git)").

Usage:
    python3 tools/review/churn_hotspots.py [--out PATH]

For every .c/.h file in the PRIMARY tier (src/, cli/, lib/), this runs
`git log --follow --numstat` ONE FILE AT A TIME (54 files -- cheap; see
runtime note below) and reports:
    file  current_lines  touch_count  lines_added  lines_removed
    total_churn  hotspot_score
`touch_count` is the number of commits that touched the file (through
renames, via --follow); `total_churn` = lines_added + lines_removed
summed across all of history; `hotspot_score` = touch_count *
current_lines -- the classic "how often does this change" x "how much is
there to get wrong" formula (Tornhill's hotspot heuristic). This is ONE
reasonable weighting, stated explicitly rather than presented as the
only one: `total_churn` is reported alongside so a reader who wants
churn-VOLUME-weighted hotspots instead of touch-FREQUENCY-weighted ones
can recompute `total_churn * current_lines` from the same row without
re-running git.

Why per-file `--follow` rather than one repo-wide `git log --numstat`
pass attributed after the fact: this codebase's files have been renamed
across the project's history (module splits, the [M5-SEAM] encoding
split, etc.), and attributing a single repo-wide numstat stream back to
a file's CURRENT path correctly through renames is exactly what
`--follow` already does per-path; reimplementing that attribution by
hand from a single combined log risks getting a rename wrong silently.
54 separate `git log` invocations is not a performance concern for a
one-shot, local, non-CI metrics script (see the runtime line the script
prints to stderr).

VALIDATION (hand-checked 2026-09-17): cross-checked `src/gen/emit_vm.c`
(the largest primary-tier file, touch_count=140) and `src/core/arena.c`
(one of the smallest, touch_count=2) against `git log --follow --oneline
-- <path> | wc -l` run by hand -- EXACT match on both. A first check
against plain `git log --oneline` (no `--follow`) gave a DIFFERENT number
for emit_vm.c (142, not 140) -- not a script bug: rename-following
changes which commits attribute to a path, and the discrepancy
disappeared entirely once the manual check used the identical
`--follow` flag the script itself uses. Recorded here because it is the
kind of mismatch that looks like a script defect until the comparison is
made apples-to-apples. Also spot-checked that `current_lines` for
emit_vm.c matches `wc -l src/gen/emit_vm.c` exactly.
"""
from __future__ import annotations

import argparse
import datetime
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reviewlib as rl  # noqa: E402


def file_churn(relpath: str, root: Path) -> tuple[int, int, int]:
    cmd = ["git", "log", "--follow", "--numstat", "--pretty=format:@@COMMIT@@", "--", relpath]
    out = subprocess.run(
        cmd, cwd=root, capture_output=True, text=True, timeout=60, check=True
    )
    touches = 0
    added = 0
    removed = 0
    for line in out.stdout.splitlines():
        if line == "@@COMMIT@@":
            touches += 1
            continue
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0] != "-" and parts[1] != "-":
            try:
                added += int(parts[0])
                removed += int(parts[1])
            except ValueError:
                pass
    return touches, added, removed


def collect() -> list[tuple]:
    rows = []
    root = rl.REPO_ROOT
    for path in rl.iter_source_files():
        relpath = rl.rel(path)
        text = path.read_text(encoding="utf-8", errors="replace")
        current_lines = text.count("\n") + (0 if text.endswith("\n") else 1)
        touches, added, removed = file_churn(relpath, root)
        total_churn = added + removed
        hotspot = touches * current_lines
        rows.append((relpath, current_lines, touches, added, removed, total_churn, hotspot))
    rows.sort(key=lambda r: -r[6])
    return rows


def write_tsv(rows, out_path: Path):
    date = datetime.date.today().isoformat()
    header = rl.tsv_header("churn_hotspots.py", date, len(rows))
    with out_path.open("w", encoding="utf-8") as f:
        f.write(header)
        f.write(
            "\t".join(
                ["file", "current_lines", "touch_count", "lines_added",
                 "lines_removed", "total_churn", "hotspot_score"]
            )
            + "\n"
        )
        for row in rows:
            f.write("\t".join(str(x) for x in row) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out", default=str(rl.REPO_ROOT / "tools/review/out/churn_hotspots.tsv")
    )
    args = ap.parse_args()
    t0 = time.time()
    rows = collect()
    elapsed = time.time() - t0
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_tsv(rows, out_path)
    print(
        f"churn_hotspots: {len(rows)} files, {elapsed:.1f}s wall "
        f"(git log --follow per file), written to {out_path}",
        file=sys.stderr,
    )
    if rows:
        top = rows[0]
        print(f"  top hotspot: {top[0]} (score={top[6]})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
