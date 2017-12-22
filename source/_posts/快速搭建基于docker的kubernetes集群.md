---
title: 快速搭建基于docker的kubernetes集群
date: 2017-10-08 10:32:35
tags: [kubernetes, k8s, docker, kubeadm]
categories: DevOps
---
##版本说明 ##

 1. kubernetes1.6
 2. docker1.12.6

## 环境准备 ##

192.168.0.51 master
192.168.0.52 minion1
192.168.0.53 minion2

##安装docker  ##

```
# 安装yum-utils 管理yum repository及扩展包的工具
yum install -y yum-utils   
# 增加docker repository
yum-config-manager \
    --add-repo \
    https://docs.docker.com/v1.13/engine/installation/linux/repo_files/centos/docker.repo
# 下载包信息到本地
yum makecache fast
# 安装docker-1.12.6
yum install -y docker-engine-1.12.6
# 启动docker服务
systemctl start docker
# 开机启动docker
systemctl enable docker
```
##系统配置 ##
创建/etc/sysctl.d/k8s.conf文件，内容为:

```
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
```
执行

```
sysctl -p /etc/sysctl.d/k8s.conf
```
**在/etc/hostname中修改各节点的hostname**，在/etc/hosts中设置hostname对应非lo回环网卡ip:
```
192.168.0.51 master
192.168.0.52 minion1
192.168.0.53 minion2
```
##安装kubeadm和kubelet  ##
安装kubeadm和kubelet需要技术梯子，添加以下
1、通过修改/etc/hosts文件添加IP *.google.com，比如

```
216.58.200.33  gcr.io
216.58.200.33  www.gcr.io
216.58.200.33  cloud.google.com
216.58.200.33  packages.cloud.google.com
216.58.200.33  console.cloud.google.com
216.58.200.33  status.cloud.google.com
216.58.200.33  ssh.cloud.google.com
```
2、:
```
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
```
输入如下内容：

```
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=0
repo_gpgcheck=0
EOF
```

安装kubelet，kubeadm，kubectl

```
yum -y install socat kubelet-1.6.1 kubeadm-1.6.1 kubectl-1.6.1
systemctl enable kubelet.service
```
##初始化集群  ##
上面的步骤每个node都需要执行，此步骤只在Master Node 执行。选择192.168.0.51这台作为Master Node，在此机器上
```
kubeadm init --kubernetes-version=v1.6.1 --pod-network-cidr=10.244.0.0/16 --apiserver-advertise-address=192.168.0.51
```
选择flannel作为网络插件，所以上面的命令指定--pod-network-cidr=10.244.0.0/16。初始化遇到问题时，使用下面的命令清理然后再初始化：

```
kubeadm reset
ifconfig cni0 down
ip link delete cni0
ifconfig flannel.1 down
ip link delete flannel.1
rm -rf /var/lib/cni/
```
不出意外Master Node 已初始化成功。此时查看节点状态 kubectl get nodes 会报 The connection to the server localhost:8080 was refused - did you specify the right host or port? 我们查看kube-apiserver的监听端口

```
[root@kube-master ~]# netstat -nltp | grep apiserver
tcp6       0      0 :::6443                 :::*                    LISTEN      5430/kube-apiserver
```
我们发现apiserver只监听了6443端口，但是我们需要使用kubectl访问apiserver，so 在~/.bash_profile追加下面的环境变量

```
export KUBECONFIG=/etc/kubernetes/admin.conf
# 使环境变量生效
source ~/.bash_profile
```
现在再试试kubectl get nodes 吧！

##安装Pod Network  ##
安装flannel network add-on
分两种情况

1、只有一张网卡
直接执行

```
kubectl create -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel-rbac.yml
kubectl apply -f  https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```
2、有多张网卡
执行

```
kubectl create -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel-rbac.yml
```
执行第二步有所不同，下载https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml ，flanneld启动参数加上***--iface=[iface-name]***

```
......
apiVersion: extensions/v1beta1
kind: DaemonSet
metadata:
  name: kube-flannel-ds
......
containers:
      - name: kube-flannel
        image: quay.io/coreos/flannel:v0.7.0-amd64
        command: [ "/opt/bin/flanneld", "--ip-masq", "--kube-subnet-mgr", "--iface=eth1" ]
......
```
eth1这里换成自己的网卡名即可。创建flanneld

```
kubectl create -f {修改后的kube-flannel.yml路径}
# 确保所有的Pod都处于Running状态
kubectl get pod --all-namespaces -o wide
```
##使Master Node 参与工作负载  ##
一般不建议将Master Node参与负载，此时只为测试环境方便。

```
# 使Master Node参与工作负载
kubectl taint nodes --all  node-role.kubernetes.io/master-
```

##测试  ##

```
kubectl run curl --image=radial/busyboxplus:curl -i --tty
If you don't see a command prompt, try pressing enter.
[ root@curl-57077659-xgckw:/ ]$
```
进入后执行nslookup kubernetes.default确认DNS解析正常。

```
[ root@curl-57077659-xgckw:/ ]$ nslookup kubernetes.default
Server:    10.96.0.10
Address 1: 10.96.0.10 kube-dns.kube-system.svc.cluster.local

Name:      kubernetes.default
Address 1: 10.96.0.1 kubernetes.default.svc.cluster.local
```
如果正常解析，就大功告成啦！

```
# 删除curl这个Pod
kubectl delete deploy cutl
```
##向集群中添加节点  ##
根据上面的步骤安装docker，kubelet套件。
在Master Node节点上执行

```
# 获取token
kubeadm token list
```
在minion1上执行

```
# 关闭防火墙
systemctl stop firewalld
# 禁止防火墙开机启动
systemctl disable firewalld
# 添加节点
kubeadm join --token ${token} ${master-ip}:6443
```
看到如下内容就说明我们已经成功向集群中添加节点了！nice

```
kubeadm join --token a432c6.078b144b659c82b4 192.168.0.51:6443
-----  略略略  ----
Node join complete:
* Certificate signing request sent to master and response
  received.
* Kubelet informed of new secure connection details.

Run 'kubectl get nodes' on the master to see this machine join.
```
在Master Node上执行kubectl get nodes 确保所有的node是Ready的状态。

##问题总结 ##
Q：Minion Node一直处于notReady状态？

A：主要有两个原因：

 1、启动kubelet的时候，会pull两个镜像(gcr.io/**)，因为GFW的存在，不能成功pull，所以要自己找到这两个docker镜像
```
gcr.io/google_containers/pause-amd64:3.0
gcr.io/google_containers/kube-proxy-amd64:v1.6.1
```
 2、 使用Kubeadm工具搭建的Kubernetes集群，已经默认集成了安全策略，所以要将Master Node节点/etc/kubernetes/pki下的所有文件复制到Minion Node相同目录下一份。所以在Master Node上执行
```
scp /etc/kubernetes/pki/* root@{minion-ip}:/etc/kubernetes/pki
```


参考:
http://blog.frognew.com/2017/04/kubeadm-install-kubernetes-1.6.html
http://www.iyunv.com/thread-383770-1-1.html
http://www.infoq.com/cn/articles/Kubernetes-system-architecture-introduction