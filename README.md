# Proxy_IP_Pool
A Repo for FrankWkd to Save Available Proxy IPs and Update Available IPs by Using Github Actions
### 具体可执行策略（Ubuntu 24.04 + GitHub Actions）

#### 1. 创建项目结构
```bash
# 在Ubuntu上执行
mkdir -p proxy-pool/{.github/workflows,scripts,data}
cd proxy-pool
touch .github/workflows/update.yml
touch scripts/{fetch.py,validate.py,deploy.sh}
touch data/valid_ips.txt
```

#### 2. 创建GitHub Actions工作流 (`.github/workflows/update.yml`)
```yaml
name: Proxy Pool Update

on:
schedule:
- cron: '0 */6 * * *'# 每6小时运行一次
workflow_dispatch:# 支持手动触发

jobs:
build:
runs-on: ubuntu-latest
steps:
- name: Checkout
uses: actions/checkout@v4

- name: Set up Python
uses: actions/setup-python@v5
with:
python-version: '3.10'

- name: Install dependencies
run: |
python -m pip install --upgrade pip
pip install requests PyYAML

- name: Fetch proxies
run: python scripts/fetch.py

- name: Validate proxies
run: python scripts/validate.py

- name: Push updates
run: |
git config --global user.name 'GitHub Actions'
git config --global user.email 'actions@github.com'
git add data/valid_ips.txt
git commit -m "Update valid proxies"
git push
```

#### 3. 创建爬取脚本 (`scripts/fetch.py`)
```python
import requests
import os

# 免费代理源列表
SOURCES = [
"https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
"https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
"https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
]

def fetch_proxies():
proxies = set()
for url in SOURCES:
try:
r = requests.get(url, timeout=10)
proxies.update(r.text.strip().split('\n'))
except Exception as e:
print(f"Failed to fetch from {url}: {e}")
return list(proxies)

if __name__ == "__main__":
proxies = fetch_proxies()
os.makedirs('data', exist_ok=True)
with open('data/raw_ips.txt', 'w') as f:
f.write('\n'.join(proxies))
print(f"Fetched {len(proxies)} proxies")
```

#### 4. 创建验证脚本 (`scripts/validate.py`)
```python
import requests
import concurrent.futures
import os

TEST_URL = "http://www.gstatic.com/generate_204"
TIMEOUT = 5

def load_proxies():
with open('data/raw_ips.txt') as f:
return [p.strip() for p in f.readlines() if p.strip()]

def test_proxy(proxy):
try:
r = requests.get(TEST_URL,
proxies={'http': f'http://{proxy}', 'https': f'http://{proxy}'},
timeout=TIMEOUT)
if r.status_code == 204:
return proxy
except:
pass
return None

if __name__ == "__main__":
proxies = load_proxies()
valid_proxies = []

with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
futures = [executor.submit(test_proxy, proxy) for proxy in proxies]
for future in concurrent.futures.as_completed(futures):
result = future.result()
if result:
valid_proxies.append(result)
print(f"Valid: {result}")

with open('data/valid_ips.txt', 'w') as f:
f.write('\n'.join(valid_proxies))

print(f"Found {len(valid_proxies)} valid proxies")
```

#### 5. 创建部署脚本 (`scripts/deploy.sh`)
```bash
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
```

#### 6. 设置自动部署（在Ubuntu上）
```bash
# 1. 克隆仓库到本地
git clone https://github.com/你的用户名/proxy-pool.git
cd proxy-pool

# 2. 创建定时任务
(crontab -l ; echo "*/30 * * * * cd /path/to/proxy-pool && ./scripts/deploy.sh") | crontab -

# 3. 赋予脚本执行权限
chmod +x scripts/deploy.sh

# 4. 首次手动运行
./scripts/deploy.sh
```

#### 7. 验证流程
1. GitHub Actions每6小时自动：
- 爬取新代理IP
- 验证IP有效性
- 更新仓库中的valid_ips.txt

2. 你的Ubuntu服务器每30分钟：
- 拉取最新代理列表
- 生成Clash配置
- 重启Clash服务

#### 优化建议：
1. 在Clash配置中添加健康检查：
```yaml
proxy-groups:
- name: Auto
type: url-test
url: http://www.gstatic.com/generate_204
interval: 300
proxies:
${PROXY_LIST}# 会被脚本替换
```

2. 如需更高匿名性，在`fetch.py`中添加SOCKS5源：
```python
SOCKS_SOURCES = [
"https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
"https://www.proxy-list.download/api/v1/get?type=socks5"
]
```

3. 监控日志：
```bash
# 查看Clash日志
journalctl -u clash -f

# 查看脚本日志
grep CRON /var/log/syslog
```

此方案完全自动化运行，无需手动维护，GitHub Actions处理所有Python依赖和网络请求，Ubuntu只需执行简单的shell脚本。
