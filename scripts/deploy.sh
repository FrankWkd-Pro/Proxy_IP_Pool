#!/bin/bash

# 在Ubuntu上执行
CLASH_CONFIG="/etc/clash/config.yaml"# 修改为你的Clash配置文件路径

# 从GitHub仓库获取最新代理列表
git pull origin main

# 生成Clash代理配置
echo "proxies:" > temp.yaml
awk '{print "- name: Proxy_" NR "\ntype: http\nserver: " split($1, parts, ":")[1] "\nport: " split($1, parts, ":")[2] "\nusername: \"\"\npassword: \"\""}' data/valid_ips.txt >> temp.yaml

# 添加到现有配置中
awk '/^proxies:/ {while(getline && $0 !~ /^[^ ]/) {}}1' $CLASH_CONFIG | \
sed '/^proxies:/r temp.yaml' > $CLASH_CONFIG.new

mv $CLASH_CONFIG.new $CLASH_CONFIG
rm temp.yaml

# 重启Clash服务
systemctl restart clash
echo "Clash配置已更新并重启"
