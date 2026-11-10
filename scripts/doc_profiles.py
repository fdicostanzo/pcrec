"""scripts/doc_profiles.py -- the ONE profile table ([DOC-INDEX], D192; docs/design/doc_index_format.md §2.4).

Read by scripts/entry (the accessor) and, from unit 1, by doc_lint and the hooks; plan_lint imports the id
shapes below for PL18. A new file or a new level is a row here, not code. Standard library only.

A profile row is a dict; the keys are the columns of the design's table:
    name       profile name
    index      path of the index file (relative to the root); the file named by the profile's name today
    details    path of the details file, or None (single / archive forms)
    id         regex of an item id, or None (plan: the [TAG] itself)
    states     the states an index line may carry (documentation; the linters check it)
    caps       (statement, line, file_bytes) soft caps; None = none. Characters for lines, bytes for the file
    level1     the working fields printed at level 1 (documentation + --levels)
    work       the --work view (documentation + --levels)
    form       'single' | 'pair' | 'archive' | 'dormant'
    dormant    for form 'dormant': the unit that wakes it
    linter     the script that lints it
    extra      extra paths the linter reads
    floor      C9 non-vacuity floor (None until the unit that sets it)
"""

# The id shapes an item KEY can take (design §2.3 routing rows 2, 3, 5, 6). PL18 refuses a plan [TAG] that
# fully matches any of them, because `entry` would route that KEY away from the plan row.
ADDENDUM_N = r"[0-9]+(?:\.[0-9]+)?[a-z]?"
KEY_SHAPES = (
    r"D[0-9]+",
    r"K[0-9]+",
    r"U[0-9]+[a-z]?",
    r"D[0-9]+\.[0-9]+",
    r"D[0-9]+\.a" + ADDENDUM_N,
    r"[a-z0-9]+(?:-[a-z0-9]+)*",
)

PLAN_PATH = "docs/dev/plan.md"
COMPLETED_PATH = "docs/dev/plan_completed.md"

PROFILES = [
    dict(name="decisions", index="docs/dev/decisions.md", details="docs/dev/decisions_details.md", id=r"D[0-9]+",
         states=("live", "sup", "part", "retired", "absorbed", "?"), caps=(200, 300, 48 * 1024),
         level1="rulings list, `### ID.aN` headings, `later:`", work="-", form="dormant", dormant="unit 1",
         linter="doc_lint", extra=(), floor=None, aliases=True),
    dict(name="plan", index=PLAN_PATH, details=None, id=None,
         states=("not-started", "started", "blocked", "deferred"), caps=(90, 300, 48 * 1024),
         level1="next: trigger: status (...): refs:", work="not-started + blocked, level 1, by section",
         form="single", dormant=None, linter="plan_lint", extra=("docs/design/plan_row_bodies/",), floor=150),
    dict(name="completed", index=COMPLETED_PATH, details=None, id=None,
         states=(), caps=None, level1="the row's attribute lines", work="-",
         form="archive", dormant=None, linter="plan_lint", extra=(), floor=None),
    dict(name="known", index="docs/dev/known_issues.md", details="docs/dev/known_issues_details.md", id=r"K[0-9]+",
         states=(), caps=(180, 280, 32 * 1024), level1="first line of **Witness:** / **Fix:**",
         work="open states, level 1", form="dormant", dormant="unit 3", linter="doc_lint", extra=(), floor=None),
    dict(name="upstream", index="docs/dev/upstream_issues.md", details="docs/dev/upstream_issues_details.md",
         id=r"U[0-9]+[a-z]?", states=(), caps=(180, 280, 12 * 1024), level1="unit 4's", work="unit 4's",
         form="dormant", dormant="unit 4", linter="doc_lint", extra=(), floor=None),
]


def profile(name, profiles=None):
    for p in profiles or PROFILES:
        if p["name"] == name:
            return p
    return None


# FIXTURE profiles: used by `entry --selftest` (and tests/doc_lint) over a scratch root, never by the real tree.
# They exercise the routing rows, the pair form and --over-cap before the real profiles wake.
FIXTURE_PROFILES = [
    dict(name="fixdec", index="fixdec.md", details="fixdec_details.md", id=r"D[0-9]+", states=(),
         caps=(200, 300, 48 * 1024), level1="", work="-", form="pair", dormant=None, linter="-", extra=(),
         floor=None, aliases=True),
    dict(name="fixknown", index="fixknown.md", details="fixknown_details.md", id=r"K[0-9]+", states=(),
         caps=(180, 280, 32 * 1024), level1="", work="-", form="pair", dormant=None, linter="-", extra=(),
         floor=None),
    dict(name="fixplan", index="fixplan.md", details=None, id=None, states=(), caps=None, level1="",
         work="not-started + blocked, level 1, by section", form="single", dormant=None, linter="-", extra=(),
         floor=None),
    dict(name="fixarch", index="fixarch.md", details=None, id=None, states=(), caps=None, level1="", work="-",
         form="archive", dormant=None, linter="-", extra=(), floor=None),
    dict(name="fixdorm", index="fixdorm.md", details="fixdorm_details.md", id=r"U[0-9]+[a-z]?", states=(),
         caps=None, level1="", work="-", form="dormant", dormant="unit 9", linter="-", extra=(), floor=None),
]
