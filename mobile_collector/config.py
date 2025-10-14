"""
配置管理模块

负责加载和管理应用程序配置，支持从配置文件和环境变量读取。
"""

import json
import os
from typing import Any, Optional


class Config:
    """配置管理类"""
    
    DEFAULT_CONFIG = {
        "microsoft": {
            "client_id": "",
            "client_secret": "",
            "redirect_uri": "http://localhost:8000/callback",
            "scopes": [
                "Notes.Create",
                "Notes.Read",
                "Files.ReadWrite"
            ]
        },
        "onenote": {
            "default_notebook_id": None,
            "default_section_id": None
        },
        "onedrive": {
            "default_folder": "/LifeLog"
        },
        "categories": {
            "enabled": False,
            "rules": []
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置
        
        Args:
            config_file: 配置文件路径，如果为None则使用默认路径
        """
        self.config_file = config_file or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'config.json'
        )
        self.config = self.DEFAULT_CONFIG.copy()
        self._load()
    
    def _load(self):
        """从配置文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self._merge_config(user_config)
            except Exception as e:
                print(f"警告: 无法加载配置文件 {self.config_file}: {e}")
        
        # 从环境变量加载敏感配置
        self._load_from_env()
    
    def _merge_config(self, user_config: dict):
        """合并用户配置到默认配置"""
        def merge(base, update):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge(base[key], value)
                else:
                    base[key] = value
        
        merge(self.config, user_config)
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        env_mappings = {
            'MS_CLIENT_ID': ['microsoft', 'client_id'],
            'MS_CLIENT_SECRET': ['microsoft', 'client_secret'],
            'MS_REDIRECT_URI': ['microsoft', 'redirect_uri'],
        }
        
        for env_key, config_path in env_mappings.items():
            value = os.getenv(env_key)
            if value:
                current = self.config
                for key in config_path[:-1]:
                    current = current[key]
                current[config_path[-1]] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的路径，如 "microsoft.client_id"
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
        设置配置值
        
        Args:
            key: 配置键，支持点号分隔的路径
            value: 配置值
        """
        keys = key.split('.')
        current = self.config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def save(self):
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"错误: 无法保存配置文件: {e}")
            raise
    
    def validate(self) -> bool:
        """
        验证配置是否完整
        
        Returns:
            True 如果配置有效，否则 False
        """
        required_fields = [
            'microsoft.client_id',
            'microsoft.client_secret',
        ]
        
        for field in required_fields:
            value = self.get(field)
            if not value:
                print(f"错误: 缺少必需的配置项: {field}")
                return False
        
        return True
