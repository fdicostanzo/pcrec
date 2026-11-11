#!/usr/bin/env python3
"""cloud_status.py — live view of ONE cloud run's shards ([CLOUD-SUITE], lane cloudmon).

  cloud_status.py status RUNID [--cache FILE]   one run, human text: kind, name, shards done/total, elapsed, and each
                                                red shard with its failing lines
  cloud_status.py reds RUNID --cache FILE       machine form for scripts/queuewatch: one line per red shard,
                                                `RUNID|K/N<TAB>owner kind name shard K/N run=ID :: <first failing lines>`

A red shard = a `shard (K/N)` job of the run that completed with failure or timed_out. Its log is fetched ONCE
(`gh api .../actions/jobs/ID/logs`) and the failing lines come from tests/ci/cloud_failures.sh, the same extractor the
final verdict uses; --cache FILE (lines `RUNID|K/N<TAB>text`) remembers what was fetched, so a re-poll costs the jobs
listing only. API calls per call of this script: 1 (the run) + 1 (the jobs) + 1 per newly red shard.
Env: CLOUDSTATUS_ALERT_LINES (3) / CLOUDSTATUS_STATUS_LINES (6) failing lines per alert / per status shard; GH_TIMEOUT (60).
"""
import json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
TO = int(os.environ.get("GH_TIMEOUT", "60"))


def gh(path, raw=False):
    r = subprocess.run(["gh", "api", path] + ([] if raw else ["--paginate"]), capture_output=True, text=True, timeout=TO)
    if r.returncode:
        raise RuntimeError("gh api %s: %s" % (path, (r.stderr or "failed").strip().splitlines()[0][:160]))
    return r.stdout


def parse_ts(s):
    return time.mktime(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ")) - time.timezone if s else None


def run_info(rid):
    r = json.loads(gh("repos/{owner}/{repo}/actions/runs/%s" % rid))
    parts = (r.get("head_branch") or "").split("/", 3)
    owner, kind, name = (parts[1:] + ["?", "?", "?"])[:3] if parts[0] == "cloud" else ("?", "?", r.get("head_branch"))
    end = parse_ts(r["updated_at"]) if r["status"] == "completed" else time.time()
    return dict(owner=owner, kind=kind, name=name, status=r["status"], conclusion=r.get("conclusion"),
                elapsed=int(end - parse_ts(r["created_at"])), url=r.get("html_url"))


def shard_jobs(rid):
    """[(K/N, job id, status, conclusion)] — concatenated --paginate pages are separate JSON documents."""
    txt = gh("repos/{owner}/{repo}/actions/runs/%s/jobs" % rid)
    dec, i, out = json.JSONDecoder(), 0, []
    while i < len(txt):
        while i < len(txt) and txt[i].isspace():
            i += 1
        if i >= len(txt):
            break
        page, i = dec.raw_decode(txt, i)
        for j in page.get("jobs", []):
            m = re.match(r"shard \((\d+/\d+)\)$", j["name"])
            if m:
                out.append((m.group(1), j["id"], j["status"], j["conclusion"]))
    return out


def failing_lines(job_id, limit):
    log = gh("repos/{owner}/{repo}/actions/jobs/%s/logs" % job_id, raw=True)
    r = subprocess.run(["bash", os.path.join(HERE, "cloud_failures.sh"), str(limit)], input=log, capture_output=True, text=True)
    return [" ".join(l.split())[:200] for l in r.stdout.splitlines()]


def is_red(c):
    return c in ("failure", "timed_out")


def read_cache(path):
    d = {}
    if path and os.path.exists(path):
        for l in open(path):
            k, _, v = l.rstrip("\n").partition("\t")
            d[k] = v
    return d


def red_texts(rid, jobs, cache, limit):
    """{K/N: text} for each red shard; fetches a log only for a shard not in the cache."""
    cached, out = read_cache(cache), {}
    for sh, jid, st, concl in jobs:
        if st != "completed" or not is_red(concl):
            continue
        key = "%s|%s" % (rid, sh)
        if key not in cached:
            try:
                lines = failing_lines(jid, limit)
            except Exception as e:
                lines = ["(log not fetched: %s)" % e]
            cached[key] = " || ".join(lines) if lines else "(no failing line found in the log; conclusion=%s)" % concl
            if cache:
                with open(cache, "a") as f:
                    f.write("%s\t%s\n" % (key, cached[key]))
        out[sh] = cached[key]
    return out


def main(a):
    if len(a) < 2 or a[0] not in ("status", "reds"):
        sys.exit(__doc__)
    mode, rid = a[0], a[1]
    cache = a[a.index("--cache") + 1] if "--cache" in a else None
    try:
        info, jobs = run_info(rid), shard_jobs(rid)
    except Exception as e:
        print("cloud_status: %s" % e, file=sys.stderr)
        sys.exit(1)
    if mode == "reds":
        n = int(os.environ.get("CLOUDSTATUS_ALERT_LINES", "3"))
        for sh, txt in sorted(red_texts(rid, jobs, cache, n).items(), key=lambda kv: int(kv[0].split("/")[0])):
            print("%s|%s\t%s %s %s shard %s run=%s :: %s" % (rid, sh, info["owner"], info["kind"], info["name"], sh, rid, txt))
        return
    total = max([int(s.split("/")[1]) for s, *_ in jobs] or [0])
    done = sum(1 for j in jobs if j[2] == "completed")
    red = red_texts(rid, jobs, cache, int(os.environ.get("CLOUDSTATUS_STATUS_LINES", "6")))
    running = sum(1 for j in jobs if j[2] == "in_progress")
    print("run %s  %s %s (owner %s)  %s%s  shards done %d/%d (%d red, %d running)  elapsed %dm%02ds" % (
        rid, info["kind"], info["name"], info["owner"], info["status"],
        "/" + info["conclusion"] if info["conclusion"] else "", done, total, len(red), running, info["elapsed"] // 60, info["elapsed"] % 60))
    for sh, txt in sorted(red.items(), key=lambda kv: int(kv[0].split("/")[0])):
        print("  RED shard %s" % sh)
        for l in txt.split(" || "):
            print("      " + l)
    if info.get("url"):
        print("  " + info["url"])


main(sys.argv[1:])
