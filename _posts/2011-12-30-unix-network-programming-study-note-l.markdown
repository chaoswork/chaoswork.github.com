---
author: huangchao
date: 2011-12-30 08:17:44+00:00
layout: post
title: Unix Network Programming 读书笔记1:daytimetcp注解
categories:
- 学习
- 编程
tags:
- Network
- Socket
- Unix
- UNP

published: true
status: publish
---

最近在看Stevens大师的《Unix Network Programming：V1》.虽然已经写的十分清晰，但是有些地方对于我这样的新手还是很吃力，可能第一章只是进行介绍，详细讲解在后面。  
下面是我第一章的学习笔记。  
环境编译：  
由于本书已经有第三版，所以我到网上下载了第三版的源码，README已经写的很清楚了，整个编译过程轻松加愉快。其实主要是为了生成libunp.a这个库文件。  
简单的时间客户端代码  
daytimetcpcli.c  

{% highlight c++ %}
#include "unp.h"
int main(int argc, char **argv)
{
    int sockfd, n;
    char recvline[MAXLINE + 1];
    struct sockaddr_in servaddr;
    if (argc != 2)
        err_quit("usage: a.out <IPaddress>");
    if ( (sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
        err_sys("socket error");
    bzero(&servaddr, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(13); /* daytime server */
    if (inet_pton(AF_INET, argv[1], &servaddr.sin_addr) <= 0)
        err_quit("inet_pton error for %s", argv[1]);
    if (connect(sockfd, (SA *) &servaddr, sizeof(servaddr)) < 0)
        err_sys("connect error");
    while ( (n = read(sockfd, recvline, MAXLINE)) > 0) {
        recvline[n] = 0; /* null terminate */
        if (fputs(recvline, stdout) == EOF)
            err_sys("fputs error");
    }
    if (n < 0)
        err_sys("read error");
    exit(0);
}    

{% endhighlight %}

  
只有27行，麻雀虽小，五脏俱全。下面进行详细的介绍。  
第1行，包含unp.h的头文件，这个头文件是作者自己写的，这里面包含了诸多的系统头文件以及网U络编程所需要的头文件。  
第5行，sockfd,全称应该是socket file descriptor，用整形表示，是用来保存socket函数返回值，其余的socket相关操作都要通过这个文件描述符来找到我们生成的socket。n用来保存后面read函数读到的字符流的长度。  
第6行，recvline，用来保存字符串。  
第7行，servaddr，是个sockaddr_in类型的结构体，书中整个结构体声明如下：  

{% highlight c++ %}
struct in_addr{
    in_addr_t s_addr; //32bit表示的ip地址，一个unsigned int
};
struct sockaddr_in{
    uint8_t sin_len; //OSI协议的支持
    sa_family_t sin_family; //协议族，这里是AF_INET
    in_port_t sin_port; //16bit端口
    struct in_addr sin_addr; //ipv4地址,32bit
    char sin_zero[8]; //为了和sockaddr结构大小一样进行的冗余数据
};
struct sockaddr{
    uint8_t sa_len;
    sa_family_t sa_family;
    char sa_data[14]; //14字节的协议
};
{% endhighlight %}

由于作者采用的是通用的unix协议，ubuntu等linux版本中有了一些变化，但是仍然遵循POSIX标准。<!-- more -->  
ubuntu中是这个样子的：  

{% highlight c++ %}
#define __SOCKADDR_COMMON(sa_prefix) 
sa_family_t sa_prefix##family 
//宏定义的函数，##代表字符连接，比如下面代码中的__SOCKADDR_COMMON (sin_);就相当于sin_family_t sin_family;
 
/* Internet address. */
typedef uint32_t in_addr_t;
struct in_addr
{
     in_addr_t s_addr;
};
/* 
Structure describing an Internet socket address. */
struct 
sockaddr_in
{
     __SOCKADDR_COMMON (sin_);
 
    in_port_t sin_port; /* Port number. */
    struct in_addr sin_addr; /* Internet address. */
    /* Pad to size of `struct sockaddr'. */
    unsigned char sin_zero[sizeof (struct sockaddr) - 
    __SOCKADDR_COMMON_SIZE - 
    sizeof (in_port_t) - 
    sizeof (struct in_addr)];
};
/* Structure describing a generic socket 
address. */
struct sockaddr
{
     __SOCKADDR_COMMON (sa_); /* Common data: address family and length. */
     char sa_data[14]; /* Address data. */
};

{% endhighlight %}

可以看出书中sockaddr.sa_len和sockaddr_in.sin_len在ubuntu的版本中被去掉了。其余的结构都是一样的。  
sockaddr_in是IPv4套接口地址的结构，也叫"Internet socket address structure"，POSIX标准中要求其必须含有3个成员，sin_family,sin_port和sin_addr，后两个我们已经知道了他们的大小，sin_family的类型为unsiged short，可能会随着操作系统的不同会有所改变。  
第10行，socket函数  
用来创建一个新的socket，如果成功，则返回socket的文件描述符，如果失败，则可以根据返回的负数来查询相应的错误。  

{% highlight c++ %}
/* Create a new socket of type TYPE in domain DOMAIN, using protocol 
PROTOCOL. If PROTOCOL is zero, one is chosen automatically. 
Returns a file descriptor for the new socket, or -1 for errors. 
*/
extern int socket (int __domain, int __type, int __protocol) __THROW;
{% endhighlight %}

domain参数表示通信的域，一般是指定通信的协议族，比如PF_INET/AF_INET表示IPv4协议，PF_INET6/AF_INET6表示IPv6协议，PF_UNIX/PF_LOCAL/AF_UNIX/AF_LOCAL UNIX表示进程通信协议；type表示socket的类型，比如SOCK_STREAM 提供双向连续且可信赖的数据流，即TCP，SOCK_DGRAM 使用不连续不可信赖的数据包连接，UDP；protocol指定在socket中使用的特定的协议。一般来讲，只存在一个单独的协议来支持给定的协议族中特定的socket类型，  
在这种情况下protocol可以用0来代表默认值。然而，有可能很多协议都会存在，在这种情况下特定的协议必须在这种方式下指定。我去源码中找了一下，发现了下面的协议编号。可以根据网络的环境进行选择。  


    {% highlight c++ %}
    /* Standard well-defined IP protocols. */
    enum {
    IPPROTO_IP = 0, /*     Dummy protocol for TCP */
    IPPROTO_ICMP = 1, /* Internet Control Message     Protocol */
    IPPROTO_IGMP = 2, /* Internet Group Management Protocol     */
    IPPROTO_IPIP = 4, /* IPIP tunnels (older KA9Q tunnels use 94)     */
    IPPROTO_TCP = 6, /* Transmission Control Protocol */
    IPPROTO_EGP = 8, /* Exterior Gateway Protocol */
    IPPROTO_PUP = 12, /* PUP protocol */
    IPPROTO_UDP = 17, /* User Datagram Protocol */
    IPPROTO_IDP = 22, /* XNS IDP protocol */
    IPPROTO_DCCP = 33, /* Datagram Congestion Control Protocol */
    IPPROTO_RSVP = 46, /* RSVP protocol */
    IPPROTO_GRE = 47, /* Cisco GRE tunnels (rfc 1701,1702) */
    IPPROTO_IPV6 = 41, /* IPv6-in-IPv4 tunnelling */
    IPPROTO_ESP = 50, /* Encapsulation Security Payload protocol */
    IPPROTO_AH = 51, /* Authentication Header protocol*/
    IPPROTO_BEETPH = 94, /* IP option pseudo header for BEET */
    IPPROTO_PIM = 103, /* Protocol Independent Multicast */
    IPPROTO_COMP = 108, /* Compression Header protocol */
    IPPROTO_SCTP = 132, /* Stream Control Transport Protocol */
    IPPROTO_UDPLITE = 136, /* UDP-Lite (RFC 3828) */
    IPPROTO_RAW = 255, /* Raw IP packets */
    IPPROTO_MAX
    };
    {% endhighlight %}

第12行，bzero函数不知道是不是标准c的一部分，这个函数就是给一段字符串赋0值，比如  

{% highlight c++ %}
char s[10];
bzero(s,sizeof(s));//相当于memset(s,0,sizeof(s));
{% endhighlight %}



   


这一行代码的作用是将servaddr中的内容全部置零。  
第13行，指定通信地址的协议族。  
第14行，指定通信地址的端口。这里有个htons函数，和这个函数类似的函数还有htonl,ntohs,ntohl,这一系列函数中，h代表host，也就是主机，to是转换，n是network，网络，l代表long，s代表short，这里的host和network应该怎么理解，这其实牵扯到主机字节顺序(Host Byte Order)和网络字节顺序(Network Byte Order)这两个概念有关。现在的CPU有两大派系，PowerPC系列CPU和Intel的x86系列CPU。PowerPC系列采用big endian方式存储数据，而x86系列则采用little endian方式存储数据。Big-Endian表示高字节存放在最后(Big End first)，Little-Endian表示低字节放在最后(Litter End first)，举例来说：比如一个数字0x12345678,Big-Endian形式下这4个字节在内存中存放的顺序是  
|12|34|56|78|  
而Little-Endian形式的为  
|78|56|34|12|  
网络上的传输采用的是Big-Endian类型的，所以将本地的数字在进行网络传输之前要先进行转换，利用的就是上面提到的几个函数。  
第15行，赋值通信的ip地址。这里有个函数`inet_pton(int family,const char * strptr,void * addrptr);`就是将点分十进制串转换成网络字节序二进制值，同样要指定下协议族。  
第17行，`connect(sockfd,(SA*)&servaddr,sizeof(servaddr))`，建立一个指定地址的连接。连接的服务器地址为servaddr。这里先给出它的声明`int connect(int sockfdFD,struct sockaddr*,int addrlength);`  
这里就有一个问题，我们是把一个sockaddr_in类型的数据强制转换成了sockaddr类型。其实sockaddr的存储结构和sockaddr_in的存储结构是一样的，sockaddr是通用套接口地址结构(Generic Socket Address Structure)，而sockaddr_in可以看作是sockaddr的一个子集，至于后面的in的含义，我猜是internet的意思。这也解释了为什么sockaddr_in中会有冗余的数据，就是为了将结构体的大小设置成和sockaddr相等。而sockaddr.sa_data中数据可以看作是一种协议地址，不同协议所会有差别，这本书主要讲Internet协议。  
第19行，read函数其实是系统函数，从指定的文件读取数据，这里的文件描述符是创建socket时返回的描述符，也就是从网络读取。这也反映了在Unix系统中一切都是文件的思想。  
剩下的内容都很容易理解了，都是写基本的C语言的语法。  
上面的文件只是一个获取服务器时间的客户端代码，那么服务器端肯定要首先有这个服务，服务器端的代码如下：




daytimetcpsrv.c 

{% highlight c++ %}
#include "unp.h" 
#include <time.h> 
int 
main(int argc, char **argv) 
{ 
    int listenfd, connfd; 
    struct sockaddr_in servaddr; 
    char buff[MAXLINE]; 
    time_t ticks; 
    listenfd = Socket(AF_INET, SOCK_STREAM, 0); 
    bzero(&servaddr, sizeof(servaddr)); 
    servaddr.sin_family = AF_INET; 
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY); 
    servaddr.sin_port = htons(13); /* daytime server */ 
    Bind(listenfd, (SA *) &servaddr, sizeof(servaddr)); 
    Listen(listenfd, LISTENQ); 
    for ( ; ; ) {
        connfd = Accept(listenfd, (SA *) NULL, NULL); 
        ticks = time(NULL); 
        snprintf(buff, sizeof(buff), "%.24srn", ctime(&ticks)); 
        Write(connfd, buff, strlen(buff)); 
        Close(connfd); 
    } 
} 
{% endhighlight %}



这段代码里面又出现了几个新函数。  
第15行，`int bind(int sockfd, const struct sockaddr *my_addr, socklen_t addrlen);`函数，这个函数将socket绑定到网络地址，对于Internet来说，就是ip地址和端口号，每个socket在正常工作前都要进行这种绑定，那么现在看daytimetcpcli.c中的代码中并没有发现这个函数，原因是这样的，如果你没有手动进行绑定，那么系统会在运行的时候绑定本机地址和一个临时的端口，但是这对于客户来说用那个端口是无所谓的，但是如果服务器绑定了一个临时的端口，客户并不知道是那个端口，就没法连接了，所以服务端要绑定一个特定的端口，并和服务器说，你来连接这个端口，这样才会正常的工作。现在看这个socket绑定的地址和端口都是什么，端口是13，这个号理解，但是地址是INADDR_ANY，这是什么意思？因为有可能我的这个服务器有很多网卡，有很多IP地址，我想不管是那个IP地址接受到的数据，只要是通过13端口连接的，我都处理，这时候就可以通过绑定INADDR_ANY来实现。  
第16行，int listen(int sockfd, int backlog)，这个函数是使用主动连接套接口变为被连接套接口，使得一个进程可以接受其它进程的请求，从而成为一个服务器进程。因为当一个socket建立时，默认是主动的，也就是说准备去连接服务器的，但是调用listen后，会将这个socket变成被动，准备接受来自其他socket的连接。一般这个函数只会在服务器端出现。第二个参数是指内核为此套接字排队的最大连接个数。比如很多客户端尝试着连接这个socket，服务器无法快速的完成所有的请求，那么就会维护一个队列。这里指定的值为LISTENQ，这里为1024.  
第18行，`int accept(int sockfd, struct sockaddr* addr, socklen_t* len)`，接受来自sockaddr的连接，如果成功则返回一个全新的文件描述符，代表与客户的网络连接，后面的代码可以看到怎么处理的这个新的文件描述符，需要注意的是，accept函数默认会阻塞进程，也就是说连接成功后程序才会往下执行。  
分析了这两个代码可以基本了解整个连接是怎么建立起来的了：






  1. 服务器端建立一个标识为listenfd的套接字。 

  2. 将listenfd这个套接字绑定到13端口。 

  3. 将listenfd变成被动的socket接口。 

  4. 利用accept函数让listenfd这个套接字来等待客户的连接，服务器端阻塞。 

  5. 服务器建立标识为sockfd的socket，这个socket并没有手动绑定。系统会用本机地址和一个随机的端口对其绑定。 

  6. 将sockfd这个套接字通过connect与服务器地址相连接。如果连接成功，则read函数准备读取这个sockfd的数据，客户端阻塞。 

  7. 服务器端接收到请求，生成一个新的socket与客户端相连接connfd。 

  8. 服务器通过新生成的socket发送给客户端数据。 

  9. 客户端通过与服务器相连接的socket读取到了数据并显示，结束。






![image](/images/unp/005_thumb.png)
其实是两台电脑通过socket进行了进程间通信，代码中是通过文件描述符来代表socket的，至于socket的结构以及怎么就能通过这个socket进行数据传输，这些内容有待研究。
