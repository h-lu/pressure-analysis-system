import json
import os
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

class ConfigManager:
    """配置管理器，用于存储和获取动态配置"""
    
    def __init__(self):
        self.config_file = Path(__file__).parent.parent / "config" / "user_config.json"
        self.config_file.parent.mkdir(exist_ok=True)
        self._default_config = {
            "deepseek": {
                "api_key": "",
                "base_url": "https://api.deepseek.com",
                "model": "deepseek-chat",
                "last_updated": None
            }
        }
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self._default_config.copy()
        except Exception as e:
            print(f"加载配置失败: {e}")
            return self._default_config.copy()
    
    def _save_config(self, config: Dict) -> bool:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get_deepseek_config(self) -> Dict:
        """获取DeepSeek配置"""
        config = self._load_config()
        deepseek_config = config.get("deepseek", self._default_config["deepseek"].copy())
        
        # 如果配置为空，尝试从环境变量获取默认值
        if not deepseek_config.get("api_key"):
            deepseek_config["api_key"] = os.getenv("DEEPSEEK_API_KEY", "")
        if not deepseek_config.get("base_url"):
            deepseek_config["base_url"] = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        if not deepseek_config.get("model"):
            deepseek_config["model"] = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        return deepseek_config
    
    def save_deepseek_config(self, api_key: str, base_url: str = None, model: str = None) -> bool:
        """保存DeepSeek配置"""
        config = self._load_config()
        
        if "deepseek" not in config:
            config["deepseek"] = self._default_config["deepseek"].copy()
        
        config["deepseek"]["api_key"] = api_key
        if base_url:
            config["deepseek"]["base_url"] = base_url
        if model:
            config["deepseek"]["model"] = model
        config["deepseek"]["last_updated"] = datetime.now().isoformat()
        
        return self._save_config(config)
    
    def get_masked_api_key(self) -> str:
        """获取隐藏的API密钥"""
        config = self.get_deepseek_config()
        api_key = config.get("api_key", "")
        
        if not api_key or len(api_key) <= 8:
            return ""
        
        return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
    
    def has_valid_config(self) -> bool:
        """检查是否有有效的配置"""
        config = self.get_deepseek_config()
        return bool(config.get("api_key"))

# 全局配置管理器实例
config_manager = ConfigManager() 