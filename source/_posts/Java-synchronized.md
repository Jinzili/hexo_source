---
title: Java - synchronized
date: 2017-11-25 16:34:07
tags: ["锁", "synchronized"]
categories: "技术杂谈"
---
当我们在使用synchronized时，通常有下面几种方式：

### synchronized(this){}

```Java
public class SynchronizedTest {

    public static class RunnableThread implements Runnable{

        @Override
        public void run() {
            synchronized (this){
                System.out.println(this);
                for(int i = 0; i < 50; i++){
                    System.out.println(Thread.currentThread().getName() + ":" + i);
                }
            }
        }
    }


    @Test
    public void synchronizedThisTest(){
        RunnableThread r1 = new RunnableThread();
//        RunnableThread r2 = new RunnableThread();
        Thread t1 = new Thread(r1, "t1");
        Thread t2 = new Thread(r1, "t2");
        t1.start();
        t2.start();
    }

}
```

```
com.jzl.javabase.SynchronizedTest$RunnableThread@4c5986b6
t1:0
...
com.jzl.javabase.SynchronizedTest$RunnableThread@4c5986b6
t2:0
...
```
**此时我们可以看到syschronized(this)中this指的是同一对象, 这段代码块同一时刻只能有同一线程运行。** 

再来看这种形式:

```Java
RunnableThread r1 = new RunnableThread();
RunnableThread r2 = new RunnableThread();
Thread t1 = new Thread(r1, "t1");
Thread t2 = new Thread(r2, "t2");
```

```
com.jzl.javabase.SynchronizedTest$RunnableThread@4c5986b6
com.jzl.javabase.SynchronizedTest$RunnableThread@22419e86
t2:0
...
```
**此时this指的不是同一个对象, 所以这种情况syschronized代码块并不能保证同一时刻只有同一线程运行**。

再来看看这种情况：

```Java
public static class CommonClass{

        public void lockMethod() {
            synchronized (this){
                for(int i = 0; i < 5; i++){
                    System.out.println(Thread.currentThread().getName() + ":" + i);
                    try {
                        TimeUnit.SECONDS.sleep(2);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
        }

        public void notLockMethod() {
            for(int i = 0; i < 5; i++){
                System.out.println(Thread.currentThread().getName() + ":" + i);
                try {
                    TimeUnit.SECONDS.sleep(2);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }

    }

    @Test
    public void test2() throws InterruptedException {
        CommonClass cc = new CommonClass();
        Thread t1 = new Thread(() -> {cc.lockMethod();}, "t1");
        Thread t2 = new Thread(() -> {cc.notLockMethod();}, "t2");
        t1.start();
        t2.start();
        t1.join();
        t2.join();
    }
```
运行结果：

```
t1:0
t2:0
t2:1
t1:1
...
```
很显然，**当一个线程访问这个对象的synchronized(this)方法时, 其他线程仍然可以访问这个对象的非synchronized(this)方法。**

### public synchronized void lockMethod()


```Java
public static class LockClass{

        public synchronized void lockMethod(){
            for(int i = 0; i < 5; i ++){
                System.out.println(Thread.currentThread().getName() + ":" + i);
                try {
                    TimeUnit.SECONDS.sleep(1);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }

    }

    @Test
    public void lockClassTest() throws InterruptedException {
        LockClass l1 = new LockClass();
//        LockClass l2 = new LockClass();
        Thread t1 = new Thread(() -> {l1.lockMethod();}, "t1");
        Thread t2 = new Thread(() -> {l1.lockMethod();}, "t2");
        t1.start();
        t2.start();
        t1.join();
        t2.join();
    }
    
    @Test
    public void lockClassTest() throws InterruptedException {
        LockClass l1 = new LockClass();        LockClass l2 = new LockClass();
        Thread t1 = new Thread(() -> {l1.lockMethod();}, "t1");
        Thread t2 = new Thread(() -> {l2.lockMethod();}, "t2");
        t1.start();
        t2.start();
        t1.join();
        t2.join();
    }
```
通过对比运行结果发现, 这种方式与synchronized(this)方式相同。第二种虽然方法是同步的, 但是锁住的却不是一个对象, 所以不能保证同一时刻只有一个线程运行此代码块。
如果要求不同对象间也只能有一个线程运行某个方法, 有两种方法可以实现：
- synchronized(Object.class){// 同步代码块}
- public synchronized static void lockMethod(){// 同步代码块}
- public void lockMethod2(SomeObject so){synchronized(so){// 同步代码块}}

对于第一种方法, 通常定一个静态byte数组实现：

```Java
private static final byte[] mutex = new byte[0];
...
synchronzied(mutex){// 同步代码块}
...
// 或者是
synchronzied(SomeObject.class){// 同步代码块}
```
注：使用byte数组创建起来比其他对象更加经济--生成零长度的byte数组只需要三行操作码，而new Object()需要7行。

### 总结
在使用synchronized锁时，我们要注意锁住的对象到底是什么，然后在假设同时有多个线程同时进入代码块可能会发生的情况。这样我们就能设计更安全的多线程程序。