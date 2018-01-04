---
title: Hibernate - no longer referenced异常
date: 2018-01-04 18:09:17
tags: ["Hibernate"]
categories: "Java Framework"
---
在使用hibernate级联关系时给了我们极大的便利，但是有时也会出现莫名其妙的异常，代码怎么看都没有问题，save的时候就是抛出了异常(气😠)。

最近就被同事问到了这样的问题，调用save的时候抛出了这个异常：


```Java
org.hibernate.HibernateException:
A collection with cascade="all-delete-orphan" was no longer referenced by the owning entity instance
```

字面意思是说，这个entity不再拥有实例的引用，我们反复检查了代码都没有发现问题。。。。

经过一顿操作之后（google😏），终于发现了问题。

在一个one to many关系时，一的那一方我们定义了：

```Java
@OneToMany(cascade = CascadeType.ALL, mappedBy = "parent", orphanRemoval = true)
private List<Children> childs = new ArrayList<>();
```
问题就出在orphanRemoval=true这里，当这个值为true时，hibernate会帮我们管理这个子集合，所有当childs为null或调用普通的set方法时，就会抛出上面这个异常。


```Java
public void setChilds(List<Children> childs){
    // will throw exception like this
    this.childs = childs;
}

```

这是因为我们声明了一个新的childs代替了原本的childs，导致parent实体与原本的childs之间的关系被破坏了，但是原本的childs还存在于这一个session中，所以当我们调用save的时候，原本的childs与parent之间关系被破坏，hibernate不认识了原本的childs，就会throw上面的异常。

当知道了为什么之后，事情就好办了，我们需要对set方法进行改造：
```Java
public void setChilds(List<Children> childs){
    this.childs.clear();
    this.childs.addAll(childs);
}
```
这样childs和parent之间的关系没有被破坏，当然save的时候hibernate也就认识了这个childs啦。
