00000000000021c0 <rx_search>:
    21c0:	endbr64
    21c4:	xor    %eax,%eax
    21c6:	cmp    %rdx,%rsi
    21c9:	jb     2380 <rx_search+0x1c0>
    21cf:	push   %r12
    21d1:	mov    %rcx,%r11
    21d4:	mov    %rdx,%r8
    21d7:	mov    %rdx,%rax
    21da:	push   %rbp
    21db:	mov    %rdx,%r9
    21de:	xor    %ecx,%ecx
    21e0:	lea    0x1101(%rip),%r10        # 32e8 <rx_forward_next_state.6>
    21e7:	push   %rbx
    21e8:	lea    0x1211(%rip),%rbp        # 3400 <rx_forward_is_accepting.8>
    21ef:	lea    0x110a(%rip),%rbx        # 3300 <rx_forward_byte_class.7>
    21f6:	jmp    2234 <rx_search+0x74>
    21f8:	nopl   0x0(%rax,%rax,1)
    2200:	movzbl (%rdi,%rax,1),%edx
    2204:	lea    -0x61(%rdx),%r12d
    2208:	cmp    $0x19,%r12b
    220c:	jbe    22d0 <rx_search+0x110>
    2212:	movzbl (%rbx,%rdx,1),%edx
    2216:	add    %ecx,%edx
    2218:	mov    %edx,%edx
    221a:	movzwl (%r10,%rdx,2),%ecx
    221f:	cmp    $0xffff,%ecx
    2225:	je     2241 <rx_search+0x81>
    2227:	add    $0x1,%rax
    222b:	cmpb   $0x0,0x0(%rbp,%rcx,1)
    2230:	cmovne %rax,%r9
    2234:	test   %ecx,%ecx
    2236:	jne    230c <rx_search+0x14c>
    223c:	cmp    %rsi,%rax
    223f:	jb     2200 <rx_search+0x40>
    2241:	xor    %eax,%eax
    2243:	cmp    $0xffffffffffffffff,%r9
    2247:	je     22ca <rx_search+0x10a>
    224d:	mov    %r9,%rax
    2250:	mov    %r9,%rdx
    2253:	lea    0xf86(%rip),%rbx        # 31e0 <rx_reverse_byte_class.4>
    225a:	xor    %esi,%esi
    225c:	lea    0xf65(%rip),%r10        # 31c8 <rx_reverse_next_state.3>
    2263:	lea    0x1076(%rip),%rbp        # 32e0 <rx_reverse_is_accepting.5>
    226a:	jmp    22a4 <rx_search+0xe4>
    226c:	nopl   0x0(%rax)
    2270:	sub    $0x1,%rax
    2274:	movzbl (%rdi,%rax,1),%ecx
    2278:	lea    -0x61(%rcx),%r12d
    227c:	cmp    $0x19,%r12b
    2280:	jbe    2320 <rx_search+0x160>
    2286:	movzbl (%rbx,%rcx,1),%ecx
    228a:	add    %esi,%ecx
    228c:	mov    %ecx,%ecx
    228e:	movzwl (%r10,%rcx,2),%esi
    2293:	cmp    $0xffff,%esi
    2299:	je     22b1 <rx_search+0xf1>
    229b:	cmpb   $0x0,0x0(%rbp,%rsi,1)
    22a0:	cmovne %rax,%rdx
    22a4:	test   %esi,%esi
    22a6:	jne    2358 <rx_search+0x198>
    22ac:	cmp    %rax,%r8
    22af:	jb     2270 <rx_search+0xb0>
    22b1:	xor    %eax,%eax
    22b3:	cmp    $0xffffffffffffffff,%rdx
    22b7:	je     22ca <rx_search+0x10a>
    22b9:	test   %r11,%r11
    22bc:	je     22c5 <rx_search+0x105>
    22be:	mov    %rdx,(%r11)
    22c1:	mov    %r9,0x8(%r11)
    22c5:	mov    $0x1,%eax
    22ca:	pop    %rbx
    22cb:	pop    %rbp
    22cc:	pop    %r12
    22ce:	ret
    22cf:	nop
    22d0:	add    $0x1,%rax
    22d4:	cmp    %rsi,%rax
    22d7:	jae    239b <rx_search+0x1db>
    22dd:	mov    $0x1,%ecx
    22e2:	jmp    22fb <rx_search+0x13b>
    22e4:	nopl   0x0(%rax)
    22e8:	add    $0x1,%rax
    22ec:	add    $0x1,%rcx
    22f0:	cmp    %rsi,%rax
    22f3:	jae    2370 <rx_search+0x1b0>
    22f5:	cmp    $0x4,%rcx
    22f9:	je     2370 <rx_search+0x1b0>
    22fb:	movzbl (%rdi,%rax,1),%edx
    22ff:	sub    $0x61,%edx
    2302:	cmp    $0x19,%dl
    2305:	jbe    22e8 <rx_search+0x128>
    2307:	xor    %ecx,%ecx
    2309:	mov    %rax,%r9
    230c:	cmp    %rsi,%rax
    230f:	jae    2241 <rx_search+0x81>
    2315:	movzbl (%rdi,%rax,1),%edx
    2319:	jmp    2212 <rx_search+0x52>
    231e:	xchg   %ax,%ax
    2320:	cmp    %rax,%r8
    2323:	jae    23a3 <rx_search+0x1e3>
    2325:	mov    $0x1,%esi
    232a:	jmp    233f <rx_search+0x17f>
    232c:	nopl   0x0(%rax)
    2330:	add    $0x1,%rsi
    2334:	cmp    %rax,%r8
    2337:	jae    2388 <rx_search+0x1c8>
    2339:	cmp    $0x4,%rsi
    233d:	je     2388 <rx_search+0x1c8>
    233f:	mov    %rax,%rdx
    2342:	lea    -0x1(%rax),%rax
    2346:	movzbl -0x1(%rdi,%rdx,1),%ecx
    234b:	sub    $0x61,%ecx
    234e:	cmp    $0x19,%cl
    2351:	jbe    2330 <rx_search+0x170>
    2353:	xor    %esi,%esi
    2355:	mov    %rdx,%rax
    2358:	cmp    %rax,%r8
    235b:	jae    22b1 <rx_search+0xf1>
    2361:	sub    $0x1,%rax
    2365:	movzbl (%rdi,%rax,1),%ecx
    2369:	jmp    2286 <rx_search+0xc6>
    236e:	xchg   %ax,%ax
    2370:	cmp    $0x4,%rcx
    2374:	sete   %cl
    2377:	movzbl %cl,%ecx
    237a:	add    %ecx,%ecx
    237c:	jmp    2309 <rx_search+0x149>
    237e:	xchg   %ax,%ax
    2380:	ret
    2381:	nopl   0x0(%rax)
    2388:	cmp    $0x4,%rsi
    238c:	mov    %rax,%rdx
    238f:	sete   %sil
    2393:	movzbl %sil,%esi
    2397:	add    %esi,%esi
    2399:	jmp    2355 <rx_search+0x195>
    239b:	mov    %rax,%r9
    239e:	jmp    2241 <rx_search+0x81>
    23a3:	mov    %rax,%rdx
    23a6:	jmp    22b1 <rx_search+0xf1>
    23ab:	nopl   0x0(%rax,%rax,1)

