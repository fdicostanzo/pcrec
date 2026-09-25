
### (a)
| pattern | regime | testee | REQ_WHY | b1885a83 ns | 6ef76820 ns | Δ% | IQR% | null edge | verdict (IQR / band) |
|---|---|---|---|---|---|---|---|---|---|
| wild-validator-email-owasp | thr | auto-caps | one-attempt | 23,158.8 | 37.0 | -99.84 | 0.12 | -8.18 | improve / improve |
| wild-validator-email-owasp | thr | auto-nocaps | one-attempt | 23,119.5 | 38.0 | -99.84 | 0.10 | -8.18 | improve / improve |
| wild-validator-email-owasp | thr | vm-caps | one-attempt | 23,200.5 | 63.1 | -99.73 | 0.13 | -8.18 | improve / improve |
| wild-validator-email-owasp | thr | vm-in-caps | one-attempt | 23,118.8 | 68.8 | -99.70 | 0.20 | -8.18 | improve / improve |

### (b)
| pattern | regime | testee | REQ_WHY | b1885a83 ns | 6ef76820 ns | Δ% | IQR% | null edge | verdict (IQR / band) |
|---|---|---|---|---|---|---|---|---|---|
| winpath-near-miss | thr | auto-caps | one-attempt | 23,143.3 | 18.8 | -99.92 | 0.14 | -8.18 | improve / improve |
| winpath-near-miss | thr | auto-nocaps | one-attempt | 23,145.0 | 18.9 | -99.92 | 0.12 | -8.18 | improve / improve |
| winpath-near-miss | thr | vm-caps | one-attempt | 23,143.2 | 27.7 | -99.88 | 0.02 | -8.18 | improve / improve |
| winpath-near-miss | thr | vm-in-caps | one-attempt | 23,156.0 | 36.4 | -99.84 | 0.05 | -8.18 | improve / improve |
| email-nested-plus | thr | auto-caps | one-attempt | 23,136.1 | 48.1 | -99.79 | 0.10 | -8.18 | improve / improve |
| email-nested-plus | thr | auto-nocaps | one-attempt | 23,133.8 | 37.1 | -99.84 | 0.10 | -8.18 | improve / improve |
| email-nested-plus | thr | vm-caps | one-attempt | 23,126.7 | 7,206.9 | -68.84 | 0.13 | -8.18 | improve / improve |
| email-nested-plus | thr | vm-in-caps | one-attempt | 23,148.1 | 7,257.4 | -68.65 | 0.15 | -8.18 | improve / improve |

### (c)
| pattern | regime | testee | REQ_WHY | b1885a83 ns | 6ef76820 ns | Δ% | IQR% | null edge | verdict (IQR / band) |
|---|---|---|---|---|---|---|---|---|---|
| wild-codegrammar-json-array-begin | thr | auto-caps | dominated | 349,719.5 | 263,314.2 | -24.71 | 0.01 | -8.18 | improve / improve |
| wild-codegrammar-json-array-begin | thr | auto-nocaps | dominated | 349,629.1 | 263,573.7 | -24.61 | 0.20 | -8.18 | improve / improve |
| wild-codegrammar-json-array-begin | thr | vm-caps | emitted | 1,101,475.4 | 1,098,667.1 | -0.25 | 0.20 | -8.18 | improve / within |
| wild-codegrammar-json-array-begin | thr | vm-in-caps | emitted | 1,094,794.5 | 1,114,971.0 | +1.84 | 0.27 | +6.75 | REGRESS / within |

### (d)
| pattern | regime | testee | REQ_WHY | b1885a83 ns | 6ef76820 ns | Δ% | IQR% | null edge | verdict (IQR / band) |
|---|---|---|---|---|---|---|---|---|---|
| uuid-near-miss | thr | auto-caps | one-attempt | 27.6 | 13.5 | -51.11 | 0.10 | -29.68 | improve / improve |
| uuid-near-miss | thr | auto-nocaps | one-attempt | 27.6 | 13.3 | -51.60 | 0.11 | -29.68 | improve / improve |
| uuid-near-miss | srch | auto-caps | one-attempt | 671.5 | 547.9 | -18.40 | 0.93 | -3.80 | improve / improve |
| uuid-near-miss | srch | auto-nocaps | one-attempt | 671.4 | 548.6 | -18.30 | 0.46 | -3.80 | improve / improve |
| ipv4-near-miss | thr | auto-caps | one-attempt | 24.9 | 12.6 | -49.56 | 0.08 | -29.68 | improve / improve |
| ipv4-near-miss | thr | auto-nocaps | one-attempt | 24.9 | 12.6 | -49.33 | 0.10 | -29.68 | improve / improve |
| ipv4-near-miss | srch | auto-caps | one-attempt | 627.2 | 444.9 | -29.07 | 0.06 | -3.80 | improve / improve |
| ipv4-near-miss | srch | auto-nocaps | one-attempt | 627.4 | 444.8 | -29.10 | 0.27 | -3.80 | improve / improve |

### (f)
| pattern | regime | testee | REQ_WHY | b1885a83 ns | 6ef76820 ns | Δ% | IQR% | null edge | verdict (IQR / band) |
|---|---|---|---|---|---|---|---|---|---|
| nested-comment-rec | thr | auto-caps | emitted | 23,118.5 | 23,172.8 | +0.24 | 0.06 | +6.75 | REGRESS / within |
| nested-comment-rec | thr | auto-nocaps | emitted | 23,134.7 | 23,148.6 | +0.06 | 0.06 | +6.75 | REGRESS / within |
| nested-comment-rec | thr | vm-caps | emitted | 23,152.5 | 23,138.7 | -0.06 | 0.12 | -8.18 | within / within |
| nested-comment-rec | thr | vm-in-caps | emitted | 23,149.3 | 23,133.3 | -0.07 | 0.17 | -8.18 | within / within |

### (g)
| pattern | regime | testee | REQ_WHY | b1885a83 ns | 6ef76820 ns | Δ% | IQR% | null edge | verdict (IQR / band) |
|---|---|---|---|---|---|---|---|---|---|
| wild-secrets-github-pat | thr | vm-caps | emitted | 129,145.4 | 129,109.7 | -0.03 | 0.19 | -8.18 | within / within |
| wild-secrets-github-pat | thr | vm-in-caps | emitted | 125,586.1 | 125,631.9 | +0.04 | 0.07 | +6.75 | within / within |

### (h)
| pattern | regime | testee | REQ_WHY | b1885a83 ns | 6ef76820 ns | Δ% | IQR% | null edge | verdict (IQR / band) |
|---|---|---|---|---|---|---|---|---|---|
| router-prefix-order | thr | auto-caps | emitted | 720,485.6 | 719,995.6 | -0.07 | 0.02 | -8.18 | improve / within |
| router-prefix-order | thr | auto-nocaps | emitted | 720,106.1 | 720,273.3 | +0.02 | 0.11 | +6.75 | within / within |
| router-prefix-order | thr | vm-caps | emitted | 4,451,241.0 | 4,459,252.1 | +0.18 | 0.14 | +6.75 | REGRESS / within |
| router-prefix-order | thr | vm-in-caps | emitted | 4,441,972.6 | 4,443,144.3 | +0.03 | 0.14 | +6.75 | within / within |
| keyword-prefix-order | thr | auto-caps | emitted | 1,236,473.0 | 1,238,485.2 | +0.16 | 0.08 | +6.75 | REGRESS / within |
| keyword-prefix-order | thr | auto-nocaps | emitted | 1,237,361.1 | 1,239,078.3 | +0.14 | 0.03 | +6.75 | REGRESS / within |
| keyword-prefix-order | thr | vm-caps | emitted | 4,625,669.0 | 4,617,899.1 | -0.17 | 0.12 | -8.18 | improve / within |
| keyword-prefix-order | thr | vm-in-caps | emitted | 4,643,087.0 | 4,640,082.7 | -0.06 | 0.19 | -8.18 | within / within |

### G2 29
| pattern | regime | testee | REQ_WHY | b1885a83 ns | 6ef76820 ns | Δ% | IQR% | null edge | verdict (IQR / band) | vs batch-1 BEFORE 25b1984f |
|---|---|---|---|---|---|---|---|---|---|---|
| uuid-near-miss | thr | auto-caps | one-attempt | 27.6 | 13.5 | -51.11 | 0.10 | -29.68 | improve / improve | -32.37% |
| uuid-near-miss | thr | auto-nocaps | one-attempt | 27.6 | 13.3 | -51.60 | 0.11 | -29.68 | improve / improve | -32.98% |
| uuid-near-miss | srch | auto-caps | one-attempt | 671.5 | 547.9 | -18.40 | 0.93 | -3.80 | improve / improve | -2.50% |
| uuid-near-miss | srch | auto-nocaps | one-attempt | 671.4 | 548.6 | -18.30 | 0.46 | -3.80 | improve / improve | -3.01% |
| ipv4-near-miss | thr | auto-caps | one-attempt | 24.9 | 12.6 | -49.56 | 0.08 | -29.68 | improve / improve | -33.21% |
| ipv4-near-miss | thr | auto-nocaps | one-attempt | 24.9 | 12.6 | -49.33 | 0.10 | -29.68 | improve / improve | -32.67% |
| ipv4-near-miss | srch | auto-caps | one-attempt | 627.2 | 444.9 | -29.07 | 0.06 | -3.80 | improve / improve | -9.59% |
| ipv4-near-miss | srch | auto-nocaps | one-attempt | 627.4 | 444.8 | -29.10 | 0.27 | -3.80 | improve / improve | -10.50% |
| logparse-atomic-removed | srch | auto-nocaps | one-attempt | 649.9 | 517.7 | -20.33 | 0.08 | -3.80 | improve / improve | +5.10% |
| wild-validator-ipv4-owasp | srch | auto-nocaps | one-attempt | 626.7 | 446.3 | -28.79 | 0.04 | -3.80 | improve / improve | -10.50% |
| winpath-near-miss | srch | auto-caps | one-attempt | 644.9 | 489.0 | -24.18 | 0.43 | -3.80 | improve / improve | -2.20% |
| winpath-near-miss | srch | auto-nocaps | one-attempt | 644.9 | 494.2 | -23.36 | 0.16 | -3.80 | improve / improve | -1.11% |
| wild-datetime-moment-iso8601 | srch | auto-nocaps | one-attempt | 633.8 | 589.3 | -7.01 | 0.11 | -3.80 | improve / improve | +0.05% |
| logparse-atomic-removed | srch | auto-caps | one-attempt | 894.5 | 822.5 | -8.04 | 1.70 | -3.80 | improve / improve | +1.61% |
| logparse-atomic | srch | auto-caps | one-attempt | 830.5 | 843.9 | +1.61 | 0.18 | +11.85 | REGRESS / within | -0.97% |
| logparse-atomic | srch | auto-nocaps | one-attempt | 815.7 | 840.7 | +3.06 | 0.85 | +11.85 | REGRESS / within | +0.24% |
| winpath-near-miss | thr | auto-caps | one-attempt | 23,143.3 | 18.8 | -99.92 | 0.14 | -8.18 | improve / improve | -6.60% |
| winpath-near-miss | thr | auto-nocaps | one-attempt | 23,145.0 | 18.9 | -99.92 | 0.12 | -8.18 | improve / improve | -7.23% |
| email-nested-plus | thr | auto-nocaps | one-attempt | 23,133.8 | 37.1 | -99.84 | 0.10 | -8.18 | improve / improve | +15.91% |
| email-nested-plus | thr | auto-caps | one-attempt | 23,136.1 | 48.1 | -99.79 | 0.10 | -8.18 | improve / improve | +1.65% |
| wild-datetime-moment-iso8601 | thr | auto-nocaps | one-attempt | 36.9 | 18.8 | -49.08 | 0.36 | -29.68 | improve / improve | -4.58% |
| logparse-atomic-removed | thr | auto-nocaps | one-attempt | 35.6 | 18.9 | -46.90 | 0.49 | -29.68 | improve / improve | +0.77% |
| wild-datetime-moment-iso8601 | thr | auto-caps | one-attempt | 49.2 | 32.8 | -33.37 | 1.31 | -29.68 | improve / improve | -0.44% |
| logparse-atomic | thr | auto-caps | one-attempt | 44.4 | 30.1 | -32.21 | 0.36 | -29.68 | improve / improve | +0.35% |
| wild-validator-ipv4-owasp | thr | auto-nocaps | one-attempt | 25.0 | 12.5 | -49.99 | 0.36 | -29.68 | improve / improve | -33.17% |
| logparse-atomic-removed | thr | auto-caps | one-attempt | 43.9 | 30.1 | -31.34 | 0.28 | -29.68 | improve / improve | -0.66% |
| logparse-atomic | thr | auto-nocaps | one-attempt | 43.2 | 30.2 | -30.17 | 0.32 | -29.68 | improve / improve | -6.58% |
| wild-validator-email-owasp | thr | auto-nocaps | one-attempt | 23,119.5 | 38.0 | -99.84 | 0.10 | -8.18 | improve / improve | -2.48% |
| wild-validator-email-owasp | thr | auto-caps | one-attempt | 23,158.8 | 37.0 | -99.84 | 0.12 | -8.18 | improve / improve | -8.51% |
g2_29 IQR: {'improve': 27, 'REGRESS': 2} band: {'improve': 27, 'within': 2}
g2_superset IQR: {'improve': 49, 'REGRESS': 21, 'GIVE-UP': 2} band: {'improve': 43, 'REGRESS': 16, 'GIVE-UP': 2, 'within': 11}

### superset regressions (band)
| pattern | regime | testee | REQ_WHY | b1885a83 ns | 6ef76820 ns | Δ% | IQR% | null edge | verdict (IQR / band) | vs batch-1 BEFORE 25b1984f |
|---|---|---|---|---|---|---|---|---|---|---|
| email-nested-plus | srch | auto-caps | one-attempt | 905.9 | 1,394.5 | +53.93 | 0.06 | +11.85 | REGRESS / REGRESS | -2.90% |
| email-nested-plus | srch | auto-nocaps | one-attempt | 650.0 | 1,000.0 | +53.84 | 1.18 | +11.85 | REGRESS / REGRESS | +2.44% |
| email-nested-plus | srch | vm-caps | one-attempt | 835.1 | GIVE-UP ×5 | — | — | — | **GIVE-UP** | — |
| email-nested-plus | srch | vm-in-caps | one-attempt | 896.5 | GIVE-UP ×5 | — | — | — | **GIVE-UP** | — |
| ipv4-near-miss | thr | vm-caps | one-attempt | 28.4 | 37.3 | +31.19 | 0.06 | +12.51 | REGRESS / REGRESS | -100.00% |
| ipv4-near-miss | thr | vm-in-caps | one-attempt | 34.3 | 42.5 | +23.75 | 0.12 | +12.51 | REGRESS / REGRESS | -100.00% |
| ipv4-near-miss | srch | vm-caps | one-attempt | 893.5 | 1,194.2 | +33.65 | 0.31 | +11.85 | REGRESS / REGRESS | -81.36% |
| ipv4-near-miss | srch | vm-in-caps | one-attempt | 1,135.4 | 1,269.6 | +11.83 | 0.11 | +2.56 | REGRESS / REGRESS | -80.14% |
| uuid-near-miss | srch | vm-caps | one-attempt | 778.4 | 964.7 | +23.92 | 0.36 | +11.85 | REGRESS / REGRESS | -78.34% |
| wild-datetime-moment-iso8601 | srch | auto-caps | one-attempt | 847.3 | 975.0 | +15.07 | 0.20 | +11.85 | REGRESS / REGRESS | -0.58% |
| wild-datetime-moment-iso8601 | srch | vm-caps | one-attempt | 816.9 | 1,390.5 | +70.20 | 0.40 | +11.85 | REGRESS / REGRESS | -78.01% |
| wild-datetime-moment-iso8601 | srch | vm-in-caps | one-attempt | 924.9 | 1,557.6 | +68.41 | 0.43 | +11.85 | REGRESS / REGRESS | -75.26% |
| wild-validator-email-owasp | srch | auto-caps | one-attempt | 663.2 | 1,099.6 | +65.80 | 0.33 | +11.85 | REGRESS / REGRESS | +3.37% |
| wild-validator-email-owasp | srch | auto-nocaps | one-attempt | 662.2 | 1,101.7 | +66.38 | 0.31 | +11.85 | REGRESS / REGRESS | +3.39% |
| wild-validator-email-owasp | srch | vm-caps | one-attempt | 785.7 | 1,405.5 | +78.88 | 0.48 | +11.85 | REGRESS / REGRESS | -78.34% |
| wild-validator-email-owasp | srch | vm-in-caps | one-attempt | 850.2 | 1,465.7 | +72.41 | 0.09 | +11.85 | REGRESS / REGRESS | -77.16% |
| wild-validator-ipv4-owasp | srch | vm-caps | one-attempt | 909.0 | 1,168.7 | +28.57 | 0.22 | +11.85 | REGRESS / REGRESS | -81.84% |
| wild-validator-ipv4-owasp | srch | vm-in-caps | one-attempt | 1,039.4 | 1,438.1 | +38.36 | 0.05 | +2.56 | REGRESS / REGRESS | -78.25% |
