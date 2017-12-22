---
title: 让centos7中的docker飞过墙
date: 2017-10-08 10:37:04
tags: [centos7, docker]
categories: DevOps
---
安装shadowsocks

yum install -y epel-release python-pip

pip install shadowsocks

vim /etc/shadowsocks.json

{
  "server": "your.vpn.com",
  "server_port": 8388,
  "password": "pwd",
  "method": "aes-256-cfb",
  "local_address":"127.0.0.1",
  "local_port":1080
}



客户端启动命令(server、password、methond是你购买的ss账号提供的服务)

sslocal  -c /etc/shadowsocks.json

安装privoxy

yum install -y privoxy

vi /etc/privoxy/config，注释掉listen-address行，在最后加入两行

forward-socks5t / 127.0.0.1:1080 .
listen-address  127.0.0.1:8118

vi ~/.bashrc

export http_proxy=http://127.0.0.1:8118
export https_proxy=http://127.0.0.1:8118
export ftp_proxy=http://127.0.0.1:8118

source ~/.bashrc

systemctl restart privoxy，重启privoxy

curl http://www.google.com，查看是否可以访问

docker pull gcr.io/google_containers/kube-apiserver-amd64:v1.6.1 试试吧