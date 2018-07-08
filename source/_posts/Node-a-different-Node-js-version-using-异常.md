---
title: Node - a different Node.js version using 异常
date: 2018-07-08 08:54:51
tags: ["node"]
categories: "技术杂谈"
---
今天在更新博客的时候，突然报了异常，

```
Error: The module '/usr/local/lib/node_modules/hexo-cli/node_modules/dtrace-provider/build/Release/DTraceProviderBindings.node'
was compiled against a different Node.js version using
NODE_MODULE_VERSION 57. This version of Node.js requires
NODE_MODULE_VERSION 59. Please try re-compiling or re-installing
the module (for instance, using `npm rebuild` or `npm install`).
    at Object.Module._extensions..node (module.js:689:18)
    at Module.load (module.js:573:32)
    at tryModuleLoad (module.js:513:12)
    at Function.Module._load (module.js:505:3)
    at Module.require (module.js:604:17)
    at require (internal/module.js:11:18)
    at Object.<anonymous> (/usr/local/lib/node_modules/hexo-cli/node_modules/dtrace-provider/dtrace-provider.js:18:23)
    at Module._compile (module.js:660:30)
    at Object.Module._extensions..js (module.js:671:10)
    at Module.load (module.js:573:32)
    at tryModuleLoad (module.js:513:12)
    at Function.Module._load (module.js:505:3)
    at Module.require (module.js:604:17)
    at require (internal/module.js:11:18)
    at Object.<anonymous> (/usr/local/lib/node_modules/hexo-cli/node_modules/bunyan/lib/bunyan.js:79:18)
    at Module._compile (module.js:660:30)
```
看样子是有一个模块因为被不同版本的node给build了，估计是前一阵子更新mac系统版本的时候更新了node版本。
关于node我也不是很懂，只能求助于谷歌- -
最后终于找到了一个暴力的解决方法：
1、cd 到 /usr/local/lib/node_modules/hexo-cli/
2、干掉node_modules文件夹
3、npm install
4、cd 到 hexo_project
5、干掉node_modules文件夹
6、npm install

搞定 收工~