import re, sys, json
from collections import defaultdict, Counter

LOG = "/private/tmp/claude-501/-Users-fdicostanzo-pcrec/6c826da8-f394-412e-b898-373008f3c3a9/scratchpad/grain/full_log.txt"

commit_re = re.compile(r'^COMMIT\t([0-9a-f]{40})\t(\d{4}-\d{2}-\d{2})\t(.*)$')
hunk_re = re.compile(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@\s?(.*)$')
tag_re = re.compile(r'\[([^\]\[]{1,40}?)\]')

def funcname_from_context(ctx):
    ctx = ctx.strip()
    if not ctx:
        return None
    # heuristic: identifier before first '(' -- typical for C function defs
    m = re.search(r'([A-Za-z_][A-Za-z0-9_]*)\s*\(', ctx)
    if m:
        name = m.group(1)
        # filter out control keywords picked up as "function-like"
        if name in ('if','for','while','switch','return','sizeof','static'):
            return ('FILESCOPE', ctx)
        return name
    return ('FILESCOPE', ctx)

commits = []  # list of dicts: hash,date,subject,campaign,funcs(set),hunks(list of (func,line))
cur = None

with open(LOG, encoding='utf-8', errors='replace') as f:
    for line in f:
        line = line.rstrip('\n')
        m = commit_re.match(line)
        if m:
            if cur is not None:
                commits.append(cur)
            h, d, s = m.groups()
            tagm = tag_re.search(s)
            campaign = tagm.group(1) if tagm else None
            cur = {'hash': h, 'date': d, 'subject': s, 'campaign': campaign,
                   'funcs': [], 'hunk_ctx': []}
            continue
        hm = hunk_re.match(line)
        if hm and cur is not None:
            a, b, c, d, ctx = hm.groups()
            fn = funcname_from_context(ctx)
            cur['hunk_ctx'].append(ctx)
            if fn is None:
                label = 'FILESCOPE:(empty)'
            elif isinstance(fn, tuple):
                label = 'FILESCOPE'
            else:
                label = fn
            cur['funcs'].append(label)
if cur is not None:
    commits.append(cur)

print(f"Total commits parsed: {len(commits)}", file=sys.stderr)

# distinguish sweeps: >60 distinct functions touched
for c in commits:
    c['func_set'] = sorted(set(c['funcs']))
    c['n_funcs'] = len(c['func_set'])
    c['is_sweep'] = c['n_funcs'] > 60

with open('/private/tmp/claude-501/-Users-fdicostanzo-pcrec/6c826da8-f394-412e-b898-373008f3c3a9/scratchpad/grain/commits.json','w') as f:
    json.dump(commits, f, indent=1)

sweeps = [c for c in commits if c['is_sweep']]
nonsweep = [c for c in commits if not c['is_sweep']]
print(f"Sweeps: {len(sweeps)}  Non-sweep: {len(nonsweep)}", file=sys.stderr)
for c in sweeps:
    print(f"SWEEP {c['hash'][:10]} {c['date']} n_funcs={c['n_funcs']} {c['subject']}", file=sys.stderr)
