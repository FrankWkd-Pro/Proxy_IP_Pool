import requests
import os
import re  # 新增：用于解析SOCKS5代理URL

# 免费代理源列表（区分协议类型）
SOURCES = [
    # HTTP代理源（保持原有）
    {
        "url": "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
        "protocol": "http"
    },
    {
        "url": "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        "protocol": "http"
    },
    {
        "url": "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "protocol": "http"
    },
    # 新增SOCKS5代理源
    {
        "url": "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks5/data.txt",
        "protocol": "socks5"
    }
]

def fetch_proxies():
    # 按协议类型存储代理（key: 协议, value: 代理集合）
    proxies = {"http": set(), "socks5": set()}
    for source in SOURCES:
        url = source["url"]
        protocol = source["protocol"]
        try:
            r = requests.get(url, timeout=10)
            for line in r.text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                # 处理SOCKS5代理的URL格式（socks5://ip:port）
                if protocol == "socks5":
                    # 正则提取ip和port（例如从"socks5://1.2.3.4:1080"中提取"1.2.3.4:1080"）
                    match = re.match(r"socks5://([\d.]+:\d+)", line)
                    if match:
                        proxy = match.group(1)
                    else:
                        continue  # 格式不符合则跳过
                else:
                    # HTTP代理直接取第一个字段
                    proxy = line.split()[0]
                
                if proxy and ':' in proxy:
                    proxies[protocol].add(proxy)
        except Exception as e:
            print(f"Failed to fetch from {url}: {e}")
    
    # 创建data目录（确保存在）
    os.makedirs('data', exist_ok=True)
    # 分别存储不同协议的代理
    for proto in ["http", "socks5"]:
        with open(f'data/raw_ips_{proto}.txt', 'w') as f:
            f.write('\n'.join(proxies[proto]))
        print(f"Fetched {len(proxies[proto])} {proto} proxies")
    
    return proxies

if __name__ == "__main__":
    fetch_proxies()
