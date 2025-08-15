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
