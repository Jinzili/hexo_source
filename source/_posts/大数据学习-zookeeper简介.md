---
title: 大数据学习 - zookeeper简介
date: 2018-07-22 21:42:11
tags: ["大数据", "zookeeper"]
categories: "大数据"
---

## 概念简介
 zookeeper(zk)是一个分布式协调服务，zk本身就是一个分布式程序，在底层其实只提供了两个功能：

- 管理（存储、读取）用户程序提交的数据
- 提供数据节点监听服务

常用的应用场景有
- 服务器状态的动态通知
- 配置文件管理
- 分布式共享锁
- 名称服务

zk集群有两个角色：leader和follower(observer)
只要集群中半数以上节点存活，集群就能提供服务。

## 特性
1. 一个leader、多个follower组成的集群
2. 全局数据一致, 每个server保存一份相同的数据副本, client无论连接到哪个server, 数据都是一致的(强一致性)
3. 分布式读写, 更新请求转发, 由leader实施
4. 更新请求顺序进行, 来自同一个client的更新请求按其发送顺序依次执行
5. 数据更新原子性, 一次数据更新要么成功, 要么失败
6. 实时性, 在一定时间范围内, client能读到最新数据

## 数据结构
1. 层次化的目录结构, 明明符合常规文件系统规范
2. 每个节点在zk中叫做znode, 并且有一个唯一的路径标识
3. 节点znode可以包含数据和子节点(但是EPHEMERAL类型的节点不能有子节点)
4. 客户端应用可以在节点上设置监视器

## 节点类型
1. znode有两种类型
短暂(ephemeral): 断开连接自动删除
持久(persistent): 断开连接不删除
2. znode有4中形式的目录节点
- PERSISTENT(default)
- PERSISTENT_SEQUENTIAL(持久序列/test0000000019)
- EPHEMERAL
- EPEMERAL_SEQUENTIAL
3. SEQUENTIAL表示序列节点, 创建znode时设置顺序标识, znode名称后会附加一个值, 顺序时一个单调递增的计数器, 又父节点维护
4. 在分布式系统中, 顺序号可以被用于为所有的时间进行全局排序, 这样客户端可以通过顺序号推断时间的顺序。

## zk原理
zk虽然在配置文件并没有指定leader和follower, 但是, zk工作时, 是有一个节点为leader, 其他则为follower, leader是通过内部的选举机制临时产生的。
### zk的选举机制(全新集群使用paxos)
 以一个简单的例子来说明整个选举的过程.
假设有五台服务器组成的zookeeper集群,它们的id从1-5,同时它们都是最新启动的,也就是没有历史数据,在存放数据量这一点上,都是一样的.假设这些服务器依序启动,来看看会发生什么.
1) 服务器1启动,此时只有它一台服务器启动了,它发出去的报没有任何响应,所以它的选举状态一直是LOOKING状态
2) 服务器2启动,它与最开始启动的服务器1进行通信,互相交换自己的选举结果,由于两者都没有历史数据,所以id值较大的服务器2胜出,但是由于没有达到超过半数以上的服务器都同意选举它(这个例子中的半数以上是3),所以服务器1,2还是继续保持LOOKING状态.
3) 服务器3启动,根据前面的理论分析,服务器3成为服务器1,2,3中的老大,而与上面不同的是,此时有三台服务器选举了它,所以它成为了这次选举的leader.
4) 服务器4启动,根据前面的分析,理论上服务器4应该是服务器1,2,3,4中最大的,但是由于前面已经有半数以上的服务器选举了服务器3,所以它只能接收当小弟的命了.
5) 服务器5启动,同4一样,当小弟.
### 非全新集群的选举机制
那么，初始化的时候，是按照上述的说明进行选举的，但是当zookeeper运行了一段时间之后，有机器down掉，重新选举时，选举过程就相对复杂了。
需要加入数据id、leader id和逻辑时钟。
数据id：数据新的id就大，数据每次更新都会更新id。
Leader id：就是我们配置的myid中的值，每个机器一个。
逻辑时钟：这个值从0开始递增,每次选举对应一个值,也就是说:  如果在同一次选举中,那么这个值应该是一致的 ;  逻辑时钟值越大,说明这一次选举leader的进程更新.
选举的标准就变成：
		
1、逻辑时钟小的选举结果被忽略，重新投票

2、统一逻辑时钟后，数据id大的胜出

3、数据id相同的情况下，leader id大的胜出

根据这个规则选出leader。

## 安装
### 环境部署
至少3台有jdk环境的机器（虚拟机也可）
### 下载
两种方法，官网下载使用ftp工具传输到机器上或直接使用wget

```
wget https://mirrors.tuna.tsinghua.edu.cn/apache/zookeeper/zookeeper-3.4.13/zookeeper-3.4.13.tar.gz
```
### 解压并重命名

```
tar -zxvf zookeeper-3.4.13.tar.gz
mv zookeeper-3.4.13 zookeeper
```
### 修改环境变量
1. su -root，切换到root用户
2. vim /etx/profile
3. 添加内容
```
export ZOOKEEPER_HOME=/home/hadoop/zookeeper
export PATH=$PATH:$ZOOKEEPER_HOME/bin
```
4. 重新加载文件

```
source /etc/profile
```
5. 切换回hadoop用户
6. 注意，所有的zk机器都需要修改

## 修改配置文件
1. 在zk文件夹中操作
```
cd zookeeper/conf
cp zoo_sample.cfg zoo.cfg
```
2. vim zoo.cfg 添加内容

```
dataDir=/home/hadoop/zookeeper/data
dataLogDir=/home/hadoop/zookeeper/log
server.1=slave1:2888:3888 (主机名, 心跳端口、数据端口)
server.2=slave2:2888:3888
server.3=slave3:2888:3888
```
3. 创建文件夹

```
cd /home/hadoop/zookeeper/
mkdir -m 755 data
mkdir -m 755 log
```
4. 在data文件下新建myid文件, 内容为

```
echo 1 >> myid
```

## 复制修改好的zk文件夹到其他机器上

```
scp -r /home/hadoop/zookeeper hadoop@slave2:/home/hadoop/
scp -r /home/hadoop/zookeeper hadoop@slave3:/home/hadoop/
```
并且要记得修改myid文件：
slave2上内容修改为2
slave3上内容修改为3
## 启动
zkServer.sh start

