import requests
import concurrent.futures
import os
import time
import logging
import json
from datetime import datetime

# 配置详细日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 输出到控制台
        logging.FileHandler('validation.log')  # 输出到日志文件
    ]
)
logger = logging.getLogger('ProxyValidator')

# 配置参数
TEST_URL = "http://www.gstatic.com/generate_204"
TIMEOUT = 5
MAX_WORKERS = 100
DEBUG_LEVEL = 1  # 【调试内容输出级别】 0: 仅显示关键信息和最终报告1: 正常模式（推荐）2: 详细模式（显示所有错误）3: 极端模式（包含堆栈跟踪）

def load_proxies():
    """加载原始代理列表并进行初步清理"""
    try:
        logger.info("Starting proxy load process")
        start_time = time.time()
        
        if not os.path.exists('data/raw_ips.txt'):
            logger.error("❌ raw_ips.txt not found. Run fetch.py first.")
            return []
        
        with open('data/raw_ips.txt') as f:
            raw_lines = f.readlines()
            logger.info(f"Loaded {len(raw_lines)} lines from raw_ips.txt")
            
            # 清理无效行
            proxies = []
            invalid_lines = 0
            for line_num, line in enumerate(raw_lines, 1):
                stripped = line.strip()
                if stripped and ':' in stripped:
                    proxies.append(stripped)
                    if DEBUG_LEVEL >= 3:
                        logger.debug(f"🔍 Line {line_num} is valid: {stripped}")
                else:
                    invalid_lines += 1
                    if DEBUG_LEVEL >= 2:
                        logger.debug(f"🚫 Line {line_num} is invalid (empty or missing colon): {repr(line)}")
            
            duration = time.time() - start_time
            logger.info(f"✅ Proxy load completed. Valid entries: {len(proxies)}/{len(raw_lines)}")
            if DEBUG_LEVEL >= 1:
                logger.info(f"📊 Invalid lines filtered: {invalid_lines}")
            logger.info(f"⏱️ Load time: {duration:.2f} seconds")
            
            return proxies
            
    except Exception as e:
        logger.exception(f"🔥 Critical error loading proxies: {str(e)}")
        return []

def test_proxy(proxy):
    """测试单个代理的有效性"""
    test_start = time.time()
    result = {
        "proxy": proxy,
        "status": "failed",
        "error": None,
        "response_time": 0,
        "status_code": None
    }
    
    try:
        # 配置代理设置
        proxy_url = f"http://{proxy}"
        proxies = {"http": proxy_url, "https": proxy_url}
        
        if DEBUG_LEVEL >= 3:
            logger.debug(f"🔍 Starting detailed test for proxy: {proxy}")
            logger.debug(f"📡 Using proxy URL: {proxy_url}")
            logger.debug(f"⏱️ Timeout set to: {TIMEOUT}s")
        
        # 发送测试请求
        if DEBUG_LEVEL >= 2:
            logger.debug(f"📤 Sending request to {TEST_URL} via {proxy}")
        
        response = requests.get(
            TEST_URL, 
            proxies=proxies, 
            timeout=TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"}
        )
        
        # 记录响应信息
        result["response_time"] = time.time() - test_start
        result["status_code"] = response.status_code
        
        if DEBUG_LEVEL >= 3:
            logger.debug(f"📥 Received response from {proxy} (status: {response.status_code}, time: {result['response_time']:.2f}s)")
        
        # 验证响应
        if response.status_code == 204:
            result["status"] = "success"
            if DEBUG_LEVEL >= 2:
                logger.info(f"✅ Success: {proxy} responded in {result['response_time']:.2f}s")
            return proxy
        else:
            result["error"] = f"Unexpected status code: {response.status_code}"
            if DEBUG_LEVEL >= 2:
                logger.warning(f"⚠️ Failed: {proxy} returned HTTP {response.status_code} in {result['response_time']:.2f}s")
    
    except requests.exceptions.ConnectTimeout:
        result["error"] = "Connection timeout"
        if DEBUG_LEVEL >= 2:
            logger.warning(f"⏱️ Timeout: {proxy} failed to connect within {TIMEOUT}s")
    except requests.exceptions.ProxyError as pe:
        result["error"] = f"Proxy error: {str(pe)}"
        if DEBUG_LEVEL >= 2:
            logger.warning(f"🚫 Proxy error: {proxy} - {str(pe)}")
    except requests.exceptions.SSLError:
        result["error"] = "SSL certificate error"
        if DEBUG_LEVEL >= 2:
            logger.warning(f"🔒 SSL error with proxy: {proxy}")
    except Exception as e:
        result["error"] = f"General error: {str(e)}"
        if DEBUG_LEVEL >= 2:
            logger.error(f"🔥 Error testing {proxy}: {str(e)}", exc_info=DEBUG_LEVEL >= 3)
    
    # 记录详细调试信息
    if DEBUG_LEVEL >= 3:
        logger.debug(f"📋 Test result for {proxy}: {json.dumps(result, indent=2)}")
    
    return None

def log_progress(current, total, valid_count, start_time):
    """记录验证进度并估算剩余时间"""
    elapsed = time.time() - start_time
    processed_percent = (current / total) * 100
    speed = current / elapsed if elapsed > 0 else 0
    
    # 估算剩余时间（秒）
    remaining_proxies = total - current
    remaining_time = remaining_proxies / speed if speed > 0 else 0
    
    # 格式化时间显示（转换为分:秒格式）
    elapsed_str = f"{int(elapsed // 60)}m{int(elapsed % 60)}s"
    remaining_str = f"{int(remaining_time // 60)}m{int(remaining_time % 60)}s" if speed > 0 else "N/A"
    
    progress = f"🚀 Progress: {current}/{total} ({processed_percent:.1f}%)"
    stats = (f"✅ Valid: {valid_count} | ⏱️ Elapsed: {elapsed_str} | "
             f"⌛ Remaining: {remaining_str} | 📈 Speed: {speed:.1f} proxies/s")
    
    logger.info(progress)
    logger.info(stats)
    if DEBUG_LEVEL >= 2:
        logger.debug(f"📊 Detailed progress: {valid_count}/{current} valid so far ({(valid_count/current)*100:.1f}% success rate)")
    logger.info("-" * 60)

if __name__ == "__main__":
    # 初始化
    start_time = time.time()
    logger.info("=" * 70)
    logger.info(f"🚀 STARTING PROXY VALIDATION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🔧 Configuration: Test URL={TEST_URL}, Timeout={TIMEOUT}s, Workers={MAX_WORKERS}, Debug Level={DEBUG_LEVEL}")
    if DEBUG_LEVEL >= 2:
        logger.debug("📝 Debug mode enabled - additional details will be shown")
    logger.info("=" * 70)
    
    # 加载代理
    proxies = load_proxies()
    if not proxies:
        logger.error("❌ No proxies to validate. Exiting.")
        exit(1)
    
    # 初始化验证
    valid_proxies = []
    total_proxies = len(proxies)
    logger.info(f"🔍 Beginning validation of {total_proxies} proxies")
    if DEBUG_LEVEL >= 2:
        logger.debug(f"📋 First 5 proxies to test: {proxies[:5]}")  # 显示前5个代理用于调试
    
    # 使用线程池验证代理
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            if DEBUG_LEVEL >= 3:
                logger.debug(f"🧵 Thread pool initialized with {MAX_WORKERS} workers")
            
            futures = {executor.submit(test_proxy, proxy): proxy for proxy in proxies}
            
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                proxy = futures[future]
                if DEBUG_LEVEL >= 3:
                    logger.debug(f"🔄 Processing result for proxy: {proxy} (index: {i+1})")
                
                result = future.result()
                
                if result:
                    valid_proxies.append(result)
                    if DEBUG_LEVEL >= 1:
                        logger.info(f"✅ Added valid proxy: {result} (total valid: {len(valid_proxies)})")
                else:
                    if DEBUG_LEVEL >= 3:
                        logger.debug(f"❌ Proxy {proxy} is invalid")
                
                # 定期记录进度
                if (i + 1) % 100 == 0 or (i + 1) == total_proxies:
                    log_progress(i + 1, total_proxies, len(valid_proxies), start_time)
    
    except Exception as e:
        logger.exception(f"🔥 Critical error during validation: {str(e)}")
    
    # 保存有效代理
    os.makedirs('data', exist_ok=True)
    with open('data/valid_ips.txt', 'w') as f:
        f.write('\n'.join(valid_proxies))
    
    if DEBUG_LEVEL >= 1:
        logger.info(f"💾 Saved {len(valid_proxies)} valid proxies to data/valid_ips.txt")
    if DEBUG_LEVEL >= 3:
        logger.debug(f"📂 Valid proxies file path: {os.path.abspath('data/valid_ips.txt')}")
    
    # 最终报告统计数据收集
    validation_time = time.time() - start_time
    success_rate = (len(valid_proxies) / total_proxies) * 100 if total_proxies > 0 else 0
    
    # 写入验证统计信息
    stats = {
        "valid_count": len(valid_proxies),
        "total_count": total_proxies,
        "success_rate": success_rate,
        "validation_time": validation_time,
        "run_timestamp": datetime.now().isoformat()
    }
    
    # 确保stats目录存在
    os.makedirs('stats', exist_ok=True)
    with open('stats/validation_stats.json', 'w') as stats_file:
        json.dump(stats, stats_file, indent=2)
    
    if DEBUG_LEVEL >= 1:
        logger.info(f"📊 Validation statistics saved to stats/validation_stats.json")
    if DEBUG_LEVEL >= 3:
        logger.debug(f"📊 Detailed stats: {json.dumps(stats, indent=2)}")
    
    # 最终报告日志输出
    logger.info("=" * 70)
    logger.info(f"🏁 VALIDATION COMPLETED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📊 Results: {len(valid_proxies)} valid out of {total_proxies} ({success_rate:.2f}% success rate)")
    logger.info(f"⏱️ Total time: {validation_time:.2f} seconds")
    logger.info(f"📈 Average speed: {total_proxies/validation_time:.2f} proxies/second")
    logger.info(f"💾 Valid proxies saved to data/valid_ips.txt")
    logger.info("=" * 70)
    
    # 退出状态
    if valid_proxies:
        logger.info("✅ Validation successful")
        exit(0)
    else:
        logger.error("❌ No valid proxies found")
        exit(1)
