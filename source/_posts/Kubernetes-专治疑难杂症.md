---
title: Kubernetes - 专治疑难杂症
date: 2017-11-27 16:14:26
tags: ["kubernetes"]
categories: "DevOps"
---
- 使用kubectl logs 出现 failed to create fsnotify watcher: too many open files
这是因为系统默认的fs.inotify.max_user_instances=128太小，重新设置此值：

```shell
sudo sysctl fs.inotify.max_user_instances=8192
```
