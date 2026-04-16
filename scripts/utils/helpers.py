"""
Helper Utilities Module
通用工具模块
"""

import re
import time
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


def clean_text(text: str) -> str:
    """
    清理文本
    
    Args:
        text: 原始文本
        
    Returns:
        清理后的文本
    """
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text)
    # 移除特殊字符
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    return text.strip()


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_number(num: int) -> str:
    """
    格式化数字（添加千位分隔符）
    
    Args:
        num: 数字
        
    Returns:
        格式化后的字符串
    """
    if num >= 10000:
        return f"{num / 10000:.1f}万"
    elif num >= 1000:
        return f"{num:,}"
    return str(num)


def parse_date(date_string: str, fmt: str = "%Y-%m-%d") -> Optional[datetime]:
    """
    解析日期字符串
    
    Args:
        date_string: 日期字符串
        fmt: 日期格式
        
    Returns:
        datetime对象或None
    """
    try:
        return datetime.strptime(date_string, fmt)
    except:
        return None


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间
    
    Args:
        dt: datetime对象
        fmt: 格式字符串
        
    Returns:
        格式化后的字符串
    """
    return dt.strftime(fmt)


def sleep_random(min_seconds: float = 1.0, max_seconds: float = 3.0):
    """
    随机延迟（防止请求过于规律）
    
    Args:
        min_seconds: 最小秒数
        max_seconds: 最大秒数
    """
    sleep_time = random.uniform(min_seconds, max_seconds)
    time.sleep(sleep_time)


def retry_operation(operation, max_retries: int = 3, 
                   delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    重试操作
    
    Args:
        operation: 操作函数
        max_retries: 最大重试次数
        delay: 延迟秒数
        exceptions: 捕获的异常类型
        
    Returns:
        操作结果
    """
    for attempt in range(max_retries):
        try:
            return operation()
        except exceptions as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(delay * (attempt + 1))
            
    return None


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    分割列表
    
    Args:
        lst: 原始列表
        chunk_size: 每块大小
        
    Returns:
        分割后的列表
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def deduplicate_list(lst: List[Any]) -> List[Any]:
    """
    列表去重（保持顺序）
    
    Args:
        lst: 原始列表
        
    Returns:
        去重后的列表
    """
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def extract_urls(text: str) -> List[str]:
    """
    从文本中提取URL
    
    Args:
        text: 文本
        
    Returns:
        URL列表
    """
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return url_pattern.findall(text)


def extract_emails(text: str) -> List[str]:
    """
    从文本中提取邮箱
    
    Args:
        text: 文本
        
    Returns:
        邮箱列表
    """
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    return email_pattern.findall(text)


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    安全获取字典值
    
    Args:
        dictionary: 字典
        key: 键
        default: 默认值
        
    Returns:
        值或默认值
    """
    if dictionary is None:
        return default
    return dictionary.get(key, default)


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并多个字典
    
    Args:
        *dicts: 字典列表
        
    Returns:
        合并后的字典
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def calculate_time_diff(start: datetime, end: datetime) -> Dict[str, int]:
    """
    计算时间差
    
    Args:
        start: 开始时间
        end: 结束时间
        
    Returns:
        时间差字典（天、小时、分钟、秒）
    """
    diff = end - start
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    seconds = diff.seconds % 60
    
    return {
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "total_seconds": diff.total_seconds()
    }


def generate_timestamp() -> str:
    """生成ISO格式时间戳"""
    return datetime.now().isoformat()


def is_valid_phone(phone: str) -> bool:
    """
    验证手机号格式
    
    Args:
        phone: 手机号
        
    Returns:
        是否有效
    """
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def mask_sensitive(text: str, start: int = 3, end: int = -4) -> str:
    """
    掩码敏感信息
    
    Args:
        text: 原始文本
        start: 显示起始位置
        end: 显示结束位置
        
    Returns:
        掩码后的文本
    """
    if len(text) <= abs(start) + abs(end):
        return '*' * len(text)
        
    end = end if end >= 0 else len(text) + end + 1
    return text[:start] + '*' * (end - start) + text[end:]
