---
title: quartz集群配置
date: 2017-10-19 15:14:27
tags: [quartz]
categories: "Java Framework"
---
# JobStore
在开始配置quartz集群之前，先要了解一下Scheduler的“工作数据”的存放点：
## RAMJobStore
RAMJobStore是最简单最高效，也是quartz默认的存储方式，它将“工作数据”存放在内存中，所以它无需任何额外配置，也是最高效的原因。但是这种方式的弊端也是显而易见的：

- 任务量受限于内存大小
- 当系统崩溃时，就丢掉了所有任务信息，这对于一些程序是灾难性的
- 无法集群化

## JDBCJobStore
看到JDBC我们就应该已经知道了，这种方式是将“工作数据”存储到了数据库中并且广泛适用于所有数据库，这既有利：
- 任务量没有限制
- 持久化任务信息
- 可集群化
- 失败转移(fail-over, 集群化情况下，其中一台系统崩溃会自动将任务转移到其他可用系统上)

也有弊：
- 没有RAMJobStore方式高效
- 增大数据库压力

相比之下，利远大于弊，所以一般使用quartz框架都使用JDBCJobStore这种方式。
### 两种事务管理方式
quartz提供了两种事务管理方式：
#### JobStoreTX
quartz框架自己管理事务，这是最常用的方式
#### JobStoreCMT
将quartz框架的事务集成到J2EE容器事务中。

# quartz.properties
程序启动时，会默认读取classpath下的quartz.properties，所以我们将配置都写在此文件中：

```
# 在同一个项目中name不同（用来区分scheduler）, 在集群中name相同
quartz.scheduler.instanceName=myScheduler
#org.quartz.jobStore.dataSource=myDS
#org.quartz.dataSource.myDS.driver=com.mysql.cj.jdbc.Driver
#org.quartz.dataSource.myDS.URL=jdbc:mysql://localhost:3306/quartzdb?useUnicode=true&characterEncoding=utf8
#org.quartz.dataSource.myDS.user=root
#org.quartz.dataSource.myDS.password=root
#org.quartz.dataSource.myDS.maxConnections=10

# 可以为任意字符串, 但必须保持唯一, AUTO 自动生成ID, SYS_PROP使用系统环境变量${org.quartz.scheduler.instanceId}
org.quartz.scheduler.instanceId=AUTO
# 是否跳过更新检查
org.quartz.scheduler.skipUpdateCheck=true
# 是否打开quartz的JMX支持
org.quartz.scheduler.jmx.export=true
# jobStore类配置
org.quartz.jobStore.class=org.quartz.impl.jdbcjobstore.JobStoreTX
# 通过JDBC访问数据库的代理类
org.quartz.jobStore.driverDelegateClass=org.quartz.impl.jdbcjobstore.StdJDBCDelegate
# quartz数据表前缀
# org.quartz.jobStore.tablePrefix=T_B_QRTZ_
# 是否使用集群
org.quartz.jobStore.isClustered=true
# 集群状态的更新时间间隔
org.quartz.jobStore.clusterCheckinInterval=20000
# 最大错误重试次数
org.quartz.jobStore.maxMisfiresToHandleAtATime=1
# 在Trigger被认为是错误触发之前, scheduler还容许Trigger通过它的下次触发时间的秒数, 默认60000
org.quartz.jobStore.misfireThreshold=120000
# 调用setTransactionIsolation(Connection.TRANSACTION_SERIALIZABLE)方法设置事务级别
org.quartz.jobStore.txIsolationLevelSerializable=true
# 必须为一个sql字符串, 查询locks表里的一行, {0}被覆盖为tablePrefix ? 被覆盖为scheduler's name
org.quartz.jobStore.selectWithLockSQL=SELECT * FROM {0}LOCKS WHERE LOCK_NAME = ? FOR UPDATE

# 使用的线程池实例
org.quartz.threadPool.class=org.quartz.simpl.SimpleThreadPool
# 线程池中线程数, 很大取决于任务的性质和系统资源
org.quartz.threadPool.threadCount=10
# 线程的优先级, 介于Thread.MIN_PRIORITY(1)和Thread.PRIORITY(10), 默认Thread.NORM_PRIORITY(5)
org.quartz.threadPool.threadPriority=5
# 加载任务代码的ClassLoader是否从外部继承
org.quartz.threadPool.threadsInheritContextClassLoaderOfInitializingThread=true
# trigger历史记录插件
org.quartz.plugin.triggHistory.class=org.quartz.plugins.history.LoggingJobHistoryPlugin
# shutdown-hook 插件捕捉JVM关闭时间并调用scheduler的shutdown方法
org.quartz.plugin.shutdownhook.class=org.quartz.plugins.management.ShutdownHookPlugin
org.quartz.plugin.shutdownhook.cleanShutdown=true
```
在这里我注释掉了关于数据库连接信息的配置，决定在quartConfig.java文件中注入dataSource。

# SpringJobFactoryConfig.java
在Job执行类中，无法注入Spring容器中的bean，因为Spring容器和quartz容器是隔离开的，所以我们需要使用Spring提供的AutowireCapableBeanFactory（可装配applicationContext之外的bean）和重写AdaptableJobFactory中的createJobInstance方法。


```java
/**
 * TODO 自定义JobFactory, 为了注入jobInstance中的@Autowired @Resource等实例
 * Created by jinzili on 25/09/2017.
 */
@Component
public class SpringJobFactoryConfig extends AdaptableJobFactory{

    // 装配applicationContext管理之外的bean
    @Autowired
    private AutowireCapableBeanFactory capableBeanFactory;

    @Override
    protected Object createJobInstance(TriggerFiredBundle bundle) throws Exception {
        Object jobInstance = super.createJobInstance(bundle);
        // 装配jobInstance
        capableBeanFactory.autowireBean(jobInstance);
        return jobInstance;
    }
}
```
# QuartzConfig.java
将自定义的JobFactory配置到SchedulerFactoryBean和Scheduler：

```java
@Configuration
public class QuartzConfig {

    @Autowired
    private SpringJobFactoryConfig springJobFactory;

    @Qualifier("dataSource")
    @Autowired
    private DataSource dataSource;

    @Bean
    public SchedulerFactoryBean schedulerFactoryBean(){
        SchedulerFactoryBean factory = new SchedulerFactoryBean();
        // 是否覆盖已存在的job
        factory.setOverwriteExistingJobs(true);
        // 配置数据源
        System.out.println(dataSource);
        factory.setDataSource(dataSource);
        // 启动延时
        factory.setStartupDelay(10);
        // 是否自动启动
        factory.setAutoStartup(true);
//        factory.setQuartzProperties(this.quartzProperties());
        factory.setApplicationContextSchedulerContextKey("applicationContext");
        // 配置自定义JobFactory
        factory.setJobFactory(springJobFactory);
        return factory;
    }

    @Bean
    public Scheduler scheduler(){
        return schedulerFactoryBean().getScheduler();
    }

}
```

在其他bean中通过注入scheduler来增删改查Job。

至此，一个有可持久化，集群化，失败转移的功能的quartz框架就搭建好了。
