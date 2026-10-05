"""[OPT-GAPREPORT] the criteria, declared once.

Every threshold, comparator class and weight the pipeline applies lives in
the tables below.  Each table is FIRST-MATCH: the first row whose predicate
holds decides, and the last row of each is the catch-all (decisions.md
D-first-match idiom).  gap.py, rank.py and gapreport.py import this module;
none of them carries a literal criterion of its own.  Changing a row here is
a criteria change: say so in the report's judgement section, because it
moves the verdicts of every cell.
"""

# --- scale tiers (D144 addendum 1 + 2) -------------------------------------
# (floor on the smaller side's per-subject mean ns, tier, how it is read,
#  parameter)
#   ratio: verdict "behind" past x(param), "ahead" under 1/x(param), else null
#   delta: ns-scale, absolute delta per call; null when |delta| is under
#          param (a fraction) of the comparator's per-call figure; never scored
# The bands are the cross-window program-identical null bands measured by
# cycle2_batch2_reading.md section 1 (+8.77% us-scale throughput, +11.16%
# search, +41.09% below 100 ns).
TIERS = [
    (1000, "A", "ratio", 1.10),
    (100, "B", "ratio", 1.15),
    (0, "C", "delta", 0.41),
]

# --- comparators ------------------------------------------------------------
# (short testee name, captures?, role, semantic flag)
#   role peer      the primary like-for-like comparator
#   role scalar    a SCALAR engine: its beating auto is D119 algorithmic
#                  evidence (cycle1_analysis.md section 0 rules 1-4)
#   role simd      a SIMD-prefilter engine: a ceiling, counted rust_only
#   role excluded  carried in cmp but never a ceiling target (SIMD-first,
#                  nosom, nocaps: cycle1 section 0 rule 2)
# A caps=no comparator is faced by the better of auto-caps / auto-nocaps (the
# bench's I-99/I-100 classes); a caps=yes one by auto-caps.
PEER = "libpcre2:jit-caps"
COMPARATORS = [
    ("libpcre2:jit-caps", "yes", "peer", "PEER"),
    ("libpcre2:interp-caps", "yes", "scalar", "same semantics, interpreter"),
    ("libpcre2:dfa-nocaps", "no", "scalar", "longest-match DFA, no captures/backrefs"),
    ("re2:default-caps", "yes", "scalar", "leftmost-first, no backtracking features"),
    ("re2:longest-caps", "yes", "scalar", "LEFTMOST-LONGEST semantics"),
    ("oniguruma:default-caps", "yes", "scalar", "backtracker, Ruby dialect"),
    ("rust:default-caps", "no", "simd",
     "no backtracking features; NO-class driver; SIMD prefilters"),
    ("tre:default-caps", "yes", "scalar", "POSIX leftmost-longest"),
    ("vectorscan:block-nosom-nocaps", "no", "excluded",
     "SIMD multi-pattern, no start-of-match, no captures"),
]
CAPS_YES = {t for t, c, _r, _f in COMPARATORS if c == "yes"}
CAPS_NO = {t for t, c, _r, _f in COMPARATORS if c == "no"}
FLAGS = {t: f for t, _c, _r, f in COMPARATORS}
SCALAR = tuple(t for t, _c, r, _f in COMPARATORS if r == "scalar")
EXCLUDED = {t for t, _c, r, _f in COMPARATORS if r == "excluded"}

# --- realism weights (a stated judgement, D144 addendum 2 item 4) -----------
# (set name, weight); the "*" row is synthetic or hazard material.
REALISM = [
    ("loglines", 1.0),
    ("email-specimen", 1.0),
    ("capability", 0.75),
    ("utf8", 0.6),
    ("*", 0.4),
]


def realism(set_name):
    return next(w for s, w in REALISM if s in (set_name, "*"))


# --- group merges (first-match: a cause id listed here reports as its target) -
# The first instance judged FS-DFA and FS-VM to be one question with two
# consumers (D124), so they report as one START-SET group.
GROUP_MERGE = [
    ("FS-DFA", "START-SET"),
    ("FS-VM", "START-SET"),
]

# --- cause-group ranking (report order, first-match on the key list) --------
# Sorted descending on this key tuple: algorithmic evidence first (D119: a
# group where a scalar engine also wins), then the combined realism-weighted
# score, then breadth.  The manager's judgement section may reorder; this is
# the mechanical order only.
RANK_KEY = ("algorithmic", "score_combined", "breadth")

# --- fetch ------------------------------------------------------------------
REMOTE = "duxevents@100.69.121.107"
REMOTE_BENCH = "/home/duxevents/pcrec-bench"
# the sets stamps.py compiles, with the extra compiler flags the bench's
# pcrec-auto testee uses (pcrec-bench testees/pcrec/configs.toml)
SETS = {"capability": [], "syntax": [], "utf8": ["-e", "utf8"],
        "loglines": [], "bounded": [], "email": [], "altwide": [], "litrun": []}
