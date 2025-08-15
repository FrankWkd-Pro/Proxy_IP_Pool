# Proxy_IP_Pool
A Repo for FrankWkd to Save Available Proxy IPs and Update Available IPs by Using Github Actions.  
一个用来自动爬取并检测可用免费 Proxy 代理服务器的仓库。使用 Github Actions 自动爬取一些免费 Proxy 代理服务器的 Proxy IP。爬取完成后会自动检测 IP 的连通性和可用性，并且输出可用的 IP 到 data/ 目录下。

## Todo
- [x] 自动爬取可用 IP
- [x] 自动验证 IP 连通性
- [x] 自动整理可用 IP
- [ ] 自动生成 Clash 订阅
- [ ] 本地部署定时任务


# 免责声明 / Disclaimer
> ## 使用即代表您同意以下所有条款：
> ## By using it, you agree to all of the following terms:
### 1. 项目目的声明
本项目（Proxy IP Pool）仅为技术研究与学习目的开发，旨在探索网络爬虫、代理验证等技术实现原理。项目提供的代理IP仅用于教育目的，不得用于任何非法活动或商业用途。  
**项目创作者(FrankWkd-Pro)具有最高级别的项目解释权。**

### 2. 时效性与数据删除
**重要提示：**
- **请在下载或获取代理IP列表后的24小时内删除所有相关数据**
- 本项目提供的代理IP具有高度时效性，长期使用可能导致安全风险
- 我们不维护代理IP的历史记录或存档
- 禁止长期存储或重新分发代理IP列表

### 3. 使用者责任
使用者应对使用本项目的所有行为承担全部责任：
- 使用本项目即表示您已了解并同意自行承担所有风险
- 您必须遵守所在国家/地区的所有适用法律法规
- 禁止用于任何侵犯他人隐私、版权或其他权利的活动
- 禁止用于传播恶意软件、网络攻击或任何破坏性活动

### 4. 代理IP来源声明
本项目提供的代理IP来自公开网络资源：
- 我们不拥有、控制或管理这些代理服务器
- 我们不保证代理IP的可用性、速度或安全性
- 我们不验证代理IP所有者的合法性及使用政策
- 我们不存储或记录通过代理传输的任何用户数据

### 5. 版权与内容责任
- 本项目不抓取、存储或传播任何受版权保护的内容
- 不对通过代理访问的任何内容负责
- 禁止使用本项目访问非法网站或获取非法内容

### 6. 免责条款
在任何情况下，项目作者及贡献者均不对因以下原因导致的任何损害承担责任：
- 使用或无法使用本项目而产生的直接或间接损失
- 通过本项目获取的代理IP造成的任何问题
- 因违反本免责声明或当地法律造成的后果
- 未能在24小时内删除获取的代理IP而产生的风险


#### 7. 严格禁止条款
**使用本项目即表示您同意以下严格禁令**：
- 禁止任何非法活动（包括但不限于黑客攻击、欺诈、侵犯隐私）
- 禁止侵犯知识产权（版权、商标等）
- 禁止传播恶意软件、发起网络攻击或破坏性活动
- 禁止访问非法内容或规避地理限制
- 禁止商业用途及转售代理服务

#### 8. 有限使用授权
本项目仅授予**临时、非独占、不可转让、可撤销**的使用权：
- 所有获取的数据必须在使用后 **24小时内永久删除**
- 禁止创建衍生作品或修改本项目代码
- 禁止反编译、逆向工程或任何形式的代码分析

#### 9. 无担保声明
项目以 **"现状"提供，不作任何明示或暗示担保**：
- 不保证代理的可用性、速度或安全性
- 不保证项目的持续可用性或功能完整性
- 不承担因使用本项目导致的任何损失或损害

#### 10. 完全责任免除
**在任何情况下，项目创作者、管理者及贡献者均不承担**：
- 直接、间接、偶然、特殊或后果性损害
- 第三方使用本项目造成的损害
- 因违反本声明或当地法律导致的损失
- 未能在24小时内删除数据产生的风险

#### 11. 用户赔偿条款
用户同意赔偿并保护项目方免受因以下原因产生的索赔：
- 用户违反本免责声明
- 用户不当使用本项目
- 用户侵犯第三方权利的行为

#### 12. 数据合规要求
- 所有获取的代理数据必须在 **24小时内永久删除**
- 禁止存储、存档或重新分发代理列表
- 禁止使用自动化工具持续下载数据
- 使用前必须验证代理是否符合本地法律

---

## English Version

### 1. Purpose Statement
This project (Proxy IP Pool) is developed solely for technical research and educational purposes, aiming to explore the implementation principles of web crawling and proxy validation technologies. The proxy IPs provided by this project are for educational use only and shall not be used for any illegal activities or commercial purposes.  
**Project creators(FrankWkd-Pro) have the highest level of project interpretation rights.**

### 2. Timeliness and Data Deletion
**Important Notice:**
- **Please delete all related data within 24 hours of downloading or obtaining the proxy IP list**
- The proxy IPs provided have high timeliness; long-term use may pose security risks
- We do not maintain historical records or archives of proxy IPs
- Long-term storage or redistribution of proxy IP lists is prohibited

### 3. User Responsibility
Users assume full responsibility for all actions when using this project:
- By using this project, you acknowledge and agree to bear all risks
- You must comply with all applicable laws and regulations in your jurisdiction
- Prohibited from any activities that infringe on others' privacy, copyright, or other rights
- Prohibited from spreading malware, conducting network attacks, or any destructive activities

### 4. Proxy Source Declaration
The proxy IPs provided by this project are sourced from public network resources:
- We do not own, control, or manage these proxy servers
- We do not guarantee the availability, speed, or security of proxy IPs
- We do not verify the legality or usage policies of proxy IP owners
- We do not store or log any user data transmitted through proxies

### 5. Copyright and Content Liability
- This project does not crawl, store, or distribute any copyrighted content
- Not responsible for any content accessed through proxies
- Prohibited from using this project to access illegal websites or obtain illegal content

### 6. Liability Limitation
Under no circumstances shall the project authors and contributors be liable for any damages resulting from:
- Direct or indirect losses arising from the use or inability to use this project
- Any issues caused by proxy IPs obtained through this project
- Consequences of violating this disclaimer or local laws
- Risks arising from failure to delete obtained proxy IPs within 24 hours

#### 7. Strict Prohibitions
**By using this project, you agree to the following strict prohibitions**:
- No illegal activities (including but not limited to hacking, fraud, privacy infringement)
- No intellectual property violations (copyright, trademarks, etc.)
- No malware distribution, network attacks, or destructive activities
- No access to illegal content or geo-restriction circumvention
- No commercial use or resale of proxy services

#### 8. Limited Use License
This project grants only a **temporary, non-exclusive, non-transferable, revocable** license:
- All obtained data must be **permanently deleted within 24 hours** of use
- Creation of derivative works or code modification is prohibited
- Reverse engineering, decompilation, or any form of code analysis is prohibited

#### 9. No Warranty
The project is provided **"AS IS" without warranties of any kind**:
- No guarantee of proxy availability, speed, or security
- No guarantee of continuous availability or functional integrity
- No liability for any losses or damages resulting from use

#### 10. Complete Liability Exclusion
**Under no circumstances shall the project creators, maintainers, or contributors be liable for**:
- Direct, indirect, incidental, special, or consequential damages
- Damages caused by third-party use of this project
- Losses resulting from violation of this disclaimer or local laws
- Risks arising from failure to delete data within 24 hours

#### 11. User Indemnification
User agrees to indemnify and hold harmless the project parties from claims arising from:
- User's violation of this disclaimer
- User's misuse of this project
- User's infringement of third-party rights

#### 12. Data Compliance Requirements
- All obtained proxy data must be **permanently deleted within 24 hours**
- Storage, archiving, or redistribution of proxy lists is prohibited
- Use of automated tools for continuous data harvesting is prohibited
- Must verify proxy compliance with local laws before use

