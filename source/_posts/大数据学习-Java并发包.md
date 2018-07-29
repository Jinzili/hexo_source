---
title: 大数据学习 - Java并发包
date: 2018-07-29 22:24:52
tags: ["大数据", "并发包"]
categories: "大数据"
---
Java并发包介绍

JDK5.0以后的版本都引入了高级并发特性，大多数的特性在java.util.concurrent包中，时专门用于多线程编程的，充分利用了现代多处理器和多核心系统的功能以编写大规模并发应用程序。主要包含原子量，并发集合，同步器，可重入锁，并对线程池的构造提供了支持。

线程池

Single Thread Executor：只有一个线程的线程池，因此所有提交的任务都是顺序执行。Executors.newSingleThreadExecurot()
Cached Thread Pool：线程池具有很多线程需要同时执行，老的可用线程将被新的任务出发重新执行，如果线程超过60秒内没执行，那么将被终止并从池中删除。Execurots.newCachedThreadPool()
Fixed Thread Pool：拥有固定线程数的线程池，如果没有任务执行，那么线程会一直等待。Executors.newFixedThreadPool(4)，构造函数中的4是线程池大小，可以根据需要配置。获取cpu数量：
int cpuNums = Runtime.getRuntime().availableProcessors()
Scheduled Thread Pool：用来调度即将执行的任务的线程池。Executors.newScheduledThreadPool()。
Single Thread Scheduled Pool：只有一个线程，用来调度任务在指定时间执行。Executors.newSingleThreadScheduledExecutor()
(未完待续)