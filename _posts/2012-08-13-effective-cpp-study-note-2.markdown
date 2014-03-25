---
author: huangchao
comments: true
date: 2012-08-13 15:52:47+00:00
layout: post

tags:
- C++

title: Effective C++ 笔记2

published: true
status: publish
---

#条款2：尽量以const, enum, inline替换#define

define只是简单的替换，就是因为太简单，程序员考虑的可就要多了。

比如我来一段这样的代码：

![image](/images/effectivecpp/truefalse.jpg)

直觉上觉得应该是编译不通过吧，可是：

![image](/images/effectivecpp/run.jpg)

如果有个坏蛋把这一条加到某个头文件中，估计找bug也会找晕吧。

还有，如果2个文件中都有宏定义，而且名字重复了，这样的情况也是可能存在的。

用const还有一个好处，就是const的变量在程序里只有一份拷贝，而define则会产生多份拷贝，算是程序的一个小优化。

不过define还有const做不到的事，其一就是宏函数，但是宏函数也有一些缺陷，

    {% highlight c++ %}
    #define CALL_WITH_MAX(a,b)  f((a)>(b)?(a):(b))
    int a = 5, b = 0;
    CALL_WITH_MAX(++a, b);
    CALL_WITH_MAX(++a,b+10);
    {% endhighlight %}

这些都是不良代码，足以体现出define的缺陷。所以书中建议用const来代替#define.并借助inline在保证效率的同时解决上述宏函数的问题。

至此，似乎define一无是处，那为什么不废除define，说是为了兼容c代码似乎有些说不过去，因为C99里面const也是关键字之一了。

我觉得define还有const做不到的事，这源自于define的处理是在编译期间的预处理阶段，所以可以作为编译开关，最常用的：

    {% highlight c++ %}
    #ifndef XXX_H
    #define XXX_H
    #endif
    {% endhighlight %}

还有就是define的用法里面一直有##和#,这2个符号我几乎没有用过，只是在某些地方看到过，简单来说，##用来拼接，而#则是将其变为字符串。比如：

    {% highlight c++ %}
    #define A(n) A##n，那么A(1)就是A1，A(2)就是A2,ABC(def)就是ABCdef,依然是简单的替换。
    #define A(n) #n，则A(1+2)则是"1+2"
    {% endhighlight %}

![image](/images/effectivecpp/define.jpg)

有个想法，以前在指定函数指针的时候，总感觉不能按照规律来调用某个函数，现在能否借助define的##来实现不同函数指针的调用呢？

比如我:

    {% highlight c++ %}
    #define FUN fun##x
    case x:call(FUN(x));//实现情况2则调用fun_x这个函数。
    {% endhighlight %}

有待于进一步验证，今天太晚了，明天再去公司试试。

严格来说，define和const根本就是2个不同的东西，只不过实现的功能有部分的类似，不过对于变量的定义来说，最好用const，因为const更健壮。

最后，总结一下类中成员变量的初始化问题：

const 变量只能在构造函数的初始化列表中初始化。

static 变量只能在类外部初始化，只有一种例外，static const int类型可以在类中初始化。

除上述的变量外，其余变量都应该在类的构造函数中初始化，除非你不想初始化，而是在某个函数中第一次用的时候赋值，当然，这不是一种好的编程习惯。
