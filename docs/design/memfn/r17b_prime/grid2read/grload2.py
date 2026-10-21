"""grid2read: loaders for the zen4-grid2 slot (analysis only; no clock, no build).

Inputs are read-only, under OUT = worktrees/memfn-slot/grid2/ (listed in SHA256SUMS):
  time/raw_{F1,F3,OB,TRIG}.tsv   every launch (phase cell subject mode round pos arm ns answer load1 ts)
  time_*.log, slot.status        the harness's tables, status events
  counts.tsv, subj_facts.tsv, groups2.tsv, subjects.tsv, fit_map.tsv, f2/raw.tsv, ...

A raw file holds one *visit* per (cell, subject, mode) in time order; the quiet gate's requeue
adds a SECOND visit of the same key at the end of the phase, so visits are cut at key changes,
never merged by key (a dict keyed by round would silently overwrite the first visit).
"""
import collections, csv, hashlib, os, statistics, time

EPOCH_TZ = 'US/Eastern'
# the binding contamination window, 2026-10-16 local (EDT = UTC-4), as epoch seconds
WIN = (1792193891.0, 1792193970.0)          # 19:38:11 .. 19:39:30 EDT
LOADHI = 1.5                                  # the harness's LOADMAX
INPUTS = ['slot.status', 'provenance.txt', 'prov.out', 'prov.status', 'census.status', 'check2.status',
          'counts.tsv', 'subj_facts.tsv',
          'time/raw_F1.tsv', 'time/raw_F3.tsv', 'time/raw_OB.tsv', 'time/raw_TRIG.tsv',
          'time_F1.log', 'time_F3.log', 'time_OB.log', 'time_TRIG.log', 'f2.log', 'f2s.log']


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def hmed(xs):
    """time.sh's med: sorted, element int((n+1)/2) (the lower middle for an even count)."""
    s = sorted(xs)
    return s[int((len(s) + 1) / 2) - 1] if s else float('nan')


def load_raw(path):
    rows = []
    for d in csv.DictReader(open(path), delimiter='\t'):
        rows.append(dict(phase=d['phase'], cell=d['cell'], subj=d['subject'], mode=d['mode'],
                         rnd=int(d['round']), pos=int(d['pos']), arm=d['arm'], ns=float(d['ns']),
                         ans=d['answer'], load=float(d['load1']), ts=float(d['ts'])))
    return rows


class Visit:
    def __init__(self, phase, key):
        self.phase, self.key, self.rows = phase, key, []
        self.vid = None

    def finish(self):
        self.t0 = min(r['ts'] for r in self.rows)
        self.t1 = max(r['ts'] for r in self.rows)
        self.loadmax = max(r['load'] for r in self.rows)
        self.n_in_win = sum(WIN[0] <= r['ts'] <= WIN[1] for r in self.rows)
        # a launch's stamp is taken AFTER it ends; a launch lasts <= ~0.95 s (SEC_STREAM 0.65, grid1 0.95),
        # so it overlaps the window iff stamp >= WIN[0] and stamp - 1.0 <= WIN[1]
        self.overlap = any(t >= WIN[0] and t - 1.0 <= WIN[1] for t in (r['ts'] for r in self.rows))
        self.n_load_hi = sum(r['load'] > LOADHI for r in self.rows)
        self.launches = max(r['rnd'] for r in self.rows)
        self.arm_vals = collections.defaultdict(dict)       # arm -> {round: ns}
        self.answers = collections.defaultdict(set)
        for r in self.rows:
            self.arm_vals[r['arm']][r['rnd']] = r['ns']
            self.answers[r['arm']].add(r['ans'])
        return self

    def med(self, arm):
        return hmed(list(self.arm_vals[arm].values()))

    def spread(self, arm):
        v = list(self.arm_vals[arm].values())
        m = hmed(v)
        return (min(v) - m) / m, (max(v) - m) / m


def visits(path, phase):
    rows = load_raw(path)
    out, cur = [], None
    for r in rows:
        k = (r['cell'], r['subj'], r['mode'])
        if cur is None or cur.key != k:
            cur = Visit(phase, k)
            out.append(cur)
        cur.rows.append(r)
    for v in out:
        v.finish()
    seen = collections.Counter()
    for v in out:
        seen[v.key] += 1
        v.vid = seen[v.key]
    return out


def base_of(visit):
    """the base arm name (the arm that has '#b' and '#c' copies)."""
    for a in visit.arm_vals:
        if a + '#b' in visit.arm_vals:
            return a
    raise KeyError(visit.key)


def usable(v, strict_load=True):
    """overlap with the contamination window is excluded everywhere; a load1 > LOADMAX excursion
    inside a visit is flagged (suspect) and excluded only where strict_load is set."""
    if v.overlap:
        return False
    if strict_load and v.n_load_hi:
        return False
    return True


def parse_kv(s):
    d = {}
    for x in s.split():
        if '=' in x:
            k, v = x.split('=', 1)
            try:
                d[k] = int(v)
            except ValueError:
                d[k] = v
    return d


def load_counts(path):
    C = {}
    for d in csv.DictReader(open(path), delimiter='\t'):
        C[(d['cell'], d['arm'], d['subject'], d['mode'])] = parse_kv(d['counters'])
    return C


def load_facts(path):
    F = {}
    for d in csv.DictReader(open(path), delimiter='\t'):
        F[d['name']] = dict(fam=d['family'], n=int(d['n']), g=int(d['g']), L=int(d['L']),
                            shape=d['shape'], reuse=d['reuse'], nbuf=int(d['nbuf']),
                            pm=int(d['planted_matches']), pl=int(d['planted_landings']))
    return F


def hms(t):
    return time.strftime('%H:%M:%S', time.localtime(t))
