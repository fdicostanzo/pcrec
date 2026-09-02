00000000000021c0 <rx_search>:
    21c0:	endbr64
    21c4:	mov    %rdi,%r8
    21c7:	mov    %rcx,%r9
    21ca:	mov    %rsi,%rdi
    21cd:	xor    %ecx,%ecx
    21cf:	cmp    %rdx,%rsi
    21d2:	jb     21f3 <rx_search+0x33>
    21d4:	cmp    %rsi,%rdx
    21d7:	jb     2200 <rx_search+0x40>
    21d9:	cmp    $0xffffffffffffffff,%rdx
    21dd:	je     21f3 <rx_search+0x33>
    21df:	mov    %rdx,%rax
    21e2:	test   %r9,%r9
    21e5:	je     21ee <rx_search+0x2e>
    21e7:	mov    %rdx,(%r9)
    21ea:	mov    %rax,0x8(%r9)
    21ee:	mov    $0x1,%ecx
    21f3:	mov    %ecx,%eax
    21f5:	ret
    21f6:	cs nopw 0x0(%rax,%rax,1)
    2200:	movzbl (%r8,%rdx,1),%eax
    2205:	sub    $0x61,%eax
    2208:	cmp    $0x19,%al
    220a:	ja     21df <rx_search+0x1f>
    220c:	lea    0x1(%rdx),%rax
    2210:	mov    $0x1,%esi
    2215:	cmp    %rdi,%rax
    2218:	jb     2233 <rx_search+0x73>
    221a:	jmp    22a8 <rx_search+0xe8>
    221f:	nop
    2220:	add    $0x1,%rax
    2224:	add    $0x1,%rsi
    2228:	cmp    %rdi,%rax
    222b:	jae    2290 <rx_search+0xd0>
    222d:	cmp    $0x4,%rsi
    2231:	je     2290 <rx_search+0xd0>
    2233:	movzbl (%r8,%rax,1),%ecx
    2238:	sub    $0x61,%ecx
    223b:	cmp    $0x19,%cl
    223e:	jbe    2220 <rx_search+0x60>
    2240:	cmp    %rax,%rdx
    2243:	jae    2258 <rx_search+0x98>
    2245:	movzbl -0x1(%r8,%rax,1),%edi
    224b:	lea    -0x1(%rax),%rcx
    224f:	lea    -0x61(%rdi),%esi
    2252:	cmp    $0x19,%sil
    2256:	jbe    226c <rx_search+0xac>
    2258:	mov    %rax,%rdx
    225b:	jmp    21e2 <rx_search+0x22>
    225d:	nopl   (%rax)
    2260:	mov    %rax,%rsi
    2263:	sub    %rcx,%rsi
    2266:	cmp    $0x4,%rsi
    226a:	je     22a0 <rx_search+0xe0>
    226c:	cmp    %rcx,%rdx
    226f:	jae    22a0 <rx_search+0xe0>
    2271:	mov    %rcx,%rdi
    2274:	sub    $0x1,%rcx
    2278:	movzbl (%r8,%rcx,1),%esi
    227d:	sub    $0x61,%esi
    2280:	cmp    $0x19,%sil
    2284:	jbe    2260 <rx_search+0xa0>
    2286:	mov    %rdi,%rdx
    2289:	jmp    21e2 <rx_search+0x22>
    228e:	xchg   %ax,%ax
    2290:	xor    %ecx,%ecx
    2292:	cmp    $0xffffffffffffffff,%rax
    2296:	je     21f3 <rx_search+0x33>
    229c:	jmp    2240 <rx_search+0x80>
    229e:	xchg   %ax,%ax
    22a0:	mov    %rcx,%rdx
    22a3:	jmp    21e2 <rx_search+0x22>
    22a8:	cmp    $0xffffffffffffffff,%rax
    22ac:	jne    21e2 <rx_search+0x22>
    22b2:	jmp    21f3 <rx_search+0x33>
    22b7:	nopw   0x0(%rax,%rax,1)

