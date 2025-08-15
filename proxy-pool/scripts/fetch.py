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
