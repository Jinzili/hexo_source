---
title: Java类加载机制(二)
date: 2018-07-08 08:52:42
tags: ["类加载"]
categories: "JavaBase"
---
## 类加载
先来看个栗子🌰：

```Java
@Test
public void test(){
    ClassLoader loader = Thread.currentThread().getContextClassLoader();
    System.out.println(loader);
    System.out.println(loader.getParent());
    System.out.println(loader.getParent().getParent());
}
```
输出为：

```Java
sun.misc.Launcher$AppClassLoader@18b4aac2
sun.misc.Launcher$ExtClassLoader@5f5a92bb
null
```
可以看出，没有获取到ExtClassLoader的父Loader，原因是Bootstrap Loader(引导类加载器)是用C语言实现的，找不到一个确定的返回父Loader的方式，于是返回为null。

站在Java虚拟机的角度来说，只存在两种不同的类加载器：
- 启动类加载器：使用C++实现（仅限于Hotspot），是虚拟机的一部分
- 所有其他类加载器：这些加载器都由Java语言实现，独立于虚拟机之外，并且全部继承自抽象类java.lang.ClassLoader，这些类加载器需要由启动类加载器加载到内存中之后才能去加载其他的类。

站在开发人员的角度来说，大致可分为三类类加载器：
- 启动类加载器：Bootstrap Loader，负责加载存放在JDK/jre/lib下，或被-Xbootclasspath参数指定的路径中，并且能被虚拟机识别的类库（如rt.jar，所有的java.*开头的类均被BootstrapClassLaoder加载）。启动类加载器是无法被Java程序直接引用的。
- 扩展类加载器：Extension ClassLoader，该加载器由sun.misc.Launcher$ExtClassLoader实现，它负责加载JDK/jre/lib/ext目录中，或者由java.ext.dirs系统变量指定的路径中的所有类库（如javax.*开头的类），开发人员可以直接使用扩展类加载器。
- 应用程序类加载器：Application ClassLoader，该类加载器由sun.misc.Launcher$AppClassLoader来实现，它负责加载用户类路径所指定的类，开发人员可以直接使用该类加载器，如果应用程序中没有自定义过自己的类加载器，一般情况下这个就是程序中默认的类加载器。

如果有必要，还可以假如自定义的类加载器。

ExtClassLoader和APPClassLoader并不是继承关系，它们都继承同一个类URLClassLoader。

> JVM类加载机制：
> 
> - 全盘负责：当一个类加载器负责加载某个Class时，该Class所依赖的和引用的其他Class也将由该类加载器负责载入，除非显示使用另外一个类加载器来载入
> - 父类委托：先让父类加载器试图加载该类，只有在父类加载器无法加载该类时才尝试从自己的类路径加载该类
> - 缓存机制：缓存机制会保证所有加载过的Class都会被缓存，当程序中需要使用某个Class时，类加载器先从缓存区寻找该Class，只有缓存区不存在，系统才会读取该类对应的二进制数据，并将其转换成Class对象，存入缓存区。这就是为什么修改了Class后，必须重启JVM，程序的修改才会生效

![image](https://cloud.gemii.cc/lizcloud/fs/noauth/media/5ac4463d1e6d8a0037546f68)

## 双亲委派机制
> 为什么需要双亲委派机制？
> 
> 先说明一下，jvm判断两个类相同的前提是这两个类都是同一个加载器进行加载的，如果使用不同的类加载器进行加载同一个类，那在jvm中会认为它们是不同的。所以如果没有双亲委派机制，如果我们在rt.jar中随便找一个类，如java.util.HashMap，那么我们同样也可以写一个一样的类，也叫java.util.HashMap存放在我们自己的路径下，那么这两个类采用的是不同的类加载器，程序中就会出现两个不同的HashMap类。总结来说，1、系统类防止内存中出现多芬同样的字节码 2、保证Java程序安全稳定运行

双亲委派的工作流程是：如果一个类加载器收到了类加载的请求，它首先不会自己去尝试加载这个类，而是把请求委托给父加载器去完成，依次向上，所以所有的类加载请求最终都应该被传递到顶层的启动类加载器中，只有当父加载器在它的搜索范围中没有找到所需的类时，即无法完成该加载，子加载器才会尝试自己去加载该类。