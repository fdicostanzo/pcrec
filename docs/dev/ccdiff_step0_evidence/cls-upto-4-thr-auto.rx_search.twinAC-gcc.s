00000000000021c0 <rx_search>:
    21c0:	endbr64
    21c4:	mov    %rdi,%r8
    21c7:	mov    %rdx,%rax
    21ca:	mov    %rcx,%rdi
    21cd:	xor    %ecx,%ecx
    21cf:	cmp    %rdx,%rsi
    21d2:	jb     21f3 <rx_search+0x33>
    21d4:	cmp    %rsi,%rdx
    21d7:	jb     2200 <rx_search+0x40>
    21d9:	cmp    $0xffffffffffffffff,%rdx
    21dd:	je     21f3 <rx_search+0x33>
    21df:	mov    %rax,%rdx
    21e2:	test   %rdi,%rdi
    21e5:	je     21ee <rx_search+0x2e>
    21e7:	mov    %rax,(%rdi)
    21ea:	mov    %rdx,0x8(%rdi)
    21ee:	mov    $0x1,%ecx
    21f3:	mov    %ecx,%eax
    21f5:	ret
    21f6:	cs nopw 0x0(%rax,%rax,1)
    2200:	movzbl (%r8,%rdx,1),%edx
    2205:	sub    $0x61,%edx
    2208:	cmp    $0x19,%dl
    220b:	ja     21df <rx_search+0x1f>
    220d:	mov    %rsi,%r9
    2210:	lea    0x4(%rax),%rdx
    2214:	sub    %rax,%r9
    2217:	cmp    $0x4,%r9
    221b:	cmova  %rdx,%rsi
    221f:	lea    0x1(%rax),%rdx
    2223:	cmp    %rsi,%rdx
    2226:	jb     224d <rx_search+0x8d>
    2228:	jmp    22e1 <rx_search+0x121>
    222d:	nopl   0x0(%rax,%rax,1)
    2235:	data16 cs nopw 0x0(%rax,%rax,1)
    2240:	add    $0x1,%rdx
    2244:	cmp    %rsi,%rdx
    2247:	jae    22d0 <rx_search+0x110>
    224d:	movzbl (%r8,%rdx,1),%ecx
    2252:	sub    $0x61,%ecx
    2255:	cmp    $0x19,%cl
    2258:	jbe    2240 <rx_search+0x80>
    225a:	cmp    %rdx,%rax
    225d:	jae    22c0 <rx_search+0x100>
    225f:	movzbl -0x1(%r8,%rdx,1),%esi
    2265:	lea    -0x1(%rdx),%r9
    2269:	lea    -0x61(%rsi),%ecx
    226c:	cmp    $0x19,%cl
    226f:	ja     22c0 <rx_search+0x100>
    2271:	mov    %rdx,%rcx
    2274:	lea    -0x4(%rdx),%rsi
    2278:	sub    %rax,%rcx
    227b:	cmp    $0x4,%rcx
    227f:	cmovbe %rax,%rsi
    2283:	mov    %r9,%rax
    2286:	jmp    22b6 <rx_search+0xf6>
    2288:	xchg   %ax,%ax
    228a:	data16 cs nopw 0x0(%rax,%rax,1)
    2295:	data16 cs nopw 0x0(%rax,%rax,1)
    22a0:	movzbl -0x1(%r8,%rax,1),%ecx
    22a6:	sub    $0x61,%ecx
    22a9:	cmp    $0x19,%cl
    22ac:	ja     21e2 <rx_search+0x22>
    22b2:	sub    $0x1,%rax
    22b6:	cmp    %rax,%rsi
    22b9:	jb     22a0 <rx_search+0xe0>
    22bb:	jmp    21e2 <rx_search+0x22>
    22c0:	mov    %rdx,%rax
    22c3:	jmp    21e2 <rx_search+0x22>
    22c8:	nopl   0x0(%rax,%rax,1)
    22d0:	xor    %ecx,%ecx
    22d2:	cmp    $0xffffffffffffffff,%rdx
    22d6:	je     21f3 <rx_search+0x33>
    22dc:	jmp    225a <rx_search+0x9a>
    22e1:	mov    %rax,%r9
    22e4:	cmp    $0xffffffffffffffff,%rdx
    22e8:	jne    2271 <rx_search+0xb1>
    22ea:	jmp    21f3 <rx_search+0x33>
    22ef:	nop

