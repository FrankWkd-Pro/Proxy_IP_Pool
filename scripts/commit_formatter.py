def format_commit_message():
    """生成格式化的提交消息"""
    try:
        # 读取验证统计数据
        with open('stats/validation_stats.json') as f:  # 注意这里修正了文件路径！
            stats = json.load(f)
        
        # 提取关键指标
        valid_count = stats.get('valid_count', 0)
        total_count = stats.get('total_count', 0)
        validation_time = stats.get('validation_time', 0)
        success_rate = stats.get('success_rate', 0)
        
        # 计算成功率百分比
        success_percent = f"{success_rate:.2f}%" if success_rate else "N/A"
        
        # 获取当前时间
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        
        # 生成状态标记（用文字代替emoji）
        status_flag = "Success" if valid_count > 0 else "Warning"
        
        # 构建提交消息（移除所有emoji和特殊符号）
        message = (
            f"[Bot] Update Available proxies {status_flag}\n\n"
            f"Valid proxies: {valid_count}/{total_count} ({success_percent})\n"
            f"Validation time: {validation_time:.2f}s\n"
            f"Update time: {current_time}"
        )
        
        return message
    
    except FileNotFoundError:
        # 如果找不到统计文件，使用默认消息
        return "[Bot] Update Available proxies Warning\n\nNo validation data available"
    except Exception as e:
        # 其他异常处理
        return f"[Bot] Update Available proxies Error\n\nError formatting message: {str(e)}"
