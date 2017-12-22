---
title: 安装kubernetes-dashboard插件
date: 2017-10-08 10:35:19
tags: [kubernetes, k8s, dashboard]
categories: DevOps
---
关于如何搭建基于docker的Kubernetes环境，请看笔者另一片博客：
https://my.oschina.net/u/3559870/blog/1031428
## 插件说明  ##
完成[使用Kubeadm搭建Kubernetes(docker)](https://my.oschina.net/u/3559870/blog/1031428)之后，Kubernetes实际已经搭建成功～但是频繁操作命令行界面是会崩溃的好吗！！所以在Kubernetes 1.2版本后新增了Kube Dashboard，我们就可以在浏览器愉快的通过点 点 点操作啦。
##功能说明  ##
create：上传json或者yaml的方式新建resource，同kubectl create -f
delete：删除副本(Replication Controllers)
modify：修改副本数(replicas)
query：查询相关信息，同kubectl get
通过web-ui+上述功能，我们就能基本脱离命令行界面了！
## 安装步骤  ##
***此时已经完成kubernetes的搭建。***
我们将dashboard以静态Pod的方式运行在Master Node上。

```
cd /etc/kubernetes/manifests
```
此目录是已有的静态Pod的yaml文件，我们创建kubernetes-dashboard.yaml文件

```
# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Configuration to deploy release version of the Dashboard UI compatible with
# Kubernetes 1.6 (RBAC enabled).
#
# Example usage: kubectl create -f <this_file>

apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    app: kubernetes-dashboard
  name: kubernetes-dashboard
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: kubernetes-dashboard
  labels:
    app: kubernetes-dashboard
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: kubernetes-dashboard
  namespace: kube-system
---
kind: Deployment
apiVersion: extensions/v1beta1
metadata:
  labels:
    app: kubernetes-dashboard
  name: kubernetes-dashboard
  namespace: kube-system
spec:
  replicas: 1
  revisionHistoryLimit: 10
  selector:
    matchLabels:
      app: kubernetes-dashboard
  template:
    metadata:
      labels:
        app: kubernetes-dashboard
    spec:
      containers:
      - name: kubernetes-dashboard
        image: registry.cn-beijing.aliyuncs.com/bbt_k8s/kubernetes-dashboard-amd64:v1.6.0
        imagePullPolicy: Always
        ports:
        - containerPort: 9090
          protocol: TCP
        args:
          # Uncomment the following line to manually specify Kubernetes API server Host
          # If not specified, Dashboard will attempt to auto discover the API server and connect
          # to it. Uncomment only if the default does not work.
          # - --apiserver-host=http://my-address:port
        livenessProbe:
          httpGet:
            path: /
            port: 9090
          initialDelaySeconds: 30
          timeoutSeconds: 30
      serviceAccountName: kubernetes-dashboard
      # Comment the following tolerations if Dashboard must not be deployed on master
      tolerations:
      - key: node-role.kubernetes.io/master
        effect: NoSchedule
---
kind: Service
apiVersion: v1
metadata:
  labels:
    app: kubernetes-dashboard
  name: kubernetes-dashboard
  namespace: kube-system
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 9090
  selector:
    app: kubernetes-dashboard
```
创建文件kubernetes-dashboard-rbac.yaml文件

```
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1beta1
metadata:
  name: dashboard-admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin 
subjects:
- kind: ServiceAccount
  name: default
  namespace: kube-system
```
创建dashboard、dashboard-rbac resource

```
kubectl create -f kubernetes-dashboard-rbac.yml
kubectl create -f kubernetes-dashboard.yaml
```
创建成功结果如下所示

```
[root@kube-master manifests]# kubectl create -f dashboard-rbac.yaml
clusterrolebinding "dashboard-admin" created
[root@kube-master manifests]# kubectl create -f dashboard.yaml
serviceaccount "kubernetes-dashboard" created
clusterrolebinding "kubernetes-dashboard" created
deployment "kubernetes-dashboard" created
service "kubernetes-dashboard" created
```
查询dashboard运行的端口

```
kubectl describe --namespace kube-system service kubernetes-dashboard

```

```
[root@kube-master manifests]# kubectl describe --namespace kube-system service kubernetes-dashboard
Name:			kubernetes-dashboard
Namespace:		kube-system
Labels:			app=kubernetes-dashboard
Annotations:		<none>
Selector:		app=kubernetes-dashboard
Type:			NodePort
IP:			10.110.236.54
Port:			<unset>	80/TCP
NodePort:		<unset>	30989/TCP
Endpoints:		10.244.0.16:9090
Session Affinity:	None
Events:			<none>
```
NodePort就是我们要访问的端口啦！快快打开浏览器输入{master-ip}:{node-port}吧！