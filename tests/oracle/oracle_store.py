r"""tests/oracle/oracle_store.py — the ORACLE STORE core: `Question`/`Answer`
serialization, the question hash, `OracleId`, and the self-checking TSV
store format, built to the letter of `docs/design/oracle_interface.md`
(PROPOSED, PANELED at r56, REVISED, VERIFIED — see that document's own header
and `docs/dev/reviews/2026-09-10-r56-oracle-interface.md`). Do not redesign
anything here; this module implements the design, it does not extend it.

WHAT THIS FILE IS NOT: an adapter. It knows nothing about libpcre2, ssh, or
any oracle's own binding. `local_adapter.py` and `remote_adapter.py` are the
consumers that turn a `Question` batch into an `Answer` batch; this file is
only the shared vocabulary (§2-§5) and the store format (§7-§8) both of them
and every future adapter speak.

## The six kinds (§2)

Each kind's Question fields, in serialization order (§4):

    compile-accept  pattern
    match-at        pattern, subject, startpos
    captures        pattern, subject, startpos, nslots
    name-accept     namespace, name
    membership      property, encoding
    pattern-info    pattern

`pattern`/`subject` are raw BYTES; every other field is a decimal integer or
a bare identifier, already tab/newline/backslash-free by its own grammar (§4)
and serialized unescaped.

## Canonical serialization (§4, R56-1 corrected)

The `docs/spec/rxt_format.md`:458-474 FIVE-ESCAPE TSV-FRAMING SUBSET
(`\\ \t \n \r \xNN`), BACKSLASH ESCAPED FIRST — not the seven-escape
quoted-context vocabulary, which protects a `"`-delimited `<subject>` literal
and has nothing to protect here. Escaping the backslash first is what makes
the five-escape subset INJECTIVE: an un-escaped raw TAB byte and the literal
two-byte sequence `\`+`t` would otherwise both serialize to the same two
characters `\t`.

## The store (§7)

One file per `(OracleId, kind)`, TSV, rows sorted by `question_hash` for a
stable diff. The header row is TWO `#` lines: a provenance line
(`store_format_version`, the resolved `OracleId` fields, `rows`, `captured_at`,
`captured_by`, `command`) and a column-name line. **R56-4**: the row count is
asserted against what the file actually holds on every read (a truncated file
is a hard failure, the `artifact_size_log.tsv` precedent's actual shape); a
looked-up row's stored `question` text is verified against the caller's own
recomputed serialization before its answer is trusted (the cheap
collision/corruption tripwire R56-4 specifies) — a mismatch is a hard read
failure, never a silently-returned wrong answer. **R56-3**: a file whose
`store_format_version` this reader does not implement is a CLEAN MISS (every
row unread), never a partial parse. **R56-5**: `write_store` sorts by hash and
raises on a duplicate hash whose two rows carry different question text (the
collision tripwire at the write side, "the check rides the thing it guards").
"""
import hashlib
import os
import re

STORE_FORMAT_VERSION = 1

KIND_QUESTION_FIELDS = {
    "compile-accept": ("pattern",),
    "match-at": ("pattern", "subject", "startpos"),
    "captures": ("pattern", "subject", "startpos", "nslots"),
    "name-accept": ("namespace", "name"),
    "membership": ("property", "encoding"),
    "pattern-info": ("pattern",),
}

# Per-kind ANSWER column names (§5), in the order written to a store row
# after `question_hash` and `question`. `captures`' pairs and `membership`'s
# intervals and `pattern-info`'s nametable are each kept as ONE space-joined
# column rather than spread across a variable count of TAB columns, because
# the row's own field count must be independent of a query-specific quantity
# (`nslots` for `captures`) for the file to stay a fixed-column TSV the
# `table_contract.md` convention can name by header — a genuinely open
# implementation choice the design left unstated; recorded here and in the
# lane report rather than silently decided.
KIND_ANSWER_COLUMNS = {
    "compile-accept": ("verdict", "code", "message"),
    "match-at": ("verdict", "start", "end", "giveup_code"),
    "captures": ("pairs",),          # "s0 e0 s1 e1 ... s(nslots-1) e(nslots-1)"
    "name-accept": ("verdict", "code"),
    "membership": ("intervals",),    # "lo1-hi1 lo2-hi2 ..." (hex, ascending)
    "pattern-info": ("capturecount", "namecount", "nametable"),
}

_BYTE_FIELDS = frozenset(("pattern", "subject"))

_HEX_RE = re.compile(r"^[0-9A-Fa-f]+$")


# ---------------------------------------------------------------------------
# §4 — canonical serialization
# ---------------------------------------------------------------------------

def escape_field(raw):
    """The five-escape TSV-framing subset, backslash first (§4). `raw` is
    bytes. Every byte 0x20-0x7e except backslash passes through verbatim;
    tab/newline/CR get their two-character escape; backslash and every other
    byte (control chars, high bytes, DEL) get `\\xHH`. Backslash is escaped
    FIRST in the sense that matters: the loop is a single left-to-right pass
    over RAW bytes, so a literal backslash byte always becomes `\\\\` and can
    never be produced by, or confused with, any other escape's own output."""
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    out = []
    for b in raw:
        if b == 0x5c:
            out.append("\\\\")
        elif b == 0x09:
            out.append("\\t")
        elif b == 0x0a:
            out.append("\\n")
        elif b == 0x0d:
            out.append("\\r")
        elif 0x20 <= b < 0x7f:
            out.append(chr(b))
        else:
            out.append("\\x%02x" % b)
    return "".join(out)


def unescape_field(s):
    """Inverse of escape_field. Returns bytes. Raises ValueError on a
    dangling or unrecognised escape (never silently drops or misreads one —
    a store reader must not guess)."""
    out = bytearray()
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c != "\\":
            b = ord(c)
            if b > 0xff:
                raise ValueError("non-Latin-1 character %r in serialized "
                                  "field (escape_field never emits one)" % c)
            out.append(b)
            i += 1
            continue
        if i + 1 >= n:
            raise ValueError("dangling backslash at end of field %r" % s)
        nc = s[i + 1]
        if nc == "\\":
            out.append(0x5c); i += 2
        elif nc == "t":
            out.append(0x09); i += 2
        elif nc == "n":
            out.append(0x0a); i += 2
        elif nc == "r":
            out.append(0x0d); i += 2
        elif nc == "x":
            if i + 4 > n or not _HEX_RE.match(s[i + 2:i + 4]):
                raise ValueError("malformed \\x escape in field %r at %d"
                                  % (s, i))
            out.append(int(s[i + 2:i + 4], 16))
            i += 4
        else:
            raise ValueError("unknown escape \\%s in field %r" % (nc, s))
    return bytes(out)


def _field_text(kind, name, value):
    if name in _BYTE_FIELDS:
        if isinstance(value, str):
            value = value.encode("utf-8")
        return escape_field(value)
    # startpos / nslots: decimal integer, canonical (no leading zero, per
    # §4's byte-stability rule -- the producer normalizes before serializing).
    if isinstance(value, int):
        return str(value)
    value = str(value)
    if any(c in value for c in ("\t", "\n", "\r", "\\")):
        raise ValueError("field %r of kind %r (%r) is documented tab/"
                          "newline/backslash-free by its own grammar and "
                          "is not: %r" % (name, kind, value, value))
    return value


def serialize_question(kind, **fields):
    """Build the canonical serialized form of one Question (§4's diagram).
    `fields` are keyword args named per KIND_QUESTION_FIELDS[kind]; extra or
    missing fields are a hard error (a Question's field set is closed)."""
    if kind not in KIND_QUESTION_FIELDS:
        raise ValueError("unknown question kind %r" % kind)
    names = KIND_QUESTION_FIELDS[kind]
    missing = [n for n in names if n not in fields]
    extra = [n for n in fields if n not in names]
    if missing or extra:
        raise ValueError("kind %r fields: missing %r extra %r"
                          % (kind, missing, extra))
    return "\t".join(_field_text(kind, n, fields[n]) for n in names)


def question_hash(serialized):
    """sha256, truncated to 16 hex chars (§4) -- `bundle.py`'s own
    truncation, reused rather than re-decided."""
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# §3 — OracleId
# ---------------------------------------------------------------------------

# The measured PCRE2 compiled-in defaults (§3, R56-2): "match_limit =
# 10000000, depth_limit = 10000000, heap_limit = 20000000 (KiB)" -- measured
# 2026-09-10 via pcre2_config() against this box's resolved binding. A config
# record that does not name these three explicitly means exactly these
# values, never "unset" or "whatever ran".
DEFAULT_MATCH_LIMIT = 10_000_000
DEFAULT_DEPTH_LIMIT = 10_000_000
DEFAULT_HEAP_LIMIT = 20_000_000


class OracleId(object):
    """`(name, version, config)` (§3). `config` is the answer-affecting
    subset only: `utf`, `caseless`, and the limit triple (R56-2). Explicitly
    EXCLUDED, by measured-fact argument (§3): PCRE2_NO_UTF_CHECK (perf-only,
    inert on the well-formed subjects every kind here can construct),
    PCRE2_UCP (no producer in this tree), newline/BSR convention and
    JIT-vs-interpreted (no adapter surveyed varies either, R56-8) -- an
    adapter that ever varies one of these four must widen `config` FIRST,
    measuring the divergence, before adding the field."""

    __slots__ = ("name", "version", "utf", "caseless",
                 "match_limit", "depth_limit", "heap_limit")

    def __init__(self, name, version, utf=False, caseless=False,
                 match_limit=DEFAULT_MATCH_LIMIT,
                 depth_limit=DEFAULT_DEPTH_LIMIT,
                 heap_limit=DEFAULT_HEAP_LIMIT):
        self.name = name
        self.version = version
        self.utf = bool(utf)
        self.caseless = bool(caseless)
        self.match_limit = match_limit
        self.depth_limit = depth_limit
        self.heap_limit = heap_limit

    def _config_tag(self):
        # The directory naming (§7.1) leaves the exact spelling of a
        # non-default config's tag genuinely open ("<config-tag> present
        # only when more than one config is exercised"). Simplest
        # conforming choice, recorded rather than silently decided: one
        # hyphen-joined token per active axis, in a fixed order (utf,
        # caseless, then the limit triple ONLY if any of the three differs
        # from its default -- the three travel together because a config
        # record that names one must name all three, per §3's own rule).
        parts = []
        if self.utf:
            parts.append("utf")
        if self.caseless:
            parts.append("caseless")
        if (self.match_limit, self.depth_limit, self.heap_limit) != (
                DEFAULT_MATCH_LIMIT, DEFAULT_DEPTH_LIMIT, DEFAULT_HEAP_LIMIT):
            parts.append("lim%d-%d-%d" % (self.match_limit, self.depth_limit,
                                           self.heap_limit))
        return "-".join(parts)

    def dirname(self):
        """`<oracle-name>-<version>[-<config-tag>]` (§7.1)."""
        base = "%s-%s" % (self.name, self.version)
        tag = self._config_tag()
        return base + ("-" + tag if tag else "")

    def header_fields(self):
        return {
            "oracle_name": self.name,
            "oracle_version": self.version,
            "utf": "1" if self.utf else "0",
            "caseless": "1" if self.caseless else "0",
            "match_limit": str(self.match_limit),
            "depth_limit": str(self.depth_limit),
            "heap_limit": str(self.heap_limit),
        }

    def __repr__(self):
        return "OracleId(%r)" % (self.dirname(),)


# ---------------------------------------------------------------------------
# §7 — the store: path resolution, write, read, self-checked lookup
# ---------------------------------------------------------------------------

def store_path(store_root, oracle_id, kind):
    if kind not in KIND_QUESTION_FIELDS:
        raise ValueError("unknown question kind %r" % kind)
    return os.path.join(store_root, oracle_id.dirname(), kind + ".tsv")


class StoreCorruption(Exception):
    """A store file failed its own self-check (§7.1/R56-4): a row count
    that does not match what the file holds, a duplicate question_hash
    whose two rows carry different question text, or (at lookup) a stored
    `question` column that does not equal the caller's own recomputed
    serialization. Never silently absorbed -- a hard read failure."""


def write_store(path, oracle_id, kind, rows, captured_at, captured_by,
                 command):
    """`rows`: iterable of (question_fields_dict, answer_fields_tuple),
    `answer_fields_tuple` ordered per KIND_ANSWER_COLUMNS[kind]. Serializes,
    hashes, sorts by hash (§7.1a: "regeneration is sorted-by-hash"),
    detects a duplicate hash whose two rows disagree on question text
    (R56-5's write-side tripwire) before writing a byte, and writes the
    two-line `#` header (store_format_version + provenance, then column
    names) that read_store/lookup depend on."""
    cols = KIND_ANSWER_COLUMNS[kind]
    built = []
    seen = {}
    for qfields, afields in rows:
        if len(afields) != len(cols):
            raise ValueError("kind %r answer needs %d fields %r, got %r"
                              % (kind, len(cols), cols, afields))
        q = serialize_question(kind, **qfields)
        h = question_hash(q)
        if h in seen and seen[h] != q:
            raise StoreCorruption(
                "duplicate question_hash %s with two different questions: "
                "%r vs %r (R56-1's collision, or a real bug feeding two "
                "distinct questions the same key)" % (h, seen[h], q))
        seen[h] = q
        built.append((h, q, afields))
    built.sort(key=lambda row: row[0])

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        prov = dict(oracle_id.header_fields())
        prov["store_format_version"] = str(STORE_FORMAT_VERSION)
        prov["rows"] = str(len(built))
        prov["captured_at"] = captured_at
        prov["captured_by"] = captured_by
        prov["command"] = command
        header = " ".join("%s=%s" % (k, _hdr_escape(v))
                           for k, v in prov.items())
        f.write("# %s\n" % header)
        f.write("# question_hash\tquestion\t%s\n" % "\t".join(cols))
        for h, q, afields in built:
            f.write("%s\t%s\t%s\n"
                    % (h, q, "\t".join(str(a) for a in afields)))
    return len(built)


def _hdr_escape(v):
    # Header fields are provenance prose (a command line, a hostname) and
    # can legitimately contain spaces; only whitespace that would break the
    # ONE-line "# key=val key=val ..." header format needs protection, so
    # this is deliberately a narrower escape than escape_field -- it is not
    # a Question field and §4's rule does not apply to it.
    return str(v).replace("\n", "\\n").replace("\t", "\\t")


def read_store(path):
    """Parses a store file's header + rows, verifying (R56-4/R56-5) the
    stamped `rows` count against what the file actually holds and that no
    two rows share a hash with different question text. Returns
    (header_dict, {question_hash: (question_text, answer_fields_tuple)}),
    or (None, None) if the file's `store_format_version` is not the one
    this reader implements (§8 Claim 4: a version mismatch is a CLEAN MISS,
    never a partial parse -- so a caller must treat that return the same
    way it treats "row not found", not raise).

    THE ROW-WIDTH SUBTLETY: a serialized `question` is itself TAB-JOINED
    internally (§4's diagram -- `match-at` is `pattern\tsubject\tstartpos`),
    so a naive `line.split("\t")` cannot tell "the question's own field
    boundary" from "the row's own column boundary" by looking at the line
    alone. The KIND (named by the file's own basename, one file per kind by
    construction, §7.1) fixes both field counts, so the split width is
    always `1 (hash) + len(question fields) + len(answer columns)` -- known
    before any row is read, not inferred from one."""
    kind = os.path.splitext(os.path.basename(path))[0]
    if kind not in KIND_QUESTION_FIELDS:
        raise StoreCorruption(
            "%s: filename does not name a known question kind" % path)
    n_qfields = len(KIND_QUESTION_FIELDS[kind])
    with open(path, "r", encoding="utf-8") as f:
        prov_line = f.readline()
        col_line = f.readline()
        if not prov_line.startswith("# ") or not col_line.startswith("# "):
            raise StoreCorruption("%s: missing the two-line header" % path)
        header = _parse_hdr(prov_line[2:].rstrip("\n"))
        cols = col_line[2:].rstrip("\n").split("\t")
        if cols[:2] != ["question_hash", "question"]:
            raise StoreCorruption(
                "%s: column header does not start question_hash, question: "
                "%r" % (path, cols))
        if header.get("store_format_version") != str(STORE_FORMAT_VERSION):
            return None, None
        answer_cols = cols[2:]
        total_width = 1 + n_qfields + len(answer_cols)
        rows = {}
        n = 0
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            n += 1
            parts = line.split("\t")
            if len(parts) != total_width:
                raise StoreCorruption(
                    "%s: row %d has %d tab-fields, kind %r + header %r "
                    "declare %d" % (path, n, len(parts), kind, answer_cols,
                                     total_width))
            h = parts[0]
            q = "\t".join(parts[1:1 + n_qfields])
            afields = tuple(parts[1 + n_qfields:])
            if h in rows and rows[h][0] != q:
                raise StoreCorruption(
                    "%s: duplicate question_hash %s with two different "
                    "questions" % (path, h))
            rows[h] = (q, afields)
        declared = int(header.get("rows", "-1"))
        if declared != n:
            raise StoreCorruption(
                "%s: header declares rows=%d, file holds %d -- truncated "
                "or corrupted" % (path, declared, n))
        return header, rows


def _parse_hdr(s):
    out = {}
    for tok in s.split(" "):
        if "=" not in tok:
            continue
        k, v = tok.split("=", 1)
        out[k] = v.replace("\\t", "\t").replace("\\n", "\n")
    return out


def lookup(store_root, oracle_id, kind, **question_fields):
    """The self-checking read path (R56-4): recompute the canonical
    serialization and hash from `question_fields`, look the hash up, and
    verify the STORED question text equals the recomputed serialization
    before trusting the answer -- a bit-flip, a hand edit, or a hash
    collision is a StoreCorruption, never a silently wrong answer.
    Returns None on a clean miss (no such row, file absent, or an
    unreadable store_format_version) -- a caller cannot distinguish those
    three from this return value alone, by design: all three mean "ask the
    oracle live"."""
    path = store_path(store_root, oracle_id, kind)
    if not os.path.exists(path):
        return None
    header, rows = read_store(path)
    if rows is None:
        return None
    q = serialize_question(kind, **question_fields)
    h = question_hash(q)
    if h not in rows:
        return None
    stored_q, afields = rows[h]
    if stored_q != q:
        raise StoreCorruption(
            "%s: row %s's stored question %r != recomputed %r -- the "
            "collision/corruption tripwire fired" % (path, h, stored_q, q))
    return afields
