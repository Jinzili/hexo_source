---
title: get set原子性引发出的思考
date: 2018-06-14 10:07:08
tags: ["原子性"]
categories: "技术杂谈"
---
经常在业务中碰到对变量先get变量判断是否为blank，如果不为blank直接返回，如果为blank需先获取设置到变量，在返回，伪代码如下：
```Java
    private String getToken(){
        // select
        String accessToken = redisUtils.get(key);
        if(StringUtils.isBlank(accessToken)){
            // get set
            accessToken = HTTPUtils.doGet(url);
            redisUtils.setEx(key, accessToken, 7000, TimeUtils.SECONDS);
        }
        return accessToken;
    }
```

这里我们就能发现问题了，我们操作的redis中的key相当于全局变量，如果此时不幸同一时刻多个线程同时获取accessToken，更不幸的是最新获取的accessToken才是有效的，那么有很大的几率前一个线程刚获取到accessToken开始表演的时候，被通知accessToken已失效导致整段垮掉。所以怎样保证线程安全的同时还能保证高性能呢？这期间也思考了多种方法：

### 简单粗暴型
直接对getToken整个方法进行同步

```Java
    private syncronzied String getToken(){...}
```

这个方法完全解决了全局变量线程安全的问题，select->get->set 将这一整个操作保证原子性，但是劣处也是显而易见的，这里的锁颗粒度太大，导致所有线程必须乖乖的一个一个getToken, 性能不用说也知道极差，有没有一种方法可以保证多线程的读，但是只有一个线程能写呢？
### 只锁get set
我们来改变一下锁的位置:

```Java
    private static final byte[] mutex = new byte[0];
    private String getToken(){
        // select
        String accessToken = redisUtils.get(key);
        if(StringUtils.isBlank(accessToken)){
            syncronized(mutex){
                // get set
                accessToken = HTTPUtils.doGet(url);
                redisUtils.setEx(key, accessToken, 7000, TimeUtils.SECONDS);
            }
        }
        return accessToken;
    }
```

当select accessToken为blank的时候才会进入同步代码块 get set，乍一看可能没问题了，其实当同一时刻多个线程访问的时候还是会有问题，比如多个线程已经进行了blank判断，都在等待mutext的锁，导致前一个得到mutex锁的线程获取到的accessToken因为下一个线程再次get set accessToken而失效。

### 双重检查
为了解决上一种方法碰到的问题，我们可以在获取到锁时再次进行确认：

```Java
    private static final byte[] mutex = new byte[0];
    private String getToken(){
        // select
        String accessToken = redisUtils.get(key);
        if(StringUtils.isBlank(accessToken)){
            syncronized(mutex){
                // 再次确认
                accessToken = redisUtils.get(key);
                if(StringUtils.isBlank(accessToken)){
                    // get set
                    accessToken = HTTPUtils.doGet(url);
                    redisUtils.setEx(key, accessToken, 7000, TimeUtils.SECONDS);
                }
            }
        }
        return accessToken;
    }
```

此时既保证了线程安全的同时，又尽可能的减少同步代码提升性能。