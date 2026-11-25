#!/usr/bin/env python3
"""Verify every mech sabotage's SAB_BEFORE anchor still occurs in its target
file. A stale anchor means the sabotage silently fails to apply, i.e. a
sabotage row that certifies nothing.

Pure grep -- no builds, seconds to run -- which is what makes it usable as a
standing tripwire beside `make mech`'s build-per-sabotage sweep. It was that
gap that let seven anchors drift undetected for weeks.

Graduated from the [M6-READ] lane. Its root was HARDCODED to that lane's
worktree, so it ran nowhere else once the worktree was removed; the root is
now derived from this file's own location, the same way every tests/ script
derives ROOT_DIR from BASH_SOURCE. Run it from anywhere.

Modes (lane plantfix2, review r94):
  (none)         both halves: the mech anchors, then the runner plant pass. Exit 1 on either.
  --plant-only   the runner plant pass alone (the self-test's per-case run; same exit rule).
  --selftest     the plant pass's STANDING CONTROL (r94 CA-5): planted faults in copies of
                 the tracked tree, each red with its own status word, the clean copy green;
                 plus the applier's decoder/apply rows. `--serial` runs the cases one by
                 one (the default is a pool; the output is identical). Run by [SABANCHOR].
"""
import json, os, re, shutil, signal, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sabdir = os.path.join(root, "tests/mech/sabotages")


def read_row(path):
    """One mech row's SAB_* values, asked of bash (the shell that will run them):
    (None, [FILE, BEFORE, COUNT, FILE2, BEFORE2, COUNT2, AFTER, AFTER2, SUITES, '']) or
    (why, None). The mech half and the plant pass's twin check both read rows through this."""
    out = subprocess.run(
        ["bash", "-c",
         'set -a; SAB_ID=; SAB_FILE=; SAB_BEFORE=; SAB_AFTER=; SAB_COUNT=; '
         'SAB_FILE2=; SAB_BEFORE2=; SAB_AFTER2=; SAB_COUNT2=; SAB_SUITES=; . "%s"; '
         'printf "%%s\\x00%%s\\x00%%s\\x00%%s\\x00%%s\\x00%%s\\x00%%s\\x00%%s\\x00%%s\\x00" '
         '"$SAB_FILE" "$SAB_BEFORE" "${SAB_COUNT:-1}" '
         '"$SAB_FILE2" "$SAB_BEFORE2" "${SAB_COUNT2:-1}" "$SAB_AFTER" "$SAB_AFTER2" "$SAB_SUITES"' % path],
        capture_output=True, text=True)
    if out.returncode != 0 or out.stderr.strip():
        why = (out.stderr.strip().splitlines() or ["exit %d" % out.returncode])[-1]
        return "DOES NOT SOURCE: " + why[:70], None
    return None, out.stdout.split("\x00")


# THREE OUTCOMES, and keeping them apart is the point of this tool.
#
#   unreadable  the row cannot be READ -- it does not parse, or it names no
#               target, or it carries no anchor. Says nothing about the anchor;
#               says the tripwire is blind to this row.
#   stale       the row reads fine and its anchor does NOT occur in its target.
#   (neither)   fine.
#
# The first class used to be a silent `continue`, which scored an unreadable
# row as healthy -- a blind spot of exactly the kind this tool exists to catch,
# and this tree's catalogue lesson 9 (extraction helpers hard-fail on empty,
# never default). Found by a positive control, after that control's own first
# attempt was itself vacuous: the sabotage regex matched an ESCAPED quote and
# never corrupted the anchor at all, so the resulting "all resolve" was read as
# a checker failure when in fact nothing had been sabotaged. Prove the sabotage
# reached the target before believing what the check says about it.
# [M6.5.2-FIX] A ROW MAY CARRY A SECOND SITE, and this tool checks BOTH.
# `run_sabotage_matrix.sh` grew an optional SAB_FILE2/BEFORE2/AFTER2/COUNT2
# for S108, whose claim needs two independent gates removed at once. A second
# site the tripwire did not read would be exactly the blind spot this file
# exists to close -- a stale anchor there fails the row's apply at mech time
# and nowhere earlier. SITES are counted and printed alongside rows, so
# "sabotages checked: 118" can never again be mistaken for "anchors checked".
def mech_pass():
    unreadable, stale = [], []
    sites = 0
    for fn in sorted(f for f in os.listdir(sabdir) if f.endswith(".sh")):
        path = os.path.join(sabdir, fn)
        # SAB_FILE / SAB_BEFORE are shell assignments; ask bash for their values so
        # quoting and continuations are handled by the shell that will run them.
        # stderr is CAPTURED, never discarded: a file that fails to source is the
        # case that used to vanish.
        why, parts = read_row(path)
        if why:
            unreadable.append((fn, why))
            continue
        if len(parts) < 2:
            unreadable.append((fn, "NO SAB_FILE/SAB_BEFORE EXTRACTED"))
            continue
        tgt, before = parts[0].strip(), parts[1]
        # [M6.4.4] the EXACT-COUNT check: mech's apply (tests/mech/lib/replace.py)
        # refuses unless the anchor occurs exactly SAB_COUNT times, so a presence-
        # only check here passed S48 while mech scored it ANOMALY (the block had
        # been duplicated by a refactor). The two instruments now ask the same question.
        try:
            want = int((parts[2] if len(parts) > 2 else "1").strip() or "1")
        except ValueError:
            want = 1
        if not tgt:
            unreadable.append((fn, "SAB_FILE IS EMPTY"))
            continue
        if not before.strip():
            unreadable.append((fn, "SAB_BEFORE IS EMPTY"))
            continue
        tp = os.path.join(root, tgt)
        if not os.path.exists(tp):
            stale.append((fn, tgt, "TARGET MISSING"))
            continue
        body = open(tp, errors="replace").read()
        sites += 1
        if before not in body:
            stale.append((fn, tgt, "ANCHOR NOT FOUND"))
        elif body.count(before) != want:
            stale.append((fn, tgt, "ANCHOR COUNT %d, SAB_COUNT %d" % (body.count(before), want)))

        # The optional SECOND site, asked the identical question. A row that names
        # SAB_FILE2 with no anchor is UNREADABLE rather than fine: the matrix will
        # score it ANOMALY, and this tool must not say "resolves" about a site it
        # could not read.
        tgt2 = parts[3].strip() if len(parts) > 3 else ""
        if tgt2:
            before2 = parts[4] if len(parts) > 4 else ""
            try:
                want2 = int((parts[5] if len(parts) > 5 else "1").strip() or "1")
            except ValueError:
                want2 = 1
            if not before2.strip():
                unreadable.append((fn, "SAB_FILE2 SET BUT SAB_BEFORE2 IS EMPTY"))
            else:
                tp2 = os.path.join(root, tgt2)
                sites += 1
                if not os.path.exists(tp2):
                    stale.append((fn, tgt2, "SITE 2: TARGET MISSING"))
                else:
                    body2 = open(tp2, errors="replace").read()
                    if before2 not in body2:
                        stale.append((fn, tgt2, "SITE 2: ANCHOR NOT FOUND"))
                    elif body2.count(before2) != want2:
                        stale.append((fn, tgt2, "SITE 2: ANCHOR COUNT %d, SAB_COUNT2 %d"
                                      % (body2.count(before2), want2)))

    print("sabotages checked:", len([f for f in os.listdir(sabdir) if f.endswith('.sh')]),
          "(%d anchor sites)" % sites)
    if unreadable:
        print("UNREADABLE ROWS:", len(unreadable), "-- the tripwire is BLIND to these")
        for fn, why in unreadable:
            print("  %-42s %s" % (fn, why))
    if stale:
        print("STALE ANCHORS:", len(stale))
        for fn, tgt, why in stale:
            print("  %-42s %-24s %s" % (fn, tgt, why))
    if not unreadable and not stale:
        print("all anchors resolve")
    return bool(unreadable or stale)


# ---------------------------------------------------------------------------
# THE RUNNER PLANT PASS (lane plantfix, 2026-11-24, FUW-12's class, triage
# docs/dev/lanes/plantri_report.md; review r94's fixes, lane plantfix2). The four
# shell runners carry plants of their own -- a `plant_spec` case function and a
# `PLANTS` id list, applied by their `--plant ID` / `--plants` modes, which nothing
# runs automatically -- and the mech half never read them: four FROM texts went
# stale and nothing noticed. The pass reads each plant through THE RUNNER'S OWN
# APPLIER: every runner's `--plant-check` mode hands its edits, built by the same
# `plant_edits` its --plants mode applies, to tests/lib/plants.py's `check` entry,
# which runs the apply entry's own loop over an in-memory copy of the files the
# --plant copy holds (r94 CA-1/CA-6). There is no second decoder here; this pass
# only discovers, runs, parses and counts.
#
#   discovery   a RUNNER is a file that names tests/lib/plants.py (any non-.md file
#               the tree holds: `git ls-files -co --exclude-standard`) AND defines
#               plant_spec in any spelling (`plant_spec()`, `plant_spec ()`,
#               `function plant_spec`). Either without the other is UNREADABLE
#               (r94 CA-3), unless NOT_RUNNERS declares the file, with its reason
#               (a declared entry that no longer names the applier is red: no
#               vacuous exemption). A runner with no --plant-check mode is
#               UNREADABLE and is never run (it would run the suite).
#   per plant   STALE / AMBIGUOUS / MISSING FILE / NO SPEC / UNDECODABLE per edit,
#               ORPHAN for a plant_spec case PLANTS does not list, BAD LABEL for a
#               case label that is no id (labels read from bash's own
#               `declare -f plant_spec`, r94 CA-2).
#   population  "runner plants checked: N", and each runner held to its EXACT pin
#               in PLANT_PINS (r94 CA-4): a runner missing, unpinned, or off its pin
#               in either direction is red and named. Move a pin in the change that
#               moves its plants.
#   twins       (r94 GF-1) an id that is both a runner plant and a
#               tests/mech/sabotages row must be DECLARED a twin by its runner
#               (PLANT_TWINS) -- else it is an id COLLISION -- and a declared twin
#               must be the same plant: each edit's file, FROM and TO (decoded by
#               the runner's `--plant-check dump`, plants.py's decoder) equal to the
#               row's SAB_FILE/BEFORE/AFTER (and site 2) once C comments (the
#               row's `/* SABOTAGE Sxxxx */` marker among them), `#` comments in a
#               .py target, and whitespace runs are normalised. A twin is the same plant
#               with the same DETECTOR too (lane s3012fix, S3012: its row moved to arm g2win
#               while the runner copy stayed in run_g2_pres.sh, GREEN for 11 days): the
#               twin's runner must be run, in its DEFAULT mode, by an arm among its row's
#               SAB_SUITES -- else TWIN DETECTOR MOVED. Which arm runs which runner is READ
#               from run_sabotage_matrix.sh's arm table (each `NAME)` block that scores an
#               arm, its `bash "$tree/X"` calls with no argument), closed over the scripts
#               those run (`bash "$ROOT/X"`, no argument: memfnfinder -> run_finder.sh ->
#               run_proof.sh); an arm passing a mode (g2v: run_g2_win.sh --v) runs another
#               detector and does not count. A table that yields no arm is UNREADABLE.
#   explicit    PLANT_TWINS is ONE literal assignment of ids (`PLANT_TWINS="S1 S2"`), and
#               the dump's declared twins are exactly its ids: `"$PLANTS"` (S3012's
#               declaration: every new plant a twin unasked) or any other spelling is
#               TWINS NOT EXPLICIT.
#
# The runners run CONCURRENTLY, each in its own session, under ONE shared deadline
# (r94 PAR-2/PAR-3): on the deadline the whole process group is killed and the
# pipes read with a bound, so a grandchild holding them cannot hang the pass.
PLANT_PINS = {   # exact plant count per runner (lane plantfix2, 2026-11-24; S3012 pres -> win, lane s3012fix)
    "memfn/tests/run_g2_win.sh": 39,
    "memfn/tests/run_g2_pres.sh": 34,
    "tests/memfn/run_proof.sh": 6,
    "tests/memfn/run_wreply.sh": 2,
}
NOT_RUNNERS = {  # files that name the applier and are not runners: path -> why
    "docs/dev/lanes/plantfix_evidence/applier_compare.sh": "lane plantfix's one-shot evidence, run by no suite",
    "docs/dev/lanes/plantfix_evidence/twincmp.sh": "lane plantfix's one-shot evidence, run by no suite",
    "docs/dev/lanes/plantfix_evidence/twin_census.py": "lane plantfix's one-shot evidence, run by no suite",
    "docs/dev/lanes/plantfix2_evidence/harness.py": "lane plantfix2's mutant harness (evidence), run by no suite",
}
APPLIER = "tests/lib/plants.py"
DEFINES = re.compile(rb"^[ \t]*(function[ \t]+plant_spec\b|plant_spec[ \t]*\([ \t]*\))", re.M)


def tree_files():
    """The tree's files: tracked plus untracked-not-ignored (git's own view of the tree,
    which is what keeps a lane's nested worktrees/ and build/ out of it)."""
    out = subprocess.run(["git", "-C", root, "ls-files", "-z", "-co", "--exclude-standard"],
                         capture_output=True)
    if out.returncode != 0:
        return None
    return sorted(set(f.decode() for f in out.stdout.split(b"\0") if f))


def discover():
    """(runners, unreadable): runners = the sorted rel paths that name the applier and
    define plant_spec; unreadable = [(rel, why)] for every mismatch."""
    files = tree_files()
    if files is None:
        return [], [(".", "git ls-files FAILED: the tree cannot be listed, no runner was read")]
    me = os.path.relpath(os.path.abspath(__file__), root)
    callers, definers = set(), set()
    for f in files:
        if f.endswith(".md") or f in (me, APPLIER):
            continue
        fp = os.path.join(root, f)
        if not os.path.isfile(fp):
            continue
        b = open(fp, "rb").read()
        if b"plant" not in b:
            continue
        if APPLIER.encode() in b:
            callers.add(f)
        if DEFINES.search(b):
            definers.add(f)
    bad = []
    for f in sorted(callers - definers):
        if f not in NOT_RUNNERS:
            bad.append((f, "NAMES %s BUT DEFINES NO plant_spec" % APPLIER))
    for f in sorted(definers - callers):
        bad.append((f, "DEFINES plant_spec BUT NEVER NAMES %s" % APPLIER))
    for f in sorted(NOT_RUNNERS):
        if f not in callers or f in definers:
            bad.append((f, "DECLARED NOT A RUNNER (NOT_RUNNERS) BUT %s"
                        % ("DEFINES plant_spec" if f in definers else "NO LONGER NAMES THE APPLIER")))
    return sorted(callers & definers), bad


def run_all(cmds, budget):
    """Run every (key, argv) concurrently, each in its own session, under ONE shared
    deadline, each drained by its own thread: {key: (rc, out, err) or (None, why, '')}.
    On the deadline the process GROUP is killed and the pipes read with a bound, so a
    grandchild holding them cannot hang the pass (r94 PAR-2/PAR-3)."""
    env = dict(os.environ, CC_RESOLVE_ANNOUNCED="1")   # cc_resolve's notice; any OTHER stderr is a finding
    deadline = time.monotonic() + budget

    def one(argv):
        pr = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, env=env, start_new_session=True)
        try:
            out, err = pr.communicate(timeout=max(0.0, deadline - time.monotonic()))
            return pr.returncode, out, err
        except subprocess.TimeoutExpired:
            try:
                os.killpg(pr.pid, signal.SIGKILL)
            except OSError:            # the group is gone already
                pass
            try:
                pr.communicate(timeout=5)
                return None, "--plant-check TIMED OUT (%g s shared deadline)" % budget, ""
            except subprocess.TimeoutExpired:
                for s in (pr.stdout, pr.stderr):
                    s.close()
                return None, ("--plant-check TIMED OUT (%g s shared deadline), ITS PIPES "
                              "STILL HELD after the group kill" % budget), ""

    with ThreadPoolExecutor(max_workers=max(1, len(cmds))) as ex:
        futs = [(key, ex.submit(one, argv)) for key, argv in cmds]
        return {key: f.result() for key, f in futs}


def norm(text, path):
    """Twin equality's normal form: C comments (the mech row's `/* SABOTAGE Sxxxx */`
    marker among them), `#` comments in a .py target, whitespace runs."""
    if path.endswith(".py"):
        text = re.sub(r"#[^\n]*", "", text)
    else:
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        text = re.sub(r"//[^\n]*", "", text)
    return " ".join(text.split())


MATRIX = "tests/mech/run_sabotage_matrix.sh"
ARM_BLOCK = re.compile(r"^ {12}([A-Za-z0-9_|-]+)\)[ \t]*\n(.*?)^ {16};;[ \t]*$", re.M | re.S)
# a DEFAULT-mode call: the quoted script, then (past a continuation) a redirect or the line's end
DEFAULT_CALL = r'^[^#\n]*\bbash "\$%s/([^"]+)"[ \t]*(?:\\\n[ \t]*)?(?:[<>]|2>|$)'


def arm_runners():
    """(why, {script rel: {arm}}): every matrix arm and the scripts it runs in DEFAULT mode,
    closed over the scripts those run. why is None, or the reason the table is unreadable."""
    mp = os.path.join(root, MATRIX)
    if not os.path.isfile(mp):
        return "%s MISSING" % MATRIX, {}
    runs = {}
    narms = 0
    for m in ARM_BLOCK.finditer(open(mp, errors="replace").read()):
        if "score_arm " not in m.group(2):
            continue
        narms += 1
        todo = [(c, set()) for c in re.findall(DEFAULT_CALL % "tree", m.group(2), re.M)]
        while todo:
            rel, seen = todo.pop()
            rel = os.path.normpath(rel)
            if rel in seen:
                continue
            for arm in m.group(1).split("|"):
                runs.setdefault(rel, set()).add(arm)
            fp = os.path.join(root, rel)
            if os.path.isfile(fp):
                todo += [(c, seen | {rel}) for c in
                         re.findall(DEFAULT_CALL % "ROOT", open(fp, errors="replace").read(), re.M)]
    if not narms:
        return "%s: NO ARM READ (no `NAME)` block that scores an arm)" % MATRIX, {}
    return None, runs


TWINS_ASSIGN = re.compile(r"^[ \t]*(?:export[ \t]+|declare[^\n=]*[ \t])?PLANT_TWINS\+?=", re.M)
TWINS_LITERAL = re.compile(r'^PLANT_TWINS="([^"$`\\]*)"[ \t]*(?:#[^\n]*)?$', re.M)


def explicit_twins(rel, dump, p_bad):
    """(lane s3012fix) PLANT_TWINS one literal id list, and the dump's twins exactly it."""
    src = open(os.path.join(root, rel), errors="replace").read()
    n = len(TWINS_ASSIGN.findall(src))
    lit = TWINS_LITERAL.findall(src)
    ids = lit[0].split() if len(lit) == 1 else []
    # (an id-shaped token is not asked here: any other token reaches the dump as a declared
    # twin PLANTS does not list, TWIN NOT IN PLANTS)
    if n != 1 or len(lit) != 1:
        p_bad.append((rel, ("-", "-", "TWINS NOT EXPLICIT", "0",
                            "PLANT_TWINS must be ONE literal id list (`PLANT_TWINS=\"S1 S2\"`): "
                            "%d assignment(s), %d literal" % (n, len(lit)))))
        return
    declared = {r[0] for r in dump if r[2] == "twin"}
    if declared != set(ids):
        p_bad.append((rel, ("-", "-", "TWINS NOT EXPLICIT", "0",
                            "the dump declares %d twin(s), the PLANT_TWINS literal %d (the mode "
                            "does not pass the literal)" % (len(declared), len(set(ids))))))


def twin_check(rel, dump, p_bad, runs):
    """GF-1 over one runner's dump rows: (ids, twins compared). Appends findings to p_bad.
    runs: arm_runners()'s map, the arms that run each script in its default mode."""
    plants, twins, notlisted = {}, set(), []
    for r in dump:
        if r[2] == "twin":
            twins.add(r[0])
        if r[1] == "-":
            notlisted.append(r[0])
        elif r[1] != "0/0":
            plants.setdefault(r[0], []).append(r)
        else:
            plants.setdefault(r[0], [])
    for pid in notlisted:
        p_bad.append((rel, (pid, "-", "TWIN NOT IN PLANTS", "0", "declared in PLANT_TWINS, not a plant")))
    ncmp = 0
    allrows = sorted(f for f in os.listdir(sabdir) if f.endswith(".sh"))
    byid = {pid: [f for f in allrows if f.split("_")[0] == pid] for pid in plants}
    wanted = [m[0] for pid, m in byid.items() if pid in twins and len(m) == 1]
    with ThreadPoolExecutor(max_workers=8) as ex:
        got = dict(zip(wanted, ex.map(lambda f: read_row(os.path.join(sabdir, f)), wanted)))
    for pid, rows in plants.items():
        mech = byid[pid]
        if not mech:
            if pid in twins:
                p_bad.append((rel, (pid, "-", "TWIN WITHOUT ROW", "0", "declared a twin; tests/mech/sabotages has no %s row" % pid)))
            continue
        if pid not in twins:
            p_bad.append((rel, (pid, "-", "ID COLLISION", "0", "tests/mech/sabotages/%s is another plant's id (declare a twin or renumber)" % mech[0])))
            continue
        if len(mech) > 1:
            p_bad.append((rel, (pid, "-", "ID COLLISION", "0", "%d mech rows carry the id" % len(mech))))
            continue
        why, parts = got[mech[0]]
        if why:
            p_bad.append((rel, (pid, "-", "TWIN UNREADABLE", "0", why)))
            continue
        sites = [(parts[0].strip(), parts[1], parts[6])]
        if parts[3].strip():
            sites.append((parts[3].strip(), parts[4], parts[7]))
        ncmp += 1
        suites = parts[8].split() if len(parts) > 8 else []
        mine = runs.get(rel, set())
        if not set(suites) & mine:
            p_bad.append((rel, (pid, "-", "TWIN DETECTOR MOVED", "0",
                                "%s's SAB_SUITES (%s) run no arm that runs this runner (%s)"
                                % (mech[0], " ".join(suites) or "none",
                                   " ".join(sorted(mine)) or "no arm does"))))
        if len(sites) != len(rows):
            p_bad.append((rel, (pid, "-", "TWIN DRIFT", "0", "%d edits, its row %d sites" % (len(rows), len(sites)))))
            continue
        for r, (sf, sb, sa) in zip(rows, sites):
            try:
                a, b = json.loads(r[4]), json.loads(r[5])
            except ValueError:
                p_bad.append((rel, (pid, r[1], "TWIN UNREADABLE", "0", "dump row: " + r[3])))
                break
            if os.path.normpath(r[3]) != os.path.normpath(sf):
                p_bad.append((rel, (pid, r[1], "TWIN DRIFT", "0", "file %s, its row %s" % (r[3], sf))))
            elif norm(a, sf) != norm(sb, sf):
                p_bad.append((rel, (pid, r[1], "TWIN DRIFT", "0", "FROM differs from %s" % mech[0])))
            elif norm(b, sf) != norm(sa, sf):
                p_bad.append((rel, (pid, r[1], "TWIN DRIFT", "0", "TO differs from %s" % mech[0])))
    return set(plants), ncmp


def plant_pass():
    runners, p_unreadable = discover()
    p_bad = []
    why, runs = arm_runners()
    if why:
        p_unreadable.append((MATRIX, "ARM TABLE UNREADABLE: " + why))
    nplants = nedits = ntwins = 0
    counts, seen = {}, {}
    cmds = []
    for rel in runners:
        if '"--plant-check"' not in open(os.path.join(root, rel), errors="replace").read():
            p_unreadable.append((rel, "DEFINES plant_spec BUT HAS NO --plant-check MODE"))
            continue
        for mode in ("check", "dump"):
            cmds.append(((rel, mode), ["bash", os.path.join(root, rel), "--plant-check", mode]))
    res = run_all(cmds, float(os.environ.get("PLANT_CHECK_TIMEOUT", "120")))
    for rel in runners:
        if (rel, "check") not in res:
            continue
        bad_here = False
        for mode in ("check", "dump"):
            rc, out, err = res[(rel, mode)]
            if rc is None:
                p_unreadable.append((rel, out + ("" if mode == "check" else " (dump)")))
                bad_here = True
                break
            lines = out.split("\n")
            if mode == "dump":
                rows = [l.split("\t") for l in lines if l]
                if err.strip() or rc != 0 or any(len(r) != 6 for r in rows):
                    why = (err.strip().splitlines() or ["exit %d" % rc])[-1]
                    p_unreadable.append((rel, "--plant-check dump UNREADABLE: " + why[:70]))
                    bad_here = True
                    break
                dump = rows
                continue
            summ = [l for l in lines if l.startswith("plant-check: ")]
            rows = [l.split("\t") for l in lines if l and not l.startswith("plant-check: ")]
            if err.strip() or rc not in (0, 1) or len(summ) != 1 \
                    or any(len(r) != 5 for r in rows):
                why = (err.strip().splitlines() or ["exit %d, %d summary line(s)" % (rc, len(summ))])[-1]
                p_unreadable.append((rel, "--plant-check UNREADABLE: " + why[:70]))
                bad_here = True
                break
            try:
                P, E, Bn = [int(x.split()[0]) for x in summ[0][len("plant-check: "):].split(", ")]
            except ValueError:
                p_unreadable.append((rel, "--plant-check SUMMARY UNREADABLE: " + summ[0][:60]))
                bad_here = True
                break
            bad = [r for r in rows if r[2] != "OK"]
            ids = {r[0] for r in rows if r[1] != "-"}
            if len(ids) != P or len(bad) != Bn or (rc == 0) != (Bn == 0):
                p_unreadable.append((rel, "--plant-check INCONSISTENT: %d ids, summary %s" % (len(ids), summ[0])))
                bad_here = True
                break
            check_ids = ids
        if bad_here:
            continue
        explicit_twins(rel, dump, p_bad)
        dump_ids, ncmp = twin_check(rel, dump, p_bad, runs)
        if dump_ids != check_ids:
            p_unreadable.append((rel, "--plant-check check and dump name different plants"))
            continue
        for pid in sorted(check_ids):
            if pid in seen:
                p_bad.append((rel, (pid, "-", "DUPLICATE ID", "0", "also a plant of " + seen[pid])))
            seen[pid] = rel
        counts[rel] = P
        nplants += P
        nedits += E
        ntwins += ncmp
        for r in bad:
            p_bad.append((rel, r))
    pins = []
    for rel in sorted(set(PLANT_PINS) | set(counts)):
        if rel not in PLANT_PINS:
            pins.append("%s: %d plants read, NOT PINNED in PLANT_PINS" % (rel, counts[rel]))
        elif rel not in counts:
            pins.append("%s: pinned at %d, NOT READ (left discovery, or unreadable above)" % (rel, PLANT_PINS[rel]))
        elif counts[rel] != PLANT_PINS[rel]:
            pins.append("%s: %d plants read, pinned at %d" % (rel, counts[rel], PLANT_PINS[rel]))
    print("runner plants checked: %d (%d edits, %d runners, each at its pin)"
          % (nplants, nedits, len(counts)) if not pins else
          "runner plants checked: %d (%d edits, %d runners)" % (nplants, nedits, len(counts)))
    print("runner plant twins checked: %d (declared twins of a tests/mech/sabotages row)" % ntwins)
    if p_unreadable:
        print("UNREADABLE RUNNERS:", len(p_unreadable), "-- the plant pass is BLIND to these")
        for rel, why in p_unreadable:
            print("  %-42s %s" % (rel, why))
    if pins:
        print("RUNNER PLANT PINS:", len(pins), "-- a runner left, joined or moved its population")
        for ln in pins:
            print("  " + ln)
    if p_bad:
        print("BAD RUNNER PLANTS:", len(p_bad))
        for rel, (pid, edit, st, c, path) in p_bad:
            print("  %-30s %-6s edit %-4s %-18s count %s  %s" % (rel, pid, edit, st, c, path))
    p_fail = bool(p_unreadable or p_bad or pins)
    if not p_fail:
        print("all runner plants apply, every shared id is an equal declared twin of a row whose suites run its runner")
    return p_fail


# ---------------------------------------------------------------------------
# THE SELF-TEST (r94 CA-5/CA-6): the plant pass's standing control, run by
# [SABANCHOR]. A copy of the tracked files this pass reads (SELFTEST_TREE, as
# they stand in the working tree, so an edited checker is the one tested), one
# git index in it (run_wreply.sh's file set and discovery ask git), then one
# HARDLINKED copy per case (a fault writes by replace, never in place). Each case
# runs `--plant-only` in its copy and must end with its rc AND print each of its
# words; the clean copy must be green. UNIT rows drive plants.py directly (the
# dialect rules and the apply loop's refusals, r94 CA-6).
SELFTEST_TREE = ("scripts/m6read_check_sab_anchors.py", "tests/lib", "tests/memfn", "memfn/src",
                 "memfn/tests", "docs/design/memfn/span_pick", "src/gen/emit_dfa.c",
                 "tests/mech/sabotages", MATRIX) + tuple(sorted(NOT_RUNNERS))
# of tests/mech/sabotages, only the rows whose id a pinned runner's text names (every
# twin and collision candidate; the other ~1350 rows are the mech half's, not read here)
WIN, PRES, PROOF, WREPLY = ("memfn/tests/run_g2_win.sh", "memfn/tests/run_g2_pres.sh",
                             "tests/memfn/run_proof.sh", "tests/memfn/run_wreply.sh")
NOMODE = ("#!/bin/bash\n# applies through tests/lib/plants.py\nplant_spec() {\n    case \"$1\" in\n"
          "    S9001) echo 'x.c@@a@@b' ;;\n    *) return 1 ;;\n    esac\n}\nPLANTS=\"S9001\"\n")


class Case:
    def __init__(self, t):
        self.t = t

    def rd(self, rel):
        return open(os.path.join(self.t, rel)).read()

    def wr(self, rel, s):
        p = os.path.join(self.t, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        tmp = p + ".selftest-new"
        open(tmp, "w").write(s)
        if os.path.exists(p):
            shutil.copymode(p, tmp)
        os.replace(tmp, p)        # a new inode: the base copy's link is never written

    def sub(self, rel, a, b):
        s = self.rd(rel)
        if s.count(a) != 1:
            raise RuntimeError("SELFTEST FIXTURE: %r occurs %d times in %s" % (a[:60], s.count(a), rel))
        self.wr(rel, s.replace(a, b))

    def mode(self, rel, line):
        """a line run first in rel's --plant-check mode"""
        self.sub(rel, 'if [ "${1:-}" = "--plant-check" ]; then\n',
                 'if [ "${1:-}" = "--plant-check" ]; then\n' + line + "\n")

    def unexec(self, rel, tail):
        """rel's --plant-check runs the applier WITHOUT exec, then `tail`"""
        s = self.rd(rel)
        i = s.index('if [ "${1:-}" = "--plant-check" ]; then\n')
        j = s.index('    exec python3 -I "$ROOT/tests/lib/plants.py"', i)
        k = s.index('\nfi\n', j)
        self.wr(rel, s[:j] + '    python3' + s[j + len('    exec python3'):k] + tail + s[k:])

    def case_line(self, rel, line):
        """a case line added to rel's plant_spec, before its default"""
        s = self.rd(rel)
        m = re.compile(r"\n[ \t]*\*\) return 1 ;;\n").search(s, s.index("plant_spec() {"))
        self.wr(rel, s[:m.start() + 1] + line + "\n" + s[m.start() + 1:])

    def row(self, pid):
        d = "tests/mech/sabotages"
        return [os.path.join(d, f) for f in sorted(os.listdir(os.path.join(self.t, d))) if f.split("_")[0] == pid][0]

    def mv(self, rel, rel2):
        os.makedirs(os.path.dirname(os.path.join(self.t, rel2)), exist_ok=True)
        os.replace(os.path.join(self.t, rel), os.path.join(self.t, rel2))


def plants_line(c, rel):
    return re.search(r'^PLANTS="([^"]*)"', c.rd(rel), re.M).group(1)


def s3012_to_pres(c):
    """S3012 put back where it was before lane s3012fix: out of the window runner (its case,
    PLANTS, PLANT_TWINS), into the presence runner's, its edit unchanged (the GF-1 hole)"""
    w = c.rd(WIN)
    m = re.search(r"\n    S3012\) #.*?\n(        echo [^\n]*;;)\n", w, re.S)
    c.wr(WIN, w[:m.start() + 1] + w[m.end():])
    c.sub(WIN, " S3118 S3012\"", " S3118\"")
    c.sub(WIN, 'PLANT_TWINS="S3012"', 'PLANT_TWINS=""')
    c.case_line(PRES, "    S3012) " + m.group(1).strip())
    c.sub(PRES, 'PLANTS="S3007 ', 'PLANTS="S3012 S3007 ')
    c.sub(PRES, 'PLANT_TWINS="S3007 ', 'PLANT_TWINS="S3012 S3007 ')


def suites(c, pid, val):
    c.wr(c.row(pid), c.rd(c.row(pid)) + '\nSAB_SUITES="%s"\n' % val)


# (name, fault, rc, words that must ALL be printed, wall bound or None, PLANT_CHECK_TIMEOUT)
CASES = [
    ("clean copy", lambda c: None, 0, ["all runner plants apply", "runner plants checked: 81 ", "runner plant twins checked: 39 "], None, None),
    ("stale FROM (win, its plant_spec)", lambda c: c.sub(WIN, "echo 'ofsskip.c@@    const int m[2] = { a, b };", "echo 'ofsskip.c@@    const int m[2] = { a, bXYZZY };"), 1, ["STALE", WIN], None, None),
    ("stale FROM (pres edit 2 of 2, the source moved)", lambda c: c.sub("memfn/src/compose.c", 'return kit_fail(art, "mf_define: the presence decision refuses this site: %s", pw);', 'return kit_fail(art, "mf_define: THE presence decision refuses this site: %s", pw);'), 1, ["S3064", "edit 2/2", "STALE"], None, None),
    ("stale @c0/ FROM (census0.py moved)", lambda c: c.sub("docs/design/memfn/span_pick/census0.py", 'off, kind, val = t.split(":", 2)', 'off, kind, val = t.split(":", 2)  # moved'), 1, ["STALE", "census0.py"], None, None),
    ("stale wreply PERT", lambda c: c.sub(WREPLY, "    bool reseed = wk && wk->nwalk >= 1 && us->cand.count >= 1@@", "    bool reseed = wk && wk->nwalkX >= 1 && us->cand.count >= 1@@"), 1, ["STALE", WREPLY], None, None),
    ("ambiguous FROM (wreply S1414's text twice)", lambda c: c.wr("src/gen/emit_dfa.c", c.rd("src/gen/emit_dfa.c") + '\n/*    [NK_RUN_PINNED] = { "run-pinned[-bounded]", WR_ANY, 1, 1, */\n'), 1, ["S1414", "AMBIGUOUS"], None, None),
    ("missing file (proof S1221)", lambda c: c.sub(PROOF, "echo 'compose.c@@long d = (long)t->offset + j;@@", "echo 'Xcompose.c@@long d = (long)t->offset + j;@@"), 1, ["S1221", "MISSING FILE"], None, None),
    ("@c0/ file outside the copy's set (CA-1)", lambda c: (c.case_line(PRES, "    S9301) echo '@c0/counts.py@@import collections\\n@@import collections  # S9301\\n' ;;"), c.sub(PRES, 'PLANTS="S3007 ', 'PLANTS="S9301 S3007 ')), 1, ["S9301", "MISSING FILE"], None, None),
    ("one file by two spellings (CA-1 alias)", lambda c: (c.case_line(PRES, "    S9302) echo 'vrun.c@@SPDX-License-Identifier: 0BSD@@SPDX (1)'\n        echo './vrun.c@@SPDX-License-Identifier: 0BSD@@SPDX (2)' ;;"), c.sub(PRES, 'PLANTS="S3007 ', 'PLANTS="S9302 S3007 ')), 1, ["S9302", "edit 2/2", "STALE"], None, None),
    ("an undecodable edit (wreply, a fourth @@ field)", lambda c: c.sub(WREPLY, "@@        if (us->wr_stated && 0 && !f->pf->u.pf.reseeds)' ;;", "@@        if (us->wr_stated && 0 && !f->pf->u.pf.reseeds)@@x' ;;"), 1, ["S1413", "UNDECODABLE"], None, None),
    ("PLANTS id with no case (NO SPEC)", lambda c: c.sub(PROOF, 'PLANTS="S1221', 'PLANTS="S9999 S1221'), 1, ["S9999", "NO SPEC"], None, None),
    ("ORPHAN, plain label", lambda c: c.case_line(PROOF, "    S9998) echo 'compose.c@@x@@y' ;;"), 1, ["S9998", "ORPHAN"], None, None),
    ("ORPHAN, alternation S1|S2)", lambda c: c.case_line(PROOF, "    S9997|S9996) echo 'compose.c@@x@@y' ;;"), 1, ["S9997", "S9996", "ORPHAN"], None, None),
    ("ORPHAN, a listed label widened", lambda c: c.sub(PROOF, "    S1225) #", "    S1225|S9995) #"), 1, ["S9995", "ORPHAN"], None, None),
    ("ORPHAN, label `S9994 )`", lambda c: c.case_line(PROOF, "    S9994 ) echo 'compose.c@@x@@y' ;;"), 1, ["S9994", "ORPHAN"], None, None),
    ("ORPHAN, quoted label", lambda c: c.case_line(PROOF, "    \"S9993\") echo 'compose.c@@x@@y' ;;"), 1, ["S9993", "ORPHAN"], None, None),
    ("BAD LABEL (a glob)", lambda c: c.case_line(PROOF, "    S12*) echo 'compose.c@@x@@y' ;;"), 1, ["S12*", "BAD LABEL"], None, None),
    ("runner deleted", lambda c: os.remove(os.path.join(c.t, WREPLY)), 1, ["RUNNER PLANT PINS", WREPLY, "NOT READ"], None, None),
    ("runner renamed .bash", lambda c: c.mv(WREPLY, WREPLY[:-3] + ".bash"), 1, ["NOT PINNED", WREPLY[:-3] + ".bash", "NOT READ"], None, None),
    ("runner moved to scripts/", lambda c: c.mv(WREPLY, "scripts/run_wreply.sh"), 1, ["scripts/run_wreply.sh", "NOT READ"], None, None),
    ("plant_spec respelled `plant_spec () {` (still read)", lambda c: c.sub(WREPLY, "plant_spec() {", "plant_spec () {"), 0, ["all runner plants apply"], None, None),
    ("PLANTS emptied", lambda c: c.sub(WREPLY, 'PLANTS="S1413 S1414"', 'PLANTS=""'), 1, ["ORPHAN", "pinned at 2"], None, None),
    ("pin up: a plant added (proof)", lambda c: (c.case_line(PROOF, "    S9101) plant_spec S1408 ;;"), c.sub(PROOF, 'PLANTS="S1221', 'PLANTS="S9101 S1221')), 1, [PROOF, "7 plants read, pinned at 6"], None, None),
    ("pin down: a plant removed (proof)", lambda c: (c.sub(PROOF, 'S1408 S3242"', 'S3242"'), c.wr(PROOF, re.sub(r"\n    S1408\).*?;;\n", "\n", c.rd(PROOF), count=1, flags=re.S))), 1, [PROOF, "5 plants read, pinned at 6"], None, None),
    ("fifth runner, no --plant-check mode", lambda c: c.wr("tests/zz/run_zz.sh", NOMODE), 1, ["tests/zz/run_zz.sh", "NO --plant-check MODE"], None, None),
    ("fifth runner `function plant_spec {`, no mode", lambda c: c.wr("tests/zz/run_zz.sh", NOMODE.replace("plant_spec() {", "function plant_spec {")), 1, ["tests/zz/run_zz.sh", "NO --plant-check MODE"], None, None),
    ("fifth runner under scripts/", lambda c: c.wr("scripts/run_zz.sh", NOMODE), 1, ["scripts/run_zz.sh", "UNREADABLE"], None, None),
    ("fifth runner under examples/", lambda c: c.wr("examples/zz/run_zz.sh", NOMODE), 1, ["examples/zz/run_zz.sh", "UNREADABLE"], None, None),
    ("defines plant_spec, never names the applier", lambda c: c.wr("examples/zz/run_zz.sh", NOMODE.replace("# applies through tests/lib/plants.py\n", "")), 1, ["examples/zz/run_zz.sh", "NEVER NAMES"], None, None),
    ("names the applier, defines no plant_spec", lambda c: c.wr("examples/zz/zz.py", "# python3 tests/lib/plants.py apply win x -- 'a@@b@@c'\n"), 1, ["examples/zz/zz.py", "DEFINES NO plant_spec"], None, None),
    ("a NOT_RUNNERS entry gone vacuous", lambda c: c.wr(sorted(NOT_RUNNERS)[0], "#!/bin/bash\n:\n"), 1, [sorted(NOT_RUNNERS)[0], "NO LONGER NAMES"], None, None),
    ("--plant-check prints garbage", lambda c: c.mode(PROOF, "    echo garbage"), 1, [PROOF, "UNREADABLE"], None, None),
    ("--plant-check prints a well-formed lie", lambda c: c.mode(PROOF, '    [ "${2:-check}" = check ] && printf "a\\tb\\tOK\\td\\te\\n"'), 1, [PROOF, "INCONSISTENT"], None, None),
    ("--plant-check dies (exit 3)", lambda c: c.mode(PROOF, "    exit 3"), 1, [PROOF, "exit 3"], None, None),
    ("--plant-check exits 0 silently", lambda c: c.mode(PROOF, "    exit 0"), 1, [PROOF, "UNREADABLE"], None, None),
    ("--plant-check writes stderr", lambda c: c.mode(PROOF, '    [ "${2:-check}" = check ] && echo oops >&2'), 1, [PROOF, "--plant-check UNREADABLE: oops"], None, None),
    ("--plant-check dump writes stderr", lambda c: c.mode(PROOF, '    [ "${2:-check}" = dump ] && echo oops >&2'), 1, [PROOF, "dump UNREADABLE: oops"], None, None),
    ("--plant-check's answer right, its exit 3", lambda c: c.unexec(PROOF, "; exit 3"), 1, [PROOF, "exit 3, 1 summary"], None, None),
    ("--plant-check prints its summary twice", lambda c: c.mode(PROOF, '    [ "${2:-check}" = check ] && echo "plant-check: %d plants, %d edits, 0 bad"' % (PLANT_PINS[PROOF], PLANT_PINS[PROOF])), 1, [PROOF, "2 summary line(s)"], None, None),
    ("--plant-check's summary unparsable", lambda c: c.unexec(PROOF, " | sed 's/^plant-check: [0-9]*/plant-check: many/'; exit \"${PIPESTATUS[0]}\""), 1, [PROOF, "SUMMARY UNREADABLE"], None, None),
    ("check and dump name different plants", lambda c: c.mode(PROOF, '    [ "${2:-check}" = dump ] && PLANTS="${PLANTS% *}"'), 1, [PROOF, "name different plants"], None, None),
    ("--plant-check dump dies", lambda c: c.mode(PROOF, '    [ "${2:-check}" = dump ] && exit 3'), 1, [PROOF, "dump UNREADABLE"], None, None),
    ("--plant-check reads only the first id", lambda c: c.sub(PROOF, "    for id in $PLANTS; do\n        if plant_edits", "    for id in ${PLANTS%% *}; do\n        if plant_edits"), 1, [PROOF, "ORPHAN"], None, None),
    ("--plant-check hangs (exec'd)", lambda c: c.mode(PROOF, "    exec sleep 300"), 1, [PROOF, "TIMED OUT"], 20, "3"),
    ("--plant-check's grandchild hangs holding the pipes (PAR-3)", lambda c: c.mode(PROOF, '    ( while :; do date > "$PLANT_ALIVE"; sleep 0.2; done ); exit 0'), 1, [PROOF, "TIMED OUT"], 20, "3"),
    ("a grandchild escapes the group, holding the pipes", lambda c: c.mode(PROOF, "    python3 -c 'import os, time; os.setsid(); time.sleep(30)' & exit 0"), 1, [PROOF, "PIPES STILL HELD"], 15, "3"),
    ("two runners hang: one shared deadline (PAR-2)", lambda c: (c.mode(PROOF, "    exec sleep 300"), c.mode(WIN, "    exec sleep 300")), 1, [PROOF, WIN, "TIMED OUT"], 20, "3"),
    ("twin drift: the runner's TO moved (proof S1221)", lambda c: c.sub(PROOF, "@@long d = (long)t->offset + j + (t->kind == MF_T_RUN);'", "@@long d = (long)t->offset + j + 2 * (t->kind == MF_T_RUN);'"), 1, ["S1221", "TWIN DRIFT"], None, None),
    ("twin drift: the mech row's FROM moved (S3045)", lambda c: c.wr(c.row("S3045"), c.rd(c.row("S3045")) + '\nSAB_BEFORE="${SAB_BEFORE}x"\n'), 1, ["S3045", "TWIN DRIFT"], None, None),
    ("twin drift: the mech row's file moved (S1221)", lambda c: c.wr(c.row("S1221"), c.rd(c.row("S1221")) + '\nSAB_FILE="memfn/src/generic.c"\n'), 1, ["S1221", "TWIN DRIFT", "file"], None, None),
    ("twin drift: the mech row grew a site 2 (S1221)", lambda c: c.wr(c.row("S1221"), c.rd(c.row("S1221")) + '\nSAB_FILE2="memfn/src/generic.c"\nSAB_BEFORE2="x"\nSAB_AFTER2="y"\n'), 1, ["S1221", "TWIN DRIFT", "its row 2 sites"], None, None),
    ("undeclared shared id (ID COLLISION)", lambda c: c.sub(PROOF, 'PLANT_TWINS="S1221 ', 'PLANT_TWINS="'), 1, ["S1221", "ID COLLISION"], None, None),
    ("the S1540 collision restored (GF-2)", lambda c: (c.sub(WIN, "    S1544) # code review r2", "    S1540) # code review r2"), c.sub(WIN, " S1544 S1541 ", " S1540 S1541 ")), 1, ["S1540", "ID COLLISION"], None, None),
    ("declared twin without a row", lambda c: c.sub(PROOF, 'PLANT_TWINS="S1221 ', 'PLANT_TWINS="S1408 S1221 '), 1, ["S1408", "TWIN WITHOUT ROW"], None, None),
    ("declared twin not in PLANTS", lambda c: c.sub(PROOF, 'PLANT_TWINS="S1221 ', 'PLANT_TWINS="S9990 S1221 '), 1, ["S9990", "TWIN NOT IN PLANTS"], None, None),
    # the DETECTOR half of a twin and the EXPLICIT declaration (lane s3012fix; S3012's GF-1 hole)
    ("S3012 restored to pres (its row's arm is g2win)", s3012_to_pres, 1, ["S3012", "TWIN DETECTOR MOVED", PRES], None, None),
    ("S3044's row re-aimed to g2win, the runner not", lambda c: suites(c, "S3044", "g2win"), 1, ["S3044", "TWIN DETECTOR MOVED", "g2win"], None, None),
    ("S3044's row to g2pres-asan (the same runner: green)", lambda c: suites(c, "S3044", "g2pres-asan"), 0, ["all runner plants apply"], None, None),
    ("S3012's row to g2v (a MODE of its runner, not it)", lambda c: suites(c, "S3012", "g2v"), 1, ["S3012", "TWIN DETECTOR MOVED", "g2v"], None, None),
    ("S1221's row with no SAB_SUITES", lambda c: suites(c, "S1221", ""), 1, ["S1221", "TWIN DETECTOR MOVED", "none"], None, None),
    ("run_finder.sh runs run_proof.sh in a mode (the closure)", lambda c: c.sub("tests/memfn/run_finder.sh", 'bash "$ROOT/tests/memfn/run_proof.sh" >', 'bash "$ROOT/tests/memfn/run_proof.sh" --reach >'), 1, ["S1221", "TWIN DETECTOR MOVED", PROOF], None, None),
    ("a non-arm block (scores no arm) running the runner", lambda c: (c.sub(MATRIX, "\n            g2pres)\n", '\n            zzfake)\n                bash "$tree/tests/memfn/run_proof.sh" > "$work/zz.log" 2>&1\n                ;;\n            g2pres)\n'), suites(c, "S1221", "zzfake")), 1, ["S1221", "TWIN DETECTOR MOVED", "zzfake"], None, None),
    ("the arm table gone", lambda c: os.remove(os.path.join(c.t, MATRIX)), 1, ["ARM TABLE UNREADABLE", "MISSING"], None, None),
    ("the arm table yields no arm", lambda c: c.wr(MATRIX, "#!/usr/bin/env bash\n:\n"), 1, ["ARM TABLE UNREADABLE", "NO ARM READ"], None, None),
    ("blanket PLANT_TWINS=\"$PLANTS\" (pres)", lambda c: c.wr(PRES, re.sub(r'^PLANT_TWINS="[^"]*"$', 'PLANT_TWINS="$PLANTS"', c.rd(PRES), count=1, flags=re.M)), 1, ["TWINS NOT EXPLICIT", PRES, "0 literal"], None, None),
    ("a second, blanket PLANT_TWINS after the literal (pres)", lambda c: c.sub(PRES, "\n# --plant-check [check|dump]", '\nPLANT_TWINS="$PLANTS"\n# --plant-check [check|dump]'), 1, ["TWINS NOT EXPLICIT", PRES, "2 assignment"], None, None),
    ("the mode passes $PLANTS, not the literal (win)", lambda c: c.sub(WIN, '--twins "$PLANT_TWINS"', '--twins "$PLANTS"'), 1, ["TWINS NOT EXPLICIT", WIN, "does not pass"], None, None),
    ("one id in two runners", lambda c: (c.case_line(WREPLY, "        S1221) echo 'src/gen/emit_dfa.c@@x@@y' ;;"), c.sub(WREPLY, 'PLANTS="S1413 S1414"', 'PLANTS="S1413 S1414 S1221"')), 1, ["S1221", "DUPLICATE ID"], None, None),
]


def unit_rows(t):
    """plants.py's own rules, driven directly: [(name, ok, detail)]."""
    py = os.path.join(root, "tests/lib/plants.py")
    d = t
    os.makedirs(d)
    out = []

    def run(*args):
        return subprocess.run(["python3", "-I", py] + list(args), capture_output=True, text=True)

    def put(s):
        open(os.path.join(d, "f.c"), "w").write(s)

    def got():
        return open(os.path.join(d, "f.c")).read()

    put("A B\n")
    r = run("apply", "wreply", d, "--", "f.c@@A@@X@@Y")
    out.append(("wreply: a fourth @@ field refuses, the file untouched",
                r.returncode == 1 and "undecodable" in r.stderr and got() == "A B\n", r.stderr.strip()))
    put("A B\n")
    r = run("apply", "win", d, "--", "f.c@@A@@X@@Y")
    out.append(("win: a later @@ stays in TO", r.returncode == 0 and got() == "X@@Y B\n", repr(got())))
    put("A B\n")
    r = run("apply", "pres", d, d, "--", "f.c@@A@@P\\\\nQ\\nR\\&")
    out.append(("pres: \\\\\\\\n stays the C escape, \\\\n a newline, \\\\& an ampersand",
                r.returncode == 0 and got() == "P\\nQ\nR& B\n", repr(got())))
    put("A B\n")
    r = run("apply", "win", d, "--", "f.c@@A@@P\\nQ\\&")
    out.append(("win: \\\\n a newline, \\\\& an ampersand", r.returncode == 0 and got() == "P\nQ& B\n", repr(got())))
    put("A B\n")
    r = run("apply", "win", d, "--", "f.c@@A@@C", "f.c@@C B@@D")
    out.append(("apply: cumulative (edit 2 sees edit 1) and written", r.returncode == 0 and got() == "D\n", repr(got())))
    put("A A\n")
    r = run("apply", "win", d, "--", "f.c@@A@@C")
    out.append(("apply: an ambiguous FROM refuses, the file untouched",
                r.returncode == 1 and "plant text found 2 times" in r.stderr and got() == "A A\n", r.stderr.strip()))
    put("A B\n")
    r = run("apply", "win", d, "--", "f.c@@A@@C", "f.c@@Z@@Y")
    out.append(("apply: a stale edit 2 refuses at that edit",
                r.returncode == 1 and "plant text found 0 times" in r.stderr and got() == "C B\n", r.stderr.strip()))
    put("A B\n")
    r = run("apply", "wreply", d, "--", "f.c@@Z@@Y")
    out.append(("wreply: its own refusal text", r.returncode == 1 and "f.c: the text is found 0 times" in r.stderr, r.stderr.strip()))
    put("A B\n")
    r = run("apply", "win", d, "--", "g.c@@A@@C")
    out.append(("apply: a missing file refuses", r.returncode == 1 and "no such file" in r.stderr, r.stderr.strip()))
    lab = os.path.join(d, "labels")
    open(lab, "w").write("plant_spec () \n{ \n    case \"$1\" in \n        S1)\n            :\n        ;;\n    esac\n}\n")
    put("A B\n")
    r = run("check", "win", d, os.path.join(d, "r.sh"), "--labels", lab, "--",
            "--plant", "S1", "2", "f.c@@A@@C", "f.c@@C B@@D")
    out.append(("check: the same loop, cumulative, in memory only",
                r.returncode == 0 and "S1\t2/2\tOK\t1\t" in r.stdout and got() == "A B\n", r.stdout.strip()))
    fc = os.path.normpath(os.path.join(d, "f.c"))
    r = run("dump", "win", d, os.path.join(d, "r.sh"), "--twins", "S1", "--", "--plant", "S1", "1", "f.c@@A\\n@@B@@C")
    out.append(("dump: decoded FILE/FROM/TO, the twin field",
                r.returncode == 0 and r.stdout.split("\t")[1:] == ["1/1", "twin", fc if not fc.startswith(root + os.sep) else os.path.relpath(fc, root), '"A\\n"', '"B@@C"\n'],
                r.stdout.strip()))
    return out


def selftest(serial):
    scratch = os.environ.get("TMPDIR") or "/var/tmp/pcrec-%s" % os.environ.get("USER", "user")
    os.makedirs(scratch, exist_ok=True)
    top = tempfile.mkdtemp(prefix="sabanchor-selftest.", dir=scratch)
    t0 = time.monotonic()
    try:
        base = os.path.join(top, "base")
        ls = subprocess.run(["git", "-C", root, "ls-files", "-z", "--"] + list(SELFTEST_TREE),
                            capture_output=True, check=True).stdout
        named = set()
        for rel in PLANT_PINS:
            if os.path.isfile(os.path.join(root, rel)):
                named |= set(re.findall(r"\bS[0-9]+\b", open(os.path.join(root, rel)).read()))
        for f in (x.decode() for x in ls.split(b"\0") if x):
            if f.startswith("tests/mech/sabotages/S") and os.path.basename(f).split("_")[0] not in named:
                continue
            if os.path.isfile(os.path.join(root, f)):
                os.makedirs(os.path.dirname(os.path.join(base, f)), exist_ok=True)
                shutil.copy2(os.path.join(root, f), os.path.join(base, f))
        genv = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        for argv in (["git", "init", "-q"], ["git", "add", "-A"]):
            subprocess.run(argv, cwd=base, capture_output=True, check=True, env=genv)

        def one(i):
            name, fault, want_rc, words, bound, tmo = CASES[i]
            t = os.path.join(top, "c%02d" % i)
            os.makedirs(t)
            os.symlink(os.path.join(base, ".git"), os.path.join(t, ".git"))   # one index, read only
            for dp, dns, fns in os.walk(base):
                if dp == base:
                    dns.remove(".git")
                rd = os.path.join(t, os.path.relpath(dp, base))
                os.makedirs(rd, exist_ok=True)
                for fn in fns:
                    os.link(os.path.join(dp, fn), os.path.join(rd, fn))
            os.makedirs(os.path.join(t, "tmp"))
            try:
                fault(Case(t))
            except Exception as e:     # a fixture that no longer applies is a red case
                return name, False, "FIXTURE: %s" % e
            env = dict(os.environ, TMPDIR=os.path.join(t, "tmp"), PLANT_ALIVE=os.path.join(t, "alive"))
            if tmo:
                env["PLANT_CHECK_TIMEOUT"] = tmo
            s0 = time.monotonic()
            r = subprocess.run(["python3", "-I", os.path.join(t, "scripts/m6read_check_sab_anchors.py"),
                                "--plant-only"], capture_output=True, text=True, env=env, timeout=600)
            wall = time.monotonic() - s0
            out = r.stdout + r.stderr
            alive = os.path.join(t, "alive")
            if os.path.exists(alive):     # a hang fixture's heartbeat: the pass must have killed it
                m1 = os.stat(alive).st_mtime_ns
                time.sleep(1.0)
                if os.stat(alive).st_mtime_ns != m1:
                    out += "\nSELFTEST: the hung runner's process group is STILL ALIVE after the pass"
                    words = words + ["<the group killed>"]
            miss = [w for w in words if w not in out]
            ok = r.returncode == want_rc and not miss and (bound is None or wall < bound) \
                and not os.listdir(os.path.join(t, "tmp"))
            why = "rc %d (want %d)%s%s%s" % (r.returncode, want_rc,
                                              ", missing %s" % miss if miss else "",
                                              ", %.0f s over its %d s bound" % (wall, bound) if bound and wall >= bound else "",
                                              ", left %s in TMPDIR" % os.listdir(os.path.join(t, "tmp")) if os.listdir(os.path.join(t, "tmp")) else "")
            return name, ok, why if not ok else ""

        t1 = time.monotonic()
        idx = list(range(len(CASES)))
        if serial:
            res = [one(i) for i in idx]
        else:       # the slow (hang) cases first, so they overlap the rest; output in case order
            with ThreadPoolExecutor(max_workers=min(len(idx) + 1, max(2, os.cpu_count() or 2))) as ex:
                uf = ex.submit(unit_rows, os.path.join(top, "units"))
                futs = {i: ex.submit(one, i) for i in sorted(idx, key=lambda i: CASES[i][4] is None)}
                res = [futs[i].result() for i in idx]
                units = uf.result()
        print("selftest: base copy %.1f s, cases %.1f s" % (t1 - t0, time.monotonic() - t1), file=sys.stderr)
        if serial:
            units = unit_rows(os.path.join(top, "units"))
    finally:
        shutil.rmtree(top, ignore_errors=True)
    nbad = 0
    for name, ok, why in res:
        print("selftest case %-58s %s%s" % (name, "ok" if ok else "FAIL", "  " + why if why else ""))
        nbad += not ok
    for name, ok, why in units:
        print("selftest unit %-58s %s%s" % (name, "ok" if ok else "FAIL", "" if ok else "  " + why))
        nbad += not ok
    print("plant pass selftest: %d cases, %d unit rows, %d failed" % (len(res), len(units), nbad))
    print("selftest wall: %.1f s" % (time.monotonic() - t0), file=sys.stderr)
    return nbad != 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--selftest"]:
        sys.exit(1 if selftest("--serial" in args) else 0)
    if args not in ([], ["--plant-only"]):
        sys.exit("usage: m6read_check_sab_anchors.py [--plant-only | --selftest [--serial]]")
    mech_fail = mech_pass() if not args else False
    p_fail = plant_pass()
    sys.exit(1 if (mech_fail or p_fail) else 0)
