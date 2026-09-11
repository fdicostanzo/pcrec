r"""tests/rxtsource/build_c3_store.py -- the C3 THREE-WAY VERDICT's own
store instance (`docs/design/c3_three_way.md`), populated via the LOCAL
DIRECT-LINK adapter (`tests/oracle/local_adapter.py`), per Frank's ruling
(2026-09-10, relayed in this lane's brief): python is narrowed to a
TRANSCRIPTION-ERROR TRIPWIRE, and its one remaining actionable value is
INDEPENDENCE from the expectations -- so a python/expectation divergence is
NEVER a failure once libpcre2 (the compatibility target, D26) CONFIRMS the
expectation. `tests/harness/verify_rxt.py` consults the committed store at
CHECK TIME and never a live library (the design's own rule, D77's economy
argument too: a live ctypes call per corpus case would be exactly the
per-question cost the store exists to amortize away).

**WHAT THIS SCRIPT DOES NOT DO: sweep the corpus.** The store's population
is not derived from a scan of every `.rxt` cell -- it is the small,
hand-enumerated, CITED set of questions this lane's mechanism actually needs
today: one `match-at` and six `captures` questions, one per currently-known
python-vs-expectation divergence (`tests/harness/verify_rxt.py`'s own run
over the whole corpus, 2026-09-10, finds EXACTLY these seven cells red and
no others -- see the design note's own table). A FUTURE divergence this
store does not cover is not silently accepted: `oracle_store.lookup` returns
a clean miss, `verify_rxt.py`'s store-uncovered bucket counts it, and the
cell FAILS exactly as it would have before this mechanism existed (the
design's own fallback rule) -- so under-covering the store is SAFE, and
growing it later (a corpus edit exposes a new divergence; re-run this
script with the new question appended) is the ordinary maintenance path,
never a silent hole.

**WHY THIS IS A COMMITTED `libpcre2-10.48` INSTANCE, not the `libpcre2-10.46`
reference `oracle_store/CLAUDE.md` otherwise reserves for committed data.**
This is a DEVIATION from that file's stated convention (committed = the
project's pin only; a local box's own resolved library is a gitignored
`build/oracle_cache/` cache) and Frank's brief for this lane directs it
explicitly, for a reason worth stating plainly rather than leaving as an
unexplained exception: no general (compile-accept/match-at/captures)
REMOTE adapter exists yet (`remote_adapter.py`'s own scope note: "membership
kind ONLY... D77, not built here"), and building one is explicitly out of
this lane's scope. Committing the LOCAL Homebrew 10.48 answers is SAFE
under the design's own staleness-impossibility argument (`oracle_interface.md`
§8 claim 2): `OracleId` carries `version`, so a box whose resolved libpcre2
is NOT 10.48 gets a clean miss on every row here, never a wrong answer
passed off as confirmed -- the same property that lets a version bump be
"a clean miss, never a stale hit" protects a version MISMATCH across boxes
identically. A Linux box with a different local libpcre2 simply falls back
to today's python-only verdict on these seven cells until its own local
instance is captured (or a real 10.46 remote capture supersedes this one --
this script's `remote` mode, added for exactly that future migration, is
untested here since no reference-box round trip was warranted for seven
questions this lane could answer over a two-second local ctypes call).

Usage:
    python3 tests/rxtsource/build_c3_store.py local
    python3 tests/rxtsource/build_c3_store.py remote   # NOT exercised by
                                                         # this lane -- see
                                                         # above; requires a
                                                         # general remote
                                                         # adapter this repo
                                                         # does not have yet
"""
import datetime
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
_ORACLE_DIR = os.path.join(_ROOT, "tests", "oracle")
sys.path.insert(0, _ORACLE_DIR)

import oracle_store as os_  # noqa: E402
from local_adapter import LocalAdapter  # noqa: E402

STORE_ROOT = os.path.join(_ROOT, "oracle_store")

# ---------------------------------------------------------------------------
# THE QUESTION LIST. Each entry cites the exact .rxt file:line whose
# python-vs-expectation divergence it exists to confirm-or-refute --
# verify_rxt.py's own run over the whole corpus (2026-09-10) is the source
# of this list, not the other way around: a question here was ADDED because
# a real corpus cell diverged, never invented ahead of one.
# ---------------------------------------------------------------------------

# kind -> list of (question_fields_dict, cite)
QUESTIONS = {
    "match-at": [
        (
            {"pattern": r"^((?i)a)\1$", "subject": "aA", "startpos": 0},
            "tests/backrefs/d27/caseless.rxt:39 -- 'n \"aA\"' after "
            "'pattern ^((?i)a)\\1$'. Divergence class: pre-3.11 python "
            "compiles a non-leading global (?i) ANYWAY (with a "
            "DeprecationWarning) and applies it to the WHOLE pattern "
            "(including the \\1 comparison); PCRE2 scopes (?i) to its "
            "enclosing group, so the backreference compare stays "
            "case-sensitive and 'aA' does not match.",
        ),
    ],
    "captures": [
        (
            {"pattern": "((a)|ab){0,12}?c", "subject": "abc", "startpos": 0,
             "nslots": 2},
            "tests/counterk/counterk.rxt:568 -- 'g 1 0 2' after "
            "'m \"abc\" 0 3' under 'pattern ((a)|ab){0,12}?c'. Divergence "
            "class: capture-timing in a LAZY counted alternation -- "
            "python's group-1 span reflects only the LAST alternative "
            "taken per iteration, not the whole repeated group's start.",
        ),
        (
            {"pattern": "((a)|ab){0,12}?c", "subject": "zabc", "startpos": 0,
             "nslots": 2},
            "tests/counterk/counterk.rxt:626 -- 'g 1 1 3' after "
            "'m \"zabc\" 1 4' under 'pattern ((a)|ab){0,12}?c'. Same class "
            "as :568, different subject.",
        ),
        (
            {"pattern": "((a)|ab){0,17}?c", "subject": "abc", "startpos": 0,
             "nslots": 2},
            "tests/counterk/counterk.rxt:644 -- 'g 1 0 2' after "
            "'m \"abc\" 0 3' under 'pattern ((a)|ab){0,17}?c'. Same class "
            "as :568, different residue (K=17 vs K=12).",
        ),
        (
            {"pattern": "((a)|ab){0,17}?c", "subject": "zabc", "startpos": 0,
             "nslots": 2},
            "tests/counterk/counterk.rxt:702 -- 'g 1 1 3' after "
            "'m \"zabc\" 1 4' under 'pattern ((a)|ab){0,17}?c'. Same class "
            "as :626, different residue.",
        ),
        (
            {"pattern": "(?!(a)x)ab", "subject": "ab", "startpos": 0,
             "nslots": 2},
            "tests/lookaround/captures.rxt:59 -- 'g 1 -1 -1' after "
            "'m \"ab\" 0 2' under 'pattern (?!(a)x)ab'. Divergence class: "
            "negative-lookahead capture handling -- python RETAINS the "
            "group-1 capture made during the assertion body's FAILED "
            "attempt ('a' matched, then 'x' failed against 'b'); PCRE2's "
            "trail rewind on assertion failure discards it, per the "
            "module's own C2 semantics (lookaround_design.md).",
        ),
        (
            {"pattern": "(?!(a)x)(a)", "subject": "ab", "startpos": 0,
             "nslots": 2},
            "tests/lookaround/captures.rxt:67 -- 'g 1 -1 -1' after "
            "'m \"ab\" 0 1' under 'pattern (?!(a)x)(a)'. Same class as "
            ":59, with a second group outside the assertion (retained, "
            "and NOT part of the divergence -- group 2 already agrees).",
        ),
    ],
}


def _run(cmd):
    return subprocess.run(cmd, cwd=_ROOT, capture_output=True,
                           text=True, timeout=30)


def build_local():
    adapter = LocalAdapter()
    oid = adapter.oracle_id()
    print("oracle_id:", oid)

    git_commit = _run(["git", "rev-parse", "--short", "HEAD"]).stdout.strip()
    host = _run(["hostname"]).stdout.strip()
    now = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")

    for kind, qlist in QUESTIONS.items():
        batch = [(kind, qfields) for qfields, _cite in qlist]
        answers = adapter.answer(batch)
        rows = [(qfields, ans) for (qfields, _cite), ans
                in zip(qlist, answers)]
        path = os_.store_path(STORE_ROOT, oid, kind)
        n = os_.write_store(
            path, oid, kind, rows,
            captured_at=now,
            captured_by=host,
            command="tests/rxtsource/build_c3_store.py local "
                    "(commit %s)" % (git_commit or "unknown"),
        )
        print("wrote %d row(s) to %s" % (n, path))
        for (qfields, cite), ans in zip(qlist, answers):
            print("  %r -> %r  [%s]" % (qfields, ans, cite.split(" -- ")[0]))


def build_remote():
    raise NotImplementedError(
        "no general (non-membership) remote adapter exists yet -- see this "
        "module's own header. Capture via 'local' today; migrate to a real "
        "10.46 reference capture once remote_adapter.py grows match-at/"
        "captures support (docs/design/oracle_interface.md §9 Step 4).")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("local", "remote"):
        print(__doc__)
        sys.exit(2)
    if sys.argv[1] == "local":
        build_local()
    else:
        build_remote()
