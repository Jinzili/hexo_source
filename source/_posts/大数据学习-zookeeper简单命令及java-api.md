---
title: 大数据学习 - zookeeper简单命令及java api
date: 2018-07-22 21:43:32
tags: ["大数据", "zookeeper"]
categories: "大数据"
---

## bash cmd
- 1、使用ls命令来查看当前zk中所包含的内容
```
ls /
```
- 2、创建一个新的znode。这个命令创建了一个新的znode节点 "zk"以及与它关联的字符串。
```
create /zk
```

- 3、运行get命令来确认znode是否包含我们所创建的字符串
```
get /zk
```
- 4、通过set命令来对zk所关联的字符串进行设置
```
set /zk "test"
```
- 5、删除znode
```
delete /zk
```
- 6、删除节点
```
rmr /zk
```
## java api


org.apache.zookeeper.Zookeeper时客户端入口类, 负责建立与server的会话, 提供了几类主要方法:

功能 | 描述
---|---
create | 在本地目录树中创建一个节点
delete | 删除一个节点
exists | 是否存在目标节点
get/set data | 从目标姐弟啊读取/写数据
get/set ACL | 获取/设置目标节点访问控制列表信息
get children | 检索目标节点的子节点
sync | 等待要被传送的数据

### demo

```Java
private static final String CONNECT_STRING = "bigdata1:2181,bigdata2:2181,bigdata3:2181";

private static final Integer SESSION_TIMEOUT = 2000;

private ZooKeeper zkClient = null;

/**
 * 初始化client
 */
@Before
public void init() throws IOException {
    zkClient = new ZooKeeper(CONNECT_STRING, SESSION_TIMEOUT, (event) -> {
        // 收到时间通知后的回调函数 是我们自己的事件处理逻辑
        // 初始化时会收到一次
        System.out.println(event.getType() + "---" + event.getPath());
        try {
            // 重新执行监听
            zkClient.getChildren("/", true);
        } catch (Exception e) {
            e.printStackTrace();
        }
    });
}

/**
 * 数据的增删改查
 */
// 创建数据
@Test
public void create() throws KeeperException, InterruptedException {
    // 路径 数据 权限 类型
    String create = zkClient.create("/idea",
            "hello world".getBytes(),
            ZooDefs.Ids.OPEN_ACL_UNSAFE,
            CreateMode.PERSISTENT);
    System.out.println("create: " + create);
}

// 子节点是否存在
@Test
public void exists() throws KeeperException, InterruptedException {
    Stat stat = zkClient.exists("/idea", false);
    System.out.println(stat == null ? "not exists" : "exists");
}

// 获取子节点数据
@Test
public void getChildren() throws KeeperException, InterruptedException {
    // 路径 是否监听数据变化
    List<String> childs = zkClient.getChildren("/", true);
    childs.forEach(System.out::println);
}

// 获取节点数据
@Test
public void get() throws KeeperException, InterruptedException {
    byte[] data = zkClient.getData("/idea", false, null);
    System.out.println(new String(data));
}

// 删除节点数据
@Test
public void delete() throws KeeperException, InterruptedException {
    // 参数2, 指定要删除的版本, -1表示删除所有版本
    zkClient.delete("/idea", -1);
}

// 设置节点数据
@Test
public void set() throws KeeperException, InterruptedException {
    zkClient.setData("/idea", "hello world 2".getBytes(), -1);
}
```



