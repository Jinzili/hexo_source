---
title: 大数据学习 - socket
date: 2018-08-19 21:33:01
tags: ["socket"]
categories: "大数据"
---
## 一个socket小Demo
### server

```Java
public class ServiceServer {

    public static void main(String[] args) throws IOException {

        // 创建一个serverSocket 绑定到本机的8080端口上
        ServerSocket server = new ServerSocket();
        server.bind(new InetSocketAddress("localhost", 8080));

        // 接收客户端的连接请求, accpet时一个阻塞方法, 会一直等待到有客户端连接
        while(true){
            Socket socket = server.accept();
            new Thread(new ServiceServerTask(socket)).start();
        }


    }

}
```
### client

```Java
public class ServiceClient {

    public static void main(String[] args) throws IOException {
        // 和服务器发送请求建立了连接
        Socket socket = new Socket("localhost", 8080);
        // 从socket获取输入输出流
        InputStream is = socket.getInputStream();
        OutputStream os = socket.getOutputStream();

        PrintWriter pw = new PrintWriter(os);
        pw.println("hello, server");
        pw.flush();

        BufferedReader br = new BufferedReader(new InputStreamReader(is));
        String result = br.readLine();
        System.out.println(result);

        socket.close();

    }

}
```
### task

```Java
public class ServiceServerTask implements Runnable {

    private Socket socket;

    public ServiceServerTask(Socket socket){
        this.socket = socket;
    }

    // 业务逻辑, 跟客户端进行数据交互
    @Override
    public void run() {
        InputStream is = null;
        OutputStream os = null;
        try {
            // 从socket连接中获取到与client之间的网络通信输入输出流
            is = socket.getInputStream();
            os = socket.getOutputStream();
            BufferedReader br = new BufferedReader(new InputStreamReader(is));
            // 从网络通信输入流中读取客户端发送过来的数据
            // socketinputstream的读数据的方法都是阻塞的
            String param = br.readLine();
            GetDataServiceImpl getDataService = new GetDataServiceImpl();
            String result = getDataService.getData(param);
            // 将返回数据写道socket的输出流中, 以发送客户端
            PrintWriter pw = new PrintWriter(os);
            pw.println(result);
            pw.flush();
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            try {
                if(is != null){
                    is.close();
                }
                if(os != null) {
                    os.close();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

}
```
### 处理类

```Java
public class GetDataServiceImpl {

    public String getData(String param){
        return "OK: " + param;
    }

}
```
