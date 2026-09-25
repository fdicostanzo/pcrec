#!/usr/bin/env python3
"""Reusable byte-level counting module for [FINDINGS] Q5 (D123 addendum 3).

Shared by the estimator scorer here and intended as the prototype for the
one-counter rule (R27b): the shipped generators and the analyzer/exemplar
scanner should share ONE counting implementation. This module counts
unigrams, bigrams, trigrams and whitespace/punctuation-delimited tokens over
a byte string in ONE PASS each, streaming-friendly (works on a bytes object
or anything that yields bytes in chunks via `iter_chunks`).

No dependency on pcrec's own source; this is the python PROTOTYPE tier
(D123 addendum 3, Q8): the analyzer's eventual C end state would reimplement
these same four counts with the same definitions.
"""
from __future__ import annotations
import collections
from typing import Iterable, Iterator

TOKEN_BREAK = set(b" \t\r\n\"'(){}[]<>,;:=/\\?&%#!*+|^~`")


def iter_chunks(data: bytes, chunk_size: int = 1 << 16) -> Iterator[bytes]:
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


class Counts:
    """One-pass counts over a byte string: unigram, bigram, trigram, token.

    unigram: 256-entry count table.
    bigram: dict[(b0,b1)] -> count, 65536 possible keys.
    trigram: dict[(b0,b1,b2)] -> count, sparse (only observed).
    tokens: dict[bytes token] -> count, split on TOKEN_BREAK, empties dropped.
    n: total byte length counted.
    """

    def __init__(self) -> None:
        self.unigram = [0] * 256
        self.bigram: dict[tuple[int, int], int] = collections.defaultdict(int)
        self.trigram: dict[tuple[int, int, int], int] = collections.defaultdict(int)
        self.tokens: dict[bytes, int] = collections.defaultdict(int)
        self.n = 0

    def add(self, data: bytes) -> None:
        n = len(data)
        self.n += n
        uni = self.unigram
        for b in data:
            uni[b] += 1
        bg = self.bigram
        tg = self.trigram
        for i in range(n - 1):
            bg[(data[i], data[i + 1])] += 1
        for i in range(n - 2):
            tg[(data[i], data[i + 1], data[i + 2])] += 1
        # tokens (whole-string tokenization is fine at this corpus size;
        # a streaming version would carry a partial-token tail across chunks)
        tok = self.tokens
        cur = bytearray()
        for b in data:
            if b in TOKEN_BREAK:
                if cur:
                    tok[bytes(cur)] += 1
                    cur = bytearray()
            else:
                cur.append(b)
        if cur:
            tok[bytes(cur)] += 1

    @classmethod
    def build(cls, data: bytes) -> "Counts":
        c = cls()
        for chunk in iter_chunks(data):
            c.add(chunk)
        return c

    def top_k_trigrams(self, k: int) -> list[tuple[tuple[int, int, int], int]]:
        return sorted(self.trigram.items(), key=lambda kv: -kv[1])[:k]

    def top_k_tokens(self, k: int) -> list[tuple[bytes, int]]:
        return sorted(self.tokens.items(), key=lambda kv: -kv[1])[:k]


def count_run_occurrences(data: bytes, run: bytes) -> int:
    """Exact overlapping-aware substring count (non-overlapping, str.count
    semantics — matches memchr/memcmp-style scanning: one hit consumes the
    run before scanning resumes, same convention pcrec's own REQ_RUN scan
    uses at a single scan byte)."""
    return data.count(run)
