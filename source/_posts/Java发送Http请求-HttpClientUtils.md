---
title: 'Java发送Http请求:HttpClientUtils'
date: 2017-10-10 14:18:10
tags: [JavaUtils, Http]
categories: "JavaUtils"
---
- 添加依赖

```xml
<dependency>
	<groupId>org.apache.httpcomponents</groupId>
	<artifactId>httpclient</artifactId>
	<version>4.5.2</version>
</dependency>
```
- 导入包

```java
import java.io.IOException;
import java.io.Serializable;
import java.net.URI;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.apache.http.NameValuePair;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.utils.URIBuilder;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.util.EntityUtils;
```
- 核心代码

```java
/**
 * ClassName: HttpClientUtil.java 
 * FUNCTION:
 * @author: zili
 * @version:
 * @Date: Oct 9, 2017
 */
public class HttpClientUtils {

	private final static Integer DEFAULT_TIMEOUT = 10000;
	
	public static HttpResponse doGet(String url, Map<String, String> param, Integer timeout) {

		// 创建Httpclient对象
		CloseableHttpClient httpclient = HttpClients.createDefault();

		HttpResponse httpResponse = null;
		CloseableHttpResponse response = null;
		try {
			// 创建uri
			URIBuilder builder = new URIBuilder(url);
			if (param != null) {
				for (String key : param.keySet()) {
					builder.addParameter(key, param.get(key));
				}
			}
			URI uri = builder.build();

			// 创建http GET请求
			HttpGet httpGet = new HttpGet(uri);
			if(timeout != null && timeout > 0){
				RequestConfig requestConfig = RequestConfig.custom()
						.setSocketTimeout(timeout)
						.setConnectTimeout(timeout)
						.setConnectionRequestTimeout(timeout)
						.build();
				httpGet.setConfig(requestConfig);
			}
			// 执行请求
			response = httpclient.execute(httpGet);
			httpResponse = new HttpResponse();
			httpResponse.setResponseCode(response.getStatusLine().getStatusCode());
			if(response.getStatusLine().getStatusCode() == 200){
				httpResponse.setResponseData(EntityUtils.toString(response.getEntity(), "UTF-8"));
			}
		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			try {
				if (response != null) {
					response.close();
				}
				httpclient.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		return httpResponse;
	}

	public static HttpResponse doGet(String url) {
		return doGet(url, null, DEFAULT_TIMEOUT);
	}

	public static HttpResponse doPost(String url, Map<String, String> param, Integer timeout) {
		// 创建Httpclient对象
		CloseableHttpClient httpClient = HttpClients.createDefault();
		CloseableHttpResponse response = null;
		HttpResponse httpResponse = null;
		try {
			// 创建Http Post请求
			HttpPost httpPost = new HttpPost(url);
			// 创建参数列表
			if (param != null) {
				List<NameValuePair> paramList = new ArrayList<>();
				for (String key : param.keySet()) {
					paramList.add(new BasicNameValuePair(key, param.get(key)));
				}
				// 模拟表单
				UrlEncodedFormEntity entity = new UrlEncodedFormEntity(paramList, "utf-8");
				httpPost.setEntity(entity);
			}
			if(timeout != null && timeout > 0){
				RequestConfig requestConfig = RequestConfig.custom()
						.setSocketTimeout(timeout)
						.setConnectTimeout(timeout)
						.setConnectionRequestTimeout(timeout)
						.build();
				httpPost.setConfig(requestConfig);
			}
			// 执行http请求
			response = httpClient.execute(httpPost);
			httpResponse = new HttpResponse();
			httpResponse.setResponseCode(response.getStatusLine().getStatusCode());
			if(response.getStatusLine().getStatusCode() == 200){
				httpResponse.setResponseData(EntityUtils.toString(response.getEntity(), "UTF-8"));
			}
		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			try {
				response.close();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}

		return httpResponse;
	}

	public static HttpResponse doPost(String url) {
		return doPost(url, null, DEFAULT_TIMEOUT);
	}

	public static HttpResponse doPostJson(String url, String json, Integer timeout) {
		// 创建Httpclient对象
		CloseableHttpClient httpClient = HttpClients.createDefault();
		CloseableHttpResponse response = null;
		HttpResponse httpResponse = null;
		try {
			// 创建Http Post请求
			HttpPost httpPost = new HttpPost(url);
			// 创建请求内容
			StringEntity entity = new StringEntity(json, ContentType.APPLICATION_JSON);
			if(timeout != null && timeout > 0){
				RequestConfig requestConfig = RequestConfig.custom()
						.setSocketTimeout(timeout)
						.setConnectTimeout(timeout)
						.setConnectionRequestTimeout(timeout)
						.build();
				httpPost.setConfig(requestConfig);
			}
			httpPost.setEntity(entity);
			// 执行http请求
			response = httpClient.execute(httpPost);
			httpResponse = new HttpResponse();
			httpResponse.setResponseCode(response.getStatusLine().getStatusCode());
			if(response.getStatusLine().getStatusCode() == 200){
				httpResponse.setResponseData(EntityUtils.toString(response.getEntity(), "UTF-8"));
			}
		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			try {
				response.close();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}

		return httpResponse;
	}
	
	public static class HttpResponse implements Serializable{
		
		/**
		 * 
		 */
		private static final long serialVersionUID = -2033460329795125474L;

		private Integer responseCode;
		
		private String responseData;
		
		// 省略getter setter
		
	}
	
}
```


