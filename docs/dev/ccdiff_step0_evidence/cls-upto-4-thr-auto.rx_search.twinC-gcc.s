00000000000021c0 <rx_search>:
    21c0:	endbr64
    21c4:	xor    %eax,%eax
    21c6:	cmp    %rdx,%rsi
    21c9:	jb     23a8 <rx_search+0x1e8>
    21cf:	push   %r12
    21d1:	mov    %rsi,%r8
    21d4:	mov    %rcx,%r11
    21d7:	mov    %rdx,%r9
    21da:	push   %rbp
    21db:	mov    %rdx,%rcx
    21de:	xor    %esi,%esi
    21e0:	lea    0x1101(%rip),%r10        # 32e8 <rx_forward_next_state.6>
    21e7:	push   %rbx
    21e8:	lea    0x1211(%rip),%rbp        # 3400 <rx_forward_is_accepting.8>
    21ef:	lea    0x110a(%rip),%rbx        # 3300 <rx_forward_byte_class.7>
    21f6:	jmp    2234 <rx_search+0x74>
    21f8:	nopl   0x0(%rax,%rax,1)
    2200:	movzbl (%rdi,%rcx,1),%eax
    2204:	lea    -0x61(%rax),%r12d
    2208:	cmp    $0x19,%r12b
    220c:	jbe    22e0 <rx_search+0x120>
    2212:	movzbl (%rbx,%rax,1),%eax
    2216:	add    %esi,%eax
    2218:	mov    %eax,%eax
    221a:	movzwl (%r10,%rax,2),%esi
    221f:	cmp    $0xffff,%esi
    2225:	je     2241 <rx_search+0x81>
    2227:	add    $0x1,%rcx
    222b:	cmpb   $0x0,0x0(%rbp,%rsi,1)
    2230:	cmovne %rcx,%rdx
    2234:	test   %esi,%esi
    2236:	jne    232d <rx_search+0x16d>
    223c:	cmp    %r8,%rcx
    223f:	jb     2200 <rx_search+0x40>
    2241:	xor    %eax,%eax
    2243:	cmp    $0xffffffffffffffff,%rdx
    2247:	je     22d2 <rx_search+0x112>
    224d:	mov    %rdx,%rax
    2250:	mov    %rdx,%rbp
    2253:	lea    0xf86(%rip),%r10        # 31e0 <rx_reverse_byte_class.4>
    225a:	xor    %esi,%esi
    225c:	lea    0xf65(%rip),%r8        # 31c8 <rx_reverse_next_state.3>
    2263:	lea    0x1076(%rip),%rbx        # 32e0 <rx_reverse_is_accepting.5>
    226a:	jmp    22ac <rx_search+0xec>
    226c:	nopl   0x0(%rax)
    2270:	movzbl -0x1(%rdi,%rax,1),%r12d
    2276:	lea    -0x1(%rax),%rcx
    227a:	lea    -0x61(%r12),%esi
    227f:	cmp    $0x19,%sil
    2283:	jbe    2340 <rx_search+0x180>
    2289:	mov    %rcx,%rax
    228c:	xor    %esi,%esi
    228e:	movzbl (%r10,%r12,1),%ecx
    2293:	add    %esi,%ecx
    2295:	mov    %ecx,%ecx
    2297:	movzwl (%r8,%rcx,2),%esi
    229c:	cmp    $0xffff,%esi
    22a2:	je     22b9 <rx_search+0xf9>
    22a4:	cmpb   $0x0,(%rbx,%rsi,1)
    22a8:	cmovne %rax,%rbp
    22ac:	test   %esi,%esi
    22ae:	jne    238c <rx_search+0x1cc>
    22b4:	cmp    %rax,%r9
    22b7:	jb     2270 <rx_search+0xb0>
    22b9:	xor    %eax,%eax
    22bb:	cmp    $0xffffffffffffffff,%rbp
    22bf:	je     22d2 <rx_search+0x112>
    22c1:	test   %r11,%r11
    22c4:	je     22cd <rx_search+0x10d>
    22c6:	mov    %rbp,(%r11)
    22c9:	mov    %rdx,0x8(%r11)
    22cd:	mov    $0x1,%eax
    22d2:	pop    %rbx
    22d3:	pop    %rbp
    22d4:	pop    %r12
    22d6:	ret
    22d7:	nopw   0x0(%rax,%rax,1)
    22e0:	mov    %r8,%rax
    22e3:	lea    0x4(%rcx),%r12
    22e7:	sub    %rcx,%rax
    22ea:	cmp    $0x4,%rax
    22ee:	lea    0x1(%rcx),%rax
    22f2:	cmovbe %r8,%r12
    22f6:	cmp    %r12,%rax
    22f9:	jb     2309 <rx_search+0x149>
    22fb:	jmp    2327 <rx_search+0x167>
    22fd:	nopl   (%rax)
    2300:	add    $0x1,%rax
    2304:	cmp    %r12,%rax
    2307:	jae    2315 <rx_search+0x155>
    2309:	movzbl (%rdi,%rax,1),%edx
    230d:	sub    $0x61,%edx
    2310:	cmp    $0x19,%dl
    2313:	jbe    2300 <rx_search+0x140>
    2315:	mov    %rax,%rdx
    2318:	xor    %esi,%esi
    231a:	sub    %rcx,%rdx
    231d:	cmp    $0x4,%rdx
    2321:	sete   %sil
    2325:	add    %esi,%esi
    2327:	mov    %rax,%rcx
    232a:	mov    %rax,%rdx
    232d:	cmp    %r8,%rcx
    2330:	jae    2241 <rx_search+0x81>
    2336:	movzbl (%rdi,%rcx,1),%eax
    233a:	jmp    2212 <rx_search+0x52>
    233f:	nop
    2340:	mov    %rax,%rsi
    2343:	lea    -0x4(%rax),%rbp
    2347:	sub    %r9,%rsi
    234a:	cmp    $0x4,%rsi
    234e:	cmovbe %r9,%rbp
    2352:	jmp    2372 <rx_search+0x1b2>
    2354:	nop
    2355:	data16 cs nopw 0x0(%rax,%rax,1)
    2360:	movzbl -0x1(%rdi,%rcx,1),%esi
    2365:	sub    $0x61,%esi
    2368:	cmp    $0x19,%sil
    236c:	ja     2377 <rx_search+0x1b7>
    236e:	sub    $0x1,%rcx
    2372:	cmp    %rcx,%rbp
    2375:	jb     2360 <rx_search+0x1a0>
    2377:	sub    %rcx,%rax
    237a:	xor    %esi,%esi
    237c:	mov    %rcx,%rbp
    237f:	cmp    $0x4,%rax
    2383:	mov    %rcx,%rax
    2386:	sete   %sil
    238a:	add    %esi,%esi
    238c:	cmp    %rax,%r9
    238f:	jae    22b9 <rx_search+0xf9>
    2395:	sub    $0x1,%rax
    2399:	movzbl (%rdi,%rax,1),%r12d
    239e:	jmp    228e <rx_search+0xce>
    23a3:	nopl   0x0(%rax,%rax,1)
    23a8:	ret
    23a9:	nopl   0x0(%rax)

