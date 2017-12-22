---
title: WebSocket实现即时聊天室
date: 2017-10-07 09:39:09
tags: [WebSocket, online, 聊天室]
categories: 技术杂谈
---
原理
==
很多网站为了实现即时聊天，使用的是轮询方式（在特定的时间间隔，由浏览器向服务器端发出 Http request，然后由服务器返回最新的数据）实现。这种传统的 Http request的方式有个明显的缺点，浏览器需要不断的向服务器发出请求，然而HTTP request 的header是非常长的，里面包含的有用数据可能只是一个很小的值，这样会占用很多的带宽。
比较新的方式是Comet---用了Ajax，但是还是要发出请求。
但是在WebSocket API中，浏览器和服务器只需要做一个握手的动作，然后，浏览器和服务器之间就形成了一条快速通道。两者之间就直接可以数据互相传送。这样做的两大好处是
1. Header
互相沟通的Header是很小的-大概只有 2 Bytes
2. Server Push
服务器的推送，服务器不再被动的接收到浏览器的request之后才返回数据，而是在有新数据时就主动推送给浏览器。

开发基于WebSocket协议的聊天室
==

开发环境
--
MyEclipse2014、JDK1.7.45 64位、Tomcat8

WebSocketConfig
--

```java
package com.sx2.websocket;

import java.util.Set;

import javax.websocket.Endpoint;
import javax.websocket.server.ServerApplicationConfig;
import javax.websocket.server.ServerEndpointConfig;
/**
 * 
 * @author Jin
 *	在Tomcat启动的时候会加载此类(因为实现了ServerApplicationConfig接口)
 */
public class WebSocketConfig implements ServerApplicationConfig{

	@Override
	public Set<Class<?>> getAnnotatedEndpointClasses(Set<Class<?>> scan) {
		/*
		 * 这里会自动扫描带有@ServerEndpoint注解的类
		 * 返回它们的类名集合,这里可以做一些过滤,比如过滤测试用的带有@ServerEndpoint注解的类
		 * 最后一定要返回过滤后的set集合,相当于注册服务
		 * 最后一定要返回过滤后的set集合,相当于注册服务
		 * 最后一定要返回过滤后的set集合,相当于注册服务
		 */
		return scan;
	}

	@Override
	public Set<ServerEndpointConfig> getEndpointConfigs(
			Set<Class<? extends Endpoint>> arg0) {
		return null;
	}

}

```

chatSocket.java
--

```java

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;
import javax.websocket.OnClose;
import javax.websocket.OnMessage;
import javax.websocket.OnOpen;
import javax.websocket.Session;
import javax.websocket.server.ServerEndpoint;

import com.alibaba.fastjson.JSONObject;
import com.sx2.pojo.WebSocketResult;

/**
 * 
 * @author Jin
 * 这里带有@ServerEndpoint注解,会自动被扫描到
 */
@ServerEndpoint("/chatSocket")
public class ChatSocket {
	//所有的实例的集合
	private  static  Set<ChatSocket>  sockets=new HashSet<ChatSocket>();
	//保存每个username对应的用户头像,这里只是这个项目中需要,如果实际项目中不需要,此变量无用
	private static Map<String, String> photos = new HashMap<String, String>();
	//保存每个用户的用户名
	private  static  Set<String>   names=new HashSet<String>();
	//每个用户进入聊天室,都会开启一个session,要注意的是这里的session是javax.websocket.Session
	private  Session  session;
	//当有用户进入聊天室时,保存用户名
	private String username;
	//当有用户进入聊天室时,保存用户头像,不是必须的
	private String photo;
	
	/**
	 * 每当有用户进入聊天室时,都会执行一次此函数
	 * @param session
	 */
	@OnOpen
	public  void open(Session  session){
			this.session=session;
			sockets.add(this);
			//这里的逻辑是得到请求路径后的参数
			//比如:ws://localhost:8080/SX2/chatSocket?username=jin&photo=/image/user/b3.png",那么queryString就是username=jin&photo=/image/user/b3.png
			//username为用户的用户名,是必须的。photo为用户的头像,看实际需要并不是必须的
			String  queryString = session.getQueryString();
			//对得到queryString进行切割,得到用户名和头像
			String[] infos = queryString.split("&");
			this.username = infos[0].substring(infos[0].indexOf("=") + 1);
			this.photo = infos[1].substring(infos[1].indexOf("=") + 1);
			//WebSocket返回值的包装类
			WebSocketResult message = new WebSocketResult();
			String encodeUsername = "";
			try {
				if(this.username.matches("[A-Za-z]")){   //如果用户的用户名是纯英文,比如Tom,Jerry,不用编码
					encodeUsername = this.username;
				}else{									 //如果用户的用户名不是纯英文的,则需要编码
					encodeUsername = URLDecoder.decode(this.username,"UTF-8");
				}
				this.username = encodeUsername;
				//将经过处理的用户名,添加到用户名集合中
				names.add( encodeUsername);
				//将用户名集合放到返回值中
				message.setNames(names);
				
				photos.put(encodeUsername, photo);
				message.setPhotos(photos);
				//将欢迎信息放到返回值中
				message.setWelCome(encodeUsername+"进入聊天室！！");
				//将返回值的包装类转为json字符串,向所有人打印欢迎信息。
				broadcast(sockets, JSONObject.toJSONString(message));
			} catch (UnsupportedEncodingException e1) {
				// TODO Auto-generated catch block
				message.setWelCome("服务器异常!");
				broadcast(sockets, JSONObject.toJSONString(message));
			}
			
			
	}
	@SuppressWarnings("deprecation")
	/**
	 * 当有用户发送消息时,会执行此函数
	 * @param session  为此用户开启的session
	 * @param msg 用户发送的消息文本
	 */
	@OnMessage
	public  void receive(Session  session,String msg ){
		
		WebSocketResult  message=new WebSocketResult();
		//将消息文本放到返回值中
		message.setSendMsg(msg);
		//将来自哪个用户放到返回值中
		message.setFrom(this.username);
		//将发送日期放到返回值中
		message.setDate(new Date().toLocaleString());
		//用户头像
		message.setPhotos(photos);
		//向所有人打印发送的消息
		broadcast(sockets, JSONObject.toJSONString(message));
	}
	
	/**
	 * 
	 * @param session 为此用户开启的session
	 */
	@OnClose
	public  void close(Session session){
		//从实例集合中移除此实例
		sockets.remove(this);
		//从用户名集合中移除此用户名
		names.remove(this.username);
		//从头像集合中移除此用户的头像
		photos.remove(this.username);
		WebSocketResult   message=new WebSocketResult();
		//将欢送消息放到返回值中
		message.setWelCome(this.username+"退出聊天室！！");
		//重新设置用户名集合
		message.setNames(names);
		//重新设置头像集合
		message.setPhotos(photos);
		//向所有人打印欢送消息
		broadcast(sockets, JSONObject.toJSONString(message));
	}
	/**
	 * 
	 * @param ss 所有实例集合
	 * @param msg 要向浏览器端发送的json字符串
	 */
	public void broadcast(Set<ChatSocket>  ss ,String msg ){
		
		for (Iterator<ChatSocket> iterator = ss.iterator(); iterator.hasNext();) {
			ChatSocket chatSocket = (ChatSocket) iterator.next();
			try {
				//使用session的getBasicRemote方法向浏览器端发送json字符串
				chatSocket.session.getBasicRemote().sendText(msg);
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
	}
}

```
WebSocketResult.java

```java
import java.util.Map;
import java.util.Set;
/**
 * 
 * @author Jin
 * WebSocket返回值的包装类
 */
public class WebSocketResult {

	
	private String sendMsg;
	
	private String date;
	
	private String from;
	
	private String welCome;
	
	private Set<String> names;

	private Map<String, String> photos;
	
	public String getWelCome() {
		return welCome;
	}

	public void setWelCome(String welCome) {
		this.welCome = welCome;
	}

	public String getSendMsg() {
		return sendMsg;
	}

	public void setSendMsg(String sendMsg) {
		this.sendMsg = sendMsg;
	}

	public String getDate() {
		return date;
	}

	public void setDate(String date) {
		this.date = date;
	}

	public String getFrom() {
		return from;
	}

	public void setFrom(String from) {
		this.from = from;
	}

	public Set<String> getNames() {
		return names;
	}

	public void setNames(Set<String> names) {
		this.names = names;
	}

	public Map<String, String> getPhotos() {
		return photos;
	}

	public void setPhotos(Map<String, String> photos) {
		this.photos = photos;
	}
}

```

客户端代码
--

```html
<?xml version="1.0" encoding="UTF-8"?>

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
    <title>Apache Tomcat WebSocket Examples: Chat</title>
    <style type="text/css">
        input#chat {
            width: 410px
        }

        #console-container {
            width: 400px;
        }

        #console {
            border: 1px solid #CCCCCC;
            border-right-color: #999999;
            border-bottom-color: #999999;
            height: 170px;
            overflow-y: scroll;
            padding: 5px;
            width: 100%;
        }
		#userlist {
            border: 1px solid #CCCCCC;
            border-right-color: #999999;
            border-bottom-color: #999999;
            height: 170px;
            overflow-y: scroll;
            padding: 5px;
            width: 100%;
        }
        p {
            padding: 0;
            margin: 0;
        }
   </style>
   <script type="application/javascript">
	   //这里的target就是websocket服务的路径
	   //对应于@ServerEndpoint("/chatSocket")
	   var target = "ws://localhost:8080/SX2/chatSocket?username="+ username +"&photo=<%=path%>/image/user/b3.png";
		window.onload = function() {
			//进入聊天页面，就打开socket通道;
			if ('WebSocket' in window) {
				ws = new WebSocket(target);
			} else if ('MozWebSocket' in window) {
				ws = new MozWebSocket(target);
			} else {
				alert("WebSocket is not supported by this browser!");
				return;
			}
			//当服务端向浏览器发送消息时会执行此函数
			ws.onmessage = function(event) {
				eval("var msg=" + event.data);
				if(undefined != msg.welCome){
					$('#console').append("msg.welCome");
				}
				if(undefined != msg.sendMsg){
				$('#console').append(msg.sendMsg);
				}
				if(undefined != msg.names){
					$('#userlist').html("");
					$(msg.names).each(function(){
					$('#userlist').append(this);
					});
				}
			};
		};
		//发送消息
		function sendMsg() {
			var msg = $('#chat').val();
			if(msg == "" || msg == null)
				return;
			ws.send(msg);
			$('#chat').val("");
		}
		document.getElementById('chat').onkeydown = function(event) {
			if (event.keyCode == 13) {
				sendMsg();
			}
		};
   </script>
   </head>
<body>
<div>
    <p>
        <input type="text" placeholder="type and press enter to chat" id="chat" />
    </p>
    <div id="console-container">
        <div id="console"/>
    </div>
    <div id="console-container">
        <div id="userlist"/>
    </div>
</div>
</body>
</html>
```