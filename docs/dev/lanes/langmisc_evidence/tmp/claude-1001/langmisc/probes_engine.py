# Engine axis (§4.5): replay every earlier probe that pcrec accepted under --engine=vm and --engine=dfa --no-captures
import json, glob, os
HERE = "/tmp/claude-1001/langmisc"
P = []
for f in ["probes_base", "probes_uni", "probes_mods", "probes_lb"]:
    src = {pp.get("id"): pp for pp in __import__("runpy").run_path(os.path.join(HERE, f + ".py"))["PROBES"]}
    for l in open(os.path.join(HERE, "results", f + ".jsonl")):
        r = json.loads(l)
        if r["verdict"] not in ("AGREE", "DIFF", "GIVEUP") or r["opts"].get("extra"):
            continue
        base = dict(src[r["id"]])
        for tag, extra in (("vm", ["--engine=vm"]), ("dfa", ["--engine=dfa", "--no-captures"])):
            q = dict(base); q["extra"] = extra; q["id"] = r["id"] + "-" + tag; P.append(q)
PROBES = P
