#!/usr/bin/env python3
"""
clone_candidates.py -- token-shingle winnowing clone detector over the
PRIMARY review tier (src/, cli/, lib/), function-granularity.

Usage:
    python3 tools/review/clone_candidates.py [--out PATH] [--k 20] [--w 8]

Method (Schleimer/Wilkerson/Aiken winnowing, the MOSS algorithm's core):
  1. Every function is walked with the SAME reviewlib.iter_top_level_headers
     boundary detector function_census.py uses, so a row here joins directly
     to a census row on (file, name, start_line, end_line) -- the charter's
     ADDENDUM 1 requirement ("the census and clone-candidate outputs share
     join keys ... so lens 11's over-N rows can be joined directly to lens
     1's extract candidates").
  2. Each function's body (masked: comments blanked, string/char literal
     INTERIORS blanked but the literal kept as one token) is tokenized;
     identifiers are normalized to a generic ID token (keywords kept as
     themselves), numeric literals to NUM, string/char literals to STR/CHR.
     This makes the detector TYPE-2-ish: it finds structural duplication
     (same control flow / call shape / operator sequence) independent of
     variable names and literal VALUES -- which is exactly the "separable
     semantic operation...repeated with variation" shape lens 1 is chartered
     to find (error paths, table emission, option plumbing with a differing
     constant or message string at each call site).
  3. Overlapping k-token shingles are hashed (blake2b, truncated -- stdlib,
     and deterministic across runs/machines, unlike Python's randomized
     str hash()) and WINNOWED: a sliding window of w hashes keeps only the
     minimum per window (ties keep the rightmost), giving each function a
     sparse fingerprint set. The winnowing guarantee: any shared token
     run of length >= k + w - 1 between two functions is caught by at
     least one common fingerprint. Defaults k=20, w=8 -> a guaranteed
     catch at 27 shared tokens, roughly 4-6 source lines in this codebase's
     density -- coarse enough to skip single-statement idioms, fine enough
     to catch a repeated error-path or table-emission block.
  4. Functions are paired via an inverted index (hash -> functions holding
     it) rather than all-pairs, then a pair is admitted as a CANDIDATE only
     if it shares >= PAIR_MIN_SHARED fingerprints AND that count is >=
     PAIR_MIN_FRAC of the SMALLER function's own fingerprint count (this
     is what keeps one large function from swallowing many small ones
     through generic boilerplate alone). Admitted pairs are then grouped
     into candidate clone GROUPS by connected components (union-find).

This tool finds STRUCTURAL similarity; it does NOT judge whether a shared
abstraction should be extracted -- that is lens 1's job, and per the
charter's admissibility rule A2, a lens-1 finding built on a row here
still needs the SHARED ABSTRACTION named (proposed signature, call sites,
what varies) before it is admissible. "These look similar" is not enough;
this script only says which functions are worth that closer look.

Output: tools/review/out/clone_candidates.tsv, one row per (group, member):
    group_id  group_size  file  function  start_line  end_line  code_lines
    shared_fingerprints  group_frac
`shared_fingerprints`/`group_frac` are THIS MEMBER's overlap with the rest
of its group (count and fraction of its own fingerprint set echoed
elsewhere in the group) -- a rough "how much of this function recurs
elsewhere" signal, not a symmetric pairwise score.

VALIDATION (hand-checked 2026-09-17): every group in the shipped output
was read by eye against the two members' source. The largest group is
the six `emit_predicate_axes`-family sibling functions in
src/parse/axes_dump.c / src/parse/limits_dump.c / src/parse/schema_dump.c
(one dump function per registry table -- header comment, a loop over the
table's rows, per-row field formatting, a closing summary line -- REAL
structural duplication, the exact "one dump function per table with no
shared spine" shape lens 2's own charter names as a seed finding). A
second group is the four `mod_*_LIMIT`-macro-driven per-limit dumper
callbacks (mod_backrefs.c/mod_recursion.c/mod_lookaround.c/rxt_source.c),
confirmed real by reading two members side by side.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import re
import sys
from collections import defaultdict, deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reviewlib as rl  # noqa: E402

MIN_CODE_LINES = 6
SHINGLE_K_DEFAULT = 20
WINNOW_W_DEFAULT = 8
PAIR_MIN_SHARED = 3
PAIR_MIN_FRAC = 0.25

_C_KEYWORDS = {
    "auto", "break", "case", "char", "const", "continue", "default", "do",
    "double", "else", "enum", "extern", "float", "for", "goto", "if",
    "inline", "int", "long", "register", "restrict", "return", "short",
    "signed", "sizeof", "static", "struct", "switch", "typedef", "union",
    "unsigned", "void", "volatile", "while", "_Bool", "_Complex",
    "_Imaginary",
}

_TOKEN_RE = re.compile(
    r"""
      "[^"]*"                      # (already comment/interior-blanked) string
    | '[^']*'                      # char literal
    | [A-Za-z_][A-Za-z0-9_]*       # identifier / keyword
    | 0[xX][0-9a-fA-F]+            # hex literal
    | \d+\.\d+([eE][+-]?\d+)?      # float literal
    | \d+                          # int literal
    | ->|\+\+|--|<<=?|>>=?|<=|>=|==|!=|&&|\|\||[+\-*/%&|^]=|::
    | [{}()\[\];,.:?~!<>=+\-*/%&|^]
    """,
    re.VERBOSE,
)


def tokenize(masked_slice: str) -> list[str]:
    out = []
    for m in _TOKEN_RE.finditer(masked_slice):
        t = m.group(0)
        if t.startswith('"'):
            out.append("STR")
        elif t.startswith("'"):
            out.append("CHR")
        elif t[0].isdigit():
            out.append("NUM")
        elif t[0].isalpha() or t[0] == "_":
            out.append(t if t in _C_KEYWORDS else "ID")
        else:
            out.append(t)
    return out


def stable_hash(shingle: tuple) -> int:
    h = hashlib.blake2b("\x1f".join(shingle).encode("utf-8"), digest_size=8)
    return int.from_bytes(h.digest(), "big")


def shingle_hashes(tokens: list[str], k: int) -> list[int]:
    if len(tokens) < k:
        return []
    return [stable_hash(tuple(tokens[i : i + k])) for i in range(len(tokens) - k + 1)]


def winnow(hashes: list[int], w: int) -> set[int]:
    n = len(hashes)
    if n == 0:
        return set()
    if n < w:
        return {min(hashes)}
    dq: deque[int] = deque()
    selected: list[int] = []
    prev_min_idx = -1
    for i in range(n):
        while dq and hashes[dq[-1]] >= hashes[i]:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - w:
            dq.popleft()
        if i >= w - 1:
            min_idx = dq[0]
            if min_idx != prev_min_idx:
                selected.append(hashes[min_idx])
                prev_min_idx = min_idx
    return set(selected)


class UnionFind:
    def __init__(self):
        self.parent: dict = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def collect_functions(k: int):
    """Same walk as function_census.py, so join keys match exactly."""
    entries = []  # (key, file, name, start, end, code_lines, fingerprints)
    for path in rl.iter_source_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        masked = rl.mask_text(text)
        line_of = rl.make_line_of(text)
        lines = masked.split("\n")
        relpath = rl.rel(path)
        offs = rl.newline_offsets(text)  # to slice masked text by char offset
        for kind, name, start, end, _depth, _header in rl.iter_top_level_headers(
            masked, line_of
        ):
            if kind != "func":
                continue
            code_lines = sum(
                1 for ln in range(start, end + 1)
                if ln - 1 < len(lines) and lines[ln - 1].strip()
            )
            if code_lines < MIN_CODE_LINES:
                continue
            start_off = offs[start - 1] + 1
            end_off = offs[end] if end < len(offs) else len(masked)
            body = masked[start_off:end_off]
            toks = tokenize(body)
            hashes = shingle_hashes(toks, k)
            entries.append((relpath, name, start, end, code_lines, hashes))
    return entries


def build_groups(entries, w: int):
    fps = []  # parallel to entries: fingerprint set
    hash_index = defaultdict(list)  # hash -> list of entry indices
    for idx, (_f, _n, _s, _e, _cl, hashes) in enumerate(entries):
        fp = winnow(hashes, w)
        fps.append(fp)
        for h in fp:
            hash_index[h].append(idx)

    pair_shared = defaultdict(int)
    for h, idxs in hash_index.items():
        if len(idxs) < 2:
            continue
        idxs = sorted(set(idxs))
        for i in range(len(idxs)):
            for j in range(i + 1, len(idxs)):
                pair_shared[(idxs[i], idxs[j])] += 1

    uf = UnionFind()
    admitted_pairs = []
    for (i, j), shared in pair_shared.items():
        smaller = min(len(fps[i]), len(fps[j])) or 1
        frac = shared / smaller
        if shared >= PAIR_MIN_SHARED and frac >= PAIR_MIN_FRAC:
            uf.union(i, j)
            admitted_pairs.append((i, j))

    groups = defaultdict(set)
    involved = {i for pair in admitted_pairs for i in pair}
    for i in involved:
        groups[uf.find(i)].add(i)

    # per-member overlap: fraction of this member's own fingerprints that
    # appear in the UNION of the rest of its group.
    rows = []
    group_list = sorted(groups.values(), key=lambda members: (-len(members),
                         -max(entries[m][4] for m in members)))
    for gid, members in enumerate(group_list, start=1):
        for m in sorted(members, key=lambda i: (entries[i][0], entries[i][2])):
            others_fp = set()
            for other in members:
                if other != m:
                    others_fp |= fps[other]
            own = fps[m]
            shared_n = len(own & others_fp)
            frac = shared_n / len(own) if own else 0.0
            f, n, s, e, cl, _h = entries[m]
            rows.append((gid, len(members), f, n, s, e, cl, shared_n, frac))
    return rows


def write_tsv(rows, out_path: Path, k: int, w: int):
    date = datetime.date.today().isoformat()
    header = rl.tsv_header(
        "clone_candidates.py", date, len(rows), extra=f"k={k} w={w}"
    )
    with out_path.open("w", encoding="utf-8") as f:
        f.write(header)
        f.write(
            "\t".join(
                ["group_id", "group_size", "file", "function", "start_line",
                 "end_line", "code_lines", "shared_fingerprints", "group_frac"]
            )
            + "\n"
        )
        for gid, gsize, file_, name, s, e, cl, shared_n, frac in rows:
            f.write(
                f"{gid}\t{gsize}\t{file_}\t{name}\t{s}\t{e}\t{cl}\t"
                f"{shared_n}\t{frac:.3f}\n"
            )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out", default=str(rl.REPO_ROOT / "tools/review/out/clone_candidates.tsv")
    )
    ap.add_argument("--k", type=int, default=SHINGLE_K_DEFAULT)
    ap.add_argument("--w", type=int, default=WINNOW_W_DEFAULT)
    args = ap.parse_args()

    entries = collect_functions(args.k)
    rows = build_groups(entries, args.w)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_tsv(rows, out_path, args.k, args.w)
    n_groups = len({r[0] for r in rows})
    print(
        f"clone_candidates: {len(entries)} functions considered, "
        f"{n_groups} candidate groups ({len(rows)} member rows), "
        f"written to {out_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
