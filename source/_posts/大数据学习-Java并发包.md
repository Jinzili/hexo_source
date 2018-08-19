---
title: 大数据学习 - Java并发包
date: 2018-07-29 22:24:52
tags: ["大数据", "并发包"]
categories: "大数据"
---
## Java并发包介绍
JDK5.0以后的版本都引入了高级并发特性，大多数的特性在java.util.concurrent包中，是专门用于多线程编程的，充分利用了现代多处理器和多核心系统的功能以编写大规模并发应用程序。主要包含原子量，并发集合，同步器，可重入锁，并对线程池的构造提供了支持。
## 线程池
1. Single Thread Executor：只有一个线程的线程池，因此所有提交的任务都是顺序执行。Executors.newSingleThreadExecurot()
2. Cached Thread Pool：线程池具有很多线程需要同时执行，老的可用线程将被新的任务出发重新执行，如果线程超过60秒内没执行，那么将被终止并从池中删除。Execurots.newCachedThreadPool()
3. Fixed Thread Pool：拥有固定线程数的线程池，如果没有任务执行，那么线程会一直等待。Executors.newFixedThreadPool(4)，构造函数中的4是线程池大小，可以根据需要配置。获取cpu数量：
```
int cpuNums = Runtime.getRuntime().availableProcessors()
```
4. Scheduled Thread Pool：用来调度即将执行的任务的线程池。Executors.newScheduledThreadPool()。
5. Single Thread Scheduled Pool：只有一个线程，用来调度任务在指定时间执行。Executors.newSingleThreadScheduledExecutor()

## runnable和callable
1. runnable的run方法不会有任何返回结果, 所以主线程无法获得任务线程的返回值
2. callable的call方法可以返回结果, 但是主线程在获取时会被阻塞, 需要等待任务线程返回才能拿到结果。

## 并发包消息队列BlockingQueue
BlockingQueue是java.util.concurrent下的主要用来控制线程同步的工具。
主要的方法是: put, take 阻塞存取。add, poll 非阻塞存取。
### 插入
- add(anObject)：把anObject加到BlockingQueue里, 即如果BlockingQueue可以容纳, 则返回true, 否则抛出
- offer(anObject)：如果可能的话, 将anObject插入, 返回true, 如果不可以容纳则返回false
- put(anObject)：插入anObject, 如果BlockQueue没有空间, 则调用此方法的线程被阻断知道BlockingQueue里面有空间再继续。
### 读取
- poll(time)：读取BlockingQueue里首位对象, 若不能立即取出, 则可以等time参数规定的时间, 取不到返回null
- take()：读取BlockingQueue首位对象, 若BlockingQueue为空, 阻断, 进入等待状态直到有对象可以读取
### 其他
- int remaingCapacity()：返回队列剩余的容量
- boolean remove(Object o)：从队列移除元素, 如果存在, 即移除一个或多个, 队列有改变了返回true
- boolean contains(Object o)：查看队列是否存在这个元素, 存在返回true
- int drainTo(Collection<? super E> c)：移除队列中所有的可用元素, 并将它们添加到给定的collection中
- int drainTo(Collection<? super E> c, int maxElements)：和上面方法的区别在于制定了移动的数量

### BlockingQueue两种实现类
- ArrayBlockingQueue：一个由数组支持的有界阻塞队列, 规定大小的BlockingQueue, 其构造函数必须带一个in参数来知名其大小, 其所含的对象是以FIFO顺序排序的。
- LinkedBlockingQueue： 大小不定的BlockingQueue, 若其构造函数带一个规定大小的参数, 生成的BlockingQueue有大小限制, 若不带大小参数, 所生成的BlockingQueue的大小由Integer.MAX_VALUE来决定, 同样也是FIFO。

区别
- 它们背后所用的数据结构不一样，导致LinkedBlockingQueue的数据吞吐量要大于ArrayBockingQueue，但在线程数量很大时其性能的可预见性低于ArrayBlockingQueue
- 队列大小有所不同，ArrayBlockingQueue是有界的必须指定大小，而linkedBlockingQueue可以是有界的也可以是无界的（Integer.MAX_VALUE），对于后者，当添加速度大于移除速度时，在无界的情况下，可能会造成内存泄漏
- 由于ArrayBlockingQueue采用的数组作为数据存储容器，因此在插入或删除元素时不会产生或销毁任何额外的对象实例，而LinkedBlockingQueue则会生成一个额外的Node对象。这可能在长时间内需要高效并发地处理大批量数据时，对于GC可能存在较大影响
- 两者的实现队列添加或移除的锁不一样，ArrayBlockingQueue实现的队列中的锁是没有分离的，即添加操作和移除操作采用的同一个ReentrantLock，而LinkedBlockingQueue实现的队列中的锁是分离的，其添加采用的putLock，移除采用的则是takeLock，这样能大大提高队列的吞吐量，也意味着在高并发的情况下生产者和消费者可以并行地操作队列的数据，以此来提高整个队列的并发性能。
## 总结
1.  不应用线程池的缺点
- 新建线程的开销，线程虽然比进程要轻量许多，但对于JVM来说，新建一个线程的代价还是挺大的，绝不同于新建一个对象
- 资源消耗量，没有一个池来限制线程的数量，会导致线程的数量直接取决于应用的并发量，这样有潜在的线程数巨大的可能，那么消耗的资源类将是巨大的
- 稳定性，当线程数量超过系统资源所能承受的成都，稳定性就会成问题
2.  制定线程策略
在每个需要多线程处理的地方，不管并发量有多大，需要考虑线程的执行策略
- 任务以什么顺序执行
- 可以有多少个任务并发执行
- 可以有多少个任务进入等待执行队列
- 系统过载的时候，应该放弃哪些任务？如何通知到应用程序？
- 一个任务的执行前后应该做什么处理
3.  线程池饱和策略

除了CachedThreadPool其他线程池都有饱和的可能，当饱和以后就需要相应的策略处理请求线程的任务，比如，达到上限时通过ThreadPoolExecutor.setRejectedExecutionHandler方法设置一个拒绝任务的策略JDK提供了AbortPolicy, CallerRunsPolicy, DiscardPolicy, DiscardOldestPolicy
4. 线程无依赖性

多线程任务设计上尽量使得个任务是独立无依赖的，两个方面
1、线程之间的依赖性。如果线程有依赖可能会造成死锁或饥饿
2、调用者与线程的依赖性，调用者得监视线程的完成情况，影响并发量