"""
Logging Module
日志模块
"""

import os
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional


class Logger:
    """日志管理器"""
    
    def __init__(self, name: str = "wechat-xhs-automation",
                 log_path: str = "./logs/wechat-xhs-automation.log",
                 level: str = "INFO"):
        """
        初始化日志管理器
        
        Args:
            name: 日志器名称
            log_path: 日志文件路径
            level: 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # 清除现有处理器
        self.logger.handlers = []
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # 文件处理器
        if log_path:
            os.makedirs(os.path.dirname(log_path) or '.', exist_ok=True)
            file_handler = RotatingFileHandler(
                log_path, 
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
            
    def debug(self, message: str):
        """调试日志"""
        self.logger.debug(message)
        
    def info(self, message: str):
        """信息日志"""
        self.logger.info(message)
        
    def warning(self, message: str):
        """警告日志"""
        self.logger.warning(message)
        
    def error(self, message: str):
        """错误日志"""
        self.logger.error(message)
        
    def critical(self, message: str):
        """严重错误日志"""
        self.logger.critical(message)


class OperationLogger:
    """操作日志"""
    
    def __init__(self, log_path: str = "./logs/operations.log"):
        """
        初始化操作日志
        
        Args:
            log_path: 日志文件路径
        """
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path) or '.', exist_ok=True)
        
    def log_operation(self, operation: str, platform: str, 
                     details: dict, status: str = "success"):
        """
        记录操作
        
        Args:
            operation: 操作类型
            platform: 平台名称
            details: 操作详情
            status: 操作状态
        """
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "operation": operation,
            "platform": platform,
            "status": status,
            "details": details
        }
        
        import json
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
    def get_operations(self, platform: Optional[str] = None,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None,
                      limit: int = 100) -> list:
        """
        获取操作记录
        
        Args:
            platform: 平台筛选
            start_time: 开始时间
            end_time: 结束时间
            limit: 返回数量限制
            
        Returns:
            操作记录列表
        """
        import json
        
        operations = []
        
        if not os.path.exists(self.log_path):
            return operations
            
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        
                        # 筛选
                        if platform and entry.get("platform") != platform:
                            continue
                            
                        if start_time:
                            entry_time = datetime.fromisoformat(entry["timestamp"])
                            if entry_time < start_time:
                                continue
                                
                        if end_time:
                            entry_time = datetime.fromisoformat(entry["timestamp"])
                            if entry_time > end_time:
                                continue
                                
                        operations.append(entry)
                        
                        if len(operations) >= limit:
                            break
                            
                    except:
                        continue
                        
        except Exception as e:
            print(f"[OperationLogger] 读取日志失败: {e}")
            
        return operations
