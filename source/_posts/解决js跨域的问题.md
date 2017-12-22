---
title: 解决js跨域的问题
date: 2017-10-08 10:28:13
tags: [js, 跨域]
categories: 技术杂谈
---
## 什么是跨域？ ##
Js为了安全有一个限制，不允许跨域访问。
1、如果两个url的域名不同
2、Url相同，端口不同也是跨域
3、Ip不同也是跨域
## 解决方法 ##

方法的原理
=====
可以使用jsonp解决跨域的问题。
1、在js中不能跨域请求数据，js可以跨域请求js片段。
2、可以把数据包装成js片段。可以把数据使用js方法来包装，形成一条方法的调用语句。
3、可以使用ajax请求js片段，当js判断到达浏览器会被立即执行。
4、在浏览器端，先创建好回调方法，在回调方法中通过参数可以获得请求的数据。
![原理](http://img.blog.csdn.net/20160417223133628)

前期准备
====

1、需要把js的回调方法先写好。
2、做ajax请求时，需要把回调方法的方法名传递给服务端。
3、服务端接收回调方法名，把数据包装好，响应给客户端。

## 例子 ##
首先，在客户端要把回调方法写好，简单的说就是假设你已经取到了数据，哪些方法要用到这些数据先写好。
假设一个click事件:

```js
var url = "http://localhost:8081/data.json?callback=getDataService";
$("#button").click(function(){
	$.getJSONP(url);
	//或者是$.getJSONP(url,getDataService),一定要用$.getJSONP，使用$.getJSON还是会遇到无法跨域请求的问题。
});
getDateService(data){
	//取得数据，执行业务逻辑
}
```
在服务端：
原始json数据为：

```json
{
    "data": [
        {
            "k": "key",
            "v": "value"
        }
    ]
}
```
这时候要将回调函数加到原始的json数据中，将服务端中json数据改为：

```
getDataService({
    "data": [
        {
            "k": "key",
            "v": "value"
        }
    ]
}};
```
将原始json数据包装成js片段。此时当包装后的js片段到达浏览器时会自动执行。这里的getDataService就是浏览器端要执行的函数名。
