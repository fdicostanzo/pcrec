#!/usr/bin/env python3
"""tests/knowledge/meas_recompute.py -- the RECOMPUTE CHECK of a format-2
measurement set (span_pick stage 2 unit S2e; docs/design/memfn/span_cards.md
§3.8 step 4, Goal 3).

Written from the spec text alone: docs/spec/measures.md §3.4 (the estimator,
steps 1-8, its arithmetic: rhafz, isqrt_rn, the lower median, exact
integers) and §3.5 (cost gates ¶2, the NULL rule ¶3, sub-resolution ¶3a,
bound rows ¶3b, the unit's bimodal test ¶4-¶5, drift ¶6, the floor ¶7, the
run record ¶8, the producer's rules ¶8a, the three copies ¶9, what the
recompute covers ¶10, the outcome table ¶11-¶13), plus the rules of the one
producer it holds, `kit-grid@3`, from span_cards.md (the family base rule of
§2.4, the floor token `unless-j1-b` of §3.5, J1's verdict rule of §3.6, the
bound token `fused-load-op` of §R1.5). It imports NOTHING from the slot
harness (docs/design/memfn/span_cards/slot/) nor its drills; the set and the
record are parsed by tests/knowledge/ks_ref.py's section reader, pcrec's
spec-written python reader. Integer arithmetic only.

    meas_recompute.py ROOT
        every committed ROOT/measure_store/*/*/set.tsv whose header `format`
        is 2 (keyed on format, never a name list; counted, floored at 1),
        format-1 sets counted as skipped
    meas_recompute.py --set SETFILE --provenance PROVFILE --root ROOT
        one set; its run record is ROOT/<the path PROVENANCE.md names>

One `PASS: ...` / `FAIL: ...` line per checked item group, a `REFUSED:
<REASON> ...` line for an input refusal (the reasons are distinct grep-able
tokens: SET-LOAD, PROVENANCE, THREE-COPY, RECORD-SHA, RECORD, RULES, CARDS,
POLICY, ID-PARSE, ID-COLUMNS, DUP-ID, PLAN, JOBS, BASE-ONE, BASE-RULE,
BASE-GROUP, EVENTS, POSITIVE, J1-CELLS; a recomputed difference is
ROW-MISMATCH, ROW-LIST, J1-VERDICT, OUTCOME, PARTIAL, UNREAD-CELL). Exit 0
iff no FAIL.
"""
import hashlib
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ks_ref  # noqa: E402  (pcrec's spec-written set reader)

E6 = 10 ** 6
K_TRIM_E6 = 1723000     # measures.md §3.4¶16
K_MED_E6 = 210300       # measures.md §3.5¶6
L_SUPPORTED = 7         # measures.md §3.4¶2a

# --- the producer rules this recompute HOLDS (measures.md §3.5¶8a) -------
# kit-grid@3, from span_cards.md: the family base rule (§2.4, restated in
# §3.4 step 1 (c)), the floor condition tokens (§3.5 "The run record"), the
# bound token (§R1.5, measures.md §3.5¶3b), the policy names a `-` gate and
# r_max take (§2.4, §3.5 run record `policy`), J1's rule (§3.6: m 0.5, k 5).
RULES = {
    "kit-grid@3": {
        "base": {
            "find_hit": "base.{form}",
            "verify_cmp": "base.null.{cls}",
            "enter": "base.fail.{kind}.{entry}",
        },
        "conditions": {"always", "unless-j1-b"},
        "bound": "fused-load-op",
        "gate_policy": "gate_default_e6",
        "rmax_policy": "r_max_e6",
        "j1": {"ref": "128", "twin": "128#b", "k": 5},
    },
}


class Refuse(Exception):
    def __init__(self, reason, detail):
        Exception.__init__(self, reason)
        self.reason, self.detail = reason, detail


# --- arithmetic, measures.md §3.4¶2 ---------------------------------------
def rhafz(n, d):
    """n/d rounded half away from zero: truncating division, sign after."""
    if d == 0:
        raise Refuse("POSITIVE", "a division by zero")
    neg = (n < 0) != (d < 0)
    q, r = divmod(abs(n), abs(d))
    if 2 * r >= abs(d):
        q += 1
    return -q if neg else q


def isqrt_rn(n):
    r = math.isqrt(n)
    return r + (1 if n - r * r > r else 0)


def med(v):
    return sorted(v)[(len(v) - 1) // 2]


def trimmed(v):
    """v (in launch order) less the ONE launch farthest from med(v), ties the
    later launch (§3.4¶16; ¶3's trim of D_l is the same)."""
    m = med(v)
    drop = 0
    for i, x in enumerate(v):
        if abs(x - m) >= abs(v[drop] - m):
            drop = i
    return v[:drop] + v[drop + 1:]


def sp2_of(v):
    """§3.4¶16 step 6."""
    w = trimmed(v)
    n = len(w)
    q = n * sum(x * x for x in w) - sum(w) ** 2
    return rhafz(K_TRIM_E6 * q, E6 * n * (n - 1))


def slope(xs, ys):
    """§3.4¶10: least-squares slope, exact integers, n = 3."""
    n = len(xs)
    s = n * sum(x * y for x, y in zip(xs, ys)) - sum(xs) * sum(ys)
    d = n * sum(x * x for x in xs) - sum(xs) ** 2
    return rhafz(s, d)


# --- reading ---------------------------------------------------------------
def text_sections(raw):
    out = {}
    for name, (cols, rows) in ks_ref.sections(raw).items():
        out[name] = (cols, [{k: v.decode() for k, v in r.items()} for r in rows])
    return out


def as_int(s, what):
    if not re.fullmatch(r"-?(0|[1-9][0-9]*)", s or ""):
        raise Refuse("RECORD" if what.startswith("record") else "SET-LOAD",
                     "%s is not an integer: %r" % (what, s))
    return int(s)


def provenance_record(provpath):
    """measures.md §3.5¶9: PROVENANCE.md's bullet `- **The run record.**`
    names the tree-relative path, `sha-256` and the hex, `run id` and the id,
    each in backticks."""
    try:
        lines = open(provpath, encoding="utf-8").read().split("\n")
    except OSError as e:
        raise Refuse("PROVENANCE", "cannot read %s: %s" % (provpath, e))
    text = None
    for i, ln in enumerate(lines):
        if ln.startswith("- **The run record.**"):
            buf = [ln]
            for nxt in lines[i + 1:]:
                if not nxt.strip() or nxt.startswith("- "):
                    break
                buf.append(nxt.strip())
            text = " ".join(buf)
            break
    if text is None:
        raise Refuse("PROVENANCE", "no `- **The run record.**` bullet")
    path = re.search(r"`([^`]+)`", text)
    sha = re.search(r"sha-256\s+`([0-9a-f]{64})`", text)
    rid = re.search(r"run id\s+`([^`]+)`", text)
    if not (path and sha and rid):
        raise Refuse("PROVENANCE", "the run-record bullet lacks a path, a "
                     "`sha-256` hex or a `run id`")
    p = path.group(1)
    if p.startswith("/") or ".." in p.split("/"):
        raise Refuse("PROVENANCE", "record path %r is not tree-relative" % p)
    return p, sha.group(1), rid.group(1)


class Checker:
    def __init__(self, setpath, provpath, root, label):
        self.setpath, self.provpath, self.root = setpath, provpath, root
        self.label = label
        self.lines = []
        self.failed = False

    def ok(self, group, msg):
        self.lines.append("PASS: %s %s (%s)" % (self.label, group, msg))

    def bad(self, group, msg):
        self.failed = True
        self.lines.append("FAIL: %s %s: %s" % (self.label, group, msg))

    # -- the run --------------------------------------------------------------
    def run(self):
        try:
            self.check()
        except Refuse as r:
            self.failed = True
            self.lines.append("REFUSED: %s %s: %s" % (r.reason, self.label, r.detail))
            self.lines.append("FAIL: %s refused (%s)" % (self.label, r.reason))
        return self.lines, self.failed

    def check(self):
        self.load_set()
        self.three_copies()
        self.read_record()
        self.read_cards()
        self.read_cells()
        self.read_plan_jobs()
        self.base_rule()
        self.needed_cells()
        self.estimate()
        self.drift()
        self.rows()
        self.compare_rows()
        self.gates_line()
        self.j1()
        self.floor_outcome()
        self.unread()

    # -- the set (§2, §3.3) -------------------------------------------------
    def load_set(self):
        try:
            raw = open(self.setpath, "rb").read()
        except OSError as e:
            raise Refuse("SET-LOAD", "cannot read: %s" % e)
        doc = ks_ref.load(self.setpath)
        s = text_sections(raw)
        self.head = {r["key"]: r["value"] for r in s.get("header", ([], []))[1]}
        if self.head.get("format") != "2":
            raise Refuse("SET-LOAD", "not a format-2 set")
        if ks_ref.digest(doc) != self.head.get("values_digest") or \
                str(len(doc["rows"])) != self.head.get("rows"):
            raise Refuse("SET-LOAD", "values_digest or rows differs from the "
                         "rows (§3.3¶2): the set does not load")
        self.set_cards = s.get("cards", ([], []))[1]
        self.set_rows = {r["key"]: r for r in s.get("rows", ([], []))[1]}
        self.cells_raw = s.get("cells", ([], []))[1]
        self.unit_key = self.head.get("unit_key", "")
        self.method = self.head.get("method", "")

    # -- §3.5¶9: header `run`, PROVENANCE.md, the record's sha and run_id -----
    def three_copies(self):
        m = re.fullmatch(r"(\S+) record:([0-9a-f]{64})", self.head.get("run", ""))
        if not m:
            raise Refuse("THREE-COPY", "header `run` %r is not `<run id> "
                         "record:<sha-256>`" % self.head.get("run", ""))
        h_rid, h_sha = m.group(1), m.group(2)
        path, p_sha, p_rid = provenance_record(self.provpath)
        if h_sha != p_sha:
            raise Refuse("THREE-COPY", "header sha %s != PROVENANCE.md sha %s"
                         % (h_sha, p_sha))
        if h_rid != p_rid:
            raise Refuse("THREE-COPY", "header run id %s != PROVENANCE.md "
                         "run id %s" % (h_rid, p_rid))
        try:
            raw = open(os.path.join(self.root, path), "rb").read()
        except OSError as e:
            raise Refuse("RECORD-SHA", "cannot read record %s: %s" % (path, e))
        f_sha = hashlib.sha256(raw).hexdigest()
        if f_sha != h_sha:   # checked BEFORE the record is read (§3.5¶9)
            raise Refuse("RECORD-SHA", "record %s has sha-256 %s, the header "
                         "and PROVENANCE.md name %s" % (path, f_sha, h_sha))
        self.rec_raw, self.rec_path, self.run_id, self.rec_sha = raw, path, h_rid, h_sha

    # -- §3.5¶8, ¶8a ----------------------------------------------------------
    def read_record(self):
        s = text_sections(self.rec_raw)
        for need in ("run", "jobs", "plan", "floor"):
            if need not in s:
                raise Refuse("RECORD", "no section `%s` (§3.5¶8)" % need)
        self.rec = s
        self.rrun = {r["key"]: r["value"] for r in s["run"][1]}
        if self.rrun.get("run_id") != self.run_id:
            raise Refuse("THREE-COPY", "record run_id %r != header/PROVENANCE.md "
                         "run id %s" % (self.rrun.get("run_id"), self.run_id))
        want = "%s@%s" % (self.head.get("id"), self.head.get("rev"))
        if self.rrun.get("set") != want:
            raise Refuse("RECORD", "record `set` %r, the set is %s"
                         % (self.rrun.get("set"), want))
        owner = self.rrun.get("rules")
        if owner not in RULES:
            raise Refuse("RULES", "rules owner %r is not one this recompute "
                         "holds (§3.5¶8a)" % owner)
        self.rules = RULES[owner]
        self.owner = owner
        if self.method not in RULES:   # §3.4¶6: a base rule for the method
            raise Refuse("BASE-RULE", "no base rule held for method %r" % self.method)
        self.policy = {r["name"]: r["value"] for r in s.get("policy", ([], []))[1]}
        if self.rules["rmax_policy"] not in self.policy:
            raise Refuse("POLICY", "the record pins no `%s`" % self.rules["rmax_policy"])
        self.r_max = as_int(self.policy[self.rules["rmax_policy"]], "record r_max_e6")
        self.ok("three copies", "header run, PROVENANCE.md and record agree: "
                "run id %s, sha-256 %s..., rules %s" % (self.run_id, self.rec_sha[:16], owner))

    # -- §3.4¶2a, ¶3; the cards the record pinned ---------------------------
    def read_cards(self):
        cols = ks_ref.CARD
        mine = sorted(tuple(r.get(c, "") for c in cols) for r in self.set_cards)
        rec = sorted(tuple(r.get(c, "") for c in cols)
                     for r in self.rec.get("cards", ([], []))[1])
        if mine != rec:
            raise Refuse("CARDS", "the set's cards differ from the cards the "
                         "record pinned")
        self.cards = {}
        for r in self.set_cards:
            q = r["quantity"]
            lg = r["lengths"]
            m1 = re.fullmatch(r"slope ([0-9]+),([0-9]+),([0-9]+)", lg)
            m2 = re.fullmatch(r"delta ([0-9]+)", lg)
            if m1:
                xs = [int(x) for x in m1.groups()]
                if not (xs[0] < xs[1] < xs[2]):
                    raise Refuse("CARDS", "%s: slope lengths not distinct ascending" % q)
                est = ("slope", xs)
            elif m2:
                est = ("delta", int(m2.group(1)))
            else:
                raise Refuse("CARDS", "%s: lengths %r is not `slope X1,X2,X3` or "
                             "`delta LEN` (§3.4¶3)" % (q, lg))
            if r["launches"] != str(L_SUPPORTED):
                raise Refuse("CARDS", "%s: launches %r, the recompute is written "
                             "for 7 (§3.4¶2a)" % (q, r["launches"]))
            aa = set(r["aa_rule"].split(";"))
            if not aa <= {"twin-per-arm", "bimodal-test"} or "twin-per-arm" not in aa:
                raise Refuse("CARDS", "%s: aa_rule %r" % (q, r["aa_rule"]))
            g = r["gate_e6"]
            if g == "-":
                if self.rules["gate_policy"] not in self.policy:
                    raise Refuse("POLICY", "card %s states gate `-`, the record "
                                 "pins no `%s`" % (q, self.rules["gate_policy"]))
                g = self.policy[self.rules["gate_policy"]]
            self.cards[q] = {
                "dims": [d for d in r["dims"].split(";") if d not in ("", "-")],
                "unit": r["unit"], "est": est, "gate": as_int(g, "gate_e6"),
                "R": as_int(r["rounds"], "rounds"), "aa": aa,
                "owner": r["owner"]}
        self.ok("cards", "%d cards equal the record's, launches 7, %s"
                % (len(self.cards), ", ".join("%s %s gate %d" % (
                    q, c["est"][0], c["gate"]) for q, c in sorted(self.cards.items()))))

    # -- §3.4¶5-¶8: ids, columns, uniqueness --------------------------------
    def read_cells(self):
        self.cells = {}
        ids = set()
        for r in self.cells_raw:
            cid = r["cell"]
            f = cid.split("/")
            if len(f) not in (4, 5) or any(x == "" for x in f):
                raise Refuse("ID-PARSE", "cell id %r is not group/arm/length/"
                             "launch[/base] (§3.4¶5)" % cid)
            cols = (r["group"], r["arm"], r["length"], r["launch"])
            if tuple(f[:4]) != cols:   # §3.4¶6
                raise Refuse("ID-COLUMNS", "cell id %r disagrees with its columns "
                             "group/arm/length/launch %s" % (cid, "/".join(cols)))
        for r in self.cells_raw:
            cid = r["cell"]
            if cid in ids:
                raise Refuse("DUP-ID", "cell id %r twice (§2.2¶4)" % cid)
            ids.add(cid)
            f = cid.split("/")
            g = r["group"]
            if not re.fullmatch(r"J[0-9A-Za-z]+\.[^/]+", g):
                raise Refuse("ID-PARSE", "group %r is not J<j>.<name> (§3.4¶7)" % g)
            ln = as_int(r["length"], "cell length")
            la = as_int(r["launch"], "cell launch")
            if not 1 <= la <= L_SUPPORTED:
                raise Refuse("ID-PARSE", "cell %r launch outside 1..7" % cid)
            if r.get("round") != "med":
                raise Refuse("ID-PARSE", "cell %r round %r, not `med` (§3.4¶8)"
                             % (cid, r.get("round")))
            ev = r.get("events", "")
            k = (g, r["arm"], ln, la)
            if k in self.cells:
                raise Refuse("DUP-ID", "two cells for %s" % "/".join(map(str, k)))
            self.cells[k] = {"id": cid, "ns": as_int(r["ns_e6"], "cell ns_e6"),
                             "events": ev, "base": f[4] if len(f) == 5 else None}
        self.read_ids = set()
        self.ok("cell ids", "%d cells: ids parse, the first four fields equal "
                "group/arm/length/launch, unique" % len(self.cells))

    # -- §3.5¶8 plan and jobs ---------------------------------------------
    def read_plan_jobs(self):
        self.plan = {}
        for r in self.rec["plan"][1]:
            k, g, j = r["key"], r["group"], r["job"]
            if k in self.plan or g.split(".")[0] != j:
                raise Refuse("PLAN", "plan line %s %s %s" % (k, g, j))
            parts = k.split(".")
            if len(parts) < 2 or parts[0] != "kit" and parts[0] != "pcrec":
                raise Refuse("PLAN", "plan key %r" % k)
            q = parts[1]
            if q not in self.cards:
                raise Refuse("PLAN", "plan key %s has no card" % k)
            if len(parts) - 2 != len(self.cards[q]["dims"]):
                raise Refuse("PLAN", "plan key %s: %d tokens, card dims %d (§2.3¶2)"
                             % (k, len(parts) - 2, len(self.cards[q]["dims"])))
            self.plan[k] = {"group": g, "job": j, "q": q, "tok": parts[2:]}
        if self.unit_key not in self.plan:
            raise Refuse("PLAN", "the unit key %s is not planned" % self.unit_key)
        self.jobs = {}
        for r in self.rec["jobs"][1]:
            st = r["state"]
            if st not in ("ran", "never-ran") or r["job"] in self.jobs or \
                    (st == "never-ran" and r.get("cause", "-") in ("", "-")):
                raise Refuse("JOBS", "jobs line %s %s %s" % (r["job"], st, r.get("cause")))
            self.jobs[r["job"]] = st
        for k, p in self.plan.items():
            if p["job"] not in self.jobs:
                raise Refuse("JOBS", "plan key %s's job %s has no jobs line" % (k, p["job"]))
        # §3.5¶10: a never-ran job has no cell in the set
        for (g, arm, ln, la), c in self.cells.items():
            j = g.split(".")[0]
            if j not in self.jobs:
                raise Refuse("JOBS", "cell %s names job %s, not in `jobs`" % (c["id"], j))
            if self.jobs[j] == "never-ran":
                raise Refuse("JOBS", "never-ran job %s has cell %s (§3.5¶10)" % (j, c["id"]))
        self.unit_job = self.plan[self.unit_key]["job"]

    # -- §3.4¶6, ¶11, ¶12: the producer's family base rule -----------------
    def family_base(self, key):
        p = self.plan[key]
        tmpl = self.rules["base"].get(p["q"])
        if tmpl is None:
            raise Refuse("BASE-RULE", "no base rule of %s for quantity %s"
                         % (self.owner, p["q"]))
        return tmpl.format(**dict(zip(self.cards[p["q"]]["dims"], p["tok"])))

    def base_rule(self):
        n = 0
        self.bases = {}
        for key, p in self.plan.items():
            if self.jobs[p["job"]] != "ran":
                continue
            kind = self.cards[p["q"]]["est"][0]
            mine = [c for (g, a, ln, la), c in self.cells.items()
                    if g == p["group"] and a in (key, key + "#b")]
            if kind == "slope":
                for c in mine:
                    if c["base"] is not None:
                        raise Refuse("ID-PARSE", "slope cell %s has a fifth field" % c["id"])
                continue
            named = {c["base"] for c in mine}
            if len(named) != 1 or None in named:
                raise Refuse("BASE-ONE", "%s: its cells and its twin's name bases %s, "
                             "not ONE (§3.4¶11)" % (key, sorted(map(str, named))))
            b = named.pop()
            want = self.family_base(key)
            if b != want:
                raise Refuse("BASE-RULE", "%s's cells name base %s, the family rule "
                             "of %s declares %s (§3.4¶6)" % (key, b, self.owner, want))
            self.bases[key] = b
            n += 1
        for (g, a, ln, la), c in self.cells.items():
            if c["base"] is not None and not any(
                    g == self.plan[k]["group"] and a in (k, k + "#b")
                    for k in self.bases):
                raise Refuse("ID-PARSE", "cell %s carries a fifth field and is no "
                             "delta row's arm or twin" % c["id"])
        self.ok("base rule", "%d delta rows: one base each, the family rule of %s"
                % (n, self.owner))

    # -- §3.5¶10: a ran job has every cell its plan keys need ---------------
    def need(self, g, arm, ln, la):
        c = self.cells.get((g, arm, ln, la))
        if c is None:
            raise Refuse("JOBS", "ran job %s lacks cell %s/%s/%d/%d"
                         % (g.split(".")[0], g, arm, ln, la))
        self.read_ids.add(c["id"])
        return c

    def needed_cells(self):
        L = range(1, L_SUPPORTED + 1)
        self.ctl = {}
        ran = sorted(j for j, st in self.jobs.items() if st == "ran")
        for j in ran:
            g = j + ".ctl"
            lens = sorted({ln for (gg, a, ln, la) in self.cells if gg == g})
            if not lens and not any(p["job"] == j for p in self.plan.values()):
                continue   # a ran job with no plan key and no control (J1)
            if len(lens) != 3:
                raise Refuse("JOBS", "%s holds %d control lengths, not exactly "
                             "three (§3.4¶10)" % (g, len(lens)))
            for (gg, a, ln, la) in self.cells:
                if gg == g and a != "ctl":
                    raise Refuse("ID-PARSE", "arm %s in a control group" % a)
            u = []
            for la in L:
                ys = [self.need(g, "ctl", ln, la)["ns"] for ln in lens]
                for ln in lens:
                    if self.need(g, "ctl", ln, la)["events"] != "-":
                        raise Refuse("EVENTS", "ctl cell events not `-` (§3.4¶8)")
                u.append(slope(lens, ys))
            if min(u) <= 0:
                raise Refuse("POSITIVE", "%s: a control slope <= 0 (§3.4¶14a)" % j)
            self.ctl[j] = u
        for k, p in self.plan.items():
            if self.jobs[p["job"]] == "ran" and p["job"] not in self.ctl:
                raise Refuse("JOBS", "ran job %s has no control group" % p["job"])
        self.ok("jobs", "%s; never-ran jobs hold no cell, ran jobs hold every "
                "planned key's cells and a three-length control" % ", ".join(
                    "%s %s" % kv for kv in sorted(self.jobs.items())))

    # -- §3.4 steps 2-4: per-launch values ------------------------------------
    def per_launch(self, key):
        p = self.plan[key]
        card = self.cards[p["q"]]
        g = p["group"]
        L = range(1, L_SUPPORTED + 1)
        out = {}
        if card["est"][0] == "slope":
            xs = card["est"][1]
            for arm in (key, key + "#b"):
                for x in xs:
                    for la in L:
                        if self.need(g, arm, x, la)["events"] != "-":
                            raise Refuse("EVENTS", "slope cell %s events not `-`"
                                         % self.need(g, arm, x, la)["id"])
                out[arm] = [slope(xs, [self.need(g, arm, x, la)["ns"] for x in xs])
                            for la in L]
            out["D"] = out["Db"] = None
            return out
        LEN = card["est"][1]
        b = self.bases[key]
        jb = p["job"] + ".base"   # §3.4¶12: the job's base group, checked
        if not any(gg == jb and a == b for (gg, a, ln, la) in self.cells):
            other = [gg for (gg, a, ln, la) in self.cells if a == b]
            raise Refuse("BASE-GROUP", "%s's base %s has no cells in %s (found in %s)"
                         % (key, b, jb, sorted(set(other))))
        evs = {self.need(g, arm, LEN, la)["events"] for arm in (key, key + "#b") for la in L}
        if len(evs) != 1:
            raise Refuse("EVENTS", "%s: events %s, not one value (§3.4¶11)" % (key, sorted(evs)))
        E = as_int(evs.pop(), "events")
        if E <= 0:
            raise Refuse("POSITIVE", "%s: E = %d (§3.4¶14a)" % (key, E))
        for la in L:
            bc = self.need(jb, b, LEN, la)
            if not re.fullmatch(r"0|[1-9][0-9]*", bc["events"]):
                raise Refuse("EVENTS", "base cell %s events %r" % (bc["id"], bc["events"]))
        for arm, dk in ((key, "D"), (key + "#b", "Db")):
            d = [self.need(g, arm, LEN, la)["ns"] - self.need(jb, b, LEN, la)["ns"] for la in L]
            out[dk] = d
            out[arm] = [rhafz(x, E) for x in d]
        return out

    def estimate(self):
        self.pl = {}
        for k, p in self.plan.items():
            if self.jobs[p["job"]] != "ran":
                continue
            pl = self.per_launch(k)
            u = self.ctl[p["job"]]
            pl["abs"] = pl[k]
            pl["v"] = [rhafz(a * E6, uu) for a, uu in zip(pl[k], u)]
            pl["vb"] = [rhafz(a * E6, uu) for a, uu in zip(pl[k + "#b"], u)]
            self.pl[k] = pl
        if self.unit_key not in self.pl:
            self.W = None
            return
        self.W = med(self.pl[self.unit_key]["v"])
        if self.W <= 0:
            raise Refuse("POSITIVE", "W = %d (§3.4¶14a)" % self.W)
        for k, pl in self.pl.items():
            pl["x"] = [rhafz(v * E6, self.W) for v in pl["v"]]
            pl["xb"] = [rhafz(v * E6, self.W) for v in pl["vb"]]

    # -- §3.5¶6 drift ----------------------------------------------------------
    def drift(self):
        self.refused_jobs = set()
        self.drift_txt = []
        if self.unit_job not in self.ctl:
            self.bad("drift", "the unit's job %s has no control" % self.unit_job)
            return
        G = self.cards[self.plan[self.unit_key]["q"]]["gate"]

        def rel_sp2(u):
            mu = med(u)
            return sp2_of([rhafz(x * E6, mu) for x in u])
        cu = med(self.ctl[self.unit_job])
        su = rel_sp2(self.ctl[self.unit_job])
        for j in sorted(self.ctl):
            cj = med(self.ctl[j])
            d = rhafz(abs(cj - cu) * E6, cu)
            se3 = 3 * isqrt_rn(rhafz(K_MED_E6 * (su + rel_sp2(self.ctl[j])), E6))
            refused = 2 * d > G and d > se3
            if refused:
                self.refused_jobs.add(j)
            self.drift_txt.append("%s %d/%d %s" % (j, d, max(se3, (G + 1) // 2),
                                                   "REFUSED" if refused else "kept"))
        self.ok("drift", "per job drift/threshold: " + ", ".join(self.drift_txt))

    # -- §3.4 steps 5-8 and §3.5¶2-¶5: every row ------------------------------
    def rows(self):
        self.calc = {}
        self.cost = {}
        self.unit_fail = None
        for k, p in sorted(self.plan.items()):
            if k not in self.pl or self.W is None:
                continue
            pl = self.pl[k]
            card = self.cards[p["q"]]
            x, xb = pl["x"], pl["xb"]
            value = med(x)
            aa = med([abs(b - a) for a, b in zip(x, xb)])
            sp2 = sp2_of(x)
            noise = isqrt_rn(aa * aa + sp2)
            row = {"value": value, "noise": noise, "status": "measured",
                   "abs": med(pl["abs"]), "n": L_SUPPORTED * card["R"],
                   "unit": card["unit"], "how": "priced"}
            if card["est"][0] == "slope":
                G = card["gate"]
                if k == self.unit_key:   # ¶2 half gate, ¶4 bimodal, ¶5
                    gate_ok = value > 0 and 2 * noise * E6 <= G * value
                    s = sorted(x)
                    bim = "bimodal-test" in card["aa"] and any(
                        2 * (s[i] - s[i - 1]) > G for i in range(2, L_SUPPORTED - 1))
                    self.unit_gate, self.unit_bim = gate_ok, bim
                    if not gate_ok or bim:
                        self.unit_fail = "half gate" if not gate_ok else "bimodal"
                    ok = gate_ok and not bim
                else:
                    ok = value > 0 and noise * E6 <= G * value
                self.cost[k] = ok
                row["how"] = "gate pass" if ok else "gate fail"
            else:
                row = self.delta_row(k, pl, row, value, aa, sp2, noise)
            self.calc[k] = row

    def delta_row(self, k, pl, row, value, aa, sp2, noise):
        D, Db = pl["D"], pl["Db"]
        tags = self.set_rows.get(k, {}).get("tags", "-")
        bound = self.rules["bound"] in tags.split(";")
        six = trimmed(D)
        aa_d = med([abs(b - a) for a, b in zip(D, Db)])
        r = min(3 * isqrt_rn(rhafz(K_MED_E6 * sp2, E6)), self.r_max)
        if bound:   # ¶3b: whatever ¶3's test says
            row.update(value=max(0, value), noise=max(self.r_max, abs(value)),
                       how="bound")
        elif all(d > 0 for d in six) and med(D) > aa_d:   # ¶3
            pass
        elif not all(d < 0 for d in six) and abs(value) <= r and aa <= r:   # ¶3a
            row.update(value=max(0, value), noise=max(r, noise),
                       how="sub-resolution r %d" % r)
        else:
            row.update(value=None, noise=None, status="null", how="null")
        return row

    # -- §3.5¶10: the row list and every row, exact ---------------------------
    def compare_rows(self):
        absent = {}
        for k, p in self.plan.items():
            if self.jobs[p["job"]] != "ran":
                absent[k] = "never-ran:%s" % p["job"]
            elif p["job"] in self.refused_jobs:
                absent[k] = "drift:%s" % p["job"]
            elif k in self.cost and not self.cost[k]:
                absent[k] = "text"
        self.absent = absent
        want = set(self.plan) - set(absent)
        have = set(self.set_rows)
        if want == have:
            self.ok("row list", "%d rows = %d planned keys minus %d absent"
                    % (len(have), len(self.plan), len(absent)))
        else:
            for k in sorted(want - have):
                self.bad("ROW-LIST", "%s recomputed present, not in the set" % k)
            for k in sorted(have - want):
                self.bad("ROW-LIST", "%s in the set, recomputed %s" % (
                    k, absent.get(k, "unplanned")))
        diffs = 0
        for k in sorted(want & have):
            c, s = self.calc[k], self.set_rows[k]

            def cmp(field, setv, mine):
                nonlocal diffs
                if setv != mine:
                    diffs += 1
                    self.bad("ROW-MISMATCH", "%s %s set=%s recomputed=%s"
                             % (k, field, setv or "''", mine))
            if c["status"] == "null":
                cmp("value_e6", s["value_e6"], "")
                cmp("noise_e6", s["noise_e6"], "-")
                # reading: ¶3 names no abs_ns_e6 for a null row; held to
                # med(abs_l) when the set states one
                if s["abs_ns_e6"] not in ("", "-"):
                    cmp("abs_ns_e6", s["abs_ns_e6"], str(c["abs"]))
            else:
                cmp("value_e6", s["value_e6"], str(c["value"]))
                cmp("noise_e6", s["noise_e6"], str(c["noise"]))
                cmp("abs_ns_e6", s["abs_ns_e6"], str(c["abs"]))
            cmp("status", s["status"], c["status"])
            cmp("unit", s["unit"], c["unit"])
            cmp("n", s["n"], str(c["n"]))
            cmp("derivation", s["derivation"] if s["derivation"] else "-", "-")
            cmp("inputs", s["inputs"] if s["inputs"] else "-", "-")
        if not diffs:
            hows = {}
            for k in want & have:
                h = self.calc[k]["how"].split(" r ")[0]
                hows[h] = hows.get(h, 0) + 1
            self.ok("rows exact", "%d rows: value_e6, noise_e6, abs_ns_e6, status, n "
                    "equal; W %d; %s" % (len(want & have), self.W, ", ".join(
                        "%s %d" % kv for kv in sorted(hows.items()))))

    def gates_line(self):
        if self.unit_key not in self.calc:
            self.bad("gates", "the unit row %s was not computed" % self.unit_key)
            return
        cost = ["%s %s" % (k, "pass" if v else "FAIL") for k, v in sorted(self.cost.items())]
        self.ok("gates", "unit half gate %s, bimodal %s; cost rows: %s" % (
            "pass" if self.unit_gate else "FAIL", "yes" if self.unit_bim else "no",
            ", ".join(cost)))

    # -- span_cards.md §3.6: J1's verdict, re-derived (§3.5¶10) -------------
    def j1(self):
        rule = self.rules["j1"]
        stated = (self.rrun.get("j1_verdict"), self.rrun.get("j1_widths"))
        rows = self.rec.get("j1_cells", ([], []))[1]
        if not rows:
            self.j1v = None
            if stated[0] is not None:
                self.bad("J1-VERDICT", "record states %s, no j1_cells" % stated[0])
            else:
                self.ok("J1", "no J1 cells, no verdict")
            return
        t = {}
        for r in rows:
            f = r["cell"].split("/")
            cols = ["J1", r["pattern"], r["subject"], r["regime"], r["width"], r["launch"]]
            if f != cols:
                raise Refuse("J1-CELLS", "j1 cell id %r disagrees with its columns" % r["cell"])
            c = (r["pattern"], r["subject"], r["regime"])
            key = (c, r["width"], as_int(r["launch"], "record j1 launch"))
            if key in t:
                raise Refuse("J1-CELLS", "j1 cell %r twice" % r["cell"])
            t[key] = as_int(r["ns_e6"], "record j1 ns_e6")
        cells = sorted({k[0] for k in t})
        widths = sorted({k[1] for k in t} - {rule["twin"]}, key=int)
        L = range(1, L_SUPPORTED + 1)
        for c in cells:
            for w in widths + [rule["twin"]]:
                for la in L:
                    if (c, w, la) not in t:
                        raise Refuse("J1-CELLS", "j1 lacks %s/%s/%d" % ("/".join(c), w, la))
        if rule["ref"] not in widths:
            raise Refuse("J1-CELLS", "no width %s" % rule["ref"])
        beats, loses = {}, {}
        for w in widths:
            if w == rule["ref"]:
                continue
            beats[w] = loses[w] = 0
            for c in cells:
                ref = [t[(c, rule["ref"], la)] for la in L]
                tw = [t[(c, rule["twin"], la)] for la in L]
                rl = [rhafz((t[(c, w, la)] - r0) * E6, r0) for la, r0 in zip(L, ref)]
                aa = med([rhafz(abs(b - r0) * E6, r0) for b, r0 in zip(tw, ref)])
                margin = 2 * abs(med(rl)) > isqrt_rn(aa * aa + sp2_of(rl))
                if margin and all(x < 0 for x in rl):
                    beats[w] += 1
                elif margin and all(x > 0 for x in rl):
                    loses[w] += 1
        b_w = [w for w in beats if beats[w] >= rule["k"] and loses[w] == 0]
        if b_w:
            v, ws = "b", ";".join(b_w)
        elif not any(beats.values()):
            v, ws = "a", "-"
        else:
            v, ws = "c", "-"
        self.j1v = v
        detail = ", ".join("w%s beats %d loses %d" % (w, beats[w], loses[w]) for w in beats)
        if (v, ws) != stated:
            self.bad("J1-VERDICT", "record states j1_verdict %s j1_widths %s, re-derived "
                     "%s %s from %d cells (%s)" % (stated[0], stated[1], v, ws, len(cells), detail))
        else:
            self.ok("J1", "verdict %s widths %s re-derived from %d j1 cells (%s)"
                    % (v, ws, len(cells), detail))

    # -- §3.5¶7, ¶11-¶13: floor, outcome, partial -----------------------------
    def priced(self, k):
        if k in self.absent or k not in self.calc:
            return False
        return self.calc[k]["status"] != "null"

    def why(self, k):
        if k in self.absent:
            return self.absent[k]
        if k not in self.calc:
            return "unplanned"
        return "text" if self.calc[k]["status"] == "null" else "priced"

    def floor_outcome(self):
        clauses = {}
        for r in self.rec["floor"][1]:
            w = r["when"]
            if w not in self.rules["conditions"]:
                raise Refuse("RULES", "floor condition token %r is not one %s defines"
                             % (w, self.owner))
            if r["key"] not in self.plan:
                raise Refuse("RECORD", "floor key %s is not planned" % r["key"])
            clauses.setdefault(r["clause"], []).append((r["key"], w))
        active, failed = 0, []
        for cl, lines in sorted(clauses.items()):
            # unless-j1-b is true (the line inactive) iff J1's re-derived verdict is b
            act = [k for k, w in lines if w == "always" or (w == "unless-j1-b" and self.j1v != "b")]
            if not act:
                continue
            active += 1
            if not any(self.priced(k) for k in act):
                failed.append("floor:%s (%s)" % (cl, ", ".join(
                    "%s %s" % (k, self.why(k)) for k in act)))
        if self.unit_key in self.absent or self.unit_fail or self.W is None:
            outcome = "REFUSED (unit%s)" % (": " + self.unit_fail if self.unit_fail else "")
        elif failed:
            outcome = "REFUSED (" + "; ".join(failed) + ")"
        elif self.absent:
            outcome = "PARTIAL"
        else:
            outcome = "FULL"
        if outcome.startswith("REFUSED"):
            self.bad("OUTCOME", "recomputed %s, yet the set exists" % outcome)
            return
        want = "1" if outcome == "PARTIAL" else "0"
        if self.head.get("partial", "") != want:
            self.bad("PARTIAL", "header partial %r, outcome %s wants %s"
                     % (self.head.get("partial", ""), outcome, want))
            return
        self.ok("floor/outcome/partial", "%d clauses, %d active, all met; outcome %s, "
                "partial %s; absent %s" % (len(clauses), active, outcome, want,
                                           ", ".join(sorted(self.absent)) or "none"))

    # -- §2.2¶5: the set carries the cells its rows and verdict read ---------
    def unread(self):
        extra = sorted(c["id"] for c in self.cells.values() if c["id"] not in self.read_ids)
        if extra:
            self.bad("UNREAD-CELL", "%d cells no row or verdict reads, first %s"
                     % (len(extra), extra[0]))
        else:
            self.ok("cells read", "every one of %d cells is read" % len(self.cells))


def check_one(setpath, provpath, root, label):
    return Checker(setpath, provpath, root, label).run()


def store(root):
    out, failed, n2, n1 = [], False, 0, 0
    base = os.path.join(root, "measure_store")
    sets = []
    for d in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        dd = os.path.join(base, d)
        if not os.path.isdir(dd):
            continue
        for rev in sorted(os.listdir(dd)):
            f = os.path.join(dd, rev, "set.tsv")
            if os.path.isfile(f):
                sets.append((d, rev, f))
    for d, rev, f in sets:
        s = ks_ref.sections(open(f, "rb").read())
        head = {r["key"]: r["value"] for r in s.get("header", ([], []))[1]}
        fmt = head.get(b"format", b"1")
        if fmt == b"1":
            n1 += 1
            continue
        if fmt != b"2":
            out.append("FAIL: %s@%s format %r unknown" % (d, rev, fmt))
            failed = True
            continue
        n2 += 1
        lines, bad = check_one(f, os.path.join(os.path.dirname(f), "PROVENANCE.md"),
                               root, "%s@%s" % (d, rev))
        out += lines
        failed = failed or bad
    line = "recompute: %d format-2 set(s) (floor 1), %d format-1 skipped" % (n2, n1)
    if n2 < 1:   # K35: the population is counted and floored
        out.append("FAIL: " + line)
        failed = True
    else:
        out.append("PASS: " + line)
    return out, failed


def main(argv):
    if len(argv) == 2 and not argv[1].startswith("-"):
        lines, failed = store(argv[1])
    elif len(argv) == 7 and argv[1] == "--set" and argv[3] == "--provenance" \
            and argv[5] == "--root":
        d = os.path.dirname(os.path.abspath(argv[2]))
        label = "%s@%s" % (os.path.basename(os.path.dirname(d)), os.path.basename(d))
        lines, failed = check_one(argv[2], argv[4], argv[6], label)
    else:
        sys.stderr.write(__doc__)
        return 2
    for ln in lines:
        print(ln)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
