---
title: 在web项目中应用SpringMVC
date: 2017-10-08 10:30:16
tags: [SpringMVC, web]
categories: Spring
---
## 什么是springmvc ##

springmvc是spring框架的一个模块,springmvc和spring无需通过中间整个层进行整合，它是一个基于mvc的web框架。

## springmvc与struts2的区别 ##

 1. springmvc是基于方法开发的，struts2是基于类开发的。springmvc将url和controller方法映射，映射成功后springmvc生成一个Handler对象（也就是controller），对象中只包括了映射的method，方法执行结束后，形参数据销毁。
 2. springmvc可以进行单例开发，并且建议使用单例开发，struts2只能多例开发（struts2通过类成员变量接收数据，多个线程中的数据可能不一样，所以不能使用单例开发）。
 3. 经过实际的测试，struts2速度慢，是因为使用了struts标签，所以在使用struts2进行开发的时候，建议使用jstl。

## springmvc框架执行流程 ##
![springmvc框架执行流程](http://img.blog.csdn.net/20160409092707614)

## 用入门程序来学习springmvc ##

springmvc运行环境
==
![所有jar包](http://img.blog.csdn.net/20160409093349320)
jar包下载地址（mybatis+spring（包括springmvc）所有jar包）：
http://download.csdn.net/detail/jinzili777/9480604

配置前端控制器
==
在web.xml文件中，

```xml
<!-- springmvc前端控制器 -->
<servlet>
  	<servlet-name>springmvc</servlet-name>
  	<servlet-class>org.springframework.web.servlet.DispatcherServlet</servlet-class>
  	<!-- 
  		contextConfigLocation配置springmvc加载的配置文件路径(配置映射器,适配器等)
		如果不配置此属性,默认加载的是/WEB-INF/servlet名称-servlet.xml(在这里就是上面<servlet-name>的值:springmvc-servlet.xml)
  	 -->
  	<init-param>
  		<param-name>contextConfigLocation</param-name>
  		<param-value>classpath:spring/springmvc.xml</param-value>
  	</init-param>
  </servlet>
  <servlet-mapping>
  	<servlet-name>springmvc</servlet-name>
  	<!-- 
  		第一种:*.action,访问以*.action结尾的由DispatcherServlet解析
  		第二种:/,所有的访问都由DispatcherServlet解析,如要访问静态资源(js,css...)需要配置不让DispatcherServlet
  	解析,此方法可以实现RESTurl风格的url
  		第三种:/*,这种配置是不正确的,使用此方法,当我们要转发到一个jsp页面时也会由DispatcherServlet解析,会报错
  	 -->
  	<url-pattern>*.action</url-pattern>
  </servlet-mapping>
```

非注解的处理器映射器和适配器
==
在classpath下的springmvc.xml中

 **不使用注解的处理器适配器**
 ![不使用注解的处理器适配器的配置](http://img.blog.csdn.net/20160409095656438)
 
 此方法只能执行实现了Controller接口的Handler，下面是一个小demo
 
 **开发Handler**
 

```java
public class ItemsController1 implements Controller {
	@Override
	public ModelAndView handleRequest(HttpServletRequest request,
			HttpServletResponse response) throws Exception {
		
		//调用service查找 数据库，查询商品列表，这里使用静态数据模拟
		List<Items> itemsList = new ArrayList<Items>();
		//向list中填充静态数据
		
		Items items_1 = new Items();
		items_1.setName("联想笔记本");
		items_1.setPrice(6000f);
		items_1.setDetail("ThinkPad T430 联想笔记本电脑！");
		
		Items items_2 = new Items();
		items_2.setName("苹果手机");
		items_2.setPrice(5000f);
		items_2.setDetail("iphone6苹果手机！");
		
		itemsList.add(items_1);
		itemsList.add(items_2);

		//返回ModelAndView
		ModelAndView modelAndView =  new ModelAndView();
		//相当 于request的setAttribut，在jsp页面中通过itemsList取数据
		modelAndView.addObject("itemsList", itemsList);
		
		//指定视图
		modelAndView.setViewName("/WEB-INF/jsp/items/itemsList.jsp");
		return modelAndView;
}
```
setViewName()方法中是转发到的jsp页面，页面这里不再赘述，在这个jsp页面可以取到request域中的itemsList。
**在spring容器加载Handler**

```xml
<bean name="/queryItems.action" class="cn.jzl.ssm.controller.ItemsController1"></bean>
```
 **配置不使用注解的处理器映射器**
```xml
<!-- 
	将bean的name作为url进行查找，需要在配置Handler时指定beanname（就是url）
 -->
<bean class="org.springframework.web.servlet.handler.BeanNameUrlHandlerMapping"/>
```
**配置视图解析器**
 
```xml
<!-- 视图解析器 
		解析jsp,默认使用jstl,classpath下得有jstl的包
		jsp路径的前缀和jsp路径的后缀
	-->
	<bean class="org.springframework.web.servlet.view.InternalResourceViewResolver">
		<property name="prefix" value="/WEB-INF/jsp/"/>
		<property name="suffix" value=".jsp"/>
	</bean>
```

注解的处理器映射器和适配器
==

在spring3.1之前使用
org.springframework.web.servlet.mvc.annotation.DefaultAnnotationHandlerMapping注解映射器。

在spring3.1之后使用
org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping注解映射器。

在spring3.1之前使用
org.springframework.web.servlet.mvc.annotation.AnnotationMethodHandlerAdapter注解适配器。

在spring3.1之后使用
org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerAdapter注解适配器。

**配置注解映射器和适配器**

```xml
<!-- 注解映射器 -->
	<bean class="org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping" />
	<!-- 注解适配器 -->
	<bean class="org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerAdapter" />
```
**开发注解Handler**

```java
//使用Controller标识 它是一个控制器
@Controller
public class ItemsController {
	@Resource
	private ItemsService itemsService;
	//@RequestMapping实现 对queryItems方法和url进行映射，一个方法对应一个url
	//一般建议将url和方法写成一样
	@RequestMapping("/queryItems")
	public ModelAndView queryItems(ItemsQueryVo itemsQueryVo) throws Exception{
		/*
			业务逻辑
		*/
		List<ItemsCustom> itemsList = itemsService.findItemsList(itemsQueryVo);
		ModelAndView modelAndView = new ModelAndView();
		modelAndView.addObject("itemsList", itemsList);
		modelAndView.setViewName("items/itemsList");
		return modelAndView;
	}
}
```
@controller注解必须要加，作用标识类是一个Handler处理器。
@requestMapping注解必须要加，作用：
	1、对url和Handler的方法进行映射。
	2、可以窄化请求映射，设置Handler的根路径，url就是根路径+子路径请求方式
	3、可以限制http请求的方法
映射成功后，springmvc框架生成一个Handler对象，对象中只包括 一个映射成功的method。

**在spring容器中加载Handler**

```
<!-- 对于注解的Handler可以单个配置 -->
<!-- <bean class="cn.jzl.ssm.controller.ItemsController"/> -->
<!-- 但是在开发中，建议使用扫描 -->
<context:component-scan base-package="cn.jzl.ssm.controller" />
```
**配置视图解析器方法不变**

使用mvc:annotation-driven
==
**配置映射器和适配器**
使用如下配置，可以代替第二种方法中注解的适配器和映射器

```
<mvc:annotation-driven></mvc:annotation-driven>
```
**开发注解Handler**
	
	与第二种方法开发方法一致
	
**配置视图解析器方法不变**

## 小结 ##
 
   在学习并使用springmvc的过程中，了解其执行流程是非常重要的。在实际使用过程中会碰到各式各样的问题，也不是一篇博客或一部视频能够介绍完全的，所以学习没有捷径，只有通过一行行的代码累加、沉淀，多敲几行代码，理解就会加深几分。共勉。
