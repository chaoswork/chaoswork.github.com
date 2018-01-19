---
author: huangchao
comments: true
date: 2011-05-01 14:49:20+00:00
layout: post
title: 寻找哈密顿回路
categories:
- 学习
- 编程
tags:
- Algorithm
- Hamiltonian

published: true
status: publish
---

前几天做sgu 122，结果官网给挂了，没提交上，今天已提交，竟然过了，哈哈，总结一下在图上找哈密顿回路的方法。

下面引用自wikipedia

“**哈密顿图**（[英语](http://zh.wikipedia.org/wiki/%E8%8B%B1%E8%AF%AD)：Hamiltonian path，或Traceable path）是一个[无向图](http://zh.wikipedia.org/wiki/%E7%84%A1%E5%90%91%E5%9C%96)，由天文学家[哈密顿](http://zh.wikipedia.org/wiki/%E5%93%88%E5%AF%86%E9%A1%BF)提出，由指定的起点前往指定的终点，途中经过所有其他节点且只经过一次。在[图论](http://zh.wikipedia.org/wiki/%E5%9B%BE%E8%AE%BA)中是指含有哈密顿回路的图，闭合的哈密顿路径称作**哈密顿回路**（**Hamiltonian cycle**），含有图中所有顶的路径称作**哈密顿路径**。

美国[图论](http://zh.wikipedia.org/wiki/%E5%9B%BE%E8%AE%BA)[数学家](http://zh.wikipedia.org/wiki/%E6%95%B0%E5%AD%A6%E5%AE%B6)[奥勒](http://zh.wikipedia.org/w/index.php?title=%E5%A5%A5%E5%8B%92&action=edit&redlink=1)在[1960年](http://zh.wikipedia.org/wiki/1960%E5%B9%B4)给出了一个图是哈密尔顿图的[充分条件](http://zh.wikipedia.org/wiki/%E5%85%85%E5%88%86%E6%9D%A1%E4%BB%B6)：对于顶点个数大于2的图，如果图中任意两点度的和大于或等于顶点总数，那这个图一定是哈密尔顿图。 

寻找哈密顿路径是一个典型的[NP-完全](http://zh.wikipedia.org/wiki/NP-%E5%AE%8C%E5%85%A8)问题。后来人们也证明了，找一条哈密顿路的近似比为常数的近似算法也是NP-完全的。 

寻找哈密顿路的确定算法虽然很难有多项式时间的，但是这并不意味着只能进行[时间复杂度](http://zh.wikipedia.org/wiki/%E6%97%B6%E9%97%B4%E5%A4%8D%E6%9D%82%E5%BA%A6)为O(n!*n)暴力搜索。利用[状态压缩动态规划](http://zh.wikipedia.org/w/index.php?title=%E7%8A%B6%E6%80%81%E5%8E%8B%E7%BC%A9%E5%8A%A8%E6%80%81%E8%A7%84%E5%88%92&action=edit&redlink=1)，我们可以将时间复杂度降低到O(2^n*n^3)，具体算法是建立方程`f[i][S][j]`，表示经过了i个节点，节点都是集合S的，到达节点j时的最短路径。每次我们都按照点j所连的节点进行转移。” 

其中Ore性质可以表示为： 

对所有不邻接的不同点对，有`deg(x)+deg(y)>=n` 

《组合数学》书上同时给出了一个满足Ore性质的稠密图的O(V^2)的算法，算法描述如下： 

1）从任意一个顶点开始，在它的两端邻接一个顶点，构造一个越来越长的链，直到不能再长为止。设该链为 

y1-y2-y3-…-ym 

2）检查y1和ym是否邻接。 

> a)如果不邻接则转3),如果邻接，转b）  
> 
> b)如果m=n，则停止构造，并输出链y1-y2-…-ym-y1;否则转c)  
> 
> c)找一个不在链上的顶点z和在链上的顶点yk,满足yk和z邻接，则得到一条m+1的新链  
> 
> z-yk-…ym-y1-y2-…y(k-1) 

3)在链上找出一个yk，满足y1和yk邻接，y(k-1)和ym邻接，则将链转换为y1-…-y(k-1)-ym-…yk,则y1和yk邻接，转b)
