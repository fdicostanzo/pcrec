0000000000003040 <rx_search>:
    3040:	endbr64
    3044:	push   %r13
    3046:	push   %r12
    3048:	mov    %rdx,%r12
    304b:	push   %rbp
    304c:	mov    %rsi,%rbp
    304f:	push   %rbx
    3050:	mov    %rdi,%rbx
    3053:	sub    $0xc48,%rsp
    305a:	mov    %fs:0x28,%r13
    3063:	mov    %r13,0xc38(%rsp)
    306b:	mov    %rcx,%r13
    306e:	lea    0x70(%rsp),%rax
    3073:	mov    %rsp,%r8
    3076:	movq   $0x3f,0x30(%rsp)
    307f:	mov    %rax,0x28(%rsp)
    3084:	lea    0x658(%rsp),%rax
    308c:	mov    %rax,0x38(%rsp)
    3091:	movq   $0x5e,0x40(%rsp)
    309a:	call   2cd0 <rx_search_run>
    309f:	cmp    $0xfffffffd,%eax
    30a2:	je     30c8 <rx_search+0x88>
    30a4:	mov    0xc38(%rsp),%rdx
    30ac:	sub    %fs:0x28,%rdx
    30b5:	jne    30db <rx_search+0x9b>
    30b7:	add    $0xc48,%rsp
    30be:	pop    %rbx
    30bf:	pop    %rbp
    30c0:	pop    %r12
    30c2:	pop    %r13
    30c4:	ret
    30c5:	nopl   (%rax)
    30c8:	mov    %r13,%rcx
    30cb:	mov    %r12,%rdx
    30ce:	mov    %rbp,%rsi
    30d1:	mov    %rbx,%rdi
    30d4:	call   2df0 <rx_search_deep>
    30d9:	jmp    30a4 <rx_search+0x64>
    30db:	call   20b0 <__stack_chk_fail@plt>

