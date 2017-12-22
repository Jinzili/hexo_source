---
title: quartz基础详解
date: 2017-10-17 18:40:41
tags: [quartz]
categories: "JavaUtils"
---
# quartz基础知识
## Job
要想让quartz来管理任务，就必须要遵守quartz的规。Job类需要实现org.quartz.Job接口，重写接口中唯一的exceute(JobExecutionContext jec)方法，在这个方法中实现具体的业务逻辑。JobExecutionContext保存了任务执行时的上下文，比如执行的是哪个trigger，也包括了执行时的数据信息等。定义一个Job：

```java
public static class JobImpl implements Job{
    @Override
    public void execute(JobExecutionContext jobExecutionContext) throws JobExecutionException {
        // do some thing... 
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        System.out.println(sdf.format(new Date()));
    }
}
```

## JobDetail
JobDetail接口定义了用来描述一个job所有的属性信息，下面列出一些核心属性：

属性 | 说明
---|---
class | Job实现类，jobDetail根据此获取Job实例
name | Job名称，同一Job组中名称唯一
group | Job组名, 同一scheduler容器中组名唯一
description | Job描述信息
durability | 是否持久化。如果非持久化，当没有trigger与之关联，则会被自动删除。
shouldRecover | 是否可恢复。如果可恢复，那么job执行中，scheduler崩溃，当scheduler重启后，此job会被重新执行。
jobDataMap | 可把任意kv数据存入此属性，支持序列化实现了Serialiable接口，key=String, value=Object。
定义一个JobDetail：

```java
// 定义一个job
JobDetail jobDetail = JobBuilder.newJob(JobImpl.class)
        .withIdentity("myJob", "myJobGroup")
        .build();
```

## Trigger
quartz提供了多种触发器，他们是Trigger的具体实现。其中经常使用的有两种：SimpleTrigger和CronTrigger。
### SimpleTrigger
SimpleTrigger包含几个特点：开始时间、结束时间、重复次数和重复间隔。结束时间会覆盖重复次数，比如某触发器已到结束时间但是未达到重复次数也会停止执行。如果任务符合这种工作性质，那么使用SimpleTrigger这种触发器最适合。定义一个SimpleTrigger:

```java
 // 定义一个trigger
Trigger trigger = TriggerBuilder.newTrigger()
        .withIdentity("myTrigger", "myTriggerGroup")
        .startNow()
        .withSchedule(SimpleScheduleBuilder.simpleSchedule()
                .withIntervalInSeconds(5)
                .repeatForever())
        .build();
```
这个Trigger立即开始并每5秒无限循环执行。
SimpleTrigger提供了许多执行策略，比如：未来5分钟开始执行、偶数小时执行等，需要在不同业务逻辑中不同配置。
**自定义失败重试策略**

策略 | 含义
---|---
REPEAT_INDEFINITELY | 不断重复直到结束时间戳
MISFIRE_INSTRUCTION_FIRE_NOW | 如果失败立即再次触发
MISFIRE_INSTRUCTION_RESCHEDULE_NOW_WITH_EXISTING_REPEAT_COUNT | 如果失败立即再次触发，重试次数+1，遵守结束时间戳
MISFIRE_INSTRUCTION_RESCHEDULE_NOW_WITH_REMAINING_REPEAT_COUNT | 如果失败立即再次触发，遵守结束时间戳
MISFIRE_INSTRUCTION_RESCHEDULE_NEXT_WITH_REMAINING_COUNT | 如果失败，则到下次触发时间再执行

### CronTrigger
CronTrigger触发器用的更多一下，这个触发器基于日历的概念，而不是具体开始时间，具体结束时间，重复次数等。你可以指定每周一凌晨2点执行，每月每周一执行等复杂逻辑。使用此触发器需要了解Cron表达式，这里不在赘述。定义一个CronTrigger：

```java
CronTrigger cronTrigger = TriggerBuilder.newTrigger()
    .withIdentity("helloworld-trigger-name-1", "helloworld-trigger-group-1")
    .withSchedule(CronScheduleBuilder.cronSchedule("0/5 * * ? * *"))
    .startNow()
    .build();
```
**自定义失败重试策略**

策略 | 含义
---|---
MISFIRE_INSTRUCTION_FIRE_ONCE_NOW | 如果失败立即再次触发
MISFIRE_INSTRUCTION_DO_NOTHING | 如果失败则到下次执行时间再次触发

## Scheduler容器
一个Scheduler容器对应一个quartz独立的运行容器，在Scheduler容器中，将Trigger绑定到JobDetail上，由Scheduler调度执行。

**一个Trigger对应一个JobDetail，一个JobDetail可对应多个Trigger。**

Scheduler容器以键值对的形式保存了任务执行时的上下文信息，还提供了多个接口方法，允许外部通过组名及任务名或触发器名访问容器中的JobDetail或Trigger，定义一个Scheduler：

```java
Scheduler scheduler = StdSchedulerFactory.getDefaultScheduler();
```
注册一个可执行的任务到Scheduler容器中：

```java
scheduler.scheduleJob(jobDetail, trigger);
```
一个可执行的任务需要一个JobDetail和一个Trigger，这个很好理解，一个任务需要任务的描述信息，和一个触发任务执行的策略。quartz将任务和触发器解耦，这样我们就可以实现一个任务对应多个触发器。

## 一个简单demo
因为quartz的是多线程执行的，所以我们在main方法里测试而不是使用JUnit。
```java
/**
 * TODO quartz simple demo
 * Created by jinzili on 17/10/2017.
 */
public class QuartzController {

    public static class JobImpl implements Job{

        @Override
        public void execute(JobExecutionContext jobExecutionContext) throws JobExecutionException {
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
            System.out.println(sdf.format(new Date()));
        }

    }

    public static void main(String[] args) throws SchedulerException{
        Scheduler scheduler = StdSchedulerFactory.getDefaultScheduler();

        // 定义一个jobDetail
        JobDetail jobDetail = JobBuilder.newJob(JobImpl.class)
                .withIdentity("myJob", "myJobGroup")
                .build();

        // 定义一个trigger
        Trigger trigger = TriggerBuilder.newTrigger()
                .withIdentity("myTrigger", "myTriggerGroup")
                .startNow()
                .withSchedule(SimpleScheduleBuilder.simpleSchedule()
                        .withIntervalInSeconds(5)
                        .repeatForever())
                .build();


        scheduler.scheduleJob(jobDetail, trigger);
        scheduler.start();
    }

}
```





