import os
import time
import logging
import requests
from concurrent.futures import ThreadPoolExecutor  # 新增：并发验证

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

TEST_URL = "http://www.gstatic.com/generate_204"  # 测试目标URL
TIMEOUT = 10  # 超时时间（秒）
MAX_WORKERS = 50  # 并发线程数

def load_proxies(protocol):
    """加载指定协议的原始代理列表"""
    try:
        file_path = f'data/raw_ips_{protocol}.txt'
        if not os.path.exists(file_path):
            logger.error(f"❌ {file_path} not found. Run fetch.py first.")
            return []
        
        with open(file_path) as f:
            raw_lines = f.readlines()
        
        proxies = [line.strip() for line in raw_lines if line.strip() and ':' in line.strip()]
        logger.info(f"Loaded {len(proxies)} {protocol} proxies from {file_path}")
        return proxies
    except Exception as e:
        logger.error(f"🔥 Error loading {protocol} proxies: {e}")
        return []

def test_proxy(proxy, protocol):
    """测试单个代理（支持http和socks5）"""
    try:
        ip, port = proxy.split(':')
        proxies = {
            "http": f"{protocol}://{ip}:{port}",
            "https": f"{protocol}://{ip}:{port}"
        }
        # 发送测试请求
        response = requests.get(TEST_URL, proxies=proxies, timeout=TIMEOUT)
        if response.status_code == 204:
            return proxy  # 验证成功返回代理
    except:
        return None  # 验证失败

def validate_proxies(protocol):
    """批量验证指定协议的代理"""
    proxies = load_proxies(protocol)
    if not proxies:
        return []
    
    logger.info(f"Validating {len(proxies)} {protocol} proxies...")
    start_time = time.time()
    
    # 并发验证
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(lambda p: test_proxy(p, protocol), proxies)
    
    valid_proxies = [p for p in results if p is not None]
    duration = time.time() - start_time
    
    # 保存有效代理
    with open(f'data/valid_ips_{protocol}.txt', 'w') as f:
        f.write('\n'.join(valid_proxies))
    
    logger.info(f"✅ Valid {protocol} proxies: {len(valid_proxies)}/{len(proxies)}")
    logger.info(f"⏱️ Validation time: {duration:.2f} seconds")
    return valid_proxies

if __name__ == "__main__":
    # 分别验证HTTP和SOCKS5代理
    validate_proxies("http")
    validate_proxies("socks5")
