== R-12 VMLAZY timing pair: stream c-default, recipe -O2, 2 patterns, core 13, 7 reps, cc gcc ==
| kind | pattern | regime | parent | normalized | ratio | spread parent | spread normalized | answers |
|---|---|---|---|---|---|---|---|---|
| CONTROL | `'(?=(\\w+?))\\1\\B'` | thr | 14.3125 ns/B | 14.2701 ns/B | 0.997 | 1.078 | 1.035 | same |
| CONTROL | `'(?=(\\w+?))\\1\\B'` | call | 26.7625 ns/call | 26.8593 ns/call | 1.004 | 1.120 | 1.125 | same |
| CONTROL | `'z(a){3,}?c?'` | thr | 0.0180 ns/B | 0.0181 ns/B | 1.007 | 1.153 | 1.133 | same |
| CONTROL | `'z(a){3,}?c?'` | call | 8.3895 ns/call | 8.3426 ns/call | 0.994 | 1.069 | 1.082 | same |
timing: answers agree
== R-12 VMLAZY timing pair: stream c-utf8, recipe -O2, 2 patterns, core 13, 7 reps, cc gcc ==
| kind | pattern | regime | parent | normalized | ratio | spread parent | spread normalized | answers |
|---|---|---|---|---|---|---|---|---|
| CONTROL | `'(a{1,3}?){3,5}'` | thr | 0.1875 ns/B | 0.1874 ns/B | 0.999 | 1.009 | 1.013 | same |
| CONTROL | `'(a{1,3}?){3,5}'` | call | 16.8560 ns/call | 18.0895 ns/call | 1.073 | 1.080 | 1.090 | same |
| CONTROL | `'(a+?)(?1)\\b'` | thr | 0.1877 ns/B | 0.1872 ns/B | 0.998 | 1.012 | 1.007 | same |
| CONTROL | `'(a+?)(?1)\\b'` | call | 19.9049 ns/call | 18.8704 ns/call | 0.948 | 1.124 | 1.089 | same |
timing: answers agree
== R-12 VMLAZY timing pair: stream c-vm, recipe -O2, 3 patterns, core 13, 7 reps, cc gcc ==
| kind | pattern | regime | parent | normalized | ratio | spread parent | spread normalized | answers |
|---|---|---|---|---|---|---|---|---|
| CONTROL | `'[^abc]{2,4}?'` | thr | 3.9754 ns/B | 4.1866 ns/B | 1.053 | 2.063 | 1.071 | same |
| CONTROL | `'[^abc]{2,4}?'` | call | 9.1107 ns/call | 9.8531 ns/call | 1.081 | 1.424 | 1.176 | same |
| CONTROL | `'(?:ab){3,}?c?'` | thr | 0.4895 ns/B | 0.5026 ns/B | 1.027 | 1.084 | 1.125 | same |
| CONTROL | `'(?:ab){3,}?c?'` | call | 14.0343 ns/call | 14.7114 ns/call | 1.048 | 1.097 | 1.061 | same |
| CONTROL | `'\\w{1,3}?\\Ba'` | thr | 9.4538 ns/B | 9.8833 ns/B | 1.045 | 2.560 | 1.152 | same |
| CONTROL | `'\\w{1,3}?\\Ba'` | call | 141.4375 ns/call | 147.4190 ns/call | 1.042 | 1.056 | 2.491 | same |
timing: answers agree
