# span_cards rev 1.1 drill (lane s2rev11): the COUNTS rev 1.1 quotes, read off the tree where the tree holds
# them (review 2026-11-06 r5 CHECKC, EMBED, J3, CELLS-1 (d)). Read-only; no build, no timing.
#   A. zen4-grid3's projected key population (§2.5's keys; the census-scoped counts are INPUTS).
#   B. the jobs' points, cells and box time (§3.7's layout).
#   C. finder_check.py check C's population AT THE TREE (which sets it reads, how many form tokens it
#      resolves) and the card-row deps guard's population; and the population the new measure_store pass
#      would have over zen4-grid3 (A's form-bearing rows).
#   D. the libpcrec embed's arithmetic: grid1 measured, zen4-grid3 projected with and without its cells.
# python3 -I tree_drill.py REPO_ROOT
import os, sys

root = sys.argv[1] if len(sys.argv) > 1 else "."
# ---- INPUTS (each named; change here, re-run) ----------------------------------------------------------
CENSUS_PAIRS = 8        # verify (form, cls) pairs the census finds on row-1 sites (rev 1's "~8"; S2b fixes it)
CENSUS_CLS = 2          # distinct cls among them (one `null` base each)
ENTER_KINDS = 3         # consumer kinds the census finds (rev 1's "~3"); entries NONE, PARKED, RESEED
L, SEC_PER_POINT_LAUNCH = 7, 0.95       # §2.1; regime_eval.md's per-launch figure (§3.7)
JOB_START_S = 60        # one quiet gate per job start: two load samples >= 55 s apart (650's --ready)
# measured on main's build tree (468afbb0a's build/, 2026-11-04 objects), `size -A build/obj/core/measures.o`
# and `size -t build/libpcrec.a`: the one object that embeds the store (measures_store.inc, measures_table.inc)
OBJ = {"rodata": 9595, "rodata.str1.1": 3195, "rodata.str1.8": 2078, "data.rel.ro.local": 8920, "text": 2039}
LIBPCREC = 1834467
FOLD_ALLOC = 23776 + 1047 + 24 + 48     # `size -A build/obj/core/fold.o`: rodata + text + str + rel.ro
# ---------------------------------------------------------------------------------------------------------

print("== A. zen4-grid3 keys (§2.5)")
byte = ["walk", "libc", "pair", "walk-set"]
hit = ([("libc", "one"), ("walk", "one"), ("pair", "one"), ("pair", "alt"), ("walk-set", "alt")])
hit_keys = ["%s.%s.%s.%d" % (f, land, sp, g) for f, sp in hit for land in ("periodic", "random") for g in (256, 1024)]
verify_keys = CENSUS_PAIRS * 2
enter_keys = ENTER_KINDS * 3
rows = len(byte) + len(hit_keys) + verify_keys + enter_keys
form_rows = len(byte) + len(hit_keys) + verify_keys
print("find_byte %d, find_hit %d, verify_cmp %d (= %d pairs x 2 passes), enter %d (= %d kinds x 3 entries)"
      % (len(byte), len(hit_keys), verify_keys, CENSUS_PAIRS, enter_keys, ENTER_KINDS))
print("rows %d; rows with a `form` dim (check C's new measure_store pass) %d" % (rows, form_rows))

print("\n== B. jobs (§3.7): points = (arm, length) timed per launch")
twin = 2
jobs = [
    ("J1 sweep (slot evidence, not in the set)", 3 + 8 * (5 + 1)),
    ("J2 unit + byte", 3 + 3 * twin + 3 * twin * 2),                        # ctl; walk; libc, walk-set
    ("J2p pair (its own job, J1-gated)", 3 + 3 * twin + 1 + 2 * 2 * 2 * twin),  # ctl; byte pair; base.pair; 8 hit arms
    ("J3 hit (libc, walk, walk-set)", 3 + 3 + 4 * 3 * twin),               # ctl; 3 bases; 4 groups x 3 arms
    ("J4 verify", 3 + CENSUS_PAIRS * 2 * twin + CENSUS_CLS),
    ("J5 enter", 3 + ENTER_KINDS * 3 * twin + ENTER_KINDS * 3),            # ctl; pass, pass#b; fail bases
]
tot = 0
for name, p in jobs:
    tot += p
    print("%-44s %4d points %5.1f min" % (name, p, p * L * SEC_PER_POINT_LAUNCH / 60))
timed = tot * L * SEC_PER_POINT_LAUNCH / 60
starts = len(jobs) * JOB_START_S / 60
cells = (tot - jobs[0][1]) * L
print("total %d points, %.1f min timed, + %d job starts %.0f min = %.1f min; set cells (J2-J5) %d"
      % (tot, timed, len(jobs), starts, timed + starts, cells))

print("\n== C. check C at the tree (tests/memfn/finder_check.py check_sets)")
def sections(path):
    secs, cur = {}, None
    for ln in open(path, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.startswith("#section "):
            cur = ln.split()[1]
            secs[cur] = {"head": None, "rows": []}
        elif ln.startswith("#"):
            if cur:
                secs[cur]["head"] = ln[1:].split("\t")
        elif cur and ln:
            secs[cur]["rows"].append(dict(zip(secs[cur]["head"], ln.split("\t"))))
    return secs
cards = [l.rstrip("\n").split("\t") for l in open(os.path.join(root, "memfn/data/cards/kit-grid.tsv"))
         if l.strip() and not l.startswith("#")]
dep_cards = [c for c in cards if "kit:form." in c[12]]
print("kit-grid.tsv cards %d; with a kit:form. dep %d; of those without `form` as first dim %d"
      % (len(cards), len(dep_cards), sum(1 for c in dep_cards if c[3].split(";")[0] != "form")))
sdir = os.path.join(root, "memfn/data/sets")
nform = 0
for fn in sorted(os.listdir(sdir)):
    if not fn.endswith(".tsv"):
        continue
    s = sections(os.path.join(sdir, fn))
    hdr = {r["key"]: r.get("value", "") for r in s["header"]["rows"]}
    on = {c[1]: c for c in cards if "kit-grid@" + c[2] == hdr.get("method")}
    k = sum(1 for r in s["rows"]["rows"] if len(r["key"].split(".")) > 2 and r["key"].split(".")[1] in on
            and on[r["key"].split(".")[1]][3].split(";")[0] == "form")
    nform += k
    print("  memfn/data/sets/%s: method %s, rows %d, form-token rows resolved %d"
          % (fn, hdr.get("method"), len(s["rows"]["rows"]), k))
store = sorted(d for d in os.listdir(os.path.join(root, "measure_store"))
               if os.path.isdir(os.path.join(root, "measure_store", d)) and d != "movers")
print("check C reads memfn/data/sets only: %d form-token rows; measure_store sets it reads: 0 of %d (%s)"
      % (nform, len(store), ", ".join(store)))
print("zen4-grid3 keys check C would see as written: 0; the new measure_store pass at S2e: %d" % form_rows)

print("\n== D. the embed (measures.md §8¶2), libpcrec bytes")
g1 = os.path.join(root, "measure_store/zen4-grid1/1/set.tsv")
s1 = sections(g1)
g1_rows, g1_cards, g1_bytes = len(s1["rows"]["rows"]), len(s1["cards"]["rows"]), os.path.getsize(g1)
inc = {n: os.path.getsize(os.path.join(root, "src/core", n)) for n in ("measures_store.inc", "measures_table.inc")}
alloc = OBJ["rodata"] + OBJ["rodata.str1.1"] + OBJ["rodata.str1.8"] + OBJ["data.rel.ro.local"]
per_row = alloc / (g1_rows + g1_cards)
print("grid1: set.tsv %d B, %d rows + %d cards; measures_store.inc %d B (%.1fx), measures_table.inc %d B"
      % (g1_bytes, g1_rows, g1_cards, inc["measures_store.inc"], inc["measures_store.inc"] / g1_bytes,
         inc["measures_table.inc"]))
print("grid1 embed in libpcrec (measures.o data sections) %d B = %.0f B per row or card" % (alloc, per_row))
line = "J3.hit.random.1024/kit.find_hit.walk-set.random.alt.1024#b/1048576/7\tJ3.hit.random.1024\t" \
       "kit.find_hit.walk-set.random.alt.1024#b\t1048576\t7\tmed\t1024\t199229440000\n"
cell_text = len(line)
cell_pre = 8 * 8 + 40          # 8 pointers (format 2's cell columns) + its distinct strings (ids, values)
g3_no_cells = (rows + 4) * per_row
g3_cells = cells * (cell_text + cell_pre)
print("zen4-grid3 projected: %d rows + 4 cards = %.1f KB embedded without cells; its %d cells would add "
      "%.0f KB (%d B text + ~%d B pre-parse each) = %.1f %% of libpcrec.a (%d B)"
      % (rows, g3_no_cells / 1024, cells, g3_cells / 1024, cell_text, cell_pre, 100 * g3_cells / LIBPCREC, LIBPCREC))
print("ten grid1-size embeds %.0f KB vs fold.o's allocated tables %.1f KB (measure_sets.md's 'ten sets below "
      "one fold_tables.inc')" % (10 * alloc / 1024, FOLD_ALLOC / 1024))
