---
title: quartz的misfire策略
date: 2017-11-30 14:01:52
tags: ["quartz"]
categories: "JavaUtils"
---
quartz框架中提供了一系列misfire策略，是指任务因为某种原因错过了执行，可以根据不同任务需求定制不同的策略。

## without repeating (不重复的任务)

这是一个在2017-11-30 11:25:00执行的任务，距离我写此篇文章的时候已经过去了十分钟左右，所以一定会出发misfire策略

```Java
SimpleTrigger simpleTrigger = TriggerBuilder.newTrigger()
    .withIdentity("helloworld-trigger-name-1", "helloworld-trigger-group-1")
    .withSchedule(SimpleScheduleBuilder.simpleSchedule())
    .startAt(new Date(1512012300000L))
    .build();
```

**withMisfireHandlingInstructionFireNow**

错过之后马上执行

**withMisfireHandlingInstructionNextWithRemainingCount**

错过之后忽略

## repeating fixed number of times (多次执行)

这是一个在2017-11-30 12:00:00执行的任务，共执行5次，每次间隔1个小时的任务
```Java
SimpleTrigger simpleTrigger = TriggerBuilder.newTrigger()
    .withIdentity("helloworld-trigger-name-1", "helloworld-trigger-group-1")
    .withSchedule(SimpleScheduleBuilder.simpleSchedule()
            .withRepeatCount(5)
            .withIntervalInHours(1))
    .startAt(1512014400000L)
    .build();
```

**withMisfireHandlingInstructionFireNow**

错过之后，恢复正常时马上执行，总次数还是5次，假如在12:15:00分时执行了misfire，则以后每次执行都会在15分时执行，会执行到16:15:00。

**withMisfireHandlingInstructionNowWithExistingCount**

如果13:00:00错过执行，13:15:00恢复执行，则将清空已执行次数，总的执行次数为6，会执行到17:15:00。

**withMisfireHandlingInstructionNextWithRemainingCount**

错过之后忽略，do nothing， 总次数还是5次

## reapting forever (重复执行)

会在2017-11-30 12:00:00开始第一次执行，并每隔1个小时重复执行下去

```Java
SimpleTrigger simpleTrigger = TriggerBuilder.newTrigger()
    .withIdentity("helloworld-trigger-name-1", "helloworld-trigger-group-1")
    .withSchedule(SimpleScheduleBuilder.simpleSchedule()
            .repeatForever()
            .withIntervalInHours(1))
    .startAt(1512014400000L)
    .build();
```
**withMisfireHandlingInstructionFireNow**

每次错过后，在下一个失效节点执行

**withMisfireHandlingInstructionNextWithRemainingCount**

每次错过后，在下个定义的时间点执行

## Cron triggers (cron表达式执行)

这是一个会在每天下午两点到五点每隔一小时执行的任务
```Java
CronTrigger cronTrigger = TriggerBuilder.newTrigger()
    .withIdentity("helloworld-trigger-name-" + i, "helloworld-trigger-group-1")
    .withSchedule(CronScheduleBuilder.cronSchedule("00 00 14-17 * * ?"))
    .build();
```

**withMisfireHandlingInstructionIgnoreMisfires**

所有错过的任务马上执行

**withMisfireHandlingInstructionDoNothing**

所有错过的任务忽略

**withMisfireHandlingInstructionFireAndProceed**

合并错过的任务，如14点和15点的任务错过，只会执行一次misfire，下次整点继续执行。
