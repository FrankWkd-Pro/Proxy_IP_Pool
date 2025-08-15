import requests
import concurrent.futures
import os

TEST_URL = "http://www.gstatic.com/generate_204"
TIMEOUT = 5

def load_proxies():
    try:
        with open('data/raw_ips.txt', 'r') as f:
            return [p.strip() for p in f.readlines() if p.strip() and ':' in p]
    except FileNotFoundError:
        print("raw_ips.txt not found. Run fetch.py first.")
        return []

def test_proxy(proxy):
    try:
        proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        r = requests.get(TEST_URL, proxies=proxies, timeout=TIMEOUT)
        if r.status_code == 204:
            return proxy
    except Exception as e:
        # 可以取消注释下一行来查看详细的错误信息（用于调试）
        # print(f"Proxy {proxy} failed: {e}")
        pass
    return None

if __name__ == "__main__":
    proxies = load_proxies()
    if not proxies:
        print("No proxies to validate. Exiting.")
        exit(1)
        
    valid_proxies = []
    
    print(f"Testing {len(proxies)} proxies...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(test_proxy, proxy) for proxy in proxies]
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            result = future.result()
            if result:
                valid_proxies.append(result)
                # 每找到一个有效代理就打印一次，可能会很多，如不想太多输出可以注释掉
                # print(f"Valid ({len(valid_proxies)}): {result}")
            # 每测试100个代理打印一次进度
            if (i + 1) % 100 == 0:
                print(f"Progress: {i+1}/{len(proxies)} proxies tested")

    with open('data/valid_ips.txt', 'w') as f:
        f.write('\n'.join(valid_proxies))
    
    print(f"Found {len(valid_proxies)} valid proxies")
