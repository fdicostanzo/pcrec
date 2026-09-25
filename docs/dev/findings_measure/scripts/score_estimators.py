#!/usr/bin/env python3
"""[FINDINGS] Q5 measurement — score run-density estimators against TRUE
occurrence counts on held-out text, per corpus class (D123 addendum 3).

Candidates (docs/design/findings/requirements.md R6):
  (0) unigram independence product, using the SHIPPED static prior
      (src/opt/prefix_k.c's pcrec_byte_freq_ppm, dumped to byte_freq_ppm.tsv);
  (1) bigram Markov chain, fit per class on the TRAIN half;
  (2) trigram Markov chain (top-K observed contexts; falls back to the
      bigram chain for an unseen (b0,b1) context) — this is candidates (b)
      and (c) combined: a hashed/top-K n-gram table used AS a chain;
  (3) a token/word table (top-K exact tokens with fallback to the bigram
      chain for a run that is not an exact token in this class's text);
  (4) a hybrid: token-exact override on top of the trigram chain.

Metric: predicted and true DENSITY (occurrences per 1e6 bytes), plus the
per-class RANK correlation (Spearman) of predicted vs true density across
the candidate run set — the "does it pick the truly rarest run" question —
and the WAF sign check (does an estimator rank union rarer than select
rarer than from, matching the true corpus order).

Nothing here is derived from pcrec-bench subjects for FITTING (R30): the
four training corpora are fetched public samples (manifest.tsv). The bench
t-1m.bin capability throughput subject is read ONLY as an out-of-sample
EVALUATION set, explicitly labelled, never used to fit any table.
"""
from __future__ import annotations
import json
import math
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from ngram_count import Counts, count_run_occurrences  # noqa: E402

FLOOR = 1e-9  # per-symbol probability floor, avoids log(0) / zero predictions


def load_static_ppm(path: str) -> list[float]:
    tbl = [0.0] * 256
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            b, ppm = line.split('\t')
            tbl[int(b)] = int(ppm) / 1_000_000.0
    return tbl


def load_runs(path: str) -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    with open(path) as f:
        for line in f:
            parts = line.rstrip('\n').split('\t')
            name, hexs = parts[0], parts[1]
            out[name] = bytes.fromhex(hexs)
    return out


def split_train_test(data: bytes, frac: float = 0.8) -> tuple[bytes, bytes]:
    cut = int(len(data) * frac)
    return data[:cut], data[cut:]


class BigramModel:
    """P(b_i | b_{i-1}) with add-one smoothing over 256 symbols."""

    def __init__(self, counts: Counts):
        self.uni = counts.unigram
        self.n = sum(self.uni) or 1
        self.bi = counts.bigram
        self.row_totals: dict[int, int] = {}
        for (a, b), c in self.bi.items():
            self.row_totals[a] = self.row_totals.get(a, 0) + c

    def p_first(self, b: int) -> float:
        return (self.uni[b] + 1) / (self.n + 256)

    def p_next(self, prev: int, b: int) -> float:
        row_total = self.row_totals.get(prev, 0)
        c = self.bi.get((prev, b), 0)
        return (c + 1) / (row_total + 256)

    def p_run(self, run: bytes) -> float:
        p = self.p_first(run[0])
        for i in range(1, len(run)):
            p *= self.p_next(run[i - 1], run[i])
        return p

    def size_bytes(self) -> int:
        # dense 256x256 table of ppm-scale integers (2 bytes/entry) -- the
        # emitted shape a shipped bigram analysis would take.
        return 256 * 256 * 2


class TrigramModel:
    """P(b_i | b_{i-2}, b_{i-1}), top-K observed contexts only; falls back
    to the bigram chain for any unseen (b0,b1) context or unseen next byte."""

    def __init__(self, counts: Counts, bigram: BigramModel, top_k: int = 20000):
        top = counts.top_k_trigrams(top_k)
        self.tri: dict[tuple[int, int, int], int] = dict(top)
        self.ctx_totals: dict[tuple[int, int], int] = {}
        for (a, b, c), cnt in self.tri.items():
            self.ctx_totals[(a, b)] = self.ctx_totals.get((a, b), 0) + cnt
        self.bigram = bigram
        self.kept = len(self.tri)
        self.dropped = len(counts.trigram) - self.kept

    def p_next(self, ctx: tuple[int, int], b: int) -> float:
        total = self.ctx_totals.get(ctx)
        if total is None:
            return self.bigram.p_next(ctx[1], b)  # unseen context: fall back
        c = self.tri.get((ctx[0], ctx[1], b), 0)
        # Witten-Bell-ish: reserve mass for unseen next-byte within a seen
        # context by blending toward the bigram fallback rather than a flat
        # add-one (a seen context should not default to uniform).
        alpha = total / (total + 1)
        return alpha * (c / total) + (1 - alpha) * self.bigram.p_next(ctx[1], b)

    def p_run(self, run: bytes) -> float:
        p = self.bigram.p_first(run[0])
        if len(run) > 1:
            p *= self.bigram.p_next(run[0], run[1])
        for i in range(2, len(run)):
            p *= self.p_next((run[i - 2], run[i - 1]), run[i])
        return p

    def size_bytes(self) -> int:
        # sparse table: 3-byte key + 2-byte count per kept entry
        return self.kept * 5


class TokenModel:
    """Top-K exact-token frequency, falling back to a supplied chain model
    for any run that is not an exact token of this class's training text."""

    def __init__(self, counts: Counts, fallback, top_k: int = 4000):
        self.top = dict(counts.top_k_tokens(top_k))
        self.n_train = counts.n
        self.fallback = fallback
        self.kept = len(self.top)

    def p_run(self, run: bytes) -> tuple[float, bool]:
        if run in self.top:
            # empirical per-byte density of this exact token, train-fitted
            return self.top[run] / self.n_train, True
        return self.fallback.p_run(run), False

    def size_bytes(self) -> int:
        # token bytes + 4-byte count, per kept entry
        return sum(len(k) + 4 for k in self.top)


def independence_baseline(run: bytes, ppm: list[float]) -> float:
    p = 1.0
    for b in run:
        p *= max(ppm[b], FLOOR)
    return p


def spearman(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return float('nan')

    def ranks(v: list[float]) -> list[float]:
        order = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg_rank
            i = j + 1
        return r

    rx, ry = ranks(xs), ranks(ys)
    mean_rx, mean_ry = sum(rx) / n, sum(ry) / n
    num = sum((a - mean_rx) * (b - mean_ry) for a, b in zip(rx, ry))
    denx = math.sqrt(sum((a - mean_rx) ** 2 for a in rx))
    deny = math.sqrt(sum((b - mean_ry) ** 2 for b in ry))
    if denx == 0 or deny == 0:
        return float('nan')
    return num / (denx * deny)


def log_error(pred: float, true: float) -> float:
    pred = max(pred, 1e-15)
    true_c = max(true, 1e-15)
    return math.log2(pred / true_c)


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    fm = os.path.dirname(here)                 # docs/dev/findings_measure
    repo = os.path.dirname(os.path.dirname(os.path.dirname(fm)))  # repo root
    data_dir = os.path.join(fm, 'data')
    corpora_dir = os.path.join(fm, 'corpora')
    os.makedirs(data_dir, exist_ok=True)
    ppm = load_static_ppm(os.path.join(data_dir, 'byte_freq_ppm.tsv'))
    runs = load_runs(os.path.join(data_dir, 'runs.tsv'))
    # dedupe by literal bytes, keep first name as label
    uniq_runs: dict[bytes, str] = {}
    for name, r in runs.items():
        uniq_runs.setdefault(r, name)
    run_list = [(name, r) for r, name in uniq_runs.items()]

    classes = {
        'web_request': os.path.join(corpora_dir, 'web_request.txt'),
        'log_lines': os.path.join(corpora_dir, 'log_lines.txt'),
        'prose': os.path.join(corpora_dir, 'prose.txt'),
        'json': os.path.join(corpora_dir, 'json.txt'),
    }
    for cls, p in classes.items():
        if not os.path.exists(p):
            print(f"missing corpus for class={cls}: {p}\n"
                  f"  run scripts/fetch_corpora.sh first (see manifest.tsv)", file=sys.stderr)
            sys.exit(1)

    results = []  # rows for the TSV
    class_models = {}
    class_data = {}

    for cls, path in classes.items():
        data = open(path, 'rb').read()
        train, test = split_train_test(data)
        counts = Counts.build(train)
        bigram = BigramModel(counts)
        trigram = TrigramModel(counts, bigram, top_k=20000)
        token = TokenModel(counts, bigram, top_k=4000)
        class_models[cls] = dict(bigram=bigram, trigram=trigram, token=token, counts=counts)
        class_data[cls] = dict(train=train, test=test)

        true_density = {}
        true_count_raw = {}
        pred = {est: {} for est in ('baseline', 'bigram', 'trigram', 'token', 'hybrid')}
        for name, run in run_list:
            true_cnt = count_run_occurrences(test, run)
            true_count_raw[name] = true_cnt
            # continuity correction (+0.5): a raw zero count in a small
            # held-out sample is not evidence of impossibility (the same
            # floor discipline prefix_k.c's own table uses), and without it
            # the log-error metric is dominated by an infinite ratio against
            # a sample-size artifact rather than a real estimator error.
            true_density[name] = (true_cnt + 0.5) / max(len(test), 1) * 1_000_000

            p_base = independence_baseline(run, ppm) * 1_000_000
            p_bi = bigram.p_run(run) * 1_000_000
            p_tri = trigram.p_run(run) * 1_000_000
            p_tok, tok_hit = token.p_run(run)
            p_tok *= 1_000_000
            p_hybrid = (p_tok if tok_hit else p_tri)

            pred['baseline'][name] = p_base
            pred['bigram'][name] = p_bi
            pred['trigram'][name] = p_tri
            pred['token'][name] = p_tok
            pred['hybrid'][name] = p_hybrid

            for est in pred:
                results.append(dict(
                    corpus=cls, run=name, run_bytes=run.decode('latin1'),
                    run_len=len(run), estimator=est,
                    true_count=true_count_raw[name],
                    true_density_ppm=true_density[name],
                    pred_density_ppm=pred[est][name],
                    log2_error=log_error(pred[est][name], true_density[name]),
                    token_exact=(est in ('token', 'hybrid') and tok_hit),
                ))

        # per-class rank correlation & summary, printed to stderr / captured by caller
        names = [n for n, _ in run_list]
        true_vec = [true_density[n] for n in names]
        for est in pred:
            pred_vec = [pred[est][n] for n in names]
            rho = spearman(pred_vec, true_vec)
            mae = sum(abs(log_error(pred[est][n], true_density[n])) for n in names) / len(names)
            print(f"class={cls}\testimator={est}\tspearman_rho={rho:.4f}\tlog2_MAE={mae:.4f}",
                  file=sys.stderr)

    # write scoring TSV
    out_path = os.path.join(data_dir, 'scoring.tsv')
    cols = ['corpus', 'run', 'run_bytes', 'run_len', 'estimator', 'true_count',
            'true_density_ppm', 'pred_density_ppm', 'log2_error', 'token_exact']
    with open(out_path, 'w') as f:
        f.write('\t'.join(cols) + '\n')
        for row in results:
            f.write('\t'.join(str(row[c]) for c in cols) + '\n')

    # table sizes
    sizes = {}
    for cls, m in class_models.items():
        sizes[cls] = dict(
            bigram_bytes=m['bigram'].size_bytes(),
            trigram_bytes=m['trigram'].size_bytes(),
            trigram_kept=m['trigram'].kept,
            trigram_dropped=m['trigram'].dropped,
            token_bytes=m['token'].size_bytes(),
            token_kept=m['token'].kept,
            train_len=len(class_data[cls]['train']),
            test_len=len(class_data[cls]['test']),
        )
    with open(os.path.join(data_dir, 'table_sizes.json'), 'w') as f:
        json.dump(sizes, f, indent=2)

    print(json.dumps(sizes, indent=2), file=sys.stderr)

    # derived tables for the recommended estimator (bigram: see report) --
    # one JSON per class, sparse bigram counts + unigram counts, so the
    # winning shape is reproducible without re-fetching/re-splitting.
    os.makedirs(os.path.join(data_dir, 'tables'), exist_ok=True)
    for cls, m in class_models.items():
        bigram_out = {f"{a},{b}": c for (a, b), c in m['counts'].bigram.items()}
        table = dict(
            train_len=len(class_data[cls]['train']),
            unigram=m['counts'].unigram,
            bigram_sparse=bigram_out,
            top_tokens=[[tok.decode('latin1'), cnt] for tok, cnt in m['counts'].top_k_tokens(200)],
        )
        with open(os.path.join(data_dir, 'tables', f'{cls}_bigram.json'), 'w') as f:
            json.dump(table, f)

    # --- WAF sign check: does each estimator rank union rarer than select
    # rarer than from, on web_request (deployment-shaped) text? ---
    waf_runs = [('waf/union', b'union'), ('waf/select', b'select'), ('waf/from', b'from')]
    wr_test = class_data['web_request']['test']
    m = class_models['web_request']
    print("\n--- WAF rank check on web_request held-out text ---", file=sys.stderr)
    true_order = sorted(waf_runs, key=lambda kv: count_run_occurrences(wr_test, kv[1]))
    print("true order (rarest first): " + " < ".join(n for n, _ in true_order), file=sys.stderr)
    for est_name, fn in [
        ('baseline', lambda r: independence_baseline(r, ppm)),
        ('bigram', lambda r: m['bigram'].p_run(r)),
        ('trigram', lambda r: m['trigram'].p_run(r)),
        ('token', lambda r: m['token'].p_run(r)[0]),
        ('hybrid', lambda r: (lambda pt, hit: pt if hit else m['trigram'].p_run(r))(*m['token'].p_run(r))),
    ]:
        order = sorted(waf_runs, key=lambda kv: fn(kv[1]))
        matches = [n for n, _ in order] == [n for n, _ in true_order]
        print(f"{est_name}: predicted order " + " < ".join(n for n, _ in order)
              + f"  MATCHES_TRUE={matches}", file=sys.stderr)

    # --- out-of-sample generalization: apply web_request/log_lines-trained
    # models to the pcrec-bench capability throughput subject (t-1m.bin),
    # READ-ONLY, EVALUATION ONLY -- never used to fit any table (R30). ---
    bench_path = os.path.join(os.path.dirname(repo), 'pcrec-bench',
                               'bench/capability/throughput/t-1m.bin')
    if os.path.exists(bench_path):
        bench_data = open(bench_path, 'rb').read()
        print(f"\n--- bench t-1m.bin EVALUATION ONLY ({len(bench_data)} bytes) ---", file=sys.stderr)
        names = [n for n, _ in run_list]
        true_bench = {n: count_run_occurrences(bench_data, r) for n, r in run_list}
        bench_rows = []
        for src_cls in ('web_request', 'log_lines'):
            m2 = class_models[src_cls]
            preds = {
                'baseline': {n: independence_baseline(r, ppm) for n, r in run_list},
                'trigram': {n: m2['trigram'].p_run(r) for n, r in run_list},
                'hybrid': {n: (lambda pt, hit: pt if hit else m2['trigram'].p_run(r))(*m2['token'].p_run(r))
                           for n, r in run_list},
            }
            true_vec = [true_bench[n] for n in names]
            for est, pv in preds.items():
                pred_vec = [pv[n] for n in names]
                rho = spearman(pred_vec, true_vec)
                print(f"trained_on={src_cls}\testimator={est}\tspearman_rho_vs_bench={rho:.4f}",
                      file=sys.stderr)
                for n in names:
                    bench_rows.append(dict(
                        trained_on=src_cls, estimator=est, run=n,
                        true_count_bench=true_bench[n],
                        pred_density_ppm=pv[n] * 1_000_000,
                    ))
        with open(os.path.join(data_dir, 'bench_eval.tsv'), 'w') as f:
            cols2 = ['trained_on', 'estimator', 'run', 'true_count_bench', 'pred_density_ppm']
            f.write('\t'.join(cols2) + '\n')
            for row in bench_rows:
                f.write('\t'.join(str(row[c]) for c in cols2) + '\n')


if __name__ == '__main__':
    main()
