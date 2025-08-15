#!/usr/bin/env python3
"""
commit_formatter.py - 生成提交消息的工具
确保输出不含额外换行符或空格
"""

import sys

def format_commit_message():
    """生成简单的提交消息"""
    return "[Bot] Proxy IP Updated"  # 注意：没有换行符

if __name__ == "__main__":
    try:
        # 直接输出消息，不添加额外内容
        sys.stdout.write(format_commit_message())
        # 确保立即刷新输出缓冲区
        sys.stdout.flush()
    except Exception as e:
        # 出错时输出简单错误信息
        sys.stderr.write(f"Error: {str(e)}")
        sys.exit(1)
