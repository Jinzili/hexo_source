---
title: SpringMVC之下载文件
date: 2017-10-08 10:25:40
tags: [SpringMVC, 下载文件]
categories: Spring
---
## springMVC 下载文件 ##
在开发web项目时，我们经常会遇到下载文件的情况。我们下来看下面这个代码：
```java
public void downLoad(HttpServletResponse response, String filename) {
		if (file == null || !file.exists()) {
			return;
		}
		OutputStream out = null;
		try {
			response.reset();
			response.setContentType("application/octet-stream; charset=utf-8");
			response.setHeader("Content-Disposition", "attachment; filename="
					+ file.getName());
			out = response.getOutputStream();
			File file = new File(savePath + fileName);//文件路径
			out.write(FileUtils.readFileToByteArray(file));
			out.flush();
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			if (out != null) {
				try {
					out.close();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}
	}
```
在之前的servlet中这样的写法非常普遍，但是既然我们使用springmvc框架，不应该在暴露HttpServletResponse 这种j2ee的接口了，所以spring提供了更好、更优雅的实现方式。

```java
@RequestMapping("/download")  
	public ResponseEntity<byte[]> download(String fileName) throws IOException { 
	    HttpHeaders headers = new HttpHeaders();  
	    headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);  
	    headers.setContentDispositionFormData("attachment", URLEncoder.encode(fileName,"UTF-8")); 
	    return new ResponseEntity<byte[]>(FileUtils.readFileToByteArray(mailService.getDownloadFile(fileName)),  
	                                      headers, HttpStatus.CREATED);  
	}
```
我们详细看看这几行代码:

```java
headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
```
在源码中：

```java
	/**
	 * Public constant media type for {@code application/octet-stream}.
	 *  */
	public final static MediaType APPLICATION_OCTET_STREAM;

	/**
	 * A String equivalent of {@link MediaType#APPLICATION_OCTET_STREAM}.
	 */
	public final static String APPLICATION_OCTET_STREAM_VALUE = "application/octet-stream";
	APPLICATION_OCTET_STREAM = MediaType.valueOf(APPLICATION_OCTET_STREAM_VALUE);
```
这一句的作用相当于

```
response.setContentType("application/octet-stream; charset=utf-8");
```
指定contentType为"application/octet-stream"，contentType的作用就是用于定义网络文件的类型和网页的编码，决定浏览器将以什么形式、什么编码读取这个文件。这里的作用就是，告诉浏览器返回的是二进制流数据。

```java
headers.setContentDispositionFormData("attachment", URLEncoder.encode(fileName,"UTF-8")); 
```
Content-disposition其实可以控制用户请求所得的内容存为一个文件的时候提供一个默认的文件名，文件直接在浏览器上显示或者在访问时弹出文件下载对话框。 如attachment为以附件方式下载 。相当于servlet中：

```
response.setHeader("Content-Disposition", "attachment; filename="
					+ file.getName());
```
filename就是显示的下载框中默认的下载文件名。Content-Disposition参数本来是为了在客户端另存文件时提供一个建议的文件名，但是考虑到安全的原因，就从规范中去掉了这个参数。但是由于很多浏览器已经能够支持这个参数，所以只是在规范文档中列出，但是要注意这个不是HTTP/1.1的标准参数。为了让建议的文件名支持中文，使用了URLEncoder.encode(fileName,"UTF-8")。
最后一句代码：

```java
return new ResponseEntity<byte[]>(FileUtils.readFileToByteArray(mailService.getDownloadFile(fileName)),  
	                                      headers, HttpStatus.CREATED);
```
这里getDownloadFile()方法就是通过文件名得到文件，在使用这段代码时需要换成自己的实现方式。headers上面已经介绍过了，就是告诉浏览器返回的是二进制流数据（application/octet-stream），以附件的形式打开（"attachment;filename=xxx"）。并且返回状态码HttpStatus.CREATED(201,代表已创建请求成功并且服务器创建了新的资源。)
最后提醒注意的是，导包的时候不要导错了:

```java
import org.apache.commons.io.FileUtils;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
```
