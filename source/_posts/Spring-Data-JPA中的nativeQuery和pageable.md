---
title: Spring Data JPA中的nativeQuery和pageable
date: 2017-10-11 19:59:21
tags: [SpringDataJPA]
categories: "Spring Cloud"
---

在Sprint Data JPA中默认提供了许多CRUD方法，基本上单表操作已经完全够用了，但是在开发过程中发现使用nativeQuery不能和pageable共用，例如

```java
@Query(value = "SELECT * FROM USERS WHERE EMAIL_ADDRESS = ?1", nativeQuery = true)
  Page<User> findByEmailAddress(String emailAddress, Pageable pageable);
```
此时项目启动时会报:

```java
org.springframework.data.jpa.repository.query.InvalidJpaQueryMethodException: Cannot use native queries with dynamic sorting and/or pagination in method
```
意思就是同一个方法中native queries 不能和 sorting、pagination共用。
但是这种需求却是实实在在的存在的，查看Spring Data JPA官方文档，给出了一下解决方式:

```java
@Query(value = "SELECT * FROM USERS WHERE LASTNAME = ?1",
    countQuery = "SELECT count(*) FROM USERS WHERE LASTNAME = ?1",
    nativeQuery = true)
  Page<User> findByLastname(String lastname, Pageable pageable);
```
使用此方式后依然报上文的exception，查阅其他资料后使用如下方式解决:


```java
@Query(value = "SELECT * FROM USERS WHERE EMAIL_ADDRESS = ?1 \n#pageable\n", nativeQuery = true)
  Page<User> findByEmailAddress(String emailAddress, Pageable pageable);
```

在sql一句后加上 **\n#pageable\n**

这很有可能是Spring Data JPA的一个bug，并且在Spring的jira上也发现了这个issue
**https://jira.spring.io/browse/DATAJPA-928**

都是泪。