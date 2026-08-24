"""[DD-14] PROBE 2 -- a pure-text CENSUS of how many patterns bear a
subroutine call at all, with backreference and lookaround counts alongside
as scale references. NO COMPILER INVOLVED (module `recursion` has no
producer -- see probe_spellings.py's A6 -- so a compiler-side census would
just be "every call refuses").

TWO TIERS, because pcrec's tree has exactly one AUTHORITATIVE population and
several other places a construct's SPELLING can appear in TEXT without being
an actual test pattern:

  TIER A (authoritative): every `tests/**/*.rxt` file, `pattern <regex>`
  lines ONLY, parsed the way docs/testing.md's own format section states it
  -- a line starting with the literal keyword `pattern ` (one space) starts
  a block; the regex is everything after that first space, VERBATIM, to
  EOL. `#`-comment lines and expectation lines (`m`/`n`/`ms`/`ns`/`g`/`gp`/
  `flags`/`features`/`perr`) are not pattern lines and are skipped. This is
  pcrec's actual committed test population -- the number the DD-14 gate
  should trust for "how many patterns in this codebase use a call".

  TIER B (context, not population): every OTHER pattern-list-SHAPED file
  this probe could find under `tests/` and `docs/` -- the design lane's own
  measurement probes (`docs/design/*_measurements/probes/*.py`, which
  deliberately enumerate call/backref/lookaround spellings for STUDY, not as
  a production corpus), `docs/measurements/*.txt`, `tests/registry/*.c`
  (literal PCRE strings in the C differential harness), `tests/reject/*.sh`.
  These are grepped RAW -- no attempt to isolate "the pattern" from
  surrounding code/prose/comments, because their formats differ too much
  for one parser to parse honestly. A Tier B count therefore means "the
  spelling's TEXT appears in this file this many times" (could be inside a
  comment, a docstring, a `note=` string), not "this many test patterns use
  it" -- reported separately, per file, so nobody mistakes it for Tier A.
  This probe's OWN two files (probe_prefilter.py, probe_population.py) are
  excluded from Tier B -- they are the instrument, not the population, and
  probe_prefilter.py's inlining table alone would swamp every count.

THE CLASS-MASKING FIX (Tier A only -- mandatory, or the numbers lie).
Found while writing this probe, reading `tests/backrefs/octal_class.rxt`'s
own comment on `pattern ^[\\g<1>]$`: inside a character class, `\\g<1>` is
FOUR LITERAL one-byte escapes (`g`, `<`, `1`, `>`), NOT a subroutine call --
"the class doorway arbitrates on the SAME tail the atom doorway does", so
`[\\g<]` answers 'g' and '<' as two ordinary class members. A naive
substring/regex scan for `\\g<` over the raw pattern text counts that .rxt
row as a call. This probe masks character-class CONTENTS (the bytes between
an unescaped `[` and its closing `]`, respecting PCRE2's "leading `^]`/`]`
is literal" rule and backslash-escapes) to a neutral filler before running
any spelling regex over a Tier-A pattern line -- so only spellings OUTSIDE a
class are counted. (`\\Q...\\E` literal-quoting is NOT handled -- a
documented, accepted gap; see the tail of this file.)

REACHABILITY: if Tier A's total is zero for every CALL spelling, that IS a
finding (recursion refuses, so no committed test pattern could keep a call
in it) and this probe says so loudly, then prints the backref/lookaround
reference counts so the reader can see the census machinery itself is not
the reason for the zero.
"""
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", "..", ".."))
_THIS_FILE_BASENAMES = {"probe_prefilter.py", "probe_population.py"}

print("python3:", sys.version.split()[0])
print("repo root:", _ROOT)
print()


# ---------------------------------------------------------------------------
# CLASS-MASKING (Tier A only)
# ---------------------------------------------------------------------------
def mask_classes(pat):
    """Blank out (to 'x') the CONTENTS of every `[...]` character class in
    `pat`, leaving everything outside a class untouched, so a spelling regex
    run over the result only fires on constructs OUTSIDE a class. Handles:
      - backslash-escapes (both inside and outside a class) -- the escaped
        character is never itself treated as a class delimiter;
      - a leading `^` and/or a leading `]` right after `[` (optionally after
        `^`) being LITERAL, per PCRE2 class syntax, not the closing `]`.
    Does NOT handle `\\Q...\\E` literal-quoting or POSIX `[:class:]` nesting
    quirks -- neither construct appears in this lane's population, and a
    census probe is not the place to grow a PCRE2 parser."""
    out = list(pat)
    i, n = 0, len(pat)
    in_class = False
    while i < n:
        c = pat[i]
        if c == "\\" and i + 1 < n:
            i += 2
            continue
        if not in_class:
            if c == "[":
                in_class = True
                i += 1
                if i < n and pat[i] == "^":
                    i += 1
                if i < n and pat[i] == "]":
                    i += 1
                continue
            i += 1
        else:
            if c == "]":
                in_class = False
                i += 1
                continue
            out[i] = "x"
            i += 1
    return "".join(out)


# ---------------------------------------------------------------------------
# SPELLING TABLE. Order matters within a bucket only where spans could
# otherwise be double-counted (the numeric-absolute regex explicitly
# excludes a leading 0, since "(?0)" is its own row).
# ---------------------------------------------------------------------------
CALL_SPELLINGS = [
    ("(?N) absolute",       re.compile(r"\(\?[1-9][0-9]*\)")),
    ("(?-N)/(?+N) relative", re.compile(r"\(\?[+-][0-9]+\)")),
    ("(?&name)",            re.compile(r"\(\?&[A-Za-z_][A-Za-z0-9_]*\)")),
    ("(?P>name)",           re.compile(r"\(\?P>[A-Za-z_][A-Za-z0-9_]*\)")),
    ("(?R)",                re.compile(r"\(\?R\)")),
    ("(?0)",                re.compile(r"\(\?0\)")),
    (r"\g<...> call",       re.compile(r"\\g<[^>]*>")),
    (r"\g'...' call",       re.compile(r"\\g'[^']*'")),
]

BACKREF_SPELLINGS = [
    (r"\N bare numeric",    re.compile(r"\\[1-9][0-9]?(?![0-9])")),
    (r"\g{...} braced",     re.compile(r"\\g\{[^}]*\}")),
    (r"\gN bare (no delim)", re.compile(r"\\g[+-]?[0-9]+(?![<'{0-9])")),
    (r"\k<...>",            re.compile(r"\\k<[^>]*>")),
    (r"\k'...'",            re.compile(r"\\k'[^']*'")),
    (r"\k{...}",            re.compile(r"\\k\{[^}]*\}")),
    ("(?P=name)",           re.compile(r"\(\?P=[A-Za-z_][A-Za-z0-9_]*\)")),
]

LOOKAROUND_SPELLINGS = [
    ("(?= lookahead",       re.compile(r"\(\?=")),
    ("(?! neg lookahead",   re.compile(r"\(\?!")),
    ("(?<= lookbehind",     re.compile(r"\(\?<=")),
    ("(?<! neg lookbehind", re.compile(r"\(\?<!")),
]

ALL_BUCKETS = [("CALL", CALL_SPELLINGS), ("BACKREF", BACKREF_SPELLINGS),
               ("LOOKAROUND", LOOKAROUND_SPELLINGS)]


def count_in_text(text, buckets):
    """{bucket_name: {label: (pattern_occurrences, total_hits)}} -- but here
    `text` is ONE pattern line, so pattern_occurrences is 0/1 (this line
    counted or not) and total_hits is the number of non-overlapping matches
    on this one line."""
    out = {}
    for bucket_name, rows in buckets:
        out[bucket_name] = {}
        for label, rx in rows:
            hits = len(rx.findall(text))
            out[bucket_name][label] = hits
    return out


# ---------------------------------------------------------------------------
# TIER A -- tests/**/*.rxt, `pattern` lines only
# ---------------------------------------------------------------------------
def find_rxt_files(root):
    out = []
    for dirpath, _dirnames, filenames in os.walk(os.path.join(root, "tests")):
        for fn in filenames:
            if fn.endswith(".rxt"):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def rxt_pattern_lines(path):
    """Yield (lineno, regex_text) for every `pattern <regex>` line, per
    docs/testing.md: `pattern ` is the literal keyword (checked with the
    exact prefix, not startswith on a stripped line, so a subject line that
    happens to start with the word "pattern" inside its quoted text is not
    mistaken for a block header -- subject lines start with `m`/`n`/etc.,
    never `pattern`, so this is a non-issue in practice but the exact-prefix
    check costs nothing and documents the rule)."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            raw = line.rstrip("\n")
            if raw.startswith("#"):
                continue
            if raw.startswith("pattern "):
                yield lineno, raw[len("pattern "):]


tier_a_files = find_rxt_files(_ROOT)
print("=== TIER A: tests/**/*.rxt (%d files) ================================"
      % len(tier_a_files))

tier_a_totals = {b: {label: 0 for label, _ in rows} for b, rows in ALL_BUCKETS}
tier_a_pattern_hits = {b: {label: [] for label, _ in rows}
                        for b, rows in ALL_BUCKETS}
tier_a_total_patterns = 0

for path in tier_a_files:
    rel = os.path.relpath(path, _ROOT)
    for lineno, regex_text in rxt_pattern_lines(path):
        tier_a_total_patterns += 1
        masked = mask_classes(regex_text)
        counts = count_in_text(masked, ALL_BUCKETS)
        for bucket_name, _rows in ALL_BUCKETS:
            for label, hits in counts[bucket_name].items():
                if hits:
                    tier_a_totals[bucket_name][label] += hits
                    tier_a_pattern_hits[bucket_name][label].append(
                        (rel, lineno, regex_text))

print("scanned %d `pattern` lines across %d .rxt files\n"
      % (tier_a_total_patterns, len(tier_a_files)))

for bucket_name, rows in ALL_BUCKETS:
    bucket_total = sum(tier_a_totals[bucket_name].values())
    print("--- %s (total occurrences: %d) ---" % (bucket_name, bucket_total))
    for label, _rx in rows:
        n_occ = tier_a_totals[bucket_name][label]
        n_pat = len(tier_a_pattern_hits[bucket_name][label])
        print("  %-24s occurrences=%-4d patterns=%-4d" % (label, n_occ, n_pat))
        for rel, lineno, regex_text in tier_a_pattern_hits[bucket_name][label][:8]:
            print("      %s:%d  pattern %s" % (rel, lineno, regex_text))
        if n_pat > 8:
            print("      ... and %d more" % (n_pat - 8))
    print()

call_total = sum(tier_a_totals["CALL"].values())
if call_total == 0:
    print("TIER A CALL TOTAL: 0 -- no committed .rxt pattern contains a "
          "subroutine-call spelling. EXPECTED: module `recursion` has no "
          "producer, so a call ALWAYS refuses to compile, and no `perr` "
          "block (or any other block) in this tree was written against it.")
else:
    print("TIER A CALL TOTAL: %d occurrence(s) across %d distinct pattern "
          "line(s) -- see tests/backrefs/spellings.rxt's `perr` rows: a "
          "call spelling that MUST refuse is exactly the case a `perr` "
          "block tests, so a nonzero count here does not mean pcrec "
          "compiles calls." % (call_total,
                                len({(r, l) for rows in
                                     tier_a_pattern_hits["CALL"].values()
                                     for r, l, _ in rows})))
backref_total = sum(tier_a_totals["BACKREF"].values())
look_total = sum(tier_a_totals["LOOKAROUND"].values())
print("TIER A BACKREF TOTAL (scale reference): %d occurrences" % backref_total)
print("TIER A LOOKAROUND TOTAL (scale reference): %d occurrences" % look_total)
print()


# ---------------------------------------------------------------------------
# TIER B -- broader raw sweep, context only
# ---------------------------------------------------------------------------
def find_tier_b_files(root):
    out = []
    design_probes = os.path.join(root, "docs", "design")
    for dirpath, _dirnames, filenames in os.walk(design_probes):
        if not dirpath.replace(os.sep, "/").endswith("/probes"):
            continue
        for fn in filenames:
            if fn.endswith(".py") and fn not in _THIS_FILE_BASENAMES:
                out.append(os.path.join(dirpath, fn))
    meas_dir = os.path.join(root, "docs", "measurements")
    if os.path.isdir(meas_dir):
        for fn in sorted(os.listdir(meas_dir)):
            if fn.endswith(".txt"):
                out.append(os.path.join(meas_dir, fn))
    registry_dir = os.path.join(root, "tests", "registry")
    if os.path.isdir(registry_dir):
        for fn in sorted(os.listdir(registry_dir)):
            if fn.endswith(".c") or fn.endswith(".h"):
                out.append(os.path.join(registry_dir, fn))
    reject_dir = os.path.join(root, "tests", "reject")
    if os.path.isdir(reject_dir):
        for fn in sorted(os.listdir(reject_dir)):
            if fn.endswith(".sh"):
                out.append(os.path.join(reject_dir, fn))
    return sorted(out)


tier_b_files = find_tier_b_files(_ROOT)
print("=== TIER B: broader raw sweep, %d files (context, NOT population) ===="
      % len(tier_b_files))
print("files scanned:")
for p in tier_b_files:
    print("   ", os.path.relpath(p, _ROOT))
print()

tier_b_totals = {b: {label: 0 for label, _ in rows} for b, rows in ALL_BUCKETS}
tier_b_by_file = {}
for path in tier_b_files:
    rel = os.path.relpath(path, _ROOT)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    counts = count_in_text(text, ALL_BUCKETS)
    file_total = sum(sum(counts[b].values()) for b, _ in ALL_BUCKETS)
    if file_total:
        tier_b_by_file[rel] = counts
    for bucket_name, _rows in ALL_BUCKETS:
        for label, hits in counts[bucket_name].items():
            tier_b_totals[bucket_name][label] += hits

for bucket_name, rows in ALL_BUCKETS:
    bucket_total = sum(tier_b_totals[bucket_name].values())
    print("--- %s (raw text occurrences: %d) ---" % (bucket_name, bucket_total))
    for label, _rx in rows:
        n = tier_b_totals[bucket_name][label]
        if n:
            print("  %-24s occurrences=%d" % (label, n))
    print()

print("--- per-file totals (files with >=1 hit in ANY bucket) ---")
for rel, counts in sorted(tier_b_by_file.items(),
                           key=lambda kv: -sum(sum(c.values())
                                                for c in kv[1].values())):
    call_n = sum(counts["CALL"].values())
    bref_n = sum(counts["BACKREF"].values())
    look_n = sum(counts["LOOKAROUND"].values())
    print("  %-70s call=%-4d backref=%-4d lookaround=%-4d"
          % (rel, call_n, bref_n, look_n))
print()

print("=== SUMMARY =========================================================")
print("Tier A (authoritative, tests/**/*.rxt `pattern` lines, %d files, %d "
      "pattern lines):" % (len(tier_a_files), tier_a_total_patterns))
print("  CALL total       : %d" % call_total)
print("  BACKREF total     : %d" % backref_total)
print("  LOOKAROUND total  : %d" % look_total)
print("Tier B (context only, raw text sweep, %d files):" % len(tier_b_files))
print("  CALL total        : %d" % sum(tier_b_totals["CALL"].values()))
print("  BACKREF total     : %d" % sum(tier_b_totals["BACKREF"].values()))
print("  LOOKAROUND total  : %d" % sum(tier_b_totals["LOOKAROUND"].values()))
