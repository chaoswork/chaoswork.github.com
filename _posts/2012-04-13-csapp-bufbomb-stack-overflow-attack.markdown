---
author: huangchao
date: 2012-04-13 14:17:13+00:00
layout: post
title: CS:APP bufbomb 缓冲区溢出攻击
categories:
- 学习
- 编程
tags:
- bufbomb
- csapp
- stack overflow attack

published: true
status: publish
---

要攻击的程序源代码:

[http://csapp.cs.cmu.edu/public/1e/ics/code/asm/bufbomb.c](http://csapp.cs.cmu.edu/public/1e/ics/code/asm/bufbomb.c)

目标是输入特定的字符，让程序最终输出0xdeadbeef.

需要注意的是该程序接受数据是字符的16进制编码，比如你如果想让getbuf函数中的buf中的内容变成“0123”，那么你要输入30 31 32 33.

以前听到这个缓冲区溢出攻击这个词总觉得高深莫测，那是黑客的本领，最近在看CS:APP发现上面就有缓冲区溢出的实验,从这本书的名字可以看出，就是让你知道计算机底层都在干什么，推荐每个写程序的人都看一下。

    {% highlight c++ %}
    
    /* $begin getbuf-c */
    int getbuf()
    {
        char buf[12];
        getxs(buf);
        return 1;
    }
    
    void test()
    {
      int val;
      printf("Type Hex string:");
      val = getbuf();
      printf("getbuf returned 0x%x\n", val);
    }
    {% endhighlight %}


上面的代码可以看出，val的值应该是总是为1的，所以输出总是1，现在就是让你写入特定的字符，让其输出为0xdeadbeef.这个实验只是简单介绍了缓冲区溢出攻击的原理，但是随着编译器的发展，这个实验也越来越难做了。目前我只能做到禁用gcc的堆栈保护，而且只在gdb中成功，真实运行的时候虽然成功的输出了0xdeadbeef，但是程序结束后总是伴随着段错误。这里记录一下学习的过程，我觉得这个实验还有改进的余地，只是目前对编译器以及汇编的掌握还不够熟练。

这个程序的缓冲区溢出攻击是十分依赖于机器的，编译器的版本，系统内核的版本等等因素都会导致生成的可执行文件不同，所以这个实验需要了解程序的机器级表示的相关知识，也就是CS:APP的第3章的内容，windows版本的攻击应该是更为简单的，目前我还没有听到windows有类似linux的Exec Shield Overflow Protection.

可以说，通过这次实验的学习，发现了很多对程序运行过程的误解，操作系统学的真烂=.=

首先，一个进程是怎么在内存里布局的？强烈建议读一下这篇blog:[http://duartes.org/gustavo/blog/post/anatomy-of-a-program-in-memory](http://duartes.org/gustavo/blog/post/anatomy-of-a-program-in-memory),在现代的操作系统中，每个进程都运行在自己的虚拟地址空间中，类似一个沙盒，让每一个进程都感觉自己运行在一个4G的内存空间中，当然这只是给进程以及用户的一种幻觉，实际上每个进程的虚拟地址空间都会被分页机制映射到物理地址的页或者虚拟内存的页，虚拟内存就是当内存不够时用硬盘充当一部份内存使用，比如linux的swap分区。

下面仅以linux说明可执行文件的运行过程。

其中，在0-0xFFFFFFFF的虚拟地址空间中，高地址的1G(0xC0000000-0xFFFFFFFF)范围被linux用作内核空间，用户空间是低的3G范围。如下图所示(来自上面链接的文章)：

![image](/images/csapp/linuxFlexibleAddressSpaceLayout.png)

这里吗可以看出中间有许多random offset，这也加大了缓冲区溢出攻击的难度，其中栈区是有固定大小的，可以输入ulimit -s来确定，我的机子返回的是8192，也就是8M的空间，当你写了一个无限递归的函数时，这个空间就会很快被填满，然后导致stack overflow,堆区理论上可以一直向上申请到Memory Mapping Segment,不过一般没有程序会使用这么大的内存。

这里我很好奇的是0x08048000这个数是怎么来的，Google了一下，好像都没有说明，不知道有没有什么历史。不过这个数是作为linux应用程序的起始地址。但是如果用objdump反汇编一个程序，会发现程序的文本段，比如main函数的位置并不是从0x08048000开始的，这是因为0x08048000首先存放的是ELF header，包含了这个程序的信息。

每个进程的虚拟内存布局可以通过查看/proc/pid/maps这个文件来查看，其中pid换成想要查看的进程编号，比如实验的./bufbomb布局如下：

![image](/images/csapp/part_017.png)

这里可以看到0x08048000以下的地址被用来映射许多动态链接库，比如libc和ld，这和上图的布局有些出入，估计是因为linux的内核升级，将memory mapping segment存放到了0x08048000下面？以前最下面的空白区是不做任何用途的。

缓冲区溢出攻击只是针对程序的栈这一部分，在栈里面会存放程序运行的栈帧，因为当一个函数调用另一个函数时，要将当前运行的信息保存起来(相当于入栈)，然后再跳转到另一个函数的地址执行，执行完后要回到调用这个函数的下一条指令接着执行，然后就将保存的信息取出(相当于出栈)，入栈出栈的操作是通过ebp寄存器和esp寄存器来完成的。这两个寄存器都指向栈区，可以这么理解，ebp指向某个过程的基地址，esp指向某个过程的栈顶，这里的某个过程通常来说就是指函数。ebp和esp之间，就是某个过程(函数)运行需要的所有数据。

拿上述的bufbomb.c来说，用gcc 将其编译为可执行文件:

    
    $gcc bufbomb.c -o bufbomb -fno-stack-protector


之所以加上后面的-fno-stack-protector是为了禁用gcc的堆栈保护。

然后用objdump将bufbomb反汇编

    
    $objdump -d bufbomb


然后可以得到bufbomb的代码如下，只取test函数和getbuf函数的：

    
    08048532 <getbuf>:
    8048532: 55                  push %ebp
    8048533: 89 e5               mov %esp,%ebp
    8048535: 83 ec 28            sub $0x28,%esp
    8048538: 8d 45 ec            lea -0x14(%ebp),%eax
    804853b: 89 04 24            mov %eax,(%esp)
    804853e: e8 21 ff ff ff      call 8048464 <getxs>
    8048543: b8 01 00 00 00      mov $0x1,%eax
    8048548: c9 leave
    8048549: c3 ret
    
    0804854a <test>:
    804854a: 55                  push %ebp
    804854b: 89 e5               mov %esp,%ebp
    804854d: 83 ec 28            sub $0x28,%esp
    8048550: b8 c0 86 04 08      mov $0x80486c0,%eax
    8048555: 89 04 24            mov %eax,(%esp)
    8048558: e8 03 fe ff ff      call 8048360 <printf@plt>
    804855d: e8 d0 ff ff ff      call 8048532 <getbuf>
    8048562: 89 45 f4            mov %eax,-0xc(%ebp)
    8048565: b8 d1 86 04 08      mov $0x80486d1,%eax   #printf args 0
    804856a: 8b 55 f4            mov -0xc(%ebp),%edx
    804856d: 89 54 24 04         mov %edx,0x4(%esp)
    8048571: 89 04 24            mov %eax,(%esp)
    8048574: e8 e7 fd ff ff      call 8048360 <printf@plt>
    8048579: c9                  leave
    804857a: c3                  ret


然后通过gdb调试可以得到下面的栈帧图,我保存在了google doc里面：

![image](/images/csapp/part_020.png)

左边绿色的部分是test函数的栈帧，黄色的部分是getbuf函数的栈帧，蓝色部分是下面的栈帧执行完后要跳转到的指令地址，这个地址每次call的时候自动填充，所以理论上应该是属于上衣个栈帧的内容，这里由于返回后的esp并没有指向这个返回地址，所以没有将其包含进栈帧。目前我明确的参数都有所注释，还有许多地址中的数据我还不明白其中的含义，所以这里还值得研究一下。目前该图含有的信息:

一个函数执行完成后要跳转到的地址(由ret指令来完成)，比如getbuf函数的栈帧(黄色区域),其执行完后eip的地址即为0x08048562。

printf的参数放在第27,28行，分别表示printf的第0个参数,第一个参数是1，因为最后printf只会打印一个1出来，第0个参数则是字符串的地址，用gdb可以获得其数据：

![image](/images/csapp/part_021.png)

需要注意的是栈帧图中的28行为0x080486c0,而不是上面gdb调试中的0x080486d1,是因为0x080486c0是第一次printf的参数，也就是打印"Type Hex String:"字符串的地址，而0x080486d1才是第二个printf的字符串地址。这个地址怎么得到的？可以通过gdb单指令调试，其实汇编语言中就有，见上文汇编代码中注释的那一行。

现在我们的目标是让test中的第二个printf输出0xdeadbeef，而不是程序中默认的1。

首先，buf数组开的大小有12，但是系统并不检查边界(现在的gcc版本可能会有相关的处理机制),所以我们可以一直写，写多了，就把高地址的数据覆盖了。我们的目标至少要覆盖到printf的第二个参数，也就是上面栈帧图中红色的区域，当然上面多了一行，只是为了演示如果我们想，完全可以把整个栈都覆盖掉。

现在的关键就是要写入什么数据，随便写肯定程序的eip都不知道运行到那去了。

首先要保证第30行的数据不变，因为这里保存了函数返回后test的ebp。

然后我们要绕过给val赋值为1，并用printf输出这一块，可以让getbuf返回后直接执行printf,所以要让eip直接返回到printf函数的指令，即将第29行的数据写为0x08048574，看上面的汇编代码可以知道，这里存放的就是printf的指令。

现在可以直接执行printf了，剩下的就是设置参数了，第0个参数设置为0x080486d1,原因上文已经说过了，第1个参数就是输出的内容,应该是0xdeadbeef.

ok,这就是我们需要注意的所有地方，至于从31到35行要填入什么数据就随意了，需要注意的是，由于一次填写2个字符，所以要将上述必须填的顺序逆序的输入，比如你想存0x12345678,输入的时候应该是78 56 34 12 。

这样，就完成了一次缓冲区溢出攻击:)

![image](/images/csapp/deafbeef2.png)

但是，不再gdb下运行的时候，虽然也返回了0xdeadbeef,但是总是伴随着段错误。

![image](images/csapp/part_023.png)



应该还是有改进的空间，下一步可以尝试在stack protector下的溢出攻击。
