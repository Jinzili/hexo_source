---
title: Spring Cloud - Eureka
date: 2017-10-25 18:31:10
tags: [SpringCloud, Eureka]
categories: "Spring Cloud"
---
# Eureka
在Spring Cloud体系中，eureka承担着服务注册与发现的任务，在整个微服务架构中起着整合作用。eureka的一些概念：
## 服务提供者
provider，指一个将自身的功能接口暴露出来的应用。
## 服务消费者
consumer，指需要借助provider提供的功能完成自身业务的应用。
## 服务注册
当provider应用启动时，会将自身的元数据，比如IP地址，端口，应用名等注册到eureka server中。
## 服务续约
provider每搁固定的时间段(默认30秒)，向eureka server汇报一次自身状况，如果eureka server在固定的时间段(默认90秒)内没有收到某一provider的服务续约的请求，将会把这个provider实例从服务列表中剔除。
## 获取注册信息
consumer应用会定时从eureka server获取服务注册列表信息以供自身进行远程调用，consumer应用默认每30秒会更新一次注册列表信息，默认eureka server和consumer应用使用压缩的json进行交互。
## 服务下线
provider应用关闭时，会向eureka server发送下线请求，eureka server收到请求后会将此provider实例信息从服务注册列表中剔除。

# Eureka Server
## 添加eureka server依赖

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-eureka-server</artifactId>
</dependency>
```
## application.yml 配置


```
server:
  port: 8761 # 服务端口

spring:
  application:
    name: eurekaServer # 服务名
eureka:
  environment: devlopment # eureka server环境
  instance:
    lease-renewal-interval-in-seconds: 10 # 发送心跳的间隔时间
    lease-expiration-duration-in-seconds: 30 # 若这个时间段没收到心跳则移除该instance
    prefer-ip-address: true # 实例名称显示IP配置

  client:
    serviceUrl:
      defaultZone: http://localhost:8761/eureka/ # eureka server的地址
    register-with-eureka: true # 此服务是否注册到eureka server上
  server:
    enable-self-preservation: false # 关闭自我保护模式
    eviction-interval-timer-in-ms: 4000 # 扫描失效服务间隔(单位ms, 默认是60 * 1000)
    wait-time-in-ms-when-sync-empty: 0

debug: true # debug 模式
```

## 加入@EnableEurekaServer注解


```java
@SpringBootApplication
@EnableEurekaServer
public class EurekaApplication {
    public static void main(String[] args) {
        SpringApplication.run(EurekaApplication.class, args);
    }
}
```
只需这简单的配置，就已经搭建了一台eureka server应用。

# Eureka Client
## 添加eureka依赖

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-eureka</artifactId>
</dependency>
```
## application.yml 配置

```
server:
  port: 8080
debug: true
eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
  instance:
    prefer-ip-address: true   #将自己的IP注册到eureka server上,如不配置则表示注册微服务所在操作系统的hostname到eureka server
```

## 加入@EnableDiscoveryClient注解

```java
/**
 * TODO
 * Created by jinzili on 09/06/2017.
 */
@SpringBootApplication
@EnableDiscoveryClient
public class ProviderUserApplication {
    public static void main(String[] args) {
        SpringApplication.run(ProviderUserApplication.class, args);
    }
}
```

现在我们已经搭建好了一台Eureka Server 和一台provider，访问http://localhost:8761看看效果！
![image](https://static.oschina.net/uploads/space/2017/1025/182114_6w0z_3559870.png)

perfect!

我们的两个服务已经注册到了Eureka Server上，上图的红字是因为我们在Eureka Server服务的application.yml配置了eureka.server.enable-self-preservation: false 关闭了自我保护模式，推荐在开发中我们使用此配置，可以及时刷新服务的最新状态，但是切记在生产环境使用要开启自我保护模式。