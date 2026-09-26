#!/usr/bin/env python3
"""pcrec-analyze — the [FINDINGS] exemplar analyzer (D83, D123-3/3a, R26-R27d).

STEP B3 PROTOTYPE (docs/design/findings/design.md §10; lane `findb3`,
2026-09-26). Grown from `docs/dev/findings_measure/scripts/ngram_count.py`'s
one-pass counting SHAPE (streaming, per-scan-kind, sparse), which was
written to graduate into exactly this role (its own docstring: "intended as
the prototype for the one-counter rule"). This file does not IMPORT that
module: `docs/dev/findings_measure/` is a completed measurement lane's own
archived record (own CLAUDE.md, its own lifecycle), and coupling a
permanent `scripts/` tool to it would tie two things that must be free to
diverge. R27b's "one counter" is honoured going forward by THIS file being
the one implementation every shipped generator calls (§13 step B5) — not
by importing runest's.

Emits a `.rxt` `analysis <name>` BUNDLE fragment (design.md §2.7's shape)
on stdout. Touches no pcrec C source and needs no built `pcrec`/`libpcrec`
— it is a standalone counting + provenance tool. `analyze/` (design.md
§10.1's end-state C binary, build step B6) re-implements the SAME four
command forms and byte-identical output; this file is then DELETED
(implement-then-replace, §10.1/§12).

Command forms (design.md §10.2):

    pcrec-analyze --name NAME --retrieved DATE [--scan freq,cpfreq,bigram]
                  [--source TOKEN] [--url U] [--ref R] [--license L]
                  [--shard K/N] [FILE | -]           -> one bundle on stdout
    pcrec-analyze --merge --name NAME PART.rxt...    -> merged bundle
                  [--bytes N --sha256 HEX]               (see NOTE)
    pcrec-analyze --digest-only [FILE | -]           -> "bytes N" / "sha256 H"
    pcrec-analyze --check BUNDLE.rxt [FILE | -]      -> exit 0 iff a recount
                                                         reproduces every row

NOTE on --merge's --bytes/--sha256 (a manager-review item; see
docs/dev/lanes/findb3_report.md "Judgment calls owed to the manager"): the
design's own CLI table (§10.2) spells `--merge --name NAME PART.rxt...`
with no file operand, but §10.4 also says a merge's final `bytes`/`sha256`
"come from a --digest-only run over the whole input ... and --merge checks
that the shards' byte total equals it" — a check --merge cannot perform on
its own, since sha256 is sequential and a shard PART only ever saw its own
nominal byte range. This build reads that as: the caller runs
`--digest-only` once over the whole input and hands both values to
`--merge` via `--bytes`/`--sha256`; `--merge` then verifies them against
the SUM of the parts' own recorded `bytes` fields (a real integrity check —
F-7's detector) before stamping the merged bundle with the verified
totals. Both flags are optional; omitting them merges and sums `bytes`
with no `sha256` recorded — documented, never silent.

No clock is read anywhere in this file (R27c: `--retrieved` is a required
flag for the scan form, not a timestamp this tool takes itself), so the
same input and flags give byte-identical output on every run.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PCREC_ANALYZE_VERSION = "0.1"

# design.md §2.2/§1 row 4: the closed kind set, in CANONICAL order (§5.2,
# §8.1's "kinds in canonical order").
CANONICAL_KINDS = ("freq", "cpfreq", "bigram")

# design.md §2.2: which query each kind's derivation answers.
QUERY_OF_KIND = {"freq": "byte-rate", "cpfreq": "byte-rate", "bigram": "run-rarity"}

# design.md §2.4: solo-kind derivation names (no sibling kind in the bundle).
DERIVATION_ALONE = {"freq": "unigram", "bigram": "markov1"}

# design.md §2.4/§10.2: when freq AND cpfreq are BOTH present in one bundle,
# [r2 M-B1]'s split — freq answers `byte` only, cpfreq answers `utf8` only,
# via its own derivation.
CPFREQ_DERIVATION_SPLIT = "encode-utf8"

QUESTION_OF_KIND = {
    "freq": "How often does each byte occur in this exemplar?",
    "cpfreq": "How often does each Unicode code point occur in this exemplar?",
    "bigram": "How often does each adjacent byte pair occur in this exemplar?",
}
READER_OF_QUERY = {
    "byte-rate": "byte-rate (docs/spec/findings.md §4)",
    "run-rarity": "run-rarity (docs/spec/findings.md §4)",
}

# design.md §10.4: the encoding lattice `ascii < utf8 < bytes`.
ENCODING_RANK = {"ascii": 0, "utf8": 1, "bytes": 2}
RANK_ENCODING = {v: k for k, v in ENCODING_RANK.items()}

PCREC_MAX_FIND_COUNT = 1 << 40  # design.md §8.3 (kept as a courtesy bound)


# ---------------------------------------------------------------------------
# Encoding classification (design.md §10.2's observed-characteristic column)
# ---------------------------------------------------------------------------

def classify_encoding(data: bytes) -> str:
    """"ascii" | "utf8" | "bytes", per design.md §10.2's observed column."""
    try:
        data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return "bytes"
    return "ascii" if all(b < 0x80 for b in data) else "utf8"


def combine_encoding(values: List[str]) -> str:
    """design.md §10.4 merge rule: the lattice max."""
    return RANK_ENCODING[max(ENCODING_RANK[v] for v in values)]


# ---------------------------------------------------------------------------
# One-pass counters (design.md §10.3: freq/bigram/cpfreq are each one-pass)
# ---------------------------------------------------------------------------

def count_freq(data: bytes) -> List[int]:
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    return counts


def count_bigram(data: bytes) -> Dict[Tuple[int, int], int]:
    """Adjacent-byte-pair counts over `data` exactly as given — the CALLER
    is responsible for widening `data` by the one-byte-left overlap on a
    sharded, non-first shard (design.md §0.5/§10.4, [r2 A-1])."""
    counts: Dict[Tuple[int, int], int] = {}
    for i in range(len(data) - 1):
        key = (data[i], data[i + 1])
        counts[key] = counts.get(key, 0) + 1
    return counts


def is_continuation_byte(b: int) -> bool:
    return 0x80 <= b <= 0xBF


def count_cpfreq(text: str) -> Dict[int, int]:
    counts: Dict[int, int] = {}
    for ch in text:
        cp = ord(ch)
        counts[cp] = counts.get(cp, 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Sharding (design.md §10.4; [r2 A-1] the k=1 exception, [r2 A-2] the
# cpfreq lead-byte ownership seam)
# ---------------------------------------------------------------------------

def shard_bounds(size: int, k: int, n: int) -> Tuple[int, int]:
    if not (1 <= k <= n):
        raise ValueError(f"shard {k}/{n} out of range")
    start = (k - 1) * size // n
    end = k * size // n
    return start, end


def freq_shard_range(data: bytes, k: int, n: int) -> bytes:
    """freq/cpfreq's OWN nominal range: [start_K, end_K). Shard 1 starts at
    offset 0 like any ordinary read [r2 A-1] — there is no overlap byte to
    exclude."""
    start, end = shard_bounds(len(data), k, n)
    return data[start:end]


def bigram_shard_range(data: bytes, k: int, n: int) -> bytes:
    """The bigram range for shard K: [start_K, end_K) with ONE extra byte
    prepended for K > 1 (design.md §0.5) — the pair this shard OPENS uses
    that byte as its first element and counts it into NOTHING else. This
    partitions the whole file's pair-index space [0, size-2) across shards
    with no gap and no double-count: shard K's own pair-start indices are
    exactly [max(start_K-1, 0), end_K - 1)."""
    start, end = shard_bounds(len(data), k, n)
    lo = start - 1 if k > 1 else start
    return data[lo:end]


def cpfreq_shard_range(data: bytes, k: int, n: int) -> bytes:
    """[r2 A-2] Shard K owns exactly the code points whose LEAD byte lies
    in [start_K, end_K): skip continuation bytes at the shard's own start
    (they belong to a code point owned by an earlier shard) and read past
    end_K to finish a code point whose lead byte is still < end_K (owned
    HERE). Each shard computes its own cut from the file alone; a run of
    more than 3 continuation bytes is invalid UTF-8 either way (R26)."""
    start, end = shard_bounds(len(data), k, n)
    cp_start = start
    while cp_start < end and is_continuation_byte(data[cp_start]):
        cp_start += 1
    cp_end = end
    while cp_end < len(data) and is_continuation_byte(data[cp_end]):
        cp_end += 1
    return data[cp_start:cp_end]


# ---------------------------------------------------------------------------
# Key rendering (design.md §2.3: hex keys, per-kind arity, ascending)
# ---------------------------------------------------------------------------

def byte_key(b: int) -> str:
    return f"{b:02x}"


def pair_key(a: int, b: int) -> str:
    return f"{a:02x} {b:02x}"


def cp_key(cp: int) -> str:
    """`U+HHHH`..`U+HHHHHH` (design.md §2.2): 4 hex digits up to U+FFFF, 5 up
    to U+FFFFF, 6 up to the U+10FFFF ceiling."""
    if cp <= 0xFFFF:
        return f"U+{cp:04X}"
    if cp <= 0xFFFFF:
        return f"U+{cp:05X}"
    return f"U+{cp:06X}"


# ---------------------------------------------------------------------------
# The bundle model: one kind block's rows + declarations + provenance
# ---------------------------------------------------------------------------

class KindBlock:
    def __init__(self, kind: str) -> None:
        assert kind in CANONICAL_KINDS
        self.kind = kind
        self.rows: Dict[object, int] = {}  # key -> count; key kind is per-block
        self.encoding: Optional[str] = None
        self.source: Optional[str] = None
        self.retrieved: Optional[str] = None
        self.url: Optional[str] = None
        self.ref: Optional[str] = None
        self.license: Optional[str] = None
        self.provenance_bytes: Optional[int] = None
        self.provenance_sha256: Optional[str] = None

    def add_row(self, key, count: int) -> None:
        if count < 0 or count > PCREC_MAX_FIND_COUNT:
            raise ValueError(f"count {count} for key {key!r} out of range")
        self.rows[key] = self.rows.get(key, 0) + count

    def sorted_items(self):
        if self.kind == "bigram":
            return sorted(self.rows.items())  # tuple compare is numeric
        return sorted(self.rows.items())  # int keys compare numeric too


def merge_kind_blocks(blocks: List[KindBlock]) -> KindBlock:
    """design.md §10.4: "Counts ADD"; encoding by the lattice max; the
    caller (provenance metadata + bytes/sha256) is checked/combined
    separately in `cmd_merge`."""
    assert blocks
    out = KindBlock(blocks[0].kind)
    for b in blocks:
        assert b.kind == out.kind
        for key, count in b.rows.items():
            out.add_row(key, count)
    out.encoding = combine_encoding([b.encoding for b in blocks if b.encoding])
    return out


# ---------------------------------------------------------------------------
# Declaration synthesis (design.md §10.2's table; [r2 M-B1] collision-free)
# ---------------------------------------------------------------------------

def derive_serves(kind: str, encoding: str, has_freq: bool, has_cpfreq: bool) -> Tuple[str, str]:
    """Returns (when_list, via) for this kind's ONE `serves` line, per
    design.md §10.2's written-declarations table. `bigram` never collides
    with anything (it answers a different query); `freq`/`cpfreq` split
    ONLY when both are present in the same bundle [r2 M-B1]."""
    if kind == "bigram":
        when = "byte,utf8" if encoding in ("ascii", "utf8") else "byte"
        return when, "markov1"
    if kind == "freq":
        if has_cpfreq:
            # split: freq is the BYTE-only half regardless of encoding class,
            # since a cpfreq sibling exists to answer the utf8 side.
            return "byte", "unigram"
        when = "byte,utf8" if encoding in ("ascii", "utf8") else "byte"
        return when, "unigram"
    if kind == "cpfreq":
        # cpfreq can only exist at all when the input decoded as UTF-8
        # (R26), so encoding is always "ascii" or "utf8" here.
        assert encoding in ("ascii", "utf8"), (
            "cpfreq present with encoding=%r — R26 should have refused this "
            "before a cpfreq block could exist" % (encoding,)
        )
        return "utf8", CPFREQ_DERIVATION_SPLIT
    raise AssertionError(kind)


# ---------------------------------------------------------------------------
# Rendering (design.md §2.3/§2.7's exhibit shape)
# ---------------------------------------------------------------------------

def render_row(kind: str, key, count: int) -> str:
    if kind == "freq":
        return f"        row {byte_key(key)} {count}"
    if kind == "bigram":
        a, b = key
        return f"        row {pair_key(a, b)} {count}"
    if kind == "cpfreq":
        return f"        row {cp_key(key)} {count}"
    raise AssertionError(kind)


def render_kind_block(block: KindBlock, has_freq: bool, has_cpfreq: bool,
                       scan_list: List[str]) -> List[str]:
    when, via = derive_serves(block.kind, block.encoding, has_freq, has_cpfreq)
    query = QUERY_OF_KIND[block.kind]
    lines = [f"    {block.kind}"]
    lines.append(f"        question {QUESTION_OF_KIND[block.kind]}")
    lines.append(f"        reader {READER_OF_QUERY[query]}")
    lines.append(
        f"        analyzer pcrec-analyze {PCREC_ANALYZE_VERSION} --scan "
        + ",".join(scan_list)
    )
    lines.append(f"        encoding {block.encoding}")
    lines.append(f"        serves {query} when {when} via {via}")
    for key, count in block.sorted_items():
        lines.append(render_row(block.kind, key, count))
    lines.append("        provenance")
    lines.append(f"            source {block.source or 'exemplar'}")
    if block.retrieved:
        lines.append(f"            retrieved {block.retrieved}")
    if block.provenance_bytes is not None:
        lines.append(f"            bytes {block.provenance_bytes}")
    if block.provenance_sha256:
        lines.append(f"            sha256 {block.provenance_sha256}")
    if block.url:
        lines.append(f"            url {block.url}")
    if block.ref:
        lines.append(f"            ref {block.ref}")
    if block.license:
        lines.append(f"            license {block.license}")
    return lines


def render_bundle(name: str, blocks: Dict[str, KindBlock]) -> str:
    scan_list = [k for k in CANONICAL_KINDS if k in blocks]
    has_freq = "freq" in blocks
    has_cpfreq = "cpfreq" in blocks
    lines = [f"analysis {name}"]
    for kind in CANONICAL_KINDS:
        if kind in blocks:
            lines.extend(render_kind_block(blocks[kind], has_freq, has_cpfreq, scan_list))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# A minimal reader for the bundle text THIS tool emits (used by --check and
# --merge). Single writer, single reader, by design: this is not the full
# `.rxt` schema, only the subset design.md §2.7 specifies for a bundle.
# ---------------------------------------------------------------------------

class ParsedKind:
    def __init__(self, kind: str) -> None:
        self.kind = kind
        self.encoding: Optional[str] = None
        self.serves: List[Tuple[str, str, str]] = []  # (query, when, via)
        self.rows: Dict[object, int] = {}
        self.provenance: Dict[str, str] = {}


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def parse_bundle(text: str) -> Tuple[str, Dict[str, ParsedKind]]:
    raw_lines = [l for l in text.splitlines() if l.strip() != ""]
    if not raw_lines:
        raise ValueError("empty bundle")
    head = raw_lines[0]
    if not head.startswith("analysis "):
        raise ValueError(f"expected 'analysis NAME' header, got: {head!r}")
    name = head[len("analysis "):].strip()

    kinds: Dict[str, ParsedKind] = {}
    i = 1
    n = len(raw_lines)
    while i < n:
        line = raw_lines[i]
        indent = _indent_of(line)
        token = line.strip()
        if indent != 4:
            raise ValueError(f"line {i}: expected a kind header at indent 4: {line!r}")
        kind = token.split()[0] if token.split() else token
        if kind not in CANONICAL_KINDS:
            raise ValueError(f"line {i}: unknown kind {kind!r}")
        pk = ParsedKind(kind)
        i += 1
        in_provenance = False
        while i < n and _indent_of(raw_lines[i]) >= 8:
            fline = raw_lines[i]
            findent = _indent_of(fline)
            ftoken = fline.strip()
            if findent == 8:
                in_provenance = False
                if ftoken == "provenance":
                    in_provenance = True
                elif ftoken.startswith("encoding "):
                    pk.encoding = ftoken[len("encoding "):].strip()
                elif ftoken.startswith("serves "):
                    rest = ftoken[len("serves "):]
                    # "<query> when <enc-list> via <derivation>"
                    q, rest = rest.split(" when ", 1)
                    when, via = rest.split(" via ", 1)
                    pk.serves.append((q.strip(), when.strip(), via.strip()))
                elif ftoken.startswith("row "):
                    parts = ftoken[len("row "):].split()
                    count = int(parts[-1])
                    keyparts = parts[:-1]
                    if pk.kind == "freq":
                        key = int(keyparts[0], 16)
                    elif pk.kind == "bigram":
                        key = (int(keyparts[0], 16), int(keyparts[1], 16))
                    elif pk.kind == "cpfreq":
                        key = int(keyparts[0][2:], 16)  # strip "U+"
                    else:
                        raise AssertionError(pk.kind)
                    pk.rows[key] = pk.rows.get(key, 0) + count
                # question/reader/analyzer: free prose, not parsed further.
            elif findent == 12 and in_provenance:
                pfield, _, pval = ftoken.partition(" ")
                pk.provenance[pfield] = pval
            elif findent > 12 or (findent == 8 and False):
                raise ValueError(f"line {i}: unexpected indent: {fline!r}")
            i += 1
        kinds[pk.kind] = pk
    return name, kinds


# ---------------------------------------------------------------------------
# Command: scan (the default form)
# ---------------------------------------------------------------------------

def read_source(file_arg: Optional[str], shard: Optional[Tuple[int, int]]) -> bytes:
    is_stdin = file_arg is None or file_arg == "-"
    if is_stdin:
        if shard is not None:
            raise SystemExit("pcrec-analyze: --shard cannot be used with stdin (design.md §10.4)")
        return sys.stdin.buffer.read()
    return Path(file_arg).read_bytes()


def cmd_scan(args: argparse.Namespace) -> int:
    requested = args.scan.split(",") if args.scan else ["freq", "bigram"]
    requested = [k.strip() for k in requested if k.strip()]
    for k in requested:
        if k not in CANONICAL_KINDS:
            print(f"pcrec-analyze: unknown --scan kind {k!r}", file=sys.stderr)
            return 2
    shard = None
    if args.shard:
        k_s, n_s = args.shard.split("/")
        shard = (int(k_s), int(n_s))

    try:
        data = read_source(args.file, shard)
    except FileNotFoundError as e:
        print(f"pcrec-analyze: {e}", file=sys.stderr)
        return 2

    if shard:
        k, n = shard
        freq_range = freq_shard_range(data, k, n)
        bigram_range = bigram_shard_range(data, k, n)
        cpfreq_range = cpfreq_shard_range(data, k, n)
        provenance_bytes = len(freq_range)  # nominal shard size; see NOTE
        provenance_sha256 = None  # sha256 is sequential (design.md §10.4);
        # a shard PART never carries one — only --digest-only / --merge do.
    else:
        freq_range = bigram_range = cpfreq_range = data
        provenance_bytes = len(data)
        provenance_sha256 = hashlib.sha256(data).hexdigest()

    # design.md §10.2's table classifies the OBSERVED INPUT once, and every
    # kind's `encoding` field uses the SAME classification so a bundle never
    # disagrees with itself. For a sharded scan, `freq_range`'s own nominal
    # cut can split a multi-byte UTF-8 sequence exactly at its boundary —
    # classifying THAT slice would spuriously read "bytes" for a shard that
    # is really the middle of valid UTF-8. So classification always reads
    # `cpfreq_range`, the code-point-ALIGNED window ([r2 A-2]'s own seam
    # adjustment, computed above regardless of whether cpfreq was
    # requested), which for a non-sharded run is simply the whole input.
    encoding = classify_encoding(cpfreq_range)

    if "cpfreq" in requested:
        try:
            cp_text = cpfreq_range.decode("utf-8", errors="strict")
        except UnicodeDecodeError as e:
            print(
                f"pcrec-analyze: --scan cpfreq requires valid UTF-8 input "
                f"(R26); decode failed: {e}",
                file=sys.stderr,
            )
            return 2

    blocks: Dict[str, KindBlock] = {}
    if "freq" in requested:
        b = KindBlock("freq")
        for byte, count in enumerate(count_freq(freq_range)):
            if count:
                b.add_row(byte, count)
        b.encoding = encoding
        blocks["freq"] = b
    if "cpfreq" in requested:
        b = KindBlock("cpfreq")
        for cp, count in count_cpfreq(cp_text).items():
            b.add_row(cp, count)
        b.encoding = encoding
        blocks["cpfreq"] = b
    if "bigram" in requested:
        b = KindBlock("bigram")
        for key, count in count_bigram(bigram_range).items():
            b.add_row(key, count)
        b.encoding = encoding
        blocks["bigram"] = b

    for b in blocks.values():
        b.source = args.source or "exemplar"
        b.retrieved = args.retrieved
        b.url = args.url
        b.ref = args.ref
        b.license = args.license
        b.provenance_bytes = provenance_bytes
        b.provenance_sha256 = provenance_sha256

    sys.stdout.write(render_bundle(args.name, blocks))
    return 0


# ---------------------------------------------------------------------------
# Command: --digest-only
# ---------------------------------------------------------------------------

def cmd_digest_only(args: argparse.Namespace) -> int:
    data = read_source(args.file, None)
    print(f"bytes {len(data)}")
    print(f"sha256 {hashlib.sha256(data).hexdigest()}")
    return 0


# ---------------------------------------------------------------------------
# Command: --merge
# ---------------------------------------------------------------------------

def cmd_merge(args: argparse.Namespace) -> int:
    if not args.parts:
        print("pcrec-analyze: --merge needs at least one PART.rxt", file=sys.stderr)
        return 2

    per_kind: Dict[str, List[ParsedKind]] = {}
    common_name = None
    for part_path in args.parts:
        text = Path(part_path).read_text()
        try:
            name, kinds = parse_bundle(text)
        except ValueError as e:
            print(f"pcrec-analyze: {part_path}: {e}", file=sys.stderr)
            return 2
        for kind, pk in kinds.items():
            per_kind.setdefault(kind, []).append(pk)

    blocks: Dict[str, KindBlock] = {}
    nominal_bytes_total = 0
    for kind, parsed_list in per_kind.items():
        block = KindBlock(kind)
        for pk in parsed_list:
            for key, count in pk.rows.items():
                block.add_row(key, count)
        block.encoding = combine_encoding(
            [pk.encoding for pk in parsed_list if pk.encoding]
        )
        # provenance metadata must agree across parts, or this is a caller
        # error (never silently pick one — "never" per design.md §9).
        for field_name in ("source", "retrieved", "url", "ref", "license"):
            values = {pk.provenance.get(field_name) for pk in parsed_list}
            values.discard(None)
            if len(values) > 1:
                print(
                    f"pcrec-analyze: --merge: parts disagree on provenance "
                    f"'{field_name}' for kind {kind!r}: {sorted(values)}",
                    file=sys.stderr,
                )
                return 2
            setattr(block, field_name, next(iter(values), None))
        kind_bytes = 0
        for pk in parsed_list:
            b = pk.provenance.get("bytes")
            if b is not None:
                kind_bytes += int(b)
        block.provenance_bytes = kind_bytes if kind_bytes else None
        nominal_bytes_total = max(nominal_bytes_total, kind_bytes)
        blocks[kind] = block

    # [r2 A-2]/F-7: the shard-total integrity check, if the caller supplied
    # a --digest-only result to verify against (see the module docstring's
    # NOTE on why this is a --merge flag rather than a bare positional).
    if args.bytes is not None:
        if nominal_bytes_total and nominal_bytes_total != args.bytes:
            print(
                f"pcrec-analyze: --merge: shard byte total {nominal_bytes_total} "
                f"!= --bytes {args.bytes} (a shard boundary or overlap is wrong)",
                file=sys.stderr,
            )
            return 2
        for block in blocks.values():
            block.provenance_bytes = args.bytes
    if args.sha256 is not None:
        for block in blocks.values():
            block.provenance_sha256 = args.sha256

    sys.stdout.write(render_bundle(args.name, blocks))
    return 0


# ---------------------------------------------------------------------------
# Command: --check
# ---------------------------------------------------------------------------

def cmd_check(args: argparse.Namespace) -> int:
    bundle_path = Path(args.check)
    if not bundle_path.exists():
        print(f"pcrec-analyze: --check: {bundle_path} not found", file=sys.stderr)
        return 2
    name, kinds = parse_bundle(bundle_path.read_text())

    # [r2 A-5]'s analyzer-level analogue: a missing sample source FAILS
    # CLOSED, loudly, never a silent pass. Stdin ("-") is always available
    # (it is read once, below); only a NAMED, missing FILE is refused here.
    file_arg = args.file
    if file_arg is not None and file_arg != "-" and not Path(file_arg).exists():
        print(
            f"pcrec-analyze: --check: source {file_arg!r} not found — "
            f"cannot recount (manifest-only sources fail CLOSED, never skip)",
            file=sys.stderr,
        )
        return 2

    data = read_source(file_arg, None)
    mismatches: List[str] = []

    if "freq" in kinds:
        recounted = {b: c for b, c in enumerate(count_freq(data)) if c}
        if recounted != kinds["freq"].rows:
            mismatches.append("freq: recount does not match the bundle's rows")
    if "bigram" in kinds:
        recounted = count_bigram(data)
        recounted = {k: v for k, v in recounted.items() if v}
        if recounted != kinds["bigram"].rows:
            mismatches.append("bigram: recount does not match the bundle's rows")
    if "cpfreq" in kinds:
        try:
            text = data.decode("utf-8", errors="strict")
        except UnicodeDecodeError as e:
            mismatches.append(f"cpfreq: source no longer decodes as UTF-8 ({e})")
        else:
            recounted = count_cpfreq(text)
            if recounted != kinds["cpfreq"].rows:
                mismatches.append("cpfreq: recount does not match the bundle's rows")

    for kind, pk in kinds.items():
        b = pk.provenance.get("bytes")
        if b is not None and int(b) != len(data):
            mismatches.append(
                f"{kind}: provenance bytes {b} != source length {len(data)} (drift)"
            )
        s = pk.provenance.get("sha256")
        if s is not None:
            actual = hashlib.sha256(data).hexdigest()
            if s != actual:
                mismatches.append(f"{kind}: provenance sha256 {s} != recomputed {actual} (drift)")

    if mismatches:
        for m in mismatches:
            print(f"pcrec-analyze: --check FAILED: {m}", file=sys.stderr)
        return 1
    print(f"pcrec-analyze: --check OK: '{name}' reproduces its rows from {file_arg or '-'}")
    return 0


# ---------------------------------------------------------------------------
# argparse wiring
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pcrec-analyze",
        description="the [FINDINGS] exemplar analyzer prototype (design.md §10)",
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--merge", action="store_true", help="merge PART.rxt bundles")
    mode.add_argument("--digest-only", action="store_true", help="print bytes + sha256")
    mode.add_argument("--check", metavar="BUNDLE.rxt", help="recount and verify a bundle")

    p.add_argument("--name", help="bundle name (--merge and the scan form)")
    p.add_argument("--retrieved", help="required for the scan form (R27c: no clock)")
    p.add_argument("--scan", help="comma list of freq,cpfreq,bigram (default freq,bigram)")
    p.add_argument("--source", help="provenance source token (default: exemplar)")
    p.add_argument("--url")
    p.add_argument("--ref")
    p.add_argument("--license")
    p.add_argument("--shard", metavar="K/N", help="scan only shard K of N (design.md §10.4)")
    p.add_argument("--bytes", type=int, help="--merge: the verified whole-input byte total")
    p.add_argument("--sha256", help="--merge: the verified whole-input sha256")
    # ONE variadic positional (argparse cannot cleanly split "nargs='*' then
    # nargs='?'": the first one greedily eats everything). --merge treats
    # every positional as a PART.rxt; every other mode treats at most one
    # positional as FILE (or '-'/omitted for stdin) — see main().
    p.add_argument("pos", nargs="*", metavar="PART.rxt... | FILE", help=argparse.SUPPRESS)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.merge:
        if not args.name:
            print("pcrec-analyze: --merge requires --name", file=sys.stderr)
            return 2
        args.parts = args.pos
        return cmd_merge(args)

    if len(args.pos) > 1:
        print("pcrec-analyze: unexpected extra arguments: " + " ".join(args.pos[1:]), file=sys.stderr)
        return 2
    args.file = args.pos[0] if args.pos else None

    if args.digest_only:
        return cmd_digest_only(args)

    if args.check:
        return cmd_check(args)

    if not args.name or not args.retrieved:
        print("pcrec-analyze: the scan form requires --name and --retrieved", file=sys.stderr)
        return 2
    return cmd_scan(args)


if __name__ == "__main__":
    raise SystemExit(main())
