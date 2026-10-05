#!/bin/bash
# cases.sh — every cross-source cell option_sets.md §2.5a tabulates, in
# table order. Usage: SCRATCH=<dir> ./cases.sh > out/cross_source.txt
here=$(cd "$(dirname "$0")" && pwd); X=$here/probe.sh
V='x(ab|cd)+y'   # VM (capture-bearing) witness
D='ab+cd'        # DFA witness
echo "# pcrec $(${PCREC:-$here/../../../build/pcrec} --version 2>&1 | head -1); tree $(git -C "$here" rev-parse --short HEAD)"
# raw -f bits: union, then the pair rule
$X A1  $V 'pcrec -fno-prefilter' '' -- -fprefilter
$X A2  $V 'pcrec -fprefilter' '' -- -fno-prefilter
$X A3  $V '' '' -- -fno-prefilter
$X A4  $D 'pcrec -fno-premul-table' '' -- -fno-req-byte
$X A5  $V 'pcrec -fno-startpos-guard' '' -- -fstartpos-guard=align
$X A6  $V 'pcrec -fcomments' '' -- -fno-comments
$X A7  $V 'pcrec -fno-comments' '' -- -fcomments
$X A8  $V '' '' -- -fcomments
$X A9  $V 'pcrec -fprefilter\npcrec -fno-prefilter' '' --
$X A10 $V 'pcrec -fcomments\npcrec -fno-comments' '' --
# typed `flags` letters vs raw -i/--ucp vs the CLI
$X B1  $V 'features ucp' 'flags u' -- -i
$X B2  $V 'flags u\nfeatures ucp' '' -- -i
$X B3  $V 'pcrec --ucp\nfeatures ucp' '' -- -i
$X B4  $V 'flags i' '' -- --no-captures
$X B7  $V 'pcrec -i' 'flags u\nfeatures ucp' --
$X B8  $V 'flags i\nfeatures ucp' 'flags u' --
# features
$X C1  '(?>a)b' 'features std1' '' -- --features atomic-groups
$X C2  '(?>a)b' '' '' -- --features atomic-groups
$X C3  '(?>a)b' 'pcrec --features std1' '' -- --features atomic-groups
$X C5  '(?>a)b' 'features atomic-groups' '' -- --features lookaround
$X C6  '(?>a)(?=b)b' 'features atomic-groups' '' -- --features lookaround
$X C8  '(?>a)(?=b)b' 'features atomic-groups' 'features lookaround' --
# engine
$X D1  $D 'engine vm' '' -- --engine=dfa
$X D2  $D 'engine vm' '' -- --engine=auto
$X D3  $D 'pcrec --engine=vm' '' -- --engine=dfa
# tune
$X E1  $V 'tune speed' '' -- --tune=min-size
$X E2  $V 'pcrec --tune=speed' '' -- --tune=min-size
$X E3  $V 'pcrec --tune=min-size\ntune speed' '' --
$X E4  $V '' '' -- --tune=min-size --tune=speed
$X T1  $V 'tune min-size' '' -- -fno-tiered-entry
$X T2  $D 'pcrec -fno-premul-table' '' -- --tune=speed
# analysis
$X F1  $V 'analysis log' '' -- --analysis weblog
$X F2  $V 'tune balanced' '' -- --analysis weblog
# encoding
$X G1  $V 'encoding utf8' '' -- -e byte
$X G2  $V 'pcrec -e utf8' '' -- -e byte
$X G4  $V 'encoding utf8' 'encoding byte' --
# value options and budgets
$X H1  $V 'pcrec --unroll=4' '' -- --unroll=2
$X H3  $V 'budget steps=1000' '' -- --step-budget=2000
$X H4  $V 'pcrec --step-budget=1000' '' -- --step-budget=2000
$X H6  $V '' '' -- --step-budget=2000
# constraint rows co-firing on one compile (OS-M3)
$X M3  $V '' '' -- -futf-check -fstartpos-guard=align
$X M3b $V '' '' -- -futf-check=extent
