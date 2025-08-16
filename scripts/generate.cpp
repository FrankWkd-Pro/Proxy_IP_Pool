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

// 代理服务器结构体
struct Proxy {
    std::string ip;
    int port;
    int latency; // 延迟(毫秒，-1表示无效)
};

// 线程参数结构体
struct ThreadArgs {
    const Proxy* proxy;          // 待测试的代理
    std::vector<Proxy>* results; // 存储测试结果的容器
    pthread_mutex_t* mutex;      // 互斥锁，保护结果容器
    int timeoutMs;               // 超时时间
};

// 测试单个代理延迟（毫秒）
int testSingleProxy(const std::string& ip, int port, int timeoutMs) {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd == -1) return -1;

    // 设置超时
    struct timeval timeout;
    timeout.tv_sec = timeoutMs / 1000;
    timeout.tv_usec = (timeoutMs % 1000) * 1000;
    setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    setsockopt(sockfd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));

    // 准备地址
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    if (inet_pton(AF_INET, ip.c_str(), &server_addr.sin_addr) <= 0) {
        close(sockfd);
        return -1;
    }

    // 计时并连接
    auto start = std::chrono::high_resolution_clock::now();
    int connectResult = connect(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr));
    auto end = std::chrono::high_resolution_clock::now();
    close(sockfd);

    // 计算延迟
    if (connectResult == 0) {
        return std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    }
    return -1;
}

// 线程入口函数
void* threadFunc(void* arg) {
    ThreadArgs* args = static_cast<ThreadArgs*>(arg);
    Proxy result = *args->proxy;
    
    // 测试延迟
    result.latency = testSingleProxy(args->proxy->ip, args->proxy->port, args->timeoutMs);
    
    // 线程安全地存入结果
    pthread_mutex_lock(args->mutex);
    args->results->push_back(result);
    pthread_mutex_unlock(args->mutex);
    
    return nullptr;
}

// 从文件读取代理列表
std::vector<Proxy> readProxies(const std::string& filename) {
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
            proxy.latency = -1;
            proxies.push_back(proxy);
        } catch (...) {
            continue;
        }
    }
    file.close();
    return proxies;
}

// 多线程筛选低延迟代理（核心优化）
std::vector<Proxy> filterLowLatencyProxies(const std::vector<Proxy>& proxies, 
                                          int maxLatencyMs = 1000, 
                                          int maxThreads = 50) { // 并发线程数，可根据CPU调整
    std::vector<Proxy> results;
    pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
    std::vector<pthread_t> threads;
    threads.reserve(proxies.size());

    std::cout << "使用 " << maxThreads << " 线程并行测试 " << proxies.size() << " 个代理..." << std::endl;
    auto start = std::chrono::high_resolution_clock::now();

    for (size_t i = 0; i < proxies.size(); ++i) {
        // 控制并发线程数，避免资源耗尽
        if (i >= maxThreads) {
            pthread_join(threads[i - maxThreads], nullptr);
        }

        // 创建线程参数
        ThreadArgs* args = new ThreadArgs{
            &proxies[i], &results, &mutex, maxLatencyMs
        };

        // 启动线程
        pthread_t thread;
        if (pthread_create(&thread, nullptr, threadFunc, args) != 0) {
            delete args;
            std::cerr << "线程创建失败，跳过代理 " << proxies[i].ip << std::endl;
            continue;
        }
        threads.push_back(thread);
    }

    // 等待剩余线程完成
    for (size_t i = std::max(0, (int)threads.size() - maxThreads); i < threads.size(); ++i) {
        pthread_join(threads[i], nullptr);
    }

    // 计算总耗时
    auto end = std::chrono::high_resolution_clock::now();
    int totalMs = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    std::cout << "并行测试完成，总耗时: " << totalMs << "ms" << std::endl;

    // 筛选有效代理并排序
    std::vector<Proxy> validProxies;
    for (const auto& p : results) {
        if (p.latency != -1 && p.latency <= maxLatencyMs) {
            validProxies.push_back(p);
        }
    }

    // 按延迟升序排序（最快的在前）
    std::sort(validProxies.begin(), validProxies.end(),
              [](const Proxy& a, const Proxy& b) { return a.latency < b.latency; });

    std::cout << "筛选出 " << validProxies.size() << " 个有效代理（延迟≤" << maxLatencyMs << "ms）" << std::endl;
    return validProxies;
}

// 生成Clash配置文件（简化IO操作）
bool generateClashConfig(const std::vector<Proxy>& proxies, const std::string& outputFilename) {
    if (proxies.empty()) {
        std::cerr << "没有有效代理可生成配置" << std::endl;
        return false;
    }

    // 使用缓冲区减少IO次数
    std::stringstream ss;

    // 写入基础配置
    ss << "mixed-port: 7890\n"
       << "allow-lan: false\n"
       << "mode: rule\n"
       << "log-level: info\n"
       << "external-controller: 127.0.0.1:9090\n"
       << "secret: \"\"\n\n";

    // 写入代理列表
    ss << "proxies:\n";
    for (size_t i = 0; i < proxies.size(); ++i) {
        ss << "  - name: \"Proxy_" << (i + 1) << "_" << proxies[i].latency << "ms\"\n"
           << "    type: http\n"
           << "    server: " << proxies[i].ip << "\n"
           << "    port: " << proxies[i].port << "\n"
           << "    username: \"\"\n"
           << "    password: \"\"\n"
           << "    timeout: 1000\n"
           << "    keep-alive: true\n";
        if (i != proxies.size() - 1) ss << "\n";
    }
    ss << "\n";

    // 写入代理组
    ss << "proxy-groups:\n"
       << "  - name: \"AutoSelect\"\n"
       << "    type: url-test\n"
       << "    url: \"http://www.gstatic.com/generate_204\"\n"
       << "    interval: 300\n"
       << "    proxies:\n";
    for (size_t i = 0; i < proxies.size(); ++i) {
        ss << "      - \"Proxy_" << (i + 1) << "_" << proxies[i].latency << "ms\"\n";
    }
    ss << "    tolerance: 100\n\n";

    // 写入规则
    ss << "rules:\n"
       << "  - MATCH,AutoSelect\n";

    // 一次性写入文件（减少磁盘IO）
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
    // 读取代理列表
    std::vector<Proxy> proxies = readProxies("../data/valid_ips.txt");
    if (proxies.empty()) {
        return 1;
    }

    // 多线程筛选低延迟代理（可调整maxThreads参数，根据CPU核心数）
    std::vector<Proxy> validProxies = filterLowLatencyProxies(proxies, 1000, 50);
    if (validProxies.empty()) {
        std::cerr << "没有符合条件的低延迟代理" << std::endl;
        return 1;
    }

    // 生成配置文件
    bool success = generateClashConfig(validProxies, "clash_config.yaml");
    if (success) {
        std::cout << "Clash配置文件生成成功: clash_config.yaml" << std::endl;
    } else {
        std::cerr << "配置文件生成失败" << std::endl;
        return 1;
    }

    return 0;
}
