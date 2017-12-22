---
title: 在web项目中应用Mybatis
date: 2017-10-08 10:31:12
tags: [Mybatis, web]
categories: Spring
---
## mybatis环境准备 ##

 1. 加入所需jar包
 ![](http://img.blog.csdn.net/20160404111830053)
 工程结构
 ![](http://img.blog.csdn.net/20160404111855553)
 
 所需jar包，博主有上传资源
 http://download.csdn.net/detail/jinzili777/9480604

**在开始之前我们有必要了解mybatis执行流程:** 

①SqlMapConfig.xml（是mybatis的全局配置文件，名称不固定的）配置了数据源、事务等mybatis运行环境、配置映射文件（配置sql语句）
mapper.xml（映射文件）、mapper.xml、mapper.xml.....

②SqlSessionFactory（会话工厂），根据配置文件创建工厂
作用：创建SqlSession

③SqlSession（会话），是一个接口，面向用户（程序员）的接口
作用：操作数据库（发出sql增、删、改、查）

④Executor（执行器），是一个接口（基本执行器、缓存执行器）
作用：SqlSession内部通过执行器操作数据库

⑤mapped statement（底层封装对象）
作用：对操作数据库存储封装，包括 sql语句，输入参数、输出结果类型
## SqlMapConfig.xml ##

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE configuration
PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
"http://mybatis.org/dtd/mybatis-3-config.dtd">
<configuration>
	<!-- 加载属性文件 -->
	<properties resource="db.properties">
		<!-- properties中还可以配置一些属性名和属性值,但不建议在这里添加任何属性 -->
	</properties>
	<!-- 全局配置 -->
	<settings>
		<!-- 打开延迟加载的开关 -->
		<setting name="lazyLoadingEnabled" value="true"/>
		<!-- 将积极加载改为消极加载即按需加载 -->
		<setting name="aggressiveLazyLoading" value="false"/>
	</settings>
	<!-- 别名定义 -->
	<typeAliases>
		<!-- 
			type:类型路径
			alias:别名 
		
		<typeAlias type="cn.jzl.mybatis.po.User" alias="user"/>
		 -->
		<!-- 批量别名定义
			指定包名:mybatis自动扫描包中的po类,自动定义别名
			别名就是类名(首字母大小写都可以)
		 -->
		 <package name="cn.jzl.mybatis.po"/>
	</typeAliases>
	<environments default="development">
		<environment id="development">
			<transactionManager type="JDBC" />
			<dataSource type="POOLED">
				<property name="driver" value="${jdbc.driver}" />
				<property name="url" value="${jdbc.url}" />
				<property name="username" value="${jdbc.username}" />
				<property name="password" value="${jdbc.password}" />
			</dataSource>
		</environment>
	</environments>
	<!-- 加载映射文件 -->
	<mappers>
		<mapper resource="sqlmap/User.xml" />
		<!-- 加载单个mapper 
		<mapper resource="mapper/UserMapper.xml" />-->
		<!-- mapper接口加载
		<mapper class="cn.jinzili.mybatis.mapper.UserMapper"/>
		 -->
		 <!-- 批量加载 -->
		 <package name="cn.jinzili.mybatis.mapper"/>
	</mappers>
</configuration>
```
**db.properties**

```
jdbc.driver=com.mysql.jdbc.Driver
jdbc.url=jdbc:mysql://localhost:3306/mybatis?characterEncoding=utf-8
jdbc.username=root
jdbc.password=111111
```
**log4j.properties**

```
# Global logging configuration
log4j.rootLogger=DEBUG, stdout
# MyBatis logging configuration...
log4j.logger.org.mybatis.example.BlogMapper=TRACE
# Console output...
log4j.appender.stdout=org.apache.log4j.ConsoleAppender
log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
log4j.appender.stdout.layout.ConversionPattern=%5p [%t] - %m%n
```
## mybatis开发dao ##

 1. 开发原始dao的方法
 ①dao接口
```javaweb
public interface UserDao {
	//根据id查询用户信息
	public User findUserById(int id) throws Exception;
}
```
②dao接口实现类

```javaweb
public class UserDaoImpl implements UserDao{
	
	//需要向dao实现类中SqlSessionFactory
	//通过构造函数注入
	private SqlSessionFactory sqlSessionFactory;
	public UserDaoImpl(SqlSessionFactory sqlSessionFactory){
		this.sqlSessionFactory = sqlSessionFactory;
	}
	@Override
	public User findUserById(int id) throws Exception {
		SqlSession sqlSession = sqlSessionFactory.openSession();
		User user = sqlSession.selectOne("test.findUserById", id);
		sqlSession.close();
		return user;
	}
}
```
③测试代码

```javaweb
public class UserDaoImplTest {
	//创建sqlSessionFactory
	private SqlSessionFactory sqlSessionFactory;
	@Before
	public void setUp() throws Exception{
		//加载mybatis配置文件
		String resource = "SqlMapConfig.xml";
		//得到配置文件流
		InputStream inputStream = Resources.getResourceAsStream(resource);
		//创建会话工厂,传入mybatis的配置文件信息
		sqlSessionFactory = new SqlSessionFactoryBuilder().build(inputStream);
	}
	@Test
	public void testFindUserById() throws Exception {
		//创建UserDao的对象
		UserDao userDao = new UserDaoImpl(sqlSessionFactory);
		//调用UserDao的方法,并打印
		System.out.println(userDao.findUserById(1));
	}

}
```
**测试结果**
![](http://img.blog.csdn.net/20160404112854182)

 2. mapper代理方法
 ①mapper.java
 
```javaweb
public interface UserMapper {
	public User findUserById(int id) throws Exception;
}
```
②mapper.xml

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper
PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
"http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<!-- 
	namespace命名空间，作用就是对sql进行分类管理，理解为sql隔离 
	注意：使用mapper代理方法开发，namespace有特殊重要的作用
 -->
<mapper namespace="cn.jinzili.mybatis.mapper.UserMapper">
<!-- 在映射文件中配置很多sql语句 -->
	<!-- 
		通过select执行数据库查询
		id：标识映射文件中的sql，将sql语句封装到mappedStatement对象中，称为statement的id
	 	parameterType:指定输入参数的类型 ,这里指定int型
	 	#{id}:其中的id标识接收输入的参数，参数名称是id，如果输入参数是简单类型，#{}中的参数吗可以任意
		resultType:指定sql输出结果的所映射的java对象类型,select指定resultType表示将单条记录映射成的java对象
	 -->
	 <select id="findUserById" parameterType="int" resultType="user">
	 	SELECT * FROM USER WHERE id=#{id}
	 </select>
</mapper>
```
③在SqlMapConfig.xml文件加载mapper.xml

```xml
<!-- 加载映射文件 -->
	<mappers>
		<mapper resource="sqlmap/User.xml" />
		<!-- 加载单个mapper 
		<mapper resource="mapper/UserMapper.xml" />-->
		<!-- mapper接口加载
		<mapper class="cn.jinzili.mybatis.mapper.UserMapper"/>
		 -->
		 <!-- 批量加载,建议用此方法 -->
		 <package name="cn.jinzili.mybatis.mapper"/>
	</mappers>
```
④测试代码

```javaweb
public class UserMapperTest {
	private SqlSessionFactory sqlSessionFactory;
	@Before
	public void setUp() throws Exception{
		String resource = "SqlMapConfig.xml";
		InputStream inputStream = Resources.getResourceAsStream(resource);
		sqlSessionFactory = new SqlSessionFactoryBuilder().build(inputStream);
	}
	@Test
	public void testFindUserById() throws Exception {
		SqlSession sqlSession = sqlSessionFactory.openSession();
		//创建UserMapper对象,mybatis自动生成mapper代理对象
		UserMapper userMapper = sqlSession.getMapper(UserMapper.class);
		User user = userMapper.findUserById(1);
		sqlSession.close();
		System.out.println(user);
	}
}
```
![](http://img.blog.csdn.net/20160404113857780)
如果mapper方法返回单个pojo对象（非集合对象），代理对象内部通过selectOne查询数据库。
如果mapper方法返回集合对象，代理对象内部通过selectList查询数据库。

## 总结 ##
在此博客中，只介绍了mybatis最简单的使用方法，适合初学者快速入门，但是想要深入了解mybatis，还需要大家一起努力（推荐看一些mybatis的培训视频）。