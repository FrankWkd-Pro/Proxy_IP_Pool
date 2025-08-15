import os
import json
import time
import sys
from datetime import datetime

def format_commit_message():
    """生成格式化的提交消息（确保非空且无特殊字符）"""
    try:
        # 注意：验证统计文件实际保存在stats目录（修复路径错误）
        with open('stats/validation_stats.json') as f:
            stats = json.load(f)
        
        valid_count = stats.get('valid_count', 0)
        total_count = stats.get('total_count', 0)
        validation_time = stats.get('validation_time', 0)
        success_rate = stats.get('success_rate', 0)
        
        success_percent = f"{success_rate:.2f}%" if success_rate else "N/A"
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        
        # 用文字代替emoji，避免环境变量解析错误
        status = "Success" if valid_count > 0 else "Warning"
        
        message = (
            f"[Bot] Update Available proxies ({status})\n\n"
            f"Valid proxies: {valid_count}/{total_count} ({success_percent})\n"
            f"Validation time: {validation_time:.2f}s\n"
            f"Update time: {current_time}"
        )
        return message
    
    except FileNotFoundError:
        return "[Bot] Update Available proxies (Warning)\n\nNo validation data available"
    except Exception as e:
        return f"[Bot] Update Available proxies (Error)\n\nError formatting message: {str(e)}"

if __name__ == "__main__":
    commit_message = format_commit_message()
    # 确保消息非空（最后防线）
    if not commit_message.strip():
        commit_message = "[Bot] Update Available proxies (Fallback)\n\nNo valid message generated"
    
    print(commit_message)
    with open('commit_message.txt', 'w') as f:
        f.write(commit_message)
    
    sys.exit(0 if "Error" not in commit_message else 1)
