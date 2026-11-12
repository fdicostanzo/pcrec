#!/usr/bin/env python3
"""workflow_perms_check.py DIR -- caller/called permission check for reusable workflows.

A workflow that does `uses: ./.github/workflows/X.yml` hands X at most the caller's grant: every permission X declares
(top-level and per-job) must be granted by the calling job (its own `permissions:`, else the caller's top-level one).
An unspecified caller grant is NONE (the repo default is not assumed). CI 43163694339 failed as "a workflow file issue":
cloud-test.yml declared actions: read, ci.yml granted only contents: read.
Prints one line per violation; exit 1 when any, 2 on a usage/parse error.
"""
import os, sys, glob
import yaml

RANK = {"none": 0, "read": 1, "write": 2}
SCOPES_ALL = None


def grants(p):
    """permissions value -> dict scope->rank, or None when the key is absent."""
    if p is None:
        return None
    if p == "read-all":
        return {"*": 1}
    if p == "write-all":
        return {"*": 2}
    if p == {} or p == "{}":
        return {}
    return {k: RANK[str(v)] for k, v in p.items()}


def level(g, scope):
    if g is None:
        return 0
    return max(g.get(scope, 0), g.get("*", 0))


def declared(wf):
    """(where, scope, rank) for every permission a workflow declares, top-level and per-job."""
    out = []
    t = grants(wf.get("permissions"))
    for s, r in (t or {}).items():
        out.append(("top-level", s, r))
    for jn, j in (wf.get("jobs") or {}).items():
        for s, r in (grants(j.get("permissions")) or {}).items():
            out.append(("job " + jn, s, r))
    return out


def main(d):
    wfdir = os.path.join(d, ".github", "workflows")
    files = sorted(glob.glob(os.path.join(wfdir, "*.yml")) + glob.glob(os.path.join(wfdir, "*.yaml")))
    wfs = {os.path.basename(f): yaml.safe_load(open(f)) for f in files}
    bad, ncalls = [], 0
    for cn, c in wfs.items():
        top = grants(c.get("permissions"))
        for jn, j in (c.get("jobs") or {}).items():
            u = j.get("uses")
            if not (isinstance(u, str) and u.startswith("./.github/workflows/")):
                continue
            ncalls += 1
            callee = os.path.basename(u)
            if callee not in wfs:
                bad.append(f"{cn} job {jn}: calls {u}, which does not exist")
                continue
            jg = grants(j.get("permissions"))
            eff = jg if jg is not None else top
            for where, scope, rank in declared(wfs[callee]):
                if rank > level(eff, scope):
                    bad.append(f"{callee} ({where}) declares {scope}: {[k for k, v in RANK.items() if v == rank][0]} "
                               f"but {cn} job {jn} grants {scope}: {[k for k, v in RANK.items() if v == level(eff, scope)][0]}")
    for b in bad:
        print("FAIL:", b)
    if not bad:
        print(f"ok: {ncalls} reusable-workflow call(s), every callee permission is granted by its caller")
    return 1 if bad else 0


if len(sys.argv) != 2:
    print(__doc__.splitlines()[0], file=sys.stderr)
    sys.exit(2)
sys.exit(main(sys.argv[1]))
