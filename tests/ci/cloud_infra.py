#!/usr/bin/env python3
"""tests/ci/cloud_infra.py -- INFRA vs RED for a cloud run ([CLOUD-SUITE] D): a shard whose TEST step passed but whose
artifact upload failed (GitHub 502s, "workflow run not found": runs 43092896361 shards 2/11, 43093102021 shard 1) says
nothing about the code under test, so it is INFRA, never RED.

  cloud_infra.py shards JOBS.json            the shards (K/N, one per line) whose job failed ONLY at the upload step
  cloud_infra.py classify JOBS.json          `infra` (every failed shard job is such a shard, and at least one failed),
                                             `red` (some job failed otherwise, or a shard job never ran its test step),
                                             `ok` (no job failed)
  cloud_infra.py run RUNID [--repo O/N]      gh api the run and its LATEST attempt's jobs: prints `CLASS ATTEMPT`
                                             (what scripts/cloudrun --verdict asks; one run call + one jobs call)

JOBS.json is the Actions jobs answer ({"jobs": [{name, conclusion, steps: [{name, conclusion}]}]}), trimmed or not.
The step names are the workflow's own (.github/workflows/cloud-test.yml); tests/ci/cloud_gather.test holds them equal.
The gather job and the plan job are not shards: a failed plan is RED, the gather is the verdict itself and is ignored.
"""
import json
import re
import subprocess
import sys

TEST_STEP = "Run the shard"
UPLOAD_STEP = "Upload the shard result and log"
SHARD = re.compile(r"^shard \((\d+/\d+)\)$")
BAD = ("failure", "timed_out", "cancelled", "startup_failure")


def infra_shape(job):
    """True when the job's test step succeeded and the upload step is the one that failed."""
    st = {s["name"]: s.get("conclusion") for s in job.get("steps", [])}
    return st.get(TEST_STEP) == "success" and st.get(UPLOAD_STEP) in BAD and not any(
        c in BAD for n, c in st.items() if n != UPLOAD_STEP)


def split(jobs):
    infra, red = [], []
    for j in jobs:
        if j.get("conclusion") not in BAD:
            continue
        m = SHARD.match(j["name"])
        if m and infra_shape(j):
            infra.append(m.group(1))
        elif m or j["name"] == "plan":
            red.append(j["name"])
    return infra, red


def classify(jobs):
    infra, red = split(jobs)
    return "red" if red else ("infra" if infra else "ok")


def gh(path):
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if r.returncode:
        sys.exit("cloud_infra: gh api %s failed: %s" % (path, r.stderr.strip()[:200]))
    return json.loads(r.stdout)


def main(argv):
    if len(argv) >= 3 and argv[1] in ("shards", "classify"):
        jobs = json.load(open(argv[2]))["jobs"]
        if argv[1] == "shards":
            print("\n".join(split(jobs)[0]))
        else:
            print(classify(jobs))
        return 0
    if len(argv) >= 3 and argv[1] == "run":
        repo = argv[argv.index("--repo") + 1] if "--repo" in argv else "{owner}/{repo}"
        run = gh("repos/%s/actions/runs/%s" % (repo, argv[2]))
        jobs = gh("repos/%s/actions/runs/%s/jobs?per_page=100&filter=latest" % (repo, argv[2]))["jobs"]
        print("%s %d" % (classify(jobs), run["run_attempt"]))
        return 0
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
