---
layout: post
meta: 
  views: "6"
type: post
tags: 
- Algorithm
- Binary Search

title: 二分查找

published: true
status: publish
---
以前学的时候也没好好研究，只是大概知道思想，昨天写程序的时候发现bug了，十分惭愧，结果在网上发现了这样资料：

>二分查找可以解决（预排序数组的查找）问题：只要数组中包含T（即要查找的值），那么通过不断缩小包含T的范围，最终就可以找到它。一开始，范围覆盖整个数组。将数组的中间项与T进行比较，可以排除一半元素，范围缩小一半。就这样反复比较，反复缩小范围，最终就会在数组中找到T，或者确定原以为T所在的范围实际为空。对于包含N个元素的表，整个查找过程大约要经过log(2)N次比较。 
>多数程序员都觉得只要理解了上面的描述，写出代码就不难了；但事实并非如此。如果你不认同这一点，最好的办法就是放下书本，自己动手写一写。试试吧。 
>我在贝尔实验室和IBM的时候都出过这道考题。那些专业的程序员有几个小时的时间，可以用他们选择的语言把上面的描述写出来；写出高级伪代码也可以。考试结束后，差不多所有程序员都认为自己写出了正确的程序。于是，我们花了半个钟头来看他们编写的代码经过测试用例验证的结果。几次课，一百多人的结果相差无几：90%的程序员写的程序中有bug（我并不认为没有bug的代码就正确）。 
>我很惊讶：在足够的时间内，只有大约10%的专业程序员可以把这个小程序写对。但写不对这个小程序的还不止这些人：高德纳在《计算机程序设计的艺术 第3卷 排序和查找》第6.2.1节的“历史与参考文献”部分指出，虽然早在1946年就有人将二分查找的方法公诸于世，但直到1962年才有人写出没有bug的二分查找程序。 
>			-- 乔恩.本特利，《编程珠玑（第1版）》第35-36页

只有10%的程序员可以写出正确的二分查找程序，看来我还不属于这10%。

当时错误的原因很简单，就是一个小小的bug陷入的死循环：

```c++
int bSearch(vector<int>a,int x)
{
    int l=0,r=a.size()-1;
    int mid=(l+r)/2;
    while(l<r)
    {
        if(a[mid]<x) l=mid;
        else if(a[mid]>x) r=mid;
        else break;
        mid=(l+r)/2;
    }
    return mid;
}
```

乍一看是正确的，但是会陷入死循环，比如一个`vector<int>a`,从大到小存了9个数，设为1到9，现在要找到9的位置，那么执行上述代码时，mid依次为4,6,7,7,7…，陷入死循环。

正确的方法是将第7,8句修改，变成l=mid+1,r=mid-1,当然，这是保证x在a里的时候，如果x有可能不在a中，那么正确而且完整的代码如下(参考《编程珠玑(第二版)》第87页)：

    {% highlight c++ %}
    int bSearch(vector<int>a,int x)
    {
        int l=0,r=a.size()-1;
        int mid;
        for(;;)
        {
            if(l>r) return -1;
            mid=(l+r)/2;
            if(a[mid]<x) l=mid+1;
            else if(a[mid]==x) return mid;
            else if(a[mid]>x) r=mid-1;
        }
        return mid;
    }
    {% endhighlight %}
然后我看到了一道课后题：用二分法返回数组a中出现的第一个x的位置，我是这样想的：

在上面的基础上进行改进，如果已经搜到x的一个位置，那么如果x的前一个位置比x小，则意味着第一个x已经找到，如果前一个位置也是x，那么将r修改为mid-1;需要注意的是，如果mid==0，则直接判断mid是否是x即可，代码如下：

    {% highlight c++ %}
    int bSearch2(vector<int>a,int x)
    {
        int l=0,r=a.size()-1;
        int mid;
        for(;;)
        {
            if(l>r) return -1;
            mid=(l+r)/2;
            if(mid==0)
            {
                if(a[mid]==x) return mid;
                else return -1;
            }    
            if(a[mid]<x) l=mid+1;
            else if(a[mid]==x)
            {
                if(a[mid-1]<x) return mid;
                else r=mid-1;
            }
            else if(a[mid]>x) r=mid-1;
        }
        return mid;
    }
    {% endhighlight %}
但是看了《编程珠玑(第二版)》的答案后，发现答案的方法比我的思路还有效率都清晰多了：

初始的循环不变式是：`a[l]<x && a[r]>=x && l<r`,代码如下：

    {% highlight c++ %}
    int bSearch3(vector<int>a,int x)
    {
        int l=-1,r=a.size();
        int mid;
        while(l+1!=r)
        {
            mid=(l+r)/2;
            if(a[mid]<x) l=mid;
            else r=mid;
        }
        if(r>=a.size() || a[r]!=x) return -1;
        return r;
    }
    {% endhighlight %}
一般的程序用这个就已经很好了，因为相比于bSearch2，bSearch3每次迭代只比较一次。

当然，书中还提到了进一步的优化，最终将结合搜索数组的大小，将循环展开，这样可以借助于现在计算机的流水线处理技术来增加指令集的并行，从而进一步的优化，不过一般情况下bSearch3的表现就已经相当出色，而且更容易编写和实现。

    {% highlight c++ %}
    int bSearch4(vector<int>a,int x)
    {
        int l=-1;
        if(a[512]<x) l=1000-512;
        if(a[l+256]<x) l+=256;
        if(a[l+128]<x) l+=128;
        if(a[l+64]<x) l+=64;
        if(a[l+32]<x) l+=32;
        if(a[l+16]<x) l+=16;
        if(a[l+8]<x) l+=8;
        if(a[l+4]<x) l+=4;
        if(a[l+2]<x) l+=2;
        if(a[l+1]<x) l+=1;
     
        int p=l+1;
        if(p>1000 || a[p]!=x) p=-1;
        return p;
    }
    {% endhighlight %}
这是一个1000个数据的二分查找的优化。
