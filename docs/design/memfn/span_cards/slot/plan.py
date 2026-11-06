# span_cards/slot/plan.py — THE PLAN of the stage-2 window (span_cards.md §2.4-§2.5, §3.3, §3.5, §3.7): every
# row key the run plans, its group, job, arms and estimator; the delta bases; the floor's clauses. The ONE
# source the slot harness's other parts read (link.py, run.py, record.py) at DRY-RUN time; the dry run FREEZES
# it into RUNDIR/plan.tsv (`freeze`), and everything after the links (run.py run, record.py finalize, est.py)
# reads that frozen copy or the run record, never a live rebuild (review r9 G3). The recompute (S2e) reads the
# run record's copy, never this file.
#
# Populations: the find forms are §2.5's (walk the unit, libc, pair); `walk-set` is FOLDED into `walk` (§2.4: the
# hash decides): formhash.c's entry table renders the composer's FIND over `{X,x}` named by pcrec's table as
# the walk's text byte for byte, so its keys are not planned (formhash.c's entry-table comment); the verify (form, cls) pairs are
# vcls.out's (the census's sites re-classed by the text's boundaries, vcls.py); the `enter` kinds are
# census0.out's "(2) the card population" `enter kind=K` lines (RTE and DEF), entries NONE (the floor's) plus
# PARKED and RESEED where enter/fixtures.tsv names a fixture (a pair no fixture reaches is reported by
# `plan.py report`, never forced). J1's cells are j1/'s.
# THE CARD FACTS have ONE home (review r9 G7): the kit-grid@3 cards (memfn/data/cards/kit-grid.tsv: estimator,
# unit, launches, rounds) and the kit policy table (memfn/data/policy.tsv: the gate a card stating `-` takes,
# R-35 (e), r9 SLOT-17); nothing below restates them. The FROZEN plan pins their values verbatim (sections
# `cards`, `policy`), the run record copies them with the files' sha-256, and est.py reads only that copy
# ([rev1.3 r9fc-FIX-1]: a table edited after the run never moves its verdict).
#   python3 -I plan.py report          the plan, the floor, the counts (§3.7's table, recounted)
#   python3 -I plan.py groups JOB      the job's group count (a job script's `expect groups=N`)
#   python3 -I plan.py freeze OUT      the frozen plan (rows, floor, inputs' sha-256) into OUT
import hashlib, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# SLOT_TREE: the tree when slot/ runs from a copy (sabotage.sh plants in scratch copies)
TREE = os.environ.get("SLOT_TREE") or os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", ".."))
CENSUS0 = os.path.join(TREE, "docs", "design", "memfn", "span_pick", "census0.out")
VCLS = os.path.join(HERE, "vcls.out")
ENTER_FIX = os.path.join(HERE, "enter", "fixtures.tsv")
CARDS = os.path.join(TREE, "memfn", "data", "cards", "kit-grid.tsv")
POLICY = os.path.join(TREE, "memfn", "data", "policy.tsv")
METHOD_VER = "3"                       # kit-grid@3 (span_cards.md §2.1)
UNIT_KEY = "kit.find_byte.walk"        # the set's unit row (§2.2): the walk's find_byte


CARD_COLS = ["owner", "quantity", "ver", "dims", "unit", "subject", "lengths", "launches", "rounds", "aa_rule",
             "gate_e6", "env", "deps"]
POLICY_COLS = ["name", "value", "reason"]


def table_rows(path):
    """a TAB table's data rows, as field lists"""
    return [ln.rstrip("\n").split("\t") for ln in open(path) if ln.strip() and not ln.startswith("#")]


def card_rows(rows):
    """the ver-METHOD_VER rows of a card table (the rows the frozen plan and the run record pin, verbatim)"""
    return [f for f in rows if len(f) == len(CARD_COLS) and f[2] == METHOD_VER]


def parse_policy(rows):
    pol = {}
    for f in rows:
        if len(f) != len(POLICY_COLS) or f[0] in pol:
            raise SystemExit("plan: the policy rows name %s twice or with %d fields" % (f[0], len(f)))
        pol[f[0]] = int(f[1])
    return pol


def parse_cards(rows, pol):
    """{quantity: card} for the kit-grid@3 card rows; `est` the estimator (`lengths`), `gate` the gate_e6 the card
    states or, for `-`, the policy's gate_default_e6. One parser for the live tables (the dry run) and the run
    record's pinned copies (est.py, [rev1.3 r9fc-FIX-1])"""
    cards = {}
    for f in card_rows(rows):
        c = dict(zip(CARD_COLS, f))
        c["gate"] = pol["gate_default_e6"] if c["gate_e6"] == "-" else int(c["gate_e6"])
        c["est"] = c["lengths"]
        cards[c["quantity"]] = c
    if not cards:
        raise SystemExit("plan: the card rows hold no ver-%s card" % METHOD_VER)
    return cards


CARD = parse_cards(table_rows(CARDS), parse_policy(table_rows(POLICY)))


def _one(cards, field):
    v = {c[field] for c in cards.values()}
    if len(v) != 1:
        raise SystemExit("plan: the ver-3 cards disagree on %s (%s): one window times one L x R" % (field, sorted(v)))
    return int(v.pop())


def _est_parse(est):
    m = re.fullmatch(r"(slope|delta) (\d+(?:,\d+)*)", est)
    if not m:
        raise SystemExit("plan: card estimator %r is neither `slope X1,X2,X3` nor `delta LEN`" % est)
    return m.group(1), tuple(int(x) for x in m.group(2).split(","))


def card_facts(cards):
    """the window's facts the cards determine: find_byte's slope LENGTHS (§2.3), every delta row's LEN, the
    launches L and rounds R (§2.1), the UNIT card's gate (§3.5: drift's G and the unit's half gate)"""
    delta = {_est_parse(c["est"])[1] for c in cards.values() if _est_parse(c["est"])[0] == "delta"}
    if len(delta) != 1 or len(next(iter(delta))) != 1:
        raise SystemExit("plan: the delta cards name %s, not one LEN" % sorted(delta))
    L = _one(cards, "launches")
    if L != 7:                         # measures.md §3.4¶2a: the estimator's constants are seven launches'
        raise SystemExit("plan: the ver-3 cards state %d launches; the spec's estimator is written for 7" % L)
    return (_est_parse(cards["find_byte"]["est"])[1], next(iter(delta))[0], L, _one(cards, "rounds"),
            cards["find_byte"]["gate"])


LENGTHS, LEN, L_LAUNCHES, R_ROUNDS, GATE_E6 = card_facts(CARD)
GAPS = (256, 1024)
LANDINGS = ("periodic", "random")
PASSES = ("p0", "p50")
ENTRIES = ("NONE", "PARKED", "RESEED")
CAND_STRIDE = 64                       # a verify candidate every 64 bytes: the ONE home (link.py passes it to the
                                       # driver's C as -DCAND_STRIDE); UNMEASURED DEFAULT (D149)
ENTER_GAP = 256                        # an `enter` candidate every 256 bytes (§2.3; art.py's block)
POOL_BYTES = 16 << 20                  # the pinned 16 MiB pool (§2.3): link.py passes it to the driver's C
TIMING_CPU = "7"                       # the one CPU the window times on (§3.3; run.py's taskset, the record's box)


def census_enter_kinds():
    kinds = set()
    for ln in open(CENSUS0):
        m = re.match(r"(RTE|DEF) enter kind=(\d+) ", ln)
        if m:
            kinds.add(int(m.group(2)))
    return sorted(kinds)


def vcls_pairs():
    pairs = set()
    for ln in open(VCLS):
        f = ln.rstrip("\n").split("\t")
        if len(f) == 5 and f[1] == "verify" and int(f[4]) > 0:
            pairs.add((f[2], f[3]))
    return sorted(pairs)


def shape_split():
    """{(form, cls): {shape: sites}} over both arms: vcls.out's lowering-shape lines (review r9 EMIT-3)"""
    out = {}
    for ln in open(VCLS):
        f = ln.rstrip("\n").split("\t")
        if len(f) == 5 and f[1] == "shape":
            cls, shape = f[3].split(".", 1)
            d = out.setdefault((f[2], cls), {})
            d[shape] = d.get(shape, 0) + int(f[4])
    return out


def shape_majority(form, cls):
    """the class's majority lowering shape (MORE than half its sites), None when no shape is one, or "" when
    vcls.out splits the class by no shape"""
    d = shape_split().get((form, cls))
    if not d:
        return ""
    tot = sum(d.values())
    best = max(d, key=lambda s: (d[s], s))
    return best if 2 * d[best] > tot else None


J1_WIDTHS = (32, 64, 128, 256, 512)    # §3.6; 128 carries the twin 128#b
J1_SUBJECTS = ("mixed", "qs")          # j1/subjects.py: the bench capability subjects' two shapes
J1_REGIMES = (("throughput", 1048576), ("short", 524288))   # j1/subjects.py LEN_TPUT, LEN_SHORT


def j1_pattern_ids():
    return [ln.split("\t")[0] for ln in open(os.path.join(HERE, "j1", "patterns.tsv"))
            if ln.strip() and not ln.startswith("#")]


def enter_fixtures():
    fx = {}
    for ln in open(ENTER_FIX):
        if ln.startswith("#") or not ln.strip():
            continue
        f = ln.rstrip("\n").split("\t")
        fx[(int(f[0]), f[1])] = f
    return fx


# THE KEY'S DIMS ([rev1.3 r9fc-FIX-2], r9 G2's general form): each card dim -> the Arm field its key token
# names, ONE table. A row key `kit.<quantity>.<t1>...` has exactly its card's `dims` (key_dims); link.py's render
# reads every token through this table and REFUSES an Arm whose field disagrees (KEY-ARM MISMATCH), so the
# subject an arm is planted and timed with is the one its key prices. A card dim with no line here refuses.
DIM_FIELD = (
    ("form",    lambda a: a.form),
    ("landing", lambda a: a.landing),
    ("split",   lambda a: a.split),
    ("gap",     lambda a: None if a.gap is None else str(a.gap)),
    ("cls",     lambda a: a.cls),
    ("pass",    lambda a: a.pas),
    ("kind",    lambda a: a.fixture[0] if a.fixture else None),
    ("entry",   lambda a: a.fixture[1] if a.fixture else None),
)


def key_dims(name):
    """{dim: token} of a row key (KEY#b: its arm's) read by its card's `dims`; None for a name that is no row
    key (a base, ctl, a J1 arm). A quantity with no card, or a token count other than its dims', refuses"""
    n = name[:-2] if name.endswith("#b") else name
    q = n.split(".")
    if q[0] != "kit":
        return None
    if q[1] not in CARD:
        raise SystemExit("plan: key %s names quantity %s, which has no ver-%s card" % (name, q[1], METHOD_VER))
    dims = CARD[q[1]]["dims"].split(";")
    if len(q) - 2 != len(dims):
        raise SystemExit("plan: key %s has %d tokens, its card's dims %s are %d" % (name, len(q) - 2, dims, len(dims)))
    return dict(zip(dims, q[2:]))


def key_arm_mismatch(a):
    """[(dim, key token, Arm field)] where the Arm's field is not the token its key names (empty: they agree)"""
    kd = key_dims(a.name) or {}
    field = dict(DIM_FIELD)
    for dim in kd:
        if dim not in field:
            raise SystemExit("plan: card dim %s (key %s) has no DIM_FIELD line" % (dim, a.name))
    return [(dim, tok, field[dim](a)) for dim, tok in kd.items() if field[dim](a) != tok]


def key_form(name):
    """the (form, cls) whose site text an arm NAMED `name` times, read off the name's tokens alone (review r9
    G2: the cell-text check compares against the KEY, never the Arm's own fields; a row key through its card's
    dims, r9fc FIX-2); None for an arm with no form text (the null base, whole artifacts)"""
    n = name[:-2] if name.endswith("#b") else name
    q = n.split(".")
    if n == "ctl":
        return ("walk", None)
    kd = key_dims(n)
    if kd is not None:
        return (kd["form"], kd.get("cls")) if "form" in kd else None
    if q[0] == "base" and len(q) == 2:
        return (q[1], None)
    return None


def base_of(key):
    """the base a delta row's cells name, by the method's FAMILY RULE (§2.4; measures.md §3.4¶6)"""
    q = key.split(".")
    if q[1] == "find_hit":
        return "base.%s" % q[2]
    if q[1] == "verify_cmp":
        return "base.null.%s" % q[3]
    if q[1] == "enter":
        return "base.fail.%s.%s" % (q[2], q[3])
    return None


class Arm:
    """One timed arm: its name (a row key, KEY#b, base.<name> or ctl), the job group, its shape and lengths.
    `of` names a null base's paired verify instance (form, cls): its run/mask/members are the base's."""
    def __init__(self, name, group, kind, form, cls=None, lengths=(LEN,), landing=None, split=None, gap=None,
                 pas=None, base=None, events=None, fixture=None, of=None):
        self.name, self.group, self.kind, self.form, self.cls = name, group, kind, form, cls
        self.lengths, self.landing, self.split, self.gap = lengths, landing, split, gap
        self.pas, self.base, self.events, self.fixture, self.of = pas, base, events, fixture, of

    def twin(self):
        return Arm(self.name + "#b", self.group, self.kind, self.form, self.cls, self.lengths, self.landing,
                   self.split, self.gap, self.pas, self.base, self.events, self.fixture, self.of)


def find_hit_rows(form, splits):
    return [(form, ld, sp, g) for g in GAPS for ld in LANDINGS for sp in splits]


# THE FLOOR (§3.5 "The run record", §1 Goal 2), one row per quantity, first match: (quantity, which of its keys
# join, the clause). A planned row whose quantity has no line REFUSES the plan (never a silent no-clause).
FLOOR = (
    ("find_byte",  lambda q: True,              lambda q: "byte.%s" % q[2]),
    ("find_hit",   lambda q: q[3] == "random",  lambda q: "hit.%s" % q[2]),
    ("verify_cmp", lambda q: True,              lambda q: "verify.%s.%s" % (q[2], q[3])),
    ("enter",      lambda q: q[3] == "NONE",    lambda q: "enter.%s" % q[2]),
)


def build():
    """The plan: jobs -> groups -> arms (twins included), the rows (key, group, job, estimator, base),
    the floor's clauses (clause, key, when), and what the plan could not reach."""
    jobs, rows, floor, unreached = {}, [], [], []

    def add(job, arm):
        jobs.setdefault(job, []).append(arm)

    def row(job, arm, base=None, twin=True):
        q = arm.name.split(".")
        rows.append((arm.name, arm.group, job, CARD[q[1]]["est"], base))
        add(job, arm)
        if twin:
            add(job, arm.twin())
    # J2: the unit group (walk and its twin ONLY, §2.2) and the byte group (libc)
    row("J2", Arm(UNIT_KEY, "J2.unit", "find", "walk", lengths=LENGTHS))
    row("J2", Arm("kit.find_byte.libc", "J2.byte", "find", "libc", lengths=LENGTHS))
    # J2p: pair, its byte row and its hit rows, the base on its own job (§3.7)
    row("J2p", Arm("kit.find_byte.pair", "J2p.byte", "find", "pair", lengths=LENGTHS))
    add("J2p", Arm("base.pair", "J2p.base", "find", "pair", events=0))
    for form, ld, sp, g in find_hit_rows("pair", ("one", "alt")):
        k = "kit.find_hit.pair.%s.%s.%d" % (ld, sp, g)
        row("J2p", Arm(k, "J2p.hit.%s.%d" % (ld, g), "find", "pair", landing=ld, split=sp, gap=g, base=base_of(k),
                       events=LEN // g), base_of(k))
    # J3: libc one, walk one (walk-set alt folded into walk; the walk's control flow never sees which member
    # hit, so its `alt` is its `one`: r9 SLOT-10); bases on J3.base
    for f in ("libc", "walk"):
        add("J3", Arm("base.%s" % f, "J3.base", "find", f, events=0))
    for g in GAPS:
        for ld in LANDINGS:
            for f, sp in (("libc", "one"), ("walk", "one")):
                k = "kit.find_hit.%s.%s.%s.%d" % (f, ld, sp, g)
                row("J3", Arm(k, "J3.hit.%s.%d" % (ld, g), "find", f, landing=ld, split=sp, gap=g,
                              base=base_of(k), events=LEN // g), base_of(k))
    # J4: verify_cmp per (form, cls), each cls its own null base (its run, mask or members the cls's instance's)
    pairs = vcls_pairs()
    owner = {}
    for f, c in pairs:
        if owner.setdefault(c, f) != f:
            raise SystemExit("plan: class %s belongs to two forms (%s, %s): one null base per class" % (c, owner[c], f))
    for cls in sorted(owner):
        add("J4", Arm("base.null.%s" % cls, "J4.base", "verify", "null", cls=cls, events=0, of=(owner[cls], cls)))
    for f, c in pairs:
        for p in PASSES:
            k = "kit.verify_cmp.%s.%s.%s" % (f, c, p)
            row("J4", Arm(k, "J4.verify.%s" % f, "verify", f, cls=c, pas=p, base=base_of(k),
                          events=LEN // CAND_STRIDE), base_of(k))
    # J5 (art.py): enter per (kind, entry) with a fixture; the fail subject is the base. events: the pass
    # subject's candidates (one per ENTER_GAP bytes), 0 on the fail base (§3.4 step 1)
    fx = enter_fixtures()
    for k in census_enter_kinds():
        for e in ENTRIES:
            if (k, e) not in fx or fx[(k, e)][2] == "-":
                why = fx[(k, e)][-1] if (k, e) in fx else "no fixture pattern states kind %d with a %s alternative" % (k, e)
                unreached.append("enter.%d.%s: %s" % (k, e, why))
                continue
            key = "kit.enter.%d.%s" % (k, e)
            add("J5", Arm(base_of(key), "J5.base", "enter", "artifact", fixture=fx[(k, e)], events=0))
            row("J5", Arm(key, "J5.enter", "enter", "artifact", fixture=fx[(k, e)], base=base_of(key),
                          events=LEN // ENTER_GAP), base_of(key))
    # J1 (§3.6, art.py, j1/): per cell (pattern, subject, regime) one group, a whole-artifact arm per PAIR width
    # and the twin 128#b; no rows (J1's cells go to the run record, never the set)
    for pid in j1_pattern_ids():
        for subj in J1_SUBJECTS:
            for regime, n in J1_REGIMES:
                g = "J1.%s.%s.%s" % (pid, subj, regime)
                for w in J1_WIDTHS:
                    a = Arm("j1.%s.%s.%s.%d" % (pid, subj, regime, w), g, "j1", "artifact", lengths=(n,),
                            fixture=(pid, subj, regime, w))
                    add("J1", a)
                    if w == 128:
                        add("J1", a.twin())
    # every job's control (§3.2): three find_byte lengths, one fixed executable
    for j in jobs:
        jobs[j].insert(0, Arm("ctl", "%s.ctl" % j, "ctl", "walk", lengths=LENGTHS))
    # the floor, by the FLOOR table
    rule = {q: (test, clause) for q, test, clause in FLOOR}
    for key, _g, job, _e, _b in rows:
        q = key.split(".")
        if q[1] not in rule:
            raise SystemExit("plan: row %s's quantity %s has no FLOOR line" % (key, q[1]))
        test, clause = rule[q[1]]
        if test(q):
            floor.append((clause(q), key, "unless-j1-b" if job == "J2p" else "always"))
    return jobs, rows, floor, unreached


def points(arms):
    return sum(len(a.lengths) for a in arms)


def groups(jobs, job):
    return sorted({a.group for a in jobs[job]})


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def frozen_text():
    """the frozen plan: its inputs' sha-256, the rows (key group job estimator base), the floor, the ver-3 card
    rows and the policy rows (verbatim) and the jobs"""
    jobs, rows, floor, _un = build()
    t = ["# span_cards stage-2 FROZEN PLAN (slot/plan.py freeze; review r9 G3): the plan every later step reads"]
    t += ["#section inputs", "#path\tsha256"]
    for p in (CENSUS0, VCLS, ENTER_FIX, CARDS, POLICY, os.path.join(HERE, "j1", "patterns.tsv")):
        t.append("%s\t%s" % (os.path.relpath(p, TREE), sha256(p)))
    t += ["#section rows", "#key\tgroup\tjob\testimator\tbase"]
    t += ["\t".join([k, g, j, e, b or "-"]) for k, g, j, e, b in rows]
    t += ["#section floor", "#clause\tkey\twhen"] + ["\t".join(f) for f in floor]
    # the card and policy VALUES the run is planned under, verbatim (r9fc FIX-1: the record pins them, est reads them)
    t += ["#section cards", "#" + "\t".join(CARD_COLS)] + ["\t".join(f) for f in card_rows(table_rows(CARDS))]
    t += ["#section policy", "#" + "\t".join(POLICY_COLS)] + ["\t".join(f) for f in table_rows(POLICY)]
    t += ["#section jobs", "#job\tarms\tgroups"]
    t += ["%s\t%d\t%d" % (j, len(jobs[j]), len(groups(jobs, j))) for j in sorted(jobs)]
    return "\n".join(t) + "\n"


def read_frozen(path):
    """{section: [fields]} of a frozen plan file"""
    secs, cur = {}, None
    for ln in open(path):
        ln = ln.rstrip("\n")
        if ln.startswith("#section "):
            cur = ln.split()[1]
            secs[cur] = []
        elif ln and not ln.startswith("#") and cur:
            secs[cur].append(ln.split("\t"))
    return secs


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "groups":
        print(len(groups(build()[0], sys.argv[2])))
        sys.exit(0)
    if cmd == "freeze":
        open(sys.argv[2], "w").write(frozen_text())
        sys.exit(0)
    jobs, rows, floor, unreached = build()
    print("== slot plan: %d rows, %d floor lines over %d clauses" % (len(rows), len(floor), len({c for c, _k, _w in floor})))
    for j in sorted(jobs):
        print("%s\tarms %d\tpoints %d\tgroups %s" % (j, len(jobs[j]), points(jobs[j]), ",".join(groups(jobs, j))))
    for r in rows:
        print("row\t%s\t%s\t%s\t%s\t%s" % (r[0], r[1], r[2], r[3], r[4] or "-"))
    for c in floor:
        print("floor\t%s\t%s\t%s" % c)
    for u in unreached:
        print("UNREACHED\t" + u)
