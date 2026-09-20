import json, re, csv, itertools
from collections import defaultdict, Counter

GRAIN = "/private/tmp/claude-501/-Users-fdicostanzo-pcrec/6c826da8-f394-412e-b898-373008f3c3a9/scratchpad/grain"

commits = json.load(open(f"{GRAIN}/commits.json"))

# --- load census (functions at HEAD, with span/code_lines) ---
census = []
with open(f"{GRAIN}/emit_vm_census.tsv") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 8 or parts[0] != "src/gen/emit_vm.c":
            continue
        file_, start, end, span, code, depth, name, header = parts[:8]
        census.append({"start": int(start), "end": int(end), "span": int(span),
                        "code": int(code), "name": name})
census.sort(key=lambda r: r["start"])
all_funcs = set(r["name"] for r in census)
code_lines = {r["name"]: r["code"] for r in census}

# --- identify MECHANICAL rename commits (pure identifier renames) ---
MECH_HASHES = set()
for c in commits:
    subj = c["subject"]
    if ("REVW.5] item 6" in subj and re.search(r"rename \d+", subj)) or \
       ("mechanical rename" in subj.lower()):
        MECH_HASHES.add(c["hash"])

for c in commits:
    c["is_mech"] = c["hash"] in MECH_HASHES

mech = [c for c in commits if c["is_mech"]]
nonmech = [c for c in commits if not c["is_mech"]]
sweeps = [c for c in commits if c["is_sweep"]]  # >60 funcs, none as computed earlier
print(f"Total={len(commits)} mechanical-rename={len(mech)} sweep(>60)={len(sweeps)} analysis-set={len(nonmech)}")

# restrict FILESCOPE / unmatched labels: keep as pseudo-function "FILESCOPE" for closure purposes
def real_funcs(funcset):
    return set(f for f in funcset if f in all_funcs)

for c in commits:
    c["real_funcs"] = real_funcs(c["func_set"])
    c["has_filescope"] = any(f.startswith("FILESCOPE") for f in c["func_set"])

# ============================================================
# EXPERIMENT 2: the three walks (cost / count / emit-arms)
# ============================================================
COST_RE = re.compile(r"^vm_cost")
COUNT_RE = re.compile(r"^vm_count_slots")
# "emit arms": vm_ functions that are not cost/count/listing/plan
LISTING_NAMES = set(f for f in all_funcs if f.startswith("vm_listing") or f in
                     ("vm_render_listing","vm_ev","vm_rolef","vm_bounds_text","vm_charge",
                      "vm_label","vm_mask_names","vm_sec","vm_row3","vm_prow",
                      "vm_cls_describe","vm_layout","vm_frame_fields","vm_trail_fields",
                      "vm_fields_join"))
PLAN_NAMES = set(f for f in all_funcs if f.startswith("vm_plan") or "capacit" in f)

def is_emit_arm(f):
    if not f.startswith("vm_") and not f.startswith("pcrec_vm_"):
        return False
    if COST_RE.match(f) or COUNT_RE.match(f):
        return False
    if f in LISTING_NAMES or f in PLAN_NAMES:
        return False
    return True

EMIT_NAMES = set(f for f in all_funcs if is_emit_arm(f))

def touches(c, pred_set_or_re, is_re=False):
    for f in c["real_funcs"]:
        if is_re:
            if pred_set_or_re.match(f):
                return True
        else:
            if f in pred_set_or_re:
                return True
    return False

rows2 = []
counts_2x2x2 = Counter()
any_of_three = []
for c in nonmech:
    tc = touches(c, COST_RE, True)
    tn = touches(c, COUNT_RE, True)
    te = touches(c, EMIT_NAMES, False)
    if tc or tn or te:
        counts_2x2x2[(tc,tn,te)] += 1
        any_of_three.append(c["hash"][:10])

print("\n=== EXPERIMENT 2: 2x2x2 (cost,count,emit) among commits touching >=1 ===")
labels = {(0,0,0):"none(excluded)", (1,0,0):"cost only", (0,1,0):"count only", (0,0,1):"emit only",
          (1,1,0):"cost+count", (1,0,1):"cost+emit", (0,1,1):"count+emit", (1,1,1):"all three"}
total3 = sum(counts_2x2x2.values())
for k,v in sorted(counts_2x2x2.items(), key=lambda kv: -kv[1]):
    print(f"  {labels[tuple(int(x) for x in k)]:16s} {v:4d}  ({100*v/total3:.1f}%)")
print(f"  TOTAL commits touching >=1 of the three: {total3}")

# ============================================================
# EXPERIMENT 3: partitions
# ============================================================

# --- P-BANNER: banner sections at HEAD ---
banners = [
 (69,'B_capacities_hdr'), (234,'B_emitter_state'), (236,'B_listing'),
 (1214,'B_ast_predicates'), (1381,'B_atomic_lift'), (1505,'B_class_pool'),
 (1622,'B_cursor_ladder'), (1809,'B_revdet_facts'), (1934,'B_capacity_analysis'),
 (2637,'B_slot_counting'), (3039,'B_emission'), (3239,'B_mrl_pruning'),
 (3434,'B_island_step1'), (3522,'B_island_input'), (4809,'B_revdet_rung'),
 (6053,'B_atomic_group'), (6201,'B_lookaround'), (8369,'B_rendering_listing'),
 (9225,'B_the_artifact'),
]
import bisect
starts = [b[0] for b in banners]
def banner_of(start_line):
    idx = bisect.bisect_right(starts, start_line) - 1
    return banners[idx][1] if idx >= 0 else 'B_PREAMBLE'

P_BANNER = {}
for r in census:
    P_BANNER[r["name"]] = banner_of(r["start"])

# --- P-PASS: literal name-pattern rule, first-match wins, order: cost,count,plan,listing,emit-core,entry,util ---
def p_pass(f):
    if f.startswith("vm_cost"):
        return "PP_cost"
    if f.startswith("vm_count_slots"):
        return "PP_count"
    if f.startswith("vm_plan") or "capacit" in f:
        return "PP_plan"
    if f.startswith("vm_listing") or f == "vm_render_listing" or f == "vm_ev":
        return "PP_listing"
    EXACT_EMIT = {"vm_emit","vm_goto","vm_fail","vm_label","vm_set","vm_rep","vm_alt","vm_cap",
                  "vm_cat","vm_wordb","vm_bref","vm_call","vm_splice"}
    PREFIX_EMIT = ("vm_push","vm_look","vm_region","vm_isl","vm_cursor","vm_revdet","vm_counter")
    if f in EXACT_EMIT or any(f.startswith(p) for p in PREFIX_EMIT):
        return "PP_emitcore"
    if f in ("pcrec_emit_vm","vm_emit_default_entry") or "stamp" in f:
        return "PP_entry"
    return "PP_util"

P_PASS = {r["name"]: p_pass(r["name"]) for r in census}

# --- P-KIND: by AST node kind served; cost/count/emit of same kind co-located ---
def p_kind(f):
    if f in ("vm_rep","vm_cost_rep","vm_count_slots_rep","vm_star","vm_poss_star",
             "vm_poss_chain","vm_opt_chain","vm_lifts","vm_cuts","vm_nullable","vm_det_seq","bare"):
        return "PK_rep"
    if f in ("vm_alt","vm_emit_span_scan"):
        return "PK_alt"
    if f in ("vm_cap","vm_grp_set_cap","vm_cap_offsets","vm_w_cap_slots","vm_walk_caps",
              "vm_publish_saves","vm_publish_nonnull","vm_resolve_nonnull",
              "vm_slot_ctr","vm_slot_ref","vm_slot_rev","vm_slot_mark","vm_slot_guard",
              "vm_slot_low","vm_slot_pend"):
        return "PK_cap"
    if f in ("vm_look","vm_look_behind","vm_look_behind_branch","vm_look_needs_mark",
              "vm_look_needs_pos","vm_count_slots_look","vm_marked","vm_snap",
              "vm_slot_lookmark","vm_slot_lookpos"):
        return "PK_look"
    if f in ("vm_call","vm_splice","vm_region","vm_build_region_saves","vm_memo_region_costs",
              "vm_plan_regions","vm_w_range","vm_walk_calls","vm_slot_splice","vm_slot_expr"):
        return "PK_call_splice_region"
    if f.startswith("vm_isl") or f in ("vm_cat","vm_wordb","vm_bref","vm_cls","vm_cls_shape",
                                        "vm_cls_test","vm_cls_fold_count","vm_cls_describe"):
        return "PK_island"
    if f in ("vm_cursor_fits","vm_cursor_rep","vm_revdet_fits","vm_revdet_rep","vm_rev_canmove",
              "vm_rev_caps","vm_rev_index","vm_rev_emit","vm_counter_fits","vm_counter_copies",
              "vm_counter_phase","vm_counter_poss_opt","vm_counter_rep","vm_rung_mark"):
        return "PK_cursor_revdet_counter"
    return "PK_misc"

P_KIND = {r["name"]: p_kind(r["name"]) for r in census}

def score_partition(name, mapping, commits_to_score):
    file_of = lambda f: mapping.get(f, "UNMAPPED")
    n_single = 0
    n_total = 0
    files_per_commit = []
    for c in commits_to_score:
        rf = c["real_funcs"]
        if not rf:
            continue
        n_total += 1
        files_touched = set(file_of(f) for f in rf)
        files_per_commit.append(len(files_touched))
        if len(files_touched) == 1:
            n_single += 1
    pct_single = 100*n_single/n_total if n_total else 0.0
    mean_files = sum(files_per_commit)/len(files_per_commit) if files_per_commit else 0.0
    # size balance: lines per resulting file
    sizes = defaultdict(int)
    for r in census:
        sizes[file_of(r["name"])] += r["code"]
    sizes = dict(sizes)
    return {"name": name, "n_commits": n_total, "pct_single_file": pct_single,
            "mean_files_per_commit": mean_files, "n_files": len(sizes),
            "sizes": sizes}

results = []
for nm, mp in [("P-BANNER", P_BANNER), ("P-PASS", P_PASS), ("P-KIND", P_KIND)]:
    results.append(score_partition(nm, mp, nonmech))

# ============================================================
# co-change graph + greedy agglomerative clustering (empirical optimum)
# ============================================================
pair_counts = Counter()
solo_counts = Counter()
for c in nonmech:
    rf = sorted(c["real_funcs"])
    if len(rf) < 1:
        continue
    for f in rf:
        solo_counts[f] += 1
    for a,b in itertools.combinations(rf, 2):
        pair_counts[(a,b)] += 1

# Jaccard-normalized edge weight to avoid hub functions dominating naive counts
def jaccard(a,b):
    inter = pair_counts.get((a,b),0) if (a,b) in pair_counts else pair_counts.get((b,a),0)
    if inter == 0:
        return 0.0
    union = solo_counts[a] + solo_counts[b] - inter
    return inter/union if union else 0.0

funcs_list = sorted(all_funcs)
# init: each function its own cluster
clusters = {f: {f} for f in funcs_list}
cluster_id = {f: f for f in funcs_list}

def cluster_edge_weight(c1_id, c2_id):
    total = 0
    n = 0
    for a in clusters[c1_id]:
        for b in clusters[c2_id]:
            key = (a,b) if (a,b) in pair_counts else (b,a)
            total += pair_counts.get(key, 0)
            n += 1
    return total / n if n else 0

# greedy agglomerative merge using raw co-change counts (avg-linkage).
# Stage 1: merge only while a positive (data-supported) co-change edge exists.
TARGET = 8
active = list(clusters.keys())
natural_stop_n = None
while len(active) > 1:
    best = None
    best_w = -1
    for i in range(len(active)):
        for j in range(i+1, len(active)):
            w = cluster_edge_weight(active[i], active[j])
            if w > best_w:
                best_w = w
                best = (active[i], active[j])
    if best is None or best_w <= 0:
        natural_stop_n = len(active)
        break
    a, b = best
    clusters[a] |= clusters[b]
    del clusters[b]
    active.remove(b)
    if len(active) <= TARGET:
        # keep going only to record the natural stop; but if we already hit
        # target via real signal, that's the natural stop too.
        pass

natural_clusters = {k: sorted(v) for k, v in clusters.items() if k in active}

# Stage 2 (NOT data-supported): to get a same-footing score in the table,
# continue merging down to TARGET by combining the two SMALLEST remaining
# clusters (pure size-balancing, zero co-change weight behind these merges).
forced_merges = []
while len(active) > TARGET:
    active.sort(key=lambda k: sum(code_lines.get(m, 0) for m in clusters[k]))
    a, b = active[0], active[1]
    forced_merges.append((a, b))
    clusters[a] |= clusters[b]
    del clusters[b]
    active.remove(b)

final_clusters = {k: sorted(v) for k, v in clusters.items() if k in active}

CLUSTER_MAP = {}
for cid, members in final_clusters.items():
    for m in members:
        CLUSTER_MAP[m] = cid

cluster_result = score_partition("P-CLUSTER(empirical, forced-to-8)", CLUSTER_MAP, nonmech)
results.append(cluster_result)

print(f"\nNatural (data-supported) stopping point: {natural_stop_n} clusters")
for cid, members in sorted(natural_clusters.items(), key=lambda kv: -sum(code_lines.get(m,0) for m in kv[1])):
    tot = sum(code_lines.get(m,0) for m in members)
    print(f"  cluster[{cid}] n={len(members)} code_lines={tot}")
    if len(members) > 1:
        print(f"    members: {members}")
print(f"\nForced merges beyond natural stop (size-balancing, no co-change signal): {forced_merges}")

# ============================================================
# Function-level churn
# ============================================================
touch_count = Counter()
touch_campaigns = defaultdict(set)
for c in commits:  # churn uses ALL commits including mechanical, per brief (function-level churn, not closure)
    for f in c["real_funcs"]:
        touch_count[f] += 1
        if c["campaign"]:
            touch_campaigns[f].add(c["campaign"])

top15 = touch_count.most_common(15)

# ============================================================
# Write report data to json for the writer step
# ============================================================
out = {
    "n_commits_total": len(commits),
    "n_mech": len(mech),
    "n_sweep": len(sweeps),
    "n_nonmech": len(nonmech),
    "exp2_counts": {str(k): v for k,v in counts_2x2x2.items()},
    "exp2_total": total3,
    "partition_scores": [{k: (v if k != "sizes" else v) for k,v in r.items()} for r in results],
    "clusters": final_clusters,
    "natural_stop_n": natural_stop_n,
    "natural_clusters": natural_clusters,
    "forced_merges": forced_merges,
    "top15_churn": [(f, n, sorted(touch_campaigns[f])) for f,n in top15],
    "mech_hashes": sorted(MECH_HASHES),
    "p_pass_table": P_PASS,
    "p_kind_table": P_KIND,
    "p_banner_table": P_BANNER,
}
json.dump(out, open(f"{GRAIN}/results.json","w"), indent=1)
print("\nWrote results.json")

# also write commits.tsv for the manager to re-score
with open(f"{GRAIN}/commits.tsv","w",newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["hash","date","campaign","is_mech","n_funcs","funcs"])
    for c in commits:
        w.writerow([c["hash"], c["date"], c["campaign"] or "", c["is_mech"], c["n_funcs"],
                    ";".join(c["func_set"])])
print("Wrote commits.tsv")
