"""
Configuration Management Module
配置管理模块
"""

import os
import json
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG_PATH = "./config.json"
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config: Dict[str, Any] = {}
        self._load_config()
        
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"[ConfigManager] 加载配置失败: {e}")
                self.config = {}
        else:
            # 加载示例配置
            example_path = os.path.join(
                os.path.dirname(__file__), 
                "../../config.example.json"
            )
            if os.path.exists(example_path):
                try:
                    with open(example_path, 'r', encoding='utf-8') as f:
                        self.config = json.load(f)
                except:
                    self.config = {}
                    
    def save_config(self):
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(self.config_path) or '.', exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[ConfigManager] 保存配置失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键（支持点号分隔，如 'wechat.app_id'）
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
    
    def set(self, key: str, value: Any):
        """
        设置配置项
        
        Args:
            key: 配置键
            value: 配置值
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
        self.save_config()
        
    def get_wechat_config(self) -> Dict[str, Any]:
        """获取微信配置"""
        return self.config.get("wechat", {})
    
    def get_xhs_config(self) -> Dict[str, Any]:
        """获取小红书配置"""
        return self.config.get("xiaohongshu", {})
    
    def get_sync_config(self) -> Dict[str, Any]:
        """获取同步配置"""
        return self.config.get("sync", {})
    
    def get_scheduler_config(self) -> Dict[str, Any]:
        """获取调度配置"""
        return self.config.get("scheduler", {})
    
    def validate_config(self) -> Dict[str, Any]:
        """
        验证配置完整性
        
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        
        # 检查微信配置
        wechat = self.config.get("wechat", {})
        if not wechat.get("app_id"):
            errors.append("缺少微信公众号AppID")
        if not wechat.get("app_secret"):
            errors.append("缺少微信公众号AppSecret")
            
        # 检查小红书配置
        xhs = self.config.get("xiaohongshu", {})
        if not xhs.get("phone"):
            warnings.append("未配置小红书手机号")
        if not xhs.get("password"):
            warnings.append("未配置小红书密码")
            
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
