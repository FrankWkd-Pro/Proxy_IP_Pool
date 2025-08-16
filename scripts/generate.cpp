#include <algorithm>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <chrono>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <stdexcept>
#include <pthread.h>
#include <semaphore.h>

// 代理服务器结构体（新增协议类型字段）
struct Proxy {
    std::string ip;
    int port;
    std::string protocol;  // 新增：协议类型（http/socks5）
    int latency; // 延迟(毫秒，-1表示无效)
};

// 线程参数结构体（保持不变）
struct ThreadArgs {
    const Proxy* proxy;
    std::vector<Proxy>* results;
    pthread_mutex_t* mutex;
    int timeoutMs;
};

// 测试单个代理延迟（保持不变，仅检测端口连通性）
int testSingleProxy(const std::string& ip, int port, int timeoutMs) {
    // （原有代码不变）
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd == -1) return -1;

    struct timeval timeout;
    timeout.tv_sec = timeoutMs / 1000;
    timeout.tv_usec = (timeoutMs % 1000) * 1000;
    setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    setsockopt(sockfd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    if (inet_pton(AF_INET, ip.c_str(), &server_addr.sin_addr) <= 0) {
        close(sockfd);
        return -1;
    }

    auto start = std::chrono::high_resolution_clock::now();
    int connectResult = connect(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr));
    auto end = std::chrono::high_resolution_clock::now();
    close(sockfd);

    if (connectResult == 0) {
        return std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    }
    return -1;
}

// 线程入口函数（保持不变）
void* threadFunc(void* arg) {
    ThreadArgs* args = static_cast<ThreadArgs*>(arg);
    Proxy result = *args->proxy;
    result.latency = testSingleProxy(args->proxy->ip, args->proxy->port, args->timeoutMs);
    
    pthread_mutex_lock(args->mutex);
    args->results->push_back(result);
    pthread_mutex_unlock(args->mutex);
    
    return nullptr;
}

// 新增：从文件读取指定协议的代理
std::vector<Proxy> readProxiesByProtocol(const std::string& filename, const std::string& protocol) {
    std::vector<Proxy> proxies;
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "无法打开文件: " << filename << std::endl;
        return proxies;
    }

    std::string line;
    while (std::getline(file, line)) {
        if (line.empty()) continue;
        size_t colonPos = line.find(':');
        if (colonPos == std::string::npos) continue;

        try {
            Proxy proxy;
            proxy.ip = line.substr(0, colonPos);
            proxy.port = std::stoi(line.substr(colonPos + 1));
            proxy.protocol = protocol;  // 设置协议类型
            proxy.latency = -1;
            proxies.push_back(proxy);
        } catch (...) {
            continue;
        }
    }
    file.close();
    return proxies;
}

// 多线程筛选低延迟代理（保持不变）
std::vector<Proxy> filterLowLatencyProxies(const std::vector<Proxy>& proxies, 
                                          int maxLatencyMs = 1000, 
                                          int maxThreads = 50) {
    // （原有代码不变）
    std::vector<Proxy> results;
    pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
    std::vector<pthread_t> threads;
    threads.reserve(proxies.size());

    std::cout << "使用 " << maxThreads << " 线程并行测试 " << proxies.size() << " 个代理..." << std::endl;
    auto start = std::chrono::high_resolution_clock::now();

    for (size_t i = 0; i < proxies.size(); ++i) {
        if (i >= maxThreads) {
            pthread_join(threads[i - maxThreads], nullptr);
        }

        ThreadArgs* args = new ThreadArgs{
            &proxies[i], &results, &mutex, maxLatencyMs
        };

        pthread_t thread;
        if (pthread_create(&thread, nullptr, threadFunc, args) != 0) {
            delete args;
            std::cerr << "线程创建失败，跳过代理 " << proxies[i].ip << std::endl;
            continue;
        }
        threads.push_back(thread);
    }

    for (size_t i = std::max(0, (int)threads.size() - maxThreads); i < threads.size(); ++i) {
        pthread_join(threads[i], nullptr);
    }

    auto end = std::chrono::high_resolution_clock::now();
    int totalMs = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    std::cout << "并行测试完成，总耗时: " << totalMs << "ms" << std::endl;

    std::vector<Proxy> validProxies;
    for (const auto& p : results) {
        if (p.latency != -1 && p.latency <= maxLatencyMs) {
            validProxies.push_back(p);
        }
    }

    std::sort(validProxies.begin(), validProxies.end(),
              [](const Proxy& a, const Proxy& b) { return a.latency < b.latency; });

    std::cout << "筛选出 " << validProxies.size() << " 个有效代理（延迟≤" << maxLatencyMs << "ms）" << std::endl;
    return validProxies;
}

// 生成Clash配置文件（修改：支持多协议）
bool generateClashConfig(const std::vector<Proxy>& proxies, const std::string& outputFilename) {
    if (proxies.empty()) {
        std::cerr << "没有有效代理可生成配置" << std::endl;
        return false;
    }

    std::stringstream ss;

    // 基础配置（不变）
    ss << "mixed-port: 7890\n"
       << "allow-lan: false\n"
       << "mode: rule\n"
       << "log-level: info\n"
       << "external-controller: 127.0.0.1:9090\n"
       << "secret: \"\"\n\n";

    // 写入代理列表（根据协议设置type）
    ss << "proxies:\n";
    for (size_t i = 0; i < proxies.size(); ++i) {
        ss << "  - name: \"" << proxies[i].protocol << "_Proxy_" << (i + 1) << "_" << proxies[i].latency << "ms\"\n"
           << "    type: " << proxies[i].protocol << "\n"  // 使用协议类型作为type
           << "    server: " << proxies[i].ip << "\n"
           << "    port: " << proxies[i].port << "\n"
           << "    username: \"\"\n"
           << "    password: \"\"\n"
           << "    timeout: 500\n"
           << "    keep-alive: true\n";
        if (i != proxies.size() - 1) ss << "\n";
    }
    ss << "\n";

    // 代理组（不变，自动包含所有代理）
    ss << "proxy-groups:\n"
       << "  - name: \"AutoSelect\"\n"
       << "    type: url-test\n"
       << "    url: \"http://www.gstatic.com/generate_204\"\n"
       << "    interval: 300\n"
       << "    proxies:\n";
    for (size_t i = 0; i < proxies.size(); ++i) {
        ss << "      - \"" << proxies[i].protocol << "_Proxy_" << (i + 1) << "_" << proxies[i].latency << "ms\"\n";
    }
    ss << "    tolerance: 100\n\n";

    // 规则（不变）
    ss << "rules:\n"
       << "  - MATCH,AutoSelect\n";

    // 写入文件
    std::ofstream outFile(outputFilename);
    if (!outFile.is_open()) {
        std::cerr << "无法创建输出文件: " << outputFilename << std::endl;
        return false;
    }
    outFile << ss.str();
    outFile.close();

    return true;
}

int main() {
    // 读取HTTP和SOCKS5代理并合并
    std::vector<Proxy> httpProxies = readProxiesByProtocol("data/valid_ips_http.txt", "http");
    std::vector<Proxy> socks5Proxies = readProxiesByProtocol("data/valid_ips_socks5.txt", "socks5");
    
    std::vector<Proxy> allProxies;
    allProxies.insert(allProxies.end(), httpProxies.begin(), httpProxies.end());
    allProxies.insert(allProxies.end(), socks5Proxies.begin(), socks5Proxies.end());
    
    if (allProxies.empty()) {
        std::cerr << "没有找到任何有效代理" << std::endl;
        return 1;
    }

    // 筛选低延迟代理
    std::vector<Proxy> validProxies = filterLowLatencyProxies(allProxies, 1000, 50);
    if (validProxies.empty()) {
        std::cerr << "没有符合条件的低延迟代理" << std::endl;
        return 1;
    }

    // 生成配置文件
    bool success = generateClashConfig(validProxies, "data/clash_config.yaml");
    if (success) {
        std::cout << "Clash配置文件生成成功: data/clash_config.yaml" << std::endl;
    } else {
        std::cerr << "配置文件生成失败" << std::endl;
        return 1;
    }

    return 0;
}
